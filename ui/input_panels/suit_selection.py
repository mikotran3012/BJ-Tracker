import tkinter as tk


def get_suit_selection(parent, on_suit_selected):
    """FIXED: Suit selection with all 4 suits clearly visible."""
    suit_win = tk.Toplevel(parent)
    suit_win.title("Suit")

    # Slightly bigger to accommodate all suits clearly
    suit_win.geometry("180x70")
    suit_win.resizable(False, False)

    # Position relative to parent
    try:
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        # Center on parent
        x = parent_x + (parent_width // 2) - 90  # 90 = half of 180
        y = parent_y + (parent_height // 2) - 35  # 35 = half of 70

        # Keep on screen
        screen_width = suit_win.winfo_screenwidth()
        screen_height = suit_win.winfo_screenheight()

        x = max(10, min(x, screen_width - 190))
        y = max(10, min(y, screen_height - 80))

        suit_win.geometry(f"180x70+{x}+{y}")

    except:
        suit_win.geometry("180x70+600+340")

    # Prevent double selection
    selected = [False]

    def pick_suit(suit):
        if selected[0]:  # Already selected
            return
        selected[0] = True
        suit_win.destroy()
        on_suit_selected(suit)

    # FIXED: All 4 suits with proper colors
    suits = ['♠', '♥', '♦', '♣']
    colors = ['#000000', '#ff0000', '#ff6600', '#008000']  # Black, Red, Orange, Green
    names = ['Spades', 'Hearts', 'Diamonds', 'Clubs']

    # Create main frame
    main_frame = tk.Frame(suit_win, bg='white')
    main_frame.pack(fill='both', expand=True, padx=5, pady=5)

    for i, (suit, color, name) in enumerate(zip(suits, colors, names)):
        # Create button with clear background and border
        btn = tk.Button(
            main_frame,
            text=suit,
            font=('Segoe UI', 16, 'bold'),
            width=3,
            height=1,
            fg=color,
            bg='white',  # White background for all
            relief=tk.RAISED,
            bd=2,
            activebackground='#f0f0f0',  # Light gray when clicked
            activeforeground=color,
            command=lambda s=suit: pick_suit(s)
        )
        btn.grid(row=0, column=i, padx=3, pady=5, sticky='nsew')

        # Add tooltip-like label below
        label = tk.Label(
            main_frame,
            text=name[0],  # Just first letter: S, H, D, C
            font=('Segoe UI', 8),
            fg='gray',
            bg='white'
        )
        label.grid(row=1, column=i, sticky='n')

    # Make buttons expand
    for i in range(4):
        main_frame.grid_columnconfigure(i, weight=1)

    # Keyboard shortcuts
    def handle_key(event):
        if selected[0]:  # Already selected
            return

        key = event.char.lower()
        suit_map = {
            's': '♠',  # Spades
            'h': '♥',  # Hearts
            'd': '♦',  # Diamonds
            'c': '♣'  # Clubs
        }

        if key in suit_map:
            pick_suit(suit_map[key])
            return 'break'
        elif event.keysym == 'Escape':
            if not selected[0]:
                selected[0] = True
                suit_win.destroy()
            return 'break'

    suit_win.bind('<Key>', handle_key)
    suit_win.focus_set()

    suit_win.grab_set()
    suit_win.transient(parent)
    suit_win.wait_window()


def debug_suit_selection(parent):
    """Debug version to test if all suits show up."""
    print("DEBUG: Testing suit selection...")

    def on_suit_selected(suit):
        print(f"DEBUG: Selected suit: {suit}")

    get_suit_selection(parent, on_suit_selected)