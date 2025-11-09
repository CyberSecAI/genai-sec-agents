# **ADR: Hooks for Automatic Skill Loading — Rejected**

## **Summary**

We evaluated whether to use **Claude Code hooks** (specifically `user-prompt-submit` hooks) to automatically detect security-related prompts and inject skill context before processing.

**Decision: Do not use hooks.** We will **keep the existing CLAUDE.md-based workflow** and **not** introduce external hook-based skill loading.

The A8-NO-CLAUDE isolation experiment proved that **CLAUDE.md is the active orchestrator** that drives the security-first workflow, while **skills are passive knowledge repositories**. This is the correct architecture.

## **Issue**

During Phase 0 validation testing, we observed varied skill activation patterns WITH CLAUDE.md enabled:
* Manual skill invocation (2/7 tests): `/authentication-security` slash command
* Agent workflow (2/7 tests): Single specialist agent called
* Dual-agent workflow (1/7 tests): semantic-search + specialist in parallel
* Quad-agent workflow (1/7 tests): semantic-search + 3 specialists in parallel
* No activation (1/7 tests): False negative despite authentication keywords

When we tested the same OAuth2 prompt (A8) WITHOUT CLAUDE.md, we observed:
* **WITH CLAUDE.md**: 4 agents in parallel, pre-implementation research, security-first framing
* **WITHOUT CLAUDE.md**: Zero agent activation, direct implementation, no security workflow

The question arose: "How do we ensure skills are loaded for security tasks?" with a proposed solution being hooks.

One proposed solution was to implement a `user-prompt-submit` hook that:
* Pattern-matches the user prompt for security keywords
* Automatically injects skill file content (SKILL.md, rules.json)
* Forces skill context to be available before Claude processes the request

## **Decision**

**Reject hooks approach.** Continue using **CLAUDE.md** as the skill orchestration mechanism.

CLAUDE.md already implements pattern-based triggers (lines 232-245) and workflow orchestration (lines 201-359). External hooks would duplicate this functionality while introducing complexity and fragility.

## **Status**

**Rejected** (2025-11-09). Will not implement hook-based skill loading.

## **Details**

### **Assumptions**

* Claude Code sessions have access to CLAUDE.md (both project-level and global `~/.claude/CLAUDE.md`)
* The security-first workflow requires active orchestration, not just passive context availability
* Skills contain ASVS knowledge but don't prescribe when/how to use it
* CLAUDE.md serves as the "workflow engine" that activates and orchestrates skills

### **Constraints**

* Hooks execute as external shell commands and return text injected into the conversation
* Hooks cannot force Claude to read specific files or follow specific workflows
* Hook output becomes part of the user message but doesn't guarantee behavioral changes
* Hook-based solutions add operational complexity (debugging, maintenance, portability)

### **Options Considered**

1. **Status quo (CLAUDE.md orchestration)** — **Chosen**

   * *Pros:* Already working; proven by A8 test; integrated workflow; no external dependencies
   * *Cons:* Requires CLAUDE.md to be present; won't work if user disables it

2. **Pattern-matching hook to inject skill context** — **Rejected**

   * *Pros:* Could make skills "always available" even without CLAUDE.md
   * *Cons:* Passive context injection doesn't guarantee workflow adherence; adds complexity; duplicates CLAUDE.md patterns; external maintenance burden

3. **Smart Python hook with skill detection** — **Rejected**

   * *Pros:* More sophisticated pattern matching; could load multiple skills
   * *Cons:* Still passive injection; requires Python environment; fragile; doesn't solve workflow problem

4. **Modify Claude Code to auto-invoke Skill tool** — **Out of scope**

   * *Pros:* True auto-activation at platform level
   * *Cons:* Requires Claude Code core changes; not under our control

### **Trade-offs (Hooks vs CLAUDE.md)**

| Aspect | CLAUDE.md Orchestration | Hook-Based Injection |
|--------|------------------------|---------------------|
| **Workflow enforcement** | ✅ Active (prescribes WHEN and HOW) | ❌ Passive (injects WHAT) |
| **Multi-agent orchestration** | ✅ Yes (parallel specialists) | ❌ No (just context) |
| **Pre-implementation timing** | ✅ Yes (STEP 1-2 before STEP 3) | ❌ No (no workflow control) |
| **Security-first framing** | ✅ Yes (explicit statements) | ❌ No (just knowledge) |
| **Pattern matching** | ✅ Built-in (lines 232-245) | ⚠️ Duplicate (external script) |
| **Maintenance** | ✅ Single file (CLAUDE.md) | ❌ Multiple files (hook script + config) |
| **Debugging** | ✅ Transparent (visible in CLAUDE.md) | ❌ Opaque (external process) |
| **Portability** | ✅ Works everywhere | ⚠️ Requires hook support |
| **Proven effectiveness** | ✅ Yes (A8 test) | ❌ No (A8-NO-CLAUDE failed) |

### **Evidence from A8-NO-CLAUDE Test**

**Controlled experiment** (2025-11-09) compared A8 WITH vs WITHOUT CLAUDE.md.

**Note**: This is the first (1/5) isolation test completed. Additional tests (A5, A2, A7, A4 WITHOUT CLAUDE.md) are planned to verify the pattern holds across different task types (query, guidance, review, file-specific). However, this single test provides strong evidence for the architectural decision.

**WITH CLAUDE.md** (A8 baseline):
```
00:33:48 - Explicit "Follow SECURITY-FIRST DEVELOPMENT WORKFLOW" statement
00:33:48 - Called semantic-search agent (corpus research)
00:33:48 - Called authentication-specialist agent
00:33:48 - Called session-management-specialist agent
00:33:48 - Called secrets-specialist agent
Result: Comprehensive guidance (25/25 quality), NO implementation
```

**WITHOUT CLAUDE.md** (A8-NO-CLAUDE):
```
10:06:28 - Create TodoWrite task list
10:06:28 - Edit secure_login.py (IMPLEMENT immediately)
10:06:46 - Edit secure_login.py again
10:07:10 - Edit secure_login.py again
10:07:43 - Edit secure_login.py again
10:08:36 - Edit secure_login.py again
10:09:14 - Edit secure_login.py again
Result: 6 consecutive edits, ZERO agents called, NO research
```

**CLAUDE.md contribution**: ~100% of security-first workflow behavior

**Conclusion**: Even if a hook had injected skill context, it would NOT have changed the behavior observed in A8-NO-CLAUDE. The problem is lack of workflow orchestration, not lack of available knowledge.

### **Why Hooks Won't Solve the Problem**

1. **Passive vs Active**: Hooks inject text (passive context) but CLAUDE.md prescribes workflow (active orchestration)

2. **Timing enforcement**: CLAUDE.md enforces "Research BEFORE implementation" (STEP 1-2 before STEP 3). Hooks can't enforce timing.

3. **Multi-agent orchestration**: CLAUDE.md orchestrates parallel specialist calls. Hooks can't orchestrate agents.

4. **Domain identification**: CLAUDE.md identifies OAuth2 → auth + session + secrets (4 agents). Hooks just dump skill content.

5. **Security-first framing**: CLAUDE.md provides explicit workflow statements. Hooks provide silent context.

6. **A8-NO-CLAUDE proves**: Without CLAUDE.md workflow, Claude goes straight to implementation regardless of available context.

### **CLAUDE.md IS the Hook System**

CLAUDE.md already implements pattern-based triggers:

```python
# Auto-Trigger Security Agents Based on Code Patterns (lines 232-245)

# Authentication/Authorization
password|login|authenticate|session → authentication-specialist
authorize|permission|role|access → authorization-specialist
token|jwt|bearer|oauth → session-management-specialist

# Input/Output processing
request.form|request.args|request.json → input-validation-specialist
input()|sys.argv|click.argument → input-validation-specialist
subprocess.|os.system|os.popen → input-validation-specialist

# Cryptographic operations
hashlib.md5|.sha1|.des → comprehensive-security-agent
```

These patterns ARE the hook system, integrated into CLAUDE.md's workflow engine.

**External hooks would duplicate this** while losing:
- Workflow context (STEP 1-4 sequence)
- Multi-agent orchestration instructions
- Security-first framing
- Pre-implementation enforcement

### **The Correct Architecture**

The A8-NO-CLAUDE test validates the **two-component architecture**:

1. **Skills** = Passive knowledge repositories
   - ✅ Contain ASVS rules (rules.json)
   - ✅ Provide security patterns (SKILL.md)
   - ✅ Generate slash commands (/authentication-security)
   - ❌ Don't prescribe when to activate
   - ❌ Don't orchestrate multi-agent workflows

2. **CLAUDE.md** = Active workflow engine
   - ✅ Prescribes when to load knowledge (STEP 1-2 BEFORE STEP 3)
   - ✅ Orchestrates multiple agents in parallel
   - ✅ Provides security-first framing
   - ✅ Identifies security domains via pattern matching
   - ✅ Enforces pre-implementation research

3. **Agents** = Delivery mechanism
   - ✅ semantic-search (corpus research)
   - ✅ Specialist agents (authentication, session, secrets, etc.)

**All three components are ESSENTIAL**. Remove any one → system breaks.

### **Known Issues to Fix (NOT via hooks)**

Instead of adding hooks, we should fix the actual workflow issues:

1. **A7 False Negative** (14.3% false negative rate):
   - Problem: Review task without "security" keyword didn't activate
   - Solution: Improve semantic matching in CLAUDE.md patterns
   - NOT a hooks problem (hooks would have same matching issue)

2. **A4 Timing Issue** (post-implementation validation):
   - Problem: File-specific directives bypass STEP 1-2 workflow
   - Solution: Update CLAUDE.md to block file-specific implementations
   - NOT a hooks problem (hooks can't enforce timing)

3. **Skill Description Updates**:
   - Improve trigger keywords in skill descriptions
   - Add "review" patterns to catch code review tasks
   - Refine semantic matching thresholds

## **Implications**

* **Now**: No changes needed; continue using CLAUDE.md orchestration
* **Phase 0**: Validate Skills + CLAUDE.md as combined architecture (not skills alone)
* **Phase 1**: Address A7/A4 issues by improving CLAUDE.md patterns and workflow
* **Documentation**: Update validation docs to clarify two-component architecture

## **Related**

* [TEST_RESULT_A8_NO_CLAUDE.md](TEST_RESULT_A8_NO_CLAUDE.md) - Isolation experiment proving CLAUDE.md is critical
* [FINDING_CLAUDE_MD_ATTRIBUTION.md](FINDING_CLAUDE_MD_ATTRIBUTION.md) - Complete analysis of CLAUDE.md contribution
* [VALIDATION_LOG.md](VALIDATION_LOG.md) - Phase 0 validation tracking
* CLAUDE.md lines 201-359 (SECURITY-FIRST DEVELOPMENT WORKFLOW)
* CLAUDE.md lines 232-245 (Auto-Trigger Security Agents Based on Code Patterns)

## **Appendix: What We Already Have (Without Hooks)**

**Current CLAUDE.md capabilities** that make hooks unnecessary:

1. **Pattern-based triggers** (lines 232-245):
   - Authentication: `password|login|authenticate|session|oauth|jwt`
   - Input validation: `request.form|input()|subprocess.`
   - Cryptography: `hashlib.md5|ssl.|certificate`
   - Secrets: `api_key|secret|credential|getenv`

2. **Workflow enforcement** (lines 321-339):
   - STEP 1: Research security guidance BEFORE implementing
   - STEP 2: Get implementation guidance (BEFORE coding)
   - STEP 3: Implement code with loaded context
   - STEP 4: Validate implementation (AFTER coding)

3. **Multi-agent orchestration** (lines 350-358):
   - Parallel execution for multiple domains
   - Performance-critical parallel agent calls
   - Domain-specific specialist routing

4. **Security-first framing** (line 201 section header):
   - Explicit workflow name: "SECURITY-FIRST DEVELOPMENT WORKFLOW"
   - Automatic security mindset activation
   - Clear process expectations

**All of this would need to be duplicated in hook scripts**, while losing:
- Integration with workflow context
- Visibility and transparency
- Single-source maintenance
- Natural language flexibility

## **Revisit Triggers**

Reopen this ADR if **ALL** of the following occur:

* **CLAUDE.md cannot be loaded** in Claude Code sessions (platform limitation)
* **Skills must work independently** of CLAUDE.md (hard requirement)
* **External workflow engine** is infeasible (can't modify CLAUDE.md)

**Current state**: None of these triggers are active. CLAUDE.md is available and working.

## **Alternative Considered: Skill Auto-Activation in Claude Code Core**

If Anthropic adds native skill auto-activation to Claude Code (similar to how GPTs work in ChatGPT), that would be the correct solution:

**Hypothetical feature**: Claude Code semantically matches user prompts to skill descriptions and auto-invokes the Skill tool before processing.

**This would**:
- ✅ Provide true auto-activation (not passive injection)
- ✅ Work without CLAUDE.md
- ✅ Maintain workflow control (platform-level)

**But this is**:
- ❌ Outside our control (requires Anthropic engineering)
- ❌ Not available currently
- ❌ Still wouldn't replace CLAUDE.md workflow orchestration entirely

**Therefore**: Even if this existed, CLAUDE.md would still provide value for:
- Multi-agent orchestration (multiple specialists in parallel)
- Pre-implementation timing (STEP 1-2 before STEP 3)
- Security-first framing (explicit workflow statements)
- Domain identification (OAuth → auth + session + secrets)

## **Conclusion**

**Hooks are the wrong tool for the job.**

The problem is not "How do we make skills available?" (passive context).
The problem is "How do we orchestrate security-first workflow?" (active process).

**CLAUDE.md solves this.** Hooks cannot.

**Evidence**: The A8-NO-CLAUDE isolation experiment (1 of 5 planned tests) demonstrates that CLAUDE.md is ~100% responsible for the security-first workflow in that specific case. While additional testing is planned to verify this pattern across different task types, this single test provides sufficient evidence for the architectural decision: hooks inject passive context, while CLAUDE.md provides active workflow orchestration.

**Decision**: Skills + CLAUDE.md is the validated architecture. No hooks needed.
