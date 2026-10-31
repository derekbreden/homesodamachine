"""The lines off the rear-port rebuild: the pump, its two joints and what they run to, and the
flavour side of the union tee. Builds on study.py's outputs, study.json and rear-port-rebuild.step,
and writes hardware/assembly/scenes/out/rear-port-lines.step with the page spec beside it,
rear-port-lines.page.json, for tools/viz/build.py.

- The pump stands forward of the study's pump until its suction barb's axis lies in the plane the
  flipped elbow's socket turns in. The flipped elbow's stem, cut to the socket's depth, stands in the
  socket of the elbow in V-K's bottom port, and its own socket faces back up to the suction reducer.
- The suction joint's 3/8" tube bends down in one arc, as short as reaches, so a 1/4" stub with no
  length showing runs straight from the reducer's collet into the flipped elbow's socket.
- The discharge joint runs straight. A stem elbow stands in its reducer's collet and an ACVUS-44 stem
  check in the elbow's socket. water-5 leaves the check's socket and bends down at BEND_R, the tightest
  bend 1/4" LLDPE takes, onto a plumb drop that starts at the cold-core cap lid's top face and runs
  down until it lands on the first part under it. The elbow turns down from aft as far as that bend
  allows.
- Off the union tee's free run, west: fluid-1, then the YZMSZ flow regulator, straight on.
- The Mean Well IRM-90 stands on the west wall where production stands it, raised until it stands
  CLEAR over the discharge's parts under it.
- The two Teyleten relays hang from the ceiling, their backs PAD under it, CLEAR east of the PSU, in
  the order and along the run production stands them on the west wall.
Each 1/4" tube between two parts shows SPAN, as the split's stub does."""
import json
import math
import struct
import sys
from pathlib import Path

import numpy as np
from OCP.gp import gp_Trsf
from scipy.optimize import brentq, fsolve

HERE = Path(__file__).resolve().parent
HW = HERE.parents[2]
for p in ('scripts', 'manifold-layout', 'printed-parts/cadlib', 'reference/jg-pp061208w', 'reference/jg-pp0208e-tee',
          'reference/asse1022-threaded-chain', 'reference/neofit-stem-elbow', 'reference/pump-barb-joint',
          'reference/neofit-acvus44-check'):
    sys.path.insert(0, str(HW / p))
import cadquery as cq  # noqa: E402
import above_core as layout  # noqa: E402
import above_core_parts as acp  # noqa: E402
import asse1022_threaded_chain as tc  # noqa: E402
import jg_pp0208e_tee as union_tee  # noqa: E402
import jg_pp061208w as reducer_ref  # noqa: E402
import neofit_acvus44_check as acvus  # noqa: E402
import neofit_stem_elbow as stem_elbow  # noqa: E402
import pump_barb_joint as pj  # noqa: E402
from _cadq_export import export_assembly  # noqa: E402
from _materials import M_NEOFIT_ACETAL, M_NEOFIT_WHITE_ACETAL  # noqa: E402
from _routing import stock_min  # noqa: E402

OUT = HW / 'assembly' / 'scenes' / 'out'
study = json.load(open(HERE / 'study.json'))
facts = json.load(open(HW / 'manifold-layout' / 'enclosure-assembly.facts.json'))
CAP_Z = facts['faces']['foam-assembly.cap']
X_W, ROW_0 = 37.25, 328.0                       # study.py's west column and top row, where the ASSE chain stands
SPAN = study['water_split']['stub_mm']
TUBE_OD, TUBE_ID = 6.35, 4.32
BEND_R = stock_min('water', TUBE_OD)
CLEAR = 1.0                                     # study.py's PUMP_CLEAR
CEILING, PAD = 346.0, 2.0                       # study.py's roof inner face; the pads a relay bears on
REGULATOR_LENGTH = 68.117                       # the YZMSZ's inlet-to-outlet release faces
Z = np.array([0., 0., 1.])
SUPERSEDED = ('g-ganen-pump', 'suction-', 'discharge-')     # the study's pump and joints, which this file draws again
vk_mouth = np.array(study['vk_line']['lower-valve-elbow']['socket_mouth'])
up_y = np.array(study['vk_line']['lower-valve-elbow']['socket_axis'], float)
crossing = vk_mouth + up_y * stem_elbow.HUB_BACK_REACH          # the flipped elbow's, its shoulder on V-K's elbow
MOUTH = pj.reducer.LENGTH - pj.CUT_X


def frame(origin, cols):
    return layout.frame_location({'rotation': [[c[i] for c in cols] for i in range(3)],
                                  'translation_mm': [float(c) for c in origin]})


def tube_run(start, way, length):
    return (cq.Solid.makeCylinder(TUBE_OD / 2., length, cq.Vector(*start), cq.Vector(*way))
            .cut(cq.Solid.makeCylinder(TUBE_ID / 2., length, cq.Vector(*start), cq.Vector(*way))))


def square(v, to):
    v = v - to * float(v @ to)
    return v / np.linalg.norm(v)


def payload(step):
    """`{name: (positions (n, 3), triangles (m, 3))}` from the mesh payload the export wrote beside `step`."""
    data = Path(str(step) + '.mesh').read_bytes()
    n = struct.unpack('<I', data[:4])[0]
    head, blob = json.loads(data[4:4 + n]), data[4 + n:]
    return {m['name']: (np.frombuffer(blob, '<f4', m['pos'][1], m['pos'][0]).reshape(-1, 3).astype(float),
                        np.frombuffer(blob, '<u4', m['idx'][1], m['idx'][0]).reshape(-1, 3))
            for m in head['meshes'] if m.get('name')}


# --- the pump and its suction joint ---------------------------------------------------------------
comps = acp.components()
pump_body, pump_colour, carry = comps['g-ganen-pump']
WEST, AFT = study['g-ganen-pump']['west_mm'], study['g-ganen-pump']['aft_mm']
frames = {}
for port in pj.PORTS:
    tip, axis = (np.array(v, float) for v in carry(pj.pump.port(pj.PORTS[port])))
    tip += np.array([-WEST, AFT, 0.])
    lift = square(Z, axis)
    side = np.cross(lift, axis)
    frames[port] = (tip, np.column_stack([axis, side, lift]), 1 if side[1] > 0 else -1)


def arc(free, th, psi, t=1.0):
    """Joint frame: the point and direction `t` of the way along the free tube, bent `th` radians over
    `free` mm toward down, leaned `psi` radians fore (-Y)."""
    n = np.array([0., -math.sin(psi), -math.cos(psi)])
    a, r = th * t, free / th
    return r * math.sin(a) * np.array([1., 0., 0.]) + r * (1. - math.cos(a)) * n, \
        math.cos(a) * np.array([1., 0., 0.]) + math.sin(a) * n


tip0, rot, keys = frames['suction']


def chain(v):
    fwd, free, th, psi = v
    end, d = arc(free, th, psi)
    return tip0 - np.array([0., fwd, 0.]) + rot @ (end + d * MOUTH), rot @ d


def miss(v):
    mouth, d_w = chain(v)
    return [*(mouth + d_w * stem_elbow.SOCKET_MOUTH_REACH - crossing), float(d_w @ up_y)]


forward, free, th, psi = fsolve(miss, [11.9, 16.7, 0.48, 0.])
mouth, d_w = chain((forward, free, th, psi))
shift = np.array([-WEST, AFT - forward, 0.])
tip = tip0 - np.array([0., forward, 0.])
at = layout.frame_location({'rotation': rot.tolist(), 'translation_mm': [float(c) for c in tip]})
end, _ = arc(free, th, psi)
mid, _ = arc(free, th, psi, 0.5)
n = np.array([0., -math.sin(psi), -math.cos(psi)])
move = cq.Location(cq.Vector(*end)) * cq.Location(cq.Vector(), cq.Vector(*np.cross([1., 0., 0.], n)), math.degrees(th))
rows = pj.bore('suction')
on_barb, stem_r = rows[:-2], rows[-1][1]
path = cq.Wire.assembleEdges([cq.Edge.makeThreePointArc(cq.Vector(0, 0, 0), cq.Vector(*mid), cq.Vector(*end))])
span = cq.Workplane('YZ').circle(pj.TUBE_OD / 2.).circle(pj.TUBE_ID / 2.).sweep(path).val()
suction = {'tube': (pj.turned(on_barb).fuse(span, pj.turned([(0., stem_r), (pj.TRIM, stem_r)]).moved(move)).clean(),
                    pj.M_PVC_CLEAR),
           'reducer': (pj.build_reducer().moved(move), pj.M_JG_WHITE_PP)}
for name, (xc, d) in pj.bands('suction').items():
    steel, key = pj.build_clamp(d, xc, keys)
    if name == 'stem':
        steel, key = steel.moved(move), key.moved(move)
    suction[f'{name}-clamp'] = (steel, pj.M_STAINLESS)
    suction[f'{name}-key'] = (key, pj.M_POM_ORANGE)
parts = {'g-ganen-pump': (pump_body.moved(cq.Location(cq.Vector(*shift))), pump_colour)}
parts.update({f'suction-{n}': (s.moved(at), c) for n, (s, c) in suction.items()})
parts['suction-stub'] = (tube_run(mouth - d_w * reducer_ref.TUBE_INSERTION_DEPTH, d_w,
                                  reducer_ref.TUBE_INSERTION_DEPTH + stem_elbow.SOCKET_INSERTION), pj.M_PVC_CLEAR)
parts['suction-elbow'] = (acp.stem_elbow(stem_elbow.SOCKET_INSERTION).moved(
    frame(crossing, (up_y, -d_w, np.cross(up_y, -d_w)))), M_NEOFIT_WHITE_ACETAL)

# --- the discharge joint, its stem elbow and stem check, and water-5 into the cold core ---------------
tip_d, rot_d, keys_d = frames['discharge']
tip_d = tip_d - np.array([0., forward, 0.])
at_d = layout.frame_location({'rotation': rot_d.tolist(), 'translation_mm': [float(c) for c in tip_d]})
for n, (s, c) in pj.build('discharge', (keys_d,) * 2).items():
    parts[f'discharge-{n}'] = (s.moved(at_d), c)
p, o = (np.array(v, float) for v in pj.mouth('discharge'))
d_mouth, out = tip_d + rot_d @ p, rot_d @ o
aft = square(np.array([0., 1., 0.]), out)
over = square(square(Z, out), aft)              # up, square to the elbow's stem and to aft
d_crossing = d_mouth + out * stem_elbow.HUB_BACK_REACH
REACH = stem_elbow.SOCKET_MOUTH_REACH - acvus.SHOULDER + acvus.LENGTH     # the elbow's crossing to the check's port


def socket_way(tilt):
    """The elbow's socket, turned `tilt` radians down from aft about its stem."""
    return math.cos(tilt) * aft - math.sin(tilt) * over


def bend_foot(tilt):
    """The height at which water-5 runs plumb, the elbow turned `tilt` down: off the check's port the
    tube turns down at BEND_R."""
    way = socket_way(tilt)
    return (d_crossing + way * REACH)[2] - BEND_R * math.sqrt(1. - float(way @ Z) ** 2)


TILT = brentq(lambda t: bend_foot(t) - CAP_Z, 0., math.pi / 3.)
way = socket_way(TILT)
parts['discharge-elbow'] = (acp.stem_elbow(reducer_ref.TUBE_INSERTION_DEPTH).moved(
    frame(d_crossing, (out, way, np.cross(out, way)))), M_NEOFIT_WHITE_ACETAL)
stem_tip = d_crossing + way * (stem_elbow.SOCKET_MOUTH_REACH - acvus.SHOULDER)
up = square(Z, way)
parts['discharge-check'] = (acvus.build().moved(frame(stem_tip, (way, np.cross(up, way), up))), M_NEOFIT_WHITE_ACETAL)
port_at = stem_tip + way * acvus.LENGTH
level = square(way, Z)
dip = math.asin(-float(way @ Z))


def on_bend(a):
    """The point on water-5's bend where the tube runs `a` radians below level."""
    return port_at + BEND_R * ((math.sin(a) - math.sin(dip)) * level + (math.cos(a) - math.cos(dip)) * Z)


foot = on_bend(math.pi / 2.)
drop_xy, drop_top = foot[:2], foot[2]

# Where the drop lands: the highest face under the tube's end, over its whole section, of every part
# drawn under the bend but the foam caps, which the drop passes through.
rebuild = payload(OUT / 'rear-port-rebuild.step')
enclosure = payload(HW / 'manifold-layout' / 'enclosure-assembly.step')
core = {name: mesh for name, mesh in enclosure.items() if name.startswith('cold-core/')
        and mesh[0][:, 2].min() < CAP_Z and not name.startswith(('cold-core/g-ganen-pump', 'cold-core/pump-',
                                                                 'cold-core/discharge-chain', 'cold-core/tube-water-5'))}
under = {name: mesh for name, mesh in {**core, **{n: m for n, m in rebuild.items() if not n.startswith(SUPERSEDED)}}.items()
         if 'foam-cap' not in name}
ring = np.linspace(0., 2. * math.pi, 12, endpoint=False)
samples = drop_xy + np.concatenate([[[0., 0.]], *(r * np.column_stack([np.cos(ring), np.sin(ring)])
                                                   for r in (TUBE_OD / 4., TUBE_OD / 2.))])
land_z, land_on = -math.inf, None
for name, (pos, tri) in under.items():
    a, b, c = (pos[tri[:, k]] for k in range(3))
    lo, hi = np.minimum(np.minimum(a, b), c), np.maximum(np.maximum(a, b), c)
    for x, y in samples:
        m = (lo[:, 0] <= x) & (hi[:, 0] >= x) & (lo[:, 1] <= y) & (hi[:, 1] >= y) & (lo[:, 2] < drop_top)
        if not m.any():
            continue
        aa, v0, v1 = a[m], c[m] - a[m], b[m] - a[m]
        v2 = np.array([x, y]) - aa[:, :2]
        d00, d01, d11 = (v0[:, :2] * v0[:, :2]).sum(1), (v0[:, :2] * v1[:, :2]).sum(1), (v1[:, :2] * v1[:, :2]).sum(1)
        d20, d21 = (v2 * v0[:, :2]).sum(1), (v2 * v1[:, :2]).sum(1)
        den = d00 * d11 - d01 ** 2
        ok = np.abs(den) > 1e-12
        s = np.where(ok, (d11 * d20 - d01 * d21) / np.where(ok, den, 1.), -1.)
        t = np.where(ok, (d00 * d21 - d01 * d20) / np.where(ok, den, 1.), -1.)
        z = aa[:, 2] + s * v0[:, 2] + t * v1[:, 2]
        z = z[ok & (s >= -1e-9) & (t >= -1e-9) & (s + t <= 1. + 1e-9) & (z < drop_top)]
        if len(z) and z.max() > land_z:
            land_z, land_on = float(z.max()), name
drop = drop_top - land_z
bend = cq.Wire.assembleEdges([cq.Edge.makeThreePointArc(
    cq.Vector(*port_at), cq.Vector(*on_bend((dip + math.pi / 2.) / 2.)), cq.Vector(*foot))])
water_5 = cq.Workplane(cq.Plane(origin=tuple(port_at), xDir=tuple(up), normal=tuple(way))).circle(TUBE_OD / 2.) \
    .circle(TUBE_ID / 2.).sweep(cq.Workplane().add(bend)).val()
parts['water-5'] = (tube_run(port_at - way * acvus.INSERTION, way, acvus.INSERTION)
                    .fuse(water_5, tube_run(foot, -Z, drop)).clean(), pj.M_PVC_CLEAR)

# --- the PSU on the west wall, over the discharge, and the relays on the ceiling ----------------------
psu, psu_colour, _ = comps['psu']
box = psu.BoundingBox()
column = cq.Solid.makeBox(box.xlen, box.ylen, 2. * CEILING, cq.Vector(box.xmin, box.ymin, 0.))
under_psu = max(s.intersect(column).BoundingBox().zmax for n, (s, _) in parts.items()
                if n.startswith(('discharge-', 'water-5')) and s.intersect(column).Volume() > 0.)
psu_lift = under_psu + CLEAR - box.zmin
parts['psu'] = (psu.moved(cq.Location(cq.Vector(0., 0., psu_lift))), psu_colour)
backs_up = cq.Location(cq.Vector(), cq.Vector(0., 1., 0.), 90.)       # the face that bears on the wall, to the ceiling
relays = {n: comps[n][0].moved(backs_up) for n in ('relay-1', 'relay-2')}
west_edge = min(s.BoundingBox().xmin for s in relays.values())
top = max(s.BoundingBox().zmax for s in relays.values())
to_ceiling = cq.Location(cq.Vector(box.xmax + CLEAR - west_edge, 0., CEILING - PAD - top))
for n, s in relays.items():
    parts[n] = (s.moved(to_ceiling), comps[n][1])

# --- off the union tee's free run, fluid-1 and the flow regulator -----------------------------------
t = gp_Trsf()
t.SetValues(0, 0, 1, X_W - tc.bfp.BODY_CENTER_Z, -1, 0, 0,
            facts['card_ports']['bulkhead-water']['outboard']['pos'][1] + tc.ports()['inlet'][0][0], 0, -1, 0, ROW_0)
TO_WORLD = cq.Location(t)
red = tc.parameters()['pp061208w']


def chain_point(x):
    return np.array(tc.placed(cq.Vertex.makeVertex(x, 0., 0.), red).moved(TO_WORLD).Center().toTuple())


nose = chain_point(red['visible_axial_range_mm'][1])
flow = chain_point(red['visible_axial_range_mm'][1] + 1.) - nose
west = -square(np.array([1., 0., 0.]), flow)
free_mouth = nose + flow * (SPAN + union_tee.REACH) + west * union_tee.REACH
parts['fluid-1'] = (tube_run(free_mouth - west * union_tee.INSERTION, west, union_tee.INSERTION + SPAN + 15.),
                    pj.M_PVC_CLEAR)
reg_in = free_mouth + west * SPAN
up_w = square(Z, west)
parts['flow-regulator'] = (acp.native_reference('flow-regulator').moved(frame(reg_in, (west, np.cross(up_w, west), up_w))),
                           M_NEOFIT_ACETAL)

a = cq.Assembly(name='rear-port-lines')
for name, (s, c) in parts.items():
    a.add(s, name=name, color=c)
out_step = OUT / 'rear-port-lines.step'
export_assembly(a, str(out_step))

# --- the page: the rebuild without the study's pump and joints, these lines, and the cold core -------
land = [*drop_xy, land_z]
lit = 'foam-' not in land_on                    # a see-through part stays see-through
check_mid = (stem_tip + port_at) / 2.
psu_box, relay_box = parts['psu'][0].BoundingBox(), cq.Compound.makeCompound(
    [parts[n][0] for n in relays]).BoundingBox()
spec = {
    'title': 'Pump to V-K',
    'lede': (f"The pump stands {forward:.1f} mm forward of the study's pump. Its 3/8 in suction tube runs {free:.1f} mm and "
             f"bends {math.degrees(th):.1f}° down at R{free / th:.0f}, and a 1/4 in stub runs straight from the reducer's "
             f"collet into the flipped elbow in V-K's bottom-port elbow. On the discharge, the stem elbow turns "
             f"{math.degrees(TILT):.1f}° down from aft, as far as water-5's R{BEND_R:g} bend lets it: off the ACVUS-44 stem "
             f"check's port, {port_at[2] - CAP_Z:.1f} mm over the cap lid, the tube turns {90. - math.degrees(dip):.1f}° and "
             f"runs plumb from the lid's top face, {drop:.1f} mm down to {land_on.split('/')[-1]}. The Mean Well stands "
             f"{psu_lift:.1f} mm higher on the west wall than production stands it, {CLEAR:g} mm over the elbow and check, and "
             f"the two relays hang from the ceiling beside it. Off the union tee's free run, fluid-1 and the YZMSZ flow "
             f"regulator run straight west. Amber: the elbow, the check, water-5, the Mean Well and the relays"
             f"{', and the part water-5 lands on' if lit else ''}. The foam, the CO2 tube and the enclosure's back are "
             f"see-through, and clashes are drawn as they stand."),
    'columns': 1,
    'view': {'az': 240, 'el': 15},
    'panels': [{
        'name': 'The check turned down, the Mean Well over it, the relays on the ceiling',
        'view': {'az': 240, 'el': 15},
        'focus': {'center': [-55., 390., 295.], 'radius': 95.},
        'models': [
            {'step': 'hardware/assembly/scenes/out/rear-port-rebuild.step',
             'only': sorted(n for n in rebuild if not n.startswith(SUPERSEDED)),
             'ghost': ['enclosure-back-top', 'face-rail-*', 'tile-*', 'co2-tube']},
            {'step': 'hardware/assembly/scenes/out/rear-port-lines.step',
             'highlight': ['discharge-elbow*', 'discharge-check*', 'water-5*', 'psu*', 'relay-*']},
            {'step': 'hardware/manifold-layout/enclosure-assembly.step',
             'only': sorted(n for n in enclosure if n == 'enclosure-back-top'
                            or n.startswith('cold-core/') and (n in core or 'foam-' in n)),
             'ghost': ['cold-core/foam-*', 'enclosure-back-top']}],
        'marks': [
            {'at': check_mid.tolist(), 'text': f"check {math.degrees(TILT):.1f}° down, R{BEND_R:g} into the lid",
             'dx': -50, 'dy': 70},
            {'at': [psu_box.xmin, psu_box.center.y, psu_box.center.z], 'text': 'Mean Well on the west wall',
             'dx': -60, 'dy': -50},
            {'at': [relay_box.center.x, relay_box.center.y, relay_box.zmin], 'text': 'relays on the ceiling',
             'dx': 40, 'dy': -70},
            {'at': land, 'text': f"lands on {land_on.split('/')[-1]}, z {land_z:.1f}", 'dx': 40, 'dy': 60}]}]}
if lit:
    spec['panels'][0]['models'][0 if land_on in rebuild else 2]['highlight'] = [land_on]
json.dump(spec, open(OUT / 'rear-port-lines.page.json', 'w'), indent=1)
print(f'pump {forward:.2f} mm forward (aft {shift[1]:.2f}); 3/8 tube free {free:.2f} mm, bent {math.degrees(th):.2f} deg '
      f'(R{free / th:.1f}), leaned {math.degrees(psi):.2f} deg; collet mouth {np.round(mouth, 2).tolist()}')
print(f'discharge collet {np.round(d_mouth, 2).tolist()}; elbow {math.degrees(TILT):.2f} deg down; check port '
      f'{np.round(port_at, 2).tolist()}, bend {90. - math.degrees(dip):.2f} deg at R{BEND_R:g}; drop at '
      f'{np.round(drop_xy, 2).tolist()} from z {drop_top:.2f}, {drop:.2f} mm down onto {land_on} at z {land_z:.2f} '
      f'({CAP_Z - land_z:.2f} under the cap face)')
print(f'psu up {psu_lift:.2f} mm: {np.round([psu_box.xmin, psu_box.ymin, psu_box.zmin], 2).tolist()} to '
      f'{np.round([psu_box.xmax, psu_box.ymax, psu_box.zmax], 2).tolist()}; relays '
      f'{np.round([relay_box.xmin, relay_box.ymin, relay_box.zmin], 2).tolist()} to '
      f'{np.round([relay_box.xmax, relay_box.ymax, relay_box.zmax], 2).tolist()}')
print('->', out_step, OUT / 'rear-port-lines.page.json')
