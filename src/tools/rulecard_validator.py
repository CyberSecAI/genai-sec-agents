#!/usr/bin/env python3
# This script validates all Rule Card YAML files in the `rule_cards` directory.
# It checks for required fields and ensures there are no duplicate rule IDs.

import sys
import glob
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
RULE_DIR = ROOT / "rule_cards"

# These fields are required for a Rule Card to be considered valid.
REQUIRED_FIELDS = [
    "id", "title", "scope", "requirement", "do", "dont", "detect", "verify", "refs", "license"
]


def main():
    """Main entry point for the validator script."""
    files = glob.glob(str(RULE_DIR / "**" / "*.yml"), recursive=True)
    ids = set()
    errors = 0
    for fp in files:
        p = Path(fp)
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("YAML must be a mapping")
            missing = [k for k in REQUIRED_FIELDS if k not in data]
            if missing:
                raise ValueError(f"Missing fields: {missing}")
            rid = data["id"]
            if rid in ids:
                raise ValueError(f"Duplicate rule id: {rid}")
            ids.add(rid)
        except Exception as e:
            errors += 1
            print(f"[ERROR] {p}: {e}")
    if errors:
        print(f"Validation failed with {errors} error(s)")
        sys.exit(1)
    print(f"Validated {len(files)} rule card(s). All good.")


if __name__ == "__main__":
    main()
