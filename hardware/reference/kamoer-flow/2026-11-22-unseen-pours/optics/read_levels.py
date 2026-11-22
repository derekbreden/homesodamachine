"""Read both cup contacts with the previously frozen camera calibration."""
from pathlib import Path
import json
import numpy as np
from cup_volume import crop
from mark_crossings_v3 import clear_lane

CALIBRATION = json.loads((Path(__file__).parent / 'geometry-used.json').read_text())


def measure(path):
    gray = np.asarray(crop(Path(path) / 'average.png').convert('L'))
    return measure_gray(gray)


def measure_gray(gray):
    result = {}
    for site in ('x990', 'x1986'):
        row, contrast = clear_lane(gray, int(site[1:]))
        anchors = sorted(CALIBRATION['anchors'][site])
        inside = anchors[0][0] <= row <= anchors[-1][0] and contrast >= 6
        volume = float(np.interp(row, *zip(*anchors))) if inside else None
        result[site] = dict(row=row, contrast=contrast, ml=volume)
    return result
