# backtest.py

from data_downloader import update_local_data
from data_loader import load_local_data
from backtest_engine import run_backtest
from stats import compute_statistics
from config import START_DATE, END_DATE

import pandas as pd
import os


def main():

    print("Running file:", __file__)
    print("Working directory:", os.getcwd())

    # --------------------------------------------------
    # Step 1: Update local data
    # --------------------------------------------------
    update_local_data()

    # --------------------------------------------------
    # Step 2: Load local data
    # --------------------------------------------------
    df = load_local_data()

    # --------------------------------------------------
    # Step 3: Filter by date range (inclusive full day)
    # --------------------------------------------------
    start_dt = pd.to_datetime(START_DATE)
    end_dt = pd.to_datetime(END_DATE) + pd.Timedelta(days=1)

    df = df[(df['datetime'] >= start_dt) &
            (df['datetime'] < end_dt)]

    df = df.reset_index(drop=True)

    print("\nBacktest Date Range:")
    print("Filtered Start:", df['datetime'].min())
    print("Filtered End  :", df['datetime'].max())
    print("Total Bars    :", len(df))

    if df.empty:
        print("\nNo data in selected date range.")
        return

    # --------------------------------------------------
    # Step 4: Run backtest
    # --------------------------------------------------
    trades = run_backtest(df)

    # --------------------------------------------------
    # Step 5: Compute statistics
    # --------------------------------------------------
    trade_log, stats = compute_statistics(trades)

    # --------------------------------------------------
    # Step 6: Output results
    # --------------------------------------------------
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