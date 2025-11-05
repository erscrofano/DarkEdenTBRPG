"""Caching utilities"""
from functools import lru_cache
from typing import Callable, Any


class CalculationCache:
    """Cache manager for calculations"""
    _cache_size = 128
    
    @classmethod
    def cached(cls, maxsize: int = None):
        """Cache decorator"""
        cache_size = maxsize if maxsize is not None else cls._cache_size
        return lru_cache(maxsize=cache_size)
    
    @classmethod
    def clear_all(cls):
        """Clear all caches"""
        pass


@CalculationCache.cached(maxsize=256)
def calculate_damage(base_damage: int, str_stat: int, dex_stat: int) -> int:
    """Calculate damage with caching"""
    from ..constants import BASE_DAMAGE, STR_DAMAGE_MULTIPLIER
    damage = base_damage + (str_stat * STR_DAMAGE_MULTIPLIER)
    return damage


@CalculationCache.cached(maxsize=128)
def calculate_stat_derived_values(base_hp: int, str_stat: int, dex_stat: int, agl_stat: int) -> dict:
    """Calculate derived stats with caching"""
    from ..constants import HP_PER_STAT_POINT, STARTING_ATTACK, STARTING_DEFENSE
    
    max_hp = base_hp * HP_PER_STAT_POINT
    attack = STARTING_ATTACK
    defense = STARTING_DEFENSE
    
    return {'max_hp': max_hp, 'attack': attack, 'defense': defense}


@CalculationCache.cached(maxsize=64)
def calculate_dodge_chance(agl_stat: int, is_boss: bool = False) -> float:
    """Calculate dodge chance with caching"""
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

