# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the **GenAI Security Agents** repository, a collection of AI-powered security tools and frameworks with the primary focus on the CWE ChatBot project. The repository contains defensive security tools, documentation, and agent frameworks for cybersecurity professionals.

### Key Components

1. **CWE ChatBot** (`__________cwe_chatbot_bmad/`) - Primary active project
2. **Documentation** (`docs/`) - GenAI security research and ideation
3. **Prompts** (`prompts/`) - Reusable prompt templates for security agents
4. **Web Bundles** (`web-bundles/`) - BMad-Method AI agent framework configurations

## Project Structure

```
genai-sec-agents/
├── __________cwe_chatbot_bmad/    # Main CWE ChatBot project (see separate CLAUDE.md)
│   ├── apps/chatbot/              # Chainlit-based conversational AI application
│   ├── docs/                      # Comprehensive project documentation
│   ├── pyproject.toml            # Poetry configuration with Python 3.10+
│   └── CLAUDE.md                 # Detailed project-specific guidance
├── docs/                         # GenAI security research
│   └── chats/                    # Security analysis conversations
├── prompts/                      # Reusable prompt templates
└── web-bundles/                  # BMad-Method agent configurations
    ├── agents/                   # Specialized AI agents
    └── teams/                    # Agent team configurations
```

## Primary Development Context

**Most development work should focus on the CWE ChatBot project in `__________cwe_chatbot_bmad/`.**

### CWE ChatBot Project
- **Technology Stack**: Python 3.10+, Chainlit, PostgreSQL, Poetry
- **Architecture**: RAG-based conversational AI for CWE vulnerability analysis
- **Security Focus**: Enterprise-grade security with CSRF protection, rate limiting, input sanitization
- **Current Status**: Core implementation complete with production-ready security features

**For CWE ChatBot development, always refer to `__________cwe_chatbot_bmad/CLAUDE.md` for detailed project-specific guidance.**

## Development Commands

### Working with CWE ChatBot (Primary Project)
```bash
# Navigate to the main project
cd __________cwe_chatbot_bmad

# Install dependencies
poetry install

# Run the chatbot application
poetry run chainlit run apps/chatbot/main.py

# Run tests (always use poetry for application code)
poetry run pytest

# Security test scripts (use system python3)
python3 tests/scripts/test_command_injection_fix.py
python3 tests/scripts/test_sql_injection_prevention_simple.py

# Code quality
poetry run black .
poetry run ruff check .
```

### Repository-Level Operations
```bash
# Repository structure analysis
find . -name "*.py" -type f | head -20
find . -name "*.md" -type f | grep -E "(README|CLAUDE)" 

# Documentation exploration
ls -la docs/
ls -la web-bundles/agents/
```

## Key Development Principles

### 1. Security-First Development
This repository focuses on **defensive security tools only**:
- All tools are designed for vulnerability analysis and prevention
- No offensive security capabilities or malicious code creation
- Enterprise-grade security implementations required
- Comprehensive security testing mandatory

### 2. Poetry-Based Development
**Always use Poetry for Python dependency management:**
- Application code: `poetry run python`, `poetry run pytest`
- Standalone scripts: System `python3` (in `tests/scripts/`)
- Never mix system and virtual environment executables

### 3. Documentation-Driven Development
- All projects must have comprehensive documentation
- Architecture decisions documented with ADRs
- Security reviews documented and tracked
- User stories drive implementation priorities

## BMad-Method Agent Framework

This repository includes the BMad-Method framework for AI-driven development:

### Available Agents (`web-bundles/agents/`)
- **analyst**: Business analysis and requirements gathering
- **architect**: System design and technical architecture  
- **dev**: Code implementation and debugging
- **pm**: Product management and PRD creation
- **qa**: Testing and quality assurance
- **bmad-orchestrator**: Multi-agent coordination

### Team Configurations (`web-bundles/teams/`)
- **team-fullstack**: Complete development team
- **team-ide-minimal**: Minimal IDE-focused team
- **team-no-ui**: Backend-focused development team

## Security Guidelines

### Mandatory Security Practices
1. **Never hardcode secrets** - Use environment variables exclusively
2. **Input validation required** - All user inputs must be sanitized
3. **Security testing mandatory** - Run security test suites before deployment
4. **Container security** - Use SHA256-pinned base images
5. **Command execution safety** - Never use shell=True or os.system()

### Security Test Requirements
- Command injection prevention testing
- SQL injection prevention validation
- Container security verification
- CSRF protection validation
- Rate limiting effectiveness testing

## Project Status & Navigation

### Active Development
- **CWE ChatBot**: Production-ready with enterprise security features
- **Status**: Core implementation complete, cloud deployment ready

### Research & Documentation
- **GenAI Security Research**: Ongoing documentation in `docs/chats/`
- **Threat Modeling**: Comprehensive security analysis completed
- **Agent Framework**: BMad-Method configurations available

## Working with Multiple Projects

### When to Use Each CLAUDE.md
- **Root-level CLAUDE.md** (this file): Repository overview and multi-project guidance
- **CWE ChatBot CLAUDE.md**: Detailed development guidance for the main project

### Cross-Project Considerations
- Shared security principles apply across all projects
- BMad-Method agents can be used for any project type
- Documentation standards consistent across all components

## Important Notes

- **Defensive Security Focus**: This repository is for vulnerability analysis and prevention tools only
- **Production Security**: All implementations must meet enterprise security standards  
- **Poetry Dependency Management**: Consistent across all Python projects
- **Comprehensive Documentation**: Every project requires thorough documentation
- **Security Testing**: Mandatory for all code changes affecting security-critical components

## Next Steps for New Development

1. **For CWE ChatBot work**: Navigate to `__________cwe_chatbot_bmad/` and follow its CLAUDE.md
2. **For new security tools**: Follow the established patterns from CWE ChatBot
3. **For agent development**: Utilize the BMad-Method framework in `web-bundles/`
4. **For research**: Document findings in `docs/chats/` with appropriate context

**Remember**: This repository focuses exclusively on defensive security applications and vulnerability prevention tools.