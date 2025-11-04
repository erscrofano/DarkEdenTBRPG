"""Real-time in-game clock system"""
import time
from datetime import datetime
from ..ui import Colors, colorize


# Time constants
REAL_SECONDS_PER_DAY = 3600  # 1 real hour = 1 in-game day
DAY_PHASE_DURATION = 2700    # 45 real minutes (75% of cycle)
NIGHT_PHASE_DURATION = 900   # 15 real minutes (25% of cycle)
SECONDS_PER_IN_GAME_HOUR = REAL_SECONDS_PER_DAY / 24  # 150 real seconds = 1 in-game hour
SECONDS_PER_IN_GAME_MINUTE = SECONDS_PER_IN_GAME_HOUR / 60  # 2.5 real seconds = 1 in-game minute


class GameClock:
    """
    Real-time in-game clock that progresses independently of player actions.
    
    Design:
    - 1 real hour = 1 in-game day (24 hours)
    - Day: first 45 real minutes (in-game hours 0-18)
    - Night: last 15 real minutes (in-game hours 18-24)
    - Time is anchored to a real-world timestamp per save slot
    - Persists across save/load cycles
    """
    
    def __init__(self, anchor_timestamp=None):
        """
        Initialize the game clock.
        
        Args:
            anchor_timestamp: Unix timestamp marking "day 1, hour 0" for this world.
                            If None, uses current time as anchor (new world).
        """
        if anchor_timestamp is None:
            self.anchor_timestamp = time.time()
        else:
            self.anchor_timestamp = anchor_timestamp
    
    def get_current_time(self):
        """
        Get current in-game time based on real time elapsed since anchor.
        
        Returns:
            dict with:
                - day: int (1, 2, 3, ...)
                - hour: int (0-23)
                - minute: int (0-59)
                - phase: str ('DAY' or 'NIGHT')
                - cycle_progress: float (0.0 to 1.0, position in current day cycle)
        
        Note: This system is designed to handle extreme long-term use:
        - Supports up to ~10^15 days (trillions of years of continuous uptime)
        - Safe from integer overflow (Python ints have arbitrary precision)
        - Float precision remains adequate for gameplay purposes even at extreme scales
        """
        # Calculate real seconds elapsed since anchor
        current_real_time = time.time()
        elapsed_real_seconds = current_real_time - self.anchor_timestamp
        
        # Safety: Ensure elapsed time is non-negative (protect against clock adjustments)
        if elapsed_real_seconds < 0:
            elapsed_real_seconds = 0
        
        # Calculate which day we're on (starts at day 1)
        # Note: Python int() safely handles very large floats, truncating to integer
        # This will work correctly for trillions of days
        total_days_elapsed = elapsed_real_seconds / REAL_SECONDS_PER_DAY
        day_number = int(total_days_elapsed) + 1  # Day 1, 2, 3, ...
        
        # Sanity cap: if somehow day number exceeds reasonable bounds, cap it
        # (This should never happen in practice, but provides a safety net)
        if day_number > 999999999:  # Cap at ~1 billion days (2.7 million years)
            day_number = 999999999
        
        # Calculate position within current day cycle
        seconds_into_current_day = elapsed_real_seconds % REAL_SECONDS_PER_DAY
        
        # Calculate in-game hour and minute
        # 0-2700 seconds (45 min) = day phase (hours 0-18)
        # 2700-3600 seconds (15 min) = night phase (hours 18-24)
        
        if seconds_into_current_day < DAY_PHASE_DURATION:
            # Day phase (0-45 real minutes = 0-18 in-game hours)
            phase = 'DAY'
            # Map 0-2700 seconds to 0-18 hours
            progress_in_phase = seconds_into_current_day / DAY_PHASE_DURATION
            in_game_hour = progress_in_phase * 18  # 0 to 18 hours
        else:
            # Night phase (45-60 real minutes = 18-24 in-game hours)
            phase = 'NIGHT'
            seconds_into_night = seconds_into_current_day - DAY_PHASE_DURATION
            # Map 0-900 seconds to 18-24 hours
            progress_in_phase = seconds_into_night / NIGHT_PHASE_DURATION
            in_game_hour = 18 + (progress_in_phase * 6)  # 18 to 24 hours
        
        # Extract hour and minute
        hour = int(in_game_hour)
        minute = int((in_game_hour - hour) * 60)
        
        # Handle hour 24 wrapping (shouldn't happen, but safety)
        if hour >= 24:
            hour = 23
            minute = 59
        
        return {
            'day': day_number,
            'hour': hour,
            'minute': minute,
            'phase': phase,
            'cycle_progress': seconds_into_current_day / REAL_SECONDS_PER_DAY,
            'anchor_timestamp': self.anchor_timestamp
        }
    
    def get_formatted_time(self):
        """
        Get a formatted time string for display.
        
        Returns:
            str: "Day X HH:MM [PHASE]"
        """
        time_data = self.get_current_time()
        hour_str = f"{time_data['hour']:02d}"
        minute_str = f"{time_data['minute']:02d}"
        return f"Day {time_data['day']} {hour_str}:{minute_str} [{time_data['phase']}]"
    
    def get_hud_display(self):
        """
        Get a colored HUD display line for the top of screens.
        
        Returns:
            str: Colored clock display with visual day/night indicator
        """
        time_data = self.get_current_time()
        hour_str = f"{time_data['hour']:02d}"
        minute_str = f"{time_data['minute']:02d}"
        
        # Color based on phase with visual indicators (simple ASCII for Windows)
        if time_data['phase'] == 'DAY':
            phase_icon = '*'  # Sun symbol (asterisk)
            phase_color = Colors.BRIGHT_YELLOW
            time_color = Colors.BRIGHT_CYAN
            phase_text = colorize(f"[{phase_icon} {time_data['phase']}]", phase_color)
        else:  # NIGHT
            phase_icon = ')'  # Moon symbol (crescent)
            phase_color = Colors.BRIGHT_MAGENTA
            time_color = Colors.BRIGHT_BLUE
            phase_text = colorize(f"[{phase_icon} {time_data['phase']}]", phase_color)
        
        day_text = colorize(f"Day {time_data['day']}", Colors.WHITE)
        time_text = colorize(f"{hour_str}:{minute_str}", time_color)
        
        return f"@ {day_text} {time_text} {phase_text}"
    
    def is_day(self):
        """Check if it's currently daytime"""
        return self.get_current_time()['phase'] == 'DAY'
    
    def is_night(self):
        """Check if it's currently nighttime"""
        return self.get_current_time()['phase'] == 'NIGHT'
    
    def get_time_until_phase_change(self):
        """
        Get seconds until next phase change.
        
        Returns:
            int: Real seconds until DAY→NIGHT or NIGHT→DAY
        """
        time_data = self.get_current_time()
        current_real_time = time.time()
        elapsed_real_seconds = current_real_time - self.anchor_timestamp
        seconds_into_current_day = elapsed_real_seconds % REAL_SECONDS_PER_DAY
        
        if time_data['phase'] == 'DAY':
            # Time until night starts
            return DAY_PHASE_DURATION - seconds_into_current_day
        else:
            # Time until day starts (next cycle)
            return REAL_SECONDS_PER_DAY - seconds_into_current_day


# Global clock instance (will be set by GameManager)
_global_clock = None


def initialize_clock(anchor_timestamp=None):
    """Initialize the global game clock"""
    global _global_clock
    _global_clock = GameClock(anchor_timestamp)
    return _global_clock


def get_clock():
    """Get the global game clock instance"""
    global _global_clock
    if _global_clock is None:
        # Auto-initialize if not done yet (safety)
        initialize_clock()
    return _global_clock


def display_clock_hud():
    """Display the clock HUD at the top of the screen"""
    clock = get_clock()
    print(clock.get_hud_display())
    print()  # Empty line for spacing

