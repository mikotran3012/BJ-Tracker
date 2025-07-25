// bjlogic_bindings.cpp
/*
 * PyBind11 bindings for high-performance blackjack C++ logic
 * Exposes all C++ functions to Python with proper type conversion
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <pybind11/stl_bind.h>
#include "bjlogic_core.hpp"

namespace py = pybind11;
using namespace bjlogic;

// =============================================================================
// UTILITY FUNCTIONS FOR TYPE CONVERSION
// =============================================================================

// Convert Python list to std::vector<int> with validation
std::vector<int> convert_cards(const py::list& cards) {
    std::vector<int> result;
    result.reserve(cards.size());

    for (const auto& card : cards) {
        int card_val = py::cast<int>(card);
        if (card_val < 1 || card_val > 10) {
            throw std::invalid_argument("Card values must be 1-10 (1=Ace, 10=T/J/Q/K)");
        }
        result.push_back(card_val);
    }

    return result;
}

// Convert DeckState from Python dict
DeckState convert_deck_state(const py::dict& deck_dict) {
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

// Convert RulesConfig from Python dict
RulesConfig convert_rules_config(const py::dict& rules_dict) {
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

// Wrapper for calculate_hand_value with Python-friendly interface
py::dict py_calculate_hand_value(const py::list& cards) {
    std::vector<int> card_vec = convert_cards(cards);
    HandData result = BJLogicCore::calculate_hand_value(card_vec);

    return py::dict("cards"_a=result.cards,
                   "total"_a=result.total,
                   "is_soft"_a=result.is_soft,
                   "can_split"_a=result.can_split,
                   "is_blackjack"_a=result.is_blackjack,
                   "is_busted"_a=result.is_busted);
}

// Wrapper for basic strategy with enum conversion
std::string py_basic_strategy_decision(const py::list& hand_cards,
                                      int dealer_upcard,
                                      const py::dict& rules_dict) {
    std::vector<int> cards = convert_cards(hand_cards);
    RulesConfig rules = convert_rules_config(rules_dict);

    Action action = BJLogicCore::basic_strategy_decision(cards, dealer_upcard, rules);

    switch (action) {
        case Action::STAND: return "stand";
        case Action::HIT: return "hit";
        case Action::DOUBLE: return "double";
        case Action::SPLIT: return "split";
        case Action::SURRENDER: return "surrender";
        default: return "stand";
    }
}

// Wrapper for dealer probabilities
py::list py_calculate_dealer_probabilities(int upcard,
                                          const py::dict& deck_dict,
                                          const py::dict& rules_dict) {
    DeckState deck = convert_deck_state(deck_dict);
    RulesConfig rules = convert_rules_config(rules_dict);

    std::vector<double> probs = BJLogicDealer::calculate_dealer_probabilities(upcard, deck, rules);

    py::list result;
    for (double prob : probs) {
        result.append(prob);
    }
    return result;
}

// Wrapper for optimal EV calculation
py::dict py_calculate_optimal_ev(const py::list& hand_cards,
                                int dealer_upcard,
                                const py::dict& deck_dict,
                                const py::dict& rules_dict) {
    std::vector<int> cards = convert_cards(hand_cards);
    DeckState deck = convert_deck_state(deck_dict);
    RulesConfig rules = convert_rules_config(rules_dict);

    EVResult result = BJLogicEV::calculate_optimal_ev(cards, dealer_upcard, deck, rules);

    return py::dict("stand_ev"_a=result.stand_ev,
                   "hit_ev"_a=result.hit_ev,
                   "double_ev"_a=result.double_ev,
                   "split_ev"_a=result.split_ev,
                   "surrender_ev"_a=result.surrender_ev,
                   "best_action"_a=result.best_action,
                   "best_ev"_a=result.best_ev);
}

// Wrapper for Nairn exact splitting
py::dict py_nairn_exact_split_ev(int split_card,
                                int dealer_upcard,
                                const py::dict& deck_dict,
                                const py::dict& rules_dict,
                                int max_hands = 4) {
    DeckState deck = convert_deck_state(deck_dict);
    RulesConfig rules = convert_rules_config(rules_dict);

    std::map<std::string, double> result = BJLogicNairn::nairn_exact_split_ev(
        split_card, dealer_upcard, deck, rules, max_hands);

    py::dict py_result;
    for (const auto& pair : result) {
        py_result[pair.first.c_str()] = pair.second;
    }
    return py_result;
}

// Wrapper for Griffin card removal effects
py::dict py_griffin_card_removal_effects(const py::list& hand_cards,
                                         int dealer_upcard,
                                         const py::dict& deck_dict) {
    std::vector<int> cards = convert_cards(hand_cards);
    DeckState deck = convert_deck_state(deck_dict);

    std::map<int, double> result = BJLogicNairn::griffin_card_removal_effects(
        cards, dealer_upcard, deck);

    py::dict py_result;
    for (const auto& pair : result) {
        py_result[py::int_(pair.first)] = pair.second;
    }
    return py_result;
}

// Wrapper for deck operations
py::dict py_create_deck_state(int num_decks) {
    DeckState deck = BJLogicDeck::create_deck_state(num_decks);

    py::dict cards_remaining;
    for (const auto& pair : deck.cards_remaining) {
        cards_remaining[py::int_(pair.first)] = pair.second;
    }

    return py::dict("num_decks"_a=deck.num_decks,
                   "cards_remaining"_a=cards_remaining,
                   "total_cards"_a=deck.total_cards);
}

py::dict py_remove_cards(const py::dict& deck_dict, const py::list& cards) {
    DeckState deck = convert_deck_state(deck_dict);
    std::vector<int> card_vec = convert_cards(cards);

    DeckState new_deck = BJLogicDeck::remove_cards(deck, card_vec);

    py::dict cards_remaining;
    for (const auto& pair : new_deck.cards_remaining) {
        cards_remaining[py::int_(pair.first)] = pair.second;
    }

    return py::dict("num_decks"_a=new_deck.num_decks,
                   "cards_remaining"_a=cards_remaining,
                   "total_cards"_a=new_deck.total_cards);
}

// High-performance batch calculation for multiple hands
py::list py_batch_calculate_ev(const py::list& hand_list,
                              const py::list& dealer_upcards,
                              const py::dict& deck_dict,
                              const py::dict& rules_dict) {
    DeckState deck = convert_deck_state(deck_dict);
    RulesConfig rules = convert_rules_config(rules_dict);

    py::list results;

    size_t num_hands = py::len(hand_list);
    size_t num_upcards = py::len(dealer_upcards);

    for (size_t i = 0; i < num_hands; ++i) {
        py::list hand_cards = py::cast<py::list>(hand_list[i]);
        std::vector<int> cards = convert_cards(hand_cards);

        int upcard_idx = i % num_upcards;
        int dealer_upcard = py::cast<int>(dealer_upcards[upcard_idx]);

        EVResult result = BJLogicEV::calculate_optimal_ev(cards, dealer_upcard, deck, rules);

        py::dict result_dict = py::dict("stand_ev"_a=result.stand_ev,
                                       "hit_ev"_a=result.hit_ev,
                                       "double_ev"_a=result.double_ev,
                                       "split_ev"_a=result.split_ev,
                                       "surrender_ev"_a=result.surrender_ev,
                                       "best_action"_a=result.best_action,
                                       "best_ev"_a=result.best_ev);
        results.append(result_dict);
    }

    return results;
}

// =============================================================================
// PERFORMANCE MONITORING FUNCTIONS
// =============================================================================

// Cache statistics for performance monitoring
py::dict py_get_cache_stats() {
    // Implementation would track cache hit rates, memory usage, etc.
    return py::dict("dealer_cache_size"_a=BJLogicDealer::dealer_cache.size(),
                   "ev_cache_size"_a=BJLogicEV::ev_cache.size(),
                   "cache_hit_rate"_a=0.85);  // Placeholder
}

// Clear caches to free memory
void py_clear_caches() {
    BJLogicDealer::dealer_cache.clear();
    BJLogicEV::ev_cache.clear();
}

// =============================================================================
// MODULE DEFINITION
// =============================================================================

PYBIND11_MODULE(bjlogic_cpp, m) {
    m.doc() = "High-performance blackjack logic implemented in C++";

    // =================================================================
    // CORE FUNCTIONS
    // =================================================================

    m.def("calculate_hand_value", &py_calculate_hand_value,
          "Calculate hand value and properties",
          py::arg("cards"));

    m.def("basic_strategy_decision", &py_basic_strategy_decision,
          "Get basic strategy decision for hand",
          py::arg("hand_cards"), py::arg("dealer_upcard"), py::arg("rules"));

    // =================================================================
    // DEALER PROBABILITY FUNCTIONS
    // =================================================================

    m.def("calculate_dealer_probabilities", &py_calculate_dealer_probabilities,
          "Calculate dealer final hand probabilities",
          py::arg("upcard"), py::arg("deck_state"), py::arg("rules"));


    // =================================================================
    // EXPECTED VALUE FUNCTIONS
    // =================================================================

    m.def("calculate_stand_ev", [](const py::list& hand_cards, int dealer_upcard,
                                  const py::dict& deck_dict, const py::dict& rules_dict) {
        std::vector<int> cards = convert_cards(hand_cards);
        DeckState deck = convert_deck_state(deck_dict);
        RulesConfig rules = convert_rules_config(rules_dict);
        return BJLogicEV::calculate_stand_ev(cards, dealer_upcard, deck, rules);
    }, "Calculate expected value of standing",
       py::arg("hand_cards"), py::arg("dealer_upcard"), py::arg("deck_state"), py::arg("rules"));

    m.def("calculate_hit_ev", [](const py::list& hand_cards, int dealer_upcard,
                                const py::dict& deck_dict, const py::dict& rules_dict) {
        std::vector<int> cards = convert_cards(hand_cards);
        DeckState deck = convert_deck_state(deck_dict);
        RulesConfig rules = convert_rules_config(rules_dict);
        return BJLogicEV::calculate_hit_ev(cards, dealer_upcard, deck, rules);
    }, "Calculate expected value of hitting",
       py::arg("hand_cards"), py::arg("dealer_upcard"), py::arg("deck_state"), py::arg("rules"));

    m.def("calculate_double_ev", [](const py::list& hand_cards, int dealer_upcard,
                                   const py::dict& deck_dict, const py::dict& rules_dict) {
        std::vector<int> cards = convert_cards(hand_cards);
        DeckState deck = convert_deck_state(deck_dict);
        RulesConfig rules = convert_rules_config(rules_dict);
        return BJLogicEV::calculate_double_ev(cards, dealer_upcard, deck, rules);
    }, "Calculate expected value of doubling down",
       py::arg("hand_cards"), py::arg("dealer_upcard"), py::arg("deck_state"), py::arg("rules"));

    m.def("calculate_split_ev", [](const py::list& hand_cards, int dealer_upcard,
                                  const py::dict& deck_dict, const py::dict& rules_dict) {
        std::vector<int> cards = convert_cards(hand_cards);
        DeckState deck = convert_deck_state(deck_dict);
        RulesConfig rules = convert_rules_config(rules_dict);
        return BJLogicEV::calculate_split_ev(cards, dealer_upcard, deck, rules);
    }, "Calculate expected value of splitting",
       py::arg("hand_cards"), py::arg("dealer_upcard"), py::arg("deck_state"), py::arg("rules"));

    m.def("calculate_optimal_ev", &py_calculate_optimal_ev,
          "Calculate all action EVs and determine optimal play",
          py::arg("hand_cards"), py::arg("dealer_upcard"), py::arg("deck_state"), py::arg("rules"));

    // =================================================================
    // DECK OPERATION FUNCTIONS
    // =================================================================

    m.def("create_deck_state", &py_create_deck_state,
          "Create fresh deck state",
          py::arg("num_decks"));

    m.def("remove_cards", &py_remove_cards,
          "Remove cards from deck state",
          py::arg("deck_state"), py::arg("cards"));

    m.def("calculate_card_weight", [](int card, const py::dict& deck_dict,
                                     int dealer_upcard, bool avoid_blackjack = true) {
        DeckState deck = convert_deck_state(deck_dict);
        return BJLogicDeck::calculate_card_weight(card, deck, dealer_upcard, avoid_blackjack);
    }, "Calculate probability weight for drawing specific card",
       py::arg("card"), py::arg("deck_state"), py::arg("dealer_upcard"),
       py::arg("avoid_blackjack") = true);

    // =================================================================
    // NAIRN'S EXACT ALGORITHMS
    // =================================================================

    m.def("nairn_exact_split_ev", &py_nairn_exact_split_ev,
          "Nairn's exact splitting algorithm",
          py::arg("split_card"), py::arg("dealer_upcard"), py::arg("deck_state"),
          py::arg("rules"), py::arg("max_hands") = 4);

    m.def("griffin_card_removal_effects", &py_griffin_card_removal_effects,
          "Griffin's card removal effect analysis",
          py::arg("hand_cards"), py::arg("dealer_upcard"), py::arg("deck_state"));

    // =================================================================
    // BATCH PROCESSING FUNCTIONS (for high performance)
    // =================================================================

    m.def("batch_calculate_ev", &py_batch_calculate_ev,
          "Calculate EV for multiple hands efficiently",
          py::arg("hand_list"), py::arg("dealer_upcards"), py::arg("deck_state"), py::arg("rules"));

    // =================================================================
    // PERFORMANCE MONITORING
    // =================================================================

    m.def("get_cache_stats", &py_get_cache_stats,
          "Get cache statistics for performance monitoring");

    m.def("clear_caches", &py_clear_caches,
          "Clear all caches to free memory");

    // =================================================================
    // CONSTANTS AND ENUMS
    // =================================================================

    py::enum_<Action>(m, "Action")
        .value("STAND", Action::STAND)
        .value("HIT", Action::HIT)
        .value("DOUBLE", Action::DOUBLE)
        .value("SPLIT", Action::SPLIT)
        .value("SURRENDER", Action::SURRENDER);

    // =================================================================
    // VERSION AND BUILD INFO
    // =================================================================

    m.attr("__version__") = "1.0.0";
    m.attr("__build_date__") = __DATE__;
    m.attr("__compiler__") =
#ifdef __clang__
        "clang " __clang_version__;
#elif defined(__GNUC__)
        "gcc " __VERSION__;
#elif defined(_MSC_VER)
        "msvc";
#else
        "unknown";
#endif
}