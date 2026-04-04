# data_downloader.py

from futu import *
import pandas as pd
from datetime import datetime
import os
from connection import start_opend
from config import HOST, PORT, CODE, TIMEFRAME

# ✅ Change file extension to CSV
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


def download_full_history(ktype):

    from datetime import timedelta
    import time

    quote_ctx = OpenQuoteContext(host=HOST, port=PORT)

    start_dt = datetime.strptime("2023-01-01", "%Y-%m-%d")
    end_dt = datetime.now()

    all_data = []

    print("Downloading in 30-day chunks...")

    while start_dt < end_dt:

        chunk_end = min(start_dt + timedelta(days=30), end_dt)

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
    df = df.sort_values('datetime').drop_duplicates('datetime')

    os.makedirs("data", exist_ok=True)

    print("Earliest datetime:", df['datetime'].min())
    print("Latest datetime:", df['datetime'].max())

    # ✅ Save as CSV
    df.to_csv(SAVE_PATH, index=False)

    print(f"Saved {len(df)} rows to {SAVE_PATH}")


def update_local_data(ktype):
    """
    Update local CSV file incrementally.
    """

    if not os.path.exists(SAVE_PATH):
        print("No local file found. Performing full download.")
        download_full_history(ktype)
        return

    # ✅ Read CSV instead of Parquet
    local_df = pd.read_csv(SAVE_PATH)
    local_df['datetime'] = pd.to_datetime(local_df['datetime'])

    last_date = local_df['datetime'].max()

    start_date = last_date.strftime("%Y-%m-%d")
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
    combined = combined.sort_values('datetime').drop_duplicates('datetime')

    # ✅ Save back as CSV
    combined.to_csv(SAVE_PATH, index=False)

    print("Update complete.")
    print("Total rows:", len(combined))


def verify_time_frame():

    # ✅ Read CSV
    df = pd.read_csv(SAVE_PATH)
    df['datetime'] = pd.to_datetime(df['datetime'])

    df['date'] = df['datetime'].dt.date
    print("Candle Bars check:", df.groupby('date').size().head())


if __name__ == "__main__":

    if not start_opend():
        print("Cannot start OpenD.")
    else:
        ktype = get_ktype(TIMEFRAME)
        print("ktype: ", ktype)

        update_local_data(ktype)

        #print("Verify time frame...")
        #verify_time_frame()