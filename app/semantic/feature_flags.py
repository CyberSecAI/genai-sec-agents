"""
Feature Flags for Semantic Search

Manages feature flag configuration for semantic search capabilities.
Controls runtime retrieval behavior with security and audit logging.
"""

import os
import json
import time
import yaml
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class FeatureFlagConfiguration:
    """Configuration for semantic search feature flags."""
    
    def __init__(self, config_path: str = "app/semantic/config/search_config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.flags_file = self._get_flags_file_path()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load feature flag configuration."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
            return config.get('search', {}).get('feature_flags', {})
            
        except Exception as e:
            logger.error(f"Failed to load feature flag config: {e}")
            return {
                'runtime_retrieval_default': False,
                'explain_mode_default': True,
                'pr_review_mode_default': False,
                'audit_logging_enabled': True
            }
    
    def _get_flags_file_path(self) -> str:
        """Get runtime flags file path."""
        flags_dir = os.path.dirname(self.config_path)
        return os.path.join(flags_dir, "runtime_flags.json")
    
    def get_default_settings(self) -> Dict[str, Any]:
        """Get default feature flag settings."""
        return {
            'runtime_retrieval_default': self.config.get('runtime_retrieval_default', False),
            'explain_mode_default': self.config.get('explain_mode_default', True),
            'pr_review_mode_default': self.config.get('pr_review_mode_default', False),
            'audit_logging_enabled': self.config.get('audit_logging_enabled', True)
        }
    
    def save_runtime_flags(self, flags: Dict[str, Any]) -> bool:
        """Save runtime flags to persistent storage."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.flags_file), exist_ok=True)
            
            # Add timestamp
            flags['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            with open(self.flags_file, 'w', encoding='utf-8') as f:
                json.dump(flags, f, indent=2)
                
            logger.info(f"Runtime flags saved to {self.flags_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save runtime flags: {e}")
            return False
    
    def load_runtime_flags(self) -> Dict[str, Any]:
        """Load runtime flags from persistent storage."""
        try:
            if not os.path.exists(self.flags_file):
                return self.get_default_settings()
                
            with open(self.flags_file, 'r', encoding='utf-8') as f:
                flags = json.load(f)
                
            # Merge with defaults for missing keys
            defaults = self.get_default_settings()
            for key, value in defaults.items():
                if key not in flags:
                    flags[key] = value
                    
            return flags
            
        except Exception as e:
            logger.error(f"Failed to load runtime flags: {e}")
            return self.get_default_settings()


class SemanticSearchFeatureFlags:
    """Feature flag management for semantic search capabilities."""
    
    def __init__(self, config: Optional[FeatureFlagConfiguration] = None):
        """Initialize feature flags with configuration."""
        self.config = config or FeatureFlagConfiguration()
        self.runtime_flags = self.config.load_runtime_flags()
        self.temporary_flags = {}  # Temporary per-analysis flags
        self.audit_log = []
        
        # Initialize audit logging if enabled
        if self.runtime_flags.get('audit_logging_enabled', True):
            self._setup_audit_logging()
    
    def _setup_audit_logging(self):
        """Set up audit logging for feature flag usage."""
        self.audit_logger = logging.getLogger("semantic_search_flags")
        self.audit_logger.setLevel(logging.INFO)
        
        # Create audit log handler if not exists
        if not self.audit_logger.handlers:
            log_file = "semantic_flags_audit.log"
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.audit_logger.addHandler(handler)
    
    def _log_flag_usage(self, flag_name: str, value: Any, scope: str, user_context: str = "system"):
        """Log feature flag usage for audit compliance."""
        if hasattr(self, 'audit_logger'):
            self.audit_logger.info(
                f"FLAG_USAGE | Flag: {flag_name} | Value: {value} | "
                f"Scope: {scope} | User: {user_context} | Timestamp: {datetime.now(timezone.utc).isoformat()}"
            )
    
    @staticmethod
    def is_runtime_retrieval_enabled(scope: str = "global", analysis_id: str = None) -> bool:
        """Check if runtime retrieval is enabled for given scope."""
        instance = SemanticSearchFeatureFlags()
        
        # Check temporary flags first (highest priority)
        if analysis_id and analysis_id in instance.temporary_flags:
            temp_flags = instance.temporary_flags[analysis_id]
            if 'runtime_retrieval' in temp_flags:
                enabled = temp_flags['runtime_retrieval']
                instance._log_flag_usage('runtime_retrieval', enabled, f"temporary:{analysis_id}")
                return enabled
        
        # Check runtime flags (medium priority)
        if scope in instance.runtime_flags:
            enabled = instance.runtime_flags[scope]
            instance._log_flag_usage('runtime_retrieval', enabled, f"runtime:{scope}")
            return enabled
        
        # Fall back to global default (lowest priority)
        enabled = instance.runtime_flags.get('runtime_retrieval_default', False)
        instance._log_flag_usage('runtime_retrieval', enabled, "global_default")
        return enabled
    
    @staticmethod
    def enable_for_analysis(analysis_id: str, duration: int = 3600, user_context: str = "system") -> None:
        """Temporarily enable semantic search for specific analysis."""
        instance = SemanticSearchFeatureFlags()
        
        if analysis_id not in instance.temporary_flags:
            instance.temporary_flags[analysis_id] = {}
        
        # Set temporary flag with expiration
        instance.temporary_flags[analysis_id].update({
            'runtime_retrieval': True,
            'enabled_at': datetime.now(timezone.utc).isoformat(),
            'expires_at': (datetime.now(timezone.utc) + timedelta(seconds=duration)).isoformat(),
            'enabled_by': user_context
        })
        
        instance._log_flag_usage('runtime_retrieval', True, f"temporary:{analysis_id}:{duration}s", user_context)
        logger.info(f"Semantic search enabled for analysis {analysis_id} for {duration} seconds")
    
    @staticmethod
    def disable_for_analysis(analysis_id: str, user_context: str = "system") -> None:
        """Disable semantic search for specific analysis."""
        instance = SemanticSearchFeatureFlags()
        
        if analysis_id in instance.temporary_flags:
            del instance.temporary_flags[analysis_id]
            
        instance._log_flag_usage('runtime_retrieval', False, f"temporary:{analysis_id}", user_context)
        logger.info(f"Semantic search disabled for analysis {analysis_id}")
    
    @staticmethod
    def set_global_flag(flag_name: str, value: Any, user_context: str = "system") -> bool:
        """Set global feature flag value."""
        instance = SemanticSearchFeatureFlags()
        
        # Validate flag name
        valid_flags = [
            'runtime_retrieval_default',
            'explain_mode_default',
            'pr_review_mode_default',
            'audit_logging_enabled'
        ]
        
        if flag_name not in valid_flags:
            logger.error(f"Invalid flag name: {flag_name}")
            return False
        
        # Update runtime flags
        instance.runtime_flags[flag_name] = value
        
        # Persist to storage
        if instance.config.save_runtime_flags(instance.runtime_flags):
            instance._log_flag_usage(flag_name, value, "global", user_context)
            logger.info(f"Global flag {flag_name} set to {value}")
            return True
        
        return False
    
    @staticmethod
    def get_search_configuration() -> Dict[str, Any]:
        """Get current search behavior configuration."""
        instance = SemanticSearchFeatureFlags()
        
        config = {
            'runtime_flags': instance.runtime_flags.copy(),
            'temporary_flags': instance.temporary_flags.copy(),
            'defaults': instance.config.get_default_settings()
        }
        
        # Clean expired temporary flags
        current_time = datetime.now(timezone.utc)
        expired_analyses = []
        
        for analysis_id, flags in instance.temporary_flags.items():
            if 'expires_at' in flags:
                expires_at = datetime.fromisoformat(flags['expires_at'])
                if current_time > expires_at:
                    expired_analyses.append(analysis_id)
        
        # Remove expired flags
        for analysis_id in expired_analyses:
            del instance.temporary_flags[analysis_id]
            logger.info(f"Expired temporary flags for analysis {analysis_id}")
        
        return config
    
    @staticmethod
    def is_explain_mode_enabled(scope: str = "global") -> bool:
        """Check if explain mode is enabled."""
        instance = SemanticSearchFeatureFlags()
        
        enabled = instance.runtime_flags.get('explain_mode_default', True)
        instance._log_flag_usage('explain_mode', enabled, scope)
        return enabled
    
    @staticmethod
    def is_pr_review_mode_enabled(scope: str = "global") -> bool:
        """Check if PR review mode is enabled."""
        instance = SemanticSearchFeatureFlags()
        
        enabled = instance.runtime_flags.get('pr_review_mode_default', False)
        instance._log_flag_usage('pr_review_mode', enabled, scope)
        return enabled
    
    @staticmethod
    def is_audit_logging_enabled() -> bool:
        """Check if audit logging is enabled."""
        instance = SemanticSearchFeatureFlags()
        return instance.runtime_flags.get('audit_logging_enabled', True)
    
    def get_flag_usage_statistics(self) -> Dict[str, Any]:
        """Get feature flag usage statistics."""
        stats = {
            'total_runtime_flags': len(self.runtime_flags),
            'active_temporary_flags': len(self.temporary_flags),
            'audit_logging_enabled': self.is_audit_logging_enabled(),
            'default_settings': self.config.get_default_settings(),
            'current_flags': {
                'runtime_retrieval_default': self.runtime_flags.get('runtime_retrieval_default', False),
                'explain_mode_default': self.runtime_flags.get('explain_mode_default', True),
                'pr_review_mode_default': self.runtime_flags.get('pr_review_mode_default', False)
            }
        }
        
        # Count temporary flags by type
        temp_retrieval_count = 0
        for flags in self.temporary_flags.values():
            if flags.get('runtime_retrieval', False):
                temp_retrieval_count += 1
        
        stats['temporary_retrieval_active'] = temp_retrieval_count
        
        return stats
    
    @staticmethod
    def reset_all_flags(user_context: str = "system") -> bool:
        """Reset all flags to default values (admin function)."""
        instance = SemanticSearchFeatureFlags()
        
        # Clear temporary flags
        instance.temporary_flags.clear()
        
        # Reset runtime flags to defaults
        instance.runtime_flags = instance.config.get_default_settings()
        
        # Persist changes
        if instance.config.save_runtime_flags(instance.runtime_flags):
            instance._log_flag_usage('ALL_FLAGS', 'RESET', 'global', user_context)
            logger.warning(f"All semantic search flags reset to defaults by {user_context}")
            return True
        
        return False
    
    @staticmethod
    def validate_flag_configuration() -> Dict[str, Any]:
        """Validate current flag configuration for security and consistency."""
        instance = SemanticSearchFeatureFlags()
        
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Check if runtime retrieval is enabled by default (security consideration)
        if instance.runtime_flags.get('runtime_retrieval_default', False):
            validation_result['warnings'].append(
                "Runtime retrieval is enabled by default - consider security implications"
            )
        
        # Check for excessive temporary flags
        if len(instance.temporary_flags) > 10:
            validation_result['warnings'].append(
                f"High number of temporary flags active ({len(instance.temporary_flags)}) - consider cleanup"
            )
        
        # Validate audit logging is enabled
        if not instance.runtime_flags.get('audit_logging_enabled', True):
            validation_result['warnings'].append(
                "Audit logging is disabled - security compliance may be affected"
            )
        
        # Check for expired temporary flags
        current_time = datetime.now(timezone.utc)
        expired_count = 0
        
        for flags in instance.temporary_flags.values():
            if 'expires_at' in flags:
                expires_at = datetime.fromisoformat(flags['expires_at'])
                if current_time > expires_at:
                    expired_count += 1
        
        if expired_count > 0:
            validation_result['recommendations'].append(
                f"Clean up {expired_count} expired temporary flags"
            )
        
        # Overall validation status
        if validation_result['errors']:
            validation_result['valid'] = False
        
        return validation_result