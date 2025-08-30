#!/usr/bin/env python3
"""
Secure Rule Card Validator
Validates YAML Rule Cards against schema with security controls
"""
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml
import jsonschema
from jsonschema import validate, ValidationError

class SecureRuleCardValidator:
    """Secure validator for Rule Cards with YAML safety controls"""
    
    def __init__(self, schema_path: str):
        self.schema = self._load_schema(schema_path)
        self.validation_errors = []
        self.security_warnings = []
    
    def _load_schema(self, schema_path: str) -> Dict[str, Any]:
        """Load JSON schema with enhanced path validation"""
        validated_path = self._validate_schema_path(schema_path)
        
        try:
            with open(validated_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise ValueError(f"Failed to load schema: {e}")
    
    def _validate_schema_path(self, schema_path: str) -> str:
        """Enhanced path validation with multiple security layers.
        
        Args:
            schema_path: Path to validate
            
        Returns:
            str: Validated absolute path
            
        Raises:
            ValueError: If path validation fails
        """
        if not schema_path or not isinstance(schema_path, str):
            raise ValueError("Schema path must be a non-empty string")
        
        try:
            # Resolve symbolic links and normalize path
            safe_path = Path(schema_path).resolve()
            project_root = Path(__file__).parent.parent.parent.resolve()
            
            # Multiple validation layers
            if not str(safe_path).startswith(str(project_root)):
                raise ValueError(f"Schema path outside project: {schema_path}")
            
            if not safe_path.exists():
                raise ValueError(f"Schema file does not exist: {schema_path}")
                
            if not safe_path.is_file():
                raise ValueError(f"Schema path is not a file: {schema_path}")
            
            # Additional security check for file size (prevent DoS)
            file_size = safe_path.stat().st_size
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                raise ValueError(f"Schema file too large: {file_size} bytes")
                
            return str(safe_path)
            
        except (OSError, ValueError) as e:
            raise ValueError(f"Invalid schema path: {e}")
    
    def _safe_load_yaml(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Securely load YAML file using safe_load"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Security: Use safe_load to prevent code execution
                data = yaml.safe_load(f)
                
                # Security: Validate data type
                if not isinstance(data, dict):
                    self.security_warnings.append(
                        f"{file_path}: YAML root must be object, got {type(data).__name__}"
                    )
                    return None
                
                return data
                
        except yaml.YAMLError as e:
            self.validation_errors.append(f"{file_path}: Invalid YAML - {e}")
            return None
        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            self.validation_errors.append(f"{file_path}: File error - {e}")
            return None
    
    def validate_rule_card(self, file_path: str) -> bool:
        """Validate single Rule Card file"""
        # Security: Sanitize file path
        safe_path = os.path.normpath(file_path)
        
        # Load YAML safely
        rule_data = self._safe_load_yaml(safe_path)
        if rule_data is None:
            return False
        
        # Validate against schema
        try:
            validate(instance=rule_data, schema=self.schema)
            print(f"✅ {file_path}: Valid Rule Card")
            return True
            
        except ValidationError as e:
            self.validation_errors.append(
                f"{file_path}: Schema validation failed - {e.message}"
            )
            return False
    
    def validate_directory(self, directory: str) -> Dict[str, int]:
        """Validate all YAML files in directory"""
        # Security: Validate directory path
        safe_dir = os.path.normpath(directory)
        if not os.path.isdir(safe_dir):
            raise ValueError(f"Invalid directory: {directory}")
        
        results = {"valid": 0, "invalid": 0, "total": 0}
        
        # Find all .yml and .yaml files
        yaml_files = []
        for ext in ['*.yml', '*.yaml']:
            yaml_files.extend(Path(safe_dir).rglob(ext))
        
        for yaml_file in yaml_files:
            results["total"] += 1
            if self.validate_rule_card(str(yaml_file)):
                results["valid"] += 1
            else:
                results["invalid"] += 1
        
        return results
    
    def print_summary(self, results: Dict[str, int]):
        """Print validation summary"""
        print(f"\n📊 Validation Summary:")
        print(f"   Total files: {results['total']}")
        print(f"   Valid: {results['valid']}")
        print(f"   Invalid: {results['invalid']}")
        
        if self.security_warnings:
            print(f"\n⚠️  Security Warnings:")
            for warning in self.security_warnings:
                print(f"   {warning}")
        
        if self.validation_errors:
            print(f"\n❌ Validation Errors:")
            for error in self.validation_errors:
                print(f"   {error}")

def main():
    parser = argparse.ArgumentParser(description="Validate Rule Card YAML files")
    parser.add_argument("path", help="File or directory to validate")
    parser.add_argument("--schema", default="app/tools/rule-card-schema.json", 
                       help="Path to JSON schema file")
    
    args = parser.parse_args()
    
    try:
        validator = SecureRuleCardValidator(args.schema)
        
        if os.path.isfile(args.path):
            # Validate single file
            is_valid = validator.validate_rule_card(args.path)
            sys.exit(0 if is_valid else 1)
        
        elif os.path.isdir(args.path):
            # Validate directory
            results = validator.validate_directory(args.path)
            validator.print_summary(results)
            sys.exit(0 if results["invalid"] == 0 else 1)
        
        else:
            print(f"❌ Path does not exist: {args.path}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()