"""pytest configuration and fixtures"""
import pytest
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_player():
    """Create a sample player for testing"""
    from rpg_game.models.player import Player
    player = Player("TestPlayer")
    return player


@pytest.fixture
def sample_item():
    """Create a sample item for testing"""
    return {
        'name': 'Test Item',
        'type': 'material',
        'sell_value': 10,
        'quantity': 1
    }


@pytest.fixture
def temp_save_dir(tmp_path):
    """Create a temporary save directory for testing"""
    save_dir = tmp_path / "test_saves"
    save_dir.mkdir()
    return save_dir
