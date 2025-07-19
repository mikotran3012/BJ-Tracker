"""
ENLARGED Card composition and deck penetration panel.
Made bigger and more readable with larger fonts and better spacing.
"""

import tkinter as tk
from constants import RANKS, COLORS, normalize_rank_display, normalize_rank_internal


class CompPanel(tk.Frame):
    """ENLARGED Panel showing card composition and deck penetration."""

    def __init__(self, parent, on_decks_change, initial_decks=8):
        # ENLARGED: Increased width and height for better readability
        super().__init__(parent, bg=COLORS['bg_white'], bd=3, relief=tk.GROOVE,
                         width=750, height=130)  # Increased from 600x100
        self.pack_propagate(False)
        self.decks = initial_decks
        self.on_decks_change = on_decks_change
        # Use internal T for tracking, but display as 10
        self.comp = {r: 0 for r in ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']}
        self._build_panel()
        self.update_display()

    def _build_panel(self):
        """Build the ENLARGED composition panel UI."""
        # Left side: Shoe information with LARGER fonts
        shoe = tk.Frame(self, bg=COLORS['bg_white'])
        shoe.grid(row=0, column=0, rowspan=2, sticky='nsw', padx=8, pady=6)  # More padding

        # ENLARGED: Deck selector with bigger font
        deck_frame = tk.Frame(shoe, bg=COLORS['bg_white'])
        deck_frame.pack(pady=2)
        tk.Label(deck_frame, text='Decks', font=('Segoe UI', 10, 'bold'),  # Larger font
                 bg=COLORS['bg_white']).pack(side=tk.LEFT)
        self.deck_var = tk.IntVar(value=self.decks)
        dspin = tk.Spinbox(
            deck_frame, from_=1, to=8, width=3,  # Wider spinbox
            textvariable=self.deck_var,
            font=('Segoe UI', 12, 'bold'),  # Larger font
            command=self.set_decks,
            justify='center'
        )
        dspin.pack(side=tk.LEFT, padx=4)

        # ENLARGED: Cards remaining with bigger font
        cards_frame = tk.Frame(shoe, bg=COLORS['bg_white'])
        cards_frame.pack(pady=2)
        tk.Label(cards_frame, text='Left:', font=('Segoe UI', 10, 'bold'),  # Larger font
                 bg=COLORS['bg_white']).pack(side=tk.LEFT)
        self.cards_left_label = tk.Label(
            cards_frame, text="416",
            font=('Segoe UI', 14, 'bold'),  # Much larger font
            fg=COLORS['fg_blue'],
            bg=COLORS['bg_white']
        )
        self.cards_left_label.pack(side=tk.LEFT, padx=4)

        # ENLARGED: Penetration with bigger components
        pen_frame = tk.Frame(shoe, bg=COLORS['bg_white'])
        pen_frame.pack(pady=2)
        tk.Label(pen_frame, text='Pen:', font=('Segoe UI', 10, 'bold'),  # Larger font
                 bg=COLORS['bg_white']).pack(side=tk.LEFT)
        self.pen_bar = tk.Canvas(
            pen_frame, width=60, height=15,  # Larger penetration bar
            bg='#e0e0e0', bd=2,  # Thicker border
            highlightthickness=0
        )
        self.pen_bar.pack(side=tk.LEFT, padx=4)
        self.pen_label = tk.Label(pen_frame, text="0.0%", font=('Segoe UI', 10, 'bold'),  # Larger font
                                  bg=COLORS['bg_white'])
        self.pen_label.pack(side=tk.LEFT, padx=2)

        # Right side: ENLARGED Card composition grid
        self._build_composition_grid()

    def _build_composition_grid(self):
        """Build the ENLARGED card composition display grid."""
        # ENLARGED: Rank headers with bigger fonts
        display_ranks = [normalize_rank_display(r) for r in
                         ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']]
        for ci, r in enumerate(display_ranks):
            tk.Label(
                self, text=r,
                font=('Segoe UI', 11, 'bold'),  # Larger font
                bg=COLORS['bg_white'],
                width=3,  # Wider cells
                height=2  # Taller cells
            ).grid(row=0, column=ci + 1, padx=2, pady=2)  # More padding

        # ENLARGED: Combined composition/remaining row
        internal_ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']

        self.comp_labels = {}
        self.rem_labels = {}

        for ci, r in enumerate(internal_ranks):
            # ENLARGED: Create bigger frame for both dealt and remaining
            cell_frame = tk.Frame(self, bg=COLORS['bg_white'])
            cell_frame.grid(row=1, column=ci + 1, padx=2, pady=2)  # More padding

            # ENLARGED: Dealt count (top) with bigger font and size
            dealt_lbl = tk.Label(
                cell_frame, text='0',
                font=('Segoe UI', 10, 'bold'),  # Larger font
                width=3, height=2,  # Bigger cells
                fg=COLORS['fg_comp_cell'],
                bg=COLORS['bg_comp_cell'],
                bd=2, relief=tk.SUNKEN  # Thicker border
            )
            dealt_lbl.pack(pady=1)
            self.comp_labels[r] = dealt_lbl

            # ENLARGED: Remaining count (bottom) with bigger font and size
            remain_lbl = tk.Label(
                cell_frame, text='32',
                font=('Segoe UI', 10, 'bold'),  # Larger font
                width=3, height=2,  # Bigger cells
                fg=COLORS['fg_white'],
                bg=COLORS['bg_rem_cell'],
                bd=2, relief=tk.SUNKEN  # Thicker border
            )
            remain_lbl.pack(pady=1)
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

        # Update ENLARGED penetration bar
        pct, seen, total = self.penetration()
        self.pen_bar.delete("all")
        if total > 0:
            width = int((pct / 100) * 60)  # Adjusted for larger bar
            self.pen_bar.create_rectangle(0, 0, width, 15, fill=COLORS['fg_dealer'], outline="")
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