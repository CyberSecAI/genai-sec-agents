---
name: cryptography
description: Use me for cryptographic security reviews covering weak algorithms (MD5, SHA1), strong cryptography (AES-256, RSA-2048+), random number generation, key management, password hashing (bcrypt, Argon2), and cryptographic best practices. I return ASVS-mapped findings with rule IDs and secure code examples.
---

# Cryptography Skill

**I provide cryptographic security guidance following ASVS, OWASP, NIST, and CWE standards.**

## Activation Triggers

**I respond to these queries and tasks**:
- Weak cryptographic algorithm detection (MD5, SHA1, DES, 3DES)
- Strong cryptography recommendations (AES-256, RSA-2048+, SHA-256+)
- Cryptographically secure random number generation
- Password hashing best practices (bcrypt, Argon2, PBKDF2)
- Encryption key management and rotation
- Digital signature validation
- TLS/SSL certificate validation
- Symmetric vs asymmetric encryption selection

**Manual activation**: Use `/cryptography` or mention "cryptography review"

**Agent variant**: For parallel analysis with other security checks, use the `cryptography-specialist` agent via the Task tool

## Security Knowledge Base

### Weak Algorithm Detection (3 rules)
- Never use MD5 or SHA1 for security purposes (collisions found)
- Avoid DES, 3DES, RC4 (deprecated, weak)
- Don't use ECB mode (pattern-revealing)
- Replace weak algorithms with modern alternatives
- Use at least SHA-256 for hashing
- Use AES-256-GCM or ChaCha20-Poly1305 for encryption

### Strong Cryptography (2 rules)
- Use AES-256-GCM for symmetric encryption
- Use RSA-2048+ or ECDSA P-256+ for asymmetric
- Implement authenticated encryption (GCM, CCM)
- Use perfect forward secrecy (PFS) for TLS
- Follow NIST/FIPS recommendations

### Random Number Generation (1 rule)
- Use cryptographically secure PRNG (CSPRNG)
- Never use Math.random(), rand(), or time-based seeds for security
- Use /dev/urandom, crypto.randomBytes(), SecureRandom
- Generate sufficient entropy for keys and tokens

### Password Hashing (2 rules)
- Use bcrypt, Argon2, or PBKDF2 with high iteration count
- Never use unsalted hashes or fast algorithms (MD5, SHA-256)
- Use unique salt per password
- Configure appropriate work factor (cost parameter)
- Consider memory-hard functions (Argon2) for resistance to GPU attacks

## Common Vulnerabilities

| Vulnerability | Severity | CWE | OWASP Top 10 |
|--------------|----------|-----|--------------|
| MD5 or SHA1 usage | **HIGH** | CWE-327 | A02:2021 Cryptographic Failures |
| Weak encryption (DES, 3DES) | **HIGH** | CWE-326 | A02:2021 Cryptographic Failures |
| Insecure random number generation | **HIGH** | CWE-338 | A02:2021 Cryptographic Failures |
| Weak password hashing (MD5, unsalted) | **CRITICAL** | CWE-916 | A02:2021 Cryptographic Failures |
| ECB mode encryption | **MEDIUM** | CWE-327 | A02:2021 Cryptographic Failures |
| Hardcoded cryptographic keys | **CRITICAL** | CWE-321 | A02:2021 Cryptographic Failures |
| Insufficient key length (RSA-1024) | **MEDIUM** | CWE-326 | A02:2021 Cryptographic Failures |

## Detection Patterns

**I scan for these security issues**:

### Weak Hashing Algorithms
```python
# ❌ VULNERABLE: MD5 usage
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()  # WEAK!

# ❌ VULNERABLE: SHA1 usage
import hashlib
hash_value = hashlib.sha1(data).hexdigest()  # Collisions found!

# ❌ VULNERABLE: Unsalted SHA-256 for passwords
password_hash = hashlib.sha256(password.encode()).hexdigest()  # Too fast!

# ✅ SECURE: SHA-256 for non-security purposes (checksums, IDs)
import hashlib
file_checksum = hashlib.sha256(file_data).hexdigest()  # OK for integrity
rule_id = hashlib.sha256(rule_content.encode()).hexdigest()  # OK for IDs

# ✅ SECURE: bcrypt for password hashing
import bcrypt

def hash_password(password: str) -> str:
    """Hash password with bcrypt (work factor 12)"""
    salt = bcrypt.gensalt(rounds=12)  # Cost factor
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hash_value: str) -> bool:
    """Verify password against bcrypt hash"""
    return bcrypt.checkpw(password.encode(), hash_value.encode())

# ✅ SECURE: Argon2 for password hashing (best choice)
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher(
    time_cost=3,  # Number of iterations
    memory_cost=65536,  # Memory usage in KB (64MB)
    parallelism=4,  # Number of parallel threads
    hash_len=32,  # Length of hash in bytes
    salt_len=16  # Length of salt in bytes
)

def hash_password_argon2(password: str) -> str:
    return ph.hash(password)

def verify_password_argon2(password: str, hash_value: str) -> bool:
    try:
        ph.verify(hash_value, password)
        # Check if rehash needed (parameters changed)
        if ph.check_needs_rehash(hash_value):
            return True, hash_password_argon2(password)
        return True, None
    except VerifyMismatchError:
        return False, None
```

### Weak Encryption Algorithms
```javascript
// ❌ VULNERABLE: DES encryption
const crypto = require('crypto');
const cipher = crypto.createCipher('des', key);  // Weak algorithm!

// ❌ VULNERABLE: ECB mode (pattern-revealing)
const cipher = crypto.createCipheriv('aes-256-ecb', key, null);  // No IV, patterns!

// ❌ VULNERABLE: Weak key length
const cipher = crypto.createCipheriv('aes-128-cbc', key, iv);  // Use 256-bit

// ✅ SECURE: AES-256-GCM (authenticated encryption)
const crypto = require('crypto');

function encrypt(plaintext, key) {
  // Generate random IV (12 bytes for GCM)
  const iv = crypto.randomBytes(12);

  // Create cipher with AES-256-GCM
  const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);

  // Encrypt
  let ciphertext = cipher.update(plaintext, 'utf8', 'hex');
  ciphertext += cipher.final('hex');

  // Get authentication tag
  const authTag = cipher.getAuthTag();

  // Return IV + authTag + ciphertext (all needed for decryption)
  return {
    iv: iv.toString('hex'),
    authTag: authTag.toString('hex'),
    ciphertext: ciphertext
  };
}

function decrypt(encrypted, key) {
  // Create decipher
  const decipher = crypto.createDecipheriv(
    'aes-256-gcm',
    key,
    Buffer.from(encrypted.iv, 'hex')
  );

  // Set authentication tag
  decipher.setAuthTag(Buffer.from(encrypted.authTag, 'hex'));

  // Decrypt
  let plaintext = decipher.update(encrypted.ciphertext, 'hex', 'utf8');
  plaintext += decipher.final('utf8');

  return plaintext;
}

// Usage
const key = crypto.randomBytes(32);  // 256-bit key
const plaintext = "Sensitive data";
const encrypted = encrypt(plaintext, key);
const decrypted = decrypt(encrypted, key);
```

### Insecure Random Number Generation
```java
// ❌ VULNERABLE: Math.random() for security
String token = String.valueOf(Math.random());  // NOT cryptographically secure!

// ❌ VULNERABLE: java.util.Random for security
Random random = new Random();
int sessionId = random.nextInt();  // Predictable!

// ❌ VULNERABLE: Time-based seed
Random random = new Random(System.currentTimeMillis());  // Predictable!

// ✅ SECURE: SecureRandom for security purposes
import java.security.SecureRandom;
import java.util.Base64;

public class TokenGenerator {

    private static final SecureRandom secureRandom = new SecureRandom();

    public static String generateSecureToken(int byteLength) {
        byte[] token = new byte[byteLength];
        secureRandom.nextBytes(token);
        return Base64.getUrlEncoder().withoutPadding().encodeToString(token);
    }

    public static String generateSessionId() {
        // 256-bit session ID (32 bytes)
        return generateSecureToken(32);
    }

    public static String generateApiKey() {
        // 256-bit API key
        return generateSecureToken(32);
    }

    public static String generateCSRFToken() {
        // 128-bit CSRF token
        return generateSecureToken(16);
    }
}

// Usage
String sessionId = TokenGenerator.generateSessionId();
String apiKey = TokenGenerator.generateApiKey();
String csrfToken = TokenGenerator.generateCSRFToken();
```

### Asymmetric Encryption and Key Length
```python
# ❌ VULNERABLE: RSA-1024 (too short)
from Crypto.PublicKey import RSA
key = RSA.generate(1024)  # Insufficient key length!

# ❌ VULNERABLE: No padding or weak padding
from Crypto.Cipher import PKCS1_v1_5  # Weak padding!

# ✅ SECURE: RSA-2048+ with OAEP padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend

# Generate RSA key pair (2048-bit minimum, 4096-bit recommended)
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096,  # 4096-bit for long-term security
    backend=default_backend()
)
public_key = private_key.public_key()

# Encrypt with OAEP padding
def encrypt_rsa(plaintext: bytes, public_key) -> bytes:
    ciphertext = public_key.encrypt(
        plaintext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

# Decrypt with OAEP padding
def decrypt_rsa(ciphertext: bytes, private_key) -> bytes:
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return plaintext

# ✅ SECURE: ECDSA (Elliptic Curve) - shorter keys, equivalent security
from cryptography.hazmat.primitives.asymmetric import ec

# Generate ECDSA key pair (P-256 curve = equivalent to RSA-3072)
private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
public_key = private_key.public_key()

# Sign data
def sign_ecdsa(data: bytes, private_key) -> bytes:
    signature = private_key.sign(
        data,
        ec.ECDSA(hashes.SHA256())
    )
    return signature

# Verify signature
def verify_ecdsa(data: bytes, signature: bytes, public_key) -> bool:
    try:
        public_key.verify(
            signature,
            data,
            ec.ECDSA(hashes.SHA256())
        )
        return True
    except Exception:
        return False
```

### Key Management
```python
# ❌ VULNERABLE: Hardcoded key
AES_KEY = b'sixteen byte key'  # Hardcoded - NEVER!

# ❌ VULNERABLE: Key stored with data
with open('data.enc', 'wb') as f:
    f.write(key + encrypted_data)  # Key and data together!

# ❌ VULNERABLE: Weak key derivation
key = hashlib.md5(password.encode()).digest()  # Weak KDF!

# ✅ SECURE: Key management with KMS
import os
from google.cloud import kms
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

class KeyManager:
    def __init__(self):
        self.kms_client = kms.KeyManagementServiceClient()
        self.project_id = os.getenv('GCP_PROJECT_ID')
        self.location = 'us-central1'
        self.key_ring = 'app-keys'

    def get_encryption_key(self, key_name: str) -> bytes:
        """Get data encryption key from KMS"""
        key_path = self.kms_client.crypto_key_path(
            self.project_id,
            self.location,
            self.key_ring,
            key_name
        )

        # Use KMS to encrypt a local DEK
        # (Envelope encryption pattern)
        dek = os.urandom(32)  # Data Encryption Key (256-bit)

        # Encrypt DEK with KMS (Key Encryption Key)
        encrypt_response = self.kms_client.encrypt(
            request={'name': key_path, 'plaintext': dek}
        )

        encrypted_dek = encrypt_response.ciphertext

        return dek, encrypted_dek

    def decrypt_dek(self, encrypted_dek: bytes, key_name: str) -> bytes:
        """Decrypt DEK using KMS"""
        key_path = self.kms_client.crypto_key_path(
            self.project_id,
            self.location,
            self.key_ring,
            key_name
        )

        decrypt_response = self.kms_client.decrypt(
            request={'name': key_path, 'ciphertext': encrypted_dek}
        )

        return decrypt_response.plaintext

    def rotate_key(self, key_name: str):
        """Rotate encryption key"""
        key_path = self.kms_client.crypto_key_path(
            self.project_id,
            self.location,
            self.key_ring,
            key_name
        )

        # Create new key version
        self.kms_client.create_crypto_key_version(
            request={'parent': key_path}
        )

# ✅ SECURE: Password-based key derivation (PBKDF2)
def derive_key_from_password(password: str, salt: bytes = None) -> tuple:
    """Derive encryption key from password using PBKDF2"""
    if salt is None:
        salt = os.urandom(16)  # Generate random salt

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 256-bit key
        salt=salt,
        iterations=100_000,  # High iteration count (OWASP recommendation)
    )

    key = kdf.derive(password.encode())

    return key, salt

# Usage
password = "user_password"
key, salt = derive_key_from_password(password)
# Store salt with encrypted data (salt is not secret)
```

### Digital Signatures
```python
# ❌ VULNERABLE: No signature verification
data = receive_data()
process(data)  # Trusting unverified data!

# ❌ VULNERABLE: Weak signature algorithm
from Crypto.Signature import PKCS1_v1_5  # Deprecated!

# ✅ SECURE: RSA-PSS signature verification
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

# Generate key pair
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096
)
public_key = private_key.public_key()

def sign_data(data: bytes, private_key) -> bytes:
    """Sign data with RSA-PSS"""
    signature = private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def verify_signature(data: bytes, signature: bytes, public_key) -> bool:
    """Verify RSA-PSS signature"""
    try:
        public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception as e:
        print(f"Signature verification failed: {e}")
        return False

# Usage
data = b"Important message"
signature = sign_data(data, private_key)

# Verify before processing
if verify_signature(data, signature, public_key):
    process(data)
else:
    raise ValueError("Invalid signature - data may be tampered")
```

## Integration with Agents

**For comprehensive security analysis, use parallel agents**:

```javascript
// Example: Review cryptographic implementation
use the .claude/agents/cryptography-specialist.md agent to validate crypto usage
use the .claude/agents/secrets-specialist.md agent to check key management
use the .claude/agents/authentication-specialist.md agent to review password hashing
```

## Progressive Disclosure

**This overview provides the essentials. For deeper analysis, I can provide**:
- NIST cryptographic recommendations (FIPS 140-2/140-3)
- Post-quantum cryptography migration
- Hardware Security Module (HSM) integration
- Certificate pinning and validation
- Cryptographic library selection (OpenSSL, libsodium, cryptography.io)
- Side-channel attack prevention (timing attacks, cache attacks)
- Key rotation strategies and implementation
- Envelope encryption patterns (DEK/KEK)

**Security Rules**: See [rules.json](./rules.json) for complete ASVS-aligned rule specifications

---

**Related Skills**: [secrets-management](../secrets-management/SKILL.md), [authentication-security](../authentication-security/SKILL.md), [data-protection](../data-protection/SKILL.md)

**Standards Compliance**: ASVS V6.2, V6.3, V2.4 | OWASP Top 10 2021: A02 | NIST SP 800-175B | CWE-327, CWE-326, CWE-338, CWE-916, CWE-321
