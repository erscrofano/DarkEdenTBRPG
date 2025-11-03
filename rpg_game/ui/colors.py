"""Color utilities for terminal output"""
import platform
from ..config import DEV_FLAGS


# ANSI color codes for terminal
class Colors:
    # Reset
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Text colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Additional colors
    GRAY = '\033[90m'  # Dark gray for subtle text
    
    # Background colors
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'


def colorize(text, color):
    """Add color to text"""
    if DEV_FLAGS['no_color']:
        return text
    if platform.system() == 'Windows':
        # Enable ANSI escape sequences on Windows 10+
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except (OSError, AttributeError, Exception):
            pass  # If it fails, colors just won't work (acceptable fallback)
    return f"{color}{text}{Colors.RESET}"


def show_notification(message, color=Colors.BRIGHT_YELLOW, delay=1.5, critical=False):
    """Show a notification message (OSRS-style)"""
    # Skip non-critical notifications in quiet mode
    if DEV_FLAGS['quiet'] and not critical:
        return
    
    print(f"\n{colorize('◆', color)} {colorize(message, color + Colors.BOLD)}")
    
    # Skip delay in fast mode
    if not DEV_FLAGS['fast']:
        import time
        time.sleep(delay)

