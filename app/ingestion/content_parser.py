"""
OWASP Cheat Sheet Content Parser

Parses Markdown content from OWASP cheat sheets and extracts structured information
for Rule Card generation. Handles various cheat sheet formats consistently.
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum


class SectionType(Enum):
    """Types of sections found in OWASP cheat sheets"""
    INTRODUCTION = "introduction"
    REQUIREMENT = "requirement" 
    IMPLEMENTATION = "implementation"
    VALIDATION = "validation"
    CODE_EXAMPLE = "code_example"
    REFERENCE = "reference"
    VULNERABILITY = "vulnerability"
    MITIGATION = "mitigation"


@dataclass
class CodeExample:
    """Represents a code example from OWASP content"""
    language: str
    code: str
    description: str
    is_secure: bool  # True for secure examples, False for vulnerable


@dataclass
class SecurityRequirement:
    """Represents an actionable security requirement"""
    title: str
    description: str
    severity: str  # critical, high, medium, low
    do_guidance: List[str]
    dont_guidance: List[str]
    code_examples: List[CodeExample]
    references: List[str]


@dataclass
class ContentSection:
    """Represents a parsed section of OWASP content"""
    title: str
    content: str
    section_type: SectionType
    subsections: List['ContentSection']
    code_examples: List[CodeExample]
    requirements: List[SecurityRequirement]
    level: int  # Heading level (1-6)


class SecureCodingParser:
    """Parser for OWASP cheat sheet HTML content"""
    
    # Patterns to identify different types of content
    REQUIREMENT_PATTERNS = [
        r'must\s+(?:be|have|include|ensure|implement|use|avoid|validate)',
        r'should\s+(?:be|have|include|ensure|implement|use|avoid|validate)',
        r'(?:always|never)\s+(?:use|implement|include|allow|validate)',
        r'(?:ensure|verify|validate|check)\s+',
        r'(?:do\s+not|don\'t|avoid|never)\s+',
        r'it\s+is\s+(?:recommended|required|essential|important)',
        r'applications\s+must',
        r'never\s+(?:use|store|trust)',
        r'always\s+(?:use|validate|check)'
    ]
    
    SEVERITY_INDICATORS = {
        'critical': ['critical', 'must', 'required', 'essential', 'never'],
        'high': ['important', 'strongly', 'should', 'recommended', 'avoid'],
        'medium': ['consider', 'may', 'can', 'optional', 'prefer'],
        'low': ['note', 'tip', 'suggestion', 'enhancement']
    }
    
    CODE_LANGUAGES = {
        'java', 'python', 'javascript', 'csharp', 'c#', 'php', 'ruby', 
        'go', 'typescript', 'sql', 'html', 'css', 'xml', 'json', 'yaml',
        'bash', 'shell', 'powershell', 'kotlin', 'swift', 'rust'
    }
    
    def __init__(self):
        """Initialize parser"""
        self.requirement_regex = re.compile(
            '|'.join(self.REQUIREMENT_PATTERNS), 
            re.IGNORECASE | re.MULTILINE
        )
    
    def parse_cheatsheet_sections(self, markdown_content: str) -> List[ContentSection]:
        """
        Parse OWASP cheat sheet Markdown into structured sections
        
        Args:
            markdown_content: Raw Markdown content from OWASP cheat sheet
            
        Returns:
            List of parsed content sections
        """
        try:
            # Parse sections based on heading structure
            sections = self._parse_markdown_sections(markdown_content)
            
            # Process each section to extract requirements and code examples
            for section in sections:
                section.requirements = self._extract_security_requirements(section)
                section.code_examples = self._extract_markdown_code_examples(section.content)
                section.section_type = self._classify_section_type(section)
            
            return sections
            
        except Exception as e:
            raise RuntimeError(f"Failed to parse Markdown content: {e}")
    
    def _parse_markdown_sections(self, markdown_content: str) -> List[ContentSection]:
        """Parse markdown content into sections based on heading hierarchy"""
        sections = []
        current_section = None
        
        lines = markdown_content.split('\n')
        in_code_block = False
        
        for line in lines:
            original_line = line
            line = line.strip()
            
            # Track code block boundaries
            if line.startswith('```'):
                in_code_block = not in_code_block
                if current_section:
                    current_section.content += original_line + "\n"
                continue
            
            # Check if line is a heading (only if not in code block)
            if line.startswith('#') and not in_code_block:
                # Save previous section
                if current_section:
                    sections.append(current_section)
                
                # Extract heading level and title
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('#').strip()
                
                if title:  # Skip empty headings
                    current_section = ContentSection(
                        title=title,
                        content="",
                        section_type=SectionType.INTRODUCTION,
                        subsections=[],
                        code_examples=[],
                        requirements=[],
                        level=level
                    )
            elif current_section:
                # Add content to current section (preserve original line for proper formatting)
                if line or in_code_block:  # Include empty lines in code blocks
                    current_section.content += original_line + "\n"
        
        # Add final section
        if current_section:
            sections.append(current_section)
        
        # Build section hierarchy
        sections = self._build_section_hierarchy(sections)
        
        return sections
    
    def _build_section_hierarchy(self, flat_sections: List[ContentSection]) -> List[ContentSection]:
        """Build hierarchical section structure based on heading levels"""
        if not flat_sections:
            return []
        
        root_sections = []
        section_stack = []
        
        for section in flat_sections:
            # Pop sections from stack that are at same or higher level
            while section_stack and section_stack[-1].level >= section.level:
                section_stack.pop()
            
            if section_stack:
                # Add as subsection to parent
                section_stack[-1].subsections.append(section)
            else:
                # Add as root section
                root_sections.append(section)
            
            section_stack.append(section)
        
        return root_sections
    
    def _classify_section_type(self, section: ContentSection) -> SectionType:
        """Classify section type based on title and content"""
        title_lower = section.title.lower()
        content_lower = section.content.lower()
        
        # Classification based on common OWASP patterns
        if any(word in title_lower for word in ['introduction', 'overview', 'about']):
            return SectionType.INTRODUCTION
        elif any(word in title_lower for word in ['implementation', 'how to', 'steps']):
            return SectionType.IMPLEMENTATION
        elif any(word in title_lower for word in ['validation', 'testing', 'verification']):
            return SectionType.VALIDATION
        elif any(word in title_lower for word in ['example', 'sample', 'code']):
            return SectionType.CODE_EXAMPLE
        elif any(word in title_lower for word in ['reference', 'link', 'resource']):
            return SectionType.REFERENCE
        elif any(word in title_lower for word in ['vulnerability', 'attack', 'threat']):
            return SectionType.VULNERABILITY
        elif any(word in title_lower for word in ['mitigation', 'prevention', 'defense']):
            return SectionType.MITIGATION
        elif self.requirement_regex.search(content_lower):
            return SectionType.REQUIREMENT
        else:
            return SectionType.INTRODUCTION
    
    def _extract_security_requirements(self, section: ContentSection) -> List[SecurityRequirement]:
        """Extract actionable security requirements from section content"""
        requirements = []
        
        # Split content into sentences for analysis
        sentences = re.split(r'[.!?]+', section.content)
        
        current_requirement = None
        do_items = []
        dont_items = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check if this sentence contains a requirement
            if self.requirement_regex.search(sentence):
                # Save previous requirement if exists
                if current_requirement:
                    requirements.append(SecurityRequirement(
                        title=current_requirement,
                        description=current_requirement,
                        severity=self._determine_severity(current_requirement),
                        do_guidance=do_items.copy(),
                        dont_guidance=dont_items.copy(),
                        code_examples=[],
                        references=[]
                    ))
                
                # Start new requirement
                current_requirement = sentence
                do_items = []
                dont_items = []
                
                # Classify as do or don't
                if any(neg in sentence.lower() for neg in ['do not', "don't", 'avoid', 'never']):
                    dont_items.append(sentence)
                else:
                    do_items.append(sentence)
            elif current_requirement:
                # Continue building current requirement
                if any(neg in sentence.lower() for neg in ['do not', "don't", 'avoid', 'never']):
                    dont_items.append(sentence)
                else:
                    do_items.append(sentence)
        
        # Add final requirement
        if current_requirement:
            requirements.append(SecurityRequirement(
                title=current_requirement,
                description=current_requirement, 
                severity=self._determine_severity(current_requirement),
                do_guidance=do_items,
                dont_guidance=dont_items,
                code_examples=[],
                references=[]
            ))
        
        return requirements
    
    def _determine_severity(self, text: str) -> str:
        """Determine severity level based on text content"""
        text_lower = text.lower()
        
        for severity, indicators in self.SEVERITY_INDICATORS.items():
            if any(indicator in text_lower for indicator in indicators):
                return severity
        
        return 'medium'  # Default severity
    
    def _extract_markdown_code_examples(self, content: str) -> List[CodeExample]:
        """Extract code examples from markdown content"""
        examples = []
        
        # Pattern to match markdown code blocks
        code_block_pattern = re.compile(r'```(\w*)\n(.*?)\n```', re.DOTALL)
        
        matches = code_block_pattern.findall(content)
        
        for language, code in matches:
            if len(code.strip()) < 10:  # Skip very short snippets
                continue
            
            # Get description from context around the code block
            code_index = content.find(f'```{language}\n{code}\n```')
            description = self._get_code_context_description(content, code_index)
            
            # Determine if secure or vulnerable
            is_secure = self._is_secure_markdown_code(content, code_index, description)
            
            examples.append(CodeExample(
                language=language if language else self._detect_code_language_from_content(code),
                code=code.strip(),
                description=description,
                is_secure=is_secure
            ))
        
        return examples
    
    def identify_actionable_requirements(self, content: str) -> List[SecurityRequirement]:
        """
        Parse content text to identify actionable security requirements
        
        Args:
            content: Text content to analyze
            
        Returns:
            List of identified security requirements
        """
        sections = [ContentSection(
            title="Content",
            content=content,
            section_type=SectionType.REQUIREMENT,
            subsections=[],
            code_examples=[],
            requirements=[],
            level=1
        )]
        
        section = sections[0]
        section.requirements = self._extract_security_requirements(section)
        
        return section.requirements
    
    def extract_code_examples(self, markdown_content: str) -> List[CodeExample]:
        """
        Extract code examples from Markdown content
        
        Args:
            markdown_content: Markdown content containing code examples
            
        Returns:
            List of extracted code examples
        """
        return self._extract_markdown_code_examples(markdown_content)
    
    def _get_code_context_description(self, content: str, code_index: int) -> str:
        """Get description for code block from surrounding markdown context"""
        # Look for text in the 200 characters before the code block
        start_index = max(0, code_index - 200)
        context = content[start_index:code_index].strip()
        
        # Find the last sentence or paragraph
        lines = context.split('\n')
        for line in reversed(lines):
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('```'):
                return line[:200] + ('...' if len(line) > 200 else '')
        
        return "Code example"
    
    def _is_secure_markdown_code(self, content: str, code_index: int, description: str) -> bool:
        """Determine if markdown code example represents secure or vulnerable code"""
        # Look at surrounding context
        start_index = max(0, code_index - 300)
        end_index = min(len(content), code_index + 300)
        context = content[start_index:end_index].lower()
        
        # Check for negative indicators
        negative_words = ['vulnerable', 'insecure', 'bad', 'wrong', 'incorrect', 'avoid', "don't", 'never', 'attack', 'exploit']
        if any(word in context for word in negative_words):
            return False
        
        # Check for positive indicators
        positive_words = ['secure', 'safe', 'correct', 'recommended', 'good', 'proper', 'fix', 'solution']
        if any(word in context for word in positive_words):
            return True
        
        # Default to secure if unclear
        return True
    
    def _detect_code_language_from_content(self, code: str) -> str:
        """Detect programming language from code content"""
        code_lower = code.lower()
        
        # Language-specific patterns
        if 'public class' in code_lower or 'import java.' in code_lower:
            return 'java'
        elif 'def ' in code_lower or ('import ' in code_lower and 'from ' in code_lower):
            return 'python'
        elif 'function' in code_lower or 'var ' in code_lower or 'let ' in code_lower:
            return 'javascript'
        elif 'using ' in code_lower and 'namespace' in code_lower:
            return 'csharp'
        elif '<?php' in code_lower or '$_' in code_lower:
            return 'php'
        elif 'SELECT' in code.upper() or 'INSERT' in code.upper():
            return 'sql'
        elif '<html' in code_lower or '<!doctype' in code_lower:
            return 'html'
        
        return 'text'  # Default
    
