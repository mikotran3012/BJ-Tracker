import tkinter as tk
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from constants import RANKS, COLORS, normalize_rank_display
from .suit_selection import get_suit_selection


class BaseCardPanel(tk.Frame):
    """Essential base class with shared visual functionality."""

    def __init__(self, parent, label_text, is_player, is_dealer, on_card, on_undo):
        super().__init__(parent, bg=COLORS['bg_panel'])
        self.is_player = is_player
        self.is_dealer = is_dealer
        self.on_card = on_card
        self.on_undo = on_undo

        # Essential state
        self.hands = [[]]
        self.current_hand = 0
        self.is_busted = False
        self.is_surrendered = False
        self.is_done = False

        # Display management
        self.displays = []
        self.card_widgets = []

        # Will be set by subclasses during their _build() method
        self.label = None
        self.score_label = None
        self.status_label = None
        self.rank_btns = []
        self.undo_btn = None

    def rank_clicked(self, rank):
        """Basic rank click - show suit selection."""

        def on_suit_selected(suit):
            self.input_card(rank, suit, is_hole=False)

        get_suit_selection(self, on_suit_selected)

    def input_card(self, rank, suit, is_hole=False):
        """FIXED: Input card without duplicates."""
        print(f"BASE_INPUT: {rank}{suit}")

        # Add to current hand (ONCE!)
        self.hands[self.current_hand].append((rank, suit))

        # Check for bust
        if self.calculate_score() > 21:
            self.is_busted = True

        # Callback
        self.on_card(rank, suit, is_hole=False)

        # Let subclass handle display
        if hasattr(self, 'update_display'):
            self.update_display()

    def undo(self, hand_idx=None):
        """Basic undo.

        ``hand_idx`` allows specifying which hand to remove a card from in
        split scenarios.  When ``None`` the currently active hand is used so
        existing calls remain backwards compatible.
        """
        if hand_idx is None:
            hand_idx = self.current_hand

        if self.hands[hand_idx]:
            last_card = self.hands[hand_idx].pop()
            self.is_busted = False
            self.on_undo(rank=last_card[0], is_hole=False)

            if hasattr(self, 'update_display'):
                self.update_display()

            return last_card

    def calculate_score(self, hand_idx=None):
        """Basic blackjack scoring."""
        if hand_idx is None:
            hand_idx = self.current_hand

        if hand_idx >= len(self.hands):
            return 0

        hand = self.hands[hand_idx]
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

        # Adjust aces
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1

        return total

    def reset(self):
        """Basic reset."""
        self.hands = [[]]
        self.current_hand = 0
        self.is_busted = False
        self.is_surrendered = False
        self.is_done = False

    def set_enabled(self, enabled):
        """Basic enable/disable - subclasses override."""
        pass

    def get_cards(self):
        """Get current hand cards."""
        return self.hands[self.current_hand] if self.current_hand < len(self.hands) else []

    # ESSENTIAL SHARED VISUAL METHODS (prevent code duplication)

    def create_card_widget(self, rank, suit, parent):
        """Create card widget - SHARED by both player and dealer."""
        if suit in ['♥', '♦']:
            card_color = '#ff4444'
        else:
            card_color = 'black'

        display_rank = normalize_rank_display(rank)

        # Card size based on context
        if self.is_player and len(self.hands) > 1:
            width, height = 30, 45  # Smaller for splits
            rank_font = ('Arial', 6, 'bold')
            suit_font = ('Arial', 8, 'bold')
        else:
            width, height = 50, 70  # Normal size
            rank_font = ('Arial', 8, 'bold')
            suit_font = ('Arial', 12, 'bold')

        # Create card frame
        card_frame = tk.Frame(
            parent, bg='white', bd=1, relief=tk.RAISED,
            width=width, height=height
        )
        card_frame.pack_propagate(False)
        card_frame.pack(side=tk.LEFT, padx=1, pady=1)

        # Add rank and suit
        tk.Label(card_frame, text=display_rank, font=rank_font,
                 fg=card_color, bg='white').pack(pady=(1, 0))
        tk.Label(card_frame, text=suit, font=suit_font,
                 fg=card_color, bg='white').pack(expand=True)

        return card_frame

    def create_mystery_card_widget(self, parent):
        """Create mystery card widget - SHARED by dealer mainly."""
        card_frame = tk.Frame(
            parent, bg='#000080', bd=2, relief=tk.RAISED,
            width=50, height=70
        )
        card_frame.pack_propagate(False)
        card_frame.pack(side=tk.LEFT, padx=2, pady=2)

        tk.Label(card_frame, text='?', font=('Arial', 20, 'bold'),
                 fg='white', bg='#000080').pack(expand=True)
        return card_frame

    def get_score_display(self, hand_idx=None):
        """Get formatted score display - SHARED formatting logic."""
        score = self.calculate_score(hand_idx)
        if score == 0:
            return ""

        if hand_idx is None:
            hand_idx = self.current_hand
        if hand_idx >= len(self.hands):
            return ""

        hand = self.hands[hand_idx]
        has_usable_ace = self._has_usable_ace(hand)

        if score > 21:
            return f"Bust {score}"
        elif score == 21 and len(hand) == 2:
            return "Blackjack!"
        elif has_usable_ace:
            return f"Soft {score}"
        else:
            return f"Hard {score}"

    def _has_usable_ace(self, hand):
        """Check if hand has usable ace - SHARED logic."""
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

        while total > 21 and aces > 0:
            total -= 10
            aces -= 1

        return aces > 0

    def add_card(self, rank, suit):
        """Add card to current hand - CONVENIENCE method."""
        self.hands[self.current_hand].append((rank, suit))
        if self.calculate_score() > 21:
            self.is_busted = True
        # Subclasses should call update_display() after this
