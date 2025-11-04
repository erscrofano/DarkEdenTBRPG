"""JSON schema validation for save files"""
import json
from typing import Dict, Any, Optional
from ..utils.logging import log_error


# Save file JSON schema definition
SAVE_SCHEMA = {
    "type": "object",
    "required": ["name", "level", "exp", "exp_to_next", "gold", "inventory"],
    "properties": {
        "name": {"type": "string", "minLength": 1, "maxLength": 50},
        "level": {"type": "integer", "minimum": 1, "maximum": 100},
        "exp": {"type": "integer", "minimum": 0},
        "exp_to_next": {"type": "integer", "minimum": 1},
        "gold": {"type": "integer", "minimum": 0},
        "inventory": {
            "type": "array",
            "items": {"type": "object"},
            "maxItems": 1000  # Prevent resource exhaustion
        },
        "base_hp": {"type": "integer", "minimum": 1, "maximum": 1000},
        "str": {"type": "integer", "minimum": 1, "maximum": 1000},
        "dex": {"type": "integer", "minimum": 1, "maximum": 1000},
        "agl": {"type": "integer", "minimum": 1, "maximum": 1000},
        "stat_points": {"type": "integer", "minimum": 0},
        "hp": {"type": "integer", "minimum": 0},
        "max_hp": {"type": "integer", "minimum": 1},
        "attack": {"type": "integer", "minimum": 0},
        "defense": {"type": "integer", "minimum": 0},
        "weapon": {"type": ["object", "null"]},
        "armor": {"type": ["object", "null"]},
        "tool": {"type": ["object", "null"]},
        "save_slot": {"type": "string", "maxLength": 50},
        "schema": {"type": "integer", "minimum": 1, "maximum": 100},
        "world_anchor_timestamp": {"type": "number", "minimum": 0}
    },
    "additionalProperties": True  # Allow extra fields for forward compatibility
}


def validate_save_data(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate save file data against JSON schema.
    
    Args:
        data: Dictionary containing save data
        
    Returns:
        Tuple of (is_valid, error_message)
        If valid, error_message is None
    """
    # Basic type check
    if not isinstance(data, dict):
        return False, "Save data must be a dictionary"
    
    # Check required fields
    required_fields = SAVE_SCHEMA["required"]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    # Validate field types and ranges
    properties = SAVE_SCHEMA["properties"]
    for field_name, field_value in data.items():
        if field_name not in properties:
            continue  # Additional properties allowed
        
        field_schema = properties[field_name]
        
        # Type validation
        expected_type = field_schema.get("type")
        if expected_type:
            if isinstance(expected_type, list):
                # Multiple types allowed (e.g., ["object", "null"])
                if not any(_is_valid_type(field_value, t) for t in expected_type):
                    return False, f"Field '{field_name}' has invalid type. Expected {expected_type}, got {type(field_value).__name__}"
            else:
                if not _is_valid_type(field_value, expected_type):
                    return False, f"Field '{field_name}' has invalid type. Expected {expected_type}, got {type(field_value).__name__}"
        
        # Range validation for numbers
        if isinstance(field_value, (int, float)):
            if "minimum" in field_schema and field_value < field_schema["minimum"]:
                return False, f"Field '{field_name}' value {field_value} is below minimum {field_schema['minimum']}"
            if "maximum" in field_schema and field_value > field_schema["maximum"]:
                return False, f"Field '{field_name}' value {field_value} exceeds maximum {field_schema['maximum']}"
        
        # String length validation
        if isinstance(field_value, str):
            if "minLength" in field_schema and len(field_value) < field_schema["minLength"]:
                return False, f"Field '{field_name}' length {len(field_value)} is below minimum {field_schema['minLength']}"
            if "maxLength" in field_schema and len(field_value) > field_schema["maxLength"]:
                return False, f"Field '{field_name}' length {len(field_value)} exceeds maximum {field_schema['maxLength']}"
        
        # Array validation
        if isinstance(field_value, list):
            if "maxItems" in field_schema and len(field_value) > field_schema["maxItems"]:
                return False, f"Field '{field_name}' array length {len(field_value)} exceeds maximum {field_schema['maxItems']}"
    
    return True, None


def _is_valid_type(value: Any, expected_type: str) -> bool:
    """Check if value matches expected JSON schema type"""
    type_map = {
        "string": str,
        "integer": int,
        "number": (int, float),
        "boolean": bool,
        "array": list,
        "object": dict,
        "null": type(None)
    }
    
    if expected_type not in type_map:
        return True  # Unknown type, skip validation
    
    expected_python_type = type_map[expected_type]
    if isinstance(expected_python_type, tuple):
        return isinstance(value, expected_python_type)
    return isinstance(value, expected_python_type)


def validate_and_clean_json(data: Dict[str, Any]) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Validate JSON data and clean it for safe deserialization.
    
    Args:
        data: Raw JSON data dictionary
        
    Returns:
        Tuple of (is_valid, cleaned_data, error_message)
    """
    is_valid, error = validate_save_data(data)
    if not is_valid:
        return False, None, error
    
    # Clean the data (remove potentially dangerous fields, normalize types)
    cleaned_data = {}
    
    # Copy only known safe fields
    safe_fields = set(SAVE_SCHEMA["properties"].keys()) | set(SAVE_SCHEMA["required"])
    for field_name, field_value in data.items():
        if field_name in safe_fields or field_name in ["kill_streak", "total_kills", "highest_level_enemy", 
                                                       "highest_tower_floor", "achievements", "fishing_level",
                                                       "fishing_exp", "fishing_exp_to_next", "cooking_level",
                                                       "cooking_exp", "cooking_exp_to_next", "mining_level",
                                                       "mining_exp", "mining_exp_to_next", "current_location"]:
            cleaned_data[field_name] = field_value
    
    return True, cleaned_data, None

