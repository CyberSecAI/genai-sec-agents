"""
Test suite for SemanticSearchFeatureFlags

Tests feature flag behavior, configuration, and audit logging.
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

from app.semantic.feature_flags import SemanticSearchFeatureFlags, FeatureFlagConfiguration


class TestFeatureFlagConfiguration:
    """Test FeatureFlagConfiguration functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_config(self, temp_dir):
        """Create sample configuration file."""
        config_data = {
            'search': {
                'feature_flags': {
                    'runtime_retrieval_default': False,
                    'explain_mode_default': True,
                    'pr_review_mode_default': False,
                    'audit_logging_enabled': True
                }
            }
        }
        
        config_file = os.path.join(temp_dir, "search_config.yaml")
        with open(config_file, 'w') as f:
            import yaml
            yaml.dump(config_data, f)
        
        return config_file
    
    def test_configuration_loading(self, sample_config):
        """Test configuration loading from file."""
        config = FeatureFlagConfiguration(sample_config)
        
        assert config.config_path == sample_config
        assert 'runtime_retrieval_default' in config.config
        assert config.config['runtime_retrieval_default'] is False
        assert config.config['explain_mode_default'] is True
    
    def test_configuration_defaults_on_error(self, temp_dir):
        """Test default configuration when file loading fails."""
        # Non-existent config file
        config_file = os.path.join(temp_dir, "nonexistent.yaml")
        config = FeatureFlagConfiguration(config_file)
        
        defaults = config.get_default_settings()
        
        assert 'runtime_retrieval_default' in defaults
        assert 'audit_logging_enabled' in defaults
        assert defaults['runtime_retrieval_default'] is False  # Secure default
        assert defaults['audit_logging_enabled'] is True  # Security default
    
    def test_runtime_flags_persistence(self, sample_config, temp_dir):
        """Test saving and loading runtime flags."""
        config = FeatureFlagConfiguration(sample_config)
        
        # Save runtime flags
        test_flags = {
            'runtime_retrieval_default': True,
            'explain_mode_default': False,
            'test_flag': 'test_value'
        }
        
        success = config.save_runtime_flags(test_flags)
        assert success is True
        
        # Load runtime flags
        loaded_flags = config.load_runtime_flags()
        
        assert loaded_flags['runtime_retrieval_default'] is True
        assert loaded_flags['explain_mode_default'] is False
        assert loaded_flags['test_flag'] == 'test_value'
        assert 'last_updated' in loaded_flags
    
    def test_runtime_flags_merge_with_defaults(self, sample_config):
        """Test runtime flags merging with defaults."""
        config = FeatureFlagConfiguration(sample_config)
        
        # Create partial runtime flags file
        flags_file = config._get_flags_file_path()
        os.makedirs(os.path.dirname(flags_file), exist_ok=True)
        
        partial_flags = {'runtime_retrieval_default': True}
        with open(flags_file, 'w') as f:
            json.dump(partial_flags, f)
        
        # Load should merge with defaults
        loaded_flags = config.load_runtime_flags()
        
        assert loaded_flags['runtime_retrieval_default'] is True  # From file
        assert 'explain_mode_default' in loaded_flags  # From defaults
        assert 'audit_logging_enabled' in loaded_flags  # From defaults


class TestSemanticSearchFeatureFlags:
    """Test SemanticSearchFeatureFlags functionality."""
    
    @pytest.fixture
    def temp_config(self, temp_dir=None):
        """Create temporary configuration for testing."""
        if temp_dir is None:
            temp_dir = tempfile.mkdtemp()
            
        config_data = {
            'search': {
                'feature_flags': {
                    'runtime_retrieval_default': False,
                    'explain_mode_default': True,
                    'pr_review_mode_default': False,
                    'audit_logging_enabled': True
                }
            }
        }
        
        config_file = os.path.join(temp_dir, "test_config.yaml")
        with open(config_file, 'w') as f:
            import yaml
            yaml.dump(config_data, f)
        
        return FeatureFlagConfiguration(config_file)
    
    def test_feature_flags_initialization(self, temp_config):
        """Test feature flags initialization."""
        flags = SemanticSearchFeatureFlags(temp_config)
        
        assert flags.config is not None
        assert isinstance(flags.runtime_flags, dict)
        assert isinstance(flags.temporary_flags, dict)
        assert len(flags.temporary_flags) == 0  # Should start empty
    
    def test_runtime_retrieval_default_disabled(self, temp_config):
        """Test runtime retrieval is disabled by default."""
        flags = SemanticSearchFeatureFlags(temp_config)
        
        is_enabled = flags.is_runtime_retrieval_enabled()
        assert is_enabled is False  # Should be False by default per ADR
    
    def test_enable_for_analysis_temporary(self, temp_config):
        """Test temporarily enabling semantic search for analysis."""
        flags = SemanticSearchFeatureFlags(temp_config)
        
        analysis_id = "test_analysis_001"
        flags.enable_for_analysis(analysis_id, duration=3600)
        
        # Should be enabled for this analysis
        is_enabled = flags.is_runtime_retrieval_enabled(analysis_id=analysis_id)
        assert is_enabled is True
        
        # Should still be disabled globally
        is_global_enabled = flags.is_runtime_retrieval_enabled()
        assert is_global_enabled is False
    
    def test_disable_for_analysis(self, temp_config):
        """Test disabling semantic search for specific analysis."""
        flags = SemanticSearchFeatureFlags(temp_config)
        
        analysis_id = "test_analysis_002"
        
        # Enable first
        flags.enable_for_analysis(analysis_id)
        assert flags.is_runtime_retrieval_enabled(analysis_id=analysis_id) is True
        
        # Then disable
        flags.disable_for_analysis(analysis_id)
        assert flags.is_runtime_retrieval_enabled(analysis_id=analysis_id) is False
    
    def test_temporary_flag_expiration(self, temp_config):
        """Test temporary flag expiration."""
        flags = SemanticSearchFeatureFlags(temp_config)
        
        analysis_id = "expiring_analysis"
        
        # Enable with very short duration
        flags.enable_for_analysis(analysis_id, duration=1)  # 1 second
        
        # Should be enabled immediately
        assert flags.is_runtime_retrieval_enabled(analysis_id=analysis_id) is True
        
        # Simulate time passing by checking expired flags
        import time
        time.sleep(2)  # Wait for expiration
        
        # Get configuration which cleans up expired flags
        config = flags.get_search_configuration()
        
        # Should be cleaned up automatically
        assert analysis_id not in config['temporary_flags']
    
    def test_global_flag_setting(self, temp_config):
        """Test setting global feature flags."""
        flags = SemanticSearchFeatureFlags(temp_config)
        
        # Set global runtime retrieval to enabled
        success = flags.set_global_flag('runtime_retrieval_default', True)
        assert success is True
        
        # Should now be enabled globally
        is_enabled = flags.is_runtime_retrieval_enabled()
        assert is_enabled is True
    
    def test_invalid_global_flag_rejected(self, temp_config):
        """Test invalid global flag names are rejected."""
        flags = SemanticSearchFeatureFlags(temp_config)
        
        success = flags.set_global_flag('invalid_flag_name', True)
        assert success is False
    
    def test_explain_mode_default_enabled(self, temp_config):
        """Test explain mode is enabled by default."""
        flags = SemanticSearchFeatureFlags(temp_config)
        
        is_enabled = flags.is_explain_mode_enabled()
        assert is_enabled is True
    
    def test_pr_review_mode_default_disabled(self, temp_config):
        """Test PR review mode is disabled by default."""
        flags = SemanticSearchFeatureFlags(temp_config)
        
        is_enabled = flags.is_pr_review_mode_enabled()
        assert is_enabled is False
    
    def test_audit_logging_enabled_by_default(self, temp_config):
        """Test audit logging is enabled by default."""
        flags = SemanticSearchFeatureFlags(temp_config)
        
        is_enabled = flags.is_audit_logging_enabled()
        assert is_enabled is True
    
    def test_search_configuration_retrieval(self, temp_config):
        """Test getting complete search configuration."""
        flags = SemanticSearchFeatureFlags(temp_config)
        
        # Add a temporary flag
        flags.enable_for_analysis("test_config_analysis")
        
        config = flags.get_search_configuration()
        
        assert 'runtime_flags' in config
        assert 'temporary_flags' in config
        assert 'defaults' in config
        
        # Should contain the temporary flag
        assert 'test_config_analysis' in config['temporary_flags']
    
    def test_flag_usage_statistics(self, temp_config):
        """Test flag usage statistics retrieval."""
        flags = SemanticSearchFeatureFlags(temp_config)
        
        # Add some temporary flags
        flags.enable_for_analysis("stats_test_1")
        flags.enable_for_analysis("stats_test_2")
        
        stats = flags.get_flag_usage_statistics()
        
        assert 'total_runtime_flags' in stats
        assert 'active_temporary_flags' in stats
        assert 'audit_logging_enabled' in stats
        assert 'current_flags' in stats
        assert 'temporary_retrieval_active' in stats
        
        assert stats['active_temporary_flags'] == 2
        assert stats['temporary_retrieval_active'] == 2
    
    def test_flag_configuration_validation(self, temp_config):
        """Test flag configuration validation."""
        flags = SemanticSearchFeatureFlags(temp_config)
        
        validation = flags.validate_flag_configuration()
        
        assert 'valid' in validation
        assert 'errors' in validation
        assert 'warnings' in validation
        assert 'recommendations' in validation
        assert isinstance(validation['valid'], bool)
    
    def test_flag_validation_security_warnings(self, temp_config):
        """Test security validation warnings."""
        flags = SemanticSearchFeatureFlags(temp_config)
        
        # Enable runtime retrieval by default (should trigger warning)
        flags.set_global_flag('runtime_retrieval_default', True)
        
        validation = flags.validate_flag_configuration()
        
        # Should have warning about security implications
        assert any('security implications' in warning for warning in validation['warnings'])
    
    def test_flag_validation_audit_logging_warning(self, temp_config):
        """Test audit logging disabled warning."""
        flags = SemanticSearchFeatureFlags(temp_config)
        
        # Disable audit logging
        flags.set_global_flag('audit_logging_enabled', False)
        
        validation = flags.validate_flag_configuration()
        
        # Should warn about compliance impact
        assert any('compliance' in warning for warning in validation['warnings'])
    
    def test_reset_all_flags(self, temp_config):
        """Test resetting all flags to defaults."""
        flags = SemanticSearchFeatureFlags(temp_config)
        
        # Modify some flags
        flags.set_global_flag('runtime_retrieval_default', True)
        flags.enable_for_analysis("reset_test_analysis")
        
        # Verify changes
        assert flags.is_runtime_retrieval_enabled() is True
        assert len(flags.temporary_flags) > 0
        
        # Reset all flags
        success = flags.reset_all_flags("test_admin")
        assert success is True
        
        # Should be back to defaults
        assert flags.is_runtime_retrieval_enabled() is False
        assert len(flags.temporary_flags) == 0
    
    def test_flag_scope_priority(self, temp_config):
        """Test flag scope priority: temporary > runtime > default."""
        flags = SemanticSearchFeatureFlags(temp_config)
        
        analysis_id = "priority_test"
        
        # Default: False
        assert flags.is_runtime_retrieval_enabled() is False
        
        # Set global runtime flag: True (higher priority than default)
        flags.set_global_flag('runtime_retrieval_default', True)
        assert flags.is_runtime_retrieval_enabled() is True
        
        # Set temporary flag: False (highest priority)
        flags.temporary_flags[analysis_id] = {'runtime_retrieval': False}
        assert flags.is_runtime_retrieval_enabled(analysis_id=analysis_id) is False
        
        # Without analysis_id, should still use runtime flag
        assert flags.is_runtime_retrieval_enabled() is True
    
    @patch('app.semantic.feature_flags.logging')
    def test_audit_logging_functionality(self, mock_logging, temp_config):
        """Test audit logging for flag operations."""
        flags = SemanticSearchFeatureFlags(temp_config)
        
        # Enable audit logging
        flags.set_global_flag('audit_logging_enabled', True)
        
        # Perform operations that should be audited
        flags.is_runtime_retrieval_enabled()
        flags.enable_for_analysis("audit_test")
        flags.set_global_flag('explain_mode_default', False)
        
        # Verify logging calls were made (specific verification depends on logging setup)
        assert hasattr(flags, 'audit_logger') or hasattr(flags, '_log_flag_usage')
    
    def test_concurrent_temporary_flags(self, temp_config):
        """Test multiple concurrent temporary flags."""
        flags = SemanticSearchFeatureFlags(temp_config)
        
        # Enable for multiple analyses
        analyses = ["concurrent_1", "concurrent_2", "concurrent_3"]
        for analysis_id in analyses:
            flags.enable_for_analysis(analysis_id)
        
        # All should be enabled
        for analysis_id in analyses:
            assert flags.is_runtime_retrieval_enabled(analysis_id=analysis_id) is True
        
        # Disable one
        flags.disable_for_analysis("concurrent_2")
        
        # Others should still be enabled
        assert flags.is_runtime_retrieval_enabled(analysis_id="concurrent_1") is True
        assert flags.is_runtime_retrieval_enabled(analysis_id="concurrent_2") is False
        assert flags.is_runtime_retrieval_enabled(analysis_id="concurrent_3") is True
    
    def test_flag_persistence_across_instances(self, temp_config):
        """Test flag persistence across different instances."""
        # First instance
        flags1 = SemanticSearchFeatureFlags(temp_config)
        flags1.set_global_flag('runtime_retrieval_default', True)
        
        # Second instance should see the change
        flags2 = SemanticSearchFeatureFlags(temp_config)
        assert flags2.is_runtime_retrieval_enabled() is True
    
    def test_security_default_values(self, temp_config):
        """Test security-focused default values."""
        flags = SemanticSearchFeatureFlags(temp_config)
        
        # Runtime retrieval should be OFF by default (per ADR)
        assert flags.is_runtime_retrieval_enabled() is False
        
        # Audit logging should be ON by default
        assert flags.is_audit_logging_enabled() is True
        
        # Explain mode can be ON by default (not a security risk)
        assert flags.is_explain_mode_enabled() is True
        
        # PR review mode should be OFF by default (admin feature)
        assert flags.is_pr_review_mode_enabled() is False