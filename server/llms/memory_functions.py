"""
Memory Functions for Episodic and Semantic Memory
"""

from typing import List, Optional
from datetime import datetime
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from dotenv import load_dotenv
import uuid
import os

from memory_models import EpisodicMemory, EmotionType, SemanticMemory, SemanticMemoryType

# Load .env from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Initialize clients
client = OpenAI()

# Lazy-load embedding model to avoid initialization issues
_embedding_model = None

def get_embedding_model():
    """Lazy-load the embedding model"""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
    return _embedding_model

def get_or_create_journal_label(conversation_text: str, qdrant_client: QdrantClient, collection_name: str) -> str:
    """
    Determine the ONE journal label for this conversation.
    Check existing labels first, create new one if needed.
    
    Examples:
    - "Gifts to colleagues"
    - "Networking with director"
    - "Career growth discussions"
    - "Anxiety about presentations"
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
3. Label should be specific and descriptive (e.g., "Gifts to colleagues", "Networking with director", "Anxiety about presentations")
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
        # Clean up any quotes or extra formatting
        label = label.strip('"').strip("'").strip()
        
        print(f"📌 Journal label: {label}")
        return label
        
    except Exception as e:
        print(f"❌ Error determining journal label: {e}")
        return "General Journal"


def create_episodic_memory(conversation_text: str, qdrant_client: QdrantClient, collection_name: str) -> EpisodicMemory:
    """
    Create structured episodic memory from conversation using LLM
    Returns EpisodicMemory object and stores in Qdrant
    """
    
    # First, determine the journal label
    journal_label = get_or_create_journal_label(conversation_text, qdrant_client, collection_name)
    
    prompt = f"""Analyze this conversation and extract episodic memory details.

Conversation:
{conversation_text[:2000]}

This conversation belongs to the journal: "{journal_label}"

Return a JSON object with:
- "story": 2-3 sentence narrative summary (what happened from user's perspective)
- "emotion": Primary emotion (one of: happy, sad, anxious, excited, frustrated, neutral, confused, proud)
- "key_entities": List of important people, projects, or things mentioned
- "user_intent": What the user wanted or was trying to accomplish (1 sentence)
- "importance": Float 0-1, how personally meaningful this is

Return ONLY valid JSON, no markdown."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        result = response.choices[0].message.content.strip()
        
        # Clean markdown if present
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        
        import json
        episode_data = json.loads(result)
        
        # Create EpisodicMemory object
        episode = EpisodicMemory(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            story=episode_data.get("story", ""),
            emotion=EmotionType(episode_data.get("emotion", "neutral")) if episode_data.get("emotion") else None,
            key_entities=episode_data.get("key_entities", []),
            user_intent=episode_data.get("user_intent"),
            importance=float(episode_data.get("importance", 0.5)),
            tags=[journal_label],  # Only the journal label as tag
            raw_context=conversation_text[:500]
        )
        
        # Store in Qdrant
        vector = get_embedding_model().embed_query(episode.story)
        
        payload = {
            "journal_label": journal_label,  # THE ONE LABEL
            "story": episode.story,
            "emotion": episode.emotion.value if episode.emotion else None,
            "key_entities": episode.key_entities,
            "user_intent": episode.user_intent,
            "importance": episode.importance,
            "timestamp": episode.timestamp.timestamp(),
            "raw_context": episode.raw_context
        }
        
        qdrant_client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=episode.id,
                    vector=vector,
                    payload=payload
                )
            ]
        )
        
        print(f"✅ Stored episodic memory: {episode.id}")
        print(f"   Journal: {journal_label}")
        print(f"   Story: {episode.story[:80]}...")
        print(f"   Emotion: {episode.emotion.value if episode.emotion else 'none'}")
        
        return episode
        
    except Exception as e:
        print(f"❌ Error creating episodic memory: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback episode
        episode = EpisodicMemory(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            story=conversation_text[:200] + "...",
            importance=0.3,
            tags=["auto-generated"],
            raw_context=conversation_text[:500]
        )
        return episode


def extract_semantic_memories(qdrant_client: QdrantClient, episodic_collection: str, semantic_collection: str, limit: int = 20) -> List[SemanticMemory]:
    """
    Extract semantic memories (general facts about user) from recent episodic memories
    """
    
    try:
        # Get recent episodes
        results = qdrant_client.scroll(
            collection_name=episodic_collection,
            limit=limit,
            with_payload=True,
            with_vectors=False
        )
        
        episodes = results[0]
        
        if not episodes:
            print("⚠️ No episodes found for semantic extraction")
            return []
        
        # Build context from episodes
        episode_summaries = []
        for ep in episodes:
            story = ep.payload.get("story", "")
            emotion = ep.payload.get("emotion", "")
            emotion_str = f" [{emotion}]" if emotion else ""
            episode_summaries.append(f"- {story}{emotion_str}")
        
        episodes_text = "\n".join(episode_summaries)
        
        # Extraction prompt
        prompt = f"""Analyze these conversation episodes and extract stable, general facts about the user.

EPISODES:
{episodes_text}

Extract semantic memories (general facts) in these categories:
1. **TRAITS**: Personality characteristics (e.g., "User is ambitious and hardworking")
2. **PREFERENCES**: Likes/dislikes, values (e.g., "User values work-life balance")
3. **FACTS**: Stable facts (e.g., "User is a software engineer at RBC")
4. **PATTERNS**: Behavioral patterns (e.g., "User tends to overthink social situations")
5. **RELATIONSHIPS**: Important people (e.g., "User has a supportive manager named Sarah")

For each semantic memory, provide:
- type: one of [trait, preference, fact, pattern, relationship]
- content: A clear, concise statement (1 sentence)
- confidence: 0.0-1.0 based on how strongly supported by episodes
- tags: 2-3 relevant tags

Return a JSON array of 5-10 semantic memories. Focus on the MOST IMPORTANT and RECURRING themes.
Return ONLY valid JSON array, no markdown."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        
        result = response.choices[0].message.content.strip()
        
        # Clean markdown
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        
        import json
        semantic_data = json.loads(result)
        
        # Create and store semantic memories
        semantic_memories = []
        episode_ids = [ep.id for ep in episodes[:10]]
        
        for item in semantic_data:
            try:
                memory = SemanticMemory(
                    id=str(uuid.uuid4()),
                    type=SemanticMemoryType(item.get("type", "fact")),
                    content=item.get("content", ""),
                    confidence=float(item.get("confidence", 0.7)),
                    source_episodes=episode_ids,
                    first_observed=datetime.now(),
                    last_updated=datetime.now(),
                    occurrence_count=len(episodes),
                    tags=item.get("tags", [])
                )
                
                # Store in Qdrant
                vector = get_embedding_model().embed_query(memory.content)
                
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
                
                qdrant_client.upsert(
                    collection_name=semantic_collection,
                    points=[
                        PointStruct(
                            id=memory.id,
                            vector=vector,
                            payload=payload
                        )
                    ]
                )
                
                semantic_memories.append(memory)
                print(f"✅ Stored semantic memory: {memory.content[:60]}...")
                
            except Exception as e:
                print(f"⚠️ Skipping invalid semantic memory: {e}")
                continue
        
        print(f"🧠 Extracted {len(semantic_memories)} semantic memories")
        return semantic_memories
        
    except Exception as e:
        print(f"❌ Semantic extraction error: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_semantic_context(qdrant_client: QdrantClient, semantic_collection: str, limit: int = 5) -> str:
    """
    Get general facts about user from semantic memory to inject into system prompt
    """
    
    try:
        # Get all semantic memories (or recent ones)
        results = qdrant_client.scroll(
            collection_name=semantic_collection,
            limit=limit,
            with_payload=True,
            with_vectors=False
        )
        
        memories = results[0]
        
        if not memories:
            return ""
        
        # Format as context
        context_parts = ["━━━ GENERAL FACTS ABOUT USER ━━━"]
        for mem in memories:
            content = mem.payload.get("content", "")
            mem_type = mem.payload.get("type", "")
            context_parts.append(f"• [{mem_type.upper()}] {content}")
        
        context_parts.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        return "\n".join(context_parts)
        
    except Exception as e:
        print(f"❌ Error getting semantic context: {e}")
        return ""
