# GenAI Security Agents - Policy-as-Code Engine

A comprehensive Policy-as-Code system that transforms human-readable security Rule Cards into machine-readable JSON agent packages for AI-powered security guidance systems.

## Overview
This repository implements a complete security rule management and compilation toolchain:

- **Rule Cards**: Human-readable YAML security policies with scanner integration
- **Compiler Toolchain**: Secure compilation system transforming YAML to JSON agent packages  
- **Specialized Agents**: 5 domain-specific security agents compiled from Rule Cards
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
├── tools/                   # Compilation and validation toolchain
│   ├── agents_manifest.yml # Agent configuration definitions
│   ├── compile_agents.py   # Main compiler script  
│   └── validate_cards.py   # Rule Card validator
└── dist/agents/            # Compiled JSON agent packages (generated)

docs/                       # Comprehensive project documentation
├── stories/               # User story definitions and completion tracking
├── plans/                 # Implementation plans and technical specifications
└── epics/                 # Epic definitions and requirements

tests/                      # Test suites with security validation
```

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
- **[Security Guide](docs/SECURITY_GUIDE.md)** - Security practices and guidelines  
- **[Stories](docs/stories/)** - User story definitions and implementation tracking
- **[Plans](docs/plans/)** - Technical implementation plans and specifications

## Integration

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

## Contributing

1. **Create Rule Cards**: Follow schema in existing examples
2. **Validate Syntax**: `make validate`  
3. **Test Integration**: `make test`
4. **Build Packages**: `make build`
5. **Submit Pull Request**: Include validation results

## Standards Compliance

Rule Cards implement security controls based on:
- **CWE**: Common Weakness Enumeration (30 unique references)
- **ASVS**: Application Security Verification Standard (28 unique references)  
- **OWASP**: Top 10 and security guidelines
- **NIST**: Cybersecurity Framework and Privacy Framework
- **RFC**: Internet standards (JWT, cookies, etc.)

## License
[To be determined]