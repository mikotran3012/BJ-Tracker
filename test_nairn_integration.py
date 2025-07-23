# test_nairn_integration.py
"""
Test script to verify Nairn EV calculator integration.
Run this before integrating with your main app.
"""

import sys
import os


def test_nairn_imports():
    """Test that all Nairn modules can be imported."""
    print("Testing Nairn EV Calculator imports...")

    try:
        from nairn_ev_calculator import (
            analyze_with_nairn_algorithm,
            BlackjackTrackerNairnIntegration,
            NairnEVCalculator,
            create_nairn_calculator
        )
        print("✓ Core Nairn modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import Nairn modules: {e}")
        return False


def test_nairn_integration_imports():
    """Test that integration module can be imported."""
    print("Testing Nairn integration imports...")

    try:
        from nairn_integration import (
            integrate_nairn_with_app,
            NairnEVPanel,
            NairnUpdateHandler
        )
        print("✓ Nairn integration modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import Nairn integration: {e}")
        return False


def test_basic_analysis():
    """Test basic EV analysis functionality."""
    print("Testing basic Nairn analysis...")

    try:
        from nairn_ev_calculator import analyze_with_nairn_algorithm

        # Test case: Player 16 vs Dealer 10
        result = analyze_with_nairn_algorithm(
            player_cards=['10', '6'],
            dealer_upcard='10',
            deck_composition={
                'A': 24, '2': 24, '3': 24, '4': 24, '5': 24,
                '6': 23, '7': 24, '8': 24, '9': 24, '10': 93,
                'J': 24, 'Q': 24, 'K': 24
            },
            rules_config={'num_decks': 6}
        )

        if 'best' in result and 'best_ev' in result:
            print(f"✓ Basic analysis successful: {result['best']} (EV: {result['best_ev']:.4f})")
            return True
        else:
            print("✗ Basic analysis failed: Invalid result format")
            return False

    except Exception as e:
        print(f"✗ Basic analysis failed: {e}")
        return False


def test_splitting_analysis():
    """Test splitting analysis functionality."""
    print("Testing Nairn splitting analysis...")

    try:
        from nairn_ev_calculator import BlackjackTrackerNairnIntegration

        rules_config = {
            'num_decks': 6,
            'hits_soft_17': False,
            'resplitting': True
        }

        integration = BlackjackTrackerNairnIntegration(rules_config)

        # Test splitting for 8,8 vs A
        deck_comp = {
            'A': 23, '2': 24, '3': 24, '4': 24, '5': 24,
            '6': 24, '7': 24, '8': 22, '9': 24, '10': 96,
            'J': 24, 'Q': 24, 'K': 24
        }

        exact_results = integration.get_exact_split_analysis('8', deck_comp)

        if exact_results and len(exact_results) > 0:
            print(f"✓ Splitting analysis successful: {len(exact_results)} scenarios calculated")
            return True
        else:
            print("✗ Splitting analysis failed: No results")
            return False

    except Exception as e:
        print(f"✗ Splitting analysis failed: {e}")
        return False


def test_ui_components():
    """Test that UI components can be created (without displaying)."""
    print("Testing UI component creation...")

    try:
        import tkinter as tk
        from nairn_integration import NairnEVPanel

        # Create minimal test app structure
        class MockApp:
            def __init__(self):
                self.num_decks = 6
                self.hits_soft_17 = False
                self.resplitting_allowed = False
                self.resplit_aces = False
                self.blackjack_payout = 1.5

        root = tk.Tk()
        root.withdraw()  # Hide the window

        mock_app = MockApp()
        frame = tk.Frame(root)

        # Test panel creation
        nairn_panel = NairnEVPanel(frame, mock_app)
        panel_widget = nairn_panel.create_panel()

        if panel_widget:
            print("✓ UI components created successfully")
            root.destroy()
            return True
        else:
            print("✗ UI component creation failed")
            root.destroy()
            return False

    except Exception as e:
        print(f"✗ UI component test failed: {e}")
        return False


def run_all_tests():
    """Run all integration tests."""
    print("=" * 60)
    print("NAIRN EV CALCULATOR INTEGRATION TESTS")
    print("=" * 60)

    tests = [
        ("Import Tests", test_nairn_imports),
        ("Integration Import Tests", test_nairn_integration_imports),
        ("Basic Analysis Test", test_basic_analysis),
        ("Splitting Analysis Test", test_splitting_analysis),
        ("UI Component Test", test_ui_components)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("\n🎉 All tests passed! Nairn integration is ready.")
        print("\nNext steps:")
        print("1. Add the integration code to your main app")
        print("2. Run your app to see the Nairn EV panel")
        print("3. Deal some cards to test real-time analysis")
    else:
        print(f"\n⚠️  {len(results) - passed} tests failed. Check the errors above.")
        print("\nTroubleshooting:")
        print("1. Make sure all files are in the correct directory")
        print("2. Check for missing dependencies (tkinter should be built-in)")
        print("3. Verify file permissions")

    return passed == len(results)


if __name__ == "__main__":
    success = run_all_tests()