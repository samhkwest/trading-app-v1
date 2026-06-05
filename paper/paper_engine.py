from futu import *
from strategy.signal import generate_signal, reset_regime_cache
from paper.portfolio import Portfolio
from paper.execution import simulate_buy, simulate_sell
from risk.risk_manager import RiskManager
from risk.performance_tracker import PerformanceTracker
from datetime import datetime
import time
from config import HOST, PORT, KLINE_1M, KLINE_5M, INITIAL_CAPITAL


class PaperTrader:

    def __init__(self, code):

        reset_regime_cache()

        self.code = code
        self.portfolio = Portfolio()
        self.risk = RiskManager()

        # ✅ Performance Tracker
        self.performance = PerformanceTracker(INITIAL_CAPITAL)

        self.quote_ctx = OpenQuoteContext(host=HOST, port=PORT)
        self.quote_ctx.subscribe(code, [SubType.QUOTE, SubType.ORDER_BOOK])

    def on_tick(self):

        if not self.risk.trading_enabled:
            print("Trading disabled by Risk Manager.")
            return

        ret1, df_1m = self.quote_ctx.get_cur_kline(self.code, KLINE_1M, KLType.K_1M)
        ret2, df_5m = self.quote_ctx.get_cur_kline(self.code, KLINE_5M, KLType.K_5M)

        if ret1 != 0 or ret2 != 0:
            return

        signal = generate_signal(df_1m, df_5m, self.portfolio.position)
        last_price = df_1m["close"].iloc[-1]
        current_time = datetime.now()

        if signal == "BUY":

            if self.portfolio.position == 0:
                print("OPEN LONG", last_price)
                self.portfolio.open_position("BUY", last_price)

            elif self.portfolio.position == -1:
                print("CLOSE SHORT", last_price)
                pnl_hkd = self.portfolio.close_position(last_price)
                self.risk.update_after_trade(pnl_hkd, current_time)

                # ✅ Record trade
                trade_record = {
                    "PnL (HKD)": pnl_hkd,
                    "Equity": self.risk.equity,
                    "Drawdown (HKD)": self.risk.get_drawdown(),
                    "Drawdown (%)": self.risk.get_drawdown_pct(),
                }

                self.performance.record_trade(trade_record)

        elif signal == "SELL":

            if self.portfolio.position == 0:
                print("OPEN SHORT", last_price)
                self.portfolio.open_position("SELL", last_price)

            elif self.portfolio.position == 1:
                print("CLOSE LONG", last_price)
                pnl_hkd = self.portfolio.close_position(last_price)
                self.risk.update_after_trade(pnl_hkd, current_time)

                # ✅ Record trade
                trade_record = {
                    "PnL (HKD)": pnl_hkd,
                    "Equity": self.risk.equity,
                    "Drawdown (HKD)": self.risk.get_drawdown(),
                    "Drawdown (%)": self.risk.get_drawdown_pct(),
                }

                self.performance.record_trade(trade_record)

    def run(self):

        while True:
            try:
                self.on_tick()
                time.sleep(1)

            except KeyboardInterrupt:
                print("Stopping paper trader...")

                # ✅ Print performance report before exit
                self.performance.print_report()

                self.quote_ctx.close()
                break