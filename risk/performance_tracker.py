# performance_tracker.py
 
from config import START_DATE, END_DATE

class PerformanceTracker:

    def __init__(self, initial_capital):
        self.initial_capital = initial_capital
        self.trades = []

    # -------------------------------------------------
    # ✅ Record Trade
    # -------------------------------------------------
    def record_trade(self, trade_dict):
        """
        trade_dict must contain:
        - "PnL (HKD)"
        - "Equity"
        - "Drawdown (HKD)"
        - "Drawdown (%)"
        """
        self.trades.append(trade_dict)

    # -------------------------------------------------
    # ✅ Generate Metrics
    # -------------------------------------------------
    def generate_metrics(self):

        if not self.trades:
            return {}

        total_trades = len(self.trades)

        pnl_list = [t["PnL (HKD)"] for t in self.trades]

        pnl_total = sum(pnl_list)
        winning_trades = len([p for p in pnl_list if p > 0])
        losing_trades = len([p for p in pnl_list if p < 0])

        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0

        gross_profit = sum(p for p in pnl_list if p > 0)
        gross_loss = abs(sum(p for p in pnl_list if p < 0))

        profit_factor = (
            float("inf") if gross_loss == 0 and gross_profit > 0
            else 0 if gross_loss == 0
            else gross_profit / gross_loss
        )

        max_drawdown = max(t["Drawdown (HKD)"] for t in self.trades)
        max_drawdown_pct = max(t["Drawdown (%)"] for t in self.trades)

        recovery_factor = pnl_total / max_drawdown if max_drawdown > 0 else 0

        # ✅ Max Losing Streak
        max_losing_streak = 0
        current_streak = 0

        for p in pnl_list:
            if p < 0:
                current_streak += 1
                max_losing_streak = max(max_losing_streak, current_streak)
            else:
                current_streak = 0

        # ✅ Longest Drawdown Duration
        longest_dd_duration = 0
        current_dd = 0

        for t in self.trades:
            if t["Drawdown (HKD)"] > 0:
                current_dd += 1
                longest_dd_duration = max(longest_dd_duration, current_dd)
            else:
                current_dd = 0

        total_return_pct = (
            (self.trades[-1]["Equity"] - self.initial_capital)
            / self.initial_capital * 100
        )

        return {
            "Period": START_DATE+" - "+END_DATE,
            "P&L (HKD)": round(pnl_total, 2),
            "Profit Factor": round(profit_factor, 2),
            "Total Trades": total_trades,
            "Winning Trades": winning_trades,
            "Losing Trades": losing_trades,
            "Win Rate (%)": round(win_rate, 1),
            "Total Return (%)": round(total_return_pct, 1),
            "Max Drawdown (HKD)": round(max_drawdown, 2),
            "Max Drawdown (%)": round(max_drawdown_pct, 1),
            "Recovery Factor": round(recovery_factor, 2),            
            "Max Losing Streak": max_losing_streak,
            "Longest DD Duration (Trades)": longest_dd_duration,
        }

    # -------------------------------------------------
    # ✅ Print Report
    # -------------------------------------------------
    def print_report(self):

        metrics = self.generate_metrics()

        if not metrics:
            print("No trades executed.")
            return

        print("\n================ PERFORMANCE REPORT ================")

        for k, v in metrics.items():
            print(f"{k}: {v}")

        print("====================================================\n")

        return metrics