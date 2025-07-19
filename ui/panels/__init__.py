"""
Makes panels a Python package and provides easy imports.
"""

from .comp_panel import CompPanel
from .seat_hand_panel import SeatHandPanel
from .card_graphics import create_seat_card_widget

__all__ = [
    'CompPanel',
    'SeatHandPanel',
    'create_seat_card_widget'
]
