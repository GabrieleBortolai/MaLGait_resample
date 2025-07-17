#!/usr/bin/env python
# -*- coding: utf-8 -*

import csv

import numpy as np
from scipy import interpolate

from typing import List
from pathlib import Path


import common

# TODO: Remove samples after first dup


def resample_sensor_data(
    csv_reader_source: csv.DictReader,
    target_freq_hz: float,
    time_col: str,
) -> List[dict]:
    # Extract source data
    source_rows = list(csv_reader_source)
    source_timestamps = [float(row[time_col]) for row in source_rows]

    # Calculate target timestamps based on average frequency
    start_time = source_timestamps[0]
    end_time = source_timestamps[-1]
    target_period_ns = 1e9 / target_freq_hz
    target_timestamps = np.arange(start_time, end_time + 1, target_period_ns)

    # Resample the sensor data
    resampled_data = np.column_stack(
        [target_timestamps]
        + [
            interpolate.interp1d(
                source_timestamps,
                [float(row[col]) for row in source_rows],
                kind="linear",
                bounds_error=False,
                fill_value="extrapolate",  # type: ignore
            )(target_timestamps)
            for col in source_rows[0].keys()
            if col != time_col
        ]
    )

    # Convert resampled data back to list of dictionaries
    resampled_dicts = []
    for row in resampled_data:
        resampled_dicts.append(
            {time_col: row[0]}
            | {
                col: row[i]
                for i, col in enumerate(source_rows[0].keys())
                if col != time_col
            }
        )
    return resampled_dicts


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 5:
        print(
            "Usage: python resample_sensor.py <source_csv> <time_col> <freq> <target_csv>"
        )
        sys.exit(1)

    source_csv = common.open_csv(Path(sys.argv[1]))
    time_col = sys.argv[2]
    target_freq_hz = float(sys.argv[3])
    target_csv = Path(sys.argv[4])

    resampled_data = resample_sensor_data(source_csv, target_freq_hz, time_col)

    with open(target_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=resampled_data[0].keys())
        writer.writeheader()
        writer.writerows(resampled_data)

    sys.exit(0)
