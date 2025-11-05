"""Combat system implementation"""
import random
from ..config import DEV_FLAGS
from ..constants import (
    DODGE_CAP, DODGE_CALCULATION_DIVISOR, BOSS_ACCURACY_FLOOR, RUN_CHANCE,
    ENEMY_ATTACK_MIN_VARIANCE, ENEMY_ATTACK_MAX_VARIANCE,
    MIN_DAMAGE_RATIO, MIN_DAMAGE_ALWAYS,
    CRIT_CHANCE_MAX, CRIT_DEX_DIVISOR,
    CRIT_MULTIPLIER_MIN, CRIT_MULTIPLIER_MAX,
    DEX_PRECISION_INTERVAL, DEX_PRECISION_BONUS,
    DEX_DAMAGE_DIVISOR, DEX_UPPER_RANGE_RATIO,
    GUARANTEED_FLEE_GOLD_COST,
    KILL_STREAK_NOTIFICATION_INTERVAL,
    NOTIFICATION_DURATION_NORMAL, NOTIFICATION_DURATION_LONG,
    ENEMY_SCALE_BASE, ENEMY_SCALE_MULTIPLIER, ENEMY_SCALE_DECAY
)
from ..ui import Colors, colorize, clear_screen, show_notification, health_bar
from ..items import DROP_ITEMS, add_item_to_inventory, remove_item_from_inventory, get_item_quantity, format_item_name
from ..achievements.system import check_achievements
from ..game.stats import allocate_stats

NIGHT_MONSTER_HP_BUFF = 1.30
NIGHT_MONSTER_ATTACK_BUFF = 1.30
NIGHT_DROP_RATE_BUFF = 1.50


def is_nighttime(player):
    """Check if it's currently nighttime based on player's world clock"""
    from ..systems.time_system import GameClock
    clock = GameClock(player.world_anchor_timestamp)
    return clock.is_night()


def scale_enemy(enemy_template, player_level, location_multiplier=1.0, player=None):
    """Scale enemy stats based on player level and location"""
    level_diff = max(0, player_level - enemy_template['tier'])
    base_scaler = ENEMY_SCALE_BASE + (1 - (ENEMY_SCALE_DECAY ** level_diff)) * ENEMY_SCALE_MULTIPLIER
    scale_factor = base_scaler * location_multiplier
    
    hp = int(enemy_template['base_hp'] * scale_factor)
    attack = int(enemy_template['base_attack'] * scale_factor)
    defense = int(enemy_template['base_defense'] * scale_factor)
    exp = int(enemy_template['base_exp'] * scale_factor)
    gold = int(enemy_template['base_gold'] * scale_factor)
    
    is_night = False
    if player and hasattr(player, 'world_anchor_timestamp'):
        is_night = is_nighttime(player)
        if is_night:
            hp = int(hp * NIGHT_MONSTER_HP_BUFF)
            attack = int(attack * NIGHT_MONSTER_ATTACK_BUFF)
    
    return {
        'name': enemy_template['name'],
        'hp': hp,
        'attack': attack,
        'defense': defense,
        'exp': exp,
        'gold': gold,
        'drops': enemy_template['drops'],
        'tier': enemy_template.get('tier', 1),
        'is_boss': enemy_template.get('is_boss', False),
        'is_night': is_night
    }


def combat(player, enemy):
    # Reset guaranteed flee flag at combat start
    player._guaranteed_flee_used = False
    
    clear_screen()
    print(colorize("=" * 60, Colors.BRIGHT_RED))
    
    # Show night battle indicator if enemy spawned at night
    if hasattr(enemy, 'is_night') and enemy.is_night:
        print(colorize("🌙  NIGHT BATTLE - ENEMIES EMPOWERED!  🌙", Colors.BRIGHT_MAGENTA + Colors.BOLD))
        print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
        print(colorize("⚠️  +30% HP & ATK | +50% Drop Rate  ⚠️", Colors.BRIGHT_YELLOW + Colors.BOLD))
    else:
        print(colorize("⚔️  BATTLE BEGINS! ⚔️", Colors.BRIGHT_RED + Colors.BOLD))
    
    print(colorize("=" * 60, Colors.BRIGHT_RED))
    
    while player.is_alive() and enemy.is_alive():
        # Improved combat display
        print("\n" + colorize("─" * 60, Colors.CYAN))
        print(colorize(f"⚔️  {player.name.upper()}  ⚔️", Colors.BRIGHT_CYAN + Colors.BOLD))
        print(colorize(f"Level {player.level}", Colors.CYAN))
        print(f"{colorize('HP:', Colors.BRIGHT_RED + Colors.BOLD)} {health_bar(player.hp, player.max_hp)}")
        print(f"{colorize('Attack:', Colors.YELLOW)} {colorize(str(player.get_max_attack_power()), Colors.BRIGHT_YELLOW)} | {colorize('Defense:', Colors.BLUE)} {colorize(str(player.get_defense_power()), Colors.BRIGHT_BLUE)}")
        
        print("\n" + colorize("─" * 60, Colors.RED))
        print(colorize(f"👹  {enemy.name.upper()}  👹", Colors.BRIGHT_RED + Colors.BOLD))
        print(f"{colorize('HP:', Colors.BRIGHT_RED + Colors.BOLD)} {health_bar(enemy.hp, enemy.max_hp)}")
        print(f"{colorize('Attack:', Colors.YELLOW)} {colorize(str(enemy.attack), Colors.BRIGHT_YELLOW)} | {colorize('Defense:', Colors.BLUE)} {colorize(str(enemy.defense), Colors.BRIGHT_BLUE)}")
        print(colorize("=" * 60, Colors.BRIGHT_RED))
        
        print(f"\n{colorize('COMBAT OPTIONS:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
        print(f"  {colorize('1.', Colors.BRIGHT_GREEN)} Attack")
        print(f"  {colorize('2.', Colors.BRIGHT_YELLOW)} Use Potion")
        print(f"  {colorize('3.', Colors.BRIGHT_BLUE)} Try to Run")
        # Guaranteed Flee (safety valve): once per combat, costs streak reset
        if not hasattr(player, '_guaranteed_flee_used'):
            player._guaranteed_flee_used = False
        if not player._guaranteed_flee_used:
            print(f"  {colorize('4.', Colors.BRIGHT_RED)} Guaranteed Flee {colorize('(Resets kill streak, costs 5% gold)', Colors.YELLOW)}")
        
        choice = input(f"\n{colorize('What do you do?', Colors.BRIGHT_CYAN)} ").strip()
        
        if choice == '1':
            # Calculate damage based on STR and DEX
            max_damage = player.get_max_attack_power()
            min_damage = max(MIN_DAMAGE_ALWAYS, int(max_damage * MIN_DAMAGE_RATIO))  # Minimum damage is half of max
            
            # Critical hit chance based on DEX (Kal Online style)
            crit_chance = min(CRIT_CHANCE_MAX, player.dex / CRIT_DEX_DIVISOR)  # Max 25% crit at 50 DEX
            is_crit = random.random() < crit_chance
            
            # DEX affects damage distribution: higher DEX = more likely to hit near max
            dex_bonus = player.dex / DEX_DAMAGE_DIVISOR  # DEX/100 gives % chance for max damage range
            roll = random.random()
            
            # DEX precision floor: every 20 DEX grants +5% minimum damage floor (before defense)
            # This ensures DEX feels impactful even without crits
            precision_bonus = (player.dex // DEX_PRECISION_INTERVAL) * DEX_PRECISION_BONUS  # +5% per 20 DEX, max 25% at 100 DEX
            min_damage_with_precision = int(min_damage * (1 + precision_bonus))
            
            if is_crit:
                # Critical hit: 1.5x-2x damage
                crit_multiplier = random.uniform(CRIT_MULTIPLIER_MIN, CRIT_MULTIPLIER_MAX)
                player_damage = int(max_damage * crit_multiplier)
                crit_msg = " CRITICAL HIT!"
                print(f"\n{colorize('⚔️', Colors.BRIGHT_YELLOW)} {colorize('You attack', Colors.CYAN)} {colorize(enemy.name, Colors.BRIGHT_RED)} {colorize('for', Colors.WHITE)} {colorize(str(player_damage), Colors.BRIGHT_YELLOW + Colors.BOLD)} {colorize('damage!', Colors.CYAN)}{colorize(crit_msg, Colors.BRIGHT_YELLOW + Colors.BOLD)}")
            elif roll < dex_bonus:
                # High DEX: hit in upper 60% of damage range
                upper_range = int((max_damage - min_damage_with_precision) * DEX_UPPER_RANGE_RATIO)
                player_damage = random.randint(max(max_damage - upper_range, min_damage_with_precision), max_damage)
                print(f"\n{colorize('⚔️', Colors.BRIGHT_RED)} {colorize('You attack', Colors.CYAN)} {colorize(enemy.name, Colors.BRIGHT_RED)} {colorize('for', Colors.WHITE)} {colorize(str(player_damage), Colors.BRIGHT_RED + Colors.BOLD)} {colorize('damage!', Colors.CYAN)}")
            else:
                # Normal: hit in full damage range (with precision floor)
                player_damage = random.randint(min_damage_with_precision, max_damage)
                print(f"\n{colorize('⚔️', Colors.BRIGHT_RED)} {colorize('You attack', Colors.CYAN)} {colorize(enemy.name, Colors.BRIGHT_RED)} {colorize('for', Colors.WHITE)} {colorize(str(player_damage), Colors.BRIGHT_RED + Colors.BOLD)} {colorize('damage!', Colors.CYAN)}")
            
            enemy.take_damage(player_damage)
            
            if not enemy.is_alive():
                # Set enemy HP to 0 for display
                enemy.hp = 0
                
                # Show victory screen
                clear_screen()
                print(colorize("=" * 60, Colors.BRIGHT_GREEN))
                print(colorize("         ⚔️  VICTORY! ⚔️", Colors.BRIGHT_GREEN + Colors.BOLD))
                print(colorize("=" * 60, Colors.BRIGHT_GREEN))
                
                # Show defeated enemy
                print("\n" + colorize("DEFEATED ENEMY:", Colors.BRIGHT_RED + Colors.BOLD))
                print("-" * 60)
                print(colorize(f"{enemy.name}", Colors.BRIGHT_RED + Colors.BOLD))
                print(f"{colorize('HP:', Colors.WHITE)} {health_bar(enemy.hp, enemy.max_hp)}")
                
                # Show player state
                print("\n" + colorize("YOUR STATUS:", Colors.BRIGHT_CYAN + Colors.BOLD))
                print("-" * 60)
                print(colorize(f"{player.name} (Level {player.level})", Colors.BRIGHT_CYAN))
                print(f"{colorize('HP:', Colors.WHITE)} {health_bar(player.hp, player.max_hp)}")
                print(f"{colorize('Experience:', Colors.CYAN)} {colorize(str(player.exp), Colors.WHITE)}/{colorize(str(player.exp_to_next), Colors.WHITE)}")
                print(f"{colorize('Gold:', Colors.BRIGHT_YELLOW)} {colorize(str(player.gold), Colors.BRIGHT_YELLOW)}")
                
                # Award rewards
                print("\n" + colorize("REWARDS:", Colors.BRIGHT_YELLOW + Colors.BOLD))
                print("-" * 60)
                
                # Store old values for display
                old_exp = player.exp
                old_gold = player.gold
                
                player.exp += enemy.exp_reward
                player.gold += enemy.gold_reward
                
                # Check wealth achievements after gold gain
                check_achievements(player, 'wealth')
                
                print(f"{colorize('💰', Colors.BRIGHT_YELLOW)} {colorize('Experience:', Colors.WHITE)} +{colorize(str(enemy.exp_reward), Colors.BRIGHT_GREEN)} ({colorize(str(old_exp), Colors.WHITE)} → {colorize(str(player.exp), Colors.BRIGHT_GREEN)})")
                print(f"{colorize('💰', Colors.BRIGHT_YELLOW)} {colorize('Gold:', Colors.WHITE)} +{colorize(str(enemy.gold_reward), Colors.BRIGHT_YELLOW)} ({colorize(str(old_gold), Colors.WHITE)} → {colorize(str(player.gold), Colors.BRIGHT_YELLOW)})")
                
                # Handle drops with rarity display (OSRS-style)
                drops_received = []
                if enemy.drops:
                    # Calculate night drop bonus
                    drop_multiplier = NIGHT_DROP_RATE_BUFF if hasattr(enemy, 'is_night') and enemy.is_night else 1.0
                    
                    for drop in enemy.drops:
                        # Apply night bonus to drop rate (multiplicative, capped at 100%)
                        adjusted_drop_chance = min(1.0, drop['chance'] * drop_multiplier)
                        
                        if random.random() < adjusted_drop_chance:
                            item_id = drop['item']
                            if item_id not in DROP_ITEMS:
                                import sys
                                print(f"\nWARNING: Missing item definition '{item_id}' - skipping drop", file=sys.stderr)
                                continue
                            
                            drop_item = DROP_ITEMS[item_id].copy()
                            add_item_to_inventory(player.inventory, drop_item)
                            drops_received.append(drop_item)
                            
                            if drop_item.get('type') == 'talisman':
                                check_achievements(player, 'talisman_found')
                                if drop_item.get('name') == 'Talisman of the Hacker':
                                    check_achievements(player, 'talisman_hacker')
                                check_achievements(player, 'talisman_count')
                    
                    if drops_received:
                        print(f"\n{colorize('📦', Colors.BRIGHT_CYAN)} {colorize('LOOT OBTAINED:', Colors.BRIGHT_CYAN + Colors.BOLD)}")
                        print("-" * 60)
                        for drop_item in drops_received:
                            formatted_name = format_item_name(drop_item)
                            print(f"  {colorize('•', Colors.BRIGHT_CYAN)} {formatted_name}")
                
                player.kill_streak += 1
                player.total_kills += 1
                
                if player.kill_streak % KILL_STREAK_NOTIFICATION_INTERVAL == 0 and player.kill_streak > 0:
                    show_notification(f"Kill Streak: {player.kill_streak}!", Colors.BRIGHT_RED, NOTIFICATION_DURATION_NORMAL)
                
                check_achievements(player, 'kills')
                check_achievements(player, 'streak')
                
                # Check for level up
                while player.exp >= player.exp_to_next:
                    if player.level_up():
                        check_achievements(player, 'level')
                        allocate_stats(player)
                        # Refresh display after level up
                        clear_screen()
                        print(colorize("=" * 60, Colors.BRIGHT_GREEN))
                        print(colorize("         ⚔️  VICTORY! ⚔️", Colors.BRIGHT_GREEN + Colors.BOLD))
                        print(colorize("=" * 60, Colors.BRIGHT_GREEN))
                        print("\n" + colorize("DEFEATED ENEMY:", Colors.BRIGHT_RED + Colors.BOLD))
                        print("-" * 60)
                        print(colorize(f"{enemy.name}", Colors.BRIGHT_RED + Colors.BOLD))
                        print(f"{colorize('HP:', Colors.WHITE)} {health_bar(0, enemy.max_hp)}")
                        print("\n" + colorize("YOUR STATUS:", Colors.BRIGHT_CYAN + Colors.BOLD))
                        print("-" * 60)
                        print(colorize(f"{player.name} (Level {player.level})", Colors.BRIGHT_CYAN))
                        print(f"{colorize('HP:', Colors.WHITE)} {health_bar(player.hp, player.max_hp)}")
                        print(f"{colorize('Experience:', Colors.CYAN)} {colorize(str(player.exp), Colors.WHITE)}/{colorize(str(player.exp_to_next), Colors.WHITE)}")
                        print(f"{colorize('Gold:', Colors.BRIGHT_YELLOW)} {colorize(str(player.gold), Colors.BRIGHT_YELLOW)}")
                
                print("\n" + colorize("=" * 60, Colors.BRIGHT_GREEN))
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                return True
            
            # Enemy attacks - check for dodge
            enemy_damage = random.randint(
                max(MIN_DAMAGE_ALWAYS, enemy.attack + ENEMY_ATTACK_MIN_VARIANCE),
                enemy.attack + ENEMY_ATTACK_MAX_VARIANCE
            )
            # AGL affects dodge chance: higher AGL = better chance to dodge
            # Reduced cap to 35% (from 50%) to prevent trivialization
            base_dodge = min(DODGE_CAP, player.agl / DODGE_CALCULATION_DIVISOR)  # Max 35% dodge at 35 AGL
            
            # Boss accuracy floor: bosses/elites have at least 10% hit chance
            is_boss = hasattr(enemy, 'is_boss') and enemy.is_boss
            accuracy_floor = BOSS_ACCURACY_FLOOR if is_boss else 0.0
            dodge_chance = min(base_dodge, 1.0 - accuracy_floor)
            
            if random.random() < dodge_chance:
                attack_msg = "'s attack!"
                print(f"\n{colorize('✨', Colors.BRIGHT_CYAN)} {colorize('You dodged', Colors.BRIGHT_GREEN)} {colorize(enemy.name, Colors.BRIGHT_RED)} {colorize(attack_msg, Colors.WHITE)}")
            else:
                damage_taken = player.take_damage(enemy_damage)
                print(f"\n{colorize('💥', Colors.BRIGHT_RED)} {colorize(enemy.name, Colors.BRIGHT_RED)} {colorize('attacks you for', Colors.WHITE)} {colorize(str(damage_taken), Colors.BRIGHT_RED + Colors.BOLD)} {colorize('damage!', Colors.WHITE)}")
            
            if not player.is_alive():
                # Handle death with enhanced death screen and respawn
                from ..game.death import handle_combat_death
                return handle_combat_death(player, enemy.name)
        
        elif choice == '2':
            # Use healing item - find all consumables
            healing_items = []
            for item in player.inventory:
                if item.get('type') == 'consumable' and 'heal' in item and item.get('heal', 0) > 0:
                    healing_items.append(item)
            
            if not healing_items:
                error_msg = "❌ You don't have any healing items!"
                print(f"\n{colorize(error_msg, Colors.BRIGHT_RED)}")
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                clear_screen()
                print(colorize("=" * 60, Colors.CYAN))
                print(colorize("⚔️  BATTLE CONTINUES! ⚔️", Colors.BRIGHT_RED + Colors.BOLD))
                print(colorize("=" * 60, Colors.CYAN))
                continue
            
            # If only one type of healing item or quantity is 1, use it directly
            healing_item = healing_items[0]
            item_qty = get_item_quantity(healing_item)
            
            use_qty = 1
            if item_qty > 1:
                # Show selection menu for quantity
                clear_screen()
                print(colorize("=" * 60, Colors.CYAN))
                print(colorize("🧪  USE POTION  🧪", Colors.BRIGHT_GREEN + Colors.BOLD))
                print(colorize("=" * 60, Colors.CYAN))
                formatted_name = format_item_name(healing_item)
                print(f"\n{colorize('Item:', Colors.WHITE)} {formatted_name}")
                print(f"{colorize('Heal Amount:', Colors.WHITE)} {colorize(str(healing_item['heal']), Colors.BRIGHT_GREEN)} HP")
                print(f"{colorize('Quantity Available:', Colors.WHITE)} {colorize(str(item_qty), Colors.BRIGHT_YELLOW)}")
                print(f"\n{colorize('How many to use?', Colors.BRIGHT_CYAN)}")
                print(f"  {colorize('1.', Colors.WHITE)} Use 1")
                if item_qty >= 5:
                    print(f"  {colorize('2.', Colors.WHITE)} Use 5")
                if item_qty >= 10:
                    print(f"  {colorize('3.', Colors.WHITE)} Use 10")
                print(f"  {colorize('4.', Colors.WHITE)} Use All ({item_qty})")
                print(f"  {colorize('5.', Colors.WHITE)} Cancel")
                print(colorize("=" * 60, Colors.CYAN))
                
                qty_choice = input(f"\n{colorize('Choice:', Colors.BRIGHT_CYAN)} ").strip()
                if qty_choice == '1':
                    use_qty = 1
                elif qty_choice == '2' and item_qty >= 5:
                    use_qty = min(5, item_qty)
                elif qty_choice == '3' and item_qty >= 10:
                    use_qty = min(10, item_qty)
                elif qty_choice == '4':
                    use_qty = item_qty
                elif qty_choice == '5':
                    clear_screen()
                    print(colorize("=" * 60, Colors.CYAN))
                    print(colorize("⚔️  BATTLE CONTINUES! ⚔️", Colors.BRIGHT_RED + Colors.BOLD))
                    print(colorize("=" * 60, Colors.CYAN))
                    continue
                else:
                    use_qty = 1
            
            # Use the potion(s) with anti-overheal logic
            total_healed = 0
            items_used = 0
            
            for _ in range(use_qty):
                if player.hp >= player.max_hp:
                    break  # Already at max HP, stop using items
                
                healing_amount = healing_item.get('heal', 0)
                actual_heal = min(healing_amount, player.max_hp - player.hp)
                player.heal(actual_heal)
                total_healed += actual_heal
                items_used += 1
                remove_item_from_inventory(player.inventory, healing_item, 1)
            
            # Display result
            if total_healed > 0:
                if items_used > 1:
                    print(f"\n{colorize('🧪', Colors.BRIGHT_GREEN)} {colorize(f'You used {items_used}x', Colors.WHITE)} {colorize(healing_item['name'], Colors.BRIGHT_CYAN)} {colorize('and healed', Colors.WHITE)} {colorize(str(total_healed), Colors.BRIGHT_GREEN + Colors.BOLD)} {colorize('HP!', Colors.WHITE)}")
                else:
                    print(f"\n{colorize('🧪', Colors.BRIGHT_GREEN)} {colorize('You used', Colors.WHITE)} {colorize(healing_item['name'], Colors.BRIGHT_CYAN)} {colorize('and healed', Colors.WHITE)} {colorize(str(total_healed), Colors.BRIGHT_GREEN + Colors.BOLD)} {colorize('HP!', Colors.WHITE)}")
                
                if items_used < use_qty:
                    print(f"{colorize('ℹ️', Colors.BRIGHT_CYAN)} {colorize('(Capped at max HP - no overheal)', Colors.CYAN)}")
            else:
                print(f"\n{colorize('ℹ️', Colors.BRIGHT_CYAN)} {colorize('Already at full HP!', Colors.CYAN)}")
            
            # Continue combat
            clear_screen()
            print(colorize("=" * 60, Colors.CYAN))
            print(colorize("⚔️  BATTLE CONTINUES! ⚔️", Colors.BRIGHT_RED + Colors.BOLD))
            print(colorize("=" * 60, Colors.CYAN))
            
            # Enemy attacks - check for dodge
            enemy_damage = random.randint(
                max(MIN_DAMAGE_ALWAYS, enemy.attack + ENEMY_ATTACK_MIN_VARIANCE),
                enemy.attack + ENEMY_ATTACK_MAX_VARIANCE
            )
            # Reduced cap to 35% (from 50%) to prevent trivialization
            base_dodge = min(DODGE_CAP, player.agl / DODGE_CALCULATION_DIVISOR)  # Max 35% dodge at 35 AGL
            
            # Boss accuracy floor: bosses/elites have at least 10% hit chance
            is_boss = hasattr(enemy, 'is_boss') and enemy.is_boss
            accuracy_floor = BOSS_ACCURACY_FLOOR if is_boss else 0.0
            dodge_chance = min(base_dodge, 1.0 - accuracy_floor)
            
            if random.random() < dodge_chance:
                attack_msg = "'s attack!"
                print(f"\n{colorize('✨', Colors.BRIGHT_CYAN)} {colorize('You dodged', Colors.BRIGHT_GREEN)} {colorize(enemy.name, Colors.BRIGHT_RED)} {colorize(attack_msg, Colors.WHITE)}")
            else:
                damage_taken = player.take_damage(enemy_damage)
                print(f"\n{colorize('💥', Colors.BRIGHT_RED)} {colorize(enemy.name, Colors.BRIGHT_RED)} {colorize('attacks you for', Colors.WHITE)} {colorize(str(damage_taken), Colors.BRIGHT_RED + Colors.BOLD)} {colorize('damage!', Colors.WHITE)}")
            
            if not player.is_alive():
                # Handle death with enhanced death screen and respawn
                from ..game.death import handle_combat_death
                return handle_combat_death(player, enemy.name)
        elif choice == '4' and not player._guaranteed_flee_used:
            # Guaranteed Flee safety valve
            player._guaranteed_flee_used = True
            streak_lost = player.kill_streak
            gold_cost = max(MIN_DAMAGE_ALWAYS, int(player.gold * GUARANTEED_FLEE_GOLD_COST))
            
            player.kill_streak = 0
            player.gold -= gold_cost
            
            print(f"\n{colorize('🚪', Colors.BRIGHT_BLUE)} {colorize('You use Guaranteed Flee!', Colors.BRIGHT_GREEN)}")
            if streak_lost > 0:
                print(f"{colorize('❌', Colors.BRIGHT_RED)} {colorize(f'Kill streak reset: {streak_lost}', Colors.YELLOW)}")
            if gold_cost > 0:
                print(f"{colorize('💰', Colors.YELLOW)} {colorize(f'Lost {gold_cost} gold as escape cost.', Colors.WHITE)}")
            print(f"{colorize('✅', Colors.BRIGHT_GREEN)} {colorize('You escaped safely!', Colors.BRIGHT_GREEN)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
            return True
        
        elif choice == '3':
            run_chance = random.random()
            if run_chance > RUN_CHANCE:
                print(f"\n{colorize('🏃', Colors.BRIGHT_BLUE)} {colorize('You successfully ran away!', Colors.BRIGHT_GREEN)}")
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                return True
            else:
                escape_msg = "You couldn't escape!"
                print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(escape_msg, Colors.YELLOW)}")
                enemy_damage = random.randint(
                    max(MIN_DAMAGE_ALWAYS, enemy.attack + ENEMY_ATTACK_MIN_VARIANCE),
                    enemy.attack + ENEMY_ATTACK_MAX_VARIANCE
                )
                # Reduced cap to 35% (from 50%) to prevent trivialization
                base_dodge = min(DODGE_CAP, player.agl / DODGE_CALCULATION_DIVISOR)  # Max 35% dodge at 35 AGL
                
                # Boss accuracy floor: bosses/elites have at least 10% hit chance
                is_boss = hasattr(enemy, 'is_boss') and enemy.is_boss
                accuracy_floor = BOSS_ACCURACY_FLOOR if is_boss else 0.0
                dodge_chance = min(base_dodge, 1.0 - accuracy_floor)
                
                if random.random() < dodge_chance:
                    attack_msg = "'s attack!"
                    print(f"{colorize('✨', Colors.BRIGHT_CYAN)} {colorize('You dodged', Colors.BRIGHT_GREEN)} {colorize(enemy.name, Colors.BRIGHT_RED)} {colorize(attack_msg, Colors.WHITE)}")
                else:
                    damage_taken = player.take_damage(enemy_damage)
                    print(f"{colorize('💥', Colors.BRIGHT_RED)} {colorize(enemy.name, Colors.BRIGHT_RED)} {colorize('attacks you for', Colors.WHITE)} {colorize(str(damage_taken), Colors.BRIGHT_RED + Colors.BOLD)} {colorize('damage!', Colors.WHITE)}")
                
                if not player.is_alive():
                    # Handle death with enhanced death screen and respawn
                    from ..game.death import handle_combat_death
                    return handle_combat_death(player, enemy.name)
        else:
            print(f"\n{colorize('❌ Invalid choice!', Colors.BRIGHT_RED)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
            clear_screen()
            print(colorize("=" * 60, Colors.CYAN))
            print(colorize("⚔️  BATTLE CONTINUES! ⚔️", Colors.BRIGHT_RED + Colors.BOLD))
            print(colorize("=" * 60, Colors.CYAN))
            continue
        
        input(f"\n{colorize('Press Enter to continue...', Colors.BRIGHT_CYAN)}")
        clear_screen()
        print(colorize("=" * 60, Colors.BRIGHT_RED))
        print(colorize("⚔️  BATTLE CONTINUES! ⚔️", Colors.BRIGHT_RED + Colors.BOLD))
        print(colorize("=" * 60, Colors.BRIGHT_RED))
    
    return player.is_alive()

