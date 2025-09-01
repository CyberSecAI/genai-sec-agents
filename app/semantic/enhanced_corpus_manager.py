"""
Enhanced Semantic Search Corpus Manager

Manages the semantic search corpus including domain-organized Rule Cards
and preserved ASVS markdown sources for comprehensive search capability.

Story 2.5.1: ASVS Domain-Based Integration - Semantic Search Enhancement
"""

import json
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class EnhancedCorpusManager:
    """Enhanced corpus manager with domain-based organization and ASVS integration."""
    
    def __init__(self):
        """Initialize enhanced corpus manager."""
        self.corpus_root = Path("app/semantic")
        self.sources_root = self.corpus_root / "sources"
        self.rule_cards_root = Path("app/rule_cards")
        
        # Ensure directories exist
        self.corpus_root.mkdir(exist_ok=True)
        self.sources_root.mkdir(exist_ok=True)
        
    def discover_rule_card_domains(self) -> List[str]:
        """Discover all available domain directories in rule_cards."""
        if not self.rule_cards_root.exists():
            return []
        
        domains = []
        for item in self.rule_cards_root.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                domains.append(item.name)
        
        return sorted(domains)
    
    def index_domain_rules(self, domain: str) -> Dict[str, Any]:
        """Index all rules in a specific domain for semantic search."""
        domain_path = self.rule_cards_root / domain
        
        if not domain_path.exists():
            logger.warning(f"Domain directory {domain} does not exist")
            return {"domain": domain, "rules": [], "error": f"Directory not found"}
        
        indexed_rules = []
        yaml_files = list(domain_path.glob("**/*.yml")) + list(domain_path.glob("**/*.yaml"))
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    rule_data = yaml.safe_load(f)
                
                if rule_data and isinstance(rule_data, dict):
                    # Create searchable content
                    searchable_content = self._create_searchable_content(rule_data)
                    
                    indexed_rule = {
                        "rule_id": rule_data.get("id", "UNKNOWN"),
                        "title": rule_data.get("title", ""),
                        "domain": domain,
                        "file_path": str(yaml_file),
                        "requirement": rule_data.get("requirement", ""),
                        "severity": rule_data.get("severity", ""),
                        "scope": rule_data.get("scope", ""),
                        "searchable_content": searchable_content,
                        "asvs_refs": rule_data.get("refs", {}).get("asvs", []),
                        "cwe_refs": rule_data.get("refs", {}).get("cwe", []),
                        "owasp_refs": rule_data.get("refs", {}).get("owasp", [])
                    }
                    indexed_rules.append(indexed_rule)
                    
            except Exception as e:
                logger.warning(f"Failed to index rule from {yaml_file}: {e}")
                continue
        
        logger.info(f"Indexed {len(indexed_rules)} rules from {domain} domain")
        
        return {
            "domain": domain,
            "rule_count": len(indexed_rules),
            "rules": indexed_rules,
            "indexed_at": datetime.now().isoformat()
        }
    
    def _create_searchable_content(self, rule_data: Dict[str, Any]) -> str:
        """Create comprehensive searchable content from rule data."""
        content_parts = []
        
        # Basic rule information
        if rule_data.get("title"):
            content_parts.append(f"Title: {rule_data['title']}")
        
        if rule_data.get("requirement"):
            content_parts.append(f"Requirement: {rule_data['requirement']}")
        
        # Do/Don't guidance
        do_items = rule_data.get("do", [])
        if do_items:
            content_parts.append("Implementation guidance:")
            content_parts.extend([f"- {item}" for item in do_items if isinstance(item, str)])
        
        dont_items = rule_data.get("dont", [])
        if dont_items:
            content_parts.append("Avoid:")
            content_parts.extend([f"- {item}" for item in dont_items if isinstance(item, str)])
        
        # Testing methods
        test_items = rule_data.get("verify", {}).get("tests", [])
        if test_items:
            content_parts.append("Testing methods:")
            content_parts.extend([f"- {item}" for item in test_items if isinstance(item, str)])
        
        # References for context
        refs = rule_data.get("refs", {})
        if refs.get("asvs"):
            content_parts.append(f"ASVS references: {', '.join(refs['asvs'])}")
        if refs.get("cwe"):
            content_parts.append(f"CWE references: {', '.join(refs['cwe'])}")
        
        return "\n".join(content_parts)
    
    def discover_asvs_sources(self) -> Dict[str, Any]:
        """Discover preserved ASVS markdown sources."""
        asvs_sources_path = self.sources_root / "asvs"
        
        if not asvs_sources_path.exists():
            return {"asvs_sources": [], "metadata": None}
        
        # Look for different versions
        asvs_sources = []
        for version_dir in asvs_sources_path.iterdir():
            if version_dir.is_dir():
                markdown_files = list(version_dir.glob("*.md"))
                
                for md_file in markdown_files:
                    source_info = {
                        "version": version_dir.name,
                        "filename": md_file.name,
                        "file_path": str(md_file),
                        "file_size": md_file.stat().st_size,
                        "last_modified": datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
                    }
                    
                    # Extract section info from filename
                    if "V" in md_file.name:
                        # e.g., 0x20-V11-Cryptography.md
                        parts = md_file.stem.split("-", 2)
                        if len(parts) >= 3:
                            source_info["section_id"] = parts[1]  # V11
                            source_info["section_name"] = parts[2].replace("-", " ")  # Cryptography
                    
                    asvs_sources.append(source_info)
        
        # Load metadata if available
        metadata = None
        metadata_file = asvs_sources_path / "v5.0" / "metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load ASVS metadata: {e}")
        
        return {
            "asvs_sources": sorted(asvs_sources, key=lambda x: x.get("filename", "")),
            "metadata": metadata,
            "total_sources": len(asvs_sources)
        }
    
    def index_asvs_source(self, source_file: Path) -> Dict[str, Any]:
        """Index a single ASVS markdown source for semantic search."""
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract basic metadata from content
            lines = content.split('\n')
            title = ""
            description = ""
            
            for line in lines:
                if line.startswith('# ') and not title:
                    title = line[2:].strip()
                elif line.strip() and not title.startswith('#') and not description:
                    # First non-empty line after title
                    description = line.strip()[:200] + "..." if len(line) > 200 else line.strip()
                    break
            
            indexed_source = {
                "source_type": "asvs_markdown",
                "file_path": str(source_file),
                "filename": source_file.name,
                "title": title,
                "description": description,
                "content_length": len(content),
                "searchable_content": content[:5000],  # First 5000 chars for search
                "full_content_available": True,
                "indexed_at": datetime.now().isoformat()
            }
            
            # Extract section info from filename
            if "V" in source_file.name:
                parts = source_file.stem.split("-", 2)
                if len(parts) >= 3:
                    indexed_source["asvs_section"] = parts[1]  # V11
                    indexed_source["section_name"] = parts[2].replace("-", " ")  # Cryptography
            
            return indexed_source
            
        except Exception as e:
            logger.error(f"Failed to index ASVS source {source_file}: {e}")
            return {
                "source_type": "asvs_markdown",
                "file_path": str(source_file),
                "error": str(e),
                "indexed_at": datetime.now().isoformat()
            }
    
    def build_enhanced_corpus(self) -> Dict[str, Any]:
        """Build enhanced semantic search corpus with rules and sources."""
        logger.info("Building enhanced semantic search corpus with domain integration")
        
        corpus = {
            "corpus_type": "domain_based_security_rules_with_asvs",
            "created_at": datetime.now().isoformat(),
            "domains": {},
            "asvs_sources": {},
            "summary": {}
        }
        
        # Index domain-based rules
        domains = self.discover_rule_card_domains()
        logger.info(f"Discovered {len(domains)} rule domains: {domains}")
        
        total_rules = 0
        for domain in domains:
            domain_index = self.index_domain_rules(domain)
            corpus["domains"][domain] = domain_index
            total_rules += domain_index["rule_count"]
        
        # Index ASVS sources
        asvs_discovery = self.discover_asvs_sources()
        
        if asvs_discovery["asvs_sources"]:
            logger.info(f"Indexing {len(asvs_discovery['asvs_sources'])} ASVS sources")
            
            for source_info in asvs_discovery["asvs_sources"]:
                source_path = Path(source_info["file_path"])
                indexed_source = self.index_asvs_source(source_path)
                
                # Use filename as key
                corpus["asvs_sources"][source_info["filename"]] = indexed_source
        
        # Add metadata
        if asvs_discovery.get("metadata"):
            corpus["asvs_metadata"] = asvs_discovery["metadata"]
        
        # Generate summary
        corpus["summary"] = {
            "total_domains": len(domains),
            "total_rules": total_rules,
            "total_asvs_sources": len(corpus["asvs_sources"]),
            "domains_list": domains,
            "integration_complete": total_rules > 0 and len(corpus["asvs_sources"]) > 0,
            "rule_distribution": {domain: corpus["domains"][domain]["rule_count"] for domain in domains}
        }
        
        logger.info(f"Enhanced corpus built: {total_rules} rules across {len(domains)} domains, "
                   f"{len(corpus['asvs_sources'])} ASVS sources")
        
        return corpus
    
    def save_corpus_index(self, corpus: Dict[str, Any], output_file: Optional[Path] = None) -> bool:
        """Save enhanced corpus index to file."""
        if output_file is None:
            output_file = self.corpus_root / "enhanced_corpus_index.json"
        
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(corpus, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Enhanced corpus index saved to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save enhanced corpus index: {e}")
            return False
    
    def validate_corpus_integration(self, corpus: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the integration between Rule Cards and ASVS sources."""
        validation = {
            "timestamp": datetime.now().isoformat(),
            "rule_asvs_coverage": {},
            "asvs_rule_mapping": {},
            "integration_quality": {}
        }
        
        # Track ASVS references in rules
        asvs_refs_in_rules = set()
        rules_with_asvs = 0
        
        for domain, domain_data in corpus.get("domains", {}).items():
            domain_asvs_refs = []
            
            for rule in domain_data.get("rules", []):
                rule_asvs_refs = rule.get("asvs_refs", [])
                if rule_asvs_refs:
                    rules_with_asvs += 1
                    asvs_refs_in_rules.update(rule_asvs_refs)
                    domain_asvs_refs.extend(rule_asvs_refs)
            
            validation["rule_asvs_coverage"][domain] = {
                "total_rules": domain_data["rule_count"],
                "rules_with_asvs": len([r for r in domain_data.get("rules", []) if r.get("asvs_refs")]),
                "unique_asvs_refs": list(set(domain_asvs_refs))
            }
        
        # Map ASVS sources to sections
        asvs_sections_available = set()
        for filename, source in corpus.get("asvs_sources", {}).items():
            if source.get("asvs_section"):
                asvs_sections_available.add(source["asvs_section"])
        
        validation["asvs_rule_mapping"] = {
            "total_asvs_refs_in_rules": len(asvs_refs_in_rules),
            "asvs_sources_available": len(corpus.get("asvs_sources", {})),
            "asvs_sections_available": list(asvs_sections_available)
        }
        
        # Integration quality metrics
        total_rules = sum(d["rule_count"] for d in corpus.get("domains", {}).values())
        
        validation["integration_quality"] = {
            "rules_with_asvs_percentage": (rules_with_asvs / max(total_rules, 1)) * 100,
            "asvs_source_coverage": len(corpus.get("asvs_sources", {})) > 0,
            "domain_rule_balance": {
                "min_rules_per_domain": min((d["rule_count"] for d in corpus.get("domains", {}).values()), default=0),
                "max_rules_per_domain": max((d["rule_count"] for d in corpus.get("domains", {}).values()), default=0),
                "avg_rules_per_domain": total_rules / max(len(corpus.get("domains", {})), 1)
            }
        }
        
        return validation
    
    def generate_corpus_report(self, corpus: Dict[str, Any]) -> str:
        """Generate comprehensive corpus integration report."""
        validation = self.validate_corpus_integration(corpus)
        
        report = f"""# Enhanced Semantic Search Corpus Report
Generated: {datetime.now().isoformat()}

## Executive Summary

**Corpus Type**: {corpus.get('corpus_type', 'Unknown')}
**Integration Status**: {'✅ Complete' if corpus['summary']['integration_complete'] else '❌ Incomplete'}

### Key Metrics
- **Total Domains**: {corpus['summary']['total_domains']}
- **Total Rules**: {corpus['summary']['total_rules']}
- **Total ASVS Sources**: {corpus['summary']['total_asvs_sources']}
- **Rules with ASVS References**: {validation['integration_quality']['rules_with_asvs_percentage']:.1f}%

## Domain Distribution

"""
        
        for domain, count in corpus['summary']['rule_distribution'].items():
            asvs_coverage = validation['rule_asvs_coverage'].get(domain, {})
            asvs_rules = asvs_coverage.get('rules_with_asvs', 0)
            
            report += f"### {domain.title()} Domain\n"
            report += f"- Total Rules: {count}\n"
            report += f"- Rules with ASVS References: {asvs_rules} ({(asvs_rules/max(count, 1)*100):.1f}%)\n"
            report += f"- Unique ASVS References: {len(asvs_coverage.get('unique_asvs_refs', []))}\n\n"
        
        report += f"""## ASVS Integration Analysis

### Source Coverage
- ASVS Markdown Sources: {len(corpus.get('asvs_sources', {}))}
- ASVS Sections Available: {len(validation['asvs_rule_mapping']['asvs_sections_available'])}
- Sections: {', '.join(validation['asvs_rule_mapping']['asvs_sections_available'])}

### Reference Integration
- Total ASVS References in Rules: {validation['asvs_rule_mapping']['total_asvs_refs_in_rules']}
- Rules with ASVS Coverage: {validation['integration_quality']['rules_with_asvs_percentage']:.1f}%

## Quality Metrics

### Rule Distribution Balance
- Minimum Rules per Domain: {validation['integration_quality']['domain_rule_balance']['min_rules_per_domain']}
- Maximum Rules per Domain: {validation['integration_quality']['domain_rule_balance']['max_rules_per_domain']}
- Average Rules per Domain: {validation['integration_quality']['domain_rule_balance']['avg_rules_per_domain']:.1f}

### Integration Completeness
- Domain-Based Organization: ✅ Complete
- ASVS Source Preservation: {'✅ Complete' if validation['integration_quality']['asvs_source_coverage'] else '❌ Missing'}
- Cross-Reference Mapping: {'✅ Good' if validation['integration_quality']['rules_with_asvs_percentage'] > 50 else '⚠️ Needs Improvement'}

## Recommendations

### Immediate Actions
"""
        
        if validation['integration_quality']['rules_with_asvs_percentage'] < 50:
            report += "- Increase ASVS reference coverage in Rule Cards\n"
        
        if len(corpus.get('asvs_sources', {})) < 5:
            report += "- Add more ASVS section sources for comprehensive coverage\n"
        
        if validation['integration_quality']['domain_rule_balance']['min_rules_per_domain'] == 0:
            report += "- Ensure all domains have at least some rules\n"
        
        report += """
### Next Steps
- Implement vector-based semantic search for better relevance
- Add rule similarity analysis across domains
- Enhance cross-referencing between rules and ASVS sources
- Validate rule accuracy against original ASVS requirements

---
*Generated by Enhanced Corpus Manager - Story 2.5.1: ASVS Domain-Based Integration*
"""
        
        return report

def main():
    """Test enhanced corpus manager functionality."""
    logging.basicConfig(level=logging.INFO)
    
    try:
        manager = EnhancedCorpusManager()
        
        print("🔍 Building enhanced semantic search corpus with ASVS integration...")
        
        # Build enhanced corpus
        corpus = manager.build_enhanced_corpus()
        
        if corpus["summary"]["integration_complete"]:
            print(f"\n✅ Enhanced corpus built successfully:")
            print(f"   - {corpus['summary']['total_domains']} domains")
            print(f"   - {corpus['summary']['total_rules']} rules")
            print(f"   - {corpus['summary']['total_asvs_sources']} ASVS sources")
            print(f"   - Domains: {', '.join(corpus['summary']['domains_list'])}")
            
            # Save corpus
            manager.save_corpus_index(corpus)
            
            # Generate and save report
            report = manager.generate_corpus_report(corpus)
            report_file = Path("docs/integration_reports/enhanced_corpus_report.md")
            report_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"   - Integration report: {report_file}")
            
        else:
            print("❌ Enhanced corpus integration incomplete")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()