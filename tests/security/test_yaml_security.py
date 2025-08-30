#!/usr/bin/env python3
"""
Security tests for YAML parsing and validation
Tests for YAML injection prevention and safe parsing
"""
import os
import tempfile
import pytest
import yaml
from app.tools.validate_cards import SecureRuleCardValidator

class TestYAMLSecurity:
    """Test YAML security controls"""
    
    def setup_method(self):
        """Setup test environment"""
        self.schema_path = "app/tools/rule-card-schema.json"
        self.validator = SecureRuleCardValidator(self.schema_path)
    
    def test_safe_yaml_load_prevents_code_execution(self):
        """Test that yaml.safe_load is used to prevent code execution"""
        # Create malicious YAML content that would execute Python code
        malicious_yaml = """!!python/object/apply:os.system
- 'echo "COMPROMISED" > /tmp/test_compromise'
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(malicious_yaml)
            f.flush()
            
            try:
                # This should fail safely without executing code
                result = self.validator._safe_load_yaml(f.name)
                
                # Result should be None due to YAML parsing error (safe_load doesn't support Python objects)
                assert result is None
                
                # Should have validation error (not security warning, but error due to safe_load)
                assert len(self.validator.validation_errors) > 0
                
                # Verify no code was executed
                assert not os.path.exists('/tmp/test_compromise')
                
            finally:
                os.unlink(f.name)
    
    def test_malformed_yaml_handling(self):
        """Test handling of malformed YAML files"""
        malformed_yaml = """
        invalid: yaml: content:
        - missing
          proper: indentation
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(malformed_yaml)
            f.flush()
            
            try:
                result = self.validator._safe_load_yaml(f.name)
                
                # Should handle gracefully
                assert result is None
                assert len(self.validator.validation_errors) > 0
                
            finally:
                os.unlink(f.name)
    
    def test_empty_file_handling(self):
        """Test handling of empty YAML files"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            # Write empty content
            f.write("")
            f.flush()
            
            try:
                result = self.validator._safe_load_yaml(f.name)
                
                # Empty YAML should return None safely
                assert result is None
                
            finally:
                os.unlink(f.name)
    
    def test_non_dict_yaml_handling(self):
        """Test handling of YAML that doesn't parse to dictionary"""
        list_yaml = """
        - item1
        - item2
        - item3
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(list_yaml)
            f.flush()
            
            try:
                result = self.validator._safe_load_yaml(f.name)
                
                # Should be None with security warning
                assert result is None
                assert any("YAML root must be object" in warning 
                          for warning in self.validator.security_warnings)
                
            finally:
                os.unlink(f.name)
    
    def test_directory_traversal_prevention(self):
        """Test prevention of directory traversal attacks"""
        # Test various directory traversal attempts
        traversal_paths = [
            "../../../etc/passwd",
            "/etc/passwd",
            "app/tools/../../../etc/passwd"
        ]
        
        for path in traversal_paths:
            with pytest.raises(ValueError, match="(Invalid.*path|Failed to load schema)"):
                SecureRuleCardValidator(path)
    
    def test_unicode_handling(self):
        """Test safe handling of unicode content in YAML"""
        unicode_yaml = """
id: TEST-UNICODE-001
title: "Test with unicode: 你好世界 🔒"
severity: low
scope: test
requirement: "Unicode handling test"
do:
  - "Handle unicode safely: ñáéíóú"
dont:
  - "Don't fail on unicode: العربية"
detect:
  test:
    - "unicode-test"
verify:
  tests:
    - "Unicode validation test"
refs:
  test:
    - "UNICODE-1"
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False, encoding='utf-8') as f:
            f.write(unicode_yaml)
            f.flush()
            
            try:
                result = self.validator._safe_load_yaml(f.name)
                
                # Should handle unicode content safely
                assert result is not None
                assert isinstance(result, dict)
                assert "你好世界 🔒" in result.get('title', '')
                
            finally:
                os.unlink(f.name)