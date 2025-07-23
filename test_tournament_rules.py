# test_tournament_rules.py
"""
Test tournament rules that integrate with existing rules_engine.py
"""

import pytest
from extended_rules_engine import TournamentBlackjackRules, TournamentEVCalculator

# Try to import existing classes
try:
    from rules_engine import Hand, Card

    EXISTING_RULES_AVAILABLE = True
except ImportError:
    EXISTING_RULES_AVAILABLE = False


    # Create mock classes for testing
    class Card:
        def __init__(self, rank, suit):
            self.rank = rank
            self.suit = suit


    class Hand:
        def __init__(self, cards, is_split=False, is_doubled=False, splits_count=0, split_from_rank=None):
            self.cards = cards
            self.is_split = is_split
            self.is_doubled = is_doubled
            self.splits_count = splits_count
            self.split_from_rank = split_from_rank


class TestTournamentRules:
    """Test tournament rule enforcement."""

    def setup_method(self):
        """Setup tournament rules for each test."""
        self.rules = TournamentBlackjackRules()

    def test_no_das_rule(self):
        """Test that split hands cannot double (No DAS)."""
        # Regular hand should be able to double
        regular_hand = Hand([Card('5', '♠'), Card('6', '♥')])
        assert self.rules.can_double(regular_hand) == True

        # Split hand should NOT be able to double
        split_hand = Hand([Card('5', '♠'), Card('6', '♥')], is_split=True)
        assert self.rules.can_double(split_hand) == False

    def test_no_resplit_rule(self):
        """Test that pairs cannot be resplit."""
        # Initial pair should be splittable
        initial_pair = Hand([Card('8', '♠'), Card('8', '♥')])
        assert self.rules.can_split(initial_pair) == True

        # Already split once using splits_count - should not be splittable
        already_split = Hand([Card('8', '♠'), Card('8', '♥')], splits_count=1)
        assert self.rules.can_split(already_split) == False

        # Already split using is_split flag - should not be splittable
        split_hand_flag = Hand([Card('8', '♠'), Card('8', '♥')], is_split=True)
        assert self.rules.can_split(split_hand_flag) == False

    def test_s17_rule(self):
        """Test that dealer stands on soft 17."""
        # Hard 17 - should stand
        hard_17 = Hand([Card('T', '♠'), Card('7', '♥')])
        assert self.rules.dealer_should_hit(hard_17) == False

        # Soft 17 - should stand (S17 rule)
        soft_17 = Hand([Card('A', '♠'), Card('6', '♥')])
        assert self.rules.dealer_should_hit(soft_17) == False

        # 16 - should hit
        sixteen = Hand([Card('T', '♠'), Card('6', '♥')])
        assert self.rules.dealer_should_hit(sixteen) == True

        # 18 - should stand
        eighteen = Hand([Card('T', '♠'), Card('8', '♥')])
        assert self.rules.dealer_should_hit(eighteen) == False

    def test_split_aces_one_card_rule(self):
        """Test that split aces get only one card."""
        # Regular split hand can hit
        regular_split = Hand([Card('8', '♠'), Card('3', '♥')], is_split=True)
        # Add split_from_rank attribute manually since Hand doesn't have it built-in
        regular_split.split_from_rank = '8'
        assert self.rules.can_hit_after_split(regular_split) == True

        # Split ace with one card can hit
        split_ace_one_card = Hand([Card('A', '♠')], is_split=True)
        split_ace_one_card.split_from_rank = 'A'
        assert self.rules.can_hit_after_split(split_ace_one_card) == True

        # Split ace with two cards cannot hit
        split_ace_two_cards = Hand([Card('A', '♠'), Card('5', '♥')], is_split=True)
        split_ace_two_cards.split_from_rank = 'A'
        assert self.rules.can_hit_after_split(split_ace_two_cards) == False

    def test_surrender_rule(self):
        """Test late surrender is allowed on initial hands only."""
        # Initial 2-card hand should allow surrender
        initial_hand = Hand([Card('T', '♠'), Card('6', '♥')])
        assert self.rules.can_surrender(initial_hand) == True

        # Split hand should not allow surrender
        split_hand = Hand([Card('T', '♠'), Card('6', '♥')], is_split=True)
        assert self.rules.can_surrender(split_hand) == False

        # Doubled hand should not allow surrender
        doubled_hand = Hand([Card('T', '♠'), Card('6', '♥')], is_doubled=True)
        assert self.rules.can_surrender(doubled_hand) == False

        # 3+ card hand should not allow surrender
        three_card_hand = Hand([Card('5', '♠'), Card('5', '♥'), Card('6', '♦')])
        assert self.rules.can_surrender(three_card_hand) == False

    def test_available_actions(self):
        """Test that available actions respect tournament rules."""
        # Initial hand should have multiple options
        initial_hand = Hand([Card('T', '♠'), Card('6', '♥')])
        actions = self.rules.get_available_actions(initial_hand)
        expected_actions = {'stand', 'hit', 'surrender'}
        assert expected_actions.issubset(set(actions))

        # Split hand should not have double option
        split_hand = Hand([Card('5', '♠'), Card('6', '♥')], is_split=True)
        actions = self.rules.get_available_actions(split_hand)
        assert 'double' not in actions
        assert 'surrender' not in actions

        # Pair should have split option
        pair_hand = Hand([Card('8', '♠'), Card('8', '♥')])
        actions = self.rules.get_available_actions(pair_hand)
        assert 'split' in actions


class TestTournamentEVCalculator:
    """Test tournament EV calculator."""

    def setup_method(self):
        """Setup EV calculator for each test."""
        self.calculator = TournamentEVCalculator()

    def test_ev_calculation_basic(self):
        """Test basic EV calculation with tournament rules."""
        hand = Hand([Card('T', '♠'), Card('6', '♥')])
        deck_comp = {'A': 4, '2': 4, '3': 4, '4': 4, '5': 4, '6': 3, '7': 4, '8': 4, '9': 4, 'T': 15}

        results = self.calculator.calculate_ev(hand, 'T', deck_comp)

        # Should have surrender option (16 vs T)
        assert 'surrender' in results
        assert results['surrender'] == -0.5

        # Should have best action
        assert 'best' in results
        assert 'best_ev' in results

    def test_split_hand_ev_no_double(self):
        """Test that split hands don't get double EV option."""
        split_hand = Hand([Card('5', '♠'), Card('6', '♥')], is_split=True)
        deck_comp = {'A': 4, '2': 4, '3': 4, '4': 4, '5': 3, '6': 3, '7': 4, '8': 4, '9': 4, 'T': 16}

        results = self.calculator.calculate_ev(split_hand, '6', deck_comp)

        # Should NOT have double option due to no DAS rule
        assert 'double' not in results


def test_integration_with_existing_rules():
    """Test integration with existing rules_engine if available."""
    if EXISTING_RULES_AVAILABLE:
        print("✓ Testing with existing rules_engine integration")

        # Test that tournament rules work with existing Hand/Card classes
        rules = TournamentBlackjackRules()

        # Test with your existing classes
        hand = Hand([Card('A', '♠'), Card('6', '♥')])
        should_hit = rules.dealer_should_hit(hand)

        assert should_hit == False, "S17 rule should make dealer stand on soft 17"
        print("✓ S17 rule working with existing classes")

    else:
        print("⚠️  Running with mock classes (existing rules_engine not found)")


def run_tournament_tests():
    """Run all tournament rule tests."""
    print("=" * 60)
    print("TOURNAMENT BLACKJACK RULES TESTS")
    print("=" * 60)
    print("Testing: S17, No DAS, No Resplit, Split Aces One Card, Surrender")
    print()

    # Run pytest programmatically
    import subprocess
    import sys

    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest',
            __file__, '-v', '--tb=short'
        ], capture_output=True, text=True)

        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        return result.returncode == 0

    except Exception as e:
        print(f"Error running tests: {e}")
        return False


if __name__ == '__main__':
    # Run integration test first
    test_integration_with_existing_rules()

    # Run all tests
    success = run_tournament_tests()

    if success:
        print("\n🎉 All tournament rule tests passed!")
    else:
        print("\n❌ Some tests failed")