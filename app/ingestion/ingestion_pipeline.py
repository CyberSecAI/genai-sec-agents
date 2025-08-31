#!/usr/bin/env python3
"""
OWASP Cheat Sheet Ingestion Pipeline

End-to-end automated ingestion pipeline that orchestrates the complete
OWASP cheat sheet to Rule Card to semantic search corpus workflow.

Task 5: Ingestion Pipeline and Automation for Story 2.5
"""

import os
import sys
import json
import logging
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from app.ingestion.owasp_fetcher import OWASPFetcher
from app.ingestion.llm_rule_generator import LLMRuleCardGenerator
from app.ingestion.scanner_mapper import SecurityScannerMapper
from app.ingestion.corpus_integration import OWASPCorpusIntegrator

logger = logging.getLogger(__name__)


class PipelineConfig:
    """Configuration for the ingestion pipeline."""
    
    def __init__(self, config_path: str = "app/ingestion/config/pipeline_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load pipeline configuration with defaults."""
        default_config = {
            "pipeline": {
                "name": "OWASP Cheat Sheet Ingestion",
                "version": "1.0.0",
                "max_concurrent_requests": 2,
                "retry_count": 3,
                "timeout_seconds": 300
            },
            "validation": {
                "schema_validation": True,
                "duplicate_detection": True,
                "quality_threshold": 0.8,
                "max_failures_percent": 20
            },
            "output": {
                "rule_cards_path": "app/rule_cards/owasp",
                "backup_enabled": True,
                "backup_path": "backups/owasp_ingestion"
            },
            "logging": {
                "level": "INFO",
                "log_file": "logs/owasp_ingestion.log",
                "detailed_logging": True
            }
        }
        
        # Try to load configuration file if it exists
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                # Merge user config with defaults
                self._deep_merge(default_config, user_config)
            except Exception as e:
                logger.warning(f"Failed to load config from {self.config_path}: {e}")
                
        return default_config
    
    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> None:
        """Deep merge configuration dictionaries."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value


class PipelineState:
    """Tracks the state of the ingestion pipeline execution."""
    
    def __init__(self):
        self.start_time = datetime.now(timezone.utc)
        self.end_time = None
        self.status = "running"
        self.total_cheat_sheets = 0
        self.processed_cheat_sheets = 0
        self.successful_rule_cards = 0
        self.failed_rule_cards = 0
        self.scanner_mappings = 0
        self.corpus_integrated = False
        self.errors = []
        self.warnings = []
        
    def add_error(self, error: str):
        """Add an error to the pipeline state."""
        self.errors.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": error
        })
        logger.error(error)
        
    def add_warning(self, warning: str):
        """Add a warning to the pipeline state."""
        self.warnings.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "warning": warning
        })
        logger.warning(warning)
    
    def finalize(self, status: str):
        """Finalize pipeline execution state."""
        self.end_time = datetime.now(timezone.utc)
        self.status = status
        duration = (self.end_time - self.start_time).total_seconds()
        logger.info(f"Pipeline finished with status: {status} (duration: {duration:.2f}s)")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert pipeline state to dictionary for serialization."""
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "total_cheat_sheets": self.total_cheat_sheets,
            "processed_cheat_sheets": self.processed_cheat_sheets,
            "successful_rule_cards": self.successful_rule_cards,
            "failed_rule_cards": self.failed_rule_cards,
            "scanner_mappings": self.scanner_mappings,
            "corpus_integrated": self.corpus_integrated,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings
        }


class OWASPIngestionPipeline:
    """Complete OWASP cheat sheet ingestion pipeline."""
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        """Initialize the ingestion pipeline."""
        self.config = config or PipelineConfig()
        self.state = PipelineState()
        
        # Initialize pipeline components
        self.owasp_fetcher = OWASPFetcher()
        self.llm_generator = LLMRuleCardGenerator()
        self.scanner_mapper = SecurityScannerMapper()
        self.corpus_integrator = OWASPCorpusIntegrator()
        
        # Setup logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup detailed logging for the pipeline."""
        log_config = self.config.config["logging"]
        
        # Create logs directory if needed
        log_file = log_config.get("log_file", "logs/owasp_ingestion.log")
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
            
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_config.get("level", "INFO")),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def _backup_existing_data(self) -> bool:
        """Backup existing rule cards before pipeline execution."""
        try:
            backup_config = self.config.config["output"]
            if not backup_config.get("backup_enabled", True):
                return True
                
            backup_path = backup_config.get("backup_path", "backups/owasp_ingestion")
            rule_cards_path = backup_config.get("rule_cards_path", "app/rule_cards/owasp")
            
            # Create backup directory with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(backup_path, f"backup_{timestamp}")
            os.makedirs(backup_dir, exist_ok=True)
            
            # Copy existing rule cards if they exist
            if os.path.exists(rule_cards_path):
                import shutil
                shutil.copytree(rule_cards_path, os.path.join(backup_dir, "rule_cards"))
                logger.info(f"Backed up existing rule cards to {backup_dir}")
                
            return True
            
        except Exception as e:
            self.state.add_warning(f"Backup failed: {e}")
            return True  # Non-critical failure
    
    def _validate_prerequisites(self) -> bool:
        """Validate that all prerequisites are met for pipeline execution."""
        try:
            # Check OpenAI API key availability
            if not os.getenv('OPENAI_API_KEY'):
                self.state.add_error("OPENAI_API_KEY environment variable not set")
                return False
                
            # Validate output directories
            output_config = self.config.config["output"]
            rule_cards_path = output_config.get("rule_cards_path", "app/rule_cards/owasp")
            
            # Ensure output directory exists
            os.makedirs(rule_cards_path, exist_ok=True)
            
            # Test write permissions
            test_file = os.path.join(rule_cards_path, ".pipeline_test")
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
            except Exception as e:
                self.state.add_error(f"No write access to output directory: {e}")
                return False
                
            logger.info("Prerequisites validation passed")
            return True
            
        except Exception as e:
            self.state.add_error(f"Prerequisites validation failed: {e}")
            return False
    
    def _detect_duplicate_rule_cards(self, new_rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect and handle duplicate rule cards."""
        validation_config = self.config.config["validation"]
        if not validation_config.get("duplicate_detection", True):
            return new_rules
            
        # Load existing rule IDs
        existing_ids = set()
        rule_cards_path = self.config.config["output"]["rule_cards_path"]
        
        if os.path.exists(rule_cards_path):
            import glob
            for yaml_file in glob.glob(os.path.join(rule_cards_path, "**", "*.yml"), recursive=True):
                try:
                    import yaml
                    with open(yaml_file, 'r') as f:
                        rule_data = yaml.safe_load(f)
                        if rule_data and 'id' in rule_data:
                            existing_ids.add(rule_data['id'])
                except Exception:
                    continue
        
        # Filter out duplicates
        unique_rules = []
        duplicate_count = 0
        
        for rule in new_rules:
            if rule.get('id') in existing_ids:
                duplicate_count += 1
                self.state.add_warning(f"Skipping duplicate rule ID: {rule.get('id')}")
            else:
                unique_rules.append(rule)
                
        if duplicate_count > 0:
            logger.info(f"Filtered out {duplicate_count} duplicate rule cards")
            
        return unique_rules
    
    def _validate_rule_quality(self, rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate rule card quality against threshold."""
        validation_config = self.config.config["validation"]
        quality_threshold = validation_config.get("quality_threshold", 0.8)
        
        quality_rules = []
        failed_count = 0
        
        for rule in rules:
            quality_score = self._calculate_rule_quality_score(rule)
            
            if quality_score >= quality_threshold:
                rule['_quality_score'] = quality_score
                quality_rules.append(rule)
            else:
                failed_count += 1
                self.state.add_warning(f"Rule {rule.get('id')} failed quality check (score: {quality_score:.2f})")
        
        # Check if failure rate exceeds threshold
        max_failures_percent = validation_config.get("max_failures_percent", 20)
        if rules:  # Avoid division by zero
            failure_rate = (failed_count / len(rules)) * 100
            if failure_rate > max_failures_percent:
                self.state.add_error(f"Quality failure rate ({failure_rate:.1f}%) exceeds threshold ({max_failures_percent}%)")
                return []
        
        logger.info(f"Quality validation passed: {len(quality_rules)}/{len(rules)} rules meet quality threshold")
        return quality_rules
    
    def _calculate_rule_quality_score(self, rule: Dict[str, Any]) -> float:
        """Calculate a quality score for a rule card."""
        score = 0.0
        max_score = 10.0
        
        # Required fields presence (40% of score)
        required_fields = ['id', 'title', 'severity', 'scope', 'requirement']
        for field in required_fields:
            if field in rule and rule[field]:
                score += 0.8
        
        # Content quality (30% of score)
        if 'do' in rule and isinstance(rule['do'], list) and len(rule['do']) > 0:
            score += 1.0
        if 'dont' in rule and isinstance(rule['dont'], list) and len(rule['dont']) > 0:
            score += 1.0
        if 'detect' in rule and isinstance(rule['detect'], dict):
            score += 1.0
            
        # Metadata quality (20% of score)
        if 'refs' in rule and isinstance(rule['refs'], dict):
            if 'cwe' in rule['refs'] or 'owasp' in rule['refs']:
                score += 1.0
        if 'verify' in rule:
            score += 1.0
            
        # Title and requirement quality (10% of score)
        if 'title' in rule and len(rule['title']) > 10:
            score += 0.5
        if 'requirement' in rule and len(rule['requirement']) > 20:
            score += 0.5
            
        return score / max_score
    
    def _save_pipeline_report(self) -> bool:
        """Save pipeline execution report."""
        try:
            # Create reports directory
            reports_dir = "reports"
            os.makedirs(reports_dir, exist_ok=True)
            
            # Generate report filename with timestamp
            timestamp = self.state.start_time.strftime("%Y%m%d_%H%M%S")
            report_file = os.path.join(reports_dir, f"owasp_ingestion_report_{timestamp}.json")
            
            # Create comprehensive report
            report = {
                "pipeline_config": self.config.config,
                "execution_state": self.state.to_dict(),
                "summary": {
                    "total_execution_time": (self.state.end_time - self.state.start_time).total_seconds() if self.state.end_time else None,
                    "success_rate": (self.state.successful_rule_cards / max(self.state.processed_cheat_sheets, 1)) * 100,
                    "processing_efficiency": (self.state.processed_cheat_sheets / max(self.state.total_cheat_sheets, 1)) * 100
                }
            }
            
            # Save report
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
                
            logger.info(f"Pipeline report saved to {report_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save pipeline report: {e}")
            return False
    
    def run_full_pipeline(self, cheat_sheet_urls: Optional[List[str]] = None) -> bool:
        """Execute the complete OWASP ingestion pipeline."""
        logger.info("=" * 80)
        logger.info("OWASP CHEAT SHEET INGESTION PIPELINE - Starting Execution")
        logger.info("=" * 80)
        
        try:
            # Step 0: Prerequisites validation
            logger.info("Step 0: Validating prerequisites...")
            if not self._validate_prerequisites():
                self.state.finalize("failed_prerequisites")
                return False
            
            # Step 1: Backup existing data
            logger.info("Step 1: Backing up existing data...")
            self._backup_existing_data()
            
            # Step 2: Fetch OWASP cheat sheets
            logger.info("Step 2: Fetching OWASP cheat sheets...")
            if cheat_sheet_urls is None:
                cheat_sheets = self.owasp_fetcher.get_prioritized_cheat_sheets()
            else:
                cheat_sheets = [{"url": url, "title": f"Custom-{i}"} for i, url in enumerate(cheat_sheet_urls)]
                
            self.state.total_cheat_sheets = len(cheat_sheets)
            logger.info(f"Found {len(cheat_sheets)} cheat sheets to process")
            
            # Step 3: Generate Rule Cards using LLM
            logger.info("Step 3: Generating Rule Cards with ChatGPT...")
            generated_results = self.llm_generator.generate_bulk_rule_cards()
            
            self.state.processed_cheat_sheets = len(generated_results)
            self.state.successful_rule_cards = sum(1 for r in generated_results.values() if r.get('success', False))
            self.state.failed_rule_cards = self.state.processed_cheat_sheets - self.state.successful_rule_cards
            
            logger.info(f"Generated {self.state.successful_rule_cards}/{self.state.processed_cheat_sheets} Rule Cards successfully")
            
            # Step 4: Validate and filter Rule Cards
            logger.info("Step 4: Validating Rule Card quality...")
            all_generated_rules = []
            for result in generated_results.values():
                if result.get('success') and result.get('rule_cards'):
                    all_generated_rules.extend(result['rule_cards'])
                    
            # Quality validation
            quality_rules = self._validate_rule_quality(all_generated_rules)
            if not quality_rules:
                self.state.add_error("No rules passed quality validation")
                self.state.finalize("failed_quality")
                return False
            
            # Duplicate detection
            unique_rules = self._detect_duplicate_rule_cards(quality_rules)
            logger.info(f"Quality validation complete: {len(unique_rules)} rules ready for processing")
            
            # Step 5: Scanner integration mapping
            logger.info("Step 5: Mapping Rule Cards to security scanners...")
            scanner_results = self.scanner_mapper.process_all_rule_cards()
            self.state.scanner_mappings = len([r for r in scanner_results.values() if r.semgrep_mappings or r.trufflehog_mappings])
            
            logger.info(f"Scanner mapping complete: {self.state.scanner_mappings} rules mapped to scanners")
            
            # Step 6: Corpus integration
            logger.info("Step 6: Integrating with semantic search corpus...")
            corpus_success = self.corpus_integrator.run_full_integration()
            self.state.corpus_integrated = corpus_success
            
            if corpus_success:
                logger.info("Corpus integration completed successfully")
            else:
                self.state.add_warning("Corpus integration failed but pipeline continues")
            
            # Step 7: Final validation and reporting
            logger.info("Step 7: Generating final reports...")
            self._save_pipeline_report()
            
            # Determine final status
            if self.state.successful_rule_cards > 0 and self.state.scanner_mappings > 0:
                self.state.finalize("success")
                
                logger.info("=" * 80)
                logger.info("🎉 OWASP INGESTION PIPELINE COMPLETED SUCCESSFULLY!")
                logger.info(f"   • Processed: {self.state.processed_cheat_sheets} cheat sheets")
                logger.info(f"   • Generated: {self.state.successful_rule_cards} Rule Cards")
                logger.info(f"   • Scanner mappings: {self.state.scanner_mappings} rules")
                logger.info(f"   • Corpus integrated: {'✅' if self.state.corpus_integrated else '⚠️'}")
                logger.info("=" * 80)
                
                return True
            else:
                self.state.finalize("partial_failure")
                logger.warning("Pipeline completed with partial failures")
                return False
                
        except Exception as e:
            self.state.add_error(f"Pipeline execution failed: {e}")
            self.state.finalize("failed_execution")
            return False


def main():
    """Main entry point for the ingestion pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(description="OWASP Cheat Sheet Ingestion Pipeline")
    parser.add_argument("--config", help="Path to pipeline configuration file")
    parser.add_argument("--urls", nargs="+", help="Specific cheat sheet URLs to process")
    parser.add_argument("--dry-run", action="store_true", help="Validate configuration without executing")
    
    args = parser.parse_args()
    
    try:
        # Initialize pipeline
        config = PipelineConfig(args.config) if args.config else PipelineConfig()
        pipeline = OWASPIngestionPipeline(config)
        
        if args.dry_run:
            logger.info("Dry run mode - validating configuration only")
            success = pipeline._validate_prerequisites()
            print("✅ Configuration validation passed" if success else "❌ Configuration validation failed")
            sys.exit(0 if success else 1)
        
        # Execute pipeline
        success = pipeline.run_full_pipeline(args.urls)
        sys.exit(0 if success else 1)
        
    except Exception as e:
        logger.error(f"Pipeline initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()