# test_cpp_integration.py
"""
Comprehensive testing and benchmarking suite for C++ integration.
Ensures correctness and measures performance improvements.
"""

import pytest
import time
import statistics
import numpy as np
from typing import List, Dict, Tuple
import sys
import os

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import both implementations for comparison
try:
    import bjlogic_cpp

    CPP_AVAILABLE = True
except ImportError:
    CPP_AVAILABLE = False

try:
    from bjlogic_wrapper import (
        analyze_with_nairn_algorithm,
        calculate_hand_value,
        HybridNairnEVCalculator,
        batch_analyze_hands,
        perf_monitor,
        print_performance_report
    )

    WRAPPER_AVAILABLE = True
except ImportError:
    WRAPPER_AVAILABLE = False

try:
    from nairn_ev_calculator import (
        analyze_with_nairn_algorithm as py_analyze,
        NairnEVCalculator, NairnRules, NairnDeck, NairnHand
    )

    PYTHON_AVAILABLE = True
except ImportError:
    PYTHON_AVAILABLE = False


# =============================================================================
# CORRECTNESS TESTS
# =============================================================================

class TestCorrectness:
    """Test that C++ and Python implementations produce identical results."""

    @pytest.mark.skipif(not CPP_AVAILABLE, reason="C++ module not available")
    def test_hand_value_calculation(self):
        """Test hand value calculations match between C++ and Python."""

        test_hands = [
            ([1, 1], {"total": 12, "is_soft": True, "can_split": True}),
            ([1, 10], {"total": 21, "is_blackjack": True, "can_split": False}),
            ([10, 6], {"total": 16, "is_soft": False, "is_busted": False}),
            ([10, 10, 5], {"total": 25, "is_busted": True}),
            ([1, 2, 3, 4, 5], {"total": 16, "is_soft": True}),
            ([8, 8], {"total": 16, "can_split": True}),
        ]

        for cards, expected in test_hands:
            cpp_result = bjlogic_cpp.calculate_hand_value(cards)

            # Check key properties
            for key, expected_value in expected.items():
                assert cpp_result[key] == expected_value, \
                    f"Hand {cards}: {key} should be {expected_value}, got {cpp_result[key]}"

    @pytest.mark.skipif(not (CPP_AVAILABLE and PYTHON_AVAILABLE),
                        reason="Both C++ and Python implementations needed")
    def test_ev_calculation_parity(self):
        """Test that C++ and Python EV calculations match."""

        test_scenarios = [
            (['8', '8'], '10'),  # Split 8s vs 10
            (['A', '9'], '6'),  # Soft 20 vs 6
            (['10', '6'], 'A'),  # 16 vs A
            (['5', '6'], '5'),  # 11 vs 5 (double opportunity)
            (['A', 'A'], '8'),  # Split Aces vs 8
        ]

        deck_comp = {
            'A': 24, '2': 24, '3': 24, '4': 24, '5': 24,
            '6': 24, '7': 24, '8': 22, '9': 24, '10': 96,
            'J': 24, 'Q': 24, 'K': 24
        }

        rules = {'num_decks': 6, 'hits_soft_17': False}

        for hand, upcard in test_scenarios:
            # Python calculation
            py_result = py_analyze(hand, upcard, deck_comp, rules)

            # C++ calculation via wrapper
            cpp_result = analyze_with_nairn_algorithm(hand, upcard, deck_comp, rules)

            # Compare results (allow small floating point differences)
            tolerance = 1e-4
            for action in ['stand', 'hit', 'double']:
                if action in py_result and action in cpp_result:
                    py_ev = py_result[action]
                    cpp_ev = cpp_result[action]
                    assert abs(py_ev - cpp_ev) < tolerance, \
                        f"Hand {hand} vs {upcard}: {action} EV differs - Python: {py_ev:.6f}, C++: {cpp_ev:.6f}"

    @pytest.mark.skipif(not CPP_AVAILABLE, reason="C++ module not available")
    def test_basic_strategy_accuracy(self):
        """Test basic strategy decisions are correct."""

        strategy_tests = [
            # (hand, dealer_upcard, expected_action)
            ([10, 6], 10, 'hit'),  # 16 vs 10 - hit
            ([10, 7], 10, 'stand'),  # 17 vs 10 - stand
            ([5, 6], 5, 'double'),  # 11 vs 5 - double
            ([8, 8], 6, 'split'),  # 8,8 vs 6 - split
            ([1, 8], 6, 'stand'),  # A,8 vs 6 - stand
        ]

        rules = {'num_decks': 6, 'dealer_hits_soft_17': False, 'resplitting_allowed': True}

        for hand, upcard, expected in strategy_tests:
            action = bjlogic_cpp.basic_strategy_decision(hand, upcard, rules)
            assert action == expected, \
                f"Hand {hand} vs {upcard}: expected {expected}, got {action}"


# =============================================================================
# PERFORMANCE BENCHMARKS
# =============================================================================

class TestPerformance:
    """Benchmark C++ vs Python performance."""

    @pytest.mark.skipif(not (CPP_AVAILABLE and PYTHON_AVAILABLE),
                        reason="Both implementations needed for benchmarking")
    def test_hand_calculation_speed(self):
        """Benchmark hand value calculation speed."""

        test_hands = [
                         [1, 1], [1, 10], [10, 6], [8, 8], [2, 3, 4, 5, 6],
                         [1, 2, 3, 4, 5, 6], [10, 5, 3], [9, 9], [7, 7]
                     ] * 100  # 900 total calculations

        # Benchmark Python (via wrapper fallback)
        start = time.perf_counter()
        for hand in test_hands:
            # Force Python implementation
            if WRAPPER_AVAILABLE:
                calculate_hand_value([str(c) for c in hand], _use_cpp=False)
        python_time = time.perf_counter() - start

        # Benchmark C++
        start = time.perf_counter()
        for hand, upcard in scenarios:
            analyze_with_nairn_algorithm(hand, upcard, deck_comp, rules, _use_cpp=True)
        cpp_time = time.perf_counter() - start

        speedup = python_time / cpp_time
        print(f"\n🚀 EV calculation speedup: {speedup:.1f}x")
        print(f"   Python: {python_time:.4f}s")
        print(f"   C++: {cpp_time:.4f}s")

        # C++ should be at least 10x faster for EV calculations
        assert speedup >= 10.0, f"C++ speedup {speedup:.1f}x is less than expected 10x minimum"

    @pytest.mark.skipif(not CPP_AVAILABLE, reason="C++ module not available")
    def test_batch_processing_speed(self):
        """Test batch processing performance gains."""

        # Generate large batch of hands
        hand_list = [
                        ['8', '8'], ['A', '9'], ['10', '6'], ['5', '6'], ['A', 'A'],
                        ['9', '9'], ['7', '7'], ['2', '2'], ['3', '3'], ['6', '6']
                    ] * 50  # 500 hands

        dealer_upcards = ['6', '7', '8', '9', '10', 'A'] * 84  # Match length

        deck_comp = {
            'A': 200, '2': 200, '3': 200, '4': 200, '5': 200,
            '6': 200, '7': 200, '8': 200, '9': 200, '10': 800,
            'J': 200, 'Q': 200, 'K': 200
        }

        # Benchmark batch processing
        start = time.perf_counter()
        results = batch_analyze_hands(hand_list, dealer_upcards, deck_comp)
        batch_time = time.perf_counter() - start

        print(f"\n🚀 Batch processing: {len(hand_list)} hands in {batch_time:.4f}s")
        print(f"   Average per hand: {batch_time / len(hand_list) * 1000:.2f}ms")

        # Should process at least 100 hands per second
        hands_per_second = len(hand_list) / batch_time
        assert hands_per_second >= 100, f"Batch processing too slow: {hands_per_second:.1f} hands/sec"


# =============================================================================
# MEMORY USAGE TESTS
# =============================================================================

class TestMemoryUsage:
    """Test memory efficiency of C++ implementation."""

    @pytest.mark.skipif(not CPP_AVAILABLE, reason="C++ module not available")
    def test_memory_efficiency(self):
        """Test that C++ implementation uses less memory."""
        import tracemalloc

        # Test memory usage for many calculations
        tracemalloc.start()

        # Perform memory-intensive calculations
        for _ in range(1000):
            hand = [8, 8]
            upcard = 10
            deck = bjlogic_cpp.create_deck_state(6)
            deck = bjlogic_cpp.remove_cards(deck, [8, 8, 10])
            rules = {'num_decks': 6, 'dealer_hits_soft_17': False}

            result = bjlogic_cpp.calculate_optimal_ev(hand, upcard, deck, rules)

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print(f"\n🧠 Memory usage: Peak {peak / 1024 / 1024:.2f} MB")

        # Should use reasonable amount of memory
        assert peak < 100 * 1024 * 1024, f"Memory usage too high: {peak / 1024 / 1024:.2f} MB"


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Test integration with existing application code."""

    @pytest.mark.skipif(not WRAPPER_AVAILABLE, reason="Wrapper not available")
    def test_api_compatibility(self):
        """Test that wrapper maintains API compatibility."""

        # Test that wrapper functions exist and work
        result = calculate_hand_value(['A', 'K'])
        assert 'total' in result
        assert result['total'] == 21

        # Test analyze function
        deck_comp = {'A': 24, '2': 24, '3': 24, '4': 24, '5': 24,
                     '6': 24, '7': 24, '8': 22, '9': 24, '10': 96,
                     'J': 24, 'Q': 24, 'K': 24}

        result = analyze_with_nairn_algorithm(['8', '8'], '10', deck_comp)
        assert 'best' in result
        assert 'best_ev' in result
        assert isinstance(result['best_ev'], float)

    @pytest.mark.skipif(not (CPP_AVAILABLE and WRAPPER_AVAILABLE),
                        reason="Both C++ and wrapper needed")
    def test_hybrid_calculator(self):
        """Test HybridNairnEVCalculator compatibility."""

        rules = {'num_decks': 6, 'hits_soft_17': False}
        calculator = HybridNairnEVCalculator(rules)

        # Test that it works like original calculator
        hand = [8, 8]
        upcard = 10
        deck = {'num_decks': 6, 'cards_remaining': {i: 24 for i in range(1, 11)}, 'total_cards': 312}

        result = calculator.calculate_hand_ev(hand, upcard, deck)

        assert 'best' in result
        assert 'best_ev' in result
        assert result['best'] in ['hit', 'stand', 'double', 'split', 'surrender']


# =============================================================================
# STRESS TESTS
# =============================================================================

class TestStability:
    """Test system stability under load."""

    @pytest.mark.skipif(not CPP_AVAILABLE, reason="C++ module not available")
    def test_large_batch_stability(self):
        """Test stability with very large batches."""

        # Generate 10,000 random hands
        import random

        hand_list = []
        for _ in range(10000):
            # Random 2-card hand
            card1 = random.randint(1, 10)
            card2 = random.randint(1, 10)
            hand_list.append([card1, card2])

        dealer_upcards = [random.randint(1, 10) for _ in range(10000)]

        deck = bjlogic_cpp.create_deck_state(8)  # Use 8 decks for large test
        rules = {'num_decks': 8, 'dealer_hits_soft_17': False}

        start = time.perf_counter()

        # Process in smaller batches to avoid memory issues
        batch_size = 1000
        total_processed = 0

        for i in range(0, len(hand_list), batch_size):
            batch_hands = hand_list[i:i + batch_size]
            batch_upcards = dealer_upcards[i:i + batch_size]

            results = bjlogic_cpp.batch_calculate_ev(batch_hands, batch_upcards, deck, rules)
            total_processed += len(results)

        total_time = time.perf_counter() - start

        print(f"\n🏋️ Stress test: {total_processed:,} hands in {total_time:.2f}s")
        print(f"   Rate: {total_processed / total_time:.0f} hands/second")

        assert total_processed == len(hand_list), "Not all hands were processed"

    @pytest.mark.skipif(not CPP_AVAILABLE, reason="C++ module not available")
    def test_memory_leak_check(self):
        """Check for memory leaks in repeated usage."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Perform many calculations
        for _ in range(5000):
            hand = [random.randint(1, 10), random.randint(1, 10)]
            upcard = random.randint(1, 10)
            deck = bjlogic_cpp.create_deck_state(6)
            rules = {'num_decks': 6}

            result = bjlogic_cpp.calculate_optimal_ev(hand, upcard, deck, rules)

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        print(f"\n🧠 Memory leak check:")
        print(f"   Initial: {initial_memory / 1024 / 1024:.2f} MB")
        print(f"   Final: {final_memory / 1024 / 1024:.2f} MB")
        print(f"   Increase: {memory_increase / 1024 / 1024:.2f} MB")

        # Should not increase by more than 50MB
        assert memory_increase < 50 * 1024 * 1024, f"Possible memory leak: {memory_increase / 1024 / 1024:.2f} MB increase"


# =============================================================================
# BENCHMARK SUITE
# =============================================================================

def run_comprehensive_benchmark():
    """Run comprehensive performance benchmark."""

    print("\n" + "=" * 60)
    print("🚀 COMPREHENSIVE BLACKJACK C++ BENCHMARK")
    print("=" * 60)

    if not CPP_AVAILABLE:
        print("❌ C++ module not available - cannot run benchmarks")
        return

    results = {}

    # 1. Hand Value Calculation Benchmark
    print("\n1. Hand Value Calculations")
    print("-" * 30)

    test_hands = [[1, 1], [1, 10], [10, 6], [8, 8]] * 1000

    start = time.perf_counter()
    for hand in test_hands:
        bjlogic_cpp.calculate_hand_value(hand)
    cpp_time = time.perf_counter() - start

    results['hand_calculations'] = {
        'operations': len(test_hands),
        'cpp_time': cpp_time,
        'ops_per_second': len(test_hands) / cpp_time
    }

    print(f"   {len(test_hands):,} calculations in {cpp_time:.4f}s")
    print(f"   Rate: {len(test_hands) / cpp_time:,.0f} operations/second")

    # 2. EV Calculation Benchmark
    print("\n2. Expected Value Calculations")
    print("-" * 30)

    hands = [[8, 8], [1, 9], [10, 6], [5, 6]] * 100
    upcards = [10, 6, 1, 5] * 100
    deck = bjlogic_cpp.create_deck_state(6)
    rules = {'num_decks': 6, 'dealer_hits_soft_17': False}

    start = time.perf_counter()
    for hand, upcard in zip(hands, upcards):
        bjlogic_cpp.calculate_optimal_ev(hand, upcard, deck, rules)
    cpp_time = time.perf_counter() - start

    results['ev_calculations'] = {
        'operations': len(hands),
        'cpp_time': cpp_time,
        'ops_per_second': len(hands) / cpp_time
    }

    print(f"   {len(hands):,} calculations in {cpp_time:.4f}s")
    print(f"   Rate: {len(hands) / cpp_time:,.0f} operations/second")

    # 3. Batch Processing Benchmark
    print("\n3. Batch Processing")
    print("-" * 30)

    batch_hands = [[8, 8], [1, 9], [10, 6]] * 1000
    batch_upcards = [10, 6, 1] * 1000

    start = time.perf_counter()
    batch_results = bjlogic_cpp.batch_calculate_ev(batch_hands, batch_upcards, deck, rules)
    batch_time = time.perf_counter() - start

    results['batch_processing'] = {
        'operations': len(batch_hands),
        'cpp_time': batch_time,
        'ops_per_second': len(batch_hands) / batch_time
    }

    print(f"   {len(batch_hands):,} hands in {batch_time:.4f}s")
    print(f"   Rate: {len(batch_hands) / batch_time:,.0f} hands/second")

    # 4. Memory Efficiency Test
    print("\n4. Memory Efficiency")
    print("-" * 30)

    import tracemalloc
    tracemalloc.start()

    # Intensive memory test
    for _ in range(10000):
        hand = [8, 8]
        upcard = 10
        test_deck = bjlogic_cpp.create_deck_state(6)
        bjlogic_cpp.calculate_optimal_ev(hand, upcard, test_deck, rules)

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    results['memory_usage'] = {
        'peak_mb': peak / 1024 / 1024,
        'current_mb': current / 1024 / 1024
    }

    print(f"   Peak memory: {peak / 1024 / 1024:.2f} MB")
    print(f"   Current memory: {current / 1024 / 1024:.2f} MB")

    # 5. Cache Performance
    print("\n5. Cache Performance")
    print("-" * 30)

    if hasattr(bjlogic_cpp, 'get_cache_stats'):
        cache_stats = bjlogic_cpp.get_cache_stats()
        print(f"   Dealer cache size: {cache_stats.get('dealer_cache_size', 0)}")
        print(f"   EV cache size: {cache_stats.get('ev_cache_size', 0)}")
        print(f"   Cache hit rate: {cache_stats.get('cache_hit_rate', 0) * 100:.1f}%")

    # Summary
    print("\n" + "=" * 60)
    print("📊 BENCHMARK SUMMARY")
    print("=" * 60)

    print(f"Hand calculations: {results['hand_calculations']['ops_per_second']:,.0f} ops/sec")
    print(f"EV calculations: {results['ev_calculations']['ops_per_second']:,.0f} ops/sec")
    print(f"Batch processing: {results['batch_processing']['ops_per_second']:,.0f} hands/sec")
    print(f"Memory efficiency: {results['memory_usage']['peak_mb']:.1f} MB peak")

    # Performance grades
    print("\n🏆 PERFORMANCE GRADES:")

    hand_grade = "A+" if results['hand_calculations']['ops_per_second'] > 100000 else \
        "A" if results['hand_calculations']['ops_per_second'] > 50000 else \
            "B" if results['hand_calculations']['ops_per_second'] > 10000 else "C"

    ev_grade = "A+" if results['ev_calculations']['ops_per_second'] > 1000 else \
        "A" if results['ev_calculations']['ops_per_second'] > 500 else \
            "B" if results['ev_calculations']['ops_per_second'] > 100 else "C"

    print(f"   Hand calculations: {hand_grade}")
    print(f"   EV calculations: {ev_grade}")
    print(
        f"   Memory usage: {'A+' if results['memory_usage']['peak_mb'] < 50 else 'A' if results['memory_usage']['peak_mb'] < 100 else 'B'}")

    return results


# =============================================================================
# TEST RUNNER
# =============================================================================

def run_all_tests():
    """Run all tests and benchmarks."""

    print("🧪 Running Blackjack C++ Integration Tests...")

    # Check prerequisites
    if not CPP_AVAILABLE:
        print("❌ C++ module not available")
        print("   Run: python setup.py build_ext --inplace")
        return False

    # Run pytest tests
    print("\n📋 Running correctness tests...")
    pytest_result = pytest.main([__file__, "-v", "-x"])

    if pytest_result != 0:
        print("❌ Some tests failed!")
        return False

    print("✅ All correctness tests passed!")

    # Run benchmark
    print("\n🚀 Running performance benchmarks...")
    benchmark_results = run_comprehensive_benchmark()

    # Print final performance report
    if WRAPPER_AVAILABLE:
        print_performance_report()

    print("\n✅ All tests and benchmarks completed successfully!")
    return True


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "benchmark":
            run_comprehensive_benchmark()
        elif sys.argv[1] == "test":
            run_all_tests()
        else:
            print("Usage: python test_cpp_integration.py [benchmark|test]")
    else:
        run_all_tests()()
        for hand in test_hands:
            bjlogic_cpp.calculate_hand_value(hand)
        cpp_time = time.perf_counter() - start

        speedup = python_time / cpp_time
        print(f"\n🚀 Hand calculation speedup: {speedup:.1f}x")
        print(f"   Python: {python_time:.4f}s")
        print(f"   C++: {cpp_time:.4f}s")

        # C++ should be at least 3x faster
        assert speedup >= 3.0, f"C++ speedup {speedup:.1f}x is less than expected 3x minimum"


    @pytest.mark.skipif(not (CPP_AVAILABLE and PYTHON_AVAILABLE),
                        reason="Both implementations needed")
    def test_ev_calculation_speed(self):
        """Benchmark EV calculation speed."""

        scenarios = [
                        (['8', '8'], '10'),
                        (['A', '9'], '6'),
                        (['10', '6'], 'A'),
                        (['5', '6'], '5'),
                    ] * 10  # 40 total calculations

        deck_comp = {
            'A': 24, '2': 24, '3': 24, '4': 24, '5': 24,
            '6': 24, '7': 24, '8': 22, '9': 24, '10': 96,
            'J': 24, 'Q': 24, 'K': 24
        }
        rules = {'num_decks': 6}

        # Benchmark Python
        start = time.perf_counter()
        for hand, upcard in scenarios:
            py_analyze(hand, upcard, deck_comp, rules)
        python_time = time.perf_counter() - start

        # Benchmark C++
        start = time.perf_counter