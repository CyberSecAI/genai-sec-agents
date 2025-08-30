#!/usr/bin/env python3
"""
Tests for Rule Card validation functionality
"""
import os
import tempfile
import pytest
from app.tools.validate_cards import SecureRuleCardValidator

class TestRuleCardValidation:
    """Test Rule Card validation logic"""
    
    def setup_method(self):
        """Setup test environment"""
        self.schema_path = "app/tools/rule-card-schema.json"
        self.validator = SecureRuleCardValidator(self.schema_path)
    
    def test_valid_rule_card(self):
        """Test validation of a valid Rule Card"""
        valid_rule_card = """
id: TEST-VALID-001
title: "Test valid rule card"
severity: medium
scope: test
requirement: "This is a test requirement for validation"
do:
  - "Follow this best practice"
  - "Use secure methods"
dont:
  - "Don't use insecure methods"
  - "Avoid bad practices"
detect:
  semgrep:
    - "test.security.rule"
  hadolint:
    - "TEST001"
verify:
  tests:
    - "Test that rule is enforced"
    - "Verify security controls work"
refs:
  owasp:
    - "A01:2021"
  cis:
    - "1.1"
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(valid_rule_card)
            f.flush()
            
            try:
                result = self.validator.validate_rule_card(f.name)
                assert result is True
                assert len(self.validator.validation_errors) == 0
                
            finally:
                os.unlink(f.name)
    
    def test_invalid_rule_card_missing_fields(self):
        """Test validation failure for missing required fields"""
        invalid_rule_card = """
id: TEST-INVALID-001
title: "Incomplete rule card"
# Missing required fields: severity, scope, requirement, do, dont, detect, verify, refs
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(invalid_rule_card)
            f.flush()
            
            try:
                result = self.validator.validate_rule_card(f.name)
                assert result is False
                assert len(self.validator.validation_errors) > 0
                
            finally:
                os.unlink(f.name)
    
    def test_invalid_id_format(self):
        """Test validation failure for invalid ID format"""
        invalid_id_card = """
id: invalid-id-format
title: "Rule card with invalid ID"
severity: low
scope: test
requirement: "Test requirement"
do:
  - "Do something"
dont:
  - "Don't do something"
detect:
  test:
    - "test-rule"
verify:
  tests:
    - "Test validation"
refs:
  test:
    - "TEST-1"
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(invalid_id_card)
            f.flush()
            
            try:
                result = self.validator.validate_rule_card(f.name)
                assert result is False
                assert any("does not match" in error 
                          for error in self.validator.validation_errors)
                
            finally:
                os.unlink(f.name)
    
    def test_invalid_severity_value(self):
        """Test validation failure for invalid severity value"""
        invalid_severity_card = """
id: TEST-SEVERITY-001
title: "Rule card with invalid severity"
severity: extreme
scope: test
requirement: "Test requirement"
do:
  - "Do something"
dont:
  - "Don't do something"
detect:
  test:
    - "test-rule"
verify:
  tests:
    - "Test validation"
refs:
  test:
    - "TEST-1"
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(invalid_severity_card)
            f.flush()
            
            try:
                result = self.validator.validate_rule_card(f.name)
                assert result is False
                assert any("enum" in error.lower() or "extreme" in error
                          for error in self.validator.validation_errors)
                
            finally:
                os.unlink(f.name)
    
    def test_empty_arrays_validation(self):
        """Test validation failure for empty required arrays"""
        empty_arrays_card = """
id: TEST-EMPTY-001
title: "Rule card with empty arrays"
severity: low
scope: test
requirement: "Test requirement"
do: []
dont: []
detect:
  test:
    - "test-rule"
verify:
  tests:
    - "Test validation"
refs:
  test:
    - "TEST-1"
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(empty_arrays_card)
            f.flush()
            
            try:
                result = self.validator.validate_rule_card(f.name)
                assert result is False
                assert any("should be non-empty" in error or "minItems" in error
                          for error in self.validator.validation_errors)
                
            finally:
                os.unlink(f.name)
    
    def test_directory_validation(self):
        """Test directory validation functionality"""
        # Create temporary directory with test Rule Cards
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create valid Rule Card
            valid_card = """
id: TEMP-VALID-001
title: "Temporary valid rule card"
severity: low
scope: test
requirement: "Test requirement"
do:
  - "Do something"
dont:
  - "Don't do something"
detect:
  test:
    - "test-rule"
verify:
  tests:
    - "Test validation"
refs:
  test:
    - "TEST-1"
"""
            
            # Create invalid Rule Card
            invalid_card = """
id: TEMP-INVALID-001
title: "Temporary invalid rule card"
# Missing required fields
"""
            
            # Write files
            with open(os.path.join(temp_dir, "valid.yml"), 'w') as f:
                f.write(valid_card)
            
            with open(os.path.join(temp_dir, "invalid.yml"), 'w') as f:
                f.write(invalid_card)
            
            # Test directory validation
            results = self.validator.validate_directory(temp_dir)
            
            assert results["total"] == 2
            assert results["valid"] == 1
            assert results["invalid"] == 1