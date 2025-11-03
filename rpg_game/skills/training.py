"""Training Zone skill system"""
import time
import threading
from ..config import DEV_FLAGS
from ..ui import Colors, colorize, clear_screen, show_notification


def add_exp(player, amount, silent=False):
    """Add XP to player and handle level ups (silent mode for training)"""
    player.exp += amount
    levels_gained = 0
    
    # Handle multiple level ups in a row
    while player.level_up(silent=silent):
        levels_gained += 1
        if silent:
            # Silent mode: just show a brief notification
            show_notification(f"Level {player.level}! +5 stat points banked", Colors.BRIGHT_GREEN, 1.5, critical=True)
    
    return levels_gained


def training_simulator(player):
    """Training Zone - gain XP through simulated combat training"""
    clear_screen()
    print(colorize("=" * 60, Colors.BRIGHT_CYAN))
    print(colorize("⚔️  TRAINING ZONE  ⚔️", Colors.BRIGHT_CYAN + Colors.BOLD))
    print(colorize("=" * 60, Colors.BRIGHT_CYAN))
    print(f"\n{colorize('A combat training zone for safe XP farming.', Colors.WHITE)}")
    print(f"\n{colorize('Training will automatically continue. Press Enter to stop.', Colors.YELLOW)}")
    print(f"{colorize('Level:', Colors.BRIGHT_CYAN)} {colorize(str(player.level), Colors.BRIGHT_GREEN)}")
    print(f"{colorize('XP:', Colors.BRIGHT_CYAN)} {colorize(f'{player.exp}/{player.exp_to_next}', Colors.BRIGHT_GREEN)}")
    if player.stat_points > 0:
        print(f"{colorize('Banked Stat Points:', Colors.BRIGHT_YELLOW)} {colorize(str(player.stat_points), Colors.BRIGHT_YELLOW + Colors.BOLD)}")
    print(colorize("=" * 60, Colors.BRIGHT_CYAN))
    input(f"\n{colorize('Press Enter to start training...', Colors.BRIGHT_CYAN)}")
    
    training_active = True
    total_xp_gained = 0
    total_levels_gained = 0
    
    # Training parameters: 5 XP every 8 seconds
    xp_per_cycle = 5
    cycle_duration = 8.0
    
    def training_loop():
        nonlocal training_active, total_xp_gained, total_levels_gained
        
        while training_active:
            # Progress bar for training cycle
            progress_steps = 20
            step_delay = cycle_duration / progress_steps
            
            for i in range(progress_steps):
                if not training_active:
                    return
                
                # Calculate progress
                progress = (i + 1) / progress_steps
                filled = int(20 * progress)
                bar = colorize("█" * filled, Colors.BRIGHT_GREEN) + "░" * (20 - filled)
                percentage = int(progress * 100)
                
                # Update display
                clear_screen()
                print(colorize("=" * 60, Colors.BRIGHT_CYAN))
                print(colorize("⚔️  TRAINING ZONE  ⚔️", Colors.BRIGHT_CYAN + Colors.BOLD))
                print(colorize("=" * 60, Colors.BRIGHT_CYAN))
                print(f"\n{colorize('Training in progress...', Colors.WHITE)}")
                print(f"\n{colorize('Progress:', Colors.BRIGHT_WHITE)} [{bar}] {colorize(f'{percentage}%', Colors.BRIGHT_YELLOW)}")
                print(f"\n{colorize('Level:', Colors.BRIGHT_CYAN)} {colorize(str(player.level), Colors.BRIGHT_GREEN)}")
                print(f"{colorize('XP:', Colors.BRIGHT_CYAN)} {colorize(f'{player.exp}/{player.exp_to_next}', Colors.BRIGHT_GREEN)}")
                print(f"{colorize('Total XP Gained:', Colors.WHITE)} {colorize(str(total_xp_gained), Colors.BRIGHT_GREEN)}")
                if total_levels_gained > 0:
                    print(f"{colorize('Levels Gained:', Colors.BRIGHT_YELLOW)} {colorize(str(total_levels_gained), Colors.BRIGHT_YELLOW + Colors.BOLD)}")
                if player.stat_points > 0:
                    print(f"{colorize('Banked Stat Points:', Colors.BRIGHT_YELLOW)} {colorize(str(player.stat_points), Colors.BRIGHT_YELLOW + Colors.BOLD)}")
                print(f"\n{colorize('Press Enter to stop training', Colors.YELLOW)}")
                print(colorize("=" * 60, Colors.BRIGHT_CYAN))
                
                if not DEV_FLAGS['fast']:
                    time.sleep(step_delay)
            
            if not training_active:
                break
            
            # Award XP (silent mode to avoid interrupting training)
            levels = add_exp(player, xp_per_cycle, silent=True)
            total_xp_gained += xp_per_cycle
            total_levels_gained += levels
            
            # Show brief notification
            if not DEV_FLAGS['quiet']:
                show_notification(f"+{xp_per_cycle} XP", Colors.BRIGHT_GREEN, 0.3)
    
    def input_handler():
        """Handle user input to stop training"""
        nonlocal training_active
        input()  # Wait for Enter key
        training_active = False
    
    # Start input handler thread
    input_thread = threading.Thread(target=input_handler, daemon=True)
    input_thread.start()
    
    # Start training loop in main thread
    training_loop()
    
    # Show summary
    clear_screen()
    print(colorize("=" * 60, Colors.BRIGHT_CYAN))
    print(colorize("⚔️  TRAINING SESSION COMPLETE  ⚔️", Colors.BRIGHT_CYAN + Colors.BOLD))
    print(colorize("=" * 60, Colors.BRIGHT_CYAN))
    
    if total_xp_gained > 0:
        print(f"\n{colorize(f'Total XP Gained: {total_xp_gained}', Colors.BRIGHT_GREEN + Colors.BOLD)}")
        if total_levels_gained > 0:
            print(f"{colorize(f'Levels Gained: {total_levels_gained}', Colors.BRIGHT_YELLOW + Colors.BOLD)}")
            print(f"{colorize(f'Stat Points Banked: {total_levels_gained * 5}', Colors.BRIGHT_YELLOW + Colors.BOLD)}")
        if player.stat_points > 0:
            print(f"\n{colorize(f'You have {player.stat_points} banked stat points to allocate!', Colors.BRIGHT_YELLOW + Colors.BOLD)}")
            print(f"{colorize('Visit the Stats menu to allocate them.', Colors.WHITE)}")
    else:
        print(f"\n{colorize('No XP gained this session.', Colors.WHITE)}")
    
    print(colorize("\n" + "=" * 60, Colors.BRIGHT_CYAN))
    input(f"\n{colorize('Press Enter to continue...', Colors.BRIGHT_CYAN)}")

