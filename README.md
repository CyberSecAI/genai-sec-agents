# GenAI Security Agents - Policy-as-Code Engine

A comprehensive Policy-as-Code system that transforms human-readable security Rule Cards into machine-readable JSON agent packages for AI-powered security guidance systems, featuring **Claude Code integration for real-time security analysis**.

## Overview
This repository implements a complete security rule management and compilation toolchain with AI-powered runtime capabilities:

- **Rule Cards**: Human-readable YAML security policies with scanner integration
- **Compiler Toolchain**: Secure compilation system transforming YAML to JSON agent packages  
- **Specialized Agents**: 5 domain-specific security agents compiled from Rule Cards
- **AgenticRuntime**: AI-powered runtime for dynamic security guidance (Story 2.1)
- **Claude Code Sub-Agent**: Real-time security analysis within Claude Code IDE (Story 2.2) ✅
- **Manual Security Analysis**: On-demand security scans for files and workspaces (Story 2.3) ✅
- **Semtools Semantic Search**: Local semantic search for extended security knowledge (Story 2.4) ✅
- **CI/CD Integration**: Makefile automation with validation and compilation workflows

## Quick Start

### 1. Validate Existing Rule Cards
```bash
make validate
# or: python3 app/tools/validate_cards.py app/rule_cards/
```

### 2. Compile Agent Packages
```bash
make compile
# or: python3 app/tools/compile_agents.py --verbose
```

### 3. Complete Build Workflow
```bash
make build  # Validates Rule Cards then compiles agent packages
```

### 4. Run Tests
```bash
make test   # Runs comprehensive test suite with security validation
```

### 5. Claude Code Sub-Agent (Real-Time Security Analysis)
```bash
# Initialize Claude Code security runtime
python3 app/claude_code/initialize_security_runtime.py

# Analyze code for security issues 
python3 app/claude_code/analyze_context.py /path/to/your/code.py --format=guidance

# JSON output for programmatic use
python3 app/claude_code/analyze_context.py /path/to/your/code.py --format=json
```

### 6. Manual Security Analysis Commands (Story 2.3)
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

### 7. Semantic Search Enhancement (Story 2.4) ✅
```bash
# Enable semantic search for enhanced analysis (requires feature flag)
python3 app/claude_code/manual_commands.py file --path file.py --semantic

# Semantic search with custom filters
python3 app/claude_code/manual_commands.py workspace --semantic --semantic-filters '{"languages": ["python"], "severity_levels": ["high", "critical"]}'

# Explain mode for detailed security guidance
python3 app/claude_code/manual_commands.py explain --rule-id "SECRET-001" --code-context "api_key = 'hardcoded-secret'"

# Generate and validate semantic search corpus
python3 -c "from app.semantic import CorpusManager; cm = CorpusManager(); corpus = cm.render_corpus_from_packages([]); print('Corpus generated:', len(corpus.content), 'bytes')"

# Check semantic search availability and statistics
python3 -c "from app.semantic import SemanticSearchInterface; si = SemanticSearchInterface(); print('Available:', si.is_available()); print('Stats:', si.get_search_statistics())"
```

## Generated Agent Packages

The compilation process generates 5 specialized security agent packages:

| Agent | Description | Rules | Domains |
|-------|-------------|-------|---------|
| **secrets-specialist** | Hardcoded secrets detection and prevention | 4 | API keys, DB credentials, JWT secrets, Cloud credentials |
| **web-security-specialist** | Web application security (cookies, JWT) | 7 | Cookie security, JWT validation, Web authentication |
| **genai-security-specialist** | GenAI security controls | 3 | Prompt injection, Data protection, Model access |
| **container-security-specialist** | Container security | 1 | Docker security, Container privileges |
| **comprehensive-security-agent** | Multi-domain security agent | 15 | All security domains combined |

## Repository Structure
```
app/
├── rule_cards/              # YAML Rule Cards organized by security domain
│   ├── secrets/            # Hardcoded secrets prevention (4 cards)
│   ├── cookies/            # Secure cookie configuration (3 cards)  
│   ├── jwt/                # JWT security validation (4 cards)
│   ├── genai/              # GenAI security controls (3 cards)
│   └── docker/             # Container security (1 card)
├── runtime/                 # AgenticRuntime core components (Story 2.1)
│   ├── core.py             # Main runtime engine for dynamic guidance
│   └── ...                 # Runtime supporting modules
├── claude_code/             # Claude Code Sub-Agent (Story 2.2) ✅
│   ├── initialize_security_runtime.py  # Performance-optimized runtime manager
│   ├── analyze_context.py  # Enhanced context analyzer with snippets
│   └── manual_commands.py  # Manual analysis with semantic search integration ✅
├── semantic/                # Semantic Search Integration (Story 2.4) ✅
│   ├── corpus_manager.py    # Rule card corpus rendering and management
│   ├── semantic_search.py   # Semtools interface with fallback search
│   ├── feature_flags.py     # Runtime retrieval feature flag management
│   ├── search_results.py    # Search result formatting and provenance
│   └── config/             # Corpus and search configuration files
├── tools/                   # Compilation and validation toolchain
│   ├── agents_manifest.yml # Agent configuration definitions
│   ├── compile_agents.py   # Main compiler script  
│   └── validate_cards.py   # Rule Card validator
└── dist/agents/            # Compiled JSON agent packages (generated)

.claude/agents/             # Claude Code Sub-Agent Configuration ✅
└── security-guidance.md    # Sub-agent definition with YAML frontmatter

docs/                       # Comprehensive project documentation
├── stories/               # User story definitions and completion tracking
├── plans/                 # Implementation plans and technical specifications
└── epics/                 # Epic definitions and requirements

tests/                      # Test suites with security validation
├── claude_code/           # Claude Code sub-agent tests (44 tests) ✅
├── semantic/              # Semantic search test suites (100+ tests) ✅
│   ├── test_corpus_manager.py           # Corpus management and security tests
│   ├── test_semantic_search.py          # Search interface and fallback tests
│   ├── test_feature_flags.py            # Feature flag and audit tests
│   ├── test_developer_tools_integration.py # Integration tests
│   ├── test_performance_reliability.py  # Performance and reliability tests
│   └── test_complete_integration.py     # End-to-end integration tests
└── runtime/               # Runtime engine test suites
```

## Claude Code Integration Features ✅

The **security-guidance** sub-agent provides real-time security analysis within Claude Code:

### Key Features
- **🚀 Sub-2-Second Response**: Performance-optimized with multi-level caching
- **🔍 Framework Detection**: Automatic detection of Flask, Django, JWT, Docker, SQLAlchemy, etc.
- **📊 Security Scoring**: Letter-grade security assessment with issue breakdown
- **💻 Secure Code Snippets**: Context-aware secure implementation examples
- **⚡ Smart Caching**: Package and analysis result caching for faster responses
- **🎯 Priority Alerts**: High/critical security issues highlighted prominently
- **🔧 Manual Analysis Commands**: On-demand security scans for files and workspaces (Story 2.3)
- **🎯 CI/CD Prediction**: Predict CI/CD pipeline outcomes before commit
- **🔍 Semantic Search**: Local semantic search for extended security knowledge access (Story 2.4) ✅

### Sub-Agent Output Example
```
🔍 **Security Analysis Results** - Score: 85/100 (B)
📁 File: /path/to/your/app.py
🤖 Agent: web-security-specialist
⚙️ Frameworks: flask, requests

🚨 **Priority Security Issues (2):**
⚠️ Insecure Cookie Configuration (COOKIES-HTTPONLY-001)
   └─ Session cookies must include HttpOnly attribute

💡 **Security Guidance:**
Configure Flask cookies with security attributes to prevent XSS attacks...

✅ **Recommended Actions (3):**
⚠️ Set HttpOnly attribute on all session cookies
⚠️ Apply Secure flag for HTTPS-only cookies  
📋 Configure SameSite attribute to prevent CSRF

💻 **Secure Code Examples (1 available):**

📝 **Secure Flask Cookie Configuration** (PYTHON/flask)
   Configure Flask cookies with security attributes
   ```python
   from flask import Flask, session
   
   app = Flask(__name__)
   app.config['SESSION_COOKIE_HTTPONLY'] = True
   app.config['SESSION_COOKIE_SECURE'] = True
   # ... (5 more lines)
   ```
   🔐 HttpOnly prevents XSS cookie theft
   🔐 Secure flag requires HTTPS

🔒 Analysis: Input sanitized, context enhanced, 5 agents loaded
```

### Manual Security Analysis Commands (Story 2.3)

The Claude Code sub-agent now supports manual on-demand security analysis:

**Available Commands:**
- `*security-scan-file [file_path] [--depth=standard|comprehensive]` - Analyze single file
- `*security-scan-workspace [--path=workspace_path] [--depth=standard|comprehensive]` - Analyze workspace

**Example Manual Analysis Output:**
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

**Security Features:**
- **🔐 Path Traversal Protection**: Prevents access outside project boundaries
- **⏱️ Resource Limits**: 30-second timeout, 1MB file size limit, 1000 file workspace limit
- **🛡️ Input Validation**: Comprehensive sanitization of all user inputs
- **📊 CI/CD Consistency**: Predictions match pipeline validation rules

### 🔍 **Semantic Search Integration (Story 2.4)**

**Hybrid Architecture**: Combines deterministic compiled rules with optional local semantic search for comprehensive coverage:

```
🔒 Security Analysis Results (Enhanced)
📁 Files Analyzed: 15
🔍 Total Issues: 8
📊 Severity Breakdown:
  🚨 Critical: 2
  ⚠️ High: 1  
  📋 Medium: 3
  💡 Low: 2
🎯 CI/CD Prediction: FAIL (3 blocking issues)
⏱️ Analysis Time: 4.32s
🔍 Semantic Search: ✅ Enhanced
   ⏱️ Semantic Processing: 245ms
   📊 Semantic Matches: 7

🎯 **High Confidence Semantic Matches:**
  • SECRET-MGMT-002 [0.89] (secrets)
    └─ Use environment variables or secure key management systems for API keys
  • AUTH-BYPASS-001 [0.83] (authentication)  
    └─ Implement proper session management and token validation

🔍 **Semantic Edge Case Detections:**
  • RACE-CONDITION-001 [0.81] (concurrency)
    └─ Potential race condition in multi-threaded authentication flow
  • TIMING-ATTACK-001 [0.76] (crypto)
    └─ String comparison vulnerable to timing attacks in password validation
```

**Semantic Search Features:**
- **🎯 Local-Only Operation**: No external API calls, complete offline capability
- **🔧 Feature Flag Control**: Runtime retrieval OFF by default (secure), can be enabled per-analysis
- **🔍 Explain Mode**: Detailed explanations for security rules with context-aware guidance  
- **📊 Edge Case Detection**: Finds vulnerabilities not covered by compiled rules
- **⚡ Performance Optimized**: <1s search requirement with intelligent caching
- **🛡️ Security-First**: Comprehensive input validation, audit logging, resource limits
- **🔄 Graceful Fallback**: Works completely offline when semtools unavailable

### 📋 **Want to See This in Action?**
Check out our **[Worked Example](docs/WORKED_EXAMPLE.md)** that demonstrates the sub-agent analyzing a vulnerable Flask application and shows:
- How Claude Code routes the security task to the sub-agent
- Which agents are loaded and why
- Expected vs actual security issue detection
- Complete validation of all acceptance criteria
- Performance measurements and caching behavior

## Advanced Usage

### Claude Code Sub-Agent
```bash
# Test sub-agent functionality
cd /path/to/your/code
python3 /path/to/genai-sec-agents/app/claude_code/analyze_context.py $(pwd)/suspicious_file.py

# Performance testing (should complete under 2 seconds)
time python3 app/claude_code/analyze_context.py your_file.py

# Cache testing (second run should be much faster)
python3 app/claude_code/analyze_context.py your_file.py  # Populates cache
python3 app/claude_code/analyze_context.py your_file.py  # Uses cache
```

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

## Security Features

The compiler toolchain implements comprehensive security controls:

- **YAML Security**: Uses `yaml.safe_load()` to prevent deserialization attacks
- **Path Validation**: Prevents directory traversal and path injection attacks  
- **Input Sanitization**: Validates all Rule Card inputs against schema requirements
- **Error Handling**: Secure error messages without information disclosure
- **Source Integrity**: SHA256 source digest and Git versioning for traceability

See [SECURITY_GUIDE.md](docs/SECURITY_GUIDE.md) for complete security practices.

## Documentation

- **[User Guide](docs/USER_GUIDE.md)** - Complete usage guide with examples and troubleshooting
- **[Worked Example](docs/WORKED_EXAMPLE.md)** - ⭐ **Comprehensive demonstration** of Claude Code sub-agent analyzing vulnerable Flask app
- **[Semantic Search Guide](docs/SEMANTIC_SEARCH_GUIDE.md)** - ⭐ **Complete semantic search integration guide** with examples and best practices ✅
- **[Security Guide](docs/SECURITY_GUIDE.md)** - Security practices and guidelines  
- **[Stories](docs/stories/)** - User story definitions and implementation tracking
- **[Plans](docs/plans/)** - Technical implementation plans and specifications

## Story Implementation Status

| Story | Description | Status | Features |
|-------|-------------|--------|----------|
| **Story 1.2** | Rule Card Creation | ✅ **Complete** | 15 security Rule Cards across 5 domains |
| **Story 1.3** | Agent Compiler Toolchain | ✅ **Complete** | 5 specialized agent packages, validation, CI/CD |
| **Story 2.1** | Agentic Runtime & Router | ✅ **Complete** | AgenticRuntime engine for dynamic guidance |
| **Story 2.2** | Claude Code Sub-Agent | ✅ **Complete** | Real-time IDE integration, <2s response, secure snippets |
| **Story 2.3** | Manual On-Demand Execution | ✅ **Complete** | Manual security scans, workspace analysis, CI/CD prediction |
| **Story 2.4** | Semtools Semantic Search | ✅ **Complete** | Local semantic search, feature flags, corpus management, explain mode |
| **Story 2.5** | OWASP Cheat Sheet Ingestion | 📋 **Planned** | Automated OWASP content ingestion, 100+ generated Rule Cards, hybrid knowledge base |

### Current Capabilities
- ✅ **15 Security Rule Cards** covering secrets, web security, GenAI, containers
- ✅ **5 Specialized Agents** with domain expertise
- ✅ **Secure Compiler Toolchain** with comprehensive validation
- ✅ **AgenticRuntime** for dynamic rule selection and guidance
- ✅ **Claude Code Sub-Agent** with real-time security analysis
- ✅ **Manual Security Analysis** with file and workspace scanning
- ✅ **Semantic Search Integration** with local corpus and feature flag control
- ✅ **CI/CD Pipeline Prediction** for pre-commit validation
- ✅ **Performance Optimization** with caching and timeout handling
- ✅ **150+ Comprehensive Tests** covering all components, semantic search, and security validation

## Integration

### Claude Code Sub-Agent Integration
The security-guidance sub-agent can be used within Claude Code for real-time security analysis:

1. **Automatic Activation**: Claude Code automatically delegates security-related tasks to the sub-agent
2. **Context-Aware Analysis**: Detects frameworks (Flask, Django, etc.) and provides targeted guidance
3. **Performance Optimized**: Sub-2-second response requirement with intelligent caching
4. **Secure Code Generation**: Provides validated secure code snippets

### CI/CD Pipeline Integration
```bash
# Validation step
make validate || exit 1

# Compilation step  
make compile

# Testing step
make test || exit 1
```

### Scanner Tool Integration
Generated agent packages include `validation_hooks` mapping Rule Cards to scanner configurations:
- **Semgrep**: 57 unique rules across domains
- **TruffleHog**: 15 secret detection patterns
- **CodeQL**: 26 semantic analysis queries
- **Hadolint**: 1 Docker linting rule
- **Custom**: 3 domain-specific detection patterns

## Testing

### Comprehensive Test Suite (150+ Tests)
```bash
# Run complete test suite
python3 -m pytest tests/claude_code/test_sub_agent_framework.py -v

# Test Story 2.3 Manual Execution (NEW)
python3 -m pytest tests/claude_code/test_manual_execution.py -v

# Test Story 2.4 Semantic Search Integration (NEW)
python3 -m pytest tests/semantic/ -v

# Test specific components
python3 -m pytest tests/claude_code/test_sub_agent_framework.py::TestTask1 -v  # Sub-agent framework
python3 -m pytest tests/claude_code/test_sub_agent_framework.py::TestTask2 -v  # Real-time guidance  
python3 -m pytest tests/claude_code/test_sub_agent_framework.py::TestTask3 -v  # Secure snippets
python3 -m pytest tests/claude_code/test_sub_agent_framework.py::TestTask4 -v  # Performance optimization

# Test manual analysis features
python3 -m pytest tests/claude_code/test_manual_execution.py::TestManualCommandInterface -v
python3 -m pytest tests/claude_code/test_manual_execution.py::TestSecurityValidation -v
```

### Test Coverage
- **Sub-Agent Configuration**: 3 tests validating Claude Code integration
- **Runtime Management**: 5 tests covering initialization and package loading
- **Context Analysis**: 8 tests for code analysis and guidance generation
- **Security Validation**: 3 tests ensuring secure operation
- **Enhanced Features**: 5 tests for Task 2 improvements (scoring, frameworks)
- **Code Snippets**: 9 tests for Task 3 secure code generation
- **Performance**: 9 tests for Task 4 optimization (caching, timeout, metrics)
- **Manual Commands (NEW)**: 15+ tests for Story 2.3 manual analysis features
  - **Command Interface**: Path validation, parameter validation, security controls
  - **Analysis Engine**: File discovery, workspace traversal, rule aggregation
  - **Results Display**: Structured output, severity categorization, CI/CD prediction
  - **Security Validation**: Input sanitization, resource limits, authorization
  - **Integration**: End-to-end workflow testing and performance validation
- **Semantic Search (NEW)**: 100+ tests for Story 2.4 semantic search integration
  - **Corpus Management**: Rule card rendering, versioning, integrity validation, security features
  - **Search Interface**: Query processing, semtools integration, fallback mechanism, input validation
  - **Feature Flags**: Runtime retrieval control, audit logging, temporary enablement, configuration
  - **Developer Tools**: Manual command integration, explain mode, result formatting
  - **Performance & Reliability**: <1s search requirement, concurrent handling, resource limits
  - **Complete Integration**: End-to-end workflows, hybrid architecture validation, ADR compliance

## Contributing

1. **Create Rule Cards**: Follow schema in existing examples
2. **Validate Syntax**: `make validate`  
3. **Test Integration**: `make test`
4. **Build Packages**: `make build`
5. **Test Claude Code Sub-Agent**: `python3 -m pytest tests/claude_code/ -v`
6. **Submit Pull Request**: Include validation results

## Standards Compliance

Rule Cards implement security controls based on:
- **CWE**: Common Weakness Enumeration (30 unique references)
- **ASVS**: Application Security Verification Standard (28 unique references)  
- **OWASP**: Top 10 and security guidelines
- **NIST**: Cybersecurity Framework and Privacy Framework
- **RFC**: Internet standards (JWT, cookies, etc.)

## License
[To be determined]