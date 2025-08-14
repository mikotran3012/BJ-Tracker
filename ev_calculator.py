# ev_calculator.py - Enhanced with caching and continuous updates
import bjlogic_cpp


class EVCalculator:
    """ENHANCED: Bridge between comp_panel and C++ EV engine with caching and continuous updates"""

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

        # **NEW: Caching system**
        self.last_calculation_hash = None
        self.cached_result = None

    def calculate_exact_ev(self, player_hand, dealer_upcard, count_system="Hi-Lo"):
        """ENHANCED: Calculate exact EV with caching and composition awareness"""

        print(f"EV_CALC: calculate_exact_ev called")
        print(f"  Player hand: {player_hand}")
        print(f"  Dealer upcard: {dealer_upcard}")

        # **NEW: Create calculation hash for caching**
        calc_hash = self._create_calculation_hash(player_hand, dealer_upcard)

        # Check if we can use cached result
        if (self.last_calculation_hash == calc_hash and
                self.cached_result is not None):
            print("EV_CALC: Using cached result")
            return self.cached_result

        try:
            # Convert hand format if needed (e.g., ['K', '6'] -> [10, 6])
            numeric_hand = self._convert_to_numeric(player_hand)

            # Handle dealer upcard - it might be just a string rank
            if isinstance(dealer_upcard, tuple):
                numeric_upcard = self._convert_card(dealer_upcard[0])  # Take rank part
            else:
                numeric_upcard = self._convert_card(dealer_upcard)

            print(f"EV_CALC: Converted - Hand: {numeric_hand}, Upcard: {numeric_upcard}")

            # **ENHANCED: Check if we have the comp_panel integration function**
            if hasattr(bjlogic_cpp, 'calculate_ev_from_comp_panel'):
                print("EV_CALC: Using calculate_ev_from_comp_panel")
                result = bjlogic_cpp.calculate_ev_from_comp_panel(
                    hand=numeric_hand,
                    dealer_upcard=numeric_upcard,
                    comp_panel=self.comp_panel,
                    rules=self.rules,
                    counter_system=count_system
                )
            else:
                print("EV_CALC: Using fallback method")
                result = self._calculate_ev_fallback(numeric_hand, numeric_upcard)

            # Cache successful result
            self.last_calculation_hash = calc_hash
            self.cached_result = result

            print(f"EV_CALC: Calculation successful, optimal action: {result.get('optimal_action', 'unknown')}")
            return result

        except Exception as e:
            print(f"EV_CALC ERROR: {e}")
            import traceback
            traceback.print_exc()

            # Return error result
            error_result = {
                'success': False,
                'error': str(e),
                'optimal_action': 'hit',  # Safe default
                'optimal_ev': -0.5,
                'stand_ev': -0.5,
                'hit_ev': -0.4,
                'double_ev': -1.0,
                'split_ev': -1.0,
                'surrender_ev': -0.5
            }
            return error_result

    def _calculate_ev_fallback(self, numeric_hand, numeric_upcard):
        """Fallback EV calculation using basic engine if comp_panel integration not available."""
        print("EV_CALC: Using fallback calculation method")

        try:
            # Create a basic deck composition
            deck_comp = bjlogic_cpp.DeckComposition(self.comp_panel.decks)

            # **NEW: Adjust deck composition based on dealt cards**
            for rank in ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']:
                cards_dealt = self.comp_panel.comp.get(rank, 0)
                if cards_dealt > 0:
                    # Convert rank to numeric
                    if rank == 'A':
                        card_val = 1
                    elif rank in ['T', 'J', 'Q', 'K']:
                        card_val = 10
                    else:
                        card_val = int(rank)

                    # Remove dealt cards from deck composition
                    for _ in range(cards_dealt):
                        deck_comp.remove_card(card_val)

            # Calculate EV using the basic engine
            result = self.engine.calculate_detailed_ev(
                numeric_hand, numeric_upcard, deck_comp, self.rules
            )

            # Convert engine result to our format
            formatted_result = {
                'success': True,
                'optimal_action': result.optimal_action,
                'optimal_ev': result.optimal_ev,
                'stand_ev': result.stand_ev,
                'hit_ev': result.hit_ev,
                'double_ev': result.double_ev,
                'split_ev': result.split_ev,
                'surrender_ev': result.surrender_ev,
                'variance': getattr(result, 'variance', 1.3),
                'insurance_ev': getattr(result, 'insurance_ev', -1.0),
                'composition_used': True
            }

            return formatted_result

        except Exception as e:
            print(f"EV_CALC: Fallback calculation failed: {e}")
            raise

    def _create_calculation_hash(self, player_hand, dealer_upcard):
        """NEW: Create a hash for caching EV calculations."""
        try:
            # Convert hand to hashable format
            hand_tuple = tuple(sorted([self._convert_card(card) for card in player_hand]))

            # Convert upcard
            upcard_val = self._convert_card(dealer_upcard)

            # Include composition state
            comp_items = tuple(sorted(self.comp_panel.comp.items()))

            return hash((hand_tuple, upcard_val, comp_items, self.comp_panel.decks))
        except:
            # If hashing fails, return None to disable caching
            return None

    def get_detailed_analysis(self, player_hand, dealer_upcard):
        """ENHANCED: Get comprehensive analysis with better error handling"""
        print("EV_CALC: get_detailed_analysis called")

        result = self.calculate_exact_ev(player_hand, dealer_upcard)

        if result.get('success', True):  # Default to success if not specified
            analysis = {
                'optimal_action': result.get('optimal_action', 'hit'),
                'optimal_ev': result.get('optimal_ev', -0.5),
                'actions': {
                    'stand': result.get('stand_ev', -0.5),
                    'hit': result.get('hit_ev', -0.4),
                    'double': result.get('double_ev', -1.0),
                    'split': result.get('split_ev', -1.0),
                    'surrender': result.get('surrender_ev', -0.5)
                },
                'variance': result.get('variance', 1.3),
                'insurance_ev': result.get('insurance_ev', -1.0),
                'composition_used': result.get('composition_used', True)
            }

            # Add decision quality info
            analysis['ev_difference'] = self._calculate_ev_differences(
                analysis['actions'],
                analysis['optimal_ev']
            )

            print(f"EV_CALC: Analysis complete - optimal: {analysis['optimal_action']}")
            return analysis
        else:
            error_msg = result.get('error', 'Unknown error')
            print(f"EV_CALC: Analysis failed - {error_msg}")
            return {'error': error_msg}

    def _convert_to_numeric(self, hand):
        """Convert card representations to numeric values"""
        numeric_hand = []
        for card in hand:
            # Handle both tuple format (rank, suit) and just rank
            if isinstance(card, tuple):
                numeric_hand.append(self._convert_card(card[0]))
            else:
                numeric_hand.append(self._convert_card(card))
        return numeric_hand

    def _convert_card(self, card):
        """Convert single card to numeric value"""
        if isinstance(card, int):
            return card

        # Handle tuple format (rank, suit) - extract just the rank
        if isinstance(card, tuple):
            card_str = str(card[0]).upper()  # Take only the rank part
        else:
            card_str = str(card).upper()

        if card_str in ['J', 'Q', 'K']:
            return 10
        elif card_str == 'A':
            return 1
        elif card_str in ['T', '10']:
            return 10
        else:
            try:
                return int(card_str)
            except ValueError:
                print(f"Warning: Could not convert card '{card}' to numeric value")
                return 10  # Default fallback

    def _calculate_ev_differences(self, actions, optimal_ev):
        """Calculate EV loss for each non-optimal action"""
        differences = {}
        for action, ev in actions.items():
            if ev >= -1.0:  # Valid action
                differences[action] = optimal_ev - ev
        return differences

    def get_dealer_probabilities(self, dealer_upcard):
        """ENHANCED: Get exact dealer outcome probabilities with composition awareness"""
        print("EV_CALC: get_dealer_probabilities called")

        try:
            numeric_upcard = self._convert_card(dealer_upcard)

            # **NEW: Use the enhanced dealer probability calculation**
            if hasattr(bjlogic_cpp, 'calculate_dealer_probabilities_dict'):
                # Get cards that have been removed from the deck
                removed_cards = []
                for rank in ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']:
                    cards_dealt = self.comp_panel.comp.get(rank, 0)
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
                    'num_decks': self.comp_panel.decks,
                    'dealer_hits_soft_17': self.rules.dealer_hits_soft_17,
                    'dealer_peek_on_ten': self.rules.dealer_peek_on_ten,
                    'surrender_allowed': self.rules.surrender_allowed,
                    'blackjack_payout': self.rules.blackjack_payout,
                    'double_after_split': self.rules.double_after_split,
                    'resplitting_allowed': self.rules.resplitting_allowed,
                    'max_split_hands': self.rules.max_split_hands
                }

                result = bjlogic_cpp.calculate_dealer_probabilities_dict(
                    self.engine,
                    numeric_upcard,
                    removed_cards,
                    rules_dict
                )

                return {
                    'bust': result.get('bust_prob', 0),
                    '17': result.get('total_17_prob', 0),
                    '18': result.get('total_18_prob', 0),
                    '19': result.get('total_19_prob', 0),
                    '20': result.get('total_20_prob', 0),
                    '21': result.get('total_21_prob', 0),
                    'blackjack': result.get('blackjack_prob', 0)
                }
            else:
                print("EV_CALC: Dealer probability function not available, using fallback")
                return self._get_dealer_probabilities_fallback(numeric_upcard)

        except Exception as e:
            print(f"EV_CALC: get_dealer_probabilities failed: {e}")
            # Return default probabilities
            return {
                'bust': 0.28,
                '17': 0.13,
                '18': 0.13,
                '19': 0.13,
                '20': 0.18,
                '21': 0.08,
                'blackjack': 0.05
            }

    def _get_dealer_probabilities_fallback(self, numeric_upcard):
        """Fallback dealer probabilities using basic engine."""
        try:
            # Create deck composition
            deck_comp = bjlogic_cpp.DeckComposition(self.comp_panel.decks)

            # Adjust for dealt cards
            for rank in ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']:
                cards_dealt = self.comp_panel.comp.get(rank, 0)
                if cards_dealt > 0:
                    if rank == 'A':
                        card_val = 1
                    elif rank in ['T', 'J', 'Q', 'K']:
                        card_val = 10
                    else:
                        card_val = int(rank)

                    for _ in range(cards_dealt):
                        deck_comp.remove_card(card_val)

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
        except:
            # Return reasonable defaults
            return {
                'bust': 0.28,
                '17': 0.13,
                '18': 0.13,
                '19': 0.13,
                '20': 0.18,
                '21': 0.08,
                'blackjack': 0.05
            }

    def clear_cache(self):
        """NEW: Clear the calculation cache to force recalculation."""
        print("EV_CALC: Clearing cache")
        self.last_calculation_hash = None
        self.cached_result = None

    def update_rules(self, **rule_updates):
        """NEW: Update game rules and clear cache."""
        print(f"EV_CALC: Updating rules: {rule_updates}")

        for rule_name, value in rule_updates.items():
            if hasattr(self.rules, rule_name):
                setattr(self.rules, rule_name, value)
                print(f"  Set {rule_name} = {value}")

        # Clear cache when rules change
        self.clear_cache()