"""
Memory Management API Endpoints
Provides manual control over episodic and semantic memory systems
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

from memory_models import (
    EpisodicMemory,
    SemanticMemory,
    StoreEpisodeRequest,
    StoreEpisodeResponse,
    ExtractSemanticRequest,
    ExtractSemanticResponse
)
from episodic_memory import (
    save_interaction_as_episode,
    retrieve_episodes,
    store_episode,
    create_episodic_story
)
from semantic_memory import (
    run_semantic_extraction,
    retrieve_semantic_memories,
    get_recent_episodes
)
from working_memory import assemble_working_memory

router = APIRouter(prefix="/memory", tags=["Memory Management"])


# ========== EPISODIC MEMORY ENDPOINTS ==========

@router.post("/episode/store", response_model=StoreEpisodeResponse)
async def store_episode_endpoint(request: StoreEpisodeRequest):
    """
    Manually store an interaction as an episodic memory
    """
    try:
        result = save_interaction_as_episode(
            user_message=request.user_message,
            assistant_response=request.assistant_response,
            conversation_history=request.conversation_history
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store episode: {str(e)}")


class SearchEpisodesRequest(BaseModel):
    query: str
    limit: int = 5
    min_importance: float = 0.0


class SearchEpisodesResponse(BaseModel):
    episodes: List[EpisodicMemory]
    count: int


@router.post("/episode/search", response_model=SearchEpisodesResponse)
async def search_episodes(request: SearchEpisodesRequest):
    """
    Search for episodic memories by semantic similarity
    """
    try:
        episodes = retrieve_episodes(
            query=request.query,
            limit=request.limit,
            min_importance=request.min_importance
        )
        return SearchEpisodesResponse(
            episodes=episodes,
            count=len(episodes)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


# ========== SEMANTIC MEMORY ENDPOINTS ==========

@router.post("/semantic/extract", response_model=ExtractSemanticResponse)
async def extract_semantic_endpoint(request: ExtractSemanticRequest):
    """
    Manually trigger semantic memory extraction from episodic memories
    """
    try:
        result = run_semantic_extraction(
            min_episodes=request.min_episodes,
            lookback_days=request.lookback_days or 30
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


class SearchSemanticRequest(BaseModel):
    query: str
    limit: int = 5
    min_confidence: float = 0.5


class SearchSemanticResponse(BaseModel):
    memories: List[SemanticMemory]
    count: int


@router.post("/semantic/search", response_model=SearchSemanticResponse)
async def search_semantic(request: SearchSemanticRequest):
    """
    Search for semantic memories (facts, traits, patterns)
    """
    try:
        memories = retrieve_semantic_memories(
            query=request.query,
            limit=request.limit,
            min_confidence=request.min_confidence
        )
        return SearchSemanticResponse(
            memories=memories,
            count=len(memories)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


# ========== WORKING MEMORY ENDPOINT ==========

class WorkingMemoryRequest(BaseModel):
    query: str
    episodic_limit: int = 5
    semantic_limit: int = 5


class WorkingMemoryResponse(BaseModel):
    episodic_count: int
    semantic_count: int
    context: str
    episodic_memories: List[EpisodicMemory]
    semantic_facts: List[SemanticMemory]


@router.post("/working", response_model=WorkingMemoryResponse)
async def get_working_memory(request: WorkingMemoryRequest):
    """
    Assemble working memory for a given query
    Shows what context would be provided to the LLM
    """
    try:
        working_memory = assemble_working_memory(
            query=request.query,
            episodic_limit=request.episodic_limit,
            semantic_limit=request.semantic_limit
        )
        
        return WorkingMemoryResponse(
            episodic_count=len(working_memory.episodic_memories),
            semantic_count=len(working_memory.semantic_facts),
            context=working_memory.to_context_string(),
            episodic_memories=working_memory.episodic_memories,
            semantic_facts=working_memory.semantic_facts
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to assemble working memory: {str(e)}")


# ========== STATS ENDPOINT ==========

class MemoryStatsResponse(BaseModel):
    total_episodes: int
    total_semantic: int
    recent_episodes_30d: int
    high_importance_episodes: int


@router.get("/stats", response_model=MemoryStatsResponse)
async def get_memory_stats():
    """
    Get statistics about stored memories
    """
    try:
        from qdrant_client import QdrantClient
        import os
        
        qdrant = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        
        # Get collection info
        episodic_info = qdrant.get_collection("episodic_memory")
        semantic_info = qdrant.get_collection("semantic_memory")
        
        # Get recent episodes
        recent_episodes = get_recent_episodes(lookback_days=30, min_count=1)
        
        # Get high importance episodes
        high_importance = retrieve_episodes(query="", limit=100, min_importance=0.8)
        
        return MemoryStatsResponse(
            total_episodes=episodic_info.points_count,
            total_semantic=semantic_info.points_count,
            recent_episodes_30d=len(recent_episodes),
            high_importance_episodes=len(high_importance)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
