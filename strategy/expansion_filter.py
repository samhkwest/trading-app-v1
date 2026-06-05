# expansion_filter.py

import numpy as np

class ExpansionFilter:
    """
    Fix 5: Detect expansion regime.
    Returns True if trading is allowed.
    Returns False if expansion detected.
    """

    def __init__(
        self,
        atr_period=14,
        atr_lookback=50,
        atr_multiplier=1.3,
        persistence_window=10,
        persistence_threshold=0.7
    ):
        self.atr_period = atr_period
        self.atr_lookback = atr_lookback
        self.atr_multiplier = atr_multiplier
        self.persistence_window = persistence_window
        self.persistence_threshold = persistence_threshold

    def compute_atr(self, high, low, close):
        tr = np.maximum(
            high[1:] - low[1:],
            np.maximum(
                abs(high[1:] - close[:-1]),
                abs(low[1:] - close[:-1])
            )
        )
        atr = np.convolve(tr, np.ones(self.atr_period)/self.atr_period, mode='valid')
        return atr

    def directional_persistence(self, close):
        if len(close) < self.persistence_window + 1:
            return 0.0

        moves = np.diff(close[-self.persistence_window:])
        same_dir = np.sum(np.sign(moves) == np.sign(np.sum(moves)))
        return same_dir / self.persistence_window

    def evaluate(self, high, low, close):
        """
        Returns:
            True  -> Trading allowed
            False -> Expansion detected (block trading)
        """

        if len(close) < max(self.atr_period + self.atr_lookback, self.persistence_window + 1):
            return True  # Not enough data

        atr = self.compute_atr(high, low, close)

        current_atr = atr[-1]
        avg_atr = np.mean(atr[-self.atr_lookback:])

        atr_expansion = current_atr > avg_atr * self.atr_multiplier

        persistence = self.directional_persistence(close)
        strong_direction = persistence > self.persistence_threshold

        expansion_detected = atr_expansion and strong_direction

        return not expansion_detected