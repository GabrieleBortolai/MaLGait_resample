#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import csv
import pandas as pd
import os

from pathlib import Path
from multiprocessing import Pool

import resample_freq
import resample_sensor
import common
import fill_cam


def fill_proc(camera_csv, data_csv, time_col, data_cols, output_cam_csv , output_data_csv, interpolation_method):
    temp_csv = None
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

    # If the target CSV is an IMU, remove duplicates
    if "imu" in data_csv.stem.lower():
        target_freq_hz = 60.0

        resampled_data = resample_sensor.remove_sensor_duplicates(
            common.open_csv(data_csv),
            time_col,
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

    if "imu" in data_csv.stem.lower():
        temp_csv.unlink() # type: ignore

def run_parallel_fill_proc():
    args = [
        (global_path / videos[0], global_path_save / names[0], starts[0], ends[0]),
        (global_path / videos[1], global_path_save / names[1], starts[0], ends[0]),
        (global_path / videos[2], global_path_save / names[2], starts[1], ends[1]),
        (global_path / videos[3], global_path_save / names[3], starts[1], ends[1]),
    ]

    with Pool(processes = 4) as pool:
        pool.starmap(fill_proc, args)

if __name__=="__main__":

    global_path_sync = Path("/media/user/My Passport1/MaLGait_sync")
    global_path_sync_fill = Path("/media/user/My Passport1/MaLGait_sync")

    # global_path_sync_fill.mkdir(exist_ok = True, parents = True)

    try:
        for user in sorted(os.listdir(global_path_sync)[:1]):
            cases_path = global_path_sync / user

            cases_path_filter = list(filter(lambda x: not x.endswith(".txt"), os.listdir(cases_path)))

            for case in sorted(cases_path_filter)[:1]:

                ZED_1_path = cases_path / case / "ZED_1"
                ZED_2_path = cases_path / case / "ZED_2"

                timestamp_zed_1 = ZED_1_path / "timestamp_1080_1_sync.csv"
                timestamp_zed_2 = ZED_2_path / "timestamp_1080_2_sync.csv"

                IMUs_path = cases_path / case / "IMUs"
                imus_files = sorted(os.listdir(IMUs_path))

                IMUs_paths = [IMUs_path / imu for imu in imus_files]
                print(IMUs_paths)

                samsung_path = cases_path / case / "Sensor_Logger"
                samsung_files = os.listdir(samsung_path)
                
                samsung_path = [samsung_path / samsung for samsung in samsung_files]

                user_path = cases_path / case / "User_Phone"
                user_files = os.listdir(user_path)

                user_paths = [user_path / user_phone for user_phone in user_files]

                print(zip(timestamp_zed_1))

                

                
        # camera_csv = Path("./timestamp_1080_1_sync.csv")
        # data_csv = Path("./imu_0_data_sync.csv")
        # time_col = "time_ms_loc"
        # data_cols = ["z", "y", "x"]
        # data_cols_imus=["wx", "wy", "wz", "ax", "ay", "az", "gx", "gy", "gz"]
        # output_cam_csv = Path("./cam.csv")
        # output_data_csv = Path("./data.csv")
        # interpolation_method = "linear"
        # fill_proc(camera_csv, data_csv, time_col, data_cols, output_cam_csv, output_data_csv, interpolation_method)
    except Exception as e:
        print(f"Error: {e}")