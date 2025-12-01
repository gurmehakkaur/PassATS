"""
Semantic Memory System
Extracts stable facts, traits, and patterns from episodic memories
"""

from typing import List, Optional
from datetime import datetime, timedelta
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from dotenv import load_dotenv
import uuid
import os

from memory_models import SemanticMemory, SemanticMemoryType

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


def init_semantic_collection(qdrant_client: QdrantClient, collection_name: str):
    """Initialize the semantic memory collection"""
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
        print(f"Error initializing semantic collection: {e}")


def extract_semantic_memories(
    qdrant_client: QdrantClient,
    episodic_collection: str,
    semantic_collection: str,
    lookback_days: int = 7,
    min_episodes: int = 3
) -> List[SemanticMemory]:
    """
    Extract semantic memories from recent episodic memories.
    Looks for patterns, traits, preferences, facts, and relationships.
    """
    
    # Get recent episodes
    try:
        threshold = (datetime.now() - timedelta(days=lookback_days)).timestamp()
        
        results = qdrant_client.scroll(
            collection_name=episodic_collection,
            limit=100,
            with_payload=True,
            with_vectors=False
        )
        
        episodes = []
        for point in results[0]:
            if point.payload.get("timestamp", 0) >= threshold:
                episodes.append({
                    "id": point.id,
                    "story": point.payload.get("story", ""),
                    "emotion": point.payload.get("emotion"),
                    "key_entities": point.payload.get("key_entities", []),
                    "importance": point.payload.get("importance", 0.5),
                    "tags": point.payload.get("tags", [])
                })
        
        if len(episodes) < min_episodes:
            print(f"Not enough episodes for extraction ({len(episodes)} < {min_episodes})")
            return []
        
        # Prepare episode summaries
        episode_summaries = "\n".join([f"- {ep['story']}" for ep in episodes[:30]])
        
        # Extraction prompt
        prompt = f"""Analyze these recent conversations and extract semantic memories about the user.

RECENT CONVERSATIONS:
{episode_summaries}

Extract semantic memories in these categories:
1. TRAITS: Personality characteristics
2. PREFERENCES: Likes/dislikes, values, priorities
3. FACTS: Stable facts (job, location, relationships)
4. PATTERNS: Behavioral patterns or tendencies
5. RELATIONSHIPS: Important people and relationships

For each semantic memory, provide:
- type: one of [trait, preference, fact, pattern, relationship]
- content: A clear, concise statement (1 sentence)
- confidence: 0.0-1.0 based on evidence strength
- tags: 2-3 relevant tags

Return a JSON array of 5-15 semantic memories.
Focus on RECURRING themes and IMPORTANT information.

Return ONLY valid JSON array, no markdown."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean markdown if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        
        import json
        semantic_data = json.loads(content)
        
        # Convert to SemanticMemory objects and store
        semantic_memories = []
        episode_ids = [ep["id"] for ep in episodes]
        
        for item in semantic_data:
            try:
                memory = SemanticMemory(
                    id=str(uuid.uuid4()),
                    type=SemanticMemoryType(item.get("type", "fact")),
                    content=item.get("content", ""),
                    confidence=float(item.get("confidence", 0.7)),
                    source_episodes=episode_ids[:10],
                    first_observed=datetime.now(),
                    last_updated=datetime.now(),
                    occurrence_count=len(episodes),
                    tags=item.get("tags", [])
                )
                
                # Store in Qdrant
                vector = get_embedding_model().embed_query(memory.content)
                
                qdrant_client.upsert(
                    collection_name=semantic_collection,
                    points=[
                        PointStruct(
                            id=memory.id,
                            vector=vector,
                            payload={
                                "type": memory.type.value,
                                "content": memory.content,
                                "confidence": memory.confidence,
                                "source_episodes": memory.source_episodes,
                                "first_observed": memory.first_observed.timestamp(),
                                "last_updated": memory.last_updated.timestamp(),
                                "occurrence_count": memory.occurrence_count,
                                "tags": memory.tags
                            }
                        )
                    ]
                )
                
                semantic_memories.append(memory)
                print(f"Stored semantic memory: {memory.content[:50]}...")
                
            except Exception as e:
                print(f"Error storing semantic memory: {e}")
                continue
        
        return semantic_memories
        
    except Exception as e:
        print(f"Error extracting semantic memories: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_semantic_context(qdrant_client: QdrantClient, semantic_collection: str, limit: int = 10) -> str:
    """
    Retrieve semantic memories to inject into system prompt.
    Returns formatted string of user's traits, preferences, patterns, etc.
    """
    
    try:
        # Get all semantic memories (sorted by confidence)
        results = qdrant_client.scroll(
            collection_name=semantic_collection,
            limit=limit,
            with_payload=True,
            with_vectors=False
        )
        
        if not results[0]:
            return ""
        
        # Group by type
        memories_by_type = {}
        for point in results[0]:
            mem_type = point.payload.get("type", "fact")
            content = point.payload.get("content", "")
            confidence = point.payload.get("confidence", 0.7)
            
            if mem_type not in memories_by_type:
                memories_by_type[mem_type] = []
            memories_by_type[mem_type].append(f"- {content} (confidence: {int(confidence*100)}%)")
        
        # Format context
        context_parts = []
        
        type_labels = {
            "trait": "Personality Traits",
            "preference": "Preferences & Values",
            "fact": "Key Facts",
            "pattern": "Behavioral Patterns",
            "relationship": "Important Relationships"
        }
        
        for mem_type, label in type_labels.items():
            if mem_type in memories_by_type:
                context_parts.append(f"\n{label}:")
                context_parts.extend(memories_by_type[mem_type][:5])  # Max 5 per type
        
        if context_parts:
            return "\n".join(context_parts)
        else:
            return ""
        
    except Exception as e:
        print(f"Error getting semantic context: {e}")
        return ""
