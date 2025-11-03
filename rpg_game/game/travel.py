"""Travel system for moving between locations"""
from ..constants import TRAVEL_COST
from ..ui import Colors, colorize, clear_screen
from ..game.exploration import explore_multi_floor_dungeon, explore_tepes_lair


def handle_travel(player, travel_choice: str, current_location: str) -> tuple[str, bool]:
    """
    Handle travel between locations.
    
    Args:
        player: Player object
        travel_choice: Choice string from locations menu ('1'-'7')
        current_location: Current location string
        
    Returns:
        Tuple of (new_location, success)
        If success is False, location didn't change
    """
    travel_cost = TRAVEL_COST
    
    if travel_choice == '1':  # Eslania City
        return _travel_to_city(player, current_location, 'eslania_city', 'Eslania City')
    
    elif travel_choice == '2':  # Perona Outpost
        return _travel_to_city(player, current_location, 'perona_outpost', 'Perona Outpost')
    
    elif travel_choice == '3':  # Limbo Dungeon
        floors = {'b1': {'level': 1, 'multiplier': 0.9}, 'b2': {'level': 3, 'multiplier': 0.95}, 'b3': {'level': 5, 'multiplier': 1.0}}
        return _travel_to_dungeon(player, current_location, travel_cost, 'limbo_dungeon', 'Limbo Dungeon', floors)
    
    elif travel_choice == '4':  # Lost Taiyan
        floors = {'b1': {'level': 8, 'multiplier': 1.2}, 'b2': {'level': 12, 'multiplier': 1.3}, 'b3': {'level': 16, 'multiplier': 1.4}}
        return _travel_to_dungeon(player, current_location, travel_cost, 'lost_taiyan', 'Lost Taiyan', floors)
    
    elif travel_choice == '5':  # Rhaom Dungeon
        floors = {'b1': {'level': 3, 'multiplier': 1.0}, 'b2': {'level': 6, 'multiplier': 1.1}, 'b3': {'level': 10, 'multiplier': 1.2}}
        return _travel_to_dungeon(player, current_location, travel_cost, 'rhaom_dungeon', 'Rhaom Dungeon', floors)
    
    elif travel_choice == '6':  # Tepes lair
        return _travel_to_tepes_lair(player, current_location, travel_cost)
    
    # travel_choice == '7' means Back
    return current_location, False


def _travel_to_city(player, current_location: str, city_key: str, city_name: str) -> tuple[str, bool]:
    """Helper to travel to a city"""
    if current_location == city_key:
        clear_screen()
        print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
        print(colorize("⚠️  ALREADY THERE  ⚠️", Colors.BRIGHT_YELLOW + Colors.BOLD))
        print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
        print(f"\n{colorize(f'You are already in {city_name}!', Colors.WHITE)}")
        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
        return current_location, False
    else:
        # Traveling from another location - charge cost
        travel_cost = TRAVEL_COST
        if player.gold >= travel_cost:
            player.gold -= travel_cost
            player.current_location = city_key
            print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(f'Traveled to {city_name} for {travel_cost:,} gold!', Colors.WHITE)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
            return city_key, True
        else:
            print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(f'You need {travel_cost:,} gold to travel!', Colors.WHITE)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
            return current_location, False


def _travel_to_dungeon(player, current_location: str, travel_cost: int, dungeon_key: str, dungeon_name: str, floors: dict) -> tuple[str, bool]:
    """Helper to travel to a dungeon"""
    if player.gold >= travel_cost:
        player.gold -= travel_cost
        print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(f'Traveled to {dungeon_name} for {travel_cost:,} gold!', Colors.WHITE)}")
        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
        result = explore_multi_floor_dungeon(player, dungeon_key, floors, 'b1')
        if result == 'previous':
            # Return to the previous location (could be either city)
            if current_location == 'perona_outpost':
                player.current_location = 'perona_outpost'
                return 'perona_outpost', True
            else:
                player.current_location = 'eslania_city'
                return 'eslania_city', True
        return result, True
    else:
        print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(f'You need {travel_cost:,} gold to travel!', Colors.WHITE)}")
        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
        return current_location, False


def _travel_to_tepes_lair(player, current_location: str, travel_cost: int) -> tuple[str, bool]:
    """Helper to travel to Tepes lair"""
    if player.gold >= travel_cost:
        player.gold -= travel_cost
        print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(f'Traveled to Tepes lair for {travel_cost:,} gold!', Colors.WHITE)}")
        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
        result = explore_tepes_lair(player)
        if result == 'game_over':
            return 'game_over', True
        elif result == 'previous' or result == 'town':
            # Return to the previous location (could be either city)
            if current_location == 'perona_outpost':
                player.current_location = 'perona_outpost'
                return 'perona_outpost', True
            else:
                player.current_location = 'eslania_city'
                return 'eslania_city', True
        else:
            return result, True
    else:
        print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(f'You need {travel_cost:,} gold to travel!', Colors.WHITE)}")
        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
        return current_location, False

