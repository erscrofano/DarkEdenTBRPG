"""Combat simulator for testing drop rates and balancing"""
import time
import random
import threading
from collections import defaultdict
from ..ui import Colors, colorize, clear_screen
from ..combat.enemies import BASE_ENEMIES
from ..combat.system import scale_enemy, NIGHT_MONSTER_HP_BUFF, NIGHT_MONSTER_ATTACK_BUFF, NIGHT_DROP_RATE_BUFF
from ..items import DROP_ITEMS


def combat_simulator(player):
    """Combat simulator for testing loot drops and balance"""
    
    # Choose simulation mode
    clear_screen()
    print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
    print(colorize("⚔️  COMBAT SIMULATOR  ⚔️", Colors.BRIGHT_MAGENTA + Colors.BOLD))
    print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
    print(f"\n{colorize('Choose simulation mode:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
    print(f"\n  {colorize('1.', Colors.WHITE)} Zone Simulation (all enemies from location)")
    print(f"  {colorize('2.', Colors.WHITE)} Specific Enemy (test one enemy type)")
    print(f"  {colorize('3.', Colors.WHITE)} Boss Only (test boss drops)")
    print(f"  {colorize('4.', Colors.WHITE)} All Enemies (every enemy in game)")
    print(f"  {colorize('0.', Colors.WHITE)} Cancel")
    print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
    
    mode_choice = input(f"\n{colorize('Choice:', Colors.BRIGHT_CYAN)} ").strip()
    
    if mode_choice == '0':
        return
    
    # Get enemy pool based on mode
    enemy_pool = []
    sim_name = ""
    
    if mode_choice == '1':
        # Zone simulation
        clear_screen()
        print(colorize("=" * 60, Colors.BRIGHT_CYAN))
        print(colorize("🗺️  SELECT ZONE  🗺️", Colors.BRIGHT_CYAN + Colors.BOLD))
        print(colorize("=" * 60, Colors.BRIGHT_CYAN))
        print(f"\n{colorize('Available Zones:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
        
        zones = {
            '1': ('Underground Waterways', 4, 1.0, [1]),
            '2': ('Eslania Dungeon B1', 4, 0.9, [1]),
            '3': ('Eslania Dungeon B2', 7, 1.0, [1, 2]),
            '4': ('Eslania Dungeon B3', 10, 1.1, [2]),
            '5': ('Asylion Dungeon B1', 25, 1.5, [2, 3]),
            '6': ('Asylion Dungeon B2', 35, 1.8, [3]),
            '7': ('Asylion Dungeon B3', 50, 2.2, [3, 4]),
            '8': ('Limbo Dungeon', 3, 0.8, [1]),
            '9': ('Lost Taiyan', 15, 1.3, [2, 3]),
            '10': ('Rhaom Dungeon', 10, 1.1, [2])
        }
        
        for key, (name, level, mult, tiers) in zones.items():
            print(f"  {colorize(key + '.', Colors.WHITE)} {name} {colorize(f'(Lv {level}, x{mult})', Colors.GRAY)}")
        
        print(f"  {colorize('0.', Colors.WHITE)} Cancel")
        print(colorize("=" * 60, Colors.BRIGHT_CYAN))
        
        zone_choice = input(f"\n{colorize('Choice:', Colors.BRIGHT_CYAN)} ").strip()
        
        if zone_choice == '0' or zone_choice not in zones:
            return
        
        sim_name, sim_level, sim_mult, tiers = zones[zone_choice]
        enemy_pool = [e for e in BASE_ENEMIES if e['tier'] in tiers]
        
    elif mode_choice == '2':
        # Specific enemy
        clear_screen()
        print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
        print(colorize("👹  SELECT ENEMY  👹", Colors.BRIGHT_YELLOW + Colors.BOLD))
        print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
        print(f"\n{colorize('Available Enemies:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
        
        for i, enemy in enumerate(BASE_ENEMIES, 1):
            tier_color = Colors.GRAY if enemy['tier'] == 1 else Colors.BRIGHT_GREEN if enemy['tier'] == 2 else Colors.BRIGHT_YELLOW
            tier_text = f"(Tier {enemy['tier']})"
            print(f"  {colorize(str(i) + '.', Colors.WHITE)} {colorize(enemy['name'], tier_color)} {colorize(tier_text, Colors.GRAY)}")
        
        print(f"  {colorize('0.', Colors.WHITE)} Cancel")
        print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
        
        enemy_choice = input(f"\n{colorize('Choice:', Colors.BRIGHT_CYAN)} ").strip()
        
        try:
            enemy_idx = int(enemy_choice) - 1
            if 0 <= enemy_idx < len(BASE_ENEMIES):
                enemy_pool = [BASE_ENEMIES[enemy_idx]]
                sim_name = enemy_pool[0]['name']
                sim_level = player.level
                sim_mult = 1.0
            else:
                return
        except ValueError:
            return
            
    elif mode_choice == '3':
        # Boss only
        enemy_pool = [e for e in BASE_ENEMIES if e.get('is_boss', False)]
        sim_name = "All Bosses"
        sim_level = player.level
        sim_mult = 1.0
        
    elif mode_choice == '4':
        # All enemies
        enemy_pool = BASE_ENEMIES
        sim_name = "All Enemies"
        sim_level = player.level
        sim_mult = 1.0
    else:
        return
    
    if not enemy_pool:
        print(f"\n{colorize('❌ No enemies found!', Colors.BRIGHT_RED)}")
        input("\nPress Enter to continue...")
        return
    
    # Ask about night mode
    night_mode = False
    night_choice = input(f"\n{colorize('Simulate with night buffs? (y/n):', Colors.BRIGHT_MAGENTA)} ").strip().lower()
    if night_choice == 'y':
        night_mode = True
    
    # Run simulation
    _run_simulation(player, enemy_pool, sim_name, sim_level if mode_choice == '1' else player.level, 
                     sim_mult if mode_choice == '1' else 1.0, night_mode)


def _run_simulation(player, enemy_pool, sim_name, sim_level, location_mult, night_mode):
    """Run the actual simulation loop"""
    
    # Simulation state
    sim_active = True
    kills = 0
    start_time = time.time()
    
    # Loot tracking
    loot_counter = defaultdict(int)
    total_gold = 0
    total_exp = 0
    
    # Per-enemy tracking
    enemy_kill_counts = defaultdict(int)
    
    def simulation_loop():
        """Main simulation loop"""
        nonlocal kills, total_gold, total_exp, loot_counter, enemy_kill_counts
        
        last_update = time.time()
        kills_this_second = 0
        
        while sim_active:
            current_time = time.time()
            
            # Kill 5 enemies per second
            if current_time - last_update >= 0.2:  # 0.2s = 5 kills/sec
                # Pick random enemy from pool
                enemy_template = random.choice(enemy_pool)
                
                # Scale enemy
                # For night mode, we need to create a fake player object with world_anchor_timestamp
                if night_mode:
                    scaled_enemy = scale_enemy(enemy_template, sim_level, location_mult, player)
                else:
                    scaled_enemy = scale_enemy(enemy_template, sim_level, location_mult, None)
                
                # Track kill
                kills += 1
                kills_this_second += 1
                enemy_kill_counts[enemy_template['name']] += 1
                
                # Award gold and XP
                total_gold += scaled_enemy['gold']
                total_exp += scaled_enemy['exp']
                
                # Roll for drops
                if scaled_enemy['drops']:
                    drop_multiplier = NIGHT_DROP_RATE_BUFF if night_mode else 1.0
                    
                    for drop in scaled_enemy['drops']:
                        adjusted_chance = min(1.0, drop['chance'] * drop_multiplier)
                        
                        if random.random() < adjusted_chance:
                            item_id = drop['item']
                            if item_id in DROP_ITEMS:
                                loot_counter[DROP_ITEMS[item_id]['name']] += 1
                
                last_update = current_time
                kills_this_second = kills_this_second % 5
    
    def input_handler():
        """Wait for Enter to stop"""
        nonlocal sim_active
        input()
        sim_active = False
    
    def display_loop():
        """Update display every second"""
        while sim_active:
            elapsed = time.time() - start_time
            rate = kills / elapsed if elapsed > 0 else 0
            
            clear_screen()
            print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
            print(colorize("⚔️  COMBAT SIMULATOR - RUNNING  ⚔️", Colors.BRIGHT_MAGENTA + Colors.BOLD))
            print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
            
            print(f"\n{colorize('SIMULATION:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
            print(f"  {colorize('Zone:', Colors.WHITE)} {colorize(sim_name, Colors.BRIGHT_CYAN)}")
            if night_mode:
                print(f"  {colorize('Mode:', Colors.WHITE)} {colorize('🌙 NIGHT (+30% HP/ATK, +50% Drops)', Colors.BRIGHT_MAGENTA)}")
            print(f"  {colorize('Duration:', Colors.WHITE)} {colorize(f'{elapsed:.1f}s', Colors.BRIGHT_YELLOW)}")
            print(f"  {colorize('Kills:', Colors.WHITE)} {colorize(str(kills), Colors.BRIGHT_GREEN)} {colorize(f'({rate:.1f}/sec)', Colors.GRAY)}")
            
            # Show top 10 loot items
            if loot_counter:
                print(f"\n{colorize('LOOT TRACKER (Top 10):', Colors.BRIGHT_WHITE + Colors.BOLD)}")
                sorted_loot = sorted(loot_counter.items(), key=lambda x: x[1], reverse=True)[:10]
                for item_name, count in sorted_loot:
                    print(f"  {colorize('•', Colors.BRIGHT_CYAN)} {colorize(item_name, Colors.BRIGHT_CYAN)}: {colorize(f'{count}x', Colors.BRIGHT_YELLOW)}")
            
            # Show totals
            print(f"\n{colorize('TOTALS:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
            print(f"  {colorize('Gold:', Colors.YELLOW)} {colorize(f'{total_gold:,}g', Colors.BRIGHT_YELLOW)} {colorize(f'(Avg: {total_gold/kills if kills > 0 else 0:.1f}g/kill)', Colors.GRAY)}")
            print(f"  {colorize('XP:', Colors.CYAN)} {colorize(f'{total_exp:,}', Colors.BRIGHT_CYAN)} {colorize(f'(Avg: {total_exp/kills if kills > 0 else 0:.1f}/kill)', Colors.GRAY)}")
            
            print(colorize("\n" + "=" * 60, Colors.BRIGHT_MAGENTA))
            print(colorize("Press Enter to stop simulation...", Colors.BRIGHT_YELLOW))
            
            time.sleep(1.0)
    
    # Start threads
    input_thread = threading.Thread(target=input_handler, daemon=True)
    display_thread = threading.Thread(target=display_loop, daemon=True)
    
    input_thread.start()
    display_thread.start()
    
    # Run simulation
    simulation_loop()
    
    # Wait for display thread to finish
    time.sleep(0.5)
    
    # Show final summary
    elapsed = time.time() - start_time
    rate = kills / elapsed if elapsed > 0 else 0
    
    clear_screen()
    print(colorize("=" * 60, Colors.BRIGHT_GREEN))
    print(colorize("✅  SIMULATION COMPLETE  ✅", Colors.BRIGHT_GREEN + Colors.BOLD))
    print(colorize("=" * 60, Colors.BRIGHT_GREEN))
    
    print(f"\n{colorize('SIMULATION DETAILS:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
    print(f"  {colorize('Zone:', Colors.WHITE)} {colorize(sim_name, Colors.BRIGHT_CYAN)}")
    if night_mode:
        print(f"  {colorize('Mode:', Colors.WHITE)} {colorize('🌙 Night Mode', Colors.BRIGHT_MAGENTA)}")
    print(f"  {colorize('Duration:', Colors.WHITE)} {colorize(f'{elapsed:.1f} seconds', Colors.BRIGHT_YELLOW)}")
    print(f"  {colorize('Total Kills:', Colors.WHITE)} {colorize(str(kills), Colors.BRIGHT_GREEN)}")
    print(f"  {colorize('Kill Rate:', Colors.WHITE)} {colorize(f'{rate:.2f}/sec', Colors.BRIGHT_YELLOW)}")
    
    # Enemy breakdown
    if enemy_kill_counts:
        print(f"\n{colorize('ENEMY BREAKDOWN:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
        for enemy_name, count in sorted(enemy_kill_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / kills * 100) if kills > 0 else 0
            print(f"  {colorize(enemy_name, Colors.BRIGHT_RED)}: {colorize(str(count), Colors.BRIGHT_YELLOW)} {colorize(f'({percentage:.1f}%)', Colors.GRAY)}")
    
    # Loot breakdown with drop rates
    if loot_counter:
        print(f"\n{colorize('LOOT OBTAINED:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
        sorted_loot = sorted(loot_counter.items(), key=lambda x: x[1], reverse=True)
        
        for item_name, count in sorted_loot:
            drop_rate = (count / kills * 100) if kills > 0 else 0
            print(f"  {colorize('•', Colors.BRIGHT_CYAN)} {colorize(item_name, Colors.BRIGHT_CYAN)}: " + 
                  f"{colorize(f'{count}x', Colors.BRIGHT_YELLOW)} " +
                  f"{colorize(f'({drop_rate:.1f}% drop rate)', Colors.GRAY)}")
        
        print(f"\n  {colorize('Total Unique Items:', Colors.WHITE)} {colorize(str(len(loot_counter)), Colors.BRIGHT_CYAN)}")
        print(f"  {colorize('Total Item Drops:', Colors.WHITE)} {colorize(str(sum(loot_counter.values())), Colors.BRIGHT_YELLOW)}")
    else:
        print(f"\n{colorize('LOOT OBTAINED:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
        print(f"  {colorize('No drops received', Colors.GRAY)}")
    
    # Resource summary
    print(f"\n{colorize('RESOURCES:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
    print(f"  {colorize('Total Gold:', Colors.YELLOW)} {colorize(f'{total_gold:,}g', Colors.BRIGHT_YELLOW)}")
    print(f"  {colorize('Avg Gold/Kill:', Colors.YELLOW)} {colorize(f'{total_gold/kills if kills > 0 else 0:.1f}g', Colors.BRIGHT_YELLOW)}")
    print(f"  {colorize('Total XP:', Colors.CYAN)} {colorize(f'{total_exp:,}', Colors.BRIGHT_CYAN)}")
    print(f"  {colorize('Avg XP/Kill:', Colors.CYAN)} {colorize(f'{total_exp/kills if kills > 0 else 0:.1f}', Colors.BRIGHT_CYAN)}")
    
    # Efficiency stats
    if kills > 0:
        gold_per_second = total_gold / elapsed if elapsed > 0 else 0
        xp_per_second = total_exp / elapsed if elapsed > 0 else 0
        print(f"\n{colorize('EFFICIENCY:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
        print(f"  {colorize('Gold/Second:', Colors.YELLOW)} {colorize(f'{gold_per_second:.1f}g/s', Colors.BRIGHT_YELLOW)}")
        print(f"  {colorize('XP/Second:', Colors.CYAN)} {colorize(f'{xp_per_second:.1f}/s', Colors.BRIGHT_CYAN)}")
        print(f"  {colorize('Gold/Hour:', Colors.YELLOW)} {colorize(f'{gold_per_second * 3600:,.0f}g/hr', Colors.BRIGHT_YELLOW)}")
        print(f"  {colorize('XP/Hour:', Colors.CYAN)} {colorize(f'{xp_per_second * 3600:,.0f}/hr', Colors.BRIGHT_CYAN)}")
    
    print(colorize("\n" + "=" * 60, Colors.BRIGHT_GREEN))
    input(f"\n{colorize('Press Enter to return to dev menu...', Colors.WHITE)}")

