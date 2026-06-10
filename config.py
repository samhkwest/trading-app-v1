# config.py

# CONNECTION
# ==========================================================
HOST = "127.0.0.1"
PORT = 11111

# GENERAL
# ==========================================================
CODE = "HK.MHImain"
ENABLE_LONG = True
ENABLE_SHORT = True

# Download Data
# ==========================================================
TIMEFRAME = 1  # 1/5/15/30

# TIMEFRAME CONFIGURATION
# ==========================================================
TIMEFRAME_CONFIG = {
    "trend": 5,
    "structure": 5,
    "entry": 1
}

# DATA SETTINGS
# ==========================================================
KLINE_1M = 1500
KLINE_5M = 300

# BACKTEST SETTINGS
# ==========================================================
INITIAL_CAPITAL = 100000
START_DATE = "2026-06-01"
END_DATE = "2026-06-30"

# Trade Config
# ==========================================================
WARMUP_BARS = 6
POINT_VALUE = 10      # MHI = HKD 10 per point
TAKE_PROFIT = 200     # in points
STOP_LOSS = 50        # in points
ORDER_TYPE = "L"
MIN_ENTRY_ATR = 33    # volatility filter threshold

# VOLUME CONFIRMATION SETTINGS (NEW)
# ==========================================================
VOLUME_MA_PERIOD = 20          # Look back period for volume MA
VOLUME_MULTIPLIER = 1       # Current vol must be > 1.1x MA
VOLUME_CONFIRMATION_ENABLED = True
PRINT_DEBUG_VOLUME = False     # Debug flag for volume filtering

# STRATEGY ENABLE SWITCHES
# ==========================================================
#ENABLE_BREAKOUT = False
#ENABLE_BOTTOM = False
#ENABLE_TRANSITIONAL = False

# REGIME → STRATEGY ROUTING
# ==========================================================
#REGIME_STRATEGY_MAP = {
#    "TREND": ["BREAKOUT"],
#    "RANGE": ["BOTTOM"],
#    "TRANSITION": ["TRANSITIONAL"]
#}

# STRATEGY PRIORITY
# ==========================================================
#STRATEGY_PRIORITY = [
#    "TRANSITIONAL",
#    "BREAKOUT",
#    "BOTTOM"
#]

# RISK MANAGEMENT
# ==========================================================
ENABLE_RISK_CONTROL = True
MAX_DAILY_LOSS = 2000

# DEBUG FLAGS
# ==========================================================
PRINT_DEBUG_REGIME = True
PRINT_DEBUG_SIGNAL = True
PRINT_DEBUG_VOLUME = True     # Volume filter debug

# ==========================================================
# DIAGNOSTICS MODULE CONTROL
# ==========================================================
RUN_DIAGNOSTICS = True
DIAGNOSTICS_PATH = "log/backtest_trade_log.csv"

# Trend Regime Control
# ==========================================================
TREND_SLOPE_THRESHOLD = 45   # 5m EMA20 slope threshold
