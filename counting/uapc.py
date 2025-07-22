"""
UAPC (Uston Advanced Point Count) counting system implementation.
Uses specific tag values and corrected ace-adjusted TC calculation logic.
"""

from .system import BaseCountingSystem


class UAPCSystem(BaseCountingSystem):
    """UAPC counting system with corrected Ace-adjusted True Count calculation."""

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
        self.aces_seen = 0  # Track aces separately for accurate calculation

    def add_card(self, rank: str) -> None:
        """
        Add a card to the count and track aces separately.

        Args:
            rank: Card rank ('A', '2'-'9', '10', 'J', 'Q', 'K')
        """
        # Call parent method for running count
        super().add_card(rank)

        # Track aces separately for true count calculation
        normalized_rank = self._normalize_rank(rank)
        if normalized_rank == 'A':
            self.aces_seen += 1

    def remove_card(self, rank: str) -> None:
        """
        Remove a card from the count (for undo operations).

        Args:
            rank: Card rank to remove
        """
        # Call parent method for running count
        super().remove_card(rank)

        # Update ace tracking
        normalized_rank = self._normalize_rank(rank)
        if normalized_rank == 'A' and self.aces_seen > 0:
            self.aces_seen -= 1

    def reset(self) -> None:
        """Reset the counting system to initial state."""
        super().reset()
        self.aces_seen = 0

    def get_tc(self, cards_left: int, aces_left: int, decks: int) -> float:
        """
        Calculate UAPC True Count using corrected ace-adjusted formula.

        CORRECTED UAPC TC Formula:
        Final True Count = (Running Count + Ace Adjustment) ÷ Remaining Half-Decks
        Where:
        - Ace Adjustment = (Aces Remaining) - (4 × Remaining Decks)
        - Aces Remaining = (Total Decks × 4) - Aces Seen
        - Remaining Half-Decks = Remaining Decks × 2

        Args:
            cards_left: Cards remaining in shoe
            aces_left: Aces remaining in shoe (used for validation if needed)
            decks: Total decks in shoe

        Returns:
            Ace-adjusted true count rounded to 2 decimal places
        """
        # Calculate remaining decks
        total_cards = decks * 52
        cards_dealt = total_cards - cards_left
        remaining_decks = max(0.25, (total_cards - cards_dealt) / 52)  # Minimum 0.25 decks

        # Calculate aces remaining using our internal tracking
        # (This is more accurate than relying on the aces_left parameter)
        aces_remaining = (decks * 4) - self.aces_seen

        # Calculate ace adjustment
        expected_aces = 4 * remaining_decks
        ace_adjustment = aces_remaining - expected_aces

        # Calculate adjusted running count
        adjusted_running_count = self.running_count + ace_adjustment

        # Calculate remaining half-decks
        remaining_half_decks = remaining_decks * 2

        # Calculate true count (avoid division by zero)
        if remaining_half_decks <= 0:
            return 0.0

        true_count = adjusted_running_count / remaining_half_decks

        return round(true_count, 2)

    def get_betting_tc(self, cards_left: int, aces_left: int, decks: int) -> float:
        """
        Get TC specifically for betting decisions (uses corrected UAPC calculation).

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
        Get TC specifically for playing decisions (uses corrected UAPC calculation).

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
            aces_left: Aces remaining in shoe (for validation)
            decks: Total decks in shoe

        Returns:
            Dictionary with ace adjustment details
        """
        # Calculate remaining decks (simplified for info purposes)
        total_cards = decks * 52
        estimated_cards_dealt = (decks * 4 - aces_left) * 13  # Rough estimate
        remaining_decks = max(0.25, (total_cards - estimated_cards_dealt) / 52)

        aces_remaining = (decks * 4) - self.aces_seen
        expected_aces = 4 * remaining_decks
        ace_adjustment = aces_remaining - expected_aces

        return {
            'total_aces': decks * 4,
            'aces_seen': self.aces_seen,
            'aces_remaining': aces_remaining,
            'expected_aces': expected_aces,
            'ace_adjustment': ace_adjustment,
            'original_rc': self.running_count,
            'adjusted_rc': self.running_count + ace_adjustment,
            'remaining_decks': remaining_decks,
            'remaining_half_decks': remaining_decks * 2
        }

    def validate_calculation(self, running_count: int, aces_seen: int, remaining_decks: float, total_decks: int = 8) -> float:
        """
        Validation method to test the UAPC calculation with specific inputs.

        Test case from requirements:
        - runningCount = 18
        - acesSeen = 10
        - remainingDecks = 3.0
        - totalDecks = 8
        Expected: (18 + ((32-10) - 12)) / 6 = (18 + 10) / 6 = 4.67

        Args:
            running_count: Running count to test
            aces_seen: Number of aces seen
            remaining_decks: Decks remaining in shoe
            total_decks: Total decks in shoe

        Returns:
            Calculated true count
        """
        aces_remaining = (total_decks * 4) - aces_seen
        expected_aces = 4 * remaining_decks
        ace_adjustment = aces_remaining - expected_aces
        adjusted_running_count = running_count + ace_adjustment
        remaining_half_decks = remaining_decks * 2

        if remaining_half_decks == 0:
            return 0.0

        return round(adjusted_running_count / remaining_half_decks, 2)

    def get_system_info(self) -> dict:
        """
        Get comprehensive information about this counting system.

        Returns:
            Dictionary containing system metadata including ace tracking
        """
        base_info = super().get_system_info()
        base_info['aces_seen'] = self.aces_seen
        base_info['system_type'] = 'Ace-Adjusted'
        return base_info