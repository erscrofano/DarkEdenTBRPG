#!/usr/bin/env python3
"""Main entry point for the RPG game"""
import sys
import argparse
import random
from rpg_game.config import DEV_FLAGS
from rpg_game.ui import clear_screen, Colors, colorize
from rpg_game.models import Player
from rpg_game.save.system import load_game, save_game, get_save_paths, list_save_slots
from rpg_game.game.save_slots import select_save_slot_menu
from rpg_game.constants import DEFAULT_SAVE_SLOT
import shutil
from pathlib import Path
from rpg_game.game import (
    town_menu, view_inventory, view_achievements,
    weapon_shop, armor_shop, hospital,
    explore_location, explore_tepes_lair, explore_multi_floor_dungeon,
    allocate_stats, locations_menu, eslania_city_menu, perona_outpost_menu,
    knight_guild, army_guild, cleric_guild, general_store, fishing_store, mining_store, pimping_service
)
from rpg_game.skills import go_fishing, go_mining, cook_fish, training_simulator
from rpg_game.utils.input_validation import validate_player_name
from rpg_game.game.travel import handle_travel


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


def migrate_old_save():
    """Migrate old game_save.json to new save_main.json format"""
    from rpg_game.save.system import get_save_dir
    import json
    from rpg_game.models.player import Player
    
    save_dir = get_save_dir()
    old_save = save_dir / 'game_save.json'
    
    if old_save.exists():
        # Check if main slot already exists
        new_paths = get_save_paths(DEFAULT_SAVE_SLOT)
        if not new_paths['save'].exists():
            try:
                # Load old save directly from old path
                with open(old_save, 'r') as f:
                    data = json.load(f)
                
                old_player = Player.from_dict(data)
                old_player.save_slot = DEFAULT_SAVE_SLOT
                
                # Save using new system (this will save with save_slot in the data)
                if save_game(old_player, DEFAULT_SAVE_SLOT):
                    print(f"\n{colorize('📦', Colors.BRIGHT_YELLOW)} {colorize('Migrated old save file to save slot "main"', Colors.WHITE)}")
                    # Backup old save (rename instead of delete for safety)
                    old_backup = save_dir / 'game_save.json.old'
                    if not old_backup.exists():
                        old_save.rename(old_backup)
                    return True
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                from rpg_game.utils.logging import log_error
                log_error(f"Failed to migrate old save (corrupted): {e}")
                # Don't migrate corrupted saves
                return False
            except Exception as e:
                from rpg_game.utils.logging import log_error
                log_error(f"Failed to migrate old save: {e}")
                return False
    return False


def main():
    clear_screen()
    print("=" * 50)
    print("⚔️  TEXT-BASED RPG GAME  ⚔️")
    print("=" * 50)
    print("\nWelcome, adventurer!")
    
    # Migrate old saves if they exist
    migrate_old_save()
    
    # Show save slot selection menu
    slot_name, is_new = select_save_slot_menu(allow_new=True, allow_delete=False)
    
    if slot_name is None:
        # User cancelled
        print("\n👋 Thanks for playing!")
        return
    
    player = None
    
    if is_new:
        # Create new character
        print(f"\n{colorize('Creating new character in save slot:', Colors.BRIGHT_GREEN)} {colorize(slot_name, Colors.BRIGHT_CYAN)}")
        while True:
            name = input(f"\n{colorize('Enter your name:', Colors.BRIGHT_CYAN)} ").strip()
            is_valid, error_msg = validate_player_name(name)
            if is_valid:
                break
            elif not name:  # Empty name defaults to "Hero"
                name = "Hero"
                break
            else:
                print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(error_msg, Colors.WHITE)}")
        player = Player(name)
        player.save_slot = slot_name
        print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(f'Welcome, {player.name}!', Colors.BRIGHT_GREEN)}")
        print(f"⚔️ You start with a {player.weapon['name']} (+{player.weapon['attack']} Attack)")
        print(f"💰 You have {player.gold} gold to start your adventure!")
        input("\nPress Enter to begin...")
    else:
        # Load existing save
        saved_player = load_game(slot_name)
        if saved_player:
            player = saved_player
            print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(f'Welcome back, {player.name}!', Colors.BRIGHT_GREEN)}")
            input("\nPress Enter to continue...")
        else:
            # Slot exists but save is corrupted or missing - ask to create new
            print(f"\n{colorize('⚠️', Colors.YELLOW)} {colorize(f'Could not load save slot "{slot_name}"', Colors.WHITE)}")
            create_new = input(f"{colorize('Create a new character in this slot? (y/n): ', Colors.WHITE)}").strip().lower()
            if create_new == 'y':
                while True:
                    name = input(f"\n{colorize('Enter your name:', Colors.BRIGHT_CYAN)} ").strip()
                    is_valid, error_msg = validate_player_name(name)
                    if is_valid:
                        break
                    elif not name:
                        name = "Hero"
                        break
                    else:
                        print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(error_msg, Colors.WHITE)}")
                player = Player(name)
                player.save_slot = slot_name
                print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(f'Welcome, {player.name}!', Colors.BRIGHT_GREEN)}")
                print(f"⚔️ You start with a {player.weapon['name']} (+{player.weapon['attack']} Attack)")
                print(f"💰 You have {player.gold} gold to start your adventure!")
                input("\nPress Enter to begin...")
            else:
                print("\n👋 Thanks for playing!")
                return
    
    if player is None:
        return
    
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
                if travel_choice and travel_choice != '7':  # '7' means Back
                    new_location, success = handle_travel(player, travel_choice, current_location)
                    if success:
                        if new_location == 'game_over':
                            game_running = False
                        else:
                            current_location = new_location
                            player.current_location = new_location
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
                if travel_choice and travel_choice != '7':  # '7' means Back
                    new_location, success = handle_travel(player, travel_choice, current_location)
                    if success:
                        if new_location == 'game_over':
                            game_running = False
                        else:
                            current_location = new_location
                            player.current_location = new_location
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

