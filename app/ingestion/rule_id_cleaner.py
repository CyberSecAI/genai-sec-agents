#!/usr/bin/env python3
"""
Rule ID Cleaner

Cleans up rule files with problematic naming patterns like "(existing ID)"
and assigns proper sequential IDs while checking for duplicates.
"""

import os
import yaml
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RuleIdCleaner:
    """Cleans up rule IDs and removes duplicates."""
    
    def __init__(self, rule_cards_root: Path = Path("app/rule_cards")):
        self.rule_cards_root = rule_cards_root
        
    def find_problematic_files(self) -> List[Path]:
        """Find all files with problematic naming patterns."""
        problematic_patterns = ["existing", "duplicate", "enhanced", "(", ")"]
        problematic_files = []
        
        for pattern in ["*.yml", "*.yaml"]:
            for file_path in self.rule_cards_root.rglob(pattern):
                filename = file_path.name.lower()
                if any(prob_pattern in filename for prob_pattern in problematic_patterns):
                    problematic_files.append(file_path)
        
        return problematic_files
    
    def load_rule_content(self, file_path: Path) -> Dict:
        """Load rule content from YAML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            return {}
    
    def get_content_hash(self, rule_data: Dict) -> str:
        """Generate SHA-256 hash of rule content (excluding ID) for duplicate detection."""
        # Create a copy without the ID field for comparison
        content_for_hash = rule_data.copy()
        content_for_hash.pop('id', None)
        
        # Convert to string and hash with SHA-256 (secure cryptographic hash)
        content_str = str(sorted(content_for_hash.items()))
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    def find_duplicates_in_domain(self, domain_path: Path) -> Dict[str, List[Path]]:
        """Find duplicate rules within a domain based on content."""
        content_hashes = {}
        duplicates = {}
        
        for file_path in domain_path.glob("*.yml"):
            if file_path.name.startswith('.'):
                continue
                
            rule_data = self.load_rule_content(file_path)
            if not rule_data:
                continue
                
            content_hash = self.get_content_hash(rule_data)
            
            if content_hash in content_hashes:
                # Found duplicate
                if content_hash not in duplicates:
                    duplicates[content_hash] = [content_hashes[content_hash]]
                duplicates[content_hash].append(file_path)
            else:
                content_hashes[content_hash] = file_path
        
        return duplicates
    
    def get_next_rule_id(self, domain: str, existing_ids: Set[str]) -> str:
        """Generate next available rule ID for domain."""
        domain_prefix = domain.upper().replace('_', '-')
        
        # Find the highest existing number
        max_num = 0
        for existing_id in existing_ids:
            if existing_id.startswith(domain_prefix):
                # Extract number from ID like "AUTH-001" or "AUTH-06-006"
                parts = existing_id.replace(domain_prefix + '-', '').split('-')
                try:
                    for part in parts:
                        if part.isdigit():
                            max_num = max(max_num, int(part))
                except:
                    continue
        
        # Return next sequential ID
        next_num = max_num + 1
        return f"{domain_prefix}-{next_num:03d}"
    
    def clean_rule_id_in_content(self, rule_data: Dict, new_id: str) -> Dict:
        """Clean the rule ID within the rule content."""
        rule_data = rule_data.copy()
        rule_data['id'] = new_id
        return rule_data
    
    def save_cleaned_rule(self, rule_data: Dict, output_path: Path) -> bool:
        """Save cleaned rule to new file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(rule_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            return True
        except Exception as e:
            logger.error(f"Failed to save rule to {output_path}: {e}")
            return False
    
    def clean_domain_rules(self, domain_path: Path, dry_run: bool = True) -> Dict:
        """Clean all rules in a domain directory."""
        domain_name = domain_path.name
        logger.info(f"Cleaning rules in {domain_name} domain (dry_run={dry_run})")
        
        results = {
            'domain': domain_name,
            'problematic_files': [],
            'duplicates_removed': [],
            'renamed_files': [],
            'errors': []
        }
        
        # Find problematic files in this domain
        problematic_files = []
        for file_path in domain_path.glob("*.yml"):
            if any(pattern in file_path.name.lower() for pattern in ["existing", "duplicate", "enhanced", "(", ")"]):
                problematic_files.append(file_path)
        
        results['problematic_files'] = [str(p) for p in problematic_files]
        
        if not problematic_files:
            logger.info(f"No problematic files found in {domain_name}")
            return results
        
        # Find duplicates
        duplicates = self.find_duplicates_in_domain(domain_path)
        
        # Get all existing clean IDs
        existing_ids = set()
        for file_path in domain_path.glob("*.yml"):
            if not any(pattern in file_path.name.lower() for pattern in ["existing", "duplicate", "enhanced", "(", ")"]):
                rule_data = self.load_rule_content(file_path)
                if rule_data and 'id' in rule_data:
                    existing_ids.add(rule_data['id'])
        
        # Process duplicates first - keep the first one, remove others
        files_to_remove = set()
        for content_hash, duplicate_files in duplicates.items():
            # Keep the first file, mark others for removal
            for file_to_remove in duplicate_files[1:]:
                files_to_remove.add(file_to_remove)
                results['duplicates_removed'].append(str(file_to_remove))
                logger.info(f"Marked duplicate for removal: {file_to_remove.name}")
        
        # Process remaining problematic files
        for file_path in problematic_files:
            if file_path in files_to_remove:
                continue  # Skip files marked for duplicate removal
                
            rule_data = self.load_rule_content(file_path)
            if not rule_data:
                results['errors'].append(f"Could not load {file_path}")
                continue
            
            # Generate new clean ID
            new_id = self.get_next_rule_id(domain_name, existing_ids)
            existing_ids.add(new_id)
            
            # Clean the rule content
            cleaned_rule = self.clean_rule_id_in_content(rule_data, new_id)
            
            # Create new filename
            new_filename = f"{new_id}.yml"
            new_file_path = domain_path / new_filename
            
            if not dry_run:
                # Save cleaned rule
                if self.save_cleaned_rule(cleaned_rule, new_file_path):
                    # Remove old file
                    file_path.unlink()
                    results['renamed_files'].append({
                        'old': str(file_path),
                        'new': str(new_file_path),
                        'new_id': new_id
                    })
                    logger.info(f"Renamed {file_path.name} -> {new_filename} (ID: {new_id})")
                else:
                    results['errors'].append(f"Failed to save cleaned rule: {new_file_path}")
            else:
                results['renamed_files'].append({
                    'old': str(file_path),
                    'new': str(new_file_path),
                    'new_id': new_id
                })
                logger.info(f"DRY RUN: Would rename {file_path.name} -> {new_filename} (ID: {new_id})")
        
        # Remove duplicate files
        if not dry_run:
            for file_to_remove in files_to_remove:
                try:
                    file_to_remove.unlink()
                    logger.info(f"Removed duplicate: {file_to_remove.name}")
                except Exception as e:
                    results['errors'].append(f"Failed to remove duplicate {file_to_remove}: {e}")
        else:
            for file_to_remove in files_to_remove:
                logger.info(f"DRY RUN: Would remove duplicate: {file_to_remove.name}")
        
        return results
    
    def clean_all_domains(self, dry_run: bool = True) -> Dict:
        """Clean rules in all domains."""
        logger.info(f"Starting rule ID cleanup (dry_run={dry_run})")
        
        overall_results = {
            'total_problematic': 0,
            'total_duplicates': 0,
            'total_renamed': 0,
            'total_errors': 0,
            'domain_results': {}
        }
        
        for domain_path in self.rule_cards_root.iterdir():
            if not domain_path.is_dir() or domain_path.name.startswith('.'):
                continue
                
            domain_results = self.clean_domain_rules(domain_path, dry_run)
            overall_results['domain_results'][domain_path.name] = domain_results
            
            # Update totals
            overall_results['total_problematic'] += len(domain_results['problematic_files'])
            overall_results['total_duplicates'] += len(domain_results['duplicates_removed'])
            overall_results['total_renamed'] += len(domain_results['renamed_files'])
            overall_results['total_errors'] += len(domain_results['errors'])
        
        return overall_results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean up rule IDs and remove duplicates")
    parser.add_argument("--execute", action="store_true", help="Execute cleanup (default is dry run)")
    parser.add_argument("--domain", help="Clean specific domain only")
    
    args = parser.parse_args()
    
    cleaner = RuleIdCleaner()
    
    if args.domain:
        domain_path = cleaner.rule_cards_root / args.domain
        if not domain_path.exists():
            print(f"❌ Domain directory {args.domain} does not exist")
            return
        
        results = cleaner.clean_domain_rules(domain_path, dry_run=not args.execute)
        
        print(f"\n📊 Cleanup Results for {args.domain}:")
        print(f"   - Problematic files: {len(results['problematic_files'])}")
        print(f"   - Duplicates removed: {len(results['duplicates_removed'])}")
        print(f"   - Files renamed: {len(results['renamed_files'])}")
        print(f"   - Errors: {len(results['errors'])}")
        
    else:
        results = cleaner.clean_all_domains(dry_run=not args.execute)
        
        print(f"\n📊 Overall Cleanup Results:")
        print(f"   - Total problematic files: {results['total_problematic']}")
        print(f"   - Total duplicates removed: {results['total_duplicates']}")
        print(f"   - Total files renamed: {results['total_renamed']}")
        print(f"   - Total errors: {results['total_errors']}")
        
        if results['domain_results']:
            print(f"\n📋 Domain Breakdown:")
            for domain, domain_results in results['domain_results'].items():
                if domain_results['problematic_files'] or domain_results['duplicates_removed'] or domain_results['renamed_files']:
                    print(f"   {domain}: {len(domain_results['problematic_files'])} problematic, "
                          f"{len(domain_results['duplicates_removed'])} duplicates, "
                          f"{len(domain_results['renamed_files'])} renamed")
    
    if not args.execute:
        print(f"\n💡 This was a DRY RUN. Use --execute to perform actual cleanup.")

if __name__ == "__main__":
    main()