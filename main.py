#!/usr/bin/env python3
"""Main entry point for the RPG game"""
import sys
import argparse
import random
from rpg_game.config import DEV_FLAGS
from rpg_game.ui import clear_screen, Colors, colorize
from rpg_game.models import Player
from rpg_game.save.system import load_game, save_game
from rpg_game.game import (
    town_menu, view_inventory, view_achievements,
    weapon_shop, armor_shop, hospital,
    explore_location, explore_tepes_lair, explore_multi_floor_dungeon,
    allocate_stats, locations_menu, eslania_city_menu, perona_outpost_menu,
    knight_guild, army_guild, cleric_guild, general_store, fishing_store, mining_store, pimping_service
)
from rpg_game.skills import go_fishing, go_mining, cook_fish, training_simulator


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description='Terminal RPG Game')
    parser.add_argument('--fast', action='store_true', help='Skip sleep delays (fast mode)')
    parser.add_argument('--quiet', action='store_true', help='Suppress non-critical notifications')
    parser.add_argument('--no-color', action='store_true', help='Disable ANSI colors')
    parser.add_argument('--seed', type=int, help='Random seed for reproducible runs')
    parser.add_argument('--new', action='store_true', help='Start a new game (bypass menu)')
    parser.add_argument('--load', action='store_true', help='Load existing game (bypass menu)')
    parser.add_argument('--name', type=str, help='Player name (use with --new)')
    parser.add_argument('--auto', action='store_true', help='Run one encounter then quit (for CI)')
    return parser.parse_args()


def main():
    clear_screen()
    print("=" * 50)
    print("⚔️  TEXT-BASED RPG GAME  ⚔️")
    print("=" * 50)
    print("\nWelcome, adventurer!")
    
    # Check for save file
    saved_player = load_game()
    if saved_player:
        print("\n💾 A saved game was found!")
        load_choice = input("Load saved game? (y/n): ").strip().lower()
        if load_choice == 'y':
            player = saved_player
            print(f"\n✅ Welcome back, {player.name}!")
            input("\nPress Enter to continue...")
        else:
            name = input("\nEnter your name: ").strip()
            if not name:
                name = "Hero"
            player = Player(name)
            print(f"\n✅ Welcome, {player.name}!")
            print(f"⚔️ You start with a {player.weapon['name']} (+{player.weapon['attack']} Attack)")
            print(f"💰 You have {player.gold} gold to start your adventure!")
            input("\nPress Enter to begin...")
    else:
        name = input("\nEnter your name: ").strip()
        if not name:
            name = "Hero"
        player = Player(name)
        print(f"\n✅ Welcome, {player.name}!")
        print(f"⚔️ You start with a {player.weapon['name']} (+{player.weapon['attack']} Attack)")
        print(f"💰 You have {player.gold} gold to start your adventure!")
        input("\nPress Enter to begin...")
    
    # Use player's saved location, or default to eslania_city for new games
    current_location = player.current_location
    game_running = True
    
    while game_running and player.is_alive():
        # Sync player's location with current_location at the start of each loop
        player.current_location = current_location
        
        if current_location == 'town':
            # Town is now an alias for Eslania City (backward compatibility)
            current_location = 'eslania_city'
            player.current_location = 'eslania_city'
        
        if current_location == 'eslania_city':
            choice = eslania_city_menu(player)
            
            if choice == '1':
                knight_guild(player)
            elif choice == '2':
                army_guild(player)
            elif choice == '3':
                cleric_guild(player)
            elif choice == '4':
                general_store(player)
            elif choice == '5':
                fishing_store(player)
            elif choice == '6':
                mining_store(player)
            elif choice == '7':
                hospital(player)
            elif choice == '8':
                pimping_service(player)
            elif choice == '9':
                # Training Zone
                training_simulator(player)
            elif choice == '10':
                # Kitchen (Cook Fish)
                cook_fish(player)
            elif choice == '11':
                # Underground Waterways
                result = explore_location(player, 'underground_waterways')
                if result == 'game_over':
                    game_running = False
                elif result == 'previous':
                    current_location = 'eslania_city'
                else:
                    current_location = result
            elif choice == '12':
                # Eslania Dungeon
                floors = {'b1': {'level': 5, 'multiplier': 1.0}, 'b2': {'level': 10, 'multiplier': 1.2}, 'b3': {'level': 15, 'multiplier': 1.4}}
                result = explore_multi_floor_dungeon(player, 'eslania_dungeon', floors, 'b1')
                if result == 'previous':
                    current_location = 'eslania_city'
            elif choice == '13':
                # Go Fishing
                go_fishing(player)
            elif choice == '14':
                # Go Mining
                go_mining(player)
            elif choice == '15':
                # Travel to Another Location
                travel_choice = locations_menu(player)
                travel_cost = 5000  # Cost for non-local travel
                
                if travel_choice == '1':  # Eslania City
                    if current_location == 'eslania_city':
                        clear_screen()
                        print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
                        print(colorize("⚠️  ALREADY THERE  ⚠️", Colors.BRIGHT_YELLOW + Colors.BOLD))
                        print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
                        print(f"\n{colorize('You are already in Eslania City!', Colors.WHITE)}")
                        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                    else:
                        # Traveling from another location - charge cost
                        if player.gold >= travel_cost:
                            player.gold -= travel_cost
                            current_location = 'eslania_city'
                            player.current_location = 'eslania_city'
                            print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(f'Traveled to Eslania City for {travel_cost:,} gold!', Colors.WHITE)}")
                            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                        else:
                            print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(f'You need {travel_cost:,} gold to travel!', Colors.WHITE)}")
                            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                elif travel_choice == '2':  # Perona Outpost
                    if current_location == 'perona_outpost':
                        clear_screen()
                        print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
                        print(colorize("⚠️  ALREADY THERE  ⚠️", Colors.BRIGHT_YELLOW + Colors.BOLD))
                        print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
                        print(f"\n{colorize('You are already in Perona Outpost!', Colors.WHITE)}")
                        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                    else:
                        # Traveling from another location - charge cost
                        if player.gold >= travel_cost:
                            player.gold -= travel_cost
                            current_location = 'perona_outpost'
                            player.current_location = 'perona_outpost'
                            print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(f'Traveled to Perona Outpost for {travel_cost:,} gold!', Colors.WHITE)}")
                            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                        else:
                            print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(f'You need {travel_cost:,} gold to travel!', Colors.WHITE)}")
                            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                elif travel_choice == '3':  # Limbo Dungeon
                    # Non-local dungeon - always costs money
                    if player.gold >= travel_cost:
                        player.gold -= travel_cost
                        print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(f'Traveled to Limbo Dungeon for {travel_cost:,} gold!', Colors.WHITE)}")
                        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                        floors = {'b1': {'level': 1, 'multiplier': 0.9}, 'b2': {'level': 3, 'multiplier': 0.95}, 'b3': {'level': 5, 'multiplier': 1.0}}
                        result = explore_multi_floor_dungeon(player, 'limbo_dungeon', floors, 'b1')
                        if result == 'previous':
                            current_location = 'eslania_city'  # Return to previous location
                            player.current_location = 'eslania_city'
                    else:
                        print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(f'You need {travel_cost:,} gold to travel!', Colors.WHITE)}")
                        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                elif travel_choice == '4':  # Lost Taiyan
                    # Non-local dungeon - always costs money
                    if player.gold >= travel_cost:
                        player.gold -= travel_cost
                        print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(f'Traveled to Lost Taiyan for {travel_cost:,} gold!', Colors.WHITE)}")
                        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                        floors = {'b1': {'level': 8, 'multiplier': 1.2}, 'b2': {'level': 12, 'multiplier': 1.3}, 'b3': {'level': 16, 'multiplier': 1.4}}
                        result = explore_multi_floor_dungeon(player, 'lost_taiyan', floors, 'b1')
                        if result == 'previous':
                            current_location = 'eslania_city'  # Return to previous location
                            player.current_location = 'eslania_city'
                    else:
                        print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(f'You need {travel_cost:,} gold to travel!', Colors.WHITE)}")
                        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                elif travel_choice == '5':  # Rhaom Dungeon
                    # Non-local dungeon - always costs money
                    if player.gold >= travel_cost:
                        player.gold -= travel_cost
                        print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(f'Traveled to Rhaom Dungeon for {travel_cost:,} gold!', Colors.WHITE)}")
                        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                        floors = {'b1': {'level': 3, 'multiplier': 1.0}, 'b2': {'level': 6, 'multiplier': 1.1}, 'b3': {'level': 10, 'multiplier': 1.2}}
                        result = explore_multi_floor_dungeon(player, 'rhaom_dungeon', floors, 'b1')
                        if result == 'previous':
                            current_location = 'eslania_city'  # Return to previous location
                            player.current_location = 'eslania_city'
                    else:
                        print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(f'You need {travel_cost:,} gold to travel!', Colors.WHITE)}")
                        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                elif travel_choice == '6':  # Tepes lair
                    # Non-local dungeon - always costs money
                    if player.gold >= travel_cost:
                        player.gold -= travel_cost
                        print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(f'Traveled to Tepes lair for {travel_cost:,} gold!', Colors.WHITE)}")
                        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                        result = explore_tepes_lair(player)
                        if result == 'game_over':
                            game_running = False
                        elif result == 'previous' or result == 'town':
                            current_location = 'eslania_city'  # Return to previous location
                            player.current_location = 'eslania_city'
                        else:
                            current_location = result
                            player.current_location = result
                    else:
                        print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(f'You need {travel_cost:,} gold to travel!', Colors.WHITE)}")
                        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                # travel_choice == '7' means Back, so do nothing
            elif choice == '16':
                clear_screen()
                print(player.get_stats())
                if player.stat_points > 0:
                    print(f"\n{colorize('💡 You have banked stat points available!', Colors.BRIGHT_YELLOW + Colors.BOLD)}")
                    allocate_choice = input(f"\n{colorize('Would you like to allocate stat points? (y/n): ', Colors.BRIGHT_CYAN)}").strip().lower()
                    if allocate_choice == 'y':
                        allocate_stats(player)
                input("\nPress Enter to continue...")
            elif choice == '17':
                view_inventory(player)
            elif choice == '18':
                view_achievements(player)
            elif choice == '19':
                if player.stat_points > 0:
                    allocate_stats(player)
                else:
                    # No stat points - option 19 is Save Game
                    if save_game(player):
                        print("\n✅ Game saved successfully!")
                    else:
                        print("\n❌ Failed to save game!")
                    input("\nPress Enter to continue...")
            elif choice == '20':
                if player.stat_points > 0:
                    if save_game(player):
                        print("\n✅ Game saved successfully!")
                    else:
                        print("\n❌ Failed to save game!")
                    input("\nPress Enter to continue...")
                else:
                    save_choice = input("\n💾 Save before quitting? (y/n): ").strip().lower()
                    if save_choice == 'y':
                        if save_game(player):
                            print("\n✅ Game saved successfully!")
                        else:
                            print("\n❌ Failed to save game!")
                        input("\nPress Enter to continue...")
                    print("\n👋 Thanks for playing!")
                    game_running = False
            elif choice == '21':
                if player.stat_points > 0:
                    save_choice = input("\n💾 Save before quitting? (y/n): ").strip().lower()
                    if save_choice == 'y':
                        if save_game(player):
                            print("\n✅ Game saved successfully!")
                        else:
                            print("\n❌ Failed to save game!")
                        input("\nPress Enter to continue...")
                    print("\n👋 Thanks for playing!")
                    game_running = False
            else:
                print("\n❌ Invalid choice!")
                input("\nPress Enter to continue...")
        
        elif current_location == 'perona_outpost':
            choice = perona_outpost_menu(player)
            
            if choice == '1':
                floors = {'b1': {'level': 8, 'multiplier': 1.0}, 'b2': {'level': 12, 'multiplier': 1.3}, 'b3': {'level': 18, 'multiplier': 1.6}}
                result = explore_multi_floor_dungeon(player, 'asylion_dungeon', floors, 'b1')
                if result == 'previous':
                    current_location = 'perona_outpost'
            elif choice == '2':
                # Travel to Another Location
                travel_choice = locations_menu(player)
                travel_cost = 5000  # Cost for non-local travel
                
                if travel_choice == '1':  # Eslania City
                    if current_location == 'eslania_city':
                        clear_screen()
                        print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
                        print(colorize("⚠️  ALREADY THERE  ⚠️", Colors.BRIGHT_YELLOW + Colors.BOLD))
                        print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
                        print(f"\n{colorize('You are already in Eslania City!', Colors.WHITE)}")
                        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                    else:
                        # Traveling from another location - charge cost
                        if player.gold >= travel_cost:
                            player.gold -= travel_cost
                            current_location = 'eslania_city'
                            player.current_location = 'eslania_city'
                            print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(f'Traveled to Eslania City for {travel_cost:,} gold!', Colors.WHITE)}")
                            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                        else:
                            print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(f'You need {travel_cost:,} gold to travel!', Colors.WHITE)}")
                            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                elif travel_choice == '2':  # Perona Outpost
                    if current_location == 'perona_outpost':
                        clear_screen()
                        print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
                        print(colorize("⚠️  ALREADY THERE  ⚠️", Colors.BRIGHT_YELLOW + Colors.BOLD))
                        print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
                        print(f"\n{colorize('You are already in Perona Outpost!', Colors.WHITE)}")
                        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                    else:
                        # Traveling from another location - charge cost
                        if player.gold >= travel_cost:
                            player.gold -= travel_cost
                            current_location = 'perona_outpost'
                            player.current_location = 'perona_outpost'
                            print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(f'Traveled to Perona Outpost for {travel_cost:,} gold!', Colors.WHITE)}")
                            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                        else:
                            print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(f'You need {travel_cost:,} gold to travel!', Colors.WHITE)}")
                            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                elif travel_choice == '3':  # Limbo Dungeon
                    # Non-local dungeon - always costs money
                    if player.gold >= travel_cost:
                        player.gold -= travel_cost
                        print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(f'Traveled to Limbo Dungeon for {travel_cost:,} gold!', Colors.WHITE)}")
                        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                        floors = {'b1': {'level': 1, 'multiplier': 0.9}, 'b2': {'level': 3, 'multiplier': 0.95}, 'b3': {'level': 5, 'multiplier': 1.0}}
                        result = explore_multi_floor_dungeon(player, 'limbo_dungeon', floors, 'b1')
                        if result == 'previous':
                            current_location = 'perona_outpost'  # Return to previous location
                            player.current_location = 'perona_outpost'
                    else:
                        print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(f'You need {travel_cost:,} gold to travel!', Colors.WHITE)}")
                        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                elif travel_choice == '4':  # Lost Taiyan
                    # Non-local dungeon - always costs money
                    if player.gold >= travel_cost:
                        player.gold -= travel_cost
                        print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(f'Traveled to Lost Taiyan for {travel_cost:,} gold!', Colors.WHITE)}")
                        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                        floors = {'b1': {'level': 8, 'multiplier': 1.2}, 'b2': {'level': 12, 'multiplier': 1.3}, 'b3': {'level': 16, 'multiplier': 1.4}}
                        result = explore_multi_floor_dungeon(player, 'lost_taiyan', floors, 'b1')
                        if result == 'previous':
                            current_location = 'perona_outpost'  # Return to previous location
                            player.current_location = 'perona_outpost'
                    else:
                        print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(f'You need {travel_cost:,} gold to travel!', Colors.WHITE)}")
                        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                elif travel_choice == '5':  # Rhaom Dungeon
                    # Non-local dungeon - always costs money
                    if player.gold >= travel_cost:
                        player.gold -= travel_cost
                        print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(f'Traveled to Rhaom Dungeon for {travel_cost:,} gold!', Colors.WHITE)}")
                        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                        floors = {'b1': {'level': 3, 'multiplier': 1.0}, 'b2': {'level': 6, 'multiplier': 1.1}, 'b3': {'level': 10, 'multiplier': 1.2}}
                        result = explore_multi_floor_dungeon(player, 'rhaom_dungeon', floors, 'b1')
                        if result == 'previous':
                            current_location = 'perona_outpost'  # Return to previous location
                            player.current_location = 'perona_outpost'
                    else:
                        print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(f'You need {travel_cost:,} gold to travel!', Colors.WHITE)}")
                        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                elif travel_choice == '6':  # Tepes lair
                    # Non-local dungeon - always costs money
                    if player.gold >= travel_cost:
                        player.gold -= travel_cost
                        print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(f'Traveled to Tepes lair for {travel_cost:,} gold!', Colors.WHITE)}")
                        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                        result = explore_tepes_lair(player)
                        if result == 'game_over':
                            game_running = False
                        elif result == 'previous' or result == 'town':
                            current_location = 'perona_outpost'  # Return to previous location
                            player.current_location = 'perona_outpost'
                        else:
                            current_location = result
                            player.current_location = result
                    else:
                        print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(f'You need {travel_cost:,} gold to travel!', Colors.WHITE)}")
                        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                # travel_choice == '7' means Back, so do nothing
            elif choice == '3':  # View Stats
                clear_screen()
                print(player.get_stats())
                input("\nPress Enter to continue...")
            elif choice == '4':  # View Inventory
                view_inventory(player)
            elif choice == '5':  # View Achievements
                view_achievements(player)
            elif choice == '6':  # Allocate Stats or Save Game
                if player.stat_points > 0:
                    allocate_stats(player)
                else:
                    if save_game(player):
                        print("\n✅ Game saved successfully!")
                    else:
                        print("\n❌ Failed to save game!")
                    input("\nPress Enter to continue...")
            elif choice == '7':  # Save Game or Quit Game
                if player.stat_points > 0:
                    if save_game(player):
                        print("\n✅ Game saved successfully!")
                    else:
                        print("\n❌ Failed to save game!")
                    input("\nPress Enter to continue...")
                else:
                    save_choice = input("\n💾 Save before quitting? (y/n): ").strip().lower()
                    if save_choice == 'y':
                        if save_game(player):
                            print("\n✅ Game saved successfully!")
                        else:
                            print("\n❌ Failed to save game!")
                        input("\nPress Enter to continue...")
                    print("\n👋 Thanks for playing!")
                    game_running = False
            elif choice == '8':  # Quit Game
                if player.stat_points > 0:
                    save_choice = input("\n💾 Save before quitting? (y/n): ").strip().lower()
                    if save_choice == 'y':
                        if save_game(player):
                            print("\n✅ Game saved successfully!")
                        else:
                            print("\n❌ Failed to save game!")
                        input("\nPress Enter to continue...")
                    print("\n👋 Thanks for playing!")
                    game_running = False
            else:
                print("\n❌ Invalid choice!")
                input("\nPress Enter to continue...")
        
    
    if not player.is_alive():
        clear_screen()
        print("=" * 50)
        print("💀 GAME OVER 💀")
        print("=" * 50)
        print(f"\n{player.name} has fallen in battle...")
        print(f"\nFinal Level: {player.level}")
        print(f"Final Gold: {player.gold}")
        print("\nThanks for playing!")
        input("\nPress Enter to exit...")


if __name__ == "__main__":
    try:
        # Parse command-line arguments
        args = parse_args()
        
        # Apply developer flags
        DEV_FLAGS['fast'] = args.fast
        DEV_FLAGS['quiet'] = args.quiet
        DEV_FLAGS['no_color'] = args.no_color
        if args.seed is not None:
            DEV_FLAGS['seed'] = args.seed
            random.seed(args.seed)
        
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Game interrupted. Thanks for playing!")
        sys.exit(0)

