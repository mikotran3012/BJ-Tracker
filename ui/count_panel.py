"""
Updated Count Panel - Larger, cleaner display similar to reference image.
Uses bigger fonts, stacked layout for better readability.
"""

import tkinter as tk
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from counting.count_manager import CountManager


class CountPanel(tk.Frame):
    """Updated counting panel with larger, cleaner display."""

    def __init__(self, parent, count_manager: 'CountManager', **kwargs):
        """
        Initialize count panel with new styling.

        Args:
            parent: Parent Tkinter widget
            count_manager: Reference to the CountManager instance
            **kwargs: Additional Tkinter Frame arguments
        """
        # Updated styling for larger, cleaner look
        default_kwargs = {
            'bg': '#2c3e50',  # Darker blue-gray background
            'bd': 2,
            'relief': tk.RAISED,
            'padx': 12,
            'pady': 10
        }
        default_kwargs.update(kwargs)

        super().__init__(parent, **default_kwargs)

        self.count_manager = count_manager
        self.system_displays = []

        self._build_panel()

    def _build_panel(self):
        """Build the updated count panel UI."""
        # Optional: Panel header (can be removed if you prefer)
        header_frame = tk.Frame(self, bg='#2c3e50')
        header_frame.pack(fill='x', pady=(0, 8))

        title_label = tk.Label(
            header_frame,
            text="COUNTING SYSTEMS",
            font=('Segoe UI', 11, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'  # Light gray text
        )
        title_label.pack()

        # Container for all system displays
        self.systems_container = tk.Frame(self, bg='#2c3e50')
        self.systems_container.pack(fill='both', expand=True)

        # Build displays for each system
        self._build_system_displays()

    def _build_system_displays(self):
        """Build larger display widgets for each counting system."""
        # Clear existing displays
        for display in self.system_displays:
            display.destroy()
        self.system_displays.clear()

        # Create display for each system in the manager
        for i, system in enumerate(self.count_manager.get_all_systems()):
            system_frame = self._create_system_display(system.name, i)
            self.system_displays.append(system_frame)

    def _create_system_display(self, system_name: str, index: int) -> tk.Frame:
        """
        Create larger display widgets for a single counting system.

        Args:
            system_name: Name of the counting system
            index: Index of the system in the manager

        Returns:
            Frame containing the system display
        """
        # Main frame for this system - larger and more prominent
        system_frame = tk.Frame(
            self.systems_container,
            bg='#34495e',  # Slightly lighter than main background
            bd=2,
            relief=tk.RAISED,
            padx=15,       # Increased padding
            pady=12        # Increased padding
        )
        system_frame.pack(fill='x', pady=6)  # More space between systems

        # System name header - larger and more prominent
        name_label = tk.Label(
            system_frame,
            text=system_name,
            font=('Segoe UI', 14, 'bold'),  # Larger font
            bg='#34495e',
            fg='#e74c3c' if system_name == 'RAPC' else '#9b59b6',  # Red for RAPC, Purple for UAPC
            pady=4
        )
        name_label.pack()

        # Stats container - stacked layout like reference image
        stats_frame = tk.Frame(system_frame, bg='#34495e')
        stats_frame.pack(fill='x', pady=(8, 0))

        # Running Count row
        rc_row = tk.Frame(stats_frame, bg='#34495e')
        rc_row.pack(fill='x', pady=2)

        rc_label = tk.Label(
            rc_row,
            text="RC:",
            font=('Segoe UI', 12, 'bold'),  # Larger font
            bg='#34495e',
            fg='#bdc3c7',  # Light gray
            width=4,
            anchor='w'
        )
        rc_label.pack(side='left')

        rc_value = tk.Label(
            rc_row,
            text="0",
            font=('Segoe UI', 16, 'bold'),  # Much larger font for values
            bg='#2c3446',  # Darker background for value boxes
            fg='#ecf0f1',
            width=8,
            anchor='center',
            relief=tk.SUNKEN,
            bd=1
        )
        rc_value.pack(side='right', padx=(10, 0))

        # True Count row
        tc_row = tk.Frame(stats_frame, bg='#34495e')
        tc_row.pack(fill='x', pady=2)

        tc_label = tk.Label(
            tc_row,
            text="TC:",
            font=('Segoe UI', 12, 'bold'),  # Larger font
            bg='#34495e',
            fg='#bdc3c7',  # Light gray
            width=4,
            anchor='w'
        )
        tc_label.pack(side='left')

        tc_value = tk.Label(
            tc_row,
            text="0.00",
            font=('Segoe UI', 16, 'bold'),  # Much larger font for values
            bg='#2c3446',  # Darker background for value boxes
            fg='#f39c12',  # Orange/yellow for TC
            width=8,
            anchor='center',
            relief=tk.SUNKEN,
            bd=1
        )
        tc_value.pack(side='right', padx=(10, 0))

        # Store references to value labels for updates
        system_frame.rc_label = rc_value
        system_frame.tc_label = tc_value
        system_frame.system_index = index
        system_frame.system_name = system_name

        return system_frame

    def update_panel(self, cards_left: int, aces_left: int, decks: int):
        """
        Update all counting system displays with current values.

        Args:
            cards_left: Cards remaining in shoe
            aces_left: Aces remaining in shoe
            decks: Total decks in shoe
        """
        # Get current counts from all systems
        counts = self.count_manager.get_counts(cards_left, aces_left, decks)

        # Update each system display
        for i, (system_name, rc, tc) in enumerate(counts):
            if i < len(self.system_displays):
                display = self.system_displays[i]

                # Update RC display
                display.rc_label.config(text=str(rc))
                self._update_rc_color(display.rc_label, rc)

                # Update TC display
                display.tc_label.config(text=f"{tc:.1f}")  # Show 1 decimal place
                self._update_tc_color(display.tc_label, tc, system_name)

    def _update_rc_color(self, label: tk.Label, rc: int):
        """
        Update RC label color based on count value.

        Args:
            label: RC label to update
            rc: Running count value
        """
        if rc > 0:
            label.config(fg='#2ecc71', bg='#1e8449')  # Green background for positive
        elif rc < 0:
            label.config(fg='#e74c3c', bg='#922b21')  # Red background for negative
        else:
            label.config(fg='#ecf0f1', bg='#2c3446')  # Neutral gray

    def _update_tc_color(self, label: tk.Label, tc: float, system_name: str):
        """
        Update TC label color based on true count value and system type.

        Args:
            label: TC label to update
            tc: True count value
            system_name: Name of the counting system
        """
        # Different favorable ranges for different systems
        if system_name == "UAPC":
            # UAPC has +6 baseline, so favorable is around 7-8+
            if tc >= 8.0:
                label.config(fg='#27ae60', bg='#1e8449')  # Bright green for very favorable
            elif tc >= 7.0:
                label.config(fg='#2ecc71', bg='#239b56')  # Light green for favorable
            elif tc >= 5.5:
                label.config(fg='#f39c12', bg='#b7950b')  # Yellow for slightly unfavorable
            else:
                label.config(fg='#e74c3c', bg='#922b21')  # Red for unfavorable
        else:
            # Standard system (like RAPC) - favorable at +2+
            if tc >= 3.0:
                label.config(fg='#27ae60', bg='#1e8449')  # Bright green for very favorable
            elif tc >= 2.0:
                label.config(fg='#2ecc71', bg='#239b56')  # Light green for favorable
            elif tc >= 0.0:
                label.config(fg='#f39c12', bg='#b7950b')  # Yellow for neutral
            else:
                label.config(fg='#e74c3c', bg='#922b21')  # Red for unfavorable

    def refresh_systems(self):
        """
        Refresh the panel to reflect any changes in the count manager.
        Call this if systems are added, removed, or replaced.
        """
        self._build_system_displays()

    def reset_displays(self):
        """Reset all displays to show zero counts."""
        for display in self.system_displays:
            display.rc_label.config(text="0", fg='#ecf0f1', bg='#2c3446')
            display.tc_label.config(text="0.0", fg='#f39c12', bg='#2c3446')

    def get_display_info(self) -> dict:
        """
        Get information about the current display state.

        Returns:
            Dictionary with display information
        """
        return {
            'system_count': len(self.system_displays),
            'manager_systems': self.count_manager.get_system_count(),
            'systems': [system.name for system in self.count_manager.get_all_systems()]
        }

    def set_compact_mode(self, compact: bool = True):
        """
        Toggle between compact and expanded display modes.

        Args:
            compact: True for compact mode, False for expanded
        """
        if compact:
            # Reduce padding for compact display
            self.config(padx=8, pady=6)
            for display in self.system_displays:
                display.config(padx=10, pady=8)
        else:
            # Restore normal padding
            self.config(padx=12, pady=10)
            for display in self.system_displays:
                display.config(padx=15, pady=12)

    def highlight_system(self, system_name: str, highlight: bool = True):
        """
        Highlight a specific counting system.

        Args:
            system_name: Name of system to highlight
            highlight: True to highlight, False to remove highlight
        """
        for display in self.system_displays:
            if hasattr(display, 'system_name') and display.system_name == system_name:
                if highlight:
                    display.config(bg='#4a6741', bd=3, relief=tk.RAISED)  # Highlighted background
                else:
                    display.config(bg='#34495e', bd=2, relief=tk.RAISED)  # Normal background
                break