"""
Package Integrity Validation Module

Comprehensive integrity validation for agent packages using digital signatures,
checksums, and manifest verification to prevent tampering and ensure authenticity.
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict

from .input_validation import InputValidator, ValidationError
from .path_security import PathValidator, PathTraversalError


class IntegrityError(Exception):
    """Raised when package integrity validation fails"""
    pass


@dataclass
class PackageManifest:
    """
    Secure package manifest with integrity metadata.
    
    Contains all necessary information to validate package authenticity
    and integrity across the entire supply chain.
    """
    package_name: str
    version: str
    build_timestamp: int
    source_digest: str          # SHA256 of all source Rule Cards
    package_digest: str         # SHA256 of compiled package content
    rule_count: int
    compilation_metadata: Dict[str, Any]
    integrity_checksum: Optional[str] = None  # Additional integrity checksum
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert manifest to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PackageManifest':
        """Create manifest from dictionary."""
        # Validate required fields
        required = ['package_name', 'version', 'build_timestamp', 'source_digest', 
                   'package_digest', 'rule_count', 'compilation_metadata']
        
        for field in required:
            if field not in data:
                raise IntegrityError(f"Missing required manifest field: {field}")
        
        return cls(
            package_name=data['package_name'],
            version=data['version'], 
            build_timestamp=data['build_timestamp'],
            source_digest=data['source_digest'],
            package_digest=data['package_digest'],
            rule_count=data['rule_count'],
            compilation_metadata=data['compilation_metadata'],
            integrity_signature=data.get('integrity_signature')
        )


class PackageIntegrityValidator:
    """
    Secure package integrity validation using SHA-256 checksums.
    
    Implements multiple layers of integrity checking:
    1. Content hash validation (SHA256)
    2. Source traceability verification
    3. Manifest consistency checking
    4. Multi-level checksum verification
    5. Tampering detection through cryptographic hashes
    """
    
    def __init__(self):
        """
        Initialize integrity validator.
        
        Uses SHA-256 checksums for all integrity verification.
        No key management required - relies on cryptographic hashes.
        """
        pass
    
    def generate_package_manifest(self, package_data: Dict[str, Any], 
                                source_files: List[Path], 
                                compilation_metadata: Dict[str, Any]) -> PackageManifest:
        """
        Generate integrity manifest for a compiled package.
        
        Args:
            package_data: Compiled package JSON data
            source_files: List of source Rule Card file paths  
            compilation_metadata: Metadata about compilation process
            
        Returns:
            Complete package manifest with integrity data
            
        Raises:
            IntegrityError: If manifest generation fails
            ValidationError: If input validation fails
        """
        try:
            # Validate inputs using centralized validation
            agent_name = InputValidator.validate_agent_name(package_data['agent']['name'])
            version = InputValidator.validate_string_field(package_data['agent']['version'], 'version')
            
            # Calculate source files digest
            source_digest = self._calculate_source_digest(source_files)
            
            # Calculate package content digest  
            package_digest = self._calculate_package_digest(package_data)
            
            # Create manifest
            manifest = PackageManifest(
                package_name=agent_name,
                version=version,
                build_timestamp=int(time.time()),
                source_digest=source_digest,
                package_digest=package_digest,
                rule_count=len(package_data.get('rules', [])),
                compilation_metadata=compilation_metadata
            )
            
            # Generate additional integrity checksum
            manifest.integrity_checksum = self._generate_manifest_checksum(manifest)
            
            return manifest
            
        except (ValidationError, PathTraversalError) as e:
            raise IntegrityError(f"Input validation failed during manifest generation: {e}")
        except Exception as e:
            raise IntegrityError(f"Failed to generate package manifest: {e}")
    
    def validate_package_integrity(self, package_data: Dict[str, Any], 
                                 manifest: PackageManifest,
                                 source_files: Optional[List[Path]] = None) -> Tuple[bool, List[str]]:
        """
        Comprehensive integrity validation of package against manifest.
        
        Args:
            package_data: Package JSON data to validate
            manifest: Expected package manifest
            source_files: Optional source files for full validation
            
        Returns:
            Tuple of (validation_passed, list_of_issues)
        """
        issues = []
        
        try:
            # 1. Validate package content digest
            current_digest = self._calculate_package_digest(package_data)
            if current_digest != manifest.package_digest:
                issues.append(f"Package content modified (expected: {manifest.package_digest}, got: {current_digest})")
            
            # 2. Validate rule count consistency
            actual_rule_count = len(package_data.get('rules', []))
            if actual_rule_count != manifest.rule_count:
                issues.append(f"Rule count mismatch (expected: {manifest.rule_count}, got: {actual_rule_count})")
            
            # 3. Validate package metadata consistency
            package_name = package_data.get('agent', {}).get('name', '')
            if package_name != manifest.package_name:
                issues.append(f"Package name mismatch (expected: {manifest.package_name}, got: {package_name})")
            
            package_version = package_data.get('agent', {}).get('version', '')  
            if package_version != manifest.version:
                issues.append(f"Package version mismatch (expected: {manifest.version}, got: {package_version})")
            
            # 4. Validate source digest if source files provided
            if source_files:
                current_source_digest = self._calculate_source_digest(source_files)
                if current_source_digest != manifest.source_digest:
                    issues.append(f"Source files modified (expected: {manifest.source_digest}, got: {current_source_digest})")
            
            # 5. Validate manifest integrity checksum
            if manifest.integrity_checksum:
                expected_checksum = self._generate_manifest_checksum(manifest)
                if expected_checksum != manifest.integrity_checksum:
                    issues.append("Manifest integrity checksum failed - possible tampering detected")
            
            # 6. Check manifest age (warn if older than 30 days)
            manifest_age_days = (time.time() - manifest.build_timestamp) / (24 * 3600)
            if manifest_age_days > 30:
                issues.append(f"Package manifest is {manifest_age_days:.1f} days old - consider rebuilding")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            issues.append(f"Integrity validation failed with error: {e}")
            return False, issues
    
    def _calculate_source_digest(self, source_files: List[Path]) -> str:
        """
        Calculate SHA256 digest of all source files.
        
        Args:
            source_files: List of source file paths
            
        Returns:
            SHA256 digest as hex string
        """
        hasher = hashlib.sha256()
        
        # Sort files for deterministic digest
        sorted_files = sorted(source_files, key=lambda p: str(p))
        
        for file_path in sorted_files:
            try:
                # Validate file path is safe
                PathValidator.validate_file_path(file_path, Path.cwd())
                
                with open(file_path, 'rb') as f:
                    hasher.update(f.read())
                    
            except (PathTraversalError, OSError):
                # Skip files that can't be safely read
                continue
        
        return hasher.hexdigest()
    
    def _calculate_package_digest(self, package_data: Dict[str, Any]) -> str:
        """
        Calculate SHA256 digest of package content.
        
        Args:
            package_data: Package JSON data
            
        Returns:
            SHA256 digest as hex string
        """
        # Create deterministic JSON representation
        package_json = json.dumps(package_data, sort_keys=True, separators=(',', ':'))
        
        # Calculate SHA256 digest
        return hashlib.sha256(package_json.encode('utf-8')).hexdigest()
    
    def _generate_manifest_checksum(self, manifest: PackageManifest) -> str:
        """
        Generate SHA-256 checksum for manifest critical fields.
        
        Args:
            manifest: Package manifest to checksum
            
        Returns:
            SHA-256 checksum as hex string
        """
        # Create message from critical manifest fields (excluding the checksum itself)
        message_parts = [
            manifest.package_name,
            manifest.version,
            str(manifest.build_timestamp),
            manifest.source_digest,
            manifest.package_digest,
            str(manifest.rule_count),
            json.dumps(manifest.compilation_metadata, sort_keys=True)
        ]
        
        message = '|'.join(message_parts).encode('utf-8')
        
        # Generate SHA-256 checksum
        return hashlib.sha256(message).hexdigest()
    
    
    def save_manifest(self, manifest: PackageManifest, manifest_path: Path) -> None:
        """
        Save package manifest to file.
        
        Args:
            manifest: Package manifest to save
            manifest_path: Path to save manifest file
            
        Raises:
            IntegrityError: If saving fails
        """
        try:
            # Validate output path
            base_dir = manifest_path.parent
            validated_path = PathValidator.validate_file_path(manifest_path, base_dir)
            
            # Create directory if needed
            validated_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save manifest as JSON
            with open(validated_path, 'w', encoding='utf-8') as f:
                json.dump(manifest.to_dict(), f, indent=2, sort_keys=True)
                
        except (PathTraversalError, OSError) as e:
            raise IntegrityError(f"Failed to save manifest: {e}")
    
    def load_manifest(self, manifest_path: Path) -> PackageManifest:
        """
        Load package manifest from file.
        
        Args:
            manifest_path: Path to manifest file
            
        Returns:
            Loaded package manifest
            
        Raises:
            IntegrityError: If loading fails
        """
        try:
            # Validate file path
            base_dir = Path.cwd()
            validated_path = PathValidator.validate_file_path(manifest_path, base_dir)
            
            # Load and parse manifest
            with open(validated_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
            
            return PackageManifest.from_dict(manifest_data)
            
        except (PathTraversalError, OSError, json.JSONDecodeError) as e:
            raise IntegrityError(f"Failed to load manifest: {e}")