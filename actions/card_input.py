class CardInputHandler:
    def __init__(self, app):
        self.app = app

    def handle_shared_card(self, rank, suit):
        if self.app.game_state.is_play_phase():
            self._handle_play_phase_card(rank, suit)
        else:
            self._handle_dealing_phase_card(rank, suit)

    def _handle_dealing_phase_card(self, rank, suit):
        order = list(reversed(self.app.game_state._active_seats))
        if self.app.game_state._focus_idx >= len(order):
            return
        seat = order[self.app.game_state._focus_idx]
        if seat == self.app.game_state.seat:
            return  # Player's own zone; skip
        seat_panel = self.app.game_state.seat_hands[seat]
        print(f"[SEAT_INPUT] Adding {rank}{suit} to seat {seat}")

        # Record state BEFORE advancing the flow
        self.app.action_handler.undo_manager.record_action(
            seat, rank, suit,
            hand_idx=seat_panel.current_hand,
            is_hole=False,
        )

        seat_panel.add_card(rank, suit)  # This updates data and UI
        seat_panel.update_display()  # Refresh seat immediately
        self.app.game_state.comp_panel.log_card(rank)
        self.app.advance_flow()
        if hasattr(self.app, 'focus_manager'):
            self.app.focus_manager.set_focus()
        else:
            self.app.set_focus()

    def _handle_play_phase_card(self, rank, suit):
        order = list(reversed(self.app.game_state._active_seats))
        if self.app.game_state._focus_idx >= len(order):
            return

        seat = order[self.app.game_state._focus_idx]
        if seat == self.app.game_state.seat:
            return  # Player’s panel handles itself

        seat_panel = self.app.game_state.seat_hands[seat]
        print(f"[SEAT_INPUT] (play phase) Adding {rank}{suit} to seat {seat}")

        self.app.action_handler.undo_manager.record_action(
            seat, rank, suit,
            hand_idx=seat_panel.current_hand,
            is_hole=False,
        )

        seat_panel.add_card(rank, suit)
        seat_panel.update_display()
        self.app.game_state.comp_panel.log_card(rank)

        # Only move on when the active hand is completed
        if seat_panel.is_current_hand_done():
            # Advance to the next split hand if it exists
            more_hands = seat_panel.advance_to_next_split_hand()
            if not more_hands:  # seat finished completely
                self.app.game_state.advance_play_focus()

                # Refresh focus/highlight
            if hasattr(self.app, 'focus_manager'):
                self.app.focus_manager.set_focus()
            else:
                self.app.set_focus()

