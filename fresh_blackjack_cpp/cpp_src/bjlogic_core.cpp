// cpp_src/bjlogic_core.cpp
/*
 * Phase 2.2: Core blackjack logic implementation (WITHOUT strategy tables)
 * Strategy tables are now in basic_strategy.cpp to avoid duplicates
 */

#include "bjlogic_core.hpp"
#include <algorithm>
#include <cmath>

namespace bjlogic {

// =============================================================================
// CORE LOGIC IMPLEMENTATION (Hand calculations only)
// =============================================================================

HandData BJLogicCore::calculate_hand_value(const std::vector<int>& cards) {
    HandData result;
    result.cards = cards;

    if (cards.empty()) {
        return result;
    }

    // Fast calculation using single pass
    int hard_total = 0;
    int aces = 0;

    for (int card : cards) {
        hard_total += card;
        if (card == 1) aces++;
    }

    // Optimize aces (convert 1s to 11s when beneficial)
    int soft_total = hard_total;
    int aces_as_eleven = 0;

    while (aces_as_eleven < aces && soft_total + 10 <= 21) {
        soft_total += 10;
        aces_as_eleven++;
    }

    result.total = soft_total;
    result.is_soft = (aces_as_eleven > 0) && (soft_total < 21);  // Fixed logic!
    result.is_busted = (result.total > 21);
    result.is_blackjack = (cards.size() == 2 && result.total == 21);
    result.can_split = (cards.size() == 2 && cards[0] == cards[1]);

    return result;
}

bool BJLogicCore::is_hand_soft(const std::vector<int>& cards) {
    HandData hand = calculate_hand_value(cards);
    return hand.is_soft;
}

bool BJLogicCore::can_split_hand(const std::vector<int>& cards) {
    HandData hand = calculate_hand_value(cards);
    return hand.can_split;
}

bool BJLogicCore::is_hand_busted(const std::vector<int>& cards) {
    HandData hand = calculate_hand_value(cards);
    return hand.is_busted;
}

// NOTE: basic_strategy_decision and related functions are now in basic_strategy.cpp

// Helper functions
int BJLogicCore::calculate_hard_total(const std::vector<int>& cards) {
    int total = 0;
    for (int card : cards) {
        total += card;
    }
    return total;
}

std::pair<int, bool> BJLogicCore::calculate_optimal_total(const std::vector<int>& cards) {
    HandData hand = calculate_hand_value(cards);
    return {hand.total, hand.is_soft};
}

} // namespace bjlogic