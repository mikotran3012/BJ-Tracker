import tkinter as tk
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from constants import RANKS, COLORS, normalize_rank_display
from .base_card_panel import BaseCardPanel
from .suit_selection import get_suit_selection


class PlayerPanel(BaseCardPanel):
    """Player panel with unified actions and split support."""

    def __init__(self, parent, on_card, on_undo, on_action=None, on_global_undo=None, undo_manager=None):
        super().__init__(parent, "PLAYER", is_player=True, is_dealer=False,
                         on_card=on_card, on_undo=on_undo)
        self.on_action = on_action
        self.on_global_undo = on_global_undo  # <-- Assign here
        self.undo_manager = undo_manager  # <-- Assign here
        self._build_player_ui()

    def _build_player_ui(self):
        """Build player-specific UI."""
        # Panel background
        panel_color = COLORS['fg_player']
        self.configure(bg=panel_color)

        # Header
        self.label = tk.Label(
            self, text="PLAYER",
            font=('Segoe UI', 10, 'bold'),
            bg=panel_color, fg=COLORS['fg_white']
        )
        self.label.pack(pady=2)

        # Status display
        self.status_label = tk.Label(
            self, text="",
            font=('Segoe UI', 8),
            bg=panel_color, fg='#ff4444'
        )
        self.status_label.pack()

        # Card display area
        self.display_frame = tk.Frame(self, bg=panel_color)
        self.display_frame.pack(fill='both', expand=True, padx=4, pady=4)
        self._add_hand_display()

        # Input buttons + Score
        self._build_input_row()

        # Action buttons - SIMPLIFIED to just Stand/Skip and Split
        self._build_action_buttons()

    def _add_hand_display(self):
        """Add hand display for player."""
        hand_frame = tk.Frame(self.display_frame, bg=COLORS['fg_player'])
        hand_frame.pack(fill='both', expand=True, pady=1)
        self.displays.append(hand_frame)
        self.card_widgets.append([])

    def _build_input_row(self):
        """Build rank input buttons and score display."""
        bottom_frame = tk.Frame(self, bg=COLORS['fg_player'])
        bottom_frame.pack(fill='x', pady=3)

        # Rank buttons
        btn_row = tk.Frame(bottom_frame, bg=COLORS['fg_player'])
        btn_row.pack(side=tk.LEFT, fill='x', expand=True)

        self.rank_btns = []
        for ri, r in enumerate(RANKS):
            display_rank = normalize_rank_display(r)
            b = tk.Button(
                btn_row, text=display_rank,
                width=1 if r != '10' else 2, font=('Segoe UI', 8),
                command=lambda rank=r: self.rank_clicked(rank)
            )
            b.grid(row=0, column=ri, padx=0, sticky='ew')
            self.rank_btns.append(b)

        # GLOBAL UNDO button - calls main app's shared undo handler
        self.undo_btn = tk.Button(
            btn_row, text='U', width=1,
            font=('Segoe UI', 8, 'bold'),
            command=self._global_undo
        )
        self.undo_btn.grid(row=0, column=len(RANKS), padx=1, sticky='ew')

        # Configure grid weights
        for i in range(len(RANKS) + 1):
            btn_row.grid_columnconfigure(i, weight=1)

        # Score display
        self.score_label = tk.Label(
            bottom_frame, text="",
            font=('Segoe UI', 10, 'bold'),
            bg=COLORS['fg_player'], fg='#ffff00',
            width=8, anchor='center'
        )
        self.score_label.pack(side=tk.RIGHT, padx=3)

    def _build_action_buttons(self):
        """Build SIMPLIFIED player action buttons - only Stand/Skip and Split."""
        self.action_frame = tk.Frame(self, bg=COLORS['fg_player'])
        self.action_frame.pack(pady=2)

        # Unified Stand/Skip button - matches shared input panel exactly
        self.stand_skip_btn = tk.Button(
            self.action_frame, text='STAND/SKIP', width=12,
            font=('Segoe UI', 11, 'bold'),
            bg='#ff6666',  # Same red color as shared input
            fg='white',
            command=self._handle_stand_skip
        )
        self.stand_skip_btn.pack(side=tk.LEFT, padx=5)

        # Split button - matches shared input panel styling
        self.split_btn = tk.Button(
            self.action_frame, text='SPLIT', width=8,
            font=('Segoe UI', 11, 'bold'),
            bg='#66ff66',  # Same green color as shared input
            fg='black',
            command=lambda: self._action('split')
        )
        self.split_btn.pack(side=tk.LEFT, padx=5)

        # Update button states
        self._update_action_buttons()

    def _action(self, action):
        """Handle action button clicks."""
        print(f"PLAYER_ACTION: {action}")
        if self.on_action:
            self.on_action(action, self.current_hand)

    def _handle_stand_skip(self):
        """Handle the unified Stand/Skip button - exact same logic as shared input."""
        if self.play_phase:
            print("PLAYER: Stand action in play phase")
            self._action('stand')
        else:
            print("PLAYER: Skip action in dealing phase")
            self._action('skip')

    def _global_undo(self):
        """GLOBAL UNDO - delegates to main app's shared undo handler."""
        print("PLAYER: Global undo triggered")
        if self.on_global_undo:
            self.on_global_undo()
        else:
            print("PLAYER: No global undo handler available")

    def update_mode(self, play_phase=True):
        """Update UI mode based on current game phase."""
        self.play_phase = play_phase
        self._update_action_buttons()
        print(f"PLAYER: Updated mode to {'play' if play_phase else 'dealing'} phase")

    def input_card(self, rank, suit, is_hole=False):
        """Player card input with correct split dealing logic."""
        print(f"PLAYER_INPUT: {rank}{suit}")

        # If we're in the middle of a split, route the input to the correct hand!
        if getattr(self, "pending_split", False):
            target = self.pending_index
            if self.undo_manager:
                self.undo_manager.record_action(
                    "player", rank, suit,
                    hand_idx=target,
                    is_hole=is_hole
                )
            self.hands[target].append((rank, suit))
            if self.on_card:
                self.on_card(rank, suit, is_hole)

            self.pending_index += 1
            if self.pending_index >= len(self.hands):
                # Done dealing 1 card to each split hand
                self.pending_split = False
                self.pending_index = 0
                self.current_hand = 0  # Start play phase at hand 1
            else:
                self.current_hand = self.pending_index

            self.update_display()
            return

        # Normal card input (non-split)
        if self.undo_manager:
            self.undo_manager.record_action(
                "player", rank, suit,
                hand_idx=self.current_hand,
                is_hole=is_hole
            )
        super().input_card(rank, suit, is_hole)
        self.update_display()

    def update_display(self):
        """Update player display with cards."""
        # Clear existing card widgets
        for hand_widgets in self.card_widgets:
            for widget in hand_widgets:
                try:
                    widget.destroy()
                except:
                    pass

        self.card_widgets = []

        # Update each hand
        for i, hand in enumerate(self.hands):
            if i >= len(self.displays):
                self._add_hand_display()

            display_frame = self.displays[i]
            self.card_widgets.append([])

            # Clear display frame
            for widget in display_frame.winfo_children():
                try:
                    widget.destroy()
                except:
                    pass

            # Add hand indicator for splits
            if len(self.hands) > 1:
                hand_label = tk.Label(
                    display_frame,
                    text=f"Hand {i + 1}" + (" ←" if i == self.current_hand else ""),
                    font=('Segoe UI', 8, 'bold'),
                    bg=COLORS['fg_player'],
                    fg='#ffff00' if i == self.current_hand else '#cccccc'
                )
                hand_label.pack()

            # Add cards using base class method
            for rank, suit in hand:
                card_widget = self.create_card_widget(rank, suit, display_frame)
                self.card_widgets[i].append(card_widget)

        # Update score and status
        self._update_score_display()
        self._update_status_display()
        self._update_action_buttons()

    def _update_score_display(self):
        """Update player score display."""
        if self.hands[0]:
            if len(self.hands) > 1:
                # Split hands - show current hand score
                current_score = self.get_score_display(self.current_hand)
                self.score_label.config(text=f"H{self.current_hand + 1}: {current_score}")
            else:
                # Single hand
                score_text = self.get_score_display()
                self.score_label.config(text=score_text)
        else:
            self.score_label.config(text="")

    def _update_status_display(self):
        """Update player status display."""
        if self.is_surrendered:
            self.status_label.config(text="SURRENDERED")
        elif self.is_busted:
            self.status_label.config(text="BUST")
        elif self.is_done:
            self.status_label.config(text="STAND")
        else:
            self.status_label.config(text="")

    def _update_action_buttons(self):
        """Update action button states based on game state."""
        # Stand/Skip button is always enabled unless completely done
        disabled = self.is_done or self.is_busted or self.is_surrendered
        stand_state = tk.DISABLED if disabled else tk.NORMAL
        self.stand_skip_btn.config(state=stand_state)

        # Split button: only enabled when split is possible and not pending split dealing
        split_enabled = (self.can_split() and
                        not disabled and
                        not self.pending_split and
                        self.play_phase)  # Only allow splits during play phase
        split_state = tk.NORMAL if split_enabled else tk.DISABLED
        self.split_btn.config(state=split_state)

        print(f"PLAYER: Button states - Stand/Skip: {stand_state}, Split: {split_state}")

    def can_split(self, hand_idx=None):
        """Check if hand can be split."""
        if hand_idx is None:
            hand_idx = self.current_hand
        if hand_idx >= len(self.hands):
            return False

        hand = self.hands[hand_idx]
        if len(hand) != 2:
            return False

        # Check if same value
        rank1, rank2 = hand[0][0], hand[1][0]
        val1 = 10 if rank1 in ['T', '10', 'J', 'Q', 'K'] else (11 if rank1 == 'A' else int(rank1))
        val2 = 10 if rank2 in ['T', '10', 'J', 'Q', 'K'] else (11 if rank2 == 'A' else int(rank2))

        return val1 == val2

    def split_hand(self):
        """Split current hand."""
        if not self.can_split():
            return False

        current = self.hands[self.current_hand]
        if len(current) != 2:
            return False

        # Create second hand and prepare to deal a second card to each
        second_card = current.pop()
        new_hand = [second_card]
        self.hands.append(new_hand)

        # Show new hand display and flag that the next card inputs
        # should go to each hand in order.
        self._add_hand_display()
        self.pending_split = True
        self.pending_index = 0
        self.current_hand = 0
        self.is_done = False
        self.is_busted = False
        self.update_display()
        return True

    def surrender(self):
        """Surrender current hand."""
        self.is_surrendered = True
        self.is_done = True
        self.update_display()

    def stand(self):
        """Stand current hand."""
        self.is_done = True
        self.update_display()

    def set_enabled(self, enabled):
        """Enable/disable player controls."""
        state = tk.NORMAL if enabled else tk.DISABLED
        for btn in self.rank_btns:
            btn.config(state=state)
        self.undo_btn.config(state=state)
        # Action buttons are managed by _update_action_buttons()
        if enabled:
            self._update_action_buttons()
        else:
            self.stand_skip_btn.config(state=tk.DISABLED)
            self.split_btn.config(state=tk.DISABLED)

    def reset(self):
        """Reset player panel."""
        super().reset()
        self.pending_split = False
        self.pending_index = 0
        self.update_display()