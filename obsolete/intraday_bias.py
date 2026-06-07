# strategy/intraday_bias.py

from config import TREND_SLOPE_THRESHOLD


class IntradayBias:
    """
    Handles intraday directional regime detection.

    Responsibilities:
    - Detect strong session bias (UP / DOWN)
    - Persist bias across bars
    - Reset bias at new session
    - Control directional permission

    This module does NOT:
    - Generate signals
    - Compute ATR
    - Execute trades
    """

    def __init__(self):
        self.session_bias = "NEUTRAL"   # "UP", "DOWN", "NEUTRAL"
        self.bias_locked = False
        self.current_day = None

    # ==========================================================
    # ✅ Session Reset
    # ==========================================================

    def _reset_if_new_day(self, df_5m):
        latest_time = df_5m["datetime"].iloc[-1]
        trade_day = latest_time.date()

        if self.current_day != trade_day:
            self.current_day = trade_day
            self.session_bias = "NEUTRAL"
            self.bias_locked = False

    # ==========================================================
    # ✅ Update Bias State
    # ==========================================================

    def update(self, df_5m):

        if df_5m is None or len(df_5m) < 20:
            return

        self._reset_if_new_day(df_5m)

        # Do not re-lock if already locked
        if self.bias_locked:
            return

        # Require enough bars (~1 hour of 5m)
        if len(df_5m) < 12:
            return

        df = df_5m.copy()
        df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()

        ema_now = df["ema20"].iloc[-1]
        ema_prev = df["ema20"].iloc[-10]
        slope = ema_now - ema_prev

        price_now = df["close"].iloc[-1]

        # Directional persistence (last 5 bars)
        recent = df.iloc[-5:]
        bullish_bars = (recent["close"] > recent["open"]).sum()
        bearish_bars = (recent["close"] < recent["open"]).sum()

        persistent_up = bullish_bars >= 4
        persistent_down = bearish_bars >= 4

        strong_up = slope > TREND_SLOPE_THRESHOLD
        strong_down = slope < -TREND_SLOPE_THRESHOLD

        price_above_ema = price_now > ema_now
        price_below_ema = price_now < ema_now

        # Lock bias
        if strong_up and price_above_ema and persistent_up:
            self.session_bias = "UP"
            self.bias_locked = True

        elif strong_down and price_below_ema and persistent_down:
            self.session_bias = "DOWN"
            self.bias_locked = True

    # ==========================================================
    # ✅ Direction Permission
    # ==========================================================

    def allow(self, signal):
        """
        Returns True if trade direction is allowed
        under current session bias.
        """

        if self.session_bias == "UP" and signal == "SELL":
            return False

        if self.session_bias == "DOWN" and signal == "BUY":
            return False

        return True