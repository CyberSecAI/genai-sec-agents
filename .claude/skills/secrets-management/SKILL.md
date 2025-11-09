---
name: secrets-management
description: Use me for API key security reviews, hardcoded secret detection (passwords/tokens in code), database credential protection, JWT signing secret validation, cloud credential management (AWS/Azure/GCP keys), environment variable security, and secret rotation policies. I return ASVS-mapped findings with rule IDs and secure secret storage examples.
version: 1.0.0
domains:
  - api-key-security
  - credential-protection
  - secret-detection
  - key-rotation
allowed-tools: Read, Grep, Bash
---

# Secrets Management Security Skill

## Activation Triggers

**I respond to these queries and tasks**:
- Hardcoded secret detection (API keys, passwords, tokens in code)
- API key storage and transmission security
- Database credential protection (connection strings, DB passwords)
- JWT signing secret validation
- Cloud credential management (AWS access keys, Azure secrets, GCP credentials)
- Environment variable security (.env files, config management)
- Secret rotation policies and key lifecycle
- Private key handling (RSA, SSH, TLS certificates)
- Password storage in configuration files
- Secret scanning and audit

**Manual activation**:
- `/secrets-management` - Load this skill
- "use secrets-management skill" - Explicit load request
- "use secrets-specialist agent" - Call agent variant

---

## Skill Overview

You are equipped with 4 ASVS-aligned secrets management security rules covering API key security, database credential protection, hardcoded secret prevention, and secret rotation. This skill returns findings with ASVS references, CWE mappings, and secure credential storage examples.

## Skill Capabilities

This skill enables you to:

1. **Detect Hardcoded Secrets** - Scan for API keys, passwords, tokens embedded in source code
2. **Validate Credential Storage** - Review secret storage mechanisms and environment variable usage
3. **Assess Key Management** - Verify secret rotation policies and key lifecycle management
4. **Secure Cloud Credentials** - Check AWS, Azure, GCP credential handling

## Security Knowledge Base

### Secrets Management Domains

**API Key Security (SECRETS-API-001)**
- API key storage in environment variables vs hardcoded
- API key transmission security (HTTPS only)
- API key rotation and revocation
- Scope limitation for API keys

**JWT Signing Secrets (SECRETS-JWT-001)**
- JWT signing key strength (minimum 256 bits for HS256)
- Hardcoded JWT secrets detection
- Secret rotation for JWT signing keys
- Secure key storage for JWT validation

**Cloud Credentials (SECRETS-CLOUD-001)**
- AWS access key / secret key protection
- Azure service principal credential management
- GCP service account key security
- IAM role usage vs hardcoded credentials

**Database Credentials (SECRET-002)**
- Connection string security (no embedded passwords)
- Database credential storage in secure vaults
- Credential isolation per environment
- DB password rotation policies

## Common Vulnerabilities Detected

### Critical Issues
- 🔴 **Hardcoded API Keys**: `API_KEY = "sk_live_..."` in source code
- 🔴 **Hardcoded Passwords**: Database passwords in connection strings
- 🔴 **Committed Secrets**: `.env` files committed to version control
- 🔴 **Weak JWT Secrets**: Short or predictable JWT signing keys

### High Severity
- 🟠 **No Secret Rotation**: Credentials never rotated
- 🟠 **Plaintext Secrets**: Secrets in plaintext config files
- 🟠 **Overly Permissive Keys**: API keys with excessive scopes

## Security Standards Coverage

**ASVS Alignment**:
- V6.4.1: Secrets and credentials are not hardcoded
- V6.4.2: Cryptographic secrets are managed securely
- V14.1.3: Build processes do not include sensitive information

**CWE Mapping**:
- CWE-798: Use of Hard-coded Credentials
- CWE-259: Use of Hard-coded Password
- CWE-321: Use of Hard-coded Cryptographic Key
- CWE-522: Insufficiently Protected Credentials

**OWASP Top 10**:
- A02:2021 Cryptographic Failures
- A05:2021 Security Misconfiguration
- A07:2021 Identification and Authentication Failures

## Detection Patterns

**Automatically scans for**:
```python
# ❌ CRITICAL: Hardcoded API key
API_KEY = "sk_live_1234567890abcdef"
api_secret = "secret_key_here"

# ❌ CRITICAL: Hardcoded database password
db_url = "postgresql://user:password123@localhost/db"

# ❌ CRITICAL: JWT secret in code
jwt.encode(payload, "my_secret_key", algorithm="HS256")

# ❌ HIGH: AWS credentials in code
aws_access_key = "AKIAIOSFODNN7EXAMPLE"
```

## Secure Patterns

**✅ Use Environment Variables**:
```python
import os

# ✅ SECURE: Load from environment
API_KEY = os.environ.get('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY environment variable required")

DB_PASSWORD = os.getenv('DB_PASSWORD')
JWT_SECRET = os.getenv('JWT_SECRET_KEY')
```

**✅ Use Secret Management Services**:
```python
# ✅ SECURE: AWS Secrets Manager
import boto3
secrets_client = boto3.client('secretsmanager')
response = secrets_client.get_secret_value(SecretId='prod/api_key')
API_KEY = json.loads(response['SecretString'])['api_key']

# ✅ SECURE: HashiCorp Vault
import hvac
client = hvac.Client(url='http://vault:8200')
secret = client.secrets.kv.v2.read_secret_version(path='api_keys')
API_KEY = secret['data']['data']['key']
```

**✅ Minimum Secret Strength**:
```python
import secrets

# ✅ SECURE: Generate cryptographically strong JWT secret
JWT_SECRET = secrets.token_urlsafe(32)  # 256 bits minimum

# ✅ SECURE: Generate strong API key
API_KEY = secrets.token_hex(32)
```

## Progressive Disclosure

This skill uses staged loading:

1. **Initial Load** (~2k tokens): Skill overview and common patterns
2. **On Demand** (~1k tokens): Specific rule details when vulnerabilities detected
3. **Deep Dive** (~1k tokens): Full remediation guidance for critical issues

Total: ~4k tokens maximum (only loads what's needed)

## Usage Examples

### Example 1: Hardcoded Secret Detection
```
User: "Review this code for security issues"
[Code with API_KEY = "sk_live_..."]

Skill Response:
🔴 CRITICAL: Hardcoded API key detected (SECRETS-API-001)
- Line 5: API_KEY = "sk_live_..."
- ASVS: V6.4.1 (Secrets not hardcoded)
- CWE-798: Use of Hard-coded Credentials
- Fix: Load from environment variable
[Provides secure code example]
```

### Example 2: JWT Secret Validation
```
User: "Is this JWT implementation secure?"
[Code with jwt.encode(payload, "secret", algorithm="HS256")]

Skill Response:
🔴 CRITICAL: Weak JWT signing secret (SECRETS-JWT-001)
- Hardcoded secret detected
- Secret too short (48 bits < 256 bits minimum)
- ASVS: V6.4.2 (Cryptographic secrets managed securely)
- Fix: Use environment variable with ≥256-bit secret
[Provides secure implementation]
```

### Example 3: Database Credential Review
```
User: "Check database connection security"
[Code with connection string containing password]

Skill Response:
🔴 CRITICAL: Hardcoded database credentials (SECRET-002)
- Connection string contains plaintext password
- CWE-522: Insufficiently Protected Credentials
- Fix: Use environment variables or secret vault
[Provides secure connection pattern]
```

## Integration with Agents

**Agent Variant**: Use `secrets-specialist` agent for:
- Automated secret scanning across codebase
- TruffleHog integration for secret detection
- Semgrep rule execution for credential patterns
- Batch analysis of multiple files

**Skill Variant (this)**: Use for:
- Interactive code review with explanations
- Learning secure secret management patterns
- Understanding ASVS requirements
- Rich examples and remediation guidance

## Tools Available

- **Grep**: Search for hardcoded secret patterns
- **Read**: Analyze specific files for credentials
- **Bash**: Execute security scanning tools (when available)

## References

**Security Rules**: 4 compiled rules in `json/secrets_rules.json`

**Standards**:
- ASVS 4.0: V6.4 (Secret Management), V14.1 (Build Process)
- OWASP CheatSheet: Secrets Management
- NIST SP 800-57: Key Management

**Tools Compatibility**:
- TruffleHog: Secret scanning
- Semgrep: Credential detection rules
- git-secrets: Pre-commit secret prevention

---

**Remember**: Secrets in code = instant critical vulnerability. Always use environment variables or secret management services. Never commit secrets to version control.
