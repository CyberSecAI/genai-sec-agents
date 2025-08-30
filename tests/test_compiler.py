#!/usr/bin/env python3
"""
Comprehensive test suite for the Rule Card compiler system.

Tests include:
- Unit tests for compiler components
- Integration tests for end-to-end compilation
- Security tests for YAML deserialization attacks
- Schema validation tests
"""

import pytest
import tempfile
import yaml
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
import os

# Add app/tools to path for importing compiler
sys.path.insert(0, str(Path(__file__).parent.parent / 'app' / 'tools'))

from compile_agents import RuleCardCompiler, CompilerConfig, SecurityError, CompilerError


class TestRuleCardCompiler:
    """Test suite for RuleCardCompiler class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def sample_manifest(self, temp_dir):
        """Create sample manifest for testing."""
        manifest = {
            'version': '1.0',
            'agents': [{
                'name': 'test-agent',
                'description': 'Test agent',
                'rule_cards': ['*.yml'],
                'output_file': 'test-agent.json'
            }],
            'compilation': {'schema_version': '1.0'}
        }
        
        manifest_path = temp_dir / 'manifest.yml'
        with open(manifest_path, 'w') as f:
            yaml.safe_dump(manifest, f)
        
        return str(manifest_path)
    
    @pytest.fixture
    def sample_rule_card(self, temp_dir):
        """Create sample rule card for testing."""
        rule_card = {
            'id': 'TEST-001',
            'title': 'Test security rule',
            'severity': 'medium',
            'scope': 'test-applications',
            'requirement': 'Test requirement',
            'do': ['Test positive practice'],
            'dont': ['Test anti-pattern'],
            'detect': {
                'semgrep': ['test-rule-id'],
                'trufflehog': ['Test Secret']
            },
            'verify': {
                'tests': ['Test verification step']
            },
            'refs': {
                'cwe': ['CWE-123'],
                'asvs': ['V1.1.1']
            }
        }
        
        rule_cards_dir = temp_dir / 'rule_cards'
        rule_cards_dir.mkdir()
        
        rule_file = rule_cards_dir / 'test-rule.yml'
        with open(rule_file, 'w') as f:
            yaml.safe_dump(rule_card, f)
        
        return str(rule_cards_dir)
    
    def test_load_manifest_success(self, sample_manifest):
        """Test successful manifest loading."""
        config = CompilerConfig(
            manifest_path=sample_manifest,
            rule_cards_path='',
            output_path=''
        )
        
        compiler = RuleCardCompiler(config)
        manifest = compiler.load_manifest()
        
        assert manifest['version'] == '1.0'
        assert len(manifest['agents']) == 1
        assert manifest['agents'][0]['name'] == 'test-agent'
    
    def test_load_manifest_missing_file(self, temp_dir):
        """Test manifest loading with missing file."""
        config = CompilerConfig(
            manifest_path=str(temp_dir / 'nonexistent.yml'),
            rule_cards_path='',
            output_path=''
        )
        
        compiler = RuleCardCompiler(config)
        
        with pytest.raises(CompilerError, match="Manifest file not found"):
            compiler.load_manifest()
    
    def test_load_manifest_invalid_yaml(self, temp_dir):
        """Test manifest loading with invalid YAML."""
        invalid_manifest = temp_dir / 'invalid.yml'
        with open(invalid_manifest, 'w') as f:
            f.write("invalid: yaml: content: [")
        
        config = CompilerConfig(
            manifest_path=str(invalid_manifest),
            rule_cards_path='',
            output_path=''
        )
        
        compiler = RuleCardCompiler(config)
        
        with pytest.raises(CompilerError, match="Invalid YAML in manifest"):
            compiler.load_manifest()
    
    def test_load_rule_cards_success(self, sample_manifest, sample_rule_card):
        """Test successful rule card loading."""
        config = CompilerConfig(
            manifest_path=sample_manifest,
            rule_cards_path=sample_rule_card,
            output_path=''
        )
        
        compiler = RuleCardCompiler(config)
        rule_cards = compiler.load_rule_cards(['*.yml'])
        
        assert len(rule_cards) == 1
        assert rule_cards[0]['id'] == 'TEST-001'
        assert rule_cards[0]['title'] == 'Test security rule'
    
    def test_path_traversal_prevention(self, sample_manifest):
        """Test prevention of directory traversal attacks."""
        config = CompilerConfig(
            manifest_path=sample_manifest,
            rule_cards_path='',
            output_path=''
        )
        
        compiler = RuleCardCompiler(config)
        
        # Test path traversal patterns
        malicious_patterns = [
            '../../../etc/passwd',
            '/etc/passwd',
            '..\\..\\windows\\system32',
            './../sensitive_file.yml'
        ]
        
        for pattern in malicious_patterns:
            with pytest.raises(SecurityError, match="Unsafe rule card pattern"):
                compiler.load_rule_cards([pattern])
    
    def test_yaml_deserialization_security(self, temp_dir):
        """Test YAML deserialization security with malicious payloads."""
        # Create malicious YAML that would execute code with unsafe loader
        malicious_yaml = temp_dir / 'malicious.yml'
        with open(malicious_yaml, 'w') as f:
            f.write("""
id: TEST-MALICIOUS
title: Malicious rule
severity: high
scope: test
requirement: Test
do: []
dont: []
detect: {}
verify: {tests: []}
refs: {}
malicious: !!python/object/apply:os.system ["echo 'COMPROMISED'"]
            """)
        
        config = CompilerConfig(
            manifest_path='',
            rule_cards_path=str(temp_dir),
            output_path=''
        )
        
        compiler = RuleCardCompiler(config)
        
        # Should not execute the malicious code due to safe_load
        rule_cards = compiler.load_rule_cards(['malicious.yml'])
        
        # Should load successfully but without executing malicious payload
        assert len(rule_cards) == 1
        assert 'malicious' not in rule_cards[0]  # malicious key should be ignored/safe
    
    def test_validation_hooks_aggregation(self, sample_manifest, sample_rule_card):
        """Test validation hooks aggregation functionality."""
        config = CompilerConfig(
            manifest_path=sample_manifest,
            rule_cards_path=sample_rule_card,
            output_path=''
        )
        
        compiler = RuleCardCompiler(config)
        rule_cards = compiler.load_rule_cards(['*.yml'])
        hooks = compiler.aggregate_validation_hooks(rule_cards)
        
        assert 'semgrep' in hooks
        assert 'trufflehog' in hooks
        assert 'test-rule-id' in hooks['semgrep']
        assert 'Test Secret' in hooks['trufflehog']
    
    def test_metadata_generation(self, sample_manifest):
        """Test metadata generation functionality."""
        config = CompilerConfig(
            manifest_path=sample_manifest,
            rule_cards_path='',
            output_path=''
        )
        
        compiler = RuleCardCompiler(config)
        metadata = compiler.generate_metadata()
        
        # Check required metadata fields
        assert 'version' in metadata
        assert 'build_date' in metadata
        assert 'source_digest' in metadata
        assert 'attribution' in metadata
        assert 'compiler_version' in metadata
        
        # Validate format
        assert metadata['source_digest'].startswith('sha256:')
        assert len(metadata['version']) > 0
        assert metadata['compiler_version'] == '1.0.0'
    
    @patch('subprocess.check_output')
    def test_git_version_generation(self, mock_git, sample_manifest):
        """Test Git version generation."""
        mock_git.return_value = 'abc123def456\n'
        
        config = CompilerConfig(
            manifest_path=sample_manifest,
            rule_cards_path='',
            output_path=''
        )
        
        compiler = RuleCardCompiler(config)
        version = compiler._get_git_version()
        
        assert version.startswith('abc123de')
        assert '-' in version  # Should include timestamp
    
    def test_safe_output_path_validation(self, temp_dir):
        """Test output path validation for security."""
        config = CompilerConfig(
            manifest_path='',
            rule_cards_path='',
            output_path=str(temp_dir / 'output')
        )
        
        compiler = RuleCardCompiler(config)
        
        # Valid paths
        safe_path = temp_dir / 'output' / 'agent.json'
        assert compiler._is_safe_output_path(safe_path)
        
        # Invalid paths (traversal attempts)
        unsafe_paths = [
            temp_dir / 'output' / '..' / '..' / 'etc' / 'passwd',
            Path('/etc/passwd'),
            temp_dir / 'output' / '..' / 'sensitive.json'
        ]
        
        for unsafe_path in unsafe_paths:
            assert not compiler._is_safe_output_path(unsafe_path)


class TestCompilerIntegration:
    """Integration tests for end-to-end compilation."""
    
    def test_end_to_end_compilation(self, temp_dir):
        """Test complete compilation workflow."""
        # Setup test environment
        rule_cards_dir = temp_dir / 'rule_cards'
        rule_cards_dir.mkdir()
        
        output_dir = temp_dir / 'output'
        
        # Create test rule card
        test_rule = {
            'id': 'INTEGRATION-TEST-001',
            'title': 'Integration test rule',
            'severity': 'high',
            'scope': 'test',
            'requirement': 'Test requirement',
            'do': ['Test practice'],
            'dont': ['Test anti-pattern'],
            'detect': {'semgrep': ['test-integration-rule']},
            'verify': {'tests': ['Test verification']},
            'refs': {'cwe': ['CWE-001']}
        }
        
        with open(rule_cards_dir / 'test.yml', 'w') as f:
            yaml.safe_dump(test_rule, f)
        
        # Create test manifest
        manifest = {
            'version': '1.0',
            'agents': [{
                'name': 'integration-test-agent',
                'description': 'Integration test agent',
                'rule_cards': ['*.yml'],
                'output_file': 'integration-test.json'
            }]
        }
        
        manifest_path = temp_dir / 'manifest.yml'
        with open(manifest_path, 'w') as f:
            yaml.safe_dump(manifest, f)
        
        # Run compilation
        config = CompilerConfig(
            manifest_path=str(manifest_path),
            rule_cards_path=str(rule_cards_dir),
            output_path=str(output_dir)
        )
        
        compiler = RuleCardCompiler(config)
        compiler.load_manifest()
        packages = compiler.compile_all_agents()
        
        # Validate results
        assert len(packages) == 1
        
        package_file = packages[0]
        assert package_file.exists()
        
        with open(package_file, 'r') as f:
            package_data = json.load(f)
        
        # Validate package structure
        assert 'agent' in package_data
        assert 'rules' in package_data
        assert 'validation_hooks' in package_data
        
        # Validate agent metadata
        agent = package_data['agent']
        assert agent['name'] == 'integration-test-agent'
        assert 'version' in agent
        assert 'build_date' in agent
        assert 'source_digest' in agent
        
        # Validate rules
        assert len(package_data['rules']) == 1
        assert package_data['rules'][0]['id'] == 'INTEGRATION-TEST-001'
        
        # Validate validation hooks
        assert 'semgrep' in package_data['validation_hooks']
        assert 'test-integration-rule' in package_data['validation_hooks']['semgrep']


class TestSecurityValidation:
    """Security-focused tests for the compiler."""
    
    def test_yaml_safe_load_security(self, temp_dir):
        """Test that YAML loading prevents code execution."""
        # This test ensures our yaml.safe_load() usage is secure
        malicious_content = """
id: MALICIOUS-001
title: Malicious rule
severity: high
scope: test
requirement: Test
do: []
dont: []
detect: {}
verify: {tests: []}
refs: {}
# This would execute code with unsafe loader but should be ignored with safe_load
dangerous: !!python/object/apply:subprocess.call [['touch', '/tmp/compromised']]
        """
        
        malicious_file = temp_dir / 'malicious.yml'
        with open(malicious_file, 'w') as f:
            f.write(malicious_content)
        
        # Load with our compiler's method
        config = CompilerConfig(
            manifest_path='',
            rule_cards_path=str(temp_dir),
            output_path=''
        )
        
        compiler = RuleCardCompiler(config)
        rule_cards = compiler.load_rule_cards(['malicious.yml'])
        
        # Should load without executing malicious code
        assert len(rule_cards) == 1
        assert rule_cards[0]['id'] == 'MALICIOUS-001'
        
        # Verify no file was created (code didn't execute)
        assert not Path('/tmp/compromised').exists()
    
    def test_input_validation_prevents_injection(self, temp_dir):
        """Test input validation prevents various injection attacks."""
        config = CompilerConfig(
            manifest_path='test.yml',
            rule_cards_path=str(temp_dir),
            output_path=str(temp_dir / 'output')
        )
        
        compiler = RuleCardCompiler(config)
        
        # Test various injection patterns
        injection_patterns = [
            '../../../etc/passwd',
            '/etc/passwd',
            '$(rm -rf /)',
            '`cat /etc/passwd`',
            '; rm -rf /',
            '| cat /etc/passwd',
            '&& rm important_file'
        ]
        
        for pattern in injection_patterns:
            with pytest.raises(SecurityError):
                compiler.load_rule_cards([pattern])
    
    def test_path_security_validation(self, temp_dir):
        """Test path security validation functions."""
        config = CompilerConfig(
            manifest_path='',
            rule_cards_path=str(temp_dir),
            output_path=str(temp_dir / 'output')
        )
        
        compiler = RuleCardCompiler(config)
        
        # Test safe paths
        safe_paths = [
            temp_dir / 'test.yml',
            temp_dir / 'subdir' / 'test.yml'
        ]
        
        for safe_path in safe_paths:
            assert compiler._is_safe_path(safe_path)
        
        # Test unsafe paths
        unsafe_paths = [
            Path('/etc/passwd'),
            temp_dir.parent / 'dangerous.yml',
            Path('../../etc/passwd')
        ]
        
        for unsafe_path in unsafe_paths:
            assert not compiler._is_safe_path(unsafe_path)


def test_cli_interface():
    """Test command-line interface functionality."""
    import subprocess
    import sys
    
    compiler_script = Path(__file__).parent.parent / 'app' / 'tools' / 'compile_agents.py'
    
    # Test help output
    result = subprocess.run([
        sys.executable, str(compiler_script), '--help'
    ], capture_output=True, text=True)
    
    assert result.returncode == 0
    assert 'Compile YAML Rule Cards into JSON agent packages' in result.stdout
    assert '--manifest' in result.stdout
    assert '--rule-cards' in result.stdout
    assert '--output' in result.stdout


def test_actual_rule_cards_compilation():
    """Test compilation with actual Rule Cards from Story 1.2."""
    import subprocess
    import sys
    
    compiler_script = Path(__file__).parent.parent / 'app' / 'tools' / 'compile_agents.py'
    
    # Run actual compilation
    result = subprocess.run([
        sys.executable, str(compiler_script)
    ], capture_output=True, text=True, cwd=str(Path(__file__).parent.parent))
    
    if result.returncode != 0:
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
    
    assert result.returncode == 0
    assert "Compilation successful" in result.stdout
    assert "Generated 5 agent packages" in result.stdout
    
    # Verify output files exist
    output_dir = Path(__file__).parent.parent / 'app' / 'dist' / 'agents'
    expected_files = [
        'secrets-specialist.json',
        'web-security-specialist.json', 
        'genai-security-specialist.json',
        'container-security-specialist.json',
        'comprehensive-security-agent.json'
    ]
    
    for expected_file in expected_files:
        output_file = output_dir / expected_file
        assert output_file.exists(), f"Missing output file: {expected_file}"
        
        # Validate JSON structure
        with open(output_file, 'r') as f:
            package_data = json.load(f)
        
        assert 'agent' in package_data
        assert 'rules' in package_data
        assert 'validation_hooks' in package_data
        
        # Validate agent metadata
        agent = package_data['agent']
        required_fields = ['name', 'description', 'version', 'build_date', 'source_digest', 'attribution']
        for field in required_fields:
            assert field in agent, f"Missing agent field: {field}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])