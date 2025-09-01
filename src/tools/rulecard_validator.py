#!/usr/bin/env python3
"""
Enhanced Rule Card Validator
Validates all Rule Card YAML files with comprehensive pattern checks including:
- Required fields and structure validation
- Descriptive naming conventions
- Field ordering standards  
- Content quality checks
- Domain-based organization validation
- Filename-ID consistency
"""

import sys
import glob
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
import yaml

ROOT = Path(__file__).resolve().parents[2]
RULE_DIR = ROOT / "app" / "rule_cards"

# Required fields for a Rule Card to be considered valid
REQUIRED_FIELDS = [
    "id", "title", "severity", "scope", "requirement", "do", "dont", "detect", "verify", "refs"
]

# Standard field order for consistency
STANDARD_FIELD_ORDER = [
    "id", "title", "severity", "scope", "requirement", "do", "dont", "detect", "verify", "refs"
]

# Domain prefixes mapping
DOMAIN_PREFIXES = {
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
    'logging': 'LOG',
    'network_security': 'NET',
    'cookies': 'COOKIE',
    'nodejs': 'NODE',
    'java': 'JAVA',
    'php': 'PHP',
    'jwt': 'JWT',
    'genai': 'GENAI',
    'secrets': 'SECRET',
    'docker': 'DOCKER',
    'api_security': 'API'
}

# Valid severity levels
VALID_SEVERITIES = ['low', 'medium', 'high', 'critical']

# Valid scope values (flexible validation)
COMMON_SCOPES = ['web-application', 'api', 'web-application/api', 'mobile-application', 'infrastructure']
DOMAIN_SPECIFIC_SCOPES = ['jwt-implementations', 'genai-applications', 'web-applications', 'docker-containers']

class RuleCardValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.rule_ids = set()
        
    def validate_all_rules(self) -> bool:
        """Validate all rule cards and return success status"""
        print("🔍 Starting comprehensive Rule Card validation...")
        
        files = glob.glob(str(RULE_DIR / "**" / "*.yml"), recursive=True)
        if not files:
            print(f"❌ No YAML files found in {RULE_DIR}")
            return False
            
        print(f"📁 Found {len(files)} rule card files")
        
        for file_path in files:
            self.validate_single_rule(Path(file_path))
        
        self.print_results(len(files))
        return len(self.errors) == 0
    
    def validate_single_rule(self, file_path: Path):
        """Validate a single rule card file"""
        try:
            # Parse YAML
            data = yaml.safe_load(file_path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                self.add_error(file_path, "YAML must be a dictionary/mapping")
                return
            
            # Extract domain from file path
            domain = self.extract_domain(file_path)
            
            # Run all validation checks
            self.validate_required_fields(file_path, data)
            self.validate_field_order(file_path, data)
            self.validate_id_format(file_path, data, domain)
            self.validate_filename_consistency(file_path, data)
            self.validate_domain_consistency(file_path, data, domain)
            self.validate_content_quality(file_path, data)
            self.validate_severity_and_scope(file_path, data)
            self.validate_references(file_path, data)
            self.validate_descriptive_naming(file_path, data)
            self.check_duplicates(file_path, data)
            
        except yaml.YAMLError as e:
            self.add_error(file_path, f"Invalid YAML syntax: {e}")
        except Exception as e:
            self.add_error(file_path, f"Validation error: {e}")
    
    def extract_domain(self, file_path: Path) -> str:
        """Extract domain name from file path"""
        parts = file_path.parts
        rule_cards_index = -1
        for i, part in enumerate(parts):
            if part == "rule_cards":
                rule_cards_index = i
                break
        
        if rule_cards_index >= 0 and rule_cards_index + 1 < len(parts):
            return parts[rule_cards_index + 1]
        return "unknown"
    
    def validate_required_fields(self, file_path: Path, data: Dict[str, Any]):
        """Validate all required fields are present"""
        missing_fields = [field for field in REQUIRED_FIELDS if field not in data]
        if missing_fields:
            self.add_error(file_path, f"Missing required fields: {missing_fields}")
    
    def validate_field_order(self, file_path: Path, data: Dict[str, Any]):
        """Validate field order matches standard"""
        actual_order = list(data.keys())
        expected_order = [field for field in STANDARD_FIELD_ORDER if field in data]
        
        # Allow additional fields at the end
        for field in actual_order:
            if field not in STANDARD_FIELD_ORDER:
                expected_order.append(field)
        
        if actual_order != expected_order:
            self.add_warning(file_path, f"Field order should be: {expected_order}")
    
    def validate_id_format(self, file_path: Path, data: Dict[str, Any], domain: str):
        """Validate rule ID format and consistency"""
        if 'id' not in data:
            return  # Already caught by required fields check
            
        rule_id = data['id']
        expected_prefix = DOMAIN_PREFIXES.get(domain, domain.upper()[:6])
        
        # Check if ID starts with expected prefix
        if not rule_id.startswith(expected_prefix):
            self.add_error(file_path, f"Rule ID should start with '{expected_prefix}', got: {rule_id}")
        
        # Check for placeholder content
        if '###' in rule_id or 'XXX' in rule_id or '(to be assigned)' in rule_id:
            self.add_error(file_path, f"Rule ID contains placeholder content: {rule_id}")
        
        # Validate descriptive naming (should have meaningful words, not just PREFIX-123)
        if re.match(r'^[A-Z]+-\d+$', rule_id):
            self.add_warning(file_path, f"Rule ID is not descriptive (generic numeric format): {rule_id}")
    
    def validate_filename_consistency(self, file_path: Path, data: Dict[str, Any]):
        """Validate filename matches rule ID"""
        if 'id' not in data:
            return
            
        rule_id = data['id']
        expected_filename = f"{rule_id}.yml"
        actual_filename = file_path.name
        
        if actual_filename != expected_filename:
            self.add_warning(file_path, f"Filename should match ID: expected '{expected_filename}', got '{actual_filename}'")
    
    def validate_domain_consistency(self, file_path: Path, data: Dict[str, Any], domain: str):
        """Validate rule belongs to correct domain directory"""
        if 'id' not in data:
            return
            
        rule_id = data['id']
        expected_prefix = DOMAIN_PREFIXES.get(domain, domain.upper()[:6])
        
        # Allow descriptive IDs that are domain-relevant even if they don't start with the expected prefix
        domain_relevant_prefixes = {
            'web_security': ['XSS', 'DOM', 'CLICKJACKING'],
            'input_validation': ['SQL-INJECTION', 'INPUT-VALIDATION'],
            'secure_communication': ['HTTP-HEADERS', 'SECURE-COMMUNICATION', 'TLS'],
            'logging': ['ERROR-HANDLING'],
            'authorization': ['AUTH-DESIGN', 'AUTH-OPER', 'AUTH-OTHER'],
            'network_security': ['network_security'],
            'file_handling': ['FILE-UPLOAD', 'FILE-HANDLING'],
            'data_protection': ['DATA-PROTECTION'],
            'session_management': ['SESSION-MANAGEMENT', 'SESSION_MANAGEMENT'],
            'secrets': ['SECRETS'],
            'docker': ['DOCKER-USER'],
            'cookies': ['COOKIES'],
            'jwt': ['JWT'],
            'genai': ['GENAI']
        }
        
        relevant_prefixes = domain_relevant_prefixes.get(domain, [expected_prefix])
        
        # Check if rule ID starts with domain prefix or relevant prefixes
        if not any(rule_id.startswith(prefix) for prefix in [expected_prefix] + relevant_prefixes) and domain not in ['api_security']:
            self.add_warning(file_path, f"Rule in '{domain}' domain has non-standard prefix. Expected '{expected_prefix}' or domain-relevant prefix")
    
    def validate_content_quality(self, file_path: Path, data: Dict[str, Any]):
        """Validate content quality and completeness"""
        # Check for placeholder content
        placeholders = ['XXX', 'TODO', 'FIXME', 'TBD', 'relevant-scanner-rules', 'Testing methods']
        
        for field_name, field_value in data.items():
            if isinstance(field_value, str):
                for placeholder in placeholders:
                    if placeholder in field_value:
                        self.add_error(file_path, f"Field '{field_name}' contains placeholder: {placeholder}")
            elif isinstance(field_value, dict):
                self.check_nested_placeholders(file_path, field_value, field_name, placeholders)
            elif isinstance(field_value, list):
                for i, item in enumerate(field_value):
                    if isinstance(item, str):
                        for placeholder in placeholders:
                            if placeholder in item:
                                self.add_error(file_path, f"Field '{field_name}[{i}]' contains placeholder: {placeholder}")
        
        # Check title quality
        if 'title' in data:
            title = data['title'].strip()
            if len(title) < 5:
                self.add_warning(file_path, f"Title is too short: '{title}'")
            if title.endswith('.'):
                self.add_warning(file_path, "Title should not end with a period")
        
        # Check requirement quality
        if 'requirement' in data:
            requirement = data['requirement'].strip()
            if len(requirement) < 20:
                self.add_warning(file_path, "Requirement description is too short")
    
    def check_nested_placeholders(self, file_path: Path, data: Dict, parent_field: str, placeholders: List[str]):
        """Check for placeholders in nested structures"""
        for key, value in data.items():
            if isinstance(value, str):
                for placeholder in placeholders:
                    if placeholder in value:
                        self.add_error(file_path, f"Field '{parent_field}.{key}' contains placeholder: {placeholder}")
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, str):
                        for placeholder in placeholders:
                            if placeholder in item:
                                self.add_error(file_path, f"Field '{parent_field}.{key}[{i}]' contains placeholder: {placeholder}")
    
    def validate_severity_and_scope(self, file_path: Path, data: Dict[str, Any]):
        """Validate severity and scope values"""
        if 'severity' in data:
            severity = data['severity'].lower()
            if severity not in VALID_SEVERITIES:
                self.add_error(file_path, f"Invalid severity '{severity}'. Valid options: {VALID_SEVERITIES}")
        
        if 'scope' in data:
            scope = data['scope']
            if scope not in COMMON_SCOPES and scope not in DOMAIN_SPECIFIC_SCOPES:
                self.add_warning(file_path, f"Uncommon scope '{scope}'. Common options: {COMMON_SCOPES}")
    
    def validate_references(self, file_path: Path, data: Dict[str, Any]):
        """Validate reference structure and content"""
        if 'refs' not in data:
            return
            
        refs = data['refs']
        if not isinstance(refs, dict):
            self.add_error(file_path, "'refs' field must be a dictionary")
            return
        
        # Check for common reference types
        expected_ref_types = ['cwe', 'asvs', 'owasp']
        for ref_type in expected_ref_types:
            if ref_type in refs:
                ref_list = refs[ref_type]
                if not isinstance(ref_list, list):
                    self.add_error(file_path, f"refs.{ref_type} must be a list")
                elif not ref_list:
                    self.add_warning(file_path, f"refs.{ref_type} is empty")
                else:
                    # Check CWE format
                    if ref_type == 'cwe':
                        for cwe in ref_list:
                            if not re.match(r'^CWE-\d+$', cwe):
                                self.add_error(file_path, f"Invalid CWE format: {cwe}")
    
    def validate_descriptive_naming(self, file_path: Path, data: Dict[str, Any]):
        """Validate descriptive naming conventions"""
        if 'id' not in data:
            return
            
        rule_id = data['id']
        
        # Check if ID is descriptive (has meaningful words beyond prefix and numbers)
        meaningful_parts = re.findall(r'[A-Z]{3,}', rule_id)
        if len(meaningful_parts) < 2:  # Should have prefix + at least one meaningful word
            # Allow some exceptions for well-established patterns
            if not re.match(r'^[A-Z]+-[A-Z]+-[A-Z]+-\d+$', rule_id):  # e.g., AUTH-MFA-TOKEN-001
                self.add_warning(file_path, f"Rule ID could be more descriptive: {rule_id}")
    
    def check_duplicates(self, file_path: Path, data: Dict[str, Any]):
        """Check for duplicate rule IDs"""
        if 'id' not in data:
            return
            
        rule_id = data['id']
        if rule_id in self.rule_ids:
            self.add_error(file_path, f"Duplicate rule ID: {rule_id}")
        else:
            self.rule_ids.add(rule_id)
    
    def add_error(self, file_path: Path, message: str):
        """Add an error message"""
        self.errors.append(f"❌ {file_path.name}: {message}")
    
    def add_warning(self, file_path: Path, message: str):
        """Add a warning message"""
        self.warnings.append(f"⚠️  {file_path.name}: {message}")
    
    def print_results(self, total_files: int):
        """Print validation results"""
        print(f"\n{'='*60}")
        print(f"📊 VALIDATION RESULTS")
        print(f"{'='*60}")
        
        print(f"📁 Files processed: {total_files}")
        print(f"🆔 Unique rule IDs: {len(self.rule_ids)}")
        print(f"❌ Errors: {len(self.errors)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        
        if self.errors:
            print(f"\n🚨 ERRORS:")
            for error in self.errors:
                print(f"  {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS:")
            for warning in self.warnings[:20]:  # Limit warnings display
                print(f"  {warning}")
            if len(self.warnings) > 20:
                print(f"  ... and {len(self.warnings) - 20} more warnings")
        
        print(f"\n{'='*60}")
        if self.errors:
            print("❌ VALIDATION FAILED")
        else:
            print("✅ VALIDATION PASSED")
            if self.warnings:
                print(f"   ({len(self.warnings)} warnings - consider addressing)")
        print(f"{'='*60}")


def main():
    """Main entry point for the validator script."""
    validator = RuleCardValidator()
    success = validator.validate_all_rules()
    
    if not success:
        sys.exit(1)
    
    print(f"\n🎉 All rule cards validated successfully!")
    if validator.warnings:
        print(f"💡 Consider addressing {len(validator.warnings)} warnings for improved quality")


if __name__ == "__main__":
    main()
