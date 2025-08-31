"""
Semantic Search Module

Provides local semantic search capabilities for Rule Card corpus using semtools.
Implements hybrid approach: compiled rules (deterministic) + optional semantic search (flexible).

Key Components:
- CorpusManager: Rule card corpus rendering and versioning
- SemanticSearchInterface: Local semtools integration and search interface  
- FeatureFlags: Runtime retrieval configuration
- SearchResults: Result formatting and provenance tracking

Security Features:
- Local-only operation (no external API calls)
- Input sanitization and validation
- Resource limits and timeout controls
- Comprehensive audit logging
"""

__version__ = "0.1.0"
__author__ = "GenAI Security Agents"

# Core semantic search components
from .corpus_manager import CorpusManager

# Import other components when available
try:
    from .semantic_search import SemanticSearchInterface
    from .feature_flags import SemanticSearchFeatureFlags
    from .search_results import SemanticSearchResults
    
    __all__ = [
        'CorpusManager',
        'SemanticSearchInterface', 
        'SemanticSearchFeatureFlags',
        'SemanticSearchResults'
    ]
except ImportError:
    # Components not yet implemented
    __all__ = ['CorpusManager']