"""
Working Memory System
Assembles relevant episodic + semantic memories for current conversation context
"""

from typing import List, Optional, Dict, Any
from memory_models import WorkingMemory, EpisodicMemory, SemanticMemory
from episodic_memory import retrieve_episodes
from semantic_memory import retrieve_semantic_memories


def assemble_working_memory(
    query: str,
    episodic_limit: int = 5,
    semantic_limit: int = 5,
    min_importance: float = 0.3,
    min_confidence: float = 0.6
) -> WorkingMemory:
    """
    Assemble working memory for the current conversation
    
    This retrieves:
    1. Top-K most relevant episodic memories (stories)
    2. Top-K most relevant semantic facts (traits, preferences, patterns)
    
    Args:
        query: Current user query/message
        episodic_limit: Max episodic memories to retrieve
        semantic_limit: Max semantic memories to retrieve
        min_importance: Minimum importance for episodic memories
        min_confidence: Minimum confidence for semantic memories
        
    Returns:
        WorkingMemory object with assembled context
    """
    
    # 1. Retrieve episodic memories
    episodic_memories = retrieve_episodes(
        query=query,
        limit=episodic_limit,
        min_importance=min_importance
    )
    
    # 2. Retrieve semantic memories
    semantic_facts = retrieve_semantic_memories(
        query=query,
        limit=semantic_limit,
        min_confidence=min_confidence
    )
    
    # 3. Calculate relevance scores (based on retrieval order for now)
    relevance_scores = {}
    
    for i, ep in enumerate(episodic_memories):
        relevance_scores[ep.id] = 1.0 - (i / max(len(episodic_memories), 1))
    
    for i, sem in enumerate(semantic_facts):
        relevance_scores[sem.id] = 1.0 - (i / max(len(semantic_facts), 1))
    
    # 4. Assemble working memory
    working_memory = WorkingMemory(
        episodic_memories=episodic_memories,
        semantic_facts=semantic_facts,
        relevance_scores=relevance_scores
    )
    
    return working_memory


def get_memory_context_for_llm(query: str) -> str:
    """
    Convenience function to get formatted memory context string for LLM
    
    Args:
        query: Current user query
        
    Returns:
        Formatted context string ready to inject into system prompt
    """
    working_memory = assemble_working_memory(query)
    return working_memory.to_context_string()


def get_detailed_working_memory(
    query: str,
    include_high_importance: bool = True,
    include_recent: bool = True
) -> WorkingMemory:
    """
    Advanced working memory assembly with multiple retrieval strategies
    
    Args:
        query: Current user query
        include_high_importance: Also retrieve high-importance episodes regardless of relevance
        include_recent: Also retrieve very recent episodes
        
    Returns:
        WorkingMemory with combined results
    """
    
    # Base semantic retrieval
    working_memory = assemble_working_memory(query)
    
    # Optional: Add high-importance episodes
    if include_high_importance:
        high_importance_episodes = retrieve_episodes(
            query="",  # Empty query to get by importance only
            limit=3,
            min_importance=0.8
        )
        
        # Add if not already present
        existing_ids = {ep.id for ep in working_memory.episodic_memories}
        for ep in high_importance_episodes:
            if ep.id not in existing_ids:
                working_memory.episodic_memories.append(ep)
                working_memory.relevance_scores[ep.id] = 0.9  # High score for important memories
    
    return working_memory
