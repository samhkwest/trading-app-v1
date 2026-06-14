# strategy/reversal_logic.py

"""
Divergence Reversal Detection
----------------------------------------------
Catches reversals when short-term (1m) momentum
contradicts medium-term (5m) trend direction.

Technical: Momentum Divergence / Hidden Divergence
Mechanism: MTF (Multi-Timeframe) structure conflict
"""

import pandas as pd
from config import DIVERGENCE_MIN_SLOPE

def divergence_reversal(df_confirm, df_structure, position):
    """
    Detect reversal when 1m structure opposes 5m trend.
    
    Examples:
    - Downtrend (slope < 0) + bullish 1m (EMA5>EMA10) → BUY
    - Uptrend (slope > 0) + bearish 1m (EMA5<EMA10) → SELL
    
    Returns: "BUY", "SELL", or None
    """
    
    if position != 0:
        return None
    
    if len(df_confirm) < 10 or len(df_structure) < 20:
        return None
    
    # -------------------------------------------------
    # 1m Structure (Short-term momentum)
    # -------------------------------------------------
    df1 = df_confirm.copy()
    df1["ema5"] = df1["close"].ewm(span=5, adjust=False).mean()
    df1["ema10"] = df1["close"].ewm(span=10, adjust=False).mean()
    
    ema5 = df1["ema5"].iloc[-1]
    ema10 = df1["ema10"].iloc[-1]
    close_now = df1["close"].iloc[-1]
    close_prev = df1["close"].iloc[-2]
    
    bullish_1m = (ema5 > ema10) and (close_now > close_prev)
    bearish_1m = (ema5 < ema10) and (close_now < close_prev)
    
    # -------------------------------------------------
    # 5m Trend (Medium-term direction)
    # -------------------------------------------------
    df5 = df_structure.copy()
    df5["ema20"] = df5["close"].ewm(span=20, adjust=False).mean()
    
    ema_now = df5["ema20"].iloc[-1]
    ema_prev = df5["ema20"].iloc[-10]
    slope = ema_now - ema_prev
    
    # -------------------------------------------------
    # Divergence Detection
    # -------------------------------------------------
    
    # Bullish Divergence: Downtrend + Bullish 1m
    if slope < -DIVERGENCE_MIN_SLOPE and bullish_1m:
        return "BUY"  # ← Your 24200 case!
    
    # Bearish Divergence: Uptrend + Bearish 1m
    if slope > -DIVERGENCE_MIN_SLOPE and bearish_1m:
        return "SELL"
    
    return None