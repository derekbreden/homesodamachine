"""Manual native reading of the dry west-wall PSU and relay mounts.

The source builders supply the three placed equipment bodies and twelve local
hosts. A supplied, explicitly bound electrical cache supplies only the unchanged
conductors/housings; the fourteen moved PSU/relay conductors have a separate
electrical review. This reads finite nominal fastener stacks and local native
contacts. It does not build an appliance or qualify load, retention or hand reach.
Run through the shared CAD queue; this is not a build hook or gate.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT/'hardware/scripts'), str(ROOT/'hardware/manifold-layout'),
               str(ROOT/'hardware/printed-parts/enclosure/enclosure')]
import cadquery as cq
import above_core as layout
import above_core_parts as parts
import _above_core_shell as shell

NAMES = ('psu', 'relay-1', 'relay-2')
CHANGED = ('AC2-L', 'AC2-N', 'AC3-L', 'AC4-H', 'DC1-V12', 'DC1-GND',
           'DC2-V12', 'DC3-positive', 'J5-V5', 'relay-bus-V5', 'J5-GND',
           'relay-bus-GND', 'J5-IO19', 'J5-IO2')
TOL_MM3 = 1.e-6


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def volume(shape):
    return 0. if shape.isNull() else abs(shape.Volume())


def bounds(shape):
    b = shape.BoundingBox()
    return [b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax]


def signature(shape):
    return {'valid': shape.isValid(), 'solids': len(shape.Solids()),
            'faces': len(shape.Faces()), 'volume_mm3': volume(shape),
            'bounds_mm': bounds(shape), 'center_mm': list(shape.Center().toTuple())}


def nearby(a, b):
    aa, bb = bounds(a), bounds(b)
    return all(aa[i+3] >= bb[i] and bb[i+3] >= aa[i] for i in range(3))


def reading(first, second):
    if not nearby(first, second):
        return None
    common = first.intersect(second, tol=1.e-6)
    value = volume(common)
    return {'common_mm3': value,
            'contact_bounds_mm': bounds(common) if value > TOL_MM3 else None}


def xcylinder(radius, x0, x1, y, z):
    return cq.Solid.makeCylinder(radius, x1-x0, cq.Vector(x0, y, z),
                                 cq.Vector(1., 0., 0.))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wiring-index', required=True, type=Path,
                        help='Explicit source-bound 111-body unchanged electrical cache')
    parser.add_argument('--output', type=Path, default=HERE/'wall-mount-review.json')
    args = parser.parse_args()
    index_path = args.wiring_index.resolve()
    wire_index = json.loads(index_path.read_text())
    if set(wire_index['excluded_conductors']) != set(CHANGED):
        raise ValueError('The electrical cache must exclude exactly the fourteen moved leads')
    wire_files = {name: (Path(file) if Path(file).is_absolute()
                         else index_path.parent/file)
                  for name, file in wire_index['parts'].items()}
    wires = {name: cq.Shape.importBrep(str(file)) for name, file in wire_files.items()}
    print('Loaded unchanged electrical cache:', len(wires), flush=True)

    selected = parts.components()
    context = {name: row[0] for name, row in selected.items()}
    equipment = {name: context[name] for name in NAMES}
    hosts = {}
    for prefix, (pads, cutters) in (('psu', shell.psu_bosses()),
                                   ('relays', shell.relay_bosses())):
        for index, pad in enumerate(pads):
            hosts[prefix+'-host-'+str(index)] = pad.cut(*cutters).clean()
    subjects = {**equipment, **hosts}
    contacts = []
    errors = []
    for name, body in subjects.items():
        for other, obstacle in context.items():
            if name == other:
                continue
            try:
                result = reading(body, obstacle)
                if result is not None:
                    contacts.append({'subject': name, 'obstacle': other, **result})
            except Exception as error:
                errors.append({'subject': name, 'obstacle': other, 'error': str(error)})
    print('Equipment/local-host context candidates:', len(contacts), flush=True)
    electrical = []
    for name, body in subjects.items():
        for other, obstacle in wires.items():
            try:
                result = reading(body, obstacle)
                if result is not None:
                    electrical.append({'subject': name, 'obstacle': other, **result})
            except Exception as error:
                errors.append({'subject': name, 'obstacle': other, 'error': str(error)})
    print('Unchanged electrical candidates:', len(electrical), flush=True)

    stacks = []
    head_contacts = []
    datums = shell.wall_mount_datums()
    for name, plan in datums.items():
        for station in plan['stations']:
            if not station['threaded']:
                continue
            x, y, z = station['position_world_mm']
            face = station['insert_face_world_mm'][0]
            # The dry wall is 9 mm thick here. This local coupon reads the
            # source host/pilot stock; it is not an imported-whole-shell proof.
            coupon = xcylinder(plan['boss_radius_mm'], -107.5, face, y, z)
            pilot = xcylinder(plan['pilot_radius_mm'],
                              face-plan['pilot_depth_mm'], face+.01, y, z)
            coupon = coupon.cut(pilot)
            wall = xcylinder(5., face-plan['insert_length_mm'], face, y, z).cut(
                xcylinder(2., face-plan['insert_length_mm'], face, y, z))
            floor = xcylinder(2., face-plan['pilot_depth_mm']-3.,
                               face-plan['pilot_depth_mm'], y, z)
            receiving = plan['receiving_range_mm']
            head_face = x+(6.7 if name == 'psu' else plan['pcb_thickness_mm'])
            head = xcylinder(2.75, head_face, head_face+3., y, z)
            # Nominal DIN912 M3 head envelope. The relay terminal outline is
            # representative, so any head contact is retained as an explicit
            # reference-fit limit rather than silently removed.
            for other, body in context.items():
                result = reading(head, body)
                if result is not None:
                    head_contacts.append({'fastener':name+'-'+str(station['native_hole_index']),
                                          'obstacle':other, **result})
            stacks.append({'equipment': name, 'native_hole_index': station['native_hole_index'],
                'screw': plan['screw'], 'insert': plan['insert'],
                'receiving_range_mm': receiving,
                'insert_length_mm': plan['insert_length_mm'],
                'minimum_tip_air_mm': plan['pilot_depth_mm']-max(receiving),
                'blind_backing_mm': face-plan['pilot_depth_mm']+107.5,
                'complete3mm_insert_wall_missing_mm3': volume(wall.cut(coupon)),
                'complete3mm_blind_floor_missing_mm3': volume(floor.cut(coupon)),
                'nominal_head_diameter_mm':5.5, 'nominal_head_height_mm':3.,
                'short_bearing_tip_mm':plan.get('bearing_tip_height_mm',0.)})

    sources = [ROOT/'hardware/manifold-layout/above-core.json',
        Path(shell.__file__), Path(parts.__file__),
        ROOT/'hardware/reference/meanwell-irm90/meanwell_irm90.py',
        ROOT/'hardware/reference/teyleten-relay/teyleten_relay.py', Path(__file__)]
    report = {'schema':1, 'reviewed_date':'2026-10-25', 'scope':__doc__.strip(),
        'reproduce':'HSM_NO_BUILD_LOCK=1 tmp/takeover/cadq "manual dry-wall mounts" -- '
                    'tools/cad-venv/bin/python hardware/mechanical-qualification/enclosure-above-core/'
                    'wall_mounts.py --wiring-index '+str(index_path.relative_to(ROOT)),
        'selected_parent':'enclosure-back-top',
        'native_poses':{name:layout.pose(name) for name in NAMES},
        'plans':datums, 'component_signatures':{name:signature(s) for name,s in subjects.items()},
        'context_component_signatures':{name:signature(s) for name,s in context.items()},
        'finite_fastener_stacks':stacks,
        'equipment_and_host_contacts':contacts,
        'nominal_screw_head_contacts':head_contacts,
        'unchanged_electrical_contacts':electrical,
        'errors':errors,
        'passed_local_hosts_and_equipment':not errors and all(
            row['common_mm3']<=TOL_MM3 for row in contacts),
        'passed_unchanged_electrical':not errors and all(
            row['common_mm3']<=TOL_MM3 for row in electrical),
        'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in sources},
        'native_reference_sha256':{str(parts.REFERENCES[name].relative_to(ROOT)):
                                  sha(parts.REFERENCES[name]) for name in NAMES},
        'electrical_binding':{'index_sha256':sha(index_path),
            'manifest_sha256':wire_index['manifest_sha256'],
            'prior_source_binding_sha256':wire_index['prior_source_binding_sha256'],
            'excluded_conductors':list(CHANGED),
            'body_sha256':{name:sha(p) for name,p in wire_files.items()}},
        'limits':[
            'Source-built local hosts and finite wall coupons; final imported enclosure/assembly binding is separate.',
            'Fourteen moved PSU/relay conductors and their terminal approaches are reviewed by the electrical owner. The separate J9-B route update is not established by this unchanged-wire reading.',
            'PSU drawing envelope, mounting pattern and nominal ear height are published; its terminal blocks are representative. Relay pin and terminal envelopes are representative; its clearance-hole diameter is assumed.',
            'The relay bearing tip is a short functional support interface with an unthreaded screw passage. The full 3 mm insert wall starts behind the pin envelope. No physical pin clearance, tool/hand access, printed load capacity, heat-set retention or lifetime result is implied.',
            'Screw-head dimensions are nominal DIN912 envelopes. Actual fastener and purchased-board fit remain unqualified.']}
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print('Local hosts/equipment:',report['passed_local_hosts_and_equipment'],
          'unchanged electrical:',report['passed_unchanged_electrical'],
          'head contacts:',[r for r in head_contacts if r['common_mm3']>TOL_MM3],
          '->',args.output,flush=True)


if __name__ == '__main__':
    main()
