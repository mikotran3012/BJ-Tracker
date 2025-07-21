import tkinter as tk
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from constants import RANKS, COLORS, normalize_rank_display
from .suit_selection import get_suit_selection


class SharedInputPanel(tk.Frame):
    """UPDATED shared input panel with repositioned action buttons and Reset functionality."""

    def __init__(self, parent, on_card, on_undo):
        super().__init__(parent, bg=COLORS['bg_input'])
        self.on_card = on_card
        self.on_undo = on_undo
        self.on_stand = None
        self.on_split = None
        self.on_reset_active_seat = None  # NEW: Callback for reset active seat
        self._build_panel()

    def _build_panel(self):
        """Build the panel - UPDATED with repositioned action buttons."""
        # Main container for vertical centering
        main_container = tk.Frame(self, bg=COLORS['bg_input'])
        main_container.pack(expand=True, fill='both')

        # Centered content frame
        content_frame = tk.Frame(main_container, bg=COLORS['bg_input'])
        content_frame.pack(expand=True, anchor='center')

        # First row: Rank buttons - ENLARGED
        rank_frame = tk.Frame(content_frame, bg=COLORS['bg_input'])
        rank_frame.pack(pady=1)

        self.rank_btns = []

        # Rank buttons - LARGER and CLOSER
        for ri, r in enumerate(RANKS):
            display_rank = normalize_rank_display(r)  # Show 10 instead of T
            b = tk.Button(
                rank_frame,
                text=display_rank,
                width=2 if r != '10' else 3,  # INCREASED width (was 1/2)
                height=1,  # Keep small height
                font=('Segoe UI', 9),  # LARGER font (was 8)
                command=lambda rank=r: self.rank_clicked(rank)
            )
            b.grid(row=0, column=ri, padx=1)
            self.rank_btns.append(b)

        # Undo button - LARGER
        self.undo_btn = tk.Button(
            rank_frame,
            text='U',
            width=2,  # INCREASED width (was 1)
            height=1,  # Keep small height
            font=('Segoe UI', 9, 'bold'),  # LARGER font (was 8)
            command=self.undo
        )
        self.undo_btn.grid(row=0, column=len(RANKS), padx=2)

        # NEW: Action buttons row - LEFT-ALIGNED and horizontal
        action_frame = tk.Frame(content_frame, bg=COLORS['bg_input'])
        action_frame.pack(anchor='w', pady=(3, 1))  # LEFT-ALIGNED with anchor='w'

        # Stand button - REPOSITIONED and consistent styling
        self.stand_btn = tk.Button(
            action_frame,
            text='STAND',
            width=6,  # UPDATED: Consistent width
            height=1,  # UPDATED: Consistent height
            font=('Segoe UI', 9, 'bold'),  # UPDATED: Consistent font
            bg='#ff6666',
            fg='white',
            command=self.handle_stand
        )
        self.stand_btn.pack(side=tk.LEFT, padx=2)  # LEFT-ALIGNED in row

        # Split button - REPOSITIONED and consistent styling
        self.split_btn = tk.Button(
            action_frame,
            text='SPLIT',
            width=6,  # UPDATED: Consistent width
            height=1,  # UPDATED: Consistent height
            font=('Segoe UI', 9, 'bold'),  # UPDATED: Consistent font
            bg='#66ff66',
            fg='black',
            command=self.handle_split
        )
        self.split_btn.pack(side=tk.LEFT, padx=2)  # NEXT to Stand button

        # NEW: Reset button - ADDED to the right of Split
        self.reset_btn = tk.Button(
            action_frame,
            text='RESET',
            width=6,  # Consistent width
            height=1,  # Consistent height
            font=('Segoe UI', 9, 'bold'),  # Consistent font
            bg='#ffaa00',  # Orange background for reset
            fg='white',
            command=self.handle_reset
        )
        self.reset_btn.pack(side=tk.LEFT, padx=2)  # NEXT to Split button

        # Info label - REPOSITIONED to the right
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

    def handle_reset(self):
        """NEW: Handle reset button - resets only the active seat."""
        print("SHARED_INPUT: Reset active seat clicked")
        if self.on_reset_active_seat:
            self.on_reset_active_seat()

    def set_action_callbacks(self, on_stand=None, on_split=None, on_reset_active_seat=None):
        """Set callbacks for action buttons - UPDATED with reset callback."""
        self.on_stand = on_stand
        self.on_split = on_split
        self.on_reset_active_seat = on_reset_active_seat  # NEW callback

    def set_enabled(self, enabled):
        """Enable or disable all buttons."""
        state = tk.NORMAL if enabled else tk.DISABLED

        for btn in self.rank_btns:
            btn.config(state=state)

        self.undo_btn.config(state=state)
        self.stand_btn.config(state=state)
        self.split_btn.config(state=state)
        self.reset_btn.config(state=state)  # NEW: Enable/disable reset button