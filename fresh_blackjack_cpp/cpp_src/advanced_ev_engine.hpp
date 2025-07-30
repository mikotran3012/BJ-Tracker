// cpp_src/advanced_ev_engine.hpp - FIXED VERSION (REMOVE DUPLICATES)
/*
 * Advanced Expected Value Calculation Engine - COMPLETE PROFESSIONAL VERSION
 * Sophisticated algorithms for precise EV calculations per hand + Dealer Probability Engine
 */

#ifndef ADVANCED_EV_ENGINE_HPP
#define ADVANCED_EV_ENGINE_HPP

#include "bjlogic_core.hpp"
#include "card_counting.hpp"
#include <unordered_map>
#include <array>
#include <vector>
#include <memory>
#include <random>
#include <chrono>

namespace bjlogic {

// =============================================================================
// ADVANCED EV STRUCTURES
// =============================================================================

struct DetailedEV {
    // Core action EVs
    double stand_ev;
    double hit_ev;
    double double_ev;
    double split_ev;
    double surrender_ev;
    double insurance_ev;

    // Advanced metrics
    double composition_dependent_ev;
    double true_count_adjustment;
    double penetration_factor;
    double variance;
    double risk_of_ruin;

    // Optimal decision
    Action optimal_action;
    double optimal_ev;
    double advantage_over_basic;

    // Scenario-specific
    double early_surrender_ev;
    double late_surrender_ev;
    double das_adjustment;  // Double after split

    DetailedEV() : stand_ev(-1.0), hit_ev(-1.0), double_ev(-1.0),
                   split_ev(-1.0), surrender_ev(-0.5), insurance_ev(-1.0),
                   composition_dependent_ev(0.0), true_count_adjustment(0.0),
                   penetration_factor(1.0), variance(1.0), risk_of_ruin(0.0),
                   optimal_action(Action::STAND), optimal_ev(-1.0),
                   advantage_over_basic(0.0), early_surrender_ev(-0.5),
                   late_surrender_ev(-0.5), das_adjustment(0.0) {}
};

// =============================================================================
// DEALER PROBABILITY ENGINE STRUCTURES
// =============================================================================

struct DealerProbabilities {
    double bust_prob;           // Probability of busting (>21)
    double blackjack_prob;      // Probability of natural 21
    double total_17_prob;       // Probability of ending on 17
    double total_18_prob;       // Probability of ending on 18
    double total_19_prob;       // Probability of ending on 19
    double total_20_prob;       // Probability of ending on 20
    double total_21_prob;       // Probability of ending on 21 (non-natural)

    // Full distribution array [0-21] for advanced analysis
    std::array<double, 22> total_distribution;

    // Metadata
    int calculations_performed;
    bool from_cache;

    DealerProbabilities() : bust_prob(0.0), blackjack_prob(0.0),
                           total_17_prob(0.0), total_18_prob(0.0),
                           total_19_prob(0.0), total_20_prob(0.0), total_21_prob(0.0),
                           calculations_performed(0), from_cache(false) {
        total_distribution.fill(0.0);
    }

    // Convenience method to get probability for specific total
    double get_total_prob(int total) const {
        if (total >= 0 && total < 22) return total_distribution[total];
        return 0.0;
    }

    // Get combined probabilities for ranges
    double get_range_prob(int min_total, int max_total) const {
        double prob = 0.0;
        for (int i = std::max(0, min_total); i <= std::min(21, max_total); ++i) {
            prob += total_distribution[i];
        }
        return prob;
    }
};

struct DeckComposition {
    std::array<int, 13> cards_remaining;  // A,2,3,4,5,6,7,8,9,T,J,Q,K
    int total_cards;

    DeckComposition(int num_decks = 6) : total_cards(52 * num_decks) {
        // Initialize standard composition
        for (int i = 0; i < 9; ++i) {  // A,2-9
            cards_remaining[i] = 4 * num_decks;
        }
        // 10,J,Q,K all worth 10
        for (int i = 9; i < 13; ++i) {
            cards_remaining[i] = 4 * num_decks;
        }
    }

    // Remove a card and update total
    void remove_card(int rank) {
        if (rank >= 1 && rank <= 13 && cards_remaining[rank-1] > 0) {
            cards_remaining[rank-1]--;
            total_cards--;
        }
    }

    // Add a card back (for backtracking)
    void add_card(int rank) {
        if (rank >= 1 && rank <= 13) {
            cards_remaining[rank-1]++;
            total_cards++;
        }
    }

    // Get number of cards remaining for a rank
    int get_remaining(int rank) const {
        if (rank >= 1 && rank <= 13) return cards_remaining[rank-1];
        return 0;
    }

    // Get total 10-value cards (10,J,Q,K)
    int get_ten_cards() const {
        return cards_remaining[9] + cards_remaining[10] + cards_remaining[11] + cards_remaining[12];
    }

    // Generate cache key based on remaining cards
    uint64_t get_cache_key() const {
        uint64_t key = 0;
        for (int i = 0; i < 13; ++i) {
            key = key * 53 + cards_remaining[i];  // 53 is prime > max cards per rank
        }
        return key;
    }

    // Check if deck is valid
    bool is_valid() const {
        return total_cards >= 0 && total_cards <= 416; // Max 8 decks
    }
};

struct ScenarioAnalysis {
    std::vector<int> player_hand;
    int dealer_upcard;
    DeckComposition deck_composition;
    RulesConfig rules;

    DetailedEV basic_strategy_ev;
    DetailedEV counting_strategy_ev;
    DetailedEV composition_dependent_ev;

    double ev_improvement;
    std::string recommendation;
    double confidence_level;
};

struct SessionAnalysis {
    double total_ev;
    double hourly_ev;
    double standard_deviation;
    double risk_of_ruin;
    double kelly_bet_size;
    double optimal_session_length;
    double variance_per_hand;
    int hands_per_hour;

    SessionAnalysis() : total_ev(0.0), hourly_ev(0.0), standard_deviation(1.0),
                       risk_of_ruin(0.0), kelly_bet_size(1.0),
                       optimal_session_length(4.0), variance_per_hand(1.0),
                       hands_per_hour(80) {}
};

// =============================================================================
// ADVANCED EV CALCULATION ENGINE
// =============================================================================

class AdvancedEVEngine {
private:
    // =================================================================
    // NEW RECURSIVE DEALER PROBABILITY METHODS
    // =================================================================

    // Helper methods for dealer logic (based on John Nairn's approach)
    bool dealer_must_hit_by_total(int total, bool is_soft, const RulesConfig& rules) const;
    int get_card_value(int rank) const;

    // Utility conversion method
    DeckComposition convert_deck_state_to_composition(const DeckState& deck_state) const;

    // Verification method
    bool verify_dealer_probabilities(const DealerProbabilities& probs) const;

    // =================================================================
    // EXISTING METHODS (make sure these exist)
    // =================================================================

    // Cache key generation for probability results
    uint64_t generate_probability_cache_key(
        const std::vector<int>& dealer_hand,
        const DeckComposition& deck,
        const RulesConfig& rules) const;

    // Helper methods for dealer probability calculations
    bool dealer_must_hit(const std::vector<int>& dealer_hand, const RulesConfig& rules) const;
    bool is_fresh_deck(const DeckComposition& deck) const;

    // Simplified methods for basic calculations
    double calculate_simple_hit_ev(const std::vector<int>& hand,
                                 int dealer_upcard,
                                 const DeckState& deck,
                                 const RulesConfig& rules) const;

    double calculate_dealer_bust_probability(int dealer_upcard,
                                           const DeckState& deck,
                                           const RulesConfig& rules) const;

    double calculate_player_bust_probability(const std::vector<int>& hand,
                                           const DeckState& deck) const;

    void determine_optimal_action(DetailedEV& ev) const;

    // Hash functions
    uint64_t hash_scenario(const std::vector<int>& hand, int dealer_upcard) const;
    uint64_t hash_scenario(const std::vector<int>& hand,
                          int dealer_upcard,
                          const DeckState& deck) const;

    // Dealer probability helper methods
    bool dealer_must_hit_by_total(int total, bool is_soft, const RulesConfig& rules) const;
    int get_card_value(int rank) const;

    // No-peek rule support
    DealerProbabilities calculate_dealer_probabilities_no_peek(
        int dealer_upcard,
        const DeckComposition& deck,
        const RulesConfig& rules) const;

    // Exact stand EV calculation
    double calculate_stand_ev_with_exact_probabilities(
        const std::vector<int>& player_hand,
        int dealer_upcard,
        const DeckState& deck,
        const RulesConfig& rules) const;

    // Utility methods
    DeckComposition convert_deck_state_to_composition(const DeckState& deck_state) const;
    bool verify_dealer_probabilities(const DealerProbabilities& probs) const;

    // Split Aces one card calculation
    double calculate_split_aces_one_card_ev(int dealer_upcard,
                                           const DeckState& deck,
                                           const RulesConfig& rules) const;

    // Caching for performance
    mutable std::unordered_map<uint64_t, DetailedEV> ev_cache;
    mutable std::unordered_map<uint64_t, double> prob_cache;

    // Dealer probability cache
    mutable std::unordered_map<uint64_t, DealerProbabilities> dealer_prob_cache;

    // Performance tracking
    mutable int cache_hits;
    mutable int cache_misses;
    mutable int recursive_calls;

    // Precomputed lookup tables for speed
    std::array<std::array<double, 10>, 22> dealer_outcome_matrix;
    std::array<std::array<double, 10>, 22> player_bust_matrix;

    // Engine parameters
    int simulation_depth;
    double precision_threshold;
    bool use_composition_dependent;
    bool use_variance_reduction;

public:
    // Composition-aware EV calculation
    DetailedEV calculate_ev_with_provided_composition(
        const std::vector<int>& player_hand,
        int dealer_upcard,
        const DeckState& provided_deck,    // FROM PYTHON API
        const RulesConfig& rules,
        const CardCounter& counter) const;

    AdvancedEVEngine(int depth = 10, double precision = 0.0001);

    // =================================================================
    // CORE EV CALCULATION METHODS
    // =================================================================

    // Comprehensive EV calculation for any scenario
    DetailedEV calculate_detailed_ev(const std::vector<int>& player_hand,
                                   int dealer_upcard,
                                   const CardCounter& counter,
                                   const RulesConfig& rules) const;

    // Composition-dependent strategy calculations
    DetailedEV calculate_composition_dependent_ev(const std::vector<int>& player_hand,
                                                int dealer_upcard,
                                                const DeckState& deck,
                                                const RulesConfig& rules) const;

    // True count adjusted EV
    DetailedEV calculate_true_count_ev(const std::vector<int>& player_hand,
                                     int dealer_upcard,
                                     double true_count,
                                     const RulesConfig& rules) const;

    // =================================================================
    // DEALER PROBABILITY ENGINE
    // =================================================================

    // Main probability calculation with caching
    DealerProbabilities calculate_dealer_probabilities_advanced(
        int dealer_upcard,
        const DeckComposition& deck,
        const RulesConfig& rules) const;

    // Recursive probability engine
    DealerProbabilities calculate_dealer_probabilities_recursive(
        const std::vector<int>& dealer_hand,
        const DeckComposition& deck,
        const RulesConfig& rules,
        int depth = 0) const;

    // Optimized calculation for fresh deck
    DealerProbabilities calculate_dealer_probabilities_fresh_deck(
        int dealer_upcard,
        const RulesConfig& rules) const;

    // Probability calculation with removed cards tracking
    DealerProbabilities calculate_dealer_probabilities_with_removed(
        int dealer_upcard,
        const std::vector<int>& removed_cards,
        const RulesConfig& rules) const;

    // =================================================================
    // RECURSIVE EV CALCULATION METHODS
    // =================================================================

    // Recursive stand EV calculation
    double AdvancedEVEngine::calculate_stand_ev_recursive(const std::vector<int>& player_hand,
                                                     int dealer_upcard,
                                                     const DeckState& deck,
                                                     const RulesConfig& rules) const {
    return calculate_stand_ev_with_exact_probabilities(player_hand, dealer_upcard, deck, rules);
}

    // Recursive hit EV calculation with depth control
    double calculate_hit_ev_recursive(const std::vector<int>& hand,
                                     int dealer_upcard,
                                     const DeckState& deck,
                                     const RulesConfig& rules,
                                     int depth = 0) const;

    // Recursive double EV calculation
    double calculate_double_ev_recursive(const std::vector<int>& player_hand,
                                        int dealer_upcard,
                                        const DeckState& deck,
                                        const RulesConfig& rules) const;

    // Split EV with recursive analysis for multiple splits
    double calculate_split_ev_advanced(const std::vector<int>& pair_hand,
                                      int dealer_upcard,
                                      const DeckState& deck,
                                      const RulesConfig& rules,
                                      int splits_remaining = 3) const;

    // Helper for split hand enumeration
    double calculate_split_hand_ev(int pair_rank,
                                  int dealer_upcard,
                                  const DeckState& deck,
                                  const RulesConfig& rules,
                                  int splits_remaining) const;

    // Optimal play calculation using recursive methods
    double calculate_optimal_play_ev(const std::vector<int>& hand,
                                    int dealer_upcard,
                                    const DeckState& deck,
                                    const RulesConfig& rules) const;

    // Enhanced detailed EV calculation using recursive methods
    DetailedEV calculate_detailed_ev_with_recursion(const std::vector<int>& player_hand,
                                                   int dealer_upcard,
                                                   const CardCounter& counter,
                                                   const RulesConfig& rules) const;

    // =================================================================
    // PROBABILITY CALCULATIONS
    // =================================================================

    // Precise dealer bust probability based on exact deck composition
    double calculate_dealer_bust_probability(int dealer_upcard,
                                           const DeckState& deck,
                                           const RulesConfig& rules) const;

    // Player bust probability for hit decisions
    double calculate_player_bust_probability(const std::vector<int>& hand,
                                           const DeckState& deck) const;

    // Insurance EV with precise calculations
    double calculate_insurance_ev(int dealer_upcard,
                                const DeckState& deck,
                                double bet_amount = 1.0) const;

    // =================================================================
    // ADVANCED ANALYSIS METHODS
    // =================================================================

    // Complete scenario analysis
    ScenarioAnalysis analyze_scenario(const std::vector<int>& player_hand,
                                    int dealer_upcard,
                                    const CardCounter& counter,
                                    const RulesConfig& rules) const;

    // Session-level analysis
    SessionAnalysis analyze_session(double bankroll,
                                  double base_bet,
                                  const CardCounter& counter,
                                  const RulesConfig& rules,
                                  int session_length_hours = 4) const;

    // =================================================================
    // OPTIMIZATION AND TUNING
    // =================================================================

    // Find optimal betting strategy
    std::vector<double> calculate_optimal_bet_spread(const CardCounter& counter,
                                                   double bankroll,
                                                   double risk_tolerance = 0.01) const;

    // Risk analysis
    double calculate_risk_of_ruin(double bankroll,
                                double advantage,
                                double variance,
                                double bet_size) const;

    // Variance calculations
    double calculate_hand_variance(const std::vector<int>& player_hand,
                                 int dealer_upcard,
                                 Action chosen_action,
                                 const DeckState& deck,
                                 const RulesConfig& rules) const;

    // =================================================================
    // PERFORMANCE AND CACHING
    // =================================================================

    // Cache management
    void clear_cache() const;
    size_t get_cache_size() const;
    void precompute_tables();

    // Engine configuration
    void set_simulation_depth(int depth) { simulation_depth = depth; }
    void set_precision_threshold(double threshold) { precision_threshold = threshold; }
    void enable_composition_dependent(bool enable) { use_composition_dependent = enable; }

    // =================================================================
    // MONTE CARLO INTEGRATION
    // =================================================================

    // Monte Carlo EV estimation for complex scenarios
    DetailedEV monte_carlo_ev_estimation(const std::vector<int>& player_hand,
                                       int dealer_upcard,
                                       const CardCounter& counter,
                                       const RulesConfig& rules,
                                       int iterations = 100000) const;

    // Confidence intervals for EV estimates
    std::pair<double, double> calculate_ev_confidence_interval(double ev,
                                                             double variance,
                                                             int sample_size,
                                                             double confidence = 0.95) const;

private:
    // =================================================================
    // HELPER METHODS FOR SOPHISTICATED CALCULATIONS
    // =================================================================

    double calculate_stand_ev_advanced(const std::vector<int>& player_hand,
                                     int dealer_upcard,
                                     const DeckState& deck,
                                     const RulesConfig& rules) const;

    double calculate_double_ev_advanced(const std::vector<int>& player_hand,
                                      int dealer_upcard,
                                      const DeckState& deck,
                                      const RulesConfig& rules) const;

    // =================================================================
    // DEALER PROBABILITY HELPER METHODS
    // =================================================================

    // Cache key generation for probability results
    uint64_t generate_probability_cache_key(
        const std::vector<int>& dealer_hand,
        const DeckComposition& deck,
        const RulesConfig& rules) const;

    // Helper methods for dealer probability calculations
    bool dealer_must_hit(const std::vector<int>& dealer_hand, const RulesConfig& rules) const;
    int calculate_dealer_total(const std::vector<int>& dealer_hand) const;
    bool is_dealer_soft(const std::vector<int>& dealer_hand) const;
    bool is_fresh_deck(const DeckComposition& deck) const;

    // =================================================================
    // TRUE COUNT AND COMPOSITION ADJUSTMENTS
    // =================================================================

    double apply_true_count_adjustment(DetailedEV& base_ev,
                                     double true_count,
                                     const std::vector<int>& player_hand,
                                     int dealer_upcard) const;

    double calculate_composition_adjustment(const std::vector<int>& player_hand,
                                          int dealer_upcard,
                                          const DeckState& deck) const;

    double calculate_penetration_factor(int penetration_percent) const;

    void determine_optimal_action(DetailedEV& ev) const;

    // =================================================================
    // SIMPLIFIED METHODS FOR MISSING COMPLEX CALCULATIONS
    // =================================================================

    double calculate_simple_hit_ev(const std::vector<int>& hand,
                                 int dealer_upcard,
                                 const DeckState& deck,
                                 const RulesConfig& rules) const;

    DetailedEV calculate_basic_strategy_ev(const std::vector<int>& player_hand,
                                         int dealer_upcard,
                                         const RulesConfig& rules) const;

    DeckState simulate_remaining_deck(const CardCounter& counter, std::mt19937& gen) const;

    // Simple hash for basic scenarios
    uint64_t hash_scenario(const std::vector<int>& hand, int dealer_upcard) const;
    uint64_t hash_scenario(const std::vector<int>& hand,
                          int dealer_upcard,
                          const DeckState& deck) const;
};

// =============================================================================
// SPECIALIZED EV CALCULATORS
// =============================================================================

class TournamentEVCalculator {
public:
    // Tournament-specific EV calculations
    double calculate_tournament_ev(const std::vector<int>& hand,
                                 int dealer_upcard,
                                 int chips_remaining,
                                 int rounds_remaining,
                                 const RulesConfig& rules) const;

    // Optimal tournament betting strategy
    double calculate_optimal_tournament_bet(int current_chips,
                                          int target_chips,
                                          int rounds_remaining) const;
};

class ProgressiveEVCalculator {
public:
    // Progressive betting system analysis
    double calculate_progressive_ev(const std::vector<double>& bet_progression,
                                  double win_probability,
                                  int max_progression_length) const;

    // Martingale system risk analysis
    double calculate_martingale_risk(double base_bet,
                                   double bankroll,
                                   int max_doubles) const;
};

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

// Convert detailed EV to simple format for compatibility
EVResult detailed_to_simple_ev(const DetailedEV& detailed);

// Compare two EV calculations
double calculate_ev_difference(const DetailedEV& ev1, const DetailedEV& ev2);

// Format EV results for display
std::string format_ev_analysis(const DetailedEV& ev, bool verbose = false);

// Statistical significance testing
bool is_ev_difference_significant(double ev1, double ev2,
                                double variance1, double variance2,
                                int sample_size, double alpha = 0.05);

} // namespace bjlogic

#endif // ADVANCED_EV_ENGINE_HPP