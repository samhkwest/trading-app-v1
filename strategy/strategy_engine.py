# strategy/strategy_engine.py

import pandas as pd
from strategy.signal import generate_signal
from strategy.entry_filters import atr_filter, slope_quantile_filter
#from strategy.intraday_bias import IntradayBias
from strategy.intraday_trend import detect_intraday_regime
from config import TREND_SLOPE_THRESHOLD, ENABLE_LONG, ENABLE_SHORT

class StrategyEngine:

    #def __init__(self):
        #self.bias_engine = IntradayBias()

    # ==========================================================
    # ✅ MAIN EVALUATION ENTRY
    # ==========================================================

    def evaluate(self, df_1m, df_5m, position, df_5m_full=None):

        if df_5m is None or len(df_5m) < 20:
            return None

        # ------------------------------------------------------
        # ✅ Update Intraday Bias
        # ------------------------------------------------------
        #self.bias_engine.update(df_5m)

        # ------------------------------------------------------
        # ✅ Compute EMA20 slope (5m)
        # ------------------------------------------------------
        df5 = df_5m.copy()
        df5["ema20"] = df5["close"].ewm(span=20, adjust=False).mean()

        ema_now = df5["ema20"].iloc[-1]
        ema_prev = df5["ema20"].iloc[-10]
        slope = ema_now - ema_prev

        # ------------------------------------------------------
        # ✅ Compute ATR (5m)
        # ------------------------------------------------------
        atr = self._compute_atr(df_5m)

        # ------------------------------------------------------
        # ✅ Generate raw signal
        # ------------------------------------------------------
        signal = generate_signal(df_1m, df_5m, position)

        if signal not in ["BUY", "SELL"]:
            return None

        # ------------------------------------------------------
        # ✅ Directional Permission Filter (Intraday Bias)
        # ------------------------------------------------------
        #if not self.bias_engine.allow(signal):
        #    return None

        # ------------------------------------------------------
        # ✅ Entry Filters
        # ------------------------------------------------------
        if not atr_filter(atr):
            return None

        if df_5m_full is not None:
            if not slope_quantile_filter(slope, df_5m_full):
                return None
            
        '''
        if abs(slope) < TREND_SLOPE_THRESHOLD:
            if df_5m_full is not None:
                if not slope_quantile_filter(slope, df_5m_full):
                    return None
        '''

        # ------------------------------------------------------
        # ✅ Entry Approved
        # ------------------------------------------------------
        return {
            "action": "ENTER",
            "side": signal,
            "slope": slope,
            "atr": atr
        }

    # ==========================================================
    # ✅ ATR COMPUTATION
    # ==========================================================

    def _compute_atr(self, df_5m):

        if len(df_5m) < 15:
            return None

        high = df_5m["high"]
        low = df_5m["low"]
        close = df_5m["close"]

        tr = pd.concat([
            high - low,
            (high - close.shift()).abs(),
            (low - close.shift()).abs()
        ], axis=1).max(axis=1)

        atr = tr.rolling(14).mean().iloc[-1]

        return atr