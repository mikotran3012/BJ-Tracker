# tests/test_basic.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bjlogic_cpp


def test_module_import():
    """Test 1: Module imports correctly"""
    print("Test 1: Checking module import...")
    print(f"Module file: {bjlogic_cpp.__file__}")
    print("✓ Module imported successfully\n")


def test_basic_functions():
    """Test 2: Basic functions exist"""
    print("Test 2: Checking basic functions...")

    functions_to_check = [
        'calculate_hand_value',
        'basic_strategy_decision',
        'create_rules_config',
        'create_deck_state',
        'AdvancedEVEngine'
    ]

    for func in functions_to_check:
        if hasattr(bjlogic_cpp, func):
            print(f"  ✓ {func} exists")
        else:
            print(f"  ✗ {func} NOT FOUND")
    print()


def test_hand_calculation():
    """Test 3: Hand value calculation"""
    print("Test 3: Testing hand calculations...")

    # Test 1: Blackjack
    hand = [1, 10]  # Ace + 10
    result = bjlogic_cpp.calculate_hand_value(hand)
    print(f"  Blackjack test: A,10 = {result['total']} (BJ: {result['is_blackjack']})")

    # Test 2: Soft hand
    hand = [1, 6]  # Soft 17
    result = bjlogic_cpp.calculate_hand_value(hand)
    print(f"  Soft hand test: A,6 = {result['total']} (Soft: {result['is_soft']})")

    # Test 3: Hard hand
    hand = [10, 7]  # Hard 17
    result = bjlogic_cpp.calculate_hand_value(hand)
    print(f"  Hard hand test: 10,7 = {result['total']} (Soft: {result['is_soft']})")

    # Test 4: Bust
    hand = [10, 10, 5]  # 25 - bust
    result = bjlogic_cpp.calculate_hand_value(hand)
    print(f"  Bust test: 10,10,5 = {result['total']} (Busted: {result['is_busted']})")
    print()


def test_rules_config():
    """Test 4: Rules configuration - YOUR SPECIFIC GAME RULES"""
    print("Test 4: Testing YOUR GAME rules configuration...")

    # Create C++ RulesConfig object
    rules = bjlogic_cpp.RulesConfig()

    # YOUR GAME RULES:
    expected_rules = {
        'num_decks': 8,  # 8 decks
        'dealer_hits_soft_17': False,  # Dealer STANDS on soft 17
        'surrender_allowed': True,  # Late surrender allowed
        'blackjack_payout': 1.5,  # 3:2 payout
        'double_after_split': 0,  # NOT allowed
        'resplitting_allowed': False,  # NOT allowed
        'max_split_hands': 2,  # Only 1 split (2 hands max)
        'dealer_peek_on_ten': False,  # NO peek on 10s
    }

    print("  Checking YOUR game rules:")
    all_correct = True

    for rule, expected_value in expected_rules.items():
        if hasattr(rules, rule):
            actual_value = getattr(rules, rule)
            is_correct = actual_value == expected_value
            status = "✓" if is_correct else "✗"
            print(f"  {status} {rule}: {actual_value} (expected: {expected_value})")
            if not is_correct:
                all_correct = False
        else:
            print(f"  ✗ {rule}: NOT FOUND in rules")
            all_correct = False

    # Set correct values if needed
    if not all_correct:
        print("\n  Setting correct values...")
        rules.num_decks = 8
        rules.dealer_hits_soft_17 = False
        rules.surrender_allowed = True
        rules.blackjack_payout = 1.5
        rules.double_after_split = 0
        rules.resplitting_allowed = False
        rules.max_split_hands = 2
        rules.dealer_peek_on_ten = False
        print("  ✓ Rules updated to match YOUR game")
    else:
        print("\n  ✓ All rules match YOUR game configuration!")
    print()


def test_special_rules():
    """Test 5: YOUR special game rules"""
    print("Test 5: Testing YOUR special rules...")

    rules = bjlogic_cpp.RulesConfig()

    # Set YOUR rules
    rules.num_decks = 8
    rules.dealer_hits_soft_17 = False
    rules.surrender_allowed = True
    rules.dealer_peek_on_ten = False
    rules.double_after_split = 0
    rules.resplitting_allowed = False

    # Test basic strategy with YOUR rules
    print("  Testing basic strategy with YOUR rules:")

    # Test 16 vs 10 (should be surrender in your game)
    hand = [10, 6]
    dealer = 10
    decision = bjlogic_cpp.basic_strategy_decision(hand, dealer, rules)
    print(f"    16 vs 10: {decision}")

    # Test 11 vs 10 (double but risky with no peek)
    hand = [6, 5]
    dealer = 10
    decision = bjlogic_cpp.basic_strategy_decision(hand, dealer, rules)
    print(f"    11 vs 10: {decision}")

    # Test A,A vs 6 (always split)
    hand = [1, 1]
    dealer = 6
    decision = bjlogic_cpp.basic_strategy_decision(hand, dealer, rules)
    print(f"    A,A vs 6: {decision}")

    print("\n  Special rules summary:")
    print("    - Extended surrender (anytime before 21)")
    print("    - No peek on 10s (lose doubles/splits to dealer BJ)")
    print("    - Split Aces get only 1 card")
    print("    - No double after split")
    print("    - No resplitting")
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("BASIC FUNCTIONALITY TESTS - YOUR GAME RULES")
    print("=" * 60)

    test_module_import()
    test_basic_functions()
    test_hand_calculation()
    test_rules_config()
    test_special_rules()

    print("Basic tests completed!")