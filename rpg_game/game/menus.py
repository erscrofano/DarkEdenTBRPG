"""Game menus"""
from ..ui import Colors, colorize, clear_screen
from ..models.location import LOCATIONS
from ..items import get_item_quantity, format_item_name, add_item_to_inventory
from ..achievements.system import ALL_ACHIEVEMENTS


def town_menu(player):
    """Legacy function - redirects to Eslania City"""
    return eslania_city_menu(player)


def view_achievements(player):
    """View all achievements (locked and unlocked)"""
    clear_screen()
    print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
    print(colorize("🏆  ACHIEVEMENTS  🏆", Colors.BRIGHT_MAGENTA + Colors.BOLD))
    print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
    
    # Ensure achievements list exists (backwards compatibility)
    if not hasattr(player, 'achievements') or player.achievements is None:
        player.achievements = []
    
    unlocked_count = len(player.achievements)
    total_count = len(ALL_ACHIEVEMENTS)
    
    print(f"\n{colorize(f'Progress: {unlocked_count}/{total_count}', Colors.BRIGHT_YELLOW + Colors.BOLD)}")
    print(colorize("─" * 60, Colors.BRIGHT_MAGENTA))
    
    # Get current progress values for display (with defaults for backwards compatibility)
    current_level = player.level
    current_kills = getattr(player, 'total_kills', 0)
    current_streak = getattr(player, 'kill_streak', 0)
    current_tower_floor = getattr(player, 'highest_tower_floor', 0)
    
    # Get skill levels for progress display
    fishing_level = getattr(player, 'fishing_level', 1)
    cooking_level = getattr(player, 'cooking_level', 1)
    mining_level = getattr(player, 'mining_level', 1)
    
    # Group achievements by type for better organization
    achievement_types = {
        'Level Achievements': [k for k, v in ALL_ACHIEVEMENTS.items() if v['type'] == 'level'],
        'Kill Achievements': [k for k, v in ALL_ACHIEVEMENTS.items() if v['type'] == 'kills'],
        'Streak Achievements': [k for k, v in ALL_ACHIEVEMENTS.items() if v['type'] == 'streak'],
        'Item Achievements': [k for k, v in ALL_ACHIEVEMENTS.items() if v['type'] == 'rare_drop'],
        'Talisman Achievements': [k for k, v in ALL_ACHIEVEMENTS.items() if v['type'] in ['talisman_found', 'talisman_count', 'talisman_hacker']],
        'Tower Achievements': [k for k, v in ALL_ACHIEVEMENTS.items() if v['type'] == 'tower'],
        'Fishing Achievements': [k for k, v in ALL_ACHIEVEMENTS.items() if v['type'] == 'fishing_level'],
        'Cooking Achievements': [k for k, v in ALL_ACHIEVEMENTS.items() if v['type'] == 'cooking_level'],
        'Mining Achievements': [k for k, v in ALL_ACHIEVEMENTS.items() if v['type'] == 'mining_level'],
        'Skill Milestones': [k for k, v in ALL_ACHIEVEMENTS.items() if v['type'] in ['first_catch', 'first_cook', 'first_mine', 'masterpiece']],
        'Wealth Achievements': [k for k, v in ALL_ACHIEVEMENTS.items() if v['type'] == 'wealth'],
        'Equipment Achievements': [k for k, v in ALL_ACHIEVEMENTS.items() if v['type'] == 'gear_tier']
    }
    
    for category, ach_keys in achievement_types.items():
        print(f"\n{colorize(category.upper() + ':', Colors.BRIGHT_WHITE + Colors.BOLD)}")
        for ach_key in ach_keys:
            ach_data = ALL_ACHIEVEMENTS[ach_key]
            is_unlocked = ach_key in player.achievements
            
            if is_unlocked:
                status_icon = colorize('✓', Colors.BRIGHT_GREEN)
                status_text = colorize(ach_data['description'], Colors.BRIGHT_GREEN)
                reward_text = colorize(f'[+{ach_data["gold_reward"]}g]', Colors.BRIGHT_YELLOW)
                print(f"  {status_icon} {status_text} {reward_text}")
            else:
                status_icon = colorize('○', Colors.WHITE)
                # Show progress for locked achievements
                progress_text = ""
                if ach_data['type'] == 'level':
                    progress = f"{current_level}/{ach_data['requirement']}"
                    progress_text = colorize(f" ({progress})", Colors.YELLOW)
                elif ach_data['type'] == 'kills':
                    progress = f"{current_kills}/{ach_data['requirement']}"
                    progress_text = colorize(f" ({progress})", Colors.YELLOW)
                elif ach_data['type'] == 'streak':
                    # Show current streak progress
                    if current_streak > 0:
                        progress = f"Current: {current_streak}/{ach_data['requirement']}"
                    else:
                        progress = f"0/{ach_data['requirement']}"
                    progress_text = colorize(f" ({progress})", Colors.YELLOW)
                elif ach_data['type'] == 'tower':
                    progress = f"{current_tower_floor}/{ach_data['requirement']}"
                    progress_text = colorize(f" ({progress})", Colors.YELLOW)
                elif ach_data['type'] == 'fishing_level':
                    progress = f"{fishing_level}/{ach_data['requirement']}"
                    progress_text = colorize(f" ({progress})", Colors.YELLOW)
                elif ach_data['type'] == 'cooking_level':
                    progress = f"{cooking_level}/{ach_data['requirement']}"
                    progress_text = colorize(f" ({progress})", Colors.YELLOW)
                elif ach_data['type'] == 'mining_level':
                    progress = f"{mining_level}/{ach_data['requirement']}"
                    progress_text = colorize(f" ({progress})", Colors.YELLOW)
                elif ach_data['type'] == 'wealth':
                    progress = f"{player.gold:,}/{ach_data['requirement']:,}"
                    progress_text = colorize(f" ({progress})", Colors.YELLOW)
                elif ach_data['type'] == 'gear_tier':
                    max_grade = 0
                    if player.weapon and 'grade' in player.weapon:
                        max_grade = max(max_grade, player.weapon['grade'])
                    if player.armor and 'grade' in player.armor:
                        max_grade = max(max_grade, player.armor['grade'])
                    progress = f"{max_grade}/{ach_data['requirement']}"
                    progress_text = colorize(f" ({progress})", Colors.YELLOW)
                elif ach_data['type'] == 'talisman_count':
                    talisman_count = sum(1 for item in player.inventory if item.get('type') == 'talisman')
                    progress = f"{talisman_count}/{ach_data['requirement']}"
                    progress_text = colorize(f" ({progress})", Colors.YELLOW)
                elif ach_data['type'] in ['rare_drop', 'talisman_found', 'talisman_hacker', 'first_catch', 'first_cook', 'first_mine', 'masterpiece']:
                    # Event-based achievements, no progress to show
                    progress_text = ""
                
                locked_text = colorize(ach_data['description'], Colors.WHITE)
                reward_text = colorize(f'[+{ach_data["gold_reward"]}g]', Colors.WHITE)
                print(f"  {status_icon} {locked_text}{progress_text} {reward_text}")
    
    print(colorize("\n" + "=" * 60, Colors.BRIGHT_MAGENTA))
    input(f"\n{colorize('Press Enter to continue...', Colors.BRIGHT_CYAN)}")


def view_inventory(player):
    while True:
        clear_screen()
        print(colorize("=" * 50, Colors.CYAN))
        print(colorize("🎒 INVENTORY", Colors.BRIGHT_CYAN + Colors.BOLD))
        print(colorize("=" * 50, Colors.CYAN))
        
        # Show equipped items
        print("\n" + colorize("EQUIPPED:", Colors.BRIGHT_WHITE + Colors.BOLD))
        if player.weapon:
            print(f"{colorize('⚔️ Weapon:', Colors.WHITE)} {colorize(player.weapon['name'], Colors.BRIGHT_GREEN)} (+{colorize(str(player.weapon['attack']), Colors.BRIGHT_YELLOW)} Attack)")
        else:
            print(f"{colorize('⚔️ Weapon:', Colors.WHITE)} {colorize('None', Colors.WHITE)}")
        
        if player.armor:
            print(f"{colorize('🛡️ Armor:', Colors.WHITE)} {colorize(player.armor['name'], Colors.BRIGHT_BLUE)} (+{colorize(str(player.armor['defense']), Colors.BRIGHT_YELLOW)} Defense)")
        else:
            print(f"{colorize('🛡️ Armor:', Colors.WHITE)} {colorize('None', Colors.WHITE)}")
        
        # Get equippable items from inventory
        equippable_items = []
        for item in player.inventory:
            if item.get('type') == 'weapon' or item.get('type') == 'armor':
                equippable_items.append(item)
        
        # Show all inventory items
        print(f"\n{colorize('INVENTORY ITEMS:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
        print(colorize("─" * 60, Colors.CYAN))
        if player.inventory:
            # Group items by name and type for display
            item_display = []
            item_index_map = []  # Maps display index to actual inventory items
            
            for i, item in enumerate(player.inventory):
                item_type = item.get('type', 'unknown')
                name = item.get('name', 'Unknown')
                qty = get_item_quantity(item)
                
                # Use rarity-formatted name (OSRS-style)
                formatted_name = format_item_name(item)
                
                # Show quantity if > 1
                if qty > 1:
                    display_text = f"  {formatted_name} {colorize(f'x{qty}', Colors.BRIGHT_WHITE + Colors.BOLD)}"
                else:
                    display_text = f"  {formatted_name}"
                
                if item_type == 'weapon':
                    attack_val = item.get('attack', 0)
                    attack_text = f"(+{attack_val} Attack)"
                    display_text += f" {colorize('[WEAPON]', Colors.BRIGHT_GREEN)} {colorize(attack_text, Colors.BRIGHT_YELLOW)}"
                elif item_type == 'armor':
                    defense_val = item.get('defense', 0)
                    defense_text = f"(+{defense_val} Defense)"
                    display_text += f" {colorize('[ARMOR]', Colors.BRIGHT_BLUE)} {colorize(defense_text, Colors.BRIGHT_YELLOW)}"
                elif item_type == 'consumable':
                    heal_amount = item.get('heal', 0)
                    if heal_amount > 0:
                        heal_text = f"(Heals {heal_amount} HP)"
                        display_text += f" {colorize('[CONSUMABLE]', Colors.BRIGHT_YELLOW)} {colorize(heal_text, Colors.BRIGHT_GREEN)}"
                    else:
                        display_text += f" {colorize('[CONSUMABLE]', Colors.BRIGHT_YELLOW)}"
                elif item_type == 'material':
                    display_text += f" {colorize('[MATERIAL]', Colors.WHITE)}"
                
                # Show sell value
                if 'sell_value' in item:
                    sell_val = item['sell_value']
                    if qty > 1:
                        total_val = sell_val * qty
                        display_text += f" {colorize(f'({sell_val}g each, {total_val}g total)', Colors.YELLOW)}"
                    else:
                        display_text += f" {colorize(f'({sell_val}g)', Colors.YELLOW)}"
                
                item_display.append(display_text)
                item_index_map.append(i)
            
            for display_text in item_display:
                print(display_text)
        else:
            print(f"  {colorize('(Empty)', Colors.WHITE)}")
        
        print(colorize("\n" + "=" * 60, Colors.CYAN))
        print(f"  {colorize('1.', Colors.BRIGHT_GREEN)} Equip Item")
        print(f"  {colorize('2.', Colors.BRIGHT_BLUE)} Back")
        print(colorize("=" * 60, Colors.CYAN))
        
        choice = input(f"\n{colorize('What would you like to do?', Colors.BRIGHT_CYAN)} ").strip()
        
        if choice == '1':
            # Equip menu
            if not equippable_items:
                no_items_msg = "You don't have any equippable items in your inventory!"
                print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(no_items_msg, Colors.WHITE)}")
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                continue
            
            clear_screen()
            print(colorize("=" * 60, Colors.CYAN))
            print(colorize("⚔️  EQUIP ITEM  ⚔️", Colors.BRIGHT_CYAN + Colors.BOLD))
            print(colorize("=" * 60, Colors.CYAN))
            print(f"\n{colorize('SELECT AN ITEM TO EQUIP:', Colors.BRIGHT_WHITE + Colors.BOLD)}\n")
            
            # Show only equippable items
            for i, item in enumerate(equippable_items, 1):
                item_type = item.get('type', 'unknown')
                formatted_name = format_item_name(item)
                display_text = f"  {colorize(str(i) + '.', Colors.WHITE)} {formatted_name}"
                if item_type == 'weapon':
                    attack_val = item.get('attack', 0)
                    display_text += f" {colorize('[WEAPON]', Colors.BRIGHT_GREEN)} {colorize(f'(+{attack_val} Attack)', Colors.BRIGHT_YELLOW)}"
                elif item_type == 'armor':
                    defense_val = item.get('defense', 0)
                    display_text += f" {colorize('[ARMOR]', Colors.BRIGHT_BLUE)} {colorize(f'(+{defense_val} Defense)', Colors.BRIGHT_YELLOW)}"
                print(display_text)
            
            print(f"\n  {colorize(str(len(equippable_items) + 1) + '.', Colors.BRIGHT_BLUE)} Back")
            print(colorize("=" * 60, Colors.CYAN))
            
            equip_choice = input(f"\n{colorize('What would you like to equip?', Colors.BRIGHT_CYAN)} ").strip()
            
            try:
                equip_num = int(equip_choice)
                if equip_num == len(equippable_items) + 1:
                    continue
                
                if 1 <= equip_num <= len(equippable_items):
                    item_to_equip = equippable_items[equip_num - 1]
                    item_type = item_to_equip.get('type')
                    
                    # Remove item from inventory first
                    player.inventory.remove(item_to_equip)
                    
                    if item_type == 'weapon':
                        # Handle weapon swapping
                        if player.weapon:
                            old_weapon = player.weapon.copy()
                            add_item_to_inventory(player.inventory, old_weapon)
                            unequip_msg = f"Unequipped {old_weapon['name']}"
                            print(f"\n{colorize('🔄', Colors.BRIGHT_BLUE)} {colorize(unequip_msg, Colors.WHITE)}")
                        
                        player.weapon = item_to_equip.copy()
                        equip_msg = f"Equipped {item_to_equip['name']}!"
                        print(f"{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(equip_msg, Colors.BRIGHT_GREEN)}")
                    
                    elif item_type == 'armor':
                        # Handle armor swapping
                        if player.armor:
                            old_armor = player.armor.copy()
                            add_item_to_inventory(player.inventory, old_armor)
                            unequip_msg = f"Unequipped {old_armor['name']}"
                            print(f"\n{colorize('🔄', Colors.BRIGHT_BLUE)} {colorize(unequip_msg, Colors.WHITE)}")
                        
                        player.armor = item_to_equip.copy()
                        equip_msg = f"Equipped {item_to_equip['name']}!"
                        print(f"{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(equip_msg, Colors.BRIGHT_GREEN)}")
                    
                    input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                else:
                    print(f"\n{colorize('❌ Invalid choice!', Colors.BRIGHT_RED)}")
                    input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
            except ValueError:
                print(f"\n{colorize('❌ Invalid choice!', Colors.BRIGHT_RED)}")
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
        
        elif choice == '2':
            return
        else:
            print(f"\n{colorize('❌ Invalid choice!', Colors.BRIGHT_RED)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")


def locations_menu(player):
    """Menu for traveling between major locations and dungeons"""
    clear_screen()
    print(colorize("=" * 60, Colors.BRIGHT_CYAN))
    print(colorize("🗺️  TRAVEL  🗺️", Colors.BRIGHT_CYAN + Colors.BOLD))
    print(colorize("=" * 60, Colors.BRIGHT_CYAN))
    print(f"\n{colorize('Where would you like to travel?', Colors.WHITE)}")
    print(f"{colorize('Travel costs 5,000 gold (free for local areas)', Colors.YELLOW)}")
    print(f"\n{colorize(f'Level: {player.level} | Gold: {player.gold} | HP: {player.hp}/{player.max_hp}', Colors.BRIGHT_YELLOW)}")
    
    # Determine current location and local areas
    current_loc = player.current_location
    is_eslania = current_loc == 'eslania_city'
    is_perona = current_loc == 'perona_outpost'
    
    print("\n" + colorize("=" * 60, Colors.BRIGHT_CYAN))
    print(f"\n{colorize('CITIES:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
    if is_eslania:
        print(f"  {colorize('1.', Colors.GRAY)} Eslania City {colorize('(You are already here)', Colors.GRAY)}")
    else:
        print(f"  {colorize('1.', Colors.WHITE)} Eslania City {colorize('- 5,000g', Colors.YELLOW)}")
    
    if is_perona:
        print(f"  {colorize('2.', Colors.GRAY)} Perona Outpost {colorize('(You are already here)', Colors.GRAY)}")
    else:
        print(f"  {colorize('2.', Colors.WHITE)} Perona Outpost {colorize('- 5,000g', Colors.YELLOW)}")
    
    print(f"\n{colorize('DUNGEONS:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
    # Limbo, Lost Taiyan, Rhaom, Tepes lair are not local to any city - always cost 5k
    print(f"  {colorize('3.', Colors.WHITE)} Limbo Dungeon {colorize('- 5,000g', Colors.YELLOW)}")
    print(f"  {colorize('4.', Colors.WHITE)} Lost Taiyan {colorize('- 5,000g', Colors.YELLOW)}")
    print(f"  {colorize('5.', Colors.WHITE)} Rhaom Dungeon {colorize('- 5,000g', Colors.YELLOW)}")
    print(f"  {colorize('6.', Colors.WHITE)} Tepes lair {colorize('- 5,000g', Colors.YELLOW)}")
    
    print(f"\n  {colorize('7.', Colors.WHITE)} Back")
    print(colorize("=" * 60, Colors.BRIGHT_CYAN))
    
    choice = input(f"\n{colorize('Where do you want to go?', Colors.BRIGHT_CYAN)} ").strip()
    return choice


def eslania_city_menu(player):
    """Eslania City main menu - merged with Town"""
    clear_screen()
    location = LOCATIONS['eslania_city']
    print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
    print(colorize(f"🏰 {location.name.upper()}", Colors.BRIGHT_YELLOW + Colors.BOLD))
    print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
    print(f"\n{colorize('A grand city with guilds, shops, and access to dangerous dungeons.', Colors.WHITE)}")
    print(f"\n{colorize(f'Level: {player.level} | Gold: {player.gold} | HP: {player.hp}/{player.max_hp}', Colors.BRIGHT_YELLOW)}")
    
    print("\n" + colorize("=" * 50, Colors.BRIGHT_YELLOW))
    print(colorize("MAIN MENU", Colors.BRIGHT_YELLOW + Colors.BOLD))
    print(colorize("=" * 50, Colors.BRIGHT_YELLOW))
    print(f"\n{colorize('GUILDS:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
    print(f"  {colorize('1.', Colors.WHITE)} Knight Guild")
    print(f"  {colorize('2.', Colors.WHITE)} Army Guild")
    print(f"  {colorize('3.', Colors.WHITE)} Cleric Guild")
    print(f"\n{colorize('SHOPS:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
    print(f"  {colorize('4.', Colors.WHITE)} General Store")
    print(f"  {colorize('5.', Colors.WHITE)} Fishing Store")
    print(f"  {colorize('6.', Colors.WHITE)} Mining Store")
    print(f"\n{colorize('SERVICES:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
    print(f"  {colorize('7.', Colors.WHITE)} Hospital")
    print(f"  {colorize('8.', Colors.WHITE)} Pimping")
    print(f"  {colorize('9.', Colors.WHITE)} Training Zone")
    print(f"  {colorize('10.', Colors.WHITE)} Kitchen")
    print(f"\n{colorize('EXPLORATION:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
    print(f"  {colorize('11.', Colors.WHITE)} Underground Waterways")
    print(f"  {colorize('12.', Colors.WHITE)} Eslania Dungeon")
    print(f"  {colorize('13.', Colors.WHITE)} Go Fishing")
    print(f"  {colorize('14.', Colors.WHITE)} Go Mining")
    print(f"  {colorize('15.', Colors.WHITE)} Travel to Another Location")
    print(f"\n{colorize('CHARACTER:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
    print(f"  {colorize('16.', Colors.WHITE)} View Stats")
    print(f"  {colorize('17.', Colors.WHITE)} View Inventory")
    print(f"  {colorize('18.', Colors.WHITE)} View Achievements {colorize(f'({len(player.achievements)} unlocked)', Colors.BRIGHT_MAGENTA)}")
    if player.stat_points > 0:
        print(f"  {colorize('19.', Colors.BRIGHT_YELLOW)} Allocate Stat Points {colorize(f'({player.stat_points} available)', Colors.BRIGHT_YELLOW + Colors.BOLD)}")
    print(f"\n{colorize('GAME:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
    if player.stat_points > 0:
        print(f"  {colorize('20.', Colors.WHITE)} Save Game")
        print(f"  {colorize('21.', Colors.WHITE)} Quit Game")
    else:
        print(f"  {colorize('19.', Colors.WHITE)} Save Game")
        print(f"  {colorize('20.', Colors.WHITE)} Quit Game")
    print(colorize("=" * 50, Colors.BRIGHT_YELLOW))
    
    choice = input(f"\n{colorize('What do you do?', Colors.BRIGHT_CYAN)} ").strip()
    return choice


def perona_outpost_menu(player):
    """Perona Outpost main menu"""
    clear_screen()
    location = LOCATIONS['perona_outpost']
    print(colorize("=" * 60, Colors.BRIGHT_BLUE))
    print(colorize(f"🏕️ {location.name.upper()}", Colors.BRIGHT_BLUE + Colors.BOLD))
    print(colorize("=" * 60, Colors.BRIGHT_BLUE))
    print(f"\n{colorize(location.description, Colors.WHITE)}")
    print(f"\n{colorize(f'Level: {player.level} | Gold: {player.gold} | HP: {player.hp}/{player.max_hp}', Colors.BRIGHT_YELLOW)}")
    
    print("\n" + colorize("=" * 50, Colors.BRIGHT_BLUE))
    print(colorize("MAIN MENU", Colors.BRIGHT_BLUE + Colors.BOLD))
    print(colorize("=" * 50, Colors.BRIGHT_BLUE))
    print(f"\n{colorize('EXPLORATION:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
    print(f"  {colorize('1.', Colors.WHITE)} Asylion Dungeon {colorize('(PvE - Level 8+)', Colors.GRAY)}")
    print(f"  {colorize('2.', Colors.WHITE)} Travel to Another Location")
    print(f"\n{colorize('CHARACTER:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
    print(f"  {colorize('3.', Colors.WHITE)} View Stats")
    print(f"  {colorize('4.', Colors.WHITE)} View Inventory")
    print(f"  {colorize('5.', Colors.WHITE)} View Achievements {colorize(f'({len(player.achievements)} unlocked)', Colors.BRIGHT_MAGENTA)}")
    if player.stat_points > 0:
        print(f"  {colorize('6.', Colors.BRIGHT_YELLOW)} Allocate Stat Points {colorize(f'({player.stat_points} available)', Colors.BRIGHT_YELLOW + Colors.BOLD)}")
    print(f"\n{colorize('GAME:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
    if player.stat_points > 0:
        print(f"  {colorize('7.', Colors.WHITE)} Save Game")
        print(f"  {colorize('8.', Colors.WHITE)} Quit Game")
    else:
        print(f"  {colorize('6.', Colors.WHITE)} Save Game")
        print(f"  {colorize('7.', Colors.WHITE)} Quit Game")
    print(colorize("=" * 50, Colors.BRIGHT_BLUE))
    
    choice = input(f"\n{colorize('What do you do?', Colors.BRIGHT_CYAN)} ").strip()
    return choice

