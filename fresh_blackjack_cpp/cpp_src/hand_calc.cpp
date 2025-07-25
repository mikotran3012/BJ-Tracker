// hand_calc.cpp
// Corrected logic for soft hands

#include <vector>
#include <string>
#include <utility>

int get_card_value(const std::string &rank) {
    if (rank == "J" || rank == "Q" || rank == "K" || rank == "T" || rank == "10")
        return 10;
    if (rank == "A")
        return 11;
    return std::stoi(rank);
}

std::pair<int, bool> calculate_hand_value(const std::vector<std::string> &ranks) {
    int total = 0;
    int aces = 0;

    for (const auto &rank : ranks) {
        if (rank == "A") {
            aces++;
            total += 11;
        } else {
            total += get_card_value(rank);
        }
    }

    // Convert aces from 11 to 1 if needed
    int aces_as_eleven = aces;
    while (total > 21 && aces_as_eleven > 0) {
        total -= 10;
        aces_as_eleven--;
    }

    // A hand is "soft" only if:
    // 1. It has at least one ace counting as 11
    // 2. The total is less than 21 (if it's exactly 21, it's a natural/blackjack, not soft)
    bool is_soft = (aces_as_eleven > 0) && (total < 21);

    return {total, is_soft};
}