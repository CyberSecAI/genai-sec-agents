# GenAI Security Agents — Rule Cards & Compiler (MVP)

This package gives you:

* An initial set of **Rule Cards** derived from OWASP-aligned practices (Docker, JWT/Java, AuthN, Shared/Secrets).
* A **compiler** that builds **compiled sub-agent packages** (JSON) from rule cards — no runtime RAG needed.
* A **validator** for Rule Card schema.
* A minimal **Makefile** and **requirements.txt**.

> Note: These Rule Cards include attribution stubs for CC BY-SA. Replace/add exact attribution text per your legal review.

---

## Quick start

```bash
# 1) Create and activate a virtual environment, then install deps
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2) Validate rule cards
python tools/validate_cards.py

# 3) Compile agents (outputs JSON to dist/agents)
python tools/compile_agents.py --manifest tools/agents_manifest.yml --out dist/agents

# 4) Inspect compiled agent JSON
ls -1 dist/agents
cat dist/agents/agent.docker.json | head -n 80
```

---

## Directory layout

```
/rule_cards/
  docker/*.yml
  jwt/java/*.yml
  authn/*.yml
  shared/*.yml
/tools/
  compile_agents.py
  validate_cards.py
  agents_manifest.yml
/dist/agents/           # <- compiler output (JSON)
/ci/
  semgrep-rules/        # (placeholder for custom rules)
  conftest-policies/    # (placeholder for OPA/rego)
/policy/
  thresholds.yml        # (placeholder for CI gates)
/docs/
  ATTRIBUTION.md
  SECURITY_GUIDE.md
Makefile
requirements.txt
```

---

## tools/agents\_manifest.yml

```yaml
agents:
  - id: agent.docker
    name: "Docker Security Agent"
    topics: ["docker", "shared"]
    scope_selectors: ["dockerfile", "container-image"]
    targets: ["Dockerfile", "**/Dockerfile", "**/*.dockerfile"]
    defaults: {}
    attribution: "Derived from OWASP Cheat Sheet Series (CC BY-SA 4.0). See docs/ATTRIBUTION.md"

  - id: agent.jwt.java
    name: "JWT Security Agent (Java)"
    topics: ["jwt/java", "shared"]
    scope_selectors: ["backend:java"]
    targets: ["**/*.java", "**/*.properties", "**/*.yml"]
    defaults: { jwt_ttl_seconds: 900 }
    attribution: "Derived from OWASP Cheat Sheet Series (CC BY-SA 4.0). See docs/ATTRIBUTION.md"

  - id: agent.authn
    name: "Authentication Agent"
    topics: ["authn", "shared"]
    scope_selectors: ["backend"]
    targets: ["**/*"]
    defaults: {}
    attribution: "Derived from OWASP Cheat Sheet Series (CC BY-SA 4.0). See docs/ATTRIBUTION.md"
```

---

## tools/compile\_agents.py

```python
#!/usr/bin/env python3
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

REQUIRED_FIELDS = [
    "id", "title", "scope", "requirement", "do", "dont", "detect", "verify", "refs", "license"
]


def load_yaml(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def collect_rule_files(topic: str) -> List[Path]:
    # topic like "docker" or "jwt/java" -> expand to rule_cards/<topic>/**.yml
    pattern = str(RULE_DIR / topic / "**" / "*.yml")
    return [Path(p) for p in glob.glob(pattern, recursive=True)]


def validate_rule_schema(rule: Dict[str, Any], path: Path) -> None:
    missing = [k for k in REQUIRED_FIELDS if k not in rule]
    if missing:
        raise ValueError(f"Missing fields {missing} in {path}")
    if not isinstance(rule.get("do", []), list) or not isinstance(rule.get("dont", []), list):
        raise ValueError(f"'do' and 'dont' must be lists in {path}")
    if not isinstance(rule.get("detect", {}), dict):
        raise ValueError(f"'detect' must be a dict in {path}")


def rule_matches_scope(rule: Dict[str, Any], selectors: List[str]) -> bool:
    scope = str(rule.get("scope", "")).strip()
    for sel in selectors:
        if scope.startswith(sel) or sel == "*":
            return True
    return False


def compute_digest(file_paths: List[Path]) -> str:
    h = hashlib.sha256()
    for p in sorted(file_paths):
        h.update(p.read_bytes())
    return "sha256:" + h.hexdigest()


def reduce_rule(rule: Dict[str, Any]) -> Dict[str, Any]:
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
```

---

## tools/validate\_cards.py

```python
#!/usr/bin/env python3
import sys
import glob
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
RULE_DIR = ROOT / "rule_cards"

REQUIRED_FIELDS = [
    "id", "title", "scope", "requirement", "do", "dont", "detect", "verify", "refs", "license"
]


def main():
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
```

---

## requirements.txt

```text
PyYAML>=6.0
```

---

## Makefile

```makefile
.PHONY: validate compile clean

VENV=.venv
PY=$(VENV)/bin/python

$(VENV)/bin/activate:
	python -m venv $(VENV)
	$(PY) -m pip install -U pip
	$(PY) -m pip install -r requirements.txt

validate: $(VENV)/bin/activate
	$(PY) tools/validate_cards.py

compile: validate
	$(PY) tools/compile_agents.py --manifest tools/agents_manifest.yml --out dist/agents

clean:
	rm -rf dist/agents
```

---

## docs/ATTRIBUTION.md

```markdown
# Attribution

This project includes derivative guidance from the **OWASP Cheat Sheet Series**, licensed under **CC BY-SA 4.0**.

- Original content: OWASP Cheat Sheet Series (https://cheatsheetseries.owasp.org/)
- License: Creative Commons Attribution-ShareAlike 4.0 International (https://creativecommons.org/licenses/by-sa/4.0/)

Per the license, we provide attribution here and in compiled agent metadata. Any redistributed derivatives must remain under a compatible license.
```

---

## docs/SECURITY\_GUIDE.md (stub)

```markdown
# Security Guide (Stub)

This repository compiles security Rule Cards into agent packages for pre-guidance during code generation and post-validation via CI scanners.

- **No runtime retrieval**. Guidance is embedded into agents at build time.
- **Traceability** via rule IDs and references (ASVS, OWASP topics).
- **Validation**: agents emit expected scanner hooks; CI enforces thresholds.
```

---

## rule\_cards/docker/DOCKER-USER-001.yml

```yaml
id: DOCKER-USER-001
title: "Run as non-root"
scope: "dockerfile"
severity: high
requirement: "Set USER to a non-root UID/GID; no root processes in the final image."
_doctag: "docker-security"
do:
  - "Create an application user in the final stage and chown the workdir."
  - "Ensure ENTRYPOINT/CMD runs under the non-root user."
dont:
  - "Do not leave default USER as root."
detect:
  hadolint: ["DL3002"]
verify:
  tests:
    - "Container primary process runs with UID != 0"
refs:
  asvs: ["V14.5"]
  owasp_cheatsheet: ["Docker Security"]
license:
  source: "OWASP Cheat Sheet Series (CC BY-SA 4.0)"
```

---

## rule\_cards/docker/DOCKER-COPY-003.yml

```yaml
id: DOCKER-COPY-003
title: "Use COPY instead of ADD"
scope: "dockerfile"
severity: medium
requirement: "Use COPY for local file transfers; reserve ADD only for explicit remote URL extraction (generally avoid)."
do:
  - "Replace ADD with COPY for deterministic behavior."
  - "Use multi-stage builds to control artifacts."
dont:
  - "Do not use ADD to fetch remote URLs."
detect:
  hadolint: ["DL3020"]
verify:
  tests:
    - "No ADD instructions present unless exception noted"
refs:
  asvs: ["V14.2"]
  owasp_cheatsheet: ["Docker Security"]
license:
  source: "OWASP Cheat Sheet Series (CC BY-SA 4.0)"
```

---

## rule\_cards/docker/DOCKER-PACKAGES-002.yml

```yaml
id: DOCKER-PACKAGES-002
title: "Minimize packages and clean caches"
scope: "dockerfile"
severity: medium
requirement: "Install only required packages and remove package caches and build-time tools in the same layer."
do:
  - "Use --no-install-recommends (apt) / --no-cache (apk) where applicable."
  - "Combine install and cleanup in a single RUN layer."
dont:
  - "Do not leave package manager caches in the image."
detect:
  hadolint: []
verify:
  tests:
    - "Image size reduced vs baseline"
refs:
  asvs: ["V14.4"]
  owasp_cheatsheet: ["Docker Security"]
license:
  source: "OWASP Cheat Sheet Series (CC BY-SA 4.0)"
```

---

## rule\_cards/jwt/java/JWT-EXP-001.yml

```yaml
id: JWT-EXP-001
title: "JWTs must have exp and short TTL"
scope: "backend:java"
severity: high
requirement: "Set exp; access tokens TTL ≤ 15m; validate exp server-side with ±60s clock skew."
do:
  - "Validate iss,aud,exp,nbf claims on every request."
  - "Prefer RS256/ES256 with managed keys."
dont:
  - "Do not accept tokens without exp."
  - "Do not rely on client-side expiration only."
detect:
  semgrep: ["java-jwt-missing-exp", "java-jwt-missing-claims"]
verify:
  tests:
    - "Reject token without exp"
    - "Reject token with past exp"
refs:
  asvs: ["V2.1.5", "V2.1.2"]
  owasp_cheatsheet: ["JSON Web Token for Java"]
license:
  source: "OWASP Cheat Sheet Series (CC BY-SA 4.0)"
```

---

## rule\_cards/jwt/java/JWT-ALG-002.yml

```yaml
id: JWT-ALG-002
title: "Safe JWT algorithms"
scope: "backend:java"
severity: high
requirement: "Use RS256/ES256; reject 'none'; do not confuse HS256 shared secret with RSA public key."
do:
  - "Pin acceptable algorithms in verifier settings."
  - "Use JWKs/JWKS with key rotation."
dont:
  - "Do not allow alg from token to override server policy."
detect:
  semgrep: ["java-jwt-insecure-alg", "java-jwt-dynamic-alg"]
verify:
  tests:
    - "Reject alg=none"
    - "Reject HS256 token when RS256 expected"
refs:
  asvs: ["V2.1.1"]
  owasp_cheatsheet: ["JSON Web Token for Java"]
license:
  source: "OWASP Cheat Sheet Series (CC BY-SA 4.0)"
```

---

## rule\_cards/authn/AUTHN-MFA-001.yml

```yaml
id: AUTHN-MFA-001
title: "Require MFA for high-privilege actions"
scope: "backend"
severity: high
requirement: "Enforce MFA for admin accounts and sensitive transactions; step-up auth when risk increases."
do:
  - "Enable TOTP/WebAuthn for admin users."
  - "Implement step-up flows for sensitive endpoints."
dont:
  - "Do not allow password-only access to admin consoles."
detect:
  semgrep: ["authn-mfa-required-admin"]
verify:
  tests:
    - "Admin login without MFA is rejected"
refs:
  asvs: ["V1.2", "V2.8"]
  owasp_cheatsheet: ["Authentication"]
license:
  source: "OWASP Cheat Sheet Series (CC BY-SA 4.0)"
```

---

## rule\_cards/shared/SHARED-SECRETS-001.yml

```yaml
id: SHARED-SECRETS-001
title: "No hardcoded secrets"
scope: "*"
severity: high
requirement: "Secrets, API keys, and credentials must not be hardcoded; use a secrets manager."
do:
  - "Load secrets from env vars or secrets manager (e.g., Vault, cloud KMS)."
  - "Rotate and scope secrets with least privilege."
dont:
  - "Do not commit secrets to version control."
detect:
  gitleaks: ["generic-api-key", "jwt", "password"]
verify:
  tests:
    - "Repo scan finds 0 secrets"
refs:
  asvs: ["V7.4", "V14.2"]
  owasp_cheatsheet: ["Secrets Management", "Password Storage"]
license:
  source: "OWASP Cheat Sheet Series (CC BY-SA 4.0)"
```

---

## rule\_cards/shared/SHARED-LOGGING-001.yml

```yaml
id: SHARED-LOGGING-001
title: "Avoid sensitive data in logs"
scope: "*"
severity: medium
requirement: "Never log secrets, tokens, passwords, or full PANs; mask/ redact sensitive fields."
do:
  - "Use structured logging with allowlists."
  - "Mask tokens and PII at the logger boundary."
dont:
  - "Do not log Authorization headers or session IDs."
detect:
  semgrep: ["logging-sensitive-data"]
verify:
  tests:
    - "Simulated requests do not emit secrets in logs"
refs:
  asvs: ["V7.1", "V7.3"]
  owasp_cheatsheet: ["Logging", "Privacy"]
license:
  source: "OWASP Cheat Sheet Series (CC BY-SA 4.0)"
```

---

## Sample output (after compile)

```json
{
  "id": "agent.docker",
  "name": "Docker Security Agent",
  "version": "2025.08.27",
  "build_date": "2025-08-27T00:00:00Z",
  "source_digest": "sha256:...",
  "attribution": "Derived from OWASP Cheat Sheet Series (CC BY-SA 4.0). See docs/ATTRIBUTION.md",
  "policy": {
    "targets": ["Dockerfile", "**/Dockerfile", "**/*.dockerfile"],
    "defaults": {}
  },
  "rules": ["DOCKER-USER-001", "DOCKER-COPY-003", "DOCKER-PACKAGES-002", "SHARED-SECRETS-001", "SHARED-LOGGING-001"],
  "rules_detail": [
    { "id": "DOCKER-USER-001", "title": "Run as non-root", "severity": "high", "scope": "dockerfile", "requirement": "Set USER to a non-root UID/GID; no root processes in the final image.", "do": ["Create an application user in the final stage and chown the workdir.", "Ensure ENTRYPOINT/CMD runs under the non-root user."], "dont": ["Do not leave default USER as root."], "detect": {"hadolint": ["DL3002"]}, "verify": {"tests": ["Container primary process runs with UID != 0"]}, "refs": {"asvs": ["V14.5"], "owasp_cheatsheet": ["Docker Security"]} }
  ],
  "validation_hooks": { "hadolint": ["DL3002", "DL3020"], "gitleaks": ["generic-api-key", "jwt", "password"], "semgrep": ["logging-sensitive-data"] }
}
```

---

## Notes & Next Steps

* Add more Rule Cards (TLS, Input Validation, Session Mgmt, K8s, Terraform).
* Fill `/ci/semgrep-rules` with the custom rules referenced in `detect.semgrep`.
* Wire CI to parse `validation_hooks` and enforce thresholds.
* Consider adding a small runtime renderer that turns `rules_detail` into concise bullet prompts for the sub-agent.
