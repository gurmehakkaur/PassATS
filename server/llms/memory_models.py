"""
Memory Models for Gossip AI
Defines the structure for Episodic, Semantic, and Working Memory
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class MemoryType(str, Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"


class EmotionType(str, Enum):
    HAPPY = "happy"
    SAD = "sad"
    ANXIOUS = "anxious"
    EXCITED = "excited"
    FRUSTRATED = "frustrated"
    NEUTRAL = "neutral"
    CONFUSED = "confused"
    PROUD = "proud"


# ========== EPISODIC MEMORY ==========
class EpisodicMemory(BaseModel):
    """
    Represents a single interaction episode - the 'story' of what happened
    """
    id: str = Field(description="Unique identifier for this episode")
    timestamp: datetime = Field(default_factory=datetime.now)
    story: str = Field(description="2-3 sentence narrative of what happened")
    emotion: Optional[EmotionType] = Field(default=None, description="Primary emotion detected")
    key_entities: List[str] = Field(default_factory=list, description="People, projects, or things mentioned")
    user_intent: Optional[str] = Field(default=None, description="What the user wanted or was trying to do")
    importance: float = Field(default=0.5, ge=0.0, le=1.0, description="How significant this episode is (0-1)")
    tags: List[str] = Field(default_factory=list, description="Searchable tags for this episode")
    raw_context: Optional[str] = Field(default=None, description="Optional: raw conversation snippet")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "ep_1701234567890",
                "timestamp": "2024-11-30T13:25:00",
                "story": "User messaged a cloud architect for a coffee chat, got great insights and now wants to be an architect.",
                "emotion": "ambitious",
                "key_entities": ["coffee-chat", "career"],
                "user_intent": "wanted to learn about different professions",
                "importance": 0.8,
                "tags": ["career","networking", "social"],
                 }
        }


# ========== SEMANTIC MEMORY ==========
class SemanticMemoryType(str, Enum):
    TRAIT = "trait"              # Personality traits
    PREFERENCE = "preference"    # Likes/dislikes
    FACT = "fact"               # Stable facts about user
    PATTERN = "pattern"         # Behavioral patterns
    RELATIONSHIP = "relationship" # Info about relationships


class SemanticMemory(BaseModel):
    """
    Represents extracted facts, traits, and patterns about the user
    """
    id: str = Field(description="Unique identifier")
    type: SemanticMemoryType = Field(description="Type of semantic knowledge")
    content: str = Field(description="The actual fact/trait/pattern")
    confidence: float = Field(default=0.7, ge=0.0, le=1.0, description="Confidence in this knowledge (0-1)")
    source_episodes: List[str] = Field(default_factory=list, description="Episode IDs that support this")
    first_observed: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    occurrence_count: int = Field(default=1, description="How many times this pattern appeared")
    tags: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "sem_1701234567890",
                "type": "trait",
                "content": "User tends to overthink responses from people she cares about",
                "confidence": 0.85,
                "source_episodes": ["ep_001", "ep_045", "ep_089"],
                "first_observed": "2024-11-01T10:00:00",
                "last_updated": "2024-11-30T13:25:00",
                "occurrence_count": 12,
                "tags": ["personality", "anxiety", "relationships"]
            }
        }


# ========== WORKING MEMORY ==========
class WorkingMemory(BaseModel):
    """
    Assembled context for the current conversation
    Combines relevant episodic memories + semantic facts
    """
    episodic_memories: List[EpisodicMemory] = Field(default_factory=list)
    semantic_facts: List[SemanticMemory] = Field(default_factory=list)
    relevance_scores: Dict[str, float] = Field(default_factory=dict, description="Memory ID -> relevance score")
    
    def to_context_string(self) -> str:
        """
        Converts working memory into a formatted string for LLM context
        """
        context_parts = []
        
        if self.semantic_facts:
            context_parts.append("=== WHAT I KNOW ABOUT YOU ===")
            for fact in self.semantic_facts:
                context_parts.append(f"• {fact.content}")
        
        if self.episodic_memories:
            context_parts.append("\n=== RELEVANT PAST CONVERSATIONS ===")
            for memory in self.episodic_memories:
                timestamp_str = memory.timestamp.strftime("%b %d, %Y")
                emotion_str = f" [{memory.emotion.value}]" if memory.emotion else ""
                context_parts.append(f"• {timestamp_str}{emotion_str}: {memory.story}")
        
        return "\n".join(context_parts)


# ========== MEMORY STORAGE PAYLOADS ==========
class EpisodicPayload(BaseModel):
    """Payload structure for Qdrant episodic memory storage"""
    story: str
    emotion: Optional[str] = None
    key_entities: List[str] = []
    user_intent: Optional[str] = None
    importance: float
    tags: List[str] = []
    timestamp: float
    raw_context: Optional[str] = None


class SemanticPayload(BaseModel):
    """Payload structure for Qdrant semantic memory storage"""
    type: str
    content: str
    confidence: float
    source_episodes: List[str] = []
    first_observed: float
    last_updated: float
    occurrence_count: int
    tags: List[str] = []


# ========== API MODELS ==========
class StoreEpisodeRequest(BaseModel):
    """Request to store a new episodic memory"""
    user_message: str
    assistant_response: str
    conversation_history: Optional[List[Dict[str, str]]] = None


class StoreEpisodeResponse(BaseModel):
    """Response after storing an episode"""
    status: str
    episode_id: str
    story: str
    importance: float
    emotion: Optional[str] = None


class ExtractSemanticRequest(BaseModel):
    """Request to extract semantic memories from episodes"""
    min_episodes: int = Field(default=10, description="Minimum episodes needed for extraction")
    lookback_days: Optional[int] = Field(default=30, description="How far back to look")


class ExtractSemanticResponse(BaseModel):
    """Response after semantic extraction"""
    status: str
    extracted_count: int
    semantic_memories: List[SemanticMemory]
