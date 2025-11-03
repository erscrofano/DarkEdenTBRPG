"""Player model class"""
from ..config import SAVE_SCHEMA_VERSION
from ..ui import Colors, colorize, health_bar, skill_xp_bar
from ..save.system import save_game


class Player:
    def __init__(self, name):
        self.name = name
        self.level = 1
        self.exp = 0
        self.exp_to_next = 100
        # Base stats
        self.base_hp = 10  # HP stat
        self.str = 10  # Strength - increases max damage
        self.dex = 10  # Dexterity - increases chance for high damage rolls
        self.agl = 10  # Agility - increases dodge chance
        self.stat_points = 0  # Unallocated stat points
        # Derived stats
        self.max_hp = self.base_hp * 10  # Each HP point = 10 max HP
        self.hp = self.max_hp
        self.attack = 10
        self.defense = 5
        self.gold = 50
        self.inventory = []
        # Give starter weapon (G0 Training Sword)
        from ..items.definitions import SWORDS
        self.weapon = SWORDS['g0'].copy()
        self.armor = None
        # Tracking stats (Kal Online / OSRS inspired)
        self.kill_streak = 0
        self.total_kills = 0
        self.highest_level_enemy = 0
        self.highest_tower_floor = 0  # Track highest tower floor reached
        self.achievements = []
        # Skills
        self.fishing_level = 1
        self.fishing_exp = 0
        self.fishing_exp_to_next = 100
        self.cooking_level = 1
        self.cooking_exp = 0
        self.cooking_exp_to_next = 100
        self.mining_level = 1
        self.mining_exp = 0
        self.mining_exp_to_next = 100
        # Location tracking
        self.current_location = 'eslania_city'
        
    def to_dict(self):
        """Convert player to dictionary for saving"""
        return {
            'name': self.name,
            'level': self.level,
            'exp': self.exp,
            'exp_to_next': self.exp_to_next,
            'base_hp': self.base_hp,
            'str': self.str,
            'dex': self.dex,
            'agl': self.agl,
            'stat_points': self.stat_points,
            'max_hp': self.max_hp,
            'hp': self.hp,
            'attack': self.attack,
            'defense': self.defense,
            'gold': self.gold,
            'inventory': self.inventory,
            'weapon': self.weapon,
            'armor': self.armor,
            'kill_streak': getattr(self, 'kill_streak', 0),
            'total_kills': getattr(self, 'total_kills', 0),
            'highest_level_enemy': getattr(self, 'highest_level_enemy', 0),
            'highest_tower_floor': getattr(self, 'highest_tower_floor', 0),
            'achievements': getattr(self, 'achievements', []),
            'schema': SAVE_SCHEMA_VERSION,
            'fishing_level': getattr(self, 'fishing_level', 1),
            'fishing_exp': getattr(self, 'fishing_exp', 0),
            'fishing_exp_to_next': getattr(self, 'fishing_exp_to_next', 100),
            'cooking_level': getattr(self, 'cooking_level', 1),
            'cooking_exp': getattr(self, 'cooking_exp', 0),
            'cooking_exp_to_next': getattr(self, 'cooking_exp_to_next', 100),
            'mining_level': getattr(self, 'mining_level', 1),
            'mining_exp': getattr(self, 'mining_exp', 0),
            'mining_exp_to_next': getattr(self, 'mining_exp_to_next', 100),
            'current_location': getattr(self, 'current_location', 'eslania_city')
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create player from dictionary"""
        from ..save.system import save_game  # Import here to avoid circular dependency
        
        # Ensure name is loaded correctly - use 'name' field, fallback to 'Hero' if missing
        player_name = data.get('name', 'Hero')
        if not player_name or player_name.strip() == '':
            player_name = 'Hero'
        player = cls(player_name)
        player.level = data['level']
        player.exp = data['exp']
        player.exp_to_next = data['exp_to_next']
        # Load stats (with defaults for old save files)
        player.base_hp = data.get('base_hp', 10)
        player.str = data.get('str', 10)
        player.dex = data.get('dex', 10)
        player.agl = data.get('agl', 10)
        player.stat_points = data.get('stat_points', 0)
        # Update derived stats
        player.max_hp = player.base_hp * 10
        player.hp = min(data.get('hp', player.max_hp), player.max_hp)
        player.attack = data.get('attack', 10)
        player.defense = data.get('defense', 5)
        player.gold = data['gold']
        player.inventory = data['inventory']
        # Ensure all items have quantity field for backwards compatibility
        for item in player.inventory:
            if 'quantity' not in item:
                item['quantity'] = 1
        player.weapon = data.get('weapon')  # Use get() with default None if missing
        player.armor = data.get('armor')  # Use get() with default None if missing
        # Ensure new players have starter weapon
        if not player.weapon:
            # Use G0 Training Sword as starter weapon
            from ..items.definitions import SWORDS
            player.weapon = SWORDS['g0'].copy()
        # Load tracking stats
        player.kill_streak = data.get('kill_streak', 0)
        player.total_kills = data.get('total_kills', 0)
        player.highest_level_enemy = data.get('highest_level_enemy', 0)
        player.highest_tower_floor = data.get('highest_tower_floor', 0)
        player.achievements = data.get('achievements', [])
        
        # Load skills (with defaults for old save files)
        schema_version = data.get('schema', 1)
        if schema_version < SAVE_SCHEMA_VERSION:
            # Migration: set defaults for new skill fields
            player.fishing_level = 1
            player.fishing_exp = 0
            player.fishing_exp_to_next = 100
            player.cooking_level = 1
            player.cooking_exp = 0
            player.cooking_exp_to_next = 100
            player.mining_level = 1
            player.mining_exp = 0
            player.mining_exp_to_next = 100
            # Auto-resave with new schema
            try:
                save_game(player)
            except Exception as e:
                # Log error but don't fail loading
                from ..utils.logging import log_warning
                log_warning(f"Failed to auto-resave player after migration: {e}")
        else:
            player.fishing_level = data.get('fishing_level', 1)
            player.fishing_exp = data.get('fishing_exp', 0)
            player.fishing_exp_to_next = data.get('fishing_exp_to_next', 100)
            player.cooking_level = data.get('cooking_level', 1)
            player.cooking_exp = data.get('cooking_exp', 0)
            player.cooking_exp_to_next = data.get('cooking_exp_to_next', 100)
            player.mining_level = data.get('mining_level', 1)
            player.mining_exp = data.get('mining_exp', 0)
            player.mining_exp_to_next = data.get('mining_exp_to_next', 100)
        
        # Load location (default to eslania_city for backwards compatibility)
        player.current_location = data.get('current_location', 'eslania_city')
        # Handle legacy 'town' location
        if player.current_location == 'town':
            player.current_location = 'eslania_city'
        
        return player
        
    def calculate_max_hp(self):
        """Recalculate max HP based on base_hp stat and talisman bonuses"""
        old_max = self.max_hp if hasattr(self, 'max_hp') else 0
        self.max_hp = self.base_hp * 10
        # Add HP bonus from armor talisman if present
        if self.armor and 'talisman_bonuses' in self.armor:
            bonuses = self.armor['talisman_bonuses']
            self.max_hp += bonuses.get('bonus_hp', 0) * 10  # Each HP point = 10 max HP
        # If max HP increased, increase current HP proportionally
        if old_max > 0 and self.max_hp > old_max:
            hp_percentage = self.hp / old_max
            self.hp = int(self.hp + (self.max_hp - old_max) * hp_percentage)
        # Ensure current HP doesn't exceed new max
        if self.hp > self.max_hp:
            self.hp = self.max_hp
        # Ensure HP is never negative
        if self.hp < 0:
            self.hp = 0
    
    def get_effective_str(self):
        """Get effective STR including talisman bonuses"""
        str_bonus = 0
        if self.weapon and 'talisman_bonuses' in self.weapon:
            str_bonus += self.weapon['talisman_bonuses'].get('bonus_str', 0)
        if self.armor and 'talisman_bonuses' in self.armor:
            str_bonus += self.armor['talisman_bonuses'].get('bonus_str', 0)
        return self.str + str_bonus
    
    def get_effective_dex(self):
        """Get effective DEX including talisman bonuses"""
        dex_bonus = 0
        if self.weapon and 'talisman_bonuses' in self.weapon:
            dex_bonus += self.weapon['talisman_bonuses'].get('bonus_dex', 0)
        if self.armor and 'talisman_bonuses' in self.armor:
            dex_bonus += self.armor['talisman_bonuses'].get('bonus_dex', 0)
        return self.dex + dex_bonus
    
    def get_effective_agl(self):
        """Get effective AGL including talisman bonuses"""
        agl_bonus = 0
        if self.weapon and 'talisman_bonuses' in self.weapon:
            agl_bonus += self.weapon['talisman_bonuses'].get('bonus_agl', 0)
        if self.armor and 'talisman_bonuses' in self.armor:
            agl_bonus += self.armor['talisman_bonuses'].get('bonus_agl', 0)
        return self.agl + agl_bonus
    
    def level_up(self, silent=False):
        """Level up and give stat points. If silent=True, stat points are banked without prompting."""
        if self.exp >= self.exp_to_next:
            self.level += 1
            self.exp -= self.exp_to_next
            self.exp_to_next = int(self.exp_to_next * 1.5)
            self.stat_points += 5  # Give 5 stat points per level
            # Auto-heal on level up
            self.calculate_max_hp()
            self.hp = self.max_hp
            if not silent:
                print(f"\n{colorize('🌟', Colors.BRIGHT_YELLOW)} {colorize(f'{self.name} LEVELED UP!', Colors.BRIGHT_GREEN + Colors.BOLD)} {colorize('🌟', Colors.BRIGHT_YELLOW)}")
                print(f"{colorize('You are now level', Colors.WHITE)} {colorize(str(self.level), Colors.BRIGHT_CYAN + Colors.BOLD)}!")
                print(f"{colorize('✨', Colors.BRIGHT_YELLOW)} {colorize('You gained 5 stat points to allocate!', Colors.BRIGHT_GREEN)}")
                input("\nPress Enter to allocate stats...")
            return True
        return False
            
    def get_max_attack_power(self):
        """Calculate maximum attack power based on STR and talisman bonuses"""
        effective_str = self.get_effective_str()
        base = 5 + (effective_str * 0.5)  # Base damage scales with STR
        if self.weapon:
            base += self.weapon['attack']
        return int(base)
    
    def get_attack_power(self):
        """Legacy method for compatibility"""
        return self.get_max_attack_power()
    
    def get_defense_power(self):
        base = self.defense
        if self.armor:
            base += self.armor['defense']
            # Add defense bonus from talisman if present
            if 'talisman_bonuses' in self.armor:
                base += self.armor['talisman_bonuses'].get('bonus_defense', 0)
        return base
    
    def take_damage(self, damage):
        """
        Apply damage to player, reducing by defense.
        
        DAMAGE FLOW DOCUMENTATION:
        - This is the SINGLE point where player defense is applied.
        - Upstream code should pass RAW damage (before defense).
        - Defense reduces damage, minimum 1 damage always dealt.
        - Returns actual damage taken for display purposes.
        """
        actual_damage = max(1, damage - self.get_defense_power())
        self.hp -= actual_damage
        if self.hp < 0:
            self.hp = 0
        return actual_damage
    
    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)
    
    def is_alive(self):
        return self.hp > 0
    
    def get_stats(self):
        name_str = f"{colorize('Name:', Colors.CYAN)} {colorize(self.name, Colors.BRIGHT_CYAN + Colors.BOLD)}"
        level_str = f"{colorize('Level:', Colors.CYAN)} {colorize(str(self.level), Colors.BRIGHT_GREEN)}"
        exp_str = f"{colorize('Experience:', Colors.CYAN)} {colorize(str(self.exp), Colors.WHITE)}/{colorize(str(self.exp_to_next), Colors.WHITE)}"
        hp_str = f"{colorize('HP:', Colors.BRIGHT_RED)} {health_bar(self.hp, self.max_hp)}"
        stat_points_str = f"{colorize('Stat Points:', Colors.BRIGHT_YELLOW)} {colorize(str(self.stat_points), Colors.BRIGHT_YELLOW + Colors.BOLD)}" if self.stat_points > 0 else ""
        str_str = f"{colorize('STR', Colors.BRIGHT_RED)} {colorize('(Strength):', Colors.WHITE)} {colorize(str(self.str), Colors.BRIGHT_RED)}"
        dex_str = f"{colorize('DEX', Colors.BRIGHT_GREEN)} {colorize('(Dexterity):', Colors.WHITE)} {colorize(str(self.dex), Colors.BRIGHT_GREEN)}"
        agl_str = f"{colorize('AGL', Colors.BRIGHT_BLUE)} {colorize('(Agility):', Colors.WHITE)} {colorize(str(self.agl), Colors.BRIGHT_BLUE)}"
        hp_stat_str = f"{colorize('HP Stat:', Colors.MAGENTA)} {colorize(str(self.base_hp), Colors.BRIGHT_MAGENTA)}"
        attack_str = f"{colorize('Max Attack:', Colors.YELLOW)} {colorize(str(self.get_max_attack_power()), Colors.BRIGHT_YELLOW)}"
        defense_str = f"{colorize('Defense:', Colors.BLUE)} {colorize(str(self.get_defense_power()), Colors.BRIGHT_BLUE)}"
        gold_str = f"{colorize('Gold:', Colors.BRIGHT_YELLOW)} {colorize(str(self.gold), Colors.BRIGHT_YELLOW)}"
        
        # Tracking stats (Kal Online/OSRS inspired)
        kills_str = f"{colorize('Total Kills:', Colors.CYAN)} {colorize(str(self.total_kills), Colors.WHITE)}"
        streak_str = f"{colorize('Kill Streak:', Colors.BRIGHT_RED)} {colorize(str(self.kill_streak), Colors.BRIGHT_RED + Colors.BOLD)}" if self.kill_streak > 0 else ""
        achievements_count = f"{colorize('Achievements:', Colors.BRIGHT_MAGENTA)} {colorize(str(len(self.achievements)), Colors.BRIGHT_MAGENTA)}"
        
        # Skills section
        fishing_level = getattr(self, 'fishing_level', 1)
        fishing_exp = getattr(self, 'fishing_exp', 0)
        fishing_exp_to_next = getattr(self, 'fishing_exp_to_next', 100)
        cooking_level = getattr(self, 'cooking_level', 1)
        cooking_exp = getattr(self, 'cooking_exp', 0)
        cooking_exp_to_next = getattr(self, 'cooking_exp_to_next', 100)
        
        mining_level = getattr(self, 'mining_level', 1)
        mining_exp = getattr(self, 'mining_exp', 0)
        mining_exp_to_next = getattr(self, 'mining_exp_to_next', 100)
        
        fishing_str = f"{colorize('Fishing:', Colors.BRIGHT_CYAN)} {colorize(f'Level {fishing_level}', Colors.BRIGHT_GREEN)} | {colorize(f'XP: {fishing_exp}/{fishing_exp_to_next}', Colors.WHITE)}"
        fishing_bar = f"{colorize('Fishing XP:', Colors.CYAN)} {skill_xp_bar(fishing_exp, fishing_exp_to_next, width=20)}"
        cooking_str = f"{colorize('Cooking:', Colors.BRIGHT_MAGENTA)} {colorize(f'Level {cooking_level}', Colors.BRIGHT_GREEN)} | {colorize(f'XP: {cooking_exp}/{cooking_exp_to_next}', Colors.WHITE)}"
        cooking_bar = f"{colorize('Cooking XP:', Colors.MAGENTA)} {skill_xp_bar(cooking_exp, cooking_exp_to_next, width=20)}"
        mining_str = f"{colorize('Mining:', Colors.BRIGHT_MAGENTA)} {colorize(f'Level {mining_level}', Colors.BRIGHT_GREEN)} | {colorize(f'XP: {mining_exp}/{mining_exp_to_next}', Colors.WHITE)}"
        mining_bar = f"{colorize('Mining XP:', Colors.MAGENTA)} {skill_xp_bar(mining_exp, mining_exp_to_next, width=20)}"
        
        lines = [
            colorize("=" * 50, Colors.CYAN),
            colorize("         CHARACTER STATS", Colors.BRIGHT_CYAN + Colors.BOLD),
            colorize("=" * 50, Colors.CYAN),
            name_str,
            level_str,
            exp_str,
            "",
            colorize("ATTRIBUTES:", Colors.BRIGHT_WHITE + Colors.BOLD),
            str_str,
            dex_str,
            agl_str,
            hp_stat_str,
            "",
            stat_points_str if stat_points_str else "",
            colorize("COMBAT STATS:", Colors.BRIGHT_WHITE + Colors.BOLD),
            hp_str,
            attack_str,
            defense_str,
            "",
            colorize("SKILLS:", Colors.BRIGHT_WHITE + Colors.BOLD),
            fishing_str,
            fishing_bar,
            cooking_str,
            cooking_bar,
            mining_str,
            mining_bar,
            "",
            colorize("TRACKING:", Colors.BRIGHT_WHITE + Colors.BOLD),
            gold_str,
            kills_str,
            streak_str if streak_str else "",
            achievements_count,
            colorize("=" * 50, Colors.CYAN)
        ]
        return "\n".join([line for line in lines if line])  # Remove empty strings

