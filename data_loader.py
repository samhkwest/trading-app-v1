# data_loader.py

import pandas as pd

def load_local_data(path):
    df = pd.read_parquet(path)
    df = df.sort_values('datetime').reset_index(drop=True)
    return df