#!/usr/bin/env python3
"""
Fix Rule Card Filenames
Fixes problematic filenames with placeholders like ### and assigns proper IDs
"""

import os
import yaml
import re
from pathlib import Path
from typing import Dict, List

class RuleFilenameFixer:
    def __init__(self, rule_cards_path: str = "app/rule_cards"):
        self.rule_cards_path = Path(rule_cards_path)
        self.fixes_applied = []
    
    def fix_all_problematic_filenames(self):
        """Find and fix all problematic filenames"""
        print("=== Fixing Problematic Rule Filenames ===")
        
        # Find files with problematic names
        problematic_files = []
        
        for yaml_file in self.rule_cards_path.rglob("*.yml"):
            filename = yaml_file.name
            if any([
                "###" in filename,
                "(to be assigned)" in filename,
                "(for new rules)" in filename,
                "(new ID)" in filename,
                "(existing ID)" in filename
            ]):
                problematic_files.append(yaml_file)
        
        print(f"Found {len(problematic_files)} problematic filenames")
        
        for file_path in problematic_files:
            self.fix_single_filename(file_path)
        
        print(f"\n✅ Fixed {len(self.fixes_applied)} filename issues")
        return self.fixes_applied
    
    def fix_single_filename(self, file_path: Path):
        """Fix a single problematic filename"""
        try:
            # Read the file content to get rule data
            with open(file_path, 'r') as f:
                rule_data = yaml.safe_load(f)
            
            if not isinstance(rule_data, dict):
                print(f"  ❌ Invalid YAML structure in {file_path.name}")
                return
            
            domain = file_path.parent.name
            current_id = rule_data.get('id', '')
            
            # Determine the correct filename and ID
            new_id, new_filename = self.generate_proper_id_and_filename(rule_data, domain, file_path)
            
            if new_id and new_filename:
                # Update the rule ID if needed
                if current_id != new_id:
                    rule_data['id'] = new_id
                
                # Create new file path
                new_file_path = file_path.parent / new_filename
                
                # Check if target already exists
                if new_file_path.exists() and new_file_path != file_path:
                    print(f"  ⚠️  Target exists {new_filename}, adding suffix")
                    base, ext = new_filename.rsplit('.', 1)
                    counter = 1
                    while new_file_path.exists():
                        new_filename = f"{base}-{counter:02d}.{ext}"
                        new_file_path = file_path.parent / new_filename
                        counter += 1
                    new_id = f"{new_id}-{counter-1:02d}"
                    rule_data['id'] = new_id
                
                # Write to new location
                with open(new_file_path, 'w') as f:
                    yaml.dump(rule_data, f, default_flow_style=False, indent=2)
                
                # Remove old file if different
                if new_file_path != file_path:
                    file_path.unlink()
                
                self.fixes_applied.append({
                    'old_filename': file_path.name,
                    'new_filename': new_filename,
                    'old_id': current_id,
                    'new_id': new_id,
                    'domain': domain
                })
                
                print(f"  ✓ Fixed: {file_path.name} → {new_filename}")
            
        except Exception as e:
            print(f"  ❌ Error fixing {file_path.name}: {e}")
    
    def generate_proper_id_and_filename(self, rule_data: Dict, domain: str, file_path: Path) -> tuple:
        """Generate proper ID and filename for a rule"""
        title = rule_data.get('title', '').strip()
        current_id = rule_data.get('id', '').strip()
        
        # Domain prefixes
        domain_prefixes = {
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
            'network_security': 'NET'
        }
        
        domain_prefix = domain_prefixes.get(domain, domain.upper()[:6])
        
        # If current ID has ### or placeholder, generate new one
        if '###' in current_id or not current_id or any(x in current_id for x in ['(', 'to be assigned']):
            # Find next available number for this domain
            next_num = self.find_next_available_number(domain, domain_prefix)
            new_id = f"{domain_prefix}-{next_num:03d}"
        else:
            # Keep existing ID if it's valid
            new_id = current_id
        
        # Generate filename from ID
        new_filename = f"{new_id}.yml"
        
        return new_id, new_filename
    
    def find_next_available_number(self, domain: str, prefix: str) -> int:
        """Find the next available number for a domain prefix"""
        domain_path = self.rule_cards_path / domain
        if not domain_path.exists():
            return 1
        
        # Find existing numbers
        existing_numbers = set()
        for file_path in domain_path.glob("*.yml"):
            # Extract number from filename like PREFIX-001.yml
            match = re.search(rf'{re.escape(prefix)}-(\d+)', file_path.stem)
            if match:
                existing_numbers.add(int(match.group(1)))
        
        # Find next available number
        next_num = 1
        while next_num in existing_numbers:
            next_num += 1
        
        return next_num

def main():
    fixer = RuleFilenameFixer()
    fixes = fixer.fix_all_problematic_filenames()
    
    if fixes:
        print("\n=== Summary ===")
        for fix in fixes:
            print(f"  {fix['domain']}: {fix['old_filename']} → {fix['new_filename']} (ID: {fix['new_id']})")
    else:
        print("\n✅ No problematic filenames found!")
    
    return len(fixes)

if __name__ == "__main__":
    main()