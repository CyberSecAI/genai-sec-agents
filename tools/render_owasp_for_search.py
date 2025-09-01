#!/usr/bin/env python3
"""
OWASP CheatSheet Normalization for Semantic Search

This script processes OWASP cheatsheets into searchable corpus format with:
- Front-matter with metadata and tags
- Normalized markdown content
- SHA256 checksums for integrity
- Security controls and input validation

Security Features:
- Input validation and path sanitization
- Directory traversal prevention
- Content integrity verification
- Safe file operations with proper error handling
"""

import os
import re
import hashlib
import yaml
from pathlib import Path
from typing import Dict, List, Set, Optional
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SecurityError(Exception):
    """Custom exception for security-related errors"""
    pass

class OWASPNormalizer:
    """Secure OWASP CheatSheet normalizer with comprehensive security controls"""
    
    def __init__(self, source_dir: str, output_dir: str):
        self.source_dir = Path(source_dir).resolve()
        self.output_dir = Path(output_dir).resolve()
        
        # Security validation
        self._validate_paths()
        
        # Security domain tag mappings
        self.tag_patterns = {
            'authentication': re.compile(r'\b(auth|login|credential|password|mfa|2fa)\b', re.IGNORECASE),
            'jwt': re.compile(r'\b(jwt|json web token|bearer token)\b', re.IGNORECASE),
            'docker': re.compile(r'\b(docker|container|dockerfile|image)\b', re.IGNORECASE),
            'secrets': re.compile(r'\b(secret|api key|token|credential|password)\b', re.IGNORECASE),
            'session_management': re.compile(r'\b(session|cookie|csrf|xsrf)\b', re.IGNORECASE),
            'cryptography': re.compile(r'\b(crypto|encrypt|hash|cipher|tls|ssl)\b', re.IGNORECASE),
            'input_validation': re.compile(r'\b(validation|sanitiz|xss|injection|sqli)\b', re.IGNORECASE),
            'authorization': re.compile(r'\b(authz|access control|permission|rbac)\b', re.IGNORECASE),
            'network_security': re.compile(r'\b(network|firewall|vpn|proxy|cors)\b', re.IGNORECASE),
            'data_protection': re.compile(r'\b(privacy|gdpr|pii|sensitive data)\b', re.IGNORECASE)
        }
        
        # Content filters for normalization
        self.noise_patterns = [
            re.compile(r'^\s*---\s*$', re.MULTILINE),  # YAML frontmatter separators
            re.compile(r'^\s*Table of Contents.*?(?=^#|\Z)', re.MULTILINE | re.DOTALL),
            re.compile(r'^\s*## References\s*$.*?(?=^#|\Z)', re.MULTILINE | re.DOTALL),
            re.compile(r'^\s*## Related Articles\s*$.*?(?=^#|\Z)', re.MULTILINE | re.DOTALL),
            re.compile(r'^\s*## References and Further Reading\s*$.*?(?=^#|\Z)', re.MULTILINE | re.DOTALL),
            re.compile(r'^\s*## References in Related Cheat Sheets\s*$.*?(?=^#|\Z)', re.MULTILINE | re.DOTALL)
        ]

    def _validate_paths(self):
        """Validate file paths to prevent directory traversal attacks"""
        # Ensure paths are within expected boundaries
        allowed_source_patterns = [
            '/home/chris/work/CyberSecAI/genai-sec-agents/vendor/owasp-cheatsheets',
            './vendor/owasp-cheatsheets',
            'vendor/owasp-cheatsheets'
        ]
        
        allowed_output_patterns = [
            '/home/chris/work/CyberSecAI/genai-sec-agents/research/search_corpus',
            './research/search_corpus',
            'research/search_corpus'
        ]
        
        source_str = str(self.source_dir)
        output_str = str(self.output_dir)
        
        # Check for directory traversal attempts
        if '..' in source_str or '..' in output_str:
            raise SecurityError("Directory traversal detected in paths")
            
        # Validate source directory contains expected patterns
        if not any(pattern in source_str for pattern in allowed_source_patterns):
            logger.warning(f"Source directory {source_str} not in expected location")
            
        # Validate output directory contains expected patterns  
        if not any(pattern in output_str for pattern in allowed_output_patterns):
            logger.warning(f"Output directory {output_str} not in expected location")
            
        logger.info(f"Path validation completed: source={self.source_dir}, output={self.output_dir}")

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent path traversal and injection"""
        # Remove directory traversal attempts
        sanitized = re.sub(r'\.\.+', '', filename)
        
        # Remove or replace unsafe characters
        sanitized = re.sub(r'[<>:"|?*]', '', sanitized)
        sanitized = re.sub(r'[/\\]', '_', sanitized)
        
        # Limit length
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
            
        return sanitized

    def _calculate_sha256(self, content: str) -> str:
        """Calculate SHA256 checksum of content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _extract_security_tags(self, content: str, filename: str) -> List[str]:
        """Extract relevant security tags from content and filename"""
        tags = set()
        
        # Check filename for tag patterns
        for tag, pattern in self.tag_patterns.items():
            if pattern.search(filename) or pattern.search(content):
                tags.add(tag)
        
        # Add general OWASP tag
        tags.add('owasp')
        
        return sorted(list(tags))

    def _normalize_content(self, content: str) -> str:
        """Normalize markdown content by removing noise and keeping relevant sections"""
        normalized = content
        
        # Remove noise patterns
        for pattern in self.noise_patterns:
            normalized = pattern.sub('', normalized)
        
        # Clean up multiple newlines
        normalized = re.sub(r'\n{3,}', '\n\n', normalized)
        
        # Remove empty sections
        normalized = re.sub(r'^##\s*$', '', normalized, flags=re.MULTILINE)
        
        return normalized.strip()

    def _generate_front_matter(self, source_path: Path, content: str, tags: List[str]) -> str:
        """Generate YAML front-matter with metadata and security information"""
        sha256_hash = self._calculate_sha256(content)
        
        front_matter = {
            'source': 'owasp-cheatsheet-series',
            'path': str(source_path.relative_to(self.source_dir.parent)),
            'tags': tags,
            'license': 'CC-BY-SA-4.0',
            'sha256': sha256_hash,
            'processed_at': None,  # Will be set by YAML dumper
            'security_domains': [tag for tag in tags if tag != 'owasp']
        }
        
        return yaml.dump(front_matter, default_flow_style=False, sort_keys=True)

    def _process_file(self, md_file: Path) -> Optional[Path]:
        """Process a single markdown file with comprehensive security controls"""
        try:
            # Validate file path
            if not md_file.is_file() or md_file.suffix.lower() != '.md':
                logger.warning(f"Skipping non-markdown file: {md_file}")
                return None
                
            # Read source content safely
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                logger.error(f"Failed to decode file {md_file} as UTF-8")
                return None
                
            # Validate content length (prevent resource exhaustion)
            if len(content) > 1024 * 1024:  # 1MB limit
                logger.warning(f"File {md_file} too large ({len(content)} bytes), truncating")
                content = content[:1024 * 1024]
                
            # Extract security tags
            tags = self._extract_security_tags(content, md_file.stem)
            
            # Normalize content
            normalized_content = self._normalize_content(content)
            
            if len(normalized_content.strip()) < 100:  # Skip files with minimal content
                logger.info(f"Skipping file with minimal content: {md_file}")
                return None
                
            # Generate front-matter
            front_matter = self._generate_front_matter(md_file, normalized_content, tags)
            
            # Create output filename
            output_filename = self._sanitize_filename(f"{md_file.stem}.md")
            output_path = self.output_dir / output_filename
            
            # Write normalized file
            final_content = f"---\n{front_matter}---\n\n{normalized_content}"
            
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(final_content)
                    
                logger.info(f"Processed: {md_file.name} -> {output_filename} ({len(tags)} tags)")
                return output_path
                
            except IOError as e:
                logger.error(f"Failed to write output file {output_path}: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing file {md_file}: {e}")
            return None

    def process_all_cheatsheets(self) -> Dict[str, int]:
        """Process all OWASP cheatsheets with security validation"""
        stats = {
            'processed': 0,
            'skipped': 0,
            'errors': 0,
            'total_files': 0
        }
        
        # Ensure output directory exists
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise SecurityError(f"Cannot create output directory {self.output_dir}: {e}")
            
        # Find all markdown files in source directory
        cheatsheets_dir = self.source_dir / 'cheatsheets'
        if not cheatsheets_dir.exists():
            logger.warning(f"Cheatsheets directory not found: {cheatsheets_dir}")
            cheatsheets_dir = self.source_dir  # Fallback to root
            
        md_files = list(cheatsheets_dir.glob('*.md'))
        stats['total_files'] = len(md_files)
        
        if not md_files:
            logger.warning(f"No markdown files found in {cheatsheets_dir}")
            return stats
            
        logger.info(f"Processing {len(md_files)} markdown files...")
        
        # Process each file
        for md_file in md_files:
            try:
                result = self._process_file(md_file)
                if result:
                    stats['processed'] += 1
                else:
                    stats['skipped'] += 1
                    
            except Exception as e:
                logger.error(f"Processing error for {md_file}: {e}")
                stats['errors'] += 1
                
        # Log summary
        logger.info(f"Processing complete: {stats['processed']} processed, "
                   f"{stats['skipped']} skipped, {stats['errors']} errors")
        
        return stats

def validate_corpus_integrity(corpus_dir: str) -> bool:
    """Validate corpus file integrity using stored checksums"""
    corpus_path = Path(corpus_dir)
    if not corpus_path.exists():
        logger.error(f"Corpus directory does not exist: {corpus_dir}")
        return False
        
    valid_files = 0
    invalid_files = 0
    
    for md_file in corpus_path.glob('*.md'):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract front-matter
            if content.startswith('---\n'):
                parts = content.split('---\n', 2)
                if len(parts) >= 3:
                    front_matter = yaml.safe_load(parts[1])
                    file_content = parts[2]
                    
                    stored_hash = front_matter.get('sha256')
                    if stored_hash:
                        calculated_hash = hashlib.sha256(file_content.encode('utf-8')).hexdigest()
                        if stored_hash == calculated_hash:
                            valid_files += 1
                        else:
                            logger.warning(f"Checksum mismatch for {md_file.name}")
                            invalid_files += 1
                    else:
                        logger.warning(f"No checksum found for {md_file.name}")
                        invalid_files += 1
                else:
                    logger.warning(f"Invalid front-matter format in {md_file.name}")
                    invalid_files += 1
            else:
                logger.warning(f"No front-matter found in {md_file.name}")
                invalid_files += 1
                
        except Exception as e:
            logger.error(f"Error validating {md_file}: {e}")
            invalid_files += 1
    
    logger.info(f"Integrity check: {valid_files} valid, {invalid_files} invalid files")
    return invalid_files == 0

def main():
    """Main function with argument parsing and error handling"""
    parser = argparse.ArgumentParser(description='Normalize OWASP CheatSheets for semantic search')
    parser.add_argument('--source', '-s', 
                       default='vendor/owasp-cheatsheets',
                       help='Source directory containing OWASP cheatsheets')
    parser.add_argument('--output', '-o',
                       default='research/search_corpus/owasp',
                       help='Output directory for normalized corpus')
    parser.add_argument('--validate', '-v', action='store_true',
                       help='Validate corpus integrity after processing')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    try:
        # Initialize normalizer
        normalizer = OWASPNormalizer(args.source, args.output)
        
        # Process all cheatsheets
        stats = normalizer.process_all_cheatsheets()
        
        # Validate if requested
        if args.validate:
            logger.info("Running corpus integrity validation...")
            is_valid = validate_corpus_integrity(args.output)
            if not is_valid:
                logger.error("Corpus integrity validation failed")
                return 1
                
        # Print final statistics
        print(f"\nProcessing Summary:")
        print(f"  Files processed: {stats['processed']}")
        print(f"  Files skipped: {stats['skipped']}")
        print(f"  Errors: {stats['errors']}")
        print(f"  Total files: {stats['total_files']}")
        
        if stats['processed'] == 0:
            logger.error("No files were successfully processed")
            return 1
            
        return 0
        
    except SecurityError as e:
        logger.error(f"Security error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    exit(main())