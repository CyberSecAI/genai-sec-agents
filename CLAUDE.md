<!-- cSpell:words pytest psycopg pgvector bmad hashlib Unvalidated popen getenv hexdigest ASVS sequentialthinking decisionframework debuggingapproach genai asvs semsearch -->

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.


**Prefer blunt honesty over sycophancy. Please explain issues and solution as if I'm a junior developer.**


## CRITICAL: GIT Commit
  - Start with a present-tense verb (Fix, Add, Implement, etc.)
  - Do not include adjectives that sound like praise (comprehensive, best practices, essential)
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
- agent compilation: Use `poetry run python app/tools/compile_agents.py`

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

## SECURITY-FIRST DEVELOPMENT WORKFLOW

This repository contains **defensive security tools** with specialized security agents. **MANDATORY**: Use security specialist agents for any security-related code changes.

## ESSENTIAL SECURITY AWARENESS

### Never Implement These Patterns (Auto-Trigger Agent Calls)
🚨 **Weak Cryptography** → `hashlib.md5|.sha1|DES` → Use SHA-256+ → Call comprehensive-security-agent  
🚨 **Hardcoded Secrets** → `api_key = "sk-..."|password = "..."` → Environment variables only → Call secrets-specialist  
🚨 **Unvalidated Input** → `request.form|input()|sys.argv` without validation → Always sanitize → Call input-validation-specialist  
🚨 **Command Injection** → `subprocess.*shell=True|os.system|os.popen` → Use parameterized arrays → Call input-validation-specialist  
🚨 **SQL Injection** → String concatenation in queries → Use prepared statements → Call input-validation-specialist  
🚨 **Path Traversal** → `open(user_input)|Path(user_input)` → Validate paths → Call input-validation-specialist  
🚨 **Insecure HTTP** → `requests.*verify=False|urllib.*` → Always verify SSL → Call configuration-specialist  

### Auto-Trigger Security Agents Based on Code Patterns

**When code contains these patterns, IMMEDIATELY call the specified agent:**

```python
# Cryptographic operations
hashlib.md5|.sha1|.des → comprehensive-security-agent
random.random|uuid.uuid4 → comprehensive-security-agent (if used for security)
ssl.|tls.|certificate → comprehensive-security-agent

# Input/Output processing  
request.form|request.args|request.json → input-validation-specialist
input()|sys.argv|click.argument → input-validation-specialist
subprocess.|os.system|os.popen → input-validation-specialist

# Authentication/Authorization
password|login|authenticate|session → authentication-specialist  
authorize|permission|role|access → authorization-specialist
token|jwt|bearer|oauth → session-management-specialist

# Secret/Credential handling
api_key|secret|credential|private_key → secrets-specialist
getenv|environ|config → secrets-specialist (if accessing secrets)

# File/Network operations
open(|Path(|file(|urllib|requests → configuration-specialist
connect|socket|server|client → configuration-specialist

# Logging/Monitoring
logger|log.|print(|sys.stdout → logging-specialist (if may log secrets)
```

### CRITICAL: Pre-Implementation Security Guard

**BEFORE implementing security code in a specific file, you MUST:**

**Detection Pattern**:
```
IF user prompt contains:
  - File path with extension: \.(py|js|ts|java|go|rb|php|cs)\b
  AND
  - Security keyword: (auth|login|password|session|token|oauth|mfa|jwt|crypto|hash|secret|api_key|credential)
```

**Then MANDATORY workflow**:
```
1. STOP → Do NOT write/modify files yet
2. RESEARCH → Run STEP 1 (semantic-search agent)
3. ANALYZE → Run STEP 2 (specialist agents in parallel)
4. GUIDE → Provide security requirements with ASVS citations
5. CONFIRM → Ask user: "Ready to implement with these security requirements?"
6. IMPLEMENT → STEP 3 (only after user confirmation)
```

**Examples that trigger guard**:
- "Add MFA to src/auth/login.py" → STOP → Research → Guide → Confirm
- "Implement OAuth2 in app.js" → STOP → Research → Guide → Confirm
- "Fix password hashing in user_model.rb" → STOP → Research → Guide → Confirm

**Rationale**: Isolation tests (A4, A8) proved file-specific prompts bypass research phase. This guard enforces security-first workflow for ALL file-specific security implementations.

---

### Expanded Review Intent Patterns

**Review tasks now auto-activate security specialists**:

```
Pattern 1: Explicit security review
  (?i)\breview\b.*\b(security|vulnerabilit|exploit|attack)\b
  → comprehensive-security-agent

Pattern 2: Auth/session review (no "security" keyword needed)
  (?i)\breview\b.*\b(authenticate|login|password|session|token|oauth|jwt)\b
  → authentication-specialist + session-management-specialist

Pattern 3: Audit/pentest intent
  (?i)\b(audit|pen.*test|security.*scan|threat.*model)\b
  → comprehensive-security-agent

Pattern 4: Authorization review
  (?i)\breview\b.*\b(authorize|permission|access.*control|role)\b
  → authorization-specialist
```

**Fix for A7 false negative**: "Review authenticate_user()" now triggers authentication-specialist (no "security" keyword required).

---

### Security Implementation Patterns (Always Use)

```python
# ✅ SECURE: Cryptographic hashing
import hashlib
hash_value = hashlib.sha256(data.encode()).hexdigest()

# ✅ SECURE: Environment variables for secrets
import os
api_key = os.getenv('API_KEY')
if not api_key:
    raise ValueError("API_KEY environment variable required")

# ✅ SECURE: Input validation
from app.security.input_validation import InputValidator
validated_input = InputValidator.validate_string_field(user_input, "username")

# ✅ SECURE: Subprocess calls
subprocess.run(['git', 'status'], cwd=safe_path, timeout=10, shell=False)

# ✅ SECURE: HTTP requests with SSL verification
response = requests.get(url, verify=True, timeout=30)

# ✅ SECURE: Path validation
from app.security.path_security import PathValidator
safe_path = PathValidator.validate_file_path(user_path, base_dir)
```

### Mandatory Security Checks Before Any Implementation

**ALWAYS ask yourself:**
- "Does this code handle user input?" → input-validation-specialist
- "Does this code use cryptography?" → comprehensive-security-agent  
- "Does this code access secrets/credentials?" → secrets-specialist
- "Does this code authenticate/authorize users?" → authentication-specialist + authorization-specialist
- "Does this code make network requests?" → configuration-specialist
- "Does this code log information?" → logging-specialist

### Security Decision Tree

```
Code Change Type → Required Security Agent(s)
│
├─ Cryptographic operations → comprehensive-security-agent
├─ User input processing → input-validation-specialist
├─ Authentication/login → authentication-specialist  
├─ Authorization/permissions → authorization-specialist
├─ Session management → session-management-specialist
├─ Secret/credential handling → secrets-specialist
├─ Configuration/network → configuration-specialist
├─ Logging/monitoring → logging-specialist
├─ Web security (XSS/CSRF) → web-security-specialist
├─ Data handling/privacy → data-protection-specialist
└─ Multiple domains → comprehensive-security-agent (+ parallel specialists)
```

### Automatic Security Agent Triggering

**CRITICAL**: Call appropriate security specialist agents based on the type of change:

#### Code Change Type → Required Agent
- **Authentication/Login code** → `authentication-specialist`
- **Authorization/Access control** → `authorization-specialist`  
- **Input validation/User data** → `input-validation-specialist`
- **Cryptographic operations** → `comprehensive-security-agent` (has crypto rules)
- **Session management** → `session-management-specialist`
- **Secret/Credential handling** → `secrets-specialist`
- **Configuration changes** → `configuration-specialist`
- **Logging/Monitoring** → `logging-specialist`
- **Web security (XSS/CSRF)** → `web-security-specialist`
- **Data handling** → `data-protection-specialist`
- **Multiple domains** → `comprehensive-security-agent`

#### Security Agent Usage Pattern
```javascript
// STEP 1: Research security guidance BEFORE implementing
use the .claude/agents/semantic-search.md agent to search for [security topic] guidance in research corpus

// STEP 2: Get implementation guidance (BEFORE coding)
use the .claude/agents/[agent-name].md agent to provide guidance for implementing [security feature] following security rules

// STEP 3: Implement code with loaded context

// STEP 4: Validate implementation (AFTER coding)
use the .claude/agents/[agent-name].md agent to validate [implemented code] against security rules and detect vulnerabilities

// EXAMPLE: Complete crypto fix workflow  
use the .claude/agents/semantic-search.md agent to find cryptographic best practices for hash algorithms
use the .claude/agents/comprehensive-security-agent.md agent to provide guidance for secure hash algorithm implementation
// [implement code with guidance]
use the .claude/agents/comprehensive-security-agent.md agent to validate the implemented MD5 to SHA-256 fix
```

### Security Change Process
1. **RESEARCH** security guidance using semantic-search agent on research corpus
2. **IDENTIFY** the security domain(s) affected by your change
3. **GET GUIDANCE** from specialist agent(s) for implementation patterns and security rules (**IN PARALLEL** for multiple domains)
4. **IMPLEMENT** code following research findings, agent guidance, and loaded security rules
5. **VALIDATE** implementation with specialist agent(s) to verify rule compliance and detect issues
6. **TEST** with security tests and validation scripts
7. **DOCUMENT** security decisions and compliance

### Parallel Agent Execution - PERFORMANCE CRITICAL
**ALWAYS use parallel execution for multiple security agents:**

✅ **EFFICIENT (3 minutes):**
```javascript
// Single message with multiple tool calls - agents run in parallel
use the .claude/agents/input-validation-specialist.md agent to check injection risks
use the .claude/agents/secrets-specialist.md agent to scan credential handling
use the .claude/agents/configuration-specialist.md agent to validate security settings
```

❌ **INEFFICIENT (7+ minutes):**
```javascript  
// Separate messages - agents run sequentially
use the .claude/agents/input-validation-specialist.md agent to check injection risks
// Wait for completion, then:
use the .claude/agents/secrets-specialist.md agent to scan credential handling  
// Wait for completion, then:
use the .claude/agents/configuration-specialist.md agent to validate security settings
```

**Performance Impact:** Parallel execution can save 50-70% of analysis time

**For this repository:** Use **Multiple Specialists (Parallel)** - security-critical codebase justifies maximum detection capability

### Security Red Flags - Immediate Agent Required
🚨 **Cryptographic algorithms** (MD5, SHA1, weak ciphers)
🚨 **SQL queries or database operations** 
🚨 **User input processing**
🚨 **File system operations**
🚨 **Network requests/HTTP clients**
🚨 **Authentication/session logic**
🚨 **Environment variable handling**
🚨 **Error messages with sensitive data**

### Available Security Agents
- `semantic-search` - Research security guidance from OWASP/ASVS corpus
- `authentication-specialist` - Login, MFA, password policies (45+ rules)
- `authorization-specialist` - RBAC, permissions, access control (13+ rules)
- `input-validation-specialist` - Injection prevention (6+ rules)  
- `session-management-specialist` - Session security (22+ rules)
- `secrets-specialist` - Credential management (8+ rules)
- `logging-specialist` - Security logging (15+ rules)
- `configuration-specialist` - Secure defaults (16+ rules)
- `data-protection-specialist` - Privacy, encryption (14+ rules)
- `web-security-specialist` - XSS, CSRF prevention (varies)
- `comprehensive-security-agent` - Multi-domain analysis (191+ rules)

### Example Security-First Workflow
```
User: "Fix MD5 cryptographic vulnerability in rule_id_cleaner.py"

✅ CORRECT Process (RESEARCH-FIRST):
1. Research security guidance:
   use the .claude/agents/semantic-search.md agent to find best practices for cryptographic hash algorithms
2. Call security validation agent:
   use the .claude/agents/comprehensive-security-agent.md agent to validate the MD5 to SHA-256 fix
3. Implement fixes following research findings and agent recommendations
4. Create security tests validating the implementation
5. Run validation scripts and document compliance

❌ WRONG Process (NO RESEARCH):
1. Call agents without research context
2. Risk implementing solutions that miss latest security guidance
3. May not align with OWASP/ASVS best practices in corpus

❌ WORST Process:
1. Direct implementation without research or agent consultation
2. Risk missing security vulnerabilities and established best practices
```

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

### Security Red Flags - NEVER DO THESE
🚨 **Implementing security changes without calling specialist agents**
🚨 **Using deprecated cryptographic algorithms (MD5, SHA1, DES)**
🚨 **Hardcoding secrets, API keys, or credentials**
🚨 **Processing user input without validation/sanitization**
🚨 **Ignoring security test failures or warnings**
🚨 **Implementing authentication/authorization without expert review**
🚨 **Copying security code from untrusted sources**
🚨 **Disabling security features for "convenience"**

## Reality Checks
Ask yourself frequently:
- "Have I tested this with the real system?"
- "Am I building what's needed or what I think is cool?"
- "Does this actually integrate with existing code?"
- "Am I hiding problems with elaborate abstractions?"
- "Would a simpler solution work just as well?"
- "Did I write the test first and see it fail?"

### Security Reality Checks
Ask for EVERY security-related change:
- "Did I call the appropriate security specialist agent BEFORE coding?"
- "Am I following loaded security rules and best practices?"
- "Does this change affect authentication, authorization, or cryptography?"
- "Have I created security tests to validate the implementation?"
- "Could this introduce injection, XSS, or other vulnerabilities?"
- "Are secrets and credentials properly protected?"
- "Does this meet compliance requirements (OWASP, ASVS, CWE)?"

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

This is the **GenAI Security Agents** repository, a comprehensive Policy-as-Code system that creates security knowledge from standards and delivers it through Claude Code CLI integration. The repository contains defensive security tools, specialized security agents, and agent frameworks for cybersecurity professionals.

### Key Components

1. **Security Agent Framework** (`app/`) - Core security rule cards and agent compilation system
2. **Claude Code Integration** (`.claude/`) - Specialized security agents for real-time analysis
3. **Semantic Search Corpus** (`research/search_corpus/`) - OWASP and ASVS knowledge base
4. **Documentation** (`docs/`) - GenAI security research, implementation guides, and validation reports
5. **Security Tools** (`tools/`) - Agent compilation, semantic search, and validation utilities

## Project Structure

```
genai-sec-agents/
├── app/                          # Core security framework
│   ├── rule_cards/              # 197 YAML security rule cards across 20 domains
│   ├── tools/                   # Agent compilation and validation toolchain
│   ├── security/                # Security validation and input sanitization
│   └── ingestion/               # OWASP and ASVS content processing
├── .claude/                      # Claude Code integration
│   ├── agents/                  # Specialized security agent definitions
│   └── README.md                # Agent usage patterns and capabilities
├── research/search_corpus/       # Semantic search knowledge base
│   ├── owasp/                   # 102 OWASP CheatSheets (processed)
│   └── asvs/                    # 17 ASVS standards (processed)
├── docs/                         # Implementation documentation
│   ├── stories/                 # User story definitions and tracking
│   └── plans/                   # Technical implementation specifications
└── tools/                        # Processing and search utilities
    ├── semsearch.sh             # Semantic search wrapper with security controls
    └── render_owasp_for_search.py # Content processing for search corpus
```



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
