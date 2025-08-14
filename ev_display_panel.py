# ev_display_panel.py - Enhanced with better error handling and updates
import tkinter as tk
from tkinter import ttk


class EVDisplayPanel(tk.Frame):
    """ENHANCED: Panel to display EV calculations with better update handling"""

    def __init__(self, parent, ev_calculator):
        super().__init__(parent)
        self.ev_calculator = ev_calculator
        self.last_update_hash = None
        self.is_updating = False
        self.setup_ui()

    def setup_ui(self):
        # Title
        title = ttk.Label(self, text="Expected Value Analysis",
                          font=('Arial', 12, 'bold'))
        title.grid(row=0, column=0, columnspan=3, pady=8)

        # Current hand info
        self.hand_label = ttk.Label(self, text="Hand: --", font=('Arial', 10))
        self.hand_label.grid(row=1, column=0, columnspan=3, pady=3)

        # **NEW: Status indicator**
        self.status_label = ttk.Label(self, text="Ready", font=('Arial', 8), foreground='gray')
        self.status_label.grid(row=2, column=0, columnspan=3, pady=2)

        # Action EVs frame
        ev_frame = ttk.LabelFrame(self, text="Action EVs", padding=8)
        ev_frame.grid(row=3, column=0, columnspan=3, pady=8, padx=8, sticky='ew')

        # EV displays
        self.ev_labels = {}
        actions = ['stand', 'hit', 'double', 'split', 'surrender']

        for i, action in enumerate(actions):
            row = i // 2
            col = i % 2

            frame = ttk.Frame(ev_frame)
            frame.grid(row=row, column=col, padx=4, pady=3, sticky='w')

            ttk.Label(frame, text=f"{action.capitalize()}:",
                      width=9).grid(row=0, column=0)

            self.ev_labels[action] = ttk.Label(frame, text="--",
                                               font=('Courier', 9, 'bold'))
            self.ev_labels[action].grid(row=0, column=1)

        # Optimal action display
        self.optimal_frame = ttk.LabelFrame(self, text="Optimal Play", padding=8)
        self.optimal_frame.grid(row=4, column=0, columnspan=3, pady=8, padx=8, sticky='ew')

        self.optimal_action = ttk.Label(self.optimal_frame, text="--",
                                        font=('Arial', 14, 'bold'))
        self.optimal_action.pack()

        self.optimal_ev = ttk.Label(self.optimal_frame, text="EV: --",
                                    font=('Arial', 10))
        self.optimal_ev.pack()

        # **NEW: EV difference indicator**
        self.ev_diff_label = ttk.Label(self.optimal_frame, text="",
                                       font=('Arial', 8), foreground='gray')
        self.ev_diff_label.pack()

        # Dealer probabilities - SMALLER
        self.dealer_frame = ttk.LabelFrame(self, text="Dealer Probs", padding=6)
        self.dealer_frame.grid(row=5, column=0, columnspan=3, pady=6, padx=8, sticky='ew')

        self.dealer_labels = {}
        outcomes = ['bust', '17', '18', '19', '20', '21']

        for i, outcome in enumerate(outcomes):
            row = i // 3
            col = i % 3

            frame = ttk.Frame(self.dealer_frame)
            frame.grid(row=row, column=col, padx=3, pady=1)

            ttk.Label(frame, text=f"{outcome}:", width=4).grid(row=0, column=0)

            self.dealer_labels[outcome] = ttk.Label(frame, text="--",
                                                    font=('Courier', 8))
            self.dealer_labels[outcome].grid(row=0, column=1)

    def update_analysis(self, player_hand, dealer_upcard):
        """ENHANCED: Update display with better error handling and caching."""

        # Prevent recursive updates
        if self.is_updating:
            print("EV_DISPLAY: Update already in progress, skipping")
            return

        try:
            self.is_updating = True
            self.status_label.config(text="Calculating...", foreground='blue')

            # Create update hash for caching
            update_hash = self._create_update_hash(player_hand, dealer_upcard)
            if update_hash == self.last_update_hash:
                print("EV_DISPLAY: No change detected, skipping update")
                self.status_label.config(text="Ready", foreground='gray')
                return

            print(f"EV_DISPLAY: Updating analysis for {player_hand} vs {dealer_upcard}")

            # Update hand display
            hand_display_parts = []
            for rank, suit in player_hand:
                display_rank = '10' if rank == 'T' else rank
                suit_symbols = {'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣'}
                display_suit = suit_symbols.get(suit, suit)
                hand_display_parts.append(f"{display_rank}{display_suit}")
            hand_str = ', '.join(hand_display_parts)

            # Show dealer upcard
            dealer_display = '10' if dealer_upcard == 'T' else dealer_upcard
            self.hand_label.config(text=f"Hand: {hand_str} vs Dealer: {dealer_display}")

            # Get analysis
            analysis = self.ev_calculator.get_detailed_analysis(player_hand, dealer_upcard)

            if 'error' in analysis:
                self._show_error(analysis['error'])
                return

            # Update action EVs
            self._update_action_evs(analysis['actions'])

            # Update optimal action
            self._update_optimal_action(analysis)

            # Update dealer probabilities
            self._update_dealer_probabilities(dealer_upcard)

            # Cache successful update
            self.last_update_hash = update_hash
            self.status_label.config(text="Updated", foreground='green')

            print("EV_DISPLAY: Update completed successfully")

        except Exception as e:
            print(f"EV_DISPLAY ERROR: {e}")
            import traceback
            traceback.print_exc()
            self._show_error(f"Calculation error: {str(e)}")

        finally:
            self.is_updating = False

    def _create_update_hash(self, player_hand, dealer_upcard):
        """Create hash for update caching."""
        try:
            hand_tuple = tuple(player_hand)
            comp_state = None
            if hasattr(self.ev_calculator, 'comp_panel'):
                comp_items = tuple(sorted(self.ev_calculator.comp_panel.comp.items()))
                comp_state = (comp_items, self.ev_calculator.comp_panel.decks)
            return hash((hand_tuple, dealer_upcard, comp_state))
        except:
            return None

    def _update_action_evs(self, actions):
        """Update the action EV displays."""
        for action, ev in actions.items():
            if action in self.ev_labels:
                if ev >= -1.0:  # Valid action
                    ev_text = f"{ev:+.4f}"
                    color = self._get_ev_color(ev)
                    self.ev_labels[action].config(text=ev_text, foreground=color)
                else:
                    self.ev_labels[action].config(text="N/A", foreground='gray')

    def _update_optimal_action(self, analysis):
        """Update the optimal action display."""
        optimal_action = analysis['optimal_action'].upper()
        optimal_ev = analysis['optimal_ev']

        self.optimal_action.config(text=optimal_action)
        self.optimal_ev.config(text=f"EV: {optimal_ev:+.4f}")

        # Color code optimal action
        optimal_color = self._get_ev_color(optimal_ev)
        self.optimal_action.config(foreground=optimal_color)

        # **NEW: Show EV differences**
        ev_differences = analysis.get('ev_difference', {})
        if ev_differences:
            # Find the second-best option
            sorted_diffs = sorted([(diff, action) for action, diff in ev_differences.items()
                                   if diff > 0 and action != analysis['optimal_action']])
            if sorted_diffs:
                second_best_diff, second_best_action = sorted_diffs[0]
                self.ev_diff_label.config(
                    text=f"vs {second_best_action}: +{second_best_diff:.4f}",
                    foreground='darkgreen'
                )
            else:
                self.ev_diff_label.config(text="")
        else:
            self.ev_diff_label.config(text="")

    def _update_dealer_probabilities(self, dealer_upcard):
        """Update dealer probability display."""
        try:
            dealer_probs = self.ev_calculator.get_dealer_probabilities(dealer_upcard)
            for outcome, prob in dealer_probs.items():
                if outcome in self.dealer_labels:
                    self.dealer_labels[outcome].config(text=f"{prob:.3f}")
        except Exception as e:
            print(f"EV_DISPLAY: Error updating dealer probabilities: {e}")
            # Clear dealer probabilities on error
            for outcome in self.dealer_labels:
                self.dealer_labels[outcome].config(text="--")

    def _show_error(self, error_message):
        """Show error state in the display."""
        self.optimal_action.config(text="ERROR", foreground='red')
        self.optimal_ev.config(text=f"Error: {error_message[:30]}...")
        self.status_label.config(text="Error", foreground='red')

        # Clear other displays
        for action in self.ev_labels:
            self.ev_labels[action].config(text="--", foreground='black')
        for outcome in self.dealer_labels:
            self.dealer_labels[outcome].config(text="--")

    def _get_ev_color(self, ev):
        """Get color based on EV value"""
        if ev > 0:
            return 'darkgreen'
        elif ev > -0.1:
            return 'green'
        elif ev > -0.3:
            return 'orange'
        else:
            return 'red'

    def clear_display(self):
        """ENHANCED: Clear all displays and reset cache"""
        print("EV_DISPLAY: Clearing display")

        self.hand_label.config(text="Hand: --")
        self.status_label.config(text="Ready", foreground='gray')

        # Clear action EVs
        for action in self.ev_labels:
            self.ev_labels[action].config(text="--", foreground='black')

        # Clear optimal action
        self.optimal_action.config(text="--", foreground='black')
        self.optimal_ev.config(text="EV: --")
        self.ev_diff_label.config(text="")

        # Clear dealer probabilities
        for outcome in self.dealer_labels:
            self.dealer_labels[outcome].config(text="--")

        # Reset cache
        self.last_update_hash = None

    def force_update(self, player_hand=None, dealer_upcard=None):
        """NEW: Force update by clearing cache."""
        print("EV_DISPLAY: Force update called")
        self.last_update_hash = None
        if player_hand and dealer_upcard:
            self.update_analysis(player_hand, dealer_upcard)
        else:
            self.clear_display()

    def test_display(self):
        """NEW: Test the display with sample data."""
        print("EV_DISPLAY: Running test display")

        try:
            # Test with sample hand
            test_hand = [('10', 'H'), ('6', 'S')]
            test_upcard = 'K'

            self.update_analysis(test_hand, test_upcard)

            # Show test indicator
            self.status_label.config(text="Test Mode", foreground='orange')

            return True
        except Exception as e:
            print(f"EV_DISPLAY: Test failed: {e}")
            self._show_error(f"Test failed: {e}")
            return False