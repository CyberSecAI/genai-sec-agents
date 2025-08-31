"""
Tests for OWASP Content Parser

Tests HTML parsing, section extraction, and requirement identification.
"""

import pytest
from app.ingestion.content_parser import SecureCodingParser, ContentSection, SectionType, SecurityRequirement, CodeExample


class TestSecureCodingParser:
    """Test OWASP content parser functionality"""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance"""
        return SecureCodingParser()
    
    def test_parser_initialization(self, parser):
        """Test parser initializes correctly"""
        assert parser is not None
        assert parser.requirement_regex is not None
        assert len(parser.CODE_LANGUAGES) > 0
        assert 'python' in parser.CODE_LANGUAGES
        assert 'java' in parser.CODE_LANGUAGES
    
    def test_requirement_pattern_matching(self, parser):
        """Test requirement pattern recognition"""
        test_cases = [
            ("Applications must validate all input", True),
            ("You should always use HTTPS", True),
            ("Never store passwords in plain text", True),
            ("Ensure that user input is sanitized", True),
            ("Do not trust user input", True),
            ("It is recommended to use prepared statements", True),
            ("This is just a regular sentence", False),
            ("The following example shows code", False)
        ]
        
        for text, should_match in test_cases:
            match = parser.requirement_regex.search(text)
            if should_match:
                assert match is not None, f"Should match requirement: '{text}'"
            else:
                assert match is None, f"Should not match requirement: '{text}'"
    
    def test_severity_determination(self, parser):
        """Test severity level determination"""
        test_cases = [
            ("Applications must never store passwords in plain text", "critical"),
            ("You should always validate user input", "high"), 
            ("It is recommended to use HTTPS", "high"),
            ("Consider using a web application firewall", "medium"),
            ("You may want to implement rate limiting", "medium"),
            ("This is a helpful tip for developers", "low")
        ]
        
        for text, expected_severity in test_cases:
            severity = parser._determine_severity(text)
            assert severity == expected_severity, f"Text: '{text}' expected {expected_severity}, got {severity}"
    
    def test_code_language_detection(self, parser):
        """Test programming language detection"""
        # Test with class attributes
        from bs4 import BeautifulSoup
        
        html_java = '<pre><code class="language-java">public class Test {}</code></pre>'
        soup = BeautifulSoup(html_java, 'html.parser')
        code_block = soup.find('code')
        
        language = parser._detect_code_language(code_block, "public class Test {}")
        assert language == "java"
        
        # Test with content analysis
        test_cases = [
            ("public class Test { import java.util.*; }", "java"),
            ("def main(): import sys", "python"),
            ("function test() { var x = 5; }", "javascript"),
            ("using System; namespace Test {}", "csharp"),
            ("<?php echo 'test'; ?>", "php"),
            ("SELECT * FROM users WHERE id = ?", "sql"),
            ("<html><head></head></html>", "html")
        ]
        
        for code, expected_lang in test_cases:
            empty_block = BeautifulSoup('<code></code>', 'html.parser').find('code')
            detected = parser._detect_code_language(empty_block, code)
            assert detected == expected_lang, f"Code: '{code}' expected {expected_lang}, got {detected}"
    
    def test_section_type_classification(self, parser):
        """Test section type classification"""
        test_sections = [
            ContentSection("Introduction", "This section provides an overview", SectionType.INTRODUCTION, [], [], [], 1),
            ContentSection("Implementation Steps", "How to implement validation", SectionType.IMPLEMENTATION, [], [], [], 1),
            ContentSection("Code Examples", "Here are some examples", SectionType.CODE_EXAMPLE, [], [], [], 1),
            ContentSection("Validation Testing", "Test your implementation", SectionType.VALIDATION, [], [], [], 1),
            ContentSection("References", "Links and resources", SectionType.REFERENCE, [], [], [], 1),
            ContentSection("Vulnerability Details", "This attack works by", SectionType.VULNERABILITY, [], [], [], 1),
            ContentSection("Mitigation Strategies", "Prevent attacks with", SectionType.MITIGATION, [], [], [], 1)
        ]
        
        for section in test_sections:
            classified_type = parser._classify_section_type(section)
            assert classified_type == section.section_type, f"Section '{section.title}' misclassified"
    
    def test_security_requirements_extraction(self, parser):
        """Test extraction of security requirements from content"""
        test_content = """
        Applications must validate all user input to prevent injection attacks.
        Never trust data from external sources.
        You should always use HTTPS for sensitive data transmission.
        Consider implementing rate limiting to prevent abuse.
        Do not store passwords in plain text format.
        """
        
        section = ContentSection(
            title="Security Requirements",
            content=test_content,
            section_type=SectionType.REQUIREMENT,
            subsections=[],
            code_examples=[],
            requirements=[],
            level=1
        )
        
        requirements = parser._extract_security_requirements(section)
        
        assert len(requirements) > 0, "Should extract at least one requirement"
        
        # Check that requirements have proper structure
        for req in requirements:
            assert isinstance(req, SecurityRequirement)
            assert req.title
            assert req.severity in ['critical', 'high', 'medium', 'low']
            assert isinstance(req.do_guidance, list)
            assert isinstance(req.dont_guidance, list)
    
    def test_actionable_requirements_identification(self, parser):
        """Test identification of actionable requirements from text"""
        test_content = """
        Input validation is crucial for application security.
        All user input must be validated against a whitelist of acceptable values.
        Applications should never trust user-supplied data without validation.
        Consider using a validation library to standardize the process.
        You may want to log validation failures for monitoring.
        """
        
        requirements = parser.identify_actionable_requirements(test_content)
        
        assert len(requirements) > 0, "Should identify actionable requirements"
        
        # Check for critical requirements
        critical_reqs = [req for req in requirements if req.severity == 'critical']
        high_reqs = [req for req in requirements if req.severity == 'high'] 
        
        assert len(critical_reqs) + len(high_reqs) > 0, "Should identify high/critical requirements"
    
    def test_html_content_parsing(self, parser):
        """Test parsing of complete HTML content"""
        sample_html = """
        <!DOCTYPE html>
        <html>
        <head><title>OWASP Cheat Sheet</title></head>
        <body>
            <main>
                <h1>Input Validation Cheat Sheet</h1>
                <p>This cheat sheet provides guidance on input validation.</p>
                
                <h2>Requirements</h2>
                <p>Applications must validate all user input. Never trust external data sources.</p>
                
                <h2>Implementation</h2>
                <p>Use whitelist validation whenever possible.</p>
                
                <h3>Code Example</h3>
                <pre><code class="language-python">
def validate_input(data):
    if data in allowed_values:
        return data
    else:
        raise ValueError("Invalid input")
                </code></pre>
                
                <h2>References</h2>
                <p>See OWASP Top 10 for more information.</p>
            </main>
        </body>
        </html>
        """
        
        sections = parser.parse_cheatsheet_sections(sample_html)
        
        assert len(sections) > 0, "Should parse sections from HTML"
        
        # Should have main sections
        section_titles = [section.title for section in sections]
        assert "Input Validation Cheat Sheet" in section_titles
        
        # Check section hierarchy
        main_section = next(s for s in sections if s.title == "Input Validation Cheat Sheet")
        assert len(main_section.subsections) > 0, "Should have subsections"
        
        # Check that requirements are extracted
        req_sections = [s for s in main_section.subsections if s.section_type == SectionType.REQUIREMENT]
        if req_sections:
            assert len(req_sections[0].requirements) > 0, "Should extract requirements"
    
    def test_secure_vs_vulnerable_code_detection(self, parser):
        """Test detection of secure vs vulnerable code examples"""
        from bs4 import BeautifulSoup
        
        # Test secure code context
        secure_html = '<p>This is the recommended secure approach:</p><pre><code>validate_input(data)</code></pre>'
        soup = BeautifulSoup(secure_html, 'html.parser')
        code_block = soup.find('pre')
        description = parser._get_code_description(code_block)
        
        is_secure = parser._is_secure_code_example(code_block, description)
        assert is_secure, "Should detect secure code example"
        
        # Test vulnerable code context
        vulnerable_html = '<p>This is a vulnerable approach to avoid:</p><pre><code>execute_raw_sql(user_input)</code></pre>'
        soup = BeautifulSoup(vulnerable_html, 'html.parser') 
        code_block = soup.find('pre')
        description = parser._get_code_description(code_block)
        
        is_secure = parser._is_secure_code_example(code_block, description)
        assert not is_secure, "Should detect vulnerable code example"
    
    def test_code_example_extraction(self, parser):
        """Test extraction of code examples from HTML"""
        html_with_code = """
        <html><body>
            <h2>Secure Implementation</h2>
            <p>Use prepared statements to prevent SQL injection:</p>
            <pre><code class="language-python">
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            </code></pre>
            
            <h2>Vulnerable Code</h2>  
            <p>Never use string concatenation for SQL queries:</p>
            <pre><code class="language-python">
cursor.execute("SELECT * FROM users WHERE id = " + user_id)
            </code></pre>
        </body></html>
        """
        
        code_examples = parser.extract_code_examples(html_with_code)
        
        assert len(code_examples) == 2, "Should extract both code examples"
        
        # Check that one is marked secure and one vulnerable
        secure_examples = [ex for ex in code_examples if ex.is_secure]
        vulnerable_examples = [ex for ex in code_examples if not ex.is_secure]
        
        assert len(secure_examples) >= 1, "Should identify at least one secure example"
        assert len(vulnerable_examples) >= 1, "Should identify at least one vulnerable example"
        
        # Check language detection
        for example in code_examples:
            assert example.language == 'python', "Should detect Python language"