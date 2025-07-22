import tkinter as tk
from constants import RANKS


class KeyboardHandler:
    """FIXED: Keyboard handler with working hotkeys."""

    def __init__(self, app):
        self.app = app

    def handle_key(self, event):
        """FIXED: Handle keyboard input with working hotkeys."""
        char = event.char.upper()
        key_string = event.char.lower()

        print(f"KEY_DEBUG: Got key '{event.char}' -> '{char}' -> '{key_string}'")

        # PRIORITY 1: Handle rank+suit hotkeys FIRST
        if self._handle_rank_suit_hotkey(key_string):
            print("KEY_DEBUG: Hotkey handled successfully")
            return

        # PRIORITY 2: Handle T key (convert to 10)
        if char == 'T':
            char = '10'

        # PRIORITY 3: Check if it's a valid rank
        if char in RANKS:
            print(f"KEY_DEBUG: Valid rank {char}, handling...")
            if self.app.game_state._auto_focus:
                self._handle_rank_input(char)

        # PRIORITY 4: Handle undo
        elif char == 'U':
            if self.app.game_state._auto_focus:
                self._handle_undo_input()

        # PRIORITY 5: Handle other actions
        elif char == 'S':  # Stand
            self._handle_stand()
        elif char == 'P':  # Split
            self._handle_split()
        elif char == ' ':  # Space = Skip
            self._handle_skip()

    def _handle_rank_suit_hotkey(self, key_string):
        """FIXED: Handle rank+suit hotkeys with proper input routing."""
        rank, suit = self._parse_hotkey(key_string)
        if not rank or not suit:
            return False

        print(f"HOTKEY_FOUND: {rank}{suit}")

        # FIXED: Route to the correct input method based on current focus
        if not self.app.game_state._auto_focus:
            # Manual mode - use shared input
            print("HOTKEY: Manual mode, using shared input")
            self.app.handle_shared_card(rank, suit)
            return True

        # Auto focus mode - route to current focus
        if self.app.game_state.is_play_phase():
            print("HOTKEY: Play phase")
            self._input_hotkey_play_phase(rank, suit)
        else:
            print("HOTKEY: Dealing phase")
            self._input_hotkey_dealing_phase(rank, suit)

        return True

    def _parse_hotkey(self, key_string):
        """FIXED: Parse hotkey string into rank and suit."""
        # Handle 2-character hotkeys (7h, as, kd, etc.)
        if len(key_string) == 2:
            rank_char = key_string[0]
            suit_char = key_string[1]

            # Suit mapping
            suit_map = {'h': '♥', 'd': '♦', 'c': '♣', 's': '♠'}
            if suit_char not in suit_map:
                return None, None

            suit = suit_map[suit_char]

            # Rank mapping
            rank_map = {
                'a': 'A', '2': '2', '3': '3', '4': '4', '5': '5',
                '6': '6', '7': '7', '8': '8', '9': '9', 't': '10',
                'j': 'J', 'q': 'Q', 'k': 'K'
            }

            if rank_char not in rank_map:
                return None, None

            rank = rank_map[rank_char]
            print(f"PARSE_2CHAR: '{key_string}' -> {rank}{suit}")
            return rank, suit

        # Handle 3-character hotkeys (10h, 10d, etc.)
        elif len(key_string) == 3 and key_string.startswith('10'):
            suit_char = key_string[2]
            suit_map = {'h': '♥', 'd': '♦', 'c': '♣', 's': '♠'}
            if suit_char in suit_map:
                suit = suit_map[suit_char]
                rank = '10'
                print(f"PARSE_3CHAR: '{key_string}' -> {rank}{suit}")
                return rank, suit

        return None, None

    def _input_hotkey_play_phase(self, rank, suit):
        """FIXED: Input hotkey during play phase."""
        order = list(reversed(self.app.game_state._active_seats))

        if self.app.game_state._focus_idx < len(order):
            seat = order[self.app.game_state._focus_idx]
            if seat == self.app.game_state.seat:
                # PLAYER - use direct input_card method
                print(f"HOTKEY_PLAY: Inputting {rank}{suit} to PLAYER")
                self.app.game_state.player_panel.input_card(rank, suit)
            else:
                # OTHER SEAT - use shared card handler
                print(f"HOTKEY_PLAY: Inputting {rank}{suit} to SEAT {seat}")
                self.app.handle_shared_card(rank, suit)
        else:
            # DEALER
            if self.app.game_state.dealer_panel.is_done:
                print("HOTKEY_PLAY: Dealer locked - input ignored")
                return
            print(f"HOTKEY_PLAY: Inputting {rank}{suit} to DEALER")
            self.app.game_state.dealer_panel.input_card(rank, suit)

    def _input_hotkey_dealing_phase(self, rank, suit):
        """FIXED: Input hotkey during dealing phase."""
        order = list(reversed(self.app.game_state._active_seats))

        if self.app.game_state._focus_idx < len(order):
            seat = order[self.app.game_state._focus_idx]
            if seat == self.app.game_state.seat:
                # PLAYER - use direct input_card method
                print(f"HOTKEY_DEAL: Inputting {rank}{suit} to PLAYER")
                self.app.game_state.player_panel.input_card(rank, suit)
            else:
                # OTHER SEAT - use shared card handler
                print(f"HOTKEY_DEAL: Inputting {rank}{suit} to SEAT {seat}")
                self.app.handle_shared_card(rank, suit)
        elif self.app.game_state._focus_idx == len(order):
            # DEALER
            if self.app.game_state.dealer_panel.is_done:
                print("HOTKEY_DEAL: Dealer locked - input ignored")
                return
            print(f"HOTKEY_DEAL: Inputting {rank}{suit} to DEALER")
            self.app.game_state.dealer_panel.input_card(rank, suit)

    def _handle_rank_input(self, char):
        """Handle single rank input (shows suit dialog)."""
        print(f"RANK_INPUT: Handling rank {char}")

        if self.app.game_state.is_play_phase():
            order = list(reversed(self.app.game_state._active_seats))
            if self.app.game_state._focus_idx < len(order):
                seat = order[self.app.game_state._focus_idx]
                if seat == self.app.game_state.seat:
                    self.app.game_state.player_panel.rank_clicked(char)
                else:
                    self.app.game_state.shared_input_panel.rank_clicked(char)
            elif self.app.game_state._focus_idx >= len(order):
                if not self.app.game_state.dealer_panel.is_done:
                    self.app.game_state.dealer_panel.rank_clicked(char)
                else:
                    print("RANK_INPUT: Dealer locked - input ignored")
        else:
            order = list(reversed(self.app.game_state._active_seats))
            if self.app.game_state._focus_idx < len(order):
                seat = order[self.app.game_state._focus_idx]
                if seat == self.app.game_state.seat:
                    self.app.game_state.player_panel.rank_clicked(char)
                else:
                    self.app.game_state.shared_input_panel.rank_clicked(char)
            elif self.app.game_state._focus_idx == len(order):
                if not self.app.game_state.dealer_panel.is_done:
                    self.app.game_state.dealer_panel.rank_clicked(char)
                else:
                    print("RANK_INPUT: Dealer locked - input ignored")

    def _handle_stand(self):
        """Handle stand action."""
        if not self.app.game_state.is_play_phase():
            return

        pp = self.app.game_state.player_panel
        sip = self.app.game_state.shared_input_panel

        player_enabled = pp and pp.stand_skip_btn['state'] == tk.NORMAL
        shared_enabled = sip and sip.stand_btn['state'] == tk.NORMAL

        if not (player_enabled or shared_enabled):
            return

        order = list(reversed(self.app.game_state._active_seats))
        if self.app.game_state._focus_idx < len(order):
            seat = order[self.app.game_state._focus_idx]
            if seat == self.app.game_state.seat and player_enabled:
                self.app.handle_player_action('stand')
            elif seat != self.app.game_state.seat and shared_enabled:
                self.app.handle_shared_stand()

    def _handle_split(self):
        """Handle split action."""
        if self.app.game_state.is_play_phase():
            order = list(reversed(self.app.game_state._active_seats))
            if self.app.game_state._focus_idx < len(order):
                seat = order[self.app.game_state._focus_idx]
                if seat == self.app.game_state.seat:
                    self.app.handle_player_action('split')
                else:
                    self.app.handle_shared_split()

    def _handle_skip(self):
        """Handle skip action."""
        if self.app.game_state.is_play_phase():
            self.app.advance_play_focus()