# backtest_engine.py

import os
import pandas as pd
from strategy.signal import generate_signal, reset_regime_cache
from config import (
    WARMUP_BARS,
    POINT_VALUE,
    TAKE_PROFIT,
    STOP_LOSS,
    ORDER_TYPE,
    INITIAL_CAPITAL,
    MIN_ENTRY_ATR
)

from risk.risk_manager import RiskManager
from risk.performance_tracker import PerformanceTracker

print("ENGINE FILE LOADED")


def run_backtest(df_1m, df_5m):

    reset_regime_cache()
    risk = RiskManager()
    performance = PerformanceTracker(INITIAL_CAPITAL)

    trades = []

    position = 0
    entry_price = 0
    entry_time = None
    direction = None
    entry_slope = None
    entry_atr = None

    # ✅ Precompute EMA20 slope distribution (for dynamic regime filter)
    df_5m_copy = df_5m.copy()
    df_5m_copy["ema20"] = df_5m_copy["close"].ewm(span=20, adjust=False).mean()
    df_5m_copy["ema20_slope"] = df_5m_copy["ema20"] - df_5m_copy["ema20"].shift(10)

    # Start after warmup
    for i in range(WARMUP_BARS, len(df_1m)):

        # -------------------------------------------------
        # 1) Slice 1-minute data up to current bar
        # -------------------------------------------------
        df_1m_slice = df_1m.iloc[:i+1].copy()

        current_bar = df_1m_slice.iloc[-1]
        current_time = current_bar["datetime"]
        current_close = current_bar["close"]
        current_high = current_bar["high"]
        current_low = current_bar["low"]

        # ✅ Force daily reset check (no pnl impact)
        risk.update_after_trade(0, current_time)

        # -------------------------------------------------
        # 2) Slice ONLY closed 5-minute bars
        # -------------------------------------------------
        df_5m_slice = df_5m[
            df_5m["datetime"] <= current_time
        ].copy()

        if len(df_5m_slice) < WARMUP_BARS:
            continue

        # -------------------------------------------------
        # ✅ Compute EMA20 slope (5m)
        # -------------------------------------------------
        df_5m_slice["ema20"] = df_5m_slice["close"].ewm(span=20, adjust=False).mean()

        if len(df_5m_slice) >= 20:
            ema_now = df_5m_slice["ema20"].iloc[-1]
            ema_prev = df_5m_slice["ema20"].iloc[-10]
            ema20_slope = ema_now - ema_prev
        else:
            ema20_slope = None

        # -------------------------------------------------
        # ✅ Compute ATR (5m)
        # -------------------------------------------------
        if len(df_5m_slice) >= 15:
            high = df_5m_slice["high"]
            low = df_5m_slice["low"]
            close = df_5m_slice["close"]

            tr = pd.concat([
                high - low,
                (high - close.shift()).abs(),
                (low - close.shift()).abs()
            ], axis=1).max(axis=1)

            atr = tr.rolling(14).mean().iloc[-1]
        else:
            atr = None

        # -------------------------------------------------
        # 3) Generate signal
        # -------------------------------------------------
        signal = generate_signal(df_1m_slice, df_5m_slice, position)

        # -------------------------------------------------
        # 4) Entry logic
        # -------------------------------------------------
        if position == 0 and risk.trading_enabled and signal in ["BUY", "SELL"]:

            # ✅ ATR FILTER
            if atr is None or atr <= MIN_ENTRY_ATR:
                continue

            # SLOPE REGIME FILTER
            slope_q3 = df_5m_copy["ema20_slope"].quantile(0.75)
            if ema20_slope is None or ema20_slope >= slope_q3:
                continue

            entry_slope = ema20_slope
            entry_atr = atr

            print(f"Order Executed → {signal} @ {current_time}")

            position = 1 if signal == "BUY" else -1
            direction = "LONG" if signal == "BUY" else "SHORT"
            entry_price = current_close
            entry_time = current_time

        # -------------------------------------------------
        # 5) Exit logic (TP / SL)
        # -------------------------------------------------
        if position != 0:

            if position == 1:

                tp_price = entry_price + TAKE_PROFIT
                sl_price = entry_price - STOP_LOSS

                tp_hit = current_high >= tp_price
                sl_hit = current_low <= sl_price

                exit_price = None

                if tp_hit and sl_hit:
                    exit_price = sl_price
                elif tp_hit:
                    exit_price = tp_price
                elif sl_hit:
                    exit_price = sl_price

            elif position == -1:

                tp_price = entry_price - TAKE_PROFIT
                sl_price = entry_price + STOP_LOSS

                tp_hit = current_low <= tp_price
                sl_hit = current_high >= sl_price

                exit_price = None

                if tp_hit and sl_hit:
                    exit_price = sl_price
                elif tp_hit:
                    exit_price = tp_price
                elif sl_hit:
                    exit_price = sl_price

            if exit_price is not None:

                pnl_points = (exit_price - entry_price) * position
                pnl_hkd = pnl_points * POINT_VALUE

                risk.update_after_trade(pnl_hkd, current_time)

                stop_flag = "Y" if not risk.trading_enabled else ""

                trade_record = {
                    "Direction": direction,
                    "Entry Time": entry_time,
                    "Exit Time": current_time,
                    "Entry Price": entry_price,
                    "Exit Price": exit_price,
                    #"PnL (Points)": pnl_points,
                    "PnL (HKD)": pnl_hkd,
                    "Equity": risk.equity,
                    "Equity Peak": risk.equity_peak,
                    "Drawdown (HKD)": risk.get_drawdown(),
                    "Drawdown (%)": risk.get_drawdown_pct(),
                    "Stop Loss (Y/N)": stop_flag,
                    "Entry EMA20 Slope": entry_slope,
                    "Exit EMA20 Slope": ema20_slope,
                    "Entry ATR": entry_atr,
                    "Exit ATR": atr
                }

                trades.append(trade_record)
                performance.record_trade(trade_record)

                position = 0
                direction = None
                entry_price = 0
                entry_time = None
                entry_slope = None
                entry_atr = None

    # ----------------------------------------------------------
    # 6) Close open position at end of backtest
    # ----------------------------------------------------------
    if position != 0:

        final_price = df_1m["close"].iloc[-1]
        final_time = df_1m["datetime"].iloc[-1]

        pnl_points = (final_price - entry_price) * position
        pnl_hkd = pnl_points * POINT_VALUE

        risk.update_after_trade(pnl_hkd, final_time)

        stop_flag = "Y" if not risk.trading_enabled else ""

        trade_record = {
            "Direction": direction,
            "Entry Time": entry_time,
            "Exit Time": final_time,
            "Entry Price": entry_price,
            "Exit Price": final_price,
            #"PnL (Points)": pnl_points,
            "PnL (HKD)": pnl_hkd,
            "Equity": risk.equity,
            "Equity Peak": risk.equity_peak,
            "Drawdown (HKD)": risk.get_drawdown(),
            "Drawdown (%)": risk.get_drawdown_pct(),
            "Stop Loss (Y/N)": stop_flag,
            "Entry EMA20 Slope": entry_slope,
            "Exit EMA20 Slope": ema20_slope,
            "Entry ATR": entry_atr,
            "Exit ATR": atr
        }

        trades.append(trade_record)
        performance.record_trade(trade_record)

    # ----------------------------------------------------------
    # 7) Save trade log
    # ----------------------------------------------------------
    df_trades = pd.DataFrame(trades)

    if not os.path.exists("log"):
        os.makedirs("log")

    if not df_trades.empty:
        df_trades.to_csv("log/backtest_trade_log.csv", index=False)
    else:
        # create empty file with headers to avoid diagnostics crash
        df_trades = pd.DataFrame(columns=[
            "Direction",
            "Entry Time",
            "Exit Time",
            "Entry Price",
            "Exit Price",
            #"PnL (Points)",
            "PnL (HKD)",
            "Equity",
            "Equity Peak",
            "Drawdown (HKD)",
            "Drawdown (%)",
            "Stop Loss (Y/N)",
            "Entry EMA20 Slope",
            "Exit EMA20 Slope",
            "Entry ATR",
            "Exit ATR"
        ])
        df_trades.to_csv("log/backtest_trade_log.csv", index=False)

    # ----------------------------------------------------------
    # 8) Generate metrics
    # ----------------------------------------------------------
    metrics = performance.generate_metrics()

    return df_trades, metrics