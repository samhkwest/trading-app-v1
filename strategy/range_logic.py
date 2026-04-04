def range_signal(df_5m, position):

    close = df_5m["close"].iloc[-1]
    upper = df_5m["bb_upper"].iloc[-1]
    lower = df_5m["bb_lower"].iloc[-1]
    rsi = df_5m["rsi"].iloc[-1]

    if position == 0:

        # Buy at lower band
        if close <= lower and rsi < 35:
            return "BUY"

        # Sell at upper band
        if close >= upper and rsi > 65:
            return "SELL"

    return None