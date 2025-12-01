"""
Memory Functions - Re-exports from episodic_memory and semantic_memory modules
For backwards compatibility with chat.py
"""

# Import and re-export from episodic_memory
from episodic_memory import (
    init_episodic_collection,
    get_or_create_journal_label,
    create_episodic_memory
)

# Import and re-export from semantic_memory
from semantic_memory import (
    init_semantic_collection,
    extract_semantic_memories,
    get_semantic_context
)

__all__ = [
    'init_episodic_collection',
    'get_or_create_journal_label',
    'create_episodic_memory',
    'init_semantic_collection',
    'extract_semantic_memories',
    'get_semantic_context'
]

