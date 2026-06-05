import pandas as pd
import os


def print_section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def segment_by_quartile(df, column_name):

    if column_name not in df.columns:
        print(f"Column not found for diagnostics: {column_name}")
        return

    df = df[df[column_name].notna()]

    if len(df) < 20:
        print(f"Not enough data for {column_name} segmentation.")
        return

    print_section(f"Performance by {column_name} Quartile")

    df[f"{column_name}_bucket"] = pd.qcut(
        df[column_name], 4, duplicates="drop"
    )

    grouped = df.groupby(f"{column_name}_bucket").agg(
        trades=("PnL (HKD)", "count"),
        total_pnl=("PnL (HKD)", "sum"),
        win_rate=("win", "mean")
    )

    grouped["win_rate"] *= 100
    print(grouped.sort_values("total_pnl"))


def run_diagnostics(path):

    if not os.path.exists(path):
        print("Diagnostics file not found:", path)
        return

    df = pd.read_csv(path, parse_dates=["Entry Time", "Exit Time"])

    if df.empty:
        print("No trades found for diagnostics.")
        return

    df["win"] = df["PnL (HKD)"] > 0
    df["entry_hour"] = df["Entry Time"].dt.hour

    # -------------------------------------------------
    # Overall Summary
    # -------------------------------------------------
    print_section("Overall Summary")

    print("Total Trades:", len(df))
    print("Total PnL:", round(df["PnL (HKD)"].sum(), 2))
    print("Win Rate:", round(df["win"].mean() * 100, 2), "%")

    # -------------------------------------------------
    # Performance by Hour
    # -------------------------------------------------
    print_section("Performance by Entry Hour")

    hourly = df.groupby("entry_hour").agg(
        trades=("PnL (HKD)", "count"),
        total_pnl=("PnL (HKD)", "sum"),
        win_rate=("win", "mean")
    )

    hourly["win_rate"] *= 100
    print(hourly.sort_values("total_pnl"))

    # -------------------------------------------------
    # ✅ NEW — EMA20 Slope Quartile
    # -------------------------------------------------
    segment_by_quartile(df, "Entry EMA20 Slope")

    # -------------------------------------------------
    # ✅ NEW — ATR Quartile
    # -------------------------------------------------
    segment_by_quartile(df, "Entry ATR")

    # -------------------------------------------------
    # Profit Factor
    # -------------------------------------------------
    #print_section("Profit Factor")

    gross_profit = df[df["PnL (HKD)"] > 0]["PnL (HKD)"].sum()
    gross_loss = abs(df[df["PnL (HKD)"] < 0]["PnL (HKD)"].sum())

    if gross_loss == 0:
        pf = float("inf")
    else:
        pf = gross_profit / gross_loss

    print("\n");
    #print("Profit Factor:", round(pf, 2))