"""
Memory Search Package

Modules:
    search_engine.py   — Entry point (orchestrator)
    query_parser.py    — Parse + expand queries
    keyword_search.py  — FTS5 search
    memory_ranker.py   — Multi-factor ranking

Usage:
    from core.memory.search import MemorySearchEngine

    engine = MemorySearchEngine(backend=sqlite_backend)
    results = engine.search("پروژه Atlas")
"""

from core.memory.search.search_engine import MemorySearchEngine
from core.memory.search.query_parser import QueryParser
from core.memory.search.keyword_search import KeywordSearch
from core.memory.search.memory_ranker import MemoryRanker

__all__ = [
    "MemorySearchEngine",
    "QueryParser",
    "KeywordSearch",
    "MemoryRanker",
]
