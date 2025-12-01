"""
Episodic Memory System
Handles creation and storage of episodic memories with journal labels
"""

from typing import Optional
from datetime import datetime
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from dotenv import load_dotenv
import uuid
import os

from memory_models import EpisodicMemory, EmotionType

# Load .env from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Initialize clients
client = OpenAI()

# Lazy-load embedding model
_embedding_model = None

def get_embedding_model():
    """Lazy-load the embedding model"""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
    return _embedding_model


def init_episodic_collection(qdrant_client: QdrantClient, collection_name: str):
    """Initialize the episodic memory collection"""
    try:
        collections = qdrant_client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if collection_name not in collection_names:
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
            )
            print(f"Created collection: {collection_name}")
        else:
            print(f"Collection exists: {collection_name}")
    except Exception as e:
        print(f"Error initializing collection: {e}")


def get_or_create_journal_label(conversation_text: str, qdrant_client: QdrantClient, collection_name: str) -> str:
    """
    Determine the ONE journal label for this conversation.
    Check existing labels first, create new one if needed.
    
    Examples:
    - "Gifts to colleagues"
    - "Networking with director"
    - "Career growth discussions"
    """
    
    # Get all existing journal labels
    try:
        results = qdrant_client.scroll(
            collection_name=collection_name,
            limit=100,
            with_payload=True,
            with_vectors=False
        )
        
        existing_labels = set()
        for point in results[0]:
            label = point.payload.get("journal_label")
            if label:
                existing_labels.add(label)
        
        existing_labels_str = "\n".join(f"- {label}" for label in existing_labels) if existing_labels else "No existing labels yet"
        
    except:
        existing_labels_str = "No existing labels yet"
    
    # Ask LLM to pick existing label or create new one
    prompt = f"""You are organizing a personal journal. Analyze this conversation and determine the ONE journal label it belongs to.

EXISTING JOURNAL LABELS:
{existing_labels_str}

CONVERSATION:
{conversation_text[:1500]}

RULES:
1. If this conversation fits an EXISTING label, use that EXACT label (copy it exactly)
2. If it doesn't fit any existing label, create a NEW descriptive label
3. Label should be specific and descriptive (e.g., "Gifts to colleagues", "Networking with director")
4. Use title case
5. Keep it 2-5 words

Return ONLY the label text, nothing else."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        
        label = response.choices[0].message.content.strip()
        label = label.strip('"').strip("'").strip()
        
        print(f"📌 Journal label: {label}")
        return label
        
    except Exception as e:
        print(f"Error determining journal label: {e}")
        return "General Journal"


def create_episodic_memory(conversation_summary: str, qdrant_client: QdrantClient, collection_name: str) -> Optional[EpisodicMemory]:
    """
    Create an episodic memory from a conversation summary.
    Uses LLM to extract story, emotion, entities, etc.
    """
    
    # Get journal label first
    journal_label = get_or_create_journal_label(conversation_summary, qdrant_client, collection_name)
    
    # Extract episodic details
    prompt = f"""Analyze this conversation and extract episodic memory details.

CONVERSATION:
{conversation_summary}

Return a JSON object with:
- "story": A 2-3 sentence narrative summary (from user's perspective)
- "emotion": Primary emotion (happy, sad, anxious, excited, frustrated, neutral, confused, proud)
- "key_entities": List of important people, projects, or things mentioned
- "user_intent": What the user wanted to accomplish (1 sentence)
- "importance": Float 0-1, how personally meaningful this is

Return ONLY valid JSON, no markdown."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean markdown if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        
        import json
        episode_data = json.loads(content)
        
        # Create EpisodicMemory object
        episode = EpisodicMemory(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            story=episode_data.get("story", ""),
            emotion=EmotionType(episode_data.get("emotion", "neutral")),
            key_entities=episode_data.get("key_entities", []),
            user_intent=episode_data.get("user_intent"),
            importance=float(episode_data.get("importance", 0.5)),
            tags=[journal_label],
            journal_label=journal_label,
            raw_context=conversation_summary[:500]
        )
        
        # Store in Qdrant
        vector = get_embedding_model().embed_query(episode.story)
        
        qdrant_client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=episode.id,
                    vector=vector,
                    payload={
                        "story": episode.story,
                        "emotion": episode.emotion.value if episode.emotion else None,
                        "key_entities": episode.key_entities,
                        "user_intent": episode.user_intent,
                        "importance": episode.importance,
                        "tags": episode.tags,
                        "journal_label": episode.journal_label,
                        "timestamp": episode.timestamp.timestamp(),
                        "raw_context": episode.raw_context
                    }
                )
            ]
        )
        
        print(f"Stored episodic memory: {episode.id} - Journal: {journal_label}")
        return episode
        
    except Exception as e:
        print(f"Error creating episodic memory: {e}")
        import traceback
        traceback.print_exc()
        return None
