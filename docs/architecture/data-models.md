# **Data Models**

The entire system revolves around a single, critical data model: the **Rule Card**. This is the structured, version-controlled representation of a single, atomic security requirement. It is the source of truth for both the AI-powered guidance and the deterministic CI/CD validation.

## **Rule Card**

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

```typescript
// The machine-readable structure of a single security rule within a compiled agent package.  
interface RuleCard {  
  id: string;  
  title: string;  
  severity: 'low' | 'medium' | 'high' | 'critical';  
  scope: string;  
  requirement: string;  
  do: string[];  
  dont: string[];  
  detect: {  
    [tool: string]: string[]; // e.g., { "semgrep": ["java-jwt-missing-exp"] }  
  };  
  verify: {  
    tests: string[];  
  };  
  refs: {  
    [standard: string]: string[]; // e.g., { "asvs": ["V2.1.5"] }  
  };  
}
```
