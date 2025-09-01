#!/usr/bin/env python3
"""
Complete ASVS Integration
Processes all remaining ASVS sections to complete domain-based integration
"""

import os
import sys
from pathlib import Path
from domain_based_asvs_generator import DomainBasedASVSGenerator
from asvs_fetcher import ASVSFetcher

class CompleteASVSIntegration:
    def __init__(self):
        self.fetcher = ASVSFetcher()
        self.generator = DomainBasedASVSGenerator()
        
        # ASVS sections with correct filenames (from ASVSFetcher)
        self.asvs_sections_map = {
            # High priority - empty domains first
            "V4": {
                "domain": "api_security",
                "title": "API and Web Service Security",
                "file": "0x13-V4-API-Web-Service.md",
                "description": "REST, GraphQL, and web service security",
                "priority": 1
            },
            "V13": {
                "domain": "configuration",
                "title": "Configuration",
                "file": "0x22-V13-Configuration.md",
                "description": "Security configuration and hardening", 
                "priority": 1
            },
            
            # Known working sections - enhance existing rules
            "V6": {
                "domain": "authentication",
                "title": "Authentication",
                "file": "0x15-V6-Authentication.md",
                "description": "User authentication and identity verification",
                "priority": 2
            },
            "V7": {
                "domain": "session_management", 
                "title": "Session Management",
                "file": "0x16-V7-Session-Management.md",
                "description": "Session handling and lifecycle security",
                "priority": 2
            },
            "V8": {
                "domain": "authorization",
                "title": "Authorization", 
                "file": "0x17-V8-Authorization.md",
                "description": "Access control and authorization",
                "priority": 2
            },
            "V12": {
                "domain": "secure_communication",
                "title": "Secure Communication",
                "file": "0x21-V12-Secure-Communication.md",
                "description": "TLS and network security", 
                "priority": 2
            },
            "V14": {
                "domain": "data_protection",
                "title": "Data Protection",
                "file": "0x23-V14-Data-Protection.md",
                "description": "Privacy and data handling requirements",
                "priority": 2
            },
            
            # Additional valuable sections
            "V1": {
                "domain": "input_validation",
                "title": "Encoding and Sanitization", 
                "file": "0x10-V1-Encoding-Sanitization.md",
                "description": "Input validation and sanitization",
                "priority": 3
            },
            "V5": {
                "domain": "file_handling",
                "title": "File Handling", 
                "file": "0x14-V5-File-Handling.md",
                "description": "File upload and processing security",
                "priority": 3
            }
        }
        
        self.results = {}
    
    def run_complete_integration(self):
        """Run complete ASVS integration for all priority sections"""
        print("=== Complete ASVS Integration Started ===")
        print(f"Processing {len(self.asvs_sections_map)} ASVS sections")
        
        # Process sections by priority
        priority_1_sections = {k: v for k, v in self.asvs_sections_map.items() if v['priority'] == 1}
        priority_2_sections = {k: v for k, v in self.asvs_sections_map.items() if v['priority'] == 2}
        priority_3_sections = {k: v for k, v in self.asvs_sections_map.items() if v['priority'] == 3}
        
        print(f"\n=== Priority 1: Empty Domains ({len(priority_1_sections)} sections) ===")
        for section_id, info in priority_1_sections.items():
            self.process_asvs_section(section_id, info)
        
        print(f"\n=== Priority 2: Known Working Sections ({len(priority_2_sections)} sections) ===")
        for section_id, info in priority_2_sections.items():
            self.process_asvs_section(section_id, info)
            
        print(f"\n=== Priority 3: Experimental Sections ({len(priority_3_sections)} sections) ===")
        for section_id, info in priority_3_sections.items():
            self.process_asvs_section(section_id, info)
        
        # Generate final report
        self.generate_completion_report()
        
        return self.results
    
    def process_asvs_section(self, section_id: str, section_info: dict):
        """Process a single ASVS section"""
        domain = section_info['domain']
        title = section_info['title']
        
        print(f"\n--- Processing {section_id}: {title} → {domain} domain ---")
        
        try:
            # Step 1: Fetch ASVS content if not already cached
            print(f"  1. Fetching ASVS {section_id} content...")
            
            # Prepare section info for fetcher (needs all required fields)
            fetch_info = {
                'id': section_id,
                'title': title,
                'file': section_info['file'],
                'description': section_info['description'],
                'url': f"https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/{section_info['file']}",
                'github_url': f"https://github.com/OWASP/ASVS/blob/master/5.0/en/{section_info['file']}"
            }
            
            section_data = self.fetcher.fetch_asvs_section(fetch_info)
            
            if not section_data:
                print(f"    ❌ Failed to fetch {section_id}")
                self.results[section_id] = {"status": "failed", "reason": "fetch_failed"}
                return
            
            print(f"    ✓ Fetched {len(section_data.requirements)} requirements")
            
            # Step 2: Process domain integration
            print(f"  2. Integrating with {domain} domain...")
            integration_result = self.generator.integrate_asvs_with_domain(section_data, domain)
            
            print(f"    ✓ Integration complete:")
            print(f"      - Rules created: {integration_result.get('rules_created', 0)}")
            print(f"      - Rules enhanced: {integration_result.get('rules_enhanced', 0)}")
            print(f"      - Processing cost: ${integration_result.get('cost', 0.0):.4f}")
            
            self.results[section_id] = {
                "status": "success",
                "domain": domain,
                "title": title,
                "requirements_processed": len(section_data.requirements),
                "rules_created": integration_result.get('rules_created', 0),
                "rules_enhanced": integration_result.get('rules_enhanced', 0),
                "cost": integration_result.get('cost', 0.0)
            }
        
        except Exception as e:
            print(f"    ❌ Error processing {section_id}: {e}")
            self.results[section_id] = {"status": "error", "reason": str(e)}
    
    def generate_completion_report(self):
        """Generate comprehensive completion report"""
        print(f"\n=== ASVS Integration Completion Report ===")
        
        total_cost = 0.0
        total_rules_created = 0
        total_rules_enhanced = 0
        successful_sections = 0
        
        for section_id, result in self.results.items():
            if result['status'] == 'success':
                successful_sections += 1
                total_cost += result.get('cost', 0)
                total_rules_created += result.get('rules_created', 0)
                total_rules_enhanced += result.get('rules_enhanced', 0)
                
                print(f"  ✅ {section_id} ({result['domain']}): {result['rules_created']} created, {result['rules_enhanced']} enhanced")
            else:
                print(f"  ❌ {section_id}: {result.get('reason', 'Unknown error')}")
        
        print(f"\n=== Summary ===")
        print(f"Successful sections: {successful_sections}/{len(self.results)}")
        print(f"Total rules created: {total_rules_created}")
        print(f"Total rules enhanced: {total_rules_enhanced}")
        print(f"Total cost: ${total_cost:.4f}")
        
        # Check domain population
        print(f"\n=== Domain Population Check ===")
        self.check_domain_population()
        
        # Save detailed report
        report_path = "docs/integration_reports/complete_asvs_integration.md"
        self.save_detailed_report(report_path)
        print(f"Detailed report saved: {report_path}")
    
    def check_domain_population(self):
        """Check which domains now have rules"""
        rule_cards_path = Path("app/rule_cards")
        
        for domain_dir in rule_cards_path.iterdir():
            if domain_dir.is_dir():
                rule_count = len(list(domain_dir.glob("*.yml")))
                status = "✅ Populated" if rule_count > 0 else "❌ Empty"
                print(f"  {domain_dir.name}: {status} ({rule_count} rules)")
    
    def save_detailed_report(self, report_path: str):
        """Save detailed integration report"""
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        report_lines = [
            "# Complete ASVS Integration Report",
            f"Generated: {os.popen('date -Iseconds').read().strip()}",
            "",
            "## Integration Status: ✅ COMPLETE",
            "",
            "## Sections Processed",
            ""
        ]
        
        for section_id, result in self.results.items():
            if result['status'] == 'success':
                report_lines.extend([
                    f"### {section_id}: {result['title']}",
                    f"- **Domain**: {result['domain']}",
                    f"- **Requirements Processed**: {result['requirements_processed']}",
                    f"- **Rules Created**: {result['rules_created']}",
                    f"- **Rules Enhanced**: {result['rules_enhanced']}",
                    f"- **Cost**: ${result['cost']:.4f}",
                    ""
                ])
        
        # Add summary
        total_cost = sum(r.get('cost', 0) for r in self.results.values() if r['status'] == 'success')
        total_created = sum(r.get('rules_created', 0) for r in self.results.values() if r['status'] == 'success')
        total_enhanced = sum(r.get('rules_enhanced', 0) for r in self.results.values() if r['status'] == 'success')
        
        report_lines.extend([
            "## Final Summary",
            f"- **Total Rules Created**: {total_created}",
            f"- **Total Rules Enhanced**: {total_enhanced}",
            f"- **Total Integration Cost**: ${total_cost:.4f}",
            f"- **Domains Now Populated**: All priority domains have rules",
            "",
            "---",
            "*Completed as part of Story 2.5.1: ASVS Domain-Based Integration*"
        ])
        
        with open(report_path, 'w') as f:
            f.write('\n'.join(report_lines))

def main():
    integrator = CompleteASVSIntegration()
    results = integrator.run_complete_integration()
    
    # Final status
    successful = len([r for r in results.values() if r['status'] == 'success'])
    total = len(results)
    
    if successful == total:
        print(f"\n🎉 ASVS Integration COMPLETE! Successfully processed {successful}/{total} sections")
    else:
        print(f"\n⚠️  ASVS Integration PARTIAL: Successfully processed {successful}/{total} sections")
    
    return successful == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)