# **Components**

The system is composed of four primary logical components. Each component has a distinct responsibility and a well-defined interface for interacting with the others.

## **1\. Policy-as-Code Repository**

* **Responsibility:** To serve as the single source of truth for all security rules and agent configurations. This component is the human interface for the security team (Leo).  
* **Key Interfaces:**  
  * **Input:** Manual creation and editing of YAML Rule Cards (/rule\_cards/) and the agents\_manifest.yml via Git.  
  * **Output:** Version-controlled YAML files that are consumed by the Compiler.  
* **Dependencies:** None. This is the foundational component.  
* **Technology Stack:** Git, YAML.

## **2\. Rule Card Compiler**

* **Responsibility:** To perform the build-time transformation of human-readable YAML Rule Cards into machine-readable, versioned JSON packages. It is a critical offline process that ensures the runtime components are fast and deterministic.  
* **Key Interfaces:**  
  * **Input:** Reads all YAML files from the Policy-as-Code Repository.  
  * **Output:** Writes compiled agent.\<id\>.json packages to the /dist/agents/ directory.  
* **Dependencies:** Policy-as-Code Repository.  
* **Technology Stack:** Python, PyYAML.

## **3\. Agentic Runtime & Router**

* **Responsibility:** To provide real-time, "just-in-time" security guidance to developers. This component lives within the developer's agentic IDE (e.g., Claude Code).  
* **Key Interfaces:**  
  * **Input:** Consumes the developer's current code context (file path, content) and loads the relevant compiled agent JSON package.  
  * **Output:** Generates natural language guidance and secure code suggestions for the developer.  
* **Dependencies:** Compiled Agent Packages.  
* **Technology Stack:** Model-Agnostic LLM Orchestration, Anthropic Claude.

## **4\. CI/CD Validation Engine**

* **Responsibility:** To provide the deterministic "post-code" validation gate in the CI/CD pipeline. It enforces the policy defined in the Rule Cards.  
* **Key Interfaces:**  
  * **Input:** Consumes the developer's committed code and the relevant compiled agent JSON package (specifically the validation\_hooks).  
  * **Output:** Executes the specified scanners and produces a pass/fail result with a structured report (e.g., SARIF) for the CI/CD system.  
* **Dependencies:** Compiled Agent Packages, Developer's Code.  
* **Technology Stack:** GitHub Actions, Semgrep, CodeQL, TruffleHog, Checkov, Hadolint, Dockle.
