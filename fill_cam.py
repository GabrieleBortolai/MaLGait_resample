#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv


def fill_cam_gaps(csv: csv.DictReader, time_col: str, gap_threshold_ms: float) -> list:
    filled_rows = []
    last_row = None

    for row in csv:
        if last_row is not None:
            delta = float(row[time_col]) - float(last_row[time_col])
            # Ideally it should be 1 / 30 Hz = 33.33 ms
            # If the gap is larger than the threshold, we fill it with the last row's
            # timestamp incremented by half the gap size
            if delta > gap_threshold_ms:
                last_row_copy = last_row.copy()
                last_row_copy[time_col] = str(int(float(last_row[time_col]) + delta / 2.0))
                filled_rows.append(last_row_copy)
        filled_rows.append(row)
        last_row = row

    return filled_rows


if __name__ == "__main__":
    import sys
    import csv

    import common

    from pathlib import Path

    if len(sys.argv) < 4:
        print("Usage: fill_cam.py <file> <time_col> <output_file>")
        print("Example: fill_cam.py data.csv time_ms_loc output.csv")
        sys.exit(1)

    file = Path(sys.argv[1])
    time_col = sys.argv[2]
    output_file = Path(sys.argv[3])

    # We know the camera works at ~30 Hz
    # If delta between two timestamps is greater than 40 ms, we fill the gap with the last value
    filled_rows = fill_cam_gaps(common.open_csv(file), time_col, gap_threshold_ms=40.0)

    # Write the filled data back to a new CSV file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", newline="", encoding="utf-8") as csvfile:
        fieldnames = filled_rows[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for filled_row in filled_rows:
            writer.writerow(filled_row)

    print(f"Filled data written to {output_file}")
    sys.exit(0)
