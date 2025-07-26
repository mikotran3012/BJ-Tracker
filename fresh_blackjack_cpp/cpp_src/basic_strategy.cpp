// cpp_src/basic_strategy.cpp
/*
 * Phase 2.2: OFFICIAL S17 Basic Strategy
 * Based on official S17-Basic-Strategy.pdf
 */

#include "bjlogic_core.hpp"

namespace bjlogic {

// =============================================================================
// OFFICIAL S17 BASIC STRATEGY TABLES (Per S17-Basic-Strategy.pdf)
// =============================================================================

// Hard totals 5-21 vs dealer A,2,3,4,5,6,7,8,9,T
const Action BJLogicCore::HARD_STRATEGY[18][10] = {
    // Player 5-21 vs Dealer A,2,3,4,5,6,7,8,9,T
    {Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT}, // 5
    {Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT}, // 6
    {Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT}, // 7
    {Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT}, // 8
    {Action::HIT, Action::HIT, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::HIT, Action::HIT, Action::HIT, Action::HIT}, // 9
    {Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::HIT, Action::HIT}, // 10
    {Action::HIT, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE}, // 11 (CORRECTED: vs A = HIT)
    {Action::HIT, Action::HIT, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::HIT, Action::HIT, Action::HIT, Action::HIT}, // 12
    {Action::HIT, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::HIT, Action::HIT, Action::HIT, Action::HIT}, // 13
    {Action::HIT, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::HIT, Action::HIT, Action::HIT, Action::HIT}, // 14
    {Action::HIT, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::HIT, Action::HIT, Action::HIT, Action::SURRENDER}, // 15
    {Action::HIT, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::HIT, Action::HIT, Action::SURRENDER, Action::SURRENDER}, // 16
    {Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND}, // 17
    {Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND}, // 18
    {Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND}, // 19
    {Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND}, // 20
    {Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND}  // 21
};

// Soft totals A,2-A,9 vs dealer A,2,3,4,5,6,7,8,9,T (Per official PDF)
const Action BJLogicCore::SOFT_STRATEGY[10][10] = {
    // Player A,2-A,9 vs Dealer A,2,3,4,5,6,7,8,9,T
    {Action::HIT, Action::HIT, Action::HIT, Action::DOUBLE, Action::DOUBLE, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT}, // A,2 (13)
    {Action::HIT, Action::HIT, Action::HIT, Action::DOUBLE, Action::DOUBLE, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT}, // A,3 (14)
    {Action::HIT, Action::HIT, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT}, // A,4 (15)
    {Action::HIT, Action::HIT, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT}, // A,5 (16)
    {Action::HIT, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT}, // A,6 (17)
    {Action::STAND, Action::STAND, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::STAND, Action::STAND, Action::HIT, Action::HIT, Action::HIT}, // A,7 (18) CORRECTED: vs 2 = STAND
    {Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND}, // A,8 (19) CORRECTED: vs 6 = STAND
    {Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND}  // A,9 (20)
};

// Pairs A,A-T,T vs dealer A,2,3,4,5,6,7,8,9,T (Per official PDF)
const Action BJLogicCore::PAIR_STRATEGY[10][10] = {
    // Pairs A,A-T,T vs Dealer A,2,3,4,5,6,7,8,9,T
    {Action::SPLIT, Action::SPLIT, Action::SPLIT, Action::SPLIT, Action::SPLIT, Action::SPLIT, Action::SPLIT, Action::SPLIT, Action::SPLIT, Action::SPLIT}, // A,A
    {Action::HIT, Action::HIT, Action::HIT, Action::SPLIT, Action::SPLIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT}, // 2,2
    {Action::HIT, Action::HIT, Action::SPLIT, Action::SPLIT, Action::SPLIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT}, // 3,3
    {Action::HIT, Action::HIT, Action::HIT, Action::SPLIT, Action::SPLIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT}, // 4,4
    {Action::HIT, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::HIT, Action::HIT}, // 5,5 (treat as 10)
    {Action::HIT, Action::SPLIT, Action::SPLIT, Action::SPLIT, Action::SPLIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT}, // 6,6
    {Action::HIT, Action::SPLIT, Action::SPLIT, Action::SPLIT, Action::SPLIT, Action::SPLIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT}, // 7,7
    {Action::SPLIT, Action::SPLIT, Action::SPLIT, Action::SPLIT, Action::SPLIT, Action::SPLIT, Action::SPLIT, Action::SPLIT, Action::SPLIT, Action::SPLIT}, // 8,8
    {Action::STAND, Action::SPLIT, Action::SPLIT, Action::SPLIT, Action::SPLIT, Action::STAND, Action::SPLIT, Action::SPLIT, Action::STAND, Action::STAND}, // 9,9
    {Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND}  // T,T
};

// =============================================================================
// ENHANCED BASIC STRATEGY IMPLEMENTATION
// =============================================================================

Action BJLogicCore::basic_strategy_decision(const std::vector<int>& hand_cards,
                                          int dealer_upcard,
                                          const RulesConfig& rules) {
    if (hand_cards.size() < 2) return Action::HIT;

    HandData hand = calculate_hand_value(hand_cards);

    // Adjust dealer upcard index (1-based to 0-based, Ace=1 -> index 0)
    int dealer_idx = (dealer_upcard == 1) ? 0 : dealer_upcard - 1;
    if (dealer_idx < 0 || dealer_idx >= 10) dealer_idx = 9; // Default to 10

    // FIRST: Check for pair splitting (only on initial 2 cards)
    if (hand.can_split && rules.resplitting_allowed && hand_cards.size() == 2) {
        int pair_card = hand_cards[0];
        int pair_idx = (pair_card == 1) ? 0 : pair_card - 1;
        if (pair_idx >= 0 && pair_idx < 10) {
            Action split_action = PAIR_STRATEGY[pair_idx][dealer_idx];
            if (split_action == Action::SPLIT) {
                return Action::SPLIT;
            }
            // For 5,5 vs 5 -> should return DOUBLE from pair table
            if (split_action == Action::DOUBLE) {
                if (hand_cards.size() == 2) {
                    return Action::DOUBLE;
                }
            }
        }
    }

    // SECOND: Soft hand strategy (hand has ace counting as 11)
    if (hand.is_soft && hand.total >= 13 && hand.total <= 20) {
        int soft_idx = hand.total - 13;  // A,2(13) -> index 0, A,9(20) -> index 7
        if (soft_idx >= 0 && soft_idx < 8) {
            Action soft_action = SOFT_STRATEGY[soft_idx][dealer_idx];

            // Check if doubling is allowed
            if (soft_action == Action::DOUBLE) {
                if (hand_cards.size() == 2 ||
                    (rules.double_after_split > 0 && hand_cards.size() == 2)) {
                    return Action::DOUBLE;
                } else {
                    return Action::HIT;
                }
            }
            return soft_action;
        }
    }

    // THIRD: Hard hand strategy
    if (hand.total >= 5 && hand.total <= 21) {
        int hard_idx = hand.total - 5;
        if (hard_idx >= 0 && hard_idx < 18) {
            Action hard_action = HARD_STRATEGY[hard_idx][dealer_idx];

            // Check surrender rules
            if (hard_action == Action::SURRENDER) {
                if (rules.surrender_allowed && hand_cards.size() == 2) {
                    return Action::SURRENDER;
                } else {
                    return Action::HIT;
                }
            }

            // Check doubling rules
            if (hard_action == Action::DOUBLE) {
                if (hand_cards.size() == 2 ||
                    (rules.double_after_split > 0 && hand_cards.size() == 2)) {
                    return Action::DOUBLE;
                } else {
                    return Action::HIT;
                }
            }

            return hard_action;
        }
    }

    // Default fallback
    return (hand.total < 17) ? Action::HIT : Action::STAND;
}

// =============================================================================
// STRATEGY ANALYSIS FUNCTIONS
// =============================================================================

std::string BJLogicCore::action_to_string(Action action) {
    switch (action) {
        case Action::STAND: return "stand";
        case Action::HIT: return "hit";
        case Action::DOUBLE: return "double";
        case Action::SPLIT: return "split";
        case Action::SURRENDER: return "surrender";
        default: return "unknown";
    }
}

bool BJLogicCore::is_basic_strategy_optimal(const std::vector<int>& hand_cards,
                                          int dealer_upcard,
                                          const RulesConfig& rules,
                                          Action chosen_action) {
    Action optimal_action = basic_strategy_decision(hand_cards, dealer_upcard, rules);
    return chosen_action == optimal_action;
}

double BJLogicCore::get_strategy_deviation_cost(const std::vector<int>& hand_cards,
                                               int dealer_upcard,
                                               const RulesConfig& rules,
                                               Action chosen_action) {
    Action optimal_action = basic_strategy_decision(hand_cards, dealer_upcard, rules);

    if (chosen_action == optimal_action) {
        return 0.0;  // No deviation cost
    }

    // Rough estimates for common deviations
    if (optimal_action == Action::STAND && chosen_action == Action::HIT) {
        return -0.05;
    }
    if (optimal_action == Action::HIT && chosen_action == Action::STAND) {
        return -0.03;
    }
    if (optimal_action == Action::DOUBLE && chosen_action == Action::HIT) {
        return -0.02;
    }

    return -0.04;  // General deviation penalty
}

} // namespace bjlogic