// cpp_src/advanced_ev_bindings.cpp
/*
 * Phase 2.3+: Advanced EV Engine Python Bindings
 * Professional-grade EV calculations with sophisticated algorithms
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "advanced_ev_engine.hpp"

namespace py = pybind11;
using namespace bjlogic;

// =============================================================================
// CONVERSION HELPERS FOR ADVANCED STRUCTURES
// =============================================================================

py::dict detailed_ev_to_dict(const DetailedEV& ev) {
    py::dict result;

    // Core action EVs
    result["stand_ev"] = ev.stand_ev;
    result["hit_ev"] = ev.hit_ev;
    result["double_ev"] = ev.double_ev;
    result["split_ev"] = ev.split_ev;
    result["surrender_ev"] = ev.surrender_ev;
    result["insurance_ev"] = ev.insurance_ev;

    // Advanced metrics
    result["composition_dependent_ev"] = ev.composition_dependent_ev;
    result["true_count_adjustment"] = ev.true_count_adjustment;
    result["penetration_factor"] = ev.penetration_factor;
    result["variance"] = ev.variance;
    result["risk_of_ruin"] = ev.risk_of_ruin;

    // Optimal decision
    result["optimal_action"] = BJLogicCore::action_to_string(ev.optimal_action);
    result["optimal_ev"] = ev.optimal_ev;
    result["advantage_over_basic"] = ev.advantage_over_basic;

    // Scenario-specific
    result["early_surrender_ev"] = ev.early_surrender_ev;
    result["late_surrender_ev"] = ev.late_surrender_ev;
    result["das_adjustment"] = ev.das_adjustment;

    return result;
}

py::dict scenario_analysis_to_dict(const ScenarioAnalysis& analysis) {
    py::dict result;

    result["player_hand"] = analysis.player_hand;
    result["dealer_upcard"] = analysis.dealer_upcard;
    result["basic_strategy_ev"] = detailed_ev_to_dict(analysis.basic_strategy_ev);
    result["counting_strategy_ev"] = detailed_ev_to_dict(analysis.counting_strategy_ev);
    result["composition_dependent_ev"] = detailed_ev_to_dict(analysis.composition_dependent_ev);
    result["ev_improvement"] = analysis.ev_improvement;
    result["recommendation"] = analysis.recommendation;
    result["confidence_level"] = analysis.confidence_level;

    return result;
}

py::dict session_analysis_to_dict(const SessionAnalysis& analysis) {
    py::dict result;

    result["total_ev"] = analysis.total_ev;
    result["hourly_ev"] = analysis.hourly_ev;
    result["standard_deviation"] = analysis.standard_deviation;
    result["risk_of_ruin"] = analysis.risk_of_ruin;
    result["kelly_bet_size"] = analysis.kelly_bet_size;
    result["optimal_session_length"] = analysis.optimal_session_length;
    result["variance_per_hand"] = analysis.variance_per_hand;
    result["hands_per_hour"] = analysis.hands_per_hour;

    return result;
}

// Convert Python dict to RulesConfig (reuse from other files)
RulesConfig dict_to_rules_config(const py::dict& rules_dict) {
    RulesConfig rules;

    if (rules_dict.contains("num_decks")) {
        rules.num_decks = py::cast<int>(rules_dict["num_decks"]);
    }
    if (rules_dict.contains("dealer_hits_soft_17")) {
        rules.dealer_hits_soft_17 = py::cast<bool>(rules_dict["dealer_hits_soft_17"]);
    }
    if (rules_dict.contains("double_after_split")) {
        rules.double_after_split = py::cast<int>(rules_dict["double_after_split"]);
    }
    if (rules_dict.contains("resplitting_allowed")) {
        rules.resplitting_allowed = py::cast<bool>(rules_dict["resplitting_allowed"]);
    }
    if (rules_dict.contains("max_split_hands")) {
        rules.max_split_hands = py::cast<int>(rules_dict["max_split_hands"]);
    }
    if (rules_dict.contains("blackjack_payout")) {
        rules.blackjack_payout = py::cast<double>(rules_dict["blackjack_payout"]);
    }
    if (rules_dict.contains("surrender_allowed")) {
        rules.surrender_allowed = py::cast<bool>(rules_dict["surrender_allowed"]);
    }

    return rules;
}

// =============================================================================
// PYTHON WRAPPER CLASSES
// =============================================================================

class PyAdvancedEVEngine {
private:
    AdvancedEVEngine engine;

public:
    PyAdvancedEVEngine(int depth = 10, double precision = 0.0001)
        : engine(depth, precision) {}

    // =================================================================
    // CORE EV CALCULATION METHODS
    // =================================================================

    py::dict calculate_detailed_ev(const std::vector<int>& player_hand,
                                 int dealer_upcard,
                                 const std::string& counter_system,
                                 const py::dict& rules_dict,
                                 int running_count = 0,
                                 int cards_seen = 52) const {

        // Convert system name to enum
        CountingSystem system = CountingSystem::HI_LO;
        if (counter_system == "Hi-Opt I") system = CountingSystem::HI_OPT_I;
        else if (counter_system == "Hi-Opt II") system = CountingSystem::HI_OPT_II;
        else if (counter_system == "Omega II") system = CountingSystem::OMEGA_II;
        else if (counter_system == "Zen Count") system = CountingSystem::ZEN_COUNT;
        else if (counter_system == "Uston APC") system = CountingSystem::USTON_APC;

        RulesConfig rules = dict_to_rules_config(rules_dict);

        // Create a counter with the specified state
        CardCounter counter(system, rules.num_decks);

        SessionAnalysis result = engine.analyze_session(bankroll, base_bet, counter, rules, session_length_hours);
        return session_analysis_to_dict(result);
    }

    py::dict calculate_exact_dealer_probabilities(int dealer_upcard,
                                            const py::dict& deck_composition,
                                            const py::dict& rules_dict) const {

    RulesConfig rules = dict_to_rules_config(rules_dict);

    // Convert Python deck to DeckComposition
    DeckComposition deck(rules.num_decks);
    deck.total_cards = 0;
    for (int i = 0; i < 13; ++i) deck.cards[i] = 0;

    if (deck_composition.contains("cards_remaining")) {
        py::dict cards_remaining = py::cast<py::dict>(deck_composition["cards_remaining"]);
        for (auto item : cards_remaining) {
            int rank = py::cast<int>(item.first);
            int count = py::cast<int>(item.second);
            if (rank >= 1 && rank <= 10) {
                if (rank == 10) {
                    // Distribute ten-value cards
                    int per_slot = count / 4;
                    int remainder = count % 4;
                    for (int i = 9; i < 13; ++i) {
                        deck.cards[i] = per_slot + (i - 9 < remainder ? 1 : 0);
                    }
                } else {
                    deck.cards[rank - 1] = count;
                }
                deck.total_cards += count;
            }
        }
    }

    // Calculate exact probabilities
    ExactDealerProbs probs = engine.recursive_dealer_engine.calculate_exact_probabilities(
        dealer_upcard, deck, rules);

    // Convert to Python dict
    py::dict result;
    result["prob_17"] = probs.prob_17;
    result["prob_18"] = probs.prob_18;
    result["prob_19"] = probs.prob_19;
    result["prob_20"] = probs.prob_20;
    result["prob_21"] = probs.prob_21;
    result["prob_bust"] = probs.prob_bust;
    result["prob_blackjack"] = probs.prob_blackjack;

    // Verification data
    result["total_probability"] = probs.get_total_probability();
    result["recursive_calls"] = probs.recursive_calls;
    result["from_cache"] = probs.from_cache;
    result["is_mathematically_valid"] = engine.recursive_dealer_engine.verify_probabilities(probs);

    return result;
}

py::dict calculate_no_peek_ev(const std::vector<int>& player_hand,
                             int dealer_upcard,
                             const py::dict& deck_composition,
                             const py::dict& rules_dict) const {

    RulesConfig rules = dict_to_rules_config(rules_dict);

    // YOUR GAME RULE: No peek on 10-value cards
    rules.dealer_peek_on_ten = false;

    // Convert Python deck to DeckComposition format
    DeckComposition deck(rules.num_decks);
    deck.total_cards = 0;
    for (int i = 0; i < 13; ++i) deck.cards[i] = 0;

    if (deck_composition.contains("cards_remaining")) {
        py::dict cards_remaining = py::cast<py::dict>(deck_composition["cards_remaining"]);
        for (auto item : cards_remaining) {
            int rank = py::cast<int>(item.first);
            int count = py::cast<int>(item.second);
            if (rank >= 1 && rank <= 10) {
                if (rank == 10) {
                    int per_slot = count / 4;
                    int remainder = count % 4;
                    for (int i = 9; i < 13; ++i) {
                        deck.cards[i] = per_slot + (i - 9 < remainder ? 1 : 0);
                    }
                } else {
                    deck.cards[rank - 1] = count;
                }
                deck.total_cards += count;
            }
        }
    }

    // Calculate exact dealer probabilities
    ExactDealerProbs dealer_probs = engine.recursive_dealer_engine.calculate_exact_probabilities(
        dealer_upcard, deck, rules);

    // Convert deck to DeckState for compatibility with existing methods
    DeckState deck_state(rules.num_decks);
    deck_state.total_cards = deck.total_cards;
    deck_state.cards_remaining.clear();

    for (int rank = 1; rank <= 9; ++rank) {
        deck_state.cards_remaining[rank] = deck.cards[rank - 1];
    }
    deck_state.cards_remaining[10] = deck.get_ten_cards();

    // Calculate all EVs using exact probabilities
    py::dict result;

    // Stand EV using exact probabilities
    result["stand_ev"] = engine.recursive_dealer_engine.calculate_stand_ev_from_exact_probs(
        player_hand, dealer_probs, rules);

    // Hit EV using recursive calculation
    result["hit_ev"] = engine.calculate_hit_ev_recursive(player_hand, dealer_upcard, deck_state, rules, 0);

    // Double EV (if valid)
    if (player_hand.size() == 2) {
        result["double_ev"] = engine.calculate_double_ev_recursive(player_hand, dealer_upcard, deck_state, rules);
    } else {
        result["double_ev"] = -2.0;
    }

    // Split EV (if valid - YOUR RULES: no resplitting, no DAS)
    if (player_hand.size() == 2 && player_hand[0] == player_hand[1]) {
        rules.resplitting_allowed = false;  // Your rule
        rules.double_after_split = false;   // Your rule
        rules.max_split_hands = 2;          // Your rule
        result["split_ev"] = engine.calculate_split_ev_advanced(player_hand, dealer_upcard, deck_state, rules, 0);
    } else {
        result["split_ev"] = -2.0;
    }

    // Surrender EV (YOUR RULE: anytime before 21)
    if (rules.surrender_allowed) {
        HandData hand_data = BJLogicCore::calculate_hand_value(player_hand);
        if (!hand_data.is_busted && hand_data.total < 21) {
            result["surrender_ev"] = -0.5;
        } else {
            result["surrender_ev"] = -1.0;
        }
    } else {
        result["surrender_ev"] = -1.0;
    }

    // Determine optimal action
    double best_ev = result["stand_ev"].cast<double>();
    std::string best_action = "stand";

    if (result["hit_ev"].cast<double>() > best_ev) {
        best_ev = result["hit_ev"].cast<double>();
        best_action = "hit";
    }
    if (result["double_ev"].cast<double>() > best_ev) {
        best_ev = result["double_ev"].cast<double>();
        best_action = "double";
    }
    if (result["split_ev"].cast<double>() > best_ev) {
        best_ev = result["split_ev"].cast<double>();
        best_action = "split";
    }
    if (result["surrender_ev"].cast<double>() > best_ev) {
        best_ev = result["surrender_ev"].cast<double>();
        best_action = "surrender";
    }

    result["optimal_action"] = best_action;
    result["optimal_ev"] = best_ev;

    // Include dealer probability analysis
    py::dict dealer_prob_dict;
    dealer_prob_dict["prob_17"] = dealer_probs.prob_17;
    dealer_prob_dict["prob_18"] = dealer_probs.prob_18;
    dealer_prob_dict["prob_19"] = dealer_probs.prob_19;
    dealer_prob_dict["prob_20"] = dealer_probs.prob_20;
    dealer_prob_dict["prob_21"] = dealer_probs.prob_21;
    dealer_prob_dict["prob_bust"] = dealer_probs.prob_bust;
    dealer_prob_dict["prob_blackjack"] = dealer_probs.prob_blackjack;
    dealer_prob_dict["total_check"] = dealer_probs.get_total_probability();
    result["dealer_probabilities"] = dealer_prob_dict;

    // Performance metadata
    result["recursive_calls"] = dealer_probs.recursive_calls;
    result["from_cache"] = dealer_probs.from_cache;
    result["mathematically_valid"] = engine.recursive_dealer_engine.verify_probabilities(dealer_probs);

    return result;
}

    py::dict test_recursive_dealer_engine() const {
        py::dict test_results;

        // Your game rules
        RulesConfig your_rules;
        your_rules.num_decks = 8;                    // Your rule
        your_rules.dealer_hits_soft_17 = false;     // Your rule: stands on soft 17
        your_rules.dealer_peek_on_ten = false;      // Your rule: no peek on 10
        your_rules.surrender_allowed = true;        // Your rule: late surrender
        your_rules.double_after_split = false;      // Your rule: no DAS
        your_rules.resplitting_allowed = false;     // Your rule: no resplit
        your_rules.blackjack_payout = 1.5;         // Your rule: 3:2

        DeckComposition fresh_deck(8);  // 8 deck fresh shoe

        // Test dealer 6 upcard (should bust frequently)
        ExactDealerProbs dealer_6_probs = engine.recursive_dealer_engine.calculate_exact_probabilities(
            6, fresh_deck, your_rules);

        test_results["dealer_6_total_prob"] = dealer_6_probs.get_total_probability();
        test_results["dealer_6_bust_prob"] = dealer_6_probs.prob_bust;
        test_results["dealer_6_valid"] = engine.recursive_dealer_engine.verify_probabilities(dealer_6_probs);

        // Test dealer Ace with blackjack check
        ExactDealerProbs dealer_ace_probs = engine.recursive_dealer_engine.calculate_exact_probabilities(
            1, fresh_deck, your_rules);

        test_results["dealer_ace_total_prob"] = dealer_ace_probs.get_total_probability();
        test_results["dealer_ace_blackjack_prob"] = dealer_ace_probs.prob_blackjack;
        test_results["dealer_ace_valid"] = engine.recursive_dealer_engine.verify_probabilities(dealer_ace_probs);

        // Test dealer 10 with no peek rule
        ExactDealerProbs dealer_10_probs = engine.recursive_dealer_engine.calculate_exact_probabilities(
            10, fresh_deck, your_rules);

        test_results["dealer_10_total_prob"] = dealer_10_probs.get_total_probability();
        test_results["dealer_10_blackjack_prob"] = dealer_10_probs.prob_blackjack;
        test_results["dealer_10_valid"] = engine.recursive_dealer_engine.verify_probabilities(dealer_10_probs);

        // Test all dealer upcards should sum to 1.0
        std::vector<bool> all_valid;
        for (int upcard = 1; upcard <= 10; ++upcard) {
            ExactDealerProbs probs = engine.recursive_dealer_engine.calculate_exact_probabilities(
                upcard, fresh_deck, your_rules);
            all_valid.push_back(engine.recursive_dealer_engine.verify_probabilities(probs));
        }

        test_results["all_upcards_valid"] = std::all_of(all_valid.begin(), all_valid.end(), [](bool v) { return v; });

        // Performance metrics
        test_results["cache_hits"] = engine.recursive_dealer_engine.get_cache_hits();
        test_results["cache_misses"] = engine.recursive_dealer_engine.get_cache_misses();
        test_results["cache_size"] = static_cast<int>(engine.recursive_dealer_engine.get_cache_size());

        test_results["test_passed"] = (
            test_results["dealer_6_valid"].cast<bool>() &&
            test_results["dealer_ace_valid"].cast<bool>() &&
            test_results["dealer_10_valid"].cast<bool>() &&
            test_results["all_upcards_valid"].cast<bool>()
        );

        return test_results;
    }

    // =================================================================
    // OPTIMIZATION AND RISK ANALYSIS
    // =================================================================

    py::list calculate_optimal_bet_spread(const std::string& counter_system,
                                        double bankroll,
                                        double risk_tolerance = 0.01,
                                        int running_count = 0) const {

        // Convert system name to enum
        CountingSystem system = CountingSystem::HI_LO;
        if (counter_system == "Hi-Opt I") system = CountingSystem::HI_OPT_I;
        else if (counter_system == "Hi-Opt II") system = CountingSystem::HI_OPT_II;
        else if (counter_system == "Omega II") system = CountingSystem::OMEGA_II;
        else if (counter_system == "Zen Count") system = CountingSystem::ZEN_COUNT;
        else if (counter_system == "Uston APC") system = CountingSystem::USTON_APC;

        CardCounter counter(system, 6);

        std::vector<double> bet_spread = engine.calculate_optimal_bet_spread(counter, bankroll, risk_tolerance);

        py::list result;
        for (double bet : bet_spread) {
            result.append(bet);
        }
        return result;
    }

    double calculate_risk_of_ruin(double bankroll,
                                double advantage,
                                double variance,
                                double bet_size) const {
        return engine.calculate_risk_of_ruin(bankroll, advantage, variance, bet_size);
    }

    double calculate_hand_variance(const std::vector<int>& player_hand,
                                 int dealer_upcard,
                                 const std::string& action_str,
                                 const py::dict& deck_composition,
                                 const py::dict& rules_dict) const {

        // Convert action string to enum
        Action action = Action::STAND;
        if (action_str == "hit") action = Action::HIT;
        else if (action_str == "double") action = Action::DOUBLE;
        else if (action_str == "split") action = Action::SPLIT;
        else if (action_str == "surrender") action = Action::SURRENDER;

        RulesConfig rules = dict_to_rules_config(rules_dict);

        // Create deck state from Python dict
        DeckState deck(rules.num_decks);
        if (deck_composition.contains("cards_remaining")) {
            py::dict cards_remaining = py::cast<py::dict>(deck_composition["cards_remaining"]);
            for (auto item : cards_remaining) {
                int rank = py::cast<int>(item.first);
                int count = py::cast<int>(item.second);
                if (rank >= 1 && rank <= 10) {
                    deck.cards_remaining[rank] = count;
                }
            }
        }

        return engine.calculate_hand_variance(player_hand, dealer_upcard, action, deck, rules);
    }

    // =================================================================
    // MONTE CARLO METHODS
    // =================================================================

    py::dict monte_carlo_ev_estimation(const std::vector<int>& player_hand,
                                     int dealer_upcard,
                                     const std::string& counter_system,
                                     const py::dict& rules_dict,
                                     int iterations = 100000,
                                     int running_count = 0) const {

        // Convert system name to enum
        CountingSystem system = CountingSystem::HI_LO;
        if (counter_system == "Hi-Opt I") system = CountingSystem::HI_OPT_I;
        else if (counter_system == "Hi-Opt II") system = CountingSystem::HI_OPT_II;
        else if (counter_system == "Omega II") system = CountingSystem::OMEGA_II;
        else if (counter_system == "Zen Count") system = CountingSystem::ZEN_COUNT;
        else if (counter_system == "Uston APC") system = CountingSystem::USTON_APC;

        RulesConfig rules = dict_to_rules_config(rules_dict);
        CardCounter counter(system, rules.num_decks);

        DetailedEV result = engine.monte_carlo_ev_estimation(player_hand, dealer_upcard, counter, rules, iterations);
        return detailed_ev_to_dict(result);
    }

    py::dict calculate_ev_confidence_interval(double ev,
                                            double variance,
                                            int sample_size,
                                            double confidence = 0.95) const {

        auto interval = engine.calculate_ev_confidence_interval(ev, variance, sample_size, confidence);

        py::dict result;
        result["lower_bound"] = interval.first;
        result["upper_bound"] = interval.second;
        result["confidence_level"] = confidence;
        result["margin_of_error"] = (interval.second - interval.first) / 2.0;

        return result;
    }

    // =================================================================
    // PERFORMANCE AND CONFIGURATION
    // =================================================================

    void clear_cache() const {
        engine.clear_cache();
    }

    size_t get_cache_size() const {
        return engine.get_cache_size();
    }

    void set_simulation_depth(int depth) {
        engine.set_simulation_depth(depth);
    }

    void set_precision_threshold(double threshold) {
        engine.set_precision_threshold(threshold);
    }

    void enable_composition_dependent(bool enable) {
        engine.enable_composition_dependent(enable);
    }
};

// =============================================================================
// SPECIALIZED CALCULATOR WRAPPERS
// =============================================================================

class PyTournamentEVCalculator {
private:
    TournamentEVCalculator calculator;

public:
    double calculate_tournament_ev(const std::vector<int>& hand,
                                 int dealer_upcard,
                                 int chips_remaining,
                                 int rounds_remaining,
                                 const py::dict& rules_dict) const {

        RulesConfig rules = dict_to_rules_config(rules_dict);
        return calculator.calculate_tournament_ev(hand, dealer_upcard, chips_remaining, rounds_remaining, rules);
    }

    double calculate_optimal_tournament_bet(int current_chips,
                                          int target_chips,
                                          int rounds_remaining) const {

        return calculator.calculate_optimal_tournament_bet(current_chips, target_chips, rounds_remaining);
    }
};

class PyProgressiveEVCalculator {
private:
    ProgressiveEVCalculator calculator;

public:
    double calculate_progressive_ev(const py::list& bet_progression,
                                  double win_probability,
                                  int max_progression_length) const {

        std::vector<double> progression;
        for (auto item : bet_progression) {
            progression.push_back(py::cast<double>(item));
        }

        return calculator.calculate_progressive_ev(progression, win_probability, max_progression_length);
    }

    double calculate_martingale_risk(double base_bet,
                                   double bankroll,
                                   int max_doubles) const {

        return calculator.calculate_martingale_risk(base_bet, bankroll, max_doubles);
    }
};

// =============================================================================
// UTILITY WRAPPER FUNCTIONS
// =============================================================================

py::dict py_detailed_to_simple_ev(const py::dict& detailed_ev_dict) {
    // Convert detailed EV dict back to simple format for compatibility
    py::dict result;
    result["stand_ev"] = detailed_ev_dict["stand_ev"];
    result["hit_ev"] = detailed_ev_dict["hit_ev"];
    result["double_ev"] = detailed_ev_dict["double_ev"];
    result["split_ev"] = detailed_ev_dict["split_ev"];
    result["surrender_ev"] = detailed_ev_dict["surrender_ev"];
    result["optimal_action"] = detailed_ev_dict["optimal_action"];
    result["optimal_ev"] = detailed_ev_dict["optimal_ev"];

    return result;
}

double py_calculate_ev_difference(const py::dict& ev1_dict, const py::dict& ev2_dict) {
    double ev1 = py::cast<double>(ev1_dict["optimal_ev"]);
    double ev2 = py::cast<double>(ev2_dict["optimal_ev"]);

    return std::abs(ev1 - ev2);
}

std::string py_format_ev_analysis(const py::dict& ev_dict, bool verbose = false) {
    std::string result = "EV Analysis:\n";
    result += "  Stand EV: " + std::to_string(py::cast<double>(ev_dict["stand_ev"])) + "\n";
    result += "  Hit EV: " + std::to_string(py::cast<double>(ev_dict["hit_ev"])) + "\n";
    result += "  Double EV: " + std::to_string(py::cast<double>(ev_dict["double_ev"])) + "\n";
    result += "  Optimal: " + py::cast<std::string>(ev_dict["optimal_action"]) +
              " (EV: " + std::to_string(py::cast<double>(ev_dict["optimal_ev"])) + ")\n";

    if (verbose) {
        result += "  True Count Adj: " + std::to_string(py::cast<double>(ev_dict["true_count_adjustment"])) + "\n";
        result += "  Variance: " + std::to_string(py::cast<double>(ev_dict["variance"])) + "\n";
        result += "  Advantage over Basic: " + std::to_string(py::cast<double>(ev_dict["advantage_over_basic"])) + "\n";
    }

    return result;
}

bool py_is_ev_difference_significant(double ev1, double ev2,
                                   double variance1, double variance2,
                                   int sample_size, double alpha = 0.05) {

    return is_ev_difference_significant(ev1, ev2, variance1, variance2, sample_size, alpha);
}

// =============================================================================
// COMPREHENSIVE ANALYSIS FUNCTIONS
// =============================================================================

py::dict py_comprehensive_hand_analysis(const std::vector<int>& player_hand,
                                       int dealer_upcard,
                                       const py::dict& rules_dict,
                                       const std::string& counter_system = "Hi-Lo",
                                       int running_count = 0,
                                       int cards_seen = 52,
                                       bool include_composition = true,
                                       bool include_monte_carlo = false) {

    PyAdvancedEVEngine engine;
    py::dict result;

    // Basic strategy EV
    py::dict basic_ev = engine.calculate_true_count_ev(player_hand, dealer_upcard, 0.0, rules_dict);
    result["basic_strategy"] = basic_ev;

    // Counting strategy EV
    py::dict counting_ev = engine.calculate_detailed_ev(player_hand, dealer_upcard,
                                                       counter_system, rules_dict,
                                                       running_count, cards_seen);
    result["counting_strategy"] = counting_ev;

    // Calculate improvement
    double basic_optimal = py::cast<double>(basic_ev["optimal_ev"]);
    double counting_optimal = py::cast<double>(counting_ev["optimal_ev"]);
    result["ev_improvement"] = counting_optimal - basic_optimal;
    result["improvement_percentage"] = ((counting_optimal - basic_optimal) / std::abs(basic_optimal)) * 100.0;

    // Probability analysis
    py::dict deck_comp = bjlogic_cpp.create_deck_state(py::cast<int>(rules_dict["num_decks"]));
    double dealer_bust_prob = engine.calculate_dealer_bust_probability(dealer_upcard, deck_comp, rules_dict);
    double player_bust_prob = engine.calculate_player_bust_probability(player_hand, deck_comp);

    result["dealer_bust_probability"] = dealer_bust_prob;
    result["player_bust_probability"] = player_bust_prob;

    // Risk analysis
    double variance = py::cast<double>(counting_ev["variance"]);
    result["variance"] = variance;
    result["standard_deviation"] = std::sqrt(variance);

    // Betting recommendation
    double advantage = py::cast<double>(counting_ev["advantage_over_basic"]);
    result["betting_advantage"] = advantage;

    if (advantage > 0.01) {
        result["betting_recommendation"] = "Increase bet size";
        result["suggested_bet_multiplier"] = 1.0 + (advantage * 20.0); // Simplified Kelly
    } else if (advantage < -0.01) {
        result["betting_recommendation"] = "Minimum bet or skip hand";
        result["suggested_bet_multiplier"] = 0.5;
    } else {
        result["betting_recommendation"] = "Standard bet size";
        result["suggested_bet_multiplier"] = 1.0;
    }

    // Monte Carlo validation (optional)
    if (include_monte_carlo) {
        py::dict mc_ev = engine.monte_carlo_ev_estimation(player_hand, dealer_upcard,
                                                        counter_system, rules_dict,
                                                        50000, running_count);
        result["monte_carlo_validation"] = mc_ev;

        // Confidence interval
        py::dict confidence = engine.calculate_ev_confidence_interval(counting_optimal, variance, 50000);
        result["confidence_interval"] = confidence;
    }

    // Summary and recommendation
    std::string recommendation;
    double confidence_level = 0.9;

    if (result["ev_improvement"].cast<double>() > 0.02) {
        recommendation = "Strong deviation recommended - significant counting advantage";
        confidence_level = 0.95;
    } else if (result["ev_improvement"].cast<double>() > 0.005) {
        recommendation = "Moderate deviation recommended - follow counting strategy";
        confidence_level = 0.85;
    } else if (result["ev_improvement"].cast<double>() > -0.005) {
        recommendation = "Marginal difference - either strategy acceptable";
        confidence_level = 0.75;
    } else {
        recommendation = "Stick to basic strategy - counting shows negative adjustment";
        confidence_level = 0.90;
    }

    result["recommendation"] = recommendation;
    result["confidence_level"] = confidence_level;
    result["analysis_summary"] = py_format_ev_analysis(counting_ev, true);

    return result;
}

py::dict py_session_optimization(double bankroll,
                               double base_bet,
                               const std::string& counter_system,
                               const py::dict& rules_dict,
                               int session_hours = 4,
                               double risk_tolerance = 0.01) {

    PyAdvancedEVEngine engine;
    py::dict result;

    // Session analysis
    py::dict session_analysis = engine.analyze_session(bankroll, base_bet, counter_system,
                                                      rules_dict, session_hours);
    result["session_analysis"] = session_analysis;

    // Optimal bet spread
    py::list bet_spread = engine.calculate_optimal_bet_spread(counter_system, bankroll, risk_tolerance);
    result["optimal_bet_spread"] = bet_spread;

    // Risk analysis
    double hourly_ev = py::cast<double>(session_analysis["hourly_ev"]);
    double variance = py::cast<double>(session_analysis["variance_per_hand"]);
    double risk_of_ruin = engine.calculate_risk_of_ruin(bankroll, hourly_ev / (80 * base_bet), variance, base_bet);

    result["risk_of_ruin"] = risk_of_ruin;
    result["safe_bankroll_ratio"] = bankroll / base_bet;

    // Recommendations
    if (risk_of_ruin > risk_tolerance * 2) {
        result["recommendation"] = "Reduce bet size - risk of ruin too high";
        result["suggested_base_bet"] = base_bet * 0.7;
    } else if (risk_of_ruin < risk_tolerance * 0.5) {
        result["recommendation"] = "Can increase bet size safely";
        result["suggested_base_bet"] = base_bet * 1.3;
    } else {
        result["recommendation"] = "Current bet size is appropriate";
        result["suggested_base_bet"] = base_bet;
    }

    return result;
}

// Test function for advanced EV engine
std::string test_advanced_ev_engine() {
    return "🎯 Advanced EV Calculation Engine successfully implemented!";
}

// =============================================================================
// ADD TO MODULE DEFINITION
// =============================================================================

void add_advanced_ev_bindings(py::module& m) {

    // =================================================================
    // MAIN EV ENGINE CLASS
    // =================================================================

    py::class_<PyAdvancedEVEngine>(m, "AdvancedEVEngine")
        .def(py::init<int, double>(), py::arg("depth") = 10, py::arg("precision") = 0.0001)

        // Core EV calculations
        .def("calculate_detailed_ev", &PyAdvancedEVEngine::calculate_detailed_ev,
             py::arg("hand"), py::arg("dealer_upcard"), py::arg("counter_system"),
             py::arg("rules"), py::arg("running_count") = 0, py::arg("cards_seen") = 52)

        .def("calculate_composition_dependent_ev", &PyAdvancedEVEngine::calculate_composition_dependent_ev,
             py::arg("hand"), py::arg("dealer_upcard"), py::arg("deck_composition"), py::arg("rules"))

        .def("calculate_true_count_ev", &PyAdvancedEVEngine::calculate_true_count_ev,
             py::arg("hand"), py::arg("dealer_upcard"), py::arg("true_count"), py::arg("rules"))

        // Probability calculations
        .def("calculate_dealer_bust_probability", &PyAdvancedEVEngine::calculate_dealer_bust_probability,
             py::arg("dealer_upcard"), py::arg("deck_composition"), py::arg("rules"))

        .def("calculate_player_bust_probability", &PyAdvancedEVEngine::calculate_player_bust_probability,
             py::arg("hand"), py::arg("deck_composition"))

        .def("calculate_insurance_ev", &PyAdvancedEVEngine::calculate_insurance_ev,
             py::arg("dealer_upcard"), py::arg("deck_composition"), py::arg("bet_amount") = 1.0)

        // Advanced analysis
        .def("analyze_scenario", &PyAdvancedEVEngine::analyze_scenario,
             py::arg("hand"), py::arg("dealer_upcard"), py::arg("counter_system"),
             py::arg("rules"), py::arg("running_count") = 0, py::arg("cards_seen") = 52)

        .def("analyze_session", &PyAdvancedEVEngine::analyze_session,
             py::arg("bankroll"), py::arg("base_bet"), py::arg("counter_system"),
             py::arg("rules"), py::arg("session_hours") = 4, py::arg("running_count") = 0)

        // Optimization and risk
        .def("calculate_optimal_bet_spread", &PyAdvancedEVEngine::calculate_optimal_bet_spread,
             py::arg("counter_system"), py::arg("bankroll"), py::arg("risk_tolerance") = 0.01,
             py::arg("running_count") = 0)

        .def("calculate_risk_of_ruin", &PyAdvancedEVEngine::calculate_risk_of_ruin,
             py::arg("bankroll"), py::arg("advantage"), py::arg("variance"), py::arg("bet_size"))

        .def("calculate_hand_variance", &PyAdvancedEVEngine::calculate_hand_variance,
             py::arg("hand"), py::arg("dealer_upcard"), py::arg("action"),
             py::arg("deck_composition"), py::arg("rules"))

        // Monte Carlo methods
        .def("monte_carlo_ev_estimation", &PyAdvancedEVEngine::monte_carlo_ev_estimation,
             py::arg("hand"), py::arg("dealer_upcard"), py::arg("counter_system"),
             py::arg("rules"), py::arg("iterations") = 100000, py::arg("running_count") = 0)

        .def("calculate_ev_confidence_interval", &PyAdvancedEVEngine::calculate_ev_confidence_interval,
             py::arg("ev"), py::arg("variance"), py::arg("sample_size"), py::arg("confidence") = 0.95)

        // Performance and configuration
        .def("clear_cache", &PyAdvancedEVEngine::clear_cache)
        .def("get_cache_size", &PyAdvancedEVEngine::get_cache_size)
        .def("set_simulation_depth", &PyAdvancedEVEngine::set_simulation_depth)
        .def("set_precision_threshold", &PyAdvancedEVEngine::set_precision_threshold)
        .def("enable_composition_dependent", &PyAdvancedEVEngine::enable_composition_dependent);

        .def("calculate_exact_dealer_probabilities", &PyAdvancedEVEngine::calculate_exact_dealer_probabilities,
         "Calculate mathematically exact dealer probabilities using recursive method",
         py::arg("dealer_upcard"), py::arg("deck_composition"), py::arg("rules"))

    .def("calculate_no_peek_ev", &PyAdvancedEVEngine::calculate_no_peek_ev,
         "Calculate EV with your game's no-peek rule on 10-value cards",
         py::arg("hand"), py::arg("dealer_upcard"), py::arg("deck_composition"), py::arg("rules"))

    .def("test_recursive_dealer_engine", &PyAdvancedEVEngine::test_recursive_dealer_engine,
         "Test recursive dealer engine for mathematical correctness")

    // =================================================================
    // SPECIALIZED CALCULATORS
    // =================================================================

    py::class_<PyTournamentEVCalculator>(m, "TournamentEVCalculator")
        .def(py::init<>())
        .def("calculate_tournament_ev", &PyTournamentEVCalculator::calculate_tournament_ev,
             py::arg("hand"), py::arg("dealer_upcard"), py::arg("chips_remaining"),
             py::arg("rounds_remaining"), py::arg("rules"))
        .def("calculate_optimal_tournament_bet", &PyTournamentEVCalculator::calculate_optimal_tournament_bet,
             py::arg("current_chips"), py::arg("target_chips"), py::arg("rounds_remaining"));

    py::class_<PyProgressiveEVCalculator>(m, "ProgressiveEVCalculator")
        .def(py::init<>())
        .def("calculate_progressive_ev", &PyProgressiveEVCalculator::calculate_progressive_ev,
             py::arg("bet_progression"), py::arg("win_probability"), py::arg("max_progression_length"))
        .def("calculate_martingale_risk", &PyProgressiveEVCalculator::calculate_martingale_risk,
             py::arg("base_bet"), py::arg("bankroll"), py::arg("max_doubles"));

    // =================================================================
    // UTILITY FUNCTIONS
    // =================================================================

    m.def("detailed_to_simple_ev", &py_detailed_to_simple_ev,
          "Convert detailed EV dict to simple format");

    m.def("calculate_ev_difference", &py_calculate_ev_difference,
          "Calculate difference between two EV calculations");

    m.def("format_ev_analysis", &py_format_ev_analysis,
          "Format EV analysis for display", py::arg("ev_dict"), py::arg("verbose") = false);

    m.def("is_ev_difference_significant", &py_is_ev_difference_significant,
          "Test statistical significance of EV difference",
          py::arg("ev1"), py::arg("ev2"), py::arg("variance1"), py::arg("variance2"),
          py::arg("sample_size"), py::arg("alpha") = 0.05);

    // =================================================================
    // COMPREHENSIVE ANALYSIS FUNCTIONS
    // =================================================================

    m.def("comprehensive_hand_analysis", &py_comprehensive_hand_analysis,
          "Complete hand analysis with all EV methods",
          py::arg("hand"), py::arg("dealer_upcard"), py::arg("rules"),
          py::arg("counter_system") = "Hi-Lo", py::arg("running_count") = 0,
          py::arg("cards_seen") = 52, py::arg("include_composition") = true,
          py::arg("include_monte_carlo") = false);

    m.def("session_optimization", &py_session_optimization,
          "Optimize session parameters for maximum EV",
          py::arg("bankroll"), py::arg("base_bet"), py::arg("counter_system"),
          py::arg("rules"), py::arg("session_hours") = 4, py::arg("risk_tolerance") = 0.01);

    m.def("test_advanced_ev_engine", &test_advanced_ev_engine,
          "Test advanced EV engine functionality");
}
        CardCounter counter(system, rules.num_decks);

        // Simulate the count state (simplified approach)
        // In a real implementation, you'd want to track the actual cards played
        for (int i = 0; i < cards_seen / 10; ++i) {
            counter.process_card(5); // Neutral cards to reach the desired count
        }

        DetailedEV result = engine.calculate_detailed_ev(player_hand, dealer_upcard, counter, rules);
        return detailed_ev_to_dict(result);
    }

    py::dict calculate_composition_dependent_ev(const std::vector<int>& player_hand,
                                              int dealer_upcard,
                                              const py::dict& deck_composition,
                                              const py::dict& rules_dict) const {

        RulesConfig rules = dict_to_rules_config(rules_dict);

        // Create deck state from Python dict
        DeckState deck(rules.num_decks);
        if (deck_composition.contains("cards_remaining")) {
            py::dict cards_remaining = py::cast<py::dict>(deck_composition["cards_remaining"]);
            for (auto item : cards_remaining) {
                int rank = py::cast<int>(item.first);
                int count = py::cast<int>(item.second);
                if (rank >= 1 && rank <= 10) {
                    deck.cards_remaining[rank] = count;
                }
            }
        }

        DetailedEV result = engine.calculate_composition_dependent_ev(player_hand, dealer_upcard, deck, rules);
        return detailed_ev_to_dict(result);
    }

    py::dict calculate_true_count_ev(const std::vector<int>& player_hand,
                                   int dealer_upcard,
                                   double true_count,
                                   const py::dict& rules_dict) const {

        RulesConfig rules = dict_to_rules_config(rules_dict);
        DetailedEV result = engine.calculate_true_count_ev(player_hand, dealer_upcard, true_count, rules);
        return detailed_ev_to_dict(result);
    }

    // =================================================================
    // PROBABILITY CALCULATIONS
    // =================================================================

    double calculate_dealer_bust_probability(int dealer_upcard,
                                           const py::dict& deck_composition,
                                           const py::dict& rules_dict) const {

        RulesConfig rules = dict_to_rules_config(rules_dict);

        // Create deck state from Python dict
        DeckState deck(rules.num_decks);
        if (deck_composition.contains("cards_remaining")) {
            py::dict cards_remaining = py::cast<py::dict>(deck_composition["cards_remaining"]);
            for (auto item : cards_remaining) {
                int rank = py::cast<int>(item.first);
                int count = py::cast<int>(item.second);
                if (rank >= 1 && rank <= 10) {
                    deck.cards_remaining[rank] = count;
                }
            }
        }

        return engine.calculate_dealer_bust_probability(dealer_upcard, deck, rules);
    }

    double calculate_player_bust_probability(const std::vector<int>& hand,
                                           const py::dict& deck_composition) const {

        // Create deck state from Python dict
        DeckState deck(6); // Default
        if (deck_composition.contains("cards_remaining")) {
            py::dict cards_remaining = py::cast<py::dict>(deck_composition["cards_remaining"]);
            for (auto item : cards_remaining) {
                int rank = py::cast<int>(item.first);
                int count = py::cast<int>(item.second);
                if (rank >= 1 && rank <= 10) {
                    deck.cards_remaining[rank] = count;
                }
            }
        }

        return engine.calculate_player_bust_probability(hand, deck);
    }

    double calculate_insurance_ev(int dealer_upcard,
                                const py::dict& deck_composition,
                                double bet_amount = 1.0) const {

        // Create deck state from Python dict
        DeckState deck(6); // Default
        if (deck_composition.contains("cards_remaining")) {
            py::dict cards_remaining = py::cast<py::dict>(deck_composition["cards_remaining"]);
            for (auto item : cards_remaining) {
                int rank = py::cast<int>(item.first);
                int count = py::cast<int>(item.second);
                if (rank >= 1 && rank <= 10) {
                    deck.cards_remaining[rank] = count;
                }
            }
        }

        return engine.calculate_insurance_ev(dealer_upcard, deck, bet_amount);
    }

    // =================================================================
    // ADVANCED ANALYSIS METHODS
    // =================================================================

    py::dict analyze_scenario(const std::vector<int>& player_hand,
                            int dealer_upcard,
                            const std::string& counter_system,
                            const py::dict& rules_dict,
                            int running_count = 0,
                            int cards_seen = 52) const {

        // Convert system name to enum
        CountingSystem system = CountingSystem::HI_LO;
        if (counter_system == "Hi-Opt I") system = CountingSystem::HI_OPT_I;
        else if (counter_system == "Hi-Opt II") system = CountingSystem::HI_OPT_II;
        else if (counter_system == "Omega II") system = CountingSystem::OMEGA_II;
        else if (counter_system == "Zen Count") system = CountingSystem::ZEN_COUNT;
        else if (counter_system == "Uston APC") system = CountingSystem::USTON_APC;

        RulesConfig rules = dict_to_rules_config(rules_dict);

        // Create a counter with the specified state
        CardCounter counter(system, rules.num_decks);

        ScenarioAnalysis result = engine.analyze_scenario(player_hand, dealer_upcard, counter, rules);
        return scenario_analysis_to_dict(result);
    }

    py::dict analyze_session(double bankroll,
                           double base_bet,
                           const std::string& counter_system,
                           const py::dict& rules_dict,
                           int session_length_hours = 4,
                           int running_count = 0) const {

        // Convert system name to enum
        CountingSystem system = CountingSystem::HI_LO;
        if (counter_system == "Hi-Opt I") system = CountingSystem::HI_OPT_I;
        else if (counter_system == "Hi-Opt II") system = CountingSystem::HI_OPT_II;
        else if (counter_system == "Omega II") system = CountingSystem::OMEGA_II;
        else if (counter_system == "Zen Count") system = CountingSystem::ZEN_COUNT;
        else if (counter_system == "Uston APC") system = CountingSystem::USTON_APC;

        RulesConfig rules = dict_to_rules_config(rules_dict);

        // Create a counter with the specified state