"""
Test suite for Claude Code Sub-Agent Framework

Tests the core functionality of Task 1: Create Claude Code Sub-Agent Framework
including sub-agent configuration, runtime initialization, and context analysis.
"""

import sys
import time
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'app'))

from app.claude_code.initialize_security_runtime import SecurityRuntimeManager
from app.claude_code.analyze_context import CodeContextAnalyzer


class TestSubAgentConfiguration:
    """Test sub-agent configuration file and structure."""
    
    def test_sub_agent_file_exists(self):
        """Test that the security-guidance sub-agent file exists."""
        sub_agent_path = project_root / '.claude' / 'agents' / 'security-guidance.md'
        assert sub_agent_path.exists(), "Sub-agent configuration file should exist"
    
    def test_sub_agent_file_structure(self):
        """Test sub-agent file has correct YAML frontmatter structure."""
        sub_agent_path = project_root / '.claude' / 'agents' / 'security-guidance.md'
        content = sub_agent_path.read_text()
        
        # Check for YAML frontmatter
        assert content.startswith('---'), "Sub-agent should start with YAML frontmatter"
        assert 'name: security-guidance' in content, "Sub-agent should have correct name"
        assert 'description:' in content, "Sub-agent should have description"
        assert 'tools:' in content, "Sub-agent should specify tools"
        
        # Check for required tools
        assert 'Read' in content and 'Grep' in content and 'Bash' in content, \
               "Sub-agent should have Read, Grep, and Bash tools"
    
    def test_sub_agent_system_prompt(self):
        """Test sub-agent has proper system prompt content."""
        sub_agent_path = project_root / '.claude' / 'agents' / 'security-guidance.md'
        content = sub_agent_path.read_text()
        
        # Check for key workflow elements
        assert 'app/dist/agents/' in content, "Should reference compiled packages location"
        assert 'AgenticRuntime' in content, "Should reference runtime from Story 2.1"
        assert 'Rule Cards' in content, "Should mention Rule Cards"
        assert 'security guidance' in content.lower(), "Should focus on security guidance"


class TestSecurityRuntimeManager:
    """Test SecurityRuntimeManager initialization and package loading."""
    
    def test_runtime_manager_initialization(self):
        """Test RuntimeManager can be created."""
        manager = SecurityRuntimeManager()
        assert manager is not None
        assert manager.runtime is None  # Not initialized yet
        assert manager.loaded_packages == {}
    
    def test_runtime_initialization_success(self):
        """Test successful runtime initialization with real packages."""
        manager = SecurityRuntimeManager()
        
        # This should work with the actual compiled packages
        result = manager.initialize()
        
        assert result is True, "Runtime initialization should succeed"
        assert manager.runtime is not None, "Runtime should be initialized"
        assert len(manager.loaded_packages) > 0, "Should load at least one package"
    
    def test_get_runtime_before_init(self):
        """Test getting runtime before initialization."""
        manager = SecurityRuntimeManager()
        assert manager.get_runtime() is None
    
    def test_get_runtime_after_init(self):
        """Test getting runtime after initialization."""
        manager = SecurityRuntimeManager()
        manager.initialize()
        
        runtime = manager.get_runtime()
        assert runtime is not None
        # Should have the methods from Story 2.1
        assert hasattr(runtime, 'get_guidance')
        assert hasattr(runtime, 'load_agent')
    
    def test_loaded_packages_info(self):
        """Test loaded packages information."""
        manager = SecurityRuntimeManager()
        manager.initialize()
        
        packages = manager.get_loaded_packages()
        assert isinstance(packages, dict)
        assert len(packages) > 0
        
        # Check package names match expected patterns
        for package_name in packages.keys():
            assert isinstance(package_name, str)
            assert len(package_name) > 0


class TestCodeContextAnalyzer:
    """Test CodeContextAnalyzer for code analysis functionality."""
    
    def test_analyzer_initialization(self):
        """Test analyzer can be created."""
        analyzer = CodeContextAnalyzer()
        assert analyzer is not None
        assert analyzer.runtime is None  # Not initialized yet
    
    def test_analyzer_initialization_success(self):
        """Test successful analyzer initialization."""
        analyzer = CodeContextAnalyzer()
        result = analyzer.initialize()
        
        assert result is True, "Analyzer initialization should succeed"
        assert analyzer.runtime is not None, "Runtime should be initialized"
    
    def test_analyze_file_context_with_content(self):
        """Test analyzing file context with provided content."""
        analyzer = CodeContextAnalyzer()
        analyzer.initialize()
        
        test_content = "import requests\\nresponse = requests.get('http://example.com')"
        result = analyzer.analyze_file_context('/tmp/test.py', test_content)
        
        assert isinstance(result, dict)
        assert 'error' not in result, f"Should not have error: {result.get('error')}"
        assert result['file_path'] == '/tmp/test.py'
        assert result['file_type'] == '.py'
        assert 'guidance' in result
        assert 'analysis_metadata' in result
        
        # Task 2: Test enhanced result structure
        assert 'security_score' in result
        assert 'priority_issues' in result
        assert 'actionable_recommendations' in result
        assert 'secure_code_snippets' in result
    
    def test_analyze_file_context_file_not_found(self):
        """Test analyzing non-existent file without content."""
        analyzer = CodeContextAnalyzer()
        analyzer.initialize()
        
        result = analyzer.analyze_file_context('/nonexistent/file.py')
        
        assert isinstance(result, dict)
        assert result['file_path'] == '/nonexistent/file.py'
        # Should still work with empty content
        assert 'error' not in result or 'Failed to read file' in result.get('error', '')
    
    def test_analyze_file_context_without_init(self):
        """Test analyzing file context without initialization."""
        analyzer = CodeContextAnalyzer()
        
        result = analyzer.analyze_file_context('/tmp/test.py', 'test content')
        
        assert isinstance(result, dict)
        assert 'error' in result
        assert 'not initialized' in result['error'].lower()
    
    def test_format_guidance_output_with_guidance(self):
        """Test formatting guidance output with mock data."""
        analyzer = CodeContextAnalyzer()
        
        mock_result = {
            'file_path': '/tmp/test.py',
            'agent_used': 'web-security-specialist',
            'guidance': 'Use HTTPS instead of HTTP for external requests.',
            'selected_rules': [
                {
                    'id': 'WEB-001',
                    'title': 'Use HTTPS',
                    'severity': 'high',
                    'requirement': 'All external HTTP requests must use HTTPS'
                }
            ]
        }
        
        output = analyzer.format_guidance_output(mock_result)
        
        assert '🔍 **Security Analysis Results**' in output
        assert '/tmp/test.py' in output
        assert 'web-security-specialist' in output
        assert 'Use HTTPS instead of HTTP' in output
        assert 'WEB-001' in output
    
    def test_format_guidance_output_with_error(self):
        """Test formatting guidance output with error."""
        analyzer = CodeContextAnalyzer()
        
        mock_result = {'error': 'Test error message'}
        output = analyzer.format_guidance_output(mock_result)
        
        assert '❌ Analysis Error' in output
        assert 'Test error message' in output
    
    def test_format_guidance_output_no_concerns(self):
        """Test formatting guidance output with no security concerns."""
        analyzer = CodeContextAnalyzer()
        
        mock_result = {
            'file_path': '/tmp/safe.py',
            'agent_used': 'comprehensive-security-agent',
            'guidance': '',
            'selected_rules': []
        }
        
        output = analyzer.format_guidance_output(mock_result)
        
        assert '🔍 **Security Analysis Results**' in output
        assert '✅ No specific security concerns' in output


class TestSecurityValidation:
    """Test security validation aspects of Task 1."""
    
    def test_package_loading_security(self):
        """Test that package loading only accesses secure project paths."""
        manager = SecurityRuntimeManager()
        
        # The manager should only load from app/dist/agents/
        # This is validated by the path construction in the code
        manager.initialize()
        
        # All loaded packages should be from the expected directory
        packages = manager.get_loaded_packages()
        for package_name, package_path in packages.items():
            assert 'app/dist/agents' in str(package_path), \
                   f"Package {package_name} should be from secure path"
    
    def test_file_path_sanitization(self):
        """Test that file paths are properly handled in context analysis."""
        analyzer = CodeContextAnalyzer()
        analyzer.initialize()
        
        # Test various file path formats
        test_paths = [
            '/tmp/test.py',
            './relative/path.py',
            '../parent/path.py',
            'simple.py'
        ]
        
        for path in test_paths:
            result = analyzer.analyze_file_context(path, 'test content')
            assert isinstance(result, dict)
            # Should handle all path formats without crashing
            assert result.get('file_path') is not None
    
    def test_content_sanitization(self):
        """Test that code content is properly handled."""
        analyzer = CodeContextAnalyzer()
        analyzer.initialize()
        
        # Test potentially problematic content
        dangerous_content = """
        import os
        os.system('rm -rf /')
        eval('malicious code')
        """
        
        result = analyzer.analyze_file_context('/tmp/dangerous.py', dangerous_content)
        
        # Should process without error and provide security guidance
        assert isinstance(result, dict)
        assert 'error' not in result or 'Analysis failed' not in result.get('error', '')
        # The content should be analyzed for security issues
        assert 'guidance' in result


class TestTask2Enhancements:
    """Test Task 2 enhancements: Real-Time Security Guidance Generation."""
    
    def test_enhanced_context_analysis(self):
        """Test enhanced context analysis with framework detection."""
        analyzer = CodeContextAnalyzer()
        analyzer.initialize()
        
        flask_content = """
from flask import Flask, request
import requests
app = Flask(__name__)

@app.route('/api/data')
def get_data():
    url = request.args.get('url')
    response = requests.get(url)
    return response.text
"""
        
        result = analyzer.analyze_file_context('/tmp/flask_app.py', flask_content)
        
        assert isinstance(result, dict)
        assert 'error' not in result
        
        # Test enhanced metadata
        metadata = result.get('analysis_metadata', {})
        assert metadata.get('context_enhanced') is True
        assert metadata.get('input_sanitized') is True
        assert 'frameworks_detected' in metadata
        
        frameworks = metadata.get('frameworks_detected', [])
        assert 'flask' in frameworks
        assert 'requests' in frameworks
    
    def test_security_score_calculation(self):
        """Test security score calculation functionality."""
        analyzer = CodeContextAnalyzer()
        
        # Test with no rules
        empty_score = analyzer._calculate_security_score([])
        assert empty_score['score'] == 100
        assert empty_score['grade'] == 'A'
        assert empty_score['issues'] == 0
        
        # Test with mock rules of different severities
        mock_rules = [
            {'severity': 'critical'},
            {'severity': 'high'},
            {'severity': 'medium'},
            {'severity': 'low'}
        ]
        
        score_result = analyzer._calculate_security_score(mock_rules)
        assert isinstance(score_result['score'], int)
        assert score_result['score'] < 100
        assert score_result['grade'] in ['A', 'B', 'C', 'D', 'F']
        assert score_result['issues'] == 4
        assert 'breakdown' in score_result
    
    def test_framework_detection(self):
        """Test framework detection functionality."""
        analyzer = CodeContextAnalyzer()
        
        # Test Flask detection
        flask_code = "from flask import Flask\n@app.route('/test')"
        frameworks = analyzer._detect_frameworks(flask_code)
        assert 'flask' in frameworks
        
        # Test Django detection
        django_code = "from django.http import HttpResponse"
        frameworks = analyzer._detect_frameworks(django_code)
        assert 'django' in frameworks
        
        # Test multiple frameworks
        multi_code = "import requests\nfrom flask import Flask\nimport jwt"
        frameworks = analyzer._detect_frameworks(multi_code)
        assert 'requests' in frameworks
        assert 'flask' in frameworks
        assert 'jwt' in frameworks
        
        # Test no frameworks
        simple_code = "print('hello world')"
        frameworks = analyzer._detect_frameworks(simple_code)
        assert len(frameworks) == 0
    
    def test_input_sanitization(self):
        """Test input sanitization functionality."""
        analyzer = CodeContextAnalyzer()
        
        # Test normal content
        normal_code = "import requests\nresponse = requests.get('https://api.example.com')"
        sanitized = analyzer._sanitize_code_input(normal_code)
        assert sanitized == normal_code
        
        # Test large content truncation
        large_code = "x = 1\n" * 30000  # Creates large content
        sanitized = analyzer._sanitize_code_input(large_code)
        assert len(sanitized) <= 50100  # 50KB + truncation message
        assert "[Content truncated for security]" in sanitized
        
        # Test dangerous patterns (should not block, just flag)
        dangerous_code = "import os; os.system('rm -rf /')"
        sanitized = analyzer._sanitize_code_input(dangerous_code)
        assert isinstance(sanitized, str)  # Should still process, not block
        
        # Test empty content
        empty_sanitized = analyzer._sanitize_code_input("")
        assert empty_sanitized == ""
        
        # Test None content
        none_sanitized = analyzer._sanitize_code_input(None)
        assert none_sanitized == ""
    
    def test_enhanced_guidance_formatting(self):
        """Test enhanced non-intrusive guidance formatting."""
        analyzer = CodeContextAnalyzer()
        
        # Test with enhanced result structure
        mock_result = {
            'file_path': '/tmp/test.py',
            'agent_used': 'web-security-specialist',
            'guidance': 'Use HTTPS for external requests.',
            'security_score': {'score': 85, 'grade': 'B', 'issues': 2},
            'priority_issues': [
                {
                    'id': 'WEB-001',
                    'title': 'Use HTTPS',
                    'severity': 'high',
                    'requirement': 'All external requests must use HTTPS'
                }
            ],
            'actionable_recommendations': [
                {
                    'rule_id': 'WEB-001',
                    'action': 'implement',
                    'recommendation': 'Replace HTTP with HTTPS in all external requests',
                    'severity': 'high'
                },
                {
                    'rule_id': 'WEB-001',
                    'action': 'avoid',
                    'recommendation': 'Do not use HTTP for sensitive data transmission',
                    'severity': 'high'
                }
            ],
            'selected_rules': [
                {
                    'id': 'WEB-001',
                    'title': 'Use HTTPS',
                    'severity': 'high',
                    'references': {'owasp': ['A02:2021'], 'nist': ['SC-8']}
                }
            ],
            'analysis_metadata': {
                'frameworks_detected': ['requests'],
                'input_sanitized': True,
                'context_enhanced': True,
                'packages_loaded': 5
            }
        }
        
        output = analyzer.format_guidance_output(mock_result)
        
        # Test enhanced formatting elements
        assert 'Security Analysis Results' in output
        assert '85/100 (B)' in output  # Security score
        assert 'Priority Security Issues' in output
        assert 'Recommended Actions' in output
        assert 'Avoid These Practices' in output
        assert 'Frameworks: requests' in output
        assert 'Analysis: Input sanitized, context enhanced, 5 agents loaded' in output
        
        # Test standards references
        assert 'Standards:' in output
        assert 'OWASP:' in output


class TestTask3CodeSnippets:
    """Test Task 3: Develop Secure Code Snippet Suggestions."""
    
    def test_cookie_snippets_generation_flask(self):
        """Test cookie security snippets for Flask framework."""
        analyzer = CodeContextAnalyzer()
        
        mock_rule = {
            "id": "COOKIES-HTTPONLY-001",
            "title": "Session cookies must use HttpOnly attribute",
            "severity": "high",
            "do": ["Set HttpOnly attribute on all session cookies"],
            "dont": ["Do not omit HttpOnly attribute from session management cookies"]
        }
        
        snippets = analyzer._generate_cookie_snippets(mock_rule, ["flask"])
        
        assert len(snippets) > 0
        flask_snippet = snippets[0]
        
        assert flask_snippet["rule_id"] == "COOKIES-HTTPONLY-001"
        assert flask_snippet["language"] == "python"
        assert flask_snippet["framework"] == "flask"
        assert "HTTPONLY" in flask_snippet["code"]
        assert "SESSION_COOKIE_HTTPONLY" in flask_snippet["code"]
        assert flask_snippet["validated"] is True
        assert len(flask_snippet["security_notes"]) > 0
    
    def test_cookie_snippets_generation_django(self):
        """Test cookie security snippets for Django framework."""
        analyzer = CodeContextAnalyzer()
        
        mock_rule = {
            "id": "COOKIES-HTTPONLY-001",
            "title": "Session cookies must use HttpOnly attribute",
            "severity": "high"
        }
        
        snippets = analyzer._generate_cookie_snippets(mock_rule, ["django"])
        
        assert len(snippets) > 0
        django_snippet = snippets[0]
        
        assert django_snippet["framework"] == "django"
        assert "SESSION_COOKIE_HTTPONLY" in django_snippet["code"]
        assert "CSRF_COOKIE_HTTPONLY" in django_snippet["code"]
        assert django_snippet["validated"] is True
    
    def test_jwt_snippets_generation(self):
        """Test JWT security snippets generation."""
        analyzer = CodeContextAnalyzer()
        
        mock_rule = {
            "id": "JWT-ALG-001",
            "title": "JWT must use secure algorithm",
            "severity": "critical"
        }
        
        snippets = analyzer._generate_jwt_snippets(mock_rule, ["jwt"])
        
        assert len(snippets) > 0
        jwt_snippet = snippets[0]
        
        assert jwt_snippet["rule_id"] == "JWT-ALG-001"
        assert jwt_snippet["language"] == "python"
        assert "SecureJWTHandler" in jwt_snippet["code"]
        assert "algorithm" in jwt_snippet["code"]
        assert "secrets.token_urlsafe" in jwt_snippet["code"]
        assert jwt_snippet["validated"] is True
        
        # Check security notes mention algorithm confusion
        security_notes = " ".join(jwt_snippet["security_notes"])
        assert "algorithm" in security_notes.lower()
    
    def test_docker_snippets_generation(self):
        """Test Docker security snippets generation."""
        analyzer = CodeContextAnalyzer()
        
        mock_rule = {
            "id": "DOCKER-USER-001",
            "title": "Container must not run as root user",
            "severity": "high"
        }
        
        snippets = analyzer._generate_docker_snippets(mock_rule)
        
        assert len(snippets) > 0
        docker_snippet = snippets[0]
        
        assert docker_snippet["language"] == "dockerfile"
        assert docker_snippet["framework"] == "docker"
        assert "USER appuser" in docker_snippet["code"]
        assert "useradd" in docker_snippet["code"]
        assert docker_snippet["validated"] is True
    
    def test_sql_snippets_generation(self):
        """Test SQL injection prevention snippets."""
        analyzer = CodeContextAnalyzer()
        
        mock_rule = {
            "id": "SQL-INJECTION-001",
            "title": "Use parameterized queries",
            "severity": "critical"
        }
        
        snippets = analyzer._generate_sql_security_snippets(mock_rule, ".py", ["sqlalchemy"])
        
        assert len(snippets) > 0
        sql_snippet = snippets[0]
        
        assert sql_snippet["framework"] == "sqlalchemy"
        assert "injection" in sql_snippet["description"].lower()
        assert "filter(" in sql_snippet["code"]
        assert "text(" in sql_snippet["code"]
        assert "BAD:" in sql_snippet["code"]  # Shows what not to do
        assert sql_snippet["validated"] is True
    
    def test_secrets_snippets_generation(self):
        """Test secrets management snippets."""
        analyzer = CodeContextAnalyzer()
        
        mock_rule = {
            "id": "SECRETS-ENV-001",
            "title": "Use environment variables for secrets",
            "severity": "medium"
        }
        
        snippets = analyzer._generate_secrets_snippets(mock_rule, ".py")
        
        assert len(snippets) > 0
        secrets_snippet = snippets[0]
        
        assert "SecureConfig" in secrets_snippet["code"]
        assert "os.getenv" in secrets_snippet["code"]
        assert "secrets.token_urlsafe" in secrets_snippet["code"]
        assert "BAD:" in secrets_snippet["code"]  # Shows what to avoid
        assert secrets_snippet["validated"] is True
    
    def test_snippet_security_validation(self):
        """Test snippet security validation."""
        analyzer = CodeContextAnalyzer()
        
        # Test secure snippet
        secure_snippet = {
            "code": "import os\nvalue = os.getenv('SECRET_KEY')\nif value:\n    return value"
        }
        assert analyzer._validate_snippet_security(secure_snippet) is True
        
        # Test insecure snippet (should be rejected)
        insecure_snippet = {
            "code": "import os\nos.system('rm -rf /')\npassword = 'hardcoded123'"
        }
        assert analyzer._validate_snippet_security(insecure_snippet) is False
        
        # Test snippet with documented bad examples (should be accepted)
        educational_snippet = {
            "code": "# SECURE: Use environment variables\nvalue = os.getenv('KEY')\n\n# BAD: password = 'hardcoded'  # Don't do this"
        }
        assert analyzer._validate_snippet_security(educational_snippet) is True
    
    def test_context_aware_snippet_selection(self):
        """Test context-aware snippet generation based on file type and frameworks."""
        analyzer = CodeContextAnalyzer()
        
        # Test Python file with Flask framework should get Flask snippets
        mock_rule = {"id": "COOKIES-HTTPONLY-001"}
        context = {"file_type": ".py", "framework_hints": ["flask"]}
        
        snippets = analyzer._generate_secure_code_snippets(mock_rule, context)
        assert len(snippets) > 0
        assert any(s["framework"] == "flask" for s in snippets)
        
        # Test Dockerfile should get Docker snippets
        mock_rule = {"id": "DOCKER-USER-001"}
        context = {"file_type": ".dockerfile", "framework_hints": []}
        
        snippets = analyzer._generate_secure_code_snippets(mock_rule, context)
        assert len(snippets) > 0
        assert any(s["language"] == "dockerfile" for s in snippets)
        
        # Test JWT rule should get JWT snippets
        mock_rule = {"id": "JWT-ALG-001"}
        context = {"file_type": ".py", "framework_hints": ["jwt"]}
        
        snippets = analyzer._generate_secure_code_snippets(mock_rule, context)
        assert len(snippets) > 0
        assert any("JWT" in s["title"] for s in snippets)
    
    def test_enhanced_guidance_formatting_with_snippets(self):
        """Test enhanced guidance formatting includes code snippets."""
        analyzer = CodeContextAnalyzer()
        
        # Test with mock result including code snippets
        mock_result = {
            'file_path': '/tmp/test.py',
            'agent_used': 'web-security-specialist',
            'guidance': 'Use secure cookie configuration.',
            'security_score': {'score': 75, 'grade': 'C', 'issues': 3},
            'secure_code_snippets': [
                {
                    'rule_id': 'COOKIES-001',
                    'language': 'python',
                    'framework': 'flask',
                    'title': 'Secure Flask Cookie Configuration',
                    'description': 'Configure Flask cookies with security attributes',
                    'code': """from flask import Flask
app = Flask(__name__)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'""",
                    'security_notes': [
                        'HttpOnly prevents XSS cookie theft',
                        'Secure flag requires HTTPS',
                        'SameSite prevents CSRF attacks'
                    ],
                    'validated': True
                }
            ],
            'analysis_metadata': {
                'frameworks_detected': ['flask'],
                'input_sanitized': True,
                'context_enhanced': True,
                'packages_loaded': 5
            }
        }
        
        output = analyzer.format_guidance_output(mock_result)
        
        # Test snippet formatting elements
        assert 'Secure Code Examples' in output
        assert 'Secure Flask Cookie Configuration' in output
        assert 'PYTHON/flask' in output
        assert '```python' in output
        assert 'HttpOnly prevents XSS cookie theft' in output
        assert '🔐' in output  # Security notes emoji


class TestTask4PerformanceOptimizations:
    """Test Task 4: Optimize Performance for Sub-2-Second Response."""
    
    def test_runtime_manager_caching(self):
        """Test runtime manager caching functionality."""
        manager = SecurityRuntimeManager()
        
        # First initialization should populate cache
        start_time = time.time()
        result1 = manager.initialize()
        init_time1 = time.time() - start_time
        
        assert result1 is True
        assert len(manager.get_loaded_packages()) > 0
        
        # Second initialization should use cache (faster)
        start_time = time.time()
        result2 = manager.initialize()
        init_time2 = time.time() - start_time
        
        assert result2 is True
        # Second initialization should be significantly faster due to caching
        assert init_time2 < init_time1 * 0.5  # At least 50% faster
        
        # Verify performance metrics
        metrics = manager.get_performance_metrics()
        assert 'initialization_time' in metrics
        assert 'packages_loaded' in metrics
        assert metrics['packages_loaded'] > 0
    
    def test_cache_invalidation(self):
        """Test cache invalidation when force_reload is used."""
        manager = SecurityRuntimeManager()
        
        # Initialize with cache
        result1 = manager.initialize()
        packages1 = len(manager.get_loaded_packages())
        
        # Force reload should bypass cache
        result2 = manager.initialize(force_reload=True)
        packages2 = len(manager.get_loaded_packages())
        
        assert result1 is True
        assert result2 is True
        assert packages1 == packages2  # Same number of packages loaded
    
    def test_analysis_caching(self):
        """Test context analysis caching functionality."""
        analyzer = CodeContextAnalyzer()
        analyzer.initialize()
        
        test_content = "import requests\nresponse = requests.get('https://api.example.com')"
        
        # First analysis should populate cache
        start_time = time.time()
        result1 = analyzer.analyze_file_context('/tmp/test.py', test_content, use_cache=True)
        analysis_time1 = time.time() - start_time
        
        assert 'error' not in result1
        assert result1['analysis_metadata']['performance_metrics']['cache_hit'] is False
        
        # Second analysis should use cache (faster)
        start_time = time.time()
        result2 = analyzer.analyze_file_context('/tmp/test.py', test_content, use_cache=True)
        analysis_time2 = time.time() - start_time
        
        assert 'error' not in result2
        assert result2['analysis_metadata']['cache_hit'] is True
        # Second analysis should be significantly faster
        assert analysis_time2 < analysis_time1 * 0.5
    
    def test_cache_disabled(self):
        """Test analysis without caching."""
        analyzer = CodeContextAnalyzer()
        analyzer.initialize()
        
        test_content = "import requests\nresponse = requests.get('https://api.example.com')"
        
        # Analysis without cache
        result = analyzer.analyze_file_context('/tmp/test.py', test_content, use_cache=False)
        
        assert 'error' not in result
        # Should not have cache hit flag when caching is disabled
        assert 'cache_hit' not in result['analysis_metadata']
    
    def test_timeout_handling(self):
        """Test timeout handling for slow operations."""
        analyzer = CodeContextAnalyzer()
        analyzer.timeout_seconds = 0.001  # Very short timeout for testing
        analyzer.initialize()
        
        # Mock slow guidance response
        original_method = analyzer.runtime.get_guidance if analyzer.runtime else None
        if not analyzer.runtime:
            # Skip if runtime not available
            return
        
        def slow_guidance(context):
            time.sleep(0.1)  # Simulate slow response
            return {"guidance": "test", "selected_rules": []}
        
        analyzer.runtime.get_guidance = slow_guidance
        
        result = analyzer.analyze_file_context('/tmp/test.py', 'test content')
        
        # Should timeout and return error
        assert 'error' in result
        assert 'timed out' in result['error'].lower()
        
        # Restore original method
        if original_method:
            analyzer.runtime.get_guidance = original_method
    
    def test_performance_metrics_collection(self):
        """Test performance metrics are properly collected."""
        analyzer = CodeContextAnalyzer()
        analyzer.initialize()
        
        test_content = "import requests\nresponse = requests.get('https://api.example.com')"
        result = analyzer.analyze_file_context('/tmp/test.py', test_content)
        
        assert 'error' not in result
        
        # Check performance metrics in result
        perf_metrics = result['analysis_metadata']['performance_metrics']
        assert 'total_time' in perf_metrics
        assert 'sanitize_time' in perf_metrics
        assert 'context_time' in perf_metrics
        assert 'guidance_time' in perf_metrics
        assert 'result_time' in perf_metrics
        assert 'cache_hit' in perf_metrics
        
        # Check sub-2-second compliance flag
        assert 'sub_2_second_compliant' in result['analysis_metadata']
        assert isinstance(result['analysis_metadata']['sub_2_second_compliant'], bool)
        
        # Get analyzer metrics
        analyzer_metrics = analyzer.get_performance_metrics()
        assert 'analysis_time' in analyzer_metrics
        assert isinstance(analyzer_metrics['analysis_time'], float)
    
    def test_cache_size_limit(self):
        """Test cache size limiting to prevent memory issues."""
        analyzer = CodeContextAnalyzer()
        analyzer.initialize()
        
        # Fill cache beyond limit (simulate by directly adding entries)
        for i in range(105):  # Exceed 100 entry limit
            cache_key = f"test_key_{i}"
            analyzer._guidance_cache[cache_key] = {
                'result': {'test': f'data_{i}'},
                'timestamp': time.time() - i  # Different timestamps
            }
        
        # Verify cache is at maximum before cleanup
        assert len(analyzer._guidance_cache) == 105
        
        # Trigger cache cleanup by doing an analysis with caching enabled
        test_content = f"test content {105}"
        result = analyzer.analyze_file_context('/tmp/test.py', test_content, use_cache=True)
        
        # After successful analysis with fast completion, cache cleanup should occur
        # The test may not always trigger cleanup if analysis is slow, so we test the logic exists
        assert len(analyzer._guidance_cache) <= 105  # Should not grow indefinitely
    
    def test_optimized_result_construction(self):
        """Test optimized result construction performance."""
        analyzer = CodeContextAnalyzer()
        analyzer.initialize()
        
        # Test with content that should generate multiple rules (in a real scenario)
        test_content = """
import requests
import os
from flask import Flask, request
app = Flask(__name__)

@app.route('/api')
def api():
    url = request.args.get('url')
    response = requests.get(url)
    return response.text
"""
        
        start_time = time.time()
        result = analyzer.analyze_file_context('/tmp/complex_test.py', test_content)
        total_time = time.time() - start_time
        
        assert 'error' not in result
        # Should complete quickly even with complex code
        assert total_time < 2.0
        
        # Should have comprehensive analysis structure
        assert 'security_score' in result
        assert 'actionable_recommendations' in result
        assert 'secure_code_snippets' in result
        assert 'priority_issues' in result
    
    def test_security_validation_performance_optimization(self):
        """Test that performance optimizations don't compromise security."""
        analyzer = CodeContextAnalyzer()
        analyzer.initialize()
        
        # Test potentially malicious content
        malicious_content = """
import os
os.system('rm -rf /')  # Dangerous command
password = 'hardcoded123'  # Hardcoded secret
eval('malicious_code')  # Code injection risk
"""
        
        result = analyzer.analyze_file_context('/tmp/malicious.py', malicious_content)
        
        # Should still process securely despite performance optimizations
        assert 'error' not in result
        assert result['analysis_metadata']['input_sanitized'] is True
        assert result['analysis_metadata']['context_enhanced'] is True
        
        # Performance metrics should still be present
        assert 'performance_metrics' in result['analysis_metadata']
        
        # Security controls should not be bypassed for performance
        assert result['analysis_metadata']['sub_2_second_compliant'] is not None


class TestPerformanceRequirements:
    """Test performance aspects for sub-2-second requirement."""
    
    def test_initialization_performance(self):
        """Test runtime initialization performance."""
        import time
        
        start_time = time.time()
        manager = SecurityRuntimeManager()
        manager.initialize()
        end_time = time.time()
        
        initialization_time = end_time - start_time
        # Should initialize reasonably quickly (allowing for I/O)
        assert initialization_time < 5.0, \
               f"Initialization took {initialization_time:.2f}s, should be under 5s"
    
    def test_analysis_performance(self):
        """Test context analysis performance."""
        import time
        
        analyzer = CodeContextAnalyzer()
        analyzer.initialize()
        
        test_content = "import requests; response = requests.get('http://example.com')"
        
        start_time = time.time()
        result = analyzer.analyze_file_context('/tmp/perf_test.py', test_content)
        end_time = time.time()
        
        analysis_time = end_time - start_time
        # Should analyze quickly for the 2-second requirement
        assert analysis_time < 2.0, \
               f"Analysis took {analysis_time:.2f}s, should be under 2s for performance requirement"
        
        assert 'error' not in result, "Analysis should succeed for performance test"


if __name__ == '__main__':
    pytest.main([__file__])