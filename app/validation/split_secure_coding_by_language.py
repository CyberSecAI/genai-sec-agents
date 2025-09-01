#!/usr/bin/env python3
"""
Split Secure Coding Domain by Programming Language
Splits the secure_coding domain into separate language-specific directories
"""

import os
import yaml
import shutil
from pathlib import Path
from typing import Dict, List

class SecureCodingSplitter:
    def __init__(self, rule_cards_path: str = "app/rule_cards"):
        self.rule_cards_path = Path(rule_cards_path)
        self.secure_coding_path = self.rule_cards_path / "secure_coding"
        self.moves_applied = []
        
        # Language mapping based on rule ID patterns
        self.language_mappings = {
            'nodejs': {
                'patterns': ['NODEJS-', 'NODE-'],
                'directory': 'nodejs',
                'prefix': 'NODE'
            },
            'java': {
                'patterns': ['JAVA-'],
                'directory': 'java', 
                'prefix': 'JAVA'
            },
            'php': {
                'patterns': ['LARAVEL-', 'PHP-'],
                'directory': 'php',
                'prefix': 'PHP'
            }
        }
    
    def split_secure_coding_by_language(self):
        """Split secure_coding domain into language-specific directories"""
        print("=== Splitting Secure Coding by Language ===")
        
        if not self.secure_coding_path.exists():
            print("❌ secure_coding directory not found")
            return []
        
        # Get all YAML files in secure_coding
        yaml_files = list(self.secure_coding_path.glob("*.yml"))
        print(f"Found {len(yaml_files)} secure coding rules")
        
        # Analyze files and categorize by language
        language_files = self.categorize_files_by_language(yaml_files)
        
        # Create language directories and move files
        for language, files in language_files.items():
            if files:
                self.create_language_directory_and_move_files(language, files)
        
        # Remove empty secure_coding directory if all files moved
        remaining_files = list(self.secure_coding_path.glob("*.yml"))
        if not remaining_files:
            print(f"  ✓ Removing empty secure_coding directory")
            self.secure_coding_path.rmdir()
        
        print(f"\n✅ Moved {len(self.moves_applied)} files to language-specific directories")
        return self.moves_applied
    
    def categorize_files_by_language(self, yaml_files: List[Path]) -> Dict[str, List[Path]]:
        """Categorize files by programming language based on rule IDs"""
        language_files = {}
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r') as f:
                    rule_data = yaml.safe_load(f)
                
                if not isinstance(rule_data, dict) or 'id' not in rule_data:
                    print(f"  ⚠️  No ID found in {yaml_file.name}, skipping")
                    continue
                
                rule_id = rule_data['id']
                language = self.determine_language_from_id(rule_id)
                
                if language:
                    if language not in language_files:
                        language_files[language] = []
                    language_files[language].append(yaml_file)
                else:
                    print(f"  ⚠️  Could not determine language for {yaml_file.name} (ID: {rule_id})")
                    
            except Exception as e:
                print(f"  ❌ Error processing {yaml_file.name}: {e}")
        
        return language_files
    
    def determine_language_from_id(self, rule_id: str) -> str:
        """Determine programming language from rule ID"""
        for language, config in self.language_mappings.items():
            for pattern in config['patterns']:
                if pattern in rule_id:
                    return language
        return None
    
    def create_language_directory_and_move_files(self, language: str, files: List[Path]):
        """Create language directory and move files with proper renaming"""
        config = self.language_mappings[language]
        language_dir = self.rule_cards_path / config['directory']
        
        # Create directory if it doesn't exist
        language_dir.mkdir(exist_ok=True)
        print(f"\n  📁 Processing {language} ({len(files)} files)")
        
        # Find existing numbers in target directory
        existing_numbers = self.get_existing_numbers(language_dir, config['prefix'])
        
        for i, yaml_file in enumerate(files, 1):
            try:
                # Find next available number
                new_number = self.find_next_available_number(existing_numbers)
                existing_numbers.add(new_number)
                
                # Generate new filename and ID
                new_filename = f"{config['prefix']}-{new_number:03d}.yml"
                new_id = f"{config['prefix']}-{new_number:03d}"
                new_path = language_dir / new_filename
                
                # Read and update rule data
                with open(yaml_file, 'r') as f:
                    rule_data = yaml.safe_load(f)
                
                old_id = rule_data.get('id', 'unknown')
                rule_data['id'] = new_id
                
                # Write to new location
                with open(new_path, 'w') as f:
                    yaml.dump(rule_data, f, default_flow_style=False, indent=2, sort_keys=False)
                
                # Remove old file
                yaml_file.unlink()
                
                self.moves_applied.append({
                    'language': language,
                    'old_path': str(yaml_file),
                    'new_path': str(new_path),
                    'old_filename': yaml_file.name,
                    'new_filename': new_filename,
                    'old_id': old_id,
                    'new_id': new_id
                })
                
                print(f"    ✓ {yaml_file.name} → {config['directory']}/{new_filename}")
                
            except Exception as e:
                print(f"    ❌ Error moving {yaml_file.name}: {e}")
    
    def get_existing_numbers(self, directory: Path, prefix: str) -> set:
        """Get existing numbers in a directory for a given prefix"""
        existing_numbers = set()
        
        if directory.exists():
            for yaml_file in directory.glob("*.yml"):
                # Extract number from filename
                import re
                match = re.search(rf'{re.escape(prefix)}-(\d+)', yaml_file.stem)
                if match:
                    existing_numbers.add(int(match.group(1)))
        
        return existing_numbers
    
    def find_next_available_number(self, existing_numbers: set) -> int:
        """Find the next available number"""
        number = 1
        while number in existing_numbers:
            number += 1
        return number

def main():
    splitter = SecureCodingSplitter()
    moves = splitter.split_secure_coding_by_language()
    
    if moves:
        print(f"\n=== Summary ===")
        language_counts = {}
        for move in moves:
            language = move['language']
            language_counts[language] = language_counts.get(language, 0) + 1
        
        for language, count in sorted(language_counts.items()):
            print(f"  {language}: {count} rules moved")
            
        print(f"\nTotal: {len(moves)} rules moved")
        
        # Show examples
        print(f"\n=== Examples ===")
        for move in moves[:8]:
            print(f"  {move['old_filename']} → {move['language']}/{move['new_filename']} (ID: {move['new_id']})")
        
        if len(moves) > 8:
            print(f"  ... and {len(moves) - 8} more")
    else:
        print("\n✅ No files to move or secure_coding directory not found!")
    
    return len(moves)

if __name__ == "__main__":
    main()