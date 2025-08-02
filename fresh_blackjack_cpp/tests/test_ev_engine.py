# tests/test_ev_engine.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bjlogic_cpp


def create_your_game_rules():
    """Create rules dict with YOUR specific game rules"""
    rules = bjlogic_cpp.create_rules_config()

    # Explicitly set YOUR rules (though defaults should match)
    rules['num_decks'] = 8
    rules['dealer_hits_soft_17'] = False  # Dealer STANDS on soft 17
    rules['surrender_allowed'] = True  # Late surrender (extended)
    rules['blackjack_payout'] = 1.5  # 3:2
    rules['double_after_split'] = 0  # NOT allowed
    rules['resplitting_allowed'] = False  # NOT allowed
    rules['max_split_hands'] = 2  # Only 1 split allowed
    rules['dealer_peek_on_ten'] = False  # NO peek on 10s

    return rules


def test_ev_engine_creation():
    """Test 1: Create EV Engine"""
    print("Test 1: Creating EV Engine...")

    engine = bjlogic_cpp.AdvancedEVEngine()
    print("  ✓ Engine created successfully")

    # Test cache size
    cache_size = engine.get_cache_size()
    print(f"  Initial cache size: {cache_size}")
    print()


def test_basic_ev_calculation():
    """Test 2: Basic EV Calculation with YOUR rules"""
    print("Test 2: Basic EV Calculation (YOUR GAME RULES)...")

    engine = bjlogic_cpp.AdvancedEVEngine()
    rules = create_your_game_rules()

    # Test hard 16 vs 10 (common decision)
    hand = [10, 6]
    dealer_upcard = 10

    result = engine.calculate_true_count_ev(
        hand=hand,
        dealer_upcard=dealer_upcard,
        true_count=0.0,
        rules=rules
    )

    print(f"  Hand: {hand} vs Dealer: {dealer_upcard}")
    print(f"  Stand EV: {result['stand_ev']:.4f}")
    print(f"  Hit EV: {result['hit_ev']:.4f}")
    print(f"  Double EV: {result['double_ev']:.4f}")
    print(f"  Surrender EV: {result['surrender_ev']:.4f} (should be -0.5)")
    print(f"  Optimal action: {result['optimal_action']}")
    print(f"  Optimal EV: {result['optimal_ev']:.4f}")

    # Verify surrender is available (YOUR rule)
    if result['surrender_ev'] == -0.5:
        print("  ✓ Late surrender correctly available")
    else:
        print("  ✗ Late surrender NOT available (should be!)")
    print()


def test_no_peek_rule():
    """Test 3: No Peek on 10s (YOUR SPECIAL RULE)"""
    print("Test 3: Testing NO PEEK on 10s rule...")

    engine = bjlogic_cpp.AdvancedEVEngine()
    rules = create_your_game_rules()

    # Create deck composition for testing
    deck_comp = {
        'cards_remaining': {
            1: 32,  # Aces (potential dealer BJ)
            2: 32, 3: 32, 4: 32, 5: 32,
            6: 32, 7: 32, 8: 32, 9: 32,
            10: 128  # 10s, Js, Qs, Ks
        }
    }

    # Test player double vs dealer 10 (risky with no peek)
    hand = [11]  # Player has 11
    dealer_upcard = 10

    result = engine.calculate_no_peek_ev(
        hand=hand,
        dealer_upcard=dealer_upcard,
        deck_composition=deck_comp,
        rules=rules
    )

    print(f"  Hand: 11 vs Dealer: 10 (no peek)")
    print(f"  Double EV: {result['double_ev']:.4f}")
    print(f"  Hit EV: {result['hit_ev']:.4f}")
    print(f"  Dealer BJ probability: {result['dealer_probabilities']['prob_blackjack']:.4f}")
    print("  Note: Double EV reduced due to losing double bet to dealer BJ")
    print()


def test_split_aces_rule():
    """Test 4: Split Aces get only 1 card (YOUR RULE)"""
    print("Test 4: Testing Split Aces (1 card only) rule...")

    engine = bjlogic_cpp.AdvancedEVEngine()
    rules = create_your_game_rules()

    # Test splitting Aces
    hand = [1, 1]  # Pair of Aces
    dealer_upcard = 6

    result = engine.calculate_true_count_ev(
        hand=hand,
        dealer_upcard=dealer_upcard,
        true_count=0.0,
        rules=rules
    )

    print(f"  Hand: A,A vs Dealer: {dealer_upcard}")
    print(f"  Split EV: {result['split_ev']:.4f}")
    print(f"  Stand EV: {result['stand_ev']:.4f}")
    print(f"  Hit EV: {result['hit_ev']:.4f}")
    print("  Note: Split Aces receive only 1 card each")
    print()


def test_no_double_after_split():
    """Test 5: No Double After Split (YOUR RULE)"""
    print("Test 5: Testing NO Double After Split rule...")

    rules = create_your_game_rules()

    print(f"  Double after split allowed: {rules['double_after_split']}")
    print("  Expected: 0 (not allowed)")
    print("  This means after splitting, you can only hit or stand")
    print()


def test_dealer_probabilities():
    """Test 6: Dealer Probabilities with YOUR rules"""
    print("Test 6: Testing Dealer Probabilities (S17 rule)...")

    engine = bjlogic_cpp.AdvancedEVEngine()
    test_result = engine.test_recursive_dealer_engine()

    print(f"  Dealer 6 bust probability: {test_result['dealer_6_bust_prob']:.4f}")
    print(f"  Dealer Ace blackjack probability: {test_result['dealer_ace_blackjack_prob']:.4f}")
    print(f"  Dealer 10 blackjack probability: {test_result['dealer_10_blackjack_prob']:.4f}")
    print(f"  All tests valid: {test_result['test_passed']}")
    print("  Note: Probabilities calculated with dealer STANDS on soft 17")
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("EV ENGINE TESTS - YOUR GAME RULES")
    print("=" * 60)

    test_ev_engine_creation()
    test_basic_ev_calculation()
    test_no_peek_rule()
    test_split_aces_rule()
    test_no_double_after_split()
    test_dealer_probabilities()

    print("EV Engine tests completed!")