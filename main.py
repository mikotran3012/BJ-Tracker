import tkinter as tk
import sys
import os

from counting import CountManager
from ui.count_panel import CountPanel
# Ensure proper imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# SIMPLE IMPORTS - only what we need
from constants import SEATS, RANKS, COLORS, DEFAULT_DECKS, normalize_rank_display, normalize_rank_internal

# Core modules
from core.game_state import GameState
from actions import ActionHandler
from focus_manager import FocusManager

# UI Panels - use the SIMPLE versions
from ui.panels import CompPanel, SeatHandPanel
from ui.input_panels import SharedInputPanel, PlayerPanel, DealerPanel

# Dialogs
from ui.dialogs import SeatSelectDialog


class BlackjackTrackerApp(tk.Tk):
    """Main application with cleaned up UI - no debug dialogs."""

    def __init__(self):
        super().__init__()
        self.title("Blackjack Card Tracker Pro")
        self.geometry("1200x700")  # Reduced height since removing debug area
        self.configure(bg=COLORS['bg_main'])

        # Initialize core managers
        self.game_state = GameState(DEFAULT_DECKS)
        self.action_handler = ActionHandler(self)
        self.focus_manager = FocusManager(self.game_state)
        # ADD THIS: Initialize counting system
        self.count_manager = CountManager(DEFAULT_DECKS)

        self._setup_ui()
        self._setup_bindings()

        # Prompt for seat selection
        self.after(200, self.prompt_seat_selection)

    def _calculate_aces_left(self):
        """Calculate aces remaining based on composition panel."""
        total_aces = self.game_state.decks * 4
        aces_dealt = self.game_state.comp_panel.comp.get('A', 0)
        return total_aces - aces_dealt

    def _update_counting_display(self):
        """Update the counting panel display."""
        cards_left = self.game_state.comp_panel.cards_left()
        aces_left = self._calculate_aces_left()
        self.count_panel.update_panel(cards_left, aces_left, self.game_state.decks)

    # In your main.py _setup_ui method, replace the top section with this:

    # Alternative approach for even tighter left alignment:

    def _setup_ui(self):
        """Setup UI with enlarged composition panel and tight vertical spacing."""
        # Main container - TIGHT spacing
        main_container = tk.Frame(self, bg=COLORS['bg_main'])
        main_container.pack(fill='both', expand=True, padx=(2, 8), pady=6)  # Reduced top/bottom padding

        # TOP SECTION: Enlarged composition + counting panel
        top_section = tk.Frame(main_container, bg=COLORS['bg_main'])
        top_section.pack(fill='x', pady=(0, 6))  # Reduced bottom padding

        # LEFT: ENLARGED Composition panel
        self.game_state.comp_panel = CompPanel(top_section, self.on_decks_change, self.game_state.decks)
        self.game_state.comp_panel.pack(side=tk.LEFT, anchor='nw', padx=0, pady=0)

        # RIGHT: Counting panel
        self.count_panel = CountPanel(top_section, self.count_manager)
        self.count_panel.pack(side=tk.RIGHT, anchor='ne')

        # SEATS SECTION: Reduced spacing
        seats_container = tk.Frame(main_container, bg=COLORS['bg_main'])
        seats_container.pack(fill='x', pady=(0, 6))  # Tight spacing

        tk.Label(seats_container, text="SEATS", font=('Segoe UI', 9, 'bold'),
                 bg=COLORS['bg_main'], fg=COLORS['fg_white']).pack(anchor='w')

        seats_row = tk.Frame(seats_container, bg=COLORS['bg_main'])
        seats_row.pack(anchor='w')

        for si, seat in enumerate(SEATS):
            self.game_state.seat_hands[seat] = SeatHandPanel(
                seats_row, seat, False, False,
                on_action=self.handle_seat_action
            )
            self.game_state.seat_hands[seat].pack(side=tk.LEFT, padx=1)

        # SHARED INPUT SECTION: Reduced spacing
        input_container = tk.Frame(main_container, bg=COLORS['bg_main'])
        input_container.pack(fill='x', pady=(0, 6))  # Tight spacing

        self.game_state.shared_input_panel = SharedInputPanel(
            input_container,
            self.handle_shared_card,
            self.handle_shared_undo
        )
        self.game_state.shared_input_panel.set_action_callbacks(
            on_stand=self.handle_shared_stand,
            on_split=self.handle_shared_split
        )
        self.game_state.shared_input_panel.pack(anchor='w')

        # GAME PANELS SECTION: PULLED UP - reduced spacing and height
        game_panels_container = tk.Frame(main_container, bg=COLORS['bg_main'], height=280)  # Reduced height
        game_panels_container.pack(fill='x', pady=(0, 4))  # Much tighter spacing
        game_panels_container.pack_propagate(False)

        # Dealer panel (left side)
        dealer_container = tk.Frame(game_panels_container, bg=COLORS['bg_main'], width=400)
        dealer_container.pack(side=tk.LEFT, fill='y', anchor='nw', padx=(0, 10))
        dealer_container.pack_propagate(False)

        self.game_state.dealer_panel = DealerPanel(
            dealer_container,
            self.on_dealer_card,
            self.on_dealer_undo,
            hole_card_reveal=True,
            on_global_undo=self.handle_shared_undo,
            undo_manager=self.action_handler.undo_manager
        )
        self.game_state.dealer_panel.pack(fill='both', expand=True)

        # Player panel (right side)
        player_container = tk.Frame(game_panels_container, bg=COLORS['bg_main'], width=400)
        player_container.pack(side=tk.LEFT, fill='y', anchor='nw')
        player_container.pack_propagate(False)

        self.game_state.player_panel = PlayerPanel(
            player_container,
            self.on_player_card,
            self.on_player_undo,
            on_action=self.handle_player_action,
            on_global_undo=self.handle_shared_undo,
            undo_manager=self.action_handler.undo_manager
        )
        self.game_state.player_panel.pack(fill='both', expand=True)

        # REMOVED: Debug status bar and dialog area
        # This area is now reserved for future features

    def _setup_bindings(self):
        """Setup keyboard bindings."""
        self.bind_all('<Key>', self.handle_key)

    def handle_key(self, event):
        """Handle keyboard input."""
        try:
            print(f"\n=== KEY EVENT ===")
            print(f"Key: '{event.char}' (char)")
            print(f"Current focus: {self.game_state._focus_idx}")
            print(f"Play phase: {self.game_state.is_play_phase()}")
            print(f"Auto focus: {self.game_state._auto_focus}")

            # Use the keyboard handler
            result = self.action_handler.keyboard.handle_key(event)
            print(f"Keyboard handler result: {result}")
            print("=== END KEY EVENT ===\n")

            return result

        except Exception as e:
            print(f"ERROR in handle_key: {e}")
            import traceback
            traceback.print_exc()

    def prompt_seat_selection(self):
        """Show seat selection."""
        print("PROMPT_SEAT: Showing seat selection dialog")
        dialog = SeatSelectDialog(self)
        selected_seat = dialog.selected.get()
        print(f"PROMPT_SEAT: Selected seat: {selected_seat}")
        self.game_state.set_seat(selected_seat)
        self.reset_flow()

    def on_decks_change(self):
        """Handle deck change."""
        print("DECKS_CHANGE: Deck count changed")
        new_decks = self.game_state.comp_panel.decks
        self.game_state.set_decks(new_decks)

        # ADD THIS: Update counting systems
        self.count_manager.set_decks(new_decks)
        self._update_counting_display()

    def reset_flow(self):
        """Reset game."""
        print("RESET_FLOW: Resetting game flow")
        self.game_state.reset_game()

        # ADD THIS: Reset counting systems
        self.count_manager.reset()
        self.count_panel.reset_displays()

        self.set_focus()

    def set_focus(self):
        """Set focus with proper phase management."""
        try:
            print(f"\nSET_FOCUS: Called")
            print(f"  Current focus_idx: {self.game_state._focus_idx}")
            print(f"  Play phase: {self.game_state.is_play_phase()}")
            print(f"  Auto focus: {self.game_state._auto_focus}")
            print(f"  Deal step: {self.game_state._deal_step}")

            if hasattr(self, 'focus_manager'):
                print("  Using focus_manager")
                self.focus_manager.set_focus()
            else:
                print("  Using simple focus")
                self._simple_set_focus()

            print("SET_FOCUS: Completed\n")

        except Exception as e:
            print(f"ERROR in set_focus: {e}")
            import traceback
            traceback.print_exc()

    def _simple_set_focus(self):
        """ENHANCED: Set focus with proper phase management for panels."""
        print(f"SIMPLE_FOCUS: Current focus_idx={self.game_state._focus_idx}, play_phase={self.game_state.is_play_phase()}")

        # Reset all panels
        for seat, panel in self.game_state.seat_hands.items():
            panel.highlight(active=False)

        if self.game_state.player_panel:
            self.game_state.player_panel.set_enabled(False)

        self.game_state.shared_input_panel.set_enabled(False)
        self.game_state.dealer_panel.set_enabled(False)
        print("SIMPLE_FOCUS: Reset all panels")

        if not self.game_state._auto_focus:
            # Manual mode - enable everything
            print("SIMPLE_FOCUS: Manual mode - enabling all panels")
            self.game_state.shared_input_panel.set_enabled(True)
            self.game_state.player_panel.update_mode(self.game_state.is_play_phase())
            self.game_state.player_panel.set_enabled(True)
            self.game_state.dealer_panel.set_play_mode()
            self.game_state.dealer_panel.set_enabled(True)
            return

        if self.game_state.is_play_phase():
            print("SIMPLE_FOCUS: Play phase")
            order = list(reversed(self.game_state._active_seats))
            if self.game_state._focus_idx < len(order):
                seat = order[self.game_state._focus_idx]
                if seat == self.game_state.seat:
                    print(f"SIMPLE_FOCUS: Enabling PLAYER (seat {seat})")
                    self.game_state.player_panel.update_mode(True)  # Play mode
                    self.game_state.player_panel.set_enabled(True)
                else:
                    print(f"SIMPLE_FOCUS: Enabling SHARED INPUT for seat {seat}")
                    self.game_state.shared_input_panel.set_enabled(True)
                    self.game_state.seat_hands[seat].highlight(active=True)
            else:
                print("SIMPLE_FOCUS: Enabling DEALER for play")
                self.game_state.dealer_panel.set_play_mode()
                self.game_state.dealer_panel.set_enabled(True)
        else:
            print("SIMPLE_FOCUS: Dealing phase")
            order = list(reversed(self.game_state._active_seats))
            n = len(order)

            if self.game_state._deal_step < 2:
                if self.game_state._focus_idx < n:
                    seat = order[self.game_state._focus_idx]
                    print(f"SIMPLE_FOCUS: Current seat in dealing: {seat}")

                    if seat == self.game_state.seat:
                        # Player's turn to get a card
                        cards_needed = self.game_state._deal_step + 1
                        current_cards = len(self.game_state.player_panel.hands[0])
                        print(f"SIMPLE_FOCUS: Player needs {cards_needed} cards, has {current_cards}")

                        if current_cards >= cards_needed:
                            print("SIMPLE_FOCUS: Player has enough cards, advancing flow")
                            self.advance_flow()
                            return

                        print("SIMPLE_FOCUS: Enabling PLAYER for dealing")
                        self.game_state.player_panel.update_mode(False)  # Dealing mode
                        self.game_state.player_panel.set_enabled(True)
                    else:
                        # Other seat's turn to get a card
                        print(f"SIMPLE_FOCUS: Enabling SHARED INPUT for dealing to {seat}")
                        self.game_state.shared_input_panel.set_enabled(True)
                        self.game_state.seat_hands[seat].highlight(active=True)

                elif self.game_state._focus_idx == n:
                    print("SIMPLE_FOCUS: Enabling DEALER for dealing")
                    self.game_state.dealer_panel.set_dealer_turn(self.game_state._deal_step)
                    self.game_state.dealer_panel.set_enabled(True)
            else:
                print("SIMPLE_FOCUS: Dealing complete, switching to play phase")
                self.game_state._play_phase = True
                self.game_state._focus_idx = 0
                self.set_focus()

        print("SIMPLE_FOCUS: Completed")

    def advance_flow(self):
        """Advance dealing flow."""
        print("ADVANCE_FLOW: Called")
        self.game_state.advance_deal_step()
        self.set_focus()

    def advance_play_focus(self):
        """Advance play focus."""
        print("ADVANCE_PLAY_FOCUS: Called")
        self.game_state.advance_play_focus()
        self.set_focus()

    # CARD INPUT HANDLERS
    def on_player_card(self, rank, suit, is_hole=False):
        """Handle player card."""
        try:
            print(f"\nON_PLAYER_CARD: {rank}{suit} (hole={is_hole})")
            self.game_state.log_card(rank)
            # ADD THIS: Update counting systems (only for non-hole cards)
            if not is_hole:
                self.count_manager.add_card(rank)
                self._update_counting_display()

            if self.game_state.is_play_phase():
                print("ON_PLAYER_CARD: In play phase")
                current_score = self.game_state.player_panel.calculate_score()
                print(f"ON_PLAYER_CARD: Current score: {current_score}")
                if current_score >= 21:
                    print("ON_PLAYER_CARD: Hand finished, handling completion")
                    self._handle_player_completion()
                else:
                    print("ON_PLAYER_CARD: Hand continues, setting focus")
                    self.set_focus()
            else:
                print("ON_PLAYER_CARD: In dealing phase, advancing flow")
                self.advance_flow()

            print("ON_PLAYER_CARD: Completed\n")

        except Exception as e:
            print(f"ERROR in on_player_card: {e}")
            import traceback
            traceback.print_exc()

    def _handle_player_completion(self):
        """Handle player hand completion."""
        print("HANDLE_PLAYER_COMPLETION: Called")
        player_panel = self.game_state.player_panel

        if player_panel.current_hand < len(player_panel.hands) - 1:
            print("HANDLE_PLAYER_COMPLETION: More split hands, advancing to next")
            player_panel.current_hand += 1
            player_panel.update_display()
            self.set_focus()
        else:
            print("HANDLE_PLAYER_COMPLETION: All hands done, advancing play focus")
            player_panel.is_done = True
            player_panel.update_display()
            self.advance_play_focus()

    def on_player_undo(self, rank=None, is_hole=False):
        """Handle player undo."""
        try:
            print(f"ON_PLAYER_UNDO: rank={rank}, is_hole={is_hole}")
            if rank:
                self.game_state.undo_card(rank)
        except Exception as e:
            print(f"ERROR in on_player_undo: {e}")

    def on_dealer_card(self, rank, suit, is_hole=False):
        """Handle dealer card."""
        try:
            print(f"ON_DEALER_CARD: {rank}{suit} (hole={is_hole})")
            if not is_hole:
                self.game_state.log_card(rank)
                # ADD THIS: Update counting systems (only for non-hole cards)
                self.count_manager.add_card(rank)
                self._update_counting_display()
            if not self.game_state.is_play_phase():
                self.advance_flow()
        except Exception as e:
            print(f"ERROR in on_dealer_card: {e}")

    def on_dealer_undo(self, rank=None, is_hole=False):
        """Handle dealer undo."""
        try:
            print(f"ON_DEALER_UNDO: rank={rank}, is_hole={is_hole}")
            if rank and not is_hole:
                self.game_state.undo_card(rank)
        except Exception as e:
            print(f"ERROR in on_dealer_undo: {e}")

    # ACTION HANDLERS
    def handle_shared_card(self, rank, suit):
        """Handle shared card input."""
        try:
            print(f"HANDLE_SHARED_CARD: {rank}{suit}")
            result = self.action_handler.handle_shared_card(rank, suit)
            # ADD THIS: Update counting systems
            self.count_manager.add_card(rank)
            self._update_counting_display()
            return result
        except Exception as e:
            print(f"ERROR in handle_shared_card: {e}")
            import traceback
            traceback.print_exc()

    def handle_shared_undo(self):
        """GLOBAL UNDO - Handle shared undo across all panels."""
        try:
            print("HANDLE_SHARED_UNDO: Global undo called")
            result = self.action_handler.handle_shared_undo()
            # ADD THIS: Sync counting systems after undo
            self._sync_counting_systems()

            return result
        except Exception as e:
            print(f"ERROR in handle_shared_undo: {e}")

    def handle_shared_stand(self):
        """Handle shared stand."""
        try:
            print("HANDLE_SHARED_STAND: Called")
            return self.action_handler.handle_shared_stand()
        except Exception as e:
            print(f"ERROR in handle_shared_stand: {e}")

    def handle_shared_split(self):
        """Handle shared split."""
        try:
            print("HANDLE_SHARED_SPLIT: Called")
            return self.action_handler.handle_shared_split()
        except Exception as e:
            print(f"ERROR in handle_shared_split: {e}")

    def handle_seat_action(self, seat, action, hand_idx=0):
        """Handle seat action."""
        try:
            print(f"HANDLE_SEAT_ACTION: {seat} -> {action}")
            return self.action_handler.handle_seat_action(seat, action, hand_idx)
        except Exception as e:
            print(f"ERROR in handle_seat_action: {e}")

    def handle_player_action(self, action, hand_idx=0):
        """Handle player action."""
        try:
            print(f"HANDLE_PLAYER_ACTION: {action}")

            if action == 'stand':
                print("HANDLE_PLAYER_ACTION: Stand - handling stand")
                self._handle_player_stand()
            elif action == 'split':
                print("HANDLE_PLAYER_ACTION: Split - attempting split")
                if self.game_state.player_panel.split_hand():
                    # Record split for undo before focus moves
                    self.action_handler.undo_manager.record_split(
                        "player", self.game_state.player_panel
                    )
                    self.set_focus()
            elif action == 'skip':
                print("HANDLE_PLAYER_ACTION: Skip - advancing focus")
                self.advance_play_focus()


        except Exception as e:
            print(f"ERROR in handle_player_action: {e}")

    def _handle_player_stand(self):
        """Handle player stand."""
        print("HANDLE_PLAYER_STAND: Called")
        player_panel = self.game_state.player_panel

        if player_panel.current_hand < len(player_panel.hands) - 1:
            print("HANDLE_PLAYER_STAND: More split hands")
            player_panel.current_hand += 1
            player_panel.update_display()
            self.set_focus()
        else:
            print("HANDLE_PLAYER_STAND: All hands done")
            player_panel.is_done = True
            player_panel.update_display()
            self.advance_play_focus()

    def _sync_counting_systems(self):
        """Sync counting systems with current composition panel state."""
        # Reset counts
        self.count_manager.reset()

        # Re-add all cards from composition panel
        for rank in ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']:
            count = self.game_state.comp_panel.comp.get(rank, 0)
            display_rank = '10' if rank == 'T' else rank
            for _ in range(count):
                self.count_manager.add_card(display_rank)

        # Update display
        self._update_counting_display()

    # BACKWARD COMPATIBILITY PROPERTIES
    @property
    def seat(self):
        return self.game_state.seat

    @property
    def seat_index(self):
        return self.game_state.seat_index

    @property
    def decks(self):
        return self.game_state.decks

    @property
    def comp_panel(self):
        return self.game_state.comp_panel

    @property
    def seat_hands(self):
        return self.game_state.seat_hands

    @property
    def player_panel(self):
        return self.game_state.player_panel

    @property
    def dealer_panel(self):
        return self.game_state.dealer_panel

    @property
    def shared_input_panel(self):
        return self.game_state.shared_input_panel

    @property
    def _play_phase(self):
        return self.game_state._play_phase

    @property
    def _focus_idx(self):
        return self.game_state._focus_idx

    @property
    def _active_seats(self):
        return self.game_state._active_seats

    @property
    def _auto_focus(self):
        return self.game_state._auto_focus


def main():
    """Main entry point."""
    try:
        print("MAIN: Starting application")
        app = BlackjackTrackerApp()
        app.mainloop()

    except ImportError as e:
        print(f"Import Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()