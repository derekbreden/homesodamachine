"""Numeric installation inputs for the machine's Rust placement program.

The inputs are current part models and authored scalar datums. A plan carries ordered
references and installed frames, with no CadQuery, OCP or meshcad geometry in Python.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HW = ROOT / 'hardware'
LAYOUT = HW / 'manifold-layout'
ENCLOSURE = HW / 'printed-parts/enclosure/enclosure'
for _path in (ROOT, LAYOUT, ENCLOSURE, HW / 'cold-core-layout',
              HW / 'reference/compressor', HW / 'reference/mq6-gas-sensor',
              HW / 'reference/sf76e-thermal-fuse'):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))


def _source(root, path):
    """Current producer models or the declared fine geometry of a frozen reference."""
    relative = Path(path)
    path = Path(root) / relative
    authored = ROOT / relative
    for manifest in (path.parent / 'frozen-asset.json', authored.parent / 'frozen-asset.json'):
        if not manifest.is_file():
            continue
        record = json.loads(manifest.read_text())
        selected = record.get('fine_models', {}).get(path.name)
        if selected is None and path.name in record.get('members', {}):
            selected = record.get('fine_model')
        if selected:
            supplied = path.parent / selected['path']
            return str(supplied if supplied.is_file() else authored.parent / selected['path'])
    fine = Path(str(path) + '.npz')
    return str(fine if fine.is_file() else Path(str(path) + '.mesh'))


def _linear(color):
    from _materials import linear
    return linear(color)


def _point(frame, point):
    return tuple(sum(frame[i][j] * point[j] for j in range(3)) + frame[i][3]
                 for i in range(3))


def _axis(frame, axis):
    return tuple(sum(frame[i][j] * axis[j] for j in range(3)) for i in range(3))


def _installed(point):
    x, y, z = point
    return -x, z + 14.48, y + 201.425


def _manifold_datums(enc, construction):
    """The pump bracket and tee-wall numbers, from their authored case datums."""
    kp = enc._tray._kp
    tee = enc._dock.tee
    plumbing = enc._dock.plumbing
    interface = enc._interface
    import manifold_layout as manifold
    pump_pitch = tee.BRANCH_REACH + kp.barb_pitch / 2.
    barb_z = kp.head_w - interface.pump_station_lead
    pump_y = (kp.outlet_above_skirt_bottom - interface.pump_station_drop
              - interface.pump_seated_drop - interface.manifold_rise)
    inset = kp.arch_plane_z - kp.head_front_z
    head_y = -inset + pump_y - kp.head_front_z + kp.base_plane_z
    head_z = barb_z - kp.body_y_face + kp.cy
    pump_trays = []
    for px in (-pump_pitch, pump_pitch):
        center = list(_installed((px, head_y, head_z)))
        center[2] += interface.pump_seated_drop
        pump_trays.append(tuple(round(c, 6) for c in center))
    # Each current reference row already carries the manifold's source frame. The native
    # collet datums ride it, then the machine's explicit installed frame.
    rows = {row['name']: row for row in construction['bodies'] if row['kind'] == 'reference'}
    valve_ports = {'inlet': ((0., -29.75, 11.05), (0., -1., 0.), 6.35),
                   'outlet': ((0., 29.75, 11.05), (0., 1., 0.), 6.35)}
    manifold_ports = {name: valve_ports for name in rows if name.startswith('valve-v-')}
    for name in ('valve-v-g', 'valve-v-j'):
        manifold_ports[name] = {**valve_ports,
            'outlet': ((0., 29.75 + (1.445 - .827) * 25.4, 11.05), (0., 1., 0.), 4.)}
    tee_ports = {'lower': ((0., 0., -tee.RUN_HALF), (0., 0., -1.), 6.35),
                 'upper': ((0., 0., tee.RUN_HALF), (0., 0., 1.), 6.35),
                 'branch': ((0., tee.BRANCH_REACH, 0.), (0., 1., 0.), 6.35)}
    manifold_ports.update({name: tee_ports for name in rows if name.startswith('tee-y-')})
    barbs = {'Y-C': (-pump_pitch, 1), 'Y-D': (-pump_pitch, -1),
             'Y-F': (pump_pitch, -1), 'Y-G': (pump_pitch, 1)}
    valves = {'Y-C': ('V-E', 'V-C'), 'Y-D': ('V-F', 'V-G'),
              'Y-F': ('V-H', 'V-D'), 'Y-G': ('V-I', 'V-J')}
    holes, upper, returns = [], {}, {}
    # The production prepared tube places its tip BARB_TO_PLATE + TIP_FROM_FORE past its
    # barb. This is the datum used by manifold_layout.pump_wall_fore_y(), not a mesh bound.
    fore = round(_installed((0., pump_y, barb_z))[1] + 5.351, 6)
    for name, (px, side) in sorted(barbs.items()):
        at = _installed((px + side * kp.barb_pitch / 2., pump_y, barb_z))
        x, z = round(at[0], 6), round(at[2], 6)
        holes.append((x, z))
        for destination, valve, end in ((upper, valves[name][0], 'front'),
                                          (returns, valves[name][1], 'back')):
            direction = manifold.port_axis(valve, end)
            destination[str(x)] = {'point': _installed(manifold.port(valve, end)),
                                  'axis': (-direction[0], direction[2], direction[1]),
                                  'valve': valve}
    collet = {'holes': sorted(holes), 'fore_y': fore,
              'aft_y': round(plumbing.plate_aft_y(fore), 6),
              'wall_aft_y': round(enc._dock.wall_aft_y(fore), 6),
              'x0': enc.interior_x()[0], 'x1': enc.interior_x()[1],
              'z0': enc.z_seam, 'z1': 218.85,
              'hole_d': 2 * enc._dock.HOLE_R,
              'seat_z': round(enc.bay_floor_z(pump_trays)[1], 6),
              'upper_ports': upper, 'return_ports': returns, 'valve_trays': [],
              'fixture_print_bed_z': enc.z_seam + enc.slide_slip,
              'tee_axis_y': round(plumbing.tee_axis_y(fore), 6),
              'seated_tube_bottom_y': round(plumbing.tip_y(fore), 6),
              'tube_bottom_y': round(plumbing.tip_y(fore), 6),
              'pump_tube_cut': 13.149 + 5.351 + plumbing.TIP_FROM_FORE,
              'assembly_state': 'seated'}
    authored = {'water-7', 'water-6', 'water-5', 'water-2', 'fluid-1', 'water-3',
                'co2-0', 'co2-1', 'co2-2', 'fluid-2', 'fluid-4', 'fluid-28', 'carb-1', 'carb-2',
                'fluid-18', 'fluid-24', 'fluid-26', 'fluid-14', 'fluid-16',
                'refrig-3', 'refrig-2', 'refrig-1'}
    omitted = {'valve-v-a', 'coil-v-a', 'valve-v-b', 'coil-v-b',
               'step-fluid-3', 'step-fluid-5', 'turn-fluid-3', 'turn-fluid-5',
               'stub-fluid-2', 'stub-fluid-4'} | {'stub-' + name for name in authored}
    for name in barbs:
        omitted.add('tee-' + name.lower())
        for host in (name, valves[name][1]):
            omitted.add('stem-elbow-' + host.lower())
    return {'manifold_exclude': sorted(omitted), 'manifold_ports': manifold_ports,
            'pump_trays': pump_trays, 'collet_plate': collet,
            'pump_face_z': pump_y - inset}


def numbers(*, stage='pack', box_document=None, input_root=ROOT):
    import _rust_part
    _rust_part.start()
    import _enclosure_datums
    enc = _enclosure_datums.load()
    import core_reference
    import compressor
    import mq6_gas_sensor as mq6
    import sf76e_thermal_fuse as fuse
    from _materials import (C_COMP, C_COND, C_MQ6, C_DISPLAY_GLASS, C_AC_HUB,
                            M_TINNED_STEEL, M_PETG_BLACK, M_PETGF_BLACK,
                            M_SILICONE_BLACK, M_TPU_BLACK, M_STAINLESS, M_BRASS,
                            M_NEOFIT_WHITE_ACETAL, M_DONOR_BLACK)
    root = Path(input_root)
    construction = json.loads((root / 'hardware/manifold-layout/manifold-layout.numbers.json').read_text())
    core = core_reference.datums()
    import _cold_core_interface as cci
    core['source_seat'] = core['seat']
    core['corner_round_radius'] = cci.corner_round_radius
    core['ports'] = {name: (*mouth, 6.35) for name, mouth in core['conduit_mouths'].items()}
    core['ports'].update({name: (*mouth, 6.35) for name, mouth in core['copper_mouths'].items()})
    datums = {'compressor_front': 11., 'world_lift': 201.425, 'pack_y': 14.48,
               'suction_lane_x': enc.lip_face_x()[0] + 25.4,
               'cond_bore_depth': enc.cond_bore_depth,
               'cond_mount_clear': enc.cond_mount_clear,
               'cond_slot_press': enc.cond_slot_press,
               'cond_slot_grip': enc.cond_slot_grip, 'cond_rail_wall': enc.cond_rail_wall,
               'front_bottom_west': enc.front_bottom_flank_face()[0],
               'front_bottom_east': enc.front_bottom_flank_face()[1],
               'front_top_west': enc.front_top_flank_face()[0],
               'front_top_east': enc.front_top_flank_face()[1],
               'clearance_floor': 1., 'mq6_y0': 38.3, 'mq6_rail_wall': enc.mq6_rail_wall,
               'mq6_card_plane': mq6.card_plane()[0], 'floor_grommet_squeeze': .4,
               'floor_boss_slip': 1., 'rear_plane_y': enc.rear_plane_y,
               'rear_seam_clear': enc.rear_seam_clear, 'core_stop_rise': enc.core_stop_rise,
               'through_wall': ['bulkhead-water', 'c14-inlet', 'keystone-jack', 'co2-inlet',
                                'bulkhead-flavor-a', 'bulkhead-flavor-b', 'bulkhead-carb', 'bulkhead-drain'],
               'compressor': {'ports': {name: (*mouth, 6.35) for name, mouth in compressor.stations().items()},
                   'power_face': compressor.power_face()[0], 'mount_xy': compressor.mount_pattern(),
                   'base_z': compressor.BASE_Z, 'mount_d': compressor.MOUNT_D,
                   'power_y': compressor.POWER_Y, 'power_z': compressor.POWER_Z},
               'fuse': {'length': fuse.LENGTH, 'diameter': fuse.BODY_D},
               'condenser': {'airflow': 56., 'face_a': 154., 'face_b': 137.,
                   'plate_t': .4, 'recess_y': 20., 'mount_x': 29., 'mount_y': 139., 'mount_d': 5.,
                   'ports': {'refrig-inlet': ((0., 87., 66.), (-1., 0., 0.), 6.35),
                             'refrig-outlet': ((33., 154., 38.75), (0., 1., 0.), 6.35)}}}
    datums.update(_manifold_datums(enc, construction))
    colors = {'compressor': C_COMP, 'condenser': C_COND, 'mq6': C_MQ6,
              'fuse': M_TINNED_STEEL, 'fuse_clamp': M_PETG_BLACK,
              'funnel': M_SILICONE_BLACK, 'funnel_cover': M_PETG_BLACK,
              'display': C_DISPLAY_GLASS, 'display_cover': M_PETGF_BLACK,
              'display_gasket': M_TPU_BLACK, 'wago': C_AC_HUB,
              'screw': M_STAINLESS, 'insert': M_BRASS, 'seam_screw': M_DONOR_BLACK,
              'elbow': M_NEOFIT_WHITE_ACETAL}
    sources = {'compressor': _source(root, 'hardware/reference/compressor/compressor.step'),
               'mq6': _source(root, 'hardware/reference/mq6-gas-sensor/mq6-gas-sensor.step'),
               'fuse': _source(root, 'hardware/reference/sf76e-thermal-fuse/sf76e-thermal-fuse.step'),
               'fuse_clamp': _source(root, 'hardware/printed-parts/refrigeration/fuse-clamp/fuse-clamp.step'),
               'manifold': str(root / 'hardware/manifold-layout/manifold-layout.step.npz'),
               'core': str(root / 'hardware/cold-core-layout/cold-core-assembly.scene.npz'),
               'casing': str(root / 'hardware/printed-parts/cold-core/foam-assembly/foam-assembly.step.npz')}
    return {'stage': stage, 'sources': sources, 'datums': datums,
            'input_root': str(root),
            'core_datums': core, 'colors': {name: _linear(color) for name, color in colors.items()},
            'above_core': json.loads((root / 'hardware/manifold-layout/above-core.json').read_text()),
            'manifold_numbers': construction, 'box': box_document,
            'equipment': {}, 'installed': {}}


def _box_tuple(document, enc):
    import _box_spec
    records = {cls.__name__: cls for cls in (enc.Pack, enc.PortField, enc.Nameplate)}
    return enc.Box(*(_box_spec._tupled(document['box'][field], records)
                     for field in enc.Box._fields))


def installed_numbers(request, document, *, input_root=ROOT):
    """The wall-carried stations and purchased installed bodies, as scalar Rust inputs."""
    import _enclosure_datums
    enc = _enclosure_datums.load()
    box = _box_tuple(document, enc)
    import elbow_cradle
    import neofit_stem_elbow as elbow
    frame = enc._funnel_frame_part
    funnel = enc._funnel
    cx, cy = (box.inner[0] + box.inner[1]) / 2., frame.center_y
    seat = enc.funnel_seat_z(box.outer)
    floor = frame.datums(seat)[0]
    _angle, normal, origin, _dy, _dz = enc._facet_geom(box.outer)
    fasteners = frame.fastener_datums(box.inner, box.y_joint, (cx, cy), seat)
    seam = []
    for side, xi, sx in (('west', box.inner[0], 1.), ('east', box.inner[1], -1.)):
        for station, head, tip, length, owner, insert0, insert1 in enc.y_stack_rods(box.inner):
            x, y = enc.y_stack_axis(xi, sx, box.y_joint, station)
            seam.append({'name': f'y-seam-{side}-{station}', 'x': x, 'y': y,
                         'seat': head, 'tip': tip, 'upward': station == 'lower',
                         'insert0': insert0, 'insert1': insert1, 'owner': owner,
                         'length': length})
    data = {'cx': cx, 'cy': cy, 'funnel_seat_z': seat,
             'cover_z': box.outer[5] + funnel.apron_rise,
             'frame_floor': floor, 'frame_front': frame.roof_datums(box.inner, (cx, cy), seat, box.y_joint)['front'],
             'neck_dx': funnel.neck_dx, 'neck_dy': funnel.neck_dy,
             'cradle_catch_gap': elbow_cradle.CATCH_GAP,
             'cradle_source_z0': elbow_cradle.block()[3],
             'drain_stem_tip': elbow.stem_tip()[0], 'drain_ports': {
                 'stub': (*elbow.stem_tip(), elbow.STEM_OD),
                 'outlet': (*elbow.socket(), elbow.TUBE_OD)},
             'funnel_ports': {'drain': (funnel.drain_local, (0., 0., -1.), funnel.spout_id)},
             'spout_land_z': funnel.spout_land_z,
             'display_angle_deg': enc.display_facet_angle_deg,
             'display_origin': origin, 'display_normal': normal,
             'display_centre_x': enc.display_centre_x(box.outer),
             'display_bezel_depth': enc.display_bezel_depth,
             'display_native_bezel_depth': 1.,
             'display_body_offset_x': enc.display_body_offset_x,
             'display_body_offset_slope': enc.display_body_offset_slope,
             'display_cover_origin': enc.display_plane(box.outer).origin.toTuple(),
             'funnel_fasteners': fasteners, 'y_seam': seam,
             'funnel_seal': {'point': (cx + funnel.neck_dx, cy + funnel.neck_dy, seat + funnel.spout_land_z),
                             'outer_radius': elbow.STEM_OD / 2.,
                             'inner_radius': funnel.spout_id / 2., 'length': funnel.sealing_land}}
    paths = {'funnel': 'printed-parts/zone-c/funnel/funnel.step',
              'funnel_cover': 'printed-parts/zone-c/funnel-cover/funnel-cover.step',
              'cradle': 'printed-parts/zone-c/funnel/elbow-cradle.step',
              'stem_elbow': 'reference/neofit-stem-elbow/neofit-stem-elbow.step',
              'display': 'reference/waveshare-43b-display/waveshare-43b-display.step',
              'display_cover': 'printed-parts/enclosure/display-cover/display-cover.step',
              'display_gasket': 'printed-parts/enclosure/display-gasket/display-gasket.step'}
    request['sources'].update({name: _source(input_root, 'hardware/' + path) for name, path in paths.items()})
    request['piece_models'] = {name: _source(input_root,
        f'hardware/printed-parts/enclosure/enclosure/enclosure-{name}.step')
        for name in ('front-bottom', 'front-top', 'back-bottom', 'back-top', 'pump-retainer')}
    request['installed_datums'] = data
    return box


def _run_records(frames):
    """The three existing copper routes, solved as scalar paths and cut in Rust."""
    import _rust_part
    _rust_part.start()
    import _routing as routing
    from types import SimpleNamespace
    for name, row in frames.items():
        if not row.get('ports'):
            continue
        b = row.get('bb', (0., 0., 0., 0., 0., 0.))
        ports = {port: (tuple(item['pos']), tuple(item['axis']), item['diam'])
                 for port, item in row['ports'].items()}
        routing.frame(name, None, ports, bb=SimpleNamespace(**dict(zip(
            ('xmin', 'xmax', 'ymin', 'ymax', 'zmin', 'zmax'), b))))
    records, sweeps = [], []
    for identifier, frm, to, kwargs in (
            ('refrig-1', 'compressor.refrig-discharge', 'condenser+fan.refrig-inlet', {}),
            ('refrig-2', 'condenser+fan.refrig-outlet', 'foam-assembly.evap-inlet', {'lead': 2., 'min_bend': 8.}),
            ('refrig-3', 'compressor.refrig-suction', 'foam-assembly.evap-outlet', {'bend': 12.7, 'lead': 20.})):
        run = routing.bent(identifier, frm, to, kind='refrigerant', **kwargs)
        records.append({**vars(run), 'length': run.length})
        # A sweep's path stays the exact lines and three-point circular arcs the old
        # centreline constructor made; only their evaluation moves to the Rust kernel.
        need = {i: run.radii[i] * math.tan(math.radians(turn) / 2.)
                for i, turn, _a, _b in run.bends}
        segments, cursor = [], run.pts[0]
        for i, turn, _a, _b in run.bends:
            if not need[i]:
                continue
            vertex = run.pts[i]
            incoming = routing._unit(run.pts[i - 1], vertex)
            outgoing = routing._unit(vertex, run.pts[i + 1])
            p1 = [vertex[k] - incoming[k] * need[i] for k in range(3)]
            p2 = [vertex[k] + outgoing[k] * need[i] for k in range(3)]
            bisector = [outgoing[k] - incoming[k] for k in range(3)]
            span = math.sqrt(sum(c * c for c in bisector))
            distance = run.radii[i] / math.cos(math.radians(turn) / 2.)
            center = [vertex[k] + bisector[k] / span * distance for k in range(3)]
            radial = [vertex[k] - center[k] for k in range(3)]
            span = math.sqrt(sum(c * c for c in radial))
            middle = [center[k] + radial[k] / span * run.radii[i] for k in range(3)]
            if math.dist(cursor, p1) > 1e-9:
                segments.append({'kind': 'line', 'points_mm': [cursor, p1]})
            segments.append({'kind': 'arc', 'points_mm': [p1, middle, p2]})
            cursor = p2
        if math.dist(cursor, run.pts[-1]) > 1e-9:
            segments.append({'kind': 'line', 'points_mm': [cursor, run.pts[-1]]})
        from _materials import linear, M_COPPER
        sweeps.append({'name': 'tube-' + identifier, 'segments': segments,
                       'od_mm': run.diam, 'id_mm': 0., 'color': linear(M_COPPER)})
    return records, sweeps


def _result_plan(receipt, directory, name):
    if 'instances' in receipt:
        return receipt
    path = Path(directory) / (name + '.json')
    if path.is_file():
        return json.loads(path.read_text())
    for result in reversed(receipt.get('results', ())):
        if 'instances' in result:
            return result
    raise ValueError(f'{name} did not emit its model-reference plan')


def _route_records(routes):
    """The existing reporting Run rows for explicitly authored native paths."""
    result = []
    for name, row in routes.items():
        owners = row.get('owners', ('', ''))
        points = row.get('points_mm', row.get('centerline_mm'))
        if points is None:
            # Copper runs retain their corner/radius records separately.
            continue
        result.append({'id': name, 'kind': 'fluid', 'frm': row.get('frm', row.get('from', owners[0])),
                       'to': row.get('to', owners[-1]), 'pts': points, 'diam': row['od_mm'],
                       'bend': row.get('minimum_radius_mm') or 0., 'note': row.get('basis', ''),
                       'min_bend': None, 'bends': [], 'radii': {}, 'caps': {},
                       'length': sum(math.dist(a, b) for a, b in zip(points, points[1:]))})
    return result


def _placement_metadata(request, equipment_request, runs):
    import _enclosure_datums
    enc = _enclosure_datums.load()
    import above_core
    import above_core_wiring
    import manifold_layout as ml
    import _stated_bounds
    import _cold_core_interface as core
    import _reservoir_a_anchors

    def made(how):
        if how == 'spine': return 'elbows'
        if how in ml.BARB_OF: return 'pump-dock'
        if how in ml.FORE_STUBS: return 'straight'
        if how in ('turn', 'butt'): return how
        return 'straight' if math.dist(*ml.RUNS[how]) > 1e-9 else 'butt'

    holders = {}
    pump_at = {x: name for name, x in ml.PUMPS.items()}
    for cid, _frm, _to, how in ml.SEGMENTS:
        if how in ml.BARB_OF:
            holders[f'tube-fluid-{cid}'] = pump_at[ml.BARB_OF[how][0]] + '-head'
        elif how in ml.FORE_STUBS:
            holders[f'tube-fluid-{cid}'] = 'enclosure-front-top'
    holders.update({f'tube-fluid-{cid}': 'enclosure-front-top' for cid in ml.lower_links()})
    anchors = []
    active = {run['id'] for run in runs}
    anchor_spec = _reservoir_a_anchors.specification()
    for row in _reservoir_a_anchors.datums().values():
        for name, point, axis in zip(row['routes_west_to_east'], row['tube_centers_world_mm'], row['tube_axes_world']):
            if name in active:
                anchors.append((point, axis, (0., 0., -1.), row.get('seat_radius_mm', anchor_spec['seat_radius_mm'])))
    bounds = [{**bound._asdict(), 'kind': 'gate'} for bound in _stated_bounds.records()]
    if request.get('box'):
        import _box_spec
        bounds.extend({key: _box_spec._tupled(value, {}) for key, value in row.items()}
                      for row in request['box']['bounds'])
    metadata = {'runs': runs, 'native_route_specs': equipment_request['routes'],
        'native_route_order': list(equipment_request['routes']),
        'route_lengths': {name: row['length_mm'] for name, row in equipment_request['routes'].items()
                          if 'length_mm' in row},
        'world_ports': equipment_request['world_ports'],
        'native_connections': above_core.logical_connections(),
        'manifold_connection_made': {'fluid-' + str(cid): made(how) for cid, _frm, _to, how in ml.SEGMENTS},
        'refrigerant_mates': [], 'blocked_runs': {}, 'bounds': bounds,
        'tube_anchor_sites': [], 'tube_anchor_pieces': {}, 'tube_anchors': [], 'body_anchors': [],
        'cap_tube_anchors': anchors, 'tube_anchor_span': 200.,
        'manifold_tube_holders': holders,
        'core_equipment_names': sorted(above_core.core_equipment_names()),
        'cap_anchor_names': [name for name, row in core.cap_anchors.items() if row.closure == 'cap'],
        'cap_conduits': list(core.cap_conduits),
        'selected_fitting_names': equipment_request['component_order'],
        'fluid_grid_assignment': request['above_core']['fluid_grid']['assignment'],
        'wiring_placements': above_core_wiring.placements(),
        'soft_neighbors': equipment_request.get('insulation', {}).get('neighbors', ()),
        'wall_mount_datums': enc._above_core_shell.wall_mount_datums(),
        'keystone_station': (request['above_core']['rear_wall']['dry_openings']['keystone']['face_center_mm'][0],
                             request['above_core']['rear_wall']['dry_openings']['keystone']['face_center_mm'][2]),
        'keystone_clearances': [],
        'core_alpha_by_name': {}, 'bed': [325., 320., 320.]}
    from _assembly_model import document
    metadata['core_alpha_by_name'] = document(request['sources']['core']).get('alpha_by_name', {})
    installed = request.get('installed_datums', {})
    metadata.update(funnel_fasteners=installed.get('funnel_fasteners', []),
                    funnel_seal=installed.get('funnel_seal'),
                    y_seam_insert_datums=installed.get('y_seam', []))
    return metadata


def _equipment(request, prepared, directory):
    import _machine_equipment
    import _machine_routes
    ports = {name: {port: (row['pos'], row['axis'], row['diam'])
                    for port, row in value['ports'].items()}
             for name, value in prepared['metadata']['frames'].items()}
    equipment_request = _machine_equipment.numbers(external_ports=ports, input_root=request['input_root'])
    equipment = _result_plan(_machine_equipment.build(Path(directory) / 'equipment', external_ports=ports,
                                                       input_root=request['input_root']),
                             Path(directory) / 'equipment', 'machine-equipment')
    model = str(Path(directory) / 'equipment/machine-equipment.step.npz')
    route_inputs = _machine_routes.equipment_inputs(equipment_request, model, equipment['groups'])
    copper_records, copper_sweeps = _run_records(prepared['metadata']['frames'])
    # The normal assembly writes the copper before all warm-side continuations.
    route_inputs['routes'] = {row['name'].removeprefix('tube-'):
            {**{k: v for k, v in row.items() if k != 'name'}, 'spool': 'copper'}
        for row in copper_sweeps} | route_inputs['routes']
    routes = _result_plan(_machine_routes.build(Path(directory) / 'routes', **route_inputs),
                          Path(directory) / 'routes', 'machine-routes')
    for name, length in routes.get('lengths', routes.get('route_lengths', {})).items():
        if name in equipment_request['routes']:
            equipment_request['routes'][name]['length_mm'] = length
    equipment['instances'].extend(routes['instances'])
    equipment['route_specs'] = equipment_request['routes']
    equipment['metadata'] = _placement_metadata(request, equipment_request,
        copper_records + _route_records(equipment_request['routes']))
    equipment['core_equipment'] = equipment_request['core_equipment']
    equipment['component_order'] = equipment_request['component_order']
    equipment['frames'] = {name: {'transform': row['transform'],
        'ports': {port: {'pos': p, 'axis': u, 'diam': d}
                  for port, (p, u, d) in equipment_request['world_ports'].get(name, {}).items()}}
        for name, row in equipment_request['frames'].items()}
    # Installed electrical junctions use frozen references and scalar frames. Their geometry
    # follows the same ordered reference/placement path as every other purchased component.
    import above_core_wiring
    for name, row in above_core_wiring.placements().items():
        instance = {'model': _source(Path(request['sources']['core']).parents[2], f'hardware/reference/wago-221/wago-221-{row["size"]}.step'),
                    'name': name, 'transform': [list(r) + [t] for r, t in zip(row['rotation'], row['translation_mm'])],
                    'color': request['colors']['wago'], 'owner': row['parent']}
        equipment.setdefault('junctions', []).append(instance)
    return equipment


def _bind_presentations(plan, input_root=ROOT):
    """Explicit frozen drawings for raw source-model packets without a bound payload."""
    manifests = {}
    skins = plan.setdefault('presentation', [])
    existing = {json.dumps(row, sort_keys=True) for row in skins}
    for row in plan['instances']:
        model = Path(row['model'])
        if model.parent not in manifests:
            path = model.parent / 'frozen-asset.json'
            manifests[model.parent] = json.loads(path.read_text()) if path.is_file() else {}
        manifest = manifests[model.parent]
        fine = manifest.get('fine_model', {})
        if fine.get('path') != model.name:
            continue
        payload = model.parent / manifest['fine_payload']['path']
        if not payload.is_file() and payload.is_relative_to(ROOT):
            payload = Path(input_root) / payload.relative_to(ROOT)
        skin = {'payload': str(payload), 'indices': row.get('indices'),
                'transform': row['transform'], 'targets': [row['name']]}
        key = json.dumps(skin, sort_keys=True)
        if key not in existing:
            skins.append(skin)
            existing.add(key)
    return plan


def _run(request, directory):
    import _rust_part
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    output = directory / 'machine-layout.json'
    _rust_part.cut('machine', 'machine-layout', {'request': request}, directory)
    plan = json.loads(output.read_text())
    staged = plan['generated_model']
    installed = str((directory / 'machine-layout.parts.npz').resolve())

    def local(value):
        if isinstance(value, dict):
            return {key: local(row) for key, row in value.items()}
        if isinstance(value, list):
            return [local(row) for row in value]
        return installed if value == staged else value

    plan = _bind_presentations(local(plan), request.get('input_root', ROOT))
    output.write_text(json.dumps(plan, separators=(',', ':')) + '\n')
    return plan


def plan(*, stage='pack', box_document=None, directory=None, input_root=ROOT):
    """The current installed reference plan, with scalar construction/check metadata."""
    if directory is None:
        directory = ROOT / '.cache/hsm/machine-layout' / stage
    request = numbers(stage='pack', box_document=box_document, input_root=input_root)
    prepared = _run(request, Path(directory) / 'references')
    if stage == 'installed':
        box = installed_numbers(request, box_document, input_root=input_root)
        import _enclosure_rust_driver
        request['installed'] = _enclosure_rust_driver.installed_instances(box_document, Path(directory) / 'enclosure')
        panels = [{'model': _source(input_root, f'hardware/printed-parts/enclosure/enclosure/enclosure-{name}.step'),
                   'name': 'enclosure-' + name, 'color': request['colors']['display_cover']}
                  for name in ('front-bottom', 'front-top', 'back-bottom', 'back-top')]
        ordinary = request['installed'].setdefault('instances', [])
        for row in ordinary:
            if row.get('name', '').endswith('-word') or row.get('name') == 'nameplate-ink':
                row['split_components'] = True
        retainer = [row for row in ordinary if row.get('name') == 'enclosure-pump-retainer']
        request['installed']['instances'] = [row for row in ordinary if row not in retainer] + panels + retainer
        request['dock'] = dock_instances(box.pack.collet_plate, Path(directory) / 'dock', input_root=input_root)
    equipment = _equipment(request, prepared, directory)
    request.update(prepared=prepared, equipment=equipment, stage=stage)
    return _run(request, Path(directory) / 'complete')


def dock_instances(plate, directory=None, *, input_root=ROOT):
    """The purchased pump tees and their trimmed return elbows as world fine references."""
    import _enclosure_datums
    enc = _enclosure_datums.load()
    from _materials import M_NEOFIT_WHITE_ACETAL, M_JG_BLACK_PP
    layouts = enc._dock.plumbing.layouts(plate)
    rows = []
    for station, tee_name, x, z in enc._dock.stations(plate):
        target = plate['return_ports'][str(x)]
        rows.append({'tee': 'tee-' + tee_name.lower(), 'x': x, 'z': z,
                     'tee_y': enc._dock.plumbing.tee_axis_y(plate['fore_y']),
                     'elbows': [{'name': 'stem-elbow-' + host.lower(), **row}
                                for host, row in zip((tee_name, target['valve']), layouts[str(x)]['return']['elbows'])]})
    request = {'stage': 'dock', 'sources': {
        'tee': _source(input_root, 'hardware/reference/tee-connector/tee-connector.step'),
        'stem_elbow': _source(input_root, 'hardware/reference/neofit-stem-elbow/neofit-stem-elbow.step')},
        'dock_rows': rows, 'hub_back_reach': enc._dock.stem_elbow.HUB_BACK_REACH,
        'colors': {'tee': _linear(M_JG_BLACK_PP), 'elbow': _linear(M_NEOFIT_WHITE_ACETAL)}}
    return _run(request, directory or ROOT / '.cache/hsm/machine-layout/dock')


def main():
    """Normal assembly entry: scalar input, Rust construction/checking and Rust exports."""
    import _box_spec
    import _machine_export
    import _machine_checks
    import _machine_reporting
    path = _box_spec.ARTIFACT
    box_document = json.loads(path.read_text())
    spec = plan(stage='installed', box_document=box_document)
    output = LAYOUT / 'enclosure-assembly.step'
    produced = _machine_export.export(spec, output.parent)
    model = str(output) + '.npz'
    metadata = spec['metadata']
    from hardware.wiring.installed.build import export_from_fine
    wiring = export_from_fine(model, output, _machine_reporting.scalar_namespace(spec))
    from _assembly_model import identity
    wire_model = HW / 'wiring/enclosure-wiring.step.npz'
    metadata['wiring_names'] = sorted({
        name.rsplit('/', 1)[0] if name.rsplit('/', 1)[-1].isdigit() else name
        for name, _color in identity(wire_model)})
    checked = _machine_checks.check(model, envelope=spec['envelope'],
                                     aliases=spec.get('aliases', {}), metadata=metadata)
    metadata.update(mounts=checked.get('mounts', []), rides=checked.get('rides', {}))
    document = _machine_reporting.scene_document(spec, checked)
    _machine_export.scene(model, LAYOUT / 'enclosure-assembly.scene.npz',
                          aliases=spec.get('aliases', {}), envelope=spec['envelope'], document=document)
    for name, value in [('enclosure-assembly.scorecard.json', checked['scorecard']),
                        ('drain-clearance-check.json', checked['drain'])]:
        (LAYOUT / name).write_text(json.dumps(value, indent=2) + '\n')
    _machine_reporting.write(spec, checked, model,
                             scene_path=LAYOUT / 'enclosure-assembly.scene.npz',
                             step_path=output, scorecard_path=LAYOUT / 'enclosure-assembly.scorecard.json')
    spec['checks'] = checked
    _view_metadata(spec, model)
    sys.path.insert(0, str(HW / 'assembly/scenes'))
    import render_scenes
    render_scenes.write_glbs(spec, require_core_payload=True)
    return produced, checked


def _view_metadata(spec, model):
    """Names and stock RGBA for existing viewer scenes, without geometry objects."""
    import _assembly_model
    metadata = spec['metadata']
    metadata['core_carry3x4'] = metadata['core_carry']
    colours = {}
    alpha = metadata.get('core_alpha_by_name', {})
    for name, color in _assembly_model.identity(model):
        stem, _, tail = name.rpartition('/')
        name = stem if tail.isdigit() else name
        if color is not None:
            colours[name] = [*color, alpha.get(name.removeprefix('cold-core/'), 1.)]
    metadata['rgba'] = colours
    metadata['colours'] = colours
    metadata['core_rgba'] = {name.removeprefix('cold-core/'): color for name, color in colours.items()
                              if name.startswith('cold-core/')}
    spec['payload'] = str(LAYOUT / 'enclosure-assembly.step.mesh')
    spec['core_payload'] = str(HW / 'cold-core-layout/cold-core-assembly.step.mesh')
