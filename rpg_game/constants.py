"""Game constants and configuration values"""

# Travel costs
TRAVEL_COST = 5000  # Cost for non-local travel

# Combat constants
DODGE_CAP = 0.35  # Maximum dodge chance (35%)
BOSS_ACCURACY_FLOOR = 0.10  # Bosses have at least 10% hit chance
RUN_CHANCE = 0.3  # Base chance to successfully run away (70% success)
GUARANTEED_FLEE_GOLD_COST = 0.05  # 5% of gold as escape cost

# Enemy scaling
ENEMY_SCALE_BASE = 1.0
ENEMY_SCALE_MULTIPLIER = 1.2
ENEMY_SCALE_DECAY = 0.85

# Damage calculations
MIN_DAMAGE_RATIO = 0.5  # Minimum damage is 50% of max
CRIT_CHANCE_MAX = 0.25  # Max 25% crit chance
CRIT_DEX_THRESHOLD = 50.0  # DEX needed for max crit (50 DEX)
DEX_PRECISION_INTERVAL = 20  # Every 20 DEX grants precision bonus
DEX_PRECISION_BONUS = 0.05  # +5% per interval
DEX_PRECISION_MAX = 0.25  # Max 25% precision bonus at 100 DEX

# Death mechanics
DEATH_GOLD_LOSS = 0.1  # Lose 10% of gold on death
DEATH_ITEM_PROTECTION = 3  # Keep 3 most valuable items on death

# Input validation
MAX_PLAYER_NAME_LENGTH = 50
MIN_PLAYER_NAME_LENGTH = 1

# Save file
SAVE_DIR_NAME = '.terminal_rpg'
SAVE_FILE_NAME = 'game_save.json'

