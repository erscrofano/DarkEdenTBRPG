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
    DEATH_GOLD_LOSS, DEATH_ITEM_PROTECTION,
    GUARANTEED_FLEE_GOLD_COST,
    KILL_STREAK_NOTIFICATION_INTERVAL,
    NOTIFICATION_DURATION_NORMAL, NOTIFICATION_DURATION_LONG,
    ENEMY_SCALE_BASE, ENEMY_SCALE_MULTIPLIER, ENEMY_SCALE_DECAY
)
from ..ui import Colors, colorize, clear_screen, show_notification, health_bar
from ..items import DROP_ITEMS, add_item_to_inventory, remove_item_from_inventory, get_item_quantity, format_item_name, get_item_rarity, ITEM_RARITY
from ..achievements.system import check_achievements, log_rare_drop
from ..game.stats import allocate_stats


def scale_enemy(enemy_template, player_level, location_multiplier=1.0):
    """Scale enemy stats based on player level and location (eased growth curve)"""
    # Smooth difficulty curve: use asymptotic scaling instead of linear
    # Formula: scaler = ENEMY_SCALE_BASE + (1 - (ENEMY_SCALE_DECAY ** level_diff)) * ENEMY_SCALE_MULTIPLIER
    # This provides strong early scaling that tapers off for smoother progression
    level_diff = max(0, player_level - enemy_template['tier'])
    
    # Asymptotic scaler that caps growth smoothly
    base_scaler = ENEMY_SCALE_BASE + (1 - (ENEMY_SCALE_DECAY ** level_diff)) * ENEMY_SCALE_MULTIPLIER
    scale_factor = base_scaler * location_multiplier
    
    # Apply scaling
    hp = int(enemy_template['base_hp'] * scale_factor)
    attack = int(enemy_template['base_attack'] * scale_factor)
    defense = int(enemy_template['base_defense'] * scale_factor)
    exp = int(enemy_template['base_exp'] * scale_factor)
    gold = int(enemy_template['base_gold'] * scale_factor)
    
    return {
        'name': enemy_template['name'],
        'hp': hp,
        'attack': attack,
        'defense': defense,
        'exp': exp,
        'gold': gold,
        'drops': enemy_template['drops'],
        'tier': enemy_template.get('tier', 1),  # Track tier for boss detection
        'is_boss': enemy_template.get('is_boss', False)  # Mark bosses/elites
    }


def combat(player, enemy):
    # Reset guaranteed flee flag at combat start
    player._guaranteed_flee_used = False
    
    clear_screen()
    print(colorize("=" * 60, Colors.BRIGHT_RED))
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
                    for drop in enemy.drops:
                        if random.random() < drop['chance']:
                            drop_item = DROP_ITEMS[drop['item']].copy()
                            add_item_to_inventory(player.inventory, drop_item)
                            drops_received.append(drop_item)
                            
                            # Check for rare/legendary drop achievements
                            drop_value = drop_item.get('sell_value', 0)
                            check_achievements(player, 'rare_drop', drop_value)
                            
                            # Check for talisman achievements
                            if drop_item.get('type') == 'talisman':
                                check_achievements(player, 'talisman_found')
                                if drop_item.get('name') == 'Talisman of the Hacker':
                                    check_achievements(player, 'talisman_hacker')
                                # Check talisman count achievements
                                check_achievements(player, 'talisman_count')
                            
                            # Log rare drops (Epic ≥75, Legendary ≥200)
                            if drop_value >= 75:
                                log_rare_drop(player, drop_item, drop_value)
                    
                    if drops_received:
                        print(f"\n{colorize('📦', Colors.BRIGHT_CYAN)} {colorize('LOOT OBTAINED:', Colors.BRIGHT_CYAN + Colors.BOLD)}")
                        print("-" * 60)
                        for drop_item in drops_received:
                            formatted_name = format_item_name(drop_item)
                            print(f"  {colorize('•', Colors.BRIGHT_CYAN)} {formatted_name}")
                        
                            # Special notification for rare drops
                        for drop_item in drops_received:
                            rarity = get_item_rarity(drop_item)
                            if rarity in ['epic', 'legendary']:
                                rarity_name = ITEM_RARITY[rarity]['name']
                                show_notification(f"{rarity_name} drop: {drop_item['name']}!", ITEM_RARITY[rarity]['color'], NOTIFICATION_DURATION_LONG)
                
                # Update kill tracking (Kal Online inspired)
                player.kill_streak += 1
                player.total_kills += 1
                
                # Kill streak notifications
                if player.kill_streak % KILL_STREAK_NOTIFICATION_INTERVAL == 0 and player.kill_streak > 0:
                    show_notification(f"Kill Streak: {player.kill_streak}!", Colors.BRIGHT_RED, NOTIFICATION_DURATION_NORMAL)
                
                # Check achievements
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
                # Death mechanics (OSRS/Kal Online inspired - keep some items)
                print(f"\n{colorize('💀 You have been defeated!', Colors.BRIGHT_RED + Colors.BOLD)}")
                
                # Reset kill streak on death (Kal Online style)
                lost_streak = player.kill_streak
                player.kill_streak = 0
                
                if lost_streak > 0:
                    print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(f'Kill streak lost: {lost_streak}', Colors.YELLOW)}")
                
                # Keep 3 most valuable items on death (OSRS-style protection)
                # Calculate total item value considering quantities
                item_values = []
                for item in player.inventory:
                    qty = get_item_quantity(item)
                    total_value = item.get('sell_value', 0) * qty
                    item_values.append((item, total_value, qty))
                
                if len(item_values) > DEATH_ITEM_PROTECTION:
                    # Sort by total value
                    item_values.sort(key=lambda x: x[1], reverse=True)
                    kept_items = item_values[:DEATH_ITEM_PROTECTION]
                    lost_items = item_values[DEATH_ITEM_PROTECTION:]
                    
                    # Remove lost items
                    total_lost = 0
                    for lost_item, value, qty in lost_items:
                        remove_item_from_inventory(player.inventory, lost_item, qty)
                        total_lost += qty
                    
                    if total_lost > 0:
                        print(f"\n{colorize('💔', Colors.YELLOW)} {colorize(f'You lost {total_lost} items on death!', Colors.WHITE)}")
                        print(f"{colorize('🛡️', Colors.BRIGHT_GREEN)} {colorize(f'Kept your {DEATH_ITEM_PROTECTION} most valuable items.', Colors.BRIGHT_GREEN)}")
                
                # Lose 10% of gold on death (Kal Online style)
                gold_lost = int(player.gold * DEATH_GOLD_LOSS)
                player.gold -= gold_lost
                if gold_lost > 0:
                    print(f"{colorize('💰', Colors.YELLOW)} {colorize(f'Lost {gold_lost} gold on death.', Colors.WHITE)}")
                
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                return False
        
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
            
            # Use the potion(s)
            total_heal = healing_item['heal'] * use_qty
            remove_item_from_inventory(player.inventory, healing_item, use_qty)
            player.heal(total_heal)
            
            if use_qty > 1:
                print(f"\n{colorize('🧪', Colors.BRIGHT_GREEN)} {colorize(f'You used {use_qty}x', Colors.WHITE)} {colorize(healing_item['name'], Colors.BRIGHT_CYAN)} {colorize('and healed', Colors.WHITE)} {colorize(str(total_heal), Colors.BRIGHT_GREEN + Colors.BOLD)} {colorize('HP!', Colors.WHITE)}")
            else:
                print(f"\n{colorize('🧪', Colors.BRIGHT_GREEN)} {colorize('You used', Colors.WHITE)} {colorize(healing_item['name'], Colors.BRIGHT_CYAN)} {colorize('and healed', Colors.WHITE)} {colorize(str(total_heal), Colors.BRIGHT_GREEN + Colors.BOLD)} {colorize('HP!', Colors.WHITE)}")
            
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
                # Death mechanics (OSRS/Kal Online inspired - keep some items)
                print(f"\n{colorize('💀 You have been defeated!', Colors.BRIGHT_RED + Colors.BOLD)}")
                
                # Reset kill streak on death (Kal Online style)
                lost_streak = player.kill_streak
                player.kill_streak = 0
                
                if lost_streak > 0:
                    print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(f'Kill streak lost: {lost_streak}', Colors.YELLOW)}")
                
                # Keep 3 most valuable items on death (OSRS-style protection)
                # Calculate total item value considering quantities
                item_values = []
                for item in player.inventory:
                    qty = get_item_quantity(item)
                    total_value = item.get('sell_value', 0) * qty
                    item_values.append((item, total_value, qty))
                
                if len(item_values) > DEATH_ITEM_PROTECTION:
                    # Sort by total value
                    item_values.sort(key=lambda x: x[1], reverse=True)
                    kept_items = item_values[:DEATH_ITEM_PROTECTION]
                    lost_items = item_values[DEATH_ITEM_PROTECTION:]
                    
                    # Remove lost items
                    total_lost = 0
                    for lost_item, value, qty in lost_items:
                        remove_item_from_inventory(player.inventory, lost_item, qty)
                        total_lost += qty
                    
                    if total_lost > 0:
                        print(f"\n{colorize('💔', Colors.YELLOW)} {colorize(f'You lost {total_lost} items on death!', Colors.WHITE)}")
                        print(f"{colorize('🛡️', Colors.BRIGHT_GREEN)} {colorize(f'Kept your {DEATH_ITEM_PROTECTION} most valuable items.', Colors.BRIGHT_GREEN)}")
                
                # Lose 10% of gold on death (Kal Online style)
                gold_lost = int(player.gold * DEATH_GOLD_LOSS)
                player.gold -= gold_lost
                if gold_lost > 0:
                    print(f"{colorize('💰', Colors.YELLOW)} {colorize(f'Lost {gold_lost} gold on death.', Colors.WHITE)}")
                
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                return False
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
                    print(f"\n{colorize('💀 You have been defeated!', Colors.BRIGHT_RED + Colors.BOLD)}")
                    input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                    return False
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

