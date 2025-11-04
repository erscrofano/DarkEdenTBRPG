# Clock Update Implementation Guide

## Current Implementation

The clock now features:
- **Fancy ASCII-bordered display** at the top of every screen
- **Visual day/night indicators**: `*` for DAY, `)` for NIGHT
- **Color-coded phases**: Yellow/cyan for DAY, magenta/blue for NIGHT
- **Consistent 60-character width** with centered content
- **Updates on screen refresh** (when navigating menus)

## Clock Display Format

```
+----------------------------------------------------------+
|                 Day 1 | 14:32 | * DAY                  |
+----------------------------------------------------------+
```

## How Clock Updates Work

### Current Behavior
The clock updates whenever:
1. You change screens/menus
2. The game calls `clear_screen()` followed by `display_time_hud(player)`
3. You perform an action that refreshes the screen

### Making It Update More Frequently

#### Option 1: Pre-Input Refresh (Recommended - No External Libraries)
Add `refresh_time_display(player)` before input prompts:

```python
from rpg_game.ui import refresh_time_display

# Before any input
refresh_time_display(player)
choice = input("What do you do? ").strip()
```

This shows a compact time update right before the user types.

#### Option 2: Periodic Screen Refresh (Simple Loop)
For long-running activities (fishing, mining), refresh periodically:

```python
import time
from rpg_game.ui import display_time_hud, clear_screen

while activity_active:
    clear_screen()
    display_time_hud(player)
    print("Fishing...")
    time.sleep(1)  # Update every second
    # ... activity logic ...
```

#### Option 3: Background Thread (Advanced)
For true real-time updates while waiting for input:

```python
import threading
import time

def update_clock_thread(player, stop_event):
    while not stop_event.is_set():
        # Move cursor to clock position and update
        refresh_time_display(player)
        time.sleep(1)

# Start thread before menu
stop_event = threading.Event()
clock_thread = threading.Thread(target=update_clock_thread, args=(player, stop_event))
clock_thread.daemon = True
clock_thread.start()

# Show menu...

# Stop thread
stop_event.set()
```

**Note**: This approach is complex and may cause display issues with `input()`.

#### Option 4: Curses Library (Professional Solution)
For a true "always updating" clock like a status bar:

```python
import curses

def main_game_loop(stdscr, player):
    # Initialize
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(True)  # Non-blocking input
    
    while running:
        # Clear screen
        stdscr.clear()
        
        # Draw clock at top (always updated)
        clock = GameClock(player.world_anchor_timestamp)
        time_data = clock.get_current_time()
        stdscr.addstr(0, 0, f"Day {time_data['day']} {time_data['hour']:02d}:{time_data['minute']:02d}")
        
        # Draw rest of UI
        # ...
        
        # Refresh display
        stdscr.refresh()
        
        # Small delay
        time.sleep(0.1)
        
        # Check for input (non-blocking)
        key = stdscr.getch()
        if key != -1:
            # Handle input
            pass

# Run with curses
curses.wrapper(lambda stdscr: main_game_loop(stdscr, player))
```

## Day/Night Cycle Details

### Timing Breakdown
- **1 real hour** = **1 in-game day** (24 hours)
- **2.5 real seconds** = **1 in-game minute**
- **150 real seconds** = **1 in-game hour**

### Phase Duration
- **DAY**: First 45 real minutes (in-game 0:00 - 18:00) - 75% of cycle
- **NIGHT**: Last 15 real minutes (in-game 18:00 - 24:00) - 25% of cycle

### Phase Transition Times
| Real Time Elapsed | In-Game Time | Phase |
|-------------------|--------------|-------|
| 0 min             | 0:00         | DAY   |
| 22.5 min          | 9:00         | DAY   |
| 45 min            | 18:00        | NIGHT |
| 52.5 min          | 21:00        | NIGHT |
| 60 min            | 0:00 (Day 2) | DAY   |

## Usage Examples

### Example 1: Refresh Before Important Prompts
```python
def important_choice_menu(player):
    clear_screen()
    display_time_hud(player)
    
    print("Important Decision:")
    print("1. Option A")
    print("2. Option B")
    
    refresh_time_display(player)  # Show current time right before input
    choice = input("Choose: ").strip()
```

### Example 2: Activity Loop with Updates
```python
def long_activity(player):
    start_time = time.time()
    
    while time.time() - start_time < 10:  # 10 second activity
        clear_screen()
        display_time_hud(player)  # Full fancy display
        print("Activity in progress...")
        time.sleep(1)
```

### Example 3: Time-Based Gameplay
```python
from rpg_game.systems.time_system import GameClock

def check_shop_hours(player):
    clock = GameClock(player.world_anchor_timestamp)
    
    if clock.is_night():
        print("The shop is closed at night!")
        print("Come back during the day (0:00 - 18:00)")
        return False
    
    return True
```

## Recommendation

For **your current game style** (menu-based with blocking input), the best approach is:

1. **Keep the current implementation** - clock updates on screen changes
2. **Add `refresh_time_display(player)` before key input prompts** for frequent updates
3. **Consider curses** only if you want a completely different UI with:
   - Non-blocking input
   - Continuously updating status bars
   - More complex terminal control

The current implementation is **clean, professional, and follows best practices** for a traditional terminal RPG. Adding `refresh_time_display()` calls will make it feel more dynamic without major architectural changes.

## Best Practice Integration

To maximize clock visibility, add refresh calls in these strategic locations:

### High-Priority Locations (adds freshness without spam)
```python
# Main menu loops
def eslania_city_menu(player):
    clear_screen()
    display_time_hud(player)
    # ... menu display ...
    refresh_time_display(player)  # <-- Add here
    choice = input("What do you do? ").strip()

# Combat (between turns)
def combat_loop(player, enemy):
    while combat_active:
        clear_screen()
        display_time_hud(player)
        # ... combat display ...
        refresh_time_display(player)  # <-- Add here
        action = input("Choose action: ").strip()

# Skills/activities (periodic updates)
def go_fishing(player):
    while fishing:
        clear_screen()
        display_time_hud(player)
        # ... fishing UI ...
        time.sleep(1)  # Natural update rhythm
```

This gives you the "always updating" feel without requiring complex threading or curses implementation.

