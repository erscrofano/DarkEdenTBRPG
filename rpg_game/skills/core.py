"""Core skill XP system"""
from ..ui import Colors, show_notification
from ..achievements.system import check_achievements


def add_skill_xp(player, skill, amount):
    """Add XP to a skill and handle level ups"""
    if skill == "fishing":
        player.fishing_exp += amount
        while player.fishing_exp >= player.fishing_exp_to_next and player.fishing_level < 99:
            player.fishing_exp -= player.fishing_exp_to_next
            player.fishing_level += 1
            player.fishing_exp_to_next = int(player.fishing_exp_to_next * 1.35)
            show_notification(f"Fishing level {player.fishing_level}!", Colors.BRIGHT_CYAN, 1.5, critical=True)
            check_achievements(player, 'fishing_level')
        if player.fishing_level >= 99:
            player.fishing_exp = player.fishing_exp_to_next - 1  # Cap at 99
    elif skill == "cooking":
        player.cooking_exp += amount
        while player.cooking_exp >= player.cooking_exp_to_next and player.cooking_level < 99:
            player.cooking_exp -= player.cooking_exp_to_next
            player.cooking_level += 1
            player.cooking_exp_to_next = int(player.cooking_exp_to_next * 1.35)
            show_notification(f"Cooking level {player.cooking_level}!", Colors.BRIGHT_MAGENTA, 1.5, critical=True)
            check_achievements(player, 'cooking_level')
        if player.cooking_level >= 99:
            player.cooking_exp = player.cooking_exp_to_next - 1  # Cap at 99
    elif skill == "mining":
        player.mining_exp += amount
        while player.mining_exp >= player.mining_exp_to_next and player.mining_level < 99:
            player.mining_exp -= player.mining_exp_to_next
            player.mining_level += 1
            player.mining_exp_to_next = int(player.mining_exp_to_next * 1.35)
            show_notification(f"Mining level {player.mining_level}!", Colors.BRIGHT_MAGENTA, 1.5, critical=True)
            check_achievements(player, 'mining_level')
        if player.mining_level >= 99:
            player.mining_exp = player.mining_exp_to_next - 1  # Cap at 99

