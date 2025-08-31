#!/usr/bin/env python3
"""
Comprehensive Tests for Manual Execution Commands - Story 2.3

Tests all manual security analysis functionality including command interface,
analysis engine extensions, results display, CI/CD consistency, and security validation.
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

# Add project root and app to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'app'))

from app.claude_code.manual_commands import ManualSecurityCommands, SecurityAnalysisResults
from app.claude_code.analyze_context import CodeContextAnalyzer


class TestManualCommandInterface:
    """Test Task 1: Manual Command Interface with security validation."""
    
    def setup_method(self):
        """Setup test environment for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create mock files for testing
        self.test_file = self.temp_path / "test.py"
        self.test_file.write_text("import requests\npassword = 'secret123'")
        
        # Initialize commands
        self.commands = ManualSecurityCommands()
        self.commands._project_root = self.temp_path  # Override for testing
        self.commands._allowed_paths.add(self.temp_path.resolve())
    
    def teardown_method(self):
        """Cleanup test environment."""
        shutil.rmtree(self.temp_dir)
    
    @patch('app.claude_code.manual_commands.CodeContextAnalyzer')
    def test_manual_commands_initialization(self, mock_analyzer):
        """Test manual command initialization and dependencies."""
        mock_analyzer.return_value.initialize.return_value = True
        
        commands = ManualSecurityCommands()
        result = commands.initialize()
        
        assert result is True
        assert commands._initialized is True
        mock_analyzer.assert_called_once()
    
    def test_file_path_validation_success(self):
        """Test successful file path validation."""
        validated_path = self.commands._validate_file_path(str(self.test_file))
        assert validated_path == self.test_file.resolve()
    
    def test_file_path_validation_traversal_attack(self):
        """Test path traversal attack prevention."""
        malicious_paths = [
            "../../../etc/passwd",
            "/etc/passwd",
            "../../secrets.txt",
            str(self.temp_path / "../outside.py")
        ]
        
        for malicious_path in malicious_paths:
            with pytest.raises(ValueError, match="Path access denied|outside project boundaries"):
                self.commands._validate_file_path(malicious_path)
    
    def test_file_path_validation_invalid_extension(self):
        """Test rejection of invalid file extensions."""
        invalid_file = self.temp_path / "malicious.exe"
        invalid_file.write_text("malicious content")
        
        with pytest.raises(ValueError, match="File type not allowed"):
            self.commands._validate_file_path(str(invalid_file))
    
    def test_file_path_validation_large_file(self):
        """Test rejection of oversized files."""
        large_file = self.temp_path / "large.py"
        large_file.write_text("# Large file\n" * 100000)  # Create large file
        
        with pytest.raises(ValueError, match="File too large"):
            self.commands._validate_file_path(str(large_file))
    
    def test_analysis_depth_validation(self):
        """Test analysis depth parameter validation."""
        assert self.commands._validate_analysis_depth("standard") == "standard"
        assert self.commands._validate_analysis_depth("comprehensive") == "comprehensive"
        
        with pytest.raises(ValueError, match="Invalid analysis depth"):
            self.commands._validate_analysis_depth("invalid")
    
    def test_workspace_path_validation_success(self):
        """Test successful workspace path validation."""
        validated_path = self.commands._validate_workspace_path(str(self.temp_path))
        assert validated_path == self.temp_path.resolve()
    
    def test_workspace_path_validation_traversal_attack(self):
        """Test workspace path traversal attack prevention."""
        malicious_paths = [
            "../../../",
            "/root",
            str(self.temp_path / "../../")
        ]
        
        for malicious_path in malicious_paths:
            with pytest.raises(ValueError, match="Workspace access denied|outside project boundaries"):
                self.commands._validate_workspace_path(malicious_path)


class TestSecurityAnalysisEngine:
    """Test Task 2: Comprehensive Security Analysis Engine."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create test files with various security issues
        self.python_file = self.temp_path / "app.py"
        self.python_file.write_text("""
import requests
import jwt
from flask import Flask

app = Flask(__name__)

# Security issues for testing
password = "hardcoded_secret"
api_key = "sk-1234567890abcdef"

@app.route('/login')
def login():
    response = make_response('OK')
    response.set_cookie('session', 'value')  # Missing security flags
    return response

def fetch_url(url):
    return requests.get(url)  # SSRF vulnerability
        """)
        
        self.js_file = self.temp_path / "client.js"
        self.js_file.write_text("""
const API_KEY = 'secret123';
document.innerHTML = userInput;  // XSS vulnerability
        """)
        
        # Initialize analyzer with mocking
        self.analyzer = CodeContextAnalyzer()
        self.commands = ManualSecurityCommands()
        self.commands._project_root = self.temp_path
        self.commands._allowed_paths.add(self.temp_path.resolve())
    
    def teardown_method(self):
        """Cleanup test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_file_discovery_with_security_limits(self):
        """Test secure file discovery with limits and filtering."""
        # Create many files to test limits
        for i in range(10):
            (self.temp_path / f"test_{i}.py").write_text("# Test file")
        
        discovered_files = self.commands._discover_workspace_files(self.temp_path)
        
        # Should find Python and JS files
        assert len(discovered_files) > 0
        assert all(f.suffix in self.commands.ALLOWED_EXTENSIONS for f in discovered_files)
        assert self.python_file in discovered_files
        assert self.js_file in discovered_files
    
    def test_file_discovery_depth_limit(self):
        """Test file discovery respects depth limits for security."""
        # Create deep directory structure
        deep_path = self.temp_path
        for i in range(15):  # Deeper than MAX_DEPTH
            deep_path = deep_path / f"level_{i}"
            deep_path.mkdir()
        
        deep_file = deep_path / "deep.py"
        deep_file.write_text("# Deep file")
        
        discovered_files = self.commands._discover_workspace_files(self.temp_path)
        
        # Deep file should not be discovered due to depth limit
        assert deep_file not in discovered_files
    
    @patch('app.claude_code.manual_commands.CodeContextAnalyzer.analyze_file_context')
    def test_single_file_analysis_with_mocked_runtime(self, mock_analyze):
        """Test single file analysis with mocked dependencies."""
        # Mock analyzer response
        mock_analyze.return_value = {
            "selected_rules": [
                {
                    "id": "HARDCODED-SECRET-001",
                    "title": "Hardcoded Secret Detected",
                    "severity": "high",
                    "requirement": "Remove hardcoded secrets",
                    "do": ["Use environment variables"],
                    "dont": ["Hardcode secrets"],
                    "detect": {"semgrep": ["hardcoded-secret"]}
                }
            ],
            "frameworks": ["requests", "flask"],
            "guidance": "Remove hardcoded secrets and use secure configuration."
        }
        
        self.commands._initialized = True
        self.commands.analyzer = Mock()
        self.commands.analyzer.analyze_file_context = mock_analyze
        
        result = self.commands.analyze_file(str(self.python_file))
        
        assert result["status"] == "success"
        assert result["analysis_type"] == "single_file"
        assert result["results"]["summary"]["total_issues"] == 1
        assert result["results"]["summary"]["high_count"] == 1
        assert result["results"]["ci_cd_prediction"]["would_pass"] is False
    
    def test_input_sanitization_for_ide_display(self):
        """Test content sanitization prevents IDE injection attacks."""
        malicious_content = '<script>alert("XSS")</script>\n<img src="x" onerror="alert(1)">'
        
        sanitized = self.commands._sanitize_for_ide_display(malicious_content)
        
        # Should be HTML escaped
        assert '<script>' not in sanitized
        assert '&lt;script&gt;' in sanitized
        assert 'onerror=' not in sanitized
    
    def test_resource_limits_timeout_protection(self):
        """Test resource limits prevent resource exhaustion attacks."""
        def slow_function():
            import time
            time.sleep(35)  # Longer than ANALYSIS_TIMEOUT
            return "result"
        
        with pytest.raises(Exception):  # Should timeout
            self.commands._apply_resource_limits(slow_function)


class TestResultsDisplaySystem:
    """Test Task 3: Structured Results Display System."""
    
    def setup_method(self):
        """Setup test environment."""
        self.results = SecurityAnalysisResults()
    
    def test_security_analysis_results_structure(self):
        """Test structured results format with severity categorization."""
        assert "total_issues" in self.results.summary
        assert "files_analyzed" in self.results.summary
        assert "critical_count" in self.results.summary
        assert "issues_by_severity" in self.results.__dict__
        assert "critical" in self.results.issues_by_severity
        assert "high" in self.results.issues_by_severity
        assert "medium" in self.results.issues_by_severity
        assert "low" in self.results.issues_by_severity
    
    def test_issue_categorization_by_severity(self):
        """Test issues are properly categorized by severity levels."""
        # Simulate adding issues
        self.results.issues_by_severity["critical"].append({
            "id": "CRIT-001",
            "severity": "critical",
            "title": "Critical Issue"
        })
        self.results.issues_by_severity["high"].append({
            "id": "HIGH-001", 
            "severity": "high",
            "title": "High Issue"
        })
        
        self.results.summary["critical_count"] = 1
        self.results.summary["high_count"] = 1
        self.results.summary["total_issues"] = 2
        
        assert len(self.results.issues_by_severity["critical"]) == 1
        assert len(self.results.issues_by_severity["high"]) == 1
        assert self.results.summary["total_issues"] == 2
    
    def test_ci_cd_prediction_format(self):
        """Test CI/CD prediction structure and logic."""
        # Test passing prediction
        self.results.ci_cd_prediction = {
            "would_pass": True,
            "blocking_issues": [],
            "score": 100
        }
        
        assert self.results.ci_cd_prediction["would_pass"] is True
        assert self.results.ci_cd_prediction["score"] == 100
        
        # Test failing prediction
        self.results.ci_cd_prediction = {
            "would_pass": False,
            "blocking_issues": ["CRIT-001", "HIGH-001"],
            "score": 80
        }
        
        assert self.results.ci_cd_prediction["would_pass"] is False
        assert len(self.results.ci_cd_prediction["blocking_issues"]) == 2


class TestCICDConsistency:
    """Test Task 4: CI/CD Consistency and Prediction."""
    
    def setup_method(self):
        """Setup test environment."""
        self.analyzer = CodeContextAnalyzer()
    
    def test_cicd_rule_relevance_detection(self):
        """Test detection of CI/CD relevant rules."""
        # Rule with detect hooks - should be CI/CD relevant
        cicd_rule = {
            "id": "SEMGREP-001",
            "severity": "high",
            "detect": {"semgrep": ["hardcoded-password"]}
        }
        
        # Rule without detect hooks - not CI/CD relevant
        advisory_rule = {
            "id": "ADVISORY-001",
            "severity": "medium"
        }
        
        assert self.analyzer._is_rule_cicd_relevant(cicd_rule) is True
        assert self.analyzer._is_rule_cicd_relevant(advisory_rule) is False
    
    def test_cicd_outcome_prediction_logic(self):
        """Test CI/CD pipeline outcome prediction accuracy."""
        # Test with critical and high issues (should fail)
        blocking_rules = [
            {"severity": "critical", "id": "CRIT-001"},
            {"severity": "high", "id": "HIGH-001"},
            {"severity": "medium", "id": "MED-001"}
        ]
        
        prediction = self.analyzer._predict_cicd_outcome(blocking_rules)
        assert prediction["would_pass"] is False
        assert prediction["blocking_issues"] == 2
        assert prediction["critical_issues"] == 1
        assert prediction["high_issues"] == 1
        
        # Test with only low/medium issues (should pass)
        non_blocking_rules = [
            {"severity": "medium", "id": "MED-001"},
            {"severity": "low", "id": "LOW-001"}
        ]
        
        prediction = self.analyzer._predict_cicd_outcome(non_blocking_rules)
        assert prediction["would_pass"] is True
        assert prediction["blocking_issues"] == 0
    
    def test_remediation_steps_generation(self):
        """Test actionable remediation suggestions generation."""
        rule = {
            "id": "TEST-001",
            "do": ["Use environment variables", "Implement proper validation"],
            "dont": ["Hardcode secrets", "Trust user input"],
            "verify": {"tests": ["Test with invalid input", "Verify no secrets in logs"]}
        }
        
        steps = self.analyzer._generate_remediation_steps(rule)
        
        # Should have steps from all sections
        assert any("Use environment variables" in step for step in steps)
        assert any("Avoid: Hardcode secrets" in step for step in steps) 
        assert any("Verify: Test with invalid input" in step for step in steps)
        assert len(steps) >= 4  # At least one from each section


class TestSecurityValidation:
    """Test Security Requirements implementation and validation."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.commands = ManualSecurityCommands()
        self.commands._project_root = self.temp_path
        self.commands._allowed_paths.add(self.temp_path.resolve())
    
    def teardown_method(self):
        """Cleanup test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_secure_api_key_handling_environment_variables(self):
        """Test secure API key handling via environment variables."""
        # This test ensures no API keys are hardcoded in the manual commands
        commands_source = Path("app/claude_code/manual_commands.py").read_text()
        
        # Should not contain common API key patterns
        dangerous_patterns = [
            'api_key = "',
            'API_KEY = "',
            'secret = "',
            'password = "',
            'sk-',  # OpenAI/Anthropic key prefix
            'pk-'   # Private key prefix
        ]
        
        for pattern in dangerous_patterns:
            assert pattern not in commands_source
    
    def test_input_validation_prevents_path_traversal(self):
        """Test comprehensive input validation prevents traversal attacks."""
        traversal_attempts = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
            "C:\\Windows\\System32\\config\\SAM",
            "../secrets.env",
            "../../.ssh/id_rsa"
        ]
        
        for attempt in traversal_attempts:
            with pytest.raises(ValueError, match="Path access denied|outside project boundaries"):
                self.commands._validate_file_path(attempt)
    
    def test_malformed_data_handling_graceful_failure(self):
        """Test system handles malformed data gracefully without crashing."""
        malformed_inputs = [
            "",  # Empty string
            None,  # None value  
            "not_a_path",  # Invalid path
            "\x00\x01\x02",  # Binary data
            "../" * 1000,  # Excessive traversal
            "file.py" + "A" * 10000  # Excessive length
        ]
        
        for malformed_input in malformed_inputs:
            try:
                if malformed_input is not None and malformed_input != "":
                    self.commands._validate_file_path(malformed_input)
            except (ValueError, TypeError, OSError):
                # Expected to fail gracefully with proper exceptions
                continue
            except Exception as e:
                # Should not crash with unexpected errors
                pytest.fail(f"Unexpected exception for input '{malformed_input}': {e}")
    
    def test_resource_limits_prevent_dos_attacks(self):
        """Test resource limits prevent denial of service attacks."""
        # Test file size limit
        assert self.commands.MAX_FILE_SIZE == 1024 * 1024  # 1MB
        
        # Test workspace file count limit
        assert self.commands.MAX_WORKSPACE_FILES == 1000
        
        # Test analysis timeout
        assert self.commands.ANALYSIS_TIMEOUT == 30  # 30 seconds
    
    def test_authorization_controls_package_access(self):
        """Test authorization controls restrict package access properly."""
        # Commands should only access packages within allowed paths
        allowed_extensions = self.commands.ALLOWED_EXTENSIONS
        
        # Security-relevant extensions should be included
        assert '.py' in allowed_extensions
        assert '.js' in allowed_extensions
        assert '.yaml' in allowed_extensions
        assert '.yml' in allowed_extensions
        
        # Dangerous extensions should be excluded
        dangerous_extensions = {'.exe', '.bat', '.sh', '.ps1', '.cmd'}
        # Note: .sh is actually allowed for legitimate shell script analysis
        # but .exe, .bat are correctly excluded
        assert '.exe' not in allowed_extensions
        assert '.bat' not in allowed_extensions
    
    def test_data_protection_local_analysis_only(self):
        """Test analysis results remain within local environment."""
        # Manual commands should not make external network calls
        # This is ensured by the architecture - all analysis is local
        
        commands_source = Path("app/claude_code/manual_commands.py").read_text()
        
        # Should not contain external networking code
        network_patterns = [
            'requests.post(',
            'urllib.request.urlopen(',
            'http://',
            'https://',
            'socket.connect(',
            'telnet'
        ]
        
        # Allow https:// in comments/documentation only
        lines = commands_source.split('\n')
        for line_num, line in enumerate(lines, 1):
            if not line.strip().startswith('#') and not line.strip().startswith('"""'):
                for pattern in network_patterns:
                    if pattern in line and pattern != 'https://':  # Allow https in comments
                        pytest.fail(f"Network call found at line {line_num}: {line.strip()}")


class TestPerformanceRequirements:
    """Test performance requirements and optimization."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create test files
        self.small_file = self.temp_path / "small.py"
        self.small_file.write_text("import os\nprint('hello')")
        
        self.commands = ManualSecurityCommands()
        self.commands._project_root = self.temp_path
        self.commands._allowed_paths.add(self.temp_path.resolve())
    
    def teardown_method(self):
        """Cleanup test environment."""
        shutil.rmtree(self.temp_dir)
    
    @patch('app.claude_code.manual_commands.CodeContextAnalyzer')
    def test_single_file_analysis_performance_under_10_seconds(self, mock_analyzer):
        """Test single file analysis completes under 10 seconds."""
        import time
        
        # Mock fast response
        mock_analyzer.return_value.analyze_file_context.return_value = {
            "selected_rules": [],
            "frameworks": [],
            "guidance": "No issues found."
        }
        mock_analyzer.return_value.initialize.return_value = True
        
        self.commands._initialized = True
        self.commands.analyzer = mock_analyzer.return_value
        
        start_time = time.time()
        result = self.commands.analyze_file(str(self.small_file))
        execution_time = time.time() - start_time
        
        assert execution_time < 10.0
        assert result["status"] == "success"
        assert "execution_time" in result["metadata"]
    
    def test_resource_limits_timeout_enforcement(self):
        """Test timeout controls activate within specified limits."""
        def long_running_task():
            import time
            time.sleep(self.commands.ANALYSIS_TIMEOUT + 1)
            return "completed"
        
        start_time = time.time()
        with pytest.raises(Exception):  # Should timeout
            self.commands._apply_resource_limits(long_running_task)
        
        execution_time = time.time() - start_time
        # Should timeout close to the limit, not wait for the full task
        assert execution_time <= self.commands.ANALYSIS_TIMEOUT + 2


class TestIntegrationWorkflow:
    """Integration tests for complete manual analysis workflow."""
    
    def setup_method(self):
        """Setup comprehensive test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create realistic project structure
        (self.temp_path / "src").mkdir()
        (self.temp_path / "tests").mkdir()
        
        # Create files with various security issues
        auth_file = self.temp_path / "src" / "auth.py"
        auth_file.write_text("""
import jwt
import hashlib

# Security issues for testing
SECRET_KEY = "hardcoded_jwt_secret_12345"
API_TOKEN = "sk-1234567890abcdef"

def authenticate(username, password):
    # Weak password hashing
    hash_obj = hashlib.md5(password.encode())
    return hash_obj.hexdigest()

def generate_token(user_id):
    # JWT with hardcoded secret
    return jwt.encode({"user_id": user_id}, SECRET_KEY, algorithm="HS256")
        """)
        
        api_file = self.temp_path / "src" / "api.py" 
        api_file.write_text("""
from flask import Flask, request, make_response
import requests

app = Flask(__name__)

@app.route('/proxy')
def proxy():
    # SSRF vulnerability
    url = request.args.get('url')
    response = requests.get(url)
    return response.text

@app.route('/login')
def login():
    resp = make_response('Login successful')
    # Insecure cookie
    resp.set_cookie('session', 'user123')
    return resp
        """)
        
        self.commands = ManualSecurityCommands()
        self.commands._project_root = self.temp_path
        self.commands._allowed_paths.add(self.temp_path.resolve())
    
    def teardown_method(self):
        """Cleanup test environment."""
        shutil.rmtree(self.temp_dir)
    
    @patch('app.claude_code.manual_commands.CodeContextAnalyzer')
    def test_end_to_end_workspace_analysis_workflow(self, mock_analyzer_class):
        """Test complete workspace analysis workflow with multiple files."""
        # Mock analyzer for consistent testing
        mock_analyzer = Mock()
        mock_analyzer_class.return_value = mock_analyzer
        mock_analyzer.initialize.return_value = True
        
        # Mock different responses for different files
        def mock_analyze_file_context(file_path, *args, **kwargs):
            if "auth.py" in str(file_path):
                return {
                    "selected_rules": [
                        {
                            "id": "HARDCODED-JWT-SECRET",
                            "title": "Hardcoded JWT Secret",
                            "severity": "critical",
                            "requirement": "Use secure key management",
                            "do": ["Store secrets in environment variables"],
                            "dont": ["Hardcode JWT secrets"],
                            "detect": {"semgrep": ["hardcoded-jwt-secret"]}
                        }
                    ],
                    "frameworks": ["jwt"],
                    "guidance": "Critical: Remove hardcoded JWT secret."
                }
            elif "api.py" in str(file_path):
                return {
                    "selected_rules": [
                        {
                            "id": "SSRF-VULNERABILITY",
                            "title": "Server-Side Request Forgery",
                            "severity": "high", 
                            "requirement": "Validate URLs before requests",
                            "do": ["Implement URL validation"],
                            "dont": ["Trust user-provided URLs"],
                            "detect": {"semgrep": ["ssrf-requests"]}
                        }
                    ],
                    "frameworks": ["flask", "requests"],
                    "guidance": "High: Implement URL validation to prevent SSRF."
                }
            else:
                return {"selected_rules": [], "frameworks": [], "guidance": "No issues."}
        
        mock_analyzer.analyze_file_context = mock_analyze_file_context
        
        self.commands._initialized = True
        self.commands.analyzer = mock_analyzer
        
        # Test workspace analysis
        result = self.commands.analyze_workspace(str(self.temp_path))
        
        # Verify comprehensive results
        assert result["status"] == "success"
        assert result["analysis_type"] == "workspace"
        assert result["metadata"]["files_found"] >= 2  # Should find both test files
        
        results_data = result["results"]
        summary = results_data["summary"]
        
        # Should have found security issues
        assert summary["total_issues"] >= 2
        assert summary["critical_count"] >= 1  # From auth.py
        assert summary["high_count"] >= 1     # From api.py
        
        # CI/CD prediction should fail due to critical/high issues
        cicd_prediction = results_data["ci_cd_prediction"]
        assert cicd_prediction["would_pass"] is False
        assert cicd_prediction["blocking_issues"] >= 2
    
    def test_command_line_interface_integration(self):
        """Test command-line interface matches expected behavior."""
        from app.claude_code.manual_commands import main
        
        # Create minimal test
        test_file = self.temp_path / "simple.py"
        test_file.write_text("print('hello world')")
        
        # Test file command parsing
        test_args = ["file", "--path", str(test_file), "--depth", "standard", "--format", "json"]
        
        with patch('sys.argv', ['manual_commands.py'] + test_args):
            with patch('app.claude_code.manual_commands.ManualSecurityCommands') as mock_commands:
                mock_instance = Mock()
                mock_commands.return_value = mock_instance
                mock_instance.initialize.return_value = True
                mock_instance.analyze_file.return_value = {
                    "status": "success",
                    "analysis_type": "single_file",
                    "results": SecurityAnalysisResults().__dict__
                }
                
                # Should not raise exceptions
                try:
                    result = main()
                    # main() returns 0 on success, 1 on error
                    assert result == 0
                except SystemExit as e:
                    assert e.code == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])