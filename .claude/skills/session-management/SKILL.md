---
name: session-management
description: Use me for session lifecycle security reviews, session token validation, session fixation/hijacking prevention, cookie security (HttpOnly/Secure/SameSite), session timeout policies, JWT session handling, logout implementation, and concurrent session management. I return ASVS-mapped findings with rule IDs and secure session patterns.
version: 1.0.0
domains:
  - session-lifecycle
  - session-tokens
  - cookie-security
  - session-attacks
allowed-tools: Read, Grep, Bash
---

# Session Management Security Skill

## Activation Triggers

**I respond to these queries and tasks**:
- Session lifecycle management (create, validate, destroy)
- Session token generation and validation
- Session fixation prevention
- Session hijacking protection
- Cookie security (HttpOnly, Secure, SameSite flags)
- Session timeout and expiration
- JWT session token handling
- Logout and session termination
- Concurrent session management
- Session storage security (Redis, databases)
- Remember-me functionality security
- CSRF protection for sessions

**Manual activation**:
- `/session-management` - Load this skill
- "use session-management skill" - Explicit load request
- "use session-management-specialist agent" - Call agent variant

---

## Skill Overview

You are equipped with 22 ASVS-aligned session management security rules covering session lifecycle, token security, attack prevention, and cookie handling. This skill returns findings with ASVS references, CWE mappings, and secure session implementation examples.

## Security Knowledge Base

### Session Management Domains

**Session Lifecycle (8 rules)**
- Session creation with cryptographically secure IDs
- Session validation and regeneration
- Session termination and logout
- Session expiration and timeout policies

**Session Tokens (6 rules)**
- Token generation (minimum 128 bits entropy)
- Token transmission security (HTTPS only)
- Token storage (HttpOnly cookies)
- Token rotation and regeneration

**Attack Prevention (5 rules)**
- Session fixation prevention (regenerate on login)
- Session hijacking protection (bind to IP/User-Agent)
- Concurrent session limits
- Session replay prevention

**Cookie Security (3 rules)**
- HttpOnly flag (prevent XSS access)
- Secure flag (HTTPS only)
- SameSite attribute (CSRF protection)

## Common Vulnerabilities Detected

### Critical Issues
- 🔴 **Weak Session IDs**: Predictable or short session tokens
- 🔴 **Session Fixation**: No regeneration after login
- 🔴 **Missing HttpOnly**: Cookies accessible via JavaScript
- 🔴 **Missing Secure Flag**: Sessions transmitted over HTTP

### High Severity
- 🟠 **No Session Timeout**: Sessions never expire
- 🟠 **Poor Logout**: Session not destroyed on logout
- 🟠 **No CSRF Protection**: Missing SameSite/tokens

## Security Standards Coverage

**ASVS Alignment**:
- V3.2: Session Binding
- V3.3: Session Logout and Timeout
- V3.4: Cookie-based Session Management
- V3.5: Token-based Session Management
- V3.7: Defenses Against Session Management Exploits

**CWE Mapping**:
- CWE-384: Session Fixation
- CWE-613: Insufficient Session Expiration
- CWE-565: Reliance on Cookies without Validation
- CWE-311: Missing Encryption of Sensitive Data

**OWASP Top 10**:
- A07:2021 Identification and Authentication Failures
- A01:2021 Broken Access Control

## Detection Patterns

**Automatically scans for**:
```python
# ❌ CRITICAL: Weak session ID
session_id = str(random.randint(1000, 9999))

# ❌ CRITICAL: No HttpOnly flag
response.set_cookie('session_id', value, httponly=False)

# ❌ CRITICAL: Session fixation (no regeneration)
def login(username, password):
    # ... auth logic ...
    session['user_id'] = user.id  # Uses existing session!

# ❌ HIGH: No session timeout
SESSION_PERMANENT = True
PERMANENT_SESSION_LIFETIME = None  # Never expires
```

## Secure Patterns

**✅ Secure Session Creation**:
```python
import secrets
from flask import session

# ✅ SECURE: Cryptographically secure session ID
session_id = secrets.token_urlsafe(32)  # 256 bits

# ✅ SECURE: Regenerate session on login
def login(username, password):
    if verify_credentials(username, password):
        session.clear()  # Clear old session
        session.regenerate()  # New session ID
        session['user_id'] = user.id
```

**✅ Secure Cookie Configuration**:
```python
# ✅ SECURE: Proper cookie flags
response.set_cookie(
    'session_id',
    value=session_id,
    httponly=True,   # Prevent XSS access
    secure=True,     # HTTPS only
    samesite='Strict'  # CSRF protection
)

# Flask configuration
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE='Strict',
    PERMANENT_SESSION_LIFETIME=1800  # 30 minutes
)
```

**✅ Secure Logout**:
```python
# ✅ SECURE: Complete session destruction
@app.route('/logout')
def logout():
    session.clear()  # Clear session data
    response = make_response(redirect('/login'))
    response.set_cookie('session_id', '', expires=0)  # Delete cookie
    return response
```

## Progressive Disclosure

1. **Initial Load** (~2k tokens): Overview and common patterns
2. **On Demand** (~1.5k tokens): Specific vulnerability details
3. **Deep Dive** (~1.5k tokens): Full remediation guidance

Total: ~5k tokens maximum

## References

**Security Rules**: 22 compiled rules in `json/session_rules.json`

**Standards**:
- ASVS 4.0: V3 (Session Management)
- OWASP CheatSheet: Session Management
- OWASP Top 10:2021

---

**Remember**: Weak session management = account takeover. Always use cryptographically secure session IDs, regenerate on login, set proper cookie flags, and implement timeouts.
