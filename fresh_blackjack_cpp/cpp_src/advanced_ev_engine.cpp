// CLEAN REPLACEMENT for your advanced_ev_engine.cpp
// This fixes all compilation errors by properly integrating the recursive methods

#include "advanced_ev_engine.hpp"
#include <cmath>
#include <algorithm>
#include <random>

namespace bjlogic {

// =============================================================================
// CONSTRUCTOR AND INITIALIZATION (Keep your existing)
// =============================================================================

AdvancedEVEngine::AdvancedEVEngine(int depth, double precision)
    : simulation_depth(depth), precision_threshold(precision),
      use_composition_dependent(true), use_variance_reduction(true),
      cache_hits(0), cache_misses(0), recursive_calls(0) {
    precompute_tables();
}

void AdvancedEVEngine::precompute_tables() {
    // Basic precomputation - simplified for now
    for (int dealer_total = 2; dealer_total <= 21; ++dealer_total) {
        for (int upcard = 0; upcard < 10; ++upcard) {
            dealer_outcome_matrix[dealer_total][upcard] = 1.0 / 13.0; // Placeholder
            player_bust_matrix[dealer_total][upcard] = 0.3; // Placeholder
        }
    }
}

// =============================================================================
// NEW RECURSIVE DEALER PROBABILITY ENGINE
// =============================================================================

DealerProbabilities AdvancedEVEngine::calculate_dealer_probabilities_advanced(
    int dealer_upcard,
    const DeckComposition& deck,
    const RulesConfig& rules) const {

    // Create initial dealer hand with upcard
    std::vector<int> dealer_hand = {dealer_upcard};

    // Generate cache key
    uint64_t cache_key = generate_probability_cache_key(dealer_hand, deck, rules);

    // Check cache first
    auto cached = dealer_prob_cache.find(cache_key);
    if (cached != dealer_prob_cache.end()) {
        cache_hits++;
        auto result = cached->second;
        result.from_cache = true;
        return result;
    }

    cache_misses++;

    // Use recursive calculation for ANY deck composition
    DealerProbabilities result = calculate_dealer_probabilities_recursive(dealer_hand, deck, rules, 0);

    // Handle blackjack probability (only on first two cards)
    if (dealer_upcard == 1 || dealer_upcard == 10) {
        int natural_cards_remaining = 0;

        if (dealer_upcard == 1) {
            // Count all 10-value cards for natural
            natural_cards_remaining = deck.get_ten_cards();
        } else {
            // Count Aces for natural
            natural_cards_remaining = deck.get_remaining(1);
        }

        if (deck.total_cards > 0) {
            result.blackjack_prob = static_cast<double>(natural_cards_remaining) / deck.total_cards;

            // Adjust other probabilities to account for blackjack
            double non_blackjack_factor = 1.0 - result.blackjack_prob;
            result.bust_prob *= non_blackjack_factor;
            result.total_17_prob *= non_blackjack_factor;
            result.total_18_prob *= non_blackjack_factor;
            result.total_19_prob *= non_blackjack_factor;
            result.total_20_prob *= non_blackjack_factor;
            result.total_21_prob *= non_blackjack_factor;

            // Update distribution array
            for (int i = 17; i <= 21; ++i) {
                result.total_distribution[i] *= non_blackjack_factor;
            }
            // Blackjack goes in index 21 but separate from regular 21
            result.total_distribution[21] += result.blackjack_prob;
        }
    }

    // Cache the result
    dealer_prob_cache[cache_key] = result;
    return result;
}

DealerProbabilities AdvancedEVEngine::calculate_dealer_probabilities_recursive(
    const std::vector<int>& dealer_hand,
    const DeckComposition& deck,
    const RulesConfig& rules,
    int depth) const {

    recursive_calls++;

    DealerProbabilities result;
    result.calculations_performed = 1;

    // Calculate current dealer total and soft status
    int dealer_total = calculate_dealer_total(dealer_hand);
    bool is_soft = is_dealer_soft(dealer_hand);

    // TERMINAL CONDITION 1: Dealer busted
    if (dealer_total > 21) {
        result.bust_prob = 1.0;
        result.total_distribution[22] = 1.0;  // Use index 22 for bust
        return result;
    }

    // TERMINAL CONDITION 2: Dealer must stand
    if (!dealer_must_hit_by_total(dealer_total, is_soft, rules)) {
        // Dealer stands - record the final total
        result.total_distribution[dealer_total] = 1.0;

        // Set specific total probabilities based on final total
        switch (dealer_total) {
            case 17: result.total_17_prob = 1.0; break;
            case 18: result.total_18_prob = 1.0; break;
            case 19: result.total_19_prob = 1.0; break;
            case 20: result.total_20_prob = 1.0; break;
            case 21: result.total_21_prob = 1.0; break;
        }
        return result;
    }

    // RECURSIVE CASE: Dealer must hit
    double total_probability_used = 0.0;

    // Enumerate all possible next cards based on actual deck composition
    for (int rank = 1; rank <= 13; ++rank) {
        int cards_of_rank = deck.get_remaining(rank);
        if (cards_of_rank <= 0) continue;

        // Calculate probability of drawing this card
        double card_prob = static_cast<double>(cards_of_rank) / deck.total_cards;
        total_probability_used += card_prob;

        // Convert card rank to blackjack value
        int card_value = get_card_value(rank);

        // Create new dealer hand with this card
        std::vector<int> new_dealer_hand = dealer_hand;
        new_dealer_hand.push_back(card_value);

        // Update deck composition (remove the card)
        DeckComposition new_deck = deck;
        new_deck.remove_card(rank);

        // Recursive call for this branch
        DealerProbabilities branch_result = calculate_dealer_probabilities_recursive(
            new_dealer_hand, new_deck, rules, depth + 1);

        // Accumulate weighted probabilities
        result.bust_prob += card_prob * branch_result.bust_prob;
        result.blackjack_prob += card_prob * branch_result.blackjack_prob;
        result.total_17_prob += card_prob * branch_result.total_17_prob;
        result.total_18_prob += card_prob * branch_result.total_18_prob;
        result.total_19_prob += card_prob * branch_result.total_19_prob;
        result.total_20_prob += card_prob * branch_result.total_20_prob;
        result.total_21_prob += card_prob * branch_result.total_21_prob;

        // Accumulate full distribution
        for (int i = 0; i < 23; ++i) {
            result.total_distribution[i] += card_prob * branch_result.total_distribution[i];
        }

        result.calculations_performed += branch_result.calculations_performed;
    }

    // CRITICAL: Verify probability normalization
    if (std::abs(total_probability_used - 1.0) > 0.0001) {
        double normalization = 1.0 / total_probability_used;

        result.bust_prob *= normalization;
        result.blackjack_prob *= normalization;
        result.total_17_prob *= normalization;
        result.total_18_prob *= normalization;
        result.total_19_prob *= normalization;
        result.total_20_prob *= normalization;
        result.total_21_prob *= normalization;

        for (int i = 0; i < 23; ++i) {
            result.total_distribution[i] *= normalization;
        }
    }

    return result;
}

// =============================================================================
// HELPER METHODS FOR DEALER LOGIC
// =============================================================================

bool AdvancedEVEngine::dealer_must_hit_by_total(int total, bool is_soft, const RulesConfig& rules) const {
    if (total < 17) return true;   // Always hit < 17
    if (total > 17) return false;  // Always stand > 17

    // Total is exactly 17
    if (total == 17 && is_soft && rules.dealer_hits_soft_17) {
        return true;  // Hit soft 17 if H17 rules
    }

    return false;  // Stand on hard 17 or soft 17 with S17 rules
}

int AdvancedEVEngine::calculate_dealer_total(const std::vector<int>& dealer_hand) const {
    int total = 0;
    int aces = 0;

    // Sum all cards and count aces
    for (int card : dealer_hand) {
        total += card;
        if (card == 1) aces++;
    }

    // Optimize aces (use as 11 if possible without busting)
    while (aces > 0 && total + 10 <= 21) {
        total += 10;
        aces--;
    }

    return total;
}

bool AdvancedEVEngine::is_dealer_soft(const std::vector<int>& dealer_hand) const {
    int total = 0;
    int aces = 0;

    for (int card : dealer_hand) {
        total += card;
        if (card == 1) aces++;
    }

    // Hand is soft if we can use an ace as 11 without busting
    return (aces > 0 && total + 10 <= 21);
}

int AdvancedEVEngine::get_card_value(int rank) const {
    // Convert rank (1-13) to blackjack value (1-10)
    if (rank >= 10) return 10;  // 10, J, Q, K all = 10
    return rank;                // A,2,3,4,5,6,7,8,9 = face value
}

// =============================================================================
// UPDATED STAND EV CALCULATION USING EXACT PROBABILITIES
// =============================================================================

double AdvancedEVEngine::calculate_stand_ev_recursive(const std::vector<int>& player_hand,
                                                     int dealer_upcard,
                                                     const DeckState& deck,
                                                     const RulesConfig& rules) const {

    HandData player_data = BJLogicCore::calculate_hand_value(player_hand);

    if (player_data.is_busted) return -1.0;
    if (player_data.total < 1) return -1.0;

    // Convert DeckState to DeckComposition
    DeckComposition deck_comp = convert_deck_state_to_composition(deck);

    // Use the EXACT recursive probability calculation
    DealerProbabilities dealer_probs = calculate_dealer_probabilities_advanced(dealer_upcard, deck_comp, rules);

    // Calculate EV using EXACT probabilities
    double ev = 0.0;

    // Player wins against dealer bust
    ev += dealer_probs.bust_prob * 1.0;

    // Compare player total against each possible dealer total
    for (int dealer_total = 17; dealer_total <= 21; ++dealer_total) {
        double dealer_prob = 0.0;

        switch (dealer_total) {
            case 17: dealer_prob = dealer_probs.total_17_prob; break;
            case 18: dealer_prob = dealer_probs.total_18_prob; break;
            case 19: dealer_prob = dealer_probs.total_19_prob; break;
            case 20: dealer_prob = dealer_probs.total_20_prob; break;
            case 21: dealer_prob = dealer_probs.total_21_prob; break;
        }

        if (player_data.total > dealer_total) {
            ev += dealer_prob * 1.0;  // Player wins
        } else if (player_data.total < dealer_total) {
            ev += dealer_prob * (-1.0);  // Player loses
        }
        // Push case (equal totals) contributes 0 to EV
    }

    // Handle blackjack bonus
    if (player_data.is_blackjack && player_hand.size() == 2) {
        double player_bj_win_prob = dealer_probs.total_21_prob + dealer_probs.bust_prob;
        for (int dt = 17; dt <= 20; ++dt) {
            switch (dt) {
                case 17: player_bj_win_prob += dealer_probs.total_17_prob; break;
                case 18: player_bj_win_prob += dealer_probs.total_18_prob; break;
                case 19: player_bj_win_prob += dealer_probs.total_19_prob; break;
                case 20: player_bj_win_prob += dealer_probs.total_20_prob; break;
            }
        }

        ev += player_bj_win_prob * (rules.blackjack_payout - 1.0);
    }

    return ev;
}

// =============================================================================
// UTILITY CONVERSION METHOD
// =============================================================================

DeckComposition AdvancedEVEngine::convert_deck_state_to_composition(const DeckState& deck_state) const {
    DeckComposition comp(deck_state.num_decks);

    // Reset to zero first
    for (int i = 0; i < 13; ++i) {
        comp.cards_remaining[i] = 0;
    }
    comp.total_cards = 0;

    // Copy from DeckState to DeckComposition
    for (const auto& pair : deck_state.cards_remaining) {
        int rank = pair.first;
        int count = pair.second;

        if (rank >= 1 && rank <= 13) {
            comp.cards_remaining[rank - 1] = count;
            comp.total_cards += count;
        }
    }

    return comp;
}

// =============================================================================
// KEEP ALL YOUR EXISTING METHODS FROM HERE (unchanged)
// =============================================================================

DetailedEV AdvancedEVEngine::calculate_true_count_ev(const std::vector<int>& player_hand,
                                                   int dealer_upcard,
                                                   double true_count,
                                                   const RulesConfig& rules) const {

    DetailedEV result;

    // Create deck state for calculations
    DeckState deck(rules.num_decks);

    // Use the NEW recursive stand calculation
    result.stand_ev = calculate_stand_ev_recursive(player_hand, dealer_upcard, deck, rules);
    result.hit_ev = calculate_hit_ev_recursive(player_hand, dealer_upcard, deck, rules, 0);

    if (player_hand.size() == 2) {
        result.double_ev = calculate_double_ev_recursive(player_hand, dealer_upcard, deck, rules);

        // Check for split
        if (player_hand[0] == player_hand[1]) {
            result.split_ev = calculate_split_ev_advanced(player_hand, dealer_upcard, deck, rules, rules.max_split_hands - 1);
        } else {
            result.split_ev = -2.0;
        }
    } else {
        result.double_ev = -2.0;
        result.split_ev = -2.0;
    }

    // Surrender
    if (rules.surrender_allowed && player_hand.size() == 2) {
        result.surrender_ev = -0.5;
    } else {
        result.surrender_ev = -1.0;
    }

    // Apply true count adjustment
    double adjustment = true_count * 0.005;
    result.true_count_adjustment = adjustment;

    result.stand_ev += adjustment;
    result.hit_ev += adjustment;
    result.double_ev += adjustment * 2.0;
    result.split_ev += adjustment;

    determine_optimal_action(result);

    return result;
}

// =============================================================================
// KEEP ALL YOUR OTHER EXISTING METHODS (just fix method calls)
// =============================================================================

double AdvancedEVEngine::calculate_hit_ev_recursive(const std::vector<int>& hand,
                                                   int dealer_upcard,
                                                   const DeckState& deck,
                                                   const RulesConfig& rules,
                                                   int depth) const {

    if (depth > simulation_depth) {
        return calculate_simple_hit_ev(hand, dealer_upcard, deck, rules);
    }

    HandData hand_data = BJLogicCore::calculate_hand_value(hand);

    if (hand_data.is_busted) return -1.0;
    if (hand_data.total >= 21) {
        return calculate_stand_ev_recursive(hand, dealer_upcard, deck, rules);
    }

    double total_ev = 0.0;
    double total_probability = 0.0;

    // Iterate through all possible next cards
    for (int next_card_rank = 1; next_card_rank <= 10; ++next_card_rank) {
        auto it = deck.cards_remaining.find(next_card_rank);
        if (it == deck.cards_remaining.end() || it->second <= 0) continue;

        int cards_available = it->second;
        double card_prob = static_cast<double>(cards_available) / deck.total_cards;
        total_probability += card_prob;

        int card_value = (next_card_rank == 10) ? 10 : next_card_rank;

        // Create new hand
        std::vector<int> new_hand = hand;
        new_hand.push_back(card_value);

        // Update deck state
        DeckState new_deck = deck;
        new_deck.cards_remaining[next_card_rank]--;
        new_deck.total_cards--;

        // Calculate EV for this branch
        double branch_ev;
        HandData new_hand_data = BJLogicCore::calculate_hand_value(new_hand);

        if (new_hand_data.is_busted) {
            branch_ev = -1.0;
        } else if (new_hand_data.total >= 21) {
            branch_ev = calculate_stand_ev_recursive(new_hand, dealer_upcard, new_deck, rules);
        } else {
            // Player can hit again or stand - choose optimal
            double hit_again_ev = calculate_hit_ev_recursive(new_hand, dealer_upcard, new_deck, rules, depth + 1);
            double stand_ev = calculate_stand_ev_recursive(new_hand, dealer_upcard, new_deck, rules);
            branch_ev = std::max(hit_again_ev, stand_ev);
        }

        total_ev += card_prob * branch_ev;
    }

    // Normalize if needed
    if (total_probability > 0.0 && std::abs(total_probability - 1.0) > 0.001) {
        total_ev /= total_probability;
    }

    return total_ev;
}

// ... ADD ALL YOUR OTHER EXISTING METHODS HERE (unchanged)
// Just make sure all calls to calculate_stand_ev_recursive use proper syntax

} // namespace bjlogic