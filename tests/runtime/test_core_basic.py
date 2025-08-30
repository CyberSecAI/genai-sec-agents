"""
Basic tests for AgenticRuntime core functionality.

Tests the core infrastructure components to ensure they initialize
properly and handle basic operations securely.
"""

import sys
import os

# Add app directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from app.runtime.core import AgenticRuntime, AgenticRuntimeError
from app.runtime.package_loader import PackageLoader, PackageLoaderError


def test_runtime_initialization():
    """Test AgenticRuntime initializes properly."""
    print("Testing AgenticRuntime initialization...")
    
    # Test with default directory
    try:
        runtime = AgenticRuntime()
        assert runtime.package_directory.endswith('app/dist/agents')
        print("✓ Default initialization successful")
    except Exception as e:
        print(f"✗ Default initialization failed: {e}")
        return False
    
    # Test with custom directory (should fail if doesn't exist)
    try:
        runtime = AgenticRuntime("/nonexistent/path")
        print("✗ Should have failed with invalid path")
        return False
    except AgenticRuntimeError:
        print("✓ Invalid path properly rejected")
    
    return True


def test_package_loader_security():
    """Test PackageLoader security validations."""
    print("Testing PackageLoader security features...")
    
    loader = PackageLoader()
    
    # Test invalid file paths
    invalid_paths = [
        "",
        None,
        "/etc/passwd",
        "../../../etc/passwd",
        "nonexistent.json"
    ]
    
    for path in invalid_paths:
        try:
            result = loader.load_package(path)
            if result is not None:
                print(f"✗ Should have rejected invalid path: {path}")
                return False
        except (PackageLoaderError, TypeError):
            print(f"✓ Properly rejected invalid path: {path}")
    
    return True


def test_agent_name_sanitization():
    """Test agent name sanitization."""
    print("Testing agent name sanitization...")
    
    runtime = AgenticRuntime()
    
    # Test valid names
    valid_names = ["secrets-specialist", "web_security", "test123"]
    for name in valid_names:
        try:
            sanitized = runtime._sanitize_agent_name(name)
            assert sanitized == name
            print(f"✓ Valid name unchanged: {name}")
        except Exception as e:
            print(f"✗ Valid name rejected: {name} - {e}")
            return False
    
    # Test invalid names
    invalid_names = ["../secrets", "test/path", "", None]
    for name in invalid_names:
        try:
            sanitized = runtime._sanitize_agent_name(name)
            if name is not None and sanitized == name:
                print(f"✗ Invalid name not sanitized: {name}")
                return False
            print(f"✓ Invalid name properly handled: {name}")
        except AgenticRuntimeError:
            print(f"✓ Invalid name properly rejected: {name}")
    
    return True


def test_context_validation():
    """Test context input validation."""
    print("Testing context validation...")
    
    runtime = AgenticRuntime()
    
    # Test valid context
    valid_context = {
        "file_path": "src/test.py",
        "content": "password = 'secret'",
        "language": "python"
    }
    
    try:
        validated = runtime._validate_context(valid_context)
        assert "file_path" in validated
        assert "content" in validated
        print("✓ Valid context properly validated")
    except Exception as e:
        print(f"✗ Valid context rejected: {e}")
        return False
    
    # Test invalid context types
    invalid_contexts = [None, "string", [], 123]
    for context in invalid_contexts:
        try:
            validated = runtime._validate_context(context)
            print(f"✗ Invalid context type accepted: {type(context)}")
            return False
        except AgenticRuntimeError:
            print(f"✓ Invalid context type rejected: {type(context)}")
    
    return True


def main():
    """Run all basic tests."""
    print("Running basic AgenticRuntime tests...\n")
    
    tests = [
        test_runtime_initialization,
        test_package_loader_security,
        test_agent_name_sanitization,
        test_context_validation
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
        print("🎉 All basic tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)