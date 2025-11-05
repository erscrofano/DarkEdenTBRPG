"""Service layer for game actions - separates business logic from presentation"""
from typing import Optional
from ..models.player import Player
from ..save.system import save_game


class GameActionService:
    """Service layer for game actions"""
    
    def __init__(self, player: Player):
        self.player = player
    
    def handle_shop_action(self, shop_type: str) -> bool:
        """Handle shop interaction"""
        from ..game import (
            knight_guild, army_guild, cleric_guild,
            general_store, fishing_store, mining_store
        )
        
        shop_handlers = {
            'knight_guild': knight_guild,
            'army_guild': army_guild,
            'cleric_guild': cleric_guild,
            'general_store': general_store,
            'fishing_store': fishing_store,
            'mining_store': mining_store,
        }
        
        handler = shop_handlers.get(shop_type)
        if handler:
            handler(self.player)
            return True
        return False
    
    def handle_service_action(self, service_type: str) -> bool:
        """Handle service interaction"""
        from ..game import hospital, pimping_service
        from ..skills import training_simulator, cook_fish
        
        service_handlers = {
            'hospital': hospital,
            'pimping_service': pimping_service,
            'training_simulator': training_simulator,
            'cook_fish': cook_fish,
        }
        
        handler = service_handlers.get(service_type)
        if handler:
            handler(self.player)
            return True
        return False
    
    def handle_exploration_action(self, location: str) -> Optional[str]:
        """Handle exploration"""
        from ..game.exploration import explore_location, explore_multi_floor_dungeon
        
        if location == 'underground_waterways':
            return explore_location(self.player, 'underground_waterways')
        elif location == 'eslania_dungeon':
            floors = {
                'b1': {'level': 4, 'multiplier': 0.9},
                'b2': {'level': 7, 'multiplier': 1.0},
                'b3': {'level': 10, 'multiplier': 1.1}
            }
            return explore_multi_floor_dungeon(self.player, 'eslania_dungeon', floors, 'b1')
        return None
    
    def handle_skill_action(self, skill_type: str) -> bool:
        """Handle skill use"""
        from ..skills import go_fishing, go_mining
        
        skill_handlers = {
            'fishing': go_fishing,
            'mining': go_mining,
        }
        
        handler = skill_handlers.get(skill_type)
        if handler:
            handler(self.player)
            return True
        return False
    
    def handle_player_info_action(self) -> bool:
        """Display player stats"""
        from ..ui import clear_screen
        from ..game.stats import allocate_stats
        
        clear_screen()
        print(self.player.get_stats())
        if self.player.stat_points > 0:
            from ..ui import Colors, colorize
            print(f"\n{colorize('💡 You have banked stat points available!', Colors.BRIGHT_YELLOW + Colors.BOLD)}")
            allocate_choice = input(f"\n{colorize('Would you like to allocate stat points? (y/n): ', Colors.BRIGHT_CYAN)}").strip().lower()
            if allocate_choice == 'y':
                allocate_stats(self.player)
        input("\nPress Enter to continue...")
        return True
    
    def handle_view_action(self, view_type: str) -> bool:
        """Handle view screens"""
        from ..game import view_inventory, view_achievements
        
        view_handlers = {
            'inventory': view_inventory,
            'achievements': view_achievements,
        }
        
        handler = view_handlers.get(view_type)
        if handler:
            handler(self.player)
            return True
        return False
    
    def handle_save_action(self) -> tuple[bool, str]:
        """Save game"""
        if save_game(self.player):
            return True, "Game saved successfully!"
        return False, "Failed to save game!"
    
    def handle_stat_allocation(self) -> bool:
        """Allocate stat points"""
        from ..game.stats import allocate_stats
        
        if self.player.stat_points > 0:
            allocate_stats(self.player)
            return True
        return False


class LocationHandlerService:
    """Location menu handler"""
    
    def __init__(self, player: Player):
        self.player = player
        self.action_service = GameActionService(player)
    
    def handle_eslania_city_choice(self, choice: str) -> tuple[bool, Optional[str]]:
        """Handle Eslania City menu choice"""
        from ..game import eslania_city_menu, locations_menu
        from ..game.dev_menu import dev_menu
        from ..game.travel import handle_travel
        from ..ui import clear_screen, Colors, colorize
        
        # Check if this is a modern UI command string
        if isinstance(choice, str) and ':' in choice or choice in ['save', 'quit', 'travel', 'invalid', 'dev_menu']:
            from .command_router import CommandRouter
            router = CommandRouter(self.player, self.action_service)
            return router.route_command(choice)
        
        # Hidden dev menu
        if choice == '1337':
            dev_menu(self.player)
            return True, None
        
        # Shops
        shop_map = {
            '1': 'knight_guild',
            '2': 'army_guild',
            '3': 'cleric_guild',
            '4': 'general_store',
            '5': 'fishing_store',
            '6': 'mining_store',
        }
        if choice in shop_map:
            self.action_service.handle_shop_action(shop_map[choice])
            return True, None
        
        # Services
        service_map = {
            '7': 'hospital',
            '8': 'pimping_service',
            '9': 'training_simulator',
            '10': 'cook_fish',
        }
        if choice in service_map:
            self.action_service.handle_service_action(service_map[choice])
            return True, None
        
        # Exploration
        if choice == '11':
            result = self.action_service.handle_exploration_action('underground_waterways')
            if result == 'game_over':
                return False, 'game_over'
            elif result == 'previous':
                return True, 'eslania_city'
            return True, result
        
        if choice == '12':
            result = self.action_service.handle_exploration_action('eslania_dungeon')
            if result == 'previous':
                return True, 'eslania_city'
            return True, None
        
        # Skills
        if choice == '13':
            self.action_service.handle_skill_action('fishing')
            return True, None
        if choice == '14':
            self.action_service.handle_skill_action('mining')
            return True, None
        
        # Travel
        if choice == '15':
            travel_choice = locations_menu(self.player)
            if travel_choice and travel_choice != '7':
                new_location, success = handle_travel(self.player, travel_choice, 'eslania_city')
                if success:
                    if new_location == 'game_over':
                        return False, 'game_over'
                    return True, new_location
            return True, None
        
        # Player info
        if choice == '16':
            self.action_service.handle_player_info_action()
            return True, None
        
        # View actions
        if choice == '17':
            self.action_service.handle_view_action('inventory')
            return True, None
        if choice == '18':
            self.action_service.handle_view_action('achievements')
            return True, None
        
        # Stat allocation or save
        if choice == '19':
            if self.player.stat_points > 0:
                self.action_service.handle_stat_allocation()
            else:
                success, message = self.action_service.handle_save_action()
                print(f"\n{'✅' if success else '❌'} {message}")
                input("\nPress Enter to continue...")
            return True, None
        
        # Save game
        if choice == '20':
            if self.player.stat_points > 0:
                success, message = self.action_service.handle_save_action()
                print(f"\n{'✅' if success else '❌'} {message}")
                input("\nPress Enter to continue...")
            else:
                save_choice = input("\n💾 Save before quitting? (y/n): ").strip().lower()
                if save_choice == 'y':
                    success, message = self.action_service.handle_save_action()
                    print(f"\n{'✅' if success else '❌'} {message}")
                    input("\nPress Enter to continue...")
                print("\n👋 Thanks for playing!")
                return False, None
        
        # Quit game
        if choice == '21':
            if self.player.stat_points > 0:
                save_choice = input("\n💾 Save before quitting? (y/n): ").strip().lower()
                if save_choice == 'y':
                    success, message = self.action_service.handle_save_action()
                    print(f"\n{'✅' if success else '❌'} {message}")
                    input("\nPress Enter to continue...")
                print("\n👋 Thanks for playing!")
                return False, None
        
        # Invalid choice
        print("\n❌ Invalid choice!")
        input("\nPress Enter to continue...")
        return True, None
    
    def handle_perona_outpost_choice(self, choice: str) -> tuple[bool, Optional[str]]:
        """Handle Perona Outpost menu choice"""
        from ..game import perona_outpost_menu, locations_menu
        from ..game.dev_menu import dev_menu
        from ..game.exploration import explore_multi_floor_dungeon
        from ..game.travel import handle_travel
        from ..ui import clear_screen
        
        # Hidden dev menu
        if choice == '1337':
            dev_menu(self.player)
            return True, None
        
        # Exploration
        if choice == '1':
            floors = {
                'b1': {'level': 25, 'multiplier': 1.5},
                'b2': {'level': 35, 'multiplier': 1.8},
                'b3': {'level': 50, 'multiplier': 2.2}
            }
            result = explore_multi_floor_dungeon(self.player, 'asylion_dungeon', floors, 'b1')
            if result == 'previous':
                return True, 'perona_outpost'
            return True, None
        
        # Travel
        if choice == '2':
            travel_choice = locations_menu(self.player)
            if travel_choice and travel_choice != '7':
                new_location, success = handle_travel(self.player, travel_choice, 'perona_outpost')
                if success:
                    if new_location == 'game_over':
                        return False, 'game_over'
                    return True, new_location
            return True, None
        
        # Player info
        if choice == '3':
            clear_screen()
            print(self.player.get_stats())
            input("\nPress Enter to continue...")
            return True, None
        
        # View actions
        if choice == '4':
            self.action_service.handle_view_action('inventory')
            return True, None
        if choice == '5':
            self.action_service.handle_view_action('achievements')
            return True, None
        
        # Stat allocation or save
        if choice == '6':
            if self.player.stat_points > 0:
                self.action_service.handle_stat_allocation()
            else:
                success, message = self.action_service.handle_save_action()
                print(f"\n{'✅' if success else '❌'} {message}")
                input("\nPress Enter to continue...")
            return True, None
        
        # Save game
        if choice == '7':
            if self.player.stat_points > 0:
                success, message = self.action_service.handle_save_action()
                print(f"\n{'✅' if success else '❌'} {message}")
                input("\nPress Enter to continue...")
            else:
                save_choice = input("\n💾 Save before quitting? (y/n): ").strip().lower()
                if save_choice == 'y':
                    success, message = self.action_service.handle_save_action()
                    print(f"\n{'✅' if success else '❌'} {message}")
                    input("\nPress Enter to continue...")
                print("\n👋 Thanks for playing!")
                return False, None
        
        # Quit game
        if choice == '8':
            if self.player.stat_points > 0:
                save_choice = input("\n💾 Save before quitting? (y/n): ").strip().lower()
                if save_choice == 'y':
                    success, message = self.action_service.handle_save_action()
                    print(f"\n{'✅' if success else '❌'} {message}")
                    input("\nPress Enter to continue...")
                print("\n👋 Thanks for playing!")
                return False, None
        
        # Invalid choice
        print("\n❌ Invalid choice!")
        input("\nPress Enter to continue...")
        return True, None

