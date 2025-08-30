# **Rule Management & Governance Workflow**

The primary interface for managing the security knowledge base is not a traditional GUI, but rather a **Policy-as-Code** workflow centered around a Git repository and a command-line toolchain. This approach provides maximum efficiency, auditability, and precision for expert users like Leo (AppSec Engineer) and Charlotte (CISO).

## **Core Principles**

* **Policy-as-Code (GitOps Model):** The "single source of truth" for all security rules is a collection of human-readable YAML files ("Rule Cards") stored in a dedicated Git repository. This is the primary interface for managing policy.  
* **Git-Based Versioning and Audit:** All changes to Rule Cards—creations, edits, deactivations—are managed through standard Git workflows (branches, pull requests, reviews, merges). This provides a complete, immutable, and auditable history of every policy change, directly satisfying **FR7**.  
* **Automated Compilation:** A command-line compiler script (compile\_agents.py) transforms the human-readable YAML Rule Cards into structured, machine-readable JSON packages. These compiled packages are the artifacts used by the GenAI agents at runtime, ensuring there is no need for a live RAG database in the MVP.

## **Workflow Components**

* **Rule Card Directory (/rule\_cards/):** The main workspace for Leo. AppSec engineers will create and edit YAML files in this directory. The structure is organized by security domain (e.g., /docker/, /jwt/java/) for clarity.  
* **Agent Manifest (tools/agents\_manifest.yml):** The high-level configuration file where Leo defines the different sub-agents and maps which Rule Card topics belong to each one.  
* **Validation & Compilation Toolchain (tools/):** A set of Python scripts that provide the core engine for the system:  
  * validate\_cards.py: A script to validate all Rule Cards against the required schema (**FR8**).  
  * compile\_agents.py: The script that reads the manifest, collects the relevant Rule Cards, and builds the final JSON packages for the agents.  
* **Compiled Agent Packages (/dist/agents/):** The output directory containing the final, versioned JSON artifacts that are consumed by the GenAI agents. This separation of source (YAML) from compiled output (JSON) is a key architectural principle.
