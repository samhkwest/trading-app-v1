def warrant_strength(call_vol, put_vol):

    total = call_vol + put_vol
    if total == 0:
        return "NEUTRAL"

    bull_ratio = call_vol / total
    bear_ratio = put_vol / total

    if bull_ratio > 0.65:
        return "BULLISH"

    if bear_ratio > 0.65:
        return "BEARISH"

    return "NEUTRAL"