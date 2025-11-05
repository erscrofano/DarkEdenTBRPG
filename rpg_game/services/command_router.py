"""Command router for modern menu system"""
from typing import Optional, Tuple
from ..models.player import Player


class CommandRouter:
    """Routes menu commands to handlers"""
    
    def __init__(self, player: Player, action_service):
        self.player = player
        self.action_service = action_service
        self.menu_stack = []
    
    def route_command(self, command: str) -> Tuple[bool, Optional[str]]:
        """Route command to appropriate handler"""
        if command == "invalid":
            print("\n❌ Invalid choice!")
            input("\nPress Enter to continue...")
            return True, None
        
        if command == "back":
            return True, None
        
        if command == "save":
            success, message = self.action_service.handle_save_action()
            print(f"\n{'✅' if success else '❌'} {message}")
            input("\nPress Enter to continue...")
            return True, None
        
        if command == "quit":
            save_choice = input("\n💾 Save before quitting? (y/n): ").strip().lower()
            if save_choice == 'y':
                success, message = self.action_service.handle_save_action()
                print(f"\n{'✅' if success else '❌'} {message}")
                input("\nPress Enter to continue...")
            print("\n👋 Thanks for playing!")
            return False, None
        
        if command == "dev_menu":
            from ..game.dev_menu import dev_menu
            dev_menu(self.player)
            return True, None
        
        if command.startswith("submenu:"):
            submenu_name = command.split(":", 1)[1]
            self.menu_stack.append(submenu_name)
            return self._handle_submenu(submenu_name)
        
        if command.startswith("explore:"):
            location = command.split(":", 1)[1]
            return self._handle_exploration(location)
        
        if command.startswith("character:"):
            action = command.split(":", 1)[1]
            return self._handle_character_action(action)
        
        if command.startswith("shop:"):
            shop = command.split(":", 1)[1]
            self.action_service.handle_shop_action(shop)
            return True, None
        
        if command.startswith("service:"):
            service = command.split(":", 1)[1]
            self.action_service.handle_service_action(service)
            return True, None
        
        if command.startswith("skill:"):
            skill = command.split(":", 1)[1]
            self.action_service.handle_skill_action(skill)
            return True, None
        
        if command == "travel":
            from ..game import locations_menu
            from ..game.travel import handle_travel
            travel_choice = locations_menu(self.player)
            if travel_choice and travel_choice != '7':
                new_location, success = handle_travel(self.player, travel_choice, 'eslania_city')
                if success:
                    if new_location == 'game_over':
                        return False, 'game_over'
                    return True, new_location
            return True, None
        
        return True, None
    
    def _handle_submenu(self, submenu_name: str) -> Tuple[bool, Optional[str]]:
        """Navigate submenu"""
        from ..game.menus_refactored import (
            explore_menu, character_menu, town_services_menu,
            guilds_menu, shops_menu, services_menu
        )
        
        while True:
            if submenu_name == "explore":
                command = explore_menu(self.player)
            elif submenu_name == "character":
                command = character_menu(self.player)
            elif submenu_name == "town_services":
                command = town_services_menu(self.player)
            elif submenu_name == "guilds":
                command = guilds_menu(self.player)
            elif submenu_name == "shops":
                command = shops_menu(self.player)
            elif submenu_name == "services":
                command = services_menu(self.player)
            else:
                return True, None
            
            if command == "back":
                self.menu_stack.pop() if self.menu_stack else None
                return True, None
            
            result = self.route_command(command)
            
            if not result[0] or result[1] in ['game_over']:
                return result
            
            if result[1]:
                return result
            
            continue
    
    def _handle_exploration(self, location: str) -> Tuple[bool, Optional[str]]:
        """Handle exploration"""
        if location == "underground_waterways":
            result = self.action_service.handle_exploration_action('underground_waterways')
            if result == 'game_over':
                return False, 'game_over'
            elif result == 'previous':
                return True, 'eslania_city'
            return True, result
        
        elif location == "eslania_dungeon":
            result = self.action_service.handle_exploration_action('eslania_dungeon')
            if result == 'previous':
                return True, 'eslania_city'
            return True, None
        
        return True, None
    
    def _handle_character_action(self, action: str) -> Tuple[bool, Optional[str]]:
        """Handle character menu"""
        if action == "stats":
            self.action_service.handle_player_info_action()
        elif action == "inventory":
            self.action_service.handle_view_action('inventory')
        elif action == "achievements":
            self.action_service.handle_view_action('achievements')
        elif action == "allocate_stats":
            self.action_service.handle_stat_allocation()
        
        return True, None

