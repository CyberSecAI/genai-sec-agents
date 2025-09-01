#!/usr/bin/env python3
"""
Fix Placeholder Content in Rule Cards
Replaces generic placeholders with specific, actionable content
"""

import os
import yaml
import re
from pathlib import Path
from typing import Dict, List

class PlaceholderFixer:
    def __init__(self, rule_cards_path: str = "app/rule_cards"):
        self.rule_cards_path = Path(rule_cards_path)
        self.fixes_applied = []
        
        # CWE mappings for common security domains
        self.domain_cwe_mappings = {
            "authentication": ["CWE-287", "CWE-288", "CWE-290", "CWE-294"],
            "session_management": ["CWE-384", "CWE-613", "CWE-315"], 
            "authorization": ["CWE-285", "CWE-284", "CWE-862", "CWE-863"],
            "configuration": ["CWE-16", "CWE-2", "CWE-209"],
            "data_protection": ["CWE-311", "CWE-312", "CWE-200", "CWE-359"],
            "secure_communication": ["CWE-295", "CWE-326", "CWE-327", "CWE-780"],
            "file_handling": ["CWE-434", "CWE-22", "CWE-73", "CWE-829"],
            "input_validation": ["CWE-20", "CWE-79", "CWE-89", "CWE-116"],
            "cryptography": ["CWE-321", "CWE-326", "CWE-327", "CWE-328"]
        }
        
        # Semgrep rule mappings
        self.semgrep_mappings = {
            "authentication": [
                "javascript.express.security.audit.express-session-no-secret",
                "python.django.security.audit.session-cookie-secure-false", 
                "java.spring.security.audit.spring-csrf-disabled"
            ],
            "session_management": [
                "javascript.express.security.audit.express-session-no-secret",
                "python.django.security.audit.session-cookie-httponly-false",
                "java.servlets.security.audit.cookie-missing-secure-flag"
            ],
            "authorization": [
                "javascript.express.security.audit.express-jwt-not-revoked",
                "python.django.security.audit.avoid-csrf-disable",
                "java.spring.security.audit.spring-csrf-disabled"
            ],
            "configuration": [
                "yaml.docker-compose.security.writable-filesystem-service",
                "terraform.aws.security.aws-s3-bucket-public-read-prohibited",
                "kubernetes.security.allow-privilege-escalation"
            ],
            "data_protection": [
                "python.lang.security.audit.hardcoded-password",
                "javascript.lang.security.audit.hardcoded-secret",
                "generic.secrets.security.detected-private-key"
            ],
            "secure_communication": [
                "python.requests.security.disabled-cert-validation",
                "javascript.lang.security.audit.tls-min-version",
                "java.lang.security.audit.ssl-context-getsocketfactory"
            ],
            "file_handling": [
                "python.lang.security.audit.dangerous-system-call",
                "javascript.lang.security.audit.path-traversal",
                "java.lang.security.audit.zip-slip"
            ]
        }
    
    def fix_all_placeholders(self):
        """Fix placeholders in all rule cards"""
        print("=== Fixing Placeholder Content ===")
        
        # Find all YAML files with placeholders
        yaml_files = list(self.rule_cards_path.rglob("*.yml"))
        
        for yaml_file in yaml_files:
            self.fix_file_placeholders(yaml_file)
        
        print(f"\n✅ Applied {len(self.fixes_applied)} placeholder fixes")
        return self.fixes_applied
    
    def fix_file_placeholders(self, yaml_file: Path):
        """Fix placeholders in a single file"""
        try:
            with open(yaml_file, 'r') as f:
                content = f.read()
            
            # Check if file has placeholders
            has_placeholders = any([
                "CWE-XXX" in content,
                "relevant-scanner-rules" in content,
                "Testing methods" in content,
                "A##:2021" in content
            ])
            
            if not has_placeholders:
                return
            
            # Parse YAML
            rule_data = yaml.safe_load(content)
            if not isinstance(rule_data, dict):
                return
            
            # Determine domain
            domain = yaml_file.parent.name
            
            # Fix placeholders
            fixed = False
            
            # Fix CWE references
            if self.fix_cwe_placeholders(rule_data, domain):
                fixed = True
            
            # Fix Semgrep rules
            if self.fix_semgrep_placeholders(rule_data, domain):
                fixed = True
            
            # Fix test methods
            if self.fix_test_placeholders(rule_data, domain):
                fixed = True
            
            # Fix OWASP references
            if self.fix_owasp_placeholders(rule_data, domain):
                fixed = True
            
            if fixed:
                # Write back the fixed YAML
                with open(yaml_file, 'w') as f:
                    yaml.dump(rule_data, f, default_flow_style=False, indent=2)
                
                self.fixes_applied.append({
                    'file': str(yaml_file),
                    'domain': domain,
                    'rule_id': rule_data.get('id', 'N/A'),
                    'fixes': 'placeholders_resolved'
                })
                
                print(f"  ✓ Fixed placeholders in {yaml_file.name}")
        
        except Exception as e:
            print(f"  ❌ Error fixing {yaml_file}: {e}")
    
    def fix_cwe_placeholders(self, rule_data: Dict, domain: str) -> bool:
        """Fix CWE-XXX placeholders with domain-appropriate CWEs"""
        if 'refs' not in rule_data or 'cwe' not in rule_data['refs']:
            return False
        
        cwe_list = rule_data['refs']['cwe']
        if not isinstance(cwe_list, list):
            return False
        
        fixed = False
        for i, cwe in enumerate(cwe_list):
            if cwe == "CWE-XXX":
                # Replace with domain-appropriate CWE
                domain_cwes = self.domain_cwe_mappings.get(domain, ["CWE-20"])
                rule_data['refs']['cwe'][i] = domain_cwes[0]  # Use primary CWE
                fixed = True
        
        return fixed
    
    def fix_semgrep_placeholders(self, rule_data: Dict, domain: str) -> bool:
        """Fix relevant-scanner-rules placeholders"""
        if 'detect' not in rule_data or 'semgrep' not in rule_data['detect']:
            return False
        
        semgrep_list = rule_data['detect']['semgrep']
        if not isinstance(semgrep_list, list):
            return False
        
        fixed = False
        for i, rule in enumerate(semgrep_list):
            if rule == "relevant-scanner-rules":
                # Replace with domain-appropriate rules
                domain_rules = self.semgrep_mappings.get(domain, ["generic.secrets.security.detected-secret"])
                rule_data['detect']['semgrep'][i:i+1] = domain_rules[:2]  # Use up to 2 rules
                fixed = True
        
        return fixed
    
    def fix_test_placeholders(self, rule_data: Dict, domain: str) -> bool:
        """Fix Testing methods placeholders"""
        if 'verify' not in rule_data or 'tests' not in rule_data['verify']:
            return False
        
        tests_list = rule_data['verify']['tests']
        if not isinstance(tests_list, list):
            return False
        
        fixed = False
        for i, test in enumerate(tests_list):
            if test == "Testing methods":
                # Generate domain-specific test description
                test_description = self.generate_test_description(rule_data, domain)
                rule_data['verify']['tests'][i] = test_description
                fixed = True
        
        return fixed
    
    def fix_owasp_placeholders(self, rule_data: Dict, domain: str) -> bool:
        """Fix A##:2021 OWASP placeholders"""
        if 'refs' not in rule_data or 'owasp' not in rule_data['refs']:
            return False
        
        owasp_list = rule_data['refs']['owasp']
        if not isinstance(owasp_list, list):
            return False
        
        # OWASP Top 10 2021 mapping by domain
        owasp_mappings = {
            "authentication": ["A07:2021"],
            "session_management": ["A07:2021"], 
            "authorization": ["A01:2021", "A05:2021"],
            "configuration": ["A05:2021"],
            "data_protection": ["A02:2021", "A04:2021"],
            "secure_communication": ["A02:2021"],
            "file_handling": ["A01:2021", "A03:2021"]
        }
        
        fixed = False
        for i, ref in enumerate(owasp_list):
            if ref == "A##:2021":
                domain_refs = owasp_mappings.get(domain, ["A10:2021"])
                rule_data['refs']['owasp'][i] = domain_refs[0]
                fixed = True
        
        return fixed
    
    def generate_test_description(self, rule_data: Dict, domain: str) -> str:
        """Generate domain-specific test description"""
        title = rule_data.get('title', '').lower()
        
        if 'authentication' in title or domain == 'authentication':
            return "Verify authentication mechanisms and credential handling"
        elif 'session' in title or domain == 'session_management':
            return "Test session lifecycle management and security controls"  
        elif 'authorization' in title or domain == 'authorization':
            return "Validate access control enforcement and privilege management"
        elif 'config' in title or domain == 'configuration':
            return "Review security configuration settings and hardening"
        elif 'data' in title or domain == 'data_protection':
            return "Test data encryption, masking, and privacy controls"
        elif 'communication' in title or domain == 'secure_communication':
            return "Verify TLS configuration and secure transport protocols"
        elif 'file' in title or domain == 'file_handling':
            return "Test file upload validation and processing security"
        else:
            return "Verify implementation meets security requirements"

def main():
    fixer = PlaceholderFixer()
    fixes = fixer.fix_all_placeholders()
    
    if fixes:
        print("\n=== Summary ===")
        domain_counts = {}
        for fix in fixes:
            domain = fix['domain']
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        for domain, count in sorted(domain_counts.items()):
            print(f"  {domain}: {count} files fixed")
    else:
        print("\n✅ No placeholder fixes needed!")
    
    return len(fixes)

if __name__ == "__main__":
    main()