// cpp_src/bjlogic_core.hpp
/*
 * Phase 2.2: Enhanced Core with Complete Basic Strategy
 * Professional-grade blackjack logic with full strategy tables
 */

#ifndef BJLOGIC_CORE_HPP
#define BJLOGIC_CORE_HPP

#include <vector>
#include <map>
#include <string>
#include <cstdint>
#include <algorithm>
#include <numeric>

namespace bjlogic {

// =============================================================================
// DATA STRUCTURES
// =============================================================================

struct HandData {
    std::vector<int> cards;
    int total;
    bool is_soft;
    bool can_split;
    bool is_blackjack;
    bool is_busted;

    HandData() : total(0), is_soft(false), can_split(false),
                 is_blackjack(false), is_busted(false) {}
};

struct DeckState {
    int num_decks;
    std::map<int, int> cards_remaining;  // rank -> count
    int total_cards;

    DeckState(int decks = 6) : num_decks(decks), total_cards(52 * decks) {
        // Initialize standard deck
        for (int rank = 1; rank <= 9; ++rank) {
            cards_remaining[rank] = 4 * decks;
        }
        cards_remaining[10] = 16 * decks;  // 10, J, Q, K
    }
};

struct RulesConfig {
    int num_decks;
    bool dealer_hits_soft_17;
    int double_after_split;  // 0=none, 1=any, 2=10&11 only
    bool resplitting_allowed;
    int max_split_hands;
    double blackjack_payout;
    bool surrender_allowed;

    RulesConfig() : num_decks(6), dealer_hits_soft_17(false),
                    double_after_split(0), resplitting_allowed(false),
                    max_split_hands(2), blackjack_payout(1.5),
                    surrender_allowed(true) {}
};

struct EVResult {
    double stand_ev;
    double hit_ev;
    double double_ev;
    double split_ev;
    double surrender_ev;
    std::string best_action;
    double best_ev;

    EVResult() : stand_ev(-1.0), hit_ev(-1.0), double_ev(-1.0),
                 split_ev(-1.0), surrender_ev(-0.5),
                 best_action("stand"), best_ev(-1.0) {}
};

enum class Action {
    STAND = 0,
    HIT = 1,
    DOUBLE = 2,
    SPLIT = 3,
    SURRENDER = 4
};

// =============================================================================
// CORE BLACKJACK LOGIC CLASS
// =============================================================================

class BJLogicCore {
public:
    // Enhanced hand value calculation
    static HandData calculate_hand_value(const std::vector<int>& cards);

    // Additional hand analysis functions
    static bool is_hand_soft(const std::vector<int>& cards);
    static bool can_split_hand(const std::vector<int>& cards);
    static bool is_hand_busted(const std::vector<int>& cards);

    // Complete basic strategy with full lookup tables
    static Action basic_strategy_decision(const std::vector<int>& hand_cards,
                                        int dealer_upcard,
                                        const RulesConfig& rules);

    // Strategy analysis functions
    static std::string action_to_string(Action action);
    static bool is_basic_strategy_optimal(const std::vector<int>& hand_cards,
                                        int dealer_upcard,
                                        const RulesConfig& rules,
                                        Action chosen_action);
    static double get_strategy_deviation_cost(const std::vector<int>& hand_cards,
                                            int dealer_upcard,
                                            const RulesConfig& rules,
                                            Action chosen_action);

private:
    // Complete basic strategy lookup tables
    static const Action HARD_STRATEGY[18][10];   // Hard totals 5-21 vs dealer A,2-10
    static const Action SOFT_STRATEGY[10][10];   // Soft totals A,2-A,9 vs dealer A,2-10
    static const Action PAIR_STRATEGY[10][10];   // Pairs A,A-T,T vs dealer A,2-10

    // Helper functions
    static int calculate_hard_total(const std::vector<int>& cards);
    static std::pair<int, bool> calculate_optimal_total(const std::vector<int>& cards);
};

} // namespace bjlogic

#endif // BJLOGIC_CORE_HPP