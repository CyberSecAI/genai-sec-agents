#!/usr/bin/env python3
"""
Count security rules by domain.
Single source of truth for rule counts referenced across documentation.
"""

import os
from pathlib import Path
from collections import defaultdict

def count_rules():
    """Count YAML rule files by domain."""
    rule_cards_dir = Path("app/rule_cards")

    if not rule_cards_dir.exists():
        print(f"Error: {rule_cards_dir} not found")
        return

    domain_counts = defaultdict(int)
    total = 0

    # Count rules in each domain subdirectory
    for domain_dir in sorted(rule_cards_dir.iterdir()):
        if domain_dir.is_dir():
            rule_files = list(domain_dir.glob("*.yml"))
            count = len(rule_files)
            if count > 0:
                domain_counts[domain_dir.name] = count
                total += count

    # Output results
    print(f"# Security Rule Counts (Generated {Path.cwd()})")
    print(f"\n**Total Rules**: {total}")
    print(f"**Total Domains**: {len(domain_counts)}\n")

    print("## Rules by Domain\n")
    print("| Domain | Rule Count |")
    print("|--------|------------|")

    for domain, count in sorted(domain_counts.items(), key=lambda x: -x[1]):
        print(f"| {domain.replace('_', '-')} | {count} |")

    print(f"\n**Last updated**: Run `python3 app/tools/count_rules.py` to regenerate")

if __name__ == "__main__":
    count_rules()
