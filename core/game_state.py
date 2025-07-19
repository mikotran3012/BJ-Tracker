# core/game_state.py
"""
Centralized game state management for Blackjack Tracker.
Handles all game data and state transitions.
"""

from constants import SEATS, DEFAULT_DECKS


class GameState:
    """Manages all game state and data."""

    def __init__(self, decks=DEFAULT_DECKS):
        # Game configuration
        self.decks = decks
        self.seat = None
        self.seat_index = 0

        # Flow state variables (move these FROM main.py)
        self._deal_step = 0
        self._focus_idx = 0
        self._auto_focus = True
        self._play_phase = False
        self._active_seats = SEATS.copy()

        # UI panel references (set by main.py after UI creation)
        self.comp_panel = None
        self.seat_hands = {}
        self.player_panel = None
        self.dealer_panel = None
        self.shared_input_panel = None

    def reset_game(self):
        """Reset game to initial state."""
        # Reset UI panels
        if self.comp_panel:
            self.comp_panel.reset()

        for panel in self.seat_hands.values():
            panel.reset()
            panel.highlight(active=False)

        if self.player_panel:
            self.player_panel.reset()

        if self.dealer_panel:
            self.dealer_panel.reset()
            self.dealer_panel.hole_card_enabled = False

        # Reset flow state
        self._deal_step = 0
        self._focus_idx = 0
        self._auto_focus = True
        self._play_phase = False

    def set_seat(self, seat):
        """Set player's seat and update UI."""
        self.seat = seat
        self.seat_index = SEATS.index(seat)

        # Update seat panels
        for s, panel in self.seat_hands.items():
            panel.is_your_seat = (s == seat)
            panel.highlight(active=False)

    def advance_deal_step(self):
        """Advance dealing step."""
        self._focus_idx += 1
        order = list(reversed(self._active_seats))

        if self._focus_idx > len(order):
            self._focus_idx = 0
            self._deal_step += 1
            if self._deal_step >= 2:
                self._play_phase = True
                self._focus_idx = 0

    def advance_play_focus(self):
        """Advance focus during play phase."""
        self._focus_idx += 1

    def get_current_seat(self):
        """Get currently focused seat."""
        if not self._play_phase:
            return None
        order = list(reversed(self._active_seats))
        if self._focus_idx < len(order):
            return order[self._focus_idx]
        return None

    def get_current_seat_panel(self):
        """Get currently focused seat panel."""
        current_seat = self.get_current_seat()
        if current_seat and current_seat in self.seat_hands:
            return self.seat_hands[current_seat]
        return None

    def is_dealing_phase(self):
        """Check if in dealing phase."""
        return not self._play_phase and self._deal_step < 2

    def is_play_phase(self):
        """Check if in play phase."""
        return self._play_phase

    def is_manual_mode(self):
        """Check if in manual input mode."""
        return not self._auto_focus

    def enable_manual_mode(self):
        """Enable manual input mode."""
        self._auto_focus = False

    def enable_auto_mode(self):
        """Enable automatic focus mode."""
        self._auto_focus = True

    def get_dealing_order(self):
        """Get the order of seats for dealing."""
        return list(reversed(self._active_seats))

    def get_dealer_focus_index(self):
        """Get the focus index when dealer should be active."""
        return len(self._active_seats)

    def is_dealer_turn(self):
        """Check if it's dealer's turn."""
        return self._focus_idx >= len(self._active_seats)

    def is_player_turn(self):
        """Check if it's the player's turn."""
        if not self._play_phase:
            return False
        current_seat = self.get_current_seat()
        return current_seat == self.seat

    def get_active_seat_count(self):
        """Get number of active seats."""
        return len(self._active_seats)

    def set_decks(self, decks):
        """Set number of decks and trigger reset."""
        self.decks = decks
        self.reset_game()

    def log_card(self, rank):
        """Log a card to the composition panel."""
        if self.comp_panel:
            self.comp_panel.log_card(rank)

    def undo_card(self, rank):
        """Undo a card from the composition panel."""
        if self.comp_panel:
            self.comp_panel.undo_card(rank)

    def get_state_info(self):
        """Get current state information for debugging."""
        return {
            'decks': self.decks,
            'seat': self.seat,
            'deal_step': self._deal_step,
            'focus_idx': self._focus_idx,
            'auto_focus': self._auto_focus,
            'play_phase': self._play_phase,
            'current_seat': self.get_current_seat(),
            'is_dealer_turn': self.is_dealer_turn(),
            'is_player_turn': self.is_player_turn(),
            'dealing_phase': self.is_dealing_phase()
        }

    def print_state(self):
        """Print current state for debugging."""
        state = self.get_state_info()
        print("=== GAME STATE ===")
        for key, value in state.items():
            print(f"{key}: {value}")
        print("==================")

    def validate_state(self):
        """Validate current state for consistency."""
        errors = []

        # Check if seat is valid
        if self.seat and self.seat not in SEATS:
            errors.append(f"Invalid seat: {self.seat}")

        # Check if focus index is reasonable
        if self._focus_idx < 0:
            errors.append(f"Invalid focus index: {self._focus_idx}")

        # Check if deal step is reasonable
        if self._deal_step < 0:
            errors.append(f"Invalid deal step: {self._deal_step}")

        # Check if decks is reasonable
        if self.decks < 1 or self.decks > 8:
            errors.append(f"Invalid deck count: {self.decks}")

        return errors

    def __str__(self):
        """String representation of game state."""
        return f"GameState(seat={self.seat}, phase={'play' if self._play_phase else 'deal'}, focus={self._focus_idx})"

    def __repr__(self):
        """Detailed string representation."""
        return f"GameState(decks={self.decks}, seat={self.seat}, deal_step={self._deal_step}, focus_idx={self._focus_idx}, play_phase={self._play_phase})"
