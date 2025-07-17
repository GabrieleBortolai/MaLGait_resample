#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import csv
import numpy as np

from typing import Tuple
from pathlib import Path

import common


def get_estimated_frequencies(
    csv_reader: csv.DictReader,
    col: str,
    frames: int,
    time_scale: float,
) -> np.ndarray:
    # Convert CSV rows to list and extract timestamps
    rows = list(csv_reader)
    timestamps = np.array([float(row[col]) for row in rows])

    windows = np.lib.stride_tricks.sliding_window_view(timestamps, window_shape=frames)
    intervals = np.diff(windows, axis=1)

    # Calculate mean interval for each window
    avg_intervals_ms = np.mean(intervals, axis=1)

    # Convert to frequency in Hz (1/seconds)
    frequencies = time_scale / avg_intervals_ms

    return frequencies


def get_outlier_frequencies(
    frames: np.ndarray,
    frequencies: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    data = sorted(zip(frames, frequencies), key=lambda x: x[1])
    sorted_frames, sorted_frequencies = zip(*data)

    n = len(sorted_frequencies)

    # Plain IQR method to find outliers
    q1 = sorted_frequencies[n // 4]
    q3 = sorted_frequencies[3 * n // 4]
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outlier_frequencies = []
    outlier_frames = []

    for frame, freq in zip(sorted_frames, sorted_frequencies):
        if freq < lower_bound or freq > upper_bound:
            outlier_frequencies.append(freq)
            outlier_frames.append(frame)

    return np.array(outlier_frequencies), np.array(outlier_frames)


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    if len(sys.argv) < 4:
        print(
            "Usage: python check_freq.py <csv_file> <column_name> <frames> [<time_scale>]"
        )
        print(
            "Example: python check_freq.py timestamp_1080_1_sync.csv time_ms_loc 30 1000"
        )
        sys.exit(1)

    csv_file = Path(sys.argv[1])
    column_name = sys.argv[2]
    frames = int(sys.argv[3])
    time_scale = float(sys.argv[4]) if len(sys.argv) > 4 else 1000.0  # Default to ms

    try:
        csv_reader = common.open_csv(csv_file)
        estimated_frequencies = get_estimated_frequencies(
            csv_reader,
            column_name,
            frames=frames,
            time_scale=time_scale,
        )
    except (FileNotFoundError, IsADirectoryError) as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

    # Plot the frequencies info
    avg_frequency = sum(estimated_frequencies) / len(estimated_frequencies)
    deviations = [freq - avg_frequency for freq in estimated_frequencies]
    frame_numbers = np.arange(len(estimated_frequencies))

    plt.figure(figsize=(10, 5))
    plt.plot(
        frame_numbers, deviations, "b-", linewidth=1.5, label="Frequency Deviation"
    )
    plt.scatter(frame_numbers, deviations, c="blue", s=20, alpha=0.7)
    plt.axhline(
        y=0,
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Average Frequency ({avg_frequency:.2f} Hz)",
    )
    plt.grid(True, alpha=0.3)
    plt.xlabel("Frame Number")
    plt.ylabel("Frequency Deviation from Average (Hz)")
    plt.title("Frequency Deviation from Average Over Frames")
    plt.legend()

    # Add statistics text box
    std_dev = np.std(deviations)
    max_dev = max(abs(d) for d in deviations)

    stats_text = f"Avg Freq: {avg_frequency:.2f} Hz\nStd Dev: {std_dev:.3f} Hz\nMax Dev: {max_dev:.3f} Hz"
    plt.text(
        0.02,
        0.98,
        stats_text,
        transform=plt.gca().transAxes,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
    )

    plt.tight_layout()
    plt.show()

    outlier_frequencies, outlier_frames = get_outlier_frequencies(
        frame_numbers,
        estimated_frequencies,
    )
    if len(outlier_frequencies) > 0:
        print("Outlier Frequencies Detected:")
        for freq, frame in zip(outlier_frequencies, outlier_frames):
            print(f"Frame {frame}: Frequency {freq:.2f} Hz")
    else:
        print("No outlier frequencies detected.")

    sys.exit(0)
