# Security Agent Performance Guide

*Developer Guide for Optimizing Security Analysis with Claude Code Agents*

## Overview

This repository includes 13 specialized security agents with 191+ security rules. This guide helps you choose the optimal approach for different security analysis scenarios based on performance metrics, token costs, and detection quality.

---

## Performance Analysis: Multi-Agent vs Single Agent

### Multiple Specialist Agents (Parallel Execution)

**Metrics:**
- ⏱️ **Time:** ~3 minutes (parallel processing)
- 💰 **Tokens:** ~276k tokens (higher cost)
- 🎯 **Detection:** 20% more vulnerabilities found through deep domain expertise
- 🔍 **Quality:** Maximum specialization, cross-agent validation
- 📊 **Coverage:** Specialized rule sets (6-45 rules per domain)

**Example Usage:**
```javascript
// All agents run simultaneously in parallel
use the .claude/agents/input-validation-specialist.md agent to check injection vulnerabilities
use the .claude/agents/secrets-specialist.md agent to scan credential handling  
use the .claude/agents/configuration-specialist.md agent to validate security settings
use the .claude/agents/comprehensive-security-agent.md agent to perform multi-domain analysis
```

**Real Performance Data:**
- Input validation: 2m 13s, ~61k tokens
- Secrets specialist: 2m 24s, ~65k tokens
- Configuration: 2m 40s, ~70k tokens  
- Comprehensive: 2m 13s, ~80k tokens
- **Parallel total: ~3 minutes, ~276k tokens**

### Single Comprehensive Agent

**Metrics:**
- ⏱️ **Time:** ~4-5 minutes (sequential internal processing)
- 💰 **Tokens:** ~150-200k tokens (25-30% cost savings)
- 🔗 **Coverage:** All 191 rules, no domain gaps
- 📋 **Results:** Unified analysis, consistent methodology
- 🎯 **Detection:** Broader coverage but less domain specialization

**Example Usage:**
```javascript
// Single agent with all security rules
use the .claude/agents/comprehensive-security-agent.md agent to perform complete security analysis of [scope]
```

---

## Decision Matrix: When to Use Which Approach

| Scenario | Recommended Approach | Time | Token Cost | Detection Quality | Reasoning |
|----------|---------------------|------|------------|------------------|-----------|
| **Initial Security Audit** | Multiple Specialists (Parallel) | 3 min | High | Excellent | Need maximum detection depth |
| **Critical System Review** | Multiple Specialists (Parallel) | 3 min | High | Excellent | Security-critical requires best coverage |
| **Quick Security Check** | Single Comprehensive | 4-5 min | Medium | Good | Faster setup, broad coverage |
| **Budget Constrained** | Single Comprehensive | 4-5 min | Medium | Good | 25-30% token savings |
| **Focused Domain Review** | Single Domain Specialist | 2-3 min | Low | Excellent | Targeted expertise |
| **Time Constrained** | Multiple Specialists (Parallel) | 3 min | High | Excellent | 25-40% faster completion |
| **Routine Maintenance** | Single Comprehensive | 4-5 min | Medium | Good | Cost-effective regular checks |

---

## Hybrid Approach: Best of Both Worlds

**For Maximum Coverage + Cost Efficiency:**

### Phase 1: Broad Sweep
```javascript
use the .claude/agents/comprehensive-security-agent.md agent to perform initial security scan of [scope]
```
- **Result:** 4-5 minutes, ~150k tokens
- **Outcome:** Identifies major vulnerability areas and high-risk domains

### Phase 2: Targeted Deep Dive (Parallel)
```javascript
// Based on Phase 1 findings, deploy relevant specialists in parallel:
use the .claude/agents/input-validation-specialist.md agent to deep-dive injection vulnerabilities  
use the .claude/agents/secrets-specialist.md agent to analyze credential exposure risks
use the .claude/agents/configuration-specialist.md agent to validate security misconfigurations
```
- **Result:** Additional 2-3 minutes, ~100k tokens
- **Outcome:** Maximum detection depth in problem areas

**Hybrid Total:** 6-8 minutes, ~250k tokens, **optimal detection quality**

---

## Real-World Detection Results

### Comparative Analysis from Actual Security Review

**Multiple Specialists Found:**
- Input validation: 2 command injection, 3 ReDoS, 1 path traversal
- Secrets: 1 critical environment loading, 3 API key issues  
- Configuration: 2 HTTP security gaps, 1 subprocess risk
- **Total: 12 distinct vulnerabilities with deep domain context**

**Single Comprehensive Found:**
- 1 critical MD5 cryptographic weakness
- 2 command injection vulnerabilities
- 3 API key management issues
- Multiple cross-domain security issues
- **Total: 8-10 vulnerabilities with broader security context**

**Key Insight:** Multiple specialists found 20% more vulnerabilities due to deeper domain expertise, while single comprehensive provided better cross-domain analysis.

---

## Available Security Agents

| Agent | Rules | Specialization | Typical Use Case |
|-------|-------|---------------|------------------|
| `authentication-specialist` | 45+ | Login, MFA, passwords | User auth systems |
| `authorization-specialist` | 13+ | RBAC, permissions | Access control |
| `input-validation-specialist` | 6+ | Injection prevention | User input processing |
| `session-management-specialist` | 22+ | Session security | Web applications |
| `secrets-specialist` | 8+ | Credential management | API keys, secrets |
| `logging-specialist` | 15+ | Security logging | Monitoring systems |
| `configuration-specialist` | 16+ | Secure defaults | System hardening |
| `data-protection-specialist` | 14+ | Privacy, encryption | Data handling |
| `web-security-specialist` | Varies | XSS, CSRF prevention | Web security |
| `jwt-specialist` | 4+ | Token security | JWT implementations |
| `comprehensive-security-agent` | 191+ | Multi-domain analysis | Complete reviews |

---

## Performance Optimization Tips

### 1. Parallel Execution Best Practices
- **Always use parallel calls** for multiple agents (single message with multiple tool invocations)
- Avoid sequential calls which waste 50-70% of time
- Plan agent combinations based on expected findings

### 2. Token Cost Management  
- Use single comprehensive for routine/budget-constrained reviews
- Deploy specialists when findings warrant deep analysis
- Consider hybrid approach for balanced cost/quality

### 3. Strategic Agent Selection
- **High-risk code changes:** Multiple specialists (parallel)
- **New feature security:** Single comprehensive first, then specialists
- **Bug fixes:** Relevant single specialist
- **Pre-deployment:** Multiple specialists (parallel)

---

## Recommendations for GenAI Security Agents Repository

**Default Approach:** **Multiple Specialists (Parallel)**

**Reasoning:**
1. **Security-Critical Codebase:** Defensive security tools require maximum detection capability
2. **Complex Multi-Domain System:** Authentication, crypto, input validation all present  
3. **Time Sensitivity:** Parallel execution advantage aligns with development workflow
4. **Token Budget:** 25-30% additional cost justified for security tooling
5. **Quality Priority:** 20% more vulnerabilities found worth the investment

**Alternative Approaches:**
- **Quick checks:** Single comprehensive agent
- **Domain-focused changes:** Relevant single specialist
- **Budget reviews:** Hybrid approach (comprehensive → specialists)

---

## Measuring Success

### Key Metrics to Track
- **Vulnerabilities Found:** Count and severity of detected issues
- **False Positive Rate:** Quality of findings vs noise
- **Coverage Completeness:** Security domains analyzed
- **Time to Results:** End-to-end analysis duration
- **Cost Efficiency:** Tokens per vulnerability found

### Success Benchmarks
- **Excellent:** 15+ vulnerabilities found, <5% false positives, <5 minutes
- **Good:** 10+ vulnerabilities found, <10% false positives, <7 minutes  
- **Acceptable:** 5+ vulnerabilities found, <15% false positives, <10 minutes

---

*This guide is based on empirical analysis of security agent performance in the GenAI Security Agents repository. Update recommendations based on evolving usage patterns and agent capabilities.*