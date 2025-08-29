#!/usr/bin/env python3
# This script compiles human-readable YAML Rule Cards into machine-readable JSON agent packages.
# It reads the manifest, collects rule files by topic, validates them, and builds the final JSON output.

import argparse
import datetime as dt
import glob
import hashlib
import json
import os
from pathlib import Path
from typing import Dict, List, Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
RULE_DIR = ROOT / "rule_cards"

# These fields are required for a Rule Card to be considered valid.
REQUIRED_FIELDS = [
    "id", "title", "scope", "requirement", "do", "dont", "detect", "verify", "refs", "license"
]


def load_yaml(path: Path) -> Any:
    """Loads a YAML file from the given path."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def collect_rule_files(topic: str) -> List[Path]:
    """Collects all .yml rule files for a given topic recursively."""
    # topic like "docker" or "jwt/java" -> expand to rule_cards/<topic>/**.yml
    pattern = str(RULE_DIR / topic / "**" / "*.yml")
    return [Path(p) for p in glob.glob(pattern, recursive=True)]


def validate_rule_schema(rule: Dict[str, Any], path: Path) -> None:
    """Validates that a rule card contains all required fields and correct types."""
    missing = [k for k in REQUIRED_FIELDS if k not in rule]
    if missing:
        raise ValueError(f"Missing fields {missing} in {path}")
    if not isinstance(rule.get("do", []), list) or not isinstance(rule.get("dont", []), list):
        raise ValueError(f"'do' and 'dont' must be lists in {path}")
    if not isinstance(rule.get("detect", {}), dict):
        raise ValueError(f"'detect' must be a dict in {path}")


def rule_matches_scope(rule: Dict[str, Any], selectors: List[str]) -> bool:
    """Checks if a rule's scope matches any of the agent's selectors."""
    scope = str(rule.get("scope", "")).strip()
    for sel in selectors:
        if scope.startswith(sel) or sel == "*":
            return True
    return False


def compute_digest(file_paths: List[Path]) -> str:
    """Computes a SHA256 digest of all rule card files to create a version hash."""
    h = hashlib.sha256()
    for p in sorted(file_paths):
        h.update(p.read_bytes())
    return "sha256:" + h.hexdigest()


def reduce_rule(rule: Dict[str, Any]) -> Dict[str, Any]:
    """Strips a rule card down to only the fields needed by the runtime agent."""
    # Keep only what the runtime/LLM needs
    keep = {
        "id": rule["id"],
        "title": rule["title"],
        "severity": rule.get("severity", "medium"),
        "scope": rule["scope"],
        "requirement": rule["requirement"],
        "do": rule.get("do", []),
        "dont": rule.get("dont", []),
        "detect": rule.get("detect", {}),
        "verify": rule.get("verify", {}),
        "refs": rule.get("refs", {}),
    }
    return keep


def build_agent_package(agent: Dict[str, Any]) -> Dict[str, Any]:
    """Builds a single, compiled JSON package for a given agent definition."""
    topics = agent["topics"]
    selectors = agent.get("scope_selectors", ["*"])

    files: List[Path] = []
    for t in topics:
        files.extend(collect_rule_files(t))

    rules: List[Dict[str, Any]] = []
    rule_ids = set()

    for path in files:
        data = load_yaml(path)
        if not isinstance(data, dict):
            raise ValueError(f"Rule card at {path} is not a YAML mapping")
        validate_rule_schema(data, path)
        if not rule_matches_scope(data, selectors):
            continue
        rid = data["id"]
        if rid in rule_ids:
            raise ValueError(f"Duplicate rule id {rid} across topics for agent {agent['id']}")
        rule_ids.add(rid)
        rules.append(reduce_rule(data))

    # Aggregate all scanner hooks (e.g., semgrep rules) from the included rules.
    hooks: Dict[str, List[str]] = {}
    for r in rules:
        for tool, rule_list in r.get("detect", {}).items():
            hooks.setdefault(tool, [])
            for rr in rule_list:
                if rr not in hooks[tool]:
                    hooks[tool].append(rr)

    digest = compute_digest(files)
    build_date = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    version = dt.datetime.utcnow().strftime("%Y.%m.%d")

    pkg = {
        "id": agent["id"],
        "name": agent.get("name", agent["id"]),
        "version": version,
        "build_date": build_date,
        "source_digest": digest,
        "attribution": agent.get("attribution", ""),
        "policy": {
            "targets": agent.get("targets", []),
            "defaults": agent.get("defaults", {}),
        },
        "rules": [r["id"] for r in rules],
        "rules_detail": rules,
        "validation_hooks": hooks,
    }
    return pkg


def main():
    """Main entry point for the compiler script."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, help="Path to agents_manifest.yml")
    ap.add_argument("--out", required=True, help="Output directory for agent JSON")
    args = ap.parse_args()

    manifest = load_yaml(Path(args.manifest))
    agents = manifest.get("agents", [])
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    for agent in agents:
        pkg = build_agent_package(agent)
        out_path = outdir / f"{agent['id']}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(pkg, f, indent=2, sort_keys=False)
        print(f"wrote {out_path} with {len(pkg['rules'])} rules and hooks {list(pkg['validation_hooks'].keys())}")


if __name__ == "__main__":
    main()
