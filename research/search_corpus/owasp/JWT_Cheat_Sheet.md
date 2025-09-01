---
license: CC-BY-SA-4.0
path: owasp-cheatsheets/cheatsheets/JWT_Cheat_Sheet.md
processed_at: null
security_domains:
- input_validation
- jwt
- secrets
sha256: b80c6ba68dbc17263371d05853a038683d3d5c448c522d96040c5d659d00ea55
source: owasp-cheatsheet-series
tags:
- input_validation
- jwt
- owasp
- secrets
---

# JSON Web Token (JWT) Cheat Sheet

## Introduction

JSON Web Token (JWT) is an open standard that defines a compact and self-contained way for securely transmitting information between parties as a JSON object.

## JWT Structure

A JWT consists of three parts separated by dots (.), which are:
- Header
- Payload  
- Signature

### Header

The header typically consists of two parts: the type of the token (JWT) and the signing algorithm being used.

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

### Payload

The payload contains the claims. Claims are statements about an entity (typically, the user) and additional data.

```json
{
  "sub": "1234567890",
  "name": "John Doe",
  "iat": 1516239022
}
```

## Security Considerations

### Use Strong Secrets

Always use strong, randomly generated secrets for HMAC-based algorithms.

### Validate All Claims

Always validate:
- Signature
- Expiration time (exp)
- Not before time (nbf)
- Issuer (iss)
- Audience (aud)

### Short Expiration Times

Use short expiration times to limit the impact of token theft.

```python
# Example: Set 15-minute expiration
payload = {
    'user_id': user.id,
    'exp': datetime.utcnow() + timedelta(minutes=15)
}
```

## Implementation Guidelines

### Token Storage

- Store tokens in secure HTTP-only cookies when possible
- Avoid localStorage for sensitive tokens
- Consider secure storage mechanisms on mobile

### Token Validation

```python
def validate_jwt(token, secret):
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
```

## Common Vulnerabilities

### None Algorithm Attack

Never accept 'none' as a valid algorithm.

### Algorithm Confusion

Always specify allowed algorithms explicitly.

### Key Confusion

Ensure RSA public keys are not used as HMAC secrets.