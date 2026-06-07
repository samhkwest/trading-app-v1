# strategy/sweep_logic.py

import pandas as pd
from strategy.exhaustion_filter import is_exhausted_move
from strategy.entry_filters import volume_confirmation_filter
from config import PRINT_DEBUG_VOLUME

def sweep_signal(df_1m, df_5m, position):
    """
    Liquidity sweep signal with volume and exhaustion confirmation.
    
    Implements stop hunt patterns:
    - Bullish: Break below swing low + reclaim with strong body + volume
    - Bearish: Break above swing high + reclaim with strong body + volume
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
            if PRINT_DEBUG_VOLUME:
                print("[Sweep] BUY signal BLOCKED by exhaustion filter")
            return None
        
        # ✅ CHECK VOLUME CONFIRMATION (NEW)
        if not volume_confirmation_filter(df_5m, print_debug=PRINT_DEBUG_VOLUME):
            if PRINT_DEBUG_VOLUME:
                print("[Sweep] BUY signal BLOCKED by volume filter")
            return None
        
        if PRINT_DEBUG_VOLUME:
            print("[Sweep] BUY signal APPROVED (exhaustion + volume confirmed)")
        return "BUY"

    # -------------------------------------------------
    # 4) Bearish Sweep (Stop Hunt Above)
    # -------------------------------------------------
    sweep_up = current_high > swing_high
    reclaim_down = current_close < swing_high

    if sweep_up and reclaim_down:
        
        # ✅ ADD GUARDS FOR BEARISH SWEEP (MATCHING BULLISH LOGIC)
        is_bearish = current_close < current_open
        strong_body_bearish = body_size > 0.5 * candle_range
        
        # Close must be in lower 30% of candle
        close_position_bearish = (current_high - current_close) / candle_range
        strong_close_bearish = close_position_bearish > 0.7
        
        # Upper wick must be meaningful (rejection)
        upper_wick = current_high - max(current_open, current_close)
        lower_wick = min(current_open, current_close) - current_low
        wick_rejection_bearish = upper_wick > lower_wick
        
        # Require same quality as bullish sweep
        if not (is_bearish and strong_body_bearish and strong_close_bearish and wick_rejection_bearish):
            if PRINT_DEBUG_VOLUME:
                print("[Sweep] SELL signal BLOCKED by pattern quality filter")
            return None
        
        # ✅ CHECK VOLUME CONFIRMATION (NEW)
        if not volume_confirmation_filter(df_5m, print_debug=PRINT_DEBUG_VOLUME):
            if PRINT_DEBUG_VOLUME:
                print("[Sweep] SELL signal BLOCKED by volume filter")
            return None
        
        if PRINT_DEBUG_VOLUME:
            print("[Sweep] SELL signal APPROVED (pattern + volume confirmed)")
        return "SELL"

    return None
