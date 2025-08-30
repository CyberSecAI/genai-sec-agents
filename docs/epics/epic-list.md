# **Epic List**

The work required to deliver the MVP will be organized into the following logically sequenced epics. Each epic delivers a significant, deployable increment of value.

* **Epic 1: The Policy-as-Code Engine:** This foundational epic delivers the core value for the AppSec Engineer (Leo). It establishes the Git-based workflow for managing Rule Cards, **includes the manual ingestion and creation of the initial set of Rule Cards from key internal and external sources**, and provides the toolchain to validate and compile them into agent-ready packages. This epic creates the "brain" of our system and populates it with its initial knowledge.  
* **Epic 2: IDE Agent Integration (Claude Code MVP):** This epic focuses on delivering the "just-in-time" guidance for the Developer (Daniella). It involves building the agentic component that consumes the compiled packages from Epic 1 and integrates with our primary target platform, Claude Code, to provide real-time feedback.  
* **Epic 3: CI/CD Advisory Integration:** This epic delivers the value for the SRE (Sara) and closes the loop on consistency. It focuses on integrating the compiled security rules into the CI/CD pipeline in a non-blocking, advisory mode. This provides the deterministic "post-code validation" gate and generates the reports needed by the CISO (Charlotte) and PM (Priya).
