#!/usr/bin/env python3
"""
Fix Numbering Consistency in Rule Cards
Ensures all rule cards follow consistent PREFIX-XXX.yml format with 3-digit numbers
"""

import os
import yaml
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

class NumberingConsistencyFixer:
    def __init__(self, rule_cards_path: str = "app/rule_cards"):
        self.rule_cards_path = Path(rule_cards_path)
        self.fixes_applied = []
        
        # Domain prefixes
        self.domain_prefixes = {
            'authentication': 'AUTH',
            'authorization': 'AUTHZ', 
            'configuration': 'CONFIG',
            'session_management': 'SESSION',
            'data_protection': 'DATA',
            'secure_communication': 'COMM',
            'file_handling': 'FILE',
            'cryptography': 'CRYPTO',
            'input_validation': 'INPUT',
            'web_security': 'WEB',
            'secure_coding': 'CODE',
            'logging': 'LOG',
            'network_security': 'NET',
            'cookies': 'COOKIE'
        }
    
    def fix_all_numbering_consistency(self):
        """Fix numbering consistency for all domains"""
        print("=== Fixing Numbering Consistency ===")
        
        for domain_path in self.rule_cards_path.iterdir():
            if domain_path.is_dir():
                domain = domain_path.name
                print(f"\nProcessing domain: {domain}")
                self.fix_domain_numbering(domain_path, domain)
        
        print(f"\n✅ Fixed {len(self.fixes_applied)} numbering inconsistencies")
        return self.fixes_applied
    
    def fix_domain_numbering(self, domain_path: Path, domain: str):
        """Fix numbering consistency for a single domain"""
        prefix = self.domain_prefixes.get(domain, domain.upper()[:6])
        
        # Get all YAML files and categorize them
        yaml_files = list(domain_path.glob("*.yml"))
        inconsistent_files = []
        standard_files = []
        
        for yaml_file in yaml_files:
            if self.is_standard_numbering(yaml_file.name, prefix):
                standard_files.append(yaml_file)
            else:
                inconsistent_files.append(yaml_file)
        
        if not inconsistent_files:
            print(f"  ✅ All files already have consistent numbering")
            return
        
        # Find used numbers in standard files
        used_numbers = self.extract_used_numbers(standard_files, prefix)
        
        print(f"  Found {len(inconsistent_files)} files with inconsistent numbering")
        
        # Process inconsistent files
        for yaml_file in inconsistent_files:
            self.fix_single_file_numbering(yaml_file, domain, prefix, used_numbers)
    
    def is_standard_numbering(self, filename: str, prefix: str) -> bool:
        """Check if filename follows standard PREFIX-XXX.yml format"""
        pattern = rf'^{re.escape(prefix)}-\d{{3}}\.yml$'
        return bool(re.match(pattern, filename))
    
    def extract_used_numbers(self, yaml_files: List[Path], prefix: str) -> Set[int]:
        """Extract numbers already used by standard files"""
        used_numbers = set()
        
        for yaml_file in yaml_files:
            match = re.search(rf'{re.escape(prefix)}-(\d+)', yaml_file.stem)
            if match:
                used_numbers.add(int(match.group(1)))
        
        return used_numbers
    
    def fix_single_file_numbering(self, yaml_file: Path, domain: str, prefix: str, used_numbers: Set[int]):
        """Fix numbering for a single file"""
        try:
            # Read file content to get rule data
            with open(yaml_file, 'r') as f:
                rule_data = yaml.safe_load(f)
            
            if not isinstance(rule_data, dict) or 'id' not in rule_data:
                print(f"  ❌ No ID found in {yaml_file.name}")
                return
            
            # Determine new number
            new_number = self.determine_new_number(yaml_file.name, rule_data['id'], used_numbers)
            
            # Generate new filename and ID
            new_filename = f"{prefix}-{new_number:03d}.yml"
            new_id = f"{prefix}-{new_number:03d}"
            new_path = yaml_file.parent / new_filename
            
            # Check if target already exists
            if new_path.exists():
                print(f"  ⚠️  Target exists: {new_filename}, finding alternative")
                new_number = self.find_next_available_number(used_numbers)
                new_filename = f"{prefix}-{new_number:03d}.yml"
                new_id = f"{prefix}-{new_number:03d}"
                new_path = yaml_file.parent / new_filename
            
            # Update rule data
            rule_data['id'] = new_id
            used_numbers.add(new_number)
            
            # Write to new file
            with open(new_path, 'w') as f:
                yaml.dump(rule_data, f, default_flow_style=False, indent=2, sort_keys=False)
            
            # Remove old file if different
            if new_path != yaml_file:
                yaml_file.unlink()
            
            self.fixes_applied.append({
                'domain': domain,
                'old_filename': yaml_file.name,
                'new_filename': new_filename,
                'old_id': rule_data.get('id', 'unknown'),
                'new_id': new_id
            })
            
            print(f"  ✓ Fixed: {yaml_file.name} → {new_filename}")
            
        except Exception as e:
            print(f"  ❌ Error fixing {yaml_file.name}: {e}")
    
    def determine_new_number(self, filename: str, rule_id: str, used_numbers: Set[int]) -> int:
        """Determine the best number for the new filename"""
        
        # Try to extract existing number from filename or ID
        for source in [filename, rule_id]:
            # Look for various number patterns
            patterns = [
                r'(\d{3})',  # 3-digit numbers first
                r'(\d{2})',  # 2-digit numbers  
                r'(\d+)',    # any digits
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, source)
                if matches:
                    for match in matches:
                        number = int(match)
                        if number > 0 and number not in used_numbers:
                            return number
        
        # Fallback: find next available number
        return self.find_next_available_number(used_numbers)
    
    def find_next_available_number(self, used_numbers: Set[int]) -> int:
        """Find the next available number"""
        number = 1
        while number in used_numbers:
            number += 1
        return number

def main():
    fixer = NumberingConsistencyFixer()
    fixes = fixer.fix_all_numbering_consistency()
    
    if fixes:
        print(f"\n=== Summary ===")
        domain_counts = {}
        for fix in fixes:
            domain = fix['domain']
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        for domain, count in sorted(domain_counts.items()):
            print(f"  {domain}: {count} files renumbered")
            
        print(f"\nTotal: {len(fixes)} files renumbered")
        
        # Show examples
        print(f"\n=== Examples ===")
        for fix in fixes[:10]:
            print(f"  {fix['old_filename']} → {fix['new_filename']} (ID: {fix['new_id']})")
        
        if len(fixes) > 10:
            print(f"  ... and {len(fixes) - 10} more")
    else:
        print("\n✅ All files already have consistent numbering!")
    
    return len(fixes)

if __name__ == "__main__":
    main()