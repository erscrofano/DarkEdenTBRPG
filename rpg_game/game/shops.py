"""Shop menus"""
import random
from ..ui import Colors, colorize, clear_screen, health_bar, display_time_hud
from ..items import WEAPONS, SWORDS, BLADES, GUNS, CROSSES, MACES, MAGIC_WEAPONS, ARMOR_SETS, POTIONS, FISHING_RODS, PICKAXES, add_item_to_inventory, remove_item_from_inventory, get_item_quantity, format_item_name
from ..constants import MAX_QUANTITY_PER_PURCHASE, MIN_QUANTITY_PER_PURCHASE


def sell_items_menu(player, shop_name):
    """Helper function for selling items in any shop"""
    while True:
        clear_screen()
        print(colorize("=" * 60, Colors.CYAN))
        print(colorize(f"💰  SELL ITEMS  💰", Colors.BRIGHT_YELLOW + Colors.BOLD))
        print(colorize("=" * 60, Colors.CYAN))
        
        # Get sellable items (materials and items with sell_value)
        sellable_items = []
        for item in player.inventory:
            if 'sell_value' in item:
                sellable_items.append(item)
        
        # Also allow selling equipped items
        if player.weapon and 'sell_value' in player.weapon:
            sellable_items.append({'item_ref': 'weapon', 'name': player.weapon['name'], 
                                 'sell_value': player.weapon.get('sell_value', 0), 
                                 'equipped': True})
        if player.armor and 'sell_value' in player.armor:
            sellable_items.append({'item_ref': 'armor', 'name': player.armor['name'], 
                                 'sell_value': player.armor.get('sell_value', 0), 
                                 'equipped': True})
        
        if not sellable_items:
            no_items_msg = "You don't have any items to sell!"
            print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(no_items_msg, Colors.WHITE)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
            return
        
        print(f"\n{colorize('Your Items:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
        for i, item in enumerate(sellable_items, 1):
            equipped_tag = colorize(" (EQUIPPED)", Colors.BRIGHT_RED) if item.get('equipped') else ""
            qty = get_item_quantity(item)
            if qty > 1 and not item.get('equipped'):
                print(f"{i}. {item['name']} {colorize(f'x{qty}', Colors.BRIGHT_WHITE)} - {colorize(str(item['sell_value']), Colors.BRIGHT_YELLOW)} gold each ({colorize(str(item['sell_value'] * qty), Colors.BRIGHT_YELLOW)} total)")
            else:
                print(f"{i}. {item['name']}{equipped_tag} - {colorize(str(item['sell_value']), Colors.BRIGHT_YELLOW)} gold")
        
        print(f"\n{len(sellable_items) + 1}. Back")
        print(colorize("=" * 60, Colors.CYAN))
        
        choice = input(f"\n{colorize('What would you like to sell?', Colors.BRIGHT_CYAN)} ").strip()
        
        try:
            choice_num = int(choice)
            if choice_num == len(sellable_items) + 1:
                return
            
            if 1 <= choice_num <= len(sellable_items):
                item_to_sell = sellable_items[choice_num - 1]
                
                if item_to_sell.get('equipped'):
                    # Selling equipped item (no quantity selection)
                    if item_to_sell['item_ref'] == 'weapon':
                        player.gold += item_to_sell['sell_value']
                        sold_msg = f"You sold {player.weapon['name']} for {item_to_sell['sell_value']} gold!"
                        print(f"\n{colorize('💰', Colors.BRIGHT_YELLOW)} {colorize(sold_msg, Colors.WHITE)}")
                        player.weapon = None
                        # Check wealth achievements after selling
                        from ..achievements.system import check_achievements
                        check_achievements(player, 'wealth')
                    elif item_to_sell['item_ref'] == 'armor':
                        player.gold += item_to_sell['sell_value']
                        sold_msg = f"You sold {player.armor['name']} for {item_to_sell['sell_value']} gold!"
                        print(f"\n{colorize('💰', Colors.BRIGHT_YELLOW)} {colorize(sold_msg, Colors.WHITE)}")
                        player.armor = None
                        # Check wealth achievements after selling
                        from ..achievements.system import check_achievements
                        check_achievements(player, 'wealth')
                else:
                    # Selling inventory item - handle quantity
                    item_qty = get_item_quantity(item_to_sell)
                    sell_qty = 1
                    
                    if item_qty > 1:
                        # Show quantity selection menu
                        clear_screen()
                        print(colorize("=" * 60, Colors.CYAN))
                        print(colorize("💰  SELL ITEMS  💰", Colors.BRIGHT_YELLOW + Colors.BOLD))
                        print(colorize("=" * 60, Colors.CYAN))
                        formatted_name = format_item_name(item_to_sell)
                        print(f"\n{colorize('Item:', Colors.WHITE)} {formatted_name}")
                        print(f"{colorize('Sell Value:', Colors.WHITE)} {colorize(str(item_to_sell['sell_value']), Colors.BRIGHT_YELLOW)} gold each")
                        print(f"{colorize('Quantity Available:', Colors.WHITE)} {colorize(str(item_qty), Colors.BRIGHT_YELLOW)}")
                        print(f"\n{colorize('How many to sell?', Colors.BRIGHT_CYAN)}")
                        print(f"  {colorize('1.', Colors.WHITE)} Sell 1")
                        if item_qty >= 5:
                            print(f"  {colorize('2.', Colors.WHITE)} Sell 5")
                        if item_qty >= 10:
                            print(f"  {colorize('3.', Colors.WHITE)} Sell 10")
                        print(f"  {colorize('4.', Colors.WHITE)} Sell All ({item_qty})")
                        print(f"  {colorize('5.', Colors.WHITE)} Cancel")
                        print(colorize("=" * 60, Colors.CYAN))
                        
                        qty_choice = input(f"\n{colorize('Choice:', Colors.BRIGHT_CYAN)} ").strip()
                        if qty_choice == '1':
                            sell_qty = 1
                        elif qty_choice == '2' and item_qty >= 5:
                            sell_qty = min(5, item_qty)
                        elif qty_choice == '3' and item_qty >= 10:
                            sell_qty = min(10, item_qty)
                        elif qty_choice == '4':
                            sell_qty = item_qty
                        else:
                            continue  # Cancel
                    
                    # Perform sale
                    total_value = item_to_sell['sell_value'] * sell_qty
                    player.gold += total_value
                    remove_item_from_inventory(player.inventory, item_to_sell, sell_qty)
                    
                    if sell_qty > 1:
                        sold_msg = f"You sold {sell_qty}x {item_to_sell['name']} for {total_value} gold!"
                    else:
                        sold_msg = f"You sold {item_to_sell['name']} for {total_value} gold!"
                    print(f"\n{colorize('💰', Colors.BRIGHT_YELLOW)} {colorize(sold_msg, Colors.WHITE)}")
                    
                    # Check wealth achievements after selling
                    from ..achievements.system import check_achievements
                    check_achievements(player, 'wealth')
                
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
            else:
                print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Invalid choice!', Colors.WHITE)}")
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
        except ValueError:
            print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Invalid choice!', Colors.WHITE)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")


def weapon_shop(player):
    """Legacy weapon shop - redirects to Knight Guild"""
    knight_guild(player)


def armor_shop(player):
    """Legacy armor shop - redirects to Knight Guild"""
    knight_guild(player)


def _buy_weapon_from_list(player, weapons_dict, weapon_type_name):
    """Helper function to buy weapons from a dictionary with level requirements"""
    weapons_list = list(weapons_dict.items())
    for i, (key, weapon) in enumerate(weapons_list, 1):
        grade_color = Colors.WHITE
        if weapon['grade'] >= 50:
            grade_color = Colors.BRIGHT_MAGENTA
        elif weapon['grade'] >= 30:
            grade_color = Colors.BRIGHT_CYAN
        elif weapon['grade'] >= 20:
            grade_color = Colors.BRIGHT_GREEN
        
        grade_text = f"G{weapon['grade']}"
        
        # Check level requirement
        level_req = weapon.get('level_req', weapon.get('grade', 0))
        level_met = player.level >= level_req
        level_color = Colors.BRIGHT_GREEN if level_met else Colors.RED
        
        # Display weapon info
        if level_met:
            print(f"  {colorize(str(i) + '.', Colors.WHITE)} {colorize(weapon['name'], grade_color)} {colorize('(' + grade_text + ')', Colors.WHITE)}")
            print(f"     {colorize('Attack:', Colors.YELLOW)} {colorize('+' + str(weapon['attack']), Colors.BRIGHT_YELLOW)} | {colorize('Cost:', Colors.BRIGHT_YELLOW)} {colorize(str(weapon['cost']) + 'g', Colors.BRIGHT_YELLOW)}")
        else:
            print(f"  {colorize(str(i) + '.', Colors.GRAY)} {colorize(weapon['name'], Colors.GRAY)} {colorize('(' + grade_text + ')', Colors.GRAY)}")
            print(f"     {colorize('Level Required:', Colors.RED)} {colorize(str(level_req), Colors.RED)}")
    
    print(f"\n  {colorize(str(len(weapons_list) + 1) + '.', Colors.BRIGHT_BLUE)} Back")
    print(colorize("=" * 60, Colors.CYAN))
    
    choice = input(f"\n{colorize('What would you like to buy?', Colors.BRIGHT_CYAN)} ").strip()
    
    try:
        choice_num = int(choice)
        if choice_num == len(weapons_list) + 1:
            return False
        
        if 1 <= choice_num <= len(weapons_list):
            weapon_key, weapon = weapons_list[choice_num - 1]
            
            # Check level requirement
            level_req = weapon.get('level_req', weapon.get('grade', 0))
            if player.level < level_req:
                level_msg = f"You need to be level {level_req} to use this weapon!"
                print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(level_msg, Colors.WHITE)}")
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                return False
            
            if player.gold >= weapon['cost']:
                player.gold -= weapon['cost']
                
                # Handle weapon swapping
                if player.weapon:
                    old_weapon = player.weapon.copy()
                    add_item_to_inventory(player.inventory, old_weapon)
                    unequip_msg = f"Unequipped {old_weapon['name']}"
                    print(f"\n{colorize('🔄', Colors.BRIGHT_BLUE)} {colorize(unequip_msg, Colors.WHITE)}")
                
                player.weapon = weapon.copy()
                equip_msg = f"Equipped {weapon['name']}!"
                print(f"{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(equip_msg, Colors.BRIGHT_GREEN)}")
                
                # Check gear tier achievements
                from ..achievements.system import check_achievements
                check_achievements(player, 'gear_tier')
                
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                return True
            else:
                no_gold_msg = "You don't have enough gold!"
                print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(no_gold_msg, Colors.WHITE)}")
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                return False
        else:
            print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Invalid choice!', Colors.WHITE)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
            return False
    except ValueError:
        print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Invalid choice!', Colors.WHITE)}")
        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
        return False


def _buy_armor_from_list(player):
    """Helper function to buy armor from ARMOR_SETS dictionary"""
    armor_list = list(ARMOR_SETS.items())
    for i, (key, armor) in enumerate(armor_list, 1):
        grade_color = Colors.WHITE
        if armor['grade'] >= 50:
            grade_color = Colors.BRIGHT_MAGENTA
        elif armor['grade'] >= 30:
            grade_color = Colors.BRIGHT_CYAN
        elif armor['grade'] >= 20:
            grade_color = Colors.BRIGHT_GREEN
        
        grade_text = f"G{armor['grade']}"
        print(f"  {colorize(str(i) + '.', Colors.WHITE)} {colorize(armor['name'], grade_color)} {colorize('(' + grade_text + ')', Colors.WHITE)}")
        print(f"     {colorize('Defense:', Colors.BLUE)} {colorize('+' + str(armor['defense']), Colors.BRIGHT_BLUE)} | {colorize('Cost:', Colors.BRIGHT_YELLOW)} {colorize(str(armor['cost']) + 'g', Colors.BRIGHT_YELLOW)}")
    
    print(f"\n  {colorize(str(len(armor_list) + 1) + '.', Colors.BRIGHT_BLUE)} Back")
    print(colorize("=" * 60, Colors.CYAN))
    
    choice = input(f"\n{colorize('What would you like to buy?', Colors.BRIGHT_CYAN)} ").strip()
    
    try:
        choice_num = int(choice)
        if choice_num == len(armor_list) + 1:
            return False
        
        if 1 <= choice_num <= len(armor_list):
            armor_key, armor = armor_list[choice_num - 1]
            
            if player.gold >= armor['cost']:
                player.gold -= armor['cost']
                
                # Handle armor swapping
                if player.armor:
                    old_armor = player.armor.copy()
                    add_item_to_inventory(player.inventory, old_armor)
                    unequip_msg = f"Unequipped {old_armor['name']}"
                    print(f"\n{colorize('🔄', Colors.BRIGHT_BLUE)} {colorize(unequip_msg, Colors.WHITE)}")
                
                player.armor = armor.copy()
                equip_msg = f"Equipped {armor['name']}!"
                print(f"{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(equip_msg, Colors.BRIGHT_GREEN)}")
                
                # Check gear tier achievements
                from ..achievements.system import check_achievements
                check_achievements(player, 'gear_tier')
                
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                return True
            else:
                no_gold_msg = "You don't have enough gold!"
                print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(no_gold_msg, Colors.WHITE)}")
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                return False
        else:
            print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Invalid choice!', Colors.WHITE)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
            return False
    except ValueError:
        print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Invalid choice!', Colors.WHITE)}")
        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
        return False


def knight_guild(player):
    """Knight Guild - sells swords, blades, and armor"""
    while True:
        clear_screen()
        display_time_hud(player)  # Real-time clock display
        print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
        print(colorize("⚔️  KNIGHT GUILD  ⚔️", Colors.BRIGHT_YELLOW + Colors.BOLD))
        print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
        print(f"\n{colorize('The honored Knight Guild, home of swords, blades, and valor.', Colors.WHITE)}")
        print(f"\n{colorize(f'Your Gold: {player.gold}', Colors.BRIGHT_YELLOW + Colors.BOLD)}")
        print(colorize("─" * 60, Colors.BRIGHT_YELLOW))
        print(f"\n{colorize('SHOP MENU:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
        print(f"  {colorize('1.', Colors.BRIGHT_GREEN)} Sword Shop")
        print(f"  {colorize('2.', Colors.BRIGHT_GREEN)} Blade Shop")
        print(f"  {colorize('3.', Colors.BRIGHT_BLUE)} Buy Armor")
        print(f"  {colorize('4.', Colors.BRIGHT_YELLOW)} Sell Items")
        print(f"  {colorize('5.', Colors.BRIGHT_BLUE)} Exit")
        print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
        
        menu_choice = input(f"\n{colorize('What would you like to do?', Colors.BRIGHT_CYAN)} ").strip()
        
        if menu_choice == '1':
            clear_screen()
            print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
            print(colorize("⚔️  SWORD SHOP  ⚔️", Colors.BRIGHT_YELLOW + Colors.BOLD))
            print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
            print(f"\n{colorize(f'Your Gold: {player.gold}', Colors.BRIGHT_YELLOW + Colors.BOLD)}")
            print(colorize("─" * 60, Colors.BRIGHT_YELLOW))
            print(f"\n{colorize('AVAILABLE SWORDS:', Colors.BRIGHT_WHITE + Colors.BOLD)}\n")
            _buy_weapon_from_list(player, SWORDS, "Swords")
        
        elif menu_choice == '2':
            clear_screen()
            print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
            print(colorize("⚔️  BLADE SHOP  ⚔️", Colors.BRIGHT_YELLOW + Colors.BOLD))
            print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
            print(f"\n{colorize(f'Your Gold: {player.gold}', Colors.BRIGHT_YELLOW + Colors.BOLD)}")
            print(colorize("─" * 60, Colors.BRIGHT_YELLOW))
            print(f"\n{colorize('AVAILABLE BLADES:', Colors.BRIGHT_WHITE + Colors.BOLD)}\n")
            _buy_weapon_from_list(player, BLADES, "Blades")
        
        elif menu_choice == '3':
            # Buy Armor
            clear_screen()
            print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
            print(colorize("🛡️  BUY ARMOR SETS  🛡️", Colors.BRIGHT_BLUE + Colors.BOLD))
            print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
            print(f"\n{colorize(f'Your Gold: {player.gold}', Colors.BRIGHT_YELLOW + Colors.BOLD)}")
            print(colorize("─" * 60, Colors.BRIGHT_YELLOW))
            print(f"\n{colorize('AVAILABLE ARMOR SETS:', Colors.BRIGHT_WHITE + Colors.BOLD)}\n")
            _buy_armor_from_list(player)
        
        elif menu_choice == '4':
            sell_items_menu(player, "Knight Guild")
        
        elif menu_choice == '5':
            return
        else:
            print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Invalid choice!', Colors.WHITE)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")


def army_guild(player):
    """Army Guild - sells guns and armor"""
    while True:
        clear_screen()
        display_time_hud(player)  # Real-time clock display
        print(colorize("=" * 60, Colors.BRIGHT_RED))
        print(colorize("🔫  ARMY GUILD  🔫", Colors.BRIGHT_RED + Colors.BOLD))
        print(colorize("=" * 60, Colors.BRIGHT_RED))
        print(f"\n{colorize('The powerful Army Guild, home of firearms and military might.', Colors.WHITE)}")
        print(f"\n{colorize(f'Your Gold: {player.gold}', Colors.BRIGHT_YELLOW + Colors.BOLD)}")
        print(colorize("─" * 60, Colors.BRIGHT_RED))
        print(f"\n{colorize('SHOP MENU:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
        print(f"  {colorize('1.', Colors.BRIGHT_GREEN)} Buy Guns")
        print(f"  {colorize('2.', Colors.BRIGHT_BLUE)} Buy Armor")
        print(f"  {colorize('3.', Colors.BRIGHT_YELLOW)} Sell Items")
        print(f"  {colorize('4.', Colors.BRIGHT_BLUE)} Exit")
        print(colorize("=" * 60, Colors.BRIGHT_RED))
        
        menu_choice = input(f"\n{colorize('What would you like to do?', Colors.BRIGHT_CYAN)} ").strip()
        
        if menu_choice == '1':
            clear_screen()
            print(colorize("=" * 60, Colors.BRIGHT_RED))
            print(colorize("🔫  BUY GUNS  🔫", Colors.BRIGHT_RED + Colors.BOLD))
            print(colorize("=" * 60, Colors.BRIGHT_RED))
            print(f"\n{colorize(f'Your Gold: {player.gold}', Colors.BRIGHT_YELLOW + Colors.BOLD)}")
            print(colorize("─" * 60, Colors.BRIGHT_RED))
            print(f"\n{colorize('AVAILABLE GUNS:', Colors.BRIGHT_WHITE + Colors.BOLD)}\n")
            _buy_weapon_from_list(player, GUNS, "Guns")
        
        elif menu_choice == '2':
            # Buy Armor
            clear_screen()
            print(colorize("=" * 60, Colors.BRIGHT_RED))
            print(colorize("🛡️  BUY ARMOR SETS  🛡️", Colors.BRIGHT_BLUE + Colors.BOLD))
            print(colorize("=" * 60, Colors.BRIGHT_RED))
            print(f"\n{colorize(f'Your Gold: {player.gold}', Colors.BRIGHT_YELLOW + Colors.BOLD)}")
            print(colorize("─" * 60, Colors.BRIGHT_RED))
            print(f"\n{colorize('AVAILABLE ARMOR SETS:', Colors.BRIGHT_WHITE + Colors.BOLD)}\n")
            _buy_armor_from_list(player)
        
        elif menu_choice == '3':
            sell_items_menu(player, "Army Guild")
        
        elif menu_choice == '4':
            return
        else:
            print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Invalid choice!', Colors.WHITE)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")


def cleric_guild(player):
    """Cleric Guild - sells crosses, maces, and armor"""
    while True:
        clear_screen()
        display_time_hud(player)  # Real-time clock display
        print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
        print(colorize("✨  CLERIC GUILD  ✨", Colors.BRIGHT_MAGENTA + Colors.BOLD))
        print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
        print(f"\n{colorize('The sacred Cleric Guild, home of blessed weapons and divine protection.', Colors.WHITE)}")
        print(f"\n{colorize(f'Your Gold: {player.gold}', Colors.BRIGHT_YELLOW + Colors.BOLD)}")
        print(colorize("─" * 60, Colors.BRIGHT_MAGENTA))
        print(f"\n{colorize('SHOP MENU:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
        print(f"  {colorize('1.', Colors.BRIGHT_GREEN)} Cross Shop")
        print(f"  {colorize('2.', Colors.BRIGHT_GREEN)} Mace Shop")
        print(f"  {colorize('3.', Colors.BRIGHT_BLUE)} Buy Armor")
        print(f"  {colorize('4.', Colors.BRIGHT_YELLOW)} Sell Items")
        print(f"  {colorize('5.', Colors.BRIGHT_BLUE)} Exit")
        print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
        
        menu_choice = input(f"\n{colorize('What would you like to do?', Colors.BRIGHT_CYAN)} ").strip()
        
        if menu_choice == '1':
            clear_screen()
            print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
            print(colorize("✨  CROSS SHOP  ✨", Colors.BRIGHT_MAGENTA + Colors.BOLD))
            print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
            print(f"\n{colorize(f'Your Gold: {player.gold}', Colors.BRIGHT_YELLOW + Colors.BOLD)}")
            print(colorize("─" * 60, Colors.BRIGHT_MAGENTA))
            print(f"\n{colorize('AVAILABLE CROSSES:', Colors.BRIGHT_WHITE + Colors.BOLD)}\n")
            _buy_weapon_from_list(player, CROSSES, "Crosses")
        
        elif menu_choice == '2':
            clear_screen()
            print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
            print(colorize("✨  MACE SHOP  ✨", Colors.BRIGHT_MAGENTA + Colors.BOLD))
            print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
            print(f"\n{colorize(f'Your Gold: {player.gold}', Colors.BRIGHT_YELLOW + Colors.BOLD)}")
            print(colorize("─" * 60, Colors.BRIGHT_MAGENTA))
            print(f"\n{colorize('AVAILABLE MACES:', Colors.BRIGHT_WHITE + Colors.BOLD)}\n")
            _buy_weapon_from_list(player, MACES, "Maces")
        
        elif menu_choice == '3':
            # Buy Armor
            clear_screen()
            print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
            print(colorize("🛡️  BUY ARMOR SETS  🛡️", Colors.BRIGHT_BLUE + Colors.BOLD))
            print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
            print(f"\n{colorize(f'Your Gold: {player.gold}', Colors.BRIGHT_YELLOW + Colors.BOLD)}")
            print(colorize("─" * 60, Colors.BRIGHT_MAGENTA))
            print(f"\n{colorize('AVAILABLE ARMOR SETS:', Colors.BRIGHT_WHITE + Colors.BOLD)}\n")
            _buy_armor_from_list(player)
        
        elif menu_choice == '4':
            sell_items_menu(player, "Cleric Guild")
        
        elif menu_choice == '5':
            return
        else:
            print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Invalid choice!', Colors.WHITE)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")


def general_store(player):
    """General Store - buy general items, sell anything for coins"""
    while True:
        clear_screen()
        display_time_hud(player)  # Real-time clock display
        print(colorize("=" * 60, Colors.BRIGHT_GREEN))
        print(colorize("🏪  GENERAL STORE  🏪", Colors.BRIGHT_GREEN + Colors.BOLD))
        print(colorize("=" * 60, Colors.BRIGHT_GREEN))
        print(f"\n{colorize('A general store where you can buy supplies and sell anything.', Colors.WHITE)}")
        print(f"\n{colorize(f'Your Gold: {player.gold}', Colors.BRIGHT_YELLOW + Colors.BOLD)}")
        print(colorize("─" * 60, Colors.BRIGHT_GREEN))
        print(f"\n{colorize('SHOP MENU:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
        print(f"  {colorize('1.', Colors.BRIGHT_GREEN)} Buy Items")
        print(f"  {colorize('2.', Colors.BRIGHT_YELLOW)} Sell Items")
        print(f"  {colorize('3.', Colors.BRIGHT_BLUE)} Exit")
        print(colorize("=" * 60, Colors.BRIGHT_GREEN))
        
        menu_choice = input(f"\n{colorize('What would you like to do?', Colors.BRIGHT_CYAN)} ").strip()
        
        if menu_choice == '1':
            # Buy potions, fishing rods, and other general items
            clear_screen()
            print(colorize("=" * 60, Colors.BRIGHT_GREEN))
            print(colorize("🏪  BUY ITEMS  🏪", Colors.BRIGHT_GREEN + Colors.BOLD))
            print(colorize("=" * 60, Colors.BRIGHT_GREEN))
            print(f"\n{colorize(f'Your Gold: {player.gold}', Colors.BRIGHT_YELLOW + Colors.BOLD)}")
            print(colorize("─" * 60, Colors.BRIGHT_GREEN))
            print(f"\n{colorize('AVAILABLE ITEMS:', Colors.BRIGHT_WHITE + Colors.BOLD)}\n")
            
            # Only potions in general store now
            items_list = []
            item_display_info = []
            
            # Add potions
            for key, potion in POTIONS.items():
                items_list.append(('potion', key, potion))
                item_display_info.append({
                    'name': potion['name'],
                    'info': f"{colorize('Heals:', Colors.BRIGHT_GREEN)} {colorize(str(potion['heal']) + ' HP', Colors.BRIGHT_GREEN)}",
                    'cost': potion['cost']
                })
            
            # Display items
            for i, display in enumerate(item_display_info, 1):
                print(f"  {colorize(str(i) + '.', Colors.WHITE)} {colorize(display['name'], Colors.BRIGHT_GREEN)}")
                print(f"     {display['info']} | {colorize('Cost:', Colors.BRIGHT_YELLOW)} {colorize(str(display['cost']) + 'g', Colors.BRIGHT_YELLOW)}")
            
            print(f"\n  {colorize(str(len(items_list) + 1) + '.', Colors.BRIGHT_BLUE)} Back")
            print(colorize("=" * 60, Colors.BRIGHT_GREEN))
            
            choice = input(f"\n{colorize('What would you like to buy?', Colors.BRIGHT_CYAN)} ").strip()
            
            try:
                choice_num = int(choice)
                if choice_num == len(items_list) + 1:
                    continue
                
                if 1 <= choice_num <= len(items_list):
                    item_type, item_key, item_data = items_list[choice_num - 1]
                    
                    # Only potions in general store
                    if item_type == 'potion':
                        # Potions can be bought in quantity
                        quantity = input(f"{colorize(f'How many? ({MIN_QUANTITY_PER_PURCHASE}-{MAX_QUANTITY_PER_PURCHASE}):', Colors.WHITE)} ").strip()
                        try:
                            qty = int(quantity)
                            if qty < MIN_QUANTITY_PER_PURCHASE:
                                qty = MIN_QUANTITY_PER_PURCHASE
                            elif qty > MAX_QUANTITY_PER_PURCHASE:
                                qty = MAX_QUANTITY_PER_PURCHASE
                            
                            total_cost = item_data['cost'] * qty
                            
                            if player.gold >= total_cost:
                                player.gold -= total_cost
                                for _ in range(qty):
                                    add_item_to_inventory(player.inventory, item_data.copy())
                                bought_msg = f"Bought {qty}x {item_data['name']}!"
                                print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(bought_msg, Colors.BRIGHT_GREEN)}")
                                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                            else:
                                no_gold_msg = "You don't have enough gold!"
                                print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(no_gold_msg, Colors.WHITE)}")
                                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                        except ValueError:
                            print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Invalid quantity!', Colors.WHITE)}")
                            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                else:
                    print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Invalid choice!', Colors.WHITE)}")
                    input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
            except ValueError:
                print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Invalid choice!', Colors.WHITE)}")
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
        
        elif menu_choice == '2':
            sell_items_menu(player, "General Store")
        
        elif menu_choice == '3':
            return
        else:
            print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Invalid choice!', Colors.WHITE)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")


def fishing_store(player):
    """Fishing Store - sells fishing rods"""
    while True:
        clear_screen()
        display_time_hud(player)  # Real-time clock display
        print(colorize("=" * 60, Colors.BRIGHT_CYAN))
        print(colorize("🎣  FISHING STORE  🎣", Colors.BRIGHT_CYAN + Colors.BOLD))
        print(colorize("=" * 60, Colors.BRIGHT_CYAN))
        print(f"\n{colorize('A shop dedicated to fishing equipment and supplies.', Colors.WHITE)}")
        print(f"\n{colorize(f'Your Gold: {player.gold}', Colors.BRIGHT_YELLOW + Colors.BOLD)}")
        print(colorize("─" * 60, Colors.BRIGHT_CYAN))
        print(f"\n{colorize('SHOP MENU:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
        print(f"  {colorize('1.', Colors.BRIGHT_GREEN)} Buy Fishing Rods")
        print(f"  {colorize('2.', Colors.BRIGHT_YELLOW)} Sell Items")
        print(f"  {colorize('3.', Colors.BRIGHT_BLUE)} Exit")
        print(colorize("=" * 60, Colors.BRIGHT_CYAN))
        
        menu_choice = input(f"\n{colorize('What would you like to do?', Colors.BRIGHT_CYAN)} ").strip()
        
        if menu_choice == '1':
            clear_screen()
            print(colorize("=" * 60, Colors.BRIGHT_CYAN))
            print(colorize("🎣  BUY FISHING RODS  🎣", Colors.BRIGHT_CYAN + Colors.BOLD))
            print(colorize("=" * 60, Colors.BRIGHT_CYAN))
            print(f"\n{colorize(f'Your Gold: {player.gold}', Colors.BRIGHT_YELLOW + Colors.BOLD)}")
            print(colorize("─" * 60, Colors.BRIGHT_CYAN))
            print(f"\n{colorize('AVAILABLE RODS:', Colors.BRIGHT_WHITE + Colors.BOLD)}\n")
            
            rods_list = list(FISHING_RODS.items())
            for i, (key, rod) in enumerate(rods_list, 1):
                boost_desc = f"Speeds up fishing by {abs(rod['fishing_speed_boost'])} seconds"
                print(f"  {colorize(str(i) + '.', Colors.WHITE)} {colorize(rod['name'], Colors.BRIGHT_CYAN)}")
                print(f"     {colorize('Effect:', Colors.BRIGHT_CYAN)} {colorize(boost_desc, Colors.WHITE)} | {colorize('Cost:', Colors.BRIGHT_YELLOW)} {colorize(str(rod['cost']) + 'g', Colors.BRIGHT_YELLOW)}")
            
            print(f"\n  {colorize(str(len(rods_list) + 1) + '.', Colors.BRIGHT_BLUE)} Back")
            print(colorize("=" * 60, Colors.BRIGHT_CYAN))
            
            choice = input(f"\n{colorize('What would you like to buy?', Colors.BRIGHT_CYAN)} ").strip()
            
            try:
                choice_num = int(choice)
                if choice_num == len(rods_list) + 1:
                    continue
                
                if 1 <= choice_num <= len(rods_list):
                    rod_key, rod = rods_list[choice_num - 1]
                    
                    if player.gold >= rod['cost']:
                        player.gold -= rod['cost']
                        add_item_to_inventory(player.inventory, rod.copy())
                        bought_msg = f"Bought {rod['name']}!"
                        print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(bought_msg, Colors.BRIGHT_GREEN)}")
                        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                    else:
                        no_gold_msg = "You don't have enough gold!"
                        print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(no_gold_msg, Colors.WHITE)}")
                        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                else:
                    print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Invalid choice!', Colors.WHITE)}")
                    input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
            except ValueError:
                print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Invalid choice!', Colors.WHITE)}")
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
        
        elif menu_choice == '2':
            sell_items_menu(player, "Fishing Store")
        
        elif menu_choice == '3':
            return
        else:
            print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Invalid choice!', Colors.WHITE)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")


def mining_store(player):
    """Mining Store - sells pickaxes"""
    while True:
        clear_screen()
        display_time_hud(player)  # Real-time clock display
        print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
        print(colorize("⛏️  MINING STORE  ⛏️", Colors.BRIGHT_MAGENTA + Colors.BOLD))
        print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
        print(f"\n{colorize('A shop dedicated to mining equipment and supplies.', Colors.WHITE)}")
        print(f"\n{colorize(f'Your Gold: {player.gold}', Colors.BRIGHT_YELLOW + Colors.BOLD)}")
        print(colorize("─" * 60, Colors.BRIGHT_MAGENTA))
        print(f"\n{colorize('SHOP MENU:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
        print(f"  {colorize('1.', Colors.BRIGHT_GREEN)} Buy Pickaxes")
        print(f"  {colorize('2.', Colors.BRIGHT_YELLOW)} Sell Items")
        print(f"  {colorize('3.', Colors.BRIGHT_BLUE)} Exit")
        print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
        
        menu_choice = input(f"\n{colorize('What would you like to do?', Colors.BRIGHT_CYAN)} ").strip()
        
        if menu_choice == '1':
            clear_screen()
            print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
            print(colorize("⛏️  BUY PICKAXES  ⛏️", Colors.BRIGHT_MAGENTA + Colors.BOLD))
            print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
            print(f"\n{colorize(f'Your Gold: {player.gold}', Colors.BRIGHT_YELLOW + Colors.BOLD)}")
            print(colorize("─" * 60, Colors.BRIGHT_MAGENTA))
            print(f"\n{colorize('AVAILABLE PICKAXES:', Colors.BRIGHT_WHITE + Colors.BOLD)}\n")
            
            pickaxes_list = list(PICKAXES.items())
            for i, (key, pickaxe) in enumerate(pickaxes_list, 1):
                boost_desc = f"Speeds up mining by {abs(pickaxe['mining_speed_boost'])} seconds"
                print(f"  {colorize(str(i) + '.', Colors.WHITE)} {colorize(pickaxe['name'], Colors.BRIGHT_MAGENTA)}")
                print(f"     {colorize('Effect:', Colors.BRIGHT_MAGENTA)} {colorize(boost_desc, Colors.WHITE)} | {colorize('Cost:', Colors.BRIGHT_YELLOW)} {colorize(str(pickaxe['cost']) + 'g', Colors.BRIGHT_YELLOW)}")
            
            print(f"\n  {colorize(str(len(pickaxes_list) + 1) + '.', Colors.BRIGHT_BLUE)} Back")
            print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
            
            choice = input(f"\n{colorize('What would you like to buy?', Colors.BRIGHT_CYAN)} ").strip()
            
            try:
                choice_num = int(choice)
                if choice_num == len(pickaxes_list) + 1:
                    continue
                
                if 1 <= choice_num <= len(pickaxes_list):
                    pickaxe_key, pickaxe = pickaxes_list[choice_num - 1]
                    
                    if player.gold >= pickaxe['cost']:
                        player.gold -= pickaxe['cost']
                        add_item_to_inventory(player.inventory, pickaxe.copy())
                        bought_msg = f"Bought {pickaxe['name']}!"
                        print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(bought_msg, Colors.BRIGHT_GREEN)}")
                        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                    else:
                        no_gold_msg = "You don't have enough gold!"
                        print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(no_gold_msg, Colors.WHITE)}")
                        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                else:
                    print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Invalid choice!', Colors.WHITE)}")
                    input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
            except ValueError:
                print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Invalid choice!', Colors.WHITE)}")
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
        
        elif menu_choice == '2':
            sell_items_menu(player, "Mining Store")
        
        elif menu_choice == '3':
            return
        else:
            print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Invalid choice!', Colors.WHITE)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")


def hospital(player):
    """Hospital - heal HP and cure all status effects"""
    clear_screen()
    print(colorize("=" * 60, Colors.BRIGHT_GREEN))
    print(colorize("🏥  HOSPITAL  🏥", Colors.BRIGHT_GREEN + Colors.BOLD))
    print(colorize("=" * 60, Colors.BRIGHT_GREEN))
    print(f"\n{colorize('Welcome to the Hospital. We can heal your wounds and cure all ailments.', Colors.WHITE)}")
    
    if player.hp >= player.max_hp:
        print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize('You are already at full health!', Colors.WHITE)}")
    else:
        old_hp = player.hp
        player.hp = player.max_hp
        healed = player.hp - old_hp
        print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(f'You have been healed for {healed} HP!', Colors.BRIGHT_GREEN)}")
        print(f"{colorize('Current HP:', Colors.WHITE)} {colorize(str(player.hp) + '/' + str(player.max_hp), Colors.BRIGHT_GREEN)}")
    
    # Clear any status effects (future implementation)
    # if hasattr(player, 'status_effects'):
    #     player.status_effects.clear()
    
    input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")


def inn(player):
    """Legacy inn function - redirects to hospital"""
    hospital(player)


def pimping_service(player):
    """Pimping Service - fuse talismans with weapons/armor"""
    from ..items.definitions import DROP_ITEMS
    
    while True:
        clear_screen()
        print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
        print(colorize("💎  PIMPING  💎", Colors.BRIGHT_MAGENTA + Colors.BOLD))
        print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
        print(f"\n{colorize('Enhance your weapons and armor with powerful talismans!', Colors.WHITE)}")
        print(f"{colorize('Talismans can add stat bonuses to make your gear stronger.', Colors.WHITE)}")
        print(f"\n{colorize(f'Your Gold: {player.gold}', Colors.BRIGHT_YELLOW + Colors.BOLD)}")
        print(colorize("─" * 60, Colors.BRIGHT_MAGENTA))
        print(f"\n{colorize('MENU:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
        print(f"  {colorize('1.', Colors.BRIGHT_GREEN)} Upgrade Weapon")
        print(f"  {colorize('2.', Colors.BRIGHT_BLUE)} Upgrade Armor")
        print(f"  {colorize('3.', Colors.BRIGHT_BLUE)} Exit")
        print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
        
        menu_choice = input(f"\n{colorize('What would you like to do?', Colors.BRIGHT_CYAN)} ").strip()
        
        if menu_choice == '1':
            # Upgrade Weapon
            if not player.weapon:
                print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('You need to equip a weapon first!', Colors.WHITE)}")
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                continue
            
            # Get talismans that can be used on weapons
            weapon_talismans = []
            for item in player.inventory:
                if item.get('type') == 'talisman':
                    item_type = item.get('item_type', 'weapon')
                    if item_type in ['weapon', 'both']:
                        weapon_talismans.append(item)
            
            if not weapon_talismans:
                print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('You need a talisman in your inventory that can be used on weapons!', Colors.WHITE)}")
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                continue
            
            clear_screen()
            print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
            print(colorize("💎  UPGRADE WEAPON  💎", Colors.BRIGHT_MAGENTA + Colors.BOLD))
            print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
            print(f"\n{colorize('Current Weapon:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
            weapon_display_name = player.weapon['name']
            if 'talisman_bonuses' in player.weapon:
                bonuses = player.weapon['talisman_bonuses']
                bonus_parts = []
                if bonuses.get('bonus_str', 0) > 0:
                    bonus_parts.append(f"+{bonuses['bonus_str']} STR")
                if bonuses.get('bonus_dex', 0) > 0:
                    bonus_parts.append(f"+{bonuses['bonus_dex']} DEX")
                if bonuses.get('bonus_agl', 0) > 0:
                    bonus_parts.append(f"+{bonuses['bonus_agl']} AGIL")
                if bonuses.get('bonus_hp', 0) > 0:
                    bonus_parts.append(f"+{bonuses['bonus_hp']} HP")
                if bonuses.get('bonus_defense', 0) > 0:
                    bonus_parts.append(f"+{bonuses['bonus_defense']} DEF")
                if bonus_parts:
                    weapon_display_name += f" {colorize('(' + ', '.join(bonus_parts) + ')', Colors.BRIGHT_GREEN)}"
            print(f"  {colorize(weapon_display_name, Colors.BRIGHT_CYAN)}")
            print(f"  {colorize('Attack:', Colors.YELLOW)} {colorize(str(player.weapon['attack']), Colors.BRIGHT_YELLOW)}")
            
            print(f"\n{colorize('Available Talismans:', Colors.BRIGHT_WHITE + Colors.BOLD)}\n")
            for i, talisman in enumerate(weapon_talismans, 1):
                bonus_parts = []
                if talisman.get('bonus_str', 0) > 0:
                    bonus_parts.append(f"+{talisman['bonus_str']} STR")
                if talisman.get('bonus_dex', 0) > 0:
                    bonus_parts.append(f"+{talisman['bonus_dex']} DEX")
                if talisman.get('bonus_agl', 0) > 0:
                    bonus_parts.append(f"+{talisman['bonus_agl']} AGIL")
                if talisman.get('bonus_hp', 0) > 0:
                    bonus_parts.append(f"+{talisman['bonus_hp']} HP")
                if talisman.get('bonus_defense', 0) > 0:
                    bonus_parts.append(f"+{talisman['bonus_defense']} DEF")
                bonus_text = ', '.join(bonus_parts) if bonus_parts else 'No bonuses'
                print(f"  {colorize(str(i) + '.', Colors.WHITE)} {colorize(talisman['name'], Colors.BRIGHT_MAGENTA)}")
                print(f"     {colorize('Bonuses:', Colors.BRIGHT_GREEN)} {colorize(bonus_text, Colors.WHITE)}")
            
            print(f"\n  {colorize(str(len(weapon_talismans) + 1) + '.', Colors.BRIGHT_BLUE)} Back")
            print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
            
            choice = input(f"\n{colorize('Which talisman to fuse?', Colors.BRIGHT_CYAN)} ").strip()
            
            try:
                choice_num = int(choice)
                if choice_num == len(weapon_talismans) + 1:
                    continue
                
                if 1 <= choice_num <= len(weapon_talismans):
                    selected_talisman = weapon_talismans[choice_num - 1]
                    
                    # Check if weapon already has a talisman
                    had_talisman = 'talisman_bonuses' in player.weapon and player.weapon['talisman_bonuses']
                    
                    if had_talisman:
                        print(f"\n{colorize('⚠️', Colors.BRIGHT_YELLOW)} {colorize('This weapon already has a talisman applied!', Colors.YELLOW)}")
                        print(f"{colorize('The new talisman will REPLACE the existing one.', Colors.YELLOW)}")
                        confirm = input(f"\n{colorize('Continue? (y/n):', Colors.BRIGHT_CYAN)} ").strip().lower()
                        if confirm != 'y':
                            print(f"\n{colorize('❌ Cancelled', Colors.BRIGHT_RED)}")
                            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                            continue
                        
                        # Need to recalculate HP loss from old talisman before replacing
                        old_hp_bonus = player.weapon['talisman_bonuses'].get('bonus_hp', 0)
                    else:
                        old_hp_bonus = 0
                    
                    # REPLACE talisman bonuses (not stack)
                    player.weapon['talisman_bonuses'] = {}
                    bonuses = player.weapon['talisman_bonuses']
                    
                    for key in ['bonus_str', 'bonus_dex', 'bonus_agl', 'bonus_hp', 'bonus_defense']:
                        if key in selected_talisman:
                            bonuses[key] = selected_talisman[key]
                    
                    # Remove talisman from inventory
                    remove_item_from_inventory(player.inventory, selected_talisman, 1)
                    
                    # Recalculate max HP
                    old_max_hp = player.max_hp
                    player.calculate_max_hp()
                    hp_gained = player.max_hp - old_max_hp
                    if hp_gained > 0:
                        player.hp += hp_gained
                    elif hp_gained < 0:
                        player.hp = max(1, player.hp + hp_gained)
                    
                    if had_talisman:
                        success_msg = f"Replaced talisman on {player.weapon['name']} with {selected_talisman['name']}!"
                    else:
                        success_msg = f"Successfully fused {selected_talisman['name']} with {player.weapon['name']}!"
                    print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(success_msg, Colors.BRIGHT_GREEN)}")
                    input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                else:
                    print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Invalid choice!', Colors.WHITE)}")
                    input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
            except ValueError:
                print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Invalid choice!', Colors.WHITE)}")
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
        
        elif menu_choice == '2':
            # Upgrade Armor
            if not player.armor:
                print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('You need to equip armor first!', Colors.WHITE)}")
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                continue
            
            # Get talismans that can be used on armor
            armor_talismans = []
            for item in player.inventory:
                if item.get('type') == 'talisman':
                    item_type = item.get('item_type', 'armor')
                    if item_type in ['armor', 'both']:
                        armor_talismans.append(item)
            
            if not armor_talismans:
                print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('You need a talisman in your inventory that can be used on armor!', Colors.WHITE)}")
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                continue
            
            clear_screen()
            print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
            print(colorize("💎  UPGRADE ARMOR  💎", Colors.BRIGHT_MAGENTA + Colors.BOLD))
            print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
            print(f"\n{colorize('Current Armor:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
            armor_display_name = player.armor['name']
            if 'talisman_bonuses' in player.armor:
                bonuses = player.armor['talisman_bonuses']
                bonus_parts = []
                if bonuses.get('bonus_str', 0) > 0:
                    bonus_parts.append(f"+{bonuses['bonus_str']} STR")
                if bonuses.get('bonus_dex', 0) > 0:
                    bonus_parts.append(f"+{bonuses['bonus_dex']} DEX")
                if bonuses.get('bonus_agl', 0) > 0:
                    bonus_parts.append(f"+{bonuses['bonus_agl']} AGIL")
                if bonuses.get('bonus_hp', 0) > 0:
                    bonus_parts.append(f"+{bonuses['bonus_hp']} HP")
                if bonuses.get('bonus_defense', 0) > 0:
                    bonus_parts.append(f"+{bonuses['bonus_defense']} DEF")
                if bonus_parts:
                    armor_display_name += f" {colorize('(' + ', '.join(bonus_parts) + ')', Colors.BRIGHT_GREEN)}"
            print(f"  {colorize(armor_display_name, Colors.BRIGHT_CYAN)}")
            print(f"  {colorize('Defense:', Colors.BLUE)} {colorize(str(player.armor['defense']), Colors.BRIGHT_BLUE)}")
            
            print(f"\n{colorize('Available Talismans:', Colors.BRIGHT_WHITE + Colors.BOLD)}\n")
            for i, talisman in enumerate(armor_talismans, 1):
                bonus_parts = []
                if talisman.get('bonus_str', 0) > 0:
                    bonus_parts.append(f"+{talisman['bonus_str']} STR")
                if talisman.get('bonus_dex', 0) > 0:
                    bonus_parts.append(f"+{talisman['bonus_dex']} DEX")
                if talisman.get('bonus_agl', 0) > 0:
                    bonus_parts.append(f"+{talisman['bonus_agl']} AGIL")
                if talisman.get('bonus_hp', 0) > 0:
                    bonus_parts.append(f"+{talisman['bonus_hp']} HP")
                if talisman.get('bonus_defense', 0) > 0:
                    bonus_parts.append(f"+{talisman['bonus_defense']} DEF")
                bonus_text = ', '.join(bonus_parts) if bonus_parts else 'No bonuses'
                print(f"  {colorize(str(i) + '.', Colors.WHITE)} {colorize(talisman['name'], Colors.BRIGHT_MAGENTA)}")
                print(f"     {colorize('Bonuses:', Colors.BRIGHT_GREEN)} {colorize(bonus_text, Colors.WHITE)}")
            
            print(f"\n  {colorize(str(len(armor_talismans) + 1) + '.', Colors.BRIGHT_BLUE)} Back")
            print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
            
            choice = input(f"\n{colorize('Which talisman to fuse?', Colors.BRIGHT_CYAN)} ").strip()
            
            try:
                choice_num = int(choice)
                if choice_num == len(armor_talismans) + 1:
                    continue
                
                if 1 <= choice_num <= len(armor_talismans):
                    selected_talisman = armor_talismans[choice_num - 1]
                    
                    # Check if armor already has a talisman
                    had_talisman = 'talisman_bonuses' in player.armor and player.armor['talisman_bonuses']
                    
                    if had_talisman:
                        print(f"\n{colorize('⚠️', Colors.BRIGHT_YELLOW)} {colorize('This armor already has a talisman applied!', Colors.YELLOW)}")
                        print(f"{colorize('The new talisman will REPLACE the existing one.', Colors.YELLOW)}")
                        confirm = input(f"\n{colorize('Continue? (y/n):', Colors.BRIGHT_CYAN)} ").strip().lower()
                        if confirm != 'y':
                            print(f"\n{colorize('❌ Cancelled', Colors.BRIGHT_RED)}")
                            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                            continue
                        
                        # Need to track HP loss from old talisman
                        old_hp_bonus = player.armor['talisman_bonuses'].get('bonus_hp', 0)
                    else:
                        old_hp_bonus = 0
                    
                    # REPLACE talisman bonuses (not stack)
                    player.armor['talisman_bonuses'] = {}
                    bonuses = player.armor['talisman_bonuses']
                    
                    for key in ['bonus_str', 'bonus_dex', 'bonus_agl', 'bonus_hp', 'bonus_defense']:
                        if key in selected_talisman:
                            bonuses[key] = selected_talisman[key]
                    
                    # Remove talisman from inventory
                    remove_item_from_inventory(player.inventory, selected_talisman, 1)
                    
                    # Recalculate max HP
                    old_max_hp = player.max_hp
                    player.calculate_max_hp()
                    hp_gained = player.max_hp - old_max_hp
                    if hp_gained > 0:
                        player.hp += hp_gained
                    elif hp_gained < 0:
                        player.hp = max(1, player.hp + hp_gained)
                    
                    if had_talisman:
                        success_msg = f"Replaced talisman on {player.armor['name']} with {selected_talisman['name']}!"
                    else:
                        success_msg = f"Successfully fused {selected_talisman['name']} with {player.armor['name']}!"
                    print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(success_msg, Colors.BRIGHT_GREEN)}")
                    input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                else:
                    print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Invalid choice!', Colors.WHITE)}")
                    input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
            except ValueError:
                print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Invalid choice!', Colors.WHITE)}")
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
        
        elif menu_choice == '3':
            return
        else:
            print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('Invalid choice!', Colors.WHITE)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
