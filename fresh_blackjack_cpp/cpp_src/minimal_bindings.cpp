// cpp_src/minimal_bindings.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <string>
#include <vector>
#include <utility>

namespace py = pybind11;

// Declare functions from hand_calc.cpp
extern int get_card_value(const std::string &rank);
extern std::pair<int, bool> calculate_hand_value(const std::vector<std::string> &ranks);

// Test function
std::string test_extension() {
    return "🎉 C++ extension is working perfectly!";
}

// Module definition
PYBIND11_MODULE(bjlogic_cpp, m) {
    m.doc() = "Blackjack C++ logic - working version";

    m.def("test_extension", &test_extension, "Test function");

    m.def("get_card_value", &get_card_value,
          "Get numeric value of card rank",
          py::arg("rank"));

    m.def("calculate_hand_value", &calculate_hand_value,
          "Calculate hand value (total, is_soft)",
          py::arg("ranks"));

    m.attr("__version__") = "1.0.0";
}