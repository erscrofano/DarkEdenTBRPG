"""Inventory management functions"""


def get_item_key(item):
    """Generate unique key for item stacking"""
    if item.get('type') in ['weapon', 'armor']:
        return None
    return (item.get('name'), item.get('type'), item.get('sell_value'), item.get('heal', 0))


def add_item_to_inventory(inventory, item):
    """Add item to inventory with stacking"""
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
    """Remove item(s) from inventory"""
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

