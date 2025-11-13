# Test Prompts: secrets-management Skill

**Skill**: secrets-management
**Date**: 2025-11-09
**Phase**: Phase 1 - First skill migration
**Goal**: Validate activation, ASVS references, timing

**Status**: 🔄 RETEST NEEDED - CLAUDE.md patterns updated (Pattern 5 & 6 added)

**Previous Results**: 0/2 activation (0%)
**Pattern Fix**: Added missing review patterns (lines 300-306)
**Expected After Fix**: Tests 1-2 should now activate secrets-specialist

---

## Test Instructions

1. **Start FRESH Claude Code session** for each test (no context pollution)
2. **Copy ONE prompt** below
3. **Run it** and observe activation
4. **Document results** in table below
5. **Move to next prompt** in new session

---

## Test Prompts (5 total)

### Test 1: Hardcoded API Key Detection (Review)
**Pattern Match**: Should trigger Pattern 5 (`api.*key` in review context)

```
Review this Python code for security issues:

```python
import requests

API_KEY = "sk_live_1234567890abcdefghijklmnop"

def fetch_data():
    response = requests.get(
        "https://api.example.com/data",
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    return response.json()
```


**Expected**:
- ✅ secrets-management or secrets-specialist activation
- ✅ ASVS V6.4.1 reference (secrets not hardcoded)
- ✅ CWE-798 citation
- ✅ Secure code example (environment variables)



### Test 2: Database Credential Security (Review)
**Pattern Match**: Should trigger Pattern 6 (`connection.*secur` in review context)

```
Review the database connection security in this code:

```python
import psycopg2

conn = psycopg2.connect(
    "postgresql://admin:password123@localhost:5432/mydb"
)
```


**Expected**:
- ✅ secrets-management or secrets-specialist activation
- ✅ ASVS reference
- ✅ Identifies hardcoded password in connection string
- ✅ Suggests environment variables or secret vault



### Test 3: JWT Secret Validation (Implementation)
```
Add JWT authentication to this Flask app:

```python
from flask import Flask, request
import jwt

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    # TODO: Add JWT token generation
    pass
```
```

**Expected**:
- ✅ Pre-implementation guard triggers (file path + security keyword)
- ✅ Research BEFORE implementation
- ✅ secrets-management + authentication-specialist (dual-agent?)
- ✅ Guidance on JWT secret strength (≥256 bits)
- ✅ Environment variable recommendation

---

### Test 4: Cloud Credentials Query
```
What's the secure way to handle AWS credentials in a Python application?
```

**Expected**:
- ✅ secrets-management or semantic-search activation
- ✅ Dual-agent workflow (semantic-search + secrets-specialist)
- ✅ OWASP / ASVS references
- ✅ Multiple options: IAM roles, environment variables, AWS Secrets Manager
- ✅ Warns against hardcoded access keys

---

### Test 5: Environment Variable Security (File-Specific)
```
Add secret management to .claude/skills/validation/sample_code/secure_login.py
```

**Expected**:
- ✅ Pre-implementation guard triggers
- ✅ Research → Guide workflow
- ✅ secrets-management or secrets-specialist
- ✅ .env file guidance
- ✅ python-dotenv or similar recommendations

---

## Results Tracking

| Test | Prompt Type | Activated? | Correct Agent? | ASVS Refs? | Timing OK? | Notes |
|------|-------------|------------|----------------|------------|------------|-------|
| 1 | Review | | | | | Hardcoded API key |
| 2 | Review | | | | | DB credentials |
| 3 | Implementation | | | | | JWT + Flask (pre-guard?) |
| 4 | Query | | | | | AWS creds query |
| 5 | File-specific | | | | | Pre-guard test |

**Activation Rate**: __/5 = __%
**False Positives**: __/5 = __%
**Critical Failures**: __

**Gate Decision**: ⬜ PASS (≥70%, no critical) / ⬜ FIX / ⬜ FAIL

---

## Quick Fill Instructions

For each test, mark:
- **Activated?**: YES / NO / PARTIAL
- **Correct Agent?**: secrets-mgmt / secrets-specialist / other / NONE
- **ASVS Refs?**: YES / NO
- **Timing OK?**: ✅ (research before) / ⚠️ (direct implementation) / N/A (query/review)
- **Notes**: Any observations

---

## Example Filled Row

| Test | Prompt Type | Activated? | Correct Agent? | ASVS Refs? | Timing OK? | Notes |
|------|-------------|------------|----------------|------------|------------|-------|
| 1 | Review | YES | secrets-specialist | YES | ✅ | V6.4.1 cited, good examples |

---

## After Testing

1. Calculate activation rate: (Activated correctly / 5) × 100%
2. Check for critical failures (timing issues like A4)
3. Make gate decision:
   - ✅ PASS if ≥70% (4/5 or 5/5) and no critical failures
   - ⚠️ FIX if close but has issues
   - ❌ FAIL if <70% or critical failures

4. Document findings in PHASE_1_TESTS.md
5. Update STATUS.md with secrets-management progress
6. If PASS: Proceed to next skill (session-management)

---

**Note**: Don't obsess over perfection. Looking for patterns, not 100% accuracy. Manual testing = realistic expectations.
