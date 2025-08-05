# ev_display_panel.py
import tkinter as tk
from tkinter import ttk


class EVDisplayPanel(tk.Frame):
    """Panel to display EV calculations and recommendations"""

    def __init__(self, parent, ev_calculator):
        super().__init__(parent)
        self.ev_calculator = ev_calculator
        self.setup_ui()

    def setup_ui(self):
        # Title
        title = ttk.Label(self, text="Expected Value Analysis",
                          font=('Arial', 14, 'bold'))
        title.grid(row=0, column=0, columnspan=3, pady=10)

        # Current hand info
        self.hand_label = ttk.Label(self, text="Hand: --", font=('Arial', 12))
        self.hand_label.grid(row=1, column=0, columnspan=3, pady=5)

        # Action EVs frame
        ev_frame = ttk.LabelFrame(self, text="Action EVs", padding=10)
        ev_frame.grid(row=2, column=0, columnspan=3, pady=10, padx=10, sticky='ew')

        # EV displays
        self.ev_labels = {}
        actions = ['stand', 'hit', 'double', 'split', 'surrender']

        for i, action in enumerate(actions):
            row = i // 2
            col = i % 2

            frame = ttk.Frame(ev_frame)
            frame.grid(row=row, column=col, padx=5, pady=5, sticky='w')

            ttk.Label(frame, text=f"{action.capitalize()}:",
                      width=10).grid(row=0, column=0)

            self.ev_labels[action] = ttk.Label(frame, text="--",
                                               font=('Courier', 10, 'bold'))
            self.ev_labels[action].grid(row=0, column=1)

        # Optimal action display
        self.optimal_frame = ttk.LabelFrame(self, text="Optimal Play", padding=10)
        self.optimal_frame.grid(row=3, column=0, columnspan=3, pady=10, padx=10, sticky='ew')

        self.optimal_action = ttk.Label(self.optimal_frame, text="--",
                                        font=('Arial', 16, 'bold'))
        self.optimal_action.pack()

        self.optimal_ev = ttk.Label(self.optimal_frame, text="EV: --",
                                    font=('Arial', 12))
        self.optimal_ev.pack()

        # Dealer probabilities
        self.dealer_frame = ttk.LabelFrame(self, text="Dealer Probabilities", padding=10)
        self.dealer_frame.grid(row=4, column=0, columnspan=3, pady=10, padx=10, sticky='ew')

        self.dealer_labels = {}
        outcomes = ['bust', '17', '18', '19', '20', '21']

        for i, outcome in enumerate(outcomes):
            row = i // 3
            col = i % 3

            frame = ttk.Frame(self.dealer_frame)
            frame.grid(row=row, column=col, padx=5, pady=2)

            ttk.Label(frame, text=f"{outcome}:", width=5).grid(row=0, column=0)

            self.dealer_labels[outcome] = ttk.Label(frame, text="--",
                                                    font=('Courier', 9))
            self.dealer_labels[outcome].grid(row=0, column=1)

    def update_analysis(self, player_hand, dealer_upcard):
        """Update display with new hand analysis"""
        # Update hand display
        hand_str = ', '.join(str(c) for c in player_hand)
        self.hand_label.config(text=f"Hand: {hand_str} vs Dealer: {dealer_upcard}")

        # Get analysis
        analysis = self.ev_calculator.get_detailed_analysis(player_hand, dealer_upcard)

        if 'error' in analysis:
            self.optimal_action.config(text=f"Error: {analysis['error']}")
            return

        # Update action EVs
        for action, ev in analysis['actions'].items():
            if ev >= -1.0:  # Valid action
                ev_text = f"{ev:+.4f}"
                color = self._get_ev_color(ev)
                self.ev_labels[action].config(text=ev_text, foreground=color)
            else:
                self.ev_labels[action].config(text="N/A", foreground='gray')

        # Update optimal action
        self.optimal_action.config(text=analysis['optimal_action'].upper())
        self.optimal_ev.config(text=f"EV: {analysis['optimal_ev']:+.4f}")

        # Color code optimal action
        optimal_color = self._get_ev_color(analysis['optimal_ev'])
        self.optimal_action.config(foreground=optimal_color)

        # Update dealer probabilities
        dealer_probs = self.ev_calculator.get_dealer_probabilities(dealer_upcard)
        for outcome, prob in dealer_probs.items():
            if outcome in self.dealer_labels:
                self.dealer_labels[outcome].config(text=f"{prob:.3f}")

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