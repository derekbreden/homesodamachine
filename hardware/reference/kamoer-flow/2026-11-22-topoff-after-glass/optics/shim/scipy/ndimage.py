"""SciPy's ndimage 1-D filters reproduced in NumPy with its default reflect mode, so the frozen cup reader runs where SciPy is not installed."""
import numpy as np


def _windows(x, before, after, axis):
    x = np.asarray(x)
    x = np.moveaxis(x, axis, -1)
    pad = [(0, 0)] * (x.ndim - 1) + [(before, after)]
    p = np.pad(x, pad, mode='symmetric')
    n = x.shape[-1]
    return x, p, n


def _size_split(size):
    before = size // 2
    return before, size - before - 1


def correlate1d(x, weights, axis=-1):
    weights = np.asarray(weights, dtype=np.float64)
    size = len(weights)
    before, after = _size_split(size)
    x0, p, n = _windows(x, before, after, axis)
    out = np.zeros(x0.shape, dtype=np.float64)
    for k, w in enumerate(weights):
        out += w * p[..., k:k + n]
    if np.issubdtype(x0.dtype, np.integer):
        out = np.rint(out).astype(x0.dtype)
    return np.moveaxis(out, -1, axis)


def gaussian_filter1d(x, sigma, axis=-1, truncate=4.0):
    radius = int(truncate * float(sigma) + 0.5)
    t = np.arange(-radius, radius + 1, dtype=np.float64)
    w = np.exp(-0.5 / (sigma * sigma) * t * t)
    w /= w.sum()
    return correlate1d(x, w, axis)


def uniform_filter1d(x, size, axis=-1):
    return correlate1d(x, np.full(size, 1.0 / size), axis)


def _rank(x, size, axis, fn):
    before, after = _size_split(size)
    x0, p, n = _windows(x, before, after, axis)
    out = p[..., 0:n].copy()
    for k in range(1, size):
        out = fn(out, p[..., k:k + n])
    return np.moveaxis(out, -1, axis)


def maximum_filter1d(x, size, axis=-1):
    return _rank(x, size, axis, np.maximum)


def minimum_filter1d(x, size, axis=-1):
    return _rank(x, size, axis, np.minimum)
