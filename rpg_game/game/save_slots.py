"""Save slot selection and management"""
from ..ui import Colors, colorize, clear_screen
from ..save.system import list_save_slots, delete_save_slot, sanitize_slot_name
from ..constants import DEFAULT_SAVE_SLOT, MAX_SAVE_SLOT_NAME_LENGTH


def select_save_slot_menu(allow_new=True, allow_delete=False):
    """
    Display menu for selecting a save slot.
    
    Args:
        allow_new: If True, allow creating new save slots
        allow_delete: If True, allow deleting save slots
    
    Returns:
        Tuple of (slot_name, is_new) where is_new indicates if this is a new slot
        Returns (None, None) if user cancelled
    """
    while True:
        clear_screen()
        slots = list_save_slots()
        
        print(colorize("=" * 60, Colors.BRIGHT_CYAN))
        print(colorize("💾  SAVE SLOT SELECTION  💾", Colors.BRIGHT_CYAN + Colors.BOLD))
        print(colorize("=" * 60, Colors.BRIGHT_CYAN))
        
        if slots:
            print(f"\n{colorize('AVAILABLE SAVE SLOTS:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
            print(colorize("─" * 60, Colors.CYAN))
            
            for i, slot in enumerate(slots, 1):
                slot_name = slot['slot_name']
                player_name = slot['player_name']
                level = slot['level']
                
                # Highlight default slot
                if slot_name == DEFAULT_SAVE_SLOT:
                    slot_display = f"{colorize(str(i) + '.', Colors.BRIGHT_GREEN)} {colorize(slot_name, Colors.BRIGHT_GREEN + Colors.BOLD)}"
                else:
                    slot_display = f"{colorize(str(i) + '.', Colors.WHITE)} {colorize(slot_name, Colors.CYAN)}"
                
                # Show player info if available
                if player_name != 'Corrupted Save':
                    player_info = f"{colorize(f'({player_name} - Level {level})', Colors.WHITE)}"
                    print(f"  {slot_display} {player_info}")
                else:
                    corrupted_info = colorize("(Corrupted Save)", Colors.RED)
                    print(f"  {slot_display} {corrupted_info}")
        else:
            print(f"\n{colorize('No save slots found.', Colors.YELLOW)}")
        
        # Build menu options
        menu_items = []
        next_num = len(slots) + 1
        
        if allow_new:
            menu_items.append(('new', f"{colorize(str(next_num) + '.', Colors.BRIGHT_GREEN)} {colorize('Create New Save Slot', Colors.BRIGHT_GREEN)}"))
            next_num += 1
        
        if allow_delete and slots:
            menu_items.append(('delete', f"{colorize(str(next_num) + '.', Colors.BRIGHT_RED)} {colorize('Delete Save Slot', Colors.BRIGHT_RED)}"))
            next_num += 1
        
        menu_items.append(('cancel', f"{colorize(str(next_num) + '.', Colors.WHITE)} {colorize('Cancel', Colors.WHITE)}"))
        
        # Display menu options with separator
        if slots or menu_items:
            print()
            print(colorize("─" * 60, Colors.CYAN))
            if slots:
                print(f"\n{colorize('OPTIONS:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
            else:
                print()
            for action, text in menu_items:
                print(f"  {text}")
        
        print()
        print(colorize("=" * 60, Colors.BRIGHT_CYAN))
        
        choice = input(f"\n{colorize('Select an option:', Colors.BRIGHT_CYAN)} ").strip()
        
        try:
            choice_num = int(choice)
            
            # Check if selecting an existing slot
            if 1 <= choice_num <= len(slots):
                selected_slot = slots[choice_num - 1]
                return selected_slot['slot_name'], False
            
            # Check menu options
            offset = len(slots)
            if allow_new and choice_num == offset + 1:
                # Create new slot
                new_slot = create_new_save_slot()
                if new_slot:
                    return new_slot, True
                continue
            
            if allow_delete and slots and choice_num == offset + (2 if allow_new else 1):
                # Delete slot
                deleted = delete_save_slot_menu(slots)
                if deleted is None:
                    continue
                # Refresh and continue
                continue
            
            # Cancel
            if choice_num == next_num:
                return None, None
            
            print(f"\n{colorize('❌ Invalid choice!', Colors.BRIGHT_RED)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
        
        except ValueError:
            print(f"\n{colorize('❌ Invalid input! Please enter a number.', Colors.BRIGHT_RED)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")


def create_new_save_slot():
    """Prompt user to create a new save slot"""
    clear_screen()
    print(colorize("=" * 60, Colors.BRIGHT_CYAN))
    print(colorize("✨  CREATE NEW SAVE SLOT  ✨", Colors.BRIGHT_GREEN + Colors.BOLD))
    print(colorize("=" * 60, Colors.BRIGHT_CYAN))
    print()
    
    # Format the message with the constant value
    max_length_msg = f"Enter a name for your save slot (max {MAX_SAVE_SLOT_NAME_LENGTH} characters)"
    print(f"{colorize(max_length_msg, Colors.WHITE)}")
    print(f"{colorize('Allowed characters: letters, numbers, spaces, dashes, underscores', Colors.GRAY)}")
    print(f"{colorize(f'Press Enter to use default name ({DEFAULT_SAVE_SLOT})', Colors.GRAY)}")
    print()
    print(colorize("─" * 60, Colors.CYAN))
    
    while True:
        slot_name = input(f"\n{colorize('Save slot name:', Colors.BRIGHT_CYAN)} ").strip()
        
        if not slot_name:
            # Use default
            slot_name = DEFAULT_SAVE_SLOT
        
        # Sanitize the slot name
        sanitized = sanitize_slot_name(slot_name)
        
        # Check if slot already exists
        existing_slots = list_save_slots()
        if any(s['slot_name'] == sanitized for s in existing_slots):
            print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(f'A save slot named "{sanitized}" already exists!', Colors.WHITE)}")
            retry = input(f"{colorize('Try again? (y/n): ', Colors.WHITE)}").strip().lower()
            if retry != 'y':
                return None
            # Re-display the prompt
            print()
            print(colorize("─" * 60, Colors.CYAN))
            continue
        
        # Validate length
        if len(sanitized) > MAX_SAVE_SLOT_NAME_LENGTH:
            max_len_msg = f'Name is too long (max {MAX_SAVE_SLOT_NAME_LENGTH} characters)'
            print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(max_len_msg, Colors.WHITE)}")
            print()
            print(colorize("─" * 60, Colors.CYAN))
            continue
        
        # Confirm if using sanitized version
        if sanitized != slot_name:
            print(f"\n{colorize('⚠️', Colors.YELLOW)} {colorize(f'Name sanitized to: "{sanitized}"', Colors.WHITE)}")
            confirm = input(f"{colorize('Use this name? (y/n): ', Colors.WHITE)}").strip().lower()
            if confirm != 'y':
                print()
                print(colorize("─" * 60, Colors.CYAN))
                continue
        
        # Success
        print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(f'Save slot "{sanitized}" created!', Colors.BRIGHT_GREEN)}")
        return sanitized


def delete_save_slot_menu(slots):
    """Menu for deleting a save slot"""
    print(f"\n{colorize('DELETE SAVE SLOT', Colors.BRIGHT_RED + Colors.BOLD)}")
    print(colorize("─" * 60, Colors.CYAN))
    print(f"{colorize('⚠️  WARNING: This action cannot be undone!  ⚠️', Colors.BRIGHT_RED + Colors.BOLD)}")
    print(colorize("─" * 60, Colors.CYAN))
    
    for i, slot in enumerate(slots, 1):
        slot_name = slot['slot_name']
        player_name = slot['player_name']
        level = slot['level']
        
        if player_name != 'Corrupted Save':
            info = f"{colorize(f'({player_name} - Level {level})', Colors.WHITE)}"
        else:
            info = colorize("(Corrupted Save)", Colors.RED)
        
        print(f"  {colorize(str(i) + '.', Colors.WHITE)} {colorize(slot_name, Colors.CYAN)} {info}")
    
    print(f"  {colorize(str(len(slots) + 1) + '.', Colors.WHITE)} Cancel")
    print(colorize("─" * 60, Colors.CYAN))
    
    choice = input(f"\n{colorize('Select slot to delete:', Colors.BRIGHT_RED)} ").strip()
    
    try:
        choice_num = int(choice)
        
        if choice_num == len(slots) + 1:
            return None  # Cancelled
        
        if 1 <= choice_num <= len(slots):
            slot_to_delete = slots[choice_num - 1]
            slot_name = slot_to_delete['slot_name']
            
            # Confirm deletion
            print(f"\n{colorize('⚠️', Colors.BRIGHT_RED)} {colorize(f'Are you sure you want to delete save slot "{slot_name}"?', Colors.WHITE)}")
            print(f"{colorize('This will permanently delete all data for this character!', Colors.BRIGHT_RED)}")
            confirm = input(f"\n{colorize('Type DELETE to confirm, or press Enter to cancel: ', Colors.BRIGHT_RED)}").strip()
            
            if confirm.upper() == 'DELETE':
                if delete_save_slot(slot_name):
                    print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(f'Save slot "{slot_name}" deleted successfully!', Colors.BRIGHT_GREEN)}")
                    input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                    return True
                else:
                    print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(f'Failed to delete save slot "{slot_name}"!', Colors.WHITE)}")
                    input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                    return False
            else:
                return None  # Cancelled
        
        print(f"\n{colorize('❌ Invalid choice!', Colors.BRIGHT_RED)}")
        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
        return None
    
    except ValueError:
        print(f"\n{colorize('❌ Invalid input!', Colors.BRIGHT_RED)}")
        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
        return None


def rename_save_slot_menu():
    """Menu to rename an existing save slot"""
    from ..save.system import list_save_slots, load_game, save_game, delete_save_slot
    import os
    
    clear_screen()
    print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
    print(colorize("✏️  RENAME SAVE SLOT  ✏️", Colors.BRIGHT_YELLOW + Colors.BOLD))
    print(colorize("=" * 60, Colors.BRIGHT_YELLOW))
    
    existing_slots = list_save_slots()
    
    if not existing_slots:
        print(f"\n{colorize('No save slots found!', Colors.BRIGHT_RED)}")
        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
        return
    
    print(f"\n{colorize('AVAILABLE SLOTS:', Colors.BRIGHT_WHITE + Colors.BOLD)}")
    print(colorize("─" * 60, Colors.BRIGHT_YELLOW))
    
    for idx, slot_info in enumerate(existing_slots, 1):
        slot_name = slot_info['slot_name']
        char_name = slot_info.get('character_name', 'Unknown')
        level = slot_info.get('level', '?')
        print(f"  {colorize(f'{idx}.', Colors.WHITE)} {slot_name} ({char_name} - Level {level})")
    
    print(colorize("─" * 60, Colors.BRIGHT_YELLOW))
    print(f"  {colorize(f'{len(existing_slots) + 1}.', Colors.WHITE)} Cancel")
    
    try:
        choice = input(f"\n{colorize('Select slot to rename: ', Colors.BRIGHT_YELLOW)}").strip()
        choice_num = int(choice)
        
        if choice_num == len(existing_slots) + 1:
            return
        
        if 1 <= choice_num <= len(existing_slots):
            old_slot_name = existing_slots[choice_num - 1]['slot_name']
            
            print(f"\n{colorize(f'Renaming slot: {old_slot_name}', Colors.CYAN)}")
            new_name = input(f"{colorize('Enter new slot name: ', Colors.BRIGHT_YELLOW)}").strip()
            
            if not new_name:
                print(f"\n{colorize('❌ Name cannot be empty!', Colors.BRIGHT_RED)}")
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                return
            
            # Sanitize new name
            from ..save.system import sanitize_slot_name
            sanitized = sanitize_slot_name(new_name)
            
            if sanitized != new_name:
                sanitized_msg = f'Name sanitized to: "{sanitized}"'
                print(f"\n{colorize('⚠️', Colors.YELLOW)} {colorize(sanitized_msg, Colors.WHITE)}")
            
            # Check if new name already exists
            if any(s['slot_name'] == sanitized for s in existing_slots if s['slot_name'] != old_slot_name):
                exists_msg = f'A save slot named "{sanitized}" already exists!'
                print(f"\n{colorize('❌', Colors.BRIGHT_RED)} {colorize(exists_msg, Colors.WHITE)}")
                input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
                return
            
            # Load the save, update slot name, save to new slot, delete old
            player = load_game(old_slot_name)
            if player:
                player.save_slot = sanitized
                save_game(player, sanitized)
                delete_save_slot(old_slot_name)
                
                success_msg = f'Slot renamed from "{old_slot_name}" to "{sanitized}"!'
                print(f"\n{colorize('✅', Colors.BRIGHT_GREEN)} {colorize(success_msg, Colors.BRIGHT_GREEN)}")
            else:
                print(f"\n{colorize('❌ Failed to load save slot!', Colors.BRIGHT_RED)}")
            
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
        else:
            print(f"\n{colorize('❌ Invalid choice!', Colors.BRIGHT_RED)}")
            input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")
    
    except ValueError:
        print(f"\n{colorize('❌ Invalid input!', Colors.BRIGHT_RED)}")
        input(f"\n{colorize('Press Enter to continue...', Colors.WHITE)}")

