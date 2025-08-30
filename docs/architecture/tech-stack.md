# **Tech Stack**

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
