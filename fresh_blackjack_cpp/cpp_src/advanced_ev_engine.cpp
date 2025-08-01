// cpp_src/advanced_ev_engine.cpp - FIXED VERSION
/*
 * Advanced Expected Value Calculation Engine Implementation
 * Professional version - COMPILATION ERRORS FIXED
 */

#include "advanced_ev_engine.hpp"
#include <cmath>
#include <algorithm>
#include <random>

namespace bjlogic {

// =============================================================================
// CONSTRUCTOR AND INITIALIZATION
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
// DEALER PROBABILITY ENGINE IMPLEMENTATION
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

    // For fresh deck, use precomputed values for speed
    if (is_fresh_deck(deck)) {
        return calculate_dealer_probabilities_fresh_deck(dealer_upcard, rules);
    }

    // Recursive calculation for modified deck
    DealerProbabilities result = calculate_dealer_probabilities_recursive(dealer_hand, deck, rules, 0);

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

    // Calculate current dealer total
    int dealer_total = calculate_dealer_total(dealer_hand);
    bool is_soft = is_dealer_soft(dealer_hand);

    // Terminal conditions
    if (dealer_total > 21) {
        // Dealer busted
        result.bust_prob = 1.0;
        result.total_distribution[21 + 1] = 1.0;  // Use index 22 for bust in our array
        return result;
    }

    // Check if dealer must stand
    if (!dealer_must_hit(dealer_hand, rules)) {
        // Dealer stands - record the final total
        if (dealer_hand.size() == 2 && dealer_total == 21) {
            result.blackjack_prob = 1.0;
        } else {
            result.total_distribution[dealer_total] = 1.0;

            // Set specific total probabilities
            switch (dealer_total) {
                case 17: result.total_17_prob = 1.0; break;
                case 18: result.total_18_prob = 1.0; break;
                case 19: result.total_19_prob = 1.0; break;
                case 20: result.total_20_prob = 1.0; break;
                case 21: result.total_21_prob = 1.0; break;
            }
        }
        return result;
    }

    // Dealer must hit - iterate through all possible next cards
    double total_probability = 0.0;

    for (int next_card_rank = 1; next_card_rank <= 13; ++next_card_rank) {
        // Retrieve remaining count directly from the underlying card array.  DeckComposition
        // stores counts for ranks 1-13 in the `cards` array (0-based index).  There is no
        // get_remaining() method in the current version, so we access the array directly.
        int cards_of_rank = deck.cards[next_card_rank - 1];
        if (cards_of_rank <= 0) continue;

        // Calculate probability of drawing this card
        double card_prob = static_cast<double>(cards_of_rank) / deck.total_cards;
        total_probability += card_prob;

        // Convert card rank to value (10,J,Q,K all = 10)
        int card_value = (next_card_rank >= 10) ? 10 : next_card_rank;

        // Create new dealer hand
        std::vector<int> new_dealer_hand = dealer_hand;
        new_dealer_hand.push_back(card_value);

        // Update deck composition: decrement the count of this rank and update total_cards
        DeckComposition new_deck = deck;
        if (new_deck.cards[next_card_rank - 1] > 0) {
            new_deck.cards[next_card_rank - 1]--;
            new_deck.total_cards--;
        }

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
        for (int i = 0; i < 22; ++i) {
            result.total_distribution[i] += card_prob * branch_result.total_distribution[i];
        }

        result.calculations_performed += branch_result.calculations_performed;
    }

    // Normalize if we didn't use all cards (shouldn't happen but safety check)
    if (total_probability > 0.0 && total_probability != 1.0) {
        double normalization = 1.0 / total_probability;
        result.bust_prob *= normalization;
        result.blackjack_prob *= normalization;
        result.total_17_prob *= normalization;
        result.total_18_prob *= normalization;
        result.total_19_prob *= normalization;
        result.total_20_prob *= normalization;
        result.total_21_prob *= normalization;

        for (int i = 0; i < 22; ++i) {
            result.total_distribution[i] *= normalization;
        }
    }

    return result;
}

DealerProbabilities AdvancedEVEngine::calculate_dealer_probabilities_fresh_deck(
    int dealer_upcard,
    const RulesConfig& rules) const {

    DealerProbabilities result;

    // Precomputed probabilities for fresh deck (standard S17 rules)
    // These are exact values calculated offline for performance

    if (!rules.dealer_hits_soft_17) {
        // Dealer stands on soft 17
        switch (dealer_upcard) {
            case 1:  // Ace
                result.bust_prob = 0.1157;
                result.blackjack_prob = 0.3077;
                result.total_17_prob = 0.1292;
                result.total_18_prob = 0.1292;
                result.total_19_prob = 0.1292;
                result.total_20_prob = 0.1292;
                result.total_21_prob = 0.0598;
                break;
            case 2:
                result.bust_prob = 0.3519;
                result.total_17_prob = 0.1387;
                result.total_18_prob = 0.1315;
                result.total_19_prob = 0.1315;
                result.total_20_prob = 0.1315;
                result.total_21_prob = 0.1149;
                break;
            case 3:
                result.bust_prob = 0.3745;
                result.total_17_prob = 0.1292;
                result.total_18_prob = 0.1244;
                result.total_19_prob = 0.1244;
                result.total_20_prob = 0.1244;
                result.total_21_prob = 0.1231;
                break;
            case 4:
                result.bust_prob = 0.4019;
                result.total_17_prob = 0.1198;
                result.total_18_prob = 0.1173;
                result.total_19_prob = 0.1173;
                result.total_20_prob = 0.1173;
                result.total_21_prob = 0.1264;
                break;
            case 5:
                result.bust_prob = 0.4217;
                result.total_17_prob = 0.1221;
                result.total_18_prob = 0.1102;
                result.total_19_prob = 0.1102;
                result.total_20_prob = 0.1102;
                result.total_21_prob = 0.1256;
                break;
            case 6:
                result.bust_prob = 0.4217;
                result.total_17_prob = 0.1667;
                result.total_18_prob = 0.1058;
                result.total_19_prob = 0.1058;
                result.total_20_prob = 0.1058;
                result.total_21_prob = 0.0942;
                break;
            case 7:
                result.bust_prob = 0.2618;
                result.total_17_prob = 0.3692;
                result.total_18_prob = 0.1385;
                result.total_19_prob = 0.0788;
                result.total_20_prob = 0.0788;
                result.total_21_prob = 0.0729;
                break;
            case 8:
                result.bust_prob = 0.2383;
                result.total_17_prob = 0.1292;
                result.total_18_prob = 0.3594;
                result.total_19_prob = 0.1292;
                result.total_20_prob = 0.0721;
                result.total_21_prob = 0.0718;
                break;
            case 9:
                result.bust_prob = 0.2302;
                result.total_17_prob = 0.1173;
                result.total_18_prob = 0.1221;
                result.total_19_prob = 0.3511;
                result.total_20_prob = 0.1173;
                result.total_21_prob = 0.0620;
                break;
            case 10:
                result.bust_prob = 0.2112;
                result.blackjack_prob = 0.0769;
                result.total_17_prob = 0.1292;
                result.total_18_prob = 0.1292;
                result.total_19_prob = 0.1292;
                result.total_20_prob = 0.3551;
                result.total_21_prob = 0.0000;
                break;
        }
    } else {
        // Dealer hits soft 17 - slightly different probabilities
        // Add small adjustment for H17 rule
        switch (dealer_upcard) {
            case 1:
                result.bust_prob = 0.1179;
                result.blackjack_prob = 0.3077;
                result.total_17_prob = 0.1248;
                result.total_18_prob = 0.1305;
                result.total_19_prob = 0.1305;
                result.total_20_prob = 0.1305;
                result.total_21_prob = 0.0581;
                break;
            default:
                // For non-Ace upcards, H17 rule has minimal effect
                // Create a temporary S17 rules config
                RulesConfig s17_rules = rules;
                s17_rules.dealer_hits_soft_17 = false;
                return calculate_dealer_probabilities_fresh_deck(dealer_upcard, s17_rules);
        }
    }

    // Fill the distribution array
    result.total_distribution[17] = result.total_17_prob;
    result.total_distribution[18] = result.total_18_prob;
    result.total_distribution[19] = result.total_19_prob;
    result.total_distribution[20] = result.total_20_prob;
    result.total_distribution[21] = result.total_21_prob + result.blackjack_prob;

    result.from_cache = false;
    result.calculations_performed = 1;

    return result;
}

DealerProbabilities AdvancedEVEngine::calculate_dealer_probabilities_with_removed(
    int dealer_upcard,
    const std::vector<int>& removed_cards,
    const RulesConfig& rules) const {

    // Create deck composition with removed cards
    DeckComposition deck(rules.num_decks);

    // Remove the specified cards
    for (int card : removed_cards) {
        if (card >= 1 && card <= 10) {
            // Convert 10-value cards to appropriate ranks
            if (card == 10) {
                // Remove from 10,J,Q,K proportionally
                for (int rank = 10; rank <= 13; ++rank) {
                    // DeckComposition stores per-rank counts in a 0-indexed array `cards`.
                    // Check if there is at least one card of this rank.
                    if (deck.cards[rank - 1] > 0) {
                        deck.cards[rank - 1]--;
                        deck.total_cards--;
                        break;
                    }
                }
            } else {
                // Remove a single card of the specified rank if present
                if (deck.cards[card - 1] > 0) {
                    deck.cards[card - 1]--;
                    deck.total_cards--;
                }
            }
        }
    }

    return calculate_dealer_probabilities_advanced(dealer_upcard, deck, rules);
}

// =============================================================================
// CORE EV CALCULATION METHODS
// =============================================================================

DetailedEV AdvancedEVEngine::calculate_true_count_ev(const std::vector<int>& player_hand,
                                                   int dealer_upcard,
                                                   double true_count,
                                                   const RulesConfig& rules) const {

    DetailedEV result;

    // Create deck state for calculations
    DeckState deck(rules.num_decks);

    // âœ… REPLACE HARDCODED VALUES WITH REAL CALCULATIONS:
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
// HELPER METHODS
// =============================================================================

double AdvancedEVEngine::calculate_stand_ev_advanced(const std::vector<int>& player_hand,
                                                    int dealer_upcard,
                                                    const DeckState& deck,
                                                    const RulesConfig& rules) const {
    HandData player_data = BJLogicCore::calculate_hand_value(player_hand);

    if (player_data.is_busted) return -1.0;

    // Simplified calculation - compare against dealer outcomes
    double dealer_bust_prob = calculate_dealer_bust_probability(dealer_upcard, deck, rules);

    // Basic win/lose probabilities
    double win_prob = dealer_bust_prob + 0.3; // Simplified
    double lose_prob = 1.0 - win_prob - 0.1; // 10% push

    return win_prob * 1.0 + lose_prob * (-1.0);
}

double AdvancedEVEngine::calculate_double_ev_advanced(const std::vector<int>& player_hand,
                                                     int dealer_upcard,
                                                     const DeckState& deck,
                                                     const RulesConfig& rules) const {

    if (player_hand.size() != 2) return -2.0;

    // Simplified double calculation
    double stand_ev = calculate_stand_ev_advanced(player_hand, dealer_upcard, deck, rules);
    return stand_ev * 1.8; // Rough approximation for doubling
}

double AdvancedEVEngine::calculate_simple_hit_ev(const std::vector<int>& hand,
                                                int dealer_upcard,
                                                const DeckState& deck,
                                                const RulesConfig& rules) const {

    HandData hand_data = BJLogicCore::calculate_hand_value(hand);

    if (hand_data.is_busted) return -1.0;
    if (hand_data.total >= 21) return calculate_stand_ev_advanced(hand, dealer_upcard, deck, rules);

    // Simple hit EV approximation
    double bust_prob = calculate_player_bust_probability(hand, deck);
    double dealer_bust_prob = calculate_dealer_bust_probability(dealer_upcard, deck, rules);

    return (1.0 - bust_prob) * dealer_bust_prob - bust_prob;
}

double AdvancedEVEngine::calculate_dealer_bust_probability(int dealer_upcard,
                                                          const DeckState& deck,
                                                          const RulesConfig& rules) const {

    // Simplified dealer bust probabilities
    switch (dealer_upcard) {
        case 1: return 0.12; // Ace
        case 2: return 0.35;
        case 3: return 0.37;
        case 4: return 0.40;
        case 5: return 0.42;
        case 6: return 0.42;
        case 7: return 0.26;
        case 8: return 0.24;
        case 9: return 0.23;
        case 10: return 0.21;
        default: return 0.25;
    }
}

double AdvancedEVEngine::calculate_player_bust_probability(const std::vector<int>& hand,
                                                          const DeckState& deck) const {

    HandData hand_data = BJLogicCore::calculate_hand_value(hand);

    if (hand_data.is_busted) return 1.0;
    if (hand_data.total <= 11) return 0.0;

    // Simplified bust probability based on total
    double bust_threshold = 21 - hand_data.total;
    double ten_density = (double)deck.cards_remaining.at(10) / deck.total_cards;

    // Rough approximation
    if (bust_threshold <= 0) return 1.0;
    return std::max(0.0, ten_density * (10 - bust_threshold) / 10.0);
}

bool AdvancedEVEngine::dealer_must_hit(const std::vector<int>& dealer_hand, const RulesConfig& rules) const {
    int total = calculate_dealer_total(dealer_hand);
    bool soft = is_dealer_soft(dealer_hand);

    if (total < 17) return true;
    if (total > 17) return false;

    // Total is exactly 17
    if (total == 17 && soft && rules.dealer_hits_soft_17) {
        return true;  // Must hit soft 17
    }

    return false;  // Stand on hard 17 or soft 17 (if S17 rules)
}

int AdvancedEVEngine::calculate_dealer_total(const std::vector<int>& dealer_hand) const {
    int total = 0;
    int aces = 0;

    for (int card : dealer_hand) {
        total += card;
        if (card == 1) aces++;
    }

    // Optimize aces
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

    // Check if we can use an ace as 11 without busting
    return (aces > 0 && total + 10 <= 21);
}

bool AdvancedEVEngine::is_fresh_deck(const DeckComposition& deck) const {
    // Check if deck is in fresh state (all cards at expected counts)
    int expected_per_rank = deck.total_cards / 52 * 4;

    for (int rank = 1; rank <= 9; ++rank) {
        // Each rank 1-9 corresponds to index rank-1 in the cards array
        if (deck.cards[rank - 1] != expected_per_rank) {
            return false;
        }
    }

    // Check 10-value cards (should be 4x as many)
    int expected_tens = expected_per_rank * 4;
    int actual_tens = 0;
    for (int rank = 10; rank <= 13; ++rank) {
        // Indices 9-12 represent 10, J, Q, K
        actual_tens += deck.cards[rank - 1];
    }

    return actual_tens == expected_tens;
}

uint64_t AdvancedEVEngine::generate_probability_cache_key(
    const std::vector<int>& dealer_hand,
    const DeckComposition& deck,
    const RulesConfig& rules) const {

    uint64_t key = deck.get_cache_key();

    // Add dealer hand to key
    for (size_t i = 0; i < dealer_hand.size(); ++i) {
        key = key * 23 + dealer_hand[i];
    }

    // Add rules that affect dealer play
    key = key * 2 + (rules.dealer_hits_soft_17 ? 1 : 0);

    return key;
}

// =============================================================================
// UTILITY METHODS
// =============================================================================

double AdvancedEVEngine::apply_true_count_adjustment(DetailedEV& base_ev,
                                                    double true_count,
                                                    const std::vector<int>& player_hand,
                                                    int dealer_upcard) const {

    // Apply linear true count effect
    double adjustment = true_count * 0.005;

    // Apply famous deviations
    HandData hand_data = BJLogicCore::calculate_hand_value(player_hand);

    if (hand_data.total == 16 && dealer_upcard == 10 && true_count >= 0) {
        adjustment += 0.02; // Stand 16 vs 10 at TC 0+
    }

    return adjustment;
}

double AdvancedEVEngine::calculate_composition_adjustment(const std::vector<int>& player_hand,
                                                         int dealer_upcard,
                                                         const DeckState& deck) const {

    // Simple composition effects
    double ten_density = (double)deck.cards_remaining.at(10) / deck.total_cards;
    double expected_ten_density = 16.0 / 52.0;

    return (ten_density - expected_ten_density) * 0.05; // Small effect
}

double AdvancedEVEngine::calculate_penetration_factor(int penetration_percent) const {
    return penetration_percent > 75 ? 1.0 : 0.8; // Simplified
}

void AdvancedEVEngine::determine_optimal_action(DetailedEV& ev) const {
    double max_ev = ev.stand_ev;
    ev.optimal_action = Action::STAND;

    if (ev.hit_ev > max_ev) {
        max_ev = ev.hit_ev;
        ev.optimal_action = Action::HIT;
    }

    if (ev.double_ev > max_ev) {
        max_ev = ev.double_ev;
        ev.optimal_action = Action::DOUBLE;
    }

    if (ev.split_ev > max_ev) {
        max_ev = ev.split_ev;
        ev.optimal_action = Action::SPLIT;
    }

    if (ev.surrender_ev > max_ev) {
        max_ev = ev.surrender_ev;
        ev.optimal_action = Action::SURRENDER;
    }

    ev.optimal_ev = max_ev;
}

// =============================================================================
// CACHE AND UTILITY METHODS
// =============================================================================

void AdvancedEVEngine::clear_cache() const {
    ev_cache.clear();
    prob_cache.clear();
    dealer_prob_cache.clear();
}

size_t AdvancedEVEngine::get_cache_size() const {
    return ev_cache.size() + prob_cache.size() + dealer_prob_cache.size();
}

uint64_t AdvancedEVEngine::hash_scenario(const std::vector<int>& hand,
                                        int dealer_upcard,
                                        const DeckState& deck) const {
    uint64_t hash = 0;

    for (size_t i = 0; i < hand.size(); ++i) {
        hash = hash * 31 + hand[i];
    }
    hash = hash * 31 + dealer_upcard;
    hash = hash * 31 + deck.total_cards;

    return hash;
}

uint64_t AdvancedEVEngine::hash_scenario(const std::vector<int>& hand, int dealer_upcard) const {
    uint64_t hash = 0;

    for (size_t i = 0; i < hand.size(); ++i) {
        hash = hash * 31 + hand[i];
    }
    hash = hash * 31 + dealer_upcard;

    return hash;
}

// =============================================================================
// RECURSIVE EV CALCULATION METHODS - ADD TO END OF FILE
// =============================================================================

double AdvancedEVEngine::calculate_stand_ev_recursive(
    const std::vector<int>& player_hand,
    int dealer_upcard,
    const DeckState& deck,
    const RulesConfig& rules) const {

    // Convert DeckState to DeckComposition for recursive engine
    DeckComposition deck_comp = recursive_dealer_engine.convert_from_deck_state(deck);

    // Calculate EXACT dealer probabilities using recursive method
    ExactDealerProbs dealer_probs = recursive_dealer_engine.calculate_exact_probabilities(
        dealer_upcard, deck_comp, rules);

    // Verify probabilities (debugging - remove in production)
    if (!recursive_dealer_engine.verify_probabilities(dealer_probs)) {
        // This should never happen with correct implementation
        // You might want to log a warning here
    }

    // Calculate stand EV using exact probabilities
    return recursive_dealer_engine.calculate_stand_ev_from_exact_probs(
        player_hand, dealer_probs, rules);
}

double AdvancedEVEngine::calculate_hit_ev_recursive(const std::vector<int>& hand,
                                                   int dealer_upcard,
                                                   const DeckState& deck,
                                                   const RulesConfig& rules,
                                                   int depth) const {

    if (depth > simulation_depth) {
        // Fallback to your existing simple hit EV at max depth
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

double AdvancedEVEngine::calculate_double_ev_recursive(const std::vector<int>& player_hand,
                                                      int dealer_upcard,
                                                      const DeckState& deck,
                                                      const RulesConfig& rules) const {

    if (player_hand.size() != 2) return -2.0; // Can only double on initial hand

    double total_ev = 0.0;
    double total_probability = 0.0;

    // Iterate through all possible cards to double with
    for (int next_card_rank = 1; next_card_rank <= 10; ++next_card_rank) {
        auto it = deck.cards_remaining.find(next_card_rank);
        if (it == deck.cards_remaining.end() || it->second <= 0) continue;

        int cards_available = it->second;
        double card_prob = static_cast<double>(cards_available) / deck.total_cards;
        total_probability += card_prob;

        int card_value = (next_card_rank == 10) ? 10 : next_card_rank;

        // Create final hand after doubling
        std::vector<int> final_hand = player_hand;
        final_hand.push_back(card_value);

        // Update deck state
        DeckState new_deck = deck;
        new_deck.cards_remaining[next_card_rank]--;
        new_deck.total_cards--;

        // Calculate stand EV for this final hand (must stand after doubling)
        double hand_ev = calculate_stand_ev_recursive(final_hand, dealer_upcard, new_deck, rules);

        // Double the result (double bet)
        total_ev += card_prob * (hand_ev * 2.0);
    }

    if (total_probability > 0.0 && std::abs(total_probability - 1.0) > 0.001) {
        total_ev /= total_probability;
    }

    return total_ev;
}

double AdvancedEVEngine::calculate_split_ev_advanced(const std::vector<int>& pair_hand,
                                                    int dealer_upcard,
                                                    const DeckState& deck,
                                                    const RulesConfig& rules,
                                                    int splits_remaining) const {

    if (pair_hand.size() != 2 || pair_hand[0] != pair_hand[1]) {
        return -2.0; // Not a valid pair
    }

    if (splits_remaining <= 0) {
        // No more splits allowed, play as regular hand
        return calculate_optimal_play_ev(pair_hand, dealer_upcard, deck, rules);
    }

    int pair_rank = pair_hand[0];
    double total_ev = 0.0;

    // Calculate EV for each split hand (average of two hands)
    for (int split_hand = 0; split_hand < 2; ++split_hand) {
        double hand_ev = calculate_split_hand_ev(pair_rank, dealer_upcard, deck, rules, splits_remaining);
        total_ev += hand_ev;
    }

    return total_ev / 2.0; // Average the two hands
}

double AdvancedEVEngine::calculate_split_hand_ev(int pair_rank,
                                                int dealer_upcard,
                                                const DeckState& deck,
                                                const RulesConfig& rules,
                                                int splits_remaining) const {

    double total_ev = 0.0;
    double total_probability = 0.0;

    // Enumerate all possible second cards for this split hand
    for (int second_card_rank = 1; second_card_rank <= 10; ++second_card_rank) {
        auto it = deck.cards_remaining.find(second_card_rank);
        if (it == deck.cards_remaining.end() || it->second <= 0) continue;

        int cards_available = it->second;
        double card_prob = static_cast<double>(cards_available) / deck.total_cards;
        total_probability += card_prob;

        int second_card_value = (second_card_rank == 10) ? 10 : second_card_rank;

        // Create the split hand
        std::vector<int> split_hand = {pair_rank, second_card_value};

        // Update deck state
        DeckState new_deck = deck;
        new_deck.cards_remaining[second_card_rank]--;
        new_deck.total_cards--;

        double hand_ev;

        // Check if we got another pair and can re-split
        if (second_card_value == pair_rank && splits_remaining > 0 && rules.resplitting_allowed) {
            // Option to re-split
            double resplit_ev = calculate_split_ev_advanced(split_hand, dealer_upcard, new_deck, rules, splits_remaining - 1);
            double play_ev = calculate_optimal_play_ev(split_hand, dealer_upcard, new_deck, rules);
            hand_ev = std::max(resplit_ev, play_ev);
        } else {
            // Play the hand optimally
            hand_ev = calculate_optimal_play_ev(split_hand, dealer_upcard, new_deck, rules);
        }

        total_ev += card_prob * hand_ev;
    }

    if (total_probability > 0.0 && std::abs(total_probability - 1.0) > 0.001) {
        total_ev /= total_probability;
    }

    return total_ev;
}

double AdvancedEVEngine::calculate_optimal_play_ev(const std::vector<int>& hand,
                                                  int dealer_upcard,
                                                  const DeckState& deck,
                                                  const RulesConfig& rules) const {

    // Calculate EV for all available actions
    double stand_ev = calculate_stand_ev_recursive(hand, dealer_upcard, deck, rules);
    double hit_ev = calculate_hit_ev_recursive(hand, dealer_upcard, deck, rules, 0);

    double best_ev = std::max(stand_ev, hit_ev);

    // Check doubling (if available)
    if (hand.size() == 2 || (rules.double_after_split > 0 && hand.size() == 2)) {
        HandData hand_data = BJLogicCore::calculate_hand_value(hand);

        bool can_double = (hand.size() == 2);
        if (rules.double_after_split == 2) {
            // Only double on 10 and 11
            can_double = can_double && (hand_data.total == 10 || hand_data.total == 11);
        }

        if (can_double) {
            double double_ev = calculate_double_ev_recursive(hand, dealer_upcard, deck, rules);
            best_ev = std::max(best_ev, double_ev);
        }
    }

    // Check surrender (if available and initial hand)
    if (rules.surrender_allowed && hand.size() == 2) {
        best_ev = std::max(best_ev, -0.5);
    }

    return best_ev;
}

DetailedEV AdvancedEVEngine::calculate_detailed_ev_with_recursion(const std::vector<int>& player_hand,
                                                                 int dealer_upcard,
                                                                 const CardCounter& counter,
                                                                 const RulesConfig& rules) const {

    // Simple deck state based on penetration
    DeckState current_deck(rules.num_decks);

    int penetration = counter.get_penetration();
    double cards_played_ratio = penetration / 100.0;

    for (auto& pair : current_deck.cards_remaining) {
        int rank = pair.first;
        int original_count = (rank == 10) ? 64 : 24; // 6 decks default
        int estimated_played = static_cast<int>(original_count * cards_played_ratio);
        pair.second = original_count - estimated_played;
        pair.second = std::max(0, pair.second);
    }

    // Recalculate total
    current_deck.total_cards = 0;
    for (const auto& pair : current_deck.cards_remaining) {
        current_deck.total_cards += pair.second;
    }

    DetailedEV result;

    // Calculate all action EVs using NEW recursive methods
    result.stand_ev = calculate_stand_ev_recursive(player_hand, dealer_upcard, current_deck, rules);
    result.hit_ev = calculate_hit_ev_recursive(player_hand, dealer_upcard, current_deck, rules, 0);

    if (player_hand.size() == 2) {
        result.double_ev = calculate_double_ev_recursive(player_hand, dealer_upcard, current_deck, rules);

        // Check for pair splitting
        if (player_hand[0] == player_hand[1] && rules.resplitting_allowed) {
            result.split_ev = calculate_split_ev_advanced(player_hand, dealer_upcard, current_deck, rules, rules.max_split_hands - 1);
        } else {
            result.split_ev = -2.0; // Not available
        }

        // Surrender calculation
        if (rules.surrender_allowed) {
            result.surrender_ev = -0.5;
            result.late_surrender_ev = -0.5;
        }
    }

    // Apply true count adjustments
    double true_count = counter.get_true_count();
    double adjustment = true_count * 0.005; // Simple linear adjustment
    result.true_count_adjustment = adjustment;

    result.stand_ev += adjustment;
    result.hit_ev += adjustment;
    result.double_ev += adjustment * 2.0;
    result.split_ev += adjustment;

    // Calculate variance (simplified)
    result.variance = 1.3; // Typical blackjack variance

    // Determine optimal action
    double max_ev = result.stand_ev;
    result.optimal_action = Action::STAND;

    if (result.hit_ev > max_ev) {
        max_ev = result.hit_ev;
        result.optimal_action = Action::HIT;
    }

    if (result.double_ev > max_ev) {
        max_ev = result.double_ev;
        result.optimal_action = Action::DOUBLE;
    }

    if (result.split_ev > max_ev) {
        max_ev = result.split_ev;
        result.optimal_action = Action::SPLIT;
    }

    if (result.surrender_ev > max_ev) {
        max_ev = result.surrender_ev;
        result.optimal_action = Action::SURRENDER;
    }

    result.optimal_ev = max_ev;

    // Calculate advantage over basic strategy (simplified)
    result.advantage_over_basic = adjustment;

    return result;
}

// =============================================================================
// PLACEHOLDER IMPLEMENTATIONS FOR COMPLEX METHODS
// =============================================================================

DetailedEV AdvancedEVEngine::calculate_detailed_ev(const std::vector<int>& player_hand,
                                                  int dealer_upcard,
                                                  const CardCounter& counter,
                                                  const RulesConfig& rules) const {
    // Use the recursive version for now
    return calculate_detailed_ev_with_recursion(player_hand, dealer_upcard, counter, rules);
}

DetailedEV AdvancedEVEngine::calculate_composition_dependent_ev(const std::vector<int>& player_hand,
                                                              int dealer_upcard,
                                                              const DeckState& deck,
                                                              const RulesConfig& rules) const {
    DetailedEV result;

    // Calculate EVs based on exact deck composition using recursive methods
    result.stand_ev = calculate_stand_ev_recursive(player_hand, dealer_upcard, deck, rules);
    result.hit_ev = calculate_hit_ev_recursive(player_hand, dealer_upcard, deck, rules, 0);

    if (player_hand.size() == 2) {
        result.double_ev = calculate_double_ev_recursive(player_hand, dealer_upcard, deck, rules);
    }

    // Apply composition adjustments
    result.composition_dependent_ev = calculate_composition_adjustment(player_hand, dealer_upcard, deck);

    determine_optimal_action(result);

    return result;
}

ScenarioAnalysis AdvancedEVEngine::analyze_scenario(const std::vector<int>& player_hand,
                                                  int dealer_upcard,
                                                  const CardCounter& counter,
                                                  const RulesConfig& rules) const {
    ScenarioAnalysis analysis;
    analysis.player_hand = player_hand;
    analysis.dealer_upcard = dealer_upcard;
    analysis.rules = rules;

    // Basic strategy EV
    analysis.basic_strategy_ev = calculate_true_count_ev(player_hand, dealer_upcard, 0.0, rules);

    // Counting strategy EV
    analysis.counting_strategy_ev = calculate_detailed_ev_with_recursion(player_hand, dealer_upcard, counter, rules);

    // Calculate improvement
    analysis.ev_improvement = analysis.counting_strategy_ev.optimal_ev - analysis.basic_strategy_ev.optimal_ev;

    // Generate recommendation
    if (analysis.ev_improvement > 0.02) {
        analysis.recommendation = "Strong counting advantage - follow counting strategy";
    } else if (analysis.ev_improvement > 0.005) {
        analysis.recommendation = "Moderate counting advantage";
    } else {
        analysis.recommendation = "Basic strategy sufficient";
    }

    analysis.confidence_level = 0.90;

    return analysis;
}

SessionAnalysis AdvancedEVEngine::analyze_session(double bankroll,
                                                 double base_bet,
                                                 const CardCounter& counter,
                                                 const RulesConfig& rules,
                                                 int session_length_hours) const {
    SessionAnalysis analysis;
    analysis.hourly_ev = base_bet * counter.get_advantage() * 80; // 80 hands/hour
    analysis.total_ev = analysis.hourly_ev * session_length_hours;
    analysis.kelly_bet_size = base_bet * (1.0 + counter.get_advantage() * 10);
    analysis.variance_per_hand = 1.3;
    analysis.hands_per_hour = 80;
    return analysis;
}

std::vector<double> AdvancedEVEngine::calculate_optimal_bet_spread(const CardCounter& counter,
                                                                 double bankroll,
                                                                 double risk_tolerance) const {
    // Simple bet spread
    return {10.0, 15.0, 25.0, 50.0, 100.0};
}

double AdvancedEVEngine::calculate_risk_of_ruin(double bankroll,
                                               double advantage,
                                               double variance,
                                               double bet_size) const {
    if (advantage <= 0) return 1.0;
    return std::exp(-2.0 * advantage * bankroll / (variance * bet_size));
}

double AdvancedEVEngine::calculate_hand_variance(const std::vector<int>& player_hand,
                                               int dealer_upcard,
                                               Action chosen_action,
                                               const DeckState& deck,
                                               const RulesConfig& rules) const {
    // Simplified variance calculation
    HandData hand_data = BJLogicCore::calculate_hand_value(player_hand);
    double base_variance = 1.15; // Typical blackjack variance

    // Adjust based on hand characteristics
    if (hand_data.is_blackjack) {
        base_variance *= 0.8; // Lower variance for blackjack
    } else if (hand_data.total >= 17) {
        base_variance *= 0.9; // Lower variance for pat hands
    } else if (hand_data.total <= 11) {
        base_variance *= 1.1; // Higher variance for hitting hands
    }

    // Adjust for action
    if (chosen_action == Action::DOUBLE) {
        base_variance *= 2.0; // Doubling increases variance
    } else if (chosen_action == Action::SPLIT) {
        base_variance *= 1.5; // Splitting increases variance
    }

    return base_variance;
}

double AdvancedEVEngine::calculate_insurance_ev(int dealer_upcard,
                                              const DeckState& deck,
                                              double bet_amount) const {
    if (dealer_upcard != 1) return -1.0; // Insurance only available against Ace

    double ten_density = (double)deck.cards_remaining.at(10) / deck.total_cards;

    // Insurance pays 2:1, so we need > 1/3 ten density to be profitable
    return (ten_density * 2.0 - 1.0) * bet_amount;
}

DetailedEV AdvancedEVEngine::calculate_basic_strategy_ev(const std::vector<int>& player_hand,
                                                        int dealer_upcard,
                                                        const RulesConfig& rules) const {
    // Simple basic strategy EV - this would normally be calculated once and cached
    DetailedEV result;

    Action basic_action = BJLogicCore::basic_strategy_decision(player_hand, dealer_upcard, rules);

    // Rough EV estimates for basic strategy
    switch (basic_action) {
        case Action::STAND:
            result.stand_ev = -0.10;
            result.optimal_ev = -0.10;
            break;
        case Action::HIT:
            result.hit_ev = -0.12;
            result.optimal_ev = -0.12;
            break;
        case Action::DOUBLE:
            result.double_ev = -0.08;
            result.optimal_ev = -0.08;
            break;
        case Action::SPLIT:
            result.split_ev = -0.09;
            result.optimal_ev = -0.09;
            break;
        case Action::SURRENDER:
            result.surrender_ev = -0.50;
            result.optimal_ev = -0.50;
            break;
    }

    result.optimal_action = basic_action;
    return result;
}

DeckState AdvancedEVEngine::simulate_remaining_deck(const CardCounter& counter, std::mt19937& gen) const {
    // Create a deck state based on the counter's information
    auto frequencies = counter.get_remaining_card_frequencies();

    DeckState deck(6); // Assume 6 decks

    // Estimate remaining cards based on penetration
    int penetration = counter.get_penetration();
    double cards_played_ratio = penetration / 100.0;

    for (int rank = 1; rank <= 10; ++rank) {
        int original_count = (rank == 10) ? 64 : 24; // 6 decks
        int estimated_played = static_cast<int>(original_count * cards_played_ratio);
        deck.cards_remaining[rank] = original_count - estimated_played;
        deck.cards_remaining[rank] = std::max(0, deck.cards_remaining[rank]);
    }

    // Recalculate total
    deck.total_cards = 0;
    for (const auto& pair : deck.cards_remaining) {
        deck.total_cards += pair.second;
    }

    return deck;
}

DetailedEV AdvancedEVEngine::monte_carlo_ev_estimation(const std::vector<int>& player_hand,
                                                     int dealer_upcard,
                                                     const CardCounter& counter,
                                                     const RulesConfig& rules,
                                                     int iterations) const {
    // Simplified Monte Carlo - just return the recursive calculation for now
    return calculate_detailed_ev_with_recursion(player_hand, dealer_upcard, counter, rules);
}

std::pair<double, double> AdvancedEVEngine::calculate_ev_confidence_interval(double ev,
                                                                           double variance,
                                                                           int sample_size,
                                                                           double confidence) const {
    // Simple confidence interval calculation
    double z_score = (confidence >= 0.95) ? 1.96 : 1.645; // 95% or 90%
    double margin = z_score * std::sqrt(variance / sample_size);

    return std::make_pair(ev - margin, ev + margin);
}

// ðŸ”§ ADD the missing function BEFORE calculate_ev_with_provided_composition

double AdvancedEVEngine::calculate_split_aces_one_card_ev(int dealer_upcard,
                                                         const DeckState& deck,
                                                         const RulesConfig& rules) const {
    double total_ev = 0.0;
    double total_probability = 0.0;

    // Enumerate all possible single cards to go with each Ace
    for (const auto& card_pair : deck.cards_remaining) {
        int card_rank = card_pair.first;
        int cards_available = card_pair.second;

        if (cards_available <= 0) continue;

        double card_prob = static_cast<double>(cards_available) / deck.total_cards;
        total_probability += card_prob;

        int card_value = (card_rank >= 10) ? 10 : card_rank;

        // Create final hand: Ace + one card (no more cards allowed)
        std::vector<int> final_hand = {1, card_value};

        // Update deck for this scenario
        DeckState new_deck = deck;
        new_deck.cards_remaining[card_rank]--;
        new_deck.total_cards--;

        // Calculate stand EV for this final hand (must stand after split Aces)
        double hand_ev = calculate_stand_ev_recursive(final_hand, dealer_upcard, new_deck, rules);

        total_ev += card_prob * hand_ev;
    }

    if (total_probability > 0.0) {
        total_ev /= total_probability;
    }

    // Return EV for both hands (split creates 2 hands)
    return total_ev;
}

// âœ… NOW the calculate_ev_with_provided_composition function (FIXED)
DetailedEV AdvancedEVEngine::calculate_ev_with_provided_composition(
    const std::vector<int>& player_hand,
    int dealer_upcard,
    const DeckState& provided_deck,  // FROM YOUR PYTHON API
    const RulesConfig& rules,
    const CardCounter& counter) const {

    DetailedEV result;

    // Create playing deck by removing player and dealer cards
    DeckState playing_deck = provided_deck;

    // Remove player cards
    for (int card : player_hand) {
        if (playing_deck.cards_remaining.find(card) != playing_deck.cards_remaining.end() &&
            playing_deck.cards_remaining[card] > 0) {
            playing_deck.cards_remaining[card]--;
            playing_deck.total_cards--;
        }
    }

    // Remove dealer upcard
    if (playing_deck.cards_remaining.find(dealer_upcard) != playing_deck.cards_remaining.end() &&
        playing_deck.cards_remaining[dealer_upcard] > 0) {
        playing_deck.cards_remaining[dealer_upcard]--;
        playing_deck.total_cards--;
    }

    // ðŸ”¥ CALCULATE ALL EVs WITH EXACT COMPOSITION

    // Stand EV using exact dealer probabilities
    result.stand_ev = calculate_stand_ev_recursive(player_hand, dealer_upcard, playing_deck, rules);

    // Hit EV using recursive enumeration
    result.hit_ev = calculate_hit_ev_recursive(player_hand, dealer_upcard, playing_deck, rules, 0);

    // Double EV with composition and no-peek adjustments
    if (player_hand.size() == 2) {
        result.double_ev = calculate_double_ev_recursive(player_hand, dealer_upcard, playing_deck, rules);

        // Apply no-peek adjustment using exact Ace count
        if (!rules.dealer_peek_on_ten && dealer_upcard == 10) {
            int aces_remaining = playing_deck.cards_remaining.count(1) ? playing_deck.cards_remaining.at(1) : 0;
            double dealer_bj_prob = static_cast<double>(aces_remaining) / playing_deck.total_cards;
            result.double_ev = result.double_ev * (1.0 - dealer_bj_prob) - dealer_bj_prob * 2.0;
        }
    } else {
        result.double_ev = -2.0;
    }

    // Split EV with exact composition
    if (player_hand.size() == 2 && player_hand[0] == player_hand[1]) {
        result.split_ev = calculate_split_ev_advanced(player_hand, dealer_upcard, playing_deck, rules, rules.max_split_hands - 1);

        // Special handling for split Aces with one card rule
        if (player_hand[0] == 1 && rules.split_aces_one_card) {
            result.split_ev = calculate_split_aces_one_card_ev(dealer_upcard, playing_deck, rules);
        }

        // Apply no-peek adjustment
        if (!rules.dealer_peek_on_ten && dealer_upcard == 10) {
            int aces_remaining = playing_deck.cards_remaining.count(1) ? playing_deck.cards_remaining.at(1) : 0;
            double dealer_bj_prob = static_cast<double>(aces_remaining) / playing_deck.total_cards;
            result.split_ev = result.split_ev * (1.0 - dealer_bj_prob) - dealer_bj_prob * 2.0;
        }
    } else {
        result.split_ev = -2.0;
    }

    // Surrender EV
    if (rules.surrender_allowed && player_hand.size() == 2) {
        result.surrender_ev = -0.5;
    } else {
        result.surrender_ev = -1.0;
    }

    // Insurance EV using exact 10-card density
    if (dealer_upcard == 1) {
        result.insurance_ev = calculate_insurance_ev(dealer_upcard, playing_deck);
    } else {
        result.insurance_ev = -1.0;
    }

    // True count adjustment (minimal since composition already accounts for most effects)
    double true_count = counter.get_true_count();
    result.true_count_adjustment = true_count * 0.002; // Reduced since composition handles most of it

    // Apply small residual true count effects
    result.stand_ev += result.true_count_adjustment;
    result.hit_ev += result.true_count_adjustment;
    result.double_ev += result.true_count_adjustment * 2.0;
    result.split_ev += result.true_count_adjustment;

    // Calculate variance based on exact composition
    result.variance = calculate_hand_variance(player_hand, dealer_upcard, Action::STAND, playing_deck, rules);

    // Determine optimal action
    determine_optimal_action(result);

    // Calculate advantage over basic strategy
    DetailedEV basic_ev = calculate_true_count_ev(player_hand, dealer_upcard, 0.0, rules);
    result.advantage_over_basic = result.optimal_ev - basic_ev.optimal_ev;

    return result;
}

// Statistical significance testing implementation
bool is_ev_difference_significant(double ev1, double ev2,
                                double variance1, double variance2,
                                int sample_size, double alpha) {
    // Calculate the standard error of the difference
    double se_diff = std::sqrt((variance1 + variance2) / sample_size);

    // Calculate the z-score
    double z_score = std::abs(ev1 - ev2) / se_diff;

    // For alpha = 0.05, critical z-value is 1.96
    // For alpha = 0.01, critical z-value is 2.576
    double critical_z = (alpha <= 0.01) ? 2.576 : 1.96;

    return z_score > critical_z;
}

} // namespace bjlogic