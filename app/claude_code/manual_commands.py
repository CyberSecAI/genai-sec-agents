#!/usr/bin/env python3
"""
Manual Security Analysis Commands for Claude Code

Provides manual command interface for triggering comprehensive security analysis
of files or workspaces directly from Claude Code IDE.
"""

import sys
import os
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import logging

# Add project root and app to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'app'))

try:
    from app.claude_code.analyze_context import CodeContextAnalyzer
    from app.claude_code.initialize_security_runtime import SecurityRuntimeManager
except ImportError as e:
    print(f"Error importing required components: {e}")
    sys.exit(1)


class SecurityAnalysisResults:
    """Structured format for manual analysis results with severity categorization."""
    
    def __init__(self):
        self.summary = {
            "total_issues": 0,
            "files_analyzed": 0,
            "analysis_time": 0,
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0
        }
        self.issues_by_severity = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }
        self.remediation_suggestions = []
        self.file_coverage = {}
        self.ci_cd_prediction = {
            "would_pass": True,
            "blocking_issues": [],
            "score": 100
        }


class ManualSecurityCommands:
    """Handles manual security analysis commands with comprehensive validation and security controls."""
    
    # Security configuration
    ALLOWED_EXTENSIONS = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs', '.rb', '.php',
        '.c', '.cpp', '.h', '.hpp', '.cs', '.kt', '.swift', '.sql', '.yaml', '.yml',
        '.json', '.xml', '.html', '.css', '.sh', '.bash', '.ps1', '.dockerfile'
    }
    
    MAX_FILE_SIZE = 1024 * 1024  # 1MB per file
    MAX_WORKSPACE_FILES = 1000   # Maximum files to analyze in workspace
    ANALYSIS_TIMEOUT = 30        # 30 seconds max per analysis
    
    def __init__(self):
        self.analyzer = CodeContextAnalyzer()
        self._initialized = False
        self._performance_metrics = {}
        
        # Security: Path validation patterns
        self._allowed_paths = set()
        self._project_root = Path.cwd()  # Assume current working directory is project root
        
    def initialize(self) -> bool:
        """Initialize the analyzer and runtime components."""
        try:
            if self.analyzer.initialize():
                self._initialized = True
                # Initialize allowed paths from current working directory
                self._allowed_paths.add(self._project_root.resolve())
                return True
        except Exception as e:
            logging.error(f"Failed to initialize manual commands: {e}")
        return False
    
    def _validate_file_path(self, file_path: str) -> Path:
        """Validate and sanitize file path to prevent traversal attacks.
        
        Args:
            file_path: User-provided file path
            
        Returns:
            Validated Path object
            
        Raises:
            ValueError: If path is invalid or unsafe
        """
        if not file_path or not isinstance(file_path, str):
            raise ValueError("File path must be a non-empty string")
        
        try:
            # Convert to Path and resolve
            path_obj = Path(file_path).resolve()
            
            # Security: Ensure path is within project boundaries
            if not any(str(path_obj).startswith(str(allowed)) for allowed in self._allowed_paths):
                # Check if it's within current working directory
                if not str(path_obj).startswith(str(self._project_root.resolve())):
                    raise ValueError(f"Path access denied: {file_path} is outside project boundaries")
            
            # Security: Check file extension
            if path_obj.suffix.lower() not in self.ALLOWED_EXTENSIONS:
                raise ValueError(f"File type not allowed: {path_obj.suffix}")
            
            # Security: Check file size
            if path_obj.exists() and path_obj.stat().st_size > self.MAX_FILE_SIZE:
                raise ValueError(f"File too large: {path_obj} exceeds {self.MAX_FILE_SIZE} bytes")
            
            return path_obj
            
        except (OSError, ValueError) as e:
            raise ValueError(f"Invalid file path: {e}")
    
    def _validate_analysis_depth(self, depth: str) -> str:
        """Validate analysis depth parameter.
        
        Args:
            depth: Analysis depth level
            
        Returns:
            Validated depth string
            
        Raises:
            ValueError: If depth is invalid
        """
        valid_depths = {"standard", "comprehensive"}
        if depth not in valid_depths:
            raise ValueError(f"Invalid analysis depth: {depth}. Must be one of {valid_depths}")
        return depth
    
    def _validate_workspace_path(self, path: str) -> Path:
        """Validate workspace path against traversal attacks.
        
        Args:
            path: User-provided workspace path
            
        Returns:
            Validated Path object
            
        Raises:
            ValueError: If path is invalid or unsafe
        """
        if not path or not isinstance(path, str):
            raise ValueError("Workspace path must be a non-empty string")
        
        try:
            # Convert to Path and resolve
            path_obj = Path(path).resolve()
            
            # Security: Ensure path is within project boundaries
            if not str(path_obj).startswith(str(self._project_root.resolve())):
                raise ValueError(f"Workspace access denied: {path} is outside project boundaries")
            
            # Must be a directory
            if path_obj.exists() and not path_obj.is_dir():
                raise ValueError(f"Workspace path must be a directory: {path}")
            
            return path_obj
            
        except (OSError, ValueError) as e:
            raise ValueError(f"Invalid workspace path: {e}")
    
    def _discover_workspace_files(self, workspace_path: Path, 
                                 filters: Optional[List[str]] = None) -> List[Path]:
        """Safely discover files in workspace with security controls.
        
        Args:
            workspace_path: Root directory to search
            filters: Optional file patterns to include
            
        Returns:
            List of valid file paths within security limits
        """
        discovered_files = []
        
        if not workspace_path.exists():
            return discovered_files
        
        try:
            # Security: Limit search depth to prevent deep traversal
            max_depth = 10
            
            for file_path in workspace_path.rglob('*'):
                # Skip if not a file
                if not file_path.is_file():
                    continue
                
                # Security: Check depth
                relative_path = file_path.relative_to(workspace_path)
                if len(relative_path.parts) > max_depth:
                    continue
                
                # Security: Check file extension
                if file_path.suffix.lower() not in self.ALLOWED_EXTENSIONS:
                    continue
                
                # Security: Check file size
                try:
                    if file_path.stat().st_size > self.MAX_FILE_SIZE:
                        continue
                except OSError:
                    continue  # Skip files we can't access
                
                # Apply filters if provided
                if filters:
                    if not any(pattern in str(file_path) for pattern in filters):
                        continue
                
                discovered_files.append(file_path)
                
                # Security: Limit total files
                if len(discovered_files) >= self.MAX_WORKSPACE_FILES:
                    break
        
        except Exception as e:
            logging.warning(f"Error discovering workspace files: {e}")
        
        return discovered_files
    
    def _sanitize_for_ide_display(self, content: str) -> str:
        """Sanitize content for safe IDE display.
        
        Args:
            content: Raw content that may contain unsafe characters
            
        Returns:
            Sanitized content safe for IDE display
        """
        if not content:
            return ""
        
        # Remove potentially dangerous characters/sequences for IDE display
        import html
        
        # HTML escape for safety
        sanitized = html.escape(content)
        
        # Limit length to prevent UI issues
        MAX_DISPLAY_LENGTH = 10000
        if len(sanitized) > MAX_DISPLAY_LENGTH:
            sanitized = sanitized[:MAX_DISPLAY_LENGTH] + "\n[Content truncated for display]"
        
        return sanitized
    
    def _apply_resource_limits(self, analysis_func, *args, **kwargs):
        """Apply resource limits to analysis operations.
        
        Args:
            analysis_func: Function to execute with limits
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or raises TimeoutError
        """
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(analysis_func, *args, **kwargs)
            try:
                return future.result(timeout=self.ANALYSIS_TIMEOUT)
            except Exception as e:
                raise TimeoutError(f"Analysis timed out after {self.ANALYSIS_TIMEOUT} seconds: {e}")
    
    def analyze_file(self, file_path: str, analysis_depth: str = "standard") -> Dict[str, Any]:
        """Analyze a single file for security issues.
        
        Args:
            file_path: Path to the file to analyze
            analysis_depth: Level of analysis ("standard" or "comprehensive")
            
        Returns:
            Dictionary containing analysis results and recommendations
        """
        if not self._initialized:
            raise RuntimeError("Manual commands not initialized. Call initialize() first.")
        
        start_time = time.time()
        
        try:
            # Validate inputs
            validated_path = self._validate_file_path(file_path)
            validated_depth = self._validate_analysis_depth(analysis_depth)
            
            # Perform analysis with resource limits
            def _run_file_analysis():
                return self.analyzer.analyze_file_context(
                    str(validated_path), 
                    use_cache=True
                )
            
            analysis_result = self._apply_resource_limits(_run_file_analysis)
            
            # Build structured results
            results = SecurityAnalysisResults()
            results.summary["files_analyzed"] = 1
            results.summary["analysis_time"] = time.time() - start_time
            results.file_coverage[str(validated_path)] = {
                "status": "analyzed",
                "issues_found": len(analysis_result.get("selected_rules", [])),
                "frameworks_detected": analysis_result.get("frameworks", [])
            }
            
            # Process rules and categorize by severity
            selected_rules = analysis_result.get("selected_rules", [])
            for rule in selected_rules:
                severity = rule.get("severity", "medium")
                issue = {
                    "id": rule.get("id", "unknown"),
                    "title": rule.get("title", "Security Issue"),
                    "severity": severity,
                    "file": str(validated_path),
                    "description": rule.get("requirement", ""),
                    "recommendations": rule.get("do", []),
                    "avoid": rule.get("dont", [])
                }
                
                if severity in results.issues_by_severity:
                    results.issues_by_severity[severity].append(issue)
                    results.summary[f"{severity}_count"] += 1
            
            results.summary["total_issues"] = len(selected_rules)
            
            # Generate CI/CD prediction
            critical_high_count = (results.summary["critical_count"] + 
                                 results.summary["high_count"])
            results.ci_cd_prediction = {
                "would_pass": critical_high_count == 0,
                "blocking_issues": results.issues_by_severity["critical"] + results.issues_by_severity["high"],
                "score": max(0, 100 - (critical_high_count * 10))
            }
            
            return {
                "status": "success",
                "analysis_type": "single_file",
                "results": results.__dict__,
                "metadata": {
                    "file_path": str(validated_path),
                    "analysis_depth": validated_depth,
                    "execution_time": time.time() - start_time,
                    "timestamp": time.time()
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "metadata": {
                    "file_path": file_path,
                    "analysis_depth": analysis_depth,
                    "execution_time": time.time() - start_time,
                    "timestamp": time.time()
                }
            }
    
    def analyze_workspace(self, workspace_path: Optional[str] = None, 
                         analysis_depth: str = "standard") -> Dict[str, Any]:
        """Analyze entire workspace for security issues.
        
        Args:
            workspace_path: Path to workspace directory (defaults to current directory)
            analysis_depth: Level of analysis ("standard" or "comprehensive")
            
        Returns:
            Dictionary containing aggregated analysis results
        """
        if not self._initialized:
            raise RuntimeError("Manual commands not initialized. Call initialize() first.")
        
        start_time = time.time()
        
        # Default to current directory if not specified
        if workspace_path is None:
            workspace_path = str(self._project_root)
        
        try:
            # Validate inputs
            validated_path = self._validate_workspace_path(workspace_path)
            validated_depth = self._validate_analysis_depth(analysis_depth)
            
            # Discover files in workspace
            discovered_files = self._discover_workspace_files(validated_path)
            
            if not discovered_files:
                return {
                    "status": "success",
                    "analysis_type": "workspace",
                    "results": SecurityAnalysisResults().__dict__,
                    "metadata": {
                        "workspace_path": str(validated_path),
                        "files_found": 0,
                        "analysis_depth": validated_depth,
                        "execution_time": time.time() - start_time,
                        "timestamp": time.time()
                    }
                }
            
            # Aggregate results
            aggregated_results = SecurityAnalysisResults()
            aggregated_results.summary["files_analyzed"] = len(discovered_files)
            
            # Analyze each file
            for file_path in discovered_files:
                try:
                    def _run_single_analysis():
                        return self.analyzer.analyze_file_context(
                            str(file_path), 
                            use_cache=True
                        )
                    
                    file_result = self._apply_resource_limits(_run_single_analysis)
                    
                    # Track file coverage
                    aggregated_results.file_coverage[str(file_path)] = {
                        "status": "analyzed",
                        "issues_found": len(file_result.get("selected_rules", [])),
                        "frameworks_detected": file_result.get("frameworks", [])
                    }
                    
                    # Aggregate issues by severity
                    for rule in file_result.get("selected_rules", []):
                        severity = rule.get("severity", "medium")
                        issue = {
                            "id": rule.get("id", "unknown"),
                            "title": rule.get("title", "Security Issue"),
                            "severity": severity,
                            "file": str(file_path),
                            "description": rule.get("requirement", ""),
                            "recommendations": rule.get("do", []),
                            "avoid": rule.get("dont", [])
                        }
                        
                        if severity in aggregated_results.issues_by_severity:
                            aggregated_results.issues_by_severity[severity].append(issue)
                            aggregated_results.summary[f"{severity}_count"] += 1
                
                except Exception as e:
                    # Log error but continue with other files
                    logging.warning(f"Error analyzing {file_path}: {e}")
                    aggregated_results.file_coverage[str(file_path)] = {
                        "status": "error",
                        "error": str(e)
                    }
            
            # Calculate totals
            aggregated_results.summary["total_issues"] = sum(
                aggregated_results.summary[f"{sev}_count"] 
                for sev in ["critical", "high", "medium", "low"]
            )
            aggregated_results.summary["analysis_time"] = time.time() - start_time
            
            # Generate CI/CD prediction for workspace
            critical_high_count = (aggregated_results.summary["critical_count"] + 
                                 aggregated_results.summary["high_count"])
            aggregated_results.ci_cd_prediction = {
                "would_pass": critical_high_count == 0,
                "blocking_issues": (aggregated_results.issues_by_severity["critical"] + 
                                  aggregated_results.issues_by_severity["high"]),
                "score": max(0, 100 - (critical_high_count * 5))  # Less penalty for workspace
            }
            
            return {
                "status": "success",
                "analysis_type": "workspace",
                "results": aggregated_results.__dict__,
                "metadata": {
                    "workspace_path": str(validated_path),
                    "files_found": len(discovered_files),
                    "files_analyzed": len(aggregated_results.file_coverage),
                    "analysis_depth": validated_depth,
                    "execution_time": time.time() - start_time,
                    "timestamp": time.time()
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "metadata": {
                    "workspace_path": workspace_path,
                    "analysis_depth": analysis_depth,
                    "execution_time": time.time() - start_time,
                    "timestamp": time.time()
                }
            }


def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manual Security Analysis Commands")
    parser.add_argument("command", choices=["file", "workspace"], 
                       help="Analysis command type")
    parser.add_argument("--path", help="File or workspace path to analyze")
    parser.add_argument("--depth", choices=["standard", "comprehensive"], 
                       default="standard", help="Analysis depth")
    parser.add_argument("--format", choices=["json", "human"], 
                       default="human", help="Output format")
    
    args = parser.parse_args()
    
    # Initialize manual commands
    commands = ManualSecurityCommands()
    if not commands.initialize():
        print("ERROR: Failed to initialize security analysis components")
        return 1
    
    try:
        if args.command == "file":
            if not args.path:
                print("ERROR: --path is required for file analysis")
                return 1
            result = commands.analyze_file(args.path, args.depth)
        else:  # workspace
            result = commands.analyze_workspace(args.path, args.depth)
        
        # Output results
        if args.format == "json":
            import json
            print(json.dumps(result, indent=2))
        else:
            # Human-readable format
            if result["status"] == "error":
                print(f"ERROR: {result['error']}")
                return 1
            
            results = result["results"]
            summary = results["summary"]
            print(f"\n🔒 Security Analysis Results")
            print(f"📁 Files Analyzed: {summary['files_analyzed']}")
            print(f"🔍 Total Issues: {summary['total_issues']}")
            print(f"📊 Severity Breakdown:")
            print(f"  🚨 Critical: {summary['critical_count']}")
            print(f"  ⚠️ High: {summary['high_count']}")
            print(f"  📋 Medium: {summary['medium_count']}")
            print(f"  💡 Low: {summary['low_count']}")
            print(f"🎯 CI/CD Prediction: {'PASS' if results['ci_cd_prediction']['would_pass'] else 'FAIL'}")
            print(f"⏱️ Analysis Time: {summary['analysis_time']:.2f}s")
        
        return 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())