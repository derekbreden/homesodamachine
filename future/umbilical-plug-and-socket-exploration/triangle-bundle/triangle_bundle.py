"""Three equal tubes in a triangle; smaller tube added against one outer edge.

All five neighboring gaps and the exposed TPU skin are 0.85 mm. Hardware,
guard and counter-hole references come from the minimal packing scene.
"""
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'minimal-bundle'))
import minimal_bundle as b

PITCH = 6.35 + b.GAP
TRIANGLE_H = PITCH * math.sqrt(3) / 2
PAIR_REACH = 3.175 + 2 + b.GAP
OUTWARD_REACH = math.sqrt(PAIR_REACH**2 - (PITCH/2)**2)
OUTWARD = (math.sqrt(3)/2, -.5)
# The centroid of the equilateral large-tube group starts at (0,0).
RAW_PORTS = {
    'flavor-a': (-PITCH/2, TRIANGLE_H/3, 6.35, 4.32),
    'flavor-b': (PITCH/2, TRIANGLE_H/3, 6.35, 4.32),
    'soda': (0., -2*TRIANGLE_H/3, 6.35, 4.32),
    'drain': (PITCH/4 + OUTWARD_REACH*OUTWARD[0],
              -TRIANGLE_H/6 + OUTWARD_REACH*OUTWARD[1], 4., 2.5),
}
# Center the enclosing circle on the far large lobe and the small lobe.
# The other two lobes lie inside it. This keeps the guard centered on the bundle.
LARGE_RADIUS = PITCH/math.sqrt(3)
SMALL_RADIUS = LARGE_RADIUS/2 + OUTWARD_REACH
CENTER_SHIFT = (SMALL_RADIUS + 2 + b.GAP - LARGE_RADIUS - 3.175 - b.GAP)/2
SHIFT = tuple(CENTER_SHIFT*v for v in OUTWARD)
PORTS = {name: (x-SHIFT[0], z-SHIFT[1], od, tube_id)
         for name, (x, z, od, tube_id) in RAW_PORTS.items()}
PAIRS = list(itertools.combinations(['flavor-a', 'flavor-b', 'soda'], 2))
PAIRS += [('flavor-b', 'drain'), ('soda', 'drain')]


def main():
    rows = b.scene(PORTS)
    assembly = b.u.cq.Assembly(name='triangle-bundle')
    for name, shape, color, _ in rows:
        if not shape.isValid() or len(shape.Solids()) != 1:
            raise ValueError(f'Invalid or disconnected body: {name}')
        assembly.add(shape, name=name, color=color)
    gaps = {}
    for a, c in PAIRS:
        ax, az, ad, _ = PORTS[a]
        cx, cz, cd, _ = PORTS[c]
        gap = math.hypot(ax-cx, az-cz) - (ad+cd)/2
        if abs(gap-b.GAP) > 1e-8:
            raise ValueError(f'Unequal neighboring gap: {a}/{c}')
        gaps[a+'/'+c] = round(gap, 6)
    envelope = LARGE_RADIUS + CENTER_SHIFT + 3.175 + b.GAP
    for x, z, od, _ in PORTS.values():
        if math.hypot(x, z) + od/2 + b.GAP > envelope + 1e-8:
            raise ValueError('TPU outline exceeds centered envelope')
    guard = next(shape for name, shape, _, _ in rows if name == 'blue-plug-guard')
    if any(guard.intersect(shape).Volume() > 1e-7
           for name, shape, _, role in rows if role == 'bundle' and name != 'blue-plug-guard'):
        raise ValueError('Core intersects protective wall')
    (HERE / 'out').mkdir(exist_ok=True)
    b.export_assembly(assembly, str(HERE / 'out/triangle-bundle.step'))
    profile = next(shape for name, shape, _, _ in rows if name == 'tpu-profile')
    bb = profile.BoundingBox()
    record = {
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'shared_source_sha256': hashlib.sha256(Path(b.__file__).read_bytes()).hexdigest(),
        'scope': 'Triangular large-tube packing, smaller tube added against two; separate size references',
        'units': 'mm', 'tube_axis': 'Y',
        'roles': {name: role for name, _, _, role in rows},
        'tube_centers_xz_and_od': {name: [round(v, 6) for v in values[:3]] for name, values in PORTS.items()},
        'neighboring_tube_gaps': gaps, 'exposed_tpu_skin': b.GAP,
        'tpu_bounds_xz': [round(bb.xlen, 6), round(bb.zlen, 6)],
        'tpu_enclosing_circle_diameter': round(2*envelope, 6),
        'tpu_length': 12, 'tube_and_tpu_tip_recess': 2,
        'guard_od': 34, 'guard_id': 22, 'guard_wall': 6, 'guard_length': 16,
        'counter_hole_diameter': 34.93, 'reference_counter_patch_thickness': 2,
        'bodies': len(rows), 'all_bodies_valid_and_single_solid': True,
        'core_guard_overlap_mm3': 0,
    }
    (HERE / 'geometry.json').write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
