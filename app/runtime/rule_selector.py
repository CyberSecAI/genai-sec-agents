"""
Rule Selector for Context-Aware Rule Filtering

Provides intelligent rule selection based on development context
to deliver relevant security guidance.

Security Features:
- Prevents unauthorized rule access
- Validates all context inputs
- Implements secure pattern matching
"""

import re
import logging
from typing import Dict, List, Optional, Set
from pathlib import Path


class RuleSelectorError(Exception):
    """Exception for rule selection errors"""
    pass


class RuleSelector:
    """
    Context-aware rule selector for filtering relevant security rules.
    
    Implements intelligent filtering based on file type, directory patterns,
    and content analysis to provide focused security guidance.
    """
    
    def __init__(self):
        """Initialize the rule selector with pattern mappings."""
        self.logger = logging.getLogger(__name__)
        
        # File extension to scope mappings
        self.extension_mapping = {
            '.py': ['python', 'backend', 'api'],
            '.js': ['javascript', 'frontend', 'web'],
            '.ts': ['typescript', 'frontend', 'web'],  
            '.java': ['java', 'backend', 'api'],
            '.go': ['golang', 'backend', 'api'],
            '.rs': ['rust', 'backend', 'system'],
            '.dockerfile': ['docker', 'container', 'deployment'],
            '.yaml': ['config', 'deployment', 'infrastructure'],
            '.yml': ['config', 'deployment', 'infrastructure'],
            '.json': ['config', 'data', 'api'],
            '.sql': ['database', 'backend', 'data'],
            '.tf': ['terraform', 'infrastructure', 'cloud'],
        }
        
        # Directory patterns to scope mappings
        self.directory_patterns = {
            r'src/': ['source', 'application'],
            r'test/': ['testing', 'validation'],
            r'tests/': ['testing', 'validation'],
            r'config/': ['configuration', 'settings'],
            r'docker/': ['container', 'deployment'],
            r'deploy/': ['deployment', 'infrastructure'],
            r'api/': ['api', 'backend'],
            r'web/': ['web', 'frontend'],
            r'auth/': ['authentication', 'security'],
            r'admin/': ['administration', 'privileged'],
        }
        
        # Content patterns for advanced matching
        self.content_patterns = {
            'secrets': [
                r'password\s*=',
                r'secret\s*=', 
                r'api[_-]?key',
                r'private[_-]?key',
                r'jwt[_-]?secret',
                r'token\s*=',
            ],
            'authentication': [
                r'login\s*\(',
                r'authenticate',
                r'session\s*\[',
                r'cookie\s*\[',
                r'auth\s*=',
            ],
            'database': [
                r'SELECT\s+',
                r'INSERT\s+',
                r'UPDATE\s+',
                r'DELETE\s+',
                r'cursor\.',
                r'execute\s*\(',
            ],
            'web': [
                r'request\.',
                r'response\.',
                r'http\s*=',
                r'url\s*=',
                r'render\s*\(',
            ],
            'container': [
                r'FROM\s+',
                r'RUN\s+',
                r'COPY\s+',
                r'EXPOSE\s+',
                r'docker\s',
            ],
        }
    
    def select_rules(self, context: Dict, rules: List[Dict], max_rules: int = 10) -> List[Dict]:
        """
        Select relevant rules based on development context.
        
        Args:
            context: Development context (file_path, content, etc.)
            rules: Available rules to filter from
            max_rules: Maximum number of rules to return
            
        Returns:
            List of relevant rules, ordered by relevance
            
        Raises:
            RuleSelectorError: If context or rules are invalid
        """
        try:
            # Validate inputs
            self._validate_inputs(context, rules)
            
            # Analyze context to determine relevant scopes
            relevant_scopes = self._analyze_context(context)
            
            # Score and filter rules
            scored_rules = self._score_rules(rules, relevant_scopes, context)
            
            # Sort by relevance score and limit results
            scored_rules.sort(key=lambda x: x['score'], reverse=True)
            selected_rules = scored_rules[:max_rules]
            
            # Remove scoring metadata and return clean rules
            result = [rule['rule'] for rule in selected_rules if rule['score'] > 0]
            
            self.logger.info(f"Selected {len(result)} rules from {len(rules)} available")
            return result
            
        except Exception as e:
            self.logger.error(f"Error selecting rules: {e}")
            raise RuleSelectorError(f"Rule selection failed: {e}")
    
    def _validate_inputs(self, context: Dict, rules: List[Dict]) -> None:
        """
        Validate context and rules inputs.
        
        Args:
            context: Context to validate
            rules: Rules list to validate
            
        Raises:
            RuleSelectorError: If inputs are invalid
        """
        if not isinstance(context, dict):
            raise RuleSelectorError("Context must be a dictionary")
        
        if not isinstance(rules, list):
            raise RuleSelectorError("Rules must be a list")
        
        if len(rules) > 1000:  # Prevent DoS
            raise RuleSelectorError("Too many rules provided")
        
        # Validate rule structure
        for i, rule in enumerate(rules):
            if not isinstance(rule, dict):
                raise RuleSelectorError(f"Rule at index {i} is not a dictionary")
            
            if 'id' not in rule or 'scope' not in rule:
                raise RuleSelectorError(f"Rule at index {i} missing required fields")
    
    def _analyze_context(self, context: Dict) -> Set[str]:
        """
        Analyze context to determine relevant scopes and domains.
        
        Args:
            context: Development context
            
        Returns:
            Set of relevant scope tags
        """
        relevant_scopes = set()
        
        # Analyze file path
        file_path = context.get('file_path', '')
        if file_path:
            relevant_scopes.update(self._analyze_file_path(file_path))
        
        # Analyze file content
        content = context.get('content', '')
        if content:
            relevant_scopes.update(self._analyze_content(content))
        
        # Add explicit context hints
        if 'language' in context:
            relevant_scopes.add(context['language'].lower())
        
        if 'framework' in context:
            relevant_scopes.add(context['framework'].lower())
        
        if 'domain' in context:
            relevant_scopes.add(context['domain'].lower())
        
        return relevant_scopes
    
    def _analyze_file_path(self, file_path: str) -> Set[str]:
        """
        Extract scope information from file path.
        
        Args:
            file_path: File path to analyze
            
        Returns:
            Set of relevant scopes
        """
        scopes = set()
        
        try:
            # Get file extension
            path_obj = Path(file_path)
            extension = path_obj.suffix.lower()
            
            if extension in self.extension_mapping:
                scopes.update(self.extension_mapping[extension])
            
            # Check directory patterns
            path_str = str(path_obj).lower()
            for pattern, pattern_scopes in self.directory_patterns.items():
                if re.search(pattern, path_str):
                    scopes.update(pattern_scopes)
        
        except Exception as e:
            self.logger.warning(f"Error analyzing file path: {e}")
        
        return scopes
    
    def _analyze_content(self, content: str) -> Set[str]:
        """
        Extract scope information from file content.
        
        Args:
            content: File content to analyze
            
        Returns:
            Set of relevant scopes
        """
        scopes = set()
        
        try:
            # Limit content size for analysis
            analysis_content = content[:10000].lower()
            
            # Check content patterns
            for domain, patterns in self.content_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, analysis_content, re.IGNORECASE):
                        scopes.add(domain)
                        break  # Don't need multiple matches per domain
        
        except Exception as e:
            self.logger.warning(f"Error analyzing content: {e}")
        
        return scopes
    
    def _score_rules(self, rules: List[Dict], relevant_scopes: Set[str], context: Dict) -> List[Dict]:
        """
        Score rules based on relevance to context.
        
        Args:
            rules: Rules to score
            relevant_scopes: Relevant scope tags
            context: Original context
            
        Returns:
            List of rules with relevance scores
        """
        scored_rules = []
        
        for rule in rules:
            score = self._calculate_rule_score(rule, relevant_scopes, context)
            scored_rules.append({
                'rule': rule,
                'score': score
            })
        
        return scored_rules
    
    def _calculate_rule_score(self, rule: Dict, relevant_scopes: Set[str], context: Dict) -> float:
        """
        Calculate relevance score for a single rule.
        
        Args:
            rule: Rule to score
            relevant_scopes: Relevant context scopes
            context: Original context
            
        Returns:
            Relevance score (0.0 to 1.0)
        """
        score = 0.0
        
        try:
            # Base scope matching
            rule_scope = rule.get('scope', '').lower()
            rule_scopes = set(re.split(r'[,\s:]+', rule_scope))
            
            # Calculate scope overlap
            scope_overlap = len(relevant_scopes.intersection(rule_scopes))
            if scope_overlap > 0:
                score += 0.5 + (scope_overlap * 0.1)
            
            # Severity boost
            severity = rule.get('severity', 'medium')
            severity_boost = {
                'critical': 0.3,
                'high': 0.2,
                'medium': 0.1,
                'low': 0.05
            }.get(severity, 0.1)
            score += severity_boost
            
            # Content-specific matching
            content = context.get('content', '').lower()
            if content:
                # Check if rule keywords appear in content
                rule_text = f"{rule.get('title', '')} {rule.get('requirement', '')}".lower()
                
                # Simple keyword matching
                common_words = set(re.findall(r'\b\w{4,}\b', rule_text))
                content_words = set(re.findall(r'\b\w{4,}\b', content[:1000]))
                
                keyword_overlap = len(common_words.intersection(content_words))
                if keyword_overlap > 0:
                    score += keyword_overlap * 0.05
        
        except Exception as e:
            self.logger.warning(f"Error calculating rule score: {e}")
        
        # Ensure score is within bounds
        return min(1.0, max(0.0, score))
    
    def get_scope_analysis(self, context: Dict) -> Dict:
        """
        Get detailed scope analysis for debugging.
        
        Args:
            context: Development context
            
        Returns:
            Analysis results
        """
        try:
            relevant_scopes = self._analyze_context(context)
            
            return {
                'relevant_scopes': sorted(list(relevant_scopes)),
                'file_path_analysis': self._analyze_file_path(context.get('file_path', '')),
                'content_analysis': self._analyze_content(context.get('content', ''))
            }
        
        except Exception as e:
            self.logger.error(f"Error in scope analysis: {e}")
            return {'error': str(e)}