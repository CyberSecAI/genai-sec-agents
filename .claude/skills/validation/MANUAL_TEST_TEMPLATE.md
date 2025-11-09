# Manual Test Protocol for Skill Validation

**Purpose**: Validate new skills work as expected before migrating next skill
**Method**: Manual execution in fresh Claude Code sessions
**Effort**: ~20 minutes per skill domain

---

## Test Execution Steps

### 1. Prepare Test Prompts
- Create 5-10 prompts for the skill domain
- Mix task types: implementation, query, review
- Document expected behavior

### 2. Run Tests
- Start **fresh Claude Code session** (clear context)
- Run ONE prompt
- **Immediately document results** before running next
- Note: Cannot batch - each session is independent

### 3. Record Results
Use the tracking table below (copy to new file per skill)

### 4. Calculate Metrics
- Activation rate = (Activated correctly / Total prompts) × 100%
- False positives = Prompts that activated when they shouldn't
- Critical failures = Timing issues (like A4) or missing ASVS refs

### 5. Gate Decision
**Proceed to next skill if**:
- ✅ Activation rate ≥ 70% (e.g., 7/10 or 14/20)
- ✅ False positives ≤ 15% (e.g., ≤2/10 or ≤3/20)
- ✅ NO critical failures (timing/missing ASVS)

---

## Test Tracking Template

```markdown
# Skill: [DOMAIN-NAME]
**Date**: YYYY-MM-DD
**Tester**: [Name]
**Total Prompts**: [N]

| # | Prompt | Type | Expected | Activated? | Correct Agent? | ASVS Refs? | Timing OK? | Notes |
|---|--------|------|----------|------------|----------------|------------|------------|-------|
| 1 | "Review session token validation in auth.py" | Review | ✅ session-specialist | YES | session-mgmt | YES | ✅ Before | Perfect |
| 2 | "Add JWT refresh token logic" | Implementation | ✅ Research→Guide | YES | session+jwt | YES | ⚠️ Direct | A4-like timing issue |
| 3 | "What's a secure session timeout?" | Query | ✅ Dual-agent | YES | session+semantic | YES | ✅ Before | Good quality |
| 4 | ... | ... | ... | ... | ... | ... | ... | ... |

**Results**:
- Activation Rate: [X/N] = [X%]
- False Positives: [Y/N] = [Y%]
- Critical Failures: [Z]

**Gate Decision**: ✅ PASS / ⚠️ FIX ISSUES / ❌ FAIL

**Issues Found**:
1. [Description of any problems]
2. [Patterns observed]

**Follow-up Actions**:
- [ ] Fix timing issue in prompt #2
- [ ] Update CLAUDE.md patterns for edge case
- [ ] Document findings in STATUS.md
```

---

## Example: Session Management Skill Test

```markdown
# Skill: session-management
**Date**: 2025-11-09
**Tester**: Claude
**Total Prompts**: 10

| # | Prompt | Type | Expected | Activated? | Correct Agent? | ASVS Refs? | Timing OK? | Notes |
|---|--------|------|----------|------------|----------------|------------|------------|-------|
| 1 | "Review session token validation" | Review | session-specialist | ✅ YES | ✅ YES | ✅ YES | ✅ YES | V3.2.1 cited |
| 2 | "Add session timeout to login.py" | Implementation | Research→Guide | ✅ YES | ✅ YES | ✅ YES | ⚠️ DIRECT | Pre-guard caught it |
| 3 | "What's secure session duration?" | Query | Dual-agent | ✅ YES | ✅ YES | ✅ YES | ✅ YES | OWASP + ASVS |
| 4 | "Implement session fixation protection" | Implementation | Research→Guide | ✅ YES | ✅ YES | ✅ YES | ✅ YES | V3.2.2 cited |
| 5 | "Review logout() function" | Review | session-specialist | ❌ NO | ❌ NO | ❌ NO | N/A | Pattern gap! |
| 6 | "Store session in Redis" | Implementation | Research→Guide | ✅ YES | ✅ session+config | ✅ YES | ✅ YES | Multi-domain |
| 7 | "Session hijacking prevention?" | Query | Dual-agent | ✅ YES | ✅ YES | ✅ YES | ✅ YES | Good |
| 8 | "Add remember-me cookie" | Implementation | Research→Guide | ✅ YES | ✅ session+cookie | ✅ YES | ⚠️ DIRECT | Pre-guard caught |
| 9 | "Review session.create() security" | Review | session-specialist | ✅ YES | ✅ YES | ✅ YES | ✅ YES | V3.3.1 cited |
| 10 | "What's CSRF protection for sessions?" | Query | Dual-agent | ✅ YES | ✅ YES | ✅ YES | ✅ YES | Excellent |

**Results**:
- Activation Rate: 9/10 = 90% ✅
- False Positives: 0/10 = 0% ✅
- Critical Failures: 1 (prompt #5 - "logout" not in review patterns)

**Gate Decision**: ✅ PASS (with minor fix)

**Issues Found**:
1. Prompt #5: "Review logout()" didn't trigger - needs pattern update
2. Prompts #2, #8: Pre-implementation guard working correctly
3. Overall: Strong activation, good ASVS coverage

**Follow-up Actions**:
- [x] Add "logout|signout" to review patterns in CLAUDE.md
- [ ] Document #5 as false negative in next validation report
- [ ] Update STATUS.md with 90% activation rate
```

---

## Quick Reference: What to Track

**Must Track**:
1. ✅ Did skill/agent activate when expected?
2. ✅ Were ASVS references included?
3. ✅ Was timing correct (research before implementation)?

**Nice to Track**:
- Which agent(s) activated
- Quality of guidance
- Token usage (if visible)
- User experience notes

**Don't Obsess Over**:
- Exact wording of responses
- Minor variations in citations
- Perfect reproduction across sessions

---

## Practical Tips

1. **Keep it simple**: 5-10 prompts is enough to spot patterns
2. **Fresh sessions**: Don't run tests in same session (context pollution)
3. **Document immediately**: Results fade fast, note right away
4. **Pattern recognition**: Looking for systematic issues, not perfection
5. **Gate is guidance**: 70%/15% are guidelines, not hard rules
6. **Use Phase 0 as baseline**: We already have 12 test results to compare

---

## When to Skip Testing

**Skip detailed testing if**:
- Domain is similar to tested domain (e.g., auth → authz overlap)
- Just updating existing skill (not net new)
- Low-risk domain (e.g., logging vs authentication)

**Always test**:
- First 2-3 skills (establish baseline)
- High-risk domains (auth, crypto, secrets)
- After major CLAUDE.md pattern changes

---

**Reality**: We're validating an AI system's behavior, not testing deterministic code. Manual spot-checking with clear gate criteria is more realistic than automated test suites.
