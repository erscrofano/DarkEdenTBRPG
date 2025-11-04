"""Game constants and configuration values"""

# ============================================================================
# Player Starting Values
# ============================================================================
STARTING_LEVEL = 1
STARTING_EXP = 0
STARTING_EXP_TO_NEXT = 100
STARTING_BASE_HP = 10
STARTING_STR = 10
STARTING_DEX = 10
STARTING_AGL = 10
STARTING_ATTACK = 10
STARTING_DEFENSE = 5
STARTING_GOLD = 50
STARTING_STAT_POINTS = 0

# HP calculation
HP_PER_STAT_POINT = 10  # Each HP stat point = 10 max HP

# Skill starting values
STARTING_SKILL_LEVEL = 1
STARTING_SKILL_EXP = 0
STARTING_SKILL_EXP_TO_NEXT = 100
MAX_SKILL_LEVEL = 99  # Maximum level for skills

# ============================================================================
# Level Up & Progression
# ============================================================================
STAT_POINTS_PER_LEVEL = 5  # Stat points gained per level up
EXP_MULTIPLIER_PER_LEVEL = 1.5  # Exp required multiplier per level
SKILL_EXP_MULTIPLIER_PER_LEVEL = 1.35  # Skill exp multiplier per level

# ============================================================================
# Combat Constants
# ============================================================================
DODGE_CAP = 0.35  # Maximum dodge chance (35%)
DODGE_CALCULATION_DIVISOR = 100.0  # AGL / this value for dodge calculation
BOSS_ACCURACY_FLOOR = 0.10  # Bosses have at least 10% hit chance
RUN_CHANCE = 0.3  # Base chance to successfully run away (70% success)
GUARANTEED_FLEE_GOLD_COST = 0.05  # 5% of gold as escape cost

# Enemy attack variance
ENEMY_ATTACK_MIN_VARIANCE = -3  # Enemy attack can vary by -3
ENEMY_ATTACK_MAX_VARIANCE = 5   # Enemy attack can vary by +5

# Enemy scaling
ENEMY_SCALE_BASE = 0.9
ENEMY_SCALE_MULTIPLIER = 1.0
ENEMY_SCALE_DECAY = 0.85

# Damage calculations
BASE_DAMAGE = 5  # Base attack damage
STR_DAMAGE_MULTIPLIER = 0.5  # STR * this value = damage bonus
MIN_DAMAGE_RATIO = 0.5  # Minimum damage is 50% of max
MIN_DAMAGE_ALWAYS = 1  # Always deal at least 1 damage

# Critical hit calculations
CRIT_CHANCE_MAX = 0.25  # Max 25% crit chance
CRIT_DEX_THRESHOLD = 50.0  # DEX needed for max crit (50 DEX)
CRIT_DEX_DIVISOR = 200.0  # DEX / this value for crit calculation
CRIT_MULTIPLIER_MIN = 1.5  # Minimum crit multiplier
CRIT_MULTIPLIER_MAX = 2.0  # Maximum crit multiplier

# DEX precision calculations
DEX_PRECISION_INTERVAL = 20  # Every 20 DEX grants precision bonus
DEX_PRECISION_BONUS = 0.05  # +5% per interval
DEX_PRECISION_MAX = 0.25  # Max 25% precision bonus at 100 DEX
DEX_DAMAGE_DIVISOR = 100.0  # DEX / this value for damage bonus calculation
DEX_UPPER_RANGE_RATIO = 0.6  # High DEX hits in upper 60% of damage range

# ============================================================================
# Death Mechanics
# ============================================================================
DEATH_GOLD_LOSS = 0.1  # Lose 10% of gold on death
DEATH_ITEM_PROTECTION = 3  # Keep 3 most valuable items on death
REVIVE_HP = 1  # HP when revived after death

# ============================================================================
# Exploration & Encounters
# ============================================================================
ENCOUNTER_CHANCE = 0.7  # 70% chance of combat encounter
RANDOM_EVENT_CHANCE = 0.05  # 5% chance of random event

# Location multipliers
LOCATION_MULTIPLIER_UNDERGROUND = 1.1
LOCATION_MULTIPLIER_DEFAULT = 1.0

# Random event rewards
RANDOM_EVENT_GOLD_MIN = 50
RANDOM_EVENT_GOLD_MAX = 200
RANDOM_EVENT_EXP_MIN = 20
RANDOM_EVENT_EXP_MAX = 100

# ============================================================================
# Skills System
# ============================================================================
# Fishing
FISHING_LEVEL_BOOST_MULTIPLIER = 0.002  # Level boost per fishing level
FISHING_LEVEL_BOOST_MAX = 0.25  # Maximum level boost
FISHING_RARITY_WEIGHT_DIVISOR = 80.0  # Divisor for rarity weight calculation
FISHING_LOW_TIER_THRESHOLD = 0.55  # Low tier fish threshold
FISHING_RARE_CATCH_CHANCE = 0.05  # 5% chance for rare catch notification

# Cooking
COOKING_SUCCESS_BASE = 0.80  # Base success chance
COOKING_SUCCESS_INCREMENT = 0.01  # Success chance increment per level above requirement
COOKING_SUCCESS_MIN = 0.10  # Minimum success chance (10%)
COOKING_SUCCESS_MAX = 0.95  # Maximum success chance (95%)

# Mining
MINING_LEVEL_BOOST_MULTIPLIER = 0.002  # Level boost per mining level
MINING_LEVEL_BOOST_MAX = 0.25  # Maximum level boost

# ============================================================================
# Travel Costs
# ============================================================================
TRAVEL_COST = 5000  # Cost for non-local travel

# ============================================================================
# UI Thresholds
# ============================================================================
HEALTH_BAR_HEALTHY_THRESHOLD = 0.6  # Above 60% = green
HEALTH_BAR_WOUNDED_THRESHOLD = 0.3  # Above 30% = yellow, below = red

# ============================================================================
# Kill Streak Notifications
# ============================================================================
KILL_STREAK_NOTIFICATION_INTERVAL = 5  # Notify every N kills

# ============================================================================
# Input Validation
# ============================================================================
MAX_PLAYER_NAME_LENGTH = 50
MIN_PLAYER_NAME_LENGTH = 1

# ============================================================================
# Save File
# ============================================================================
SAVE_DIR_NAME = '.terminal_rpg'
SAVE_FILE_NAME = 'game_save.json'
DEFAULT_SAVE_SLOT = 'main'  # Default save slot name
MAX_SAVE_SLOT_NAME_LENGTH = 30  # Maximum length for save slot names

# ============================================================================
# Notification Durations (seconds)
# ============================================================================
NOTIFICATION_DURATION_SHORT = 0.2
NOTIFICATION_DURATION_MEDIUM = 0.5
NOTIFICATION_DURATION_NORMAL = 1.5
NOTIFICATION_DURATION_LONG = 2.0

# ============================================================================
# Shop & Inventory Constants
# ============================================================================
MAX_QUANTITY_PER_PURCHASE = 10  # Maximum items that can be bought at once
MIN_QUANTITY_PER_PURCHASE = 1   # Minimum items that can be bought at once

# ============================================================================
# Developer Menu Constants
# ============================================================================
MAX_DEV_LEVEL = 999              # Maximum level allowed in dev menu

