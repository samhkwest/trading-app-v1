# paper/paper_engine.py

"""
Paper Trading Engine (Refactored)
---------------------------------------------------------

Now uses EXACT SAME:
- StrategyEngine
- ExecutionEngine
- PositionManager

This ensures backtest = paper parity.
"""

from futu import *
from datetime import datetime
import time

from strategy.strategy_engine import StrategyEngine
from execution.position_manager import PositionManager
from execution.execution_engine import ExecutionEngine

from risk.risk_manager import RiskManager
from risk.performance_tracker import PerformanceTracker

from config import HOST, PORT, KLINE_1M, KLINE_5M, INITIAL_CAPITAL


class PaperTrader:

    def __init__(self, code):

        self.code = code

        self.strategy = StrategyEngine()
        self.position_manager = PositionManager()
        self.execution = ExecutionEngine(self.position_manager)

        self.risk = RiskManager()
        self.performance = PerformanceTracker(INITIAL_CAPITAL)

        self.quote_ctx = OpenQuoteContext(host=HOST, port=PORT)
        self.quote_ctx.subscribe(code, [SubType.QUOTE])

    # ==========================================================
    # ✅ TICK HANDLER
    # ==========================================================

    def on_tick(self):

        if not self.risk.trading_enabled:
            return

        ret1, df_1m = self.quote_ctx.get_cur_kline(
            self.code, KLINE_1M, KLType.K_1M
        )
        ret2, df_5m = self.quote_ctx.get_cur_kline(
            self.code, KLINE_5M, KLType.K_5M
        )

        if ret1 != 0 or ret2 != 0:
            return

        current_time = datetime.now()
        last_price = df_1m["close"].iloc[-1]
        high = df_1m["high"].iloc[-1]
        low = df_1m["low"].iloc[-1]

        # ==========================================================
        # ✅ STRATEGY EVALUATION
        # ==========================================================
        decision = self.strategy.evaluate(
            df_1m,
            df_5m,
            self.position_manager.position,
            df_5m_full=df_5m
        )

        # ==========================================================
        # ✅ ENTRY
        # ==========================================================
        if (
            decision
            and self.position_manager.position == 0
            and self.risk.trading_enabled
        ):
            self.execution.process_entry(
                decision,
                last_price,
                current_time
            )

        # ==========================================================
        # ✅ EXIT
        # ==========================================================
        exit_result = self.execution.check_exit(
            high,
            low,
            current_time
        )

        if exit_result:

            pnl_hkd = exit_result["pnl_hkd"]
            direction = exit_result["direction"]

            self.risk.update_after_trade(pnl_hkd, current_time)

            trade_record = {
                "Direction": direction,
                "PnL (HKD)": pnl_hkd,
                "Equity": self.risk.equity,
                "Drawdown (HKD)": self.risk.get_drawdown(),
                "Drawdown (%)": self.risk.get_drawdown_pct(),
            }

            self.performance.record_trade(trade_record)

    # ==========================================================
    # ✅ MAIN LOOP
    # ==========================================================

    def run(self):

        while True:
            try:
                self.on_tick()
                time.sleep(1)

            except KeyboardInterrupt:
                self.performance.print_report()
                self.quote_ctx.close()
                break