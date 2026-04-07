# backtest.py

from data_downloader import update_local_data, get_ktype
from data_loader import load_local_data
from backtest_engine import run_backtest
from stats import compute_statistics
from config import START_DATE, END_DATE, CODE

import pandas as pd
import os


def main():

    print("Running file:", __file__)
    print("Working directory:", os.getcwd())

    # --------------------------------------------------
    # 1) Update data
    # --------------------------------------------------
    print("\nUpdating 1m data...")
    update_local_data(get_ktype(1), 1)

    print("Updating 5m data...")
    update_local_data(get_ktype(5), 5)

    # --------------------------------------------------
    # 2) Load CSV files
    # --------------------------------------------------
    path_1m = f"data/{CODE.replace('.', '_')}_1m.csv"
    path_5m = f"data/{CODE.replace('.', '_')}_5m.csv"

    print("\nLoading files:")
    print("1m path:", path_1m)
    print("5m path:", path_5m)

    df_1m = load_local_data(path_1m)
    df_5m = load_local_data(path_5m)

    # --------------------------------------------------
    # 3) Datetime Filtering (Correct for Futures)
    # --------------------------------------------------

    df_1m["datetime"] = pd.to_datetime(df_1m["datetime"])
    df_5m["datetime"] = pd.to_datetime(df_5m["datetime"])

    start_dt = pd.to_datetime(START_DATE)
    end_dt = pd.to_datetime(END_DATE) + pd.Timedelta(days=1)

    df_1m = df_1m[
        (df_1m["datetime"] >= start_dt) &
        (df_1m["datetime"] <= end_dt)
    ].reset_index(drop=True)

    df_5m = df_5m[
        (df_5m["datetime"] >= start_dt) &
        (df_5m["datetime"] <= end_dt)
    ].reset_index(drop=True)

    # --------------------------------------------------
    # 4) Check if empty
    # --------------------------------------------------
    if df_1m.empty or df_5m.empty:
        print("\nNo data in selected date range.")
        return

    print("\nBacktest Date Range:")
    print("1m Start:", df_1m["datetime"].min())
    print("1m End  :", df_1m["datetime"].max())
    print("1m Bars :", len(df_1m))
    print("5m Bars :", len(df_5m))

    # --------------------------------------------------
    # 5) Run backtest
    # --------------------------------------------------
    trades = run_backtest(df_1m, df_5m)

    # --------------------------------------------------
    # 6) Statistics
    # --------------------------------------------------
    trade_log, stats = compute_statistics(trades)

    if trade_log is not None and not trade_log.empty:
        print("\n================ TRADE LOG ================")
        print(trade_log)
        trade_log.to_csv("trade_log.csv", index=False)
        print("\nTrade log saved to trade_log.csv")

    print("\n================ STATISTICS ================")
    for k, v in stats.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()