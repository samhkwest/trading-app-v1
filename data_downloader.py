# data_downloader.py

from futu import *
import pandas as pd
from datetime import datetime, timedelta
import os
import time

from connection import start_opend
from config import HOST, PORT, CODE, TIMEFRAME


SAVE_PATH = f"data/{CODE.replace('.', '_')}_{TIMEFRAME}m.csv"


def get_ktype(timeframe):
    mapping = {
        1: KLType.K_1M,
        3: KLType.K_3M,
        5: KLType.K_5M,
        15: KLType.K_15M,
        30: KLType.K_30M,
        60: KLType.K_60M,
    }
    return mapping.get(timeframe)


def get_chunk_days(timeframe):
    """
    Avoid Futu 1000-bar limit.
    """

    if timeframe == 1:
        return 5      # ~5 days for 1m (~1200–1500 bars trading hours)
    elif timeframe <= 5:
        return 15
    else:
        return 30


def download_full_history(ktype):

    quote_ctx = OpenQuoteContext(host=HOST, port=PORT)

    start_dt = datetime.strptime("2023-01-01", "%Y-%m-%d")
    end_dt = datetime.now()

    chunk_days = get_chunk_days(TIMEFRAME)
    all_data = []

    print("Downloading historical data in chunks...")

    while start_dt < end_dt:

        chunk_end = min(start_dt + timedelta(days=chunk_days), end_dt)

        print(f"Requesting {start_dt.date()} to {chunk_end.date()}")

        ret, data, _ = quote_ctx.request_history_kline(
            CODE,
            start=start_dt.strftime("%Y-%m-%d"),
            end=chunk_end.strftime("%Y-%m-%d"),
            ktype=ktype,
            max_count=1000
        )

        if ret != RET_OK:
            print("Error:", data)
            break

        if not data.empty:
            all_data.append(data)
            print(f"  Received {len(data)} rows")

        start_dt = chunk_end + timedelta(days=1)
        time.sleep(0.5)

    quote_ctx.close()

    if not all_data:
        print("No data downloaded.")
        return

    df = pd.concat(all_data)

    df['datetime'] = pd.to_datetime(df['time_key'])

    df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']]

    df = (
        df.sort_values('datetime')
          .drop_duplicates('datetime')
          .reset_index(drop=True)
    )

    os.makedirs("data", exist_ok=True)

    print("Earliest datetime:", df['datetime'].min())
    print("Latest datetime:", df['datetime'].max())

    df.to_csv(SAVE_PATH, index=False)

    print(f"Saved {len(df)} rows to {SAVE_PATH}")


def update_local_data(ktype):
    """
    Incrementally update local CSV file.
    """

    if not os.path.exists(SAVE_PATH):
        print("No local file found. Performing full download.")
        download_full_history(ktype)
        return

    local_df = pd.read_csv(SAVE_PATH, parse_dates=['datetime'])

    last_datetime = local_df['datetime'].max()

    # Start from next minute to avoid duplication
    next_dt = last_datetime + pd.Timedelta(minutes=TIMEFRAME)

    start_date = next_dt.strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")

    print(f"Updating from {start_date} to {end_date}")

    quote_ctx = OpenQuoteContext(host=HOST, port=PORT)

    ret, data, _ = quote_ctx.request_history_kline(
        CODE,
        start=start_date,
        end=end_date,
        ktype=ktype,
        max_count=1000
    )

    quote_ctx.close()

    if ret != RET_OK:
        print("Update error:", data)
        return

    if data.empty:
        print("No new data.")
        return

    new_df = data.copy()

    new_df['datetime'] = pd.to_datetime(new_df['time_key'])

    new_df = new_df[['datetime', 'open', 'high', 'low', 'close', 'volume']]

    combined = pd.concat([local_df, new_df])

    combined = (
        combined.sort_values('datetime')
                .drop_duplicates('datetime')
                .reset_index(drop=True)
    )

    combined.to_csv(SAVE_PATH, index=False)

    print("Update complete.")
    print("Total rows:", len(combined))


if __name__ == "__main__":

    if not start_opend():
        print("Cannot start OpenD.")
    else:
        ktype = get_ktype(TIMEFRAME)

        if ktype is None:
            print("Invalid TIMEFRAME in config.")
        else:
            print("ktype:", ktype)
            update_local_data(ktype)