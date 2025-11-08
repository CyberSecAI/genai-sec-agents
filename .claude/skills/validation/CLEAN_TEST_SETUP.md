# Clean Test Setup - Skill Activation Only

**Problem Identified**: CLAUDE.md instructs Claude to explicitly call agents, which interferes with testing **skill auto-activation**.

**Solution**: Temporarily disable CLAUDE.md during skill validation tests.

---

## Issue Discovered (2025-11-08)

### Test A1 Initial Run - What Happened

**Prompt**: "Review this login function for security issues"

**Expected**: authentication-security skill auto-activates

**Actual**: Skill did NOT activate, but Claude referenced security workflow from CLAUDE.md:
- "Research security guidance using semantic-search agent"
- "Call authentication-specialist agent"
- "Identify vulnerabilities against OWASP/ASVS"

**Root Cause**: CLAUDE.md contains this instruction:
```markdown
## SECURITY-FIRST DEVELOPMENT WORKFLOW

### Automatic Security Agent Triggering

**When code contains these patterns, IMMEDIATELY call the specified agent:**

- Authentication/Authorization code → authentication-specialist
- Input/Output processing → input-validation-specialist
- etc.
```

This causes Claude to **explicitly invoke agents** rather than letting **skills auto-activate**.

**Result**: Cannot test if skills work because CLAUDE.md overrides the skill mechanism.

---

## Clean Test Environment Setup

### Step 1: Disable CLAUDE.md

```bash
# Temporarily rename CLAUDE.md
mv CLAUDE.md CLAUDE.md.disabled

# Verify it's disabled
git status  # Should show CLAUDE.md as deleted
```

### Step 2: Verify Skills Are Still Present

```bash
# Skills should still be active
ls -la .claude/skills/authentication-security/

# Expected output:
# SKILL.md
# rules.json -> ../../agents/json/authentication-specialist.json
```

**Important**: Skills are discovered from `.claude/skills/`, NOT from CLAUDE.md. Disabling CLAUDE.md removes the explicit agent-calling instructions but leaves skills intact.

### Step 3: Start Fresh Claude Code Session

```bash
# Close all existing Claude Code sessions
# Open new terminal
# Navigate to project
cd /home/chris/work/CyberSecAI/genai-sec-agents

# Start new Claude Code session
# This ensures clean discovery without CLAUDE.md influence
```

---

## Testing Protocol (Clean Environment)

### Test A1 (Revised): Review Vulnerable Login Code

**Prompt** (exact):
```
Review .claude/skills/validation/sample_code/vulnerable_login.py for security issues
```

### What to Observe

**✅ Skill ACTIVATED if response shows:**
- Explicit mention of "authentication-security skill" or "loaded skill"
- Direct references to ASVS sections (2.4.1, 2.2.1, etc.)
- References to the 45+ authentication rules
- Security patterns from SKILL.md content
- **WITHOUT** explicit agent calls ("calling authentication-specialist agent...")

**❌ Skill DID NOT activate if response shows:**
- Generic security advice
- No ASVS or rule references
- Asks for clarification
- Suggests calling agents explicitly (this would mean CLAUDE.md is still active)

**🤔 Ambiguous if:**
- Good security advice but unclear if from skill or base Claude knowledge
- ASVS references present but no explicit skill mention

### How to Confirm Skill Activation

**Progressive Disclosure Evidence:**

1. **Description loaded** (~50 tokens):
   - Claude knows there's an authentication skill
   - May mention it in passing

2. **SKILL.md loaded** (~500 tokens):
   - References ASVS standards
   - Mentions authentication security patterns
   - Shows awareness of 45+ rules

3. **rules.json loaded** (~2000 tokens):
   - Specific rule IDs (AUTH-CRYPTO-001, AUTH-FACTOR-001, etc.)
   - Detailed ASVS mappings
   - Comprehensive vulnerability detection

**Check token usage** in response metadata to estimate what loaded.

---

## Expected Behavior Comparison

### WITH CLAUDE.md (Explicit Agent Calls)

**User**: "Review this login function for security issues"

**Claude Response**:
```
Based on the CLAUDE.md security-first workflow, when analyzing
authentication code I should:

1. Research security guidance using semantic-search agent
2. Call authentication-specialist agent to validate against 45+ rules
3. Identify vulnerabilities against OWASP/ASVS

Let me call the authentication-specialist agent...
```

**Result**: Agent explicitly invoked (not skill auto-activation)

---

### WITHOUT CLAUDE.md (Skill Auto-Activation)

**User**: "Review .claude/skills/validation/sample_code/vulnerable_login.py for security issues"

**Claude Response (if skill activates)**:
```
I'll review this login implementation for security issues.
[reads vulnerable_login.py]

This code has multiple critical authentication security vulnerabilities:

1. **Weak Password Hashing (ASVS 2.4.1)**
   - Uses MD5 which is cryptographically broken
   - Recommendation: Use bcrypt or argon2

2. **SQL Injection Risk (ASVS 5.1.1)**
   - String concatenation in queries
   - Recommendation: Use parameterized queries

[... continues with ASVS-aligned analysis ...]
```

**Key difference**:
- ASVS references appear naturally in analysis
- No explicit "calling agent" language
- Knowledge appears to come from loaded skill context

**Claude Response (if skill does NOT activate)**:
```
I'll review this login code.
[reads vulnerable_login.py]

Issues I see:
- MD5 is weak, use bcrypt instead
- SQL injection vulnerability from string concatenation
- No rate limiting

[... generic security advice without ASVS references ...]
```

---

## Test Data Collection

### Record for Each Test

```markdown
**Test**: A1
**Prompt**: "Review .claude/skills/validation/sample_code/vulnerable_login.py for security issues"
**Environment**: CLAUDE.md disabled
**Session**: [fresh/continued]

**Skill Activated?**: YES / NO / UNCLEAR

**Evidence**:
- ASVS references: [list sections mentioned]
- Rule IDs: [list any AUTH-* rule IDs]
- Skill mention: [direct quote if skill mentioned]
- Token usage: [input/output tokens from log]

**Vulnerabilities Detected**: __/15
[List which of the 15 intentional vulns were found]

**Assessment**: STRONG / MARGINAL / WEAK activation
```

---

## Re-Enabling CLAUDE.md After Tests

### After Completing All Validation Tests

```bash
# Restore CLAUDE.md
mv CLAUDE.md.disabled CLAUDE.md

# Verify restoration
git status  # Should show CLAUDE.md as unmodified

# Discard git changes if needed
git restore CLAUDE.md
```

**Important**: Don't commit the disabled state - this is temporary for testing only.

---

## Why This Matters

### Testing Skills vs. Agent Workflow

**Skills (what we're testing)**:
- Auto-activate based on semantic matching
- Progressive disclosure (description → SKILL.md → rules.json)
- Probabilistic activation
- Goal: Prove they work before scaling

**Agents (what CLAUDE.md triggers)**:
- Explicit invocation via Task tool
- Full rule loading every time
- Deterministic execution
- Already proven to work

**Interference**: CLAUDE.md causes Claude to use agents (explicit) instead of testing if skills (automatic) work.

**Clean test**: Remove CLAUDE.md → Only skills remain → Can measure skill activation rate

---

## Test Sequence (Clean Environment)

### Phase 1: Skill Activation Baseline (CLAUDE.md disabled)

1. Test A1-A10 (should activate skill)
2. Test B1-B10 (should NOT activate skill)
3. Record true positive / false positive rates
4. Measure token overhead
5. **Decision**: Do skills work well enough?

### Phase 2: Value Comparison (Optional)

**Test A**: With skills enabled, CLAUDE.md disabled
- Measure skill-based responses

**Test B**: With skills disabled (move .claude/skills/ temporarily)
- Measure baseline Claude responses

**Compare**: Is skill activation providing value?

### Phase 3: Restore Full Workflow

- Re-enable CLAUDE.md
- Document final findings
- Decide on production configuration (skills + agents + hooks)

---

## Expected Outcomes

### Scenario 1: Skills Work Well

**Results**:
- True positive ≥80% (skills activate on auth prompts)
- False positive ≤10% (don't activate on unrelated prompts)
- ASVS references consistent
- Value improvement measurable

**Decision**: ✅ GO to Phase 1 (create more skills)

**Production Config**: Skills + Hooks + Agents (three-layer defense)

---

### Scenario 2: Skills Work Marginally

**Results**:
- True positive 70-79% (inconsistent activation)
- False positive 10-20% (some noise)
- ASVS references sometimes present
- Marginal value improvement

**Decision**: 🟡 ITERATE (improve skill descriptions, re-test)

**Production Config**: TBD based on iteration results

---

### Scenario 3: Skills Don't Work

**Results**:
- True positive <70% (rarely activate)
- False positive >20% (activate randomly)
- No consistent ASVS references
- No measurable value

**Decision**: ❌ NO-GO (skills approach not viable)

**Production Config**: Hooks + Agents only (skip skills)

---

## Current Status

**CLAUDE.md**: ✅ Disabled (ready for clean testing)
**Skills**: ✅ Present (authentication-security)
**Sample Code**: ✅ Ready (vulnerable_login.py)
**Test Framework**: ✅ Complete

**Next Action**: Run Test A1 in fresh Claude Code session and observe skill activation behavior without CLAUDE.md interference.

---

## Notes for Testers

### Key Differences to Watch

**With CLAUDE.md active**:
- Claude says "I should call the authentication-specialist agent"
- Explicit Task tool invocation
- Agent framework visible

**With CLAUDE.md disabled, skills active**:
- Claude naturally references ASVS in analysis
- No explicit agent calls
- Skill knowledge appears integrated in response

**With both disabled (baseline)**:
- Generic security advice
- No ASVS references
- Base Claude knowledge only

### Token Budget Awareness

**Skill Discovery** (happens once per session):
- Small overhead (~50-100 tokens per skill)
- Happens at session start

**Skill Activation** (happens per relevant prompt):
- Variable overhead based on progressive disclosure
- Target: <500 tokens per activation

**Full Agent Call** (CLAUDE.md triggers):
- Higher overhead (~2000+ tokens)
- Guaranteed full rule loading

**Clean test measures skill overhead only**, without agent call overhead.
