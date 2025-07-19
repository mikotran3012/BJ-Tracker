class SplitHandler:
    '''Handles split logic and hand completion.'''

    def __init__(self, app):
        self.app = app

    def handle_shared_split(self):
        '''Handle split action from shared panel.'''
        # Split actions only occur during the play phase and only for
        # non-player seats.  We look up the currently focused seat from
        # ``GameState`` and attempt to split that hand if allowed.
        if not self.app.game_state.is_play_phase():
            return

        current_seat = self.app.game_state.get_current_seat()
        if not current_seat or current_seat == self.app.game_state.seat:
            # Either no seat is focused or it's the player's seat.  The
            # player panel handles its own split logic elsewhere.
            return

        seat_panel = self.app.game_state.seat_hands[current_seat]

        # Validate the current hand can actually be split using the
        # panel's helper.  ``split_hand`` already updates the UI and
        # resets state when successful.
        if seat_panel.can_split():
            if seat_panel.split_hand():
                # Record state so a global undo can revert the split
                self.app.action_handler.undo_manager.record_split(current_seat, seat_panel)
                # After a successful split we keep the focus on the same
                # seat so the user can play the first split hand.
                self._ensure_focus()
        else:
            # Invalid split attempt – simply ignore and keep focus.
            self._ensure_focus()

    def handle_shared_stand(self):
        '''Handle stand action with split progression.'''
        # Stand is similar to a hand completion.  We mark the current
        # hand as stood and either advance to the next split hand or to
        # the next seat in the focus order.
        if not self.app.game_state.is_play_phase():
            return

        current_seat = self.app.game_state.get_current_seat()
        if not current_seat or current_seat == self.app.game_state.seat:
            return

        seat_panel = self.app.game_state.seat_hands[current_seat]

        # ``stand`` returns ``True`` when all split hands are finished.
        seat_done = seat_panel.stand()

        if seat_done:
            # Move focus to the next player when the seat is completely
            # finished.  Otherwise focus stays on the same seat for the
            # next split hand.
            self.app.game_state.advance_play_focus()

        self._ensure_focus()

    def is_seat_completely_done(self, seat_panel):
        '''Check if a seat is completely done with all hands.'''
        # Seat is done if surrendered or flagged as done.
        if seat_panel.is_surrendered or seat_panel.is_done:
            return True

        # Split hands require checking the current hand index and score.
        if len(seat_panel.hands) > 1:
            # If we've progressed past the last hand the seat is finished.
            if seat_panel.current_hand >= len(seat_panel.hands):
                return True

            # On the last hand, completion depends on the score or bust
            if seat_panel.current_hand == len(seat_panel.hands) - 1:
                score = seat_panel.calculate_score(seat_panel.current_hand)
                return score >= 21 or seat_panel.is_busted or seat_panel.is_done

            # Otherwise there are more hands to play.
            return False

        # Single hand logic: bust or score >= 21 means done.
        if seat_panel.is_busted:
            return True

        score = seat_panel.calculate_score(0)
        return score >= 21

    def _ensure_focus(self):
        '''Ensure proper focus management.'''
        if hasattr(self.app, 'focus_manager'):
            self.app.focus_manager.set_focus()
        else:
            self.app.set_focus()