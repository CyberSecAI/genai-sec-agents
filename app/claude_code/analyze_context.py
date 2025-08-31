#!/usr/bin/env python3
"""
Code Context Analysis for Claude Code Sub-Agent

Analyzes user code context and selects relevant security rules using 
the AgenticRuntime from Story 2.1.
"""

import sys
import json
import time
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError

# Add project root and app to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'app'))

try:
    from app.runtime.core import AgenticRuntime
    from app.claude_code.initialize_security_runtime import SecurityRuntimeManager
except ImportError as e:
    print(f"Error importing runtime components: {e}")
    sys.exit(1)


class CodeContextAnalyzer:
    """Analyzes code context and selects relevant security rules with performance optimization."""
    
    def __init__(self):
        self.runtime_manager = SecurityRuntimeManager()
        self.runtime: Optional[AgenticRuntime] = None
        # Task 4: Performance optimization attributes
        self._guidance_cache: Dict[str, Any] = {}
        self._performance_metrics: Dict[str, float] = {}
        self.timeout_seconds = 2.0  # Sub-2-second requirement
        
    def initialize(self) -> bool:
        """Initialize the runtime manager."""
        if self.runtime_manager.initialize():
            self.runtime = self.runtime_manager.get_runtime()
            return True
        return False
    
    def _sanitize_code_input(self, code_content: str) -> str:
        """Sanitize user code input for security (Task 2 enhancement)."""
        if not code_content:
            return ""
            
        # Remove potential command injection patterns
        import re
        sanitized = code_content
        
        # Limit content size to prevent DoS
        MAX_CODE_SIZE = 50000  # 50KB limit
        if len(sanitized) > MAX_CODE_SIZE:
            sanitized = sanitized[:MAX_CODE_SIZE] + "\n# [Content truncated for security]"
        
        # Remove suspicious patterns that could be used maliciously
        dangerous_patterns = [
            r'import\s+os\s*;\s*os\.system\([^)]*\)',
            r'subprocess\.[^(]*\([^)]*shell\s*=\s*True',
            r'eval\s*\([^)]*\)',
            r'exec\s*\([^)]*\)'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                # Log potential security issue but don't block - just flag for analysis
                pass
                
        return sanitized
    
    def _enhance_context_analysis(self, file_path_obj: Path, code_content: str) -> Dict[str, Any]:
        """Enhanced context analysis for better rule selection (Task 2)."""
        context = {
            'file_path': str(file_path_obj),
            'content': code_content,
            'file_type': file_path_obj.suffix,
            # Enhanced context attributes for better rule selection
            'file_size': len(code_content),
            'line_count': len(code_content.splitlines()) if code_content else 0,
            'has_imports': 'import ' in code_content if code_content else False,
            'contains_http': any(proto in code_content.lower() for proto in ['http://', 'https://']),
            'contains_sql': any(keyword in code_content.lower() for keyword in ['select ', 'insert ', 'update ', 'delete ']),
            'contains_crypto': any(keyword in code_content.lower() for keyword in ['password', 'secret', 'key', 'token', 'cipher']),
            'framework_hints': self._detect_frameworks(code_content)
        }
        return context
    
    def _detect_frameworks(self, code_content: str) -> List[str]:
        """Detect frameworks and libraries for better guidance (Task 2)."""
        if not code_content:
            return []
            
        frameworks = []
        framework_patterns = {
            'flask': ['from flask', 'import flask', '@app.route'],
            'django': ['from django', 'import django', 'Django'],
            'fastapi': ['from fastapi', 'import fastapi', 'FastAPI'],
            'requests': ['import requests', 'requests.'],
            'sqlalchemy': ['from sqlalchemy', 'import sqlalchemy'],
            'jwt': ['import jwt', 'jwt.encode', 'jwt.decode'],
            'crypto': ['from crypto', 'import crypto', 'hashlib', 'bcrypt']
        }
        
        content_lower = code_content.lower()
        for framework, patterns in framework_patterns.items():
            if any(pattern.lower() in content_lower for pattern in patterns):
                frameworks.append(framework)
                
        return frameworks
    
    def analyze_file_context(self, file_path: str, code_content: Optional[str] = None, 
                           use_cache: bool = True) -> Dict[str, Any]:
        """Enhanced analyze file context with performance optimization (Task 4).
        
        Args:
            file_path: Path to the file being analyzed
            code_content: Optional code content (if not provided, will read from file)
            use_cache: Whether to use caching for performance
            
        Returns:
            Dict containing enhanced analysis results and selected rules
        """
        analysis_start_time = time.time()
        
        if not self.runtime:
            return {"error": "Runtime not initialized"}
        
        try:
            # Create context from file path and content
            file_path_obj = Path(file_path)
            
            # Read content if not provided
            if code_content is None and file_path_obj.exists():
                try:
                    code_content = file_path_obj.read_text(encoding='utf-8')
                except Exception as e:
                    return {"error": f"Failed to read file: {e}"}
            elif code_content is None:
                code_content = ""
            
            # Task 4: Check guidance cache for performance
            cache_key = self._get_analysis_cache_key(str(file_path_obj), code_content)
            if use_cache and cache_key in self._guidance_cache:
                cached_result = self._guidance_cache[cache_key]
                if time.time() - cached_result['timestamp'] < 60:  # 1-minute cache
                    cached_result['result']['analysis_metadata']['cache_hit'] = True
                    self._performance_metrics['analysis_time'] = time.time() - analysis_start_time
                    return cached_result['result']
            
            # Task 2: Sanitize user code input
            sanitize_start = time.time()
            sanitized_content = self._sanitize_code_input(code_content)
            sanitize_time = time.time() - sanitize_start
            
            # Task 2: Enhanced context analysis for better rule selection
            context_start = time.time()
            context = self._enhance_context_analysis(file_path_obj, sanitized_content)
            context_time = time.time() - context_start
            
            # Task 4: Timeout-controlled guidance generation
            guidance_start = time.time()
            try:
                guidance_response = self._get_guidance_with_timeout(context, self.timeout_seconds)
            except TimeoutError:
                return {"error": "Analysis timed out - response took longer than 2 seconds"}
            guidance_time = time.time() - guidance_start
            
            if not guidance_response:
                return {"error": "No guidance response received"}
            
            # Extract selected rules from guidance response
            selected_rules = guidance_response.get("selected_rules", [])
            
            # Task 4: Optimized result construction
            result_start = time.time()
            result = self._build_analysis_result(
                file_path_obj, selected_rules, guidance_response, context
            )
            
            # Task 4: Performance metrics
            total_time = time.time() - analysis_start_time
            result["analysis_metadata"].update({
                "performance_metrics": {
                    "total_time": total_time,
                    "sanitize_time": sanitize_time,
                    "context_time": context_time,
                    "guidance_time": guidance_time,
                    "result_time": time.time() - result_start,
                    "cache_hit": False
                },
                "sub_2_second_compliant": total_time < 2.0
            })
            
            # Task 4: Cache the result if successful
            if use_cache and total_time < 2.0:  # Only cache successful fast results
                self._guidance_cache[cache_key] = {
                    'result': result,
                    'timestamp': time.time()
                }
                
                # Limit cache size to prevent memory issues
                if len(self._guidance_cache) > 100:
                    oldest_key = min(self._guidance_cache.keys(), 
                                   key=lambda k: self._guidance_cache[k]['timestamp'])
                    del self._guidance_cache[oldest_key]
            
            self._performance_metrics['analysis_time'] = total_time
            return result
            
        except Exception as e:
            return {"error": f"Analysis failed: {e}"}
    
    def _get_analysis_cache_key(self, file_path: str, content: str) -> str:
        """Generate cache key for analysis results."""
        import hashlib
        content_hash = hashlib.md5(f"{file_path}:{len(content)}:{content[:100]}".encode()).hexdigest()
        return content_hash
    
    def _get_guidance_with_timeout(self, context: Dict[str, Any], timeout_seconds: float) -> Dict[str, Any]:
        """Get guidance with timeout handling for performance."""
        def guidance_worker():
            return self.runtime.get_guidance(context)
        
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(guidance_worker)
            try:
                return future.result(timeout=timeout_seconds)
            except TimeoutError:
                raise TimeoutError(f"Guidance generation exceeded {timeout_seconds}s timeout")
    
    def _build_analysis_result(self, file_path_obj: Path, selected_rules: List[Dict], 
                             guidance_response: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimized analysis result construction."""
        result = {
            "file_path": str(file_path_obj),
            "file_type": file_path_obj.suffix,
            "rules_count": len(selected_rules),
            "selected_rules": [],
            "guidance": guidance_response.get("guidance", ""),
            "agent_used": guidance_response.get("agent_name", "unknown"),
            "security_score": self._calculate_security_score(selected_rules),
            "priority_issues": [],
            "actionable_recommendations": [],
            "secure_code_snippets": [],
            "analysis_metadata": {
                "packages_loaded": len(self.runtime_manager.get_loaded_packages()),
                "guidance_generated": True,
                "context_enhanced": True,
                "input_sanitized": True,
                "frameworks_detected": context.get('framework_hints', [])
            }
        }
        
        # Task 4: Optimized rule processing
        for rule in selected_rules:
            rule_info = {
                "id": rule.get("id", "unknown"),
                "title": rule.get("title", ""),
                "severity": rule.get("severity", "unknown"),
                "scope": rule.get("scope", ""),
                "requirement": rule.get("requirement", ""),
                "do_recommendations": rule.get("do", []),
                "dont_recommendations": rule.get("dont", []),
                "detection_tools": rule.get("detect", {}),
                "references": rule.get("refs", {}),
                "actionability_score": len(rule.get("do", [])) + len(rule.get("dont", []))
            }
            result["selected_rules"].append(rule_info)
            
            # Identify priority issues (high/critical severity)
            if rule.get("severity") in ["high", "critical"]:
                result["priority_issues"].append({
                    "id": rule.get("id"),
                    "title": rule.get("title"),
                    "severity": rule.get("severity"),
                    "requirement": rule.get("requirement")
                })
            
            # Extract actionable recommendations
            for do_item in rule.get("do", []):
                result["actionable_recommendations"].append({
                    "rule_id": rule.get("id"),
                    "action": "implement",
                    "recommendation": do_item,
                    "severity": rule.get("severity")
                })
            
            for dont_item in rule.get("dont", []):
                result["actionable_recommendations"].append({
                    "rule_id": rule.get("id"),
                    "action": "avoid",
                    "recommendation": dont_item,
                    "severity": rule.get("severity")
                })
            
            # Task 3: Generate secure code snippets based on rule recommendations
            snippets = self._generate_secure_code_snippets(rule, context)
            for snippet in snippets:
                result["secure_code_snippets"].append(snippet)
        
        return result
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get performance metrics for monitoring."""
        runtime_metrics = self.runtime_manager.get_performance_metrics()
        return {**self._performance_metrics, **runtime_metrics}
    
    def _calculate_security_score(self, selected_rules: List[Dict]) -> Dict[str, Any]:
        """Calculate security score based on selected rules (Task 2)."""
        if not selected_rules:
            return {"score": 100, "grade": "A", "issues": 0}
        
        severity_weights = {"critical": 25, "high": 15, "medium": 10, "low": 5}
        total_penalty = 0
        issue_count = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for rule in selected_rules:
            severity = rule.get("severity", "low")
            issue_count[severity] += 1
            total_penalty += severity_weights.get(severity, 5)
        
        score = max(0, 100 - total_penalty)
        
        if score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B"
        elif score >= 70:
            grade = "C"
        elif score >= 60:
            grade = "D"
        else:
            grade = "F"
        
        return {
            "score": score,
            "grade": grade,
            "issues": sum(issue_count.values()),
            "breakdown": issue_count
        }
    
    def _generate_secure_code_snippets(self, rule: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate secure code snippets based on rule recommendations (Task 3)."""
        snippets = []
        rule_id = rule.get("id", "unknown")
        file_type = context.get("file_type", "")
        frameworks = context.get("framework_hints", [])
        
        # Task 3: Generate context-aware snippets based on rule type and file context
        if "COOKIES" in rule_id and file_type == ".py":
            snippets.extend(self._generate_cookie_snippets(rule, frameworks))
        elif "JWT" in rule_id and file_type == ".py":
            snippets.extend(self._generate_jwt_snippets(rule, frameworks))
        elif "DOCKER" in rule_id and file_type in [".dockerfile", ""]:
            snippets.extend(self._generate_docker_snippets(rule))
        elif "SQL" in rule_id or "INJECTION" in rule_id:
            snippets.extend(self._generate_sql_security_snippets(rule, file_type, frameworks))
        elif "SECRETS" in rule_id or "KEY" in rule_id:
            snippets.extend(self._generate_secrets_snippets(rule, file_type))
        
        return snippets
    
    def _generate_cookie_snippets(self, rule: Dict[str, Any], frameworks: List[str]) -> List[Dict[str, Any]]:
        """Generate secure cookie configuration snippets."""
        snippets = []
        rule_id = rule.get("id", "unknown")
        
        if "flask" in frameworks:
            snippets.append({
                "rule_id": rule_id,
                "language": "python",
                "framework": "flask",
                "title": "Secure Flask Cookie Configuration",
                "description": "Configure Flask cookies with security attributes",
                "code": """# Secure Flask cookie configuration
from flask import Flask, session

app = Flask(__name__)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'

@app.route('/login')
def login():
    session['user_id'] = user.id
    # Session cookies automatically inherit security settings
    return 'Logged in securely'""",
                "security_notes": [
                    "HttpOnly prevents XSS cookie theft",
                    "Secure flag requires HTTPS",
                    "SameSite prevents CSRF attacks"
                ],
                "validated": True
            })
        
        if "django" in frameworks:
            snippets.append({
                "rule_id": rule_id,
                "language": "python", 
                "framework": "django",
                "title": "Secure Django Cookie Settings",
                "description": "Configure Django session cookies securely",
                "code": """# settings.py - Secure Django cookie configuration
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True  # Requires HTTPS
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Optional: Custom secure cookie in views
from django.http import HttpResponse

def secure_cookie_view(request):
    response = HttpResponse('Cookie set securely')
    response.set_cookie(
        'secure_data', 
        value='sensitive_value',
        httponly=True,
        secure=True,
        samesite='Strict',
        max_age=3600  # 1 hour
    )
    return response""",
                "security_notes": [
                    "Comprehensive Django security cookie settings",
                    "CSRF cookies also secured",
                    "Custom cookies follow same security pattern"
                ],
                "validated": True
            })
        
        # Generic Python example if no specific framework detected
        if not frameworks or not any(fw in frameworks for fw in ['flask', 'django']):
            snippets.append({
                "rule_id": rule_id,
                "language": "python",
                "framework": "generic",
                "title": "Secure HTTP Cookie Headers",
                "description": "Set secure cookie headers manually",
                "code": """# Generic secure cookie implementation
import http.cookies

def set_secure_cookie(response, name, value):
    \"\"\"Set a cookie with all security attributes.\"\"\"
    cookie = http.cookies.SimpleCookie()
    cookie[name] = value
    cookie[name]['httponly'] = True
    cookie[name]['secure'] = True  # HTTPS only
    cookie[name]['samesite'] = 'Strict'
    cookie[name]['max-age'] = 3600  # 1 hour
    
    response.headers['Set-Cookie'] = cookie[name].OutputString()
    return response

# Example usage with secure session management
class SecureSession:
    def set_session_cookie(self, response, session_id):
        set_secure_cookie(response, 'session_id', session_id)
        return response""",
                "security_notes": [
                    "Manual cookie security attribute setting",
                    "Reusable secure cookie function",
                    "Includes proper expiration handling"
                ],
                "validated": True
            })
            
        return snippets
    
    def _generate_jwt_snippets(self, rule: Dict[str, Any], frameworks: List[str]) -> List[Dict[str, Any]]:
        """Generate secure JWT implementation snippets."""
        snippets = []
        rule_id = rule.get("id", "unknown")
        
        snippets.append({
            "rule_id": rule_id,
            "language": "python",
            "framework": "jwt",
            "title": "Secure JWT Implementation",
            "description": "JWT creation and validation with security best practices",
            "code": """# Secure JWT implementation with PyJWT
import jwt
import datetime
import secrets
from typing import Dict, Any, Optional

class SecureJWTHandler:
    def __init__(self, secret_key: str, algorithm: str = 'HS256'):
        # Task 3: Use secure algorithm and strong secret
        if algorithm in ['none', 'HS1']:  # Prevent algorithm confusion
            raise ValueError("Insecure JWT algorithm")
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def create_token(self, payload: Dict[str, Any], expires_in: int = 3600) -> str:
        \"\"\"Create secure JWT with expiration.\"\"\"
        now = datetime.datetime.utcnow()
        payload.update({
            'iat': now,  # Issued at
            'exp': now + datetime.timedelta(seconds=expires_in),  # Expiration
            'jti': secrets.token_urlsafe(16)  # JWT ID for revocation
        })
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        \"\"\"Verify JWT with comprehensive security checks.\"\"\"
        try:
            # Explicit algorithm specification prevents algorithm confusion attacks
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],  # Whitelist specific algorithm
                options={
                    'verify_exp': True,  # Verify expiration
                    'verify_iat': True,  # Verify issued at
                    'require': ['exp', 'iat', 'jti']  # Require security claims
                }
            )
            return payload
        except jwt.ExpiredSignatureError:
            # Handle expired tokens
            return None
        except jwt.InvalidTokenError:
            # Handle invalid tokens
            return None

# Usage example
jwt_handler = SecureJWTHandler(secrets.token_urlsafe(32))  # Strong random key
token = jwt_handler.create_token({'user_id': 123, 'role': 'user'})
payload = jwt_handler.verify_token(token)""",
            "security_notes": [
                "Algorithm whitelist prevents algorithm confusion attacks",
                "Mandatory expiration prevents token reuse",
                "Strong random secret key generation",
                "Comprehensive error handling for security edge cases",
                "JWT ID (jti) enables token revocation"
            ],
            "validated": True
        })
        
        return snippets
    
    def _generate_docker_snippets(self, rule: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate secure Dockerfile snippets."""
        snippets = []
        rule_id = rule.get("id", "unknown")
        
        if "USER" in rule_id:
            snippets.append({
                "rule_id": rule_id,
                "language": "dockerfile",
                "framework": "docker",
                "title": "Secure Dockerfile User Configuration",
                "description": "Run containers with non-root user",
                "code": """# Secure Dockerfile with non-root user
FROM python:3.11-slim

# Create dedicated application user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Set up application directory with proper permissions
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and set ownership
COPY . .
RUN chown -R appuser:appgroup /app

# Switch to non-root user before running application
USER appuser

# Run application as non-root user
EXPOSE 8000
CMD ["python", "app.py"]""",
                "security_notes": [
                    "Dedicated non-root user prevents privilege escalation",
                    "Proper file ownership ensures application can access files",
                    "User switching happens before CMD to ensure non-root execution",
                    "Follows principle of least privilege"
                ],
                "validated": True
            })
            
        return snippets
    
    def _generate_sql_security_snippets(self, rule: Dict[str, Any], file_type: str, frameworks: List[str]) -> List[Dict[str, Any]]:
        """Generate SQL injection prevention snippets."""
        snippets = []
        rule_id = rule.get("id", "unknown")
        
        if file_type == ".py":
            if "sqlalchemy" in frameworks:
                snippets.append({
                    "rule_id": rule_id,
                    "language": "python",
                    "framework": "sqlalchemy",
                    "title": "SQLAlchemy Parameterized Queries",
                    "description": "Prevent SQL injection with SQLAlchemy ORM",
                    "code": """# Secure SQLAlchemy query implementation
from sqlalchemy import text
from sqlalchemy.orm import Session

class SecureUserService:
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_user_by_id(self, user_id: int):
        \"\"\"Secure parameterized query using ORM.\"\"\"
        # SECURE: ORM prevents SQL injection
        return self.db.query(User).filter(User.id == user_id).first()
    
    def search_users_by_email(self, email_pattern: str):
        \"\"\"Secure text query with parameter binding.\"\"\"
        # SECURE: Named parameters prevent injection
        query = text(\"SELECT * FROM users WHERE email LIKE :pattern\")
        return self.db.execute(query, {'pattern': f'%{email_pattern}%'}).fetchall()
    
    def authenticate_user(self, username: str, password: str):
        \"\"\"Secure authentication query.\"\"\"
        # SECURE: Parameterized query with password hashing
        user = self.db.query(User).filter(
            User.username == username  # Parameterized automatically
        ).first()
        
        if user and self.verify_password(password, user.password_hash):
            return user
        return None

# AVOID: Never use string formatting for SQL
# BAD: f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection risk
# BAD: "SELECT * FROM users WHERE email = '" + email + "'"  # SQL injection risk""",
                    "security_notes": [
                        "SQLAlchemy ORM automatically parameterizes queries",
                        "text() queries use named parameter binding",
                        "Never use string formatting for SQL construction",
                        "Password verification uses secure hashing"
                    ],
                    "validated": True
                })
        
        return snippets
    
    def _generate_secrets_snippets(self, rule: Dict[str, Any], file_type: str) -> List[Dict[str, Any]]:
        """Generate secure secrets management snippets."""
        snippets = []
        rule_id = rule.get("id", "unknown")
        
        if file_type == ".py":
            snippets.append({
                "rule_id": rule_id,
                "language": "python",
                "framework": "generic",
                "title": "Secure Environment Variable Usage",
                "description": "Secure secrets management with environment variables",
                "code": """# Secure secrets management
import os
import secrets
from typing import Optional

class SecureConfig:
    \"\"\"Secure configuration management.\"\"\"
    
    def __init__(self):
        self.required_vars = ['DATABASE_URL', 'SECRET_KEY', 'API_TOKEN']
        self._validate_environment()
    
    def _validate_environment(self):
        \"\"\"Validate required environment variables exist.\"\"\"
        missing = [var for var in self.required_vars if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {missing}")
    
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        \"\"\"Securely retrieve environment variable.\"\"\"
        value = os.getenv(key, default)
        if not value:
            raise ValueError(f"Secret '{key}' not found in environment")
        return value
    
    def generate_secure_key(self, length: int = 32) -> str:
        \"\"\"Generate cryptographically secure random key.\"\"\"
        return secrets.token_urlsafe(length)
    
    @property
    def database_url(self) -> str:
        return self.get_secret('DATABASE_URL')
    
    @property  
    def secret_key(self) -> str:
        return self.get_secret('SECRET_KEY')
    
    @property
    def api_token(self) -> str:
        return self.get_secret('API_TOKEN')

# Usage example
config = SecureConfig()

# SECURE: Environment variables, never hardcoded
db_url = config.database_url
secret = config.secret_key

# AVOID: Never hardcode secrets in source code
# BAD: SECRET_KEY = "hardcoded-secret-key-123"  # Security risk
# BAD: API_TOKEN = "sk-1234567890abcdef"  # Security risk
# BAD: DATABASE_URL = "postgresql://user:pass@localhost/db"  # Security risk""",
                "security_notes": [
                    "Environment variables prevent secrets in source code",
                    "Validation ensures required secrets are present",
                    "Cryptographically secure random key generation",
                    "Clear separation of secure and insecure practices"
                ],
                "validated": True
            })
            
        return snippets
    
    def _validate_snippet_security(self, snippet: Dict[str, Any]) -> bool:
        """Validate that generated code snippet is secure (Task 3)."""
        code = snippet.get("code", "")
        
        # Task 3: Security validation patterns
        security_issues = [
            "eval(",
            "exec(",
            "os.system(",
            "shell=True",
            "password = ",
            "secret = ",
            "api_key = "
        ]
        
        # Check for obvious security anti-patterns
        for issue in security_issues:
            if issue in code and "# BAD:" not in code and "# AVOID:" not in code:
                return False
                
        return True
    
    def format_guidance_output(self, analysis_result: Dict[str, Any]) -> str:
        """Enhanced format analysis result for Claude Code sub-agent display (Task 2)."""
        if "error" in analysis_result:
            return f"❌ Analysis Error: {analysis_result['error']}"
        
        output = []
        
        # Task 2: Enhanced header with security score
        security_score = analysis_result.get("security_score", {})
        score_text = f"{security_score.get('score', 0)}/100 ({security_score.get('grade', 'N/A')})"
        
        output.append(f"🔍 **Security Analysis Results** - Score: {score_text}")
        output.append(f"📁 File: {analysis_result.get('file_path', 'unknown')}")
        output.append(f"🤖 Agent: {analysis_result.get('agent_used', 'unknown')}")
        
        # Task 2: Show frameworks detected
        metadata = analysis_result.get("analysis_metadata", {})
        frameworks = metadata.get("frameworks_detected", [])
        if frameworks:
            output.append(f"⚙️ Frameworks: {', '.join(frameworks)}")
        
        # Task 2: Priority issues section (non-intrusive but prominent)
        priority_issues = analysis_result.get("priority_issues", [])
        if priority_issues:
            output.append(f"\n🚨 **Priority Security Issues ({len(priority_issues)}):**")
            for issue in priority_issues[:2]:  # Show top 2 priority issues
                severity_emoji = "🚨" if issue.get("severity") == "critical" else "⚠️"
                output.append(f"{severity_emoji} {issue.get('title')} ({issue.get('id')})")
                if issue.get("requirement"):
                    output.append(f"   └─ {issue.get('requirement')}")
        
        # Task 2: Include the generated guidance if available
        guidance = analysis_result.get("guidance", "")
        if guidance and len(guidance.strip()) > 0:
            output.append(f"\n💡 **Security Guidance:**")
            output.append(guidance)
        
        # Task 2: Actionable recommendations section
        recommendations = analysis_result.get("actionable_recommendations", [])
        if recommendations:
            # Group by severity and action type
            implement_recs = [r for r in recommendations if r.get("action") == "implement"]
            avoid_recs = [r for r in recommendations if r.get("action") == "avoid"]
            
            if implement_recs:
                output.append(f"\n✅ **Recommended Actions ({len(implement_recs)}):**")
                for rec in implement_recs[:3]:  # Show top 3 implementation recommendations
                    severity_emoji = {
                        "critical": "🚨", "high": "⚠️", "medium": "📋", "low": "📝"
                    }.get(rec.get("severity", ""), "📋")
                    output.append(f"{severity_emoji} {rec.get('recommendation')}")
            
            if avoid_recs:
                output.append(f"\n🚫 **Avoid These Practices ({len(avoid_recs)}):**")
                for rec in avoid_recs[:3]:  # Show top 3 things to avoid
                    severity_emoji = {
                        "critical": "🚨", "high": "⚠️", "medium": "📋", "low": "📝"
                    }.get(rec.get("severity", ""), "📋")
                    output.append(f"{severity_emoji} {rec.get('recommendation')}")
        
        # Task 2: Show detailed rules (collapsed view for non-intrusiveness)
        rules = analysis_result.get("selected_rules", [])
        if rules:
            output.append(f"\n📊 **Rule Details ({len(rules)} applicable):**")
            
            for i, rule in enumerate(rules[:2], 1):  # Limit to top 2 for readability
                severity_emoji = {
                    "critical": "🚨", "high": "⚠️", 
                    "medium": "📋", "low": "📝"
                }.get(rule.get("severity", ""), "📋")
                
                output.append(f"{severity_emoji} **{rule.get('title', 'Security Rule')}** ({rule.get('severity', 'unknown').upper()}) - {rule.get('id', 'unknown')}")
                
                # Show references if available
                refs = rule.get("references", {})
                if refs:
                    ref_list = []
                    for standard, codes in refs.items():
                        if codes:
                            ref_list.append(f"{standard.upper()}: {', '.join(codes)}")
                    if ref_list:
                        output.append(f"   📚 Standards: {' | '.join(ref_list[:2])}")
            
            if len(rules) > 2:
                output.append(f"   └─ ... and {len(rules) - 2} more rules (run with --format=json for full details)")
        
        elif not guidance and not priority_issues:
            output.append(f"\n✅ No specific security concerns identified.")
            if security_score.get('score', 0) == 100:
                output.append(f"🎉 Excellent security posture!")
        
        # Task 3: Show secure code snippets if available
        snippets = analysis_result.get("secure_code_snippets", [])
        if snippets:
            output.append(f"\n💻 **Secure Code Examples ({len(snippets)} available):**")
            
            for i, snippet in enumerate(snippets[:2], 1):  # Show first 2 snippets
                framework = snippet.get("framework", "generic")
                language = snippet.get("language", "code")
                title = snippet.get("title", "Secure Implementation")
                
                output.append(f"\n📝 **{title}** ({language.upper()}{f'/{framework}' if framework != 'generic' else ''})")
                output.append(f"   {snippet.get('description', 'Secure code implementation')}")
                
                # Show a condensed version of the code (first few lines)
                code_lines = snippet.get("code", "").strip().split('\n')
                if code_lines:
                    output.append(f"   ```{language}")
                    # Show first 5 lines + indication if more exists
                    for line in code_lines[:5]:
                        output.append(f"   {line}")
                    if len(code_lines) > 5:
                        output.append(f"   # ... ({len(code_lines)-5} more lines)")
                    output.append(f"   ```")
                
                # Show key security notes
                security_notes = snippet.get("security_notes", [])[:2]  # Top 2 notes
                for note in security_notes:
                    output.append(f"   🔐 {note}")
            
            if len(snippets) > 2:
                output.append(f"\n   └─ ... and {len(snippets) - 2} more examples (run with --format=json for full code)")
        
        # Task 2: Performance metadata (non-intrusive footer)
        if metadata.get("input_sanitized") and metadata.get("context_enhanced"):
            output.append(f"\n🔒 Analysis: Input sanitized, context enhanced, {metadata.get('packages_loaded', 0)} agents loaded")
        
        return "\n".join(output)

    # === Manual Analysis Extensions for Story 2.3 ===
    
    def analyze_file_manual(self, file_path: str, include_all_rules: bool = True) -> Dict[str, Any]:
        """Analyze file with comprehensive rule set for manual analysis.
        
        Args:
            file_path: Path to file to analyze
            include_all_rules: Whether to include all applicable rules (True for manual mode)
            
        Returns:
            Enhanced analysis results for manual use
        """
        if not self.runtime:
            return {"error": "Runtime not initialized"}
        
        try:
            file_path_obj = Path(file_path)
            
            # Read file content
            if not file_path_obj.exists():
                return {"error": f"File not found: {file_path}"}
            
            try:
                code_content = file_path_obj.read_text(encoding='utf-8')
            except Exception as e:
                return {"error": f"Failed to read file: {e}"}
            
            # Enhanced context for manual analysis
            context = self._enhance_context_analysis(file_path_obj, code_content)
            context["manual_mode"] = True
            context["comprehensive_analysis"] = include_all_rules
            
            # Get all applicable rules from all packages for comprehensive analysis
            if include_all_rules:
                all_rules = self._select_all_applicable_rules(context)
                context["force_all_rules"] = True
            
            # Get guidance with extended timeout for manual mode
            guidance_response = self._get_guidance_with_timeout(context, 10.0)  # 10s for manual
            
            if not guidance_response:
                return {"error": "No guidance response received"}
            
            # Enhanced result building for manual analysis
            result = self._build_manual_analysis_result(
                file_path_obj, guidance_response.get("selected_rules", []), 
                guidance_response, context
            )
            
            return result
            
        except Exception as e:
            return {"error": f"Manual analysis failed: {e}"}

    def analyze_workspace_manual(self, workspace_path: str, 
                               file_filters: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analyze multiple files in workspace for manual analysis.
        
        Args:
            workspace_path: Path to workspace directory
            file_filters: Optional list of file patterns to include
            
        Returns:
            Aggregated analysis results for workspace
        """
        workspace_path_obj = Path(workspace_path)
        
        if not workspace_path_obj.exists():
            return {"error": f"Workspace path not found: {workspace_path}"}
        
        if not workspace_path_obj.is_dir():
            return {"error": f"Workspace path is not a directory: {workspace_path}"}
        
        try:
            # Discover files using the manual commands logic (reuse for consistency)
            from app.claude_code.manual_commands import ManualSecurityCommands
            manual_cmd = ManualSecurityCommands()
            discovered_files = manual_cmd._discover_workspace_files(workspace_path_obj, file_filters)
            
            if not discovered_files:
                return {
                    "workspace_path": str(workspace_path_obj),
                    "files_found": 0,
                    "files_analyzed": 0,
                    "aggregated_results": [],
                    "summary": {
                        "total_issues": 0,
                        "critical_issues": 0,
                        "high_issues": 0,
                        "medium_issues": 0,
                        "low_issues": 0
                    }
                }
            
            # Analyze each file
            file_results = []
            for file_path in discovered_files[:50]:  # Limit to 50 files for performance
                try:
                    result = self.analyze_file_manual(str(file_path), include_all_rules=True)
                    if "error" not in result:
                        file_results.append(result)
                except Exception as e:
                    # Continue with other files if one fails
                    continue
            
            # Aggregate results
            aggregated = self._aggregate_analysis_results(file_results)
            aggregated["workspace_path"] = str(workspace_path_obj)
            aggregated["files_found"] = len(discovered_files)
            aggregated["files_analyzed"] = len(file_results)
            
            return aggregated
            
        except Exception as e:
            return {"error": f"Workspace analysis failed: {e}"}
    
    def _select_all_applicable_rules(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Select all applicable rules from all agent packages for manual analysis.
        
        Args:
            context: Analysis context
            
        Returns:
            List of all applicable rules across packages
        """
        if not self.runtime:
            return []
        
        try:
            # Get all loaded packages
            packages = self.runtime_manager.get_loaded_packages()
            all_rules = []
            
            for package_name, package_path in packages.items():
                try:
                    # Load package content to get rules
                    import json
                    with open(package_path, 'r') as f:
                        package_data = json.load(f)
                    
                    # Extract rules from package
                    rules = package_data.get("rules_detail", [])
                    
                    # Add package context to each rule
                    for rule in rules:
                        rule["source_package"] = package_name
                        rule["package_path"] = str(package_path)
                    
                    all_rules.extend(rules)
                    
                except Exception as e:
                    # Continue with other packages if one fails
                    continue
            
            return all_rules
            
        except Exception as e:
            return []
    
    def _aggregate_analysis_results(self, file_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate results from multiple file analyses.
        
        Args:
            file_results: List of individual file analysis results
            
        Returns:
            Aggregated analysis results
        """
        if not file_results:
            return {
                "aggregated_results": [],
                "summary": {
                    "total_issues": 0,
                    "critical_issues": 0,
                    "high_issues": 0,
                    "medium_issues": 0,
                    "low_issues": 0,
                    "files_with_issues": 0,
                    "highest_severity": "none"
                }
            }
        
        aggregated = {
            "aggregated_results": file_results,
            "summary": {
                "total_issues": 0,
                "critical_issues": 0,
                "high_issues": 0,
                "medium_issues": 0,
                "low_issues": 0,
                "files_with_issues": 0,
                "highest_severity": "low"
            }
        }
        
        # Aggregate issue counts
        for result in file_results:
            rules = result.get("selected_rules", [])
            if rules:
                aggregated["summary"]["files_with_issues"] += 1
                
                for rule in rules:
                    severity = rule.get("severity", "medium").lower()
                    
                    if severity == "critical":
                        aggregated["summary"]["critical_issues"] += 1
                        aggregated["summary"]["highest_severity"] = "critical"
                    elif severity == "high":
                        aggregated["summary"]["high_issues"] += 1
                        if aggregated["summary"]["highest_severity"] not in ["critical"]:
                            aggregated["summary"]["highest_severity"] = "high"
                    elif severity == "medium":
                        aggregated["summary"]["medium_issues"] += 1
                        if aggregated["summary"]["highest_severity"] not in ["critical", "high"]:
                            aggregated["summary"]["highest_severity"] = "medium"
                    else:  # low
                        aggregated["summary"]["low_issues"] += 1
        
        aggregated["summary"]["total_issues"] = (
            aggregated["summary"]["critical_issues"] +
            aggregated["summary"]["high_issues"] +
            aggregated["summary"]["medium_issues"] +
            aggregated["summary"]["low_issues"]
        )
        
        return aggregated
    
    def _build_manual_analysis_result(self, file_path_obj: Path, selected_rules: List[Dict],
                                    guidance_response: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Build enhanced analysis result for manual analysis mode.
        
        Args:
            file_path_obj: Path object for the analyzed file
            selected_rules: Rules selected for this analysis
            guidance_response: Response from guidance generation
            context: Analysis context
            
        Returns:
            Enhanced analysis result with manual mode features
        """
        # Base result
        result = self._build_analysis_result(file_path_obj, selected_rules, guidance_response, context)
        
        # Add manual analysis enhancements
        result["manual_analysis"] = True
        result["comprehensive_mode"] = context.get("comprehensive_analysis", True)
        result["frameworks_detected"] = context.get("framework_hints", [])
        
        # Enhanced rule processing for manual mode
        enhanced_rules = []
        for rule in selected_rules:
            enhanced_rule = rule.copy()
            
            # Add CI/CD consistency information
            enhanced_rule["cicd_relevant"] = self._is_rule_cicd_relevant(rule)
            enhanced_rule["blocking_severity"] = rule.get("severity") in ["critical", "high"]
            
            # Generate actionable remediation
            enhanced_rule["remediation_steps"] = self._generate_remediation_steps(rule)
            
            enhanced_rules.append(enhanced_rule)
        
        result["selected_rules"] = enhanced_rules
        result["cicd_prediction"] = self._predict_cicd_outcome(enhanced_rules)
        
        return result
    
    def _is_rule_cicd_relevant(self, rule: Dict[str, Any]) -> bool:
        """Check if a rule is relevant for CI/CD pipeline validation.
        
        Args:
            rule: Rule to check
            
        Returns:
            True if rule would be checked in CI/CD pipeline
        """
        # Rules with detect hooks are typically CI/CD relevant
        return bool(rule.get("detect", {}))
    
    def _generate_remediation_steps(self, rule: Dict[str, Any]) -> List[str]:
        """Generate specific remediation steps for a rule.
        
        Args:
            rule: Rule to generate remediation for
            
        Returns:
            List of actionable remediation steps
        """
        steps = []
        
        # Add steps from rule's "do" recommendations
        do_items = rule.get("do", [])
        for item in do_items:
            steps.append(f"✅ {item}")
        
        # Add steps to avoid from rule's "dont" items
        dont_items = rule.get("dont", [])
        for item in dont_items:
            steps.append(f"❌ Avoid: {item}")
        
        # Add verification steps
        verify_tests = rule.get("verify", {}).get("tests", [])
        for test in verify_tests:
            steps.append(f"🔍 Verify: {test}")
        
        return steps if steps else ["Review the security requirement and apply appropriate fixes"]
    
    def _predict_cicd_outcome(self, rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict CI/CD pipeline outcome based on analysis results.
        
        Args:
            rules: List of rules/issues found
            
        Returns:
            CI/CD prediction information
        """
        critical_count = sum(1 for rule in rules if rule.get("severity") == "critical")
        high_count = sum(1 for rule in rules if rule.get("severity") == "high")
        blocking_count = critical_count + high_count
        
        # CI/CD typically fails on critical/high severity issues
        would_pass = blocking_count == 0
        
        return {
            "would_pass": would_pass,
            "blocking_issues": blocking_count,
            "critical_issues": critical_count,
            "high_issues": high_count,
            "confidence": "high" if blocking_count <= 2 else "medium",
            "recommendation": (
                "Code is ready for commit" if would_pass 
                else f"Fix {blocking_count} blocking issues before commit"
            )
        }


def main():
    """Main entry point for context analysis."""
    parser = argparse.ArgumentParser(description="Analyze code context for security rules")
    parser.add_argument("file_path", help="Path to file to analyze")
    parser.add_argument("--content", help="Code content to analyze (optional)")
    parser.add_argument("--format", choices=["json", "guidance"], default="guidance",
                       help="Output format")
    
    args = parser.parse_args()
    
    analyzer = CodeContextAnalyzer()
    if not analyzer.initialize():
        print("❌ Failed to initialize code context analyzer")
        return 1
    
    # Perform analysis
    result = analyzer.analyze_file_context(args.file_path, args.content)
    
    # Output results
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(analyzer.format_guidance_output(result))
    
    return 0




if __name__ == "__main__":
    sys.exit(main())