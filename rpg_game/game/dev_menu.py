"""Developer menu for testing and balancing"""
from ..ui import Colors, colorize, clear_screen
from ..constants import (
    MAX_SKILL_LEVEL,
    EXP_MULTIPLIER_PER_LEVEL, STARTING_EXP_TO_NEXT, STAT_POINTS_PER_LEVEL
)
from .dev_tables import view_all_items, view_all_monsters


def dev_menu(player):
    """Hidden dev menu accessible by typing 1337"""
    while True:
        clear_screen()
        print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
        print(colorize("🔧  DEVELOPER MENU  🔧", Colors.BRIGHT_MAGENTA + Colors.BOLD))
        print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
        
        print(f"\n{colorize('CURRENT STATUS:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
        print(f"  {colorize('Level:', Colors.CYAN)} {player.level}")
        print(f"  {colorize('XP:', Colors.CYAN)} {player.exp}/{player.exp_to_next}")
        print(f"  {colorize('Gold:', Colors.CYAN)} {player.gold:,}")
        fishing_level = getattr(player, 'fishing_level', 1)
        cooking_level = getattr(player, 'cooking_level', 1)
        mining_level = getattr(player, 'mining_level', 1)
        print(f"  {colorize('Fishing Level:', Colors.CYAN)} {fishing_level}")
        print(f"  {colorize('Cooking Level:', Colors.CYAN)} {cooking_level}")
        print(f"  {colorize('Mining Level:', Colors.CYAN)} {mining_level}")
        
        print(f"\n{colorize('PLAYER ADJUSTMENTS:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
        print(f"  {colorize('1.', Colors.WHITE)} Set Character Level")
        print(f"  {colorize('2.', Colors.WHITE)} Gain XP (simulate earning)")
        print(f"  {colorize('3.', Colors.WHITE)} Set Gold Amount")
        print(f"  {colorize('4.', Colors.WHITE)} Set Fishing Level")
        print(f"  {colorize('5.', Colors.WHITE)} Set Cooking Level")
        print(f"  {colorize('6.', Colors.WHITE)} Set Mining Level")
        print(f"\n{colorize('GAME DATA:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
        print(f"  {colorize('7.', Colors.WHITE)} View All Items")
        print(f"  {colorize('8.', Colors.WHITE)} View All Monsters")
        print(f"\n{colorize('NAVIGATION:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
        print(f"  {colorize('9.', Colors.WHITE)} Back to Game")
        print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
        
        choice = input(f"\n{colorize('Select option:', Colors.BRIGHT_CYAN)} ").strip()
        
        if choice == '1':
            set_character_level(player)
        elif choice == '2':
            gain_xp(player)
        elif choice == '3':
            set_gold(player)
        elif choice == '4':
            set_skill_level(player, 'fishing')
        elif choice == '5':
            set_skill_level(player, 'cooking')
        elif choice == '6':
            set_skill_level(player, 'mining')
        elif choice == '7':
            view_all_items()
        elif choice == '8':
            view_all_monsters()
        elif choice == '9':
            break
        else:
            print(f"\n{colorize('❌ Invalid choice!', Colors.BRIGHT_RED)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")


def set_character_level(player):
    """Set the character's level directly"""
    clear_screen()
    print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
    print(colorize("📊  SET CHARACTER LEVEL  📊", Colors.BRIGHT_MAGENTA + Colors.BOLD))
    print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
    
    print(f"\n{colorize(f'Current Level: {player.level}', Colors.WHITE)}")
    print(f"{colorize('Enter new level (1-999, or 0 to cancel):', Colors.WHITE)}")
    
    try:
        new_level_input = input(f"\n{colorize('Level:', Colors.BRIGHT_CYAN)} ").strip()
        new_level = int(new_level_input)
        
        if new_level == 0:
            return
        
        if new_level < 1:
            print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Level must be at least 1!', Colors.WHITE)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
            return
        
        if new_level > 999:
            print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Level cannot exceed 999!', Colors.WHITE)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
            return
        
        old_level = player.level
        level_diff = new_level - old_level
        
        # Update level
        player.level = new_level
        
        # Recalculate exp_to_next based on new level
        # Start from level 1 exp requirement
        player.exp_to_next = STARTING_EXP_TO_NEXT
        for _ in range(1, new_level):
            player.exp_to_next = int(player.exp_to_next * EXP_MULTIPLIER_PER_LEVEL)
        
        # Reset exp to 0 when setting level directly (clean slate)
        player.exp = 0
        
        # If level increased, add stat points for the levels gained
        if level_diff > 0:
            player.stat_points += level_diff * STAT_POINTS_PER_LEVEL
        
        # Recalculate max HP based on new level
        player.calculate_max_hp()
        player.hp = player.max_hp
        
        print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(f'Level changed from {old_level} to {new_level}!', Colors.BRIGHT_GREEN)}")
        if level_diff > 0:
            stat_points_gained = level_diff * STAT_POINTS_PER_LEVEL
            print(f"{colorize(f'Gained {stat_points_gained} stat points for {level_diff} level(s).', Colors.WHITE)}")
        print(f"{colorize('XP reset to 0. Max HP updated.', Colors.WHITE)}")
        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
        
    except ValueError:
        print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Invalid input! Please enter a number.', Colors.WHITE)}")
        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")


def gain_xp(player):
    """Add XP to the player, simulating earning it naturally (may trigger level ups)"""
    clear_screen()
    print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
    print(colorize("⭐  GAIN XP  ⭐", Colors.BRIGHT_MAGENTA + Colors.BOLD))
    print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
    
    print(f"\n{colorize(f'Current Level: {player.level}', Colors.WHITE)}")
    print(f"{colorize(f'Current XP: {player.exp}/{player.exp_to_next}', Colors.WHITE)}")
    print(f"{colorize('Enter amount of XP to gain:', Colors.WHITE)}")
    
    try:
        xp_input = input(f"\n{colorize('XP Amount:', Colors.BRIGHT_CYAN)} ").strip()
        xp_gain = int(xp_input)
        
        if xp_gain < 0:
            print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('XP amount cannot be negative!', Colors.WHITE)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
            return
        
        if xp_gain == 0:
            return
        
        old_level = player.level
        player.exp += xp_gain
        
        # Check for level ups (handle multiple level ups)
        # Use the player's level_up method to properly handle stat points and other level-up logic
        levels_gained = 0
        while player.level_up(silent=True):
            levels_gained += 1
        
        print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(f'Gained {xp_gain} XP!', Colors.BRIGHT_GREEN)}")
        
        if levels_gained > 0:
            print(f"{colorize('🌟', Colors.BRIGHT_YELLOW)} {colorize(f'Leveled up {levels_gained} time(s)! New level: {player.level}', Colors.BRIGHT_GREEN)}")
            print(f"{colorize(f'Current XP: {player.exp}/{player.exp_to_next}', Colors.WHITE)}")
        else:
            print(f"{colorize(f'New XP: {player.exp}/{player.exp_to_next}', Colors.WHITE)}")
        
        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
        
    except ValueError:
        print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Invalid input! Please enter a number.', Colors.WHITE)}")
        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")


def set_gold(player):
    """Set the player's gold amount"""
    clear_screen()
    print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
    print(colorize("💰  SET GOLD  💰", Colors.BRIGHT_MAGENTA + Colors.BOLD))
    print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
    
    print(f"\n{colorize(f'Current Gold: {player.gold:,}', Colors.WHITE)}")
    print(f"{colorize('Enter new gold amount (0 to cancel):', Colors.WHITE)}")
    
    try:
        gold_input = input(f"\n{colorize('Gold Amount:', Colors.BRIGHT_CYAN)} ").strip()
        new_gold = int(gold_input)
        
        if new_gold == 0 and player.gold != 0:
            # Only cancel if not already at 0
            confirm = input(f"{colorize('Set gold to 0? (y/n): ', Colors.WHITE)}").strip().lower()
            if confirm != 'y':
                return
        
        if new_gold < 0:
            print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Gold cannot be negative!', Colors.WHITE)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
            return
        
        old_gold = player.gold
        player.gold = new_gold
        
        print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(f'Gold changed from {old_gold:,} to {new_gold:,}!', Colors.BRIGHT_GREEN)}")
        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
        
    except ValueError:
        print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Invalid input! Please enter a number.', Colors.WHITE)}")
        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")


def set_skill_level(player, skill_name):
    """Set a skill level (fishing, cooking, or mining)"""
    clear_screen()
    skill_display_name = skill_name.capitalize()
    print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
    print(colorize(f"🎣  SET {skill_display_name.upper()} LEVEL  🎣", Colors.BRIGHT_MAGENTA + Colors.BOLD))
    print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
    
    current_level = getattr(player, f'{skill_name}_level', 1)
    current_exp = getattr(player, f'{skill_name}_exp', 0)
    current_exp_to_next = getattr(player, f'{skill_name}_exp_to_next', 100)
    
    print(f"\n{colorize(f'Current {skill_display_name} Level: {current_level}', Colors.WHITE)}")
    print(f"{colorize(f'Current XP: {current_exp}/{current_exp_to_next}', Colors.WHITE)}")
    print(f"{colorize(f'Enter new level (1-{MAX_SKILL_LEVEL}, or 0 to cancel):', Colors.WHITE)}")
    
    try:
        level_input = input(f"\n{colorize('Level:', Colors.BRIGHT_CYAN)} ").strip()
        new_level = int(level_input)
        
        if new_level == 0:
            return
        
        if new_level < 1:
            print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Level must be at least 1!', Colors.WHITE)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
            return
        
        if new_level > MAX_SKILL_LEVEL:
            print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(f'Level cannot exceed {MAX_SKILL_LEVEL}!', Colors.WHITE)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
            return
        
        old_level = current_level
        setattr(player, f'{skill_name}_level', new_level)
        
        # Reset XP to 0 for clean state
        setattr(player, f'{skill_name}_exp', 0)
        
        # Recalculate exp_to_next based on new level
        from ..constants import STARTING_SKILL_EXP_TO_NEXT, SKILL_EXP_MULTIPLIER_PER_LEVEL
        exp_to_next = STARTING_SKILL_EXP_TO_NEXT
        for _ in range(1, new_level):
            exp_to_next = int(exp_to_next * SKILL_EXP_MULTIPLIER_PER_LEVEL)
        setattr(player, f'{skill_name}_exp_to_next', exp_to_next)
        
        print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(f'{skill_display_name} level changed from {old_level} to {new_level}!', Colors.BRIGHT_GREEN)}")
        print(f"{colorize('XP reset to 0.', Colors.WHITE)}")
        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
        
    except ValueError:
        print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Invalid input! Please enter a number.', Colors.WHITE)}")
        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")

