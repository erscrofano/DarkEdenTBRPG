"""HUD (Heads-Up Display) elements"""
from .colors import Colors, colorize


def display_time_hud(player, compact=False):
    """
    Display the time HUD at the top of screens with fancy ASCII border.
    Shows: Day X HH:MM [PHASE] with visual day/night indicator
    
    Args:
        player: Player object with world_anchor_timestamp
        compact: If True, shows minimal single-line version
    """
    from ..systems.time_system import GameClock
    
    # Get or create clock from player's anchor
    clock = GameClock(player.world_anchor_timestamp)
    time_data = clock.get_current_time()
    
    if compact:
        # Compact version for tight spaces
        hud_line = clock.get_hud_display()
        print(hud_line)
        print()
        return
    
    # Fancy bordered version
    day = time_data['day']
    hour = time_data['hour']
    minute = time_data['minute']
    phase = time_data['phase']
    
    # Visual indicators (use simple ASCII for Windows compatibility)
    if phase == 'DAY':
        phase_icon = '*'  # Sun (asterisk)
        phase_color = Colors.BRIGHT_YELLOW
        time_color = Colors.BRIGHT_YELLOW
    else:  # NIGHT
        phase_icon = ')'  # Moon (crescent)
        phase_color = Colors.BRIGHT_MAGENTA
        time_color = Colors.BRIGHT_MAGENTA
    
    # Use bright cyan for clock border to stand out from other UI elements
    border_color = Colors.BRIGHT_CYAN
    
    # Build the clock display
    time_str = f"{hour:02d}:{minute:02d}"
    day_str = f"Day {day}"
    phase_str = f"{phase_icon} {phase}"
    
    # Calculate total width (fixed at 60 for consistency)
    width = 60
    
    # Build borders without color codes in length calculation
    border_char = "-"
    top_border = "+" + (border_char * (width - 2)) + "+"
    
    # Top border
    print(colorize(top_border, border_color))
    
    # Content line with centered elements
    content = f"{day_str} | {time_str} | {phase_str}"
    padding = (width - len(content) - 2) // 2
    remaining = width - len(content) - padding - 2
    
    # Build the middle line with proper spacing (calculate without color codes)
    middle_line = "|"
    middle_line += " " * padding
    middle_line += content
    middle_line += " " * remaining
    middle_line += "|"
    
    # Now colorize the displayed version (borders in cyan, content varies)
    print(colorize("|", border_color) + 
          " " * padding + 
          colorize(day_str, Colors.WHITE) + 
          colorize(" | ", Colors.GRAY) + 
          colorize(time_str, time_color) + 
          colorize(" | ", Colors.GRAY) + 
          colorize(phase_str, phase_color) +
          " " * remaining +
          colorize("|", border_color))
    
    # Bottom border
    print(colorize(top_border, border_color))
    print()  # Extra spacing


def refresh_time_display(player):
    """
    Refresh just the time display (can be called before input prompts).
    Uses compact format to avoid screen clutter during continuous updates.
    
    Args:
        player: Player object with world_anchor_timestamp
    """
    from ..systems.time_system import GameClock
    
    clock = GameClock(player.world_anchor_timestamp)
    time_data = clock.get_current_time()
    
    phase = time_data['phase']
    if phase == 'DAY':
        phase_icon = '*'  # Sun (asterisk)
        phase_color = Colors.BRIGHT_YELLOW
    else:
        phase_icon = ')'  # Moon (crescent)
        phase_color = Colors.BRIGHT_MAGENTA
    
    # Single line, less intrusive
    time_str = f"{time_data['hour']:02d}:{time_data['minute']:02d}"
    display = f"[{phase_icon} Day {time_data['day']} {time_str} {colorize(phase, phase_color)}]"
    
    # Print with carriage return to allow for potential updates
    print(f"\r{display}", end='', flush=True)
    print()  # Newline after

