from config import POINT_VALUE


class Portfolio:
    def __init__(self):
        self.position = 0  # 0 flat, 1 long, -1 short
        self.entry_price = 0

    def open_position(self, side, price):

        if side == "BUY":
            self.position = 1
        elif side == "SELL":
            self.position = -1

        self.entry_price = price

    def close_position(self, price):

        if self.position == 1:
            pnl_points = price - self.entry_price
        elif self.position == -1:
            pnl_points = self.entry_price - price
        else:
            pnl_points = 0

        pnl_hkd = pnl_points * POINT_VALUE

        print(f"Closed position | PnL (Points): {pnl_points} | PnL (HKD): {pnl_hkd}")

        self.position = 0
        self.entry_price = 0

        # Required for RiskManager
        return pnl_hkd