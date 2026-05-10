# strategy/bottom_logic.py

def bottom_signal(df_5m, position):

    if position != 0:
        return None

    df = df_5m.copy()

    df["bb_mid"] = df["close"].rolling(20).mean()
    df["bb_std"] = df["close"].rolling(20).std()

    df["bb_upper"] = df["bb_mid"] + 2 * df["bb_std"]
    df["bb_lower"] = df["bb_mid"] - 2 * df["bb_std"]

    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    avg_loss = avg_loss.replace(0, 1e-10)

    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))

    latest = df.iloc[-1]

    # Buy at range low
    if latest["close"] <= latest["bb_lower"] and latest["rsi"] < 35:
        return "BUY"

    # Sell at range high
    if latest["close"] >= latest["bb_upper"] and latest["rsi"] > 65:
        return "SELL"

    return None