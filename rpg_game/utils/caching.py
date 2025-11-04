"""Caching utilities for repeated calculations"""
from functools import lru_cache
from typing import Callable, Any


class CalculationCache:
    """
    Cache manager for expensive calculations.
    Provides cache invalidation and manual clearing.
    """
    _cache_size = 128  # Default cache size
    
    @classmethod
    def cached(cls, maxsize: int = None):
        """
        Decorator for caching function results.
        
        Args:
            maxsize: Maximum cache size (default: 128)
        """
        cache_size = maxsize if maxsize is not None else cls._cache_size
        return lru_cache(maxsize=cache_size)
    
    @classmethod
    def clear_all(cls):
        """Clear all function caches"""
        # This is a bit tricky - we'd need to track all cached functions
        # For now, users can call function.cache_clear() directly
        pass


# Cached functions for common calculations
@CalculationCache.cached(maxsize=256)
def calculate_damage(base_damage: int, str_stat: int, dex_stat: int) -> int:
    """
    Calculate damage with caching.
    This is called frequently in combat.
    """
    from ..constants import BASE_DAMAGE, STR_DAMAGE_MULTIPLIER
    damage = base_damage + (str_stat * STR_DAMAGE_MULTIPLIER)
    # Add DEX-based variance (already handled in combat system, but cache the base)
    return damage


@CalculationCache.cached(maxsize=128)
def calculate_stat_derived_values(base_hp: int, str_stat: int, dex_stat: int, agl_stat: int) -> dict:
    """
    Cache stat-derived calculations.
    Returns dict with max_hp, attack, defense calculations.
    """
    from ..constants import HP_PER_STAT_POINT, STARTING_ATTACK, STARTING_DEFENSE
    
    max_hp = base_hp * HP_PER_STAT_POINT
    # Attack and defense calculations (simplified - actual values depend on equipment)
    attack = STARTING_ATTACK  # Base attack, equipment adds to this
    defense = STARTING_DEFENSE  # Base defense, equipment adds to this
    
    return {
        'max_hp': max_hp,
        'attack': attack,
        'defense': defense
    }


@CalculationCache.cached(maxsize=64)
def calculate_dodge_chance(agl_stat: int, is_boss: bool = False) -> float:
    """
    Cache dodge chance calculation.
    """
    from ..constants import DODGE_CAP, DODGE_CALCULATION_DIVISOR, BOSS_ACCURACY_FLOOR
    
    base_dodge = min(DODGE_CAP, agl_stat / DODGE_CALCULATION_DIVISOR)
    accuracy_floor = BOSS_ACCURACY_FLOOR if is_boss else 0.0
    dodge_chance = min(base_dodge, 1.0 - accuracy_floor)
    return dodge_chance


def clear_caches():
    """Clear all calculation caches"""
    calculate_damage.cache_clear()
    calculate_stat_derived_values.cache_clear()
    calculate_dodge_chance.cache_clear()

