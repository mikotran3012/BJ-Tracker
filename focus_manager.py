# core/focus_manager.py
"""
Manages focus and game flow logic for Blackjack Tracker.
Handles the complex logic of who plays when, including split hand management.
"""

import tkinter as tk
from constants import SEATS


class FocusManager:
    """Manages focus and turn order logic."""

    def __init__(self, game_state):
        self.game_state = game_state

    def set_focus(self):
        """Main focus management - delegates to phase-specific handlers."""
        self._reset_all_focus()

        if self.game_state.is_manual_mode():
            self._enable_manual_mode()
            return

        if self.game_state.is_play_phase():
            self._handle_play_phase_focus()
        else:
            self._handle_dealing_phase_focus()

    def _reset_all_focus(self):
        """Reset all UI focus states."""
        # Reset seat panels
        for panel in self.game_state.seat_hands.values():
            panel.highlight(active=False)
            panel._hide_action_buttons()

        # Reset player panel
        if self.game_state.player_panel:
            self.game_state.player_panel.set_enabled(False)
            if hasattr(self.game_state.player_panel, '_hide_action_buttons'):
                self.game_state.player_panel._hide_action_buttons()

        # Reset shared input panel
        if self.game_state.shared_input_panel:
            self.game_state.shared_input_panel.set_enabled(False)

        # Reset dealer panel
        if self.game_state.dealer_panel:
            self.game_state.dealer_panel.set_enabled(False)

    def _enable_manual_mode(self):
        """Enable all panels for manual input."""
        if self.game_state.shared_input_panel:
            self.game_state.shared_input_panel.set_enabled(True)
        if self.game_state.player_panel:
            self.game_state.player_panel.set_enabled(True)
        if self.game_state.dealer_panel:
            self.game_state.dealer_panel.set_enabled(True)

    def _handle_dealing_phase_focus(self):
        """Handle focus during initial card dealing."""
        order = self.game_state.get_dealing_order()
        n = len(order)

        if self.game_state._deal_step < 2:
            if self.game_state._focus_idx < n:
                seat = order[self.game_state._focus_idx]
                if seat == self.game_state.seat:
                    self._focus_player_dealing(seat)
                else:
                    self._focus_other_seat_dealing(seat)
            elif self.game_state._focus_idx == n:
                self._focus_dealer_dealing()
        else:
            # Enter play phase
            self.game_state._play_phase = True
            self.game_state._focus_idx = 0
            self.set_focus()

    def _focus_player_dealing(self, seat):
        """Focus player during dealing phase."""
        cards_needed = self.game_state._deal_step + 1
        if len(self.game_state.player_panel.hands[0]) >= cards_needed:
            self.game_state.advance_deal_step()
            self.set_focus()
            return
        self.game_state.player_panel.update_mode(False)
        self.game_state.player_panel.set_enabled(True)
        self.game_state.shared_input_panel.set_enabled(False)
        self.game_state.dealer_panel.set_enabled(False)
        if seat in self.game_state.seat_hands:
            self.game_state.seat_hands[seat].highlight(active=True)

    def _focus_other_seat_dealing(self, seat):
        """Focus other seat during dealing phase."""
        self.game_state.player_panel.set_enabled(False)
        self.game_state.shared_input_panel.set_enabled(True)
        self.game_state.dealer_panel.set_enabled(False)
        self.game_state.seat_hands[seat].highlight(active=True)

    def _focus_dealer_dealing(self):
        """Focus dealer during dealing phase."""
        if self.game_state._deal_step == 0:
            # Dealer upcard
            self.game_state.dealer_panel.set_enabled(True)
            self.game_state.shared_input_panel.set_enabled(False)
            self.game_state.player_panel.set_enabled(False)
        elif self.game_state._deal_step == 1:
            # Dealer hole card - only mystery card allowed
            self.game_state.dealer_panel.set_enabled(True, hole_phase=True)
            self.game_state.shared_input_panel.set_enabled(False)
            self.game_state.player_panel.set_enabled(False)

    def _handle_play_phase_focus(self):
        """Handle focus during play phase - FIXED for proper split handling."""
        if self.game_state.is_dealer_turn():
            # All players done, dealer plays
            self.game_state.dealer_panel.set_enabled(True)
            return

        current_seat = self.game_state.get_current_seat()
        if not current_seat:
            return

        if self.game_state.is_player_turn():
            self._focus_player_play()
        else:
            self._focus_other_seat_play(current_seat)

    def _focus_player_play(self):
        """Focus player during play phase - without action buttons."""
        player_panel = self.game_state.player_panel
        if not player_panel.is_done and not player_panel.is_busted and not player_panel.is_surrendered:
            if self.game_state.seat in self.game_state.seat_hands:
                self.game_state.seat_hands[self.game_state.seat].highlight(active=True)
            player_panel.update_mode(True)
            player_panel.set_enabled(True)
            # REMOVED: self._show_player_action_buttons()
        else:
            self.game_state.advance_play_focus()
            self.set_focus()

    def _focus_other_seat_play(self, seat):
        """Focus other seat during play phase - FIXED for split handling."""
        seat_panel = self.game_state.seat_hands[seat]

        if self._is_seat_completely_done(seat_panel):
            print(f"FOCUS: Seat {seat} completely done, advancing")
            self.game_state.advance_play_focus()
            self.set_focus()
        else:
            print(f"FOCUS: Seat {seat} playing hand {seat_panel.current_hand + 1}")
            self.game_state.shared_input_panel.set_enabled(True)
            seat_panel.highlight(active=True)
            self._show_seat_action_buttons(seat_panel)

    def _is_seat_completely_done(self, seat_panel):
        """FIXED: Proper detection of split hand completion."""
        # If surrendered or globally done, then yes
        if seat_panel.is_surrendered or seat_panel.is_done:
            return True

        # If single hand, check normal completion
        if len(seat_panel.hands) == 1:
            if seat_panel.is_busted:
                return True
            score = seat_panel.calculate_score(0)
            return score >= 21

        # For split hands - FIXED logic
        print(
            f"COMPLETION_CHECK: {seat_panel.seat} has {len(seat_panel.hands)} hands, current: {seat_panel.current_hand}")

        # If current hand index is beyond available hands, we're done
        if seat_panel.current_hand >= len(seat_panel.hands):
            print(f"COMPLETION_CHECK: Beyond available hands - DONE")
            return True

        # Check if we're on the last hand AND it's finished
        if seat_panel.current_hand == len(seat_panel.hands) - 1:
            current_score = seat_panel.calculate_score(seat_panel.current_hand)
            is_last_hand_done = current_score >= 21 or seat_panel.is_done or seat_panel.is_busted
            print(f"COMPLETION_CHECK: Last hand (score: {current_score}, done: {is_last_hand_done})")
            return is_last_hand_done

        # Still have more hands to play
        print(f"COMPLETION_CHECK: More hands to play")
        return False

    def _show_seat_action_buttons(self, seat_panel):
        """Show action buttons for other seats."""
        if hasattr(seat_panel, '_hide_action_buttons'):
            seat_panel._hide_action_buttons()

        if seat_panel.is_done or seat_panel.is_busted or seat_panel.is_surrendered:
            return

        # Only show skip button for other seats
        if hasattr(seat_panel, 'skip_btn'):
            seat_panel.skip_btn.pack(side=tk.LEFT, padx=1)

    def advance_to_next_focus(self):
        """Advance to next focus position."""
        if self.game_state.is_play_phase():
            self.game_state.advance_play_focus()
        else:
            self.game_state.advance_deal_step()
        self.set_focus()

    def can_advance_focus(self):
        """Check if focus can be advanced."""
        if self.game_state.is_play_phase():
            return self.game_state._focus_idx < len(self.game_state.get_dealing_order())
        else:
            return self.game_state._deal_step < 2

    def get_focus_info(self):
        """Get current focus information for debugging."""
        current_seat = self.game_state.get_current_seat()

        info = {
            'phase': 'play' if self.game_state.is_play_phase() else 'deal',
            'deal_step': self.game_state._deal_step,
            'focus_idx': self.game_state._focus_idx,
            'current_seat': current_seat,
            'is_dealer_turn': self.game_state.is_dealer_turn(),
            'is_player_turn': self.game_state.is_player_turn(),
            'auto_focus': not self.game_state.is_manual_mode(),
            'dealing_order': self.game_state.get_dealing_order()
        }

        # Add seat-specific info if available
        if current_seat and current_seat in self.game_state.seat_hands:
            seat_panel = self.game_state.seat_hands[current_seat]
            info['seat_info'] = {
                'current_hand': seat_panel.current_hand,
                'num_hands': len(seat_panel.hands),
                'is_done': seat_panel.is_done,
                'is_busted': seat_panel.is_busted,
                'is_surrendered': seat_panel.is_surrendered,
                'completely_done': self._is_seat_completely_done(seat_panel)
            }

        return info

    def print_focus_info(self):
        """Print current focus information for debugging."""
        info = self.get_focus_info()
        print("=== FOCUS INFO ===")
        for key, value in info.items():
            if key == 'seat_info':
                print(f"{key}:")
                for subkey, subvalue in value.items():
                    print(f"  {subkey}: {subvalue}")
            else:
                print(f"{key}: {value}")
        print("==================")

    def validate_focus_state(self):
        """Validate current focus state for consistency."""
        errors = []

        # Check if focus index is reasonable
        if self.game_state._focus_idx < 0:
            errors.append(f"Invalid focus index: {self.game_state._focus_idx}")

        # Check if focus index is within bounds
        max_focus = len(self.game_state.get_dealing_order()) + 1  # +1 for dealer
        if self.game_state._focus_idx > max_focus:
            errors.append(f"Focus index {self.game_state._focus_idx} exceeds max {max_focus}")

        # Check if current seat exists
        current_seat = self.game_state.get_current_seat()
        if current_seat and current_seat not in self.game_state.seat_hands:
            errors.append(f"Current seat {current_seat} not found in seat_hands")

        # Check if deal step is reasonable
        if self.game_state._deal_step < 0:
            errors.append(f"Invalid deal step: {self.game_state._deal_step}")

        return errors

    def reset_focus(self):
        """Reset focus to initial state."""
        self.game_state._focus_idx = 0
        self.game_state._deal_step = 0
        self.game_state._play_phase = False
        self.set_focus()

    def force_manual_mode(self):
        """Force manual mode and enable all panels."""
        self.game_state.enable_manual_mode()
        self._enable_manual_mode()

    def force_auto_mode(self):
        """Force auto mode and set proper focus."""
        self.game_state.enable_auto_mode()
        self.set_focus()

    def skip_current_turn(self):
        """Skip the current turn and advance focus."""
        if self.game_state.is_play_phase():
            current_seat = self.game_state.get_current_seat()
            if current_seat and current_seat in self.game_state.seat_hands:
                seat_panel = self.game_state.seat_hands[current_seat]
                if not self._is_seat_completely_done(seat_panel):
                    # Mark current hand as done and advance
                    seat_panel.stand()

        self.advance_to_next_focus()

    def handle_split_completion(self, seat):
        """Handle when a split hand is completed."""
        if seat not in self.game_state.seat_hands:
            return

        seat_panel = self.game_state.seat_hands[seat]

        # Check if there are more split hands to play
        if seat_panel.current_hand < len(seat_panel.hands) - 1:
            # More split hands - advance to next hand, stay on same seat
            seat_panel.current_hand += 1
            seat_panel.update_display()
            self.set_focus()  # Stay on same seat
        else:
            # All hands done - advance to next player
            seat_panel.is_done = True
            seat_panel.update_display()
            self.game_state.advance_play_focus()
            self.set_focus()

    def handle_hand_completion(self, seat, hand_idx=None):
        """Handle when any hand is completed (21, bust, stand)."""
        if seat not in self.game_state.seat_hands:
            return

        seat_panel = self.game_state.seat_hands[seat]

        # If this is a split hand, use split completion logic
        if len(seat_panel.hands) > 1:
            self.handle_split_completion(seat)
        else:
            # Single hand - just advance to next player
            seat_panel.is_done = True
            seat_panel.update_display()
            self.game_state.advance_play_focus()
            self.set_focus()

    def __str__(self):
        """String representation of focus state."""
        current_seat = self.game_state.get_current_seat()
        phase = 'play' if self.game_state.is_play_phase() else 'deal'
        return f"FocusManager(phase={phase}, seat={current_seat}, idx={self.game_state._focus_idx})"

    def __repr__(self):
        """Detailed string representation."""
        return f"FocusManager(deal_step={self.game_state._deal_step}, focus_idx={self.game_state._focus_idx}, play_phase={self.game_state._play_phase})"
