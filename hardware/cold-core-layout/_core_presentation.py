"""Finish cold-core shown surfaces and bind them to the authoritative fine archive."""

import math
from pathlib import Path

import numpy as np


def bind(model, payload):
    """Replace only the model document's presentation binding; keep all other members exact."""
    from meshcad.presentation import bind as bind_presentation
    return bind_presentation(model, payload)


def placement(row):
    """The same ordered source-frame carry used for the body's fine geometry."""
    matrix = np.eye(4)

    def turn(rotation):
        nonlocal matrix
        axis = np.asarray(rotation['axis'], dtype=float)
        axis /= np.linalg.norm(axis)
        x, y, z = axis
        skew = np.array([[0., -z, y], [z, 0., -x], [-y, x, 0.]])
        angle = math.radians(rotation['degrees'])
        value = np.eye(4)
        value[:3, :3] = (math.cos(angle) * np.eye(3) + math.sin(angle) * skew
                         + (1. - math.cos(angle)) * np.outer(axis, axis))
        matrix = value @ matrix

    def shift(vector):
        nonlocal matrix
        value = np.eye(4)
        value[:3, 3] = vector
        matrix = value @ matrix

    for rotation in row.get('rotations', ()):
        turn(rotation)
    if 'rotation_z_degrees' in row:
        turn({'axis': (0., 0., 1.), 'degrees': row['rotation_z_degrees']})
    if 'translation' in row:
        shift(row['translation'])
    if 'transform' in row:
        value = np.eye(4)
        value[:3, :3] = np.asarray(row['transform']['columns']).T
        value[:3, 3] = row['transform']['translation']
        matrix = value @ matrix
    for rotation in row.get('after_rotations', ()):
        turn(rotation)
    if 'after_translation' in row:
        shift(row['after_translation'])
    return matrix


def carried(surface, row):
    matrix = placement(row)
    linear, offset = matrix[:3, :3], matrix[:3, 3]
    return {**surface,
            'pos': (np.asarray(surface['pos'], dtype=float).reshape(-1, 3) @ linear.T + offset).ravel(),
            'nrm': (np.asarray(surface['nrm'], dtype=float).reshape(-1, 3) @ np.linalg.inv(linear)).ravel()}


def finish(step, rows):
    """Graft the current printed surfaces and bind that final payload to its fine model."""
    from _cadq_export import note_read, note_write
    import flute_payload

    step = Path(step)
    payload = step.with_name(step.name + '.mesh')
    for part, _stl in flute_payload.pieces(flute_payload.COLD_CORE_DIRS):
        note_read(part)
        note_read(part.with_name(part.name + '.mesh'))
    surfaces = flute_payload.surfaces(flute_payload.COLD_CORE_DIRS)
    placed = {row['name']: carried(surfaces[row['name']], row)
              for row in rows if row['name'] in surfaces}
    grafted = flute_payload.graft(payload, placed, same_frame=True)
    if grafted:
        note_write(payload)
        print(f'-> {payload.name}  ({grafted} fluted piece(s))')
    bind(step.with_name(step.name + '.npz'), payload)
    return grafted
