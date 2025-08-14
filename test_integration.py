#!/usr/bin/env python3
"""
test_integration.py - Test C++ integration with dealer probabilities and EV calculations
"""

import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_bjlogic_import():
    """Test if bjlogic_cpp module can be imported."""
    print("=" * 60)
    print("TESTING C++ MODULE IMPORT")
    print("=" * 60)

    try:
        import bjlogic_cpp
        print("✓ bjlogic_cpp module imported successfully")

        # List available functions
        functions = [x for x in dir(bjlogic_cpp) if not x.startswith('_')]
        print(f"✓ Available functions: {len(functions)}")
        for func in sorted(functions):
            print(f"  - {func}")

        return True
    except ImportError as e:
        print(f"✗ Failed to import bjlogic_cpp: {e}")
        print("\nPossible solutions:")
        print("1. Run: python setup.py build_ext --inplace")
        print("2. Check if compilation succeeded")
        print("3. Verify pybind11 is installed")
        return False


def test_dealer_probabilities():
    """Test dealer probability calculations."""
    print("\n" + "=" * 60)
    print("TESTING DEALER PROBABILITIES")
    print("=" * 60)

    try:
        import bjlogic_cpp

        # Test basic dealer probability calculation
        print("Testing dealer probability calculation...")

        # Create engine
        engine = bjlogic_cpp.AdvancedEVEngine()
        print("✓ Created AdvancedEVEngine")

        # Test parameters
        dealer_upcard = 10  # Dealer shows 10
        removed_cards = [1, 1, 10, 10]  # Some cards removed (2 Aces, 2 tens)

        rules_dict = {
            'num_decks': 8,
            'dealer_hits_soft_17': False,
            'dealer_peek_on_ten': False,
            'surrender_allowed': True,
            'blackjack_payout': 1.5,
            'double_after_split': 0,
            'resplitting_allowed': False,
            'max_split_hands': 2
        }

        print(f"Test scenario: Dealer upcard {dealer_upcard}, {len(removed_cards)} cards removed")

        # Test the function
        if hasattr(bjlogic_cpp, 'calculate_dealer_probabilities_dict'):
            result = bjlogic_cpp.calculate_dealer_probabilities_dict(
                engine, dealer_upcard, removed_cards, rules_dict
            )

            print("✓ Dealer probability calculation succeeded!")
            print("Results:")
            for key, value in result.items():
                print(f"  {key:>15}: {value:.5f}")

            # Verify probabilities sum to approximately 1
            total_prob = sum([
                result.get('total_17_prob', 0),
                result.get('total_18_prob', 0),
                result.get('total_19_prob', 0),
                result.get('total_20_prob', 0),
                result.get('total_21_prob', 0),
                result.get('blackjack_prob', 0),
                result.get('bust_prob', 0)
            ])

            print(f"\nProbability sum: {total_prob:.5f}")
            if abs(total_prob - 1.0) < 0.001:
                print("✓ Probabilities sum correctly to 1.0")
            else:
                print(f"⚠ Warning: Probabilities don't sum to 1.0 (diff: {abs(total_prob - 1.0):.5f})")

            return True
        else:
            print("✗ calculate_dealer_probabilities_dict function not found")
            print("Available dealer functions:")
            dealer_funcs = [x for x in dir(bjlogic_cpp) if 'dealer' in x.lower()]
            for func in dealer_funcs:
                print(f"  - {func}")
            return False

    except Exception as e:
        print(f"✗ Dealer probability test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ev_calculations():
    """Test EV calculations."""
    print("\n" + "=" * 60)
    print("TESTING EV CALCULATIONS")
    print("=" * 60)

    try:
        import bjlogic_cpp

        # Test if we have EV calculation functions
        print("Checking for EV calculation functions...")

        ev_functions = [x for x in dir(bjlogic_cpp) if 'ev' in x.lower()]
        if ev_functions:
            print("✓ Found EV functions:")
            for func in ev_functions:
                print(f"  - {func}")
        else:
            print("⚠ No EV functions found")

        # Try to create mock comp_panel for testing
        print("\nTesting with mock composition panel...")

        class MockCompPanel:
            def __init__(self):
                self.decks = 8
                self.comp = {
                    'A': 2, '2': 1, '3': 0, '4': 1, '5': 2,
                    '6': 1, '7': 0, '8': 1, '9': 0, 'T': 3,
                    'J': 1, 'Q': 2, 'K': 1
                }

        # Test EV calculation if function exists
        if hasattr(bjlogic_cpp, 'calculate_ev_from_comp_panel'):
            mock_comp = MockCompPanel()
            player_hand = [10, 6]  # Player has 16
            dealer_upcard = 10  # Dealer shows 10

            rules = bjlogic_cpp.RulesConfig()
            rules.num_decks = 8
            rules.dealer_hits_soft_17 = False
            rules.surrender_allowed = True
            rules.blackjack_payout = 1.5

            result = bjlogic_cpp.calculate_ev_from_comp_panel(
                hand=player_hand,
                dealer_upcard=dealer_upcard,
                comp_panel=mock_comp,
                rules=rules,
                counter_system="Hi-Lo"
            )

            print("✓ EV calculation succeeded!")
            print("Results:")
            for key, value in result.items():
                if isinstance(value, (int, float)):
                    print(f"  {key:>15}: {value:.5f}")
                else:
                    print(f"  {key:>15}: {value}")

            return True
        else:
            print("⚠ calculate_ev_from_comp_panel function not found")
            return False

    except Exception as e:
        print(f"✗ EV calculation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_comp_panel_integration():
    """Test integration with actual comp_panel if available."""
    print("\n" + "=" * 60)
    print("TESTING COMP_PANEL INTEGRATION")
    print("=" * 60)

    try:
        # Try to import and create a real comp_panel
        from ui.panels import CompPanel
        import tkinter as tk

        # Create a minimal tkinter environment
        root = tk.Tk()
        root.withdraw()  # Hide the window

        # Create comp_panel
        comp_panel = CompPanel(root, lambda: None, 8)

        # Add some test cards
        test_cards = ['A', 'A', '10', '10', 'K', '6', '5']
        for card in test_cards:
            comp_panel.add_card(card)

        print(f"✓ Created comp_panel with {len(test_cards)} test cards")
        print(f"  Composition: {dict(comp_panel.comp)}")

        # Test dealer probability calculation with real comp_panel
        if hasattr(bjlogic_cpp, 'calculate_dealer_probabilities_dict'):
            import bjlogic_cpp

            # Convert comp_panel data for C++
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

            engine = bjlogic_cpp.AdvancedEVEngine()
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

            # Test with dealer 10
            result = bjlogic_cpp.calculate_dealer_probabilities_dict(
                engine, 10, removed_cards, rules_dict
            )

            print("✓ Real comp_panel integration succeeded!")
            print("Dealer probabilities with current composition:")
            for key, value in result.items():
                print(f"  {key:>15}: {value:.5f}")

            root.destroy()
            return True
        else:
            print("⚠ Dealer probability function not available")
            root.destroy()
            return False

    except Exception as e:
        print(f"✗ Comp_panel integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all integration tests."""
    print("BLACKJACK C++ INTEGRATION TEST SUITE")
    print("=" * 60)

    tests = [
        ("C++ Module Import", test_bjlogic_import),
        ("Dealer Probabilities", test_dealer_probabilities),
        ("EV Calculations", test_ev_calculations),
        ("CompPanel Integration", test_comp_panel_integration),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = 0
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status:>8} - {test_name}")
        if success:
            passed += 1

    print(f"\nPassed: {passed}/{len(results)} tests")

    if passed == len(results):
        print("\n🎉 All tests passed! Your C++ integration is working correctly.")
        print("\nNext steps:")
        print("1. Run your main application")
        print("2. Press the 'Cal' button to test live integration")
        print("3. Deal some cards and watch probabilities update")
    else:
        print("\n⚠ Some tests failed. Check the errors above.")
        print("\nCommon fixes:")
        print("1. Rebuild the C++ extension: python setup.py build_ext --inplace")
        print("2. Check that all required C++ functions are exposed in bindings")
        print("3. Verify pybind11 installation")

    return passed == len(results)


if __name__ == "__main__":
    run_all_tests()