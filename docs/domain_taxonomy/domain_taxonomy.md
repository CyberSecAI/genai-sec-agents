# Security Domain Taxonomy

## Overview
This document defines the comprehensive domain mapping for organizing Rule Cards by security topic rather than by source standard (OWASP, ASVS, etc.).

## Domain Mapping Configuration

### Priority 1 - Core Security Domains

**authentication**
- Description: User authentication and identity verification
- ASVS Sections: V6, V9, V10
- OWASP Topics: authentication, session_management
- Directory: `app/rule_cards/authentication/`

**authorization**
- Description: Access control and privilege management
- ASVS Sections: V8
- OWASP Topics: authorization, access_control
- Directory: `app/rule_cards/authorization/`

**cryptography**
- Description: Cryptographic implementation and key management
- ASVS Sections: V11
- OWASP Topics: cryptography, key_management, hashing, encryption
- Directory: `app/rule_cards/cryptography/`

**input_validation**
- Description: Input validation and business logic security
- ASVS Sections: V1, V2
- OWASP Topics: input_validation, sql_injection_prevention, business_logic
- Directory: `app/rule_cards/input_validation/`

**session_management**
- Description: Session lifecycle and security
- ASVS Sections: V7
- OWASP Topics: session_management, authentication
- Directory: `app/rule_cards/session_management/`

**api_security**
- Description: REST, GraphQL, and web service security
- ASVS Sections: V4
- OWASP Topics: api_security, rest_security
- Directory: `app/rule_cards/api_security/`

**data_protection**
- Description: Privacy and data handling requirements
- ASVS Sections: V14
- OWASP Topics: data_protection, privacy
- Directory: `app/rule_cards/data_protection/`

**secure_communication**
- Description: TLS and network security
- ASVS Sections: V12
- OWASP Topics: transport_layer_security, network_security
- Directory: `app/rule_cards/secure_communication/`

### Priority 2 - Specialized Domains

**web_security**
- Description: Frontend and client-side security including WebRTC
- ASVS Sections: V3, V17
- OWASP Topics: web_security, frontend_security
- Directory: `app/rule_cards/web_security/`

**file_handling**
- Description: File upload and processing security
- ASVS Sections: V5
- OWASP Topics: file_upload, file_security
- Directory: `app/rule_cards/file_handling/`

**configuration**
- Description: Security configuration and hardening
- ASVS Sections: V13
- OWASP Topics: security_configuration, hardening
- Directory: `app/rule_cards/configuration/`

**logging**
- Description: Security logging and error handling
- ASVS Sections: V16
- OWASP Topics: logging, error_handling
- Directory: `app/rule_cards/logging/`

### Priority 3 - Advanced Topics

**secure_coding**
- Description: Architectural patterns and development practices
- ASVS Sections: V15
- OWASP Topics: secure_coding, architectural_patterns
- Directory: `app/rule_cards/secure_coding/`

**network_security**
- Description: Advanced network-layer protections
- ASVS Sections: V12
- OWASP Topics: network_security, infrastructure_security
- Directory: `app/rule_cards/network_security/`

## Validation Results

❌ Duplicate ASVS sections: V12

## Domain Statistics

- Total domains: 14
- Priority 1 domains: 8
- Priority 2 domains: 4
- Priority 3 domains: 2
- Total ASVS sections covered: 18

