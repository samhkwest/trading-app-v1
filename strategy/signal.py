# strategy/signal.py

from config import (
    ENABLE_BREAKOUT,
    ENABLE_BOTTOM,
    ENABLE_TRANSITIONAL,
    REGIME_STRATEGY_MAP,
    STRATEGY_PRIORITY,
    PRINT_DEBUG_REGIME,
    PRINT_DEBUG_SIGNAL
)

from strategy.regime import detect_regime
from strategy.breakout_logic import breakout_signal
from strategy.bottom_logic import bottom_signal
from strategy.transitional_logic import transitional_signal
from strategy.place_order import order_signal

# ==========================================================
# Regime Cache (Multi-Timeframe Optimization)
# ==========================================================

_cached_regime = None
_last_5m_bar_time = None


def reset_regime_cache():
    """
    Reset regime cache before each backtest run.
    Prevents cross-run contamination.
    """
    global _cached_regime, _last_5m_bar_time
    _cached_regime = None
    _last_5m_bar_time = None


# ----------------------------------------------------------
# Strategy Execution Dispatcher
# ----------------------------------------------------------

def _execute_strategy(strategy_name, df_1m, df_5m, position):

    if strategy_name == "BREAKOUT" and ENABLE_BREAKOUT:
        return breakout_signal(df_1m, df_5m, position)

    if strategy_name == "BOTTOM" and ENABLE_BOTTOM:
        return bottom_signal(df_5m, position)

    if strategy_name == "TRANSITIONAL" and ENABLE_TRANSITIONAL:
        return transitional_signal(df_1m, df_5m, position)

    return None


# ----------------------------------------------------------
# Main Signal Router
# ----------------------------------------------------------
def generate_signal(df_1m, df_5m, position):

    signal = order_signal(df_1m, df_5m, position)

    '''
    if signal and PRINT_DEBUG_SIGNAL:
        print(f"[Signal] Order → {signal}")
    '''

    return signal

"""
def generate_signal(df_1m, df_5m, position):

    global _cached_regime
    global _last_5m_bar_time

    # Safety check
    if df_5m.empty:
        return None

    # ------------------------------------------------------
    # 1️⃣ Detect current market regime (Optimized)
    # ------------------------------------------------------

    current_5m_time = df_5m.iloc[-1]["datetime"]

    # Only recompute regime when a new 5m candle appears
    if _last_5m_bar_time != current_5m_time:

        _cached_regime = detect_regime(df_5m)
        _last_5m_bar_time = current_5m_time

        if PRINT_DEBUG_REGIME:
            print(f"[{current_5m_time}] [Regime Update] {_cached_regime}")

    regime = _cached_regime

    # ------------------------------------------------------
    # 2️⃣ Get mapped strategies for this regime
    # ------------------------------------------------------

    strategies = REGIME_STRATEGY_MAP.get(regime, [])

    if not strategies:
        return None

    # ------------------------------------------------------
    # 3️⃣ Apply priority ordering
    # ------------------------------------------------------

    ordered_strategies = sorted(
        strategies,
        key=lambda x: STRATEGY_PRIORITY.index(x)
        if x in STRATEGY_PRIORITY else 999
    )

    # ------------------------------------------------------
    # 4️⃣ Execute in order, return first valid signal
    # ------------------------------------------------------

    for strategy_name in ordered_strategies:

        signal = _execute_strategy(
            strategy_name,
            df_1m,
            df_5m,
            position
        )

        if signal:

            if PRINT_DEBUG_SIGNAL:
                print(f"[Signal] {strategy_name} → {signal}")

            return signal

    return None
"""