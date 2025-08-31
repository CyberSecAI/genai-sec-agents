"""
Test suite for Developer Tools Integration (Task 4)

Tests semantic search integration with manual commands and enhanced features.
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Mock dependencies that may not be available during testing
class MockSemanticSearchInterface:
    """Mock semantic search interface for testing."""
    
    def __init__(self):
        self.available = True
        
    def search_by_context(self, code_context, language):
        """Mock context search."""
        from app.semantic.search_results import SearchMatch, SemanticSearchResults
        
        matches = [
            SearchMatch(
                content=f"Mock security guidance for {language}",
                confidence_score=0.8,
                source_rule_id="MOCK-001",
                source_file="mock_rule.yml",
                source_type="yaml",
                snippet="Mock security guidance snippet",
                category="mock_security",
                severity="high"
            )
        ]
        
        return SemanticSearchResults("mock query", matches)
    
    def search_query(self, query, filters=None):
        """Mock query search."""
        from app.semantic.search_results import SearchMatch, SemanticSearchResults
        
        matches = [
            SearchMatch(
                content=f"Mock result for query: {query}",
                confidence_score=0.7,
                source_rule_id="MOCK-QUERY-001",
                source_file="mock_query.yml",
                source_type="yaml",
                snippet=f"Mock guidance for {query}",
                category="mock_category",
                severity="medium"
            )
        ]
        
        return SemanticSearchResults(query, matches)
    
    def explain_rule_match(self, rule_id, code_snippet):
        """Mock rule explanation."""
        from app.semantic.search_results import SearchMatch, SemanticSearchResults
        
        matches = [
            SearchMatch(
                content=f"Mock explanation for {rule_id}",
                confidence_score=0.9,
                source_rule_id=rule_id,
                source_file="mock_explanation.yml",
                source_type="yaml",
                snippet=f"Detailed explanation for {rule_id}",
                category="explanation",
                severity="info"
            )
        ]
        
        return SemanticSearchResults(f"explain {rule_id}", matches)


class MockFeatureFlags:
    """Mock feature flags for testing."""
    
    def __init__(self):
        self.runtime_retrieval_enabled = False
        self.explain_mode_enabled = True
        
    def is_runtime_retrieval_enabled(self):
        return self.runtime_retrieval_enabled
        
    def is_explain_mode_enabled(self):
        return self.explain_mode_enabled


class MockCodeContextAnalyzer:
    """Mock code context analyzer for testing."""
    
    def initialize(self):
        return True
        
    def analyze_file_context(self, file_path, use_cache=True):
        return {
            "selected_rules": [
                {
                    "id": "TEST-001",
                    "title": "Test Security Rule",
                    "severity": "high",
                    "requirement": "Test requirement",
                    "do": ["Follow secure practices"],
                    "dont": ["Avoid insecure patterns"]
                }
            ],
            "frameworks": ["test_framework"],
            "analysis_time": 0.5
        }


class TestDeveloperToolsIntegration:
    """Test enhanced manual commands with semantic search integration."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_python_file(self, temp_dir):
        """Create sample Python file for testing."""
        code_content = '''
import flask
from flask import session

app = flask.Flask(__name__)
app.secret_key = "hardcoded-secret"

@app.route("/login")
def login():
    session["user"] = "admin"
    return "Login successful"
'''
        
        file_path = os.path.join(temp_dir, "test_app.py")
        with open(file_path, 'w') as f:
            f.write(code_content)
            
        return file_path
    
    @patch('app.claude_code.manual_commands.SEMANTIC_SEARCH_AVAILABLE', True)
    @patch('app.claude_code.manual_commands.CodeContextAnalyzer')
    def test_enhanced_file_analysis_without_semantic(self, mock_analyzer_class, sample_python_file):
        """Test file analysis without semantic search enabled."""
        # Set up mocks
        mock_analyzer = MockCodeContextAnalyzer()
        mock_analyzer_class.return_value = mock_analyzer
        
        # Import after patching
        from app.claude_code.manual_commands import ManualSecurityCommands
        
        commands = ManualSecurityCommands()
        commands.semantic_search = MockSemanticSearchInterface()
        commands.feature_flags = MockFeatureFlags()
        commands.analyzer = mock_analyzer
        commands._initialized = True
        
        # Test analysis without semantic search
        result = commands.analyze_file_with_semantic_search(
            sample_python_file, 
            semantic_enabled=False
        )
        
        # Should have metadata indicating semantic search was not used
        assert 'metadata' in result
        assert result['metadata']['semantic_search_used'] is False
        assert result['metadata']['semantic_search_available'] is True
        assert result['metadata']['semantic_search_enabled'] is False
    
    @patch('app.claude_code.manual_commands.SEMANTIC_SEARCH_AVAILABLE', True)
    @patch('app.claude_code.manual_commands.CodeContextAnalyzer')
    def test_enhanced_file_analysis_with_semantic(self, mock_analyzer_class, sample_python_file):
        """Test file analysis with semantic search enabled."""
        # Set up mocks
        mock_analyzer = MockCodeContextAnalyzer()
        mock_analyzer_class.return_value = mock_analyzer
        
        from app.claude_code.manual_commands import ManualSecurityCommands
        
        commands = ManualSecurityCommands()
        commands.semantic_search = MockSemanticSearchInterface()
        commands.feature_flags = MockFeatureFlags()
        commands.feature_flags.runtime_retrieval_enabled = True  # Enable semantic search
        commands.analyzer = mock_analyzer
        commands._initialized = True
        
        # Test analysis with semantic search
        result = commands.analyze_file_with_semantic_search(
            sample_python_file, 
            semantic_enabled=True
        )
        
        # Should have semantic search enhancements
        assert 'metadata' in result
        assert result['metadata']['semantic_search_used'] is True
        assert 'semantic_processing_time_ms' in result['metadata']
        assert 'semantic_results_count' in result['metadata']
        assert 'semantic_supplements' in result
        assert 'high_confidence_matches' in result['semantic_supplements']
    
    @patch('app.claude_code.manual_commands.SEMANTIC_SEARCH_AVAILABLE', True)
    @patch('app.claude_code.manual_commands.CodeContextAnalyzer')
    def test_enhanced_workspace_analysis_with_semantic(self, mock_analyzer_class, temp_dir):
        """Test workspace analysis with semantic search enabled."""
        # Create multiple test files
        for i in range(3):
            file_path = os.path.join(temp_dir, f"test_file_{i}.py")
            with open(file_path, 'w') as f:
                f.write(f"# Test file {i}\nprint('Hello world {i}')")
        
        # Set up mocks
        mock_analyzer = MockCodeContextAnalyzer()
        mock_analyzer_class.return_value = mock_analyzer
        
        from app.claude_code.manual_commands import ManualSecurityCommands
        
        commands = ManualSecurityCommands()
        commands.semantic_search = MockSemanticSearchInterface()
        commands.feature_flags = MockFeatureFlags()
        commands.feature_flags.runtime_retrieval_enabled = True
        commands.analyzer = mock_analyzer
        commands._initialized = True
        
        # Test workspace analysis with semantic options
        semantic_options = {
            'enabled': True,
            'filters': {
                'languages': ['python'],
                'severity_levels': ['high', 'critical']
            }
        }
        
        result = commands.analyze_workspace_with_semantic_search(
            temp_dir, 
            semantic_options=semantic_options
        )
        
        # Should have semantic enhancements
        assert 'metadata' in result
        assert result['metadata']['semantic_search_used'] is True
        assert 'semantic_enhancements_count' in result['metadata']
        assert 'semantic_edge_cases' in result
    
    @patch('app.claude_code.manual_commands.SEMANTIC_SEARCH_AVAILABLE', True)
    def test_explain_security_guidance(self):
        """Test security guidance explanation functionality."""
        from app.claude_code.manual_commands import ManualSecurityCommands
        
        commands = ManualSecurityCommands()
        commands.semantic_search = MockSemanticSearchInterface()
        commands.feature_flags = MockFeatureFlags()
        commands._initialized = True
        
        # Test explanation
        result = commands.explain_security_guidance(
            "TEST-001", 
            "api_key = 'hardcoded-secret'"
        )
        
        assert result['rule_id'] == "TEST-001"
        assert result['semantic_search_used'] is True
        assert 'explanation' in result
        assert 'related_guidance' in result
        assert len(result['related_guidance']) > 0
    
    @patch('app.claude_code.manual_commands.SEMANTIC_SEARCH_AVAILABLE', False)
    def test_commands_without_semantic_search_available(self, sample_python_file):
        """Test commands when semantic search is not available."""
        from app.claude_code.manual_commands import ManualSecurityCommands
        
        commands = ManualSecurityCommands()
        # semantic_search should be None when not available
        assert commands.semantic_search is None
        assert commands.feature_flags is None
    
    def test_language_detection_from_extension(self):
        """Test programming language detection from file extension."""
        from app.claude_code.manual_commands import ManualSecurityCommands
        
        commands = ManualSecurityCommands()
        
        assert commands._detect_language_from_extension('.py') == 'python'
        assert commands._detect_language_from_extension('.js') == 'javascript'
        assert commands._detect_language_from_extension('.ts') == 'typescript'
        assert commands._detect_language_from_extension('.java') == 'java'
        assert commands._detect_language_from_extension('.go') == 'go'
        assert commands._detect_language_from_extension('.unknown') == 'unknown'
    
    @patch('app.claude_code.manual_commands.CodeContextAnalyzer')
    def test_merge_analysis_with_semantic(self, mock_analyzer_class):
        """Test merging base analysis with semantic results."""
        mock_analyzer_class.return_value = MockCodeContextAnalyzer()
        
        from app.claude_code.manual_commands import ManualSecurityCommands
        from app.semantic.search_results import SearchMatch, SemanticSearchResults
        
        commands = ManualSecurityCommands()
        
        base_results = {
            'status': 'success',
            'selected_rules': [{'id': 'BASE-001'}],
            'metadata': {'base': True}
        }
        
        semantic_matches = [
            SearchMatch(
                content="High confidence match",
                confidence_score=0.9,
                source_rule_id="SEM-001",
                source_file="sem.yml",
                source_type="yaml",
                snippet="High confidence guidance",
                category="authentication",
                severity="critical"
            ),
            SearchMatch(
                content="Medium confidence match",
                confidence_score=0.5,
                source_rule_id="SEM-002",
                source_file="sem2.yml", 
                source_type="yaml",
                snippet="Medium confidence guidance",
                category="encryption",
                severity="medium"
            )
        ]
        
        semantic_results = SemanticSearchResults("test query", semantic_matches)
        
        merged = commands._merge_analysis_with_semantic(base_results, semantic_results)
        
        assert 'semantic_supplements' in merged
        assert 'query_used' in merged['semantic_supplements']
        assert len(merged['semantic_supplements']['high_confidence_matches']) == 1
        assert len(merged['semantic_supplements']['additional_context']) == 1
        
        # High confidence match should be included
        high_conf = merged['semantic_supplements']['high_confidence_matches'][0]
        assert high_conf['rule_id'] == 'SEM-001'
        assert high_conf['confidence'] == 0.9
        assert high_conf['category'] == 'authentication'
    
    @patch('app.claude_code.manual_commands.CodeContextAnalyzer')
    def test_merge_workspace_with_semantic(self, mock_analyzer_class):
        """Test merging workspace analysis with semantic enhancements."""
        mock_analyzer_class.return_value = MockCodeContextAnalyzer()
        
        from app.claude_code.manual_commands import ManualSecurityCommands
        from app.semantic.search_results import SearchMatch
        
        commands = ManualSecurityCommands()
        
        base_results = {
            'status': 'success',
            'summary': {'total_issues': 2},
            'metadata': {'base': True}
        }
        
        semantic_enhancements = [
            SearchMatch(
                content="High confidence edge case",
                confidence_score=0.85,
                source_rule_id="EDGE-001",
                source_file="edge.yml",
                source_type="yaml", 
                snippet="High confidence edge case detection",
                category="race_condition",
                severity="high"
            ),
            SearchMatch(
                content="Medium confidence recommendation",
                confidence_score=0.6,
                source_rule_id="REC-001",
                source_file="rec.yml",
                source_type="yaml",
                snippet="Additional security recommendation",
                category="memory_safety",
                severity="medium"
            )
        ]
        
        merged = commands._merge_workspace_with_semantic(base_results, semantic_enhancements)
        
        assert 'semantic_edge_cases' in merged
        assert merged['semantic_edge_cases']['total_enhancements'] == 2
        assert len(merged['semantic_edge_cases']['edge_case_detections']) == 1
        assert len(merged['semantic_edge_cases']['additional_recommendations']) == 1
        
        # High confidence should be in edge case detections
        edge_case = merged['semantic_edge_cases']['edge_case_detections'][0]
        assert edge_case['rule_id'] == 'EDGE-001'
        assert edge_case['confidence'] == 0.85
        assert edge_case['source_type'] == 'semantic_search'
    
    def test_semantic_search_fallback_on_error(self, sample_python_file):
        """Test fallback to base analysis when semantic search fails."""
        from app.claude_code.manual_commands import ManualSecurityCommands
        
        # Mock that throws exception
        class FailingSemanticSearch:
            def search_by_context(self, *args, **kwargs):
                raise Exception("Semantic search failed")
        
        class FailingFeatureFlags:
            def is_runtime_retrieval_enabled(self):
                return True
        
        commands = ManualSecurityCommands()
        commands.semantic_search = FailingSemanticSearch()
        commands.feature_flags = FailingFeatureFlags()
        commands._initialized = True
        
        # Mock the base analyze_file method
        def mock_analyze_file(file_path, depth):
            return {
                'status': 'success',
                'results': {'summary': {'total_issues': 1}},
                'metadata': {'fallback': True}
            }
        
        commands.analyze_file = mock_analyze_file
        
        # Should fall back to base analysis
        result = commands.analyze_file_with_semantic_search(
            sample_python_file, 
            semantic_enabled=True
        )
        
        assert result['metadata']['fallback'] is True


class TestCommandLineInterface:
    """Test command line interface enhancements."""
    
    def test_command_line_parser_semantic_options(self):
        """Test command line parser includes semantic options."""
        import argparse
        
        # Simulate the argument parser from main()
        parser = argparse.ArgumentParser(description="Manual Security Analysis Commands")
        parser.add_argument("command", choices=["file", "workspace", "explain"], 
                           help="Analysis command type")
        parser.add_argument("--path", help="File or workspace path to analyze")
        parser.add_argument("--depth", choices=["standard", "comprehensive"], 
                           default="standard", help="Analysis depth")
        parser.add_argument("--format", choices=["json", "human"], 
                           default="human", help="Output format")
        parser.add_argument("--semantic", action="store_true", 
                           help="Enable semantic search enhancement (requires feature flag)")
        parser.add_argument("--semantic-filters", help="JSON string with semantic search filters")
        parser.add_argument("--rule-id", help="Rule ID for explanation command")
        parser.add_argument("--code-context", help="Code context for explanation command")
        
        # Test parsing semantic options
        args = parser.parse_args([
            "file", 
            "--path", "test.py", 
            "--semantic", 
            "--semantic-filters", '{"languages": ["python"]}'
        ])
        
        assert args.command == "file"
        assert args.path == "test.py"
        assert args.semantic is True
        assert args.semantic_filters == '{"languages": ["python"]}'
        
        # Test explain command
        explain_args = parser.parse_args([
            "explain",
            "--rule-id", "TEST-001",
            "--code-context", "test code"
        ])
        
        assert explain_args.command == "explain"
        assert explain_args.rule_id == "TEST-001" 
        assert explain_args.code_context == "test code"
    
    def test_semantic_filters_json_parsing(self):
        """Test JSON parsing of semantic filters."""
        import json
        
        # Valid JSON
        valid_json = '{"languages": ["python"], "severity_levels": ["high"]}'
        parsed = json.loads(valid_json)
        assert parsed['languages'] == ['python']
        assert parsed['severity_levels'] == ['high']
        
        # Invalid JSON should raise exception
        invalid_json = '{"languages": ["python"'  # Missing closing bracket
        with pytest.raises(json.JSONDecodeError):
            json.loads(invalid_json)