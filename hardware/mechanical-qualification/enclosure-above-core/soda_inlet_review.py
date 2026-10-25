"""Manual native reading of the selected continuous insulated soda inlet.

Run through tmp/takeover/cadq after the appliance, cap and cold-core exports. The default
reads production builders and native artifacts. Optional saved fixtures avoid
rebuilding the same four inlet shapes during a coordinated manual review.
This script is not a generator, build hook, or physical qualification.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(ROOT/'hardware/scripts'), str(ROOT/'hardware/manifold-layout'),
               str(ROOT/'hardware/cold-core-layout'),
               str(ROOT/'hardware/printed-parts/cold-core'),
               str(ROOT/'hardware/printed-parts/cold-core/foam-assembly')]
import cadquery as cq
from _cadq_export import import_assembly, import_step
import above_core as layout
import above_core_parts as parts
import above_core_routes as routes
import soda_inlet
import _above_core_mounts as mounts
import _cold_core_interface as core
import _internal_routes as internal
import _internals as internals
import cold_core_assembly as assembly
import foam_assembly as foam

CHANGED_LEADS = ('wire-J1-OUT1', 'wire-J1-positive-A', 'wire-J2-OUT3',
                 'wire-J2-positive-K', 'wire-J5-V5', 'wire-J5-IO19')
CONTACT_TOL_MM3 = 1.e-6


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
            'center_mm': list(shape.Center().toTuple()), 'bounds_mm': bounds(shape)}


def nearby(a, b, margin=0.):
    return all(a[i] <= b[i+3]+margin and b[i] <= a[i+3]+margin for i in range(3))


def shell_world_point(point):
    return layout.point(layout.cap_lid_pose(),
        (-point[0], -point[1], point[2]-core.foam_shell_outer_height-foam.top_cap_height))


def shell_world_shape(shape):
    return (shape.translate((0., 0., -core.foam_shell_outer_height-foam.top_cap_height))
            .rotate((0., 0., 0.), (0., 0., 1.), 180.)
            .moved(layout.frame_location(layout.cap_lid_pose())))


def flat_names(imported):
    result = {}
    for name, (shape, _color) in imported.items():
        tail = name.rsplit('/', 1)[-1]
        if tail in result:
            raise ValueError('Duplicate physical component tail: '+tail)
        result[tail] = shape
    return result


def access_witnesses(placed):
    """The existing 30 nominal witnesses, from production and public records."""
    import above_core_wiring as wiring
    from connector_service import recorded_witnesses
    installation = parts._module('inlet_review_pump_installation',
        'reference/g-ganen-pump/installation/g_ganen_installation.py')
    pcb = parts._module('inlet_review_pcba',
        'printed-parts/electronics/pcba-tray/pcba_tray.py')
    psu = parts._module('inlet_review_psu',
        'reference/meanwell-irm90/meanwell_irm90.py')
    result = {}
    for name, holes, z in (
        ('g-ganen-pump', installation.mount_holes(),
         installation.observed_pad_upper_z()+installation.WASHER_T+3.),
        ('pcba', pcb.board.holes, pcb._thickness+3.),
        ('psu', psu.holes, psu.ledge_h+3.)):
        for index, (x, y) in enumerate(holes):
            point = layout.point(layout.pose(name), (x, y, z))
            result[f'{name}-mount-{index}'] = cq.Solid.makeCylinder(
                2.5/math.sqrt(3.)+.15, 355.-point[2], cq.Vector(*point))
    result.update(wiring.driver_columns())
    review = json.loads((ROOT/'hardware/wiring/installed/above-core-review/native-review.json').read_text())
    connector = json.loads((ROOT/'hardware/wiring/installed/connector-map.json').read_text())['connectors']['J10']
    for pin in connector['pins']:
        x, y = pin['xy_mm']
        point = layout.point(layout.pose('pcba'),
            (x-pcb._centre[0], y-pcb._centre[1],
             pcb._thickness+connector['component_glb_bounds_mm'][5]))
        result['J10-'+pin['label']] = cq.Solid.makeCylinder(
            1.65, 355.-point[2], cq.Vector(*point))
        mouth = review['terminals']['J10.'+pin['label']]['point']
        result['J10-mouth-'+pin['label']] = cq.Solid.makeCylinder(
            1.5, 8., cq.Vector(*mouth), cq.Vector(0., 1., 0.))
    services = recorded_witnesses()
    for name, shape in placed.items():
        if name.startswith('terminal-J'):
            if name in services:
                result[name+'-service'] = services[name][1]
            else:
                b = shape.BoundingBox()
                result[name+'-withdrawal'] = cq.Solid.makeBox(
                    b.xlen, b.ylen, 355.-b.zmax, cq.Vector(b.xmin, b.ymin, b.zmax))
    return result


def contacts(subjects, obstacles, finite=None):
    """Native Booleans only for overlapping conservative component bounds."""
    boxes = {name: bounds(shape) for name, shape in obstacles.items()}
    rows = []
    for name, shape in subjects.items():
        box = bounds(shape)
        for other, body in obstacles.items():
            if not nearby(box, boxes[other]):
                continue
            common = shape.intersect(body)
            raw = volume(common)
            mate = (finite or {}).get((name, other))
            outside = volume(common.cut(mate)) if mate is not None and raw else raw
            rows.append({'subject': name, 'obstacle': other, 'common_mm3': raw,
                         'outside_finite_mate_mm3': outside,
                         'distance_mm': shape.distance(body),
                         'common_bounds_mm': bounds(common) if raw > CONTACT_TOL_MM3 else None})
    return rows


def missing_stock(stock, air, actual):
    return volume(stock.cut(air).cut(actual))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=HERE/'soda-inlet-review.json')
    parser.add_argument('--fixture', type=Path,
                        help='Directory containing the four source-current inlet BREPs and index.json')
    parser.add_argument('--wiring-cache', type=Path,
                        help='Optional coordinated 119-body cache; six peer-reviewed changed leads are omitted')
    parser.add_argument('--tool-cache', type=Path,
                        help='Optional saved native versions of the existing 30 access witnesses')
    args = parser.parse_args()
    start = time.monotonic()
    plan = soda_inlet.plan()
    warm = {name: row[0] for name, row in parts.components().items()}
    if args.fixture:
        fixture = json.loads((args.fixture/'index.json').read_text())
        if fixture['plan'] != plan:
            raise ValueError('Saved fixture plan differs from current production plan')
        shapes = {name: cq.Shape.importBrep(str(args.fixture/row['brep']))
                  for name, row in fixture['parts'].items()}
    else:
        shapes = {'tube-soda-core-rise': soda_inlet.tube(),
                  'soda-bend-holder': soda_inlet.holder(),
                  'soda-foam-stock': soda_inlet.foam_stock(),
                  'soda-continuous-insulation': soda_inlet.foam_occupied(warm)}
    signatures = {name: signature(shape) for name, shape in shapes.items()
                  if name != 'soda-foam-stock'}
    print('Reading actual appliance and current exported core', flush=True)
    ea_path = ROOT/'hardware/manifold-layout/enclosure-assembly.step'
    cca_path = ROOT/'hardware/cold-core-layout/cold-core-assembly.step'
    placed = flat_names(import_assembly(ea_path))
    core_bodies = {name: shell_world_shape(shape)
                   for name, shape in flat_names(import_assembly(cca_path)).items()}
    source_signatures = signatures
    signatures = {name: signature(placed[name]) for name in source_signatures}
    placed.update(core_bodies)
    placed.update(warm)
    for name in (*soda_inlet.RETIRED, *shapes):
        placed.pop(name, None)
    if args.wiring_cache:
        cached_wires = json.loads((args.wiring_cache/'index.json').read_text())['parts']
        wires = {name: cq.Shape.importBrep(str(args.wiring_cache/file))
                 for name, file in cached_wires.items() if name not in CHANGED_LEADS}
    else:
        cached_wires = {}
        wires = {name: shape for name, shape in placed.items()
                 if name.startswith(('wire-', 'terminal-'))}
    if args.tool_cache:
        tools_index = json.loads((args.tool_cache/'index.json').read_text())['parts']
        tools = {name: cq.Shape.importBrep(str(args.tool_cache/file))
                 for name, file in tools_index.items()}
    else:
        tools_index = {}
        tools = access_witnesses(placed)
    placed = {name: shape for name, shape in placed.items()
              if not name.startswith(('wire-', 'terminal-'))}
    print('Querying new rigid inlet and nominal full foam', flush=True)
    rigid = {name: shapes[name] for name in ('tube-soda-core-rise', 'soda-bend-holder')}
    mouth = plan['meter_mouth_mm']
    finite_meter = cq.Solid.makeCylinder(plan['tube_od_mm']/2.,
        plan['meter_insertion_mm'], cq.Vector(*mouth), cq.Vector(*plan['flow_axis']))
    rigid_rows = contacts(rigid, placed,
        {('tube-soda-core-rise', 'digiten-flow'): finite_meter})
    rigid_wire_rows = contacts(rigid, wires)
    rigid_tool_rows = contacts(rigid, tools)
    nominal_rows = contacts({'soda-foam-stock': shapes['soda-foam-stock']}, placed)
    nominal_wire_rows = contacts({'soda-foam-stock': shapes['soda-foam-stock']}, wires)
    nominal_tool_rows = contacts({'soda-foam-stock': shapes['soda-foam-stock']}, tools)
    own_rows = contacts({'tube-soda-core-rise': shapes['tube-soda-core-rise']},
                        {'soda-bend-holder': shapes['soda-bend-holder']})
    own_foam = contacts({'soda-foam-stock': shapes['soda-foam-stock']},
                       {'soda-bend-holder': shapes['soda-bend-holder']})
    print('Querying the explicitly named cap-shoulder diagnostic', flush=True)
    shoulder = cq.Solid.makeBox(7.7, 6., 12.7, cq.Vector(50., 364.7148, 267.3))
    shoulder_obstacles = {name: shape for name, shape in placed.items()
                         if name not in ('foam-cap-lid-top', 'cap-lid-top')}
    shoulder_rows = contacts({'meter-fore-shoulder-restored': shoulder},
        {**shoulder_obstacles, **shapes, **wires, **tools})
    print('Reading current native internal tube and cup/lid passage', flush=True)
    internal_points = [shell_world_point(point)
                       for point in assembly.trimmed_routes()['carb-water-out']]
    wire = internal.route_wire(internal_points, 14.)
    radius_values = [radius for radius in internal.corner_radii(internal_points, 14.)[1]
                     if radius > 0.]
    exported_tube = core_bodies['line-carb-water-out']
    features = mounts.soda_out_features()
    cap_dir = ROOT/'hardware/printed-parts/cold-core/foam-cap'
    cup = (import_step(cap_dir/'foam-cap-top.step').val()
           .translate((0., 0., -foam.top_cap_height))
           .moved(layout.frame_location(layout.cap_lid_pose())))
    lid = (import_step(cap_dir/'foam-cap-lid-top.step').val()
           .moved(layout.frame_location(layout.cap_lid_pose())))
    air = features['cut']
    floor_z = (layout.cap_lid_pose()['translation_mm'][2]-foam.top_cap_height
               +core.cap_shell_clearance)
    passage = mounts.soda_out_guide_points()
    d = [passage[2][i]-passage[1][i] for i in range(3)]
    d = [x/math.sqrt(sum(v*v for v in d)) for x in d]
    # The complete ordinary floor underneath the straight traverse; curved
    # entry/exit openings are measured separately by the named air corridor.
    a = [passage[1][i]+14.*d[i] for i in range(3)]
    b = [passage[2][i]-14.*d[i] for i in range(3)]
    a[2] = b[2] = floor_z+core.wall_and_floor_thickness/2.
    floor_path = cq.Wire.assembleEdges([cq.Edge.makeLine(cq.Vector(*a), cq.Vector(*b))])
    plane = cq.Plane(origin=a, normal=d, xDir=(-d[1], d[0], 0.))
    floor_probe = (cq.Workplane(plane).rect(2.*core.cap_conduit_bore_radius,
                                         core.wall_and_floor_thickness)
                   .sweep(floor_path, isFrenet=False).val())
    passage_rows = contacts({'soda-pressure-passage': air},
        {name: body for name, body in core_bodies.items()
         if name not in ('line-carb-water-out', 'foam-cap-top', 'foam-cap-lid-top',
                         'foam-envelope', 'foam-shell', 'soda-bend-holder',
                         'soda-continuous-insulation', 'tube-soda-core-rise')})
    passage_wire_rows = contacts({'soda-pressure-passage': air}, wires)
    # Same straight-axis native sample as the selected layout: a geometric
    # residual distance, not a compression or thermal calculation.
    samples = []
    for index in range(100):
        z = plan['foam_segments'][0]['points_mm'][0][2] + index/99.*(
            plan['arc_start_mm'][2]-plan['foam_segments'][0]['points_mm'][0][2])
        vertex = cq.Vertex.makeVertex(plan['core_guide_mm'][0], plan['core_guide_mm'][1], z)
        for name in soda_inlet.SOFT_NEIGHBORS:
            samples.append({'neighbor': name, 'z_mm': z,
                            'estimated_thickness_mm': vertex.distance(warm[name])-plan['tube_od_mm']/2.})
    minimum = min(samples, key=lambda row: row['estimated_thickness_mm'])
    unexpected = [row for row in rigid_rows+rigid_wire_rows+own_rows
                  if row['outside_finite_mate_mm3'] > CONTACT_TOL_MM3]
    tool_hits = [row for row in rigid_tool_rows if row['common_mm3'] > CONTACT_TOL_MM3]
    unstaged_tool_hits = [row for row in tool_hits if not (
        row['subject'] == 'tube-soda-core-rise' and row['obstacle'] == 'g-ganen-pump-mount-2')]
    unexpected_foam = [row for row in nominal_rows if row['common_mm3'] > CONTACT_TOL_MM3
                       and row['obstacle'] not in soda_inlet.SOFT_NEIGHBORS]
    unexpected_foam += [row for row in nominal_wire_rows+nominal_tool_rows
                        if row['common_mm3'] > CONTACT_TOL_MM3]
    cap_readings = {
        'cup': {**signature(cup), 'passage_contact_mm3': volume(air.intersect(cup)),
                'missing_named_sleeve_stock_mm3': missing_stock(features['cup_add'], air, cup)},
        'lid': {**signature(lid), 'passage_contact_mm3': volume(air.intersect(lid)),
                'missing_named_sleeve_stock_mm3': missing_stock(features['lid_add'], air, lid)},
        'floor': {'outer_world_z_mm': floor_z,
                  'specification_mm': core.wall_and_floor_thickness,
                  'horizontal_backing_mm': features['horizontal_floor_backing_mm'],
                  'straight_floor_probe_missing_mm3': volume(floor_probe.cut(cup))},
        'new_side_and_roof_stock_mm': features['wall_mm'],
        'new_stock_min_world_z_mm': bounds(features['cup_add'])[2],
        'root_connectivity': 'Named carrier fused into the retained cup floor; current cup and lid are each one valid solid. New stock is clipped at the existing outer floor face.',
    }
    sources = ['hardware/manifold-layout/soda_inlet.py',
               'hardware/manifold-layout/above-core.json',
               'hardware/manifold-layout/above_core_parts.py',
               'hardware/manifold-layout/above_core_routes.py',
               'hardware/printed-parts/cold-core/_above_core_mounts.py',
               'hardware/printed-parts/cold-core/_cold_core_interface.py',
               'hardware/printed-parts/cold-core/_internal_routes.py',
               'hardware/printed-parts/cold-core/_foam_cap.py',
               'hardware/cold-core-layout/cold_core_assembly.py']
    artifacts = [ea_path, cca_path, cap_dir/'foam-cap-top.step',
                 cap_dir/'foam-cap-lid-top.step',
                 ROOT/'hardware/printed-parts/cold-core/foam-assembly/foam-assembly.step',
                 ROOT/'hardware/printed-parts/soda-bend-holder/soda-bend-holder.step']
    report = {
        'schema': 1, 'reviewed_date': '2026-10-24',
        'scope': 'Manual source-current native inlet fixture, actual exported core/cup/lid and recorded appliance context. Rigid contacts and nominal full-stock foam contacts are distinct. No physical fit, insertion force, retained tube roundness, pressure, sealing, thermal or lifetime qualification.',
        'reproduce': 'tools/cad-venv/bin/python hardware/mechanical-qualification/enclosure-above-core/soda_inlet_review.py',
        'state': 'Current exported appliance inlet and separate core passage geometry.',
        'plan': plan, 'component_signatures': signatures,
        'source_fixture_component_signatures': source_signatures,
        'signature_scope': 'Canonical installed appliance bodies before tessellation; exact solid/face counts. The source Boolean proxy signatures are separately retained. Actual EA comparisons use volume max(0.001 mm3, 1e-7 times volume) and coordinate tolerance 1e-5 mm. Full-stock foam contact readings do not use the carved occupied display estimate.',
        'rigid_contacts': rigid_rows, 'rigid_vs_electrical': rigid_wire_rows,
        'rigid_vs_30_access_witnesses': rigid_tool_rows,
        'tube_holder': own_rows, 'nominal_foam_holder': own_foam,
        'nominal_full_foam_contacts': nominal_rows,
        'nominal_full_foam_vs_electrical': nominal_wire_rows,
        'nominal_full_foam_vs_30_access_witnesses': nominal_tool_rows,
        'accepted_soft_neighbors': list(soda_inlet.SOFT_NEIGHBORS),
        'estimated_minimum_straight_thickness': minimum,
        'occupied_foam_scope': 'Boolean display estimate of local compression against holder and the four accepted soft neighbors. It does not establish physical clearance, a cutting pattern or measured strain. One square-cut 63 mm physical foam piece remains uncut; disconnected native proxy regions are not physical piece count.',
        'physical_records': [soda_inlet.HOLDER_ACCEPTANCE, soda_inlet.FOAM_EVIDENCE],
        'internal_pressure_path_world_mm': internal_points,
        'internal_minimum_radius_mm': min(radius_values),
        'internal_passage_context': passage_rows,
        'internal_passage_vs_electrical': passage_wire_rows,
        'assembly_prerequisites': {
            'retained_tool_contacts': tool_hits,
            'pump_mount_2': 'Tighten all four pump screws before threading the continuous tube, holder and foam into place. Remove/disconnect that inlet before using the intersected pump screw driver path during service. The nominal driver contact is retained explicitly; there is no geometric mask or access claim with the inlet installed.',
            'foam': 'Thread the holder and slide the one square-cut foam piece over it before connecting the meter.'},
        'passage': cap_readings,
        'continuous_tube_accounting': {
            'internal_span_mm': wire.Length(),
            'external_span_mm': parts.route_wire(soda_inlet.tube_spec()).Length(),
            'meter_receiving_estimate_mm': plan['meter_insertion_mm'],
            'carbonator_nominal_adapter_standoff_mm': internals.PTC_STANDOFF,
            'carbonator_socket_receiving_depth_mm': None,
            'receiving_basis': 'DIGITEN 15.7 mm is a layout estimate. The internal CAD span starts at the actual metal elbow mouth and includes nominal 18.5 mm PP010822E adapter standoff; its actual receiving depth is unmeasured. Replace nominal allowances with actual receiving marks.',
            'plain_guide_joint': False, 'plain_guide_insertion_mm': 0.,
            'plain_guide_cut': False,
            'exported_internal_outer_envelope_volume_mm3': volume(exported_tube),
            'nominal_R14_outer_envelope_volume_mm3': math.pi*(core.lldpe_tube_od/2.)**2*wire.Length(),
            'model_scope': 'Internal CAD span is a solid outer envelope; the external span is an annular 6.35/4.24 mm tube.'},
        'optional_fore_meter_shoulder_restoration': {
            'stock': signature(shoulder), 'world_box_mm': bounds(shoulder),
            'contacts': shoulder_rows,
            'scope': 'Restoration of the existing flat step to Z267.3 from Z280, preserving the pump-foot step and 4.6 mm east root. Own lid union is omitted; six changed conductors have a separate peer receipt.',
            'clear_in_this_scope': all(row['common_mm3'] <= CONTACT_TOL_MM3 for row in shoulder_rows)},
        'electrical_scope': {'count': len(wires),
            'excluded_peer_reviewed_leads': list(CHANGED_LEADS) if args.wiring_cache else [],
            'body_sha256': {name: sha(args.wiring_cache/file) for name, file in cached_wires.items()
                            if name not in CHANGED_LEADS}},
        'access_witness_scope': {'count': len(tools),
            'body_sha256': {name: sha(args.tool_cache/file) for name, file in tools_index.items()}},
        'unexpected_rigid_contacts': unexpected, 'unexpected_nominal_foam_contacts': unexpected_foam,
        'source_hashes_sha256': {rel: sha(ROOT/rel) for rel in sources},
        'artifact_hashes_sha256': {str(path.relative_to(ROOT)): sha(path) for path in artifacts},
        'seconds': time.monotonic()-start,
    }
    report['passed'] = (not unexpected and not unexpected_foam and not unstaged_tool_hits
        and cap_readings['cup']['valid'] and cap_readings['cup']['solids'] == 1
        and cap_readings['lid']['valid'] and cap_readings['lid']['solids'] == 1
        and all(cap_readings[part][key] <= CONTACT_TOL_MM3
                for part in ('cup', 'lid')
                for key in ('passage_contact_mm3', 'missing_named_sleeve_stock_mm3'))
        and cap_readings['floor']['straight_floor_probe_missing_mm3'] <= CONTACT_TOL_MM3
        and all(row['common_mm3'] <= CONTACT_TOL_MM3
                for row in passage_rows+passage_wire_rows)
        and min(radius_values) >= 14.-1e-6)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({key: report[key] for key in (
        'passed', 'unexpected_rigid_contacts', 'unexpected_nominal_foam_contacts',
        'estimated_minimum_straight_thickness', 'passage', 'continuous_tube_accounting')}, indent=2), flush=True)
    print('SHOULDER_CLEAR', report['optional_fore_meter_shoulder_restoration']['clear_in_this_scope'], flush=True)
    print('->', args.output, flush=True)


if __name__ == '__main__':
    main()
