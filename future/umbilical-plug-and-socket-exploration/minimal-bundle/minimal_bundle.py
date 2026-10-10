"""Minimal tube/TPU packing study, with separate hardware size references.

Coordinates are millimetres. The tube axis is Y; the front view looks along +Y.
The TPU depicts the inserted profile, without selecting seal interference.
"""
import hashlib
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import umbilical as u
import _materials as m
sys.path.insert(0, str(u.ROOT / 'hardware/printed-parts/enclosure/y-wall-of-back-top'))
import _y_wall_dimensions as yw
from _cadq_export import export_assembly

GAP = .85
HALF_PITCH = (6.35 + GAP) / 2
DRAIN_CENTER = math.sqrt(((3.175 + 2 + GAP)**2 - 2*HALF_PITCH**2) / 2)
PORTS = {
    'flavor-a': (-HALF_PITCH, HALF_PITCH, 6.35, 4.32),
    'flavor-b': (HALF_PITCH, HALF_PITCH, 6.35, 4.32),
    'soda': (-HALF_PITCH, -HALF_PITCH, 6.35, 4.32),
    'drain': (DRAIN_CENTER, -DRAIN_CENTER, 4., 2.5),
}
PAIRS = [('flavor-a', 'flavor-b'), ('flavor-a', 'soda'),
         ('flavor-b', 'drain'), ('soda', 'drain')]
BLUE = u.cq.Color(*(v/255 for v in yw.chip_color('carb')))
TPU = u.cq.Color(.35, .65, .5)
COUNTER = u.cq.Color(.72, .72, .72)


def tpu_profile(ports=PORTS):
    """Offset each tube by GAP, fill the enclosed interstice, then remove bores."""
    disks = [u.cyl(od + 2*GAP, 2, 14, x, z)
             for x, z, od, _ in ports.values()]
    merged = disks[0].fuse(*disks[1:]).clean()
    front = next(face for face in merged.Faces()
                 if abs(face.Center().y - 2) < 1e-7 and
                 abs(face.normalAt().y) > .999)
    shape = u.cq.Solid.extrudeLinear(front.outerWire(), [], u._v(0, 12, 0))
    for x, z, od, _ in ports.values():
        shape = shape.cut(u.cyl(od, 1.9, 14.1, x, z))
    return shape.clean()


def magnet(x, z):
    """Selected SB443-IN envelope and two side grooves; no mounting proposal."""
    shape = u.box(x-u.BAR/2, x+u.BAR/2, 0, u.BAR_T, z-u.BAR/2, z+u.BAR/2)
    for sign in [-1, 1]:
        edge = x + sign*u.BAR/2
        lo, hi = sorted([edge, edge-sign*u.GROOVE_D])
        shape = shape.cut(u.box(lo, hi, u.GROOVE_TOP,
                               u.GROOVE_TOP+u.GROOVE_H, z-3.3, z+3.3))
    return shape.clean()


def scene(ports=PORTS):
    rows = []
    def add(name, shape, color, role):
        rows.append((name, shape, color, role))
    for name, (x, z, od, tube_id) in ports.items():
        tube = u.cyl(od, 2, 14, x, z).cut(u.cyl(tube_id, 1.9, 14.1, x, z))
        color_key = 'carb' if name == 'soda' else 'drain' if name == 'drain' else 'flavor'
        color = u.cq.Color(*(v/255 for v in yw.port_colors[color_key]))
        add(name, tube.clean(), color, 'bundle')
    add('tpu-profile', tpu_profile(ports), TPU, 'bundle')
    add('blue-plug-guard', u.cyl(34, 0, 16).cut(u.cyl(22, -.1, 16.1)), BLUE, 'bundle')
    counter = u.box(24, 70, 0, 2, -23, 23).cut(u.cyl(34.93, -.1, 2.1, 47, 0))
    add('counter-hole-reference', counter.clean(), COUNTER, 'reference')
    for name, shape, z in [('pogo-female', u.P.build_female().val(), -30),
                           ('pogo-male', u.P.build_male().val(), -38)]:
        add(name, shape.rotate((0, 0, 0), (1, 0, 0), 90).translate((0, 0, z)),
            m.M_PETGF_BLACK, 'reference')
    add('sb443-in-left', magnet(-18, -34), m.M_NICKEL_PLATE, 'reference')
    add('sb443-in-right', magnet(18, -34), m.M_NICKEL_PLATE, 'reference')
    return rows


def main():
    rows = scene()
    assembly = u.cq.Assembly(name='minimal-bundle')
    for name, shape, color, _ in rows:
        if not shape.isValid() or len(shape.Solids()) != 1:
            raise ValueError(f'Invalid or disconnected body: {name}')
        assembly.add(shape, name=name, color=color)
    gaps = {}
    for a, b in PAIRS:
        ax, az, ad, _ = PORTS[a]
        bx, bz, bd, _ = PORTS[b]
        gap = math.hypot(ax-bx, az-bz) - (ad+bd)/2
        if abs(gap-GAP) > 1e-8:
            raise ValueError(f'Unequal neighboring gap: {a}/{b}')
        gaps[a+'/'+b] = round(gap, 6)
    guard = next(shape for name, shape, _, _ in rows if name == 'blue-plug-guard')
    core = [shape for _, shape, _, role in rows if role == 'bundle' and shape is not guard]
    if any(guard.intersect(shape).Volume() > 1e-7 for shape in core):
        raise ValueError('Core intersects protective wall')
    (HERE / 'out').mkdir(exist_ok=True)
    export_assembly(assembly, str(HERE / 'out/minimal-bundle.step'))
    profile = next(shape for name, shape, _, _ in rows if name == 'tpu-profile')
    bb = profile.BoundingBox()
    record = {
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'scope': 'Inserted tube/TPU packing, thick guard, separate same-scale references',
        'units': 'mm', 'tube_axis': 'Y',
        'roles': {name: role for name, _, _, role in rows},
        'tube_centers_xz_and_od': {name: list(values[:3]) for name, values in PORTS.items()},
        'neighboring_tube_gaps': gaps, 'exposed_tpu_skin': GAP,
        'drain_center_inward_shift_per_axis': round(HALF_PITCH-DRAIN_CENTER, 6),
        'tpu_bounds_xz': [round(bb.xlen, 6), round(bb.zlen, 6)],
        'tpu_length': 12, 'tube_and_tpu_tip_recess': 2,
        'guard_od': 34, 'guard_id': 22, 'guard_wall': 6,
        'guard_length': 16, 'counter_hole_diameter': 34.93,
        'reference_counter_patch_thickness': 2,
        'pogo_reference': 'YYFKGCP screw-ear pair; unattached, male pins extended',
        'magnet_reference': 'Two K&J SB443-IN; 6.35 x 6.35 x 4.7625, side grooves',
        'bodies': len(rows), 'all_bodies_valid_and_single_solid': True,
        'core_guard_overlap_mm3': 0,
    }
    (HERE / 'geometry.json').write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
