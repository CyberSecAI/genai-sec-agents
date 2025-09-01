#!/usr/bin/env python3
"""
Fix Missing IDs in Rule Cards
Adds missing id fields to rule cards that don't have them
"""

import os
import yaml
import re
from pathlib import Path
from typing import Dict, Set

class MissingIDFixer:
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
    
    def fix_all_missing_ids(self):
        """Fix missing IDs for all rule cards"""
        print("=== Fixing Missing Rule IDs ===")
        
        # Find files without IDs
        missing_id_files = []
        
        for yaml_file in self.rule_cards_path.rglob("*.yml"):
            if self.needs_id_fix(yaml_file):
                missing_id_files.append(yaml_file)
        
        print(f"Found {len(missing_id_files)} files with missing IDs")
        
        for yaml_file in missing_id_files:
            self.fix_missing_id(yaml_file)
        
        print(f"\n✅ Fixed {len(self.fixes_applied)} missing IDs")
        return self.fixes_applied
    
    def needs_id_fix(self, yaml_file: Path) -> bool:
        """Check if file needs ID fix"""
        try:
            with open(yaml_file, 'r') as f:
                rule_data = yaml.safe_load(f)
            
            if not isinstance(rule_data, dict):
                return False
            
            # Check if ID is missing or empty
            return 'id' not in rule_data or not rule_data['id'].strip()
            
        except:
            return False
    
    def fix_missing_id(self, yaml_file: Path):
        """Fix missing ID for a single file"""
        try:
            # Read current content
            with open(yaml_file, 'r') as f:
                rule_data = yaml.safe_load(f)
            
            if not isinstance(rule_data, dict):
                print(f"  ❌ Invalid YAML structure in {yaml_file.name}")
                return
            
            domain = yaml_file.parent.name
            
            # Generate ID based on filename or find next available
            new_id = self.generate_id_from_filename(yaml_file, domain)
            
            # Add the ID
            rule_data['id'] = new_id
            
            # Reorder to put ID first
            ordered_data = {'id': new_id}
            for key, value in rule_data.items():
                if key != 'id':
                    ordered_data[key] = value
            
            # Write back
            with open(yaml_file, 'w') as f:
                yaml.dump(ordered_data, f, default_flow_style=False, indent=2, sort_keys=False)
            
            self.fixes_applied.append({
                'file': str(yaml_file),
                'domain': domain,
                'old_filename': yaml_file.name,
                'new_id': new_id
            })
            
            print(f"  ✓ Added ID to {yaml_file.name}: {new_id}")
            
        except Exception as e:
            print(f"  ❌ Error fixing {yaml_file.name}: {e}")
    
    def generate_id_from_filename(self, yaml_file: Path, domain: str) -> str:
        """Generate ID from filename"""
        domain_prefix = self.domain_prefixes.get(domain, domain.upper()[:6])
        
        # Extract number from filename if present
        filename_stem = yaml_file.stem
        number_match = re.search(r'(\d+)', filename_stem)
        
        if number_match:
            number = int(number_match.group(1))
        else:
            # Find next available number
            number = self.find_next_available_number(domain, domain_prefix)
        
        return f"{domain_prefix}-{number:03d}"
    
    def find_next_available_number(self, domain: str, prefix: str) -> int:
        """Find the next available number for a domain prefix"""
        domain_path = self.rule_cards_path / domain
        if not domain_path.exists():
            return 1
        
        existing_numbers = set()
        
        # Check existing files
        for file_path in domain_path.glob("*.yml"):
            try:
                with open(file_path, 'r') as f:
                    rule_data = yaml.safe_load(f)
                
                if isinstance(rule_data, dict) and 'id' in rule_data:
                    rule_id = rule_data['id']
                    match = re.search(rf'{re.escape(prefix)}-(\d+)', rule_id)
                    if match:
                        existing_numbers.add(int(match.group(1)))
                        
            except:
                continue
        
        # Find next available
        next_num = 1
        while next_num in existing_numbers:
            next_num += 1
        
        return next_num

def main():
    fixer = MissingIDFixer()
    fixes = fixer.fix_all_missing_ids()
    
    if fixes:
        print(f"\n=== Summary ===")
        domain_counts = {}
        for fix in fixes:
            domain = fix['domain']
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        for domain, count in sorted(domain_counts.items()):
            print(f"  {domain}: {count} IDs added")
            
        print(f"\nTotal: {len(fixes)} IDs added")
    else:
        print("\n✅ All rule cards already have IDs!")
    
    return len(fixes)

if __name__ == "__main__":
    main()