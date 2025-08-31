"""
Search Results for Semantic Search

Handles search result formatting, provenance tracking, and integration
with compiled rule results for unified security guidance display.
"""

import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class SearchMatch:
    """Individual search result match with metadata."""
    content: str
    confidence_score: float
    source_rule_id: str
    source_file: str
    source_type: str  # 'compiled', 'yaml', 'external'
    snippet: str
    category: Optional[str] = None
    severity: Optional[str] = None
    language: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'content': self.content,
            'confidence_score': self.confidence_score,
            'source_rule_id': self.source_rule_id,
            'source_file': self.source_file,
            'source_type': self.source_type,
            'snippet': self.snippet,
            'category': self.category,
            'severity': self.severity,
            'language': self.language
        }


@dataclass
class SearchProvenance:
    """Provenance tracking for search results."""
    query: str
    timestamp: datetime
    corpus_version: str
    search_method: str
    filters_applied: Dict[str, Any]
    total_results: int
    processing_time_ms: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'query': self.query,
            'timestamp': self.timestamp.isoformat(),
            'corpus_version': self.corpus_version,
            'search_method': self.search_method,
            'filters_applied': self.filters_applied,
            'total_results': self.total_results,
            'processing_time_ms': self.processing_time_ms
        }


class SemanticSearchResults:
    """Formatted search results with provenance and confidence scoring."""
    
    def __init__(self, query: str, results: List[SearchMatch], provenance: Optional[SearchProvenance] = None):
        self.query = query
        self.results = results
        self.provenance = provenance or SearchProvenance(
            query=query,
            timestamp=datetime.now(timezone.utc),
            corpus_version="unknown",
            search_method="semantic",
            filters_applied={},
            total_results=len(results),
            processing_time_ms=0
        )
        
    def get_high_confidence_results(self, threshold: float = 0.7) -> List[SearchMatch]:
        """Get results above confidence threshold."""
        return [result for result in self.results if result.confidence_score >= threshold]
    
    def get_results_by_severity(self, severity: str) -> List[SearchMatch]:
        """Get results filtered by severity level."""
        return [result for result in self.results if result.severity == severity]
    
    def get_results_by_category(self, category: str) -> List[SearchMatch]:
        """Get results filtered by security category."""
        return [result for result in self.results if result.category == category]
    
    def get_top_results(self, limit: int = 10) -> List[SearchMatch]:
        """Get top N results sorted by confidence score."""
        sorted_results = sorted(self.results, key=lambda r: r.confidence_score, reverse=True)
        return sorted_results[:limit]
    
    def format_for_display(self, format_type: str = "ide") -> str:
        """Format results for IDE display with clear semantic/compiled differentiation."""
        if format_type == "ide":
            return self._format_ide_display()
        elif format_type == "json":
            return self._format_json_display()
        elif format_type == "console":
            return self._format_console_display()
        else:
            raise ValueError(f"Unsupported format type: {format_type}")
    
    def _format_ide_display(self) -> str:
        """Format for IDE integration with clear visual indicators."""
        lines = []
        
        # Header with semantic search indicator
        lines.append("🔍 **Semantic Search Results**")
        lines.append(f"📝 Query: {self.query}")
        lines.append(f"📊 Results: {len(self.results)} matches")
        
        if self.provenance.processing_time_ms > 0:
            lines.append(f"⏱️ Processing Time: {self.provenance.processing_time_ms}ms")
        
        lines.append("")
        
        # Group results by confidence level
        high_confidence = self.get_high_confidence_results(0.7)
        medium_confidence = [r for r in self.results if 0.4 <= r.confidence_score < 0.7]
        low_confidence = [r for r in self.results if r.confidence_score < 0.4]
        
        if high_confidence:
            lines.append("🎯 **High Confidence Matches:**")
            for result in high_confidence[:5]:  # Limit to top 5
                lines.append(self._format_result_item(result))
            lines.append("")
        
        if medium_confidence:
            lines.append("🔍 **Medium Confidence Matches:**")
            for result in medium_confidence[:3]:  # Limit to top 3
                lines.append(self._format_result_item(result))
            lines.append("")
        
        if low_confidence:
            lines.append("💭 **Additional Context:**")
            for result in low_confidence[:2]:  # Limit to top 2
                lines.append(self._format_result_item(result))
            lines.append("")
        
        # Provenance footer
        lines.append(f"🔒 **Search Provenance:** {self.provenance.search_method} | {self.provenance.corpus_version}")
        
        return "\n".join(lines)
    
    def _format_console_display(self) -> str:
        """Format for console/terminal display."""
        lines = []
        
        lines.append("=== SEMANTIC SEARCH RESULTS ===")
        lines.append(f"Query: {self.query}")
        lines.append(f"Results: {len(self.results)}")
        lines.append("")
        
        for i, result in enumerate(self.get_top_results(10), 1):
            lines.append(f"{i}. [{result.confidence_score:.2f}] {result.source_rule_id}")
            lines.append(f"   Category: {result.category or 'N/A'}")
            lines.append(f"   Severity: {result.severity or 'N/A'}")
            lines.append(f"   Snippet: {result.snippet[:100]}...")
            lines.append(f"   Source: {result.source_file} ({result.source_type})")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_json_display(self) -> str:
        """Format as JSON for programmatic use."""
        data = {
            'query': self.query,
            'results': [result.to_dict() for result in self.results],
            'provenance': self.provenance.to_dict(),
            'summary': {
                'total_results': len(self.results),
                'high_confidence_count': len(self.get_high_confidence_results()),
                'avg_confidence': sum(r.confidence_score for r in self.results) / len(self.results) if self.results else 0
            }
        }
        
        return json.dumps(data, indent=2)
    
    def _format_result_item(self, result: SearchMatch) -> str:
        """Format individual result item for display."""
        # Determine severity emoji
        severity_emoji = {
            'critical': '🚨',
            'high': '⚠️', 
            'medium': '📋',
            'low': '💡'
        }.get(result.severity, '📌')
        
        # Format result line
        line = f"{severity_emoji} **{result.source_rule_id}** [{result.confidence_score:.2f}]"
        
        if result.category:
            line += f" | {result.category}"
        
        # Add snippet on next line with proper indentation
        snippet = result.snippet[:150] + ("..." if len(result.snippet) > 150 else "")
        return f"{line}\n   └─ {snippet}"
    
    def merge_with_compiled_rules(self, compiled_results: List[Dict[str, Any]]) -> 'UnifiedResults':
        """Merge semantic search results with compiled rule matches."""
        return UnifiedResults(
            compiled_results=compiled_results,
            semantic_results=self.results,
            query=self.query,
            provenance=self.provenance
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'query': self.query,
            'results': [result.to_dict() for result in self.results],
            'provenance': self.provenance.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SemanticSearchResults':
        """Create from dictionary data."""
        results = [SearchMatch(**result) for result in data['results']]
        provenance_data = data['provenance']
        provenance_data['timestamp'] = datetime.fromisoformat(provenance_data['timestamp'])
        provenance = SearchProvenance(**provenance_data)
        
        return cls(data['query'], results, provenance)


class UnifiedResults:
    """Unified display of compiled rules and semantic search results."""
    
    def __init__(self, compiled_results: List[Dict[str, Any]], semantic_results: List[SearchMatch], 
                 query: str, provenance: SearchProvenance):
        self.compiled_results = compiled_results
        self.semantic_results = semantic_results
        self.query = query
        self.provenance = provenance
        
    def format_unified_display(self) -> str:
        """Format unified results showing both compiled and semantic matches."""
        lines = []
        
        # Header
        lines.append("🔍 **Unified Security Analysis Results**")
        lines.append(f"📝 Query/Context: {self.query}")
        lines.append("")
        
        # Compiled results (primary/deterministic)
        if self.compiled_results:
            lines.append("⚡ **Compiled Rule Matches (Primary):**")
            for result in self.compiled_results[:5]:  # Top 5 compiled
                rule_id = result.get('id', 'UNKNOWN')
                severity = result.get('severity', 'medium')
                title = result.get('title', 'Security Rule')
                
                severity_emoji = {
                    'critical': '🚨',
                    'high': '⚠️',
                    'medium': '📋', 
                    'low': '💡'
                }.get(severity, '📌')
                
                lines.append(f"{severity_emoji} **{rule_id}**: {title}")
                
            lines.append("")
        
        # Semantic results (supplementary/flexible)  
        if self.semantic_results:
            high_confidence = [r for r in self.semantic_results if r.confidence_score >= 0.7]
            
            if high_confidence:
                lines.append("🔍 **Semantic Search Supplements (High Confidence):**")
                for result in high_confidence[:3]:  # Top 3 semantic
                    lines.append(f"🎯 **{result.source_rule_id}** [{result.confidence_score:.2f}]")
                    lines.append(f"   └─ {result.snippet[:120]}...")
                    
                lines.append("")
        
        # Summary
        lines.append(f"📊 **Analysis Summary:**")
        lines.append(f"   • Compiled Rules: {len(self.compiled_results)} matches")
        lines.append(f"   • Semantic Results: {len(self.semantic_results)} matches")
        lines.append(f"   • Processing Time: {self.provenance.processing_time_ms}ms")
        
        return "\n".join(lines)
    
    def get_all_rule_ids(self) -> List[str]:
        """Get all rule IDs from both compiled and semantic results."""
        compiled_ids = [result.get('id', '') for result in self.compiled_results]
        semantic_ids = [result.source_rule_id for result in self.semantic_results]
        
        # Remove duplicates while preserving order
        all_ids = []
        for rule_id in compiled_ids + semantic_ids:
            if rule_id and rule_id not in all_ids:
                all_ids.append(rule_id)
                
        return all_ids
    
    def get_highest_severity(self) -> str:
        """Get highest severity from all results."""
        severity_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        max_severity = 'low'
        max_score = 0
        
        # Check compiled results
        for result in self.compiled_results:
            severity = result.get('severity', 'low')
            score = severity_order.get(severity, 0)
            if score > max_score:
                max_score = score
                max_severity = severity
        
        # Check semantic results
        for result in self.semantic_results:
            severity = result.severity or 'low'
            score = severity_order.get(severity, 0)
            if score > max_score:
                max_score = score
                max_severity = severity
        
        return max_severity


class SearchResultsAuditLogger:
    """Audit logging for semantic search results."""
    
    def __init__(self, log_file: str = "semantic_search_audit.log"):
        self.log_file = log_file
        self._setup_logger()
    
    def _setup_logger(self):
        """Set up audit logger with secure configuration."""
        self.audit_logger = logging.getLogger("semantic_search_audit")
        self.audit_logger.setLevel(logging.INFO)
        
        # File handler for audit trail
        if not self.audit_logger.handlers:
            handler = logging.FileHandler(self.log_file)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.audit_logger.addHandler(handler)
    
    def log_search_query(self, query: str, user_context: str = "unknown"):
        """Log search query for audit compliance."""
        self.audit_logger.info(f"SEARCH_QUERY | User: {user_context} | Query: {query}")
    
    def log_search_results(self, results: SemanticSearchResults):
        """Log search results summary for audit compliance."""
        self.audit_logger.info(
            f"SEARCH_RESULTS | Query: {results.query} | "
            f"Results: {len(results.results)} | "
            f"HighConf: {len(results.get_high_confidence_results())} | "
            f"ProcessingTime: {results.provenance.processing_time_ms}ms | "
            f"CorpusVersion: {results.provenance.corpus_version}"
        )
    
    def log_unified_analysis(self, unified: UnifiedResults):
        """Log unified analysis results for compliance tracking."""
        self.audit_logger.info(
            f"UNIFIED_ANALYSIS | Query: {unified.query} | "
            f"CompiledRules: {len(unified.compiled_results)} | "
            f"SemanticResults: {len(unified.semantic_results)} | "
            f"HighestSeverity: {unified.get_highest_severity()}"
        )