# ui/input_panels.py - COMPLETE CLEAN VERSION
"""
Input panels for card entry in the Blackjack Tracker application.
FIXES: Button sizing, card graphics display, layout issues, T->10 conversion
PRESERVES: All original methods and functionality
"""

import tkinter as tk
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import RANKS, COLORS, normalize_rank_display, normalize_rank_internal


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
    """Shared input panel for all seats except the player's seat - BIGGER BUTTONS."""

    def __init__(self, parent, on_card, on_undo):
        super().__init__(parent, bg=COLORS['bg_input'])
        self.on_card = on_card
        self.on_undo = on_undo
        self._build_panel()

    def _build_panel(self):
        """Build the shared input panel with BIGGER BUTTONS, MORE SPACING, and ACTION BUTTONS."""
        # First row: Rank buttons
        rank_frame = tk.Frame(self, bg=COLORS['bg_input'])
        rank_frame.pack(pady=2)

        self.rank_btns = []

        # Rank buttons - BIGGER with MORE SPACING
        for ri, r in enumerate(RANKS):
            display_rank = normalize_rank_display(r)  # Show 10 instead of T
            b = tk.Button(
                rank_frame, text=display_rank, width=2 if r != '10' else 3,  # Bigger width, extra for "10"
                font=('Segoe UI', 11),  # BIGGER font
                command=lambda rank=r: self.rank_clicked(rank)  # Use internal rank
            )
            b.grid(row=0, column=ri, padx=3)  # MORE SPACING between buttons
            self.rank_btns.append(b)

        # Undo button - BIGGER
        self.undo_btn = tk.Button(
            rank_frame, text='U', width=3,  # Bigger width
            font=('Segoe UI', 11, 'bold'),  # BIGGER font
            command=self.undo
        )
        self.undo_btn.grid(row=0, column=len(RANKS), padx=5)  # Extra spacing

        # Second row: Action buttons (STAND/SKIP and SPLIT)
        action_frame = tk.Frame(self, bg=COLORS['bg_input'])
        action_frame.pack(pady=(8, 2))

        # Stand/Skip button - for players who don't want to hit (like 20s)
        self.stand_btn = tk.Button(
            action_frame, text='STAND/SKIP', width=12,
            font=('Segoe UI', 11, 'bold'),
            bg='#ff6666', fg='white',  # Red color for stand
            command=self.handle_stand
        )
        self.stand_btn.pack(side=tk.LEFT, padx=5)

        # Split button - for splitting pairs
        self.split_btn = tk.Button(
            action_frame, text='SPLIT', width=8,
            font=('Segoe UI', 11, 'bold'),
            bg='#66ff66', fg='black',  # Green color for split
            command=self.handle_split
        )
        self.split_btn.pack(side=tk.LEFT, padx=5)

        # Info label
        info_label = tk.Label(
            action_frame, text="(For other players)",
            font=('Segoe UI', 8),
            bg=COLORS['bg_input'], fg='#cccccc'
        )
        info_label.pack(side=tk.LEFT, padx=10)

    def rank_clicked(self, rank):
        """Handle rank button click."""

        def on_suit_selected(suit):
            self.on_card(rank, suit)

        get_suit_selection(self, on_suit_selected)

    def undo(self):
        """Handle undo button click."""
        self.on_undo()

    def handle_stand(self):
        """Handle stand/skip button for other players."""
        # This will be handled by the main app - stand the current focused seat
        if hasattr(self, 'on_stand') and self.on_stand:
            self.on_stand()

    def handle_split(self):
        """Handle split button for other players."""
        # This will be handled by the main app - split the current focused seat
        if hasattr(self, 'on_split') and self.on_split:
            self.on_split()

    def set_action_callbacks(self, on_stand=None, on_split=None):
        """Set callbacks for action buttons."""
        self.on_stand = on_stand
        self.on_split = on_split

    def set_enabled(self, enabled):
        """Enable or disable all buttons."""
        state = tk.NORMAL if enabled else tk.DISABLED
        for btn in self.rank_btns:
            btn.config(state=state)
        self.undo_btn.config(state=state)
        self.stand_btn.config(state=state)
        self.split_btn.config(state=state)


class PlayerOrDealerPanel(tk.Frame):
    """Enhanced input panel for player or dealer cards with split support and proper card graphics."""

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
        """Reset all cards and state - FIXED for proper cleanup."""
        print("RESET: Starting reset")

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
        self.hole_card = None
        self.mystery_hole = False
        self.is_busted = False
        self.is_surrendered = False
        self.is_done = False
        self.card_widgets = [[]]

        # Clear split-related attributes
        if hasattr(self, 'needs_split_completion'):
            delattr(self, 'needs_split_completion')
        if hasattr(self, 'split_cards_needed'):
            delattr(self, 'split_cards_needed')
        if hasattr(self, 'next_split_hand_for_card'):
            delattr(self, 'next_split_hand_for_card')

        # Clear hand score labels for splits
        if hasattr(self, 'hand_score_labels'):
            self.hand_score_labels = []

        # Clear displays - PROPERLY destroy split containers
        if hasattr(self, 'displays'):
            for i, display in enumerate(self.displays):
                if i > 0:  # Keep first display
                    try:
                        # For player splits, destroy the parent container
                        if self.is_player:
                            parent = display.master
                            if parent != self.display_frame:  # It's a split hand container
                                parent.destroy()
                        else:
                            display.destroy()
                    except:
                        pass

            # Keep only first display and clear it
            if self.displays:
                self.displays = self.displays[:1]
                if self.displays[0].winfo_exists():
                    for widget in self.displays[0].winfo_children():
                        try:
                            widget.destroy()
                        except:
                            pass
            else:
                self._add_hand_display()

        print(f"RESET: Complete - hands: {self.hands}")

        self.update_display()
        self.set_enabled(True)
        if self.is_dealer:
            self.hole_card_enabled = False
        if self.is_player:
            self._hide_action_buttons()

    def _build(self, label_text):
        """Build the panel UI with FIXED sizing and proper split hand layout."""
        # Make the entire panel the colored background
        self.configure(bg=COLORS['fg_player'] if self.is_player else COLORS['fg_dealer'])

        # Compact header with just title
        self.label = tk.Label(
            self, text=label_text,
            font=('Segoe UI', 10, 'bold'),
            bg=COLORS['fg_player'] if self.is_player else COLORS['fg_dealer'],
            fg=COLORS['fg_white']
        )
        self.label.pack(pady=2)

        # Status display (small, separate line)
        self.status_label = tk.Label(
            self, text="",
            font=('Segoe UI', 8),
            bg=COLORS['fg_player'] if self.is_player else COLORS['fg_dealer'],
            fg='#ff4444'  # Red for status
        )
        self.status_label.pack()

        # Card display area - FIXED for splits
        self.display_frame = tk.Frame(
            self,
            bg=COLORS['fg_player'] if self.is_player else COLORS['fg_dealer']
        )
        self.display_frame.pack(fill='both', expand=True, padx=4, pady=4)

        self.displays = []
        self.card_widgets = []
        self.hand_score_labels = []  # Initialize this properly

        # Always start with one display
        self._add_hand_display()

        # Bottom row: Input buttons + Score display side by side
        bottom_frame = tk.Frame(self, bg=COLORS['fg_player'] if self.is_player else COLORS['fg_dealer'])
        bottom_frame.pack(fill='x', pady=3)

        # Input button row - SMALLER BUTTONS to fit all (left side)
        btn_row = tk.Frame(bottom_frame, bg=COLORS['fg_player'] if self.is_player else COLORS['fg_dealer'])
        btn_row.pack(side=tk.LEFT, fill='x', expand=True)

        self.rank_btns = []
        for ri, r in enumerate(RANKS):
            display_rank = normalize_rank_display(r)  # Show 10 instead of T
            b = tk.Button(
                btn_row, text=display_rank, width=1 if r != '10' else 2,  # Wider for "10"
                font=('Segoe UI', 8),  # Smaller font
                command=lambda rank=r: self.rank_clicked(rank)  # Use internal rank
            )
            b.grid(row=0, column=ri, padx=0, sticky='ew')  # No padding, expand evenly
            self.rank_btns.append(b)

        self.undo_btn = tk.Button(
            btn_row, text='U', width=1,  # Smaller width
            font=('Segoe UI', 8, 'bold'),  # Smaller font
            command=self.undo
        )
        self.undo_btn.grid(row=0, column=len(RANKS), padx=1, sticky='ew')

        # Configure grid weights so buttons expand evenly
        for i in range(len(RANKS) + 1):
            btn_row.grid_columnconfigure(i, weight=1)

        # Score display (right side, next to buttons) - ALWAYS VISIBLE
        self.score_label = tk.Label(
            bottom_frame, text="",  # Start empty
            font=('Segoe UI', 12, 'bold'),
            bg=COLORS['fg_player'] if self.is_player else COLORS['fg_dealer'],
            fg='#ffff00',  # Yellow for visibility
            width=10, anchor='center'  # Fixed width, centered
        )
        self.score_label.pack(side=tk.RIGHT, padx=5)

        # Action buttons and dealer buttons (rest of the method unchanged)
        if self.is_player:
            self.action_frame = tk.Frame(self, bg=COLORS['fg_player'])
            self.action_frame.pack(pady=2)

            self.hit_btn = tk.Button(
                self.action_frame, text='Hit', width=4,
                font=('Segoe UI', 8, 'bold'), command=lambda: self._action('hit')
            )

            self.stand_btn = tk.Button(
                self.action_frame, text='Stand', width=4,
                font=('Segoe UI', 8, 'bold'), command=lambda: self._action('stand')
            )

            self.double_btn = tk.Button(
                self.action_frame, text='Dbl', width=3,  # Shorter text
                font=('Segoe UI', 8, 'bold'), command=lambda: self._action('double')
            )

            self.surrender_btn = tk.Button(
                self.action_frame, text='Sur', width=3,  # Shorter text
                font=('Segoe UI', 8, 'bold'), command=lambda: self._action('surrender')
            )

            self.split_btn = tk.Button(
                self.action_frame, text='Split', width=4,
                font=('Segoe UI', 8, 'bold'), command=lambda: self._action('split')
            )

            self.skip_btn = tk.Button(
                self.action_frame, text='Skip', width=4,
                font=('Segoe UI', 8, 'bold'), command=lambda: self._action('skip')
            )

            self._hide_action_buttons()

        # Dealer-specific buttons - SMALLER
        if self.is_dealer:
            dealer_btn_row = tk.Frame(self, bg=COLORS['fg_dealer'])
            dealer_btn_row.pack(pady=2)

            self.mystery_btn = tk.Button(
                dealer_btn_row, text="Mystery (?)",
                font=('Segoe UI', 8),  # Smaller
                command=self.input_mystery_card
            )
            self.mystery_btn.pack(side=tk.LEFT, padx=2)

            self.reveal_btn = tk.Button(
                dealer_btn_row, text="Reveal Hole",
                font=('Segoe UI', 8),  # Smaller
                command=self.reveal_hole_card
            )
            self.reveal_btn.pack(side=tk.LEFT, padx=2)

    def _add_hand_display(self):
        """Add a hand display area for card graphics - FIXED logic for single vs split hands."""
        if self.is_player and len(self.displays) > 1:
            # ONLY for ACTUAL splits (when we already have 1+ displays AND multiple hands)
            hand_container = tk.Frame(
                self.display_frame,
                bg=COLORS['fg_player'],
                width=180, height=120  # Compact size
            )
            hand_container.pack(side=tk.LEFT, padx=4, pady=2)  # Side by side
            hand_container.pack_propagate(False)

            # Hand header - COMPACT
            hand_header = tk.Frame(hand_container, bg=COLORS['fg_player'], height=20)
            hand_header.pack(fill='x')
            hand_header.pack_propagate(False)

            hand_label = tk.Label(
                hand_header,
                text=f"Hand {len(self.displays) + 1}" + (" ←" if len(self.displays) == self.current_hand else ""),
                font=('Segoe UI', 8, 'bold'),  # Smaller font
                bg=COLORS['fg_player'],
                fg='#ffff00'
            )
            hand_label.pack(side=tk.LEFT)

            # Score for this specific hand - COMPACT
            hand_score_label = tk.Label(
                hand_header,
                text="",
                font=('Segoe UI', 9, 'bold'),  # Smaller font
                bg=COLORS['fg_player'],
                fg='#ffff00'
            )
            hand_score_label.pack(side=tk.RIGHT)

            # Store reference to score label for this hand
            if not hasattr(self, 'hand_score_labels'):
                self.hand_score_labels = []
            self.hand_score_labels.append(hand_score_label)

            # Card area - COMPACT
            hand_frame = tk.Frame(hand_container, bg=COLORS['fg_player'])
            hand_frame.pack(fill='both', expand=True)
        else:
            # Single hand display - normal layout (NO hand labels)
            hand_frame = tk.Frame(
                self.display_frame,
                bg=COLORS['fg_player'] if self.is_player else COLORS['fg_dealer']
            )
            hand_frame.pack(fill='both', expand=True, pady=1)

            # Initialize hand_score_labels if needed but don't add any for single hand
            if not hasattr(self, 'hand_score_labels'):
                self.hand_score_labels = []

        self.displays.append(hand_frame)
        self.card_widgets.append([])  # Empty list for this hand's cards

    def create_card_widget(self, rank, suit, parent):
        """Create a visual card widget - SMALLER for splits."""
        # Determine card color based on suit
        if suit in ['♥', '♦']:
            card_color = '#ff4444'  # Red
        else:
            card_color = 'black'

        # Display rank (show 10 instead of T)
        display_rank = normalize_rank_display(rank)

        # Create card frame - SMALLER SIZE for splits
        if self.is_player and len(self.hands) > 1:
            # Smaller cards for splits
            card_frame = tk.Frame(parent, bg='white', bd=1, relief=tk.RAISED, width=35, height=50)
        else:
            # Normal size for single hands
            card_frame = tk.Frame(parent, bg='white', bd=2, relief=tk.RAISED, width=60, height=85)

        card_frame.pack_propagate(False)
        card_frame.pack(side=tk.LEFT, padx=1, pady=1)

        # Adjust font sizes for splits
        if self.is_player and len(self.hands) > 1:
            rank_font = ('Arial', 8, 'bold')
            suit_font = ('Arial', 12, 'bold')
        else:
            rank_font = ('Arial', 10, 'bold')
            suit_font = ('Arial', 16, 'bold')

        # Card rank (top)
        rank_label = tk.Label(card_frame, text=display_rank, font=rank_font,
                              fg=card_color, bg='white')
        rank_label.pack(pady=(1, 0))

        # Card suit (center)
        suit_label = tk.Label(card_frame, text=suit, font=suit_font,
                              fg=card_color, bg='white')
        suit_label.pack(expand=True)

        # Card rank (bottom, upside down)
        rank_label_bottom = tk.Label(card_frame, text=display_rank, font=rank_font,
                                     fg=card_color, bg='white')
        rank_label_bottom.pack(pady=(0, 1))

        return card_frame

    def create_mystery_card_widget(self, parent):
        """Create a mystery/hidden card widget with BIGGER sizing."""
        card_frame = tk.Frame(parent, bg='#000080', bd=2, relief=tk.RAISED, width=60, height=85)
        card_frame.pack_propagate(False)
        card_frame.pack(side=tk.LEFT, padx=2, pady=2)

        # Mystery pattern - BIGGER font
        mystery_label = tk.Label(card_frame, text='?', font=('Arial', 24, 'bold'),
                                 fg='white', bg='#000080')
        mystery_label.pack(expand=True)

        return card_frame

    def update_display(self):
        """Update the card display with actual card graphics - FIXED for single hand display."""
        # Clear all existing card widgets
        for hand_widgets in self.card_widgets:
            for widget in hand_widgets:
                widget.destroy()

        # Reset card widgets tracking
        self.card_widgets = []

        if self.is_dealer:
            # Dealer display logic (unchanged)
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
            # Player display logic - FIXED for single hands
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

                # ONLY update individual hand score labels if we have MULTIPLE hands (splits)
                if len(self.hands) > 1 and hasattr(self, 'hand_score_labels') and hand_idx < len(
                        self.hand_score_labels):
                    hand_score = self.get_score_display(hand_idx)
                    self.hand_score_labels[hand_idx].config(text=hand_score)

                    # Update hand label to show current hand
                    try:
                        parent_container = display_frame.master
                        if hasattr(parent_container, 'winfo_children'):
                            children = parent_container.winfo_children()
                            if len(children) > 0:
                                header_frame = children[0]
                                if hasattr(header_frame, 'winfo_children'):
                                    header_children = header_frame.winfo_children()
                                    if len(header_children) > 0:
                                        hand_label = header_children[0]
                                        current_indicator = " ←" if hand_idx == self.current_hand else ""
                                        hand_label.config(text=f"Hand {hand_idx + 1}{current_indicator}")
                    except:
                        pass  # Ignore errors in label updating

        # Update main score and status displays
        self._update_score_display()
        self._update_status_display()

    def _update_score_display(self):
        """Update the score display - ALWAYS show something."""
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
                    elif rank in ['T', '10']:  # Handle both T and 10
                        total += 10
                    else:
                        total += int(rank)
                while total > 21 and aces > 0:
                    total -= 10
                    aces -= 1

                # Determine if soft
                has_usable_ace = aces > 0
                if total > 21:
                    score_text = f"Bust {total}"
                elif has_usable_ace:
                    score_text = f"Soft {total}"
                else:
                    score_text = f"Hard {total}"

                self.score_label.config(text=score_text)
            elif len(self.hands[0]) >= 1:
                # Show upcard value
                upcard = self.hands[0][0]
                rank = upcard[0]
                if rank in ['J', 'Q', 'K']:
                    value = 10
                elif rank in ['T', '10']:  # Handle both T and 10
                    value = 10
                elif rank == 'A':
                    value = 11
                else:
                    value = int(rank)
                self.score_label.config(text=f"Up card {value}")
            else:
                self.score_label.config(text="")
        else:
            # Player score - ALWAYS show if cards exist
            if self.hands[0]:  # If player has any cards
                score_text = self.get_score_display()
                self.score_label.config(text=score_text if score_text else "")
            else:
                self.score_label.config(text="")

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
        val1 = 10 if rank1 in ['T', '10', 'J', 'Q', 'K'] else (11 if rank1 == 'A' else int(rank1))
        val2 = 10 if rank2 in ['T', '10', 'J', 'Q', 'K'] else (11 if rank2 == 'A' else int(rank2))

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
        """Get formatted score display text like in screenshot."""
        score = self.calculate_score(hand_idx)
        if score == 0:
            return ""

        if hand_idx is None:
            hand_idx = self.current_hand

        if hand_idx >= len(self.hands):
            return ""

        hand = self.hands[hand_idx]

        # Determine if hand is soft
        has_usable_ace = False
        if hand:
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

            # Check if we have a usable ace (counted as 11)
            while total > 21 and aces > 0:
                total -= 10
                aces -= 1
            has_usable_ace = aces > 0

        if score > 21:
            return f"Bust {score}"  # Like "Bust 22"
        elif score == 21 and len(hand) == 2:
            return f"Blackjack!"  # Natural 21
        elif has_usable_ace:
            return f"Soft {score}"  # Like "Soft 18"
        else:
            return f"Hard {score}"  # Like "Hard 16"

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
