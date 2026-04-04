# data_loader.py

import pandas as pd


def load_local_data(path):
    """
    Load CSV data safely with datetime parsing.
    """

    df = pd.read_csv(path, parse_dates=['datetime'])

    df = (
        df.sort_values('datetime')
          .drop_duplicates('datetime')
          .reset_index(drop=True)
    )

    return df