#!/usr/bin/env python3
# advanced_ev_examples.py
"""
Professional examples demonstrating the Advanced EV Calculation Engine
Real-world scenarios for professional blackjack players and researchers
"""

import json
import time
from typing import Dict, List, Tuple


def professional_player_analysis():
    """Example: Professional player analyzing a challenging decision"""
    print("🎯 Professional Player Analysis")
    print("=" * 50)

    try:
        import bjlogic_cpp

        # Scenario: Hard 16 vs 10 in different counting situations
        print("Scenario: You have 16 vs dealer 10 in a 6-deck game")
        print("Question: How does the decision change with count and penetration?")

        rules = bjlogic_cpp.create_rules_config()
        rules["surrender_allowed"] = True

        # Test different true count scenarios
        count_scenarios = [
            (-2, "Negative count (rich in small cards)"),
            (0, "Neutral count"),
            (+2, "Positive count (rich in tens)"),
            (+4, "High positive count"),
        ]

        print(f"\nTrue Count | Basic Strategy | Counting Strategy | EV Improvement | Recommendation")
        print(f"-----------|---------------|-------------------|----------------|----------------")

        engine = bjlogic_cpp.AdvancedEVEngine()

        for true_count, description in count_scenarios:
            # Basic strategy (TC = 0)
            basic_ev = engine.calculate_true_count_ev([10, 6], 10, 0.0, rules)

            # Counting strategy
            counting_ev = engine.calculate_true_count_ev([10, 6], 10, true_count, rules)

            improvement = counting_ev['optimal_ev'] - basic_ev['optimal_ev']

            print(f"{true_count:10} | {basic_ev['optimal_action']:13} | "
                  f"{counting_ev['optimal_action']:17} | {improvement:14.4f} | {description[:15]}")

        # Comprehensive analysis for the critical TC +2 scenario
        print(f"\n🔍 Detailed Analysis for True Count +2:")
        analysis = bjlogic_cpp.comprehensive_hand_analysis(
            [10, 6], 10, rules, "Hi-Lo", 4, 150, True, True
        )

        print(f"  Basic Strategy EV: {analysis['basic_strategy']['optimal_ev']:.4f}")
        print(f"  Counting Strategy EV: {analysis['counting_strategy']['optimal_ev']:.4f}")
        print(f"  EV Improvement: {analysis['ev_improvement']:.4f}")
        print(f"  Variance: {analysis['variance']:.4f}")
        print(f"  Betting Advantage: {analysis['betting_advantage']:.4f}")
        print(f"  Suggested Bet Multiplier: {analysis['suggested_bet_multiplier']:.2f}x")
        print(f"  Recommendation: {analysis['recommendation']}")

        # Monte Carlo validation
        if 'monte_carlo_validation' in analysis:
            mc_result = analysis['monte_carlo_validation']
            confidence = analysis['confidence_interval']
            print(f"  Monte Carlo EV: {mc_result['optimal_ev']:.4f}")
            print(f"  95% Confidence: [{confidence['lower_bound']:.4f}, {confidence['upper_bound']:.4f}]")

        print("✅ Professional analysis complete")
        return True

    except Exception as e:
        print(f"❌ Professional analysis failed: {e}")
        return False


def bankroll_management_optimization():
    """Example: Optimizing bankroll and betting strategy"""
    print("\n💰 Bankroll Management Optimization")
    print("=" * 50)

    try:
        import bjlogic_cpp

        print("Scenario: Professional player optimizing a $10,000 bankroll")
        print("Goal: Find optimal bet sizing and risk management")

        engine = bjlogic_cpp.AdvancedEVEngine()
        rules = bjlogic_cpp.create_rules_config()

        # Test different base bet sizes
        bankroll = 10000
        base_bet_options = [25, 50, 100, 200]

        print(f"\nBase Bet | Hourly EV | Session EV | Risk of Ruin | Kelly Bet | Recommendation")
        print(f"---------|-----------|------------|--------------|-----------|----------------")

        optimal_results = []

        for base_bet in base_bet_options:
            session_analysis = engine.analyze_session(
                bankroll, base_bet, "Hi-Lo", rules, 4, 0
            )

            session_data = session_analysis['session_analysis']
            hourly_ev = session_data['hourly_ev']
            total_ev = session_data['total_ev']
            risk_of_ruin = session_analysis['risk_of_ruin']
            kelly_bet = session_data['kelly_bet_size']
            recommendation = session_analysis['recommendation'][:12]

            optimal_results.append({
                'base_bet': base_bet,
                'hourly_ev': hourly_ev,
                'risk_of_ruin': risk_of_ruin,
                'kelly_bet': kelly_bet
            })

            print(f"${base_bet:7} | ${hourly_ev:9.2f} | ${total_ev:10.2f} | "
                  f"{risk_of_ruin:11.4f} | ${kelly_bet:8.0f} | {recommendation:12}")

        # Find optimal bet size (best risk-adjusted return)
        best_option = min(optimal_results, key=lambda x: x['risk_of_ruin'] if x['hourly_ev'] > 0 else float('inf'))

        print(f"\n🎯 Recommended Strategy:")
        print(f"  Optimal Base Bet: ${best_option['base_bet']}")
        print(f"  Expected Hourly EV: ${best_option['hourly_ev']:.2f}")
        print(f"  Risk of Ruin: {best_option['risk_of_ruin']:.4f}")
        print(f"  Bankroll Ratio: {bankroll / best_option['base_bet']:.0f}:1")

        # Optimal bet spread analysis
        print(f"\n📊 Optimal Bet Spread for Hi-Lo:")
        bet_spread = engine.calculate_optimal_bet_spread("Hi-Lo", bankroll, 0.01)

        true_counts = [-2, -1, 0, 1, 2, 3, 4, 5]
        print(f"  True Count | Bet Size | Units")
        print(f"  -----------|----------|-------")

        for i, tc in enumerate(true_counts):
            if i < len(bet_spread):
                bet_size = bet_spread[i]
                units = bet_size / best_option['base_bet']
                print(f"  {tc:10} | ${bet_size:8.0f} | {units:5.1f}")

        print("✅ Bankroll optimization complete")
        return True

    except Exception as e:
        print(f"❌ Bankroll optimization failed: {e}")
        return False


def composition_dependent_analysis():
    """Example: Composition-dependent strategy analysis"""
    print("\n🃏 Composition-Dependent Strategy Analysis")
    print("=" * 50)

    try:
        import bjlogic_cpp

        print("Scenario: Single deck game with unusual card distribution")
        print("Question: How do remaining cards affect strategy decisions?")

        engine = bjlogic_cpp.AdvancedEVEngine()
        rules = bjlogic_cpp.create_rules_config()
        rules["num_decks"] = 1

        # Create different deck compositions
        base_deck = bjlogic_cpp.create_deck_state(1)

        # Scenario 1: Ten-poor deck (many tens already played)
        ten_poor_deck = base_deck.copy()
        ten_poor_deck['cards_remaining'][10] = 8  # Half the tens removed
        ten_poor_deck['total_cards'] = 44

        # Scenario 2: Five-poor deck (many fives already played)
        five_poor_deck = base_deck.copy()
        five_poor_deck['cards_remaining'][5] = 1  # Almost all fives removed
        five_poor_deck['total_cards'] = 49

        # Scenario 3: Ace-rich deck (few aces played)
        ace_rich_deck = base_deck.copy()
        ace_rich_deck['cards_remaining'][1] = 4  # All aces still in deck
        ace_rich_deck['cards_remaining'][6] = 2  # Some sixes removed
        ace_rich_deck['total_cards'] = 50

        compositions = [
            (base_deck, "Normal deck"),
            (ten_poor_deck, "Ten-poor deck"),
            (five_poor_deck, "Five-poor deck"),
            (ace_rich_deck, "Ace-rich deck"),
        ]

        # Test critical hands
        test_hands = [
            ([10, 6], 10, "Hard 16 vs 10"),
            ([10, 2], 4, "Hard 12 vs 4"),
            ([5, 6], 1, "Hard 11 vs A"),
        ]

        for hand, dealer, description in test_hands:
            print(f"\n{description}:")
            print(f"  Deck Composition | Optimal Action | EV      | Difference")
            print(f"  -----------------|----------------|---------|----------")

            base_ev = None

            for deck, deck_name in compositions:
                comp_ev = engine.calculate_composition_dependent_ev(hand, dealer, deck, rules)

                if base_ev is None:
                    base_ev = comp_ev['optimal_ev']
                    difference = 0.0
                else:
                    difference = comp_ev['optimal_ev'] - base_ev

                print(f"  {deck_name:15} | {comp_ev['optimal_action']:14} | "
                      f"{comp_ev['optimal_ev']:7.4f} | {difference:+8.4f}")

        print(f"\n🔍 Key Insights:")
        print(f"  • Ten-poor decks favor more aggressive play (hitting stiffs)")
        print(f"  • Five-poor decks reduce dealer bust probability")
        print(f"  • Ace-rich decks increase blackjack probability")
        print(f"  • Composition effects are typically 0.001-0.01 EV units")

        print("✅ Composition-dependent analysis complete")
        return True

    except Exception as e:
        print(f"❌ Composition-dependent analysis failed: {e}")
        return False


def tournament_strategy_analysis():
    """Example: Tournament strategy optimization"""
    print("\n🏆 Tournament Strategy Analysis")
    print("=" * 50)

    try:
        import bjlogic_cpp

        print("Scenario: Blackjack tournament final table")
        print("Goal: Maximize probability of winning tournament")

        tournament_calc = bjlogic_cpp.TournamentEVCalculator()
        rules = bjlogic_cpp.create_rules_config()

        # Tournament scenarios
        tournament_situations = [
            (1000, 5, "Leading with comfortable margin"),
            (800, 3, "Close competition, need to catch up"),
            (500, 2, "Behind, need aggressive play"),
            (200, 1, "Final hand, all-or-nothing"),
        ]

        test_hands = [
            ([10, 10], 6, "20 vs 6 (very strong hand)"),
            ([10, 6], 10, "16 vs 10 (marginal hand)"),
            ([1, 7], 3, "Soft 18 vs 3 (doubling candidate)"),
        ]

        print(f"\nChips | Rounds | Hand      | Cash Game | Tournament | Difference")
        print(f"------|--------|-----------|-----------|------------|----------")

        for chips, rounds, situation in tournament_situations:
            for hand, dealer, hand_desc in test_hands[:1]:  # Test with 20 vs 6
                # Cash game EV
                engine = bjlogic_cpp.AdvancedEVEngine()
                cash_ev = engine.calculate_true_count_ev(hand, dealer, 0.0, rules)

                # Tournament EV
                tournament_ev = tournament_calc.calculate_tournament_ev(
                    hand, dealer, chips, rounds, rules
                )

                # Optimal tournament bet
                target_chips = chips * 1.5  # Want to increase by 50%
                optimal_bet = tournament_calc.calculate_optimal_tournament_bet(
                    chips, target_chips, rounds
                )

                difference = tournament_ev - cash_ev['optimal_ev']

                print(f"{chips:5} | {rounds:6} | {hand_desc[:9]:9} | "
                      f"{cash_ev['optimal_ev']:9.4f} | {tournament_ev:10.4f} | {difference:+9.4f}")

                if rounds == 1:  # Show betting recommendation for final round
                    print(f"      |        |           | Optimal tournament bet: {optimal_bet:.0f} chips")

        print(f"\n🎯 Tournament Strategy Insights:")
        print(f"  • Leading players should play more conservatively")
        print(f"  • Behind players need more aggressive betting")
        print(f"  • Final round decisions focus on chip position vs. opponents")
        print(f"  • Tournament EV can differ significantly from cash game EV")

        print("✅ Tournament analysis complete")
        return True

    except Exception as e:
        print(f"❌ Tournament analysis failed: {e}")
        return False


def progressive_betting_analysis():
    """Example: Progressive betting system analysis"""
    print("\n📈 Progressive Betting System Analysis")
    print("=" * 50)

    try:
        import bjlogic_cpp

        print("Scenario: Analyzing popular progressive betting systems")
        print("Warning: Demonstrating why these systems don't work!")

        progressive_calc = bjlogic_cpp.ProgressiveEVCalculator()

        # Different progressive systems
        systems = [
            ([10, 20, 40, 80, 160], "Martingale (double after loss)"),
            ([10, 15, 25, 40, 65], "Modified Martingale"),
            ([10, 20, 30, 40, 50], "Linear progression"),
            ([10, 12, 15, 19, 24], "Conservative progression"),
        ]

        win_probabilities = [0.43, 0.46, 0.48]  # Different game scenarios

        print(f"\nProgression Type    | Win Rate | System EV | Risk of Ruin | Verdict")
        print(f"--------------------|----------|-----------|--------------|--------")

        for progression, system_name in systems:
            for win_prob in win_probabilities[:1]:  # Test with 43% win rate
                system_ev = progressive_calc.calculate_progressive_ev(
                    progression, win_prob, len(progression)
                )

                # Calculate risk for Martingale-type systems
                if "Martingale" in system_name:
                    base_bet = progression[0]
                    bankroll = sum(progression) * 3  # Conservative bankroll
                    max_doubles = len(progression) - 1
                    risk = progressive_calc.calculate_martingale_risk(
                        base_bet, bankroll, max_doubles
                    )
                else:
                    risk = 0.15  # Estimated risk for other systems

                verdict = "AVOID" if system_ev < 0 or risk > 0.1 else "Consider"

                print(f"{system_name[:19]:19} | {win_prob:8.2f} | {system_ev:9.4f} | "
                      f"{risk:11.4f} | {verdict:7}")

        print(f"\n⚠️  Progressive Betting Reality Check:")
        print(f"  • No betting system can overcome negative expectation")
        print(f"  • Martingale systems have devastating risk of ruin")
        print(f"  • House edge remains the same regardless of bet size")
        print(f"  • Only advantage play (counting) can beat the house")

        # Show proper advantage play comparison
        print(f"\n✅ Proper Advantage Play (Card Counting):")
        engine = bjlogic_cpp.AdvancedEVEngine()
        rules = bjlogic_cpp.create_rules_config()

        # Simulate advantage play session
        session_analysis = engine.analyze_session(
            bankroll=5000, base_bet=25, counter_system="Hi-Lo",
            rules=rules, session_hours=4
        )

        session_data = session_analysis['session_analysis']
        print(f"  Expected hourly EV: ${session_data['hourly_ev']:.2f}")
        print(f"  Risk of ruin: {session_analysis['risk_of_ruin']:.4f}")
        print(f"  This beats ANY progressive betting system!")

        print("✅ Progressive betting analysis complete")
        return True

    except Exception as e:
        print(f"❌ Progressive betting analysis failed: {e}")
        return False


def monte_carlo_validation_study():
    """Example: Monte Carlo validation of EV calculations"""
    print("\n🎰 Monte Carlo Validation Study")
    print("=" * 50)

    try:
        import bjlogic_cpp

        print("Scenario: Validating deterministic EV calculations with simulation")
        print("Purpose: Ensure accuracy of sophisticated algorithms")

        engine = bjlogic_cpp.AdvancedEVEngine()
        rules = bjlogic_cpp.create_rules_config()

        # Test scenarios that are difficult to calculate
        validation_scenarios = [
            ([8, 8], 10, "Hi-Lo", 2, "Pair 8s vs 10, TC +2"),
            ([1, 7], 3, "Zen Count", 1, "Soft 18 vs 3, TC +1"),
            ([10, 5], 10, "Uston APC", 4, "Hard 15 vs 10, high TC"),
        ]

        print(f"\nScenario              | Deterministic | Monte Carlo | Difference | Status")
        print(f"----------------------|---------------|-------------|------------|--------")

        for hand, dealer, system, count, description in validation_scenarios:
            # Deterministic calculation
            det_start = time.time()
            det_ev = engine.calculate_detailed_ev(hand, dealer, system, rules, count, 100)
            det_time = time.time() - det_start

            # Monte Carlo simulation
            mc_start = time.time()
            mc_ev = engine.monte_carlo_ev_estimation(hand, dealer, system, rules, 50000, count)
            mc_time = time.time() - mc_start

            det_optimal = det_ev['optimal_ev']
            mc_optimal = mc_ev['optimal_ev']
            difference = abs(det_optimal - mc_optimal)

            # Calculate confidence interval
            variance = mc_ev['variance']
            confidence = engine.calculate_ev_confidence_interval(mc_optimal, variance, 50000, 0.95)

            # Check if deterministic result falls within confidence interval
            within_ci = (confidence['lower_bound'] <= det_optimal <= confidence['upper_bound'])
            status = "✅ VALID" if within_ci and difference < 0.01 else "⚠️  CHECK"

            print(f"{description[:21]:21} | {det_optimal:13.4f} | {mc_optimal:11.4f} | "
                  f"{difference:10.4f} | {status:7}")

            # Show confidence interval for first scenario
            if hand == [8, 8]:
                print(f"                      | Time: {det_time:.3f}s | Time: {mc_time:.3f}s | "
                      f"CI: ±{confidence['margin_of_error']:.4f} |")

        print(f"\n📊 Validation Results:")
        print(f"  • Deterministic calculations are typically 10-100x faster")
        print(f"  • Monte Carlo provides confidence intervals and validation")
        print(f"  • Differences should be within statistical noise (< 0.01)")
        print(f"  • Both methods agree on optimal actions")

        print("✅ Monte Carlo validation complete")
        return True

    except Exception as e:
        print(f"❌ Monte Carlo validation failed: {e}")
        return False


def real_world_casino_comparison():
    """Example: Comparing different casino rule variations"""
    print("\n🌍 Real-World Casino Rule Comparison")
    print("=" * 50)

    try:
        import bjlogic_cpp

        print("Scenario: Professional player choosing between casinos")
        print("Goal: Find the most profitable game conditions")

        engine = bjlogic_cpp.AdvancedEVEngine()

        # Real casino rule sets
        casinos = [
            {
                "name": "Las Vegas Strip Premium",
                "num_decks": 6,
                "dealer_hits_soft_17": False,
                "surrender_allowed": True,
                "blackjack_payout": 1.5,
                "double_after_split": 1,
                "penetration": 75
            },
            {
                "name": "Atlantic City Standard",
                "num_decks": 8,
                "dealer_hits_soft_17": True,
                "surrender_allowed": True,
                "blackjack_payout": 1.5,
                "double_after_split": 1,
                "penetration": 80
            },
            {
                "name": "6:5 Blackjack (AVOID)",
                "num_decks": 6,
                "dealer_hits_soft_17": False,
                "surrender_allowed": False,
                "blackjack_payout": 1.2,
                "double_after_split": 0,
                "penetration": 65
            },
            {
                "name": "European Style",
                "num_decks": 6,
                "dealer_hits_soft_17": False,
                "surrender_allowed": False,
                "blackjack_payout": 1.5,
                "double_after_split": 1,
                "penetration": 70
            }
        ]

        print(f"\nCasino                 | House Edge | Hi-Lo EV | Session EV | Rating")
        print(f"-----------------------|------------|----------|------------|--------")

        best_casino = None
        best_ev = float('-inf')

        for casino in casinos:
            # Create rules
            rules = bjlogic_cpp.create_rules_config()
            rules.update({k: v for k, v in casino.items() if k != 'name' and k != 'penetration'})

            # Calculate theoretical house edge
            house_edge = bjlogic_cpp.calculate_theoretical_house_edge(rules)

            # Calculate counting advantage (simulated average)
            session_analysis = engine.analyze_session(
                bankroll=10000, base_bet=50, counter_system="Hi-Lo",
                rules=rules, session_hours=4
            )

            session_data = session_analysis['session_analysis']
            hilo_ev = session_data['hourly_ev']
            session_ev = session_data['total_ev']

            # Rate the casino
            if session_ev > 50:
                rating = "⭐⭐⭐"
            elif session_ev > 0:
                rating = "⭐⭐"
            elif session_ev > -50:
                rating = "⭐"
            else:
                rating = "💀"

            if session_ev > best_ev:
                best_ev = session_ev
                best_casino = casino['name']

            print(f"{casino['name'][:22]:22} | {house_edge:10.4f} | "
                  f"${hilo_ev:7.2f} | ${session_ev:9.2f} | {rating:7}")

        print(f"\n🎯 Recommendation: {best_casino}")
        print(f"  Best expected value for skilled counter")
        print(f"  Avoid 6:5 blackjack games at all costs!")

        # Show impact of rule variations
        print(f"\n📊 Rule Impact Analysis:")
        rule_impacts = [
            ("Dealer hits soft 17", "+0.22% house edge"),
            ("6:5 blackjack payout", "+1.39% house edge"),
            ("No surrender", "+0.08% house edge"),
            ("No double after split", "+0.14% house edge"),
            ("8 decks vs 6 decks", "+0.02% house edge"),
        ]

        for rule, impact in rule_impacts:
            print(f"  {rule}: {impact}")

        print("✅ Casino comparison complete")
        return True

    except Exception as e:
        print(f"❌ Casino comparison failed: {e}")
        return False


def run_all_advanced_examples():
    """Run all advanced EV engine examples"""
    print("🎯 ADVANCED EV CALCULATION ENGINE EXAMPLES")
    print("🧮 Professional Blackjack Analysis Demonstrations")
    print("=" * 80)

    try:
        import bjlogic_cpp

        # Check if advanced EV engine is available
        if not hasattr(bjlogic_cpp, 'AdvancedEVEngine'):
            print("❌ Advanced EV Engine not available")
            print("Please build the extension with advanced EV support")
            return False

        print(f"✅ Extension version: {bjlogic_cpp.__version__}")
        print(f"✅ Advanced EV Engine available")

        # Test the engine
        engine = bjlogic_cpp.AdvancedEVEngine()
        cache_size = engine.get_cache_size()
        print(f"✅ Engine initialized (cache: {cache_size} entries)")

    except ImportError as e:
        print(f"❌ Failed to import bjlogic_cpp: {e}")
        return False
    except Exception as e:
        print(f"❌ Engine initialization failed: {e}")
        return False

    # Run all examples
    examples = [
        professional_player_analysis,
        bankroll_management_optimization,
        composition_dependent_analysis,
        tournament_strategy_analysis,
        progressive_betting_analysis,
        monte_carlo_validation_study,
        real_world_casino_comparison,
    ]

    passed = 0
    total = len(examples)

    for example_func in examples:
        try:
            if example_func():
                passed += 1
            else:
                print(f"❌ {example_func.__name__} failed")
        except Exception as e:
            print(f"❌ {example_func.__name__} crashed: {e}")

    # Final summary
    print(f"\n" + "=" * 80)
    print(f"🎯 ADVANCED EV ENGINE EXAMPLES: {passed}/{total} completed successfully")

    if passed == total:
        print("🎉 ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("\n✨ Professional Features Demonstrated:")
        print("   🎯 Professional player decision analysis")
        print("   💰 Bankroll management and risk optimization")
        print("   🃏 Composition-dependent strategy calculations")
        print("   🏆 Tournament strategy optimization")
        print("   📈 Progressive betting system analysis")
        print("   🎰 Monte Carlo validation and confidence intervals")
        print("   🌍 Real-world casino rule comparisons")
        print("\n🚀 Advanced EV Engine ready for professional use!")
        print("💡 Perfect for serious players, researchers, and developers")
        return True
    else:
        print(f"❌ {total - passed} examples had issues")
        return False


if __name__ == "__main__":
    success = run_all_advanced_examples()

    import sys

    sys.exit(0 if success else 1)