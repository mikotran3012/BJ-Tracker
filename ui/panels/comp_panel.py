"""
Card composition and deck penetration panel.
Extracted from panels.py for better organization.
"""

import tkinter as tk
from constants import RANKS, COLORS, normalize_rank_display, normalize_rank_internal


class CompPanel(tk.Frame):
    """Panel showing card composition and deck penetration - COMPACT VERSION."""

    def __init__(self, parent, on_decks_change, initial_decks=8):
        super().__init__(parent, bg=COLORS['bg_white'], bd=2, relief=tk.GROOVE,
                         width=600, height=100)
        self.pack_propagate(False)
        self.decks = initial_decks
        self.on_decks_change = on_decks_change
        # Use internal T for tracking, but display as 10
        self.comp = {r: 0 for r in ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']}
        self._build_panel()
        self.update_display()

    def _build_panel(self):
        """Build the COMPACT composition panel UI."""
        # Left side: Shoe information
        shoe = tk.Frame(self, bg=COLORS['bg_white'])
        shoe.grid(row=0, column=0, rowspan=2, sticky='nsw', padx=2, pady=1)

        # Deck selector
        deck_frame = tk.Frame(shoe, bg=COLORS['bg_white'])
        deck_frame.pack()
        tk.Label(deck_frame, text='Decks', font=('Segoe UI', 8, 'bold'),
                 bg=COLORS['bg_white']).pack(side=tk.LEFT)
        self.deck_var = tk.IntVar(value=self.decks)
        dspin = tk.Spinbox(
            deck_frame, from_=1, to=8, width=2,
            textvariable=self.deck_var,
            font=('Segoe UI', 10),
            command=self.set_decks,
            justify='center'
        )
        dspin.pack(side=tk.LEFT, padx=2)

        # Cards remaining
        cards_frame = tk.Frame(shoe, bg=COLORS['bg_white'])
        cards_frame.pack()
        tk.Label(cards_frame, text='Left:', font=('Segoe UI', 8, 'bold'),
                 bg=COLORS['bg_white']).pack(side=tk.LEFT)
        self.cards_left_label = tk.Label(
            cards_frame, text="416",
            font=('Segoe UI', 11, 'bold'),
            fg=COLORS['fg_blue'],
            bg=COLORS['bg_white']
        )
        self.cards_left_label.pack(side=tk.LEFT, padx=2)

        # Penetration
        pen_frame = tk.Frame(shoe, bg=COLORS['bg_white'])
        pen_frame.pack()
        tk.Label(pen_frame, text='Pen:', font=('Segoe UI', 8, 'bold'),
                 bg=COLORS['bg_white']).pack(side=tk.LEFT)
        self.pen_bar = tk.Canvas(
            pen_frame, width=40, height=10,
            bg='#e0e0e0', bd=1,
            highlightthickness=0
        )
        self.pen_bar.pack(side=tk.LEFT, padx=2)
        self.pen_label = tk.Label(pen_frame, text="0.0%", font=('Segoe UI', 8, 'bold'),
                                  bg=COLORS['bg_white'])
        self.pen_label.pack(side=tk.LEFT, padx=1)

        # Right side: Card composition grid
        self._build_composition_grid()

    def _build_composition_grid(self):
        """Build the card composition display grid - COMPACT VERSION."""
        # Rank headers
        display_ranks = [normalize_rank_display(r) for r in
                         ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']]
        for ci, r in enumerate(display_ranks):
            tk.Label(
                self, text=r,
                font=('Segoe UI', 9, 'bold'),
                bg=COLORS['bg_white'],
                width=2
            ).grid(row=0, column=ci + 1, padx=1, pady=1)

        # Combined composition/remaining row
        internal_ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']

        self.comp_labels = {}
        self.rem_labels = {}

        for ci, r in enumerate(internal_ranks):
            # Create frame for both dealt and remaining
            cell_frame = tk.Frame(self, bg=COLORS['bg_white'])
            cell_frame.grid(row=1, column=ci + 1, padx=1, pady=1)

            # Dealt count (top)
            dealt_lbl = tk.Label(
                cell_frame, text='0',
                font=('Segoe UI', 8, 'bold'),
                width=2, height=1,
                fg=COLORS['fg_comp_cell'],
                bg=COLORS['bg_comp_cell'],
                bd=1, relief=tk.SUNKEN
            )
            dealt_lbl.pack()
            self.comp_labels[r] = dealt_lbl

            # Remaining count (bottom)
            remain_lbl = tk.Label(
                cell_frame, text='32',
                font=('Segoe UI', 8, 'bold'),
                width=2, height=1,
                fg=COLORS['fg_white'],
                bg=COLORS['bg_rem_cell'],
                bd=1, relief=tk.SUNKEN
            )
            remain_lbl.pack()
            self.rem_labels[r] = remain_lbl

    def update_display(self):
        """Update all display elements."""
        d = self.decks
        internal_ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']

        # Update composition and remaining counts
        for r in internal_ranks:
            dealt = self.comp[r]
            remain = d * 4 - dealt
            self.comp_labels[r].config(text=str(dealt))
            self.rem_labels[r].config(text=str(remain))

        # Update cards remaining
        cards_rem = self.cards_left()
        self.cards_left_label.config(text=str(cards_rem))

        # Update penetration bar
        pct, seen, total = self.penetration()
        self.pen_bar.delete("all")
        if total > 0:
            width = int((pct / 100) * 40)
            self.pen_bar.create_rectangle(0, 0, width, 10, fill=COLORS['fg_dealer'], outline="")
        self.pen_label.config(text=f"{pct:.1f}%")

    def set_decks(self):
        """Handle deck count change."""
        self.decks = self.deck_var.get()
        self.reset()
        self.on_decks_change()

    def reset(self):
        """Reset all composition counts."""
        self.comp = {r: 0 for r in ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']}
        self.update_display()

    def log_card(self, rank):
        """Log a dealt card - convert 10 to T internally."""
        internal_rank = normalize_rank_internal(rank)
        if internal_rank != "?":  # Don't log mystery cards
            self.comp[internal_rank] += 1
            self.update_display()

    def undo_card(self, rank):
        """Undo a dealt card - convert 10 to T internally."""
        internal_rank = normalize_rank_internal(rank)
        if internal_rank != "?" and self.comp[internal_rank] > 0:
            self.comp[internal_rank] -= 1
            self.update_display()

    def cards_left(self):
        """Calculate cards remaining in shoe."""
        return sum(
            self.decks * 4 - self.comp[r] for r in ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K'])

    def penetration(self):
        """Calculate penetration percentage."""
        seen = sum(self.comp.values())
        total = self.decks * 52
        pct = (seen / total) * 100 if total > 0 else 0
        return pct, seen, total
