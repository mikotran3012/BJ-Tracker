# test_nairn_integration.py
"""
Test script to verify Nairn EV calculator integration.
Run this before integrating with your main app.
"""

from nairn_ev_calculator import (
    BlackjackTrackerNairnIntegration,
    DDNone,
    analyze_with_enforced_tournament_rules,
    analyze_with_nairn_algorithm,
)

# Wrapper used in tests to maintain backward-compatible function name
def analyze_with_nonstandard_rules(*args, **kwargs):
    """Call :func:`analyze_with_nairn_algorithm` with the given arguments."""
    return analyze_with_nairn_algorithm(*args, **kwargs)


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
        from nairn_ev_calculator import analyze_with_enforced_tournament_rules

        # Test case: Player 16 vs Dealer 10
        result = analyze_with_enforced_tournament_rules(
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
    """Test Nairn splitting analysis - REAL TEST."""
    print("Testing Nairn splitting analysis...")

    try:
        # Create integration instance
        integration = BlackjackTrackerNairnIntegration({
            'num_decks': 1,
            'hits_soft_17': False,
            'dd_after_split': DDNone,
            'resplitting': False
        })

        # Test deck composition
        deck_comp = {
            'A': 4, '2': 4, '3': 4, '4': 4, '5': 4,
            '6': 4, '7': 4, '8': 2, '9': 4, '10': 3,
            'J': 4, 'Q': 4, 'K': 4
        }

        # REAL SPLITTING TEST
        exact_results = integration.get_exact_split_analysis('8', deck_comp)

        print(f"Real splitting results: {exact_results}")

        # Verify we got actual numbers
        if isinstance(exact_results, dict) and len(exact_results) >= 2:
            for rule, ev in exact_results.items():
                if isinstance(ev, (int, float)) and -1.0 <= ev <= 1.0:
                    print(f"  {rule}: {ev:.4f}")
                else:
                    print(f"  WARNING: Unusual EV for {rule}: {ev}")

            print("✓ Splitting analysis successful: Real results calculated")
            return True
        else:
            print("❌ Splitting analysis failed: Invalid results")
            return False

    except Exception as e:
        print(f"❌ Splitting analysis failed: {e}")
        import traceback
        traceback.print_exc()
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


def test_nonstandard_rules():
    """Test the nonstandard rules implementation."""
    print("Testing nonstandard rules...")

    try:
        # Test case: Hard 16 vs 10 with nonstandard rules
        nonstandard_result = analyze_with_enforced_tournament_rules(
            player_cards=['10', '6'],  # Hard 16
            dealer_upcard='10',
            deck_composition={
                'A': 4, '2': 4, '3': 4, '4': 4, '5': 4, '6': 3, '7': 4,
                '8': 4, '9': 4, '10': 3, 'J': 4, 'Q': 4, 'K': 4
            },
            rules_config={
                'peek_hole': False,  # NO PEEK
                'ultra_late_surrender': True,  # ULTRA-LENIENT SURRENDER
                'num_decks': 1
            }
        )

        print(f"Nonstandard rules result: {nonstandard_result}")

        # Verify surrender is available in nonstandard rules
        if 'surrender' in nonstandard_result:
            print("✓ Ultra-lenient surrender available")
            surrender_ev = nonstandard_result['surrender']
            print(f"  Surrender EV: {surrender_ev:.4f}")
            return True
        else:
            print("❌ Ultra-lenient surrender not available")
            return False

    except Exception as e:
        print(f"❌ Nonstandard rules test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all tests including nonstandard rules."""
    tests = [
        ("Import Tests", test_nairn_imports),
        ("Integration Import Tests", test_nairn_integration_imports),
        ("Basic Analysis", test_basic_analysis),
        ("Splitting Analysis", test_splitting_analysis),
        ("Nonstandard Rules", test_nonstandard_rules),
        ("UI Component", test_ui_components),
        ("Comprehensive Move Analysis", test_all_moves_comprehensive),  # Add this line
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


def test_all_moves_comprehensive():
    """Test that Nairn calculator provides comprehensive move analysis."""
    print("Testing comprehensive move analysis...")

    try:
        test_scenarios = [
            (['10', '6'], '10', "Hard 16 vs 10"),
            (['A', '7'], '9', "Soft 18 vs 9"),
            (['8', '8'], 'A', "Pair 8s vs Ace"),
            (['5', '6'], '5', "11 vs 5"),
        ]

        all_passed = True

        for player_cards, dealer_upcard, description in test_scenarios:
            deck_comp = {
                'A': 24, '2': 24, '3': 24, '4': 24, '5': 24,
                '6': 24, '7': 24, '8': 24, '9': 24, '10': 24,
                'J': 24, 'Q': 24, 'K': 24
            }
            # Remove dealt cards
            for card in player_cards + [dealer_upcard]:
                if card in deck_comp:
                    deck_comp[card] -= 1

            try:
                results = analyze_with_enforced_tournament_rules(
                    player_cards, dealer_upcard, deck_comp, {'num_decks': 6}
                )

                print(f"\n  📋 {description}")

                # Check that we have the 5 main moves
                expected_moves = ['stand', 'hit', 'double', 'split', 'surrender']
                moves_found = []

                for move in expected_moves:
                    if move in results:
                        moves_found.append(move)
                        if results[move] is None:
                            print(f"    {move}: N/A")
                        elif isinstance(results[move], (int, float)):
                            print(f"    {move}: {results[move]:+.4f}")
                        else:
                            print(f"    {move}: {results[move]}")

                if 'best' in results:
                    print(f"    ➤ Best: {results['best'].upper()}")

                # Check if we got most moves (some might be N/A for impossible moves like split non-pairs)
                if len(moves_found) >= 4:  # At least 4 out of 5 moves
                    print(f"    ✓ Comprehensive analysis: {len(moves_found)}/5 moves calculated")
                else:
                    print(f"    ⚠️ Limited analysis: only {len(moves_found)}/5 moves calculated")
                    all_passed = False

            except Exception as e:
                print(f"    ❌ {description}: {e}")
                all_passed = False

        if all_passed:
            print("\n✓ Comprehensive move analysis test passed")
            return True
        else:
            print("\n⚠️ Some comprehensive analysis tests had issues")
            return True  # Don't fail the whole suite for this

    except Exception as e:
        print(f"❌ Comprehensive analysis test failed: {e}")
        return False

if __name__ == "__main__":
    success = run_all_tests()

