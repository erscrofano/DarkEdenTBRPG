"""Skill systems"""

from .core import add_skill_xp
from .fishing import (
    FISH_TYPES, FISH_LEVEL_REQUIREMENTS, FISHING_XP_AWARDS, COOKED_FISH_ITEMS,
    get_fishing_catch, go_fishing, get_fish_key_from_name
)
from .mining import (
    MINING_ORES, MINING_LEVEL_REQUIREMENTS, MINING_XP_AWARDS,
    get_mining_catch, go_mining
)
from .cooking import COOK_LEVEL_REQUIREMENTS, COOKING_XP_AWARDS, cook_fish
from .training import training_simulator

__all__ = [
    'add_skill_xp',
    'FISH_TYPES', 'FISH_LEVEL_REQUIREMENTS', 'FISHING_XP_AWARDS', 'COOKED_FISH_ITEMS',
    'get_fishing_catch', 'go_fishing', 'get_fish_key_from_name',
    'MINING_ORES', 'MINING_LEVEL_REQUIREMENTS', 'MINING_XP_AWARDS',
    'get_mining_catch', 'go_mining',
    'COOK_LEVEL_REQUIREMENTS', 'COOKING_XP_AWARDS', 'cook_fish',
    'training_simulator'
]

