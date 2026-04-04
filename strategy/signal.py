# strategy/signal.py

def generate_signal(df_1m, df_5m, position):

    if position != 0:
        return None

    latest_1m = df_1m.iloc[-1]
    latest_5m = df_5m.iloc[-1]

    prev_5m = df_5m.iloc[-2]

    # ==========================
    # 1️⃣ TREND LOGIC (EMA)
    # ==========================
    ema5 = df_1m["ema5"].iloc[-1]
    ema10 = df_1m["ema10"].iloc[-1]

    # ==========================
    # 2️⃣ BREAKOUT LOGIC (NEW)
    # ==========================
    breakout_long = (
        latest_5m["close"] > prev_5m["high"] and
        ema5 > ema10 and
        latest_5m["rsi"] > 55
    )

    breakout_short = (
        latest_5m["close"] < prev_5m["low"] and
        ema5 < ema10 and
        latest_5m["rsi"] < 45
    )

    if breakout_long:
        return "BUY"

    if breakout_short:
        return "SELL"

    return None