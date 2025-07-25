#!/usr/bin/env python3
# test_extension.py
"""
Test the working C++ extension
"""


def test_extension():
    """Test all extension functions"""
    print("🧪 Testing C++ Extension")
    print("=" * 40)

    try:
        import bjlogic_cpp
        print("✅ Import successful")

        # Test basic function
        message = bjlogic_cpp.test_extension()
        print(f"✅ Test function: {message}")

        # Test card value function
        ace_value = bjlogic_cpp.get_card_value("A")
        king_value = bjlogic_cpp.get_card_value("K")
        five_value = bjlogic_cpp.get_card_value("5")

        print(f"✅ Card values: A={ace_value}, K={king_value}, 5={five_value}")

        # Test hand calculations
        blackjack = bjlogic_cpp.calculate_hand_value(["A", "K"])
        soft_17 = bjlogic_cpp.calculate_hand_value(["A", "6"])
        hard_20 = bjlogic_cpp.calculate_hand_value(["K", "Q"])

        print(f"✅ Blackjack (A,K): {blackjack}")
        print(f"✅ Soft 17 (A,6): {soft_17}")
        print(f"✅ Hard 20 (K,Q): {hard_20}")

        # Verify results
        assert blackjack == (21, False), f"Expected (21, False), got {blackjack}"
        assert soft_17 == (17, True), f"Expected (17, True), got {soft_17}"
        assert hard_20 == (20, False), f"Expected (20, False), got {hard_20}"

        print("\n🎉 ALL TESTS PASSED!")
        print("Your C++ extension is working perfectly!")
        return True

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("Make sure you ran: python setup.py build_ext --inplace")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    test_extension()