"""Rust measurements of the installed wiring's recorded clamped splines."""
from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
import json


@lru_cache(maxsize=64)
def _measure(encoded):
    import _rust_part

    request = json.loads(encoded)
    return _rust_part.check("machine", "wire-route-samples", {"splines": [request]})["splines"][0]


def measure(segment):
    """Keep the authored curve recipe and return its length-based scalar samples."""
    request = {key: segment[key] for key in
               ("interpolation_points_mm", "endpoint_derivatives", "parameters")}
    result = deepcopy(_measure(json.dumps(request, sort_keys=True)))
    result["sampled_points_mm"] = [tuple(point) for point in result["sampled_points_mm"]]
    return result
