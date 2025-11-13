# GenAI Security Agents - Policy-as-Code Engine

A comprehensive Policy-as-Code system that **creates** knowledge packs from standards and **delivers** it through Claude Code CLI integration for **pre-code guidance** or **post-code checking**.

> **🎯 TL;DR**: Just copy the `.claude/` folder to your project. The agents and skills are **ready to use** - no installation required!
> **🛠️ Installation** is only needed if you want to **build** new agents/skills from your own documentation.

---

## 📋 Executive Summary

**Purpose**: Turn *any* complex documentation (internal standards, regulator rules, framework docs) into something engineers can actually use in design, coding, and review.

### Two Ways to Use This

1. **🎯 Use Pre-Built Security Knowledge** (Most Users)
   - Copy `.claude/` folder to your project
   - Get 11 skills + 21 agents + 195 ASVS/OWASP rules immediately
   - No installation, no compilation, no dependencies

2. **🛠️ Build Your Own Knowledge Packs** (Advanced)
   - Process YOUR documentation (internal policies, standards, frameworks)
   - Generate custom agents and skills for your organization
   - Requires Python, Poetry, and build tools

### Core Idea

- Take large documents that should be applied during product development
- Break them into small, testable **"rule cards"**
- Compile those rules into reusable **knowledge packs**
- Expose them via **agents** and **interactive skills**, orchestrated by **CLAUDE.md**
- **Result**: **The information is served on demand at the time it is needed**

### Layered Architecture

1. **Source Documents** (`research/`) - OWASP CheatSheets, ASVS standards, internal policies
2. **Atomic Rule Cards** (`app/rule_cards/`) - 195 precise, testable requirements
3. **Compiled Rule Sets** (`.claude/agents/json/`) - Machine-friendly JSON bundles
4. **Agents & Skills** (`.claude/`) - Deep specialists (agents) + Interactive helpers (skills)

### How People & Systems Use It

- **Implicit**: Auto-trigger agents when prompts match known risk areas
- **Explicit**: Named skills (`/authentication-security`) for predictable guidance
- **Search**: Semantic search over 119 OWASP/ASVS documents

### Business Outcomes

- **Reusable Knowledge**: Operationalize external standards and internal policies
- **Lower Risk**: Decisions grounded in documented rules, not ad-hoc answers
- **Developer Velocity**: Contextual guidance instead of long PDFs
- **Compliance & Auditability**: Every recommendation traceable to source documents

---

## 🔑 How LLMs Access Security Knowledge

This repository implements **five complementary access patterns**:

| Pattern | Activation | Token Cost | Use Case |
|---------|-----------|------------|----------|
| **Skills** | Deterministic (slash) or probabilistic | 2k-12k | User-facing guidance, progressive disclosure |
| **Agents** | Explicit (Task tool) | 15k+ | Parallel analysis, deep validation |
| **Semantic Search** | Explicit (tool) | Variable | Standards research, best practices lookup |
| **Grep** | Explicit (tool) | Minimal | Direct pattern search in rules/corpus |
| **CLAUDE.md** | Automatic (patterns) | <1K | Workflow orchestration, security enforcement |

**Agent Invocation Strategy**: Claude can invoke `comprehensive-security-agent` (loads all 195 rules across 20 domains) for broad cross-domain analysis, or invoke specific specialist agents (e.g., `authentication-specialist`, `secrets-specialist`) for focused domain expertise.

📖 **Learn more**:
- [ARCHITECTURE.md](.claude/skills/ARCHITECTURE.md) - Complete system architecture
- [SKILLS_VS_AGENTS.md](.claude/skills/SKILLS_VS_AGENTS.md) - When to use skills vs agents

---

## 🚀 Quick Start: Use Pre-Built Agents & Skills

**The `.claude/` folder is ready to use immediately** - no installation required!

### Option 1: Use Pre-Built Security Knowledge (Recommended)

**Just copy the `.claude/` folder to your project:**

```bash
# Copy everything (11 skills + 21 agents + orchestration)
cp -r .claude/ /path/to/your/project/.claude/

```

**That's it!** Claude Code will automatically:
- Load skills via `/authentication-security` slash commands
- Route security tasks to specialist agents
- Apply 195 security rules from OWASP/ASVS standards

**What you get:**
- ✅ **11 Security Skills**: Interactive guidance with progressive disclosure
- ✅ **21 Security Agents**: Deep specialists for automated analysis
- ✅ **195 Security Rules**: ASVS/OWASP/CWE-aligned requirements
- ✅ **119 Documents**: Searchable OWASP CheatSheets + ASVS standards (via `research/`)

**Optional: Enable Semantic Search**

To use the `/semsearch` command for searching security standards:

```bash
# Install Rust and semtools (one-time setup)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
cargo install semtools

# Verify installation
search --version
```

Then use semantic search:
```bash
/semsearch "JWT token validation"
/semsearch "SQL injection prevention"
/semsearch "session timeout controls" --corpus research/search_corpus/asvs
```

**Note**: Semantic search is optional. Skills and agents work without it.

### Option 2: Build Your Own Knowledge Packs

**Installation only needed if you want to create NEW agents/skills from YOUR documentation.**

<details>
<summary><b>Click to expand: Building from Source</b></summary>

#### Prerequisites

- **Python 3.8+**
- **Poetry** (dependency management)
- **Rust** (for semantic search - optional)

#### 1. Clone Repository

```bash
git clone https://github.com/your-org/genai-sec-agents.git
cd genai-sec-agents
```

#### 2. Install Dependencies

```bash
# Install Poetry if not present
curl -sSL https://install.python-poetry.org | python3 -

# Install Python dependencies
poetry install
```

#### 3. Compile Security Agents

```bash
# Transform your YAML rule cards → JSON specialist agents
poetry run python app/tools/compile_agents.py --verbose

# Or use makefile
make compile
```

**Output:** Updated `.claude/` folder with your custom agents and skills!

**Note**: For semantic search installation, see "Optional: Enable Semantic Search" in Option 1 above.

</details>

---

## 🎯 Quick Usage

### Use Skills (Interactive Guidance)

```bash
# Deterministic activation via slash commands
/authentication-security  # Load authentication skill
/session-management       # Load session security skill
/secrets-management       # Load secrets handling skill
```

### Search Security Knowledge

```bash
# Via slash command (requires semtools - see "Optional: Enable Semantic Search" above)
/semsearch "JWT token validation"

# Via makefile (requires semtools)
make semsearch q="JWT token validation best practices"
make semsearch-asvs q="password complexity requirements"

# Direct grep for exact matches (no installation required)
grep -r "bcrypt" app/rule_cards/
grep -r "AUTH-PASSWORD" .claude/agents/json/
```

### Agents Work Automatically

**No manual invocation needed** - Claude Code automatically routes security tasks to agents:

```
User: "Review this login function for security issues"
→ Claude routes to authentication-specialist agent
→ Agent applies 49 authentication rules
→ Returns findings with ASVS/CWE citations
```

---

## 📚 Documentation

### 🎯 Getting Started
- **[USAGE.md](USAGE.md)** - Complete usage guide with examples and workflows
- **[Worked Example](docs/WORKED_EXAMPLE.md)** - Hands-on demonstration of security analysis

### 🏗️ Architecture & Design
- **[ARCHITECTURE.md](.claude/skills/ARCHITECTURE.md)** - Complete system architecture (six layers, five access patterns)
- **[SYSTEM_OVERVIEW.md](.claude/skills/SYSTEM_OVERVIEW.md)** - Technical details with diagrams
- **[SKILLS_VS_AGENTS.md](.claude/skills/SKILLS_VS_AGENTS.md)** - When to use skills vs agents

### 🔐 Security & Validation
- **[SECURITY_GUIDE.md](docs/SECURITY_GUIDE.md)** - Security practices and controls
- **[Validation Summary](.claude/skills/validation/VALIDATION_SUMMARY.md)** - Phase 0 and Phase 1 validation results
- **[Threat Model](docs/BMadSecurityAgentInitialThreatModel.md)** - STRIDE methodology analysis

### 👥 User Guides
- **[User Guide](docs/USER_GUIDE.md)** - Comprehensive usage guide
- **[Personas & Scenarios](docs/BMadSecurityAgent_Personas_Scenarios.md)** - Role-based benefits

### 📊 Project Management
- **[Project Overview](docs/BMadSecurityAgentProjectOverview.md)** - Strategic vision and scope
- **[Product Requirements](docs/PRD.md)** - Epic breakdowns and user stories
- **[Stories](docs/stories/)** - User story definitions and status

---

## 👥 Who This Is For

- **🧑‍💻 Developers**: Immediate security feedback while coding
- **🛡️ AppSec Engineers**: Codify security lessons into automated guardrails
- **⚙️ SREs**: Enforce consistent security policies in CI/CD
- **📊 CISOs**: Demonstrate compliance with auditable trails
- **📋 Product Managers**: Prevent last-minute vulnerabilities from derailing releases

📖 **Details**: See [Personas & Scenarios](docs/BMadSecurityAgent_Personas_Scenarios.md)

---

## 🎯 What This System Does

- **📝 Rule Card Creation**: Convert security standards into structured YAML rule cards
- **🤖 Agent Compilation**: Generate specialized JSON security agents for Claude Code
- **🎓 Skills Development**: Create 11 security domain skills with progressive disclosure
- **🔍 Semantic Search**: Query 119+ security documents (OWASP CheatSheets + ASVS standards)
- **⚡ Real-Time Analysis**: Provide immediate security guidance during coding
- **🛡️ Standards Compliance**: Automatic CWE/OWASP/ASVS reference validation

---

## 📦 Repository Structure

```
genai-sec-agents/
├── app/
│   ├── rule_cards/              # 195 YAML Rule Cards across 20 domains
│   ├── tools/                   # Compilation and validation toolchain
│   ├── claude_code/             # Claude Code integration
│   └── semantic/                # Semantic search integration
├── .claude/
│   ├── agents/                  # 21 specialized security agents
│   └── skills/                  # 11 interactive security skills
├── research/search_corpus/      # 119 OWASP/ASVS documents (processed)
├── docs/                        # Comprehensive documentation
└── tests/                       # 150+ comprehensive tests
```

---

## 🛠️ Key Features

### Claude Code Integration
- **Sub-2-Second Response**: Performance-optimized with multi-level caching
- **Framework Detection**: Automatic detection of Flask, Django, JWT, Docker, SQLAlchemy
- **Security Scoring**: Letter-grade security assessment with issue breakdown
- **Secure Code Snippets**: Context-aware secure implementation examples
- **Manual Analysis**: On-demand security scans for files and workspaces

### Security Knowledge Base
- **195 Security Rules** across 20 domains (authentication, session, logging, etc.)
- **119 Documents**: 102 OWASP CheatSheets + 17 ASVS standards
- **11 Skills**: Interactive security guidance with progressive disclosure
- **21 Agents**: Deep specialists for automated analysis

### Semantic Search
- **Fast**: Sub-second search via Rust-based semtools
- **Local-Only**: No external API calls, complete offline capability
- **Comprehensive**: Search across OWASP CheatSheets and ASVS standards
- **Secure**: Input validation, audit logging, resource limits

---

## 🧪 Testing

```bash
# Run complete test suite (150+ tests)
poetry run pytest tests/ -v

# Test specific components
poetry run pytest tests/claude_code/ -v           # Claude Code integration
poetry run pytest tests/semantic/ -v              # Semantic search
poetry run pytest tests/runtime/ -v               # Runtime engine
```

---

## 🤝 Contributing

1. **Create Rule Cards**: Follow schema in existing examples
2. **Validate Syntax**: `make validate`
3. **Test Integration**: `make test`
4. **Build Packages**: `make build`
5. **Submit Pull Request**: Include validation results

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📋 Standards Compliance

**195 Rule Cards** implement security controls based on:
- **CWE**: Common Weakness Enumeration (69 unique references)
- **ASVS**: Application Security Verification Standard (146 unique references)
- **OWASP**: Top 10 and security guidelines (25 unique references)
- **NIST**: Cybersecurity Framework and Privacy Framework
- **RFC**: Internet standards (JWT, cookies, etc.)

---

## 📄 License

This project is licensed under the **Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)**.

See [LICENSE.md](LICENSE.md) for full details.

---

## 🔗 References

1. [Claude Code Best Practices](https://www.reddit.com/r/ClaudeAI/comments/1oivjvm/claude_code_is_a_beast_tips_from_6_months_of/)
2. [Claude Skills Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)
3. [Claude Code Internals Analysis](https://agiflow.io/blog/claude-code-internals-reverse-engineering-prompt-augmentation/)
4. [Test-Driven Development Skill](https://github.com/obra/superpowers/blob/main/skills/test-driven-development/SKILL.md)
5. [Agent Skills for the Real World](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
6. [Skills Automation Framework](https://github.com/Toowiredd/claude-skills-automation)
7. [Technical Deep Dive](https://medium.com/data-science-collective/claude-skills-a-technical-deep-dive-into-context-injection-architecture-ee6bf30cf514)
8. [Skills Testing with Subagents](https://github.com/obra/superpowers/blob/main/skills/testing-skills-with-subagents/examples/CLAUDE_MD_TESTING.md)

---

**For complete documentation**: See [docs/README.md](docs/README.md) for documentation index
