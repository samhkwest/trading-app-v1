# data/futu_price_provider.py

"""
Futu Price Provider
-------------------------------------------------------
Used for paper trading / live trading.

Wraps Futu OpenD API and provides
a unified interface identical to CSV provider.
"""

from futu import *
import pandas as pd
from data.price_provider_base import BasePriceProvider


class FutuPriceProvider(BasePriceProvider):

    def __init__(self, quote_ctx, code: str):
        """
        Parameters:
        ----------
        quote_ctx : OpenQuoteContext
        code : str (e.g. HK.MHImain)
        """
        self.ctx = quote_ctx
        self.code = code

    # -----------------------------------------------------
    # ✅ Map integer timeframe to Futu KLType
    # -----------------------------------------------------
    def _map_ktype(self, timeframe: int):

        mapping = {
            1: KLType.K_1M,
            3: KLType.K_3M,
            5: KLType.K_5M,
            15: KLType.K_15M,
            30: KLType.K_30M,
            60: KLType.K_60M,
        }

        if timeframe not in mapping:
            raise ValueError(f"Unsupported timeframe: {timeframe}m")

        return mapping[timeframe]

    # -----------------------------------------------------
    # ✅ Get Candles
    # -----------------------------------------------------
    def get_candles(self, timeframe: int, up_to_time=None) -> pd.DataFrame:

        ktype = self._map_ktype(timeframe)

        ret, df = self.ctx.get_cur_kline(
            self.code,
            1000,
            ktype
        )

        if ret != RET_OK or df.empty:
            return pd.DataFrame()

        df["datetime"] = pd.to_datetime(df["time_key"])

        df = df[["datetime", "open", "high", "low", "close", "volume"]]

        if up_to_time is not None:
            df = df[df["datetime"] <= up_to_time]

        df = (
            df.sort_values("datetime")
              .drop_duplicates("datetime")
              .reset_index(drop=True)
        )

        return df.copy()