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
// Compare to: Manually calling 3 agents serially
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

**The "missing layer" isn't missing - it's skills!**

---

## Migration Strategy

### Current State (Already Implemented)

- ✅ 15+ agents in `.claude/agents/` with compiled JSON rule cards
- ✅ Authentication-security skill prototype in `.claude/skills/`
- ✅ Symlink architecture (skills reference agent JSON)
- ✅ Single source of truth for security rules

### Next Steps

**Phase 1: Create Remaining Skills (2-3 weeks)**
- Convert each agent to skill format
- Focus on rich descriptions for semantic matching
- Add progressive disclosure structure
- Test auto-activation patterns

**Phase 2: Validate Auto-Activation (1 week)**
- Test semantic matching accuracy
- Measure token efficiency gains
- Document activation patterns
- Refine skill descriptions

**Phase 3: Optimize Hybrid Usage (1 week)**
- Document when to use skills vs agents
- Create usage examples
- Update CLAUDE.md with guidance
- Train team on hybrid approach

---

## Recommendation: Embrace the Hybrid

**Keep both skills and agents:**

**Benefits:**
- ✅ Skills for automatic context (interactive workflows)
- ✅ Agents for explicit execution (programmatic workflows)
- ✅ Backward compatible (existing agent workflows unchanged)
- ✅ Forward compatible (new skill-based workflows enabled)
- ✅ Token efficient (skills auto-activate only when needed)
- ✅ Flexible (choose right tool for each scenario)

**Implementation:**
1. Skills in `.claude/skills/` (new, auto-discovery)
2. Agents in `.claude/agents/` (existing, explicit invocation)
3. Symlink to shared JSON rule sets (no duplication)
4. Document when to use each approach
5. Support both invocation methods

**Result:**
```
User can say:
- "What authentication security capabilities exist?" → Skills auto-activate
- "Validate auth system" → Agents execute explicitly
- "Guide me through secure auth" → Skills provide examples
- "Scan codebase for auth vulns" → Agents run in parallel
```

---

**Conclusion:** Skills and agents serve different but complementary purposes. The hybrid architecture gives the best of both worlds without sacrificing existing capabilities. Skills already solve automatic context injection - no additional infrastructure needed.

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
