"""
Agentic Runtime Core Module

This module provides the core runtime system for loading and interpreting 
compiled security agent packages to deliver context-aware security guidance.

Security Features:
- Safe JSON parsing with validation
- Input sanitization and size limits
- Secure file system operations
- Information disclosure prevention
"""

from .core import AgenticRuntime
from .package_loader import PackageLoader
from .rule_selector import RuleSelector
from .llm_interface import LLMInterface, LLMProvider

__version__ = "1.0.0"
__all__ = ["AgenticRuntime", "PackageLoader", "RuleSelector", "LLMInterface", "LLMProvider"]