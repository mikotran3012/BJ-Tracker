import tkinter as tk
from tkinter import ttk

# ---- Constants ----
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
SUITS = ['♠', '♥', '♦', '♣']
SUIT_KEYS = {'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣'}
SEATS = ['P7', 'P6', 'P5', 'P4', 'P3', 'P2', 'P1']  # Left to right; rightmost is P1
DEFAULT_DECKS = 8


def total_cards(decks): return decks * 52


# ---- Seat Selection Dialog ----
class SeatSelectDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Select Your Seat")
        self.selected = tk.StringVar(value=SEATS[0])
        self.resizable(False, False)
        self.configure(bg="white")
        label = tk.Label(self, text="Choose your seat (rightmost = P1):", font=("Segoe UI", 11), bg="white")
        label.pack(pady=(14, 2))
        radio_row = tk.Frame(self, bg="white")
        radio_row.pack(pady=(2, 8), padx=14)
        for seat in SEATS:  # Left to right
            rb = tk.Radiobutton(radio_row, text=seat, variable=self.selected, value=seat, bg="white")
            rb.pack(side=tk.LEFT, padx=7)
        ok_btn = ttk.Button(self, text="OK", command=self.on_ok)
        ok_btn.pack(pady=(0, 8))
        self.bind("<Return>", lambda e: self.on_ok())
        self.grab_set()
        self.transient(parent)
        self.wait_window(self)

    def on_ok(self):
        self.destroy()


# ---- Card Composition Panel ----
class CompPanel(tk.Frame):
    def __init__(self, parent, on_decks_change):
        super().__init__(parent, bg='white', bd=1, relief=tk.GROOVE)
        self.decks = DEFAULT_DECKS
        self.on_decks_change = on_decks_change
        self.comp = {r: 0 for r in RANKS}
        self._build_panel()
        self.update_display()

    def _build_panel(self):
        # Shoe info
        shoe = tk.Frame(self, bg='white')
        shoe.grid(row=0, column=0, rowspan=3, sticky='nsw', padx=2)
        tk.Label(shoe, text='Decks', font=('Segoe UI', 9, 'bold'), bg='white').pack()
        self.deck_var = tk.IntVar(value=self.decks)
        dspin = tk.Spinbox(shoe, from_=1, to=8, width=2, textvariable=self.deck_var, font=('Segoe UI', 12),
                           command=self.set_decks, justify='center')
        dspin.pack()
        tk.Label(shoe, text='Cards', font=('Segoe UI', 9, 'bold'), bg='white').pack(pady=(4, 0))
        self.cards_left_label = tk.Label(shoe, text="", font=('Segoe UI', 12, 'bold'), fg='#1565c0', bg='white')
        self.cards_left_label.pack()
        # Penetration bar
        tk.Label(shoe, text='Pen', font=('Segoe UI', 9), bg='white').pack(pady=(4, 0))
        self.pen_bar = tk.Canvas(shoe, width=48, height=14, bg='#e0e0e0', bd=0, highlightthickness=0)
        self.pen_bar.pack()
        self.pen_label = tk.Label(shoe, text="0%", font=('Segoe UI', 9), bg='white')
        self.pen_label.pack()
        # Ranks
        for ci, r in enumerate(RANKS):
            tk.Label(self, text=r, font=('Segoe UI', 10, 'bold'), bg='white').grid(row=0, column=ci + 1, padx=2)
        tk.Label(self, text='Comp', font=('Segoe UI', 9), bg='white').grid(row=1, column=0, sticky='e')
        self.comp_labels = {}
        for ci, r in enumerate(RANKS):
            lbl = tk.Label(self, text='0', font=('Segoe UI', 11), width=3, fg='#1976d2', bg='#cfd8dc', bd=1,
                           relief=tk.SUNKEN)
            lbl.grid(row=1, column=ci + 1, padx=1, pady=1)
            self.comp_labels[r] = lbl
        tk.Label(self, text='Rem', font=('Segoe UI', 9), bg='white').grid(row=2, column=0, sticky='e')
        self.rem_labels = {}
        for ci, r in enumerate(RANKS):
            lbl = tk.Label(self, text='0', font=('Segoe UI', 11), width=3, fg='black', bg='#222', bd=1,
                           relief=tk.SUNKEN)
            lbl.grid(row=2, column=ci + 1, padx=1, pady=(0, 2))
            self.rem_labels[r] = lbl

    def set_decks(self):
        self.decks = self.deck_var.get()
        self.reset()
        self.on_decks_change()

    def reset(self):
        self.comp = {r: 0 for r in RANKS}
        self.update_display()

    def log_card(self, rank):
        self.comp[rank] += 1
        self.update_display()

    def undo_card(self, rank):
        if self.comp[rank] > 0:
            self.comp[rank] -= 1
            self.update_display()

    def cards_left(self):
        return sum(self.decks * 4 - self.comp[r] for r in RANKS)

    def penetration(self):
        seen = sum(self.comp.values())
        total = self.decks * 52
        pct = (seen / total) * 100 if total > 0 else 0
        return pct, seen, total

    def update_display(self):
        d = self.decks
        for r in RANKS:
            self.comp_labels[r].config(text=str(self.comp[r]))
            rem = d * 4 - self.comp[r]
            self.rem_labels[r].config(text=str(rem))
        cards_rem = self.cards_left()
        self.cards_left_label.config(text=str(cards_rem))
        pct, seen, total = self.penetration()
        self.pen_bar.delete("all")
        width = int((pct / 100) * 48)
        self.pen_bar.create_rectangle(0, 0, width, 14, fill="#1976d2")
        self.pen_label.config(text=f"{pct:.1f}%")


# ---- Shared Card Entry Panel ----
class SharedInputPanel(tk.Frame):
    def __init__(self, parent, on_card, on_undo):
        super().__init__(parent, bg='#2a3047')
        self.on_card = on_card
        self.on_undo = on_undo
        self._build_panel()

    def _build_panel(self):
        self.rank_btns = []
        for ri, r in enumerate(RANKS):
            b = tk.Button(self, text=r, width=2, font=('Segoe UI', 11),
                          command=lambda rank=r: self.rank_clicked(rank))
            b.grid(row=0, column=ri, padx=1)
            self.rank_btns.append(b)
        self.undo_btn = tk.Button(self, text='U', width=2, font=('Segoe UI', 11, 'bold'), command=self.undo)
        self.undo_btn.grid(row=0, column=len(RANKS), padx=3)

    def rank_clicked(self, rank):
        suit_win = tk.Toplevel(self)
        suit_win.title("Suit")
        suit_win.geometry("+600+340")

        def pick_suit(suit):
            suit_win.destroy()
            self.on_card(rank, suit)

        for i, suit in enumerate(SUITS):
            btn = tk.Button(suit_win, text=suit, font=('Segoe UI', 16, 'bold'), width=3,
                            fg='#ff4d4d' if suit == '♥' else '#40e0d0' if suit == '♦' else '#90ee90' if suit == '♣' else 'white',
                            command=lambda s=suit: pick_suit(s))
            btn.grid(row=0, column=i, padx=6, pady=8)
        suit_win.grab_set()
        suit_win.transient(self)
        suit_win.wait_window()

    def undo(self):
        self.on_undo()

    def set_enabled(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        for btn in self.rank_btns:
            btn.config(state=state)
        self.undo_btn.config(state=state)


# ---- Per-seat display (just the hand, no buttons) ----
class SeatHandPanel(tk.Frame):
    def __init__(self, parent, seat, is_player, is_your_seat):
        super().__init__(parent, bg='#222')
        self.seat = seat
        self.is_player = is_player
        self.is_your_seat = is_your_seat
        self.cards = []
        self.display = tk.Label(self, text="", font=('Consolas', 15, 'bold'),
                                bg='#858585' if is_your_seat else ('#26734d' if is_player else '#2b354d'),
                                fg='white', anchor='w', width=10, height=2, bd=2, relief=tk.SUNKEN)
        self.display.pack(fill='x', expand=True, padx=3, pady=(3, 1))

    def add_card(self, rank, suit):
        self.cards.append((rank, suit))
        self.update_display()

    def undo(self):
        if self.cards:
            self.cards.pop()
            self.update_display()

    def reset(self):
        self.cards = []
        self.update_display()

    def update_display(self):
        disp = ""
        for r, s in self.cards:
            disp += f"{r}{s} "
        self.display.config(text=disp.strip())

    def highlight(self, active=True):
        if self.is_your_seat:
            self.display.config(bg='#858585')
        elif active:
            self.display.config(bg='#ffae42')
        else:
            self.display.config(bg='#2b354d')


# ---- Player and Dealer Panels ----
class PlayerOrDealerPanel(tk.Frame):
    def __init__(self, parent, label_text, is_player, is_dealer, on_card, on_undo, hole_card_reveal=False):
        super().__init__(parent, bg='#222')
        self.is_player = is_player
        self.is_dealer = is_dealer
        self.on_card = on_card
        self.on_undo = on_undo
        self.cards = []
        self.hole_card = None
        self.hole_card_enabled = hole_card_reveal
        self._build(label_text)

    def _build(self, label_text):
        self.label = tk.Label(self, text=label_text, font=('Segoe UI', 10, 'bold'),
                              bg='#222', fg='white')
        self.label.pack()
        self.display = tk.Label(self, text="", font=('Consolas', 18), bg='#004d1a' if self.is_player else '#1565c0',
                                fg='#fff', anchor='w', height=2, width=18, bd=2, relief=tk.SUNKEN)
        self.display.pack(padx=2, pady=(0, 2), fill='x', expand=True)
        btn_row = tk.Frame(self, bg='#222')
        btn_row.pack()
        self.rank_btns = []
        for ri, r in enumerate(RANKS):
            b = tk.Button(btn_row, text=r, width=2, font=('Segoe UI', 11),
                          command=lambda rank=r: self.rank_clicked(rank))
            b.grid(row=0, column=ri, padx=1)
            self.rank_btns.append(b)
        self.undo_btn = tk.Button(btn_row, text='U', width=2, font=('Segoe UI', 11, 'bold'), command=self.undo)
        self.undo_btn.grid(row=0, column=len(RANKS), padx=3)
        if self.is_dealer:
            self.reveal_btn = tk.Button(self, text="Reveal Hole Card", font=('Segoe UI', 9),
                                        command=self.reveal_hole_card)
            self.reveal_btn.pack(pady=(4, 2))

    def rank_clicked(self, rank):
        if self.is_dealer and self.hole_card_enabled and (len(self.cards) == 1 or self.hole_card is not None):
            # Only allow input in the hole card slot when enabled
            self.choose_suit(rank, is_hole=True)
        else:
            self.choose_suit(rank, is_hole=False)

    def choose_suit(self, rank, is_hole=False):
        suit_win = tk.Toplevel(self)
        suit_win.title("Suit")
        suit_win.geometry("+600+340")

        def pick_suit(suit):
            suit_win.destroy()
            self.input_card(rank, suit, is_hole)

        for i, suit in enumerate(SUITS):
            btn = tk.Button(suit_win, text=suit, font=('Segoe UI', 16, 'bold'), width=3,
                            fg='#ff4d4d' if suit == '♥' else '#40e0d0' if suit == '♦' else '#90ee90' if suit == '♣' else 'white',
                            command=lambda s=suit: pick_suit(s))
            btn.grid(row=0, column=i, padx=6, pady=8)
        suit_win.grab_set()
        suit_win.transient(self)
        suit_win.wait_window()

    def input_card(self, rank, suit, is_hole=False):
        if self.is_dealer and is_hole:
            self.hole_card = (rank, suit)
            self.on_card(rank, suit, is_hole=True)
        else:
            self.cards.append((rank, suit))
            self.on_card(rank, suit, is_hole=False)
        self.update_display()

    def undo(self):
        if self.is_dealer and self.hole_card:
            self.hole_card = None
            self.on_undo(is_hole=True)
        elif self.cards:
            last_card = self.cards.pop()
            self.on_undo(rank=last_card[0], is_hole=False)
        self.update_display()

    def reset(self):
        self.cards = []
        self.hole_card = None
        self.update_display()
        self.set_enabled(True)
        if self.is_dealer:
            self.hole_card_enabled = False

    def update_display(self):
        if self.is_dealer:
            up = self.cards[0] if self.cards else None
            up_str = f"{up[0]}{up[1]}" if up else ""
            hole_str = f"{self.hole_card[0]}{self.hole_card[1]}" if self.hole_card else "?"
            self.display.config(text=f"{up_str}   {hole_str}")
        else:
            disp = ""
            for r, s in self.cards:
                disp += f"{r}{s} "
            self.display.config(text=disp.strip())

    def set_enabled(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        for btn in self.rank_btns:
            btn.config(state=state)
        self.undo_btn.config(state=state)
        if self.is_dealer:
            self.reveal_btn.config(state=tk.NORMAL if enabled else tk.DISABLED)

    def reveal_hole_card(self):
        self.hole_card_enabled = True

    def get_cards(self):
        return self.cards

    def add_card(self, rank, suit):
        self.cards.append((rank, suit))
        self.update_display()


# ---- Main App ----
class BlackjackTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Blackjack Card Tracker Pro")
        self.geometry("1240x700")
        self.configure(bg='#202645')
        self.decks = DEFAULT_DECKS
        self.seat = None
        self.seat_index = 0
        self._deal_step = 0  # 0 = first card, 1 = second card dealt, >=2 = manual
        self._focus_idx = 0
        self._auto_focus = True

        # --- Card comp panel ---
        self.comp_panel = CompPanel(self, self.on_decks_change)
        self.comp_panel.grid(row=0, column=0, sticky='nw', padx=12, pady=8)

        # --- Table row (hand panels) ---
        self.seat_hands = {}
        table_frame = tk.Frame(self, bg='#202645')
        table_frame.grid(row=0, column=1, sticky='nw', pady=8)
        for si, seat in enumerate(SEATS):  # Left to right: P7 ... P1
            self.seat_hands[seat] = SeatHandPanel(table_frame, seat, False, False)
            self.seat_hands[seat].grid(row=0, column=si, padx=4, pady=2)

        # --- Shared input panel (for all seats except your seat) ---
        self.shared_input_panel = SharedInputPanel(self, self.handle_shared_card, self.handle_shared_undo)
        self.shared_input_panel.grid(row=1, column=1, sticky='n', pady=(0, 2))

        # --- Dealer zone (below) ---
        self.dealer_panel = PlayerOrDealerPanel(self, "Dealer", False, True, self.on_dealer_card, self.on_dealer_undo,
                                                hole_card_reveal=True)
        self.dealer_panel.grid(row=2, column=0, padx=12, pady=(10, 2), sticky='ew')

        # --- Player zone (your hand, below dealer) ---
        self.player_panel = PlayerOrDealerPanel(self, "Player", True, False, self.on_player_card, self.on_player_undo)
        self.player_panel.grid(row=2, column=1, padx=12, pady=(10, 2), sticky='ew')

        # --- Seat selection ---
        self.after(200, self.prompt_seat_selection)

        # --- Keyboard ---
        self.bind_all('<Key>', self.handle_key)

    def prompt_seat_selection(self):
        dialog = SeatSelectDialog(self)
        self.seat = dialog.selected.get()
        self.seat_index = SEATS.index(self.seat)
        for s, panel in self.seat_hands.items():
            panel.is_your_seat = (s == self.seat)
            panel.highlight(active=False)
        self.reset_flow()

    def on_decks_change(self):
        self.decks = self.comp_panel.decks
        self.reset_flow()

    def reset_flow(self):
        self.comp_panel.reset()
        for s, p in self.seat_hands.items():
            p.reset()
            p.highlight(active=False)
        self.player_panel.reset()
        self.dealer_panel.reset()
        self._deal_step = 0
        self._focus_idx = 0
        self._auto_focus = True
        self._deal_counts = {seat: 0 for seat in SEATS}
        self._player_deal_count = 0
        self._dealer_deal_count = 0
        self.dealer_panel.hole_card_enabled = False
        self.set_focus()

    def set_focus(self):
        # Handle auto-focus for initial two cards only
        for seat, panel in self.seat_hands.items():
            panel.highlight(active=False)
        self.player_panel.set_enabled(False)
        self.shared_input_panel.set_enabled(False)
        self.dealer_panel.set_enabled(False)

        if not self._auto_focus:
            self.shared_input_panel.set_enabled(True)
            self.player_panel.set_enabled(True)
            self.dealer_panel.set_enabled(True)
            return

        # Auto-focus logic
        order = list(reversed(SEATS))
        n = len(order)
        if self._deal_step < 2:
            if self._focus_idx < n:
                seat = order[self._focus_idx]
                if seat == self.seat:
                    # Check if player needs more cards for this deal step
                    cards_needed = self._deal_step + 1
                    if len(self.player_panel.cards) >= cards_needed:
                        self.advance_flow()
                        return
                    self.player_panel.set_enabled(True)
                    self.shared_input_panel.set_enabled(False)
                    self.dealer_panel.set_enabled(False)
                else:
                    self.player_panel.set_enabled(False)
                    self.shared_input_panel.set_enabled(True)
                    self.dealer_panel.set_enabled(False)
                    self.seat_hands[seat].highlight(active=True)
            elif self._focus_idx == n:
                # Dealer's turn
                if self._deal_step == 0:
                    # Dealer upcard
                    self.dealer_panel.set_enabled(True)
                    self.shared_input_panel.set_enabled(False)
                    self.player_panel.set_enabled(False)
                else:
                    # Dealer hole card - skip for now
                    self.advance_flow()
        else:
            # Manual mode - enable all
            self.shared_input_panel.set_enabled(True)
            self.player_panel.set_enabled(True)
            self.dealer_panel.set_enabled(True)

    def advance_flow(self):
        self._focus_idx += 1
        order = list(reversed(SEATS))
        if self._focus_idx > len(order):  # Done with all seats + dealer in this card step
            self._focus_idx = 0
            self._deal_step += 1
            if self._deal_step >= 2:
                self._auto_focus = False
        self.set_focus()

    # -- Shared input panel logic --
    def handle_shared_card(self, rank, suit):
        if not self._auto_focus:
            return
        order = list(reversed(SEATS))
        if self._focus_idx >= len(order):
            return
        seat = order[self._focus_idx]
        if seat == self.seat:
            return
        self.seat_hands[seat].add_card(rank, suit)
        self.comp_panel.log_card(rank)
        self.advance_flow()

    def handle_shared_undo(self):
        if not self._auto_focus:
            return
        order = list(reversed(SEATS))
        if self._focus_idx >= len(order):
            return
        seat = order[self._focus_idx]
        if seat == self.seat:
            return
        if self.seat_hands[seat].cards:
            last_card = self.seat_hands[seat].cards[-1]
            self.seat_hands[seat].undo()
            self.comp_panel.undo_card(last_card[0])

    # -- Player and Dealer logic --
    def on_player_card(self, rank, suit, is_hole=False):
        self.comp_panel.log_card(rank)
        if self._auto_focus:
            self.advance_flow()

    def on_player_undo(self, rank=None, is_hole=False):
        if rank:
            self.comp_panel.undo_card(rank)

    def on_dealer_card(self, rank, suit, is_hole=False):
        if not is_hole:
            self.comp_panel.log_card(rank)
        if self._auto_focus:
            self.advance_flow()

    def on_dealer_undo(self, rank=None, is_hole=False):
        if rank and not is_hole:
            self.comp_panel.undo_card(rank)

    def handle_key(self, event):
        char = event.char.upper()
        if char in RANKS:
            if self._auto_focus:
                order = list(reversed(SEATS))
                if self._focus_idx < len(order):
                    seat = order[self._focus_idx]
                    if seat == self.seat:
                        self.player_panel.rank_clicked(char)
                    else:
                        self.shared_input_panel.rank_clicked(char)
                elif self._focus_idx == len(order) and self._deal_step == 0:
                    self.dealer_panel.rank_clicked(char)
        elif char == 'U':
            if self._auto_focus:
                order = list(reversed(SEATS))
                if self._focus_idx < len(order):
                    seat = order[self._focus_idx]
                    if seat == self.seat:
                        self.player_panel.undo()
                    else:
                        self.handle_shared_undo()
                elif self._focus_idx == len(order) and self._deal_step == 0:
                    self.dealer_panel.undo()


if __name__ == "__main__":
    app = BlackjackTrackerApp()
    app.mainloop()
