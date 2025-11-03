"""Display utilities for terminal output"""
import os
from .colors import Colors, colorize


def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def health_bar(current, maximum, width=30, show_numbers=True):
    """Create a visual health bar"""
    if maximum == 0:
        return "█" * width
    
    percentage = current / maximum
    filled = int(width * percentage)
    bar = ""
    
    # Create colored health bar
    if percentage > 0.6:
        # Green for healthy
        bar_color = Colors.BRIGHT_GREEN
    elif percentage > 0.3:
        # Yellow for wounded
        bar_color = Colors.YELLOW
    else:
        # Red for critical
        bar_color = Colors.BRIGHT_RED
    
    bar += colorize("█" * filled, bar_color)
    bar += "░" * (width - filled)
    
    if show_numbers:
        bar += f" {colorize(str(current), Colors.WHITE)}/{colorize(str(maximum), Colors.WHITE)}"
    
    return bar


def skill_xp_bar(current_exp, exp_to_next, width=20):
    """Create an XP progress bar for skills"""
    if exp_to_next <= 0:
        progress = 1.0
    else:
        progress = min(1.0, current_exp / exp_to_next)
    filled = int(width * progress)
    bar = colorize("█" * filled, Colors.BRIGHT_CYAN) + colorize("░" * (width - filled), Colors.CYAN)
    percentage = int(progress * 100)
    return f"[{bar}] {percentage}%"

