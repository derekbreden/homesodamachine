"""Finish cold-core shown surfaces and bind them to the authoritative fine archive."""

import json
import math
from pathlib import Path
import struct

import numpy as np


def bind(model, payload):
    """Replace only the model document's presentation binding; keep all other members exact."""
    import _machine_export
    _machine_export.graft(payload, [], model=model)


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


def printed_surfaces():
    """Current printed-core payloads, identified without loading their mesh arrays."""
    from _cadq_export import note_read
    import _mesh_payload

    cold = Path(__file__).resolve().parents[1] / 'printed-parts' / 'cold-core'
    surfaces = {}
    for directory in (cold / 'foam-shell', cold / 'foam-cap'):
        for step in sorted(directory.glob('*.step')):
            if not step.with_suffix('.stl').is_file():
                continue
            payload = step.with_name(step.name + '.mesh')
            note_read(step)
            note_read(payload)
            try:
                with payload.open('rb') as source:
                    header_size, = struct.unpack('<I', source.read(4))
                    header = json.loads(source.read(header_size))
            except OSError:
                continue
            entries = header.get('meshes', ())
            if header.get('v') not in _mesh_payload.DECODABLE or len(entries) != 1:
                continue
            stamped, current = header.get('src'), _mesh_payload.source_digest(step)
            if stamped != current:
                raise ValueError(
                    f"{payload.name} was cut from a {step.name} that is not the one beside it "
                    f"({str(stamped)[:12]} against {current[:12]}) — recut its printed surface")
            surfaces[entries[0]['name']] = {
                'payload': str(payload), 'source_sha256': current}
    return surfaces


def finish(step, rows):
    """Graft the current printed surfaces and bind that final payload to its fine model."""
    from _cadq_export import note_write
    import _machine_export

    step = Path(step)
    payload = step.with_name(step.name + '.mesh')
    surfaces = printed_surfaces()
    skins = [{**surfaces[row['name']], 'names': {row['name']: row['name']},
              'transform': placement(row)[:3, :4].tolist()}
             for row in rows if row['name'] in surfaces]
    result = _machine_export.graft(
        payload, skins, model=step.with_name(step.name + '.npz'))
    grafted = result['grafted']
    if grafted:
        note_write(payload)
        print(f'-> {payload.name}  ({grafted} fluted piece(s))')
    return grafted
