"""
Model-Agnostic LLM Interface

Provides flexible interface for integrating with different LLM providers
while maintaining consistent prompt formatting and response handling.

Security Features:
- Sanitizes rule content before prompt integration
- Prevents sensitive data leakage in prompts
- Implements secure response parsing
- Validates all LLM interactions
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import json
import re


class LLMInterfaceError(Exception):
    """Exception for LLM interface errors"""
    pass


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    Defines the interface that all LLM providers must implement
    for consistent interaction patterns.
    """
    
    @abstractmethod
    def generate_guidance(self, prompt: str, context: Dict) -> str:
        """
        Generate security guidance using the LLM.
        
        Args:
            prompt: Formatted prompt with rules and context
            context: Additional context for the request
            
        Returns:
            Raw LLM response string
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of this LLM provider."""
        pass


class MockLLMProvider(LLMProvider):
    """
    Mock LLM provider for testing and development.
    
    Returns structured responses without actual LLM calls.
    """
    
    def generate_guidance(self, prompt: str, context: Dict) -> str:
        """Generate mock guidance response."""
        return json.dumps({
            "guidance": "Mock security guidance based on provided rules.",
            "suggestions": [
                "Use environment variables for sensitive configuration",
                "Implement proper input validation",
                "Follow secure coding practices"
            ],
            "severity": "medium",
            "confidence": 0.8,
            "provider": "mock"
        })
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return "mock"


class ClaudeProvider(LLMProvider):
    """
    Anthropic Claude provider implementation.
    
    Note: This is a placeholder implementation. 
    Real integration would require Anthropic SDK.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Claude provider."""
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
    
    def generate_guidance(self, prompt: str, context: Dict) -> str:
        """Generate guidance using Claude."""
        # Placeholder implementation
        self.logger.info("Claude provider called (placeholder implementation)")
        
        return json.dumps({
            "guidance": "Placeholder Claude response - implement with actual Anthropic SDK",
            "suggestions": ["Implement actual Claude integration"],
            "severity": "info",
            "confidence": 0.5,
            "provider": "claude-placeholder"
        })
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return "claude"


class GPTProvider(LLMProvider):
    """
    OpenAI GPT provider implementation.
    
    Note: This is a placeholder implementation.
    Real integration would require OpenAI SDK.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize GPT provider."""
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
    
    def generate_guidance(self, prompt: str, context: Dict) -> str:
        """Generate guidance using GPT."""
        # Placeholder implementation
        self.logger.info("GPT provider called (placeholder implementation)")
        
        return json.dumps({
            "guidance": "Placeholder GPT response - implement with actual OpenAI SDK",
            "suggestions": ["Implement actual OpenAI integration"],
            "severity": "info", 
            "confidence": 0.5,
            "provider": "gpt-placeholder"
        })
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return "gpt"


class PromptTemplates:
    """
    Reusable prompt templates for different guidance scenarios.
    
    Provides secure, consistent prompt formatting across providers.
    """
    
    SECURITY_GUIDANCE = """
You are a security expert assistant providing guidance to developers.

Context:
- File: {file_path}
- Language: {language}
- Framework: {framework}

Code Context:
{code_sample}

Relevant Security Rules:
{rules_summary}

Please provide:
1. Specific security guidance based on the rules
2. Actionable code improvements
3. Risk assessment (low/medium/high/critical)
4. References to security standards where applicable

Focus on practical, implementable recommendations.
"""
    
    RULE_EXPLANATION = """
Explain this security rule in practical terms:

Rule: {rule_title}
Requirement: {rule_requirement}
Scope: {rule_scope}

Do's:
{rule_dos}

Don'ts:
{rule_donts}

Provide a clear explanation suitable for developers.
"""
    
    CODE_REVIEW = """
Review this code for security issues:

File: {file_path}
Code:
{code_content}

Apply these security rules:
{applicable_rules}

Provide specific findings and remediation suggestions.
"""


class LLMInterface:
    """
    Main interface for LLM interactions.
    
    Handles prompt formatting, provider selection, response parsing,
    and security validations for all LLM communications.
    """
    
    def __init__(self, default_provider: str = "mock"):
        """
        Initialize LLM interface.
        
        Args:
            default_provider: Default LLM provider to use
        """
        self.logger = logging.getLogger(__name__)
        self.providers = {}
        self.default_provider = default_provider
        self.templates = PromptTemplates()
        
        # Initialize available providers
        self._initialize_providers()
    
    def _initialize_providers(self) -> None:
        """Initialize available LLM providers."""
        try:
            self.providers["mock"] = MockLLMProvider()
            self.providers["claude"] = ClaudeProvider()
            self.providers["gpt"] = GPTProvider()
            
            self.logger.info(f"Initialized {len(self.providers)} LLM providers")
            
        except Exception as e:
            self.logger.error(f"Error initializing providers: {e}")
            # Ensure at least mock provider is available
            self.providers["mock"] = MockLLMProvider()
    
    def generate_guidance(self, context: Dict, rules: List[Dict], 
                         agent_metadata: Dict, provider: Optional[str] = None) -> Dict:
        """
        Generate security guidance using LLM.
        
        Args:
            context: Development context
            rules: Relevant security rules
            agent_metadata: Agent package metadata
            provider: Specific provider to use
            
        Returns:
            Structured guidance response
            
        Raises:
            LLMInterfaceError: If guidance generation fails
        """
        try:
            # Select provider
            selected_provider = provider or self.default_provider
            if selected_provider not in self.providers:
                raise LLMInterfaceError(f"Unknown provider: {selected_provider}")
            
            # Validate inputs
            self._validate_inputs(context, rules)
            
            # Format prompt securely
            prompt = self._format_prompt(context, rules, agent_metadata)
            
            # Generate response
            provider_instance = self.providers[selected_provider]
            raw_response = provider_instance.generate_guidance(prompt, context)
            
            # Parse and validate response
            parsed_response = self._parse_response(raw_response, selected_provider)
            
            return parsed_response
            
        except Exception as e:
            self.logger.error(f"Error generating guidance: {e}")
            return self._create_error_response(str(e))
    
    def _validate_inputs(self, context: Dict, rules: List[Dict]) -> None:
        """
        Validate inputs for security issues.
        
        Args:
            context: Context to validate
            rules: Rules to validate
            
        Raises:
            LLMInterfaceError: If validation fails
        """
        if not isinstance(context, dict):
            raise LLMInterfaceError("Context must be a dictionary")
        
        if not isinstance(rules, list):
            raise LLMInterfaceError("Rules must be a list")
        
        # Validate context content size
        content = context.get('content', '')
        if len(content) > 50000:  # 50KB limit
            raise LLMInterfaceError("Content too large for LLM processing")
        
        # Check for too many rules
        if len(rules) > 20:
            raise LLMInterfaceError("Too many rules for single guidance request")
    
    def _format_prompt(self, context: Dict, rules: List[Dict], agent_metadata: Dict) -> str:
        """
        Format secure prompt with context and rules.
        
        Args:
            context: Development context
            rules: Security rules
            agent_metadata: Agent metadata
            
        Returns:
            Formatted prompt string
        """
        try:
            # Sanitize context data
            safe_context = self._sanitize_context(context)
            
            # Format rules summary
            rules_summary = self._format_rules_summary(rules)
            
            # Create prompt using template
            prompt = self.templates.SECURITY_GUIDANCE.format(
                file_path=safe_context.get('file_path', 'unknown'),
                language=safe_context.get('language', 'unknown'),
                framework=safe_context.get('framework', 'unknown'),
                code_sample=self._truncate_content(safe_context.get('content', '')),
                rules_summary=rules_summary
            )
            
            return prompt
            
        except Exception as e:
            self.logger.error(f"Error formatting prompt: {e}")
            raise LLMInterfaceError(f"Prompt formatting failed: {e}")
    
    def _sanitize_context(self, context: Dict) -> Dict:
        """
        Sanitize context data for safe prompt inclusion.
        
        Args:
            context: Raw context
            
        Returns:
            Sanitized context
        """
        sanitized = {}
        
        # Sanitize file path
        if 'file_path' in context:
            file_path = str(context['file_path'])
            # Remove sensitive patterns
            file_path = re.sub(r'[<>"|*?]', '', file_path)[:200]
            sanitized['file_path'] = file_path
        
        # Sanitize content
        if 'content' in context:
            content = str(context['content'])
            # Remove potential prompt injection patterns
            content = self._remove_prompt_injection(content)
            sanitized['content'] = content
        
        # Copy safe fields
        for field in ['language', 'framework', 'domain']:
            if field in context:
                value = str(context[field])[:50]
                # Basic alphanumeric + common chars only
                if re.match(r'^[a-zA-Z0-9\-_.]+$', value):
                    sanitized[field] = value
        
        return sanitized
    
    def _remove_prompt_injection(self, content: str) -> str:
        """
        Remove potential prompt injection patterns from content.
        
        Args:
            content: Content to sanitize
            
        Returns:
            Sanitized content
        """
        # Remove common prompt injection patterns
        injection_patterns = [
            r'ignore\s+previous\s+instructions',
            r'forget\s+everything',
            r'system\s*:',
            r'assistant\s*:',
            r'human\s*:',
            r'</[^>]+>',  # HTML-like tags
            r'\[INST\]',  # Instruction markers
            r'\[/INST\]'
        ]
        
        sanitized = content
        for pattern in injection_patterns:
            sanitized = re.sub(pattern, '[FILTERED]', sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    def _format_rules_summary(self, rules: List[Dict]) -> str:
        """
        Format rules into a safe summary for prompts.
        
        Args:
            rules: Rules to summarize
            
        Returns:
            Formatted rules summary
        """
        if not rules:
            return "No specific rules apply."
        
        summary_parts = []
        
        for i, rule in enumerate(rules[:10]):  # Limit to 10 rules
            try:
                rule_id = rule.get('id', f'rule-{i}')
                title = rule.get('title', 'Unknown Rule')[:100]
                requirement = rule.get('requirement', '')[:200]
                severity = rule.get('severity', 'medium')
                
                rule_summary = f"Rule {rule_id} ({severity}): {title}\n  Requirement: {requirement}"
                summary_parts.append(rule_summary)
                
            except Exception as e:
                self.logger.warning(f"Error formatting rule {i}: {e}")
                continue
        
        return "\n\n".join(summary_parts)
    
    def _truncate_content(self, content: str, max_length: int = 2000) -> str:
        """
        Safely truncate content for prompt inclusion.
        
        Args:
            content: Content to truncate
            max_length: Maximum length
            
        Returns:
            Truncated content
        """
        if len(content) <= max_length:
            return content
        
        truncated = content[:max_length]
        return truncated + "\n... [content truncated for analysis]"
    
    def _parse_response(self, raw_response: str, provider: str) -> Dict:
        """
        Parse and validate LLM response.
        
        Args:
            raw_response: Raw response from LLM
            provider: Provider that generated response
            
        Returns:
            Structured response dict
        """
        try:
            # Try to parse as JSON first
            if raw_response.strip().startswith('{'):
                response_data = json.loads(raw_response)
                if isinstance(response_data, dict):
                    return self._validate_response_structure(response_data, provider)
            
            # Fallback to text parsing
            return self._parse_text_response(raw_response, provider)
            
        except Exception as e:
            self.logger.error(f"Error parsing response: {e}")
            return self._create_error_response(f"Response parsing failed: {e}")
    
    def _validate_response_structure(self, response: Dict, provider: str) -> Dict:
        """
        Validate and normalize response structure.
        
        Args:
            response: Response to validate
            provider: Provider name
            
        Returns:
            Validated response
        """
        validated = {
            "guidance": str(response.get("guidance", "No guidance provided"))[:2000],
            "suggestions": [],
            "severity": "info",
            "confidence": 0.5,
            "provider": provider
        }
        
        # Validate suggestions
        if "suggestions" in response and isinstance(response["suggestions"], list):
            validated["suggestions"] = [
                str(s)[:200] for s in response["suggestions"][:10]
            ]
        
        # Validate severity
        if "severity" in response:
            severity = response["severity"]
            if severity in ["low", "medium", "high", "critical", "info"]:
                validated["severity"] = severity
        
        # Validate confidence
        if "confidence" in response:
            try:
                confidence = float(response["confidence"])
                validated["confidence"] = max(0.0, min(1.0, confidence))
            except (ValueError, TypeError):
                pass
        
        return validated
    
    def _parse_text_response(self, text: str, provider: str) -> Dict:
        """
        Parse plain text response into structured format.
        
        Args:
            text: Plain text response
            provider: Provider name
            
        Returns:
            Structured response
        """
        return {
            "guidance": text[:2000],
            "suggestions": [],
            "severity": "info",
            "confidence": 0.5,
            "provider": provider
        }
    
    def _create_error_response(self, error_message: str) -> Dict:
        """
        Create error response structure.
        
        Args:
            error_message: Error message
            
        Returns:
            Error response dict
        """
        return {
            "guidance": f"Error generating guidance: {error_message}",
            "suggestions": [],
            "severity": "error",
            "confidence": 0.0,
            "provider": "error"
        }
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of available providers.
        
        Returns:
            List of provider names
        """
        return list(self.providers.keys())
    
    def set_default_provider(self, provider: str) -> bool:
        """
        Set default LLM provider.
        
        Args:
            provider: Provider name to set as default
            
        Returns:
            True if set successfully
        """
        if provider in self.providers:
            self.default_provider = provider
            self.logger.info(f"Default provider set to: {provider}")
            return True
        
        return False