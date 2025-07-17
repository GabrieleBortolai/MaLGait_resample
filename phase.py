#!/usr/bin/env python
# -*- coding: utf-8 -*-

# python phase.py imu_3_data_sync_fill.csv imu_1_data_sync_fill.csv 30 ax

# - IMU_0 = upper right leg
# - IMU_1 = lower right leg
# - IMU_2 = upper left leg
# - IMU_3 = lower left leg


import sys

import numpy as np

from scipy.signal import butter, filtfilt
from scipy.signal import find_peaks

from pathlib import Path

import common


def butter_lowpass_filter(
    data: np.ndarray,
    cutoff: float,
    fs: float,
    order: int = 4,
):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype="low", analog=False)  # type: ignore
    return filtfilt(b, a, data)


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    if len(sys.argv) < 6:
        print(
            "Usage: phase.py <left_data_csv> <right_data_csv> <freq> <col> <start:end>"
        )
        sys.exit(1)

    left_data_csv = common.open_csv(Path(sys.argv[1]))
    right_data_csv = common.open_csv(Path(sys.argv[2]))
    freq = float(sys.argv[3])
    col = sys.argv[4]
    start, end = map(int, sys.argv[5].split(":"))

    left_data_rows = list(left_data_csv)
    right_data_rows = list(right_data_csv)

    left_data_rows = left_data_rows[start:end]
    right_data_rows = right_data_rows[start:end]

    time = np.arange(len(left_data_rows)) / freq  # Time axis in seconds

    left_data = np.array([float(row[col]) for row in left_data_rows])
    right_data = np.array([float(row[col]) for row in right_data_rows])

    left_mean = np.mean(left_data)
    right_mean = np.mean(right_data)

    left_data -= left_mean
    right_data -= right_mean

    left_data_filt = butter_lowpass_filter(left_data, cutoff=5, fs=freq, order=4)
    right_data_filt = butter_lowpass_filter(right_data, cutoff=5, fs=freq, order=4)

    peaks_left, _ = find_peaks(left_data_filt, height=0.1 * freq)
    peaks_right, _ = find_peaks(right_data_filt, height=0.1 * freq)

    valleys_left, _ = find_peaks(-left_data_filt, height=0.1 * freq)
    valleys_right, _ = find_peaks(-right_data_filt, height=0.1 * freq)

    left_data_filt += left_mean
    right_data_filt += right_mean

    plt.figure(figsize=(12, 6))

    # Plot both feet data
    plt.plot(time, left_data_filt, label="Left Foot Acc (filtered)", color="blue")
    plt.plot(time, right_data_filt, label="Right Foot Acc (filtered)", color="red")

    # Plot peaks and valleys for left foot
    plt.plot(
        time[peaks_left],
        left_data_filt[peaks_left],
        "bo",
        markersize=8,
    )
    plt.plot(
        time[valleys_left],
        left_data_filt[valleys_left],
        "bx",
        markersize=8,
    )

    # Plot peaks and valleys for right foot
    plt.plot(
        time[peaks_right],
        right_data_filt[peaks_right],
        "ro",
        markersize=8,
    )
    plt.plot(
        time[valleys_right],
        right_data_filt[valleys_right],
        "rx",
        markersize=8,
    )

    plt.legend()
    plt.xlabel("Time (s)")
    plt.ylabel("Acc")
    plt.title("GAIT Phase Detection")
    plt.grid(True, alpha=0.3)
    plt.show()
