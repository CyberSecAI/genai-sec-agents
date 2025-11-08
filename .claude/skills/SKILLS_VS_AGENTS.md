# Skills vs Agents: Architecture Comparison

## Quick Decision Matrix

| Use Case | Use | Why |
|----------|-----|-----|
| Parallel execution of multiple security checks | **Agents** | Agent SDK supports parallel sub-agent execution |
| Understanding what security capabilities exist | **Skills** | Progressive disclosure, human-readable |
| Automated pre-commit validation hooks | **Agents** | Programmatic invocation via Agent SDK |
| Composing multiple security domains | **Skills** | Skills designed for composition |
| CI/CD security scanning | **Agents** | Fast, parallel execution |
| Learning secure coding patterns | **Skills** | Includes examples and detailed guidance |
| Multi-step security workflow | **Both** | Skills define workflow, agents execute steps |

## Core Architectural Principles

### How Skills Actually Work (Automatic Context Injection)

**Skills provide automatic context management out-of-the-box:**

1. **Discovery Phase** (Conversation Start, ~30-50 tokens/skill)
   - Claude scans `.claude/skills/` (project) and `~/.claude/skills/` (personal)
   - Reads YAML frontmatter from each SKILL.md
   - Loads: `name` + `description` into catalog
   - Result: Claude knows what capabilities exist

2. **Semantic Matching** (Request Analysis, ~0 tokens)
   - User request: "Review authentication code"
   - Claude compares request against skill descriptions
   - Pattern matching: "authentication" → authentication-security skill
   - Decision: Activate matched skill

3. **Context Injection** (Dynamic Loading, skill-dependent tokens)
   - Claude reads full SKILL.md content
   - Loads instructions, rules, guidelines
   - Additional files (rules.json) loaded on-demand
   - Context: User request + Skill instructions

4. **Application** (Response Generation)
   - Claude applies skill knowledge to user request
   - Follows security rules from loaded skill
   - Returns analysis per skill structure

**Key insight:** Skills automatically activate via semantic matching - no manual invocation needed.

### Skills are Useful For:
- **Automatic context activation** based on request content
- **Interactive workflows** where Claude decides what knowledge to apply
- **Progressive disclosure** (load descriptions first, content on-match)
- **Token efficiency** (small discovery cost, larger on activation)
- **Zero cognitive load** (no need to remember which skill to call)

### Agents are Better For:
- **Explicit parallel execution** (multiple sub-agents via Agent SDK)
- **Programmatic invocation** (CI/CD, pre-commit hooks, automated pipelines)
- **Background execution** with monitoring and output retrieval
- **Deterministic workflows** (user controls exactly which agents run)
- **Orchestration patterns** (main agent delegates to specialist sub-agents)

**Rule of Thumb:** Skills and agents are complementary, not competing. Use skills for automatic context injection in interactive workflows. Use agents for explicit parallel execution in programmatic workflows.

---

## How Skills Solve Automatic Context Management

**Skills already provide intelligent, automatic context injection:**

### Real-World Example: Authentication Review

**With Agents (Manual):**
```javascript
// User: "Fix authentication vulnerability in src/auth/login.py"
// Developer must explicitly invoke:
use authentication-specialist agent to review src/auth/login.py
// Problem: Developer must know which agent to call
```

**With Skills (Automatic):**
```javascript
// User: "Fix authentication vulnerability in src/auth/login.py"
// Claude automatically:
1. Matches "authentication vulnerability" → authentication-security skill
2. Loads authentication-security/SKILL.md (~2-5k tokens)
3. Applies 45 authentication rules during analysis
4. Returns security-aware recommendations
// Benefit: Zero manual invocation, Claude decides what knowledge to apply
```

### How Semantic Matching Works

**The `description` field is the activation trigger:**

```yaml
# authentication-security/SKILL.md
---
name: authentication-security
description: Authentication security expertise covering login mechanisms,
  MFA, password policies, and credential management based on 45+ ASVS-aligned
  security rules
---
```

**Semantic matching examples:**
- User: "Review this login code" → Match: "login mechanisms"
- User: "Check password hashing" → Match: "password policies"
- User: "Validate MFA implementation" → Match: "MFA"
- User: "Analyze authentication flow" → Match: "Authentication security"

**Claude autonomously activates the skill when request semantically matches description.**

### Progressive Disclosure in Action

**How skills achieve token efficiency:**

```
Session Start (All Skills)
├─ authentication-security: small cost (name + description)
├─ session-management-security: small cost
├─ secrets-management: small cost
├─ [... 12 more skills]: minimal per-skill cost
└─ Total Discovery Cost: modest upfront investment

User Request: "Review authentication code"
├─ Semantic Match: authentication-security skill
├─ Load Full Skill: authentication-security/SKILL.md (moderate cost)
├─ On-Demand: Load rules.json if needed (larger cost)
└─ Total Cost: discovery + skill content + (optional rules)

Compare to Agents (Manual Invocation)
├─ No discovery phase (user must know agent exists)
├─ Load Full Agent: authentication-specialist.md (moderate cost)
├─ Load Rules: json/authentication-specialist.json (large cost)
└─ Total Cost: all context loaded upfront, no progressive loading
```

**Skills advantage:** Only load full content when semantically matched to request.

### Multi-Skill Composition

**Skills can auto-activate together for complex requests:**

```javascript
// User: "Implement secure JWT authentication with environment-based secrets"

// Claude automatically activates:
1. authentication-security skill → "authentication" match
2. session-management-security skill → "JWT" match
3. secrets-management skill → "secrets" match

// Result: 3 skills loaded, all relevant knowledge applied
// Cost: discovery overhead + content for each activated skill
// Compare to: Manually invoking multiple agents via Agent SDK
```

**Key Takeaway:** Skills automatically solve the context management problem through semantic matching and progressive disclosure. No additional infrastructure needed.

---

## Architecture Comparison

### Agents (Current, `.claude/agents/*.md`)

**Purpose:** Task execution via Claude Code Task system

**Structure:**
```markdown
---
name: authentication-specialist
description: Brief description
tools: Read, Grep, Bash
---

[All instructions and context loaded upfront]
```

**Invocation:**
```javascript
use the authentication-specialist agent to analyze src/auth/login.py
```

**Characteristics:**
- ✅ **Parallel Execution**: Multiple sub-agents run simultaneously
- ✅ **Programmatic**: Explicit invocation via Agent SDK
- ✅ **Fast**: Optimized for automated execution
- ✅ **Validated**: Existing workflow, proven in production
- ✅ **On-Demand Loading**: References JSON rule files, loads when needed
- ✅ **Composition**: comprehensive-security-agent includes all specialist rules
- ⚠️ **Less discoverable**: Harder to understand capabilities without reading agent files

**Token Usage:**
```
Initial load: moderate (agent instructions + frontmatter)
On-demand: Load JSON rule file when needed (larger cost)
Total: varies depending on whether rules are loaded
```

**Best For:**
- Automated security validation
- CI/CD integration
- Parallel security scanning
- Pre-commit hooks
- Programmatic invocation

---

### Skills (New, `.claude/skills/*/SKILL.md`)

**Purpose:** Progressive context loading and skill composition

**Structure:**
```markdown
# .claude/skills/authentication-security/SKILL.md
---
name: authentication-security
description: Detailed description
version: 1.0.0
domains: [user-authentication, mfa, passwords]
tools: Read, Grep, Bash
---

# Authentication Security Skill

## Skill Capabilities
[Overview - loads first]

## Usage Patterns
[When to use - loads second]

## Examples
[Code samples - loads on demand]

## Integration
[Composition with other skills - loads on demand]
```

**Invocation:**
```
Activate authentication-security skill and analyze src/auth/login.py
```

**Characteristics:**
- ✅ **Progressive Disclosure**: Load context incrementally
- ✅ **Discoverable**: Clear capabilities and usage patterns
- ✅ **Composable**: Skills reference and build on each other
- ✅ **Rich Examples**: Concrete code snippets included
- ✅ **Human-Readable**: Designed for understanding
- ✅ **Automatic Activation**: Semantic matching on description
- ✅ **Token Efficient**: Small cost until activated

**Token Usage:**
```
Initial load: small (name + description during discovery)
On-activation: moderate (full SKILL.md content)
On-demand: larger (full rules via JSON symlink if needed)
Total if all loaded: varies based on what's needed
Advantage: Can provide guidance without loading full rule set
```

**Best For:**
- Interactive security guidance
- Learning secure coding patterns
- Multi-domain security analysis
- Understanding security capabilities
- Composing security workflows
- Automatic context injection

---

## Hybrid Architecture (Current Implementation)

**We use BOTH skills and agents in a two-layer architecture:**

```
.claude/
├── skills/              # Skills layer: Auto-Discovery + Progressive Loading
│   └── authentication-security/
│       ├── SKILL.md                    # Progressive disclosure entry point
│       ├── rules.json                  # Symlink to agent JSON
│       └── examples/                   # Code examples (future)
│
└── agents/              # Agents layer: Explicit Execution + Parallelism
    ├── authentication-specialist.md    # Task execution
    └── json/
        └── authentication-specialist.json  # Compiled rules
```

### Layer Interaction

**Scenario 1: Interactive Learning (Skills)**
```
User: "What are your authentication security capabilities?"

Claude: [Automatically activates authentication-security skill]
→ Progressive disclosure: Overview → Capabilities → Examples
→ Token-efficient: Only loads what's needed (~5k tokens)
```

**Scenario 2: Automated Validation (Agents)**
```
Pre-commit hook: Validate authentication changes

Task System: [Explicitly invokes authentication-specialist agent]
→ Fast: Loads full context immediately
→ Parallel: Runs with other agents simultaneously
→ Programmatic: No semantic matching needed
```

**Scenario 3: Comprehensive Analysis (Hybrid)**
```
User: "Review authentication system comprehensively"

Claude: [Automatically activates multiple skills]
1. authentication-security skill → Login mechanisms
2. session-security skill → Session handling
3. secrets-management skill → Credential storage

[Skills provide context, then Claude can optionally invoke parallel agents]
→ authentication-specialist agent
→ session-management-specialist agent
→ secrets-specialist agent

[Synthesizes results from all three]
```

---

## When to Use Each Approach

### Use Skills When:

1. **Interactive Workflows**
   - User doesn't know which capability they need
   - Claude should auto-detect relevant security domains
   - Progressive learning and exploration
   - Token efficiency is important

2. **Automatic Context Injection**
   - Semantic matching on user requests
   - Multi-skill composition for complex requests
   - Zero manual invocation needed

3. **Discovery and Learning**
   - Understanding security capabilities
   - Exploring secure coding patterns
   - Getting examples and guidance

### Use Agents When:

1. **Programmatic Invocation**
   - CI/CD security scanning
   - Pre-commit validation hooks
   - Scheduled security audits
   - Explicit control over which agents run

2. **Parallel Execution Required**
   - Multi-domain security analysis
   - Comprehensive codebase scans
   - Time-sensitive validations
   - Background execution with monitoring

3. **Deterministic Workflows**
   - User knows exactly which security domain to check
   - Orchestration patterns (main agent delegates to specialists)
   - Integration with external tools

### Use Hybrid (Skills + Agents) When:

1. **Best of Both Worlds**
   - Skills for automatic discovery and context
   - Agents for explicit parallel execution
   - Combined for complete workflow

2. **Complex Security Reviews**
   - Skills provide initial context and composition
   - Agents execute deep parallel analysis
   - Synthesis with skill-guided interpretation

---

## Key Insights

1. **Skills solve automatic context management** - Semantic matching and progressive disclosure built-in
2. **Agents solve explicit parallel execution** - Agent SDK enables deterministic workflows
3. **Both share rule knowledge** - Symlinks ensure single source of truth
4. **Complementary, not competing** - Use the right tool for each scenario
5. **No additional infrastructure needed** - Skills already provide intelligent context injection


---

## Defense-in-Depth Strategy: Skills + Hooks + Agents

### Critical Understanding: Skills Are NOT Guaranteed

**Skills activation is probabilistic, not deterministic:**

From the official documentation:
> "Skills are **model-invoked**—Claude autonomously decides when to use them based on your request and the Skill's description."

**What this means for security:**
- ✅ Skills **may** activate if description semantically matches request
- ❌ Skills **may not** activate if Claude doesn't recognize the match
- ❌ **Cannot rely on skills alone for mandatory security enforcement**

**Example risk:**
```javascript
User: "Fix this authentication bug"
→ MIGHT activate authentication-security skill (probabilistic)
→ MIGHT NOT activate if semantic matching fails
→ Security guidance may be missed
```

### The Solution: Three-Layer Security Architecture

**Use skills, hooks, AND agents for comprehensive protection:**

```
┌─────────────────────────────────────────────────────────┐
│ Layer 1: Skills (Proactive Guidance - Best Effort)     │
│ - Auto-activate based on semantic matching              │
│ - Guide Claude toward secure implementations            │
│ - Reliability: Probabilistic (not guaranteed)           │
│ - Purpose: Reduce violations before they happen         │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Layer 2: Hooks (Mandatory Validation - Guaranteed)     │
│ - PreToolUse hooks execute before commits/writes        │
│ - Validate ALL code against security rules              │
│ - Reliability: 100% (deterministic execution)           │
│ - Purpose: Block unsafe operations, provide feedback    │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Layer 3: Agents (Deep Analysis - On-Demand)            │
│ - Triggered by hooks when violations detected           │
│ - Explicit parallel security scanning                   │
│ - Comprehensive rule validation                         │
│ - Purpose: Generate detailed remediation guidance       │
└─────────────────────────────────────────────────────────┘
```

### Complete Security Flow Example

**Scenario: Add JWT authentication to API**

```javascript
// ============================================================
// STEP 1: User Starts Task
// ============================================================
User: "Add JWT authentication to the API"

// ============================================================
// STEP 2: Skills Activate (Proactive - Probabilistic)
// ============================================================
Claude scans skill descriptions:
→ authentication-security skill may activate
  ├─ Matches: "authentication" in request
  ├─ Loads: Password hashing, MFA, credential guidelines
  └─ Suggests: bcrypt, secure session handling

→ session-management-security skill may activate
  ├─ Matches: "JWT" in request
  ├─ Loads: Token validation, expiration, storage
  └─ Suggests: Strong algorithms, proper validation

→ secrets-management skill may activate
  ├─ Matches: "authentication" implies secrets
  ├─ Loads: Environment variables, key storage
  └─ Suggests: Load JWT secret from env, not hardcode

Claude writes code following skill guidance:
✅ Uses bcrypt for passwords (from authentication-security skill)
✅ Implements proper JWT validation (from session-management skill)
✅ Loads secrets from environment (from secrets-management skill)

// ============================================================
// STEP 3: Claude Attempts Commit (Hooks Execute - Guaranteed)
// ============================================================
Claude: "git commit -m 'Add JWT authentication'"

PreToolUse hook ALWAYS executes (100% guaranteed):
→ Runs: python3 .claude/hooks/validate_security.py
→ Scans code for:
  ├─ Weak crypto (MD5, SHA1, DES)
  ├─ Hardcoded secrets (API_KEY = "...", PASSWORD = "...")
  ├─ SQL injection patterns (string concatenation in queries)
  ├─ Command injection (subprocess with shell=True)
  ├─ Path traversal (open(user_input) without validation)
  └─ [... all security rules ...]

// ============================================================
// STEP 4a: If Hook Finds Violations (Enforcement)
// ============================================================
Hook detects: hashlib.md5(password.encode())  # WEAK CRYPTO!

Hook BLOCKS commit and returns to Claude:
❌ SECURITY VIOLATION DETECTED
   - File: src/auth/login.py:42
   - Issue: MD5 used for password hashing
   - Rule: CRYPTO-001 (Weak cryptographic algorithm)
   - Fix: Use bcrypt.hashpw() or argon2.hash()

Claude sees violation feedback:
→ Optionally invokes comprehensive-security-agent for deep analysis
→ Agent provides detailed remediation with code examples
→ Claude fixes the issue
→ Tries commit again (hook re-validates)

// ============================================================
// STEP 4b: If Hook Finds No Violations (Success)
// ============================================================
Hook validation passes:
✅ All security rules satisfied
✅ No weak crypto detected
✅ No hardcoded secrets found
✅ Input validation present

Hook allows commit:
→ Code committed successfully
→ Security validation complete
```

### Why This Three-Layer Approach Works

**Layer 1: Skills (Proactive)**
- **Benefit:** Reduces violations at code creation time
- **Limitation:** Not guaranteed to activate
- **Value:** When they work, violations never happen
- **Coverage:** Probabilistic with well-written descriptions

**Layer 2: Hooks (Enforcement)**
- **Benefit:** Catches EVERYTHING skills miss
- **Limitation:** Reactive (after code written, before commit)
- **Value:** 100% guaranteed execution
- **Coverage:** 100% - no code escapes validation

**Layer 3: Agents (Deep Analysis)**
- **Benefit:** Comprehensive multi-domain analysis
- **Limitation:** Higher token cost, longer execution
- **Value:** Detailed remediation when needed
- **Coverage:** Triggered only when violations detected

### Hook Implementation Example

```json
// .claude/settings.json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/security_validator.py --tool Write"
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/security_validator.py --tool Bash"
          }
        ]
      }
    ]
  }
}
```

```python
# .claude/hooks/security_validator.py
"""
Security validation hook - guaranteed execution before commits/writes
Validates against all 191 security rules from compiled rule cards
"""
import sys
import json
from pathlib import Path

def validate_security(tool, input_data, mode):
    """Run security validation against rule cards"""

    # Load all security rules
    rules_dir = Path(".claude/agents/json")
    violations = []

    for rule_file in rules_dir.glob("*.json"):
        rules = json.loads(rule_file.read_text())

        # Check each rule's detection patterns
        for rule in rules.get("rules", []):
            if check_violation(input_data, rule):
                violations.append({
                    "file": extract_file_from_input(input_data),
                    "rule_id": rule["id"],
                    "severity": rule["severity"],
                    "description": rule["description"],
                    "remediation": rule["remediation"]
                })

    if violations:
        # BLOCK operation and return violations to Claude
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"SECURITY VIOLATIONS DETECTED - {len(violations)} issues found",
                "updatedInput": None
            },
            "violations": violations
        }))
        sys.exit(1)

    # Allow operation
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "permissionDecisionReason": "No security violations detected",
            "updatedInput": None
        }
    }))
    sys.exit(0)

if __name__ == "__main__":
    # Hook receives environment variables from Claude Code
    tool = sys.argv[1].replace("--tool", "").strip()
    input_data = os.getenv("CLAUDE_TOOL_INPUT")

    validate_security(tool, input_data, None)
```

### Key Decision: When to Use Each Layer

| Scenario | Skills | Hooks | Agents |
|----------|--------|-------|--------|
| Interactive development | ✅ Auto-activate | ✅ Validate commits | ❌ Not needed |
| Pre-commit validation | ⚠️ Best effort | ✅ Always run | ✅ If violations |
| CI/CD pipeline | ❌ Skip | ✅ Always run | ✅ Parallel scan |
| Security audit | ❌ Skip | ❌ Skip | ✅ Comprehensive |
| Learning/exploration | ✅ Auto-activate | ❌ May be too strict | ❌ Not needed |

### Critical Insight

**Skills alone are NOT sufficient for security-critical codebases:**

```
❌ WRONG: Rely only on skills
   → Skills may not activate
   → Violations can slip through
   → No enforcement mechanism

✅ RIGHT: Skills + Hooks + Agents
   → Skills reduce violations proactively
   → Hooks enforce rules deterministically
   → Agents provide deep analysis when needed
   → Defense-in-depth security
```

**For this security-focused repository: ALL THREE LAYERS ARE REQUIRED.**

---

## Migration Strategy: Validation-First Approach

### Current State (Verified Reality)

**What Actually Exists:**
- ✅ 21 JSON rule files in `.claude/agents/json/` (not "15+" - actual count: 21)
- ✅ 1 skill implemented: `authentication-security/SKILL.md`
- ✅ Symlink confirmed: `authentication-security/rules.json` → `../agents/json/authentication-specialist.json`
- ✅ Agent markdown files in `.claude/agents/` for sub-agent invocation

**What Does NOT Exist:**
- ❌ No `.claude/settings.json` (hooks not implemented)
- ❌ No `.claude/hooks/` directory or validation scripts
- ❌ No evidence that `authentication-security` skill auto-activates
- ❌ No metrics on skill activation rates, token usage, or effectiveness
- ❌ No validation of semantic matching behavior

**Critical Gap:** We have infrastructure but ZERO validation that it works as designed.

### Migration Principle: Verify Before Scale

**DO NOT create 14 more skills before validating the first one works.**

**DO NOT implement hooks before proving skills provide value.**

**DO NOT set numeric targets (">85% activation") without baseline measurements.**

### Phase 0: Validate Core Assumptions (REQUIRED - 2-3 days)

**This phase MUST succeed before proceeding to Phase 1.**

#### Test 1: Skill Auto-Activation Validation

**Goal:** Prove `authentication-security` skill actually auto-activates based on semantic matching

**Method:**
1. Create 20 test prompts:
   - 10 authentication-related: "Review login code", "Check password hashing", "Analyze JWT authentication", etc.
   - 10 unrelated: "Parse JSON file", "Optimize database query", "Fix CSS layout", etc.
2. For each prompt, observe Claude's behavior
3. Document which prompts trigger skill activation
4. Measure actual token usage during activation

**Success Criteria:**
- ✅ Skill loads on ≥8/10 authentication-related prompts (80% true positive)
- ✅ Skill does NOT load on ≥9/10 unrelated prompts (<10% false positive)
- ✅ Can articulate WHY certain prompts matched (semantic understanding)
- ✅ Have actual token measurements (not guesses)

**If FAILS:**
- Refine skill description
- Test alternative descriptions
- If still fails: skills may not work as documented → STOP and reassess

#### Test 2: Progressive Disclosure Validation

**Goal:** Verify skills load incrementally, not all-at-once

**Method:**
1. Monitor what gets loaded when skill activates
2. Check if `rules.json` loads immediately or on-demand
3. Test with simple prompt vs complex violation
4. Measure token usage at each stage

**Success Criteria:**
- ✅ Evidence of staged loading (description → SKILL.md → rules.json)
- ✅ Actual token measurements for each stage
- ✅ Rules.json only loads when needed (not always)

**If FAILS:**
- Skills may load too much context upfront
- May need restructuring

#### Test 3: Skill Value Validation

**Goal:** Prove skills actually provide security guidance

**Method:**
1. Give Claude code with auth vulnerabilities (MD5 password hashing, hardcoded secrets)
2. Test WITH skill activated
3. Test WITHOUT skill activated (control)
4. Compare quality of security recommendations

**Success Criteria:**
- ✅ WITH skill: Claude catches vulnerabilities
- ✅ WITHOUT skill: Claude misses or provides weaker guidance
- ✅ Measurable difference in security advice quality

**If FAILS:**
- Skills may not add value
- May need better content in SKILL.md
- Consider whether agent invocation is sufficient

**STOP GATE:** Phase 0 must demonstrate measurable value before proceeding.

---

### Phase 1: Incremental Skill Creation (CONDITIONAL - timing TBD)

**Prerequisites:** Phase 0 tests pass with clear evidence skills work

**Process:** Create ONE skill at a time, validate, then proceed

**Per-Skill Validation Process:**
1. Create `{domain}-security/SKILL.md`
2. Test auto-activation (minimum 10 prompts)
3. Measure true positive rate, false positive rate
4. Refine description if activation rate <70%
5. ONLY create next skill after validation succeeds

**Skills Priority Order (by expected frequency):**
1. ✅ authentication-security (exists - validate in Phase 0)
2. ⬜ input-validation-security (high frequency - SQL injection, XSS)
3. ⬜ secrets-management-security (high frequency - API keys, credentials)
4. ⬜ session-management-security (moderate frequency)
5. ⬜ cryptography-security (moderate frequency)
6. ⬜ [Continue ONLY if previous skills validate successfully]

**Stop Conditions:**
- Any skill fails validation (<70% true positive OR >20% false positive)
- Token usage per skill exceeds reasonable limits (define limit based on Phase 0 data)
- Diminishing returns (skill provides no new value over existing skills)

**DO NOT create all 14 skills blindly.** Create, validate, learn, adjust.

---

### Phase 2: Minimal Hook Implementation (CONDITIONAL - 1 week)

**Prerequisites:**
- Phase 0 proves skills provide value
- At least 3 skills validated and working
- Clear understanding of token costs

**Step 1: Minimal Viable Hook (1-2 days)**

Create simplest possible hook to validate mechanism works:

```json
// .claude/settings.json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Write",
      "hooks": [{
        "type": "command",
        "command": "python3 .claude/hooks/minimal_validator.py"
      }]
    }]
  }
}
```

```python
# .claude/hooks/minimal_validator.py
# Test: detect hardcoded "password123" only
import json, sys, os

input_data = os.getenv("CLAUDE_TOOL_INPUT", "")
if "password123" in input_data:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Hardcoded password detected (test)",
            "updatedInput": None
        }
    }))
    sys.exit(1)

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "allow",
        "permissionDecisionReason": "No test violation",
        "updatedInput": None
    }
}))
sys.exit(0)
```

**Validation:**
- ✅ Hook actually executes on Write tool use
- ✅ `permissionDecision: "deny"` actually blocks the write
- ✅ Claude receives and understands the feedback
- ✅ Can unblock by removing violation

**If FAILS:** Fix hook mechanism before adding complexity

**Step 2: Single Real Rule (1-2 days)**

Add ONE security rule (e.g., detect `hashlib.md5` in Python code):

- Test detection works on real code
- Measure false positive rate
- Test Claude's response to violation feedback
- Verify violation → fix → retry flow works

**Step 3: Expand Incrementally (ONLY if Step 1+2 succeed)**

- Add rules one domain at a time
- Validate each addition doesn't spike false positives
- Monitor performance impact
- Roll back if accuracy degrades

**DO NOT load all 191 rules at once.** Incremental, validated expansion only.

---

### Phase 3: Hook-Agent Integration (CONDITIONAL - timing TBD)

**Prerequisites:**
- Phase 0: Skills validated
- Phase 2: Hooks validated with acceptable false positive rate
- Clear metrics on when agent invocation adds value

**Goal:** Hooks trigger agent analysis on violations

**Implementation:**
- Hook detects violation
- Hook calls Agent SDK to invoke specialist agent
- Agent provides detailed remediation
- Feedback loops back to Claude

**Validation:**
- Measure remediation quality WITH agent vs WITHOUT
- Measure token cost of agent invocation
- Measure time cost
- Ensure agent adds value beyond hook message

**If agent doesn't add measurable value over hook feedback alone: Skip this phase**

---

### Validation Metrics (Measured, Not Targets)

**DO NOT set targets before baseline measurement.**

**Metrics to MEASURE (not predict):**
- Skill activation rate (true positive, false positive, false negative)
- Token usage per skill activation (actual numbers)
- Hook detection accuracy (true positive, false positive rates)
- Agent remediation value (measurable improvement vs hook-only)
- End-to-end time cost

**After measurement, THEN decide if metrics are acceptable.**

**If metrics show approach isn't working: pivot or stop, don't force it.**

---

## Recommendation: Embrace the Three-Layer Architecture

**Implement skills, hooks, AND agents for defense-in-depth:**

**Benefits:**
- ✅ **Layer 1 (Skills):** Proactive guidance reduces violations before they happen
- ✅ **Layer 2 (Hooks):** Guaranteed enforcement catches everything skills miss
- ✅ **Layer 3 (Agents):** Deep analysis provides comprehensive remediation
- ✅ Backward compatible (existing agent workflows unchanged)
- ✅ Token efficient (skills auto-activate, agents only when needed)
- ✅ Security-first (100% coverage through hooks)

**Implementation:**
1. **Skills** in `.claude/skills/` - Auto-discovery and proactive guidance
2. **Hooks** in `.claude/settings.json` - Mandatory security validation
3. **Agents** in `.claude/agents/` - Explicit parallel execution and deep analysis
4. **Shared rules** via symlinks - Single source of truth (no duplication)

**Architecture:**
```
.claude/
├── skills/                          # Layer 1: Proactive Guidance
│   ├── authentication-security/
│   ├── session-management-security/
│   └── [... 15 security domains]
│
├── settings.json                    # Layer 2: Hook Configuration
├── hooks/
│   ├── security_validator.py       # Validates all commits/writes
│   └── utils/                       # Rule loading & pattern matching
│
└── agents/                          # Layer 3: Deep Analysis
    ├── authentication-specialist.md
    ├── [... 15 specialist agents]
    └── json/                        # Shared security rules
        └── *.json                   # 191 rules across 20 domains
```

**Result - Complete Security Coverage:**
```
Interactive Development:
- User: "Add JWT authentication"
  → Skills auto-activate (guidance)
  → Claude writes secure code
  → Hooks validate before commit (enforcement)
  → If violations: Agents provide remediation (analysis)

Pre-Commit Validation:
- Developer commits code
  → Hooks ALWAYS validate (100% coverage)
  → Block if violations detected
  → Trigger agents for detailed analysis
  → Provide actionable remediation

CI/CD Pipeline:
- Pipeline runs security scan
  → Hooks validate all changes
  → Agents run in parallel for comprehensive analysis
  → Generate security report
  → Block merge if violations found
```

---

**Conclusion:** Skills, hooks, and agents form a comprehensive three-layer security architecture. Skills provide proactive guidance through automatic context injection. Hooks provide guaranteed enforcement that catches everything skills miss. Agents provide deep parallel analysis when violations occur. Together, they deliver defense-in-depth security with 100% coverage for security-critical codebases.

## Detailed Comparison

### Context Loading

**Agent (Reference-Based):**
```
┌──────────────────────────────────────┐
│ Step 1: Load Agent Instructions     │ moderate cost
│ - Agent frontmatter                  │
│ - Analysis approach                  │
│ - Tool descriptions                  │
└──────────────────────────────────────┘
         ↓ (when analysis needed)
┌──────────────────────────────────────┐
│ Step 2: Load JSON Rule File         │ larger cost
│ - Read json/{agent-name}.json        │
│ - All rules, detection patterns      │
│ - References (ASVS, CWE, OWASP)      │
└──────────────────────────────────────┘
```

**Skill (Progressive):**
```
┌─────────────────────┐
│ Step 1: Overview    │ small cost (discovery)
│ - Name + description│
└─────────────────────┘
         ↓ (semantic match)
┌─────────────────────┐
│ Step 2: Load SKILL  │ moderate cost
│ - Full instructions │
│ - Capabilities      │
│ - Usage patterns    │
└─────────────────────┘
         ↓ (if needed)
┌─────────────────────┐
│ Step 3: Full Rules  │ larger cost
│ - Load rules.json   │
│ - All detection     │
└─────────────────────┘
```

---

**Final Summary:** Skills and agents are complementary tools in a hybrid architecture. Skills provide automatic context injection through semantic matching and progressive disclosure. Agents provide explicit parallel execution for programmatic workflows. Both share the same security rule knowledge base through symlinks, ensuring consistency without duplication.

Use skills for interactive workflows where Claude auto-detects what knowledge to apply.
Use agents for programmatic workflows where you explicitly control which specialists run in parallel.
Together, they provide the complete security analysis capability.
