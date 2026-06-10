# backtest_engine.py

import os
import pandas as pd

from strategy.strategy_engine import StrategyEngine
from execution.position_manager import PositionManager
from execution.execution_engine import ExecutionEngine
from config import START_DATE, END_DATE, TIMEFRAME_CONFIG
from config import WARMUP_BARS, INITIAL_CAPITAL, POINT_VALUE
from risk.risk_manager import RiskManager
from risk.performance_tracker import PerformanceTracker

print("ENGINE FILE LOADED")


def run_backtest(provider):

    strategy = StrategyEngine()
    position_manager = PositionManager()
    execution = ExecutionEngine(position_manager)

    risk = RiskManager()
    performance = PerformanceTracker(
        INITIAL_CAPITAL,
        period=f"{START_DATE} - {END_DATE}"
    )

    trades = []

    entry_tf = TIMEFRAME_CONFIG["entry"]
    structure_tf = TIMEFRAME_CONFIG["structure"]
    trend_tf = TIMEFRAME_CONFIG["trend"]

    df_entry_full = provider.get_candles(entry_tf)

    # ✅ DO NOT use full trend history (prevents look-ahead bias)
    # df_trend_full = provider.get_candles(trend_tf)

    for i in range(WARMUP_BARS, len(df_entry_full)):

        df_entry_slice = df_entry_full.iloc[:i+1].copy()

        current_bar = df_entry_slice.iloc[-1]
        current_time = current_bar["datetime"]
        current_close = current_bar["close"]
        current_high = current_bar["high"]
        current_low = current_bar["low"]

        risk.update_after_trade(0, current_time)

        df_structure_slice = provider.get_candles(
            structure_tf,
            up_to_time=current_time
        )

        df_trend_slice = provider.get_candles(
            trend_tf,
            up_to_time=current_time
        )

        # ✅ Ensure enough structure data
        if len(df_structure_slice) < WARMUP_BARS:
            continue

        # ✅ Ensure enough trend data for EMA20 + slope calculation stability
        # EMA20 requires ~20 bars, slope uses shift(10)
        if len(df_trend_slice) < 30:
            continue

        # -------------------------------------------------
        # ✅ STRATEGY
        # -------------------------------------------------
        decision = strategy.evaluate(
            df_entry_slice,
            df_structure_slice,
            position_manager.position,
            df_trend=df_trend_slice
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
                "Entry EMA20 Slope": round(exit_result["entry_slope"], 2),
                "Entry ATR": round(exit_result["entry_atr"], 2)
            }

            trades.append(trade_record)
            performance.record_trade(trade_record)

    # ----------------------------------------------------------
    # ✅ FORCE CLOSE OPEN POSITION AT END OF BACKTEST
    # ----------------------------------------------------------
    if position_manager.position != 0:

        final_price = df_entry_full["close"].iloc[-1]
        final_time = df_entry_full["datetime"].iloc[-1]

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
            "Entry EMA20 Slope": round(entry_slope, 2),
            "Entry ATR": round(entry_atr, 2)
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