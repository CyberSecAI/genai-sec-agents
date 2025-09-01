"""
Domain mapping validation and documentation generator.

Validates the domain mapping configuration and generates documentation
for the domain-based Rule Card organization system.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from .domain_mapping import DOMAIN_MAPPINGS, validate_domain_mapping, get_all_domains

def generate_domain_taxonomy_documentation() -> str:
    """Generate comprehensive domain taxonomy documentation."""
    doc = """# Security Domain Taxonomy

## Overview
This document defines the comprehensive domain mapping for organizing Rule Cards by security topic rather than by source standard (OWASP, ASVS, etc.).

## Domain Mapping Configuration

"""
    
    # Group domains by priority
    priority_groups = {1: [], 2: [], 3: []}
    for domain, mapping in DOMAIN_MAPPINGS.items():
        priority_groups[mapping.priority].append((domain, mapping))
    
    for priority in [1, 2, 3]:
        priority_name = {1: "Core Security Domains", 2: "Specialized Domains", 3: "Advanced Topics"}[priority]
        doc += f"### Priority {priority} - {priority_name}\n\n"
        
        for domain, mapping in priority_groups[priority]:
            doc += f"**{domain}**\n"
            doc += f"- Description: {mapping.description}\n"
            doc += f"- ASVS Sections: {', '.join(mapping.asvs_sections)}\n"
            doc += f"- OWASP Topics: {', '.join(mapping.owasp_topics)}\n"
            doc += f"- Directory: `app/rule_cards/{domain}/`\n\n"
    
    # Validation results
    validation_results = validate_domain_mapping()
    doc += "## Validation Results\n\n"
    
    if not validation_results['missing_sections'] and not validation_results['duplicate_sections']:
        doc += "✅ All ASVS sections V1-V17 are properly mapped with no duplicates.\n\n"
    else:
        if validation_results['missing_sections']:
            doc += f"❌ Missing ASVS sections: {', '.join(validation_results['missing_sections'])}\n"
        if validation_results['duplicate_sections']:
            doc += f"❌ Duplicate ASVS sections: {', '.join(validation_results['duplicate_sections'])}\n"
        doc += "\n"
    
    # Domain statistics  
    doc += "## Domain Statistics\n\n"
    doc += f"- Total domains: {len(DOMAIN_MAPPINGS)}\n"
    doc += f"- Priority 1 domains: {len(priority_groups[1])}\n"
    doc += f"- Priority 2 domains: {len(priority_groups[2])}\n"
    doc += f"- Priority 3 domains: {len(priority_groups[3])}\n"
    doc += f"- Total ASVS sections covered: {sum(len(m.asvs_sections) for m in DOMAIN_MAPPINGS.values())}\n\n"
    
    return doc

def generate_domain_migration_plan() -> str:
    """Generate migration plan for existing OWASP rules to domain structure."""
    plan = """# Domain Migration Plan

## Overview
Migration strategy for reorganizing existing source-based Rule Cards to domain-based structure.

## Current State
```
app/rule_cards/
├── owasp/          # 46 OWASP-generated rules
├── asvs/           # To be removed (replaced by domain integration)  
└── cryptography/   # 1 existing rule + 11 ASVS integrated rules (proof of concept)
```

## Target State
```
app/rule_cards/
"""
    
    # Add domain directories
    for domain in sorted(get_all_domains()):
        plan += f"├── {domain}/\n"
    
    plan += """```

## Migration Steps

### Phase 1: OWASP Rule Analysis and Mapping
1. Analyze existing OWASP rules to determine domain mapping
2. Create mapping file: `owasp_rule_to_domain_mapping.json`
3. Validate no rules are lost during mapping

### Phase 2: Domain-by-Domain Migration
"""
    
    # Add migration steps for each priority level
    priority_groups = {1: [], 2: [], 3: []}
    for domain, mapping in DOMAIN_MAPPINGS.items():
        priority_groups[mapping.priority].append(domain)
    
    for priority in [1, 2, 3]:
        plan += f"\n**Priority {priority} Domains:**\n"
        for domain in sorted(priority_groups[priority]):
            plan += f"- Migrate rules to `app/rule_cards/{domain}/`\n"
    
    plan += """
### Phase 3: Validation and Cleanup
1. Validate all original rules successfully migrated
2. Update semantic search corpus paths
3. Remove source-based directories (`app/rule_cards/owasp/`, `app/rule_cards/asvs/`)
4. Update documentation and tooling references

## Rollback Plan
1. Backup created before migration in `app/rule_cards/.backup/`
2. Git branch protection ensures full history preservation
3. Validation scripts verify no data loss at each step
"""
    
    return plan

def save_documentation(output_dir: Path = Path("docs/domain_taxonomy/")):
    """Save generated documentation to files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save taxonomy documentation
    taxonomy_doc = generate_domain_taxonomy_documentation()
    with open(output_dir / "domain_taxonomy.md", "w", encoding="utf-8") as f:
        f.write(taxonomy_doc)
    
    # Save migration plan
    migration_plan = generate_domain_migration_plan()
    with open(output_dir / "migration_plan.md", "w", encoding="utf-8") as f:
        f.write(migration_plan)
    
    # Save machine-readable domain mapping
    domain_config = {}
    for domain, mapping in DOMAIN_MAPPINGS.items():
        domain_config[domain] = {
            "asvs_sections": mapping.asvs_sections,
            "owasp_topics": mapping.owasp_topics,
            "description": mapping.description,
            "priority": mapping.priority
        }
    
    with open(output_dir / "domain_mapping.json", "w", encoding="utf-8") as f:
        json.dump(domain_config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Documentation saved to {output_dir}")
    print(f"   - domain_taxonomy.md: Comprehensive domain mapping")
    print(f"   - migration_plan.md: Migration strategy")
    print(f"   - domain_mapping.json: Machine-readable configuration")

if __name__ == "__main__":
    save_documentation()