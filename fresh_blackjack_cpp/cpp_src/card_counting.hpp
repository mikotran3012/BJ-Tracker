// cpp_src/card_counting.hpp - COMPLETE VERSION WITH UAPC
/*
 * Phase 2.3: Advanced Card Counting & Probability Engine
 */

#ifndef CARD_COUNTING_HPP
#define CARD_COUNTING_HPP

#include "bjlogic_core.hpp"
#include <unordered_map>
#include <array>
#include <random>

namespace bjlogic {

// =============================================================================
// CARD COUNTING SYSTEMS
// =============================================================================

enum class CountingSystem {
    HI_LO = 0,
    HI_OPT_I = 1,
    HI_OPT_II = 2,
    OMEGA_II = 3,
    ZEN_COUNT = 4,
    USTON_APC = 5,
    REVERE_RAPC = 6,
    RED_7 = 7
};

struct CountingValues {
    std::array<int, 10> values;  // A,2,3,4,5,6,7,8,9,T
    std::string name;
    double betting_correlation;
    double playing_efficiency;
    double insurance_correlation;

    // Default constructor
    CountingValues() : values{0}, name("None"),
                      betting_correlation(0.0), playing_efficiency(0.0),
                      insurance_correlation(0.0) {}

    // Constructor for initialization
    CountingValues(const std::array<int, 10>& vals, const std::string& n,
                   double bc, double pe, double ic)
        : values(vals), name(n), betting_correlation(bc),
          playing_efficiency(pe), insurance_correlation(ic) {}
};

struct CountState {
    int running_count;
    int cards_seen;
    double true_count;
    double advantage;
    int penetration_percent;
    int aces_seen;

    CountState()
        : running_count(0),
          cards_seen(0),
          true_count(0.0),
          advantage(0.0),
          penetration_percent(0),
          aces_seen(0) {}
};

// =============================================================================
// PROBABILITY ENGINE
// =============================================================================

struct ProbabilityResult {
    double dealer_bust_prob;
    double dealer_21_prob;
    double dealer_17_prob;
    double dealer_18_prob;
    double dealer_19_prob;
    double dealer_20_prob;
    std::array<double, 22> dealer_total_probs;

    ProbabilityResult() {
        dealer_bust_prob = dealer_21_prob = dealer_17_prob = 0.0;
        dealer_18_prob = dealer_19_prob = dealer_20_prob = 0.0;
        dealer_total_probs.fill(0.0);
    }
};

struct AdvancedEV {
    double stand_ev;
    double hit_ev;
    double double_ev;
    double split_ev;
    double surrender_ev;
    double insurance_ev;
    Action optimal_action;
    double optimal_ev;
    double house_edge;

    AdvancedEV() : stand_ev(-1.0), hit_ev(-1.0), double_ev(-1.0),
                   split_ev(-1.0), surrender_ev(-0.5), insurance_ev(-1.0),
                   optimal_action(Action::STAND), optimal_ev(-1.0), house_edge(0.005) {}
};

// =============================================================================
// ADVANCED CARD COUNTING CLASS
// =============================================================================

class CardCounter {
public:
    static const std::unordered_map<CountingSystem, CountingValues> COUNTING_SYSTEMS;

private:
    CountingSystem current_system;
    CountState state;
    DeckState deck;
    std::array<int, 10> cards_played;

    // Performance optimizations
    mutable std::unordered_map<uint64_t, ProbabilityResult> prob_cache;
    mutable std::unordered_map<uint64_t, AdvancedEV> ev_cache;

    // Helper functions
    uint64_t hash_deck_state() const;
    void update_true_count();
    void update_side_counts(int rank);
    void update_advantage();

public:
    CardCounter(CountingSystem system = CountingSystem::HI_LO, int num_decks = 6);

    // Core counting operations
    void reset_count();
    void process_card(int rank);
    void process_cards(const std::vector<int>& cards);

    // Count queries
    int get_running_count() const { return state.running_count; }
    double get_true_count() const { return state.true_count; }
    double get_advantage() const { return state.advantage; }
    int get_penetration() const { return state.penetration_percent; }

    // Betting recommendations
    double get_optimal_bet_units(double base_unit = 1.0) const;
    double get_kelly_bet_fraction(double bankroll) const;

    // Probability calculations
    ProbabilityResult calculate_dealer_probabilities(int dealer_upcard) const;

    // Advanced EV calculations with counting
    AdvancedEV calculate_counting_ev(const std::vector<int>& hand,
                                   int dealer_upcard,
                                   const RulesConfig& rules) const;

    // Strategy deviations based on count
    Action get_counting_strategy(const std::vector<int>& hand,
                               int dealer_upcard,
                               const RulesConfig& rules) const;

    // Insurance decisions
    bool should_take_insurance() const;

    // System information
    CountingSystem get_system() const { return current_system; }
    std::string get_system_name() const;
    CountingValues get_system_values() const;

    // Performance metrics
    size_t get_cache_size() const { return prob_cache.size() + ev_cache.size(); }
    void clear_cache() const { prob_cache.clear(); ev_cache.clear(); }

    // Deck composition analysis
    std::array<double, 10> get_remaining_card_frequencies() const;
    double get_ten_density() const;
    double get_ace_density() const;

    // =================================================================
    // USTON APC SPECIFIC FUNCTIONS (ADD THESE!)
    // =================================================================

    // USTON APC ace side count functions
    int get_aces_seen() const;
    int get_aces_remaining() const;
    double get_ace_adjustment() const;
    double get_adjusted_running_count() const;

    // Additional system-specific helpers
    bool is_balanced_system() const;
    bool uses_side_counts() const;
    std::string get_system_description() const;

    // Advanced counting metrics
    double get_betting_correlation() const;
    double get_playing_efficiency() const;
    double get_insurance_correlation() const;
};

// =============================================================================
// SIMULATION ENGINE
// =============================================================================

struct SimulationConfig {
    int num_hands;
    int num_decks;
    double penetration;
    bool use_counting;
    CountingSystem counting_system;
    RulesConfig rules;
    double base_bet;
    double max_bet;

    SimulationConfig() : num_hands(100000), num_decks(6), penetration(0.75),
                        use_counting(false), counting_system(CountingSystem::HI_LO),
                        base_bet(1.0), max_bet(100.0) {}
};

struct SimulationResult {
    double total_winnings;
    double house_edge;
    double standard_deviation;
    double win_rate;
    double push_rate;
    double loss_rate;
    int hands_played;
    double rtp;

    // Counting-specific metrics
    double average_true_count;
    double max_advantage;
    double min_advantage;
    double bet_spread;

    SimulationResult() : total_winnings(0.0), house_edge(0.0), standard_deviation(0.0),
                        win_rate(0.0), push_rate(0.0), loss_rate(0.0), hands_played(0),
                        rtp(0.0), average_true_count(0.0), max_advantage(0.0),
                        min_advantage(0.0), bet_spread(1.0) {}
};

class SimulationEngine {
private:
    std::mt19937 rng;

public:
    SimulationEngine(uint32_t seed = std::random_device{}());

    SimulationResult run_simulation(const SimulationConfig& config);

    // Specialized simulations
    SimulationResult test_basic_strategy(const RulesConfig& rules, int hands = 100000);
    SimulationResult test_counting_system(CountingSystem system,
                                        const RulesConfig& rules,
                                        int hands = 100000);

    // Strategy comparison
    std::vector<SimulationResult> compare_strategies(
        const std::vector<CountingSystem>& systems,
        const RulesConfig& rules,
        int hands = 50000);
};

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

std::string counting_system_to_string(CountingSystem system);
std::vector<CountingSystem> get_available_counting_systems();
double calculate_theoretical_house_edge(const RulesConfig& rules);
double calculate_optimal_bet_spread(double advantage, double risk_of_ruin = 0.01);

} // namespace bjlogic

#endif // CARD_COUNTING_HPP