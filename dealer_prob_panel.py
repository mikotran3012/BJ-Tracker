# dealer_prob_panel.py - Using the existing function
import tkinter as tk
import bjlogic_cpp


class DealerProbPanel(tk.Frame):
    """Panel to display dealer outcome probabilities using C++ recursive engine."""

    def __init__(self, parent, bg_color='#2b2b2b'):
        super().__init__(parent, bg=bg_color)
        self.bg_color = bg_color
        self.setup_ui()

    def setup_ui(self):
        """Setup the probability display UI."""
        # Main container with dark theme
        container = tk.Frame(self, bg=self.bg_color, relief=tk.RAISED, bd=1)
        container.pack(fill='both', expand=True, padx=2, pady=2)

        # Title
        title = tk.Label(container, text="Probabilities",
                         font=('Consolas', 9, 'bold'),
                         bg=self.bg_color, fg='#00ff00')
        title.pack(pady=(2, 4))

        # Probability rows
        self.prob_labels = {}
        outcomes = [
            ('17', '#ffffff'),
            ('18', '#ffffff'),
            ('19', '#ffffff'),
            ('20', '#ffffff'),
            ('21', '#ffffff'),
            ('BJ', '#ffff00'),  # Yellow for blackjack
            ('Bust', '#ff4444')  # Red for bust
        ]

        for outcome, color in outcomes:
            row = tk.Frame(container, bg=self.bg_color)
            row.pack(fill='x', padx=4, pady=1)

            # Outcome label (left side)
            outcome_label = tk.Label(row, text=f"{outcome:>4}",
                                     font=('Consolas', 9, 'bold'),
                                     bg=self.bg_color, fg=color, width=5, anchor='e')
            outcome_label.pack(side='left')

            # Probability value (right side)
            prob_label = tk.Label(row, text="0.00000",
                                  font=('Consolas', 9),
                                  bg=self.bg_color, fg='#00ff00', width=8, anchor='e')
            prob_label.pack(side='right')

            self.prob_labels[outcome] = prob_label

        # Add separator
        sep = tk.Frame(container, bg='#444444', height=1)
        sep.pack(fill='x', padx=4, pady=4)

        # Upcard display
        self.upcard_label = tk.Label(container, text="Up card: -",
                                     font=('Consolas', 9, 'bold'),
                                     bg=self.bg_color, fg='#ffff00')
        self.upcard_label.pack(pady=(0, 2))

    def update_probabilities(self, dealer_upcard, comp_panel):
        """Update probabilities using the C++ recursive dealer engine."""
        print(f"PROB_PANEL: update_probabilities called with upcard={dealer_upcard}")

        try:
            # Check what functions are available
            if hasattr(bjlogic_cpp, 'calculate_dealer_probabilities_dict'):
                print("PROB_PANEL: Using calculate_dealer_probabilities_dict")
                self._use_existing_function(dealer_upcard, comp_panel)
            elif hasattr(bjlogic_cpp, 'analyze_dealer_fresh_deck'):
                print("PROB_PANEL: Using analyze_dealer_fresh_deck as fallback")
                self._use_fresh_deck_function(dealer_upcard, comp_panel)
            else:
                print("PROB_PANEL ERROR: No suitable function found")
                print("Available functions:", [x for x in dir(bjlogic_cpp) if 'dealer' in x.lower()])
                self.clear_display()

        except Exception as e:
            print(f"PROB_PANEL ERROR: {e}")
            import traceback
            traceback.print_exc()
            self.clear_display()

    def _use_existing_function(self, dealer_upcard, comp_panel):
        """Use the calculate_dealer_probabilities_dict function."""
        try:
            # Convert upcard to internal format
            upcard_value = self._convert_rank_to_value(dealer_upcard)

            # Get cards that have been removed from the deck
            removed_cards = []
            for rank in ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']:
                cards_dealt = comp_panel.comp.get(rank, 0)
                # Convert rank to numeric for C++
                if rank == 'A':
                    card_val = 1
                elif rank in ['T', 'J', 'Q', 'K']:
                    card_val = 10
                else:
                    card_val = int(rank)

                # Add each removed card to the list
                for _ in range(cards_dealt):
                    removed_cards.append(card_val)

            print(f"PROB_PANEL: {len(removed_cards)} cards removed from deck")

            # Create rules dict
            rules_dict = {
                'num_decks': comp_panel.decks,
                'dealer_hits_soft_17': False,  # Your rule: stands on soft 17
                'dealer_peek_on_ten': False,  # Your rule: no peek on 10
                'surrender_allowed': True,
                'blackjack_payout': 1.5,
                'double_after_split': 0,
                'resplitting_allowed': False,
                'max_split_hands': 2
            }

            # Create the engine
            engine = bjlogic_cpp.AdvancedEVEngine()

            # Call the function
            result = bjlogic_cpp.calculate_dealer_probabilities_dict(
                engine,
                upcard_value,
                removed_cards,
                rules_dict
            )

            print(f"PROB_PANEL: Got result with bust_prob={result.get('bust_prob', 'N/A')}")

            # Update display
            self.prob_labels['17'].config(text=f"{result.get('total_17_prob', 0):.5f}")
            self.prob_labels['18'].config(text=f"{result.get('total_18_prob', 0):.5f}")
            self.prob_labels['19'].config(text=f"{result.get('total_19_prob', 0):.5f}")
            self.prob_labels['20'].config(text=f"{result.get('total_20_prob', 0):.5f}")
            self.prob_labels['21'].config(text=f"{result.get('total_21_prob', 0):.5f}")
            self.prob_labels['BJ'].config(text=f"{result.get('blackjack_prob', 0):.5f}")
            self.prob_labels['Bust'].config(text=f"{result.get('bust_prob', 0):.5f}")

            # Update upcard display
            display_rank = '10' if dealer_upcard == 'T' else dealer_upcard
            self.upcard_label.config(text=f"Up card: {display_rank}")

            # Color code based on dealer advantage
            bust_prob = result.get('bust_prob', 0)
            if bust_prob > 0.40:
                self.prob_labels['Bust'].config(fg='#00ff00')  # Green
            elif bust_prob > 0.30:
                self.prob_labels['Bust'].config(fg='#ffff00')  # Yellow
            else:
                self.prob_labels['Bust'].config(fg='#ff4444')  # Red

        except Exception as e:
            print(f"PROB_PANEL ERROR in _use_existing_function: {e}")
            raise

    def _use_fresh_deck_function(self, dealer_upcard, comp_panel):
        """Use the simpler fresh deck function as fallback."""
        try:
            upcard_value = self._convert_rank_to_value(dealer_upcard)

            rules_dict = {
                'num_decks': comp_panel.decks,
                'dealer_hits_soft_17': False,
                'dealer_peek_on_ten': False,
                'surrender_allowed': True,
                'blackjack_payout': 1.5,
                'double_after_split': 0,
                'resplitting_allowed': False,
                'max_split_hands': 2
            }

            result = bjlogic_cpp.analyze_dealer_fresh_deck(upcard_value, rules_dict)

            # Update display
            self.prob_labels['17'].config(text=f"{result.get('total_17_prob', 0):.5f}")
            self.prob_labels['18'].config(text=f"{result.get('total_18_prob', 0):.5f}")
            self.prob_labels['19'].config(text=f"{result.get('total_19_prob', 0):.5f}")
            self.prob_labels['20'].config(text=f"{result.get('total_20_prob', 0):.5f}")
            self.prob_labels['21'].config(text=f"{result.get('total_21_prob', 0):.5f}")
            self.prob_labels['BJ'].config(text=f"{result.get('blackjack_prob', 0):.5f}")
            self.prob_labels['Bust'].config(text=f"{result.get('bust_prob', 0):.5f}")

            # Update upcard display
            display_rank = '10' if dealer_upcard == 'T' else dealer_upcard
            self.upcard_label.config(text=f"Up card: {display_rank}")

        except Exception as e:
            print(f"PROB_PANEL ERROR in _use_fresh_deck_function: {e}")
            raise

    def _convert_rank_to_value(self, rank):
        """Convert rank string to numeric value for C++."""
        if rank == 'A':
            return 1
        elif rank in ['J', 'Q', 'K']:
            return 10
        elif rank == 'T' or rank == '10':
            return 10
        else:
            try:
                return int(rank)
            except:
                return 10

    def clear_display(self):
        """Clear all probability displays."""
        for label in self.prob_labels.values():
            label.config(text="0.00000")
        self.upcard_label.config(text="Up card: -")