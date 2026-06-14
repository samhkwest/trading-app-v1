# strategy/signal.py

from config import TREND_SLOPE_THRESHOLD
from strategy.sweep_logic import sweep_signal
from strategy.trend_logic import trend_signal
from strategy.reversal_logic import divergence_reversal  # NEW

def generate_signal(df_confirm, df_structure, position):
    """
    Signal router with priority:
    1. Trend continuation (strong slope)
    2. Divergence reversal (momentum divergence)
    3. Liquidity sweep (range trading)
    """
    
    if df_structure is None or len(df_structure) < 20:
        return None
    
    # Compute regime
    df5 = df_structure.copy()
    df5["ema20"] = df5["close"].ewm(span=20, adjust=False).mean()
    ema_now = df5["ema20"].iloc[-1]
    ema_prev = df5["ema20"].iloc[-10]
    slope = ema_now - ema_prev
    
    # Priority 1: Strong Trend
    if abs(slope) >= TREND_SLOPE_THRESHOLD:
        return trend_signal(df_confirm, df_structure, position)
    
    # Priority 2: Divergence Reversal (NEW)
    signal = divergence_reversal(df_confirm, df_structure, position)
    if signal:
        return signal
    
    # Priority 3: Sweep
    return sweep_signal(df_structure, position)