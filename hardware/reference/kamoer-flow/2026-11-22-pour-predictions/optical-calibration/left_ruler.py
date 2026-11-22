#!/usr/bin/env python3
"""Read the quarter-cup scale using photograph columns outside both the right dose estimator and the positioning strip."""
import importlib.util
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('quarter_cup_camera', HERE/'cup_volume.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)
# The positioning gate averages the pixel columns inclusive of these bounds.
CONTROL_COLUMNS = (986, 994)
LEFT_STATIONS = [x for x in reader.SITES['quarters'] if x+3 < CONTROL_COLUMNS[0] or x-3 > CONTROL_COLUMNS[1]]
reader.SITES = {**reader.SITES, 'quarters': LEFT_STATIONS}


def read(rgb, detail=False):
    # The left surface detector consumes only green-channel profiles and red quarter-cup strokes.
    return reader.face(np.zeros(rgb.shape[:2], dtype=np.uint8), rgb, 'quarters', detail)
