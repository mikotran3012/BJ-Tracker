class ActionValidator:
    '''Validates actions and provides utility functions.'''

    def __init__(self, app):
        self.app = app

    def validate_action(self, seat, action):
        '''Validate if an action is allowed for a seat.'''
        if seat not in self.app.seat_hands:
            return False

        seat_panel = self.app.seat_hands[seat]

        if seat_panel.is_done or seat_panel.is_busted or seat_panel.is_surrendered:
            return False

        # Your validation logic here
        pass

    def get_valid_actions(self, seat):
        '''Get list of valid actions for a seat.'''
        # Your valid actions logic
        pass

    def get_action_info(self):
        '''Get current action state information for debugging.'''
        # Your action info logic
        pass