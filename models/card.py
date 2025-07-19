# models/card.py
"""
Data models for the Blackjack Tracker application.
"""

from dataclasses import dataclass
from typing import Tuple, List
from datetime import datetime

# Type aliases
Card = Tuple[str, str]  # (rank, suit)


@dataclass
class Counts:
    """Container for all counting system results."""
    rc: int = 0  # Running count
    tc: float = 0.0  # True count
    irc: int = 0  # Illustrious 18 running count (if different)
    ace_count: int = 0  # Side count of aces
    five_count: int = 0  # Side count of fives


@dataclass
class HandRecord:
    """Record of a single hand for session tracking."""
    bet_size: int
    result: str  # 'win', 'lose', 'push', 'blackjack', 'bust'
    true_count: float
    timestamp: datetime
    dealer_upcard: str
    player_total: int
    dealer_total: int


@dataclass
class SessionSummary:
    """Summary statistics for a complete session."""
    total_profit: float
    hands_played: int
    avg_hands_per_hour: float
    win_rate: float
    bust_rate: float
    max_bet: int
    min_bet: int
    session_duration: float  # in hours
    start_time: datetime
    end_time: datetime
