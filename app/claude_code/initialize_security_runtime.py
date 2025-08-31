#!/usr/bin/env python3
"""
Security Runtime Initialization for Claude Code Sub-Agent

Initializes the AgenticRuntime from Story 2.1 and loads compiled security packages
for use by the security-guidance sub-agent.
"""

import sys
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root and app to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'app'))

try:
    from app.runtime.core import AgenticRuntime
except ImportError as e:
    print(f"Error importing AgenticRuntime: {e}")
    print("Ensure Story 2.1 runtime components are available in app/runtime/")
    sys.exit(1)


class SecurityRuntimeManager:
    """Manages security runtime initialization for Claude Code sub-agent with performance optimizations."""
    
    def __init__(self):
        self.runtime: Optional[AgenticRuntime] = None
        self.loaded_packages: Dict[str, Any] = {}
        # Task 4: Performance optimization caches
        self._package_cache: Dict[str, Dict[str, Any]] = {}
        self._initialization_cache: Dict[str, Any] = {}
        self._performance_metrics: Dict[str, float] = {}
        
    def initialize(self, force_reload: bool = False) -> bool:
        """Initialize security runtime and load compiled packages with performance optimization.
        
        Args:
            force_reload: Force reload packages ignoring cache
            
        Returns:
            bool: True if initialization successful, False otherwise
        """
        start_time = time.time()
        
        try:
            # Task 4: Check initialization cache first unless force_reload
            cache_key = self._get_initialization_cache_key()
            if not force_reload and cache_key in self._initialization_cache:
                cached_data = self._initialization_cache[cache_key]
                if cached_data['valid'] and time.time() - cached_data['timestamp'] < 300:  # 5 min cache
                    self.runtime = cached_data['runtime']
                    self.loaded_packages = cached_data['packages']
                    self._performance_metrics['initialization_time'] = time.time() - start_time
                    return True
            
            # Initialize the AgenticRuntime from Story 2.1
            self.runtime = AgenticRuntime()
            
            # Load compiled packages from dist/agents/
            package_dir = Path(__file__).parent.parent / 'dist' / 'agents'
            if not package_dir.exists():
                print(f"Package directory not found: {package_dir}")
                return False
                
            # Task 4: Batch load packages for better performance
            package_files = list(package_dir.glob('*.json'))
            if not package_files:
                print(f"No compiled agent packages found in {package_dir}")
                return False
            
            # Task 4: Parallel package loading (simulated with optimized loading)
            loaded_count = 0
            for package_file in package_files:
                try:
                    agent_name = package_file.stem
                    
                    # Task 4: Check package cache first
                    package_hash = self._get_package_hash(package_file)
                    if package_hash in self._package_cache:
                        cached_package = self._package_cache[package_hash]
                        self.loaded_packages[agent_name] = package_file
                        loaded_count += 1
                        print(f"Loaded agent: {package_file.name} (cached)")
                        continue
                    
                    # Load package and cache it
                    if self.runtime.load_agent(agent_name):
                        self.loaded_packages[agent_name] = package_file
                        self._package_cache[package_hash] = {
                            'agent_name': agent_name,
                            'file_path': str(package_file),
                            'timestamp': time.time()
                        }
                        loaded_count += 1
                        print(f"Loaded agent: {package_file.name}")
                    else:
                        print(f"Failed to load agent {package_file.name}")
                        
                except Exception as e:
                    print(f"Failed to load agent {package_file.name}: {e}")
            
            # Task 4: Cache initialization result
            if loaded_count > 0:
                self._initialization_cache[cache_key] = {
                    'runtime': self.runtime,
                    'packages': self.loaded_packages.copy(),
                    'timestamp': time.time(),
                    'valid': True
                }
            
            initialization_time = time.time() - start_time
            self._performance_metrics['initialization_time'] = initialization_time
            self._performance_metrics['packages_loaded'] = loaded_count
            
            return loaded_count > 0
            
        except Exception as e:
            print(f"Failed to initialize security runtime: {e}")
            return False
    
    def _get_initialization_cache_key(self) -> str:
        """Generate cache key for initialization state."""
        package_dir = Path(__file__).parent.parent / 'dist' / 'agents'
        if not package_dir.exists():
            return "no_packages"
        
        # Create hash based on package directory contents
        package_files = sorted(package_dir.glob('*.json'))
        content_hash = hashlib.md5()
        for file in package_files:
            content_hash.update(f"{file.name}:{file.stat().st_mtime}".encode())
        
        return content_hash.hexdigest()
    
    def _get_package_hash(self, package_file: Path) -> str:
        """Generate hash for package file for caching."""
        stat = package_file.stat()
        return hashlib.md5(f"{package_file.name}:{stat.st_mtime}:{stat.st_size}".encode()).hexdigest()
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get performance metrics for monitoring."""
        return self._performance_metrics.copy()
    
    def get_runtime(self) -> Optional[AgenticRuntime]:
        """Get the initialized runtime instance."""
        return self.runtime
    
    def get_loaded_packages(self) -> Dict[str, Any]:
        """Get information about loaded packages."""
        return self.loaded_packages


def main():
    """Main entry point for runtime initialization."""
    manager = SecurityRuntimeManager()
    
    if manager.initialize():
        print("✅ Security runtime initialized successfully")
        print(f"📦 Loaded {len(manager.get_loaded_packages())} security packages")
        
        # Output package information for sub-agent
        packages = manager.get_loaded_packages()
        for package_name, package_path in packages.items():
            print(f"  - {package_name}: {package_path}")
            
        return 0
    else:
        print("❌ Failed to initialize security runtime")
        return 1


if __name__ == "__main__":
    sys.exit(main())