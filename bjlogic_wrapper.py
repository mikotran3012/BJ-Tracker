"""Python wrapper for C++ blackjack helpers."""
try:
    from bjlogic import calculate_hand_value as cpp_calculate_hand_value
    def calculate_hand_value(ranks):
        return cpp_calculate_hand_value(ranks)
except Exception:
    from rules_engine import BlackjackRules, Hand, Card
    def calculate_hand_value(ranks):
        rules = BlackjackRules()
        hand = Hand([Card(rank, '♠') for rank in ranks])
        return rules.calculate_hand_value(hand)