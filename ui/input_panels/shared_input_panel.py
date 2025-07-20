import tkinter as tk
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from constants import RANKS, COLORS, normalize_rank_display
from .suit_selection import get_suit_selection


class SharedInputPanel(tk.Frame):
    """SIMPLE shared input panel - just make it work."""

    def __init__(self, parent, on_card, on_undo):
        super().__init__(parent, bg=COLORS['bg_input'])
        self.on_card = on_card
        self.on_undo = on_undo
        self.on_stand = None
        self.on_split = None
        self._build_panel()

    def _build_panel(self):
        """Build the panel - COMPACT version with smaller buttons."""
        # First row: Rank buttons - COMPACT
        rank_frame = tk.Frame(self, bg=COLORS['bg_input'])
        rank_frame.pack(pady=1)  # Reduced from pady=2

        self.rank_btns = []

        # Rank buttons - SMALLER and CLOSER
        for ri, r in enumerate(RANKS):
            display_rank = normalize_rank_display(r)  # Show 10 instead of T
            b = tk.Button(
                rank_frame,
                text=display_rank,
                width=1 if r != '10' else 2,
                height=1,  # Explicit small height
                font=('Segoe UI', 8),
                command=lambda rank=r: self.rank_clicked(rank)
            )
            b.grid(row=0, column=ri, padx=1)
            self.rank_btns.append(b)

        # Undo button - SMALLER
        self.undo_btn = tk.Button(
            rank_frame,
            text='U',
            width=1,
            height=1,  # Explicit small height
            font=('Segoe UI', 8, 'bold'),
            command=self.undo
        )
        self.undo_btn.grid(row=0, column=len(RANKS), padx=2)

        # Second row: Action buttons - COMPACT
        action_frame = tk.Frame(self, bg=COLORS['bg_input'])
        action_frame.pack(pady=(3, 1))

        # Stand/Skip button - SMALLER
        self.stand_btn = tk.Button(
            action_frame,
            text='STAND/SKIP',
            width=10,
            height=1,  # Explicit small height
            font=('Segoe UI', 9, 'bold'),
            bg='#ff6666',
            fg='white',
            command=self.handle_stand
        )
        self.stand_btn.pack(side=tk.LEFT, padx=3)

        # Split button - SMALLER
        self.split_btn = tk.Button(
            action_frame,
            text='SPLIT',
            width=6,  # Reduced width (was 8)
            height=1,  # Explicit small height
            font=('Segoe UI', 9, 'bold'),
            bg='#66ff66',
            fg='black',
            command=self.handle_split
        )
        self.split_btn.pack(side=tk.LEFT, padx=3)

        # Info label - SMALLER
        info_label = tk.Label(
            action_frame,
            text="(For other players)",
            font=('Segoe UI', 7),
            bg=COLORS['bg_input'],
            fg='#cccccc'
        )
        info_label.pack(side=tk.LEFT, padx=5)

    def rank_clicked(self, rank):
        """SIMPLE: Handle rank button click."""
        print(f"SHARED_INPUT: Rank {rank} clicked")

        def on_suit_selected(suit):
            print(f"SHARED_INPUT: Selected {rank}{suit}")
            self.on_card(rank, suit)

        # Use the SIMPLE suit selection
        get_suit_selection(self, on_suit_selected)

    def undo(self):
        """Handle undo button click."""
        print("SHARED_INPUT: Undo clicked")
        self.on_undo()

    def handle_stand(self):
        """Handle stand/skip button."""
        print("SHARED_INPUT: Stand/Skip clicked")
        if self.on_stand:
            self.on_stand()

    def handle_split(self):
        """Handle split button."""
        print("SHARED_INPUT: Split clicked")
        if self.on_split:
            self.on_split()

    def set_action_callbacks(self, on_stand=None, on_split=None, on_double=None):
        """Set callbacks for action buttons."""
        self.on_stand = on_stand
        self.on_split = on_split
        # Ignore on_double for now

    def set_enabled(self, enabled):
        """Enable or disable all buttons."""
        state = tk.NORMAL if enabled else tk.DISABLED

        for btn in self.rank_btns:
            btn.config(state=state)

        self.undo_btn.config(state=state)
        self.stand_btn.config(state=state)
        self.split_btn.config(state=state)
