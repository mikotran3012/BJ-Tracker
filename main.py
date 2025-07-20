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
        self.geometry("1200x700")  # Keep original size
        self.configure(bg=COLORS['bg_main'])

        # STEP 1: Initialize core managers FIRST
        self.game_state = GameState(DEFAULT_DECKS)
        self.action_handler = ActionHandler(self)
        self.focus_manager = FocusManager(self.game_state)
        self.count_manager = CountManager(DEFAULT_DECKS)

        # STEP 2: Initialize UI-related attributes to prevent AttributeError
        self.dealer_border = None
        self.player_border = None
        self.panel_min_height = 180

        # STEP 3: Build the complete UI
        self._setup_ui()

        # STEP 4: Setup keyboard bindings
        self._setup_bindings()

        # STEP 5: Only AFTER everything is built, prompt for seat selection
        # Use longer delay to ensure UI is fully rendered
        self.after(500, self.prompt_seat_selection)

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

    def _setup_ui(self):
        """Setup UI with fully independent left/right columns and vertical divider - compact layout."""

        # TOP-LEVEL CONTAINER: Grid-based layout for left/divider/right
        main_top_row = tk.Frame(self, bg=COLORS['bg_main'])
        main_top_row.pack(side='top', fill='both', expand=True, padx=5, pady=5)

        # Configure grid columns: left (expandable), divider (fixed), right (fixed)
        main_top_row.grid_columnconfigure(0, weight=3)  # Left side - larger weight for more space
        main_top_row.grid_columnconfigure(1, weight=0)  # Divider - fixed width
        main_top_row.grid_columnconfigure(2, weight=1)  # Right side - smaller fixed width
        main_top_row.grid_rowconfigure(0, weight=1)  # Allow vertical expansion

        # === LEFT COLUMN: All game panels in vertical stack ===
        left_frame = tk.Frame(main_top_row, bg=COLORS['bg_main'], relief=tk.GROOVE, bd=1)
        left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 3))

        # 1. CARD COMPOSITION TRACKER (top of left column) - REMOVED HEADER
        comp_container = tk.Frame(left_frame, bg=COLORS['bg_main'])
        comp_container.pack(fill='x', pady=5, padx=5)

        # REMOVED: comp_label header for cleaner look
        # comp_label = tk.Label(comp_container, text="CARD COMPOSITION TRACKER",
        #                       font=('Segoe UI', 10, 'bold'), bg=COLORS['bg_main'], fg=COLORS['fg_white'])
        # comp_label.pack(pady=(0, 5))

        self.game_state.comp_panel = CompPanel(comp_container, self.on_decks_change, self.game_state.decks)
        self.game_state.comp_panel.pack(anchor='w')

        # 2. SEATS SECTION - LEFT ALIGNED
        seats_container = tk.Frame(left_frame, bg=COLORS['bg_main'])
        seats_container.pack(fill='x', pady=5, padx=(5, 5), anchor='w')  # Left aligned container

        tk.Label(seats_container, text="SEATS", font=('Segoe UI', 10, 'bold'),
                 bg=COLORS['bg_main'], fg=COLORS['fg_white']).pack(anchor='w', pady=(0, 3))

        seats_row = tk.Frame(seats_container, bg=COLORS['bg_main'], relief=tk.SUNKEN, bd=1)
        seats_row.pack(anchor='w', pady=2)  # Left aligned row, no fill='x'

        # Add padding inside seats row - minimal horizontal padding
        seats_inner = tk.Frame(seats_row, bg=COLORS['bg_main'])
        seats_inner.pack(pady=3, padx=2)  # Reduced horizontal padding

        for si, seat in enumerate(SEATS):
            self.game_state.seat_hands[seat] = SeatHandPanel(
                seats_inner, seat, False, False,
                on_action=self.handle_seat_action
            )
            self.game_state.seat_hands[seat].pack(side=tk.LEFT, padx=1)

        # 3. SHARED CARD INPUT PANEL - RESTORED AND COMPACT
        input_container = tk.Frame(left_frame, bg=COLORS['bg_main'])
        input_container.pack(fill='x', pady=(5, 2), padx=0)  # Full width, minimal padding

        # REMOVED: input_label header for more compact layout
        # input_label = tk.Label(input_container, text="SHARED CARD INPUT PANEL",
        #                        font=('Segoe UI', 10, 'bold'), bg=COLORS['bg_main'], fg=COLORS['fg_white'])
        # input_label.pack(anchor='w', pady=(0, 3))

        # FIXED: Create SharedInputPanel directly in the container with proper sizing
        self.game_state.shared_input_panel = SharedInputPanel(
            input_container,
            self.handle_shared_card,
            self.handle_shared_undo
        )
        self.game_state.shared_input_panel.set_action_callbacks(
            on_stand=self.handle_shared_stand,
            on_split=self.handle_shared_split
        )
        # Pack with left alignment and minimal padding for compact layout
        self.game_state.shared_input_panel.pack(anchor='w', padx=5, pady=2)

        # 4. GAME PANELS SECTION (Dealer + Player) - SYNCHRONIZED HEIGHTS - MORE SPACE
        game_panels_container = tk.Frame(left_frame, bg=COLORS['bg_main'])
        game_panels_container.pack(fill='x', pady=5, padx=5)

        # Set fixed minimum height for synchronized panels - INCREASED for more space
        PANEL_MIN_HEIGHT = 200  # Increased from 180 for more visual space

        # Dealer panel with border and label - KEEP HEADER
        dealer_container = tk.Frame(game_panels_container, bg=COLORS['bg_main'])
        dealer_container.pack(side=tk.LEFT, fill='both', expand=True, padx=(0, 3))

        dealer_label = tk.Label(dealer_container, text="DEALER PANEL",
                                font=('Segoe UI', 10, 'bold'), bg=COLORS['bg_main'], fg=COLORS['fg_white'])
        dealer_label.pack(pady=(0, 3))

        # Fixed height border frame for dealer with minimum height
        self.dealer_border = tk.Frame(dealer_container, relief=tk.SUNKEN, bd=1, height=PANEL_MIN_HEIGHT)
        self.dealer_border.pack(fill='x')
        self.dealer_border.pack_propagate(False)  # Prevent automatic height changes

        self.game_state.dealer_panel = DealerPanel(
            self.dealer_border,
            self.on_dealer_card,
            self.on_dealer_undo,
            hole_card_reveal=True,
            on_global_undo=self.handle_shared_undo,
            undo_manager=self.action_handler.undo_manager
        )
        self.game_state.dealer_panel.pack(fill='both', expand=True, padx=3, pady=3)

        # Player panel with border and label - KEEP HEADER
        player_container = tk.Frame(game_panels_container, bg=COLORS['bg_main'])
        player_container.pack(side=tk.LEFT, fill='both', expand=True, padx=(3, 0))

        player_label = tk.Label(player_container, text="PLAYER PANEL",
                                font=('Segoe UI', 10, 'bold'), bg=COLORS['bg_main'], fg=COLORS['fg_white'])
        player_label.pack(pady=(0, 3))

        # Fixed height border frame for player with minimum height
        self.player_border = tk.Frame(player_container, relief=tk.SUNKEN, bd=1, height=PANEL_MIN_HEIGHT)
        self.player_border.pack(fill='x')
        self.player_border.pack_propagate(False)  # Prevent automatic height changes

        self.game_state.player_panel = PlayerPanel(
            self.player_border,
            self.on_player_card,
            self.on_player_undo,
            on_action=self.handle_player_action,
            on_global_undo=self.handle_shared_undo,
            undo_manager=self.action_handler.undo_manager
        )
        self.game_state.player_panel.pack(fill='both', expand=True, padx=3, pady=3)

        # Store minimum height for later use
        self.panel_min_height = PANEL_MIN_HEIGHT

        # === VERTICAL DIVIDER ===
        divider_frame = tk.Frame(
            main_top_row,
            bg='#404040',  # Dark gray divider color
            width=3,  # Thin vertical line
            relief=tk.RAISED,
            bd=1
        )
        divider_frame.grid(row=0, column=1, sticky='ns', padx=1)
        divider_frame.grid_propagate(False)  # Maintain fixed width

        # === RIGHT COLUMN: Counting systems only - REMOVED HEADER ===
        right_frame = tk.Frame(main_top_row, bg=COLORS['bg_main'], relief=tk.GROOVE, bd=1)
        right_frame.grid(row=0, column=2, sticky='nsew', padx=(3, 0))

        # Container for the counting panel - MORE COMPACT
        count_container = tk.Frame(right_frame, bg=COLORS['bg_main'])
        count_container.pack(fill='both', expand=True, padx=3, pady=3)  # Reduced padding

        self.count_panel = CountPanel(count_container, self.count_manager)
        self.count_panel.pack(fill='both', expand=True)

        # === BOTTOM AREA: Future features (spans full width below grid) ===
        future_features_frame = tk.Frame(self, bg=COLORS['bg_main'], relief=tk.GROOVE, bd=1)
        future_features_frame.pack(side='bottom', fill='x', padx=5, pady=(5, 5))

        # Future features header and content
        future_header = tk.Label(future_features_frame, text="FUTURE FEATURES",
                                 font=('Segoe UI', 14, 'bold'), bg=COLORS['bg_main'], fg=COLORS['fg_white'])
        future_header.pack(pady=10)

        # Placeholder content area
        future_content = tk.Frame(future_features_frame, bg=COLORS['bg_main'], height=50)
        future_content.pack(fill='x', padx=10, pady=(0, 10))
        future_content.pack_propagate(False)

    def _synchronize_panel_heights(self):
        """Ensure dealer and player panels maintain synchronized heights."""
        if not hasattr(self, 'dealer_border') or not hasattr(self, 'player_border'):
            return

        try:
            # Update display layouts first to get accurate measurements
            self.game_state.dealer_panel.update_idletasks()
            self.game_state.player_panel.update_idletasks()

            # Get the current required heights for both panels
            dealer_required = self.game_state.dealer_panel.winfo_reqheight()
            player_required = self.game_state.player_panel.winfo_reqheight()

            # Set both to the maximum height needed, with minimum constraint
            max_height = max(self.panel_min_height, dealer_required, player_required)

            # Update both panel heights
            self.dealer_border.config(height=max_height)
            self.player_border.config(height=max_height)

            # Force immediate visual update
            self.dealer_border.update_idletasks()
            self.player_border.update_idletasks()

        except Exception as e:
            print(f"ERROR in _synchronize_panel_heights: {e}")

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
        """Reset game with panel height synchronization."""
        print("RESET_FLOW: Resetting game flow")
        self.game_state.reset_game()

        # Reset counting systems
        self.count_manager.reset()
        self.count_panel.reset_displays()

        # SYNCHRONIZE PANEL HEIGHTS AFTER RESET
        self.after_idle(self._synchronize_panel_heights)

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
        """SAFE: Set focus with proper phase management and null checks."""
        print(
            f"SIMPLE_FOCUS: Current focus_idx={self.game_state._focus_idx}, play_phase={self.game_state.is_play_phase()}")

        # SAFE: Reset all panels with null checks
        if self.game_state.seat_hands:
            for seat, panel in self.game_state.seat_hands.items():
                if panel:
                    panel.highlight(active=False)

        if self.game_state.player_panel:
            self.game_state.player_panel.set_enabled(False)

        if self.game_state.shared_input_panel:
            self.game_state.shared_input_panel.set_enabled(False)

        if self.game_state.dealer_panel:
            self.game_state.dealer_panel.set_enabled(False)

        print("SIMPLE_FOCUS: Reset all panels")

        if not self.game_state._auto_focus:
            # Manual mode - enable everything
            print("SIMPLE_FOCUS: Manual mode - enabling all panels")
            if self.game_state.shared_input_panel:
                self.game_state.shared_input_panel.set_enabled(True)
            if self.game_state.player_panel:
                self.game_state.player_panel.update_mode(self.game_state.is_play_phase())
                self.game_state.player_panel.set_enabled(True)
            if self.game_state.dealer_panel:
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
                    if self.game_state.player_panel:
                        self.game_state.player_panel.update_mode(True)  # Play mode
                        self.game_state.player_panel.set_enabled(True)
                else:
                    print(f"SIMPLE_FOCUS: Enabling SHARED INPUT for seat {seat}")
                    if self.game_state.shared_input_panel:
                        self.game_state.shared_input_panel.set_enabled(True)
                    if seat in self.game_state.seat_hands and self.game_state.seat_hands[seat]:
                        self.game_state.seat_hands[seat].highlight(active=True)
            else:
                print("SIMPLE_FOCUS: Enabling DEALER for play")
                if self.game_state.dealer_panel:
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
                        if self.game_state.player_panel and self.game_state.player_panel.hands:
                            cards_needed = self.game_state._deal_step + 1
                            current_cards = len(self.game_state.player_panel.hands[0])
                            print(f"SIMPLE_FOCUS: Player needs {cards_needed} cards, has {current_cards}")

                            if current_cards >= cards_needed:
                                print("SIMPLE_FOCUS: Player has enough cards, advancing flow")
                                self.advance_flow()
                                return

                        print("SIMPLE_FOCUS: Enabling PLAYER for dealing")
                        if self.game_state.player_panel:
                            self.game_state.player_panel.update_mode(False)  # Dealing mode
                            self.game_state.player_panel.set_enabled(True)
                    else:
                        # Other seat's turn to get a card
                        print(f"SIMPLE_FOCUS: Enabling SHARED INPUT for dealing to {seat}")
                        if self.game_state.shared_input_panel:
                            self.game_state.shared_input_panel.set_enabled(True)
                        if seat in self.game_state.seat_hands and self.game_state.seat_hands[seat]:
                            self.game_state.seat_hands[seat].highlight(active=True)

                elif self.game_state._focus_idx == n:
                    print("SIMPLE_FOCUS: Enabling DEALER for dealing")
                    if self.game_state.dealer_panel:
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
    def on_dealer_card(self, rank, suit, is_hole=False):
        """Handle dealer card with panel height synchronization."""
        try:
            print(f"ON_DEALER_CARD: {rank}{suit} (hole={is_hole})")
            if not is_hole:
                self.game_state.log_card(rank)
                # Update counting systems (only for non-hole cards)
                self.count_manager.add_card(rank)
                self._update_counting_display()
            if not self.game_state.is_play_phase():
                self.advance_flow()

            # SYNCHRONIZE PANEL HEIGHTS AFTER CARD INPUT
            self.after_idle(self._synchronize_panel_heights)

        except Exception as e:
            print(f"ERROR in on_dealer_card: {e}")

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
        """Handle player undo with panel height synchronization."""
        try:
            print(f"ON_PLAYER_UNDO: rank={rank}, is_hole={is_hole}")
            if rank:
                self.game_state.undo_card(rank)

            # SYNCHRONIZE PANEL HEIGHTS AFTER UNDO
            self.after_idle(self._synchronize_panel_heights)

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

    def on_player_card(self, rank, suit, is_hole=False):
        """Handle player card with panel height synchronization."""
        try:
            print(f"\nON_PLAYER_CARD: {rank}{suit} (hole={is_hole})")
            self.game_state.log_card(rank)
            # Update counting systems (only for non-hole cards)
            if not is_hole:
                self.count_manager.add_card(rank)
                self._update_counting_display()

            if self.game_state.is_play_phase():
                print("ON_PLAYER_CARD: In play phase")
                if self.game_state.player_panel:
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

            # SYNCHRONIZE PANEL HEIGHTS AFTER CARD INPUT
            self.after_idle(self._synchronize_panel_heights)

            print("ON_PLAYER_CARD: Completed\n")

        except Exception as e:
            print(f"ERROR in on_player_card: {e}")
            import traceback
            traceback.print_exc()

    def on_dealer_undo(self, rank=None, is_hole=False):
        """Handle dealer undo with panel height synchronization."""
        try:
            print(f"ON_DEALER_UNDO: rank={rank}, is_hole={is_hole}")
            if rank and not is_hole:
                self.game_state.undo_card(rank)

            # SYNCHRONIZE PANEL HEIGHTS AFTER UNDO
            self.after_idle(self._synchronize_panel_heights)

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
        """GLOBAL UNDO with panel height synchronization."""
        try:
            print("HANDLE_SHARED_UNDO: Global undo called")
            result = self.action_handler.handle_shared_undo()
            # Sync counting systems after undo
            self._sync_counting_systems()

            # SYNCHRONIZE PANEL HEIGHTS AFTER UNDO
            self.after_idle(self._synchronize_panel_heights)

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