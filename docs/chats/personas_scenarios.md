## **User Personas (Updated)**

### **Daniella the Deadline-Driven Developer**

**Archetype:** A skilled software engineer focused on shipping features quickly and reliably. She values tools that provide **just-in-time, actionable guidance** directly within her workflow.

**About:** Daniella is a mid-level developer on a product team. Her primary job is to turn user stories into functional code. She lives in her IDE and Git, and her goal is to write secure code from the start without having to hunt through static documentation.

**Goals (What do I want to achieve?):**
* Get clear, actionable, and immediate feedback **as I'm coding**.
* Fix security vulnerabilities quickly with trusted code suggestions based on **both industry standards and internal lessons**.
* Avoid having my pull requests blocked by **post-code CI checks** for issues I could have fixed earlier.

**Frustrations / Pain Points (What's stopping me?):**
* Security guidance is often abstract or lives in a wiki I don't have time to read.
* It's frustrating when security requirements feel like a bureaucratic checklist instead of an integrated part of my workflow.
* CI/CD pipelines that flag issues hours after I've moved on to a new task force expensive context switching.

---

### **Leo the Lead AppSec Engineer**

**Archetype:** A security professional who scales his expertise by **codifying security policy** and creating a **human-governed, AI-powered** security program.

**About:** Leo is the sole Application Security engineer for several development teams. His mission is to turn passive policy documents into active, automated guardrails, allowing the GenAI agents to handle the baseline while he focuses on emerging threats.

**Goals (What do I want to achieve?):**
* **Codify our security standards** into executable rules that developers can't ignore.
* Translate findings from past incidents and penetration tests into **a hybrid knowledge base** of automated, preventative controls.
* Act as the **human governor** of the security program, defining the rules that the AI agents will enforce.
* Free up my time to focus on high-level architectural reviews and threat modeling.

**Frustrations / Pain Points (What's stopping me?):**
* Writing security policies that end up as "shelf-ware" that developers never read.
* The lessons learned from a security incident are forgotten after a few months.
* It's impossible to manually review every line of code to ensure compliance with our standards.

---

### **Sara the SRE & Pipeline Architect**

**Archetype:** A platform engineer who owns the CI/CD infrastructure. Her priority is a fast, reliable pipeline that provides a deterministic **post-code validation** gate based on a clear, **codified policy**.

**About:** Sara manages the CI/CD pipelines that build and deploy all applications. She ensures that the build process is not just a feature factory but a reliable quality gate that **executes the company's security policy as code**.

**Goals (What do I want to achieve?):**
* Integrate a comprehensive security gate that reliably **validates code against the codified policy**.
* Ensure the CI/CD feedback is fast and directly mirrors the **just-in-time guidance** developers see in their IDE.
* Automate the collection of security evidence and attestations for compliance.

**Frustrations / Pain Points (What's stopping me?):**
* Stitching together multiple scanners is brittle and leads to inconsistent feedback.
* When a build fails with a cryptic security error, it undermines developer trust in the pipeline.
* Security tools that aren't perfectly in sync with the development environment create confusion and friction.

***

## **User Scenarios**

### **Fixing a Vulnerability Before It's Written**

**Persona:** Daniella the Deadline-Driven Developer

**Illustrates:** **#1 (Just-in-Time Guidance)** & **#3 (Hybrid Knowledge Base)**

**Narrative:**
* **Pre-Narrative (The World Today):** "I need to add a file upload feature. I write the code, push it, and two hours later, the CI build fails with a vague SAST alert. I have to stop everything, dig through the logs, and then search online for the right way to validate files in Spring Boot. It's a huge waste of time."
* **Post-Narrative (The Aspirational Future):** "As I'm writing the file upload code, the **GenAI Security Agent** in my IDE highlights the line. A tooltip appears: '**[INTERNAL-RULE-042] Unvalidated file uploads match the pattern from the Q3-Acme-Breach. All uploads must be validated against an approved MIME type list.**' It suggests a secure code snippet that uses our company's standard validation library. I accept the change in seconds. I know that if I had ignored this, the **post-code CI validator** would have blocked my PR with the exact same 'INTERNAL-RULE-042' error, because the IDE and pipeline are using the same **codified policy**."

---

### **Turning a Pen Test Finding into an Automated Guardrail**

**Persona:** Leo the Lead AppSec Engineer

**Illustrates:** **#2 (Policy as Code)**, **#3 (Hybrid Knowledge Base)**, & **#4 (Human-Governed, AI-Powered)**

**Narrative:**
* **Pre-Narrative (The World Today):** "Our last penetration test found a critical Insecure Direct Object Reference (IDOR) flaw. I wrote a detailed report, sent an email to all engineering leads, and updated our Confluence page. Six months from now, I'll probably find the same bug in a new service because nobody has time to read the old reports."
* **Post-Narrative (The Aspirational Future):** "After the pen test, I open our security agent repository. I create a new rule card: `id: IDOR-AUTHZ-001`, `title: "Verify resource ownership in user-facing endpoints"`. I add a detection pattern based on the pen test report's proof-of-concept and link it to ASVS V4.1.1. I've just **codified the lesson from our internal intel into an executable policy**. Now, the **AI agents** act as my enforcement fleet. Any developer writing an API endpoint that fits this risky pattern will get an immediate, **just-in-time** warning and a secure code snippet. I've acted as the **human governor** to permanently prevent an entire class of vulnerability from recurring."

---

### **Providing Clear, Consistent Pipeline Feedback**

**Persona:** Sara the SRE & Pipeline Architect

**Illustrates:** **#1 (Post-Code Validation)** & **#2 (Policy as Code)**

**Narrative:**
* **Pre-Narrative (The World Today):** "A developer's build failed with a non-zero exit code from our security scanner. They're asking me why. I have to dig through text logs from three different tools to piece together the reason. The developer is blocked, and I'm pulled into debugging a tool instead of improving the platform."
* **Post-Narrative (The Aspirational Future):** "A developer's build failed today. The process was seamless. The PR was automatically commented: '**Build failed: Post-Code Validation blocked by 1 critical policy violation.**' The finding was '**[IDOR-AUTHZ-001]** Endpoint `/api/documents/{id}` does not appear to verify resource ownership.' The message linked directly to the **codified rule** Leo wrote last month. The developer knew exactly what to do because it's the same rule the agent in their IDE is based on. They fixed it and the build passed 10 minutes later, without ever needing my help. The pipeline is now a perfect executor of our **security policy as code**."