# config.py

#general
HOST="127.0.0.1"
PORT=11111

#paper trade
CODE="HK.MHImain"
KLINE_1M=1500
KLINE_5M=300
TIMEFRAME=5 # 1/5/15/30

#backtest
START_DATE="2026-04-02"
END_DATE="2026-04-02"
WARMUP_BARS=6        # Number of 5-min bars before trading starts
POINT_VALUE=10       # MHI = HKD 10 per point
TAKE_PROFIT=200      # in points
STOP_LOSS=50         # in points
