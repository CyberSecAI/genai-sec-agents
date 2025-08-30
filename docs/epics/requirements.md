# **Requirements**

## **Functional Requirements**

1. **FR1: Knowledge Base Management:** The system must provide an interface for authorized AppSec engineers (Leo) to create, edit, and manage "Rule Cards" in the knowledge base.  
2. **FR2: Hybrid Knowledge Ingestion:** The system must be able to ingest and normalize security guidance from both internal policy documents and external sources (e.g., OWASP Cheat Sheets).  
3. **FR3: Real-Time IDE Guidance:** The system's agent must provide developers (Daniella) with real-time, context-aware security guidance and actionable code suggestions as they write code in a supported IDE.  
4. **FR4: CI/CD Validation:** The system must integrate with the CI/CD pipeline to run the same validation checks as the IDE agent, reporting its findings in the build logs.  
5. **FR5: Audit Logging:** The system must generate a comprehensive and auditable log of all significant events, including the creation or modification of a Rule Card and every instance of a rule being enforced in the CI/CD pipeline (for Charlotte).  
6. **FR6: Manual and Automated Execution:** The system must support both manual, on-demand execution by a developer in their IDE and automated execution as part of the CI/CD pipeline.  
7. **FR7: Rule Card Version Control and Audit Trail:** All changes to a "Rule Card" (create, update, disable) must be version-controlled. The system must maintain a complete, auditable history of these changes, similar to a Git history, showing who made what change and when (for Leo and Charlotte).  
8. **FR8: Actionable Rule Card Schema:** Each "Rule Card" must contain a structured schema that includes not only the security guidance and rationale but also machine-readable metadata. This metadata must specify the validation tool to use (e.g., Semgrep, TruffleHog), the specific rule ID or configuration file for that tool, and secure code examples. This ensures the agent can both provide guidance and trigger the correct, deterministic check in the CI/CD pipeline.

## **Non-Functional Requirements**

1. **NFR1: Performance:** The IDE agent must provide feedback in near real-time, with a target response time of less than 2 seconds, to avoid disrupting the developer's workflow.  
2. **NFR2: Consistency:** The security feedback, rule IDs, and guidance provided by the IDE agent must be 100% consistent with the results from the CI/CD validation gate for the same code.  
3. **NFR3: Actionability:** All guidance provided by the agent must be clear, concise, and actionable, providing developers with trusted code snippets and direct links to the relevant rule in the knowledge base.  
4. **NFR4: Extensibility:** The system architecture, particularly the knowledge base, must be designed to be extensible, allowing for the easy addition of new rules and support for new programming languages and frameworks.  
5. **NFR5: Platform Agnosticism:** The agentic component of the system must be designed to be platform-agnostic, with an architecture that supports future integration into multiple IDEs and AI assistant platforms (e.g., Claude Code, Cursor, GitHub Copilot).  
6. **NFR6: Reliability (MVP):** For the MVP, the CI/CD validation gate must run in a non-blocking, advisory mode to build trust and prevent disruption to development pipelines.  
7. **NFR7: Policy Coverage Measurement:** The system must provide a mechanism to measure and report on the coverage of its "Rule Cards" against both internal policies and key security domains (e.g., JWTs, cookies, secrets, GenAI development). This is essential for auditing and demonstrating compliance (for Charlotte).  
8. **NFR8: Efficient Rule Updates:** The system must support the ability to update, add, or disable individual "Rule Cards" in the knowledge base dynamically, without requiring a full rebuild or redeployment of the entire agentic system. This ensures that policy changes can be rolled out rapidly in response to new threats (for Leo).
