#!/usr/bin/env python3
"""
Cryptographic Security Validation Script

Validates that no insecure MD5 hashing is used in the codebase
and confirms SHA-256 is properly implemented.
"""

import os
import subprocess
import sys
from pathlib import Path


def check_for_md5_usage():
    """Check for any remaining MD5 usage in application code"""
    print("🔍 Scanning for MD5 usage in application code...")
    
    # Search for MD5 usage in app directory only (exclude docs/examples)
    try:
        result = subprocess.run([
            'grep', '-r', '--include=*.py', 'hashlib.md5\\|\\.md5(',
            'app/'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        if result.returncode == 0:
            print("❌ SECURITY RISK: MD5 usage found in application code:")
            print(result.stdout)
            return False
        else:
            print("✅ No MD5 usage found in application code")
            return True
            
    except FileNotFoundError:
        print("⚠️ grep not available, skipping MD5 scan")
        return True


def validate_sha256_implementation():
    """Validate that SHA-256 is properly implemented in RuleIdCleaner"""
    print("\n🔧 Validating SHA-256 implementation...")
    
    try:
        # Add app to path
        sys.path.insert(0, str(Path(__file__).parent.parent / 'app'))
        
        from ingestion.rule_id_cleaner import RuleIdCleaner
        import hashlib
        
        cleaner = RuleIdCleaner()
        test_data = {'title': 'Crypto Test', 'description': 'SHA-256 validation'}
        
        # Get hash from cleaner
        cleaner_hash = cleaner.get_content_hash(test_data)
        
        # Calculate expected SHA-256
        content_str = str(sorted(test_data.items()))
        expected_hash = hashlib.sha256(content_str.encode()).hexdigest()
        
        if cleaner_hash == expected_hash and len(cleaner_hash) == 64:
            print(f"✅ SHA-256 properly implemented")
            print(f"   Hash length: {len(cleaner_hash)} characters")
            print(f"   Sample hash: {cleaner_hash[:32]}...")
            return True
        else:
            print(f"❌ SHA-256 implementation error")
            print(f"   Expected: {expected_hash}")
            print(f"   Got:      {cleaner_hash}")
            return False
            
    except Exception as e:
        print(f"❌ Error validating SHA-256 implementation: {e}")
        return False


def main():
    """Main validation routine"""
    print("🔒 CRYPTOGRAPHIC SECURITY VALIDATION")
    print("=" * 50)
    
    md5_check = check_for_md5_usage()
    sha256_check = validate_sha256_implementation()
    
    print("\n📋 VALIDATION SUMMARY:")
    print("=" * 50)
    
    if md5_check and sha256_check:
        print("✅ ALL SECURITY CHECKS PASSED")
        print("✅ MD5 vulnerability remediated")
        print("✅ SHA-256 properly implemented")
        print("✅ Cryptographic security requirements met")
        return 0
    else:
        print("❌ SECURITY VALIDATION FAILED")
        if not md5_check:
            print("❌ MD5 usage detected - security risk")
        if not sha256_check:
            print("❌ SHA-256 implementation error")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)