// Save this as: cpp_src/recursive_dealer_engine.cpp

#include "recursive_dealer_engine.hpp"
#include <cmath>
#include <algorithm>

namespace bjlogic {

// =============================================================================
// MAIN RECURSIVE CALCULATION
// =============================================================================

ExactDealerProbs RecursiveDealerEngine::calculate_exact_probabilities(
    int dealer_upcard, const DeckComposition& deck, const RulesConfig& rules) const {

    // Create initial dealer hand with upcard
    std::vector<int> dealer_hand = {dealer_upcard};

    // Remove dealer upcard from deck
    DeckComposition working_deck = deck;
    working_deck.remove_card(dealer_upcard);

    // Check cache first
    uint64_t cache_key = generate_cache_key(dealer_hand, working_deck, rules);
    auto cached = cache.find(cache_key);
    if (cached != cache.end()) {
        total_cache_hits++;
        auto result = cached->second;
        result.from_cache = true;
        return result;
    }

    total_cache_misses++;

    // Initialize result
    ExactDealerProbs result;

    // Handle blackjack check ONLY if dealer shows Ace or 10
    if (dealer_upcard == 1 || dealer_upcard == 10) {
        // Check for natural blackjack probability
        int needed_for_bj = (dealer_upcard == 1) ? 10 : 1;
        int bj_cards = working_deck.get_cards_for_rank(needed_for_bj);

        if (working_deck.total_cards > 0) {
            result.prob_blackjack = static_cast<double>(bj_cards) / working_deck.total_cards;

            // Calculate NON-blackjack probabilities (when dealer doesn't have natural)
            if (result.prob_blackjack < 1.0) {
                // Create deck WITHOUT the blackjack-completing card
                DeckComposition no_bj_deck = working_deck;
                no_bj_deck.remove_card(needed_for_bj);

                // Calculate probabilities assuming NO blackjack
                ExactDealerProbs non_bj_probs = calculate_recursive(dealer_hand, no_bj_deck, rules, 0);

                // Scale the non-blackjack probabilities by (1 - blackjack_prob)
                double scale_factor = 1.0 - result.prob_blackjack;
                result.prob_17 = non_bj_probs.prob_17 * scale_factor;
                result.prob_18 = non_bj_probs.prob_18 * scale_factor;
                result.prob_19 = non_bj_probs.prob_19 * scale_factor;
                result.prob_20 = non_bj_probs.prob_20 * scale_factor;

                // CRITICAL FIX: prob_21 should be non-blackjack 21s only
                result.prob_21 = non_bj_probs.prob_21 * scale_factor;

                result.prob_bust = non_bj_probs.prob_bust * scale_factor;

                result.recursive_calls = non_bj_probs.recursive_calls + 1;
            }
            // If prob_blackjack == 1.0, then all other probabilities remain 0
        }
    } else {
        // No blackjack possible with this upcard, calculate normally
        result = calculate_recursive(dealer_hand, working_deck, rules, 0);
        // result.prob_blackjack remains 0.0 (already initialized)
    }

    // Cache and return
    cache[cache_key] = result;
    return result;
}

ExactDealerProbs RecursiveDealerEngine::calculate_recursive(
    const std::vector<int>& dealer_hand, DeckComposition deck,
    const RulesConfig& rules, int depth) const {

    ExactDealerProbs result;
    result.recursive_calls = 1;

    // Calculate current dealer state
    auto [total, is_soft] = calculate_dealer_total_and_soft(dealer_hand);

    // TERMINAL CASE 1: Dealer busted
    if (total > 21) {
        result.prob_bust = 1.0;
        result.distribution[22] = 1.0;  // Index 22 = bust
        return result;
    }

    // TERMINAL CASE 2: Dealer must stand
    if (!dealer_must_hit(total, is_soft, rules)) {
        // Set probability for final total
        switch (total) {
            case 17: result.prob_17 = 1.0; break;
            case 18: result.prob_18 = 1.0; break;
            case 19: result.prob_19 = 1.0; break;
            case 20: result.prob_20 = 1.0; break;
            case 21:
                // CRITICAL FIX: This is NON-blackjack 21 (3+ cards or non-natural 2-card 21)
                result.prob_21 = 1.0;
                break;
        }
        result.distribution[total] = 1.0;
        return result;
    }

    // RECURSIVE CASE: Dealer must hit
    double total_prob_check = 0.0;

    // Try all possible next cards
    for (int rank = 1; rank <= 10; ++rank) {
        int cards_available = deck.get_cards_for_rank(rank);
        if (cards_available <= 0) continue;

        double card_prob = deck.get_probability(rank);
        total_prob_check += card_prob;

        // Create new hand with this card
        std::vector<int> new_hand = dealer_hand;
        new_hand.push_back(rank);

        // Update deck (remove the card)
        DeckComposition new_deck = deck;
        new_deck.remove_card(rank);

        // Recursive call
        ExactDealerProbs branch_result = calculate_recursive(new_hand, new_deck, rules, depth + 1);

        // Accumulate weighted probabilities
        result.prob_17 += card_prob * branch_result.prob_17;
        result.prob_18 += card_prob * branch_result.prob_18;
        result.prob_19 += card_prob * branch_result.prob_19;
        result.prob_20 += card_prob * branch_result.prob_20;
        result.prob_21 += card_prob * branch_result.prob_21;  // Non-blackjack 21s
        result.prob_bust += card_prob * branch_result.prob_bust;

        // IMPORTANT: Don't accumulate prob_blackjack here - it's only set at the top level
        result.prob_blackjack += card_prob * branch_result.prob_blackjack;

        result.recursive_calls += branch_result.recursive_calls;
    }

    // CRITICAL: Normalize if total probability != 1.0 due to deck depletion
    if (total_prob_check > 0.0 && std::abs(total_prob_check - 1.0) > 0.000001) {
        double norm = 1.0 / total_prob_check;
        result.prob_17 *= norm;
        result.prob_18 *= norm;
        result.prob_19 *= norm;
        result.prob_20 *= norm;
        result.prob_21 *= norm;
        result.prob_bust *= norm;
        result.prob_blackjack *= norm;
    }

    return result;
}

// =============================================================================
// DEALER LOGIC HELPERS
// =============================================================================

std::pair<int, bool> RecursiveDealerEngine::calculate_dealer_total_and_soft(
    const std::vector<int>& hand) const {

    int total = 0;
    int aces = 0;

    // Sum all cards and count aces
    for (int card : hand) {
        total += card;
        if (card == 1) aces++;
    }

    // Optimize aces (use one as 11 if possible)
    bool is_soft = false;
    if (aces > 0 && total + 10 <= 21) {
        total += 10;
        is_soft = true;
    }

    return {total, is_soft};
}

bool RecursiveDealerEngine::dealer_must_hit(int total, bool is_soft,
                                           const RulesConfig& rules) const {
    if (total < 17) return true;   // Always hit below 17
    if (total > 17) return false;  // Always stand above 17

    // Exactly 17
    if (total == 17 && is_soft && rules.dealer_hits_soft_17) {
        return true;  // Hit soft 17 if H17 rules
    }

    return false;  // Stand on hard 17 or soft 17 with S17 rules
}

bool RecursiveDealerEngine::is_dealer_blackjack(const std::vector<int>& hand) const {
    if (hand.size() != 2) return false;

    int total = hand[0] + hand[1];
    bool has_ace = (hand[0] == 1 || hand[1] == 1);
    bool has_ten = (hand[0] == 10 || hand[1] == 10);

    return (total == 11 && has_ace && has_ten);
}

// =============================================================================
// INTEGRATION HELPERS
// =============================================================================

DeckComposition RecursiveDealerEngine::convert_from_deck_state(const DeckState& deck_state) const {
    DeckComposition comp(deck_state.num_decks);

    // Reset composition
    comp.total_cards = 0;
    for (int i = 0; i < 13; ++i) {
        comp.cards[i] = 0;
    }

    // Convert from DeckState format
    for (const auto& [rank, count] : deck_state.cards_remaining) {
        if (rank >= 1 && rank <= 10) {
            if (rank == 10) {
                // Distribute ten-value cards evenly across slots 9-12
                int per_slot = count / 4;
                int remainder = count % 4;
                for (int i = 9; i < 13; ++i) {
                    comp.cards[i] = per_slot + (i - 9 < remainder ? 1 : 0);
                }
            } else {
                comp.cards[rank - 1] = count;
            }
            comp.total_cards += count;
        }
    }

    return comp;
}

double RecursiveDealerEngine::calculate_stand_ev_from_exact_probs(
    const std::vector<int>& player_hand, const ExactDealerProbs& dealer_probs,
    const RulesConfig& rules) const {

    HandData player_data = BJLogicCore::calculate_hand_value(player_hand);

    if (player_data.is_busted) return -1.0;

    double ev = 0.0;
    int player_total = player_data.total;

    // Player wins if dealer busts
    ev += dealer_probs.prob_bust * 1.0;

    // Compare against each dealer total
    if (player_total > 17) ev += dealer_probs.prob_17 * 1.0;
    else if (player_total < 17) ev += dealer_probs.prob_17 * (-1.0);
    // Push at 17 contributes 0

    if (player_total > 18) ev += dealer_probs.prob_18 * 1.0;
    else if (player_total < 18) ev += dealer_probs.prob_18 * (-1.0);

    if (player_total > 19) ev += dealer_probs.prob_19 * 1.0;
    else if (player_total < 19) ev += dealer_probs.prob_19 * (-1.0);

    if (player_total > 20) ev += dealer_probs.prob_20 * 1.0;
    else if (player_total < 20) ev += dealer_probs.prob_20 * (-1.0);

    // CRITICAL FIX: Handle dealer 21 vs player 21 correctly
    if (player_total > 21) {
        ev += dealer_probs.prob_21 * 1.0;  // Player 21 beats dealer non-blackjack 21
    } else if (player_total < 21) {
        ev += dealer_probs.prob_21 * (-1.0);  // Player < 21 loses to dealer 21
    }
    // If player_total == 21, it's a push against dealer non-blackjack 21 (contributes 0)

    // HANDLE BLACKJACK SCENARIOS
    if (player_data.is_blackjack && player_hand.size() == 2) {
        // Player has blackjack
        if (dealer_probs.prob_blackjack > 0) {
            // Dealer might also have blackjack -> push
            ev += dealer_probs.prob_blackjack * 0.0;  // Push
        }

        // Player blackjack wins against all other dealer outcomes with bonus
        double non_bj_dealer_outcomes = dealer_probs.prob_17 + dealer_probs.prob_18 +
                                       dealer_probs.prob_19 + dealer_probs.prob_20 +
                                       dealer_probs.prob_21 + dealer_probs.prob_bust;
        ev += non_bj_dealer_outcomes * rules.blackjack_payout;  // 1.5 for 3:2

    } else if (player_total == 21 && player_hand.size() > 2) {
        // Player has non-blackjack 21
        if (dealer_probs.prob_blackjack > 0) {
            // Dealer blackjack beats player non-blackjack 21
            ev += dealer_probs.prob_blackjack * (-1.0);
        }
        // Against dealer non-blackjack 21, it's a push (already handled above)

    } else {
        // Player doesn't have 21
        if (dealer_probs.prob_blackjack > 0) {
            // Dealer blackjack beats any non-21 player hand
            ev += dealer_probs.prob_blackjack * (-1.0);
        }
    }

    return ev;
}

// ADD a verification method to check the probabilities make sense:

// Note: The verify_probabilities_detailed function is intentionally omitted here
// because it is not declared in the RecursiveDealerEngine class definition. If
// detailed probability verification is required, consider implementing it as
// a standalone helper outside the class. The existing verify_probabilities
// function provides a basic sanity check by ensuring the probabilities sum to 1.

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

uint64_t RecursiveDealerEngine::generate_cache_key(
    const std::vector<int>& dealer_hand, const DeckComposition& deck,
    const RulesConfig& rules) const {

    uint64_t key = deck.get_cache_key();

    // Include dealer hand
    for (int card : dealer_hand) {
        key = key * 13 + card;
    }

    // Include relevant rules
    key = key * 2 + (rules.dealer_hits_soft_17 ? 1 : 0);

    return key;
}

bool RecursiveDealerEngine::verify_probabilities(const ExactDealerProbs& probs,
                                                double tolerance) const {
    double total = probs.get_total_probability();
    return std::abs(total - 1.0) <= tolerance;
}

} // namespace bjlogic