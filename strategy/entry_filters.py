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

This module contains NO strategy logic.
Only qualification logic.

This ensures:
- Clean separation of signal vs filter
- Identical behavior between backtest and paper
"""

import pandas as pd
from config import MIN_ENTRY_ATR


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

def slope_quantile_filter(current_slope, df_5m_full):
    """
    Block trades when slope is too strong relative to
    historical slope distribution (top 25%).

    This replicates your previous backtest_engine logic exactly.
    """

    if current_slope is None:
        return False

    df_copy = df_5m_full.copy()

    df_copy["ema20"] = df_copy["close"].ewm(span=20, adjust=False).mean()
    df_copy["ema20_slope"] = df_copy["ema20"] - df_copy["ema20"].shift(10)

    slope_q3 = df_copy["ema20_slope"].quantile(0.75)

    if current_slope >= slope_q3:
        return False

    return True