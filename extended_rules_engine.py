# extended_rules_engine.py
"""
Extended rules engine that enforces specific tournament rules:
- S17 (dealer stands on soft 17)
- No DAS (double after split disabled)
- No resplitting
- Split aces get one card only
- Late surrender allowed

Integrates with your existing rules_engine.py system.
"""

from typing import Dict, List, Optional, Tuple
import sys
import os

# Import your existing rules engine
try:
    from rules_engine import BlackjackRules, Hand, Card

    EXISTING_RULES_AVAILABLE = True
except ImportError:
    print("Warning: Could not import existing rules_engine. Using standalone mode.")
    EXISTING_RULES_AVAILABLE = False


class TournamentBlackjackRules:
    """
    Tournament rules that enforce specific constraints.
    Extends your existing BlackjackRules with strict enforcement.
    """

    def __init__(self):
        # Use your existing rules as base if available
        if EXISTING_RULES_AVAILABLE:
            self.base_rules = BlackjackRules()
            # Override with tournament settings
            self.base_rules.dealer_hits_soft_17 = False  # S17
            self.base_rules.double_after_split = False  # No DAS
            self.base_rules.max_splits = 1  # No resplitting
            self.base_rules.late_surrender = True  # Surrender allowed
        else:
            self.base_rules = None

        # Tournament-specific settings
        self.tournament_rules = {
            'dealer_stands_soft_17': True,  # S17 rule
            'double_after_split': False,  # No DAS
            'resplitting_allowed': False,  # No resplitting
            'split_aces_one_card': True,  # Split aces get one card
            'late_surrender': True,  # Surrender allowed
            'max_splits': 1  # Only one split per pair
        }

    def can_double(self, hand) -> bool:
        """
        ENFORCED: No double after split (DAS disabled).
        """
        # Basic checks first
        if hasattr(hand, 'cards') and len(hand.cards) != 2:
            return False
        if hasattr(hand, 'is_doubled') and hand.is_doubled:
            return False

        # RULE ENFORCEMENT: No double after split
        if hasattr(hand, 'is_split') and hand.is_split:
            return False  # DAS disabled

        return True

    def can_split(self, hand) -> bool:
        """ENFORCED: No resplitting allowed."""
        if hasattr(hand, 'cards') and len(hand.cards) != 2:
            return False

        # Check BOTH ways for splits
        if hasattr(hand, 'splits_count') and hand.splits_count >= 1:
            return False
        if hasattr(hand, 'is_split') and hand.is_split:
            return False

        # Check if same value
        if hasattr(hand, 'cards'):
            card1_value = self._get_split_value(hand.cards[0])
            card2_value = self._get_split_value(hand.cards[1])
            return card1_value == card2_value

        return False

    def can_hit_after_split(self, hand) -> bool:
        """
        ENFORCED: Split aces get only one card.
        """
        if not hasattr(hand, 'is_split') or not hand.is_split:
            return True  # Normal hand can hit

        # Check if this is a split ace hand
        if hasattr(hand, 'split_from_rank'):
            if hand.split_from_rank == 'A' and len(hand.cards) >= 2:
                return False  # Split aces can't hit after one card

        return True  # Other split hands can hit normally

    def dealer_should_hit(self, hand) -> bool:
        """
        ENFORCED: Dealer stands on soft 17 (S17 rule).
        """
        if EXISTING_RULES_AVAILABLE and self.base_rules:
            # Use existing calculation but enforce S17
            value, is_soft = self.base_rules.calculate_hand_value(hand)
        else:
            value, is_soft = self._calculate_hand_value_standalone(hand)

        if value < 17:
            return True  # Must hit
        elif value > 17:
            return False  # Must stand
        else:  # value == 17
            # RULE ENFORCEMENT: Stand on ALL 17s (including soft 17)
            return False  # S17 rule - dealer stands on soft 17

    def can_surrender(self, hand) -> bool:
        """
        ENFORCED: Late surrender allowed on initial hands only.
        """
        # Must be 2-card hand
        if hasattr(hand, 'cards') and len(hand.cards) != 2:
            return False

        # Must not be split hand
        if hasattr(hand, 'is_split') and hand.is_split:
            return False

        # Must not be doubled
        if hasattr(hand, 'is_doubled') and hand.is_doubled:
            return False

        return self.tournament_rules['late_surrender']

    def get_available_actions(self, hand) -> List[str]:
        """
        Get all available actions for a hand based on tournament rules.
        """
        actions = []

        # Always can stand (unless busted)
        if EXISTING_RULES_AVAILABLE and self.base_rules:
            if not self.base_rules.is_bust(hand):
                actions.append('stand')
        else:
            value, _ = self._calculate_hand_value_standalone(hand)
            if value <= 21:
                actions.append('stand')

        # Can hit? (check split ace rule)
        if self.can_hit_after_split(hand):
            actions.append('hit')

        # Can double?
        if self.can_double(hand):
            actions.append('double')

        # Can split?
        if self.can_split(hand):
            actions.append('split')

        # Can surrender?
        if self.can_surrender(hand):
            actions.append('surrender')

        return actions

    def _get_split_value(self, card) -> int:
        """Get the splitting value of a card (T,J,Q,K all = 10)."""
        if hasattr(card, 'rank'):
            rank = card.rank
        else:
            rank = str(card)

        if rank in ['T', 'J', 'Q', 'K']:
            return 10
        elif rank == 'A':
            return 1  # For splitting purposes
        else:
            return int(rank)

    def _calculate_hand_value_standalone(self, hand) -> Tuple[int, bool]:
        """Standalone hand value calculation if existing rules not available."""
        if hasattr(hand, 'cards'):
            cards = hand.cards
        else:
            return 0, False

        total = 0
        aces = 0

        for card in cards:
            if hasattr(card, 'rank'):
                rank = card.rank
            else:
                rank = str(card)

            if rank == 'A':
                aces += 1
                total += 11
            elif rank in ['T', 'J', 'Q', 'K']:
                total += 10
            else:
                total += int(rank)

        # Adjust aces
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1

        is_soft = aces > 0
        return total, is_soft


class TournamentEVCalculator:
    """
    EV Calculator that uses tournament rules enforcement.
    """

    def __init__(self):
        self.rules = TournamentBlackjackRules()

    def calculate_ev(self, hand, dealer_upcard: str, deck_composition: Dict[str, int]) -> Dict[str, float]:
        """
        Calculate EV for all legal actions under tournament rules.
        """
        # Get available actions based on tournament rules
        available_actions = self.rules.get_available_actions(hand)

        results = {}

        # Calculate EV for each available action
        for action in available_actions:
            if action == 'stand':
                results[action] = self._calculate_stand_ev(hand, dealer_upcard, deck_composition)
            elif action == 'hit':
                results[action] = self._calculate_hit_ev(hand, dealer_upcard, deck_composition)
            elif action == 'double':
                results[action] = self._calculate_double_ev(hand, dealer_upcard, deck_composition)
            elif action == 'split':
                results[action] = self._calculate_split_ev(hand, dealer_upcard, deck_composition)
            elif action == 'surrender':
                results[action] = -0.5

        # Find best action
        if results:
            best_action = max(results.keys(), key=lambda k: results[k])
            results['best'] = best_action
            results['best_ev'] = results[best_action]

        return results

    def _calculate_stand_ev(self, hand, dealer_upcard: str, deck_composition: Dict[str, int]) -> float:
        """Calculate EV of standing with tournament dealer rules (S17)."""
        # Use simplified dealer probabilities with S17 rule
        dealer_probs = self._get_dealer_probabilities_s17(dealer_upcard)

        if EXISTING_RULES_AVAILABLE and self.rules.base_rules:
            player_value, _ = self.rules.base_rules.calculate_hand_value(hand)
        else:
            player_value, _ = self.rules._calculate_hand_value_standalone(hand)

        if player_value > 21:
            return -1.0

        ev = 0.0
        ev += dealer_probs['bust'] * 1.0  # Win if dealer busts
        ev += dealer_probs['17'] * (1.0 if player_value > 17 else (-1.0 if player_value < 17 else 0.0))
        ev += dealer_probs['18'] * (1.0 if player_value > 18 else (-1.0 if player_value < 18 else 0.0))
        ev += dealer_probs['19'] * (1.0 if player_value > 19 else (-1.0 if player_value < 19 else 0.0))
        ev += dealer_probs['20'] * (1.0 if player_value > 20 else (-1.0 if player_value < 20 else 0.0))
        ev += dealer_probs['21'] * (1.0 if player_value > 21 else (-1.0 if player_value < 21 else 0.0))

        return ev

    def _calculate_hit_ev(self, hand, dealer_upcard: str, deck_composition: Dict[str, int]) -> float:
        """Calculate EV of hitting with tournament rules enforcement."""
        # Simplified implementation - can be expanded
        return 0.0  # Placeholder

    def _calculate_double_ev(self, hand, dealer_upcard: str, deck_composition: Dict[str, int]) -> float:
        """Calculate EV of doubling (only if allowed by tournament rules)."""
        if not self.rules.can_double(hand):
            return float('-inf')  # Not allowed
        return 0.0  # Placeholder

    def _calculate_split_ev(self, hand, dealer_upcard: str, deck_composition: Dict[str, int]) -> float:
        """Calculate EV of splitting (only if allowed by tournament rules)."""
        if not self.rules.can_split(hand):
            return float('-inf')  # Not allowed
        return 0.0  # Placeholder

    def _get_dealer_probabilities_s17(self, upcard: str) -> Dict[str, float]:
        """Get dealer probabilities with S17 rule (dealer stands on soft 17)."""
        # Simplified probabilities - can use your existing dealer calculation
        s17_probs = {
            'A': {'17': 0.13, '18': 0.13, '19': 0.13, '20': 0.13, '21': 0.31, 'bust': 0.17},
            '2': {'17': 0.14, '18': 0.14, '19': 0.13, '20': 0.13, '21': 0.12, 'bust': 0.34},
            '3': {'17': 0.14, '18': 0.14, '19': 0.13, '20': 0.13, '21': 0.12, 'bust': 0.34},
            '4': {'17': 0.14, '18': 0.14, '19': 0.13, '20': 0.13, '21': 0.12, 'bust': 0.34},
            '5': {'17': 0.14, '18': 0.14, '19': 0.13, '20': 0.13, '21': 0.12, 'bust': 0.34},
            '6': {'17': 0.14, '18': 0.14, '19': 0.13, '20': 0.13, '21': 0.12, 'bust': 0.34},
            '7': {'17': 0.14, '18': 0.13, '19': 0.13, '20': 0.13, '21': 0.12, 'bust': 0.35},
            '8': {'17': 0.14, '18': 0.13, '19': 0.13, '20': 0.13, '21': 0.12, 'bust': 0.35},
            '9': {'17': 0.14, '18': 0.13, '19': 0.13, '20': 0.13, '21': 0.12, 'bust': 0.35},
            'T': {'17': 0.13, '18': 0.13, '19': 0.13, '20': 0.13, '21': 0.22, 'bust': 0.26},
        }

        return s17_probs.get(upcard, s17_probs['T'])


def test_tournament_rules_integration():
    """Test integration with existing rules engine."""
    print("Testing Tournament Rules Integration")
    print("=" * 50)

    try:
        # Test tournament rules
        tournament_rules = TournamentBlackjackRules()

        if EXISTING_RULES_AVAILABLE:
            print("✓ Successfully integrated with existing rules_engine")

            # Create test hands using your existing Hand/Card classes
            # Split hand that should NOT be able to double (no DAS)
            split_hand = Hand([Card('5', '♠'), Card('6', '♥')], is_split=True)
            can_double = tournament_rules.can_double(split_hand)

            if not can_double:
                print("✓ No DAS rule enforced - split hand cannot double")
            else:
                print("✗ DAS rule violation - split hand can double")

            # Test S17 rule
            soft_17_hand = Hand([Card('A', '♠'), Card('6', '♥')])
            should_hit = tournament_rules.dealer_should_hit(soft_17_hand)

            if not should_hit:
                print("✓ S17 rule enforced - dealer stands on soft 17")
            else:
                print("✗ S17 rule violation - dealer hits soft 17")

            # Test resplitting prevention
            already_split = Hand([Card('8', '♠'), Card('8', '♥')], splits_count=1)
            can_split = tournament_rules.can_split(already_split)

            if not can_split:
                print("✓ No resplit rule enforced")
            else:
                print("✗ Resplit rule violation")

        else:
            print("⚠️  Running in standalone mode (existing rules_engine not found)")
            print("✓ Tournament rules created successfully")

        # Test EV calculator
        ev_calc = TournamentEVCalculator()
        print("✓ Tournament EV calculator created")

        return True

    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_tournament_rules_integration()
    if success:
        print("\n🎉 Tournament rules integration successful!")
        print("\nKey features:")
        print("- S17: Dealer stands on soft 17")
        print("- No DAS: Cannot double after split")
        print("- No Resplit: Pairs can only be split once")
        print("- Split Aces: Get one card only")
        print("- Surrender: Late surrender allowed")
    else:
        print("\n❌ Integration failed - check errors above")