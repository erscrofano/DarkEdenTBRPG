"""Modern menu system with nested menus and categories"""
from typing import Optional, Callable, List, Tuple
from .colors import Colors, colorize
from .display import clear_screen


class MenuItem:
    """Menu item"""
    
    def __init__(
        self,
        key: str,
        label: str,
        action: Optional[Callable] = None,
        submenu: Optional['Menu'] = None,
        enabled: bool = True,
        badge: Optional[str] = None
    ):
        self.key = key
        self.label = label
        self.action = action
        self.submenu = submenu
        self.enabled = enabled
        self.badge = badge
    
    def is_submenu(self) -> bool:
        return self.submenu is not None
    
    def execute(self, *args, **kwargs):
        """Execute menu action"""
        if self.action:
            return self.action(*args, **kwargs)
        return None


class Menu:
    """Menu container"""
    
    def __init__(self, title: str, description: Optional[str] = None):
        self.title = title
        self.description = description
        self.items: List[MenuItem] = []
    
    def add_item(self, item: MenuItem):
        """Add menu item"""
        self.items.append(item)
        return self
    
    def add_separator(self):
        """Add separator"""
        self.items.append(MenuItem("", "---", enabled=False))
        return self
    
    def display(self, context: dict = None) -> str:
        """Display menu and return selection"""
        clear_screen()
        
        print(colorize("=" * 60, Colors.BRIGHT_CYAN))
        print(colorize(f"  {self.title.upper()}  ", Colors.BRIGHT_CYAN + Colors.BOLD))
        print(colorize("=" * 60, Colors.BRIGHT_CYAN))
        
        if self.description:
            print(f"\n{colorize(self.description, Colors.WHITE)}")
        
        if context:
            self._display_context(context)
        
        print(colorize("\n" + "-" * 60, Colors.BRIGHT_CYAN))
        
        for item in self.items:
            if item.key == "":
                print(colorize("  " + "-" * 56, Colors.GRAY))
                continue
            
            if not item.enabled:
                print(f"  {colorize(item.key + '.', Colors.GRAY)} {colorize(item.label, Colors.GRAY)}")
                continue
            
            label = item.label
            if item.badge:
                label = f"{label} {colorize(f'({item.badge})', Colors.BRIGHT_YELLOW)}"
            
            key_color = Colors.BRIGHT_GREEN if not item.is_submenu() else Colors.BRIGHT_CYAN
            label_color = Colors.WHITE if not item.is_submenu() else Colors.BRIGHT_CYAN
            arrow = " →" if item.is_submenu() else ""
            
            print(f"  {colorize(item.key + '.', key_color)} {colorize(label + arrow, label_color)}")
        
        print(colorize("-" * 60, Colors.BRIGHT_CYAN))
        
        choice = input(f"\n{colorize('Choice:', Colors.BRIGHT_CYAN)} ").strip()
        return choice
    
    def _display_context(self, context: dict):
        """Display player stats context"""
        if 'player' in context:
            player = context['player']
            print(f"\n{colorize('Player:', Colors.BRIGHT_WHITE + Colors.BOLD)} {player.name}")
            print(f"  {colorize('Level:', Colors.WHITE)} {colorize(str(player.level), Colors.BRIGHT_GREEN)} | " +
                  f"{colorize('Gold:', Colors.YELLOW)} {colorize(str(player.gold), Colors.BRIGHT_YELLOW)} | " +
                  f"{colorize('HP:', Colors.RED)} {colorize(f'{player.hp}/{player.max_hp}', Colors.BRIGHT_RED)}")
        
        if 'location' in context:
            location = context['location']
            print(f"  {colorize('Location:', Colors.WHITE)} {colorize(location, Colors.BRIGHT_CYAN)}")


class MenuBuilder:
    """Menu builder"""
    
    @staticmethod
    def create_main_menu(player) -> Menu:
        """Create Eslania City menu"""
        menu = Menu("Eslania City", "A grand city with guilds, shops, and access to dangerous dungeons")
        
        # Exploration & Travel
        menu.add_item(MenuItem("1", "Explore & Travel", submenu=MenuBuilder._create_explore_menu()))
        
        # Character management
        badge = f"{player.stat_points} points" if player.stat_points > 0 else None
        menu.add_item(MenuItem("2", "Character", badge=badge, submenu=MenuBuilder._create_character_menu(player)))
        
        # Town services (guilds, shops, services)
        menu.add_item(MenuItem("3", "Town Services", submenu=MenuBuilder._create_town_services_menu()))
        
        menu.add_separator()
        
        # Save & Quit section
        menu.add_item(MenuItem("4", "Save Game"))
        menu.add_item(MenuItem("5", "Quit Game"))
        
        return menu
    
    @staticmethod
    def _create_explore_menu() -> Menu:
        """Create exploration submenu"""
        menu = Menu("Explore & Travel", "Dungeons, activities, and travel")
        
        # Dungeons
        menu.add_item(MenuItem("1", "Underground Waterways"))
        menu.add_item(MenuItem("2", "Eslania Dungeon"))
        
        menu.add_separator()
        
        # Activities
        menu.add_item(MenuItem("3", "Go Fishing"))
        menu.add_item(MenuItem("4", "Go Mining"))
        
        menu.add_separator()
        
        # Travel
        menu.add_item(MenuItem("5", "Travel to Another Location"))
        
        menu.add_separator()
        
        menu.add_item(MenuItem("0", "Back to Main Menu"))
        
        return menu
    
    @staticmethod
    def _create_character_menu(player) -> Menu:
        """Create character management submenu"""
        menu = Menu("Character", "Manage your character")
        
        menu.add_item(MenuItem("1", "View Stats"))
        menu.add_item(MenuItem("2", "View Inventory"))
        
        achievement_count = len([a for a in player.achievements if a])
        badge = f"{achievement_count} unlocked" if achievement_count > 0 else None
        menu.add_item(MenuItem("3", "View Achievements", badge=badge))
        
        if player.stat_points > 0:
            menu.add_item(MenuItem("4", "Allocate Stat Points", badge=f"{player.stat_points} available"))
        
        menu.add_separator()
        
        menu.add_item(MenuItem("0", "Back to Main Menu"))
        
        return menu
    
    @staticmethod
    def _create_town_services_menu() -> Menu:
        """Create town services submenu"""
        menu = Menu("Town Services", "Visit guilds, shops, and services")
        
        # Direct access to categories
        menu.add_item(MenuItem("1", "Guilds", submenu=MenuBuilder._create_guilds_menu()))
        menu.add_item(MenuItem("2", "Shops", submenu=MenuBuilder._create_shops_menu()))
        menu.add_item(MenuItem("3", "Services", submenu=MenuBuilder._create_services_menu()))
        
        menu.add_separator()
        
        menu.add_item(MenuItem("0", "Back to Main Menu"))
        
        return menu
    
    @staticmethod
    def _create_guilds_menu() -> Menu:
        """Create guilds submenu"""
        menu = Menu("Guilds", "Visit warrior, soldier, and cleric guilds")
        
        menu.add_item(MenuItem("1", "Knight Guild"))
        menu.add_item(MenuItem("2", "Army Guild"))
        menu.add_item(MenuItem("3", "Cleric Guild"))
        
        menu.add_separator()
        
        menu.add_item(MenuItem("0", "Back"))
        
        return menu
    
    @staticmethod
    def _create_shops_menu() -> Menu:
        """Create shops submenu"""
        menu = Menu("Shops", "Buy and sell items")
        
        menu.add_item(MenuItem("1", "General Store"))
        menu.add_item(MenuItem("2", "Fishing Store"))
        menu.add_item(MenuItem("3", "Mining Store"))
        
        menu.add_separator()
        
        menu.add_item(MenuItem("0", "Back"))
        
        return menu
    
    @staticmethod
    def _create_services_menu() -> Menu:
        """Create services submenu"""
        menu = Menu("Services", "Healing, training, and other services")
        
        menu.add_item(MenuItem("1", "Hospital"))
        menu.add_item(MenuItem("2", "Pimping Service"))
        menu.add_item(MenuItem("3", "Training Zone"))
        menu.add_item(MenuItem("4", "Kitchen"))
        
        menu.add_separator()
        
        menu.add_item(MenuItem("0", "Back"))
        
        return menu

