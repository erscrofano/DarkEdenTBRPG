"""Stat allocation system"""
from ..ui import Colors, colorize, clear_screen


def allocate_stats(player):
    """Menu for allocating stat points"""
    while player.stat_points > 0:
        clear_screen()
        print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
        print(colorize("📊  STAT ALLOCATION  📊", Colors.BRIGHT_YELLOW + Colors.BOLD))
        print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
        print(f"\n{colorize('Unallocated Points:', Colors.BRIGHT_WHITE + Colors.BOLD)} {colorize(str(player.stat_points), Colors.BRIGHT_YELLOW + Colors.BOLD)}")
        print(f"\n{colorize('YOUR CURRENT STATS:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
        print(f"  {colorize('HP Stat:', Colors.MAGENTA)} {colorize(str(player.base_hp), Colors.BRIGHT_MAGENTA)} {colorize(f'(Max HP: {player.base_hp * 10})', Colors.WHITE)}")
        print(f"  {colorize('STR:', Colors.BRIGHT_RED)} {colorize(str(player.str), Colors.BRIGHT_RED)} {colorize(f'(Max Damage: {player.get_max_attack_power()})', Colors.WHITE)}")
        print(f"  {colorize('DEX:', Colors.BRIGHT_GREEN)} {colorize(str(player.dex), Colors.BRIGHT_GREEN)} {colorize('(High Hit Chance)', Colors.WHITE)}")
        print(f"  {colorize('AGL:', Colors.BRIGHT_BLUE)} {colorize(str(player.agl), Colors.BRIGHT_BLUE)} {colorize('(Dodge Chance)', Colors.WHITE)}")
        print(colorize("\n" + "=" * 60, Colors.BRIGHT_YELLOW))
        print(f"\n{colorize('1.', Colors.WHITE)} Increase HP {colorize('(+1 HP Stat = +10 Max HP)', Colors.MAGENTA)}")
        print(f"{colorize('2.', Colors.WHITE)} Increase STR {colorize('(+1 STR = +0.5 Max Damage)', Colors.BRIGHT_RED)}")
        print(f"{colorize('3.', Colors.WHITE)} Increase DEX {colorize('(+1 DEX = Better damage rolls)', Colors.BRIGHT_GREEN)}")
        print(f"{colorize('4.', Colors.WHITE)} Increase AGL {colorize('(+1 AGL = Better dodge chance)', Colors.BRIGHT_BLUE)}")
        print(f"{colorize('5.', Colors.WHITE)} Finish {colorize('(keep remaining points for later)', Colors.YELLOW)}")
        print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
        
        choice = input(f"\n{colorize('What would you like to increase?', Colors.BRIGHT_CYAN)} ").strip()
        
        if choice == '1':
            player.base_hp += 1
            player.stat_points -= 1
            player.calculate_max_hp()
            print(f"\n✅ Increased HP Stat to {player.base_hp}!")
            input("\nPress Enter to continue...")
        elif choice == '2':
            player.str += 1
            player.stat_points -= 1
            print(f"\n✅ Increased STR to {player.str}!")
            input("\nPress Enter to continue...")
        elif choice == '3':
            player.dex += 1
            player.stat_points -= 1
            print(f"\n✅ Increased DEX to {player.dex}!")
            input("\nPress Enter to continue...")
        elif choice == '4':
            player.agl += 1
            player.stat_points -= 1
            print(f"\n✅ Increased AGL to {player.agl}!")
            input("\nPress Enter to continue...")
        elif choice == '5':
            break
        else:
            print("\n❌ Invalid choice!")
            input("\nPress Enter to continue...")

