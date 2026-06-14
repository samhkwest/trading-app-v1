# data/csv_price_provider.py

"""
CSV Price Provider
-------------------------------------------------------
Used for backtesting.

Loads all required timeframes into memory
and serves sliced data progressively.
"""

import pandas as pd
from data.price_provider_base import BasePriceProvider


class CSVPriceProvider(BasePriceProvider):

    def __init__(self, data_dict: dict):
        """
        Parameters:
        ----------
        data_dict : dict
            Dictionary mapping timeframe -> DataFrame

            Example:
            {
                1: df_1m,
                3: df_3m,
                5: df_5m
            }
        """
        self.data = data_dict

    # -----------------------------------------------------
    # ✅ Get Candles
    # -----------------------------------------------------
    def get_candles(self, timeframe: int, up_to_time=None) -> pd.DataFrame:

        if timeframe not in self.data:
            raise ValueError(f"Timeframe {timeframe}m not loaded in CSVPriceProvider")

        df = self.data[timeframe]

        if up_to_time is not None:
            df = df[df["datetime"] <= up_to_time]

        return df.copy()