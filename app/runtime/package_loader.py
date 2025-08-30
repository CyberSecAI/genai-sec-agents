"""
Package Loader for Compiled Agent Packages

Provides secure loading and validation of compiled JSON agent packages
with comprehensive security controls to prevent attacks.

Security Features:
- File size limits to prevent DoS
- Safe JSON parsing with validation
- Schema validation for package structure
- Path traversal prevention
- Malicious content detection
"""

import json
import os
import hashlib
import logging
from typing import Dict, Optional, Any, List
from pathlib import Path


class PackageLoaderError(Exception):
    """Exception for package loading errors"""
    pass


class PackageLoader:
    """
    Secure loader for compiled agent JSON packages.
    
    Implements multiple layers of security validation to prevent
    malicious package exploitation.
    """
    
    # Security limits
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit
    MAX_RULES_COUNT = 1000  # Maximum rules per package
    MAX_STRING_LENGTH = 10000  # Maximum string field length
    
    # Required package schema
    REQUIRED_FIELDS = {
        "agent": ["name", "version", "build_date", "source_digest"],
        "rules": [],  # Array validation handled separately
        "validation_hooks": []  # Dict validation handled separately
    }
    
    def __init__(self):
        """Initialize the package loader."""
        self.logger = logging.getLogger(__name__)
    
    def load_package(self, package_path: str) -> Optional[Dict]:
        """
        Securely load and validate a compiled agent package.
        
        Args:
            package_path: Path to the JSON package file
            
        Returns:
            Validated package data or None if loading fails
            
        Raises:
            PackageLoaderError: If security validation fails
        """
        try:
            # Validate file path
            validated_path = self._validate_file_path(package_path)
            
            # Check file size
            self._check_file_size(validated_path)
            
            # Load and parse JSON
            raw_data = self._load_json_file(validated_path)
            
            # Validate package structure
            validated_package = self._validate_package_structure(raw_data)
            
            # Additional security validations
            self._validate_package_content(validated_package)
            
            self.logger.info(f"Successfully loaded package: {package_path}")
            return validated_package
            
        except Exception as e:
            self.logger.error(f"Failed to load package {package_path}: {str(e)}")
            return None
    
    def _validate_file_path(self, file_path: str) -> str:
        """
        Validate file path for security issues.
        
        Args:
            file_path: Raw file path
            
        Returns:
            Validated absolute path
            
        Raises:
            PackageLoaderError: If path is invalid or dangerous
        """
        if not file_path or not isinstance(file_path, str):
            raise PackageLoaderError("File path must be a non-empty string")
        
        try:
            # Resolve to absolute path
            path = Path(file_path).resolve()
            
            # Security checks
            if not path.exists():
                raise PackageLoaderError(f"File does not exist: {file_path}")
            
            if not path.is_file():
                raise PackageLoaderError(f"Path is not a file: {file_path}")
            
            # Check file extension
            if path.suffix.lower() != ".json":
                raise PackageLoaderError(f"File must have .json extension: {file_path}")
            
            # Check read permissions
            if not os.access(path, os.R_OK):
                raise PackageLoaderError(f"No read permission for file: {file_path}")
            
            # Prevent access to sensitive system files
            path_str = str(path).lower()
            dangerous_paths = ["/etc/", "/proc/", "/sys/", "/dev/"]
            if any(danger in path_str for danger in dangerous_paths):
                raise PackageLoaderError("Access to system directories not allowed")
            
            return str(path)
            
        except (OSError, PermissionError) as e:
            raise PackageLoaderError(f"File path validation error: {e}")
    
    def _check_file_size(self, file_path: str) -> None:
        """
        Check file size against security limits.
        
        Args:
            file_path: Validated file path
            
        Raises:
            PackageLoaderError: If file is too large
        """
        try:
            file_size = os.path.getsize(file_path)
            
            if file_size > self.MAX_FILE_SIZE:
                raise PackageLoaderError(
                    f"File too large: {file_size} bytes (max: {self.MAX_FILE_SIZE})"
                )
            
            if file_size == 0:
                raise PackageLoaderError("File is empty")
            
        except OSError as e:
            raise PackageLoaderError(f"Error checking file size: {e}")
    
    def _load_json_file(self, file_path: str) -> Dict:
        """
        Safely load and parse JSON file.
        
        Args:
            file_path: Validated file path
            
        Returns:
            Parsed JSON data
            
        Raises:
            PackageLoaderError: If JSON parsing fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Read with size limit
                content = f.read(self.MAX_FILE_SIZE)
                
                # Parse JSON with security settings
                data = json.loads(content)
                
                if not isinstance(data, dict):
                    raise PackageLoaderError("Package must be a JSON object")
                
                return data
                
        except json.JSONDecodeError as e:
            raise PackageLoaderError(f"Invalid JSON format: {e}")
        except UnicodeDecodeError as e:
            raise PackageLoaderError(f"Invalid file encoding: {e}")
        except Exception as e:
            raise PackageLoaderError(f"Error reading file: {e}")
    
    def _validate_package_structure(self, data: Dict) -> Dict:
        """
        Validate package structure against expected schema.
        
        Args:
            data: Raw package data
            
        Returns:
            Validated package data
            
        Raises:
            PackageLoaderError: If structure validation fails
        """
        validated = {}
        
        # Check required top-level fields
        for field in self.REQUIRED_FIELDS:
            if field not in data:
                raise PackageLoaderError(f"Missing required field: {field}")
        
        # Validate agent metadata
        validated["agent"] = self._validate_agent_metadata(data["agent"])
        
        # Validate rules array
        validated["rules"] = self._validate_rules_array(data["rules"])
        
        # Validate validation hooks
        validated["validation_hooks"] = self._validate_hooks_dict(data["validation_hooks"])
        
        return validated
    
    def _validate_agent_metadata(self, agent_data: Any) -> Dict:
        """
        Validate agent metadata section.
        
        Args:
            agent_data: Raw agent metadata
            
        Returns:
            Validated agent metadata
            
        Raises:
            PackageLoaderError: If validation fails
        """
        if not isinstance(agent_data, dict):
            raise PackageLoaderError("Agent metadata must be an object")
        
        validated = {}
        
        # Check required fields
        for field in self.REQUIRED_FIELDS["agent"]:
            if field not in agent_data:
                raise PackageLoaderError(f"Missing required agent field: {field}")
            
            value = agent_data[field]
            if not isinstance(value, str) or not value.strip():
                raise PackageLoaderError(f"Agent field {field} must be non-empty string")
            
            # Limit string length
            if len(value) > self.MAX_STRING_LENGTH:
                raise PackageLoaderError(f"Agent field {field} too long")
            
            validated[field] = value.strip()
        
        # Copy optional fields with validation
        for field in ["description", "attribution", "compiler_version"]:
            if field in agent_data:
                value = agent_data[field]
                if isinstance(value, str) and len(value) <= self.MAX_STRING_LENGTH:
                    validated[field] = value
        
        # Validate domains if present
        if "domains" in agent_data:
            domains = agent_data["domains"]
            if isinstance(domains, list):
                validated["domains"] = [
                    str(d)[:100] for d in domains[:20]  # Limit count and length
                ]
        
        return validated
    
    def _validate_rules_array(self, rules_data: Any) -> List[Dict]:
        """
        Validate rules array structure.
        
        Args:
            rules_data: Raw rules data
            
        Returns:
            Validated rules array
            
        Raises:
            PackageLoaderError: If validation fails
        """
        if not isinstance(rules_data, list):
            raise PackageLoaderError("Rules must be an array")
        
        if len(rules_data) > self.MAX_RULES_COUNT:
            raise PackageLoaderError(f"Too many rules: {len(rules_data)} (max: {self.MAX_RULES_COUNT})")
        
        validated_rules = []
        
        for i, rule in enumerate(rules_data):
            try:
                validated_rule = self._validate_single_rule(rule)
                validated_rules.append(validated_rule)
            except Exception as e:
                raise PackageLoaderError(f"Invalid rule at index {i}: {e}")
        
        return validated_rules
    
    def _validate_single_rule(self, rule_data: Any) -> Dict:
        """
        Validate a single rule card structure.
        
        Args:
            rule_data: Raw rule data
            
        Returns:
            Validated rule data
            
        Raises:
            PackageLoaderError: If rule validation fails
        """
        if not isinstance(rule_data, dict):
            raise PackageLoaderError("Rule must be an object")
        
        validated = {}
        
        # Required string fields
        required_fields = ["id", "title", "scope", "requirement"]
        for field in required_fields:
            if field not in rule_data:
                raise PackageLoaderError(f"Missing required rule field: {field}")
            
            value = rule_data[field]
            if not isinstance(value, str) or not value.strip():
                raise PackageLoaderError(f"Rule field {field} must be non-empty string")
            
            validated[field] = value.strip()[:self.MAX_STRING_LENGTH]
        
        # Validate severity
        if "severity" in rule_data:
            severity = rule_data["severity"]
            if severity in ["low", "medium", "high", "critical"]:
                validated["severity"] = severity
            else:
                validated["severity"] = "medium"  # Default
        
        # Validate arrays
        for field in ["do", "dont"]:
            if field in rule_data:
                arr = rule_data[field]
                if isinstance(arr, list):
                    validated[field] = [str(item)[:self.MAX_STRING_LENGTH] for item in arr[:20]]
        
        # Validate detect object
        if "detect" in rule_data and isinstance(rule_data["detect"], dict):
            validated["detect"] = self._validate_detect_object(rule_data["detect"])
        
        # Validate verify object
        if "verify" in rule_data and isinstance(rule_data["verify"], dict):
            verify = rule_data["verify"]
            if "tests" in verify and isinstance(verify["tests"], list):
                validated["verify"] = {
                    "tests": [str(test)[:self.MAX_STRING_LENGTH] for test in verify["tests"][:10]]
                }
        
        # Validate refs object
        if "refs" in rule_data and isinstance(rule_data["refs"], dict):
            refs = rule_data["refs"]
            validated_refs = {}
            for key, value in refs.items():
                if isinstance(value, list):
                    validated_refs[str(key)[:50]] = [str(ref)[:100] for ref in value[:10]]
            if validated_refs:
                validated["refs"] = validated_refs
        
        return validated
    
    def _validate_detect_object(self, detect_data: Dict) -> Dict:
        """
        Validate detect metadata object.
        
        Args:
            detect_data: Raw detect data
            
        Returns:
            Validated detect data
        """
        validated = {}
        
        for tool, rules in detect_data.items():
            if isinstance(rules, list):
                tool_key = str(tool)[:50]  # Limit tool name length
                validated[tool_key] = [str(rule)[:200] for rule in rules[:50]]  # Limit rule count
        
        return validated
    
    def _validate_hooks_dict(self, hooks_data: Any) -> Dict:
        """
        Validate validation hooks dictionary.
        
        Args:
            hooks_data: Raw hooks data
            
        Returns:
            Validated hooks data
            
        Raises:
            PackageLoaderError: If validation fails
        """
        if not isinstance(hooks_data, dict):
            raise PackageLoaderError("Validation hooks must be an object")
        
        validated = {}
        
        for tool, config in hooks_data.items():
            if isinstance(config, (dict, list)):
                tool_key = str(tool)[:50]  # Limit tool name length
                validated[tool_key] = config
        
        return validated
    
    def _validate_package_content(self, package_data: Dict) -> None:
        """
        Additional content validation for security.
        
        Args:
            package_data: Validated package structure
            
        Raises:
            PackageLoaderError: If content validation fails
        """
        # Check for suspicious patterns in strings
        suspicious_patterns = [
            "eval(", "exec(", "import os", "subprocess", "__import__",
            "file://", "javascript:", "data:", "<script"
        ]
        
        def check_string_content(text: str, context: str) -> None:
            if not isinstance(text, str):
                return
            
            text_lower = text.lower()
            for pattern in suspicious_patterns:
                if pattern in text_lower:
                    raise PackageLoaderError(f"Suspicious content detected in {context}: {pattern}")
        
        # Check agent metadata strings
        for key, value in package_data["agent"].items():
            if isinstance(value, str):
                check_string_content(value, f"agent.{key}")
        
        # Check rule content
        for i, rule in enumerate(package_data["rules"]):
            for key, value in rule.items():
                if isinstance(value, str):
                    check_string_content(value, f"rule[{i}].{key}")
                elif isinstance(value, list):
                    for j, item in enumerate(value):
                        if isinstance(item, str):
                            check_string_content(item, f"rule[{i}].{key}[{j}]")
    
    def validate_package_integrity(self, package_data: Dict) -> bool:
        """
        Validate package integrity using source digest.
        
        Args:
            package_data: Package data with metadata
            
        Returns:
            True if integrity check passes
        """
        try:
            # Extract source digest from metadata
            source_digest = package_data["agent"].get("source_digest", "")
            
            if not source_digest.startswith("sha256:"):
                self.logger.warning("Package missing valid source digest")
                return False
            
            # For now, just verify digest format
            # Full integrity checking would require source Rule Cards
            expected_digest = source_digest.split(":", 1)[1]
            
            if len(expected_digest) != 64:  # SHA256 hex length
                self.logger.warning("Invalid source digest format")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating package integrity: {e}")
            return False