# strategy/signal.py

"""
Signal Router
---------------------------------------------------------

Pure signal generation.
No filters.
No execution.
No risk.
"""

from config import TREND_SLOPE_THRESHOLD
from strategy.sweep_logic import sweep_signal
from strategy.trend_logic import trend_signal

def reset_regime_cache():
    """
    Reset regime cache before each backtest run.
    Prevents cross-run contamination.
    """
    global _cached_regime, _last_5m_bar_time
    _cached_regime = None
    _last_5m_bar_time = None

def generate_signal(df_1m, df_5m, position):

    if df_5m is None or len(df_5m) < 20:
        return None

    df5 = df_5m.copy()
    df5["ema20"] = df5["close"].ewm(span=20, adjust=False).mean()

    ema_now = df5["ema20"].iloc[-1]
    ema_prev = df5["ema20"].iloc[-10]

    slope = ema_now - ema_prev

    if abs(slope) >= TREND_SLOPE_THRESHOLD:
        return trend_signal(df_1m, df_5m, position)

    return sweep_signal(df_1m, df_5m, position)