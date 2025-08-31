"""
Path Security Module

Robust path validation and traversal protection using canonical path resolution.
Prevents directory traversal attacks with proper path canonicalization.
"""

import os
from pathlib import Path
from typing import Union


class PathTraversalError(Exception):
    """Raised when path traversal attempt is detected"""
    pass


class PathValidator:
    """
    Secure path validation with canonical path resolution and base directory checking.
    
    Prevents path traversal attacks by:
    1. Canonicalizing paths to resolve all symbolic links and relative components
    2. Verifying resolved paths start with trusted base directories
    3. Rejecting any path that attempts to escape base directory boundaries
    """
    
    @staticmethod
    def validate_agent_name(agent_name: str) -> str:
        """
        Validate and sanitize agent name for safe file operations.
        
        Args:
            agent_name: Raw agent name input
            
        Returns:
            Sanitized agent name safe for file operations
            
        Raises:
            PathTraversalError: If agent name is invalid or contains dangerous characters
        """
        if not agent_name or not isinstance(agent_name, str):
            raise PathTraversalError("Agent name must be a non-empty string")
        
        # Allow only alphanumeric characters, hyphens, and underscores
        sanitized = "".join(c for c in agent_name if c.isalnum() or c in ['-', '_'])
        
        if not sanitized:
            raise PathTraversalError("Agent name contains no valid characters")
        
        # Prevent reserved names
        reserved_names = {'con', 'prn', 'aux', 'nul', 'com1', 'com2', 'com3', 'com4', 
                         'com5', 'com6', 'com7', 'com8', 'com9', 'lpt1', 'lpt2', 
                         'lpt3', 'lpt4', 'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9'}
        
        if sanitized.lower() in reserved_names:
            raise PathTraversalError(f"Agent name '{sanitized}' is reserved")
        
        # Limit length
        if len(sanitized) > 64:
            raise PathTraversalError("Agent name too long (max 64 characters)")
        
        return sanitized
    
    @staticmethod
    def validate_package_path(package_directory: Union[str, Path], agent_name: str) -> Path:
        """
        Validate agent package path within trusted base directory.
        
        Args:
            package_directory: Base directory for agent packages
            agent_name: Sanitized agent name
            
        Returns:
            Validated canonical package file path
            
        Raises:
            PathTraversalError: If path traversal attempt detected
        """
        try:
            # Canonicalize base directory
            base_path = Path(package_directory).resolve()
            
            # Construct package file path
            package_path = (base_path / f"{agent_name}.json").resolve()
            
            # Critical security check: ensure resolved path is within base directory
            if not str(package_path).startswith(str(base_path)):
                raise PathTraversalError(
                    f"Path traversal attempt detected: {package_path} is outside {base_path}"
                )
            
            return package_path
            
        except (OSError, ValueError) as e:
            raise PathTraversalError(f"Invalid path operation: {e}")
    
    @staticmethod
    def validate_base_directory(directory: Union[str, Path]) -> Path:
        """
        Validate base directory exists and is accessible.
        
        Args:
            directory: Directory path to validate
            
        Returns:
            Validated canonical directory path
            
        Raises:
            PathTraversalError: If directory is invalid or inaccessible
        """
        try:
            path = Path(directory).resolve()
            
            if not path.exists():
                raise PathTraversalError(f"Directory does not exist: {directory}")
            
            if not path.is_dir():
                raise PathTraversalError(f"Path is not a directory: {directory}")
            
            # Check read permissions
            if not os.access(path, os.R_OK):
                raise PathTraversalError(f"No read permission for directory: {directory}")
            
            return path
            
        except (OSError, PermissionError) as e:
            raise PathTraversalError(f"Directory validation failed: {e}")
    
    @staticmethod
    def validate_file_path(file_path: Union[str, Path], base_directory: Union[str, Path]) -> Path:
        """
        Validate file path is within base directory boundaries.
        
        Args:
            file_path: File path to validate
            base_directory: Trusted base directory
            
        Returns:
            Validated canonical file path
            
        Raises:
            PathTraversalError: If path traversal attempt detected
        """
        try:
            base_path = Path(base_directory).resolve()
            target_path = Path(file_path).resolve()
            
            # Security check: ensure target is within base directory
            if not str(target_path).startswith(str(base_path)):
                raise PathTraversalError(
                    f"Path traversal attempt: {target_path} is outside {base_path}"
                )
            
            return target_path
            
        except (OSError, ValueError) as e:
            raise PathTraversalError(f"File path validation failed: {e}")
    
    @staticmethod
    def sanitize_relative_path(file_path: str, max_length: int = 500) -> str:
        """
        Sanitize relative file path for safe display and logging.
        
        This is for display/logging purposes only - not for file operations.
        All actual file operations should use validate_file_path().
        
        Args:
            file_path: File path to sanitize
            max_length: Maximum allowed path length
            
        Returns:
            Sanitized path string for display
        """
        if not isinstance(file_path, str):
            return ""
        
        # Convert to Path to normalize
        try:
            path = Path(file_path)
            # Get normalized string representation
            sanitized = str(path.as_posix())  # Use forward slashes consistently
        except (OSError, ValueError):
            # If path is invalid, return empty string
            return ""
        
        # Remove any remaining dangerous patterns (defense in depth)
        dangerous_patterns = ['..', '//', '\\\\', '::', '~']
        for pattern in dangerous_patterns:
            sanitized = sanitized.replace(pattern, '_')
        
        # Limit length
        return sanitized[:max_length] if len(sanitized) > max_length else sanitized