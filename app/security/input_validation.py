"""
Input Validation Module

Centralized input validation and sanitization for all user-provided content.
Replaces inconsistent validation scattered across the codebase.
"""

import re
from typing import Dict, Any, Optional, Union


class ValidationError(Exception):
    """Raised when input validation fails"""
    pass


class InputValidator:
    """
    Centralized input validation and sanitization.
    
    Provides consistent, secure validation policies across the entire system.
    All user input should go through this validator before processing.
    """
    
    # Security limits
    MAX_CODE_SIZE = 1024 * 1024  # 1MB max code content
    MAX_PATH_LENGTH = 500        # Max file path length
    MAX_STRING_LENGTH = 1000     # Max string field length
    MAX_CONTEXT_FIELDS = 20      # Max number of context fields
    
    # Allowed characters for different input types
    AGENT_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
    SAFE_STRING_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_.,!?()[\]{}:;\'\"]+$')
    
    @classmethod
    def validate_agent_name(cls, agent_name: Any) -> str:
        """
        Validate agent name for safe operations.
        
        Args:
            agent_name: Raw agent name input
            
        Returns:
            Validated agent name
            
        Raises:
            ValidationError: If agent name is invalid
        """
        if not agent_name:
            raise ValidationError("Agent name cannot be empty")
        
        if not isinstance(agent_name, str):
            raise ValidationError("Agent name must be a string")
        
        if len(agent_name) > 64:
            raise ValidationError("Agent name too long (max 64 characters)")
        
        if not cls.AGENT_NAME_PATTERN.match(agent_name):
            raise ValidationError("Agent name contains invalid characters (use only letters, numbers, hyphens, underscores)")
        
        return agent_name.strip()
    
    @classmethod
    def validate_code_content(cls, content: Any) -> str:
        """
        Validate and sanitize code content for safe processing.
        
        Args:
            content: Raw code content
            
        Returns:
            Validated code content
            
        Raises:
            ValidationError: If content is invalid or too large
        """
        if not isinstance(content, str):
            if content is None:
                return ""
            raise ValidationError("Code content must be a string")
        
        # Size limit check
        if len(content) > cls.MAX_CODE_SIZE:
            raise ValidationError(f"Code content too large (max {cls.MAX_CODE_SIZE} bytes)")
        
        # Content is returned as-is for code analysis - no sanitization that could break code
        return content
    
    @classmethod
    def validate_context_dict(cls, context: Any) -> Dict[str, Any]:
        """
        Validate and sanitize context dictionary.
        
        Args:
            context: Raw context data
            
        Returns:
            Validated context dictionary
            
        Raises:
            ValidationError: If context is invalid
        """
        if not isinstance(context, dict):
            raise ValidationError("Context must be a dictionary")
        
        if len(context) > cls.MAX_CONTEXT_FIELDS:
            raise ValidationError(f"Too many context fields (max {cls.MAX_CONTEXT_FIELDS})")
        
        validated = {}
        
        # Validate required fields
        if "content" in context:
            validated["content"] = cls.validate_code_content(context["content"])
        
        if "file_path" in context:
            validated["file_path"] = cls.validate_string_field(context["file_path"], "file_path")
        
        # Validate optional string fields
        string_fields = ["language", "framework", "domain", "file_type"]
        for field in string_fields:
            if field in context:
                validated[field] = cls.validate_string_field(context[field], field)
        
        return validated
    
    @classmethod
    def validate_string_field(cls, value: Any, field_name: str) -> str:
        """
        Validate a string field with length and character restrictions.
        
        Args:
            value: Raw field value
            field_name: Name of field for error messages
            
        Returns:
            Validated string value
            
        Raises:
            ValidationError: If value is invalid
        """
        if not isinstance(value, str):
            if value is None:
                return ""
            raise ValidationError(f"{field_name} must be a string")
        
        # Length check
        if len(value) > cls.MAX_STRING_LENGTH:
            raise ValidationError(f"{field_name} too long (max {cls.MAX_STRING_LENGTH} characters)")
        
        # Basic sanitization - strip whitespace
        sanitized = value.strip()
        
        return sanitized
    
    @classmethod
    def validate_file_path_string(cls, file_path: Any) -> str:
        """
        Validate file path string for display/logging purposes only.
        
        This is NOT for actual file operations - use PathValidator for that.
        
        Args:
            file_path: Raw file path string
            
        Returns:
            Validated file path string
            
        Raises:
            ValidationError: If file path is invalid
        """
        if not isinstance(file_path, str):
            if file_path is None:
                return ""
            raise ValidationError("File path must be a string")
        
        if len(file_path) > cls.MAX_PATH_LENGTH:
            raise ValidationError(f"File path too long (max {cls.MAX_PATH_LENGTH} characters)")
        
        # Remove null bytes and control characters
        sanitized = file_path.replace('\x00', '').replace('\r', '').replace('\n', '')
        
        return sanitized.strip()
    
    @classmethod
    def validate_boolean_flag(cls, value: Any, field_name: str) -> bool:
        """
        Validate boolean flag value.
        
        Args:
            value: Raw boolean value
            field_name: Name of field for error messages
            
        Returns:
            Validated boolean value
            
        Raises:
            ValidationError: If value is not a valid boolean
        """
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            lower_value = value.lower().strip()
            if lower_value in ('true', '1', 'yes', 'on'):
                return True
            elif lower_value in ('false', '0', 'no', 'off'):
                return False
        
        raise ValidationError(f"{field_name} must be a boolean value")
    
    @classmethod
    def validate_integer_field(cls, value: Any, field_name: str, min_val: Optional[int] = None, max_val: Optional[int] = None) -> int:
        """
        Validate integer field with optional range checking.
        
        Args:
            value: Raw integer value
            field_name: Name of field for error messages
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            Validated integer value
            
        Raises:
            ValidationError: If value is invalid or out of range
        """
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be an integer")
        
        if min_val is not None and int_value < min_val:
            raise ValidationError(f"{field_name} must be at least {min_val}")
        
        if max_val is not None and int_value > max_val:
            raise ValidationError(f"{field_name} must be at most {max_val}")
        
        return int_value