---
name: jwt-security
description: Use me for JWT token validation, signature verification, algorithm security (preventing 'none' algorithm attacks), key management, expiration handling, and JWT best practices. I return ASVS-mapped findings with rule IDs and secure code examples.
---

# JWT Security Skill

**I provide JWT (JSON Web Token) security guidance following ASVS, OWASP, and CWE standards.**

## Activation Triggers

**I respond to these queries and tasks**:
- JWT signature verification and validation
- JWT algorithm security (preventing 'none' algorithm attacks)
- JWT key management and rotation
- JWT expiration and claims validation
- JWT token generation with secure algorithms
- JWT library security configuration
- Preventing JWT signature bypass vulnerabilities
- JWT header validation (alg, typ fields)

**Manual activation**: Use `/jwt-security` or mention "JWT security review"

**Agent variant**: For parallel analysis with other security checks, use the `jwt-specialist` agent via the Task tool

## Security Knowledge Base

**JWT Signature Verification (JWT-SIG-001)**
- Always verify JWT signature before accessing claims
- Use strong cryptographic algorithms (RS256, ES256)
- Validate header algorithm matches expected signing algorithm
- Never accept 'none' algorithm in production
- Use well-established JWT libraries with security updates
- Log signature verification failures for monitoring

**JWT Algorithm Validation (JWT-ALG-001)**
- Explicitly whitelist allowed signing algorithms
- Reject tokens with 'none', 'HS256' with weak keys, or unexpected algorithms
- Prevent algorithm confusion attacks (RS256 vs HS256)
- Validate alg header against expected value
- Use asymmetric algorithms (RS256, ES256) for public APIs

**JWT Key Management (JWT-KEY-001)**
- Store signing keys securely (KMS, vault, secrets manager)
- Use separate keys for signing vs verification
- Implement key rotation policies
- Never hardcode JWT signing secrets in code
- Use sufficiently long keys (>=256 bits for HS256, >=2048 bits for RS256)
- Protect private keys with appropriate access controls

**JWT Expiration Handling (JWT-EXP-001)**
- Always set expiration (exp claim) on generated tokens
- Validate exp claim before accepting tokens
- Use short expiration times (minutes to hours, not days)
- Implement token refresh mechanism for long-lived sessions
- Check nbf (not before) claim if present
- Validate iat (issued at) claim for token age

## Common Vulnerabilities

| Vulnerability | Severity | CWE | OWASP Top 10 |
|--------------|----------|-----|--------------|
| JWT signature not verified | **CRITICAL** | CWE-347 | A02:2021 Cryptographic Failures |
| 'none' algorithm accepted | **CRITICAL** | CWE-347 | A02:2021 Cryptographic Failures |
| Weak signing keys | **HIGH** | CWE-326 | A02:2021 Cryptographic Failures |
| Missing expiration validation | **HIGH** | CWE-613 | A07:2021 Identification and Authentication Failures |
| Algorithm confusion (RS256→HS256) | **HIGH** | CWE-347 | A02:2021 Cryptographic Failures |
| Hardcoded JWT secrets | **HIGH** | CWE-798 | A02:2021 Cryptographic Failures |

## Detection Patterns

**I scan for these security issues**:

### JWT Signature Bypass
```python
# ❌ VULNERABLE: No signature verification
import jwt
token = request.headers.get('Authorization').split()[1]
claims = jwt.decode(token, options={"verify_signature": False})  # Dangerous!
user_id = claims['user_id']

# ❌ VULNERABLE: Accepting 'none' algorithm
jwt.decode(token, algorithms=['none', 'HS256'])  # Allows unsigned tokens

# ✅ SECURE: Always verify signature
import jwt
from app.config import JWT_PUBLIC_KEY, ALLOWED_ALGORITHMS

token = request.headers.get('Authorization').split()[1]
try:
    claims = jwt.decode(
        token,
        JWT_PUBLIC_KEY,
        algorithms=ALLOWED_ALGORITHMS,  # ['RS256', 'ES256']
        options={"verify_signature": True}
    )
    user_id = claims['user_id']
except jwt.InvalidSignatureError:
    return {"error": "Invalid token signature"}, 401
except jwt.ExpiredSignatureError:
    return {"error": "Token expired"}, 401
```

### Algorithm Confusion Prevention
```javascript
// ❌ VULNERABLE: Accepts any algorithm
const jwt = require('jsonwebtoken');
const decoded = jwt.verify(token, publicKey);  // Algorithm from token header!

// ❌ VULNERABLE: Allows algorithm downgrade
jwt.verify(token, publicKey, { algorithms: ['HS256', 'RS256'] });

// ✅ SECURE: Explicitly specify expected algorithm
const jwt = require('jsonwebtoken');
const decoded = jwt.verify(token, publicKey, {
  algorithms: ['RS256'],  // Only allow RS256
  issuer: 'https://auth.example.com',
  audience: 'api.example.com'
});
```

### Secure Key Management
```python
# ❌ VULNERABLE: Hardcoded secret
SECRET_KEY = "my-secret-key-12345"
token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

# ❌ VULNERABLE: Weak key
SECRET_KEY = os.getenv('JWT_SECRET')  # Only 16 characters
token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

# ✅ SECURE: KMS/Vault with strong key
import os
from cryptography.hazmat.primitives import serialization
from google.cloud import kms

# Load private key from KMS
kms_client = kms.KeyManagementServiceClient()
key_name = os.getenv('JWT_SIGNING_KEY_ID')
response = kms_client.get_public_key(request={'name': key_name})
private_key = serialization.load_pem_private_key(
    response.pem.encode('utf-8'),
    password=None
)

# Generate JWT with strong algorithm
payload = {
    'user_id': user.id,
    'exp': datetime.utcnow() + timedelta(minutes=15),
    'iat': datetime.utcnow(),
    'iss': 'https://auth.example.com',
    'aud': 'api.example.com'
}
token = jwt.encode(payload, private_key, algorithm='RS256')
```

### Expiration Validation
```java
// ❌ VULNERABLE: No expiration set
Map<String, Object> claims = new HashMap<>();
claims.put("user_id", userId);
String token = Jwts.builder()
    .setClaims(claims)
    .signWith(SignatureAlgorithm.HS256, secretKey)
    .compact();

// ❌ VULNERABLE: Not validating expiration
Claims claims = Jwts.parser()
    .setSigningKey(secretKey)
    .parseClaimsJws(token)
    .getBody();  // No exp check!

// ✅ SECURE: Set and validate expiration
import io.jsonwebtoken.*;
import java.time.Instant;
import java.time.temporal.ChronoUnit;

// Generate token with expiration
String token = Jwts.builder()
    .setSubject(userId)
    .setIssuedAt(Date.from(Instant.now()))
    .setExpiration(Date.from(Instant.now().plus(15, ChronoUnit.MINUTES)))
    .setIssuer("https://auth.example.com")
    .setAudience("api.example.com")
    .signWith(SignatureAlgorithm.RS256, privateKey)
    .compact();

// Validate token with all checks
try {
    Claims claims = Jwts.parser()
        .setSigningKey(publicKey)
        .requireIssuer("https://auth.example.com")
        .requireAudience("api.example.com")
        .parseClaimsJws(token)
        .getBody();  // Auto-validates exp, nbf, iat
    String userId = claims.getSubject();
} catch (ExpiredJwtException e) {
    throw new UnauthorizedException("Token expired");
} catch (JwtException e) {
    throw new UnauthorizedException("Invalid token");
}
```

## Integration with Agents

**For comprehensive security analysis, use parallel agents**:

```javascript
// Example: Review authentication system with JWT
use the .claude/agents/jwt-specialist.md agent to validate JWT implementation
use the .claude/agents/authentication-specialist.md agent to review login flow
use the .claude/agents/session-management-specialist.md agent to check session handling
```

## Progressive Disclosure

**This overview provides the essentials. For deeper analysis, I can provide**:
- JWT library-specific secure configurations (jsonwebtoken, pyjwt, jjwt)
- JWT refresh token patterns and security
- JWT claims validation best practices
- JWT key rotation implementation strategies
- JWT testing and validation scripts
- Language-specific JWT security examples
- Common JWT vulnerabilities and exploits

**Security Rules**: See [rules.json](./rules.json) for complete ASVS-aligned rule specifications

---

**Related Skills**: [authentication-security](../authentication-security/SKILL.md), [session-management](../session-management/SKILL.md), [cryptography](../cryptography/SKILL.md)

**Standards Compliance**: ASVS V3.1, V3.5 | OWASP Top 10 2021: A02, A07 | CWE-347, CWE-326, CWE-613
