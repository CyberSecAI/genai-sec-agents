---
name: logging-security
description: Use me for security logging and monitoring reviews, audit trail implementation, sensitive data exposure in logs, log injection prevention, log tampering protection, and security event monitoring. I return ASVS-mapped findings with rule IDs and secure code examples.
---

# Logging Security Skill

**I provide security logging and monitoring guidance following ASVS, OWASP, and CWE standards.**

## Activation Triggers

**I respond to these queries and tasks**:
- Security event logging and audit trails
- Sensitive data exposure in logs (passwords, tokens, PII)
- Log injection prevention (CRLF injection, log forging)
- Log tampering and integrity protection
- Security monitoring and alerting
- Log retention and compliance (GDPR, HIPAA, SOC2)
- Centralized logging and SIEM integration
- Authentication/authorization event logging
- Error logging without sensitive data

**Manual activation**: Use `/logging-security` or mention "logging security review"

**Agent variant**: For parallel analysis with other security checks, use the `logging-specialist` agent via the Task tool

## Security Knowledge Base

### Sensitive Data in Logs (8 rules)
- Never log passwords, API keys, tokens, or secrets
- Redact or mask PII (SSN, credit cards, email) in logs
- Sanitize user input before logging
- Don't log full request/response bodies with credentials
- Avoid logging session IDs or authentication tokens
- Redact sensitive fields in structured logs (JSON)
- Use logging frameworks with built-in redaction
- Implement data classification for log content

### Security Event Logging (5 rules)
- Log authentication events (login, logout, failed attempts)
- Log authorization failures and privilege escalations
- Log security configuration changes
- Log data access and modifications
- Include context: user ID, IP, timestamp, resource
- Log security-critical events with appropriate severity
- Capture sufficient detail for incident investigation

### Log Injection Prevention (3 rules)
- Sanitize all user input before logging
- Prevent CRLF injection in log entries
- Use structured logging (JSON) to prevent log forging
- Validate log data format and encoding
- Escape newlines and control characters
- Don't trust user-controlled data in log messages

### Log Integrity and Protection (2 rules)
- Protect logs from tampering (write-only permissions)
- Use append-only log storage
- Implement log signing or cryptographic hashing
- Centralize logs to secure, immutable storage
- Monitor logs for tampering attempts
- Separate log write and read permissions

## Common Vulnerabilities

| Vulnerability | Severity | CWE | OWASP Top 10 |
|--------------|----------|-----|--------------|
| Passwords/secrets in logs | **CRITICAL** | CWE-532 | A02:2021 Cryptographic Failures |
| PII exposure in logs | **HIGH** | CWE-532 | A01:2021 Broken Access Control |
| Log injection (CRLF) | **HIGH** | CWE-117 | A03:2021 Injection |
| Missing security event logging | **MEDIUM** | CWE-778 | A09:2021 Security Logging Failures |
| Insufficient log retention | **MEDIUM** | CWE-223 | A09:2021 Security Logging Failures |
| Log tampering (no integrity check) | **MEDIUM** | CWE-117 | A08:2021 Software and Data Integrity Failures |

## Detection Patterns

**I scan for these security issues**:

### Sensitive Data Exposure
```python
# ❌ VULNERABLE: Logging passwords
import logging
logger = logging.getLogger(__name__)

def authenticate(username, password):
    logger.info(f"Login attempt: {username} with password {password}")  # Exposed!

# ❌ VULNERABLE: Logging API keys
logger.debug(f"API request with key: {api_key}")  # Exposed!

# ❌ VULNERABLE: Logging full request
logger.info(f"Request: {request.body}")  # May contain secrets

# ✅ SECURE: Redact sensitive data
import logging
import re

class SensitiveDataFilter(logging.Filter):
    def filter(self, record):
        # Redact patterns
        record.msg = re.sub(r'password["\s:=]+\S+', 'password=***REDACTED***', str(record.msg), flags=re.IGNORECASE)
        record.msg = re.sub(r'api[_-]?key["\s:=]+\S+', 'api_key=***REDACTED***', str(record.msg), flags=re.IGNORECASE)
        record.msg = re.sub(r'token["\s:=]+\S+', 'token=***REDACTED***', str(record.msg), flags=re.IGNORECASE)
        return True

logger = logging.getLogger(__name__)
logger.addFilter(SensitiveDataFilter())

def authenticate(username, password):
    logger.info(f"Login attempt: user={username}")  # No password logged
    result = check_credentials(username, password)
    if result:
        logger.info(f"Successful login: user={username}, ip={request.remote_addr}")
    else:
        logger.warning(f"Failed login: user={username}, ip={request.remote_addr}")
```

### Log Injection Prevention
```javascript
// ❌ VULNERABLE: CRLF injection
const logger = require('winston');

app.post('/login', (req, res) => {
  logger.info(`Login attempt: ${req.body.username}`);  // CRLF injection!
  // Attacker sends: username="admin\nPASSWORD: secret123"
});

// ❌ VULNERABLE: Log forging
logger.info(`User action: ${userInput}`);  // Can inject fake log entries

// ✅ SECURE: Structured logging with sanitization
const winston = require('winston');

const logger = winston.createLogger({
  format: winston.format.json(),  // Structured logging prevents injection
  transports: [
    new winston.transports.File({ filename: 'app.log' })
  ]
});

function sanitizeLogInput(input) {
  if (typeof input !== 'string') return input;
  // Remove CRLF and control characters
  return input.replace(/[\r\n\t]/g, ' ').substring(0, 1000);
}

app.post('/login', (req, res) => {
  logger.info({
    event: 'login_attempt',
    username: sanitizeLogInput(req.body.username),
    ip: req.ip,
    timestamp: new Date().toISOString()
  });
});
```

### Security Event Logging
```java
// ❌ VULNERABLE: No security event logging
public void updateUserRole(String userId, String newRole) {
    userRepository.updateRole(userId, newRole);  // No logging!
}

// ❌ VULNERABLE: Insufficient context
logger.info("User role updated");  // Who? When? What role?

// ✅ SECURE: Comprehensive security event logging
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

public class UserService {
    private static final Logger securityLogger = LoggerFactory.getLogger("SECURITY");

    public void updateUserRole(String userId, String newRole, String adminId) {
        String oldRole = userRepository.getRole(userId);

        // Set context
        MDC.put("event_type", "authorization_change");
        MDC.put("admin_id", adminId);
        MDC.put("target_user_id", userId);
        MDC.put("ip_address", getClientIp());

        try {
            userRepository.updateRole(userId, newRole);

            // Log successful change
            securityLogger.info(
                "Role changed: user={} old_role={} new_role={} admin={} ip={}",
                userId, oldRole, newRole, adminId, getClientIp()
            );
        } catch (UnauthorizedException e) {
            // Log authorization failure
            securityLogger.warn(
                "Unauthorized role change attempt: admin={} target_user={} ip={}",
                adminId, userId, getClientIp()
            );
            throw e;
        } finally {
            MDC.clear();
        }
    }

    public void login(String username, String password) {
        try {
            User user = authenticate(username, password);

            securityLogger.info(
                "Successful login: user={} ip={} user_agent={}",
                user.getId(), getClientIp(), getUserAgent()
            );
        } catch (AuthenticationException e) {
            securityLogger.warn(
                "Failed login attempt: username={} ip={} reason={}",
                username, getClientIp(), e.getMessage()
            );
            throw e;
        }
    }
}
```

### Log Integrity Protection
```python
# ❌ VULNERABLE: Logs can be tampered with
import logging
logging.basicConfig(filename='app.log', level=logging.INFO)
# File permissions allow modification

# ❌ VULNERABLE: No integrity verification
logger.info("Security event")  # Can be modified later

# ✅ SECURE: Append-only logs with integrity checks
import logging
import hmac
import hashlib
import os
from datetime import datetime

class IntegrityLogger:
    def __init__(self, log_file, secret_key):
        self.log_file = log_file
        self.secret_key = secret_key

        # Create log file with restricted permissions (append-only)
        if not os.path.exists(log_file):
            open(log_file, 'a').close()
            os.chmod(log_file, 0o600)  # Owner read/write only

    def log(self, level, message, **context):
        timestamp = datetime.utcnow().isoformat()

        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message,
            **context
        }

        # Create integrity signature
        log_data = f"{timestamp}|{level}|{message}|{context}"
        signature = hmac.new(
            self.secret_key.encode(),
            log_data.encode(),
            hashlib.sha256
        ).hexdigest()

        log_entry['signature'] = signature

        # Append to log file
        with open(self.log_file, 'a') as f:
            import json
            f.write(json.dumps(log_entry) + '\n')

    def verify_log_integrity(self):
        """Verify all log entries haven't been tampered with"""
        with open(self.log_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                entry = json.loads(line)

                # Recreate signature
                log_data = f"{entry['timestamp']}|{entry['level']}|{entry['message']}|{entry.get('context', {})}"
                expected_sig = hmac.new(
                    self.secret_key.encode(),
                    log_data.encode(),
                    hashlib.sha256
                ).hexdigest()

                if entry['signature'] != expected_sig:
                    raise ValueError(f"Log tampering detected at line {line_num}")

# Usage
secret_key = os.getenv('LOG_INTEGRITY_KEY')
logger = IntegrityLogger('/var/log/app/security.log', secret_key)

logger.log('INFO', 'User login', user_id='12345', ip='192.168.1.100')
logger.log('WARNING', 'Failed authorization', user_id='12345', resource='admin_panel')

# Periodically verify integrity
logger.verify_log_integrity()
```

### Centralized Logging with SIEM
```javascript
// ✅ SECURE: Structured logging to SIEM
const winston = require('winston');
const SyslogTransport = require('winston-syslog').Syslog;

const logger = winston.createLogger({
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    // Local file (backup)
    new winston.transports.File({
      filename: '/var/log/app/security.log',
      mode: 0o600  // Restricted permissions
    }),
    // SIEM integration (centralized, immutable)
    new SyslogTransport({
      host: process.env.SIEM_HOST,
      port: 514,
      protocol: 'tcp',
      facility: 'local0',
      app_name: 'web-api'
    })
  ]
});

// Security event helper
function logSecurityEvent(eventType, details) {
  logger.info({
    event_category: 'security',
    event_type: eventType,
    ...details,
    timestamp: new Date().toISOString()
  });
}

// Usage
logSecurityEvent('authentication_success', {
  user_id: user.id,
  ip_address: req.ip,
  user_agent: req.headers['user-agent']
});

logSecurityEvent('authorization_failure', {
  user_id: user.id,
  resource: '/admin/users',
  action: 'DELETE',
  ip_address: req.ip
});
```

## Integration with Agents

**For comprehensive security analysis, use parallel agents**:

```javascript
// Example: Review application logging
use the .claude/agents/logging-specialist.md agent to validate logging implementation
use the .claude/agents/secrets-specialist.md agent to check for hardcoded secrets in logs
use the .claude/agents/data-protection-specialist.md agent to verify PII handling
```

## Progressive Disclosure

**This overview provides the essentials. For deeper analysis, I can provide**:
- SIEM integration patterns (Splunk, ELK, Datadog)
- Compliance-specific logging requirements (GDPR, HIPAA, PCI-DSS, SOC2)
- Log aggregation and centralization strategies
- Security alerting and anomaly detection rules
- Log retention policies and archival strategies
- Language-specific logging framework configurations
- Container and cloud logging best practices (Docker, Kubernetes, AWS CloudWatch)

**Security Rules**: See [rules.json](./rules.json) for complete ASVS-aligned rule specifications

---

**Related Skills**: [data-protection](../data-protection/SKILL.md), [secrets-management](../secrets-management/SKILL.md), [authentication-security](../authentication-security/SKILL.md)

**Standards Compliance**: ASVS V7.1, V7.2 | OWASP Top 10 2021: A09 | CWE-532, CWE-117, CWE-778
