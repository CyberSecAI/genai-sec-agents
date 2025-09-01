#!/usr/bin/env python3
"""
Rule Card Validation Script
Validates Rule Cards for proper format, single rule per file, and schema compliance
Fixes multiple rules in single files by splitting them
"""

import os
import yaml
import re
from pathlib import Path
from typing import List, Dict, Any

class RuleCardValidator:
    def __init__(self, rule_cards_path: str = "app/rule_cards"):
        self.rule_cards_path = Path(rule_cards_path)
        self.issues = []
        self.fixes_applied = []
    
    def validate_all_rule_cards(self):
        """Validate all Rule Cards in the directory structure"""
        print("=== Rule Card Validation Started ===")
        
        # Find all YAML files
        yaml_files = list(self.rule_cards_path.rglob("*.yml"))
        print(f"Found {len(yaml_files)} YAML files to validate")
        
        for yaml_file in yaml_files:
            self.validate_rule_card_file(yaml_file)
        
        return self.generate_validation_report()
    
    def validate_rule_card_file(self, file_path: Path):
        """Validate a single Rule Card file"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check for multiple YAML documents
            if self.has_multiple_yaml_documents(content):
                self.issues.append({
                    "file": str(file_path),
                    "issue": "multiple_yaml_documents",
                    "severity": "high",
                    "description": "File contains multiple YAML documents (rules)"
                })
                
                # Attempt to fix by splitting
                self.fix_multiple_yaml_documents(file_path, content)
                return
            
            # Parse single YAML document
            try:
                rule_data = yaml.safe_load(content)
                
                if not isinstance(rule_data, dict):
                    self.issues.append({
                        "file": str(file_path),
                        "issue": "invalid_yaml_structure",
                        "severity": "high",
                        "description": "YAML does not parse to a dictionary"
                    })
                    return
                
                # Validate schema
                self.validate_rule_schema(file_path, rule_data)
                
                # Validate file naming convention
                self.validate_file_naming(file_path, rule_data)
                
            except yaml.YAMLError as e:
                self.issues.append({
                    "file": str(file_path),
                    "issue": "yaml_parse_error",
                    "severity": "high",
                    "description": f"YAML parsing error: {e}"
                })
        
        except Exception as e:
            self.issues.append({
                "file": str(file_path),
                "issue": "file_read_error",
                "severity": "high",
                "description": f"Error reading file: {e}"
            })
    
    def has_multiple_yaml_documents(self, content: str) -> bool:
        """Check if content has multiple YAML documents"""
        # Look for multiple ```yaml blocks or multiple id: fields
        yaml_block_count = content.count('```yaml')
        id_field_count = len(re.findall(r'^id:\s+', content, re.MULTILINE))
        
        return yaml_block_count > 1 or id_field_count > 1
    
    def fix_multiple_yaml_documents(self, file_path: Path, content: str):
        """Fix file with multiple YAML documents by splitting into separate files"""
        try:
            # Extract individual YAML blocks
            yaml_blocks = re.findall(r'```yaml\n(.*?)```', content, re.DOTALL)
            
            if not yaml_blocks:
                # Try extracting by id: fields instead
                yaml_blocks = self.extract_by_id_fields(content)
            
            if len(yaml_blocks) <= 1:
                self.issues.append({
                    "file": str(file_path),
                    "issue": "fix_failed",
                    "severity": "high",
                    "description": "Could not extract multiple YAML blocks for splitting"
                })
                return
            
            # Parse each block and create separate files
            domain_dir = file_path.parent
            original_stem = file_path.stem
            
            for i, yaml_block in enumerate(yaml_blocks):
                try:
                    rule_data = yaml.safe_load(yaml_block)
                    
                    if not isinstance(rule_data, dict) or 'id' not in rule_data:
                        continue
                    
                    rule_id = rule_data['id']
                    new_file_path = domain_dir / f"{rule_id}.yml"
                    
                    # Write clean YAML (without ```yaml wrapper)
                    with open(new_file_path, 'w') as f:
                        yaml.dump(rule_data, f, default_flow_style=False, indent=2)
                    
                    self.fixes_applied.append({
                        "action": "split_rule",
                        "original_file": str(file_path),
                        "new_file": str(new_file_path),
                        "rule_id": rule_id
                    })
                    
                    print(f"  ✓ Created {new_file_path} for rule {rule_id}")
                
                except yaml.YAMLError as e:
                    print(f"  ❌ Failed to parse YAML block {i}: {e}")
                    continue
            
            # Remove original file after successful splitting
            if self.fixes_applied and any(fix['original_file'] == str(file_path) for fix in self.fixes_applied):
                file_path.unlink()
                print(f"  ✓ Removed original file {file_path}")
        
        except Exception as e:
            self.issues.append({
                "file": str(file_path),
                "issue": "fix_error",
                "severity": "high",
                "description": f"Error fixing multiple YAML documents: {e}"
            })
    
    def extract_by_id_fields(self, content: str) -> List[str]:
        """Extract YAML blocks by splitting on id: fields"""
        # Remove any ```yaml wrappers first
        content = re.sub(r'```yaml\n?', '', content)
        content = re.sub(r'\n?```', '', content)
        
        # Split by id: at the beginning of lines
        blocks = re.split(r'^(?=id:\s+)', content, flags=re.MULTILINE)
        
        # Filter out empty blocks
        return [block.strip() for block in blocks if block.strip() and 'id:' in block]
    
    def validate_rule_schema(self, file_path: Path, rule_data: Dict[Any, Any]):
        """Validate that rule data follows expected schema"""
        required_fields = ['id', 'title', 'severity', 'scope', 'requirement']
        
        for field in required_fields:
            if field not in rule_data:
                self.issues.append({
                    "file": str(file_path),
                    "issue": "missing_required_field",
                    "severity": "medium",
                    "description": f"Missing required field: {field}",
                    "field": field
                })
        
        # Check for valid severity values
        if 'severity' in rule_data:
            valid_severities = ['low', 'medium', 'high', 'critical']
            if rule_data['severity'] not in valid_severities:
                self.issues.append({
                    "file": str(file_path),
                    "issue": "invalid_severity",
                    "severity": "medium",
                    "description": f"Invalid severity value: {rule_data['severity']}",
                    "valid_values": valid_severities
                })
    
    def validate_file_naming(self, file_path: Path, rule_data: Dict[Any, Any]):
        """Validate file naming convention matches rule ID"""
        if 'id' not in rule_data:
            return
        
        rule_id = rule_data['id']
        expected_filename = f"{rule_id}.yml"
        actual_filename = file_path.name
        
        if actual_filename != expected_filename:
            self.issues.append({
                "file": str(file_path),
                "issue": "filename_mismatch",
                "severity": "low",
                "description": f"Filename '{actual_filename}' doesn't match rule ID '{rule_id}'",
                "expected": expected_filename,
                "actual": actual_filename
            })
    
    def generate_validation_report(self) -> Dict:
        """Generate comprehensive validation report"""
        report = {
            "validation_summary": {
                "total_issues": len(self.issues),
                "fixes_applied": len(self.fixes_applied),
                "high_severity": len([i for i in self.issues if i['severity'] == 'high']),
                "medium_severity": len([i for i in self.issues if i['severity'] == 'medium']),
                "low_severity": len([i for i in self.issues if i['severity'] == 'low'])
            },
            "issues": self.issues,
            "fixes_applied": self.fixes_applied
        }
        
        return report
    
    def print_validation_report(self, report: Dict):
        """Print human-readable validation report"""
        summary = report["validation_summary"]
        
        print(f"\n=== Validation Report ===")
        print(f"Total Issues Found: {summary['total_issues']}")
        print(f"Fixes Applied: {summary['fixes_applied']}")
        print(f"  - High Severity: {summary['high_severity']}")
        print(f"  - Medium Severity: {summary['medium_severity']}")
        print(f"  - Low Severity: {summary['low_severity']}")
        
        if report["fixes_applied"]:
            print(f"\n=== Fixes Applied ===")
            for fix in report["fixes_applied"]:
                print(f"  ✓ {fix['action']}: {fix.get('rule_id', 'N/A')} -> {Path(fix['new_file']).name}")
        
        if report["issues"]:
            print(f"\n=== Issues Found ===")
            for issue in report["issues"]:
                print(f"  {issue['severity'].upper()}: {Path(issue['file']).name}")
                print(f"    {issue['issue']}: {issue['description']}")
        else:
            print(f"\n✅ No remaining issues found!")

def main():
    validator = RuleCardValidator()
    report = validator.validate_all_rule_cards()
    validator.print_validation_report(report)
    
    # Write detailed report to file
    import json
    report_path = "docs/validation_reports/rule_card_validation.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\nDetailed report saved to: {report_path}")
    
    return len(report["issues"]) == 0

if __name__ == "__main__":
    main()