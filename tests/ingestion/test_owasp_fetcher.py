"""
Tests for OWASP Cheat Sheet Fetcher

Tests secure content acquisition, caching, and validation functionality.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import json

from app.ingestion.owasp_fetcher import OWASPFetcher, ContentMetadata


class TestOWASPFetcher:
    """Test OWASP content fetcher functionality"""
    
    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def fetcher(self, temp_cache_dir):
        """Create fetcher instance with temporary cache"""
        return OWASPFetcher(cache_dir=temp_cache_dir)
    
    def test_fetcher_initialization(self, fetcher, temp_cache_dir):
        """Test fetcher initializes correctly with cache directory"""
        assert fetcher.cache_dir == Path(temp_cache_dir)
        assert fetcher.cache_dir.exists()
        assert fetcher.metadata_file.name == "metadata.json"
        assert len(fetcher.SECURE_CODING_CHEATSHEETS) == 30  # Total target sheets
    
    def test_url_validation(self, fetcher):
        """Test URL validation accepts only official OWASP URLs"""
        valid_urls = [
            "https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html",
            "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html"
        ]
        
        invalid_urls = [
            "http://cheatsheetseries.owasp.org/cheatsheets/test.html",  # HTTP not HTTPS
            "https://malicious.com/cheatsheets/test.html",  # Wrong domain
            "https://cheatsheetseries.evil.org/test.html",  # Subdomain attack
            "ftp://cheatsheetseries.owasp.org/test.html"  # Wrong protocol
        ]
        
        for url in valid_urls:
            assert fetcher._validate_url(url), f"Should accept valid URL: {url}"
        
        for url in invalid_urls:
            assert not fetcher._validate_url(url), f"Should reject invalid URL: {url}"
    
    def test_content_hash_calculation(self, fetcher):
        """Test content hash calculation for integrity validation"""
        content1 = "This is test content"
        content2 = "This is different test content"
        content3 = "This is test content"  # Same as content1
        
        hash1 = fetcher._calculate_content_hash(content1)
        hash2 = fetcher._calculate_content_hash(content2)
        hash3 = fetcher._calculate_content_hash(content3)
        
        assert len(hash1) == 64  # SHA256 hex length
        assert hash1 != hash2  # Different content = different hash
        assert hash1 == hash3  # Same content = same hash
    
    def test_metadata_save_and_load(self, fetcher):
        """Test metadata persistence"""
        test_metadata = {
            'test-sheet': ContentMetadata(
                sheet_id='test-sheet',
                url='https://cheatsheetseries.owasp.org/test.html',
                fetched_at=datetime.now(),
                content_hash='test_hash_123',
                size_bytes=1024,
                last_modified='Wed, 21 Oct 2015 07:28:00 GMT',
                etag='"test-etag"'
            )
        }
        
        # Save metadata
        fetcher._save_metadata(test_metadata)
        assert fetcher.metadata_file.exists()
        
        # Load metadata
        loaded_metadata = fetcher._load_metadata()
        assert 'test-sheet' in loaded_metadata
        
        loaded_meta = loaded_metadata['test-sheet']
        assert loaded_meta.sheet_id == 'test-sheet'
        assert loaded_meta.url == 'https://cheatsheetseries.owasp.org/test.html'
        assert loaded_meta.content_hash == 'test_hash_123'
        assert loaded_meta.size_bytes == 1024
    
    def test_cache_validity_checks(self, fetcher, temp_cache_dir):
        """Test cache validity validation"""
        # Create test metadata
        metadata = ContentMetadata(
            sheet_id='test-sheet',
            url='https://cheatsheetseries.owasp.org/test.html',
            fetched_at=datetime.now() - timedelta(hours=1),  # Recent
            content_hash='valid_hash',
            size_bytes=100
        )
        
        # Create cache file with matching content
        cache_file = Path(temp_cache_dir) / "test-sheet.html"
        test_content = "Test OWASP content"
        with open(cache_file, 'w') as f:
            f.write(test_content)
        
        # Update metadata with correct hash
        metadata.content_hash = fetcher._calculate_content_hash(test_content)
        
        # Should be valid
        assert fetcher._is_cache_valid('test-sheet', metadata)
        
        # Test expired cache
        expired_metadata = ContentMetadata(
            sheet_id='test-sheet',
            url='https://cheatsheetseries.owasp.org/test.html', 
            fetched_at=datetime.now() - timedelta(hours=25),  # Expired
            content_hash=metadata.content_hash,
            size_bytes=100
        )
        assert not fetcher._is_cache_valid('test-sheet', expired_metadata)
        
        # Test corrupted cache (wrong hash)
        corrupted_metadata = ContentMetadata(
            sheet_id='test-sheet',
            url='https://cheatsheetseries.owasp.org/test.html',
            fetched_at=datetime.now() - timedelta(hours=1),
            content_hash='wrong_hash',
            size_bytes=100
        )
        assert not fetcher._is_cache_valid('test-sheet', corrupted_metadata)
    
    @patch('requests.Session.get')
    def test_fetch_content_from_url_success(self, mock_get, fetcher):
        """Test successful content fetching from URL"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Test OWASP content with substantial length to pass validation"
        mock_response.headers = {
            'content-type': 'text/html; charset=utf-8',
            'Last-Modified': 'Wed, 21 Oct 2015 07:28:00 GMT',
            'ETag': '"test-etag"'
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        url = "https://cheatsheetseries.owasp.org/test.html"
        content, last_modified, etag = fetcher._fetch_content_from_url(url)
        
        assert content == mock_response.text
        assert last_modified == 'Wed, 21 Oct 2015 07:28:00 GMT'
        assert etag == '"test-etag"'
        mock_get.assert_called_once_with(url, timeout=30)
    
    @patch('requests.Session.get')
    def test_fetch_content_validation_failures(self, mock_get, fetcher):
        """Test content validation catches various failure modes"""
        url = "https://cheatsheetseries.owasp.org/test.html"
        
        # Test wrong content type
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Test content"
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        with pytest.raises(RuntimeError, match="Content validation failed"):
            fetcher._fetch_content_from_url(url)
        
        # Test content too short
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.text = "Short"  # Too short
        
        with pytest.raises(RuntimeError, match="Content validation failed"):
            fetcher._fetch_content_from_url(url)
        
        # Test non-OWASP content
        mock_response.text = "This is some long content but not from OWASP and doesn't mention the organization at all"
        
        with pytest.raises(RuntimeError, match="Content validation failed"):
            fetcher._fetch_content_from_url(url)
    
    @patch('requests.Session.get')  
    def test_fetch_secure_coding_cheatsheets_with_cache(self, mock_get, fetcher, temp_cache_dir):
        """Test fetching with caching behavior"""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Test OWASP cheat sheet content with sufficient length for validation"
        mock_response.headers = {
            'content-type': 'text/html',
            'Last-Modified': 'Wed, 21 Oct 2015 07:28:00 GMT'
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # First fetch should hit network
        with patch.object(fetcher, 'SECURE_CODING_CHEATSHEETS', {'test-sheet': 'https://cheatsheetseries.owasp.org/test.html'}):
            results = fetcher.fetch_secure_coding_cheatsheets()
        
        assert len(results) == 1
        assert 'test-sheet' in results
        assert mock_get.called
        
        # Second fetch should use cache
        mock_get.reset_mock()
        results2 = fetcher.fetch_secure_coding_cheatsheets()
        
        assert len(results2) == 1
        assert results2 == results
        assert not mock_get.called  # Should not hit network
    
    def test_get_cache_statistics(self, fetcher, temp_cache_dir):
        """Test cache statistics calculation"""
        # Empty cache
        stats = fetcher.get_cache_statistics()
        assert stats['cached_sheets'] == 0
        assert stats['cache_coverage'] == 0
        assert stats['total_cache_size_mb'] == 0
        
        # Add some metadata
        test_metadata = {
            'sheet1': ContentMetadata(
                sheet_id='sheet1',
                url='https://cheatsheetseries.owasp.org/test1.html',
                fetched_at=datetime.now(),
                content_hash='hash1',
                size_bytes=1024
            ),
            'sheet2': ContentMetadata(
                sheet_id='sheet2', 
                url='https://cheatsheetseries.owasp.org/test2.html',
                fetched_at=datetime.now(),
                content_hash='hash2',
                size_bytes=2048
            )
        }
        
        fetcher._save_metadata(test_metadata)
        stats = fetcher.get_cache_statistics()
        
        assert stats['cached_sheets'] == 2
        assert stats['total_cache_size_mb'] == (1024 + 2048) / (1024 * 1024)
        assert stats['cache_coverage'] == 2 / 30  # 2 cached out of 30 total
        
    @patch('requests.Session.head')
    def test_check_for_updates(self, mock_head, fetcher):
        """Test update checking functionality"""
        # Setup existing metadata
        metadata = {
            'test-sheet': ContentMetadata(
                sheet_id='test-sheet',
                url='https://cheatsheetseries.owasp.org/test.html',
                fetched_at=datetime.now(),
                content_hash='old_hash',
                size_bytes=1024,
                last_modified='Wed, 21 Oct 2015 07:28:00 GMT',
                etag='"old-etag"'
            )
        }
        fetcher._save_metadata(metadata)
        
        # Mock response indicating no updates
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            'Last-Modified': 'Wed, 21 Oct 2015 07:28:00 GMT',  # Same
            'ETag': '"old-etag"'  # Same
        }
        mock_response.raise_for_status = Mock()
        mock_head.return_value = mock_response
        
        with patch.object(fetcher, 'SECURE_CODING_CHEATSHEETS', {'test-sheet': 'https://cheatsheetseries.owasp.org/test.html'}):
            has_updates = fetcher.check_for_updates('test-sheet')
        
        assert not has_updates
        
        # Mock response indicating updates available
        mock_response.headers = {
            'Last-Modified': 'Thu, 22 Oct 2015 07:28:00 GMT',  # Different
            'ETag': '"new-etag"'  # Different
        }
        
        has_updates = fetcher.check_for_updates('test-sheet')
        assert has_updates