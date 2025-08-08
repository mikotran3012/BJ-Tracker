import tkinter as tk
import sys
import os

from ev_calculator import EVCalculator
from ev_display_panel import EVDisplayPanel
from counting import CountManager
from ui.count_panel import CountPanel

# Ensure proper imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# SIMPLE IMPORTS - only what we need
from constants import SEATS, RANKS, COLORS, DEFAULT_DECKS, normalize_rank_display, normalize_rank_internal
from rules_engine import BlackjackRules, Card, Hand
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
        self.geometry("1200x700")
        self.configure(bg=COLORS['bg_main'])

        # Initialize core managers FIRST
        self.game_state = GameState(DEFAULT_DECKS)
        self.action_handler = ActionHandler(self)
        self.focus_manager = FocusManager(self.game_state)
        self.count_manager = CountManager(DEFAULT_DECKS)
        self.rules = BlackjackRules()
        self.ev_calculator = None

        # Initialize UI-related attributes
        self.dealer_border = None
        self.player_border = None
        self.panel_min_height = 180
        self._ui_setup_complete = False

        # Build the complete UI - SHOULD ONLY BE CALLED ONCE
        print("MAIN_INIT: Calling _setup_ui()...")
        self._setup_ui()
        print("MAIN_INIT: _setup_ui() complete")

        # Setup keyboard bindings
        self._setup_bindings()

        # Prompt for seat selection
        self.after(500, self.prompt_seat_selection)

    def _update_counting_display(self):
        """Update the counting panel display."""
        cards_left = self.game_state.comp_panel.cards_left()
        aces_left = self._calculate_aces_left()
        self.count_panel.update_panel(cards_left, aces_left, self.game_state.decks)

    def _calculate_aces_left(self):
        """Calculate how many aces are left in the shoe."""
        total_aces = self.game_state.decks * 4
        aces_dealt = self.game_state.comp_panel.comp.get('A', 0)
        return total_aces - aces_dealt

    def _check_dealer_auto_stand(self):
        """Automatically stand dealer when total reaches 17 or more."""
        dp = self.game_state.dealer_panel
        if not dp or dp.mystery_hole:
            return

        cards = dp.hands[0][:]
        if dp.hole_card:
            cards.insert(1, dp.hole_card)
        if not cards:
            return

        hand_cards = [Card(normalize_rank_internal(r), s) for r, s in cards]
        hand = Hand(hand_cards)
        should_hit = self.rules.dealer_should_hit(hand)

        if should_hit:
            # Dealer still allowed to hit
            if dp.is_done:
                dp.is_done = False
                dp.set_enabled(True)
                dp.update_display()
        else:
            # Dealer must stand on this total
            dp.is_done = True
            dp.update_display()
            dp.set_enabled(False)

    def _setup_ui(self):
        """Setup UI with single panel creation and debug tracking."""

        print("SETUP_UI: Starting UI setup...")

        # Check if UI already exists (prevent double creation)
        if hasattr(self, '_ui_setup_complete') and self._ui_setup_complete:
            print("SETUP_UI: UI already setup, skipping...")
            return

        # TOP-LEVEL CONTAINER: Grid-based layout for left/divider/right
        main_top_row = tk.Frame(self, bg=COLORS['bg_main'])
        main_top_row.pack(side='top', fill='both', expand=True, padx=5, pady=5)

        # Configure grid columns
        main_top_row.grid_columnconfigure(0, weight=4)
        main_top_row.grid_columnconfigure(1, weight=0)
        main_top_row.grid_columnconfigure(2, weight=0)
        main_top_row.grid_rowconfigure(0, weight=1)

        # === LEFT COLUMN ===
        left_frame = tk.Frame(main_top_row, bg=COLORS['bg_main'], relief=tk.GROOVE, bd=1)
        left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 3))

        # 1. TOP ROW: COMPOSITION + SHARED INPUT
        top_row_container = tk.Frame(left_frame, bg=COLORS['bg_main'])
        top_row_container.pack(fill='x', pady=5, padx=5)

        top_row_container.grid_columnconfigure(0, weight=0)
        top_row_container.grid_columnconfigure(1, weight=0)
        top_row_container.grid_columnconfigure(2, weight=1)
        top_row_container.grid_rowconfigure(0, weight=1)

        # Left side: Card composition tracker
        comp_container = tk.Frame(top_row_container, bg=COLORS['bg_main'])
        comp_container.grid(row=0, column=0, sticky='w', padx=(0, 0))

        print("SETUP_UI: Creating CompPanel...")
        self.game_state.comp_panel = CompPanel(comp_container, self.on_decks_change, self.game_state.decks)
        self.game_state.comp_panel.pack(anchor='w')

        # Right side: Shared input panel + NEW CONTROL BUTTONS
        input_container = tk.Frame(top_row_container, bg=COLORS['bg_main'])
        input_container.grid(row=0, column=1, sticky='', padx=(2, 0))

        print("SETUP_UI: Creating SharedInputPanel...")
        self.game_state.shared_input_panel = SharedInputPanel(
            input_container,
            self.handle_shared_card,
            self.handle_shared_undo
        )
        self.game_state.shared_input_panel.set_action_callbacks(
            on_stand=self.handle_shared_stand,
            on_split=self.handle_shared_split,
            on_reset_active_seat=self.handle_reset_active_seat  # NEW: Add reset callback
        )
        self.game_state.shared_input_panel.pack(expand=True, fill='both', padx=0, pady=0)

        # NEW: Control buttons container - positioned to the right of shared input
        buttons_container = tk.Frame(top_row_container, bg=COLORS['bg_main'])
        buttons_container.grid(row=0, column=2, sticky='w', padx=(8, 0))

        # Add a small visual separator
        separator = tk.Frame(buttons_container, bg='#555555', width=2, height=40)
        separator.pack(side=tk.LEFT, padx=(0, 6), pady=8, fill='y')

        # Button group frame
        button_group = tk.Frame(buttons_container, bg=COLORS['bg_main'])
        button_group.pack(side=tk.LEFT, pady=8)

        # NEW: "New" button - Smaller size
        self.new_btn = tk.Button(
            button_group,
            text="New",
            width=5,  # Reduced from 6
            height=1,  # Reduced from 2
            font=('Segoe UI', 8, 'bold'),  # Smaller font
            bg='#4CAF50',  # Green - neutral/positive action
            fg='white',
            activebackground='#45a049',
            command=self.handle_new_round
        )
        self.new_btn.pack(side=tk.LEFT, padx=1)

        # NEW: "Reset" button - Smaller size
        self.reset_btn = tk.Button(
            button_group,
            text="Reset",
            width=5,  # Reduced from 6
            height=1,  # Reduced from 2
            font=('Segoe UI', 8, 'bold'),  # Smaller font
            bg='#f44336',  # Red - alert/destructive action
            fg='white',
            activebackground='#da190b',
            command=self.handle_full_reset
        )
        self.reset_btn.pack(side=tk.LEFT, padx=1)

        # NEW: "Cal" button - Smaller size
        self.cal_btn = tk.Button(
            button_group,
            text="Cal",
            width=5,  # Reduced from 6
            height=1,  # Reduced from 2
            font=('Segoe UI', 8, 'bold'),  # Smaller font
            bg='#2196F3',  # Blue - neutral/tool action
            fg='white',
            activebackground='#1976d2',
            command=self.handle_cal_function
        )
        self.cal_btn.pack(side=tk.LEFT, padx=1)

        # 2. SEATS SECTION
        seats_container = tk.Frame(left_frame, bg=COLORS['bg_main'])
        seats_container.pack(fill='x', pady=(5, 2), padx=(5, 5), anchor='w')

        seats_row = tk.Frame(seats_container, bg=COLORS['bg_main'], relief=tk.SUNKEN, bd=1)
        seats_row.pack(anchor='w', pady=0)

        seats_inner = tk.Frame(seats_row, bg=COLORS['bg_main'])
        seats_inner.pack(pady=2, padx=2)

        print("SETUP_UI: Creating seat panels...")
        for si, seat in enumerate(SEATS):
            self.game_state.seat_hands[seat] = SeatHandPanel(
                seats_inner, seat, False, False,
                on_action=self.handle_seat_action
            )
            self.game_state.seat_hands[seat].pack(side=tk.LEFT, padx=1)

        # 3. GAME PANELS SECTION - CRITICAL: Only create panels ONCE
        game_panels_container = tk.Frame(left_frame, bg=COLORS['bg_main'])
        game_panels_container.pack(fill='both', expand=True, pady=(5, 5), padx=5)

        game_panels_container.grid_columnconfigure(0, weight=17)
        game_panels_container.grid_columnconfigure(1, weight=23)
        game_panels_container.grid_rowconfigure(0, weight=1)

        PANEL_MIN_HEIGHT = 200

        # === DEALER PANEL - CREATE ONLY ONCE ===
        print("SETUP_UI: Creating dealer container...")
        dealer_container = tk.Frame(game_panels_container, bg=COLORS['bg_main'])
        dealer_container.grid(row=0, column=0, sticky='nsew', padx=(0, 2))

        print("SETUP_UI: Creating dealer border...")
        self.dealer_border = tk.Frame(dealer_container, relief=tk.SUNKEN, bd=1, height=PANEL_MIN_HEIGHT)
        self.dealer_border.pack(fill='both', expand=True)
        self.dealer_border.pack_propagate(False)

        # CRITICAL: Check if dealer panel already exists
        if hasattr(self.game_state, 'dealer_panel') and self.game_state.dealer_panel is not None:
            print("SETUP_UI: WARNING - DealerPanel already exists! Destroying old one...")
            self.game_state.dealer_panel.destroy()
            self.game_state.dealer_panel = None

        print("SETUP_UI: Creating DealerPanel...")
        self.game_state.dealer_panel = DealerPanel(
            self.dealer_border,
            self.on_dealer_card,
            self.on_dealer_undo,
            hole_card_reveal=True,
            on_global_undo=self.handle_shared_undo,
            undo_manager=self.action_handler.undo_manager
        )
        self.game_state.dealer_panel.pack(fill='both', expand=True, padx=3, pady=3)
        print("SETUP_UI: DealerPanel created and packed")

        print("SETUP_UI: DealerPanel created and packed")

        # Connect comp_panel to dealer panel for probability calculations
        if hasattr(self.game_state.dealer_panel, 'comp_panel'):
            self.game_state.dealer_panel.comp_panel = self.game_state.comp_panel
            print("SETUP_UI: Connected comp_panel to dealer panel")

        # === PLAYER PANEL - CREATE ONLY ONCE ===
        print("SETUP_UI: Creating player container...")
        player_container = tk.Frame(game_panels_container, bg=COLORS['bg_main'])
        player_container.grid(row=0, column=1, sticky='nsew', padx=(2, 0))

        print("SETUP_UI: Creating player border...")
        self.player_border = tk.Frame(player_container, relief=tk.SUNKEN, bd=1, height=PANEL_MIN_HEIGHT)
        self.player_border.pack(fill='both', expand=True)
        self.player_border.pack_propagate(False)

        # CRITICAL: Check if player panel already exists
        if hasattr(self.game_state, 'player_panel') and self.game_state.player_panel is not None:
            print("SETUP_UI: WARNING - PlayerPanel already exists! Destroying old one...")
            self.game_state.player_panel.destroy()
            self.game_state.player_panel = None

        print("SETUP_UI: Creating PlayerPanel...")
        self.game_state.player_panel = PlayerPanel(
            self.player_border,
            self.on_player_card,
            self.on_player_undo,
            on_action=self.handle_player_action,
            on_global_undo=self.handle_shared_undo,
            undo_manager=self.action_handler.undo_manager
        )
        self.game_state.player_panel.pack(fill='both', expand=True, padx=3, pady=3)
        print("SETUP_UI: PlayerPanel created and packed")

        self.panel_min_height = PANEL_MIN_HEIGHT

        # === VERTICAL DIVIDER ===
        divider_frame = tk.Frame(
            main_top_row,
            bg='#404040',
            width=3,
            relief=tk.RAISED,
            bd=1
        )
        divider_frame.grid(row=0, column=1, sticky='ns', padx=1)
        divider_frame.grid_propagate(False)

        # === RIGHT COLUMN: Counting systems ===
        right_frame = tk.Frame(main_top_row, bg=COLORS['bg_main'], relief=tk.GROOVE, bd=1, width=180, height=400)
        right_frame.grid(row=0, column=2, sticky='n', padx=(3, 0))
        right_frame.grid_propagate(False)

        count_container = tk.Frame(right_frame, bg=COLORS['bg_main'])
        count_container.pack(fill='both', expand=True, padx=2, pady=2)

        print("SETUP_UI: Creating count panel...")
        self.count_panel = CountPanel(count_container, self.count_manager)
        self.count_panel.pack(fill='both', expand=True)

        ev_container = tk.Frame(right_frame, bg=COLORS['bg_main'])
        ev_container.pack(fill='both', expand=True, padx=2, pady=2)

        # Initialize EV calculator now that comp_panel exists
        if self.game_state.comp_panel:
            self.ev_calculator = EVCalculator(self.game_state.comp_panel)
            self.ev_display = EVDisplayPanel(ev_container, self.ev_calculator)
            self.ev_display.pack(fill='both', expand=True)

        # === BOTTOM AREA: Future features ===
        future_height = int(700 * 0.20)
        future_features_frame = tk.Frame(self, bg=COLORS['bg_main'], relief=tk.GROOVE, bd=1, height=future_height)
        future_features_frame.pack(side='bottom', fill='x', padx=5, pady=(5, 5))
        future_features_frame.pack_propagate(False)

        future_header = tk.Label(future_features_frame, text="FUTURE FEATURES",
                                 font=('Segoe UI', 16, 'bold'), bg=COLORS['bg_main'], fg=COLORS['fg_white'])
        future_header.pack(pady=8)

        future_content = tk.Frame(future_features_frame, bg=COLORS['bg_main'])
        future_content.pack(fill='both', expand=True, padx=15, pady=(0, 8))

        # Mark UI setup as complete to prevent double creation
        self._ui_setup_complete = True

        print("SETUP_UI: UI setup complete")
        print("SETUP_UI: Final panel verification:")
        print(f"  - SharedInputPanel: {self.game_state.shared_input_panel is not None}")
        print(f"  - DealerPanel: {self.game_state.dealer_panel is not None}")
        print(f"  - PlayerPanel: {self.game_state.player_panel is not None}")

    def _update_ev_display(self):
        """Update EV display with enhanced debugging."""
        print("UPDATE_EV: Called")

        # Check prerequisites
        if not hasattr(self, 'ev_calculator') or not self.ev_calculator:
            print("UPDATE_EV: No EV calculator available")
            return

        if not hasattr(self, 'ev_display') or not self.ev_display:
            print("UPDATE_EV: No EV display available")
            return

        # Check game state
        if not self.game_state.is_play_phase():
            print("UPDATE_EV: Not in play phase")
            # Clear display when not in play phase
            try:
                self.ev_display.clear_display()
            except:
                pass
            return

        # Check panels
        if not (self.game_state.player_panel and self.game_state.dealer_panel):
            print("UPDATE_EV: Missing player or dealer panel")
            return

        # Check player hand
        player_hands = self.game_state.player_panel.hands
        current_hand_idx = self.game_state.player_panel.current_hand

        if current_hand_idx >= len(player_hands) or not player_hands[current_hand_idx]:
            print("UPDATE_EV: No valid player hand")
            return

        player_hand = player_hands[current_hand_idx]

        # Check dealer upcard
        dealer_hands = self.game_state.dealer_panel.hands
        if not dealer_hands or not dealer_hands[0]:
            print("UPDATE_EV: No dealer upcard")
            return

        dealer_upcard = dealer_hands[0][0][0]  # rank of first card

        print(f"UPDATE_EV: Calculating EV for player {player_hand} vs dealer {dealer_upcard}")

        # Update EV display
        try:
            self.ev_display.update_analysis(player_hand, dealer_upcard)
            print("UPDATE_EV: Success!")
        except Exception as e:
            print(f"UPDATE_EV: Error: {e}")
            import traceback
            traceback.print_exc()

    # NEW BUTTON HANDLERS
    def handle_new_round(self):
        """NEW: Handle 'New' button - Clear all cards but keep composition and counts."""
        print("NEW_ROUND: Starting new round (clearing cards only)")

        try:
            # Clear all card displays but DON'T reset composition or counts

            # Reset dealer panel cards only
            if self.game_state.dealer_panel:
                self.game_state.dealer_panel.hands = [[]]
                self.game_state.dealer_panel.hole_card = None
                self.game_state.dealer_panel.mystery_hole = False
                self.game_state.dealer_panel.is_busted = False
                self.game_state.dealer_panel.is_done = False
                self.game_state.dealer_panel.current_deal_step = 0
                self.game_state.dealer_panel.upcard_rank = None
                self.game_state.dealer_panel.update_display()

            # Reset player panel cards only
            if self.game_state.player_panel:
                self.game_state.player_panel.hands = [[]]
                self.game_state.player_panel.current_hand = 0
                self.game_state.player_panel.is_busted = False
                self.game_state.player_panel.is_done = False
                self.game_state.player_panel.is_surrendered = False
                self.game_state.player_panel.split_history.clear()
                self.game_state.player_panel.pending_split = False
                self.game_state.player_panel.pending_index = 0
                self.game_state.player_panel.update_display()

            # Reset seat panels cards only
            for seat, panel in self.game_state.seat_hands.items():
                panel.hands = [[]]
                panel.current_hand = 0
                panel.is_busted = False
                panel.is_done = False
                panel.is_surrendered = False
                panel.split_history.clear()
                panel.pending_split = False
                panel.pending_index = 0
                panel.highlight(active=False)
                panel.update_display()

            # Reset game flow state but keep composition and counting
            self.game_state._deal_step = 0
            self.game_state._focus_idx = 0
            self.game_state._play_phase = False

            # IMPORTANT: DO NOT reset comp_panel or count_manager
            # The composition and counts should remain as they were

            # Set focus for new round
            self.set_focus()

            # SYNCHRONIZE PANEL HEIGHTS
            self.after_idle(self._synchronize_panel_heights)

            print("NEW_ROUND: New round started successfully")

            if hasattr(self, 'ev_display'):
                self.ev_display.clear_display()

        except Exception as e:
            print(f"ERROR in handle_new_round: {e}")
            import traceback
            traceback.print_exc()

    def handle_full_reset(self):
        """NEW: Handle 'Reset' button - Full reset including composition and counts."""
        print("FULL_RESET: Starting full reset (everything)")

        try:
            # Reset everything using existing reset methods
            self.reset_flow()

            print("FULL_RESET: Full reset completed successfully")

        except Exception as e:
            print(f"ERROR in handle_full_reset: {e}")
            import traceback
            traceback.print_exc()

    def handle_cal_function(self):
        """Enhanced Cal button - Test EV calculator and show results."""
        print("CAL: Calculator function called - Testing EV system")

        # TEST DEALER PROBABILITIES
        if self.game_state.dealer_panel:
            print("CAL: Testing dealer probability update...")
            if hasattr(self.game_state.dealer_panel, 'update_dealer_probabilities'):
                self.game_state.dealer_panel.update_dealer_probabilities()
                print("CAL: Dealer probabilities update called")

            # Force a test with dealer having a 10
            if hasattr(self.game_state.dealer_panel, 'prob_panel') and self.game_state.dealer_panel.prob_panel:
                print("CAL: Force testing with dealer 10...")
                self.game_state.dealer_panel.prob_panel.update_probabilities('T', self.game_state.comp_panel)

        try:
            # Test the EV calculator
            if self.test_ev_calculator():
                # If test passes, show a success message
                import tkinter.messagebox as msgbox
                msgbox.showinfo("EV Calculator Test",
                                "✓ EV Calculator is working correctly!\n\n" +
                                "The EV panel should show calculations when:\n" +
                                "• You're in play phase\n" +
                                "• Player has cards\n" +
                                "• Dealer has an upcard\n\n" +
                                "Try dealing some cards and entering play phase.")
            else:
                # If test fails, show error message
                import tkinter.messagebox as msgbox
                msgbox.showerror("EV Calculator Error",
                                 "✗ EV Calculator is not working properly.\n\n" +
                                 "Check the console for error details.\n" +
                                 "The EV calculator may not be properly initialized.")

        except Exception as e:
            print(f"ERROR in handle_cal_function: {e}")
            import traceback
            traceback.print_exc()

            import tkinter.messagebox as msgbox
            msgbox.showerror("Calculator Error", f"Error testing calculator: {e}")

    def test_ev_calculator(self):
        """Test method to verify EV calculator is working."""
        print("=" * 50)
        print("TESTING EV CALCULATOR")
        print("=" * 50)

        # Check if EV calculator exists
        if not hasattr(self, 'ev_calculator') or not self.ev_calculator:
            print("ERROR: EV calculator not initialized!")
            return False

        if not hasattr(self, 'ev_display') or not self.ev_display:
            print("ERROR: EV display not initialized!")
            return False

        print("✓ EV calculator and display found")

        # Test with sample data
        test_player_hand = [('10', 'H'), ('6', 'S')]  # Player has 16
        test_dealer_upcard = '10'  # Dealer shows 10

        print(f"Testing with player hand: {test_player_hand}")
        print(f"Testing with dealer upcard: {test_dealer_upcard}")

        try:
            # Test the EV calculation
            self.ev_display.update_analysis(test_player_hand, test_dealer_upcard)
            print("✓ EV calculation completed successfully!")
            return True
        except Exception as e:
            print(f"✗ EV calculation failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def manual_ev_update(self):
        """Manually trigger EV update for testing."""
        print("MANUAL_EV: Triggering manual EV update")

        # Force an EV update regardless of game state
        if not (self.game_state.player_panel and self.game_state.dealer_panel):
            print("MANUAL_EV: Missing panels")
            return

        player_hands = self.game_state.player_panel.hands
        if not player_hands or not player_hands[0]:
            print("MANUAL_EV: No player cards")
            return

        dealer_hands = self.game_state.dealer_panel.hands
        if not dealer_hands or not dealer_hands[0]:
            print("MANUAL_EV: No dealer cards")
            return

        player_hand = player_hands[0]
        dealer_upcard = dealer_hands[0][0][0]

        print(f"MANUAL_EV: Player: {player_hand}, Dealer: {dealer_upcard}")

        try:
            self.ev_display.update_analysis(player_hand, dealer_upcard)
            print("MANUAL_EV: Update successful")
        except Exception as e:
            print(f"MANUAL_EV: Error: {e}")
            import traceback
            traceback.print_exc()

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
        """Handle keyboard input with Undo hotkey support."""
        try:
            print(f"\n=== KEY EVENT ===")
            print(f"Key: '{event.char}' (char)")
            print(f"Current focus: {self.game_state._focus_idx}")
            print(f"Play phase: {self.game_state.is_play_phase()}")
            print(f"Auto focus: {self.game_state._auto_focus}")

            if event.char.upper() == 'E':  # Press 'E' to test EV
                print("EV TEST: Manual EV update triggered")
                self.manual_ev_update()
                return "break"

            # HOTKEY: Handle 'U' key for global undo
            if event.char.upper() == 'U':
                print("UNDO HOTKEY: 'U' key pressed - triggering global undo")
                self.handle_shared_undo()
                return "break"  # Prevent further processing

            # Use the existing keyboard handler for other keys
            result = self.action_handler.keyboard.handle_key(event)
            print(f"Keyboard handler result: {result}")
            print("=== END KEY EVENT ===\n")

            return result

        except Exception as e:
            print(f"ERROR in handle_key: {e}")
            import traceback
            traceback.print_exc()

    def prompt_seat_selection(self):
        """Show seat selection dialog with error handling."""
        print("\n" + "=" * 50)
        print("PROMPT_SEAT: Starting seat selection process")

        try:
            # Create dialog
            dialog = SeatSelectDialog(self)
            print("PROMPT_SEAT: Dialog created successfully")

            # Try to center it
            try:
                self.update_idletasks()
                main_x = self.winfo_x()
                main_y = self.winfo_y()
                main_width = self.winfo_width()
                main_height = self.winfo_height()

                # Use safer approach for dialog sizing
                dialog_width = 300  # Fixed width instead of trying winfo_reqwidth
                dialog_height = 200  # Fixed height instead of trying winfo_reqheight

                center_x = main_x + (main_width - dialog_width) // 2
                center_y = main_y + (main_height - dialog_height) // 2

                dialog.geometry(f"{dialog_width}x{dialog_height}+{center_x}+{center_y}")
                print(f"PROMPT_SEAT: Dialog positioned at {center_x},{center_y}")

            except Exception as e:
                print(f"PROMPT_SEAT: Error positioning dialog: {e}")
                # Continue anyway, dialog will appear at default position

            # Get the selected seat
            selected_seat = dialog.selected.get()
            print(f"PROMPT_SEAT: User selected seat: '{selected_seat}'")

        except Exception as e:
            print(f"PROMPT_SEAT: Error with dialog: {e}")
            # Fallback: just pick a default seat
            selected_seat = 'P1'
            print(f"PROMPT_SEAT: Using fallback seat: {selected_seat}")

        # Debug: Check state before setting seat
        print("BEFORE SEAT SELECTION:")
        print(f"  - Current seat: {getattr(self.game_state, 'seat', 'None')}")
        print(f"  - Active seats: {getattr(self.game_state, '_active_seats', 'None')}")

        # Set the seat
        print(f"PROMPT_SEAT: Setting seat to {selected_seat}")
        self.game_state.set_seat(selected_seat)

        # Make sure selected seat is in active seats
        if selected_seat not in self.game_state._active_seats:
            # Clear existing active seats and set only the player's seat
            self.game_state._active_seats = [selected_seat]
            print(f"PROMPT_SEAT: Set active seats to: {self.game_state._active_seats}")

        # Debug: Check state after setting seat
        print("AFTER SEAT SELECTION:")
        print(f"  - Current seat: {getattr(self.game_state, 'seat', 'None')}")
        print(f"  - Active seats: {getattr(self.game_state, '_active_seats', 'None')}")

        # Check if panels exist
        print("PANEL EXISTENCE CHECK:")
        print(f"  - Dealer panel exists: {self.game_state.dealer_panel is not None}")
        print(f"  - Player panel exists: {self.game_state.player_panel is not None}")
        print(f"  - Shared input panel exists: {self.game_state.shared_input_panel is not None}")

        # Reset and start the game
        print("PROMPT_SEAT: Calling reset_flow()")
        self.reset_flow()
        print("=" * 50)

    def on_decks_change(self):
        """Handle deck change."""
        print("DECKS_CHANGE: Deck count changed")
        new_decks = self.game_state.comp_panel.decks
        self.game_state.set_decks(new_decks)

        # Update counting systems
        self.count_manager.set_decks(new_decks)
        self._update_counting_display()

        # Update dealer probabilities if upcard exists
        if self.game_state.dealer_panel:
            self.game_state.dealer_panel.update_dealer_probabilities()

    def reset_flow(self):
        """Reset game with detailed debugging."""
        print("\n" + "-" * 30)
        print("RESET_FLOW: Starting reset")
        print("-" * 30)

        # Debug state before reset
        print("BEFORE RESET:")
        print(f"  - Seat: {getattr(self.game_state, 'seat', 'None')}")
        print(f"  - Active seats: {getattr(self.game_state, '_active_seats', 'None')}")

        # Reset core game state
        self.game_state.reset_game()

        # Reset counting systems
        self.count_manager.reset()
        self.count_panel.reset_displays()

        # Debug state after reset
        print("AFTER RESET:")
        print(f"  - Seat: {getattr(self.game_state, 'seat', 'None')}")
        print(f"  - Active seats: {getattr(self.game_state, '_active_seats', 'None')}")
        print(f"  - Focus idx: {getattr(self.game_state, '_focus_idx', 'None')}")
        print(f"  - Play phase: {getattr(self.game_state, '_play_phase', 'None')}")
        print(f"  - Deal step: {getattr(self.game_state, '_deal_step', 'None')}")

        # SYNCHRONIZE PANEL HEIGHTS AFTER RESET
        self.after_idle(self._synchronize_panel_heights)

        # Set initial focus
        print("RESET_FLOW: Calling set_focus()")
        self.set_focus()
        print("RESET_FLOW: Reset complete")
        print("-" * 30)

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

            if self.game_state.is_play_phase():
                order = list(reversed(self.game_state._active_seats))
                if self.game_state._focus_idx < len(order):
                    seat = order[self.game_state._focus_idx]
                    if seat == self.game_state.seat:
                        self._update_ev_display()

    def _simple_set_focus(self):
        """Debug version of set focus."""
        print(f"\n" + "+" * 40)
        print("SET_FOCUS: Starting focus management")
        print("+" * 40)

        # Debug current state
        print("CURRENT STATE:")
        print(f"  - Focus idx: {getattr(self.game_state, '_focus_idx', 'None')}")
        print(f"  - Play phase: {getattr(self.game_state, '_play_phase', 'None')}")
        print(f"  - Deal step: {getattr(self.game_state, '_deal_step', 'None')}")
        print(f"  - Active seats: {getattr(self.game_state, '_active_seats', 'None')}")
        print(f"  - Player seat: {getattr(self.game_state, 'seat', 'None')}")
        print(f"  - Auto focus: {getattr(self.game_state, '_auto_focus', 'None')}")

        # Check panel states
        print("PANEL STATES:")
        if self.game_state.dealer_panel:
            print(f"  - Dealer panel: EXISTS")
        else:
            print(f"  - Dealer panel: MISSING!")

        if self.game_state.player_panel:
            print(f"  - Player panel: EXISTS")
        else:
            print(f"  - Player panel: MISSING!")

        if self.game_state.shared_input_panel:
            print(f"  - Shared input panel: EXISTS")
        else:
            print(f"  - Shared input panel: MISSING!")

        # Reset all panels
        print("RESETTING ALL PANELS...")
        panels_reset = 0

        if self.game_state.seat_hands:
            for seat, panel in self.game_state.seat_hands.items():
                if panel and hasattr(panel, 'highlight'):
                    panel.highlight(active=False)
                    panels_reset += 1

        if self.game_state.player_panel and hasattr(self.game_state.player_panel, 'set_enabled'):
            self.game_state.player_panel.set_enabled(False)
            panels_reset += 1
            print(f"  - Player panel disabled")

        if self.game_state.shared_input_panel and hasattr(self.game_state.shared_input_panel, 'set_enabled'):
            self.game_state.shared_input_panel.set_enabled(False)
            panels_reset += 1
            print(f"  - Shared input panel disabled")

        if self.game_state.dealer_panel and hasattr(self.game_state.dealer_panel, 'set_enabled'):
            self.game_state.dealer_panel.set_enabled(False)
            panels_reset += 1
            print(f"  - Dealer panel disabled")

        print(f"RESET COMPLETE: {panels_reset} panels reset")

        # Check for problems
        if not self.game_state._active_seats:
            print("PROBLEM: No active seats!")
            print("SOLUTION: Enabling all panels as fallback")
            if self.game_state.shared_input_panel:
                self.game_state.shared_input_panel.set_enabled(True)
                print("  - Shared input enabled")
            if self.game_state.player_panel:
                self.game_state.player_panel.set_enabled(True)
                print("  - Player panel enabled")
            if self.game_state.dealer_panel:
                self.game_state.dealer_panel.set_enabled(True)
                print("  - Dealer panel enabled")
            print("+" * 40)
            return

        if not hasattr(self.game_state, '_auto_focus') or not self.game_state._auto_focus:
            print("MANUAL MODE: Enabling all panels")
            if self.game_state.shared_input_panel:
                self.game_state.shared_input_panel.set_enabled(True)
            if self.game_state.player_panel:
                if hasattr(self.game_state.player_panel, 'update_mode'):
                    self.game_state.player_panel.update_mode(self.game_state.is_play_phase())
                self.game_state.player_panel.set_enabled(True)
            if self.game_state.dealer_panel:
                if hasattr(self.game_state.dealer_panel, 'set_play_mode'):
                    self.game_state.dealer_panel.set_play_mode()
                self.game_state.dealer_panel.set_enabled(True)
            print("+" * 40)
            return

        # Auto focus mode
        if self.game_state.is_play_phase():
            print("AUTO FOCUS: Play phase")
            order = list(reversed(self.game_state._active_seats))
            print(f"  - Play order: {order}")

            if self.game_state._focus_idx < len(order):
                seat = order[self.game_state._focus_idx]
                print(f"  - Current focus: seat {seat}")

                if seat == self.game_state.seat:
                    print("  - This is player's seat - enabling PLAYER PANEL")
                    if self.game_state.player_panel:
                        if hasattr(self.game_state.player_panel, 'update_mode'):
                            self.game_state.player_panel.update_mode(True)
                        self.game_state.player_panel.set_enabled(True)
                        print("  - Player panel enabled")
                    else:
                        print("  - ERROR: Player panel is None!")
                else:
                    print(f"  - Other player's seat - enabling SHARED INPUT")
                    if self.game_state.shared_input_panel:
                        self.game_state.shared_input_panel.set_enabled(True)
                        print("  - Shared input enabled")
                    if seat in self.game_state.seat_hands and self.game_state.seat_hands[seat]:
                        if hasattr(self.game_state.seat_hands[seat], 'highlight'):
                            self.game_state.seat_hands[seat].highlight(active=True)
                            print(f"  - Seat {seat} highlighted")
            else:
                print("  - Focus beyond seats - enabling DEALER PANEL")
                if self.game_state.dealer_panel:
                    if hasattr(self.game_state.dealer_panel, 'set_play_mode'):
                        self.game_state.dealer_panel.set_play_mode()
                    self.game_state.dealer_panel.set_enabled(True)
                    print("  - Dealer panel enabled for play")
        else:
            print("AUTO FOCUS: Dealing phase")
            order = list(reversed(self.game_state._active_seats))
            n = len(order)
            print(f"  - Deal order: {order}")
            print(f"  - Focus idx: {self.game_state._focus_idx}, n: {n}")

            if self.game_state._deal_step < 2:
                if self.game_state._focus_idx < n:
                    seat = order[self.game_state._focus_idx]
                    print(f"  - Dealing to seat: {seat}")

                    if seat == self.game_state.seat:
                        print("  - Player's turn - enabling PLAYER PANEL")
                        if self.game_state.player_panel:
                            if hasattr(self.game_state.player_panel, 'update_mode'):
                                self.game_state.player_panel.update_mode(False)  # Dealing mode
                            self.game_state.player_panel.set_enabled(True)
                            print("  - Player panel enabled for dealing")
                        else:
                            print("  - ERROR: Player panel is None!")
                    else:
                        print(f"  - Other seat - enabling SHARED INPUT")
                        if self.game_state.shared_input_panel:
                            self.game_state.shared_input_panel.set_enabled(True)
                            print("  - Shared input enabled")
                        if seat in self.game_state.seat_hands and self.game_state.seat_hands[seat]:
                            if hasattr(self.game_state.seat_hands[seat], 'highlight'):
                                self.game_state.seat_hands[seat].highlight(active=True)
                                print(f"  - Seat {seat} highlighted")

                elif self.game_state._focus_idx == n:
                    print("  - Dealer's turn - enabling DEALER PANEL")
                    if self.game_state.dealer_panel:
                        if hasattr(self.game_state.dealer_panel, 'set_dealer_turn'):
                            self.game_state.dealer_panel.set_dealer_turn(self.game_state._deal_step)
                        self.game_state.dealer_panel.set_enabled(True)
                        print(f"  - Dealer panel enabled for deal step {self.game_state._deal_step}")
                    else:
                        print("  - ERROR: Dealer panel is None!")
            else:
                print("  - Dealing complete - switching to play phase")
                self.game_state._play_phase = True
                self.game_state._focus_idx = 0
                print("  - Recursively calling set_focus for play phase")
                self.set_focus()

        print("SET_FOCUS: Focus management complete")
        print("+" * 40)

    def advance_flow(self):
        """Advance dealing flow."""
        print("ADVANCE_FLOW: Called")
        self.game_state.advance_deal_step()
        self.set_focus()

    def advance_play_focus(self):
        """Advance play focus with proper auto-focus logic."""
        print("ADVANCE_PLAY_FOCUS: Called")

        # Check if we're in auto-focus mode
        if not self.game_state._auto_focus:
            print("ADVANCE_PLAY_FOCUS: Manual mode - not advancing")
            return

        # Get the play order (reversed active seats)
        order = list(reversed(self.game_state._active_seats))
        print(f"ADVANCE_PLAY_FOCUS: Play order: {order}")
        print(f"ADVANCE_PLAY_FOCUS: Current focus_idx: {self.game_state._focus_idx}")

        # Advance to next seat
        self.game_state._focus_idx += 1

        # Check if we've gone past all players (move to dealer)
        if self.game_state._focus_idx >= len(order):
            print("ADVANCE_PLAY_FOCUS: Moving to dealer")
            # Focus is now on dealer
        else:
            next_seat = order[self.game_state._focus_idx]
            print(f"ADVANCE_PLAY_FOCUS: Moving to seat: {next_seat}")

        # Update focus
        self.set_focus()

    # CARD INPUT HANDLERS
    def on_dealer_card(self, rank, suit, is_hole=False):
        """Handle dealer card with panel height synchronization."""
        try:
            print(f"ON_DEALER_CARD: {rank}{suit} (hole={is_hole})")

            # ADD DEBUG TO SEE WHY advance_flow() ISN'T CALLED
            print(f"DEBUG: is_play_phase()={self.game_state.is_play_phase()}")
            print(f"DEBUG: _play_phase value={getattr(self.game_state, '_play_phase', 'MISSING')}")

            if not is_hole:
                self.game_state.log_card(rank)
                # Update counting systems (only for non-hole cards)
                self.count_manager.add_card(rank)
                self._update_counting_display()

                # FIX: Wrap probability update in try-catch to prevent breaking auto-focus
                print("ON_DEALER_CARD: Updating dealer probabilities...")
                try:
                    if hasattr(self.game_state.dealer_panel, 'update_dealer_probabilities'):
                        self.game_state.dealer_panel.update_dealer_probabilities()
                        print("ON_DEALER_CARD: Dealer probabilities updated")
                except Exception as prob_error:
                    print(f"ON_DEALER_CARD: Probability update failed: {prob_error}")
                    # Don't let this break the auto-focus flow

            if not is_hole and not self.game_state.is_play_phase():
                self._update_ev_display()

                # THE CRITICAL PART - This should now execute
            if not self.game_state.is_play_phase():
                print("ON_DEALER_CARD: Calling advance_flow()")
                self.advance_flow()
            else:
                print("ON_DEALER_CARD: NOT calling advance_flow() - in play phase")

            # SYNCHRONIZE PANEL HEIGHTS AFTER CARD INPUT
            self.after_idle(self._synchronize_panel_heights)

            # Auto-stand dealer if total is 17 or more
            self._check_dealer_auto_stand()

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

    def handle_reset_active_seat(self):
        """Reset only the currently active seat that has auto-focus."""
        try:
            print("HANDLE_RESET_ACTIVE_SEAT: Called")

            if not self.game_state._auto_focus:
                print("HANDLE_RESET_ACTIVE_SEAT: Manual mode - no active seat to reset")
                return

            if not self.game_state.is_play_phase():
                print("HANDLE_RESET_ACTIVE_SEAT: Not in play phase - no active seat to reset")
                return

            # Get the currently focused seat
            order = list(reversed(self.game_state._active_seats))
            if self.game_state._focus_idx >= len(order):
                print("HANDLE_RESET_ACTIVE_SEAT: Focus is on dealer - no seat to reset")
                return

            current_seat = order[self.game_state._focus_idx]

            if current_seat == self.game_state.seat:
                print("HANDLE_RESET_ACTIVE_SEAT: Current focus is player - use player reset button instead")
                return

            if current_seat not in self.game_state.seat_hands:
                print(f"HANDLE_RESET_ACTIVE_SEAT: Seat {current_seat} not found in seat_hands")
                return

            # Reset the specific seat
            seat_panel = self.game_state.seat_hands[current_seat]
            print(f"HANDLE_RESET_ACTIVE_SEAT: Resetting seat {current_seat}")
            seat_panel.reset()

            # Refresh focus to ensure proper UI state
            self.set_focus()

            print(f"HANDLE_RESET_ACTIVE_SEAT: Successfully reset seat {current_seat}")

        except Exception as e:
            print(f"ERROR in handle_reset_active_seat: {e}")
            import traceback
            traceback.print_exc()

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

    def on_player_card(self, rank, suit, is_hole=False):
        """Handle player card with panel height synchronization."""
        try:
            print(f"\nON_PLAYER_CARD: {rank}{suit} (hole={is_hole})")
            self.game_state.log_card(rank)
            # Update counting systems (only for non-hole cards)
            if not is_hole:
                self.count_manager.add_card(rank)
                self._update_counting_display()

            self._update_ev_display()

            if self.game_state.is_play_phase():
                print("ON_PLAYER_CARD: In play phase")
                if self.game_state.player_panel:
                    current_score = self.game_state.player_panel.calculate_score()
                    print(f"ON_PLAYER_CARD: Current score: {current_score}")
                    if current_score >= 21:
                        print("ON_PLAYER_CARD: Hand finished, handling completion")
                        self._handle_player_completion()
                    else:
                        print("ON_PLAYER_CARD: Hand continues, advancing to next player")
                        self.advance_play_focus()
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

                # Update dealer probabilities after undo
                if hasattr(self.game_state.dealer_panel, 'update_dealer_probabilities'):
                    self.game_state.dealer_panel.update_dealer_probabilities()

            # SYNCHRONIZE PANEL HEIGHTS AFTER UNDO
            self.after_idle(self._synchronize_panel_heights)

            # Re-evaluate dealer standing state after undo
            self._check_dealer_auto_stand()

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

            panel = result.get("panel") if result else None

            # If the undone panel was previously marked done, reactivate it
            if panel and result.get("was_done"):
                panel.is_done = False
                if hasattr(panel, "update_display"):
                    panel.update_display()
                self.set_focus()

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