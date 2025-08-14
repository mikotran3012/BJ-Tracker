# dealer_prob_panel.py - Enhanced with continuous updates and better caching
import tkinter as tk
import bjlogic_cpp


class DealerProbPanel(tk.Frame):
    """Enhanced panel for continuous dealer probability updates based on composition."""

    def __init__(self, parent, bg_color='#2b2b2b'):
        super().__init__(parent, bg=bg_color)
        self.bg_color = bg_color
        self.last_upcard = None
        self.last_composition_state = None
        self.is_updating = False
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

        # Composition status indicator
        self.comp_status_label = tk.Label(container, text="Cards: 0",
                                          font=('Consolas', 8),
                                          bg=self.bg_color, fg='#888888')
        self.comp_status_label.pack(pady=(0, 2))

        # Update mode indicator
        self.mode_label = tk.Label(container, text="[Live]",
                                   font=('Consolas', 7),
                                   bg=self.bg_color, fg='#00ff00')
        self.mode_label.pack(pady=(0, 2))

    def update_probabilities(self, dealer_upcard, comp_panel):
        """Update probabilities with composition tracking."""
        if self.is_updating:
            print("PROB_PANEL: Update already in progress, skipping")
            return

        print(f"PROB_PANEL: update_probabilities called with upcard={dealer_upcard}")

        try:
            self.is_updating = True

            # Check if we need to update (caching logic)
            current_comp_state = self._get_composition_hash(comp_panel)

            if (dealer_upcard == self.last_upcard and
                    current_comp_state == self.last_composition_state):
                print("PROB_PANEL: No update needed (cached)")
                return

            # Store current state for caching
            self.last_upcard = dealer_upcard
            self.last_composition_state = current_comp_state

            # Update composition status display
            total_cards = sum(comp_panel.comp.values())
            cards_remaining = comp_panel.cards_left()
            self.comp_status_label.config(
                text=f"Cards: {total_cards}/{cards_remaining}"
            )

            # Calculate and display probabilities
            self._calculate_and_display(dealer_upcard, comp_panel)

            # Update mode indicator
            self.mode_label.config(text="[Live]", fg='#00ff00')

        except Exception as e:
            print(f"PROB_PANEL ERROR: {e}")
            import traceback
            traceback.print_exc()
            self.mode_label.config(text="[Error]", fg='#ff4444')
            self.clear_display()
        finally:
            self.is_updating = False

    def force_update(self, dealer_upcard=None, comp_panel=None):
        """Force update by clearing cache and recalculating."""
        print("PROB_PANEL: Force update called")

        # Clear cache to force recalculation
        self.last_upcard = None
        self.last_composition_state = None

        # Update mode indicator
        self.mode_label.config(text="[Forced]", fg='#ffff00')

        if dealer_upcard and comp_panel:
            self.update_probabilities(dealer_upcard, comp_panel)
        elif comp_panel:
            # No dealer upcard, show average probabilities
            self.update_all_possible_upcards(comp_panel)
        else:
            self.clear_display()

    def update_all_possible_upcards(self, comp_panel):
        """Update display showing average probabilities for all possible dealer upcards."""
        if self.is_updating:
            return

        print("PROB_PANEL: Updating for all possible upcards")

        try:
            self.is_updating = True

            # Calculate weighted average probabilities
            all_upcard_probs = {}
            total_weight = 0

            for upcard in ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']:
                try:
                    # Get remaining cards of this rank
                    cards_dealt = comp_panel.comp.get(upcard, 0)
                    total_cards_per_rank = comp_panel.decks * 4
                    remaining = max(0, total_cards_per_rank - cards_dealt)

                    if remaining > 0:
                        # Calculate probabilities for this upcard
                        result = self._calculate_single_upcard(upcard, comp_panel)

                        # Weight by number of remaining cards
                        for outcome, prob in result.items():
                            if outcome not in all_upcard_probs:
                                all_upcard_probs[outcome] = 0
                            all_upcard_probs[outcome] += prob * remaining

                        total_weight += remaining

                except Exception as e:
                    print(f"PROB_PANEL: Error calculating for upcard {upcard}: {e}")
                    continue

            # Normalize by total weight
            if total_weight > 0:
                for outcome in all_upcard_probs:
                    all_upcard_probs[outcome] /= total_weight

                # Update display with average probabilities
                self._display_probabilities(all_upcard_probs)

                # Update upcard display
                self.upcard_label.config(text="Up card: AVG")

                # Update composition status
                total_cards = sum(comp_panel.comp.values())
                cards_remaining = comp_panel.cards_left()
                self.comp_status_label.config(
                    text=f"Cards: {total_cards}/{cards_remaining}"
                )

                # Update mode indicator
                self.mode_label.config(text="[Average]", fg='#00ffff')
            else:
                self.clear_display()

        except Exception as e:
            print(f"PROB_PANEL ERROR in update_all_possible_upcards: {e}")
            self.clear_display()
        finally:
            self.is_updating = False

    def _calculate_and_display(self, dealer_upcard, comp_panel):
        """Calculate and display probabilities for a specific upcard."""
        try:
            # Check what functions are available
            if hasattr(bjlogic_cpp, 'calculate_dealer_probabilities_dict'):
                print("PROB_PANEL: Using calculate_dealer_probabilities_dict")
                result = self._use_advanced_calculation(dealer_upcard, comp_panel)
            elif hasattr(bjlogic_cpp, 'analyze_dealer_fresh_deck'):
                print("PROB_PANEL: Using analyze_dealer_fresh_deck as fallback")
                result = self._use_fresh_deck_fallback(dealer_upcard, comp_panel)
            else:
                print("PROB_PANEL ERROR: No suitable function found")
                self.clear_display()
                return

            # Display the results
            self._display_probabilities(result)

            # Update upcard display
            display_rank = '10' if dealer_upcard == 'T' else dealer_upcard
            self.upcard_label.config(text=f"Up card: {display_rank}")

        except Exception as e:
            print(f"PROB_PANEL ERROR in _calculate_and_display: {e}")
            raise

    def _use_advanced_calculation(self, dealer_upcard, comp_panel):
        """Use the advanced calculation with composition awareness."""
        try:
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

            # Create rules dict matching your game rules
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
            return result

        except Exception as e:
            print(f"PROB_PANEL ERROR in _use_advanced_calculation: {e}")
            raise

    def _use_fresh_deck_fallback(self, dealer_upcard, comp_panel):
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

            print("PROB_PANEL: Using fresh deck calculation (composition not factored)")
            return result

        except Exception as e:
            print(f"PROB_PANEL ERROR in _use_fresh_deck_fallback: {e}")
            raise

    def _calculate_single_upcard(self, upcard, comp_panel):
        """Calculate probabilities for a single upcard."""
        try:
            upcard_value = self._convert_rank_to_value(upcard)

            # Get cards that have been removed from the deck
            removed_cards = []
            for rank in ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']:
                cards_dealt = comp_panel.comp.get(rank, 0)
                if rank == 'A':
                    card_val = 1
                elif rank in ['T', 'J', 'Q', 'K']:
                    card_val = 10
                else:
                    card_val = int(rank)

                for _ in range(cards_dealt):
                    removed_cards.append(card_val)

            # Create rules dict
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

            # Create the engine
            engine = bjlogic_cpp.AdvancedEVEngine()

            # Call the function
            result = bjlogic_cpp.calculate_dealer_probabilities_dict(
                engine,
                upcard_value,
                removed_cards,
                rules_dict
            )

            return result

        except Exception as e:
            print(f"PROB_PANEL ERROR in _calculate_single_upcard: {e}")
            return {}

    def _display_probabilities(self, result):
        """Display probability results with color coding."""
        try:
            # Update probability displays
            self.prob_labels['17'].config(text=f"{result.get('total_17_prob', 0):.5f}")
            self.prob_labels['18'].config(text=f"{result.get('total_18_prob', 0):.5f}")
            self.prob_labels['19'].config(text=f"{result.get('total_19_prob', 0):.5f}")
            self.prob_labels['20'].config(text=f"{result.get('total_20_prob', 0):.5f}")
            self.prob_labels['21'].config(text=f"{result.get('total_21_prob', 0):.5f}")
            self.prob_labels['BJ'].config(text=f"{result.get('blackjack_prob', 0):.5f}")
            self.prob_labels['Bust'].config(text=f"{result.get('bust_prob', 0):.5f}")

            # Color code based on dealer advantage
            bust_prob = result.get('bust_prob', 0)
            if bust_prob > 0.40:
                self.prob_labels['Bust'].config(fg='#00ff00')  # Green - good for player
            elif bust_prob > 0.30:
                self.prob_labels['Bust'].config(fg='#ffff00')  # Yellow - moderate
            else:
                self.prob_labels['Bust'].config(fg='#ff4444')  # Red - bad for player

            # Color code high totals
            total_20_21 = result.get('total_20_prob', 0) + result.get('total_21_prob', 0)
            if total_20_21 > 0.35:
                self.prob_labels['20'].config(fg='#ff4444')  # Red - dangerous
                self.prob_labels['21'].config(fg='#ff4444')
            else:
                self.prob_labels['20'].config(fg='#ffffff')  # White - normal
                self.prob_labels['21'].config(fg='#ffffff')

        except Exception as e:
            print(f"PROB_PANEL ERROR in _display_probabilities: {e}")

    def _get_composition_hash(self, comp_panel):
        """Create a hash of the current deck composition for caching."""
        try:
            comp_items = sorted(comp_panel.comp.items())
            return hash((tuple(comp_items), comp_panel.decks))
        except:
            return None

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
        """Clear all probability displays and reset cache."""
        for label in self.prob_labels.values():
            label.config(text="0.00000", fg='#00ff00')

        self.upcard_label.config(text="Up card: -")
        self.comp_status_label.config(text="Cards: 0")
        self.mode_label.config(text="[Idle]", fg='#888888')

        # Reset caching
        self.last_upcard = None
        self.last_composition_state = None

    def test_display(self):
        """Test the display with sample data."""
        print("PROB_PANEL: Running test display")

        try:
            # Create test probabilities
            test_probs = {
                'total_17_prob': 0.14523,
                'total_18_prob': 0.13982,
                'total_19_prob': 0.13445,
                'total_20_prob': 0.17892,
                'total_21_prob': 0.07234,
                'blackjack_prob': 0.04723,
                'bust_prob': 0.28201
            }

            # Display test probabilities
            self._display_probabilities(test_probs)

            # Update displays
            self.upcard_label.config(text="Up card: TEST")
            self.comp_status_label.config(text="Cards: TEST")
            self.mode_label.config(text="[Test]", fg='#ff00ff')

            return True

        except Exception as e:
            print(f"PROB_PANEL: Test failed: {e}")
            return False