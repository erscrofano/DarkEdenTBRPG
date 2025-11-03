"""Fishing skill system"""
import random
import time
import threading
from datetime import datetime
from ..config import DEV_FLAGS
from ..ui import Colors, colorize, clear_screen, show_notification
from ..items.inventory import add_item_to_inventory
from ..items.rarity import get_item_rarity, format_item_name, ITEM_RARITY
from ..models.location import LOCATIONS
from ..save.system import get_save_dir
from .core import add_skill_xp
from ..achievements.system import check_achievements


# Fishing system - Fish types with rarity (sell_value determines rarity)
FISH_TYPES = {
    'goby': {'name': 'Goby', 'type': 'material', 'sell_value': 2, 'description': 'A small, common fish', 'catch_chance': 0.30, 'key': 'goby'},  # Most common
    'mackerel': {'name': 'Mackerel', 'type': 'material', 'sell_value': 5, 'description': 'A common saltwater fish', 'catch_chance': 0.20, 'key': 'mackerel'},
    'salmon': {'name': 'Salmon', 'type': 'material', 'sell_value': 8, 'description': 'A popular freshwater fish', 'catch_chance': 0.15, 'key': 'salmon'},
    'eel': {'name': 'Eel', 'type': 'material', 'sell_value': 12, 'description': 'A slimy, elusive fish', 'catch_chance': 0.12, 'key': 'eel'},
    'shad': {'name': 'Shad', 'type': 'material', 'sell_value': 15, 'description': 'A medium-sized fish', 'catch_chance': 0.08, 'key': 'shad'},
    'carp': {'name': 'Carp', 'type': 'material', 'sell_value': 18, 'description': 'A large bottom-feeding fish', 'catch_chance': 0.06, 'key': 'carp'},
    'sea_bream': {'name': 'Sea Bream', 'type': 'material', 'sell_value': 25, 'description': 'A prized saltwater fish', 'catch_chance': 0.04, 'key': 'seabream'},
    'silvery_eel': {'name': 'Silvery Eel', 'type': 'material', 'sell_value': 50, 'description': 'A rare silvery eel', 'catch_chance': 0.03, 'key': 'silvery_eel'},
    'silvery_shad': {'name': 'Silvery Shad', 'type': 'material', 'sell_value': 75, 'description': 'An extremely rare silvery shad', 'catch_chance': 0.015, 'key': 'silvery_shad'},
    'silvery_carp': {'name': 'Silvery Carp', 'type': 'material', 'sell_value': 150, 'description': 'The legendary silvery carp - incredibly rare!', 'catch_chance': 0.005, 'key': 'silvery_carp'},  # Most rare
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
    'silvery_carp': 80
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
    'silvery_carp': 200
}

# Cooked fish items - created when cooking succeeds
COOKED_FISH_ITEMS = {
    'goby': {'name': 'Cooked Goby', 'type': 'consumable', 'heal': 10, 'sell_value': 2},
    'mackerel': {'name': 'Cooked Mackerel', 'type': 'consumable', 'heal': 20, 'sell_value': 6},
    'salmon': {'name': 'Cooked Salmon', 'type': 'consumable', 'heal': 35, 'sell_value': 10},
    'eel': {'name': 'Cooked Eel', 'type': 'consumable', 'heal': 50, 'sell_value': 14},
    'shad': {'name': 'Cooked Shad', 'type': 'consumable', 'heal': 70, 'sell_value': 18},
    'carp': {'name': 'Cooked Carp', 'type': 'consumable', 'heal': 90, 'sell_value': 22},
    'seabream': {'name': 'Cooked Seabream', 'type': 'consumable', 'heal': 120, 'sell_value': 32},
    'silvery_eel': {'name': 'Cooked Silvery Eel', 'type': 'consumable', 'heal': 150, 'sell_value': 60},
    'silvery_shad': {'name': 'Cooked Silvery Shad', 'type': 'consumable', 'heal': 180, 'sell_value': 90},
    'silvery_carp': {'name': 'Cooked Silvery Carp', 'type': 'consumable', 'heal': 220, 'sell_value': 150}
}


def get_fishing_catch(player, eligible_fish):
    """Calculate which fish to catch based on level-weighted distribution"""
    if not eligible_fish:
        return None, None
    
    # Calculate level boost (up to 25% absolute)
    level_boost = min(0.25, player.fishing_level * 0.002)
    
    # Build weights with level scaling
    weights = {}
    low_tier_fish = ['goby', 'mackerel', 'salmon']  # Low tier fish that should remain common
    
    for fish_key, fish_data in eligible_fish:
        base_chance = fish_data['catch_chance']
        required_level = FISH_LEVEL_REQUIREMENTS.get(fish_key, 1)
        
        # Rarity weight proportional to required_level / 80
        rarity_weight = required_level / 80.0
        
        # Apply level boost to higher tier fish
        if fish_key not in low_tier_fish:
            weight = base_chance + (level_boost * rarity_weight)
        else:
            weight = base_chance  # Keep low tier at base
        
        weights[fish_key] = weight
    
    # Ensure low tier fish combined are at least 55% of total
    low_tier_total = sum(weights.get(k, 0) for k in low_tier_fish if k in weights)
    total_weight = sum(weights.values())
    
    if low_tier_total / total_weight < 0.55:
        # Boost low tier to maintain 55% minimum
        scale_factor = (0.55 * total_weight) / low_tier_total
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
    print(colorize("=" * 60, Colors.CYAN))
    input(f"\n{colorize('Press Enter to start fishing...', Colors.BRIGHT_CYAN)}")
    
    fishing_active = True
    fish_caught = []
    total_value = 0
    catch_count = 0
    total_xp = 0
    
    # Check inventory for fishing rods (use best one if multiple)
    fishing_speed_boost = 0
    for item in player.inventory:
        if item.get('type') == 'tool' and 'fishing_speed_boost' in item:
            # Use the best rod (most negative boost = fastest)
            if item['fishing_speed_boost'] < fishing_speed_boost:
                fishing_speed_boost = item['fishing_speed_boost']
    
    base_fishing_duration = 8
    fishing_duration = max(1.0, base_fishing_duration + fishing_speed_boost)  # Minimum 1 second
    
    def fishing_loop():
        nonlocal fishing_active, fish_caught, total_value, catch_count, total_xp
        
        while fishing_active:
            # Progress bar for fishing
            progress_steps = 20
            step_delay = fishing_duration / progress_steps
            
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
                    time.sleep(step_delay)
            
            if not fishing_active:
                break
            
            # Check for line break (5% chance)
            if random.random() < 0.05:
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
                
                # Show catch notification (brief)
                if not DEV_FLAGS['quiet']:
                    rarity_key = get_item_rarity(caught_fish_data)
                    rarity_info = ITEM_RARITY[rarity_key]
                    formatted_name = format_item_name(caught_fish_data)
                    show_notification(f"🎣 Caught {formatted_name}! +{xp_amount} XP", Colors.BRIGHT_GREEN, 0.5)
    
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

