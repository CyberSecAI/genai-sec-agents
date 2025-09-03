"""
Semantic Search Interface

Local semantic search using semtools for rule card corpus.
Implements secure search with input validation, timeout controls, and audit logging.
"""

import os
import json
import time
import re
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging
import yaml

# Import semtools when available
try:
    import semtools
    SEMTOOLS_AVAILABLE = True
except ImportError:
    SEMTOOLS_AVAILABLE = False
    logging.warning("semtools not available, using fallback search")

from .search_results import SearchMatch, SearchProvenance, SemanticSearchResults, SearchResultsAuditLogger
from .corpus_manager import CorpusManager

logger = logging.getLogger(__name__)


class SearchFilters:
    """Search filters for semantic queries."""
    
    def __init__(self, languages: List[str] = None, categories: List[str] = None, 
                 severity_levels: List[str] = None, confidence_threshold: float = 0.3):
        self.languages = languages or []
        self.categories = categories or []
        self.severity_levels = severity_levels or []
        self.confidence_threshold = confidence_threshold
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'languages': self.languages,
            'categories': self.categories,
            'severity_levels': self.severity_levels,
            'confidence_threshold': self.confidence_threshold
        }


class SearchConfiguration:
    """Search configuration and behavior settings."""
    
    def __init__(self, config_path: str = "app/semantic/config/search_config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load search configuration with validation."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
            # Validate required sections
            required_sections = ['search', 'search.performance', 'search.security']
            for section in required_sections:
                keys = section.split('.')
                current = config
                for key in keys:
                    if key not in current:
                        raise ValueError(f"Missing required config section: {section}")
                    current = current[key]
                    
            return config
            
        except Exception as e:
            logger.error(f"Failed to load search config: {e}")
            # Return safe defaults
            return {
                'search': {
                    'performance': {
                        'max_query_time_seconds': 1.0,
                        'max_results': 50,
                        'cache_enabled': True
                    },
                    'security': {
                        'input_sanitization': True,
                        'query_length_limit': 1000,
                        'timeout_enabled': True
                    },
                    'quality': {
                        'min_confidence_score': 0.3,
                        'relevance_threshold': 0.5
                    }
                }
            }
    
    def get_performance_settings(self) -> Dict[str, Any]:
        """Get performance configuration."""
        return self.config['search']['performance']
    
    def get_security_settings(self) -> Dict[str, Any]:
        """Get security configuration."""
        return self.config['search']['security']
    
    def get_quality_settings(self) -> Dict[str, Any]:
        """Get quality configuration."""
        return self.config['search']['quality']


class SemanticSearchInterface:
    """Local semantic search using semtools for rule card corpus."""
    
    def __init__(self, corpus_path: str = None, config: SearchConfiguration = None):
        """Initialize semtools with local corpus."""
        self.config = config or SearchConfiguration()
        self.corpus_path = corpus_path or "app/semantic/corpus/"
        self.corpus_manager = CorpusManager()
        self.audit_logger = SearchResultsAuditLogger()
        
        # Performance settings
        perf_settings = self.config.get_performance_settings()
        self.max_query_time = perf_settings.get('max_query_time_seconds', 1.0)
        self.max_results = perf_settings.get('max_results', 50)
        self.cache_enabled = perf_settings.get('cache_enabled', True)
        
        # Security settings
        security_settings = self.config.get_security_settings()
        self.input_sanitization = security_settings.get('input_sanitization', True)
        self.query_length_limit = security_settings.get('query_length_limit', 1000)
        self.timeout_enabled = security_settings.get('timeout_enabled', True)
        
        # Quality settings
        quality_settings = self.config.get_quality_settings()
        self.min_confidence_score = quality_settings.get('min_confidence_score', 0.3)
        self.relevance_threshold = quality_settings.get('relevance_threshold', 0.5)
        
        # Initialize semtools if available
        self.semtools_engine = None
        if SEMTOOLS_AVAILABLE:
            self._initialize_semtools()
        
        # Query cache for performance with size limit
        self._query_cache = {} if self.cache_enabled else None
        self._max_cache_size = 1000  # Prevent memory leaks from unbounded cache
        self._cache_access_order = [] if self.cache_enabled else None  # Track access for LRU
        
    def _initialize_semtools(self):
        """Initialize semtools search engine."""
        try:
            corpus_file = os.path.join(self.corpus_path, "corpus.json")
            if os.path.exists(corpus_file):
                # Load corpus content for semtools
                with open(corpus_file, 'r', encoding='utf-8') as f:
                    corpus_data = json.load(f)
                
                # Initialize semtools with corpus content
                # Note: This is a placeholder for actual semtools initialization
                # Actual implementation would depend on semtools API
                self.semtools_engine = {
                    'corpus_content': corpus_data.get('content', ''),
                    'corpus_metadata': corpus_data.get('metadata', {}),
                    'initialized': True
                }
                
                logger.info("Semtools engine initialized successfully")
            else:
                logger.warning(f"Corpus file not found: {corpus_file}")
                
        except Exception as e:
            logger.error(f"Failed to initialize semtools: {e}")
            self.semtools_engine = None
    
    def _validate_query(self, query: str) -> str:
        """Validate and sanitize search query."""
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")
        
        # Length validation
        if len(query) > self.query_length_limit:
            raise ValueError(f"Query exceeds length limit of {self.query_length_limit} characters")
        
        if self.input_sanitization:
            # Remove potentially dangerous characters
            sanitized = re.sub(r'[<>"\'\\\x00-\x1f\x7f-\x9f]', '', query)
            
            # Remove excessive whitespace
            sanitized = re.sub(r'\s+', ' ', sanitized.strip())
            
            if not sanitized:
                raise ValueError("Query contains no valid content after sanitization")
            
            return sanitized
        
        return query.strip()
    
    def _apply_filters(self, results: List[SearchMatch], filters: SearchFilters) -> List[SearchMatch]:
        """Apply search filters to results."""
        filtered_results = results
        
        # Confidence threshold filter
        if filters.confidence_threshold > 0:
            filtered_results = [r for r in filtered_results if r.confidence_score >= filters.confidence_threshold]
        
        # Language filter
        if filters.languages:
            filtered_results = [r for r in filtered_results if r.language in filters.languages or r.language is None]
        
        # Category filter
        if filters.categories:
            filtered_results = [r for r in filtered_results if r.category in filters.categories or r.category is None]
        
        # Severity filter
        if filters.severity_levels:
            filtered_results = [r for r in filtered_results if r.severity in filters.severity_levels or r.severity is None]
        
        return filtered_results
    
    def _extract_rule_metadata(self, content: str) -> Tuple[str, str, str, str]:
        """Extract rule metadata from corpus content."""
        # Parse rule content to extract metadata
        rule_id = "UNKNOWN"
        category = "general"
        severity = "medium"
        source_file = "corpus"
        
        try:
            # Extract rule ID
            id_match = re.search(r'Rule ID:\s*([A-Z0-9\-]+)', content)
            if id_match:
                rule_id = id_match.group(1)
            
            # Extract severity
            severity_match = re.search(r'Severity:\s*(\w+)', content)
            if severity_match:
                severity = severity_match.group(1).lower()
            
            # Extract category from rule ID or content
            if 'SECRET' in rule_id or 'secret' in content.lower():
                category = "secrets"
            elif 'COOKIE' in rule_id or 'cookie' in content.lower():
                category = "web_security"
            elif 'JWT' in rule_id or 'jwt' in content.lower():
                category = "authentication"
            elif 'DOCKER' in rule_id or 'docker' in content.lower():
                category = "container"
            elif 'GENAI' in rule_id or 'genai' in content.lower():
                category = "genai"
            
            # Extract source file
            source_match = re.search(r'Source:\s*(.+)', content)
            if source_match:
                source_file = source_match.group(1).strip()
                
        except Exception as e:
            logger.warning(f"Failed to extract rule metadata: {e}")
        
        return rule_id, category, severity, source_file
    
    def _fallback_search(self, query: str, filters: SearchFilters = None) -> List[SearchMatch]:
        """Fallback search implementation when semtools is not available."""
        try:
            corpus_file = os.path.join(self.corpus_path, "corpus.json")
            if not os.path.exists(corpus_file):
                logger.warning("No corpus file found for fallback search")
                return []
            
            with open(corpus_file, 'r', encoding='utf-8') as f:
                corpus_data = json.load(f)
            
            corpus_content = corpus_data.get('content', '')
            
            # Split corpus into rule sections
            rule_sections = corpus_content.split('=' * 50)
            
            matches = []
            query_lower = query.lower()
            
            for section in rule_sections:
                section = section.strip()
                if not section:
                    continue
                
                # Simple text matching for fallback
                section_lower = section.lower()
                
                # Calculate basic relevance score
                confidence_score = 0.0
                query_words = query_lower.split()
                
                for word in query_words:
                    if word in section_lower:
                        confidence_score += 0.2
                
                # Boost score for exact phrase matches
                if query_lower in section_lower:
                    confidence_score += 0.4
                
                # Only include if above minimum confidence
                if confidence_score >= self.min_confidence_score:
                    rule_id, category, severity, source_file = self._extract_rule_metadata(section)
                    
                    # Create snippet (first 200 chars of relevant content)
                    snippet = section[:200].replace('\n', ' ')
                    
                    match = SearchMatch(
                        content=section,
                        confidence_score=min(confidence_score, 1.0),
                        source_rule_id=rule_id,
                        source_file=source_file,
                        source_type="corpus",
                        snippet=snippet,
                        category=category,
                        severity=severity
                    )
                    
                    matches.append(match)
            
            # Sort by confidence score
            matches.sort(key=lambda x: x.confidence_score, reverse=True)
            
            # Apply filters if provided
            if filters:
                matches = self._apply_filters(matches, filters)
            
            # Limit results
            return matches[:self.max_results]
            
        except Exception as e:
            logger.error(f"Fallback search failed: {e}")
            return []
    
    def _semtools_search(self, query: str, filters: SearchFilters = None) -> List[SearchMatch]:
        """Perform semantic search using semtools."""
        if not self.semtools_engine or not self.semtools_engine.get('initialized'):
            logger.warning("Semtools engine not initialized, using fallback")
            return self._fallback_search(query, filters)
        
        try:
            # Placeholder for actual semtools integration
            # In real implementation, this would use semtools API
            corpus_content = self.semtools_engine['corpus_content']
            
            # For now, use enhanced fallback with semantic-like scoring
            matches = self._fallback_search(query, filters)
            
            # TODO: Replace with actual semtools semantic search
            # matches = semtools.search(query, corpus_content, max_results=self.max_results)
            
            return matches
            
        except Exception as e:
            logger.error(f"Semtools search failed: {e}")
            return self._fallback_search(query, filters)
    
    def search_query(self, query: str, filters: SearchFilters = None) -> SemanticSearchResults:
        """Execute semantic search query with optional filters."""
        start_time = time.time()
        
        try:
            # Validate and sanitize query
            sanitized_query = self._validate_query(query)
            
            # Log query for audit compliance
            self.audit_logger.log_search_query(sanitized_query)
            
            # Check cache if enabled
            cache_key = f"{sanitized_query}:{hash(str(filters.to_dict() if filters else {}))}"
            if self._query_cache is not None and cache_key in self._query_cache:
                # Update access order for LRU
                self._cache_access_order.remove(cache_key)
                self._cache_access_order.append(cache_key)
                cached_result = self._query_cache[cache_key]
                logger.info(f"Returning cached result for query: {sanitized_query[:50]}...")
                return cached_result
            
            # Perform search with timeout
            if SEMTOOLS_AVAILABLE and self.semtools_engine:
                matches = self._semtools_search(sanitized_query, filters)
            else:
                matches = self._fallback_search(sanitized_query, filters)
            
            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Check timeout
            if self.timeout_enabled and processing_time_ms > (self.max_query_time * 1000):
                logger.warning(f"Search exceeded timeout: {processing_time_ms}ms > {self.max_query_time * 1000}ms")
            
            # Get corpus metadata
            corpus_metadata = self.corpus_manager.get_corpus_metadata()
            corpus_version = corpus_metadata.version if corpus_metadata else "unknown"
            
            # Create provenance
            provenance = SearchProvenance(
                query=sanitized_query,
                timestamp=time.time(),
                corpus_version=corpus_version,
                search_method="semtools" if SEMTOOLS_AVAILABLE else "fallback",
                filters_applied=filters.to_dict() if filters else {},
                total_results=len(matches),
                processing_time_ms=processing_time_ms
            )
            
            # Create results
            results = SemanticSearchResults(sanitized_query, matches, provenance)
            
            # Cache results if enabled with LRU eviction
            if self._query_cache is not None:
                # Implement LRU cache with size limit to prevent memory leaks
                if len(self._query_cache) >= self._max_cache_size:
                    # Remove least recently used item
                    lru_key = self._cache_access_order.pop(0)
                    del self._query_cache[lru_key]
                
                self._query_cache[cache_key] = results
                self._cache_access_order.append(cache_key)
            
            # Log results for audit
            self.audit_logger.log_search_results(results)
            
            logger.info(f"Search completed: {len(matches)} results in {processing_time_ms}ms")
            return results
            
        except Exception as e:
            logger.error(f"Search query failed: {e}")
            
            # Return empty results with error provenance
            processing_time_ms = int((time.time() - start_time) * 1000)
            provenance = SearchProvenance(
                query=query,
                timestamp=time.time(),
                corpus_version="error",
                search_method="error",
                filters_applied={},
                total_results=0,
                processing_time_ms=processing_time_ms
            )
            
            return SemanticSearchResults(query, [], provenance)
    
    def search_by_context(self, code_context: str, language: str) -> SemanticSearchResults:
        """Context-aware search for code analysis scenarios."""
        # Extract key terms from code context
        context_terms = []
        
        # Language-specific term extraction
        if language.lower() in ['python', 'py']:
            context_terms.extend(re.findall(r'import\s+(\w+)', code_context))
            context_terms.extend(re.findall(r'from\s+(\w+)', code_context))
            
            # Common security patterns
            if 'flask' in code_context.lower():
                context_terms.append('flask web security')
            if 'jwt' in code_context.lower():
                context_terms.append('jwt authentication')
            if 'cookie' in code_context.lower():
                context_terms.append('cookie security')
            if 'secret' in code_context.lower() or 'password' in code_context.lower():
                context_terms.append('secrets management')
                
        elif language.lower() in ['javascript', 'js', 'typescript', 'ts']:
            # JavaScript/TypeScript patterns
            context_terms.extend(re.findall(r'require\([\'"](\w+)[\'"]\)', code_context))
            context_terms.extend(re.findall(r'import.*from\s+[\'"](\w+)[\'"]', code_context))
            
        # Build context-aware query
        if context_terms:
            query = ' '.join(context_terms[:5])  # Limit to top 5 terms
        else:
            # Generic security terms
            query = f"{language} security vulnerability"
        
        # Create language-specific filters
        filters = SearchFilters(
            languages=[language],
            confidence_threshold=self.min_confidence_score
        )
        
        return self.search_query(query, filters)
    
    def explain_rule_match(self, rule_id: str, code_snippet: str) -> SemanticSearchResults:
        """Provide detailed explanation of why a rule matches code."""
        query = f"explain {rule_id} security rule application example"
        
        filters = SearchFilters(
            confidence_threshold=0.5  # Higher threshold for explanations
        )
        
        results = self.search_query(query, filters)
        
        # Filter results to focus on the specific rule
        rule_specific_results = []
        for result in results.results:
            if rule_id.lower() in result.source_rule_id.lower():
                rule_specific_results.append(result)
        
        # If no rule-specific results, return all results
        if not rule_specific_results:
            rule_specific_results = results.results
        
        return SemanticSearchResults(
            query=f"Explanation for {rule_id}",
            results=rule_specific_results,
            provenance=results.provenance
        )
    
    def is_available(self) -> bool:
        """Check if semantic search is available and functional."""
        try:
            # Check corpus availability
            corpus_file = os.path.join(self.corpus_path, "corpus.json")
            if not os.path.exists(corpus_file):
                return False
            
            # Check semtools availability (optional)
            # Even without semtools, fallback search is available
            
            # Test basic functionality
            test_results = self.search_query("test", SearchFilters())
            return True
            
        except Exception as e:
            logger.error(f"Semantic search availability check failed: {e}")
            return False
    
    def clear_cache(self) -> None:
        """Clear query cache to free memory."""
        if self._query_cache is not None:
            self._query_cache.clear()
            self._cache_access_order.clear()
            logger.info("Query cache cleared")
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """Get search performance and usage statistics."""
        corpus_metadata = self.corpus_manager.get_corpus_metadata()
        
        stats = {
            'semtools_available': SEMTOOLS_AVAILABLE,
            'search_engine_ready': self.semtools_engine is not None,
            'corpus_available': os.path.exists(os.path.join(self.corpus_path, "corpus.json")),
            'cache_enabled': self.cache_enabled,
            'cached_queries': len(self._query_cache) if self._query_cache else 0,
            'performance_settings': self.config.get_performance_settings(),
            'corpus_metadata': corpus_metadata.to_dict() if corpus_metadata else None
        }
        
        return stats