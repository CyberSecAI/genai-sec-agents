#!/usr/bin/env python3
"""
Quality Validator for OWASP Rule Cards

Comprehensive quality assurance and validation system for generated Rule Cards,
ensuring they meet schema requirements, content quality standards, and integration compatibility.

Task 6: Quality Assurance and Validation for Story 2.5
"""

import os
import sys
import json
import yaml
import logging
import re
import glob
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validation levels for different types of checks."""
    SCHEMA = "schema"
    CONTENT = "content"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    ERROR = "error"
    WARNING = "warning" 
    INFO = "info"


@dataclass
class ValidationIssue:
    """Represents a validation issue found during quality checks."""
    level: ValidationLevel
    severity: ValidationSeverity
    rule_id: str
    field: str
    message: str
    suggestion: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level.value,
            "severity": self.severity.value,
            "rule_id": self.rule_id,
            "field": self.field,
            "message": self.message,
            "suggestion": self.suggestion
        }


@dataclass
class ValidationReport:
    """Comprehensive validation report for Rule Cards."""
    total_rules: int
    valid_rules: int
    invalid_rules: int
    issues: List[ValidationIssue]
    quality_score: float
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": {
                "total_rules": self.total_rules,
                "valid_rules": self.valid_rules,
                "invalid_rules": self.invalid_rules,
                "quality_score": self.quality_score,
                "success_rate": (self.valid_rules / max(self.total_rules, 1)) * 100
            },
            "issues": [issue.to_dict() for issue in self.issues],
            "issues_by_severity": {
                "errors": len([i for i in self.issues if i.severity == ValidationSeverity.ERROR]),
                "warnings": len([i for i in self.issues if i.severity == ValidationSeverity.WARNING]),
                "info": len([i for i in self.issues if i.severity == ValidationSeverity.INFO])
            },
            "recommendations": self.recommendations
        }


class RuleCardSchema:
    """Defines the schema and validation rules for Rule Cards."""
    
    REQUIRED_FIELDS = {
        'id': str,
        'title': str,
        'severity': str,
        'scope': str,
        'requirement': str
    }
    
    OPTIONAL_FIELDS = {
        'do': list,
        'dont': list,
        'detect': dict,
        'verify': dict,
        'refs': dict
    }
    
    VALID_SEVERITIES = {'low', 'medium', 'high', 'critical'}
    VALID_SCOPES = {
        'web-application', 'api', 'mobile', 'infrastructure', 
        'database', 'network', 'cloud', 'container'
    }
    
    # Scanner tools that should be present in detect section
    SCANNER_TOOLS = {'semgrep', 'trufflehog', 'codeql', 'custom'}
    
    # Reference categories
    REFERENCE_CATEGORIES = {'cwe', 'asvs', 'owasp', 'standards', 'nist'}


class QualityValidator:
    """Comprehensive quality validator for OWASP Rule Cards."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the quality validator."""
        self.config = self._load_config(config_path)
        self.schema = RuleCardSchema()
        self.issues = []
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load validation configuration."""
        default_config = {
            "validation": {
                "schema_strict": True,
                "content_min_length": {
                    "title": 10,
                    "requirement": 20,
                    "do_items": 5,
                    "dont_items": 5
                },
                "content_max_length": {
                    "title": 200,
                    "requirement": 1000
                },
                "required_list_items": {
                    "do": 2,
                    "dont": 1
                },
                "scanner_integration_required": True,
                "references_required": True,
                "quality_thresholds": {
                    "minimum_score": 0.7,
                    "warning_score": 0.8,
                    "excellent_score": 0.9
                }
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                # Simple merge for now
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load validation config: {e}")
        
        return default_config
    
    def validate_schema(self, rule_card: Dict[str, Any], rule_id: str) -> List[ValidationIssue]:
        """Validate rule card against schema requirements."""
        issues = []
        
        # Check required fields
        for field, expected_type in self.schema.REQUIRED_FIELDS.items():
            if field not in rule_card:
                issues.append(ValidationIssue(
                    ValidationLevel.SCHEMA, ValidationSeverity.ERROR,
                    rule_id, field, f"Missing required field: {field}",
                    f"Add {field} field with {expected_type.__name__} value"
                ))
            elif not isinstance(rule_card[field], expected_type):
                issues.append(ValidationIssue(
                    ValidationLevel.SCHEMA, ValidationSeverity.ERROR,
                    rule_id, field, f"Field {field} has incorrect type: expected {expected_type.__name__}, got {type(rule_card[field]).__name__}",
                    f"Convert {field} to {expected_type.__name__}"
                ))
            elif not rule_card[field]:  # Empty values
                issues.append(ValidationIssue(
                    ValidationLevel.SCHEMA, ValidationSeverity.ERROR,
                    rule_id, field, f"Required field {field} is empty",
                    f"Provide a meaningful value for {field}"
                ))
        
        # Validate severity values
        if 'severity' in rule_card:
            severity = rule_card['severity']
            if severity not in self.schema.VALID_SEVERITIES:
                issues.append(ValidationIssue(
                    ValidationLevel.SCHEMA, ValidationSeverity.ERROR,
                    rule_id, 'severity', f"Invalid severity level: {severity}",
                    f"Use one of: {', '.join(self.schema.VALID_SEVERITIES)}"
                ))
        
        # Validate scope values
        if 'scope' in rule_card:
            scope = rule_card['scope']
            if scope not in self.schema.VALID_SCOPES:
                issues.append(ValidationIssue(
                    ValidationLevel.SCHEMA, ValidationSeverity.WARNING,
                    rule_id, 'scope', f"Non-standard scope: {scope}",
                    f"Consider using: {', '.join(self.schema.VALID_SCOPES)}"
                ))
        
        # Validate optional field types
        for field, expected_type in self.schema.OPTIONAL_FIELDS.items():
            if field in rule_card and not isinstance(rule_card[field], expected_type):
                issues.append(ValidationIssue(
                    ValidationLevel.SCHEMA, ValidationSeverity.ERROR,
                    rule_id, field, f"Field {field} has incorrect type: expected {expected_type.__name__}, got {type(rule_card[field]).__name__}",
                    f"Convert {field} to {expected_type.__name__}"
                ))
        
        # Validate list fields have content
        for list_field in ['do', 'dont']:
            if list_field in rule_card:
                if not rule_card[list_field] or len(rule_card[list_field]) == 0:
                    issues.append(ValidationIssue(
                        ValidationLevel.SCHEMA, ValidationSeverity.WARNING,
                        rule_id, list_field, f"Field {list_field} is empty",
                        f"Add at least one item to {list_field} list"
                    ))
        
        return issues
    
    def validate_content_quality(self, rule_card: Dict[str, Any], rule_id: str) -> List[ValidationIssue]:
        """Validate content quality and completeness."""
        issues = []
        config = self.config["validation"]
        
        # Check minimum content lengths
        min_lengths = config.get("content_min_length", {})
        for field, min_length in min_lengths.items():
            if field in rule_card:
                if field.endswith('_items'):  # Handle list items
                    list_field = field.replace('_items', '')
                    if list_field in rule_card and isinstance(rule_card[list_field], list):
                        for item in rule_card[list_field]:
                            if isinstance(item, str) and len(item) < min_length:
                                issues.append(ValidationIssue(
                                    ValidationLevel.CONTENT, ValidationSeverity.WARNING,
                                    rule_id, list_field, f"Item in {list_field} is too short ({len(item)} chars, minimum {min_length})",
                                    f"Expand the item to provide more actionable detail"
                                ))
                else:
                    if isinstance(rule_card[field], str) and len(rule_card[field]) < min_length:
                        issues.append(ValidationIssue(
                            ValidationLevel.CONTENT, ValidationSeverity.WARNING,
                            rule_id, field, f"Field {field} is too short ({len(rule_card[field])} chars, minimum {min_length})",
                            f"Expand {field} to provide more detail"
                        ))
        
        # Check maximum content lengths
        max_lengths = config.get("content_max_length", {})
        for field, max_length in max_lengths.items():
            if field in rule_card and isinstance(rule_card[field], str):
                if len(rule_card[field]) > max_length:
                    issues.append(ValidationIssue(
                        ValidationLevel.CONTENT, ValidationSeverity.WARNING,
                        rule_id, field, f"Field {field} is too long ({len(rule_card[field])} chars, maximum {max_length})",
                        f"Condense {field} to be more concise"
                    ))
        
        # Check required list item counts
        required_items = config.get("required_list_items", {})
        for list_field, min_count in required_items.items():
            if list_field in rule_card and isinstance(rule_card[list_field], list):
                if len(rule_card[list_field]) < min_count:
                    issues.append(ValidationIssue(
                        ValidationLevel.CONTENT, ValidationSeverity.WARNING,
                        rule_id, list_field, f"Field {list_field} has {len(rule_card[list_field])} items, minimum {min_count}",
                        f"Add more items to {list_field} for completeness"
                    ))
        
        # Check for actionable language in 'do' and 'dont' sections
        for action_field in ['do', 'dont']:
            if action_field in rule_card and isinstance(rule_card[action_field], list):
                for i, item in enumerate(rule_card[action_field]):
                    if isinstance(item, str):
                        # Check for imperative verbs
                        if not self._has_imperative_language(item):
                            issues.append(ValidationIssue(
                                ValidationLevel.CONTENT, ValidationSeverity.INFO,
                                rule_id, action_field, f"Item {i+1} in {action_field} may not use clear imperative language",
                                "Use clear action verbs like 'Implement', 'Validate', 'Avoid', 'Never'"
                            ))
        
        # Check for security-specific terminology
        if 'requirement' in rule_card:
            if not self._has_security_terminology(rule_card['requirement']):
                issues.append(ValidationIssue(
                    ValidationLevel.CONTENT, ValidationSeverity.INFO,
                    rule_id, 'requirement', "Requirement may lack explicit security terminology",
                    "Consider adding security-specific terms like 'validate', 'sanitize', 'authenticate', etc."
                ))
        
        return issues
    
    def validate_integration_compatibility(self, rule_card: Dict[str, Any], rule_id: str) -> List[ValidationIssue]:
        """Validate compatibility with scanner integration and semantic search."""
        issues = []
        config = self.config["validation"]
        
        # Check for scanner integration
        if config.get("scanner_integration_required", True):
            if 'detect' not in rule_card or not rule_card['detect']:
                issues.append(ValidationIssue(
                    ValidationLevel.INTEGRATION, ValidationSeverity.ERROR,
                    rule_id, 'detect', "Missing detect section for scanner integration",
                    "Add detect section with semgrep, trufflehog, or custom patterns"
                ))
            else:
                detect_tools = set(rule_card['detect'].keys())
                if not detect_tools.intersection(self.schema.SCANNER_TOOLS):
                    issues.append(ValidationIssue(
                        ValidationLevel.INTEGRATION, ValidationSeverity.WARNING,
                        rule_id, 'detect', f"No recognized scanner tools found in detect section",
                        f"Add one of: {', '.join(self.schema.SCANNER_TOOLS)}"
                    ))
        
        # Check for references section
        if config.get("references_required", True):
            if 'refs' not in rule_card or not rule_card['refs']:
                issues.append(ValidationIssue(
                    ValidationLevel.INTEGRATION, ValidationSeverity.ERROR,
                    rule_id, 'refs', "Missing refs section",
                    "Add refs section with CWE, ASVS, or OWASP references"
                ))
            else:
                ref_categories = set(rule_card['refs'].keys())
                if not ref_categories.intersection(self.schema.REFERENCE_CATEGORIES):
                    issues.append(ValidationIssue(
                        ValidationLevel.INTEGRATION, ValidationSeverity.WARNING,
                        rule_id, 'refs', "No recognized reference categories found",
                        f"Add one of: {', '.join(self.schema.REFERENCE_CATEGORIES)}"
                    ))
        
        # Check ID format for consistency
        if 'id' in rule_card:
            rule_id_value = rule_card['id']
            if not re.match(r'^[A-Z][A-Z0-9_-]*[A-Z0-9]$', rule_id_value):
                issues.append(ValidationIssue(
                    ValidationLevel.INTEGRATION, ValidationSeverity.WARNING,
                    rule_id, 'id', f"Rule ID format may not follow conventions: {rule_id_value}",
                    "Use UPPER_CASE format with hyphens or underscores"
                ))
        
        return issues
    
    def validate_performance_impact(self, rule_card: Dict[str, Any], rule_id: str) -> List[ValidationIssue]:
        """Validate potential performance impact of rule card content."""
        issues = []
        
        # Check for overly complex detection patterns
        if 'detect' in rule_card:
            for tool, patterns in rule_card['detect'].items():
                if isinstance(patterns, list):
                    for pattern in patterns:
                        if isinstance(pattern, str):
                            # Check for potentially expensive regex patterns
                            if any(char in pattern for char in ['*', '+', '.*', '.+']) and pattern.count('.') > 3:
                                issues.append(ValidationIssue(
                                    ValidationLevel.PERFORMANCE, ValidationSeverity.INFO,
                                    rule_id, 'detect', f"Pattern may be computationally expensive: {pattern}",
                                    "Consider optimizing regex patterns for better performance"
                                ))
        
        # Check for overly long content that might impact search performance
        total_content_length = 0
        for field in ['title', 'requirement', 'do', 'dont']:
            if field in rule_card:
                if isinstance(rule_card[field], str):
                    total_content_length += len(rule_card[field])
                elif isinstance(rule_card[field], list):
                    total_content_length += sum(len(str(item)) for item in rule_card[field])
        
        if total_content_length > 2000:
            issues.append(ValidationIssue(
                ValidationLevel.PERFORMANCE, ValidationSeverity.INFO,
                rule_id, 'content', f"Total content length is high ({total_content_length} chars)",
                "Consider condensing content for better search performance"
            ))
        
        return issues
    
    def _has_imperative_language(self, text: str) -> bool:
        """Check if text uses imperative language suitable for security guidelines."""
        imperative_verbs = {
            'implement', 'use', 'enforce', 'validate', 'sanitize', 'authenticate',
            'authorize', 'encrypt', 'secure', 'protect', 'verify', 'check',
            'ensure', 'avoid', 'prevent', 'disable', 'enable', 'configure',
            'apply', 'establish', 'maintain', 'monitor', 'log', 'audit'
        }
        
        words = text.lower().split()
        return any(word.strip('.,!?;:') in imperative_verbs for word in words[:3])
    
    def _has_security_terminology(self, text: str) -> bool:
        """Check if text contains security-specific terminology."""
        security_terms = {
            'security', 'secure', 'vulnerability', 'threat', 'attack', 'malicious',
            'injection', 'validation', 'sanitization', 'authentication', 'authorization',
            'encryption', 'cryptography', 'hash', 'salt', 'token', 'session',
            'xss', 'csrf', 'sql injection', 'buffer overflow', 'privilege',
            'access control', 'firewall', 'tls', 'ssl', 'certificate'
        }
        
        text_lower = text.lower()
        return any(term in text_lower for term in security_terms)
    
    def calculate_quality_score(self, rule_card: Dict[str, Any], issues: List[ValidationIssue]) -> float:
        """Calculate overall quality score for a rule card."""
        base_score = 1.0
        
        # Deduct points for issues
        for issue in issues:
            if issue.severity == ValidationSeverity.ERROR:
                base_score -= 0.2
            elif issue.severity == ValidationSeverity.WARNING:
                base_score -= 0.1
            elif issue.severity == ValidationSeverity.INFO:
                base_score -= 0.05
        
        # Add points for completeness
        completeness_bonus = 0.0
        
        # Bonus for having all optional fields
        optional_fields = ['do', 'dont', 'detect', 'verify', 'refs']
        for field in optional_fields:
            if field in rule_card and rule_card[field]:
                completeness_bonus += 0.05
        
        # Bonus for rich content
        if 'do' in rule_card and len(rule_card['do']) >= 3:
            completeness_bonus += 0.05
        if 'dont' in rule_card and len(rule_card['dont']) >= 2:
            completeness_bonus += 0.05
        if 'refs' in rule_card and len(rule_card['refs']) >= 2:
            completeness_bonus += 0.05
        
        final_score = max(0.0, min(1.0, base_score + completeness_bonus))
        return round(final_score, 3)
    
    def validate_rule_card(self, rule_card: Dict[str, Any], rule_id: str) -> Tuple[List[ValidationIssue], float]:
        """Validate a single rule card comprehensively."""
        all_issues = []
        
        # Run all validation levels
        all_issues.extend(self.validate_schema(rule_card, rule_id))
        all_issues.extend(self.validate_content_quality(rule_card, rule_id))
        all_issues.extend(self.validate_integration_compatibility(rule_card, rule_id))
        all_issues.extend(self.validate_performance_impact(rule_card, rule_id))
        
        # Calculate quality score
        quality_score = self.calculate_quality_score(rule_card, all_issues)
        
        return all_issues, quality_score
    
    def validate_rule_cards_directory(self, directory_path: str = "app/rule_cards/owasp") -> ValidationReport:
        """Validate all rule cards in a directory."""
        logger.info(f"Starting comprehensive validation of rule cards in {directory_path}")
        
        all_issues = []
        rule_scores = []
        valid_rules = 0
        total_rules = 0
        
        # Find all YAML files
        pattern = os.path.join(directory_path, "**", "*.yml")
        yaml_files = glob.glob(pattern, recursive=True)
        
        logger.info(f"Found {len(yaml_files)} rule card files to validate")
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    rule_card = yaml.safe_load(f)
                
                if not rule_card:
                    continue
                
                total_rules += 1
                rule_id = rule_card.get('id', os.path.basename(yaml_file))
                
                # Validate the rule card
                issues, quality_score = self.validate_rule_card(rule_card, rule_id)
                
                all_issues.extend(issues)
                rule_scores.append(quality_score)
                
                # Count as valid if no errors
                has_errors = any(issue.severity == ValidationSeverity.ERROR for issue in issues)
                if not has_errors:
                    valid_rules += 1
                
            except Exception as e:
                logger.warning(f"Failed to validate {yaml_file}: {e}")
                all_issues.append(ValidationIssue(
                    ValidationLevel.SCHEMA, ValidationSeverity.ERROR,
                    os.path.basename(yaml_file), 'file', f"Failed to load YAML file: {e}",
                    "Fix YAML syntax errors"
                ))
                rule_scores.append(0.0)
                total_rules += 1
        
        # Calculate overall quality score
        overall_quality_score = sum(rule_scores) / max(len(rule_scores), 1)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(all_issues, overall_quality_score)
        
        report = ValidationReport(
            total_rules=total_rules,
            valid_rules=valid_rules,
            invalid_rules=total_rules - valid_rules,
            issues=all_issues,
            quality_score=overall_quality_score,
            recommendations=recommendations
        )
        
        logger.info(f"Validation complete: {valid_rules}/{total_rules} rules valid, quality score: {overall_quality_score:.3f}")
        
        return report
    
    def _generate_recommendations(self, issues: List[ValidationIssue], quality_score: float) -> List[str]:
        """Generate actionable recommendations based on validation results."""
        recommendations = []
        
        # Count issues by type
        error_count = len([i for i in issues if i.severity == ValidationSeverity.ERROR])
        warning_count = len([i for i in issues if i.severity == ValidationSeverity.WARNING])
        
        # Recommendations based on error patterns
        if error_count > 0:
            recommendations.append(f"Fix {error_count} schema and critical issues before deployment")
        
        if warning_count > 0:
            recommendations.append(f"Address {warning_count} warnings to improve rule quality")
        
        # Quality-based recommendations
        if quality_score < 0.7:
            recommendations.append("Overall quality score is below acceptable threshold - review content completeness")
        elif quality_score < 0.85:
            recommendations.append("Good quality achieved - consider enhancing content richness for better coverage")
        else:
            recommendations.append("Excellent quality achieved - rule cards meet all standards")
        
        # Specific pattern recommendations
        common_issues = {}
        for issue in issues:
            key = f"{issue.level.value}_{issue.field}"
            common_issues[key] = common_issues.get(key, 0) + 1
        
        # Find most common issues
        if common_issues:
            most_common = max(common_issues.items(), key=lambda x: x[1])
            if most_common[1] > 2:
                recommendations.append(f"Common issue detected: {most_common[0]} - consider systematic review")
        
        return recommendations
    
    def save_validation_report(self, report: ValidationReport, output_path: str = "reports/validation_report.json") -> bool:
        """Save validation report to file."""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(report.to_dict(), f, indent=2)
            
            logger.info(f"Validation report saved to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save validation report: {e}")
            return False


def main():
    """Main entry point for quality validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="OWASP Rule Cards Quality Validator")
    parser.add_argument("--directory", default="app/rule_cards/owasp", help="Directory containing rule cards")
    parser.add_argument("--config", help="Path to validation configuration file")
    parser.add_argument("--output", default="reports/validation_report.json", help="Output path for validation report")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Initialize validator
        validator = QualityValidator(args.config)
        
        # Run comprehensive validation
        report = validator.validate_rule_cards_directory(args.directory)
        
        # Save report
        validator.save_validation_report(report, args.output)
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"OWASP RULE CARDS QUALITY VALIDATION REPORT")
        print(f"{'='*60}")
        print(f"Total Rule Cards: {report.total_rules}")
        print(f"Valid Rule Cards: {report.valid_rules}")
        print(f"Invalid Rule Cards: {report.invalid_rules}")
        print(f"Success Rate: {(report.valid_rules/max(report.total_rules,1)*100):.1f}%")
        print(f"Quality Score: {report.quality_score:.3f}")
        print(f"\nIssues Found:")
        print(f"  Errors: {len([i for i in report.issues if i.severity == ValidationSeverity.ERROR])}")
        print(f"  Warnings: {len([i for i in report.issues if i.severity == ValidationSeverity.WARNING])}")
        print(f"  Info: {len([i for i in report.issues if i.severity == ValidationSeverity.INFO])}")
        
        if report.recommendations:
            print(f"\nRecommendations:")
            for i, rec in enumerate(report.recommendations, 1):
                print(f"  {i}. {rec}")
        
        # Exit with appropriate code
        if report.invalid_rules == 0:
            print(f"\n✅ All rule cards passed validation!")
            sys.exit(0)
        else:
            print(f"\n⚠️  {report.invalid_rules} rule cards need attention")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()