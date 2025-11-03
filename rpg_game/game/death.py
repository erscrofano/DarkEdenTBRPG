"""Death and game over system"""
import time
from ..ui import Colors, colorize, clear_screen


def show_death_screen(player, enemy_name=None):
    """
    Display game over screen with statistics.
    Player must reload from a save slot.
    Returns: False to signal game over
    """
    # Small pause before clearing screen so player can see immediate death message
    time.sleep(2)
    
    clear_screen()
    
    # Dramatic death screen
    print(colorize("=" * 70, Colors.BRIGHT_RED))
    print(colorize("╔══════════════════════════════════════════════════════════════════╗", Colors.BRIGHT_RED + Colors.BOLD))
    print(colorize("║                                                                  ║", Colors.BRIGHT_RED + Colors.BOLD))
    print(colorize("║                        💀  GAME OVER  💀                         ║", Colors.BRIGHT_RED + Colors.BOLD))
    print(colorize("║                                                                  ║", Colors.BRIGHT_RED + Colors.BOLD))
    print(colorize("╚══════════════════════════════════════════════════════════════════╝", Colors.BRIGHT_RED + Colors.BOLD))
    print(colorize("=" * 70, Colors.BRIGHT_RED))
    
    print(f"\n{colorize('💔', Colors.BRIGHT_RED)} {colorize(f'{player.name} has fallen in battle...', Colors.WHITE + Colors.BOLD)}")
    
    if enemy_name:
        print(f"\n{colorize('⚔️', Colors.YELLOW)} {colorize('Defeated by:', Colors.WHITE)} {colorize(enemy_name, Colors.BRIGHT_RED + Colors.BOLD)}")
    
    print(f"\n{colorize('━' * 70, Colors.RED)}")
    print(f"\n{colorize('⚠️', Colors.BRIGHT_YELLOW)} {colorize('Progress Lost — Load your last save to continue.', Colors.WHITE)}")
    print(f"\n{colorize('💡', Colors.BRIGHT_CYAN)} {colorize('Tip: Save often and heal before your HP runs low!', Colors.WHITE)}")
    print(f"\n{colorize('━' * 70, Colors.RED)}")
    
    input(f"\n{colorize('Press Enter to return to the main menu...', Colors.BRIGHT_WHITE + Colors.BOLD)}")
    
    # Return False to signal game over
    return False


def handle_combat_death(player, enemy_name):
    """
    Handle death during combat with proper error handling.
    Shows immediate death message, then full game over screen.
    Returns: False to signal combat loss and game over
    """
    try:
        # Show immediate defeat message with slight pause for readability
        print(f"\n{colorize('━' * 60, Colors.BRIGHT_RED)}")
        print(f"{colorize('💀', Colors.BRIGHT_RED + Colors.BOLD)} {colorize('YOU HAVE BEEN DEFEATED!', Colors.BRIGHT_RED + Colors.BOLD)} {colorize('💀', Colors.BRIGHT_RED + Colors.BOLD)}")
        print(f"{colorize('━' * 60, Colors.BRIGHT_RED)}")
        
        # Show kill streak loss if applicable
        if player.kill_streak > 0:
            print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(f'Kill streak lost: {player.kill_streak}', Colors.YELLOW)}")
        
        input(f"\n{colorize('Press Enter to view results...', Colors.WHITE)}")
        
        # Show full death screen and handle game over
        return show_death_screen(player, enemy_name)
        
    except Exception as e:
        # Fallback error handling
        from ..utils.logging import log_error
        log_error(f"Error in death handler: {e}", exc_info=True)
        print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize('An error occurred. Returning to menu...', Colors.WHITE)}")
        return False

