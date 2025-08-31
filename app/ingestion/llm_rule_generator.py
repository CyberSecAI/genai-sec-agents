#!/usr/bin/env python3
"""
LLM-based OWASP Rule Card Generator

Uses ChatGPT to convert OWASP cheat sheet content into Rule Card YAML format.
This approach leverages LLM understanding instead of complex parsing logic.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import requests
from datetime import datetime

from .owasp_fetcher import OWASPFetcher


@dataclass
class GenerationResult:
    """Result of LLM rule card generation"""
    success: bool
    rule_cards: List[str]  # YAML content strings
    error_message: Optional[str] = None
    tokens_used: Optional[int] = None
    processing_time: Optional[float] = None


class LLMRuleCardGenerator:
    """Generate Rule Cards from OWASP content using ChatGPT"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize LLM generator
        
        Args:
            api_key: OpenAI API key (will use OPENAI_API_KEY env var if not provided)
            model: OpenAI model to use (gpt-4, gpt-3.5-turbo, etc.)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key required - set OPENAI_API_KEY environment variable")
        
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Load example Rule Card for prompt
        self.example_rule_card = self._load_example_rule_card()
    
    def _load_example_rule_card(self) -> str:
        """Load an example Rule Card to show ChatGPT the desired format"""
        example_path = Path("app/rule_cards/secrets/SECRETS-API-001.yml")
        
        if example_path.exists():
            with open(example_path, 'r') as f:
                return f.read()
        
        # Fallback example if file doesn't exist
        return """id: SECRETS-API-001
title: "API Keys must not be hardcoded in source code"
severity: critical
scope: application
requirement: "API keys, tokens, and authentication secrets must never be embedded directly in source code, configuration files committed to version control, or any location where they can be discovered through static analysis."
do:
  - "Store API keys in environment variables or secure key management systems"
  - "Use runtime configuration to inject secrets into applications"
  - "Implement proper secret rotation and monitoring"
  - "Use least-privilege access principles for API key permissions"
dont:
  - "Embed API keys directly in source code or configuration files"
  - "Commit secrets to version control systems"
  - "Share API keys through insecure channels (email, chat, etc.)"
  - "Use the same API key across multiple environments (dev, staging, prod)"
detect:
  semgrep:
    - "secrets.api-keys.hardcoded-secret"
    - "generic.secrets.security.detected-generic-secret"
  trufflehog:
    - "Generic API Key"
  custom:
    - "Search for common API key patterns in code"
verify:
  tests:
    - "Scan codebase with secret detection tools"
    - "Verify no secrets in git history"
    - "Test secret rotation procedures"
refs:
  cwe:
    - "CWE-798"
  asvs:
    - "V2.10.4"
  owasp:
    - "A07:2021-Identification and Authentication Failures"
  nist:
    - "IA-5"""
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for ChatGPT"""
        return f"""You are an expert cybersecurity analyst specializing in converting OWASP security guidance into structured Rule Cards for automated security analysis.

Your task is to analyze OWASP cheat sheet content and generate Rule Cards in YAML format. Each Rule Card should capture specific, actionable security requirements that can be validated by security tools.

Here's an example of the exact YAML format you must follow:

{self.example_rule_card}

IMPORTANT GUIDELINES:
1. Generate multiple Rule Cards from a single cheat sheet (typically 3-8 cards)
2. Each Rule Card must have a unique ID following the pattern: DOMAIN-TOPIC-###
3. Focus on actionable requirements that can be validated or tested
4. Include specific "do" and "dont" guidance
5. Map to appropriate scanner tools (semgrep, trufflehog, custom)
6. Include relevant CWE, ASVS, OWASP, and NIST references
7. Use appropriate severity levels: critical, high, medium, low
8. Scope should reflect the application type (web-application, api, mobile, etc.)

Output format: Return only valid YAML content with multiple Rule Cards separated by "---" (YAML document separator).

Example output structure:
```yaml
id: INPUT-VALIDATION-001
title: "Validate all user input against allowlists"
# ... rest of rule card ...
---
id: INPUT-VALIDATION-002  
title: "Sanitize user input to prevent injection attacks"
# ... rest of rule card ...
---
# Additional rule cards as needed
```"""

    def _create_user_prompt(self, cheat_sheet_content: str, cheat_sheet_name: str) -> str:
        """Create the user prompt with cheat sheet content"""
        return f"""Please analyze the following OWASP cheat sheet and generate appropriate Rule Cards:

CHEAT SHEET: {cheat_sheet_name}

CONTENT:
{cheat_sheet_content}

Generate 3-8 Rule Cards that capture the most important actionable security requirements from this cheat sheet. Focus on requirements that can be validated through code analysis, testing, or configuration checks."""

    def generate_rule_cards(self, cheat_sheet_content: str, cheat_sheet_name: str) -> GenerationResult:
        """
        Generate Rule Cards from OWASP cheat sheet content using ChatGPT
        
        Args:
            cheat_sheet_content: Raw markdown content from OWASP cheat sheet
            cheat_sheet_name: Name of the cheat sheet for context
            
        Returns:
            GenerationResult with success status and generated rule cards
        """
        start_time = time.time()
        
        try:
            # Prepare the request
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": self._create_system_prompt()
                    },
                    {
                        "role": "user", 
                        "content": self._create_user_prompt(cheat_sheet_content, cheat_sheet_name)
                    }
                ],
                "max_tokens": 4000,
                "temperature": 0.1,  # Low temperature for consistent output
                "top_p": 0.9
            }
            
            # Make the API call
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            content = data['choices'][0]['message']['content']
            tokens_used = data.get('usage', {}).get('total_tokens', 0)
            processing_time = time.time() - start_time
            
            # Split the response into individual rule cards
            rule_cards = self._parse_rule_cards(content)
            
            return GenerationResult(
                success=True,
                rule_cards=rule_cards,
                tokens_used=tokens_used,
                processing_time=processing_time
            )
            
        except requests.exceptions.RequestException as e:
            return GenerationResult(
                success=False,
                rule_cards=[],
                error_message=f"API request failed: {str(e)}",
                processing_time=time.time() - start_time
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                rule_cards=[],
                error_message=f"Generation failed: {str(e)}",
                processing_time=time.time() - start_time
            )
    
    def _parse_rule_cards(self, content: str) -> List[str]:
        """Parse the LLM response into individual rule card YAML strings"""
        # Remove code block markers if present
        content = content.strip()
        if content.startswith('```yaml'):
            content = content[7:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        
        # Split on YAML document separator
        rule_cards = content.split('---')
        
        # Clean up each rule card
        cleaned_cards = []
        for card in rule_cards:
            card = card.strip()
            if card and 'id:' in card:  # Basic validation
                cleaned_cards.append(card)
        
        return cleaned_cards
    
    def process_all_cheat_sheets(self, output_dir: str = "app/rule_cards/owasp") -> Dict[str, GenerationResult]:
        """
        Process all OWASP cheat sheets and generate rule cards
        
        Args:
            output_dir: Directory to save generated rule cards
            
        Returns:
            Dictionary mapping cheat sheet names to generation results
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Fetch all cheat sheets
        fetcher = OWASPFetcher()
        cheat_sheets = fetcher.fetch_secure_coding_cheatsheets()
        
        results = {}
        total_tokens = 0
        successful_generations = 0
        
        print(f"Processing {len(cheat_sheets)} OWASP cheat sheets...")
        print("=" * 80)
        
        for sheet_id, content in cheat_sheets.items():
            print(f"\nProcessing: {sheet_id}")
            print("-" * 40)
            
            # Generate rule cards using LLM
            result = self.generate_rule_cards(content, sheet_id)
            results[sheet_id] = result
            
            if result.success:
                print(f"✓ Generated {len(result.rule_cards)} rule cards")
                print(f"  Tokens used: {result.tokens_used}")
                print(f"  Processing time: {result.processing_time:.2f}s")
                
                # Save rule cards to files
                sheet_dir = output_path / sheet_id.replace('-', '_')
                sheet_dir.mkdir(exist_ok=True)
                
                for i, rule_card in enumerate(result.rule_cards, 1):
                    # Extract rule ID for filename
                    rule_id = self._extract_rule_id(rule_card)
                    if rule_id:
                        filename = f"{rule_id}.yml"
                    else:
                        filename = f"{sheet_id}_{i:03d}.yml"
                    
                    rule_file = sheet_dir / filename
                    with open(rule_file, 'w') as f:
                        f.write(rule_card)
                    
                    print(f"    Saved: {rule_file}")
                
                successful_generations += 1
                total_tokens += result.tokens_used or 0
                
                # Rate limiting - be respectful to OpenAI API
                time.sleep(2)
                
            else:
                print(f"✗ Generation failed: {result.error_message}")
        
        print("\n" + "=" * 80)
        print(f"Processing complete!")
        print(f"  Successful: {successful_generations}/{len(cheat_sheets)}")
        print(f"  Total tokens used: {total_tokens:,}")
        print(f"  Output directory: {output_path}")
        
        return results
    
    def _extract_rule_id(self, rule_card_yaml: str) -> Optional[str]:
        """Extract the rule ID from YAML content for filename"""
        lines = rule_card_yaml.split('\n')
        for line in lines:
            if line.startswith('id:'):
                return line.split(':', 1)[1].strip().strip('"\'')
        return None


def main():
    """CLI interface for LLM rule card generation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Rule Cards from OWASP cheat sheets using ChatGPT")
    parser.add_argument("--output-dir", default="app/rule_cards/owasp", 
                        help="Output directory for generated rule cards")
    parser.add_argument("--model", default="gpt-4", 
                        help="OpenAI model to use (gpt-4, gpt-3.5-turbo, etc.)")
    parser.add_argument("--api-key", help="OpenAI API key (or use OPENAI_API_KEY env var)")
    
    args = parser.parse_args()
    
    try:
        generator = LLMRuleCardGenerator(api_key=args.api_key, model=args.model)
        results = generator.process_all_cheat_sheets(output_dir=args.output_dir)
        
        # Print summary
        successful = sum(1 for r in results.values() if r.success)
        total_cards = sum(len(r.rule_cards) for r in results.values() if r.success)
        
        print(f"\n🎉 Generation Summary:")
        print(f"   Processed: {len(results)} cheat sheets")
        print(f"   Successful: {successful}")
        print(f"   Rule cards generated: {total_cards}")
        print(f"   Output: {args.output_dir}")
        
        return 0 if successful > 0 else 1
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())