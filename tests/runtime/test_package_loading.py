"""
Tests for package loading functionality with real compiled packages.

Tests the package loading system using the actual compiled agent packages
from Story 1.3 to ensure compatibility and proper validation.
"""

import sys
import os
import json

# Add app directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from app.runtime.core import AgenticRuntime, AgenticRuntimeError
from app.runtime.package_loader import PackageLoader, PackageLoaderError


def test_load_all_compiled_packages():
    """Test loading all 5 compiled agent packages."""
    print("Testing loading of all compiled agent packages...")
    
    runtime = AgenticRuntime()
    
    # List of expected agent packages
    expected_agents = [
        "secrets-specialist",
        "web-security-specialist", 
        "genai-security-specialist",
        "container-security-specialist",
        "comprehensive-security-agent"
    ]
    
    loaded_count = 0
    
    for agent_name in expected_agents:
        try:
            success = runtime.load_agent(agent_name)
            if success:
                print(f"✓ Successfully loaded: {agent_name}")
                loaded_count += 1
            else:
                print(f"✗ Failed to load: {agent_name}")
        except Exception as e:
            print(f"✗ Error loading {agent_name}: {e}")
    
    print(f"Loaded {loaded_count}/{len(expected_agents)} packages")
    return loaded_count == len(expected_agents)


def test_package_structure_validation():
    """Test package structure validation with real packages."""
    print("Testing package structure validation...")
    
    loader = PackageLoader()
    
    # Test with secrets specialist package
    package_path = "app/dist/agents/secrets-specialist.json"
    
    try:
        package_data = loader.load_package(package_path)
        
        if package_data is None:
            print("✗ Failed to load package")
            return False
        
        # Validate expected structure
        required_top_level = ["agent", "rules", "validation_hooks"]
        for field in required_top_level:
            if field not in package_data:
                print(f"✗ Missing required field: {field}")
                return False
        
        print(f"✓ Package structure valid")
        
        # Validate agent metadata
        agent_meta = package_data["agent"]
        required_agent_fields = ["name", "version", "build_date", "source_digest"]
        for field in required_agent_fields:
            if field not in agent_meta:
                print(f"✗ Missing agent field: {field}")
                return False
        
        print(f"✓ Agent metadata valid")
        
        # Validate rules array
        rules = package_data["rules"]
        if not isinstance(rules, list):
            print("✗ Rules is not an array")
            return False
        
        if len(rules) == 0:
            print("✗ No rules found in package")
            return False
        
        print(f"✓ Found {len(rules)} rules")
        
        # Validate first rule structure
        first_rule = rules[0]
        required_rule_fields = ["id", "title", "scope", "requirement"]
        for field in required_rule_fields:
            if field not in first_rule:
                print(f"✗ Missing rule field: {field}")
                return False
        
        print(f"✓ Rule structure valid")
        
        # Validate validation hooks
        hooks = package_data["validation_hooks"]
        if not isinstance(hooks, dict):
            print("✗ Validation hooks is not a dict")
            return False
        
        print(f"✓ Found validation hooks for {list(hooks.keys())}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error validating package: {e}")
        return False


def test_rule_extraction():
    """Test rule extraction and indexing."""
    print("Testing rule extraction...")
    
    runtime = AgenticRuntime()
    
    # Load secrets specialist
    if not runtime.load_agent("secrets-specialist"):
        print("✗ Failed to load secrets specialist")
        return False
    
    package_data = runtime.loaded_packages["secrets-specialist"]
    rules = package_data["rules"]
    
    print(f"Extracted {len(rules)} rules")
    
    # Test rule access
    for i, rule in enumerate(rules[:3]):  # Check first 3 rules
        print(f"  Rule {i+1}: {rule.get('id', 'unknown')} - {rule.get('title', 'no title')[:50]}")
        
        # Validate rule has required fields
        if not rule.get('id'):
            print(f"✗ Rule {i+1} missing ID")
            return False
        
        if not rule.get('scope'):
            print(f"✗ Rule {i+1} missing scope")
            return False
    
    print("✓ Rule extraction successful")
    return True


def test_metadata_extraction():
    """Test metadata extraction and attribution."""
    print("Testing metadata extraction...")
    
    runtime = AgenticRuntime()
    
    # Load comprehensive agent
    if not runtime.load_agent("comprehensive-security-agent"):
        print("✗ Failed to load comprehensive agent")
        return False
    
    package_data = runtime.loaded_packages["comprehensive-security-agent"]
    agent_meta = package_data["agent"]
    
    # Check metadata fields
    expected_meta = ["name", "version", "build_date", "source_digest"]
    for field in expected_meta:
        value = agent_meta.get(field)
        if not value:
            print(f"✗ Missing metadata: {field}")
            return False
        print(f"  {field}: {value}")
    
    # Check optional fields
    if "attribution" in agent_meta:
        attribution = agent_meta["attribution"]
        if len(attribution) > 0:
            print(f"✓ Attribution present ({len(attribution)} chars)")
        else:
            print("! Attribution field empty")
    
    if "domains" in agent_meta:
        domains = agent_meta["domains"]
        print(f"✓ Domains: {domains}")
    
    print("✓ Metadata extraction successful")
    return True


def test_validation_hooks_parsing():
    """Test validation hooks parsing and organization."""
    print("Testing validation hooks parsing...")
    
    runtime = AgenticRuntime()
    
    # Load web security specialist
    if not runtime.load_agent("web-security-specialist"):
        print("✗ Failed to load web security specialist")
        return False
    
    package_data = runtime.loaded_packages["web-security-specialist"]
    hooks = package_data["validation_hooks"]
    
    print(f"Found validation hooks for: {list(hooks.keys())}")
    
    # Check for expected scanner types
    expected_scanners = ["semgrep", "codeql"]  # These should be present
    
    for scanner in expected_scanners:
        if scanner in hooks:
            scanner_config = hooks[scanner]
            print(f"  {scanner}: {len(scanner_config)} rules")
        else:
            print(f"! {scanner} hooks not found (might be normal)")
    
    # Validate hook structure
    for scanner, config in hooks.items():
        if isinstance(config, list) and len(config) > 0:
            print(f"✓ {scanner} hooks valid")
        elif isinstance(config, dict):
            print(f"✓ {scanner} config valid (dict)")
        else:
            print(f"! {scanner} has unusual structure: {type(config)}")
    
    print("✓ Validation hooks parsing successful")
    return True


def main():
    """Run all package loading tests."""
    print("Running package loading tests...\n")
    
    tests = [
        test_load_all_compiled_packages,
        test_package_structure_validation,
        test_rule_extraction,
        test_metadata_extraction,
        test_validation_hooks_parsing
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
        print("🎉 All package loading tests passed!")
        return True
    else:
        print("❌ Some package loading tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)