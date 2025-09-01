# OWASP Domain Migration Analysis
Generated: 2025-09-01T14:04:59+01:00

## Current Structure Analysis
- Total OWASP rules: 46
- OWASP source directories: 15

## Source to Domain Mapping

### Secure Coding Domain
- Total rules to migrate: 12
  - java_security: 3 rules
  - expressjs_security: 3 rules
  - laravel_security: 3 rules
  - nodejs_security: 3 rules

### Web Security Domain
- Total rules to migrate: 9
  - xss_prevention: 3 rules
  - clickjacking_defense: 3 rules
  - dom_xss_prevention: 3 rules

### Input Validation Domain
- Total rules to migrate: 6
  - input_validation: 3 rules
  - sql_injection_prevention: 3 rules

### Logging Domain
- Total rules to migrate: 7
  - logging: 4 rules
  - error_handling: 3 rules

### File Handling Domain
- Total rules to migrate: 3
  - file_upload: 3 rules

### Secure Communication Domain
- Total rules to migrate: 3
  - http_headers: 3 rules

### Session Management Domain
- Total rules to migrate: 3
  - session_management: 3 rules

### Authentication Domain
- Total rules to migrate: 3
  - authentication: 3 rules

## Domain Directory Status

- authentication: ✅ Exists (51 existing rules)
- authorization: ✅ Exists (12 existing rules)
- cryptography: ✅ Exists (8 existing rules)
- input_validation: ❌ Missing (0 existing rules)
- session_management: ✅ Exists (15 existing rules)
- api_security: ❌ Missing (0 existing rules)
- data_protection: ✅ Exists (13 existing rules)
- secure_communication: ❌ Missing (0 existing rules)
- web_security: ❌ Missing (0 existing rules)
- file_handling: ❌ Missing (0 existing rules)
- configuration: ❌ Missing (0 existing rules)
- logging: ❌ Missing (0 existing rules)
- secure_coding: ❌ Missing (0 existing rules)
- network_security: ✅ Exists (9 existing rules)