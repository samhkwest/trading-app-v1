# risk_manager.py

from config import MAX_DAILY_LOSS, INITIAL_CAPITAL

class RiskManager:

    def __init__(self):
        # ---------------------------------------------
        # ✅ Daily Control
        # ---------------------------------------------
        self.current_day = None
        self.daily_pnl = 0
        self.trading_enabled = True

        # ---------------------------------------------
        # ✅ Equity & Drawdown Tracking
        # ---------------------------------------------
        self.initial_capital = INITIAL_CAPITAL
        self.equity = INITIAL_CAPITAL
        self.equity_peak = INITIAL_CAPITAL
        self.max_drawdown = 0  # in HKD

    def update_after_trade(self, pnl_hkd, current_time):

        trade_day = current_time.date()

        # -------------------------------------------------
        # ✅ New Day Reset
        # -------------------------------------------------
        if self.current_day != trade_day:
            self.current_day = trade_day
            self.daily_pnl = 0
            self.trading_enabled = True

        self.daily_pnl += pnl_hkd

        self.equity += pnl_hkd

        # ✅ Update Equity Peak
        if self.equity > self.equity_peak:
            self.equity_peak = self.equity

        # ✅ Calculate Current Drawdown
        current_drawdown = self.equity_peak - self.equity

        # ✅ Track Maximum Drawdown
        if current_drawdown > self.max_drawdown:
            self.max_drawdown = current_drawdown

        # -------------------------------------------------
        # ✅ Daily Loss Limit Check
        # -------------------------------------------------
        if self.daily_pnl <= -MAX_DAILY_LOSS and self.trading_enabled:

            self.trading_enabled = False

            formatted_time = current_time.strftime("%Y-%m-%d %H:%M")

            print(f"🚨 DAILY LOSS LIMIT HIT - {formatted_time}")

    # -------------------------------------------------
    # ✅ Helper Methods (For Backtest Logging)
    # -------------------------------------------------

    def get_drawdown(self):
        return self.equity_peak - self.equity

    def get_drawdown_pct(self):
        if self.equity_peak == 0:
            return 0
        return (self.equity_peak - self.equity) / self.equity_peak * 100