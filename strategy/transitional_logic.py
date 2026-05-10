# strategy/transitional_logic.py

def transitional_signal(df_1m, df_5m, position):

    if position != 0:
        return None

    if len(df_5m) < 5:
        return None

    # Exclude current bar from base calculation
    recent = df_5m.iloc[-6:-1]

    base_high = recent["high"].max()
    base_low = recent["low"].min()

    latest_close = df_5m["close"].iloc[-1]

    # Break above base
    if latest_close > base_high:
        return "BUY"

    # Break below base
    if latest_close < base_low:
        return "SELL"

    return None