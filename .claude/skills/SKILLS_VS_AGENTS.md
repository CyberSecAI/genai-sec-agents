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

### Skills are Useful For:
- **Simple, stateless utilities** (format conversion, validation)
- **Reusable calculations or transformations**
- **Things that DON'T need parallel execution or complex reasoning**
- **Interactive learning and discovery**
- **Progressive disclosure of capabilities**

### Sub-agents are Better For:
- **Complex multi-step analysis** (security reviews)
- **Parallel execution across multiple domains**
- **Accessing specialized knowledge bases** (rule cards)
- **Stateful workflows with multiple validation steps**
- **Automated security validation pipelines**

**Rule of Thumb:** Don't add skills just because they exist. Use the right abstraction for the job. Adding a skill wrapper around sub-agent calls creates unnecessary indirection without adding value.

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
- ❌ **Less mature**: New format, less battle-tested
- ❌ **Parallel execution**: Unclear how multiple skills run simultaneously

**Token Usage:**
```
Initial load: ~2k tokens (overview only)
On-demand: +3k tokens (examples)
On-demand: +10k tokens (full rules via JSON symlink)
On-demand: +2k tokens (detection patterns)
Total if all loaded: ~17k tokens (similar to agent with JSON loaded)
Advantage: Can provide guidance without loading full rule set
```

**Best For:**
- Interactive security guidance
- Learning secure coding patterns
- Multi-domain security analysis
- Understanding security capabilities
- Composing security workflows

---

## Hybrid Architecture (Recommended)

**Use BOTH skills and agents in a two-layer architecture:**

```
.claude/
├── skills/              # Skills layer: Discovery + Composition
│   └── authentication-security/
│       ├── SKILL.md                    # Progressive disclosure entry point
│       ├── rules.json                  # Symlink to agent JSON
│       └── examples/                   # Code examples
│
└── agents/              # Agents layer: Execution + Parallelism
    ├── authentication-specialist.md    # Task execution
    └── json/
        └── authentication-specialist.json  # Compiled rules
```

### Layer Interaction

**Scenario 1: Interactive Learning**
```
User: "What authentication security capabilities do you have?"

Claude: [Loads authentication-security SKILL.md]
→ Progressive disclosure: Overview → Capabilities → Examples
→ Token-efficient: Only loads what's needed
```

**Scenario 2: Automated Validation**
```
Pre-commit hook: Validate authentication changes

Task System: [Invokes authentication-specialist agent]
→ Fast: Loads full context immediately
→ Parallel: Runs with other agents simultaneously
```

**Scenario 3: Comprehensive Analysis**
```
User: "Review authentication system comprehensively"

Claude: [Composes multiple skills]
1. Authentication-security skill → Login mechanisms
2. Session-security skill → Session handling
3. Secrets-management skill → Credential storage

[Then executes via parallel agents]
→ authentication-specialist agent
→ session-management-specialist agent
→ secrets-specialist agent

[Synthesizes results from all three]
```

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
│ Step 1: Overview    │ ~2k tokens
│ - Capabilities      │
│ - When to use       │
└─────────────────────┘
         ↓ (if needed)
┌─────────────────────┐
│ Step 2: Examples    │ +3k tokens
│ - Code snippets     │
│ - Common patterns   │
└─────────────────────┘
         ↓ (if needed)
┌─────────────────────┐
│ Step 3: Full Rules  │ +5k tokens
│ - All 45 rules      │
│ - Detection details │
└─────────────────────┘
```

### Invocation Methods

**Agent Invocation (Programmatic):**
```javascript
// Method 1: Single agent
use the authentication-specialist agent to validate src/auth/login.py

// Method 2: Parallel agents (single message, multiple Task calls)
use the authentication-specialist agent to analyze authentication
use the session-management-specialist agent to analyze sessions
use the secrets-specialist agent to analyze credentials

// Method 3: CI/CD integration
Task(
  subagent_type="authentication-specialist",
  prompt="Validate authentication implementation",
  scope="src/auth/"
)
```

**Skill Activation (Natural Language):**
```
// Method 1: Single skill
Activate authentication-security skill and review the login system

// Method 2: Multi-skill composition
Use authentication-security, session-security, and secrets-management skills
to perform comprehensive authentication review

// Method 3: Skill-guided workflow
Guide me through implementing secure authentication using the
authentication-security skill
```

### Parallel Execution

**Agents (Native Parallel Support):**
```javascript
// Claude Code sends single message with 3 Task calls
Task(authentication-specialist, ...)
Task(session-management-specialist, ...)
Task(secrets-specialist, ...)

→ All 3 agents run in parallel
→ Results aggregated by orchestrator
→ ~3 minutes total (vs 9 minutes sequential)
```

**Skills (Composition, Then Parallel Agents):**
```
Step 1: Skill composition (understanding)
→ Load authentication-security skill
→ Load session-security skill
→ Load secrets-management skill
→ Understand how they integrate

Step 2: Execute via agents (parallel)
→ Invoke authentication-specialist agent
→ Invoke session-management-specialist agent
→ Invoke secrets-specialist agent
→ Synthesize results based on skill composition knowledge
```

## Token Efficiency Comparison

### Scenario: Simple Authentication Review

**Using Agent:**
```
Load: authentication-specialist agent     = 2k tokens (instructions)
Load: json/authentication-specialist.json = 12k tokens (rules)
Analysis: Review login.py                 = 2k tokens
Response: Security findings               = 3k tokens
─────────────────────────────────────────────────────
Total: 19k tokens
```

**Using Skill:**
```
Load: authentication-security SKILL.md    = 2k tokens (overview)
Analysis: Review login.py                 = 2k tokens
Response: Security findings (with examples) = 4k tokens
On-demand: Load rules.json (if needed)    = 12k tokens (full rules)
─────────────────────────────────────────────────────
Total: 8k tokens (without rules) or 20k tokens (with rules)
Advantage: Can answer simple questions without loading full rule set
```

### Scenario: Comprehensive Multi-Domain Review

**Using Agents (Parallel):**
```
Load: 3 specialist agents                 = 6k tokens (instructions)
Load: 3 JSON rule files                   = 36k tokens (all rules)
Analysis: Review auth system              = 10k tokens
Response: Consolidated report             = 5k tokens
─────────────────────────────────────────────────────
Total: 57k tokens
Time: 3 minutes (parallel)
```

**Using Skills → Agents (Hybrid):**
```
Step 1: Load 3 skills (progressive)       = 6k tokens (overviews)
Step 2: Compose workflow                  = 2k tokens
Step 3: Execute 3 agents (parallel)       = 6k tokens (instructions)
Step 4: Load JSON rules for analysis      = 36k tokens (via agents)
Analysis: Review auth system              = 10k tokens
Response: Skill-guided report             = 5k tokens
─────────────────────────────────────────────────────
Total: 64k tokens (+12% overhead)
Time: 3 minutes (parallel execution preserved)
Benefit: Skills provide upfront workflow understanding before execution
```

## When to Use Each Approach

### Use Agents Directly When:

1. **Automated Workflows**
   - CI/CD security scanning
   - Pre-commit validation hooks
   - Scheduled security audits

2. **Parallel Execution Required**
   - Multi-domain security analysis
   - Comprehensive codebase scans
   - Time-sensitive validations

3. **Programmatic Invocation**
   - Integration with external tools
   - Batch processing
   - API-driven security checks

4. **Token Budget is High**
   - Complex analysis requiring full context
   - Deep security reviews
   - Compliance audits

### Use Skills When:

1. **Interactive Guidance**
   - Learning secure coding patterns
   - Understanding security requirements
   - Exploring security capabilities

2. **Token Budget is Limited**
   - Simple security questions
   - Targeted guidance
   - Progressive exploration

3. **Composition Required**
   - Multi-skill security workflows
   - Cross-domain integration
   - Holistic security understanding

4. **Examples Needed**
   - Secure code implementation
   - Pattern reference
   - Best practice demonstration

### Use Hybrid (Skills + Agents) When:

1. **Comprehensive Analysis**
   - Understand scope via skills
   - Execute analysis via agents
   - Synthesize with skill context

2. **Workflow Definition**
   - Skills define "what" and "why"
   - Agents execute "how"
   - Combined for complete workflow

3. **Best of Both Worlds**
   - Progressive learning (skills)
   - Fast execution (agents)
   - Parallel processing (agents)
   - Rich context (skills)

## Migration Strategy

### Phase 1: Create Skills (Additive)
- Convert agents to skills format
- Add to `.claude/skills/`
- **Keep agents unchanged**
- No breaking changes

### Phase 2: Test Hybrid Usage
- Test skill activation
- Test agent execution
- Test composition patterns
- Validate token savings

### Phase 3: Update Documentation
- Document when to use each
- Provide usage examples
- Update Claude Code README
- Create decision matrix

### Phase 4: Optimize
- Refine skill structure
- Improve progressive disclosure
- Enhance composition patterns
- Monitor token usage

## Recommendation: Hybrid Architecture

**Best Approach:** Maintain both skills and agents

**Benefits:**
- ✅ Skills for discovery and learning (progressive disclosure)
- ✅ Agents for execution and automation (parallel processing)
- ✅ Backward compatible (existing workflows unchanged)
- ✅ Forward compatible (new skill-based workflows enabled)
- ✅ Token efficient (use skills when possible, agents when needed)
- ✅ Flexible (choose right tool for each scenario)

**Implementation:**
1. Create skills in `.claude/skills/` (new)
2. Keep agents in `.claude/agents/` (existing)
3. Symlink to shared JSON rule sets (no duplication)
4. Document when to use each approach
5. Support both invocation methods

**Result:**
```
User can say:
- "What are your authentication security capabilities?" → Load skill
- "Validate auth system" → Execute agent(s)
- "Guide me through secure auth implementation" → Use skill + examples
- "Scan codebase for auth vulnerabilities" → Run agents in parallel
```

---

**Conclusion:** Skills and agents serve different but complementary purposes. The hybrid architecture gives you the best of both worlds without sacrificing existing capabilities.
