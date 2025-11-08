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

## The Missing Layer: Automatic Context Management

### The Core Problem

**Current State (Manual):**
```javascript
// User: "Fix authentication vulnerability"
// Developer must remember to:
use authentication-specialist agent to review auth code
```

**Problems:**
- ❌ Requires developer to know which agent to call
- ❌ No automatic detection of security domains
- ❌ All-or-nothing: either load full agent or nothing
- ❌ Easy to miss relevant security domains
- ❌ Manual invocation adds cognitive load

**Desired State (Automatic):**
```javascript
// User: "Fix authentication vulnerability"
// System automatically:
1. Detects "authentication" domain from user story/code
2. Loads ONLY authentication security knowledge
3. Applies it during code creation/editing/review
4. No manual agent invocation needed
```

### Required Capabilities

**Intelligent context injection needs:**
- 🎯 **Domain detection** - What security domains are relevant?
- 🎯 **Context scoping** - Load only what's needed
- 🎯 **Automatic activation** - No manual agent calls
- 🎯 **Progressive loading** - Start small, expand if needed

### Three-Layer Context Loading Architecture

```
Layer 1: Detection (Always Active, ~0 tokens)
├─ Analyze user story/file/commit
├─ Extract security domains from keywords/imports/patterns
└─ Determine minimal context needed

Layer 2: Targeted Loading (On-Demand, 2-6k tokens)
├─ Load ONLY relevant domain overviews
├─ Apply domain-specific rules to code
└─ Escalate to full rules if violations found

Layer 3: Deep Analysis (If Needed, 15-20k tokens)
├─ Load full rule sets for detected violations
├─ Invoke parallel specialist agents
└─ Generate comprehensive remediation
```

### Context Activation Triggers

**Trigger 1: User Story Analysis**
```yaml
# Story: "Implement JWT authentication for API"
Auto-detect domains:
- authentication (JWT mention)
- session-management (token handling)
- secrets-management (signing keys)

Auto-load relevant context:
- authentication-security/overview.md (2k tokens)
- session-management-security/jwt.md (1k tokens)
- secrets-management/key-storage.md (1k tokens)
Total: 4k tokens (vs 57k for all agents)
```

**Trigger 2: Code File Analysis**
```python
# File: src/auth/login.py
# Auto-detect from imports/code:
import jwt          → session-management domain
import bcrypt       → authentication domain
import os.getenv    → secrets-management domain

# Auto-load ONLY relevant rules:
- Password hashing rules (authentication)
- JWT validation rules (session-management)
- Secret handling rules (secrets-management)
```

**Trigger 3: Git Diff Analysis**
```diff
# Pre-commit hook sees:
+ def authenticate(username, password):
+     hash = hashlib.md5(password.encode())  # WEAK CRYPTO

# Auto-trigger:
- Load crypto rules (comprehensive-security-agent/crypto)
- Flag MD5 usage immediately
- Suggest SHA-256 with reasoning
```

### Token Efficiency: Progressive Loading

**Current Approach (Manual, All-or-Nothing):**
```
Developer calls: "use authentication-specialist agent"
Load: authentication-specialist.md (2k)
Load: json/authentication-specialist.json (12k)
Load: session-management-specialist.md (2k)
Load: json/session-management-specialist.json (10k)
Load: secrets-specialist.md (2k)
Load: json/secrets-specialist.json (8k)
─────────────────────────────────────────────
Total: 36k tokens (loaded upfront, used or not)
```

**Progressive Approach (Automatic, Targeted):**
```
Auto-detect domains from story/code (0k tokens)
Load: 3 domain overviews (6k tokens)
Apply: During code creation (real-time)
Escalate: Only if violations detected
  → Load specific rules (15k tokens)
  → Invoke agents (parallel)
─────────────────────────────────────────────
Best case: 6k tokens (no violations)
Worst case: 21k tokens (violations + agents)
Average: ~13k tokens (40% token savings)
```

### Implementation Options

#### Option A: Enhanced Skills (Progressive Context)

Add auto-activation metadata to skills frontmatter:

```markdown
# .claude/skills/authentication-security/SKILL.md
---
name: authentication-security
auto_activate_on:
  keywords: [login, password, authenticate, jwt, token, mfa, 2fa]
  imports: [bcrypt, argon2, passlib, jwt, oauthlib]
  file_patterns: [**/auth/**, **/login.py, **/authentication/**]
  functions: [authenticate(), login(), verify_password()]
---

## Context Levels (Progressive Loading)

### Level 1: Overview (2k tokens) - Always load when triggered
- Core security principles
- Common vulnerabilities
- Quick validation checklist

### Level 2: Specific Rules (5k tokens) - Load when code detected
- Password hashing requirements
- MFA implementation patterns
- Session token handling

### Level 3: Full Analysis (15k tokens) - Load when violations found
- All 45 authentication rules
- Detection patterns
- Remediation examples with code
```

**How it works:**
1. User opens `src/auth/login.py` → Auto-detects "authentication" domain
2. Loads Level 1 overview (2k tokens) → Applies quick validation
3. User writes password hashing code → Loads Level 2 rules (5k tokens)
4. User uses MD5 → Detects violation → Loads Level 3 + invokes agent (15k tokens)

#### Option B: CLAUDE.md Domain Triggers (Immediate)

Enhance CLAUDE.md with domain detection rules:

```markdown
# CLAUDE.md - Automatic Security Context Loading

BEFORE any security-related work, Claude Code should:

1. **Analyze work context:**
   - Read user story/task description
   - Scan files being modified
   - Review git diff if available

2. **Detect security domains:**
   - Extract keywords (authentication, crypto, input, etc.)
   - Analyze imports and code patterns
   - Match against domain triggers

3. **Load targeted context:**
   - Start with domain overviews (2-3k tokens)
   - Load specific rules when code detected (5k tokens)
   - Invoke specialist agents only when violations found

4. **Apply during work:**
   - Code creation: Apply rules proactively
   - Code editing: Validate changes against loaded context
   - Code review: Flag violations with loaded knowledge

## Domain Trigger Definitions

### Authentication Domain
**Auto-activate when:**
- Keywords: login, password, authenticate, credentials, mfa, 2fa
- Imports: bcrypt, argon2, passlib, jwt, oauthlib
- Files: **/auth/**, **/login.py, **/authentication/**
- Functions: authenticate(), login(), verify_password()

**Load progression:**
1. Overview: Password security principles (2k)
2. Rules: Hashing requirements, MFA patterns (5k)
3. Full: All 45 authentication rules + agent (15k)

### Cryptography Domain
**Auto-activate when:**
- Keywords: encrypt, decrypt, hash, cipher, crypto, key
- Imports: hashlib, cryptography, pycryptodome, Crypto
- Code patterns: hashlib.md5, hashlib.sha1, DES, 3DES
- Functions: encrypt(), hash(), generate_key()

**Load progression:**
1. Overview: Crypto best practices (2k)
2. Rules: Algorithm requirements, key management (5k)
3. Full: All crypto rules + agent (12k)

[... similar for all 15+ security domains ...]
```

#### Option C: Smart Context Manager (Future)

Build automated context orchestration:

```python
# .claude/context-manager.py
class SecurityContextManager:
    """Intelligent security context loading based on work analysis"""

    def analyze_work_context(self, user_story=None, files=None, diff=None):
        """Detect which security domains are relevant"""
        domains = set()

        # Story analysis
        if user_story:
            domains.update(self._extract_domains_from_story(user_story))

        # Code analysis
        if files:
            for file_path in files:
                domains.update(self._extract_domains_from_code(file_path))

        # Diff analysis
        if diff:
            domains.update(self._extract_domains_from_diff(diff))

        return self._load_targeted_context(domains)

    def _extract_domains_from_code(self, file_path):
        """Extract security domains from code imports/patterns"""
        domains = set()
        code = read_file(file_path)

        # Import analysis
        if 'import jwt' in code or 'import bcrypt' in code:
            domains.add('authentication')
        if 'import hashlib' in code or 'import cryptography' in code:
            domains.add('cryptography')
        if 'request.form' in code or 'request.args' in code:
            domains.add('input-validation')

        # Pattern analysis
        if 'os.getenv' in code or 'API_KEY' in code:
            domains.add('secrets-management')
        if 'session[' in code or 'jwt.encode' in code:
            domains.add('session-management')

        return domains

    def _load_targeted_context(self, domains):
        """Load only relevant security knowledge progressively"""
        context = {}
        for domain in domains:
            context[domain] = {
                'overview': self._load_overview(domain),      # 2k tokens
                'rules': None,                                 # Load on-demand
                'agent': self._get_agent_for_domain(domain)   # Reference only
            }
        return context
```

### Real-World Workflow Example

**User story:** "Implement user login with JWT authentication"

```javascript
// === STEP 1: Automatic Detection ===
Claude analyzes story keywords: "login", "JWT", "authentication"

Domains detected:
- authentication (login mention)
- session-management (JWT mention)
- secrets-management (JWT signing keys implied)

// === STEP 2: Targeted Context Loading ===
Auto-load Level 1 overviews:
- authentication-security/overview.md (2k tokens)
- session-management-security/overview.md (2k tokens)
- secrets-management/overview.md (2k tokens)
Total: 6k tokens

Claude now has context for:
- Password hashing best practices
- JWT validation requirements
- Secret key storage patterns

// === STEP 3: Code Creation with Loaded Context ===
def login(username, password):
    user = get_user(username)
    # Claude suggests with loaded authentication context:
    # ✅ Use bcrypt/argon2 for hashing
    if bcrypt.verify(password, user.password_hash):
        # Claude suggests with loaded session context:
        # ✅ Use strong JWT signing algorithm
        token = jwt.encode(
            {'user_id': user.id},
            # Claude suggests with loaded secrets context:
            # ✅ Load key from environment variables
            os.getenv('JWT_SECRET_KEY'),
            algorithm='HS256'
        )
        return token

// === STEP 4: Progressive Escalation on Violations ===
# Developer accidentally writes:
hash = hashlib.md5(password.encode())  # VIOLATION!

Claude detects violation:
→ Escalates to Level 2: Load crypto rules (5k tokens)
→ Identifies: MD5 prohibited for passwords
→ Escalates to Level 3: Load full crypto rules + invoke agent (15k tokens)
→ Generates: Detailed fix with bcrypt example and reasoning

// === STEP 5: Final Validation ===
Before commit:
→ Run targeted validation (only loaded domains)
→ authentication-specialist validates password handling
→ session-management-specialist validates JWT implementation
→ secrets-specialist validates key management

If all pass: commit
If failures: load full context + generate remediation
```

**Token usage in this workflow:**
- Initial detection: 0 tokens
- Level 1 loading: 6k tokens
- Code creation guidance: 2k tokens
- Violation detection + Level 3: 15k tokens (only if MD5 used)
- **Total: 8k tokens (no violations) or 23k tokens (with violations)**
- **Compare to: 36k tokens (manual full agent loading)**

### Implementation Recommendation

**Phased approach:**

**Phase 1: CLAUDE.md Enhancement (Start Here - Low Effort)**
- Add domain trigger definitions to CLAUDE.md
- Document progressive loading rules
- Claude follows guidance automatically
- **Effort:** 2-3 hours
- **Benefit:** Immediate 40% token reduction

**Phase 2: Skill Auto-Activation (Medium Effort)**
- Add `auto_activate_on` frontmatter to skills
- Implement trigger matching logic
- Build progressive disclosure in skills
- **Effort:** 1-2 days per skill (15 skills = 2-3 weeks)
- **Benefit:** True automatic activation

**Phase 3: Smart Context Manager (Future - High Effort)**
- Build standalone context orchestration system
- Automated domain detection from code/diffs
- Integration with CI/CD pipelines
- **Effort:** 2-3 weeks
- **Benefit:** Fully automated, zero manual intervention

### Key Insight: Context Management is Neither Skills Nor Agents

This is a **third architectural layer** that orchestrates skills/agents:

```
┌─────────────────────────────────────────────────────────┐
│ Context Management Layer (NEW)                          │
│ - Detects security domains from work context            │
│ - Loads targeted knowledge progressively                │
│ - Activates agents when violations found                │
└─────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────┴─────────────────┐
        ↓                                   ↓
┌───────────────────┐            ┌──────────────────────┐
│ Skills Layer      │            │ Agents Layer         │
│ - Discovery       │            │ - Execution          │
│ - Learning        │            │ - Validation         │
│ - Composition     │            │ - Parallel analysis  │
└───────────────────┘            └──────────────────────┘
```

**This answers your core question:**
> "How do we ensure that the right knowledge is loaded so that code created/edited/reviewed has the right knowledge applied?"

**Answer:** Build an automatic context management layer that detects domains and progressively loads targeted knowledge based on actual work being done.

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
