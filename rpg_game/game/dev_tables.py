"""Developer tables for viewing game data"""
from ..ui import Colors, colorize, clear_screen
from ..items.definitions import (
    SWORDS, BLADES, GUNS, CROSSES, MACES, ARMOR_SETS, 
    POTIONS, FISHING_RODS, PICKAXES, DROP_ITEMS
)
from ..combat.enemies import BASE_ENEMIES
from ..skills.fishing import FISH_TYPES, FISH_LEVEL_REQUIREMENTS, COOKED_FISH_ITEMS, GOURMET_FISH_ITEMS
from ..skills.mining import MINING_ORES, MINING_LEVEL_REQUIREMENTS


def get_item_sell_value(item_key):
    """Get sell value for any item from all possible sources"""
    # Check all item dictionaries
    item_sources = [
        DROP_ITEMS,
        POTIONS,
        FISHING_RODS,
        PICKAXES,
        FISH_TYPES,
        COOKED_FISH_ITEMS,
        GOURMET_FISH_ITEMS,
        MINING_ORES
    ]
    
    for source in item_sources:
        if item_key in source:
            return source[item_key].get('sell_value', '?')
    
    return '?'


def view_all_items():
    """Display all items in the game with stats and sources"""
    pages = []
    
    # Page 1: Weapons
    weapons_page = []
    weapons_page.append(colorize("=" * 80, Colors.BRIGHT_CYAN))
    weapons_page.append(colorize("⚔️  WEAPONS", Colors.BRIGHT_CYAN + Colors.BOLD))
    weapons_page.append(colorize("=" * 80, Colors.BRIGHT_CYAN))
    weapons_page.append("")
    
    # Swords
    weapons_page.append(colorize("SWORDS (Knight Guild):", Colors.BRIGHT_GREEN + Colors.BOLD))
    weapons_page.append(colorize("─" * 80, Colors.CYAN))
    weapons_page.append(f"  {'Name':<30} {'Grade':<8} {'Attack':<8} {'Req Lvl':<10} {'Cost':<12} {'Sell':<10}")
    weapons_page.append(colorize("─" * 80, Colors.CYAN))
    for key, item in sorted(SWORDS.items(), key=lambda x: x[1].get('grade', 0)):
        name = item['name']
        grade = item.get('grade', 0)
        attack = item.get('attack', 0)
        level_req = item.get('level_req', 1)
        cost = item.get('cost', 0)
        sell = item.get('sell_value', 0)
        weapons_page.append(f"  {name:<30} G{grade:<7} {attack:<8} Lvl {level_req:<6} {cost:,}g{' '*(12-len(f'{cost:,}g'))} {sell:,}g")
    
    weapons_page.append("")
    weapons_page.append(colorize("BLADES (Knight Guild):", Colors.BRIGHT_GREEN + Colors.BOLD))
    weapons_page.append(colorize("─" * 80, Colors.CYAN))
    for key, item in sorted(BLADES.items(), key=lambda x: x[1].get('grade', 0)):
        name = item['name']
        grade = item.get('grade', 0)
        attack = item.get('attack', 0)
        level_req = item.get('level_req', 1)
        cost = item.get('cost', 0)
        sell = item.get('sell_value', 0)
        weapons_page.append(f"  {name:<30} G{grade:<7} {attack:<8} Lvl {level_req:<6} {cost:,}g{' '*(12-len(f'{cost:,}g'))} {sell:,}g")
    
    weapons_page.append("")
    weapons_page.append(colorize("GUNS (Army Guild):", Colors.BRIGHT_GREEN + Colors.BOLD))
    weapons_page.append(colorize("─" * 80, Colors.CYAN))
    for key, item in sorted(GUNS.items(), key=lambda x: x[1].get('grade', 0)):
        name = item['name']
        grade = item.get('grade', 0)
        attack = item.get('attack', 0)
        level_req = item.get('level_req', 1)
        cost = item.get('cost', 0)
        sell = item.get('sell_value', 0)
        weapons_page.append(f"  {name:<30} G{grade:<7} {attack:<8} Lvl {level_req:<6} {cost:,}g{' '*(12-len(f'{cost:,}g'))} {sell:,}g")
    
    pages.append("\n".join(weapons_page))
    
    # Page 2: Crosses and Maces, Armor
    page2 = []
    page2.append(colorize("=" * 80, Colors.BRIGHT_CYAN))
    page2.append(colorize("✝️  CROSSES & MACES | 🛡️  ARMOR", Colors.BRIGHT_CYAN + Colors.BOLD))
    page2.append(colorize("=" * 80, Colors.BRIGHT_CYAN))
    page2.append("")
    
    page2.append(colorize("CROSSES (Cleric Guild):", Colors.BRIGHT_GREEN + Colors.BOLD))
    page2.append(colorize("─" * 80, Colors.CYAN))
    page2.append(f"  {'Name':<30} {'Grade':<8} {'Attack':<8} {'Req Lvl':<10} {'Cost':<12} {'Sell':<10}")
    page2.append(colorize("─" * 80, Colors.CYAN))
    for key, item in sorted(CROSSES.items(), key=lambda x: x[1].get('grade', 0)):
        name = item['name']
        grade = item.get('grade', 0)
        attack = item.get('attack', 0)
        level_req = item.get('level_req', 1)
        cost = item.get('cost', 0)
        sell = item.get('sell_value', 0)
        page2.append(f"  {name:<30} G{grade:<7} {attack:<8} Lvl {level_req:<6} {cost:,}g{' '*(12-len(f'{cost:,}g'))} {sell:,}g")
    
    page2.append("")
    page2.append(colorize("MACES (Cleric Guild):", Colors.BRIGHT_GREEN + Colors.BOLD))
    page2.append(colorize("─" * 80, Colors.CYAN))
    for key, item in sorted(MACES.items(), key=lambda x: x[1].get('grade', 0)):
        name = item['name']
        grade = item.get('grade', 0)
        attack = item.get('attack', 0)
        level_req = item.get('level_req', 1)
        cost = item.get('cost', 0)
        sell = item.get('sell_value', 0)
        page2.append(f"  {name:<30} G{grade:<7} {attack:<8} Lvl {level_req:<6} {cost:,}g{' '*(12-len(f'{cost:,}g'))} {sell:,}g")
    
    page2.append("")
    page2.append(colorize("ARMOR SETS (General Store):", Colors.BRIGHT_BLUE + Colors.BOLD))
    page2.append(colorize("─" * 80, Colors.CYAN))
    page2.append(f"  {'Name':<30} {'Grade':<8} {'Defense':<8} {'Cost':<15} {'Sell':<10}")
    page2.append(colorize("─" * 80, Colors.CYAN))
    for key, item in sorted(ARMOR_SETS.items(), key=lambda x: x[1].get('grade', 0)):
        name = item['name']
        grade = item.get('grade', 0)
        defense = item.get('defense', 0)
        cost = item.get('cost', 0)
        sell = item.get('sell_value', 0)
        page2.append(f"  {name:<30} G{grade:<7} {defense:<8} {cost:,}g{' '*(15-len(f'{cost:,}g'))} {sell:,}g")
    
    pages.append("\n".join(page2))
    
    # Page 3: Tools and Potions
    page3 = []
    page3.append(colorize("=" * 80, Colors.BRIGHT_CYAN))
    page3.append(colorize("🔧  TOOLS & 🧪  POTIONS", Colors.BRIGHT_CYAN + Colors.BOLD))
    page3.append(colorize("=" * 80, Colors.BRIGHT_CYAN))
    page3.append("")
    
    page3.append(colorize("FISHING RODS (Fishing Store):", Colors.BRIGHT_MAGENTA + Colors.BOLD))
    page3.append(colorize("─" * 80, Colors.CYAN))
    page3.append(f"  {'Name':<25} {'Speed Boost':<15} {'Cost':<15} {'Sell':<10}")
    page3.append(colorize("─" * 80, Colors.CYAN))
    for key, item in FISHING_RODS.items():
        name = item['name']
        boost = f"{item['fishing_speed_boost']}s"
        cost = item.get('cost', 0)
        sell = item.get('sell_value', 0)
        page3.append(f"  {name:<25} {boost:<15} {cost:,}g{' '*(15-len(f'{cost:,}g'))} {sell:,}g")
    
    page3.append("")
    page3.append(colorize("PICKAXES (Mining Store):", Colors.BRIGHT_MAGENTA + Colors.BOLD))
    page3.append(colorize("─" * 80, Colors.CYAN))
    page3.append(f"  {'Name':<25} {'Speed Boost':<15} {'Cost':<15} {'Sell':<10}")
    page3.append(colorize("─" * 80, Colors.CYAN))
    for key, item in PICKAXES.items():
        name = item['name']
        boost = f"{item['mining_speed_boost']}s"
        cost = item.get('cost', 0)
        sell = item.get('sell_value', 0)
        page3.append(f"  {name:<25} {boost:<15} {cost:,}g{' '*(15-len(f'{cost:,}g'))} {sell:,}g")
    
    page3.append("")
    page3.append(colorize("POTIONS (General Store):", Colors.BRIGHT_YELLOW + Colors.BOLD))
    page3.append(colorize("─" * 80, Colors.CYAN))
    page3.append(f"  {'Name':<30} {'Heal':<10} {'Cost':<15} {'Sell':<10}")
    page3.append(colorize("─" * 80, Colors.CYAN))
    for key, item in POTIONS.items():
        name = item['name']
        heal = item.get('heal', 0)
        cost = item.get('cost', 0)
        sell = item.get('sell_value', 0)
        page3.append(f"  {name:<30} {heal:<10} {cost:,}g{' '*(15-len(f'{cost:,}g'))} {sell:,}g")
    
    pages.append("\n".join(page3))
    
    # Page 4: Fish and Ores
    page4 = []
    page4.append(colorize("=" * 80, Colors.BRIGHT_CYAN))
    page4.append(colorize("🎣  FISH & ⛏️  ORES", Colors.BRIGHT_CYAN + Colors.BOLD))
    page4.append(colorize("=" * 80, Colors.BRIGHT_CYAN))
    page4.append("")
    
    page4.append(colorize("FISH (Fishing Activity):", Colors.BRIGHT_CYAN + Colors.BOLD))
    page4.append(colorize("─" * 80, Colors.CYAN))
    page4.append(f"  {'Name':<25} {'Req Level':<12} {'Catch %':<12} {'Sell Value':<12}")
    page4.append(colorize("─" * 80, Colors.CYAN))
    for key, item in sorted(FISH_TYPES.items(), key=lambda x: FISH_LEVEL_REQUIREMENTS.get(x[1].get('key', x[0]), 1)):
        name = item['name']
        fish_key = item.get('key', key)
        req_level = FISH_LEVEL_REQUIREMENTS.get(fish_key, 1)
        catch_chance = item.get('catch_chance', 0) * 100
        sell = item.get('sell_value', 0)
        page4.append(f"  {name:<25} Lvl {req_level:<8} {catch_chance:.1f}%{' '*(12-len(f'{catch_chance:.1f}%'))} {sell:,}g")
    
    page4.append("")
    page4.append(colorize("ORES & GEMS (Mining Activity):", Colors.BRIGHT_MAGENTA + Colors.BOLD))
    page4.append(colorize("─" * 80, Colors.CYAN))
    page4.append(f"  {'Name':<25} {'Req Level':<12} {'Mine %':<12} {'Sell Value':<12}")
    page4.append(colorize("─" * 80, Colors.CYAN))
    for key, item in sorted(MINING_ORES.items(), key=lambda x: MINING_LEVEL_REQUIREMENTS.get(x[1].get('key', x[0]), 1)):
        name = item['name']
        ore_key = item.get('key', key)
        req_level = MINING_LEVEL_REQUIREMENTS.get(ore_key, 1)
        mine_chance = item.get('mine_chance', 0) * 100
        sell = item.get('sell_value', 0)
        page4.append(f"  {name:<25} Lvl {req_level:<8} {mine_chance:.2f}%{' '*(12-len(f'{mine_chance:.2f}%'))} {sell:,}g")
    
    pages.append("\n".join(page4))
    
    # Page 5: Drop Items (Materials, Consumables, Talismans)
    page5 = []
    page5.append(colorize("=" * 80, Colors.BRIGHT_CYAN))
    page5.append(colorize("💎  DROP ITEMS & TALISMANS", Colors.BRIGHT_CYAN + Colors.BOLD))
    page5.append(colorize("=" * 80, Colors.BRIGHT_CYAN))
    page5.append("")
    
    # Separate by type
    materials = {k: v for k, v in DROP_ITEMS.items() if v.get('type') == 'material'}
    consumables = {k: v for k, v in DROP_ITEMS.items() if v.get('type') == 'consumable'}
    talismans = {k: v for k, v in DROP_ITEMS.items() if v.get('type') == 'talisman'}
    
    page5.append(colorize("MATERIALS (Enemy Drops):", Colors.WHITE + Colors.BOLD))
    page5.append(colorize("─" * 80, Colors.CYAN))
    page5.append(f"  {'Name':<35} {'Sell Value':<12} {'Description':<30}")
    page5.append(colorize("─" * 80, Colors.CYAN))
    for key, item in sorted(materials.items(), key=lambda x: x[1].get('sell_value', 0)):
        name = item['name']
        sell = item.get('sell_value', 0)
        desc = item.get('description', '')[:30]
        page5.append(f"  {name:<35} {sell:,}g{' '*(12-len(f'{sell:,}g'))} {desc:<30}")
    
    page5.append("")
    page5.append(colorize("CONSUMABLES (Enemy Drops):", Colors.BRIGHT_YELLOW + Colors.BOLD))
    page5.append(colorize("─" * 80, Colors.CYAN))
    for key, item in consumables.items():
        name = item['name']
        heal = item.get('heal', 0)
        sell = item.get('sell_value', 0)
        desc = item.get('description', '')[:30]
        page5.append(f"  {name:<35} Heal: {heal}HP, Sell: {sell}g")
    
    page5.append("")
    page5.append(colorize("TALISMANS (Rare Enemy Drops - 0.01-1% chance):", Colors.BRIGHT_MAGENTA + Colors.BOLD))
    page5.append(colorize("─" * 80, Colors.CYAN))
    page5.append(f"  {'Name':<35} {'Bonuses':<40}")
    page5.append(colorize("─" * 80, Colors.CYAN))
    for key, item in sorted(talismans.items(), key=lambda x: x[1].get('sell_value', 0)):
        name = item['name']
        bonuses = []
        if 'bonus_str' in item:
            bonuses.append(f"+{item['bonus_str']} STR")
        if 'bonus_dex' in item:
            bonuses.append(f"+{item['bonus_dex']} DEX")
        if 'bonus_agl' in item:
            bonuses.append(f"+{item['bonus_agl']} AGL")
        if 'bonus_hp' in item:
            bonuses.append(f"+{item['bonus_hp']} HP")
        if 'bonus_defense' in item:
            bonuses.append(f"+{item['bonus_defense']} DEF")
        bonus_str = ', '.join(bonuses)
        page5.append(f"  {name:<35} {bonus_str:<40}")
    
    pages.append("\n".join(page5))
    
    # Display pages with pagination
    current_page = 0
    while True:
        clear_screen()
        print(pages[current_page])
        print()
        print(colorize("=" * 80, Colors.BRIGHT_CYAN))
        print(f"  {colorize(f'Page {current_page + 1}/{len(pages)}', Colors.BRIGHT_WHITE + Colors.BOLD)}")
        
        if current_page < len(pages) - 1:
            print(f"  {colorize('N', Colors.BRIGHT_GREEN)} - Next Page")
        if current_page > 0:
            print(f"  {colorize('P', Colors.BRIGHT_GREEN)} - Previous Page")
        print(f"  {colorize('Q', Colors.BRIGHT_RED)} - Back to Dev Menu")
        print(colorize("=" * 80, Colors.BRIGHT_CYAN))
        
        choice = input(f"\n{colorize('Navigation:', Colors.BRIGHT_CYAN)} ").strip().lower()
        
        if choice == 'n' and current_page < len(pages) - 1:
            current_page += 1
        elif choice == 'p' and current_page > 0:
            current_page -= 1
        elif choice == 'q':
            break


def get_monster_locations(tier):
    """Get locations where monsters of a specific tier can be found"""
    tier_locations = {
        1: ["Limbo Dungeon B1", "Underground Waterways (player level < 5)"],
        2: ["Limbo Dungeon B2-B3", "Rhaom Dungeon B1-B2", "Underground Waterways", "Eslania Dungeon B1"],
        3: ["Rhaom Dungeon B3", "Lost Taiyan B1-B2", "Eslania Dungeon B2-B3", "Asylion Dungeon B1-B2", "Underground Waterways"],
        4: ["Lost Taiyan B3", "Asylion Dungeon B2-B3", "Tepes Lair (early floors)", "Underground Waterways"],
        5: ["Tepes Lair (mid-late floors)"],
        6: ["Tepes Lair (deep floors)"]
    }
    return tier_locations.get(tier, ["Unknown"])


def view_all_monsters():
    """Display all monsters in the game with stats and drops"""
    pages = []
    
    # Group enemies by tier
    for tier_num in range(1, 7):
        tier_enemies = [e for e in BASE_ENEMIES if e.get('tier') == tier_num]
        
        if not tier_enemies:
            continue
        
        page = []
        page.append(colorize("=" * 100, Colors.BRIGHT_RED))
        tier_names = {
            1: "TIER 1 - BEGINNER (Level 1-5)",
            2: "TIER 2 - EARLY GAME (Level 5-15)",
            3: "TIER 3 - MID GAME (Level 18-30)",
            4: "TIER 4 - LATE MID GAME (Level 33-50)",
            5: "TIER 5 - LATE GAME (Level 55-73)",
            6: "TIER 6 - END GAME (Level 81-95)"
        }
        page.append(colorize(f"⚔️  {tier_names.get(tier_num, f'TIER {tier_num}')}", Colors.BRIGHT_RED + Colors.BOLD))
        page.append(colorize("=" * 100, Colors.BRIGHT_RED))
        page.append("")
        
        for enemy in tier_enemies:
            name = enemy['name']
            hp = enemy['base_hp']
            attack = enemy['base_attack']
            defense = enemy['base_defense']
            exp = enemy['base_exp']
            gold = enemy['base_gold']
            tier = enemy.get('tier', 1)
            
            page.append(colorize(f"📛 {name}", Colors.BRIGHT_YELLOW + Colors.BOLD))
            page.append(colorize("─" * 100, Colors.RED))
            page.append(f"  {colorize('Stats:', Colors.WHITE + Colors.BOLD)} HP: {colorize(str(hp), Colors.BRIGHT_RED)} | Attack: {colorize(str(attack), Colors.BRIGHT_YELLOW)} | Defense: {colorize(str(defense), Colors.BRIGHT_BLUE)}")
            page.append(f"  {colorize('Rewards:', Colors.WHITE + Colors.BOLD)} {colorize(f'{exp} XP', Colors.BRIGHT_CYAN)} | {colorize(f'{gold}g', Colors.BRIGHT_YELLOW)}")
            
            # Show locations
            locations = get_monster_locations(tier)
            locations_str = ", ".join(locations)
            page.append(f"  {colorize('Locations:', Colors.WHITE + Colors.BOLD)} {colorize(locations_str, Colors.BRIGHT_CYAN)}")
            
            # Show guaranteed drop first (head)
            guaranteed_drops = [d for d in enemy.get('drops', []) if d['chance'] >= 1.0]
            if guaranteed_drops:
                page.append(f"  {colorize('Guaranteed Drop:', Colors.BRIGHT_GREEN + Colors.BOLD)}")
                for drop in guaranteed_drops:
                    item_name = drop['item'].replace('_', ' ').title()
                    sell_value = get_item_sell_value(drop['item'])
                    page.append(f"    💀 {colorize(item_name, Colors.BRIGHT_GREEN)} - {colorize('100%', Colors.BRIGHT_GREEN)} (Worth: {colorize(f'{sell_value}g', Colors.BRIGHT_YELLOW)})")
            
            # Show regular drops (exclude talismans and guaranteed for readability)
            regular_drops = [d for d in enemy.get('drops', []) if not d['item'].startswith('talisman') and d['chance'] < 1.0]
            if regular_drops:
                page.append(f"  {colorize('Other Drops:', Colors.WHITE + Colors.BOLD)}")
                for drop in regular_drops[:5]:  # Show top 5 drops
                    item_name = drop['item'].replace('_', ' ').title()
                    chance = drop['chance'] * 100
                    # Get sell value from any item source
                    sell_value = get_item_sell_value(drop['item'])
                    page.append(f"    • {colorize(item_name, Colors.WHITE)} - {colorize(f'{chance:.1f}%', Colors.BRIGHT_YELLOW)} (Worth: {colorize(f'{sell_value}g', Colors.YELLOW)})")
            
            page.append(f"  {colorize('Talismans:', Colors.BRIGHT_MAGENTA + Colors.BOLD)} All enemies drop talismans (0.01-1% chance)")
            page.append("")
        
        pages.append("\n".join(page))
    
    # Display pages with pagination
    current_page = 0
    while True:
        clear_screen()
        print(pages[current_page])
        print()
        print(colorize("=" * 100, Colors.BRIGHT_RED))
        print(f"  {colorize(f'Page {current_page + 1}/{len(pages)}', Colors.BRIGHT_WHITE + Colors.BOLD)} | {colorize('Showing Tier ' + str(current_page + 1), Colors.BRIGHT_YELLOW)}")
        
        if current_page < len(pages) - 1:
            print(f"  {colorize('N', Colors.BRIGHT_GREEN)} - Next Tier")
        if current_page > 0:
            print(f"  {colorize('P', Colors.BRIGHT_GREEN)} - Previous Tier")
        print(f"  {colorize('Q', Colors.BRIGHT_RED)} - Back to Dev Menu")
        print(colorize("=" * 100, Colors.BRIGHT_RED))
        
        choice = input(f"\n{colorize('Navigation:', Colors.BRIGHT_CYAN)} ").strip().lower()
        
        if choice == 'n' and current_page < len(pages) - 1:
            current_page += 1
        elif choice == 'p' and current_page > 0:
            current_page -= 1
        elif choice == 'q':
            break

