"""Item definitions - weapons, armor, potions, and drop items"""

# Grade-based items
# Swords - sold at Knight Guild (Sword Shop)
SWORDS = {
    'g0': {'name': 'G0 Training Sword', 'grade': 0, 'level_req': 1, 'type': 'weapon', 'attack': 2, 'cost': 0, 'sell_value': 1},
    'g10': {'name': 'G10 Light Sword', 'grade': 10, 'level_req': 10, 'type': 'weapon', 'attack': 3, 'cost': 50, 'sell_value': 25},
    'g15': {'name': 'G15 War Sword', 'grade': 15, 'level_req': 15, 'type': 'weapon', 'attack': 6, 'cost': 150, 'sell_value': 75},
    'g20': {'name': 'G20 Broad Sword', 'grade': 20, 'level_req': 20, 'type': 'weapon', 'attack': 10, 'cost': 400, 'sell_value': 200},
    'g25': {'name': 'G25 Bastard Sword', 'grade': 25, 'level_req': 25, 'type': 'weapon', 'attack': 15, 'cost': 1000, 'sell_value': 500},
    'g30': {'name': 'G30 Broad Rapier', 'grade': 30, 'level_req': 30, 'type': 'weapon', 'attack': 22, 'cost': 2500, 'sell_value': 1250},
    'g40': {'name': 'G40 Gothic Sword', 'grade': 40, 'level_req': 40, 'type': 'weapon', 'attack': 32, 'cost': 6000, 'sell_value': 3000},
    'g50': {'name': 'G50 Great Sword', 'grade': 50, 'level_req': 50, 'type': 'weapon', 'attack': 45, 'cost': 15000, 'sell_value': 7500},
    'g60': {'name': 'G60 Sword of Goddess', 'grade': 60, 'level_req': 60, 'type': 'weapon', 'attack': 60, 'cost': 36000, 'sell_value': 18000},
    'g70': {'name': 'G70 Basilisk Sword', 'grade': 70, 'level_req': 70, 'type': 'weapon', 'attack': 80, 'cost': 84000, 'sell_value': 42000},
    'g80': {'name': 'G80 Zweihander', 'grade': 80, 'level_req': 80, 'type': 'weapon', 'attack': 100, 'cost': 192000, 'sell_value': 96000}
}

# Blades - sold at Knight Guild (Blade Shop)
BLADES = {
    'g0': {'name': 'G0 Training Blade', 'grade': 0, 'level_req': 1, 'type': 'weapon', 'attack': 2, 'cost': 0, 'sell_value': 1},
    'g10': {'name': 'G10 Cutlass', 'grade': 10, 'level_req': 10, 'type': 'weapon', 'attack': 3, 'cost': 50, 'sell_value': 25},
    'g15': {'name': 'G15 Long Shamsheer', 'grade': 15, 'level_req': 15, 'type': 'weapon', 'attack': 6, 'cost': 150, 'sell_value': 75},
    'g20': {'name': 'G20 Falchion', 'grade': 20, 'level_req': 20, 'type': 'weapon', 'attack': 10, 'cost': 400, 'sell_value': 200},
    'g25': {'name': 'G25 Severed Blade', 'grade': 25, 'level_req': 25, 'type': 'weapon', 'attack': 15, 'cost': 1000, 'sell_value': 500},
    'g30': {'name': 'G30 Moon Blade', 'grade': 30, 'level_req': 30, 'type': 'weapon', 'attack': 22, 'cost': 2500, 'sell_value': 1250},
    'g40': {'name': 'G40 Savour', 'grade': 40, 'level_req': 40, 'type': 'weapon', 'attack': 32, 'cost': 6000, 'sell_value': 3000},
    'g50': {'name': 'G50 Ring Blade', 'grade': 50, 'level_req': 50, 'type': 'weapon', 'attack': 45, 'cost': 15000, 'sell_value': 7500},
    'g60': {'name': 'G60 Scimitar', 'grade': 60, 'level_req': 60, 'type': 'weapon', 'attack': 60, 'cost': 36000, 'sell_value': 18000},
    'g70': {'name': 'G70 Khopesh', 'grade': 70, 'level_req': 70, 'type': 'weapon', 'attack': 80, 'cost': 84000, 'sell_value': 42000},
    'g80': {'name': 'G80 Katana', 'grade': 80, 'level_req': 80, 'type': 'weapon', 'attack': 100, 'cost': 192000, 'sell_value': 96000}
}

# Legacy WEAPONS dict for backward compatibility (now references SWORDS)
WEAPONS = SWORDS

# Guns - sold at Army Guild
GUNS = {
    'g0': {'name': 'G0 MK-74 "Vicious"', 'grade': 0, 'level_req': 1, 'type': 'weapon', 'attack': 2, 'cost': 0, 'sell_value': 1},
    'g10': {'name': 'G10 MK-101 "GOOSE"', 'grade': 10, 'level_req': 10, 'type': 'weapon', 'attack': 3, 'cost': 50, 'sell_value': 25},
    'g15': {'name': 'G15 P2K "EasyRider"', 'grade': 15, 'level_req': 15, 'type': 'weapon', 'attack': 6, 'cost': 150, 'sell_value': 75},
    'g20': {'name': 'G20 IS-200 "Fury"', 'grade': 20, 'level_req': 20, 'type': 'weapon', 'attack': 10, 'cost': 400, 'sell_value': 200},
    'g25': {'name': 'G25 MK-2002 "Warhammer"', 'grade': 25, 'level_req': 25, 'type': 'weapon', 'attack': 15, 'cost': 1000, 'sell_value': 500},
    'g30': {'name': 'G30 MD-Z "Zeta"', 'grade': 30, 'level_req': 30, 'type': 'weapon', 'attack': 22, 'cost': 2500, 'sell_value': 1250},
    'g40': {'name': 'G40 X-45T "Tomahawk"', 'grade': 40, 'level_req': 40, 'type': 'weapon', 'attack': 32, 'cost': 6000, 'sell_value': 3000},
    'g50': {'name': 'G50 P2K "EasyRider"', 'grade': 50, 'level_req': 50, 'type': 'weapon', 'attack': 45, 'cost': 15000, 'sell_value': 7500},
    'g60': {'name': 'G60 P-38 "SODOM"', 'grade': 60, 'level_req': 60, 'type': 'weapon', 'attack': 60, 'cost': 36000, 'sell_value': 18000},
    'g70': {'name': 'G70 P-40 "El Castle"', 'grade': 70, 'level_req': 70, 'type': 'weapon', 'attack': 80, 'cost': 84000, 'sell_value': 42000},
    'g80': {'name': 'G80 AR-Firebug', 'grade': 80, 'level_req': 80, 'type': 'weapon', 'attack': 100, 'cost': 192000, 'sell_value': 96000},
    'g90': {'name': 'G90 OICW-Flinger', 'grade': 90, 'level_req': 90, 'type': 'weapon', 'attack': 120, 'cost': 400000, 'sell_value': 200000}
}

# Crosses - sold at Cleric Guild (Cross Shop)
CROSSES = {
    'g0': {'name': 'G0 Silver Cross', 'grade': 0, 'level_req': 1, 'type': 'weapon', 'attack': 2, 'cost': 0, 'sell_value': 1},
    'g10': {'name': 'G10 Latin Cross', 'grade': 10, 'level_req': 10, 'type': 'weapon', 'attack': 3, 'cost': 50, 'sell_value': 25},
    'g20': {'name': 'G20 Passion Cross', 'grade': 20, 'level_req': 20, 'type': 'weapon', 'attack': 10, 'cost': 400, 'sell_value': 200},
    'g30': {'name': 'G30 Girisidan Cross', 'grade': 30, 'level_req': 30, 'type': 'weapon', 'attack': 22, 'cost': 2500, 'sell_value': 1250},
    'g40': {'name': 'G40 Episcopal Cross', 'grade': 40, 'level_req': 40, 'type': 'weapon', 'attack': 32, 'cost': 6000, 'sell_value': 3000},
    'g50': {'name': 'G50 Calvaria Cross', 'grade': 50, 'level_req': 50, 'type': 'weapon', 'attack': 45, 'cost': 15000, 'sell_value': 7500},
    'g60': {'name': 'G60 Gloria Cross', 'grade': 60, 'level_req': 60, 'type': 'weapon', 'attack': 60, 'cost': 36000, 'sell_value': 18000},
    'g70': {'name': 'G70 St.Helena Cross', 'grade': 70, 'level_req': 70, 'type': 'weapon', 'attack': 80, 'cost': 84000, 'sell_value': 42000},
    'g80': {'name': 'G80 Papal Cross', 'grade': 80, 'level_req': 80, 'type': 'weapon', 'attack': 100, 'cost': 192000, 'sell_value': 96000}
}

# Maces - sold at Cleric Guild (Mace Shop)
MACES = {
    'g0': {'name': 'G0 Iron Mace', 'grade': 0, 'level_req': 1, 'type': 'weapon', 'attack': 2, 'cost': 0, 'sell_value': 1},
    'g10': {'name': 'G10 Silver Mace', 'grade': 10, 'level_req': 10, 'type': 'weapon', 'attack': 3, 'cost': 50, 'sell_value': 25},
    'g20': {'name': 'G20 Greek Mace', 'grade': 20, 'level_req': 20, 'type': 'weapon', 'attack': 10, 'cost': 400, 'sell_value': 200},
    'g30': {'name': 'G30 Archbishop Mace', 'grade': 30, 'level_req': 30, 'type': 'weapon', 'attack': 22, 'cost': 2500, 'sell_value': 1250},
    'g40': {'name': 'G40 Pontiff Mace', 'grade': 40, 'level_req': 40, 'type': 'weapon', 'attack': 32, 'cost': 6000, 'sell_value': 3000},
    'g50': {'name': 'G50 Cogwheel Mace', 'grade': 50, 'level_req': 50, 'type': 'weapon', 'attack': 45, 'cost': 15000, 'sell_value': 7500},
    'g60': {'name': 'G60 Cephas Mace', 'grade': 60, 'level_req': 60, 'type': 'weapon', 'attack': 60, 'cost': 36000, 'sell_value': 18000},
    'g70': {'name': 'G70 Calix Mace', 'grade': 70, 'level_req': 70, 'type': 'weapon', 'attack': 80, 'cost': 84000, 'sell_value': 42000},
    'g80': {'name': 'G80 Pungo Mace', 'grade': 80, 'level_req': 80, 'type': 'weapon', 'attack': 100, 'cost': 192000, 'sell_value': 96000}
}

# Legacy MAGIC_WEAPONS dict for backward compatibility (now references CROSSES)
MAGIC_WEAPONS = CROSSES

# Armor Sets - one per grade
ARMOR_SETS = {
    'g0': {'name': 'G0 Flak Armor', 'grade': 0, 'type': 'armor', 'defense': 2, 'cost': 0, 'sell_value': 1},
    'g10': {'name': 'G10 Battle Armor', 'grade': 10, 'type': 'armor', 'defense': 3, 'cost': 50, 'sell_value': 25},
    'g20': {'name': 'G20 Combat Armor', 'grade': 20, 'type': 'armor', 'defense': 10, 'cost': 400, 'sell_value': 200},
    'g30': {'name': 'G30 War Armor', 'grade': 30, 'type': 'armor', 'defense': 22, 'cost': 2500, 'sell_value': 1250},
    'g40': {'name': 'G40 Kahraman Armor', 'grade': 40, 'type': 'armor', 'defense': 32, 'cost': 6000, 'sell_value': 3000},
    'g60': {'name': 'G60 R-energetic Armor', 'grade': 60, 'type': 'armor', 'defense': 60, 'cost': 36000, 'sell_value': 18000},
    'g70': {'name': 'G70 Agrippa Armor', 'grade': 70, 'type': 'armor', 'defense': 80, 'cost': 84000, 'sell_value': 42000}
}

# Potions
POTIONS = {
    'health_small': {'name': 'Minor Health Potion', 'type': 'consumable', 'heal': 30, 'cost': 20, 'sell_value': 10},
    'health_medium': {'name': 'Health Potion', 'type': 'consumable', 'heal': 60, 'cost': 50, 'sell_value': 25},
    'health_large': {'name': 'Greater Health Potion', 'type': 'consumable', 'heal': 100, 'cost': 100, 'sell_value': 50}
}

# Fishing Rods - sold at Fishing Store (reduce fishing time)
FISHING_RODS = {
    'fishing_rod': {'name': 'Fishing Rod', 'type': 'tool', 'fishing_speed_boost': -1, 'cost': 2500, 'sell_value': 1250, 'description': 'Speeds up fishing by 1 second'},
    'great_rod': {'name': 'Great Rod', 'type': 'tool', 'fishing_speed_boost': -3, 'cost': 15000, 'sell_value': 7500, 'description': 'Speeds up fishing by 3 seconds'},
    'super_rod': {'name': 'Super Rod', 'type': 'tool', 'fishing_speed_boost': -4, 'cost': 50000, 'sell_value': 25000, 'description': 'Speeds up fishing by 4 seconds'}
}

# Pickaxes - sold at Mining Store (reduce mining time)
PICKAXES = {
    'bronze_pickaxe': {'name': 'Bronze Pickaxe', 'type': 'tool', 'mining_speed_boost': -1, 'cost': 2500, 'sell_value': 1250, 'description': 'Speeds up mining by 1 second'},
    'iron_pickaxe': {'name': 'Iron Pickaxe', 'type': 'tool', 'mining_speed_boost': -2, 'cost': 15000, 'sell_value': 7500, 'description': 'Speeds up mining by 2 seconds'},
    'steel_pickaxe': {'name': 'Steel Pickaxe', 'type': 'tool', 'mining_speed_boost': -3, 'cost': 24000, 'sell_value': 12000, 'description': 'Speeds up mining by 3 seconds'},
    'diamond_pickaxe': {'name': 'Diamond Pickaxe', 'type': 'tool', 'mining_speed_boost': -4, 'cost': 50000, 'sell_value': 25000, 'description': 'Speeds up mining by 4 seconds'}
}

# Drop items that monsters can drop
DROP_ITEMS = {
    # ========================================================================
    # MONSTER HEADS - Guaranteed drops (100% chance)
    # ========================================================================
    # Tier 1 heads (100-120g)
    'head_turning_dead': {'name': 'Turning Dead Head', 'type': 'material', 'sell_value': 100, 'description': 'Skull of a reanimated corpse'},
    'head_turning_soul': {'name': 'Turning Soul Head', 'type': 'material', 'sell_value': 110, 'description': 'Ethereal skull wreathed in dark mist'},
    'head_kid': {'name': 'Kid Head', 'type': 'material', 'sell_value': 120, 'description': 'Head of a young bandit'},
    
    # Tier 2 heads (150-200g)
    'head_soldier': {'name': 'Soldier Head', 'type': 'material', 'sell_value': 150, 'description': 'Head of a corrupted soldier'},
    'head_captain': {'name': 'Captain Head', 'type': 'material', 'sell_value': 170, 'description': 'Head bearing battle scars'},
    'head_arkhan': {'name': 'Arkhan Head', 'type': 'material', 'sell_value': 160, 'description': 'Cursed warrior skull'},
    'head_iron_teeth': {'name': 'Iron Teeth Head', 'type': 'material', 'sell_value': 200, 'description': 'Orc skull with iron-reinforced teeth'},
    
    # Tier 3 heads (250-350g)
    'head_red_eye': {'name': 'Red Eye Head', 'type': 'material', 'sell_value': 250, 'description': 'Skull with glowing red eye sockets'},
    'head_mutant': {'name': 'Mutant Head', 'type': 'material', 'sell_value': 280, 'description': 'Grotesquely deformed skull'},
    'head_moderas': {'name': 'Moderas Head', 'type': 'material', 'sell_value': 270, 'description': 'Dark sorcerer skull'},
    'head_vandalizer': {'name': 'Vandalizer Head', 'type': 'material', 'sell_value': 300, 'description': 'Scarred bandit leader skull'},
    'head_dirty_strider': {'name': 'Dirty Strider Head', 'type': 'material', 'sell_value': 290, 'description': 'Troll skull caked in filth'},
    'head_estroider': {'name': 'Estroider Head', 'type': 'material', 'sell_value': 350, 'description': 'Massive troll skull'},
    
    # Tier 4 heads (400-600g)
    'head_widows': {'name': 'Widows Head', 'type': 'material', 'sell_value': 400, 'description': 'Giant spider head with multiple eyes'},
    'head_hobble': {'name': 'Hobble Head', 'type': 'material', 'sell_value': 450, 'description': 'Twisted goblin chieftain skull'},
    'head_big_fang': {'name': 'Big Fang Head', 'type': 'material', 'sell_value': 470, 'description': 'Skull with massive protruding fangs'},
    'head_blood_warlock': {'name': 'Blood Warlock Head', 'type': 'material', 'sell_value': 500, 'description': 'Crimson-stained sorcerer skull'},
    'head_golemer': {'name': 'Golemer Head', 'type': 'material', 'sell_value': 550, 'description': 'Stone golem core fragment'},
    'head_shadow_wing': {'name': 'Shadow Wing Head', 'type': 'material', 'sell_value': 600, 'description': 'Demonic skull with wing fragments'},
    
    # Tier 5 heads (700-1000g)
    'head_crimson_slaughter': {'name': 'Crimson Slaughter Head', 'type': 'material', 'sell_value': 700, 'description': 'Blood-soaked demon skull'},
    'head_ripper': {'name': 'Ripper Head', 'type': 'material', 'sell_value': 750, 'description': 'Skull with jagged bone protrusions'},
    'head_hell_wizard': {'name': 'Hell Wizard Head', 'type': 'material', 'sell_value': 800, 'description': 'Skull crackling with infernal magic'},
    'head_dark_screamer': {'name': 'Dark Screamer Head', 'type': 'material', 'sell_value': 850, 'description': 'Skull frozen in eternal scream'},
    'head_chaos_guardian': {'name': 'Chaos Guardian Head', 'type': 'material', 'sell_value': 900, 'description': 'Ancient guardian skull'},
    'head_hell_guardian': {'name': 'Hell Guardian Head', 'type': 'material', 'sell_value': 950, 'description': 'Hellforged guardian skull'},
    
    # Tier 6 heads (1200-2000g)
    'head_lord_chaos': {'name': 'Lord Chaos Head', 'type': 'material', 'sell_value': 1200, 'description': 'Skull of a chaos lord'},
    'head_lord_darkness': {'name': 'Lord Darkness Head', 'type': 'material', 'sell_value': 1500, 'description': 'Skull radiating pure darkness'},
    'head_dark_guardian': {'name': 'Dark Guardian Head', 'type': 'material', 'sell_value': 2000, 'description': 'Elite guardian skull wreathed in shadow'},
    
    # ========================================================================
    # COMMON MATERIALS - Low tier drops
    # ========================================================================
    'bone': {'name': 'Bone Fragment', 'type': 'material', 'sell_value': 8, 'description': 'Brittle bone from undead creatures'},
    'cursed_bone': {'name': 'Cursed Bone', 'type': 'material', 'sell_value': 25, 'description': 'Bone infused with dark magic'},
    'healing_herb': {'name': 'Healing Herb', 'type': 'consumable', 'heal': 20, 'sell_value': 8, 'description': 'A medicinal herb from the wilds'},
    'iron_ore': {'name': 'Iron Ore', 'type': 'material', 'sell_value': 750, 'description': 'Raw iron ore for smithing'},
    'silver_ore': {'name': 'Silver Ore', 'type': 'material', 'sell_value': 2500, 'description': 'Precious silver ore'},
    
    # ========================================================================
    # BANDIT DROPS - From humanoid enemies
    # ========================================================================
    'bandit_mask': {'name': 'Bandit Mask', 'type': 'material', 'sell_value': 20, 'description': 'Tattered mask worn by outlaws'},
    'bandit_coin': {'name': 'Bandit Coin', 'type': 'material', 'sell_value': 30, 'description': 'Stolen coins from bandit hoards'},
    'soldier_emblem': {'name': 'Soldier Emblem', 'type': 'material', 'sell_value': 35, 'description': 'Military insignia from fallen soldiers'},
    
    # ========================================================================
    # BEAST DROPS - From creature enemies
    # ========================================================================
    'spider_silk': {'name': 'Spider Silk', 'type': 'material', 'sell_value': 45, 'description': 'Strong silk from giant spiders'},
    'orc_tusk': {'name': 'Orc Tusk', 'type': 'material', 'sell_value': 40, 'description': 'Sharp tusk from orc warriors'},
    'troll_hide': {'name': 'Troll Hide', 'type': 'material', 'sell_value': 55, 'description': 'Incredibly tough troll skin'},
    'demon_horn': {'name': 'Demon Horn', 'type': 'material', 'sell_value': 80, 'description': 'Twisted horn from demonic beings'},
    'demon_wing': {'name': 'Demon Wing', 'type': 'material', 'sell_value': 85, 'description': 'Leathery wing from shadow demons'},
    
    # ========================================================================
    # MAGICAL ESSENCES - From undead and magical creatures
    # ========================================================================
    'shadow_essence': {'name': 'Shadow Essence', 'type': 'material', 'sell_value': 30, 'description': 'Condensed shadow energy'},
    'dark_essence': {'name': 'Dark Essence', 'type': 'material', 'sell_value': 60, 'description': 'Pure darkness made tangible'},
    'blood_essence': {'name': 'Blood Essence', 'type': 'material', 'sell_value': 70, 'description': 'Crystallized lifeblood of the damned'},
    'chaos_essence': {'name': 'Chaos Essence', 'type': 'material', 'sell_value': 100, 'description': 'Unstable energy from chaos beings'},
    'soul_fragment': {'name': 'Soul Fragment', 'type': 'material', 'sell_value': 50, 'description': 'Piece of a corrupted soul'},
    
    # ========================================================================
    # CRYSTALS & GEMS - Magical crafting materials
    # ========================================================================
    'crystal_shard': {'name': 'Crystal Shard', 'type': 'material', 'sell_value': 35, 'description': 'Fragment of a magical crystal'},
    'mithril_ore': {'name': 'Mithril Ore', 'type': 'material', 'sell_value': 65, 'description': 'Legendary silver-blue metal'},
    'ancient_relic': {'name': 'Ancient Relic', 'type': 'material', 'sell_value': 90, 'description': 'Artifact from a forgotten age'},
    'ethereal_gem': {'name': 'Ethereal Gem', 'type': 'material', 'sell_value': 110, 'description': 'Gem that phases between dimensions'},
    
    # ========================================================================
    # LEGENDARY MATERIALS - Rare end-game drops
    # ========================================================================
    'dragon_scale': {'name': 'Dragon Scale', 'type': 'material', 'sell_value': 150, 'description': 'Shimmering scale from ancient dragons'},
    'phoenix_feather': {'name': 'Phoenix Feather', 'type': 'material', 'sell_value': 200, 'description': 'Feather of eternal rebirth'},
    'star_fragment': {'name': 'Star Fragment', 'type': 'material', 'sell_value': 250, 'description': 'Piece of a fallen star'},
    'void_crystal': {'name': 'Void Crystal', 'type': 'material', 'sell_value': 300, 'description': 'Crystallized void energy'},
    
    # ========================================================================
    # CONSUMABLES - Healing items from enemies
    # ========================================================================
    'energy_crystal': {'name': 'Energy Crystal', 'type': 'consumable', 'heal': 40, 'sell_value': 25, 'description': 'Crystal that restores vitality'},
    'blood_vial': {'name': 'Blood Vial', 'type': 'consumable', 'heal': 50, 'sell_value': 30, 'description': 'Vial of restorative blood'},
    'soul_elixir': {'name': 'Soul Elixir', 'type': 'consumable', 'heal': 75, 'sell_value': 50, 'description': 'Distilled essence of souls'},
    
    # ========================================================================
    # TEPES LAIR-SPECIFIC LOOT
    # ========================================================================
    'tepes_shard': {'name': 'Tepes Shard', 'type': 'material', 'sell_value': 50, 'description': 'Fragment from the depths of Tepes Lair'},
    'tepes_core': {'name': 'Tepes Core', 'type': 'material', 'sell_value': 150, 'description': 'Core essence from a Tepes Lair floor'},
    'lair_essence': {'name': 'Lair Essence', 'type': 'material', 'sell_value': 200, 'description': 'Concentrated darkness from Tepes Lair'},
    
    # Talismans - rare upgrade items
    'talisman_strength': {'name': 'Talisman of Strength', 'type': 'talisman', 'sell_value': 500, 'description': 'Adds +5 STR to weapons', 'bonus_str': 5, 'item_type': 'weapon'},
    'talisman_accuracy': {'name': 'Talisman of Accuracy', 'type': 'talisman', 'sell_value': 500, 'description': 'Adds +5 DEX to weapons', 'bonus_dex': 5, 'item_type': 'weapon'},
    'talisman_intensification': {'name': 'Talisman of Intensification', 'type': 'talisman', 'sell_value': 1000, 'description': 'Adds +5 STR and +5 DEX to weapons', 'bonus_str': 5, 'bonus_dex': 5, 'item_type': 'weapon'},
    'talisman_insanity': {'name': 'Talisman of Insanity', 'type': 'talisman', 'sell_value': 2000, 'description': 'Adds +10 STR and +10 DEX to weapons', 'bonus_str': 10, 'bonus_dex': 10, 'item_type': 'weapon'},
    'talisman_health': {'name': 'Talisman of Health', 'type': 'talisman', 'sell_value': 500, 'description': 'Adds +5 HP to armor', 'bonus_hp': 5, 'item_type': 'armor'},
    'talisman_defense': {'name': 'Talisman of Defense', 'type': 'talisman', 'sell_value': 500, 'description': 'Adds +5 DEF to armor', 'bonus_defense': 5, 'item_type': 'armor'},
    'talisman_agility': {'name': 'Talisman of Agility', 'type': 'talisman', 'sell_value': 500, 'description': 'Adds +5 AGIL to armor', 'bonus_agl': 5, 'item_type': 'armor'},
    'talisman_heroic': {'name': 'Talisman of The Heroic', 'type': 'talisman', 'sell_value': 1500, 'description': 'Adds +5 HP, +5 DEF, and +5 AGIL to armor', 'bonus_hp': 5, 'bonus_defense': 5, 'bonus_agl': 5, 'item_type': 'armor'},
    'talisman_infinity': {'name': 'Talisman of Infinity', 'type': 'talisman', 'sell_value': 10000, 'description': 'Adds +15 to all stats, usable on weapons and armor', 'bonus_str': 15, 'bonus_dex': 15, 'bonus_agl': 15, 'bonus_hp': 15, 'bonus_defense': 15, 'item_type': 'both'},
    'talisman_hacker': {'name': 'Talisman of the Hacker', 'type': 'talisman', 'sell_value': 50000, 'description': 'Adds +50 to all stats, usable on weapons and armor', 'bonus_str': 50, 'bonus_dex': 50, 'bonus_agl': 50, 'bonus_hp': 50, 'bonus_defense': 50, 'item_type': 'both'}
}

