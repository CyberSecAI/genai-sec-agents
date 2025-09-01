#!/usr/bin/env python3
"""
OWASP Domain Migration Tool
Migrates existing source-based OWASP Rule Cards to domain-based structure
Part of Story 2.5.1: ASVS Domain-Based Integration - Phase 2
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Set
import yaml

class OwaspDomainMigrator:
    def __init__(self, rule_cards_path: str = "app/rule_cards"):
        self.rule_cards_path = Path(rule_cards_path)
        self.owasp_path = self.rule_cards_path / "owasp"
        
        # Load domain mapping from taxonomy
        with open("docs/domain_taxonomy/domain_mapping.json", "r") as f:
            self.domain_config = json.load(f)
        
        # OWASP source to domain mapping
        self.owasp_to_domain_mapping = {
            "sql_injection_prevention": "input_validation",
            "xss_prevention": "web_security", 
            "dom_xss_prevention": "web_security",
            "csrf_prevention": "web_security",
            "clickjacking_defense": "web_security",
            "http_headers": "secure_communication",
            "authentication": "authentication",
            "session_management": "session_management",
            "file_upload": "file_handling",
            "input_validation": "input_validation",
            "error_handling": "logging",
            "logging": "logging",
            "java_security": "secure_coding",
            "nodejs_security": "secure_coding",
            "expressjs_security": "secure_coding", 
            "laravel_security": "secure_coding"
        }
    
    def analyze_current_structure(self) -> Dict:
        """Analyze current OWASP rule structure"""
        analysis = {
            "owasp_directories": [],
            "rule_counts": {},
            "total_owasp_rules": 0,
            "domain_coverage": {}
        }
        
        if not self.owasp_path.exists():
            print(f"OWASP path {self.owasp_path} does not exist")
            return analysis
        
        # Analyze OWASP subdirectories
        for subdir in self.owasp_path.iterdir():
            if subdir.is_dir():
                owasp_name = subdir.name
                analysis["owasp_directories"].append(owasp_name)
                
                # Count rules in each directory
                rule_files = list(subdir.glob("*.yml"))
                rule_count = len(rule_files)
                analysis["rule_counts"][owasp_name] = rule_count
                analysis["total_owasp_rules"] += rule_count
                
                # Map to domain
                target_domain = self.owasp_to_domain_mapping.get(owasp_name, "unmapped")
                if target_domain not in analysis["domain_coverage"]:
                    analysis["domain_coverage"][target_domain] = []
                analysis["domain_coverage"][target_domain].append({
                    "source": owasp_name,
                    "rules": rule_count
                })
        
        return analysis
    
    def migrate_owasp_to_domains(self, dry_run: bool = True) -> Dict:
        """Migrate OWASP rules to domain-based structure"""
        results = {
            "migrations": [],
            "unmapped_sources": [],
            "errors": []
        }
        
        if not self.owasp_path.exists():
            results["errors"].append(f"OWASP source path does not exist: {self.owasp_path}")
            return results
        
        # Process each OWASP subdirectory
        for source_dir in self.owasp_path.iterdir():
            if not source_dir.is_dir():
                continue
                
            owasp_name = source_dir.name
            target_domain = self.owasp_to_domain_mapping.get(owasp_name)
            
            if not target_domain:
                results["unmapped_sources"].append(owasp_name)
                continue
            
            # Create target domain directory
            target_dir = self.rule_cards_path / target_domain
            if not dry_run:
                target_dir.mkdir(exist_ok=True)
            
            # Migrate rule files
            rule_files = list(source_dir.glob("*.yml"))
            migration_info = {
                "source": owasp_name,
                "target_domain": target_domain,
                "rule_count": len(rule_files),
                "files": []
            }
            
            for rule_file in rule_files:
                target_file = target_dir / rule_file.name
                migration_info["files"].append({
                    "source": str(rule_file),
                    "target": str(target_file),
                    "exists_in_target": target_file.exists() if not dry_run else False
                })
                
                if not dry_run:
                    # Check for conflicts and merge if needed
                    if target_file.exists():
                        # Handle conflict - could implement smart merging here
                        print(f"WARNING: Target exists {target_file}")
                    else:
                        shutil.copy2(rule_file, target_file)
            
            results["migrations"].append(migration_info)
        
        return results
    
    def generate_migration_report(self) -> str:
        """Generate comprehensive migration analysis report"""
        analysis = self.analyze_current_structure()
        
        report = [
            "# OWASP Domain Migration Analysis",
            f"Generated: {os.popen('date -Iseconds').read().strip()}",
            "",
            "## Current Structure Analysis",
            f"- Total OWASP rules: {analysis['total_owasp_rules']}",
            f"- OWASP source directories: {len(analysis['owasp_directories'])}",
            "",
            "## Source to Domain Mapping",
            ""
        ]
        
        for domain, sources in analysis["domain_coverage"].items():
            total_rules = sum(s["rules"] for s in sources)
            report.append(f"### {domain.title().replace('_', ' ')} Domain")
            report.append(f"- Total rules to migrate: {total_rules}")
            for source in sources:
                report.append(f"  - {source['source']}: {source['rules']} rules")
            report.append("")
        
        if "unmapped" in analysis["domain_coverage"]:
            report.extend([
                "## ⚠️ Unmapped Sources",
                ""
            ])
            for source in analysis["domain_coverage"]["unmapped"]:
                report.append(f"- {source['source']}: {source['rules']} rules")
            report.append("")
        
        # Domain directory status
        report.extend([
            "## Domain Directory Status",
            ""
        ])
        
        for domain in self.domain_config.keys():
            domain_dir = self.rule_cards_path / domain
            existing_rules = len(list(domain_dir.glob("*.yml"))) if domain_dir.exists() else 0
            status = "✅ Exists" if domain_dir.exists() else "❌ Missing"
            report.append(f"- {domain}: {status} ({existing_rules} existing rules)")
        
        return "\n".join(report)

def main():
    migrator = OwaspDomainMigrator()
    
    print("=== OWASP Domain Migration Analysis ===")
    analysis = migrator.analyze_current_structure()
    print(f"Found {analysis['total_owasp_rules']} OWASP rules in {len(analysis['owasp_directories'])} source directories")
    
    # Generate detailed report
    report = migrator.generate_migration_report()
    
    # Write report to file
    report_path = "docs/integration_reports/owasp_migration_analysis.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        f.write(report)
    
    print(f"Migration analysis report written to: {report_path}")
    
    # Perform dry run migration
    print("\n=== Dry Run Migration ===")
    migration_results = migrator.migrate_owasp_to_domains(dry_run=True)
    
    print(f"Planned migrations: {len(migration_results['migrations'])}")
    print(f"Unmapped sources: {len(migration_results['unmapped_sources'])}")
    
    if migration_results["unmapped_sources"]:
        print("Unmapped sources:", migration_results["unmapped_sources"])
    
    return report_path

if __name__ == "__main__":
    main()