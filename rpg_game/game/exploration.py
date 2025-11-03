"""Exploration and location systems"""
import random
from ..constants import (
    ENCOUNTER_CHANCE, RANDOM_EVENT_CHANCE,
    LOCATION_MULTIPLIER_UNDERGROUND, LOCATION_MULTIPLIER_DEFAULT,
    RANDOM_EVENT_GOLD_MIN, RANDOM_EVENT_GOLD_MAX,
    RANDOM_EVENT_EXP_MIN, RANDOM_EVENT_EXP_MAX,
    REVIVE_HP
)
from ..ui import Colors, colorize, clear_screen, health_bar
from ..models.location import LOCATIONS
from ..models.enemy import Enemy
from ..combat.enemies import BASE_ENEMIES
from ..combat.system import scale_enemy, combat
from ..items import POTIONS, add_item_to_inventory
from ..achievements.system import check_achievements


def explore_location(player, location_name):
    location = LOCATIONS[location_name]
    
    # Determine enemy pool and scaling multiplier based on location
    enemy_pool = []
    location_multiplier = LOCATION_MULTIPLIER_DEFAULT
    
    if location_name == 'underground_waterways':
        # Tiers 2-4 enemies, medium-hard difficulty
        enemy_pool = [e for e in BASE_ENEMIES if 2 <= e['tier'] <= 4]
        location_multiplier = LOCATION_MULTIPLIER_UNDERGROUND
    else:
        # Unknown location - shouldn't happen, but provide fallback
        enemy_pool = BASE_ENEMIES
        location_multiplier = LOCATION_MULTIPLIER_DEFAULT
    
    while True:
        clear_screen()
        print(colorize("=" * 60, Colors.CYAN))
        print(colorize(f"📍 {location.name.upper()}", Colors.BRIGHT_CYAN + Colors.BOLD))
        print(colorize("=" * 60, Colors.CYAN))
        print(f"\n{colorize(location.description, Colors.WHITE)}")
        print(f"\n{colorize(f'Your Status: Level {player.level} | HP: {player.hp}/{player.max_hp}', Colors.BRIGHT_YELLOW)}")
        print(colorize("\n" + "=" * 60, Colors.CYAN))
        print(f"\n{colorize('1.', Colors.BRIGHT_GREEN)} Explore deeper")
        print(f"{colorize('2.', Colors.BRIGHT_BLUE)} Return to Town")
        print(colorize("=" * 60, Colors.CYAN))
        
        choice = input(f"\n{colorize('What do you do?', Colors.BRIGHT_CYAN)} ").strip()
        
        if choice == '1':
            encounter_chance = random.random()
            if encounter_chance < ENCOUNTER_CHANCE:  # 70% chance of combat
                enemy_template = random.choice(enemy_pool).copy()
                # Scale enemy based on player level
                enemy_data = scale_enemy(enemy_template, player.level, location_multiplier)
                
                enemy = Enemy(
                    name=enemy_data['name'],
                    hp=enemy_data['hp'],
                    attack=enemy_data['attack'],
                    defense=enemy_data['defense'],
                    exp_reward=enemy_data['exp'],
                    gold_reward=enemy_data['gold'],
                    drops=enemy_data.get('drops', [])
                )
                # Pass through boss flag if present
                enemy.is_boss = enemy_data.get('is_boss', False)
                won = combat(player, enemy)
                
                if not won:
                    return 'game_over'
                
                # After combat, continue the explore loop
                continue
            else:
                # Random events (OSRS-style) - 5% chance
                if random.random() < RANDOM_EVENT_CHANCE:
                    random_event = random.choice([
                        ('treasure', 'You found a hidden treasure chest!'),
                        ('mysterious', 'A mysterious figure appears and rewards you!'),
                        ('lucky', 'Your luck shines - you find valuable loot!')
                    ])
                    event_type, event_msg = random_event
                    
                    clear_screen()
                    print(colorize("=" * 60, Colors.BRIGHT_CYAN))
                    print(colorize("✨  RANDOM EVENT! ✨", Colors.BRIGHT_CYAN + Colors.BOLD))
                    print(colorize("=" * 60, Colors.BRIGHT_CYAN))
                    print(f"\n{colorize(event_msg, Colors.BRIGHT_YELLOW)}")
                    
                    if event_type == 'treasure':
                        bonus_gold = random.randint(RANDOM_EVENT_GOLD_MIN, RANDOM_EVENT_GOLD_MAX)
                        player.gold += bonus_gold
                        print(f"\n{colorize('💰', Colors.BRIGHT_YELLOW)} {colorize(f'Gained {bonus_gold} gold!', Colors.BRIGHT_YELLOW)}")
                    elif event_type == 'mysterious':
                        bonus_exp = random.randint(RANDOM_EVENT_EXP_MIN, RANDOM_EVENT_EXP_MAX)
                        player.exp += bonus_exp
                        print(f"\n{colorize('✨', Colors.BRIGHT_GREEN)} {colorize(f'Gained {bonus_exp} experience!', Colors.BRIGHT_GREEN)}")
                    elif event_type == 'lucky':
                        # Give a random consumable
                        potion_key = random.choice(list(POTIONS.keys()))
                        potion = POTIONS[potion_key].copy()
                        add_item_to_inventory(player.inventory, potion)
                        potion_name = potion['name']
                        print(f"\n{colorize('🎁', Colors.BRIGHT_MAGENTA)} {colorize(f'Received {potion_name}!', Colors.BRIGHT_MAGENTA)}")
                    
                    input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                    continue
                else:
                    # Gold scales with level
                    base_gold = random.randint(10, 30)
                    gold_found = int(base_gold * (1 + player.level * 0.1))
                    player.gold += gold_found
                    print(f"\n💰 You found {gold_found} gold!")
                    input("\nPress Enter to continue...")
        
        elif choice == '2':
            # Return to previous area - 'town' for original locations, 'previous' for new ones
            if location_name in ['underground_waterways']:
                return 'previous'
            else:
                return 'town'
        else:
            print(f"\n{colorize('❌ Invalid choice!', Colors.BRIGHT_RED)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")


def explore_tepes_lair(player):
    """Tepes lair - infinite progressive difficulty"""
    lair_loot_gained = []  # Track loot gained in this lair run
    lair_gold_gained = 0
    lair_exp_gained = 0
    lair_level = 1
    
    # Save player state before entering lair (for death penalty)
    original_inventory = [item.copy() for item in player.inventory]
    original_gold = player.gold
    original_exp = player.exp
    original_hp = player.hp
    
    while True:
        clear_screen()
        location = LOCATIONS['tepes_lair']
        print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
        print(colorize(f"🦇  TEPES LAIR  🦇", Colors.BRIGHT_MAGENTA + Colors.BOLD))
        print(colorize(f"   Floor {lair_level}", Colors.BRIGHT_CYAN + Colors.BOLD))
        print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
        print(f"\n{colorize(location.description, Colors.WHITE)}")
        print(f"\n{colorize('YOUR STATUS:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
        print(f"  {colorize('Level:', Colors.WHITE)} {colorize(str(player.level), Colors.BRIGHT_GREEN)}")
        print(f"  {colorize('HP:', Colors.BRIGHT_RED)} {health_bar(player.hp, player.max_hp)}")
        print(f"  {colorize('Current Floor:', Colors.WHITE)} {colorize(str(lair_level), Colors.BRIGHT_CYAN + Colors.BOLD)}")
        print(f"  {colorize('Loot Gained:', Colors.BRIGHT_YELLOW)} {len(lair_loot_gained)} items, {lair_gold_gained} gold")
        print(colorize("\n" + "=" * 60, Colors.BRIGHT_MAGENTA))
        print(f"\n{colorize('1.', Colors.BRIGHT_GREEN)} Enter Floor {colorize(str(lair_level), Colors.BRIGHT_CYAN)}")
        print(f"{colorize('2.', Colors.BRIGHT_YELLOW)} Leave Lair {colorize('(Keep all loot)', Colors.WHITE)}")
        print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
        
        choice = input(f"\n{colorize('What do you do?', Colors.BRIGHT_CYAN)} ").strip()
        
        if choice == '1':
            # Generate scaled enemy for this tower floor
            # Lair floors get progressively harder: floor N = level N difficulty
            difficulty_level = lair_level
            
            # Choose enemy tier based on floor level (progressive scaling)
            if lair_level <= 5:
                enemy_pool = [e for e in BASE_ENEMIES if e['tier'] == 1]
            elif lair_level <= 15:
                enemy_pool = [e for e in BASE_ENEMIES if e['tier'] <= 2]
            elif lair_level <= 30:
                enemy_pool = [e for e in BASE_ENEMIES if e['tier'] <= 3]
            elif lair_level <= 50:
                enemy_pool = [e for e in BASE_ENEMIES if e['tier'] <= 4]
            elif lair_level <= 73:
                enemy_pool = [e for e in BASE_ENEMIES if e['tier'] <= 5]
            else:
                enemy_pool = BASE_ENEMIES  # All tiers including end game
            
            # Lair enemies scale more aggressively
            enemy_template = random.choice(enemy_pool).copy()
            lair_multiplier = 1.0 + (lair_level * 0.1)  # Each floor adds 10% difficulty
            enemy_data = scale_enemy(enemy_template, difficulty_level, lair_multiplier)
            
            # Lair rewards scale with floor level
            reward_multiplier = 1.0 + (lair_level * 0.2)
            enemy_data['exp'] = int(enemy_data['exp'] * reward_multiplier)
            enemy_data['gold'] = int(enemy_data['gold'] * reward_multiplier)
            
            # Add Tepes Lair-specific drops at higher floors
            if lair_level >= 10:
                if random.random() < 0.3:
                    enemy_data['drops'].append({'item': 'tepes_shard', 'chance': 1.0})
            if lair_level >= 25:
                if random.random() < 0.2:
                    enemy_data['drops'].append({'item': 'tepes_core', 'chance': 1.0})
            if lair_level >= 50:
                if random.random() < 0.15:
                    enemy_data['drops'].append({'item': 'lair_essence', 'chance': 1.0})
            if lair_level >= 75:
                if random.random() < 0.1:
                    enemy_data['drops'].append({'item': 'void_crystal', 'chance': 1.0})
            
            enemy = Enemy(
                name=f"{enemy_data['name']} (Floor {lair_level})",
                hp=enemy_data['hp'],
                attack=enemy_data['attack'],
                defense=enemy_data['defense'],
                exp_reward=enemy_data['exp'],
                gold_reward=enemy_data['gold'],
                drops=enemy_data.get('drops', [])
            )
            # Pass through boss flag if present
            enemy.is_boss = enemy_data.get('is_boss', False)
            
            # Store state before combat for tracking
            pre_combat_inventory_count = len(player.inventory)
            pre_combat_gold = player.gold
            pre_combat_exp = player.exp
            
            won = combat(player, enemy)
            
            if not won:
                # Player died - lose all Lair loot gained this run
                clear_screen()
                print(colorize("=" * 60, Colors.BRIGHT_RED))
                print(colorize("💀  LAIR DEATH  💀", Colors.BRIGHT_RED + Colors.BOLD))
                print(colorize("=" * 60, Colors.BRIGHT_RED))
                print(f"\n{colorize('You have fallen in Tepes Lair!', Colors.BRIGHT_RED)}")
                print(f"{colorize('All loot gained in this Lair run has been lost!', Colors.YELLOW)}")
                print(f"\n{colorize('Lost:', Colors.WHITE)}")
                print(f"  {colorize('Items:', Colors.BRIGHT_YELLOW)} {len(lair_loot_gained)}")
                print(f"  {colorize('Gold:', Colors.BRIGHT_YELLOW)} {lair_gold_gained}")
                print(f"  {colorize('Experience:', Colors.BRIGHT_YELLOW)} {lair_exp_gained}")
                
                # Restore player to pre-lair state
                player.inventory = [item.copy() for item in original_inventory]
                player.gold = original_gold
                player.exp = original_exp
                player.hp = REVIVE_HP  # Revive with 1 HP
                
                input(f"\n{colorize('Press Enter to return...', Colors.WHITE)}")
                return 'previous'
            
            # Track gains from this combat
            gold_gained = player.gold - pre_combat_gold
            exp_gained = player.exp - pre_combat_exp
            lair_gold_gained += gold_gained
            lair_exp_gained += exp_gained
            
            # Track new items from this combat
            items_gained = len(player.inventory) - pre_combat_inventory_count
            if items_gained > 0:
                for i in range(pre_combat_inventory_count, len(player.inventory)):
                    lair_loot_gained.append(player.inventory[i]['name'])
            
            # Floor cleared - ask to continue
            clear_screen()
            print(colorize("=" * 60, Colors.BRIGHT_GREEN))
            print(colorize(f"✅  FLOOR {lair_level} CLEARED!  ✅", Colors.BRIGHT_GREEN + Colors.BOLD))
            print(colorize("=" * 60, Colors.BRIGHT_GREEN))
            print(f"\n{colorize('Your Status:', Colors.BRIGHT_CYAN + Colors.BOLD)}")
            print(f"{colorize('HP:', Colors.WHITE)} {health_bar(player.hp, player.max_hp)}")
            print(f"{colorize('Total Loot This Run:', Colors.BRIGHT_YELLOW)} {len(lair_loot_gained)} items, {lair_gold_gained} gold")
            print(colorize("=" * 60, Colors.BRIGHT_GREEN))
            print(f"\n{colorize('1. Continue to Floor', Colors.BRIGHT_GREEN)} {colorize(str(lair_level + 1), Colors.BRIGHT_CYAN)}")
            print(f"{colorize('2. Leave Lair', Colors.BRIGHT_YELLOW)} {colorize('(Keep all loot)', Colors.WHITE)}")
            print(colorize("=" * 60, Colors.BRIGHT_GREEN))
            
            continue_choice = input(f"\n{colorize('What do you do?', Colors.BRIGHT_CYAN)} ").strip()
            
            if continue_choice == '1':
                lair_level += 1
                continue
            elif continue_choice == '2':
                # Successful exit - keep all loot
                clear_screen()
                print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
                print(colorize("🏆  LAIR EXIT  🏆", Colors.BRIGHT_YELLOW + Colors.BOLD))
                print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
                print(f"\n{colorize('You successfully cleared', Colors.WHITE)} {colorize(str(lair_level), Colors.BRIGHT_CYAN + Colors.BOLD)} {colorize('floors!', Colors.WHITE)}")
                print(f"\n{colorize('Loot Kept:', Colors.BRIGHT_GREEN + Colors.BOLD)}")
                print(f"  {colorize('Items:', Colors.WHITE)} {len(lair_loot_gained)}")
                print(f"  {colorize('Gold:', Colors.BRIGHT_YELLOW)} {lair_gold_gained}")
                print(f"  {colorize('Experience:', Colors.BRIGHT_GREEN)} {lair_exp_gained}")
                input(f"\n{colorize('Press Enter to return...', Colors.WHITE)}")
                return 'previous'
            else:
                print(f"\n{colorize('Invalid choice, continuing...', Colors.YELLOW)}")
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                lair_level += 1
                continue
        
        elif choice == '2':
            # Leave tower with all loot
            if lair_level > 1:
                clear_screen()
                print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
                print(colorize("🏆  LAIR EXIT  🏆", Colors.BRIGHT_YELLOW + Colors.BOLD))
                print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
                floors_cleared = lair_level
                print(f"\n{colorize('You cleared', Colors.WHITE)} {colorize(str(floors_cleared), Colors.BRIGHT_CYAN + Colors.BOLD)} {colorize('floors!', Colors.WHITE)}")
                print(f"\n{colorize('Loot Kept:', Colors.BRIGHT_GREEN + Colors.BOLD)}")
                print(f"  {colorize('Items:', Colors.WHITE)} {len(lair_loot_gained)}")
                print(f"  {colorize('Gold:', Colors.BRIGHT_YELLOW)} {lair_gold_gained}")
                print(f"  {colorize('Experience:', Colors.BRIGHT_GREEN)} {lair_exp_gained}")
                
                # Update highest tower floor and check achievements
                if floors_cleared > player.highest_tower_floor:
                    player.highest_tower_floor = floors_cleared
                check_achievements(player, 'tower_floor', floors_cleared)
                
                input(f"\n{colorize('Press Enter to return...', Colors.BRIGHT_CYAN)}")
            return 'previous'  # Changed from 'town' to 'previous' for consistency
        else:
            print(f"\n{colorize('❌ Invalid choice!', Colors.BRIGHT_RED)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")


def explore_multi_floor_dungeon(player, dungeon_name, floors, start_floor='b1'):
    """
    Explore a multi-floor dungeon (B1, B2, B3)
    
    Args:
        player: Player object
        dungeon_name: Base name of dungeon (e.g., 'eslania_dungeon', 'asylion_dungeon')
        floors: Dict mapping floor keys to level requirements and multipliers
                e.g., {'b1': {'level': 5, 'multiplier': 1.0}, ...}
        start_floor: Starting floor key (default 'b1')
    """
    current_floor_key = start_floor
    dungeon_loot_gained = []
    dungeon_gold_gained = 0
    dungeon_exp_gained = 0
    
    # Save player state before entering dungeon
    original_inventory = [item.copy() for item in player.inventory]
    original_gold = player.gold
    original_exp = player.exp
    original_hp = player.hp
    
    while True:
        clear_screen()
        floor_key = current_floor_key
        floor_data = floors[floor_key]
        location_key = f"{dungeon_name}_{floor_key}"
        location = LOCATIONS[location_key]
        
        print(colorize("=" * 60, Colors.BRIGHT_RED))
        print(colorize(f"🗡️  {location.name.upper()}  🗡️", Colors.BRIGHT_RED + Colors.BOLD))
        print(colorize("=" * 60, Colors.BRIGHT_RED))
        print(f"\n{colorize(location.description, Colors.WHITE)}")
        print(f"\n{colorize('YOUR STATUS:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
        print(f"  {colorize('Level:', Colors.WHITE)} {colorize(str(player.level), Colors.BRIGHT_GREEN)}")
        print(f"  {colorize('HP:', Colors.BRIGHT_RED)} {health_bar(player.hp, player.max_hp)}")
        print(f"  {colorize('Current Floor:', Colors.WHITE)} {colorize(floor_key.upper(), Colors.BRIGHT_CYAN + Colors.BOLD)}")
        print(f"  {colorize('Loot Gained:', Colors.BRIGHT_YELLOW)} {len(dungeon_loot_gained)} items, {dungeon_gold_gained} gold")
        
        # Check if player can proceed to next floor
        next_floor_key = None
        prev_floor_key = None
        floor_keys_list = list(floors.keys())
        current_index = floor_keys_list.index(floor_key)
        if current_index < len(floor_keys_list) - 1:
            next_floor_key = floor_keys_list[current_index + 1]
            next_floor_data = floors[next_floor_key]
        if current_index > 0:
            prev_floor_key = floor_keys_list[current_index - 1]
        
        print(colorize("\n" + "=" * 60, Colors.BRIGHT_RED))
        option_num = 1
        print(f"{colorize(f'{option_num}.', Colors.BRIGHT_GREEN)} Explore {colorize(floor_key.upper(), Colors.BRIGHT_CYAN)}")
        option_num += 1
        
        # Initialize option variables
        next_floor_option = None
        prev_floor_option = None
        leave_option = None
        
        # Option to go deeper (if available and player meets level requirement)
        if next_floor_key:
            if player.level >= next_floor_data['level']:
                print(f"{colorize(f'{option_num}.', Colors.BRIGHT_YELLOW)} Go Deeper to {colorize(next_floor_key.upper(), Colors.BRIGHT_CYAN)}")
                next_floor_option = option_num
                option_num += 1
            else:
                print(f"{colorize(f'{option_num}.', Colors.WHITE)} {colorize(f'Go Deeper to {next_floor_key.upper()} (Requires Level {next_floor_data["level"]})', Colors.GRAY)}")
                option_num += 1
        
        # Option to go back (if not on B1)
        if prev_floor_key:
            print(f"{colorize(f'{option_num}.', Colors.BRIGHT_BLUE)} Go Back to {colorize(prev_floor_key.upper(), Colors.BRIGHT_CYAN)}")
            prev_floor_option = option_num
            option_num += 1
        
        # Option to leave dungeon (only from B1)
        if not prev_floor_key:
            print(f"{colorize(f'{option_num}.', Colors.BRIGHT_BLUE)} Leave Dungeon {colorize('(Return to previous area)', Colors.WHITE)}")
            leave_option = option_num
        
        print(colorize("=" * 60, Colors.BRIGHT_RED))
        
        choice = input(f"\n{colorize('What do you do?', Colors.BRIGHT_CYAN)} ").strip()
        
        try:
            choice_num = int(choice)
        except ValueError:
            choice_num = 0
        
        if choice_num == 1:
            # Generate scaled enemy for this floor
            floor_data = floors[floor_key]
            difficulty_level = floor_data['level']
            location_multiplier = floor_data['multiplier']
            
            # Choose enemy tier based on dungeon and floor level
            # Limbo Dungeon: Tier 1 (beginner dungeon, levels 1-5)
            if dungeon_name == 'limbo_dungeon':
                enemy_pool = [e for e in BASE_ENEMIES if e['tier'] == 1]
            # Rhaom Dungeon: Tiers 1-2 (levels 3-10)
            elif dungeon_name == 'rhaom_dungeon':
                enemy_pool = [e for e in BASE_ENEMIES if e['tier'] <= 2]
            # Lost Taiyan: Tiers 2-3 (levels 8-16)
            elif dungeon_name == 'lost_taiyan':
                enemy_pool = [e for e in BASE_ENEMIES if 2 <= e['tier'] <= 3]
            # Eslania Dungeon: Tiers 2-3 (levels 5-15)
            elif dungeon_name == 'eslania_dungeon':
                enemy_pool = [e for e in BASE_ENEMIES if 2 <= e['tier'] <= 3]
            # Asylion Dungeon: Tiers 3-4 (levels 8-18)
            elif dungeon_name == 'asylion_dungeon':
                enemy_pool = [e for e in BASE_ENEMIES if 3 <= e['tier'] <= 4]
            # Fallback: Use floor level to determine tier range
            else:
                if floor_data['level'] <= 5:
                    enemy_pool = [e for e in BASE_ENEMIES if e['tier'] == 1]
                elif floor_data['level'] <= 15:
                    enemy_pool = [e for e in BASE_ENEMIES if e['tier'] <= 2]
                elif floor_data['level'] <= 30:
                    enemy_pool = [e for e in BASE_ENEMIES if e['tier'] <= 3]
                elif floor_data['level'] <= 50:
                    enemy_pool = [e for e in BASE_ENEMIES if e['tier'] <= 4]
                elif floor_data['level'] <= 73:
                    enemy_pool = [e for e in BASE_ENEMIES if e['tier'] <= 5]
                else:
                    enemy_pool = BASE_ENEMIES  # All tiers for end game
            
            enemy_template = random.choice(enemy_pool).copy()
            enemy_data = scale_enemy(enemy_template, difficulty_level, location_multiplier)
            
            enemy = Enemy(
                name=f"{enemy_data['name']} ({floor_key.upper()})",
                hp=enemy_data['hp'],
                attack=enemy_data['attack'],
                defense=enemy_data['defense'],
                exp_reward=enemy_data['exp'],
                gold_reward=enemy_data['gold'],
                drops=enemy_data.get('drops', [])
            )
            enemy.is_boss = enemy_data.get('is_boss', False)
            
            # Store state before combat
            pre_combat_inventory_count = len(player.inventory)
            pre_combat_gold = player.gold
            pre_combat_exp = player.exp
            
            won = combat(player, enemy)
            
            if not won:
                # Player died
                clear_screen()
                print(colorize("=" * 60, Colors.BRIGHT_RED))
                print(colorize("💀  DUNGEON DEATH  💀", Colors.BRIGHT_RED + Colors.BOLD))
                print(colorize("=" * 60, Colors.BRIGHT_RED))
                print(f"\n{colorize('You have fallen in the dungeon!', Colors.BRIGHT_RED)}")
                
                # Restore player to pre-dungeon state
                player.inventory = [item.copy() for item in original_inventory]
                player.gold = original_gold
                player.exp = original_exp
                player.hp = REVIVE_HP  # Revive with 1 HP
                
                input(f"\n{colorize('Press Enter to return to previous area...', Colors.WHITE)}")
                return 'previous'  # Signal to return to previous area
            
            # Track gains
            gold_gained = player.gold - pre_combat_gold
            exp_gained = player.exp - pre_combat_exp
            dungeon_gold_gained += gold_gained
            dungeon_exp_gained += exp_gained
            
            items_gained = len(player.inventory) - pre_combat_inventory_count
            if items_gained > 0:
                for i in range(pre_combat_inventory_count, len(player.inventory)):
                    dungeon_loot_gained.append(player.inventory[i]['name'])
            
            continue
        
        elif choice_num == next_floor_option and next_floor_key and player.level >= next_floor_data['level']:
            # Go deeper to next floor
            current_floor_key = next_floor_key
            continue
        elif choice_num == prev_floor_option and prev_floor_key:
            # Go back to previous floor
            current_floor_key = prev_floor_key
            continue
        elif choice_num == leave_option:
            # Leave dungeon
            clear_screen()
            print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
            print(colorize("🏆  DUNGEON EXIT  🏆", Colors.BRIGHT_YELLOW + Colors.BOLD))
            print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
            print(f"\n{colorize('You successfully explored the dungeon!', Colors.WHITE)}")
            print(f"\n{colorize('Loot Gained:', Colors.BRIGHT_GREEN + Colors.BOLD)}")
            print(f"  {colorize('Items:', Colors.WHITE)} {len(dungeon_loot_gained)}")
            print(f"  {colorize('Gold:', Colors.BRIGHT_YELLOW)} {dungeon_gold_gained}")
            print(f"  {colorize('Experience:', Colors.BRIGHT_GREEN)} {dungeon_exp_gained}")
            input(f"\n{colorize('Press Enter to return...', Colors.BRIGHT_CYAN)}")
            return 'previous'
        else:
            print(f"\n{colorize('❌ Invalid choice!', Colors.BRIGHT_RED)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")

