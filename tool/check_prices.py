# check_mhi_timeframes.py

from futu import *
import pandas as pd

# ==============================
# CONFIG
# ==============================

HOST = "127.0.0.1"
PORT = 11111

CODE = "HK.MHI2604"
TARGET_DATE = "2026-04-02"

N_MIN = 5  # Change to 1,3,5,15,30,60

KLINE_MAP = {
    1: KLType.K_1M,
    3: KLType.K_3M,
    5: KLType.K_5M,
    15: KLType.K_15M,
    30: KLType.K_30M,
    60: KLType.K_60M
}

if N_MIN not in KLINE_MAP:
    raise ValueError("Unsupported N_MIN value")

INTRADAY_KTYPE = KLINE_MAP[N_MIN]

OUTPUT_FILE = f"{CODE.replace('.', '_')}_{TARGET_DATE}_{N_MIN}min_WITH_DAILY.csv"

# ==============================
# CONNECT
# ==============================

quote_ctx = OpenQuoteContext(host=HOST, port=PORT)

print(f"\nRequesting DAILY + {N_MIN}-min data for {CODE} on {TARGET_DATE}\n")

# ==============================
# 1️⃣ REQUEST DAILY DATA
# ==============================

ret_day, data_day, _ = quote_ctx.request_history_kline(
    code=CODE,
    ktype=KLType.K_DAY,
    start=TARGET_DATE,
    end=TARGET_DATE,
    max_count=10
)

if ret_day != RET_OK:
    print("Daily Data Error:", data_day)
    quote_ctx.close()
    exit()

data_day['time_key'] = pd.to_datetime(data_day['time_key'])

daily_df = data_day[
    data_day['time_key'].dt.date == pd.to_datetime(TARGET_DATE).date()
].copy()

# ==============================
# 2️⃣ REQUEST INTRADAY DATA
# ==============================

ret_intra, data_intra, _ = quote_ctx.request_history_kline(
    code=CODE,
    ktype=INTRADAY_KTYPE,
    start=TARGET_DATE,
    end=TARGET_DATE,
    max_count=3000
)

if ret_intra != RET_OK:
    print("Intraday Data Error:", data_intra)
    quote_ctx.close()
    exit()

data_intra['time_key'] = pd.to_datetime(data_intra['time_key'])

intra_df = data_intra[
    data_intra['time_key'].dt.date == pd.to_datetime(TARGET_DATE).date()
].copy()

if intra_df.empty:
    print("No intraday data returned.")
    quote_ctx.close()
    exit()

intra_df = intra_df[['time_key', 'open', 'high', 'low', 'close']]
intra_df = intra_df.sort_values(by='time_key')

# ==============================
# 3️⃣ CALCULATE SUMMARIES
# ==============================

# Daily timeframe values
if not daily_df.empty:
    daily_open = daily_df.iloc[0]['open']
    daily_high = daily_df.iloc[0]['high']
    daily_low = daily_df.iloc[0]['low']
    daily_close = daily_df.iloc[0]['close']
else:
    daily_open = daily_high = daily_low = daily_close = None

# Intraday derived values
intra_high = intra_df['high'].max()
intra_low = intra_df['low'].min()
earliest = intra_df['time_key'].min()
latest = intra_df['time_key'].max()
total_bars = len(intra_df)

# ==============================
# PRINT SUMMARY
# ==============================

print("========== DAILY (1-DAY TIMEFRAME) ==========")
print("Open :", daily_open)
print("High :", daily_high)
print("Low  :", daily_low)
print("Close:", daily_close)

print("\n========== INTRADAY SUMMARY ==========")
print("Bar Type :", f"{N_MIN}-Minute")
print("Earliest :", earliest)
print("Latest   :", latest)
print("Day High :", intra_high)
print("Day Low  :", intra_low)
print("Total Bars:", total_bars)

# ==============================
# 4️⃣ EXPORT CSV (3 SECTIONS)
# ==============================

daily_summary_df = pd.DataFrame({
    "Metric": ["Open", "High", "Low", "Close"],
    "Daily_Timeframe_Value": [daily_open, daily_high, daily_low, daily_close]
})

intra_summary_df = pd.DataFrame({
    "Metric": [
        "Bar Type",
        "Earliest Time",
        "Latest Time",
        "Intraday High (from N-min)",
        "Intraday Low (from N-min)",
        "Total Bars"
    ],
    "Value": [
        f"{N_MIN}-Minute",
        earliest,
        latest,
        intra_high,
        intra_low,
        total_bars
    ]
})

with open(OUTPUT_FILE, "w", newline="") as f:
    f.write("=== DAILY TIMEFRAME (K_DAY) ===\n")
    daily_summary_df.to_csv(f, index=False)

    f.write("\n=== INTRADAY SUMMARY ===\n")
    intra_summary_df.to_csv(f, index=False)

    f.write("\n=== INTRADAY N-MIN DATA ===\n")
    intra_df.to_csv(f, index=False)

print(f"\nCSV exported to: {OUTPUT_FILE}")

quote_ctx.close()