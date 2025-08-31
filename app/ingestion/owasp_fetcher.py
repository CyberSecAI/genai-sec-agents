"""
OWASP Cheat Sheet Content Fetcher

Securely fetches and caches OWASP cheat sheet markdown content from GitHub repository
with integrity validation and version tracking. Focuses on secure coding related cheat sheets only.
"""

import hashlib
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import requests
from dataclasses import dataclass


@dataclass
class ContentMetadata:
    """Metadata for cached OWASP content"""
    sheet_id: str
    url: str
    fetched_at: datetime
    content_hash: str
    size_bytes: int
    last_modified: Optional[str] = None
    etag: Optional[str] = None


class OWASPFetcher:
    """Secure OWASP cheat sheet content fetcher with caching and validation"""
    
    # Focus on secure coding related cheat sheets only - GitHub raw URLs for markdown files
    SECURE_CODING_CHEATSHEETS = {
        # Priority 1: Core Secure Coding (15 sheets)
        'input-validation': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Input_Validation_Cheat_Sheet.md',
        'sql-injection-prevention': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.md',
        'xss-prevention': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.md',
        'csrf-prevention': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.md',
        'authentication': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Authentication_Cheat_Sheet.md',
        'session-management': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Session_Management_Cheat_Sheet.md',
        'cryptographic-storage': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Cryptographic_Storage_Cheat_Sheet.md',
        'error-handling': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Error_Handling_Cheat_Sheet.md',
        'logging': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Logging_Cheat_Sheet.md',
        'file-upload': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/File_Upload_Cheat_Sheet.md',
        'http-headers': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/HTTP_Headers_Cheat_Sheet.md',
        'content-security-policy': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Content_Security_Policy_Cheat_Sheet.md',
        'clickjacking-defense': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Clickjacking_Defense_Cheat_Sheet.md',
        'dom-xss-prevention': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.md',
        'unvalidated-redirects': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.md',
        
        # Priority 2: Language-Specific Secure Coding (8 sheets)
        'java-security': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Java_Security_Cheat_Sheet.md',
        'dotnet-security': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/DotNet_Security_Cheat_Sheet.md',
        'python-security': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Python_Security_Cheat_Sheet.md',
        'nodejs-security': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Nodejs_Security_Cheat_Sheet.md',
        'csharp-security': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/DotNet_Security_Cheat_Sheet.md',
        'php-security': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/PHP_Configuration_Cheat_Sheet.md',
        'ruby-security': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Ruby_on_Rails_Security_Cheat_Sheet.md',
        'go-security': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Go_SCP.md',
        
        # Priority 3: Framework-Specific Secure Coding (7 sheets)  
        'spring-security': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Spring_Security_Cheat_Sheet.md',
        'django-security': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Django_Security_Cheat_Sheet.md',
        'react-security': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/React_Security_Cheat_Sheet.md',
        'angular-security': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Angular_Security_Cheat_Sheet.md',
        'vuejs-security': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Vue_Security_Cheat_Sheet.md',
        'expressjs-security': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Nodejs_Security_Cheat_Sheet.md',
        'laravel-security': 'https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Laravel_Cheat_Sheet.md'
    }
    
    def __init__(self, cache_dir: str = "data/owasp_cache"):
        """Initialize fetcher with cache directory"""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.cache_dir / "metadata.json"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GenAI-Security-Agents/1.0 (Educational/Research)',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
        
    def _load_metadata(self) -> Dict[str, ContentMetadata]:
        """Load cached content metadata"""
        if not self.metadata_file.exists():
            return {}
            
        try:
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)
                
            metadata = {}
            for sheet_id, meta_dict in data.items():
                metadata[sheet_id] = ContentMetadata(
                    sheet_id=meta_dict['sheet_id'],
                    url=meta_dict['url'],
                    fetched_at=datetime.fromisoformat(meta_dict['fetched_at']),
                    content_hash=meta_dict['content_hash'],
                    size_bytes=meta_dict['size_bytes'],
                    last_modified=meta_dict.get('last_modified'),
                    etag=meta_dict.get('etag')
                )
            return metadata
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Warning: Could not load metadata: {e}")
            return {}
    
    def _save_metadata(self, metadata: Dict[str, ContentMetadata]) -> None:
        """Save content metadata to cache"""
        data = {}
        for sheet_id, meta in metadata.items():
            data[sheet_id] = {
                'sheet_id': meta.sheet_id,
                'url': meta.url,
                'fetched_at': meta.fetched_at.isoformat(),
                'content_hash': meta.content_hash,
                'size_bytes': meta.size_bytes,
                'last_modified': meta.last_modified,
                'etag': meta.etag
            }
            
        with open(self.metadata_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL is from official OWASP GitHub repository"""
        try:
            parsed = urlparse(url)
            return (parsed.netloc == 'raw.githubusercontent.com' and 
                    parsed.scheme == 'https' and
                    '/OWASP/CheatSheetSeries/' in parsed.path and
                    parsed.path.endswith('.md'))
        except Exception:
            return False
    
    def _calculate_content_hash(self, content: str) -> str:
        """Calculate SHA256 hash of content for integrity validation"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _fetch_content_from_url(self, url: str) -> Tuple[str, Optional[str], Optional[str]]:
        """Fetch content from URL with error handling"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Validate content type for markdown
            content_type = response.headers.get('content-type', '')
            if 'text/plain' not in content_type and 'text/markdown' not in content_type:
                # GitHub serves markdown as text/plain, but be flexible
                print(f"Warning: Unexpected content type: {content_type}")
            
            content = response.text
            last_modified = response.headers.get('Last-Modified')
            etag = response.headers.get('ETag')
            
            # Basic content validation for markdown
            if len(content) < 500:  # OWASP cheat sheets are substantial
                raise ValueError("Content too short - possible error page")
                
            # Check for markdown indicators and OWASP content
            if not content.startswith('#') and '# ' not in content[:200]:
                raise ValueError("Content does not appear to be markdown")
                
            if 'OWASP' not in content and 'owasp' not in content.lower():
                raise ValueError("Content does not appear to be OWASP content")
            
            return content, last_modified, etag
            
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch {url}: {e}")
        except Exception as e:
            raise RuntimeError(f"Content validation failed for {url}: {e}")
    
    def _is_cache_valid(self, sheet_id: str, metadata: ContentMetadata) -> bool:
        """Check if cached content is still valid"""
        # Cache expires after 24 hours
        if datetime.now() - metadata.fetched_at > timedelta(hours=24):
            return False
            
        # Check if cached file exists
        cache_file = self.cache_dir / f"{sheet_id}.md"
        if not cache_file.exists():
            return False
            
        # Validate cached content integrity
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_content = f.read()
            
            if self._calculate_content_hash(cached_content) != metadata.content_hash:
                return False
                
        except Exception:
            return False
            
        return True
    
    def fetch_secure_coding_cheatsheets(self, force_refresh: bool = False) -> Dict[str, str]:
        """
        Fetch all secure coding related OWASP cheat sheets
        
        Args:
            force_refresh: Force refresh of cached content
            
        Returns:
            Dict mapping sheet_id to HTML content
            
        Raises:
            RuntimeError: If fetching fails for critical sheets
        """
        metadata = self._load_metadata()
        results = {}
        updated_metadata = metadata.copy()
        
        for sheet_id, url in self.SECURE_CODING_CHEATSHEETS.items():
            try:
                print(f"Processing {sheet_id}...")
                
                # Validate URL security
                if not self._validate_url(url):
                    print(f"Warning: Skipping invalid URL for {sheet_id}: {url}")
                    continue
                
                # Check cache validity
                if (not force_refresh and 
                    sheet_id in metadata and 
                    self._is_cache_valid(sheet_id, metadata[sheet_id])):
                    
                    # Load from cache
                    cache_file = self.cache_dir / f"{sheet_id}.md"
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    results[sheet_id] = content
                    print(f"  ✓ Loaded from cache")
                    continue
                
                # Fetch from URL
                content, last_modified, etag = self._fetch_content_from_url(url)
                
                # Cache the content
                cache_file = self.cache_dir / f"{sheet_id}.md"
                with open(cache_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Update metadata
                updated_metadata[sheet_id] = ContentMetadata(
                    sheet_id=sheet_id,
                    url=url,
                    fetched_at=datetime.now(),
                    content_hash=self._calculate_content_hash(content),
                    size_bytes=len(content.encode('utf-8')),
                    last_modified=last_modified,
                    etag=etag
                )
                
                results[sheet_id] = content
                print(f"  ✓ Fetched from URL ({len(content)} chars)")
                
                # Rate limiting - be respectful to OWASP servers
                time.sleep(1)
                
            except Exception as e:
                print(f"  ✗ Failed to fetch {sheet_id}: {e}")
                # Continue with other sheets - don't fail entire process
                continue
        
        # Save updated metadata
        self._save_metadata(updated_metadata)
        
        if not results:
            raise RuntimeError("Failed to fetch any OWASP cheat sheets")
        
        print(f"\nSuccessfully fetched {len(results)} cheat sheets")
        return results
    
    def check_for_updates(self, sheet_id: str) -> bool:
        """
        Check if a specific cheat sheet has been updated
        
        Args:
            sheet_id: ID of sheet to check
            
        Returns:
            True if content has been updated
        """
        if sheet_id not in self.SECURE_CODING_CHEATSHEETS:
            return False
            
        metadata = self._load_metadata()
        if sheet_id not in metadata:
            return True  # Never fetched before
            
        url = self.SECURE_CODING_CHEATSHEETS[sheet_id]
        try:
            # Use HEAD request to check for updates efficiently
            response = self.session.head(url, timeout=10)
            response.raise_for_status()
            
            cached_meta = metadata[sheet_id]
            
            # Check Last-Modified header
            if response.headers.get('Last-Modified'):
                if cached_meta.last_modified != response.headers['Last-Modified']:
                    return True
            
            # Check ETag header  
            if response.headers.get('ETag'):
                if cached_meta.etag != response.headers['ETag']:
                    return True
                    
            return False
            
        except Exception as e:
            print(f"Warning: Could not check updates for {sheet_id}: {e}")
            return False
    
    def get_cache_statistics(self) -> Dict[str, any]:
        """Get statistics about cached content"""
        metadata = self._load_metadata()
        
        total_sheets = len(self.SECURE_CODING_CHEATSHEETS)
        cached_sheets = len(metadata)
        total_size = sum(meta.size_bytes for meta in metadata.values())
        
        oldest_fetch = None
        newest_fetch = None
        
        if metadata:
            fetch_times = [meta.fetched_at for meta in metadata.values()]
            oldest_fetch = min(fetch_times)
            newest_fetch = max(fetch_times)
        
        return {
            'total_sheets_available': total_sheets,
            'cached_sheets': cached_sheets,
            'cache_coverage': cached_sheets / total_sheets if total_sheets > 0 else 0,
            'total_cache_size_mb': total_size / (1024 * 1024),
            'oldest_fetch': oldest_fetch.isoformat() if oldest_fetch else None,
            'newest_fetch': newest_fetch.isoformat() if newest_fetch else None,
            'cache_directory': str(self.cache_dir)
        }