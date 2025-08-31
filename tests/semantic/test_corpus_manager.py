"""
Test suite for CorpusManager

Tests corpus rendering, validation, and security features.
"""

import os
import json
import yaml
import tempfile
import shutil
from pathlib import Path
import pytest

from app.semantic.corpus_manager import CorpusManager, CorpusData, CorpusMetadata, ValidationResult


class TestCorpusManager:
    """Test CorpusManager functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_config(self, temp_dir):
        """Create sample configuration for testing."""
        config_data = {
            'corpus': {
                'sources': {
                    'compiled_agent_packages': f"{temp_dir}/packages/*.json",
                    'rule_cards': f"{temp_dir}/rule_cards/**/*.yml"
                },
                'output': {
                    'format': 'semtools_v1',
                    'path': f"{temp_dir}/corpus/",
                    'max_size_mb': 100
                },
                'versioning': {
                    'track_sources': True,
                    'auto_update': False,
                    'freshness_check': True
                },
                'security': {
                    'sanitize_inputs': True,
                    'validate_paths': True,
                    'prevent_traversal': True
                }
            }
        }
        
        config_path = os.path.join(temp_dir, "corpus_config.yaml")
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
            
        return config_path
    
    @pytest.fixture
    def sample_agent_package(self, temp_dir):
        """Create sample agent package for testing."""
        package_data = {
            'agent_id': 'test-agent',
            'version': '1.0.0',
            'rules_detail': [
                {
                    'id': 'TEST-001',
                    'title': 'Test Security Rule',
                    'severity': 'high',
                    'scope': 'application',
                    'requirement': 'Test security requirement',
                    'do': ['Follow secure practices'],
                    'dont': ['Avoid insecure patterns'],
                    'detect': {
                        'semgrep': ['test-rule-001']
                    },
                    'refs': {
                        'cwe': ['CWE-123'],
                        'asvs': ['V1.1.1']
                    }
                }
            ]
        }
        
        packages_dir = os.path.join(temp_dir, "packages")
        os.makedirs(packages_dir, exist_ok=True)
        
        package_path = os.path.join(packages_dir, "test-agent.json")
        with open(package_path, 'w') as f:
            json.dump(package_data, f)
            
        return package_path
    
    @pytest.fixture
    def sample_rule_card(self, temp_dir):
        """Create sample rule card YAML for testing."""
        rule_data = {
            'id': 'YAML-001',
            'title': 'YAML Rule Card',
            'severity': 'medium',
            'scope': 'web',
            'requirement': 'YAML security requirement',
            'do': ['Use secure YAML practices'],
            'dont': ['Avoid YAML vulnerabilities'],
            'detect': {
                'custom': ['yaml-rule-001']
            },
            'refs': {
                'cwe': ['CWE-456'],
                'owasp': ['A01:2021']
            }
        }
        
        rule_cards_dir = os.path.join(temp_dir, "rule_cards")
        os.makedirs(rule_cards_dir, exist_ok=True)
        
        rule_path = os.path.join(rule_cards_dir, "test-rule.yml")
        with open(rule_path, 'w') as f:
            yaml.dump(rule_data, f)
            
        return rule_path
    
    def test_corpus_manager_initialization(self, sample_config):
        """Test CorpusManager initialization with configuration."""
        manager = CorpusManager(sample_config)
        
        assert manager.config_path == sample_config
        assert 'corpus' in manager.config
        assert manager.max_size_mb == 100
        assert os.path.exists(manager.corpus_path)
    
    def test_path_sanitization_security(self, sample_config):
        """Test path sanitization prevents directory traversal."""
        manager = CorpusManager(sample_config)
        
        # Test legitimate path
        legitimate_path = "app/test.json"
        sanitized = manager._sanitize_path(legitimate_path)
        assert legitimate_path in sanitized
        
        # Test directory traversal attempt
        with pytest.raises(ValueError, match="Path traversal detected"):
            manager._sanitize_path("../../etc/passwd")
    
    def test_rule_extraction_from_package(self, sample_config, sample_agent_package):
        """Test rule extraction from agent package."""
        manager = CorpusManager(sample_config)
        rules = manager._extract_rules_from_package(sample_agent_package)
        
        assert len(rules) == 1
        assert rules[0]['id'] == 'TEST-001'
        assert rules[0]['title'] == 'Test Security Rule'
        assert rules[0]['severity'] == 'high'
    
    def test_rule_extraction_from_yaml(self, sample_config, sample_rule_card):
        """Test rule extraction from YAML file."""
        manager = CorpusManager(sample_config)
        rule = manager._extract_rules_from_yaml(sample_rule_card)
        
        assert rule['id'] == 'YAML-001'
        assert rule['title'] == 'YAML Rule Card'
        assert rule['severity'] == 'medium'
        assert rule['_source_file'] == sample_rule_card
        assert rule['_source_type'] == 'yaml'
    
    def test_rule_formatting_for_corpus(self, sample_config):
        """Test rule formatting for corpus inclusion."""
        manager = CorpusManager(sample_config)
        
        rule = {
            'id': 'FORMAT-001',
            'title': 'Format Test Rule',
            'severity': 'high',
            'scope': 'test',
            'requirement': 'Test formatting requirement',
            'do': ['Do this', 'Do that'],
            'dont': ['Dont do this'],
            'detect': {
                'semgrep': ['format-rule-001'],
                'custom': ['format-custom-001']
            },
            'refs': {
                'cwe': ['CWE-123'],
                'asvs': ['V1.1.1'],
                'owasp': ['A01:2021']
            },
            '_source_file': 'test.json',
            '_source_type': 'compiled'
        }
        
        formatted = manager._format_rule_for_corpus(rule)
        
        assert 'Rule ID: FORMAT-001' in formatted
        assert 'Title: Format Test Rule' in formatted
        assert 'Severity: high' in formatted
        assert 'Secure Practices:' in formatted
        assert '• Do this' in formatted
        assert '• Do that' in formatted
        assert 'Avoid These Patterns:' in formatted
        assert '• Dont do this' in formatted
        assert 'Detection Methods:' in formatted
        assert 'semgrep: format-rule-001' in formatted
        assert 'CWE: CWE-123' in formatted
        assert 'ASVS: V1.1.1' in formatted
        assert 'OWASP: A01:2021' in formatted
        assert 'Source: test.json' in formatted
        assert 'Type: compiled' in formatted
    
    def test_corpus_rendering_from_packages(self, sample_config, sample_agent_package, sample_rule_card):
        """Test complete corpus rendering from packages and YAML files."""
        manager = CorpusManager(sample_config)
        
        corpus_data = manager.render_corpus_from_packages([sample_agent_package])
        
        assert isinstance(corpus_data, CorpusData)
        assert len(corpus_data.content) > 0
        assert 'TEST-001' in corpus_data.content
        assert 'Test Security Rule' in corpus_data.content
        
        # Check metadata
        metadata = corpus_data.metadata
        assert 'version' in metadata
        assert 'source_hash' in metadata
        assert 'rule_count' in metadata
        assert 'size_bytes' in metadata
        assert metadata['rule_count'] >= 1
        assert metadata['size_bytes'] > 0
    
    def test_corpus_validation_valid_corpus(self, sample_config, temp_dir):
        """Test corpus validation with valid corpus."""
        manager = CorpusManager(sample_config)
        
        # Create valid corpus
        corpus_data = CorpusData("Test corpus content", {
            'version': '20250831_120000',
            'source_hash': 'test_hash',
            'rule_count': 1,
            'size_bytes': 18
        })
        
        corpus_path = os.path.join(temp_dir, "test_corpus.json")
        with open(corpus_path, 'w') as f:
            json.dump(corpus_data.to_dict(), f)
        
        result = manager.validate_corpus_integrity(corpus_path)
        
        assert isinstance(result, ValidationResult)
        assert result.valid is True
        assert len(result.errors) == 0
    
    def test_corpus_validation_invalid_corpus(self, sample_config, temp_dir):
        """Test corpus validation with invalid corpus."""
        manager = CorpusManager(sample_config)
        
        # Create invalid corpus (missing required fields)
        invalid_corpus = {'content': 'Test content'}
        
        corpus_path = os.path.join(temp_dir, "invalid_corpus.json")
        with open(corpus_path, 'w') as f:
            json.dump(invalid_corpus, f)
        
        result = manager.validate_corpus_integrity(corpus_path)
        
        assert isinstance(result, ValidationResult)
        assert result.valid is False
        assert len(result.errors) > 0
        assert any('Missing required field' in error for error in result.errors)
    
    def test_corpus_size_limit_warning(self, sample_config, temp_dir):
        """Test corpus size limit validation."""
        # Modify config to have very small limit
        with open(sample_config, 'r') as f:
            config = yaml.safe_load(f)
        
        config['corpus']['output']['max_size_mb'] = 0.001  # 1KB limit
        
        with open(sample_config, 'w') as f:
            yaml.dump(config, f)
        
        manager = CorpusManager(sample_config)
        
        # Create large corpus content
        large_content = "A" * 2000  # 2KB content
        corpus_data = CorpusData(large_content, {
            'version': '20250831_120000',
            'source_hash': 'test_hash',
            'rule_count': 1,
            'size_bytes': len(large_content)
        })
        
        corpus_path = os.path.join(temp_dir, "large_corpus.json")
        with open(corpus_path, 'w') as f:
            json.dump(corpus_data.to_dict(), f)
        
        result = manager.validate_corpus_integrity(corpus_path)
        
        # Should have warnings about size
        assert len(result.warnings) > 0
        assert any('exceeds recommended limit' in warning for warning in result.warnings)
    
    def test_corpus_metadata_retrieval(self, sample_config, temp_dir):
        """Test corpus metadata retrieval."""
        manager = CorpusManager(sample_config)
        
        # Create corpus with metadata
        metadata_dict = {
            'version': '20250831_120000',
            'source_hash': 'abcd1234',
            'rule_count': 5,
            'size_bytes': 1024
        }
        
        corpus_data = CorpusData("Test content", metadata_dict)
        
        # Save corpus
        corpus_path = os.path.join(manager.corpus_path, "corpus.json")
        os.makedirs(os.path.dirname(corpus_path), exist_ok=True)
        with open(corpus_path, 'w') as f:
            json.dump(corpus_data.to_dict(), f)
        
        # Retrieve metadata
        metadata = manager.get_corpus_metadata()
        
        assert isinstance(metadata, CorpusMetadata)
        assert metadata.version == '20250831_120000'
        assert metadata.source_hash == 'abcd1234'
        assert metadata.rule_count == 5
        assert metadata.size_bytes == 1024
    
    def test_nonexistent_corpus_metadata(self, sample_config):
        """Test metadata retrieval for nonexistent corpus."""
        manager = CorpusManager(sample_config)
        metadata = manager.get_corpus_metadata()
        
        assert metadata is None


class TestCorpusData:
    """Test CorpusData container."""
    
    def test_corpus_data_creation(self):
        """Test CorpusData creation and serialization."""
        metadata = {'version': '1.0', 'count': 10}
        corpus_data = CorpusData("Test content", metadata)
        
        assert corpus_data.content == "Test content"
        assert corpus_data.metadata == metadata
        assert corpus_data.created_at is not None
        
        # Test serialization
        data_dict = corpus_data.to_dict()
        assert 'content' in data_dict
        assert 'metadata' in data_dict
        assert 'created_at' in data_dict


class TestCorpusMetadata:
    """Test CorpusMetadata tracking."""
    
    def test_corpus_metadata_creation(self):
        """Test CorpusMetadata creation and serialization."""
        metadata = CorpusMetadata("1.0", "hash123", 10, 1024)
        
        assert metadata.version == "1.0"
        assert metadata.source_hash == "hash123"
        assert metadata.rule_count == 10
        assert metadata.size_bytes == 1024
        assert metadata.created_at is not None
        assert metadata.last_updated is not None
        
        # Test serialization
        data_dict = metadata.to_dict()
        assert 'version' in data_dict
        assert 'source_hash' in data_dict
        assert 'rule_count' in data_dict
        assert 'size_bytes' in data_dict
        assert 'created_at' in data_dict
        assert 'last_updated' in data_dict


class TestValidationResult:
    """Test ValidationResult container."""
    
    def test_validation_result_valid(self):
        """Test ValidationResult for valid corpus."""
        result = ValidationResult(True)
        
        assert result.valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
        assert result.checked_at is not None
    
    def test_validation_result_invalid(self):
        """Test ValidationResult for invalid corpus."""
        errors = ["Error 1", "Error 2"]
        warnings = ["Warning 1"]
        result = ValidationResult(False, errors, warnings)
        
        assert result.valid is False
        assert result.errors == errors
        assert result.warnings == warnings
        assert result.checked_at is not None