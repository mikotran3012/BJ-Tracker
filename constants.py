# constants.py
"""
Constants and configuration for the Blackjack Tracker application.
UPDATED: T changed to 10 for better readability
"""

# Card definitions - CHANGED: T → 10
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
SUITS = ['♠', '♥', '♦', '♣']
SUIT_KEYS = {'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣'}

# Table configuration
SEATS = ['P7', 'P6', 'P5', 'P4', 'P3', 'P2', 'P1']  # Left to right; rightmost is P1
DEFAULT_DECKS = 8

# UI Colors
COLORS = {
    'bg_main': '#202645',
    'bg_panel': '#222',
    'bg_input': '#2a3047',
    'bg_white': 'white',
    'fg_white': 'white',
    'fg_black': 'black',
    'fg_blue': '#1565c0',
    'fg_green': '#26734d',
    'fg_player': '#004d1a',
    'fg_dealer': '#1565c0',
    'bg_your_seat': '#858585',
    'bg_active_seat': '#ffae42',
    'bg_normal_seat': '#2b354d',
    'bg_comp_cell': '#cfd8dc',
    'fg_comp_cell': '#1976d2',
    'bg_rem_cell': '#222',
    'suit_heart': '#ff4d4d',
    'suit_diamond': '#40e0d0',
    'suit_club': '#90ee90',
    'suit_spade': 'white'
}


# Utility functions
def total_cards(decks):
    return decks * 52


# Helper function to normalize rank display
def normalize_rank_display(rank):
    """Convert T to 10 for display purposes."""
    return '10' if rank == 'T' else rank


# Helper function to normalize rank for internal logic
def normalize_rank_internal(rank):
    """Convert 10 to T for internal logic compatibility."""
    return 'T' if rank == '10' else rank
