#!/usr/bin/env python3
"""
Create Descriptive Names for Rule Cards
Analyzes rule content and generates descriptive filenames and IDs
"""

import os
import yaml
import re
from pathlib import Path
from typing import Dict, List, Tuple

class DescriptiveNameGenerator:
    def __init__(self, rule_cards_path: str = "app/rule_cards"):
        self.rule_cards_path = Path(rule_cards_path)
        self.renames_applied = []
        
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
        
        # Common security keywords for naming
        self.security_keywords = {
            # Authentication & Authorization
            'multi-factor', 'mfa', '2fa', 'oauth', 'saml', 'sso', 'token', 'password', 
            'credential', 'biometric', 'certificate', 'key', 'secret', 'hash', 'salt',
            'authentication', 'authorization', 'access', 'permission', 'role', 'privilege',
            
            # Session Management  
            'session', 'cookie', 'timeout', 'expiry', 'lifetime', 'revocation', 'invalidation',
            
            # Data Protection
            'encryption', 'decryption', 'cipher', 'cryptography', 'pii', 'gdpr', 'ccpa',
            'anonymization', 'pseudonymization', 'masking', 'redaction',
            
            # Input/Output Security
            'validation', 'sanitization', 'encoding', 'escaping', 'xss', 'injection',
            'sql', 'nosql', 'ldap', 'xpath', 'command', 'code', 'script',
            
            # Network & Communication
            'tls', 'ssl', 'https', 'certificate', 'cors', 'csp', 'hsts', 'headers',
            'firewall', 'proxy', 'load-balancer', 'cdn',
            
            # Infrastructure & Config
            'debug', 'production', 'staging', 'environment', 'logging', 'monitoring',
            'backup', 'restore', 'update', 'patch', 'vulnerability',
            
            # Actions
            'prevent', 'protection', 'detection', 'verification', 'validation',
            'implementation', 'configuration', 'management', 'handling',
            'disable', 'enable', 'enforce', 'restrict', 'allow', 'deny'
        }
    
    def generate_descriptive_names_for_all(self):
        """Generate descriptive names for all rule cards that need them"""
        print("=== Generating Descriptive Names for Rule Cards ===")
        
        total_processed = 0
        for domain_path in self.rule_cards_path.iterdir():
            if domain_path.is_dir():
                domain = domain_path.name
                print(f"\n📁 Processing domain: {domain}")
                processed = self.process_domain(domain_path, domain)
                total_processed += processed
        
        print(f"\n✅ Generated descriptive names for {len(self.renames_applied)} rules")
        return self.renames_applied
    
    def process_domain(self, domain_path: Path, domain: str) -> int:
        """Process all rules in a domain"""
        yaml_files = list(domain_path.glob("*.yml"))
        processed = 0
        
        for yaml_file in yaml_files:
            if self.needs_descriptive_name(yaml_file):
                self.generate_descriptive_name_for_file(yaml_file, domain)
                processed += 1
        
        print(f"  {processed}/{len(yaml_files)} files processed")
        return processed
    
    def needs_descriptive_name(self, yaml_file: Path) -> bool:
        """Check if file needs a descriptive name (has generic numeric ID)"""
        try:
            with open(yaml_file, 'r') as f:
                rule_data = yaml.safe_load(f)
            
            if not isinstance(rule_data, dict) or 'id' not in rule_data:
                return False
            
            rule_id = rule_data['id']
            
            # Check if ID is already descriptive (has meaningful words beyond prefix and numbers)
            # Generic pattern: PREFIX-XXX or PREFIX-XX-XXX
            if re.match(r'^[A-Z]+-\d+$', rule_id) or re.match(r'^[A-Z]+-\d+-\d+$', rule_id):
                return True
                
            return False
            
        except:
            return False
    
    def generate_descriptive_name_for_file(self, yaml_file: Path, domain: str):
        """Generate descriptive name for a single file"""
        try:
            with open(yaml_file, 'r') as f:
                rule_data = yaml.safe_load(f)
            
            if not isinstance(rule_data, dict):
                return
            
            # Generate descriptive name based on title and content
            descriptive_name = self.create_descriptive_name(rule_data, domain)
            
            if descriptive_name:
                # Update rule data
                old_id = rule_data.get('id', 'unknown')
                rule_data['id'] = descriptive_name
                
                # Create new filename
                new_filename = f"{descriptive_name}.yml"
                new_path = yaml_file.parent / new_filename
                
                # Check for conflicts
                counter = 1
                while new_path.exists() and new_path != yaml_file:
                    base_name = descriptive_name.rsplit('-', 1)[0]  # Remove last number
                    descriptive_name = f"{base_name}-{counter:03d}"
                    rule_data['id'] = descriptive_name
                    new_filename = f"{descriptive_name}.yml"
                    new_path = yaml_file.parent / new_filename
                    counter += 1
                
                # Write updated content to new file
                with open(new_path, 'w') as f:
                    yaml.dump(rule_data, f, default_flow_style=False, indent=2, sort_keys=False)
                
                # Remove old file if different
                if new_path != yaml_file:
                    yaml_file.unlink()
                
                self.renames_applied.append({
                    'domain': domain,
                    'old_filename': yaml_file.name,
                    'new_filename': new_filename,
                    'old_id': old_id,
                    'new_id': descriptive_name
                })
                
                print(f"  ✓ {yaml_file.name} → {new_filename}")
                
        except Exception as e:
            print(f"  ❌ Error processing {yaml_file.name}: {e}")
    
    def create_descriptive_name(self, rule_data: Dict, domain: str) -> str:
        """Create descriptive name based on rule content"""
        prefix = self.domain_prefixes.get(domain, domain.upper()[:6])
        title = rule_data.get('title', '').lower()
        requirement = rule_data.get('requirement', '').lower()
        
        # Extract key concepts from title and requirement
        key_concepts = self.extract_key_concepts(title, requirement)
        
        if len(key_concepts) >= 2:
            # Use top 2-3 concepts
            concepts = '-'.join(key_concepts[:3]).upper()
            return f"{prefix}-{concepts}-001"
        elif len(key_concepts) == 1:
            # Use single concept
            concept = key_concepts[0].upper()
            return f"{prefix}-{concept}-001"
        else:
            # Fallback to simplified title
            simplified = self.simplify_title(title)
            if simplified:
                return f"{prefix}-{simplified}-001"
        
        return None
    
    def extract_key_concepts(self, title: str, requirement: str) -> List[str]:
        """Extract key security concepts from text"""
        text = f"{title} {requirement}".lower()
        found_concepts = []
        
        # Look for security keywords
        for keyword in self.security_keywords:
            if keyword in text:
                # Convert to shorter form if needed
                short_form = self.get_short_form(keyword)
                if short_form not in found_concepts:
                    found_concepts.append(short_form)
        
        # Limit to most relevant concepts
        return found_concepts[:4]
    
    def get_short_form(self, keyword: str) -> str:
        """Convert keywords to shorter forms for naming"""
        short_forms = {
            'multi-factor': 'MFA',
            'authentication': 'AUTH',
            'authorization': 'AUTHZ',
            'out-of-band': 'OOB', 
            'cross-site-scripting': 'XSS',
            'sql-injection': 'SQLI',
            'command-injection': 'CMDI',
            'cross-site-request-forgery': 'CSRF',
            'transport-layer-security': 'TLS',
            'secure-socket-layer': 'SSL',
            'content-security-policy': 'CSP',
            'http-strict-transport-security': 'HSTS',
            'personally-identifiable-information': 'PII',
            'general-data-protection-regulation': 'GDPR',
            'certificate': 'CERT',
            'cryptography': 'CRYPTO',
            'encryption': 'ENCRYPT',
            'validation': 'VALID',
            'sanitization': 'SANITIZE',
            'configuration': 'CONFIG',
            'implementation': 'IMPL',
            'management': 'MGMT',
            'protection': 'PROTECT',
            'prevention': 'PREVENT',
            'detection': 'DETECT',
            'verification': 'VERIFY',
            'revocation': 'REVOKE',
            'lifetime': 'LIFETIME',
            'timeout': 'TIMEOUT'
        }
        
        return short_forms.get(keyword, keyword.upper().replace('-', ''))
    
    def simplify_title(self, title: str) -> str:
        """Create simplified version of title for naming"""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must', 'shall'}
        
        words = re.findall(r'\b\w+\b', title.lower())
        meaningful_words = [w for w in words if w not in stop_words and len(w) > 2]
        
        if meaningful_words:
            # Take first 2-3 meaningful words
            key_words = meaningful_words[:3]
            return '-'.join(key_words).upper()
        
        return None

def main():
    generator = DescriptiveNameGenerator()
    renames = generator.generate_descriptive_names_for_all()
    
    if renames:
        print(f"\n=== Summary ===")
        domain_counts = {}
        for rename in renames:
            domain = rename['domain']
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        for domain, count in sorted(domain_counts.items()):
            print(f"  {domain}: {count} rules renamed")
            
        print(f"\nTotal: {len(renames)} rules renamed with descriptive names")
        
        # Show examples
        print(f"\n=== Examples ===")
        for rename in renames[:10]:
            print(f"  {rename['old_filename']} → {rename['new_filename']}")
            print(f"    ID: {rename['old_id']} → {rename['new_id']}")
        
        if len(renames) > 10:
            print(f"  ... and {len(renames) - 10} more")
    else:
        print("\n✅ All rules already have descriptive names!")
    
    return len(renames)

if __name__ == "__main__":
    main()