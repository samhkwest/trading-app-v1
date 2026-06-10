# strategy/signal.py

"""
Signal Router
---------------------------------------------------------

Pure signal generation.
No filters.
No execution.
No risk.

Updated:
- Sweep evaluated FIRST (can trigger inside strong trend)
- Trend evaluated only if sweep does not trigger
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


def generate_signal(df_entry, df_structure, position):

    # ✅ Require enough completed structure bars
    if df_structure is None or len(df_structure) < 30:
        return None

    # ---------------------------------------------------------
    # ✅ 1) ALWAYS CHECK SWEEP FIRST
    # ---------------------------------------------------------
    sweep = sweep_signal(df_structure, position)
    if sweep is not None:
        return sweep

    # ---------------------------------------------------------
    # ✅ 2) Compute EMA20 slope on structure timeframe
    # ---------------------------------------------------------
    ema = df_structure["close"].ewm(span=20, adjust=False).mean()

    ema_now = ema.iloc[-2]
    ema_prev = ema.iloc[-11]

    slope = ema_now - ema_prev

    if slope is None or slope != slope:
        return None

    # ---------------------------------------------------------
    # ✅ 3) Only allow trend continuation if strong slope
    # ---------------------------------------------------------
    if abs(slope) >= TREND_SLOPE_THRESHOLD:
        return trend_signal(df_entry, df_structure, position)

    return None