#!/usr/bin/env python3
"""
Standardize Rule Card Filenames
Ensures all rule card filenames follow domain-prefix-number format
"""

import os
import yaml
import re
from pathlib import Path
from typing import Dict, List, Set

class FilenameStandardizer:
    def __init__(self, rule_cards_path: str = "app/rule_cards"):
        self.rule_cards_path = Path(rule_cards_path)
        self.fixes_applied = []
        
        # Domain prefixes for consistent naming
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
    
    def standardize_all_filenames(self):
        """Standardize filenames for all rule cards"""
        print("=== Standardizing Rule Card Filenames ===")
        
        # Process each domain
        for domain_path in self.rule_cards_path.iterdir():
            if domain_path.is_dir():
                domain = domain_path.name
                print(f"\nProcessing domain: {domain}")
                self.standardize_domain_filenames(domain_path, domain)
        
        print(f"\n✅ Standardized {len(self.fixes_applied)} filenames")
        return self.fixes_applied
    
    def standardize_domain_filenames(self, domain_path: Path, domain: str):
        """Standardize filenames for a single domain"""
        prefix = self.domain_prefixes.get(domain, domain.upper()[:6])
        
        # Get all YAML files in domain
        yaml_files = list(domain_path.glob("*.yml"))
        
        # Extract existing numbers to avoid conflicts
        existing_numbers = self.extract_existing_numbers(yaml_files, prefix)
        
        # Track files that need renaming
        files_to_rename = []
        
        for yaml_file in yaml_files:
            # Check if filename already follows standard format
            if self.is_standard_filename(yaml_file.name, prefix):
                continue
            
            # Read rule to get ID
            try:
                with open(yaml_file, 'r') as f:
                    rule_data = yaml.safe_load(f)
                
                if not isinstance(rule_data, dict) or 'id' not in rule_data:
                    print(f"  ❌ No ID found in {yaml_file.name}")
                    continue
                
                rule_id = rule_data['id']
                
                # Generate standard filename
                standard_filename = self.generate_standard_filename(rule_id, prefix, existing_numbers)
                
                if standard_filename != yaml_file.name:
                    files_to_rename.append({
                        'old_path': yaml_file,
                        'new_filename': standard_filename,
                        'rule_id': rule_id
                    })
                    
                    # Extract number from new filename to avoid conflicts
                    number_match = re.search(rf'{re.escape(prefix)}-(\d+)', standard_filename)
                    if number_match:
                        existing_numbers.add(int(number_match.group(1)))
                
            except Exception as e:
                print(f"  ❌ Error processing {yaml_file.name}: {e}")
        
        # Perform the renames
        for rename_info in files_to_rename:
            self.rename_file(rename_info, domain)
    
    def extract_existing_numbers(self, yaml_files: List[Path], prefix: str) -> Set[int]:
        """Extract existing numbers for a prefix to avoid conflicts"""
        numbers = set()
        
        for yaml_file in yaml_files:
            # Look for prefix-number pattern
            match = re.search(rf'{re.escape(prefix)}-(\d+)', yaml_file.stem)
            if match:
                numbers.add(int(match.group(1)))
        
        return numbers
    
    def is_standard_filename(self, filename: str, prefix: str) -> bool:
        """Check if filename already follows standard format"""
        # Standard format: PREFIX-XXX.yml where XXX is 3+ digits
        pattern = rf'^{re.escape(prefix)}-\d{{3,}}\.yml$'
        return bool(re.match(pattern, filename))
    
    def generate_standard_filename(self, rule_id: str, domain_prefix: str, existing_numbers: Set[int]) -> str:
        """Generate standard filename based on rule ID"""
        
        # If rule ID already has the correct prefix, use it
        if rule_id.startswith(domain_prefix + '-'):
            # Extract number part
            match = re.search(rf'{re.escape(domain_prefix)}-(\d+)', rule_id)
            if match:
                number = int(match.group(1))
                return f"{domain_prefix}-{number:03d}.yml"
        
        # Extract any number from the rule ID
        number_match = re.search(r'(\d+)', rule_id)
        if number_match:
            number = int(number_match.group(1))
            
            # Ensure it's not conflicting
            while number in existing_numbers:
                number += 1
                
            return f"{domain_prefix}-{number:03d}.yml"
        
        # Fallback: find next available number
        next_num = 1
        while next_num in existing_numbers:
            next_num += 1
            
        return f"{domain_prefix}-{next_num:03d}.yml"
    
    def rename_file(self, rename_info: Dict, domain: str):
        """Rename a single file"""
        old_path = rename_info['old_path']
        new_filename = rename_info['new_filename']
        new_path = old_path.parent / new_filename
        
        try:
            # Check if target already exists
            if new_path.exists():
                print(f"  ⚠️  Target exists: {new_filename}, skipping")
                return
            
            # Rename the file
            old_path.rename(new_path)
            
            self.fixes_applied.append({
                'domain': domain,
                'old_filename': old_path.name,
                'new_filename': new_filename,
                'rule_id': rename_info['rule_id']
            })
            
            print(f"  ✓ Renamed: {old_path.name} → {new_filename}")
            
        except Exception as e:
            print(f"  ❌ Error renaming {old_path.name}: {e}")
    
    def find_next_available_number(self, domain: str, prefix: str) -> int:
        """Find the next available number for a domain prefix"""
        domain_path = self.rule_cards_path / domain
        if not domain_path.exists():
            return 1
        
        existing_numbers = set()
        for file_path in domain_path.glob("*.yml"):
            match = re.search(rf'{re.escape(prefix)}-(\d+)', file_path.stem)
            if match:
                existing_numbers.add(int(match.group(1)))
        
        next_num = 1
        while next_num in existing_numbers:
            next_num += 1
        
        return next_num

def main():
    standardizer = FilenameStandardizer()
    fixes = standardizer.standardize_all_filenames()
    
    if fixes:
        print(f"\n=== Summary ===")
        domain_counts = {}
        for fix in fixes:
            domain = fix['domain']
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        for domain, count in sorted(domain_counts.items()):
            print(f"  {domain}: {count} files renamed")
            
        print(f"\nTotal: {len(fixes)} files renamed")
        
        # Show some examples
        print(f"\n=== Examples ===")
        for fix in fixes[:10]:
            print(f"  {fix['old_filename']} → {fix['new_filename']} (ID: {fix['rule_id']})")
        
        if len(fixes) > 10:
            print(f"  ... and {len(fixes) - 10} more")
    else:
        print("\n✅ All filenames already follow standard format!")
    
    return len(fixes)

if __name__ == "__main__":
    main()