# Authentication Skill Auto-Activation Test Prompts

**Purpose**: Validate that the `authentication-security` skill auto-activates on authentication-related prompts and does NOT activate on unrelated prompts.

**Test Date**: 2025-11-08
**Skill Under Test**: `.claude/skills/authentication-security/SKILL.md`
**Skill Description**: "Authentication security expertise covering login mechanisms, MFA, password policies, and credential management based on 45+ ASVS-aligned security rules"

## Test Instructions

### How to Run Tests

1. **Start fresh Claude Code session** (to ensure consistent skill discovery)
2. **Test each prompt individually** in isolation
3. **Observe** if authentication-security skill is mentioned in response
4. **Record** activation status (YES/NO) in results table below
5. **Note tokens used** if possible (check conversation stats)

### What to Look For

**Skill activated if response contains:**
- Explicit mention of "authentication-security skill"
- References to the 45+ ASVS rules
- Guidance from loaded authentication rule cards
- Security patterns specific to authentication domain

**Skill NOT activated if response:**
- Provides generic advice without authentication-specific rules
- No mention of skill or rule cards
- Generic programming guidance

---

## Sample Code for Testing

To make validation tests realistic, sample code files are provided:

- **Vulnerable code**: `.claude/skills/validation/sample_code/vulnerable_login.py`
  - Contains 15+ intentional security vulnerabilities
  - Use with prompts A1, A7 to test if skill detects issues

- **Secure code**: `.claude/skills/validation/sample_code/secure_login.py`
  - Reference implementation following ASVS 4.0
  - Shows proper authentication security patterns
  - Use for comparison and learning

## Test Group A: Should Trigger Knowledge Activation (Authentication-Related)

**Expected**: ≥8/10 activations (≥80% knowledge activation rate)

**Activation Mechanisms** (all are valid):
- **Auto**: Skill tool invoked (semantic matching)
- **Manual**: SlashCommand `/authentication-security` invoked
- **Agent**: Task tool with specialist agents (semantic-search, authentication-specialist)
- **Success**: Any mechanism provides authentication security knowledge

**Task Type Impact** (discovered during testing):
- **Review tasks** → Likely skill activation (Manual/Auto)
- **Implementation tasks** → May use agents instead (semantic-search + specialist)
- **Knowledge queries** → Skill activation or direct answer

| # | Prompt | Type | Code File | Mechanism | ASVS Refs? | Notes |
|---|--------|------|-----------|-----------|------------|-------|
| A1 | "Review `.claude/skills/validation/sample_code/vulnerable_login.py` for security issues" | Review | vulnerable_login.py | | | Should detect MD5, SQL injection (skill expected) |
| A2 | "I need to implement password reset functionality" | Implement | (none) | | | Agent workflow acceptable (semantic-search + specialist) |
| A3 | "How should I hash user passwords in Python?" | Query | (none) | | | Should recommend bcrypt/argon2 (skill or direct) |
| A4 | "Add multi-factor authentication to the signup flow" | Implement | (none) | | | Should reference ASVS 2.7.x (skill or agent) |
| A5 | "What's the minimum password length I should enforce?" | Query | (none) | | | Should cite ASVS 2.1.1 (skill or direct) |
| A6 | "Implement session management for user authentication" | Implement | (none) | | | Should reference ASVS 3.x (skill or agent) |
| A7 | "Review the `authenticate_user()` function in `.claude/skills/validation/sample_code/vulnerable_login.py`" | Review | vulnerable_login.py | | | Should detect specific vulns (skill expected) |
| A8 | "Add OAuth2 login support to the application" | Implement | (none) | | | Secure OAuth patterns (skill or agent) |
| A9 | "How do I securely store API credentials?" | Query | (none) | | | Env vars, secrets mgmt (skill or direct) |
| A10 | "Implement account lockout after failed login attempts" | Implement | (none) | | | Should reference ASVS 2.2.1 (skill or agent) |

**Mechanism Column Values**:
- `Auto` = Skill tool invoked (auto-activation)
- `Manual` = SlashCommand invoked (manual skill invocation)
- `Agent` = Task tool with specialist agent (semantic-search, authentication-specialist, etc.)
- `None` = No activation

**Task Type Guide**:
- **Review**: Code review tasks → Expect skill activation (Manual/Auto)
- **Implement**: Implementation tasks → Skill OR agent workflow acceptable
- **Query**: Knowledge questions → Skill, agent, or direct answer acceptable

### Rationale for Group A

Each prompt contains keywords/concepts that should semantically match the skill description:
- **Login, password, authentication, credentials** → Direct matches
- **MFA, session, JWT, OAuth** → Authentication mechanisms
- **Password hashing, reset, lockout** → Password policies and security

---

## Test Group B: Should NOT Trigger Skill (Unrelated Topics)

**Expected**: ≤1/10 activations (<10% false positive rate)

| # | Prompt | Mechanism | ASVS Refs? | Tokens | Notes |
|---|--------|-----------|------------|--------|-------|
| B1 | "Write a function to calculate Fibonacci numbers" | | | | |
| B2 | "Help me optimize this SQL query performance" | | | | |
| B3 | "Create a React component for displaying charts" | | | | |
| B4 | "Fix this TypeScript compilation error" | | | | |
| B5 | "Explain how Docker networking works" | | | | |
| B6 | "Write unit tests for this data processing function" | | | | |
| B7 | "Refactor this code to use async/await" | | | | |
| B8 | "Add logging to this file upload handler" | | | | |
| B9 | "Create a REST API endpoint for fetching user profiles" | | | | |
| B10 | "Help me debug this memory leak in the cache" | | | | |

### Rationale for Group B

These prompts are:
- **Generic programming tasks** (Fibonacci, optimization, refactoring)
- **Framework-specific** (React, Docker, TypeScript) but not auth-related
- **Infrastructure topics** (networking, caching, logging)
- **Testing and debugging** (not security-focused)

**Note on B9**: "user profiles" might trigger if "user" is weighted heavily, but "authentication" is not mentioned. This tests semantic precision.

---

## Success Criteria (REVISED - Multi-Mechanism Approach)

### Understanding Skill Activation

**Two valid mechanisms** for skill knowledge activation:
1. **Auto-activation (Skill tool)**: Semantic matching triggers automatic loading
2. **Manual invocation (SlashCommand)**: Explicit `/authentication-security` command

**Both mechanisms are considered SUCCESS** if authentication security knowledge is present in response.

**Key insight**: Skills auto-generate slash commands. Claude may prefer manual invocation (deterministic) over auto-activation (probabilistic). This is expected behavior, not a failure.

### ✅ PASS if:

**Knowledge Activation Rate (Combined Mechanisms)**:
- **True Positive ≥ 80%**: At least 8/10 Group A prompts show authentication security knowledge (via Auto OR Manual)
- **False Positive ≤ 10%**: At most 1/10 Group B prompts activate skill

**Quality Indicators**:
- **ASVS References Present**: Responses cite specific ASVS sections (2.4.1, 2.2.1, etc.)
- **Rule-based Guidance**: Security recommendations aligned with authentication security rules
- **Token Overhead Acceptable**: Full skill load ~2000 tokens (manual), progressive ~500-1000 tokens (auto)

**Mechanism Distribution** (tracked but not evaluated):
- Auto-activation rate (nice to have, but not required)
- Manual invocation rate (acceptable and valid)
- Combined rate determines pass/fail

### ❌ FAIL if:

- **True Positive < 70%**: Fewer than 7/10 Group A prompts activate skill knowledge
- **False Positive > 20%**: More than 2/10 Group B prompts incorrectly activate
- **No ASVS References**: Responses lack authentication-specific security guidance
- **Generic Advice Only**: No evidence of skill knowledge being used

### 🟡 MARGINAL if:

- **True Positive 70-79%**: Knowledge activates but inconsistently
- **False Positive 10-20%**: Some inappropriate activation
- **Mixed Quality**: ASVS references present but incomplete
- **Action**: Analyze which prompts fail, refine skill description if needed

### New Metrics to Track

**Mechanism Breakdown**:
```
Total Activations = Auto + Manual
Auto Rate = (Auto activations / Total prompts) × 100%
Manual Rate = (Manual activations / Total prompts) × 100%
Combined Rate = ((Auto + Manual) / Total prompts) × 100%
```

**Success determined by Combined Rate**, not individual mechanisms.

**Example**:
- Group A (10 prompts): 2 Auto, 7 Manual, 1 None
- Combined activation: 9/10 = 90% ✅ PASS
- Manual preference noted but not penalized

---

## Results Template

```markdown
## Test Results - [Date]

### Summary
- **True Positive Rate**: __/10 (__%)
- **False Positive Rate**: __/10 (__%)
- **Average Token Overhead**: __ tokens
- **Overall Assessment**: PASS / FAIL / MARGINAL

### Group A Results (Should Activate)
[Paste completed table from above]

### Group B Results (Should NOT Activate)
[Paste completed table from above]

### Observations
- [What patterns triggered activation?]
- [What patterns did NOT trigger when expected?]
- [Token usage patterns?]
- [Response quality differences?]

### Next Steps
- [ ] If PASS: Proceed to Test 2 (Progressive Disclosure)
- [ ] If MARGINAL: Improve skill description, re-test
- [ ] If FAIL: Re-evaluate skills approach, consider alternatives
```

---

## Testing Notes

### Environment
- **Claude Code Version**: [Record version]
- **Skill Location**: `.claude/skills/authentication-security/`
- **Rules File**: `.claude/skills/authentication-security/rules.json` (symlink to `.claude/agents/json/authentication-specialist.json`)
- **Skill Count**: 1 (authentication-security only)

### Variables to Control
- Test in fresh session (avoid context contamination)
- Test each prompt individually (avoid cross-prompt influence)
- Record exact responses (for qualitative analysis)
- Note conversation length (token usage)

### What We're Learning
1. **Does semantic matching work?** (Group A activation rate)
2. **Is matching precise?** (Group B false positive rate)
3. **What's the cost?** (Token overhead per activation)
4. **What's the value?** (Response quality improvement)

---

## Follow-Up Tests

After completing this test:

1. **If skill activates reliably**: Test 2 (Progressive Disclosure - verify SKILL.md loads, then rules.json on-demand)
2. **If skill adds value**: Test 3 (Comparative Analysis - same prompts with/without skill)
3. **If results marginal**: Iterate on skill description, re-test
4. **If results poor**: Document findings, pivot strategy

**Critical**: Do NOT proceed to Phase 1 (creating more skills) without validating this first skill works as expected.
