# strategy/entry_filters.py

"""
Entry Filters Module
---------------------------------------------------------

Purpose:
Centralize all entry qualification filters that were
previously scattered inside backtest_engine.

Responsibilities:
- ATR volatility filter
- EMA20 slope quantile filter (dynamic regime filter)
- Volume confirmation filter (NEW)

This module contains NO strategy logic.
Only qualification logic.

This ensures:
- Clean separation of signal vs filter
- Identical behavior between backtest and paper
"""

import pandas as pd
from config import MIN_ENTRY_ATR, VOLUME_MA_PERIOD, VOLUME_MULTIPLIER


# ==========================================================
# ✅ ATR FILTER
# ==========================================================

def atr_filter(atr_value):
    """
    ATR must be strictly greater than configured threshold.
    """

    if atr_value is None:
        return False

    if atr_value <= MIN_ENTRY_ATR:
        return False

    return True


# ==========================================================
# ✅ EMA20 SLOPE QUANTILE FILTER
# ==========================================================

def slope_quantile_filter(current_slope, df_5m_full, ema20_series=None):
    """
    Block trades when slope is too strong relative to
    historical slope distribution (top 25%).

    This replicates your previous backtest_engine logic exactly.
    """

    if current_slope is None:
        return False

    df_copy = df_5m_full.copy()

    if ema20_series is not None:
        df_copy["ema20"] = ema20_series
    else:
        df_copy["ema20"] = df_copy["close"].ewm(span=20, adjust=False).mean()
    df_copy["ema20_slope"] = df_copy["ema20"] - df_copy["ema20"].shift(10)

    slope_q3 = df_copy["ema20_slope"].quantile(0.75)

    if current_slope >= slope_q3:
        return False

    return True


# ==========================================================
# ✅ VOLUME CONFIRMATION FILTER
# ==========================================================

def volume_confirmation_filter(df_5m, print_debug=False):
    """
    Checks if current candle volume confirms the move.
    
    Rules:
    - Current volume must exceed MA(volume) by multiplier
    - This ensures institutional participation, not noise
    
    Args:
        df_5m: 5m OHLCV dataframe
        print_debug: Print debug info
    
    Returns:
        bool: True if volume confirms, False otherwise
    
    Example:
        >>> volume_confirmation_filter(df, print_debug=True)
        [Volume] Current: 15000 | MA: 12000 | Ratio: 1.25x
        False  # Blocked because 1.25x < 1.3x multiplier
    """
    
    if df_5m is None or len(df_5m) < VOLUME_MA_PERIOD:
        if print_debug:
            print(f"[Volume] Insufficient data: {len(df_5m) if df_5m is not None else 0} bars")
        return False
    
    # Ensure volume column exists
    if "volume" not in df_5m.columns:
        if print_debug:
            print("[ERROR] Volume column not found in dataframe")
        return False
    
    # Calculate volume MA
    df_copy = df_5m.copy()
    df_copy["volume_ma"] = df_copy["volume"].rolling(window=VOLUME_MA_PERIOD).mean()
    
    current_volume = df_copy["volume"].iloc[-1]
    volume_ma = df_copy["volume_ma"].iloc[-1]
    
    # Handle division by zero
    volume_ratio = current_volume / volume_ma if volume_ma > 0 else 0
    
    if print_debug:
        print(f"[Volume] Current: {current_volume:.0f} | MA: {volume_ma:.0f} | Ratio: {volume_ratio:.2f}x | Threshold: {VOLUME_MULTIPLIER}x")
    
    # Pass if current volume exceeds MA by multiplier
    passes = current_volume > (volume_ma * VOLUME_MULTIPLIER)
    
    return passes
