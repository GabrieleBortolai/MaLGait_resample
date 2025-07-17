#!/usr/bin/env python
# -*- coding: utf-8 -*

import csv

import pandas as pd


from typing import List
from pathlib import Path


import common


def remove_sensor_duplicates(
    csv_reader_source: csv.DictReader,
    time_col: str,
) -> List[dict]:
    # Extract source data
    source_rows = list(csv_reader_source)

    # Use pandas to handle duplicates
    df = pd.DataFrame(source_rows)

    df[time_col] = pd.to_numeric(df[time_col], errors="coerce")

    for col in df.columns:
        if col != time_col:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    res = df.groupby(time_col).mean().reset_index()

    return res.to_dict(orient="records")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        print("Usage: python resample_sensor.py <source_csv> <time_col> <target_csv>")
        sys.exit(1)

    source_csv = common.open_csv(Path(sys.argv[1]))
    time_col = sys.argv[2]
    target_csv = Path(sys.argv[3])

    resampled_data = remove_sensor_duplicates(source_csv, time_col)

    with open(target_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=resampled_data[0].keys())
        writer.writeheader()
        writer.writerows(resampled_data)

    sys.exit(0)
