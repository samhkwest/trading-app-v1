# config.py

# CONNECTION
# ==========================================================
HOST = "127.0.0.1"
PORT = 11111

# GENERAL
# ==========================================================
CODE = "HK.MHImain"

# Download Data
# ==========================================================
TIMEFRAME = 1  # 1/5/15/30

# DATA SETTINGS
# ==========================================================
KLINE_1M = 1500
KLINE_5M = 300

# BACKTEST SETTINGS
# ==========================================================
START_DATE = "2026-05-04"
END_DATE = "2026-05-04"

# Trade Config
# ==========================================================
WARMUP_BARS = 6
POINT_VALUE = 10      # MHI = HKD 10 per point
TAKE_PROFIT = 200     # in points
STOP_LOSS = 50        # in points
ORDER_TYPE = "L"

# STRATEGY ENABLE SWITCHES
# ==========================================================
ENABLE_BREAKOUT = False
ENABLE_BOTTOM = False
ENABLE_TRANSITIONAL = False

# REGIME → STRATEGY ROUTING
# ==========================================================
REGIME_STRATEGY_MAP = {
    "TREND": ["BREAKOUT"],
    "RANGE": ["BOTTOM"],
    "TRANSITION": ["TRANSITIONAL"]
}

# STRATEGY PRIORITY
# ==========================================================
STRATEGY_PRIORITY = [
    "TRANSITIONAL",
    "BREAKOUT",
    "BOTTOM"
]

# RISK MANAGEMENT
# ==========================================================
ENABLE_RISK_CONTROL = True
INITIAL_CAPITAL = 70000
MAX_ACCOUNT_DD_PERCENT = 0.35
MAX_DAILY_LOSS = 3000

# DEBUG FLAGS
# ==========================================================
PRINT_DEBUG_REGIME = True
PRINT_DEBUG_SIGNAL = True