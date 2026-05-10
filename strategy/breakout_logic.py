# strategy/breakout_logic.py

def breakout_signal(df_1m, df_5m, position):

    if position != 0:
        return None

    if len(df_5m) < 2:
        return None

    latest_5m = df_5m.iloc[-1]
    prev_5m = df_5m.iloc[-2]

    df_1m = df_1m.copy()
    df_1m["ema5"] = df_1m["close"].ewm(span=5, adjust=False).mean()
    df_1m["ema10"] = df_1m["close"].ewm(span=10, adjust=False).mean()

    ema5 = df_1m["ema5"].iloc[-1]
    ema10 = df_1m["ema10"].iloc[-1]

    breakout_long = (
        latest_5m["close"] > prev_5m["high"] and
        ema5 > ema10
    )

    breakout_short = (
        latest_5m["close"] < prev_5m["low"] and
        ema5 < ema10
    )

    if breakout_long:
        return "BUY"

    if breakout_short:
        return "SELL"

    return None