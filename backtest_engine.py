# backtest_engine.py

import pandas as pd
from strategy.signal import generate_signal
from config import WARMUP_BARS, POINT_VALUE, TAKE_PROFIT, STOP_LOSS

print("ENGINE FILE LOADED")


def run_backtest(df_1m, df_5m):

    trades = []

    position = 0
    entry_price = 0
    entry_time = None
    direction = None

    # Start after warmup
    for i in range(WARMUP_BARS, len(df_1m)):

        # -------------------------------------------------
        # 1) Slice 1-minute data up to current bar
        # -------------------------------------------------
        df_1m_slice = df_1m.iloc[:i+1].copy()

        current_time = df_1m_slice["datetime"].iloc[-1]
        current_price = df_1m_slice["close"].iloc[-1]

        # -------------------------------------------------
        # 2) Slice ONLY closed 5-minute bars
        # -------------------------------------------------
        df_5m_slice = df_5m[
            df_5m["datetime"] <= current_time
        ].copy()

        if len(df_5m_slice) < WARMUP_BARS:
            continue

        # -------------------------------------------------
        # 3) Generate signal (IDENTICAL TO PAPER ENGINE)
        # -------------------------------------------------
        signal = generate_signal(df_1m_slice, df_5m_slice, position)

        # -------------------------------------------------
        # 4) Entry logic (same as paper engine)
        # -------------------------------------------------
        if position == 0 and signal in ["BUY", "SELL"]:

            position = 1 if signal == "BUY" else -1
            direction = "LONG" if signal == "BUY" else "SHORT"
            entry_price = current_price
            entry_time = current_time

        # -------------------------------------------------
        # 5) Exit logic (TP / SL)
        # -------------------------------------------------
        if position != 0:

            pnl_points = (current_price - entry_price) * position

            if pnl_points >= TAKE_PROFIT or pnl_points <= -STOP_LOSS:

                pnl_hkd = pnl_points * POINT_VALUE

                trades.append({
                    "Direction": direction,
                    "Entry Time": entry_time,
                    "Exit Time": current_time,
                    "Entry Price": entry_price,
                    "Exit Price": current_price,
                    "PnL (Points)": pnl_points,
                    "PnL (HKD)": pnl_hkd
                })

                position = 0
                direction = None
                entry_price = 0
                entry_time = None

    return pd.DataFrame(trades)