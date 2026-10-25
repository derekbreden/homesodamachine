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
from _cadq_export import import_step

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


def printed_pilot_floors(path, datums, names=None):
    """Read the printed flutes, which are absent from the smooth native STEP."""
    import numpy as np
    import trimesh
    mesh = trimesh.load(path,process=False)
    triangles = mesh.triangles
    low,high = triangles.min(axis=1),triangles.max(axis=1)
    offsets = [(u,v) for u in np.linspace(-1.99,1.99,17)
                       for v in np.linspace(-1.99,1.99,17) if u*u+v*v<=1.99**2]
    rows = []
    for name,plan in datums.items():
        if names is not None and name not in names:
            continue
        for station in plan['stations']:
            if not station['threaded']:
                continue
            _,y,z = station['position_world_mm']
            end = station['insert_face_world_mm'][0]-plan['pilot_depth_mm']
            window = ((low[:,1]<=y+2.) & (high[:,1]>=y-2.)
                      & (low[:,2]<=z+2.) & (high[:,2]>=z-2.))
            plane_count = int(np.count_nonzero(window & np.all(
                np.abs(triangles[:,:,0]-end)<1.e-4,axis=1)))
            local_triangles = triangles[window & (low[:,0]<end-.01)]
            local = trimesh.Trimesh(vertices=local_triangles.reshape(-1,3),
                faces=np.arange(len(local_triangles)*3).reshape(-1,3),process=False)
            origins = np.array([[end-.001,y+u,z+v] for u,v in offsets])
            hits,_,_ = local.ray.intersects_location(origins,
                np.tile([-1.,0.,0.],(len(origins),1)),multiple_hits=False)
            minimum = float(min(end-point[0] for point in hits)) if len(hits) else None
            rows.append({'equipment':name,'native_hole_index':station['native_hole_index'],
                'pilot_floor_world_x_mm':end,'matching_printed_floor_facets':plane_count,
                'sampled_axes':len(offsets),'ray_hits':len(hits),
                'minimum_sampled_printed_backing_mm':minimum,
                'conservative_backing_after_full_flute_depth_mm':plan['minimum_fluted_backing_mm'],
                'maximum_source_flute_depth_mm':plan['maximum_flute_depth_mm'],
                'passed':plane_count>0 and len(hits)==len(offsets)
                    and minimum is not None and minimum>=3.-1.e-4
                    and plan['minimum_fluted_backing_mm']>=3.-1.e-9})
    return {'path':str(path.relative_to(ROOT)),'sha256':sha(path),
        'scope':'197 finite axes per pilot, directly through printed STL triangles, '
                'plus the source bound on the full 1.2 mm flute depth. '
                'The smooth native STEP alone does not establish printed backing.',
        'rows':rows,'passed':all(row['passed'] for row in rows)}


def bind_printed_floor_delta(path, output):
    """Only the four changed relay pilots; retain the existing contact fixture."""
    report = json.loads(output.read_text())
    datums = shell.wall_mount_datums()
    printed = printed_pilot_floors(path,datums,('relay-1','relay-2'))
    original = report.get('contact_fixture_plans',report.get('plans'))
    outer_keys = ('boss_radius_mm','bearing_tip_radius_mm','bearing_tip_height_mm',
                  'screw_clearance_radius_mm','active_hole_indices')
    preserved = {}
    for name in NAMES:
        first,last = original[name],datums[name]
        preserved[name] = (all(first.get(k)==json.loads(json.dumps(last.get(k)))
                              for k in outer_keys)
            and first['stations']==json.loads(json.dumps(last['stations']))
            and report['native_poses'][name]==layout.pose(name))
    if 'plans' in report:
        report['contact_fixture_plans'] = report.pop('plans')
    if 'finite_fastener_stacks' in report:
        report['contact_fixture_finite_fastener_stacks'] = report.pop('finite_fastener_stacks')
    if 'retained_native_back_top_fixture' not in report:
        report['retained_native_back_top_fixture'] = report.pop('actual_back_top_binding')
    report['selected_fastener_plans'] = datums
    report['selected_finite_fastener_stacks'] = [
        {'equipment':name,'native_hole_index':station['native_hole_index'],
         'screw':plan['screw'],'insert':plan['insert'],
         'receiving_range_mm':plan['receiving_range_mm'],
         'insert_length_mm':plan['insert_length_mm'],
         'pilot_depth_mm':plan['pilot_depth_mm'],
         'minimum_tip_air_mm':plan['minimum_tip_air_mm'],
         'native_smooth_blind_backing_mm':plan['minimum_blind_backing_mm'],
         'minimum_fluted_backing_mm':plan['minimum_fluted_backing_mm']}
        for name,plan in datums.items() for station in plan['stations'] if station['threaded']]
    step = path.with_suffix('.step')
    report['actual_back_top_binding'] = {
        'path':str(step.relative_to(ROOT)), 'sha256':sha(step),
        'printed_pilot_floor_reading':printed,
        'unchanged_device_pad_head_stations':preserved,
        'scope':'Only four changed relay pilot floors read against the physical '
                'printed STL. The devices, pad outer profiles, bearing tips, '
                'head envelopes and stations retain the prior native/electrical '
                'fixture scope. No unchanged contact pair or core check is replayed. '
                'The independent fore-meter neck belongs to wall-meter-review.json.',
        'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in (
            Path(__file__),Path(shell.__file__),ROOT/'hardware/manifold-layout/above-core.json')},
        'reproduce':'HSM_NO_BUILD_LOCK=1 tmp/takeover/cadq "relay printed pilot floors" -- '
            'tools/cad-venv/bin/python hardware/mechanical-qualification/enclosure-above-core/'
            'wall_mounts.py --bind-printed-floors '+str(path.relative_to(ROOT)),
        'passed':printed['passed'] and all(preserved.values())}
    output.write_text(json.dumps(report,indent=2)+'\n')
    print('Printed relay floor delta',report['actual_back_top_binding']['passed'],
          printed,flush=True)


def bind_back_top(path, output):
    """Append a local imported-shell reading without repeating electrical pairs."""
    report = json.loads(output.read_text())
    stock = import_step(path).val()
    equipment = {name:layout.place(parts.native_reference(name),name) for name in NAMES}
    subjects = dict(equipment)
    for prefix,(pads,cutters) in (('psu',shell.psu_bosses()),
                                   ('relays',shell.relay_bosses())):
        subjects.update({prefix+'-host-'+str(i):pad.cut(*cutters).clean()
                         for i,pad in enumerate(pads)})
    metrics = {}
    for name,body in subjects.items():
        first,last = report['component_signatures'][name],signature(body)
        deviation = max(abs(x-y) for x,y in zip(first['bounds_mm'],last['bounds_mm']))
        dv = abs(first['volume_mm3']-last['volume_mm3'])
        metrics[name] = {'bounds_max_deviation_mm':deviation,'volume_deviation_mm3':dv,
            'same_face_count':first['faces']==last['faces'],
            'same_solid_count':first['solids']==last['solids'],
            'matched':deviation<=1.e-5 and dv<=max(.001,first['volume_mm3']*1.e-7)
                and first['faces']==last['faces'] and first['solids']==last['solids']}
    rows = []
    datums = shell.wall_mount_datums()
    for name,plan in datums.items():
        for station in plan['stations']:
            if not station['threaded']:
                continue
            _,y,z = station['position_world_mm']
            face = station['insert_face_world_mm'][0]
            wall = xcylinder(5.,face-plan['insert_length_mm'],face,y,z).cut(
                xcylinder(2.,face-plan['insert_length_mm'],face,y,z))
            floor = xcylinder(2.,face-plan['pilot_depth_mm']-3.,
                               face-plan['pilot_depth_mm'],y,z)
            rows.append({'equipment':name,'native_hole_index':station['native_hole_index'],
                'complete3mm_insert_wall_missing_mm3':volume(wall.cut(stock)),
                'complete3mm_blind_floor_missing_mm3':volume(floor.cut(stock))})
    contacts = {name:reading(body,stock) for name,body in equipment.items()}
    # The ordinary roof is source Z346. Restrict this distance to the ceiling
    # band, leaving the intended board-bearing contacts out of the measurement.
    b = equipment['relay-2'].BoundingBox()
    ceiling = stock.intersect(cq.Solid.makeBox(b.xlen+2.,b.ylen+2.,9.01,
        cq.Vector(b.xmin-1.,b.ymin-1.,346.)))
    host_missing = {name:volume(body.cut(stock))
                    for name,body in subjects.items() if name not in equipment}
    printed = printed_pilot_floors(path.with_suffix('.stl'),datums)
    # Contact subjects have identical outer geometry; the pilot-depth change
    # lies inside the enclosure wall. Preserve the recorded contact cache and
    # identify the selected finite stack separately from that fixture.
    stacks = []
    for row in rows:
        plan = datums[row['equipment']]
        receiving = plan['receiving_range_mm']
        stacks.append({**row,'screw':plan['screw'],'insert':plan['insert'],
            'receiving_range_mm':receiving,'insert_length_mm':plan['insert_length_mm'],
            'minimum_tip_air_mm':plan['pilot_depth_mm']-max(receiving),
            'native_smooth_blind_backing_mm':plan['minimum_blind_backing_mm'],
            'minimum_fluted_backing_mm':plan['minimum_fluted_backing_mm']})
    report['selected_fastener_plans'] = datums
    report['selected_finite_fastener_stacks'] = stacks
    report['actual_back_top_binding'] = {
        'path':str(path.relative_to(ROOT)), 'sha256':sha(path),
        'stock':signature(stock), 'component_geometry_comparison':metrics,
        'local_host_material_missing_mm3':host_missing,
        'equipment_contacts':contacts, 'finite_insert_stock':rows,
        'printed_pilot_floor_reading':printed,
        'relay2_top_world_z_mm':b.zmax,'plain_roof_inner_world_z_mm':346.,
        'relay2_to_actual_ceiling_band_gap_mm':equipment['relay-2'].distance(ceiling),
        'comparison_tolerances':{'coordinate_mm':1.e-5,'volume_mm3':.001,
                                'volume_relative':1.e-7,'faces_solids':'exact'},
        'reproduce':'HSM_NO_BUILD_LOCK=1 tmp/takeover/cadq "bind actual dry-wall hosts" -- '
            'tools/cad-venv/bin/python hardware/mechanical-qualification/enclosure-above-core/'
            'wall_mounts.py --bind-back-top '+str(path.relative_to(ROOT)),
        'binding_source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in (
            Path(__file__),Path(shell.__file__),ROOT/'hardware/manifold-layout/above-core.json')},
        'scope':'Imported back-top only versus the three unchanged equipment bodies and eight finite insert-wall/floor witnesses. Electrical results above retain their original source/cache binding; those pairs were not replayed.',
        'passed':stock.isValid() and len(stock.Solids())==1
            and all(r['matched'] for r in metrics.values())
            and all(value<=.001 for value in host_missing.values())
            and printed['passed']
            and all(r is None or r['common_mm3']<=TOL_MM3 for r in contacts.values())
            and all(max(r['complete3mm_insert_wall_missing_mm3'],
                        r['complete3mm_blind_floor_missing_mm3'])<=.001 for r in rows)}
    output.write_text(json.dumps(report,indent=2)+'\n')
    print('Actual back-top binding',report['actual_back_top_binding']['passed'],flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wiring-index', type=Path,
                        help='Explicit source-bound 111-body unchanged electrical cache')
    parser.add_argument('--bind-back-top', type=Path,
                        help='Append the imported final-shell reading to the existing receipt only')
    parser.add_argument('--bind-printed-floors', type=Path,
                        help='Bind only four changed relay floors to the physical STL')
    parser.add_argument('--output', type=Path, default=HERE/'wall-mount-review.json')
    args = parser.parse_args()
    if args.bind_printed_floors:
        return bind_printed_floor_delta(args.bind_printed_floors.resolve(),args.output)
    if args.bind_back_top:
        return bind_back_top(args.bind_back_top.resolve(),args.output)
    if not args.wiring_index:
        parser.error('--wiring-index is required for the source/cache review')
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
