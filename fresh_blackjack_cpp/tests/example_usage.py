# example_usage.py
import bjlogic_cpp

import bjlogic_cpp


def create_your_game_rules():
    """YOUR specific game rules"""
    rules = bjlogic_cpp.create_rules_config()
    rules["num_decks"] = 8
    rules["dealer_hits_soft_17"] = False
    rules["surrender_allowed"] = True
    rules["blackjack_payout"] = 1.5
    rules["double_after_split"] = 0
    rules["resplitting_allowed"] = False
    rules["max_split_hands"] = 2
    rules["dealer_peek_on_ten"] = False
    return rules



def analyze_common_decisions():
    """Analyze common difficult decisions in YOUR game"""
    print("COMMON DECISIONS IN YOUR 8-DECK GAME")
    print("=" * 50)

    engine = bjlogic_cpp.AdvancedEVEngine()
    rules = create_your_game_rules()

    scenarios = [
        # (hand, dealer_upcard, description)
        ([10, 6], 10, "Hard 16 vs 10 - The classic dilemma"),
        ([1, 1], 10, "Pair of Aces vs 10 - Always split?"),
        ([8, 8], 10, "Pair of 8s vs 10 - Split or surrender?"),
        ([11], 10, "11 vs 10 - Double with no peek risk?"),
        ([10, 2], 3, "12 vs 3 - Hit or stand?"),
        ([9, 9], 7, "Pair of 9s vs 7 - Stand or split?"),
    ]

    for hand, dealer, desc in scenarios:
        print(f"\n{desc}")
        print(f"Hand: {hand} vs Dealer: {dealer}")
        print("-" * 40)

        # Get basic strategy
        basic = bjlogic_cpp.basic_strategy_decision(hand, dealer, rules)

        # Get detailed EVs
        result = engine.calculate_true_count_ev(hand, dealer, 0.0, rules)

        print(f"Basic Strategy: {basic}")
        print(f"EVs: Stand={result.stand_ev:.4f}, "
              f"Hit={result.hit_ev:.4f}, "
              f"Double={result.double_ev:.4f}, "
              f"Split={result.split_ev:.4f}, "
              f"Surrender={result.surrender_ev:.4f}")
        print(f"Best: {result.optimal_action} (EV: {result.optimal_ev:.4f})")


def test_extended_surrender():
    """Test YOUR unique extended surrender rule"""
    print("\n\nEXTENDED SURRENDER RULE TEST")
    print("=" * 50)
    print("YOUR RULE: Can surrender anytime with total < 21")
    print("(Standard rules only allow surrender on first 2 cards)")

    engine = bjlogic_cpp.AdvancedEVEngine()
    rules = create_your_game_rules()

    # Test with 3 cards
    hand = [5, 6, 5]  # 16 with 3 cards
    dealer_upcard = 10

    print(f"\nHand: {hand} (16 with 3 cards) vs Dealer: {dealer_upcard}")

    # Note: The C++ code might need modification to fully support
    # surrender with 3+ cards. This shows what it currently returns.
    result = engine.calculate_true_count_ev(hand, dealer_upcard, 0.0, rules)

    print(f"Surrender EV: {result.surrender_ev:.4f}")
    print("Note: Standard implementation may not support 3+ card surrender")
    print("You may need to modify the C++ code for this special rule")


def test_no_peek_impact():
    """Show impact of no peek on 10s rule"""
    print("\n\nNO PEEK ON 10s IMPACT")
    print("=" * 50)

    engine = bjlogic_cpp.AdvancedEVEngine()
    rules = create_your_game_rules()

    # Fresh 8-deck composition
    deck_comp = {
        'cards_remaining': {
            1: 32, 2: 32, 3: 32, 4: 32, 5: 32,
            6: 32, 7: 32, 8: 32, 9: 32, 10: 128
        }
    }

    hand = [11]  # 11 - normally great double
    dealer_upcard = 10

    result = engine.calculate_no_peek_ev(hand, dealer_upcard, deck_comp, rules)

    print(f"Hand: 11 vs Dealer: 10 (NO PEEK)")
    print(f"Dealer BJ probability: {result['dealer_probabilities']['prob_blackjack']:.4f}")
    print(f"Double EV: {result['double_ev']:.4f}")
    print(f"Hit EV: {result['hit_ev']:.4f}")
    print("\nImpact: Double EV is reduced because you lose 2 bets to dealer BJ")
    print("With peek, dealer would check first and you'd only lose 1 bet")


if __name__ == "__main__":
    analyze_common_decisions()
    test_extended_surrender()
    test_no_peek_impact()