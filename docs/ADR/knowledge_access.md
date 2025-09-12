# ADR: Knowledge Access Strategy (No Vector DB, Medium Agents + Local Semantic Search)

<!-- cSpell:words genai ASVS semtools semsearch -->

## Status

**Implemented and Operational**
- Initial Decision: Accepted 2025-08-30
- Implementation Status: Complete as of 2025-09-12

## Context

We need a way for our GenAI Security Agents to access OWASP-aligned guidance (Cheat Sheets, ASVS, LLM Top 10, NIST SSDF) in order to provide:

* **Pre-guidance** during code generation.
* **Post-validation** through scanner integration.

Key priorities include:

* **Minimal latency** at runtime so agents remain fast and cheap.
* **Ease of updating the knowledge base** so guidance changes can be applied quickly without heavy rebuilds or infra overhead.

Several approaches were considered:

1. **Vector database (RAG)**

   * Store rule cards and docs in a vector DB.
   * Agents query semantically at runtime for relevant chunks.
   * Pros: flexible, supports long-tail queries.
   * Cons: operational overhead (infrastructure, costs, persistence), determinism issues, increased latency, larger attack surface.

2. **Compiled sub-agents with embedded guidance**

   * Agents include a curated set of rules directly in their definition (no runtime retrieval).
   * Pros: deterministic, very small prompts, easy to test, minimal latency.
   * Cons: requires rebuilds to update guidance, risk of stale content, less coverage for niche topics.

3. **Hybrid approach: compiled sub-agents + lightweight local semantic search**

   * Use **medium-granularity sub-agents** (topic+language, \~6–12 rules each).
   * Agents load essential, compiled rules by default.
   * Optionally, a local semantic search tool ([semtools](https://github.com/run-llama/semtools)) can provide *extra snippets* from the rule card corpus.
   * Pros: freshness and explainability without external infra; low latency compared to vector DBs; simple updates (re-run corpus render).
   * Cons: introduces some non-determinism, modest extra complexity.

## Decision

We will **not use a vector database**.
Instead, we will adopt **medium-granularity sub-agents with compiled rule cards** as the authoritative baseline.

* **Routing**: rely on the router to select the correct sub-agents based on files/stack.
* **Compiled rules**: each agent includes its critical 6–12 rules, ensuring determinism, minimal latency, and CI enforceability.
* **Semantic search (semtools)**: kept as a **developer tool and governance aid by default** (local queries, PR explainability, diffing).
* **Runtime retrieval**: behind a **feature flag**. Off in normal runs; may be enabled for explain mode, developer assistance, or as a bridge immediately after rule updates before recompilation.
* **Ease of update**: rule cards remain the single source of truth; updating knowledge is as simple as editing YAML and recompiling.

## Consequences

* **Pros**

  * Deterministic core behavior (compiled rules).
  * Minimal latency and low token usage.
  * Router + medium agents cover most cases without retrieval.
  * Semtools still provides developer search and explainability benefits.
  * Freshness gap between rule merge and compile can be bridged by optional runtime retrieval.
  * Updating knowledge is lightweight (edit YAML, recompile agents, re-render corpus).

* **Cons**

  * Maintaining a searchable corpus adds some overhead.
  * Runtime retrieval, if enabled, reduces determinism and requires provenance logging.
  * Agents won’t cover *all* edge cases unless rules are curated or snippets retrieved.

* **Future flexibility**

  * If scaling demands increase, we can later swap semtools for a lightweight vector store without rewriting sub-agents.
  * Rule card corpus remains the single source of truth.

## Implementation Status (2025-09-12)

The ADR has been **fully implemented and is operational** with the following components:

### ✅ Completed Components

1. **Compiled Sub-Agents (15+ specialized agents)**
   - `app/dist/agents/` contains compiled JSON agents with embedded rule cards
   - Each agent contains 6-12 curated security rules for deterministic behavior
   - Examples: `authentication-specialist.json`, `secrets-specialist.json`, `comprehensive-security-agent.json`

2. **Rule Card System (50+ rules across 5 domains)**
   - YAML source files in `app/rule_cards/` (secrets, cookies, jwt, genai, docker)
   - Compilation toolchain: `app/tools/compile_agents.py` + `app/tools/agents_manifest.yml`
   - Automated validation and JSON generation workflow

3. **Local Semantic Search Corpus (219+ documents)**
   - `research/search_corpus/` with OWASP CheatSheets + ASVS standards
   - 219 processed security documents for semantic search
   - semtools integration for lightweight, on-the-fly semantic search

4. **Claude Code Integration (22+ agent configurations)**
   - `.claude/agents/` contains 22+ agent configuration files
   - Real-time security guidance during development workflow
   - Automatic agent routing based on security domain detection

5. **Developer Toolchain**
   - `Makefile` with `semsearch`, `compile`, `validate` commands
   - `tools/semsearch.sh` script for corpus querying
   - Automated build and validation workflows

### Architecture Validation

The implemented system **exactly matches ADR decisions**:

- ✅ **No vector database** - Uses semtools for direct file search with on-the-fly embeddings
- ✅ **Medium-granularity sub-agents** - 15+ specialized agents with 6-12 rules each
- ✅ **Compiled rule cards** - JSON packages with embedded rules for determinism
- ✅ **Local semantic search** - 219-document corpus with semtools integration
- ✅ **Minimal latency** - Compiled rules avoid runtime retrieval overhead
- ✅ **Easy updates** - YAML editing + recompilation workflow
- ✅ **Developer tooling** - Claude Code CLI integration with real-time guidance

### Performance Characteristics

- **Agent Loading**: Instant (pre-compiled JSON packages)
- **Rule Retrieval**: Zero latency (embedded in agent definitions)
- **Semantic Search**: Fast file-based search with Rust semtools engine
- **Knowledge Updates**: Simple YAML editing + `make compile` workflow
- **CI Integration**: Automated validation and compilation in build pipeline

### Operational Benefits Realized

1. **Deterministic Core Behavior**: Compiled rules ensure consistent security guidance
2. **Minimal Infrastructure**: No database setup, hosting, or persistence required
3. **Developer-Friendly**: Real-time IDE integration through Claude Code CLI
4. **Maintainable**: Single source of truth in YAML rule cards
5. **Scalable**: Easy to add new domains and rules without architectural changes

The system is production-ready and successfully providing real-time security guidance to developers through the Claude Code CLI integration.
