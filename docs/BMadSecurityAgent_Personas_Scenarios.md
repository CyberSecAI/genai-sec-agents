# **BMad Security Agent \- Project Overview**

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

### **Charlotte the Strategic CISO**

**Archetype:** A senior executive focused on managing risk and ensuring the organization's security program is auditable and aligned with industry frameworks.

**About:** Charlotte is the Chief Information Security Officer, responsible for the overall security posture of the company. She must demonstrate to auditors, regulators, and the board that the company has a mature and effective security program.

**Goals (What do I want to achieve?):**

* Ensure the company's security policies are **consistently enforced** across all development teams.  
* Have a clear, **auditable trail** that maps internal security rules to recognized industry frameworks (like ASVS, NIST SSDF).  
* Reduce the organization's risk profile by **preventing entire classes** of common vulnerabilities.  
* Report on the **effectiveness and ROI** of the security program to the board.

**Frustrations / Pain Points (What's stopping me?):**

* It's difficult to **prove** that security policies are actually being followed in code.  
* **Audits** are a painful, manual process of collecting evidence from disparate systems.  
* Security tools produce a lot of noise, making it hard to see the **real risk trends**.  
* It's a constant battle to show the value of security investments beyond just "preventing bad things."

### **Priya the Pragmatic Product Manager**

**Archetype:** A product leader focused on a predictable roadmap and efficient delivery. She sees security as a critical quality attribute that must be a predictable part of the development process, not a last-minute surprise.

**About:** Priya translates business goals into a prioritized backlog. Her success is measured by her ability to ship value to customers on a predictable schedule. Security is a key requirement, but it must be managed efficiently to prevent it from derailing sprint commitments and release timelines.

**Goals (What do I want to achieve?):**

* Maintain a **predictable and fast development velocity**.  
* **Prevent last-minute security surprises** that block releases and derail sprints.  
* Make security a **transparent and estimable part** of every user story.  
* Confidently forecast release timelines without security being a constant unknown variable.

**Frustrations / Pain Points (What's stopping me?):**

* Critical security findings that emerge *after* a feature is functionally "done," forcing painful rework and delaying releases.  
* The "security tax" on every story feels unpredictable and difficult to estimate during sprint planning.  
* Having to explain to stakeholders why a release is delayed due to a preventable security issue that should have been caught weeks earlier.

## **User Scenarios**

### **Fixing a Vulnerability Before It's Written**

**Persona:** Daniella the Deadline-Driven Developer

**Illustrates:** **\#1 (Just-in-Time Guidance)** & **\#3 (Hybrid Knowledge Base)**

**Narrative:**

* **Pre-Narrative (The World Today):** "I need to add a file upload feature. I write the code, push it, and two hours later, the CI build fails with a vague SAST alert. I have to stop everything, dig through the logs, and then search online for the right way to validate files in Spring Boot. It's a huge waste of time."  
* **Post-Narrative (The Aspirational Future):** "As I'm writing the file upload code, the **GenAI Security Agent** in my IDE highlights the line. A tooltip appears: 'INTERNAL−RULE−042  
  Unvalidated file uploads match the pattern from the Q3-Acme-Breach. All uploads must be validated against an approved MIME type list.' It suggests a secure code snippet that uses our company's standard validation library. I accept the change in seconds. I know that if I had ignored this, the **post-code CI validator** would have blocked my PR with the exact same 'INTERNAL-RULE-042' error, because the IDE and pipeline are using the same **codified policy**."

### **Turning a Pen Test Finding into an Automated Guardrail**

**Persona:** Leo the Lead AppSec Engineer

**Illustrates:** **\#2 (Policy as Code)**, **\#3 (Hybrid Knowledge Base)**, & **\#4 (Human-Governed, AI-Powered)**

**Narrative:**

* **Pre-Narrative (The World Today):** "Our last penetration test found a critical Insecure Direct Object Reference (IDOR) flaw. I wrote a detailed report, sent an email to all engineering leads, and updated our Confluence page. Six months from now, I'll probably find the same bug in a new service because nobody has time to read the old reports."  
* **Post-Narrative (The Aspirational Future):** "After the pen test, I open our security agent repository. I create a new rule card: id: IDOR-AUTHZ-001, title: "Verify resource ownership in user-facing endpoints". I add a detection pattern based on the pen test report's proof-of-concept and link it to ASVS V4.1.1. I've just **codified the lesson from our internal intel into an executable policy**. Now, the **AI agents** act as my enforcement fleet. Any developer writing an API endpoint that fits this risky pattern will get an immediate, **just-in-time** warning and a secure code snippet. I've acted as the **human governor** to permanently prevent an entire class of vulnerability from recurring."

### **Providing Clear, Consistent Pipeline Feedback**

**Persona:** Sara the SRE & Pipeline Architect

**Illustrates:** **\#1 (Post-Code Validation)** & **\#2 (Policy as Code)**

**Narrative:**

* **Pre-Narrative (The World Today):** "A developer's build failed with a non-zero exit code from our security scanner. They're asking me why. I have to dig through text logs from three different tools to piece together the reason. The developer is blocked, and I'm pulled into debugging a tool instead of improving the platform."  
* **Post-Narrative (The Aspirational Future):** "A developer's build failed today. The process was seamless. The PR was automatically commented: '**Build failed: Post-Code Validation blocked by 1 critical policy violation.**' The finding was 'IDOR−AUTHZ−001  
  Endpoint /api/documents/{id} does not appear to verify resource ownership.' The message linked directly to the **codified rule** Leo wrote last month. The developer knew exactly what to do because it's the same rule the agent in their IDE is based on. They fixed it and the build passed 10 minutes later, without ever needing my help. The pipeline is now a perfect executor of our **security policy as code**."

### **Proving Compliance to Auditors in Minutes**

**Persona:** Charlotte the Strategic CISO

**Illustrates:** The value of a codified, traceable, and standards-aligned security policy.

**Narrative:**

* **Pre-Narrative (The World Today):** "An auditor is asking for proof that we're complying with ASVS V4.2.1 across our 50 microservices. My team now has to spend the next two weeks manually gathering code samples, running ad-hoc scans, and trying to map our internal policies to the ASVS standard in a giant spreadsheet. It's a nightmare, and the evidence is always incomplete."  
* **Post-Narrative (The Aspirational Future):** "An auditor asks for our ASVS V4.2.1 compliance. I go to our security agent's dashboard. I filter for all the rule cards tagged with 'ASVS-V4.2.1'. It shows me a list of the internal rules we've codified that map to this standard. I can click on any rule (like 'IDOR-AUTHZ-001') and see that it has been enforced in 100% of our production builds over the last quarter, with links to the CI/CD logs that prove it. The audit evidence is generated in minutes, not weeks. I can confidently report to the board that our security program is not just a policy document; it's a living, auditable, and automated system."

### **Keeping the Sprint on Track and Predictable**

**Persona:** Priya the Pragmatic Product Manager

**Illustrates:** How shifting security left makes delivery velocity predictable.

**Narrative:**

* **Pre-Narrative (The World Today):** "My team finished all their stories for the sprint and we marked the feature as 'Done'. But during the release scan, a critical vulnerability was found. The release is now blocked, the story has to be pulled back into the next sprint for rework, and my entire release forecast is off. I have to explain to stakeholders why we're delayed by a problem we should have caught weeks ago."  
* **Post-Narrative (The Aspirational Future):** "My team is wrapping up the sprint. The developer, Daniella, fixed a potential IDOR vulnerability in her story in minutes because the IDE agent flagged it and gave her a secure code snippet. The CI/CD check, which uses the same rule, passed on the first commit. When the story moves to 'Done,' it's truly done. Security is no longer a last-minute surprise. My release forecasts are accurate, and I can confidently tell stakeholders that we're shipping a secure feature on schedule."