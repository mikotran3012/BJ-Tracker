"""
UAPC (Universal Advanced Point Count) counting system implementation.
Uses specific tag values and ace-corrected TC calculation logic.
"""

from .system import BaseCountingSystem


class UAPCSystem(BaseCountingSystem):
    """UAPC counting system with ace-corrected True Count calculation."""

    # UAPC tag values as specified
    UAPC_TAGS = {
        'A': 0, '2': 1, '3': 2, '4': 2, '5': 3, '6': 2, '7': 2,
        '8': 1, '9': -1, '10': -3, 'J': -3, 'Q': -3, 'K': -3
    }

    def __init__(self, decks: int = 8):
        """
        Initialize UAPC counting system.

        Args:
            decks: Number of decks in the shoe
        """
        super().__init__("UAPC", self.UAPC_TAGS, decks)

    def get_tc(self, cards_left: int, aces_left: int, decks: int) -> float:
        """
        Calculate UAPC True Count using ace-corrected formula.

        UAPC TC Formula:
        1. aces_seen = (decks * 4) - aces_left
        2. adjusted_rc = rc - (3 * aces_seen)
        3. half_decks_remaining = (decks - cards_seen / 52) * 2
        4. tc = adjusted_rc / half_decks_remaining (avoid division by zero)
        5. final_tc = tc + 6

        Args:
            cards_left: Cards remaining in shoe
            aces_left: Aces remaining in shoe
            decks: Total decks in shoe

        Returns:
            Ace-corrected true count rounded to 2 decimal places
        """
        # Step 1: Calculate aces seen
        total_aces = decks * 4
        aces_seen = total_aces - aces_left

        # Step 2: Adjust running count for aces
        adjusted_rc = self.running_count - (3 * aces_seen)

        # Step 3: Calculate half-decks remaining
        total_cards = decks * 52
        cards_dealt = total_cards - cards_left
        decks_remaining = max(0.25, (total_cards - cards_dealt) / 52)  # Minimum 0.25 decks
        half_decks_remaining = decks_remaining * 2

        # Step 4: Calculate TC (avoid division by zero)
        if half_decks_remaining <= 0:
            tc = 0.0
        else:
            tc = adjusted_rc / half_decks_remaining

        # Step 5: Add the constant +6
        final_tc = tc + 6

        return round(final_tc, 2)

    def get_betting_tc(self, cards_left: int, aces_left: int, decks: int) -> float:
        """
        Get TC specifically for betting decisions (uses full UAPC calculation).

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
        Get TC specifically for playing decisions (uses full UAPC calculation).

        Args:
            cards_left: Cards remaining in shoe
            aces_left: Aces remaining in shoe
            decks: Total decks in shoe

        Returns:
            Playing true count
        """
        return self.get_tc(cards_left, aces_left, decks)

    def get_ace_adjustment_info(self, aces_left: int, decks: int) -> dict:
        """
        Get detailed information about the ace adjustment calculation.
        Useful for debugging and understanding the UAPC system.

        Args:
            aces_left: Aces remaining in shoe
            decks: Total decks in shoe

        Returns:
            Dictionary with ace adjustment details
        """
        total_aces = decks * 4
        aces_seen = total_aces - aces_left
        adjustment = 3 * aces_seen
        adjusted_rc = self.running_count - adjustment

        return {
            'total_aces': total_aces,
            'aces_left': aces_left,
            'aces_seen': aces_seen,
            'ace_adjustment': adjustment,
            'original_rc': self.running_count,
            'adjusted_rc': adjusted_rc
        }