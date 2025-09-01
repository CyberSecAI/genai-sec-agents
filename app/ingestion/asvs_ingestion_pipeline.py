#!/usr/bin/env python3
"""
ASVS Comprehensive Ingestion Pipeline

Complete automated pipeline for OWASP ASVS (Application Security Verification Standard)
ingestion, Rule Card generation, scanner integration, and corpus enhancement.

Building on Story 2.5 success for ASVS integration
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

from app.ingestion.asvs_fetcher import ASVSFetcher
from app.ingestion.asvs_rule_generator import ASVSRuleCardGenerator, ASVSRuleCardResult

logger = logging.getLogger(__name__)


class ASVSPipelineStats:
    """Statistics tracking for ASVS ingestion pipeline."""
    
    def __init__(self):
        self.start_time = datetime.now(timezone.utc)
        self.end_time = None
        self.sections_processed = 0
        self.sections_successful = 0
        self.total_requirements = 0
        self.total_rule_cards = 0
        self.total_tokens_used = 0
        self.total_cost = 0.0
        self.errors = []
        self.section_results = {}
        
    def add_section_result(self, section_id: str, result: ASVSRuleCardResult, requirements_count: int):
        """Add results from processing a section."""
        self.sections_processed += 1
        self.total_requirements += requirements_count
        
        if result.success:
            self.sections_successful += 1
            self.total_rule_cards += len(result.rule_cards)
        
        self.total_tokens_used += result.tokens_used
        self.total_cost += result.tokens_used * 0.0015 / 1000  # GPT-3.5-turbo pricing
        
        self.section_results[section_id] = {
            'success': result.success,
            'rule_cards': len(result.rule_cards),
            'requirements': requirements_count,
            'tokens': result.tokens_used,
            'error': result.error_message
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
            'total_rule_cards': self.total_rule_cards,
            'conversion_rate': (self.total_rule_cards / max(self.total_requirements, 1)) * 100,
            'total_tokens_used': self.total_tokens_used,
            'estimated_cost': self.total_cost,
            'avg_tokens_per_requirement': self.total_tokens_used / max(self.total_requirements, 1),
            'section_results': self.section_results
        }


class ASVSIngestionPipeline:
    """Comprehensive ASVS ingestion pipeline."""
    
    def __init__(self, priority_levels: List[int] = [1, 2]):
        """Initialize ASVS ingestion pipeline."""
        self.priority_levels = priority_levels
        self.stats = ASVSPipelineStats()
        
        # Initialize components
        self.asvs_fetcher = ASVSFetcher()
        self.rule_generator = ASVSRuleCardGenerator()
        
        logger.info(f"ASVS Ingestion Pipeline initialized for priority levels: {priority_levels}")
    
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
    
    def process_asvs_section(self, section) -> ASVSRuleCardResult:
        """Process a single ASVS section into Rule Cards."""
        logger.info(f"Processing ASVS section: {section.title} ({len(section.requirements)} requirements)")
        
        try:
            # Generate Rule Cards for this section
            result = self.rule_generator.generate_rule_cards_from_asvs_section(
                section, max_requirements_per_batch=5
            )
            
            # Save Rule Cards to files if successful
            if result.success:
                save_success = self.rule_generator.save_rule_cards_to_files(result)
                if not save_success:
                    logger.warning(f"Generated Rule Cards for {section.title} but failed to save files")
            
            # Update statistics
            self.stats.add_section_result(section.id, result, len(section.requirements))
            
            logger.info(f"Section {section.title}: {len(result.rule_cards)} Rule Cards generated")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process section {section.title}: {e}")
            # Create failed result
            failed_result = ASVSRuleCardResult(
                asvs_id=section.id,
                success=False,
                rule_cards=[],
                error_message=str(e)
            )
            self.stats.add_section_result(section.id, failed_result, len(section.requirements))
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
            
            # Step 3: Process each section
            logger.info("Step 3: Processing ASVS sections...")
            successful_sections = []
            
            for i, section in enumerate(sections, 1):
                logger.info(f"Processing section {i}/{len(sections)}: {section.title}")
                
                result = self.process_asvs_section(section)
                
                if result.success:
                    successful_sections.append(section.title)
                
                # Rate limiting between sections
                if i < len(sections):  # Don't sleep after the last section
                    logger.info("Rate limiting delay...")
                    time.sleep(3)
            
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
            logger.info(f"Total Rule Cards generated: {summary['total_rule_cards']}")
            logger.info(f"Conversion rate: {summary['conversion_rate']:.1f}%")
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
            logger.info(f"  Rule Cards generated: {summary['total_rule_cards']}")
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