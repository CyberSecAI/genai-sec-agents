#!/usr/bin/env python3
"""
Domain-Based ASVS Rule Card Generator

Intelligently integrates ASVS verification requirements with existing Rule Cards
organized by security domains (cryptography, authentication, etc.) rather than by source.

Enhances existing rules and creates new ones as needed.
"""

import os
import sys
import json
import yaml
import logging
import time
import glob
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from app.ingestion.asvs_fetcher import ASVSFetcher, ASVSSection, ASVSVerificationRequirement
from app.ingestion.asvs_rule_generator import ASVSRuleCardGenerator

logger = logging.getLogger(__name__)


@dataclass
class DomainIntegrationResult:
    """Result of integrating ASVS requirements with existing domain rules."""
    domain: str
    asvs_section: str
    existing_rules_count: int
    asvs_requirements_count: int
    new_rules_created: int
    existing_rules_enhanced: int
    success: bool
    tokens_used: int
    error_message: Optional[str] = None


class DomainBasedASVSGenerator:
    """Generates and integrates ASVS Rule Cards by security domain."""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize domain-based ASVS generator."""
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
        self.max_tokens = 3000  # Increased for integration tasks
        self.rate_limit_delay = 2
        
        # Domain mapping for ASVS sections
        self.asvs_domain_mapping = {
            'V1-Encoding-Sanitization': 'input_validation',
            'V2-Validation-Business-Logic': 'input_validation', 
            'V3-Web-Frontend-Security': 'web_security',
            'V4-API-Web-Service': 'api_security',
            'V5-File-Handling': 'file_handling',
            'V6-Authentication': 'authentication',
            'V7-Session-Management': 'session_management',
            'V8-Authorization': 'authorization',
            'V9-Self-contained-Tokens': 'authentication',
            'V10-OAuth-OIDC': 'authentication',
            'V11-Cryptography': 'cryptography',
            'V12-Secure-Communication': 'network_security',
            'V13-Configuration': 'configuration',
            'V14-Data-Protection': 'data_protection',
            'V15-Secure-Coding-Architecture': 'secure_coding',
            'V16-Logging-Error-Handling': 'logging',
            'V17-WebRTC': 'web_security'
        }
        
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
            print(f"Loaded environment variables from {env_path}")
        else:
            print(f"Warning: Environment file not found at {env_path}")
    
    def get_domain_for_asvs_section(self, asvs_section_id: str) -> str:
        """Get the security domain for an ASVS section."""
        return self.asvs_domain_mapping.get(asvs_section_id, 'general')
    
    def load_existing_domain_rules(self, domain: str) -> List[Dict[str, Any]]:
        """Load existing Rule Cards from a security domain."""
        domain_path = Path("app/rule_cards") / domain
        existing_rules = []
        
        if not domain_path.exists():
            logger.info(f"Domain directory {domain} does not exist yet")
            return existing_rules
        
        # Find all YAML files in domain directory (including subdirectories)
        yaml_files = list(domain_path.glob("**/*.yml")) + list(domain_path.glob("**/*.yaml"))
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    rule_data = yaml.safe_load(f)
                    if rule_data and isinstance(rule_data, dict):
                        rule_data['_source_file'] = str(yaml_file)
                        existing_rules.append(rule_data)
            except Exception as e:
                logger.warning(f"Failed to load rule from {yaml_file}: {e}")
                continue
        
        logger.info(f"Loaded {len(existing_rules)} existing rules from {domain} domain")
        return existing_rules
    
    def create_domain_integration_prompt(self, 
                                       asvs_requirements: List[ASVSVerificationRequirement],
                                       existing_rules: List[Dict[str, Any]],
                                       domain: str) -> str:
        """Create prompt for integrating ASVS requirements with existing domain rules."""
        
        # Format existing rules
        existing_rules_text = ""
        if existing_rules:
            existing_rules_text = "\n\nEXISTING RULES IN THIS DOMAIN:\n"
            for i, rule in enumerate(existing_rules[:5], 1):  # Show first 5 existing rules
                existing_rules_text += f"\nRule {i}:\n"
                existing_rules_text += f"ID: {rule.get('id', 'N/A')}\n"
                existing_rules_text += f"Title: {rule.get('title', 'N/A')}\n"
                existing_rules_text += f"Requirement: {rule.get('requirement', 'N/A')[:100]}...\n"
            
            if len(existing_rules) > 5:
                existing_rules_text += f"\n... and {len(existing_rules) - 5} more existing rules"
        
        # Format ASVS requirements
        asvs_text = "\n\nASVS REQUIREMENTS TO INTEGRATE:\n"
        for req in asvs_requirements:
            asvs_text += f"\nASVS {req.id} (Level {req.level}):\n"
            asvs_text += f"Category: {req.category}\n"
            asvs_text += f"Description: {req.description}\n"
        
        prompt = f"""You are a security expert integrating OWASP ASVS requirements with existing Rule Cards in the {domain} security domain.

Your task is to intelligently merge ASVS verification requirements with existing rules:

1. **ENHANCE EXISTING RULES**: If an ASVS requirement covers similar ground to an existing rule, enhance the existing rule by:
   - Adding ASVS-specific guidance to 'do' and 'dont' sections
   - Adding the ASVS reference to 'refs.asvs'
   - Updating the requirement text if ASVS provides more comprehensive guidance
   - Keep the existing rule ID

2. **CREATE NEW RULES**: Only create new Rule Cards for ASVS requirements that address security concerns not covered by existing rules

3. **MAINTAIN CONSISTENCY**: Ensure all rules follow the same YAML schema and quality standards

YAML Schema for Rule Cards:
```yaml
id: DOMAIN-TOPIC-### (for new rules) or existing ID (for enhanced rules)
title: "Actionable title"
severity: high/medium/low (based on ASVS level: 3=high, 2=medium, 1=low)
scope: web-application/api/mobile/infrastructure
requirement: "Clear requirement description"
do:
  - "Specific implementation actions"
dont:
  - "What to avoid"
detect:
  semgrep:
    - "relevant-scanner-rules"
verify:
  tests:
    - "Testing methods"
refs:
  cwe:
    - "CWE-XXX"
  asvs:
    - "V##.##.##"
  owasp:
    - "A##:2021"
```

INSTRUCTIONS:
- Output ENHANCED rules first, then NEW rules
- Use "---" to separate multiple YAML documents
- For enhanced rules, clearly indicate what was added/changed in comments
- Prioritize enhancing existing rules over creating new ones
- Ensure no duplicate coverage between rules

{existing_rules_text}

{asvs_text}

Generate the integrated Rule Cards:"""

        return prompt
    
    def integrate_asvs_with_domain(self, 
                                  asvs_section: ASVSSection, 
                                  domain: str,
                                  max_requirements_per_batch: int = 8) -> DomainIntegrationResult:
        """Integrate ASVS section requirements with existing domain rules."""
        logger.info(f"Integrating ASVS section {asvs_section.title} with {domain} domain")
        
        # Load existing rules from domain
        existing_rules = self.load_existing_domain_rules(domain)
        
        # Process ASVS requirements in batches
        all_integrated_rules = []
        total_tokens = 0
        
        requirements = asvs_section.requirements
        for i in range(0, len(requirements), max_requirements_per_batch):
            batch = requirements[i:i + max_requirements_per_batch]
            logger.info(f"Processing batch {i//max_requirements_per_batch + 1}: {len(batch)} ASVS requirements")
            
            # Create integration prompt
            prompt = self.create_domain_integration_prompt(batch, existing_rules, domain)
            
            # Call OpenAI API
            try:
                response = self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                
                content = response.choices[0].message.content
                tokens_used = response.usage.total_tokens
                total_tokens += tokens_used
                
                # Parse integrated rules
                batch_rules = self._parse_yaml_rule_cards(content)
                all_integrated_rules.extend(batch_rules)
                
                logger.info(f"Batch {i//max_requirements_per_batch + 1}: Generated {len(batch_rules)} integrated rules")
                
            except Exception as e:
                logger.error(f"Failed to process batch {i//max_requirements_per_batch + 1}: {e}")
                continue
            
            # Rate limiting
            time.sleep(self.rate_limit_delay)
        
        # Analyze integration results
        new_rules = [r for r in all_integrated_rules if not any(
            r.get('id') == existing.get('id') for existing in existing_rules
        )]
        enhanced_rules = [r for r in all_integrated_rules if any(
            r.get('id') == existing.get('id') for existing in existing_rules
        )]
        
        success = len(all_integrated_rules) > 0
        
        result = DomainIntegrationResult(
            domain=domain,
            asvs_section=asvs_section.id,
            existing_rules_count=len(existing_rules),
            asvs_requirements_count=len(requirements),
            new_rules_created=len(new_rules),
            existing_rules_enhanced=len(enhanced_rules),
            success=success,
            tokens_used=total_tokens,
            error_message=None if success else "No rules generated"
        )
        
        if success:
            # Save integrated rules
            self._save_integrated_rules(all_integrated_rules, domain)
        
        logger.info(f"Domain integration complete: {len(new_rules)} new, {len(enhanced_rules)} enhanced")
        return result
    
    def _parse_yaml_rule_cards(self, yaml_content: str) -> List[Dict[str, Any]]:
        """Parse YAML Rule Cards from LLM response."""
        rule_cards = []
        
        try:
            # Handle multiple YAML documents separated by ---
            yaml_docs = yaml_content.split('---')
            
            for doc in yaml_docs:
                doc = doc.strip()
                if not doc:
                    continue
                
                # Remove code block markers if present
                if doc.startswith('```yaml'):
                    doc = doc[7:]
                if doc.startswith('```'):
                    doc = doc[3:]
                if doc.endswith('```'):
                    doc = doc[:-3]
                
                doc = doc.strip()
                if not doc:
                    continue
                
                # Remove comments and parse
                lines = doc.split('\n')
                cleaned_lines = []
                for line in lines:
                    if not line.strip().startswith('#'):
                        cleaned_lines.append(line)
                cleaned_doc = '\n'.join(cleaned_lines)
                
                try:
                    rule_card = yaml.safe_load(cleaned_doc)
                    if rule_card and isinstance(rule_card, dict):
                        rule_cards.append(rule_card)
                except yaml.YAMLError as e:
                    logger.warning(f"Failed to parse YAML rule card: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Failed to parse rule cards from response: {e}")
        
        return rule_cards
    
    def _save_integrated_rules(self, integrated_rules: List[Dict[str, Any]], domain: str) -> bool:
        """Save integrated rules to the domain directory."""
        try:
            domain_path = Path("app/rule_cards") / domain
            domain_path.mkdir(parents=True, exist_ok=True)
            
            saved_count = 0
            
            for rule in integrated_rules:
                rule_id = rule.get('id', f"RULE-{saved_count + 1:03d}")
                filename = f"{rule_id}.yml"
                file_path = domain_path / filename
                
                # Save rule as YAML
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(rule, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
                
                saved_count += 1
            
            logger.info(f"Saved {saved_count} integrated rules to {domain_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save integrated rules to {domain}: {e}")
            return False
    
    def process_asvs_section_by_domain(self, asvs_section: ASVSSection) -> DomainIntegrationResult:
        """Process an ASVS section and integrate with the appropriate domain."""
        domain = self.get_domain_for_asvs_section(asvs_section.id)
        logger.info(f"Processing ASVS {asvs_section.title} → {domain} domain")
        
        return self.integrate_asvs_with_domain(asvs_section, domain)
    
    def run_bulk_domain_integration(self, priority_levels: List[int] = [1, 2]) -> Dict[str, DomainIntegrationResult]:
        """Run domain-based integration for multiple ASVS sections."""
        logger.info(f"Starting bulk domain integration for ASVS priority levels: {priority_levels}")
        
        # Initialize ASVS fetcher
        asvs_fetcher = ASVSFetcher()
        
        # Fetch ASVS sections
        sections = asvs_fetcher.fetch_all_priority_sections(priority_levels)
        
        if not sections:
            logger.error("No ASVS sections fetched")
            return {}
        
        results = {}
        total_tokens = 0
        
        for section in sections:
            logger.info(f"Processing ASVS section: {section.title}")
            
            result = self.process_asvs_section_by_domain(section)
            results[section.id] = result
            
            total_tokens += result.tokens_used
            
            # Rate limiting between sections
            time.sleep(self.rate_limit_delay)
        
        # Log summary
        successful_sections = sum(1 for r in results.values() if r.success)
        total_new_rules = sum(r.new_rules_created for r in results.values())
        total_enhanced_rules = sum(r.existing_rules_enhanced for r in results.values())
        
        logger.info(f"Domain integration complete:")
        logger.info(f"  Sections processed: {len(results)}")
        logger.info(f"  Successful sections: {successful_sections}")
        logger.info(f"  New rules created: {total_new_rules}")
        logger.info(f"  Existing rules enhanced: {total_enhanced_rules}")
        logger.info(f"  Total tokens used: {total_tokens}")
        logger.info(f"  Estimated cost: ${total_tokens * 0.0015 / 1000:.3f}")
        
        return results


def main():
    """Test domain-based ASVS integration."""
    logging.basicConfig(level=logging.INFO)
    
    try:
        generator = DomainBasedASVSGenerator()
        
        # Test with Cryptography section
        asvs_fetcher = ASVSFetcher()
        
        test_section_info = {
            'id': 'V11-Cryptography',
            'title': 'Cryptography',
            'file': '0x20-V11-Cryptography.md',
            'url': asvs_fetcher.base_url + '0x20-V11-Cryptography.md',
            'github_url': asvs_fetcher.github_base + '0x20-V11-Cryptography.md',
            'description': 'Cryptographic implementation and key management',
            'priority': 1
        }
        
        # Fetch the section
        section = asvs_fetcher.fetch_asvs_section(test_section_info)
        
        if not section:
            print("❌ Failed to fetch ASVS section")
            return
        
        print(f"🔍 Testing domain integration for {section.title}")
        
        # Process section with domain integration
        result = generator.process_asvs_section_by_domain(section)
        
        if result.success:
            print(f"✅ Domain integration successful!")
            print(f"   Domain: {result.domain}")
            print(f"   Existing rules: {result.existing_rules_count}")
            print(f"   ASVS requirements: {result.asvs_requirements_count}")
            print(f"   New rules created: {result.new_rules_created}")
            print(f"   Existing rules enhanced: {result.existing_rules_enhanced}")
            print(f"   Tokens used: {result.tokens_used}")
            print(f"   Estimated cost: ${result.tokens_used * 0.0015 / 1000:.3f}")
        else:
            print(f"❌ Domain integration failed: {result.error_message}")
    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()