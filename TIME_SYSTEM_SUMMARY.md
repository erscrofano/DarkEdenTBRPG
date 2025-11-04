# Real-Time In-Game Clock System

## Overview
A comprehensive real-time clock system has been implemented that tracks in-game time independent of player actions, providing an immersive time-of-day experience.

## Core Features

### Time Progression
- **1 real hour = 1 in-game day (24 hours)**
- **DAY phase**: First 45 real minutes (in-game 0:00 - 18:00) - 75% of cycle
- **NIGHT phase**: Last 15 real minutes (in-game 18:00 - 24:00) - 25% of cycle
- Time advances **continuously** regardless of player activity
- Independent of game actions (combat, shopping, menu browsing)

### Persistence System
- **Per-save-slot anchoring**: Each save has its own "world birth" timestamp
- **Cross-session continuity**: Time continues logically from where it left off
- **Backward compatibility**: Old saves automatically initialize with current time as anchor
- **Atomic save/load**: Anchor timestamp persisted in save file

### HUD Display
- **Format**: `@ Day X HH:MM [PHASE]`
- **Example**: `@ Day 3 14:32 [DAY]`
- **Color coding**:
  - DAY: Bright cyan time, bright yellow phase
  - NIGHT: Bright blue time, bright magenta phase
- **Universal placement**: Top of every major screen after clear_screen()

## Technical Implementation

### File Structure
```
rpg_game/systems/
├── time_system.py      # Core clock logic
└── __init__.py         # Module exports

rpg_game/ui/
└── hud.py             # HUD display function

rpg_game/models/
└── player.py          # world_anchor_timestamp field
```

### Key Components

#### 1. GameClock Class (`rpg_game/systems/time_system.py`)
```python
class GameClock:
    - __init__(anchor_timestamp): Initialize with world birth time
    - get_current_time(): Returns day, hour, minute, phase
    - get_formatted_time(): Returns "Day X HH:MM [PHASE]"
    - get_hud_display(): Returns colored HUD string
    - is_day() / is_night(): Phase checks
    - get_time_until_phase_change(): Countdown to next phase
```

#### 2. Player Model Integration
- Added `world_anchor_timestamp` field to Player class
- Automatically set on character creation (`time.time()`)
- Serialized in `to_dict()` method
- Deserialized in `from_dict()` method
- Old saves get current time as default anchor

#### 3. HUD Display Function (`rpg_game/ui/hud.py`)
```python
def display_time_hud(player):
    """Display time HUD at top of screens"""
    clock = GameClock(player.world_anchor_timestamp)
    print(clock.get_hud_display())
    print()  # Spacing
```

### Integration Points

The clock HUD has been integrated into:

#### Location Menus
- ✅ Eslania City menu
- ✅ Perona Outpost menu
- ✅ Travel/locations menu

#### Shops & Guilds
- ✅ General Store
- ✅ Fishing Store
- ✅ Mining Store
- ✅ Knight Guild
- ✅ Army Guild
- ✅ Cleric Guild

#### Character Menus
- ✅ Inventory
- ✅ Achievements
- ✅ Dev Menu

### Time Calculation Algorithm

```python
# Get elapsed real time since anchor
elapsed_seconds = current_time - anchor_timestamp

# Calculate day number (starts at Day 1)
day_number = int(elapsed_seconds / 3600) + 1

# Get position within current day (0-3600 seconds)
seconds_into_day = elapsed_seconds % 3600

# Determine phase and in-game hour
if seconds_into_day < 2700:  # First 45 minutes
    phase = 'DAY'
    # Map 0-2700s to 0-18 hours
    in_game_hour = (seconds_into_day / 2700) * 18
else:  # Last 15 minutes
    phase = 'NIGHT'
    # Map 2700-3600s to 18-24 hours
    in_game_hour = 18 + ((seconds_into_day - 2700) / 900) * 6

# Extract hour and minute
hour = int(in_game_hour)
minute = int((in_game_hour - hour) * 60)
```

## Constants

All timing constants are defined in `rpg_game/systems/time_system.py`:

```python
REAL_SECONDS_PER_DAY = 3600      # 1 hour real time
DAY_PHASE_DURATION = 2700        # 45 minutes
NIGHT_PHASE_DURATION = 900       # 15 minutes
SECONDS_PER_IN_GAME_HOUR = 150   # 2.5 real minutes
SECONDS_PER_IN_GAME_MINUTE = 2.5 # 2.5 real seconds
```

## Usage Examples

### Basic Display
```python
from rpg_game.ui import display_time_hud

def my_menu(player):
    clear_screen()
    display_time_hud(player)  # Shows clock at top
    # ... rest of menu
```

### Direct Clock Access
```python
from rpg_game.systems.time_system import GameClock

clock = GameClock(player.world_anchor_timestamp)
time_data = clock.get_current_time()

print(f"Day: {time_data['day']}")
print(f"Time: {time_data['hour']}:{time_data['minute']:02d}")
print(f"Phase: {time_data['phase']}")

if clock.is_night():
    print("It's nighttime!")
```

### Phase-Based Logic
```python
# Example: Night-time bonuses
from rpg_game.systems.time_system import GameClock

clock = GameClock(player.world_anchor_timestamp)
if clock.is_night():
    enemy_power *= 1.2  # Enemies stronger at night
    experience_bonus *= 1.5  # But more XP
```

## Testing

All core functionality has been tested:

### ✅ Time Advancement
```python
# Test shows time advancing by ~1 minute every 2.5 real seconds
@ Day 1 00:00 [DAY]
# ... wait 3 seconds ...
@ Day 1 00:01 [DAY]
# ... wait 3 seconds ...
@ Day 1 00:02 [DAY]
```

### ✅ Save/Load Persistence
- Create player → anchor timestamp recorded
- Save game → anchor stored in save file
- Load game → anchor restored correctly
- Time continues from logical point

### ✅ Phase Transitions
- DAY phase: 0:00 - 18:00 (first 45 real minutes)
- NIGHT phase: 18:00 - 24:00 (last 15 real minutes)
- Smooth transitions between phases

## Future Enhancement Opportunities

While not implemented, the system supports:

1. **Day/Night Gameplay Mechanics**
   - Different enemies spawn at night
   - Shop hours (some close at night)
   - Special night-time events
   - Visibility/lighting effects

2. **Extended Time Effects**
   - Seasonal changes (could add seasons)
   - Weather patterns tied to time
   - NPC schedules

3. **Time-Based Quests**
   - "Complete before Day X"
   - "Only available at night"
   - Time-limited events

4. **Player Time Tracking**
   - Total real-time played
   - In-game days survived
   - Achievement: "Survived 100 days"

## Design Decisions

### Why per-slot anchoring?
- Different characters can have different "world ages"
- Supports multiple parallel playthroughs
- Makes saves truly independent

### Why 1 hour = 1 day?
- Fast enough to see progression in a play session
- Slow enough to not be distracting
- Day/night split (75%/25%) feels natural

### Why continuous time?
- More immersive than action-based time
- Adds urgency to gameplay decisions
- Realistic: world doesn't pause when you menu-dive

### Why @ symbol instead of emoji?
- Windows terminal encoding issues with Unicode emojis
- @ is universally supported and recognizable
- Clean, simple aesthetic

## Compatibility

- **Python version**: 3.10+
- **OS**: Windows, Linux, macOS
- **Terminal**: Any standard terminal (no curses required)
- **Save format**: JSON-compatible (float timestamp)
- **Backward compatible**: Old saves work seamlessly

## Performance

- **CPU impact**: Negligible (simple arithmetic)
- **Memory**: ~40 bytes per player (single float)
- **Calculation**: O(1) constant time
- **Display**: Standard print operations

## Summary

The real-time clock system is fully functional and integrated throughout the game. It provides a living, breathing world where time passes independently of player actions, enhancing immersion and opening possibilities for time-based gameplay mechanics.

All major menus now display the clock, all saves persist their world time, and the system is ready for both current gameplay and future feature expansion.

