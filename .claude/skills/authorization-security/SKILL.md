---
name: authorization-security
description: Use me for RBAC (Role-Based Access Control) reviews, permission model validation, privilege escalation prevention, access control enforcement, resource authorization checks, insecure direct object references (IDOR), and least privilege principle validation. I return ASVS-mapped findings with rule IDs and secure authorization patterns.
version: 1.0.0
domains:
  - rbac
  - access-control
  - privilege-management
  - authorization-enforcement
allowed-tools: Read, Grep, Bash
---

# Authorization Security Skill

**Complete Security Rules**: [rules.json](./rules.json) | 13 ASVS-aligned authorization rules with detection patterns

## Activation Triggers

**I respond to these queries and tasks**:
- Role-Based Access Control (RBAC) implementation
- Permission model design and validation
- Privilege escalation prevention
- Access control enforcement
- Resource-level authorization checks
- Insecure Direct Object References (IDOR) prevention
- Least privilege principle validation
- Authorization bypass detection
- Admin/user role separation
- Fine-grained access control

**Manual activation**:
- `/authorization-security` - Load this skill
- "use authorization-security skill" - Explicit load request
- "use authorization-specialist agent" - Call agent variant

---

## Skill Overview

You are equipped with 13 ASVS-aligned authorization security rules covering RBAC, access control enforcement, privilege management, and IDOR prevention. This skill returns findings with ASVS references, CWE mappings, and secure authorization patterns.

## Security Knowledge Base

### Authorization Domains

**RBAC & Permissions (5 rules)**
- Role definition and assignment
- Permission granularity
- Role hierarchy management
- Default deny principle

**Access Control Enforcement (4 rules)**
- Authorization checks on every request
- Resource-level access validation
- Ownership verification
- Contextual authorization

**Privilege Management (4 rules)**
- Least privilege enforcement
- Privilege escalation prevention
- Administrative function protection
- Temporary privilege elevation

## Common Vulnerabilities Detected

### Critical Issues
- 🔴 **Missing Authorization**: No access checks
- 🔴 **IDOR**: Direct object access without ownership check
- 🔴 **Privilege Escalation**: Users can elevate privileges

### High Severity
- 🟠 **Broken Access Control**: Inconsistent enforcement
- 🟠 **Horizontal Privilege Escalation**: Access other users' data
- 🟠 **Vertical Privilege Escalation**: Access admin functions

## Security Standards Coverage

**ASVS Alignment**:
- V4.1: General Access Control Design
- V4.2: Operation Level Access Control
- V4.3: Other Access Control Considerations

**CWE Mapping**:
- CWE-285: Improper Authorization
- CWE-639: Authorization Bypass
- CWE-732: Incorrect Permission Assignment
- CWE-284: Improper Access Control

**OWASP Top 10**:
- A01:2021 Broken Access Control

## Detection Patterns

```python
# ❌ CRITICAL: No authorization check
@app.route('/user/<user_id>/profile')
def get_profile(user_id):
    return User.query.get(user_id).to_dict()

# ❌ CRITICAL: IDOR - no ownership check
@app.route('/document/<doc_id>')
def get_document(doc_id):
    return Document.query.get(doc_id).content
```

## Secure Patterns

**✅ Resource Authorization**:
```python
from flask_login import current_user

@app.route('/user/<user_id>/profile')
def get_profile(user_id):
    # ✅ SECURE: Check ownership
    if str(current_user.id) != user_id and not current_user.is_admin:
        abort(403)
    return User.query.get(user_id).to_dict()

@app.route('/document/<doc_id>')
def get_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    # ✅ SECURE: Verify ownership
    if doc.owner_id != current_user.id:
        abort(403)
    return doc.content
```

**✅ RBAC Implementation**:
```python
from functools import wraps

def require_role(role):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.has_role(role):
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator

@app.route('/admin/users')
@require_role('admin')
def admin_users():
    return User.query.all()
```

## References

**Security Rules**: 13 compiled rules in `json/authorization_rules.json`

**Standards**:
- ASVS 4.0: V4 (Access Control)
- OWASP CheatSheet: Authorization
- OWASP Top 10:2021 A01

---

**Remember**: Always check authorization on EVERY request. Verify resource ownership. Implement least privilege. Default deny.
