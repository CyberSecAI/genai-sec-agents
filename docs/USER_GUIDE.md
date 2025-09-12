# GenAI Security Agents - User Guide

Complete guide for using the GenAI Security Agents Policy-as-Code system, from rule card development to Claude Code integration.

**🔗 Navigation:**
- **[← Documentation Overview](README.md)** - Complete documentation hub and reading order
- **[← Main README](../README.md)** - Repository overview and quick start
- **[⭐ Worked Example](WORKED_EXAMPLE.md)** - Hands-on demonstration with Flask app

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Detailed Workflows](#detailed-workflows)
- [Rule Card Development](#rule-card-development)
- [Agent Configuration](#agent-configuration)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Overview

The GenAI Security Agents system transforms security knowledge into intelligent development assistance through multiple integrated components:

- **Semantic Search Corpus**: OWASP CheatSheets (102 files) + ASVS standards (17 files) for comprehensive security guidance
- **Rule Card Compilation**: YAML to JSON transformation with security validation for Claude Code sub-agents
- **Development Integration**: Real-time security guidance during coding with Claude Code CLI
- **Multi-Search Approach**: Semantic search + lexical search + compiled rule cards for comprehensive coverage
- **Standards Compliance**: Automatic CWE, ASVS, and OWASP reference validation and mapping

## Installation

### Prerequisites
- Python 3.11+ 
- Git repository access
- Rust toolchain (for semantic search capabilities)
- Basic YAML knowledge for Rule Card creation

### Setup
```bash
# Clone repository
git clone <repository-url>
cd genai-sec-agents

# Install Rust and semtools for semantic search
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
cargo install semtools

# Build OWASP & ASVS semantic search corpus
make semsearch-build

# Verify installation
make help
make validate
```

The system includes both compiled rule cards (using Python standard library) and semantic search capabilities (using Rust-based semtools).

## Quick Start

### 1. Validate Existing Rule Cards
```bash
make validate
```
**Output**: Validation report for all 15 Rule Cards across 5 domains

### 2. Compile Agent Packages
```bash
make compile
```
**Output**: 5 JSON agent packages in `app/dist/agents/`

### 3. Run Full Build
```bash
make build
```
**Output**: Complete validation + compilation workflow

### 4. Test Everything
```bash
make test
```
**Output**: Security validation and integration test results

### 5. Use Semantic Search for Development
```bash
# Search OWASP guidance for JWT security
make semsearch q="JWT token validation best practices"

# Search ASVS standards for authentication requirements
make semsearch-asvs q="password security requirements"

# Use with Claude Code CLI for development assistance
# See main README.md for comprehensive development workflow examples
```
**Output**: Semantic search results from OWASP CheatSheets and ASVS standards

## Detailed Workflows

### Rule Card Validation Workflow
```bash
# Validate single Rule Card
python3 app/tools/validate_cards.py app/rule_cards/secrets/SECRETS-API-001.yml

# Validate entire domain
python3 app/tools/validate_cards.py app/rule_cards/secrets/

# Validate all Rule Cards
python3 app/tools/validate_cards.py app/rule_cards/
```

**Validation Checks**:
- YAML syntax correctness
- Required field completeness
- Schema compliance
- Security standards reference validity

### Compilation Workflow
```bash
# Basic compilation
python3 app/tools/compile_agents.py

# With verbose logging
python3 app/tools/compile_agents.py --verbose

# Custom configuration
python3 app/tools/compile_agents.py --manifest custom_manifest.yml --output dist/custom/

# Force overwrite existing packages
python3 app/tools/compile_agents.py --force
```

**Compilation Process**:
1. Load and validate `agents_manifest.yml`
2. Load Rule Cards matching agent patterns
3. Generate metadata (version, build date, source digest)
4. Aggregate validation hooks from detect metadata
5. Compile to JSON with schema validation
6. Save agent packages with integrity checks

## Rule Card Development

### Creating New Rule Cards

#### Step 1: Choose Security Domain
Add to existing directories or create new domain:
- `app/rule_cards/secrets/` - Hardcoded secrets prevention
- `app/rule_cards/cookies/` - Web cookie security
- `app/rule_cards/jwt/` - JWT token validation
- `app/rule_cards/genai/` - GenAI security controls
- `app/rule_cards/docker/` - Container security
- `app/rule_cards/your-domain/` - New security domain

#### Step 2: Follow Schema Structure
```yaml
id: DOMAIN-TOPIC-001              # Unique identifier (required)
title: "Human readable title"     # Descriptive title (required)
severity: critical                # critical|high|medium|low (required)
scope: application-type           # Target context (required)
requirement: "Detailed requirement description"  # Normative requirement (required)

do:                              # Positive practices (required)
  - "Practice 1"
  - "Practice 2"

dont:                            # Anti-patterns (required)
  - "Anti-pattern 1"
  - "Anti-pattern 2"

detect:                          # Scanner integration (required)
  semgrep:
    - "rule-id-1"
    - "rule-id-2"
  trufflehog:
    - "Secret Type"
  codeql:
    - "query-name"
  custom:
    - "Custom detection logic"

verify:                          # Validation tests (required)
  tests:
    - "Test description 1"
    - "Test description 2"

refs:                           # Standards references (required)
  cwe:
    - "CWE-XXX"
  asvs:
    - "V.X.X"
  owasp:
    - "AXX:YYYY"
  standards:
    - "Standard reference"
```

#### Step 3: Follow Naming Conventions
- **ID Format**: `DOMAIN-TOPIC-001` (uppercase, incrementing numbers)
- **File Name**: Match ID with `.yml` extension (`DOMAIN-TOPIC-001.yml`)
- **Directory**: Organize by security domain (`app/rule_cards/domain/`)

#### Step 4: Add Scanner Integration
Include specific scanner rules in the `detect` section:

**Semgrep Examples**:
```yaml
detect:
  semgrep:
    - "javascript.jsonwebtoken.security.jwt-hardcode-key"
    - "python.jwt.security.jwt-hardcode-key"
    - "generic.secrets.security.hardcoded-secret"
```

**TruffleHog Examples**:
```yaml
detect:
  trufflehog:
    - "API Key"
    - "JWT Secret"
    - "Private Key"
```

**CodeQL Examples**:
```yaml
detect:
  codeql:
    - "hardcoded-credentials"
    - "jwt-signature-not-verified"
```

#### Step 5: Validate and Test
```bash
# Validate new Rule Card
python3 app/tools/validate_cards.py app/rule_cards/your-domain/YOUR-CARD-001.yml

# Test compilation
make compile

# Verify in agent package
cat app/dist/agents/comprehensive-security-agent.json | jq '.rules[] | select(.id=="YOUR-CARD-001")'
```

### Rule Card Best Practices

#### Security Requirements
- **Be Specific**: Clearly define the security requirement and context
- **Include Standards**: Always map to CWE, ASVS, and OWASP where applicable
- **Scanner Ready**: Include real scanner rule references for automation
- **Testable**: Write verification tests that can be implemented

#### Content Guidelines
- **Do/Don't Balance**: Include both positive practices and anti-patterns
- **Actionable Guidance**: Make recommendations implementable by developers
- **Context Aware**: Specify scope and applicable scenarios clearly
- **Evidence Based**: Base requirements on established security standards

#### Technical Requirements
- **Valid YAML**: Ensure syntax correctness and proper escaping
- **Schema Compliance**: Include all required fields
- **Unique IDs**: Use consistent naming across the domain
- **Version Control**: Track changes and maintain backward compatibility

## Agent Configuration

### Understanding agents_manifest.yml

The manifest defines which Rule Cards each agent includes:

```yaml
version: "1.0"
description: "Agent configuration manifest"

agents:
  - name: "secrets-specialist"
    description: "Hardcoded secrets detection and prevention"
    rule_cards:
      - "secrets/*.yml"
    output_file: "secrets-specialist.json"
    domains:
      - "API key security"
      - "Database credential protection"

  - name: "comprehensive-security-agent"  
    description: "Multi-domain security agent"
    rule_cards:
      - "secrets/*.yml"
      - "cookies/*.yml"
      - "jwt/*.yml"
      - "genai/*.yml"
      - "docker/*.yml"
    output_file: "comprehensive-security-agent.json"

compilation:
  base_path: "app/rule_cards"
  output_path: "app/dist/agents"
  schema_version: "1.0"

security:
  safe_yaml_loading: true
  path_validation: true
  schema_validation: true
  attribution_required: true
```

### Creating Custom Agents

#### Add New Agent Definition
```yaml
agents:
  - name: "api-security-specialist"
    description: "API security focused agent"
    rule_cards:
      - "api/*.yml"
      - "secrets/SECRETS-API-001.yml"
    output_file: "api-security-specialist.json"
    domains:
      - "API authentication security"
      - "API key management"
```

#### Recompile with New Agent
```bash
make compile
```

The compiler will automatically generate the new agent package.

## Advanced Usage

### Custom Manifest Configuration
```bash
# Use custom manifest
python3 app/tools/compile_agents.py --manifest custom_manifest.yml

# Custom input and output paths
python3 app/tools/compile_agents.py --rule-cards custom/rule_cards/ --output custom/agents/
```

### Debugging and Logging
```bash
# Enable verbose logging
python3 app/tools/compile_agents.py --verbose

# Debug specific agent
python3 app/tools/compile_agents.py --verbose | grep "secrets-specialist"
```

### Integration with CI/CD
```yaml
# .github/workflows/security.yml
name: Security Rule Validation
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Validate Rule Cards
        run: make validate
      - name: Compile Agent Packages
        run: make compile
      - name: Run Security Tests
        run: make test
```

### Output Analysis
```bash
# Analyze generated agent package
jq '.agent | {name, version, build_date, domains}' app/dist/agents/secrets-specialist.json

# Extract validation hooks
jq '.validation_hooks' app/dist/agents/comprehensive-security-agent.json

# Count rules by severity
jq '[.rules[] | .severity] | group_by(.) | map({severity: .[0], count: length})' app/dist/agents/comprehensive-security-agent.json
```

## Troubleshooting

### Common Issues

#### YAML Syntax Errors
```
Error: Invalid YAML in app/rule_cards/secrets/SECRETS-API-001.yml: scanner cannot find expected ':'
```
**Solution**: Check YAML indentation and colons. Use `yamllint` or validate online.

#### Missing Required Fields
```
Warning: Rule card SECRETS-API-001 missing fields: ['verify']
```
**Solution**: Add all required fields from the schema. Check existing cards for examples.

#### Path Traversal Security Error
```
SecurityError: Unsafe rule card pattern: ../../../etc/passwd
```
**Solution**: Use relative paths within `app/rule_cards/`. Remove `../` patterns.

#### Compilation Permission Errors
```
PermissionError: [Errno 13] Permission denied: 'app/dist/agents/secrets-specialist.json'
```
**Solution**: Check write permissions on output directory. Run `chmod -R 755 app/dist/`.

#### Git Version Generation Fails
```
subprocess.CalledProcessError: Command '['git', 'rev-parse', 'HEAD']' returned non-zero exit status
```
**Solution**: Ensure you're in a Git repository. The compiler falls back to timestamp-based versioning.

### Validation Debugging

#### Check Rule Card Structure
```bash
# Validate single file with verbose output
python3 app/tools/validate_cards.py app/rule_cards/secrets/SECRETS-API-001.yml --verbose
```

#### Examine Compiled Output
```bash
# Pretty print agent package
python3 -m json.tool app/dist/agents/secrets-specialist.json

# Validate JSON structure
python3 -c "import json; json.load(open('app/dist/agents/secrets-specialist.json'))"
```

#### Test Compilation Components
```bash
# Test compilation without saving
python3 -c "
import sys
sys.path.insert(0, 'app/tools')
from compile_agents import RuleCardCompiler, CompilerConfig

config = CompilerConfig(
    manifest_path='app/tools/agents_manifest.yml',
    rule_cards_path='app/rule_cards/',
    output_path='app/dist/agents/'
)
compiler = RuleCardCompiler(config)
manifest = compiler.load_manifest()
print(f'Loaded {len(manifest[\"agents\"])} agents')
"
```

## Best Practices

### Development Workflow
1. **Plan First**: Design Rule Card scope and requirements before implementation
2. **Follow Examples**: Use existing Rule Cards as templates for consistency
3. **Validate Early**: Run validation after each Rule Card creation
4. **Test Integration**: Ensure compiled agents include your Rule Cards
5. **Document Changes**: Update agent descriptions when adding new domains

### Security Considerations
- **Review Content**: Ensure Rule Cards don't include sensitive information
- **Validate References**: Check that scanner rules and standards references are current
- **Test Scenarios**: Include real-world attack scenarios in verification tests
- **Monitor Output**: Review compiled agent packages for completeness and accuracy

### Maintenance Guidelines
- **Regular Updates**: Keep scanner rule references current as tools evolve
- **Standards Alignment**: Update CWE/ASVS/OWASP references when standards change
- **Performance Monitoring**: Track compilation times as Rule Card count grows
- **Version Management**: Use semantic versioning for significant changes

### Team Collaboration
- **Code Reviews**: Review Rule Card content for accuracy and completeness
- **Testing Standards**: Maintain consistent test coverage across domains
- **Documentation**: Keep user guide and examples current with changes
- **Knowledge Sharing**: Document domain expertise and security rationale

This comprehensive user guide provides everything needed to effectively use and extend the GenAI Security Agents system. 

**🔗 Related Documentation:**
- **[📋 Documentation Overview](README.md)** - Complete documentation hub with reading order
- **[⭐ Worked Example](WORKED_EXAMPLE.md)** - Step-by-step demonstration with real code analysis
- **[🏗️ System Architecture](architecture.md)** - Technical architecture and design patterns
- **[📊 Implementation Stories](stories/)** - Detailed user stories and completion tracking

---

**Need Help?** Check the [main documentation hub](README.md) for the complete documentation ecosystem and proper reading order.