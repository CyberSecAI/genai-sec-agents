# Usage Guide

Complete usage documentation for the GenAI Security Agents system.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Claude Code Integration](#claude-code-integration)
3. [Semantic Search](#semantic-search)
4. [Manual Security Analysis](#manual-security-analysis)
5. [Development Workflows](#development-workflows)
6. [Advanced Usage](#advanced-usage)

---

## Quick Start

### Phase 1: Create Security Knowledge (One-Time Setup)

#### 1. Ingest Security Standards (Optional - Rule Cards already created)
```bash
# Fetch latest OWASP CheatSheets and generate rule cards
python3 app/ingestion/complete_owasp_migration.py

# Fetch ASVS standards and generate rule cards
python3 app/ingestion/complete_asvs_integration.py
```

#### 2. Compile Rule Cards into JSON Agents
```bash
# Transform 195+ YAML rule cards → 21 JSON specialist agents
python3 app/tools/compile_agents.py --verbose

# Or use makefile
make compile
```

#### 3. Build Semantic Search Corpus
```bash
# Create OWASP & ASVS search corpus for semantic queries
make semsearch-build
```

### Phase 2: Use Security Knowledge (Claude Code CLI)

#### 4. Security Analysis via Claude Code
```bash
# Route to specialist agents (NO Python runtime needed)
claude-code → Task(subagent_type="authentication-specialist")
claude-code → Task(subagent_type="web-security-specialist")
claude-code → Task(subagent_type="secrets-specialist")

# Semantic search for security knowledge
claude-code → Task(subagent_type="semantic-search", prompt="JWT security best practices")
```

#### 5. Direct Tool Usage (Advanced)
```bash
# Use security tools directly (integrated with agents)
semgrep --config=auto  # Uses rules from agent validation hooks
tools/semsearch.sh "input validation OWASP"  # Direct semantic search
```

---

## Claude Code Integration

### Skills (Interactive Guidance)

**Deterministic activation** via slash commands:
```bash
/authentication-security  # Load authentication skill
/session-management       # Load session security skill
/secrets-management       # Load secrets handling skill
```

**Progressive disclosure** - loads only what you need:
- Simple queries: 2k tokens (overview)
- Complex queries: 5k tokens (examples + guidance)
- Deep analysis: 10k tokens (full rules)

### Agents (Deep Analysis)

**Automatic invocation** by Claude based on context:
- Implementation tasks → Multiple specialist agents in parallel
- Review tasks → Appropriate domain specialist
- Complex tasks → `comprehensive-security-agent` (all 195 rules)

**Manual invocation** via CLAUDE.md patterns or explicit requests.

---

## Semantic Search

### OWASP CheatSheets Search
```bash
# JWT Security
make semsearch q="JWT token validation best practices"

# Input Validation
make semsearch q="SQL injection prevention techniques"

# Authentication
make semsearch q="multi-factor authentication implementation"

# Container Security
make semsearch q="Docker container hardening"

# Cross-Site Scripting
make semsearch q="XSS prevention output encoding"
```

### ASVS Standards Search
```bash
# Authentication Requirements
make semsearch-asvs q="password complexity requirements"

# Session Management
make semsearch-asvs q="session timeout controls"

# Access Control
make semsearch-asvs q="authorization bypass prevention"

# Cryptography
make semsearch-asvs q="encryption algorithm recommendations"

# Input Validation
make semsearch-asvs q="input sanitization requirements"
```

### Advanced Search Patterns
```bash
# Domain-specific searches
make semsearch q="API security headers" | head -20        # Focused results
make semsearch-asvs q="mobile application security"       # ASVS corpus search

# Direct semtools usage (the 'search' command installed via cargo install semtools)
search "authentication bypass" research/search_corpus/owasp/*.md --top-k 3 --max-distance 0.7

# Advanced semtools options
search "CSRF protection" research/search_corpus/owasp/*.md --top-k 5 --n-lines 3
search "access control" research/search_corpus/asvs/*.md --max-distance 0.5 --n-lines 2
```

### Semtools CLI Reference
```
Usage: search [OPTIONS] <QUERY> [FILES]...

Arguments:
  <QUERY>     Query to search for (positional argument)
  [FILES]...  Files or directories to search

Options:
  -n, --n-lines <N_LINES>            How many lines before/after to return as context [default: 3]
      --top-k <TOP_K>                The top-k files or texts to return [default: 3]
  -m, --max-distance <MAX_DISTANCE>  Return all results with distance below threshold (0.0+)
  -i, --ignore-case                  Perform case-insensitive search
  -h, --help                         Print help
  -V, --version                      Print version
```

---

## Manual Security Analysis

### Command Interface

```bash
# Analyze a single file for security issues
python3 app/claude_code/manual_commands.py file --path /path/to/your/file.py

# Comprehensive analysis of a single file
python3 app/claude_code/manual_commands.py file --path /path/to/your/file.py --depth comprehensive

# Analyze entire workspace for security issues
python3 app/claude_code/manual_commands.py workspace

# Analyze specific directory with comprehensive depth
python3 app/claude_code/manual_commands.py workspace --path src/ --depth comprehensive

# JSON output for programmatic integration
python3 app/claude_code/manual_commands.py file --path file.py --format json
```

### Semantic Search Enhancement

```bash
# Enable semantic search for enhanced analysis (requires feature flag)
python3 app/claude_code/manual_commands.py file --path file.py --semantic

# Semantic search with custom filters
python3 app/claude_code/manual_commands.py workspace --semantic --semantic-filters '{"languages": ["python"], "severity_levels": ["high", "critical"]}'

# Explain mode for detailed security guidance
python3 app/claude_code/manual_commands.py explain --rule-id "SECRET-001" --code-context "api_key = 'hardcoded-secret'"
```

### Example Output

```
🔒 Security Analysis Results
📁 Files Analyzed: 15
🔍 Total Issues: 8
📊 Severity Breakdown:
  🚨 Critical: 2
  ⚠️ High: 1
  📋 Medium: 3
  💡 Low: 2
🎯 CI/CD Prediction: FAIL (3 blocking issues)
⏱️ Analysis Time: 4.32s

🚨 **Blocking Issues for CI/CD:**
- HARDCODED-JWT-SECRET-001: Remove hardcoded JWT secrets (Critical)
- SSRF-VULNERABILITY-002: Validate URLs in proxy endpoint (High)
- INSECURE-COOKIE-CONFIG: Add HttpOnly flag to session cookies (High)

💡 **Remediation Priority:**
1. ✅ Store JWT secrets in environment variables
2. ✅ Implement URL whitelist for proxy requests
3. ✅ Configure secure cookie attributes
```

---

## Development Workflows

### Example 1: JWT Implementation Assistance

**Scenario:** Developer implementing JWT authentication

```bash
# Developer starts coding JWT handler
$ claude-code start jwt_auth.js

# Claude Code detects JWT context and automatically:
# 1. Searches corpus: make semsearch q="JWT security implementation"
# 2. Loads relevant rule cards: JWT-SIG-001, JWT-ALG-001, JWT-KEY-001
# 3. Provides proactive guidance

# Developer writes problematic code:
const jwt = require('jsonwebtoken');
const token = jwt.sign({userId: 123}, 'hardcoded-secret', {algorithm: 'none'});

# Claude Code immediately flags:
# - Rule violation: JWT-KEY-001 (hardcoded secret)
# - Security issue: JWT-ALG-001 (insecure algorithm 'none')
# - References: JWT_Cheat_Sheet.md sections on key management and algorithms
```

**Interactive Correction:**
```bash
$ claude-code fix jwt_auth.js --security

# Claude Code searches corpus and suggests:
Based on OWASP JWT Cheat Sheet, here's the secure implementation:

const jwt = require('jsonwebtoken');
const secret = process.env.JWT_SECRET; // From environment
const token = jwt.sign(
    {userId: 123},
    secret,
    {
        algorithm: 'RS256',  // Asymmetric algorithm
        expiresIn: '15m',    // Short expiration
        issuer: 'your-app',
        audience: 'your-users'
    }
);

# References:
# - OWASP JWT Cheat Sheet: Algorithm security
# - ASVS V3.1.1: Cryptographic verification
# - Rule Card JWT-ALG-001: Algorithm validation
```

### Example 2: Database Security Review with Agent Integration

**Scenario:** Code review for database operations using security agents

```python
# Code under review
def get_user_data(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)
```

```bash
# Reviewer uses Claude Code with input-validation-specialist agent
$ claude-code security --agent input-validation-specialist database_operations.py

# Agent-powered security report:
🚨 SQL Injection Vulnerability Detected (Agent: input-validation-specialist)

Issue: String formatting in SQL query construction
File: database_operations.py:2
Rule: SQL-INJECT-001 (SQL Injection Prevention)
Reference: OWASP SQL Injection Prevention Cheat Sheet

Detected by Agent Tools:
✓ Semgrep rule: owasp.python.lang.security.audit.sqli.python-sqli-string-concat
✓ TruffleHog scan: No hardcoded credentials found
✓ CodeQL analysis: Available for CI integration

Recommendation:
def get_user_data(user_id):
    query = "SELECT * FROM users WHERE id = %s"
    return db.execute(query, (user_id,))  # Parameterized query

ASVS Compliance: V5.3.4 - SQL injection prevention
CWE Reference: CWE-89 - Improper Neutralization of Special Elements
```

### Example 3: Container Security Analysis

**Scenario:** Dockerfile security hardening using container security agent

```dockerfile
# Dockerfile under analysis
FROM ubuntu:latest
RUN apt-get update && apt-get install -y python3
COPY . /app
USER root
CMD ["python3", "/app/main.py"]
```

```bash
# Security analysis with secure-coding-specialist agent
$ claude-code security --agent secure-coding-specialist Dockerfile

# Agent-powered security analysis:
🔒 Container Security Improvements (Agent: secure-coding-specialist)

Issues Found:
1. Root user execution (HIGH) - Rule: DOCKER-USER-001
2. Latest tag usage (MEDIUM) - Rule: DOCKER-IMAGE-001
3. Missing security updates (MEDIUM) - Best practice violation

Agent Tool Integration:
✓ Hadolint: Available for static Dockerfile analysis
✓ Docker Scout: Available for vulnerability scanning
✓ Semgrep: Container security rules applied

Recommended Dockerfile:
FROM ubuntu:22.04  # Specific version
RUN apt-get update && apt-get install -y python3 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
COPY . /app
RUN adduser --disabled-password appuser  # Non-root user
USER appuser
CMD ["python3", "/app/main.py"]

References:
- OWASP Docker Security Cheat Sheet: User privileges
- ASVS V14.2.1: Container isolation
- CWE-250: Execution with unnecessary privileges
```

---

## Advanced Usage

### Compiler Options

```bash
# Custom manifest and output directory
python3 app/tools/compile_agents.py --manifest custom_manifest.yml --output dist/custom/

# Force overwrite existing packages
python3 app/tools/compile_agents.py --force

# Verbose logging for debugging
python3 app/tools/compile_agents.py --verbose
```

### Creating New Rule Cards

1. **Choose Security Domain**: Add to existing directory or create new domain
2. **Follow Schema**: Use existing Rule Cards as templates
3. **Include Required Fields**: `id`, `title`, `severity`, `scope`, `requirement`, `do`, `dont`, `detect`, `verify`, `refs`
4. **Add Scanner Integration**: Include Semgrep, TruffleHog, CodeQL, or custom detection rules
5. **Validate**: `python3 app/tools/validate_cards.py app/rule_cards/your-card.yml`

### Example Rule Card Structure

```yaml
id: DOMAIN-TOPIC-001
title: "Security requirement description"
severity: critical|high|medium|low
scope: application-type
requirement: "Detailed security requirement"
do:
  - "Positive security practice"
dont:
  - "Anti-pattern to avoid"
detect:
  semgrep:
    - "scanner-rule-id"
  trufflehog:
    - "Secret Type"
verify:
  tests:
    - "Verification test description"
refs:
  cwe:
    - "CWE-XXX"
  asvs:
    - "V.X.X"
  owasp:
    - "AXX:YYYY"
```

### CI/CD Pipeline Integration

```bash
# Validation step
make validate || exit 1

# Compilation step
make compile

# Testing step
make test || exit 1

# Build semantic search corpus (optional)
make semsearch-build
```

### Makefile Targets

#### Core Development
```bash
make validate         # Validate all Rule Cards
make compile         # Compile agent packages
make build           # Full validation and compilation
make test           # Run comprehensive test suite
```

#### Semantic Search
```bash
# Corpus Building
make semsearch-build       # Build both OWASP and ASVS corpora
make semsearch-build-owasp # Build OWASP CheatSheets corpus only
make semsearch-build-asvs  # Build ASVS standards corpus only

# Semantic Searching (via secure wrapper script)
make semsearch q="JWT token validation"           # Search OWASP corpus
make semsearch-asvs q="authentication controls"  # Search ASVS corpus
```

---

## Troubleshooting

### Semantic Search Issues

**Installation Issues:**
```bash
# Install Rust toolchain if not present
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# Install semtools with search feature
cargo install semtools --no-default-features --features=search

# Verify installation
search --version
which search  # Should show ~/.cargo/bin/search or system path
```

**Common Errors:**
```bash
# Error: "search binary not found"
# Solution: Add ~/.cargo/bin to PATH or reinstall semtools

# Error: "Corpus not found or empty"
# Solution: Build corpus first
make semsearch-build

# Error: "Query contains invalid characters"
# Solution: Use only letters, numbers, spaces, dots, hyphens, underscores
make semsearch q="valid query here"

# Error: "Search timeout after 10s"
# Solution: Simplify query or increase timeout
SEARCH_TIMEOUT=20 make semsearch q="simpler query"
```

**Performance Tuning:**
```bash
# Faster searches with stricter distance threshold
search "query" research/search_corpus/owasp/*.md --max-distance 0.3

# More context lines for better understanding
search "query" research/search_corpus/owasp/*.md --n-lines 7

# Return more/fewer results
search "query" research/search_corpus/owasp/*.md --top-k 10
```

---

## Next Steps

- **[Architecture Documentation](.claude/skills/ARCHITECTURE.md)** - Complete system architecture
- **[Security Guide](docs/SECURITY_GUIDE.md)** - Security practices and controls
- **[Worked Example](docs/WORKED_EXAMPLE.md)** - Hands-on demonstration
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute rule cards

---

**For questions or issues**: See [docs/README.md](docs/README.md) for complete documentation index
