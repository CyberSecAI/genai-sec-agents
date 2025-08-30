# AgenticRuntime - Security Guidance Engine

The AgenticRuntime is a secure, high-performance system for loading and interpreting compiled security agent packages to deliver context-aware security guidance for IDE integration.

## Overview

The AgenticRuntime provides the foundational infrastructure for delivering "just-in-time" security guidance to developers by:

- **Securely loading** compiled agent packages with comprehensive validation
- **Intelligently selecting** relevant rules based on development context
- **Generating guidance** through model-agnostic LLM interfaces
- **Maintaining security** through multiple layers of validation and sanitization

## Quick Start

### Basic Usage

```python
from app.runtime import AgenticRuntime

# Initialize runtime
runtime = AgenticRuntime()

# Load a specific agent
runtime.load_agent("secrets-specialist")

# Get guidance for code context
context = {
    "file_path": "auth/jwt_handler.py",
    "content": "JWT_SECRET = 'hardcoded-secret'",
    "language": "python"
}

guidance = runtime.get_guidance(context)
print(guidance["guidance"])
```

### Auto-Agent Selection

```python
# Let runtime choose the best agent
context = {
    "file_path": "Dockerfile", 
    "content": "FROM ubuntu:latest\nUSER root"
}

guidance = runtime.get_guidance(context)  # Automatically selects container-security-specialist
print(f"Agent used: {guidance['agent_used']}")
print(f"Severity: {guidance['severity']}")
```

## Architecture

### Core Components

1. **AgenticRuntime** (`core.py`) - Main orchestrator and public API
2. **PackageLoader** (`package_loader.py`) - Secure JSON package loading with validation
3. **RuleSelector** (`rule_selector.py`) - Context-aware rule filtering
4. **LLMInterface** (`llm_interface.py`) - Model-agnostic guidance generation

### Security Features

- **Safe JSON parsing** with size limits and malicious payload detection
- **Input sanitization** for all context data and file paths
- **Path traversal prevention** in file operations
- **Information disclosure protection** in error messages and logging
- **Content validation** to prevent prompt injection attacks

## API Reference

### AgenticRuntime

#### `__init__(package_directory="app/dist/agents", debug=False)`

Initialize the runtime with specified package directory.

**Parameters:**
- `package_directory` (str): Path to compiled agent packages
- `debug` (bool): Enable debug logging (warning: may log sensitive data)

#### `load_agent(agent_name: str) -> bool`

Load a compiled agent package by name.

**Parameters:**
- `agent_name` (str): Name of the agent (e.g., 'secrets-specialist')

**Returns:**
- `bool`: True if agent loaded successfully

**Example:**
```python
success = runtime.load_agent("web-security-specialist")
if not success:
    print("Failed to load agent")
```

#### `get_guidance(context: Dict, agent_name: Optional[str] = None) -> Optional[Dict]`

Generate security guidance based on code context.

**Parameters:**
- `context` (Dict): Development context with keys:
  - `file_path` (str): File path being analyzed
  - `content` (str): File content (max 1MB)
  - `language` (str, optional): Programming language
  - `framework` (str, optional): Framework being used
  - `domain` (str, optional): Security domain hint
- `agent_name` (str, optional): Specific agent to use (auto-select if None)

**Returns:**
- `Dict` or `None`: Guidance response with keys:
  - `guidance` (str): Main security guidance text
  - `suggestions` (List[str]): Actionable code improvements
  - `severity` (str): Risk level ('low', 'medium', 'high', 'critical')
  - `agent_used` (str): Name of agent that provided guidance
  - `rules_applied` (int): Number of rules that matched context
  - `confidence` (float): Confidence score (0.0-1.0)

**Example:**
```python
context = {
    "file_path": "api/auth.py",
    "content": "session['user_id'] = user.id",
    "language": "python",
    "framework": "flask"
}

guidance = runtime.get_guidance(context, agent_name="web-security-specialist")

if guidance:
    print(f"Guidance: {guidance['guidance']}")
    print(f"Severity: {guidance['severity']}")
    for suggestion in guidance['suggestions']:
        print(f"- {suggestion}")
```

#### `get_available_agents() -> List[str]`

Get list of available agent packages in the directory.

#### `get_loaded_agents() -> List[str]`

Get list of currently loaded agent names.

#### `unload_agent(agent_name: str) -> bool`

Unload a specific agent from memory.

#### `clear_all_agents() -> None`

Clear all loaded agents from memory.

### Available Agents

The runtime works with compiled agent packages from Story 1.3:

| Agent Name | Domain Focus | Rules Count | Hook Types |
|------------|-------------|-------------|------------|
| `secrets-specialist` | API keys, DB credentials, JWT secrets | 4 | Semgrep, CodeQL, TruffleHog |
| `web-security-specialist` | Cookies, sessions, HTTP security | 7 | Semgrep, CodeQL, TruffleHog |
| `genai-security-specialist` | AI/ML security, prompt injection | 3 | Semgrep, CodeQL, Custom |
| `container-security-specialist` | Docker, container security | 1 | Hadolint, Custom |
| `comprehensive-security-agent` | All security domains | 15 | All scanner types |

## Context-Aware Rule Selection

The runtime intelligently selects relevant rules based on:

### File Extension Mapping

- `.py` → Python, backend, API rules
- `.js/.ts` → JavaScript/TypeScript, frontend, web rules
- `.java` → Java, backend, API rules
- `.dockerfile` → Docker, container rules
- `.yaml/.yml` → Configuration, deployment rules

### Directory Pattern Detection

- `src/` → Source code rules
- `test/` → Testing-specific rules
- `config/` → Configuration security rules
- `api/` → API security rules
- `auth/` → Authentication rules

### Content Pattern Analysis

- JWT/token patterns → Secrets and authentication rules
- Database query patterns → SQL injection rules
- HTTP request/response patterns → Web security rules
- Docker commands → Container security rules

## LLM Provider Integration

### Mock Provider (Development/Testing)

```python
from app.runtime.llm_interface import LLMInterface

llm = LLMInterface(default_provider="mock")

# Mock provider returns structured test responses
response = llm.generate_guidance(context, rules, metadata)
```

### Claude Provider (Placeholder)

```python
# Placeholder implementation - requires Anthropic SDK
llm = LLMInterface(default_provider="claude")
```

### Custom Provider Implementation

```python
from app.runtime.llm_interface import LLMProvider

class CustomLLMProvider(LLMProvider):
    def generate_guidance(self, prompt: str, context: Dict) -> str:
        # Implement your LLM integration
        return json.dumps({"guidance": "Custom guidance"})
    
    def get_provider_name(self) -> str:
        return "custom"

# Register custom provider
llm.providers["custom"] = CustomLLMProvider()
llm.set_default_provider("custom")
```

## Error Handling

The runtime implements comprehensive error handling:

```python
from app.runtime.core import AgenticRuntimeError

try:
    runtime = AgenticRuntime("/invalid/path")
except AgenticRuntimeError as e:
    print(f"Runtime initialization failed: {e}")

try:
    guidance = runtime.get_guidance(invalid_context)
except AgenticRuntimeError as e:
    print(f"Guidance generation failed: {e}")
```

## Performance Characteristics

- **Package Loading**: < 100ms per agent package
- **Rule Selection**: < 10ms for typical contexts  
- **Memory Usage**: ~1-5MB per loaded agent package
- **Concurrent Operations**: Thread-safe for read operations

## Security Considerations

### Input Validation

All inputs are validated and sanitized:
- File paths are checked for traversal attempts
- Content is limited to 1MB to prevent DoS
- Context fields are sanitized for prompt injection

### Information Disclosure Prevention

- Error messages don't expose system paths or sensitive data
- Debug logging is disabled by default
- Rule content is sanitized before LLM processing

### Package Integrity

- JSON packages are validated against expected schema
- File size limits prevent resource exhaustion
- Malicious content patterns are detected and blocked

## Integration Patterns

### Claude Code Integration

```python
# Example Claude Code sub-agent integration
class SecuritySubAgent:
    def __init__(self):
        self.runtime = AgenticRuntime()
        self.runtime.load_agent("comprehensive-security-agent")
    
    def provide_guidance(self, file_path: str, content: str) -> str:
        context = {"file_path": file_path, "content": content}
        guidance = self.runtime.get_guidance(context)
        
        if guidance:
            return f"Security Guidance:\n{guidance['guidance']}"
        return "No security issues detected."
```

### CLI Tool Integration

```python
import argparse
from app.runtime import AgenticRuntime

def main():
    parser = argparse.ArgumentParser(description="Security analysis CLI")
    parser.add_argument("file", help="File to analyze")
    parser.add_argument("--agent", help="Specific agent to use")
    args = parser.parse_args()
    
    runtime = AgenticRuntime()
    
    with open(args.file, 'r') as f:
        content = f.read()
    
    context = {"file_path": args.file, "content": content}
    guidance = runtime.get_guidance(context, agent_name=args.agent)
    
    if guidance:
        print(f"Severity: {guidance['severity']}")
        print(guidance['guidance'])
    else:
        print("No guidance available")

if __name__ == "__main__":
    main()
```

## Testing

Run the comprehensive test suite:

```bash
python3 tests/runtime/run_all_tests.py
```

Individual test categories:

```bash
python3 tests/runtime/test_core_basic.py          # Basic functionality
python3 tests/runtime/test_package_loading.py     # Package loading
python3 tests/runtime/test_rule_selection.py      # Rule selection
python3 tests/runtime/test_integration.py         # End-to-end workflow
```

## Troubleshooting

### Common Issues

**Agent fails to load:**
```python
# Check if package file exists
available = runtime.get_available_agents()
print(f"Available agents: {available}")

# Check package directory permissions
import os
print(f"Package dir readable: {os.access('app/dist/agents', os.R_OK)}")
```

**No guidance generated:**
```python
# Check rule selection
from app.runtime.rule_selector import RuleSelector
selector = RuleSelector()
analysis = selector.get_scope_analysis(context)
print(f"Detected scopes: {analysis['relevant_scopes']}")
```

**Performance issues:**
```python
# Enable debug logging to identify bottlenecks
runtime = AgenticRuntime(debug=True)
```

### Debug Mode

Enable comprehensive logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

runtime = AgenticRuntime(debug=True)
```

## Contributing

When extending the runtime:

1. **Follow security-first principles** - validate all inputs
2. **Maintain backwards compatibility** - don't break existing APIs
3. **Add comprehensive tests** - security and functionality
4. **Update documentation** - keep examples current
5. **Performance testing** - ensure sub-2 second response times

## License

This component is part of the GenAI Security Agents project. See project root for license details.