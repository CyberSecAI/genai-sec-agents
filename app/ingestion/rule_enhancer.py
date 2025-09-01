"""
Rule Quality Enhancement System

Enhances Rule Cards by resolving placeholder content and improving specificity.
Addresses issues like "CWE-XXX", "relevant-scanner-rules", and generic testing methods.
"""

import os
import re
import yaml
import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PlaceholderAnalysis:
    """Analysis of placeholder content in a rule card."""
    rule_id: str
    total_placeholders: int
    cwe_placeholders: int
    scanner_placeholders: int
    test_placeholders: int
    owasp_placeholders: int
    placeholder_details: List[str]

@dataclass
class EnhancementResult:
    """Result of enhancing a rule card."""
    rule_id: str
    original_placeholders: int
    resolved_placeholders: int
    success: bool
    changes_made: List[str]
    error_message: Optional[str] = None

class RuleEnhancer:
    """Enhances Rule Cards by resolving placeholder content."""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize rule enhancer."""
        self._load_env_file()
        
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        # Initialize OpenAI client
        try:
            from openai import OpenAI
            self.openai_client = OpenAI(api_key=self.openai_api_key)
        except ImportError:
            raise ImportError("OpenAI library not available. Install with: pip install openai")
        
        self.model = "gpt-3.5-turbo"
        self.temperature = 0.1
        self.max_tokens = 2000
        
        # Load CWE database for reference
        self.cwe_database = self._load_cwe_database()
        
        # Load Semgrep rule mappings
        self.semgrep_mappings = self._load_semgrep_mappings()
        
    def _load_env_file(self):
        """Load environment variables from ../../env/.env file"""
        project_root = Path(__file__).parent.parent.parent
        env_path = project_root.parent.parent / 'env' / '.env'
        
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        value = value.strip("'\"")
                        os.environ[key] = value
    
    def _load_cwe_database(self) -> Dict[str, Any]:
        """Load CWE database for resolving CWE-XXX placeholders."""
        # This would ideally load from a comprehensive CWE database
        # For now, we'll use common security domain mappings
        return {
            'cryptography': [
                {'id': 'CWE-327', 'name': 'Use of Broken or Risky Cryptographic Algorithm'},
                {'id': 'CWE-328', 'name': 'Use of Weak Hash'},
                {'id': 'CWE-329', 'name': 'Generation of Predictable IV with CBC Mode'},
                {'id': 'CWE-330', 'name': 'Use of Insufficiently Random Values'},
                {'id': 'CWE-331', 'name': 'Insufficient Entropy'},
                {'id': 'CWE-332', 'name': 'Insufficient Entropy in PRNG'},
                {'id': 'CWE-338', 'name': 'Use of Cryptographically Weak Pseudo-Random Number Generator'},
                {'id': 'CWE-798', 'name': 'Use of Hard-coded Credentials'},
                {'id': 'CWE-320', 'name': 'Key Management Errors'},
                {'id': 'CWE-325', 'name': 'Missing Cryptographic Step'},
                {'id': 'CWE-326', 'name': 'Inadequate Encryption Strength'}
            ],
            'authentication': [
                {'id': 'CWE-287', 'name': 'Improper Authentication'},
                {'id': 'CWE-288', 'name': 'Authentication Bypass Using an Alternate Path or Channel'},
                {'id': 'CWE-289', 'name': 'Authentication Bypass by Alternate Name'},
                {'id': 'CWE-620', 'name': 'Unverified Password Change'},
                {'id': 'CWE-640', 'name': 'Weak Password Recovery Mechanism for Forgotten Password'},
                {'id': 'CWE-798', 'name': 'Use of Hard-coded Credentials'},
                {'id': 'CWE-521', 'name': 'Weak Password Requirements'},
                {'id': 'CWE-307', 'name': 'Improper Restriction of Excessive Authentication Attempts'}
            ],
            'authorization': [
                {'id': 'CWE-285', 'name': 'Improper Authorization'},
                {'id': 'CWE-284', 'name': 'Improper Access Control'},
                {'id': 'CWE-862', 'name': 'Missing Authorization'},
                {'id': 'CWE-863', 'name': 'Incorrect Authorization'},
                {'id': 'CWE-269', 'name': 'Improper Privilege Management'},
                {'id': 'CWE-250', 'name': 'Execution with Unnecessary Privileges'},
                {'id': 'CWE-732', 'name': 'Incorrect Permission Assignment for Critical Resource'}
            ],
            'input_validation': [
                {'id': 'CWE-20', 'name': 'Improper Input Validation'},
                {'id': 'CWE-79', 'name': 'Cross-site Scripting'},
                {'id': 'CWE-89', 'name': 'SQL Injection'},
                {'id': 'CWE-78', 'name': 'OS Command Injection'},
                {'id': 'CWE-94', 'name': 'Improper Control of Generation of Code'},
                {'id': 'CWE-91', 'name': 'XML Injection'},
                {'id': 'CWE-643', 'name': 'Improper Neutralization of Data within XPath Expressions'},
                {'id': 'CWE-22', 'name': 'Path Traversal'}
            ],
            'session_management': [
                {'id': 'CWE-384', 'name': 'Session Fixation'},
                {'id': 'CWE-613', 'name': 'Insufficient Session Expiration'},
                {'id': 'CWE-664', 'name': 'Improper Control of a Resource Through its Lifetime'},
                {'id': 'CWE-693', 'name': 'Protection Mechanism Failure'},
                {'id': 'CWE-311', 'name': 'Missing Encryption of Sensitive Data'}
            ]
        }
    
    def _load_semgrep_mappings(self) -> Dict[str, List[str]]:
        """Load Semgrep rule mappings for different security domains."""
        return {
            'cryptography': [
                'crypto.key-hardcoded',
                'generic.secrets.security.detected-hardcoded-key',
                'crypto.weak-crypto',
                'crypto.weak-hash',
                'crypto.insecure-randomness',
                'crypto.weak-cipher',
                'generic.secrets.security.detected-cryptographic-key'
            ],
            'authentication': [
                'security.hardcoded-credentials',
                'security.weak-password-requirements',
                'security.authentication-bypass',
                'security.session-management',
                'generic.secrets.security.detected-password'
            ],
            'authorization': [
                'security.authorization-bypass',
                'security.privilege-escalation',
                'security.access-control',
                'security.permission-bypass'
            ],
            'input_validation': [
                'security.injection.sql-injection',
                'security.injection.command-injection', 
                'security.xss.reflected-xss',
                'security.xss.stored-xss',
                'security.path-traversal',
                'security.xml-injection'
            ],
            'session_management': [
                'security.session-fixation',
                'security.session-timeout',
                'security.insecure-session',
                'security.cookie-security'
            ]
        }
    
    def analyze_placeholders(self, rule_card: Dict[str, Any]) -> PlaceholderAnalysis:
        """Analyze placeholder content in a rule card."""
        rule_id = rule_card.get('id', 'UNKNOWN')
        placeholder_details = []
        
        # Check for CWE placeholders
        cwe_placeholders = 0
        cwe_refs = rule_card.get('refs', {}).get('cwe', [])
        for cwe in cwe_refs:
            if isinstance(cwe, str) and ('CWE-XXX' in cwe or 'CWE-###' in cwe):
                cwe_placeholders += 1
                placeholder_details.append(f"CWE placeholder: {cwe}")
        
        # Check for scanner rule placeholders
        scanner_placeholders = 0
        semgrep_rules = rule_card.get('detect', {}).get('semgrep', [])
        for rule in semgrep_rules:
            if isinstance(rule, str) and ('relevant-scanner-rules' in rule or 'TODO' in rule):
                scanner_placeholders += 1
                placeholder_details.append(f"Scanner placeholder: {rule}")
        
        # Check for test method placeholders
        test_placeholders = 0
        test_methods = rule_card.get('verify', {}).get('tests', [])
        for test in test_methods:
            if isinstance(test, str) and ('Testing methods' in test or 'TODO' in test):
                test_placeholders += 1
                placeholder_details.append(f"Test placeholder: {test}")
        
        # Check for OWASP placeholders
        owasp_placeholders = 0
        owasp_refs = rule_card.get('refs', {}).get('owasp', [])
        for ref in owasp_refs:
            if isinstance(ref, str) and ('A##:' in ref or 'TODO' in ref):
                owasp_placeholders += 1
                placeholder_details.append(f"OWASP placeholder: {ref}")
        
        total_placeholders = cwe_placeholders + scanner_placeholders + test_placeholders + owasp_placeholders
        
        return PlaceholderAnalysis(
            rule_id=rule_id,
            total_placeholders=total_placeholders,
            cwe_placeholders=cwe_placeholders,
            scanner_placeholders=scanner_placeholders,
            test_placeholders=test_placeholders,
            owasp_placeholders=owasp_placeholders,
            placeholder_details=placeholder_details
        )
    
    def resolve_cwe_placeholders(self, rule_card: Dict[str, Any], domain: str) -> List[str]:
        """Resolve CWE-XXX placeholders with specific CWE references."""
        changes = []
        
        if 'refs' not in rule_card:
            return changes
        
        if 'cwe' not in rule_card['refs']:
            return changes
        
        cwe_refs = rule_card['refs']['cwe']
        if not isinstance(cwe_refs, list):
            return changes
        
        # Get relevant CWEs for this domain
        domain_cwes = self.cwe_database.get(domain, [])
        if not domain_cwes:
            return changes
        
        # Replace placeholders with specific CWEs
        updated_cwes = []
        for cwe in cwe_refs:
            if isinstance(cwe, str) and ('CWE-XXX' in cwe or 'CWE-###' in cwe):
                # Replace with top 2-3 most relevant CWEs for domain
                for domain_cwe in domain_cwes[:3]:
                    updated_cwes.append(domain_cwe['id'])
                changes.append(f"Replaced '{cwe}' with specific CWEs: {[c['id'] for c in domain_cwes[:3]]}")
            else:
                updated_cwes.append(cwe)
        
        rule_card['refs']['cwe'] = updated_cwes
        return changes
    
    def resolve_semgrep_placeholders(self, rule_card: Dict[str, Any], domain: str) -> List[str]:
        """Resolve relevant-scanner-rules placeholders with specific Semgrep rules."""
        changes = []
        
        if 'detect' not in rule_card:
            return changes
        
        if 'semgrep' not in rule_card['detect']:
            return changes
        
        semgrep_rules = rule_card['detect']['semgrep']
        if not isinstance(semgrep_rules, list):
            return changes
        
        # Get relevant Semgrep rules for this domain
        domain_rules = self.semgrep_mappings.get(domain, [])
        if not domain_rules:
            return changes
        
        # Replace placeholders with specific rules
        updated_rules = []
        for rule in semgrep_rules:
            if isinstance(rule, str) and ('relevant-scanner-rules' in rule or 'TODO' in rule):
                # Replace with domain-specific rules
                updated_rules.extend(domain_rules[:3])  # Top 3 most relevant
                changes.append(f"Replaced '{rule}' with specific Semgrep rules: {domain_rules[:3]}")
            else:
                updated_rules.append(rule)
        
        rule_card['detect']['semgrep'] = updated_rules
        return changes
    
    def enhance_rule_with_llm(self, rule_card: Dict[str, Any], domain: str) -> Tuple[Dict[str, Any], List[str]]:
        """Use LLM to enhance rule card quality and resolve remaining placeholders."""
        changes = []
        
        # Create enhancement prompt
        prompt = f"""You are a security expert enhancing a Rule Card in the {domain} domain.

Please improve this rule card by:
1. Replacing any remaining placeholders with specific, actionable content
2. Adding more specific testing methods instead of generic "Testing methods"
3. Ensuring all guidance is practical and implementable
4. Maintaining the exact YAML structure

Current Rule Card:
```yaml
{yaml.dump(rule_card, default_flow_style=False, sort_keys=False)}
```

Rules for enhancement:
- Keep the same rule ID and basic structure
- Make 'do' and 'dont' sections more specific and actionable
- Replace generic testing methods with concrete test approaches
- Ensure detect.semgrep rules are realistic (if not already specific)
- Keep refs.cwe references accurate to the actual security vulnerabilities addressed
- Maintain refs.asvs if present
- Update refs.owasp to accurate 2021 Top 10 references if applicable

Output only the enhanced YAML rule card:"""

        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            enhanced_yaml = response.choices[0].message.content.strip()
            
            # Remove code block markers
            if enhanced_yaml.startswith('```yaml'):
                enhanced_yaml = enhanced_yaml[7:]
            elif enhanced_yaml.startswith('```'):
                enhanced_yaml = enhanced_yaml[3:]
            if enhanced_yaml.endswith('```'):
                enhanced_yaml = enhanced_yaml[:-3]
            
            # Parse enhanced rule
            enhanced_rule = yaml.safe_load(enhanced_yaml.strip())
            
            if enhanced_rule and isinstance(enhanced_rule, dict):
                changes.append("Enhanced rule content with LLM for better specificity")
                return enhanced_rule, changes
            else:
                logger.warning("LLM returned invalid YAML structure")
                return rule_card, changes
                
        except Exception as e:
            logger.error(f"LLM enhancement failed: {e}")
            return rule_card, changes
    
    def enhance_rule_card(self, rule_card: Dict[str, Any], domain: str) -> EnhancementResult:
        """Enhance a rule card by resolving placeholders and improving quality."""
        rule_id = rule_card.get('id', 'UNKNOWN')
        
        # Analyze initial placeholders
        initial_analysis = self.analyze_placeholders(rule_card)
        
        changes = []
        enhanced_rule = rule_card.copy()
        
        try:
            # Resolve CWE placeholders
            cwe_changes = self.resolve_cwe_placeholders(enhanced_rule, domain)
            changes.extend(cwe_changes)
            
            # Resolve Semgrep placeholders
            semgrep_changes = self.resolve_semgrep_placeholders(enhanced_rule, domain)
            changes.extend(semgrep_changes)
            
            # Use LLM for final enhancement
            enhanced_rule, llm_changes = self.enhance_rule_with_llm(enhanced_rule, domain)
            changes.extend(llm_changes)
            
            # Analyze final placeholders
            final_analysis = self.analyze_placeholders(enhanced_rule)
            
            resolved_placeholders = initial_analysis.total_placeholders - final_analysis.total_placeholders
            
            return EnhancementResult(
                rule_id=rule_id,
                original_placeholders=initial_analysis.total_placeholders,
                resolved_placeholders=resolved_placeholders,
                success=True,
                changes_made=changes,
                error_message=None
            )
            
        except Exception as e:
            return EnhancementResult(
                rule_id=rule_id,
                original_placeholders=initial_analysis.total_placeholders,
                resolved_placeholders=0,
                success=False,
                changes_made=changes,
                error_message=str(e)
            )
    
    def enhance_domain_rules(self, domain: str) -> List[EnhancementResult]:
        """Enhance all rules in a domain directory."""
        domain_path = Path("app/rule_cards") / domain
        
        if not domain_path.exists():
            logger.warning(f"Domain directory {domain} does not exist")
            return []
        
        results = []
        yaml_files = list(domain_path.glob("**/*.yml")) + list(domain_path.glob("**/*.yaml"))
        
        for yaml_file in yaml_files:
            try:
                # Load rule
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    rule_card = yaml.safe_load(f)
                
                if not rule_card or not isinstance(rule_card, dict):
                    continue
                
                # Check if enhancement is needed
                analysis = self.analyze_placeholders(rule_card)
                if analysis.total_placeholders == 0:
                    logger.info(f"Rule {rule_card.get('id')} has no placeholders, skipping")
                    continue
                
                logger.info(f"Enhancing rule {rule_card.get('id')} ({analysis.total_placeholders} placeholders)")
                
                # Enhance rule
                result = self.enhance_rule_card(rule_card, domain)
                results.append(result)
                
                if result.success and result.resolved_placeholders > 0:
                    # Save enhanced rule back to file
                    enhanced_rule = rule_card  # The enhance_rule_card modifies in place
                    with open(yaml_file, 'w', encoding='utf-8') as f:
                        yaml.dump(enhanced_rule, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
                    
                    logger.info(f"Enhanced and saved rule {result.rule_id}")
                
            except Exception as e:
                logger.error(f"Failed to enhance rule from {yaml_file}: {e}")
                continue
        
        return results

def main():
    """Test rule enhancement functionality."""
    logging.basicConfig(level=logging.INFO)
    
    try:
        enhancer = RuleEnhancer()
        
        print("🔍 Testing Rule Enhancement System...")
        
        # Test with cryptography domain
        results = enhancer.enhance_domain_rules("cryptography")
        
        if results:
            print(f"✅ Enhanced {len(results)} rules in cryptography domain")
            
            total_original = sum(r.original_placeholders for r in results)
            total_resolved = sum(r.resolved_placeholders for r in results)
            successful = sum(1 for r in results if r.success)
            
            print(f"   Rules processed: {len(results)}")
            print(f"   Successful enhancements: {successful}")
            print(f"   Original placeholders: {total_original}")
            print(f"   Resolved placeholders: {total_resolved}")
            print(f"   Resolution rate: {(total_resolved/total_original)*100:.1f}%" if total_original > 0 else "   No placeholders found")
            
        else:
            print("❌ No rules enhanced")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()