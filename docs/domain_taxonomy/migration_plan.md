# Domain Migration Plan

## Overview
Migration strategy for reorganizing existing source-based Rule Cards to domain-based structure.

## Current State
```
app/rule_cards/
├── owasp/          # 46 OWASP-generated rules
├── asvs/           # To be removed (replaced by domain integration)  
└── cryptography/   # 1 existing rule + 11 ASVS integrated rules (proof of concept)
```

## Target State
```
app/rule_cards/
├── api_security/
├── authentication/
├── authorization/
├── configuration/
├── cryptography/
├── data_protection/
├── file_handling/
├── input_validation/
├── logging/
├── network_security/
├── secure_coding/
├── secure_communication/
├── session_management/
├── web_security/
```

## Migration Steps

### Phase 1: OWASP Rule Analysis and Mapping
1. Analyze existing OWASP rules to determine domain mapping
2. Create mapping file: `owasp_rule_to_domain_mapping.json`
3. Validate no rules are lost during mapping

### Phase 2: Domain-by-Domain Migration

**Priority 1 Domains:**
- Migrate rules to `app/rule_cards/api_security/`
- Migrate rules to `app/rule_cards/authentication/`
- Migrate rules to `app/rule_cards/authorization/`
- Migrate rules to `app/rule_cards/cryptography/`
- Migrate rules to `app/rule_cards/data_protection/`
- Migrate rules to `app/rule_cards/input_validation/`
- Migrate rules to `app/rule_cards/secure_communication/`
- Migrate rules to `app/rule_cards/session_management/`

**Priority 2 Domains:**
- Migrate rules to `app/rule_cards/configuration/`
- Migrate rules to `app/rule_cards/file_handling/`
- Migrate rules to `app/rule_cards/logging/`
- Migrate rules to `app/rule_cards/web_security/`

**Priority 3 Domains:**
- Migrate rules to `app/rule_cards/network_security/`
- Migrate rules to `app/rule_cards/secure_coding/`

### Phase 3: Validation and Cleanup
1. Validate all original rules successfully migrated
2. Update semantic search corpus paths
3. Remove source-based directories (`app/rule_cards/owasp/`, `app/rule_cards/asvs/`)
4. Update documentation and tooling references

## Rollback Plan
1. Backup created before migration in `app/rule_cards/.backup/`
2. Git branch protection ensures full history preservation
3. Validation scripts verify no data loss at each step
