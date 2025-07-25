// cpp_src/enhanced_bindings.cpp
/*
 * Phase 2.1: Enhanced PyBind11 bindings with advanced data structures
 * Fixed version without _a literals for compatibility
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/operators.h>
#include "bjlogic_core.hpp"

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

// Convert Python dict to DeckState
DeckState dict_to_deck_state(const py::dict& deck_dict) {
    DeckState deck;

    if (deck_dict.contains("num_decks")) {
        deck.num_decks = py::cast<int>(deck_dict["num_decks"]);
    }

    if (deck_dict.contains("cards_remaining")) {
        py::dict cards = py::cast<py::dict>(deck_dict["cards_remaining"]);
        deck.cards_remaining.clear();
        deck.total_cards = 0;

        for (const auto& item : cards) {
            int rank = py::cast<int>(item.first);
            int count = py::cast<int>(item.second);
            deck.cards_remaining[rank] = count;
            deck.total_cards += count;
        }
    }

    return deck;
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

// Basic strategy wrapper
std::string py_basic_strategy_decision(const std::vector<int>& hand_cards,
                                      int dealer_upcard,
                                      const py::dict& rules_dict) {
    RulesConfig rules = dict_to_rules_config(rules_dict);
    Action action = BJLogicCore::basic_strategy_decision(hand_cards, dealer_upcard, rules);

    switch (action) {
        case Action::STAND: return "stand";
        case Action::HIT: return "hit";
        case Action::DOUBLE: return "double";
        case Action::SPLIT: return "split";
        case Action::SURRENDER: return "surrender";
        default: return "stand";
    }
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

// Test function for migration verification
std::string test_advanced_extension() {
    return "🚀 Advanced bjlogic structures successfully migrated to C++!";
}

// Keep backward compatibility with original functions
extern int get_card_value(const std::string &rank);
extern std::pair<int, bool> calculate_hand_value(const std::vector<std::string> &ranks);

// =============================================================================
// MODULE DEFINITION
// =============================================================================

PYBIND11_MODULE(bjlogic_cpp, m) {
    m.doc() = "Advanced Blackjack C++ Logic - Phase 2.1 Migration";

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

    m.def("test_extension", &test_advanced_extension, "Test advanced extension");

    m.def("calculate_hand_value", &py_calculate_hand_value,
          "Enhanced hand value calculation with full details",
          py::arg("cards"));

    m.def("basic_strategy_decision", &py_basic_strategy_decision,
          "Get basic strategy decision",
          py::arg("hand_cards"), py::arg("dealer_upcard"), py::arg("rules"));

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
    // BACKWARD COMPATIBILITY
    // =================================================================

    m.def("get_card_value", &get_card_value,
          "Get numeric value of card rank (compatibility)",
          py::arg("rank"));

    m.def("calculate_hand_value_legacy", &calculate_hand_value,
          "Calculate hand value from string ranks (compatibility)",
          py::arg("ranks"));

    // =================================================================
    // VERSION INFO
    // =================================================================

    m.attr("__version__") = "2.1.0-migration";
    m.attr("__phase__") = "Core Data Structures";
}