#!/usr/bin/env python3
"""
Duplicate Rule Detection and Deduplication
Detects and resolves duplicate rules with similar names or content
"""

import os
import yaml
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any
from difflib import SequenceMatcher
import json

class DuplicateRuleDetector:
    def __init__(self, rule_cards_path: str = "app/rule_cards"):
        self.rule_cards_path = Path(rule_cards_path)
        self.rules_data = {}
        self.duplicates_found = []
        self.recommendations = []
    
    def analyze_all_duplicates(self):
        """Analyze all rules for duplicates and naming issues"""
        print("=== Duplicate Rule Analysis Started ===")
        
        # Load all rules
        self.load_all_rules()
        
        # Detect different types of duplicates
        self.detect_naming_inconsistencies()
        self.detect_content_similarity()
        self.detect_id_mismatches()
        
        # Generate recommendations
        self.generate_deduplication_recommendations()
        
        return self.generate_analysis_report()
    
    def load_all_rules(self):
        """Load all rule cards into memory for analysis"""
        yaml_files = list(self.rule_cards_path.rglob("*.yml"))
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r') as f:
                    rule_data = yaml.safe_load(f)
                
                if isinstance(rule_data, dict) and 'id' in rule_data:
                    self.rules_data[str(yaml_file)] = {
                        'file_path': yaml_file,
                        'rule_data': rule_data,
                        'domain': yaml_file.parent.name
                    }
            except Exception as e:
                print(f"Error loading {yaml_file}: {e}")
                continue
        
        print(f"Loaded {len(self.rules_data)} rules for analysis")
    
    def detect_naming_inconsistencies(self):
        """Detect rules with similar names but different content"""
        print("\n=== Detecting Naming Inconsistencies ===")
        
        # Group by domain for analysis
        domains = {}
        for file_path, rule_info in self.rules_data.items():
            domain = rule_info['domain']
            if domain not in domains:
                domains[domain] = []
            domains[domain].append((file_path, rule_info))
        
        for domain, rules in domains.items():
            if len(rules) <= 1:
                continue
            
            print(f"\nAnalyzing {domain} domain ({len(rules)} rules):")
            
            # Look for similar filenames
            filenames = [(rule[0], Path(rule[0]).name) for rule in rules]
            
            for i, (path1, name1) in enumerate(filenames):
                for j, (path2, name2) in enumerate(filenames[i+1:], i+1):
                    similarity = self.calculate_name_similarity(name1, name2)
                    
                    if similarity > 0.7:  # High name similarity threshold
                        rule1_data = self.rules_data[path1]['rule_data']
                        rule2_data = self.rules_data[path2]['rule_data']
                        
                        content_similarity = self.calculate_content_similarity(rule1_data, rule2_data)
                        
                        duplicate_info = {
                            'type': 'naming_inconsistency',
                            'domain': domain,
                            'file1': name1,
                            'file2': name2,
                            'path1': path1,
                            'path2': path2,
                            'name_similarity': similarity,
                            'content_similarity': content_similarity,
                            'rule1_id': rule1_data.get('id', 'N/A'),
                            'rule2_id': rule2_data.get('id', 'N/A'),
                            'rule1_title': rule1_data.get('title', 'N/A'),
                            'rule2_title': rule2_data.get('title', 'N/A')
                        }
                        
                        self.duplicates_found.append(duplicate_info)
                        
                        print(f"  🔍 Similar names: {name1} <-> {name2} (name: {similarity:.2f}, content: {content_similarity:.2f})")
                        print(f"      Titles: '{rule1_data.get('title', 'N/A')[:50]}' vs '{rule2_data.get('title', 'N/A')[:50]}'")
    
    def detect_content_similarity(self):
        """Detect rules with similar content regardless of names"""
        print("\n=== Detecting Content Similarity ===")
        
        # Group by domain
        domains = {}
        for file_path, rule_info in self.rules_data.items():
            domain = rule_info['domain']
            if domain not in domains:
                domains[domain] = []
            domains[domain].append((file_path, rule_info))
        
        for domain, rules in domains.items():
            if len(rules) <= 1:
                continue
            
            print(f"\nAnalyzing {domain} domain content similarity:")
            
            for i, (path1, rule_info1) in enumerate(rules):
                for j, (path2, rule_info2) in enumerate(rules[i+1:], i+1):
                    content_similarity = self.calculate_content_similarity(
                        rule_info1['rule_data'], 
                        rule_info2['rule_data']
                    )
                    
                    if content_similarity > 0.6:  # High content similarity threshold
                        name1 = Path(path1).name
                        name2 = Path(path2).name
                        
                        duplicate_info = {
                            'type': 'content_similarity',
                            'domain': domain,
                            'file1': name1,
                            'file2': name2,
                            'path1': path1,
                            'path2': path2,
                            'content_similarity': content_similarity,
                            'rule1_id': rule_info1['rule_data'].get('id', 'N/A'),
                            'rule2_id': rule_info2['rule_data'].get('id', 'N/A'),
                            'rule1_title': rule_info1['rule_data'].get('title', 'N/A'),
                            'rule2_title': rule_info2['rule_data'].get('title', 'N/A')
                        }
                        
                        self.duplicates_found.append(duplicate_info)
                        
                        print(f"  📋 Similar content: {name1} <-> {name2} (similarity: {content_similarity:.2f})")
                        print(f"      Titles: '{rule_info1['rule_data'].get('title', 'N/A')[:50]}' vs '{rule_info2['rule_data'].get('title', 'N/A')[:50]}'")
    
    def detect_id_mismatches(self):
        """Detect cases where filename doesn't match rule ID"""
        print("\n=== Detecting ID Mismatches ===")
        
        mismatches = []
        for file_path, rule_info in self.rules_data.items():
            filename = Path(file_path).stem  # Remove .yml extension
            rule_id = rule_info['rule_data'].get('id', '')
            
            if filename != rule_id:
                mismatch_info = {
                    'type': 'id_mismatch',
                    'file_path': file_path,
                    'filename': filename,
                    'rule_id': rule_id,
                    'domain': rule_info['domain']
                }
                mismatches.append(mismatch_info)
                print(f"  ⚠️  ID mismatch: {filename} != {rule_id}")
        
        self.duplicates_found.extend(mismatches)
        return mismatches
    
    def calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two filenames"""
        return SequenceMatcher(None, name1.lower(), name2.lower()).ratio()
    
    def calculate_content_similarity(self, rule1: Dict, rule2: Dict) -> float:
        """Calculate similarity between rule content"""
        # Compare key fields
        fields_to_compare = ['title', 'requirement', 'do', 'dont']
        similarities = []
        
        for field in fields_to_compare:
            text1 = str(rule1.get(field, ''))
            text2 = str(rule2.get(field, ''))
            
            if text1 and text2:
                similarity = SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
                similarities.append(similarity)
        
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def generate_deduplication_recommendations(self):
        """Generate recommendations for resolving duplicates"""
        print("\n=== Generating Deduplication Recommendations ===")
        
        # Group duplicates by type
        naming_issues = [d for d in self.duplicates_found if d['type'] == 'naming_inconsistency']
        content_issues = [d for d in self.duplicates_found if d['type'] == 'content_similarity'] 
        id_mismatches = [d for d in self.duplicates_found if d['type'] == 'id_mismatch']
        
        # Session management specific recommendations
        session_naming_issues = [d for d in naming_issues if d['domain'] == 'session_management']
        if session_naming_issues:
            self.recommendations.append({
                'domain': 'session_management',
                'issue': 'naming_inconsistency',
                'recommendation': 'Standardize naming to SESSION-MANAGEMENT-XXX format',
                'action': 'rename_files',
                'files_affected': len([d for d in self.duplicates_found if d.get('domain') == 'session_management']),
                'specific_actions': [
                    'Rename SESSION_MANAGEMENT-* files to SESSION-MANAGEMENT-*',
                    'Update rule IDs to match new filenames',
                    'Review content to ensure no actual duplicates exist'
                ]
            })
        
        # Node.js security recommendations
        nodejs_content_issues = [d for d in content_issues if d['domain'] == 'secure_coding' and 'NODEJS' in d['file1']]
        if nodejs_content_issues:
            self.recommendations.append({
                'domain': 'secure_coding',
                'issue': 'nodejs_duplication',
                'recommendation': 'Consolidate Node.js security rules',
                'action': 'merge_and_deduplicate',
                'files_affected': len(set([d['file1'] for d in nodejs_content_issues] + [d['file2'] for d in nodejs_content_issues])),
                'specific_actions': [
                    'Review NODEJS-SECURITY-* vs NODEJS-APPLICATION-SECURITY-* rules',
                    'Merge complementary content where appropriate',
                    'Remove true duplicates',
                    'Standardize naming convention'
                ]
            })
        
        print(f"Generated {len(self.recommendations)} recommendations")
    
    def generate_analysis_report(self) -> Dict:
        """Generate comprehensive duplicate analysis report"""
        report = {
            'analysis_summary': {
                'total_rules_analyzed': len(self.rules_data),
                'duplicates_found': len(self.duplicates_found),
                'naming_inconsistencies': len([d for d in self.duplicates_found if d['type'] == 'naming_inconsistency']),
                'content_similarities': len([d for d in self.duplicates_found if d['type'] == 'content_similarity']),
                'id_mismatches': len([d for d in self.duplicates_found if d['type'] == 'id_mismatch']),
                'recommendations_generated': len(self.recommendations)
            },
            'duplicates': self.duplicates_found,
            'recommendations': self.recommendations,
            'domain_analysis': self.generate_domain_summary()
        }
        
        return report
    
    def generate_domain_summary(self) -> Dict:
        """Generate per-domain duplicate analysis"""
        domain_summary = {}
        
        for file_path, rule_info in self.rules_data.items():
            domain = rule_info['domain']
            if domain not in domain_summary:
                domain_summary[domain] = {
                    'total_rules': 0,
                    'duplicates': 0,
                    'issues': []
                }
            domain_summary[domain]['total_rules'] += 1
        
        for duplicate in self.duplicates_found:
            if 'domain' in duplicate:
                domain = duplicate['domain']
                if domain in domain_summary:
                    domain_summary[domain]['duplicates'] += 1
                    domain_summary[domain]['issues'].append(duplicate['type'])
        
        return domain_summary

def main():
    detector = DuplicateRuleDetector()
    report = detector.analyze_all_duplicates()
    
    # Print summary
    summary = report['analysis_summary']
    print(f"\n=== Analysis Complete ===")
    print(f"Total rules analyzed: {summary['total_rules_analyzed']}")
    print(f"Duplicates/issues found: {summary['duplicates_found']}")
    print(f"  - Naming inconsistencies: {summary['naming_inconsistencies']}")
    print(f"  - Content similarities: {summary['content_similarities']}")
    print(f"  - ID mismatches: {summary['id_mismatches']}")
    print(f"Recommendations: {summary['recommendations_generated']}")
    
    # Save detailed report
    report_path = "docs/validation_reports/duplicate_analysis_report.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\nDetailed report saved to: {report_path}")
    
    return report

if __name__ == "__main__":
    main()