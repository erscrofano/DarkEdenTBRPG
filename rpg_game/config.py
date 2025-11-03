"""Configuration constants and developer flags"""

# Save schema version for migration support
SAVE_SCHEMA_VERSION = 3  # Increment when adding new fields

# Global developer flags
DEV_FLAGS = {
    'fast': False,      # Skip sleep delays
    'quiet': False,     # Suppress non-critical notifications
    'no_color': False,  # Disable ANSI colors
    'seed': None        # Random seed for reproducibility
}

