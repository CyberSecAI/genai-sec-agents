#!/usr/bin/env python3
"""
ASVS Domain-Based Ingestion Pipeline

Complete automated pipeline for OWASP ASVS (Application Security Verification Standard)
domain-based integration with intelligent rule enhancement.

Story 2.5.1: ASVS Domain-Based Integration
"""

import os
import sys
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from app.ingestion.asvs_fetcher import ASVSFetcher, ASVSSection
from app.ingestion.domain_based_asvs_generator import DomainBasedASVSGenerator, DomainIntegrationResult
from app.ingestion.rule_enhancer import RuleEnhancer, EnhancementResult
from app.ingestion.domain_mapping import DOMAIN_MAPPINGS, get_domain_for_asvs_section

logger = logging.getLogger(__name__)


class ASVSPipelineStats:
    """Statistics tracking for domain-based ASVS ingestion pipeline."""
    
    def __init__(self):
        self.start_time = datetime.now(timezone.utc)
        self.end_time = None
        self.sections_processed = 0
        self.sections_successful = 0
        self.total_requirements = 0
        self.new_rules_created = 0
        self.existing_rules_enhanced = 0
        self.rules_quality_enhanced = 0
        self.placeholders_resolved = 0
        self.total_tokens_used = 0
        self.total_cost = 0.0
        self.domains_updated = set()
        self.integration_results = {}
        self.enhancement_results = {}
        
    def add_integration_result(self, section_id: str, result: DomainIntegrationResult):
        """Add results from domain integration."""
        self.sections_processed += 1
        self.total_requirements += result.asvs_requirements_count
        
        if result.success:
            self.sections_successful += 1
            self.new_rules_created += result.new_rules_created
            self.existing_rules_enhanced += result.existing_rules_enhanced
            self.domains_updated.add(result.domain)
        
        self.total_tokens_used += result.tokens_used
        self.total_cost += result.tokens_used * 0.0015 / 1000
        
        self.integration_results[section_id] = {
            'domain': result.domain,
            'success': result.success,
            'new_rules': result.new_rules_created,
            'enhanced_rules': result.existing_rules_enhanced,
            'requirements': result.asvs_requirements_count,
            'tokens': result.tokens_used,
            'error': result.error_message
        }
    
    def add_enhancement_results(self, domain: str, results: List[EnhancementResult]):
        """Add results from rule quality enhancement."""
        if results:
            self.rules_quality_enhanced += len(results)
            self.placeholders_resolved += sum(r.resolved_placeholders for r in results)
            
            self.enhancement_results[domain] = {
                'rules_enhanced': len(results),
                'placeholders_resolved': sum(r.resolved_placeholders for r in results),
                'success_rate': (sum(1 for r in results if r.success) / len(results)) * 100
            }
    
    def finalize(self):
        """Finalize pipeline statistics."""
        self.end_time = datetime.now(timezone.utc)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get pipeline execution summary."""
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0
        
        return {
            'execution_time': duration,
            'sections_processed': self.sections_processed,
            'sections_successful': self.sections_successful,
            'success_rate': (self.sections_successful / max(self.sections_processed, 1)) * 100,
            'total_requirements': self.total_requirements,
            'new_rules_created': self.new_rules_created,
            'existing_rules_enhanced': self.existing_rules_enhanced,
            'rules_quality_enhanced': self.rules_quality_enhanced,
            'placeholders_resolved': self.placeholders_resolved,
            'domains_updated': list(self.domains_updated),
            'total_tokens_used': self.total_tokens_used,
            'estimated_cost': self.total_cost,
            'avg_tokens_per_requirement': self.total_tokens_used / max(self.total_requirements, 1),
            'integration_results': self.integration_results,
            'enhancement_results': self.enhancement_results
        }


class ASVSIngestionPipeline:
    """Domain-based ASVS ingestion and integration pipeline."""
    
    def __init__(self, priority_levels: List[int] = [1, 2]):
        """Initialize domain-based ASVS ingestion pipeline."""
        self.priority_levels = priority_levels
        self.stats = ASVSPipelineStats()
        
        # Initialize components
        self.asvs_fetcher = ASVSFetcher()
        self.domain_generator = DomainBasedASVSGenerator()
        self.rule_enhancer = RuleEnhancer()
        
        # Pipeline configuration
        self.rate_limit_delay = 2
        
        logger.info(f"Domain-based ASVS Pipeline initialized for priority levels: {priority_levels}")
    
    def validate_prerequisites(self) -> bool:
        """Validate prerequisites for pipeline execution."""
        try:
            # Check OpenAI API key
            if not os.getenv('OPENAI_API_KEY'):
                logger.error("OPENAI_API_KEY environment variable not set")
                return False
            
            # Check output directory access
            output_dir = Path("app/rule_cards/asvs")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Test write permissions
            test_file = output_dir / ".pipeline_test"
            try:
                test_file.write_text("test")
                test_file.unlink()
            except Exception as e:
                logger.error(f"Cannot write to output directory: {e}")
                return False
            
            logger.info("Prerequisites validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Prerequisites validation failed: {e}")
            return False
    
    def fetch_asvs_sections(self) -> List:
        """Fetch all ASVS sections based on priority levels."""
        logger.info(f"Fetching ASVS sections for priority levels: {self.priority_levels}")
        
        try:
            sections = self.asvs_fetcher.fetch_all_priority_sections(self.priority_levels)
            logger.info(f"Successfully fetched {len(sections)} ASVS sections")
            return sections
            
        except Exception as e:
            logger.error(f"Failed to fetch ASVS sections: {e}")
            return []
    
    def process_asvs_section(self, section: ASVSSection) -> DomainIntegrationResult:
        """Process a single ASVS section with domain-based integration."""
        logger.info(f"Processing ASVS section: {section.title} ({len(section.requirements)} requirements)")
        
        try:
            # Determine target domain
            domain = get_domain_for_asvs_section(section.id.split('-')[0])  # V11-Cryptography -> V11
            
            if domain == "unknown":
                logger.warning(f"No domain mapping found for section {section.id}")
                # Create failed result
                failed_result = DomainIntegrationResult(
                    domain="unknown",
                    asvs_section=section.id,
                    existing_rules_count=0,
                    asvs_requirements_count=len(section.requirements),
                    new_rules_created=0,
                    existing_rules_enhanced=0,
                    success=False,
                    tokens_used=0,
                    error_message=f"No domain mapping for section {section.id}"
                )
                self.stats.add_integration_result(section.id, failed_result)
                return failed_result
            
            logger.info(f"Integrating {section.title} with {domain} domain")
            
            # Perform domain integration
            result = self.domain_generator.integrate_asvs_with_domain(section, domain)
            
            # Update statistics
            self.stats.add_integration_result(section.id, result)
            
            if result.success:
                logger.info(f"✅ {section.title}: {result.new_rules_created} new, {result.existing_rules_enhanced} enhanced")
            else:
                logger.error(f"❌ {section.title}: {result.error_message}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to process section {section.title}: {e}")
            # Create failed result
            failed_result = DomainIntegrationResult(
                domain="error",
                asvs_section=section.id,
                existing_rules_count=0,
                asvs_requirements_count=len(section.requirements),
                new_rules_created=0,
                existing_rules_enhanced=0,
                success=False,
                tokens_used=0,
                error_message=str(e)
            )
            self.stats.add_integration_result(section.id, failed_result)
            return failed_result
    
    def run_full_pipeline(self) -> bool:
        """Execute the complete ASVS ingestion pipeline."""
        logger.info("=" * 80)
        logger.info("ASVS INGESTION PIPELINE - Starting Execution")
        logger.info("=" * 80)
        
        try:
            # Step 1: Prerequisites validation
            logger.info("Step 1: Validating prerequisites...")
            if not self.validate_prerequisites():
                logger.error("Prerequisites validation failed")
                return False
            
            # Step 2: Fetch ASVS sections
            logger.info("Step 2: Fetching ASVS sections...")
            sections = self.fetch_asvs_sections()
            
            if not sections:
                logger.error("No ASVS sections fetched")
                return False
            
            logger.info(f"Found {len(sections)} ASVS sections to process")
            
            # Step 3: Process each section with domain integration
            logger.info("Step 3: Processing ASVS sections with domain integration...")
            successful_sections = []
            
            for i, section in enumerate(sections, 1):
                logger.info(f"Processing section {i}/{len(sections)}: {section.title}")
                
                result = self.process_asvs_section(section)
                
                if result.success:
                    successful_sections.append(section.title)
                
                # Rate limiting between sections
                if i < len(sections):
                    logger.info("Rate limiting delay...")
                    time.sleep(self.rate_limit_delay)
            
            # Step 4: Enhance rule quality for updated domains
            if self.stats.domains_updated:
                logger.info("Step 4: Enhancing rule quality...")
                
                for domain in self.stats.domains_updated:
                    logger.info(f"Enhancing rules in {domain} domain")
                    enhancement_results = self.rule_enhancer.enhance_domain_rules(domain)
                    self.stats.add_enhancement_results(domain, enhancement_results)
                    
                    if enhancement_results:
                        successful = sum(1 for r in enhancement_results if r.success)
                        total_resolved = sum(r.resolved_placeholders for r in enhancement_results)
                        logger.info(f"✅ {domain}: {successful}/{len(enhancement_results)} rules enhanced, {total_resolved} placeholders resolved")
                    
                    time.sleep(self.rate_limit_delay)
            
            # Step 4: Finalize and report
            self.stats.finalize()
            summary = self.stats.get_summary()
            
            logger.info("=" * 80)
            logger.info("ASVS INGESTION PIPELINE - Execution Complete")
            logger.info("=" * 80)
            logger.info(f"Execution time: {summary['execution_time']:.1f} seconds")
            logger.info(f"Sections processed: {summary['sections_processed']}")
            logger.info(f"Sections successful: {summary['sections_successful']}")
            logger.info(f"Success rate: {summary['success_rate']:.1f}%")
            logger.info(f"Total ASVS requirements: {summary['total_requirements']}")
            logger.info(f"New rules created: {summary['new_rules_created']}")
            logger.info(f"Existing rules enhanced: {summary['existing_rules_enhanced']}")
            logger.info(f"Rules quality enhanced: {summary['rules_quality_enhanced']}")
            logger.info(f"Placeholders resolved: {summary['placeholders_resolved']}")
            logger.info(f"Domains updated: {len(summary['domains_updated'])}")
            logger.info(f"Total tokens used: {summary['total_tokens_used']}")
            logger.info(f"Estimated cost: ${summary['estimated_cost']:.3f}")
            
            # Save detailed report
            self.save_pipeline_report(summary)
            
            return summary['sections_successful'] > 0
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            return False
    
    def save_pipeline_report(self, summary: Dict[str, Any]) -> bool:
        """Save detailed pipeline execution report."""
        try:
            reports_dir = Path("reports")
            reports_dir.mkdir(exist_ok=True)
            
            timestamp = self.stats.start_time.strftime("%Y%m%d_%H%M%S")
            report_file = reports_dir / f"asvs_ingestion_report_{timestamp}.json"
            
            report = {
                "pipeline_type": "ASVS_INGESTION",
                "timestamp": self.stats.start_time.isoformat(),
                "priority_levels": self.priority_levels,
                "summary": summary,
                "detailed_results": {
                    "section_breakdown": summary["section_results"],
                    "performance_metrics": {
                        "avg_tokens_per_requirement": summary["avg_tokens_per_requirement"],
                        "tokens_per_second": summary["total_tokens_used"] / max(summary["execution_time"], 1),
                        "rule_cards_per_minute": summary["total_rule_cards"] * 60 / max(summary["execution_time"], 1)
                    }
                }
            }
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Pipeline report saved to {report_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save pipeline report: {e}")
            return False
    
    def run_sample_pipeline(self, section_names: List[str] = ["V6-Authentication", "V11-Cryptography"]) -> bool:
        """Run pipeline on a sample of ASVS sections for testing."""
        logger.info(f"Running sample ASVS pipeline with sections: {section_names}")
        
        try:
            # Get prioritized sections
            all_sections = self.asvs_fetcher.get_prioritized_asvs_sections(self.priority_levels)
            
            # Filter to sample sections
            sample_sections_info = [s for s in all_sections if s['id'] in section_names]
            
            if not sample_sections_info:
                logger.error(f"No sections found matching: {section_names}")
                return False
            
            logger.info(f"Found {len(sample_sections_info)} sample sections to process")
            
            # Fetch sample sections
            sample_sections = []
            for section_info in sample_sections_info:
                section = self.asvs_fetcher.fetch_asvs_section(section_info)
                if section:
                    sample_sections.append(section)
            
            if not sample_sections:
                logger.error("Failed to fetch sample sections")
                return False
            
            # Process sample sections
            for section in sample_sections:
                result = self.process_asvs_section(section)
                logger.info(f"Sample result for {section.title}: {result.success}")
            
            # Generate summary
            self.stats.finalize()
            summary = self.stats.get_summary()
            
            logger.info("Sample pipeline complete:")
            logger.info(f"  Success rate: {summary['success_rate']:.1f}%")
            logger.info(f"  New rules created: {summary['new_rules_created']}")
            logger.info(f"  Existing rules enhanced: {summary['existing_rules_enhanced']}")
            logger.info(f"  Estimated cost: ${summary['estimated_cost']:.3f}")
            
            return True
            
        except Exception as e:
            logger.error(f"Sample pipeline failed: {e}")
            return False


def main():
    """Main entry point for ASVS ingestion pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ASVS Ingestion Pipeline")
    parser.add_argument("--sample", action="store_true", help="Run sample pipeline with limited sections")
    parser.add_argument("--priority", nargs="+", type=int, default=[1, 2], help="ASVS priority levels to process")
    parser.add_argument("--sections", nargs="+", help="Specific sections for sample run")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Initialize pipeline
        pipeline = ASVSIngestionPipeline(priority_levels=args.priority)
        
        if args.sample:
            # Run sample pipeline
            sections = args.sections or ["V6-Authentication", "V11-Cryptography"]
            success = pipeline.run_sample_pipeline(sections)
        else:
            # Run full pipeline
            success = pipeline.run_full_pipeline()
        
        if success:
            print("✅ ASVS ingestion pipeline completed successfully!")
        else:
            print("❌ ASVS ingestion pipeline failed")
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        logger.error(f"Pipeline initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()