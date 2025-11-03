"""Game state definitions and enums"""
from enum import Enum, auto


class GameState(Enum):
    """All possible game states for the state machine"""
    INITIALIZING = auto()       # Initial setup and configuration
    MAIN_MENU = auto()          # Save slot selection screen
    CHARACTER_CREATION = auto()  # Creating a new character
    LOADING_GAME = auto()       # Loading an existing save
    IN_GAME = auto()            # Active gameplay
    GAME_OVER = auto()          # Death screen
    QUITTING = auto()           # Exiting application
    
    def __str__(self):
        return self.name.lower().replace('_', ' ').title()


# Valid state transitions for validation
VALID_TRANSITIONS = {
    GameState.INITIALIZING: [GameState.MAIN_MENU],
    GameState.MAIN_MENU: [GameState.CHARACTER_CREATION, GameState.LOADING_GAME, GameState.QUITTING],
    GameState.CHARACTER_CREATION: [GameState.IN_GAME, GameState.MAIN_MENU],
    GameState.LOADING_GAME: [GameState.IN_GAME, GameState.MAIN_MENU],
    GameState.IN_GAME: [GameState.GAME_OVER, GameState.QUITTING, GameState.MAIN_MENU],
    GameState.GAME_OVER: [GameState.MAIN_MENU],
    GameState.QUITTING: []  # Terminal state
}


def validate_transition(from_state: GameState, to_state: GameState) -> bool:
    """Validate if a state transition is allowed"""
    valid_next_states = VALID_TRANSITIONS.get(from_state, [])
    return to_state in valid_next_states

