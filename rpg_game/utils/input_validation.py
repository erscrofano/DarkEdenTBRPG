"""Input validation and sanitization utilities"""
import re
from ..constants import MAX_PLAYER_NAME_LENGTH, MIN_PLAYER_NAME_LENGTH
from ..ui import Colors, colorize


def sanitize_input(user_input: str) -> str:
    """Sanitize user input"""
    if not isinstance(user_input, str):
        return ""
    
    sanitized = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', user_input)
    sanitized = sanitized.strip()
    
    return sanitized


def validate_player_name(name: str) -> tuple[bool, str]:
    """Validate player name"""
    if not name:
        return False, "Name cannot be empty"
    
    if len(name) < MIN_PLAYER_NAME_LENGTH:
        return False, f"Name must be at least {MIN_PLAYER_NAME_LENGTH} character"
    
    if len(name) > MAX_PLAYER_NAME_LENGTH:
        return False, f"Name must be no more than {MAX_PLAYER_NAME_LENGTH} characters"
    
    if not name.isprintable():
        return False, "Name contains invalid control characters"
    
    if not re.match(r'^[\x20-\x7E]+$', name):
        return False, "Name contains invalid characters (only printable ASCII characters allowed)"
    
    if len(name) != len(name.encode('ascii', errors='ignore')):
        if not re.match(r'^[a-zA-Z0-9\s\-_\.]+$', name):
            return False, "Name contains invalid characters (only letters, numbers, spaces, hyphens, underscores, and periods allowed)"
    
    if not name.strip():
        return False, "Name cannot be only whitespace"
    
    return True, ""


def get_validated_choice(prompt: str, valid_choices: list[str], case_sensitive: bool = False) -> str | None:
    """Get validated user choice"""
    while True:
        choice = input(prompt).strip()
        choice = sanitize_input(choice)
        
        if not choice:
            continue
        
        if not case_sensitive:
            choice = choice.lower()
            valid_choices_lower = [c.lower() for c in valid_choices]
            if choice in valid_choices_lower:
                # Return original casing from valid_choices
                idx = valid_choices_lower.index(choice)
                return valid_choices[idx]
        else:
            if choice in valid_choices:
                return choice
        
        print(f"{colorize('❌', Colors.BRIGHT_RED)} {colorize('Invalid choice. Please try again.', Colors.WHITE)}")


def get_validated_int(prompt: str, min_value: int | None = None, max_value: int | None = None) -> int | None:
    """Get validated integer input"""
    while True:
        choice = input(prompt).strip()
        choice = sanitize_input(choice)
        
        if not choice:
            return None
        
        try:
            value = int(choice)
            
            if min_value is not None and value < min_value:
                print(f"{colorize('❌', Colors.BRIGHT_RED)} {colorize(f'Value must be at least {min_value}', Colors.WHITE)}")
                continue
            
            if max_value is not None and value > max_value:
                print(f"{colorize('❌', Colors.BRIGHT_RED)} {colorize(f'Value must be at most {max_value}', Colors.WHITE)}")
                continue
            
            return value
        except ValueError:
            print(f"{colorize('❌', Colors.BRIGHT_RED)} {colorize('Please enter a valid number.', Colors.WHITE)}")

