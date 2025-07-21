"""
IMPROVED seat panel - SMALLER but still clear, optimized for space.
UPDATED with split limitation logic.
"""

import tkinter as tk
from constants import RANKS, COLORS, normalize_rank_display, normalize_rank_internal
from .card_graphics import create_seat_card_widget


class SeatHandPanel(tk.Frame):
    """UPDATED seat panel with proper split hand management and split limitation."""

    def __init__(self, parent, seat, is_player=False, is_your_seat=False, on_action=None):
        super().__init__(parent, bg=COLORS['bg_panel'], width=90, height=110)
        self.seat = seat
        self.is_player = is_player
        self.is_your_seat = is_your_seat
        self.on_action = on_action

        # Initialize split tracking properly
        self.hands = [[]]  # List of hands (for splits)
        self.current_hand = 0  # Index of currently active hand
        self.is_busted = False
        self.is_surrendered = False
        self.is_done = False

        # When a split occurs we temporarily deal a second card to each
        # new hand before normal play resumes.  These helpers track that
        # state so the next card inputs go to the correct hand.
        self.pending_split = False  # True while waiting for second cards
        self.pending_index = 0  # Which split hand needs the next card

        # NEW: Track which hands have been split to limit splitting to once per hand
        self.split_history = set()

        self.pack_propagate(False)
        self._build_panel()

    def _build_panel(self):
        """Build the improved seat display with SMALLER but clear layout."""
        # Seat label with background color coding
        seat_color = self._get_background_color()
        seat_frame = tk.Frame(self, bg=seat_color, height=20)
        seat_frame.pack(fill='x')
        seat_frame.pack_propagate(False)

        seat_label = tk.Label(
            seat_frame, text=self.seat,
            font=('Segoe UI', 10, 'bold'),
            bg=seat_color,
            fg=COLORS['fg_white']
        )
        seat_label.pack(expand=True)

        # Score display (prominent but smaller)
        self.score_label = tk.Label(
            self, text="",
            font=('Segoe UI', 12, 'bold'),
            bg=COLORS['bg_panel'],
            fg='#ffff00',  # Bright yellow
            height=1
        )
        self.score_label.pack(pady=1)

        # Status display
        self.status_label = tk.Label(
            self, text="",
            font=('Segoe UI', 8, 'bold'),
            bg=COLORS['bg_panel'],
            fg='#ff4444'
        )
        self.status_label.pack()

        # Card display area
        self.display_frame = tk.Frame(self, bg=COLORS['bg_panel'], height=60)
        self.display_frame.pack(fill='x', expand=True, pady=1)
        self.display_frame.pack_propagate(False)

        self.displays = []
        self.card_widgets = []
        self._add_hand_display()

        # Only skip button for other seats
        self.action_frame = tk.Frame(self, bg=COLORS['bg_panel'])
        self.action_frame.pack()

        self.skip_btn = tk.Button(
            self.action_frame, text='SKIP', width=6,
            font=('Segoe UI', 7), command=lambda: self._action('skip')
        )

        self._hide_action_buttons()

    def _get_background_color(self):
        """Get the appropriate background color for this seat."""
        if self.is_your_seat:
            return COLORS['bg_your_seat']
        elif self.is_player:
            return COLORS['fg_green']
        else:
            return COLORS['bg_normal_seat']

    def _add_hand_display(self):
        """Add a hand display area for card graphics."""
        hand_frame = tk.Frame(
            self.display_frame,
            bg=COLORS['bg_panel']
        )
        hand_frame.pack(fill='both', expand=True, pady=1)
        self.displays.append(hand_frame)
        self.card_widgets.append([])

    def _action(self, action):
        """Handle action button clicks."""
        if self.on_action:
            self.on_action(self.seat, action, self.current_hand)

    # Split hand management methods
    def can_split(self, hand_idx=None):
        """UPDATED: Check if current hand can be split - LIMITED to once per hand."""
        if hand_idx is None:
            hand_idx = self.current_hand

        if hand_idx >= len(self.hands):
            return False

        # NEW: Check if this hand has already been split
        if hand_idx in self.split_history:
            print(f"SEAT {self.seat}: Cannot split hand {hand_idx} - already split once")
            return False

        hand = self.hands[hand_idx]
        if len(hand) != 2:
            return False

        # Check if both cards have same value
        rank1, rank2 = hand[0][0], hand[1][0]
        val1 = 10 if rank1 in ['T', '10', 'J', 'Q', 'K'] else (11 if rank1 == 'A' else int(rank1))
        val2 = 10 if rank2 in ['T', '10', 'J', 'Q', 'K'] else (11 if rank2 == 'A' else int(rank2))

        return val1 == val2

    def split_hand(self):
        """UPDATED: Split the current hand into two hands - with split limitation tracking."""
        if not self.can_split():
            print(f"SPLIT: Cannot split {self.seat} - conditions not met")
            return False

        current_hand_idx = self.current_hand
        current = self.hands[current_hand_idx]
        if len(current) != 2:
            print(f"SPLIT: Cannot split {self.seat} - need exactly 2 cards")
            return False

        print(f"SPLIT: Splitting {self.seat} hand {current_hand_idx} with {current}")

        # Create second hand with second card
        second_card = current.pop()
        new_hand = [second_card]
        self.hands.append(new_hand)

        # NEW: Mark this hand as having been split (prevent future splits)
        self.split_history.add(current_hand_idx)
        print(f"SPLIT: Added hand {current_hand_idx} to {self.seat} split history: {self.split_history}")

        print(f"SPLIT: {self.seat} now has hands: {self.hands}")

        # Reset to first hand and clear done status
        self.current_hand = 0
        self.is_done = False
        self.is_busted = False
        # Next two card inputs should go to each split hand in order
        self.pending_split = True
        self.pending_index = 0

        # Add new display for second hand
        self._add_hand_display()
        self.update_display()

        print(f"SPLIT: {self.seat} split complete, current_hand={self.current_hand}")
        return True

    def add_card(self, rank, suit, hand_idx=None):
        """Add a card to the appropriate hand.

        During a split the dealer immediately gives each new hand a
        second card.  ``pending_split`` tracks this state so incoming
        card inputs are routed to each split hand in turn before normal
        play resumes.
        """
        if self.pending_split:
            hand_idx = self.pending_index
        elif hand_idx is None:
            hand_idx = self.current_hand

        if hand_idx >= len(self.hands):
            print(f"ERROR: Trying to add card to hand {hand_idx}, but only have {len(self.hands)} hands")
            return

        print(f"ADD_CARD: Adding {rank}{suit} to {self.seat} hand {hand_idx + 1}")
        self.hands[hand_idx].append((rank, suit))

        # During the split dealing phase just move to the next hand until
        # each one has its second card.  Normal bust logic is applied once
        # the split is complete.
        if self.pending_split:
            self.pending_index += 1
            if self.pending_index >= len(self.hands):
                # Finished giving second cards
                self.pending_split = False
                self.pending_index = 0
                self.current_hand = 0
            else:
                self.current_hand = self.pending_index
        else:
            # Check for bust on the specific hand
            score = self.calculate_score(hand_idx)
            if score > 21:
                print(f"ADD_CARD: Hand {hand_idx + 1} busted with {score}")
                if hand_idx == self.current_hand:
                    self.is_busted = True

        self.update_display()

    def is_current_hand_done(self):
        """Check if the current hand is done."""
        if self.is_busted or self.is_surrendered:
            return True

        if self.current_hand >= len(self.hands):
            return True

        # Check if current hand is at 21 or busted
        current_score = self.calculate_score(self.current_hand)
        return current_score >= 21

    def advance_to_next_split_hand(self):
        if self.current_hand < len(self.hands) - 1:
            self.current_hand += 1
            self.is_done = False
            self.is_busted = False
            self.update_display()
            return True  # another split hand remains
        else:
            self.is_done = True
            self.update_display()
            return False  # all hands finished

    def should_advance_focus(self):
        """Determine if focus should advance to next player."""
        # If surrendered, advance
        if self.is_surrendered:
            return True

        # If only one hand, check if done/busted/21
        if len(self.hands) == 1:
            return self.is_done or self.is_busted or self.calculate_score(0) >= 21

        # For split hands, check if we're beyond all hands OR all hands are done
        if self.current_hand >= len(self.hands):
            return True

        # Check if current hand is done and it's the last hand
        if self.current_hand == len(self.hands) - 1:
            current_score = self.calculate_score(self.current_hand)
            return current_score >= 21 or self.is_done or self.is_busted

        return False

    def stand(self):
        """Mark current hand as done and handle split progression."""
        print(f"STAND: {self.seat} standing hand {self.current_hand + 1}")

        if len(self.hands) > 1:  # Split hands exist
            if self.current_hand < len(self.hands) - 1:
                # More split hands to play, advance to next
                self.current_hand += 1
                print(f"STAND: {self.seat} advanced to hand {self.current_hand + 1}")
                self.update_display()
                return False  # Still have hands to play
            else:
                # All split hands completed
                self.is_done = True
                print(f"STAND: {self.seat} all hands completed")
                self.update_display()
                return True  # Completely done
        else:
            # Single hand, just stand
            self.is_done = True
            self.update_display()
            return True  # Completely done

    def calculate_score(self, hand_idx=None):
        """Calculate blackjack score for specified hand."""
        if hand_idx is None:
            hand_idx = self.current_hand

        if hand_idx >= len(self.hands):
            return 0

        hand = self.hands[hand_idx]
        if not hand:
            return 0

        total = 0
        aces = 0

        for rank, suit in hand:
            if rank in ['J', 'Q', 'K']:
                total += 10
            elif rank in ['T', '10']:
                total += 10
            elif rank == 'A':
                aces += 1
                total += 11
            else:
                total += int(rank)

        # Adjust for aces
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1

        return total

    def get_score_display(self, hand_idx=None):
        """Get formatted score display text."""
        if hand_idx is None:
            hand_idx = self.current_hand

        score = self.calculate_score(hand_idx)
        if score == 0:
            return ""

        if hand_idx >= len(self.hands):
            return ""

        hand = self.hands[hand_idx]

        if score > 21:
            return f"{score}"
        elif score == 21 and len(hand) == 2:
            return f"BJ"
        else:
            return str(score)

    def update_display(self):
        """UPDATED: Update the display with current cards and scores."""
        # Clear all existing card widgets
        for hand_widgets in self.card_widgets:
            for widget in hand_widgets:
                try:
                    widget.destroy()
                except:
                    pass

        # Reset card widgets tracking
        self.card_widgets = []

        # Update each hand display
        for i, hand in enumerate(self.hands):
            if i >= len(self.displays):
                self._add_hand_display()

            display_frame = self.displays[i]
            self.card_widgets.append([])

            # Clear the display frame
            for widget in display_frame.winfo_children():
                try:
                    widget.destroy()
                except:
                    pass

            # Add hand indicator for splits
            if len(self.hands) > 1:
                # UPDATED: Show split limitation status
                split_status = " (No Resplit)" if i in self.split_history else ""
                hand_label = tk.Label(
                    display_frame,
                    text=f"H{i + 1}" + (" ←" if i == self.current_hand else "") + split_status,
                    font=('Segoe UI', 6, 'bold'),
                    bg=COLORS['bg_panel'],
                    fg='#ffff00' if i == self.current_hand else '#888888'
                )
                hand_label.pack()

            # Add cards for this hand
            for rank, suit in hand:
                card_widget = create_seat_card_widget(rank, suit, display_frame)
                self.card_widgets[i].append(card_widget)

        # Update score display (show current hand score)
        if len(self.hands) > 1:
            # For splits, show current hand score with indicator
            current_score = self.get_score_display(self.current_hand)
            self.score_label.config(text=f"H{self.current_hand + 1}: {current_score}")
        else:
            # Single hand, show normal score
            score_text = self.get_score_display()
            self.score_label.config(text=score_text)

        # Update status
        if self.is_surrendered:
            self.status_label.config(text="SUR")
        elif self.is_busted:
            self.status_label.config(text="BUST")
        elif self.is_done:
            if len(self.hands) > 1:
                self.status_label.config(text="DONE")
            else:
                self.status_label.config(text="STAND")
        else:
            if len(self.hands) > 1:
                self.status_label.config(text=f"HAND {self.current_hand + 1}")
            else:
                self.status_label.config(text="")

    def undo(self, hand_idx=None):
        """Remove the last card from specified hand."""
        if hand_idx is None:
            hand_idx = self.current_hand

        if hand_idx >= len(self.hands) or not self.hands[hand_idx]:
            return None

        card = self.hands[hand_idx].pop()
        self.is_busted = False  # Reset bust status
        # Reactivate hand if an undone card existed
        self.is_done = False
        self.update_display()
        self.show_action_buttons()
        return card

    def reset(self):
        """UPDATED: Clear all cards and reset state - clear split history."""
        print(f"RESET: Resetting {self.seat}")

        # Clear all card widgets first
        for hand_widgets in self.card_widgets:
            for widget in hand_widgets:
                try:
                    widget.destroy()
                except:
                    pass

        # Reset state
        self.hands = [[]]
        self.current_hand = 0
        self.is_busted = False
        self.is_surrendered = False
        self.is_done = False
        self.card_widgets = [[]]

        # NEW: Clear split history on reset
        self.split_history.clear()
        print(f"RESET: Cleared split history for {self.seat}")

        # Reset displays (keep only first one)
        for display in self.displays[1:]:
            try:
                display.destroy()
            except:
                pass
        self.displays = self.displays[:1] if self.displays else []

        if not self.displays:
            self._add_hand_display()

        self.update_display()
        self._hide_action_buttons()

    def surrender(self):
        """Mark hand as surrendered."""
        self.is_surrendered = True
        self.is_done = True
        self.update_display()

    def show_action_buttons(self):
        """Show only skip button for other seats."""
        self._hide_action_buttons()
        if self.is_done or self.is_busted or self.is_surrendered:
            return
        self.skip_btn.pack()

    def _hide_action_buttons(self):
        """Hide the skip button."""
        self.skip_btn.pack_forget()

    def highlight(self, active=True):
        """Highlight or unhighlight this seat."""
        seat_frame = self.winfo_children()[0]
        seat_label = seat_frame.winfo_children()[0]

        if active:
            seat_frame.config(bg=COLORS['bg_active_seat'])
            seat_label.config(bg=COLORS['bg_active_seat'])
        else:
            bg_color = self._get_background_color()
            seat_frame.config(bg=bg_color)
            seat_label.config(bg=bg_color)