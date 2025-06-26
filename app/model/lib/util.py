import re
import math
import itertools
import zipfile
import gzip
import shutil
from io import BytesIO
from pathlib import Path

import requests


def is_non_negative_float(string, *, isnan_check):
    try:
        value = float(string)
        if isnan_check:
            return not math.isnan(value) and value >= 0.0
        else:
            return math.isnan(value) or value >= 0.0
    except ValueError:
        return False


def trim_lines(string):
    return "\n".join(
        line.strip()
        for line in string.splitlines()
        if line != ''
    )


def createzip(csv_data: list[tuple[str, bytes]]):
    buf = BytesIO()

    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as csv_zip:
        for (csv_name, csv_bytes) in csv_data:
            csv_zip.writestr(csv_name, csv_bytes)

    buf.seek(0)
    return buf


def group_by_unique_name(collection):
    return {
        name: _one_or_error(name, group)
        for (name, group) in itertools.groupby(collection, lambda c: c.name)
    }


def humanize_camelcased_string(string):
    return re.sub(r'([a-z])([A-Z])', r'\1 \2', string)


# Adapted from: https://stackoverflow.com/a/16696317
def download_file(url, filename):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()

        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


def gunzip(path, extracted_path=None):
    gz_path = Path(path)
    if gz_path.suffix != '.gz':
        raise ValueError(f"Path doesn't end in .gz: {path}")

    if extracted_path is None:
        extracted_path = gz_path.parent / gz_path.stem

    with gzip.open(gz_path, 'rb') as f_in:
        with open(extracted_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def _one_or_error(key, iterator):
    value = next(iterator)
    try:
        next(iterator)
        # If we're here, we have more than one item
        raise ValueError(f"Non-unique key: {key}")
    except StopIteration:
        return value
