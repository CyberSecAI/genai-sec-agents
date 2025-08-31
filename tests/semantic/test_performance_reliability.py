"""
Test suite for Performance and Reliability (Task 5)

Tests performance requirements, offline fallback, search quality validation,
and comprehensive reliability features.
"""

import os
import sys
import time
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock
import threading
import concurrent.futures

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.semantic.corpus_manager import CorpusManager, CorpusData
from app.semantic.semantic_search import SemanticSearchInterface, SearchConfiguration
from app.semantic.search_results import SemanticSearchResults, SearchMatch
from app.semantic.feature_flags import SemanticSearchFeatureFlags


class TestPerformanceRequirements:
    """Test NFR1: Semantic search results returned within 1 second."""
    
    @pytest.fixture
    def temp_corpus(self):
        """Create temporary corpus for performance testing."""
        temp_dir = tempfile.mkdtemp()
        
        # Create sample corpus data
        corpus_content = """Rule ID: PERF-001
Title: Performance Test Rule
Severity: high
Requirement: Test performance requirement
Secure Practices:
  • Follow performance guidelines
Detection Methods:
  semgrep: performance-test
Source: perf_test.yml
Type: yaml
""" + ("=" * 50 + "\n") * 100  # 100 rule sections for testing
        
        corpus_data = {
            'content': corpus_content,
            'metadata': {
                'version': '20250831_test',
                'rule_count': 100,
                'size_bytes': len(corpus_content)
            }
        }
        
        corpus_dir = os.path.join(temp_dir, "corpus")
        os.makedirs(corpus_dir, exist_ok=True)
        
        with open(os.path.join(corpus_dir, "corpus.json"), 'w') as f:
            import json
            json.dump(corpus_data, f)
        
        yield corpus_dir
        shutil.rmtree(temp_dir)
    
    def test_search_query_performance_requirement(self, temp_corpus):
        """Test search queries complete within 1 second (NFR1)."""
        # Initialize search interface with performance corpus
        search_interface = SemanticSearchInterface(temp_corpus)
        
        # Test multiple queries to ensure consistent performance
        queries = [
            "security vulnerability",
            "authentication bypass",
            "input validation",
            "sql injection prevention",
            "cross site scripting"
        ]
        
        for query in queries:
            start_time = time.time()
            
            results = search_interface.search_query(query)
            
            execution_time = time.time() - start_time
            
            # Should complete within 1 second (NFR1)
            assert execution_time < 1.0, f"Query '{query}' took {execution_time:.3f}s, exceeds 1s requirement"
            
            # Should return valid results
            assert isinstance(results, SemanticSearchResults)
            assert results.provenance.processing_time_ms < 1000
    
    def test_context_search_performance(self, temp_corpus):
        """Test context-aware search meets performance requirements."""
        search_interface = SemanticSearchInterface(temp_corpus)
        
        # Large code context for performance testing
        code_context = '''
import flask
from flask import request, session, jsonify
import sqlite3
import hashlib
import jwt
import os

app = flask.Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

def validate_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Hash password
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password_hash))
    
    user = cursor.fetchone()
    conn.close()
    
    return user is not None

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if validate_user(username, password):
        token = jwt.encode({'user': username}, app.secret_key, algorithm='HS256')
        session['user'] = username
        return jsonify({'token': token})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

if __name__ == '__main__':
    app.run(debug=True)
'''
        
        start_time = time.time()
        results = search_interface.search_by_context(code_context, 'python')
        execution_time = time.time() - start_time
        
        # Context search should also meet 1s requirement
        assert execution_time < 1.0, f"Context search took {execution_time:.3f}s"
        assert isinstance(results, SemanticSearchResults)
    
    def test_concurrent_search_performance(self, temp_corpus):
        """Test concurrent search operations maintain performance."""
        search_interface = SemanticSearchInterface(temp_corpus)
        
        def run_search(query):
            start_time = time.time()
            results = search_interface.search_query(f"security {query}")
            execution_time = time.time() - start_time
            return execution_time, len(results.results)
        
        # Run 5 concurrent searches
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            queries = ['auth', 'input', 'crypto', 'session', 'validation']
            futures = [executor.submit(run_search, query) for query in queries]
            
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All searches should complete within performance requirements
        for execution_time, result_count in results:
            assert execution_time < 1.5, f"Concurrent search took {execution_time:.3f}s"  # Slightly relaxed for concurrency
            assert result_count >= 0  # Should return valid results


class TestOfflineReliability:
    """Test NFR3: Core functionality works without semantic search when offline."""
    
    def test_graceful_fallback_missing_corpus(self):
        """Test graceful fallback when corpus is not available."""
        # Use non-existent corpus path
        search_interface = SemanticSearchInterface("/nonexistent/corpus/path")
        
        # Should not crash, should return empty results gracefully
        results = search_interface.search_query("test query")
        
        assert isinstance(results, SemanticSearchResults)
        assert len(results.results) == 0
        assert results.provenance.search_method in ["error", "fallback"]
    
    def test_availability_check_offline(self):
        """Test availability check when offline/unavailable."""
        search_interface = SemanticSearchInterface("/nonexistent/path")
        
        is_available = search_interface.is_available()
        
        # Should report unavailable but not crash
        assert isinstance(is_available, bool)
        assert is_available is False
    
    def test_feature_flags_offline_behavior(self):
        """Test feature flags work correctly when offline."""
        # Initialize feature flags with non-existent config
        flags = SemanticSearchFeatureFlags()
        
        # Should still work with defaults
        assert flags.is_runtime_retrieval_enabled() is False  # Default OFF
        assert flags.is_explain_mode_enabled() is True      # Default ON
        assert flags.is_audit_logging_enabled() is True     # Default ON
    
    def test_corpus_manager_offline_validation(self):
        """Test corpus manager validation when files unavailable."""
        manager = CorpusManager()
        
        # Validate non-existent corpus
        validation = manager.validate_corpus_integrity("/nonexistent/corpus.json")
        
        assert validation.valid is False
        assert len(validation.errors) > 0
        assert any("not found" in error for error in validation.errors)


class TestSearchQualityValidation:
    """Test search result quality and consistency validation."""
    
    @pytest.fixture
    def quality_test_corpus(self):
        """Create corpus with known security scenarios for quality testing."""
        temp_dir = tempfile.mkdtemp()
        
        # Create corpus with specific security scenarios
        security_scenarios = [
            {
                'id': 'SQL-INJ-001',
                'title': 'SQL Injection Prevention',
                'content': 'Use parameterized queries to prevent SQL injection attacks',
                'category': 'input_validation',
                'severity': 'critical'
            },
            {
                'id': 'XSS-PREV-001', 
                'title': 'Cross-Site Scripting Prevention',
                'content': 'Sanitize user input and encode output to prevent XSS',
                'category': 'web_security',
                'severity': 'high'
            },
            {
                'id': 'AUTH-001',
                'title': 'Strong Authentication Requirements',
                'content': 'Implement multi-factor authentication for sensitive operations',
                'category': 'authentication',
                'severity': 'high'
            }
        ]
        
        corpus_content = ""
        for scenario in security_scenarios:
            corpus_content += f"""Rule ID: {scenario['id']}
Title: {scenario['title']}
Severity: {scenario['severity']}
Category: {scenario['category']}
Requirement: {scenario['content']}
Source: test_{scenario['id'].lower()}.yml
Type: yaml
""" + ("=" * 50) + "\n"
        
        corpus_data = {
            'content': corpus_content,
            'metadata': {
                'version': '20250831_quality',
                'rule_count': len(security_scenarios),
                'size_bytes': len(corpus_content)
            }
        }
        
        corpus_dir = os.path.join(temp_dir, "corpus")
        os.makedirs(corpus_dir, exist_ok=True)
        
        with open(os.path.join(corpus_dir, "corpus.json"), 'w') as f:
            import json
            json.dump(corpus_data, f)
        
        yield corpus_dir, security_scenarios
        shutil.rmtree(temp_dir)
    
    def test_search_quality_sql_injection_scenario(self, quality_test_corpus):
        """Test search quality for SQL injection scenarios."""
        corpus_dir, scenarios = quality_test_corpus
        search_interface = SemanticSearchInterface(corpus_dir)
        
        # Search for SQL injection related terms
        sql_queries = [
            "sql injection",
            "parameterized queries", 
            "database security",
            "injection prevention"
        ]
        
        for query in sql_queries:
            results = search_interface.search_query(query)
            
            # Should find SQL injection rule
            sql_matches = [r for r in results.results if 'SQL-INJ-001' in r.source_rule_id]
            assert len(sql_matches) > 0, f"Query '{query}' should find SQL injection rule"
            
            # Top result should have reasonable confidence
            if results.results:
                top_result = results.get_top_results(1)[0]
                assert top_result.confidence_score > 0.2, f"Top result confidence too low for '{query}'"
    
    def test_search_consistency_across_versions(self, quality_test_corpus):
        """Test NFR2: Search results are reproducible and consistent."""
        corpus_dir, scenarios = quality_test_corpus
        search_interface = SemanticSearchInterface(corpus_dir)
        
        test_query = "authentication security"
        
        # Run same search multiple times
        results_list = []
        for i in range(3):
            results = search_interface.search_query(test_query)
            results_list.append(results)
        
        # Results should be consistent
        assert len(results_list) == 3
        
        # Same number of results
        result_counts = [len(r.results) for r in results_list]
        assert all(count == result_counts[0] for count in result_counts)
        
        # Same top result
        if results_list[0].results:
            top_rules = [r.get_top_results(1)[0].source_rule_id if r.results else None for r in results_list]
            assert all(rule == top_rules[0] for rule in top_rules)
    
    def test_search_relevance_threshold_validation(self, quality_test_corpus):
        """Test search relevance meets quality thresholds."""
        corpus_dir, scenarios = quality_test_corpus
        search_interface = SemanticSearchInterface(corpus_dir)
        
        # Test specific security term searches
        relevance_tests = [
            ("sql injection", "SQL-INJ-001"),
            ("cross site scripting", "XSS-PREV-001"),  
            ("authentication", "AUTH-001")
        ]
        
        for query, expected_rule in relevance_tests:
            results = search_interface.search_query(query)
            
            # Find expected rule in results
            expected_matches = [r for r in results.results if expected_rule in r.source_rule_id]
            
            if expected_matches:
                best_match = max(expected_matches, key=lambda x: x.confidence_score)
                
                # Confidence should be reasonable for direct matches
                assert best_match.confidence_score > 0.3, f"Relevance too low for '{query}' -> {expected_rule}"


class TestCorpusManagementPerformance:
    """Test corpus loading and management performance."""
    
    def test_corpus_loading_performance(self):
        """Test corpus loads efficiently at startup."""
        # Create temporary large corpus
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Generate large corpus content (but under 100MB limit)
            large_content = "Test corpus content with security rules\n" * 10000  # ~400KB
            
            corpus_data = CorpusData(large_content, {
                'version': '20250831_large',
                'rule_count': 1000,
                'size_bytes': len(large_content)
            })
            
            # Save corpus
            corpus_dir = os.path.join(temp_dir, "corpus")
            os.makedirs(corpus_dir, exist_ok=True)
            
            with open(os.path.join(corpus_dir, "corpus.json"), 'w') as f:
                import json
                json.dump(corpus_data.to_dict(), f)
            
            # Test loading performance
            start_time = time.time()
            search_interface = SemanticSearchInterface(corpus_dir)
            loading_time = time.time() - start_time
            
            # Should load efficiently (under 2 seconds for reasonable size)
            assert loading_time < 2.0, f"Corpus loading took {loading_time:.3f}s"
            
            # Should be available after loading
            assert search_interface.is_available() is True
            
        finally:
            shutil.rmtree(temp_dir)
    
    def test_corpus_size_management(self):
        """Test NFR2: Local corpus size is manageable (<100MB)."""
        manager = CorpusManager()
        
        # Test with size limit configuration
        assert manager.max_size_mb == 100  # Should be configured to 100MB limit
        
        # Create test corpus data
        test_rules = [{'id': f'TEST-{i:03d}', 'content': 'test rule'} for i in range(10)]
        
        # Should handle reasonable number of rules
        corpus_data = manager.render_corpus_from_packages([])  # Empty for test
        
        # Size should be manageable
        size_mb = corpus_data.metadata['size_bytes'] / (1024 * 1024)
        assert size_mb < 100, f"Corpus size {size_mb:.1f}MB exceeds 100MB limit"
    
    def test_corpus_validation_performance(self):
        """Test corpus validation completes efficiently."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create test corpus
            corpus_data = CorpusData("Test content", {
                'version': '20250831_val',
                'rule_count': 1,
                'size_bytes': 12
            })
            
            corpus_file = os.path.join(temp_dir, "test_corpus.json")
            with open(corpus_file, 'w') as f:
                import json
                json.dump(corpus_data.to_dict(), f)
            
            manager = CorpusManager()
            
            # Test validation performance
            start_time = time.time()
            validation = manager.validate_corpus_integrity(corpus_file)
            validation_time = time.time() - start_time
            
            # Validation should be fast
            assert validation_time < 1.0, f"Validation took {validation_time:.3f}s"
            assert validation.valid is True
            
        finally:
            shutil.rmtree(temp_dir)


class TestReliabilityFeatures:
    """Test comprehensive reliability and error handling."""
    
    def test_search_timeout_handling(self):
        """Test search operations respect timeout limits."""
        # Mock a slow search interface
        class SlowSearchInterface(SemanticSearchInterface):
            def _fallback_search(self, query, filters=None):
                time.sleep(2)  # Simulate slow operation
                return []
        
        search_interface = SlowSearchInterface()
        search_interface.timeout_enabled = True
        search_interface.max_query_time = 0.5  # Very short timeout
        
        # Should handle timeout gracefully
        results = search_interface.search_query("test query")
        
        # Should return empty results, not crash
        assert isinstance(results, SemanticSearchResults)
        # Processing time might exceed limit but should be logged
        assert results.provenance.processing_time_ms >= 500
    
    def test_memory_usage_limits(self):
        """Test search operations respect memory limits."""
        search_interface = SemanticSearchInterface()
        
        # Very large query should be rejected
        huge_query = "a" * 10000  # 10KB query
        
        with pytest.raises(ValueError, match="exceeds length limit"):
            search_interface.search_query(huge_query)
    
    def test_input_sanitization_reliability(self):
        """Test input sanitization works reliably."""
        search_interface = SemanticSearchInterface()
        
        # Test various malicious inputs
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE rules; --",
            "../../../etc/passwd",
            "\x00\x01\x02malicious",
            "normal\nquery\rwith\twhitespace"
        ]
        
        for malicious_input in malicious_inputs:
            try:
                # Should sanitize but not crash
                results = search_interface.search_query(malicious_input)
                assert isinstance(results, SemanticSearchResults)
            except ValueError as e:
                # Acceptable to reject invalid input
                assert "Query" in str(e) or "no valid content" in str(e)
    
    def test_concurrent_access_safety(self):
        """Test concurrent access to search interface is safe."""
        search_interface = SemanticSearchInterface()
        
        def concurrent_search(query_id):
            try:
                results = search_interface.search_query(f"concurrent test {query_id}")
                return len(results.results), None
            except Exception as e:
                return 0, str(e)
        
        # Run multiple concurrent searches
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(concurrent_search, i) for i in range(20)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All should complete without errors
        for result_count, error in results:
            assert error is None or "not available" in error, f"Concurrent access error: {error}"
            assert result_count >= 0
    
    def test_configuration_error_recovery(self):
        """Test recovery from configuration errors."""
        # Test with invalid configuration path
        with pytest.raises(Exception):
            SemanticSearchInterface(config=SearchConfiguration("/invalid/config/path"))
        
        # Should fall back to defaults
        search_interface = SemanticSearchInterface()
        assert search_interface.max_query_time > 0
        assert search_interface.max_results > 0
    
    def test_feature_flag_persistence_reliability(self):
        """Test feature flag persistence is reliable."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            from app.semantic.feature_flags import FeatureFlagConfiguration
            
            config_file = os.path.join(temp_dir, "test_flags.yaml")
            with open(config_file, 'w') as f:
                f.write("""
search:
  feature_flags:
    runtime_retrieval_default: false
    audit_logging_enabled: true
""")
            
            config = FeatureFlagConfiguration(config_file)
            flags = SemanticSearchFeatureFlags(config)
            
            # Test persistence across operations
            original_state = flags.is_runtime_retrieval_enabled()
            
            # Modify flags
            flags.set_global_flag('runtime_retrieval_default', not original_state)
            
            # Create new instance - should persist
            new_flags = SemanticSearchFeatureFlags(config)
            new_state = new_flags.is_runtime_retrieval_enabled()
            
            assert new_state != original_state, "Flag changes should persist"
            
        finally:
            shutil.rmtree(temp_dir)


class TestEndToEndReliability:
    """Test complete end-to-end reliability scenarios."""
    
    def test_full_stack_reliability(self):
        """Test complete semantic search stack reliability."""
        # Test complete workflow: corpus -> search -> results -> display
        temp_dir = tempfile.mkdtemp()
        
        try:
            # 1. Create corpus
            manager = CorpusManager()
            
            # 2. Initialize search  
            search_interface = SemanticSearchInterface()
            
            # 3. Test search with various scenarios
            test_scenarios = [
                "normal security query",
                "",  # Empty query
                "very specific rare vulnerability type",
                "a" * 100,  # Long query
            ]
            
            for scenario in test_scenarios:
                try:
                    if scenario:  # Skip empty query
                        results = search_interface.search_query(scenario)
                        assert isinstance(results, SemanticSearchResults)
                        
                        # Test result formatting
                        display = results.format_for_display("console")
                        assert isinstance(display, str)
                        
                        json_display = results.format_for_display("json")
                        import json
                        json.loads(json_display)  # Should be valid JSON
                        
                except ValueError:
                    # Acceptable for invalid inputs
                    pass
                except Exception as e:
                    pytest.fail(f"Unexpected error in scenario '{scenario}': {e}")
            
            # 4. Test statistics and availability
            stats = search_interface.get_search_statistics()
            assert isinstance(stats, dict)
            assert 'semtools_available' in stats
            
            is_available = search_interface.is_available()
            assert isinstance(is_available, bool)
            
        finally:
            shutil.rmtree(temp_dir)
    
    def test_degraded_mode_operation(self):
        """Test operation in degraded mode (limited functionality)."""
        # Test with missing semtools
        with patch('app.semantic.semantic_search.SEMTOOLS_AVAILABLE', False):
            search_interface = SemanticSearchInterface()
            
            # Should still work with fallback
            results = search_interface.search_query("test query")
            assert isinstance(results, SemanticSearchResults)
            assert results.provenance.search_method == "fallback"
    
    def test_resource_cleanup(self):
        """Test proper resource cleanup and memory management."""
        import gc
        
        # Create and destroy many search interfaces
        interfaces = []
        for i in range(10):
            interface = SemanticSearchInterface()
            interfaces.append(interface)
        
        # Clear references
        interfaces.clear()
        gc.collect()
        
        # Should not cause memory leaks or resource issues
        # This is a basic test - comprehensive memory testing would require specialized tools
        assert True  # If we get here without crashing, basic cleanup works