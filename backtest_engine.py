# backtest_engine.py

import pandas as pd
from strategy.signal import generate_signal, reset_regime_cache
from config import WARMUP_BARS, POINT_VALUE, TAKE_PROFIT, STOP_LOSS, ORDER_TYPE

print("ENGINE FILE LOADED")


def run_backtest(df_1m, df_5m):

    # Reset regime cache before each run
    reset_regime_cache()

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

        current_bar = df_1m_slice.iloc[-1]
        current_time = current_bar["datetime"]
        current_close = current_bar["close"]
        current_high = current_bar["high"]
        current_low = current_bar["low"]

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
            entry_price = current_close
            entry_time = current_time

        # -------------------------------------------------
        # 5) Exit logic (TP / SL)
        # -------------------------------------------------
        if position != 0:

            # LONG POSITION
            if position == 1:

                tp_price = entry_price + TAKE_PROFIT
                sl_price = entry_price - STOP_LOSS

                tp_hit = current_high >= tp_price
                sl_hit = current_low <= sl_price

                exit_price = None

                if tp_hit and sl_hit:
                    # Conservative: assume SL hit first
                    exit_price = sl_price
                elif tp_hit:
                    exit_price = tp_price
                elif sl_hit:
                    exit_price = sl_price

            # SHORT POSITION
            elif position == -1:

                tp_price = entry_price - TAKE_PROFIT
                sl_price = entry_price + STOP_LOSS

                tp_hit = current_low <= tp_price
                sl_hit = current_high >= sl_price

                exit_price = None

                if tp_hit and sl_hit:
                    # Conservative: assume SL hit first
                    exit_price = sl_price
                elif tp_hit:
                    exit_price = tp_price
                elif sl_hit:
                    exit_price = sl_price

            # If exit triggered
            if exit_price is not None:

                pnl_points = (exit_price - entry_price) * position
                pnl_hkd = pnl_points * POINT_VALUE

                trades.append({
                    "Direction": direction,
                    "Entry Time": entry_time,
                    "Exit Time": current_time,
                    "Entry Price": entry_price,
                    "Exit Price": exit_price,
                    "PnL (Points)": pnl_points,
                    "PnL (HKD)": pnl_hkd
                })

                position = 0
                direction = None
                entry_price = 0
                entry_time = None

    # ----------------------------------------------------------
    # 6) Close open position at end of backtest (mark-to-market)
    # ----------------------------------------------------------
    if position != 0:

        final_price = df_1m["close"].iloc[-1]
        final_time = df_1m["datetime"].iloc[-1]

        pnl_points = (final_price - entry_price) * position
        pnl_hkd = pnl_points * POINT_VALUE

        trades.append({
            "Direction": direction,
            "Entry Time": entry_time,
            "Exit Time": final_time,
            "Entry Price": entry_price,
            "Exit Price": final_price,
            "PnL (Points)": pnl_points,
            "PnL (HKD)": pnl_hkd
        })

    return pd.DataFrame(trades)