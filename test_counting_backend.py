#!/usr/bin/env python3
"""
Enhanced test of counting backend with UAPC validation
"""

import sys
import os

# Add the current directory to Python path so it can find the counting module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from counting import CountManager


def test_basic_functionality():
    """Test basic counting functionality"""
    print("=== Basic Functionality Test ===")

    # Test basic functionality
    manager = CountManager(decks=8)
    print(f"Initialized: {manager}")

    # Add some cards
    cards = ['A', 'K', '5', '6', '2']
    for card in cards:
        manager.add_card(card)
        print(f"Added {card}")

    # Get counts
    cards_left = 400  # Example
    aces_left = 30  # Example
    counts = manager.get_counts(cards_left, aces_left, 8)

    print("\nCurrent counts:")
    for name, rc, tc in counts:
        print(f"{name}: RC={rc}, TC={tc}")

    print("✓ Basic functionality test completed successfully!")
    return True


def test_uapc_validation():
    """Test the corrected UAPC calculation with the provided validation case."""
    print("\n" + "=" * 50)
    print("=== UAPC Validation Test ===")

    # Import the updated UAPC system
    try:
        from counting.uapc import UAPCSystem
    except ImportError as e:
        print(f"Error importing UAPCSystem: {e}")
        return False

    # Test Case from Requirements:
    # - runningCount = 18
    # - acesSeen = 10
    # - remainingDecks = 3.0
    # - totalDecks = 8
    # Expected: (18 + ((32-10) - 12)) / 6 = (18 + 10) / 6 = 4.67

    print("\nTest Case Parameters:")
    running_count = 18
    aces_seen = 10
    remaining_decks = 3.0
    total_decks = 8

    print(f"Running Count: {running_count}")
    print(f"Aces Seen: {aces_seen}")
    print(f"Remaining Decks: {remaining_decks}")
    print(f"Total Decks: {total_decks}")

    # Create UAPC system instance
    uapc = UAPCSystem(total_decks)

    # Use the validation method to test the calculation
    result = uapc.validate_calculation(running_count, aces_seen, remaining_decks, total_decks)

    print("\nCalculation Steps:")
    aces_remaining = (total_decks * 4) - aces_seen
    expected_aces = 4 * remaining_decks
    ace_adjustment = aces_remaining - expected_aces
    adjusted_rc = running_count + ace_adjustment
    remaining_half_decks = remaining_decks * 2

    print(f"1. Aces Remaining = ({total_decks} × 4) - {aces_seen} = {aces_remaining}")
    print(f"2. Expected Aces = 4 × {remaining_decks} = {expected_aces}")
    print(f"3. Ace Adjustment = {aces_remaining} - {expected_aces} = {ace_adjustment}")
    print(f"4. Adjusted RC = {running_count} + {ace_adjustment} = {adjusted_rc}")
    print(f"5. Remaining Half-Decks = {remaining_decks} × 2 = {remaining_half_decks}")
    print(f"6. True Count = {adjusted_rc} ÷ {remaining_half_decks} = {result}")

    expected_result = 4.67
    print(f"\nExpected Result: {expected_result}")
    print(f"Actual Result: {result}")

    success = abs(result - expected_result) < 0.01
    print(f"Match: {'✓ PASS' if success else '✗ FAIL'}")

    return success


def test_uapc_integration():
    """Test UAPC integration with CountManager"""
    print("\n" + "=" * 50)
    print("=== UAPC Integration Test ===")

    try:
        manager = CountManager(decks=8)

        # Get the UAPC system specifically
        uapc_system = manager.get_system_by_name("UAPC")
        if not uapc_system:
            print("✗ UAPC system not found in CountManager")
            return False

        print(f"Found UAPC system: {uapc_system.name}")

        # Simulate dealing some cards including aces
        test_cards = ['A', 'K', '5', '6', '2', 'A', '10', '7']

        print(f"Dealing cards: {test_cards}")
        for card in test_cards:
            manager.add_card(card)

        # Get counts from manager
        cards_left = 8 * 52 - len(test_cards)
        aces_left = 8 * 4 - 2  # We dealt 2 aces

        counts = manager.get_counts(cards_left, aces_left, 8)

        print(f"\nAfter dealing {len(test_cards)} cards:")
        for name, rc, tc in counts:
            print(f"{name}: RC={rc}, TC={tc}")

        # Verify UAPC ace tracking
        print(f"\nUAPC Internal Ace Tracking: {uapc_system.aces_seen}")
        print(f"Expected Aces Seen: 2")

        ace_tracking_correct = uapc_system.aces_seen == 2
        print(f"Ace Tracking: {'✓ PASS' if ace_tracking_correct else '✗ FAIL'}")

        print("✓ UAPC integration test completed")
        return ace_tracking_correct

    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False


def test_uapc_edge_cases():
    """Test UAPC edge cases"""
    print("\n" + "=" * 50)
    print("=== UAPC Edge Cases Test ===")

    try:
        from counting.uapc import UAPCSystem
    except ImportError as e:
        print(f"Error importing UAPCSystem: {e}")
        return False

    uapc = UAPCSystem(decks=8)

    # Test 1: Division by zero protection
    print("\nTest 1: Division by zero protection")
    result = uapc.validate_calculation(10, 5, 0.0, 8)  # 0 remaining decks
    print(f"Result with 0 remaining decks: {result}")
    test1_pass = result == 0.0
    print(f"Should be 0: {'✓ PASS' if test1_pass else '✗ FAIL'}")

    # Test 2: Reset functionality
    print("\nTest 2: Reset functionality")
    uapc.add_card('A')
    uapc.add_card('A')
    print(f"Before reset - RC: {uapc.running_count}, Aces: {uapc.aces_seen}")
    uapc.reset()
    print(f"After reset - RC: {uapc.running_count}, Aces: {uapc.aces_seen}")
    test2_pass = uapc.running_count == 0 and uapc.aces_seen == 0
    print(f"Reset successful: {'✓ PASS' if test2_pass else '✗ FAIL'}")

    # Test 3: Undo functionality
    print("\nTest 3: Undo functionality")
    uapc.add_card('A')
    uapc.add_card('K')
    print(f"After adding A, K - RC: {uapc.running_count}, Aces: {uapc.aces_seen}")
    uapc.remove_card('A')
    print(f"After removing A - RC: {uapc.running_count}, Aces: {uapc.aces_seen}")
    test3_pass = uapc.running_count == -3 and uapc.aces_seen == 0  # Only K should remain
    print(f"Undo successful: {'✓ PASS' if test3_pass else '✗ FAIL'}")

    all_passed = test1_pass and test2_pass and test3_pass
    print(f"\nEdge cases test: {'✓ ALL PASSED' if all_passed else '✗ SOME FAILED'}")
    return all_passed


def main():
    """Run all counting backend tests including UAPC validation"""
    print("Enhanced Counting Backend Test Suite")
    print("=" * 60)

    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("UAPC Validation", test_uapc_validation),
        ("UAPC Integration", test_uapc_integration),
        ("UAPC Edge Cases", test_uapc_edge_cases)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n{test_name}: ✓ PASSED")
            else:
                print(f"\n{test_name}: ✗ FAILED")
        except Exception as e:
            print(f"\n{test_name}: ✗ ERROR - {e}")

    print("\n" + "=" * 60)
    print(f"FINAL RESULTS: {passed}/{total} tests passed")

    if passed == total:
        print("✓ ALL TESTS PASSED - Counting backend is working correctly!")
        return True
    else:
        print("✗ SOME TESTS FAILED - Please check the implementation")
        return False


if __name__ == "__main__":
    success = main()
    print("\nBackend test completed!")
    sys.exit(0 if success else 1)