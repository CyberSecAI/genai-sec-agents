# Agent to Skills Migration Guide

This guide explains how to convert Claude Code agents to Claude Skills format while preserving parallel execution capabilities.

## Overview

**Why Migrate to Skills?**
- **Progressive Disclosure**: Load context incrementally instead of all at once
- **Modularity**: Skills can reference supplementary files and resources
- **Composability**: Skills can be combined and reused across contexts
- **Discoverability**: Standardized format makes skills easier to find and use
- **Extensibility**: Skills can include executable code, not just instructions

**What We're Preserving:**
- **Parallel Execution**: Multiple skills can still run simultaneously
- **Agent Invocation**: Existing Task system continues to work
- **Rule Sets**: Compiled JSON rule sets remain unchanged
- **Tool Access**: Same tools (Read, Grep, Bash) available

## Architecture: Hybrid Skills + Agents

We're implementing a **two-layer architecture** that gives you the best of both worlds:

```
.claude/
├── skills/                           # NEW: Skills layer for discovery and composition
│   ├── authentication-security/
│   │   ├── SKILL.md                 # Entry point (progressive disclosure)
│   │   ├── rules.json               # Symlink to agent JSON
│   │   ├── examples/                # Code examples (optional)
│   │   └── detection-patterns.md    # Semgrep/CodeQL patterns (optional)
│   └── secrets-management/
│       └── SKILL.md
│
└── agents/                           # KEEP: Agents layer for Task execution
    ├── authentication-specialist.md  # Keep for backward compatibility
    ├── secrets-specialist.md
    └── json/                         # Compiled rule sets (unchanged)
        ├── authentication-specialist.json
        └── secrets-specialist.json
```

### Layer Responsibilities

**Skills Layer (`.claude/skills/`)**
- **Primary Purpose**: Human-readable documentation and progressive context loading
- **Used For**: Understanding capabilities, composing multi-skill workflows
- **Structure**: `SKILL.md` + supplementary files
- **Invocation**: Via natural language skill activation

**Agents Layer (`.claude/agents/`)**
- **Primary Purpose**: Task execution via Claude Code Task system
- **Used For**: Parallel execution, automated validation hooks
- **Structure**: Frontmatter + instructions + JSON rules
- **Invocation**: Via `Task` tool with `subagent_type` parameter

## Migration Process

### Step 1: Create Skills Directory Structure

```bash
mkdir -p .claude/skills/{skill-name}
```

### Step 2: Convert Agent to SKILL.md

**From:** `.claude/agents/authentication-specialist.md`

```markdown
---
name: authentication-specialist
description: Authentication security specialist covering login, MFA, password policies
tools: Read, Grep, Bash
---

You are an authentication security specialist with access to 45 rules...
```

**To:** `.claude/skills/authentication-security/SKILL.md`

```markdown
---
name: authentication-security
description: Authentication security expertise covering login, MFA, password policies based on 45+ rules
version: 1.0.0
domains:
  - user-authentication
  - multi-factor-authentication
  - password-security
tools:
  - Read
  - Grep
  - Bash
---

# Authentication Security Skill

You are equipped with authentication security expertise...

## Skill Capabilities
[Progressive disclosure: overview first, details on demand]

## Usage Patterns
[When and how to activate this skill]

## Examples
[Concrete examples with code]

## Integration with Other Skills
[How this skill composes with others]
```

### Step 3: Link to Existing Rule Sets

```bash
cd .claude/skills/authentication-security
ln -s ../../agents/json/authentication-specialist.json rules.json
```

### Step 4: Add Optional Enhancements

Skills can include supplementary resources that agents don't have:

**Code Examples:**
```bash
mkdir examples
cat > examples/secure-login.py <<EOF
# Example: Secure login implementation
import bcrypt
from flask import request, session

def login():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash):
        session['user_id'] = user.id
        return redirect('/dashboard')
    return "Invalid credentials", 401
EOF
```

**Detection Patterns:**
```bash
cat > detection-patterns.md <<EOF
# Authentication Security Detection Patterns

## Semgrep Rules
- \`weak-password-hashing\`: Detects MD5/SHA1 for passwords
- \`missing-mfa-check\`: Identifies authentication without MFA
- \`timing-attack-vulnerable\`: Finds string comparison vulnerabilities

## CodeQL Queries
- \`InsecureAuthentication.ql\`: Authentication bypass patterns
- \`WeakPasswordStorage.ql\`: Weak hashing algorithms
EOF
```

### Step 5: Keep Agent for Parallel Execution

**DO NOT DELETE** `.claude/agents/authentication-specialist.md`

This agent file enables parallel execution:

```javascript
// Parallel execution still works via Task tool
use the authentication-specialist agent to analyze login system
use the secrets-specialist agent to analyze credential storage
use the session-management-specialist agent to analyze session handling
```

## Usage Patterns

### Pattern 1: Single Skill Activation (Natural Language)

```
User: "Review the authentication system using authentication-security skill"

Claude: I'll activate the authentication-security skill to analyze your authentication system.
[Loads SKILL.md context progressively]
```

### Pattern 2: Parallel Agent Execution (Task Tool)

```javascript
// Still works with existing agents!
use the authentication-specialist agent to validate login implementation
use the session-management-specialist agent to validate session security
use the secrets-specialist agent to validate credential storage
```

### Pattern 3: Multi-Skill Composition (New Capability)

```
User: "Perform comprehensive authentication review using authentication-security, session-management, and secrets-management skills"

Claude: I'll compose these three skills for a comprehensive analysis:
1. Authentication-security skill → Login mechanism review
2. Session-management skill → Post-auth session handling
3. Secrets-management skill → Credential storage security
```

## Migration Checklist

For each agent to convert:

- [ ] Create skill directory: `.claude/skills/{skill-name}/`
- [ ] Convert agent to `SKILL.md` with progressive disclosure
- [ ] Add enhanced frontmatter (version, domains)
- [ ] Symlink to existing JSON: `ln -s ../../agents/json/{agent}.json rules.json`
- [ ] Add usage patterns section
- [ ] Add integration section (how skill composes with others)
- [ ] Add concrete examples
- [ ] Keep original agent file in `.claude/agents/` for parallel execution
- [ ] Update `.claude/README.md` with skill references
- [ ] Test skill activation via natural language
- [ ] Test agent execution via Task tool

## Agent → Skill Mapping

| Agent File | Skill Name | Status |
|------------|------------|--------|
| `authentication-specialist.md` | `authentication-security` | ✅ Example created |
| `authorization-specialist.md` | `authorization-security` | ⏳ Pending |
| `secrets-specialist.md` | `secrets-management` | ⏳ Pending |
| `session-management-specialist.md` | `session-security` | ⏳ Pending |
| `input-validation-specialist.md` | `input-validation` | ⏳ Pending |
| `jwt-specialist.md` | `jwt-security` | ⏳ Pending |
| `logging-specialist.md` | `logging-security` | ⏳ Pending |
| `configuration-specialist.md` | `secure-configuration` | ⏳ Pending |
| `data-protection-specialist.md` | `data-protection` | ⏳ Pending |
| `web-security-specialist.md` | `web-security` | ⏳ Pending |
| `semantic-search.md` | `security-research` | ⏳ Pending |
| `comprehensive-security-agent.md` | `comprehensive-security` | ⏳ Pending |

## Benefits of Hybrid Architecture

### 1. Progressive Disclosure
Skills load context incrementally, reducing token usage:

**Before (Agent):**
```
[Load all 45 rules + instructions + examples at once]
→ ~15k tokens upfront
```

**After (Skill):**
```
[Load SKILL.md overview: ~2k tokens]
→ If deeper analysis needed, load rules.json
→ If examples needed, load examples/
→ If detection patterns needed, load detection-patterns.md
```

### 2. Composability
Skills can reference and build on each other:

```markdown
## Integration with Other Skills

This skill works with:
- **session-security** → Post-authentication session handling
- **secrets-management** → Credential storage
- **logging-security** → Authentication event logging
```

### 3. Parallel Execution Preserved
Task system continues to work for parallel agent invocation:

```javascript
// Run 3 agents in parallel (each in separate Task call in single message)
use authentication-specialist to analyze auth/login.py
use session-management-specialist to analyze auth/session.py
use secrets-specialist to analyze auth/credentials.py
```

### 4. Backward Compatibility
Existing workflows continue to work unchanged:

```bash
# Old workflow still works
Task: authentication-specialist
Prompt: "Validate login implementation in src/auth/login.py"

# New skill-based workflow also works
Task: Activate authentication-security skill and validate login.py
```

## Best Practices

### When to Use Skills vs Agents

**Use Skills When:**
- User wants to understand capabilities ("What can you do for authentication security?")
- Composing multiple security domains ("Use authentication, session, and secrets skills")
- Need progressive context loading to save tokens
- Want to reference code examples and documentation

**Use Agents When:**
- Parallel execution required (multiple domains simultaneously)
- Automated validation hooks (pre-commit, CI/CD)
- Programmatic invocation via Task tool
- Existing workflows and automation

### Skill Design Principles

1. **Progressive Disclosure**: Start with overview, provide details on demand
2. **Concrete Examples**: Include real code snippets, not just descriptions
3. **Clear Scope**: Define exactly when to activate this skill
4. **Integration Points**: Show how skill composes with others
5. **Actionable Guidance**: Every rule violation includes remediation steps

### Naming Conventions

**Agents (Task System):**
- Format: `{domain}-specialist` (e.g., `authentication-specialist`)
- Purpose: Programmatic invocation via Task tool
- Kept for backward compatibility

**Skills (Progressive Loading):**
- Format: `{domain}-security` (e.g., `authentication-security`)
- Purpose: Human-readable skill activation
- New format for improved UX

## Migration Script

Automate conversion for all agents:

```bash
#!/bin/bash
# migrate-agents-to-skills.sh

AGENTS_DIR=".claude/agents"
SKILLS_DIR=".claude/skills"

for agent_file in "$AGENTS_DIR"/*.md; do
    # Skip non-specialist agents
    [[ ! $agent_file =~ -specialist\.md$ ]] && continue

    # Extract agent name
    agent_name=$(basename "$agent_file" .md)
    skill_name=$(echo "$agent_name" | sed 's/-specialist$//' | sed 's/^//' | sed 's/$/-security/')

    echo "Converting $agent_name → $skill_name"

    # Create skill directory
    mkdir -p "$SKILLS_DIR/$skill_name"

    # Create SKILL.md (template - needs manual completion)
    cat > "$SKILLS_DIR/$skill_name/SKILL.md" <<EOF
---
name: $skill_name
description: [Copy from agent frontmatter]
version: 1.0.0
domains: []
tools:
  - Read
  - Grep
  - Bash
---

# ${skill_name^} Skill

[TODO: Convert agent content to skill format with progressive disclosure]

## Skill Capabilities

## Usage Patterns

## Examples

## Integration with Other Skills
EOF

    # Symlink to JSON rules
    if [ -f "$AGENTS_DIR/json/$agent_name.json" ]; then
        ln -sf "../../agents/json/$agent_name.json" "$SKILLS_DIR/$skill_name/rules.json"
    fi

    echo "✅ Created $SKILLS_DIR/$skill_name/SKILL.md"
done

echo "Migration templates created. Manual completion required for each SKILL.md"
```

## Testing Migration

After migration, verify both skills and agents work:

```bash
# Test 1: Skill activation (natural language)
echo "Activate authentication-security skill and review src/auth/login.py"

# Test 2: Agent execution (Task tool)
echo "Use authentication-specialist agent to validate src/auth/login.py"

# Test 3: Parallel agents (multiple Task calls)
echo "Use authentication-specialist, session-management-specialist, and secrets-specialist in parallel to analyze src/auth/"

# Test 4: Multi-skill composition
echo "Compose authentication-security, session-security, and secrets-management skills for comprehensive auth review"
```

## Rollback Plan

If migration causes issues:

1. **Skills are additive** - Original agents remain unchanged
2. **Delete `.claude/skills/`** - Revert to agents-only architecture
3. **No data loss** - JSON rule sets untouched, symlinks only
4. **Backward compatible** - Task system continues to work with agents

## Next Steps

1. ✅ Review example conversion (authentication-security)
2. Create 2-3 more skill conversions to validate approach
3. Refine SKILL.md template based on learnings
4. Run migration script for remaining agents
5. Update `.claude/README.md` with skills documentation
6. Test parallel execution with skills + agents
7. Document skill composition patterns
8. Create validation tests for skill activation

---

**Questions or Issues?**
- Review example: `.claude/skills/authentication-security/SKILL.md`
- Check hybrid architecture diagram above
- Test with single skill before migrating all agents
