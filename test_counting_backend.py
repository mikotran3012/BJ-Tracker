#!/usr/bin/env python3
"""Quick test of counting backend"""

import sys
import os

# Add the current directory to Python path so it can find the counting module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from counting import CountManager

# Test basic functionality
manager = CountManager(decks=8)
print(f"Initialized: {manager}")

# Add some cards
cards = ['A', 'K', '5', '6', '2']
for card in cards:
    manager.add_card(card)
    print(f"Added {card}")

# Get counts
cards_left = 400  # Example
aces_left = 30    # Example
counts = manager.get_counts(cards_left, aces_left, 8)

print("\nCurrent counts:")
for name, rc, tc in counts:
    print(f"{name}: RC={rc}, TC={tc}")

print("\nBackend test completed successfully!")