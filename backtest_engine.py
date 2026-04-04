# backtest_engine.py

import pandas as pd
from strategy.signal import generate_signal
from strategy.regime import detect_regime
from config import WARMUP_BARS, POINT_VALUE, TAKE_PROFIT, STOP_LOSS

print("ENGINE FILE LOADED")

def run_backtest(df):

    trades = []

    position = 0
    entry_price = 0
    entry_time = None
    direction = None

    for i in range(50, len(df)):

        # -----------------------------
        # 1) Slice 1-minute data
        # -----------------------------
        df_slice = df.iloc[:i+1].copy()

        # -----------------------------
        # 2) Calculate 1-minute indicators
        # -----------------------------
        df_slice["ema5"] = df_slice["close"].ewm(span=5, adjust=False).mean()
        df_slice["ema10"] = df_slice["close"].ewm(span=10, adjust=False).mean()

        # -----------------------------
        # 3) Build 5-minute bars
        # -----------------------------
        df_5m = (
            df_slice
            .set_index("datetime")
            .resample("5min")
            .agg({
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum"
            })
            .dropna()
            .reset_index()
        )

        if len(df_5m) < WARMUP_BARS:
            continue

        # -----------------------------
        # 4) Calculate 5-minute indicators
        # -----------------------------
        df_5m["ema20"] = df_5m["close"].ewm(span=20, adjust=False).mean()

        df_5m["bb_mid"] = df_5m["close"].rolling(20).mean()
        df_5m["bb_std"] = df_5m["close"].rolling(20).std()
        df_5m["bb_upper"] = df_5m["bb_mid"] + 2 * df_5m["bb_std"]
        df_5m["bb_lower"] = df_5m["bb_mid"] - 2 * df_5m["bb_std"]

        delta = df_5m["close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()

        rs = avg_gain / avg_loss
        df_5m["rsi"] = 100 - (100 / (1 + rs))

        # -----------------------------
        # 5) Get current time + debug
        # -----------------------------
        current_price = df_slice["close"].iloc[-1]
        current_time = df_slice["datetime"].iloc[-1]
    
        # -----------------------------
        # 6) Generate signal
        # -----------------------------
        signal = generate_signal(df_slice, df_5m, position)

        # -----------------------------
        # 7) Entry logic
        # -----------------------------
        if position == 0 and signal in ["BUY", "SELL"]:
            position = 1 if signal == "BUY" else -1
            direction = "LONG" if signal == "BUY" else "SHORT"
            entry_price = current_price
            entry_time = current_time

        # -----------------------------
        # 8) Exit logic
        # -----------------------------
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