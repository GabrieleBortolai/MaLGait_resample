#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import matplotlib.pyplot as plt
import numpy as np

from pathlib import Path

import common

if len(sys.argv) < 4:
    print("Usage: plot.py <file> <sample_rate> <cols>")
    print("Example: plot.py data.csv 100 x,y,z")
    sys.exit(1)


file = Path(sys.argv[1])
sample_rate = int(sys.argv[2])
cols = sys.argv[3].split(",")
csv = common.open_csv(file)
rows = list(csv)

t = np.arange(len(rows)) / sample_rate  # Time axis in seconds

plt.figure(figsize=(10, 6))
for col in cols:
    if col in rows[0]:
        x = np.array([float(row[col]) for row in rows])
        plt.plot(t, x, label=col)
plt.xlabel("Time (s)")
plt.ylabel("Angular Velocity (deg/s)")
plt.title("Data Over Time")
plt.legend()
plt.grid(True)
plt.show()
