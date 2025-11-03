"""Location model class"""


class Location:
    def __init__(self, name, description):
        self.name = name
        self.description = description


LOCATIONS = {
    'town': Location('Town', 'A peaceful town with shops and an inn.'),
    'tepes_lair': Location('Tepes lair', 'A mysterious lair that descends deeper into darkness. Each floor grows progressively more dangerous. Infinite challenge awaits.'),
    'fishing': Location('Fishing Spot', 'A peaceful spot by the water. Perfect for catching fish.'),
    'mining': Location('Mining Site', 'A rich mining vein. Perfect for extracting ores and gems.'),
    
    # New locations
    'eslania_city': Location('Eslania City', 'A grand city with guilds, shops, and access to dangerous dungeons.'),
    'perona_outpost': Location('Perona Outpost', 'A remote outpost near the treacherous Asylion Dungeon.'),
    'underground_waterways': Location('Underground Waterways', 'Dark tunnels beneath Eslania City, filled with water and monsters.'),
    
    # Limbo Dungeon (formerly Dark Forest)
    'limbo_dungeon_b1': Location('Limbo Dungeon B1', 'The first floor of the Limbo Dungeon. Recommended for levels 1+.'),
    'limbo_dungeon_b2': Location('Limbo Dungeon B2', 'The second floor of the Limbo Dungeon. Recommended for levels 3+.'),
    'limbo_dungeon_b3': Location('Limbo Dungeon B3', 'The deepest floor of the Limbo Dungeon. Recommended for levels 5+.'),
    
    # Rhaom Dungeon (formerly Dark Cave)
    'rhaom_dungeon_b1': Location('Rhaom Dungeon B1', 'The first floor of the Rhaom Dungeon. Recommended for levels 3+.'),
    'rhaom_dungeon_b2': Location('Rhaom Dungeon B2', 'The second floor of the Rhaom Dungeon. Recommended for levels 6+.'),
    'rhaom_dungeon_b3': Location('Rhaom Dungeon B3', 'The deepest floor of the Rhaom Dungeon. Recommended for levels 10+.'),
    
    # Lost Taiyan (formerly Ancient Dungeon)
    'lost_taiyan_b1': Location('Lost Taiyan B1', 'The first floor of Lost Taiyan. Recommended for levels 8+.'),
    'lost_taiyan_b2': Location('Lost Taiyan B2', 'The second floor of Lost Taiyan. Recommended for levels 12+.'),
    'lost_taiyan_b3': Location('Lost Taiyan B3', 'The deepest floor of Lost Taiyan. Recommended for levels 16+.'),
    
    # Eslania Dungeon
    'eslania_dungeon_b1': Location('Eslania Dungeon B1', 'The first floor of the Eslania Dungeon. Recommended for levels 5+.'),
    'eslania_dungeon_b2': Location('Eslania Dungeon B2', 'The second floor of the Eslania Dungeon. Recommended for levels 10+.'),
    'eslania_dungeon_b3': Location('Eslania Dungeon B3', 'The deepest floor of the Eslania Dungeon. Recommended for levels 15+.'),
    
    # Asylion Dungeon
    'asylion_dungeon_b1': Location('Asylion Dungeon B1', 'The first floor of the Asylion Dungeon. Recommended for levels 8+.'),
    'asylion_dungeon_b2': Location('Asylion Dungeon B2', 'The second floor of the Asylion Dungeon. Recommended for levels 12+.'),
    'asylion_dungeon_b3': Location('Asylion Dungeon B3', 'The deepest floor of the Asylion Dungeon. Recommended for levels 18+.')
}

