"""
AgenticRuntime Core Class

Main runtime component that orchestrates package loading, rule selection,
and LLM interaction for providing security guidance.

Security Controls:
- Validates all inputs and file paths
- Implements secure error handling
- Prevents information disclosure
- Uses principle of least privilege
"""

import os
import logging
from typing import Dict, List, Optional, Union
from pathlib import Path

from .package_loader import PackageLoader
from .rule_selector import RuleSelector
from .llm_interface import LLMInterface


class AgenticRuntimeError(Exception):
    """Base exception for runtime errors"""
    pass


class AgenticRuntime:
    """
    Core runtime for loading and interpreting compiled security agent packages.
    
    Provides context-aware security guidance for IDE integration with
    model-agnostic LLM interfaces for flexible deployment.
    """
    
    def __init__(self, package_directory: str = "app/dist/agents", debug: bool = False):
        """
        Initialize the Agentic Runtime.
        
        Args:
            package_directory: Path to compiled agent packages
            debug: Enable debug logging (warning: may log sensitive data)
        
        Raises:
            AgenticRuntimeError: If package directory is invalid
        """
        self.package_directory = self._validate_package_directory(package_directory)
        self.loaded_packages = {}
        self.debug = debug
        
        # Initialize components
        self.package_loader = PackageLoader()
        self.rule_selector = RuleSelector()
        self.llm_interface = LLMInterface()
        
        # Configure logging
        self._setup_logging()
        
        if self.debug:
            self.logger.debug(f"AgenticRuntime initialized with package directory: {self.package_directory}")
    
    def _validate_package_directory(self, directory: str) -> str:
        """
        Validate package directory exists and is accessible.
        
        Args:
            directory: Directory path to validate
            
        Returns:
            Validated absolute directory path
            
        Raises:
            AgenticRuntimeError: If directory is invalid
        """
        try:
            path = Path(directory).resolve()
            
            # Security check: Ensure path is within allowed directories
            if not path.exists():
                raise AgenticRuntimeError(f"Package directory does not exist: {directory}")
            
            if not path.is_dir():
                raise AgenticRuntimeError(f"Package path is not a directory: {directory}")
            
            # Check read permissions
            if not os.access(path, os.R_OK):
                raise AgenticRuntimeError(f"No read permission for package directory: {directory}")
            
            return str(path)
            
        except (OSError, PermissionError) as e:
            raise AgenticRuntimeError(f"Invalid package directory: {e}")
    
    def _setup_logging(self) -> None:
        """Configure secure logging with appropriate levels."""
        self.logger = logging.getLogger(__name__)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Set appropriate log level
        self.logger.setLevel(logging.DEBUG if self.debug else logging.INFO)
    
    def load_agent(self, agent_name: str) -> bool:
        """
        Load a compiled agent package by name.
        
        Args:
            agent_name: Name of the agent (e.g., 'secrets-specialist')
            
        Returns:
            True if agent loaded successfully, False otherwise
            
        Raises:
            AgenticRuntimeError: If loading fails due to security issues
        """
        try:
            # Sanitize agent name to prevent path traversal
            safe_agent_name = self._sanitize_agent_name(agent_name)
            package_path = os.path.join(self.package_directory, f"{safe_agent_name}.json")
            
            # Load package using secure loader
            package_data = self.package_loader.load_package(package_path)
            
            if package_data is None:
                self.logger.error(f"Failed to load agent package: {agent_name}")
                return False
            
            # Store loaded package
            self.loaded_packages[agent_name] = package_data
            
            self.logger.info(f"Successfully loaded agent: {agent_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading agent {agent_name}: {str(e)}")
            return False
    
    def _sanitize_agent_name(self, agent_name: str) -> str:
        """
        Sanitize agent name to prevent path traversal attacks.
        
        Args:
            agent_name: Raw agent name input
            
        Returns:
            Sanitized agent name
            
        Raises:
            AgenticRuntimeError: If agent name contains invalid characters
        """
        if not agent_name or not isinstance(agent_name, str):
            raise AgenticRuntimeError("Agent name must be a non-empty string")
        
        # Remove dangerous characters
        sanitized = "".join(c for c in agent_name if c.isalnum() or c in ['-', '_'])
        
        if not sanitized:
            raise AgenticRuntimeError("Agent name contains no valid characters")
        
        if sanitized != agent_name:
            self.logger.warning(f"Agent name sanitized: {agent_name} -> {sanitized}")
        
        return sanitized
    
    def get_guidance(self, context: Dict, agent_name: Optional[str] = None) -> Optional[Dict]:
        """
        Get security guidance based on code context.
        
        Args:
            context: Development context (file_path, content, etc.)
            agent_name: Specific agent to use (auto-select if None)
            
        Returns:
            Guidance response dict or None if error
            
        Raises:
            AgenticRuntimeError: If context is invalid
        """
        try:
            # Validate context input
            validated_context = self._validate_context(context)
            
            # Select or validate agent
            selected_agent = agent_name or self._select_best_agent(validated_context)
            
            if selected_agent not in self.loaded_packages:
                if not self.load_agent(selected_agent):
                    raise AgenticRuntimeError(f"Failed to load required agent: {selected_agent}")
            
            # Get relevant rules for context
            package_data = self.loaded_packages[selected_agent]
            relevant_rules = self.rule_selector.select_rules(validated_context, package_data["rules"])
            
            if not relevant_rules:
                return {
                    "guidance": "No specific security rules apply to this context.",
                    "suggestions": [],
                    "severity": "info",
                    "agent_used": selected_agent
                }
            
            # Generate guidance using LLM interface
            guidance_response = self.llm_interface.generate_guidance(
                validated_context, relevant_rules, package_data["agent"]
            )
            
            # Add metadata to response
            guidance_response["agent_used"] = selected_agent
            guidance_response["rules_applied"] = len(relevant_rules)
            
            return guidance_response
            
        except Exception as e:
            self.logger.error(f"Error generating guidance: {str(e)}")
            return None
    
    def _validate_context(self, context: Dict) -> Dict:
        """
        Validate and sanitize context input.
        
        Args:
            context: Raw context input
            
        Returns:
            Validated context dict
            
        Raises:
            AgenticRuntimeError: If context is invalid
        """
        if not isinstance(context, dict):
            raise AgenticRuntimeError("Context must be a dictionary")
        
        validated = {}
        
        # Validate required fields
        if "file_path" in context:
            validated["file_path"] = self._sanitize_file_path(context["file_path"])
        
        if "content" in context:
            validated["content"] = self._sanitize_content(context["content"])
        
        # Add optional fields
        for field in ["language", "framework", "domain"]:
            if field in context:
                validated[field] = str(context[field])[:100]  # Limit length
        
        return validated
    
    def _sanitize_file_path(self, file_path: str) -> str:
        """Sanitize file path to prevent path traversal."""
        if not isinstance(file_path, str):
            return ""
        
        # Remove dangerous patterns
        sanitized = file_path.replace("..", "").replace("//", "/")
        
        # Limit length
        return sanitized[:500]
    
    def _sanitize_content(self, content: str) -> str:
        """Sanitize file content for safe processing."""
        if not isinstance(content, str):
            return ""
        
        # Limit content size (1MB max)
        MAX_CONTENT_SIZE = 1024 * 1024
        return content[:MAX_CONTENT_SIZE]
    
    def _select_best_agent(self, context: Dict) -> str:
        """
        Select the most appropriate agent based on context.
        
        Args:
            context: Development context
            
        Returns:
            Best agent name for the context
        """
        # Simple heuristic-based selection
        file_path = context.get("file_path", "").lower()
        content = context.get("content", "").lower()
        
        # Dockerfile detection
        if "dockerfile" in file_path or "docker" in content:
            return "container-security-specialist"
        
        # Secrets detection
        if any(keyword in content for keyword in ["password", "secret", "key", "token", "jwt"]):
            return "secrets-specialist"
        
        # Web security patterns
        if any(keyword in content for keyword in ["http", "request", "response", "cookie", "session"]):
            return "web-security-specialist"
        
        # GenAI patterns
        if any(keyword in content for keyword in ["openai", "anthropic", "llm", "ai", "prompt"]):
            return "genai-security-specialist"
        
        # Default to comprehensive agent
        return "comprehensive-security-agent"
    
    def get_loaded_agents(self) -> List[str]:
        """
        Get list of currently loaded agent names.
        
        Returns:
            List of loaded agent names
        """
        return list(self.loaded_packages.keys())
    
    def get_available_agents(self) -> List[str]:
        """
        Get list of available agent packages in the directory.
        
        Returns:
            List of available agent names
        """
        try:
            agents = []
            package_dir = Path(self.package_directory)
            
            for file_path in package_dir.glob("*.json"):
                agent_name = file_path.stem
                agents.append(agent_name)
            
            return sorted(agents)
            
        except Exception as e:
            self.logger.error(f"Error listing available agents: {e}")
            return []
    
    def unload_agent(self, agent_name: str) -> bool:
        """
        Unload a specific agent from memory.
        
        Args:
            agent_name: Name of agent to unload
            
        Returns:
            True if unloaded successfully
        """
        if agent_name in self.loaded_packages:
            del self.loaded_packages[agent_name]
            self.logger.info(f"Unloaded agent: {agent_name}")
            return True
        
        return False
    
    def clear_all_agents(self) -> None:
        """Clear all loaded agents from memory."""
        self.loaded_packages.clear()
        self.logger.info("Cleared all loaded agents")