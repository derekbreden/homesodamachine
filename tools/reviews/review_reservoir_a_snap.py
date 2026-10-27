"""Manually inspect the fore Reservoir A snap after its production exports.

    tools/cad-venv/bin/python tools/reviews/review_reservoir_a_snap.py

This is a task-scoped geometry reading, outside the build and commit paths.
The bent section is a cantilever kinematic proxy, not a material simulation.
"""
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT/'hardware/scripts'),
               str(ROOT/'hardware/manifold-layout'),
               str(ROOT/'hardware/printed-parts/cold-core')]
import cadquery as cq
import _reservoir_a_snap as snap
import _reservoir_a_anchors as anchors
import above_core as layout
import above_core_parts as parts
import above_core_routes as routes
import above_core_wiring as electrical
from _cadq_export import import_step
from hardware.wiring.installed.model import Connection, Route, STOCK, shape as wire_shape

HERE = ROOT/'hardware/printed-parts/cold-core/foam-cap'
OUT = HERE/'reservoir-a-snap-review'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bounds(body):
    b = body.BoundingBox()
    return [[b.xmin, b.ymin, b.zmin], [b.xmax, b.ymax, b.zmax]]


def describe(body):
    return dict(valid=body.isValid(), solids=len(body.Solids()),
                volume_mm3=body.Volume(), bounds_mm=bounds(body))


def bent_cap(delta):
    """Spread both integral wings using native cubic curves.

    The root-to-hook beam follows u²(3-u)/2; the deeper hook continues at its
    tip tangent. The unchanged Y extrusion preserves the cap's entire width.
    This reading asks if space exists for the movement, not what force or
    constitutive response produces it. Rigid edges retain their exact curves.
    """
    p, cap = snap.specification(), snap.cap()
    end = next(face for face in cap.Faces()
               if abs(face.Center().y+p['cap_length_mm']/2)<1.e-6
               and abs(face.normalAt().y)>.99)
    def shift(point):
        u = (p['spring_root_z_mm']-point.z)/p['spring_length_mm']
        f = u*u*(3-u)/2 if u<=1 else 1+1.5*(u-1)
        return cq.Vector(point.x+math.copysign(delta*f, point.x), point.y, point.z)

    def derivative(a, b, at):
        u = (p['spring_root_z_mm']-at.z)/p['spring_length_mm']
        slope = -delta*(3*u-1.5*u*u)/p['spring_length_mm']
        return cq.Vector(b.x-a.x+math.copysign(1., at.x)*slope*(b.z-a.z),
                         b.y-a.y, b.z-a.z)

    edges = []
    for edge in end.outerWire().Edges():
        a, b = edge.startPoint(), edge.endPoint()
        moving = (edge.geomType() == 'LINE'
                  and min(abs(a.x), abs(b.x))>p['hook_inner_x_mm']-.002
                  and min(a.z, b.z)<p['spring_root_z_mm']-1.e-7)
        if not moving:
            edges.append(edge)
            continue
        points = [a]
        lip = p['hook_top_z_mm']
        if min(a.z, b.z)<lip<max(a.z, b.z):
            f = (lip-a.z)/(b.z-a.z)
            points.append(a+(b-a)*f)
        points.append(b)
        for first, last in zip(points, points[1:]):
            if (first.z+last.z)/2<lip:
                edges.append(cq.Edge.makeLine(shift(first), shift(last)))
            else:
                q0, q3 = shift(first), shift(last)
                edges.append(cq.Edge.makeBezier([
                    q0, q0+derivative(first,last,first)/3,
                    q3-derivative(first,last,last)/3, q3]))
    return cq.Solid.extrudeLinear(cq.Wire.assembleEdges(edges), [],
                                  cq.Vector(0, p['cap_length_mm'], 0)).translate(snap.CENTRE)


def nearby(body):
    lo, hi = bounds(body)
    envelope = ((40., 69.), (202.5, 217.), (252., 276.))
    return all(hi[i]>=a and lo[i]<=b for i, (a, b) in enumerate(envelope))


def main():
    p, base, cap = snap.specification(), snap.base(), snap.installed_cap()
    spread = bent_cap(.6)
    # These are current native purchased references and the current authored
    # placement/tube routes. No cached draft BREP is a fixture input.
    fixtures = {name: row[0] for name, row in
                {**parts.components(), **electrical.components()}.items()
                if nearby(row[0])}
    for name, row in routes.reservoir_a_route_specs().items():
        if name in ('fluid-14', 'fluid-16'):
            fixtures[name] = parts.route_shape(row)
    native_lid = import_step(HERE/'foam-cap-lid-top.step').val()
    # Exact local native stock, with every crop plane outside the complete
    # moving cap envelope. Remote lid bosses cannot take part in this motion.
    local_window = cq.Solid.makeBox(31., 15., 23., cq.Vector(39., 202., 253.))
    fixtures['top-lid'] = native_lid.moved(
        layout.frame_location(layout.cap_lid_pose())).intersect(local_window)
    manifest = ROOT/'hardware/wiring/enclosure-wiring.json'
    for row in json.loads(manifest.read_text())['routes']:
        points = [s[k] for s in row['segments'] for k in ('start_mm', 'end_mm')]
        if not points:
            continue
        lo = [min(q[i] for q in points)-3 for i in range(3)]
        hi = [max(q[i] for q in points)+3 for i in range(3)]
        if any(hi[i]<a or lo[i]>b for i, (a, b) in
               enumerate(((40., 69.), (202.5, 217.), (252., 276.)))):
            continue
        connection = Connection(**{key: row[key] for key in
                                    ('id', 'harness', 'net', 'start', 'end', 'stock')})
        fixtures['wire-'+row['id']] = wire_shape(
            Route(connection, row['points_mm'], row['segments']), STOCK[row['stock']]['od_mm'])

    results = {}
    for name, other in fixtures.items():
        entry = dict(cap_seated_distance_mm=cap.distance(other),
                     cap_seated_overlap_mm3=cap.intersect(other).Volume())
        if name != 'top-lid':
            entry.update(base_distance_mm=base.distance(other),
                         base_overlap_mm3=base.intersect(other).Volume())
        # The lid includes the receiver: pass its ledges in the spread state.
        # For external neighbors also inspect the relaxed sweep as a broader
        # fixture envelope. Relaxed start and seated endpoints apply to both.
        moving = (spread,) if name == 'top-lid' else (cap, spread)
        entry['cap_motion_min_distance_mm'] = min(
            [body.translate((0, 0, p['insertion_lift_mm']*i/20)).distance(other)
             for body in moving for i in range(21)]
            + [cap.distance(other), cap.translate((0, 0, p['insertion_lift_mm'])).distance(other)])
        results[name] = entry
        print(name, entry, flush=True)

    # At this axial position the whole cap section clears the fixed cheeks;
    # each end retains its independent 0.25 mm running gap during spreading.
    motion = []
    for i in range(54):
        lift = p['insertion_lift_mm']*i/53
        overlap = base.intersect(spread.translate((0, 0, lift))).Volume()
        motion.append(dict(lift_mm=lift, spread_at_hook_mm=.6, overlap_mm3=overlap))
    axial = [dict(offset_y_mm=y, overlap_mm3=base.intersect(cap.translate((0, y, 0))).Volume())
             for y in (-.35, -.25, 0., .25, .35)]
    sources = [Path(__file__), Path(snap.__file__), Path(anchors.__file__), HERE/'foam_cap.py',
               ROOT/'hardware/manifold-layout/above-core.json',
               ROOT/'hardware/reference/ground-ring-stack/ground_ring_stack.py',
               ROOT/'hardware/wiring/installed/route-overrides.json']
    artifacts = [HERE/'foam-cap-lid-top.step', HERE/'foam-cap-lid-top.stl',
                 HERE/(snap.CAP_NAME+'.step'), HERE/(snap.CAP_NAME+'.stl'), manifest,
                 ROOT/'hardware/manifold-layout/enclosure-assembly.step',
                 ROOT/'hardware/cold-core-layout/cold-core-assembly.step']
    report = dict(
        units='mm', frame='appliance XYZ', specification=p,
        source_sha256={str(path.relative_to(ROOT)): sha(path) for path in sources},
        artifact_sha256={str(path.relative_to(ROOT)): sha(path) for path in artifacts},
        receiver=describe(base), cap=describe(cap), bent_proxy=describe(spread),
        exported_lid=describe(native_lid),
        seated_receiver_cap_overlap_mm3=base.intersect(cap).Volume(),
        fixtures=results, axial_capture=axial,
        insertion_proxy=dict(scope='Native cap section; exact cubic outward '
                             'cantilever displacement, rigid hook continuation; '
                             '6 mm full-width extrusion. A space/motion proxy, not FEA.',
                             stations=motion, overlap_tolerance_mm3=.002),
        nominal_beam_strain_estimate=dict(
            formula='1.5*t*delta/L^2', thickness_mm=p['spring_thickness_mm'],
            length_mm=p['spring_length_mm'], hook_overlap_mm=.45,
            nominal_percent=100*1.5*p['spring_thickness_mm']*.45/p['spring_length_mm']**2,
            with_extra_015_mm_percent=100*1.5*p['spring_thickness_mm']*.6/p['spring_length_mm']**2),
        scope='Current digital geometry and offline print preparation. Physical snap fit, '
              'tube restraint, forces, creep, fatigue and load capacity are not qualified.')
    OUT.mkdir(exist_ok=True)
    (OUT/'native-review.json').write_text(json.dumps(report, indent=2)+'\n')
    failures = [name for name, row in results.items()
                if row['cap_seated_overlap_mm3']>.002
                or row.get('base_overlap_mm3', 0)>.002
                or row['cap_motion_min_distance_mm']<.01]
    failures += ['receiver motion'] if any(row['overlap_mm3']>.002 for row in motion) else []
    failures += ['axial capture'] if not (axial[0]['overlap_mm3']>0
                                          and axial[-1]['overlap_mm3']>0) else []
    print('Native review:', 'PASS' if not failures else failures)
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())
