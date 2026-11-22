#!/usr/bin/env python3
"""Use the original x990 contact above the diagnosed wall reflection and the neighboring-lane correction below it."""
import importlib.util
from pathlib import Path

import mark_crossings_v2

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('range_limited_printed_caps', HERE / 'mark_crossings.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
original = base.clear_lane
LOWER_RANGE_START = 1065


def clear_lane(gray, site=990):
    y, contrast = original(gray, site)
    if site == 990 and y >= LOWER_RANGE_START:
        return mark_crossings_v2.clear_lane(gray, site)
    return y, contrast


base.clear_lane = clear_lane
read = base.read


if __name__ == '__main__':
    base.main()
