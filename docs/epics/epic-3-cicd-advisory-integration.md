# **Epic 3: CI/CD Advisory Integration**

**Goal:** To provide a deterministic, trustworthy "post-code validation" gate in the CI/CD pipeline that is 100% consistent with the guidance developers receive in their IDE. This epic closes the feedback loop and provides auditable evidence of policy enforcement for Sara, Charlotte, and Priya.

## **Stories**

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