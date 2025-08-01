import tkinter as tk
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from constants import RANKS, COLORS, normalize_rank_display
from .base_card_panel import BaseCardPanel
from .suit_selection import get_suit_selection


class PlayerPanel(BaseCardPanel):
    """Player panel with unified actions and UPDATED stacked card display."""

    def __init__(self, parent, on_card, on_undo, on_action=None, on_global_undo=None, undo_manager=None):
        super().__init__(parent, "PLAYER", is_player=True, is_dealer=False,
                         on_card=on_card, on_undo=on_undo)
        self.on_action = on_action
        self.on_global_undo = on_global_undo
        self.undo_manager = undo_manager

        # Track which hands have been split to limit splitting to once per hand
        self.split_history = set()
        self.hand_labels = []  # store labels for each hand container

        self._build_player_ui()

    def _build_player_ui(self):
        """Build player-specific UI with UPDATED stacked card display."""
        # Panel background
        panel_color = COLORS['fg_player']
        self.configure(bg=panel_color)

        # Header
        self.label = tk.Label(
            self, text="PLAYER",
            font=('Segoe UI', 10, 'bold'),
            bg=panel_color, fg=COLORS['fg_white']
        )
        self.label.pack(anchor='w', padx=2, pady=(2, 0))  # align to left edge

        # Status display
        self.status_label = tk.Label(
            self, text="",
            font=('Segoe UI', 8),
            bg=panel_color, fg='#ff4444'
        )
        self.status_label.pack()

        # UPDATED: Card display area with stacked card support
        self.display_frame = tk.Frame(self, bg=panel_color)
        self.display_frame.pack(fill='both', expand=True, padx=4, pady=4)

        # UPDATED: Container for stacked cards
        self.card_center_container = tk.Frame(self.display_frame, bg=panel_color)
        self.card_center_container.pack(anchor='w', expand=True)

        self._add_hand_display()

        # Input buttons, score, and action buttons
        self._build_input_row()

    def _add_hand_display(self):
        """Add container for a hand with stacked cards."""
        hand_container = tk.Frame(self.card_center_container, bg=COLORS['fg_player'], height=80)
        hand_container.pack(anchor='w', pady=(10, 0), fill='x')
        label = tk.Label(hand_container, text="", font=('Segoe UI', 8, 'bold'),
                         bg=COLORS['fg_player'], fg='#cccccc')
        label.pack(side='top', anchor='w', padx=2, pady=(0, 2))

        card_area = tk.Frame(hand_container, bg=COLORS['fg_player'], height=80)
        card_area.pack(anchor='w', pady=0)

        self.displays.append(card_area)
        self.hand_labels.append(label)
        self.card_widgets.append([])

    def _build_input_row(self):
        """Build rank input buttons and REPOSITIONED score display."""
        bottom_frame = tk.Frame(self, bg=COLORS['fg_player'])
        bottom_frame.pack(fill='x', pady=2)

        # Create horizontal container for buttons and score
        input_container = tk.Frame(bottom_frame, bg=COLORS['fg_player'])
        input_container.pack(side=tk.LEFT, anchor='w', padx=0)

        # Rank buttons
        btn_row = tk.Frame(input_container, bg=COLORS['fg_player'])
        btn_row.pack(side=tk.LEFT, anchor='w', padx=0)

        self.rank_btns = []
        for ri, r in enumerate(RANKS):
            display_rank = normalize_rank_display(r)
            b = tk.Button(
                btn_row, text=display_rank,
                width=1 if r != '10' else 2,
                height=1,
                font=('Segoe UI', 7),
                bd=1,
                command=lambda rank=r: self.rank_clicked(rank)
            )
            b.grid(row=0, column=ri, padx=(0 if ri == 0 else 2, 0), pady=0, ipadx=0, ipady=0, sticky='w')
            self.rank_btns.append(b)

        # GLOBAL UNDO button
        self.undo_btn = tk.Button(
            btn_row, text='U',
            width=1,
            height=1,
            font=('Segoe UI', 7, 'bold'),
            bd=1,
            command=self._global_undo
        )
        self.undo_btn.grid(row=0, column=len(RANKS), padx=(2, 0), pady=0, ipadx=0, ipady=0, sticky='w')

        # UPDATED: Score display positioned immediately to the right of rank buttons
        self.score_label = tk.Label(
            input_container, text="",
            font=('Segoe UI', 10, 'bold'),  # Slightly larger font for better visibility
            bg=COLORS['fg_player'], fg='#ffff00',
            width=10, anchor='center',  # Reduced width to fit better
            relief=tk.SUNKEN, bd=1  # Added visual separation
        )
        self.score_label.pack(side=tk.LEFT, padx=(10, 0))  # Position immediately to the right with 10px spacing

        # Action buttons (moved to new row to prevent crowding)
        action_row = tk.Frame(self, bg=COLORS['fg_player'])
        action_row.pack(anchor='w', pady=(0, 2))

        self.stand_skip_btn = tk.Button(
            action_row, text='STAND',
            width=6,
            height=1,
            font=('Segoe UI', 9, 'bold'),
            bg='#ff6666',
            fg='white',
            command=self._handle_stand_skip
        )
        self.stand_skip_btn.pack(side=tk.LEFT, padx=2)

        self.split_btn = tk.Button(
            action_row, text='SPLIT',
            width=6,
            height=1,
            font=('Segoe UI', 9, 'bold'),
            bg='#66ff66',
            fg='black',
            command=lambda: self._action('split')
        )
        self.split_btn.pack(side=tk.LEFT, padx=2)

        # Reset button
        self.reset_btn = tk.Button(
            action_row, text='RESET',
            width=6,
            height=1,
            font=('Segoe UI', 9, 'bold'),
            bg='#ffaa00',
            fg='white',
            command=self._handle_reset
        )
        self.reset_btn.pack(side=tk.LEFT, padx=2)

        # Update button states
        self._update_action_buttons()

    def _handle_reset(self):
        """Handle reset button - resets the player panel."""
        print("PLAYER: Reset clicked - resetting player panel")
        self.reset()

    def create_stacked_card_widget(self, rank, suit, parent, x_offset, size_scale=0.8):  # REDUCED: 0.6 for splits, 1.6 for single becomes 0.48 and 1.28 (20% reduction)
        """Create a single card widget positioned for stacking with 20% smaller size."""
        # Base dimensions with scaling - REDUCED by 20%
        base_width = 45
        base_height = 65

        card_width = int(base_width * size_scale)
        card_height = int(base_height * size_scale)

        # Create main card frame
        card_frame = tk.Frame(parent,
                              bg='white',
                              relief=tk.SOLID,
                              bd=1,
                              width=card_width,
                              height=card_height)
        card_frame.pack_propagate(False)

        # Position using place() for stacking
        card_frame.place(x=x_offset, y=0)

        # Determine suit color and symbol
        suit_colors = {'♠': 'black', '♣': 'black', '♥': 'red', '♦': 'red'}
        suit_symbols = {'S': '♠', 'C': '♣', 'H': '♥', 'D': '♦'}

        suit_symbol = suit_symbols.get(suit, suit)
        suit_color = suit_colors.get(suit_symbol, 'black')
        display_rank = '10' if rank in ['T', '10'] else rank

        # Scaled font sizes - ADJUSTED for smaller cards
        corner_font_size = max(3, int(5 * size_scale))  # Slightly smaller for legibility
        center_font_size = max(6, int(10 * size_scale))  # Slightly smaller for legibility

        if rank in ['J', 'Q', 'K']:
            center_font_size = max(8, int(12 * size_scale))  # Slightly smaller for legibility
        elif rank == 'A':
            center_font_size = max(11, int(16 * size_scale))  # Slightly smaller for legibility

        # Top-left corner: rank and suit (ALWAYS VISIBLE for stacking)
        top_left = tk.Label(card_frame,
                            text=f"{display_rank}\n{suit_symbol}",
                            font=('Arial', corner_font_size, 'bold'),
                            fg=suit_color,
                            bg='white',
                            justify=tk.LEFT)
        corner_x = max(1, int(2 * size_scale))
        corner_y = max(1, int(2 * size_scale))
        top_left.place(x=corner_x, y=corner_y)

        # Center: Large suit symbol(s)
        if rank in ['J', 'Q', 'K']:
            center_text = rank
        elif rank == 'A':
            center_text = suit_symbol
        elif rank in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'T']:
            center_text = suit_symbol
        else:
            center_text = suit_symbol

        center_label = tk.Label(card_frame,
                                text=center_text,
                                font=('Arial', center_font_size, 'bold'),
                                fg=suit_color,
                                bg='white')
        center_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Bottom-right corner: rank and suit (upside down)
        bottom_right = tk.Label(card_frame,
                                text=f"{suit_symbol}\n{display_rank}",
                                font=('Arial', corner_font_size, 'bold'),
                                fg=suit_color,
                                bg='white',
                                justify=tk.RIGHT)
        corner_offset = max(-1, int(-2 * size_scale))
        bottom_right.place(relx=1, rely=1, anchor=tk.SE, x=corner_offset, y=corner_offset)

        return card_frame

    def _action(self, action):
        """Handle action button clicks."""
        print(f"PLAYER_ACTION: {action}")
        if self.on_action:
            self.on_action(action, self.current_hand)

    def _handle_stand_skip(self):
        """Handle the unified Stand/Skip button."""
        if getattr(self, 'play_phase', True):
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
        """Update player display with stacked cards."""
        # Clear existing card widgets
        for hand_widgets in self.card_widgets:
            for widget in hand_widgets:
                try:
                    widget.destroy()
                except Exception:
                    pass

        self.card_widgets = []

        # UPDATED: Determine card scale based on number of hands - REDUCED by 20%
        card_scale = 0.6 if len(self.hands) > 1 else 1.6  # Reduced from 0.75/2.0 to 0.6/1.6 (20% reduction)
        stack_offset = int(18 * (card_scale / 1.6))  # Adjust offset proportionally (was 22 * scale/2.0)
        print(f"PLAYER: Using card scale {card_scale} for {len(self.hands)} hands")

        # Update each hand
        for i, hand in enumerate(self.hands):
            if i >= len(self.displays):
                self._add_hand_display()

            card_area = self.displays[i]
            label = self.hand_labels[i]
            self.card_widgets.append([])

            # Clear card area
            for child in card_area.winfo_children():
                child.destroy()

            # Hand label
            if len(self.hands) > 1:
                split_status = " (No Resplit)" if i in self.split_history else ""
                arrow = " ←" if i == self.current_hand else ""
                label_text = f"Hand {i + 1}{arrow}{split_status}"
                label.config(text=label_text,
                             fg='#ffff00' if i == self.current_hand else '#cccccc')
            else:
                label.config(text="")

            # UPDATED: Position cards with better spacing and layout for smaller cards
            current_x = 0

            for card_idx, (rank, suit) in enumerate(hand):
                card_widget = self.create_stacked_card_widget(rank, suit, card_area, current_x, card_scale)
                self.card_widgets[i].append(card_widget)
                current_x += stack_offset

            # Size card area to fit cards - ADJUSTED for smaller cards
            card_width = int(45 * card_scale)
            total_width = card_width + (len(hand) - 1) * stack_offset if hand else card_width
            card_area.configure(width=total_width, height=int(65 * card_scale) + 10)

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
                         not getattr(self, 'pending_split', False) and
                         getattr(self, 'play_phase', True))
        split_state = tk.NORMAL if split_enabled else tk.DISABLED
        self.split_btn.config(state=split_state)

        # Reset button is always enabled
        reset_state = tk.NORMAL
        self.reset_btn.config(state=reset_state)

        print(f"PLAYER: Button states - Stand/Skip: {stand_state}, Split: {split_state}, Reset: {reset_state}")

    def can_split(self, hand_idx=None):
        """Check if hand can be split - LIMITED to once per hand."""
        if hand_idx is None:
            hand_idx = self.current_hand
        if hand_idx >= len(self.hands):
            return False

        # Check if this hand has already been split
        if hand_idx in self.split_history:
            print(f"PLAYER: Cannot split hand {hand_idx} - already split once")
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
        """Split current hand - with split limitation tracking."""
        if not self.can_split():
            return False

        current_hand_idx = self.current_hand
        current = self.hands[current_hand_idx]
        if len(current) != 2:
            return False

        print(f"PLAYER: Splitting hand {current_hand_idx} with cards {current}")

        # Create second hand and prepare to deal a second card to each
        second_card = current.pop()
        new_hand = [second_card]
        self.hands.append(new_hand)

        # Mark this hand as having been split (prevent future splits)
        self.split_history.add(current_hand_idx)
        print(f"PLAYER: Added hand {current_hand_idx} to split history: {self.split_history}")

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

    def undo(self, hand_idx=None):
        """Undo last card and reactivate hand if needed."""
        card = super().undo(hand_idx)
        if card is not None:
            # Re-check completion status after card removal
            score = self.calculate_score(hand_idx if hand_idx is not None else self.current_hand)
            if self.is_done and not self.is_surrendered and score < 21:
                self.is_done = False
                self.update_display()
        return card

    def set_enabled(self, enabled):
        """Enable/disable player controls."""
        state = tk.NORMAL if enabled else tk.DISABLED
        for btn in self.rank_btns:
            btn.config(state=state)
        self.undo_btn.config(state=state)

        # Action buttons are managed by _update_action_buttons() when enabled
        if enabled:
            self._update_action_buttons()
        else:
            self.stand_skip_btn.config(state=tk.DISABLED)
            self.split_btn.config(state=tk.DISABLED)
            self.reset_btn.config(state=tk.DISABLED)

    def reset(self):
        """Reset player panel - clear split history."""
        super().reset()
        self.pending_split = False
        self.pending_index = 0
        # Clear split history on reset
        self.split_history.clear()
        print("PLAYER: Cleared split history on reset")
        self.update_display()