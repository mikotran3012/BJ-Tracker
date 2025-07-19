"""
Card graphics and visual utilities.
Extracted from panels.py
"""

import tkinter as tk
from constants import normalize_rank_display


def create_seat_card_widget(rank, suit, parent):
    """Create a card widget optimized for seat display - SMALLER but clear."""
    # Determine card color based on suit
    if suit in ['♥', '♦']:
        card_color = '#ff4444'  # Red
    else:
        card_color = 'black'

    # Display rank (show 10 instead of T)
    display_rank = normalize_rank_display(rank)

    # Create card frame - SMALLER for compact seats
    card_frame = tk.Frame(parent, bg='white', bd=1, relief=tk.RAISED, width=25, height=35)
    card_frame.pack_propagate(False)
    card_frame.pack(side=tk.LEFT, padx=1, pady=1)

    # Card rank (center) - SMALLER font
    rank_label = tk.Label(card_frame, text=display_rank, font=('Arial', 7, 'bold'),
                          fg=card_color, bg='white')
    rank_label.pack(expand=True)

    # Card suit (bottom) - SMALLER font
    suit_label = tk.Label(card_frame, text=suit, font=('Arial', 8, 'bold'),
                          fg=card_color, bg='white')
    suit_label.pack()

    return card_frame


def get_card_color(suit):
    """Get the display color for a card suit."""
    if suit in ['♥', '♦']:
        return '#ff4444'  # Red
    else:
        return 'black'


def get_card_size(context='normal'):
    """Get card size based on context."""
    sizes = {
        'normal': {'width': 60, 'height': 85},
        'small': {'width': 35, 'height': 50},
        'seat': {'width': 25, 'height': 35},
        'mini': {'width': 20, 'height': 28}
    }
    return sizes.get(context, sizes['normal'])


def create_mystery_card_widget(parent, size='normal'):
    """Create a mystery/hidden card widget."""
    dimensions = get_card_size(size)

    card_frame = tk.Frame(parent, bg='#000080', bd=2, relief=tk.RAISED,
                          width=dimensions['width'], height=dimensions['height'])
    card_frame.pack_propagate(False)
    card_frame.pack(side=tk.LEFT, padx=2, pady=2)

    # Mystery pattern
    font_size = 24 if size == 'normal' else 16 if size == 'small' else 12
    mystery_label = tk.Label(card_frame, text='?', font=('Arial', font_size, 'bold'),
                             fg='white', bg='#000080')
    mystery_label.pack(expand=True)

    return card_frame
