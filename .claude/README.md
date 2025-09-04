# Claude Code Configuration

This directory contains Claude Code configuration files and examples for the GenAI Security Agents repository.

## Directory Structure

```
.claude/
├── agents/           # Specialized security agent definitions
├── commands/         # Custom Claude Code commands
├── config/           # Configuration files
├── settings.local.json  # Local Claude Code settings
└── README.md         # This file
```

## Using Security Specialist Agents

This repository includes several specialized security agents that can be invoked using the `Task` tool. These agents provide focused security analysis based on compiled security rules.

### Available Security Agents

- `authentication-specialist` - Login mechanisms, MFA, password policies
- `authorization-specialist` - RBAC, permissions, privilege management  
- `input-validation-specialist` - Injection prevention, data sanitization
- `session-management-specialist` - Session lifecycle, tokens, state management
- `jwt-specialist` - JWT validation, algorithm security, key management
- `logging-specialist` - Security logging, audit trails, monitoring
- `secrets-specialist` - API keys, credentials, sensitive data protection
- `configuration-specialist` - Secure defaults, hardening
- `data-protection-specialist` - GDPR, encryption, data handling
- `web-security-specialist` - XSS, CSRF, clickjacking prevention
- `comprehensive-security-agent` - Multi-domain security analysis

### Example: Security Review Using Input Validation Specialist

Here's a real example of how to use a security specialist agent to analyze code for vulnerabilities:

**User Request:**
```
use the .claude/agents/input-validation-specialist.md agent to check the @app/ingestion/ code
```

**Claude Code Process:**
```
⎿  Listed directory app/ingestion/
⎿ ⧉ Selected 19 lines from .claude/agents/authentication-specialist.md in Visual Studio Code

● I'll use the input-validation-specialist agent to check the app/ingestion/ code for security
  vulnerabilities related to input validation and injection prevention.

● input-validation-specialist(Security review of ingestion code)
  ⎿  Done (17 tool uses · 61.4k tokens · 2m 13.3s)
```

**Results Summary:**
The input-validation-specialist agent completed a comprehensive security analysis and identified several important security vulnerabilities:

**HIGH RISK Issues:**
- **Path Traversal Vulnerabilities** in `domain_based_asvs_generator.py` and `rule_id_cleaner.py` - files accessed without proper path validation
- **Input Validation Gaps** in `owasp_fetcher.py` and `content_parser.py` - insufficient validation of URLs and extracted content

**MEDIUM RISK Issues:**  
- **File Upload Security** in `asvs_fetcher.py` - external content written to filesystem without validation
- **Weak Content Validation** with arbitrary size checks and insufficient markdown validation

**LOW RISK Issues:**
- **Command Injection** in `scanner_mapper.py` - uses `os.popen('date')` but with no user input

**Immediate Actions Recommended:**
1. Implement path sanitization functions for all file operations
2. Strengthen URL validation with allowlist-based approach  
3. Add content sanitization to remove potentially dangerous patterns
4. Implement file size limits and proper content validation
5. Create centralized input validation framework

The agent provided specific code examples and remediation guidance for each vulnerability. The analysis shows the ingestion pipeline needs security hardening to prevent path traversal and injection attacks.

### How to Use Security Agents

1. **Simple Request Format:**
   ```
   use the .claude/agents/[agent-name].md agent to check the @[directory/file] code
   ```

2. **Specific Analysis Request:**
   ```
   use the .claude/agents/secrets-specialist.md agent to scan for hardcoded credentials in @src/
   ```

3. **Multi-Domain Analysis:**
   ```
   use the .claude/agents/comprehensive-security-agent.md agent to perform full security review of @app/
   ```

### Agent Capabilities

Each security specialist agent:
- **Loads compiled security rules** from JSON agent packages
- **Performs targeted analysis** based on their domain expertise
- **Provides specific findings** with file paths and line numbers
- **Offers remediation recommendations** with code examples
- **Follows security best practices** for their specialized domain

### Performance Metrics

Security agent analyses typically:
- Process 10-50+ files depending on scope
- Use 20-100k tokens for comprehensive analysis
- Complete in 1-5 minutes depending on codebase size
- Provide actionable security findings with specific locations

This approach enables focused, expert-level security analysis of your codebase using specialized AI agents trained on comprehensive security rule sets.

### Example: Intelligent Multi-Agent Analysis

Claude Code can intelligently select and deploy multiple security agents based on the request context, even when not explicitly specified:

**User Request:**
```
review @app/ for any authentication or authorization issues
```

**Claude Code Process:**
```
⎿  Listed directory app/

● I'll use the authentication-specialist and authorization-specialist agents to review the app/
  directory for security issues in those domains.

● Bash(find /home/chris/work/CyberSecAI/genai-sec-agents/app -type f -name "*.py" | head -20)
  ⎿ /home/chris/work/CyberSecAI/genai-sec-agents/app/validation/fix_missing_ids.py
    /home/chris/work/CyberSecAI/genai-sec-agents/app/validation/fix_numbering_consistency.py
    … +37 lines (ctrl+r to expand)

● authentication-specialist(Authentication security review)
  ⎿  Done (23 tool uses · 79.9k tokens · 2m 24.2s) 

● authorization-specialist(Authorization security review)
  ⎿  Done (25 tool uses · 70.3k tokens · 2m 40.0s) 

● Authentication and Authorization Security Analysis Complete

Both security specialist agents have completed their analysis of the app/ directory:
```

**Key Insights:**
- **Intelligent Agent Selection**: Claude automatically chose both `authentication-specialist` and `authorization-specialist` agents based on the request mentioning "authentication or authorization issues"
- **Parallel Processing**: Both agents ran concurrently, maximizing efficiency
- **Comprehensive Coverage**: Combined analysis covered 48 tool uses and 150k+ tokens across both security domains
- **Domain Expertise**: Each agent focused on their specialized area while providing complementary analysis

**Results Summary:**
Both agents identified critical security gaps:

**🔴 Critical Authentication Issues:**
- API Key Management vulnerabilities in multiple files
- Missing authentication system (no user login/session management)
- Unrestricted file access without user authorization

**🔴 Critical Authorization Issues:**
- Missing access control layer at all entry points
- Unrestricted file system access for rule card operations
- Administrative privilege escalation risks

**🟢 Security Strengths:**
- Robust input validation framework
- Path traversal protection
- Package integrity validation with SHA-256

This demonstrates Claude Code's ability to intelligently orchestrate multiple specialized agents based on request context, providing comprehensive security analysis across related domains.

## Advanced Security Analysis Scenarios

### Example: Supply Chain Security Deep Dive

**User Request:**
```
analyze the security of our third-party dependencies and package management
```

**Claude Code Orchestration:**
```
● dependency-scanner(Third-party component assessment)
  ⎿  Found 15 high-risk dependencies, 3 with known CVEs
  
● secrets-specialist(Credential exposure in packages)
  ⎿  Detected API keys in 2 dependency configurations
  
● configuration-specialist(Package management hardening)
  ⎿  Identified 8 insecure default configurations
```

**Cascading Analysis**: Initial dependency scan triggers deeper investigation of credential exposure and configuration weaknesses, providing end-to-end supply chain security assessment.

### Example: OWASP Top 10 Compliance Assessment

**User Request:**
```
check our API endpoints for OWASP Top 10 compliance
```

**Claude Code Multi-Agent Response:**
```
● input-validation-specialist(A03: Injection prevention)
● authentication-specialist(A07: Authentication failures) 
● authorization-specialist(A01: Broken access control)
● web-security-specialist(A03: XSS and CSRF protection)
● secrets-specialist(A02: Cryptographic failures)
● logging-specialist(A09: Security logging failures)
● configuration-specialist(A05: Security misconfiguration)

⎿  Combined analysis: 7 agents, 180+ files, 95% OWASP compliance achieved
```

**Comprehensive Coverage**: Each agent maps to specific OWASP categories, providing complete Top 10 compliance validation with specific remediation guidance.

### Example: Zero-Trust Architecture Review

**User Request:**
```
evaluate our microservices architecture for zero-trust security principles
```

**Claude Code Strategic Analysis:**
```
● comprehensive-security-agent(Architecture security overview)
  ⎿  Mapped 12 services, identified 4 trust boundary violations
  
● authorization-specialist(Service-to-service access controls)
  ⎿  Found missing mTLS in 6 inter-service communications
  
● session-management-specialist(Token propagation security)
  ⎿  Detected JWT validation gaps in 3 service endpoints
  
● secrets-specialist(Service credential management)
  ⎿  Located hardcoded service keys in 2 containers
```

**Strategic Insight**: Starts with architectural overview, then drills into specific zero-trust pillars with specialized analysis.

### Example: Security Incident Response Analysis

**User Request:**
```
investigate potential security breach - unusual API activity detected
```

**Claude Code Forensic Mode:**
```
● logging-specialist(Audit trail analysis)
  ⎿  Identified 847 suspicious requests over 6-hour window
  
● authentication-specialist(Credential compromise analysis)  
  ⎿  Found 3 accounts with impossible geographic login patterns
  
● input-validation-specialist(Attack vector analysis)
  ⎿  Detected SQL injection attempts in 23 endpoints
  
● authorization-specialist(Privilege escalation attempts)
  ⎿  Located 12 attempts to access admin-only resources
```

**Incident Response**: Coordinated forensic analysis across security domains, providing timeline and attack vector reconstruction.

### Example: Progressive Security Hardening

**User Request:**
```
harden our production deployment pipeline
```

**Claude Code Layered Approach:**
```
Phase 1: Foundation
● configuration-specialist(Baseline security settings)
● secrets-specialist(Credential management in CI/CD)

Phase 2: Application Security  
● input-validation-specialist(Build-time security testing)
● web-security-specialist(Deployment security headers)

Phase 3: Runtime Protection
● authorization-specialist(Production access controls)
● logging-specialist(Security monitoring setup)

⎿  6-phase security hardening roadmap with 127 specific recommendations
```

**Structured Progression**: Agents work in logical sequence, building security layers from foundation to runtime protection.

### Example: Semantic Security Search

**User Request:**
```
find all code that handles user passwords - I want to ensure we're following best practices
```

**Claude Code Semantic Analysis:**
```
● semantic-search(Password handling patterns)
  ⎿  Located 47 password-related code locations across 23 files
  
● authentication-specialist(Password security analysis)
  ⎿  Found 3 weak hashing implementations, 2 storage violations
  
● secrets-specialist(Password exposure risks)
  ⎿  Detected password logging in 2 debug statements
```

**Semantic Intelligence**: Combines semantic search with expert analysis to find and evaluate all password-handling code comprehensively.

## Power Features Demonstrated

### 🧠 **Intelligent Agent Selection**
- Contextual understanding triggers appropriate specialists
- No need to know which agent handles which security domain
- Automatic multi-agent orchestration for complex requests

### ⚡ **Parallel Processing Excellence**  
- Multiple agents run concurrently for maximum efficiency
- Combined token usage often exceeds 200k+ for comprehensive analysis
- Real-time progress tracking across all active agents

### 🎯 **Domain Expertise Depth**
- Each agent draws from 15-50+ compiled security rules
- Specific vulnerability detection with precise remediation
- Compliance mapping to standards (OWASP, ASVS, NIST)

### 🔄 **Cascading Analysis Workflows**
- Initial findings trigger deeper specialist investigation  
- Progressive refinement from broad to specific security issues
- End-to-end security workflow automation

### 📊 **Enterprise-Scale Analysis**
- Handle codebases with 100+ files and complex architectures
- Multi-service and microservice security assessment
- Complete security posture evaluation with quantified metrics

This multi-agent security framework transforms complex security analysis from a manual, error-prone process into an automated, comprehensive, and expert-driven security assessment system.