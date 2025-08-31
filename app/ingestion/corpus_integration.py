#!/usr/bin/env python3
"""
OWASP Rule Cards Corpus Integration

Integrates generated OWASP Rule Cards into the semantic search corpus
for enhanced knowledge base and semantic search capabilities.

Task 4: Corpus Integration and Semantic Enhancement for Story 2.5
"""

import os
import sys
import logging
import yaml
import glob
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from app.semantic.corpus_manager import CorpusManager

logger = logging.getLogger(__name__)


class OWASPCorpusIntegrator:
    """Integrates OWASP Rule Cards with semantic search corpus."""
    
    def __init__(self):
        """Initialize the corpus integrator."""
        self.corpus_manager = CorpusManager()
        self.owasp_rules_path = "app/rule_cards/owasp"
        
    def load_owasp_rule_cards(self) -> List[Dict[str, Any]]:
        """Load all OWASP Rule Cards from the file system."""
        rule_cards = []
        
        # Find all YAML files in OWASP rule cards directory
        pattern = os.path.join(self.owasp_rules_path, "**", "*.yml")
        yaml_files = glob.glob(pattern, recursive=True)
        
        logger.info(f"Found {len(yaml_files)} OWASP Rule Card files")
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    rule_data = yaml.safe_load(f)
                    
                # Add provenance metadata
                rule_data['_source_file'] = yaml_file
                rule_data['_source_type'] = 'owasp_generated'
                rule_data['_source_category'] = 'external_guidance'
                
                # Extract topic from file path
                path_parts = Path(yaml_file).parts
                if len(path_parts) >= 2:
                    rule_data['_topic'] = path_parts[-2]  # Directory name
                    
                rule_cards.append(rule_data)
                
            except Exception as e:
                logger.warning(f"Failed to load rule card {yaml_file}: {e}")
                continue
                
        logger.info(f"Successfully loaded {len(rule_cards)} OWASP Rule Cards")
        return rule_cards
    
    def validate_rule_cards(self, rule_cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate Rule Cards against schema requirements."""
        valid_cards = []
        required_fields = ['id', 'title', 'severity', 'scope', 'requirement']
        
        for rule_card in rule_cards:
            # Check required fields
            missing_fields = [field for field in required_fields if field not in rule_card]
            
            if missing_fields:
                logger.warning(f"Rule Card {rule_card.get('id', 'unknown')} missing fields: {missing_fields}")
                continue
                
            # Validate severity levels
            valid_severities = ['low', 'medium', 'high', 'critical']
            if rule_card.get('severity') not in valid_severities:
                logger.warning(f"Rule Card {rule_card.get('id')} has invalid severity: {rule_card.get('severity')}")
                continue
                
            valid_cards.append(rule_card)
            
        logger.info(f"Validated {len(valid_cards)}/{len(rule_cards)} Rule Cards")
        return valid_cards
    
    def enhance_rule_cards_for_search(self, rule_cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance Rule Cards with semantic search metadata."""
        enhanced_cards = []
        
        for rule_card in rule_cards:
            # Add search keywords based on content
            search_keywords = []
            
            # Extract keywords from title and requirement
            if 'title' in rule_card:
                search_keywords.extend(rule_card['title'].lower().split())
            if 'requirement' in rule_card:
                search_keywords.extend(rule_card['requirement'].lower().split())
                
            # Add domain-specific keywords
            if 'do' in rule_card:
                for practice in rule_card['do']:
                    search_keywords.extend(practice.lower().split())
                    
            # Clean and deduplicate keywords
            cleaned_keywords = []
            stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            for keyword in search_keywords:
                clean_keyword = keyword.strip('.,!?;:').lower()
                if len(clean_keyword) > 2 and clean_keyword not in stop_words:
                    cleaned_keywords.append(clean_keyword)
                    
            rule_card['_search_keywords'] = list(set(cleaned_keywords))
            
            # Add provenance tags for search filtering
            rule_card['_provenance_tags'] = [
                'owasp_generated',
                'external_guidance', 
                f"topic_{rule_card.get('_topic', 'general')}",
                f"severity_{rule_card.get('severity', 'medium')}"
            ]
            
            enhanced_cards.append(rule_card)
            
        logger.info(f"Enhanced {len(enhanced_cards)} Rule Cards for semantic search")
        return enhanced_cards
    
    def integrate_with_corpus(self, rule_cards: List[Dict[str, Any]]) -> bool:
        """Integrate OWASP Rule Cards with existing corpus."""
        try:
            logger.info("Starting corpus integration...")
            
            # Check existing corpus status
            corpus_metadata = self.corpus_manager.get_corpus_metadata()
            if corpus_metadata:
                logger.info(f"Existing corpus: {corpus_metadata.rule_count} rules, {corpus_metadata.size_bytes} bytes")
            else:
                logger.info("No existing corpus found - will create new one")
            
            # Update corpus incrementally to preserve existing content
            success = self.corpus_manager.update_corpus_incremental(rule_cards)
            
            if success:
                # Validate updated corpus
                validation_result = self.corpus_manager.validate_corpus_integrity()
                
                if validation_result.valid:
                    logger.info("Corpus integration completed successfully")
                    
                    # Log final corpus statistics
                    updated_metadata = self.corpus_manager.get_corpus_metadata()
                    if updated_metadata:
                        logger.info(f"Updated corpus: {updated_metadata.rule_count} total rules")
                        logger.info(f"Corpus size: {updated_metadata.size_bytes / 1024:.1f} KB")
                        
                    return True
                else:
                    logger.error(f"Corpus validation failed: {validation_result.errors}")
                    return False
            else:
                logger.error("Failed to update corpus")
                return False
                
        except Exception as e:
            logger.error(f"Corpus integration failed: {e}")
            return False
    
    def run_full_integration(self) -> bool:
        """Run the complete OWASP Rule Cards corpus integration process."""
        logger.info("=" * 60)
        logger.info("OWASP Rule Cards Corpus Integration - Task 4")
        logger.info("=" * 60)
        
        try:
            # Step 1: Load OWASP Rule Cards
            logger.info("Step 1: Loading OWASP Rule Cards...")
            rule_cards = self.load_owasp_rule_cards()
            
            if not rule_cards:
                logger.error("No OWASP Rule Cards found to integrate")
                return False
            
            # Step 2: Validate Rule Cards
            logger.info("Step 2: Validating Rule Cards...")
            valid_cards = self.validate_rule_cards(rule_cards)
            
            if not valid_cards:
                logger.error("No valid Rule Cards found after validation")
                return False
            
            # Step 3: Enhance for semantic search
            logger.info("Step 3: Enhancing Rule Cards for semantic search...")
            enhanced_cards = self.enhance_rule_cards_for_search(valid_cards)
            
            # Step 4: Integrate with corpus
            logger.info("Step 4: Integrating with semantic search corpus...")
            integration_success = self.integrate_with_corpus(enhanced_cards)
            
            if integration_success:
                logger.info("✅ OWASP Rule Cards corpus integration completed successfully!")
                logger.info(f"   • {len(enhanced_cards)} Rule Cards integrated")
                logger.info(f"   • Enhanced semantic search capabilities")
                logger.info(f"   • OWASP provenance tracking enabled")
                return True
            else:
                logger.error("❌ Corpus integration failed")
                return False
                
        except Exception as e:
            logger.error(f"Integration process failed: {e}")
            return False


def main():
    """Main entry point for corpus integration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    integrator = OWASPCorpusIntegrator()
    success = integrator.run_full_integration()
    
    if success:
        print("\n🎉 OWASP Rule Cards successfully integrated with semantic search corpus!")
        print("   The knowledge base is now enhanced with industry-standard OWASP guidance.")
    else:
        print("\n❌ Integration failed. Check logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()