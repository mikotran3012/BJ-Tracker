# ui/panels.py
"""
UI panels for the Blackjack Tracker application.
"""

import tkinter as tk
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import RANKS, COLORS


class CompPanel(tk.Frame):
    """Panel showing card composition and deck penetration - compact but complete."""

    def __init__(self, parent, on_decks_change, initial_decks=8):
        super().__init__(parent, bg=COLORS['bg_white'], bd=2, relief=tk.GROOVE, width=700, height=160)
        self.pack_propagate(False)  # Maintain fixed size
        self.decks = initial_decks
        self.on_decks_change = on_decks_change
        self.comp = {r: 0 for r in RANKS}
        self._build_panel()
        self.update_display()

    def _build_panel(self):
        """Build the compact but complete composition panel UI."""
        # Left side: Shoe information (make it more compact but visible)
        shoe = tk.Frame(self, bg=COLORS['bg_white'])
        shoe.grid(row=0, column=0, rowspan=3, sticky='nsw', padx=4, pady=2)

        # Deck selector
        tk.Label(shoe, text='Decks', font=('Segoe UI', 10, 'bold'), bg=COLORS['bg_white']).pack()
        self.deck_var = tk.IntVar(value=self.decks)
        dspin = tk.Spinbox(
            shoe, from_=1, to=8, width=3,
            textvariable=self.deck_var,
            font=('Segoe UI', 12),
            command=self.set_decks,
            justify='center'
        )
        dspin.pack(pady=1)

        # Cards remaining - make sure this is visible
        tk.Label(shoe, text='Cards Left', font=('Segoe UI', 10, 'bold'), bg=COLORS['bg_white']).pack(pady=(4, 0))
        self.cards_left_label = tk.Label(
            shoe, text="416",
            font=('Segoe UI', 14, 'bold'),
            fg=COLORS['fg_blue'],
            bg=COLORS['bg_white']
        )
        self.cards_left_label.pack(pady=1)

        # Penetration section - make sure bar is visible
        tk.Label(shoe, text='Penetration', font=('Segoe UI', 10, 'bold'), bg=COLORS['bg_white']).pack(pady=(4, 1))
        self.pen_bar = tk.Canvas(
            shoe, width=70, height=16,
            bg='#e0e0e0', bd=1,
            highlightthickness=1, highlightbackground='#666'
        )
        self.pen_bar.pack(pady=1)
        self.pen_label = tk.Label(shoe, text="0.0%", font=('Segoe UI', 10, 'bold'), bg=COLORS['bg_white'])
        self.pen_label.pack(pady=1)

        # Right side: Card composition grid
        self._build_composition_grid()

    def _build_composition_grid(self):
        """Build the card composition display grid."""
        # Rank headers - compact but readable
        for ci, r in enumerate(RANKS):
            tk.Label(
                self, text=r,
                font=('Segoe UI', 12, 'bold'),
                bg=COLORS['bg_white'],
                width=3
            ).grid(row=0, column=ci + 1, padx=1, pady=2)

        # Composition row
        tk.Label(
            self, text='Dealt',
            font=('Segoe UI', 10, 'bold'),
            bg=COLORS['bg_white']
        ).grid(row=1, column=0, sticky='e', padx=(0, 4))

        self.comp_labels = {}
        for ci, r in enumerate(RANKS):
            lbl = tk.Label(
                self, text='0',
                font=('Segoe UI', 11, 'bold'),
                width=3, height=1,
                fg=COLORS['fg_comp_cell'],
                bg=COLORS['bg_comp_cell'],
                bd=1, relief=tk.SUNKEN
            )
            lbl.grid(row=1, column=ci + 1, padx=1, pady=1)
            self.comp_labels[r] = lbl

        # Remaining row
        tk.Label(
            self, text='Remain',
            font=('Segoe UI', 10, 'bold'),
            bg=COLORS['bg_white']
        ).grid(row=2, column=0, sticky='e', padx=(0, 4))

        self.rem_labels = {}
        for ci, r in enumerate(RANKS):
            lbl = tk.Label(
                self, text='32',
                font=('Segoe UI', 11, 'bold'),
                width=3, height=1,
                fg=COLORS['fg_white'],
                bg=COLORS['bg_rem_cell'],
                bd=1, relief=tk.SUNKEN
            )
            lbl.grid(row=2, column=ci + 1, padx=1, pady=(1, 4))
            self.rem_labels[r] = lbl

    def update_display(self):
        """Update all display elements - ensure everything shows."""
        d = self.decks

        # Update composition and remaining counts
        for r in RANKS:
            dealt = self.comp[r]
            remain = d * 4 - dealt
            self.comp_labels[r].config(text=str(dealt))
            self.rem_labels[r].config(text=str(remain))

        # Update cards remaining - make sure this updates
        cards_rem = self.cards_left()
        self.cards_left_label.config(text=str(cards_rem))

        # Update penetration bar - ensure it's visible
        pct, seen, total = self.penetration()
        self.pen_bar.delete("all")
        if total > 0:
            width = int((pct / 100) * 70)  # Match canvas width
            self.pen_bar.create_rectangle(0, 0, width, 16, fill=COLORS['fg_dealer'], outline="")
        self.pen_label.config(text=f"{pct:.1f}%")

    def set_decks(self):
        """Handle deck count change."""
        self.decks = self.deck_var.get()
        self.reset()
        self.on_decks_change()

    def reset(self):
        """Reset all composition counts."""
        self.comp = {r: 0 for r in RANKS}
        self.update_display()

    def log_card(self, rank):
        """Log a dealt card."""
        if rank != "?":  # Don't log mystery cards
            self.comp[rank] += 1
            self.update_display()

    def undo_card(self, rank):
        """Undo a dealt card."""
        if rank != "?" and self.comp[rank] > 0:
            self.comp[rank] -= 1
            self.update_display()

    def cards_left(self):
        """Calculate cards remaining in shoe."""
        return sum(self.decks * 4 - self.comp[r] for r in RANKS)

    def penetration(self):
        """Calculate penetration percentage."""
        seen = sum(self.comp.values())
        total = self.decks * 52
        pct = (seen / total) * 100 if total > 0 else 0
        return pct, seen, total

    def update_display(self):
        """Update all display elements."""
        d = self.decks

        # Update composition and remaining counts
        for r in RANKS:
            self.comp_labels[r].config(text=str(self.comp[r]))
            rem = d * 4 - self.comp[r]
            self.rem_labels[r].config(text=str(rem))

        # Update cards remaining
        cards_rem = self.cards_left()
        self.cards_left_label.config(text=str(cards_rem))

        # Update penetration bar
        pct, seen, total = self.penetration()
        self.pen_bar.delete("all")
        width = int((pct / 100) * 48)
        self.pen_bar.create_rectangle(0, 0, width, 14, fill=COLORS['fg_dealer'])
        self.pen_label.config(text=f"{pct:.1f}%")


class SeatHandPanel(tk.Frame):
    """Ultra-compact panel for player seats - only skip button needed."""

    def __init__(self, parent, seat, is_player=False, is_your_seat=False, on_action=None):
        super().__init__(parent, bg=COLORS['bg_panel'], width=70, height=80)
        self.seat = seat
        self.is_player = is_player
        self.is_your_seat = is_your_seat
        self.on_action = on_action
        self.hands = [[]]
        self.current_hand = 0
        self.is_busted = False
        self.is_surrendered = False
        self.is_done = False
        self.pack_propagate(False)  # Maintain minimal fixed size
        self._build_panel()

    def _build_panel(self):
        """Build the ultra-compact seat hand display with only skip button."""
        # Seat label (smaller)
        seat_label = tk.Label(
            self, text=self.seat,
            font=('Segoe UI', 8, 'bold'),
            bg=COLORS['bg_panel'],
            fg=COLORS['fg_white']
        )
        seat_label.pack()

        # Score display (compact)
        self.score_label = tk.Label(
            self, text="",
            font=('Segoe UI', 8, 'bold'),
            bg=COLORS['bg_panel'],
            fg='#ffff00'
        )
        self.score_label.pack()

        # Status display (tiny)
        self.status_label = tk.Label(
            self, text="",
            font=('Segoe UI', 6),
            bg=COLORS['bg_panel'],
            fg='#ff4444'
        )
        self.status_label.pack()

        # Card display (very compact)
        self.display_frame = tk.Frame(self, bg=COLORS['bg_panel'])
        self.display_frame.pack(fill='x', expand=True, pady=1)

        self.displays = []
        self._add_hand_display()

        # Only skip button for other seats
        self.action_frame = tk.Frame(self, bg=COLORS['bg_panel'])
        self.action_frame.pack()

        self.skip_btn = tk.Button(
            self.action_frame, text='SKIP', width=6,
            font=('Segoe UI', 6), command=lambda: self._action('skip')
        )

        self._hide_action_buttons()

    def _add_hand_display(self):
        """Add a very compact hand display."""
        bg_color = self._get_background_color()

        display = tk.Label(
            self.display_frame, text="",
            font=('Consolas', 6),
            bg=bg_color,
            fg=COLORS['fg_white'],
            anchor='w',
            width=8, height=2,
            bd=1, relief=tk.SUNKEN
        )
        display.pack(fill='x', pady=1)
        self.displays.append(display)

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

        # Check if both cards have same value
        rank1, rank2 = hand[0][0], hand[1][0]
        val1 = 10 if rank1 in ['T', 'J', 'Q', 'K'] else (11 if rank1 == 'A' else int(rank1))
        val2 = 10 if rank2 in ['T', 'J', 'Q', 'K'] else (11 if rank2 == 'A' else int(rank2))

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
        """Split the current hand into two hands."""
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
        self.update_display()
        return True

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
            elif rank == 'A':
                aces += 1
                total += 11
            elif rank == 'T':
                total += 10
            else:
                total += int(rank)

        # Adjust for aces
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1

        return total

    def get_score_display(self, hand_idx=None):
        """Get formatted score display text."""
        score = self.calculate_score(hand_idx)
        if score == "":
            return ""

        if hand_idx is None:
            hand_idx = self.current_hand

        hand = self.hands[hand_idx]

        if score > 21:
            return f"{score} 💥"  # Bust icon
        elif score == 21 and len(hand) == 2:
            return f"{score} ⭐"  # Blackjack icon
        else:
            return str(score)

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
        self.hands = [[]]
        self.current_hand = 0
        self.is_busted = False
        self.is_surrendered = False
        self.is_done = False

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
        """Update the display with current cards and scores."""
        # Update each hand display
        for i, (hand, display) in enumerate(zip(self.hands, self.displays)):
            disp = ""
            for r, s in hand:
                disp += f"{r}{s} "
            display.config(text=disp.strip())

            # Highlight current hand
            if i == self.current_hand:
                display.config(relief=tk.RIDGE, bd=3)
            else:
                display.config(relief=tk.SUNKEN, bd=2)

        # Update score display (show current hand score)
        score_text = self.get_score_display()
        self.score_label.config(text=score_text)

        # Update status
        if self.is_surrendered:
            self.status_label.config(text="SURRENDERED")
        elif self.is_busted:
            self.status_label.config(text="BUST")
        elif self.is_done:
            self.status_label.config(text="STAND")
        else:
            self.status_label.config(text="")

    def highlight(self, active=True):
        """Highlight or unhighlight this seat."""
        if active:
            for display in self.displays:
                display.config(bg=COLORS['bg_active_seat'])
        else:
            bg_color = self._get_background_color()
            for display in self.displays:
                display.config(bg=bg_color)
