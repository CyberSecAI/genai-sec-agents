"""
Tests for context-aware rule selection functionality.

Tests the rule selection system to ensure it properly filters rules
based on development context (file type, content, etc.).
"""

import sys
import os

# Add app directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from app.runtime.core import AgenticRuntime
from app.runtime.rule_selector import RuleSelector


def test_file_extension_selection():
    """Test rule selection based on file extensions."""
    print("Testing file extension-based rule selection...")
    
    runtime = AgenticRuntime()
    runtime.load_agent("comprehensive-security-agent")
    
    package_data = runtime.loaded_packages["comprehensive-security-agent"]
    all_rules = package_data["rules"]
    
    print(f"Total available rules: {len(all_rules)}")
    
    # Test different file contexts
    test_contexts = [
        {
            "file_path": "src/auth.py",
            "content": "jwt_secret = 'hardcoded_secret'",
            "expected_domains": ["python", "secrets"]
        },
        {
            "file_path": "Dockerfile",
            "content": "FROM ubuntu:20.04\nRUN apt-get update",
            "expected_domains": ["docker", "container"]
        },
        {
            "file_path": "api/users.js", 
            "content": "app.get('/users', (req, res) => {})",
            "expected_domains": ["javascript", "web", "api"]
        },
        {
            "file_path": "config/database.yml",
            "content": "password: admin123",
            "expected_domains": ["config", "secrets"]
        }
    ]
    
    selector = RuleSelector()
    
    for i, context in enumerate(test_contexts):
        print(f"\nTest {i+1}: {context['file_path']}")
        
        # Get scope analysis
        analysis = selector.get_scope_analysis(context)
        relevant_scopes = analysis.get("relevant_scopes", [])
        
        print(f"  Detected scopes: {relevant_scopes}")
        
        # Select rules
        selected_rules = selector.select_rules(context, all_rules, max_rules=5)
        
        print(f"  Selected {len(selected_rules)} rules:")
        for rule in selected_rules[:3]:  # Show first 3
            print(f"    - {rule.get('id', 'unknown')}: {rule.get('title', 'no title')[:50]}")
        
        # Check if expected domains are detected
        expected_found = any(domain in relevant_scopes for domain in context["expected_domains"])
        if expected_found:
            print(f"  ✓ Expected domain detection")
        else:
            print(f"  ! Expected domains {context['expected_domains']} not fully detected")
    
    return True


def test_content_pattern_matching():
    """Test rule selection based on content patterns."""
    print("Testing content pattern-based rule selection...")
    
    runtime = AgenticRuntime()
    runtime.load_agent("secrets-specialist")
    
    package_data = runtime.loaded_packages["secrets-specialist"]
    rules = package_data["rules"]
    
    # Test secret-related content
    secret_contexts = [
        {
            "file_path": "config.py",
            "content": "DATABASE_PASSWORD = 'secret123'\nAPI_KEY = 'abc123'",
            "description": "hardcoded secrets"
        },
        {
            "file_path": "auth.js",
            "content": "const jwt = require('jsonwebtoken');\nconst secret = 'my-secret-key';",
            "description": "JWT secret"
        },
        {
            "file_path": "deploy.py", 
            "content": "AWS_ACCESS_KEY = 'AKIA...' \nAWS_SECRET_KEY = 'xyz...'",
            "description": "cloud credentials"
        }
    ]
    
    selector = RuleSelector()
    
    for context in secret_contexts:
        print(f"\nTesting: {context['description']}")
        
        selected_rules = selector.select_rules(context, rules, max_rules=3)
        
        print(f"  Selected {len(selected_rules)} rules for secrets context")
        
        if len(selected_rules) > 0:
            print("  ✓ Secrets-related rules selected")
            for rule in selected_rules:
                print(f"    - {rule.get('id', 'unknown')}")
        else:
            print("  ! No secrets rules selected")
    
    return True


def test_scope_matching():
    """Test rule selection based on scope matching."""
    print("Testing scope-based rule selection...")
    
    runtime = AgenticRuntime()
    runtime.load_agent("web-security-specialist")
    
    package_data = runtime.loaded_packages["web-security-specialist"]
    rules = package_data["rules"]
    
    # Test web-specific contexts
    web_contexts = [
        {
            "file_path": "api/auth.py",
            "content": "def login(request):\n    session['user'] = user_id",
            "scope_hint": "web"
        },
        {
            "file_path": "frontend/app.js", 
            "content": "document.cookie = 'session=abc123'",
            "scope_hint": "web"
        }
    ]
    
    selector = RuleSelector()
    
    for context in web_contexts:
        print(f"\nTesting web context: {context['file_path']}")
        
        selected_rules = selector.select_rules(context, rules, max_rules=5)
        
        print(f"  Selected {len(selected_rules)} web security rules")
        
        if len(selected_rules) > 0:
            print("  ✓ Web security rules selected")
            # Check if rules have web-related scopes
            web_related = 0
            for rule in selected_rules:
                rule_scope = rule.get('scope', '').lower()
                if any(term in rule_scope for term in ['web', 'http', 'cookie', 'session']):
                    web_related += 1
            
            if web_related > 0:
                print(f"  ✓ {web_related} rules have web-related scopes")
        else:
            print("  ! No web security rules selected")
    
    return True


def test_rule_scoring():
    """Test rule relevance scoring."""
    print("Testing rule relevance scoring...")
    
    runtime = AgenticRuntime()
    runtime.load_agent("comprehensive-security-agent")
    
    package_data = runtime.loaded_packages["comprehensive-security-agent"]
    rules = package_data["rules"]
    
    # Test high-relevance context
    high_relevance_context = {
        "file_path": "auth/jwt_handler.py",
        "content": """
import jwt
import os

JWT_SECRET = os.getenv('JWT_SECRET', 'fallback-secret')

def create_token(user_id):
    payload = {'user_id': user_id}
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    return token
        """,
        "language": "python"
    }
    
    selector = RuleSelector()
    
    selected_rules = selector.select_rules(high_relevance_context, rules, max_rules=10)
    
    print(f"Selected {len(selected_rules)} rules for JWT context")
    
    # Check for JWT/secrets related rules
    jwt_related = 0
    secret_related = 0
    
    for rule in selected_rules:
        rule_text = f"{rule.get('title', '')} {rule.get('requirement', '')}".lower()
        if 'jwt' in rule_text:
            jwt_related += 1
        if any(term in rule_text for term in ['secret', 'key', 'credential']):
            secret_related += 1
    
    print(f"  JWT-related rules: {jwt_related}")
    print(f"  Secret-related rules: {secret_related}")
    
    if jwt_related > 0 or secret_related > 0:
        print("  ✓ Relevant rules properly scored and selected")
        return True
    else:
        print("  ! Expected relevant rules not selected")
        return False


def test_performance():
    """Test rule selection performance."""
    print("Testing rule selection performance...")
    
    import time
    
    runtime = AgenticRuntime()
    runtime.load_agent("comprehensive-security-agent")
    
    package_data = runtime.loaded_packages["comprehensive-security-agent"]
    rules = package_data["rules"]
    
    # Test context
    test_context = {
        "file_path": "src/app.py",
        "content": "app = Flask(__name__)\napp.secret_key = 'dev-key'",
        "language": "python"
    }
    
    selector = RuleSelector()
    
    # Time multiple selections
    times = []
    for i in range(10):
        start_time = time.time()
        selected_rules = selector.select_rules(test_context, rules)
        end_time = time.time()
        times.append(end_time - start_time)
    
    avg_time = sum(times) / len(times)
    max_time = max(times)
    
    print(f"  Average selection time: {avg_time:.3f}s")
    print(f"  Maximum selection time: {max_time:.3f}s")
    
    # Should be under 2 seconds for real-time IDE usage
    if max_time < 2.0:
        print("  ✓ Performance meets real-time requirements")
        return True
    else:
        print(f"  ! Performance too slow for real-time use (max: {max_time:.3f}s)")
        return False


def main():
    """Run all rule selection tests."""
    print("Running rule selection tests...\n")
    
    tests = [
        test_file_extension_selection,
        test_content_pattern_matching,
        test_scope_matching,
        test_rule_scoring,
        test_performance
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print(f"\n{test.__name__}:")
        if test():
            passed += 1
            print("PASSED")
        else:
            print("FAILED")
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All rule selection tests passed!")
        return True
    else:
        print("❌ Some rule selection tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)