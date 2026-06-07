# strategy/sweep_logic.py

import pandas as pd
from strategy.exhaustion_filter import is_exhausted_move

def sweep_signal(df_1m, df_5m, position):
    """
    Primary signal engine.
    Implements 5-minute liquidity sweep logic.
    """

    # -------------------------------------------------
    # 1) Only trade when flat
    # -------------------------------------------------
    if position != 0:
        return None

    if df_5m is None or len(df_5m) < 6:
        return None

    df = df_5m.copy()

    # -------------------------------------------------
    # 2) Define previous swing levels
    #    (Exclude latest 2 bars to avoid self-reference)
    # -------------------------------------------------
    prev_cnt = 15
    recent_lows = df["low"].iloc[-1 * prev_cnt:-2]
    recent_highs = df["high"].iloc[-1 * prev_cnt:-2]

    if recent_lows.empty or recent_highs.empty:
        return None

    swing_low = recent_lows.min()
    swing_high = recent_highs.max()

    current = df.iloc[-1]
    current_low = current["low"]
    current_high = current["high"]
    current_close = current["close"]
    current_open = current["open"]

    # -------------------------------------------------
    # 3) Bullish Sweep (Stop Hunt Below)
    # -------------------------------------------------
    sweep_down = current_low < swing_low
    reclaim_up = current_close > swing_low

    body_size = abs(current_close - current_open)
    candle_range = current_high - current_low

    if candle_range == 0:
        return None

    is_bullish = current_close > current_open
    strong_body = body_size > 0.5 * candle_range

    # Close must be in upper 30% of candle
    close_position = (current_close - current_low) / candle_range
    strong_close = close_position > 0.7

    # Lower wick must be meaningful (rejection)
    lower_wick = min(current_open, current_close) - current_low
    upper_wick = current_high - max(current_open, current_close)
    wick_rejection = lower_wick > upper_wick

    if sweep_down and reclaim_up and is_bullish and strong_body and strong_close and wick_rejection:
        # Block entry during impulse continuation
        if is_exhausted_move(df):
            return None
        return "BUY"

    # -------------------------------------------------
    # 4) Bearish Sweep (Stop Hunt Above)
    # -------------------------------------------------
    sweep_up = current_high > swing_high
    reclaim_down = current_close < swing_high

    if sweep_up and reclaim_down:
        return "SELL"

    return None