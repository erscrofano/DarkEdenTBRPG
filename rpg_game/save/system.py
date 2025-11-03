"""Save and load game system"""
import json
import platform
import shutil
from pathlib import Path
from ..ui import Colors, colorize


def get_save_dir():
    """Get the save directory, creating it if needed"""
    if platform.system() == 'Windows':
        save_dir = Path.home() / '.terminal_rpg'
    else:
        save_dir = Path.home() / '.terminal_rpg'
    save_dir.mkdir(parents=True, exist_ok=True)
    return save_dir


def get_save_paths():
    """Get save file paths"""
    save_dir = get_save_dir()
    return {
        'save': save_dir / 'game_save.json',
        'temp': save_dir / 'game_save.json.tmp',
        'backup': save_dir / 'game_save.json.bak'
    }


def save_game(player):
    """Save player data to file with atomic write and backup"""
    try:
        paths = get_save_paths()
        data = player.to_dict()
        
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
        # Clean up temp file if it exists
        try:
            paths = get_save_paths()
            if paths['temp'].exists():
                paths['temp'].unlink()
        except:
            pass
        return False


def load_game():
    """Load player data from file with backup fallback"""
    # Import here to avoid circular dependency
    from ..models.player import Player
    
    try:
        paths = get_save_paths()
        
        # Try main save file first
        if paths['save'].exists():
            try:
                with open(paths['save'], 'r') as f:
                    data = json.load(f)
                return Player.from_dict(data)
            except Exception as e:
                # Main save corrupted, try backup
                print(f"\n{colorize('⚠️', Colors.YELLOW)} {colorize('Main save file corrupted. Attempting backup...', Colors.WHITE)}")
                if paths['backup'].exists():
                    try:
                        with open(paths['backup'], 'r') as f:
                            data = json.load(f)
                        player = Player.from_dict(data)
                        print(f"{colorize('✅', Colors.BRIGHT_GREEN)} {colorize('Loaded from backup save!', Colors.BRIGHT_GREEN)}")
                        return player
                    except Exception as e2:
                        print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(f'Backup also corrupted: {e2}', Colors.WHITE)}")
        
        return None
    except Exception as e:
        error_msg = f"Error loading game: {e}"
        print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(error_msg, Colors.WHITE)}")
        return None

