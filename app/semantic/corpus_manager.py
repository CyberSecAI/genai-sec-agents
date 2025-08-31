"""
Corpus Manager for Semantic Search

Manages rule card corpus rendering and versioning for semtools integration.
Implements secure corpus management with integrity validation and freshness tracking.
"""

import os
import json
import yaml
import hashlib
import glob
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class CorpusData:
    """Container for corpus data with metadata."""
    
    def __init__(self, content: str, metadata: Dict[str, Any]):
        self.content = content
        self.metadata = metadata
        self.created_at = datetime.now(timezone.utc)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'content': self.content,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat()
        }


class CorpusMetadata:
    """Corpus metadata tracking version and freshness."""
    
    def __init__(self, version: str, source_hash: str, rule_count: int, size_bytes: int):
        self.version = version
        self.source_hash = source_hash
        self.rule_count = rule_count
        self.size_bytes = size_bytes
        self.created_at = datetime.now(timezone.utc)
        self.last_updated = self.created_at
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'version': self.version,
            'source_hash': self.source_hash,
            'rule_count': self.rule_count,
            'size_bytes': self.size_bytes,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat()
        }


class ValidationResult:
    """Result of corpus validation check."""
    
    def __init__(self, valid: bool, errors: List[str] = None, warnings: List[str] = None):
        self.valid = valid
        self.errors = errors or []
        self.warnings = warnings or []
        self.checked_at = datetime.now(timezone.utc)


class CorpusManager:
    """Manages rule card corpus rendering and versioning for semantic search."""
    
    def __init__(self, config_path: str = "app/semantic/config/corpus_config.yaml"):
        """Initialize corpus manager with configuration."""
        self.config_path = config_path
        self.config = self._load_config()
        self.corpus_path = self.config['corpus']['output']['path']
        self.max_size_mb = self.config['corpus']['output']['max_size_mb']
        
        # Ensure corpus directory exists
        Path(self.corpus_path).mkdir(parents=True, exist_ok=True)
        
    def _load_config(self) -> Dict[str, Any]:
        """Load corpus configuration with security validation."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
            # Validate required configuration sections
            required_sections = ['corpus', 'corpus.sources', 'corpus.output', 'corpus.security']
            for section in required_sections:
                keys = section.split('.')
                current = config
                for key in keys:
                    if key not in current:
                        raise ValueError(f"Missing required config section: {section}")
                    current = current[key]
                    
            return config
            
        except Exception as e:
            logger.error(f"Failed to load corpus config: {e}")
            raise
    
    def _sanitize_path(self, path: str) -> str:
        """Sanitize file path to prevent directory traversal."""
        # Convert to absolute path and resolve
        abs_path = Path(path).resolve()
        
        # Ensure path is within project boundaries
        project_root = Path(os.getcwd()).resolve()
        
        try:
            abs_path.relative_to(project_root)
        except ValueError:
            raise ValueError(f"Path traversal detected: {path}")
            
        return str(abs_path)
    
    def _compute_source_hash(self, sources: List[str]) -> str:
        """Compute hash of source files for freshness tracking."""
        hasher = hashlib.sha256()
        
        # Sort sources for consistent hashing
        sorted_sources = sorted(sources)
        
        for source in sorted_sources:
            try:
                with open(source, 'rb') as f:
                    hasher.update(f.read())
            except FileNotFoundError:
                logger.warning(f"Source file not found: {source}")
                continue
                
        return hasher.hexdigest()
    
    def _extract_rules_from_package(self, package_path: str) -> List[Dict[str, Any]]:
        """Extract rule cards from compiled agent package."""
        try:
            with open(package_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
                
            rules = package_data.get('rules_detail', [])
            logger.info(f"Extracted {len(rules)} rules from {package_path}")
            return rules
            
        except Exception as e:
            logger.error(f"Failed to extract rules from {package_path}: {e}")
            return []
    
    def _extract_rules_from_yaml(self, yaml_path: str) -> Dict[str, Any]:
        """Extract rule card from YAML file."""
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                rule_data = yaml.safe_load(f)
                
            # Add source file information
            rule_data['_source_file'] = yaml_path
            rule_data['_source_type'] = 'yaml'
            
            return rule_data
            
        except Exception as e:
            logger.error(f"Failed to extract rule from {yaml_path}: {e}")
            return {}
    
    def _format_rule_for_corpus(self, rule: Dict[str, Any]) -> str:
        """Format rule card for semtools corpus inclusion."""
        # Build searchable text content
        content_parts = []
        
        # Core rule information
        if 'id' in rule:
            content_parts.append(f"Rule ID: {rule['id']}")
        if 'title' in rule:
            content_parts.append(f"Title: {rule['title']}")
        if 'severity' in rule:
            content_parts.append(f"Severity: {rule['severity']}")
        if 'scope' in rule:
            content_parts.append(f"Scope: {rule['scope']}")
            
        # Security requirement
        if 'requirement' in rule:
            content_parts.append(f"Requirement: {rule['requirement']}")
            
        # Security practices
        if 'do' in rule and isinstance(rule['do'], list):
            content_parts.append("Secure Practices:")
            for practice in rule['do']:
                content_parts.append(f"  • {practice}")
                
        if 'dont' in rule and isinstance(rule['dont'], list):
            content_parts.append("Avoid These Patterns:")
            for pattern in rule['dont']:
                content_parts.append(f"  • {pattern}")
                
        # Detection methods
        if 'detect' in rule:
            content_parts.append("Detection Methods:")
            detect = rule['detect']
            for tool, patterns in detect.items():
                if isinstance(patterns, list):
                    content_parts.append(f"  {tool}: {', '.join(patterns)}")
                    
        # References
        if 'refs' in rule:
            refs = rule['refs']
            if 'cwe' in refs:
                content_parts.append(f"CWE: {', '.join(refs['cwe'])}")
            if 'asvs' in refs:
                content_parts.append(f"ASVS: {', '.join(refs['asvs'])}")
            if 'owasp' in refs:
                content_parts.append(f"OWASP: {', '.join(refs['owasp'])}")
                
        # Metadata for provenance
        content_parts.append(f"Source: {rule.get('_source_file', 'unknown')}")
        content_parts.append(f"Type: {rule.get('_source_type', 'compiled')}")
        
        return "\n".join(content_parts)
    
    def render_corpus_from_packages(self, agent_packages: List[str] = None) -> CorpusData:
        """Render compiled agent packages into searchable corpus."""
        if agent_packages is None:
            # Use packages from configuration
            package_pattern = self.config['corpus']['sources']['compiled_agent_packages']
            agent_packages = glob.glob(package_pattern)
            
        all_rules = []
        source_files = []
        
        # Extract rules from agent packages
        for package_path in agent_packages:
            sanitized_path = self._sanitize_path(package_path)
            source_files.append(sanitized_path)
            rules = self._extract_rules_from_package(sanitized_path)
            
            # Mark rules with package source
            for rule in rules:
                rule['_source_file'] = package_path
                rule['_source_type'] = 'compiled'
                
            all_rules.extend(rules)
            
        # Extract rules from YAML files
        yaml_pattern = self.config['corpus']['sources']['rule_cards']
        yaml_files = glob.glob(yaml_pattern, recursive=True)
        
        for yaml_path in yaml_files:
            sanitized_path = self._sanitize_path(yaml_path)
            source_files.append(sanitized_path)
            rule = self._extract_rules_from_yaml(sanitized_path)
            
            if rule:  # Only add non-empty rules
                all_rules.append(rule)
                
        # Format rules for corpus
        corpus_content_parts = []
        for rule in all_rules:
            formatted_rule = self._format_rule_for_corpus(rule)
            corpus_content_parts.append(formatted_rule)
            corpus_content_parts.append("=" * 50)  # Rule separator
            
        corpus_content = "\n".join(corpus_content_parts)
        
        # Check size limits
        size_bytes = len(corpus_content.encode('utf-8'))
        max_size_bytes = self.max_size_mb * 1024 * 1024
        
        if size_bytes > max_size_bytes:
            logger.warning(f"Corpus size ({size_bytes} bytes) exceeds limit ({max_size_bytes} bytes)")
            
        # Create metadata
        source_hash = self._compute_source_hash(source_files)
        metadata = CorpusMetadata(
            version=datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"),
            source_hash=source_hash,
            rule_count=len(all_rules),
            size_bytes=size_bytes
        )
        
        logger.info(f"Rendered corpus: {len(all_rules)} rules, {size_bytes} bytes")
        return CorpusData(corpus_content, metadata.to_dict())
    
    def update_corpus_incremental(self, new_rules: List[Dict[str, Any]]) -> bool:
        """Update corpus with new rule cards incrementally."""
        try:
            # Load existing corpus
            existing_corpus = self._load_existing_corpus()
            
            if not existing_corpus:
                logger.info("No existing corpus, creating new one")
                return self._save_corpus_from_rules(new_rules)
                
            # Format new rules and append
            new_content_parts = []
            for rule in new_rules:
                formatted_rule = self._format_rule_for_corpus(rule)
                new_content_parts.append(formatted_rule)
                new_content_parts.append("=" * 50)
                
            updated_content = existing_corpus['content'] + "\n" + "\n".join(new_content_parts)
            
            # Update metadata
            updated_metadata = existing_corpus['metadata'].copy()
            updated_metadata['rule_count'] += len(new_rules)
            updated_metadata['size_bytes'] = len(updated_content.encode('utf-8'))
            updated_metadata['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            # Save updated corpus
            corpus_data = CorpusData(updated_content, updated_metadata)
            return self._save_corpus(corpus_data)
            
        except Exception as e:
            logger.error(f"Failed to update corpus incrementally: {e}")
            return False
    
    def validate_corpus_integrity(self, corpus_path: str = None) -> ValidationResult:
        """Validate corpus against tampering and corruption."""
        if corpus_path is None:
            corpus_path = os.path.join(self.corpus_path, "corpus.json")
            
        errors = []
        warnings = []
        
        try:
            # Check file existence
            if not os.path.exists(corpus_path):
                errors.append(f"Corpus file not found: {corpus_path}")
                return ValidationResult(False, errors, warnings)
                
            # Load corpus data
            with open(corpus_path, 'r', encoding='utf-8') as f:
                corpus_data = json.load(f)
                
            # Validate required fields
            required_fields = ['content', 'metadata', 'created_at']
            for field in required_fields:
                if field not in corpus_data:
                    errors.append(f"Missing required field: {field}")
                    
            # Validate metadata structure
            if 'metadata' in corpus_data:
                metadata = corpus_data['metadata']
                required_meta_fields = ['version', 'source_hash', 'rule_count', 'size_bytes']
                for field in required_meta_fields:
                    if field not in metadata:
                        errors.append(f"Missing metadata field: {field}")
                        
            # Check content size consistency
            if 'content' in corpus_data and 'metadata' in corpus_data:
                actual_size = len(corpus_data['content'].encode('utf-8'))
                declared_size = corpus_data['metadata'].get('size_bytes', 0)
                
                if actual_size != declared_size:
                    errors.append(f"Size mismatch: actual={actual_size}, declared={declared_size}")
                    
            # Check file size limits
            file_size = os.path.getsize(corpus_path)
            max_size_bytes = self.max_size_mb * 1024 * 1024
            
            if file_size > max_size_bytes:
                warnings.append(f"Corpus size ({file_size} bytes) exceeds recommended limit ({max_size_bytes} bytes)")
                
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            
        is_valid = len(errors) == 0
        logger.info(f"Corpus validation: {'PASSED' if is_valid else 'FAILED'} ({len(errors)} errors, {len(warnings)} warnings)")
        
        return ValidationResult(is_valid, errors, warnings)
    
    def get_corpus_metadata(self) -> Optional[CorpusMetadata]:
        """Get corpus version, freshness, and statistics."""
        try:
            corpus_path = os.path.join(self.corpus_path, "corpus.json")
            
            if not os.path.exists(corpus_path):
                logger.warning("Corpus file not found")
                return None
                
            with open(corpus_path, 'r', encoding='utf-8') as f:
                corpus_data = json.load(f)
                
            metadata_dict = corpus_data.get('metadata', {})
            
            return CorpusMetadata(
                version=metadata_dict.get('version', 'unknown'),
                source_hash=metadata_dict.get('source_hash', ''),
                rule_count=metadata_dict.get('rule_count', 0),
                size_bytes=metadata_dict.get('size_bytes', 0)
            )
            
        except Exception as e:
            logger.error(f"Failed to get corpus metadata: {e}")
            return None
    
    def _load_existing_corpus(self) -> Optional[Dict[str, Any]]:
        """Load existing corpus data."""
        try:
            corpus_path = os.path.join(self.corpus_path, "corpus.json")
            
            if not os.path.exists(corpus_path):
                return None
                
            with open(corpus_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Failed to load existing corpus: {e}")
            return None
    
    def _save_corpus(self, corpus_data: CorpusData) -> bool:
        """Save corpus data to file."""
        try:
            corpus_path = os.path.join(self.corpus_path, "corpus.json")
            
            with open(corpus_path, 'w', encoding='utf-8') as f:
                json.dump(corpus_data.to_dict(), f, indent=2)
                
            logger.info(f"Corpus saved to {corpus_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save corpus: {e}")
            return False
    
    def _save_corpus_from_rules(self, rules: List[Dict[str, Any]]) -> bool:
        """Create and save corpus from rules list."""
        try:
            # Format rules for corpus
            content_parts = []
            for rule in rules:
                formatted_rule = self._format_rule_for_corpus(rule)
                content_parts.append(formatted_rule)
                content_parts.append("=" * 50)
                
            content = "\n".join(content_parts)
            
            # Create metadata
            size_bytes = len(content.encode('utf-8'))
            metadata = CorpusMetadata(
                version=datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"),
                source_hash=hashlib.sha256(content.encode('utf-8')).hexdigest(),
                rule_count=len(rules),
                size_bytes=size_bytes
            )
            
            corpus_data = CorpusData(content, metadata.to_dict())
            return self._save_corpus(corpus_data)
            
        except Exception as e:
            logger.error(f"Failed to save corpus from rules: {e}")
            return False