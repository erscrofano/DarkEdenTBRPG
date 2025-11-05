"""Fishing skill system"""
import random
import time
import threading
from datetime import datetime
from ..config import DEV_FLAGS
from ..ui import Colors, colorize, clear_screen, show_notification
from ..items.inventory import add_item_to_inventory
from ..items.rarity import format_item_name
from ..models.location import LOCATIONS
from ..save.system import get_save_dir
from .core import add_skill_xp
from ..achievements.system import check_achievements


# Fishing system - Fish types with rarity (sell_value determines rarity)
FISH_TYPES = {
    'goby': {'name': 'Goby', 'type': 'material', 'sell_value': 50, 'description': 'A small, common fish', 'catch_chance': 0.30, 'key': 'goby'},  # Most common
    'mackerel': {'name': 'Mackerel', 'type': 'material', 'sell_value': 100, 'description': 'A common saltwater fish', 'catch_chance': 0.20, 'key': 'mackerel'},
    'salmon': {'name': 'Salmon', 'type': 'material', 'sell_value': 250, 'description': 'A popular freshwater fish', 'catch_chance': 0.15, 'key': 'salmon'},
    'eel': {'name': 'Eel', 'type': 'material', 'sell_value': 1000, 'description': 'A slimy, elusive fish', 'catch_chance': 0.12, 'key': 'eel'},
    'shad': {'name': 'Shad', 'type': 'material', 'sell_value': 2500, 'description': 'A medium-sized fish', 'catch_chance': 0.08, 'key': 'shad'},
    'carp': {'name': 'Carp', 'type': 'material', 'sell_value': 5000, 'description': 'A large bottom-feeding fish', 'catch_chance': 0.06, 'key': 'carp'},
    'sea_bream': {'name': 'Sea Bream', 'type': 'material', 'sell_value': 10000, 'description': 'A prized saltwater fish', 'catch_chance': 0.04, 'key': 'seabream'},
    'silvery_eel': {'name': 'Silvery Eel', 'type': 'material', 'sell_value': 30000, 'description': 'A rare silvery eel', 'catch_chance': 0.03, 'key': 'silvery_eel'},
    'silvery_shad': {'name': 'Silvery Shad', 'type': 'material', 'sell_value': 50000, 'description': 'An extremely rare silvery shad', 'catch_chance': 0.015, 'key': 'silvery_shad'},
    'silvery_carp': {'name': 'Silvery Carp', 'type': 'material', 'sell_value': 100000, 'description': 'The legendary silvery carp - incredibly rare!', 'catch_chance': 0.005, 'key': 'silvery_carp'},
    'giant_eel': {'name': 'Giant Eel', 'type': 'material', 'sell_value': 200000, 'description': 'A massive legendary eel of unimaginable size!', 'catch_chance': 0.001, 'key': 'giant_eel'},  # Most rare
}

# Skill tables - Fishing requirements and XP
FISH_LEVEL_REQUIREMENTS = {
    'goby': 1,
    'mackerel': 5,
    'salmon': 10,
    'eel': 20,
    'shad': 30,
    'carp': 40,
    'seabream': 50,
    'silvery_eel': 60,
    'silvery_shad': 70,
    'silvery_carp': 80,
    'giant_eel': 90
}

FISHING_XP_AWARDS = {
    'goby': 10,
    'mackerel': 15,
    'salmon': 20,
    'eel': 30,
    'shad': 40,
    'carp': 55,
    'seabream': 75,
    'silvery_eel': 110,
    'silvery_shad': 150,
    'silvery_carp': 200,
    'giant_eel': 300
}

# Cooked fish items - created when cooking succeeds
COOKED_FISH_ITEMS = {
    'goby': {'name': 'Cooked Goby', 'type': 'consumable', 'heal': 10, 'sell_value': 100},
    'mackerel': {'name': 'Cooked Mackerel', 'type': 'consumable', 'heal': 20, 'sell_value': 200},
    'salmon': {'name': 'Cooked Salmon', 'type': 'consumable', 'heal': 35, 'sell_value': 500},
    'eel': {'name': 'Cooked Eel', 'type': 'consumable', 'heal': 50, 'sell_value': 2000},
    'shad': {'name': 'Cooked Shad', 'type': 'consumable', 'heal': 70, 'sell_value': 5000},
    'carp': {'name': 'Cooked Carp', 'type': 'consumable', 'heal': 90, 'sell_value': 10000},
    'seabream': {'name': 'Cooked Seabream', 'type': 'consumable', 'heal': 120, 'sell_value': 20000},
    'silvery_eel': {'name': 'Cooked Silvery Eel', 'type': 'consumable', 'heal': 150, 'sell_value': 60000},
    'silvery_shad': {'name': 'Cooked Silvery Shad', 'type': 'consumable', 'heal': 180, 'sell_value': 100000},
    'silvery_carp': {'name': 'Cooked Silvery Carp', 'type': 'consumable', 'heal': 220, 'sell_value': 200000},
    'giant_eel': {'name': 'Cooked Giant Eel', 'type': 'consumable', 'heal': 300, 'sell_value': 400000}
}

# Gourmet fish items - 1% chance when cooking (4x heal and 4x sell value)
GOURMET_FISH_ITEMS = {
    'goby': {'name': 'Gourmet Goby', 'type': 'consumable', 'heal': 40, 'sell_value': 400},
    'mackerel': {'name': 'Gourmet Mackerel', 'type': 'consumable', 'heal': 80, 'sell_value': 800},
    'salmon': {'name': 'Gourmet Salmon', 'type': 'consumable', 'heal': 140, 'sell_value': 2000},
    'eel': {'name': 'Gourmet Eel', 'type': 'consumable', 'heal': 200, 'sell_value': 8000},
    'shad': {'name': 'Gourmet Shad', 'type': 'consumable', 'heal': 280, 'sell_value': 20000},
    'carp': {'name': 'Gourmet Carp', 'type': 'consumable', 'heal': 360, 'sell_value': 40000},
    'seabream': {'name': 'Gourmet Seabream', 'type': 'consumable', 'heal': 480, 'sell_value': 80000},
    'silvery_eel': {'name': 'Gourmet Silvery Eel', 'type': 'consumable', 'heal': 600, 'sell_value': 240000},
    'silvery_shad': {'name': 'Gourmet Silvery Shad', 'type': 'consumable', 'heal': 720, 'sell_value': 400000},
    'silvery_carp': {'name': 'Gourmet Silvery Carp', 'type': 'consumable', 'heal': 880, 'sell_value': 800000},
    'giant_eel': {'name': 'Gourmet Giant Eel', 'type': 'consumable', 'heal': 1200, 'sell_value': 1600000}
}

# Gourmet cooking chance
GOURMET_COOKING_CHANCE = 0.01  # 1% chance


def get_fishing_catch(player, eligible_fish):
    """Calculate which fish to catch based on level-weighted distribution"""
    if not eligible_fish:
        return None, None
    
    from ..constants import (
        FISHING_LEVEL_BOOST_MULTIPLIER, FISHING_LEVEL_BOOST_MAX,
        FISHING_RARITY_WEIGHT_DIVISOR, FISHING_LOW_TIER_THRESHOLD
    )
    
    # Calculate level boost (up to 25% absolute)
    level_boost = min(FISHING_LEVEL_BOOST_MAX, player.fishing_level * FISHING_LEVEL_BOOST_MULTIPLIER)
    
    # Build weights with level scaling
    weights = {}
    low_tier_fish = ['goby', 'mackerel', 'salmon']  # Low tier fish that should remain common
    
    for fish_key, fish_data in eligible_fish:
        base_chance = fish_data['catch_chance']
        required_level = FISH_LEVEL_REQUIREMENTS.get(fish_key, 1)
        
        # Rarity weight proportional to required_level / 80
        rarity_weight = required_level / FISHING_RARITY_WEIGHT_DIVISOR
        
        # Apply level boost to higher tier fish
        if fish_key not in low_tier_fish:
            weight = base_chance + (level_boost * rarity_weight)
        else:
            weight = base_chance  # Keep low tier at base
        
        weights[fish_key] = weight
    
    # Ensure low tier fish combined are at least 55% of total
    low_tier_total = sum(weights.get(k, 0) for k in low_tier_fish if k in weights)
    total_weight = sum(weights.values())
    
    if low_tier_total / total_weight < FISHING_LOW_TIER_THRESHOLD:
        # Boost low tier to maintain 55% minimum
        scale_factor = (FISHING_LOW_TIER_THRESHOLD * total_weight) / low_tier_total
        for fish_key in low_tier_fish:
            if fish_key in weights:
                weights[fish_key] *= scale_factor
        
        # Re-normalize
        total_weight = sum(weights.values())
    
    # Normalize to probabilities
    probabilities = {k: v / total_weight for k, v in weights.items()}
    
    # Roll for catch
    roll = random.random()
    cumulative = 0
    
    for fish_key, fish_data in eligible_fish:
        if fish_key in probabilities:
            cumulative += probabilities[fish_key]
            if roll <= cumulative:
                return fish_key, fish_data
    
    # Fallback to first eligible
    return eligible_fish[0][0], eligible_fish[0][1]


def log_fishing_outcome(player, fish_data, quantity, xp_gained):
    """Log fishing outcomes to file"""
    try:
        log_dir = get_save_dir() / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / 'fishing.log'
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        fish_name = fish_data['name'] if fish_data else "Various"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {player.name} (Fishing Lv.{player.fishing_level}) caught {quantity}x {fish_name} (+{xp_gained} XP)\n")
    except (OSError, PermissionError, IOError) as e:
        # Log error but don't fail fishing
        from ..utils.logging import log_warning
        log_warning(f"Failed to log fishing outcome: {e}")


def go_fishing(player):
    """Fishing mini-game - catch fish automatically until player stops"""
    # Get eligible fish based on fishing level
    eligible_fish = []
    locked_fish = []
    
    for fish_key, fish_data in FISH_TYPES.items():
        # Use the 'key' field from fish_data if available, otherwise use fish_key
        lookup_key = fish_data.get('key', fish_key)
        required_level = FISH_LEVEL_REQUIREMENTS.get(lookup_key, 1)
        if player.fishing_level >= required_level:
            eligible_fish.append((lookup_key, fish_data))
        else:
            locked_fish.append((lookup_key, fish_data, required_level))
    
    if not eligible_fish:
        clear_screen()
        print(colorize("=" * 60, Colors.BRIGHT_CYAN))
        print(colorize("🎣  FISHING  🎣", Colors.BRIGHT_CYAN + Colors.BOLD))
        print(colorize("=" * 60, Colors.CYAN))
        print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('You need Fishing level 1 to catch fish!', Colors.WHITE)}")
        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
        return
    
    clear_screen()
    location = LOCATIONS['fishing']
    print(colorize("=" * 60, Colors.BRIGHT_CYAN))
    print(colorize("🎣  FISHING SPOT  🎣", Colors.BRIGHT_CYAN + Colors.BOLD))
    print(colorize("=" * 60, Colors.CYAN))
    print(f"\n{colorize(location.description, Colors.WHITE)}")
    print(f"\n{colorize('Fishing will automatically continue. Press Enter to stop.', Colors.YELLOW)}")
    print(f"{colorize('Fishing Level:', Colors.BRIGHT_CYAN)} {colorize(str(player.fishing_level), Colors.BRIGHT_GREEN)}")
    if player.tool and player.tool.get('type') == 'tool' and 'fishing_speed_boost' in player.tool:
        boost = abs(player.tool['fishing_speed_boost'])
        print(f"{colorize('Equipped Tool:', Colors.BRIGHT_CYAN)} {colorize(player.tool['name'], Colors.BRIGHT_GREEN)} {colorize(f'(-{boost}s)', Colors.WHITE)}")
    else:
        print(f"{colorize('Equipped Tool:', Colors.BRIGHT_CYAN)} {colorize('None', Colors.YELLOW)} {colorize('(No speed bonus)', Colors.GRAY)}")
    print(colorize("=" * 60, Colors.CYAN))
    input(f"\n{colorize('Press Enter to start fishing...', Colors.BRIGHT_CYAN)}")
    
    fishing_active = True
    fish_caught = []
    total_value = 0
    catch_count = 0
    total_xp = 0
    
    # Check equipped tool for fishing rod bonus
    fishing_speed_boost = 0
    if player.tool and player.tool.get('type') == 'tool' and 'fishing_speed_boost' in player.tool:
        fishing_speed_boost = player.tool['fishing_speed_boost']
    
    base_fishing_duration = 8
    fishing_duration = max(1.0, base_fishing_duration + fishing_speed_boost)  # Minimum 1 second
    
    def fishing_loop():
        nonlocal fishing_active, fish_caught, total_value, catch_count, total_xp
        
        while fishing_active:
            # Track start time to ensure accurate total duration
            start_time = time.time()
            progress_steps = 20
            
            for i in range(progress_steps):
                if not fishing_active:
                    return
                
                # Calculate progress
                progress = (i + 1) / progress_steps
                filled = int(20 * progress)
                bar = colorize("█" * filled, Colors.BRIGHT_GREEN) + "░" * (20 - filled)
                percentage = int(progress * 100)
                
                # Update display
                clear_screen()
                print(colorize("=" * 60, Colors.BRIGHT_CYAN))
                print(colorize("🎣  FISHING  🎣", Colors.BRIGHT_CYAN + Colors.BOLD))
                print(colorize("=" * 60, Colors.CYAN))
                print(f"\n{colorize('Casting line...', Colors.WHITE)}")
                print(f"\n{colorize('Progress:', Colors.BRIGHT_WHITE)} [{bar}] {colorize(f'{percentage}%', Colors.BRIGHT_YELLOW)}")
                print(f"\n{colorize('Total Caught:', Colors.WHITE)} {colorize(str(catch_count), Colors.BRIGHT_YELLOW)} fish")
                if total_value > 0:
                    print(f"{colorize('Total Value:', Colors.WHITE)} {colorize(str(total_value) + 'g', Colors.BRIGHT_YELLOW)}")
                if total_xp > 0:
                    print(f"{colorize('Total XP:', Colors.BRIGHT_CYAN)} {colorize(str(total_xp), Colors.BRIGHT_GREEN)}")
                print(f"\n{colorize('Press Enter to stop fishing', Colors.YELLOW)}")
                print(colorize("=" * 60, Colors.CYAN))
                
                if not DEV_FLAGS['fast']:
                    # Calculate elapsed time and adjust sleep to maintain exact duration
                    elapsed_time = time.time() - start_time
                    target_time = (i + 1) * (fishing_duration / progress_steps)
                    sleep_time = max(0.0, target_time - elapsed_time)
                    if sleep_time > 0:
                        time.sleep(sleep_time)
            
            if not fishing_active:
                break
            
            # Check for line break (5% chance)
            from ..constants import FISHING_RARE_CATCH_CHANCE
            if random.random() < FISHING_RARE_CATCH_CHANCE:
                continue  # Skip this catch
            
            # Determine catch using level-based weighting
            caught_fish_key, caught_fish_data = get_fishing_catch(player, eligible_fish)
            
            if caught_fish_key:
                # Add to inventory
                add_item_to_inventory(player.inventory, caught_fish_data.copy())
                fish_caught.append(caught_fish_data['name'])
                total_value += caught_fish_data['sell_value']
                catch_count += 1
                
                # Award XP
                xp_amount = FISHING_XP_AWARDS.get(caught_fish_key, 10)
                total_xp += xp_amount
                add_skill_xp(player, "fishing", xp_amount)
                
                # Check achievements
                if catch_count == 1:
                    check_achievements(player, 'first_catch')
                
                if not DEV_FLAGS['quiet']:
                    formatted_name = format_item_name(caught_fish_data)
                    from ..constants import NOTIFICATION_DURATION_MEDIUM
                    show_notification(f"🎣 Caught {formatted_name}! +{xp_amount} XP", Colors.BRIGHT_GREEN, NOTIFICATION_DURATION_MEDIUM)
    
    def input_handler():
        """Handle user input to stop fishing"""
        nonlocal fishing_active
        input()  # Wait for Enter key
        fishing_active = False
    
    # Start input handler thread
    input_thread = threading.Thread(target=input_handler, daemon=True)
    input_thread.start()
    
    # Start fishing loop in main thread
    fishing_loop()
    
    # Show summary
    clear_screen()
    print(colorize("=" * 60, Colors.BRIGHT_CYAN))
    print(colorize("🎣  FISHING SESSION COMPLETE  🎣", Colors.BRIGHT_CYAN + Colors.BOLD))
    print(colorize("=" * 60, Colors.CYAN))
    
    if fish_caught:
        print(f"\n{colorize(f'Total Fish Caught: {len(fish_caught)}', Colors.BRIGHT_GREEN + Colors.BOLD)}")
        print(f"{colorize(f'Total Value: {total_value}g', Colors.BRIGHT_YELLOW + Colors.BOLD)}")
        print(f"{colorize(f'Total XP: +{total_xp}', Colors.BRIGHT_CYAN + Colors.BOLD)}")
        
        # Show fish breakdown
        fish_counts = {}
        for fish_name in fish_caught:
            fish_counts[fish_name] = fish_counts.get(fish_name, 0) + 1
        
        print(f"\n{colorize('Catch Breakdown:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
        for fish_key, fish_data in FISH_TYPES.items():
            if fish_data['name'] in fish_counts:
                count = fish_counts[fish_data['name']]
                formatted_name = format_item_name(fish_data)
                print(f"  {formatted_name}: {colorize(str(count), Colors.BRIGHT_YELLOW)}x")
        
        # Log session
        if len(fish_caught) > 0:
            log_fishing_outcome(player, None, len(fish_caught), total_xp)
    else:
        print(f"\n{colorize('No fish caught this session.', Colors.WHITE)}")
    
    print(colorize("\n" + "=" * 60, Colors.CYAN))
    input(f"\n{colorize('Press Enter to continue...', Colors.BRIGHT_CYAN)}")


def get_fish_key_from_name(fish_name):
    """Map fish name to FISH_TYPES key"""
    for fish_key, fish_data in FISH_TYPES.items():
        if fish_data['name'] == fish_name:
            return fish_key
    return None

