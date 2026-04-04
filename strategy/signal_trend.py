import pandas as pd
from strategy.warrant_filter import warrant_strength
from strategy.regime import detect_regime
from strategy.trend_logic import trend_signal
from strategy.range_logic import range_signal

def calculate_ema(df):
    df["ema5"] = df["close"].ewm(span=5).mean()
    df["ema10"] = df["close"].ewm(span=10).mean()
    df["ema20"] = df["close"].ewm(span=20).mean()
    return df


def get_bias(df_5m):
    df_5m = calculate_ema(df_5m)

    ema20_now = df_5m["ema20"].iloc[-1]
    ema20_prev = df_5m["ema20"].iloc[-2]

    if ema20_now > ema20_prev:
        return "BULL"
    elif ema20_now < ema20_prev:
        return "BEAR"

    return None

def generate_signal_warrant(df_1m, df_5m, position, call_vol, put_vol):

    df_1m = calculate_ema(df_1m)
    bias = get_bias(df_5m)

    ema5 = df_1m["ema5"].iloc[-1]
    ema10 = df_1m["ema10"].iloc[-1]
    ema20 = df_1m["ema20"].iloc[-1]

    close_now = df_1m["close"].iloc[-1]
    close_prev = df_1m["close"].iloc[-2]

    warrant_bias = warrant_strength(call_vol, put_vol)

    # ENTRY
    if position == 0:

        # Long
        if bias == "BULL" and warrant_bias == "BULLISH":
            if ema5 > ema10 and close_now > close_prev:
                return "BUY"

        # Short
        if bias == "BEAR" and warrant_bias == "BEARISH":
            if ema5 < ema10 and close_now < close_prev:
                return "SELL"

    # EXIT LONG
    if position == 1:
        if ema5 < ema10:
            return "SELL"

    # EXIT SHORT
    if position == -1:
        if ema5 > ema10:
            return "BUY"

    return None

def generate_signal(df_1m, df_5m, position):

    regime = detect_regime(df_5m)

    if regime == "TREND":
        return trend_signal(df_1m, df_5m, position)

    elif regime == "RANGE":
        return range_signal(df_5m, position)

    return None