# **AI-Powered DevSecOps Assistant \- Product Requirements Document (PRD)**

| Date | Version | Description | Author |
| :---- | :---- | :---- | :---- |
| 2025-08-29 | 1.0 | Initial draft based on Project Brief | John, PM |
| 2025-08-29 | 1.1 | Added UI/Rule Management Workflow | John, PM |
| 2025-08-29 | 1.2 | Clarified Epic 1 Scope | John, PM |

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