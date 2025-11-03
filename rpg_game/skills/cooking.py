"""Cooking skill system"""
import random
import time
import threading
from datetime import datetime
from ..config import DEV_FLAGS
from ..ui import Colors, colorize, clear_screen, show_notification, skill_xp_bar
from ..items.inventory import add_item_to_inventory, remove_item_from_inventory, get_item_quantity
from ..items.rarity import format_item_name
from ..save.system import get_save_dir
from .core import add_skill_xp
from .fishing import FISH_TYPES, COOKED_FISH_ITEMS
from ..achievements.system import check_achievements


# Skill tables - Cooking requirements and XP
COOK_LEVEL_REQUIREMENTS = {
    'goby': 1,
    'mackerel': 5,
    'salmon': 10,
    'eel': 20,
    'shad': 30,
    'carp': 40,
    'seabream': 50,
    'silvery_eel': 60,
    'silvery_shad': 70,
    'silvery_carp': 80
}

COOKING_XP_AWARDS = {
    'goby': 10,
    'mackerel': 18,
    'salmon': 26,
    'eel': 40,
    'shad': 60,
    'carp': 85,
    'seabream': 120,
    'silvery_eel': 160,
    'silvery_shad': 190,
    'silvery_carp': 240
}


def log_cooking_outcome(player, cooked_name, successes, burns, xp_gained):
    """Log cooking outcomes to file"""
    try:
        log_dir = get_save_dir() / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / 'cooking.log'
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {player.name} (Cooking Lv.{player.cooking_level}) cooked {successes}x {cooked_name} ({burns} burnt) (+{xp_gained} XP)\n")
    except (OSError, PermissionError, IOError) as e:
        # Log error but don't fail cooking
        from ..utils.logging import log_warning
        log_warning(f"Failed to log cooking outcome: {e}")


def cook_fish(player):
    """Cooking system - cook raw fish into healing foods with automatic progress"""
    while True:
        clear_screen()
        print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
        print(colorize("🔥  COOKING  🔥", Colors.BRIGHT_MAGENTA + Colors.BOLD))
        print(colorize("=" * 60, Colors.MAGENTA))
        print(f"\n{colorize('Cooking Level:', Colors.BRIGHT_MAGENTA)} {colorize(str(player.cooking_level), Colors.BRIGHT_GREEN)}")
        print(f"{colorize('Cooking XP:', Colors.WHITE)} {skill_xp_bar(player.cooking_exp, player.cooking_exp_to_next, width=25)}")
        
        # Refresh raw fish list
        raw_fish_items = []
        for item in player.inventory:
            if item.get('type') == 'material':
                for fish_key, fish_data in FISH_TYPES.items():
                    if item.get('name') == fish_data['name']:
                        # Use normalized key for lookup
                        lookup_key = fish_data.get('key', fish_key)
                        required_level = COOK_LEVEL_REQUIREMENTS.get(lookup_key, 1)
                        if player.cooking_level < required_level:
                            success_chance = 0.0
                        else:
                            success_chance = max(0.10, min(0.95, 0.80 + 0.01 * (player.cooking_level - required_level)))
                        
                        qty = get_item_quantity(item)
                        xp_per_cook = COOKING_XP_AWARDS.get(lookup_key, 10)
                        
                        raw_fish_items.append({
                            'item': item,
                            'fish_key': lookup_key,  # Use normalized key
                            'required_level': required_level,
                            'success_chance': success_chance,
                            'quantity': qty,
                            'xp_per_cook': xp_per_cook
                        })
                        break
        
        if not raw_fish_items:
            print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('You have no raw fish to cook!', Colors.WHITE)}")
            print(colorize("\n" + "=" * 60, Colors.MAGENTA))
            print(f"\n  {colorize('1.', Colors.BRIGHT_BLUE)} Back to Town")
            print(colorize("=" * 60, Colors.MAGENTA))
            choice = input(f"\n{colorize('What do you do?', Colors.BRIGHT_CYAN)} ").strip()
            if choice == '1':
                return
            continue
        
        print(f"\n{colorize('Raw Fish Available:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
        for idx, fish_info in enumerate(raw_fish_items, 1):
            item = fish_info['item']
            fish_key = fish_info['fish_key']
            required = fish_info['required_level']
            success_chance = fish_info['success_chance']
            qty = fish_info['quantity']
            xp = fish_info['xp_per_cook']
            cooked_name = COOKED_FISH_ITEMS[fish_key]['name']
            heal = COOKED_FISH_ITEMS[fish_key]['heal']
            
            if player.cooking_level < required:
                status = colorize(f'LOCKED (Requires Lv.{required})', Colors.RED)
            else:
                status = colorize(f'{int(success_chance * 100)}% success', Colors.BRIGHT_GREEN)
            
            formatted_name = format_item_name(item)
            print(f"  {colorize(str(idx) + '.', Colors.WHITE)} {formatted_name} {colorize(f'x{qty}', Colors.YELLOW)}")
            print(f"      → {colorize(cooked_name, Colors.BRIGHT_YELLOW)} {colorize(f'(Heals {heal} HP, +{xp} XP)', Colors.GRAY)}")
            print(f"      {status}")
        
        print(colorize("\n" + "=" * 60, Colors.MAGENTA))
        print(f"\n  {colorize(str(len(raw_fish_items) + 1) + '.', Colors.BRIGHT_BLUE)} Back to Town")
        print(colorize("=" * 60, Colors.MAGENTA))
        
        try:
            choice = input(f"\n{colorize('Select fish to cook (or number to go back):', Colors.BRIGHT_CYAN)} ").strip()
            choice_num = int(choice)
            
            if choice_num == len(raw_fish_items) + 1:
                return
            
            if 1 <= choice_num <= len(raw_fish_items):
                selected_fish = raw_fish_items[choice_num - 1]
                
                if player.cooking_level < selected_fish['required_level']:
                    required_level_msg = f"You need Cooking level {selected_fish['required_level']} to cook this fish!"
                    print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(required_level_msg, Colors.WHITE)}")
                    input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                    continue
                
                # Choose quantity
                max_qty = selected_fish['quantity']
                print(f"\n{colorize('How many to cook?', Colors.BRIGHT_WHITE + Colors.BOLD)}")
                print(f"  {colorize('1.', Colors.WHITE)} Cook 1")
                if max_qty >= 5:
                    print(f"  {colorize('2.', Colors.WHITE)} Cook 5")
                if max_qty >= 10:
                    print(f"  {colorize('3.', Colors.WHITE)} Cook 10")
                print(f"  {colorize('4.', Colors.WHITE)} Cook All {colorize(f'({max_qty})', Colors.YELLOW)}")
                print(f"  {colorize('5.', Colors.WHITE)} Cancel")
                
                qty_choice = input(f"\n{colorize('Choice:', Colors.BRIGHT_CYAN)} ").strip()
                
                if qty_choice == '1':
                    cook_qty = 1
                elif qty_choice == '2' and max_qty >= 5:
                    cook_qty = min(5, max_qty)
                elif qty_choice == '3' and max_qty >= 10:
                    cook_qty = min(10, max_qty)
                elif qty_choice == '4':
                    cook_qty = max_qty
                elif qty_choice == '5':
                    continue
                else:
                    print(f"\n{colorize('❌ Invalid choice!', Colors.BRIGHT_RED)}")
                    input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                    continue
                
                # Start automatic cooking with progress bars and cancellation
                cooked_fish_key = selected_fish['fish_key']
                cooked_item_template = COOKED_FISH_ITEMS[cooked_fish_key].copy()
                success_chance = selected_fish['success_chance']
                successes = 0
                burns = 0
                total_xp = 0
                cooking_active = True
                
                # Cooking duration per fish (3 seconds base)
                cooking_duration = 3
                progress_steps = 20
                step_delay = cooking_duration / progress_steps
                
                def input_handler():
                    """Handle user input to stop cooking"""
                    nonlocal cooking_active
                    input()  # Wait for Enter key
                    cooking_active = False
                
                # Start input handler thread for cancellation
                input_thread = threading.Thread(target=input_handler, daemon=True)
                input_thread.start()
                
                for cook_num in range(cook_qty):
                    if not cooking_active:
                        break  # User cancelled
                    
                    # Show progress bar for each fish
                    for i in range(progress_steps):
                        if not cooking_active:
                            break  # User cancelled mid-progress
                        
                        clear_screen()
                        print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
                        print(colorize("🔥  COOKING  🔥", Colors.BRIGHT_MAGENTA + Colors.BOLD))
                        print(colorize("=" * 60, Colors.MAGENTA))
                        progress = (i + 1) / progress_steps
                        filled = int(20 * progress)
                        bar = colorize("█" * filled, Colors.BRIGHT_YELLOW) + "░" * (20 - filled)
                        percentage = int(progress * 100)
                        
                        cooked_name = COOKED_FISH_ITEMS[cooked_fish_key]['name']
                        print(f"\n{colorize('Cooking:', Colors.WHITE)} {colorize(cooked_name, Colors.BRIGHT_YELLOW)}")
                        print(f"{colorize('Progress:', Colors.BRIGHT_WHITE)} [{bar}] {colorize(f'{percentage}%', Colors.BRIGHT_YELLOW)}")
                        print(f"\n{colorize('Fish', Colors.WHITE)} {colorize(str(cook_num + 1), Colors.BRIGHT_CYAN)}/{colorize(str(cook_qty), Colors.WHITE)}")
                        print(f"{colorize('Cooked:', Colors.BRIGHT_GREEN)} {colorize(str(successes), Colors.BRIGHT_GREEN)} | {colorize('Burnt:', Colors.BRIGHT_RED)} {colorize(str(burns), Colors.BRIGHT_RED)}")
                        if total_xp > 0:
                            print(f"{colorize('Total XP:', Colors.BRIGHT_MAGENTA)} {colorize(str(total_xp), Colors.BRIGHT_GREEN)}")
                        print(f"\n{colorize('Press Enter to stop cooking', Colors.YELLOW)}")
                        print(colorize("=" * 60, Colors.MAGENTA))
                        
                        if not DEV_FLAGS['fast']:
                            time.sleep(step_delay)
                    
                    if not cooking_active:
                        break  # User cancelled before this fish finished
                    
                    # Determine success/failure
                    if random.random() < success_chance:
                        # Success - create cooked fish
                        add_item_to_inventory(player.inventory, cooked_item_template.copy())
                        successes += 1
                        xp_gain = selected_fish['xp_per_cook']
                        total_xp += xp_gain
                        add_skill_xp(player, "cooking", xp_gain)
                        
                        # Check achievements
                        if cook_num == 0:
                            check_achievements(player, 'first_cook')
                        if cooked_fish_key == 'silvery_carp':
                            check_achievements(player, 'masterpiece')
                        
                        # Brief success notification
                        if not DEV_FLAGS['quiet']:
                            cooked_name = COOKED_FISH_ITEMS[cooked_fish_key]['name']
                            show_notification(f"🔥 Cooked {cooked_name}! +{xp_gain} XP", Colors.BRIGHT_GREEN, 0.3)
                    else:
                        # Burnt - remove fish, no item created
                        burns += 1
                        if not DEV_FLAGS['quiet']:
                            show_notification(f"💨 Burnt the fish…", Colors.RED, 0.2)
                    
                    # Remove 1 raw fish
                    remove_item_from_inventory(player.inventory, selected_fish['item'], 1)
                    
                    # Brief pause between cooks (unless fast mode or cancelled)
                    if cook_num < cook_qty - 1 and not DEV_FLAGS['fast'] and cooking_active:
                        time.sleep(0.2)
                
                # Track how many were attempted
                attempted_count = successes + burns
                was_cancelled = attempted_count < cook_qty
                
                # Stop the input handler thread
                cooking_active = False
                
                # Log outcome
                if successes > 0 or burns > 0:
                    cooked_name = COOKED_FISH_ITEMS[cooked_fish_key]['name']
                    log_cooking_outcome(player, cooked_name, successes, burns, total_xp)
                
                # Show final results
                clear_screen()
                if was_cancelled:
                    # Cooking was cancelled early
                    title = "🔥  COOKING CANCELLED  🔥"
                    title_color = Colors.BRIGHT_YELLOW
                    print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
                    print(colorize(title, title_color + Colors.BOLD))
                    print(colorize("=" * 60, Colors.MAGENTA))
                    print(f"\n{colorize(f'You cooked {attempted_count} out of {cook_qty} fish before stopping.', Colors.WHITE)}")
                else:
                    # All fish cooked
                    title = "🔥  COOKING COMPLETE  🔥"
                    title_color = Colors.BRIGHT_GREEN
                    print(colorize("=" * 60, Colors.BRIGHT_GREEN))
                    print(colorize(title, title_color + Colors.BOLD))
                    print(colorize("=" * 60, Colors.MAGENTA))
                
                if successes > 0:
                    cooked_name = COOKED_FISH_ITEMS[cooked_fish_key]['name']
                    heal_amount = COOKED_FISH_ITEMS[cooked_fish_key]['heal']
                    print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(f'Cooked {successes}x {cooked_name}!', Colors.BRIGHT_GREEN)}")
                    print(f"{colorize('   Heals:', Colors.WHITE)} {heal_amount} HP each")
                
                if burns > 0:
                    print(f"\n{colorize('💨', Colors.BRIGHT_RED)} {colorize(f'Burnt {burns}x fish…', Colors.WHITE)}")
                
                if total_xp > 0:
                    print(f"{colorize('Total XP Gained:', Colors.BRIGHT_MAGENTA)} {colorize(f'+{total_xp} Cooking XP', Colors.BRIGHT_GREEN)}")
                
                if not DEV_FLAGS['quiet'] and (successes + burns) > 1:
                    show_notification(f"Cooking Summary: {successes + burns} attempted — {successes} cooked, {burns} burnt | +{total_xp} XP", Colors.BRIGHT_MAGENTA, 1.5)
                
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
            else:
                print(f"\n{colorize('❌ Invalid choice!', Colors.BRIGHT_RED)}")
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
        except ValueError:
            print(f"\n{colorize('❌ Invalid choice!', Colors.BRIGHT_RED)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")

