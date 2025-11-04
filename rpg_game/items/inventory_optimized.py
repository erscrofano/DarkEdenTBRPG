"""Optimized inventory management with O(1) lookups"""
from collections import defaultdict
from typing import Dict, List, Any, Optional, Tuple


class InventoryIndex:
    """
    Efficient inventory indexing system for O(1) lookups.
    Maintains both list (for iteration) and dict (for fast lookup) representations.
    """
    
    def __init__(self):
        # List maintains insertion order
        self._items: List[Dict[str, Any]] = []
        # Index maps item keys to list indices for O(1) lookup
        self._index: Dict[Tuple, List[int]] = defaultdict(list)
        # Index for name-based lookups (for display/search)
        self._name_index: Dict[str, List[int]] = defaultdict(list)
    
    def add_item(self, item: Dict[str, Any]) -> None:
        """Add item to inventory with indexing"""
        item_key = self._get_item_key(item)
        list_index = len(self._items)
        self._items.append(item)
        
        # Index by item key
        if item_key is not None:
            self._index[item_key].append(list_index)
        
        # Index by name for search
        item_name = item.get('name', '')
        if item_name:
            self._name_index[item_name].append(list_index)
    
    def remove_item(self, item: Dict[str, Any], quantity: int = 1) -> bool:
        """Remove item(s) from inventory"""
        item_key = self._get_item_key(item)
        
        if item_key is None:
            # Non-stackable item - remove directly
            try:
                list_index = self._items.index(item)
                self._remove_at_index(list_index)
                return True
            except ValueError:
                return False
        
        # Find matching item in index
        if item_key not in self._index:
            return False
        
        # Find the item with matching key
        for list_index in self._index[item_key]:
            existing_item = self._items[list_index]
            current_qty = existing_item.get('quantity', 1)
            
            if current_qty <= quantity:
                # Remove entire stack
                self._remove_at_index(list_index)
                return True
            else:
                # Decrease quantity
                existing_item['quantity'] = current_qty - quantity
                return True
        
        return False
    
    def find_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find item in inventory (O(1) lookup)"""
        item_key = self._get_item_key(item)
        if item_key is None:
            # Non-stackable - linear search (rare case)
            try:
                return self._items[self._items.index(item)]
            except ValueError:
                return None
        
        if item_key not in self._index:
            return None
        
        list_index = self._index[item_key][0]
        return self._items[list_index]
    
    def find_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Find all items with matching name (O(1) lookup)"""
        if name not in self._name_index:
            return []
        return [self._items[i] for i in self._name_index[name]]
    
    def get_all_items(self) -> List[Dict[str, Any]]:
        """Get all items (maintains insertion order)"""
        return self._items.copy()
    
    def clear(self) -> None:
        """Clear all items and indices"""
        self._items.clear()
        self._index.clear()
        self._name_index.clear()
    
    def _remove_at_index(self, list_index: int) -> None:
        """Remove item at specific index and update indices"""
        if list_index >= len(self._items):
            return
        
        removed_item = self._items[list_index]
        item_key = self._get_item_key(removed_item)
        item_name = removed_item.get('name', '')
        
        # Remove from list
        self._items.pop(list_index)
        
        # Update all indices (shift indices after removed item)
        if item_key is not None:
            self._index[item_key].remove(list_index)
            # Update indices for items after removed one
            for key, indices in self._index.items():
                self._index[key] = [i if i < list_index else i - 1 for i in indices if i != list_index]
        
        if item_name:
            self._name_index[item_name].remove(list_index)
            # Update name indices
            for name, indices in self._name_index.items():
                self._name_index[name] = [i if i < list_index else i - 1 for i in indices if i != list_index]
    
    @staticmethod
    def _get_item_key(item: Dict[str, Any]) -> Optional[Tuple]:
        """Generate unique key for item stacking"""
        # Weapons and armor don't stack - each is unique
        if item.get('type') in ['weapon', 'armor']:
            return None
        # All other items stack by name, type, sell_value, and heal
        return (
            item.get('name'),
            item.get('type'),
            item.get('sell_value'),
            item.get('heal', 0)
        )


# Backward-compatible functions that use the optimized index
def get_item_key(item):
    """Generate a unique key for item stacking (backward compatibility)"""
    return InventoryIndex._get_item_key(item)


def add_item_to_inventory(inventory, item):
    """
    Add item to inventory with stacking support.
    Uses optimized indexing if inventory has _index attribute.
    """
    # Check if inventory has index (optimized version)
    if hasattr(inventory, '_index'):
        inventory.add_item(item)
        return
    
    # Fallback to old O(n) implementation for backward compatibility
    # Weapons and armor don't stack (unique items with potential talismans)
    if item.get('type') in ['weapon', 'armor']:
        inventory.append(item)
        return
    
    # For stackable items, check if it exists
    item_key = get_item_key(item)
    for existing_item in inventory:
        if get_item_key(existing_item) == item_key:
            # Item exists, increment quantity
            existing_item['quantity'] = existing_item.get('quantity', 1) + 1
            return
    
    # Item doesn't exist, add with quantity 1
    item['quantity'] = 1
    inventory.append(item)


def remove_item_from_inventory(inventory, item, quantity=1):
    """
    Remove item(s) from inventory, handling stacking.
    Uses optimized indexing if inventory has _index attribute.
    """
    # Check if inventory has index (optimized version)
    if hasattr(inventory, 'remove_item'):
        return inventory.remove_item(item, quantity)
    
    # Fallback to old O(n) implementation
    # For non-stackable items (weapons/armor), remove directly
    if item.get('type') in ['weapon', 'armor']:
        if item in inventory:
            inventory.remove(item)
            return True
        return False
    
    # For stackable items, find and decrease quantity
    item_key = get_item_key(item)
    for existing_item in inventory:
        if get_item_key(existing_item) == item_key:
            current_qty = existing_item.get('quantity', 1)
            if current_qty <= quantity:
                # Remove entire stack
                inventory.remove(existing_item)
                return True
            else:
                # Decrease quantity
                existing_item['quantity'] = current_qty - quantity
                return True
    return False


def get_item_quantity(item):
    """Get item quantity (defaults to 1 for backwards compatibility)"""
    return item.get('quantity', 1)

