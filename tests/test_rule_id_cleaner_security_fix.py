#!/usr/bin/env python3
"""
Security fix test for RuleIdCleaner - MD5 to SHA-256 migration
Tests the cryptographic hash upgrade and ensures functionality.
"""

# import pytest  # Not needed for direct execution
import hashlib
from pathlib import Path
import tempfile
import yaml
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from ingestion.rule_id_cleaner import RuleIdCleaner


class TestRuleIdCleanerSecurityFix:
    """Test suite for MD5 to SHA-256 security fix"""
    
    def test_hash_algorithm_is_sha256(self):
        """Verify that SHA-256 is used instead of insecure MD5"""
        cleaner = RuleIdCleaner()
        test_data = {
            'title': 'Test Rule',
            'description': 'Test Description',
            'category': 'test'
        }
        
        # Generate hash using the cleaner
        result_hash = cleaner.get_content_hash(test_data)
        
        # Manually generate expected SHA-256 hash
        content_str = str(sorted(test_data.items()))
        expected_hash = hashlib.sha256(content_str.encode()).hexdigest()
        
        # Verify they match
        assert result_hash == expected_hash, "Hash should be SHA-256"
        
    def test_hash_length_is_sha256(self):
        """Verify hash length is 64 characters (SHA-256), not 32 (MD5)"""
        cleaner = RuleIdCleaner()
        test_data = {'title': 'Test Rule'}
        
        result_hash = cleaner.get_content_hash(test_data)
        
        # SHA-256 produces 64-character hex string, MD5 produces 32
        assert len(result_hash) == 64, f"SHA-256 hash should be 64 chars, got {len(result_hash)}"
        
    def test_hash_excludes_id_field(self):
        """Verify that ID field is excluded from hash calculation"""
        cleaner = RuleIdCleaner()
        
        test_data1 = {
            'id': 'RULE-001',
            'title': 'Test Rule',
            'description': 'Test Description'
        }
        
        test_data2 = {
            'id': 'RULE-002', # Different ID
            'title': 'Test Rule',
            'description': 'Test Description'
        }
        
        hash1 = cleaner.get_content_hash(test_data1)
        hash2 = cleaner.get_content_hash(test_data2)
        
        # Hashes should be identical despite different IDs
        assert hash1 == hash2, "Hashes should be same when only ID differs"
        
    def test_different_content_produces_different_hashes(self):
        """Verify that different content produces different hashes"""
        cleaner = RuleIdCleaner()
        
        test_data1 = {'title': 'Rule One', 'category': 'auth'}
        test_data2 = {'title': 'Rule Two', 'category': 'auth'}
        
        hash1 = cleaner.get_content_hash(test_data1)
        hash2 = cleaner.get_content_hash(test_data2)
        
        assert hash1 != hash2, "Different content should produce different hashes"
        
    def test_hash_consistency(self):
        """Verify that same content produces same hash consistently"""
        cleaner = RuleIdCleaner()
        test_data = {
            'title': 'Consistent Test Rule',
            'description': 'This should hash consistently',
            'severity': 'HIGH'
        }
        
        # Generate hash multiple times
        hash1 = cleaner.get_content_hash(test_data)
        hash2 = cleaner.get_content_hash(test_data)
        hash3 = cleaner.get_content_hash(test_data)
        
        assert hash1 == hash2 == hash3, "Same content should always produce same hash"
        
    def test_hash_is_not_md5(self):
        """Security test: Verify hash is definitely not MD5"""
        cleaner = RuleIdCleaner()
        test_data = {'title': 'Security Test'}
        
        result_hash = cleaner.get_content_hash(test_data)
        
        # Generate what MD5 would produce
        content_str = str(sorted(test_data.items()))
        md5_hash = hashlib.md5(content_str.encode()).hexdigest()
        
        # Verify they're different
        assert result_hash != md5_hash, "Hash must not be MD5 (security vulnerability)"
        
    def test_duplicate_detection_still_works(self):
        """Integration test: Verify duplicate detection still works with SHA-256"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create test rule cards with identical content (except ID)
            rule1_data = {
                'id': 'TEST-001',
                'title': 'Duplicate Rule',
                'description': 'This is a duplicate rule'
            }
            
            rule2_data = {
                'id': 'TEST-002',  # Different ID
                'title': 'Duplicate Rule',
                'description': 'This is a duplicate rule'
            }
            
            # Write to files
            rule1_path = tmpdir_path / "rule1.yml"
            rule2_path = tmpdir_path / "rule2.yml"
            
            with open(rule1_path, 'w') as f:
                yaml.safe_dump(rule1_data, f)
                
            with open(rule2_path, 'w') as f:
                yaml.safe_dump(rule2_data, f)
            
            # Test duplicate detection
            cleaner = RuleIdCleaner(tmpdir_path)
            duplicates = cleaner.find_duplicates_in_domain(tmpdir_path)
            
            # Should find one group of duplicates
            assert len(duplicates) == 1, "Should find exactly one group of duplicates"
            
            # The duplicate group should contain both files
            duplicate_files = list(duplicates.values())[0]
            assert len(duplicate_files) == 2, "Duplicate group should contain both files"


if __name__ == "__main__":
    # Run the tests
    test_suite = TestRuleIdCleanerSecurityFix()
    
    print("🔒 Running Security Fix Tests for MD5 → SHA-256 Migration")
    print("=" * 60)
    
    try:
        test_suite.test_hash_algorithm_is_sha256()
        print("✅ SHA-256 algorithm verification: PASSED")
        
        test_suite.test_hash_length_is_sha256()
        print("✅ SHA-256 hash length verification: PASSED")
        
        test_suite.test_hash_excludes_id_field()
        print("✅ ID field exclusion: PASSED")
        
        test_suite.test_different_content_produces_different_hashes()
        print("✅ Hash uniqueness: PASSED")
        
        test_suite.test_hash_consistency()
        print("✅ Hash consistency: PASSED")
        
        test_suite.test_hash_is_not_md5()
        print("✅ MD5 security vulnerability fix: PASSED")
        
        test_suite.test_duplicate_detection_still_works()
        print("✅ Duplicate detection functionality: PASSED")
        
        print("\n🎉 All security fix tests PASSED!")
        print("✅ MD5 vulnerability successfully remediated with SHA-256")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)