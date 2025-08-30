# **Deployment Architecture**

The system has two main deployment artifacts: the **Rule Card Repository** itself and the **Compiled Agent Packages**.

## **1\. Rule Card Repository Deployment**

The repository is not "deployed" in a traditional sense. Its lifecycle is managed entirely through Git.

* **Updates**: All changes to rules are proposed via Pull Requests, which must be reviewed and approved by the AppSec team (Leo).  
* **Versioning**: Git tags will be used to create official, versioned releases of the rule set (e.g., v1.0, v1.1).

## **2\. Compiled Agent Package Deployment**

The compiled JSON packages in /dist/agents/ are the deployable artifacts.

* **CI/CD Pipeline**: A GitHub Actions workflow (.github/workflows/release.yml) will be created to automate the compilation and release process.  
* **Trigger**: The release workflow will be triggered upon the creation of a new Git tag.  
* **Process**:  
  1. The workflow validates and compiles the Rule Cards using make compile.  
  2. The compiled JSON files in /dist/agents/ are packaged.  
  3. These packages are published as release artifacts to a secure object store (e.g., a versioned S3 bucket or GitHub Releases).  
* **Consumption**: The Agentic Runtime in the developer's IDE will be configured to pull the latest version of the compiled packages from this secure location.

## **3\. Environments**

* **Development**: The Git repository itself, where rules are authored and tested locally.  
* **Production**: The secure object store where the versioned, compiled JSON packages are hosted for consumption by agents.

---
