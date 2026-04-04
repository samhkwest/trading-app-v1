#!/usr/bin/env python3

import sys
import os
import pandas as pd

def convert_parquet_to_csv(parquet_path):
    # Validate file existence
    if not os.path.isfile(parquet_path):
        print(f"Error: File not found -> {parquet_path}")
        sys.exit(1)

    if not parquet_path.lower().endswith(".parquet"):
        print("Error: Input file must have a .parquet extension")
        sys.exit(1)

    try:
        # Read parquet file
        df = pd.read_parquet(parquet_path)

        # Create output CSV path (same directory, same name)
        csv_path = os.path.splitext(parquet_path)[0] + ".csv"

        # Write to CSV
        df.to_csv(csv_path, index=False)

        print(f"Successfully converted:")
        print(f"Parquet: {parquet_path}")
        print(f"CSV:     {csv_path}")

    except Exception as e:
        print(f"Conversion failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python parquet_to_csv.py <absolute_parquet_file_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    convert_parquet_to_csv(input_path)