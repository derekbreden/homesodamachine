"""Manual native review of the guided boot; no build or printer hook invokes it."""
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
import boot_concept as b


def radius(a, c, length):
    """Sample curvature of the exact quintic centerline, including its ends."""
    offset = math.dist(a, c)
    if offset == 0:
        return None
    minimum = math.inf
    for i in range(10001):
        t = i / 10000
        first = 30 * t * t * (1 - t) ** 2
        second = 60 * t * (1 - t) * (1 - 2 * t)
        numerator = (length**2 + offset**2 * first**2)**1.5
        denominator = length * offset * abs(second)
        if denominator:
            minimum = min(minimum, numerator / denominator)
    return minimum


def overlap(a, c):
    return a.intersect(c).Volume()


y0 = b.ENTRY - 60
parts = {'plug': b.plug(), 'key': b.key(), 'foam': b.foam(y0),
         'fabric': b.jacket(y0), 'ribbon': b.ribbon(y0)}
tubes = {name: b.tube(name, y0, hollow=False) for name in b.u.PORTS}
curves = {name: b.guide(name) for name in b.u.PORTS}
foam_corridor = b.foam_fan(b.FOAM_CLEARANCE)
record = {
    'reviewed_local_date': '2026-10-09',
    'scope': 'Native geometry of the guided PET-GF boot. Foam and fabric describe intended compressed envelopes, not deformation predictions. No physical feed force, insulation performance, strain relief, wall strength or retention is established. Saved coupling print projects omit this boot.',
    'source_sha256': {name: hashlib.sha256((HERE/name).read_bytes()).hexdigest()
                      for name in ('umbilical.py', 'boot_concept.py', 'scene.py', 'assessment/review_guided_boot.py')},
    'valid_solids': {name: s.isValid() for name, s in (parts | tubes).items()},
    'solid_count': {name: len(s.Solids()) for name, s in parts.items()},
    'dimensions_mm': {
        'boot_length': b.PLUG_L, 'rigid_max_diameter': 2*b.BODY_R,
        'counter_hole': b.u.COUNTER_HOLE, 'counter_nominal_radial_clearance': b.u.COUNTER_HOLE/2-b.BODY_R,
        'cuff_length': b.CUFF_L, 'tube_transition_length': b.FAN_L, 'straight_nose_length': b.GUIDE_L,
        'key_window_length': b.u.KEY_Y1-b.u.KEY_Y0,
        'port_insertion': b.u.CUP_DEPTH, 'boot_outside_port': b.PLUG_L-b.u.CUP_DEPTH,
        'shoulder_to_socket_mouth_at_face_stop': .3, 'shoulder_chamfer_length': b.SHOULDER_CHAMFER,
        'mouth_wall': b.BODY_R-b.CUFF_R-b.CUFF_LEAD,
        'fabric_tuck': b.CUFF_L, 'assumed_compressed_fabric_wall': b.BRAID_WALL,
        'foam_inside_axial_span': b.FOAM_END-b.ENTRY,
        'foam_wall_at_entry': b.FOAM_REAR_R-6.35/2,
        'foam_wall_at_end_perpendicular_to_path': b.FOAM_END_R-6.35/2,
        'foam_cavity_clearance': b.FOAM_CLEARANCE, 'purchased_nominal_foam_wall': 9.525,
        'quarter_tube_projection': b.STUB_Q, 'provisional_drain_projection': b.STUB_D,
        'nominal_key_bite': b.KEY_BITE,
    },
    'tube_positions_xz_mm': {'packed_entry': b.PACK,
                             'straight_outlet': {name: list(v[:2]) for name,v in b.u.PORTS.items()}},
    'minimum_centerline_bend_radius_mm': {
        'internal': {name: radius(b.PACK[name], b.u.PORTS[name][:2], b.FAN_L) for name in b.u.PORTS},
        'external_illustrative_packing': {name: radius(b.FREE[name], b.PACK[name], b.EXTERNAL_L) for name in b.u.PORTS},
    },
    'manufacturer_bend_limits': {
        'source': 'https://assets.freshwatersystems.com/image/upload/s--N9disqrx--/gjtidjfc0tlprqbhb4ka.pdf',
        'quarter_inch_minimum_mm': 25.4, 'four_mm_minimum_mm': 25.0,
        'scope': 'neoFlo published tube limits. Modeled curves exceed them; actual fed tubing remains unobserved.',
    },
    'native_corridor_gap_mm': {
        'foam_to_other_tube_channels': {name: foam_corridor.distance(s) for name,s in curves.items() if name != 'soda'},
        'tube_channel_pairs': {f'{a}/{c}': curves[a].distance(curves[c]) for a,c in itertools.combinations(curves,2)},
    },
    'material_inside_boot_mm3': {name: s.intersect(b.u.box(-100,100,b.ENTRY,0,-100,100)).Volume()
                                for name,s in parts.items() if name in ('foam','fabric')},
    'intersection_mm3': {
        'foam_with_plug': overlap(parts['foam'],parts['plug']),
        'fabric_with_plug': overlap(parts['fabric'],parts['plug']),
        'foam_with_fabric': overlap(parts['foam'],parts['fabric']),
        'ribbon_with_plug': overlap(parts['ribbon'],parts['plug']),
        'ribbon_with_foam': overlap(parts['ribbon'],parts['foam']),
        'ribbon_with_fabric': overlap(parts['ribbon'],parts['fabric']),
        'key_with_plug': overlap(parts['key'],parts['plug']),
        'tube_with_plug': {name: overlap(s,parts['plug']) for name,s in tubes.items()},
        'tube_with_foam': {name: overlap(s,parts['foam']) for name,s in tubes.items()},
        'tube_with_fabric': {name: overlap(s,parts['fabric']) for name,s in tubes.items()},
        'tube_pairs': {f'{a}/{c}': overlap(tubes[a],tubes[c]) for a,c in itertools.combinations(tubes,2)},
    },
}
(HERE/'boot-packing.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'valid':record['valid_solids'], 'intersections_mm3':record['intersection_mm3'],
                  'bend_radius_mm':record['minimum_centerline_bend_radius_mm'],
                  'corridor_gap_mm':record['native_corridor_gap_mm']},indent=2))
