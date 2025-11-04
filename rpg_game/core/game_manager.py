"""Game Manager - Central game state and flow coordinator"""
from typing import Optional
from .game_states import GameState, validate_transition
from ..models.player import Player
from ..save.system import load_game, save_game, get_save_dir
from ..game.save_slots import select_save_slot_menu
from ..ui import clear_screen, Colors, colorize
from ..utils.input_validation import validate_player_name
from ..constants import DEFAULT_SAVE_SLOT
from ..utils.logging import log_info, log_error
import json
from pathlib import Path


class GameManager:
    """
    Central game state manager and coordinator.
    Manages game loop, state transitions, and system coordination.
    """
    
    def __init__(self):
        """Initialize the game manager"""
        self.state = GameState.INITIALIZING
        self.player: Optional[Player] = None
        self.current_location: Optional[str] = None
        self.previous_location: Optional[str] = None
        self.running = True
        self.selected_slot: Optional[str] = None
        
    def run(self):
        """Main game loop with state machine"""
        log_info("GameManager started")
        self.transition_to(GameState.MAIN_MENU)
        
        while self.running:
            try:
                if self.state == GameState.MAIN_MENU:
                    self.handle_main_menu()
                    
                elif self.state == GameState.CHARACTER_CREATION:
                    if not self.handle_character_creation():
                        self.transition_to(GameState.MAIN_MENU)
                        
                elif self.state == GameState.LOADING_GAME:
                    if not self.handle_loading_game():
                        self.transition_to(GameState.MAIN_MENU)
                        
                elif self.state == GameState.IN_GAME:
                    self.handle_in_game()
                    
                elif self.state == GameState.GAME_OVER:
                    self.handle_game_over()
                    
                elif self.state == GameState.QUITTING:
                    self.handle_quitting()
                    break
                    
            except (KeyboardInterrupt, SystemExit):
                # Let system exceptions propagate
                raise
            except (ValueError, TypeError, AttributeError, KeyError) as e:
                # Handle specific expected exceptions
                log_error(f"Error in game state {self.state}: {e}", exc_info=True)
                print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('An error occurred. Returning to main menu...', Colors.WHITE)}")
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                self.transition_to(GameState.MAIN_MENU)
            except Exception as e:
                # Catch-all for unexpected errors, but log them properly
                log_error(f"Unexpected error in game state {self.state}: {e}", exc_info=True)
                print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('An unexpected error occurred. Returning to main menu...', Colors.WHITE)}")
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                self.transition_to(GameState.MAIN_MENU)
        
        log_info("GameManager stopped")
    
    def transition_to(self, new_state: GameState):
        """Safely transition to a new game state with validation"""
        if validate_transition(self.state, new_state):
            log_info(f"State transition: {self.state} → {new_state}")
            self.state = new_state
        else:
            log_error(f"Invalid state transition: {self.state} → {new_state}")
            raise ValueError(f"Invalid state transition from {self.state} to {new_state}")
    
    def handle_main_menu(self):
        """Handle save slot selection and menu"""
        clear_screen()
        print("=" * 50)
        print("⚔️  TEXT-BASED RPG GAME  ⚔️")
        print("=" * 50)
        print("\nWelcome, adventurer!")
        
        # Migrate old saves if they exist
        self.migrate_saves()
        
        # Show save slot selection menu
        slot_name, is_new = select_save_slot_menu(allow_new=True, allow_delete=False)
        
        if slot_name is None:
            # User cancelled - quit
            print("\n👋 Thanks for playing!")
            self.transition_to(GameState.QUITTING)
            return
        
        self.selected_slot = slot_name
        
        if is_new:
            self.transition_to(GameState.CHARACTER_CREATION)
        else:
            self.transition_to(GameState.LOADING_GAME)
    
    def handle_character_creation(self) -> bool:
        """
        Handle new character creation.
        Returns True if successful, False to return to main menu.
        """
        if self.selected_slot is None:
            log_error("Character creation called without selected slot")
            return False
        
        print(f"\n{colorize('Creating new character in save slot:', Colors.BRIGHT_GREEN)} {colorize(self.selected_slot, Colors.BRIGHT_CYAN)}")
        
        # Get player name with validation
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
        
        # Create new player
        self.player = Player(name)
        self.player.save_slot = self.selected_slot
        self.current_location = self.player.current_location
        
        # Welcome message
        print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(f'Welcome, {self.player.name}!', Colors.BRIGHT_GREEN)}")
        print(f"⚔️ You start with a {self.player.weapon['name']} (+{self.player.weapon['attack']} Attack)")
        print(f"💰 You have {self.player.gold} gold to start your adventure!")
        input("\nPress Enter to begin...")
        
        log_info(f"New character created: {self.player.name}")
        self.transition_to(GameState.IN_GAME)
        return True
    
    def handle_loading_game(self) -> bool:
        """
        Handle loading an existing save.
        Returns True if successful, False to return to main menu.
        """
        if self.selected_slot is None:
            log_error("Loading game called without selected slot")
            return False
        
        saved_player = load_game(self.selected_slot)
        
        if saved_player:
            self.player = saved_player
            self.current_location = self.player.current_location
            print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(f'Welcome back, {self.player.name}!', Colors.BRIGHT_GREEN)}")
            input("\nPress Enter to continue...")
            log_info(f"Loaded character: {self.player.name}")
            self.transition_to(GameState.IN_GAME)
            return True
        else:
            # Save corrupted or missing - offer to create new
            print(f"\n{colorize('⚠️', Colors.YELLOW)} {colorize(f'Could not load save slot "{self.selected_slot}"', Colors.WHITE)}")
            create_new = input(f"{colorize('Create a new character in this slot? (y/n): ', Colors.WHITE)}").strip().lower()
            
            if create_new == 'y':
                self.transition_to(GameState.CHARACTER_CREATION)
                return False  # Will handle in character_creation state
            else:
                # User declined
                return False
    
    def handle_in_game(self):
        """Main gameplay loop with location routing"""
        if self.player is None:
            log_error("Entered IN_GAME state without player")
            self.transition_to(GameState.MAIN_MENU)
            return
        
        from ..game import (
            eslania_city_menu, perona_outpost_menu,
            knight_guild, army_guild, cleric_guild, general_store,
            fishing_store, mining_store, hospital, pimping_service,
            view_inventory, view_achievements, allocate_stats, locations_menu
        )
        from ..game.dev_menu import dev_menu
        from ..skills import go_fishing, go_mining, cook_fish, training_simulator
        from ..game.exploration import explore_location, explore_multi_floor_dungeon
        from ..game.travel import handle_travel
        
        game_running = True
        
        while game_running and self.state == GameState.IN_GAME:
            # Sync player's location
            self.player.current_location = self.current_location
            
            # Handle legacy 'town' alias
            if self.current_location == 'town':
                self.current_location = 'eslania_city'
                self.player.current_location = 'eslania_city'
            
            # Route to location-specific menu
            if self.current_location == 'eslania_city':
                if not self._handle_eslania_city():
                    game_running = False
                    
            elif self.current_location == 'perona_outpost':
                if not self._handle_perona_outpost():
                    game_running = False
                    
            else:
                log_error(f"Unknown location: {self.current_location}")
                self.current_location = 'eslania_city'
        
        # Game loop ended - check why
        if not self.player.is_alive():
            self.transition_to(GameState.GAME_OVER)
        elif self.state == GameState.IN_GAME:
            # Player quit normally
            self.transition_to(GameState.QUITTING)
    
    def _handle_eslania_city(self) -> bool:
        """Handle Eslania City menu and actions. Returns False to end game loop."""
        from ..game import eslania_city_menu
        from ..services.actions import LocationHandlerService
        
        choice = eslania_city_menu(self.player)
        
        # Use service layer to handle choice
        handler_service = LocationHandlerService(self.player)
        should_continue, new_location = handler_service.handle_eslania_city_choice(choice)
        
        # Update location if changed
        if new_location:
            if new_location == 'game_over':
                return False
            self.current_location = new_location
            self.player.current_location = new_location
        
        return should_continue
    
    def _handle_perona_outpost(self) -> bool:
        """Handle Perona Outpost menu and actions. Returns False to end game loop."""
        from ..game import perona_outpost_menu
        from ..services.actions import LocationHandlerService
        
        choice = perona_outpost_menu(self.player)
        
        # Use service layer to handle choice
        handler_service = LocationHandlerService(self.player)
        should_continue, new_location = handler_service.handle_perona_outpost_choice(choice)
        
        # Update location if changed
        if new_location:
            if new_location == 'game_over':
                return False
            self.current_location = new_location
            self.player.current_location = new_location
        
        return should_continue
    
    def handle_game_over(self):
        """Handle game over state - return to main menu"""
        # Death screen has already been shown by combat system
        # Just transition back to main menu
        self.player = None
        self.current_location = None
        self.selected_slot = None
        self.transition_to(GameState.MAIN_MENU)
    
    def handle_quitting(self):
        """Handle clean application shutdown"""
        self.running = False
        log_info("User quit game")
    
    def migrate_saves(self):
        """Migrate old game_save.json to new save_main.json format"""
        try:
            save_dir = get_save_dir()
            old_save = save_dir / 'game_save.json'
            
            if old_save.exists():
                from ..save.system import get_save_paths
                new_paths = get_save_paths(DEFAULT_SAVE_SLOT)
                
                if not new_paths['save'].exists():
                    try:
                        with open(old_save, 'r') as f:
                            data = json.load(f)
                        
                        old_player = Player.from_dict(data)
                        old_player.save_slot = DEFAULT_SAVE_SLOT
                        
                        if save_game(old_player, DEFAULT_SAVE_SLOT):
                            print(f"\n{colorize('📦', Colors.BRIGHT_YELLOW)} {colorize('Migrated old save file to save slot "main"', Colors.WHITE)}")
                            old_backup = save_dir / 'game_save.json.old'
                            if not old_backup.exists():
                                old_save.rename(old_backup)
                            log_info("Successfully migrated old save file")
                            
                    except (json.JSONDecodeError, KeyError, ValueError) as e:
                        log_error(f"Failed to migrate old save (corrupted): {e}")
                    except Exception as e:
                        log_error(f"Failed to migrate old save: {e}")
                        
        except Exception as e:
            log_error(f"Error in save migration: {e}")

