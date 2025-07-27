// cpp_src/advanced_ev_engine.hpp
/*
 * Advanced Expected Value Calculation Engine - COMPLETE PROFESSIONAL VERSION
 * Sophisticated algorithms for precise EV calculations per hand
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

struct ScenarioAnalysis {
    std::vector<int> player_hand;
    int dealer_upcard;
    CountState count_state;
    DeckState deck_composition;
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
    // Caching for performance
    mutable std::unordered_map<uint64_t, DetailedEV> ev_cache;
    mutable std::unordered_map<uint64_t, double> prob_cache;

    // Precomputed lookup tables for speed
    std::array<std::array<double, 10>, 22> dealer_outcome_matrix;
    std::array<std::array<double, 10>, 22> player_bust_matrix;

    // Engine parameters
    int simulation_depth;
    double precision_threshold;
    bool use_composition_dependent;
    bool use_variance_reduction;

public:
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
    // RECURSIVE EV CALCULATION (SOPHISTICATED ALGORITHM)
    // =================================================================

    // Recursive hit EV calculation with depth control
    double calculate_hit_ev_recursive(const std::vector<int>& hand,
                                    int dealer_upcard,
                                    const DeckState& deck,
                                    const RulesConfig& rules,
                                    int depth = 0) const;

    // Recursive dealer outcome calculation
    double calculate_dealer_final_ev(int dealer_upcard,
                                   const std::vector<int>& dealer_hand,
                                   const DeckState& deck,
                                   const RulesConfig& rules) const;

    // Split EV with recursive analysis for multiple splits
    double calculate_split_ev_advanced(const std::vector<int>& pair_hand,
                                     int dealer_upcard,
                                     const DeckState& deck,
                                     const RulesConfig& rules,
                                     int splits_remaining = 3) const;

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

    // Blackjack probability calculations
    double calculate_dealer_blackjack_prob(int dealer_upcard,
                                         const DeckState& deck) const;

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

    // Insurance EV with precise calculations
    double calculate_insurance_ev(int dealer_upcard,
                                const DeckState& deck,
                                double bet_amount = 1.0) const;

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

    // Hash functions for caching
    uint64_t hash_scenario(const std::vector<int>& hand,
                          int dealer_upcard,
                          const DeckState& deck) const;

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

    double calculate_optimal_play_ev(const std::vector<int>& hand,
                                   int dealer_upcard,
                                   const DeckState& deck,
                                   const RulesConfig& rules) const;

    double calculate_dealer_final_probability(int dealer_upcard,
                                            int final_total,
                                            const DeckState& deck,
                                            const RulesConfig& rules) const;

    double calculate_dealer_total_recursive(int upcard,
                                          const std::vector<int>& dealer_hand,
                                          int target_total,
                                          const DeckState& deck,
                                          const RulesConfig& rules) const;

    double calculate_dealer_bust_recursive(int upcard,
                                         const std::vector<int>& dealer_hand,
                                         const DeckState& deck,
                                         const RulesConfig& rules) const;

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