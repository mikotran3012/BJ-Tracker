# rules_engine.py
"""
Pure-logic engine for Blackjack house rules and game mechanics.
"""

from typing import List, Tuple, Union
from dataclasses import dataclass


@dataclass
class Card:
    """Represents a playing card."""
    rank: str  # 'A', '2'-'9', 'T', 'J', 'Q', 'K'
    suit: str  # '♠', '♥', '♦', '♣'


@dataclass
class Hand:
    """Represents a blackjack hand."""
    cards: List[Card]
    is_split: bool = False
    splits_count: int = 0
    is_doubled: bool = False


class BlackjackRules:
    """
    Pure-logic engine for Blackjack house rules.
    Encapsulates all game rules and decision logic without UI dependencies.
    """

    def __init__(self):
        # House rules configuration
        self.dealer_hits_soft_17 = False
        self.blackjack_payout = (3, 2)  # 3:2 payout ratio
        self.double_after_split = False
        self.max_splits = 2
        self.late_surrender = True
        self.insurance_allowed = True

    def get_card_value(self, rank: str) -> int:
        """Get the base value of a card rank."""
        if rank in ['J', 'Q', 'K']:
            return 10
        elif rank == 'T':
            return 10
        elif rank == 'A':
            return 11  # Will be adjusted in hand calculation
        else:
            return int(rank)

    def calculate_hand_value(self, hand: Hand) -> Tuple[int, bool]:
        """
        Calculate hand value and determine if it's soft.
        Returns (value, is_soft) where is_soft means contains usable ace as 11.
        """
        total = 0
        aces = 0

        for card in hand.cards:
            if card.rank == 'A':
                aces += 1
                total += 11
            else:
                total += self.get_card_value(card.rank)

        # Adjust for aces
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1

        # Hand is soft if we have an ace counted as 11
        is_soft = aces > 0 and total <= 21

        return total, is_soft

    def can_split(self, hand: Hand) -> bool:
        """
        Check if a hand can be split.
        Requirements: exactly 2 cards of same rank, under max splits limit.
        """
        if len(hand.cards) != 2:
            return False

        if hand.splits_count >= self.max_splits:
            return False

        # Check if both cards have same rank value
        card1, card2 = hand.cards[0], hand.cards[1]
        val1 = self.get_card_value(card1.rank)
        val2 = self.get_card_value(card2.rank)

        return val1 == val2

    def can_double(self, hand: Hand) -> bool:
        """
        Check if a hand can be doubled.
        Requirements: exactly 2 cards, or split-allowed based on double_after_split rule.
        """
        if len(hand.cards) != 2:
            return False

        if hand.is_doubled:
            return False

        # If this is a split hand, check double_after_split rule
        if hand.is_split and not self.double_after_split:
            return False

        return True

    def is_blackjack(self, hand: Hand) -> bool:
        """
        Check if hand is a natural blackjack.
        Requirements: exactly 2 cards totaling 21, not from a split.
        """
        if len(hand.cards) != 2:
            return False

        if hand.is_split:
            return False  # Split hands can't be blackjack

        value, _ = self.calculate_hand_value(hand)
        return value == 21

    def can_surrender(self, hand: Hand) -> bool:
        """
        Check if a hand can surrender.
        Requirements: late_surrender enabled, exactly 2 cards, not split, not doubled.
        """
        if not self.late_surrender:
            return False

        if len(hand.cards) != 2:
            return False

        if hand.is_split:
            return False  # Can't surrender split hands

        if hand.is_doubled:
            return False  # Can't surrender after doubling

        return True

    def dealer_should_hit(self, dealer_hand: Hand) -> bool:
        """
        Determine if dealer should hit based on house rules.
        Standard: hit on 16 or less, stand on 17 or more.
        Variation: dealer_hits_soft_17 affects soft 17 decision.
        """
        value, is_soft = self.calculate_hand_value(dealer_hand)

        if value < 17:
            return True
        elif value > 17:
            return False
        elif value == 17:
            # Value is exactly 17
            if is_soft and self.dealer_hits_soft_17:
                return True
            else:
                return False
        else:
            return False

    def is_bust(self, hand: Hand) -> bool:
        """Check if hand is busted (over 21)."""
        value, _ = self.calculate_hand_value(hand)
        return value > 21

    def get_blackjack_payout_amount(self, bet: float) -> float:
        """Calculate blackjack payout amount based on payout ratio."""
        numerator, denominator = self.blackjack_payout
        return bet * (numerator / denominator)

    def compare_hands(self, player_hand: Hand, dealer_hand: Hand) -> str:
        """
        Compare player and dealer hands to determine outcome.
        Returns: 'win', 'lose', 'push', 'blackjack', 'bust'
        """
        player_value, _ = self.calculate_hand_value(player_hand)
        dealer_value, _ = self.calculate_hand_value(dealer_hand)

        # Check for busts
        if player_value > 21:
            return 'bust'

        if dealer_value > 21:
            return 'win'

        # Check for blackjacks
        player_bj = self.is_blackjack(player_hand)
        dealer_bj = self.is_blackjack(dealer_hand)

        if player_bj and dealer_bj:
            return 'push'
        elif player_bj:
            return 'blackjack'
        elif dealer_bj:
            return 'lose'

        # Compare values
        if player_value > dealer_value:
            return 'win'
        elif player_value < dealer_value:
            return 'lose'
        else:
            return 'push'
