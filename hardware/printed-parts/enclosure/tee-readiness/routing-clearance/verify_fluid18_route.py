#!/usr/bin/env python3
"""Check current fluid-18 against a retained native pack and placed route neighbors.

No geometry is exported. The check includes every current pack route, the seated
funnel drain, complete cap bearing length, all cap/wall/body anchor declarations,
and the refrigerant joint calculations downstream of those declarations.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'hardware/scripts').is_dir())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pack-cache', type=Path, required=True)
    parser.add_argument('--neighbor-cache', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=HERE / 'fluid18-current-pack.json')
    args = parser.parse_args()
    os.environ['HSM_NO_BUILD_LOCK'] = '1'
    sys.path[:0] = [str(ROOT / 'hardware/manifold-layout'), str(ROOT / 'hardware/scripts')]
    import cadquery as cq
    import numpy as np
    import _lines as lines
    import _routing as routing
    import _clearing as clearing
    import _scorecard as card
    import enclosure_assembly as assembly

    inputs = {}
    def tracked(path):
        inputs[str(path.resolve())] = sha(path)
        return path

    records = json.loads(tracked(args.pack_cache / 'frames.json').read_text())
    neighbors = json.loads(tracked(args.neighbor_cache / 'neighbors.json').read_text())
    foam_file = args.pack_cache / records['foam-assembly']['brep']
    if sha(foam_file) != neighbors['foam_brep_sha256']:
        raise ValueError('The electronics/funnel neighbors use a different native foam placement')
    solids = {n: cq.Shape.importBrep(str(tracked(args.pack_cache / r['brep'])))
              for n, r in records.items()}
    frames = {n: routing.frame(n, solids[n], r['ports'])
              for n, r in records.items() if 'ports' in r}
    for name, row in neighbors['placed'].items():
        path = tracked(args.neighbor_cache / row['brep'])
        if sha(path) != row['sha256']:
            raise ValueError('Native route neighbor changed: ' + name)
        solids[name] = cq.Shape.importBrep(str(path))

    # Recover the funnel and union frames from the exact placement functions' data.
    # The parent cache records the dimensions those functions actually consume.
    enc = assembly._enc
    inner, outer = neighbors['funnel_inner'], neighbors['funnel_outer']
    if tuple(inner[:2]) != tuple(enc.interior_x()):
        raise ValueError('Funnel cache no longer matches the stated enclosure width')
    if abs(outer[-1] - (enc.appliance_height - enc.floor_t)) > 1e-8:
        raise ValueError('Funnel cache no longer matches the stated roof height')
    centre = ((inner[0] + inner[1]) / 2,
              enc.funnel_front_y + assembly._funnel.collar_d / 2,
              enc.funnel_seat_z(outer))
    def yaw(angle):
        a = math.radians(angle)
        return np.array(((math.cos(a), -math.sin(a), 0),
                         (math.sin(a), math.cos(a), 0), (0, 0, 1)))
    turn = yaw(assembly.FUNNEL_ROT)
    def funnel_carry(station):
        return (tuple(turn @ station[0] + centre), tuple(turn @ station[1]))
    ports = {p: (*funnel_carry(row[0]()), row[1])
             for p, row in lines.STATIONS['funnel'].items()}
    frames['funnel'] = routing.frame('funnel', solids['funnel'], ports)
    drain = frames['funnel'].at('drain')
    union_turn = yaw(180.)
    union_shift = np.array(drain) - union_turn @ assembly._elbow.port('z')[0]
    def union_carry(station):
        return (tuple(union_turn @ station[0] + union_shift), tuple(union_turn @ station[1]))
    ports = {p: (*union_carry(row[0]()), row[1])
             for p, row in lines.STATIONS['funnel-drain-union'].items()}
    frames['funnel-drain-union'] = routing.frame('funnel-drain-union', solids['funnel-drain-union'], ports)

    source_paths = (Path(__file__), Path(lines.__file__), Path(routing.__file__),
                    Path(lines._cc.__file__), Path(assembly.__file__), Path(enc.__file__))
    sources = {str(p.relative_to(ROOT)): sha(p) for p in source_paths}
    original_frames = lines.frames
    try:
        lines.frames = lambda *_args: frames
        runs = lines.build_runs(solids, {}) + lines.build_seated_runs(solids, {})
    finally:
        lines.frames = original_frames
    run = next(r for r in runs if r.id == 'fluid-18')
    tube, wire = routing.tube(run), routing.centreline(run)
    if not tube.isValid() or len(tube.Solids()) != 1:
        raise ValueError('Fluid-18 does not produce one valid native solid')
    radius = run.diam / 2
    bounds = tube.BoundingBox()
    readings = []
    for name, shape in solids.items():
        if name in ('valve-v-g', 'bulkhead-flavor-a', 'stub-fluid-18'):
            continue  # The run's two intentional terminal bodies and its own mouth stub.
        if clearing.box_gap(bounds, shape.BoundingBox()) >= 5.:
            continue
        pieces = [s for s in shape.Solids()
                  if clearing.box_gap(bounds, s.BoundingBox()) < 5.]
        if not pieces:
            continue
        gap = min(tube.distance(s) for s in pieces)
        overlap = (sum(tube.intersect(s).Volume() for s in pieces)
                   if gap <= 1e-7 else 0.)
        required = 0. if name == 'foam-assembly' else card.CLEARANCE_FLOOR
        passed = gap >= required - 1e-6 and overlap <= 1e-5
        readings.append(dict(name=name, air_mm=gap, required_air_mm=required,
                             overlap_mm3=overlap, pass_=passed))
        print(('PASS ' if passed else 'FAIL ') + name + f': {gap:.6f} mm air', flush=True)

    pairs = []
    for other in runs:
        if other.id == run.id:
            continue
        # Each swept tube lies inside the ball envelope of its actual native
        # centreline. Subtracting both radii gives a conservative clearance bound.
        lower = wire.distance(routing.centreline(other)) - radius - other.diam / 2
        row = dict(name=other.id, native_centreline_lower_bound_mm=lower,
                   required_air_mm=card.CLEARANCE_FLOOR)
        if lower < 5.:
            other_tube = routing.tube(other)
            gap = tube.distance(other_tube)
            overlap = tube.intersect(other_tube).Volume() if gap <= 1e-7 else 0.
            row.update(air_mm=gap, overlap_mm3=overlap,
                       pass_=gap >= card.CLEARANCE_FLOOR - 1e-6 and overlap <= 1e-5)
        else:
            row['pass_'] = True
        pairs.append(row)
        print(('PASS ' if row['pass_'] else 'FAIL ') + 'tube ' + other.id +
              f': >= {lower:.6f} mm air', flush=True)

    # Reconstruct every available body transform from its declared positions and
    # directions. These are rigid transforms, never a fit to the native body size.
    carries, residuals = {}, {}
    for name, frame in frames.items():
        if name not in lines.STATIONS:
            continue
        local, world = [], []
        for port, row in lines.STATIONS[name].items():
            if port not in frame.ports:
                continue
            p, u = row[0](); q, v, _d = frame.ports[port]
            local.extend((p, np.asarray(p) + 10 * np.asarray(u)))
            world.extend((q, np.asarray(q) + 10 * np.asarray(v)))
        local, world = np.asarray(local), np.asarray(world)
        a, b = local.mean(axis=0), world.mean(axis=0)
        u, _s, vt = np.linalg.svd((local-a).T @ (world-b))
        rot = vt.T @ u.T
        if np.linalg.det(rot) < 0:
            vt[-1, :] *= -1; rot = vt.T @ u.T
        shift = b - rot @ a
        residual = float(np.max(np.linalg.norm(local @ rot.T + shift - world, axis=1)))
        if residual > 1e-6:
            raise ValueError(f'{name}: frame reconstruction residual {residual} mm')
        residuals[name] = residual
        carries[name] = lambda station, rot=rot, shift=shift: (
            tuple(rot @ station[0] + shift), tuple(rot @ station[1]))
    cap_rows = assembly.cap_tube_anchors(carries['foam-assembly'], runs)
    wall_rows = assembly.tube_anchors(runs)
    body_rows = assembly.body_anchors(carries)
    refrigerant = assembly.refrigerant_joints(carries, runs)
    declared = set(lines._cc.cap_anchors) | set(lines._cc.cap_side_anchors)
    expected_cap = sorted(declared & {r.id for r in runs})
    if len(cap_rows) != len(expected_cap):
        raise ValueError('Not every declared cap route anchor was exercised')
    cap_axis = carries['foam-assembly'](assembly.cap_side_anchor('fluid-18'))[0]
    half = lines._cc.cap_side_len / 2
    bearing_errors = [wire.distance(cq.Vertex.makeVertex(cap_axis[0] + x, *cap_axis[1:]))
                      for x in (-half, 0., half)]
    tangents = {i: run.radii[i] * math.tan(math.radians(turn) / 2)
                for i, turn, _li, _lo in run.bends}
    leads = (math.dist(run.pts[0], run.pts[1]) - tangents.get(1, 0.),
             math.dist(run.pts[-2], run.pts[-1]) - tangents.get(len(run.pts)-2, 0.))
    need = card.port_lead(run.bend, run.diam)
    passed = (all(r['pass_'] for r in readings + pairs)
              and run.tightest >= lines.TUBE_BEND - 1e-6
              and max(bearing_errors) <= 1e-6
              and min(leads) >= need - 1e-6 and not routing.BLOCKED)
    for path, digest in inputs.items():
        if sha(path) != digest:
            raise ValueError('Native input changed during verification: ' + path)
    for path, digest in sources.items():
        if sha(ROOT / path) != digest:
            raise ValueError('Source changed during verification: ' + path)
    report = dict(
        status='pass' if passed else 'fail', created_at_utc=datetime.now(timezone.utc).isoformat(),
        scope='Current fluid-18 native sweep, all retained/currently placed neighbors and all pack/seated tube routes. Full shell remains a separate build.',
        assembly_current=False, production_print_released=False,
        source_sha256=sources, input_sha256=inputs, waypoints_mm=run.pts,
        radii_mm=run.radii, minimum_radius_mm=run.tightest,
        developed_length_mm=run.length, straight_port_leads_mm=leads,
        required_port_lead_mm=need, blocked_runs=dict(routing.BLOCKED),
        native_neighbor_readings=readings, tube_pair_readings=pairs,
        cap_anchor_checks=dict(names=expected_cap, rows=cap_rows,
                              fluid18_axis_mm=cap_axis, bearing_length_mm=2*half,
                              native_centreline_error_at_bearing_ends_and_centre_mm=bearing_errors),
        wall_anchor_rows=wall_rows, body_anchor_rows=body_rows,
        refrigerant_joints=[r._asdict() for r in refrigerant],
        frame_reconstruction_max_residual_mm=max(residuals.values()))
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(('PASS' if passed else 'FAIL') + f': {len(readings)} native neighbors, {len(pairs)} tubes; '
          f'{len(cap_rows)} cap/{len(wall_rows)} wall/{len(body_rows)} body anchors; '
          f'R{run.tightest:g}; full {2*half:g} mm cap bearing', flush=True)
    if not passed:
        raise ValueError('Current fluid-18 failed native routing/anchor checks')


if __name__ == '__main__':
    main()
