# strategy/exhaustion_filter.py

def is_exhausted_move(df, lookback=20, range_multiplier=2.2):
    """
    Detect true impulse continuation.
    Much stricter than previous version.
    """

    if df is None or len(df) < lookback + 4:
        return False

    df = df.copy()

    # -----------------------------------------
    # 1) Abnormally Large Candle
    # -----------------------------------------
    df["range"] = df["high"] - df["low"]
    avg_range = df["range"].rolling(lookback).mean().iloc[-2]
    current_range = df["range"].iloc[-1]

    large_expansion = current_range > avg_range * range_multiplier

    # -----------------------------------------
    # 2) 3 Strong Continuation Candles BEFORE current
    # -----------------------------------------
    prev3 = df.iloc[-4:-1]  # exclude current candle

    bullish_seq = (prev3["close"] > prev3["open"]).all()
    bearish_seq = (prev3["close"] < prev3["open"]).all()

    strong_sequence = bullish_seq or bearish_seq

    # -----------------------------------------
    # Final Exhaustion Condition
    # Only block if BOTH true
    # -----------------------------------------
    if large_expansion and strong_sequence:
        return True

    return False