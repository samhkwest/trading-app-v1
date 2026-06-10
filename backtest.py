# backtest.py

from data_downloader import update_local_data, get_ktype
from data_loader import load_local_data
from engine.backtest_engine import run_backtest
from config import START_DATE, END_DATE, CODE, RUN_DIAGNOSTICS
from config import DIAGNOSTICS_PATH, TIMEFRAME_CONFIG
from diagnostics.performance_segmenter import run_diagnostics
from datetime import datetime
from data.csv_price_provider import CSVPriceProvider
import pandas as pd
import os


def main():

    print("Running file:", __file__)
    print("Working directory:", os.getcwd())

    # --------------------------------------------------
    # ✅ 1) Update required timeframes dynamically
    # --------------------------------------------------
    required_tfs = set(TIMEFRAME_CONFIG.values())

    for tf in required_tfs:
        path = f"data/{CODE.replace('.', '_')}_{tf}m.csv"

        if not os.path.exists(path):
            print(f"\nDownloading {tf}m data...")
            update_local_data(get_ktype(tf), tf)
        else:
            print(f"\n{tf}m data already exists. Skipping download.")

    # --------------------------------------------------
    # ✅ 2) Load CSV files dynamically
    # --------------------------------------------------
    data_dict = {}

    for tf in required_tfs:
        path = f"data/{CODE.replace('.', '_')}_{tf}m.csv"
        print(f"Loading {tf}m path:", path)

        df = load_local_data(path)
        df["datetime"] = pd.to_datetime(df["datetime"])

        start_dt = pd.to_datetime(START_DATE)
        end_dt = pd.to_datetime(END_DATE) + pd.Timedelta(days=1)

        df = df[
            (df["datetime"] >= start_dt) &
            (df["datetime"] <= end_dt)
        ].reset_index(drop=True)

        if df.empty:
            print(f"No data in selected range for {tf}m.")
            return

        data_dict[tf] = df

        print(f"{tf}m Bars:", len(df))

    # --------------------------------------------------
    # ✅ 3) Create Provider
    # --------------------------------------------------
    provider = CSVPriceProvider(data_dict)

    # --------------------------------------------------
    # ✅ 4) Run Backtest
    # --------------------------------------------------
    trade_log, stats = run_backtest(provider)

    # --------------------------------------------------
    # 5) Print Trade Log
    # --------------------------------------------------
    if trade_log is not None and not trade_log.empty:
        print("\n================ TRADE LOG (BACKTEST.PY) ================")
        print(trade_log.to_string(index=False))
        trade_log.to_csv("trade_log.csv", index=False)
        print("\nTrade log saved to trade_log.csv")

    # --------------------------------------------------
    # 6) Print Performance AFTER trade log
    # --------------------------------------------------
    if stats:
        print("\n================ PERFORMANCE REPORT ================")
        for k, v in stats.items():
            print(f"{k}: {v}")
        print("====================================================\n")
    # --------------------------------------------------
    # 7) Run Diagnostics
    # --------------------------------------------------
    if RUN_DIAGNOSTICS:
        print("\nRunning Performance Diagnostics...")
        run_diagnostics(DIAGNOSTICS_PATH)
    else:
        print("Diagnostics disabled in config.py")


if __name__ == "__main__":
    main()