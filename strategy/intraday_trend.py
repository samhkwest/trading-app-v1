# intraday_trend.py
# ------------------------------------------------------
# Intraday Trend Regime Detection
# ------------------------------------------------------
# This module encapsulates strong directional bias detection.
# It can be plugged into any strategy engine without modifying
# signal-generation logic.
# ------------------------------------------------------

import pandas as pd
from config import TREND_SLOPE_THRESHOLD

def detect_intraday_regime(
    df5: pd.DataFrame,
    ema_now: float,
    slope: float,
    slope_threshold: float = TREND_SLOPE_THRESHOLD,
    persistence_bars: int = 5,
    min_bullish: int = 4,
    min_bearish: int = 4,
):
    """
    Detect strong intraday directional regime.

    Parameters:
    ----------
    df5 : 5-minute dataframe
    ema_now : current EMA value
    slope : EMA slope value
    slope_threshold : minimum slope magnitude to qualify as strong
    persistence_bars : lookback window for persistence
    min_bullish : required bullish bars for strong uptrend
    min_bearish : required bearish bars for strong downtrend

    Returns:
    -------
    regime : str
        "UP_ONLY"
        "DOWN_ONLY"
        "NEUTRAL"
    """

    # ------------------------------------------------------
    # Safety Check
    # ------------------------------------------------------
    if len(df5) < persistence_bars:
        return "NEUTRAL"

    recent = df5.iloc[-persistence_bars:]

    bullish_bars = (recent["close"] > recent["open"]).sum()
    bearish_bars = (recent["close"] < recent["open"]).sum()

    price_now = df5["close"].iloc[-1]

    price_above_ema = price_now > ema_now
    price_below_ema = price_now < ema_now

    # ------------------------------------------------------
    # Strong Uptrend Definition
    # ------------------------------------------------------
    strong_uptrend = (
        slope > slope_threshold and
        bullish_bars >= min_bullish and
        price_above_ema
    )

    # ------------------------------------------------------
    # Strong Downtrend Definition
    # ------------------------------------------------------
    strong_downtrend = (
        slope < -slope_threshold and
        bearish_bars >= min_bearish and
        price_below_ema
    )

    # ------------------------------------------------------
    # Regime Classification
    # ------------------------------------------------------
    if strong_uptrend:
        return "UP_ONLY"
    elif strong_downtrend:
        return "DOWN_ONLY"
    else:
        return "NEUTRAL"