#!/usr/bin/env python3
"""
Standardize Rule Card Structure
Ensures all rule cards follow the standard field order starting with id:
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List

class RuleStructureStandardizer:
    def __init__(self, rule_cards_path: str = "app/rule_cards"):
        self.rule_cards_path = Path(rule_cards_path)
        self.fixes_applied = []
        
        # Standard field order for rule cards
        self.standard_order = [
            'id',
            'title', 
            'severity',
            'scope',
            'requirement',
            'do',
            'dont',
            'detect',
            'verify',
            'refs'
        ]
    
    def standardize_all_rules(self):
        """Standardize structure for all rule cards"""
        print("=== Standardizing Rule Card Structure ===")
        
        # Find all YAML files
        yaml_files = list(self.rule_cards_path.rglob("*.yml"))
        print(f"Found {len(yaml_files)} rule card files")
        
        for yaml_file in yaml_files:
            self.standardize_single_rule(yaml_file)
        
        print(f"\n✅ Standardized {len(self.fixes_applied)} rule cards")
        return self.fixes_applied
    
    def standardize_single_rule(self, file_path: Path):
        """Standardize structure for a single rule card"""
        try:
            # Read the file
            with open(file_path, 'r') as f:
                rule_data = yaml.safe_load(f)
            
            if not isinstance(rule_data, dict):
                print(f"  ❌ Invalid YAML structure in {file_path.name}")
                return
            
            # Check if reordering is needed
            current_keys = list(rule_data.keys())
            if current_keys == [key for key in self.standard_order if key in rule_data]:
                # Already in correct order
                return
            
            # Reorder the dictionary
            reordered_data = {}
            
            # Add fields in standard order
            for field in self.standard_order:
                if field in rule_data:
                    reordered_data[field] = rule_data[field]
            
            # Add any additional fields that aren't in standard order
            for field, value in rule_data.items():
                if field not in reordered_data:
                    reordered_data[field] = value
            
            # Write back to file with proper formatting
            with open(file_path, 'w') as f:
                yaml.dump(reordered_data, f, default_flow_style=False, indent=2, sort_keys=False)
            
            self.fixes_applied.append({
                'file': str(file_path),
                'domain': file_path.parent.name,
                'rule_id': rule_data.get('id', 'unknown'),
                'old_order': current_keys,
                'new_order': list(reordered_data.keys())
            })
            
            print(f"  ✓ Standardized: {file_path.name}")
            
        except Exception as e:
            print(f"  ❌ Error standardizing {file_path.name}: {e}")
    
    def validate_structure(self, file_path: Path) -> bool:
        """Validate that a rule card has correct structure"""
        try:
            with open(file_path, 'r') as f:
                rule_data = yaml.safe_load(f)
            
            if not isinstance(rule_data, dict):
                return False
            
            # Check required fields
            required_fields = ['id', 'title', 'severity', 'scope', 'requirement']
            for field in required_fields:
                if field not in rule_data:
                    return False
            
            # Check field order
            current_keys = list(rule_data.keys())
            expected_order = [key for key in self.standard_order if key in rule_data]
            
            return current_keys == expected_order
            
        except:
            return False

def main():
    standardizer = RuleStructureStandardizer()
    fixes = standardizer.standardize_all_rules()
    
    if fixes:
        print(f"\n=== Summary ===")
        domain_counts = {}
        for fix in fixes:
            domain = fix['domain']
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        for domain, count in sorted(domain_counts.items()):
            print(f"  {domain}: {count} rules standardized")
            
        print(f"\nTotal: {len(fixes)} rules standardized")
    else:
        print("\n✅ All rule cards already have standard structure!")
    
    return len(fixes)

if __name__ == "__main__":
    main()