# main_app_integration.py
import tkinter as tk
from comp_panel import CompPanel  # Your existing comp_panel
from ev_calculator import EVCalculator
from ev_display_panel import EVDisplayPanel


class BlackjackApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Blackjack Tracker with EV Analysis")

        # Your existing comp_panel
        self.comp_panel = CompPanel(root)
        self.comp_panel.pack(side='left')

        # Create EV calculator
        self.ev_calc = EVCalculator(self.comp_panel)

        # Create EV display
        self.ev_display = EVDisplayPanel(root, self.ev_calc)
        self.ev_display.pack(side='right', fill='both', expand=True)

        # Hook into hand completion to auto-calculate
        self.setup_hooks()

    def setup_hooks(self):
        """Connect to your existing game flow"""
        # Example: When a hand is complete, calculate EV
        # You'll need to adapt this to your actual code
        pass

    def analyze_current_hand(self, player_hand, dealer_upcard):
        """Call this when you want to analyze a hand"""
        self.ev_display.update_analysis(player_hand, dealer_upcard)

    def get_real_time_advice(self, player_hand, dealer_upcard):
        """Get advice for current decision"""
        result = self.ev_calc.calculate_exact_ev(player_hand, dealer_upcard)

        if result['success']:
            return {
                'action': result['optimal_action'],
                'ev': result['optimal_ev'],
                'confidence': 'HIGH' if result['composition_used'] else 'MEDIUM'
            }
        return None


# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    app = BlackjackApp(root)

    # Test with a hand
    app.analyze_current_hand(['K', '6'], 'T')

    root.mainloop()