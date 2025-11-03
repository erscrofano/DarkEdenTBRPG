"""Achievement system"""
from datetime import datetime
from ..ui import Colors, show_notification
from ..save.system import get_save_dir
from ..items.rarity import get_item_rarity


# All available achievements in the game
ALL_ACHIEVEMENTS = {
    # Level Achievements - Scaled to match game economy
    'Level 5': {'name': 'Level 5', 'description': 'Reach Level 5', 'gold_reward': 500, 'type': 'level', 'requirement': 5},
    'Level 10': {'name': 'Level 10', 'description': 'Reach Level 10', 'gold_reward': 1000, 'type': 'level', 'requirement': 10},
    'Level 25': {'name': 'Level 25', 'description': 'Reach Level 25', 'gold_reward': 5000, 'type': 'level', 'requirement': 25},
    'Level 50': {'name': 'Level 50', 'description': 'Reach Level 50', 'gold_reward': 25000, 'type': 'level', 'requirement': 50},
    'Level 75': {'name': 'Level 75', 'description': 'Reach Level 75', 'gold_reward': 75000, 'type': 'level', 'requirement': 75},
    'Level 90': {'name': 'Level 90', 'description': 'Reach Level 90', 'gold_reward': 200000, 'type': 'level', 'requirement': 90},
    'Level 99': {'name': 'Level 99', 'description': 'Reach Level 99', 'gold_reward': 500000, 'type': 'level', 'requirement': 99},
    
    # Kill Achievements - Scaled rewards
    '100 Kills': {'name': '100 Kills', 'description': 'Slay 100 enemies', 'gold_reward': 1000, 'type': 'kills', 'requirement': 100},
    '500 Kills': {'name': '500 Kills', 'description': 'Slay 500 enemies', 'gold_reward': 5000, 'type': 'kills', 'requirement': 500},
    '1000 Kills': {'name': '1000 Kills', 'description': 'Slay 1000 enemies', 'gold_reward': 15000, 'type': 'kills', 'requirement': 1000},
    '2500 Kills': {'name': '2500 Kills', 'description': 'Slay 2500 enemies', 'gold_reward': 40000, 'type': 'kills', 'requirement': 2500},
    '5000 Kills': {'name': '5000 Kills', 'description': 'Slay 5000 enemies', 'gold_reward': 100000, 'type': 'kills', 'requirement': 5000},
    '10000 Kills': {'name': '10000 Kills', 'description': 'Slay 10000 enemies', 'gold_reward': 250000, 'type': 'kills', 'requirement': 10000},
    '25000 Kills': {'name': '25000 Kills', 'description': 'Slay 25000 enemies', 'gold_reward': 750000, 'type': 'kills', 'requirement': 25000},
    
    # Kill Streak Achievements
    '10 Kill Streak': {'name': '10 Kill Streak', 'description': 'Achieve a 10 kill streak', 'gold_reward': 500, 'type': 'streak', 'requirement': 10},
    '25 Kill Streak': {'name': '25 Kill Streak', 'description': 'Achieve a 25 kill streak', 'gold_reward': 2000, 'type': 'streak', 'requirement': 25},
    '50 Kill Streak': {'name': '50 Kill Streak', 'description': 'Achieve a 50 kill streak', 'gold_reward': 10000, 'type': 'streak', 'requirement': 50},
    '75 Kill Streak': {'name': '75 Kill Streak', 'description': 'Achieve a 75 kill streak', 'gold_reward': 25000, 'type': 'streak', 'requirement': 75},
    '100 Kill Streak': {'name': '100 Kill Streak', 'description': 'Achieve a 100 kill streak', 'gold_reward': 50000, 'type': 'streak', 'requirement': 100},
    '150 Kill Streak': {'name': '150 Kill Streak', 'description': 'Achieve a 150 kill streak', 'gold_reward': 100000, 'type': 'streak', 'requirement': 150},
    
    # Item Drop Achievements
    'Rare Drop': {'name': 'Rare Drop', 'description': 'Find a Rare (Epic) item', 'gold_reward': 2000, 'type': 'rare_drop', 'requirement': 75},
    'Legendary Drop': {'name': 'Legendary Drop', 'description': 'Find a Legendary item', 'gold_reward': 10000, 'type': 'rare_drop', 'requirement': 200},
    'Talisman Found': {'name': 'Talisman Found', 'description': 'Find your first Talisman', 'gold_reward': 5000, 'type': 'talisman_found', 'requirement': 1},
    'Talisman Collector': {'name': 'Talisman Collector', 'description': 'Find 10 Talismans', 'gold_reward': 25000, 'type': 'talisman_count', 'requirement': 10},
    'Talisman Master': {'name': 'Talisman Master', 'description': 'Find 25 Talismans', 'gold_reward': 75000, 'type': 'talisman_count', 'requirement': 25},
    'Ultimate Talisman': {'name': 'Ultimate Talisman', 'description': 'Find Talisman of the Hacker', 'gold_reward': 500000, 'type': 'talisman_hacker', 'requirement': 1},
    
    # Tower/Tepes Lair Achievements
    'Tower Floor 10': {'name': 'Tower Floor 10', 'description': 'Reach Floor 10 in Tepes lair', 'gold_reward': 2000, 'type': 'tower', 'requirement': 10},
    'Tower Floor 25': {'name': 'Tower Floor 25', 'description': 'Reach Floor 25 in Tepes lair', 'gold_reward': 10000, 'type': 'tower', 'requirement': 25},
    'Tower Floor 50': {'name': 'Tower Floor 50', 'description': 'Reach Floor 50 in Tepes lair', 'gold_reward': 50000, 'type': 'tower', 'requirement': 50},
    'Tower Floor 75': {'name': 'Tower Floor 75', 'description': 'Reach Floor 75 in Tepes lair', 'gold_reward': 125000, 'type': 'tower', 'requirement': 75},
    'Tower Floor 100': {'name': 'Tower Floor 100', 'description': 'Reach Floor 100 in Tepes lair', 'gold_reward': 300000, 'type': 'tower', 'requirement': 100},
    'Tower Floor 150': {'name': 'Tower Floor 150', 'description': 'Reach Floor 150 in Tepes lair', 'gold_reward': 750000, 'type': 'tower', 'requirement': 150},
    'Tower Floor 200': {'name': 'Tower Floor 200', 'description': 'Reach Floor 200 in Tepes lair', 'gold_reward': 1500000, 'type': 'tower', 'requirement': 200},
    
    # Fishing Achievements
    'Angler 10': {'name': 'Angler 10', 'description': 'Reach Fishing level 10', 'gold_reward': 1000, 'type': 'fishing_level', 'requirement': 10},
    'Angler 25': {'name': 'Angler 25', 'description': 'Reach Fishing level 25', 'gold_reward': 5000, 'type': 'fishing_level', 'requirement': 25},
    'Angler 50': {'name': 'Angler 50', 'description': 'Reach Fishing level 50', 'gold_reward': 25000, 'type': 'fishing_level', 'requirement': 50},
    'Angler 75': {'name': 'Angler 75', 'description': 'Reach Fishing level 75', 'gold_reward': 75000, 'type': 'fishing_level', 'requirement': 75},
    'Angler 99': {'name': 'Angler 99', 'description': 'Reach Fishing level 99', 'gold_reward': 200000, 'type': 'fishing_level', 'requirement': 99},
    
    # Cooking Achievements
    'Chef 10': {'name': 'Chef 10', 'description': 'Reach Cooking level 10', 'gold_reward': 1000, 'type': 'cooking_level', 'requirement': 10},
    'Chef 25': {'name': 'Chef 25', 'description': 'Reach Cooking level 25', 'gold_reward': 5000, 'type': 'cooking_level', 'requirement': 25},
    'Chef 50': {'name': 'Chef 50', 'description': 'Reach Cooking level 50', 'gold_reward': 25000, 'type': 'cooking_level', 'requirement': 50},
    'Chef 75': {'name': 'Chef 75', 'description': 'Reach Cooking level 75', 'gold_reward': 75000, 'type': 'cooking_level', 'requirement': 75},
    'Chef 99': {'name': 'Chef 99', 'description': 'Reach Cooking level 99', 'gold_reward': 200000, 'type': 'cooking_level', 'requirement': 99},
    
    # Mining Achievements
    'Miner 10': {'name': 'Miner 10', 'description': 'Reach Mining level 10', 'gold_reward': 1000, 'type': 'mining_level', 'requirement': 10},
    'Miner 25': {'name': 'Miner 25', 'description': 'Reach Mining level 25', 'gold_reward': 5000, 'type': 'mining_level', 'requirement': 25},
    'Miner 50': {'name': 'Miner 50', 'description': 'Reach Mining level 50', 'gold_reward': 25000, 'type': 'mining_level', 'requirement': 50},
    'Miner 75': {'name': 'Miner 75', 'description': 'Reach Mining level 75', 'gold_reward': 75000, 'type': 'mining_level', 'requirement': 75},
    'Miner 99': {'name': 'Miner 99', 'description': 'Reach Mining level 99', 'gold_reward': 200000, 'type': 'mining_level', 'requirement': 99},
    
    # Skill Milestone Achievements
    'First Catch': {'name': 'First Catch', 'description': 'Catch any fish', 'gold_reward': 200, 'type': 'first_catch', 'requirement': 1},
    'First Cook': {'name': 'First Cook', 'description': 'Successfully cook any fish', 'gold_reward': 200, 'type': 'first_cook', 'requirement': 1},
    'First Mine': {'name': 'First Mine', 'description': 'Mine any ore', 'gold_reward': 200, 'type': 'first_mine', 'requirement': 1},
    'Masterpiece': {'name': 'Masterpiece', 'description': 'Successfully cook a Silvery Carp', 'gold_reward': 5000, 'type': 'masterpiece', 'requirement': 1},
    
    # Wealth Achievements
    'Rich': {'name': 'Rich', 'description': 'Accumulate 100,000 gold', 'gold_reward': 10000, 'type': 'wealth', 'requirement': 100000},
    'Wealthy': {'name': 'Wealthy', 'description': 'Accumulate 500,000 gold', 'gold_reward': 50000, 'type': 'wealth', 'requirement': 500000},
    'Millionaire': {'name': 'Millionaire', 'description': 'Accumulate 1,000,000 gold', 'gold_reward': 200000, 'type': 'wealth', 'requirement': 1000000},
    'Tycoon': {'name': 'Tycoon', 'description': 'Accumulate 5,000,000 gold', 'gold_reward': 1000000, 'type': 'wealth', 'requirement': 5000000},
    
    # Equipment Achievements
    'Gear Collector': {'name': 'Gear Collector', 'description': 'Equip G40 weapon or armor', 'gold_reward': 10000, 'type': 'gear_tier', 'requirement': 40},
    'Elite Gear': {'name': 'Elite Gear', 'description': 'Equip G60 weapon or armor', 'gold_reward': 50000, 'type': 'gear_tier', 'requirement': 60},
    'Legendary Gear': {'name': 'Legendary Gear', 'description': 'Equip G80 weapon or armor', 'gold_reward': 200000, 'type': 'gear_tier', 'requirement': 80},
    'Ultimate Gear': {'name': 'Ultimate Gear', 'description': 'Equip G90 weapon or armor', 'gold_reward': 500000, 'type': 'gear_tier', 'requirement': 90}
}


def log_rare_drop(player, item, sell_value):
    """Log rare drops to file"""
    try:
        log_dir = get_save_dir() / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / 'rare_drops.log'
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        rarity = get_item_rarity(item)
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {player.name} (Lv.{player.level}) found {rarity.upper()}: {item['name']} (Value: {sell_value}g)\n")
    except Exception:
        pass  # Fail silently if logging fails


def check_achievements(player, achievement_type, value=None):
    """Check and unlock achievements (OSRS-style) with gold rewards"""
    new_achievements = []
    total_gold_reward = 0
    
    if achievement_type == 'level':
        for ach_key, ach_data in ALL_ACHIEVEMENTS.items():
            if ach_data['type'] == 'level':
                if player.level >= ach_data['requirement'] and ach_key not in player.achievements:
                    player.achievements.append(ach_key)
                    new_achievements.append((ach_data['name'], ach_data['gold_reward']))
                    total_gold_reward += ach_data['gold_reward']
    
    elif achievement_type == 'kills':
        for ach_key, ach_data in ALL_ACHIEVEMENTS.items():
            if ach_data['type'] == 'kills':
                if player.total_kills >= ach_data['requirement'] and ach_key not in player.achievements:
                    player.achievements.append(ach_key)
                    new_achievements.append((ach_data['name'], ach_data['gold_reward']))
                    total_gold_reward += ach_data['gold_reward']
    
    elif achievement_type == 'streak':
        for ach_key, ach_data in ALL_ACHIEVEMENTS.items():
            if ach_data['type'] == 'streak':
                if player.kill_streak >= ach_data['requirement'] and ach_key not in player.achievements:
                    player.achievements.append(ach_key)
                    new_achievements.append((ach_data['name'], ach_data['gold_reward']))
                    total_gold_reward += ach_data['gold_reward']
    
    elif achievement_type == 'rare_drop':
        if value:
            for ach_key, ach_data in ALL_ACHIEVEMENTS.items():
                if ach_data['type'] == 'rare_drop':
                    if value >= ach_data['requirement'] and ach_key not in player.achievements:
                        player.achievements.append(ach_key)
                        new_achievements.append((ach_data['name'], ach_data['gold_reward']))
                        total_gold_reward += ach_data['gold_reward']
    
    elif achievement_type == 'tower_floor':
        if value:
            for ach_key, ach_data in ALL_ACHIEVEMENTS.items():
                if ach_data['type'] == 'tower':
                    if value >= ach_data['requirement'] and ach_key not in player.achievements:
                        player.achievements.append(ach_key)
                        new_achievements.append((ach_data['name'], ach_data['gold_reward']))
                        total_gold_reward += ach_data['gold_reward']
    
    elif achievement_type == 'fishing_level':
        for ach_key, ach_data in ALL_ACHIEVEMENTS.items():
            if ach_data['type'] == 'fishing_level':
                if player.fishing_level >= ach_data['requirement'] and ach_key not in player.achievements:
                    player.achievements.append(ach_key)
                    new_achievements.append((ach_data['name'], ach_data['gold_reward']))
                    total_gold_reward += ach_data['gold_reward']
    
    elif achievement_type == 'cooking_level':
        for ach_key, ach_data in ALL_ACHIEVEMENTS.items():
            if ach_data['type'] == 'cooking_level':
                if player.cooking_level >= ach_data['requirement'] and ach_key not in player.achievements:
                    player.achievements.append(ach_key)
                    new_achievements.append((ach_data['name'], ach_data['gold_reward']))
                    total_gold_reward += ach_data['gold_reward']
    
    elif achievement_type == 'mining_level':
        for ach_key, ach_data in ALL_ACHIEVEMENTS.items():
            if ach_data['type'] == 'mining_level':
                if player.mining_level >= ach_data['requirement'] and ach_key not in player.achievements:
                    player.achievements.append(ach_key)
                    new_achievements.append((ach_data['name'], ach_data['gold_reward']))
                    total_gold_reward += ach_data['gold_reward']
    
    elif achievement_type == 'first_catch':
        ach_key = 'First Catch'
        if ach_key not in player.achievements:
            player.achievements.append(ach_key)
            ach_data = ALL_ACHIEVEMENTS.get(ach_key)
            if ach_data:
                new_achievements.append((ach_data['name'], ach_data['gold_reward']))
                total_gold_reward += ach_data['gold_reward']
    
    elif achievement_type == 'first_cook':
        ach_key = 'First Cook'
        if ach_key not in player.achievements:
            player.achievements.append(ach_key)
            ach_data = ALL_ACHIEVEMENTS.get(ach_key)
            if ach_data:
                new_achievements.append((ach_data['name'], ach_data['gold_reward']))
                total_gold_reward += ach_data['gold_reward']
    
    elif achievement_type == 'masterpiece':
        ach_key = 'Masterpiece'
        if ach_key not in player.achievements:
            player.achievements.append(ach_key)
            ach_data = ALL_ACHIEVEMENTS.get(ach_key)
            if ach_data:
                new_achievements.append((ach_data['name'], ach_data['gold_reward']))
                total_gold_reward += ach_data['gold_reward']
    
    elif achievement_type == 'first_mine':
        ach_key = 'First Mine'
        if ach_key not in player.achievements:
            player.achievements.append(ach_key)
            ach_data = ALL_ACHIEVEMENTS.get(ach_key)
            if ach_data:
                new_achievements.append((ach_data['name'], ach_data['gold_reward']))
                total_gold_reward += ach_data['gold_reward']
    
    elif achievement_type == 'talisman_found':
        ach_key = 'Talisman Found'
        if ach_key not in player.achievements:
            player.achievements.append(ach_key)
            ach_data = ALL_ACHIEVEMENTS.get(ach_key)
            if ach_data:
                new_achievements.append((ach_data['name'], ach_data['gold_reward']))
                total_gold_reward += ach_data['gold_reward']
    
    elif achievement_type == 'talisman_hacker':
        ach_key = 'Ultimate Talisman'
        if ach_key not in player.achievements:
            player.achievements.append(ach_key)
            ach_data = ALL_ACHIEVEMENTS.get(ach_key)
            if ach_data:
                new_achievements.append((ach_data['name'], ach_data['gold_reward']))
                total_gold_reward += ach_data['gold_reward']
    
    elif achievement_type == 'talisman_count':
        # Check talisman count achievements
        talisman_count = 0
        for item in player.inventory:
            if item.get('type') == 'talisman':
                talisman_count += 1
        
        for ach_key, ach_data in ALL_ACHIEVEMENTS.items():
            if ach_data['type'] == 'talisman_count':
                if talisman_count >= ach_data['requirement'] and ach_key not in player.achievements:
                    player.achievements.append(ach_key)
                    new_achievements.append((ach_data['name'], ach_data['gold_reward']))
                    total_gold_reward += ach_data['gold_reward']
    
    elif achievement_type == 'wealth':
        # Check wealth achievements based on current gold
        for ach_key, ach_data in ALL_ACHIEVEMENTS.items():
            if ach_data['type'] == 'wealth':
                if player.gold >= ach_data['requirement'] and ach_key not in player.achievements:
                    player.achievements.append(ach_key)
                    new_achievements.append((ach_data['name'], ach_data['gold_reward']))
                    total_gold_reward += ach_data['gold_reward']
    
    elif achievement_type == 'gear_tier':
        # Check gear tier achievements based on equipped weapon/armor
        max_grade = 0
        if player.weapon and 'grade' in player.weapon:
            max_grade = max(max_grade, player.weapon['grade'])
        if player.armor and 'grade' in player.armor:
            max_grade = max(max_grade, player.armor['grade'])
        
        for ach_key, ach_data in ALL_ACHIEVEMENTS.items():
            if ach_data['type'] == 'gear_tier':
                if max_grade >= ach_data['requirement'] and ach_key not in player.achievements:
                    player.achievements.append(ach_key)
                    new_achievements.append((ach_data['name'], ach_data['gold_reward']))
                    total_gold_reward += ach_data['gold_reward']
    
    # Show notifications and award gold
    for ach_name, gold_reward in new_achievements:
        player.gold += gold_reward
        show_notification(f"Achievement Unlocked: {ach_name} (+{gold_reward} gold)!", Colors.BRIGHT_GREEN, 2.0, critical=True)
    
    if total_gold_reward > 0:
        # Also show total if multiple achievements unlocked
        if len(new_achievements) > 1:
            show_notification(f"Total Gold Reward: {total_gold_reward} gold!", Colors.BRIGHT_YELLOW, 1.5, critical=True)

