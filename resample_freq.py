#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv

import numpy as np
from scipy import interpolate

from typing import List, Tuple
from pathlib import Path

import common


def resample_signal(
    source_timestamps: np.ndarray,
    source_values: np.ndarray,
    target_timestamps: np.ndarray,
    interpolation_method: str = "linear",
) -> np.ndarray:
    interp_func = interpolate.interp1d(
        source_timestamps,
        source_values,
        kind=interpolation_method,
        bounds_error=False,
        assume_sorted=False,
        fill_value="extrapolate",  # type: ignore
    )
    resampled_values = interp_func(target_timestamps)

    return resampled_values


def resample_signal_from_csv(
    csv_reader_source: csv.DictReader,
    csv_reader_target: csv.DictReader,
    source_time_col: str,
    source_value_cols: List[str],
    target_time_col: str,
    interpolation_method: str = "linear",
) -> Tuple[np.ndarray, np.ndarray]:
    # Extract target data
    target_rows = list(csv_reader_target)
    target_timestamps = np.array([float(row[target_time_col]) for row in target_rows])

    # Extract source data
    source_rows = list(csv_reader_source)
    source_timestamps = np.array([float(row[source_time_col]) for row in source_rows])
    source_values = np.array(
        [[float(row[col]) for col in source_value_cols] for row in source_rows]
    )

    # Resample each source value column
    interp_func = interpolate.interp1d(
        source_timestamps,
        source_values,
        axis=0,  # Interpolate along the columns (values)
        kind=interpolation_method,
        bounds_error=False,
        assume_sorted=False,
    )

    return interp_func(target_timestamps), target_timestamps


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 7:
        print(
            "Usage: python resample_freq.py <source_csv> <target_csv> <source_time_col> <source_value_cols> <target_time_col> <output_csv> [interpolation_method]"
        )
        sys.exit(1)

    source_csv = common.open_csv(Path(sys.argv[1]))
    target_csv = common.open_csv(Path(sys.argv[2]))
    source_time_col = sys.argv[3]
    source_value_cols = sys.argv[4].split(",")
    target_time_col = sys.argv[5]
    output_csv = Path(sys.argv[6])
    interpolation_method = sys.argv[7] if len(sys.argv) > 7 else "linear"

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [target_time_col] + source_value_cols
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for resampled_values, target_timestamps in zip(
            *resample_signal_from_csv(
                source_csv,
                target_csv,
                source_time_col,
                source_value_cols,
                target_time_col,
                interpolation_method=interpolation_method,
            )
        ):
            row = {target_time_col: target_timestamps}
            for col, value in zip(source_value_cols, resampled_values):
                row[col] = value
            writer.writerow(row)

    print(f"Resampled data written to {output_csv}")
    sys.exit(0)
