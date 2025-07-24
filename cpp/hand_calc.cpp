#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <string>
#include <utility>

namespace py = pybind11;

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
    while (total > 21 && aces > 0) {
        total -= 10;
        aces--;
    }
    bool is_soft = aces > 0 && total <= 21;
    return {total, is_soft};
}

PYBIND11_MODULE(bjlogic, m) {
    m.doc() = "C++ blackjack helper functions";
    m.def("calculate_hand_value", &calculate_hand_value, "Calculate blackjack hand value");
}