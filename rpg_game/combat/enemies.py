"""Enemy templates"""
# Common talisman drops (1.0% for most talismans)
COMMON_TALISMANS = [
    'talisman_strength', 'talisman_accuracy', 'talisman_health', 
    'talisman_defense', 'talisman_agility', 'talisman_intensification', 
    'talisman_insanity', 'talisman_heroic'
]

def get_all_talisman_drops():
    """Get all talisman drops with their drop rates"""
    drops = []
    # Common talismans (1.0% each)
    for talisman in COMMON_TALISMANS:
        drops.append({'item': talisman, 'chance': 0.01})
    # Rare talismans
    drops.append({'item': 'talisman_infinity', 'chance': 0.005})  # 0.5%
    drops.append({'item': 'talisman_hacker', 'chance': 0.0001})   # 0.01%
    return drops

BASE_ENEMIES = [
    # Tier 1 - Beginner (Level 1)
    # HP kept as provided, attack/defense balanced for level 1 players
    # Expected: 3-5 hits to kill, enemy deals 3-8 damage per hit
    {'name': 'Turning Dead', 'base_hp': 30, 'base_attack': 10, 'base_defense': 1, 'base_exp': 20, 'base_gold': 15, 'tier': 1, 'drops': [
        {'item': 'head_turning_dead', 'chance': 1.0},  # Guaranteed
        {'item': 'bone', 'chance': 0.7},
        {'item': 'healing_herb', 'chance': 0.4},
        {'item': 'soul_fragment', 'chance': 0.3}
    ]},
    {'name': 'Turning Soul', 'base_hp': 40, 'base_attack': 12, 'base_defense': 1, 'base_exp': 25, 'base_gold': 18, 'tier': 1, 'drops': [
        {'item': 'head_turning_soul', 'chance': 1.0},  # Guaranteed
        {'item': 'cursed_bone', 'chance': 0.5},
        {'item': 'healing_herb', 'chance': 0.35},
        {'item': 'shadow_essence', 'chance': 0.3}
    ]},
    {'name': 'Kid', 'base_hp': 60, 'base_attack': 14, 'base_defense': 2, 'base_exp': 30, 'base_gold': 22, 'tier': 1, 'drops': [
        {'item': 'head_kid', 'chance': 1.0},  # Guaranteed
        {'item': 'healing_herb', 'chance': 0.5},
        {'item': 'bandit_coin', 'chance': 0.3},
        {'item': 'iron_ore', 'chance': 0.35}
    ]},
    
    # Tier 2 - Early Game (Level 5-15)
    # HP kept as provided, balanced for level 5-10 players
    {'name': 'Soldier', 'base_hp': 82, 'base_attack': 18, 'base_defense': 3, 'base_exp': 50, 'base_gold': 35, 'tier': 2, 'drops': [
        {'item': 'head_soldier', 'chance': 1.0},  # Guaranteed
        {'item': 'bandit_mask', 'chance': 0.6},
        {'item': 'soldier_emblem', 'chance': 0.5},
        {'item': 'iron_ore', 'chance': 0.4},
        {'item': 'healing_herb', 'chance': 0.3}
    ]},
    {'name': 'Captain', 'base_hp': 105, 'base_attack': 20, 'base_defense': 4, 'base_exp': 65, 'base_gold': 50, 'tier': 2, 'drops': [
        {'item': 'head_captain', 'chance': 1.0},  # Guaranteed
        {'item': 'soldier_emblem', 'chance': 0.7},
        {'item': 'bandit_coin', 'chance': 0.5},
        {'item': 'silver_ore', 'chance': 0.4},
        {'item': 'crystal_shard', 'chance': 0.25}
    ]},
    {'name': 'Arkhan', 'base_hp': 86, 'base_attack': 19, 'base_defense': 3, 'base_exp': 55, 'base_gold': 40, 'tier': 2, 'drops': [
        {'item': 'head_arkhan', 'chance': 1.0},  # Guaranteed
        {'item': 'cursed_bone', 'chance': 0.6},
        {'item': 'shadow_essence', 'chance': 0.4},
        {'item': 'soul_fragment', 'chance': 0.35}
    ]},
    {'name': 'Iron Teeth', 'base_hp': 129, 'base_attack': 22, 'base_defense': 5, 'base_exp': 75, 'base_gold': 60, 'tier': 2, 'drops': [
        {'item': 'head_iron_teeth', 'chance': 1.0},  # Guaranteed
        {'item': 'orc_tusk', 'chance': 0.7},
        {'item': 'iron_ore', 'chance': 0.6},
        {'item': 'silver_ore', 'chance': 0.4},
        {'item': 'crystal_shard', 'chance': 0.3}
    ]},
    
    # Tier 3 - Mid Game (Level 18-30)
    # HP kept as provided, balanced for level 15-25 players
    {'name': 'Red Eye', 'base_hp': 65, 'base_attack': 26, 'base_defense': 4, 'base_exp': 85, 'base_gold': 70, 'tier': 3, 'drops': [
        {'item': 'head_red_eye', 'chance': 1.0},  # Guaranteed
        {'item': 'cursed_bone', 'chance': 0.65},
        {'item': 'shadow_essence', 'chance': 0.5},
        {'item': 'crystal_shard', 'chance': 0.4},
        {'item': 'soul_fragment', 'chance': 0.3}
    ]},
    {'name': 'Mutant', 'base_hp': 154, 'base_attack': 28, 'base_defense': 6, 'base_exp': 100, 'base_gold': 80, 'tier': 3, 'drops': [
        {'item': 'head_mutant', 'chance': 1.0},  # Guaranteed
        {'item': 'troll_hide', 'chance': 0.6},
        {'item': 'cursed_bone', 'chance': 0.5},
        {'item': 'crystal_shard', 'chance': 0.45},
        {'item': 'blood_essence', 'chance': 0.3}
    ]},
    {'name': 'Moderas', 'base_hp': 89, 'base_attack': 27, 'base_defense': 5, 'base_exp': 95, 'base_gold': 75, 'tier': 3, 'drops': [
        {'item': 'head_moderas', 'chance': 1.0},  # Guaranteed
        {'item': 'shadow_essence', 'chance': 0.6},
        {'item': 'crystal_shard', 'chance': 0.5},
        {'item': 'cursed_bone', 'chance': 0.4},
        {'item': 'mithril_ore', 'chance': 0.25}
    ]},
    {'name': 'Vandalizer', 'base_hp': 124, 'base_attack': 30, 'base_defense': 7, 'base_exp': 115, 'base_gold': 95, 'tier': 3, 'drops': [
        {'item': 'head_vandalizer', 'chance': 1.0},  # Guaranteed
        {'item': 'bandit_mask', 'chance': 0.7},
        {'item': 'bandit_coin', 'chance': 0.6},
        {'item': 'crystal_shard', 'chance': 0.5},
        {'item': 'mithril_ore', 'chance': 0.3}
    ]},
    {'name': 'Dirty Strider', 'base_hp': 114, 'base_attack': 29, 'base_defense': 6, 'base_exp': 110, 'base_gold': 90, 'tier': 3, 'drops': [
        {'item': 'head_dirty_strider', 'chance': 1.0},  # Guaranteed
        {'item': 'troll_hide', 'chance': 0.65},
        {'item': 'shadow_essence', 'chance': 0.5},
        {'item': 'crystal_shard', 'chance': 0.4},
        {'item': 'mithril_ore', 'chance': 0.3}
    ]},
    {'name': 'Estroider', 'base_hp': 207, 'base_attack': 32, 'base_defense': 8, 'base_exp': 130, 'base_gold': 110, 'tier': 3, 'drops': [
        {'item': 'head_estroider', 'chance': 1.0},  # Guaranteed
        {'item': 'troll_hide', 'chance': 0.7},
        {'item': 'crystal_shard', 'chance': 0.6},
        {'item': 'mithril_ore', 'chance': 0.45},
        {'item': 'demon_horn', 'chance': 0.2}
    ]},
    
    # Tier 4 - Late Mid Game (Level 33-50)
    # HP kept as provided, balanced for level 25-40 players
    {'name': 'Widows', 'base_hp': 117, 'base_attack': 34, 'base_defense': 7, 'base_exp': 150, 'base_gold': 120, 'tier': 4, 'drops': [
        {'item': 'head_widows', 'chance': 1.0},  # Guaranteed
        {'item': 'spider_silk', 'chance': 0.8},
        {'item': 'cursed_bone', 'chance': 0.6},
        {'item': 'mithril_ore', 'chance': 0.5},
        {'item': 'crystal_shard', 'chance': 0.45}
    ]},
    {'name': 'Hobble', 'base_hp': 141, 'base_attack': 36, 'base_defense': 8, 'base_exp': 165, 'base_gold': 135, 'tier': 4, 'drops': [
        {'item': 'head_hobble', 'chance': 1.0},  # Guaranteed
        {'item': 'troll_hide', 'chance': 0.7},
        {'item': 'mithril_ore', 'chance': 0.6},
        {'item': 'demon_horn', 'chance': 0.35},
        {'item': 'ancient_relic', 'chance': 0.25}
    ]},
    {'name': 'Big Fang', 'base_hp': 71, 'base_attack': 38, 'base_defense': 6, 'base_exp': 170, 'base_gold': 140, 'tier': 4, 'drops': [
        {'item': 'head_big_fang', 'chance': 1.0},  # Guaranteed
        {'item': 'orc_tusk', 'chance': 0.8},
        {'item': 'mithril_ore', 'chance': 0.55},
        {'item': 'demon_horn', 'chance': 0.4},
        {'item': 'dark_essence', 'chance': 0.3}
    ]},
    {'name': 'Blood Warlock', 'base_hp': 144, 'base_attack': 40, 'base_defense': 9, 'base_exp': 185, 'base_gold': 155, 'tier': 4, 'drops': [
        {'item': 'head_blood_warlock', 'chance': 1.0},  # Guaranteed
        {'item': 'shadow_essence', 'chance': 0.7},
        {'item': 'blood_essence', 'chance': 0.6},
        {'item': 'demon_horn', 'chance': 0.5},
        {'item': 'ancient_relic', 'chance': 0.35}
    ]},
    {'name': 'Golemer', 'base_hp': 319, 'base_attack': 42, 'base_defense': 11, 'base_exp': 200, 'base_gold': 170, 'tier': 4, 'drops': [
        {'item': 'head_golemer', 'chance': 1.0},  # Guaranteed
        {'item': 'ancient_relic', 'chance': 0.5},
        {'item': 'mithril_ore', 'chance': 0.7},
        {'item': 'crystal_shard', 'chance': 0.6},
        {'item': 'energy_crystal', 'chance': 0.4}
    ]},
    {'name': 'Shadow Wing', 'base_hp': 175, 'base_attack': 44, 'base_defense': 10, 'base_exp': 215, 'base_gold': 180, 'tier': 4, 'drops': [
        {'item': 'head_shadow_wing', 'chance': 1.0},  # Guaranteed
        {'item': 'shadow_essence', 'chance': 0.8},
        {'item': 'demon_horn', 'chance': 0.6},
        {'item': 'ancient_relic', 'chance': 0.45},
        {'item': 'dragon_scale', 'chance': 0.2}
    ]},
    
    # Tier 5 - Late Game (Level 55-73)
    # HP kept as provided, balanced for level 40-60 players
    {'name': 'Crimson Slaughter', 'base_hp': 306, 'base_attack': 48, 'base_defense': 12, 'base_exp': 240, 'base_gold': 210, 'tier': 5, 'drops': [
        {'item': 'head_crimson_slaughter', 'chance': 1.0},  # Guaranteed
        {'item': 'demon_horn', 'chance': 0.7},
        {'item': 'blood_essence', 'chance': 0.6},
        {'item': 'dragon_scale', 'chance': 0.4},
        {'item': 'phoenix_feather', 'chance': 0.25}
    ]},
    {'name': 'Ripper', 'base_hp': 258, 'base_attack': 50, 'base_defense': 13, 'base_exp': 255, 'base_gold': 225, 'tier': 5, 'drops': [
        {'item': 'head_ripper', 'chance': 1.0},  # Guaranteed
        {'item': 'demon_horn', 'chance': 0.75},
        {'item': 'dark_essence', 'chance': 0.65},
        {'item': 'dragon_scale', 'chance': 0.45},
        {'item': 'phoenix_feather', 'chance': 0.3}
    ]},
    {'name': 'Hell Wizard', 'base_hp': 263, 'base_attack': 52, 'base_defense': 14, 'base_exp': 270, 'base_gold': 240, 'tier': 5, 'drops': [
        {'item': 'head_hell_wizard', 'chance': 1.0},  # Guaranteed
        {'item': 'shadow_essence', 'chance': 0.75},
        {'item': 'ancient_relic', 'chance': 0.65},
        {'item': 'dragon_scale', 'chance': 0.5},
        {'item': 'star_fragment', 'chance': 0.25}
    ]},
    {'name': 'Dark Screamer', 'base_hp': 213, 'base_attack': 54, 'base_defense': 13, 'base_exp': 285, 'base_gold': 255, 'tier': 5, 'drops': [
        {'item': 'head_dark_screamer', 'chance': 1.0},  # Guaranteed
        {'item': 'cursed_bone', 'chance': 0.8},
        {'item': 'shadow_essence', 'chance': 0.7},
        {'item': 'dragon_scale', 'chance': 0.5},
        {'item': 'phoenix_feather', 'chance': 0.3}
    ]},
    {'name': 'Chaos Guardian', 'base_hp': 405, 'base_attack': 56, 'base_defense': 15, 'base_exp': 300, 'base_gold': 270, 'tier': 5, 'drops': [
        {'item': 'head_chaos_guardian', 'chance': 1.0},  # Guaranteed
        {'item': 'ancient_relic', 'chance': 0.7},
        {'item': 'chaos_essence', 'chance': 0.6},
        {'item': 'dragon_scale', 'chance': 0.5},
        {'item': 'star_fragment', 'chance': 0.3}
    ]},
    {'name': 'Hell Guardian', 'base_hp': 218, 'base_attack': 58, 'base_defense': 14, 'base_exp': 295, 'base_gold': 265, 'tier': 5, 'drops': [
        {'item': 'head_hell_guardian', 'chance': 1.0},  # Guaranteed
        {'item': 'demon_horn', 'chance': 0.75},
        {'item': 'ancient_relic', 'chance': 0.65},
        {'item': 'dragon_scale', 'chance': 0.55},
        {'item': 'star_fragment', 'chance': 0.35}
    ]},
    
    # Tier 6 - End Game (Level 81-95)
    # HP kept as provided, balanced for level 60-90 players
    {'name': 'Lord Chaos', 'base_hp': 506, 'base_attack': 64, 'base_defense': 17, 'base_exp': 360, 'base_gold': 340, 'tier': 6, 'drops': [
        {'item': 'head_lord_chaos', 'chance': 1.0},  # Guaranteed
        {'item': 'chaos_essence', 'chance': 0.8},
        {'item': 'dragon_scale', 'chance': 0.7},
        {'item': 'phoenix_feather', 'chance': 0.6},
        {'item': 'star_fragment', 'chance': 0.5},
        {'item': 'void_crystal', 'chance': 0.3}
    ]},
    {'name': 'Lord Darkness', 'base_hp': 435, 'base_attack': 66, 'base_defense': 18, 'base_exp': 380, 'base_gold': 360, 'tier': 6, 'drops': [
        {'item': 'head_lord_darkness', 'chance': 1.0},  # Guaranteed
        {'item': 'shadow_essence', 'chance': 0.9},
        {'item': 'dark_essence', 'chance': 0.8},
        {'item': 'dragon_scale', 'chance': 0.75},
        {'item': 'star_fragment', 'chance': 0.6},
        {'item': 'void_crystal', 'chance': 0.4}
    ]},
    {'name': 'Dark Guardian', 'base_hp': 718, 'base_attack': 72, 'base_defense': 19, 'base_exp': 450, 'base_gold': 450, 'tier': 6, 'drops': [
        {'item': 'head_dark_guardian', 'chance': 1.0},  # Guaranteed
        {'item': 'dragon_scale', 'chance': 1.0},
        {'item': 'dragon_scale', 'chance': 0.5},
        {'item': 'phoenix_feather', 'chance': 0.7},
        {'item': 'star_fragment', 'chance': 0.65},
        {'item': 'void_crystal', 'chance': 0.5}
    ]}
]

# Add talisman drops to all enemies
for enemy in BASE_ENEMIES:
    enemy['drops'].extend(get_all_talisman_drops())

