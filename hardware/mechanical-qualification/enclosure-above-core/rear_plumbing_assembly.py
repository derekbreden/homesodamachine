"""Manual finite nominal assembly reading for the nested rear soda connection.

Run through tmp/takeover/cadq after exporting the back-top and cold core.
No enclosure/appliance generation, recurring hook or physical qualification runs.
The default delegates to the approved carried-group and handoff query.
The optional seven-member and late-connection probes are evaluated scenarios;
they do not define the approved carrying pieces or current assembly procedure.
"""
from pathlib import Path
import hashlib
import json
import math
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / 'hardware/scripts'),
                str(ROOT / 'hardware/manifold-layout'),
                str(ROOT / 'hardware/printed-parts/cold-core')]
import cadquery as cq
from _cadq_export import import_assembly, import_step
import above_core as layout
import above_core_parts as parts
import above_core_wiring as electrical
import _cold_core_interface as core

LATE_BODIES = ('bulkhead-carb', 'bulkhead-carb-nut', 'bulkhead-drain',
               'bulkhead-drain-nut', 'soda-stem-elbow',
               'soda-outlet-return-stem')
LATE_TUBES = ('soda-meter-bulkhead', 'drain-vent')
PAIR_OFFSETS = (15.7, 14., 12., 10., 8., 6., 4., 2., 1., 0.)
FEED_OFFSETS = (26., 25., 24., 20., 16., 12.7, 10., 8., 6., 4., 2., 1., .5, .25, 0.)
PARK = (57.375, 463.3, 323.3)
NUT_CLOCK_CHANGE = -30.


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bounds(shape):
    box = shape.BoundingBox()
    return np.array([[box.xmin, box.ymin, box.zmin],
                     [box.xmax, box.ymax, box.zmax]])


def volume(shape):
    return 0. if shape.isNull() else abs(shape.Volume())


def nearby(a, b):
    return np.all(a[1] >= b[0] - 1e-6) and np.all(b[1] >= a[0] - 1e-6)


def contacts(shape, obstacles):
    found = []
    box = bounds(shape)
    for name, other in obstacles.items():
        if not nearby(box, bounds(other)):
            continue
        common = shape.intersect(other)
        v = volume(common)
        if v > 1e-6:
            found.append(dict(body=name, overlap_mm3=v,
                              bounds_world_mm=bounds(common).tolist()))
    return found


def translated_feed(moving, obstacles, offsets, direction=(0., 1., 0.)):
    rows = []
    for offset in offsets:
        row = dict(offset_mm=offset, contacts={})
        for name, shape in moving.items():
            moved = shape.translate(tuple(offset * x for x in direction))
            row['contacts'][name] = contacts(moved, obstacles)
        rows.append(row)
        print(json.dumps(row), flush=True)
    return rows


def core_to_world(shape):
    return (shape.translate((0., 0., -core.foam_shell_outer_height
                              - (core.foam_cap_height-core.head_pad_height)))
            .rotate((0., 0., 0.), (0., 0., 1.), 180.)
            .moved(layout.frame_location(layout.cap_lid_pose())))


def envelope_reading(shape, radius, inboard_length):
    clip = cq.Solid.makeBox(80., inboard_length, 80.,
                            cq.Vector(-40., -inboard_length, -40.))
    envelope = cq.Solid.makeCylinder(radius, inboard_length,
                                    cq.Vector(), cq.Vector(0., -1., 0.))
    section = shape.intersect(clip)
    return dict(valid=shape.isValid(), solids=len(shape.Solids()),
                maximum_inboard_envelope_d_mm=2.*radius,
                outside_envelope_mm3=max(0., volume(section)
                                          - volume(section.intersect(envelope))))


def optional_late_connection_probe():
    started = time.monotonic()
    warm = parts.components()
    junctions = electrical.components()
    meter = parts.components()['digiten-flow'][0]
    pair = {name: warm[name][0] for name in LATE_BODIES[-2:]}
    tube_review = parts._module('rear_assembly_tube_sources',
                               'wiring/installed/above-core-review/tube_review.py')
    specs = tube_review.production_specifications()
    tube = parts.route_shape(specs['soda-meter-bulkhead'])

    shell_path = ROOT / 'hardware/printed-parts/enclosure/enclosure/enclosure-back-top.step'
    shell = import_step(shell_path).val()
    wall_roi = cq.Solid.makeBox(85., 130., 65., cq.Vector(20., 395., 285.))
    wall = shell.intersect(wall_roi)
    static = {name: row[0] for name, row in warm.items()
              if name not in LATE_BODIES}
    static.update({name: row[0] for name, row in junctions.items()})
    static.update({'digiten-flow': meter, 'actual-back-top-rear': wall})
    label_paths = []
    for name in ('carb', 'drain'):
        path = ROOT / f'hardware/printed-parts/enclosure/rear-identification/rear-label-{name}.step'
        label_paths.append(path)
        row = next(row for row in parts._grid() if row['name'] == 'bulkhead-' + name)
        static['actual-' + name + '-label'] = import_step(path).val().translate(
            (row['x'], row['flange_y']-2., row['z']))
    region = np.array([[20., 395., 285.], [100., 500., 350.]])
    for name, spec in specs.items():
        if name in LATE_TUBES:
            continue
        points = np.asarray(spec['points_mm'])
        pad = max(spec['od_mm']/2., float(spec.get('bend_radius_mm') or 0.),
                  float(spec.get('radius_mm') or 0.)) + 1.
        box = np.array([points.min(axis=0)-pad, points.max(axis=0)+pad])
        if nearby(region, box):
            static['tube-' + name] = parts.route_shape(spec)

    # The concealed tube is already fully seated in the rear elbow. Its free
    # 15.7 mm end enters the fixed meter as the complete pair moves fore.
    outlet = specs['soda-meter-bulkhead']['points_mm'][0]
    meter_insertion = cq.Solid.makeCylinder(3.175, 15.7,
                                           cq.Vector(*outlet), cq.Vector(0., 1., 0.))
    pair_targets = dict(static)
    pair_targets['digiten-flow'] = meter.cut(meter_insertion)
    pair_feed = translated_feed({**pair, 'tube-soda-meter-bulkhead': tube},
                                pair_targets, PAIR_OFFSETS)

    nut = warm['bulkhead-carb-nut'][0]
    nut_box = bounds(nut)
    axis = nut_box.mean(axis=0)
    parked = nut.rotate((axis[0], 0., axis[2]), (axis[0], 1., axis[2]),
                        NUT_CLOCK_CHANGE).translate(tuple(np.asarray(PARK)-axis))
    park_static = contacts(parked, static)
    park_feed = []
    for offset in PAIR_OFFSETS:
        moving = {name: shape.translate((0., offset, 0.))
                  for name, shape in {**pair, 'concealed-tube': tube}.items()}
        hit = contacts(parked, moving)
        if hit:
            park_feed.append(dict(offset_y_mm=offset, contacts=hit))
    final_pair = {**static, **pair, 'tube-soda-meter-bulkhead': tube}
    nut_slide = []
    for i in range(11):
        fraction = i/10.
        moved = parked.translate(tuple((axis-np.asarray(PARK))*fraction))
        hit = contacts(moved, final_pair)
        if hit:
            nut_slide.append(dict(fraction=fraction, contacts=hit))

    core_path = ROOT / 'hardware/cold-core-layout/cold-core-assembly.step'
    fixed_core = {name: core_to_world(shape)
                  for name, (shape, _color) in import_assembly(core_path).items()}
    fixed_core.update({name: row[0] for name, row in warm.items()
                       if name in layout.core_equipment_names()})
    fixed_core.update({name: row[0] for name, row in junctions.items()
                       if electrical.owner(name) == 'cold-core'})
    ride_offsets = (0., .25, .5, 1., *range(2, 302, 2))
    parked_box = bounds(parked)
    swept_box = np.array([parked_box[0], parked_box[1] + (0., 300., 0.)])
    ride = []
    for name, shape in fixed_core.items():
        box = bounds(shape)
        if not nearby(swept_box, box):
            continue
        hits = []
        for offset in ride_offsets:
            if not nearby(parked_box + (0., offset, 0.), box):
                continue
            v = volume(parked.translate((0., offset, 0.)).intersect(shape))
            if v > 1e-6:
                hits.append(dict(offset_y_mm=offset, overlap_mm3=v))
        ride.append(dict(body=name, hits=hits))

    # The bulkhead is fed from outside while its loose nut is brought onto
    # the barrel. Sampled axial envelopes do not model helical thread motion.
    soda_body = warm['bulkhead-carb'][0]
    soda_targets = {**final_pair, 'bulkhead-carb-nut': nut}
    stem_frame = layout.snapshot_pose('soda-stem-elbow')
    tip = layout.point(stem_frame, (-18.7452, 0., 0.))
    stem_mask = cq.Solid.makeCylinder(3.175, 12.7,
                                     cq.Vector(*tip), cq.Vector(0., -1., 0.))
    soda_targets['soda-stem-elbow'] = pair['soda-stem-elbow'].cut(stem_mask)
    soda_feed = translated_feed({'bulkhead-carb': soda_body}, soda_targets, FEED_OFFSETS)
    common = soda_body.intersect(pair['soda-stem-elbow'])
    residue = common.cut(stem_mask)
    residue_reading = dict(overlap_mm3=volume(residue),
                           bounds_world_mm=bounds(residue).tolist(),
                           treatment='Explicit accepted nominal-form contact outside the finite stem engagement. No shape trimming or broader mate mask. PP operating collet and NeoFit hub flare are unmeasured; physical fit remains unqualified.')

    drain_body = warm['bulkhead-drain'][0]
    drain_nut = warm['bulkhead-drain-nut'][0]
    after_soda = {**final_pair, 'bulkhead-carb': soda_body,
                  'bulkhead-carb-nut': nut}
    drain_feed = translated_feed({'bulkhead-drain': drain_body}, after_soda, FEED_OFFSETS)
    drain_nut_feed = translated_feed({'bulkhead-drain-nut': drain_nut},
                                     {**after_soda, 'bulkhead-drain': drain_body},
                                     (-11.7, -10., -8., -6., -4., -2., -1., 0.))
    rotations = {}
    for name, body, af, bore, depth in (
        ('bulkhead-carb-nut', nut, 20., 17.14, 4.),
        ('bulkhead-drain-nut', drain_nut, 18., 15., 6.5),
    ):
        box = bounds(body)
        center = box.mean(axis=0)
        annulus = cq.Solid.makeCylinder(af/math.sqrt(3.), depth,
            cq.Vector(center[0], box[0,1], center[2]), cq.Vector(0., 1., 0.)).cut(
            cq.Solid.makeCylinder(bore/2., depth,
                cq.Vector(center[0], box[0,1], center[2]), cq.Vector(0., 1., 0.)))
        rotation_targets = {**after_soda, 'bulkhead-drain': drain_body}
        rotation_targets.pop(name, None)
        rotations[name] = contacts(annulus, rotation_targets)

    sources = [Path(__file__), ROOT/'hardware/manifold-layout/above_core_parts.py',
               ROOT/'hardware/manifold-layout/above-core.json',
               ROOT/'hardware/reference/jg-bulkhead-union/jg_bulkhead_union.py',
               ROOT/'hardware/reference/neofit-drain-bulkhead/neofit_drain_bulkhead.py',
               ROOT/'hardware/manifold-layout/above_core_wiring.py',
               ROOT/'hardware/manifold-layout/above_core_routes.py',
               shell_path, core_path, *label_paths]
    collet = meter.intersect(pair['soda-outlet-return-stem'])
    report = dict(
        scope='Manual finite nominal CAD assembly envelopes. Current rear-wall STEP, purchased reference bodies, rear-region production tube spans and populated exported core are used. Electrical conductors and the flexible drain-vent line are dressed through the open roof afterward. No helical thread/collet release motion, tool or hand reach, installation force, hardware fit, retention, pressure, sealing or lifetime qualification.',
        primary_drawings={
            'PP1208E': dict(url='https://www.johnguest.com/sites/jg/files/2023-04/JG%20Drinks%20Polypropylene%20Bulkhead%20Connector%20Data%20Sheet.pdf',
                drawing='PP4608_01/23', nominal_mount_hole_N_mm=17.,
                released_collet_overall_B_mm=34.6,
                limits='Operating collet extensions are unmeasured. Selected nominal mouth planes and conservative outside flange retained.'),
            'ABU44M': dict(url='https://assets.freshwatersystems.com/image/upload/qnbgcy8djx3nj2weqz9v.pdf',
                thread='M15 x 1.5', panel_span_A_mm=8.1, nut_width_E_mm=6.5,
                limits='The drawing places the far body and collet inside the M15 barrel. Their exact profiles and operating mouth stations remain unmeasured; selected nominal mouth planes retained.')},
        production_adapters={
            'PP1208E': envelope_reading(parts.pp1208e_bulkhead(), 17.14/2., 24.79),
            'ABU44M': envelope_reading(parts.abu44m_bulkhead(), 15./2., 17.7)},
        late_bodies=list(LATE_BODIES), late_tube_ids=list(LATE_TUBES),
        sequence=[
            'Preplace the loose soda nut in the back-top rear relief at the recorded parked pose. Hold it or temporarily tape it at the rear wall with the roof panel open; no printed stock retains it. Keep both late bulkheads, the rear elbow pair and the two late flexible spans disconnected.',
            'Close the back-top over the populated core with the parked nut travelling with the back-top.',
            'Preassemble the two rear elbows and the concealed 32.591 mm tube, with 16.891 mm seated in the return elbow and 15.7 mm free for the meter.',
            'Move that assembly fore by 15.7 mm into the fixed meter outlet, maintaining the recorded coaxial pose.',
            'Slide the loose soda nut diagonally to its final axis. Feed the PP1208E from outside, engaging its inboard port with the fixed stem and threading the nut onto the barrel. The axial samples represent the combined envelope, not free sliding through real threads.',
            'Feed the adjacent ABU44M drain bulkhead from outside. Bring its nut from the inboard side onto the barrel and tighten. Connect the drain-vent tube and dress flexible conductors through the open roof.',
        ],
        rear_pair_feed_y_offsets_mm=list(PAIR_OFFSETS), rear_pair_feed=pair_feed,
        concealed_tube=dict(id='soda-meter-bulkhead', length_mm=32.591,
                             meter_insertion_mm=15.7, return_insertion_mm=16.891,
                             exposed_length_mm=0.),
        loose_soda_nut=dict(park_center_world_mm=list(PARK),
            clock_change_deg=NUT_CLOCK_CHANGE, static_contacts=park_static,
            retention='Loose part held or temporarily taped at the rear wall with the roof panel open. No printed retention, tape envelope, hand/tool path or retention capacity is qualified.',
            rear_pair_feed_contacts=park_feed, diagonal_transfer_contacts=nut_slide,
            ride_y_offsets_mm=list(ride_offsets), fixed_core_bodies=len(fixed_core),
            sampled_ride=ride),
        soda_bulkhead_feed=soda_feed, drain_bulkhead_feed=drain_feed,
        drain_nut_feed=drain_nut_feed, nut_rotation_envelope_contacts=rotations,
        accepted_nominal_soda_end_contact=residue_reading,
        meter_to_return_collet=dict(overlap_mm3=volume(collet),
                                    distance_mm=meter.distance(pair['soda-outlet-return-stem'])),
        source_sha256={str(path.relative_to(ROOT)):sha(path) for path in sources},
        seconds=time.monotonic()-started)
    output = HERE / 'rear-plumbing-assembly.json'
    output.write_text(json.dumps(report, indent=2)+'\n')
    print('REPORT '+str(output), flush=True)


def seven_member_candidate():
    """Read the evaluated tube-on-back-top scenario and finite capture."""
    started = time.monotonic()
    sys.path.insert(0, str(ROOT / 'hardware/assembly/scenes'))
    import _scenes
    candidate_members = (*LATE_BODIES, 'tube-soda-meter-bulkhead')

    appliance = ROOT / 'hardware/manifold-layout/enclosure-assembly.step'
    placed = {name: row[0] for name, row in import_assembly(appliance).items()}
    names = {name.rsplit('/', 1)[-1]: name for name in placed}
    boxes = {name: bounds(shape) for name, shape in placed.items()}
    stationary = {
        name: shape for name, shape in placed.items()
        if ('cold-core/' in name and boxes[name][1, 2] > 253.3)
        or name.rsplit('/', 1)[-1] in _scenes.BACK_TOP_INLET_HEADER
    }
    meter_name = names['digiten-flow']
    native_mouth, native_outward, diameter = parts.port_stations('digiten-flow')['outlet']
    frame = layout.pose('digiten-flow')
    mouth = np.asarray(layout.point(frame, native_mouth))
    outward = np.asarray(layout.vector(frame['rotation'], native_outward))
    inward = -outward
    insertion = 15.7
    margin = 1e-6
    mask = cq.Solid.makeCylinder(
        diameter / 2. + margin, insertion + 2. * margin,
        cq.Vector(*(mouth - margin * inward)), cq.Vector(*inward))
    masked = dict(stationary)
    masked[meter_name] = placed[meter_name].cut(mask)
    rows = []
    for tail in candidate_members:
        name = names[tail]
        low, high = boxes[name]
        if tail == 'tube-soda-meter-bulkhead':
            origin = mouth - insertion * outward
            origin[1] = low[1]
            swept = cq.Solid.makeCylinder(
                diameter / 2., high[1] - low[1] + 300.,
                cq.Vector(*origin), cq.Vector(0., 1., 0.))
            method = 'Continuous coaxial full outer cylinder'
        else:
            swept = cq.Solid.makeBox(
                *(high - low + np.array((0., 300., 0.))), cq.Vector(*low))
            method = 'Continuous full component bounding-box prism'
        readings = []
        for other_name, other in masked.items():
            if not nearby(bounds(swept), boxes[other_name]):
                continue
            readings.append({
                'body': other_name,
                'common_mm3': volume(swept.intersect(other)),
            })
        rows.append({
            'part': tail, 'bounds_world_mm': boxes[name].tolist(),
            'envelope': method, 'native_candidates': readings,
            'continuous_envelope_clear': all(row['common_mm3'] < 1e-6
                                             for row in readings),
        })

    tube = placed[names['tube-soda-meter-bulkhead']]
    capture = []
    for offset in (15.7, 14., 12., 10., 8., 6., 4., 2., 1., .5, .25, 0.):
        common = tube.translate((0., offset, 0.)).intersect(placed[meter_name])
        raw = volume(common)
        outside = volume(common.cut(mask)) if raw > 1e-10 else 0.
        capture.append({
            'offset_y_mm': offset, 'raw_common_mm3': raw,
            'outside_finite_outlet_mm3': outside,
        })
    path = HERE / 'rear-plumbing-assembly.json'
    report = json.loads(path.read_text())
    prior = report.get('evaluated_tube_on_back_top_scenario', {})
    prior.update({
        'scope': 'The selected seven-member rear group rides with back-top. '
                 'Continuous conservative component prisms and a coaxial tube '
                 'cylinder bound every closing offset from +Y300 mm to zero. '
                 'Only the fixed meter outlet finite receiving region permits '
                 'intended tube capture. The connected inlet header and '
                 'populated core remain stationary. No thread tightening, '
                 'hand/tool reach, installation force, sealing or retention '
                 'qualification is inferred.',
        'base_appliance_sha256': sha(appliance),
        'moving_components': list(candidate_members),
        'stationary_components': sorted(stationary),
        'continuous_prism_readings': rows,
        'finite_outlet_capture': {
            'mouth_world_mm': mouth.tolist(),
            'outward_world': outward.tolist(),
            'radius_mm': diameter / 2., 'insertion_mm': insertion,
            'readings': capture,
        },
        'continuous_carried_group_clear': all(row['continuous_envelope_clear']
                                              for row in rows),
        'finite_outlet_capture_clear': all(row['outside_finite_outlet_mm3'] < 1e-6
                                           for row in capture),
        'source_sha256': {
            str(source.relative_to(ROOT)): sha(source)
            for source in (Path(__file__), Path(_scenes.__file__),
                           ROOT / 'hardware/manifold-layout/above-core.json',
                           ROOT / 'hardware/manifold-layout/above_core_parts.py')
        },
        'seconds': time.monotonic() - started,
    })
    report['evaluated_tube_on_back_top_scenario'] = prior
    path.write_text(json.dumps(report, indent=2) + '\n')
    print('REPORT ' + str(path), flush=True)


def main():
    if '--evaluated-seven-member-candidate' in sys.argv:
        seven_member_candidate()
    else:
        import approved_carried_group_review
        approved_carried_group_review.main()


if __name__ == '__main__':
    main()
