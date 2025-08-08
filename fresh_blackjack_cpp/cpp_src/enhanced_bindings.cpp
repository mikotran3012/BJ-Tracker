// cpp_src/enhanced_bindings.cpp - FIXED VERSION
/*
 * Phase 2.3: Enhanced PyBind11 bindings with card counting
 * Professional-grade strategy analysis and card counting
 * FIXED: Added calculate_exact_dealer_probabilities function
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/operators.h>
#include "bjlogic_core.hpp"
#include "card_counting.hpp"
#include "advanced_ev_engine.hpp"
#include "recursive_dealer_engine.hpp"

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
static RulesConfig dict_to_rules_config(const py::dict& rules_dict) {
    RulesConfig rules;

    // Set defaults to YOUR game rules first
    rules.num_decks = 8;                         // Your rule: 8 decks
    rules.dealer_hits_soft_17 = false;           // Your rule: Stands on soft 17
    rules.double_after_split = 0;                // Your rule: Not allowed
    rules.resplitting_allowed = false;           // Your rule: No resplitting
    rules.max_split_hands = 2;                   // Your rule: Max 2 hands
    rules.blackjack_payout = 1.5;               // Your rule: 3:2 payout
    rules.surrender_allowed = true;              // Your rule: Late surrender
    rules.dealer_peek_on_ten = false;           // Your rule: NO peek on 10-value cards

    // Allow overrides from Python dict
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
    if (rules_dict.contains("dealer_peek_on_ten")) {
        rules.dealer_peek_on_ten = py::cast<bool>(rules_dict["dealer_peek_on_ten"]);
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
                                      const RulesConfig& rules) {
    Action action = BJLogicCore::basic_strategy_decision(hand_cards, dealer_upcard, rules);
    return BJLogicCore::action_to_string(action);
}

// Strategy analysis wrapper
bool py_is_basic_strategy_optimal(const std::vector<int>& hand_cards,
                                 int dealer_upcard,
                                 const RulesConfig& rules,
                                 const std::string& chosen_action_str) {

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
                                     const RulesConfig& rules,
                                     const std::string& chosen_action_str) {

    // Convert string to Action enum
    Action chosen_action = Action::STAND;  // Default
    if (chosen_action_str == "hit") chosen_action = Action::HIT;
    else if (chosen_action_str == "double") chosen_action = Action::DOUBLE;
    else if (chosen_action_str == "split") chosen_action = Action::SPLIT;
    else if (chosen_action_str == "surrender") chosen_action = Action::SURRENDER;

    return BJLogicCore::get_strategy_deviation_cost(hand_cards, dealer_upcard, rules, chosen_action);
}

// Batch strategy analysis
py::list py_batch_strategy_analysis(const py::list& scenarios, const RulesConfig& rules) {
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
RulesConfig py_create_rules_config() {
    return RulesConfig();
}

// Test function for Phase 2.2
std::string test_strategy_extension() {
    return "Complete Basic Strategy Tables successfully implemented!";
}

// Converter: Your comp_panel format → C++ DeckState
DeckState python_composition_to_deck_state(const py::dict& composition, int num_decks) {
    DeckState deck(num_decks);

    // YOUR FORMAT: Based on comp_panel.py structure
    if (composition.contains("comp") && composition.contains("decks")) {
        // Direct access to your comp_panel data
        py::dict comp_dict = py::cast<py::dict>(composition["comp"]);
        int decks = py::cast<int>(composition["decks"]);

        deck.total_cards = 0;

        // Clear existing cards_remaining
        deck.cards_remaining.clear();

        // Your ranks: ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
        std::vector<std::string> your_ranks = {"A", "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K"};

        for (const auto& rank_str : your_ranks) {
            if (comp_dict.contains(rank_str.c_str())) {
                int cards_dealt = py::cast<int>(comp_dict[rank_str.c_str()]);
                int cards_remaining = decks * 4 - cards_dealt;

                // Convert your ranks to C++ internal format
                int rank_key;
                if (rank_str == "A") rank_key = 1;
                else if (rank_str == "T") rank_key = 10;
                else if (rank_str == "J") rank_key = 11;
                else if (rank_str == "Q") rank_key = 12;
                else if (rank_str == "K") rank_key = 13;
                else rank_key = std::stoi(rank_str); // 2-9

                // Use insert or emplace instead of operator[]
                deck.cards_remaining.insert(std::make_pair(rank_key, std::max(0, cards_remaining)));
                deck.total_cards += std::max(0, cards_remaining);
            }
        }
    }

    return deck;
}

// Extract composition data from your comp_panel
py::dict py_extract_composition_from_panel(py::object comp_panel) {
    py::dict result;

    try {
        // Get the composition dict and deck count from your panel
        py::dict comp_dict = comp_panel.attr("comp");
        int decks = py::cast<int>(comp_panel.attr("decks"));

        result["comp"] = comp_dict;
        result["decks"] = decks;

        return result;

    } catch (const std::exception& e) {
        py::dict error;
        error["error"] = std::string("Failed to extract composition: ") + e.what();
        return error;
    }
}

// Main function: Calculate EV using your comp_panel directly
py::dict py_calculate_ev_from_comp_panel(const std::vector<int>& hand,
                                        int dealer_upcard,
                                        py::object comp_panel,
                                        const RulesConfig& rules,
                                        const std::string& counter_system = "Hi-Lo") {
    try {
        // Extract composition from your panel
        py::dict composition = py_extract_composition_from_panel(comp_panel);

        if (composition.contains("error")) {
            return composition; // Return error if extraction failed
        }

        // Create engine and use provided rules
        bjlogic::AdvancedEVEngine engine(8, 0.001);

        // Convert composition to DeckState
        int decks = py::cast<int>(composition["decks"]);
        DeckState deck = python_composition_to_deck_state(composition, decks);

        // Create counter
        bjlogic::CountingSystem system = bjlogic::CountingSystem::HI_LO;
        if (counter_system == "Hi-Opt I") system = bjlogic::CountingSystem::HI_OPT_I;
        else if (counter_system == "Hi-Opt II") system = bjlogic::CountingSystem::HI_OPT_II;
        else if (counter_system == "Omega II") system = bjlogic::CountingSystem::OMEGA_II;
        else if (counter_system == "Zen Count") system = bjlogic::CountingSystem::ZEN_COUNT;
        else if (counter_system == "Uston APC") system = bjlogic::CountingSystem::USTON_APC;

        bjlogic::CardCounter counter(system, rules.num_decks);

        // Calculate EV with provided composition
        auto result = engine.calculate_ev_with_provided_composition(hand, dealer_upcard, deck, rules, counter);

        // Return detailed results
        py::dict py_result;
        py_result["stand_ev"] = result.stand_ev;
        py_result["hit_ev"] = result.hit_ev;
        py_result["double_ev"] = result.double_ev;
        py_result["split_ev"] = result.split_ev;
        py_result["surrender_ev"] = result.surrender_ev;
        py_result["insurance_ev"] = result.insurance_ev;
        py_result["optimal_action"] = BJLogicCore::action_to_string(result.optimal_action);
        py_result["optimal_ev"] = result.optimal_ev;
        py_result["variance"] = result.variance;
        py_result["advantage_over_basic"] = result.advantage_over_basic;
        py_result["composition_used"] = true;
        py_result["success"] = true;

        return py_result;

    } catch (const std::exception& e) {
        py::dict error_result;
        error_result["error"] = e.what();
        error_result["success"] = false;
        return error_result;
    }
}

// Test function for Phase 2.3
std::string test_counting_extension() {
    return "Advanced Card Counting & Probability Engine successfully implemented!";
}

// Simple card counter wrapper
py::dict py_create_card_counter(const std::string& system_name = "Hi-Lo", int num_decks = 6) {
    try {
        // Convert string to enum
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
        // Convert string to enum
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
    // DEALER PROBABILITY FUNCTION - ADD THIS FIRST
    // =================================================================

    m.def("calculate_exact_dealer_probabilities",
    [](int dealer_upcard,
       const py::dict& deck_composition,
       const py::dict& rules_dict) -> py::dict {
    try {
        // Convert rules
        RulesConfig rules = dict_to_rules_config(rules_dict);

        // Create recursive dealer engine
        bjlogic::RecursiveDealerEngine dealer_engine;

        // Create deck composition
        bjlogic::DeckComposition deck_comp(rules.num_decks);

        // Update deck composition from Python dict
        if (deck_composition.contains("cards_remaining")) {
            py::dict cards_rem = py::cast<py::dict>(deck_composition["cards_remaining"]);

            // Reset the deck composition based on cards remaining
            deck_comp.total_cards = 0;
            for (int i = 0; i < 13; ++i) {
                deck_comp.cards[i] = 0;
            }

            // Set cards remaining for each rank
            for (int rank = 1; rank <= 10; ++rank) {
                // FIX: Use py::int_ to wrap the integer key
                py::int_ py_rank(rank);
                if (cards_rem.contains(py_rank)) {
                    int count = py::cast<int>(cards_rem[py_rank]);
                    if (rank == 1) {
                        deck_comp.cards[0] = count;  // Ace
                    } else if (rank >= 2 && rank <= 9) {
                        deck_comp.cards[rank - 1] = count;
                    } else if (rank == 10) {
                        // Distribute 10s evenly across 10,J,Q,K
                        int per_slot = count / 4;
                        int remainder = count % 4;
                        for (int i = 9; i < 13; ++i) {
                            deck_comp.cards[i] = per_slot + (i - 9 < remainder ? 1 : 0);
                        }
                    }
                    deck_comp.total_cards += count;
                }
            }
        }

        // Calculate exact probabilities
        auto result = dealer_engine.calculate_exact_probabilities(dealer_upcard, deck_comp, rules);

        // Convert to Python dict
        py::dict py_result;
        py_result["prob_17"] = result.prob_17;
        py_result["prob_18"] = result.prob_18;
        py_result["prob_19"] = result.prob_19;
        py_result["prob_20"] = result.prob_20;
        py_result["prob_21"] = result.prob_21;
        py_result["prob_bust"] = result.prob_bust;
        py_result["prob_blackjack"] = result.prob_blackjack;
        py_result["success"] = true;
        py_result["recursive_calls"] = result.recursive_calls;
        py_result["from_cache"] = result.from_cache;

        // Verify total probability
        double total = result.get_total_probability();
        py_result["total_probability"] = total;

        return py_result;

    } catch (const std::exception& e) {
        py::dict error_result;
        error_result["error"] = e.what();
        error_result["success"] = false;
        error_result["prob_17"] = 0.0;
        error_result["prob_18"] = 0.0;
        error_result["prob_19"] = 0.0;
        error_result["prob_20"] = 0.0;
        error_result["prob_21"] = 0.0;
        error_result["prob_bust"] = 0.0;
        error_result["prob_blackjack"] = 0.0;
        return error_result;
    }
}, "Calculate exact dealer probabilities using recursive engine",
   py::arg("dealer_upcard"), py::arg("deck_composition"), py::arg("rules"));

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

    m.def("calculate_ev_from_comp_panel", &py_calculate_ev_from_comp_panel,
          "Calculate EV directly from comp_panel instance",
          py::arg("hand"), py::arg("dealer_upcard"), py::arg("comp_panel"),
          py::arg("rules"), py::arg("counter_system") = "Hi-Lo");

    // =================================================================
    // ADVANCED EV ENGINE BINDINGS
    // =================================================================

    // RulesConfig structure
    py::class_<bjlogic::RulesConfig>(m, "RulesConfig")
        .def(py::init<>())
        .def_readwrite("num_decks", &bjlogic::RulesConfig::num_decks)
        .def_readwrite("dealer_hits_soft_17", &bjlogic::RulesConfig::dealer_hits_soft_17)
        .def_readwrite("double_after_split", &bjlogic::RulesConfig::double_after_split)
        .def_readwrite("resplitting_allowed", &bjlogic::RulesConfig::resplitting_allowed)
        .def_readwrite("max_split_hands", &bjlogic::RulesConfig::max_split_hands)
        .def_readwrite("blackjack_payout", &bjlogic::RulesConfig::blackjack_payout)
        .def_readwrite("surrender_allowed", &bjlogic::RulesConfig::surrender_allowed)
        .def_readwrite("dealer_peek_on_ace", &bjlogic::RulesConfig::dealer_peek_on_ace)
        .def_readwrite("dealer_peek_on_ten", &bjlogic::RulesConfig::dealer_peek_on_ten)
        .def_readwrite("split_aces_one_card", &bjlogic::RulesConfig::split_aces_one_card)
        .def_readwrite("surrender_anytime_before_21", &bjlogic::RulesConfig::surrender_anytime_before_21)
        .def_readwrite("penetration", &bjlogic::RulesConfig::penetration);

    // AdvancedEVEngine
    py::class_<bjlogic::AdvancedEVEngine>(m, "AdvancedEVEngine")
        .def(py::init<int, double>(), py::arg("depth") = 10, py::arg("precision") = 0.0001)
        .def("calculate_true_count_ev", &bjlogic::AdvancedEVEngine::calculate_true_count_ev)
        .def("clear_cache", &bjlogic::AdvancedEVEngine::clear_cache)
        .def("get_cache_size", &bjlogic::AdvancedEVEngine::get_cache_size);

    // =================================================================
    // VERSION INFO
    // =================================================================

    m.attr("__version__") = "2.3.1-advanced-ev-fixed";
    m.attr("__phase__") = "Advanced EV Calculation Engine with Dealer Probabilities";
}