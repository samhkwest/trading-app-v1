# risk_manager.py

from config import (
    ENABLE_RISK_CONTROL,
    INITIAL_CAPITAL,
    MAX_ACCOUNT_DD_PERCENT,
    MAX_DAILY_LOSS
)


class RiskManager:

    def __init__(self):
        self.equity = INITIAL_CAPITAL
        self.peak_equity = INITIAL_CAPITAL
        self.daily_pnl = 0
        self.current_day = None
        self.trading_enabled = True

    # -----------------------------------------------------
    def update_after_trade(self, pnl_hkd, trade_time):

        if not ENABLE_RISK_CONTROL:
            return

        trade_day = trade_time.date()

        if self.current_day != trade_day:
            self.current_day = trade_day
            self.daily_pnl = 0

        self.equity += pnl_hkd
        self.daily_pnl += pnl_hkd

        if self.equity > self.peak_equity:
            self.peak_equity = self.equity

        self._check_limits()

    # -----------------------------------------------------
    def _check_limits(self):

        drawdown = (self.peak_equity - self.equity) / self.peak_equity

        if drawdown >= MAX_ACCOUNT_DD_PERCENT:
            print("🚨 HARD DRAWDOWN LIMIT HIT")
            self.trading_enabled = False

        if self.daily_pnl <= -MAX_DAILY_LOSS:
            print("🚨 DAILY LOSS LIMIT HIT")
            self.trading_enabled = False