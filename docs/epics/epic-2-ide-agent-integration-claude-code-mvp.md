# **Epic 2: IDE Agent Integration (Claude Code MVP)**

**Goal:** To provide developers (Daniella) with immediate, consistent, and actionable security guidance directly within their primary agentic tool, Claude Code. This epic builds the "inner loop" of the feedback system, preventing vulnerabilities at the moment of creation.

## **Stories**

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
