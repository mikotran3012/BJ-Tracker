import tkinter as tk
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from constants import RANKS, COLORS, normalize_rank_display
from .base_card_panel import BaseCardPanel
from .suit_selection import get_suit_selection


class DealerPanel(BaseCardPanel):
    """Dealer panel with hole card support and UPDATED scaled card display."""

    def __init__(self, parent, on_card, on_undo, hole_card_reveal=False, on_global_undo=None, undo_manager=None):
        print(f"DEALER_PANEL: Creating new DealerPanel instance in parent: {parent}")
        print(f"DEALER_PANEL: Parent has {len(parent.winfo_children())} existing children")

        super().__init__(parent, "DEALER", is_player=False, is_dealer=True,
                         on_card=on_card, on_undo=on_undo)
        self.hole_card = None
        self.hole_card_enabled = hole_card_reveal
        self.allow_reveal = hole_card_reveal
        self.mystery_hole = False
        self.on_global_undo = on_global_undo
        self.undo_manager = undo_manager

        # Add missing attributes
        self.current_deal_step = 0
        self.upcard_rank = None
        self.in_hole_phase = False

        self._build_dealer_ui()
        print("DEALER_PANEL: DealerPanel construction complete")

    def _build_dealer_ui(self):
        """Build dealer-specific UI with UPDATED card display sizing."""
        # Panel background
        panel_color = COLORS['fg_dealer']
        self.configure(bg=panel_color)

        # Header
        self.label = tk.Label(
            self, text="DEALER",
            font=('Segoe UI', 10, 'bold'),
            bg=panel_color, fg=COLORS['fg_white']
        )
        self.label.pack(pady=2)

        # Status display
        self.status_label = tk.Label(
            self, text="",
            font=('Segoe UI', 8),
            bg=panel_color, fg='#ff4444'
        )
        self.status_label.pack()

        # UPDATED: Card display area with vertical centering
        self.display_frame = tk.Frame(self, bg=panel_color)
        self.display_frame.pack(fill='both', expand=True, padx=4, pady=4)

        # UPDATED: Container for vertical centering of cards
        self.card_center_container = tk.Frame(self.display_frame, bg=panel_color)
        self.card_center_container.pack(expand=True, anchor='center')


        self._add_hand_display()

        # Input buttons + Score
        self._build_input_row_dealer()

    def _add_hand_display(self):
        """Add hand display for dealer with vertical centering."""
        hand_frame = tk.Frame(self.card_center_container, bg=COLORS['fg_dealer'])
        hand_frame.pack(expand=True, anchor='center')  # Centered within the container
        self.displays.append(hand_frame)
        self.card_widgets.append([])

    def create_card_widget(self, rank, suit, parent, size_scale=2.0):
        """UPDATED: Create dealer card widget with configurable scaling - DEFAULT 2x size."""
        # UPDATED: Base dimensions (doubled from original)
        base_width = 50
        base_height = 70

        # Apply scaling
        card_width = int(base_width * size_scale)
        card_height = int(base_height * size_scale)

        # Determine suit color and symbol
        suit_colors = {'♠': 'black', '♣': 'black', '♥': 'red', '♦': 'red'}
        suit_symbols = {'S': '♠', 'C': '♣', 'H': '♥', 'D': '♦'}

        suit_symbol = suit_symbols.get(suit, suit)
        suit_color = suit_colors.get(suit_symbol, 'black')

        # Display rank (handle 10 specially)
        display_rank = '10' if rank in ['T', '10'] else rank

        # Create main card frame
        card_frame = tk.Frame(parent,
                              bg='white',
                              relief=tk.SOLID,
                              bd=1,
                              width=card_width,
                              height=card_height)
        card_frame.pack_propagate(False)
        card_frame.pack(side=tk.LEFT, padx=2, pady=2)  # Slightly more spacing for larger cards

        # UPDATED: Scaled font sizes
        corner_font_size = max(6, int(8 * size_scale))
        center_font_size = max(12, int(16 * size_scale))
        if rank in ['J', 'Q', 'K']:
            center_font_size = max(14, int(18 * size_scale))
        elif rank == 'A':
            center_font_size = max(20, int(24 * size_scale))

        # Top-left corner: rank and suit
        top_left = tk.Label(card_frame,
                            text=f"{display_rank}\n{suit_symbol}",
                            font=('Arial', corner_font_size, 'bold'),
                            fg=suit_color,
                            bg='white',
                            justify=tk.LEFT)
        corner_x = max(2, int(3 * size_scale))
        corner_y = max(2, int(3 * size_scale))
        top_left.place(x=corner_x, y=corner_y)

        # Center: Large suit symbol or rank
        if rank in ['J', 'Q', 'K']:
            center_text = rank
        elif rank == 'A':
            center_text = suit_symbol
        else:
            center_text = suit_symbol

        center_label = tk.Label(card_frame,
                                text=center_text,
                                font=('Arial', center_font_size, 'bold'),
                                fg=suit_color,
                                bg='white')
        center_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Bottom-right corner: rank and suit (upside down)
        bottom_right = tk.Label(card_frame,
                                text=f"{suit_symbol}\n{display_rank}",
                                font=('Arial', corner_font_size, 'bold'),
                                fg=suit_color,
                                bg='white',
                                justify=tk.RIGHT)
        corner_offset = max(-2, int(-3 * size_scale))
        bottom_right.place(relx=1, rely=1, anchor=tk.SE, x=corner_offset, y=corner_offset)

        return card_frame

    def create_mystery_card_widget(self, parent, size_scale=2.0):
        """UPDATED: Create mystery card widget with scaling."""
        # UPDATED: Base dimensions (doubled from original)
        base_width = 50
        base_height = 70

        # Apply scaling
        card_width = int(base_width * size_scale)
        card_height = int(base_height * size_scale)

        card_frame = tk.Frame(parent, bg='#000080', bd=2, relief=tk.RAISED,
                              width=card_width, height=card_height)
        card_frame.pack_propagate(False)
        card_frame.pack(side=tk.LEFT, padx=2, pady=2)

        # UPDATED: Scaled font for mystery symbol
        mystery_font_size = max(20, int(24 * size_scale))
        tk.Label(card_frame, text='?', font=('Arial', mystery_font_size, 'bold'),
                 fg='white', bg='#000080').pack(expand=True)
        return card_frame

    def _build_input_row_dealer(self):
        """Build rank input buttons and score display - LEFT-ALIGNED with minimal spacing."""
        bottom_frame = tk.Frame(self, bg=COLORS['fg_dealer'])
        bottom_frame.pack(fill='x', pady=2)

        # Rank buttons - LEFT-ALIGNED with MINIMAL SPACING
        btn_row = tk.Frame(bottom_frame, bg=COLORS['fg_dealer'])
        btn_row.pack(side=tk.LEFT, anchor='w', padx=0)

        self.rank_btns = []
        for ri, r in enumerate(RANKS):
            display_rank = normalize_rank_display(r)
            b = tk.Button(
                btn_row, text=display_rank,
                width=1 if r != '10' else 2,
                height=1,
                font=('Segoe UI', 7),
                command=lambda rank=r: self.rank_clicked(rank)
            )
            b.grid(row=0, column=ri, padx=(0 if ri == 0 else 2, 0), pady=0, sticky='w')
            self.rank_btns.append(b)

        # Undo button - MINIMAL SPACING
        self.undo_btn = tk.Button(
            btn_row, text='U',
            width=1,
            height=1,
            font=('Segoe UI', 7, 'bold'),
            command=self.on_global_undo
        )
        self.undo_btn.grid(row=0, column=len(RANKS), padx=(2, 0), pady=0, sticky='w')

        # Score display - RIGHT-ALIGNED with more space
        self.score_label = tk.Label(
            bottom_frame, text="",
            font=('Segoe UI', 9, 'bold'),
            bg=COLORS['fg_dealer'], fg='#ffff00',
            width=12, anchor='center'
        )
        self.score_label.pack(side=tk.RIGHT, padx=5)

        # Dealer action buttons directly below rank buttons
        dealer_btn_row = tk.Frame(self, bg=COLORS['fg_dealer'])
        dealer_btn_row.pack(anchor='w', pady=(0, 2))

        self.mystery_btn = tk.Button(
            dealer_btn_row, text="Mystery (?)",
            width=8,
            height=1,
            font=('Segoe UI', 7),
            command=self.input_mystery_card
        )
        self.mystery_btn.pack(side=tk.LEFT, padx=2)

        self.reveal_btn = tk.Button(
            dealer_btn_row, text="Reveal Hole",
            width=8,
            height=1,
            font=('Segoe UI', 7),
            command=self.reveal_hole_card
        )
        if self.allow_reveal:
            self.reveal_btn.pack(side=tk.LEFT, padx=2)

    def set_play_mode(self):
        """Enable all controls when dealer is hitting during play phase."""
        print("DEALER: Setting play mode - enabling all controls")
        self.current_deal_step = 2
        for btn in self.rank_btns:
            btn.config(state=tk.NORMAL)
        self.mystery_btn.config(state=tk.NORMAL)
        self.reveal_btn.config(state=tk.NORMAL)
        self.undo_btn.config(state=tk.NORMAL)

    def set_dealer_turn(self, deal_step):
        """Configure controls during the initial dealing phase."""
        print(f"DEALER: Setting dealer turn for deal step {deal_step}")
        self.current_deal_step = deal_step

        if deal_step == 0:
            print("DEALER: Dealing upcard - enabling all rank buttons")
            for btn in self.rank_btns:
                btn.config(state=tk.NORMAL)
            self.mystery_btn.config(state=tk.DISABLED)
            self.reveal_btn.config(state=tk.DISABLED)
            self.undo_btn.config(state=tk.NORMAL)

        elif deal_step == 1:
            print("DEALER: Dealing hole card")
            upcard_is_ace = (self.upcard_rank == 'A')

            if upcard_is_ace:
                print("DEALER: Upcard is Ace - allowing insurance input")
                for btn in self.rank_btns:
                    btn.config(state=tk.NORMAL)
            else:
                print("DEALER: Upcard is not Ace - disabling rank buttons")
                for btn in self.rank_btns:
                    btn.config(state=tk.DISABLED)

            self.mystery_btn.config(state=tk.NORMAL)
            self.reveal_btn.config(state=tk.NORMAL)
            self.undo_btn.config(state=tk.NORMAL)

    def rank_clicked(self, rank):
        """DEALER: Handle rank click - check for hole card."""
        print(f"DEALER_RANK: {rank}")

        if self.in_hole_phase and not self.hole_card_enabled:
            print("DEALER_RANK: Ignored during hole card phase")
            return

        if self.current_deal_step == 0:
            self.upcard_rank = rank

            if (len(self.hands[0]) == 1 and
                    not self.hole_card and
                    not self.mystery_hole):
                print("DEALER_RANK: This is hole card input")
                self.choose_suit(rank, is_hole=True)
            else:
                print("DEALER_RANK: This is regular card")
                self.choose_suit(rank, is_hole=False)

    def choose_suit(self, rank, is_hole=False):
        """Show suit selection for dealer."""
        print(f"DEALER_SUIT: {rank} (hole={is_hole})")

        def on_suit_selected(suit):
            print(f"DEALER_SUIT_SELECTED: {rank}{suit}")
            self.input_card(rank, suit, is_hole)

        get_suit_selection(self, on_suit_selected)

    def input_card(self, rank, suit, is_hole=False):
        """DEALER: Input card with hole card support."""
        print(f"DEALER_INPUT: {rank}{suit} (hole={is_hole})")

        if self.undo_manager:
            self.undo_manager.record_action(
                "dealer", rank, suit,
                hand_idx=self.current_hand,
                is_hole=is_hole
            )

        if is_hole:
            self.hole_card = (rank, suit)
            self.mystery_hole = False
            print("DEALER_INPUT: Set hole card")
            self.on_card(rank, suit, is_hole=True)
        else:
            super().input_card(rank, suit, is_hole=False)

        self.update_display()

    def input_mystery_card(self):
        """Input mystery hole card."""
        if self.in_hole_phase and len(self.hands[0]) == 1:
            self.mystery_hole = True
            self.hole_card = None
            print("DEALER_MYSTERY: Added mystery hole card")
            self.on_card("?", "?", is_hole=True)
            self.update_display()

    def undo(self, hand_idx=None):
        """Undo last card."""
        print(f"UNDO: {self.label.cget('text')} undo clicked")

        if hand_idx is None:
            hand_idx = self.current_hand

        if self.is_dealer and (self.hole_card or self.mystery_hole):
            self.hole_card = None
            self.mystery_hole = False
            self.on_undo(is_hole=True)
            print("UNDO: Removed dealer hole card")
            card_removed = None
        elif self.hands[hand_idx]:
            last_card = self.hands[hand_idx].pop()
            self.is_busted = False
            self.on_undo(rank=last_card[0], is_hole=False)
            print(f"UNDO: Removed {last_card[0]}{last_card[1]}")
            card_removed = last_card
        else:
            print("UNDO: Nothing to undo")
            card_removed = None

        self.update_display()
        return card_removed

    def update_display(self):
        """UPDATED: Update dealer display with scaled cards and hole card logic."""
        # Clear existing card widgets
        for hand_widgets in self.card_widgets:
            for widget in hand_widgets:
                try:
                    widget.destroy()
                except:
                    pass

        self.card_widgets = []

        if not self.displays:
            return

        display_frame = self.displays[0]
        self.card_widgets.append([])

        # Clear display frame
        for widget in display_frame.winfo_children():
            widget.destroy()

        # UPDATED: Use 2x scale for dealer cards (always large)
        card_scale = 2.0

        # Show upcard (first card)
        if self.hands[0]:
            upcard = self.hands[0][0]
            card_widget = self.create_card_widget(upcard[0], upcard[1], display_frame, card_scale)
            self.card_widgets[0].append(card_widget)

        # Show hole card (second card)
        if self.mystery_hole:
            mystery_widget = self.create_mystery_card_widget(display_frame, card_scale)
            self.card_widgets[0].append(mystery_widget)
            start_idx = 2
        elif self.hole_card:
            hole_widget = self.create_card_widget(self.hole_card[0], self.hole_card[1], display_frame, card_scale)
            self.card_widgets[0].append(hole_widget)
            start_idx = 2
        elif len(self.hands[0]) > 1:
            mystery_widget = self.create_mystery_card_widget(display_frame, card_scale)
            self.card_widgets[0].append(mystery_widget)
            start_idx = 2
        else:
            start_idx = 1

        # Show any additional cards (hits)
        if len(self.hands[0]) > start_idx:
            for i in range(start_idx, len(self.hands[0])):
                card = self.hands[0][i]
                card_widget = self.create_card_widget(card[0], card[1], display_frame, card_scale)
                self.card_widgets[0].append(card_widget)

        # Update score and status
        self._update_score_display()
        self._update_status_display()

    def _update_score_display(self):
        """Update dealer score display."""
        if self.hole_card and not self.mystery_hole:
            temp_cards = self.hands[0] + [self.hole_card]
            score_text = self._calculate_full_score(temp_cards)
        elif len(self.hands[0]) >= 1:
            upcard = self.hands[0][0]
            value = self._get_card_value(upcard[0])
            score_text = f"Up: {value}"
        else:
            score_text = ""

        self.score_label.config(text=score_text)

    def _calculate_full_score(self, cards):
        """Calculate full dealer score for display."""
        total = 0
        aces = 0

        for rank, suit in cards:
            if rank in ['J', 'Q', 'K']:
                total += 10
            elif rank in ['T', '10']:
                total += 10
            elif rank == 'A':
                aces += 1
                total += 11
            else:
                total += int(rank)

        while total > 21 and aces > 0:
            total -= 10
            aces -= 1

        has_usable_ace = aces > 0

        if total > 21:
            return f"Bust {total}"
        elif has_usable_ace:
            return f"Soft {total}"
        else:
            return f"Hard {total}"

    def _get_card_value(self, rank):
        """Get single card value."""
        if rank in ['J', 'Q', 'K']:
            return 10
        elif rank in ['T', '10']:
            return 10
        elif rank == 'A':
            return 11
        else:
            return int(rank)

    def _update_status_display(self):
        """Update dealer status display."""
        if self.is_busted:
            self.status_label.config(text="BUST")
        elif self.is_done:
            self.status_label.config(text="STAND")
        else:
            self.status_label.config(text="")

    def reveal_hole_card(self):
        """Enable hole card input mode."""
        self.hole_card_enabled = True
        self.in_hole_phase = False
        self.mystery_hole = False
        print("DEALER_REVEAL: Enabled hole card input")

    def set_enabled(self, enabled, hole_phase=False):
        """Enable/disable dealer controls."""
        self.in_hole_phase = enabled and hole_phase
        state = tk.NORMAL if enabled else tk.DISABLED

        for btn in self.rank_btns:
            btn_state = tk.DISABLED if hole_phase else state
            btn.config(state=btn_state)

        self.undo_btn.config(state=state)
        self.mystery_btn.config(state=tk.NORMAL if hole_phase and enabled else state)
        if hasattr(self, 'reveal_btn'):
            self.reveal_btn.config(state=state if not hole_phase else tk.DISABLED)
        else:
            if self.current_deal_step == 0:
                self.set_dealer_turn(0)
            elif self.current_deal_step == 1:
                self.set_dealer_turn(1)
            else:
                self.set_play_mode()

    def reset(self):
        """Reset dealer panel."""
        super().reset()
        self.hole_card = None
        self.mystery_hole = False
        self.hole_card_enabled = False
        self.in_hole_phase = False
        self.current_deal_step = 0
        self.upcard_rank = None
        self.update_display()