# ev_calculator.py
import bjlogic_cpp


class EVCalculator:
    """Bridge between comp_panel and C++ EV engine"""

    def __init__(self, comp_panel):
        self.comp_panel = comp_panel
        self.engine = bjlogic_cpp.AdvancedEVEngine()

        # Set up YOUR game rules
        self.rules = bjlogic_cpp.RulesConfig()
        self.rules.num_decks = 8
        self.rules.dealer_hits_soft_17 = False
        self.rules.surrender_allowed = True
        self.rules.blackjack_payout = 1.5
        self.rules.double_after_split = 0
        self.rules.resplitting_allowed = False
        self.rules.max_split_hands = 2
        self.rules.dealer_peek_on_ten = False

    def calculate_exact_ev(self, player_hand, dealer_upcard, count_system="Hi-Lo"):
        """Calculate exact EV based on current deck composition"""

        # Convert hand format if needed (e.g., ['K', '6'] -> [10, 6])
        numeric_hand = self._convert_to_numeric(player_hand)
        numeric_upcard = self._convert_card(dealer_upcard)

        # Use the direct comp_panel integration
        result = bjlogic_cpp.calculate_ev_from_comp_panel(
            hand=numeric_hand,
            dealer_upcard=numeric_upcard,
            comp_panel=self.comp_panel,
            rules=self.rules,
            counter_system=count_system
        )

        return result

    def get_detailed_analysis(self, player_hand, dealer_upcard):
        """Get comprehensive analysis with all action EVs"""
        result = self.calculate_exact_ev(player_hand, dealer_upcard)

        if result['success']:
            analysis = {
                'optimal_action': result['optimal_action'],
                'optimal_ev': result['optimal_ev'],
                'actions': {
                    'stand': result['stand_ev'],
                    'hit': result['hit_ev'],
                    'double': result['double_ev'],
                    'split': result['split_ev'],
                    'surrender': result['surrender_ev']
                },
                'variance': result.get('variance', 1.3),
                'insurance_ev': result.get('insurance_ev', -1.0),
                'composition_used': result.get('composition_used', True)
            }

            # Add decision quality info
            analysis['ev_difference'] = self._calculate_ev_differences(analysis['actions'], analysis['optimal_ev'])

            return analysis
        else:
            return {'error': result.get('error', 'Unknown error')}

    def _convert_to_numeric(self, hand):
        """Convert card representations to numeric values"""
        numeric_hand = []
        for card in hand:
            numeric_hand.append(self._convert_card(card))
        return numeric_hand

    def _convert_card(self, card):
        """Convert single card to numeric value"""
        if isinstance(card, int):
            return card

        card_str = str(card).upper()
        if card_str in ['J', 'Q', 'K']:
            return 10
        elif card_str == 'A':
            return 1
        elif card_str == 'T':
            return 10
        else:
            return int(card_str)

    def _calculate_ev_differences(self, actions, optimal_ev):
        """Calculate EV loss for each non-optimal action"""
        differences = {}
        for action, ev in actions.items():
            if ev >= -1.0:  # Valid action
                differences[action] = optimal_ev - ev
        return differences

    def get_dealer_probabilities(self, dealer_upcard):
        """Get exact dealer outcome probabilities"""
        numeric_upcard = self._convert_card(dealer_upcard)

        # Create deck composition from comp_panel
        deck_comp = bjlogic_cpp.DeckComposition(8)

        # Note: You might need to adjust the deck composition based on dealt cards
        # This is a simplified version

        result = self.engine.calculate_dealer_probabilities_advanced(
            numeric_upcard, deck_comp, self.rules
        )

        return {
            'bust': result.bust_prob,
            '17': result.total_17_prob,
            '18': result.total_18_prob,
            '19': result.total_19_prob,
            '20': result.total_20_prob,
            '21': result.total_21_prob,
            'blackjack': result.blackjack_prob
        }