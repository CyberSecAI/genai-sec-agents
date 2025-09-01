#!/usr/bin/env python3
"""
Rule Card Fix Script
Fixes common issues found in Rule Cards validation
"""

import os
import yaml
import re
from pathlib import Path
from typing import Dict, Any

class RuleCardFixer:
    def __init__(self, rule_cards_path: str = "app/rule_cards"):
        self.rule_cards_path = Path(rule_cards_path)
        self.fixes_applied = []
    
    def fix_all_issues(self):
        """Fix all detected issues in Rule Cards"""
        print("=== Rule Card Fixer Started ===")
        
        # Fix YAML parsing errors (remove ```yaml wrappers)
        self.fix_yaml_wrappers()
        
        # Fix missing ID fields for RULE-*.yml files
        self.fix_missing_ids()
        
        # Remove problematic incomplete rules
        self.cleanup_incomplete_rules()
        
        print(f"\n✅ Applied {len(self.fixes_applied)} fixes")
        return self.fixes_applied
    
    def fix_yaml_wrappers(self):
        """Fix files with ```yaml wrappers that cause parsing errors"""
        problematic_patterns = [
            "```yaml",
            "```",
        ]
        
        # Find files with YAML parsing errors
        yaml_files = list(self.rule_cards_path.rglob("*.yml"))
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r') as f:
                    content = f.read()
                
                # Check if file has ```yaml wrappers
                if any(pattern in content for pattern in problematic_patterns):
                    print(f"  Fixing YAML wrappers in {yaml_file.name}")
                    
                    # Remove all ```yaml and ``` lines
                    fixed_content = re.sub(r'^```yaml\s*\n?', '', content, flags=re.MULTILINE)
                    fixed_content = re.sub(r'\n?```\s*$', '', fixed_content, flags=re.MULTILINE)
                    fixed_content = re.sub(r'^```\s*\n?', '', fixed_content, flags=re.MULTILINE)
                    
                    # Clean up any leading/trailing whitespace
                    fixed_content = fixed_content.strip()
                    
                    # Validate the fixed YAML
                    try:
                        yaml.safe_load(fixed_content)
                        
                        # Write the fixed content
                        with open(yaml_file, 'w') as f:
                            f.write(fixed_content)
                        
                        self.fixes_applied.append({
                            "action": "remove_yaml_wrappers",
                            "file": str(yaml_file),
                            "description": "Removed ```yaml wrappers"
                        })
                        
                        print(f"    ✓ Fixed {yaml_file.name}")
                    
                    except yaml.YAMLError as e:
                        print(f"    ❌ Still invalid YAML after wrapper removal: {e}")
                        continue
            
            except Exception as e:
                print(f"    ❌ Error processing {yaml_file}: {e}")
                continue
    
    def fix_missing_ids(self):
        """Fix files with missing ID fields by extracting from filename or content"""
        yaml_files = list(self.rule_cards_path.rglob("RULE-*.yml"))
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r') as f:
                    content = f.read()
                
                # Parse YAML
                rule_data = yaml.safe_load(content)
                
                if not isinstance(rule_data, dict):
                    continue
                
                # Check if ID is missing
                if 'id' not in rule_data or not rule_data['id']:
                    # Extract ID from filename
                    filename_id = yaml_file.stem
                    
                    # Check if we can infer ID from content
                    title = rule_data.get('title', '')
                    if title and not filename_id.startswith('RULE-'):
                        # Generate ID from title
                        rule_id = self.generate_rule_id_from_title(title)
                    else:
                        rule_id = filename_id
                    
                    rule_data['id'] = rule_id
                    
                    # Write back with ID
                    with open(yaml_file, 'w') as f:
                        yaml.dump(rule_data, f, default_flow_style=False, indent=2)
                    
                    self.fixes_applied.append({
                        "action": "add_missing_id",
                        "file": str(yaml_file),
                        "rule_id": rule_id,
                        "description": f"Added missing ID: {rule_id}"
                    })
                    
                    print(f"    ✓ Added ID '{rule_id}' to {yaml_file.name}")
            
            except Exception as e:
                print(f"    ❌ Error processing {yaml_file}: {e}")
                continue
    
    def generate_rule_id_from_title(self, title: str) -> str:
        """Generate a rule ID from title"""
        # Convert title to uppercase, replace spaces with hyphens
        rule_id = re.sub(r'[^A-Za-z0-9\s-]', '', title)
        rule_id = re.sub(r'\s+', '-', rule_id.upper())
        rule_id = rule_id[:50]  # Limit length
        
        # Add a prefix if it doesn't have one
        if not rule_id.startswith(('AUTH-', 'CRYPTO-', 'INPUT-', 'WEB-')):
            rule_id = f"GENERAL-{rule_id}"
        
        return rule_id
    
    def cleanup_incomplete_rules(self):
        """Remove or fix rules that are severely incomplete"""
        yaml_files = list(self.rule_cards_path.rglob("*.yml"))
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r') as f:
                    content = f.read()
                
                # Skip if file is too small or mostly empty
                if len(content.strip()) < 20:
                    print(f"    Removing empty file: {yaml_file.name}")
                    yaml_file.unlink()
                    
                    self.fixes_applied.append({
                        "action": "remove_empty_file",
                        "file": str(yaml_file),
                        "description": "Removed empty or minimal content file"
                    })
                    continue
                
                # Parse and check for minimum required content
                rule_data = yaml.safe_load(content)
                
                if not isinstance(rule_data, dict):
                    continue
                
                # Check if rule has absolute minimum content
                required_fields = ['id', 'title']
                missing_critical = [field for field in required_fields if field not in rule_data]
                
                if len(missing_critical) >= len(required_fields):
                    print(f"    Removing severely incomplete rule: {yaml_file.name}")
                    yaml_file.unlink()
                    
                    self.fixes_applied.append({
                        "action": "remove_incomplete_rule",
                        "file": str(yaml_file),
                        "description": f"Removed rule missing critical fields: {missing_critical}"
                    })
            
            except Exception as e:
                print(f"    ❌ Error processing {yaml_file}: {e}")
                continue

def main():
    fixer = RuleCardFixer()
    fixes = fixer.fix_all_issues()
    
    if fixes:
        print("\n=== Fixes Applied Summary ===")
        for fix in fixes:
            print(f"  {fix['action']}: {Path(fix['file']).name} - {fix['description']}")
    else:
        print("\n✅ No fixes needed!")
    
    return len(fixes)

if __name__ == "__main__":
    main()