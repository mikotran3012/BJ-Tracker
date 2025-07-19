"""
Count Manager - Manages all active counting systems.
Provides unified API for UI interaction and system management.
"""

from typing import List, Tuple, Optional, Union
from .system import BaseCountingSystem
from .rapc import RAPCSystem
from .uapc import UAPCSystem


class CountManager:
    """Manages multiple counting systems and provides unified API."""

    def __init__(self, decks: int = 8):
        """
        Initialize CountManager with default systems.

        Args:
            decks: Number of decks in the shoe
        """
        self.decks = decks
        self.systems: List[BaseCountingSystem] = []

        # Initialize default systems
        self._initialize_default_systems()

    def _initialize_default_systems(self) -> None:
        """Initialize RAPC and UAPC systems by default."""
        self.systems = [
            RAPCSystem(self.decks),
            UAPCSystem(self.decks)
        ]

    def add_card(self, rank: str) -> None:
        """
        Add a card to all active counting systems.

        Args:
            rank: Card rank ('A', '2'-'9', '10', 'J', 'Q', 'K', 'T')
        """
        for system in self.systems:
            system.add_card(rank)

    def remove_card(self, rank: str) -> None:
        """
        Remove a card from all active counting systems (for undo).

        Args:
            rank: Card rank to remove
        """
        for system in self.systems:
            system.remove_card(rank)

    def reset(self) -> None:
        """Reset all counting systems to initial state."""
        for system in self.systems:
            system.reset()

    def set_decks(self, decks: int) -> None:
        """
        Update deck count for all systems and reset counts.

        Args:
            decks: New number of decks
        """
        self.decks = decks
        for system in self.systems:
            system.decks = decks
        self.reset()

    def get_counts(self, cards_left: int, aces_left: int, decks: int) -> List[Tuple[str, int, float]]:
        """
        Get counts from all active systems for UI display.

        Args:
            cards_left: Cards remaining in shoe
            aces_left: Aces remaining in shoe
            decks: Total decks in shoe

        Returns:
            List of tuples: (system_name, running_count, true_count)
        """
        counts = []
        for system in self.systems:
            rc = system.get_rc()
            tc = system.get_tc(cards_left, aces_left, decks)
            counts.append((system.name, rc, tc))
        return counts

    def get_system_by_name(self, name: str) -> Optional[BaseCountingSystem]:
        """
        Get a specific counting system by name.

        Args:
            name: Name of the counting system

        Returns:
            The counting system if found, None otherwise
        """
        for system in self.systems:
            if system.name == name:
                return system
        return None

    def get_system_by_index(self, index: int) -> Optional[BaseCountingSystem]:
        """
        Get a counting system by its index.

        Args:
            index: Index of the system

        Returns:
            The counting system if index is valid, None otherwise
        """
        if 0 <= index < len(self.systems):
            return self.systems[index]
        return None

    def replace_system(self, idx: int, system_instance: BaseCountingSystem) -> bool:
        """
        Replace a counting system at the specified index.
        Useful for user customization in the future.

        Args:
            idx: Index of system to replace
            system_instance: New counting system instance

        Returns:
            True if replacement successful, False otherwise
        """
        if 0 <= idx < len(self.systems):
            # Update deck count to match manager
            system_instance.decks = self.decks
            self.systems[idx] = system_instance
            return True
        return False

    def add_system(self, system_instance: BaseCountingSystem) -> None:
        """
        Add a new counting system to the manager.

        Args:
            system_instance: Counting system to add
        """
        system_instance.decks = self.decks
        self.systems.append(system_instance)

    def remove_system(self, idx: int) -> bool:
        """
        Remove a counting system by index.

        Args:
            idx: Index of system to remove

        Returns:
            True if removal successful, False otherwise
        """
        if 0 <= idx < len(self.systems):
            self.systems.pop(idx)
            return True
        return False

    def get_system_count(self) -> int:
        """Get the number of active counting systems."""
        return len(self.systems)

    def get_all_systems(self) -> List[BaseCountingSystem]:
        """Get a copy of all active systems."""
        return self.systems.copy()

    def get_detailed_counts(self, cards_left: int, aces_left: int, decks: int) -> List[dict]:
        """
        Get detailed count information for all systems.

        Args:
            cards_left: Cards remaining in shoe
            aces_left: Aces remaining in shoe
            decks: Total decks in shoe

        Returns:
            List of dictionaries with detailed system information
        """
        detailed = []
        for system in self.systems:
            info = system.get_system_info()
            tc = system.get_tc(cards_left, aces_left, decks)

            detail = {
                'name': info['name'],
                'running_count': info['running_count'],
                'true_count': tc,
                'cards_seen': info['cards_seen'],
                'system_type': system.__class__.__name__
            }

            # Add UAPC-specific ace adjustment info if available
            if hasattr(system, 'get_ace_adjustment_info'):
                detail['ace_adjustment'] = system.get_ace_adjustment_info(aces_left, decks)

            detailed.append(detail)

        return detailed

    def simulate_cards(self, cards: List[str]) -> List[Tuple[str, int, float]]:
        """
        Simulate adding cards and return final counts without affecting actual state.
        Useful for testing and analysis.

        Args:
            cards: List of card ranks to simulate

        Returns:
            List of final counts: (system_name, final_rc, estimated_tc)
        """
        # Save current state
        original_states = []
        for system in self.systems:
            original_states.append({
                'rc': system.running_count,
                'cards_seen': system.cards_seen
            })

        # Simulate cards
        for card in cards:
            self.add_card(card)

        # Get simulated results (using rough estimates for TC)
        simulated_counts = []
        for system in self.systems:
            # Rough TC estimate (assumes average penetration)
            estimated_decks_left = max(0.5, self.decks - (system.cards_seen / 52))
            estimated_tc = system.running_count / estimated_decks_left
            simulated_counts.append((system.name, system.running_count, round(estimated_tc, 2)))

        # Restore original state
        for system, original in zip(self.systems, original_states):
            system.running_count = original['rc']
            system.cards_seen = original['cards_seen']

        return simulated_counts

    def __str__(self) -> str:
        """String representation of the count manager."""
        system_names = [system.name for system in self.systems]
        return f"CountManager({self.get_system_count()} systems: {', '.join(system_names)})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"CountManager(decks={self.decks}, systems={len(self.systems)})"