"""Save and load game system"""
import json
import platform
import shutil
import re
from pathlib import Path
from ..ui import Colors, colorize
from ..constants import DEFAULT_SAVE_SLOT, MAX_SAVE_SLOT_NAME_LENGTH, SAVE_DIR_NAME


def get_save_dir():
    """Get the save directory, creating it if needed"""
    save_dir = Path.home() / SAVE_DIR_NAME
    save_dir.mkdir(parents=True, exist_ok=True)
    return save_dir


def sanitize_slot_name(slot_name):
    """Sanitize save slot name for filesystem safety"""
    if not isinstance(slot_name, str):
        return DEFAULT_SAVE_SLOT
    
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f\x7f-\x9f]', '', slot_name)
    sanitized = sanitized.strip('. -')
    sanitized = re.sub(r'\.{2,}', '', sanitized)
    
    if len(sanitized) > MAX_SAVE_SLOT_NAME_LENGTH:
        sanitized = sanitized[:MAX_SAVE_SLOT_NAME_LENGTH]
    if not sanitized:
        sanitized = DEFAULT_SAVE_SLOT
    
    try:
        safe_path = Path(sanitized)
        if '..' in str(safe_path) or safe_path.is_absolute():
            return DEFAULT_SAVE_SLOT
        if platform.system() == 'Windows':
            reserved_names = {'CON', 'PRN', 'AUX', 'NUL', 
                            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
                            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'}
            if sanitized.upper() in reserved_names:
                return DEFAULT_SAVE_SLOT
    except (ValueError, OSError):
        return DEFAULT_SAVE_SLOT
    
    return sanitized


def get_save_paths(slot_name=None):
    """Get save file paths with security validation"""
    if slot_name is None:
        slot_name = DEFAULT_SAVE_SLOT
    slot_name = sanitize_slot_name(slot_name)
    save_dir = get_save_dir()
    base_name = f'save_{slot_name}.json'
    
    save_path = save_dir / base_name
    temp_path = save_dir / f'{base_name}.tmp'
    backup_path = save_dir / f'{base_name}.bak'
    
    try:
        save_dir_resolved = save_dir.resolve()
        if save_path.resolve().is_relative_to(save_dir_resolved):
            return {'save': save_path, 'temp': temp_path, 'backup': backup_path}
    except (ValueError, AttributeError):
        save_dir_str = str(save_dir.resolve())
        save_path_str = str(save_path.resolve())
        if save_path_str.startswith(save_dir_str):
            return {'save': save_path, 'temp': temp_path, 'backup': backup_path}
    
    from ..utils.logging import log_error
    log_error(f"Path traversal attempt detected for slot: {slot_name}")
    safe_base_name = f'save_{DEFAULT_SAVE_SLOT}.json'
    return {
        'save': save_dir / safe_base_name,
        'temp': save_dir / f'{safe_base_name}.tmp',
        'backup': save_dir / f'{safe_base_name}.bak'
    }


def list_save_slots():
    """List all available save slots"""
    try:
        save_dir = get_save_dir()
    except (OSError, PermissionError) as e:
        from ..utils.logging import log_error
        log_error(f"Failed to access save directory: {e}")
        return []
    
    slots = []
    
    # Look for all save_*.json files
    try:
        save_files = list(save_dir.glob('save_*.json'))
    except (OSError, PermissionError) as e:
        from ..utils.logging import log_error
        log_error(f"Failed to list save files: {e}")
        return []
    
    for save_file in save_files:
        # Skip temp and backup files
        if save_file.name.endswith('.tmp') or save_file.name.endswith('.bak'):
            continue
        
        # Extract slot name from filename (save_<slot_name>.json)
        match = re.match(r'save_(.+)\.json$', save_file.name)
        if match:
            slot_name = match.group(1)
            # Try to load the save to get player info
            try:
                with open(save_file, 'r') as f:
                    data = json.load(f)
                    player_name = data.get('name', 'Unknown')
                    level = data.get('level', 0)
                    slots.append({
                        'slot_name': slot_name,
                        'player_name': player_name,
                        'level': level,
                        'path': save_file
                    })
            except (json.JSONDecodeError, KeyError, IOError):
                # Skip corrupted saves, but still list the slot
                slots.append({
                    'slot_name': slot_name,
                    'player_name': 'Corrupted Save',
                    'level': 0,
                    'path': save_file
                })
    
    # Sort by slot name
    slots.sort(key=lambda x: x['slot_name'])
    return slots


def delete_save_slot(slot_name):
    """Delete a save slot and its backup files"""
    try:
        paths = get_save_paths(slot_name)
        deleted = False
        
        for path_type in ['save', 'backup', 'temp']:
            if paths[path_type].exists():
                paths[path_type].unlink()
                deleted = True
        
        return deleted
    except Exception as e:
        from ..utils.logging import log_error
        log_error(f"Failed to delete save slot '{slot_name}': {e}")
        return False


def save_game(player, slot_name=None):
    """Save player data to file with atomic write and backup"""
    try:
        # Use player's save slot if available, otherwise use provided slot or default
        if hasattr(player, 'save_slot') and player.save_slot:
            slot_name = player.save_slot
        elif slot_name is None:
            slot_name = DEFAULT_SAVE_SLOT
        
        slot_name = sanitize_slot_name(slot_name)
        paths = get_save_paths(slot_name)
        data = player.to_dict()
        # Store save slot in player data for future loads
        data['save_slot'] = slot_name
        
        # Create backup of existing save if it exists
        if paths['save'].exists():
            shutil.copy2(paths['save'], paths['backup'])
        
        # Write to temp file first
        with open(paths['temp'], 'w') as f:
            json.dump(data, f, indent=2)
        
        # Atomic replace
        if platform.system() == 'Windows':
            # On Windows, need to remove target first
            if paths['save'].exists():
                paths['save'].unlink()
            paths['temp'].rename(paths['save'])
        else:
            # Unix atomic replace
            paths['temp'].replace(paths['save'])
        
        return True
    except Exception as e:
        error_msg = f"Error saving game: {e}"
        print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(error_msg, Colors.WHITE)}")
        # Log the error
        from ..utils.logging import log_error
        log_error(f"Failed to save game: {e}", exc_info=True)
        # Clean up temp file if it exists (use the slot_name from the try block)
        try:
            # Re-determine slot_name for cleanup (slot_name param always exists, may be None)
            cleanup_slot = DEFAULT_SAVE_SLOT
            if hasattr(player, 'save_slot') and player.save_slot:
                cleanup_slot = player.save_slot
            elif slot_name is not None:
                cleanup_slot = slot_name
            cleanup_paths = get_save_paths(cleanup_slot)
            if cleanup_paths['temp'].exists():
                cleanup_paths['temp'].unlink()
        except (OSError, PermissionError) as cleanup_error:
            log_error(f"Failed to clean up temp save file: {cleanup_error}")
        return False


def load_game(slot_name=None):
    """Load player data from file with backup fallback"""
    # Import here to avoid circular dependency
    from ..models.player import Player
    
    try:
        if slot_name is None:
            slot_name = DEFAULT_SAVE_SLOT
        
        slot_name = sanitize_slot_name(slot_name)
        paths = get_save_paths(slot_name)
        
        # Try main save file first
        if paths['save'].exists():
            try:
                with open(paths['save'], 'r') as f:
                    raw_data = json.load(f)
                
                # Validate JSON schema before deserialization
                from .validation import validate_and_clean_json
                is_valid, cleaned_data, error_msg = validate_and_clean_json(raw_data)
                if not is_valid:
                    raise ValueError(f"Save file validation failed: {error_msg}")
                
                # Use cleaned data
                data = cleaned_data if cleaned_data else raw_data
                player = Player.from_dict(data)
                # Restore save slot
                if 'save_slot' in data:
                    player.save_slot = data['save_slot']
                else:
                    player.save_slot = slot_name
                return player
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                # Main save corrupted, try backup
                from ..utils.logging import log_error, log_warning
                log_error(f"Main save file corrupted: {e}", exc_info=True)
                print(f"\n{colorize('⚠️', Colors.YELLOW)} {colorize('Main save file corrupted. Attempting backup...', Colors.WHITE)}")
                if paths['backup'].exists():
                    try:
                        with open(paths['backup'], 'r') as f:
                            raw_data = json.load(f)
                        
                        # Validate JSON schema before deserialization
                        from .validation import validate_and_clean_json
                        is_valid, cleaned_data, error_msg = validate_and_clean_json(raw_data)
                        if not is_valid:
                            raise ValueError(f"Backup save file validation failed: {error_msg}")
                        
                        # Use cleaned data
                        data = cleaned_data if cleaned_data else raw_data
                        player = Player.from_dict(data)
                        # Restore save slot
                        if 'save_slot' in data:
                            player.save_slot = data['save_slot']
                        else:
                            player.save_slot = slot_name
                        print(f"{colorize('✅', Colors.BRIGHT_GREEN)} {colorize('Loaded from backup save!', Colors.BRIGHT_GREEN)}")
                        log_warning("Successfully loaded from backup save")
                        return player
                    except (json.JSONDecodeError, KeyError, ValueError) as e2:
                        log_error(f"Backup save file also corrupted: {e2}", exc_info=True)
                        print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(f'Backup also corrupted: {e2}', Colors.WHITE)}")
        
        return None
    except (OSError, PermissionError, IOError) as e:
        from ..utils.logging import log_error
        error_msg = f"Error loading game: {e}"
        log_error(f"Failed to load game: {e}", exc_info=True)
        print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(error_msg, Colors.WHITE)}")
        return None
    except Exception as e:
        from ..utils.logging import log_error
        error_msg = f"Unexpected error loading game: {e}"
        log_error(f"Unexpected error loading game: {e}", exc_info=True)
        print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(error_msg, Colors.WHITE)}")
        return None

