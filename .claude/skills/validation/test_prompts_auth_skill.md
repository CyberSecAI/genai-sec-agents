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

## Test Group A: Should Trigger Skill (Authentication-Related)

**Expected**: ≥8/10 activations (≥80% true positive rate)

| # | Prompt | Activated? | Tokens | Notes |
|---|--------|-----------|--------|-------|
| A1 | "Review this login function for security issues" | | | |
| A2 | "I need to implement password reset functionality" | | | |
| A3 | "How should I hash user passwords in Python?" | | | |
| A4 | "Add multi-factor authentication to the signup flow" | | | |
| A5 | "What's the minimum password length I should enforce?" | | | |
| A6 | "Implement session management for user authentication" | | | |
| A7 | "Review this JWT token validation code" | | | |
| A8 | "Add OAuth2 login support to the application" | | | |
| A9 | "How do I securely store API credentials?" | | | |
| A10 | "Implement account lockout after failed login attempts" | | | |

### Rationale for Group A

Each prompt contains keywords/concepts that should semantically match the skill description:
- **Login, password, authentication, credentials** → Direct matches
- **MFA, session, JWT, OAuth** → Authentication mechanisms
- **Password hashing, reset, lockout** → Password policies and security

---

## Test Group B: Should NOT Trigger Skill (Unrelated Topics)

**Expected**: ≤1/10 activations (<10% false positive rate)

| # | Prompt | Activated? | Tokens | Notes |
|---|--------|-----------|--------|-------|
| B1 | "Write a function to calculate Fibonacci numbers" | | | |
| B2 | "Help me optimize this SQL query performance" | | | |
| B3 | "Create a React component for displaying charts" | | | |
| B4 | "Fix this TypeScript compilation error" | | | |
| B5 | "Explain how Docker networking works" | | | |
| B6 | "Write unit tests for this data processing function" | | | |
| B7 | "Refactor this code to use async/await" | | | |
| B8 | "Add logging to this file upload handler" | | | |
| B9 | "Create a REST API endpoint for fetching user profiles" | | | |
| B10 | "Help me debug this memory leak in the cache" | | | |

### Rationale for Group B

These prompts are:
- **Generic programming tasks** (Fibonacci, optimization, refactoring)
- **Framework-specific** (React, Docker, TypeScript) but not auth-related
- **Infrastructure topics** (networking, caching, logging)
- **Testing and debugging** (not security-focused)

**Note on B9**: "user profiles" might trigger if "user" is weighted heavily, but "authentication" is not mentioned. This tests semantic precision.

---

## Success Criteria

### ✅ PASS if:
- **True Positive Rate ≥ 80%**: At least 8/10 Group A prompts activate skill
- **False Positive Rate ≤ 10%**: At most 1/10 Group B prompts activate skill
- **Token overhead acceptable**: Skill activation adds <500 tokens per prompt
- **Response quality improved**: Skill-activated responses show measurable security improvement

### ❌ FAIL if:
- **True Positive Rate < 70%**: Fewer than 7/10 Group A prompts activate skill
- **False Positive Rate > 20%**: More than 2/10 Group B prompts activate skill
- **Token overhead excessive**: Skill activation adds >1000 tokens per prompt
- **No measurable value**: Skill-activated responses no better than baseline

### 🟡 MARGINAL if:
- **True Positive Rate 70-79%**: Skill activates but unreliably
- **False Positive Rate 10-20%**: Some noise but potentially acceptable
- **Action**: Improve skill description for better semantic matching

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
