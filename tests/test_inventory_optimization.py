"""Unit tests for inventory optimization"""
import pytest
from rpg_game.items.inventory_optimized import InventoryIndex, add_item_to_inventory, remove_item_from_inventory


class TestInventoryOptimization:
    """Test inventory optimization features"""
    
    def test_inventory_index_add_item(self):
        """Test adding items to optimized inventory"""
        index = InventoryIndex()
        item = {'name': 'Test Item', 'type': 'material', 'sell_value': 10}
        
        index.add_item(item)
        assert len(index.get_all_items()) == 1
        
        # Add same item again (should stack)
        item2 = {'name': 'Test Item', 'type': 'material', 'sell_value': 10}
        index.add_item(item2)
        items = index.get_all_items()
        assert len(items) == 1
        assert items[0]['quantity'] == 2
    
    def test_inventory_index_find_item(self):
        """Test O(1) item lookup"""
        index = InventoryIndex()
        item = {'name': 'Test Item', 'type': 'material', 'sell_value': 10}
        index.add_item(item)
        
        found = index.find_item(item)
        assert found is not None
        assert found['name'] == 'Test Item'
    
    def test_inventory_index_remove_item(self):
        """Test removing items from optimized inventory"""
        index = InventoryIndex()
        item = {'name': 'Test Item', 'type': 'material', 'sell_value': 10}
        index.add_item(item)
        index.add_item(item.copy())  # Stack to quantity 2
        
        removed = index.remove_item(item, quantity=1)
        assert removed is True
        items = index.get_all_items()
        assert len(items) == 1
        assert items[0]['quantity'] == 1
    
    def test_backward_compatibility(self):
        """Test backward compatibility with old inventory API"""
        inventory = []
        item = {'name': 'Test Item', 'type': 'material', 'sell_value': 10}
        
        add_item_to_inventory(inventory, item)
        assert len(inventory) == 1
        
        removed = remove_item_from_inventory(inventory, item)
        assert removed is True
        assert len(inventory) == 0

