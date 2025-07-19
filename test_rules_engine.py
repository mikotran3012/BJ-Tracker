# test_rules_engine.py
"""
Unit tests for BlackjackRules engine using pytest.
Run with: pytest test_rules_engine.py -v
"""

import pytest
from rules_engine import BlackjackRules, Card, Hand


class TestBlackjackRules:
    """Test suite for BlackjackRules class."""

    def setup_method(self):
        """Setup fresh rules engine for each test."""
        self.rules = BlackjackRules()

    def test_initialization(self):
        """Test that rules are initialized with correct default values."""
        assert self.rules.dealer_hits_soft_17 == False
        assert self.rules.blackjack_payout == (3, 2)
        assert self.rules.double_after_split == False
        assert self.rules.max_splits == 2
        assert self.rules.late_surrender == True
        assert self.rules.insurance_allowed == True

    def test_get_card_value(self):
        """Test card value calculation."""
        assert self.rules.get_card_value('A') == 11
        assert self.rules.get_card_value('2') == 2
        assert self.rules.get_card_value('9') == 9
        assert self.rules.get_card_value('T') == 10
        assert self.rules.get_card_value('J') == 10
        assert self.rules.get_card_value('Q') == 10
        assert self.rules.get_card_value('K') == 10

    def test_calculate_hand_value_simple(self):
        """Test hand value calculation for simple cases."""
        # Simple numeric hand
        hand = Hand([Card('7', '♠'), Card('5', '♥')])
        value, is_soft = self.rules.calculate_hand_value(hand)
        assert value == 12
        assert is_soft == False

        # Hand with face cards
        hand = Hand([Card('K', '♠'), Card('Q', '♥')])
        value, is_soft = self.rules.calculate_hand_value(hand)
        assert value == 20
        assert is_soft == False

    def test_calculate_hand_value_with_aces(self):
        """Test hand value calculation with aces."""
        # Soft 17 (A,6)
        hand = Hand([Card('A', '♠'), Card('6', '♥')])
        value, is_soft = self.rules.calculate_hand_value(hand)
        assert value == 17
        assert is_soft == True

        # Hard 17 (A,6,A - ace adjusted)
        hand = Hand([Card('A', '♠'), Card('6', '♥'), Card('A', '♦')])
        value, is_soft = self.rules.calculate_hand_value(hand)
        assert value == 18
        assert is_soft == True

        # Bust then adjust (A,A,9)
        hand = Hand([Card('A', '♠'), Card('A', '♥'), Card('9', '♦')])
        value, is_soft = self.rules.calculate_hand_value(hand)
        assert value == 21
        assert is_soft == True

        # Multiple aces adjusted (A,A,A,8)
        hand = Hand([Card('A', '♠'), Card('A', '♥'), Card('A', '♦'), Card('8', '♣')])
        value, is_soft = self.rules.calculate_hand_value(hand)
        assert value == 21
        assert is_soft == True

    def test_can_split_valid_cases(self):
        """Test can_split for valid splitting scenarios."""
        # Same rank cards
        hand = Hand([Card('8', '♠'), Card('8', '♥')])
        assert self.rules.can_split(hand) == True

        # Same value different ranks (T,K)
        hand = Hand([Card('T', '♠'), Card('K', '♥')])
        assert self.rules.can_split(hand) == True

        # Aces
        hand = Hand([Card('A', '♠'), Card('A', '♥')])
        assert self.rules.can_split(hand) == True

    def test_can_split_invalid_cases(self):
        """Test can_split for invalid splitting scenarios."""
        # Different values
        hand = Hand([Card('8', '♠'), Card('7', '♥')])
        assert self.rules.can_split(hand) == False

        # More than 2 cards
        hand = Hand([Card('8', '♠'), Card('8', '♥'), Card('5', '♦')])
        assert self.rules.can_split(hand) == False

        # Already at max splits
        hand = Hand([Card('8', '♠'), Card('8', '♥')], splits_count=2)
        assert self.rules.can_split(hand) == False

    def test_can_double_valid_cases(self):
        """Test can_double for valid doubling scenarios."""
        # Standard 2-card hand
        hand = Hand([Card('5', '♠'), Card('6', '♥')])
        assert self.rules.can_double(hand) == True

        # Split hand with double_after_split enabled
        self.rules.double_after_split = True
        hand = Hand([Card('5', '♠'), Card('6', '♥')], is_split=True)
        assert self.rules.can_double(hand) == True

    def test_can_double_invalid_cases(self):
        """Test can_double for invalid doubling scenarios."""
        # More than 2 cards
        hand = Hand([Card('5', '♠'), Card('6', '♥'), Card('2', '♦')])
        assert self.rules.can_double(hand) == False

        # Already doubled
        hand = Hand([Card('5', '♠'), Card('6', '♥')], is_doubled=True)
        assert self.rules.can_double(hand) == False

        # Split hand with double_after_split disabled (default)
        hand = Hand([Card('5', '♠'), Card('6', '♥')], is_split=True)
        assert self.rules.can_double(hand) == False

    def test_is_blackjack_valid_cases(self):
        """Test is_blackjack for valid blackjack hands."""
        # A,K
        hand = Hand([Card('A', '♠'), Card('K', '♥')])
        assert self.rules.is_blackjack(hand) == True

        # A,T
        hand = Hand([Card('A', '♠'), Card('T', '♥')])
        assert self.rules.is_blackjack(hand) == True

        # T,A (order doesn't matter)
        hand = Hand([Card('T', '♠'), Card('A', '♥')])
        assert self.rules.is_blackjack(hand) == True

    def test_is_blackjack_invalid_cases(self):
        """Test is_blackjack for invalid blackjack scenarios."""
        # 21 with 3 cards
        hand = Hand([Card('7', '♠'), Card('7', '♥'), Card('7', '♦')])
        assert self.rules.is_blackjack(hand) == False

        # Split hand (even if A,K)
        hand = Hand([Card('A', '♠'), Card('K', '♥')], is_split=True)
        assert self.rules.is_blackjack(hand) == False

        # 20 (not 21)
        hand = Hand([Card('K', '♠'), Card('Q', '♥')])
        assert self.rules.is_blackjack(hand) == False

    def test_can_surrender_valid_cases(self):
        """Test can_surrender for valid surrender scenarios."""
        # Standard 2-card hand
        hand = Hand([Card('T', '♠'), Card('6', '♥')])
        assert self.rules.can_surrender(hand) == True

        # Bad hand (should be allowed)
        hand = Hand([Card('T', '♠'), Card('5', '♥')])
        assert self.rules.can_surrender(hand) == True

    def test_can_surrender_invalid_cases(self):
        """Test can_surrender for invalid surrender scenarios."""
        # Late surrender disabled
        self.rules.late_surrender = False
        hand = Hand([Card('T', '♠'), Card('6', '♥')])
        assert self.rules.can_surrender(hand) == False

        # Reset for other tests
        self.rules.late_surrender = True

        # More than 2 cards
        hand = Hand([Card('T', '♠'), Card('6', '♥'), Card('2', '♦')])
        assert self.rules.can_surrender(hand) == False

        # Split hand
        hand = Hand([Card('T', '♠'), Card('6', '♥')], is_split=True)
        assert self.rules.can_surrender(hand) == False

        # Doubled hand
        hand = Hand([Card('T', '♠'), Card('6', '♥')], is_doubled=True)
        assert self.rules.can_surrender(hand) == False

    def test_dealer_should_hit_standard_rules(self):
        """Test dealer hitting logic with standard rules (no soft 17)."""
        # Dealer has 16 - should hit
        hand = Hand([Card('T', '♠'), Card('6', '♥')])
        assert self.rules.dealer_should_hit(hand) == True

        # Dealer has hard 17 - should stand
        hand = Hand([Card('T', '♠'), Card('7', '♥')])
        assert self.rules.dealer_should_hit(hand) == False

        # Dealer has soft 17 (A,6) - should stand (standard rules)
        hand = Hand([Card('A', '♠'), Card('6', '♥')])
        assert self.rules.dealer_should_hit(hand) == False

        # Dealer has 18 - should stand
        hand = Hand([Card('T', '♠'), Card('8', '♥')])
        assert self.rules.dealer_should_hit(hand) == False

    def test_dealer_should_hit_soft_17_rule(self):
        """Test dealer hitting logic with dealer hits soft 17 rule."""
        self.rules.dealer_hits_soft_17 = True

        # Dealer has soft 17 (A,6) - should hit
        hand = Hand([Card('A', '♠'), Card('6', '♥')])
        assert self.rules.dealer_should_hit(hand) == True

        # Dealer has hard 17 - should still stand
        hand = Hand([Card('T', '♠'), Card('7', '♥')])
        assert self.rules.dealer_should_hit(hand) == False

        # Dealer has soft 18 (A,7) - should stand
        hand = Hand([Card('A', '♠'), Card('7', '♥')])
        assert self.rules.dealer_should_hit(hand) == False

    def test_is_bust(self):
        """Test bust detection."""
        # Bust hand
        hand = Hand([Card('T', '♠'), Card('K', '♥'), Card('5', '♦')])
        assert self.rules.is_bust(hand) == True

        # Non-bust hand
        hand = Hand([Card('T', '♠'), Card('A', '♥')])
        assert self.rules.is_bust(hand) == False

        # Exactly 21
        hand = Hand([Card('T', '♠'), Card('A', '♥')])
        assert self.rules.is_bust(hand) == False

    def test_get_blackjack_payout_amount(self):
        """Test blackjack payout calculation."""
        # 3:2 payout on $100 bet
        assert self.rules.get_blackjack_payout_amount(100) == 150.0

        # 3:2 payout on $25 bet
        assert self.rules.get_blackjack_payout_amount(25) == 37.5

        # Change to 6:5 payout
        self.rules.blackjack_payout = (6, 5)
        assert self.rules.get_blackjack_payout_amount(100) == 120.0

    def test_compare_hands(self):
        """Test hand comparison logic."""
        # Player blackjack vs dealer 20
        player = Hand([Card('A', '♠'), Card('K', '♥')])
        dealer = Hand([Card('T', '♠'), Card('Q', '♥')])
        assert self.rules.compare_hands(player, dealer) == 'blackjack'

        # Both blackjack
        player = Hand([Card('A', '♠'), Card('K', '♥')])
        dealer = Hand([Card('A', '♦'), Card('Q', '♣')])
        assert self.rules.compare_hands(player, dealer) == 'push'

        # Player bust
        player = Hand([Card('T', '♠'), Card('K', '♥'), Card('5', '♦')])
        dealer = Hand([Card('T', '♠'), Card('7', '♥')])
        assert self.rules.compare_hands(player, dealer) == 'bust'

        # Dealer bust
        player = Hand([Card('T', '♠'), Card('8', '♥')])
        dealer = Hand([Card('T', '♠'), Card('K', '♥'), Card('5', '♦')])
        assert self.rules.compare_hands(player, dealer) == 'win'

        # Player wins with higher value
        player = Hand([Card('T', '♠'), Card('9', '♥')])
        dealer = Hand([Card('T', '♠'), Card('7', '♥')])
        assert self.rules.compare_hands(player, dealer) == 'win'

        # Player loses with lower value
        player = Hand([Card('T', '♠'), Card('6', '♥')])
        dealer = Hand([Card('T', '♠'), Card('8', '♥')])
        assert self.rules.compare_hands(player, dealer) == 'lose'

        # Push with same value
        player = Hand([Card('T', '♠'), Card('8', '♥')])
        dealer = Hand([Card('9', '♠'), Card('9', '♥')])
        assert self.rules.compare_hands(player, dealer) == 'push'


# Additional test for edge cases
class TestBlackjackRulesEdgeCases:
    """Test edge cases and rule variations."""

    def setup_method(self):
        """Setup fresh rules engine for each test."""
        self.rules = BlackjackRules()

    def test_multiple_aces_adjustment(self):
        """Test proper ace adjustment with multiple aces."""
        # Four aces should equal 14 (A,A,A,A = 1+1+1+11)
        hand = Hand([Card('A', '♠'), Card('A', '♥'), Card('A', '♦'), Card('A', '♣')])
        value, is_soft = self.rules.calculate_hand_value(hand)
        assert value == 14
        assert is_soft == True

    def test_rule_customization(self):
        """Test that rules can be customized."""
        # Change payout to 6:5
        self.rules.blackjack_payout = (6, 5)
        assert self.rules.get_blackjack_payout_amount(100) == 120.0

        # Enable double after split
        self.rules.double_after_split = True
        hand = Hand([Card('5', '♠'), Card('6', '♥')], is_split=True)
        assert self.rules.can_double(hand) == True

        # Change max splits
        self.rules.max_splits = 3
        hand = Hand([Card('8', '♠'), Card('8', '♥')], splits_count=2)
        assert self.rules.can_split(hand) == True


if __name__ == '__main__':
    # Run tests if script is executed directly
    pytest.main([__file__, '-v'])
