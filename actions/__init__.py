from .card_input import CardInputHandler
from .undo_manager import UndoManager
from .split_handler import SplitHandler
from .keyboard_handler import KeyboardHandler  # ADD THIS
from .player_actions import PlayerActionHandler
from .seat_actions import SeatActionHandler
from .validation import ActionValidator


class ActionHandler:
    '''Main action handler - coordinates all sub-handlers.'''

    def __init__(self, app):
        self.app = app

        # Initialize sub-handlers
        self.card_input = CardInputHandler(app)
        self.undo_manager = UndoManager(app)
        self.split_handler = SplitHandler(app)
        self.keyboard = KeyboardHandler(app)  # ADD THIS
        self.player_actions = PlayerActionHandler(app)
        self.seat_actions = SeatActionHandler(app)
        self.validator = ActionValidator(app)

    # Delegate methods to appropriate handlers
    def handle_shared_card(self, rank, suit):
        return self.card_input.handle_shared_card(rank, suit)

    def handle_shared_undo(self):
        return self.undo_manager.handle_shared_undo()

    def handle_shared_stand(self):
        return self.split_handler.handle_shared_stand()

    def handle_shared_split(self):
        return self.split_handler.handle_shared_split()

    def handle_key(self, event):
        return self.keyboard.handle_key(event)  # ADD THIS

    def handle_player_action(self, action, hand_idx=0):
        return self.player_actions.handle_action(action, hand_idx)

    def handle_seat_action(self, seat, action, hand_idx=0):
        return self.seat_actions.handle_action(seat, action, hand_idx)

    def validate_action(self, seat, action):
        return self.validator.validate_action(seat, action)