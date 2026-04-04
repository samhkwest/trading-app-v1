def detect_regime(df_5m):

    if len(df_5m) < 20:
        return "RANGE"

    ema20_now = df_5m["ema20"].iloc[-1]
    ema20_prev = df_5m["ema20"].iloc[-12]

    slope_strength = abs(ema20_now - ema20_prev)

    if slope_strength > 80:
        return "TREND"

    return "RANGE"