#!/usr/bin/env python3
"""
Counting Systems Demo - Comprehensive test of the counting backend and UI.
Demonstrates RAPC and UAPC systems with live UI updates.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the project root to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from counting import CountManager
from ui.count_panel import CountPanel


class CountingDemo(tk.Tk):
    """Demo application showing the counting systems in action."""
    
    def __init__(self):
        super().__init__()
        self.title("Blackjack Counting Systems Demo")
        self.geometry("500x600")
        self.configure(bg='#1a1a1a')
        
        # Initialize counting system
        self.count_manager = CountManager(decks=8)
        
        # Game state for demo
        self.cards_left = 8 * 52  # Start with full shoe
        self.aces_left = 8 * 4    # Start with all aces
        
        self._build_demo_ui()
        self._update_displays()
    
    def _build_demo_ui(self):
        """Build the demo application UI."""
        # Title
        title_label = tk.Label(
            self,
            text="Counting Systems Demo",
            font=('Segoe UI', 16, 'bold'),
            bg='#1a1a1a',
            fg='#ffffff'
        )
        title_label.pack(pady=10)
        
        # Count panel (main feature)
        self.count_panel = CountPanel(self, self.count_manager)
        self.count_panel.pack(fill='x', padx=20, pady=10)
        
        # Shoe status
        self._build_shoe_status()
        
        # Card input section
        self._build_card_input()
        
        # Control buttons
        self._build_controls()
        
        # Demo buttons
        self._build_demo_buttons()
    
    def _build_shoe_status(self):
        """Build shoe status display."""
        status_frame = tk.LabelFrame(
            self,
            text="Shoe Status",
            font=('Segoe UI', 10, 'bold'),
            bg='#1a1a1a',
            fg='#ffffff',
            bd=2,
            relief=tk.RAISED
        )
        status_frame.pack(fill='x', padx=20, pady=5)
        
        info_frame = tk.Frame(status_frame, bg='#1a1a1a')
        info_frame.pack(fill='x', padx=10, pady=5)
        
        # Cards left
        tk.Label(
            info_frame,
            text="Cards Left:",
            font=('Segoe UI', 9),
            bg='#1a1a1a',
            fg='#cccccc'
        ).grid(row=0, column=0, sticky='w', padx=(0, 10))
        
        self.cards_left_label = tk.Label(
            info_frame,
            text=str(self.cards_left),
            font=('Segoe UI', 9, 'bold'),
            bg='#1a1a1a',
            fg='#00ff00'
        )
        self.cards_left_label.grid(row=0, column=1, sticky='w')
        
        # Aces left
        tk.Label(
            info_frame,
            text="Aces Left:",
            font=('Segoe UI', 9),
            bg='#1a1a1a',
            fg='#cccccc'
        ).grid(row=0, column=2, sticky='w', padx=(20, 10))
        
        self.aces_left_label = tk.Label(
            info_frame,
            text=str(self.aces_left),
            font=('Segoe UI', 9, 'bold'),
            bg='#1a1a1a',
            fg='#ffff00'
        )
        self.aces_left_label.grid(row=0, column=3, sticky='w')
        
        # Penetration
        tk.Label(
            info_frame,
            text="Penetration:",
            font=('Segoe UI', 9),
            bg='#1a1a1a',
            fg='#cccccc'
        ).grid(row=1, column=0, sticky='w', padx=(0, 10))
        
        self.penetration_label = tk.Label(
            info_frame,
            text="0.0%",
            font=('Segoe UI', 9, 'bold'),
            bg='#1a1a1a',
            fg='#ff8800'
        )
        self.penetration_label.grid(row=1, column=1, sticky='w')
    
    def _build_card_input(self):
        """Build card input section."""
        input_frame = tk.LabelFrame(
            self,
            text="Card Input",
            font=('Segoe UI', 10, 'bold'),
            bg='#1a1a1a',
            fg='#ffffff',
            bd=2,
            relief=tk.RAISED
        )
        input_frame.pack(fill='x', padx=20, pady=5)
        
        # Card rank buttons
        ranks_frame = tk.Frame(input_frame, bg='#1a1a1a')
        ranks_frame.pack(pady=10)
        
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        self.rank_buttons = {}
        
        for i, rank in enumerate(ranks):
            btn = tk.Button(
                ranks_frame,
                text=rank,
                width=3,
                font=('Segoe UI', 9, 'bold'),
                command=lambda r=rank: self._add_card(r),
                bg='#444444',
                fg='#ffffff',
                activebackground='#666666',
                activeforeground='#ffffff'
            )
            btn.grid(row=0, column=i, padx=2, pady=2)
            self.rank_buttons[rank] = btn
    
    def _build_controls(self):
        """Build control buttons."""
        controls_frame = tk.Frame(self, bg='#1a1a1a')
        controls_frame.pack(pady=10)
        
        # Undo button
        undo_btn = tk.Button(
            controls_frame,
            text="UNDO",
            font=('Segoe UI', 10, 'bold'),
            command=self._undo_card,
            bg='#ff6666',
            fg='#ffffff',
            activebackground='#ff8888',
            activeforeground='#ffffff',
            width=10
        )
        undo_btn.pack(side='left', padx=5)
        
        # Reset button
        reset_btn = tk.Button(
            controls_frame,
            text="RESET",
            font=('Segoe UI', 10, 'bold'),
            command=self._reset_count,
            bg='#6666ff',
            fg='#ffffff',
            activebackground='#8888ff',
            activeforeground='#ffffff',
            width=10
        )
        reset_btn.pack(side='left', padx=5)
    
    def _build_demo_buttons(self):
        """Build demo scenario buttons."""
        demo_frame = tk.LabelFrame(
            self,
            text="Demo Scenarios",
            font=('Segoe UI', 10, 'bold'),
            bg='#1a1a1a',
            fg='#ffffff',
            bd=2,
            relief=tk.RAISED
        )
        demo_frame.pack(fill='x', padx=20, pady=5)
        
        buttons_frame = tk.Frame(demo_frame, bg='#1a1a1a')
        buttons_frame.pack(pady=10)
        
        # High count scenario
        high_count_btn = tk.Button(
            buttons_frame,
            text="High Count\nScenario",
            font=('Segoe UI', 9),
            command=self._demo_high_count,
            bg='#00aa00',
            fg='#ffffff',
            activebackground='#00cc00',
            activeforeground='#ffffff',
            width=12,
            height=2
        )
        high_count_btn.pack(side='left', padx=5)
        
        # Low count scenario
        low_count_btn = tk.Button(
            buttons_frame,
            text="Low Count\nScenario",
            font=('Segoe UI', 9),
            command=self._demo_low_count,
            bg='#aa0000',
            fg='#ffffff',
            activebackground='#cc0000',
            activeforeground='#ffffff',
            width=12,
            height=2
        )
        low_count_btn.pack(side='left', padx=5)
        
        # Balanced scenario
        balanced_btn = tk.Button(
            buttons_frame,
            text="Balanced\nScenario",
            font=('Segoe UI', 9),
            command=self._demo_balanced,
            bg='#aa6600',
            fg='#ffffff',
            activebackground='#cc8800',
            activeforeground='#ffffff',
            width=12,
            height=2
        )
        balanced_btn.pack(side='left', padx=5)
    
    def _add_card(self, rank: str):
        """Add a card to the count."""
        self.count_manager.add_card(rank)
        
        # Update shoe tracking
        self.cards_left -= 1
        if rank == 'A':
            self.aces_left -= 1
        
        self._update_displays()
    
    def _undo_card(self):
        """Undo the last card (simplified - just removes an ace for demo)."""
        if self.cards_left < 8 * 52:  # Only if cards have been dealt
            # For demo purposes, we'll undo an ace
            self.count_manager.remove_card('A')
            self.cards_left += 1
            self.aces_left = min(self.aces_left + 1, 8 * 4)
            self._update_displays()
    
    def _reset_count(self):
        """Reset all counts and shoe state."""
        self.count_manager.reset()
        self.cards_left = 8 * 52
        self.aces_left = 8 * 4
        self._update_displays()
    
    def _update_displays(self):
        """Update all displays with current values."""
        # Update count panel
        self.count_panel.update_panel(self.cards_left, self.aces_left, 8)
        
        # Update shoe status
        self.cards_left_label.config(text=str(self.cards_left))
        self.aces_left_label.config(text=str(self.aces_left))
        
        # Calculate and display penetration
        total_cards = 8 * 52
        cards_dealt = total_cards - self.cards_left
        penetration = (cards_dealt / total_cards) * 100
        self.penetration_label.config(text=f"{penetration:.1f}%")
    
    def _demo_high_count(self):
        """Demo scenario with high positive count."""
        self._reset_count()
        
        # Deal lots of low cards to create positive count
        low_cards = ['2', '3', '4', '5', '6'] * 10  # 50 low cards
        for card in low_cards:
            self._add_card(card)
        
        print("High count scenario: Dealt 50 low cards")
        self._show_scenario_info("High Count", "Favorable for player - increase bets!")
    
    def _demo_low_count(self):
        """Demo scenario with low negative count."""
        self._reset_count()
        
        # Deal lots of high cards to create negative count
        high_cards = ['10', 'J', 'Q', 'K', 'A'] * 8  # 40 high cards
        for card in high_cards:
            self._add_card(card)
        
        print("Low count scenario: Dealt 40 high cards")
        self._show_scenario_info("Low Count", "Unfavorable for player - minimum bets!")
    
    def _demo_balanced(self):
        """Demo scenario with balanced count."""
        self._reset_count()
        
        # Deal balanced mix of cards
        balanced_cards = ['2', '7', '8', '9', '10', 'A'] * 5  # 30 mixed cards
        for card in balanced_cards:
            self._add_card(card)
        
        print("Balanced scenario: Dealt balanced mix")
        self._show_scenario_info("Balanced Count", "Near neutral - normal betting")
    
    def _show_scenario_info(self, title: str, description: str):
        """Show scenario information in a popup."""
        info_window = tk.Toplevel(self)
        info_window.title(title)
        info_window.geometry("300x150")
        info_window.configure(bg='#1a1a1a')
        info_window.resizable(False, False)
        
        # Center the window
        info_window.transient(self)
        info_window.grab_set()
        
        tk.Label(
            info_window,
            text=title,
            font=('Segoe UI', 14, 'bold'),
            bg='#1a1a1a',
            fg='#ffffff'
        ).pack(pady=10)
        
        tk.Label(
            info_window,
            text=description,
            font=('Segoe UI', 10),
            bg='#1a1a1a',
            fg='#cccccc',
            wraplength=250
        ).pack(pady=10)
        
        tk.Button(
            info_window,
            text="OK",
            command=info_window.destroy,
            bg='#444444',
            fg='#ffffff',
            font=('Segoe UI', 10)
        ).pack(pady=10)


def run_console_demo():
    """Run a console-based demo of the counting systems."""
    print("=== Blackjack Counting Systems Console Demo ===\n")
    
    # Initialize manager
    manager = CountManager(decks=6)
    print(f"Initialized: {manager}")
    print(f"Active systems: {[sys.name for sys in manager.get_all_systems()]}\n")
    
    # Simulate some cards
    print("Simulating card sequence: A, K, Q, 5, 6, 2, 3, 4...")
    cards = ['A', 'K', 'Q', '5', '6', '2', '3', '4']
    
    cards_left = 6 * 52
    aces_left = 6 * 4
    
    for card in cards:
        manager.add_card(card)
        cards_left -= 1
        if card == 'A':
            aces_left -= 1
        
        counts = manager.get_counts(cards_left, aces_left, 6)
        print(f"After {card}: ", end="")
        for name, rc, tc in counts:
            print(f"{name}(RC:{rc}, TC:{tc:.2f}) ", end="")
        print()
    
    print("\n=== Detailed System Information ===")
    detailed = manager.get_detailed_counts(cards_left, aces_left, 6)
    for system_info in detailed:
        print(f"\n{system_info['name']} System:")
        print(f"  Running Count: {system_info['running_count']}")
        print(f"  True Count: {system_info['true_count']}")
        print(f"  Cards Seen: {system_info['cards_seen']}")
        
        if 'ace_adjustment' in system_info:
            ace_info = system_info['ace_adjustment']
            print(f"  Ace Adjustment Details:")
            print(f"    Aces Seen: {ace_info['aces_seen']}")
            print(f"    Adjustment: {ace_info['ace_adjustment']}")
            print(f"    Adjusted RC: {ace_info['adjusted_rc']}")
    
    print("\n=== Simulation Test ===")
    sim_cards = ['10', 'J', 'Q', 'K'] * 5  # 20 high cards
    simulated = manager.simulate_cards(sim_cards)
    print("After simulating 20 high cards:")
    for name, rc, tc in simulated:
        print(f"  {name}: RC={rc}, TC≈{tc}")
    
    print("\nDemo complete!")


if __name__ == "__main__":
    print("Blackjack Counting Systems Demo")
    print("Choose demo mode:")
    print("1. GUI Demo (recommended)")
    print("2. Console Demo")
    print("3. Both")
    
    try:
        choice = input("Enter choice (1-3): ").strip()
        
        if choice in ['2', '3']:
            run_console_demo()
            print("\n" + "="*50 + "\n")
        
        if choice in ['1', '3']:
            print("Starting GUI Demo...")
            app = CountingDemo()
            app.mainloop()
        
        if choice not in ['1', '2', '3']:
            print("Invalid choice. Running GUI demo by default.")
            app = CountingDemo()
            app.mainloop()
            
    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")
    except Exception as e:
        print(f"Error running demo: {e}")
        import traceback
        traceback.print_exc()