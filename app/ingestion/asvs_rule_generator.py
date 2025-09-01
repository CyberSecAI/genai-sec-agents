#!/usr/bin/env python3
"""
ASVS Rule Card Generator

Generates Rule Cards from OWASP ASVS (Application Security Verification Standard)
verification requirements using ChatGPT/OpenAI API.

Extension of Story 2.5 for ASVS integration
"""

import os
import sys
import json
import yaml
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from app.ingestion.asvs_fetcher import ASVSFetcher, ASVSSection, ASVSVerificationRequirement

logger = logging.getLogger(__name__)


@dataclass
class ASVSRuleCardResult:
    """Result of ASVS Rule Card generation."""
    asvs_id: str
    success: bool
    rule_cards: List[Dict[str, Any]]
    error_message: Optional[str] = None
    tokens_used: int = 0


class ASVSRuleCardGenerator:
    """Generates Rule Cards from ASVS verification requirements using LLM."""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize ASVS Rule Card generator."""
        self._load_env_file()  # Load environment variables
        
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        self.model = "gpt-3.5-turbo"
        self.temperature = 0.1
        self.max_tokens = 2000
        self.rate_limit_delay = 2  # Seconds between API calls
        
        # Initialize OpenAI client
        try:
            from openai import OpenAI
            self.openai_client = OpenAI(api_key=self.openai_api_key)
        except ImportError:
            raise ImportError("OpenAI library not available. Install with: pip install openai")
        
        # ASVS-specific prompt template
        self.asvs_prompt_template = self._create_asvs_prompt_template()
        
    def _load_env_file(self):
        """Load environment variables from ../../env/.env file"""
        # From app/ingestion/asvs_rule_generator.py, go up to project root, then to ../../env/.env
        project_root = Path(__file__).parent.parent.parent  # genai-sec-agents/
        env_path = project_root.parent.parent / 'env' / '.env'  # ../../env/.env
        
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        # Remove quotes if present
                        value = value.strip("'\"")
                        os.environ[key] = value
            print(f"Loaded environment variables from {env_path}")
        else:
            print(f"Warning: Environment file not found at {env_path}")
    
    def _create_asvs_prompt_template(self) -> str:
        """Create the prompt template for ASVS Rule Card generation."""
        return """You are a security expert creating Rule Cards from OWASP ASVS (Application Security Verification Standard) requirements.

Convert the following ASVS verification requirements into actionable Rule Cards following this YAML format:

```yaml
id: ASVS-V##-###
title: "Brief, actionable title"
severity: high/medium/low
scope: web-application/api/mobile/infrastructure
requirement: "Clear requirement description"
do:
  - "Specific action to implement"
  - "Another specific action"
dont:
  - "What to avoid"
  - "Anti-pattern to prevent"
detect:
  semgrep:
    - "relevant-semgrep-rule"
  trufflehog:
    - "Relevant TruffleHog detector"
verify:
  tests:
    - "How to test this requirement"
    - "Verification method"
refs:
  cwe:
    - "CWE-XXX"
  asvs:
    - "{asvs_id}"
  owasp:
    - "A0X:2021"
```

IMPORTANT GUIDELINES:
1. Create one Rule Card per ASVS requirement
2. Make titles actionable and specific
3. Set severity based on ASVS level: Level 3 = high, Level 2 = medium, Level 1 = low
4. Use precise "do" and "dont" items that developers can implement
5. Include relevant scanner rules in "detect" section
6. Always include the ASVS requirement ID in refs.asvs
7. Map to relevant CWEs and OWASP Top 10 when applicable

ASVS Requirements to convert:

{requirements_text}

Generate Rule Cards in valid YAML format. Separate multiple Rule Cards with "---".
"""
    
    def _format_asvs_requirements(self, requirements: List[ASVSVerificationRequirement]) -> str:
        """Format ASVS requirements for LLM processing."""
        formatted_parts = []
        
        for req in requirements:
            req_text = f"""
ASVS {req.id} (Level {req.level}):
Section: {req.section} - {req.category}
Description: {req.description}
"""
            formatted_parts.append(req_text.strip())
        
        return "\n\n".join(formatted_parts)
    
    def _call_openai_api(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI API with error handling and rate limiting."""
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return {
                'success': True,
                'content': response.choices[0].message.content,
                'tokens_used': response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'tokens_used': 0
            }
    
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
                if doc.endswith('```'):
                    doc = doc[:-3]
                
                doc = doc.strip()
                if not doc:
                    continue
                
                try:
                    rule_card = yaml.safe_load(doc)
                    if rule_card and isinstance(rule_card, dict):
                        rule_cards.append(rule_card)
                except yaml.YAMLError as e:
                    logger.warning(f"Failed to parse YAML rule card: {e}")
                    logger.debug(f"Problematic YAML content: {doc[:200]}...")
                    continue
        
        except Exception as e:
            logger.error(f"Failed to parse rule cards from response: {e}")
        
        return rule_cards
    
    def generate_rule_cards_from_asvs_section(self, asvs_section: ASVSSection, max_requirements_per_batch: int = 5) -> ASVSRuleCardResult:
        """Generate Rule Cards from a complete ASVS section."""
        logger.info(f"Generating Rule Cards for ASVS section: {asvs_section.title}")
        
        all_rule_cards = []
        total_tokens = 0
        requirements = asvs_section.requirements
        
        # Process requirements in batches to avoid token limits
        for i in range(0, len(requirements), max_requirements_per_batch):
            batch = requirements[i:i + max_requirements_per_batch]
            batch_id = f"{asvs_section.id}-batch-{i//max_requirements_per_batch + 1}"
            
            logger.info(f"Processing batch {batch_id}: {len(batch)} requirements")
            
            # Format requirements for this batch
            requirements_text = self._format_asvs_requirements(batch)
            
            # Create prompt
            prompt = self.asvs_prompt_template.format(
                requirements_text=requirements_text,
                asvs_id=asvs_section.id
            )
            
            # Call OpenAI API
            api_result = self._call_openai_api(prompt)
            total_tokens += api_result.get('tokens_used', 0)
            
            if not api_result['success']:
                logger.error(f"Failed to generate Rule Cards for batch {batch_id}: {api_result.get('error')}")
                continue
            
            # Parse Rule Cards from response
            batch_rule_cards = self._parse_yaml_rule_cards(api_result['content'])
            
            if batch_rule_cards:
                all_rule_cards.extend(batch_rule_cards)
                logger.info(f"Generated {len(batch_rule_cards)} Rule Cards from batch {batch_id}")
            else:
                logger.warning(f"No valid Rule Cards generated from batch {batch_id}")
            
            # Rate limiting
            time.sleep(self.rate_limit_delay)
        
        # Create result
        success = len(all_rule_cards) > 0
        
        if success:
            logger.info(f"Successfully generated {len(all_rule_cards)} Rule Cards from {len(requirements)} ASVS requirements")
        else:
            logger.error(f"Failed to generate any Rule Cards from ASVS section {asvs_section.title}")
        
        return ASVSRuleCardResult(
            asvs_id=asvs_section.id,
            success=success,
            rule_cards=all_rule_cards,
            tokens_used=total_tokens
        )
    
    def save_rule_cards_to_files(self, result: ASVSRuleCardResult, output_dir: str = "app/rule_cards/asvs") -> bool:
        """Save generated Rule Cards to YAML files."""
        try:
            # Create output directory structure
            section_dir = Path(output_dir) / result.asvs_id.lower().replace('-', '_')
            section_dir.mkdir(parents=True, exist_ok=True)
            
            saved_files = []
            
            for i, rule_card in enumerate(result.rule_cards):
                # Generate filename from rule card ID or use index
                rule_id = rule_card.get('id', f"{result.asvs_id}-RULE-{i+1:03d}")
                filename = f"{rule_id}.yml"
                file_path = section_dir / filename
                
                # Save Rule Card as YAML
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(rule_card, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
                
                saved_files.append(str(file_path))
            
            logger.info(f"Saved {len(saved_files)} Rule Cards to {section_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save Rule Cards: {e}")
            return False
    
    def generate_bulk_asvs_rule_cards(self, priority_levels: List[int] = [1, 2]) -> Dict[str, ASVSRuleCardResult]:
        """Generate Rule Cards from multiple ASVS sections."""
        logger.info(f"Starting bulk ASVS Rule Card generation for levels {priority_levels}")
        
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
            logger.info(f"Processing ASVS section: {section.title} ({len(section.requirements)} requirements)")
            
            # Generate Rule Cards for this section
            result = self.generate_rule_cards_from_asvs_section(section)
            results[section.id] = result
            
            total_tokens += result.tokens_used
            
            # Save Rule Cards to files
            if result.success:
                self.save_rule_cards_to_files(result)
            
            # Rate limiting between sections
            time.sleep(self.rate_limit_delay)
        
        # Log summary
        successful_sections = sum(1 for r in results.values() if r.success)
        total_rule_cards = sum(len(r.rule_cards) for r in results.values())
        
        logger.info(f"Bulk generation complete:")
        logger.info(f"  Sections processed: {len(results)}")
        logger.info(f"  Successful sections: {successful_sections}")
        logger.info(f"  Total Rule Cards: {total_rule_cards}")
        logger.info(f"  Total tokens used: {total_tokens}")
        logger.info(f"  Estimated cost (GPT-3.5-turbo): ${total_tokens * 0.0015 / 1000:.3f}")
        
        return results


def main():
    """Test ASVS Rule Card generation."""
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Initialize generator
        generator = ASVSRuleCardGenerator()
        
        # Test with a single section (Cryptography)
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
        
        print(f"📋 Testing with {len(section.requirements)} ASVS requirements")
        
        # Generate Rule Cards
        result = generator.generate_rule_cards_from_asvs_section(section, max_requirements_per_batch=3)
        
        if result.success:
            print(f"✅ Successfully generated {len(result.rule_cards)} Rule Cards")
            print(f"   Tokens used: {result.tokens_used}")
            print(f"   Estimated cost: ${result.tokens_used * 0.0015 / 1000:.3f}")
            
            # Save to files
            generator.save_rule_cards_to_files(result)
            
            # Show sample Rule Card
            if result.rule_cards:
                print(f"\n📄 Sample Rule Card:")
                sample_card = result.rule_cards[0]
                print(f"   ID: {sample_card.get('id', 'N/A')}")
                print(f"   Title: {sample_card.get('title', 'N/A')}")
                print(f"   Severity: {sample_card.get('severity', 'N/A')}")
        else:
            print(f"❌ Failed to generate Rule Cards: {result.error_message}")
    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()