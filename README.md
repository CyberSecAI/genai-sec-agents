# GenAI Security Agents - Policy-as-Code Engine

A comprehensive Policy-as-Code system for security rule management and AI-powered guidance generation.

## Overview
This repository contains Rule Cards (human-readable security policies) and toolchain for compiling them into machine-readable agent packages.

## Quick Start
1. **Validate Rule Cards**: `python app/tools/validate_cards.py app/rule_cards/`
2. **Create New Rule Card**: Copy example from `app/rule_cards/docker/DOCKER-USER-001.yml`
3. **Run Tests**: `pytest tests/`

## Repository Structure
- `app/rule_cards/` - YAML Rule Cards organized by category
- `app/tools/` - Validation and compilation scripts
- `docs/` - Project documentation  
- `tests/` - Test suites
- `app/dist/` - Compiled agent packages

## Security
See [SECURITY_GUIDE.md](docs/SECURITY_GUIDE.md) for security practices and guidelines.

## Contributing
1. Create Rule Cards following the schema in `app/tools/rule-card-schema.json`
2. Validate with `python app/tools/validate_cards.py`
3. Run full test suite: `pytest`
4. Submit pull request

## License
[To be determined]