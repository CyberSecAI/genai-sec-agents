# Security Knowledge System: Complete Architecture

**Purpose**: Transform security standards (OWASP, ASVS) into actionable guidance through multiple access patterns

---

## System Overview Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: SOURCE DOCUMENTS (research/)                                   │
│                                                                         │
│  research/search_corpus/                                                │
│  ├── owasp/              102 OWASP CheatSheets (processed)              │
│  │   ├── Authentication_Cheat_Sheet.md                                  │
│  │   ├── Session_Management_Cheat_Sheet.md                              │
│  │   └── ... (100 more)                                                 │
│  └── asvs/               17 ASVS standards (processed)                  │
│      ├── V2-Authentication.md                                           │
│      ├── V3-Session-Management.md                                       │
│      └── ... (15 more)                                                  │
│                                                                         │
│  Purpose: Original security knowledge (OWASP, ASVS standards)           │
│  Access: Semantic search, grep, direct reading                          │
└─────────────────────────────────────────────────────────────────────────┘
                               ↓ refactored into
┌─────────────────────────────────────────────────────────────────────────┐
│ LAYER 2: ATOMIC DOMAIN KNOWLEDGE (app/rule_cards/)                      │
│                                                                         │
│  app/rule_cards/                                                        │
│  ├── authentication/     45 rules (AUTH-*)                              │
│  │   ├── AUTH-PASSWORD-HASH-001.yml                                     │
│  │   ├── AUTH-LOGIN-MECHANISM-001.yml                                   │
│  │   └── ... (43 more)                                                  │
│  ├── session_management/ 22 rules (SESSION-*)                           │
│  ├── secrets/            8 rules (SECRET-*)                             │
│  ├── authorization/      13 rules (AUTHZ-*)                             │
│  └── ... (16 more domains, 197 rules total)                             │
│                                                                         │
│  Purpose: Atomic, testable security rules extracted from standards      │
│  Format: YAML with rule_id, description, severity, cwe, asvs refs       │
│  Tool: app/tools/compile_agents.py (creates domain-specific JSON)       │
└─────────────────────────────────────────────────────────────────────────┘
                               ↓ compiled into
┌─────────────────────────────────────────────────────────────────────────┐
│ LAYER 3: COMPILED RULE SETS (.claude/agents/json/)                      │
│                                                                         │
│  .claude/agents/json/                                                   │
│  ├── authentication_rules.json  (45 rules compiled)                     │
│  ├── session_rules.json         (22 rules compiled)                     │
│  ├── secrets_rules.json         (8 rules compiled)                      │
│  └── ... (197 rules total across 20 domains)                            │
│                                                                         │
│  Purpose: Optimized JSON for fast loading by agents/skills              │
│  Shared by: Both agents (.claude/agents/) and skills (.claude/skills/)  │
└─────────────────────────────────────────────────────────────────────────┘
              ↓ loaded by (two access patterns) ↓
┌──────────────────────────────┬──────────────────────────────────────────┐
│ LAYER 4A: AGENTS             │ LAYER 4B: SKILLS                         │
│ (Programmatic)               │ (Interactive)                            │
│                              │                                          │
│ .claude/agents/              │ .claude/skills/                          │
│ ├── authentication-          │ ├── authentication-security/             │
│ │   specialist.md            │ │   ├── SKILL.md (progressive)           │
│ │   (loads auth rules.json)  │ │   ├── rules.json → symlink             │
│ │                            │ │   └── examples/                        │
│ ├── session-management-      │ ├── session-security/                    │
│ │   specialist.md            │ │   └── ... (same structure)             │
│ │   (loads session rules)    │ └── ... (12 skills total)                │
│ └── semantic-search.md       │                                          │
│     (searches research/)     │ Purpose: Interactive learning,           │
│                              │ progressive disclosure, composition      │
│ Purpose: Fast execution,     │ Activation: Natural language OR          │
│ parallel processing          │ slash commands (/auth-security)          │
│ Activation: Task tool        │                                          │
└──────────────────────────────┴──────────────────────────────────────────┘
                               ↑ orchestrated by
┌─────────────────────────────────────────────────────────────────────────┐
│ LAYER 5: WORKFLOW ORCHESTRATION (CLAUDE.md)                             │
│                                                                         │
│  CLAUDE.md (Lines 201-359: SECURITY-FIRST DEVELOPMENT WORKFLOW)         │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────┐      │
│  │ Pattern Triggers (lines 232-245)                              │      │
│  │ ──────────────────────────────────────────────────────────────│      │
│  │ oauth|jwt|token → session-management-specialist               │      │
│  │ password|login|auth → authentication-specialist               │      │
│  │ api_key|secret → secrets-specialist                           │      │
│  │ ... (auto-detects security tasks)                             │      │
│  └───────────────────────────────────────────────────────────────┘      │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────┐      │
│  │ Workflow Steps (lines 321-339)                                │      │
│  │ ──────────────────────────────────────────────────────────────│      │
│  │ STEP 1: Research security guidance (semantic-search)          │      │
│  │ STEP 2: Get implementation guidance (specialists)             │      │
│  │ STEP 3: Implement with loaded context                         │      │
│  │ STEP 4: Validate implementation                               │      │
│  └───────────────────────────────────────────────────────────────┘      │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────┐      │
│  │ Multi-Agent Orchestration (lines 350-358)                     │      │
│  │ ──────────────────────────────────────────────────────────────│      │
│  │ Parallel execution for performance                            │      │
│  │ Multiple specialists for multi-domain tasks                   │      │
│  └───────────────────────────────────────────────────────────────┘      │
│                                                                         │
│  Purpose: Active workflow engine that orchestrates when/how to          │
│  access knowledge based on task type                                    │
└─────────────────────────────────────────────────────────────────────────┘
                               ↓ delivers via
┌─────────────────────────────────────────────────────────────────────────┐
│ LAYER 6: ACCESS TOOLS (How knowledge is retrieved)                      │
│                                                                         │
│  ┌─────────────────┬─────────────────┬────────────────────────────┐     │
│  │ Semantic Search │ Direct Grep     │ Agent/Skill Loading        │     │
│  │ ──────────────  │ ───────────     │ ──────────────────────     │     │
│  │ semsearch.sh    │ Grep tool       │ Task tool → agents         │     │
│  │ search command  │ grep patterns   │ Skill tool → skills        │     │
│  │                 │                 │ SlashCommand → /auth-sec   │     │
│  │ Searches:       │ Searches:       │ Loads:                     │     │
│  │ research/       │ research/       │ rules.json + SKILL.md      │     │
│  │ (corpus)        │ app/rule_cards/ │ (compiled knowledge)       │     │
│  │                 │ .yml files      │                            │     │
│  └─────────────────┴─────────────────┴────────────────────────────┘     │
│                                                                         │
│  Purpose: Multiple ways to access the same underlying knowledge         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## The Five Key Points (Your Requirements)

### 1. ✅ Info in Documents (research/)

**What**: Original security standards from authoritative sources

**Where**: `research/search_corpus/`
- 102 OWASP CheatSheets (processed for search)
- 17 ASVS standards (processed for search)

**Purpose**: Source of truth for security best practices

**Access Patterns**:
- **Semantic search**: `semsearch.sh "password hashing best practices"`
- **Grep**: `grep -r "bcrypt" research/`
- **Direct read**: Via agents (semantic-search agent)

**Example Flow**:
```
User: "What's the minimum password length?"
→ CLAUDE.md triggers semantic-search agent
→ Agent runs semsearch.sh on research/
→ Returns OWASP Password Storage CheatSheet + ASVS V2.1
→ Provides answer with citations
```

### 2. ✅ Refactored into Atomic Domains (app/rule_cards/)

**What**: Security standards broken into testable, atomic rules

**Where**: `app/rule_cards/{domain}/{RULE-ID}.yml`

**Domains** (20 total):
- `authentication/` - 45 rules
- `session_management/` - 22 rules
- `secrets/` - 8 rules
- `authorization/` - 13 rules
- `input_validation/` - 6 rules
- ... (15 more, 197 total rules)

**Rule Structure** (YAML):
```yaml
rule_id: AUTH-PASSWORD-HASH-001
title: Use Strong Password Hashing
severity: CRITICAL
description: |
  Passwords MUST be hashed using bcrypt, Argon2id, or scrypt.
  NEVER use MD5, SHA1, or unsalted SHA-256.
cwe: CWE-327
asvs: V2.4.1, V2.4.5
owasp: Authentication CheatSheet
detection_patterns:
  - hashlib.md5
  - hashlib.sha1
secure_example: |
  import bcrypt
  hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

**Why Atomic**: Each rule is independently testable, trackable, and composable

**Tool**: `app/tools/compile_agents.py` compiles YAML → JSON

### 3. ✅ Explicit & Implicit Access

**Explicit Access** (User-Initiated):
- Manual skill invocation: `/authentication-security`
- Direct agent call: `use authentication-specialist agent`
- Query: "Show me authentication security capabilities"

**Implicit Access** (Auto-Triggered by CLAUDE.md):
- User: "Add OAuth2 login" → CLAUDE.md detects "oauth" → Triggers agents
- User: "Hash passwords" → CLAUDE.md detects "password" → Loads auth skill
- User: "Review login code" → CLAUDE.md detects "login" → Security analysis

**How Implicit Works**:
1. CLAUDE.md pattern triggers (lines 232-245) detect keywords
2. Auto-invokes appropriate agents/skills
3. Context injected before user sees response
4. Security-first workflow enforced

**Example**:
```
User: "Implement password reset"  [Implementation task]
↓
CLAUDE.md detects: "password" keyword + implementation intent
↓
Triggers STEP 1-2 (BEFORE coding):
  - semantic-search agent → searches research/
  - authentication-specialist → loads auth rules.json
↓
Provides guidance with ASVS citations
↓
User decides whether to implement
```

### 4. ✅ Data Arranged as Agents & Skills

**Why Both?**

| Aspect | Agents (.claude/agents/) | Skills (.claude/skills/) |
|--------|-------------------------|-------------------------|
| **Access** | Programmatic (Task tool) | Interactive (natural language) |
| **Loading** | All-at-once (fast) | Progressive (token-efficient) |
| **Activation** | Deterministic (explicit call) | Probabilistic (semantic matching) |
| **Best For** | Execution, automation | Learning, exploration |
| **Examples** | Minimal | Rich code samples |
| **Parallel** | Native (multiple agents) | Via agent delegation |

**Both Share**: Same compiled rules.json (single source of truth)

**Critical Difference**:
- **Agents**: Deterministic - when called via Task tool, they WILL execute
- **Skills**: Probabilistic - may or may not load based on semantic matching
- **Skills**: Claude may interpret as commands OR context (non-deterministic)
- **CLAUDE.md**: Provides deterministic orchestration over probabilistic skills

**Agent Example** (authentication-specialist.md):
```markdown
You are an authentication security specialist.

Load: .claude/agents/json/authentication_rules.json (45 rules)

Execute: Fast security analysis with full context
```

**Skill Example** (authentication-security/SKILL.md):
```markdown
# Authentication Security Skill

## Overview (loads first - 2k tokens)
Covers login, passwords, MFA, credentials

## Examples (loads on demand - 3k tokens)
[Concrete code examples]

## Full Rules (loads if needed - 5k tokens)
→ Symlinks to authentication_rules.json
```

**Semantic Search & Grep Support**:
- **Semantic search**: `semsearch.sh` searches research/corpus directly
- **Grep**: Can search both research/ and app/rule_cards/*.yml
- **Agents**: Load compiled JSON (fast)
- **Skills**: Progressive disclosure from compiled JSON

**All access patterns** can find the same information, optimized for different use cases.

### 5. ✅ CLAUDE.md for Implicit Invocation

**The Probabilistic Problem**:
- Skills have semantic matching → may or may not load
- Claude may interpret skills as commands vs context
- No deterministic control over WHEN knowledge applies
- Implementation tasks bypass research without explicit orchestration

**Without CLAUDE.md** (proven by isolation testing):
- Implementation tasks: Direct coding, NO security research ❌
- Query tasks: Bash tools research (lower quality) ⚠️
- Skills dormant or randomly activated (probabilistic) ❌

**With CLAUDE.md** (validated):
- Implementation tasks: Research FIRST, security-first workflow ✅
- Query tasks: Agent orchestration (higher quality) ✅
- Skills activated deterministically via agent calls ✅
- Probabilistic activation replaced with explicit orchestration

**How CLAUDE.md Enables Deterministic Invocation**:

```markdown
Lines 232-245: Pattern Triggers
──────────────────────────────
password|login|authenticate → authentication-specialist
oauth|jwt|token → session-management-specialist
api_key|secret → secrets-specialist

When Claude sees these keywords → Auto-loads relevant knowledge


Lines 321-339: Workflow Steps
──────────────────────────────
STEP 1: Research BEFORE implementing
STEP 2: Get guidance BEFORE coding
STEP 3: Implement WITH loaded context
STEP 4: Validate AFTER implementation

Enforces: Security-first workflow (research → guidance → code)


Lines 350-358: Multi-Agent Orchestration
─────────────────────────────────────────
For complex tasks (e.g., OAuth2):
  - Parallel: semantic-search + authentication + session + secrets
  - Efficient: All run simultaneously
  - Comprehensive: Multi-domain coverage

Result: Fast, complete security analysis
```

**Example Flow WITH CLAUDE.md**:
```
User: "Add OAuth2 login to app"
↓
CLAUDE.md (line 234): Detects "oauth" → Triggers workflow
↓
STEP 1 (line 323): Call semantic-search agent
  → Searches research/owasp/ for OAuth best practices
  → Returns OWASP OAuth CheatSheet content
↓
STEP 2 (lines 326-327): Call specialists in parallel
  → authentication-specialist (login mechanisms)
  → session-management-specialist (token handling)
  → secrets-specialist (client_secret protection)
  → All load from compiled rules.json
↓
Result: Comprehensive OAuth2 guidance with ASVS citations
Quality: 25/25 (exceptional)
Workflow: Research FIRST, implementation SECOND
```

**Example Flow WITHOUT CLAUDE.md** (A8-NO-CLAUDE test):
```
User: "Add OAuth2 login to app"
↓
(No pattern detection, no workflow)
↓
Direct implementation:
  - Edit secure_login.py (6 consecutive edits)
  - NO research, NO ASVS citations
  - Implemented from general knowledge
↓
Result: OAuth2 code without security compliance
Quality: Unknown (no standards consulted)
Workflow: Implementation ONLY (no research)
```

**Key Insight: CLAUDE.md Converts Probabilistic to Deterministic**

Skills alone:
- May or may not load (semantic matching)
- May be interpreted as commands vs context
- No control over timing or workflow

CLAUDE.md + Agents:
- Deterministic activation (explicit agent calls)
- Controlled timing (research BEFORE implementation)
- Structured workflow (STEP 1-4)
- Skills loaded via agents (reliable delivery)

**Result**: CLAUDE.md provides the deterministic orchestration layer that makes probabilistic skills reliable for security-critical work.

---

## Complete Data Flow Examples

### Flow 1: Implementation Task (OAuth2)

```
┌──────────────────────────────────────────────────────────────────┐
│ USER: "Add OAuth2 login support to the application"              │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ CLAUDE.md: Pattern detection (line 234)                          │
│ → Detected: "oauth" keyword                                      │
│ → Task type: Implementation                                      │
│ → Action: Trigger SECURITY-FIRST DEVELOPMENT WORKFLOW            │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 1: Research security guidance (line 323)                    │
│                                                                  │
│ semantic-search agent:                                           │
│ → Executes: semsearch.sh "OAuth2 security best practices"        │
│ → Searches: research/search_corpus/owasp/                        │
│ → Finds: OAuth_CheatSheet.md, Authentication_CheatSheet.md       │
│ → Returns: Relevant excerpts with citations                      │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 2: Get implementation guidance (lines 326-327, parallel)    │
│                                                                  │
│ authentication-specialist agent:                                 │
│ → Loads: .claude/agents/json/authentication_rules.json           │
│ → Applies: 45 authentication rules                               │
│ → Finds: AUTH-LOGIN-MECHANISM-*, AUTH-OAUTH-*                    │
│                                                                  │
│ session-management-specialist agent:                             │
│ → Loads: .claude/agents/json/session_rules.json                  │
│ → Applies: 22 session rules                                      │
│ → Finds: SESSION-TOKEN-*, SESSION-LIFECYCLE-*                    │
│                                                                  │
│ secrets-specialist agent:                                        │
│ → Loads: .claude/agents/json/secrets_rules.json                  │
│ → Applies: 8 secrets rules                                       │
│ → Finds: SECRET-STORAGE-*, SECRET-ROTATION-*                     │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ SYNTHESIS: Combine all loaded knowledge                          │
│                                                                  │
│ Sources:                                                         │
│ ✓ OWASP OAuth CheatSheet (from semantic-search)                  │
│ ✓ ASVS V2.2 OAuth requirements (from authentication rules)       │
│ ✓ Session token security (from session rules)                    │
│ ✓ Client secret protection (from secrets rules)                  │
│                                                                  │
│ Output: Comprehensive OAuth2 implementation guidance             │
│ Citations: ASVS 2.2.1, 2.2.3, OWASP OAuth CheatSheet             │
│ Quality: 25/25 (exceptional)                                     │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ RESPONSE TO USER:                                                │
│                                                                  │
│ "I'll help add OAuth2 login following secure authentication      │
│  best practices. Based on ASVS 2.2 and OWASP OAuth CheatSheet:   │
│                                                                  │
│  Key Requirements:                                               │
│  1. Use authorization code flow with PKCE                        │
│  2. Validate redirect URIs (ASVS 2.2.1)                          │
│  3. Secure token storage (ASVS 3.2.2)                            │
│  4. Implement token refresh (ASVS 2.2.3)                         │
│  5. Protect client_secret (SECRET-STORAGE-001)                   │
│                                                                  │
│  [Detailed guidance follows...]                                  │
│                                                                  │
│  Would you like me to implement this?"                           │
└──────────────────────────────────────────────────────────────────┘
```

**Timeline**: ~2 minutes (agents run in parallel)
**Knowledge Sources**: 4 (corpus + 3 rule sets)
**Total Rules Applied**: 75+ (45 auth + 22 session + 8 secrets)
**Outcome**: User gets comprehensive security guidance BEFORE any code is written

---

### Flow 2: Query Task (Password Length)

```
┌──────────────────────────────────────────────────────────────────┐
│ USER: "What's the minimum password length I should enforce?"     │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ CLAUDE.md: Pattern detection (line 232)                          │
│ → Detected: "password" keyword                                   │
│ → Task type: Query                                               │
│ → Action: Research answer                                        │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ Dual-Agent Workflow (parallel)                                   │
│                                                                  │
│ semantic-search agent:                                           │
│ → Searches: research/search_corpus/                              │
│ → Finds: Password_Storage_CheatSheet.md, ASVS V2.1               │
│ → Extracts: NIST SP800-63B recommendations                       │
│                                                                  │
│ authentication-specialist agent:                                 │
│ → Loads: authentication_rules.json                               │
│ → Finds: AUTH-PASSWORD-POLICY-001 (min length 8)                 │
│         AUTH-PASSWORD-STRENGTH-001 (complexity)                  │
│ → References: ASVS 6.2.1, 6.2.9, CWE-521                         │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ RESPONSE TO USER:                                                │
│                                                                  │
│ "Based on ASVS 6.2.1 and NIST SP800-63B:                         │
│                                                                  │
│  Minimum password length: 8 characters                           │
│  Recommended: 12-15 characters                                   │
│                                                                  │
│  However, ASVS 6.2.9 and OWASP recommend:                        │
│  - Allow passwords up to 128 characters                          │
│  - Complexity requirements are LESS important than length        │
│  - Consider passphrase support (4+ words)                        │
│                                                                  │
│  [References: ASVS 6.2.1, 6.2.9, NIST SP800-63B]"                │
└──────────────────────────────────────────────────────────────────┘
```

**Contrast WITHOUT CLAUDE.md** (A5-NO-CLAUDE):
```
Same query WITHOUT CLAUDE.md:
→ Uses: search command, semsearch.sh, grep (bash tools directly)
→ No agent orchestration
→ Raw tool output (lower quality synthesis)
→ Still researches, but less structured
```

**CLAUDE.md Value**: Agent orchestration + structured synthesis (50-70% improvement)

---

### Flow 3: Review Task

```
┌──────────────────────────────────────────────────────────────────┐
│ USER: "Review authenticate_user() function for security issues"  │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ CLAUDE.md: Pattern detection (line 232)                          │
│ → Detected: "authenticate" + "security" keywords ✓               │
│ → Task type: Review                                              │
│ → Action: Load authentication-security skill/agent               │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ Manual Skill Invocation (slash command)                          │
│                                                                  │
│ User's IDE: /authentication-security                             │
│ → Loads: authentication-security/SKILL.md                        │
│ → Loads: authentication_rules.json (45 rules)                    │
│ → Reads: vulnerable_login.py                                     │
│ → Applies: All 45 authentication rules                           │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ ANALYSIS: Check code against rules                               │
│                                                                  │
│ Violations Found (with ASVS citations):                          │
│ ✗ MD5 password hashing → AUTH-PASSWORD-HASH-001 (ASVS 2.4.1)     │
│ ✗ SQL injection → AUTH-LOGIN-MECHANISM-002 (ASVS 5.3.1)          │
│ ✗ Hardcoded secret → SECRET-STORAGE-001 (ASVS 2.10.1)            │
│ ✗ No rate limiting → AUTH-RATE-LIMIT-001 (ASVS 2.2.1)            │
│ ... (15 total vulnerabilities)                                   │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ RESPONSE: Detailed security review with standards                │
│                                                                  │
│ Found 15 security issues (7 CRITICAL, 5 HIGH, 3 MEDIUM):         │
│                                                                  │
│ 🔴 CRITICAL: MD5 password hashing (line 45)                      │
│    Violation: AUTH-PASSWORD-HASH-001                             │
│    ASVS: V2.4.1 (passwords MUST use bcrypt/Argon2)               │
│    CWE: CWE-327 (Use of broken crypto)                           │
│    Fix: Use bcrypt.hashpw() instead                              │
│                                                                  │
│ [14 more vulnerabilities with citations...]                      │
└──────────────────────────────────────────────────────────────────┘
```

**Note**: Review tasks work best with explicit "security" keyword or manual invocation.

---

## Capabilities Summary

### What the System Can Do

**1. Answer Security Questions**
- Query: "What's secure password hashing?"
- Access: semantic-search → research/corpus → OWASP Password CheatSheet
- Result: Answer with citations (ASVS 2.4.1, CWE-327)

**2. Provide Implementation Guidance**
- Query: "How do I implement OAuth2?"
- Access: Multi-agent (semantic-search + auth + session + secrets)
- Result: Step-by-step guidance with code examples and ASVS compliance

**3. Review Code for Security Issues**
- Query: "Review login.py for security issues"
- Access: authentication-specialist → loads 45 rules → applies to code
- Result: Detailed vulnerability report with ASVS/CWE citations

**4. Detect Vulnerabilities**
- Automatic: CLAUDE.md detects security keywords in prompts
- Access: Appropriate specialist agents load rules
- Result: Proactive security guidance before implementation

**5. Compose Multi-Domain Analysis**
- Complex task: OAuth2 requires auth + session + secrets expertise
- Access: Parallel agents, each loading their domain rules
- Result: Comprehensive multi-domain security analysis

### Access Patterns Supported

| Pattern | Use Case | Example | Knowledge Source |
|---------|----------|---------|------------------|
| **Semantic Search** | Find concepts | "password hashing best practices" | research/corpus |
| **Grep** | Find specifics | `grep -r "bcrypt"` | research/ + rule_cards/ |
| **Agent Loading** | Fast execution | authentication-specialist | Compiled rules.json |
| **Skill Loading** | Interactive learning | /authentication-security | Progressive SKILL.md |
| **Auto-Trigger** | Implicit context | "Add OAuth2" → agents | CLAUDE.md patterns |
| **Manual Invoke** | Explicit control | "Use auth skill" | User command |

**All patterns** access the same underlying knowledge, optimized for different workflows.

---

## Why This Architecture?

### Problem: Monolithic Security Knowledge

**Before**:
- 102 OWASP CheatSheets (unstructured documents)
- 17 ASVS standards (requirements lists)
- Hard to apply to specific code
- No programmatic access

### Solution: Multi-Layer Refactoring

**Layer 1** (research/): Preserve originals for search
**Layer 2** (rule_cards/): Extract atomic, testable rules
**Layer 3** (compiled JSON): Optimize for fast loading
**Layer 4** (agents/skills): Multiple access patterns
**Layer 5** (CLAUDE.md): Orchestrate when/how to access

### Benefits

1. **Explicit & Implicit Access**: User chooses OR system auto-triggers
2. **Multiple Patterns**: Query, implement, review, compose
3. **Single Source**: Same knowledge, different access methods
4. **Progressive Loading**: Token-efficient (2k to 95k based on need)
5. **Standards Aligned**: Every rule cites ASVS, OWASP, CWE
6. **Testable**: Atomic rules can be validated individually
7. **Composable**: Multi-domain analysis via parallel agents
8. **Fast**: Compiled JSON loads quickly
9. **Rich**: Original documents preserved for deep research

---

## Status

**Phase 0**: ✅ VALIDATED (2025-11-09)
- Skills + CLAUDE.md + Agents architecture proven essential
- Task-type dependency understood
- Known issues identified and fixable

**Phase 1**: 🚀 READY TO BEGIN
- Migrate 9 remaining agents to skills
- Fix A7 pattern gap (review tasks)
- Fix A4 timing issue (file-specific)
- Maintain hybrid architecture

**Current Capabilities**:
- ✅ 1/12 skills complete (authentication-security)
- ✅ 20/20 agent domains operational
- ✅ 197 security rules compiled
- ✅ 119 documents in search corpus
- ✅ CLAUDE.md orchestration validated

---

## Quick Reference

**Find security guidance**:
```bash
# Semantic search original documents
semsearch.sh "password hashing"

# Grep for specific patterns
grep -r "bcrypt" research/

# Load compiled rules
cat .claude/agents/json/authentication_rules.json

# Interactive skill
/authentication-security

# Auto-trigger (CLAUDE.md)
"Add OAuth2 login"  # Automatic security-first workflow
```

**Understand architecture**:
- [SKILLS_ARCHITECTURE_VALIDATED.md](SKILLS_ARCHITECTURE_VALIDATED.md) - Phase 0 validation
- [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) - This document
- [README.md](README.md) - Skills overview

**Phase 0 documentation**:
- validation/ISOLATION_EXPERIMENT_COMPLETE_ANALYSIS.md - Complete technical analysis
- ADR/ADR_NO_HOOKS_FOR_SKILL_LOADING.md - Architectural decision

---

**Key Insight**: This is not just "skills" or "agents" - it's a comprehensive security knowledge system with multiple access patterns, all orchestrated by CLAUDE.md to provide security-first development workflow.
