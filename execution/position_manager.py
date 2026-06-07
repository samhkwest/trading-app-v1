# execution/position_manager.py

class PositionManager:
    """
    Stores the current position state.

    This class DOES NOT:
    - Calculate TP/SL
    - Calculate PnL
    - Make strategy decisions

    It only stores trade state and metadata.
    """

    def __init__(self):
        self.reset()

    # ----------------------------------------------------------
    # ✅ RESET POSITION STATE
    # ----------------------------------------------------------

    def reset(self):
        """Clears all position data."""
        self.position = 0            # +1 (long), -1 (short), 0 (flat)
        self.direction = None        # "LONG" or "SHORT"

        self.entry_price = None
        self.entry_time = None

        # ✅ Strategy metadata at entry
        self.entry_slope = None
        self.entry_atr = None

        # ✅ Exit metadata (captured at exit)
        self.last_exit_slope = None
        self.last_exit_atr = None

    # ----------------------------------------------------------
    # ✅ OPEN POSITION
    # ----------------------------------------------------------

    def open_position(self, side, price, timestamp, slope=None, atr=None):
        """
        Opens a new position and stores entry metadata.
        """

        self.position = 1 if side == "BUY" else -1
        self.direction = "LONG" if side == "BUY" else "SHORT"

        self.entry_price = price
        self.entry_time = timestamp

        self.entry_slope = slope
        self.entry_atr = atr

    # ----------------------------------------------------------
    # ✅ CLOSE POSITION
    # ----------------------------------------------------------

    def close_position(self, exit_slope=None, exit_atr=None):
        """
        Stores exit metadata before resetting.
        """

        self.last_exit_slope = exit_slope
        self.last_exit_atr = exit_atr

        # Reset active trade state
        self.position = 0
        self.direction = None
        self.entry_price = None
        self.entry_time = None