# execution/execution_engine.py

from config import TAKE_PROFIT, STOP_LOSS, POINT_VALUE


class ExecutionEngine:
    """
    Handles trade execution logic:

    - Entry processing
    - TP/SL checks
    - PnL calculation

    This class is STRATEGY-AGNOSTIC.
    """

    def __init__(self, position_manager):
        self.pm = position_manager

    # ----------------------------------------------------------
    # ✅ PROCESS ENTRY
    # ----------------------------------------------------------

    def process_entry(self, decision, price, timestamp):
        """
        Opens a position using decision data.
        """

        self.pm.open_position(
            side=decision["side"],
            price=price,
            timestamp=timestamp,
            slope=decision.get("slope"),
            atr=decision.get("atr")
        )

    # ----------------------------------------------------------
    # ✅ CHECK EXIT (TP / SL)
    # ----------------------------------------------------------

    def check_exit(self, current_high, current_low, timestamp):
        """
        Checks if TP or SL is hit.

        Returns:
            dict with full exit + entry metadata
            OR None if no exit
        """

        if self.pm.position == 0:
            return None

        entry_price = self.pm.entry_price
        entry_time = self.pm.entry_time
        entry_slope = self.pm.entry_slope
        entry_atr = self.pm.entry_atr

        position = self.pm.position
        direction = "LONG" if position == 1 else "SHORT"

        exit_price = None

        # --------------------------------------------------
        # ✅ LONG POSITION
        # --------------------------------------------------

        if position == 1:

            tp_price = entry_price + TAKE_PROFIT
            sl_price = entry_price - STOP_LOSS

            tp_hit = current_high >= tp_price
            sl_hit = current_low <= sl_price

            # Conservative assumption:
            # SL first if both hit in same candle
            if tp_hit and sl_hit:
                exit_price = sl_price
            elif tp_hit:
                exit_price = tp_price
            elif sl_hit:
                exit_price = sl_price

        # --------------------------------------------------
        # ✅ SHORT POSITION
        # --------------------------------------------------

        elif position == -1:

            tp_price = entry_price - TAKE_PROFIT
            sl_price = entry_price + STOP_LOSS

            tp_hit = current_low <= tp_price
            sl_hit = current_high >= sl_price

            if tp_hit and sl_hit:
                exit_price = sl_price
            elif tp_hit:
                exit_price = tp_price
            elif sl_hit:
                exit_price = sl_price

        # --------------------------------------------------
        # ✅ IF EXIT TRIGGERED
        # --------------------------------------------------

        if exit_price is not None:

            pnl_points = (exit_price - entry_price) * position
            pnl_hkd = pnl_points * POINT_VALUE

            # ✅ Close position AFTER capturing metadata
            self.pm.close_position()

            return {
                "entry_time": entry_time,
                "entry_price": entry_price,
                "entry_slope": entry_slope,
                "entry_atr": entry_atr,
                "exit_price": exit_price,
                "pnl_hkd": pnl_hkd,
                "direction": direction,
                "exit_time": timestamp
            }

        return None