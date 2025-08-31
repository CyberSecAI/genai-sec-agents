#!/usr/bin/env python3
"""
Agent Compiler Toolchain
Transforms YAML Rule Cards into machine-readable JSON agent packages.

Security Features:
- Uses yaml.safe_load() to prevent deserialization attacks
- Validates all file paths to prevent directory traversal
- Comprehensive input validation and error handling
- Secure temporary file operations
"""

import argparse
import json
import yaml
import hashlib
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

# Import centralized security modules
from ..security import (InputValidator, ValidationError, PathValidator, PathTraversalError,
                       PackageIntegrityValidator, PackageManifest, IntegrityError)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class CompilerConfig:
    """Configuration for the compilation process."""
    manifest_path: str
    rule_cards_path: str
    output_path: str
    force_overwrite: bool = False


class SecurityError(Exception):
    """Raised when security validation fails."""
    pass


class CompilerError(Exception):
    """Raised when compilation fails."""
    pass


class RuleCardCompiler:
    """Secure Rule Card to JSON compiler."""
    
    def __init__(self, config: CompilerConfig):
        self.config = config
        self.manifest = None
        self.rule_cards = {}
        self.integrity_validator = PackageIntegrityValidator()
        self.source_files_used = []  # Track source files for integrity validation
        
    def load_manifest(self) -> Dict[str, Any]:
        """Load and validate the agent manifest file."""
        try:
            manifest_path = Path(self.config.manifest_path)
            if not manifest_path.exists():
                raise CompilerError(f"Manifest file not found: {manifest_path}")
                
            if not self._is_safe_path(manifest_path):
                raise SecurityError(f"Unsafe manifest path: {manifest_path}")
                
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = yaml.safe_load(f)  # Security: prevent code execution
                
            if not isinstance(manifest, dict):
                raise CompilerError("Manifest must be a YAML dictionary")
                
            if 'agents' not in manifest:
                raise CompilerError("Manifest must contain 'agents' section")
                
            self.manifest = manifest
            logger.info(f"Loaded manifest with {len(manifest['agents'])} agents")
            return manifest
            
        except yaml.YAMLError as e:
            raise CompilerError(f"Invalid YAML in manifest: {e}")
        except Exception as e:
            logger.error(f"Failed to load manifest: {e}")
            raise CompilerError(f"Manifest loading failed: {e}")
    
    def load_rule_cards(self, patterns: List[str]) -> List[Dict[str, Any]]:
        """Load Rule Cards matching the given patterns."""
        rule_cards = []
        base_path = Path(self.config.rule_cards_path)
        
        if not base_path.exists():
            raise CompilerError(f"Rule cards directory not found: {base_path}")
            
        for pattern in patterns:
            # Security: validate pattern to prevent path traversal
            if '..' in pattern or pattern.startswith('/'):
                raise SecurityError(f"Unsafe rule card pattern: {pattern}")
                
            try:
                matching_files = list(base_path.glob(pattern))
                
                for file_path in matching_files:
                    if not self._is_safe_path(file_path):
                        logger.warning(f"Skipping unsafe path: {file_path}")
                        continue
                        
                    rule_card = self._load_single_rule_card(file_path)
                    if rule_card:
                        rule_card['_source_file'] = str(file_path.relative_to(base_path))
                        rule_cards.append(rule_card)
                        # Track source file for integrity validation
                        if file_path not in self.source_files_used:
                            self.source_files_used.append(file_path)
                        
            except Exception as e:
                logger.error(f"Error processing pattern {pattern}: {e}")
                raise CompilerError(f"Failed to load rule cards for pattern {pattern}: {e}")
                
        logger.info(f"Loaded {len(rule_cards)} rule cards")
        return rule_cards
    
    def _load_single_rule_card(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load and validate a single Rule Card file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                rule_card = yaml.safe_load(f)  # Security: prevent code execution
                
            if not isinstance(rule_card, dict):
                logger.warning(f"Skipping non-dict rule card: {file_path}")
                return None
                
            # Validate required fields
            required_fields = ['id', 'title', 'severity', 'scope', 'requirement', 'do', 'dont', 'detect', 'verify', 'refs']
            missing_fields = [field for field in required_fields if field not in rule_card]
            
            if missing_fields:
                logger.warning(f"Rule card {file_path} missing fields: {missing_fields}")
                return None
            
            # Validate critical string fields using centralized validation
            try:
                rule_card['id'] = InputValidator.validate_string_field(rule_card['id'], 'rule_card_id')
                rule_card['title'] = InputValidator.validate_string_field(rule_card['title'], 'rule_card_title')
            except ValidationError as e:
                logger.warning(f"Rule card {file_path} validation failed: {e}")
                return None
                
            return rule_card
            
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return None
    
    def _is_safe_path(self, path: Path) -> bool:
        """Validate that path is safe and doesn't allow traversal attacks."""
        try:
            # Security: check for path traversal attempts
            resolved = path.resolve()
            base_dir = Path(self.config.rule_cards_path).resolve()
            
            # Ensure path is within expected directory
            return str(resolved).startswith(str(base_dir)) or str(resolved).startswith(str(Path(self.config.manifest_path).parent.resolve()))
        except Exception:
            return False
    
    def generate_metadata(self) -> Dict[str, Any]:
        """Generate package metadata with version, build date, and source digest."""
        try:
            # Generate version from Git commit
            version = self._get_git_version()
            
            # Build date in ISO format
            build_date = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            
            # Source digest of all rule card files
            source_digest = self._calculate_source_digest()
            
            # Attribution notice
            attribution = self._get_attribution_notice()
            
            return {
                'version': version,
                'build_date': build_date,
                'source_digest': source_digest,
                'attribution': attribution,
                'compiler_version': '1.0.0'
            }
            
        except Exception as e:
            logger.error(f"Failed to generate metadata: {e}")
            raise CompilerError(f"Metadata generation failed: {e}")
    
    def _get_git_version(self) -> str:
        """Generate version string from Git commit hash and timestamp."""
        try:
            # Security: Validate git working directory is within project boundaries
            cwd_path = self._validate_git_working_directory(
                Path(self.config.rule_cards_path).parent
            )
            commit_hash = subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'], 
                cwd=cwd_path,
                text=True,
                timeout=10  # Add timeout protection
            ).strip()
            timestamp = int(time.time())
            return f"{commit_hash[:8]}-{timestamp}"
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            # Fallback if not in Git repository or timeout
            timestamp = int(time.time())
            return f"local-{timestamp}"
    
    def _validate_git_working_directory(self, path: Path) -> Path:
        """Validate git working directory is within project boundaries.
        
        Args:
            path: Path to validate for git operations
            
        Returns:
            Path: Validated and resolved path
            
        Raises:
            SecurityError: If path is outside project directory
        """
        try:
            # Resolve symbolic links and normalize path
            resolved_path = path.resolve()
            project_root = Path(__file__).parent.parent.parent.resolve()
            
            # Ensure cwd is within project boundaries
            if not str(resolved_path).startswith(str(project_root)):
                raise SecurityError(
                    f"Git operation attempted outside project directory: {path}"
                )
            
            # Verify the path exists and is accessible
            if not resolved_path.exists():
                raise SecurityError(f"Git working directory does not exist: {path}")
                
            return resolved_path
            
        except (OSError, ValueError) as e:
            raise SecurityError(f"Invalid git working directory: {e}")
    
    def _calculate_source_digest(self) -> str:
        """Calculate SHA256 digest of all source Rule Card files."""
        hasher = hashlib.sha256()
        base_path = Path(self.config.rule_cards_path)
        
        # Sort files for deterministic digest
        rule_files = sorted(base_path.rglob('*.yml'))
        
        for file_path in rule_files:
            if self._is_safe_path(file_path):
                try:
                    with open(file_path, 'rb') as f:
                        hasher.update(f.read())
                except Exception as e:
                    logger.warning(f"Could not include {file_path} in digest: {e}")
                    
        return f"sha256:{hasher.hexdigest()}"
    
    def _get_attribution_notice(self) -> str:
        """Load attribution notice from ATTRIBUTION.md."""
        try:
            attribution_path = Path(self.config.rule_cards_path).parent.parent / 'docs' / 'ATTRIBUTION.md'
            if attribution_path.exists():
                with open(attribution_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            else:
                return "Generated by GenAI Security Agents Rule Card Compiler"
        except Exception:
            return "Generated by GenAI Security Agents Rule Card Compiler"
    
    def aggregate_validation_hooks(self, rule_cards: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Aggregate detect metadata into unified validation hooks."""
        hooks = {}
        
        for rule_card in rule_cards:
            detect_config = rule_card.get('detect', {})
            
            for tool, rules in detect_config.items():
                if not isinstance(rules, list):
                    logger.warning(f"Invalid detect config in {rule_card.get('id', 'unknown')}: {tool}")
                    continue
                    
                if tool not in hooks:
                    hooks[tool] = []
                    
                # Security: validate rule references
                for rule in rules:
                    if isinstance(rule, str) and len(rule.strip()) > 0:
                        if rule not in hooks[tool]:  # Deduplicate
                            hooks[tool].append(rule)
                    else:
                        logger.warning(f"Invalid rule reference in {rule_card.get('id', 'unknown')}: {rule}")
        
        # Sort for deterministic output
        for tool in hooks:
            hooks[tool].sort()
            
        logger.info(f"Aggregated validation hooks for {len(hooks)} tools")
        return hooks
    
    def compile_agent(self, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """Compile a single agent based on its configuration."""
        agent_name = agent_config['name']
        logger.info(f"Compiling agent: {agent_name}")
        
        # Load Rule Cards for this agent
        rule_cards = self.load_rule_cards(agent_config['rule_cards'])
        
        if not rule_cards:
            raise CompilerError(f"No rule cards found for agent {agent_name}")
        
        # Generate metadata
        metadata = self.generate_metadata()
        
        # Aggregate validation hooks
        validation_hooks = self.aggregate_validation_hooks(rule_cards)
        
        # Remove internal fields from rule cards
        clean_rule_cards = []
        for rule_card in rule_cards:
            clean_card = {k: v for k, v in rule_card.items() if not k.startswith('_')}
            clean_rule_cards.append(clean_card)
        
        # Build agent package
        agent_package = {
            'agent': {
                'name': agent_name,
                'description': agent_config['description'],
                'domains': agent_config.get('domains', []),
                **metadata
            },
            'rules': clean_rule_cards,
            'validation_hooks': validation_hooks,
            'schema_version': self.manifest.get('compilation', {}).get('schema_version', '1.0')
        }
        
        logger.info(f"Compiled {agent_name}: {len(clean_rule_cards)} rules, {len(validation_hooks)} hook types")
        
        # Generate package manifest for integrity validation
        try:
            compilation_metadata = {
                'compiler_version': '1.0.0',
                'compilation_timestamp': metadata.get('build_date', ''),
                'source_rule_cards': len(clean_rule_cards),
                'validation_hooks_count': len(validation_hooks)
            }
            
            package_manifest = self.integrity_validator.generate_package_manifest(
                agent_package, 
                self.source_files_used,
                compilation_metadata
            )
            
            # Add manifest metadata to package
            agent_package['_integrity_manifest'] = package_manifest.to_dict()
            
            logger.info(f"Generated integrity manifest for {agent_name}")
            
        except IntegrityError as e:
            logger.warning(f"Failed to generate integrity manifest for {agent_name}: {e}")
            # Continue without manifest - not critical for basic compilation
        
        return agent_package
    
    def save_agent_package(self, agent_package: Dict[str, Any], output_file: str) -> Path:
        """Save compiled agent package to JSON file."""
        output_path = Path(self.config.output_path) / output_file
        
        # Security: validate output path
        if not self._is_safe_output_path(output_path):
            raise SecurityError(f"Unsafe output path: {output_path}")
        
        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Save main package file
            with open(output_path, 'w', encoding='utf-8') as f:
                # Remove manifest from package data before saving
                package_to_save = {k: v for k, v in agent_package.items() if k != '_integrity_manifest'}
                json.dump(package_to_save, f, indent=2, sort_keys=True)
            
            # Save separate manifest file if integrity manifest was generated
            if '_integrity_manifest' in agent_package:
                try:
                    manifest_path = output_path.with_suffix('.manifest.json')
                    manifest_data = agent_package['_integrity_manifest']
                    manifest = PackageManifest.from_dict(manifest_data)
                    
                    self.integrity_validator.save_manifest(manifest, manifest_path)
                    logger.info(f"Saved integrity manifest: {manifest_path}")
                    
                except (IntegrityError, Exception) as e:
                    logger.warning(f"Failed to save manifest file: {e}")
            
            logger.info(f"Saved agent package: {output_path}")
            return output_path
            
        except Exception as e:
            raise CompilerError(f"Failed to save agent package {output_file}: {e}")
    
    def _is_safe_output_path(self, path: Path) -> bool:
        """Validate output path is safe."""
        try:
            resolved = path.resolve()
            base_output = Path(self.config.output_path).resolve()
            return str(resolved).startswith(str(base_output))
        except Exception:
            return False
    
    def compile_all_agents(self) -> List[Path]:
        """Compile all agents defined in the manifest."""
        if not self.manifest:
            raise CompilerError("Manifest not loaded. Call load_manifest() first.")
        
        compiled_packages = []
        
        for agent_config in self.manifest['agents']:
            try:
                agent_package = self.compile_agent(agent_config)
                output_path = self.save_agent_package(agent_package, agent_config['output_file'])
                compiled_packages.append(output_path)
                
            except Exception as e:
                logger.error(f"Failed to compile agent {agent_config['name']}: {e}")
                if not self.config.force_overwrite:
                    raise CompilerError(f"Agent compilation failed: {agent_config['name']}")
        
        logger.info(f"Successfully compiled {len(compiled_packages)} agent packages")
        return compiled_packages


def main():
    """Main entry point for the compiler."""
    parser = argparse.ArgumentParser(
        description='Compile YAML Rule Cards into JSON agent packages',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Use default paths
  %(prog)s --manifest custom_manifest.yml    # Custom manifest
  %(prog)s --output dist/custom/             # Custom output directory
  %(prog)s --force                           # Overwrite existing packages
        """
    )
    
    parser.add_argument(
        '--manifest',
        default='app/tools/agents_manifest.yml',
        help='Path to agent manifest file (default: app/tools/agents_manifest.yml)'
    )
    
    parser.add_argument(
        '--rule-cards',
        default='app/rule_cards/',
        help='Path to Rule Cards directory (default: app/rule_cards/)'
    )
    
    parser.add_argument(
        '--output',
        default='app/dist/agents/',
        help='Output directory for compiled packages (default: app/dist/agents/)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing agent packages'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create compiler configuration
    config = CompilerConfig(
        manifest_path=args.manifest,
        rule_cards_path=args.rule_cards,
        output_path=args.output,
        force_overwrite=args.force
    )
    
    try:
        # Initialize compiler
        compiler = RuleCardCompiler(config)
        
        # Load manifest
        manifest = compiler.load_manifest()
        logger.info(f"Starting compilation of {len(manifest['agents'])} agents")
        
        # Compile all agents
        compiled_packages = compiler.compile_all_agents()
        
        # Success summary
        print(f"\n✅ Compilation successful!")
        print(f"📦 Generated {len(compiled_packages)} agent packages:")
        for package_path in compiled_packages:
            print(f"  - {package_path}")
        
        return 0
        
    except SecurityError as e:
        logger.error(f"Security validation failed: {e}")
        print(f"❌ Security Error: {e}")
        return 1
        
    except CompilerError as e:
        logger.error(f"Compilation failed: {e}")
        print(f"❌ Compilation Error: {e}")
        return 1
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected Error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())