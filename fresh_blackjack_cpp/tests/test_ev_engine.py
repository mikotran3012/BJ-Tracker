# tests/test_ev_engine.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bjlogic_cpp


def create_your_game_rules():
    """Create rules object with YOUR specific game rules"""
    # Use the C++ RulesConfig class directly
    rules = bjlogic_cpp.RulesConfig()

    # Set YOUR specific rules
    rules.num_decks = 8
    rules.dealer_hits_soft_17 = False  # Dealer STANDS on soft 17
    rules.surrender_allowed = True  # Late surrender
    rules.blackjack_payout = 1.5  # 3:2
    rules.double_after_split = 0  # NOT allowed
    rules.resplitting_allowed = False  # NOT allowed
    rules.max_split_hands = 2  # Only 1 split allowed
    rules.dealer_peek_on_ten = False  # NO peek on 10s

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

    # Call with positional arguments
    result = engine.calculate_true_count_ev(hand, dealer_upcard, 0.0, rules)

    print(f"  Hand: {hand} vs Dealer: {dealer_upcard}")
    print(f"  Stand EV: {result.stand_ev:.4f}")
    print(f"  Hit EV: {result.hit_ev:.4f}")
    print(f"  Double EV: {result.double_ev:.4f}")
    print(f"  Surrender EV: {result.surrender_ev:.4f} (should be -0.5)")

    # Determine optimal action manually
    evs = {
        'stand': result.stand_ev,
        'hit': result.hit_ev,
        'double': result.double_ev,
        'surrender': result.surrender_ev
    }

    # Filter out invalid EVs (< -1.0)
    valid_evs = {k: v for k, v in evs.items() if v >= -1.0}
    optimal_action = max(valid_evs.items(), key=lambda x: x[1])

    print(f"  Optimal action: {optimal_action[0].upper()} (EV: {optimal_action[1]:.4f})")

    # Check available attributes
    print("\n  Available DetailedEV attributes:")
    for attr in dir(result):
        if not attr.startswith('_'):
            print(f"    - {attr}")

    # Verify surrender is available (YOUR rule)
    if result.surrender_ev == -0.5:
        print("\n  ✓ Late surrender correctly available")
    else:
        print("\n  ✗ Late surrender NOT available (should be!)")
    print()


def test_dict_wrapper():
    """Test 3: Test dict wrapper function"""
    print("Test 3: Testing dictionary wrapper function...")

    engine = bjlogic_cpp.AdvancedEVEngine()

    # Create rules as dict for the wrapper function
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

    hand = [10, 6]
    dealer_upcard = 10

    # Use the dict wrapper function
    result = bjlogic_cpp.calculate_true_count_ev_dict(engine, hand, dealer_upcard, 0.0, rules_dict)

    print(f"  Hand: {hand} vs Dealer: {dealer_upcard}")
    print(f"  Stand EV: {result['stand_ev']:.4f}")
    print(f"  Hit EV: {result['hit_ev']:.4f}")
    print(f"  Surrender EV: {result['surrender_ev']:.4f}")
    print(f"  Optimal action: {result['optimal_action']}")
    print()


def test_dealer_probabilities():
    """Test 4: Dealer Probabilities"""
    print("Test 4: Testing Dealer Probabilities...")

    engine = bjlogic_cpp.AdvancedEVEngine()
    rules = create_your_game_rules()

    # Create a fresh deck composition
    deck_comp = bjlogic_cpp.DeckComposition(8)  # 8 decks

    # Test dealer 6 (high bust probability)
    dealer_upcard = 6
    result = engine.calculate_dealer_probabilities_advanced(dealer_upcard, deck_comp, rules)

    print(f"  Dealer {dealer_upcard} probabilities:")
    print(f"    Bust: {result.bust_prob:.4f}")
    print(f"    17: {result.total_17_prob:.4f}")
    print(f"    18: {result.total_18_prob:.4f}")
    print(f"    19: {result.total_19_prob:.4f}")
    print(f"    20: {result.total_20_prob:.4f}")
    print(f"    21: {result.total_21_prob:.4f}")
    print(f"    BJ: {result.blackjack_prob:.4f}")

    # Verify probabilities sum to 1
    total = (result.bust_prob + result.total_17_prob + result.total_18_prob +
             result.total_19_prob + result.total_20_prob + result.total_21_prob)
    print(f"    Total probability: {total:.4f} (should be ~1.0)")
    print()


def test_recursive_methods():
    """Test 5: Recursive EV Methods"""
    print("Test 5: Testing Recursive EV Methods...")

    # Use the test function provided in bindings
    result = bjlogic_cpp.test_recursive_methods()

    if result['success']:
        print("  ✓ Recursive methods working correctly")
        print(f"    Test hand: {result['test_hand']} vs {result['dealer_upcard']}")
        print(f"    Stand EV: {result['stand_ev']:.4f}")
        print(f"    Hit EV: {result['hit_ev']:.4f}")
        print(f"    Double EV: {result['double_ev']:.4f}")
    else:
        print(f"  ✗ Error: {result['error']}")
    print()


def test_comp_panel_integration():
    """Test 6: comp_panel Integration"""
    print("Test 6: Testing comp_panel integration...")

    # Create a mock comp_panel
    class MockCompPanel:
        def __init__(self):
            self.decks = 8
            self.comp = {
                'A': 0, '2': 0, '3': 0, '4': 0, '5': 0,
                '6': 0, '7': 0, '8': 0, '9': 0, 'T': 0,
                'J': 0, 'Q': 0, 'K': 0
            }

    comp_panel = MockCompPanel()
    rules = create_your_game_rules()

    hand = [10, 6]
    dealer_upcard = 10

    result = bjlogic_cpp.calculate_ev_from_comp_panel(
        hand, dealer_upcard, comp_panel, rules, "Hi-Lo"
    )

    if result['success']:
        print("  ✓ comp_panel integration successful")
        print(f"    Optimal action: {result['optimal_action']}")
        print(f"    Optimal EV: {result['optimal_ev']:.4f}")
    else:
        print(f"  ✗ Error: {result.get('error', 'Unknown error')}")
    print()


def test_performance():
    """Test 7: Performance Benchmark"""
    print("Test 7: Performance benchmark...")

    # Use the benchmark function from bindings
    result = bjlogic_cpp.benchmark_recursive_methods(100)

    print(f"  Iterations: {result['num_tests']}")
    print(f"  Total time: {result['total_time_microseconds'] / 1000:.2f} ms")
    print(f"  Time per calculation: {result['average_time_microseconds']:.2f} μs")
    print(f"  Calculations per second: {result['calculations_per_second']:,.0f}")
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("EV ENGINE TESTS - YOUR GAME RULES")
    print("=" * 60)

    test_ev_engine_creation()
    test_basic_ev_calculation()
    test_dict_wrapper()
    test_dealer_probabilities()
    test_recursive_methods()
    test_comp_panel_integration()
    test_performance()

    print("EV Engine tests completed!")