"""Perlin noise, vectorised over numpy point arrays.

Classic 3D Perlin plus the fractal sum built on it. Sampled in WORLD space by every
caller here, so a grain laid on a part runs continuously across its arrises and faces
instead of restarting per surface — which is the whole reason a baked texture reads as
a material and a per-layer slicer texture reads as noise.

`fbm` returns a field scaled so its own extreme reaches ±1. An amplitude in mm handed
to it is then the displacement that amplitude actually buys, rather than an upper bound
the octave sum never approaches.
"""

import numpy as np


def _fade(t):
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


def perlin3(points, permutation):
    """Classic 3D Perlin over an (n, 3) array of sample positions."""
    lattice = np.floor(points).astype(np.int64)
    frac = points - lattice
    cell = lattice & 255
    fade = _fade(frac)

    def hashed(dx, dy, dz):
        a = permutation[cell[:, 0] + dx]
        b = permutation[(a + cell[:, 1] + dy) & 511]
        return permutation[(b + cell[:, 2] + dz) & 511]

    def dot(h, dx, dy, dz):
        gx, gy, gz = frac[:, 0] - dx, frac[:, 1] - dy, frac[:, 2] - dz
        low = h & 15
        u = np.where(low < 8, gx, gy)
        v = np.where(low < 4, gy, np.where((low == 12) | (low == 14), gx, gz))
        return np.where(low & 1 == 0, u, -u) + np.where(low & 2 == 0, v, -v)

    def lerp(a, b, t):
        return a + t * (b - a)

    corners = {(dx, dy, dz): dot(hashed(dx, dy, dz), dx, dy, dz)
               for dx in (0, 1) for dy in (0, 1) for dz in (0, 1)}
    along_x = [lerp(corners[(0, dy, dz)], corners[(1, dy, dz)], fade[:, 0])
               for dy in (0, 1) for dz in (0, 1)]
    return lerp(lerp(along_x[0], along_x[2], fade[:, 1]),
                lerp(along_x[1], along_x[3], fade[:, 1]),
                fade[:, 2])


def permutation_for(seed):
    base = np.random.default_rng(seed).permutation(256)
    return np.concatenate([base, base])


def fbm(points, feature_size, octaves=4, persistence=0.5, seed=0):
    """Fractal Perlin at `octaves` octaves, the first with a `feature_size` wavelength,
    scaled so the field's own extreme reaches ±1."""
    permutation = permutation_for(seed)
    total = np.zeros(len(points))
    amplitude, frequency = 1.0, 1.0 / feature_size
    for octave in range(octaves):
        shift = 37.13 * (octave + 1)
        total += amplitude * perlin3(points * frequency + shift, permutation)
        amplitude *= persistence
        frequency *= 2.0
    return total / np.abs(total).max()
