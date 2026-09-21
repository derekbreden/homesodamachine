"""Conservative G Ganen clearance shape, separate from the detailed reference.

Measured slots, feet, rails, ports and datum APIs come from the frozen reference.
This solid is an occupied envelope, not material or a mount-passage certificate.
"""
from functools import lru_cache
from pathlib import Path
import hashlib
import json
import sys

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
REFERENCE = HERE.parent
NATIVE = HERE/'g-ganen-integration-envelope.step'
sys.path.insert(0, str(REFERENCE))
from g_ganen_pump import (parameters, port, suction, discharge, mount_slots,
                         port_profile, sliding_rails, mount_seat_z)


@lru_cache(maxsize=1)
def _native_parts(native_time, native_size, proof_time):
    proof = json.loads((HERE/'native-validation.json').read_text())
    if not proof['all_native_solids_valid']:
        raise ValueError('Integration envelope is not qualified')
    if hashlib.sha256(NATIVE.read_bytes()).hexdigest() != proof['native_sha256']:
        raise ValueError('Integration envelope STEP differs from its proof')
    remaining = list(cq.importers.importStep(str(NATIVE)).val().Solids())
    result = {}
    for row in proof['components']:
        target = np.asarray(row['bounds_mm'])
        matches = []
        for shape in remaining:
            box = shape.BoundingBox()
            actual = [[box.xmin, box.ymin, box.zmin], [box.xmax, box.ymax, box.zmax]]
            if np.allclose(actual, target, atol=1e-5, rtol=0):
                matches.append(shape)
        if len(matches) != 1:
            raise ValueError('Cannot identify integration solid: '+row['name'])
        result[row['name']] = matches[0]
        remaining.remove(matches[0])
    if remaining:
        raise ValueError('Unidentified integration solids')
    return result


def build_parts():
    """Separate rigid components and observed, independently movable rubber feet."""
    stat = NATIVE.stat()
    proof_stat = (HERE/'native-validation.json').stat()
    return dict(_native_parts(stat.st_mtime_ns, stat.st_size, proof_stat.st_mtime_ns))


def build():
    return cq.Workplane(obj=cq.Compound.makeCompound(list(build_parts().values())))


def build_scene():
    return build().val()


def build_assembly():
    assembly = cq.Assembly(name='g-ganen-integration-envelope')
    for name, shape in build_parts().items():
        color = (.18, .19, .20) if 'rubber_slider' in name else (.45, .58, .63)
        assembly.add(shape, name=name, color=cq.Color(*color))
    return assembly
