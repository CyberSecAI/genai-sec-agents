# **Epic 1: The Policy-as-Code Engine**

**Goal:** To empower the AppSec Engineer (Leo) with a robust, auditable, and efficient "Policy-as-Code" workflow. This epic delivers the complete toolchain for creating, validating, and compiling security Rule Cards into machine-readable agent packages, and includes the manual creation of the initial, high-value set of rules.

## **Stories**

* **Story 1.1: Establish the Rule Card Repository & Schema**  
  * **As a** Lead AppSec Engineer (Leo),  
  * **I want** a standardized YAML schema and a dedicated Git repository for "Rule Cards,"  
  * **so that** I have a single, version-controlled source of truth for all security policies.  
  * **Acceptance Criteria:**  
    1. A new Git repository (genai-sec-agents) is created.  
    2. A formal YAML schema for a "Rule Card" is defined and documented, including all required fields (id, title, detect, etc.) as specified in **FR8**.  
    3. The repository includes the initial directory structure (/rule\_cards, /tools, /docs).  
    4. A validate\_cards.py script is created that can validate a directory of Rule Cards against the defined schema.  
    5. The ATTRIBUTION.md and SECURITY\_GUIDE.md documents are created.  
* **Story 1.2: Manually Ingest and Author Initial Rule Cards**  
  * **As a** Lead AppSec Engineer (Leo),  
  * **I want** to manually create the first set of Rule Cards based on our internal policies,  
  * **so that** the system's MVP knowledge base is seeded with our most critical, high-value security requirements.  
  * **Acceptance Criteria:**  
    1. A minimum of 10-15 "Rule Cards" are authored in YAML format and pass schema validation.  
    2. The initial set of cards covers the MVP's target domains: hardcoded secrets, secure cookies, JWT handling, and GenAI development security.  
    3. Each Rule Card contains accurate detect metadata, mapping the rule to a specific, real-world scanner rule (e.g., a Semgrep rule ID).  
    4. Each Rule Card includes traceability references (refs) to external standards like ASVS where applicable.  
* **Story 1.3: Implement the Agent Compiler Toolchain**  
  * **As a** Lead AppSec Engineer (Leo),  
  * **I want** a compiler script that transforms the YAML Rule Cards into versioned, machine-readable JSON packages,  
  * **so that** I can create deterministic, self-contained knowledge packages for the GenAI agents.  
  * **Acceptance Criteria:**  
    1. An agents\_manifest.yml file is created to define the different sub-agents and their associated Rule Card topics.  
    2. A compile\_agents.py script is created that reads the manifest and the Rule Cards.  
    3. The script successfully compiles the rules into a valid JSON package per the defined schema.  
    4. The output JSON includes all required metadata: version, build date, source digest, and attribution notices.  
    5. The script aggregates all detect hooks from the included Rule Cards into a single validation\_hooks map in the output JSON.
