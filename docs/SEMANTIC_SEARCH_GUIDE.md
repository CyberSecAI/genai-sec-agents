# OWASP & ASVS Semantic Search User Guide

## Overview

The GenAI Security Agents OWASP & ASVS semantic search integration (Story 2.6) provides **comprehensive security knowledge access** that transforms development workflows with intelligent guidance. This complete system combines:

- **102 OWASP CheatSheets**: Complete security guidance corpus with intelligent processing
- **17 ASVS Verification Standards**: V1-V17 requirements with automated cleanup
- **Hybrid Search Architecture**: Semantic search + lexical search + compiled rule cards
- **Development Integration**: Real-time Claude Code CLI assistance during coding

## Key Features

### 🎯 Local-Only Operation
- No external API calls or internet dependencies  
- Complete offline capability for secure development environments
- Uses local rule card corpus generated from existing Rule Cards

### 🔧 Feature Flag Control
- **Runtime retrieval OFF by default** (secure configuration per ADR)
- Temporary per-analysis enablement with automatic expiration
- Global and scoped configuration management
- Comprehensive audit logging for compliance

### 🔍 Enhanced Analysis Capabilities
- **Edge Case Detection**: Finds vulnerabilities not covered by compiled rules
- **Explain Mode**: Detailed explanations with context-aware guidance
- **Provenance Tracking**: Complete audit trail with confidence scores
- **Result Differentiation**: Clear separation between compiled vs semantic results

### ⚡ Performance Optimized
- **<1s search requirement** (NFR1) with intelligent caching
- **Graceful fallback** when semtools unavailable
- **Resource limits** preventing DoS (30s timeout, 1MB files, 1000 file limit)
- **Concurrent handling** with proper resource management

## Installation and Setup

### 1. Install Dependencies

```bash
# Install Rust toolchain
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# Install semtools for semantic search functionality
cargo install semtools

# Verify installation
search --version
```

### 2. Build OWASP & ASVS Corpus

```bash
# Build both OWASP CheatSheets and ASVS standards
make semsearch-build

# Or build individually
make semsearch-build-owasp    # 102 OWASP CheatSheets
make semsearch-build-asvs     # 17 ASVS verification standards

# Verify corpus built successfully
ls -la research/search_corpus/owasp/ | wc -l
ls -la research/search_corpus/asvs/ | wc -l
```

### 3. Test Semantic Search Functionality

```bash
# Test OWASP CheatSheets search
make semsearch q="JWT token validation"

# Test ASVS standards search  
make semsearch-asvs q="authentication requirements"

# Direct semtools usage
search "password security" research/search_corpus/owasp/*.md --top-k 5
```

## Usage Examples

### Basic File Analysis with Semantic Search

```bash
# Standard analysis (compiled rules only)
python3 app/claude_code/manual_commands.py file --path suspicious_file.py

# Enhanced analysis with semantic search (requires feature flag)
python3 app/claude_code/manual_commands.py file --path suspicious_file.py --semantic
```

**Example Output with Semantic Search:**

```
🔒 Security Analysis Results (Enhanced)
📁 File: suspicious_file.py  
🔍 Total Issues: 5
📊 Severity Breakdown:
  🚨 Critical: 1
  ⚠️ High: 2
  📋 Medium: 2
⏱️ Analysis Time: 1.24s
🔍 Semantic Search: ✅ Enhanced
   ⏱️ Semantic Processing: 245ms
   📊 Semantic Matches: 3

🔥 **Compiled Rule Matches (2):**
  • SECRET-HARDCODED-001 [compiled]
    └─ Remove hardcoded API keys from source code
  • AUTH-BYPASS-002 [compiled]  
    └─ Implement proper session validation

🎯 **High Confidence Semantic Matches (3):**
  • SECRET-MGMT-002 [0.89] (secrets)
    └─ Use environment variables or secure key management systems for API keys
  • AUTH-TIMING-001 [0.83] (authentication)
    └─ Prevent timing attacks in password comparison functions
  • RACE-CONDITION-001 [0.81] (concurrency) 
    └─ Potential race condition in multi-threaded authentication flow

🔍 **Edge Case Detections:**
  • Input validation bypass in custom authentication middleware
  • Potential side-channel information disclosure in error handling
```

### Workspace Analysis with Semantic Filters

```bash
# Workspace analysis with semantic search and filters
python3 app/claude_code/manual_commands.py workspace --semantic --semantic-filters '{
  "languages": ["python", "javascript"],
  "severity_levels": ["high", "critical"],  
  "categories": ["secrets", "authentication"]
}'
```

### Explain Mode for Security Guidance

```bash
# Get detailed explanation for specific security rules
python3 app/claude_code/manual_commands.py explain \
  --rule-id "SECRET-001" \
  --code-context "api_key = 'sk-1234567890abcdef'"

# Explain mode with semantic search enhancement
python3 app/claude_code/manual_commands.py explain \
  --rule-id "AUTH-BYPASS-001" \
  --code-context "def login(user, password): return True" \
  --semantic
```

**Example Explain Mode Output:**

```
🔍 **Security Rule Explanation** 
📋 Rule: SECRET-001 - Hardcoded API Key Detection
🎯 Severity: Critical
📁 Context: Python authentication code

📖 **Rule Description:**
API keys, tokens, and other secrets must never be hardcoded in source code as they can be easily discovered through static analysis, version control history, or binary inspection.

🔍 **Code Analysis:**
```python
api_key = 'sk-1234567890abcdef'  # ❌ Hardcoded secret
```

🎯 **Semantic Search Enhancement (3 related patterns):**
  • SECRET-ENV-001 [0.94] - Environment variable storage patterns
  • SECRET-VAULT-001 [0.87] - Key management service integration  
  • SECRET-ROTATION-001 [0.82] - Automatic secret rotation strategies

💡 **Remediation Steps:**
1. ✅ Move secret to environment variable: `api_key = os.getenv('API_KEY')`
2. ✅ Use secure key management service (AWS KMS, Azure Key Vault)
3. ✅ Implement secret rotation and monitoring
4. ✅ Scan version control history for exposed secrets

💻 **Secure Code Example:**
```python
import os
from cryptography.fernet import Fernet

# ✅ Secure: Environment variable with validation
api_key = os.getenv('API_KEY')
if not api_key:
    raise ValueError("API_KEY environment variable required")

# ✅ Secure: Key management service integration  
def get_api_key():
    # Use AWS SSM, Azure Key Vault, etc.
    return key_management_service.get_secret('api-key')
```
```

## Feature Flag Management

### Understanding Runtime Retrieval

**Runtime retrieval** refers to using semantic search to supplement compiled rules during analysis. This is **OFF by default** per ADR security requirements to ensure deterministic behavior.

### Checking Feature Flag Status

```python
from app.semantic import SemanticSearchFeatureFlags

# Check global status (should be False by default)
print("Global runtime retrieval:", SemanticSearchFeatureFlags.is_runtime_retrieval_enabled())

# Check for specific analysis
print("Analysis-specific:", SemanticSearchFeatureFlags.is_runtime_retrieval_enabled(analysis_id="test-123"))
```

### Enabling Semantic Search (Temporary)

```python
from app.semantic import SemanticSearchFeatureFlags

# Enable for specific analysis (expires automatically)
SemanticSearchFeatureFlags.enable_for_analysis(
    analysis_id="security-review-456", 
    duration=3600,  # 1 hour
    user_context="manual-security-review"
)

# Enable globally (requires admin privileges)
SemanticSearchFeatureFlags.set_global_flag(
    enabled=True,
    user_context="development-testing",
    expiration=7200  # 2 hours
)
```

### Audit Trail

All semantic search usage is logged for compliance:

```python
from app.semantic import SemanticSearchFeatureFlags

# View audit log
audit_entries = SemanticSearchFeatureFlags.get_audit_log(limit=10)
for entry in audit_entries:
    print(f"{entry['timestamp']}: {entry['action']} by {entry['user_context']}")
```

## Advanced Configuration

### Corpus Configuration

Edit `app/semantic/config/corpus_config.yaml` to customize corpus generation:

```yaml
corpus_generation:
  include_domains:
    - secrets
    - authentication  
    - web-security
    - containers
    - genai
  
  rule_card_sources:
    - path: "app/rule_cards/"
      recursive: true
      
  additional_sources:
    - path: "docs/security_guidance/"
      type: "markdown"
      
  output:
    format: "semtools"
    max_size_mb: 100
    compression: true
```

### Search Configuration  

Edit `app/semantic/config/search_config.yaml` for search behavior:

```yaml
search_behavior:
  default_limit: 10
  confidence_threshold: 0.7
  timeout_seconds: 30
  
  filters:
    languages:
      - python
      - javascript
      - typescript
      - go
      - rust
      
    severity_levels:
      - critical
      - high
      - medium
      - low
      
  result_formatting:
    include_provenance: true
    include_confidence_scores: true
    max_snippet_length: 200
```

## Integration with Manual Commands

### Enhanced Manual Commands

The manual security analysis commands have been enhanced with semantic search integration:

```bash
# File analysis with semantic search
python3 app/claude_code/manual_commands.py file \
  --path vulnerable_app.py \
  --semantic \
  --depth comprehensive

# Workspace analysis with semantic filtering  
python3 app/claude_code/manual_commands.py workspace \
  --path src/ \
  --semantic \
  --semantic-filters '{"languages": ["python"], "categories": ["secrets"]}'

# Explain mode with semantic enhancement
python3 app/claude_code/manual_commands.py explain \
  --rule-id "JWT-001" \
  --code-context "token = jwt.encode({'user': 'admin'}, 'secret')" \
  --semantic
```

### Command-Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--semantic` | Enable semantic search enhancement | `--semantic` |
| `--semantic-filters` | JSON filter specification | `--semantic-filters '{"severity_levels": ["critical"]}'` |
| `--explain` | Detailed rule explanation mode | `--explain` |
| `--rule-id` | Specific rule ID for explanation | `--rule-id "SECRET-001"` |
| `--code-context` | Code context for explanation | `--code-context "api_key = 'secret'"` |

## Performance and Reliability

### Performance Requirements

- **Search Response Time**: <1 second (NFR1)
- **Corpus Loading**: Efficient startup with caching
- **Concurrent Operations**: Proper resource management  
- **Memory Usage**: Bounded memory consumption

### Reliability Features

- **Graceful Degradation**: Works offline without semtools
- **Fallback Search**: Text-based search when semtools unavailable
- **Resource Limits**: Timeout and memory protections
- **Error Recovery**: Continues analysis if semantic search fails

### Performance Monitoring

```python
from app.semantic import SemanticSearchInterface

si = SemanticSearchInterface()
stats = si.get_search_statistics()

print(f"Average search time: {stats['avg_search_time_ms']}ms")
print(f"Cache hit rate: {stats['cache_hit_rate']}%") 
print(f"Total searches: {stats['total_searches']}")
print(f"Failed searches: {stats['failed_searches']}")
```

## Security Considerations

### Input Validation

All search queries undergo comprehensive validation:

- **Query Length**: Limited to 1000 characters
- **Special Characters**: Sanitized to prevent injection
- **Path Traversal**: Prevented in file path parameters
- **Resource Limits**: Timeout and memory protections

### Audit and Compliance

- **Complete Audit Trail**: All semantic search usage logged
- **User Context Tracking**: Identity and purpose recorded
- **Configuration Changes**: Feature flag changes audited
- **Security Events**: Suspicious activity detection and logging

### Privacy and Data Protection

- **Local-Only Processing**: No external API calls or data transmission
- **Secure Defaults**: Runtime retrieval OFF by default 
- **Data Minimization**: Only necessary data included in corpus
- **Access Control**: Feature flag management restricted to authorized users

## Troubleshooting

### Common Issues

#### Semtools Not Available

```bash
# Check if semtools is installed
python3 -c "import semtools; print('Semtools available')"

# Install if missing
pip install semtools>=0.1.0

# Verify fallback behavior works
python3 -c "
from app.semantic import SemanticSearchInterface
si = SemanticSearchInterface()
print('Fallback available:', si.is_fallback_available())
"
```

#### Feature Flag Issues

```bash
# Check feature flag status
python3 -c "
from app.semantic import SemanticSearchFeatureFlags
print('Runtime retrieval enabled:', SemanticSearchFeatureFlags.is_runtime_retrieval_enabled())
"

# Enable for testing (temporary)
python3 -c "
from app.semantic import SemanticSearchFeatureFlags
SemanticSearchFeatureFlags.enable_for_analysis('test', duration=300)
print('Enabled for test analysis')
"
```

#### Performance Issues

```bash
# Check corpus size and statistics
python3 -c "
from app.semantic import CorpusManager
cm = CorpusManager()
stats = cm.get_corpus_statistics()
print(f'Corpus size: {stats[\"size_mb\"]}MB')
print(f'Rule cards: {stats[\"rule_count\"]}')
print(f'Last updated: {stats[\"last_updated\"]}')
"

# Monitor search performance
python3 -c "
from app.semantic import SemanticSearchInterface
si = SemanticSearchInterface()
import time
start = time.time()
results = si.search_query('hardcoded secrets')
elapsed = time.time() - start
print(f'Search time: {elapsed*1000:.1f}ms')
print(f'Results: {len(results.matches)}')
"
```

### Debug Mode

Enable debug logging for detailed troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from app.semantic import SemanticSearchInterface
si = SemanticSearchInterface()
results = si.search_query("authentication bypass", debug=True)
```

## Best Practices

### When to Use Semantic Search

✅ **Recommended Use Cases:**
- Investigating edge cases not covered by compiled rules
- Security research and vulnerability analysis
- Training and educational purposes
- Comprehensive security reviews

❌ **Not Recommended:**
- Automated CI/CD pipelines (use compiled rules)
- Real-time production monitoring
- High-frequency analysis tasks

### Configuration Management

- **Keep runtime retrieval OFF** for production environments
- **Use temporary enablement** for specific analysis tasks
- **Monitor audit logs** for compliance and security
- **Regular corpus updates** to maintain freshness

### Performance Optimization

- **Use appropriate filters** to narrow search scope
- **Cache search results** for repeated queries
- **Monitor resource usage** to prevent performance degradation
- **Regular performance testing** to validate NFR requirements

## API Reference

### SemanticSearchInterface

```python
from app.semantic import SemanticSearchInterface

si = SemanticSearchInterface()

# Basic search
results = si.search_query("hardcoded secrets", limit=10)

# Context-aware search  
results = si.search_by_context(code_content, language="python")

# Search with filters
filters = {"severity_levels": ["critical"], "languages": ["python"]}
results = si.search_query("authentication", filters=filters)
```

### CorpusManager

```python
from app.semantic import CorpusManager

cm = CorpusManager()

# Generate corpus
corpus = cm.render_corpus_from_packages([])

# Validate corpus integrity
validation = cm.validate_corpus_integrity("corpus.json")
print(f"Valid: {validation.is_valid}")
```

### SemanticSearchFeatureFlags

```python
from app.semantic import SemanticSearchFeatureFlags

# Check status
enabled = SemanticSearchFeatureFlags.is_runtime_retrieval_enabled()

# Temporary enablement
SemanticSearchFeatureFlags.enable_for_analysis("analysis-123", duration=3600)

# Audit trail
audit = SemanticSearchFeatureFlags.get_audit_log(limit=20)
```

## Further Reading

- [Story 2.4 Technical Specification](stories/2.4.semtools-semantic-search.md)
- [ADR: Knowledge Access Architecture](ADR/knowledge_access.md)
- [Manual Commands Guide](MANUAL_COMMANDS_GUIDE.md)
- [Security Best Practices](SECURITY_GUIDE.md)
- [Performance Testing Guide](PERFORMANCE_TESTING_GUIDE.md)

---

*This guide covers the complete semantic search integration for GenAI Security Agents. For additional support or questions, refer to the comprehensive test suites in `tests/semantic/` or review the technical implementation in `app/semantic/`.*