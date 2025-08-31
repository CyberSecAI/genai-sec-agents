#!/usr/bin/env python3
"""
Scanner Integration Mapper

Maps generated OWASP Rule Cards to existing security scanner rules (Semgrep, TruffleHog, etc.)
and creates custom detection patterns when no existing rules are available.
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ScannerRule:
    """Represents a security scanner rule mapping"""
    scanner_type: str
    rule_id: str
    rule_name: str
    description: Optional[str] = None
    severity: Optional[str] = None
    confidence: str = "high"


@dataclass
class MappingResult:
    """Result of scanner rule mapping for a Rule Card"""
    rule_card_id: str
    success: bool
    mapped_scanners: List[ScannerRule]
    custom_rules_created: List[str]
    error_message: Optional[str] = None


class SecurityScannerMapper:
    """
    Maps OWASP Rule Cards to security scanner rules for automated detection.
    
    Supports mapping to:
    - Semgrep rules for static analysis
    - TruffleHog for secret detection
    - Custom detection patterns
    """
    
    def __init__(self):
        """Initialize the scanner mapper with rule databases"""
        self.semgrep_rules_db = self._load_semgrep_rules_database()
        self.trufflehog_rules_db = self._load_trufflehog_rules_database()
        self.custom_patterns = {}
        
    def _load_semgrep_rules_database(self) -> Dict[str, List[str]]:
        """Load Semgrep rules database for mapping"""
        return {
            # Input validation rules
            'input-validation': [
                'python.django.security.audit.avoid-unsafe-deserialization',
                'python.flask.security.audit.direct-use-of-jinja2',
                'java.spring.security.audit.spring-unvalidated-redirect',
                'javascript.express.security.audit.express-unvalidated-redirect',
                'python.sqlalchemy.security.audit.sqlalchemy-execute-raw-query'
            ],
            
            # SQL injection prevention
            'sql-injection': [
                'python.django.security.injection.sql.django-sql-injection',
                'python.sqlalchemy.security.audit.sqlalchemy-execute-raw-query',
                'java.spring.security.audit.spring-sqli',
                'javascript.sequelize.security.audit.sequelize-injection',
                'php.lang.security.injection.sql-injection'
            ],
            
            # XSS prevention
            'xss-prevention': [
                'python.django.security.audit.xss.direct-use-of-httpresp-write',
                'javascript.browser.security.audit.dom-based-xss',
                'java.spring.security.audit.spring-xss',
                'php.lang.security.xss.reflected-xss',
                'python.flask.security.audit.direct-use-of-jinja2'
            ],
            
            # Authentication and session management
            'authentication': [
                'python.django.security.audit.session-cookie-secure-false',
                'python.django.security.audit.session-cookie-httponly-false',
                'java.spring.security.audit.spring-csrf-disabled',
                'javascript.express.security.audit.express-session-no-secret'
            ],
            
            # File upload security
            'file-upload': [
                'python.django.security.audit.unescaped-file-extension',
                'java.spring.security.audit.spring-file-upload-filename',
                'php.lang.security.file-inclusion.file-inclusion',
                'javascript.express.security.audit.express-file-upload'
            ],
            
            # Logging and error handling
            'logging': [
                'python.logging.security.audit.logging-sensitive-data',
                'java.lang.security.audit.system-exit',
                'javascript.express.security.audit.express-expose-sensitive-data'
            ],
            
            # HTTP headers security
            'http-headers': [
                'python.django.security.audit.xss-filter-disabled',
                'python.flask.security.audit.flask-cors-origin-wildcard',
                'java.spring.security.audit.spring-security-headers'
            ],
            
            # Language-specific rules
            'java-security': [
                'java.lang.security.audit.crypto.weak-hash',
                'java.lang.security.audit.crypto.insecure-random',
                'java.spring.security.audit.spring-security-disabled'
            ],
            
            'nodejs-security': [
                'javascript.express.security.audit.express-cors-origin-wildcard',
                'javascript.lang.security.audit.crypto-js-hardcoded-secret',
                'javascript.express.security.audit.express-helmet-disabled'
            ]
        }
    
    def _load_trufflehog_rules_database(self) -> Dict[str, List[str]]:
        """Load TruffleHog detector database for secret detection"""
        return {
            'authentication': [
                'Generic API Key',
                'JWT Token',
                'Private Key',
                'Basic Auth'
            ],
            'api-security': [
                'AWS Access Key',
                'GitHub Token',
                'Slack Token',
                'Google API Key'
            ],
            'database-security': [
                'Connection String',
                'Database Password',
                'MongoDB URI'
            ]
        }
    
    def map_rule_card_to_scanners(self, rule_card_path: Path) -> MappingResult:
        """
        Map a single Rule Card to appropriate scanner rules
        
        Args:
            rule_card_path: Path to the Rule Card YAML file
            
        Returns:
            MappingResult with scanner mappings
        """
        try:
            # Load rule card
            with open(rule_card_path, 'r') as f:
                rule_card = yaml.safe_load(f)
            
            rule_id = rule_card.get('id', 'unknown')
            logger.info(f"Mapping scanner rules for: {rule_id}")
            
            # Extract current detect section if exists
            current_detect = rule_card.get('detect', {})
            
            # Map to scanner rules
            mapped_scanners = []
            custom_rules = []
            
            # Map based on rule category and content
            category = self._categorize_rule_card(rule_card)
            
            # Map to Semgrep rules
            semgrep_rules = self._map_to_semgrep(rule_card, category)
            for rule in semgrep_rules:
                mapped_scanners.append(ScannerRule(
                    scanner_type="semgrep",
                    rule_id=rule,
                    rule_name=rule,
                    description=f"Semgrep rule for {rule_id}"
                ))
            
            # Map to TruffleHog rules  
            trufflehog_rules = self._map_to_trufflehog(rule_card, category)
            for rule in trufflehog_rules:
                mapped_scanners.append(ScannerRule(
                    scanner_type="trufflehog",
                    rule_id=rule,
                    rule_name=rule,
                    description=f"TruffleHog detector for {rule_id}"
                ))
            
            # Create custom rules if needed
            if not mapped_scanners:
                custom_rule = self._create_custom_detection_pattern(rule_card)
                if custom_rule:
                    custom_rules.append(custom_rule)
                    mapped_scanners.append(ScannerRule(
                        scanner_type="custom",
                        rule_id=custom_rule,
                        rule_name=f"Custom detection for {rule_id}",
                        description=f"Custom pattern for {rule_card.get('title', 'security requirement')}"
                    ))
            
            # Update the rule card with enhanced detect section
            self._update_rule_card_detect_section(rule_card, mapped_scanners, rule_card_path)
            
            return MappingResult(
                rule_card_id=rule_id,
                success=True,
                mapped_scanners=mapped_scanners,
                custom_rules_created=custom_rules
            )
            
        except Exception as e:
            logger.error(f"Failed to map {rule_card_path}: {e}")
            return MappingResult(
                rule_card_id=str(rule_card_path),
                success=False,
                mapped_scanners=[],
                custom_rules_created=[],
                error_message=str(e)
            )
    
    def _categorize_rule_card(self, rule_card: Dict) -> str:
        """Categorize rule card based on content for mapping"""
        rule_id = rule_card.get('id', '').lower()
        title = rule_card.get('title', '').lower()
        requirement = rule_card.get('requirement', '').lower()
        
        # Analyze content to determine category
        if any(keyword in rule_id + title + requirement for keyword in 
               ['input', 'validation', 'sanitiz', 'filter']):
            return 'input-validation'
        elif any(keyword in rule_id + title + requirement for keyword in 
                 ['sql', 'injection', 'query', 'database']):
            return 'sql-injection'
        elif any(keyword in rule_id + title + requirement for keyword in 
                 ['xss', 'script', 'cross-site', 'encoding']):
            return 'xss-prevention'
        elif any(keyword in rule_id + title + requirement for keyword in 
                 ['auth', 'login', 'password', 'credential', 'session']):
            return 'authentication'
        elif any(keyword in rule_id + title + requirement for keyword in 
                 ['file', 'upload', 'path', 'directory']):
            return 'file-upload'
        elif any(keyword in rule_id + title + requirement for keyword in 
                 ['log', 'error', 'exception', 'debug']):
            return 'logging'
        elif any(keyword in rule_id + title + requirement for keyword in 
                 ['header', 'http', 'cors', 'csp', 'frame']):
            return 'http-headers'
        elif any(keyword in rule_id + title + requirement for keyword in 
                 ['java', 'spring', 'servlet']):
            return 'java-security'
        elif any(keyword in rule_id + title + requirement for keyword in 
                 ['node', 'javascript', 'express', 'npm']):
            return 'nodejs-security'
        else:
            return 'generic'
    
    def _map_to_semgrep(self, rule_card: Dict, category: str) -> List[str]:
        """Map rule card to relevant Semgrep rules"""
        semgrep_rules = self.semgrep_rules_db.get(category, [])
        
        # Filter based on scope and language if specified
        scope = rule_card.get('scope', '')
        filtered_rules = []
        
        for rule in semgrep_rules:
            # Basic filtering based on rule content and scope
            if scope == 'web-application' and any(web_tech in rule for web_tech in 
                                                ['django', 'flask', 'express', 'spring']):
                filtered_rules.append(rule)
            elif scope == 'api' and any(api_tech in rule for api_tech in 
                                       ['api', 'rest', 'graphql']):
                filtered_rules.append(rule)
            else:
                filtered_rules.append(rule)
        
        return filtered_rules[:3]  # Limit to top 3 most relevant rules
    
    def _map_to_trufflehog(self, rule_card: Dict, category: str) -> List[str]:
        """Map rule card to relevant TruffleHog detectors"""
        trufflehog_rules = self.trufflehog_rules_db.get(category, [])
        
        # Filter based on rule content
        requirement = rule_card.get('requirement', '').lower()
        filtered_rules = []
        
        for rule in trufflehog_rules:
            rule_lower = rule.lower()
            if any(keyword in requirement for keyword in 
                   rule_lower.split()):
                filtered_rules.append(rule)
        
        return filtered_rules[:2]  # Limit to top 2 most relevant detectors
    
    def _create_custom_detection_pattern(self, rule_card: Dict) -> Optional[str]:
        """Create custom detection pattern when no existing rules match"""
        rule_id = rule_card.get('id', '')
        title = rule_card.get('title', '')
        
        # Create custom pattern based on rule content
        pattern_name = f"custom-{rule_id.lower()}"
        
        # Store pattern for potential future use
        self.custom_patterns[pattern_name] = {
            'title': title,
            'pattern': f"Check for {title.lower()} violations",
            'description': f"Custom detection pattern for {rule_id}"
        }
        
        return pattern_name
    
    def _update_rule_card_detect_section(self, rule_card: Dict, mapped_scanners: List[ScannerRule], rule_card_path: Path):
        """Update the Rule Card detect section with mapped scanner rules"""
        detect_section = rule_card.get('detect', {})
        
        # Group scanners by type
        for scanner in mapped_scanners:
            if scanner.scanner_type not in detect_section:
                detect_section[scanner.scanner_type] = []
            
            # Add rule if not already present
            if scanner.rule_id not in detect_section[scanner.scanner_type]:
                detect_section[scanner.scanner_type].append(scanner.rule_id)
        
        # Update rule card
        rule_card['detect'] = detect_section
        
        # Save updated rule card
        with open(rule_card_path, 'w') as f:
            yaml.dump(rule_card, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Updated detect section for {rule_card.get('id', 'unknown')}")
    
    def process_all_rule_cards(self, rule_cards_dir: str = "app/rule_cards/owasp") -> Dict[str, MappingResult]:
        """
        Process all OWASP Rule Cards and map them to scanner rules
        
        Args:
            rule_cards_dir: Directory containing Rule Card YAML files
            
        Returns:
            Dictionary mapping file paths to mapping results
        """
        rule_cards_path = Path(rule_cards_dir)
        if not rule_cards_path.exists():
            logger.error(f"Rule cards directory not found: {rule_cards_dir}")
            return {}
        
        # Find all rule card files
        rule_card_files = list(rule_cards_path.rglob("*.yml"))
        
        logger.info(f"Processing {len(rule_card_files)} Rule Card files for scanner mapping")
        print("=" * 80)
        
        results = {}
        successful_mappings = 0
        total_scanners_mapped = 0
        
        for rule_card_file in rule_card_files:
            print(f"\nMapping: {rule_card_file.relative_to(rule_cards_path)}")
            print("-" * 40)
            
            result = self.map_rule_card_to_scanners(rule_card_file)
            results[str(rule_card_file)] = result
            
            if result.success:
                print(f"✓ Mapped to {len(result.mapped_scanners)} scanner rules")
                for scanner in result.mapped_scanners:
                    print(f"  - {scanner.scanner_type}: {scanner.rule_id}")
                
                if result.custom_rules_created:
                    print(f"  + Created {len(result.custom_rules_created)} custom patterns")
                
                successful_mappings += 1
                total_scanners_mapped += len(result.mapped_scanners)
            else:
                print(f"✗ Mapping failed: {result.error_message}")
        
        print("\n" + "=" * 80)
        print("Scanner mapping complete!")
        print(f"  Successful mappings: {successful_mappings}/{len(rule_card_files)}")
        print(f"  Total scanner rules mapped: {total_scanners_mapped}")
        print(f"  Custom patterns created: {len(self.custom_patterns)}")
        
        return results
    
    def generate_scanner_integration_report(self, results: Dict[str, MappingResult]) -> str:
        """Generate a report of scanner integration results"""
        report_lines = [
            "# Scanner Integration Report",
            f"Generated on: {os.popen('date').read().strip()}",
            "",
            "## Summary",
            f"- Total Rule Cards processed: {len(results)}",
            f"- Successful mappings: {sum(1 for r in results.values() if r.success)}",
            f"- Failed mappings: {sum(1 for r in results.values() if not r.success)}",
            "",
            "## Scanner Coverage",
        ]
        
        # Count scanner types
        scanner_counts = {}
        for result in results.values():
            if result.success:
                for scanner in result.mapped_scanners:
                    scanner_counts[scanner.scanner_type] = scanner_counts.get(scanner.scanner_type, 0) + 1
        
        for scanner_type, count in scanner_counts.items():
            report_lines.append(f"- {scanner_type}: {count} rules mapped")
        
        report_lines.extend([
            "",
            "## Detailed Results",
        ])
        
        for file_path, result in results.items():
            if result.success:
                report_lines.append(f"### {result.rule_card_id}")
                for scanner in result.mapped_scanners:
                    report_lines.append(f"- {scanner.scanner_type}: {scanner.rule_id}")
        
        return "\n".join(report_lines)


def main():
    """CLI interface for scanner rule mapping"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Map OWASP Rule Cards to security scanner rules")
    parser.add_argument("--rule-cards-dir", default="app/rule_cards/owasp",
                        help="Directory containing Rule Card YAML files")
    parser.add_argument("--report", action="store_true",
                        help="Generate scanner integration report")
    
    args = parser.parse_args()
    
    try:
        mapper = SecurityScannerMapper()
        results = mapper.process_all_rule_cards(args.rule_cards_dir)
        
        if args.report:
            report = mapper.generate_scanner_integration_report(results)
            report_file = Path("scanner_integration_report.md")
            with open(report_file, 'w') as f:
                f.write(report)
            print(f"\n📊 Scanner integration report saved: {report_file}")
        
        # Print summary
        successful = sum(1 for r in results.values() if r.success)
        total_mappings = sum(len(r.mapped_scanners) for r in results.values() if r.success)
        
        print(f"\n🎉 Scanner Mapping Summary:")
        print(f"   Processed: {len(results)} Rule Cards")
        print(f"   Successfully mapped: {successful}")
        print(f"   Total scanner rules mapped: {total_mappings}")
        
        return 0 if successful > 0 else 1
        
    except Exception as e:
        logger.error(f"Scanner mapping failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())