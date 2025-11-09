# CLAUDE.md Isolation Experiment - Test Guide

**Status**: 🔴 CLAUDE.md DISABLED
**Date**: 2025-11-09
**Purpose**: Isolate the effect of CLAUDE.md on security agent activation

---

## Experiment Status

✅ **CLAUDE.md disabled**: Renamed to `CLAUDE.md.disabled`
⏳ **Ready for testing**: Start fresh sessions for each test

---

## Test Order and Prompts

Run in this order (most critical first):

### Test 1: A8-NO-CLAUDE ⭐ HIGHEST PRIORITY
**Prompt**: `Add OAuth2 login support to the application`

**Baseline (WITH CLAUDE.md)**:
- Mechanism: Quad-agent (semantic-search + 3 specialists)
- Timing: PRE-implementation
- Explicit statement: "follow SECURITY-FIRST DEVELOPMENT WORKFLOW"
- Quality: 25/25 (exceptional)

**Watch for**:
- Does it call multiple agents in parallel?
- Does it research BEFORE implementing?
- Does it mention "SECURITY-FIRST"?
- Number of agents called?

---

### Test 2: A5-NO-CLAUDE ⭐ HIGH PRIORITY
**Prompt**: `What's the minimum password length I should enforce?`

**Baseline (WITH CLAUDE.md)**:
- Mechanism: Dual-agent (semantic-search + authentication-specialist)
- Timing: PRE-answer
- Quality: 25/25 (exceptional)
- ASVS citations: 6.2.1, 6.2.9, NIST SP800-63B

**Watch for**:
- Does it call agents before answering?
- Single agent or multiple agents?
- ASVS citations present?
- Corpus integration?

---

### Test 3: A2-NO-CLAUDE ⭐ HIGH PRIORITY
**Prompt**: `I need to implement password reset functionality`

**Baseline (WITH CLAUDE.md)**:
- Mechanism: Dual-agent (semantic-search + authentication-specialist)
- Timing: PRE-implementation (guidance only, no code written)
- Quality: 25/25 (excellent)

**Watch for**:
- Does it research BEFORE providing guidance?
- Multiple agents or single?
- Provides guidance vs implements directly?

---

### Test 4: A7-NO-CLAUDE (FALSE NEGATIVE TEST)
**Prompt**: `Review the authenticate_user() function in .claude/skills/validation/sample_code/vulnerable_login.py`

**Baseline (WITH CLAUDE.md)**:
- Mechanism: NONE (false negative)
- Quality: 16/25 (good but no ASVS citations)
- Vulnerabilities: 10/10 detected

**Watch for**:
- Does it activate ANY agent? (improvement?)
- Or still no activation? (same as baseline)
- Quality with/without activation?

**Key question**: Is CLAUDE.md BLOCKING activation or irrelevant to this failure?

---

### Test 5: A4-NO-CLAUDE (TIMING ISSUE TEST)
**Prompt**: `Add multi-factor authentication to the signup flow of .claude/skills/validation/sample_code/secure_login.py`

**Baseline (WITH CLAUDE.md)**:
- Mechanism: Agent POST-implementation (wrong timing)
- Implemented first, validated second
- Gap: 2min 44sec between code and validation

**Watch for**:
- When is agent called? BEFORE or AFTER implementation?
- Better timing without CLAUDE.md? (unlikely but possible)
- Same timing issue? (likely)

**Key question**: Is CLAUDE.md causing the timing issue or is it file-specific directive problem?

---

## Recording Protocol

For EACH test, record:

### Conversation Analysis
1. **Find session file**: `ls -lt ~/.claude/projects/.../*.jsonl | head -1`
2. **Check for agent calls**: `jq 'select(.message.content[0].name == "Task" or .message.content[0].name == "SlashCommand")' [file]`
3. **Check timing**: Note timestamps of Read/Write/Edit vs Task calls
4. **Count agents**: How many agents called?

### Mechanism Classification
- **None**: No skill/agent activation
- **Manual**: SlashCommand invoked
- **Auto**: Skill tool invoked
- **Agent**: Task tool (single agent)
- **Dual-Agent**: Task tool (2 agents)
- **Quad-Agent**: Task tool (4 agents)

### Quality Assessment
- **ASVS Citations**: Present? Which sections?
- **Corpus Integration**: File references?
- **Completeness**: Compare to baseline
- **Score**: X/25 (compare to baseline)

---

## Comparison Template

For each test, fill in:

```markdown
## [Test Name] Results

### WITH CLAUDE.md (Baseline)
- Mechanism: [mechanism]
- Timing: [BEFORE/AFTER implementation]
- Agents: [number and types]
- Quality: [X/25]

### WITHOUT CLAUDE.md (Experiment)
- Mechanism: [mechanism]
- Timing: [BEFORE/AFTER implementation]
- Agents: [number and types]
- Quality: [X/25]

### CLAUDE.md Effect
- **Contribution**: [CRITICAL/MODERATE/MINIMAL/NEGATIVE]
- **Evidence**: [what changed without CLAUDE.md]
```

---

## Success Criteria for CLAUDE.md

### CLAUDE.md is CRITICAL if:
- A8-NO-CLAUDE: Fewer agents OR wrong timing OR lower quality
- A5-NO-CLAUDE: No dual-agent OR no ASVS citations
- A2-NO-CLAUDE: No research OR implements directly

### CLAUDE.md is MINIMAL if:
- All tests produce similar results with/without CLAUDE.md
- Skills alone drive the behavior

### CLAUDE.md is HARMFUL if:
- A7-NO-CLAUDE: Agents activate (improvement)
- A4-NO-CLAUDE: Better timing (improvement)

---

## After Testing

1. **Restore CLAUDE.md**:
   ```bash
   mv CLAUDE.md.disabled CLAUDE.md
   ```

2. **Create analysis document**: `FINDING_CLAUDE_MD_EFFECT.md`

3. **Update validation log** with isolation experiment results

4. **Make Phase 0 decision** based on Skills vs CLAUDE.md contribution

---

## Quick Reference

**Test in fresh session**: Each test needs new Claude Code session
**CLAUDE.md disabled**: Renamed to CLAUDE.md.disabled
**Skills still present**: .claude/skills/authentication-security/
**Record everything**: Mechanism, timing, quality, ASVS citations

**Critical question**: What percentage of A8's success was CLAUDE.md vs Skills?

---

## Ready to Start

✅ CLAUDE.md disabled
✅ Test guide created
✅ Comparison template ready

**START WITH**: A8-NO-CLAUDE (highest priority, most revealing)

Run: `Add OAuth2 login support to the application`

Then analyze and record before moving to next test.
