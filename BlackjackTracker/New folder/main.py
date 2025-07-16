# main.py - COMPLETE FIXED VERSION
"""
Main application for the Blackjack Card Tracker Pro with enhanced blackjack rules.
Enhanced with rules engine integration for proper game logic.
FIXED: Updated to use "10" instead of "T" and work with improved panels.
"""

import tkinter as tk
import sys
import os

# Ensure proper imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from constants import SEATS, RANKS, COLORS, DEFAULT_DECKS, normalize_rank_display, normalize_rank_internal
from ui.panels import CompPanel, SeatHandPanel
from ui.input_panels import SharedInputPanel, PlayerOrDealerPanel
from ui.dialogs import SeatSelectDialog
from rules_engine import BlackjackRules, Card, Hand


class BlackjackTrackerApp(tk.Tk):
    """Main application window for the Blackjack Tracker with rules integration."""

    def __init__(self):
        super().__init__()
        self.title("Blackjack Card Tracker Pro - With Rules Engine")
        self.geometry("1200x800")  # Smaller window since no right panel needed
        self.configure(bg=COLORS['bg_main'])

        # Initialize rules engine
        self.rules = BlackjackRules()

        # Application state
        self.decks = DEFAULT_DECKS
        self.seat = None
        self.seat_index = 0
        self._deal_step = 0
        self._focus_idx = 0
        self._auto_focus = True
        self._play_phase = False
        self._active_seats = []

        # Track hands for rules engine
        self.seat_rule_hands = {}  # Maps seat to Hand objects
        self.player_rule_hands = []  # List of Hand objects for player
        self.dealer_rule_hand = Hand([])  # Dealer's Hand object

        self._setup_ui()
        self._setup_bindings()

        # Prompt for seat selection after UI is built
        self.after(200, self.prompt_seat_selection)

    def _setup_ui(self):
        """Setup the main UI components - compact left layout without rules panel."""
        # Main container - everything on left side
        main_container = tk.Frame(self, bg=COLORS['bg_main'])
        main_container.pack(fill='both', expand=True, padx=8, pady=8)

        # 1. Top: Composition panel
        comp_container = tk.Frame(main_container, bg=COLORS['bg_main'])
        comp_container.pack(anchor='w', pady=4)

        self.comp_panel = CompPanel(comp_container, self.on_decks_change, self.decks)
        self.comp_panel.pack()

        # 2. Player seats (compact, aligned with composition)
        seats_container = tk.Frame(main_container, bg=COLORS['bg_main'])
        seats_container.pack(anchor='w', pady=4)

        tk.Label(seats_container, text="SEATS", font=('Segoe UI', 9, 'bold'),
                 bg=COLORS['bg_main'], fg=COLORS['fg_white']).pack(anchor='w')

        self.seat_hands = {}
        seats_row = tk.Frame(seats_container, bg=COLORS['bg_main'])
        seats_row.pack(anchor='w')

        for si, seat in enumerate(SEATS):
            self.seat_hands[seat] = SeatHandPanel(
                seats_row, seat, False, False,
                on_action=self.handle_seat_action
            )
            self.seat_hands[seat].pack(side=tk.LEFT, padx=1)

        # 3. Shared input (aligned with composition)
        input_container = tk.Frame(main_container, bg=COLORS['bg_main'])
        input_container.pack(anchor='w', pady=4)

        self.shared_input_panel = SharedInputPanel(
            input_container,
            self.handle_shared_card,
            self.handle_shared_undo
        )
        # Set up action button callbacks
        self.shared_input_panel.set_action_callbacks(
            on_stand=self.handle_shared_stand,
            on_split=self.handle_shared_split
        )
        self.shared_input_panel.pack()

        # 4. Game panels container (dealer + player side by side, much smaller)
        game_panels_container = tk.Frame(main_container, bg=COLORS['bg_main'], height=200)
        game_panels_container.pack(anchor='w', fill='x', pady=8)
        game_panels_container.pack_propagate(False)  # Maintain smaller height

        # Dealer panel (left side, smaller)
        dealer_container = tk.Frame(game_panels_container, bg=COLORS['bg_main'], width=350)
        dealer_container.pack(side=tk.LEFT, fill='y', anchor='nw', padx=(0, 10))
        dealer_container.pack_propagate(False)

        self.dealer_panel = PlayerOrDealerPanel(
            dealer_container, "DEALER", False, True,
            self.on_dealer_card, self.on_dealer_undo,
            hole_card_reveal=True
        )
        self.dealer_panel.pack(fill='both', expand=True)

        # Player panel (right side, smaller)
        player_container = tk.Frame(game_panels_container, bg=COLORS['bg_main'], width=350)
        player_container.pack(side=tk.LEFT, fill='y', anchor='nw')
        player_container.pack_propagate(False)

        self.player_panel = PlayerOrDealerPanel(
            player_container, "PLAYER", True, False,
            self.on_player_card, self.on_player_undo,
            on_action=self.handle_player_action
        )
        self.player_panel.pack(fill='both', expand=True)

        # Bottom space reserved for future features
        bottom_space = tk.Frame(main_container, bg='#444444', height=150)
        bottom_space.pack(fill='x', pady=(10, 0))

        tk.Label(bottom_space, text="RESERVED FOR FUTURE FEATURES",
                 font=('Segoe UI', 12, 'bold'),
                 bg='#444444', fg='white').pack(expand=True)

    def convert_ui_hand_to_rules_hand(self, ui_cards, is_split=False, splits_count=0):
        """Convert UI card list to rules engine Hand object."""
        rule_cards = []
        for rank, suit in ui_cards:
            # Convert 10 back to T for rules engine compatibility
            internal_rank = normalize_rank_internal(rank)
            rule_cards.append(Card(internal_rank, suit))
        return Hand(rule_cards, is_split=is_split, splits_count=splits_count)

    def validate_action_with_rules(self, action, hand_cards, is_split=False):
        """Validate if an action is allowed according to rules."""
        if not hand_cards:
            return False

        hand = self.convert_ui_hand_to_rules_hand(hand_cards, is_split)

        if action == 'split':
            return self.rules.can_split(hand)
        elif action == 'double':
            return self.rules.can_double(hand)
        elif action == 'surrender':
            return self.rules.can_surrender(hand)
        elif action == 'hit':
            return not self.rules.is_bust(hand)  # Can't hit if already bust
        else:
            return True  # Stand and skip are always allowed

    def show_action_buttons_with_rules(self, panel):
        """Show action buttons - simplified for player vs other seats."""
        if not hasattr(panel, 'show_action_buttons'):
            return

        # Hide all buttons first
        if hasattr(panel, '_hide_action_buttons'):
            panel._hide_action_buttons()

        if panel.is_done or panel.is_busted or panel.is_surrendered:
            return

        # For player panel - show all action buttons
        if panel == self.player_panel:
            current_hand_cards = panel.hands[panel.current_hand] if panel.hands else []
            is_split_hand = len(panel.hands) > 1

            # Show available actions
            if hasattr(panel, 'hit_btn'):
                can_hit = self.validate_action_with_rules('hit', current_hand_cards, is_split_hand)
                if can_hit:
                    panel.hit_btn.pack(side=tk.LEFT, padx=1)

            if hasattr(panel, 'stand_btn'):
                panel.stand_btn.pack(side=tk.LEFT, padx=1)

            if hasattr(panel, 'double_btn'):
                can_double = self.validate_action_with_rules('double', current_hand_cards, is_split_hand)
                if can_double:
                    panel.double_btn.pack(side=tk.LEFT, padx=1)

            if hasattr(panel, 'surrender_btn'):
                can_surrender = self.validate_action_with_rules('surrender', current_hand_cards, is_split_hand)
                if can_surrender:
                    panel.surrender_btn.pack(side=tk.LEFT, padx=1)

            if hasattr(panel, 'split_btn'):
                can_split = self.validate_action_with_rules('split', current_hand_cards, is_split_hand)
                if can_split:
                    panel.split_btn.pack(side=tk.LEFT, padx=1)

            if hasattr(panel, 'skip_btn'):
                panel.skip_btn.pack(side=tk.LEFT, padx=1)

        else:
            # For other seat panels - only show skip button
            if hasattr(panel, 'skip_btn'):
                panel.skip_btn.pack(side=tk.LEFT, padx=1)

    def _setup_bindings(self):
        """Setup keyboard bindings."""
        self.bind_all('<Key>', self.handle_key)

    def prompt_seat_selection(self):
        """Show seat selection dialog."""
        dialog = SeatSelectDialog(self)
        self.seat = dialog.selected.get()
        self.seat_index = SEATS.index(self.seat)

        for s, panel in self.seat_hands.items():
            panel.is_your_seat = (s == self.seat)
            panel.highlight(active=False)

        self._active_seats = SEATS.copy()
        self.reset_flow()

    def on_decks_change(self):
        """Handle deck count change."""
        self.decks = self.comp_panel.decks
        self.reset_flow()

    def reset_flow(self):
        """Reset the dealing flow and all panels."""
        self.comp_panel.reset()

        for s, p in self.seat_hands.items():
            p.reset()
            p.highlight(active=False)

        self.player_panel.reset()
        self.dealer_panel.reset()

        self._deal_step = 0
        self._focus_idx = 0
        self._auto_focus = True
        self._play_phase = False
        self.dealer_panel.hole_card_enabled = False

        # Reset rules tracking
        self.seat_rule_hands = {}
        self.player_rule_hands = []
        self.dealer_rule_hand = Hand([])

        self.set_focus()

    def set_focus(self):
        """Handle focus for both dealing and play phases."""
        # Reset all highlights and buttons
        for seat, panel in self.seat_hands.items():
            panel.highlight(active=False)
            panel._hide_action_buttons()
        self.player_panel.set_enabled(False)
        self.shared_input_panel.set_enabled(False)
        self.dealer_panel.set_enabled(False)
        self.player_panel._hide_action_buttons()

        if not self._auto_focus:
            # Manual mode - enable all
            self.shared_input_panel.set_enabled(True)
            self.player_panel.set_enabled(True)
            self.dealer_panel.set_enabled(True)
            return

        if self._play_phase:
            # Play phase auto-focus
            self._handle_play_phase_focus()
        else:
            # Initial dealing phase
            self._handle_dealing_phase_focus()

    def _handle_dealing_phase_focus(self):
        """Handle focus during initial dealing (first 2 cards)."""
        order = list(reversed(self._active_seats))
        n = len(order)

        if self._deal_step < 2:
            if self._focus_idx < n:
                seat = order[self._focus_idx]
                if seat == self.seat:
                    # Check if player needs more cards for this deal step
                    cards_needed = self._deal_step + 1
                    if len(self.player_panel.hands[0]) >= cards_needed:
                        self.advance_flow()
                        return
                    self.player_panel.set_enabled(True)
                    self.shared_input_panel.set_enabled(False)
                    self.dealer_panel.set_enabled(False)
                else:
                    self.player_panel.set_enabled(False)
                    self.shared_input_panel.set_enabled(True)
                    self.dealer_panel.set_enabled(False)
                    self.seat_hands[seat].highlight(active=True)
            elif self._focus_idx == n:
                # Dealer's turn
                if self._deal_step == 0:
                    # Dealer upcard
                    self.dealer_panel.set_enabled(True)
                    self.shared_input_panel.set_enabled(False)
                    self.player_panel.set_enabled(False)
                elif self._deal_step == 1:
                    # Dealer hole card (show mystery button)
                    self.dealer_panel.set_enabled(True)
                    self.shared_input_panel.set_enabled(False)
                    self.player_panel.set_enabled(False)
        else:
            # After 2nd cards are dealt, enter play phase
            self._play_phase = True
            self._focus_idx = 0
            self.set_focus()

    def _handle_play_phase_focus(self):
        """Handle focus during play phase (hitting/standing) - IMPROVED for splits."""
        order = list(reversed(self._active_seats))

        if self._focus_idx >= len(order):
            # All players done, dealer plays
            self.dealer_panel.set_enabled(True)
            return

        seat = order[self._focus_idx]

        if seat == self.seat:
            # Player's turn
            if not self.player_panel.is_done and not self.player_panel.is_busted and not self.player_panel.is_surrendered:
                self.player_panel.set_enabled(True)
                self.show_action_buttons_with_rules(self.player_panel)
            else:
                # Player is done, move to next
                self.advance_play_focus()
        else:
            # Other seat's turn - check if they should still be playing
            seat_panel = self.seat_hands[seat]

            # Use the new method to check if focus should advance
            if seat_panel.should_advance_focus():
                # This seat is completely done, move to next player
                self.advance_play_focus()
            else:
                # This seat still has hands to play
                self.shared_input_panel.set_enabled(True)
                seat_panel.highlight(active=True)
                self.show_action_buttons_with_rules(seat_panel)

    def advance_flow(self):
        """Advance to the next position in the dealing flow."""
        self._focus_idx += 1
        order = list(reversed(self._active_seats))

        if self._focus_idx > len(order):  # Done with all seats + dealer in this card step
            self._focus_idx = 0
            self._deal_step += 1
            if self._deal_step >= 2:
                # Enter play phase
                self._play_phase = True
                self._focus_idx = 0
        self.set_focus()

    def advance_play_focus(self):
        """Advance focus during play phase."""
        self._focus_idx += 1
        self.set_focus()

    # -- Action handlers --
    def handle_seat_action(self, seat, action, hand_idx=0):
        """Handle actions from seat panels with rules validation."""
        seat_panel = self.seat_hands[seat]
        current_hand_cards = seat_panel.hands[hand_idx] if seat_panel.hands else []
        is_split_hand = len(seat_panel.hands) > 1

        # Validate action with rules engine
        if not self.validate_action_with_rules(action, current_hand_cards, is_split_hand):
            print(f"Action '{action}' not allowed by rules for seat {seat}!")
            return

        if action == 'hit':
            # Enable input for this seat
            self.shared_input_panel.set_enabled(True)
            seat_panel.highlight(active=True)
        elif action == 'stand':
            seat_panel.stand()
            self.advance_play_focus()
        elif action == 'double':
            # Hit one card then stand
            self.shared_input_panel.set_enabled(True)
            seat_panel.highlight(active=True)
            # Note: After card input, will auto-stand
        elif action == 'surrender':
            seat_panel.surrender()
            self.advance_play_focus()
        elif action == 'split':
            if seat_panel.split_hand():
                # Stay on same seat to play first split hand
                self.set_focus()
        elif action == 'skip':
            self.advance_play_focus()

    def handle_player_action(self, action, hand_idx=0):
        """Handle player actions with rules validation."""
        current_hand_cards = self.player_panel.hands[hand_idx] if self.player_panel.hands else []
        is_split_hand = len(self.player_panel.hands) > 1

        # Validate action with rules engine
        if not self.validate_action_with_rules(action, current_hand_cards, is_split_hand):
            print(f"Action '{action}' not allowed by rules!")
            return

        # Proceed with action if valid
        if action == 'hit':
            self.player_panel.set_enabled(True)
        elif action == 'stand':
            self.player_panel.stand()
            self.advance_play_focus()
        elif action == 'double':
            self.player_panel.set_enabled(True)
        elif action == 'surrender':
            self.player_panel.surrender()
            self.advance_play_focus()
        elif action == 'split':
            if self.player_panel.split_hand():
                self.set_focus()
        elif action == 'skip':
            self.advance_play_focus()

    # -- Card input handlers --
    def handle_shared_card(self, rank, suit):
        """Handle card input from shared panel - IMPROVED for splits."""
        if self._play_phase:
            # Play phase - card goes to currently focused seat
            order = list(reversed(self._active_seats))
            if self._focus_idx < len(order):
                seat = order[self._focus_idx]
                if seat != self.seat:
                    seat_panel = self.seat_hands[seat]

                    print(f"MAIN: Adding {rank}{suit} to {seat} (current_hand={seat_panel.current_hand})")  # Debug

                    # Use the explicit method to ensure it goes to current hand
                    seat_panel.add_card_to_current_hand(rank, suit)
                    self.comp_panel.log_card(rank)

                    # Check if current hand is done (21 or bust)
                    if seat_panel.is_current_hand_done():
                        print(f"MAIN: {seat} hand {seat_panel.current_hand + 1} is done")  # Debug
                        # Current hand is done, check if more hands to play
                        if not seat_panel.advance_to_next_split_hand():
                            # No more hands, player is completely done
                            print(f"MAIN: Seat {seat} - all hands completed, advancing to next player")
                            self.advance_play_focus()
                        else:
                            # More split hands to play, stay on same seat
                            print(f"MAIN: Seat {seat} - continuing with next split hand")
                            self.set_focus()
                    else:
                        # Continue with current hand
                        print(f"MAIN: {seat} hand {seat_panel.current_hand + 1} continues")  # Debug
                        self.set_focus()
        else:
            # Dealing phase logic remains the same
            order = list(reversed(self._active_seats))
            if self._focus_idx >= len(order):
                return

            seat = order[self._focus_idx]
            if seat == self.seat:
                return

            self.seat_hands[seat].add_card(rank, suit)  # Use regular method for dealing phase
            self.comp_panel.log_card(rank)
            self.advance_flow()

    def handle_shared_undo(self):
        """Handle undo from shared panel."""
        if self._play_phase:
            # Undo from currently focused seat
            order = list(reversed(self._active_seats))
            if self._focus_idx < len(order):
                seat = order[self._focus_idx]
                if seat != self.seat:
                    seat_panel = self.seat_hands[seat]
                    if seat_panel.hands[seat_panel.current_hand]:
                        last_card = seat_panel.undo()
                        if last_card:
                            self.comp_panel.undo_card(last_card[0])
        else:
            # Dealing phase undo
            order = list(reversed(self._active_seats))
            if self._focus_idx >= len(order):
                return

            seat = order[self._focus_idx]
            if seat == self.seat:
                return

            if self.seat_hands[seat].hands[0]:
                last_card = self.seat_hands[seat].undo()
                if last_card:
                    self.comp_panel.undo_card(last_card[0])

    def handle_shared_stand(self):
        """Handle stand/skip action from shared panel - IMPROVED for splits."""
        if self._play_phase:
            # Stand the currently focused seat
            order = list(reversed(self._active_seats))
            if self._focus_idx < len(order):
                seat = order[self._focus_idx]
                if seat != self.seat:  # Only for other players, not your seat
                    seat_panel = self.seat_hands[seat]

                    print(f"Standing {seat} hand {seat_panel.current_hand + 1}")  # Debug

                    # Use the improved stand method that handles splits
                    completely_done = seat_panel.stand()

                    if completely_done:
                        print(f"Seat {seat} - all hands done, advancing to next player")
                        self.advance_play_focus()
                    else:
                        print(f"Seat {seat} - moved to next split hand, staying on same seat")
                        # Stay on same seat, player needs to play next split hand
                        # Don't call advance_play_focus(), just refresh the current focus
                        self.set_focus()

    def handle_shared_split(self):
        """Handle split action from shared panel."""
        if self._play_phase:
            # Split the currently focused seat
            order = list(reversed(self._active_seats))
            if self._focus_idx < len(order):
                seat = order[self._focus_idx]
                if seat != self.seat:  # Only for other players, not your seat
                    seat_panel = self.seat_hands[seat]

                    # Check if split is valid (need exactly 2 cards of same value)
                    current_hand = seat_panel.hands[seat_panel.current_hand]
                    if len(current_hand) == 2:
                        rank1, rank2 = current_hand[0][0], current_hand[1][0]
                        # Check if same value (handle T/10 conversion)
                        val1 = 10 if rank1 in ['T', '10', 'J', 'Q', 'K'] else (11 if rank1 == 'A' else int(rank1))
                        val2 = 10 if rank2 in ['T', '10', 'J', 'Q', 'K'] else (11 if rank2 == 'A' else int(rank2))

                        if val1 == val2:
                            if seat_panel.split_hand():
                                print(f"Seat {seat} splits hand")
                                # Stay focused on same seat to play first split hand
                                self.set_focus()
                            else:
                                print(f"Seat {seat} - split failed")
                        else:
                            print(f"Seat {seat} - cannot split, cards don't match")
                    else:
                        print(f"Seat {seat} - cannot split, need exactly 2 cards")

    def on_player_card(self, rank, suit, is_hole=False):
        """Handle player card input with rules validation."""
        self.comp_panel.log_card(rank)

        if self._play_phase:
            if len(self.player_panel.hands[self.player_panel.current_hand]) == 3:
                self.player_panel.stand()
                self.advance_play_focus()
            else:
                self.set_focus()
        else:
            self.advance_flow()

    def on_player_undo(self, rank=None, is_hole=False):
        """Handle player undo."""
        if rank:
            self.comp_panel.undo_card(rank)

    def on_dealer_card(self, rank, suit, is_hole=False):
        """Handle dealer card input."""
        if not is_hole:
            self.comp_panel.log_card(rank)
        if not self._play_phase:
            # Only advance during dealing phase
            self.advance_flow()

    def on_dealer_undo(self, rank=None, is_hole=False):
        """Handle dealer undo."""
        if rank and not is_hole:
            self.comp_panel.undo_card(rank)

    def handle_key(self, event):
        """Handle keyboard input - UPDATED for 10 support."""
        char = event.char.upper()

        # Handle special case for T key (convert to 10)
        if char == 'T':
            char = '10'

        # Check if it's a valid rank
        if char in RANKS:
            if self._auto_focus:
                if self._play_phase:
                    # Play phase key input
                    order = list(reversed(self._active_seats))
                    if self._focus_idx < len(order):
                        seat = order[self._focus_idx]
                        if seat == self.seat:
                            self.player_panel.rank_clicked(char)
                        else:
                            self.shared_input_panel.rank_clicked(char)
                    elif self._focus_idx >= len(order):
                        self.dealer_panel.rank_clicked(char)
                else:
                    # Dealing phase key input
                    order = list(reversed(self._active_seats))
                    if self._focus_idx < len(order):
                        seat = order[self._focus_idx]
                        if seat == self.seat:
                            self.player_panel.rank_clicked(char)
                        else:
                            self.shared_input_panel.rank_clicked(char)
                    elif self._focus_idx == len(order):
                        self.dealer_panel.rank_clicked(char)

        elif char == 'U':
            if self._auto_focus:
                if self._play_phase:
                    order = list(reversed(self._active_seats))
                    if self._focus_idx < len(order):
                        seat = order[self._focus_idx]
                        if seat == self.seat:
                            self.player_panel.undo()
                        else:
                            self.handle_shared_undo()
                    elif self._focus_idx >= len(order):
                        self.dealer_panel.undo()
                else:
                    order = list(reversed(self._active_seats))
                    if self._focus_idx < len(order):
                        seat = order[self._focus_idx]
                        if seat == self.seat:
                            self.player_panel.undo()
                        else:
                            self.handle_shared_undo()
                    elif self._focus_idx == len(order):
                        self.dealer_panel.undo()

        elif char == '?':
            # Quick mystery card input for dealer
            if self._auto_focus and not self._play_phase and self._focus_idx == len(list(reversed(self._active_seats))):
                self.dealer_panel.input_mystery_card()

        # Quick action keys for play phase
        elif self._play_phase and self._auto_focus:
            order = list(reversed(self._active_seats))
            if self._focus_idx < len(order):
                seat = order[self._focus_idx]
                if char == 'H':  # Hit
                    if seat == self.seat:
                        self.handle_player_action('hit')
                    else:
                        self.handle_seat_action(seat, 'hit')
                elif char == 'S':  # Stand
                    if seat == self.seat:
                        self.handle_player_action('stand')
                    else:
                        self.handle_seat_action(seat, 'stand')
                elif char == 'D':  # Double
                    if seat == self.seat:
                        self.handle_player_action('double')
                    else:
                        self.handle_seat_action(seat, 'double')
                elif char == 'R':  # Surrender
                    if seat == self.seat:
                        self.handle_player_action('surrender')
                    else:
                        self.handle_seat_action(seat, 'surrender')
                elif char == 'P':  # Split
                    if seat == self.seat:
                        self.handle_player_action('split')
                    else:
                        self.handle_seat_action(seat, 'split')
                elif char == ' ':  # Space = Skip
                    if seat == self.seat:
                        self.handle_player_action('skip')
                    else:
                        self.handle_seat_action(seat, 'skip')


def main():
    """Main entry point for the application."""
    app = BlackjackTrackerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
