def trend_signal(df_1m, df_5m, position):

    ema5 = df_1m["ema5"].iloc[-1]
    ema10 = df_1m["ema10"].iloc[-1]
    close_now = df_1m["close"].iloc[-1]
    close_prev = df_1m["close"].iloc[-2]

    ema20_5m_now = df_5m["ema20"].iloc[-1]
    ema20_5m_prev = df_5m["ema20"].iloc[-2]

    # 5m direction
    if ema20_5m_now > ema20_5m_prev:
        bias = "BULL"
    else:
        bias = "BEAR"

    if position == 0:

        # Long pullback
        if bias == "BULL" and ema5 > ema10 and close_now > close_prev:
            return "BUY"

        # Short pullback
        if bias == "BEAR" and ema5 < ema10 and close_now < close_prev:
            return "SELL"

    return None