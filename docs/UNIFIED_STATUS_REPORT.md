# Rule Card System Status Report

**Generated**: 2025-09-02 13:47:17 UTC  
**Source**: Automated analysis of `app/rule_cards/` directory  
**Script**: `tools/generate_status_report.py`

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Total Rule Cards** | 197 |
| **Total Domains** | 21 |
| **Populated Domains** | 20 |
| **Empty Domains** | 1 |

---

## Domain Breakdown

### Populated Domains (20 domains)

- **authentication**: 49 rule cards
- **session_management**: 22 rule cards
- **logging**: 18 rule cards
- **configuration**: 16 rule cards
- **data_protection**: 14 rule cards
- **authorization**: 13 rule cards
- **web_security**: 9 rule cards
- **cryptography**: 8 rule cards
- **network_security**: 8 rule cards
- **input_validation**: 6 rule cards
- **secure_communication**: 6 rule cards
- **file_handling**: 4 rule cards
- **jwt**: 4 rule cards
- **secrets**: 4 rule cards
- **cookies**: 3 rule cards
- **genai**: 3 rule cards
- **java**: 3 rule cards
- **nodejs**: 3 rule cards
- **php**: 3 rule cards
- **docker**: 1 rule cards

### Empty Domains (1 domains)

- **api_security**: 0 rule cards


---

## Quality Metrics

### Severity Distribution
- **critical**: 8 (4.1%)
- **high**: 85 (43.1%)
- **low**: 20 (10.2%)
- **medium**: 84 (42.6%)

### Scope Distribution
- **all-languages**: 2 (1.0%)
- **cloud-applications**: 1 (0.5%)
- **dockerfile**: 1 (0.5%)
- **genai-applications**: 3 (1.5%)
- **infrastructure**: 4 (2.0%)
- **jwt-implementations**: 5 (2.5%)
- **web-application**: 164 (83.2%)
- **web-application/api**: 10 (5.1%)
- **web-application/api/mobile/infrastructure**: 4 (2.0%)
- **web-applications**: 3 (1.5%)


---

## Standards Compliance

| Standard | References |
|----------|------------|
| **ASVS** | 146 unique references |
| **CWE** | 69 unique references |
| **OWASP** | 25 unique references |

### Detection Tool Integration
- **codeql**: 19 rule cards
- **custom**: 6 rule cards
- **hadolint**: 1 rule cards
- **semgrep**: 192 rule cards
- **trufflehog**: 37 rule cards

---

## Change History

This report reflects the current state after:
- ✅ **Priority 1-3 Duplicate Consolidation**: 18 duplicate rule cards eliminated
- ✅ **Enhanced Naming Convention**: Descriptive rule card names implemented
- ✅ **System Validation**: All agent packages compile successfully

---

## Notes

- This report is the **single source of truth** for rule card metrics
- Generated automatically from filesystem analysis
- Supersedes all previous status reports
- Updated automatically with each rule card change

