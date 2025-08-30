# Rule Card Schema Specification

## Overview
Rule Cards are YAML-formatted security policy definitions that serve as the foundation for the Policy-as-Code system. Each Rule Card contains structured information that can be both human-readable and machine-processable.

## Schema Structure

### Required Fields

#### `id` (string)
- **Pattern**: `^[A-Z][A-Z0-9]+-[A-Z0-9]+-[0-9]{3}$`
- **Example**: `DOCKER-USER-001`
- **Description**: Unique identifier for the Rule Card

#### `title` (string)
- **Length**: 5-100 characters
- **Example**: `"Docker containers must not run as root user"`
- **Description**: Human-readable title describing the rule

#### `severity` (enum)
- **Values**: `low`, `medium`, `high`, `critical`
- **Description**: Risk level associated with violating this rule

#### `scope` (string)
- **Example**: `dockerfile`, `backend:java`, `frontend:react`
- **Description**: Context where the rule applies

#### `requirement` (string)
- **Minimum length**: 10 characters
- **Description**: Normative statement of what must be achieved

#### `do` (array of strings)
- **Minimum items**: 1
- **Description**: List of recommended practices and actions

#### `dont` (array of strings)
- **Minimum items**: 1
- **Description**: List of practices to avoid

#### `detect` (object)
- **Structure**: Tool name → array of rule identifiers
- **Example**: 
  ```yaml
  detect:
    semgrep:
      - "dockerfile.security.missing-user"
    hadolint:
      - "DL3002"
  ```

#### `verify` (object)
- **Required subfield**: `tests` (array of strings)
- **Description**: Human-readable test cases to verify compliance

#### `refs` (object)
- **Structure**: Standard name → array of reference identifiers
- **Example**:
  ```yaml
  refs:
    cis:
      - "4.1"
    owasp:
      - "A06:2021"
  ```

## Security Considerations

### Schema Design Security
- **No executable content**: Schema prevents inclusion of code or scripts
- **Strict typing**: All fields have defined types and validation
- **Length limits**: Prevents oversized content that could cause issues

### Validation Security
- **Safe YAML parsing**: Only `yaml.safe_load()` is used
- **Path validation**: File paths are sanitized to prevent traversal
- **Type checking**: Runtime validation ensures proper data types

## Example Rule Card

```yaml
id: DOCKER-USER-001
title: "Docker containers must not run as root user"
severity: high
scope: dockerfile
requirement: "Container processes must run under a non-root user account to limit privilege escalation risks."
do:
  - "Use USER directive to specify non-root user"
  - "Create dedicated application user in Dockerfile"
  - "Set appropriate file permissions for non-root user"
dont:
  - "Do not run processes as root (UID 0)"
  - "Do not rely on runtime user switching"
  - "Do not use privileged containers unnecessarily"
detect:
  semgrep:
    - "dockerfile.security.missing-user"
    - "dockerfile.security.user-root"
  hadolint:
    - "DL3002"
verify:
  tests:
    - "Verify USER directive is present and not root"
    - "Test container runs with non-root UID"
    - "Validate file permissions work for specified user"
refs:
  cis:
    - "4.1"
  nist:
    - "CM-2"
  owasp:
    - "A06:2021"
```

## Validation

Use the validation script to verify Rule Card compliance:

```bash
# Validate single Rule Card
python app/tools/validate_cards.py app/rule_cards/docker/DOCKER-USER-001.yml

# Validate all Rule Cards
python app/tools/validate_cards.py app/rule_cards/
```