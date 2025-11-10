---
name: authentication-security
description: Use me for login flow reviews, password hashing checks (bcrypt/Argon2id), MFA enforcement, OAuth/JWT validation, session token handling, password reset security, and credential management. I return ASVS-mapped findings with rule IDs and secure code examples.
version: 1.0.0
domains:
  - user-authentication
  - multi-factor-authentication
  - password-security
  - credential-management
allowed-tools: Read, Grep, Bash
---

# Authentication Security Skill

**Complete Security Rules**: [rules.json](./rules.json) | 49 ASVS-aligned authentication rules with detection patterns

## Activation Triggers

**I respond to these queries and tasks**:
- Review login flows / authentication mechanisms
- Password hashing analysis (MD5/SHA1/bcrypt/Argon2id)
- MFA implementation verification
- OAuth2 / JWT / session token security
- Password reset flow review
- Credential storage and transmission
- Account enumeration prevention
- Brute force protection
- SSO / federated authentication

**Manual activation**:
- `/authentication-security` - Load this skill
- "use authentication-security skill" - Explicit load request
- "use authentication-specialist agent" - Call agent variant

---

## Skill Overview

You are equipped with 49 ASVS-aligned authentication security rules covering login mechanisms, multi-factor authentication, password policies, and credential management. This skill returns findings with ASVS references, CWE mappings, and secure code examples.

## Skill Capabilities

This skill enables you to:

1. **Analyze Authentication Systems** - Review login flows, session establishment, and credential handling
2. **Validate MFA Implementation** - Verify multi-factor authentication mechanisms and token validation
3. **Enforce Password Policies** - Check password complexity, hashing algorithms, and rotation policies
4. **Secure Credential Management** - Assess credential storage, transmission, and lifecycle management

## Security Knowledge Base

### Authentication Domains

**User Authentication (15 rules)**
- Login mechanism security (username/password, SSO, OAuth)
- Session establishment and initial authentication
- Account enumeration prevention
- Brute force protection

**Multi-Factor Authentication (12 rules)**
- MFA implementation patterns (TOTP, SMS, hardware tokens)
- Backup authentication methods
- MFA bypass prevention
- Token validation and replay protection

**Password Security (10 rules)**
- Password hashing algorithms (bcrypt, Argon2, PBKDF2)
- Password complexity requirements
- Password rotation policies
- Password reset security

**Credential Management (8 rules)**
- Credential storage security
- Credential transmission protection
- Service account management
- Credential rotation and lifecycle

## Rule Set Structure

Each security rule in this skill includes:

```yaml
id: AUTH-{CATEGORY}-{SUBCATEGORY}-{NUMBER}
title: Human-readable description
requirement: Specific security requirement
severity: critical|high|medium|low
scope: web-application|api|mobile|infrastructure
do: List of required security controls
dont: List of prohibited patterns
verify: Detection and validation methods
  semgrep: Semgrep rule IDs
  codeql: CodeQL query names
  manual: Manual verification steps
refs:
  asvs: ASVS requirement IDs
  cwe: CWE weakness IDs
  owasp: OWASP Top 10 references
  nist: NIST control references
```

## Usage Patterns

### When to Activate This Skill

This skill should be activated when working with:
- Login and authentication flows
- User credential handling
- Session management and establishment
- MFA implementation
- Password reset functionality
- Account recovery mechanisms
- OAuth/OpenID Connect integration
- API authentication (API keys, bearer tokens)

### Integration with Claude Code

**Single Analysis:**
```
Analyze the authentication system in src/auth/ using authentication-security skill
```

**Parallel Analysis with Multiple Skills:**
```
Analyze src/auth/ using authentication-security and session-management skills in parallel
```

**Validation Hook:**
```
Before committing changes to src/auth/, validate against authentication-security rules
```

## Analysis Approach

When this skill is activated, follow this process:

### 1. Load Security Rules
```bash
# Rule set available in compiled JSON format
cat .claude/skills/authentication-security/rules.json
```

### 2. Pattern Detection

Use automated detection tools:
- **Semgrep**: `semgrep --config=.semgrep/authentication.yml`
- **CodeQL**: Available queries for authentication vulnerabilities
- **Manual**: Code review patterns for authentication flows

### 3. Rule Application

Match detected patterns against rule categories:
- `AUTH-LOGIN-*` - Login mechanism rules
- `AUTH-MFA-*` - Multi-factor authentication rules
- `AUTH-PASSWORD-*` - Password security rules
- `AUTH-CREDENTIAL-*` - Credential management rules
- `AUTH-SESSION-*` - Session establishment rules

### 4. Guidance Generation

Provide actionable recommendations:
1. **Issue Identification** - Specific security violation with rule ID
2. **Impact Assessment** - Severity and potential exploitation
3. **Remediation Guidance** - Step-by-step fix with code examples
4. **Compliance Mapping** - ASVS, CWE, OWASP references

## Examples

### Example 1: Weak Password Hashing Detection

**Detected Pattern:**
```python
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()
```

**Rule Applied:** `AUTH-PASSWORD-HASH-001`
- **Severity:** Critical
- **Issue:** MD5 is cryptographically broken for password hashing
- **Violation:** CWE-327 (Use of Broken Cryptographic Algorithm)
- **ASVS:** V2.4.1 (Password hashing must use approved algorithm)

**Remediation:**
```python
import bcrypt

# Secure password hashing
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))

# Verification
bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash)
```

### Example 2: Missing MFA Implementation

**Detected Pattern:**
```python
if username == user.username and password_matches:
    session['user_id'] = user.id
    return redirect('/dashboard')
```

**Rule Applied:** `AUTH-MFA-ENFORCE-001`
- **Severity:** High
- **Issue:** Critical authentication path lacks MFA
- **Violation:** ASVS V2.8.1 (MFA required for administrative access)

**Remediation:**
```python
if username == user.username and password_matches:
    if user.requires_mfa:
        session['pending_mfa_user_id'] = user.id
        return redirect('/mfa-verify')
    else:
        session['user_id'] = user.id
        return redirect('/dashboard')
```

## Integration with Other Skills

This skill works in conjunction with:

- **session-management** - For post-authentication session handling
- **secrets-management** - For credential storage and protection
- **input-validation** - For authentication input sanitization
- **logging-security** - For authentication event logging
- **authorization-security** - For post-authentication access control

## Progressive Disclosure

For basic authentication analysis, this overview provides sufficient context. For deeper analysis:

1. **Load Full Rule Set**: Access `rules.json` for complete rule definitions
2. **Reference Detection Patterns**: See `detection-patterns.md` for Semgrep/CodeQL rules
3. **Review Code Examples**: Check `examples/` directory for secure implementations
4. **Consult Standards**: Reference ASVS, OWASP, and NIST documentation

## Skill Invocation

**Direct Invocation (Single Task):**
```
Task: Review authentication in src/auth/login.py
Skill: authentication-security
Expected Output: Security findings with rule IDs and remediation
```

**Parallel Invocation (Multiple Skills):**
```
Task: Comprehensive security review of authentication system
Skills: [authentication-security, session-management, secrets-management]
Mode: Parallel execution
Expected Output: Consolidated security report from all three perspectives
```

## Validation and Testing

After applying this skill's recommendations:

1. **Security Tests**: Run authentication security test suite
2. **Semgrep Validation**: `semgrep --config=.semgrep/authentication.yml src/`
3. **Manual Review**: Verify critical authentication flows
4. **Compliance Check**: Map findings to ASVS requirements

## Continuous Improvement

This skill is maintained through:
- Regular updates to rule set based on new vulnerabilities
- Integration of latest ASVS requirements
- Community feedback and real-world findings
- Automated testing of detection patterns

---

**Skill Metadata:**
- **Rule Count:** 45 authentication security rules
- **Standards Coverage:** ASVS v4.0, OWASP Top 10 2021, CWE Top 25
- **Detection Tools:** Semgrep (18 rules), CodeQL (7 queries), Manual patterns
- **Last Updated:** 2025-09-04
- **Maintainer:** GenAI Security Agents Project
