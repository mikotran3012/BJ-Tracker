import time

class UndoManager:
    """Handles global undo logic with a simple history stack."""

    def __init__(self, app, state=None):
        self.app = app
        self.undo_stack = []
        self.max_undo_history = 50  # keep a reasonably deep history
        gs = app.game_state
        # Only restore focus_idx if state is provided and contains the key
        if state is not None and "focus_idx" in state:
            gs._focus_idx = state["focus_idx"]

        # Restore flow state to where it was before this action
        if state is not None and "focus_idx" in state:
            gs._focus_idx = state["focus_idx"]
            gs._deal_step = state["deal_step"]
            gs._play_phase = state["play_phase"]

        # After restoring state, reset UI focus so the user can continue editing
        # from the seat/hand that was just undone.
        if hasattr(self.app, "focus_manager"):
            self.app.focus_manager.set_focus()
        else:
            self.app.set_focus()

    def record_action(self, seat, rank, suit, *, is_hole=False, hand_idx=0):
        """Record a card input action for later undo."""
        gs = self.app.game_state
        state = {
            "action": "card",
            "seat": seat,
            "rank": rank,
            "suit": suit,
            "is_hole": is_hole,
            "hand_idx": hand_idx,
            "focus_idx": gs._focus_idx,
            "deal_step": gs._deal_step,
            "play_phase": gs._play_phase,
        }
        self.undo_stack.append(state)
        if len(self.undo_stack) > self.max_undo_history:
            self.undo_stack.pop(0)

    def record_split(self, seat, panel):
        """Record a split action so it can be undone."""
        gs = self.app.game_state
        state = {
            "action": "split",
            "seat": seat,
            "hands_before": [list(h) for h in panel.hands],
            "current_hand": panel.current_hand,
            "focus_idx": gs._focus_idx,
            "deal_step": gs._deal_step,
            "play_phase": gs._play_phase,
        }
        self.undo_stack.append(state)
        if len(self.undo_stack) > self.max_undo_history:
            self.undo_stack.pop(0)

    def handle_shared_undo(self, was_done=None):
        """Undo the last recorded action and restore focus."""
        if not self.undo_stack:
            return

        state = self.undo_stack.pop()
        gs = self.app.game_state

        seat = state["seat"]

        if seat == "dealer":
            panel = gs.dealer_panel
        elif seat == "player":
            panel = gs.player_panel
        else:
            panel = gs.seat_hands.get(seat)

        if not panel:
            return

        # Track completion state before undo so callers can reactivate seats
        was_done = getattr(panel, "is_done", False)

        # -- Undo the recorded change -------------------------------------
        if state.get("action") == "card":
            # Prevent removing a protected first card during initial deal
            if (
                self._should_protect_first_card(len(panel.hands[0]))
                and state["deal_step"] == 0
                and not state.get("is_hole", False)
            ):
                # Not allowed; push state back and abort
                self.undo_stack.append(state)
                return None

            # Remove card from the specific hand
            hand_idx = state.get("hand_idx", 0)
            if hasattr(panel, "undo"):
                card = panel.undo(hand_idx)
            else:
                card = None

            # Update comp panel if this wasn't the dealer hole card
            if card and not state.get("is_hole", False):
                gs.comp_panel.undo_card(card[0])

        elif state.get("action") == "split":
            # Revert split by restoring previous hands snapshot
            panel.hands = [list(h) for h in state.get("hands_before", [])]
            panel.current_hand = state.get("current_hand", 0)
            panel.update_display()

        # -----------------------------------------------------------------

        # Restore focus to where it was when the action happened
        if state is not None and "focus_idx" in state:
            gs._focus_idx = state["focus_idx"]
            gs._deal_step = state["deal_step"]
            gs._play_phase = state["play_phase"]

        # Reset UI focus
        if hasattr(self.app, "focus_manager"):
            self.app.focus_manager.set_focus()
        else:
            self.app.set_focus()
        return {"panel": panel, "was_done": was_done}

    def _jump_to_previous_in_focus_order(self):
        '''Basic focus step back.'''
        if self.app.game_state._focus_idx > 0:
            self.app.game_state._focus_idx -= 1
            self.app.set_focus()

    def _should_protect_first_card(self, cards_in_hand):
        '''Check if first card should be protected.'''
        return self.app.game_state._deal_step == 1 and cards_in_hand == 1
