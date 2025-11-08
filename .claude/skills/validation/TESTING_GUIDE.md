# Skills Validation Testing Guide

**Purpose**: Step-by-step instructions for executing Phase 0 validation tests.

**Prerequisite**: Read `.claude/skills/SKILLS_VS_AGENTS.md` migration strategy.

---

## Quick Start

```bash
# 1. Ensure skill is in place
ls -la .claude/skills/authentication-security/

# Expected output:
# SKILL.md           (skill definition)
# rules.json -> ../../agents/json/authentication-specialist.json (symlink)

# 2. Start fresh Claude Code session
# Close all existing Claude Code sessions
# Open new terminal in project root

# 3. Verify no interfering skills
ls .claude/skills/
# Expected: Only authentication-security/ and validation/ directories

# 4. Begin Test 1
# See detailed instructions below
```

---

## Test 1: Skill Auto-Activation Validation

**Goal**: Prove authentication-security skill activates on relevant prompts.

**Time Required**: ~45-60 minutes (20 prompts × 2-3 minutes each)

### Pre-Test Checklist

- [ ] Read test prompts: `.claude/skills/validation/test_prompts_auth_skill.md`
- [ ] Open results log: `.claude/skills/validation/VALIDATION_LOG.md`
- [ ] Close all existing Claude Code sessions (fresh start)
- [ ] Verify skill files exist:
  ```bash
  cat .claude/skills/authentication-security/SKILL.md | head -20
  ls -l .claude/skills/authentication-security/rules.json
  ```

### Testing Procedure

#### For Each Test Prompt:

1. **Start Fresh Session** (Important!)
   ```bash
   # Close existing Claude Code session
   # Open new terminal in project root
   # Start new Claude Code session
   ```

2. **Send Exact Prompt**
   - Copy prompt from `test_prompts_auth_skill.md` (e.g., A1: "Review this login function for security issues")
   - Paste into Claude Code **exactly as written**
   - Send message

3. **Observe Response**
   Look for skill activation indicators:
   - ✅ **Explicit mention**: "Using authentication-security skill..."
   - ✅ **Rule references**: "Per ASVS 2.1.1..." or "Rule AUTH-FACTOR-001..."
   - ✅ **Security patterns**: Specific ASVS-aligned guidance
   - ❌ **Generic response**: No skill mention, generic programming advice

4. **Record Results**
   In `VALIDATION_LOG.md`, update the corresponding row:
   ```markdown
   | A1: Review login function | YES | ~450 | Mentioned ASVS 2.1.1, 2.7.1 |
   ```
   Or:
   ```markdown
   | A1: Review login function | NO | ~150 | Generic security advice only |
   ```

5. **Note Token Usage** (if available)
   - Check conversation stats or response length
   - Estimate: ~150 tokens (no skill) vs ~500-700 tokens (with skill)

6. **Save Response** (optional but recommended)
   ```bash
   # Create response archive
   mkdir -p .claude/skills/validation/responses/test1/

   # Copy response to file
   echo "[Response text]" > .claude/skills/validation/responses/test1/A1_response.txt
   ```

7. **Close Session** before next prompt
   - This ensures no context contamination between tests
   - Each prompt should be independent

#### Group A: Authentication-Related (Should Activate)

**Test prompts A1-A10** from `test_prompts_auth_skill.md`

Expected outcome: ≥8/10 prompts activate skill

| Prompt | Expected Activation | Rationale |
|--------|-------------------|-----------|
| A1 | YES | "login function" + "security" → strong auth signal |
| A2 | YES | "password reset" → core auth feature |
| A3 | YES | "hash passwords" → password policy domain |
| A4 | YES | "multi-factor authentication" → explicit MFA |
| A5 | YES | "password length" → password policy |
| A6 | YES | "session management" + "authentication" → dual signal |
| A7 | YES | "JWT token validation" → auth mechanism |
| A8 | YES | "OAuth2 login" → auth mechanism |
| A9 | MAYBE | "API credentials" → credential management (in skill description) |
| A10 | YES | "account lockout" + "failed login" → auth security |

#### Group B: Unrelated Topics (Should NOT Activate)

**Test prompts B1-B10** from `test_prompts_auth_skill.md`

Expected outcome: ≤1/10 prompts activate skill

| Prompt | Expected Activation | Rationale |
|--------|-------------------|-----------|
| B1 | NO | Pure algorithm, no security context |
| B2 | NO | Performance optimization, not auth |
| B3 | NO | Frontend UI, no auth |
| B4 | NO | Compilation error, not security |
| B5 | NO | Infrastructure, not auth |
| B6 | NO | Testing, not auth-specific |
| B7 | NO | Code refactoring, not security |
| B8 | NO | Logging is infrastructure, not auth |
| B9 | MAYBE? | "user profiles" might trigger on "user" keyword |
| B10 | NO | Debugging, not auth |

### Post-Test Analysis

After completing all 20 prompts:

1. **Calculate Metrics**
   ```markdown
   True Positive Rate = (Group A activations) / 10 × 100%
   False Positive Rate = (Group B activations) / 10 × 100%

   Example:
   - Group A: 9/10 activated = 90% true positive ✅
   - Group B: 1/10 activated = 10% false positive ✅
   ```

2. **Token Analysis**
   ```markdown
   Average tokens per activation = (sum of Group A activated token counts) / (number activated)
   Average tokens without activation = (sum of Group B token counts) / 10

   Overhead = Average with - Average without
   ```

3. **Update VALIDATION_LOG.md**
   - Fill in Results Summary section
   - Complete both results tables
   - Write observations

4. **Make Decision**
   - ✅ **PASS**: True positive ≥80%, false positive ≤10%, tokens <500 overhead
   - 🟡 **MARGINAL**: True positive 70-79% OR false positive 10-20%
   - ❌ **FAIL**: True positive <70% OR false positive >20% OR tokens >1000

---

## Test 2: Progressive Disclosure Validation

**Status**: Only run if Test 1 PASSES

**Goal**: Verify staged loading (description → SKILL.md → rules.json)

### Method

**Cannot directly observe internal loading**, but can infer from token usage patterns:

1. **Simple Prompt** (should load SKILL.md only)
   ```
   "What authentication security rules should I follow?"
   ```
   Expected: General guidance from SKILL.md, NO specific rule IDs

2. **Specific Rule Prompt** (should load rules.json)
   ```
   "Show me the ASVS requirements for password hashing algorithms"
   ```
   Expected: Specific rule IDs (AUTH-CRYPTO-001, etc.), detailed requirements

3. **Compare Token Usage**
   - Simple prompt: ~300-500 tokens (SKILL.md guidance)
   - Specific prompt: ~700-1200 tokens (SKILL.md + rules.json)
   - Difference suggests progressive loading

### Evidence to Look For

- ✅ Simple prompts get general guidance without rule IDs
- ✅ Complex prompts get specific rule references
- ✅ Token usage increases with prompt complexity
- ✅ Responses reference rules.json content only when needed

### Decision

- ✅ **PASS**: Clear evidence of staged loading
- 🟡 **MARGINAL**: Partial evidence, unclear pattern
- ❌ **FAIL**: All prompts seem to load everything regardless

---

## Test 3: Value Measurement

**Status**: Only run if Test 1 & 2 PASS

**Goal**: Prove skill adds measurable value

### Method: A/B Comparison

For 5 selected prompts, test with and without skill:

#### Session A: With Skill (Normal)
```bash
# 1. Ensure authentication-security skill present
ls .claude/skills/authentication-security/SKILL.md

# 2. Start Claude Code session
# 3. Send test prompt
# 4. Save response
```

#### Session B: Without Skill (Baseline)
```bash
# 1. Temporarily disable skill
mv .claude/skills/authentication-security .claude/skills/authentication-security.disabled

# 2. Start fresh Claude Code session
# 3. Send SAME test prompt
# 4. Save response
# 5. Re-enable skill
mv .claude/skills/authentication-security.disabled .claude/skills/authentication-security
```

### Test Prompts

Use these 5 from Test 1 Group A:
1. A3: "How should I hash user passwords in Python?"
2. A5: "What's the minimum password length I should enforce?"
3. A6: "Implement session management for user authentication"
4. A7: "Review this JWT token validation code"
5. A10: "Implement account lockout after failed login attempts"

### Comparison Criteria

For each pair of responses, score 0-5 on:

| Criteria | Definition | With Skill | Without Skill |
|----------|-----------|-----------|---------------|
| **ASVS Compliance** | Mentions ASVS standards, version, specific sections | /5 | /5 |
| **Specific Rules** | References CWE/OWASP/rule IDs | /5 | /5 |
| **Avoids Anti-patterns** | No MD5, hardcoded secrets, weak crypto, etc. | /5 | /5 |
| **Edge Cases** | Covers lockout, rate limiting, error handling | /5 | /5 |
| **Complete Solution** | Provides working code + security considerations | /5 | /5 |
| **Total** | | **/25** | **/25** |

### Expected Results

**With Skill** should score:
- ≥5 points higher overall (20% improvement)
- 4-5/5 on "ASVS Compliance" and "Specific Rules"
- Fewer security anti-patterns

**Without Skill** baseline:
- Generic security advice
- May include insecure patterns (MD5, etc.)
- Less comprehensive coverage

### Decision

- ✅ **PASS**: ≥4/5 prompts show ≥20% improvement
- 🟡 **MARGINAL**: 3/5 prompts show 10-19% improvement
- ❌ **FAIL**: <3/5 prompts show improvement

---

## Phase 0 Final Decision

After completing all 3 tests:

### ✅ GO (Proceed to Phase 1)
- Test 1: ≥80% true positive, ≤10% false positive
- Test 2: Evidence of progressive disclosure
- Test 3: ≥20% value improvement
- Token overhead <500 per activation

**Next Step**: Create `input-validation-security` skill, repeat validation

### 🟡 ITERATE (Improve and Re-test)
- Test 1: 70-79% true positive OR 10-20% false positive
- Test 2: Partial evidence
- Test 3: 10-19% improvement
- Token overhead 500-1000

**Next Step**: Improve skill description for better semantic matching

**Example improvements**:
```yaml
# Current description:
description: Authentication security expertise covering login mechanisms, MFA, password policies, and credential management based on 45+ ASVS-aligned security rules

# Enhanced description (if false negatives):
description: Authentication security specialist for login, signup, password management, multi-factor authentication, session handling, credential storage, JWT validation, OAuth flows, and account security based on 45+ ASVS-aligned security rules

# Narrowed description (if false positives):
description: Authentication and login security specialist for password hashing, MFA implementation, session management, and credential protection based on ASVS 2.0 standards
```

### ❌ NO-GO (Pivot Strategy)
- Test 1: <70% true positive OR >20% false positive
- Test 2: No evidence of progressive disclosure
- Test 3: <10% improvement
- Token overhead >1000

**Next Step**: Document findings, consider alternatives:
- Hooks-only approach (100% deterministic)
- Agent-only approach (explicit invocation)
- Hybrid with different architecture

---

## Tips for Effective Testing

### Do:
- ✅ Test in fresh sessions (avoid context contamination)
- ✅ Use exact prompts from test file (consistency)
- ✅ Record detailed observations (qualitative insights)
- ✅ Save actual responses (evidence for analysis)
- ✅ Test at consistent time of day (minimize variability)

### Don't:
- ❌ Test multiple prompts in same session
- ❌ Modify prompts on the fly
- ❌ Cherry-pick results (test ALL prompts)
- ❌ Proceed to next test if previous failed
- ❌ Create more skills before validating first one

### Troubleshooting

**Problem**: Skill never activates
- Check: Is SKILL.md in correct location?
- Check: Is rules.json symlink valid?
- Check: Does description match prompt semantically?

**Problem**: Skill always activates (too many false positives)
- Check: Is description too broad?
- Solution: Narrow description to core domain

**Problem**: Inconsistent activation
- Check: Are prompts sufficiently different?
- Check: Is skill description ambiguous?
- Solution: Test more prompts to establish pattern

---

## Recording Results

### File Locations

- **Test Prompts**: `.claude/skills/validation/test_prompts_auth_skill.md`
- **Results Log**: `.claude/skills/validation/VALIDATION_LOG.md`
- **Testing Guide**: `.claude/skills/validation/TESTING_GUIDE.md` (this file)
- **Responses** (optional): `.claude/skills/validation/responses/test1/`

### Git Workflow

```bash
# After completing tests
git add .claude/skills/validation/VALIDATION_LOG.md
git commit -m "Complete Phase 0 Test 1 validation - [PASS/FAIL/MARGINAL]"

# Include actual responses if saved
git add .claude/skills/validation/responses/
git commit -m "Add test response evidence for validation"
```

---

## Next Steps After Validation

### If Phase 0 Passes
1. Review `.claude/skills/SKILLS_VS_AGENTS.md` Phase 1
2. Select next skill to create (input-validation-security recommended)
3. Repeat validation process for new skill
4. **Do NOT create multiple skills simultaneously**

### If Phase 0 Fails
1. Document findings in VALIDATION_LOG.md
2. Analyze why approach didn't work
3. Discuss alternative strategies:
   - Hooks-only (100% deterministic enforcement)
   - Agent-only (explicit invocation, full control)
   - Hybrid approach (skills for common cases, hooks for guarantees)

---

## Questions or Issues?

If validation results are unclear or unexpected:

1. Document the confusion in VALIDATION_LOG.md observations
2. Save example responses showing the issue
3. Review official Claude Code skills documentation
4. Consider posting in Claude Code community for guidance

**Critical**: Do NOT proceed to creating more skills if validation shows the approach isn't working.
