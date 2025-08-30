# Security Guide for Rule Card Development

## Overview
This guide outlines security practices for developing and maintaining Rule Cards in the Policy-as-Code system.

## Rule Card Security Requirements

### YAML Security
- **Safe Parsing**: Always use `yaml.safe_load()` - never `yaml.load()`
- **Input Validation**: Validate all YAML structures against schema
- **File Path Security**: Sanitize and validate file paths to prevent traversal attacks

### Schema Security
- **Strict Validation**: Rule Cards must pass JSON Schema validation
- **Type Safety**: Enforce strict typing for all fields
- **Content Restrictions**: Prevent executable content in YAML

### Development Security
- **Code Review**: All Rule Cards must be reviewed before merge
- **Testing**: Comprehensive testing including security test cases
- **Access Control**: Repository access follows principle of least privilege

## Security Testing
Run security validation with:
```bash
python app/tools/validate_cards.py app/rule_cards/
```

## Threat Model
- **YAML Injection**: Mitigated by safe_load usage
- **Directory Traversal**: Mitigated by path validation
- **Schema Injection**: Mitigated by strict schema enforcement

## Incident Response
Report security issues to: [security-contact]