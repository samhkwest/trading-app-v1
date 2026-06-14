# data/price_provider_base.py

"""
Base Price Provider Interface
-------------------------------------------------------
Defines the abstraction layer for retrieving candle data.

Any data source (CSV, Futu, future broker, database)
must implement this interface.

This ensures:
- Strategy layer does NOT depend on data source
- Backtest and Live share identical API
- Timeframes are dynamically configurable
"""

from abc import ABC, abstractmethod
import pandas as pd


class BasePriceProvider(ABC):

    @abstractmethod
    def get_candles(self, timeframe: int, up_to_time=None) -> pd.DataFrame:
        """
        Retrieve candle data for a given timeframe.

        Parameters:
        ----------
        timeframe : int
            Candle timeframe in minutes (1, 3, 5, 15, etc.)

        up_to_time : datetime (optional)
            If provided, return only candles up to this timestamp.
            Used in backtesting to simulate progressive time.

        Returns:
        -------
        pd.DataFrame
            DataFrame containing:
            ['datetime', 'open', 'high', 'low', 'close', 'volume']
        """
        pass