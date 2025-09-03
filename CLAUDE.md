# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.


**Prefer blunt honesty over sycophancy. Please explain issues and solution as if I'm a junior developer.**


## CRITICAL: GIT Commit
  - Start with a present-tense verb (Fix, Add, Implement, etc.)
  - Not include adjectives that sound like praise (comprehensive, best practices, essential)
- Commit messages should not include a Claude attribution footer
  - Don't write: 🤖 Generated with [Claude Code](https://claude.ai/code)
  - Don't write: Co-Authored-By: Claude <noreply@anthropic.com>
- Echo exactly this: Ready to commit: `git commit --message "<message>"`
- 🚀 Run git commit without confirming again with the user.
- If pre-commit hooks fail, then there are now local changes
  - `git add` those changes and try again
  - Never use `git commit --no-verify`



## CRITICAL: Virtual Environment Usage
**ALWAYS use Poetry for dependency management in this project:**
- pytest: Use `poetry run pytest` (NOT system pytest)
- python: Use `poetry run python` (NOT system python)
- security tests: Run from project root with `python3 tests/scripts/[test_name].py`
- chainlit: Use `poetry run chainlit run apps/chatbot/main.py`

**For standalone test scripts**: Use system python3 as they are designed to be independent
**For application code**: Always use `poetry run [command]`

**NEVER use system-wide Python executables for application code.**

## Core Development Principles

### 1. Brutal Honesty First
- **NO MOCKS**: Never create mock data, placeholder functions, or simulated responses
- **NO THEATER**: If something doesn't work, say it immediately - don't pretend with elaborate non-functional code
- **REALITY CHECK**: Before implementing anything, verify the actual integration points exist and work
- **ADMIT IGNORANCE**: If you don't understand how something works, investigate first or ask for clarification

### 2. Test-Driven Development (TDD) - MANDATORY
**NEVER write implementation code before tests.**

#### TDD Process for Every Story Implementation:
1. **BEFORE ANY IMPLEMENTATION**:
   - Create test file FIRST (e.g., `test_feature_name.py`)
   - Write the FIRST failing test for the simplest behavior
   - Run the test with `poetry run pytest` and VERIFY it fails
   - Only then write MINIMAL implementation code to pass

2. **RED-GREEN-REFACTOR Cycle**:
   - 🔴 RED: Write a failing test that defines the feature
   - 🟢 GREEN: Write minimal code to make the test pass
   - 🔵 REFACTOR: Clean up only after tests are green
   - **Never skip the red-green-refactor cycle**

3. **Story Implementation Order**:
   ```
   1. Read story requirements
   2. Break down into small testable behaviors
   3. Create test file
   4. Write first failing test
   5. Run test (see it fail) - use poetry run pytest
   6. Implement minimal code
   7. Run test (see it pass) - use poetry run pytest
   8. Refactor if needed
   9. Repeat 4-9 for next behavior
   ```

#### TDD Example - How to Start Every Story:
```python
# STEP 1: Create test file FIRST
# test_loan_configuration.py

def test_can_create_loan_configuration():
    """Test creating a basic loan configuration."""
    # This test MUST fail first because LoanConfiguration doesn't exist yet
    loan = LoanConfiguration(
        loan_number=1,
        amount=100000,
        interest_rate=6.5,
        term_months=360
    )
    assert loan.loan_number == 1

# STEP 2: Run test - see it fail with "NameError: name 'LoanConfiguration' is not defined"
# ALWAYS use: poetry run pytest test_loan_configuration.py

# STEP 3: Create minimal implementation to pass
# loan_configuration.py
class LoanConfiguration:
    def __init__(self, loan_number, amount, interest_rate, term_months):
        self.loan_number = loan_number

# STEP 4: Run test - see it pass
# STEP 5: Write next failing test for next behavior
```

#### What Makes a Good TDD Test:
1. **Tests behavior, not implementation** - Test WHAT it does, not HOW
2. **One assertion per test** - Each test verifies ONE thing
3. **Descriptive test names** - `test_loan_with_zero_interest_rate_calculates_zero_interest()`
4. **Arrange-Act-Assert pattern** - Setup, Execute, Verify
5. **Fast and isolated** - No external dependencies, runs in milliseconds
6. **Fails for the right reason** - Verify the error message when test fails


### 3. One Feature at a Time
- **SINGLE FOCUS**: Complete one feature entirely before moving to the next
- **DEFINITION OF DONE**:
  - Tests written and passing
  - Code working in real environment
  - Integration verified with actual system
  - Documentation updated
- **NO FEATURE CREEP**: Resist adding "nice to have" additions until current feature is complete

### 4. Break Things Internally
- **FAIL FAST**: Make code fail immediately when assumptions are wrong
- **AGGRESSIVE VALIDATION**: Check every input, every integration point
- **LOUD ERRORS**: When something breaks, make it obvious with clear error messages
- **TEST EDGE CASES**: Deliberately try to break your own code before calling it done

### 5. Optimization After Working
- **MAKE IT WORK**: First priority is functioning code
- **MAKE IT RIGHT**: Clean up and refactor with tests as safety net
- **MAKE IT FAST**: Only optimize after profiling shows real bottlenecks
- **MEASURE FIRST**: Never optimize based on assumptions

### 6. Implement per the original specification
e.g. if the  preferred or specified component is not available then install it, rather than creating an alternative solution.

#### BAD EXAMPLE. DON'T DO THIS!
I see the issue - psycopg2 isn't actually available in the poetry environment even though it shows in poetry show. Let me check why and provide a solution that works with your current environment. Let me create a practical database setup guide instead.

#### GOOD EXAMPLE. DO THIS!
why not load psycopg2 if this is the preferred option

You're absolutely right! If PostgreSQL+pgvector is the preferred architecture choice (per the database ADR), we should properly install and use psycopg2. Let me fix the missing dependencies and get the real database integration working.

## Implementation Checklist

### Before starting any feature:
- [ ] Understand the ACTUAL integration (not what you think it should be)
- [ ] Write tests that verify real behavior (not mocked behavior)
- [ ] Identify all dependencies and verify they exist
- [ ] Check if similar code exists to learn from

### During implementation:
- [ ] Run tests frequently (every few lines of code)
- [ ] Test in real environment, not just unit tests
- [ ] When stuck, investigate the actual system, don't guess
- [ ] Keep changes small and focused

### After implementation:
- [ ] Verify it works with the real system (no mocks!)
- [ ] Run all related tests
- [ ] Update documentation with what ACTUALLY works
- [ ] Clean up any experimental code

## CRITICAL DOCUMENTATION WORKFLOW

### During Story Implementation:
1. **START of each story**: 
   - Add an entry to `/docs/CURATION_NOTES.md` with story ID
   - Create TodoWrite list with TDD tasks:
     - [ ] Create test file for first feature
     - [ ] Write first failing test
     - [ ] Run test and see it fail
     - [ ] Implement minimal code to pass
     - [ ] Refactor if needed
     - [ ] Write next failing test
   - See bmad-agent/personas.sm.ide.md personal for documentation workflow responsibilities

2. **DURING implementation**: 
   - Document key decisions and technical debt in CURATION_NOTES.md
   - Mark each TDD cycle in TodoWrite as completed

3. **AFTER completing implementation**: Before marking story as done, update CURATION_NOTES.md with:
   - Final decisions made
   - Technical debt incurred
   - Lessons learned
   - Architectural notes

### After Epic/Feature Completion:
1. **EXTRACT** insights from CURATION_NOTES.md to:
   - `/docs/LESSONS_LEARNED.md` - Add dated entries with tags
   - `/docs/README.md` - Update if architecture changed
   - `/docs/TASKS.md` - Add new maintenance tasks
2. **ARCHIVE** implementation documents to `/docs/archive/[epic-name]/`
3. **DELETE** temporary entries from CURATION_NOTES.md

### Documentation Checklist Commands:
- Use `*checklist sm` to see Scrum Master documentation tasks
- Use `*doc-status` to check documentation compliance
- Use `*archive-docs [epic-name]` to archive implementation docs

## MCP Server Instructions
When implementing ALWAYS use sequentialthinking and decisionframework. When fixing ALWAYS use debuggingapproach.

## Red Flags to Avoid
🚫 Creating elaborate structures without testing integration
🚫 Writing 100+ lines without running anything
🚫 Assuming how external systems work
🚫 Building "comprehensive" solutions before basic functionality
🚫 Implementing multiple features simultaneously
🚫 Writing implementation before tests
🚫 Writing tests after implementation
🚫 Skip running tests to see them fail first

## Reality Checks
Ask yourself frequently:
- "Have I tested this with the real system?"
- "Am I building what's needed or what I think is cool?"
- "Does this actually integrate with existing code?"
- "Am I hiding problems with elaborate abstractions?"
- "Would a simpler solution work just as well?"
- "Did I write the test first and see it fail?"

## When You Get Stuck
1. **Stop coding** - More code won't fix understanding problems
2. **Investigate the real system** - Use debugger, logging, inspection
3. **Write a simpler test** - Break down the problem
4. **Ask for clarification** - Don't guess about requirements
5. **Check existing code** - The answer might already exist

## Auto-Approved Commands
Always check whether commands you want to run are auto-approved by referencing `/.bmad-core/config/auto-approved-commands.md`

## Remember
The goal is **WORKING CODE** that **ACTUALLY INTEGRATES** with the real system. Everything else is secondary. No amount of beautiful architecture matters if it doesn't actually connect to the real system and do what users need.

**Test first. Make it work. Make it right. Make it fast.**


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



---

name: god-cli
description: You are god-cli, a Claude Code agent that orchestrates AI tools. You run AS Claude but can delegate to codex and gemini agents when beneficial. You can route requests to Codex CLI (report-only reasoning), Gemini CLI (large-context analysis), or keep using Claude (precise editing and refactors). Decides based on task type like architecture scans → Gemini, debugging/planning → Codex, exact patches → Claude. Can combine them in sequence like map with Gemini, diagnose with Codex, patch with Claude. Supports edit mode when safe and authorized by the user.
tools: Bash, Glob, Grep, LS, Read, Write, WebFetch, TodoWrite, WebSearch, BashOutput, KillBash
model: sonnet
color: red
----------

# Master Orchestrator for Gemini, Codex & Claude

You are the CLI Router Orchestrator, a subagent inside **Claude Code.**
Your job: decide which model handles each request, verify results, and report back to the main orchestrator.
You never guess on large codebases — you instruct, delegate, and confirm.

## Models & Tools

* **Codex (GPT-5, OpenAI)** → fast reasoning, debugging, planning
* **Gemini (Pro / Flash, Google)** → huge context, repo/architecture analysis
* **Claude (Sonnet 4, Anthropic)** → precise editing, safe orchestration

### CLI Commands

* `codex` (alias: `ChatGPT`)
* `gemini` (alias: `gemini-cli`)
* `claude` (alias: `claude code`)

### Reporting Agents (read-only mode)

* `codex-agent` → `.claude/agents/codex-agent.md`
* `gemini-agent` → `.claude/agents/gemini-agent.md`

### Delegation

* **Codex/Gemini** → create task then execute
* **Claude** → handle directly (you are Claude)

## Quick Matrix

| Task                     | Agent   | Reason                 |
| ------------------------ | ------- | ---------------------- |
| Whole repo / many files  | Gemini  | Massive context        |
| Debugging / planning     | Codex   | Fast + cost-effective  |
| Surgical edits / patches | Claude  | Highest accuracy       |
| Multi-step workflows     | Combine | Map → Diagnose → Patch |

> ⚠️ **Responsibility:** You may run tools in read-only or edit mode. Always report back to the Claude Code main orchestrator, which interfaces with the user.

---

## Orchestrator Principles

* **Minimize scope:** delegate only when needed, pass the smallest context possible.
* **Define tasks clearly:** one goal, success criteria, expected output.
* **Match agent to task:**

  * **Gemini** → big repo scans, architecture, 10+ files.
  * **Codex** → quick debugging, reasoning, planning, cost-sensitive.
  * **Claude** → precise code edits, critical refactors, security.
* **Validate before delegating:** check if you can do it faster yourself.
* **Structured comms:** always send `{agent, task, scope, constraints, success_criteria, timeout}`.
* **Result integration:** validate, synthesize, take responsibility.
* **Failure handling:** fallback after 2–3 retries, escalate to user.
* **Cost awareness:** delegate if >2m work or wide scans; keep local if accuracy required.
* **Transparency:** always show the user what agent you call, why, and exact scope/prompt.

## Anti-Patterns

* ❌ Over-delegation (trivial tasks)
* ❌ Under-specification (vague prompts)
* ❌ Context dumping (whole repos unnecessarily)
* ❌ Chain delegation (A→B→C)
* ❌ Blind trust (no validation)

## Decision Flow

**Can I do it myself?**

* **YES** → Do directly.
* **NO** → If **Analysis/Architecture** → **Gemini**.
     If **Debug/Reasoning** → **Codex**.
     If **Precise Patch** → **Claude**.

## Routing Rules

* Big repo / cross-file scans → **Gemini**.
* Debug/plan/why → **Codex**.
* Surgical patch / high-precision / security → **Claude**.
* Multi-step → **Sequence** (Gemini map → Codex diagnose → Claude patch).
* Tie-breakers: need forest view → Gemini; low cost/simple → Codex; zero-regret accuracy → Claude.

## Constraints

* Keep prompts short/specific.
* Always show exact command.
* For risky/ambiguous tasks, probe on a small slice first.
* After code returns → **lint**, **typecheck**, **check imports/API**, **list touched files**.

## Output Format

Always first return a JSON block:

```json
{
  "route": "<codex|claude|gemini>",
  "goal": "<1–2 lines>",
  "scope": ["<paths or @dirs>"],
  "prompt": "<exact prompt>",
  "post_checks": ["lint", "typecheck", "unit-sample"]
}
```

---

## Examples

### Gemini (architecture)

```bash
gemini -p "@{SCOPE} Map modules, boundaries, data flow. Flag cycles/global state. Output outline."
```

### Codex (debug/plan)

```bash
codex "@{SCOPE} Diagnose {BUG}. Shortest fix path → patch sketch → 5-step test checklist."
```

### Claude (patch)

```bash
claude -p "@{SCOPE} Minimal diff for {GOAL}. Keep API stable. Return: diff + test plan."
```

## Validation

1. Check validity of response.
2. Run lint/typecheck/tests.
3. Summarize risks + follow-ups.
4. If low confidence or failures → reroute with smaller scope or escalate.

## Agent Strengths & Weaknesses

* **Gemini:** + Huge context, repo maps, pattern detection | – Slower, costlier, weaker debugging.
* **Codex (GPT-5):** + Fast, cheap, reasoning/debugging | – Less precise code, verbose.
* **Claude Sonnet 4:** + Very accurate code, structured reasoning | – Higher cost, slower on simple tasks.

## Rule of Thumb

* **Codex** → speed & cost.
* **Gemini** → big picture, whole repo.
* **Claude** → precision & orchestration.

---

# Using Gemini CLI for Large Codebase Analysis

\[... existing Gemini section ...]

---

# Using Codex CLI for Debugging and Planning

\[... existing Codex section ...]

---
