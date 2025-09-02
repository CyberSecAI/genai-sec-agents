# Policy-as-Code Security Rule Cards

This directory contains a comprehensive collection of security rule cards implementing a Policy-as-Code approach for application security validation and enforcement.

## Overview

The Rule Cards system provides:
- **Standardized security requirements** across multiple domains
- **Scanner tool integration** with Semgrep, TruffleHog, and CodeQL
- **Compliance mapping** to CWE, ASVS, and OWASP standards
- **Structured YAML format** for automation and integration

## Directory Structure

```
app/
├── rule_cards/
│   ├── cookies/          # Secure cookie handling (3 cards)
│   ├── genai/           # GenAI security controls (3 cards) 
│   ├── jwt/             # JWT security validation (4 cards)
│   ├── secrets/         # Hardcoded secrets prevention (4 cards)
│   └── docker/          # Container security (1 card)
└── README.md           # This file
```

## Rule Card Schema

Each rule card follows a standardized YAML structure:

```yaml
id: DOMAIN-TOPIC-001           # Unique identifier
title: "Human readable title"  # Descriptive title
severity: critical|high|medium|low  # Risk severity
scope: application-type        # Applicable scope
requirement: "Detailed requirement description"
do:                           # Positive security practices
  - "Practice 1"
  - "Practice 2"
dont:                         # Security anti-patterns to avoid
  - "Anti-pattern 1"  
  - "Anti-pattern 2"
detect:                       # Scanner tool integration
  semgrep:
    - "rule-id-1"
  trufflehog:
    - "detector-name"
  codeql:
    - "query-name"
verify:                       # Validation tests
  tests:
    - "Test description 1"
refs:                         # Standards compliance
  cwe:
    - "CWE-XXX"
  asvs:
    - "V.X.X"
  owasp:
    - "AXX:YYYY"
  standards:
    - "Standard reference"
```

## Security Domains

### Hardcoded Secrets (4 Cards)
- **SECRETS-API-001**: API key security management
- **SECRETS-DB-001**: Database credential protection  
- **SECRETS-JWT-001**: JWT signing secret security
- **SECRETS-CLOUD-001**: Cloud service credential security

### Secure Cookies (3 Cards)
- **COOKIES-HTTPONLY-001**: HttpOnly attribute enforcement
- **COOKIES-SECURE-001**: Secure attribute for HTTPS
- **COOKIES-SAMESITE-001**: SameSite CSRF protection

### JWT Security (4 Cards)
- **JWT-SIG-001**: Signature verification requirements
- **JWT-ALG-001**: Algorithm validation controls
- **JWT-KEY-001**: Key management security
- **JWT-EXP-001**: Expiration claim validation

### GenAI Security (3 Cards)
- **GENAI-PROMPT-001**: Prompt injection prevention
- **GENAI-DATA-001**: Data exposure protection
- **GENAI-MODEL-001**: Model access security

### Container Security (1 Card)
- **DOCKER-USER-001**: Container user privilege controls

## Standards Compliance

### Coverage Statistics
- **Total Rule Cards**: 15
- **Security Domains**: 5
- **CWE References**: 30 unique mappings
- **ASVS Controls**: 28 unique references
- **Severity Distribution**:
  - Critical: 7 cards
  - High: 7 cards  
  - Medium: 1 card

### Referenced Standards
- **CWE**: Common Weakness Enumeration
- **ASVS**: Application Security Verification Standard
- **OWASP**: Top 10 and specialized guides
- **NIST**: Cybersecurity Framework and Privacy Framework
- **RFC**: Internet standards for JWT, cookies, etc.
- **ISO/IEC**: Information security standards

## Scanner Integration

### Supported Tools
- **Semgrep**: Static analysis with custom rules
- **TruffleHog**: Secrets detection and scanning
- **CodeQL**: Semantic code analysis
- **Custom**: Domain-specific detection logic

### Rule Validation
All rule cards have been validated for:
- ✅ YAML syntax correctness
- ✅ Required field completeness  
- ✅ Standards reference accuracy
- ✅ Detection tool compatibility

## Usage Examples

### Policy Enforcement
```bash
# Validate hardcoded secrets
semgrep --config=secrets/ /path/to/code

# Check JWT implementation
semgrep --config=jwt/ /path/to/jwt-code

# Scan for cookie security issues
semgrep --config=cookies/ /path/to/web-app
```

### Compliance Reporting
```python
# Generate compliance report
from rule_cards import load_rules, generate_compliance_report

rules = load_rules('app/rule_cards/')
report = generate_compliance_report(rules, scan_results)
```

## Development Guidelines

### Adding New Rule Cards
1. Follow the standardized YAML schema
2. Include comprehensive CWE/ASVS mappings
3. Provide scanner tool integration
4. Add verification test cases
5. Validate syntax and structure

### Naming Conventions
- **Card ID**: `DOMAIN-TOPIC-###` (e.g., `JWT-SIG-001`)
- **File Name**: Match card ID with `.yml` extension
- **Directory**: Organize by security domain

## Quality Assurance

All rule cards undergo validation for:
- Schema compliance and structure
- Security standards accuracy
- Scanner tool compatibility  
- Verification test completeness
- Documentation completeness

## Integration with OWASP & ASVS Corpus

These rule cards are automatically enhanced by the OWASP & ASVS semantic search corpus, creating a comprehensive security knowledge base for Claude Code CLI.

### Corpus Integration Points

**1. Rule Card Generation:**
- OWASP CheatSheets are processed to create additional rule cards
- ASVS standards provide verification requirements for existing cards
- Semantic relationships link related security concepts across standards

**2. Real-Time Search Integration:**
```bash
# Rule cards trigger corpus searches for additional context
JWT-SIG-001 → make semsearch q="JWT signature verification OWASP"
SECRETS-API-001 → make semsearch q="API key security management"
DOCKER-USER-001 → make semsearch q="container privilege escalation"
```

**3. Enhanced Guidance:**
Each rule card now references:
- **OWASP CheatSheet sections**: Specific implementation guidance
- **ASVS verification requirements**: Testing and validation criteria
- **Related security concepts**: Semantic connections to broader security topics

### Development Integration

These rule cards integrate with:
- **Claude Code CLI** for real-time security analysis during development
- **Semantic Search** for contextual security guidance (119 OWASP + 17 ASVS documents)
- **CI/CD pipelines** for automated security scanning
- **Security dashboards** for compliance reporting  
- **Developer tools** for real-time security feedback
- **Policy engines** for enforcement automation
- **Audit systems** for compliance tracking

## Contributing

When contributing new rule cards:
1. Research authoritative security standards
2. Follow the established schema exactly
3. Include comprehensive scanner integration
4. Provide detailed verification tests
5. Validate all references and mappings

