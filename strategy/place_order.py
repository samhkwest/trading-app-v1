# strategy/place_order.py

import pandas as pd


def order_signal(df_1m, df_5m, position):
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
    recent_lows = df["low"].iloc[-6:-2]
    recent_highs = df["high"].iloc[-6:-2]

    if recent_lows.empty or recent_highs.empty:
        return None

    swing_low = recent_lows.min()
    swing_high = recent_highs.max()

    current = df.iloc[-1]
    current_low = current["low"]
    current_high = current["high"]
    current_close = current["close"]

    # -------------------------------------------------
    # 3) Bullish Sweep (Stop Hunt Below)
    # -------------------------------------------------
    sweep_down = current_low < swing_low
    reclaim_up = current_close > swing_low

    if sweep_down and reclaim_up:
        return "BUY"

    # -------------------------------------------------
    # 4) Bearish Sweep (Stop Hunt Above)
    # -------------------------------------------------
    sweep_up = current_high > swing_high
    reclaim_down = current_close < swing_high

    #if sweep_up and reclaim_down:
    #    return "SELL"

    return None