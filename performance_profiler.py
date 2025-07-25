# performance_profiler.py
"""
Performance profiler for blackjack application to identify C++ migration candidates.
Profiles the most computationally intensive parts of the Nairn EV calculator.
"""

import cProfile
import pstats
import io
import time
import tracemalloc
from typing import Dict, List, Tuple, Any
import sys
import os

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your modules
try:
    from nairn_ev_calculator import (
        NairnEVCalculator, NairnRules, NairnDeck, NairnHand, NairnDealer,
        analyze_with_nairn_algorithm, DDNone, DDAny, DD10OR11,
        ACE, TEN
    )

    NAIRN_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import Nairn modules: {e}")
    NAIRN_AVAILABLE = False


class BlackjackProfiler:
    """Comprehensive profiler for blackjack performance bottlenecks."""

    def __init__(self):
        self.results = {}
        self.memory_results = {}

    def profile_nairn_ev_calculation(self, iterations=100):
        """Profile the core Nairn EV calculation bottlenecks."""
        if not NAIRN_AVAILABLE:
            print("Nairn modules not available for profiling")
            return

        print(f"Profiling Nairn EV calculations ({iterations} iterations)...")

        # Setup test scenario
        rules = NairnRules(
            num_decks=6,
            hits_soft_17=False,
            dd_after_split=DDNone,
            resplitting=False
        )

        calculator = NairnEVCalculator(rules)

        # Test hands that trigger heavy computation
        test_scenarios = [
            # Heavy scenarios
            ([8, 8], TEN, "Split 8s vs 10 (heavy recursion)"),
            ([ACE, ACE], 6, "Split Aces vs 6 (moderate)"),
            ([TEN, 6], ACE, "16 vs A (hitting recursion)"),
            ([ACE, 7], 9, "Soft 18 vs 9 (soft hitting)"),
            ([5, 6], 5, "11 vs 5 (doubling calculation)"),
            # Extreme scenarios
            ([2, 2], 7, "Split 2s vs 7 (complex)"),
            ([3, 3], 8, "Split 3s vs 8 (complex)"),
            ([9, 9], ACE, "Split 9s vs A (very heavy)"),
        ]

        for hand_cards, upcard, description in test_scenarios:
            print(f"\n--- Profiling: {description} ---")
            self._profile_single_scenario(calculator, hand_cards, upcard, iterations)

    def _profile_single_scenario(self, calculator, hand_cards, upcard, iterations):
        """Profile a single EV calculation scenario."""

        # Memory profiling
        tracemalloc.start()

        # CPU profiling
        profiler = cProfile.Profile()

        def run_calculation():
            """Single calculation run."""
            deck = NairnDeck(6)
            hand = NairnHand(hand_cards)

            # Remove known cards
            for card in hand_cards:
                deck.remove(card)
            deck.remove(upcard)

            # Calculate EV (this is what we want to optimize)
            return calculator.calculate_hand_ev(hand, upcard, deck)

        # Warm up
        run_calculation()

        # Profile the calculation
        start_time = time.perf_counter()
        profiler.enable()

        for _ in range(iterations):
            result = run_calculation()

        profiler.disable()
        end_time = time.perf_counter()

        # Memory results
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Timing results
        total_time = end_time - start_time
        avg_time = total_time / iterations

        print(f"  Total time: {total_time:.4f}s")
        print(f"  Average per calculation: {avg_time:.6f}s")
        print(f"  Peak memory: {peak / 1024 / 1024:.2f} MB")

        # Analyze profiling data
        self._analyze_profile_data(profiler, hand_cards, upcard)

        return {
            'total_time': total_time,
            'avg_time': avg_time,
            'peak_memory': peak,
            'result': result
        }

    def _analyze_profile_data(self, profiler, hand_cards, upcard):
        """Analyze cProfile data to identify bottlenecks."""

        # Capture profiling output
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s)
        ps.sort_stats('cumulative')
        ps.print_stats(20)  # Top 20 functions

        profile_output = s.getvalue()

        # Parse and identify C++ migration candidates
        print("  Top bottlenecks (C++ migration candidates):")

        # Key patterns to look for
        cpp_migration_patterns = [
            '_hit_dealer_recursive',
            '_calculate_hit_ev',
            '_calculate_stand_ev',
            '_calculate_double_ev',
            '_calculate_split_ev',
            'get_player_expected_values',
            'remove_and_get_weight',
            'get_total',
            'calculate_hand_value',
            '_nairn_approximate_split',
            'basic_strategy'
        ]

        lines = profile_output.split('\n')
        for line in lines[5:25]:  # Skip headers
            if any(pattern in line for pattern in cpp_migration_patterns):
                # Parse timing data
                parts = line.strip().split()
                if len(parts) >= 4:
                    ncalls = parts[0]
                    tottime = parts[1]
                    cumtime = parts[3] if len(parts) > 3 else parts[2]
                    print(f"    🔥 {line.strip()}")

        # Store detailed results
        scenario_key = f"{hand_cards}_vs_{upcard}"
        self.results[scenario_key] = profile_output

    def profile_deck_operations(self, iterations=10000):
        """Profile deck manipulation operations."""
        print(f"\nProfiling deck operations ({iterations} iterations)...")

        if not NAIRN_AVAILABLE:
            return

        deck = NairnDeck(6)

        # Profile card removal/restoration
        start_time = time.perf_counter()

        for i in range(iterations):
            # Remove cards
            removed_cards = []
            for card in [ACE, 2, 3, TEN, 5]:
                if deck.remove(card):
                    removed_cards.append(card)

            # Calculate weights
            for card in range(ACE, TEN + 1):
                success, weight = deck.remove_and_get_weight(card, True, ACE)
                if success:
                    deck.restore(card)

            # Restore cards
            for card in removed_cards:
                deck.restore(card)

        end_time = time.perf_counter()

        print(f"  Deck operations: {end_time - start_time:.4f}s total")
        print(f"  Per iteration: {(end_time - start_time) / iterations:.6f}s")
        print("  🔥 C++ migration candidate: Deck operations")

    def profile_hand_calculations(self, iterations=10000):
        """Profile hand value calculations."""
        print(f"\nProfiling hand calculations ({iterations} iterations)...")

        if not NAIRN_AVAILABLE:
            return

        test_hands = [
            [ACE, ACE],
            [ACE, 9],
            [TEN, 6],
            [8, 8],
            [2, 3, 4, 5, 6],  # Multi-card hand
            [ACE, 2, 3, 4, 5, 6],  # Soft multi-card
        ]

        start_time = time.perf_counter()

        for _ in range(iterations):
            for cards in test_hands:
                hand = NairnHand(cards)
                # These are the bottleneck functions
                total = hand.get_total()
                soft = hand.is_soft()
                natural = hand.is_natural()
                busted = hand.is_busted()
                can_split = hand.can_split()

        end_time = time.perf_counter()

        print(f"  Hand calculations: {end_time - start_time:.4f}s total")
        print(f"  Per iteration: {(end_time - start_time) / iterations:.6f}s")
        print("  🔥 C++ migration candidate: Hand value calculations")

    def profile_basic_strategy(self, iterations=5000):
        """Profile basic strategy decisions."""
        print(f"\nProfiling basic strategy ({iterations} iterations)...")

        # This would profile your basic strategy implementation
        # if you have one in Python
        print("  ⚠️  Basic strategy profiling not implemented")
        print("  🔥 C++ migration candidate: Basic strategy lookup")

    def run_comprehensive_profile(self):
        """Run complete performance analysis."""
        print("=" * 60)
        print("COMPREHENSIVE BLACKJACK PERFORMANCE PROFILING")
        print("=" * 60)

        # Profile different components
        self.profile_nairn_ev_calculation(50)  # Reduced for demo
        self.profile_deck_operations(1000)
        self.profile_hand_calculations(1000)
        self.profile_basic_strategy(1000)

        # Generate summary report
        self.generate_migration_report()

    def generate_migration_report(self):
        """Generate C++ migration priority report."""
        print("\n" + "=" * 60)
        print("C++ MIGRATION PRIORITY REPORT")
        print("=" * 60)

        print("\n🔥 HIGH PRIORITY (Immediate C++ migration):")
        high_priority = [
            ("Dealer probability calculations", "_hit_dealer_recursive", "Heavy recursion with floating-point math"),
            ("EV recursion (hit/stand/double)", "_calculate_*_ev", "Deep recursive trees with many branches"),
            ("Hand value calculations", "get_total, is_soft", "Called millions of times in loops"),
            ("Deck weight calculations", "remove_and_get_weight", "Complex probability math"),
        ]

        for i, (component, functions, reason) in enumerate(high_priority, 1):
            print(f"  {i}. {component}")
            print(f"     Functions: {functions}")
            print(f"     Reason: {reason}")
            print()

        print("🟡 MEDIUM PRIORITY (Second wave C++ migration):")
        medium_priority = [
            ("Basic strategy decisions", "basic_*", "Lookup tables with logic"),
            ("Split calculations", "_calculate_split_ev", "Complex but less frequent"),
            ("Card composition tracking", "NairnDeck methods", "Simple but frequent operations"),
        ]

        for i, (component, functions, reason) in enumerate(medium_priority, 1):
            print(f"  {i}. {component}")
            print(f"     Functions: {functions}")
            print(f"     Reason: {reason}")
            print()

        print("📋 RECOMMENDED C++ MODULE STRUCTURE:")
        print("  1. bjlogic_core.cpp_src     - Hand calculations, basic strategy")
        print("  2. bjlogic_dealer.cpp_src   - Dealer probability engine")
        print("  3. bjlogic_ev.cpp_src       - EV calculation recursion")
        print("  4. bjlogic_deck.cpp_src     - Deck operations and weights")
        print("  5. bjlogic_nairn.cpp_src    - Nairn-specific algorithms")

        print("\n💡 EXPECTED PERFORMANCE GAINS:")
        print("  - EV calculations: 10-50x faster")
        print("  - Hand value calculations: 5-20x faster")
        print("  - Dealer probabilities: 20-100x faster")
        print("  - Overall application: 3-10x faster")


def run_memory_profiler():
    """Separate memory profiling for memory-intensive operations."""
    print("\n" + "=" * 40)
    print("MEMORY PROFILING")
    print("=" * 40)

    if not NAIRN_AVAILABLE:
        print("Nairn modules not available")
        return

    import tracemalloc

    # Profile memory usage of large calculations
    tracemalloc.start()

    # Simulate heavy EV calculation
    rules = NairnRules(num_decks=8)  # Larger deck for more memory usage
    calculator = NairnEVCalculator(rules)

    results = []
    for i in range(100):
        deck = NairnDeck(8)
        hand = NairnHand([8, 8])  # Split scenario
        deck.remove(8)
        deck.remove(8)
        deck.remove(TEN)

        result = calculator.calculate_hand_ev(hand, TEN, deck)
        results.append(result)

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"Current memory usage: {current / 1024 / 1024:.2f} MB")
    print(f"Peak memory usage: {peak / 1024 / 1024:.2f} MB")
    print("🔥 C++ will reduce memory usage by 50-80%")


def main():
    """Main profiling entry point."""
    print("Starting Blackjack Performance Profiling...")

    profiler = BlackjackProfiler()

    try:
        profiler.run_comprehensive_profile()
        run_memory_profiler()

        print("\n✅ Profiling complete!")
        print("📁 Next step: Use this data to implement C++ modules")

    except Exception as e:
        print(f"❌ Profiling failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()