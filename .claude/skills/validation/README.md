# Skills Validation Infrastructure

**Status**: Phase 0 setup COMPLETE - Ready for manual testing
**Created**: 2025-11-08
**Purpose**: Validation-first migration strategy for Claude Code skills

---

## Overview

This directory contains the complete validation infrastructure for testing the **authentication-security** skill before scaling the skills migration strategy.

**Critical principle**: No assumptions, only verified facts based on testing.

---

## What's Been Built

### ✅ Test Framework (Complete)

1. **Test Prompts** ([test_prompts_auth_skill.md](test_prompts_auth_skill.md))
   - 20 carefully designed prompts (10 auth-related, 10 unrelated)
   - Expected activation rates documented
   - Rationale for each prompt provided

2. **Sample Code** ([sample_code/](sample_code/))
   - `vulnerable_login.py`: 15+ intentional security vulnerabilities
   - `secure_login.py`: ASVS 4.0 compliant reference implementation
   - Enables realistic testing with actual code review scenarios

3. **Results Tracking** ([VALIDATION_LOG.md](VALIDATION_LOG.md))
   - Structured templates for recording test results
   - Decision framework (GO/ITERATE/NO-GO)
   - Covers all 3 Phase 0 tests

4. **Testing Guide** ([TESTING_GUIDE.md](TESTING_GUIDE.md))
   - Step-by-step execution instructions
   - How to observe skill activation
   - Decision criteria and troubleshooting

---

## What Happens Next (Manual Testing Required)

### ⏳ Phase 0: Validate Core Assumptions

**YOU MUST COMPLETE THESE TESTS MANUALLY** - They cannot be automated.

#### Test 1: Skill Auto-Activation (Time: ~60 minutes)

**Goal**: Prove authentication-security skill actually activates on relevant prompts.

**How to run**:
1. Read [TESTING_GUIDE.md](TESTING_GUIDE.md#test-1-skill-auto-activation-validation)
2. Run each of the 20 prompts from [test_prompts_auth_skill.md](test_prompts_auth_skill.md) in **fresh Claude Code sessions**
3. Observe if skill activates (look for ASVS references, rule mentions)
4. Record results in [VALIDATION_LOG.md](VALIDATION_LOG.md)

**Success criteria**:
- ✅ True positive rate ≥80% (at least 8/10 Group A prompts activate skill)
- ✅ False positive rate ≤10% (at most 1/10 Group B prompts activate skill)
- ✅ Token overhead <500 per activation
- ✅ Skill activation is observable (mentions rules, ASVS, etc.)

**What to look for when skill activates**:
- Response mentions "authentication-security skill" or references loaded rules
- Cites specific ASVS requirements (2.4.1, 2.2.1, etc.)
- References CWE/OWASP mappings
- Provides ASVS-aligned security guidance

**What happens if skill never activates**:
- ❌ **NO-GO**: Skills approach not viable, pivot to hooks-only or agents-only
- Document findings in VALIDATION_LOG.md
- Discuss alternative strategies

#### Test 2: Progressive Disclosure (Time: ~30 minutes)

**Status**: BLOCKED until Test 1 PASSES

**Goal**: Verify staged loading (description → SKILL.md → rules.json)

**Method**:
- Compare token usage between simple and complex prompts
- Look for evidence of on-demand rule loading
- See [TESTING_GUIDE.md](TESTING_GUIDE.md#test-2-progressive-disclosure-validation)

#### Test 3: Value Measurement (Time: ~90 minutes)

**Status**: BLOCKED until Test 1 & 2 PASS

**Goal**: Prove skill adds measurable value (≥20% improvement)

**Method**:
- A/B comparison: Same prompts with and without skill
- Score responses on ASVS compliance, specificity, completeness
- See [TESTING_GUIDE.md](TESTING_GUIDE.md#test-3-value-measurement)

---

## Decision Gates

### After Test 1: Can We Proceed?

**✅ GO** (True positive ≥80%, false positive ≤10%)
→ Proceed to Test 2

**🟡 ITERATE** (True positive 70-79% OR false positive 10-20%)
→ Improve skill description, re-test

**❌ NO-GO** (True positive <70% OR false positive >20%)
→ Skills approach not viable, pivot strategy

### After All Tests: What's the Path Forward?

**✅ GO - Proceed to Phase 1**
- All 3 tests passed
- Create second skill (input-validation-security)
- Repeat validation for each new skill
- **One skill at a time** - no batch creation

**🟡 ITERATE - Improve and Re-test**
- Marginal results but promising
- Refine skill descriptions
- Optimize for better semantic matching
- Re-run validation

**❌ NO-GO - Pivot Strategy**
- Skills approach doesn't work as expected
- Document why (activation rate, precision, value)
- Consider alternatives:
  - Hooks-only (100% deterministic enforcement)
  - Agents-only (explicit invocation)
  - Hybrid approach

---

## File Structure

```
.claude/skills/validation/
├── README.md                        # This file - overview and next steps
├── TESTING_GUIDE.md                 # Step-by-step testing instructions
├── VALIDATION_LOG.md                # Results tracking and decision records
├── test_prompts_auth_skill.md       # 20 test prompts with rationale
└── sample_code/
    ├── README.md                    # Sample code documentation
    ├── vulnerable_login.py          # 15+ intentional vulnerabilities
    └── secure_login.py              # ASVS 4.0 compliant reference
```

---

## Key Principles

### 1. Validation-First
**No assumptions without proof.**
- Created test framework ✅
- Must now run tests and measure actual behavior ⏳
- Cannot proceed to Phase 1 without validation ⏸️

### 2. Incremental Approach
**One skill at a time.**
- Validate authentication-security FIRST
- Only create second skill if first passes
- Repeat validation for each new skill

### 3. Stop Gates
**STOP if validation fails.**
- <70% true positive → STOP
- >20% false positive → STOP
- No measurable value → STOP
- Document findings and pivot

### 4. Reality Over Assumptions
**Facts, not hopes.**
- Original migration strategy had unvalidated assumptions
- This framework requires proof before scaling
- If skills don't work as expected, that's valuable data too

---

## Quick Start (For Testers)

```bash
# 1. Verify skill is in place
ls -la .claude/skills/authentication-security/

# 2. Read testing guide
cat .claude/skills/validation/TESTING_GUIDE.md

# 3. Read test prompts
cat .claude/skills/validation/test_prompts_auth_skill.md

# 4. Start testing (Test 1)
# - Open fresh Claude Code session
# - Run prompt A1: "Review .claude/skills/validation/sample_code/vulnerable_login.py for security issues"
# - Observe if skill activates
# - Record result in VALIDATION_LOG.md

# 5. Continue with remaining 19 prompts

# 6. Analyze results and make decision
# - Calculate true positive and false positive rates
# - Update VALIDATION_LOG.md with decision
# - If PASS: Proceed to Test 2
# - If FAIL: Document findings and discuss alternatives
```

---

## Success Metrics (To Be Measured)

**DO NOT assume these will be met - TEST and MEASURE:**

| Metric | Target | Rationale |
|--------|--------|-----------|
| True Positive Rate | ≥80% | Skill reliably activates on auth prompts |
| False Positive Rate | ≤10% | Skill doesn't activate on unrelated prompts |
| Token Overhead | <500 avg | Acceptable cost per activation |
| Value Improvement | ≥20% | Measurably better responses vs baseline |

**After measurement**: THEN decide if metrics are acceptable for scaling.

---

## What This Framework Achieves

### Prevents Premature Scaling
- Can't create 20+ skills without proving one works first
- Stops us if approach isn't viable
- Saves time by failing fast if needed

### Provides Evidence-Based Decisions
- Actual activation rates (not guesses)
- Measured token costs (not estimates)
- Quantified value improvement (not assumptions)

### Enables Iteration
- If marginal results, framework guides improvements
- Clear criteria for when to iterate vs. when to pivot
- Structured approach to optimization

### Documents Reality
- Whatever happens, we have data
- If skills work: proof to justify scaling
- If skills don't work: evidence to guide pivot
- Either way: learned something real

---

## Questions or Issues?

If validation results are unclear or unexpected:

1. **Document** in VALIDATION_LOG.md observations section
2. **Save** example responses showing the issue
3. **Review** official Claude Code skills documentation
4. **Discuss** findings before proceeding

**Remember**: The goal is to learn what actually works, not to force a predetermined outcome.

---

## References

- **Migration Strategy**: [.claude/skills/SKILLS_VS_AGENTS.md](..//SKILLS_VS_AGENTS.md)
- **Skill Under Test**: [.claude/skills/authentication-security/SKILL.md](../authentication-security/SKILL.md)
- **Claude Skills Documentation**: https://docs.claude.ai/skills
- **Claude Code Deep Dive**: https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/

---

**Current Status**: Framework complete, waiting for manual test execution.

**Next Action**: Begin Test 1 - Skill Auto-Activation Validation (see [TESTING_GUIDE.md](TESTING_GUIDE.md))
