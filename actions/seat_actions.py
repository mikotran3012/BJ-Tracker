class SeatActionHandler:
    '''Handles actions for other seats.'''

    def __init__(self, app):
        self.app = app

    def handle_action(self, seat, action, hand_idx=0):
        '''Handle actions from seat panels.'''
        if action == 'hit':
            self._handle_seat_hit(seat)
        elif action == 'stand':
            self._handle_seat_stand(seat)
        elif action == 'split':
            self._handle_seat_split(seat)
        elif action == 'skip':
            self._handle_seat_skip(seat)

    def _handle_seat_hit(self, seat):
        '''Handle hit action for other seats.'''
        pass

    def _handle_seat_stand(self, seat):
        '''Handle stand action for other seats.'''
        pass