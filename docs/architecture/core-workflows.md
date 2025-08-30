# **Core Workflows**

This section illustrates the key operational sequences of the system, corresponding to the "Multi-Loop Feedback" architectural pattern.

## **Workflow 1: Inner Loop \- Real-time IDE Guidance**

This sequence diagram shows the flow of information when a developer receives "just-in-time" security feedback as they are writing code.

```mermaid
sequenceDiagram  
    participant Dev as Developer  
    participant IDE as Agentic IDE (Claude Code)  
    participant Runtime as Agentic Runtime  
    participant LLM as GenAI Model (Claude)

    Dev->>IDE: Writes / Modifies Code  
    IDE->>Runtime: Sends Code Context (file, content)  
    Runtime->>Runtime: Selects relevant Compiled Agent Package  
    Runtime->>LLM: Hydrates and sends secure prompt with rules  
    LLM-->>Runtime: Returns guidance / code suggestion  
    Runtime->>IDE: Formats and sends response  
    IDE-->>Dev: Displays real-time guidance
```

## **Workflow 2: Outer Loops \- Local & CI/CD Validation**

This sequence diagram shows the "post-code" validation flow, which is identical whether run manually by a developer pre-commit or automatically by the CI/CD pipeline.

```mermaid
sequenceDiagram  
    participant Dev as Developer  
    participant Runner as Local Machine or CI/CD Runner  
    participant Engine as Validation Engine  
    participant Scanners as Security Scanners (Semgrep, etc.)

    Dev->>Runner: Runs 'git push' or local validation script  
    Runner->>Engine: Invokes Validation Engine  
    Engine->>Engine: Loads relevant Compiled Agent Package  
    Engine->>Scanners: Executes scanners based on 'validation_hooks'  
    Scanners-->>Engine: Return results (e.g., SARIF)  
    Engine->>Runner: Aggregates results and determines pass/fail  
    Runner-->>Dev: Reports status (e.g., in PR comment or terminal)
```
