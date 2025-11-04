"""Unit tests for save system security"""
import pytest
import json
import tempfile
from pathlib import Path
from rpg_game.save.system import sanitize_slot_name, get_save_paths, get_save_dir
from rpg_game.save.validation import validate_save_data, validate_and_clean_json


class TestSaveSecurity:
    """Test security features of save system"""
    
    def test_path_traversal_prevention(self):
        """Test that path traversal attempts are blocked"""
        malicious_names = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "save_../../test",
            "normal_name/../../../etc",
            "....//....//etc/passwd",
        ]
        
        for malicious_name in malicious_names:
            sanitized = sanitize_slot_name(malicious_name)
            assert sanitized != malicious_name
            assert ".." not in sanitized
            assert "/" not in sanitized
            assert "\\" not in sanitized
    
    def test_windows_reserved_names(self):
        """Test that Windows reserved names are blocked"""
        reserved_names = ["CON", "PRN", "AUX", "NUL", "COM1", "LPT1"]
        for name in reserved_names:
            sanitized = sanitize_slot_name(name)
            assert sanitized != name
    
    def test_save_paths_within_directory(self):
        """Test that save paths are always within save directory"""
        save_dir = get_save_dir()
        paths = get_save_paths("test_slot")
        
        # Verify all paths are within save directory
        assert str(paths['save']).startswith(str(save_dir))
        assert str(paths['temp']).startswith(str(save_dir))
        assert str(paths['backup']).startswith(str(save_dir))
    
    def test_json_validation_valid_data(self):
        """Test JSON validation with valid save data"""
        valid_data = {
            "name": "TestPlayer",
            "level": 5,
            "exp": 100,
            "exp_to_next": 200,
            "gold": 500,
            "inventory": [],
            "base_hp": 10,
            "str": 5,
            "dex": 5,
            "agl": 5,
            "hp": 100,
            "max_hp": 100,
            "attack": 10,
            "defense": 5,
        }
        
        is_valid, error = validate_save_data(valid_data)
        assert is_valid is True
        assert error is None
    
    def test_json_validation_missing_fields(self):
        """Test JSON validation with missing required fields"""
        invalid_data = {
            "name": "TestPlayer",
            # Missing required fields
        }
        
        is_valid, error = validate_save_data(invalid_data)
        assert is_valid is False
        assert error is not None
        assert "Missing required fields" in error
    
    def test_json_validation_type_mismatch(self):
        """Test JSON validation with wrong types"""
        invalid_data = {
            "name": "TestPlayer",
            "level": "not_a_number",  # Should be int
            "exp": 100,
            "exp_to_next": 200,
            "gold": 500,
            "inventory": [],
        }
        
        is_valid, error = validate_save_data(invalid_data)
        assert is_valid is False
        assert error is not None
    
    def test_json_validation_range_limits(self):
        """Test JSON validation with out-of-range values"""
        invalid_data = {
            "name": "TestPlayer",
            "level": 999,  # Exceeds maximum
            "exp": 100,
            "exp_to_next": 200,
            "gold": 500,
            "inventory": [],
        }
        
        is_valid, error = validate_save_data(invalid_data)
        assert is_valid is False
        assert "exceeds maximum" in error.lower()
    
    def test_validate_and_clean_json(self):
        """Test JSON validation and cleaning"""
        valid_data = {
            "name": "TestPlayer",
            "level": 5,
            "exp": 100,
            "exp_to_next": 200,
            "gold": 500,
            "inventory": [],
        }
        
        is_valid, cleaned_data, error = validate_and_clean_json(valid_data)
        assert is_valid is True
        assert cleaned_data is not None
        assert error is None

