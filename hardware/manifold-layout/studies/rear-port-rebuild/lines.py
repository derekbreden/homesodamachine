"""The lines off the rear-port rebuild: the union tee and everything on it, raised on one bend in the
split's stub; the pump, its two joints and what they run to; and the boards on the walls and the
ceiling. Builds on study.py's outputs, study.json and rear-port-rebuild.step, and writes
hardware/assembly/scenes/out/rear-port-lines.step with the page spec beside it,
rear-port-lines.page.json, for tools/viz/build.py.

- The union tee and V-K's group as study.py stands them: V-K on tee-fold, V-K's wall with its arm to
  the east wall, and the elbow in V-K's outlet, its socket aft. Off the tee's free run, west: fluid-1,
  then the YZMSZ flow regulator, straight on.
- Off the regulator, production's link and elbow and V-A on them, with V-A's wall: production's
  regulator, link, elbow, V-A and wall move together by the one rigid move M that stands
  production's regulator on this one.
- The split's stub bends once, up, in one arc over the SPAN it shows, and the tee turns with the
  arc's end. The tee and everything on it move as one, as far as stands their top CLEAR under the
  ceiling. V-A's wall root reaches down to the cap lid's top face.
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
- The C14 stands where production stands it.
- The two Teyleten relays stand on the west wall where production stands them. The holes at each
  end of both boards make one line, and one bar from the wall runs under all four.
- The Mean Well IRM-90 hangs from the ceiling on four bosses, its base up and PSU_STAND under the
  ceiling, as production stands it off the wall. Its AC end stands CLEAR fore of the C14 and its
  west face CLEAR east of the relays.
- Every boss and bar is production's section: Ø mount_boss_dia, a heat-set bore on each hole.
Each 1/4" tube between two parts shows SPAN, as the split's stub does."""
import fnmatch
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
          'reference/neofit-acvus44-check', 'reference/meanwell-irm90', 'reference/teyleten-relay',
          'cold-core-layout', 'printed-parts/cold-core', 'printed-parts/cold-core/foam-assembly',
          'printed-parts/enclosure/enclosure'):
    sys.path.insert(0, str(HW / p))
import cadquery as cq  # noqa: E402
import above_core as layout  # noqa: E402
import above_core_parts as acp  # noqa: E402
import asse1022_threaded_chain as tc  # noqa: E402
import jg_pp0208e_tee as union_tee  # noqa: E402
import jg_pp061208w as reducer_ref  # noqa: E402
import meanwell_irm90 as irm90  # noqa: E402
import neofit_acvus44_check as acvus  # noqa: E402
import neofit_stem_elbow as stem_elbow  # noqa: E402
import pump_barb_joint as pj  # noqa: E402
import teyleten_relay as teyleten  # noqa: E402
import _above_core_mounts as mounts  # noqa: E402
import _enclosure_interface as interface  # noqa: E402
import valve_seat  # noqa: E402
from _cadq_export import export_assembly  # noqa: E402
from _materials import M_JG_BLACK_PP, M_NEOFIT_WHITE_ACETAL, M_PETGF_BLACK  # noqa: E402
from _routing import SPOOLS, stock_min  # noqa: E402

OUT = HW / 'assembly' / 'scenes' / 'out'
study = json.load(open(HERE / 'study.json'))
facts = json.load(open(HW / 'manifold-layout' / 'enclosure-assembly.facts.json'))
CAP_Z = facts['faces']['foam-assembly.cap']
X_W, ROW_0 = 37.25, 328.0                       # study.py's west column and top row, where the ASSE chain stands
SPAN = study['water_split']['stub_mm']
TUBE_OD, TUBE_ID = 6.35, 4.32
BEND_R = stock_min('water', TUBE_OD)
CLEAR = 1.0                                     # study.py's PUMP_CLEAR
CEILING = 346.0                                 # study.py's roof inner face
REGULATOR_LENGTH = 68.117                       # the YZMSZ's inlet-to-outlet release faces
EAST_WALL_X = 98.5                              # study.py's SIDE_WALL_X: the east wall's inner face
WEST_WALL_X = -EAST_WALL_X                      # the west wall's, across the machine
R_BOSS, R_BORE = interface.mount_boss_dia / 2., interface.heatset_dia / 2.
CORE = ('cold-core/carbonator-tube*', 'cold-core/endcap-top*', 'cold-core/endcap-bottom*', 'cold-core/evap-coil*',
        'cold-core/reservoir-a', 'cold-core/reservoir-a-cap*', 'cold-core/reservoir-b', 'cold-core/reservoir-b-cap*',
        'cold-core/foam-shell*', 'cold-core/foam-cap-top*', 'cold-core/foam-cap-lid-top*')     # the cold core drawn under it all
Z = np.array([0., 0., 1.])
GROUP = ('jg-pp0208e', 'tee-fold', 'vk-solenoid', 'vk-wall', 'lower-valve-elbow', 'fluid-1', 'flow-regulator',
         'reg-va-link', 'reg-va-elbow', 'valve-v-a', 'va-wall')          # the union tee and everything on it
SUPERSEDED = ('g-ganen-pump', 'suction-', 'discharge-', 'jg-pp0208e', 'tee-fold', 'vk-', 'lower-valve-elbow',
              'water-split-stub')       # the study's pump, joints, tee and V-K group, which this file draws again
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


def block(lo, hi):
    return cq.Solid.makeBox(*(hi[i] - lo[i] for i in range(3)), cq.Vector(*lo))


def overlap(s, o):
    a, b = s.BoundingBox(), o.BoundingBox()
    if a.xmin > b.xmax or b.xmin > a.xmax or a.ymin > b.ymax or b.ymin > a.ymax or a.zmin > b.zmax or b.zmin > a.zmax:
        return 0.
    return s.intersect(o).Volume()


def payload(step):
    """`{name: (positions (n, 3), triangles (m, 3))}` from the mesh payload the export wrote beside `step`."""
    data = Path(str(step) + '.mesh').read_bytes()
    n = struct.unpack('<I', data[:4])[0]
    head, blob = json.loads(data[4:4 + n]), data[4 + n:]
    return {m['name']: (np.frombuffer(blob, '<f4', m['pos'][1], m['pos'][0]).reshape(-1, 3).astype(float),
                        np.frombuffer(blob, '<u4', m['idx'][1], m['idx'][0]).reshape(-1, 3))
            for m in head['meshes'] if m.get('name')}


comps = acp.components()
parts = {}

# --- the union tee and V-K's group, as study.py stands them -------------------------------------------
t = gp_Trsf()
t.SetValues(0, 0, 1, X_W - tc.bfp.BODY_CENTER_Z, -1, 0, 0,
            facts['card_ports']['bulkhead-water']['outboard']['pos'][1] + tc.ports()['inlet'][0][0], 0, -1, 0, ROW_0)
TO_WORLD = cq.Location(t)
red = tc.parameters()['pp061208w']


def chain_point(x):
    return np.array(tc.placed(cq.Vertex.makeVertex(x, 0., 0.), red).moved(TO_WORLD).Center().toTuple())


nose = chain_point(red['visible_axial_range_mm'][1])              # the reducer's 1/4" collet face
flow = chain_point(red['visible_axial_range_mm'][1] + 1.) - nose
east = square(np.array([1., 0., 0.]), flow)
west = -east
tee_at = nose + flow * (SPAN + union_tee.REACH)
SHIFT = tee_at + east * union_tee.REACH - np.array(comps['tee-fold'][2](stem_elbow.socket())[0], float)
MOVE = cq.Location(cq.Vector(*SHIFT))
for n in ('vk-solenoid', 'tee-fold'):
    parts[n] = (comps[n][0].moved(MOVE), comps[n][1])
seat = mounts.valve_support_datums('vk-solenoid')
lo, hi = seat['bearing_min_world_mm'], seat['bearing_max_world_mm']
at_vk = layout.location('vk-solenoid')
vk_wall = block(lo, hi).cut(valve_seat.build_sockets().val().moved(at_vk),
                            valve_seat.build_port_channel(2. * valve_seat.seat_half_y + 2.).val().moved(at_vk))
parts['vk-wall'] = (vk_wall.moved(MOVE).fuse(block((hi[0] + SHIFT[0], lo[1] + SHIFT[1], lo[2] + SHIFT[2]),
                                                   (EAST_WALL_X, hi[1] + SHIFT[1], hi[2] + SHIFT[2]))).clean(),
                    M_PETGF_BLACK)
parts['jg-pp0208e'] = (union_tee.build_jg_pp0208e_tee().val().moved(frame(tee_at, (np.cross(-flow, east), -flow, east))),
                       M_JG_BLACK_PP)
outlet_at, outlet_axis = (np.array(v, float) for v in
                          comps['vk-solenoid'][2](acp.port_stations('vk-solenoid')['outlet'][:2]))
outlet_at += SHIFT
socket_was = square(np.array(comps['lower-valve-elbow'][2](stem_elbow.socket())[1], float), outlet_axis)
socket_to = square(np.array([0., 1., 0.]), outlet_axis)
outlet_turn = math.degrees(math.atan2(float(np.cross(socket_was, socket_to) @ outlet_axis), float(socket_was @ socket_to)))
parts['lower-valve-elbow'] = (comps['lower-valve-elbow'][0].moved(MOVE).moved(
    cq.Location(cq.Vector(*outlet_at)) * cq.Location(cq.Vector(), cq.Vector(*outlet_axis), outlet_turn)
    * cq.Location(cq.Vector(*-outlet_at))), comps['lower-valve-elbow'][1])

# --- off the tee's free run, fluid-1 and the flow regulator ------------------------------------------
free_mouth = tee_at + west * union_tee.REACH
parts['fluid-1'] = (tube_run(free_mouth - west * union_tee.INSERTION, west, union_tee.INSERTION + SPAN + 15.),
                    pj.M_PVC_CLEAR)
reg_in = free_mouth + west * SPAN

# --- off the regulator, V-A on production's link and elbow, and V-A's wall -------------------------------
prod_in, prod_flow = (np.array(v, float) for v in comps['flow-regulator'][2](((0., 0., 0.), (1., 0., 0.))))
k = np.cross(prod_flow, west)
K = np.array([[0., -k[2], k[1]], [k[2], 0., -k[0]], [-k[1], k[0], 0.]])
R_M = np.eye(3) + K + K @ K / (1. + float(prod_flow @ west))      # production's flow onto `west`, the least turn
T_M = reg_in - R_M @ prod_in
m = gp_Trsf()
m.SetValues(*R_M[0], T_M[0], *R_M[1], T_M[1], *R_M[2], T_M[2])
M = cq.Location(m)


def carried(name, station):
    """Production's `station` of `name`, moved by M."""
    p, d = (np.array(v, float) for v in comps[name][2](station))
    return R_M @ p + T_M, R_M @ d


# The elbow's mouth on the regulator's outlet release face, so the link shows no length, as production draws
# it; production's code stands the elbow `link_gap` along the flow from that face, into the regulator.
reg_out, out_w = carried('flow-regulator', ((REGULATOR_LENGTH, 0., 0.), (1., 0., 0.)))
elbow_mouth, _ = carried('reg-va-elbow', acp.stem_elbow_reference().socket())
link_gap = float((elbow_mouth - reg_out) @ out_w)
M_VA = cq.Location(cq.Vector(*(-link_gap * out_w))) * M
parts['flow-regulator'] = (comps['flow-regulator'][0].moved(M), comps['flow-regulator'][1])
for n in ('reg-va-elbow', 'valve-v-a'):
    parts[n] = (comps[n][0].moved(M_VA), comps[n][1])
parts['reg-va-link'] = (tube_run(reg_out - out_w * 15., out_w, 15. + 16.891), pj.M_PVC_CLEAR)   # production's depths
va = mounts.valve_support_datums('valve-v-a')
at_va = layout.location('valve-v-a')
root_lo = (*va['root_min_world_mm'][:2], min(CAP_Z - T_M[2], va['root_max_world_mm'][2]) - 20.)   # still past the cap once bent
wall = block(va['bearing_min_world_mm'], va['bearing_max_world_mm']).fuse(block(root_lo, va['root_max_world_mm'])).cut(
    valve_seat.build_sockets().val().moved(at_va),
    valve_seat.build_port_channel(2. * valve_seat.seat_half_y + 2.).val().moved(at_va))
parts['va-wall'] = (wall.moved(M_VA), M_PETGF_BLACK)

# --- one bend in the split's stub, and the tee and everything on it turned with the bend's end -------
# The stub bends up in one arc over the SPAN it shows. The tee's branch takes the arc's end, so the tee
# and everything on it turn by the bend about the stub's straight mouth and move onto the arc's end.
rise = square(Z, flow)
k = np.cross(flow, rise)
KB = np.array([[0., -k[2], k[1]], [k[2], 0., -k[0]], [-k[1], k[0], 0.]])
mouth_was = nose + flow * SPAN


def bent(th, t=1.):
    """The point `t` of the way along the stub bent `th` radians up, and the turn at its end."""
    a = th * t
    return (nose + SPAN / th * (flow * math.sin(a) + rise * (1. - math.cos(a))),
            np.eye(3) + math.sin(th) * KB + (1. - math.cos(th)) * KB @ KB)


def top(th):
    end, turn = bent(th)
    return ((points - mouth_was) @ turn[2]).max() + end[2]


tops = {n: np.array([v.toTuple() for v in parts[n][0].tessellate(.05, .3)[0]]) for n in GROUP}
points = np.concatenate(list(tops.values()))
TH = brentq(lambda th: top(th) - (CEILING - CLEAR), 1e-6, SPAN / BEND_R)
stub_end, TURN = bent(TH)
T_G = stub_end - TURN @ mouth_was
g = gp_Trsf()
g.SetValues(*TURN[0], T_G[0], *TURN[1], T_G[1], *TURN[2], T_G[2])
for n in GROUP:
    parts[n] = (parts[n][0].moved(cq.Location(g)), parts[n][1])
parts['va-wall'] = (parts['va-wall'][0].cut(block((-200., 0., CAP_Z - 100.), (200., 800., CAP_Z))).clean(), M_PETGF_BLACK)
on_top = max(GROUP, key=lambda n: ((tops[n] - mouth_was) @ TURN[2]).max())
stub_arc = cq.Wire.assembleEdges([cq.Edge.makeThreePointArc(*(cq.Vector(*p) for p in (nose, bent(TH, .5)[0], stub_end)))])
ring = cq.Workplane(cq.Plane(origin=tuple(nose), xDir=tuple(rise), normal=tuple(flow))).circle(TUBE_OD / 2.) \
    .circle(TUBE_ID / 2.)
parts['water-split-stub'] = (tube_run(nose - flow * reducer_ref.TUBE_INSERTION_DEPTH, flow, reducer_ref.TUBE_INSERTION_DEPTH)
                             .fuse(ring.sweep(cq.Workplane().add(stub_arc)).val(),
                                   tube_run(stub_end, TURN @ flow, union_tee.INSERTION)).clean(),
                             cq.Color(*(c / 255. for c in SPOOLS['white'].rgb)))


def moved(p):
    return TURN @ p + T_G


# --- the pump and its suction joint, onto the elbow in V-K's outlet ------------------------------------
socket_mouth, socket_axis = (np.array(study['vk_line']['lower-valve-elbow'][key], float) for key in ('socket_mouth', 'socket_axis'))
vk_socket = TURN @ socket_axis
crossing = moved(socket_mouth + socket_axis * stem_elbow.HUB_BACK_REACH)    # the flipped elbow's, its shoulder on V-K's elbow
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
    return [*(mouth + d_w * stem_elbow.SOCKET_MOUTH_REACH - crossing), float(d_w @ vk_socket)]


forward, free, th, psi = fsolve(miss, [11.9 + socket_mouth[1] - moved(socket_mouth)[1], 16.7, 0.48, 0.])
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
parts['g-ganen-pump'] = (pump_body.moved(cq.Location(cq.Vector(*shift))), pump_colour)
parts.update({f'suction-{n}': (s.moved(at), c) for n, (s, c) in suction.items()})
parts['suction-stub'] = (tube_run(mouth - d_w * reducer_ref.TUBE_INSERTION_DEPTH, d_w,
                                  reducer_ref.TUBE_INSERTION_DEPTH + stem_elbow.SOCKET_INSERTION), pj.M_PVC_CLEAR)
parts['suction-elbow'] = (acp.stem_elbow(stem_elbow.SOCKET_INSERTION).moved(
    frame(crossing, (vk_socket, -d_w, np.cross(vk_socket, -d_w)))), M_NEOFIT_WHITE_ACETAL)

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
core = {name: mesh for name, mesh in enclosure.items() if any(fnmatch.fnmatchcase(name, g) for g in CORE)}
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

# --- the relays on the west wall and the C14, where production stands them ---------------------------
relays = ('relay-1', 'relay-2')
for n in relays:
    parts[n] = comps[n][:2]
parts['c14-inlet'] = comps['c14-inlet'][:2]

# --- the Mean Well on the ceiling ----------------------------------------------------------------------
psu, psu_colour, psu_carry = comps['psu']
PSU_STAND = psu.BoundingBox().xmin - WEST_WALL_X                     # production's, off the wall
backs_up = cq.Location(cq.Vector(), cq.Vector(0., 1., 0.), 90.)       # the face that bears on the wall, to the ceiling
flat = psu.moved(backs_up).BoundingBox()
aft_y, top_z = parts['c14-inlet'][0].BoundingBox().ymin - CLEAR, CEILING - PSU_STAND
west_x = max(parts[n][0].BoundingBox().xmax for n in relays) + CLEAR
psu_at = cq.Location(cq.Vector(west_x - flat.xmin, aft_y - flat.ymax, top_z - flat.zmax)) * backs_up
parts['psu'] = (psu.moved(psu_at), psu_colour)


# --- the bosses: the Mean Well's on the ceiling, the relays' bars on the west wall ---------------------
def located(loc, p, d):
    """`p` and `d` moved by `loc`."""
    trsf = loc.wrapped.Transformation()
    rot = np.array([[trsf.Value(i, j) for j in (1, 2, 3)] for i in (1, 2, 3)])
    return rot @ p + np.array([trsf.Value(i, 4) for i in (1, 2, 3)]), rot @ d


def boss(holes, n, length):
    """From the bodies' mounting plane at `holes` along `n`, `length` to the wall or ceiling: one boss on a
    lone hole, one bar over holes in a line."""
    a, b = holes[0], holes[-1]
    span = float(np.linalg.norm(b - a))
    x = (b - a) / span if span else square(np.array([1., 0., 0.]) if abs(n[0]) < .9 else np.array([0., 1., 0.]), n)
    w = cq.Workplane(cq.Plane(origin=tuple((a + b) / 2.), xDir=tuple(x), normal=tuple(n)))
    body = (w.slot2D(span + 2. * R_BOSS, 2. * R_BOSS) if span else w.circle(R_BOSS)).extrude(length).val()
    for h in holes:
        body = body.cut(cq.Solid.makeCylinder(R_BORE, length, cq.Vector(*h), cq.Vector(*n)))
    return body


bosses = []
for i, hole in enumerate(irm90.holes, 1):
    p, n = located(psu_at, *(np.array(v, float) for v in psu_carry(((*hole, 0.), (0., 0., -1.)))))
    bosses.append((f'psu-boss-{i}', boss([p], n, (CEILING - p[2]) / n[2])))
# The relays stand one over the other, so the holes at each end of both boards make one line, and one
# bar (production's `mount_bar_reach`) runs under all four.
ends = {}
for name in relays:
    for sx in (-1., 1.):
        for sy in (-1., 1.):
            p, n = (np.array(v, float) for v in comps[name][2](
                ((sx * teyleten.hole_dx, sy * teyleten.hole_dy, 0.), (0., 0., -1.))))
            ends.setdefault(round(p[1], 1), []).append(p)
for end, y in zip(('fore', 'aft'), sorted(ends)):
    holes = sorted(ends[y], key=lambda h: h[2])
    bosses.append((f'relay-{end}-bar', boss(holes, n, (WEST_WALL_X - holes[0][0]) / n[0])))
parts.update({n: (s, M_PETGF_BLACK) for n, s in bosses})

a = cq.Assembly(name='rear-port-lines')
for name, (s, c) in parts.items():
    a.add(s, name=name, color=c)
out_step = OUT / 'rear-port-lines.step'
export_assembly(a, str(out_step))

# --- what clashes, and the page: the rebuild without what this file draws again, these parts, the core ---
ADDED = (*GROUP, 'water-split-stub', 'psu', *relays, 'c14-inlet', *(n for n, _ in bosses))
# The tee and everything on it move as one, so what overlaps among them is study.py's and production's.
MATES = {frozenset(('water-split-stub', 'jg-pp0208e')), frozenset(('lower-valve-elbow', 'suction-elbow'))}
clashes = [(n, o, v) for i, n in enumerate(ADDED) for o in parts if o not in ADDED[:i + 1] and not {n, o} <= set(GROUP)
           for v in [overlap(parts[n][0], parts[o][0])] if v > .5 and frozenset((n, o)) not in MATES]
tee_up = moved(tee_at)[2] - tee_at[2]
outlet_moved = moved(outlet_at) - outlet_at
reg_pts = tops['flow-regulator'] @ TURN.T + T_G
reg_top = reg_pts[reg_pts[:, 2].argmax()]
into_cap = CAP_Z - parts['lower-valve-elbow'][0].BoundingBox().zmin
psu_boss, relay_bar = parts['psu-boss-1'][0].BoundingBox(), parts['relay-fore-bar'][0].BoundingBox()
stand, bar = psu_boss.zlen, relay_bar.xlen
psu_box, relay_box = parts['psu'][0].BoundingBox(), cq.Compound.makeCompound(
    [parts[n][0] for n in relays]).BoundingBox()
everything = cq.Compound.makeCompound([s for s, _ in parts.values()]).BoundingBox()     # framed above the cap
tee_group = cq.Compound.makeCompound([parts[n][0] for n in (*GROUP, 'water-split-stub')]).BoundingBox()
spec = {
    'title': 'Pump to V-K',
    'lede': (f"The split's stub bends once, {math.degrees(TH):.1f}° up at R{SPAN / TH:.0f} over the {SPAN:g} mm it shows, and "
             f"the union tee turns with its end. The tee and everything on it move as one: V-K with its wall and elbows, "
             f"fluid-1, the regulator, V-A and its wall, until the {on_top} stands {CLEAR:g} mm under the ceiling. The tee "
             f"rises {tee_up:.1f} mm; V-K's outlet rises {outlet_moved[2]:.1f} mm and swings {-outlet_moved[1]:.1f} mm fore, "
             f"and the pump follows it, {forward:.1f} mm forward of the study's. V-A's wall root still reaches the cap lid. "
             f"The Mean Well hangs from the ceiling, base up, on four Ø{interface.mount_boss_dia:g} bosses {stand:.1f} mm long, "
             f"its AC end {CLEAR:g} mm fore of the C14 and its west face {CLEAR:g} mm east of the relays; the relays "
             f"stand on the west wall where production stands them, one bar {bar:.1f} mm off the wall under each end. The "
             f"walls and the ceiling are not drawn. Amber: the stub, the tee, the Mean Well and the relays. Clashes as drawn: "
             f"{'; '.join(f'{n} with {o}, {v:.0f} mm³' for n, o, v in clashes) or 'none'}."),
    'columns': 1,
    'sync': False,
    'panels': [{
        'name': 'The tee raised on one bend, the Mean Well on the ceiling, the relays on the west wall',
        'view': {'az': 240, 'el': 15},
        'focus': {'center': [everything.center.x, everything.center.y, (CAP_Z + CEILING) / 2.],
                  'radius': math.hypot(everything.xlen, everything.ylen, CEILING - CAP_Z) * .42},
        'models': [
            {'step': 'hardware/assembly/scenes/out/rear-port-rebuild.step',
             'only': sorted(n for n in rebuild if not n.startswith(SUPERSEDED)),
             'ghost': ['enclosure-back-top', 'face-rail-*', 'tile-*', 'co2-tube']},
            {'step': 'hardware/assembly/scenes/out/rear-port-lines.step',
             'highlight': ['water-split-stub', 'jg-pp0208e', 'psu', *relays]},
            {'step': 'hardware/manifold-layout/enclosure-assembly.step', 'only': list(CORE),
             'ghost': ['cold-core/foam-*']}],
        'marks': [
            {'at': reg_top.tolist(), 'text': f'{on_top}, {CEILING - reg_top[2]:.1f} mm under the ceiling',
             'dx': -60, 'dy': -50},
            {'at': [psu_box.center.x, psu_box.center.y, psu_box.zmin], 'text': 'Mean Well on the ceiling',
             'dx': 50, 'dy': 70},
            {'at': [relay_box.xmax, relay_box.center.y, relay_box.center.z], 'text': 'relays on the west wall',
             'dx': -70, 'dy': 50}]}, {
        'name': 'The bend, from the east: the tee and everything on it with the ASSE chain',
        'view': {'az': 0, 'el': 5},
        'focus': {'center': [tee_group.center.x, tee_group.center.y, tee_group.center.z],
                  'radius': math.hypot(tee_group.ylen, tee_group.zlen) / 2.},
        'models': [
            {'step': 'hardware/assembly/scenes/out/rear-port-rebuild.step',
             'only': ['jg-pp010822e', 'gagira-coupling', 'multiplex-asse1022', 'jg-pi4512f6s', 'jg-pp061208w']},
            {'step': 'hardware/assembly/scenes/out/rear-port-lines.step',
             'only': [f'{n}*' for n in (*GROUP, 'water-split-stub')], 'highlight': ['water-split-stub', 'jg-pp0208e']}],
        'marks': [
            {'at': bent(TH, .5)[0].tolist(), 'text': f'one bend, {math.degrees(TH):.1f}° at R{SPAN / TH:.0f}',
             'dx': 50, 'dy': -60}]}]}
json.dump(spec, open(OUT / 'rear-port-lines.page.json', 'w'), indent=1)


def span_of(b):
    return f'{np.round([b.xmin, b.ymin, b.zmin], 2).tolist()} to {np.round([b.xmax, b.ymax, b.zmax], 2).tolist()}'


print(f'stub bent {math.degrees(TH):.2f} deg at R{SPAN / TH:.1f}; {on_top} on top, regulator top z {reg_top[2]:.2f}; tee '
      f'centre {np.round(moved(tee_at), 2).tolist()} ({tee_up:.2f} up); V-K outlet moved {np.round(outlet_moved, 2).tolist()}; '
      f'lower elbow {into_cap:.2f} mm into the cap lid; V-A wall {span_of(parts["va-wall"][0].BoundingBox())}')
print(f'pump {forward:.2f} mm forward (aft {shift[1]:.2f}); 3/8 tube free {free:.2f} mm, bent {math.degrees(th):.2f} deg '
      f'(R{free / th:.1f}), leaned {math.degrees(psi):.2f} deg; collet mouth {np.round(mouth, 2).tolist()}; miss '
      f'{np.round(miss((forward, free, th, psi)), 5).tolist()}')
print(f'discharge collet {np.round(d_mouth, 2).tolist()}; elbow {math.degrees(TILT):.2f} deg down; check port '
      f'{np.round(port_at, 2).tolist()}, bend {90. - math.degrees(dip):.2f} deg at R{BEND_R:g}; drop at '
      f'{np.round(drop_xy, 2).tolist()} from z {drop_top:.2f}, {drop:.2f} mm down onto {land_on} at z {land_z:.2f} '
      f'({CAP_Z - land_z:.2f} under the cap face)')
print(f'psu on the ceiling, west face at x {west_x:.2f}: {span_of(psu_box)}; relays {span_of(relay_box)}')
print(f'bosses {stand:.2f} mm under the ceiling, bars {bar:.2f} mm off the wall: ' +
      '; '.join(f'{n} {span_of(s.BoundingBox())}' for n, s in bosses))
print('clashes: ' + ('; '.join(f'{n} x {o} {v:.1f} mm3' for n, o, v in clashes) or 'none'))
print('->', out_step, OUT / 'rear-port-lines.page.json')
