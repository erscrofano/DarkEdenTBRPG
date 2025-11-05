"""Mining skill system"""
import random
import time
import threading
from ..config import DEV_FLAGS
from ..ui import Colors, colorize, clear_screen, show_notification, skill_xp_bar
from ..items.inventory import add_item_to_inventory
from ..items.rarity import format_item_name
from ..models.location import LOCATIONS
from ..achievements.system import check_achievements
from .core import add_skill_xp


# Mining system - Ore types with rarity (sell_value determines rarity)
MINING_ORES = {
    'copper': {'name': 'Copper Ore', 'type': 'material', 'sell_value': 100, 'description': 'A common copper ore', 'mine_chance': 0.35, 'key': 'copper'},  # Most common
    'tin': {'name': 'Tin Ore', 'type': 'material', 'sell_value': 100, 'description': 'A common tin ore', 'mine_chance': 0.28, 'key': 'tin'},
    'clay': {'name': 'Clay', 'type': 'material', 'sell_value': 250, 'description': 'Soft clay for crafting', 'mine_chance': 0.25, 'key': 'clay'},
    'iron': {'name': 'Iron Ore', 'type': 'material', 'sell_value': 750, 'description': 'A medium-quality iron ore', 'mine_chance': 0.20, 'key': 'iron'},
    'silver': {'name': 'Silver Ore', 'type': 'material', 'sell_value': 2500, 'description': 'A valuable silver ore', 'mine_chance': 0.10, 'key': 'silver'},
    'gold': {'name': 'Gold Ore', 'type': 'material', 'sell_value': 5000, 'description': 'A rare gold ore', 'mine_chance': 0.05, 'key': 'gold'},
    'sapphire': {'name': 'Sapphire', 'type': 'material', 'sell_value': 2500, 'description': 'A beautiful blue gemstone', 'mine_chance': 0.012, 'key': 'sapphire'},
    'ruby': {'name': 'Ruby', 'type': 'material', 'sell_value': 5000, 'description': 'A brilliant red gemstone', 'mine_chance': 0.008, 'key': 'ruby'},
    'emerald': {'name': 'Emerald', 'type': 'material', 'sell_value': 10000, 'description': 'A stunning green gemstone', 'mine_chance': 0.005, 'key': 'emerald'},
    'diamond': {'name': 'Diamond', 'type': 'material', 'sell_value': 20000, 'description': 'The most precious gemstone - extremely rare!', 'mine_chance': 0.002, 'key': 'diamond'},
    'dragonstone': {'name': 'Dragonstone', 'type': 'material', 'sell_value': 40000, 'description': 'An ancient crimson gem said to contain dragon essence', 'mine_chance': 0.001, 'key': 'dragonstone'},
    'onyx': {'name': 'Onyx', 'type': 'material', 'sell_value': 80000, 'description': 'A pitch-black gemstone of legendary rarity', 'mine_chance': 0.0005, 'key': 'onyx'},  # Most rare
}

# Mining level requirements
MINING_LEVEL_REQUIREMENTS = {
    'copper': 1,
    'tin': 1,
    'clay': 5,
    'iron': 10,
    'silver': 20,
    'gold': 30,
    # Gems can be mined at any level but rarity scales with level
    'sapphire': 1,
    'ruby': 1,
    'emerald': 1,
    'diamond': 1,
    'dragonstone': 1,
    'onyx': 1
}

# Mining XP awards
MINING_XP_AWARDS = {
    'copper': 10,
    'tin': 12,
    'clay': 15,
    'iron': 25,
    'silver': 40,
    'gold': 60,
    # Gems give bonus XP based on rarity
    'sapphire': 100,
    'ruby': 150,
    'emerald': 200,
    'diamond': 300,
    'dragonstone': 400,
    'onyx': 500  # Highest gem
}


def get_mining_catch(player, eligible_ores):
    """Calculate which ore to mine based on level-weighted distribution"""
    if not eligible_ores:
        return None, None
    
    # Separate gems from regular ores
    gems = ['sapphire', 'ruby', 'emerald', 'diamond', 'dragonstone', 'onyx']
    low_tier_ores = ['copper', 'tin']  # Low tier ores that should remain common
    
    from ..constants import MINING_LEVEL_BOOST_MULTIPLIER, MINING_LEVEL_BOOST_MAX
    # Calculate level boost for higher tier ores (up to 25% absolute)
    level_boost = min(MINING_LEVEL_BOOST_MAX, player.mining_level * MINING_LEVEL_BOOST_MULTIPLIER)
    
    # Build weights with level scaling
    weights = {}
    
    for ore_key, ore_data in eligible_ores:
        base_chance = ore_data['mine_chance']
        required_level = MINING_LEVEL_REQUIREMENTS.get(ore_key, 1)
        
        # Special handling for gems - rarity scales with mining level
        if ore_key in gems:
            # Base chance is very low, but scales with level
            # At level 1: base chance, at level 99: base chance * 3.0
            level_multiplier = 1.0 + (player.mining_level / 50.0)  # Up to ~3x at level 99
            weight = base_chance * level_multiplier
        elif ore_key not in low_tier_ores:
            # Regular higher tier ores get level boost
            rarity_weight = required_level / 30.0  # Gold is highest at 30
            weight = base_chance + (level_boost * rarity_weight)
        else:
            # Keep low tier at base chance
            weight = base_chance
        
        weights[ore_key] = weight
    
    # Ensure low tier ores combined are at least 50% of total (slightly lower than fishing)
    low_tier_total = sum(weights.get(k, 0) for k in low_tier_ores if k in weights)
    total_weight = sum(weights.values())
    
    if total_weight > 0 and low_tier_total / total_weight < 0.50:
        # Boost low tier to maintain 50% minimum
        scale_factor = (0.50 * total_weight) / low_tier_total
        for ore_key in low_tier_ores:
            if ore_key in weights:
                weights[ore_key] *= scale_factor
        
        # Re-normalize
        total_weight = sum(weights.values())
    
    # Normalize to probabilities
    if total_weight > 0:
        probabilities = {k: v / total_weight for k, v in weights.items()}
    else:
        # Fallback if no weights
        probabilities = {ore_key: 1.0 / len(eligible_ores) for ore_key, _ in eligible_ores}
    
    # Roll for catch
    roll = random.random()
    cumulative = 0
    
    for ore_key, ore_data in eligible_ores:
        if ore_key in probabilities:
            cumulative += probabilities[ore_key]
            if roll <= cumulative:
                return ore_key, ore_data
    
    # Fallback to first eligible
    return eligible_ores[0][0], eligible_ores[0][1]


def go_mining(player):
    """Mining mini-game - mine ores automatically until player stops"""
    # Get eligible ores based on mining level
    eligible_ores = []
    locked_ores = []
    
    for ore_key, ore_data in MINING_ORES.items():
        # Use the 'key' field from ore_data if available, otherwise use ore_key
        lookup_key = ore_data.get('key', ore_key)
        required_level = MINING_LEVEL_REQUIREMENTS.get(lookup_key, 1)
        if player.mining_level >= required_level:
            eligible_ores.append((lookup_key, ore_data))
        else:
            locked_ores.append((lookup_key, ore_data, required_level))
    
    if not eligible_ores:
        clear_screen()
        print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
        print(colorize("⛏️  MINING  ⛏️", Colors.BRIGHT_MAGENTA + Colors.BOLD))
        print(colorize("=" * 60, Colors.MAGENTA))
        print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('You need Mining level 1 to mine ores!', Colors.WHITE)}")
        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
        return
    
    clear_screen()
    location = LOCATIONS['mining']
    print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
    print(colorize("⛏️  MINING SITE  ⛏️", Colors.BRIGHT_MAGENTA + Colors.BOLD))
    print(colorize("=" * 60, Colors.MAGENTA))
    print(f"\n{colorize(location.description, Colors.WHITE)}")
    print(f"\n{colorize('Mining will automatically continue. Press Enter to stop.', Colors.YELLOW)}")
    print(f"{colorize('Mining Level:', Colors.BRIGHT_MAGENTA)} {colorize(str(player.mining_level), Colors.BRIGHT_GREEN)}")
    if player.tool and player.tool.get('type') == 'tool' and 'mining_speed_boost' in player.tool:
        boost = abs(player.tool['mining_speed_boost'])
        print(f"{colorize('Equipped Tool:', Colors.BRIGHT_MAGENTA)} {colorize(player.tool['name'], Colors.BRIGHT_GREEN)} {colorize(f'(-{boost}s)', Colors.WHITE)}")
    else:
        print(f"{colorize('Equipped Tool:', Colors.BRIGHT_MAGENTA)} {colorize('None', Colors.YELLOW)} {colorize('(No speed bonus)', Colors.GRAY)}")
    print(colorize("=" * 60, Colors.MAGENTA))
    input(f"\n{colorize('Press Enter to start mining...', Colors.BRIGHT_CYAN)}")
    
    mining_active = True
    ores_mined = []
    total_value = 0
    mine_count = 0
    total_xp = 0
    
    # Check equipped tool for pickaxe bonus
    mining_speed_boost = 0
    if player.tool and player.tool.get('type') == 'tool' and 'mining_speed_boost' in player.tool:
        mining_speed_boost = player.tool['mining_speed_boost']
    
    base_mining_duration = 8  # Base mining time in seconds
    mining_duration = max(1.0, base_mining_duration + mining_speed_boost)  # Minimum 1 second
    
    def mining_loop():
        nonlocal mining_active, ores_mined, total_value, mine_count, total_xp
        
        while mining_active:
            # Track start time to ensure accurate total duration
            start_time = time.time()
            progress_steps = 20
            
            for i in range(progress_steps):
                if not mining_active:
                    return
                
                # Calculate progress
                progress = (i + 1) / progress_steps
                filled = int(20 * progress)
                bar = colorize("█" * filled, Colors.BRIGHT_YELLOW) + "░" * (20 - filled)
                percentage = int(progress * 100)
                
                # Update display
                clear_screen()
                print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
                print(colorize("⛏️  MINING  ⛏️", Colors.BRIGHT_MAGENTA + Colors.BOLD))
                print(colorize("=" * 60, Colors.MAGENTA))
                print(f"\n{colorize('Mining ore...', Colors.WHITE)}")
                print(f"\n{colorize('Progress:', Colors.BRIGHT_WHITE)} [{bar}] {colorize(f'{percentage}%', Colors.BRIGHT_YELLOW)}")
                print(f"\n{colorize('Total Mined:', Colors.WHITE)} {colorize(str(mine_count), Colors.BRIGHT_YELLOW)} ores")
                if total_value > 0:
                    print(f"{colorize('Total Value:', Colors.WHITE)} {colorize(str(total_value) + 'g', Colors.BRIGHT_YELLOW)}")
                if total_xp > 0:
                    print(f"{colorize('Total XP:', Colors.BRIGHT_MAGENTA)} {colorize(str(total_xp), Colors.BRIGHT_GREEN)}")
                print(f"\n{colorize('Press Enter to stop mining', Colors.YELLOW)}")
                print(colorize("=" * 60, Colors.MAGENTA))
                
                if not DEV_FLAGS['fast']:
                    # Calculate elapsed time and adjust sleep to maintain exact duration
                    elapsed_time = time.time() - start_time
                    target_time = (i + 1) * (mining_duration / progress_steps)
                    sleep_time = max(0.0, target_time - elapsed_time)
                    if sleep_time > 0:
                        time.sleep(sleep_time)
            
            if not mining_active:
                break
            
            # Determine catch using level-based weighting
            mined_ore_key, mined_ore_data = get_mining_catch(player, eligible_ores)
            
            if mined_ore_key:
                # Add to inventory
                add_item_to_inventory(player.inventory, mined_ore_data.copy())
                ores_mined.append(mined_ore_data['name'])
                total_value += mined_ore_data['sell_value']
                mine_count += 1
                
                # Award XP
                xp_amount = MINING_XP_AWARDS.get(mined_ore_key, 10)
                total_xp += xp_amount
                add_skill_xp(player, "mining", xp_amount)
                
                # Check achievements
                if mine_count == 1:
                    check_achievements(player, 'first_mine')
                
                if not DEV_FLAGS['quiet']:
                    formatted_name = format_item_name(mined_ore_data)
                    from ..constants import NOTIFICATION_DURATION_MEDIUM
                    show_notification(f"⛏️ Mined {formatted_name}! +{xp_amount} XP", Colors.BRIGHT_GREEN, NOTIFICATION_DURATION_MEDIUM)
    
    def input_handler():
        """Handle user input to stop mining"""
        nonlocal mining_active
        input()  # Wait for Enter key
        mining_active = False
    
    # Start input handler thread
    input_thread = threading.Thread(target=input_handler, daemon=True)
    input_thread.start()
    
    # Start mining loop in main thread
    mining_loop()
    
    # Show summary
    clear_screen()
    print(colorize("=" * 60, Colors.BRIGHT_MAGENTA))
    print(colorize("⛏️  MINING SESSION COMPLETE  ⛏️", Colors.BRIGHT_MAGENTA + Colors.BOLD))
    print(colorize("=" * 60, Colors.MAGENTA))
    
    if ores_mined:
        print(f"\n{colorize(f'Total Ores Mined: {len(ores_mined)}', Colors.BRIGHT_GREEN + Colors.BOLD)}")
        print(f"{colorize(f'Total Value: {total_value}g', Colors.BRIGHT_YELLOW + Colors.BOLD)}")
        if total_xp > 0:
            print(f"{colorize(f'Total XP Gained: {total_xp}', Colors.BRIGHT_MAGENTA + Colors.BOLD)}")
            print(f"\n{colorize('Mining Level:', Colors.BRIGHT_WHITE)} {colorize(str(player.mining_level), Colors.BRIGHT_GREEN)}")
            print(f"{colorize('XP Progress:', Colors.BRIGHT_WHITE)} {skill_xp_bar(player.mining_exp, player.mining_exp_to_next)}")
        
        # Show ore breakdown
        ore_counts = {}
        for ore_name in ores_mined:
            ore_counts[ore_name] = ore_counts.get(ore_name, 0) + 1
        
        print(f"\n{colorize('Mining Breakdown:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
        for ore_key, ore_data in MINING_ORES.items():
            if ore_data['name'] in ore_counts:
                count = ore_counts[ore_data['name']]
                formatted_name = format_item_name(ore_data)
                print(f"  {formatted_name}: {colorize(str(count), Colors.BRIGHT_YELLOW)}x")
        
        # Check for rare gem achievements
        for ore_name in ores_mined:
            for ore_key, ore_data in MINING_ORES.items():
                if ore_data['name'] == ore_name and ore_data['sell_value'] >= 75:
                    check_achievements(player, 'rare_drop', ore_data['sell_value'])
                    break
    else:
        print(f"\n{colorize('No ores mined this session.', Colors.WHITE)}")
    
    print(colorize("\n" + "=" * 60, Colors.MAGENTA))
    input(f"\n{colorize('Press Enter to continue...', Colors.BRIGHT_CYAN)}")

