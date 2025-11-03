"""Item rarity system"""
from ..ui import Colors, colorize


# Item Rarity System (OSRS-style)
ITEM_RARITY = {
    'common': {'name': 'Common', 'color': Colors.WHITE, 'symbol': '○'},
    'uncommon': {'name': 'Uncommon', 'color': Colors.BRIGHT_GREEN, 'symbol': '●'},
    'rare': {'name': 'Rare', 'color': Colors.BRIGHT_BLUE, 'symbol': '◆'},
    'epic': {'name': 'Epic', 'color': Colors.BRIGHT_MAGENTA, 'symbol': '★'},
    'legendary': {'name': 'Legendary', 'color': Colors.BRIGHT_YELLOW, 'symbol': '⚡'}
}


def get_item_rarity(item):
    """Determine item rarity based on sell value"""
    sell_value = item.get('sell_value', 0)
    if sell_value >= 200:
        return 'legendary'
    elif sell_value >= 75:
        return 'epic'
    elif sell_value >= 30:
        return 'rare'
    elif sell_value >= 15:
        return 'uncommon'
    return 'common'


def format_item_name(item):
    """Format item name with rarity color"""
    rarity = get_item_rarity(item)
    rarity_info = ITEM_RARITY[rarity]
    return f"{colorize(rarity_info['symbol'] + ' ', rarity_info['color'])}{colorize(item['name'], rarity_info['color'])}"

