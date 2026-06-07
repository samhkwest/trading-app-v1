# engine/paper_engine.py

from futu import *
from datetime import datetime, time as dtime
import time
import os

from strategy.strategy_engine import StrategyEngine
from execution.position_manager import PositionManager
from execution.execution_engine import ExecutionEngine
from risk.risk_manager import RiskManager
from risk.performance_tracker import PerformanceTracker
from config import HOST, PORT, KLINE_1M, KLINE_5M, INITIAL_CAPITAL, POINT_VALUE

class PaperTrader:

    MARKET_CLOSE_TIMES = [dtime(12, 0), dtime(16, 30)]

    def __init__(self, code):

        self.code = code
        self.shutdown_triggered = False

        self.strategy = StrategyEngine()
        self.position_manager = PositionManager()
        self.execution = ExecutionEngine(self.position_manager)

        self.risk = RiskManager()

        today = datetime.now().date()
        self.performance = PerformanceTracker(
            INITIAL_CAPITAL,
            period=str(today)
        )

        self.trades = []

        self.quote_ctx = OpenQuoteContext(host=HOST, port=PORT)
        self.quote_ctx.subscribe(code, [SubType.QUOTE])

    # -------------------------------------------------
    # ✅ Market Close Detection
    # -------------------------------------------------
    def is_market_close(self, now):
        current_time = now.time()
        return any(
            current_time.hour == t.hour and current_time.minute == t.minute
            for t in self.MARKET_CLOSE_TIMES
        )

    # -------------------------------------------------
    # ✅ Force Close Logic
    # -------------------------------------------------
    def force_close(self, last_price, now):

        if self.position_manager.position == 0:
            return

        entry_price = self.position_manager.entry_price
        entry_time = self.position_manager.entry_time
        entry_slope = self.position_manager.entry_slope
        entry_atr = self.position_manager.entry_atr

        position = self.position_manager.position
        direction = "LONG" if position == 1 else "SHORT"

        pnl_points = (last_price - entry_price) * position
        pnl_hkd = pnl_points * POINT_VALUE

        self.risk.update_after_trade(pnl_hkd, now)

        trade_record = {
            "Direction": direction,
            "Entry Time": entry_time,
            "Exit Time": now,
            "Entry Price": entry_price,
            "Exit Price": last_price,
            "PnL (HKD)": pnl_hkd,
            "Equity": self.risk.equity,
            "Equity Peak": self.risk.equity_peak,
            "Drawdown (HKD)": self.risk.get_drawdown(),
            "Drawdown (%)": self.risk.get_drawdown_pct(),
            "SL (Y/N)": "",
            "Entry EMA20 Slope": round(entry_slope, 2),
            "Entry ATR": round(entry_atr, 2),
        }

        self.trades.append(trade_record)
        self.performance.record_trade(trade_record)
        self.position_manager.close_position()

    # -------------------------------------------------
    # ✅ Shutdown Routine
    # -------------------------------------------------
    def shutdown(self, reason="Manual Stop"):

        if self.shutdown_triggered:
            return

        self.shutdown_triggered = True

        print(f"\nStopping Paper Trading: {reason}")

        ret, df_1m = self.quote_ctx.get_cur_kline(
            self.code, KLINE_1M, KLType.K_1M
        )

        if ret == 0 and not df_1m.empty:
            last_price = df_1m["close"].iloc[-1]
            now = datetime.now()
            self.force_close(last_price, now)

        metrics = self.performance.print_report()

        # ✅ Save identical log
        os.makedirs("log", exist_ok=True)
        filename = f"log/paper_trade_log_{datetime.now().strftime('%Y%m')}.log"

        with open(filename, "w", encoding="utf-8") as f:

            f.write("================ TRADE LOG =================\n")
            for t in self.trades:
                f.write(str(t) + "\n")

            f.write("\n================ PERFORMANCE REPORT ================\n")
            for k, v in metrics.items():
                f.write(f"{k}: {v}\n")
            f.write("====================================================\n")

        print(f"Paper trade log saved to {filename}")

        self.quote_ctx.close()

    # -------------------------------------------------
    # ✅ Tick Handler
    # -------------------------------------------------
    def on_tick(self):

        ret1, df_1m = self.quote_ctx.get_cur_kline(
            self.code, KLINE_1M, KLType.K_1M
        )
        ret2, df_5m = self.quote_ctx.get_cur_kline(
            self.code, KLINE_5M, KLType.K_5M
        )

        if ret1 != 0 or ret2 != 0:
            return

        current_time = datetime.now()

        if self.is_market_close(current_time):
            self.shutdown("Market Close")
            return

        last_price = df_1m["close"].iloc[-1]
        high = df_1m["high"].iloc[-1]
        low = df_1m["low"].iloc[-1]

        # -------------------------------------------------
        # ✅ STRATEGY EVALUATION
        # -------------------------------------------------
        decision = self.strategy.evaluate(
            df_1m,
            df_5m,
            self.position_manager.position,
            df_5m_full=df_5m
        )

        # -------------------------------------------------
        # # ✅ ENTRY
        # -------------------------------------------------
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

        # -------------------------------------------------
        # # ✅ EXIT
        # -------------------------------------------------
        exit_result = self.execution.check_exit(
            high,
            low,
            current_time
        )

        if exit_result:

            pnl_hkd = exit_result["pnl_hkd"]

            self.risk.update_after_trade(pnl_hkd, current_time)

            trade_record = {
                "Direction": exit_result["direction"],
                "Entry Time": exit_result["entry_time"],
                "Exit Time": exit_result["exit_time"],
                "Entry Price": exit_result["entry_price"],
                "Exit Price": exit_result["exit_price"],
                "PnL (HKD)": pnl_hkd,
                "Equity": self.risk.equity,
                "Equity Peak": self.risk.equity_peak,
                "Drawdown (HKD)": self.risk.get_drawdown(),
                "Drawdown (%)": self.risk.get_drawdown_pct(),
                "SL (Y/N)": "",
                "Entry EMA20 Slope": round(exit_result["entry_slope"], 2),
                "Entry ATR": round(exit_result["entry_atr"], 2),
            }

            self.trades.append(trade_record)
            self.performance.record_trade(trade_record)

    def is_market_open(self, now):

        # ✅ Weekday check (Mon=0, Sun=6)
        if now.weekday() > 4:   # 5=Sat, 6=Sun
            return False

        t = now.time()

        morning_start = dtime(9, 15)
        morning_end   = dtime(12, 0)

        afternoon_start = dtime(13, 0)
        afternoon_end   = dtime(16, 30)

        night_start = dtime(17, 15)
        night_end   = dtime(3, 0)  # next day

        # Morning session
        if morning_start <= t <= morning_end:
            return True

        # Afternoon session
        if afternoon_start <= t <= afternoon_end:
            return True

        # Night session (cross-midnight handling)
        if t >= night_start or t <= night_end:
            return True

        return False

    # -------------------------------------------------
    # ✅ Main Loop
    # -------------------------------------------------
    def run(self):

        print("Entering run loop...")

        while not self.shutdown_triggered:
            try:
                now = datetime.now()

                if not self.is_market_open(now):
                    print("Market is closed.")
                    time.sleep(60)
                    continue

                self.on_tick()
                time.sleep(1)

            except KeyboardInterrupt:
                self.shutdown("Manual Interrupt")
                break