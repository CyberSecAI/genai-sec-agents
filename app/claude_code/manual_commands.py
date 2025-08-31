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
    # Import semantic search components
    from app.semantic import SemanticSearchInterface, SemanticSearchFeatureFlags
    from app.semantic.semantic_search import SearchFilters
    SEMANTIC_SEARCH_AVAILABLE = True
except ImportError as e:
    print(f"Semantic search components not available: {e}")
    SEMANTIC_SEARCH_AVAILABLE = False
    
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
        
        # Semantic search integration
        self.semantic_search = None
        self.feature_flags = None
        if SEMANTIC_SEARCH_AVAILABLE:
            try:
                self.semantic_search = SemanticSearchInterface()
                self.feature_flags = SemanticSearchFeatureFlags()
            except Exception as e:
                logging.warning(f"Failed to initialize semantic search: {e}")
                self.semantic_search = None
                self.feature_flags = None
        
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
    
    def analyze_file_with_semantic_search(self, file_path: str, semantic_enabled: bool = False, 
                                         analysis_depth: str = "standard") -> Dict[str, Any]:
        """Enhanced file analysis with optional semantic search augmentation.
        
        Args:
            file_path: Path to the file to analyze
            semantic_enabled: Whether to enable semantic search enhancement
            analysis_depth: Level of analysis ("standard" or "comprehensive")
            
        Returns:
            Dictionary containing analysis results with semantic search supplements
        """
        if not self._initialized:
            raise RuntimeError("Manual commands not initialized. Call initialize() first.")
        
        start_time = time.time()
        
        # Check semantic search availability and feature flags
        use_semantic = (semantic_enabled and 
                       self.semantic_search is not None and 
                       self.feature_flags is not None and
                       self.feature_flags.is_runtime_retrieval_enabled())
        
        try:
            # Validate and get absolute path
            validated_path = self._validate_file_path(file_path)
            
            # Get base analysis results
            base_results = self.analyze_file(str(validated_path), analysis_depth)
            
            if not use_semantic:
                # Add note about semantic search availability
                if 'metadata' not in base_results:
                    base_results['metadata'] = {}
                base_results['metadata']['semantic_search_used'] = False
                base_results['metadata']['semantic_search_available'] = self.semantic_search is not None
                base_results['metadata']['semantic_search_enabled'] = semantic_enabled
                return base_results
            
            # Enhance with semantic search
            language = self._detect_language_from_extension(validated_path.suffix)
            
            # Read file content for context-aware search
            with open(validated_path, 'r', encoding='utf-8', errors='ignore') as f:
                file_content = f.read(10000)  # First 10KB for context
            
            # Perform semantic search
            semantic_results = self.semantic_search.search_by_context(file_content, language)
            
            # Merge results
            enhanced_results = self._merge_analysis_with_semantic(base_results, semantic_results)
            
            # Add processing metadata
            processing_time = time.time() - start_time
            enhanced_results['metadata']['semantic_search_used'] = True
            enhanced_results['metadata']['semantic_processing_time_ms'] = int((processing_time - base_results.get('analysis_time', 0)) * 1000)
            enhanced_results['metadata']['semantic_results_count'] = len(semantic_results.results)
            
            return enhanced_results
            
        except Exception as e:
            logging.error(f"Enhanced file analysis failed: {e}")
            # Fall back to base analysis
            return self.analyze_file(file_path, analysis_depth)
    
    def analyze_workspace_with_semantic_search(self, workspace_path: Optional[str] = None,
                                              semantic_options: Optional[Dict[str, Any]] = None,
                                              analysis_depth: str = "standard") -> Dict[str, Any]:
        """Enhanced workspace analysis with semantic search for edge case detection.
        
        Args:
            workspace_path: Path to workspace directory (defaults to current directory)
            semantic_options: Semantic search configuration options
            analysis_depth: Level of analysis ("standard" or "comprehensive")
            
        Returns:
            Dictionary containing workspace analysis results with semantic enhancements
        """
        if not self._initialized:
            raise RuntimeError("Manual commands not initialized. Call initialize() first.")
        
        start_time = time.time()
        
        # Parse semantic options
        semantic_options = semantic_options or {}
        semantic_enabled = semantic_options.get('enabled', False)
        filters = semantic_options.get('filters', {})
        
        # Check semantic search availability
        use_semantic = (semantic_enabled and 
                       self.semantic_search is not None and 
                       self.feature_flags is not None and
                       self.feature_flags.is_runtime_retrieval_enabled())
        
        try:
            # Get base workspace analysis
            base_results = self.analyze_workspace(workspace_path, analysis_depth)
            
            if not use_semantic:
                base_results['metadata']['semantic_search_used'] = False
                return base_results
            
            # Enhance with semantic search for edge cases
            semantic_enhancements = []
            
            # Search for common edge cases not covered by compiled rules
            edge_case_queries = [
                "authentication bypass vulnerability",
                "privilege escalation security flaw", 
                "race condition security issue",
                "memory leak security risk",
                "time-based attack vulnerability"
            ]
            
            # Create search filters based on workspace context
            search_filters = SearchFilters(
                languages=filters.get('languages', []),
                categories=filters.get('categories', []),
                severity_levels=filters.get('severity_levels', ['high', 'critical']),
                confidence_threshold=0.6  # Higher threshold for workspace analysis
            )
            
            for query in edge_case_queries:
                try:
                    semantic_results = self.semantic_search.search_query(query, search_filters)
                    if semantic_results.results:
                        high_confidence = semantic_results.get_high_confidence_results(0.7)
                        if high_confidence:
                            semantic_enhancements.extend(high_confidence[:2])  # Top 2 per query
                except Exception as e:
                    logging.warning(f"Semantic search failed for query '{query}': {e}")
                    continue
            
            # Merge semantic enhancements with base results
            enhanced_results = self._merge_workspace_with_semantic(base_results, semantic_enhancements)
            
            # Add processing metadata
            processing_time = time.time() - start_time
            enhanced_results['metadata']['semantic_search_used'] = True
            enhanced_results['metadata']['semantic_enhancements_count'] = len(semantic_enhancements)
            enhanced_results['metadata']['semantic_processing_time_ms'] = int((processing_time - base_results.get('analysis_time', 0)) * 1000)
            
            return enhanced_results
            
        except Exception as e:
            logging.error(f"Enhanced workspace analysis failed: {e}")
            # Fall back to base analysis
            return self.analyze_workspace(workspace_path, analysis_depth)
    
    def explain_security_guidance(self, rule_id: str, code_context: str) -> Dict[str, Any]:
        """Provide detailed explanation using semantic search for context.
        
        Args:
            rule_id: Security rule identifier to explain
            code_context: Code context for the explanation
            
        Returns:
            Dictionary containing detailed explanation and related guidance
        """
        if not self._initialized:
            raise RuntimeError("Manual commands not initialized. Call initialize() first.")
        
        explanation_result = {
            'rule_id': rule_id,
            'explanation': '',
            'related_guidance': [],
            'examples': [],
            'references': [],
            'semantic_search_used': False
        }
        
        # Check if explain mode is enabled and semantic search is available
        use_semantic = (self.semantic_search is not None and 
                       self.feature_flags is not None and
                       self.feature_flags.is_explain_mode_enabled())
        
        if not use_semantic:
            explanation_result['explanation'] = f"Basic explanation for {rule_id} - semantic search not available"
            return explanation_result
        
        try:
            # Use semantic search to find detailed explanation
            semantic_results = self.semantic_search.explain_rule_match(rule_id, code_context)
            
            if semantic_results.results:
                # Extract explanation from top semantic results
                top_results = semantic_results.get_top_results(3)
                
                explanation_parts = []
                related_guidance = []
                
                for result in top_results:
                    if result.confidence_score >= 0.7:
                        explanation_parts.append(f"• {result.snippet}")
                        
                        related_guidance.append({
                            'source': result.source_rule_id,
                            'category': result.category,
                            'severity': result.severity,
                            'guidance': result.snippet
                        })
                
                explanation_result['explanation'] = f"Detailed explanation for {rule_id}:\n" + "\n".join(explanation_parts)
                explanation_result['related_guidance'] = related_guidance
                explanation_result['semantic_search_used'] = True
            else:
                explanation_result['explanation'] = f"No detailed explanation found for {rule_id}"
            
            return explanation_result
            
        except Exception as e:
            logging.error(f"Explanation generation failed: {e}")
            explanation_result['explanation'] = f"Error generating explanation for {rule_id}: {str(e)}"
            return explanation_result
    
    def _merge_analysis_with_semantic(self, base_results: Dict[str, Any], semantic_results) -> Dict[str, Any]:
        """Merge base analysis results with semantic search results."""
        enhanced_results = base_results.copy()
        
        # Add semantic search section
        enhanced_results['semantic_supplements'] = {
            'query_used': semantic_results.query,
            'total_results': len(semantic_results.results),
            'high_confidence_matches': [],
            'additional_context': []
        }
        
        # Categorize semantic results
        high_confidence = semantic_results.get_high_confidence_results(0.7)
        medium_confidence = [r for r in semantic_results.results if 0.4 <= r.confidence_score < 0.7]
        
        # Add high confidence matches as primary supplements
        for result in high_confidence:
            enhanced_results['semantic_supplements']['high_confidence_matches'].append({
                'rule_id': result.source_rule_id,
                'confidence': result.confidence_score,
                'category': result.category,
                'severity': result.severity,
                'guidance': result.snippet
            })
        
        # Add medium confidence as additional context
        for result in medium_confidence[:3]:  # Limit to top 3
            enhanced_results['semantic_supplements']['additional_context'].append({
                'rule_id': result.source_rule_id,
                'confidence': result.confidence_score,
                'context': result.snippet
            })
        
        return enhanced_results
    
    def _merge_workspace_with_semantic(self, base_results: Dict[str, Any], semantic_enhancements: List) -> Dict[str, Any]:
        """Merge workspace analysis with semantic enhancements."""
        enhanced_results = base_results.copy()
        
        # Add semantic enhancements section
        enhanced_results['semantic_edge_cases'] = {
            'total_enhancements': len(semantic_enhancements),
            'edge_case_detections': [],
            'additional_recommendations': []
        }
        
        # Process semantic enhancements
        for enhancement in semantic_enhancements:
            edge_case = {
                'rule_id': enhancement.source_rule_id,
                'confidence': enhancement.confidence_score,
                'category': enhancement.category,
                'severity': enhancement.severity,
                'description': enhancement.snippet,
                'source_type': 'semantic_search'
            }
            
            if enhancement.confidence_score >= 0.8:
                enhanced_results['semantic_edge_cases']['edge_case_detections'].append(edge_case)
            else:
                enhanced_results['semantic_edge_cases']['additional_recommendations'].append(edge_case)
        
        return enhanced_results
    
    def _detect_language_from_extension(self, extension: str) -> str:
        """Detect programming language from file extension."""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript', 
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.c': 'c',
            '.cpp': 'cpp',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.kt': 'kotlin',
            '.swift': 'swift'
        }
        return extension_map.get(extension.lower(), 'unknown')
    
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
    parser.add_argument("command", choices=["file", "workspace", "explain"], 
                       help="Analysis command type")
    parser.add_argument("--path", help="File or workspace path to analyze")
    parser.add_argument("--depth", choices=["standard", "comprehensive"], 
                       default="standard", help="Analysis depth")
    parser.add_argument("--format", choices=["json", "human"], 
                       default="human", help="Output format")
    parser.add_argument("--semantic", action="store_true", 
                       help="Enable semantic search enhancement (requires feature flag)")
    parser.add_argument("--semantic-filters", help="JSON string with semantic search filters")
    parser.add_argument("--rule-id", help="Rule ID for explanation command")
    parser.add_argument("--code-context", help="Code context for explanation command")
    
    args = parser.parse_args()
    
    # Initialize manual commands
    commands = ManualSecurityCommands()
    if not commands.initialize():
        print("ERROR: Failed to initialize security analysis components")
        return 1
    
    try:
        # Parse semantic filters if provided
        semantic_options = {}
        if args.semantic_filters:
            import json
            try:
                semantic_options = json.loads(args.semantic_filters)
            except json.JSONDecodeError:
                print("ERROR: Invalid JSON format for --semantic-filters")
                return 1
        
        if args.command == "file":
            if not args.path:
                print("ERROR: --path is required for file analysis")
                return 1
            
            if args.semantic:
                result = commands.analyze_file_with_semantic_search(
                    args.path, semantic_enabled=True, analysis_depth=args.depth
                )
            else:
                result = commands.analyze_file(args.path, args.depth)
                
        elif args.command == "workspace":
            semantic_options['enabled'] = args.semantic
            
            if args.semantic:
                result = commands.analyze_workspace_with_semantic_search(
                    args.path, semantic_options=semantic_options, analysis_depth=args.depth
                )
            else:
                result = commands.analyze_workspace(args.path, args.depth)
                
        elif args.command == "explain":
            if not args.rule_id:
                print("ERROR: --rule-id is required for explain command")
                return 1
            if not args.code_context:
                print("ERROR: --code-context is required for explain command")
                return 1
                
            explanation_result = commands.explain_security_guidance(args.rule_id, args.code_context)
            
            # Format explanation output
            if args.format == "json":
                import json
                print(json.dumps(explanation_result, indent=2))
            else:
                print(f"\n🔍 **Security Rule Explanation**")
                print(f"📋 Rule ID: {explanation_result['rule_id']}")
                print(f"🔍 Semantic Search Used: {'✅' if explanation_result['semantic_search_used'] else '❌'}")
                print(f"\n📝 **Explanation:**")
                print(explanation_result['explanation'])
                
                if explanation_result['related_guidance']:
                    print(f"\n🎯 **Related Guidance:**")
                    for guidance in explanation_result['related_guidance']:
                        print(f"  • {guidance['source']} ({guidance['category']}) - {guidance['severity']}")
                        print(f"    └─ {guidance['guidance'][:100]}...")
            
            return 0
        else:
            print(f"ERROR: Unknown command: {args.command}")
            return 1
        
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
            
            # Display semantic search information if available
            metadata = results.get('metadata', {})
            if 'semantic_search_used' in metadata:
                semantic_used = metadata['semantic_search_used']
                print(f"🔍 Semantic Search: {'✅ Enhanced' if semantic_used else '❌ Not Used'}")
                
                if semantic_used:
                    if 'semantic_processing_time_ms' in metadata:
                        print(f"   ⏱️ Semantic Processing: {metadata['semantic_processing_time_ms']}ms")
                    if 'semantic_results_count' in metadata:
                        print(f"   📊 Semantic Matches: {metadata['semantic_results_count']}")
            
            # Display semantic supplements if available
            if 'semantic_supplements' in results:
                supplements = results['semantic_supplements']
                if supplements['high_confidence_matches']:
                    print(f"\n🎯 **High Confidence Semantic Matches:**")
                    for match in supplements['high_confidence_matches'][:3]:  # Top 3
                        print(f"  • {match['rule_id']} [{match['confidence']:.2f}] ({match['category']})")
                        print(f"    └─ {match['guidance'][:80]}...")
            
            # Display semantic edge cases if available
            if 'semantic_edge_cases' in results:
                edge_cases = results['semantic_edge_cases']
                if edge_cases['edge_case_detections']:
                    print(f"\n🔍 **Semantic Edge Case Detections:**")
                    for case in edge_cases['edge_case_detections'][:3]:  # Top 3
                        print(f"  • {case['rule_id']} [{case['confidence']:.2f}] ({case['category']})")
                        print(f"    └─ {case['description'][:80]}...")
                
                if edge_cases['additional_recommendations']:
                    print(f"\n💡 **Additional Semantic Recommendations:**")
                    for rec in edge_cases['additional_recommendations'][:2]:  # Top 2
                        print(f"  • {rec['rule_id']} [{rec['confidence']:.2f}]")
                        print(f"    └─ {rec['description'][:80]}...")
        
        return 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())