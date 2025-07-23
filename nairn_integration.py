# nairn_integration.py
"""
Integration module to connect Nairn's EV algorithms with BlackjackTrackerApp.
Handles format conversion and provides UI integration.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Any
import threading
import time

# Import the Nairn calculator
try:
    from nairn_ev_calculator import (
        BlackjackTrackerNairnIntegration,
        analyze_with_nairn_algorithm,
        DDAny, DDNone, DD10OR11,
        ACE, TEN
    )

    NAIRN_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Nairn EV calculator not available: {e}")
    NAIRN_AVAILABLE = False


class NairnEVPanel:
    """
    UI Panel for displaying Nairn EV analysis results.
    Integrates with your existing BlackjackTrackerApp.
    """

    def __init__(self, parent_frame, app_instance):
        self.parent = parent_frame
        self.app = app_instance
        self.panel = None
        self.labels = {}
        self.nairn_integration = None
        self.last_analysis = None
        self.analysis_thread = None

        # Initialize Nairn integration if available
        if NAIRN_AVAILABLE:
            self._init_nairn_integration()

    def _init_nairn_integration(self):
        """Initialize the Nairn integration with app rules."""
        try:
            # Extract rules from your app (adjust these based on your app's structure)
            rules_config = {
                'num_decks': getattr(self.app, 'num_decks', 6),
                'hits_soft_17': getattr(self.app, 'hits_soft_17', False),
                'resplitting': getattr(self.app, 'resplitting_allowed', False),
                'dd_after_split': DDAny,  # Adjust based on your app's settings
                'resplit_aces': getattr(self.app, 'resplit_aces', False),
                'blackjack_payout': getattr(self.app, 'blackjack_payout', 1.5)
            }

            self.nairn_integration = BlackjackTrackerNairnIntegration(rules_config)
            print("✓ Nairn EV calculator initialized successfully")

        except Exception as e:
            print(f"Failed to initialize Nairn integration: {e}")
            self.nairn_integration = None

    def create_panel(self):
        """Create the Nairn EV analysis panel UI."""
        if not NAIRN_AVAILABLE:
            # Create disabled panel
            self.panel = tk.Frame(self.parent, bg='#2d2d2d', relief=tk.RAISED, bd=2)
            disabled_label = tk.Label(
                self.panel,
                text="NAIRN EV CALCULATOR\n(Not Available)",
                font=('Segoe UI', 10, 'bold'),
                bg='#2d2d2d',
                fg='#666666'
            )
            disabled_label.pack(pady=10)
            return self.panel

        # Create main panel frame
        self.panel = tk.Frame(self.parent, bg='#1e1e1e', relief=tk.RAISED, bd=2)

        # Header with Nairn branding
        header_frame = tk.Frame(self.panel, bg='#1e1e1e')
        header_frame.pack(fill='x', padx=5, pady=5)

        header_label = tk.Label(
            header_frame,
            text="⚡ NAIRN EV ANALYSIS",
            font=('Segoe UI', 11, 'bold'),
            bg='#1e1e1e',
            fg='#00ff88'
        )
        header_label.pack(side='left')

        # Status indicator
        self.labels['status'] = tk.Label(
            header_frame,
            text="●",
            font=('Segoe UI', 12),
            bg='#1e1e1e',
            fg='#ff4444'  # Red initially
        )
        self.labels['status'].pack(side='right')

        # Main recommendation display
        self.labels['recommendation'] = tk.Label(
            self.panel,
            text="Ready for analysis...",
            font=('Segoe UI', 10, 'bold'),
            bg='#1e1e1e',
            fg='#ffff00',
            wraplength=200,
            justify='center'
        )
        self.labels['recommendation'].pack(pady=5)

        # Action breakdown table
        breakdown_frame = tk.Frame(self.panel, bg='#1e1e1e')
        breakdown_frame.pack(fill='x', padx=5, pady=2)

        # Table headers
        headers = ['Action', 'EV', 'Rating']
        for i, header in enumerate(headers):
            tk.Label(
                breakdown_frame,
                text=header,
                font=('Segoe UI', 8, 'bold'),
                bg='#1e1e1e',
                fg='#cccccc',
                width=8
            ).grid(row=0, column=i, sticky='ew')

        # Action rows
        self.action_rows = []
        for i in range(6):  # Max 6 actions (hit, stand, double, split, surrender, insurance)
            row_widgets = []
            for j in range(3):  # Action, EV, Rating
                label = tk.Label(
                    breakdown_frame,
                    text="",
                    font=('Segoe UI', 7),
                    bg='#1e1e1e',
                    fg='#aaaaaa',
                    width=8
                )
                label.grid(row=i + 1, column=j, sticky='ew')
                row_widgets.append(label)
            self.action_rows.append(row_widgets)

        # Analysis details
        details_frame = tk.Frame(self.panel, bg='#1e1e1e')
        details_frame.pack(fill='x', padx=5, pady=2)

        self.labels['details'] = tk.Label(
            details_frame,
            text="",
            font=('Segoe UI', 7),
            bg='#1e1e1e',
            fg='#888888',
            wraplength=200,
            justify='left'
        )
        self.labels['details'].pack()

        # Control buttons
        button_frame = tk.Frame(self.panel, bg='#1e1e1e')
        button_frame.pack(fill='x', padx=5, pady=5)

        # Auto-update toggle
        self.auto_update = tk.BooleanVar(value=True)
        auto_check = tk.Checkbutton(
            button_frame,
            text="Auto",
            variable=self.auto_update,
            font=('Segoe UI', 7),
            bg='#1e1e1e',
            fg='#cccccc',
            selectcolor='#2d2d2d',
            activebackground='#1e1e1e',
            activeforeground='#cccccc'
        )
        auto_check.pack(side='left')

        # Manual refresh button
        refresh_btn = tk.Button(
            button_frame,
            text="Refresh",
            font=('Segoe UI', 7),
            command=self.manual_refresh,
            bg='#4CAF50',
            fg='white',
            relief='flat',
            width=6
        )
        refresh_btn.pack(side='right')

        # Exact split button (for pairs)
        self.exact_split_btn = tk.Button(
            button_frame,
            text="Exact Split",
            font=('Segoe UI', 7),
            command=self.show_exact_split,
            bg='#FF9800',
            fg='white',
            relief='flat',
            width=8,
            state='disabled'
        )
        self.exact_split_btn.pack(side='right', padx=2)

        return self.panel

    def update_analysis(self, force_update=False):
        """Update the panel with new analysis results."""
        if not self.nairn_integration:
            return

        if not self.auto_update.get() and not force_update:
            return

        # Run analysis in background thread to avoid UI blocking
        if self.analysis_thread and self.analysis_thread.is_alive():
            return  # Already analyzing

        self.analysis_thread = threading.Thread(target=self._background_analysis)
        self.analysis_thread.daemon = True
        self.analysis_thread.start()

    def _background_analysis(self):
        """Run Nairn analysis in background thread."""
        try:
            # Update status to analyzing
            self.panel.after(0, lambda: self._update_status("analyzing"))

            # Get analysis from Nairn integration
            analysis = self.nairn_integration.analyze_current_situation(self.app)

            # Update UI in main thread
            self.panel.after(0, lambda: self._update_ui_with_analysis(analysis))

        except Exception as e:
            print(f"Error in Nairn analysis: {e}")
            self.panel.after(0, lambda: self._update_status("error"))

    def _update_ui_with_analysis(self, analysis):
        """Update UI with analysis results (called from main thread)."""
        if not analysis:
            self._update_status("no_data")
            self.labels['recommendation'].config(text="No data available")
            self._clear_action_rows()
            return

        self.last_analysis = analysis
        self._update_status("success")

        # Update main recommendation
        recommendation = self.nairn_integration.get_recommendation_text(analysis)
        self.labels['recommendation'].config(text=recommendation)

        # Update action breakdown
        self._update_action_breakdown(analysis)

        # Update details
        self._update_details(analysis)

        # Enable exact split button for pairs
        if 'split' in analysis and analysis['split'] > float('-inf'):
            self.exact_split_btn.config(state='normal')
        else:
            self.exact_split_btn.config(state='disabled')

    def _update_status(self, status):
        """Update status indicator."""
        status_colors = {
            "success": "#00ff88",  # Green
            "analyzing": "#ffaa00",  # Orange
            "error": "#ff4444",  # Red
            "no_data": "#666666"  # Gray
        }

        if status in status_colors:
            self.labels['status'].config(fg=status_colors[status])

    def _update_action_breakdown(self, analysis):
        """Update the action breakdown table."""
        # Sort actions by EV (descending)
        actions = []
        action_names = {
            'hit': 'Hit',
            'stand': 'Stand',
            'double': 'Double',
            'split': 'Split',
            'surrender': 'Surrender'
        }

        best_ev = analysis.get('best_ev', 0)

        for action, ev in analysis.items():
            if action in action_names and ev != float('-inf'):
                name = action_names[action]

                # Determine rating
                if action == analysis.get('best'):
                    rating = "OPTIMAL"
                    color = '#00ff88'
                elif ev > best_ev - 0.001:
                    rating = "Excellent"
                    color = '#88ff88'
                elif ev > best_ev - 0.01:
                    rating = "Good"
                    color = '#ffff88'
                elif ev > best_ev - 0.05:
                    rating = "Fair"
                    color = '#ffaa88'
                else:
                    rating = "Poor"
                    color = '#ff8888'

                actions.append((name, ev, rating, color))

        # Sort by EV
        actions.sort(key=lambda x: x[1], reverse=True)

        # Update display
        for i, (action_label, ev_label, rating_label) in enumerate(self.action_rows):
            if i < len(actions):
                name, ev, rating, color = actions[i]
                action_label.config(text=name, fg='#cccccc')
                ev_label.config(text=f"{ev:+.4f}", fg='#cccccc')
                rating_label.config(text=rating, fg=color)
            else:
                # Clear unused rows
                action_label.config(text="", fg='#aaaaaa')
                ev_label.config(text="", fg='#aaaaaa')
                rating_label.config(text="", fg='#aaaaaa')

    def _update_details(self, analysis):
        """Update analysis details."""
        try:
            # Get current hand info from your app
            player_cards = self._get_current_player_cards()
            dealer_upcard = self._get_current_dealer_upcard()

            if player_cards and dealer_upcard:
                hand_str = " ".join(player_cards)
                details_text = f"Hand: {hand_str} vs {dealer_upcard}\nNairn Exact Algorithm"

                # Add composition info if available
                if hasattr(self.app, 'game_state') and hasattr(self.app.game_state, 'comp_panel'):
                    details_text += f"\nComposition-dependent"

                self.labels['details'].config(text=details_text)
            else:
                self.labels['details'].config(text="Nairn Algorithm Ready")

        except Exception as e:
            self.labels['details'].config(text=f"Analysis ready")

    def _clear_action_rows(self):
        """Clear all action row displays."""
        for action_label, ev_label, rating_label in self.action_rows:
            action_label.config(text="", fg='#aaaaaa')
            ev_label.config(text="", fg='#aaaaaa')
            rating_label.config(text="", fg='#aaaaaa')

    def manual_refresh(self):
        """Force a manual refresh of the analysis."""
        self.update_analysis(force_update=True)

    def show_exact_split(self):
        """Show exact splitting analysis using Nairn's breakthrough algorithm."""
        if not self.last_analysis or 'split' not in self.last_analysis:
            return

        # Get split card
        try:
            player_cards = self._get_current_player_cards()
            if len(player_cards) == 2 and player_cards[0] == player_cards[1]:
                split_card = player_cards[0]
                self._show_exact_split_window(split_card)
        except Exception as e:
            print(f"Error showing exact split: {e}")

    def _show_exact_split_window(self, split_card):
        """Show detailed exact splitting analysis in popup window."""
        if not self.nairn_integration:
            return

        # Create popup window
        popup = tk.Toplevel(self.panel)
        popup.title(f"Exact Split Analysis: {split_card},{split_card}")
        popup.geometry("400x300")
        popup.configure(bg='#1e1e1e')
        popup.resizable(False, False)

        # Header
        header = tk.Label(
            popup,
            text=f"🔥 NAIRN EXACT SPLITTING\n{split_card},{split_card}",
            font=('Segoe UI', 12, 'bold'),
            bg='#1e1e1e',
            fg='#ff6600'
        )
        header.pack(pady=10)

        # Loading message
        loading_label = tk.Label(
            popup,
            text="Calculating exact probabilities...\n(This may take a few seconds)",
            font=('Segoe UI', 10),
            bg='#1e1e1e',
            fg='#cccccc'
        )
        loading_label.pack(pady=20)

        # Calculate in background
        def calculate_exact_split():
            try:
                deck_comp = self.nairn_integration._get_current_deck_composition(self.app)
                exact_results = self.nairn_integration.get_exact_split_analysis(split_card, deck_comp)

                # Update UI
                popup.after(0, lambda: self._update_exact_split_display(popup, loading_label, exact_results))

            except Exception as e:
                popup.after(0, lambda: loading_label.config(text=f"Error: {e}", fg='#ff4444'))

        thread = threading.Thread(target=calculate_exact_split)
        thread.daemon = True
        thread.start()

    def _update_exact_split_display(self, popup, loading_label, results):
        """Update exact split display with results."""
        loading_label.destroy()

        # Results frame
        results_frame = tk.Frame(popup, bg='#1e1e1e')
        results_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Headers
        tk.Label(results_frame, text="Doubling Rule", font=('Segoe UI', 9, 'bold'),
                 bg='#1e1e1e', fg='#cccccc').grid(row=0, column=0, sticky='w', padx=5)
        tk.Label(results_frame, text="Expected Value", font=('Segoe UI', 9, 'bold'),
                 bg='#1e1e1e', fg='#cccccc').grid(row=0, column=1, sticky='w', padx=5)

        # Results
        rule_names = {
            'no_double': 'No Doubling',
            'double_any': 'Double Any Cards',
            'double_10_11': 'Double 10&11 Only'
        }

        row = 1
        for rule, ev in results.items():
            rule_name = rule_names.get(rule, rule)

            tk.Label(results_frame, text=rule_name, font=('Segoe UI', 9),
                     bg='#1e1e1e', fg='#cccccc').grid(row=row, column=0, sticky='w', padx=5, pady=2)

            # Color code EV
            color = '#00ff88' if ev > 0 else '#ff6666' if ev < -0.1 else '#ffaa44'
            tk.Label(results_frame, text=f"{ev:+.6f}", font=('Segoe UI', 9, 'bold'),
                     bg='#1e1e1e', fg=color).grid(row=row, column=1, sticky='w', padx=5, pady=2)
            row += 1

        # Footer
        footer = tk.Label(
            popup,
            text="Calculated using Nairn's exact algorithm\n(Reduced from 11,000 years to seconds)",
            font=('Segoe UI', 7),
            bg='#1e1e1e',
            fg='#888888'
        )
        footer.pack(pady=10)

        # Close button
        close_btn = tk.Button(
            popup,
            text="Close",
            command=popup.destroy,
            bg='#666666',
            fg='white',
            relief='flat'
        )
        close_btn.pack(pady=5)

    def _get_current_player_cards(self):
        """Extract current player cards from app state."""
        try:
            if hasattr(self.app, 'game_state') and hasattr(self.app.game_state, 'player_panel'):
                if self.app.game_state.player_panel.hands:
                    return [card[0] for card in self.app.game_state.player_panel.hands[0]]
        except:
            pass
        return []

    def _get_current_dealer_upcard(self):
        """Extract current dealer upcard from app state."""
        try:
            if hasattr(self.app, 'game_state') and hasattr(self.app.game_state, 'dealer_panel'):
                if self.app.game_state.dealer_panel.hands[0]:
                    return self.app.game_state.dealer_panel.hands[0][0][0]
        except:
            pass
        return None


# Event handler for automatic updates
class NairnUpdateHandler:
    """Handles automatic updating of Nairn analysis when game state changes."""

    def __init__(self, nairn_panel):
        self.nairn_panel = nairn_panel
        self.last_state_hash = None

    def check_for_updates(self):
        """Check if game state has changed and update if needed."""
        try:
            current_hash = self._get_state_hash()
            if current_hash != self.last_state_hash:
                self.last_state_hash = current_hash
                self.nairn_panel.update_analysis()
        except Exception as e:
            pass  # Silently handle errors

    def _get_state_hash(self):
        """Generate a hash of current game state for change detection."""
        try:
            app = self.nairn_panel.app

            # Collect relevant state information
            state_parts = []

            # Player cards
            if hasattr(app, 'game_state') and hasattr(app.game_state, 'player_panel'):
                if app.game_state.player_panel.hands:
                    cards = [card[0] for card in app.game_state.player_panel.hands[0]]
                    state_parts.append(str(sorted(cards)))

            # Dealer upcard
            if hasattr(app, 'game_state') and hasattr(app.game_state, 'dealer_panel'):
                if app.game_state.dealer_panel.hands[0]:
                    upcard = app.game_state.dealer_panel.hands[0][0][0]
                    state_parts.append(str(upcard))

            # Deck composition (if tracked)
            if hasattr(app, 'game_state') and hasattr(app.game_state, 'comp_panel'):
                if app.game_state.comp_panel:
                    comp_str = str(sorted(app.game_state.comp_panel.comp.items()))
                    state_parts.append(comp_str)

            return hash("|".join(state_parts))

        except Exception:
            return 0


def integrate_nairn_with_app(app_instance, parent_frame):
    """
    Main integration function to add Nairn EV analysis to your app.

    Args:
        app_instance: Your BlackjackTrackerApp instance
        parent_frame: The tkinter frame where you want to add the Nairn panel

    Returns:
        NairnEVPanel instance for further customization
    """
    # Create the Nairn panel
    nairn_panel = NairnEVPanel(parent_frame, app_instance)
    panel_widget = nairn_panel.create_panel()

    # Pack the panel
    panel_widget.pack(fill='x', padx=5, pady=5)

    # Set up automatic updates
    update_handler = NairnUpdateHandler(nairn_panel)

    # Schedule periodic updates (every 500ms)
    def schedule_updates():
        update_handler.check_for_updates()
        parent_frame.after(500, schedule_updates)

    parent_frame.after(500, schedule_updates)

    print("✓ Nairn EV Analysis panel integrated successfully")
    return nairn_panel