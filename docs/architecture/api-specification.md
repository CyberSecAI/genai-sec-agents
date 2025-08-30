# **API Specification**

The system does not have a traditional REST or GraphQL API. Instead, its primary interface is the schema of the **Compiled Agent Package** (agent.\<id\>.json). This JSON file serves as the data contract between the build-time compiler and the agentic runtime. The agent runtime is the client, and the compiled package is the data payload.

## **Compiled Agent Package Schema**

This schema defines the complete structure of the JSON files located in the /dist/agents/ directory.

```typescript
// Defines the complete data contract for a compiled sub-agent package.  
interface CompiledAgentPackage {  
  // --- Metadata ---  
  id: string; // Unique identifier, e.g., "agent.jwt.java"  
  name: string; // Human-friendly name  
  version: string; // Build version, e.g., "2025.08.29"  
  build_date: string; // ISO 8601 timestamp of the build  
  source_digest: string; // SHA256 hash of all source Rule Cards  
  attribution: string; // License and attribution notice

  // --- Policy & Configuration ---  
  policy: {  
    targets: string[]; // Glob patterns for target files, e.g., ["**/*.java"]  
    defaults: { [key: string]: any }; // Default values, e.g., { "jwt_ttl_seconds": 900 }  
  };

  // --- Rule Data ---  
  rules: string[]; // A list of all Rule Card IDs included in this package  
  rules_detail: RuleCard[]; // The full, detailed content of each Rule Card (see Data Models)

  // --- Validation Hooks ---  
  validation_hooks: {  
    [tool: string]: string[]; // Aggregated map of all scanner rules, e.g., { "semgrep": ["rule1", "rule2"] }  
  };  
}
```
