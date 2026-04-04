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
            pnl = price - self.entry_price
        elif self.position == -1:
            pnl = self.entry_price - price
        else:
            pnl = 0

        print(f"Closed position | PnL: {pnl}")

        self.position = 0
        self.entry_price = 0