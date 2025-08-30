#!/usr/bin/env python3
"""
Simple test runner for Rule Card compiler without external dependencies.
"""

import tempfile
import yaml
import json
from pathlib import Path
import sys
import os

# Add app/tools to path for importing compiler
sys.path.insert(0, str(Path(__file__).parent.parent / 'app' / 'tools'))

from compile_agents import RuleCardCompiler, CompilerConfig, SecurityError, CompilerError


def test_manifest_loading():
    """Test manifest loading functionality."""
    print("🔍 Testing manifest loading...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir)
        
        # Create test manifest
        manifest = {
            'version': '1.0',
            'agents': [{
                'name': 'test-agent',
                'description': 'Test agent',
                'rule_cards': ['*.yml'],
                'output_file': 'test-agent.json'
            }]
        }
        
        manifest_path = temp_dir / 'manifest.yml'
        with open(manifest_path, 'w') as f:
            yaml.safe_dump(manifest, f)
        
        # Test loading
        config = CompilerConfig(
            manifest_path=str(manifest_path),
            rule_cards_path='',
            output_path=''
        )
        
        compiler = RuleCardCompiler(config)
        loaded_manifest = compiler.load_manifest()
        
        assert loaded_manifest['version'] == '1.0'
        assert len(loaded_manifest['agents']) == 1
        print("✅ Manifest loading test passed")


def test_rule_card_loading():
    """Test rule card loading functionality."""
    print("🔍 Testing rule card loading...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir)
        
        # Create test rule card
        rule_card = {
            'id': 'TEST-001',
            'title': 'Test rule',
            'severity': 'medium',
            'scope': 'test',
            'requirement': 'Test requirement',
            'do': ['Test practice'],
            'dont': ['Test anti-pattern'],
            'detect': {'semgrep': ['test-rule']},
            'verify': {'tests': ['Test verification']},
            'refs': {'cwe': ['CWE-123']}
        }
        
        rule_file = temp_dir / 'test.yml'
        with open(rule_file, 'w') as f:
            yaml.safe_dump(rule_card, f)
        
        # Test loading
        config = CompilerConfig(
            manifest_path='',
            rule_cards_path=str(temp_dir),
            output_path=''
        )
        
        compiler = RuleCardCompiler(config)
        rule_cards = compiler.load_rule_cards(['*.yml'])
        
        assert len(rule_cards) == 1
        assert rule_cards[0]['id'] == 'TEST-001'
        print("✅ Rule card loading test passed")


def test_security_validation():
    """Test security validation features."""
    print("🔍 Testing security validation...")
    
    config = CompilerConfig(
        manifest_path='',
        rule_cards_path='/tmp',
        output_path='/tmp'
    )
    
    compiler = RuleCardCompiler(config)
    
    # Test path traversal prevention
    try:
        compiler.load_rule_cards(['../../../etc/passwd'])
        assert False, "Should have raised SecurityError"
    except SecurityError:
        print("✅ Path traversal prevention test passed")
    
    # Test YAML security with malicious content
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir)
        
        # Create potentially malicious YAML (safe_load should handle this)
        malicious_yaml = temp_dir / 'malicious.yml'
        with open(malicious_yaml, 'w') as f:
            f.write("""
id: TEST-MALICIOUS
title: Test rule
severity: high
scope: test
requirement: Test
do: []
dont: []
detect: {}
verify: {tests: []}
refs: {}
            """)
        
        config_secure = CompilerConfig(
            manifest_path='',
            rule_cards_path=str(temp_dir),
            output_path=''
        )
        
        compiler_secure = RuleCardCompiler(config_secure)
        rule_cards = compiler_secure.load_rule_cards(['malicious.yml'])
        
        assert len(rule_cards) == 1
        print("✅ YAML security test passed")


def test_validation_hooks_aggregation():
    """Test validation hooks aggregation."""
    print("🔍 Testing validation hooks aggregation...")
    
    rule_cards = [
        {
            'id': 'TEST-001',
            'detect': {
                'semgrep': ['rule1', 'rule2'],
                'trufflehog': ['secret1']
            }
        },
        {
            'id': 'TEST-002', 
            'detect': {
                'semgrep': ['rule2', 'rule3'],  # rule2 should be deduplicated
                'codeql': ['query1']
            }
        }
    ]
    
    config = CompilerConfig(
        manifest_path='',
        rule_cards_path='',
        output_path=''
    )
    
    compiler = RuleCardCompiler(config)
    hooks = compiler.aggregate_validation_hooks(rule_cards)
    
    assert 'semgrep' in hooks
    assert 'trufflehog' in hooks
    assert 'codeql' in hooks
    
    # Check deduplication
    assert len(hooks['semgrep']) == 3  # rule1, rule2, rule3 (deduplicated)
    assert 'rule1' in hooks['semgrep']
    assert 'rule2' in hooks['semgrep'] 
    assert 'rule3' in hooks['semgrep']
    
    assert hooks['trufflehog'] == ['secret1']
    assert hooks['codeql'] == ['query1']
    
    print("✅ Validation hooks aggregation test passed")


def test_actual_compilation():
    """Test compilation with actual Rule Cards from Story 1.2."""
    print("🔍 Testing actual Rule Cards compilation...")
    
    try:
        # Test with actual project files
        project_root = Path(__file__).parent.parent
        
        config = CompilerConfig(
            manifest_path=str(project_root / 'app' / 'tools' / 'agents_manifest.yml'),
            rule_cards_path=str(project_root / 'app' / 'rule_cards'),
            output_path=str(project_root / 'app' / 'dist' / 'agents')
        )
        
        compiler = RuleCardCompiler(config)
        compiler.load_manifest()
        packages = compiler.compile_all_agents()
        
        assert len(packages) == 5
        
        # Validate one package structure
        with open(packages[0], 'r') as f:
            package_data = json.load(f)
        
        required_sections = ['agent', 'rules', 'validation_hooks']
        for section in required_sections:
            assert section in package_data, f"Missing section: {section}"
        
        # Validate agent metadata
        agent = package_data['agent']
        required_agent_fields = ['name', 'version', 'build_date', 'source_digest', 'attribution']
        for field in required_agent_fields:
            assert field in agent, f"Missing agent field: {field}"
        
        print(f"✅ Actual compilation test passed - {len(packages)} packages generated")
        
    except Exception as e:
        print(f"❌ Actual compilation test failed: {e}")
        raise


def run_all_tests():
    """Run all tests and report results."""
    tests = [
        test_manifest_loading,
        test_rule_card_loading,
        test_security_validation,
        test_validation_hooks_aggregation,
        test_actual_compilation
    ]
    
    passed = 0
    failed = 0
    
    print("🧪 Running Compiler Test Suite")
    print("=" * 50)
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} failed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        print("❌ Some tests failed")
        return 1
    else:
        print("✅ All tests passed!")
        return 0


if __name__ == '__main__':
    exit(run_all_tests())