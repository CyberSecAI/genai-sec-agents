# **Unified Project Structure**

The project will be housed in a single monorepo named genai-sec-agents. This structure organizes the Policy-as-Code assets, the compiler toolchain, and CI/CD configurations logically.

```
/genai-sec-agents/  
|  
├── .github/  
│   └── workflows/  
│       └── security.yml      \# Main CI/CD validation pipeline  
|  
├── rule\_cards/               \# Human-readable "single source of truth" for rules  
│   ├── docker/\*.yml  
│   ├── jwt/java/\*.yml  
│   ├── authn/\*.yml  
│   └── shared/\*.yml  
|  
├── tools/                      \# The compiler and validation toolchain  
│   ├── compile\_agents.py  
│   ├── validate\_cards.py  
│   └── agents\_manifest.yml  
|  
├── dist/                       \# Compiled, distributable agent packages  
│   └── agents/  
│       └── \*.json  
|  
├── ci/                         \# Configurations for CI scanners  
│   ├── semgrep-rules/  
│   └── conftest-policies/  
|  
├── policy/  
│   └── thresholds.yml          \# Policy for CI gates (e.g., fail on High sev)  
|  
├── docs/                       \# Project documentation  
│   ├── ATTRIBUTION.md  
│   ├── SECURITY\_GUIDE.md  
│   ├── architecture.md  
│   └── prd.md  
|  
├── Makefile                    \# Helper scripts for local development  
├── requirements.txt            \# Python dependencies for the toolchain  
└── README.md
```
