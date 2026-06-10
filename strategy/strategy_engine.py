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

    def evaluate(self, df_entry, df_structure, position, df_trend=None):

        # ✅ Require sufficient structure bars
        if df_structure is None or len(df_structure) < 30:
            return None

        # ------------------------------------------------------
        # ✅ Update Intraday Bias
        # ------------------------------------------------------
        #self.bias_engine.update(df_structure)

        # ------------------------------------------------------
        # ✅ Compute EMA20 slope (structure TF)
        # ------------------------------------------------------
        df_struct = df_structure.copy()
        df_struct["ema20"] = df_struct["close"].ewm(span=20, adjust=False).mean()

        # slope uses shift(10) → need stability
        ema_now = df_struct["ema20"].iloc[-1]
        ema_prev = df_struct["ema20"].iloc[-10]
        slope = ema_now - ema_prev

        # Guard against NaN slope
        if pd.isna(slope):
            return None

        # ------------------------------------------------------
        # ✅ Compute ATR (structure TF)
        # ------------------------------------------------------
        atr = self._compute_atr(df_structure)

        # ------------------------------------------------------
        # ✅ Generate raw signal
        # ------------------------------------------------------
        signal = generate_signal(df_entry, df_structure, position)

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

        # ✅ Dynamic slope quantile filter (no future leakage)
        if df_trend is not None and len(df_trend) >= 30:

            df_full = df_trend.copy()
            df_full["ema20"] = df_full["close"].ewm(span=20, adjust=False).mean()
            df_full["ema20_slope"] = (
                df_full["ema20"] - df_full["ema20"].shift(10)
            )

            df_full = df_full.dropna(subset=["ema20_slope"])

            if len(df_full) >= 20:
                if not slope_quantile_filter(slope, df_full):
                    return None

        '''
        if abs(slope) < TREND_SLOPE_THRESHOLD:
            if df_trend is not None:
                if not slope_quantile_filter(slope, df_trend):
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

    def _compute_atr(self, df_structure):

        if len(df_structure) < 15:
            return None

        high = df_structure["high"]
        low = df_structure["low"]
        close = df_structure["close"]

        tr = pd.concat([
            high - low,
            (high - close.shift()).abs(),
            (low - close.shift()).abs()
        ], axis=1).max(axis=1)

        atr = tr.rolling(14).mean().iloc[-1]

        return atr