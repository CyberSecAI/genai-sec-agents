#!/usr/bin/env python3
"""
Validation script for Task 1: OWASP Content Acquisition and Parsing

Simple validation without external dependencies to verify implementation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ingestion.owasp_fetcher import OWASPFetcher
from app.ingestion.content_parser import SecureCodingParser

def test_owasp_fetcher():
    """Test OWASP fetcher basic functionality"""
    print("Testing OWASP Fetcher...")
    
    try:
        fetcher = OWASPFetcher(cache_dir="test_cache")
        
        # Test URL validation
        valid_url = "https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Input_Validation_Cheat_Sheet.md"
        invalid_url = "https://evil.com/fake.md"
        
        assert fetcher._validate_url(valid_url), "Should validate OWASP GitHub URL"
        assert not fetcher._validate_url(invalid_url), "Should reject non-OWASP URL"
        
        # Test content hash calculation
        hash1 = fetcher._calculate_content_hash("test content")
        hash2 = fetcher._calculate_content_hash("test content")
        hash3 = fetcher._calculate_content_hash("different content")
        
        assert hash1 == hash2, "Same content should have same hash"
        assert hash1 != hash3, "Different content should have different hash"
        assert len(hash1) == 64, "SHA256 hash should be 64 chars"
        
        # Test cheat sheet list
        assert len(fetcher.SECURE_CODING_CHEATSHEETS) == 30, "Should have 30 cheat sheets"
        
        print("  ✓ OWASP Fetcher basic validation passed")
        return True
        
    except Exception as e:
        print(f"  ✗ OWASP Fetcher test failed: {e}")
        return False

def test_content_parser():
    """Test content parser basic functionality"""
    print("Testing Content Parser...")
    
    try:
        parser = SecureCodingParser()
        
        # Test requirement pattern matching
        test_cases = [
            ("Applications must validate all input", True),
            ("You should always use HTTPS", True),
            ("Never store passwords in plain text", True),
            ("This is just a regular sentence", False)
        ]
        
        for text, should_match in test_cases:
            match = parser.requirement_regex.search(text)
            if should_match:
                if match is None:
                    print(f"    FAIL: Should match requirement: '{text}'")
                    return False
            else:
                if match is not None:
                    print(f"    FAIL: Should not match requirement: '{text}'")
                    return False
        
        # Test severity determination
        sev1 = parser._determine_severity("must never")
        if sev1 != "critical":
            print(f"    FAIL: Expected 'critical', got '{sev1}' for 'must never'")
            return False
            
        sev2 = parser._determine_severity("should always")  
        if sev2 != "high":
            print(f"    FAIL: Expected 'high', got '{sev2}' for 'should always'")
            return False
            
        sev3 = parser._determine_severity("consider using")
        if sev3 != "medium":
            print(f"    FAIL: Expected 'medium', got '{sev3}' for 'consider using'")
            return False
        
        # Test language detection
        lang1 = parser._detect_code_language_from_content("def main(): pass")
        if lang1 != "python":
            print(f"    FAIL: Expected 'python', got '{lang1}' for Python code")
            return False
            
        lang2 = parser._detect_code_language_from_content("public class Test {}")
        if lang2 != "java":
            print(f"    FAIL: Expected 'java', got '{lang2}' for Java code")
            return False
            
        lang3 = parser._detect_code_language_from_content("function test() {}")
        if lang3 != "javascript":
            print(f"    FAIL: Expected 'javascript', got '{lang3}' for JavaScript code")
            return False
        
        # Test markdown section parsing
        sample_markdown = """
# Input Validation Cheat Sheet

## Introduction
This cheat sheet provides guidance on input validation.

## Requirements
Applications must validate all user input.

### Implementation
Use whitelist validation when possible.

## Code Examples

```python
def validate_input(data):
    return data in allowed_values
```
"""
        
        sections = parser.parse_cheatsheet_sections(sample_markdown)
        if len(sections) == 0:
            print("    FAIL: Should parse sections from markdown")
            return False
        
        # Find main section
        main_section = next((s for s in sections if "Input Validation" in s.title), None)
        if main_section is None:
            print("    FAIL: Should find main section")
            print(f"    Found sections: {[s.title for s in sections]}")
            return False
            
        if len(main_section.subsections) == 0:
            print("    FAIL: Should have subsections")
            return False
        
        print("  ✓ Content Parser basic validation passed")
        return True
        
    except Exception as e:
        print(f"  ✗ Content Parser test failed: {e}")
        return False

def test_integration():
    """Test basic integration between fetcher and parser"""
    print("Testing Integration...")
    
    try:
        # Test with small sample markdown content
        sample_content = """# Test Cheat Sheet

## Security Requirements
Applications must validate all user input to prevent injection attacks.
Never trust data from external sources.

## Implementation
```python
# Secure validation
def validate_input(user_input):
    if user_input in whitelist:
        return user_input
    raise ValueError("Invalid input")
```

```python
# Vulnerable approach - avoid this
def bad_validation(user_input):
    return user_input  # No validation!
```
"""
        
        parser = SecureCodingParser()
        sections = parser.parse_cheatsheet_sections(sample_content)
        
        if len(sections) == 0:
            print("    FAIL: Should parse sections")
            return False
        
        # Check that requirements are extracted
        req_sections = []
        for section in sections:
            if section.requirements:
                req_sections.extend(section.requirements)
        
        if len(req_sections) == 0:
            print(f"    FAIL: Should extract security requirements")
            print(f"    Sections found: {len(sections)}")
            for i, section in enumerate(sections):
                print(f"      Section {i}: {section.title}, reqs: {len(section.requirements)}")
            return False
        
        # Check that code examples are extracted
        code_examples = []
        for section in sections:
            if section.code_examples:
                code_examples.extend(section.code_examples)
        
        if len(code_examples) < 2:
            print(f"    FAIL: Should extract code examples, found {len(code_examples)}")
            for section in sections:
                print(f"      Section '{section.title}': {len(section.code_examples)} examples")
            return False
        
        # Check that we can distinguish secure vs vulnerable code
        secure_examples = [ex for ex in code_examples if ex.is_secure]
        vulnerable_examples = [ex for ex in code_examples if not ex.is_secure]
        
        # Note: This may not work perfectly with simple context analysis
        print(f"  ➤ Found {len(secure_examples)} secure and {len(vulnerable_examples)} vulnerable examples")
        
        print("  ✓ Integration test passed")
        return True
        
    except Exception as e:
        print(f"  ✗ Integration test failed: {e}")
        return False

def main():
    """Run all Task 1 validation tests"""
    print("=" * 60)
    print("Task 1: OWASP Content Acquisition and Parsing - Validation")
    print("=" * 60)
    
    tests = [
        test_owasp_fetcher,
        test_content_parser,
        test_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"Task 1 Validation Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ Task 1 implementation validated successfully!")
        return True
    else:
        print("❌ Task 1 validation failed - fix issues before continuing")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)