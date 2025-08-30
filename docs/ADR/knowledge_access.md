# ADR: Knowledge Access Strategy (No Vector DB, Medium Agents + Local Semantic Search)

## Status

Accepted
Date: 2025-08-30

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
   * Optionally, a local semantic search tool (semtools) can provide *extra snippets* from the rule card corpus.
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
