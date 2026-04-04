# stats.py

import pandas as pd
import numpy as np

def compute_statistics(trades):

    if len(trades) == 0:
        return None, {"Message": "No trades executed."}

    df_trades = pd.DataFrame(trades)

    pnl = df_trades["PnL (HKD)"]

    total_trades = len(df_trades)
    net_profit = pnl.sum()
    wins = pnl[pnl > 0]
    losses = pnl[pnl <= 0]

    win_rate = len(wins) / total_trades
    profit_factor = wins.sum() / abs(losses.sum()) if len(losses) > 0 else 0

    stats = {
        "Total Trades": total_trades,
        "Net Profit (HKD)": round(net_profit, 2),
        "Win Rate (%)": round(win_rate * 100, 2),
        "Profit Factor": round(profit_factor, 2),
        "Average Trade (HKD)": round(pnl.mean(), 2),
        "Max Win (HKD)": round(pnl.max(), 2),
        "Max Loss (HKD)": round(pnl.min(), 2)
    }

    return df_trades, stats