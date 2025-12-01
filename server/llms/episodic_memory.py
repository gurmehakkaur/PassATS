"""
Episodic Memory System
Stores interaction episodes as narrative stories with embeddings
"""

import os
import time
import uuid as uuid_lib
from typing import List, Optional, Dict, Any
from datetime import datetime

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv

from memory_models import (
    EpisodicMemory, 
    EpisodicPayload, 
    EmotionType,
    StoreEpisodeRequest,
    StoreEpisodeResponse
)

# Load .env from parent directory
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

# Verify environment variables are loaded
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError(f"OPENAI_API_KEY not found. Checked .env at: {os.path.abspath(env_path)}")

# ========== SETUP ==========
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
EPISODIC_COLLECTION = "episodic_memory"

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
episode_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)


# ========== COLLECTION INITIALIZATION ==========
def init_episodic_collection():
    """Initialize or recreate the episodic memory collection"""
    try:
        collections = qdrant_client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if EPISODIC_COLLECTION not in collection_names:
            qdrant_client.create_collection(
                collection_name=EPISODIC_COLLECTION,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
            )
            print(f"✅ Created collection: {EPISODIC_COLLECTION}")
        else:
            print(f"✅ Collection exists: {EPISODIC_COLLECTION}")
    except Exception as e:
        print(f"❌ Error initializing collection: {e}")


# ========== EPISODE CREATION ==========
def create_episodic_story(
    user_message: str,
    assistant_response: str,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> EpisodicMemory:
    """
    Uses LLM to generate an episodic memory story from the conversation
    
    Returns:
        EpisodicMemory object with story, emotion, entities, etc.
    """
    
    # Build context
    context = ""
    if conversation_history:
        context = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in conversation_history[-3:]  # Last 3 messages for context
        ])
    
    context += f"\nuser: {user_message}\nassistant: {assistant_response}"
    
    # Prompt for episodic extraction
    prompt = f"""
You are an episodic memory extractor for a personal AI assistant.

Analyze this conversation and create an episodic memory entry.

CONVERSATION:
{context}

Return a JSON object with:
- "story": A 2-3 sentence narrative summary of what happened (from user's perspective)
- "emotion": Primary emotion (one of: happy, sad, anxious, excited, frustrated, neutral, confused, proud)
- "key_entities": List of important people, projects, or things mentioned
- "user_intent": What the user wanted or was trying to accomplish (1 sentence)
- "importance": Float 0-1, how personally meaningful this is
- "tags": List of 3-5 searchable tags

Focus on:
- What happened
- How the user felt
- What they wanted
- Who was involved

Return ONLY valid JSON, no markdown.
"""

    try:
        response = episode_llm.invoke(prompt).content.strip()
        
        # Clean markdown if present
        if response.startswith("```"):
            response = response.split("```")[1]
            if response.startswith("json"):
                response = response[4:]
        
        episode_data = eval(response)  # Safe since we control the LLM output
        
        # Create EpisodicMemory object with proper UUID
        episode = EpisodicMemory(
            id=str(uuid_lib.uuid4()),
            timestamp=datetime.now(),
            story=episode_data.get("story", ""),
            emotion=EmotionType(episode_data.get("emotion", "neutral")),
            key_entities=episode_data.get("key_entities", []),
            user_intent=episode_data.get("user_intent"),
            importance=float(episode_data.get("importance", 0.5)),
            tags=episode_data.get("tags", []),
            raw_context=context[:500]  # Store first 500 chars
        )
        
        return episode
        
    except Exception as e:
        print(f"❌ Error creating episode: {e}")
        # Fallback episode
        return EpisodicMemory(
            id=str(uuid_lib.uuid4()),
            timestamp=datetime.now(),
            story=f"User said: {user_message[:100]}...",
            importance=0.3,
            tags=["auto-generated"],
            raw_context=context[:500]
        )


# ========== STORAGE ==========
def store_episode(episode: EpisodicMemory) -> bool:
    """
    Store an episodic memory in Qdrant with vector embedding
    
    Args:
        episode: EpisodicMemory object to store
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Generate embedding from the story
        vector = embedding_model.embed_query(episode.story)
        
        # Prepare payload
        payload = {
            "story": episode.story,
            "emotion": episode.emotion.value if episode.emotion else None,
            "key_entities": episode.key_entities,
            "user_intent": episode.user_intent,
            "importance": episode.importance,
            "tags": episode.tags,
            "timestamp": episode.timestamp.timestamp(),
            "raw_context": episode.raw_context
        }
        
        # Store in Qdrant
        qdrant_client.upsert(
            collection_name=EPISODIC_COLLECTION,
            points=[
                PointStruct(
                    id=episode.id,
                    vector=vector,
                    payload=payload
                )
            ]
        )
        
        print(f"✅ Stored episode: {episode.id}")
        return True
        
    except Exception as e:
        print(f"❌ Error storing episode: {e}")
        return False


# ========== RETRIEVAL ==========
def retrieve_episodes(
    query: str,
    limit: int = 5,
    min_importance: float = 0.0,
    emotion_filter: Optional[EmotionType] = None,
    tag_filter: Optional[List[str]] = None
) -> List[EpisodicMemory]:
    """
    Retrieve relevant episodic memories based on semantic similarity
    
    Args:
        query: Search query
        limit: Max number of episodes to return
        min_importance: Minimum importance threshold
        emotion_filter: Filter by specific emotion
        tag_filter: Filter by tags
        
    Returns:
        List of EpisodicMemory objects
    """
    try:
        # Generate query embedding
        query_vector = embedding_model.embed_query(query)
        
        # Build filter conditions
        filter_conditions = []
        if min_importance > 0:
            filter_conditions.append({
                "key": "importance",
                "range": {"gte": min_importance}
            })
        
        # Search using query_points
        results = qdrant_client.query_points(
            collection_name=EPISODIC_COLLECTION,
            query=query_vector,
            limit=limit
        ).points
        
        # Convert to EpisodicMemory objects
        episodes = []
        for hit in results:
            payload = hit.payload
            episode = EpisodicMemory(
                id=hit.id,
                timestamp=datetime.fromtimestamp(payload.get("timestamp", time.time())),
                story=payload.get("story", ""),
                emotion=EmotionType(payload["emotion"]) if payload.get("emotion") else None,
                key_entities=payload.get("key_entities", []),
                user_intent=payload.get("user_intent"),
                importance=payload.get("importance", 0.5),
                tags=payload.get("tags", []),
                raw_context=payload.get("raw_context")
            )
            episodes.append(episode)
        
        return episodes
        
    except Exception as e:
        print(f"❌ Error retrieving episodes: {e}")
        return []


# ========== MAIN PIPELINE ==========
def save_interaction_as_episode(
    user_message: str,
    assistant_response: str,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> StoreEpisodeResponse:
    """
    Complete pipeline: Create episode → Store → Return response
    
    This is called after every user interaction
    """
    # 1. Create episodic story
    episode = create_episodic_story(user_message, assistant_response, conversation_history)
    
    # 2. Store in vector DB
    success = store_episode(episode)
    
    # 3. Return response
    return StoreEpisodeResponse(
        status="stored" if success else "failed",
        episode_id=episode.id,
        story=episode.story,
        importance=episode.importance,
        emotion=episode.emotion.value if episode.emotion else None
    )


# Initialize collection on import
init_episodic_collection()
