"""Core skill XP system"""
from ..constants import (
    MAX_SKILL_LEVEL, SKILL_EXP_MULTIPLIER_PER_LEVEL,
    NOTIFICATION_DURATION_NORMAL
)
from ..ui import Colors, show_notification
from ..achievements.system import check_achievements


def add_skill_xp(player, skill, amount):
    """Add XP to a skill and handle level ups"""
    if skill == "fishing":
        player.fishing_exp += amount
        while player.fishing_exp >= player.fishing_exp_to_next and player.fishing_level < MAX_SKILL_LEVEL:
            player.fishing_exp -= player.fishing_exp_to_next
            player.fishing_level += 1
            player.fishing_exp_to_next = int(player.fishing_exp_to_next * SKILL_EXP_MULTIPLIER_PER_LEVEL)
            show_notification(f"Fishing level {player.fishing_level}!", Colors.BRIGHT_CYAN, NOTIFICATION_DURATION_NORMAL, critical=True)
            check_achievements(player, 'fishing_level')
        if player.fishing_level >= MAX_SKILL_LEVEL:
            player.fishing_exp = player.fishing_exp_to_next - 1  # Cap at 99
    elif skill == "cooking":
        player.cooking_exp += amount
        while player.cooking_exp >= player.cooking_exp_to_next and player.cooking_level < MAX_SKILL_LEVEL:
            player.cooking_exp -= player.cooking_exp_to_next
            player.cooking_level += 1
            player.cooking_exp_to_next = int(player.cooking_exp_to_next * SKILL_EXP_MULTIPLIER_PER_LEVEL)
            show_notification(f"Cooking level {player.cooking_level}!", Colors.BRIGHT_MAGENTA, NOTIFICATION_DURATION_NORMAL, critical=True)
            check_achievements(player, 'cooking_level')
        if player.cooking_level >= MAX_SKILL_LEVEL:
            player.cooking_exp = player.cooking_exp_to_next - 1  # Cap at 99
    elif skill == "mining":
        player.mining_exp += amount
        while player.mining_exp >= player.mining_exp_to_next and player.mining_level < MAX_SKILL_LEVEL:
            player.mining_exp -= player.mining_exp_to_next
            player.mining_level += 1
            player.mining_exp_to_next = int(player.mining_exp_to_next * SKILL_EXP_MULTIPLIER_PER_LEVEL)
            show_notification(f"Mining level {player.mining_level}!", Colors.BRIGHT_MAGENTA, NOTIFICATION_DURATION_NORMAL, critical=True)
            check_achievements(player, 'mining_level')
        if player.mining_level >= MAX_SKILL_LEVEL:
            player.mining_exp = player.mining_exp_to_next - 1  # Cap at 99

