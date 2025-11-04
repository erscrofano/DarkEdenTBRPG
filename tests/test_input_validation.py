"""Unit tests for input validation"""
import pytest
from rpg_game.utils.input_validation import validate_player_name, sanitize_input


class TestInputValidation:
    """Test input validation security"""
    
    def test_valid_player_name(self):
        """Test valid player names"""
        valid_names = ["Player", "Test123", "Player_Name", "Player-Name"]
        for name in valid_names:
            is_valid, error = validate_player_name(name)
            assert is_valid is True, f"Name '{name}' should be valid"
            assert error == ""
    
    def test_invalid_player_name_length(self):
        """Test name length validation"""
        # Too short
        is_valid, error = validate_player_name("A")
        assert is_valid is False
        assert "at least" in error.lower()
        
        # Too long (assuming MAX_PLAYER_NAME_LENGTH is reasonable)
        long_name = "A" * 100
        is_valid, error = validate_player_name(long_name)
        assert is_valid is False
        assert "no more than" in error.lower()
    
    def test_special_characters_blocked(self):
        """Test that special characters are blocked"""
        invalid_names = [
            "Player<script>",
            "Player/../../etc",
            "Player\\..",
            "Player; DROP TABLE",
        ]
        for name in invalid_names:
            is_valid, error = validate_player_name(name)
            assert is_valid is False, f"Name '{name}' should be invalid"
    
    def test_unicode_safety(self):
        """Test Unicode input validation"""
        # Control characters should be blocked
        invalid_name = "Player\x00\x01\x02"
        is_valid, error = validate_player_name(invalid_name)
        assert is_valid is False
    
    def test_sanitize_input(self):
        """Test input sanitization"""
        # Control characters should be removed
        dirty_input = "Test\x00\x01\x02String"
        sanitized = sanitize_input(dirty_input)
        assert "\x00" not in sanitized
        assert "\x01" not in sanitized
        assert "\x02" not in sanitized

