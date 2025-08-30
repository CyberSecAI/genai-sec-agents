# **Development Workflow**

This section outlines the process for local development, from initial setup to running the core scripts.

## **1\. Prerequisites**

* Python 3.11+  
* pip and venv  
* Git

## **2\. Initial Setup**

The entire setup process is managed via the Makefile.

\# 1\. Clone the repository  
git clone \<repository\_url\> genai-sec-agents  
cd genai-sec-agents

\# 2\. Create virtual environment and install dependencies  
make  




## **3\. Core Local Commands**

* **make validate**: Runs the validate\_cards.py script to ensure all Rule Cards in /rule\_cards are well-formed and adhere to the schema. This should be run before committing any changes to rules.  
* **make compile**: Runs the validation step and then executes the compile\_agents.py script to build the final JSON packages in /dist/agents.  
* **make clean**: Removes the compiled agent packages from the /dist directory.

---
