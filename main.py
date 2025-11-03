#!/usr/bin/env python3
"""Main entry point for the RPG game"""
import sys
import argparse
import random
from rpg_game.config import DEV_FLAGS
from rpg_game.core import GameManager


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description='Terminal RPG Game')
    parser.add_argument('--fast', action='store_true', help='Skip sleep delays (fast mode)')
    parser.add_argument('--quiet', action='store_true', help='Suppress non-critical notifications')
    parser.add_argument('--no-color', action='store_true', help='Disable ANSI colors')
    parser.add_argument('--seed', type=int, help='Random seed for reproducible runs')
    parser.add_argument('--new', action='store_true', help='Start a new game (bypass menu)')
    parser.add_argument('--load', action='store_true', help='Load existing game (bypass menu)')
    parser.add_argument('--name', type=str, help='Player name (use with --new)')
    parser.add_argument('--auto', action='store_true', help='Run one encounter then quit (for CI)')
    return parser.parse_args()


def main():
    """Main entry point - sets up and runs the game manager"""
    # Create and run game manager
    manager = GameManager()
    manager.run()


if __name__ == "__main__":
    try:
        # Parse command-line arguments
        args = parse_args()
        
        # Apply developer flags
        DEV_FLAGS['fast'] = args.fast
        DEV_FLAGS['quiet'] = args.quiet
        DEV_FLAGS['no_color'] = args.no_color
        if args.seed is not None:
            DEV_FLAGS['seed'] = args.seed
            random.seed(args.seed)
        
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Game interrupted. Thanks for playing!")
        sys.exit(0)

