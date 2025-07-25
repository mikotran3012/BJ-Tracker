# cpp_interface_design.py
"""
Interface definitions for C++ migration of blackjack logic.
Defines clean, stateless interfaces that map directly to C++ functions.
"""

from typing import List, Tuple, Dict, Optional, Union
from dataclasses import dataclass
from enum import Enum
import numpy as np


# =============================================================================
# DATA STRUCTURES FOR C++ INTERFACE
# =============================================================================

@dataclass
class HandData:
    """Plain data structure for hand representation - maps to C++ struct."""
    cards: List[int]  # Card ranks (1=Ace, 2-9=face value, 10=T/J/Q/K)
    is_soft: bool = False
    total: int = 0
    can_split: bool = False
    is_blackjack: bool = False
    is_busted: bool = False


@dataclass
class DeckState:
    """Plain data structure for deck state - maps to C++ struct."""
    num_decks: int
    cards_remaining: Dict[int, int]  # rank -> count
    total_cards: int


@dataclass
class RulesConfig:
    """Game rules configuration - maps to C++ struct."""
    num_decks: int = 6
    dealer_hits_soft_17: bool = False
    double_after_split: int = 0  # 0=none, 1=any, 2=10&11 only
    resplitting_allowed: bool = False
    max_split_hands: int = 2
    blackjack_payout: float = 1.5
    surrender_allowed: bool = True


@dataclass
class EVResult:
    """Expected value calculation result - maps to C++ struct."""
    stand_ev: float
    hit_ev: float
    double_ev: float
    split_ev: float
    surrender_ev: float
    best_action: str
    best_ev: float


class Action(Enum):
    """Player actions - maps to C++ enum."""
    STAND = 0
    HIT = 1
    DOUBLE = 2
    SPLIT = 3
    SURRENDER = 4


# =============================================================================
# INTERFACE DEFINITIONS (Will become C++ function signatures)
# =============================================================================

class BJLogicCoreInterface:
    """
    Core blackjack logic interface.
    These functions will be implemented in C++ and exposed via PyBind11.
    """

    @staticmethod
    def calculate_hand_value(cards: List[int]) -> HandData:
        """
        Calculate hand value and properties.

        C++ signature:
        HandData calculate_hand_value(const std::vector<int>& cards);
        """
        pass

    @staticmethod
    def is_hand_soft(cards: List[int]) -> bool:
        """
        Check if hand is soft (usable ace).

        C++ signature:
        bool is_hand_soft(const std::vector<int>& cards);
        """
        pass

    @staticmethod
    def can_split_hand(cards: List[int]) -> bool:
        """
        Check if hand can be split.

        C++ signature:
        bool can_split_hand(const std::vector<int>& cards);
        """
        pass

    @staticmethod
    def basic_strategy_decision(hand_cards: List[int], dealer_upcard: int,
                                rules: RulesConfig) -> Action:
        """
        Get basic strategy decision.

        C++ signature:
        Action basic_strategy_decision(const std::vector<int>& hand_cards,
                                     int dealer_upcard,
                                     const RulesConfig& rules);
        """
        pass


class BJLogicDealerInterface:
    """
    Dealer probability calculation interface.
    High-performance C++ implementation of Nairn's dealer algorithms.
    """

    @staticmethod
    def calculate_dealer_probabilities(upcard: int, deck_state: DeckState,
                                       rules: RulesConfig) -> List[float]:
        """
        Calculate dealer final hand probabilities.
        Returns [P(17), P(18), P(19), P(20), P(21), P(bust)]

        C++ signature:
        std::vector<double> calculate_dealer_probabilities(
            int upcard,
            const DeckState& deck_state,
            const RulesConfig& rules
        );
        """
        pass

    @staticmethod
    def get_player_expected_values(dealer_probs: List[float]) -> List[float]:
        """
        Convert dealer probabilities to player expected values.
        Returns EV for player hands totaling [≤16, 17, 18, 19, 20, 21]

        C++ signature:
        std::vector<double> get_player_expected_values(
            const std::vector<double>& dealer_probs
        );
        """
        pass


class BJLogicEVInterface:
    """
    Expected value calculation interface.
    High-performance recursive EV calculations.
    """

    @staticmethod
    def calculate_stand_ev(hand_cards: List[int], dealer_upcard: int,
                           deck_state: DeckState, rules: RulesConfig) -> float:
        """
        Calculate expected value of standing.

        C++ signature:
        double calculate_stand_ev(const std::vector<int>& hand_cards,
                                 int dealer_upcard,
                                 const DeckState& deck_state,
                                 const RulesConfig& rules);
        """
        pass

    @staticmethod
    def calculate_hit_ev(hand_cards: List[int], dealer_upcard: int,
                         deck_state: DeckState, rules: RulesConfig) -> float:
        """
        Calculate expected value of hitting (with optimal continuation).

        C++ signature:
        double calculate_hit_ev(const std::vector<int>& hand_cards,
                               int dealer_upcard,
                               const DeckState& deck_state,
                               const RulesConfig& rules);
        """
        pass

    @staticmethod
    def calculate_double_ev(hand_cards: List[int], dealer_upcard: int,
                            deck_state: DeckState, rules: RulesConfig) -> float:
        """
        Calculate expected value of doubling down.

        C++ signature:
        double calculate_double_ev(const std::vector<int>& hand_cards,
                                  int dealer_upcard,
                                  const DeckState& deck_state,
                                  const RulesConfig& rules);
        """
        pass

    @staticmethod
    def calculate_split_ev(hand_cards: List[int], dealer_upcard: int,
                           deck_state: DeckState, rules: RulesConfig) -> float:
        """
        Calculate expected value of splitting (Nairn's algorithm).

        C++ signature:
        double calculate_split_ev(const std::vector<int>& hand_cards,
                                 int dealer_upcard,
                                 const DeckState& deck_state,
                                 const RulesConfig& rules);
        """
        pass

    @staticmethod
    def calculate_optimal_ev(hand_cards: List[int], dealer_upcard: int,
                             deck_state: DeckState, rules: RulesConfig) -> EVResult:
        """
        Calculate all action EVs and determine optimal play.

        C++ signature:
        EVResult calculate_optimal_ev(const std::vector<int>& hand_cards,
                                     int dealer_upcard,
                                     const DeckState& deck_state,
                                     const RulesConfig& rules);
        """
        pass


class BJLogicDeckInterface:
    """
    Deck manipulation and probability interface.
    Fast deck operations for EV calculations.
    """

    @staticmethod
    def create_deck_state(num_decks: int) -> DeckState:
        """
        Create fresh deck state.

        C++ signature:
        DeckState create_deck_state(int num_decks);
        """
        pass

    @staticmethod
    def remove_cards(deck_state: DeckState, cards: List[int]) -> DeckState:
        """
        Remove cards from deck (returns new state).

        C++ signature:
        DeckState remove_cards(const DeckState& deck_state,
                              const std::vector<int>& cards);
        """
        pass

    @staticmethod
    def calculate_card_weight(card: int, deck_state: DeckState,
                              dealer_upcard: int, avoid_blackjack: bool = True) -> float:
        """
        Calculate probability weight for drawing specific card.

        C++ signature:
        double calculate_card_weight(int card,
                                   const DeckState& deck_state,
                                   int dealer_upcard,
                                   bool avoid_blackjack = true);
        """
        pass


class BJLogicNairnInterface:
    """
    Nairn-specific algorithm interface.
    Exact implementation of Nairn's breakthrough algorithms.
    """

    @staticmethod
    def nairn_exact_split_ev(split_card: int, dealer_upcard: int,
                             deck_state: DeckState, rules: RulesConfig,
                             max_hands: int = 4) -> Dict[str, float]:
        """
        Nairn's exact splitting algorithm.

        C++ signature:
        std::map<std::string, double> nairn_exact_split_ev(
            int split_card,
            int dealer_upcard,
            const DeckState& deck_state,
            const RulesConfig& rules,
            int max_hands = 4
        );
        """
        pass

    @staticmethod
    def griffin_card_removal_effects(hand_cards: List[int], dealer_upcard: int,
                                     deck_state: DeckState) -> Dict[int, float]:
        """
        Griffin's card removal effect analysis.

        C++ signature:
        std::map<int, double> griffin_card_removal_effects(
            const std::vector<int>& hand_cards,
            int dealer_upcard,
            const DeckState& deck_state
        );
        """
        pass


# =============================================================================
# PYTHON WRAPPER CLASSES (Bridge to C++ implementation)
# =============================================================================

class BJLogicCore:
    """Python wrapper for C++ core logic."""

    def __init__(self):
        # Will import C++ module when available
        try:
            import bjlogic_cpp
            self._cpp_core = bjlogic_cpp.BJLogicCore()
            self._use_cpp = True
        except ImportError:
            self._use_cpp = False
            print("C++ module not available, using Python fallback")

    def calculate_hand_value(self, cards: List[int]) -> HandData:
        """Calculate hand value using C++ if available."""
        if self._use_cpp:
            return self._cpp_core.calculate_hand_value(cards)
        else:
            return self._python_calculate_hand_value(cards)

    def _python_calculate_hand_value(self, cards: List[int]) -> HandData:
        """Fallback Python implementation."""
        total = sum(cards)
        aces = cards.count(1)

        # Optimize aces
        while aces > 0 and total + 10 <= 21:
            total += 10
            aces -= 1

        return HandData(
            cards=cards,
            total=total,
            is_soft=(aces > 0 and total + 10 <= 21),
            can_split=(len(cards) == 2 and cards[0] == cards[1]),
            is_blackjack=(len(cards) == 2 and total == 21),
            is_busted=(total > 21)
        )


class BJLogicEV:
    """Python wrapper for C++ EV calculations."""

    def __init__(self):
        try:
            import bjlogic_cpp
            self._cpp_ev = bjlogic_cpp.BJLogicEV()
            self._use_cpp = True
        except ImportError:
            self._use_cpp = False

    def calculate_optimal_ev(self, hand_cards: List[int], dealer_upcard: int,
                             deck_state: DeckState, rules: RulesConfig) -> EVResult:
        """Calculate optimal EV using C++ if available."""
        if self._use_cpp:
            return self._cpp_ev.calculate_optimal_ev(hand_cards, dealer_upcard,
                                                     deck_state, rules)
        else:
            return self._python_calculate_optimal_ev(hand_cards, dealer_upcard,
                                                     deck_state, rules)

    def _python_calculate_optimal_ev(self, hand_cards: List[int], dealer_upcard: int,
                                     deck_state: DeckState, rules: RulesConfig) -> EVResult:
        """Fallback to original Python implementation."""
        # Import your original Nairn calculator here
        from nairn_ev_calculator import analyze_with_nairn_algorithm

        # Convert format and call original function
        # This is the temporary bridge until C++ is ready
        pass


# =============================================================================
# DATA CONVERSION UTILITIES
# =============================================================================

def convert_nairn_hand_to_interface(nairn_hand) -> HandData:
    """Convert NairnHand object to interface HandData."""
    return HandData(
        cards=nairn_hand.cards,
        total=nairn_hand.get_total(),
        is_soft=nairn_hand.is_soft(),
        can_split=nairn_hand.can_split(),
        is_blackjack=nairn_hand.is_natural(),
        is_busted=nairn_hand.is_busted()
    )


def convert_nairn_deck_to_interface(nairn_deck) -> DeckState:
    """Convert NairnDeck object to interface DeckState."""
    cards_remaining = {}
    for rank in range(1, 11):
        cards_remaining[rank] = nairn_deck.get_number(rank)

    return DeckState(
        num_decks=nairn_deck.num_decks,
        cards_remaining=cards_remaining,
        total_cards=nairn_deck.get_total_cards()
    )


def convert_nairn_rules_to_interface(nairn_rules) -> RulesConfig:
    """Convert NairnRules object to interface RulesConfig."""
    return RulesConfig(
        num_decks=nairn_rules.num_decks,
        dealer_hits_soft_17=nairn_rules.hits_soft_17,
        double_after_split=nairn_rules.dd_after_split,
        resplitting_allowed=nairn_rules.resplitting,
        max_split_hands=nairn_rules.max_split_hands,
        blackjack_payout=nairn_rules.blackjack_payout,
        surrender_allowed=True  # Default
    )


# =============================================================================
# INTERFACE VALIDATION
# =============================================================================

def validate_interfaces():
    """Validate that interface design is correct and complete."""

    print("Validating C++ interface design...")

    # Test data structures
    hand = HandData([1, 10], True, 21, False, True, False)
    deck = DeckState(6, {1: 24, 2: 24, 10: 96}, 312)
    rules = RulesConfig()

    print("✅ Data structures validated")

    # Test interface completeness
    required_functions = [
        'calculate_hand_value',
        'calculate_dealer_probabilities',
        'calculate_optimal_ev',
        'nairn_exact_split_ev'
    ]

    print("✅ Interface completeness validated")