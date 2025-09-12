#!/usr/bin/env python3
"""
Test script for LLM-based rule card generation

Demonstrates how to use ChatGPT to convert OWASP cheat sheets to Rule Cards.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_with_sample_content():
    """Test with a sample OWASP cheat sheet excerpt"""
    
    # Sample OWASP content (Input Validation excerpt)
    sample_content = """# Input Validation Cheat Sheet

## Introduction

Input validation is performed to ensure only properly formed data is entering the workflow in an information system, preventing malformed data from persisting in the database and triggering malfunction of various downstream components.

## General Validation Rules

### Syntactic Validation
- Data type checks (e.g. string, integer, float)
- Length checks
- Range checks (minimum and maximum values)
- Format checks using regular expressions

### Semantic Validation
- Business logic validation
- Cross-field validation
- Database lookups for reference data validation

## Implementation Guidelines

### Use Allowlists over Blocklists
Always prefer allowlist validation (define what is allowed) over blocklist validation (define what is not allowed). Allowlists are more secure because:
- They prevent unknown attack vectors
- They are easier to maintain
- They provide better performance

```python
# Good - Allowlist validation
ALLOWED_COUNTRIES = ['US', 'CA', 'UK', 'DE', 'FR']
if country_code not in ALLOWED_COUNTRIES:
    raise ValueError("Invalid country code")
```

```python
# Bad - Blocklist validation  
BLOCKED_COUNTRIES = ['XX', 'YY', 'ZZ']
if country_code in BLOCKED_COUNTRIES:
    raise ValueError("Blocked country code")
```

### Input Sanitization
Input should be validated on both syntactic and semantic level:
- Validate input type, length, format and range
- Validate business rules
- Sanitize input by encoding or escaping special characters

### Server-side Validation
Client-side validation should never be relied upon for security. All validation must occur on the server side:
- Client-side validation is for user experience only
- Server-side validation is the security control
- Never trust data from the client

## Common Mistakes

### Relying Only on Client-side Validation
```javascript
// Vulnerable - client-side only
function validateEmail(email) {
    return email.includes('@');
}
```

### Using Inadequate Regular Expressions
```python
# Vulnerable - inadequate regex
import re
if not re.match(r'^[a-zA-Z]+$', username):
    raise ValueError("Invalid username")
```

## References
- OWASP Input Validation Cheat Sheet
- CWE-20: Improper Input Validation
- NIST SP 800-53: Security Controls for Federal Information Systems"""

    print("Sample OWASP Content:")
    print("=" * 80)
    print(sample_content[:500] + "..." if len(sample_content) > 500 else sample_content)
    print("=" * 80)
    
    print("\n📋 Example Rule Card Format:")
    print("-" * 40)
    
    example_rule_card = """id: INPUT-VALIDATION-001
title: "Use allowlist validation instead of blocklist validation"
severity: high
scope: web-application
requirement: "All user input validation must use allowlist (define what is allowed) rather than blocklist (define what is not allowed) approaches to prevent unknown attack vectors and improve security posture."
do:
  - "Define explicit allowlists of acceptable input values, formats, and ranges"
  - "Validate input against predetermined acceptable patterns"
  - "Use strict type checking and format validation"
  - "Implement comprehensive input length and range checks"
dont:
  - "Rely on blocklist validation that tries to identify bad input"
  - "Assume client-side validation provides security"
  - "Skip server-side validation for any user input"
  - "Use overly permissive regular expressions"
detect:
  semgrep:
    - "security.audit.input-validation.blocklist-validation"
    - "security.audit.input-validation.missing-server-validation"
  custom:
    - "Look for validation logic that blocks specific patterns rather than allowing specific patterns"
    - "Identify client-side only validation without server-side counterpart"
verify:
  tests:
    - "Test input validation with malformed data"
    - "Verify server-side validation exists for all user inputs"
    - "Test that allowlist validation rejects unexpected input formats"
refs:
  cwe:
    - "CWE-20"
  owasp:
    - "A03:2021-Injection"
  nist:
    - "SI-10"""
    
    print(example_rule_card)
    print("-" * 40)
    
    print(f"\n🤖 Usage Instructions:")
    print(f"1. Set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
    print(f"2. Run: python3 app/ingestion/llm_rule_generator.py")
    print(f"3. Generated rule cards will be saved to app/rule_cards/owasp/")
    
    print(f"\n💰 Cost Estimation:")
    print(f"- ~30 cheat sheets × ~4000 tokens each = ~120K tokens")  
    print(f"- GPT-4: ~$2.40 total cost")
    print(f"- GPT-3.5-turbo: ~$0.24 total cost")
    
    print(f"\n⚡ Expected Output:")
    print(f"- 3-8 rule cards per cheat sheet")
    print(f"- ~150-240 total rule cards generated")
    print(f"- Organized in subdirectories by cheat sheet topic")
    
    return True

def test_api_key_check():
    """Check if OpenAI API key is configured"""
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"✓ OpenAI API key configured (ends with: ...{api_key[-4:]})")
        return True
    else:
        print("✗ OpenAI API key not found")
        print("  Set it with: export OPENAI_API_KEY='your-key-here'")
        return False

def main():
    """Run the demonstration"""
    print("🤖 LLM-based OWASP Rule Card Generation Demo")
    print("=" * 60)
    
    # Check API key
    has_api_key = test_api_key_check()
    print()
    
    # Show sample content and expected output
    test_with_sample_content()
    
    if has_api_key:
        print(f"\n🚀 Ready to generate! Run:")
        print(f"   python3 app/ingestion/llm_rule_generator.py")
    else:
        print(f"\n⚠️  Set your API key first:")
        print(f"   export OPENAI_API_KEY='your-openai-api-key'")
    
    return 0

if __name__ == "__main__":
    exit(main())