# Phase 1: Skill Migration - Kickoff Plan

**Status**: ✅ Phase 0 COMPLETE → Starting Phase 1
**Date**: 2025-11-09
**Goal**: Migrate remaining agents to skills (one at a time, validated approach)

---

## Phase 0 Completion Summary

### What We Validated ✅
- **12 comprehensive tests** (7 baseline + 5 isolation)
- **Skills + CLAUDE.md + Agents architecture** validated
- **Task-type dependency** discovered (0% to 100% CLAUDE.md contribution)
- **Probabilistic vs deterministic** activation patterns understood
- **Known issues fixed**: A7 review patterns, A4 timing guard

### Architecture Fortified ✅
- Pre-implementation security guard (file path + keyword detection)
- Expanded review intent patterns (4 categories, no "security" keyword required)
- Reliability ladder (deterministic > manual > probabilistic)
- Deterministic escape hatches documented
- Canonical rule counts (195 rules, 20 domains)
- Evidence-based failure modes table

### Decision: GO TO PHASE 1 ✅
- Activation: 85.7% (6/7) - exceeds 80% target
- False negatives: 14.3% (1/7) - marginal but fixable (FIXED)
- Implementation safety: 100% with CLAUDE.md
- Security impact: HIGH risk without CLAUDE.md (proven)

---

## Phase 1: Migration Strategy

### Core Principle: ONE SKILL AT A TIME

**NOT**: "Create all 12 skills then test"
**YES**: "Create skill → Validate → Learn → Next skill"

### Per-Skill Workflow

```
1. CREATE
   - Copy authentication-security/ structure as template
   - Update SKILL.md with domain-specific content
   - Symlink to compiled rules.json
   - Add slash command
   - Update description for semantic matching

2. VALIDATE (Opportunistic Testing)
   - Run 3-5 test prompts in fresh sessions
   - Check: Activation? ASVS refs? Timing correct?
   - Record results in validation/PHASE_1_TESTS.md
   - Gate: ≥70% activation, no critical failures

3. LEARN
   - What patterns triggered activation?
   - What patterns missed?
   - Any CLAUDE.md pattern updates needed?
   - Document findings in STATUS.md

4. DECIDE
   - ✅ PASS: Proceed to next skill
   - ⚠️ FIX: Update patterns, retest, then proceed
   - ❌ STOP: Reassess if <70% after fixes

5. ITERATE
   - Move to next priority skill
   - Repeat process
```

---

## Migration Priority Order

### Tier 1: High Priority (Start Here)

1. **secrets-management** ⏳ NEXT
   - Rules: 4 rules (SECRET-*)
   - Frequency: HIGH (API keys, credentials everywhere)
   - Risk: CRITICAL (hardcoded secrets = immediate breach)
   - Overlaps: authentication, configuration
   - **Start with this one**

2. **session-management** ⏳
   - Rules: 22 rules (SESSION-*)
   - Frequency: HIGH (every auth system)
   - Risk: CRITICAL (session hijacking, fixation)
   - Overlaps: authentication, JWT

3. **input-validation** ⏳
   - Rules: 6 rules (INPUT-*)
   - Frequency: VERY HIGH (every user input)
   - Risk: CRITICAL (SQL injection, XSS)
   - Overlaps: web-security

### Tier 2: Medium Priority

4. **authorization** ⏳
   - Rules: 13 rules (AUTHZ-*)
   - Overlaps: authentication heavily

5. **jwt-security** ⏳
   - Rules: 4 rules (JWT-*)
   - Overlaps: session-management, authentication

6. **web-security** ⏳
   - Rules: 9 rules (WEB-*)
   - Overlaps: input-validation, cookies

### Tier 3: Lower Priority

7. **cryptography** ⏳
   - Rules: 8 rules (CRYPTO-*)
   - Specialized domain

8. **logging** ⏳
   - Rules: 18 rules (LOG-*)
   - Important but lower risk

9. **configuration** ⏳
   - Rules: 16 rules (CONFIG-*)
   - Overlaps many domains

10. **data-protection** ⏳
    - Rules: 14 rules (DATA-*)
    - Privacy/GDPR focused

### Tier 4: Specialized/Meta

11. **network-security** ⏳ (10 rules)
12. **file-handling** ⏳ (4 rules)
13. **security-research** ⏳ (meta-skill)
14. **comprehensive-security** ⏳ (meta-skill)

---

## First Skill: secrets-management

### Why Start Here?

1. **Small rule set** (4 rules) - easy to validate
2. **Clear triggers** - "api key", "secret", "credential", "password"
3. **High impact** - hardcoded secrets are instant critical vulnerabilities
4. **Frequent use** - appears in almost every codebase
5. **Low overlap** - distinct from authentication (which we've validated)

### Existing Agent

Location: `.claude/agents/secrets-specialist.md`
- Already has compiled rules.json
- Already has CLAUDE.md patterns (lines 236-238)
- Just need to create skill variant

### Creation Checklist

- [ ] Create `.claude/skills/secrets-management/` directory
- [ ] Create `SKILL.md` with activation triggers
- [ ] Add `description` optimized for semantic matching
- [ ] Symlink to `secrets_rules.json`
- [ ] Add slash command `/secrets-management`
- [ ] Update README.md with new skill
- [ ] Test with 3-5 prompts
- [ ] Document results
- [ ] Update STATUS.md

---

## Success Metrics for Phase 1

### Per-Skill Gates
- ✅ Activation rate ≥70% (e.g., 3/5 or 7/10)
- ✅ No critical timing failures (pre-guard should catch)
- ✅ ASVS references present when activated
- ✅ Deterministic escape hatch works (/slash-command)

### Overall Phase 1 Success
- Migrate at least **4 high-priority skills** (Tier 1)
- Maintain **hybrid architecture** (skills + agents)
- Document **patterns that work** vs **patterns that don't**
- Build **institutional knowledge** for future skill creation

### Stop Conditions
- Skill fails validation after fixes (<70% activation)
- False positive rate >20% (activates when shouldn't)
- Diminishing returns (skill adds no value over existing)
- Token costs become prohibitive (measure if visible)

---

## What NOT to Do

❌ **Don't create all 14 skills at once** - Validate incrementally
❌ **Don't skip testing** - Even 3 prompts >> zero prompts
❌ **Don't obsess over perfection** - 70% activation is good enough
❌ **Don't treat gates as hard blockers** - Use judgment
❌ **Don't automate** - Manual testing is realistic for Claude Code

---

## Ready to Start?

**Next Actions**:
1. Create `secrets-management` skill
2. Test with 3-5 prompts (hardcoded API key, credential storage, etc.)
3. Record results
4. Proceed to `session-management` or iterate

**Estimated Effort**:
- Creation: 30 minutes
- Testing: 15 minutes (3-5 fresh sessions)
- Documentation: 15 minutes
- **Total per skill: ~1 hour**

**Phase 1 Timeline**:
- 4 high-priority skills × 1 hour = **4 hours**
- Spread across days/weeks (not all at once)
- Opportunistic testing (when using Claude Code anyway)

---

**Status**: Ready to create `secrets-management` skill

Would you like to proceed with creating the first skill?
