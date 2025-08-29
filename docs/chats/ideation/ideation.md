

I want to create a set of GenAI software security agents based on existing guidance.

I think this existing guidance is suitable for this use: https://cheatsheetseries.owasp.org/cheatsheets/ 
e.g. https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html
e.g. https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html

I think we should use claude code, and create a sub-agent for each of these cheatsheets / topics (which gets called automatically whenever the relevant topic is being worked on).

The cheatsheets should be in a form suitable for this purpose.

This is guidance at the time of creation of the software for use by the LLM.
There should also be a tool or scanner that performs checks on the created software when it is created.
In this way, we have pre guidance and post validation.

Provide feedback on this - and suggest improvments.
Create a plan.
The plan should include doing Deep Research


-------------------------------

love the vision. short version: using OWASP Cheat Sheets as the “brains” for topic-specific sub-agents, then backing that up with automated scanners in CI, is absolutely workable—and smart. a few tweaks will make it more robust, up-to-date, and maintainable.

# feedback & suggested improvements

* **Make the knowledge source durable & licensed correctly.** The OWASP Cheat Sheet Series is CC BY-SA 4.0, which you *can* adapt for commercial use if you attribute and keep derivatives under a compatible license; plan for attribution + share-alike obligations in your repo/docs. ([GitHub][1], [OWASP][2])
* **Anchor everything to canonical standards.** Besides the Cheat Sheets, map guidance to **OWASP ASVS 5.0.0** controls so you get comprehensive coverage and traceability; ASVS 5.0.0 shipped in May 2025. ([GitHub][3], [OWASP][4])
* **Include GenAI-specific security guidance.** Pull in **OWASP Top 10 for LLM/GenAI (v1.1 + 2025 refresh)** for agentic risks like prompt injection & insecure output handling, and their new red-teaming guide. This ensures your agents advise safely when they (or developers) use LLMs. ([OWASP][5], [OWASP Gen AI Security Project][6])
* **Stay current—avoid stale sheets.** Some Cheat Sheets deprecate/move (e.g., Transport Layer Protection → TLS). Your ingestion should flag deprecated pages and replace them automatically. ([OWASP Cheat Sheet Series][7])
* **Model-agnostic orchestration.** Claude Code is great for coding tasks, but keep the system model-agnostic so you can use a *second* model for critique/self-review to reduce correlated errors (and swap models as they evolve).
* **Structure guidance for both generation and validation.** Normalize each cheat sheet into small, testable “rules” with: requirement → rationale → code templates (per language) → *detectable patterns* → *CI checks/tools* → references (ASVS/cheatsheet links).
* **Automate “post-validation” with proven OSS.** Pair sub-agents with scanners that embody the same rules:

  * **Code**: Semgrep (OWASP Top 10 rulesets + custom rules). ([Semgrep][8])
  * **Containers**: Hadolint (Dockerfile), Dockle (image lint), Trivy (vulns, IaC, SBOM scan). ([GitHub][9], [trivy.dev][10])
  * **IaC**: Checkov / tfsec / OPA Conftest for policy-as-code. ([checkov.io][11], [aquasecurity.github.io][12], [conftest.dev][13])
  * **Secrets**: Gitleaks / TruffleHog. ([GitHub][14])
  * **SBOM/SCA**: Syft for SBOM, scan via Trivy/Grype. ([GitHub][15], [trivy.dev][16])
  * **GenAI app testing**: garak for LLM vulnerability scanning (prompt injection, data leakage, etc.). ([GitHub][17])
* **Supply-chain attestations.** Emit in-toto/SLSA provenance from CI so each artifact is verifiably built & scanned (aim for SLSA v1 tracks over time). ([SLSA][18], [GitHub][19])

---

# proposed architecture (high-level)

**A. Knowledge layer (RAG-ready)**

* Ingest Cheat Sheets + ASVS + LLM Top 10 + SSDF v1.1 into a versioned corpus. Tag each chunk with topics (e.g., JWT, Docker, TLS), severity, ASVS IDs, and “verification hooks” (which scanner/rule checks it). ([OWASP][20], [NIST CSRC][21])
* Normalize to **Rule Cards** (YAML/JSON):
  `id, title, scope, requirement, do/don’t, defaults, exceptions, code-templates (lang), detection (semgrep rule ids / hadolint codes / checkov policy ids), quick-tests, references`.

**B. Orchestrator & sub-agents**

* **Router** classifies the developer task (files changed, stack, keywords) and dispatches to relevant sub-agents (e.g., Docker, JWT, AuthN/AuthZ, TLS, Secrets, API Security, Logging, GenAI-LLM).
* **Sub-agent prompt contract:**

  * Pulls the top Rule Cards for its topic + stack + ASVS level.
  * Generates changes (infra/app code), *cites internal Rule Card IDs* in its response, and attaches test snippets (semgrep rules, OPA policies, hadolint directives).
  * Hands off to the **Validator**.

**C. Validator & CI policy gate**

* Runs scanners aligned to the Rule Cards; on failure, returns structured findings to the orchestrator → the responsible sub-agent auto-remediates.
* Gate merges on **zero high** and **policy thresholds** for medium/low.

**D. Evidence & governance**

* Store: prompt, selected Rule Cards (hash), tool outputs, SBOM, SLSA/in-toto attestations. Enables audits and trending.

---

# concrete plan (including deep research)

## phase 0 — foundations (design & governance)

1. **Licensing & attribution**: Set up attribution banners and a LICENSE-compatibility check for CC BY-SA 4.0 derivatives. ([OWASP][2])
2. **Standards selection**: Lock the baseline: OWASP CSS, **ASVS 5.0.0**, **OWASP LLM Top 10 (2025 site + v1.1)**, **NIST SSDF v1.1**. ([GitHub][3], [OWASP Gen AI Security Project][6], [OWASP][5], [NIST CSRC][21])
3. **Tech stack policy**: Model-agnostic LLM orchestration (Claude Code for generation is fine; keep an alternate model for critique/self-check).

## phase 1 — deep research (corpus & mapping)

* **R1. Inventory & date-stamping** all Cheat Sheets; mark deprecated/redirected ones (e.g., Transport Layer Protection → TLS). ([OWASP Cheat Sheet Series][7])
* **R2. Gap analysis** vs **ASVS 5.0.0**: ensure each ASVS requirement maps to at least one Rule Card (some will map to Testing Guide/ASVS directly, not a cheat sheet). ([OWASP][20])
* **R3. GenAI risks coverage**: extract mitigations & tests from OWASP GenAI Top 10 + Red Teaming Guide; define “GenAI sub-agent” rules (prompt injection defenses, output handling, data leakage, model/connector hardening) and test using **garak**. ([OWASP Gen AI Security Project][6], [GitHub][17])
* **R4. Tool rules mapping**:

  * Cheat-sheet items → Semgrep rules (existing + custom authoring methodology). ([Semgrep][8])
  * Docker items → Hadolint/Dockle rules; container/image checks → Trivy. ([GitHub][9], [trivy.dev][10])
  * IaC items → Checkov/tfsec, plus Conftest for org-specific Rego policies. ([checkov.io][11], [aquasecurity.github.io][12], [conftest.dev][13])
  * Secrets → Gitleaks/TruffleHog. ([GitHub][14])
* **R5. Supply chain**: author SLSA/in-toto attestation plan; choose SBOM format (CycloneDX or SPDX) and generator (Syft), with Trivy/Grype scanning. ([SLSA][18], [GitHub][19], [trivy.dev][16])

**Deliverable:** a spreadsheet (Rule Card backlog) with: source link, summary, languages, ASVS mapping, candidate scanner rule, status.

## phase 2 — knowledge engineering

* Build the **Rule Card** schema and a converter that ingests OWASP pages → normalized cards (strip prose, keep normative statements, defaults, examples).
* Add **ASVS IDs** and **LLM Top 10 tags** to each card. ([OWASP][20])
* Create **starter Rule Cards** for: Authentication, Authorization, Password Storage, JWT, TLS, Input Validation, Logging, Docker, Kubernetes, API Security. ([OWASP Cheat Sheet Series][22])

## phase 3 — agent & validator MVP

* **Router**: classify tasks using repo signals (file types, paths, commit message).
* **Sub-agents** (first 3): Docker, JWT, AuthN. Each:

  * Pulls top Rule Cards from RAG index;
  * Produces diffs/templates;
  * Emits *validation hints* (expected Semgrep rules, hadolint codes, etc.).
* **CI Gate**: GitHub Actions/GitLab CI pipeline running Semgrep, Hadolint, Dockle, Trivy, Checkov/tfsec, Gitleaks, Syft→Trivy; fail on thresholds; publish SARIF. ([Semgrep][8], [GitHub][9], [trivy.dev][10], [checkov.io][11], [aquasecurity.github.io][12])
* **Attestation**: produce SLSA/in-toto provenance + attach scan reports. ([SLSA][18], [GitHub][19])

## phase 4 — genai safety add-on

* **GenAI sub-agent**: rules for prompt hygiene, context isolation, output handling (never exec untrusted output), connector hardening, data minimization.
* **LLM validation**: integrate **garak** runs for staging endpoints; include OWASP red-team test categories; block release on high-risk failures. ([GitHub][17], [OWASP Gen AI Security Project][23])

## phase 5 — evaluation & hardening

* Test against deliberately vulnerable apps (Juice Shop, WebGoat) to measure detection and auto-fix quality; add regression tests. ([OWASP][24])
* Create **scorecards** (coverage by ASVS section; time-to-fix; false-positive rate).
* Run **A/B**: generation-only vs generation+validation loop.

## phase 6 — rollout & maintenance

* **Update pipeline**: weekly crawler checks for updated cheat sheets/ASVS (diffs trigger re-ingestion + rule review).
* **Governance**: changelog, versioned Rule Cards, and attribution files to satisfy CC BY-SA. ([OWASP][2])
* **Community contributions**: publish non-org-specific Semgrep/Conftest rules upstream where possible.

---

# example “sub-agent” scope (brief)

**Docker Security Agent**

* **Pre-guidance**: base image selection, non-root user, reduce attack surface (multi-stage builds), pin versions, minimal capabilities.
* **Post-validation**: hadolint rules (DL3007, etc.), Dockle checks (CIS-aligned), Trivy image scan; Conftest Rego policies for org-specific bans (e.g., root, ADD). ([GitHub][9], [trivy.dev][10], [conftest.dev][13])

**JWT Agent (Java focus first)**

* **Pre-guidance**: alg=RS256/ES256 (reject `none`/HS256 key confusions), key mgmt/rotation, exp/aud/iss checks, clock skew handling, short TTL + refresh, JWK pinning; language-specific examples from the JWT for Java Cheat Sheet.
* **Post-validation**: Semgrep rules detecting risky JWT usage patterns; unit test templates for claim verification. ([OWASP Cheat Sheet Series][25])

**GenAI Agent**

* **Pre-guidance**: input/output contracts, tool sandboxing, secrets redaction, retrieval isolation; defensive patterns against prompt injection & insecure output handling from OWASP LLM Top 10.
* **Post-validation**: run **garak** suites for prompt injection, data leakage, jailbreaks on your staging bot/API. ([OWASP][5], [GitHub][17])

---

# success metrics

* **Coverage**: % of ASVS controls with at least one Rule Card and at least one automated check. ([OWASP][20])
* **Drift & freshness**: # of upstream changes merged/month (Cheat Sheets, ASVS, GenAI Top 10). ([GitHub][3], [OWASP Gen AI Security Project][6])
* **Security quality**: reduction in high-severity findings per KLoC; mean time-to-remediate; % of builds passing on first try.
* **GenAI safety**: garak risk score trend over time. ([GitHub][17])
* **Supply chain**: % of artifacts with valid SLSA/in-toto attestations & SBOMs. ([SLSA][18], [GitHub][19])

---

# risks to plan for (and how we handle them)

* **License obligations (CC BY-SA)** → explicit attribution + share-alike docs for derivative Rule Cards; segregate org-specific confidential guidance where needed. ([OWASP][2])
* **Tool false positives/negatives** → tune rules per repo; add “autofix” suggestions + suppression guidance with reviewer approval; write custom Semgrep/Conftest rules where gaps exist. ([Semgrep][26])
* **Staleness** → scheduled crawler + diff checks; highlight “deprecated” content and replacement. ([OWASP Cheat Sheet Series][7])
* **Over-reliance on a single LLM** → dual-model critique, and always backstop with deterministic scanners.

---

if you like this direction, I can draft:

1. the **Rule Card schema**,
2. a **sample set** for Docker/JWT/AuthN (5–10 each), and
3. a **CI pipeline** skeleton (Semgrep + Hadolint + Dockle + Trivy + Checkov + Gitleaks + Syft→Trivy + in-toto/SLSA).

that’ll give you a working end-to-end prototype you can drop into a repo and start iterating on.

[1]: https://github.com/OWASP/CheatSheetSeries?utm_source=chatgpt.com "The OWASP Cheat Sheet Series was created to provide a ..."
[2]: https://owasp.org/www-project-cheat-sheets/?utm_source=chatgpt.com "OWASP Cheat Sheet Series"
[3]: https://github.com/OWASP/ASVS?utm_source=chatgpt.com "OWASP/ASVS: Application Security Verification Standard"
[4]: https://owasp.org/www-project-application-security-verification-standard/migrated_content?utm_source=chatgpt.com "OWASP Application Security Verification Standard"
[5]: https://owasp.org/www-project-top-10-for-large-language-model-applications/?utm_source=chatgpt.com "OWASP Top 10 for Large Language Model Applications"
[6]: https://genai.owasp.org/llm-top-10/?utm_source=chatgpt.com "2025 Top 10 Risk & Mitigations for LLMs and Gen AI Apps"
[7]: https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Protection_Cheat_Sheet.html?utm_source=chatgpt.com "DEPRECATED: Transport Layer Protection Cheat Sheet"
[8]: https://semgrep.dev/p/owasp-top-ten?utm_source=chatgpt.com "owasp-top-ten ruleset - Semgrep"
[9]: https://github.com/hadolint/hadolint?utm_source=chatgpt.com "Dockerfile linter, validate inline bash, written in Haskell"
[10]: https://trivy.dev/?utm_source=chatgpt.com "Trivy"
[11]: https://www.checkov.io/?utm_source=chatgpt.com "checkov"
[12]: https://aquasecurity.github.io/tfsec/v1.28.13/?utm_source=chatgpt.com "tfsec - Aqua Security"
[13]: https://www.conftest.dev/?utm_source=chatgpt.com "Conftest"
[14]: https://github.com/gitleaks/gitleaks?utm_source=chatgpt.com "Find secrets with Gitleaks"
[15]: https://github.com/anchore/syft?utm_source=chatgpt.com "anchore/syft: CLI tool and library for generating a Software ..."
[16]: https://trivy.dev/v0.32/docs/sbom/?utm_source=chatgpt.com "SBOM"
[17]: https://github.com/NVIDIA/garak?utm_source=chatgpt.com "NVIDIA/garak: the LLM vulnerability scanner"
[18]: https://slsa.dev/spec/v1.0/?utm_source=chatgpt.com "SLSA specification"
[19]: https://github.com/in-toto/attestation?utm_source=chatgpt.com "in-toto Attestation Framework"
[20]: https://owasp.org/www-project-application-security-verification-standard/?utm_source=chatgpt.com "OWASP Application Security Verification Standard (ASVS)"
[21]: https://csrc.nist.gov/projects/ssdf?utm_source=chatgpt.com "Secure Software Development Framework | CSRC"
[22]: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html?utm_source=chatgpt.com "Authentication Cheat Sheet"
[23]: https://genai.owasp.org/2025/01/22/announcing-the-owasp-gen-ai-red-teaming-guide/?utm_source=chatgpt.com "Announcing the OWASP Gen AI Red Teaming Guide"
[24]: https://owasp.org/www-project-juice-shop/?utm_source=chatgpt.com "OWASP Juice Shop"
[25]: https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html?utm_source=chatgpt.com "JSON Web Token for Java"
[26]: https://semgrep.dev/blog/2020/writing-semgrep-rules-a-methodology?utm_source=chatgpt.com "Writing Semgrep rules"

============================================================================

I was thinking to have the relevant content as part of a sub-agent defintion instead of Knowledge layer (RAG-ready). This keeps it simpler. thoughts?

------------------------------
Short answer: you *can* keep it simple by baking the guidance straight into each sub-agent. It works well for a v1/MVP, but you’ll want a few guardrails so it doesn’t rot or blow past token limits.

Here’s how I’d think about it.

# pros of “content inside the sub-agent”

* **Simplicity**: no vector DB, no retrieval plumbing.
* **Determinism**: the agent always uses the exact, reviewed guidance you shipped.
* **Speed**: fewer moving parts → lower latency and fewer failure modes.

# cons / risks (and mitigations)

* **Staleness**: content drifts from upstream (OWASP updates).
  → **Mitigate** with build-time generation from source and a version/dated header per agent (see below).
* **Duplication**: JWT/TLS/Session guidance overlaps across agents.
  → **Mitigate** with “shared fragments” that are compiled into multiple agents at build time.
* **Token/Context bloat**: big prompts degrade quality/cost.
  → **Mitigate** with compact, structured “rule cards” + per-task filtering (files changed, language, framework).
* **Traceability** (to ASVS/LLM Top 10) gets lost if it’s just prose.
  → **Mitigate** by embedding IDs/links and emitting them in outputs/findings.
* **License hygiene** (CC BY-SA) must carry through derivative prompts.
  → **Mitigate** by auto-adding attribution blocks during build.

# recommended pattern: “compiled sub-agents” (no RAG at runtime)

* Keep a **single source of truth**: small YAML/JSON *rule cards* (one requirement each) in the repo.
* At build time, a script **compiles** topic-specific “prompt packages” per sub-agent:

  * dedupe + compress rules,
  * inject language/framework variants,
  * attach **validation hooks** (Semgrep IDs, Hadolint codes, Checkov policies, etc.),
  * stamp **source, version, date, license**.
* At runtime, the router picks the minimal subset of rules (based on changed files, stack, and labels) and hydrates the sub-agent’s system prompt. No external retrieval.

## minimal schema (source of truth)

```yaml
# rule_cards/jwt/require_exp.yml
id: JWT-EXP-001
title: "JWTs must have exp and short TTL"
scope: "backend:java,spring"
requirement: "Set exp; TTL ≤ 15m for access tokens; validate exp server-side."
rationale: "Limits replay window; aligns with ASVS 2.1.5"
do:
  - "Use RS256/ES256; do not use 'none'."
  - "Validate iss,aud,exp,nbf with clock skew ±60s."
dont:
  - "Do not accept tokens without exp."
code_templates:
  java:
    good: |
      var now = Instant.now();
      var jwt = Jwts.builder()
        .setIssuer("https://idp.example.com")
        .setAudience("api")
        .setExpiration(Date.from(now.plusSeconds(900)))
        .signWith(key, SignatureAlgorithm.RS256)
        .compact();
detect:
  semgrep: ["java.jwt.missing-exp", "java.jwt.insecure-alg"]
verify:
  tests:
    - "Reject token without exp"
    - "Reject token with exp in past"
refs:
  asvs: ["2.1.5"]
  owasp_cheatsheet: ["JWT for Java"]
license:
  source: "OWASP Cheat Sheet Series (CC BY-SA 4.0)"
```

## compiled sub-agent definition (what the runtime loads)

```json
{
  "id": "agent.jwt.java",
  "version": "2025.08.27",
  "source_digest": "sha256:…",
  "attribution": "Derived from OWASP Cheat Sheet Series (CC BY-SA 4.0). See /ATTRIBUTION.md",
  "policy": {
    "targets": ["**/*.java","**/application.yml"],
    "defaults": {"algorithms":["RS256","ES256"],"ttl_seconds":900}
  },
  "rules": ["JWT-EXP-001","JWT-ALG-002","JWT-CLAIMS-003"],
  "validation_hooks": {
    "semgrep": ["java.jwt.missing-exp","java.jwt.insecure-alg"],
    "unit_tests": ["tests/jwt/JwtExpiryTest.java"]
  }
}
```

## runtime flow (still simple, no RAG)

1. Router inspects the diff (e.g., `*.java` touched) → selects `agent.jwt.java`.
2. Agent loads only the **relevant rules** (by file/stack tags).
3. Agent proposes code changes and **lists the validation hooks** it expects to pass.
4. CI runs Semgrep/Hadolint/…; on fail, findings (with rule IDs) route back to the same agent for autofix.

# practical tips to keep it lean

* **Fragment library**: keep shared snippets (e.g., TLS basics, secrets handling) as fragments compiled into multiple agents to avoid copy-paste.
* **Prompt compression**: store rules as structured JSON and render to terse bullet points at runtime—don’t ship long prose.
* **Strict outputs**: have agents return `{diffs:[], policy_exceptions:[], expected_checks:[]}` so validators can act deterministically.
* **Version gates**: refuse to run if `version` is older than a configured cutoff (forces updates).
* **Attribution injection**: auto-append attribution & license notes to each compiled agent package.

# how this changes the earlier plan

* Drop the RAG service; **Phase 1–2** become “build the rule-card repo + compiler.”
* Keep **Phase 3–4** (agents + validators) the same.
* For **freshness**, add a weekly bot that opens PRs when upstream OWASP pages change (diff + regenerated rule cards), but still *compile* at build time.

# quick to-do list (MVP)

1. Define the rule-card schema + write 20–30 cards (Docker, JWT, AuthN).
2. Write a tiny **compiler** (Python) that:

   * reads cards, resolves fragments, emits per-agent JSON, writes `/dist/agents/*.json`,
   * validates IDs, dedupes detect hooks, stamps version/date, inserts attribution.
3. Implement the **router** (filetype + repo tags) and a slim **sub-agent runtime** that:

   * loads its JSON,
   * renders a concise system prompt from the selected rules,
   * returns structured outputs with expected validation hooks.
4. CI skeleton: Semgrep + Hadolint + Trivy + Checkov + Gitleaks wired to fail on **High**; echo rule IDs back to PR.
5. Add **release governance**: a `SECURITY_GUIDE.md` describing the approach, plus `ATTRIBUTION.md` for CC BY-SA.

This keeps your runtime dead simple—no retrieval layer—while preserving maintainability, traceability, and CI alignment. If/when you outgrow it (lots of stacks/languages), you can swap in RAG later without changing the rule-card source or the validator loop.

===================================================================

great. update the plan with this detail



awesome — here’s the **updated plan** aligned to “compiled sub-agents” (no runtime RAG), while keeping pre-guidance + post-validation.

# goals

* Package OWASP/ASVS/GenAI guidance **inside** each sub-agent at build time.
* Keep runtime dead simple: router → sub-agent → validator CI gate.
* Maintain freshness via a lightweight weekly sync job.

# phase 0 — governance & foundations

**Deliverables**

* `SECURITY_GUIDE.md` (approach & responsibilities)
* `ATTRIBUTION.md` (CC BY-SA attribution + derivative notices)
* `POLICY.yml` (merge gates: fail on High, thresholds for Medium/Low)
* Model policy: generation model + secondary critique model

**Key decisions**

* Supported stacks (e.g., Java/Spring, Node/Express, Python/FastAPI, Docker, Kubernetes, Terraform)
* CI provider (GitHub Actions/GitLab CI)

---

# phase 1 — deep research (source curation & mapping)

**Objective:** compile authoritative, current guidance and map it to verifiable controls.

**Tasks**

1. **Inventory sources** (date-stamped): OWASP Cheat Sheets (by topic), OWASP ASVS 5.x, OWASP LLM/GenAI Top 10, NIST SSDF.
2. **Deprecation pass:** mark any moved/obsolete sheets; record replacements.
3. **Control mapping:** map each topic to ASVS/LLM Top 10 IDs (traceability backbone).
4. **Scanner capability matrix:** for each topic, list feasible checks (Semgrep, Hadolint, Dockle, Trivy, Checkov/tfsec, Conftest/OPA, Gitleaks, SBOM/SCA tools, garak for GenAI apps).
5. **Gaps & custom checks:** note where custom Semgrep/Conftest rules will be needed.

**Deliverable**

* `research/controls.xlsx` (source → rule candidate → tool check → ASVS/LLM IDs → status)

---

# phase 2 — rule cards (single source of truth)

**Objective:** encode guidance in compact, testable units.

**Artifacts**

* `rule_cards/**/<topic>/*.yml` — one requirement per file.

**Schema (concise)**

```yaml
id: DOCKER-USER-001
title: "Run as non-root"
scope: "dockerfile"
requirement: "Set USER to a non-root UID/GID; no root processes in final image."
do:
  - "Create app user in final stage and chown workdir."
dont:
  - "Avoid USER root"
detect:
  hadolint: ["DL3002"]
  dockle: ["CIS-DI-0005"]
  conftest: ["policies/docker/non_root.rego"]
verify:
  tests: ["Container process UID != 0"]
refs:
  asvs: ["V14.5"]
  owasp_cheatsheet: ["Docker Security"]
license:
  source: "OWASP Cheat Sheet Series (CC BY-SA 4.0)"
```

**Tasks**

* Author 20–30 cards for MVP topics: **Docker, JWT (Java), Authentication, TLS basics, Secrets Handling, Logging**, **GenAI app safety**.
* Add shared fragments (e.g., TLS, secrets) to reuse across topics.

**Deliverable**

* Rule card repo with linting (`scripts/validate_cards.py`)

---

# phase 3 — compiler (build-time, no RAG)

**Objective:** compile rule cards into **sub-agent packages**.

**Outputs**

* `/dist/agents/<agent_id>.json` (versioned, hashed)

**Compiler responsibilities**

* Select rules by topic + stack
* Resolve fragments; dedupe & compress
* Inject **validation hooks** (scanner rule IDs)
* Stamp `version`, `build_date`, `source_digest`, **attribution block**
* Size guardrails (token budget hints)

**CLI**

```
compile-agents --topics docker jwt-java authn --out dist/agents
```

**Deliverables**

* `tools/compile_agents.py`
* CI job that runs compiler and fails on schema/traceability errors

---

# phase 4 — runtime: router + sub-agent contract

**Router**

* Heuristics: changed files, repo tags (`stack:java`, `service:payments`), path patterns
* Selects minimal agent set (e.g., `agent.docker`, `agent.jwt.java`)

**Sub-agent contract (strict)**

* **Input:** `{files_changed, stack, context}`
* **Loads:** its compiled JSON + only the needed rules
* **Output (machine-readable):**

```json
{
  "diffs": [ { "path": "Dockerfile", "patch": "..." } ],
  "policy_exceptions": [],
  "expected_checks": {
    "hadolint": ["DL3002"],
    "semgrep": ["java.jwt.missing-exp"]
  },
  "rationale_refs": ["ASVS V2.1.5", "OWASP Docker"]
}
```

**Deliverables**

* `agents/runtime/*` (language-agnostic)
* Unit tests for routing logic

---

# phase 5 — validator CI gate (post-validation)

**Pipeline steps (per PR)**

1. **Semgrep** (with custom rule bundle)
2. **Hadolint** (Dockerfile), **Dockle** (image)
3. **Trivy** (image + deps/SCA); **Syft** to generate SBOM → **Trivy/Grype** scan
4. **IaC:** Checkov/tfsec; **Conftest** org policies
5. **Secrets:** Gitleaks
6. **GenAI apps:** garak suites on staging endpoints (if applicable)
7. **Provenance:** in-toto/SLSA attestations attached to artifacts
8. **Publish SARIF** to code host; block on policy thresholds

**Deliverables**

* `.github/workflows/security.yml` (or GitLab CI equivalent)
* `policy/thresholds.yml`
* Sample PR comment formatter that echoes failing **rule IDs** back to authors

---

# phase 6 — sample content & e2e demo

**Scope**

* Docker Security Agent
* JWT (Java) Agent
* AuthN Agent

**Deliverables**

* Example repo with deliberately weak patterns
* Recorded run: router → agents suggest diffs → CI runs → fails → apply agent diffs → CI passes

---

# phase 7 — freshness & maintenance

**Weekly sync bot**

* Checks upstream OWASP/ASVS/LLM pages for changes
* Opens PR with **diff summary**, regenerated rule cards, and recompiled agents
* Fails the build if agents are past a `min_version_date`

**Metrics dashboard**

* Coverage: % ASVS controls with rule cards & checks
* Build health: pass rate on first try; mean time to remediate
* Scanner quality: FP/FN tuning backlog
* GenAI safety: garak score trend

---

# phase 8 — hardening & scale-out

* Add languages (Node, Python), platforms (K8s), and org policies
* Dual-model critique flow for high-risk changes
* Policy exceptions workflow with expiry & approval trails

---

## directory layout (suggested)

```
/rule_cards/
  docker/*.yml
  jwt/java/*.yml
  shared/*.yml
/tools/
  compile_agents.py
  validate_cards.py
/dist/agents/
agents/
  runtime/ (router + executor)
/ci/
  semgrep-rules/
  conftest-policies/
/policy/
  thresholds.yml
docs/
  SECURITY_GUIDE.md
  ATTRIBUTION.md
```

## acceptance criteria (MVP)

* Compiled agents ≤ N tokens each (configurable), with attribution + version
* Router triggers correct agents from a realistic diff
* Agents emit structured outputs with **expected\_checks** that match CI rules
* CI blocks on High and references the same **rule IDs** as the agents
* Weekly sync bot creates a PR when any upstream doc changes

---

## immediate next steps (2–3 weeks of work)

1. Finalize **rule card schema** + author first 25 cards (Docker/JWT/AuthN/TLS).
2. Build **compiler** + schema validator; produce `/dist/agents`.
3. Implement **router + runtime** and wire a demo repo.
4. Stand up **CI gate** with scanners + SARIF publishing.
5. Create **sync bot** skeleton (diff → PR) and set `min_version_date` policy.

If you want, I can spin up the initial rule cards and the compiler skeleton next.


=====================================================================================================

spin up the initial rule cards and the compiler skeleton next
---------------------------------------


now complete 
phase 1 — deep research (source curation & mapping)

Objective: compile authoritative, current guidance and map it to verifiable controls.

Tasks

Inventory sources (date-stamped): OWASP Cheat Sheets (by topic), OWASP ASVS 5.x, OWASP LLM/GenAI Top 10, NIST SSDF.

Deprecation pass: mark any moved/obsolete sheets; record replacements.

Control mapping: map each topic to ASVS/LLM Top 10 IDs (traceability backbone).

Scanner capability matrix: for each topic, list feasible checks (Semgrep, Hadolint, Dockle, Trivy, Checkov/tfsec, Conftest/OPA, Gitleaks, SBOM/SCA tools, garak for GenAI apps).

Gaps & custom checks: note where custom Semgrep/Conftest rules will be needed.

Deliverable

research/controls.xlsx (source → rule candidate → tool check → ASVS/LLM IDs → status)


==========================================================================================

what is a good github repo name for this project?

---------------------------------------

Some good GitHub repo name ideas that fit the project’s purpose and style:

* **`genai-sec-agents`** – short, clear, signals GenAI focus.
* **`owasp-agent-kit`** – emphasizes OWASP alignment + agent packaging.
* **`sec-rule-cards`** – descriptive if you want to highlight the rule card system.
* **`genai-sec-cheatsheet-agents`** – explicit about using OWASP cheat sheets as sub-agent bases.
* **`code-sec-agents`** – broad, usable if you expand beyond GenAI.
* **`agentic-secops`** – catchy if you want to brand it a bit.

👉 If you want clarity for external users, I’d recommend `genai-sec-agents` (short, unambiguous, future-proof). If you want to lean into OWASP source transparency, `owasp-agent-kit` is stronger.

Do you want the repo name to be **developer-facing & descriptive** (so outsiders instantly get it), or more of a **brandable project name**?


