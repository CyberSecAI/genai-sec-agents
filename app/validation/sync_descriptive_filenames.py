#!/usr/bin/env python3
"""
Sync Descriptive Filenames with Rule IDs
Updates filenames to match existing descriptive rule IDs
"""

import os
import yaml
import re
from pathlib import Path
from typing import Dict, List

class DescriptiveFilenameSyncer:
    def __init__(self, rule_cards_path: str = "app/rule_cards"):
        self.rule_cards_path = Path(rule_cards_path)
        self.syncs_applied = []
    
    def sync_all_descriptive_filenames(self):
        """Sync filenames with existing descriptive IDs"""
        print("=== Syncing Descriptive Filenames with Rule IDs ===")
        
        total_synced = 0
        for domain_path in self.rule_cards_path.iterdir():
            if domain_path.is_dir():
                domain = domain_path.name
                print(f"\n📁 Processing domain: {domain}")
                synced = self.sync_domain_filenames(domain_path, domain)
                total_synced += synced
        
        print(f"\n✅ Synced {len(self.syncs_applied)} filenames with descriptive IDs")
        return self.syncs_applied
    
    def sync_domain_filenames(self, domain_path: Path, domain: str) -> int:
        """Sync filenames for all rules in a domain"""
        yaml_files = list(domain_path.glob("*.yml"))
        synced = 0
        
        for yaml_file in yaml_files:
            if self.needs_filename_sync(yaml_file):
                self.sync_filename_with_id(yaml_file, domain)
                synced += 1
        
        print(f"  {synced}/{len(yaml_files)} files synced")
        return synced
    
    def needs_filename_sync(self, yaml_file: Path) -> bool:
        """Check if filename needs to be synced with descriptive ID"""
        try:
            with open(yaml_file, 'r') as f:
                rule_data = yaml.safe_load(f)
            
            if not isinstance(rule_data, dict) or 'id' not in rule_data:
                return False
            
            rule_id = rule_data['id']
            current_filename = yaml_file.stem  # filename without .yml
            expected_filename = rule_id
            
            # Check if ID is descriptive (not just PREFIX-XXX format)
            if self.is_descriptive_id(rule_id) and current_filename != expected_filename:
                return True
                
            return False
            
        except:
            return False
    
    def is_descriptive_id(self, rule_id: str) -> bool:
        """Check if rule ID is descriptive (has meaningful words)"""
        # Descriptive IDs have more than just prefix and numbers
        # They contain meaningful words like INPUT-VALIDATION-001, XSS-PREVENTION-001, etc.
        
        # Generic patterns to exclude: PREFIX-XXX, PREFIX-XX-XXX
        if re.match(r'^[A-Z]+-\d+$', rule_id) or re.match(r'^[A-Z]+-\d+-\d+$', rule_id):
            return False
        
        # Look for meaningful words (more than 2 consecutive letters)
        meaningful_parts = re.findall(r'[A-Z]{3,}', rule_id)
        return len(meaningful_parts) >= 2  # Should have prefix + at least one meaningful word
    
    def sync_filename_with_id(self, yaml_file: Path, domain: str):
        """Sync filename with the descriptive rule ID"""
        try:
            with open(yaml_file, 'r') as f:
                rule_data = yaml.safe_load(f)
            
            rule_id = rule_data['id']
            new_filename = f"{rule_id}.yml"
            new_path = yaml_file.parent / new_filename
            
            # Check if target already exists
            if new_path.exists() and new_path != yaml_file:
                print(f"  ⚠️  Target exists: {new_filename}, skipping")
                return
            
            # Rename the file
            yaml_file.rename(new_path)
            
            self.syncs_applied.append({
                'domain': domain,
                'old_filename': yaml_file.name,
                'new_filename': new_filename,
                'rule_id': rule_id
            })
            
            print(f"  ✓ {yaml_file.name} → {new_filename}")
            
        except Exception as e:
            print(f"  ❌ Error syncing {yaml_file.name}: {e}")

def main():
    syncer = DescriptiveFilenameSyncer()
    syncs = syncer.sync_all_descriptive_filenames()
    
    if syncs:
        print(f"\n=== Summary ===")
        domain_counts = {}
        for sync in syncs:
            domain = sync['domain']
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        for domain, count in sorted(domain_counts.items()):
            print(f"  {domain}: {count} files synced")
            
        print(f"\nTotal: {len(syncs)} filenames synced with descriptive IDs")
        
        # Show examples
        print(f"\n=== Examples ===")
        for sync in syncs[:10]:
            print(f"  {sync['old_filename']} → {sync['new_filename']}")
            print(f"    ID: {sync['rule_id']}")
        
        if len(syncs) > 10:
            print(f"  ... and {len(syncs) - 10} more")
    else:
        print("\n✅ All filenames already match their descriptive IDs!")
    
    return len(syncs)

if __name__ == "__main__":
    main()