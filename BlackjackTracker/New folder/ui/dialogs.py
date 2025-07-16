# ui/dialogs.py
"""
Dialog windows for the Blackjack Tracker application.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import SEATS


class SeatSelectDialog(tk.Toplevel):
    """Dialog for selecting the player's seat at the table."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Select Your Seat")
        self.selected = tk.StringVar(value=SEATS[0])
        self.resizable(False, False)
        self.configure(bg="white")
        self._build_dialog()
        self._setup_bindings()

    def _build_dialog(self):
        """Build the dialog UI elements."""
        label = tk.Label(
            self,
            text="Choose your seat (rightmost = P1):",
            font=("Segoe UI", 11),
            bg="white"
        )
        label.pack(pady=(14, 2))

        radio_row = tk.Frame(self, bg="white")
        radio_row.pack(pady=(2, 8), padx=14)

        for seat in SEATS:
            rb = tk.Radiobutton(
                radio_row,
                text=seat,
                variable=self.selected,
                value=seat,
                bg="white"
            )
            rb.pack(side=tk.LEFT, padx=7)

        ok_btn = ttk.Button(self, text="OK", command=self.on_ok)
        ok_btn.pack(pady=(0, 8))

    def _setup_bindings(self):
        """Setup keyboard and window bindings."""
        self.bind("<Return>", lambda e: self.on_ok())
        self.grab_set()
        self.transient(self.master)
        self.wait_window(self)

    def on_ok(self):
        """Handle OK button click."""
        self.destroy()


class SuitSelectDialog(tk.Toplevel):
    """Dialog for selecting a card suit."""

    def __init__(self, parent, on_suit_selected):
        super().__init__(parent)
        self.title("Suit")
        self.geometry("+600+340")
        self.on_suit_selected = on_suit_selected
        self._build_dialog()

    def _build_dialog(self):
        """Build the suit selection buttons."""
        from constants import SUITS, COLORS

        for i, suit in enumerate(SUITS):
            color = self._get_suit_color(suit)
            btn = tk.Button(
                self,
                text=suit,
                font=('Segoe UI', 16, 'bold'),
                width=3,
                fg=color,
                command=lambda s=suit: self._pick_suit(s)
            )
            btn.grid(row=0, column=i, padx=6, pady=8)

        self.grab_set()
        self.transient(self.master)
        self.wait_window()

    def _get_suit_color(self, suit):
        """Get the display color for a suit."""
        from constants import COLORS

        color_map = {
            '♥': COLORS['suit_heart'],
            '♦': COLORS['suit_diamond'],
            '♣': COLORS['suit_club'],
            '♠': COLORS['suit_spade']
        }
        return color_map.get(suit, COLORS['suit_spade'])

    def _pick_suit(self, suit):
        """Handle suit selection."""
        self.destroy()
        self.on_suit_selected(suit)
