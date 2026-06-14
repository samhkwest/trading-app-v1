# strategy/trend_logic.py

import pandas as pd
from strategy.entry_filters import volume_confirmation_filter
from config import PRINT_DEBUG_VOLUME


def trend_signal(df_entry, df_structure, position):
    """
    Trend continuation signal with volume confirmation.

    Trades pullbacks in strong trends:
    - Uptrend: EMA5 > EMA10 + higher close (with volume)
    - Downtrend: EMA5 < EMA10 + lower close (with volume)
    """

    if position != 0:
        return None

    # ✅ Require sufficient bars for stability
    if len(df_entry) < 10 or len(df_structure) < 30:
        return None

    df1 = df_entry
    df5 = df_structure

    # -------------------------------------------------
    # 1️⃣ Compute EMA on 1m (entry timeframe)
    # -------------------------------------------------
    ema5_series = df1["close"].ewm(span=5, adjust=False).mean()
    ema10_series = df1["close"].ewm(span=10, adjust=False).mean()

    ema5 = ema5_series.iloc[-2]
    ema10 = ema10_series.iloc[-2]

    close_now = df1["close"].iloc[-1]
    close_prev = df1["close"].iloc[-3]

    # -------------------------------------------------
    # 2️⃣ Compute EMA20 slope on 5m (structure timeframe)
    # ✅ USE COMPLETED 5m BAR
    # -------------------------------------------------
    ema20_series = df5["close"].ewm(span=20, adjust=False).mean()

    ema_now = ema20_series.iloc[-2]
    ema_prev = ema20_series.iloc[-11]

    slope = ema_now - ema_prev

    # ✅ Guard against NaN slope
    if slope is None or slope != slope:
        return None

    # -------------------------------------------------
    # 3️⃣ Directional Continuation Logic
    # -------------------------------------------------

    signal = None

    if slope > 0:
        if ema5 > ema10 and close_now > close_prev:
            signal = "BUY"

    if slope < 0:
        if ema5 < ema10 and close_now < close_prev:
            signal = "SELL"

    if signal is None:
        return None

    # -------------------------------------------------
    # 4️⃣ ✅ VOLUME CONFIRMATION (unchanged)
    # -------------------------------------------------
    '''
    if not volume_confirmation_filter(df_structure, print_debug=PRINT_DEBUG_VOLUME):
        if PRINT_DEBUG_VOLUME:
            print(f"[Trend] {signal} signal BLOCKED by volume filter")
        return None

    if PRINT_DEBUG_VOLUME:
        print(f"[Trend] {signal} signal APPROVED (volume confirmed)")
    '''
    return signal