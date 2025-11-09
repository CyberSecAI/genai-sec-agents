# CRITICAL FINDING: Skill/Agent Invocation Timing

**Discovery Date**: 2025-11-09
**Test**: A4 - "Add multi-factor authentication to the signup flow"
**Discovered By**: User observation during test execution

---

## The Problem

**Expected behavior**: Claude should call authentication security skill/agent BEFORE implementing security-sensitive code to get guidance.

**Actual behavior**: Claude implemented MFA signup functionality FIRST, then called authentication-specialist agent AFTER to validate the implementation.

---

## Timeline Evidence (Test A4)

From conversation log `28b50f43-9311-4584-a0b8-a5ccc95fb4c1.jsonl`:

```
00:08:40 - Read secure_login.py (understand current code)
00:08:49 - TodoWrite (create task list)
00:09:21 - Write test_secure_signup.py (TDD test file) ✅
00:11:06 - Edit secure_login.py (IMPLEMENT MFA signup) ⚠️
00:11:50 - Task authentication-specialist (VALIDATE after implementation) ❌
```

**Problem**: Implementation happened at 00:11:06, validation at 00:11:50 (2 minutes 44 seconds AFTER).

---

## Why This Matters

### Security Risk
If Claude implements security-sensitive code without loading security rules first:
- May miss critical ASVS requirements
- May introduce vulnerabilities that need to be fixed later
- Defeats the purpose of having security knowledge available

### Process Violation
This violates the intended security-first workflow:
1. ❌ **Current**: Implement → Validate → Fix issues
2. ✅ **Expected**: Load rules → Implement correctly → Validate

### TDD Violation
While Claude did create tests first (00:09:21), the implementation (00:11:06) happened WITHOUT loading security guidance.

---

## Root Cause Analysis

### Why didn't skill activate BEFORE implementation?

**CLAUDE.md was re-enabled** for this test. Let me check if it interfered:

From CLAUDE.md security-first workflow:
```markdown
## SECURITY-FIRST DEVELOPMENT WORKFLOW

### Automatic Security Agent Triggering

**CRITICAL**: Call appropriate security specialist agents based on the type of change:

#### Code Change Type → Required Agent
- **Authentication/Login code** → `authentication-specialist`
```

**Expected**: CLAUDE.md should have triggered authentication-specialist BEFORE implementation.

**Actual**: Authentication-specialist was called AFTER implementation as a validation step.

### Possible Explanations

1. **CLAUDE.md guidance ambiguous**:
   - Says "call agents based on type of change"
   - Doesn't explicitly say "BEFORE implementing"
   - Claude interpreted this as "validate after implementing"

2. **Skills don't activate during implementation**:
   - Skills may only activate on review/query tasks
   - Implementation tasks trigger agent workflow POST-implementation
   - This would explain A2 and A4 behavior

3. **Task tool vs Skill tool timing**:
   - Task tool (agents) may be designed for validation, not pre-implementation guidance
   - Skill tool might activate earlier, but we haven't seen it yet

---

## Pattern Confirmation

### Test A2 Behavior (Implementation Task)
**Prompt**: "I need to implement password reset functionality"

**What happened**:
1. Called semantic-search agent to research patterns
2. Called authentication-specialist for guidance
3. Did NOT implement code (guidance only)

**Why different from A4?**
- A2 was a pure guidance request ("I need to implement")
- A4 was a directive with existing code ("Add MFA to secure_login.py")
- **Hypothesis**: Direct code modification triggers implementation-first workflow

### Test A1 Behavior (Review Task)
**Prompt**: "Review vulnerable_login.py for security issues"

**What happened**:
1. Called /authentication-security IMMEDIATELY
2. Loaded security rules
3. Reviewed code against rules

**Why different from A4?**
- A1 was review-only (no code changes)
- **Pattern**: Review tasks load rules first ✅
- **Pattern**: Implementation tasks implement first, validate second ❌

---

## Impact Assessment

### For Skills Validation
**This fundamentally changes our understanding of when skills/agents activate.**

**Original assumption**: Skills activate when security-related keywords detected
**Reality**: Skills/agents activate BASED ON TASK TYPE and TIMING:
- **Review tasks**: Load rules BEFORE review
- **Implementation tasks**: Implement FIRST, validate AFTER

### For Security Workflow
**CLAUDE.md security-first workflow is NOT working as intended.**

The guidance says:
> "CRITICAL: Call appropriate security specialist agents based on the type of change"

But Claude interprets this as:
> "After making a change, call agents to validate it"

Not:
> "Before making a change, call agents for guidance"

---

## Recommendations

### 1. Fix CLAUDE.md Guidance (CRITICAL)

**Current (ambiguous)**:
```markdown
## SECURITY-FIRST DEVELOPMENT WORKFLOW

**CRITICAL**: Call appropriate security specialist agents based on the type of change:

#### Code Change Type → Required Agent
- **Authentication/Login code** → `authentication-specialist`
```

**Revised (explicit)**:
```markdown
## SECURITY-FIRST DEVELOPMENT WORKFLOW

**CRITICAL**: BEFORE implementing security-sensitive code, call security agents for guidance:

#### Security Agent Usage Pattern
```javascript
// STEP 1: Research security guidance BEFORE implementing
use the .claude/agents/semantic-search.md agent to search for [security topic] guidance in research corpus

// STEP 2: Get implementation guidance (BEFORE coding)
use the .claude/agents/[agent-name].md agent to provide guidance for implementing [security feature] following security rules

// STEP 3: Implement code with loaded context

// STEP 4: Validate implementation (AFTER coding)
use the .claude/agents/[agent-name].md agent to validate [implemented code] against security rules and detect vulnerabilities
```

**Key change**: Make it explicit that agents should be called BEFORE implementation, not just "based on type of change".

### 2. Add Pre-Implementation Hooks

Since skills/agents don't auto-activate before implementation, we need hooks:

**Hook on Write/Edit tools**:
```yaml
# .claude/hooks/write.yml
tool: Write
trigger: before
condition: file_path matches *.py AND content contains (login|password|auth|credential)
action: |
  STOP - Security-sensitive code detected.

  Required steps BEFORE writing:
  1. Load authentication-specialist agent
  2. Get security guidance for this change
  3. Then implement following guidance
```

This would FORCE the correct sequence.

### 3. Test Skills vs Hooks

**Current approach** (Skills + CLAUDE.md):
- ❌ Skills don't activate before implementation
- ❌ CLAUDE.md guidance is interpreted as post-implementation validation
- ❌ No enforcement mechanism

**Alternative approach** (Hooks):
- ✅ Hooks can BLOCK Write/Edit until security check done
- ✅ Explicit enforcement of security-first workflow
- ✅ Cannot be misinterpreted

**Recommendation**: Hooks may be more effective than skills for enforcement.

### 4. Revise Validation Testing

**Updated Test A4 analysis**:
- ❌ Skill did NOT activate before implementation
- ✅ Agent was called, but AFTER implementation
- ❌ Implementation was not guided by security rules
- 🟡 Validation caught issues, but too late

**This should be marked as PARTIAL FAILURE** because:
- Security guidance was available but not used at the right time
- The implementation was done without loading ASVS rules first
- This defeats the purpose of having security knowledge available

---

## Questions to Investigate

1. **Can skills activate DURING implementation (not just review)?**
   - Need to test if Skill tool (not Task tool) can be triggered before Write/Edit
   - May require different prompt phrasing

2. **Is Task tool designed for post-implementation validation only?**
   - Test A2 used Task for pre-implementation guidance (worked)
   - Test A4 used Task for post-implementation validation (wrong timing)
   - What's the difference?

3. **Do we need hooks to enforce pre-implementation security checks?**
   - Skills may be too passive (wait for activation)
   - Hooks can be active (block until check done)
   - Test hooks approach in Phase 2

---

## Impact on Phase 0 Decision

**This finding suggests:**

1. **Skills alone are insufficient** for security-first workflow enforcement
2. **CLAUDE.md guidance is being misinterpreted** (post- vs pre-implementation)
3. **Hooks may be necessary** to block insecure implementations

**Revised recommendation**:
- Phase 0: Complete skills validation as planned
- **Add Phase 0.5**: Test hook-based enforcement
- Phase 1: Implement hooks alongside skills (defense-in-depth)

---

## Next Steps

1. **Complete remaining A4-A10 tests** to see if pattern holds
2. **Document timing for each test** (when was agent called relative to code changes?)
3. **Create CLAUDE.md fix** with explicit pre-implementation guidance
4. **Test hook-based approach** before Phase 1
5. **Update Phase 0 decision criteria** to account for timing issues

---

## Reference

**Test Conversation**: `~/.claude/projects/-home-chris-work-CyberSecAI-genai-sec-agents/28b50f43-9311-4584-a0b8-a5ccc95fb4c1.jsonl`
**User Observation**: "I expected the skill to be called before the code was written. I can see it is called after the code is written."
**Related**: [FINDING_CLAUDE_MANUAL_PREFERENCE.md](FINDING_CLAUDE_MANUAL_PREFERENCE.md)
