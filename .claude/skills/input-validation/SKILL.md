---
name: input-validation
description: Use me for injection prevention (SQL/NoSQL/Command/LDAP/XPath/XSS), input sanitization and validation, output encoding, parameterized queries, allowlist validation, and data type enforcement. I return ASVS-mapped findings with rule IDs and secure input handling patterns.
version: 1.0.0
domains:
  - injection-prevention
  - input-sanitization
  - output-encoding
  - data-validation
allowed-tools: Read, Grep, Bash
---

# Input Validation Security Skill

## Activation Triggers

**I respond to these queries and tasks**:
- SQL injection prevention and detection
- NoSQL injection prevention
- Command injection prevention
- LDAP/XPath injection prevention
- Cross-Site Scripting (XSS) prevention
- Input sanitization and validation
- Output encoding (HTML/JavaScript/URL)
- Parameterized queries and prepared statements
- Allowlist validation patterns
- Data type and format enforcement
- User input handling security

**Manual activation**:
- `/input-validation` - Load this skill
- "use input-validation skill" - Explicit load request
- "use input-validation-specialist agent" - Call agent variant

---

## Skill Overview

You are equipped with 6 ASVS-aligned input validation security rules covering injection prevention, sanitization, output encoding, and validation patterns. This skill returns findings with ASVS references, CWE mappings, and secure input handling examples.

## Security Knowledge Base

### Input Validation Domains

**Injection Prevention (3 rules)**
- SQL injection (use parameterized queries)
- NoSQL injection (sanitize MongoDB/Redis queries)
- Command injection (never use shell=True with user input)
- LDAP/XPath injection

**Input Sanitization (2 rules)**
- Allowlist validation (validate before sanitize)
- Data type enforcement
- Length and format validation
- Special character handling

**Output Encoding (1 rule)**
- HTML encoding (prevent XSS)
- JavaScript encoding
- URL encoding
- Context-aware encoding

## Common Vulnerabilities Detected

### Critical Issues
- 🔴 **SQL Injection**: String concatenation in queries
- 🔴 **Command Injection**: subprocess with shell=True + user input
- 🔴 **XSS**: Unencoded user input in HTML

### High Severity
- 🟠 **NoSQL Injection**: Unsanitized input in MongoDB queries
- 🟠 **Missing Validation**: No input validation before processing
- 🟠 **Blacklist Filtering**: Using blacklist instead of allowlist

## Security Standards Coverage

**ASVS Alignment**:
- V5.1: Input Validation
- V5.2: Sanitization and Sandboxing
- V5.3: Output Encoding and Injection Prevention
- V5.5: Deserialization Prevention

**CWE Mapping**:
- CWE-89: SQL Injection
- CWE-79: Cross-site Scripting (XSS)
- CWE-78: OS Command Injection
- CWE-20: Improper Input Validation
- CWE-116: Improper Encoding/Escaping

**OWASP Top 10**:
- A03:2021 Injection

## Detection Patterns

```python
# ❌ CRITICAL: SQL injection
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)

# ❌ CRITICAL: Command injection
subprocess.run(f"ping {user_input}", shell=True)

# ❌ CRITICAL: XSS
html = f"<div>Welcome {username}</div>"
```

## Secure Patterns

**✅ SQL Injection Prevention**:
```python
# ✅ SECURE: Parameterized query
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# ✅ SECURE: ORM
user = User.query.filter_by(id=user_id).first()
```

**✅ Command Injection Prevention**:
```python
# ✅ SECURE: Array arguments, no shell
subprocess.run(['ping', '-c', '4', user_input], shell=False)

# ✅ SECURE: Allowlist validation first
if not re.match(r'^[a-zA-Z0-9.-]+$', user_input):
    raise ValueError("Invalid hostname")
subprocess.run(['ping', '-c', '4', user_input], shell=False)
```

**✅ XSS Prevention**:
```python
# ✅ SECURE: HTML encoding
from markupsafe import escape
html = f"<div>Welcome {escape(username)}</div>"

# ✅ SECURE: Template auto-escaping
return render_template('welcome.html', username=username)
```

## Progressive Disclosure

1. **Initial Load** (~1.5k tokens): Overview and patterns
2. **On Demand** (~1k tokens): Specific injection types
3. **Deep Dive** (~1k tokens): Full remediation

Total: ~3.5k tokens maximum

## References

**Security Rules**: 6 compiled rules in `json/input_validation_rules.json`

**Standards**:
- ASVS 4.0: V5 (Validation, Sanitization, Encoding)
- OWASP CheatSheet: Input Validation
- OWASP Top 10:2021 A03 (Injection)

---

**Remember**: Never trust user input. Always validate (allowlist), then sanitize, then encode for output context. Use parameterized queries for SQL, avoid shell=True for commands.
