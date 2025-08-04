# tests/test_integration.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bjlogic_cpp


class MockCompPanel:
    """Mock comp_panel matching YOUR game (8 decks)"""

    def __init__(self):
        self.decks = 8  # YOUR game uses 8 decks
        self.comp = {
            'A': 0, '2': 0, '3': 0, '4': 0, '5': 0,
            '6': 0, '7': 0, '8': 0, '9': 0, 'T': 0,
            'J': 0, 'Q': 0, 'K': 0
        }

    def deal_card(self, card):
        """Simulate dealing a card"""
        if card in self.comp:
            self.comp[card] += 1


def create_your_game_rules():
    """Create rules matching YOUR specific game"""
    # Use the C++ RulesConfig object
    rules = bjlogic_cpp.RulesConfig()

    # YOUR specific rules
    rules.num_decks = 8
    rules.dealer_hits_soft_17 = False
    rules.surrender_allowed = True
    rules.blackjack_payout = 1.5
    rules.double_after_split = 0
    rules.resplitting_allowed = False
    rules.max_split_hands = 2
    rules.dealer_peek_on_ten = False

    return rules


def test_comp_panel_integration():
    """Test 1: comp_panel Integration with YOUR rules"""
    print("Test 1: Testing comp_panel integration (8-deck game)...")

    # Create mock comp_panel for 8-deck game
    comp_panel = MockCompPanel()

    # Simulate some cards dealt
    comp_panel.deal_card('T')  # Player 10
    comp_panel.deal_card('6')  # Player 6
    comp_panel.deal_card('T')  # Dealer 10

    rules = create_your_game_rules()

    # Test the integration
    hand = [10, 6]
    dealer_upcard = 10

    result = bjlogic_cpp.calculate_ev_from_comp_panel(
        hand=hand,
        dealer_upcard=dealer_upcard,
        comp_panel=comp_panel,
        rules=rules,
        counter_system="Hi-Lo"
    )

    if result['success']:
        print("  ✓ Integration successful!")
        print(f"  Optimal action: {result['optimal_action']}")
        print(f"  Optimal EV: {result['optimal_ev']:.4f}")
        print(f"  Stand EV: {result['stand_ev']:.4f}")
        print(f"  Hit EV: {result['hit_ev']:.4f}")
        print(f"  Surrender EV: {result['surrender_ev']:.4f}")

        # Verify surrender is available (YOUR rule)
        if result['surrender_ev'] == -0.5:
            print("  ✓ Late surrender correctly available")
    else:
        print(f"  ✗ Error: {result.get('error', 'Unknown error')}")
    print()


def test_penetration_effect():
    """Test 2: Penetration Effect (~50% YOUR game)"""
    print("Test 2: Testing penetration effect (YOUR ~50% penetration)...")

    # Test with different penetration levels
    cards_dealt_50_percent = int(8 * 52 * 0.5)  # ~208 cards
    cards_dealt_60_percent = int(8 * 52 * 0.6)  # ~250 cards

    print(f"  8-deck shoe total cards: {8 * 52} = 416")
    print(f"  50% penetration: ~{cards_dealt_50_percent} cards dealt")
    print(f"  60% penetration: ~{cards_dealt_60_percent} cards dealt")
    print("  YOUR game: typically 50%, sometimes up to 60%")
    print()


def test_special_scenarios():
    """Test 3: YOUR game special scenarios"""
    print("Test 3: Testing YOUR game special scenarios...")

    engine = bjlogic_cpp.AdvancedEVEngine()
    rules = create_your_game_rules()

    # Scenario 1: Late surrender with 3+ cards (YOUR special rule)
    print("\n  Scenario 1: Extended late surrender")
    hand = [5, 6, 5]  # 16 with 3 cards
    dealer_upcard = 10

    # Note: The C++ implementation might need modification to support
    # surrender with 3+ cards. Standard rules only allow 2-card surrender.
    print(f"    Hand: {hand} (total: 16) vs Dealer: {dealer_upcard}")
    print("    YOUR RULE: Can surrender even with 3 cards (if < 21)")
    print("    Standard rule: Can only surrender with first 2 cards")

    # Scenario 2: No peek loses double bet
    print("\n  Scenario 2: No peek on dealer 10")
    hand = [11]
    dealer_upcard = 10

    print(f"    Hand: 11 vs Dealer: 10")
    print("    YOUR RULE: If you double and dealer has BJ, you lose 2 bets")
    print("    Standard rule: Dealer would check first, you'd only lose 1 bet")

    # Scenario 3: Split 8s vs 10 (no DAS affects decision)
    print("\n  Scenario 3: Split 8s vs 10 (no DAS)")
    hand = [8, 8]
    dealer_upcard = 10

    result = engine.calculate_true_count_ev(hand, dealer_upcard, 0.0, rules)

    print(f"    Hand: 8,8 vs Dealer: 10")
    print(f"    Split EV: {result.split_ev:.4f}")
    print(f"    Surrender EV: {result.surrender_ev:.4f}")
    print("    Note: No double after split makes splitting less attractive")
    print()


def test_counting_with_your_rules():
    """Test 4: Card Counting with YOUR game parameters"""
    print("Test 4: Card counting in YOUR 8-deck game...")

    # Simulate cards from an 8-deck shoe
    cards = [10, 3, 6, 1, 5, 10, 10, 2, 4, 6]  # Some cards dealt

    result = bjlogic_cpp.process_cards_and_count(
        cards=cards,
        system="Hi-Lo",
        num_decks=8  # YOUR game
    )

    print(f"  Cards seen: {cards}")
    print(f"  Running count: {result['running_count']}")
    print(f"  True count: {result['true_count']:.2f}")
    print(f"  Cards seen: {len(cards)}")
    print(f"  Approximate penetration: {len(cards) / 416 * 100:.1f}%")

    # Insurance decision
    print(f"\n  Insurance decision:")
    print(f"    Should take insurance: {result['should_take_insurance']}")
    print(f"    Ten density: {result['ten_density']:.3f}")
    print()


def test_your_game_decisions():
    """Test 5: Common decisions in YOUR specific game"""
    print("Test 5: Testing common decisions with YOUR rules...")

    engine = bjlogic_cpp.AdvancedEVEngine()
    rules = create_your_game_rules()

    scenarios = [
        ([10, 6], 10, "16 vs 10 - Surrender available"),
        ([1, 1], 10, "A,A vs 10 - Split Aces (1 card only)"),
        ([11], 10, "11 vs 10 - Double (risky, no peek)"),
        ([8, 8], 1, "8,8 vs A - Split or surrender?"),
        ([9, 9], 7, "9,9 vs 7 - Stand (no DAS)"),
    ]

    for hand, dealer, desc in scenarios:
        print(f"\n  {desc}")
        print(f"  Hand: {hand} vs Dealer: {dealer}")

        # Use dict wrapper for easier access
        rules_dict = {
            'num_decks': 8,
            'dealer_hits_soft_17': False,
            'surrender_allowed': True,
            'blackjack_payout': 1.5,
            'double_after_split': 0,
            'resplitting_allowed': False,
            'max_split_hands': 2,
            'dealer_peek_on_ten': False
        }

        result = bjlogic_cpp.calculate_true_count_ev_dict(
            engine, hand, dealer, 0.0, rules_dict
        )

        print(f"    Optimal: {result['optimal_action']} (EV: {result['optimal_ev']:.4f})")
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("INTEGRATION TESTS - YOUR GAME CONFIGURATION")
    print("=" * 60)
    print("\nYOUR GAME RULES SUMMARY:")
    print("- 8 decks")
    print("- ~50% penetration (sometimes 60%)")
    print("- Dealer STANDS on soft 17")
    print("- NO peek on 10s")
    print("- Late surrender anytime (< 21)")
    print("- NO double after split")
    print("- NO resplitting")
    print("- Split Aces get 1 card only")
    print("=" * 60)

    test_comp_panel_integration()
    test_penetration_effect()
    test_special_scenarios()
    test_counting_with_your_rules()
    test_your_game_decisions()

    print("Integration tests completed!")