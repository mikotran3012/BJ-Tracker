# ui/input_panels.py
"""
Input panels for card entry in the Blackjack Tracker application.
"""

import tkinter as tk
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import RANKS, COLORS


# Import SuitSelectDialog locally to avoid circular imports
def get_suit_selection(parent, on_suit_selected):
    """Simple suit selection dialog."""
    suit_win = tk.Toplevel(parent)
    suit_win.title("Suit")
    suit_win.geometry("200x80+600+340")
    suit_win.configure(bg='white')

    def pick_suit(suit):
        suit_win.destroy()
        on_suit_selected(suit)

    suits = ['♠', '♥', '♦', '♣']
    colors = ['white', '#ff4444', '#40e0d0', '#90ee90']

    for i, (suit, color) in enumerate(zip(suits, colors)):
        btn = tk.Button(
            suit_win, text=suit,
            font=('Segoe UI', 16, 'bold'),
            width=3, fg=color,
            command=lambda s=suit: pick_suit(s)
        )
        btn.grid(row=0, column=i, padx=6, pady=8)

    suit_win.grab_set()
    suit_win.transient(parent)
    suit_win.wait_window()


class SharedInputPanel(tk.Frame):
    """Shared input panel for all seats except the player's seat."""

    def __init__(self, parent, on_card, on_undo):
        super().__init__(parent, bg=COLORS['bg_input'])
        self.on_card = on_card
        self.on_undo = on_undo
        self._build_panel()

    def _build_panel(self):
        """Build the shared input panel."""
        self.rank_btns = []

        # Rank buttons
        for ri, r in enumerate(RANKS):
            b = tk.Button(
                self, text=r, width=2,
                font=('Segoe UI', 11),
                command=lambda rank=r: self.rank_clicked(rank)
            )
            b.grid(row=0, column=ri, padx=1)
            self.rank_btns.append(b)

        # Undo button
        self.undo_btn = tk.Button(
            self, text='U', width=2,
            font=('Segoe UI', 11, 'bold'),
            command=self.undo
        )
        self.undo_btn.grid(row=0, column=len(RANKS), padx=3)

    def rank_clicked(self, rank):
        """Handle rank button click."""

        def on_suit_selected(suit):
            self.on_card(rank, suit)

        get_suit_selection(self, on_suit_selected)

    def undo(self):
        """Handle undo button click."""
        self.on_undo()

    def set_enabled(self, enabled):
        """Enable or disable all buttons."""
        state = tk.NORMAL if enabled else tk.DISABLED
        for btn in self.rank_btns:
            btn.config(state=state)
        self.undo_btn.config(state=state)


class PlayerOrDealerPanel(tk.Frame):
    """Enhanced input panel for player or dealer cards with split support."""

    def __init__(self, parent, label_text, is_player, is_dealer, on_card, on_undo, hole_card_reveal=False,
                 on_action=None):
        super().__init__(parent, bg=COLORS['bg_panel'])
        self.is_player = is_player
        self.is_dealer = is_dealer
        self.on_card = on_card
        self.on_undo = on_undo
        self.on_action = on_action
        self.hands = [[]]
        self.current_hand = 0
        self.hole_card = None
        self.hole_card_enabled = hole_card_reveal
        self.mystery_hole = False
        self.is_busted = False
        self.is_surrendered = False
        self.is_done = False

        # Initialize card tracking
        self.card_widgets = [[]]  # Track card widgets for each hand

        self._build(label_text)

    def reset(self):
        """Reset all cards and state."""
        # Clear all card widgets first
        for hand_widgets in self.card_widgets:
            for widget in hand_widgets:
                widget.destroy()

        # Reset state
        self.hands = [[]]
        self.current_hand = 0
        self.hole_card = None
        self.mystery_hole = False
        self.is_busted = False
        self.is_surrendered = False
        self.is_done = False
        self.card_widgets = [[]]

        # Clear displays but keep the frames
        for display in self.displays:
            for widget in display.winfo_children():
                widget.destroy()

        self.update_display()
        self.set_enabled(True)
        if self.is_dealer:
            self.hole_card_enabled = False
        if self.is_player:
            self._hide_action_buttons()

    def input_card(self, rank, suit, is_hole=False):
        """Input a card to this panel and immediately show it."""
        if self.is_dealer and is_hole:
            self.hole_card = (rank, suit)
            self.mystery_hole = False
            self.on_card(rank, suit, is_hole=True)
        else:
            self.hands[self.current_hand].append((rank, suit))
            # Check for bust
            score = self.calculate_score()
            if score > 21:
                self.is_busted = True
            self.on_card(rank, suit, is_hole=False)

        # Immediately update display to show the new card
        self.update_display()

    def input_mystery_card(self):
        """Input a mystery hole card for dealer."""
        if self.is_dealer and len(self.hands[0]) == 1:
            self.mystery_hole = True
            self.hole_card = None
            self.on_card("?", "?", is_hole=True)
            # Immediately update display
            self.update_display()

    def update_display(self):
        """Update the card display with actual card graphics."""
        # Clear all existing card widgets
        for hand_widgets in self.card_widgets:
            for widget in hand_widgets:
                widget.destroy()

        # Reset card widgets tracking
        self.card_widgets = []

        if self.is_dealer:
            # Dealer display logic
            if not self.displays:
                return

            display_frame = self.displays[0]
            self.card_widgets.append([])

            # Clear the display frame
            for widget in display_frame.winfo_children():
                widget.destroy()

            # Show dealer upcard
            if self.hands[0]:
                upcard = self.hands[0][0]
                card_widget = self.create_card_widget(upcard[0], upcard[1], display_frame)
                self.card_widgets[0].append(card_widget)

            # Show hole card (mystery or revealed)
            if self.mystery_hole:
                mystery_widget = self.create_mystery_card_widget(display_frame)
                self.card_widgets[0].append(mystery_widget)
            elif self.hole_card:
                hole_widget = self.create_card_widget(self.hole_card[0], self.hole_card[1], display_frame)
                self.card_widgets[0].append(hole_widget)
            elif len(self.hands[0]) >= 1:  # Show mystery for second card if not set
                mystery_widget = self.create_mystery_card_widget(display_frame)
                self.card_widgets[0].append(mystery_widget)

        else:
            # Player display logic
            for hand_idx, hand in enumerate(self.hands):
                if hand_idx >= len(self.displays):
                    # Need to add more display frames for splits
                    self._add_hand_display()

                display_frame = self.displays[hand_idx]
                self.card_widgets.append([])

                # Clear the display frame
                for widget in display_frame.winfo_children():
                    widget.destroy()

                # Add cards for this hand
                for rank, suit in hand:
                    card_widget = self.create_card_widget(rank, suit, display_frame)
                    self.card_widgets[hand_idx].append(card_widget)

        # Update score and status displays
        self._update_score_display()
        self._update_status_display()

    def _update_score_display(self):
        """Update the score display."""
        if self.is_dealer:
            if self.hole_card and not self.mystery_hole:
                # Calculate dealer total with revealed hole card
                temp_cards = self.hands[0] + [self.hole_card]
                total = 0
                aces = 0
                for rank, suit in temp_cards:
                    if rank in ['J', 'Q', 'K']:
                        total += 10
                    elif rank == 'A':
                        aces += 1
                        total += 11
                    elif rank == 'T':
                        total += 10
                    else:
                        total += int(rank)
                while total > 21 and aces > 0:
                    total -= 10
                    aces -= 1
                score_text = f"{total}" + (" 💥" if total > 21 else "")
                self.score_label.config(text=score_text)
            else:
                self.score_label.config(text="")
        else:
            # Player score
            score_text = self.get_score_display()
            self.score_label.config(text=score_text)

    def _update_status_display(self):
        """Update the status display."""
        if self.is_surrendered:
            self.status_label.config(text="SURRENDERED")
        elif self.is_busted:
            self.status_label.config(text="BUST")
        elif self.is_done:
            self.status_label.config(text="STAND")
        else:
            self.status_label.config(text="")

    def _build(self, label_text):
        """Build the panel UI with full-height colored zones and card graphics."""
        # Make the entire panel the colored background
        self.configure(bg=COLORS['fg_player'] if self.is_player else COLORS['fg_dealer'])

        # Label
        self.label = tk.Label(
            self, text=label_text,
            font=('Segoe UI', 12, 'bold'),
            bg=COLORS['fg_player'] if self.is_player else COLORS['fg_dealer'],
            fg=COLORS['fg_white']
        )
        self.label.pack(pady=4)

        # Status display
        self.status_label = tk.Label(
            self, text="",
            font=('Segoe UI', 11, 'bold'),
            bg=COLORS['fg_player'] if self.is_player else COLORS['fg_dealer'],
            fg='#ff4444'  # Red for status
        )
        self.status_label.pack()

        # Score display
        self.score_label = tk.Label(
            self, text="",
            font=('Segoe UI', 14, 'bold'),
            bg=COLORS['fg_player'] if self.is_player else COLORS['fg_dealer'],
            fg='#ffff00'  # Yellow for visibility
        )
        self.score_label.pack(pady=2)

        # Card display area - this will show actual card graphics
        self.display_frame = tk.Frame(self, bg=COLORS['fg_player'] if self.is_player else COLORS['fg_dealer'])
        self.display_frame.pack(fill='both', expand=True, padx=8, pady=8)

        self.displays = []
        self.card_widgets = []  # Store individual card widgets
        self._add_hand_display()

        # Input button row
        btn_row = tk.Frame(self, bg=COLORS['fg_player'] if self.is_player else COLORS['fg_dealer'])
        btn_row.pack(pady=4)

        self.rank_btns = []
        for ri, r in enumerate(RANKS):
            b = tk.Button(
                btn_row, text=r, width=2,
                font=('Segoe UI', 11),
                command=lambda rank=r: self.rank_clicked(rank)
            )
            b.grid(row=0, column=ri, padx=1)
            self.rank_btns.append(b)

        self.undo_btn = tk.Button(
            btn_row, text='U', width=2,
            font=('Segoe UI', 11, 'bold'),
            command=self.undo
        )
        self.undo_btn.grid(row=0, column=len(RANKS), padx=3)

        # Action buttons (for play phase)
        if self.is_player:
            self.action_frame = tk.Frame(self, bg=COLORS['fg_player'])
            self.action_frame.pack(pady=6)

            self.hit_btn = tk.Button(
                self.action_frame, text='Hit', width=8,
                font=('Segoe UI', 10, 'bold'), command=lambda: self._action('hit')
            )

            self.stand_btn = tk.Button(
                self.action_frame, text='Stand', width=8,
                font=('Segoe UI', 10, 'bold'), command=lambda: self._action('stand')
            )

            self.double_btn = tk.Button(
                self.action_frame, text='Double', width=8,
                font=('Segoe UI', 10, 'bold'), command=lambda: self._action('double')
            )

            self.surrender_btn = tk.Button(
                self.action_frame, text='Surrender', width=10,
                font=('Segoe UI', 10, 'bold'), command=lambda: self._action('surrender')
            )

            self.split_btn = tk.Button(
                self.action_frame, text='Split', width=8,
                font=('Segoe UI', 10, 'bold'), command=lambda: self._action('split')
            )

            self.skip_btn = tk.Button(
                self.action_frame, text='Skip', width=8,
                font=('Segoe UI', 10, 'bold'), command=lambda: self._action('skip')
            )

            self._hide_action_buttons()

        # Dealer-specific buttons
        if self.is_dealer:
            dealer_btn_row = tk.Frame(self, bg=COLORS['fg_dealer'])
            dealer_btn_row.pack(pady=6)

            self.mystery_btn = tk.Button(
                dealer_btn_row, text="Mystery Card (?)",
                font=('Segoe UI', 10),
                command=self.input_mystery_card
            )
            self.mystery_btn.pack(side=tk.LEFT, padx=4)

            self.reveal_btn = tk.Button(
                dealer_btn_row, text="Reveal Hole Card",
                font=('Segoe UI', 10),
                command=self.reveal_hole_card
            )
            self.reveal_btn.pack(side=tk.LEFT, padx=4)

    def _add_hand_display(self):
        """Add a hand display area for card graphics."""
        hand_frame = tk.Frame(self.display_frame, bg=COLORS['fg_player'] if self.is_player else COLORS['fg_dealer'])
        hand_frame.pack(fill='both', expand=True, pady=2)
        self.displays.append(hand_frame)
        self.card_widgets.append([])  # Empty list for this hand's cards

    def create_card_widget(self, rank, suit, parent):
        """Create a visual card widget."""
        # Determine card color based on suit
        if suit in ['♥', '♦']:
            card_color = '#ff4444'  # Red
            text_color = 'white'
        else:
            card_color = 'black'
            text_color = 'white'

        # Create card frame
        card_frame = tk.Frame(parent, bg='white', bd=2, relief=tk.RAISED, width=60, height=80)
        card_frame.pack_propagate(False)
        card_frame.pack(side=tk.LEFT, padx=2, pady=2)

        # Card rank (top)
        rank_label = tk.Label(card_frame, text=rank, font=('Arial', 12, 'bold'),
                              fg=card_color, bg='white')
        rank_label.pack(pady=(2, 0))

        # Card suit (center)
        suit_label = tk.Label(card_frame, text=suit, font=('Arial', 16, 'bold'),
                              fg=card_color, bg='white')
        suit_label.pack(expand=True)

        # Card rank (bottom, upside down)
        rank_label_bottom = tk.Label(card_frame, text=rank, font=('Arial', 12, 'bold'),
                                     fg=card_color, bg='white')
        rank_label_bottom.pack(pady=(0, 2))

        return card_frame

    def create_mystery_card_widget(self, parent):
        """Create a mystery/hidden card widget."""
        card_frame = tk.Frame(parent, bg='#000080', bd=2, relief=tk.RAISED, width=60, height=80)
        card_frame.pack_propagate(False)
        card_frame.pack(side=tk.LEFT, padx=2, pady=2)

        # Mystery pattern
        mystery_label = tk.Label(card_frame, text='?', font=('Arial', 24, 'bold'),
                                 fg='white', bg='#000080')
        mystery_label.pack(expand=True)

        return card_frame

    def update_display(self):
        """Update the card display with actual card graphics."""
        if self.is_dealer:
            # Clear existing cards
            for widget_list in self.card_widgets:
                for widget in widget_list:
                    widget.destroy()
                widget_list.clear()

            if not self.displays:
                return

            display_frame = self.displays[0]

            # Show dealer upcard
            if self.hands[0]:
                upcard = self.hands[0][0]
                card_widget = self.create_card_widget(upcard[0], upcard[1], display_frame)
                self.card_widgets[0].append(card_widget)

            # Show hole card (mystery or revealed)
            if self.mystery_hole:
                mystery_widget = self.create_mystery_card_widget(display_frame)
                self.card_widgets[0].append(mystery_widget)
            elif self.hole_card:
                hole_widget = self.create_card_widget(self.hole_card[0], self.hole_card[1], display_frame)
                self.card_widgets[0].append(hole_widget)
            else:
                mystery_widget = self.create_mystery_card_widget(display_frame)
                self.card_widgets[0].append(mystery_widget)

        else:
            # Player cards - show all hands
            for hand_idx, (hand, display_frame) in enumerate(zip(self.hands, self.displays)):
                # Clear existing cards for this hand
                if hand_idx < len(self.card_widgets):
                    for widget in self.card_widgets[hand_idx]:
                        widget.destroy()
                    self.card_widgets[hand_idx].clear()
                else:
                    self.card_widgets.append([])

                # Add cards for this hand
                for rank, suit in hand:
                    card_widget = self.create_card_widget(rank, suit, display_frame)
                    self.card_widgets[hand_idx].append(card_widget)

        # Update score and status
        if self.is_dealer:
            if self.hole_card and not self.mystery_hole:
                temp_cards = self.hands[0] + [self.hole_card]
                total = 0
                aces = 0
                for rank, suit in temp_cards:
                    if rank in ['J', 'Q', 'K']:
                        total += 10
                    elif rank == 'A':
                        aces += 1
                        total += 11
                    elif rank == 'T':
                        total += 10
                    else:
                        total += int(rank)
                while total > 21 and aces > 0:
                    total -= 10
                    aces -= 1
                score_text = f"{total}" + (" 💥" if total > 21 else "")
                self.score_label.config(text=score_text)
            else:
                self.score_label.config(text="")
        else:
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

    def _action(self, action):
        """Handle action button clicks."""
        if self.on_action:
            self.on_action(action, self.current_hand)

    def can_split(self, hand_idx=None):
        """Check if current hand can be split."""
        if hand_idx is None:
            hand_idx = self.current_hand
        if hand_idx >= len(self.hands):
            return False

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
        if hand_idx >= len(self.hands):
            return False
        return len(self.hands[hand_idx]) == 2

    def can_surrender(self, hand_idx=None):
        """Check if current hand can surrender."""
        if hand_idx is None:
            hand_idx = self.current_hand
        if hand_idx >= len(self.hands):
            return False
        return len(self.hands[hand_idx]) == 2 and len(self.hands) == 1

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
            return 0

        hand = self.hands[hand_idx]
        if not hand:
            return 0

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
        if score == 0:
            return ""

        if hand_idx is None:
            hand_idx = self.current_hand

        if hand_idx >= len(self.hands):
            return ""

        hand = self.hands[hand_idx]

        if score > 21:
            return f"{score} 💥"  # Bust icon
        elif score == 21 and len(hand) == 2:
            return f"{score} ⭐"  # Blackjack icon
        else:
            return str(score)

    def rank_clicked(self, rank):
        """Handle rank button click."""
        if self.is_dealer and len(self.hands[0]) == 1 and not self.hole_card and not self.mystery_hole:
            # This is hole card input for dealer
            self.choose_suit(rank, is_hole=True)
        else:
            self.choose_suit(rank, is_hole=False)

    def choose_suit(self, rank, is_hole=False):
        """Show suit selection dialog."""

        def on_suit_selected(suit):
            self.input_card(rank, suit, is_hole)

        get_suit_selection(self, on_suit_selected)

    def input_card(self, rank, suit, is_hole=False):
        """Input a card to this panel."""
        if self.is_dealer and is_hole:
            self.hole_card = (rank, suit)
            self.mystery_hole = False
            self.on_card(rank, suit, is_hole=True)
        else:
            self.hands[self.current_hand].append((rank, suit))
            # Check for bust
            score = self.calculate_score()
            if score > 21:
                self.is_busted = True
            self.on_card(rank, suit, is_hole=False)
        self.update_display()

    def input_mystery_card(self):
        """Input a mystery hole card for dealer."""
        if self.is_dealer and len(self.hands[0]) == 1:
            self.mystery_hole = True
            self.hole_card = None
            self.on_card("?", "?", is_hole=True)
            self.update_display()

    def undo(self):
        """Undo the last card input."""
        if self.is_dealer and (self.hole_card or self.mystery_hole):
            self.hole_card = None
            self.mystery_hole = False
            self.on_undo(is_hole=True)
        elif self.hands[self.current_hand]:
            last_card = self.hands[self.current_hand].pop()
            self.is_busted = False  # Reset bust status
            self.on_undo(rank=last_card[0], is_hole=False)
        self.update_display()

    def reset(self):
        """Reset all cards and state."""
        self.hands = [[]]
        self.current_hand = 0
        self.hole_card = None
        self.mystery_hole = False
        self.is_busted = False
        self.is_surrendered = False
        self.is_done = False

        # Reset displays
        for display in self.displays[1:]:
            display.destroy()
        self.displays = self.displays[:1]

        self.update_display()
        self.set_enabled(True)
        if self.is_dealer:
            self.hole_card_enabled = False
        if self.is_player:
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
        """Show appropriate action buttons for current state."""
        if not self.is_player:
            return

        self._hide_action_buttons()

        if self.is_done or self.is_busted or self.is_surrendered:
            return

        # Always show hit and stand
        self.hit_btn.pack(side=tk.LEFT, padx=1)
        self.stand_btn.pack(side=tk.LEFT, padx=1)

        # Show double if eligible
        if self.can_double():
            self.double_btn.pack(side=tk.LEFT, padx=1)

        # Show surrender if eligible
        if self.can_surrender():
            self.surrender_btn.pack(side=tk.LEFT, padx=1)

        # Show split if eligible
        if self.can_split():
            self.split_btn.pack(side=tk.LEFT, padx=1)

        # Always show skip
        self.skip_btn.pack(side=tk.LEFT, padx=1)

    def _hide_action_buttons(self):
        """Hide all action buttons."""
        if not self.is_player:
            return
        for btn in [self.hit_btn, self.stand_btn, self.double_btn,
                    self.surrender_btn, self.split_btn, self.skip_btn]:
            btn.pack_forget()

    def update_display(self):
        """Update the card display and score."""
        if self.is_dealer:
            # Dealer display logic
            up = self.hands[0][0] if self.hands[0] else None
            up_str = f"{up[0]}{up[1]}" if up else ""

            if self.mystery_hole:
                hole_str = "?"
            elif self.hole_card:
                hole_str = f"{self.hole_card[0]}{self.hole_card[1]}"
            else:
                hole_str = "?"

            self.displays[0].config(text=f"{up_str}   {hole_str}")

            # Score for dealer (only show if hole card is revealed)
            if self.hole_card and not self.mystery_hole:
                temp_cards = self.hands[0] + [self.hole_card]
                total = 0
                aces = 0
                for rank, suit in temp_cards:
                    if rank in ['J', 'Q', 'K']:
                        total += 10
                    elif rank == 'A':
                        aces += 1
                        total += 11
                    elif rank == 'T':
                        total += 10
                    else:
                        total += int(rank)
                while total > 21 and aces > 0:
                    total -= 10
                    aces -= 1
                score_text = f"{total}" + (" 💥" if total > 21 else "")
                self.score_label.config(text=score_text)
            else:
                self.score_label.config(text="")
        else:
            # Player display logic
            for i, (hand, display) in enumerate(zip(self.hands, self.displays)):
                disp = ""
                for r, s in hand:
                    disp += f"{r}{s} "
                display.config(text=disp.strip())

                # Highlight current hand
                if i == self.current_hand and len(self.hands) > 1:
                    display.config(relief=tk.RIDGE, bd=3)
                else:
                    display.config(relief=tk.SUNKEN, bd=2)

            # Score for current hand
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

    def set_enabled(self, enabled):
        """Enable or disable all input controls."""
        state = tk.NORMAL if enabled else tk.DISABLED
        for btn in self.rank_btns:
            btn.config(state=state)
        self.undo_btn.config(state=state)
        if self.is_dealer:
            self.mystery_btn.config(state=tk.NORMAL if enabled else tk.DISABLED)
            self.reveal_btn.config(state=tk.NORMAL if enabled else tk.DISABLED)

    def reveal_hole_card(self):
        """Enable hole card input mode."""
        self.hole_card_enabled = True
        self.mystery_hole = False

    def get_cards(self):
        """Get the current cards list for current hand."""
        return self.hands[self.current_hand] if self.current_hand < len(self.hands) else []

    def add_card(self, rank, suit):
        """Add a card (used by the main app)."""
        self.hands[self.current_hand].append((rank, suit))
        # Check for bust
        score = self.calculate_score()
        if score > 21:
            self.is_busted = True
        self.update_display()
