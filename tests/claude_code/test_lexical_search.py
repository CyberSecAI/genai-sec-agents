"""
Test suite for LexicalSearchTool - Claude Code integration for lexical/grep search.

Following TDD approach - these tests define the expected behavior before implementation.
"""

import pytest
import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Union


@dataclass
class LexicalResult:
    """Expected result structure from lexical search."""
    content: str
    file_path: str
    line_number: int
    source: str  # 'asvs' or 'owasp' 
    context_lines: List[str]
    match_type: str  # 'literal' or 'regex'


def test_can_import_lexical_search_tool():
    """Test that we can import the LexicalSearchTool class."""
    # This test MUST fail first because LexicalSearchTool doesn't exist yet
    from tools.claude_code.lexical_search import LexicalSearchTool
    
    assert LexicalSearchTool is not None


def test_can_create_lexical_search_tool():
    """Test creating a basic LexicalSearchTool instance."""
    from tools.claude_code.lexical_search import LexicalSearchTool
    
    # Test basic instantiation
    tool = LexicalSearchTool()
    assert tool is not None


def test_search_security_standards_lexical_basic():
    """Test basic lexical search functionality with literal pattern."""
    from tools.claude_code.lexical_search import LexicalSearchTool
    
    tool = LexicalSearchTool()
    
    # Test basic literal search
    results = tool.search_security_standards_lexical("authentication")
    
    assert isinstance(results, list)
    assert len(results) <= 10  # Default max_results
    
    # If results found, validate structure
    if results:
        result = results[0]
        assert isinstance(result, LexicalResult)
        assert hasattr(result, 'content')
        assert hasattr(result, 'file_path')
        assert hasattr(result, 'line_number')
        assert hasattr(result, 'source')
        assert hasattr(result, 'context_lines')
        assert hasattr(result, 'match_type')
        assert result.match_type == 'literal'


def test_search_security_standards_lexical_regex():
    """Test regex pattern search functionality."""
    from tools.claude_code.lexical_search import LexicalSearchTool
    
    tool = LexicalSearchTool()
    
    # Test regex search
    results = tool.search_security_standards_lexical(r"JWT.*token", regex=True)
    
    assert isinstance(results, list)
    
    # If results found, validate regex match type
    if results:
        result = results[0]
        assert result.match_type == 'regex'


def test_source_filtering():
    """Test filtering by source (ASVS vs OWASP)."""
    from tools.claude_code.lexical_search import LexicalSearchTool
    
    tool = LexicalSearchTool()
    
    # Test ASVS-only filtering
    asvs_results = tool.search_security_standards_lexical("validation", source="asvs")
    if asvs_results:
        assert all(result.source == "asvs" for result in asvs_results)
    
    # Test OWASP-only filtering  
    owasp_results = tool.search_security_standards_lexical("validation", source="owasp")
    if owasp_results:
        assert all(result.source == "owasp" for result in owasp_results)


def test_performance_requirement():
    """Test that searches complete in <0.5 seconds."""
    import time
    from tools.claude_code.lexical_search import LexicalSearchTool
    
    tool = LexicalSearchTool()
    
    # Measure search time
    start_time = time.time()
    results = tool.search_security_standards_lexical("authentication")
    end_time = time.time()
    
    search_time = end_time - start_time
    assert search_time < 0.5, f"Search took {search_time:.3f}s, must be <0.5s"


def test_security_input_validation():
    """Test input validation prevents malicious patterns."""
    from tools.claude_code.lexical_search import LexicalSearchTool
    
    tool = LexicalSearchTool()
    
    # Test empty pattern
    with pytest.raises(ValueError, match="Pattern cannot be empty"):
        tool.search_security_standards_lexical("")
    
    # Test extremely long pattern (ReDoS prevention)
    long_pattern = "a" * 1000
    with pytest.raises(ValueError, match="Pattern too long"):
        tool.search_security_standards_lexical(long_pattern)
    
    # Test potentially dangerous regex (simplified check)
    dangerous_pattern = r"(a+)+b"  # Known ReDoS pattern
    with pytest.raises(ValueError, match="Potentially dangerous regex pattern"):
        tool.search_security_standards_lexical(dangerous_pattern, regex=True)


def test_file_path_validation():
    """Test that file paths are properly validated."""
    from tools.claude_code.lexical_search import LexicalSearchTool
    
    tool = LexicalSearchTool()
    
    # Should work with default corpus
    results = tool.search_security_standards_lexical("test")
    # No exception should be raised
    
    # Test with custom corpus path (should validate path exists and is secure)
    with pytest.raises(ValueError, match="Invalid corpus path"):
        tool = LexicalSearchTool(corpus_path="/etc/passwd")  # Should be blocked