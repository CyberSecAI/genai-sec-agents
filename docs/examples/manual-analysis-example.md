# Manual Security Analysis Example - Story 2.3

This example demonstrates the manual on-demand security analysis functionality implemented in Story 2.3.

## Example: Analyzing a Flask Application

Let's analyze a simple Flask application with security issues:

### 1. Create Test Application

```python
# example_app.py
from flask import Flask, request, make_response
import requests
import jwt
import hashlib

app = Flask(__name__)

# Security Issues for Testing:
SECRET_KEY = "hardcoded_secret_12345"  # Issue: Hardcoded secret
API_TOKEN = "sk-1234567890abcdef"       # Issue: Hardcoded API token

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    # Issue: Weak password hashing
    password_hash = hashlib.md5(password.encode()).hexdigest()
    
    # Issue: Insecure cookie configuration
    response = make_response('Login successful')
    response.set_cookie('session_id', 'abc123')  # Missing HttpOnly, Secure
    
    return response

@app.route('/proxy')
def proxy():
    # Issue: Server-Side Request Forgery (SSRF)
    url = request.args.get('url')
    response = requests.get(url)
    return response.text

@app.route('/generate_token')
def generate_token():
    user_id = request.args.get('user_id')
    # Issue: JWT with hardcoded secret
    token = jwt.encode({"user_id": user_id}, SECRET_KEY, algorithm="HS256")
    return {"token": token}

if __name__ == '__main__':
    # Issue: Development server on all interfaces
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### 2. Manual File Analysis

```bash
# Analyze the single file
python3 app/claude_code/manual_commands.py file --path example_app.py --format human
```

**Example Output:**
```
🔒 Security Analysis Results
📁 Files Analyzed: 1
🔍 Total Issues: 5
📊 Severity Breakdown:
  🚨 Critical: 2
  ⚠️ High: 2
  📋 Medium: 1
  💡 Low: 0
🎯 CI/CD Prediction: FAIL (4 blocking issues)
⏱️ Analysis Time: 1.23s

🚨 **Critical Issues:**
- HARDCODED-JWT-SECRET-001: JWT secret hardcoded in source code
  📍 Line 11: SECRET_KEY = "hardcoded_secret_12345"
  💡 Store JWT secrets in environment variables
  
- HARDCODED-API-TOKEN-002: API token hardcoded in source code  
  📍 Line 12: API_TOKEN = "sk-1234567890abcdef"
  💡 Use secure configuration management

⚠️ **High Severity Issues:**
- SSRF-VULNERABILITY-003: Unvalidated URL in requests.get()
  📍 Line 31: response = requests.get(url)
  💡 Implement URL validation and allowlisting
  
- INSECURE-COOKIE-CONFIG-004: Session cookies missing security attributes
  📍 Line 23: response.set_cookie('session_id', 'abc123')
  💡 Add HttpOnly, Secure, and SameSite flags

📋 **Medium Severity Issues:**
- WEAK-PASSWORD-HASHING-005: Using MD5 for password hashing
  📍 Line 20: hashlib.md5(password.encode())
  💡 Use bcrypt, scrypt, or Argon2 for password hashing

🎯 **CI/CD Impact:**
❌ Pipeline would FAIL due to 4 blocking issues (Critical + High severity)
📋 Fix critical and high severity issues before committing

💻 **Remediation Examples:**
1. Environment Variables:
   ```python
   import os
   SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
   ```

2. Secure Cookie Configuration:
   ```python
   response.set_cookie('session_id', 'abc123', 
                      httponly=True, secure=True, samesite='Strict')
   ```

3. URL Validation:
   ```python
   from urllib.parse import urlparse
   
   def is_safe_url(url):
       parsed = urlparse(url)
       return parsed.hostname in ALLOWED_HOSTS
   ```
```

### 3. Workspace Analysis

```bash
# Create a project structure
mkdir flask_project
cd flask_project
mkdir -p src tests config

# Move the app
mv example_app.py src/app.py

# Create additional files
echo "DATABASE_URL=sqlite:///app.db" > config/.env
echo "import unittest" > tests/test_app.py

# Analyze the entire workspace
python3 app/claude_code/manual_commands.py workspace --path . --depth comprehensive --format human
```

**Example Output:**
```
🔒 Security Analysis Results - Workspace Scan
📁 Files Analyzed: 3
🔍 Total Issues: 5
📊 File Breakdown:
  ✅ config/.env: 0 issues
  📝 tests/test_app.py: 0 issues  
  🚨 src/app.py: 5 issues

📊 Severity Breakdown:
  🚨 Critical: 2
  ⚠️ High: 2
  📋 Medium: 1
  💡 Low: 0

🎯 CI/CD Prediction: FAIL (4 blocking issues)
⏱️ Analysis Time: 2.45s

📊 **Workspace Summary:**
- 66% of files have security issues (2/3)
- Highest risk file: src/app.py (5 issues)
- Main concerns: Hardcoded secrets, SSRF, weak crypto

🔧 **Recommended Actions:**
1. 🚨 URGENT: Remove hardcoded secrets from src/app.py
2. ⚠️ HIGH: Fix SSRF vulnerability in proxy endpoint
3. ⚠️ HIGH: Add security headers to cookie configuration
4. 📋 MEDIUM: Upgrade password hashing algorithm
5. 📋 CONFIG: Add security linting to CI/CD pipeline

🎯 **Before Committing:**
❌ Current state would fail CI/CD validation
✅ After fixes: All issues resolved, pipeline should pass
📊 Estimated fix time: 30-45 minutes
```

### 4. JSON Output for Automation

```bash
# Get machine-readable output
python3 app/claude_code/manual_commands.py file --path src/app.py --format json > security_report.json
```

**Example JSON Structure:**
```json
{
  "status": "success",
  "analysis_type": "single_file", 
  "results": {
    "summary": {
      "total_issues": 5,
      "files_analyzed": 1,
      "analysis_time": 1.23,
      "critical_count": 2,
      "high_count": 2,
      "medium_count": 1,
      "low_count": 0
    },
    "issues_by_severity": {
      "critical": [
        {
          "id": "HARDCODED-JWT-SECRET-001",
          "title": "JWT Secret Hardcoded",
          "severity": "critical",
          "file": "src/app.py",
          "description": "JWT secret hardcoded in source code",
          "recommendations": ["Use environment variables", "Implement secure key management"],
          "avoid": ["Hardcoding secrets in source code"],
          "cicd_relevant": true,
          "blocking_severity": true
        }
      ]
    },
    "ci_cd_prediction": {
      "would_pass": false,
      "blocking_issues": 4,
      "critical_issues": 2,
      "high_issues": 2,
      "confidence": "high",
      "recommendation": "Fix 4 blocking issues before commit"
    }
  },
  "metadata": {
    "file_path": "src/app.py",
    "analysis_depth": "standard",
    "execution_time": 1.23,
    "timestamp": 1693507200
  }
}
```

### 5. Security Features Demonstration

The manual analysis commands include comprehensive security protections:

#### Path Traversal Protection
```bash
# These commands are blocked by security controls:
python3 app/claude_code/manual_commands.py file --path ../../../etc/passwd     # ❌ Blocked
python3 app/claude_code/manual_commands.py file --path /root/.ssh/id_rsa      # ❌ Blocked  
python3 app/claude_code/manual_commands.py workspace --path ../../            # ❌ Blocked
```

#### Resource Limits
```bash
# Large files are rejected:
dd if=/dev/zero of=large_file.py bs=1M count=5  # Create 5MB file
python3 app/claude_code/manual_commands.py file --path large_file.py          # ❌ Too large

# Analysis times out after 30 seconds for protection
# Workspace analysis limited to 1000 files maximum
```

#### Input Validation
```bash
# Invalid file types are rejected:
echo "malicious payload" > malware.exe
python3 app/claude_code/manual_commands.py file --path malware.exe            # ❌ Invalid extension

# Malformed inputs handled gracefully:
python3 app/claude_code/manual_commands.py file --path ""                     # ❌ Validation error
python3 app/claude_code/manual_commands.py file --path $'\x00\x01\x02'       # ❌ Validation error
```

## Integration with Claude Code

When used within Claude Code, the manual commands integrate seamlessly:

```
# In Claude Code IDE:
*security-scan-file src/app.py --depth=comprehensive
*security-scan-workspace --path=src/ --depth=standard
```

The commands provide:
- **Instant feedback** with structured, color-coded results
- **IDE-safe output** with sanitized content to prevent injection
- **Contextual guidance** relevant to detected frameworks (Flask, Django, etc.)
- **CI/CD predictions** to prevent pipeline failures
- **Actionable recommendations** with code examples

## Summary

Story 2.3 Manual On-Demand Execution provides:

1. **Comprehensive Analysis**: Files and workspaces with rule aggregation
2. **Security-First Design**: Path validation, resource limits, input sanitization  
3. **CI/CD Consistency**: Predictions match pipeline validation rules
4. **Developer-Friendly**: Human-readable output with actionable guidance
5. **Integration-Ready**: JSON output for automation and toolchain integration
6. **Performance Optimized**: Sub-30-second analysis with intelligent caching

The manual commands bridge the gap between real-time guidance (Story 2.2) and automated pipeline validation, giving developers proactive control over their security posture.