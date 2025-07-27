// cpp_src/enhanced_bindings.cpp
/*
 * Phase 2.3: Enhanced PyBind11 bindings with card counting
 * Professional-grade strategy analysis and card counting
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/operators.h>
#include "bjlogic_core.hpp"
#include "card_counting.hpp"
#include "advanced_ev_engine.hpp"

namespace py = pybind11;
using namespace bjlogic;

// =============================================================================
// CONVERSION HELPERS
// =============================================================================

// Convert HandData to Python dict
py::dict hand_data_to_dict(const HandData& hand) {
    py::dict result;
    result["cards"] = hand.cards;
    result["total"] = hand.total;
    result["is_soft"] = hand.is_soft;
    result["can_split"] = hand.can_split;
    result["is_blackjack"] = hand.is_blackjack;
    result["is_busted"] = hand.is_busted;
    return result;
}

// Convert DeckState to Python dict
py::dict deck_state_to_dict(const DeckState& deck) {
    py::dict cards_remaining;
    for (const auto& pair : deck.cards_remaining) {
        cards_remaining[py::int_(pair.first)] = pair.second;
    }

    py::dict result;
    result["num_decks"] = deck.num_decks;
    result["cards_remaining"] = cards_remaining;
    result["total_cards"] = deck.total_cards;
    return result;
}

// Convert Python dict to RulesConfig
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
// PYTHON WRAPPER FUNCTIONS
// =============================================================================

// Enhanced hand calculation
py::dict py_calculate_hand_value(const std::vector<int>& cards) {
    HandData result = BJLogicCore::calculate_hand_value(cards);
    return hand_data_to_dict(result);
}

// Enhanced basic strategy wrapper
std::string py_basic_strategy_decision(const std::vector<int>& hand_cards,
                                      int dealer_upcard,
                                      const py::dict& rules_dict) {
    RulesConfig rules = dict_to_rules_config(rules_dict);
    Action action = BJLogicCore::basic_strategy_decision(hand_cards, dealer_upcard, rules);
    return BJLogicCore::action_to_string(action);
}

// Strategy analysis wrapper
bool py_is_basic_strategy_optimal(const std::vector<int>& hand_cards,
                                 int dealer_upcard,
                                 const py::dict& rules_dict,
                                 const std::string& chosen_action_str) {
    RulesConfig rules = dict_to_rules_config(rules_dict);

    // Convert string to Action enum
    Action chosen_action = Action::STAND;  // Default
    if (chosen_action_str == "hit") chosen_action = Action::HIT;
    else if (chosen_action_str == "double") chosen_action = Action::DOUBLE;
    else if (chosen_action_str == "split") chosen_action = Action::SPLIT;
    else if (chosen_action_str == "surrender") chosen_action = Action::SURRENDER;

    return BJLogicCore::is_basic_strategy_optimal(hand_cards, dealer_upcard, rules, chosen_action);
}

// Strategy deviation cost wrapper
double py_get_strategy_deviation_cost(const std::vector<int>& hand_cards,
                                     int dealer_upcard,
                                     const py::dict& rules_dict,
                                     const std::string& chosen_action_str) {
    RulesConfig rules = dict_to_rules_config(rules_dict);

    // Convert string to Action enum
    Action chosen_action = Action::STAND;  // Default
    if (chosen_action_str == "hit") chosen_action = Action::HIT;
    else if (chosen_action_str == "double") chosen_action = Action::DOUBLE;
    else if (chosen_action_str == "split") chosen_action = Action::SPLIT;
    else if (chosen_action_str == "surrender") chosen_action = Action::SURRENDER;

    return BJLogicCore::get_strategy_deviation_cost(hand_cards, dealer_upcard, rules, chosen_action);
}

// Batch strategy analysis
py::list py_batch_strategy_analysis(const py::list& scenarios, const py::dict& rules_dict) {
    RulesConfig rules = dict_to_rules_config(rules_dict);
    py::list results;

    for (const auto& scenario : scenarios) {
        py::dict scenario_dict = py::cast<py::dict>(scenario);
        std::vector<int> hand = py::cast<std::vector<int>>(scenario_dict["hand"]);
        int dealer_upcard = py::cast<int>(scenario_dict["dealer_upcard"]);

        Action optimal_action = BJLogicCore::basic_strategy_decision(hand, dealer_upcard, rules);
        std::string action_str = BJLogicCore::action_to_string(optimal_action);

        py::dict result;
        result["hand"] = hand;
        result["dealer_upcard"] = dealer_upcard;
        result["optimal_action"] = action_str;
        result["hand_total"] = BJLogicCore::calculate_hand_value(hand).total;
        result["is_soft"] = BJLogicCore::is_hand_soft(hand);
        result["can_split"] = BJLogicCore::can_split_hand(hand);

        results.append(result);
    }

    return results;
}

// Create default deck state
py::dict py_create_deck_state(int num_decks = 6) {
    DeckState deck(num_decks);
    return deck_state_to_dict(deck);
}

// Create default rules
py::dict py_create_rules_config() {
    RulesConfig rules;
    py::dict result;
    result["num_decks"] = rules.num_decks;
    result["dealer_hits_soft_17"] = rules.dealer_hits_soft_17;
    result["double_after_split"] = rules.double_after_split;
    result["resplitting_allowed"] = rules.resplitting_allowed;
    result["max_split_hands"] = rules.max_split_hands;
    result["blackjack_payout"] = rules.blackjack_payout;
    result["surrender_allowed"] = rules.surrender_allowed;
    return result;
}

// Test function for Phase 2.2
std::string test_strategy_extension() {
    return "🎯 Complete Basic Strategy Tables successfully implemented!";
}

// =============================================================================
// PHASE 2.3: CARD COUNTING FUNCTIONS
// =============================================================================

// Test function for Phase 2.3
std::string test_counting_extension() {
    return "🎯 Advanced Card Counting & Probability Engine successfully implemented!";
}

// Simple card counter wrapper
py::dict py_create_card_counter(const std::string& system_name = "Hi-Lo", int num_decks = 6) {
    try {
        // Convert string to enum - ALL 8 SYSTEMS
        CountingSystem system = CountingSystem::HI_LO;
        if (system_name == "Hi-Opt I") system = CountingSystem::HI_OPT_I;
        else if (system_name == "Hi-Opt II") system = CountingSystem::HI_OPT_II;
        else if (system_name == "Omega II") system = CountingSystem::OMEGA_II;
        else if (system_name == "Zen Count") system = CountingSystem::ZEN_COUNT;
        else if (system_name == "Uston APC") system = CountingSystem::USTON_APC;
        else if (system_name == "Revere RAPC") system = CountingSystem::REVERE_RAPC;
        else if (system_name == "Red 7") system = CountingSystem::RED_7;

        // Create counter
        CardCounter counter(system, num_decks);

        py::dict result;
        result["system_name"] = counter.get_system_name();
        result["running_count"] = counter.get_running_count();
        result["true_count"] = counter.get_true_count();
        result["advantage"] = counter.get_advantage();
        result["penetration"] = counter.get_penetration();
        result["success"] = true;
        result["aces_seen"] = counter.get_aces_seen();
        result["aces_remaining"] = counter.get_aces_remaining();

        return result;
    } catch (const std::exception& e) {
        py::dict result;
        result["error"] = e.what();
        result["success"] = false;
        return result;
    }
}

// Process cards function
py::dict py_process_cards_and_count(const std::vector<int>& cards,
                                   const std::string& system_name = "Hi-Lo",
                                   int num_decks = 6) {
    try {
        // Convert string to enum - ALL 8 SYSTEMS
        CountingSystem system = CountingSystem::HI_LO;
        if (system_name == "Hi-Opt I") system = CountingSystem::HI_OPT_I;
        else if (system_name == "Hi-Opt II") system = CountingSystem::HI_OPT_II;
        else if (system_name == "Omega II") system = CountingSystem::OMEGA_II;
        else if (system_name == "Zen Count") system = CountingSystem::ZEN_COUNT;
        else if (system_name == "Uston APC") system = CountingSystem::USTON_APC;
        else if (system_name == "Revere RAPC") system = CountingSystem::REVERE_RAPC;
        else if (system_name == "Red 7") system = CountingSystem::RED_7;

        // Create counter and process cards
        CardCounter counter(system, num_decks);
        counter.process_cards(cards);

        py::dict result;
        result["system_name"] = counter.get_system_name();
        result["cards_processed"] = cards;
        result["running_count"] = counter.get_running_count();
        result["true_count"] = counter.get_true_count();
        result["advantage"] = counter.get_advantage();
        result["penetration"] = counter.get_penetration();
        result["optimal_bet_units"] = counter.get_optimal_bet_units(1.0);
        result["should_take_insurance"] = counter.should_take_insurance();
        result["ten_density"] = counter.get_ten_density();
        result["ace_density"] = counter.get_ace_density();
        result["success"] = true;
        result["aces_seen"] = counter.get_aces_seen();
        result["aces_remaining"] = counter.get_aces_remaining();
        result["ace_adjustment"] = counter.get_ace_adjustment();
        result["adjusted_running_count"] = counter.get_adjusted_running_count();

        return result;
    } catch (const std::exception& e) {
        py::dict result;
        result["error"] = e.what();
        result["success"] = false;
        return result;
    }
}

// Get available counting systems
py::list py_get_counting_systems() {
    py::list result;
    result.append("Hi-Lo");
    result.append("Hi-Opt I");
    result.append("Hi-Opt II");
    result.append("Omega II");
    result.append("Zen Count");
    result.append("Uston APC");
    result.append("Revere RAPC");
    result.append("Red 7");
    return result;
}

// =============================================================================
// MODULE DEFINITION
// =============================================================================

PYBIND11_MODULE(bjlogic_cpp, m) {
    m.doc() = "Advanced Blackjack C++ Logic - Phase 2.3 Complete Card Counting";

    // =================================================================
    // ENUMS
    // =================================================================

    py::enum_<Action>(m, "Action")
        .value("STAND", Action::STAND)
        .value("HIT", Action::HIT)
        .value("DOUBLE", Action::DOUBLE)
        .value("SPLIT", Action::SPLIT)
        .value("SURRENDER", Action::SURRENDER);

    // =================================================================
    // CORE FUNCTIONS
    // =================================================================

    m.def("test_extension", &test_strategy_extension, "Test Phase 2.2 strategy extension");

    m.def("calculate_hand_value", &py_calculate_hand_value,
          "Enhanced hand value calculation with full details",
          py::arg("cards"));

    m.def("basic_strategy_decision", &py_basic_strategy_decision,
          "Get optimal basic strategy decision",
          py::arg("hand_cards"), py::arg("dealer_upcard"), py::arg("rules"));

    // =================================================================
    // STRATEGY ANALYSIS FUNCTIONS
    // =================================================================

    m.def("is_basic_strategy_optimal", &py_is_basic_strategy_optimal,
          "Check if chosen action matches basic strategy",
          py::arg("hand_cards"), py::arg("dealer_upcard"), py::arg("rules"), py::arg("chosen_action"));

    m.def("get_strategy_deviation_cost", &py_get_strategy_deviation_cost,
          "Get estimated cost of deviating from basic strategy",
          py::arg("hand_cards"), py::arg("dealer_upcard"), py::arg("rules"), py::arg("chosen_action"));

    m.def("batch_strategy_analysis", &py_batch_strategy_analysis,
          "Analyze multiple scenarios at once",
          py::arg("scenarios"), py::arg("rules"));

    // =================================================================
    // UTILITY FUNCTIONS
    // =================================================================

    m.def("is_hand_soft", &BJLogicCore::is_hand_soft,
          "Check if hand is soft",
          py::arg("cards"));

    m.def("can_split_hand", &BJLogicCore::can_split_hand,
          "Check if hand can be split",
          py::arg("cards"));

    m.def("is_hand_busted", &BJLogicCore::is_hand_busted,
          "Check if hand is busted",
          py::arg("cards"));

    // =================================================================
    // FACTORY FUNCTIONS
    // =================================================================

    m.def("create_deck_state", &py_create_deck_state,
          "Create a new deck state",
          py::arg("num_decks") = 6);

    m.def("create_rules_config", &py_create_rules_config,
          "Create default rules configuration");

    // =================================================================
    // PHASE 2.3: CARD COUNTING FUNCTIONS
    // =================================================================

    m.def("test_counting_extension", &test_counting_extension,
          "Test Phase 2.3 card counting extension");

    m.def("create_card_counter", &py_create_card_counter,
          "Create a card counter",
          py::arg("system") = "Hi-Lo", py::arg("num_decks") = 6);

    m.def("process_cards_and_count", &py_process_cards_and_count,
          "Process cards and return counting results",
          py::arg("cards"), py::arg("system") = "Hi-Lo", py::arg("num_decks") = 6);

    m.def("get_counting_systems", &py_get_counting_systems,
          "Get list of available counting systems");

    // =================================================================
    // ADVANCED EV ENGINE BINDINGS
    // =================================================================

    py::class_<bjlogic::DetailedEV>(m, "DetailedEV")
        .def_readonly("stand_ev", &bjlogic::DetailedEV::stand_ev)
        .def_readonly("hit_ev", &bjlogic::DetailedEV::hit_ev)
        .def_readonly("double_ev", &bjlogic::DetailedEV::double_ev)
        .def_readonly("split_ev", &bjlogic::DetailedEV::split_ev)
        .def_readonly("surrender_ev", &bjlogic::DetailedEV::surrender_ev)
        .def_readonly("optimal_ev", &bjlogic::DetailedEV::optimal_ev)
        .def_readonly("true_count_adjustment", &bjlogic::DetailedEV::true_count_adjustment)
        .def_readonly("variance", &bjlogic::DetailedEV::variance);

    py::class_<bjlogic::AdvancedEVEngine>(m, "AdvancedEVEngine")
        .def(py::init<int, double>(), py::arg("depth") = 10, py::arg("precision") = 0.0001)
        .def("calculate_true_count_ev", &bjlogic::AdvancedEVEngine::calculate_true_count_ev)
        .def("clear_cache", &bjlogic::AdvancedEVEngine::clear_cache)
        .def("get_cache_size", &bjlogic::AdvancedEVEngine::get_cache_size);

    // Test function for advanced EV engine
    m.def("test_advanced_ev_engine", []() {
        return "🎯 Advanced EV Calculation Engine successfully implemented!";
    });

    // Python-friendly wrapper that returns a dict
    m.def("calculate_true_count_ev_dict", [](bjlogic::AdvancedEVEngine& engine,
                                            const std::vector<int>& hand,
                                            int dealer_upcard,
                                            double true_count,
                                            const py::dict& rules_dict) {
        RulesConfig rules = dict_to_rules_config(rules_dict);
        auto result = engine.calculate_true_count_ev(hand, dealer_upcard, true_count, rules);

        py::dict py_result;
        py_result["stand_ev"] = result.stand_ev;
        py_result["hit_ev"] = result.hit_ev;
        py_result["double_ev"] = result.double_ev;
        py_result["split_ev"] = result.split_ev;
        py_result["surrender_ev"] = result.surrender_ev;
        py_result["optimal_ev"] = result.optimal_ev;
        py_result["optimal_action"] = BJLogicCore::action_to_string(result.optimal_action);
        py_result["true_count_adjustment"] = result.true_count_adjustment;
        py_result["variance"] = result.variance;

        return py_result;
    });

    // =================================================================
    // VERSION INFO
    // =================================================================

    m.attr("__version__") = "2.3.1-advanced-ev";
    m.attr("__phase__") = "Advanced EV Calculation Engine";
}