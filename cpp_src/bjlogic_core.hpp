// bjlogic_core.hpp
/*
 * Core blackjack logic implementation in C++
 * High-performance hand calculations and basic strategy
 * Based on John Nairn's algorithms with optimizations
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
// CORE BLACKJACK LOGIC
// =============================================================================

class BJLogicCore {
public:
    // Hand value calculations (optimized for speed)
    static HandData calculate_hand_value(const std::vector<int>& cards);
    static bool is_hand_soft(const std::vector<int>& cards);
    static bool can_split_hand(const std::vector<int>& cards);
    static bool is_hand_busted(const std::vector<int>& cards);

    // Basic strategy (lookup table implementation)
    static Action basic_strategy_decision(const std::vector<int>& hand_cards,
                                        int dealer_upcard,
                                        const RulesConfig& rules);

private:
    // Basic strategy lookup tables (compiled into binary)
    static const Action HARD_STRATEGY[18][10];   // Hard totals 5-21 vs dealer 1-10
    static const Action SOFT_STRATEGY[10][10];   // Soft totals A,A-A,9 vs dealer 1-10
    static const Action PAIR_STRATEGY[10][10];   // Pairs A,A-T,T vs dealer 1-10

    // Helper functions
    static int calculate_hard_total(const std::vector<int>& cards);
    static std::pair<int, bool> calculate_optimal_total(const std::vector<int>& cards);
};

// =============================================================================
// DEALER PROBABILITY ENGINE
// =============================================================================

class BJLogicDealer {
public:
    // High-performance dealer probability calculation
    static std::vector<double> calculate_dealer_probabilities(
        int upcard,
        const DeckState& deck_state,
        const RulesConfig& rules
    );

    // Convert dealer probabilities to player expected values
    static std::vector<double> get_player_expected_values(
        const std::vector<double>& dealer_probs
    );

private:
    // Recursive dealer hitting with memoization
    static void hit_dealer_recursive(
        int current_total,
        int aces_as_eleven,
        const DeckState& deck_state,
        const RulesConfig& rules,
        double current_probability,
        std::vector<double>& probabilities
    );

    // Memoization cache for dealer calculations
    static std::map<uint64_t, std::vector<double>> dealer_cache;
    static uint64_t generate_cache_key(int upcard, const DeckState& deck_state);

    // Optimized probability calculation with conditional logic
    static double calculate_card_probability(
        int card,
        const DeckState& deck_state,
        int dealer_upcard,
        bool avoid_blackjack = true
    );
};

// =============================================================================
// EXPECTED VALUE CALCULATOR
// =============================================================================

class BJLogicEV {
public:
    // Core EV calculations (performance-critical)
    static double calculate_stand_ev(
        const std::vector<int>& hand_cards,
        int dealer_upcard,
        const DeckState& deck_state,
        const RulesConfig& rules
    );

    static double calculate_hit_ev(
        const std::vector<int>& hand_cards,
        int dealer_upcard,
        const DeckState& deck_state,
        const RulesConfig& rules
    );

    static double calculate_double_ev(
        const std::vector<int>& hand_cards,
        int dealer_upcard,
        const DeckState& deck_state,
        const RulesConfig& rules
    );

    static double calculate_split_ev(
        const std::vector<int>& hand_cards,
        int dealer_upcard,
        const DeckState& deck_state,
        const RulesConfig& rules
    );

    // Master function that calculates all EVs
    static EVResult calculate_optimal_ev(
        const std::vector<int>& hand_cards,
        int dealer_upcard,
        const DeckState& deck_state,
        const RulesConfig& rules
    );

private:
    // Memoization for recursive EV calculations
    static std::map<uint64_t, double> ev_cache;
    static uint64_t generate_ev_cache_key(
        const std::vector<int>& hand_cards,
        int dealer_upcard,
        const DeckState& deck_state
    );

    // Helper functions for optimal play recursion
    static double recursive_hit_ev(
        std::vector<int> hand_cards,
        int dealer_upcard,
        DeckState deck_state,
        const RulesConfig& rules,
        int depth = 0
    );
};

// =============================================================================
// DECK OPERATIONS
// =============================================================================

class BJLogicDeck {
public:
    // Fast deck manipulation
    static DeckState create_deck_state(int num_decks);
    static DeckState remove_cards(const DeckState& deck_state,
                                 const std::vector<int>& cards);
    static DeckState restore_cards(const DeckState& deck_state,
                                  const std::vector<int>& cards);

    // Probability calculations
    static double calculate_card_weight(
        int card,
        const DeckState& deck_state,
        int dealer_upcard,
        bool avoid_blackjack = true
    );

    // Utility functions
    static bool can_remove_cards(const DeckState& deck_state,
                                const std::vector<int>& cards);
    static int get_cards_remaining(const DeckState& deck_state, int rank);

private:
    // Optimized card counting
    static void update_deck_counts(DeckState& deck_state,
                                  const std::vector<int>& cards,
                                  bool remove);
};

// =============================================================================
// NAIRN'S EXACT ALGORITHMS
// =============================================================================

class BJLogicNairn {
public:
    // Nairn's exact splitting algorithm (breakthrough implementation)
    static std::map<std::string, double> nairn_exact_split_ev(
        int split_card,
        int dealer_upcard,
        const DeckState& deck_state,
        const RulesConfig& rules,
        int max_hands = 4
    );

    // Griffin's card removal effects
    static std::map<int, double> griffin_card_removal_effects(
        const std::vector<int>& hand_cards,
        int dealer_upcard,
        const DeckState& deck_state
    );

    // Combinatorial caching system (Nairn's Tj array)
    static uint64_t calculate_combinatorial_address(
        const std::vector<int>& removed_cards,
        int max_size
    );

private:
    // Exact hand enumeration (replaces 11,000-year recursive method)
    static double enumerate_split_hands(
        int split_card,
        int dealer_upcard,
        const DeckState& deck_state,
        const RulesConfig& rules,
        int current_hands,
        int max_hands
    );

    // Combinatorial coefficient calculation
    static uint64_t calculate_tj(int j, int x);

    // Pre-computed combinatorial cache
    static std::vector<std::vector<uint64_t>> tj_cache;
    static void initialize_tj_cache(int max_size = 23);
};

} // namespace bjlogic

#endif // BJLOGIC_CORE_HPP

// =============================================================================
// IMPLEMENTATION FILE
// =============================================================================

// bjlogic_core.cpp
#include "bjlogic_core.hpp"
#include <algorithm>
#include <cmath>
#include <cassert>
#include <unordered_set>

namespace bjlogic {

// =============================================================================
// STATIC DATA INITIALIZATION
// =============================================================================

// Basic strategy lookup tables (optimized for memory access)
const Action BJLogicCore::HARD_STRATEGY[18][10] = {
    // Player 5-21 vs Dealer A,2,3,4,5,6,7,8,9,T
    {Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT}, // 5
    {Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT}, // 6
    {Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT}, // 7
    {Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT, Action::HIT}, // 8
    {Action::HIT, Action::HIT, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::HIT, Action::HIT, Action::HIT, Action::HIT}, // 9
    {Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::HIT, Action::HIT}, // 10
    {Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::DOUBLE, Action::HIT}, // 11
    {Action::HIT, Action::HIT, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::HIT, Action::HIT, Action::HIT, Action::HIT}, // 12
    {Action::HIT, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::HIT, Action::HIT, Action::HIT, Action::HIT}, // 13
    {Action::HIT, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::HIT, Action::HIT, Action::HIT, Action::HIT}, // 14
    {Action::HIT, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::HIT, Action::HIT, Action::HIT, Action::HIT}, // 15
    {Action::HIT, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::HIT, Action::HIT, Action::HIT, Action::HIT}, // 16
    {Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND}, // 17
    {Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND}, // 18
    {Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND}, // 19
    {Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND}, // 20
    {Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND, Action::STAND}  // 21
};

// Initialize static members
std::map<uint64_t, std::vector<double>> BJLogicDealer::dealer_cache;
std::map<uint64_t, double> BJLogicEV::ev_cache;
std::vector<std::vector<uint64_t>> BJLogicNairn::tj_cache;

// =============================================================================
// CORE LOGIC IMPLEMENTATION
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
    result.is_soft = (aces_as_eleven > 0);
    result.is_busted = (result.total > 21);
    result.is_blackjack = (cards.size() == 2 && result.total == 21);
    result.can_split = (cards.size() == 2 && cards[0] == cards[1]);

    return result;
}

Action BJLogicCore::basic_strategy_decision(const std::vector<int>& hand_cards,
                                          int dealer_upcard,
                                          const RulesConfig& rules) {
    if (hand_cards.size() < 2) return Action::HIT;

    HandData hand = calculate_hand_value(hand_cards);

    // Adjust dealer upcard index (1-based to 0-based)
    int dealer_idx = (dealer_upcard == 1) ? 0 : dealer_upcard - 1;
    if (dealer_idx < 0 || dealer_idx >= 10) dealer_idx = 9; // Default to 10

    // Check for pair splitting first
    if (hand.can_split && rules.resplitting_allowed) {
        int pair_idx = (hand_cards[0] == 1) ? 0 : hand_cards[0] - 1;
        if (pair_idx >= 0 && pair_idx < 10) {
            return PAIR_STRATEGY[pair_idx][dealer_idx];
        }
    }

    // Soft hand strategy
    if (hand.is_soft && hand.total >= 13 && hand.total <= 21) {
        int soft_idx = hand.total - 13;  // A,2 through A,9
        if (soft_idx >= 0 && soft_idx < 10) {
            return SOFT_STRATEGY[soft_idx][dealer_idx];
        }
    }

    // Hard hand strategy
    if (hand.total >= 5 && hand.total <= 21) {
        int hard_idx = hand.total - 5;
        if (hard_idx >= 0 && hard_idx < 18) {
            return HARD_STRATEGY[hard_idx][dealer_idx];
        }
    }

    // Default action
    return (hand.total < 17) ? Action::HIT : Action::STAND;
}

// =============================================================================
// DEALER PROBABILITY ENGINE IMPLEMENTATION
// =============================================================================

std::vector<double> BJLogicDealer::calculate_dealer_probabilities(
    int upcard,
    const DeckState& deck_state,
    const RulesConfig& rules) {

    // Check cache first
    uint64_t cache_key = generate_cache_key(upcard, deck_state);
    auto cache_it = dealer_cache.find(cache_key);
    if (cache_it != dealer_cache.end()) {
        return cache_it->second;
    }

    // Initialize probabilities: [17, 18, 19, 20, 21, bust]
    std::vector<double> probabilities(6, 0.0);

    // Start recursive calculation
    int initial_aces = (upcard == 1) ? 1 : 0;
    hit_dealer_recursive(upcard, initial_aces, deck_state, rules, 1.0, probabilities);

    // Handle dealer blackjack conditioning
    if (upcard == 1 || upcard == 10) {
        int needed_card = (upcard == 1) ? 10 : 1;
        double bj_prob = calculate_card_probability(needed_card, deck_state, upcard, false);

        // Remove blackjack probability and renormalize
        probabilities[4] -= bj_prob;  // Remove from 21 count

        double total_prob = std::accumulate(probabilities.begin(), probabilities.end(), 0.0);
        if (total_prob > 0) {
            for (double& prob : probabilities) {
                prob /= total_prob;
            }
        }
    }

    // Cache the result
    dealer_cache[cache_key] = probabilities;
    return probabilities;
}

void BJLogicDealer::hit_dealer_recursive(
    int current_total,
    int aces_as_eleven,
    const DeckState& deck_state,
    const RulesConfig& rules,
    double current_probability,
    std::vector<double>& probabilities) {

    // Check if dealer must stand
    bool must_stand = false;
    if (current_total >= 17) {
        if (current_total > 17 || !rules.dealer_hits_soft_17 || aces_as_eleven == 0) {
            must_stand = true;
        }
    }

    if (must_stand) {
        // Dealer stands - record final total
        if (current_total > 21) {
            probabilities[5] += current_probability;  // Bust
        } else {
            int index = current_total - 17;  // 17->0, 18->1, etc.
            if (index >= 0 && index < 5) {
                probabilities[index] += current_probability;
            }
        }
        return;
    }

    // Dealer must hit - try each possible card
    for (int card = 1; card <= 10; ++card) {
        auto it = deck_state.cards_remaining.find(card);
        if (it == deck_state.cards_remaining.end() || it->second <= 0) continue;

        double card_prob = static_cast<double>(it->second) / deck_state.total_cards;
        double new_probability = current_probability * card_prob;

        if (new_probability < 1e-10) continue;  // Skip negligible probabilities

        // Calculate new hand state
        int new_total = current_total + card;
        int new_aces_as_eleven = aces_as_eleven;

        if (card == 1) {
            // New ace - can it be eleven?
            if (new_total + 10 <= 21) {
                new_total += 10;
                new_aces_as_eleven++;
            }
        } else if (new_total > 21 && new_aces_as_eleven > 0) {
            // Convert an ace from 11 to 1
            new_total -= 10;
            new_aces_as_eleven--;
        }

        // Create new deck state
        DeckState new_deck = deck_state;
        new_deck.cards_remaining[card]--;
        new_deck.total_cards--;

        // Recurse
        hit_dealer_recursive(new_total, new_aces_as_eleven, new_deck, rules,
                           new_probability, probabilities);
    }
}

uint64_t BJLogicDealer::generate_cache_key(int upcard, const DeckState& deck_state) {
    // Simple hash combining upcard and deck composition
    uint64_t key = static_cast<uint64_t>(upcard);
    for (const auto& pair : deck_state.cards_remaining) {
        key = key * 31 + pair.first * 1000 + pair.second;
    }
    return key;
}

double BJLogicDealer::calculate_card_probability(
    int card,
    const DeckState& deck_state,
    int dealer_upcard,
    bool avoid_blackjack) {

    auto it = deck_state.cards_remaining.find(card);
    if (it == deck_state.cards_remaining.end() || it->second <= 0) {
        return 0.0;
    }

    if (!avoid_blackjack || (dealer_upcard != 1 && dealer_upcard != 10)) {
        return static_cast<double>(it->second) / deck_state.total_cards;
    }

    // Conditional probability avoiding dealer blackjack
    double base_prob = static_cast<double>(it->second) / (deck_state.total_cards - 1);

    int blackjack_card = (dealer_upcard == 1) ? 10 : 1;
    if (card != blackjack_card) {
        auto bj_it = deck_state.cards_remaining.find(blackjack_card);
        if (bj_it != deck_state.cards_remaining.end()) {
            double total_without_bj = deck_state.total_cards - bj_it->second;
            if (total_without_bj > 0) {
                base_prob *= (total_without_bj - 1) / total_without_bj;
            }
        }
    }

    return base_prob;
}

} // namespace bjlogic