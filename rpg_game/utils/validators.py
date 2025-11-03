"""Common validation utilities"""


def validate_integer_input(value, min_value=None, max_value=None, default=None):
    """
    Validate integer input with optional bounds.
    
    Args:
        value: String input to validate
        min_value: Minimum allowed value (inclusive)
        max_value: Maximum allowed value (inclusive)
        default: Default value if parsing fails
    
    Returns:
        (is_valid, result_value, error_message)
    """
    try:
        num = int(value)
        
        if min_value is not None and num < min_value:
            return (False, default, f"Value must be at least {min_value}")
        
        if max_value is not None and num > max_value:
            return (False, default, f"Value cannot exceed {max_value}")
        
        return (True, num, None)
    
    except ValueError:
        return (False, default, "Please enter a valid number")


def validate_choice(choice, min_choice, max_choice):
    """
    Validate a menu choice is within valid range.
    
    Args:
        choice: String input from user
        min_choice: Minimum valid choice
        max_choice: Maximum valid choice
    
    Returns:
        (is_valid, choice_num, error_message)
    """
    try:
        choice_num = int(choice)
        
        if min_choice <= choice_num <= max_choice:
            return (True, choice_num, None)
        else:
            return (False, None, f"Please enter a number between {min_choice} and {max_choice}")
    
    except ValueError:
        return (False, None, "Please enter a valid number")


def validate_yes_no(value):
    """
    Validate yes/no input.
    
    Args:
        value: String input from user
    
    Returns:
        (is_yes, is_no) tuple - both False means invalid input
    """
    normalized = value.strip().lower()
    
    if normalized in ('y', 'yes'):
        return (True, False)
    elif normalized in ('n', 'no'):
        return (False, True)
    else:
        return (False, False)


def clamp(value, min_value, max_value):
    """Clamp a value between min and max bounds"""
    return max(min_value, min(value, max_value))

