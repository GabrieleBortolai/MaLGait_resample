#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import csv
import pandas as pd

from pathlib import Path

import resample_freq
import resample_sensor
import common
import fill_cam

if len(sys.argv) < 7:
    print(
        "Usage: pipe.py <camera_csv> <data_csv> <time_col> <data_cols> <output_cam_csv> <output_data_csv> [interpolation_method]"
    )
    print(
        "Example: pipe.py timestamp_1080_1_sync.csv Gyroscope_sync.csv time_ms_loc z,y,x timestamp_1080_1_sync_fill.csv Gyroscope_sync_fill.csv"
    )
    sys.exit(1)

camera_csv = Path(sys.argv[1])
data_csv = Path(sys.argv[2])
time_col = sys.argv[3]
data_cols = sys.argv[4].split(",")
output_cam_csv = Path(sys.argv[5])
output_data_csv = Path(sys.argv[6])
interpolation_method = sys.argv[7] if len(sys.argv) > 7 else "linear"

# Fill gaps in camera data
filled_camera_rows = fill_cam.fill_cam_gaps(
    common.open_csv(camera_csv),
    time_col,
    gap_threshold_ms=40.0,
)

# Write filled camera data to output CSV
output_cam_csv.parent.mkdir(parents=True, exist_ok=True)
with output_cam_csv.open("w", newline="", encoding="utf-8") as csvfile:
    fieldnames = filled_camera_rows[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for filled_row in filled_camera_rows:
        writer.writerow(filled_row)

# If the target CSV is an IMU, resample first to 60 Hz
if "imu" in data_csv.stem.lower():
    target_freq_hz = 60.0

    resampled_data = resample_sensor.resample_sensor_data(
        common.open_csv(data_csv),
        target_freq_hz,
        "timestamp_ns",  # Specify the time column for resampling
    )

    # Write resampled data to output CSV
    temp_csv = output_data_csv.with_suffix(".temp.csv")
    temp_csv.parent.mkdir(parents=True, exist_ok=True)
    with temp_csv.open("w", newline="", encoding="utf-8") as csvfile:
        fieldnames = resampled_data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(resampled_data)

    data_csv = temp_csv  # Update data_csv to the resampled output

# Resample sensor data based on filled camera timestamps
output_data_csv.parent.mkdir(parents=True, exist_ok=True)
with output_data_csv.open("w", newline="", encoding="utf-8") as csvfile:
    fieldnames = [time_col] + data_cols
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for resampled_values, target_timestamps in zip(
        *resample_freq.resample_signal_from_csv(
            common.open_csv(data_csv),
            common.open_csv(output_cam_csv),
            source_time_col=time_col,
            source_value_cols=data_cols,
            target_time_col=time_col,
            interpolation_method=interpolation_method,
        )
    ):
        row = {time_col: target_timestamps}
        for col, value in zip(data_cols, resampled_values):
            row[col] = value
        writer.writerow(row)
