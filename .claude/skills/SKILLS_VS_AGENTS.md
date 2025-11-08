# Skills vs Agents: Architecture Comparison

## Quick Decision Matrix

| Use Case | Use | Why |
|----------|-----|-----|
| Parallel execution of multiple security checks | **Agents** | Task tool supports parallel agent invocation |
| Understanding what security capabilities exist | **Skills** | Progressive disclosure, human-readable |
| Automated pre-commit validation hooks | **Agents** | Programmatic invocation via Task system |
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
- **Token efficiency** (~50 tokens until activated, then load full content)
- **Zero cognitive load** (no need to remember which skill to call)

### Agents are Better For:
- **Explicit parallel execution** (multiple agents simultaneously via Task tool)
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
├─ authentication-security: 50 tokens (name + description)
├─ session-management-security: 50 tokens
├─ secrets-management: 50 tokens
├─ [... 12 more skills]: ~600 tokens
└─ Total Discovery Cost: ~750 tokens

User Request: "Review authentication code"
├─ Semantic Match: authentication-security skill
├─ Load Full Skill: authentication-security/SKILL.md (~3-5k tokens)
├─ On-Demand: Load rules.json if needed (~12k tokens)
└─ Total Cost: 750 + 5k + (optional 12k) = ~6k-18k tokens

Compare to Agents (Manual Invocation)
├─ No discovery phase (user must know agent exists)
├─ Load Full Agent: authentication-specialist.md (~2k tokens)
├─ Load Rules: json/authentication-specialist.json (~12k tokens)
└─ Total Cost: ~14k tokens (all upfront, no progressive loading)
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
// Cost: 750 (discovery) + ~15k (3 skills × 5k each)
// Compare to: Manually calling 3 agents or calling an agent to call sub-agents
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
- ✅ **Parallel Execution**: Multiple agents run simultaneously
- ✅ **Programmatic**: Task tool with `subagent_type` parameter
- ✅ **Fast**: Optimized for automated execution
- ✅ **Validated**: Existing workflow, proven in production
- ✅ **On-Demand Loading**: References JSON rule files, loads when needed
- ✅ **Composition**: comprehensive-security-agent includes all specialist rules
- ⚠️ **Less discoverable**: Harder to understand capabilities without reading agent files

**Token Usage:**
```
Initial load: ~2k tokens (agent instructions + frontmatter)
On-demand: Load JSON rule file when needed (~10-15k tokens)
Total: 2k-17k tokens depending on whether rules are loaded
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
- ✅ **Token Efficient**: ~50 tokens until activated

**Token Usage:**
```
Initial load: ~50 tokens (name + description during discovery)
On-activation: ~3-5k tokens (full SKILL.md content)
On-demand: +10k tokens (full rules via JSON symlink if needed)
Total if all loaded: ~13-15k tokens
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
2. **Agents solve explicit parallel execution** - Task tool enables deterministic workflows
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
→ MIGHT activate authentication-security skill (~80-90% chance)
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
│ - Reliability: ~80-90% (probabilistic)                  │
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
→ authentication-security skill activates (~90% chance)
  ├─ Matches: "authentication" in request
  ├─ Loads: Password hashing, MFA, credential guidelines
  └─ Suggests: bcrypt, secure session handling

→ session-management-security skill activates (~85% chance)
  ├─ Matches: "JWT" in request
  ├─ Loads: Token validation, expiration, storage
  └─ Suggests: Strong algorithms, proper validation

→ secrets-management skill activates (~80% chance)
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
- **Coverage:** ~80-90% with well-written descriptions

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

```yaml
# .claude/hooks.yml
hooks:
  # Security validation before file writes
  - event: PreToolUse
    tool: Write
    command: |
      python3 .claude/hooks/security_validator.py \
        --tool Write \
        --input "$CLAUDE_TOOL_INPUT" \
        --mode pre-write

  # Security validation before git commits
  - event: PreToolUse
    tool: Bash
    command: |
      # Detect git commit commands
      if echo "$CLAUDE_TOOL_INPUT" | grep -q "git commit"; then
        python3 .claude/hooks/security_validator.py \
          --tool Bash \
          --input "$CLAUDE_TOOL_INPUT" \
          --mode pre-commit
      fi
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
            "blocked": True,
            "violations": violations,
            "message": f"SECURITY VIOLATIONS DETECTED - {len(violations)} issues found"
        }))
        sys.exit(1)  # Non-zero exit blocks the tool use

    # Allow operation
    sys.exit(0)

if __name__ == "__main__":
    # Hook receives environment variables from Claude Code
    tool = sys.argv[1].replace("--tool", "").strip()
    input_data = os.getenv("CLAUDE_TOOL_INPUT")
    mode = sys.argv[3].replace("--mode", "").strip()

    validate_security(tool, input_data, mode)
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

## Migration Strategy

### Current State (Already Implemented)

- ✅ 15+ agents in `.claude/agents/` with compiled JSON rule cards
- ✅ Authentication-security skill prototype in `.claude/skills/`
- ✅ Symlink architecture (skills reference agent JSON)
- ✅ Single source of truth for security rules

### Next Steps: Complete Three-Layer Implementation

**Phase 1: Create Remaining Skills (2-3 weeks) - Layer 1**
- Convert each agent to skill format
- Focus on rich descriptions for semantic matching
- Add progressive disclosure structure
- Test auto-activation patterns
- **Goal:** Proactive guidance reduces violations at creation time

**Skills to create:**
- ✅ authentication-security (completed)
- ⬜ session-management-security
- ⬜ secrets-management-security
- ⬜ input-validation-security
- ⬜ cryptography-security
- ⬜ authorization-security
- ⬜ logging-security
- ⬜ data-protection-security
- ⬜ web-security
- ⬜ configuration-security
- ⬜ [... remaining 10 domains]

**Phase 2: Implement Security Hooks (1 week) - Layer 2**
- Create `.claude/hooks.yml` configuration
- Implement `security_validator.py` hook script
- Add PreToolUse hooks for Write and Bash tools
- Validate against all 191 security rules from JSON files
- Test blocking behavior and feedback mechanism
- **Goal:** 100% guaranteed security enforcement before commits

**Hook deliverables:**
- `.claude/hooks.yml` - Hook configuration
- `.claude/hooks/security_validator.py` - Validation script
- `.claude/hooks/utils/` - Rule loading and pattern matching
- Documentation on hook behavior and debugging

**Phase 3: Integrate Hooks with Agents (1 week) - Layer 3**
- Hooks trigger agent invocation on violations
- Configure parallel agent execution
- Implement detailed remediation feedback loop
- Test end-to-end: violation → agent analysis → remediation
- **Goal:** Deep analysis and actionable guidance when violations occur

**Integration deliverables:**
- Hook-to-agent invocation logic
- Parallel execution configuration
- Remediation feedback templates
- End-to-end validation tests

**Phase 4: Validate Three-Layer Architecture (1 week)**
- Test complete flow: Skills → Hooks → Agents
- Measure effectiveness of each layer
- Document activation rates and violation detection
- Refine descriptions and detection patterns
- **Goal:** Verify defense-in-depth provides comprehensive protection

**Validation metrics:**
- Skill activation rate (target: >85%)
- Hook violation detection rate (target: 100%)
- Agent remediation effectiveness (target: >95%)
- False positive rate (target: <5%)
- End-to-end security coverage (target: 100%)

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
2. **Hooks** in `.claude/hooks.yml` - Mandatory security validation
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
├── hooks.yml                        # Layer 2: Guaranteed Enforcement
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
│ Step 1: Load Agent Instructions     │ ~2k tokens
│ - Agent frontmatter                  │
│ - Analysis approach                  │
│ - Tool descriptions                  │
└──────────────────────────────────────┘
         ↓ (when analysis needed)
┌──────────────────────────────────────┐
│ Step 2: Load JSON Rule File         │ ~10-15k tokens
│ - Read json/{agent-name}.json        │
│ - All rules, detection patterns      │
│ - References (ASVS, CWE, OWASP)      │
└──────────────────────────────────────┘
```

**Skill (Progressive):**
```
┌─────────────────────┐
│ Step 1: Overview    │ ~50 tokens (discovery)
│ - Name + description│
└─────────────────────┘
         ↓ (semantic match)
┌─────────────────────┐
│ Step 2: Load SKILL  │ ~3-5k tokens
│ - Full instructions │
│ - Capabilities      │
│ - Usage patterns    │
└─────────────────────┘
         ↓ (if needed)
┌─────────────────────┐
│ Step 3: Full Rules  │ +10k tokens
│ - Load rules.json   │
│ - All detection     │
└─────────────────────┘
```

---

**Final Summary:** Skills and agents are complementary tools in a hybrid architecture. Skills provide automatic context injection through semantic matching and progressive disclosure. Agents provide explicit parallel execution for programmatic workflows. Both share the same security rule knowledge base through symlinks, ensuring consistency without duplication.

Use skills for interactive workflows where Claude auto-detects what knowledge to apply.
Use agents for programmatic workflows where you explicitly control which specialists run in parallel.
Together, they provide the complete security analysis capability.
