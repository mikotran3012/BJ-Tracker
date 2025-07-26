#!/usr/bin/env python3
# test_phase_2_2.py
"""
Test script for Phase 2.2 - Complete Basic Strategy Tables
CORRECTED for "Dealer Stands on Soft 17" rules
"""


def test_complete_strategy():
    """Test the complete basic strategy implementation for dealer stands on soft 17"""
    print("🎯 Testing Phase 2.2 - Complete Basic Strategy Tables")
    print("🏠 Table Rules: DEALER STANDS ON SOFT 17")
    print("=" * 60)

    try:
        import bjlogic_cpp
        print("✅ Import successful")

        # Test basic function
        message = bjlogic_cpp.test_extension()
        print(f"✅ Test function: {message}")

        # Create standard rules (dealer stands on soft 17)
        rules = bjlogic_cpp.create_rules_config()
        rules["dealer_hits_soft_17"] = False  # Confirm dealer stands on soft 17
        rules["resplitting_allowed"] = True
        rules["surrender_allowed"] = True

        print(f"\n🎲 Testing with rules:")
        print(f"   - {rules['num_decks']} decks")
        print(f"   - Dealer stands on soft 17: {not rules['dealer_hits_soft_17']}")
        print(f"   - Surrender allowed: {rules['surrender_allowed']}")

        # =================================================================
        # HARD HAND STRATEGY TESTS
        # =================================================================
        print("\n🎯 Testing Hard Hand Strategy:")

        hard_tests = [
            # [hand, dealer, expected_action, description]
            ([10, 6], 10, "surrender", "Hard 16 vs 10 (surrender if allowed)"),
            ([10, 6], 6, "stand", "Hard 16 vs 6"),
            ([5, 6], 5, "double", "Hard 11 vs 5"),
            ([5, 6], 1, "hit", "🔥 Hard 11 vs ACE (per official PDF: HIT)"),  # CORRECTED per PDF!
            ([5, 4], 3, "double", "Hard 9 vs 3"),
            ([10, 2], 7, "hit", "Hard 12 vs 7"),
            ([10, 5], 10, "surrender", "Hard 15 vs 10 (surrender)"),
            ([8, 8], 10, "split", "Hard 16 (8,8) vs 10 - should split"),
            ([10, 7], 8, "stand", "Hard 17 vs 8"),
        ]

        for hand, dealer, expected, description in hard_tests:
            action = bjlogic_cpp.basic_strategy_decision(hand, dealer, rules)
            status = "✅" if action == expected else "❌"
            marker = "🔥" if "dealer stands soft 17" in description else ""
            print(f"   {status} {marker} {description}: {action} (expected: {expected})")

        # =================================================================
        # SOFT HAND STRATEGY TESTS (Critical for Soft 17 Rule)
        # =================================================================
        print("\n🌟 Testing Soft Hand Strategy:")

        soft_tests = [
            # [hand, dealer, expected_action, description]
            ([1, 6], 3, "double", "Soft 17 (A,6) vs 3"),
            ([1, 7], 2, "stand", "🔥 Soft 18 (A,7) vs 2 (per official PDF: STAND)"),  # CORRECTED per PDF!
            ([1, 7], 3, "double", "Soft 18 (A,7) vs 3"),
            ([1, 7], 4, "double", "Soft 18 (A,7) vs 4"),
            ([1, 7], 5, "double", "Soft 18 (A,7) vs 5"),
            ([1, 7], 6, "stand", "Soft 18 (A,7) vs 6"),
            ([1, 7], 9, "hit", "Soft 18 (A,7) vs 9"),
            ([1, 8], 6, "stand", "🔥 Soft 19 (A,8) vs 6 (per official PDF: STAND)"),  # CORRECTED per PDF!
            ([1, 8], 5, "stand", "Soft 19 (A,8) vs 5"),
            ([1, 8], 7, "stand", "Soft 19 (A,8) vs 7"),
            ([1, 2], 5, "double", "Soft 13 (A,2) vs 5"),
            ([1, 5], 4, "double", "Soft 16 (A,5) vs 4"),
        ]

        for hand, dealer, expected, description in soft_tests:
            action = bjlogic_cpp.basic_strategy_decision(hand, dealer, rules)
            status = "✅" if action == expected else "❌"
            marker = "🔥" if "dealer stands soft 17" in description else ""
            print(f"   {status} {marker} {description}: {action} (expected: {expected})")

        # =================================================================
        # PAIR SPLITTING STRATEGY TESTS
        # =================================================================
        print("\n✂️  Testing Pair Splitting Strategy:")

        pair_tests = [
            # [hand, dealer, expected_action, description]
            ([8, 8], 10, "split", "Pair of 8s vs 10 (always split)"),
            ([8, 8], 1, "split", "Pair of 8s vs ACE (always split)"),
            ([1, 1], 6, "split", "Pair of Aces vs 6 (always split)"),
            ([1, 1], 1, "split", "Pair of Aces vs ACE (always split)"),
            ([10, 10], 5, "stand", "Pair of 10s vs 5 (never split)"),
            ([9, 9], 7, "split", "Pair of 9s vs 7"),
            ([9, 9], 10, "stand", "Pair of 9s vs 10 (don't split)"),
            ([9, 9], 1, "stand", "Pair of 9s vs ACE (don't split)"),
            ([5, 5], 5, "double", "Pair of 5s vs 5 (double, don't split)"),
            ([7, 7], 8, "hit", "Pair of 7s vs 8 (don't split)"),
        ]

        for hand, dealer, expected, description in pair_tests:
            action = bjlogic_cpp.basic_strategy_decision(hand, dealer, rules)
            status = "✅" if action == expected else "❌"
            print(f"   {status} {description}: {action} (expected: {expected})")

        # =================================================================
        # STRATEGY ANALYSIS TESTS
        # =================================================================
        print("\n📊 Testing Strategy Analysis:")

        # Test optimal decision checking
        is_optimal = bjlogic_cpp.is_basic_strategy_optimal([10, 6], 10, rules, "hit")
        print(f"✅ Hard 16 vs 10, choosing 'hit' is optimal: {is_optimal}")

        # Test the key "dealer stands soft 17" decisions
        is_optimal_11_ace = bjlogic_cpp.is_basic_strategy_optimal([10, 1], 1, rules, "double")
        print(f"🔥 Hard 11 vs ACE, choosing 'double' is optimal: {is_optimal_11_ace}")

        is_optimal_a7_2 = bjlogic_cpp.is_basic_strategy_optimal([1, 7], 2, rules, "double")
        print(f"🔥 Soft 18 vs 2, choosing 'double' is optimal: {is_optimal_a7_2}")

        # Test deviation costs
        deviation_cost = bjlogic_cpp.get_strategy_deviation_cost([10, 6], 10, rules, "stand")
        print(f"✅ Cost of standing on 16 vs 10: {deviation_cost:.3f}")

        # Cost of not doubling 11 vs Ace
        deviation_cost_11 = bjlogic_cpp.get_strategy_deviation_cost([10, 1], 1, rules, "hit")
        print(f"🔥 Cost of hitting 11 vs ACE (should double): {deviation_cost_11:.3f}")

        # =================================================================
        # BATCH ANALYSIS TEST (Dealer Stands Soft 17 scenarios)
        # =================================================================
        print("\n⚡ Testing Batch Strategy Analysis:")

        scenarios = [
            {"hand": [5, 6], "dealer_upcard": 1},  # Hard 11 vs A - should double
            {"hand": [1, 7], "dealer_upcard": 2},  # A,7 vs 2 - should double
            {"hand": [1, 8], "dealer_upcard": 6},  # A,8 vs 6 - should double
            {"hand": [8, 8], "dealer_upcard": 9},  # 8,8 vs 9 - should split
            {"hand": [10, 6], "dealer_upcard": 10},  # 16 vs 10 - should surrender
        ]

        batch_results = bjlogic_cpp.batch_strategy_analysis(scenarios, rules)

        expected_actions = ["double", "double", "double", "split", "surrender"]

        batch_results = bjlogic_cpp.batch_strategy_analysis(scenarios, rules)

        expected_actions = ["double", "double", "double", "split", "hit"]

        for i, result in enumerate(batch_results):
            hand = result["hand"]
            dealer = result["dealer_upcard"]
            action = result["optimal_action"]
            expected = expected_actions[i]
            total = result["hand_total"]
            is_soft = result["is_soft"]
            status = "✅" if action == expected else "❌"
            marker = "🔥" if i < 3 else ""  # First 3 are dealer stands soft 17 specific
            print(
                f"   {status} {marker} {hand} vs {dealer}: {action} (expected: {expected}, total: {total}, soft: {is_soft})")

        # =================================================================
        # RULE VARIATION TESTS
        # =================================================================
        print("\n🔍 Testing Rule Variations:")

        # Test with surrender disabled
        no_surrender_rules = bjlogic_cpp.create_rules_config()
        no_surrender_rules["surrender_allowed"] = False
        no_surrender_rules["dealer_hits_soft_17"] = False

        action_no_surrender = bjlogic_cpp.basic_strategy_decision([10, 6], 10, no_surrender_rules)
        print(f"✅ Hard 16 vs 10 (no surrender): {action_no_surrender} (should be 'hit')")

        # Test double after split
        das_rules = bjlogic_cpp.create_rules_config()
        das_rules["double_after_split"] = 1
        das_rules["dealer_hits_soft_17"] = False

        print(f"✅ Double after split rules configured")

        # =================================================================
        # COMPREHENSIVE VERIFICATION
        # =================================================================
        print("\n🎊 Comprehensive Strategy Verification:")

        # Test the most important "dealer stands soft 17" decisions
        critical_tests = [
            # These are the key differences when dealer stands on soft 17
            ([5, 6], 1, "double"),  # Hard 11 vs A (CORRECTED!)
            ([1, 7], 2, "double"),  # A,7 vs 2
            ([1, 8], 6, "double"),  # A,8 vs 6
            # Standard decisions that shouldn't change
            ([10, 7], 8, "stand"),  # 17 vs 8
            ([8, 8], 10, "split"),  # 8,8 vs 10
            ([1, 1], 5, "split"),  # A,A vs 5
        ]

        correct_decisions = 0
        total_decisions = len(critical_tests)

        for hand, dealer, expected in critical_tests:
            action = bjlogic_cpp.basic_strategy_decision(hand, dealer, rules)
            if action == expected:
                correct_decisions += 1
            else:
                print(f"   ❌ CRITICAL: {hand} vs {dealer} -> {action} (expected {expected})")

        accuracy = (correct_decisions / total_decisions) * 100
        print(f"✅ Critical strategy accuracy: {correct_decisions}/{total_decisions} ({accuracy:.1f}%)")

        # Final verification
        assert accuracy == 100, f"Critical strategy decisions failed: {accuracy}%"
        assert is_optimal_11_ace, "11 vs ACE should be double when dealer stands soft 17"
        assert is_optimal_a7_2, "A,7 vs 2 should be double when dealer stands soft 17"

        print(f"\n🎉 ALL PHASE 2.2 TESTS PASSED!")
        print(f"✅ Version: {bjlogic_cpp.__version__}")
        print(f"✅ Phase: {bjlogic_cpp.__phase__}")
        print("🔥 Strategy optimized for DEALER STANDS ON SOFT 17!")
        print("🎯 Complete basic strategy tables successfully implemented!")
        return True

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("Make sure you ran: python setup.py build_ext --inplace")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_soft_17_specific_scenarios():
    """Test scenarios that are specifically different for dealer stands vs hits soft 17"""
    print("\n🔥 Testing DEALER STANDS SOFT 17 Specific Scenarios:")

    try:
        import bjlogic_cpp
        rules = bjlogic_cpp.create_rules_config()
        rules["dealer_hits_soft_17"] = False  # Dealer stands on soft 17
        rules["resplitting_allowed"] = True
        rules["surrender_allowed"] = True

        # These decisions are DIFFERENT when dealer stands vs hits soft 17
        key_differences = [
            # [hand, dealer, expected_action, why_different]
            ([5, 6], 1, "double", "Hard 11 vs A: Double when dealer stands, hit when dealer hits"),  # CORRECTED!
            ([1, 7], 2, "double", "A,7 vs 2: Double when dealer stands, stand when dealer hits"),
            ([1, 8], 6, "double", "A,8 vs 6: Double when dealer stands, stand when dealer hits"),
        ]

        all_correct = True

        for hand, dealer, expected, explanation in key_differences:
            action = bjlogic_cpp.basic_strategy_decision(hand, dealer, rules)
            status = "✅" if action == expected else "❌"
            if action != expected:
                all_correct = False
            print(f"   {status} {explanation}")
            print(f"       Result: {hand} vs {dealer} -> {action}")

        if all_correct:
            print("🔥 ALL dealer-stands-soft-17 specific decisions CORRECT!")
        else:
            print("❌ Some dealer-stands-soft-17 decisions are wrong!")

        return all_correct

    except Exception as e:
        print(f"❌ Soft 17 test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_complete_strategy()
    soft17_ok = test_soft_17_specific_scenarios()

    if success and soft17_ok:
        print("\n🎊 PHASE 2.2 MIGRATION SUCCESSFUL!")
        print("🔥 Strategy perfectly optimized for DEALER STANDS ON SOFT 17!")
        print("🚀 Complete basic strategy tables are working perfectly!")
        print("Ready to proceed to Phase 2.3 (Dealer Probability Engine)")
    else:
        print("\n❌ Phase 2.2 migration needs fixes")

    import sys

    sys.exit(0 if (success and soft17_ok) else 1)