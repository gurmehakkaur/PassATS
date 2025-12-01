"""
Semantic Memory System
Extracts stable facts, traits, and patterns from episodic memories
"""

import os
import uuid as uuid_lib
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from collections import Counter

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from dotenv import load_dotenv

from memory_models import (
    SemanticMemory,
    SemanticMemoryType,
    SemanticPayload,
    EpisodicMemory,
    ExtractSemanticResponse
)

# Load .env from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# ========== SETUP ==========
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
SEMANTIC_COLLECTION = "semantic_memory"
EPISODIC_COLLECTION = "episodic_memory"

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
semantic_llm = ChatOpenAI(model="gpt-4o", temperature=0.2)  # Use GPT-4 for better extraction


# ========== COLLECTION INITIALIZATION ==========
def init_semantic_collection():
    """Initialize the semantic memory collection"""
    try:
        collections = qdrant_client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if SEMANTIC_COLLECTION not in collection_names:
            qdrant_client.create_collection(
                collection_name=SEMANTIC_COLLECTION,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
            )
            print(f"✅ Created collection: {SEMANTIC_COLLECTION}")
        else:
            print(f"✅ Collection exists: {SEMANTIC_COLLECTION}")
    except Exception as e:
        print(f"❌ Error initializing semantic collection: {e}")


# ========== EPISODIC RETRIEVAL FOR EXTRACTION ==========
def get_recent_episodes(lookback_days: int = 30, min_count: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieve recent episodic memories for semantic extraction
    
    Args:
        lookback_days: How many days back to look
        min_count: Minimum number of episodes needed
        
    Returns:
        List of episode payloads
    """
    try:
        # Calculate timestamp threshold
        threshold = (datetime.now() - timedelta(days=lookback_days)).timestamp()
        
        # Scroll through all recent episodes
        episodes = []
        offset = None
        
        while True:
            results = qdrant_client.scroll(
                collection_name=EPISODIC_COLLECTION,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )
            
            points, next_offset = results
            
            for point in points:
                if point.payload.get("timestamp", 0) >= threshold:
                    episodes.append({
                        "id": point.id,
                        "story": point.payload.get("story", ""),
                        "emotion": point.payload.get("emotion"),
                        "key_entities": point.payload.get("key_entities", []),
                        "user_intent": point.payload.get("user_intent"),
                        "importance": point.payload.get("importance", 0.5),
                        "tags": point.payload.get("tags", []),
                        "timestamp": point.payload.get("timestamp")
                    })
            
            if next_offset is None or len(episodes) >= min_count * 2:
                break
            
            offset = next_offset
        
        return episodes[:min_count * 5]  # Return up to 5x min_count for better extraction
        
    except Exception as e:
        print(f"❌ Error retrieving episodes: {e}")
        return []


# ========== SEMANTIC EXTRACTION ==========
def extract_semantic_memories(episodes: List[Dict[str, Any]]) -> List[SemanticMemory]:
    """
    Use LLM to extract semantic memories from episodic stories
    
    Args:
        episodes: List of episode dictionaries
        
    Returns:
        List of SemanticMemory objects
    """
    
    if len(episodes) < 5:
        print("⚠️ Not enough episodes for semantic extraction")
        return []
    
    # Prepare episode summaries
    episode_summaries = []
    for ep in episodes:
        emotion_str = f" [{ep['emotion']}]" if ep.get('emotion') else ""
        episode_summaries.append(f"- {ep['story']}{emotion_str}")
    
    episodes_text = "\n".join(episode_summaries[:50])  # Limit to 50 episodes
    
    # Extraction prompt
    prompt = f"""
You are a semantic memory extractor for a personal AI assistant.

Analyze these episodic memories and extract stable, recurring patterns about the user.

EPISODIC MEMORIES:
{episodes_text}

Extract semantic memories in these categories:

1. **TRAITS**: Personality characteristics that appear consistently
2. **PREFERENCES**: Things the user likes/dislikes, values, priorities
3. **FACTS**: Stable facts about the user (job, location, relationships, etc.)
4. **PATTERNS**: Behavioral patterns or tendencies
5. **RELATIONSHIPS**: Important people and the nature of those relationships

For each semantic memory, provide:
- type: one of [trait, preference, fact, pattern, relationship]
- content: A clear, concise statement (1 sentence)
- confidence: 0.0-1.0 based on how often this appears
- tags: 2-3 relevant tags

Return a JSON array of objects. Extract 5-15 semantic memories total.
Focus on the MOST IMPORTANT and RECURRING themes.

Return ONLY valid JSON array, no markdown.
"""

    try:
        response = semantic_llm.invoke(prompt).content.strip()
        
        # Clean markdown if present
        if response.startswith("```"):
            response = response.split("```")[1]
            if response.startswith("json"):
                response = response[4:]
        
        semantic_data = eval(response)  # Safe since we control LLM output
        
        # Convert to SemanticMemory objects
        semantic_memories = []
        episode_ids = [ep["id"] for ep in episodes]
        
        for item in semantic_data:
            try:
                memory = SemanticMemory(
                    id=str(uuid_lib.uuid4()),
                    type=SemanticMemoryType(item.get("type", "fact")),
                    content=item.get("content", ""),
                    confidence=float(item.get("confidence", 0.7)),
                    source_episodes=episode_ids[:10],  # Link to source episodes
                    first_observed=datetime.now(),
                    last_updated=datetime.now(),
                    occurrence_count=len(episodes),
                    tags=item.get("tags", [])
                )
                semantic_memories.append(memory)
            except Exception as e:
                print(f"⚠️ Skipping invalid semantic memory: {e}")
                continue
        
        return semantic_memories
        
    except Exception as e:
        print(f"❌ Error extracting semantic memories: {e}")
        return []


# ========== STORAGE ==========
def store_semantic_memory(memory: SemanticMemory) -> bool:
    """
    Store a semantic memory in Qdrant
    
    Args:
        memory: SemanticMemory object to store
        
    Returns:
        True if successful
    """
    try:
        # Generate embedding from content
        vector = embedding_model.embed_query(memory.content)
        
        # Prepare payload
        payload = {
            "type": memory.type.value,
            "content": memory.content,
            "confidence": memory.confidence,
            "source_episodes": memory.source_episodes,
            "first_observed": memory.first_observed.timestamp(),
            "last_updated": memory.last_updated.timestamp(),
            "occurrence_count": memory.occurrence_count,
            "tags": memory.tags
        }
        
        # Store in Qdrant
        qdrant_client.upsert(
            collection_name=SEMANTIC_COLLECTION,
            points=[
                PointStruct(
                    id=memory.id,
                    vector=vector,
                    payload=payload
                )
            ]
        )
        
        print(f"✅ Stored semantic memory: {memory.id} - {memory.content[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ Error storing semantic memory: {e}")
        return False


# ========== RETRIEVAL ==========
def retrieve_semantic_memories(
    query: str,
    limit: int = 5,
    min_confidence: float = 0.5,
    memory_type: Optional[SemanticMemoryType] = None
) -> List[SemanticMemory]:
    """
    Retrieve relevant semantic memories
    
    Args:
        query: Search query
        limit: Max number of memories to return
        min_confidence: Minimum confidence threshold
        memory_type: Filter by specific type
        
    Returns:
        List of SemanticMemory objects
    """
    try:
        # Generate query embedding
        query_vector = embedding_model.embed_query(query)
        
        # Search using query_points
        results = qdrant_client.query_points(
            collection_name=SEMANTIC_COLLECTION,
            query=query_vector,
            limit=limit
        ).points
        
        # Convert to SemanticMemory objects
        memories = []
        for hit in results:
            payload = hit.payload
            
            # Apply confidence filter
            if payload.get("confidence", 0) < min_confidence:
                continue
            
            memory = SemanticMemory(
                id=hit.id,
                type=SemanticMemoryType(payload.get("type", "fact")),
                content=payload.get("content", ""),
                confidence=payload.get("confidence", 0.7),
                source_episodes=payload.get("source_episodes", []),
                first_observed=datetime.fromtimestamp(payload.get("first_observed", datetime.now().timestamp())),
                last_updated=datetime.fromtimestamp(payload.get("last_updated", datetime.now().timestamp())),
                occurrence_count=payload.get("occurrence_count", 1),
                tags=payload.get("tags", [])
            )
            memories.append(memory)
        
        return memories
        
    except Exception as e:
        print(f"❌ Error retrieving semantic memories: {e}")
        return []


# ========== MAIN EXTRACTION PIPELINE ==========
def run_semantic_extraction(
    min_episodes: int = 10,
    lookback_days: int = 30
) -> ExtractSemanticResponse:
    """
    Main pipeline: Retrieve episodes → Extract semantics → Store
    
    This should be run periodically (e.g., daily or after N interactions)
    
    Args:
        min_episodes: Minimum episodes needed for extraction
        lookback_days: How far back to look
        
    Returns:
        ExtractSemanticResponse with results
    """
    print(f"🔄 Starting semantic extraction (min_episodes={min_episodes}, lookback={lookback_days} days)")
    
    # 1. Get recent episodes
    episodes = get_recent_episodes(lookback_days, min_episodes)
    
    if len(episodes) < min_episodes:
        return ExtractSemanticResponse(
            status="insufficient_data",
            extracted_count=0,
            semantic_memories=[]
        )
    
    print(f"📚 Retrieved {len(episodes)} episodes")
    
    # 2. Extract semantic memories
    semantic_memories = extract_semantic_memories(episodes)
    
    if not semantic_memories:
        return ExtractSemanticResponse(
            status="extraction_failed",
            extracted_count=0,
            semantic_memories=[]
        )
    
    print(f"🧠 Extracted {len(semantic_memories)} semantic memories")
    
    # 3. Store each semantic memory
    stored_count = 0
    for memory in semantic_memories:
        if store_semantic_memory(memory):
            stored_count += 1
    
    print(f"✅ Stored {stored_count}/{len(semantic_memories)} semantic memories")
    
    return ExtractSemanticResponse(
        status="success",
        extracted_count=stored_count,
        semantic_memories=semantic_memories
    )


# Initialize collection on import
init_semantic_collection()
