# Sample Code for Skills Validation Testing

**Purpose**: Provide realistic code samples for testing authentication-security skill activation and detection capabilities.

**DO NOT USE VULNERABLE CODE IN PRODUCTION**

---

## Files

### vulnerable_login.py

**Intentionally insecure** login implementation containing 15+ security vulnerabilities.

**Use for**:
- Test A1: "Review `.claude/skills/validation/sample_code/vulnerable_login.py` for security issues"
- Test A7: "Review the `authenticate_user()` function in `.claude/skills/validation/sample_code/vulnerable_login.py`"

**Expected behavior when authentication-security skill activates**:
- Detects MD5 password hashing (should recommend bcrypt/argon2)
- Detects SQL injection via string concatenation (should recommend parameterized queries)
- Detects hardcoded secrets (should recommend environment variables)
- Detects missing rate limiting (should recommend ASVS 2.2.1 controls)
- Detects no account lockout (should recommend ASVS 2.2.1 lockout mechanism)
- Detects session fixation vulnerability (should recommend session regeneration)
- Detects weak session ID generation (should recommend secrets.token_urlsafe)
- Detects missing MFA support (should recommend ASVS 2.7.x TOTP/OTP)
- Detects timing attack vulnerability (should recommend constant-time comparison)
- Detects information disclosure in error messages (should recommend generic errors)

**Vulnerabilities by ASVS category**:
- **2.1.x Password Requirements**: No complexity checks, 6-char minimum (too short)
- **2.2.x Authentication Controls**: No rate limiting, no account lockout
- **2.4.x Credential Storage**: MD5 hashing (broken crypto)
- **2.7.x Multi-Factor**: No MFA support
- **2.8.x Authenticator Lifecycle**: No TOTP/OTP implementation
- **3.2.x Session Binding**: Session fixation, no regeneration
- **3.3.x Session Timeout**: No session expiration
- **3.4.x Cookie Security**: No Secure/HttpOnly flags
- **5.1.x Input Validation**: SQL injection via concatenation
- **6.2.x Crypto**: MD5 usage (weak algorithm)
- **8.3.x Sensitive Data**: Hardcoded secrets
- **14.1.x Build**: Debug mode enabled

---

### secure_login.py

**Production-ready** login implementation following ASVS 4.0 authentication requirements.

**Use for**:
- Reference implementation for secure patterns
- Comparison with vulnerable_login.py
- Understanding what authentication-security skill should recommend

**Security features implemented**:

#### ASVS 2.x Authentication
- **2.1.1**: Password length 8-128 characters
- **2.1.7**: Password complexity validation, common password check
- **2.1.12**: Session invalidation on password change
- **2.2.1**: Rate limiting (5 attempts/minute) + Account lockout (5 fails = 15 min lockout)
- **2.2.2**: Generic error messages (no username enumeration)
- **2.4.1**: bcrypt password hashing (12 rounds)
- **2.7.1**: MFA support via TOTP
- **2.8.5**: TOTP validation with ~30 second window

#### ASVS 3.x Session Management
- **3.2.1**: Session regeneration after authentication (prevent fixation)
- **3.2.3**: Session binding to IP/User-Agent
- **3.3.1**: 30-minute session timeout
- **3.4.1**: SESSION_COOKIE_SECURE (HTTPS only)
- **3.4.2**: SESSION_COOKIE_HTTPONLY (no JavaScript access)
- **3.4.3**: SESSION_COOKIE_SAMESITE (CSRF protection)

#### ASVS 5.x Input Validation
- **5.1.1**: Parameterized SQL queries (prevent injection)
- **5.1.3**: Input length validation

#### ASVS 6.x Cryptography
- **6.2.1**: bcrypt (approved algorithm for password hashing)
- **6.3.1**: secrets.token_urlsafe() for session IDs (cryptographically secure)

#### ASVS 8.x Data Protection
- **8.3.4**: No hardcoded secrets (environment variables)

---

## Testing Workflow

### 1. Test Skill Activation with Vulnerable Code

**Prompt**:
```
Review .claude/skills/validation/sample_code/vulnerable_login.py for security issues
```

**Expected when skill activates**:
- Response references "authentication-security skill" or similar
- Cites specific ASVS requirements (2.4.1, 2.2.1, etc.)
- References CWE/OWASP mappings
- Provides specific remediation (use bcrypt, parameterized queries, etc.)
- Mentions multiple vulnerabilities (not just one)

**Expected when skill does NOT activate**:
- Generic security advice
- No ASVS references
- May miss some vulnerabilities
- Less specific remediation guidance

### 2. Compare with Secure Implementation

**Prompt**:
```
Compare .claude/skills/validation/sample_code/vulnerable_login.py with secure_login.py
and explain the security differences
```

**Expected when skill activates**:
- Maps differences to ASVS requirements
- Explains why bcrypt > MD5
- Explains why parameterized queries prevent SQL injection
- References specific rule IDs from authentication-security skill

### 3. Request Implementation Guidance

**Prompt**:
```
How should I hash user passwords in Python?
```

**Expected when skill activates**:
- Recommends bcrypt or argon2 (per ASVS 2.4.1)
- Provides code example similar to secure_login.py
- Warns against MD5, SHA1, plain SHA-256
- May reference CWE-916 (Use of Password Hash With Insufficient Computational Effort)

---

## Vulnerability Details for Validation

When testing A1 or A7, the skill should detect these specific issues:

| Line(s) | Vulnerability | ASVS Ref | Expected Detection |
|---------|--------------|----------|-------------------|
| 9 | Hardcoded secret key | 2.10.4, 8.3.4 | Yes - AUTH-CONFIGURE-SECRET-001 |
| 29 | MD5 password hashing | 2.4.1, 6.2.1 | Yes - AUTH-CRYPTO-001 |
| 33-35 | SQL injection (string concat) | 5.1.1 | Yes (input-validation domain) |
| 37-38 | Timing attack (early return) | 2.2.7 | Yes - AUTH-FACTOR-001 related |
| 22-50 | No rate limiting | 2.2.1 | Yes - AUTH-FACTOR-RATE-LIMIT-001 |
| 22-50 | No account lockout | 2.2.1 | Yes - AUTH-FACTOR-LOCKOUT-001 |
| 43-44 | Session fixation (no regen) | 3.2.1 | Yes - Session management |
| 69 | No password complexity check | 2.1.1, 2.1.7 | Yes - AUTH-ALLOW-PASSWORD-001 |
| 75 | Password min length too short (6) | 2.1.1 | Yes - AUTH-ALLOW-PASSWORD-001 |
| 79 | MD5 in reset function | 2.4.1 | Yes - AUTH-CRYPTO-001 |
| 83-84 | SQL injection in UPDATE | 5.1.1 | Yes (input-validation domain) |
| 102 | Weak random session ID | 3.2.1, 6.3.1 | Yes - SESSION-ID-001 |
| 108 | No session timeout | 3.3.1 | Yes - SESSION-TIMEOUT-001 |
| 115 | Debug mode enabled | 14.1.1 | Maybe (configuration domain) |

**Count**: 15 distinct vulnerabilities

**Minimum expected detections**: ≥10/15 when authentication-security skill is active

---

## Validation Criteria

### Skill Activation Success (A1)

✅ **PASS** if response:
- Explicitly references authentication-security skill OR loaded ASVS rules
- Detects ≥10/15 vulnerabilities
- Provides specific ASVS references (2.4.1, 2.2.1, etc.)
- Recommends correct remediation (bcrypt, parameterized queries)
- Maps issues to CWE/OWASP where relevant

🟡 **MARGINAL** if response:
- Detects 7-9/15 vulnerabilities
- Some ASVS references but not comprehensive
- Generally correct remediation but less specific

❌ **FAIL** if response:
- Detects <7/15 vulnerabilities
- No ASVS references
- Generic security advice without authentication-specific guidance
- Incorrect remediation recommendations

### Skill Precision Success (A7)

Test A7 is more focused - only `authenticate_user()` function.

Expected vulnerabilities in this function:
1. MD5 hashing
2. SQL injection
3. Timing attack
4. No rate limiting
5. No account lockout
6. Session fixation
7. No MFA support

✅ **PASS**: Detects ≥5/7 with ASVS references
🟡 **MARGINAL**: Detects 3-4/7
❌ **FAIL**: Detects <3/7

---

## Notes for Testers

- These files are **intentionally vulnerable** for testing purposes
- The vulnerable code includes inline comments marking each issue
- The secure code includes inline comments explaining security controls
- Both files use the same structure to enable side-by-side comparison
- All ASVS references are from ASVS 4.0 specification

**Do not deploy vulnerable_login.py to any environment**
