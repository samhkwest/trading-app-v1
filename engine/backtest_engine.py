# backtest_engine.py

import os
import pandas as pd

from strategy.strategy_engine import StrategyEngine
from execution.position_manager import PositionManager
from execution.execution_engine import ExecutionEngine
#from strategy.signal import reset_regime_cache
from config import START_DATE, END_DATE

from config import (
    WARMUP_BARS,
    INITIAL_CAPITAL,
    POINT_VALUE
)

from risk.risk_manager import RiskManager
from risk.performance_tracker import PerformanceTracker

print("ENGINE FILE LOADED")


def run_backtest(df_1m, df_5m):

    #reset_regime_cache()

    strategy = StrategyEngine()
    position_manager = PositionManager()
    execution = ExecutionEngine(position_manager)

    risk = RiskManager()
    #performance = PerformanceTracker(INITIAL_CAPITAL)
    performance = PerformanceTracker(
        INITIAL_CAPITAL,
        period=f"{START_DATE} - {END_DATE}"
    )
    trades = []

    # ✅ Precompute EMA20 slope distribution
    df_5m_copy = df_5m.copy()
    df_5m_copy["ema20"] = df_5m_copy["close"].ewm(span=20, adjust=False).mean()
    df_5m_copy["ema20_slope"] = (
        df_5m_copy["ema20"] - df_5m_copy["ema20"].shift(10)
    )

    for i in range(WARMUP_BARS, len(df_1m)):

        df_1m_slice = df_1m.iloc[:i+1].copy()

        current_bar = df_1m_slice.iloc[-1]
        current_time = current_bar["datetime"]
        current_close = current_bar["close"]
        current_high = current_bar["high"]
        current_low = current_bar["low"]

        risk.update_after_trade(0, current_time)

        df_5m_slice = df_5m[
            df_5m["datetime"] <= current_time
        ].copy()

        if len(df_5m_slice) < WARMUP_BARS:
            continue

        # -------------------------------------------------
        # ✅ STRATEGY
        # -------------------------------------------------

        decision = strategy.evaluate(
            df_1m_slice,
            df_5m_slice,
            position_manager.position,
            df_5m_full=df_5m_copy
        )

        if (
            decision
            and position_manager.position == 0
            and risk.trading_enabled
        ):
            print(f"Order Executed → {decision['side']} @ {current_time}")

            execution.process_entry(
                decision,
                current_close,
                current_time
            )

        # -------------------------------------------------
        # ✅ EXIT CHECK
        # -------------------------------------------------

        exit_result = execution.check_exit(
            current_high,
            current_low,
            current_time
        )

        if exit_result:

            pnl_hkd = exit_result["pnl_hkd"]

            risk.update_after_trade(pnl_hkd, exit_result["exit_time"])

            stop_flag = "Y" if not risk.trading_enabled else ""

            # ✅ FIX: Use exit_result instead of position_manager
            trade_record = {
                "Direction": exit_result["direction"],
                "Entry Time": exit_result["entry_time"],
                "Exit Time": exit_result["exit_time"],
                "Entry Price": exit_result["entry_price"],
                "Exit Price": exit_result["exit_price"],
                "PnL (HKD)": pnl_hkd,
                "Equity": risk.equity,
                "Equity Peak": risk.equity_peak,
                "Drawdown (HKD)": risk.get_drawdown(),
                "Drawdown (%)": risk.get_drawdown_pct(),
                "SL (Y/N)": stop_flag,
                "Entry EMA20 Slope": round(exit_result["entry_slope"],2),
                #"Exit EMA20 Slope": None,
                "Entry ATR": round(exit_result["entry_atr"],2),
                #"Exit ATR": None
            }

            trades.append(trade_record)
            performance.record_trade(trade_record)

    # ----------------------------------------------------------
    # ✅ FORCE CLOSE
    # ----------------------------------------------------------

    if position_manager.position != 0:

        final_price = df_1m["close"].iloc[-1]
        final_time = df_1m["datetime"].iloc[-1]

        entry_price = position_manager.entry_price
        entry_time = position_manager.entry_time
        entry_slope = position_manager.entry_slope
        entry_atr = position_manager.entry_atr

        position = position_manager.position
        direction = "LONG" if position == 1 else "SHORT"

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
            "PnL (HKD)": pnl_hkd,
            "Equity": risk.equity,
            "Equity Peak": risk.equity_peak,
            "Drawdown (HKD)": risk.get_drawdown(),
            "Drawdown (%)": risk.get_drawdown_pct(),
            "SL (Y/N)": stop_flag,
            "Entry EMA20 Slope": round(entry_slope,2),
            #"Exit EMA20 Slope": None,
            "Entry ATR": round(entry_atr,2),
            #"Exit ATR": None
        }

        trades.append(trade_record)
        performance.record_trade(trade_record)

    # ----------------------------------------------------------
    # ✅ SAVE LOG
    # ----------------------------------------------------------

    df_trades = pd.DataFrame(trades)

    if not os.path.exists("log"):
        os.makedirs("log")

    if not df_trades.empty:
        df_trades.to_csv("log/backtest_trade_log.csv", index=False)
    else:
        df_trades = pd.DataFrame(columns=[
            "Direction",
            "Entry Time",
            "Exit Time",
            "Entry Price",
            "Exit Price",
            "PnL (HKD)",
            "Equity",
            "Equity Peak",
            "Drawdown (HKD)",
            "Drawdown (%)",
            "SL (Y/N)",
            "Entry EMA20 Slope",
            #"Exit EMA20 Slope",
            "Entry ATR",
            #"Exit ATR"
        ])
        df_trades.to_csv("log/backtest_trade_log.csv", index=False)

    metrics = performance.generate_metrics()

    return df_trades, metrics