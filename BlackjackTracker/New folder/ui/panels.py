# ui/panels.py - IMPROVED VERSION
"""
UI panels for the Blackjack Tracker application.
IMPROVED: Better seat displays, bigger cards, clearer information layout
"""

import tkinter as tk
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import RANKS, COLORS, normalize_rank_display, normalize_rank_internal


class CompPanel(tk.Frame):
    """Panel showing card composition and deck penetration - MUCH MORE COMPACT."""

    def __init__(self, parent, on_decks_change, initial_decks=8):
        super().__init__(parent, bg=COLORS['bg_white'], bd=2, relief=tk.GROOVE, width=600, height=100)  # MUCH smaller
        self.pack_propagate(False)  # Maintain fixed size
        self.decks = initial_decks
        self.on_decks_change = on_decks_change
        # Use internal T for tracking, but display as 10
        self.comp = {r: 0 for r in ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']}
        self._build_panel()
        self.update_display()

    def _build_panel(self):
        """Build the MUCH MORE COMPACT composition panel UI."""
        # Left side: Shoe information (MUCH smaller)
        shoe = tk.Frame(self, bg=COLORS['bg_white'])
        shoe.grid(row=0, column=0, rowspan=2, sticky='nsw', padx=2, pady=1)  # Only 2 rows now

        # Deck selector - SMALLER
        deck_frame = tk.Frame(shoe, bg=COLORS['bg_white'])
        deck_frame.pack()
        tk.Label(deck_frame, text='Decks', font=('Segoe UI', 8, 'bold'), bg=COLORS['bg_white']).pack(side=tk.LEFT)
        self.deck_var = tk.IntVar(value=self.decks)
        dspin = tk.Spinbox(
            deck_frame, from_=1, to=8, width=2,  # Smaller width
            textvariable=self.deck_var,
            font=('Segoe UI', 10),  # Smaller font
            command=self.set_decks,
            justify='center'
        )
        dspin.pack(side=tk.LEFT, padx=2)

        # Cards remaining - COMPACT
        cards_frame = tk.Frame(shoe, bg=COLORS['bg_white'])
        cards_frame.pack()
        tk.Label(cards_frame, text='Left:', font=('Segoe UI', 8, 'bold'), bg=COLORS['bg_white']).pack(side=tk.LEFT)
        self.cards_left_label = tk.Label(
            cards_frame, text="416",
            font=('Segoe UI', 11, 'bold'),  # Smaller font
            fg=COLORS['fg_blue'],
            bg=COLORS['bg_white']
        )
        self.cards_left_label.pack(side=tk.LEFT, padx=2)

        # Penetration - COMPACT
        pen_frame = tk.Frame(shoe, bg=COLORS['bg_white'])
        pen_frame.pack()
        tk.Label(pen_frame, text='Pen:', font=('Segoe UI', 8, 'bold'), bg=COLORS['bg_white']).pack(side=tk.LEFT)
        self.pen_bar = tk.Canvas(
            pen_frame, width=40, height=10,  # Much smaller
            bg='#e0e0e0', bd=1,
            highlightthickness=0
        )
        self.pen_bar.pack(side=tk.LEFT, padx=2)
        self.pen_label = tk.Label(pen_frame, text="0.0%", font=('Segoe UI', 8, 'bold'), bg=COLORS['bg_white'])
        self.pen_label.pack(side=tk.LEFT, padx=1)

        # Right side: Card composition grid - MUCH MORE COMPACT
        self._build_composition_grid()

    def _build_composition_grid(self):
        """Build the card composition display grid - COMPACT VERSION."""
        # Rank headers - SMALLER
        display_ranks = [normalize_rank_display(r) for r in
                         ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']]
        for ci, r in enumerate(display_ranks):
            tk.Label(
                self, text=r,
                font=('Segoe UI', 9, 'bold'),  # Smaller font
                bg=COLORS['bg_white'],
                width=2  # Smaller width
            ).grid(row=0, column=ci + 1, padx=1, pady=1)

        # Combined composition/remaining row - SINGLE ROW
        internal_ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']

        self.comp_labels = {}
        self.rem_labels = {}

        for ci, r in enumerate(internal_ranks):
            # Create frame for both dealt and remaining
            cell_frame = tk.Frame(self, bg=COLORS['bg_white'])
            cell_frame.grid(row=1, column=ci + 1, padx=1, pady=1)

            # Dealt count (top, smaller)
            dealt_lbl = tk.Label(
                cell_frame, text='0',
                font=('Segoe UI', 8, 'bold'),  # Smaller font
                width=2, height=1,
                fg=COLORS['fg_comp_cell'],
                bg=COLORS['bg_comp_cell'],
                bd=1, relief=tk.SUNKEN
            )
            dealt_lbl.pack()
            self.comp_labels[r] = dealt_lbl

            # Remaining count (bottom, smaller)
            remain_lbl = tk.Label(
                cell_frame, text='32',
                font=('Segoe UI', 8, 'bold'),  # Smaller font
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
            width = int((pct / 100) * 40)  # Match smaller canvas width
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


class SeatHandPanel(tk.Frame):
    """IMPROVED seat panel - SMALLER but still clear, optimized for space."""

    def __init__(self, parent, seat, is_player=False, is_your_seat=False, on_action=None):
        super().__init__(parent, bg=COLORS['bg_panel'], width=90, height=110)  # SMALLER size
        self.seat = seat
        self.is_player = is_player
        self.is_your_seat = is_your_seat
        self.on_action = on_action
        self.hands = [[]]
        self.current_hand = 0
        self.is_busted = False
        self.is_surrendered = False
        self.is_done = False
        self.pack_propagate(False)  # Maintain fixed size
        self._build_panel()

    def _build_panel(self):
        """Build the improved seat display with SMALLER but clear layout."""
        # Seat label with background color coding - SMALLER
        seat_color = self._get_background_color()
        seat_frame = tk.Frame(self, bg=seat_color, height=20)  # Smaller height
        seat_frame.pack(fill='x')
        seat_frame.pack_propagate(False)

        seat_label = tk.Label(
            seat_frame, text=self.seat,
            font=('Segoe UI', 10, 'bold'),  # Smaller font
            bg=seat_color,
            fg=COLORS['fg_white']
        )
        seat_label.pack(expand=True)

        # Score display (prominent but smaller)
        self.score_label = tk.Label(
            self, text="",
            font=('Segoe UI', 12, 'bold'),  # Smaller font
            bg=COLORS['bg_panel'],
            fg='#ffff00',  # Bright yellow
            height=1
        )
        self.score_label.pack(pady=1)

        # Status display
        self.status_label = tk.Label(
            self, text="",
            font=('Segoe UI', 8, 'bold'),  # Smaller font
            bg=COLORS['bg_panel'],
            fg='#ff4444'
        )
        self.status_label.pack()

        # Card display area - SMALLER
        self.display_frame = tk.Frame(self, bg=COLORS['bg_panel'], height=60)  # Smaller height
        self.display_frame.pack(fill='x', expand=True, pady=1)
        self.display_frame.pack_propagate(False)

        self.displays = []
        self.card_widgets = []
        self._add_hand_display()

        # Only skip button for other seats (smaller)
        self.action_frame = tk.Frame(self, bg=COLORS['bg_panel'])
        self.action_frame.pack()

        self.skip_btn = tk.Button(
            self.action_frame, text='SKIP', width=6,  # Smaller width
            font=('Segoe UI', 7), command=lambda: self._action('skip')  # Smaller font
        )

        self._hide_action_buttons()

    def create_seat_card_widget(self, rank, suit, parent):
        """Create a card widget optimized for seat display - SMALLER but clear."""
        # Determine card color based on suit
        if suit in ['♥', '♦']:
            card_color = '#ff4444'  # Red
        else:
            card_color = 'black'

        # Display rank (show 10 instead of T)
        display_rank = normalize_rank_display(rank)

        # Create card frame - SMALLER for compact seats
        card_frame = tk.Frame(parent, bg='white', bd=1, relief=tk.RAISED, width=25, height=35)  # Smaller
        card_frame.pack_propagate(False)
        card_frame.pack(side=tk.LEFT, padx=1, pady=1)

        # Card rank (center) - SMALLER font
        rank_label = tk.Label(card_frame, text=display_rank, font=('Arial', 7, 'bold'),
                              fg=card_color, bg='white')
        rank_label.pack(expand=True)

        # Card suit (bottom) - SMALLER font
        suit_label = tk.Label(card_frame, text=suit, font=('Arial', 8, 'bold'),
                              fg=card_color, bg='white')
        suit_label.pack()

        return card_frame

    def _add_hand_display(self):
        """Add a hand display area for card graphics."""
        bg_color = self._get_background_color()

        hand_frame = tk.Frame(
            self.display_frame,
            bg=COLORS['bg_panel']
        )
        hand_frame.pack(fill='both', expand=True, pady=1)
        self.displays.append(hand_frame)
        self.card_widgets.append([])

    def _get_background_color(self):
        """Get the appropriate background color for this seat."""
        if self.is_your_seat:
            return COLORS['bg_your_seat']
        elif self.is_player:
            return COLORS['fg_green']
        else:
            return COLORS['bg_normal_seat']

    def _action(self, action):
        """Handle action button clicks."""
        if self.on_action:
            self.on_action(self.seat, action, self.current_hand)

    def can_split(self, hand_idx=None):
        """Check if current hand can be split."""
        if hand_idx is None:
            hand_idx = self.current_hand
        hand = self.hands[hand_idx]

        if len(hand) != 2:
            return False

        # Check if both cards have same value (handle T/10 conversion)
        rank1, rank2 = hand[0][0], hand[1][0]
        val1 = 10 if rank1 in ['T', '10', 'J', 'Q', 'K'] else (11 if rank1 == 'A' else int(rank1))
        val2 = 10 if rank2 in ['T', '10', 'J', 'Q', 'K'] else (11 if rank2 == 'A' else int(rank2))

        return val1 == val2

    def can_double(self, hand_idx=None):
        """Check if current hand can double."""
        if hand_idx is None:
            hand_idx = self.current_hand
        return len(self.hands[hand_idx]) == 2

    def can_surrender(self, hand_idx=None):
        """Check if current hand can surrender."""
        if hand_idx is None:
            hand_idx = self.current_hand
        return len(self.hands[hand_idx]) == 2 and len(self.hands) == 1  # Only initial hand

    def split_hand(self):
        """Split the current hand into two hands and manage hand progression."""
        if not self.can_split():
            return False

        current = self.hands[self.current_hand]
        if len(current) != 2:
            return False

        # Create second hand with second card
        second_card = current.pop()
        new_hand = [second_card]
        self.hands.append(new_hand)

        # Add new display
        self._add_hand_display()

        # Reset current hand to 0 to play first split hand
        self.current_hand = 0
        self.is_done = False  # Make sure we're not marked as done

        self.update_display()
        return True

    def advance_to_next_split_hand(self):
        """Advance to the next split hand if available."""
        if self.current_hand < len(self.hands) - 1:
            self.current_hand += 1
            self.is_done = False  # Reset done status for new hand
            return True  # More hands to play
        else:
            self.is_done = True  # All hands completed
            return False  # No more hands

    def stand(self):
        """Mark current hand as done and check if we need to play more split hands."""
        if len(self.hands) > 1:  # Split hands exist
            if self.current_hand < len(self.hands) - 1:
                # More split hands to play, advance to next
                self.current_hand += 1
                print(f"  -> Advanced to hand {self.current_hand + 1}")  # Debug
                self.update_display()
                return False  # Still have hands to play
            else:
                # All split hands completed
                self.is_done = True
                print(f"  -> All hands completed")  # Debug
                self.update_display()
                return True  # Completely done
        else:
            # Single hand, just stand
            self.is_done = True
            self.update_display()
            return True  # Completely done

    def add_card(self, rank, suit, hand_idx=None):
        """Add a card to specified hand - FIXED to respect current_hand."""
        # FORCE use of current_hand if no hand_idx specified
        target_hand = self.current_hand if hand_idx is None else hand_idx

        if target_hand >= len(self.hands):
            print(f"ERROR: Trying to add card to hand {target_hand}, but only have {len(self.hands)} hands")
            return

        print(
            f"  -> Adding {rank}{suit} to {self.seat} hand {target_hand + 1} (current_hand={self.current_hand})")  # Debug
        self.hands[target_hand].append((rank, suit))

        # Check for bust on the specific hand
        score = self.calculate_score(target_hand)
        if score > 21:
            print(f"  -> Hand {target_hand + 1} busted with {score}")  # Debug
            # Only set busted if it's the current hand
            if target_hand == self.current_hand:
                self.is_busted = True

        self.update_display()

    def is_current_hand_done(self):
        """Check if the current hand specifically is done (bust, 21, etc)."""
        if self.is_busted or self.is_surrendered:
            return True

        # Check if current hand is at 21 or busted
        current_score = self.calculate_score(self.current_hand)
        return current_score >= 21

    def should_advance_focus(self):
        """Determine if focus should advance to next player or stay on current player."""
        if len(self.hands) == 1:
            # Single hand - advance if done
            return self.is_done or self.is_busted or self.is_surrendered
        else:
            # Split hands - check if ALL hands are done
            return self.current_hand >= len(self.hands) - 1 and (self.is_done or self.is_busted or self.is_surrendered)

    def calculate_score(self, hand_idx=None):
        """Calculate blackjack score for specified hand."""
        if hand_idx is None:
            hand_idx = self.current_hand

        if hand_idx >= len(self.hands):
            return ""

        hand = self.hands[hand_idx]
        if not hand:
            return ""

        total = 0
        aces = 0

        for rank, suit in hand:
            if rank in ['J', 'Q', 'K']:
                total += 10
            elif rank in ['T', '10']:  # Handle both T and 10
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
        # Use current_hand if no hand_idx specified
        if hand_idx is None:
            hand_idx = self.current_hand

        score = self.calculate_score(hand_idx)
        if score == "":
            return ""

        if hand_idx >= len(self.hands):
            return ""

        hand = self.hands[hand_idx]

        if score > 21:
            return f"{score}"  # Just the number for seats
        elif score == 21 and len(hand) == 2:
            return f"BJ"  # Blackjack abbreviation
        else:
            return str(score)

    # REMOVE any duplicate add_card method and replace with this definitive one
    def add_card_to_current_hand(self, rank, suit):
        """Explicitly add card to current hand - for debugging."""
        print(f"EXPLICIT: Adding {rank}{suit} to {self.seat} current hand {self.current_hand + 1}")
        self.hands[self.current_hand].append((rank, suit))

        # Check for bust
        score = self.calculate_score(self.current_hand)
        if score > 21:
            print(f"EXPLICIT: Hand {self.current_hand + 1} busted with {score}")
            self.is_busted = True

        self.update_display()

    def add_card(self, rank, suit, hand_idx=None):
        """Add a card to specified hand."""
        if hand_idx is None:
            hand_idx = self.current_hand

        if hand_idx >= len(self.hands):
            return

        self.hands[hand_idx].append((rank, suit))

        # Check for bust
        score = self.calculate_score(hand_idx)
        if score > 21:
            self.is_busted = True

        self.update_display()

    def undo(self, hand_idx=None):
        """Remove the last card from specified hand."""
        if hand_idx is None:
            hand_idx = self.current_hand

        if hand_idx >= len(self.hands) or not self.hands[hand_idx]:
            return None

        card = self.hands[hand_idx].pop()
        self.update_display()
        return card

    def reset(self):
        """Clear all cards and reset state."""
        # Clear all card widgets first
        for hand_widgets in self.card_widgets:
            for widget in hand_widgets:
                widget.destroy()

        self.hands = [[]]
        self.current_hand = 0
        self.is_busted = False
        self.is_surrendered = False
        self.is_done = False
        self.card_widgets = [[]]

        # Reset displays
        for display in self.displays[1:]:
            display.destroy()
        self.displays = self.displays[:1]

        self.update_display()
        self._hide_action_buttons()

    def surrender(self):
        """Mark hand as surrendered."""
        self.is_surrendered = True
        self.is_done = True
        self.update_display()

    def stand(self):
        """Mark current hand as done."""
        self.is_done = True
        self.update_display()

    def show_action_buttons(self):
        """Show only skip button for other seats."""
        self._hide_action_buttons()

        if self.is_done or self.is_busted or self.is_surrendered:
            return

        # Only show skip button for other seats
        self.skip_btn.pack()

    def _hide_action_buttons(self):
        """Hide the skip button."""
        self.skip_btn.pack_forget()

    def update_display(self):
        """Update the display with current cards and scores - IMPROVED for splits."""
        # Clear all existing card widgets
        for hand_widgets in self.card_widgets:
            for widget in hand_widgets:
                widget.destroy()

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
                widget.destroy()

            # Add hand indicator for splits
            if len(self.hands) > 1:
                hand_label = tk.Label(
                    display_frame,
                    text=f"H{i + 1}" + (" ←" if i == self.current_hand else ""),
                    font=('Segoe UI', 6, 'bold'),
                    bg=COLORS['bg_panel'],
                    fg='#ffff00' if i == self.current_hand else '#888888'
                )
                hand_label.pack()

            # Add cards for this hand
            for rank, suit in hand:
                card_widget = self.create_seat_card_widget(rank, suit, display_frame)
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

    def highlight(self, active=True):
        """Highlight or unhighlight this seat."""
        # Update the seat label background color
        seat_frame = self.winfo_children()[0]  # First child is seat frame
        seat_label = seat_frame.winfo_children()[0]  # First child of seat frame

        if active:
            seat_frame.config(bg=COLORS['bg_active_seat'])
            seat_label.config(bg=COLORS['bg_active_seat'])
        else:
            bg_color = self._get_background_color()
            seat_frame.config(bg=bg_color)
            seat_label.config(bg=bg_color)
