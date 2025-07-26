// cpp_src/card_counting.cpp - FIXED VERSION
/*
 * Phase 2.3: Implementation of Advanced Card Counting & Probability Engine
 */

#include "card_counting.hpp"
#include <random>
#include <cmath>
#include <algorithm>

namespace bjlogic {

// =============================================================================
// COUNTING SYSTEM DEFINITIONS - FIXED IMPLEMENTATION
// =============================================================================

// FIXED: Properly define the static member with all 8 systems
const std::unordered_map<CountingSystem, CountingValues> CardCounter::COUNTING_SYSTEMS = {
    {CountingSystem::HI_LO, CountingValues(
        {-1, 1, 1, 1, 1, 1, 0, 0, 0, -1},
        "Hi-Lo", 0.97, 0.51, 0.76)},

    {CountingSystem::HI_OPT_I, CountingValues(
        {0, 0, 1, 1, 1, 1, 0, 0, 0, -1},
        "Hi-Opt I", 0.88, 0.61, 0.85)},

    {CountingSystem::HI_OPT_II, CountingValues(
        {0, 1, 1, 2, 2, 1, 1, 0, 0, -2},
        "Hi-Opt II", 0.91, 0.67, 0.91)},

    {CountingSystem::OMEGA_II, CountingValues(
        {0, 1, 1, 2, 2, 2, 1, 0, -1, -2},
        "Omega II", 0.92, 0.67, 0.85)},

    {CountingSystem::ZEN_COUNT, CountingValues(
        {-1, 1, 1, 2, 2, 2, 1, 0, 0, -2},
        "Zen Count", 0.96, 0.63, 0.85)},

    {CountingSystem::USTON_APC, CountingValues(
        {0, 1, 2, 2, 3, 2, 2, 1, -1, -3},
        "Uston APC", 0.69, 0.55, 0.78)},

    {CountingSystem::REVERE_RAPC, CountingValues(
        {-2, 1, 2, 2, 3, 2, 1, 0, -1, -2},
        "Revere RAPC", 0.62, 0.55, 0.90)},

    {CountingSystem::RED_7, CountingValues(
        {0, 1, 1, 1, 1, 1, 1, 0, 0, -1},
        "Red 7", 0.78, 0.45, 0.65)}
};

// Helper function for systems that aren't in the map (shouldn't happen, but safety)
CountingValues get_system_values_simple(CountingSystem system) {
    auto it = CardCounter::COUNTING_SYSTEMS.find(system);
    if (it != CardCounter::COUNTING_SYSTEMS.end()) {
        return it->second;
    }

    // Fallback to Hi-Lo if system not found
    return CardCounter::COUNTING_SYSTEMS.at(CountingSystem::HI_LO);
}

// =============================================================================
// CARD COUNTER IMPLEMENTATION
// =============================================================================

CardCounter::CardCounter(CountingSystem system, int num_decks)
    : current_system(system), deck(num_decks) {
    reset_count();
    cards_played.fill(0);
}

void CardCounter::reset_count() {
    state = CountState();
    cards_played.fill(0);
    clear_cache();
}

void CardCounter::update_side_counts(int rank) {
    if (rank == 1) {        // Ace
        state.aces_seen++;
    }

    // Future: Add other side counts here if needed
    // For example, some systems track 7s, 8s, etc.
}

// Add helper functions for USTON APC debugging
int CardCounter::get_aces_seen() const {
    return state.aces_seen;
}

int CardCounter::get_aces_remaining() const {
    int total_initial_aces = deck.num_decks * 4;
    return total_initial_aces - state.aces_seen;
}

double CardCounter::get_ace_adjustment() const {
    if (current_system != CountingSystem::USTON_APC) {
        return 0.0;  // Only relevant for USTON APC
    }

    double remaining_decks = deck.total_cards / 52.0;
    int aces_remaining = get_aces_remaining();
    double expected_aces = 4.0 * remaining_decks;

    return aces_remaining - expected_aces;
}

double CardCounter::get_adjusted_running_count() const {
    if (current_system == CountingSystem::USTON_APC) {
        return state.running_count + get_ace_adjustment();
    }
    return state.running_count;  // For other systems, no adjustment
}

void CardCounter::process_card(int rank) {
    if (rank < 1 || rank > 10) return;

    // Get system values from the static map
    const CountingValues& system_values = COUNTING_SYSTEMS.at(current_system);

    int rank_index = (rank == 1) ? 0 : rank - 1;
    state.running_count += system_values.values[rank_index];

    // Track cards played
    cards_played[rank_index]++;
    state.cards_seen++;

    // CRITICAL: Track aces for USTON APC (and any other systems that need it)
    update_side_counts(rank);

    // Update derived values
    update_true_count();
    update_advantage();

    // Update deck state
    if (deck.cards_remaining.at(rank) > 0) {
        deck.cards_remaining[rank]--;
        deck.total_cards--;
    }

    // Update penetration
    int total_initial_cards = 52 * deck.num_decks;
    state.penetration_percent = (state.cards_seen * 100) / total_initial_cards;
}

void CardCounter::process_cards(const std::vector<int>& cards) {
    for (int card : cards) {
        process_card(card);
    }
}

uint64_t CardCounter::hash_deck_state() const {
    uint64_t hash = 0;
    for (int i = 0; i < 10; ++i) {
        hash = hash * 31 + deck.cards_remaining.at(i+1);
    }
    return hash;
}

void CardCounter::update_true_count() {
    if (deck.total_cards <= 0) {
        state.true_count = 0.0;
        return;
    }

    double remaining_decks = deck.total_cards / 52.0;

    if (current_system == CountingSystem::USTON_APC) {
        // USTON APC: Complete formula with ace side count
        // Final True Count = (RC + (AR - 4×RD)) ÷ (RD × 2)

        // Calculate remaining half-decks
        double remaining_half_decks = remaining_decks * 2.0;

        // Calculate aces remaining
        int total_initial_aces = deck.num_decks * 4;
        int aces_remaining = total_initial_aces - state.aces_seen;

        // Expected aces for remaining decks
        double expected_aces = 4.0 * remaining_decks;

        // Ace Adjustment = Aces Remaining - (4 × Remaining Decks)
        double ace_adjustment = aces_remaining - expected_aces;

        // Adjusted Running Count = RC + Ace Adjustment
        double adjusted_running_count = state.running_count + ace_adjustment;

        // Final True Count = Adjusted RC ÷ Remaining Half-Decks
        if (remaining_half_decks > 0.1) {
            state.true_count = adjusted_running_count / remaining_half_decks;
        } else {
            state.true_count = adjusted_running_count / 0.2;  // Minimum half-deck
        }

    } else {
        // Standard balanced counts: true count = running count ÷ decks remaining
        if (remaining_decks > 0.1) {
            state.true_count = state.running_count / remaining_decks;
        } else {
            state.true_count = state.running_count / 0.1;
        }
    }
}

void CardCounter::update_advantage() {
    // Simplified advantage calculation based on true count
    double base_advantage = -0.005;  // Base house edge
    double count_advantage = state.true_count * 0.005;  // ~0.5% per true count

    state.advantage = base_advantage + count_advantage;

    // Cap advantage at reasonable bounds
    state.advantage = std::max(-0.10, std::min(0.10, state.advantage));
}

double CardCounter::get_optimal_bet_units(double base_unit) const {
    if (state.advantage <= 0) {
        return base_unit;  // Minimum bet
    }

    // Kelly betting: bet proportion to advantage
    double kelly_fraction = state.advantage / 0.01;  // Assuming 1% variance
    double bet_units = base_unit * (1.0 + kelly_fraction * 10.0);

    // Cap at reasonable maximum
    return std::min(bet_units, base_unit * 20.0);
}

double CardCounter::get_kelly_bet_fraction(double bankroll) const {
    if (state.advantage <= 0 || bankroll <= 0) {
        return 0.01;  // Minimum 1% of bankroll
    }

    // Kelly formula: f = (bp - q) / b
    double win_prob = 0.5 + state.advantage;
    double loss_prob = 1.0 - win_prob;
    double odds = 1.0;  // Even money

    double kelly = (odds * win_prob - loss_prob) / odds;

    // Conservative Kelly (quarter Kelly for reduced variance)
    return std::max(0.01, std::min(0.25, kelly * 0.25));
}

ProbabilityResult CardCounter::calculate_dealer_probabilities(int dealer_upcard) const {
    uint64_t cache_key = hash_deck_state() ^ (dealer_upcard << 8);

    auto cached = prob_cache.find(cache_key);
    if (cached != prob_cache.end()) {
        return cached->second;
    }

    ProbabilityResult result;

    // Basic probability estimates based on dealer upcard
    switch (dealer_upcard) {
        case 1:  // Ace
            result.dealer_bust_prob = 0.12;
            result.dealer_21_prob = 0.31;
            break;
        case 2:
            result.dealer_bust_prob = 0.35;
            result.dealer_21_prob = 0.12;
            break;
        case 3:
            result.dealer_bust_prob = 0.37;
            result.dealer_21_prob = 0.13;
            break;
        case 4:
            result.dealer_bust_prob = 0.40;
            result.dealer_21_prob = 0.13;
            break;
        case 5:
            result.dealer_bust_prob = 0.42;
            result.dealer_21_prob = 0.12;
            break;
        case 6:
            result.dealer_bust_prob = 0.42;
            result.dealer_21_prob = 0.17;
            break;
        case 7:
            result.dealer_bust_prob = 0.26;
            result.dealer_21_prob = 0.14;
            break;
        case 8:
            result.dealer_bust_prob = 0.24;
            result.dealer_21_prob = 0.13;
            break;
        case 9:
            result.dealer_bust_prob = 0.23;
            result.dealer_21_prob = 0.12;
            break;
        case 10:
            result.dealer_bust_prob = 0.23;
            result.dealer_21_prob = 0.13;
            break;
    }

    // Adjust probabilities based on card counting
    double ten_density = get_ten_density();
    result.dealer_bust_prob *= (1.0 + (ten_density - 0.3077) * 2.0);
    result.dealer_bust_prob = std::max(0.0, std::min(1.0, result.dealer_bust_prob));

    // Cache result
    prob_cache[cache_key] = result;
    return result;
}

AdvancedEV CardCounter::calculate_counting_ev(const std::vector<int>& hand,
                                            int dealer_upcard,
                                            const RulesConfig& rules) const {
    AdvancedEV result;

    // Simplified EV calculations
    result.stand_ev = -0.5 + state.advantage;
    result.hit_ev = -0.6 + state.advantage;
    result.double_ev = -0.4 + state.advantage * 2.0;
    result.split_ev = -0.5 + state.advantage;
    result.surrender_ev = -0.5;

    // Insurance EV calculation
    if (dealer_upcard == 1) {
        double ten_density = get_ten_density();
        result.insurance_ev = (ten_density * 2.0) - 1.0;
    }

    // Find optimal action
    result.optimal_ev = result.stand_ev;
    result.optimal_action = Action::STAND;

    if (result.hit_ev > result.optimal_ev) {
        result.optimal_ev = result.hit_ev;
        result.optimal_action = Action::HIT;
    }

    return result;
}

Action CardCounter::get_counting_strategy(const std::vector<int>& hand,
                                        int dealer_upcard,
                                        const RulesConfig& rules) const {
    // Get basic strategy first
    Action basic_action = BJLogicCore::basic_strategy_decision(hand, dealer_upcard, rules);

    // Apply common counting deviations for Hi-Lo
    if (current_system == CountingSystem::HI_LO) {
        HandData hand_data = BJLogicCore::calculate_hand_value(hand);

        // Common Hi-Lo deviations (Illustrious 18)
        if (hand_data.total == 16 && dealer_upcard == 10 && state.true_count >= 0) {
            return Action::STAND;  // Stand 16 vs 10 at TC 0+
        }
        if (hand_data.total == 15 && dealer_upcard == 10 && state.true_count >= 4) {
            return Action::STAND;  // Stand 15 vs 10 at TC 4+
        }
    }

    return basic_action;
}

bool CardCounter::should_take_insurance() const {
    if (current_system == CountingSystem::HI_LO) {
        return state.true_count >= 3.0;
    }
    return get_ten_density() > 0.33;
}

std::string CardCounter::get_system_name() const {
    return COUNTING_SYSTEMS.at(current_system).name;
}

CountingValues CardCounter::get_system_values() const {
    return COUNTING_SYSTEMS.at(current_system);
}

std::array<double, 10> CardCounter::get_remaining_card_frequencies() const {
    std::array<double, 10> frequencies;

    if (deck.total_cards <= 0) {
        frequencies.fill(0.0);
        return frequencies;
    }

    for (int i = 0; i < 10; ++i) {
        int rank = (i == 0) ? 1 : i + 1;
        frequencies[i] = static_cast<double>(deck.cards_remaining.at(rank)) / deck.total_cards;
    }

    return frequencies;
}

double CardCounter::get_ten_density() const {
    if (deck.total_cards <= 0) return 0.0;
    return static_cast<double>(deck.cards_remaining.at(10)) / deck.total_cards;
}

double CardCounter::get_ace_density() const {
    if (deck.total_cards <= 0) return 0.0;
    return static_cast<double>(deck.cards_remaining.at(1)) / deck.total_cards;
}

// =============================================================================
// SIMULATION ENGINE IMPLEMENTATION
// =============================================================================

SimulationEngine::SimulationEngine(uint32_t seed) : rng(seed) {}

SimulationResult SimulationEngine::run_simulation(const SimulationConfig& config) {
    SimulationResult result;
    result.hands_played = config.num_hands;
    result.house_edge = 0.005;  // Simplified
    result.win_rate = 0.43;
    result.push_rate = 0.08;
    result.loss_rate = 0.49;
    result.rtp = 0.995;
    return result;
}

SimulationResult SimulationEngine::test_basic_strategy(const RulesConfig& rules, int hands) {
    SimulationConfig config;
    config.num_hands = hands;
    config.use_counting = false;
    return run_simulation(config);
}

SimulationResult SimulationEngine::test_counting_system(CountingSystem system,
                                                      const RulesConfig& rules,
                                                      int hands) {
    SimulationConfig config;
    config.num_hands = hands;
    config.use_counting = true;
    config.counting_system = system;
    return run_simulation(config);
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

std::string counting_system_to_string(CountingSystem system) {
    return CardCounter::COUNTING_SYSTEMS.at(system).name;
}

std::vector<CountingSystem> get_available_counting_systems() {
    return {
        CountingSystem::HI_LO,
        CountingSystem::HI_OPT_I,
        CountingSystem::HI_OPT_II,
        CountingSystem::OMEGA_II,
        CountingSystem::ZEN_COUNT,
        CountingSystem::USTON_APC,
        CountingSystem::REVERE_RAPC,
        CountingSystem::RED_7
    };
}

double calculate_theoretical_house_edge(const RulesConfig& rules) {
    double base_edge = 0.0050;
    if (rules.dealer_hits_soft_17) base_edge += 0.0022;
    if (rules.double_after_split > 0) base_edge -= 0.0014;
    if (rules.surrender_allowed) base_edge -= 0.0002;
    return base_edge;
}

double calculate_optimal_bet_spread(double advantage, double risk_of_ruin) {
    if (advantage <= 0) return 1.0;
    double kelly = advantage / 0.01;
    return std::max(1.0, kelly);
}

} // namespace bjlogic