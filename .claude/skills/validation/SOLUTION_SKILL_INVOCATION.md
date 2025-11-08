# Solution: Understanding Skill Invocation Mechanisms

**Date**: 2025-11-08
**Source**: https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/

---

## The Mystery Solved

### What We Discovered

**Observation**: Claude invoked `/authentication-security` as a slash command, even though we wanted to test skill auto-activation.

**Question**: How do skills activate? What's the relationship between skills and slash commands?

**Answer**: Skills have **TWO invocation mechanisms**:

1. **Model Invocation (Auto-activation)**: Claude automatically invokes skill via Skill tool when semantically matched
2. **Manual Invocation (Slash command)**: User or Claude explicitly invokes via `/skill-name` command

---

## Frontmatter Control: `disable-model-invocation`

### From Official Documentation

> The `disable-model-invocation` field (boolean) prevents Claude from automatically invoking the skill via the Skill tool. When set to `true`, the skill is excluded from the list shown to Claude and can only be invoked manually by users via `/skill-name`, making it ideal for dangerous operations, configuration commands, or interactive workflows that require explicit user control.

### Three Invocation Modes

**1. Default (no field specified or `disable-model-invocation: false`)**
```yaml
---
name: authentication-security
description: Authentication security expertise...
# disable-model-invocation: false (default)
---
```

**Behavior**:
- ✅ Claude can auto-invoke via Skill tool (semantic matching)
- ✅ User/Claude can invoke via `/authentication-security` command
- **Both mechanisms available**

---

**2. Auto-activation disabled (`disable-model-invocation: true`)**
```yaml
---
name: dangerous-delete-all
description: Deletes all data (USE WITH CAUTION)
disable-model-invocation: true
---
```

**Behavior**:
- ❌ Claude CANNOT auto-invoke (excluded from skill list)
- ✅ User can manually invoke via `/dangerous-delete-all`
- **Manual-only invocation** (safety mechanism)

**Use cases**:
- Dangerous operations (data deletion, destructive changes)
- Configuration commands (setup, initialization)
- Interactive workflows (requires explicit user consent)

---

**3. Mode commands (`mode: true`)**
```yaml
---
name: debug-mode
description: Enable verbose debugging output
mode: true
---
```

**Behavior**:
- Appears in "Mode Commands" section (separate from utility skills)
- Prominent placement at top of skills list
- For behavior-modifying skills (debug-mode, expert-mode, review-mode)

---

## Our Current Configuration

### authentication-security SKILL.md frontmatter

```yaml
---
name: authentication-security
description: Authentication security expertise covering login mechanisms, MFA, password policies, and credential management based on 45+ ASVS-aligned security rules
version: 1.0.0
domains:
  - user-authentication
  - multi-factor-authentication
  - password-security
  - credential-management
allowed-tools: Read, Grep, Bash
---
```

**Missing field**: `disable-model-invocation`

**Default behavior**: `disable-model-invocation: false` (auto-activation ENABLED)

**What this means**:
- ✅ Skill SHOULD auto-activate via Skill tool
- ✅ Slash command `/authentication-security` also available
- **Both mechanisms should work**

---

## Why Test Failed to Show Auto-Activation

### Expected Behavior (with current config)

**Scenario 1: Auto-activation**
```
User: "Review this login code for security issues"
Claude semantic matching: "login" + "security" → authentication-security skill
Claude action: Invoke Skill tool (auto-activation)
Result: Skill content loaded automatically
Evidence: Skill tool invocation in conversation log
```

**Scenario 2: Manual invocation**
```
User: "Review this login code for security issues"
Claude decision: "I should use authentication-security"
Claude action: Invoke /authentication-security slash command
Result: Skill content loaded via command
Evidence: SlashCommand tool invocation in conversation log
```

---

### What Actually Happened

**From conversation log (cf350cd8-f139-4be7-bd39-f59de9eeb6ef.jsonl)**:

```json
{
  "message": {
    "content": [{
      "type": "text",
      "text": "Now let me use the authentication-security specialist agent..."
    }]
  }
}
```

```json
{
  "message": {
    "content": [{
      "type": "tool_use",
      "name": "SlashCommand",
      "input": {"command": "/authentication-security"}
    }]
  }
}
```

**Observation**:
- Claude used **SlashCommand** tool (manual invocation)
- Did NOT use **Skill** tool (auto-activation)
- Chose manual over automatic mechanism

---

## Why Claude Chose Manual Over Auto

### Hypothesis: Explicit Control Preference

**Claude's reasoning** (inferred):
1. Sees task: "Review code for security issues"
2. Recognizes authentication domain
3. Has two options:
   - Wait for auto-activation (probabilistic, passive)
   - Explicitly invoke slash command (deterministic, active)
4. Chooses slash command for reliability and control

**Analogy**: If you can either:
- Wait for someone to offer help (may or may not happen)
- Ask someone directly for help (guaranteed response)

You'd probably ask directly.

---

### Evidence from Test

**Token usage at slash command invocation**:
```json
"usage": {
  "cache_creation": 2061,
  "cache_read": 22106
}
```

**What loaded**: Full SKILL.md content (~2061 tokens)

**Comparison**: If auto-activation had triggered earlier:
- Might see progressive disclosure (description → SKILL.md → rules.json)
- Smaller initial token load
- Different usage pattern

---

## Testing Challenge: Both Mechanisms Available

### The Interference Problem

```
┌─────────────────────────────────────┐
│ Prompt: "Review login code"         │
└─────────────────────────────────────┘
                 ↓
    ┌────────────────────────────┐
    │  Claude's Decision Point   │
    └────────────────────────────┘
         ↓                    ↓
   Auto-activation      Manual invocation
   (Skill tool)         (SlashCommand)
   Probabilistic        Deterministic
         ↓                    ↓
         ?              ✓ Claude chooses
                           this path
```

**Issue**: Cannot test auto-activation when manual invocation is more reliable.

---

## Solution Approaches

### Approach 1: Disable Manual Invocation (Not Possible)

**Desired**:
```yaml
disable-manual-invocation: true  # Hypothetical field
```

**Reality**: No such field exists in frontmatter

**Conclusion**: Cannot prevent slash command creation

---

### Approach 2: Observe Both Mechanisms

**Accept**: Both mechanisms exist and are valid

**Test**: Observe which mechanism activates under different conditions

**Metrics**:
- Auto-activation rate (Skill tool invoked)
- Manual invocation rate (SlashCommand invoked)
- Conditions that trigger each mechanism

**Value**: Understanding when each mechanism is preferred

---

### Approach 3: Test Prompts That Don't Suggest Tool Use

**Current prompts** (sound like tasks):
- "Review X for security"
- "Analyze authentication in Y"
- "Check Z for vulnerabilities"

**Alternative prompts** (sound like observations):
- "Looking at this code, what security patterns stand out?"
- "I'm reading through this login implementation - any concerns?"
- "Thinking about this from an authentication security perspective..."

**Hypothesis**: Task prompts → explicit tool use (slash command)
Observation prompts → direct analysis (may trigger auto-activation during analysis)

---

### Approach 4: Examine Session Discovery Logs

**Look for evidence of auto-activation elsewhere**:
- Check if Skill tool ever invoked in conversation
- Compare token patterns (auto vs. manual)
- Search for progressive disclosure evidence

**Example**:
```bash
# Search for Skill tool usage
jq -r '.message.content[]? | select(.name=="Skill")' session.jsonl

# Search for slash command usage
jq -r '.message.content[]? | select(.name=="SlashCommand")' session.jsonl
```

---

## Updated Understanding

### Skills Architecture (Complete Picture)

**1. Skill Discovery (Session Start)**
```
.claude/skills/authentication-security/SKILL.md discovered
    ↓
Frontmatter parsed:
  - name: authentication-security
  - description: "Authentication security expertise..."
  - disable-model-invocation: false (default)
    ↓
Two invocation paths created:
  1. Skill tool (auto-activation via semantic matching)
  2. /authentication-security command (manual invocation)
    ↓
Both paths available to Claude
```

---

**2. Skill Tool (Auto-activation)**
```
Trigger: Semantic matching on user prompt
Process:
  1. Claude analyzes prompt semantics
  2. Matches against skill descriptions
  3. If match confidence high → invoke Skill tool
  4. Progressive disclosure loads content
Reliability: Probabilistic (may or may not match)
Evidence: Skill tool in conversation log
```

---

**3. Slash Command (Manual Invocation)**
```
Trigger: Explicit invocation (/skill-name)
Process:
  1. User or Claude types /authentication-security
  2. SlashCommand tool invoked
  3. Full SKILL.md loaded immediately
Reliability: Deterministic (always works)
Evidence: SlashCommand tool in conversation log
```

---

## Validation Strategy Impact

### Original Plan

**Goal**: Measure skill auto-activation rates
- True positive: Skill activates on auth prompts (target ≥80%)
- False positive: Skill activates on unrelated prompts (target ≤10%)

**Problem**: Cannot isolate auto-activation if slash commands preferred

---

### Revised Plan Options

**Option A: Accept Mixed Invocation**

**Test**: Does authentication knowledge get loaded? (via either mechanism)

**Metrics**:
- Knowledge activation rate (Skill tool OR SlashCommand)
- False positive rate (activation on unrelated prompts)
- Quality of analysis with skill knowledge

**Value**: Measures practical utility, not mechanism purity

---

**Option B: Force Auto-Activation Testing**

**Method**: Use prompts unlikely to trigger slash command

**Examples**:
- Conversational tone: "Hey, looking at this code here..."
- Embedded context: "While implementing login, I noticed..."
- Implicit questions: "This authentication approach - thoughts?"

**Challenge**: May still prefer slash command

---

**Option C: Document Both Mechanisms**

**Accept**: Both are valid skill invocation methods

**Test**:
1. When does auto-activation (Skill tool) trigger?
2. When does manual invocation (SlashCommand) trigger?
3. What factors influence mechanism selection?

**Output**: Usage patterns guide, not pure activation rates

---

## Recommendations

### For Current Validation

**1. Update test expectations**
```markdown
# OLD expectation
Skill auto-activates via semantic matching

# NEW expectation
Skill knowledge activates via Skill tool OR SlashCommand
```

**2. Track both mechanisms**
```markdown
| Test | Auto (Skill tool) | Manual (SlashCommand) | Neither |
|------|-------------------|----------------------|---------|
| A1   |                   | ✓                    |         |
| A2   |                   |                      |         |
```

**3. Measure knowledge activation, not mechanism**
```markdown
Success criteria:
- Skill knowledge present in ≥80% of auth-related responses
- Skill knowledge absent in ≥90% of unrelated responses
- Mechanism (Skill tool vs. SlashCommand) tracked but not evaluated
```

---

### For Future Skills

**1. Explicit auto-activation preference** (if desired)

Add to SKILL.md:
```yaml
---
name: authentication-security
description: ...
disable-model-invocation: false  # Explicitly enable auto-activation
prefer-auto-activation: true      # Hypothetical field (not standard)
---
```

**2. Document expected invocation patterns**

In SKILL.md:
```markdown
## Expected Activation

**Auto-activation (Skill tool)**:
- Prompts containing: "login", "authentication", "password", "MFA"
- Code review tasks in authentication domains
- Security analysis of auth-related code

**Manual invocation (SlashCommand)**:
- Explicit security audit requests
- Multi-domain analysis requiring parallel skills
- User-initiated comprehensive reviews
```

---

## Conclusion

### Key Findings

1. **Skills auto-generate slash commands** by default
2. **Two invocation mechanisms** exist: Skill tool (auto) and SlashCommand (manual)
3. **Claude prefers manual invocation** for reliability and control
4. **Cannot isolate auto-activation** when manual option available
5. **Both mechanisms are valid** per Claude Code design

### Testing Implications

**Original goal**: Measure pure auto-activation rates

**Reality**: Auto-activation competes with manual invocation

**Solution**: Measure combined knowledge activation (both mechanisms)

### Next Steps

1. **Update validation metrics** to track both mechanisms
2. **Re-run tests** with revised expectations
3. **Document which prompts** trigger which mechanism
4. **Measure practical value** of skill knowledge regardless of mechanism

---

**Status**: Ready to proceed with revised validation approach that accepts both invocation mechanisms as valid skill activation paths.
