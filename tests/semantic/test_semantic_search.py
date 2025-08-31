"""
Test suite for SemanticSearch and SearchResults

Tests semantic search interface, result formatting, and security features.
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

from app.semantic.semantic_search import SemanticSearchInterface, SearchFilters, SearchConfiguration
from app.semantic.search_results import SearchMatch, SemanticSearchResults, UnifiedResults, SearchResultsAuditLogger


class TestSearchFilters:
    """Test SearchFilters functionality."""
    
    def test_search_filters_creation(self):
        """Test SearchFilters creation and serialization."""
        filters = SearchFilters(
            languages=['python', 'javascript'],
            categories=['authentication', 'secrets'],
            severity_levels=['high', 'critical'],
            confidence_threshold=0.7
        )
        
        assert filters.languages == ['python', 'javascript']
        assert filters.categories == ['authentication', 'secrets']
        assert filters.severity_levels == ['high', 'critical']
        assert filters.confidence_threshold == 0.7
        
        # Test serialization
        filters_dict = filters.to_dict()
        assert 'languages' in filters_dict
        assert 'confidence_threshold' in filters_dict


class TestSemanticSearchResults:
    """Test SemanticSearchResults functionality."""
    
    @pytest.fixture
    def sample_matches(self):
        """Create sample search matches for testing."""
        return [
            SearchMatch(
                content="High severity security rule content",
                confidence_score=0.9,
                source_rule_id="HIGH-001",
                source_file="high_rule.yml",
                source_type="yaml",
                snippet="High severity security guidance",
                category="authentication",
                severity="high"
            ),
            SearchMatch(
                content="Medium severity security rule content", 
                confidence_score=0.6,
                source_rule_id="MED-001",
                source_file="med_rule.yml",
                source_type="yaml",
                snippet="Medium severity security guidance",
                category="secrets",
                severity="medium"
            ),
            SearchMatch(
                content="Low severity security rule content",
                confidence_score=0.3,
                source_rule_id="LOW-001", 
                source_file="low_rule.yml",
                source_type="yaml",
                snippet="Low severity security guidance",
                category="web_security",
                severity="low"
            )
        ]
    
    def test_search_results_creation(self, sample_matches):
        """Test SemanticSearchResults creation."""
        query = "test security query"
        results = SemanticSearchResults(query, sample_matches)
        
        assert results.query == query
        assert len(results.results) == 3
        assert results.provenance is not None
        assert results.provenance.total_results == 3
    
    def test_high_confidence_filtering(self, sample_matches):
        """Test filtering by confidence threshold."""
        results = SemanticSearchResults("test", sample_matches)
        
        high_conf = results.get_high_confidence_results(0.7)
        assert len(high_conf) == 1
        assert high_conf[0].source_rule_id == "HIGH-001"
        
        medium_conf = results.get_high_confidence_results(0.5)
        assert len(medium_conf) == 2
    
    def test_severity_filtering(self, sample_matches):
        """Test filtering by severity level."""
        results = SemanticSearchResults("test", sample_matches)
        
        high_severity = results.get_results_by_severity("high")
        assert len(high_severity) == 1
        assert high_severity[0].severity == "high"
        
        medium_severity = results.get_results_by_severity("medium")
        assert len(medium_severity) == 1
        assert medium_severity[0].severity == "medium"
    
    def test_category_filtering(self, sample_matches):
        """Test filtering by security category.""" 
        results = SemanticSearchResults("test", sample_matches)
        
        auth_results = results.get_results_by_category("authentication")
        assert len(auth_results) == 1
        assert auth_results[0].category == "authentication"
        
        secrets_results = results.get_results_by_category("secrets")
        assert len(secrets_results) == 1
        assert secrets_results[0].category == "secrets"
    
    def test_top_results_sorting(self, sample_matches):
        """Test top results sorting by confidence."""
        results = SemanticSearchResults("test", sample_matches)
        
        top_2 = results.get_top_results(2)
        assert len(top_2) == 2
        assert top_2[0].confidence_score >= top_2[1].confidence_score
        assert top_2[0].source_rule_id == "HIGH-001"  # Highest confidence
    
    def test_ide_format_display(self, sample_matches):
        """Test IDE format display."""
        results = SemanticSearchResults("flask security", sample_matches)
        
        display = results.format_for_display("ide")
        
        assert "🔍 **Semantic Search Results**" in display
        assert "📝 Query: flask security" in display
        assert "📊 Results: 3 matches" in display
        assert "🎯 **High Confidence Matches:**" in display
        assert "HIGH-001" in display
    
    def test_console_format_display(self, sample_matches):
        """Test console format display."""
        results = SemanticSearchResults("test", sample_matches)
        
        display = results.format_for_display("console")
        
        assert "=== SEMANTIC SEARCH RESULTS ===" in display
        assert "Query: test" in display
        assert "Results: 3" in display
        assert "[0.90] HIGH-001" in display
    
    def test_json_format_display(self, sample_matches):
        """Test JSON format display."""
        results = SemanticSearchResults("test", sample_matches)
        
        json_display = results.format_for_display("json")
        data = json.loads(json_display)
        
        assert "query" in data
        assert "results" in data
        assert "provenance" in data
        assert "summary" in data
        assert len(data["results"]) == 3
        assert data["summary"]["total_results"] == 3
    
    def test_unified_results_merge(self, sample_matches):
        """Test merging with compiled rule results."""
        results = SemanticSearchResults("test", sample_matches)
        
        compiled_results = [
            {"id": "COMPILED-001", "title": "Compiled Rule", "severity": "critical"},
            {"id": "COMPILED-002", "title": "Another Rule", "severity": "high"}
        ]
        
        unified = results.merge_with_compiled_rules(compiled_results)
        
        assert isinstance(unified, UnifiedResults)
        assert len(unified.compiled_results) == 2
        assert len(unified.semantic_results) == 3
    
    def test_serialization_round_trip(self, sample_matches):
        """Test serialization and deserialization."""
        original = SemanticSearchResults("test query", sample_matches)
        
        # Convert to dict and back
        data_dict = original.to_dict()
        restored = SemanticSearchResults.from_dict(data_dict)
        
        assert restored.query == original.query
        assert len(restored.results) == len(original.results)
        assert restored.results[0].source_rule_id == original.results[0].source_rule_id


class TestUnifiedResults:
    """Test UnifiedResults functionality."""
    
    def test_unified_results_creation(self):
        """Test UnifiedResults creation."""
        compiled_results = [
            {"id": "COMP-001", "title": "Compiled Rule", "severity": "high"}
        ]
        
        semantic_results = [
            SearchMatch(
                content="Semantic match",
                confidence_score=0.8,
                source_rule_id="SEM-001",
                source_file="sem.yml",
                source_type="yaml",
                snippet="Semantic snippet",
                severity="medium"
            )
        ]
        
        unified = UnifiedResults(
            compiled_results=compiled_results,
            semantic_results=semantic_results,
            query="test",
            provenance=None
        )
        
        assert len(unified.compiled_results) == 1
        assert len(unified.semantic_results) == 1
        assert unified.query == "test"
    
    def test_unified_display_format(self):
        """Test unified display formatting."""
        compiled_results = [
            {"id": "COMP-001", "title": "Critical Rule", "severity": "critical"}
        ]
        
        semantic_results = [
            SearchMatch(
                content="High confidence match",
                confidence_score=0.8,
                source_rule_id="SEM-001",
                source_file="sem.yml",
                source_type="yaml",
                snippet="High confidence security guidance",
                severity="high"
            )
        ]
        
        unified = UnifiedResults(compiled_results, semantic_results, "test", None)
        display = unified.format_unified_display()
        
        assert "🔍 **Unified Security Analysis Results**" in display
        assert "⚡ **Compiled Rule Matches (Primary):**" in display
        assert "🔍 **Semantic Search Supplements (High Confidence):**" in display
        assert "COMP-001" in display
        assert "SEM-001" in display
    
    def test_get_all_rule_ids(self):
        """Test getting all rule IDs from unified results."""
        compiled_results = [
            {"id": "COMP-001", "title": "Rule 1"},
            {"id": "COMP-002", "title": "Rule 2"}
        ]
        
        semantic_results = [
            SearchMatch("content", 0.8, "SEM-001", "file", "yaml", "snippet"),
            SearchMatch("content", 0.7, "SEM-002", "file", "yaml", "snippet")
        ]
        
        unified = UnifiedResults(compiled_results, semantic_results, "test", None)
        rule_ids = unified.get_all_rule_ids()
        
        assert "COMP-001" in rule_ids
        assert "COMP-002" in rule_ids 
        assert "SEM-001" in rule_ids
        assert "SEM-002" in rule_ids
        assert len(rule_ids) == 4
    
    def test_get_highest_severity(self):
        """Test getting highest severity from all results."""
        compiled_results = [
            {"id": "COMP-001", "severity": "high"}
        ]
        
        semantic_results = [
            SearchMatch("content", 0.8, "SEM-001", "file", "yaml", "snippet", severity="critical")
        ]
        
        unified = UnifiedResults(compiled_results, semantic_results, "test", None)
        highest_severity = unified.get_highest_severity()
        
        assert highest_severity == "critical"


class TestSemanticSearchInterface:
    """Test SemanticSearchInterface functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_corpus(self, temp_dir):
        """Create sample corpus for testing."""
        corpus_data = {
            'content': """Rule ID: SECRET-001
Title: Hardcoded API Keys
Severity: critical
Requirement: API keys must not be hardcoded
Secure Practices:
  • Use environment variables for API keys
Avoid These Patterns:
  • Hardcoded API keys in source code
Detection Methods:
  semgrep: hardcoded-api-key
CWE: CWE-798
Source: secrets/api_key.yml
Type: yaml
==================================================
Rule ID: COOKIE-001  
Title: Secure Cookie Configuration
Severity: high
Requirement: Cookies must have security attributes
Secure Practices:
  • Set HttpOnly flag
  • Use Secure flag for HTTPS
Detection Methods:
  semgrep: cookie-security
Source: cookies/secure_config.yml
Type: yaml""",
            'metadata': {
                'version': '20250831_120000',
                'rule_count': 2,
                'size_bytes': 500
            }
        }
        
        corpus_dir = os.path.join(temp_dir, "corpus")
        os.makedirs(corpus_dir, exist_ok=True)
        
        corpus_file = os.path.join(corpus_dir, "corpus.json")
        with open(corpus_file, 'w') as f:
            json.dump(corpus_data, f)
        
        return corpus_dir
    
    @pytest.fixture
    def search_config(self, temp_dir):
        """Create test search configuration."""
        config_data = {
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
        
        config_file = os.path.join(temp_dir, "search_config.yaml")
        with open(config_file, 'w') as f:
            import yaml
            yaml.dump(config_data, f)
        
        return SearchConfiguration(config_file)
    
    def test_search_interface_initialization(self, sample_corpus, search_config):
        """Test SemanticSearchInterface initialization."""
        interface = SemanticSearchInterface(sample_corpus, search_config)
        
        assert interface.corpus_path == sample_corpus
        assert interface.max_query_time == 1.0
        assert interface.max_results == 50
        assert interface.input_sanitization is True
    
    def test_query_validation_success(self, sample_corpus, search_config):
        """Test successful query validation."""
        interface = SemanticSearchInterface(sample_corpus, search_config)
        
        valid_query = "api key security"
        sanitized = interface._validate_query(valid_query)
        
        assert sanitized == "api key security"
    
    def test_query_validation_sanitization(self, sample_corpus, search_config):
        """Test query sanitization."""
        interface = SemanticSearchInterface(sample_corpus, search_config)
        
        # Test sanitization of dangerous characters
        dangerous_query = "api<script>alert('xss')</script>key"
        sanitized = interface._validate_query(dangerous_query)
        
        assert "<script>" not in sanitized
        assert "alert" in sanitized  # Content preserved, just tags removed
    
    def test_query_validation_length_limit(self, sample_corpus, search_config):
        """Test query length validation."""
        interface = SemanticSearchInterface(sample_corpus, search_config)
        
        # Test query exceeding length limit
        long_query = "a" * 2000  # Exceeds 1000 char limit
        
        with pytest.raises(ValueError, match="exceeds length limit"):
            interface._validate_query(long_query)
    
    def test_query_validation_empty_query(self, sample_corpus, search_config):
        """Test empty query validation."""
        interface = SemanticSearchInterface(sample_corpus, search_config)
        
        with pytest.raises(ValueError, match="non-empty string"):
            interface._validate_query("")
        
        with pytest.raises(ValueError, match="non-empty string"):
            interface._validate_query(None)
    
    def test_fallback_search_functionality(self, sample_corpus, search_config):
        """Test fallback search when semtools unavailable."""
        interface = SemanticSearchInterface(sample_corpus, search_config)
        
        # Test search for API key content
        matches = interface._fallback_search("api key")
        
        assert len(matches) > 0
        assert any("SECRET-001" in match.source_rule_id for match in matches)
        assert any("api" in match.content.lower() for match in matches)
    
    def test_fallback_search_confidence_scoring(self, sample_corpus, search_config):
        """Test confidence scoring in fallback search."""
        interface = SemanticSearchInterface(sample_corpus, search_config)
        
        # Search for exact phrase should have higher confidence
        exact_matches = interface._fallback_search("API keys")
        partial_matches = interface._fallback_search("keys")
        
        if exact_matches and partial_matches:
            # Exact matches should generally have higher confidence
            max_exact_conf = max(m.confidence_score for m in exact_matches)
            max_partial_conf = max(m.confidence_score for m in partial_matches)
            
            assert max_exact_conf >= max_partial_conf
    
    def test_search_query_end_to_end(self, sample_corpus, search_config):
        """Test complete search query execution."""
        interface = SemanticSearchInterface(sample_corpus, search_config)
        
        results = interface.search_query("cookie security")
        
        assert isinstance(results, SemanticSearchResults)
        assert results.query == "cookie security"
        assert len(results.results) >= 0
        assert results.provenance is not None
        assert results.provenance.search_method in ["semtools", "fallback"]
    
    def test_search_with_filters(self, sample_corpus, search_config):
        """Test search with filters applied."""
        interface = SemanticSearchInterface(sample_corpus, search_config)
        
        filters = SearchFilters(
            severity_levels=["critical"],
            confidence_threshold=0.2
        )
        
        results = interface.search_query("security", filters)
        
        # Should only return critical severity results
        for result in results.results:
            if result.severity:
                assert result.severity in ["critical"]
    
    def test_context_aware_search(self, sample_corpus, search_config):
        """Test context-aware search functionality."""
        interface = SemanticSearchInterface(sample_corpus, search_config)
        
        python_code = """
import flask
from flask import session

app = flask.Flask(__name__)
app.secret_key = "hardcoded-secret"
"""
        
        results = interface.search_by_context(python_code, "python")
        
        assert isinstance(results, SemanticSearchResults)
        assert len(results.results) >= 0
    
    def test_rule_explanation(self, sample_corpus, search_config):
        """Test rule explanation functionality."""
        interface = SemanticSearchInterface(sample_corpus, search_config)
        
        code_snippet = 'api_key = "sk-1234567890"'
        results = interface.explain_rule_match("SECRET-001", code_snippet)
        
        assert isinstance(results, SemanticSearchResults)
        assert "SECRET-001" in results.query or any("SECRET-001" in r.source_rule_id for r in results.results)
    
    def test_availability_check(self, sample_corpus, search_config):
        """Test semantic search availability check."""
        interface = SemanticSearchInterface(sample_corpus, search_config)
        
        is_available = interface.is_available()
        assert isinstance(is_available, bool)
    
    def test_search_statistics(self, sample_corpus, search_config):
        """Test search statistics retrieval."""
        interface = SemanticSearchInterface(sample_corpus, search_config)
        
        stats = interface.get_search_statistics()
        
        assert isinstance(stats, dict)
        assert 'semtools_available' in stats
        assert 'search_engine_ready' in stats
        assert 'corpus_available' in stats
        assert 'performance_settings' in stats
    
    def test_search_caching(self, sample_corpus, search_config):
        """Test search result caching."""
        interface = SemanticSearchInterface(sample_corpus, search_config)
        
        # First search
        results1 = interface.search_query("test query")
        
        # Second search (should use cache)
        results2 = interface.search_query("test query")
        
        # Results should be identical
        assert results1.query == results2.query
        assert len(results1.results) == len(results2.results)


class TestSearchResultsAuditLogger:
    """Test SearchResultsAuditLogger functionality."""
    
    @pytest.fixture
    def temp_log_file(self):
        """Create temporary log file for testing."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.log')
        temp_file.close()
        yield temp_file.name
        os.unlink(temp_file.name)
    
    def test_audit_logger_creation(self, temp_log_file):
        """Test audit logger initialization."""
        logger = SearchResultsAuditLogger(temp_log_file)
        
        assert logger.log_file == temp_log_file
        assert logger.audit_logger is not None
    
    def test_search_query_logging(self, temp_log_file):
        """Test search query audit logging."""
        logger = SearchResultsAuditLogger(temp_log_file)
        
        logger.log_search_query("test query", "test_user")
        
        # Verify log file content
        with open(temp_log_file, 'r') as f:
            log_content = f.read()
        
        assert "SEARCH_QUERY" in log_content
        assert "test query" in log_content
        assert "test_user" in log_content
    
    def test_search_results_logging(self, temp_log_file):
        """Test search results audit logging."""
        logger = SearchResultsAuditLogger(temp_log_file)
        
        # Create sample results
        matches = [
            SearchMatch("content", 0.8, "TEST-001", "file", "yaml", "snippet")
        ]
        results = SemanticSearchResults("test query", matches)
        
        logger.log_search_results(results)
        
        # Verify log file content
        with open(temp_log_file, 'r') as f:
            log_content = f.read()
        
        assert "SEARCH_RESULTS" in log_content
        assert "test query" in log_content
        assert "Results: 1" in log_content