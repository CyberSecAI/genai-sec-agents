---
name: secure-configuration
description: Use me for secure defaults, security hardening, configuration security reviews, environment variable management, TLS/SSL configuration, database security settings, and production security configuration. I return ASVS-mapped findings with rule IDs and secure code examples.
---

# Secure Configuration Skill

**I provide security configuration and hardening guidance following ASVS, OWASP, and CWE standards.**

**Complete Security Rules**: [rules.json](./rules.json) | 16 ASVS-aligned configuration security rules with detection patterns

## Activation Triggers

**I respond to these queries and tasks**:
- Secure default configuration review
- Security hardening and configuration management
- Environment variable and secrets configuration
- TLS/SSL configuration and cipher suites
- Database security configuration
- Production security settings review
- Security headers configuration
- Framework security configuration (Django, Rails, Spring Boot)
- Cloud security configuration (AWS, Azure, GCP)

**Manual activation**: Use `/secure-configuration` or mention "configuration security review"

**Agent variant**: For parallel analysis with other security checks, use the `configuration-specialist` agent via the Task tool

## Security Knowledge Base

### Secure Defaults (5 rules)
- Enable security features by default (HTTPS, HSTS, CSP)
- Disable debug mode in production
- Use secure session configuration (HttpOnly, Secure, SameSite)
- Set restrictive CORS policies
- Enable security headers by default
- Fail closed on security checks (deny by default)
- Use principle of least privilege for default permissions

### TLS/SSL Configuration (4 rules)
- Enforce TLS 1.2+ (disable SSLv3, TLS 1.0, TLS 1.1)
- Use strong cipher suites only
- Enable certificate validation
- Implement HSTS with long max-age
- Use perfect forward secrecy (PFS) ciphers
- Configure secure certificate validation

### Environment Security (3 rules)
- Separate configuration from code
- Use environment-specific configurations
- Never commit secrets to configuration files
- Validate environment variables on startup
- Use secure secret management (KMS, Vault)
- Fail fast on missing critical config

### Production Hardening (4 rules)
- Disable debug endpoints and stack traces
- Remove development tools and debug libraries
- Configure appropriate timeouts
- Enable security monitoring and logging
- Restrict administrative interfaces
- Use security scanning in CI/CD

## Common Vulnerabilities

| Vulnerability | Severity | CWE | OWASP Top 10 |
|--------------|----------|-----|--------------|
| Debug mode enabled in production | **HIGH** | CWE-489 | A05:2021 Security Misconfiguration |
| Weak TLS configuration (SSLv3, TLS 1.0) | **HIGH** | CWE-326 | A02:2021 Cryptographic Failures |
| Missing security headers | **MEDIUM** | CWE-16 | A05:2021 Security Misconfiguration |
| Insecure CORS configuration | **MEDIUM** | CWE-942 | A05:2021 Security Misconfiguration |
| Default credentials | **CRITICAL** | CWE-798 | A07:2021 Identification Failures |
| Certificate validation disabled | **CRITICAL** | CWE-295 | A02:2021 Cryptographic Failures |

## Detection Patterns

**I scan for these security issues**:

### Debug Mode in Production
```python
# ❌ VULNERABLE: Debug enabled
# Django settings.py
DEBUG = True  # NEVER in production!
ALLOWED_HOSTS = ['*']  # Too permissive

# ❌ VULNERABLE: Exposing stack traces
app = Flask(__name__)
app.config['DEBUG'] = True  # Shows stack traces to users

# ✅ SECURE: Production-safe configuration
import os

# Django settings.py
DEBUG = os.getenv('DEBUG', 'False') == 'True'  # Default to False
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

if not ALLOWED_HOSTS:
    raise ValueError("ALLOWED_HOSTS must be set in production")

# Secure session settings
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Strict'  # CSRF protection
CSRF_COOKIE_SECURE = True

# Security headers
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Flask production configuration
app = Flask(__name__)
app.config.from_object('config.ProductionConfig')

if app.config['DEBUG']:
    raise RuntimeError("DEBUG must be False in production")
```

### TLS/SSL Configuration
```javascript
// ❌ VULNERABLE: Weak TLS configuration
const https = require('https');
const fs = require('fs');

const options = {
  key: fs.readFileSync('key.pem'),
  cert: fs.readFileSync('cert.pem'),
  secureProtocol: 'TLSv1_method'  // TLS 1.0 - INSECURE!
};

// ❌ VULNERABLE: Certificate validation disabled
const axios = require('axios');
axios.get('https://api.example.com', {
  httpsAgent: new https.Agent({
    rejectUnauthorized: false  // DANGEROUS!
  })
});

// ✅ SECURE: Strong TLS configuration
const https = require('https');
const fs = require('fs');
const tls = require('tls');

const options = {
  key: fs.readFileSync('/etc/ssl/private/key.pem'),
  cert: fs.readFileSync('/etc/ssl/certs/cert.pem'),

  // TLS 1.2+ only
  minVersion: 'TLSv1.2',
  maxVersion: 'TLSv1.3',

  // Strong cipher suites with PFS
  ciphers: [
    'ECDHE-ECDSA-AES128-GCM-SHA256',
    'ECDHE-RSA-AES128-GCM-SHA256',
    'ECDHE-ECDSA-AES256-GCM-SHA384',
    'ECDHE-RSA-AES256-GCM-SHA384',
    'ECDHE-ECDSA-CHACHA20-POLY1305',
    'ECDHE-RSA-CHACHA20-POLY1305'
  ].join(':'),

  // Honor server cipher order
  honorCipherOrder: true,

  // Enable OCSP stapling
  requestOCSP: true
};

const server = https.createServer(options, app);

// Set security headers
server.on('request', (req, res) => {
  res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains; preload');
});

// ✅ SECURE: Certificate validation enabled (default)
const axios = require('axios');
axios.get('https://api.example.com', {
  httpsAgent: new https.Agent({
    rejectUnauthorized: true,  // Always verify certificates
    minVersion: 'TLSv1.2'
  })
});
```

### Security Headers Configuration
```java
// ❌ VULNERABLE: Missing security headers
@Configuration
public class SecurityConfig {
    // No security headers configured
}

// ✅ SECURE: Comprehensive security headers
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.header.writers.*;

@Configuration
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .headers(headers -> headers
                // HSTS - Force HTTPS for 1 year
                .httpStrictTransportSecurity(hsts -> hsts
                    .maxAgeInSeconds(31536000)
                    .includeSubDomains(true)
                    .preload(true)
                )
                // Content Security Policy
                .contentSecurityPolicy(csp -> csp
                    .policyDirectives("default-src 'self'; " +
                        "script-src 'self' 'nonce-{random}'; " +
                        "style-src 'self' 'unsafe-inline'; " +
                        "img-src 'self' data: https:; " +
                        "font-src 'self'; " +
                        "connect-src 'self'; " +
                        "frame-ancestors 'none'; " +
                        "base-uri 'self'; " +
                        "form-action 'self'")
                )
                // X-Frame-Options - Prevent clickjacking
                .frameOptions(frame -> frame.deny())
                // X-Content-Type-Options - Prevent MIME sniffing
                .contentTypeOptions(contentType -> {})
                // X-XSS-Protection
                .xssProtection(xss -> xss
                    .headerValue(XXssProtectionHeaderWriter.HeaderValue.ENABLED_MODE_BLOCK)
                )
                // Referrer Policy
                .referrerPolicy(referrer -> referrer
                    .policy(ReferrerPolicyHeaderWriter.ReferrerPolicy.STRICT_ORIGIN_WHEN_CROSS_ORIGIN)
                )
                // Permissions Policy
                .permissionsPolicy(permissions -> permissions
                    .policy("geolocation=(), microphone=(), camera=()")
                )
            )
            .build();
    }
}
```

### Environment Variable Security
```python
# ❌ VULNERABLE: Hardcoded secrets in config
DATABASE_URL = "postgresql://user:password123@localhost/db"
API_KEY = "sk-1234567890abcdef"
SECRET_KEY = "django-insecure-hardcoded-secret"

# ❌ VULNERABLE: No validation
SECRET_KEY = os.getenv('SECRET_KEY')  # Could be None!
DATABASE_URL = os.getenv('DATABASE_URL')  # Could be None!

# ✅ SECURE: Environment variables with validation
import os
import sys

class Config:
    """Secure configuration with validation"""

    def __init__(self):
        # Required environment variables
        self.SECRET_KEY = self._require_env('SECRET_KEY')
        self.DATABASE_URL = self._require_env('DATABASE_URL')
        self.API_KEY = self._require_env('API_KEY')

        # Optional with secure defaults
        self.DEBUG = os.getenv('DEBUG', 'False') == 'True'
        self.ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
        self.SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', '3600'))

        # Validate configuration
        self._validate()

    def _require_env(self, key: str) -> str:
        """Get required environment variable or fail fast"""
        value = os.getenv(key)
        if not value:
            print(f"ERROR: Required environment variable {key} is not set", file=sys.stderr)
            sys.exit(1)
        return value

    def _validate(self):
        """Validate configuration values"""
        # Ensure DEBUG is False in production
        if self.DEBUG and os.getenv('ENV') == 'production':
            raise ValueError("DEBUG must be False in production")

        # Ensure ALLOWED_HOSTS is set
        if not self.ALLOWED_HOSTS or self.ALLOWED_HOSTS == ['']:
            raise ValueError("ALLOWED_HOSTS must be configured")

        # Validate SECRET_KEY strength
        if len(self.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")

        # Validate database URL format
        if not self.DATABASE_URL.startswith(('postgresql://', 'mysql://')):
            raise ValueError("DATABASE_URL must use postgresql:// or mysql://")

        # Validate session timeout
        if self.SESSION_TIMEOUT < 300 or self.SESSION_TIMEOUT > 86400:
            raise ValueError("SESSION_TIMEOUT must be between 300 and 86400 seconds")

# Usage
config = Config()  # Fails fast if misconfigured

# Django settings.py
SECRET_KEY = config.SECRET_KEY
DEBUG = config.DEBUG
ALLOWED_HOSTS = config.ALLOWED_HOSTS
```

### Database Security Configuration
```ruby
# ❌ VULNERABLE: Insecure database configuration
# config/database.yml (Rails)
production:
  adapter: postgresql
  database: myapp
  username: postgres
  password: password123  # Hardcoded!
  sslmode: disable  # No TLS!

# ❌ VULNERABLE: Too permissive
production:
  adapter: postgresql
  url: <%= ENV['DATABASE_URL'] %>
  # No connection limits, no SSL enforcement

# ✅ SECURE: Production-hardened database configuration
# config/database.yml
production:
  adapter: postgresql
  url: <%= ENV['DATABASE_URL'] %>  # From environment only

  # Enforce SSL/TLS
  sslmode: require
  sslrootcert: /etc/ssl/certs/ca-bundle.crt

  # Connection pooling with limits
  pool: <%= ENV.fetch("DB_POOL_SIZE") { 5 } %>
  timeout: 5000

  # Connection lifetime limits
  reaping_frequency: 10
  checkout_timeout: 5

  # Prepared statements
  prepared_statements: true

  # Read-only replica configuration
  replica:
    adapter: postgresql
    url: <%= ENV['DATABASE_REPLICA_URL'] %>
    sslmode: require
    replica: true

# Initializer: config/initializers/database.rb
Rails.application.config.after_initialize do
  # Validate database connection is using SSL
  conn = ActiveRecord::Base.connection
  ssl_status = conn.execute("SHOW ssl").first['ssl']

  unless ssl_status == 'on'
    raise "Database connection MUST use SSL in production"
  end

  # Log connection info (without credentials)
  Rails.logger.info "Database: #{conn.current_database}, SSL: #{ssl_status}"
end
```

### CORS Configuration
```javascript
// ❌ VULNERABLE: Permissive CORS
const cors = require('cors');
app.use(cors({
  origin: '*',  // Allows any origin!
  credentials: true  // With credentials = dangerous
}));

// ❌ VULNERABLE: Reflecting origin
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', req.headers.origin);  // Reflects any origin!
  res.header('Access-Control-Allow-Credentials', 'true');
  next();
});

// ✅ SECURE: Restrictive CORS configuration
const cors = require('cors');

// Whitelist of allowed origins
const allowedOrigins = process.env.ALLOWED_ORIGINS?.split(',') || [];

if (allowedOrigins.length === 0) {
  throw new Error("ALLOWED_ORIGINS environment variable must be set");
}

const corsOptions = {
  origin: function (origin, callback) {
    // Allow requests with no origin (mobile apps, Postman)
    if (!origin) {
      return callback(null, true);
    }

    // Check against whitelist
    if (allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },

  // Only allow credentials from whitelisted origins
  credentials: true,

  // Limit allowed methods
  methods: ['GET', 'POST', 'PUT', 'DELETE'],

  // Limit allowed headers
  allowedHeaders: ['Content-Type', 'Authorization'],

  // Expose only necessary headers
  exposedHeaders: ['Content-Range', 'X-Content-Range'],

  // Cache preflight for 1 hour
  maxAge: 3600,

  // Don't pass preflight to route handlers
  preflightContinue: false,

  // Provide success status for preflight
  optionsSuccessStatus: 204
};

app.use(cors(corsOptions));

// Log CORS violations
app.use((err, req, res, next) => {
  if (err.message === 'Not allowed by CORS') {
    console.warn(`CORS violation: ${req.headers.origin} attempted to access ${req.path}`);
    return res.status(403).json({ error: 'CORS policy violation' });
  }
  next(err);
});
```

## Integration with Agents

**For comprehensive security analysis, use parallel agents**:

```javascript
// Example: Review production configuration
use the .claude/agents/configuration-specialist.md agent to validate security settings
use the .claude/agents/secrets-specialist.md agent to check environment variable security
use the .claude/agents/web-security-specialist.md agent to verify security headers
```

## Progressive Disclosure

**This overview provides the essentials. For deeper analysis, I can provide**:
- Framework-specific security configurations (Django, Rails, Spring Boot, Express)
- Cloud platform security settings (AWS, Azure, GCP)
- Container security configuration (Docker, Kubernetes)
- Database-specific hardening guides (PostgreSQL, MySQL, MongoDB)
- Web server security configurations (Nginx, Apache)
- CI/CD security configuration
- Infrastructure-as-Code security (Terraform, CloudFormation)

**Security Rules**: See [rules.json](./rules.json) for complete ASVS-aligned rule specifications

---

**Related Skills**: [secrets-management](../secrets-management/SKILL.md), [web-security](../web-security/SKILL.md), [cryptography](../cryptography/SKILL.md)

**Standards Compliance**: ASVS V14.1-V14.5 | OWASP Top 10 2021: A05 | CWE-16, CWE-326, CWE-489
