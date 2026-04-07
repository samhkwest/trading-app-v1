from futu import *
import pandas as pd
from datetime import datetime, timedelta
import os
import time

from connection import start_opend
from config import HOST, PORT, CODE, TIMEFRAME


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
    Conservative chunk sizing to reduce hitting 1000-bar cap.
    """
    if timeframe == 1:
        return 3      # safer for 1m
    elif timeframe <= 5:
        return 10
    else:
        return 30


# ==========================================================
# FULL DOWNLOAD
# ==========================================================

def download_full_history(ktype, timeframe):

    save_path = f"data/{CODE.replace('.', '_')}_{timeframe}m.csv"

    quote_ctx = OpenQuoteContext(host=HOST, port=PORT)

    start_dt = datetime.strptime("2023-01-01", "%Y-%m-%d")
    end_dt = datetime.now()

    chunk_days = get_chunk_days(timeframe)
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

        if data.empty:
            start_dt = chunk_end + timedelta(days=1)
            continue

        all_data.append(data)
        print(f"  Received {len(data)} rows")

        last_time = pd.to_datetime(data['time_key'].iloc[-1])

        # SAFETY: prevent infinite loop
        if last_time <= start_dt:
            print("No forward progress detected. Breaking.")
            break

        # If hit API cap → resume from last timestamp
        if len(data) == 1000:
            start_dt = last_time + timedelta(minutes=timeframe)
        else:
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

    df.to_csv(save_path, index=False)
    print(f"Saved {len(df)} rows to {save_path}")


# ==========================================================
# INCREMENTAL UPDATE
# ==========================================================

def update_local_data(ktype, timeframe):

    save_path = f"data/{CODE.replace('.', '_')}_{timeframe}m.csv"

    if not os.path.exists(save_path):
        print("No local file found. Performing full download.")
        download_full_history(ktype, timeframe)
        return

    local_df = pd.read_csv(save_path, parse_dates=['datetime'])
    last_datetime = local_df['datetime'].max()

    start_dt = (last_datetime + pd.Timedelta(minutes=timeframe)).to_pydatetime()
    end_dt = datetime.now()

    chunk_days = get_chunk_days(timeframe)
    all_data = []

    print(f"Updating from {start_dt.date()} to {end_dt.date()}")

    quote_ctx = OpenQuoteContext(host=HOST, port=PORT)

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
            print("Update error:", data)
            break

        if data.empty:
            start_dt = chunk_end + timedelta(days=1)
            continue

        all_data.append(data)
        print(f"  Received {len(data)} rows")

        last_time = pd.to_datetime(data['time_key'].iloc[-1])

        # SAFETY: prevent infinite loop
        if last_time <= start_dt:
            print("No forward progress detected. Breaking.")
            break

        if len(data) == 1000:
            start_dt = last_time + timedelta(minutes=timeframe)
        else:
            start_dt = chunk_end + timedelta(days=1)

        time.sleep(0.5)

    quote_ctx.close()

    if not all_data:
        print("No new data.")
        return

    new_df = pd.concat(all_data)
    new_df['datetime'] = pd.to_datetime(new_df['time_key'])
    new_df = new_df[['datetime', 'open', 'high', 'low', 'close', 'volume']]

    combined = pd.concat([local_df, new_df])
    combined = (
        combined.sort_values('datetime')
                .drop_duplicates('datetime')
                .reset_index(drop=True)
    )

    combined.to_csv(save_path, index=False)

    print("Update complete.")
    print("Total rows:", len(combined))


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    if not start_opend():
        print("Cannot start OpenD.")
    else:
        ktype = get_ktype(TIMEFRAME)

        if ktype is None:
            print("Invalid TIMEFRAME in config.")
        else:
            print("ktype:", ktype)
            update_local_data(ktype, TIMEFRAME)