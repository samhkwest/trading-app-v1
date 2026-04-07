# strategy/signal.py

def generate_signal(df_1m, df_5m, position):

    if position != 0:
        return None

    # ==========================
    # 1️⃣ Calculate 1m EMA
    # ==========================
    df_1m = df_1m.copy()
    df_1m["ema5"] = df_1m["close"].ewm(span=5, adjust=False).mean()
    df_1m["ema10"] = df_1m["close"].ewm(span=10, adjust=False).mean()

    # ==========================
    # 2️⃣ Calculate 5m RSI
    # ==========================
    df_5m = df_5m.copy()

    delta = df_5m["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss
    df_5m["rsi"] = 100 - (100 / (1 + rs))

    # Need at least 2 bars for breakout comparison
    if len(df_5m) < 2:
        return None

    latest_1m = df_1m.iloc[-1]
    latest_5m = df_5m.iloc[-1]
    prev_5m = df_5m.iloc[-2]

    # ==========================
    # 3️⃣ TREND LOGIC (EMA)
    # ==========================
    ema5 = latest_1m["ema5"]
    ema10 = latest_1m["ema10"]

    # ==========================
    # 4️⃣ BREAKOUT LOGIC
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