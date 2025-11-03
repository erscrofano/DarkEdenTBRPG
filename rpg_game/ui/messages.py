"""UI message utilities for consistent user feedback"""
from .colors import Colors, colorize


def show_error(message):
    """Display an error message and wait for user input"""
    print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(message, Colors.WHITE)}")
    input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")


def show_success(message):
    """Display a success message and wait for user input"""
    print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(message, Colors.BRIGHT_GREEN)}")
    input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")


def show_info(message):
    """Display an info message and wait for user input"""
    print(f"\n{colorize('ℹ️', Colors.BRIGHT_CYAN)} {colorize(message, Colors.WHITE)}")
    input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")


def show_warning(message):
    """Display a warning message and wait for user input"""
    print(f"\n{colorize('⚠️', Colors.YELLOW)} {colorize(message, Colors.WHITE)}")
    input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")


def wait_for_input(prompt="Press Enter to continue..."):
    """Wait for user to press Enter with optional custom prompt"""
    input(f"\n{colorize(prompt, Colors.WHITE)}")


def format_gold(amount):
    """Format gold amount with thousand separators"""
    return f"{amount:,}g"


def format_stat_change(stat_name, old_value, new_value):
    """Format a stat change display (e.g., HP: 100 → 150)"""
    if new_value > old_value:
        color = Colors.BRIGHT_GREEN
        arrow = "↑"
    elif new_value < old_value:
        color = Colors.BRIGHT_RED
        arrow = "↓"
    else:
        color = Colors.WHITE
        arrow = "→"
    
    return f"{colorize(stat_name + ':', Colors.WHITE)} {colorize(str(old_value), Colors.WHITE)} {colorize(arrow, color)} {colorize(str(new_value), color)}"


def format_percentage(value):
    """Format a decimal as a percentage (e.g., 0.15 → 15%)"""
    return f"{value * 100:.1f}%"


def display_header(title, width=60, color=Colors.BRIGHT_CYAN):
    """Display a formatted header"""
    print(colorize("=" * width, color))
    print(colorize(title, color + Colors.BOLD))
    print(colorize("=" * width, color))


def display_separator(width=60, color=Colors.CYAN):
    """Display a separator line"""
    print(colorize("─" * width, color))

