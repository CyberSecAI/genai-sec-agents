#!/usr/bin/env python3
"""
Execute OWASP Domain Migration
Performs the actual migration from source-based to domain-based Rule Cards
Part of Story 2.5.1: ASVS Domain-Based Integration - Phase 2
"""

import os
import shutil
from pathlib import Path
from owasp_domain_migration import OwaspDomainMigrator

def execute_migration():
    """Execute the OWASP to domain migration"""
    migrator = OwaspDomainMigrator()
    
    print("=== Executing OWASP Domain Migration ===")
    
    # Create missing domain directories first
    print("Creating missing domain directories...")
    missing_domains = [
        "input_validation", "api_security", "secure_communication", 
        "web_security", "file_handling", "configuration", "logging", "secure_coding"
    ]
    
    for domain in missing_domains:
        domain_dir = migrator.rule_cards_path / domain
        domain_dir.mkdir(exist_ok=True)
        print(f"  ✓ Created {domain_dir}")
    
    # Execute actual migration
    print("\nMigrating OWASP rules to domains...")
    migration_results = migrator.migrate_owasp_to_domains(dry_run=False)
    
    # Report results
    print(f"\n=== Migration Results ===")
    print(f"Successful migrations: {len(migration_results['migrations'])}")
    print(f"Unmapped sources: {len(migration_results['unmapped_sources'])}")
    print(f"Errors: {len(migration_results['errors'])}")
    
    if migration_results["errors"]:
        print("Errors:")
        for error in migration_results["errors"]:
            print(f"  ❌ {error}")
    
    # Detailed migration summary
    total_migrated = 0
    for migration in migration_results["migrations"]:
        total_migrated += migration["rule_count"]
        print(f"  ✓ {migration['source']} → {migration['target_domain']} ({migration['rule_count']} rules)")
    
    print(f"\nTotal rules migrated: {total_migrated}")
    
    # Verify migration
    print("\n=== Post-Migration Verification ===")
    for domain in missing_domains:
        domain_dir = migrator.rule_cards_path / domain
        rule_count = len(list(domain_dir.glob("*.yml")))
        print(f"  {domain}: {rule_count} rules")
    
    print("\n✅ Migration completed successfully!")
    return migration_results

if __name__ == "__main__":
    execute_migration()