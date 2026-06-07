# strategy/trend_logic.py

import pandas as pd
from strategy.entry_filters import volume_confirmation_filter
from config import PRINT_DEBUG_VOLUME

def trend_signal(df_1m, df_5m, position):
    """
    Trend continuation signal with volume confirmation.
    
    Trades pullbacks in strong trends:
    - Uptrend: EMA5 > EMA10 + higher close (with volume)
    - Downtrend: EMA5 < EMA10 + lower close (with volume)
    """

    if position != 0:
        return None

    if len(df_1m) < 10 or len(df_5m) < 20:
        return None

    df1 = df_1m.copy()
    df5 = df_5m.copy()

    # -------------------------------------------------
    # 1️⃣ Compute EMA on 1m
    # -------------------------------------------------
    df1["ema5"] = df1["close"].ewm(span=5, adjust=False).mean()
    df1["ema10"] = df1["close"].ewm(span=10, adjust=False).mean()

    ema5 = df1["ema5"].iloc[-1]
    ema10 = df1["ema10"].iloc[-1]

    close_now = df1["close"].iloc[-1]
    close_prev = df1["close"].iloc[-2]

    # -------------------------------------------------
    # 2️⃣ Compute EMA20 slope on 5m
    # -------------------------------------------------
    df5["ema20"] = df5["close"].ewm(span=20, adjust=False).mean()

    ema_now = df5["ema20"].iloc[-1]
    ema_prev = df5["ema20"].iloc[-10]

    slope = ema_now - ema_prev

    # -------------------------------------------------
    # 3️⃣ Directional Continuation Logic
    # -------------------------------------------------

    signal = None

    # Strong uptrend → Long continuation only
    if slope > 0:
        if ema5 > ema10 and close_now > close_prev:
            signal = "BUY"

    # Strong downtrend → Short continuation only
    if slope < 0:
        if ema5 < ema10 and close_now < close_prev:
            signal = "SELL"

    if signal is None:
        return None

    # -------------------------------------------------
    # 4️⃣ ✅ VOLUME CONFIRMATION (NEW)
    # -------------------------------------------------
    if not volume_confirmation_filter(df_5m, print_debug=PRINT_DEBUG_VOLUME):
        if PRINT_DEBUG_VOLUME:
            print(f"[Trend] {signal} signal BLOCKED by volume filter")
        return None

    if PRINT_DEBUG_VOLUME:
        print(f"[Trend] {signal} signal APPROVED (volume confirmed)")

    return signal
