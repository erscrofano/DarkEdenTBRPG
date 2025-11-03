"""Inventory management functions"""


def get_item_key(item):
    """Generate a unique key for item stacking (weapons/armor don't stack)"""
    # Weapons and armor don't stack - each is unique
    if item.get('type') in ['weapon', 'armor']:
        return None  # Don't stack
    # Other items stack by name and all properties that matter
    return (item.get('name'), item.get('type'), item.get('sell_value'), item.get('heal', 0))


def add_item_to_inventory(inventory, item):
    """Add item to inventory with stacking support"""
    # Weapons and armor don't stack
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
    """Remove item(s) from inventory, handling stacking"""
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

