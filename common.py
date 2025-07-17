#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv

from pathlib import Path


def open_csv(file_path: Path) -> csv.DictReader:
    if not file_path.exists():
        raise FileNotFoundError(f"File {file_path} does not exist.")
    if not file_path.is_file():
        raise IsADirectoryError(f"{file_path} is a directory, not a file.")

    return csv.DictReader(file_path.open("r", encoding="utf-8"))
