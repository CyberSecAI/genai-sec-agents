# Claude Skills for Security Analysis

**Status**: ✅ Phase 1 COMPLETE (2025-11-10) | 11/11 security domain skills operational

📖 **START HERE**:
- **[SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)** - Complete architecture with diagrams (what/why/how)
- **[SKILLS_ARCHITECTURE_VALIDATED.md](SKILLS_ARCHITECTURE_VALIDATED.md)** - Phase 0 validation findings

---

## The Knowledge Access Architecture

**Given a body of security knowledge (OWASP, ASVS, CWE), how do LLMs access it?**

This repository implements **four complementary access patterns**, each optimized for different use cases:

### 1. **Skills** (Progressive Context Injection)
- **What**: Modular resources loaded into Claude Code sessions on-demand
- **How**: Slash commands (`/authentication-security`) or explicit requests
- **When**: User-facing security guidance, progressive disclosure for token efficiency
- **Tokens**: 2k-12k (staged loading, 20-87% savings vs agents)
- **Activation**: Deterministic (slash) or probabilistic (semantic matching)
- **Context**: Injected into current conversation, stays loaded

### 2. **Agents** (Task Delegation)
- **What**: Specialized sub-agents with full rule sets loaded upfront
- **How**: Task tool calls via CLAUDE.md orchestration patterns
- **When**: Parallel analysis, deep validation, autonomous research
- **Tokens**: 15k+ (full rule set loaded immediately)
- **Activation**: Explicit Task tool calls, CLAUDE.md pattern triggers
- **Context**: Separate execution context, returns results

### 3. **Semantic Search** (Corpus Research)
- **What**: Vector search over 119 OWASP/ASVS documents
- **How**: `semantic-search` agent or `semsearch.sh` tool
- **When**: Finding best practices, researching unfamiliar topics, standards lookup
- **Tokens**: Variable (depends on query/results)
- **Activation**: Explicit tool invocation
- **Context**: Returns relevant document excerpts

### 4. **CLAUDE.md Orchestration** (Workflow Automation)
- **What**: Rules and patterns that trigger security workflows automatically
- **How**: Pattern matching on code changes, security keywords, file paths
- **When**: Pre-implementation guards, review patterns, security enforcement
- **Tokens**: 0 (patterns only, triggers other mechanisms)
- **Activation**: Automatic based on user actions
- **Context**: Orchestrates skills/agents/search

### Access Pattern Comparison

| Pattern | Activation | Token Cost | Use Case | Context |
|---------|-----------|------------|----------|---------|
| **Skills** | Deterministic (slash) or probabilistic | 2k-12k | User-facing guidance, progressive disclosure | Injected into session |
| **Agents** | Explicit (Task tool) | 15k+ | Parallel analysis, deep validation | Separate execution |
| **Semantic Search** | Explicit (tool) | Variable | Standards research, best practices lookup | Returns excerpts |
| **CLAUDE.md** | Automatic (patterns) | 0 | Workflow orchestration, security enforcement | Triggers others |

### The Hybrid Model (Recommended)

**Use all four together** for maximum effectiveness:

1. **CLAUDE.md** detects security-relevant changes → triggers workflows
2. **Semantic Search** researches OWASP/ASVS best practices → finds guidance
3. **Skills** provide user-facing guidance → progressive disclosure saves tokens
4. **Agents** perform deep analysis → parallel validation, autonomous tasks

**Resilience Through Redundancy**: Multiple access patterns provide **automatic fallback mechanisms** (validated in Phase 0 testing):
- If skills fail to load → Claude Code autonomously invokes semantic search or agents
- If one pattern is unavailable → Alternative patterns compensate
- Probabilistic activation → Deterministic slash commands as backup
- This redundancy ensures security knowledge is always accessible

**Example Flow**:
```
User: "Review authenticate_user() for security issues"
↓
CLAUDE.md pattern: "review.*authenticate" → triggers authentication workflow
↓
Semantic Search: Find OWASP authentication best practices
↓
Skill: Load authentication-security (2k tokens, overview)
↓
Agent: authentication-specialist for deep validation (15k tokens, full rules)
↓
Result: ASVS-aligned findings with secure code examples
```

⚠️ **IMPORTANT**: Skills + CLAUDE.md + Agents is a **THREE-COMPONENT ARCHITECTURE**. All three are essential (proven via isolation testing). No single component works optimally alone.

📖 **For detailed decision guidance**: See [SKILLS_VS_AGENTS.md](./SKILLS_VS_AGENTS.md) for:
- When to use skills vs agents vs semantic search
- Decision trees and selection criteria
- Performance characteristics and trade-offs
- Concrete examples and anti-patterns

---

## Quick Start: Deterministic Activation (Bypass Probabilistic Matching)

**Don't rely on auto-activation!** Skills use semantic matching which is probabilistic. For security-critical work, use these **guaranteed activation methods**:

### Method 1: Slash Commands (Highest Reliability)
```
/authentication-security - Load authentication skill
/session-management - Load session security skill (when available)
/secrets-management - Load secrets handling skill (when available)
```

### Method 2: Explicit Skill Requests
```
"use authentication-security skill to review this login flow"
"load the authentication-security skill"
```

### Method 3: Direct Agent Calls (Via CLAUDE.md Orchestration)
```
"use authentication-specialist agent to analyze src/auth/"
CLAUDE.md pattern triggers automatically call agents for security tasks
```

**Reliability Guarantee**: Slash commands and explicit requests = 100% activation. Auto-activation via semantic matching = 0% in isolation tests without CLAUDE.md.

---

## What are Skills?

**Skills** are modular, composable resources that extend Claude's capabilities with:
- **Progressive disclosure**: Load context incrementally (save tokens)
- **Rich examples**: Concrete code snippets and patterns
- **Composability**: Skills reference and build on each other
- **Discoverability**: Clear capabilities and usage patterns

## Skills vs Agents

| Feature | Skills (`.claude/skills/`) | Agents (`.claude/agents/`) |
|---------|---------------------------|---------------------------|
| **Purpose** | Discovery & composition | Execution & automation |
| **Loading** | Progressive (incremental) | All-at-once |
| **Invocation** | Natural language | Task tool (programmatic) |
| **Parallel** | Via agent delegation | Native support |
| **Examples** | Rich code samples | Minimal examples |
| **Best For** | Learning, exploration | CI/CD, automation |

**Recommendation:** Use **both** in a hybrid architecture (see [SKILLS_VS_AGENTS.md](./SKILLS_VS_AGENTS.md))

## Available Skills

### Core Security Skills

1. **[authentication-security](./authentication-security/SKILL.md)** ✅
   - User authentication and login mechanisms
   - Multi-factor authentication (MFA)
   - Password security and hashing
   - Credential management
   - **49 security rules** | ASVS, OWASP, CWE aligned

2. **[authorization-security](./authorization-security/SKILL.md)** ✅
   - Role-based access control (RBAC)
   - Permission model design and validation
   - Privilege escalation prevention
   - Access control enforcement
   - Insecure Direct Object References (IDOR) prevention
   - **13 security rules** | ASVS, OWASP, CWE aligned

3. **[secrets-management](./secrets-management/SKILL.md)** ✅
   - API key security and storage
   - Hardcoded secret detection (passwords/tokens in code)
   - Database credential protection
   - JWT signing secret validation
   - Cloud credential management (AWS/Azure/GCP)
   - Environment variable security
   - Secret rotation policies
   - **4 security rules** | ASVS, OWASP, CWE aligned

4. **[session-management](./session-management/SKILL.md)** ✅
   - Session lifecycle management (create, validate, destroy)
   - Session token security and validation
   - Session fixation/hijacking prevention
   - Cookie security (HttpOnly/Secure/SameSite)
   - Session timeout and expiration
   - **22 security rules** | ASVS, OWASP, CWE aligned

5. **[input-validation](./input-validation/SKILL.md)** ✅
   - SQL injection prevention and detection
   - NoSQL injection prevention
   - Command injection prevention
   - Cross-Site Scripting (XSS) prevention
   - Input sanitization and validation
   - Output encoding (HTML/JavaScript/URL)
   - **6 security rules** | ASVS, OWASP, CWE aligned

6. **[jwt-security](./jwt-security/SKILL.md)** ✅
   - JWT signature verification and validation
   - JWT algorithm security (preventing 'none' algorithm attacks)
   - JWT key management and rotation
   - JWT expiration and claims validation
   - **4 security rules** | ASVS, OWASP, CWE aligned

### Specialized Skills

7. **[logging-security](./logging-security/SKILL.md)** ✅
   - Security event logging and audit trails
   - Sensitive data exposure in logs (passwords, tokens, PII)
   - Log injection prevention (CRLF injection, log forging)
   - Log tampering and integrity protection
   - Security monitoring and alerting
   - **18 security rules** | ASVS, OWASP, CWE aligned

8. **[secure-configuration](./secure-configuration/SKILL.md)** ✅
   - Secure default configuration review
   - Security hardening and configuration management
   - TLS/SSL configuration and cipher suites
   - Database security configuration
   - Production security settings review
   - Security headers configuration
   - **16 security rules** | ASVS, OWASP, CWE aligned

9. **[data-protection](./data-protection/SKILL.md)** ✅
   - Data privacy and protection reviews
   - GDPR and CCPA compliance validation
   - Encryption at rest and in transit
   - PII (Personally Identifiable Information) handling
   - Sensitive data classification and tagging
   - Data minimization and retention policies
   - **14 security rules** | ASVS, GDPR, CCPA aligned

10. **[web-security](./web-security/SKILL.md)** ✅
    - Cross-Site Scripting (XSS) prevention and detection
    - Cross-Site Request Forgery (CSRF) protection
    - Clickjacking prevention (X-Frame-Options, CSP)
    - Content Security Policy (CSP) implementation
    - Security headers configuration
    - Cookie security (HttpOnly, Secure, SameSite)
    - **9 security rules** | ASVS, OWASP, CWE aligned

11. **[cryptography](./cryptography/SKILL.md)** ✅
    - Weak cryptographic algorithm detection (MD5, SHA1, DES)
    - Strong cryptography recommendations (AES-256, RSA-2048+)
    - Cryptographically secure random number generation
    - Password hashing best practices (bcrypt, Argon2)
    - Encryption key management and rotation
    - **8 security rules** | ASVS, NIST, OWASP aligned

## Usage Examples

### Example 1: Interactive Learning

```
You: What are your authentication security capabilities?

Claude: [Loads authentication-security skill]
I'm equipped with authentication security expertise covering:
- User authentication (login, SSO, OAuth)
- Multi-factor authentication (TOTP, SMS, hardware tokens)
- Password security (bcrypt, Argon2, policies)
- Credential management (storage, rotation)

Based on 45 security rules aligned with ASVS, OWASP, and CWE.
[Progressive disclosure: Overview → Details → Examples]
```

### Example 2: Secure Implementation Guidance

```
You: Show me how to implement secure password hashing using authentication-security skill

Claude: [Loads authentication-security skill + examples]
Here's secure password hashing following AUTH-PASSWORD-HASH-001:

[Shows concrete code example with bcrypt]
[Explains why MD5/SHA1 are insecure]
[References ASVS V2.4.1]
```

### Example 3: Multi-Skill Composition

```
You: Review authentication system using authentication-security, session-security, and secrets-management skills

Claude: I'll compose these three skills for comprehensive analysis:

1. Authentication-security → Login mechanism review
   [Loads auth skill overview]

2. Session-security → Post-auth session handling
   [Loads session skill overview]

3. Secrets-management → Credential storage
   [Loads secrets skill overview]

[Then executes via parallel agents for full analysis]
```

### Example 4: Automated Validation (via Agent)

```
Pre-commit hook: Validate authentication changes

[Uses authentication-specialist agent directly]
→ Fast parallel execution
→ Programmatic invocation
→ Full context loaded immediately
```

## Skill Structure

Each skill directory contains:

```
authentication-security/
├── SKILL.md              # Entry point with progressive disclosure
├── rules.json           # Symlink to compiled rule set
├── examples/            # (Optional) Code examples
│   ├── secure-login.py
│   └── mfa-implementation.py
└── detection-patterns.md # (Optional) Semgrep/CodeQL patterns
```

### SKILL.md Format

```markdown
---
name: skill-name
description: Brief description
version: 1.0.0
domains: [domain1, domain2]
tools: [Read, Grep, Bash]
---

# Skill Name

## Skill Capabilities
[What this skill can do - loads first]

## Usage Patterns
[When to activate this skill]

## Examples
[Concrete code examples - loads on demand]

## Integration with Other Skills
[How to compose with other skills]

## Progressive Disclosure
[Deeper resources available on demand]
```

## Hybrid Architecture

**Best Practice:** Use skills AND agents together

```
┌─────────────────────────────────────────────┐
│ Skills Layer (.claude/skills/)             │
│ → Discovery, learning, composition         │
│ → Progressive disclosure                    │
│ → Token-efficient                           │
└─────────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────────┐
│ Agents Layer (.claude/agents/)             │
│ → Execution, automation                     │
│ → Parallel processing                       │
│ → Programmatic invocation                   │
└─────────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────────┐
│ Rule Sets (.claude/agents/json/)           │
│ → Shared by both skills and agents         │
│ → Single source of truth                    │
└─────────────────────────────────────────────┘
```

### When to Use Each

**Use Skills:**
- 🎓 Learning secure coding patterns
- 🔍 Exploring security capabilities
- 📚 Understanding requirements
- 🧩 Composing multi-domain workflows
- 💰 Saving tokens (progressive loading)

**Use Agents:**
- ⚡ Fast parallel execution
- 🤖 Automated CI/CD validation
- 🔧 Programmatic invocation
- 🔄 Pre-commit hooks
- 📊 Batch security scanning

**Use Both (Hybrid):**
- 🎯 Skills define workflow
- ⚙️ Agents execute steps
- 🔬 Skills provide context
- 🚀 Agents provide speed

## Token Efficiency

### Progressive Loading Example

**Traditional Agent:**
```
Load full agent: 15k tokens
[All 45 rules + instructions + patterns loaded upfront]
```

**Skill with Progressive Disclosure:**
```
Step 1: Overview           2k tokens
Step 2: Examples (if needed)   +3k tokens
Step 3: Full rules (if needed) +5k tokens
Step 4: Detection (if needed)  +2k tokens
────────────────────────────────────────
Total: 2k - 12k tokens (only what's needed)
```

**Savings:** 20-87% token reduction for simple queries

## Migration Status

| Agent | Skill | Status | Priority |
|-------|-------|--------|----------|
| `authentication-specialist` | `authentication-security` | ✅ Complete | High |
| `secrets-specialist` | `secrets-management` | ✅ Complete | High |
| `session-management-specialist` | `session-management` | ✅ Complete | High |
| `input-validation-specialist` | `input-validation` | ✅ Complete | Medium |
| `authorization-specialist` | `authorization-security` | ✅ Complete | Medium |
| `jwt-specialist` | `jwt-security` | ✅ Complete | Medium |
| `logging-specialist` | `logging-security` | ✅ Complete | Low |
| `configuration-specialist` | `secure-configuration` | ✅ Complete | Low |
| `data-protection-specialist` | `data-protection` | ✅ Complete | Low |
| `web-security-specialist` | `web-security` | ✅ Complete | Medium |
| `cryptography-specialist` | `cryptography` | ✅ Complete | High |

## Getting Started

### For Users

1. **Discover capabilities:**
   ```
   What security skills are available?
   ```

2. **Activate a skill:**
   ```
   Use authentication-security skill to review my login code
   ```

3. **Compose multiple skills:**
   ```
   Analyze authentication using authentication-security and session-security skills
   ```

### For Developers

1. **Review example:**
   ```bash
   cat .claude/skills/authentication-security/SKILL.md
   ```

2. **Follow migration guide:**
   ```bash
   cat .claude/skills/MIGRATION_GUIDE.md
   ```

3. **Run migration script:**
   ```bash
   .claude/skills/migrate-agents-to-skills.sh
   ```

## Documentation

- **[MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)** - How to convert agents to skills
- **[SKILLS_VS_AGENTS.md](./SKILLS_VS_AGENTS.md)** - Detailed comparison and decision matrix
- **[Example: authentication-security](./authentication-security/SKILL.md)** - Complete skill example

## Contributing

When creating new skills:

1. Follow the SKILL.md template
2. Include progressive disclosure (overview → details → examples)
3. Add concrete code examples
4. Document integration with other skills
5. Symlink to existing JSON rules (don't duplicate)
6. Keep corresponding agent for parallel execution

## Questions?

- **"Should I use skills or agents?"** → See [SKILLS_VS_AGENTS.md](./SKILLS_VS_AGENTS.md)
- **"How do I migrate an agent?"** → See [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)
- **"Can I use both?"** → Yes! Hybrid architecture recommended
- **"What about parallel execution?"** → Use agents for parallel, skills for composition

---

**Skills Status:** 11/11 complete (Phase 1 migration 100% complete ✅)
**Architecture:** Hybrid (skills + agents) recommended
**Token Efficiency:** 20-87% savings with progressive disclosure
**Backward Compatible:** Yes, agents unchanged
