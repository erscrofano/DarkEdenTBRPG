"""Item display utilities"""
from ..ui import Colors, colorize


def format_item_name(item):
    """Format item name for display"""
    return colorize(item['name'], Colors.BRIGHT_CYAN)

