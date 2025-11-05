"""Refactored menu system using nested menus"""
from ..ui.menu_system import Menu, MenuItem, MenuBuilder
from ..ui import Colors, colorize, clear_screen, display_time_hud
from ..models.player import Player


def eslania_city_menu_modern(player: Player) -> str:
    """
    Modern Eslania City menu with nested structure.
    Returns a command string like "explore:1" or "save" for the handler to process.
    """
    menu = MenuBuilder.create_main_menu(player)
    
    # Display time HUD
    display_time_hud(player)
    
    # Display menu and get choice
    choice = menu.display(context={'player': player, 'location': 'Eslania City'})
    
    # Map choice to command
    if choice == '1':
        return "submenu:explore"
    elif choice == '2':
        return "submenu:character"
    elif choice == '3':
        return "submenu:town_services"
    elif choice == '4':
        return "save"
    elif choice == '5':
        return "quit"
    elif choice == '1337':
        return "dev_menu"
    else:
        return "invalid"


def explore_menu(player: Player) -> str:
    """Exploration submenu"""
    menu = MenuBuilder._create_explore_menu()
    
    display_time_hud(player)
    choice = menu.display(context={'player': player})
    
    # Map to commands
    commands = {
        '1': 'explore:underground_waterways',
        '2': 'explore:eslania_dungeon',
        '3': 'skill:fishing',
        '4': 'skill:mining',
        '5': 'travel',
        '0': 'back'
    }
    
    return commands.get(choice, 'invalid')


def character_menu(player: Player) -> str:
    """Character management submenu"""
    menu = MenuBuilder._create_character_menu(player)
    
    display_time_hud(player)
    choice = menu.display(context={'player': player})
    
    commands = {
        '1': 'character:stats',
        '2': 'character:inventory',
        '3': 'character:achievements',
        '4': 'character:allocate_stats',
        '0': 'back'
    }
    
    return commands.get(choice, 'invalid')


def town_services_menu(player: Player) -> str:
    """Town services submenu"""
    menu = MenuBuilder._create_town_services_menu()
    
    display_time_hud(player)
    choice = menu.display(context={'player': player})
    
    commands = {
        '1': 'submenu:guilds',
        '2': 'submenu:shops',
        '3': 'submenu:services',
        '0': 'back'
    }
    
    return commands.get(choice, 'invalid')


def guilds_menu(player: Player) -> str:
    """Guilds submenu"""
    menu = MenuBuilder._create_guilds_menu()
    
    display_time_hud(player)
    choice = menu.display(context={'player': player})
    
    commands = {
        '1': 'shop:knight_guild',
        '2': 'shop:army_guild',
        '3': 'shop:cleric_guild',
        '0': 'back'
    }
    
    return commands.get(choice, 'invalid')


def shops_menu(player: Player) -> str:
    """Shops submenu"""
    menu = MenuBuilder._create_shops_menu()
    
    display_time_hud(player)
    choice = menu.display(context={'player': player})
    
    commands = {
        '1': 'shop:general_store',
        '2': 'shop:fishing_store',
        '3': 'shop:mining_store',
        '0': 'back'
    }
    
    return commands.get(choice, 'invalid')


def services_menu(player: Player) -> str:
    """Services submenu"""
    menu = MenuBuilder._create_services_menu()
    
    display_time_hud(player)
    choice = menu.display(context={'player': player})
    
    commands = {
        '1': 'service:hospital',
        '2': 'service:pimping_service',
        '3': 'service:training_simulator',
        '4': 'service:cook_fish',
        '0': 'back'
    }
    
    return commands.get(choice, 'invalid')

