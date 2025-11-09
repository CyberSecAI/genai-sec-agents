# Claude Skills for Security Analysis

**Status**: ✅ Phase 0 VALIDATED (2025-11-09) | **Decision**: GO to Phase 1

📖 **START HERE**: [SKILLS_ARCHITECTURE_VALIDATED.md](SKILLS_ARCHITECTURE_VALIDATED.md) - Complete Phase 0 validation findings

This directory contains Claude Skills for specialized security analysis. Skills provide progressive context loading and composability while working alongside **CLAUDE.md and the agent system**.

⚠️ **IMPORTANT**: Skills + CLAUDE.md + Agents is a **THREE-COMPONENT ARCHITECTURE**. All three are essential (proven via isolation testing). Skills alone don't work for implementation tasks.

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
   - **45 security rules** | ASVS, OWASP, CWE aligned

2. **authorization-security** ⏳
   - Role-based access control (RBAC)
   - Permission models
   - Privilege management
   - **13 security rules**

3. **secrets-management** ⏳
   - API key security
   - Credential protection
   - Hardcoded secret detection
   - Secret rotation
   - **8 security rules**

4. **session-security** ⏳
   - Session lifecycle management
   - Token security
   - Session fixation prevention
   - **22 security rules**

5. **input-validation** ⏳
   - Injection prevention (SQL, XSS, Command)
   - Data sanitization
   - Schema validation
   - **6 security rules**

6. **jwt-security** ⏳
   - JWT token validation
   - Algorithm security
   - Key management
   - **4 security rules**

### Specialized Skills

7. **logging-security** ⏳
   - Security event logging
   - Audit trail requirements
   - Sensitive data in logs
   - **18 security rules**

8. **secure-configuration** ⏳
   - Secure defaults
   - Hardening guidelines
   - Configuration validation
   - **16 security rules**

9. **data-protection** ⏳
   - GDPR compliance
   - Encryption at rest
   - Data handling
   - **14 security rules**

10. **web-security** ⏳
    - XSS prevention
    - CSRF protection
    - Clickjacking defense

### Meta Skills

11. **security-research** ⏳
    - Semantic search over OWASP/ASVS
    - Standards lookup
    - Best practice guidance

12. **comprehensive-security** ⏳
    - Multi-domain analysis
    - Cross-cutting concerns
    - **191 total rules**

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
| `secrets-specialist` | `secrets-management` | ⏳ Pending | High |
| `session-management-specialist` | `session-security` | ⏳ Pending | High |
| `input-validation-specialist` | `input-validation` | ⏳ Pending | Medium |
| `authorization-specialist` | `authorization-security` | ⏳ Pending | Medium |
| `jwt-specialist` | `jwt-security` | ⏳ Pending | Medium |
| `logging-specialist` | `logging-security` | ⏳ Pending | Low |
| `configuration-specialist` | `secure-configuration` | ⏳ Pending | Low |
| `data-protection-specialist` | `data-protection` | ⏳ Pending | Low |
| `semantic-search` | `security-research` | ⏳ Pending | Low |

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

**Skills Status:** 1/12 complete (authentication-security ✅)
**Architecture:** Hybrid (skills + agents) recommended
**Token Efficiency:** 20-87% savings with progressive disclosure
**Backward Compatible:** Yes, agents unchanged
