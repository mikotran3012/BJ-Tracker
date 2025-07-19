"""
RAPC (Revised Advanced Point Count) counting system implementation.
Uses specific tag values and standard TC calculation.
"""

from .system import BaseCountingSystem


class RAPCSystem(BaseCountingSystem):
    """RAPC counting system with correct tag values."""

    # RAPC tag values as specified
    RAPC_TAGS = {
        '2': 2, '3': 3, '4': 3, '5': 4, '6': 3, '7': 2,
        '8': 0, '9': -1, '10': -3, 'J': -3, 'Q': -3, 'K': -3, 'A': -4
    }

    def __init__(self, decks: int = 8):
        """
        Initialize RAPC counting system.

        Args:
            decks: Number of decks in the shoe
        """
        super().__init__("RAPC", self.RAPC_TAGS, decks)

    def get_tc(self, cards_left: int, aces_left: int, decks: int) -> float:
        """
        Calculate RAPC True Count using standard RC/decks_remaining formula.

        Args:
            cards_left: Cards remaining in shoe
            aces_left: Aces remaining in shoe (not used in RAPC TC)
            decks: Total decks in shoe

        Returns:
            True count rounded to 2 decimal places
        """
        # Calculate decks remaining
        total_cards = decks * 52
        cards_dealt = total_cards - cards_left
        decks_remaining = max(0.5, (total_cards - cards_dealt) / 52)

        if decks_remaining <= 0:
            return 0.0

        # Standard TC calculation: RC / decks_remaining
        tc = self.running_count / decks_remaining
        return round(tc, 2)

    def get_betting_tc(self, cards_left: int, aces_left: int, decks: int) -> float:
        """
        Get TC specifically for betting decisions (same as regular TC for RAPC).

        Args:
            cards_left: Cards remaining in shoe
            aces_left: Aces remaining in shoe
            decks: Total decks in shoe

        Returns:
            Betting true count
        """
        return self.get_tc(cards_left, aces_left, decks)

    def get_playing_tc(self, cards_left: int, aces_left: int, decks: int) -> float:
        """
        Get TC specifically for playing decisions (same as regular TC for RAPC).

        Args:
            cards_left: Cards remaining in shoe
            aces_left: Aces remaining in shoe
            decks: Total decks in shoe

        Returns:
            Playing true count
        """
        return self.get_tc(cards_left, aces_left, decks)