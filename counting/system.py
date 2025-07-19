"""
Abstract base class for card counting systems.
Provides framework for extensible counting system implementation.
"""

from abc import ABC, abstractmethod
from typing import Dict, Union


class BaseCountingSystem(ABC):
    """Abstract base class for all card counting systems."""

    def __init__(self, name: str, tag_map: Dict[str, int], decks: int = 8):
        """
        Initialize counting system.

        Args:
            name: Display name of the counting system
            tag_map: Dictionary mapping card ranks to tag values
            decks: Number of decks in the shoe
        """
        self.name = name
        self.tag_map = tag_map
        self.decks = decks
        self.running_count = 0
        self.cards_seen = 0

    def add_card(self, rank: str) -> None:
        """
        Add a card to the count.

        Args:
            rank: Card rank ('A', '2'-'9', '10', 'J', 'Q', 'K')
        """
        # Normalize rank (handle both 'T' and '10')
        normalized_rank = self._normalize_rank(rank)

        if normalized_rank in self.tag_map:
            self.running_count += self.tag_map[normalized_rank]
            self.cards_seen += 1

    def remove_card(self, rank: str) -> None:
        """
        Remove a card from the count (for undo operations).

        Args:
            rank: Card rank to remove
        """
        # Normalize rank (handle both 'T' and '10')
        normalized_rank = self._normalize_rank(rank)

        if normalized_rank in self.tag_map and self.cards_seen > 0:
            self.running_count -= self.tag_map[normalized_rank]
            self.cards_seen -= 1

    def reset(self) -> None:
        """Reset the counting system to initial state."""
        self.running_count = 0
        self.cards_seen = 0

    def get_rc(self) -> int:
        """Get the current running count."""
        return self.running_count

    def get_tc(self, cards_left: int, aces_left: int, decks: int) -> float:
        """
        Calculate true count. Base implementation uses standard RC/decks_remaining.
        Override this method in subclasses for custom TC calculations.

        Args:
            cards_left: Cards remaining in shoe
            aces_left: Aces remaining in shoe
            decks: Total decks in shoe

        Returns:
            True count as float, rounded to 2 decimal places
        """
        total_cards = decks * 52
        cards_dealt = total_cards - cards_left
        decks_remaining = max(0.5, (total_cards - cards_dealt) / 52)

        if decks_remaining <= 0:
            return 0.0

        tc = self.running_count / decks_remaining
        return round(tc, 2)

    def _normalize_rank(self, rank: str) -> str:
        """
        Normalize rank to handle both 'T' and '10' representations.

        Args:
            rank: Input rank string

        Returns:
            Normalized rank string
        """
        # Convert 'T' to '10' for consistency
        if rank == 'T':
            return '10'
        return rank

    def get_system_info(self) -> Dict[str, Union[str, int, Dict]]:
        """
        Get comprehensive information about this counting system.

        Returns:
            Dictionary containing system metadata
        """
        return {
            'name': self.name,
            'running_count': self.running_count,
            'cards_seen': self.cards_seen,
            'tag_map': self.tag_map.copy(),
            'decks': self.decks
        }

    def __str__(self) -> str:
        """String representation of the counting system."""
        return f"{self.name}(RC: {self.running_count}, Cards: {self.cards_seen})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"{self.__class__.__name__}(name='{self.name}', rc={self.running_count}, cards_seen={self.cards_seen})"