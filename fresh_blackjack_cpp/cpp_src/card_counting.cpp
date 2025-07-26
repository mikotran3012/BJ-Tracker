// cpp_src/card_counting.cpp
/*
 * Phase 2.3: Implementation of Advanced Card Counting & Probability Engine
 */

#include "card_counting.hpp"
#include <random>
#include <cmath>
#include <algorithm>

namespace bjlogic {

// =============================================================================
// COUNTING SYSTEM DEFINITIONS
// =============================================================================

const std::unordered_map<CountingSystem, CountingValues> CardCounter::COUNTING_SYSTEMS = {
    {CountingSystem::HI_LO, {
        {{-1, 1, 1, 1, 1, 1, 0, 0, 0, -1}},  // A,2,3,4,5,6,7,8,9,T
        "Hi-Lo",
        0.97, 0.51, 0.76
    }},
    {CountingSystem::HI_OPT_I, {
        {{0, 0, 1, 1, 1, 1, 0, 0, 0, -1}},
        "Hi-Opt I",
        0.88, 0.61, 0.85
    }},
    {CountingSystem::HI_OPT_II, {
        {{0, 1, 1, 2, 2, 1, 1, 0, 0, -2}},
        "Hi-Opt II",
        0.91, 0.67, 0.85
    }},
    {CountingSystem::OMEGA_II, {
        {{0, 1, 1, 2, 2, 2, 1, 0, -1, -2}},
        "Omega II",
        0.92, 0.69, 0.85
    }},
    {CountingSystem::ZEN_COUNT, {
        {{-1, 1, 1, 2, 2, 2, 1, 0, 0, -2}},
        "Zen Count",
        0.96, 0.63, 0.85
    }},
    {CountingSystem::USTON_APC, {
        {{0, 1, 2, 2, 3, 2, 2, 1, -1, -3}},
        "Uston APC",
        0.69, 0.55, 0.78
    }}
};

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

void CardCounter::process_card(int rank) {
    if (rank < 1 || rank > 10) return;

    // Update running count
    const auto& system_values = COUNTING_SYSTEMS.at(current_system);
    int rank_index = (rank == 1) ? 0 : rank - 1;
    state.running_count += system_values.values[rank_index];

    // Track cards played
    cards_played[rank_index]++;
    state.cards_seen++;

    // Update derived values
    update_true_count();
    update_advantage();

    // Update deck state
    if (deck.cards_remaining[rank] > 0) {
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
        hash = hash * 31 + deck.cards_remaining[i+1];
    }
    return hash;
}

void CardCounter::update_true_count() {
    if (deck.total_cards <= 0) {
        state.true_count = 0.0;
        return;
    }

    double decks_remaining = deck.total_cards / 52.0;
    if (decks_remaining > 0.1) {  // Avoid division by very small numbers
        state.true_count = state.running_count / decks_remaining;
    } else {
        state.true_count = state.running_count / 0.1;  // Cap at 0.1 decks
    }
}

void CardCounter::update_advantage() {
    // Simplified advantage calculation based on true count
    // More sophisticated models would consider specific cards remaining
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
    // Where b = odds received, p = probability of winning, q = probability of losing
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

    // Simplified probability calculation
    // In a complete implementation, this would use recursive probability calculation
    // considering all possible dealer draws given the current deck composition

    std::array<double, 10> remaining_freqs = get_remaining_card_frequencies();

    // Basic probability estimates based on dealer upcard and remaining cards
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
    double ace_density = get_ace_density();

    // More tens remaining = higher bust probability for dealer
    result.dealer_bust_prob *= (1.0 + (ten_density - 0.3077) * 2.0);
    result.dealer_bust_prob = std::max(0.0, std::min(1.0, result.dealer_bust_prob));

    // Cache result
    prob_cache[cache_key] = result;

    return result;
}

AdvancedEV CardCounter::calculate_counting_ev(const std::vector<int>& hand,
                                            int dealer_upcard,
                                            const RulesConfig& rules) const {
    uint64_t cache_key = hash_deck_state() ^
                        (dealer_upcard << 8) ^
                        (hand.size() << 16);
    for (int card : hand) {
        cache_key ^= (card << 20);
    }

    auto cached = ev_cache.find(cache_key);
    if (cached != ev_cache.end()) {
        return cached->second;
    }

    AdvancedEV result;

    // Get basic strategy decision first
    Action basic_action = BJLogicCore::basic_strategy_decision(hand, dealer_upcard, rules);

    // Calculate dealer probabilities
    ProbabilityResult dealer_probs = calculate_dealer_probabilities(dealer_upcard);

    HandData hand_data = BJLogicCore::calculate_hand_value(hand);

    // Simplified EV calculations (complete implementation would be much more complex)
    result.stand_ev = -0.5 + state.advantage;  // Rough estimate
    result.hit_ev = -0.6 + state.advantage;
    result.double_ev = -0.4 + state.advantage * 2.0;  // Double the advantage/disadvantage
    result.split_ev = -0.5 + state.advantage;
    result.surrender_ev = -0.5;

    // Insurance EV calculation
    if (dealer_upcard == 1) {
        double ten_density = get_ten_density();
        result.insurance_ev = (ten_density * 2.0) - 1.0;  // 2:1 payout
    }

    // Apply counting adjustments
    if (state.true_count > 2.0) {
        result.stand_ev += 0.02;
        result.hit_ev += 0.01;
    } else if (state.true_count < -2.0) {
        result.hit_ev += 0.02;
        result.double_ev += 0.01;
    }

    // Find optimal action
    result.optimal_ev = result.stand_ev;
    result.optimal_action = Action::STAND;

    if (result.hit_ev > result.optimal_ev) {
        result.optimal_ev = result.hit_ev;
        result.optimal_action = Action::HIT;
    }
    if (result.double_ev > result.optimal_ev && hand.size() == 2) {
        result.optimal_ev = result.double_ev;
        result.optimal_action = Action::DOUBLE;
    }
    if (result.split_ev > result.optimal_ev && hand_data.can_split) {
        result.optimal_ev = result.split_ev;
        result.optimal_action = Action::SPLIT;
    }

    // Cache result
    ev_cache[cache_key] = result;

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
        if (hand_data.total == 10 && dealer_upcard == 10 && state.true_count >= 4) {
            return Action::DOUBLE; // Double 10 vs 10 at TC 4+
        }
        if (hand_data.total == 12 && dealer_upcard == 3 && state.true_count >= 2) {
            return Action::STAND;  // Stand 12 vs 3 at TC 2+
        }
        if (hand_data.total == 12 && dealer_upcard == 2 && state.true_count >= 3) {
            return Action::STAND;  // Stand 12 vs 2 at TC 3+
        }

        // Insurance decision
        if (dealer_upcard == 1 && state.true_count >= 3) {
            // Would need to return insurance action in expanded enum
        }
    }

    return basic_action;
}

bool CardCounter::should_take_insurance() const {
    if (current_system == CountingSystem::HI_LO) {
        return state.true_count >= 3.0;
    }

    // For other systems, check ten density
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
        frequencies[i] = static_cast<double>(deck.cards_remaining[rank]) / deck.total_cards;
    }

    return frequencies;
}

double CardCounter::get_ten_density() const {
    if (deck.total_cards <= 0) return 0.0;
    return static_cast<double>(deck.cards_remaining[10]) / deck.total_cards;
}

double CardCounter::get_ace_density() const {
    if (deck.total_cards <= 0) return 0.0;
    return static_cast<double>(deck.cards_remaining[1]) / deck.total_cards;
}

// =============================================================================
// SIMULATION ENGINE IMPLEMENTATION
// =============================================================================

SimulationEngine::SimulationEngine(uint32_t seed) : rng(seed) {}

SimulationResult SimulationEngine::run_simulation(const SimulationConfig& config) {
    SimulationResult result;
    CardCounter counter(config.counting_system, config.num_decks);

    double total_bet = 0.0;
    double total_winnings = 0.0;
    int wins = 0, losses = 0, pushes = 0;

    for (int hand = 0; hand < config.num_hands; ++hand) {
        // Reset deck if penetration reached
        if (counter.get_penetration() >= config.penetration * 100) {
            counter.reset_count();
        }

        // Determine bet size
        double bet = config.base_bet;
        if (config.use_counting) {
            bet = std::min(config.max_bet,
                          counter.get_optimal_bet_units(config.base_bet));
        }

        // Simulate hand (simplified)
        // In reality, this would involve full hand simulation
        std::uniform_real_distribution<> dis(0.0, 1.0);
        double outcome = dis(rng);

        total_bet += bet;

        if (outcome < 0.43) {  // Win
            total_winnings += bet * 1.5;  // Assume some blackjacks
            wins++;
        } else if (outcome < 0.51) {  // Push
            pushes++;
        } else {  // Loss
            total_winnings -= bet;
            losses++;
        }

        // Process some cards for counting
        std::vector<int> cards = {
            static_cast<int>(dis(rng) * 10) + 1,
            static_cast<int>(dis(rng) * 10) + 1,
            static_cast<int>(dis(rng) * 10) + 1
        };
        counter.process_cards(cards);
    }

    result.hands_played = config.num_hands;
    result.total_winnings = total_winnings;
    result.house_edge = -total_winnings / total_bet;
    result.win_rate = static_cast<double>(wins) / config.num_hands;
    result.push_rate = static_cast<double>(pushes) / config.num_hands;
    result.loss_rate = static_cast<double>(losses) / config.num_hands;
    result.rtp = (total_bet + total_winnings) / total_bet;

    return result;
}

SimulationResult SimulationEngine::test_basic_strategy(const RulesConfig& rules, int hands) {
    SimulationConfig config;
    config.num_hands = hands;
    config.rules = rules;
    config.use_counting = false;

    return run_simulation(config);
}

SimulationResult SimulationEngine::test_counting_system(CountingSystem system,
                                                      const RulesConfig& rules,
                                                      int hands) {
    SimulationConfig config;
    config.num_hands = hands;
    config.rules = rules;
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
        CountingSystem::USTON_APC
    };
}

double calculate_theoretical_house_edge(const RulesConfig& rules) {
    double base_edge = 0.0050;  // Starting point

    // Rule variations impact
    if (rules.dealer_hits_soft_17) base_edge += 0.0022;
    if (rules.double_after_split > 0) base_edge -= 0.0014;
    if (rules.surrender_allowed) base_edge -= 0.0002;
    if (rules.blackjack_payout < 1.5) base_edge += 0.0139;  // 6:5 vs 3:2

    // Deck composition
    if (rules.num_decks == 1) base_edge -= 0.0003;
    else if (rules.num_decks > 6) base_edge += 0.0001;

    return base_edge;
}

double calculate_optimal_bet_spread(double advantage, double risk_of_ruin) {
    if (advantage <= 0) return 1.0;

    // Kelly criterion with risk adjustment
    double kelly = advantage / 0.01;  // Assuming 1% variance
    double risk_multiplier = -std::log(risk_of_ruin) / 5.0;  // Risk adjustment

    return std::max(1.0, kelly * risk_multiplier);
}

} // namespace bjlogic