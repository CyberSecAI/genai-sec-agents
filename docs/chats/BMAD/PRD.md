# **AI-Powered DevSecOps Assistant Product Requirements Document (PRD)**

| Date | Version | Description | Author |
| :---- | :---- | :---- | :---- |
| 2025-08-29 | 1.0 | Initial draft based on Project Brief | John, PM |
| 2025-08-29 | 1.1 | Added UI/Rule Management Workflow | John, PM |
| 2025-08-29 | 1.2 | Clarified Epic 1 Scope | John, PM |
| 2025-08-29 | 1.3 | Added Epic 1 Story Breakdown | John, PM |
| 2025-08-29 | 1.4 | Added Epic 2 Story Breakdown | John, PM |
| 2025-08-29 | 1.5 | Completed Epic 3 and finalized PRD | John, PM |

## **Goals and Background Context**

### **Goals**

The primary goals of this project are to:

* Significantly reduce the time and cost associated with remediating common security vulnerabilities.  
* Improve developer velocity by preventing security issues from blocking the CI/CD pipeline late in the development cycle.  
* Establish a consistent, auditable, and scalable security posture by codifying internal and external security standards.  
* Increase developer trust and satisfaction with the security process by providing guidance that is immediate, actionable, and consistent.

### **Background Context**

The organization's current security workflow creates significant friction for our development teams. Security feedback is often delivered late by CI/CD scanners, forcing expensive context-switching and delaying releases. This creates a perception of security as a blocker rather than a partner.

This project addresses this by creating an AI-powered assistant that shifts security guidance to the very beginning of the development process—right in the developer's IDE. By leveraging a hybrid knowledge base of both industry standards (OWASP) and our own internal security lessons, the system will provide immediate, consistent, and actionable advice. This allows us to prevent vulnerabilities before they are written, scale the expertise of our AppSec team, and ensure that our security policies are enforced consistently from the first line of code to the final build.

## **Requirements**

### **Functional Requirements**

1. **FR1: Knowledge Base Management:** The system must provide an interface for authorized AppSec engineers (Leo) to create, edit, and manage "Rule Cards" in the knowledge base.  
2. **FR2: Hybrid Knowledge Ingestion:** The system must be able to ingest and normalize security guidance from both internal policy documents and external sources (e.g., OWASP Cheat Sheets).  
3. **FR3: Real-Time IDE Guidance:** The system's agent must provide developers (Daniella) with real-time, context-aware security guidance and actionable code suggestions as they write code in a supported IDE.  
4. **FR4: CI/CD Validation:** The system must integrate with the CI/CD pipeline to run the same validation checks as the IDE agent, reporting its findings in the build logs.  
5. **FR5: Audit Logging:** The system must generate a comprehensive and auditable log of all significant events, including the creation or modification of a Rule Card and every instance of a rule being enforced in the CI/CD pipeline (for Charlotte).  
6. **FR6: Manual and Automated Execution:** The system must support both manual, on-demand execution by a developer in their IDE and automated execution as part of the CI/CD pipeline.  
7. **FR7: Rule Card Version Control and Audit Trail:** All changes to a "Rule Card" (create, update, disable) must be version-controlled. The system must maintain a complete, auditable history of these changes, similar to a Git history, showing who made what change and when (for Leo and Charlotte).  
8. **FR8: Actionable Rule Card Schema:** Each "Rule Card" must contain a structured schema that includes not only the security guidance and rationale but also machine-readable metadata. This metadata must specify the validation tool to use (e.g., Semgrep, TruffleHog), the specific rule ID or configuration file for that tool, and secure code examples. This ensures the agent can both provide guidance and trigger the correct, deterministic check in the CI/CD pipeline.

### **Non-Functional Requirements**

1. **NFR1: Performance:** The IDE agent must provide feedback in near real-time, with a target response time of less than 2 seconds, to avoid disrupting the developer's workflow.  
2. **NFR2: Consistency:** The security feedback, rule IDs, and guidance provided by the IDE agent must be 100% consistent with the results from the CI/CD validation gate for the same code.  
3. **NFR3: Actionability:** All guidance provided by the agent must be clear, concise, and actionable, providing developers with trusted code snippets and direct links to the relevant rule in the knowledge base.  
4. **NFR4: Extensibility:** The system architecture, particularly the knowledge base, must be designed to be extensible, allowing for the easy addition of new rules and support for new programming languages and frameworks.  
5. **NFR5: Platform Agnosticism:** The agentic component of the system must be designed to be platform-agnostic, with an architecture that supports future integration into multiple IDEs and AI assistant platforms (e.g., Claude Code, Cursor, GitHub Copilot).  
6. **NFR6: Reliability (MVP):** For the MVP, the CI/CD validation gate must run in a non-blocking, advisory mode to build trust and prevent disruption to development pipelines.  
7. **NFR7: Policy Coverage Measurement:** The system must provide a mechanism to measure and report on the coverage of its "Rule Cards" against both internal policies and key security domains (e.g., JWTs, cookies, secrets, GenAI development). This is essential for auditing and demonstrating compliance (for Charlotte).  
8. **NFR8: Efficient Rule Updates:** The system must support the ability to update, add, or disable individual "Rule Cards" in the knowledge base dynamically, without requiring a full rebuild or redeployment of the entire agentic system. This ensures that policy changes can be rolled out rapidly in response to new threats (for Leo).

## **Rule Management & Governance Workflow**

The primary interface for managing the security knowledge base is not a traditional GUI, but rather a **Policy-as-Code** workflow centered around a Git repository and a command-line toolchain. This approach provides maximum efficiency, auditability, and precision for expert users like Leo (AppSec Engineer) and Charlotte (CISO).

### **Core Principles**

* **Policy-as-Code (GitOps Model):** The "single source of truth" for all security rules is a collection of human-readable YAML files ("Rule Cards") stored in a dedicated Git repository. This is the primary interface for managing policy.  
* **Git-Based Versioning and Audit:** All changes to Rule Cards—creations, edits, deactivations—are managed through standard Git workflows (branches, pull requests, reviews, merges). This provides a complete, immutable, and auditable history of every policy change, directly satisfying **FR7**.  
* **Automated Compilation:** A command-line compiler script (compile\_agents.py) transforms the human-readable YAML Rule Cards into structured, machine-readable JSON packages. These compiled packages are the artifacts used by the GenAI agents at runtime, ensuring there is no need for a live RAG database in the MVP.

### **Workflow Components**

* **Rule Card Directory (/rule\_cards/):** The main workspace for Leo. AppSec engineers will create and edit YAML files in this directory. The structure is organized by security domain (e.g., /docker/, /jwt/java/) for clarity.  
* **Agent Manifest (tools/agents\_manifest.yml):** The high-level configuration file where Leo defines the different sub-agents and maps which Rule Card topics belong to each one.  
* **Validation & Compilation Toolchain (tools/):** A set of Python scripts that provide the core engine for the system:  
  * validate\_cards.py: A script to validate all Rule Cards against the required schema (**FR8**).  
  * compile\_agents.py: The script that reads the manifest, collects the relevant Rule Cards, and builds the final JSON packages for the agents.  
* **Compiled Agent Packages (/dist/agents/):** The output directory containing the final, versioned JSON artifacts that are consumed by the GenAI agents. This separation of source (YAML) from compiled output (JSON) is a key architectural principle.

## **Epic List**

The work required to deliver the MVP will be organized into the following logically sequenced epics. Each epic delivers a significant, deployable increment of value.

* **Epic 1: The Policy-as-Code Engine:** This foundational epic delivers the core value for the AppSec Engineer (Leo). It establishes the Git-based workflow for managing Rule Cards, **includes the manual ingestion and creation of the initial set of Rule Cards from key internal and external sources**, and provides the toolchain to validate and compile them into agent-ready packages. This epic creates the "brain" of our system and populates it with its initial knowledge.  
* **Epic 2: IDE Agent Integration (Claude Code MVP):** This epic focuses on delivering the "just-in-time" guidance for the Developer (Daniella). It involves building the agentic component that consumes the compiled packages from Epic 1 and integrates with our primary target platform, Claude Code, to provide real-time feedback.  
* **Epic 3: CI/CD Advisory Integration:** This epic delivers the value for the SRE (Sara) and closes the loop on consistency. It focuses on integrating the compiled security rules into the CI/CD pipeline in a non-blocking, advisory mode. This provides the deterministic "post-code validation" gate and generates the reports needed by the CISO (Charlotte) and PM (Priya).

## **Epic 1: The Policy-as-Code Engine**

**Goal:** To empower the AppSec Engineer (Leo) with a robust, auditable, and efficient "Policy-as-Code" workflow. This epic delivers the complete toolchain for creating, validating, and compiling security Rule Cards into machine-readable agent packages, and includes the manual creation of the initial, high-value set of rules.

### **Stories**

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

## **Epic 2: IDE Agent Integration (Claude Code MVP)**

**Goal:** To provide developers (Daniella) with immediate, consistent, and actionable security guidance directly within their primary agentic tool, Claude Code. This epic builds the "inner loop" of the feedback system, preventing vulnerabilities at the moment of creation.

### **Stories**

* **Story 2.1: Develop the Agentic Runtime Core**  
  * **As a** Deadline-Driven Developer (Daniella),  
  * **I want** an agentic runtime that can load and interpret the compiled security packages,  
  * **so that** the foundation for providing in-IDE guidance is in place.  
  * **Acceptance Criteria:**  
    1. A core runtime component is created that can parse a compiled agent JSON package.  
    2. The runtime can successfully load the rules\_detail and validation\_hooks from the package.  
    3. The runtime provides a function to select a subset of rules based on the current context (e.g., file type).  
    4. The runtime is designed to be model-agnostic, with a clear interface for interacting with an LLM.  
* **Story 2.2: Implement the Claude Code Sub-Agent and Router**  
  * **As a** Deadline-Driven Developer (Daniella),  
  * **I want** a sub-agent within Claude Code that automatically provides security guidance relevant to the code I'm writing,  
  * **so that** I can fix security issues in real-time without leaving my IDE.  
  * **Acceptance Criteria:**  
    1. The agentic platform (Claude Code) is responsible for routing and selecting the appropriate sub-agent based on file context.  
    2. The sub-agent, upon activation, loads its compiled JSON package.  
    3. The sub-agent uses the LLM to generate guidance based on the loaded Rule Cards and the user's code.  
    4. The guidance is displayed to the user in a non-intrusive, real-time manner.  
    5. The agent is capable of suggesting actionable, secure code snippets as defined in the Rule Cards.  
    6. The agent's response time is under 2 seconds to meet **NFR1**.  
* **Story 2.3: Manual On-Demand Execution**  
  * **As a** Deadline-Driven Developer (Daniella),  
  * **I want** to be able to manually trigger a security scan of my current file or workspace from within my IDE,  
  * **so that** I can get a complete security picture before I commit my code.  
  * **Acceptance Criteria:**  
    1. The sub-agent exposes a command that a developer can manually invoke.  
    2. When invoked, the agent performs a security analysis of the specified code against all relevant Rule Cards.  
    3. The results are displayed in a clear, easy-to-read format in the IDE's interface.  
    4. This manual execution provides feedback consistent with the automated CI/CD checks (**NFR2**).

## **Epic 3: CI/CD Advisory Integration**

**Goal:** To provide a deterministic, trustworthy "post-code validation" gate in the CI/CD pipeline that is 100% consistent with the guidance developers receive in their IDE. This epic closes the feedback loop and provides auditable evidence of policy enforcement for Sara, Charlotte, and Priya.

### **Stories**

* **Story 3.1: CI/CD Integration Scaffolding**  
  * **As an** SRE & Pipeline Architect (Sara),  
  * **I want** a basic CI/CD job (e.g., a GitHub Action) that can be triggered on pull requests,  
  * **so that** we have a dedicated entry point for our automated security validation.  
  * **Acceptance Criteria:**  
    1. A new GitHub Actions workflow is created.  
    2. The workflow is configured to trigger on pull\_request events targeting the main branch.  
    3. The job checks out the source code and sets up the required environment (e.g., Python, Docker).  
    4. The job has the necessary permissions to read code and post comments back to the pull request.  
* **Story 3.2: Implement the CI Validation Engine**  
  * **As an** SRE & Pipeline Architect (Sara),  
  * **I want** a validation engine within the CI job that can interpret the compiled agent packages,  
  * **so that** it knows exactly which scanners and rules to run for a given change.  
  * **Acceptance Criteria:**  
    1. The CI job includes a script that can identify the relevant compiled agent package based on the files changed in the PR.  
    2. The script correctly parses the validation\_hooks from the JSON package to determine which tools (e.g., Semgrep, TruffleHog) and which specific rules need to be executed.  
    3. The engine can dynamically construct the command-line arguments for each required scanner.  
* **Story 3.3: Integrate and Execute Security Scanners**  
  * **As an** SRE & Pipeline Architect (Sara),  
  * **I want** the CI job to execute the full suite of required security scanners,  
  * **so that** our codified security policy is automatically enforced.  
  * **Acceptance Criteria:**  
    1. All required scanners (Semgrep, CodeQL, TruffleHog, Checkov, Hadolint, Dockle) are installed and configured to run within the CI job.  
    2. The validation engine successfully invokes the correct scanners with the correct rules based on the validation\_hooks.  
    3. The scanners execute successfully against the changed code in the pull request.  
    4. The results from each scanner are captured in a standard format (e.g., SARIF).  
* **Story 3.4: Implement Non-Blocking Advisory Reporting**  
  * **As a** Strategic CISO (Charlotte),  
  * **I want** the CI/CD pipeline to report on security findings without blocking builds,  
  * **so that** we can gather data and build trust in the MVP without disrupting development velocity.  
  * **Acceptance Criteria:**  
    1. The CI job is configured to be **non-blocking**; it will always complete successfully regardless of scanner findings (**NFR6**).  
    2. The job aggregates all findings from the SARIF reports.  
    3. A summary of the findings is posted as a comment on the corresponding pull request.  
    4. The comment is clear, concise, and links any findings back to the originating Rule Card ID, ensuring consistency (**NFR2**).  
    5. The raw SARIF files are stored as build artifacts for audit and reporting purposes (**FR5**).