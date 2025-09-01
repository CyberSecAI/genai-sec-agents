#!/usr/bin/env python3
"""
OWASP ASVS Content Fetcher

Fetches OWASP Application Security Verification Standard (ASVS) content
from GitHub repository and prepares it for Rule Card generation.

Extension of Story 2.5 for ASVS integration
"""

import os
import re
import json
import logging
import requests
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ASVSVerificationRequirement:
    """Represents a single ASVS verification requirement."""
    id: str
    level: int
    description: str
    category: str
    section: str
    raw_text: str


@dataclass
class ASVSSection:
    """Represents an ASVS verification section."""
    id: str
    title: str
    description: str
    url: str
    requirements: List[ASVSVerificationRequirement]


class ASVSFetcher:
    """Fetches and processes OWASP ASVS content from GitHub."""
    
    def __init__(self):
        """Initialize ASVS fetcher with GitHub URLs."""
        self.base_url = "https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/"
        self.github_base = "https://github.com/OWASP/ASVS/blob/master/5.0/en/"
        
        # Semantic search preservation paths
        self.semantic_sources_path = Path("app/semantic/sources/asvs/v5.0")
        self.cached_sources_path = Path("app/data/asvs_sources")
        
        # Ensure directories exist
        self.semantic_sources_path.mkdir(parents=True, exist_ok=True)
        self.cached_sources_path.mkdir(parents=True, exist_ok=True)
        
        # ASVS 5.0 verification sections mapping
        self.asvs_sections = {
            'V1-Encoding-Sanitization': {
                'title': 'Encoding and Sanitization',
                'file': '0x10-V1-Encoding-Sanitization.md',
                'priority': 1,
                'description': 'Input validation, output encoding, and data sanitization'
            },
            'V2-Validation-Business-Logic': {
                'title': 'Validation and Business Logic',
                'file': '0x11-V2-Validation-Business-Logic.md',
                'priority': 1,
                'description': 'Input validation and business logic security'
            },
            'V3-Web-Frontend-Security': {
                'title': 'Web Frontend Security',
                'file': '0x12-V3-Web-Frontend-Security.md',
                'priority': 2,
                'description': 'Client-side security and frontend protection'
            },
            'V4-API-Web-Service': {
                'title': 'API and Web Service Security',
                'file': '0x13-V4-API-Web-Service.md',
                'priority': 1,
                'description': 'API security and web service protection'
            },
            'V5-File-Handling': {
                'title': 'File Handling',
                'file': '0x14-V5-File-Handling.md',
                'priority': 2,
                'description': 'File upload and handling security'
            },
            'V6-Authentication': {
                'title': 'Authentication',
                'file': '0x15-V6-Authentication.md',
                'priority': 1,
                'description': 'Authentication mechanisms and security'
            },
            'V7-Session-Management': {
                'title': 'Session Management',
                'file': '0x16-V7-Session-Management.md',
                'priority': 1,
                'description': 'Session handling and lifecycle security'
            },
            'V8-Authorization': {
                'title': 'Authorization',
                'file': '0x17-V8-Authorization.md',
                'priority': 1,
                'description': 'Access control and authorization'
            },
            'V9-Self-contained-Tokens': {
                'title': 'Self-contained Tokens',
                'file': '0x18-V9-Self-contained-Tokens.md',
                'priority': 2,
                'description': 'JWT and token-based authentication'
            },
            'V10-OAuth-OIDC': {
                'title': 'OAuth and OIDC',
                'file': '0x19-V10-OAuth-OIDC.md',
                'priority': 3,
                'description': 'OAuth 2.0 and OpenID Connect security'
            },
            'V11-Cryptography': {
                'title': 'Cryptography',
                'file': '0x20-V11-Cryptography.md',
                'priority': 1,
                'description': 'Cryptographic implementation and key management'
            },
            'V12-Secure-Communication': {
                'title': 'Secure Communication',
                'file': '0x21-V12-Secure-Communication.md',
                'priority': 1,
                'description': 'TLS and network communication security'
            },
            'V13-Configuration': {
                'title': 'Configuration',
                'file': '0x22-V13-Configuration.md',
                'priority': 2,
                'description': 'Security configuration and hardening'
            },
            'V14-Data-Protection': {
                'title': 'Data Protection',
                'file': '0x23-V14-Data-Protection.md',
                'priority': 1,
                'description': 'Data privacy and protection mechanisms'
            },
            'V15-Secure-Coding-Architecture': {
                'title': 'Secure Coding and Architecture',
                'file': '0x24-V15-Secure-Coding-Architecture.md',
                'priority': 2,
                'description': 'Secure development and architectural patterns'
            },
            'V16-Logging-Error-Handling': {
                'title': 'Security Logging and Error Handling',
                'file': '0x25-V16-Logging-Error-Handling.md',
                'priority': 2,
                'description': 'Security logging and error management'
            },
            'V17-WebRTC': {
                'title': 'WebRTC',
                'file': '0x26-V17-WebRTC.md',
                'priority': 3,
                'description': 'WebRTC security considerations'
            }
        }
    
    def get_prioritized_asvs_sections(self, priority_levels: List[int] = [1, 2]) -> List[Dict[str, Any]]:
        """Get ASVS sections ordered by priority."""
        prioritized_sections = []
        
        for section_id, section_info in self.asvs_sections.items():
            if section_info['priority'] in priority_levels:
                section_data = {
                    'id': section_id,
                    'title': section_info['title'],
                    'file': section_info['file'],
                    'url': self.base_url + section_info['file'],
                    'github_url': self.github_base + section_info['file'],
                    'description': section_info['description'],
                    'priority': section_info['priority']
                }
                prioritized_sections.append(section_data)
        
        # Sort by priority (1 = highest priority)
        prioritized_sections.sort(key=lambda x: (x['priority'], x['title']))
        
        logger.info(f"Selected {len(prioritized_sections)} ASVS sections for processing")
        return prioritized_sections
    
    def fetch_asvs_content(self, url: str) -> Optional[str]:
        """Fetch ASVS content from GitHub raw URL."""
        try:
            logger.info(f"Fetching ASVS content from: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            content = response.text
            logger.info(f"Successfully fetched {len(content)} characters")
            return content
            
        except Exception as e:
            logger.error(f"Failed to fetch ASVS content from {url}: {e}")
            return None
    
    def preserve_markdown_for_semantic_search(self, section_info: Dict[str, Any], content: str) -> bool:
        """Preserve original ASVS markdown files for semantic search corpus."""
        try:
            # Save to semantic search corpus
            semantic_file_path = self.semantic_sources_path / section_info['file']
            with open(semantic_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Save to cached sources with metadata
            cached_file_path = self.cached_sources_path / section_info['file']
            with open(cached_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Create/update metadata file
            metadata_path = self.semantic_sources_path / "metadata.json"
            metadata = self._load_or_create_metadata(metadata_path)
            
            # Update metadata for this section
            metadata['sections'][section_info['id']] = {
                'title': section_info['title'],
                'file': section_info['file'],
                'github_url': section_info['github_url'],
                'description': section_info['description'],
                'last_updated': datetime.now().isoformat(),
                'content_length': len(content),
                'version': '5.0'
            }
            
            # Save updated metadata
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Preserved markdown for semantic search: {section_info['file']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to preserve markdown for {section_info['file']}: {e}")
            return False
    
    def _load_or_create_metadata(self, metadata_path: Path) -> Dict[str, Any]:
        """Load existing metadata or create new structure."""
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load existing metadata: {e}, creating new")
        
        # Create new metadata structure
        return {
            'asvs_version': '5.0',
            'corpus_created': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'source_repository': 'https://github.com/OWASP/ASVS',
            'sections': {}
        }
    
    def parse_verification_requirements(self, content: str, section_id: str, section_title: str) -> List[ASVSVerificationRequirement]:
        """Parse ASVS verification requirements from markdown content."""
        requirements = []
        
        # Updated pattern for ASVS 5.0 format
        # Format: | **11.1.1** | Verify that... | 1 |
        requirement_pattern = r'\|\s*\*\*(\d+\.\d+\.\d+)\*\*\s*\|\s*(.*?)\s*\|\s*(\d+)\s*\|'
        
        lines = content.split('\n')
        current_subsection = "General"
        
        for i, line in enumerate(lines):
            # Track subsection headers (## V11.1 becomes subsection)
            if line.startswith('## V') and '.' in line:
                # Extract subsection like "V11.1 Cryptographic Storage Architecture" 
                current_subsection = line.replace('## ', '').strip()
                continue
            elif line.startswith('## ') and not line.startswith('## V'):
                current_subsection = line.replace('## ', '').strip()
                continue
            
            # Try table format
            table_match = re.search(requirement_pattern, line.strip())
            if table_match:
                req_id = table_match.group(1)
                description = table_match.group(2).strip()
                level = int(table_match.group(3))
                
                # Clean up description
                description = self._clean_description(description)
                
                if description:  # Only add non-empty descriptions
                    req = ASVSVerificationRequirement(
                        id=req_id,
                        level=level,
                        description=description,
                        category=current_subsection,
                        section=section_title,
                        raw_text=line.strip()
                    )
                    requirements.append(req)
        
        logger.info(f"Parsed {len(requirements)} verification requirements from {section_title}")
        return requirements
    
    def _clean_description(self, description: str) -> str:
        """Clean and normalize ASVS requirement descriptions."""
        if not description:
            return ""
            
        # Remove markdown formatting
        description = re.sub(r'\*\*(.*?)\*\*', r'\1', description)  # Bold
        description = re.sub(r'\*(.*?)\*', r'\1', description)      # Italic
        description = re.sub(r'`(.*?)`', r'\1', description)        # Code
        
        # Remove HTML tags
        description = re.sub(r'<[^>]+>', '', description)
        
        # Clean up whitespace
        description = ' '.join(description.split())
        
        # Remove common prefixes that don't add value
        prefixes_to_remove = [
            "Verify that the application ",
            "Verify that ",
            "Ensure that ",
            "Confirm that "
        ]
        
        for prefix in prefixes_to_remove:
            if description.startswith(prefix):
                description = description[len(prefix):]
                break
                
        # Capitalize first letter
        if description:
            description = description[0].upper() + description[1:]
            
        return description.strip()
    
    def fetch_asvs_section(self, section_info: Dict[str, Any]) -> Optional[ASVSSection]:
        """Fetch and parse a complete ASVS section."""
        try:
            # Fetch the content
            content = self.fetch_asvs_content(section_info['url'])
            if not content:
                return None
            
            # Preserve markdown for semantic search
            self.preserve_markdown_for_semantic_search(section_info, content)
            
            # Parse verification requirements
            requirements = self.parse_verification_requirements(
                content, section_info['id'], section_info['title']
            )
            
            if not requirements:
                logger.warning(f"No requirements found in section {section_info['title']}")
                return None
            
            # Create section object
            section = ASVSSection(
                id=section_info['id'],
                title=section_info['title'],
                description=section_info['description'],
                url=section_info['github_url'],
                requirements=requirements
            )
            
            logger.info(f"Successfully processed ASVS section: {section.title} ({len(requirements)} requirements)")
            return section
            
        except Exception as e:
            logger.error(f"Failed to fetch ASVS section {section_info['title']}: {e}")
            return None
    
    def fetch_all_priority_sections(self, priority_levels: List[int] = [1, 2]) -> List[ASVSSection]:
        """Fetch all ASVS sections based on priority."""
        sections = []
        prioritized_section_info = self.get_prioritized_asvs_sections(priority_levels)
        
        logger.info(f"Starting fetch of {len(prioritized_section_info)} ASVS sections")
        
        for section_info in prioritized_section_info:
            section = self.fetch_asvs_section(section_info)
            if section:
                sections.append(section)
            
            # Rate limiting - be respectful to GitHub
            import time
            time.sleep(1)
        
        logger.info(f"Successfully fetched {len(sections)} ASVS sections")
        return sections
    
    def get_requirements_by_level(self, sections: List[ASVSSection], min_level: int = 1) -> List[ASVSVerificationRequirement]:
        """Get all requirements that meet or exceed a minimum ASVS level."""
        filtered_requirements = []
        
        for section in sections:
            for req in section.requirements:
                if req.level >= min_level:
                    filtered_requirements.append(req)
        
        logger.info(f"Found {len(filtered_requirements)} requirements at level {min_level}+")
        return filtered_requirements
    
    def export_requirements_summary(self, sections: List[ASVSSection]) -> Dict[str, Any]:
        """Export a summary of fetched ASVS requirements."""
        summary = {
            'total_sections': len(sections),
            'total_requirements': sum(len(s.requirements) for s in sections),
            'sections': []
        }
        
        for section in sections:
            section_summary = {
                'id': section.id,
                'title': section.title,
                'description': section.description,
                'requirement_count': len(section.requirements),
                'level_breakdown': {
                    'level_1': len([r for r in section.requirements if r.level == 1]),
                    'level_2': len([r for r in section.requirements if r.level == 2]),
                    'level_3': len([r for r in section.requirements if r.level == 3])
                },
                'categories': list(set(r.category for r in section.requirements))
            }
            summary['sections'].append(section_summary)
        
        return summary


def main():
    """Test the ASVS fetcher functionality."""
    logging.basicConfig(level=logging.INFO)
    
    fetcher = ASVSFetcher()
    
    # Test with a single high-priority section
    test_section = {
        'id': 'V11-Cryptography',
        'title': 'Cryptography',
        'file': '0x20-V11-Cryptography.md',
        'url': fetcher.base_url + '0x20-V11-Cryptography.md',
        'github_url': fetcher.github_base + '0x20-V11-Cryptography.md',
        'description': 'Cryptographic implementation and key management',
        'priority': 1
    }
    
    print("Testing ASVS Fetcher with Cryptography section...")
    section = fetcher.fetch_asvs_section(test_section)
    
    if section:
        print(f"✅ Successfully fetched: {section.title}")
        print(f"   Requirements: {len(section.requirements)}")
        print(f"   Categories: {set(r.category for r in section.requirements)}")
        
        # Show first few requirements
        print("\nSample requirements:")
        for i, req in enumerate(section.requirements[:3]):
            print(f"   {req.id}: {req.description[:80]}...")
            
    else:
        print("❌ Failed to fetch ASVS section")


if __name__ == "__main__":
    main()