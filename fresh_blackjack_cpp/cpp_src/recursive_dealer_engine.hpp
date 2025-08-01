// Save this as: cpp_src/recursive_dealer_engine.hpp

#ifndef RECURSIVE_DEALER_ENGINE_HPP
#define RECURSIVE_DEALER_ENGINE_HPP

#include "bjlogic_core.hpp"
#include <unordered_map>
#include <array>
#include <vector>

namespace bjlogic {

// =============================================================================
// EXACT DEALER PROBABILITY STRUCTURES
// =============================================================================

struct ExactDealerProbs {
    // Exact probabilities that ALWAYS sum to 1.0000
    double prob_17;
    double prob_18;
    double prob_19;
    double prob_20;
    double prob_21;
    double prob_bust;
    double prob_blackjack;  // Natural 21 (only on first two cards)

    // Full distribution for advanced analysis [0-22]
    std::array<double, 23> distribution;

    // Metadata
    int recursive_calls;
    bool from_cache;

    ExactDealerProbs() : prob_17(0.0), prob_18(0.0), prob_19(0.0),
                        prob_20(0.0), prob_21(0.0), prob_bust(0.0),
                        prob_blackjack(0.0), recursive_calls(0), from_cache(false) {
        distribution.fill(0.0);
    }

    // Verify probabilities sum to 1.0 (for debugging)
    double get_total_probability() const {
        return prob_17 + prob_18 + prob_19 + prob_20 + prob_21 + prob_bust + prob_blackjack;
    }

    // Get probability for specific dealer total
    double get_prob_for_total(int total) const {
        switch(total) {
            case 17: return prob_17;
            case 18: return prob_18;
            case 19: return prob_19;
            case 20: return prob_20;
            case 21: return prob_21;
            case 22: return prob_bust;  // Bust represented as 22
            default: return 0.0;
        }
    }
};

struct DeckComposition {
    std::array<int, 13> cards;  // [0]=Ace, [1]=2, ..., [8]=9, [9-12]=10,J,Q,K
    int total_cards;

    DeckComposition(int num_decks = 6) : total_cards(52 * num_decks) {
        // Standard composition
        for (int i = 0; i < 9; ++i) {  // A,2,3,4,5,6,7,8,9
            cards[i] = 4 * num_decks;
        }
        for (int i = 9; i < 13; ++i) {  // 10,J,Q,K
            cards[i] = 4 * num_decks;
        }
    }

    // Remove card by rank (1=Ace, 2-9=face, 10=any ten-value)
    void remove_card(int rank) {
        if (rank >= 1 && rank <= 10) {
            int index = (rank == 10) ? 9 : (rank - 1);  // Map 10 to first ten slot
            if (rank == 10) {
                // Remove any available ten-value card
                for (int i = 9; i < 13; ++i) {
                    if (cards[i] > 0) {
                        cards[i]--;
                        total_cards--;
                        return;
                    }
                }
            } else {
                if (cards[index] > 0) {
                    cards[index]--;
                    total_cards--;
                }
            }
        }
    }

    // Get total ten-value cards remaining
    int get_ten_cards() const {
        return cards[9] + cards[10] + cards[11] + cards[12];
    }

    // Get cards remaining for specific rank
    int get_cards_for_rank(int rank) const {
        if (rank == 1) return cards[0];  // Ace
        if (rank >= 2 && rank <= 9) return cards[rank - 1];
        if (rank == 10) return get_ten_cards();
        return 0;
    }

    // Calculate probability of drawing specific rank
    double get_probability(int rank) const {
        if (total_cards <= 0) return 0.0;
        return static_cast<double>(get_cards_for_rank(rank)) / total_cards;
    }

    // Generate cache key
    uint64_t get_cache_key() const {
        uint64_t key = 0;
        for (int i = 0; i < 13; ++i) {
            key = key * 53 + cards[i];  // 53 is prime > max cards
        }
        return key;
    }
};

// =============================================================================
// RECURSIVE DEALER PROBABILITY ENGINE
// =============================================================================

class RecursiveDealerEngine {
private:
    // Cache for performance
    mutable std::unordered_map<uint64_t, ExactDealerProbs> cache;
    mutable int total_cache_hits;
    mutable int total_cache_misses;

    // Generate cache key from dealer hand and deck
    uint64_t generate_cache_key(const std::vector<int>& dealer_hand,
                                const DeckComposition& deck,
                                const RulesConfig& rules) const;

public:
    RecursiveDealerEngine() : total_cache_hits(0), total_cache_misses(0) {}

    // =================================================================
    // MAIN RECURSIVE PROBABILITY CALCULATION
    // =================================================================

    // Calculate exact dealer probabilities for given upcard and deck
    ExactDealerProbs calculate_exact_probabilities(int dealer_upcard,
                                                  const DeckComposition& deck,
                                                  const RulesConfig& rules) const;

    // Recursive engine that handles any dealer hand state
    ExactDealerProbs calculate_recursive(const std::vector<int>& dealer_hand,
                                        DeckComposition deck,
                                        const RulesConfig& rules,
                                        int depth = 0) const;

    // =================================================================
    // DEALER LOGIC HELPERS (John Nairn Style)
    // =================================================================

    // Calculate current dealer total and soft status
    std::pair<int, bool> calculate_dealer_total_and_soft(const std::vector<int>& hand) const;

    // Determine if dealer must hit based on total and rules
    bool dealer_must_hit(int total, bool is_soft, const RulesConfig& rules) const;

    // Check for blackjack (only valid on 2-card hands)
    bool is_dealer_blackjack(const std::vector<int>& hand) const;

    // =================================================================
    // INTEGRATION WITH YOUR EXISTING SYSTEM
    // =================================================================

    // Convert DeckState to DeckComposition
    DeckComposition convert_from_deck_state(const DeckState& deck_state) const;

    // Convert back to your EVResult format
    double calculate_stand_ev_from_exact_probs(const std::vector<int>& player_hand,
                                             const ExactDealerProbs& dealer_probs,
                                             const RulesConfig& rules) const;

    // =================================================================
    // PERFORMANCE AND DEBUGGING
    // =================================================================

    void clear_cache() const { cache.clear(); }
    size_t get_cache_size() const { return cache.size(); }
    int get_cache_hits() const { return total_cache_hits; }
    int get_cache_misses() const { return total_cache_misses; }

    // Verify probabilities are mathematically correct
    bool verify_probabilities(const ExactDealerProbs& probs, double tolerance = 0.000001) const;
};

} // namespace bjlogic

#endif // RECURSIVE_DEALER_ENGINE_HPP