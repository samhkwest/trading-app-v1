from futu import *
from strategy.signal import generate_signal
from paper.portfolio import Portfolio
from paper.execution import simulate_buy, simulate_sell
import time
from config import HOST, PORT, KLINE_1M, KLINE_5M

class PaperTrader:

    def __init__(self, code):
        self.code = code
        self.portfolio = Portfolio()
        self.quote_ctx = OpenQuoteContext(host=HOST, port=PORT)

        self.quote_ctx.subscribe(code, [SubType.QUOTE, SubType.ORDER_BOOK])

    def on_tick(self):

        ret1, df_1m = self.quote_ctx.get_cur_kline(
            self.code, KLINE_1M, KLType.K_1M
        )

        ret2, df_5m = self.quote_ctx.get_cur_kline(
            self.code, KLINE_5M, KLType.K_5M
        )

        if ret1 != 0 or ret2 != 0:
            return

        signal = generate_signal(df_1m, df_5m, self.portfolio.position)

        last_price = df_1m["close"].iloc[-1]

        if signal == "BUY":

            if self.portfolio.position == 0:
                print("OPEN LONG", last_price)
                self.portfolio.open_position("BUY", last_price)

            elif self.portfolio.position == -1:
                print("CLOSE SHORT", last_price)
                self.portfolio.close_position(last_price)

        elif signal == "SELL":

            if self.portfolio.position == 0:
                print("OPEN SHORT", last_price)
                self.portfolio.open_position("SELL", last_price)

            elif self.portfolio.position == 1:
                print("CLOSE LONG", last_price)
                self.portfolio.close_position(last_price)


    def on_tick_old(self):

        ret1, df_1m = self.quote_ctx.get_cur_kline(
            self.code, KLINE_1M, KLType.K_1M
        )

        ret2, df_5m = self.quote_ctx.get_cur_kline(
            self.code, KLINE_5M, KLType.K_5M
        )

        if ret1 != 0 or ret2 != 0:
            return

        signal = generate_signal(df_1m, df_5m, self.portfolio.position)

        last_price = df_1m["close"].iloc[-1]

        if signal == "BUY":

            if self.portfolio.position == 0:
                print("OPEN LONG", last_price)
                self.portfolio.open_position("BUY", last_price)

            elif self.portfolio.position == -1:
                print("CLOSE SHORT", last_price)
                self.portfolio.close_position(last_price)

        elif signal == "SELL":

            if self.portfolio.position == 0:
                print("OPEN SHORT", last_price)
                self.portfolio.open_position("SELL", last_price)

            elif self.portfolio.position == 1:
                print("CLOSE LONG", last_price)
                self.portfolio.close_position(last_price)
            
    def run(self):
        while True:
            try:
                self.on_tick()
                time.sleep(1)  # 1 second interval
            except KeyboardInterrupt:
                print("Stopping paper trader...")
                self.quote_ctx.close()
                break