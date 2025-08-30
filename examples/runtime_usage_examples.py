"""
AgenticRuntime Usage Examples

Demonstrates common usage patterns and integration scenarios
for the AgenticRuntime security guidance system.
"""

import sys
import os

# Add app directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from app.runtime import AgenticRuntime


def example_1_basic_usage():
    """Example 1: Basic runtime usage with manual agent selection."""
    print("=" * 50)
    print("Example 1: Basic Usage")
    print("=" * 50)
    
    # Initialize runtime
    runtime = AgenticRuntime()
    
    # Load a specific agent
    print("Loading secrets specialist...")
    success = runtime.load_agent("secrets-specialist")
    
    if not success:
        print("❌ Failed to load agent")
        return
    
    print("✅ Agent loaded successfully")
    
    # Define code context with hardcoded secret
    context = {
        "file_path": "auth/jwt_handler.py",
        "content": """
import jwt
import os

# BAD: Hardcoded JWT secret
JWT_SECRET = 'my-super-secret-key'

def create_token(user_id):
    payload = {'user_id': user_id, 'exp': time.time() + 3600}
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')
        """,
        "language": "python"
    }
    
    # Get security guidance
    print("\nAnalyzing code for security issues...")
    guidance = runtime.get_guidance(context, agent_name="secrets-specialist")
    
    if guidance:
        print(f"\n🔍 Analysis Results:")
        print(f"   Agent Used: {guidance['agent_used']}")
        print(f"   Severity: {guidance['severity'].upper()}")
        print(f"   Rules Applied: {guidance['rules_applied']}")
        print(f"\n💡 Guidance:")
        print(f"   {guidance['guidance']}")
        
        if guidance['suggestions']:
            print(f"\n📋 Suggestions:")
            for i, suggestion in enumerate(guidance['suggestions'], 1):
                print(f"   {i}. {suggestion}")
    else:
        print("❌ No guidance generated")


def example_2_auto_agent_selection():
    """Example 2: Automatic agent selection based on context."""
    print("\n" + "=" * 50)
    print("Example 2: Auto Agent Selection")
    print("=" * 50)
    
    runtime = AgenticRuntime()
    
    # Test different contexts that should trigger different agents
    test_cases = [
        {
            "name": "Dockerfile Analysis",
            "context": {
                "file_path": "deploy/Dockerfile",
                "content": """
FROM ubuntu:latest
USER root
RUN apt-get update && apt-get install -y curl
COPY . /app
EXPOSE 8080
                """,
                "language": "dockerfile"
            },
            "expected_agent": "container-security-specialist"
        },
        {
            "name": "Web Cookie Security",
            "context": {
                "file_path": "web/session.js",
                "content": """
// Setting session cookie
document.cookie = "session=" + sessionId + "; path=/";

// Express.js cookie handling
app.use(session({
    secret: 'keyboard cat',
    cookie: { secure: false }
}));
                """,
                "language": "javascript"
            },
            "expected_agent": "web-security-specialist"
        },
        {
            "name": "GenAI Integration",
            "context": {
                "file_path": "ai/chat.py", 
                "content": """
import openai

# Configure OpenAI client
openai.api_key = "sk-..."

def generate_response(user_input):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_input}]
    )
    return response.choices[0].message.content
                """,
                "language": "python"
            },
            "expected_agent": "genai-security-specialist"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🔍 {test_case['name']}:")
        
        # Let runtime auto-select agent
        guidance = runtime.get_guidance(test_case["context"])
        
        if guidance:
            selected_agent = guidance['agent_used']
            expected_agent = test_case['expected_agent']
            
            print(f"   Expected Agent: {expected_agent}")
            print(f"   Selected Agent: {selected_agent}")
            
            if selected_agent == expected_agent:
                print("   ✅ Correct agent selection")
            else:
                print("   ℹ️  Different agent selected (may still be appropriate)")
            
            print(f"   Severity: {guidance['severity'].upper()}")
            print(f"   Rules Applied: {guidance['rules_applied']}")
        else:
            print("   ❌ No guidance generated")


def example_3_multi_agent_workflow():
    """Example 3: Working with multiple agents for comprehensive analysis."""
    print("\n" + "=" * 50)
    print("Example 3: Multi-Agent Workflow")
    print("=" * 50)
    
    runtime = AgenticRuntime()
    
    # Load multiple agents
    agents_to_load = [
        "secrets-specialist",
        "web-security-specialist", 
        "container-security-specialist"
    ]
    
    print("Loading multiple agents...")
    loaded_agents = []
    
    for agent in agents_to_load:
        if runtime.load_agent(agent):
            loaded_agents.append(agent)
            print(f"   ✅ {agent}")
        else:
            print(f"   ❌ {agent}")
    
    print(f"\nLoaded {len(loaded_agents)} agents successfully")
    
    # Complex code example with multiple security domains
    complex_context = {
        "file_path": "app/main.py",
        "content": """
import os
from flask import Flask, request, session, make_response
import jwt
import psycopg2

app = Flask(__name__)

# Multiple security issues:
app.secret_key = 'dev-secret'  # Hardcoded secret
DATABASE_PASSWORD = 'admin123'  # Hardcoded DB password

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    # SQL injection vulnerability
    conn = psycopg2.connect(f"host=localhost dbname=app user=postgres password={DATABASE_PASSWORD}")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE username='{username}' AND password='{password}'")
    user = cursor.fetchone()
    
    if user:
        # JWT with hardcoded secret
        token = jwt.encode({'user_id': user[0]}, 'jwt-secret', algorithm='HS256')
        
        # Insecure cookie
        response = make_response("Login successful")
        response.set_cookie('auth_token', token, secure=False, httponly=False)
        return response
    
    return "Invalid credentials", 401
        """,
        "language": "python",
        "framework": "flask"
    }
    
    print(f"\n🔍 Analyzing complex code with multiple security issues...")
    
    # Analyze with different agents
    results = {}
    
    for agent in loaded_agents:
        print(f"\n   📋 Analysis with {agent}:")
        guidance = runtime.get_guidance(complex_context, agent_name=agent)
        
        if guidance:
            results[agent] = guidance
            print(f"      Severity: {guidance['severity'].upper()}")
            print(f"      Rules Applied: {guidance['rules_applied']}")
            print(f"      Guidance: {guidance['guidance'][:100]}...")
        else:
            print(f"      ❌ No guidance from {agent}")
    
    # Summary
    print(f"\n📊 Analysis Summary:")
    print(f"   Agents analyzed: {len(results)}")
    
    if results:
        all_severities = [r['severity'] for r in results.values()]
        severity_counts = {s: all_severities.count(s) for s in set(all_severities)}
        print(f"   Severity distribution: {severity_counts}")
        
        total_rules = sum(r['rules_applied'] for r in results.values())
        print(f"   Total rules applied: {total_rules}")


def example_4_error_handling():
    """Example 4: Proper error handling and edge cases."""
    print("\n" + "=" * 50)
    print("Example 4: Error Handling")
    print("=" * 50)
    
    from app.runtime.core import AgenticRuntimeError
    
    # Test error scenarios
    print("Testing error handling scenarios...\n")
    
    # 1. Invalid package directory
    print("1. Invalid package directory:")
    try:
        runtime = AgenticRuntime(package_directory="/nonexistent/path")
        print("   ❌ Should have raised error")
    except AgenticRuntimeError as e:
        print(f"   ✅ Properly caught error: {e}")
    
    # 2. Valid runtime for other tests
    runtime = AgenticRuntime()
    
    # 3. Invalid agent name
    print("\n2. Invalid agent name:")
    success = runtime.load_agent("nonexistent-agent")
    if not success:
        print("   ✅ Properly handled invalid agent name")
    
    # 4. Invalid context
    print("\n3. Invalid context types:")
    invalid_contexts = [
        ("String context", "not a dict"),
        ("None context", None),
        ("List context", ["not", "a", "dict"])
    ]
    
    for name, invalid_context in invalid_contexts:
        guidance = runtime.get_guidance(invalid_context)
        if guidance is None:
            print(f"   ✅ {name} properly rejected")
        else:
            print(f"   ❌ {name} should have been rejected")
    
    # 5. Oversized content
    print("\n4. Oversized content handling:")
    large_context = {
        "file_path": "large_file.py",
        "content": "x" * (2 * 1024 * 1024)  # 2MB content
    }
    
    guidance = runtime.get_guidance(large_context)
    if guidance is None:
        print("   ✅ Oversized content properly rejected")
    else:
        print("   ℹ️  Oversized content was sanitized and processed")


def example_5_performance_demo():
    """Example 5: Performance characteristics demonstration."""
    print("\n" + "=" * 50)
    print("Example 5: Performance Demo")
    print("=" * 50)
    
    import time
    
    runtime = AgenticRuntime()
    
    # Load comprehensive agent for testing
    print("Loading comprehensive security agent...")
    start_time = time.time()
    success = runtime.load_agent("comprehensive-security-agent")
    load_time = time.time() - start_time
    
    if success:
        print(f"✅ Agent loaded in {load_time:.3f}s")
    else:
        print("❌ Failed to load agent")
        return
    
    # Test guidance generation performance
    test_context = {
        "file_path": "performance_test.py",
        "content": """
def authenticate_user(username, password):
    # Multiple potential security issues for comprehensive analysis
    api_key = "hardcoded-api-key-12345"
    db_password = "admin123"
    jwt_secret = "my-secret-key"
    
    # SQL query construction
    query = f"SELECT * FROM users WHERE username='{username}'"
    
    # JWT token creation
    import jwt
    token = jwt.encode({"user": username}, jwt_secret, algorithm="HS256")
    
    return token
        """,
        "language": "python"
    }
    
    print(f"\nTesting guidance generation performance...")
    
    # Run multiple iterations to get average
    times = []
    for i in range(10):
        start_time = time.time()
        guidance = runtime.get_guidance(test_context)
        end_time = time.time()
        times.append(end_time - start_time)
    
    avg_time = sum(times) / len(times)
    max_time = max(times)
    min_time = min(times)
    
    print(f"   Average response time: {avg_time:.3f}s")
    print(f"   Fastest response: {min_time:.3f}s")
    print(f"   Slowest response: {max_time:.3f}s")
    
    # Performance rating
    if max_time < 0.1:
        print("   🚀 Performance: Excellent (< 100ms)")
    elif max_time < 0.5:
        print("   ⚡ Performance: Very Good (< 500ms)")
    elif max_time < 2.0:
        print("   ✅ Performance: Good (< 2s) - Meets IDE requirements")
    else:
        print("   ⚠️  Performance: Needs optimization (> 2s)")
    
    # Show sample result
    if guidance:
        print(f"\n   Rules applied: {guidance['rules_applied']}")
        print(f"   Severity: {guidance['severity']}")
        print(f"   Agent: {guidance['agent_used']}")


def main():
    """Run all usage examples."""
    print("🚀 AgenticRuntime Usage Examples")
    print("Demonstrating security guidance capabilities")
    
    try:
        example_1_basic_usage()
        example_2_auto_agent_selection()
        example_3_multi_agent_workflow()
        example_4_error_handling()
        example_5_performance_demo()
        
        print("\n" + "=" * 50)
        print("✅ All examples completed successfully!")
        print("=" * 50)
        print("\nThe AgenticRuntime is ready for IDE integration.")
        print("See app/runtime/README.md for detailed API documentation.")
        
    except Exception as e:
        print(f"\n❌ Example execution failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()