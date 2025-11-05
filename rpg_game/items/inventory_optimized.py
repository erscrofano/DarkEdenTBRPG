"""Optimized inventory with O(1) lookups"""
from collections import defaultdict
from typing import Dict, List, Any, Optional, Tuple


class InventoryIndex:
    """Inventory with O(1) hash-based lookups"""
    
    def __init__(self):
        self._items: List[Dict[str, Any]] = []
        self._index: Dict[Tuple, List[int]] = defaultdict(list)
        self._name_index: Dict[str, List[int]] = defaultdict(list)
    
    def add_item(self, item: Dict[str, Any]) -> None:
        """Add item with indexing"""
        item_key = self._get_item_key(item)
        list_index = len(self._items)
        self._items.append(item)
        
        if item_key is not None:
            self._index[item_key].append(list_index)
        
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
        """Find item (O(1))"""
        item_key = self._get_item_key(item)
        if item_key is None:
            try:
                return self._items[self._items.index(item)]
            except ValueError:
                return None
        
        if item_key not in self._index:
            return None
        
        list_index = self._index[item_key][0]
        return self._items[list_index]
    
    def find_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Find items by name (O(1))"""
        if name not in self._name_index:
            return []
        return [self._items[i] for i in self._name_index[name]]
    
    def get_all_items(self) -> List[Dict[str, Any]]:
        """Get all items"""
        return self._items.copy()
    
    def clear(self) -> None:
        """Clear inventory"""
        self._items.clear()
        self._index.clear()
        self._name_index.clear()
    
    def _remove_at_index(self, list_index: int) -> None:
        """Remove item at index"""
        if list_index >= len(self._items):
            return
        
        removed_item = self._items[list_index]
        item_key = self._get_item_key(removed_item)
        item_name = removed_item.get('name', '')
        
        self._items.pop(list_index)
        
        if item_key is not None:
            self._index[item_key].remove(list_index)
            for key, indices in self._index.items():
                self._index[key] = [i if i < list_index else i - 1 for i in indices if i != list_index]
        
        if item_name:
            self._name_index[item_name].remove(list_index)
            for name, indices in self._name_index.items():
                self._name_index[name] = [i if i < list_index else i - 1 for i in indices if i != list_index]
    
    @staticmethod
    def _get_item_key(item: Dict[str, Any]) -> Optional[Tuple]:
        """Generate item key"""
        if item.get('type') in ['weapon', 'armor']:
            return None
        return (item.get('name'), item.get('type'), item.get('sell_value'), item.get('heal', 0))


def get_item_key(item):
    """Generate item stacking key"""
    return InventoryIndex._get_item_key(item)


def add_item_to_inventory(inventory, item):
    """Add item with stacking"""
    if hasattr(inventory, '_index'):
        inventory.add_item(item)
        return
    
    if item.get('type') in ['weapon', 'armor']:
        inventory.append(item)
        return
    
    item_key = get_item_key(item)
    for existing_item in inventory:
        if get_item_key(existing_item) == item_key:
            existing_item['quantity'] = existing_item.get('quantity', 1) + 1
            return
    
    item['quantity'] = 1
    inventory.append(item)


def remove_item_from_inventory(inventory, item, quantity=1):
    """Remove item with stacking"""
    if hasattr(inventory, 'remove_item'):
        return inventory.remove_item(item, quantity)
    
    if item.get('type') in ['weapon', 'armor']:
        if item in inventory:
            inventory.remove(item)
            return True
        return False
    
    item_key = get_item_key(item)
    for existing_item in inventory:
        if get_item_key(existing_item) == item_key:
            current_qty = existing_item.get('quantity', 1)
            if current_qty <= quantity:
                inventory.remove(existing_item)
                return True
            else:
                existing_item['quantity'] = current_qty - quantity
                return True
    return False


def get_item_quantity(item):
    """Get item quantity"""
    return item.get('quantity', 1)

