# **AI-Powered DevSecOps Assistant Fullstack Architecture Document**

| Date | Version | Description | Author |
| :---- | :---- | :---- | :---- |
| 2025-08-29 | 1.0 | Initial draft of the architecture | Winston, Architect |
| 2025-08-29 | 1.1 | Added High Level Architecture section | Winston, Architect |
| 2025-08-29 | 1.2 | Refined feedback loop pattern | Winston, Architect |
| 2025-08-29 | 1.3 | Added Tech Stack section | Winston, Architect |
| 2025-08-29 | 1.4 | Added Data Models section | Winston, Architect |
| 2025-08-29 | 1.5 | Added API Specification | Winston, Architect |
| 2025-08-29 | 1.6 | Added Components section | Winston, Architect |
| 2025-08-29 | 1.7 | Added Core Workflows section | Winston, Architect |
| 2025-08-29 | 2.0 | Completed remaining architecture sections | Winston, Architect |

## **Introduction**

This document outlines the complete fullstack architecture for the AI-Powered DevSecOps Assistant, including backend systems, frontend implementation, and their integration. It serves as the single source of truth for AI-driven development, ensuring consistency across the entire technology stack.

This unified approach combines what would traditionally be separate backend and frontend architecture documents, streamlining the development process for modern fullstack applications where these concerns are increasingly intertwined.

### **Starter Template or Existing Project**

Based on the detailed project plan and "Policy-as-Code" approach, this architecture will be implemented from scratch without a starter template. The defined toolchain, directory structure, and custom compiler script will serve as the project's foundation.

## **High Level Architecture**

This section defines the overall architectural style, key components, and core patterns that will govern the system's design and implementation.

### **Technical Summary**

The system is designed as a **decoupled, event-driven security framework** that operates in multiple distinct feedback loops: a "just-in-time" guidance loop within the developer's agentic IDE, a manual "pre-commit" validation loop on the local machine, and an automated "post-commit" validation loop in the CI/CD pipeline. The architecture's core is a **Policy-as-Code repository** containing human-readable security "Rule Cards" in YAML. At build time, a Python-based **compiler** transforms these rules into versioned, machine-readable JSON packages. These compiled packages are then consumed by GenAI sub-agents to provide guidance, and by CI/CD scanners to enforce policy, ensuring 100% consistency across all feedback loops. The system is model-agnostic and relies on a curated set of best-in-class open-source scanners for deterministic validation.

### **Platform and Infrastructure Choice**

The system is platform-agnostic by design and does not require a complex infrastructure. The primary "platform" is the developer's toolchain and the organization's existing CI/CD service.

* **Platform**: The system is designed to run within standard development and CI/CD environments.  
  * **Primary Agentic Platform (MVP)**: Claude Code  
  * **CI/CD Service**: GitHub Actions or GitLab CI  
* **Key Services**:  
  * **Source Control**: Git (e.g., GitHub, GitLab) is the central platform for managing the Rule Card repository.  
  * **CI/CD Runners**: Standard Linux-based runners with Docker support are required to execute the compiler and scanning tools.  
* **Deployment Host**: The compiled agent JSON packages will be versioned and can be hosted in a simple, reliable object store (e.g., AWS S3, Google Cloud Storage) or distributed via a package manager for consumption by the agentic runtimes.

### **Repository Structure**

The project will be organized as a **monorepo** to facilitate the management of the interconnected components (Rule Cards, compiler, agent runtime, CI configurations).

* **Structure**: A single Git repository will contain all source code and configuration.  
* **Monorepo Tool**: While no complex tool like Nx is needed for the MVP, the structure is designed to be compatible with them for future scalability.  
* **Package Organization**: The repository is logically divided into directories for rule\_cards, tools, dist (compiled output), ci configurations, and docs. This provides a clear separation of concerns.

### **High Level Architecture Diagram**

This diagram illustrates the flow of information and the interaction between the core components of the system.

graph TD  
    subgraph "A. Policy-as-Code Repository (Git)"  
        A1\[rule\_cards/\*.yml\]  
        A2\[tools/agents\_manifest.yml\]  
    end

    subgraph "B. Build-Time Compiler (Python)"  
        B1\[tools/compile\_agents.py\]  
        A1 \--\> B1  
        A2 \--\> B1  
        B1 \--\> B2\[dist/agents/\*.json\]  
    end

    subgraph "C. Developer IDE (Inner Loop)"  
        C1\[Agentic Platform \- e.g., Claude Code\]  
        B2 \-- Loads \--\> C1  
        C2\[Developer's Code\]  
        C1 \-- Provides Guidance \--\> C2  
    end  
      
    subgraph "D. Local & CI/CD Validation (Outer Loops)"  
        D1\[Local Machine / CI Runner\]  
        C2 \-- Pre-Commit or Push \--\> D1  
        D1 \-- Runs \--\> D2\[CI Scanners \- Semgrep, Trivy, etc.\]  
        B2 \-- Informs \--\> D2  
        D2 \-- Reports Status \--\> D1  
    end

### **Architectural Patterns**

The system's design is guided by several key architectural patterns that ensure its effectiveness, maintainability, and trustworthiness.

* **Policy-as-Code**: The single source of truth for all security rules is human-readable, version-controlled YAML files. This provides auditability, transparency, and allows security policy to be managed with the same rigor as application code.  
* **Compiled Knowledge (No Runtime RAG)**: To ensure speed, determinism, and simplicity, the system avoids a runtime Retrieval-Augmented Generation (RAG) database for the MVP. Instead, a build-time **compiler** ingests the Rule Cards and produces optimized, self-contained JSON packages for the agents. This is a key pattern for ensuring reliability.  
* **Multi-Loop Feedback**: The architecture creates three distinct but perfectly synchronized feedback loops that provide a consistent experience for the developer:  
  1. **Inner Loop (Real-time IDE Guidance)**: Provides immediate, "just-in-time" security advice from the GenAI agent as the developer is writing code.  
  2. **Local Outer Loop (Pre-Commit Validation)**: Allows the developer to manually run the full suite of security scanners on their local machine before committing. This is a "post-code, pre-push" check that validates the changes against the full policy set.  
  3. Formal Outer Loop (CI/CD Validation): The automated, authoritative gate that runs the same scanners in the CI/CD pipeline upon a pull request.  
     Because all three loops are powered by the same compiled knowledge base, the feedback is guaranteed to be consistent, which is crucial for building developer trust.  
* **Human-in-the-Loop Governance**: The entire system is governed by human experts (Leo, the AppSec Engineer). The AI agents are enforcers of human-defined policy, not autonomous decision-makers. All rule changes are subject to a Git-based peer review process.

## **Tech Stack**

This section defines the specific technologies, frameworks, and tools that will be used to build and operate the system. These choices are definitive for the MVP.

| Category | Technology | Version | Purpose | Rationale |
| :---- | :---- | :---- | :---- | :---- |
| **Language** | Python | 3.11+ | Rule Card compiler & validator scripts. | Simplicity, strong ecosystem for YAML/JSON, and common in security tooling. |
| **Dependency Mgmt** | Pip | latest | Python package management. | Standard for Python, defined in requirements.txt. |
| **LLM Orchestration** | Model-Agnostic | N/A | Core logic for agent runtime. | Allows flexibility to swap models (e.g., Claude, GPT) for generation vs. critique. |
| **Primary LLM** | Anthropic Claude | Sonnet/Opus | Core GenAI model for guidance generation. | Strong performance on coding and reasoning tasks; specified as primary target. |
| **Code Scanning (SAST)** | Semgrep | latest | Static analysis for application code. | Highly configurable, fast, supports many languages, and can use custom rules. |
| **Code Scanning (SAST)** | CodeQL | latest | Deep static analysis for security vulnerabilities. | Excellent for finding complex, data-flow related bugs. Provides defense-in-depth. |
| **Secrets Scanning** | TruffleHog | latest | Scans Git history and files for secrets. | Chosen for its ability to validate the authenticity of found secrets, reducing false positives. |
| **Container Scanning** | Hadolint & Dockle | latest | Dockerfile linting and best practice checks. | Provides immediate, actionable feedback on Dockerfile security. |
| **IaC & SBOM Scanning** | Checkov | latest | Scans Infrastructure-as-Code files (Terraform, etc.) and SBOMs. | Comprehensive policy-as-code checker for cloud security and configurations. |
| **CI/CD Platform** | GitHub Actions | v2 | Automation for compilation and validation. | Ubiquitous, well-documented, and tightly integrated with the source code repository. |

## **Data Models**

The entire system revolves around a single, critical data model: the **Rule Card**. This is the structured, version-controlled representation of a single, atomic security requirement. It is the source of truth for both the AI-powered guidance and the deterministic CI/CD validation.

### **Rule Card**

**Purpose:** To encode a specific security requirement in a format that is both human-readable (in YAML) and machine-readable (when compiled to JSON). Each Rule Card is self-contained and provides all the necessary information for an agent to provide guidance and a CI/CD pipeline to perform validation.

**Key Attributes:**

* **id**: A unique, human-readable identifier (e.g., DOCKER-USER-001).  
* **title**: A concise, descriptive title for the rule.  
* **scope**: Defines the context where the rule applies (e.g., dockerfile, backend:java).  
* **requirement**: The normative statement of what must be achieved.  
* **do / dont**: Simple, actionable lists of best practices and anti-patterns.  
* **detect**: The crucial machine-readable section that maps the rule to specific scanner configurations. This is the lynchpin for consistent validation.  
* **verify**: A list of human-readable test cases to confirm the rule is met.  
* **refs**: Traceability links to external standards like ASVS or OWASP Cheat Sheets.

TypeScript Interface (for Agent Runtime):  
This interface defines the structure of a "reduced" rule as it exists within the compiled agent package.  
// The machine-readable structure of a single security rule within a compiled agent package.  
interface RuleCard {  
  id: string;  
  title: string;  
  severity: 'low' | 'medium' | 'high' | 'critical';  
  scope: string;  
  requirement: string;  
  do: string\[\];  
  dont: string\[\];  
  detect: {  
    \[tool: string\]: string\[\]; // e.g., { "semgrep": \["java-jwt-missing-exp"\] }  
  };  
  verify: {  
    tests: string\[\];  
  };  
  refs: {  
    \[standard: string\]: string\[\]; // e.g., { "asvs": \["V2.1.5"\] }  
  };  
}

## **API Specification**

The system does not have a traditional REST or GraphQL API. Instead, its primary interface is the schema of the **Compiled Agent Package** (agent.\<id\>.json). This JSON file serves as the data contract between the build-time compiler and the agentic runtime. The agent runtime is the client, and the compiled package is the data payload.

### **Compiled Agent Package Schema**

This schema defines the complete structure of the JSON files located in the /dist/agents/ directory.

// Defines the complete data contract for a compiled sub-agent package.  
interface CompiledAgentPackage {  
  // \--- Metadata \---  
  id: string; // Unique identifier, e.g., "agent.jwt.java"  
  name: string; // Human-friendly name  
  version: string; // Build version, e.g., "2025.08.29"  
  build\_date: string; // ISO 8601 timestamp of the build  
  source\_digest: string; // SHA256 hash of all source Rule Cards  
  attribution: string; // License and attribution notice

  // \--- Policy & Configuration \---  
  policy: {  
    targets: string\[\]; // Glob patterns for target files, e.g., \["\*\*/\*.java"\]  
    defaults: { \[key: string\]: any }; // Default values, e.g., { "jwt\_ttl\_seconds": 900 }  
  };

  // \--- Rule Data \---  
  rules: string\[\]; // A list of all Rule Card IDs included in this package  
  rules\_detail: RuleCard\[\]; // The full, detailed content of each Rule Card (see Data Models)

  // \--- Validation Hooks \---  
  validation\_hooks: {  
    \[tool: string\]: string\[\]; // Aggregated map of all scanner rules, e.g., { "semgrep": \["rule1", "rule2"\] }  
  };  
}

## **Components**

The system is composed of four primary logical components. Each component has a distinct responsibility and a well-defined interface for interacting with the others.

### **1\. Policy-as-Code Repository**

* **Responsibility:** To serve as the single source of truth for all security rules and agent configurations. This component is the human interface for the security team (Leo).  
* **Key Interfaces:**  
  * **Input:** Manual creation and editing of YAML Rule Cards (/rule\_cards/) and the agents\_manifest.yml via Git.  
  * **Output:** Version-controlled YAML files that are consumed by the Compiler.  
* **Dependencies:** None. This is the foundational component.  
* **Technology Stack:** Git, YAML.

### **2\. Rule Card Compiler**

* **Responsibility:** To perform the build-time transformation of human-readable YAML Rule Cards into machine-readable, versioned JSON packages. It is a critical offline process that ensures the runtime components are fast and deterministic.  
* **Key Interfaces:**  
  * **Input:** Reads all YAML files from the Policy-as-Code Repository.  
  * **Output:** Writes compiled agent.\<id\>.json packages to the /dist/agents/ directory.  
* **Dependencies:** Policy-as-Code Repository.  
* **Technology Stack:** Python, PyYAML.

### **3\. Agentic Runtime & Router**

* **Responsibility:** To provide real-time, "just-in-time" security guidance to developers. This component lives within the developer's agentic IDE (e.g., Claude Code).  
* **Key Interfaces:**  
  * **Input:** Consumes the developer's current code context (file path, content) and loads the relevant compiled agent JSON package.  
  * **Output:** Generates natural language guidance and secure code suggestions for the developer.  
* **Dependencies:** Compiled Agent Packages.  
* **Technology Stack:** Model-Agnostic LLM Orchestration, Anthropic Claude.

### **4\. CI/CD Validation Engine**

* **Responsibility:** To provide the deterministic "post-code" validation gate in the CI/CD pipeline. It enforces the policy defined in the Rule Cards.  
* **Key Interfaces:**  
  * **Input:** Consumes the developer's committed code and the relevant compiled agent JSON package (specifically the validation\_hooks).  
  * **Output:** Executes the specified scanners and produces a pass/fail result with a structured report (e.g., SARIF) for the CI/CD system.  
* **Dependencies:** Compiled Agent Packages, Developer's Code.  
* **Technology Stack:** GitHub Actions, Semgrep, CodeQL, TruffleHog, Checkov, Hadolint, Dockle.

## **Core Workflows**

This section illustrates the key operational sequences of the system, corresponding to the "Multi-Loop Feedback" architectural pattern.

### **Workflow 1: Inner Loop \- Real-time IDE Guidance**

This sequence diagram shows the flow of information when a developer receives "just-in-time" security feedback as they are writing code.

sequenceDiagram  
    participant Dev as Developer  
    participant IDE as Agentic IDE (Claude Code)  
    participant Runtime as Agentic Runtime  
    participant LLM as GenAI Model (Claude)

    Dev-\>\>IDE: Writes / Modifies Code  
    IDE-\>\>Runtime: Sends Code Context (file, content)  
    Runtime-\>\>Runtime: Selects relevant Compiled Agent Package  
    Runtime-\>\>LLM: Hydrates and sends secure prompt with rules  
    LLM--\>\>Runtime: Returns guidance / code suggestion  
    Runtime-\>\>IDE: Formats and sends response  
    IDE--\>\>Dev: Displays real-time guidance

### **Workflow 2: Outer Loops \- Local & CI/CD Validation**

This sequence diagram shows the "post-code" validation flow, which is identical whether run manually by a developer pre-commit or automatically by the CI/CD pipeline.

sequenceDiagram  
    participant Dev as Developer  
    participant Runner as Local Machine or CI/CD Runner  
    participant Engine as Validation Engine  
    participant Scanners as Security Scanners (Semgrep, etc.)

    Dev-\>\>Runner: Runs 'git push' or local validation script  
    Runner-\>\>Engine: Invokes Validation Engine  
    Engine-\>\>Engine: Loads relevant Compiled Agent Package  
    Engine-\>\>Scanners: Executes scanners based on 'validation\_hooks'  
    Scanners--\>\>Engine: Return results (e.g., SARIF)  
    Engine-\>\>Runner: Aggregates results and determines pass/fail  
    Runner--\>\>Dev: Reports status (e.g., in PR comment or terminal)

## **Unified Project Structure**

The project will be housed in a single monorepo named genai-sec-agents. This structure organizes the Policy-as-Code assets, the compiler toolchain, and CI/CD configurations logically.

/genai-sec-agents/  
|  
├── .github/  
│   └── workflows/  
│       └── security.yml      \# Main CI/CD validation pipeline  
|  
├── rule\_cards/               \# Human-readable "single source of truth" for rules  
│   ├── docker/\*.yml  
│   ├── jwt/java/\*.yml  
│   ├── authn/\*.yml  
│   └── shared/\*.yml  
|  
├── tools/                      \# The compiler and validation toolchain  
│   ├── compile\_agents.py  
│   ├── validate\_cards.py  
│   └── agents\_manifest.yml  
|  
├── dist/                       \# Compiled, distributable agent packages  
│   └── agents/  
│       └── \*.json  
|  
├── ci/                         \# Configurations for CI scanners  
│   ├── semgrep-rules/  
│   └── conftest-policies/  
|  
├── policy/  
│   └── thresholds.yml          \# Policy for CI gates (e.g., fail on High sev)  
|  
├── docs/                       \# Project documentation  
│   ├── ATTRIBUTION.md  
│   ├── SECURITY\_GUIDE.md  
│   ├── architecture.md  
│   └── prd.md  
|  
├── Makefile                    \# Helper scripts for local development  
├── requirements.txt            \# Python dependencies for the toolchain  
└── README.md

## **Development Workflow**

This section outlines the process for local development, from initial setup to running the core scripts.

### **1\. Prerequisites**

* Python 3.11+  
* pip and venv  
* Git

### **2\. Initial Setup**

The entire setup process is managed via the Makefile.

\# 1\. Clone the repository  
git clone \<repository\_url\> genai-sec-agents  
cd genai-sec-agents

\# 2\. Create virtual environment and install dependencies  
make  




### **3\. Core Local Commands**

* **make validate**: Runs the validate\_cards.py script to ensure all Rule Cards in /rule\_cards are well-formed and adhere to the schema. This should be run before committing any changes to rules.  
* **make compile**: Runs the validation step and then executes the compile\_agents.py script to build the final JSON packages in /dist/agents.  
* **make clean**: Removes the compiled agent packages from the /dist directory.

---

## **Deployment Architecture**

The system has two main deployment artifacts: the **Rule Card Repository** itself and the **Compiled Agent Packages**.

### **1\. Rule Card Repository Deployment**

The repository is not "deployed" in a traditional sense. Its lifecycle is managed entirely through Git.

* **Updates**: All changes to rules are proposed via Pull Requests, which must be reviewed and approved by the AppSec team (Leo).  
* **Versioning**: Git tags will be used to create official, versioned releases of the rule set (e.g., v1.0, v1.1).

### **2\. Compiled Agent Package Deployment**

The compiled JSON packages in /dist/agents/ are the deployable artifacts.

* **CI/CD Pipeline**: A GitHub Actions workflow (.github/workflows/release.yml) will be created to automate the compilation and release process.  
* **Trigger**: The release workflow will be triggered upon the creation of a new Git tag.  
* **Process**:  
  1. The workflow validates and compiles the Rule Cards using make compile.  
  2. The compiled JSON files in /dist/agents/ are packaged.  
  3. These packages are published as release artifacts to a secure object store (e.g., a versioned S3 bucket or GitHub Releases).  
* **Consumption**: The Agentic Runtime in the developer's IDE will be configured to pull the latest version of the compiled packages from this secure location.

### **3\. Environments**

* **Development**: The Git repository itself, where rules are authored and tested locally.  
* **Production**: The secure object store where the versioned, compiled JSON packages are hosted for consumption by agents.

---

## **Cross-Cutting Concerns**

### **1\. Security Strategy**

The security of this system is paramount. The strategy is detailed in the docs/mitigations.md document and is based on the threat model. Key principles include:

* **Integrity**: Ensuring the Rule Cards are from trusted sources and cannot be tampered with (via hash validation, PR reviews).  
* **Sandboxing**: The agent runtime and CI scanners must operate in least-privilege, isolated environments to contain their blast radius.  
* **Traceability**: All actions and rule changes must be auditable via Git history and CI logs.

### **2\. Performance Strategy**

* **Agent Latency**: The primary performance goal is to meet **NFR1**, ensuring the IDE agent responds in under 2 seconds. The "Compiled Knowledge" pattern is key to achieving this by avoiding slow, real-time database lookups.  
* **Compiler Performance**: The Python compiler scripts should be optimized to run efficiently within the CI/CD pipeline, ideally completing in under 60 seconds for the full ruleset.

### **3\. Testing Strategy**

The testing strategy follows the "Multi-Loop Feedback" pattern:

* **Unit Tests**: The Python toolchain (compile\_agents.py, validate\_cards.py) will have comprehensive unit tests.  
* **Integration Tests**: The primary integration test is the CI/CD pipeline itself, which validates that the compiled validation\_hooks correctly trigger the scanners.  
* **End-to-End Testing (Evaluation)**: As outlined in the project plan, the system will be tested against deliberately vulnerable applications (e.g., OWASP Juice Shop) to measure the end-to-end effectiveness of the guidance and validation loop.