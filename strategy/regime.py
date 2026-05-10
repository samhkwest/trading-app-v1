# strategy/regime.py

import numpy as np

def detect_regime(df_5m):

    if len(df_5m) < 20:
        return "RANGE"

    df = df_5m.copy()

    # EMA20
    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()

    ema_now = df["ema20"].iloc[-1]
    ema_prev_10 = df["ema20"].iloc[-10]

    slope = ema_now - ema_prev_10

    # Volatility compression (last 10 bars range avg)
    recent_range = (df["high"] - df["low"]).rolling(10).mean().iloc[-1]
    past_range = (df["high"] - df["low"]).rolling(30).mean().iloc[-1]

    # --------------------------
    # TREND
    # --------------------------
    if abs(slope) > 80:
        return "TREND"

    # --------------------------
    # TRANSITION
    # Compression + weak slope
    # --------------------------
    if abs(slope) <= 80 and recent_range < past_range * 0.8:
        return "TRANSITION"

    # --------------------------
    # RANGE
    # --------------------------
    return "RANGE"