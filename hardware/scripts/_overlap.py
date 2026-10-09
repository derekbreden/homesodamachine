"""The solid two bodies share.

`common(a, b)` hands back `(shape, mm³)`, where the shape is a `manifold3d.Manifold` and the
volume is what the two enclose between them. A body whose mesh does not close raises out of
`_meshes` rather than arriving here to be measured as a clean pair.

    import _overlap
    shape, vol = _overlap.common(a, b)
    vol = _overlap.volume(a, b)

The reading stands within the bound `_meshes` states. Two tubes of one Ø crossing axis-on-axis
share a Steinmetz solid of 16r³/3, and `_meshes.selftest` holds that crossing — a port row fixes
both runs to one z, so it is an arrangement the pack builds.
"""

import _meshes


def common(a, b) -> tuple:
    """The solid two bodies share and its volume, as `(shape, mm³)`. Empty is `(shape, 0.0)`."""
    shape = _meshes.meshed(a) ^ _meshes.meshed(b)
    return shape, shape.volume()


def volume(a, b) -> float:
    """Just the mm³ of `common`, for the checks that only threshold on it."""
    return common(a, b)[1]
