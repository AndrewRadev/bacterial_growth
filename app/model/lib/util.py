import re
import math
import itertools
import zipfile
import gzip
import tarfile
import shutil
from io import BytesIO
from pathlib import Path
from typing import Optional, Iterable
from datetime import datetime, UTC

import requests


def is_non_negative_float(string: str, *, isnan_check: bool):
    """
    Check if the given string value represents a finite float.

    This is used for validating data coming from Excel spreadsheets. It's a bit
    hacky, there might be cleaner approaches.
    """

    try:
        value = float(string)
        if isnan_check:
            return not math.isnan(value) and value >= 0.0
        else:
            return math.isnan(value) or value >= 0.0
    except ValueError:
        return False


def trim_lines(string: str):
    "Trim the whitespace from all the lines in the given string."

    return "\n".join(
        line.strip()
        for line in string.splitlines()
        if line != ''
    )


def createzip(csv_data: list[tuple[str, bytes]]) -> BytesIO:
    "Create a zip file from the given CSV files (as bytes)"

    buf = BytesIO()

    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as csv_zip:
        for (csv_name, csv_bytes) in csv_data:
            csv_zip.writestr(csv_name, csv_bytes)

    buf.seek(0)
    return buf


def group_by_unique_name(collection: Iterable) -> dict:
    """
    Group the items in the collection by their ``name``.

    Raises an error if there is more than one element with the same name.
    """

    return {
        name: _one_or_error(name, group)
        for (name, group) in itertools.groupby(collection, lambda c: c.name)
    }


def humanize_camelcased_string(string: str):
    "Separates words in camelCased strings with spaces"
    return re.sub(r'([a-z])([A-Z])', r'\1 \2', string)


# Adapted from: https://stackoverflow.com/a/16696317
def download_file(url: str, filename: str):
    "Downloads the data from the given URL into the target filename"
    with requests.get(url, stream=True) as r:
        r.raise_for_status()

        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


def gunzip(path: Path, extracted_path: Optional[Path] = None):
    """
    Extracts the given gzip file.

    If no output path is given, removes the ``.gz`` suffix and uses that as the output path.
    """
    gz_path = Path(path)
    if gz_path.suffix != '.gz':
        raise ValueError(f"Path doesn't end in .gz: {path}")

    if extracted_path is None:
        extracted_path = gz_path.parent / gz_path.stem

    with gzip.open(gz_path, 'rb') as f_in:
        with open(extracted_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def untar(path: Path, target_dir: Path, file_list: list[str]):
    """
    Extracts individual files from a tar file into the given `target_dir`.

    File paths inside the tar file are listed in `file_list`.
    """
    tar_path = Path(path)
    if '.tar' not in tar_path.suffixes:
        raise ValueError(f"Path doesn't include .tar suffix: {path}")

    target_dir = Path(target_dir)

    with tarfile.open(tar_path, 'r') as tar_f:
        for filename in file_list:
            tar_f.extract(filename, path=target_dir)


def read_timestamp_date(path):
    """
    Reads the contents of a file, if it exists, and interpret them as a
    timestamp. Returns the time formatted as a date.
    """
    timestamp = None
    timestamp_path = Path(path)

    if timestamp_path.exists():
        content = timestamp_path.read_text().strip()
        if content != '':
            timestamp = datetime.fromisoformat(content).strftime("%b %d, %Y")

    return timestamp


def _one_or_error(key, iterator):
    value = next(iterator)
    try:
        next(iterator)
        # If we're here, we have more than one item
        raise ValueError(f"Non-unique key: {key}")
    except StopIteration:
        return value
