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
    """Real-time in-game clock (1 real hour = 1 in-game day)"""
    
    def __init__(self, anchor_timestamp=None):
        """Initialize clock with anchor timestamp"""
        if anchor_timestamp is None:
            self.anchor_timestamp = time.time()
        else:
            self.anchor_timestamp = anchor_timestamp
    
    def get_current_time(self):
        """Get current in-game time"""
        current_real_time = time.time()
        elapsed_real_seconds = current_real_time - self.anchor_timestamp
        
        if elapsed_real_seconds < 0:
            elapsed_real_seconds = 0
        
        total_days_elapsed = elapsed_real_seconds / REAL_SECONDS_PER_DAY
        day_number = int(total_days_elapsed) + 1
        
        if day_number > 999999999:
            day_number = 999999999
        
        seconds_into_current_day = elapsed_real_seconds % REAL_SECONDS_PER_DAY
        
        if seconds_into_current_day < DAY_PHASE_DURATION:
            phase = 'DAY'
            progress_in_phase = seconds_into_current_day / DAY_PHASE_DURATION
            in_game_hour = progress_in_phase * 18
        else:
            phase = 'NIGHT'
            seconds_into_night = seconds_into_current_day - DAY_PHASE_DURATION
            progress_in_phase = seconds_into_night / NIGHT_PHASE_DURATION
            in_game_hour = 18 + (progress_in_phase * 6)
        
        hour = int(in_game_hour)
        minute = int((in_game_hour - hour) * 60)
        
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
        """Get formatted time string"""
        time_data = self.get_current_time()
        hour_str = f"{time_data['hour']:02d}"
        minute_str = f"{time_data['minute']:02d}"
        return f"Day {time_data['day']} {hour_str}:{minute_str} [{time_data['phase']}]"
    
    def get_hud_display(self):
        """Get colored HUD display for screen header"""
        time_data = self.get_current_time()
        hour_str = f"{time_data['hour']:02d}"
        minute_str = f"{time_data['minute']:02d}"
        
        if time_data['phase'] == 'DAY':
            phase_icon = '*'
            phase_color = Colors.BRIGHT_YELLOW
            time_color = Colors.BRIGHT_CYAN
            phase_text = colorize(f"[{phase_icon} {time_data['phase']}]", phase_color)
        else:
            phase_icon = ')'
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
        """Get seconds until next phase change"""
        time_data = self.get_current_time()
        current_real_time = time.time()
        elapsed_real_seconds = current_real_time - self.anchor_timestamp
        seconds_into_current_day = elapsed_real_seconds % REAL_SECONDS_PER_DAY
        
        if time_data['phase'] == 'DAY':
            return DAY_PHASE_DURATION - seconds_into_current_day
        else:
            return REAL_SECONDS_PER_DAY - seconds_into_current_day


_global_clock = None


def initialize_clock(anchor_timestamp=None):
    """Initialize global clock"""
    global _global_clock
    _global_clock = GameClock(anchor_timestamp)
    return _global_clock


def get_clock():
    """Get global clock instance"""
    global _global_clock
    if _global_clock is None:
        initialize_clock()
    return _global_clock


def display_clock_hud():
    """Display clock HUD"""
    clock = get_clock()
    print(clock.get_hud_display())
    print()

