#!/usr/bin/env python
# -*- coding: utf-8 -*-

import common
import sys

import numpy as np

import matplotlib.pyplot as plt

from pathlib import Path

if len(sys.argv) < 4:
    print("Usage: fourier.py <file> <columns> <rate> <resampling_rate>")
    print("Example: fourier.py data.csv x,y,z 100")
    sys.exit(1)

file = Path(sys.argv[1])
cols = sys.argv[2].split(",")
rate = sys.argv[3]
resampling_rate = float(sys.argv[4])
csv = common.open_csv(file)

rows = list(csv)


def plot_fft(signal, sample_rate_hz, aliasing_start):
    n = len(signal)
    freqs = np.fft.rfftfreq(n, d=1 / sample_rate_hz)
    fft_vals = np.abs(np.fft.rfft(signal))

    plt.plot(freqs, fft_vals)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude")
    plt.title("FFT of Gyroscope Axis")
    plt.axvline(
        x=aliasing_start,
        color="red",
        linestyle="--",
        label=f"{aliasing_start} resampling Hz",
    )
    plt.legend()
    plt.grid()
    plt.show()


def energy_above_cutoff(signal, sample_rate_hz, cutoff_hz):
    n = len(signal)
    fft_vals = np.abs(np.fft.rfft(signal))
    freqs = np.fft.rfftfreq(n, d=1 / sample_rate_hz)

    total_energy = np.sum(fft_vals**2)
    high_freq_energy = np.sum((fft_vals[freqs > cutoff_hz]) ** 2)

    return high_freq_energy / total_energy


def aliasing_frequencies(sample_rate_hz, resampling_rate_hz):
    if resampling_rate_hz >= sample_rate_hz:
        return (0, 0)

    nyquist_freq = sample_rate_hz / 2
    nyquist_freq_resampling = resampling_rate_hz / 2

    return (nyquist_freq_resampling, nyquist_freq)


for col in cols:
    data = np.array([float(row[col]) for row in rows])

    aliasing_freqs = aliasing_frequencies(
        sample_rate_hz=float(rate), resampling_rate_hz=resampling_rate
    )

    plot_fft(data, sample_rate_hz=float(rate), aliasing_start=aliasing_freqs[0])

    energy = energy_above_cutoff(
        data, sample_rate_hz=float(rate), cutoff_hz=resampling_rate
    )
    print(f"Energy above {resampling_rate} Hz for {col}: {energy:.4f}")

    print(
        f"Aliasing frequencies for {col} at {resampling_rate} Hz: {aliasing_freqs[0]:.2f} Hz to {aliasing_freqs[1]:.2f} Hz"
    )
