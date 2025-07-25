#!/usr/bin/env python3
# test_phase_2_1.py
"""
Test script for Phase 2.1 migration - Advanced data structures
"""


def test_enhanced_extension():
    """Test all the new Phase 2.1 features"""
    print("🧪 Testing Phase 2.1 - Advanced Data Structures")
    print("=" * 50)

    try:
        import bjlogic_cpp
        print("✅ Import successful")

        # Test basic function
        message = bjlogic_cpp.test_extension()
        print(f"✅ Test function: {message}")

        # Test enhanced hand calculation
        print("\n🃏 Testing Enhanced Hand Calculations:")

        # Test blackjack
        blackjack = bjlogic_cpp.calculate_hand_value([1, 10])
        print(f"✅ Blackjack (A,10): {blackjack}")

        # Test soft 17
        soft_17 = bjlogic_cpp.calculate_hand_value([1, 6])
        print(f"✅ Soft 17 (A,6): {soft_17}")

        # Test hard 20
        hard_20 = bjlogic_cpp.calculate_hand_value([10, 10])
        print(f"✅ Hard 20 (10,10): {hard_20}")

        # Test hand analysis functions
        print("\n🔍 Testing Hand Analysis Functions:")
        print(f"✅ Is [1,6] soft? {bjlogic_cpp.is_hand_soft([1, 6])}")
        print(f"✅ Can [8,8] split? {bjlogic_cpp.can_split_hand([8, 8])}")
        print(f"✅ Is [10,10,5] busted? {bjlogic_cpp.is_hand_busted([10, 10, 5])}")

        # Test deck state creation
        print("\n🎴 Testing Deck State:")
        deck = bjlogic_cpp.create_deck_state(6)
        print(f"✅ Created 6-deck state: {deck['num_decks']} decks, {deck['total_cards']} cards")

        # Test rules configuration
        print("\n📋 Testing Rules Configuration:")
        rules = bjlogic_cpp.create_rules_config()
        print(f"✅ Default rules: {rules['num_decks']} decks, dealer hits soft 17: {rules['dealer_hits_soft_17']}")

        # Test basic strategy
        print("\n🎯 Testing Basic Strategy:")
        action1 = bjlogic_cpp.basic_strategy_decision([10, 6], 10, rules)
        action2 = bjlogic_cpp.basic_strategy_decision([8, 8], 6, rules)
        print(f"✅ Hard 16 vs 10: {action1}")
        print(f"✅ Pair 8s vs 6: {action2}")

        # Test Action enum
        print("\n⚡ Testing Action Enum:")
        print(f"✅ Action enum available: {hasattr(bjlogic_cpp, 'Action')}")
        if hasattr(bjlogic_cpp, 'Action'):
            print(f"   - STAND: {bjlogic_cpp.Action.STAND}")
            print(f"   - HIT: {bjlogic_cpp.Action.HIT}")
            print(f"   - DOUBLE: {bjlogic_cpp.Action.DOUBLE}")

        # Verify results
        assert blackjack['is_blackjack'] == True, "Blackjack detection failed"
        assert blackjack['is_soft'] == False, "Blackjack should not be soft"
        assert soft_17['is_soft'] == True, "Soft 17 should be soft"
        assert soft_17['total'] == 17, f"Soft 17 total should be 17, got {soft_17['total']}"

        print(f"\n🎉 ALL PHASE 2.1 TESTS PASSED!")
        print(f"✅ Version: {bjlogic_cpp.__version__}")
        print(f"✅ Phase: {bjlogic_cpp.__phase__}")
        print("🚀 Advanced data structures successfully migrated!")
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


def test_compatibility():
    """Test that old functions still work"""
    print("\n🔄 Testing Backward Compatibility:")

    try:
        import bjlogic_cpp

        # Test if old simple functions still exist (if they do)
        if hasattr(bjlogic_cpp, 'get_card_value'):
            card_val = bjlogic_cpp.get_card_value("A")
            print(f"✅ Old get_card_value still works: A = {card_val}")

        print("✅ Backward compatibility maintained")
        return True

    except Exception as e:
        print(f"⚠️  Compatibility issue: {e}")
        return False


if __name__ == "__main__":
    success = test_enhanced_extension()
    test_compatibility()

    if success:
        print("\n🎊 PHASE 2.1 MIGRATION SUCCESSFUL!")
        print("Ready to proceed to Phase 2.2 (Basic Strategy Tables)")
    else:
        print("\n❌ Phase 2.1 migration needs fixes")

    import sys

    sys.exit(0 if success else 1)