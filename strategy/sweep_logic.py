# strategy/sweep_logic.py

import pandas as pd
from strategy.exhaustion_filter import is_exhausted_move
from strategy.entry_filters import volume_confirmation_filter
from config import PRINT_DEBUG_VOLUME


def sweep_signal(df_structure, position):
    """
    Liquidity sweep signal with volume and exhaustion confirmation.

    Implements stop hunt patterns:
    - Bullish: Break below swing low + reclaim with strong body
    - Bearish: Break above swing high + reclaim with strong body
    """

    # -------------------------------------------------
    # 1) Only trade when flat
    # -------------------------------------------------
    if position != 0:
        return None

    prev_cnt = 15

    # ✅ Require sufficient 5m history
    if df_structure is None or len(df_structure) < prev_cnt + 2:
        return None

    df = df_structure  # ✅ read-only access

    # ✅ Use last COMPLETED 5m candle
    current = df.iloc[-2]

    current_low = current["low"]
    current_high = current["high"]
    current_close = current["close"]
    current_open = current["open"]

    # -------------------------------------------------
    # 2) Define previous swing levels
    # -------------------------------------------------
    recent_lows = df["low"].iloc[-(prev_cnt + 2):-2]
    recent_highs = df["high"].iloc[-(prev_cnt + 2):-2]

    if recent_lows.empty or recent_highs.empty:
        return None

    swing_low = recent_lows.min()
    swing_high = recent_highs.max()

    # -------------------------------------------------
    # 3) Bullish Sweep
    # -------------------------------------------------
    sweep_down = current_low < swing_low
    reclaim_up = current_close > swing_low

    body_size = abs(current_close - current_open)
    candle_range = current_high - current_low

    if candle_range == 0:
        return None

    is_bullish = current_close > current_open
    strong_body = body_size > 0.5 * candle_range

    close_position = (current_close - current_low) / candle_range
    strong_close = close_position > 0.7

    lower_wick = min(current_open, current_close) - current_low
    upper_wick = current_high - max(current_open, current_close)
    wick_rejection = lower_wick > upper_wick

    if sweep_down and reclaim_up and is_bullish and strong_body and strong_close and wick_rejection:

        if is_exhausted_move(df):
            if PRINT_DEBUG_VOLUME:
                print("[Sweep] BUY signal BLOCKED by exhaustion filter")
            return None

        return "BUY"

    # -------------------------------------------------
    # 4) Bearish Sweep
    # -------------------------------------------------
    sweep_up = current_high > swing_high
    reclaim_down = current_close < swing_high

    if sweep_up and reclaim_down:

        is_bearish = current_close < current_open
        strong_body_bearish = body_size > 0.5 * candle_range

        close_position_bearish = (current_high - current_close) / candle_range
        strong_close_bearish = close_position_bearish > 0.7

        upper_wick = current_high - max(current_open, current_close)
        lower_wick = min(current_open, current_close) - current_low
        wick_rejection_bearish = upper_wick > lower_wick

        if not (
            is_bearish and
            strong_body_bearish and
            strong_close_bearish and
            wick_rejection_bearish
        ):
            return None

        if is_exhausted_move(df):
            if PRINT_DEBUG_VOLUME:
                print("[Sweep] SELL signal BLOCKED by exhaustion filter")
            return None

        return "SELL"

    return None