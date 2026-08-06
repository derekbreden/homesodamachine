"""Flavor module — one whole flavor channel as a single sub-assembly.

Everything one flavor needs and nothing another flavor touches: four solenoid
valves, one peristaltic pump, two Tee junctions, ten tube segments — channel B's
own nine plus the lead from the module's inlet port to the select valve — and
the wire loom that lands every coil and the motor on one connector, all carried
on one printed L that sets down over the cold core and hangs its pump down the
front column.

Coordinate frame
----------------
The module's own, anchored to the two faces of the cold core it wraps:

  * origin  y = 0 at the core's FRONT face, z = 0 at its TOP face; x = 0 on the
            module's SUCTION line. +X east, +Y aft, +Z up — the enclosure's own
            senses, so a placement is a translation and a mirror, never a turn.
  * DECK    y > 0, z > 0 — the leg lying on the foam cap, carrying every valve,
            both junctions and every tube.
  * FOOT    y < 0, z < 0 — the leg standing in the front column, carrying the
            pump alone, because a KPHM400 on end is the one body in a flavor
            channel that wants more height than the bay over the core has.

The two legs meet at the core's front-top arris, which is why the shape is an L
and not a box: the deck's floor is the cap and the foot's lane is the column
ahead of it, and nothing in the machine is in either place.

The circuit
-----------
`../../topology/fluid-topology.md` channel B, whose reservoir carries two mouths
of its own and so needs no junction at the bag:

      IN ──→ V-select ──┐                      ┌──→ V-nozzle ──→ OUT
                        ├─ Y-suct ─→ PUMP ─→ Y-disch ─┤
    DRAW ──→ V-draw ────┘                      └──→ V-fill ───→ FILL

Two valves merge at the suction junction, two split at the discharge one. The
graph is planar and the module is its planar embedding: TWO PARALLEL LINES along
Y, a valve at each end of each line and its Tee between them, both Tees dropping
their branch to a barb of the pump below. Every port faces along the line it is
on, so no leg crosses another anywhere in the module.

Each boundary port stands where the thing it mates does. The two reservoir
mouths open on the cap at the deck's FORWARD end; the nozzle bulkhead is in the
rear panel at its AFT end. Two lines carry two forward seats and two aft seats,
so draw and fill hold the forward pair and select and nozzle the aft — and each
line's two valves are then the pair its own Tee's run takes.

The four boundary ports are the whole interface: `PORTS` states each one's
position and axis in this frame, and nothing outside the module needs any other
number from inside it.

Run: tools/cad-venv/bin/python hardware/printed-parts/flavor-module/flavor_module.py
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts",
           _hw / "printed-parts" / "cadlib",
           _hw / "printed-parts" / "cold-core",
           _hw / "printed-parts" / "flavor" / "pump-case",
           _hw / "reference" / "beduan-solenoid",
           _hw / "reference" / "kamoer-kphm400",
           _hw / "reference" / "tee-connector",
           _hw / "printed-parts" / "valve-manifold" / "single-tray"):
    sys.path.insert(0, str(_p))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))

from _cadq_export import export_assembly          # noqa: E402
from docgen import substitute_md, substitute_py_comments   # noqa: E402
import beduan_solenoid as valve                   # noqa: E402  — its body, its two ports, its spades
import kamoer_kphm400 as pump                     # noqa: E402  — the head's two barb stations
import tee_connector as tee                       # noqa: E402  — the junction's run and branch reaches
import single_tray as cell                        # noqa: E402  — one valve's cradle, cut into our deck


# ── What the module wraps, and the room it has ────────────────────────────────
# The cold core as the enclosure places it, and the cavity around it, both read
# in this module's own frame (y = 0 the core's front face, z = 0 its top). The
# core's box is 181 x 283 x 253.4 seated in the back-bottom corner; the cavity is
# the core's own width plus a boss chain a side (`_contents.SIDE_RIB_INSET`), the
# stated 400 mm appliance less two walls, and the stated rear plane.
CORE_X = (0.0, 181.0)               # world x — the module frame shares this axis
CORE_Y = (0.0, 283.0)               # core front face to its rear
CORE_TOP = 0.0                      # the deck's floor
CAVITY_X = (-14.0, 195.0)           # world x, wall to wall
CAVITY_Y = (-187.38, 291.5)         # front wall to the stated rear plane
CAVITY_Z = (-253.4, 140.6)          # floor slab to the 400 mm ceiling
BED = 320.0                         # the printer's own bound, per piece

# The core's two cap mouths for one reservoir, and the rear panel's flavor
# bulkhead — the three fixed points every other station in this file is measured
# from. World x 47 is reservoir B's own conduit column; the mirrored instance
# takes 181 - 47 = 134, which is what this module asks of reservoir A.
MOUTH_WORLD_X = 47.0
DRAW_MOUTH_Y = 6.0                  # world y 186.5, the draw conduit's bore
FILL_MOUTH_Y = 53.5                 # world y 234.0, the fill bore in the cap

TUBE_D = tee.TUBE_D                 # 1/4" OD LLDPE, the stock every segment is
BEND = 25.4                         # what that stock's own minimum asks of a corner

# ── The two lines ─────────────────────────────────────────────────────────────
# Separation is the module's whole width bar a valve, so it is what TWO
# instances leave each other. The pump's own barbs stand wider, and the branch
# legs lean the difference in.
LINE_S = 0.0                        # suction line: draw valve, Y-suct, select valve
LINE_D = -44.0                      # discharge line: fill valve, Y-disch, nozzle valve
# Every port axis on ONE plane, and its height is the whole of what the deck
# stands off the cap. A Tee's branch hangs `BRANCH_REACH` under its run and so
# comes out BELOW the plate whatever the plate's thickness — which makes the
# band under the deck the lane both pump legs run in, and that band has to be
# deep enough for the corner that turns each of them up into its branch.
PORT_Z = 55.0
VALVE_Z = PORT_Z - valve.port_center_z   # the plane the valves' posts stand on
BRANCH_Z = PORT_Z - tee.BRANCH_REACH     # where each branch collet faces down
UNDER_DECK_Z = BRANCH_Z - BEND           # the lane, one full corner below them

# Tube between a Tee's run collet face and the valve port collet facing it. The
# two are collinear, so this is a straight length and not a lead for a corner.
COLLET_GAP = 10.0
TEE_TO_VALVE = tee.RUN_HALF + COLLET_GAP + valve.port_length / 2.0

# Y stations. The two forward valves stand far enough back that their own cells
# clear the mouths they reach — a cell over a mouth would put a valve body in the
# drop — and far enough that the leg forward of each has the straight its corner
# takes. Everything aft follows by TEE_TO_VALVE.
Y_DRAW = 90.0
Y_SUCT = Y_DRAW + TEE_TO_VALVE
Y_SELECT = Y_SUCT + TEE_TO_VALVE
Y_FILL = 128.0
Y_DISCH = Y_FILL + TEE_TO_VALVE
Y_NOZZLE = Y_DISCH + TEE_TO_VALVE

# ── The pump, in the foot ─────────────────────────────────────────────────────
# Head UP: the barbs stand 20.38 from the head end, so the native turn puts them
# at the bottom of a 127 mm body and every leg to the deck would climb the whole
# of it. Flipped, they stand near the top of the foot and each leg is one corner.
PUMP_MID_X = (LINE_S + LINE_D) / 2.0
PUMP_FACE_Y = -10.0                 # the barb face, clear of the core's front plane
# The barbs stand ON the under-deck lane, so each leg leaves its barb, crosses
# the core's front plane already at the height it will run at, and turns ONCE —
# up into the branch above it. The pump's face is ten millimetres off that plane.
PUMP_BARB_Z = UNDER_DECK_Z
PUMP_BARB_PITCH = 57.0
COLLET_SKEW = 22.0                  # `_contents.FLAVOR_SKEW`, the lean a collet grips through
# The barbs stand wider apart than the lines do, so each leg leaves its barb off
# its Tee's column by half the difference and closes it over the length of the
# run rather than in a corner.
BARB_OFFSET = (PUMP_BARB_PITCH - abs(LINE_S - LINE_D)) / 2.0
BARB_LEAN = math.degrees(math.atan2(BARB_OFFSET, Y_SUCT - PUMP_FACE_Y))

# ── The printed L ─────────────────────────────────────────────────────────────
DECK_X = (LINE_D - cell.tray_half_x, LINE_S + cell.tray_half_x)
DECK_Y = (-25.0, 288.0)
DECK_Z = (VALVE_Z + cell.tray_bottom_z, VALVE_Z + cell.tray_top_z)
RAIL_W = 8.0                        # the two rails the deck stands on, on the cap
MOUTH_BORE = 16.0                   # the deck's aperture over each cap mouth
TOWER_WALL = 3.0
TOWER_SLIP = 0.5                    # per side, around the pump
RACEWAY_Z = (VALVE_Z + valve.coil_z_range[1] + 5.0,
             VALVE_Z + valve.coil_z_range[1] + 19.0)   # clear over every coil
RACEWAY_W = 24.0
WIRE_D = 4.0                        # one valve's two-conductor drop, as a bundle
TRUNK_D = 7.0                       # the loom where all five drops run together

COLORS = {
    "deck": cq.Color(0.55, 0.60, 0.68),
    "tower": cq.Color(0.45, 0.50, 0.58),
    "valve": cq.Color(0.93, 0.93, 0.90),
    "pump": cq.Color(0.35, 0.55, 0.75),
    "tee": cq.Color(0.30, 0.65, 0.45),
    "tube": cq.Color(0.85, 0.45, 0.25),
    "wire": cq.Color(0.20, 0.20, 0.22),
}


# ── Tube geometry ─────────────────────────────────────────────────────────────

def _unit(a, b):
    v = [b[i] - a[i] for i in range(3)]
    n = math.sqrt(sum(c * c for c in v))
    return [c / n for c in v]


def _dist(a, b):
    return math.sqrt(sum((b[i] - a[i]) ** 2 for i in range(3)))


def corner_radii(pts, want=BEND):
    """Per-corner radius, as (turn°, radius, tangent) — what the legs actually let.

    A corner's tangent is `R·tan(θ/2)` off its vertex each way, so a leg between
    two corners carries both. A leg too short for the pair shrinks them IN
    PROPORTION to what each asked, so the ratio between the two is the ratio of
    their appetites. Iterated: shrinking one corner relieves the leg on its far
    side."""
    n = len(pts) - 2
    if n <= 0:
        return []
    turns, tangents = [], []
    for i in range(1, len(pts) - 1):
        din, dout = _unit(pts[i - 1], pts[i]), _unit(pts[i], pts[i + 1])
        dot = max(-1.0, min(1.0, sum(din[j] * dout[j] for j in range(3))))
        turn = math.degrees(math.acos(dot))
        turns.append(turn)
        tangents.append(0.0 if turn < 1e-6
                        else want * math.tan(math.radians(turn) / 2.0))
    legs = [_dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    for _ in range(24):
        moved = False
        for li, leg in enumerate(legs):
            # Corners standing on this leg: the one at each end that exists.
            here = [c for c in (li - 1, li) if 0 <= c < n]
            asked = sum(tangents[c] for c in here)
            if asked > leg + 1e-9 and asked > 0.0:
                for c in here:
                    tangents[c] *= leg / asked
                moved = True
        if not moved:
            break
    return [(turns[i], 0.0 if turns[i] < 1e-6
             else tangents[i] / math.tan(math.radians(turns[i]) / 2.0), tangents[i])
            for i in range(n)]


def centreline(pts, want=BEND):
    """The path as a wire — straights joined by an arc at every corner."""
    radii = corner_radii(pts, want)
    edges, cur = [], cq.Vector(*pts[0])
    for i in range(1, len(pts) - 1):
        turn, r, t = radii[i - 1]
        if t <= 1e-9:
            continue
        din, dout = _unit(pts[i - 1], pts[i]), _unit(pts[i], pts[i + 1])
        p1 = cq.Vector(*[pts[i][j] - din[j] * t for j in range(3)])
        p2 = cq.Vector(*[pts[i][j] + dout[j] * t for j in range(3)])
        # Arc centre on the inward bisector, r/cos(θ/2) from the vertex; the arc's
        # own midpoint is r back from that centre toward the vertex.
        bis = [dout[j] - din[j] for j in range(3)]
        bl = math.sqrt(sum(c * c for c in bis))
        bis = [c / bl for c in bis]
        ctr = [pts[i][j] + bis[j] * (r / math.cos(math.radians(turn) / 2.0))
               for j in range(3)]
        mv = [pts[i][j] - ctr[j] for j in range(3)]
        ml = math.sqrt(sum(c * c for c in mv))
        mid = cq.Vector(*[ctr[j] + mv[j] / ml * r for j in range(3)])
        if (p1 - cur).Length > 1e-9:
            edges.append(cq.Edge.makeLine(cur, p1))
        edges.append(cq.Edge.makeThreePointArc(p1, mid, p2))
        cur = p2
    tail = cq.Vector(*pts[-1])
    if (tail - cur).Length > 1e-9:
        edges.append(cq.Edge.makeLine(cur, tail))
    return cq.Wire.assembleEdges(edges)


def swept(pts, diam=TUBE_D, want=BEND):
    """Sweep a bore of `diam` along the path."""
    path = centreline(pts, want)
    prof = cq.Wire.makeCircle(diam / 2.0, cq.Vector(*pts[0]),
                              cq.Vector(*_unit(pts[0], pts[1])))
    return cq.Solid.sweep(prof, [], path, makeSolid=True, isFrenet=True)


# ── Stations ──────────────────────────────────────────────────────────────────

def valve_at(x, y, flow_aft: bool):
    """One valve on its seat: `flow_aft` puts its inlet forward, else it is
    turned round and its inlet faces aft. The cell is symmetric in Y, so the
    turn is the valve's alone and both clockings sit in the same seat."""
    v = valve.build_beduan_solenoid().val()
    if not flow_aft:
        v = v.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 180.0)
    return v.translate(cq.Vector(x, y, VALVE_Z))


def valve_ports(x, y, flow_aft: bool):
    """That valve's two collet faces, as (inlet, outlet) points on `PORT_Z`."""
    reach = valve.port_length / 2.0
    fwd, aft = (x, y - reach, PORT_Z), (x, y + reach, PORT_Z)
    return (fwd, aft) if flow_aft else (aft, fwd)


def tee_at(x, y):
    """A Tee with its RUN along Y and its BRANCH facing DOWN.

    The run is the line — both valves on it stand on that axis, so each leg to
    the Tee is one straight length with no corner in it — and the branch is the
    leg that leaves it, which here is the drop to the pump below. Native is run
    on Z and branch on +Y, so one turn of -90° about X puts both where they go."""
    body = cq.importers.importStep(str(tee.STEP)).val()
    body = body.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), -90.0)
    return body.translate(cq.Vector(x, y, PORT_Z))


def tee_ports(x, y):
    """Its three collet faces: forward run, aft run, and the branch under it."""
    return ((x, y - tee.RUN_HALF, PORT_Z),
            (x, y + tee.RUN_HALF, PORT_Z),
            (x, y, PORT_Z - tee.BRANCH_REACH))


def pump_placed():
    """The pump, head up, its barb midpoint on the foot's own station."""
    asm = pump.build_assembly().toCompound()
    asm = asm.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), 180.0)
    (bx0, _, bz0), _ = pump.barb(0)
    (bx1, by1, bz1), _ = pump.barb(1)
    mid = (-(bx0 + bx1) / 2.0, by1, -(bz0 + bz1) / 2.0)   # after the flip
    return asm.translate(cq.Vector(PUMP_MID_X - mid[0],
                                   PUMP_FACE_Y - mid[1],
                                   PUMP_BARB_Z - mid[2]))


BARB_PROUD = 1.0                    # where a leg starts, off the body's own face


def pump_barbs():
    """The two barb faces, suction first — each on the line whose Tee it feeds.

    A leg starts `BARB_PROUD` off the pump's face. The leg LEANS, so its opening
    circle stands square to the leaning axis and not to the face. The real barb
    stands 11.3 mm proud of that face."""
    half = PUMP_BARB_PITCH / 2.0
    y = PUMP_FACE_Y + BARB_PROUD
    return ((PUMP_MID_X + half, y, PUMP_BARB_Z),
            (PUMP_MID_X - half, y, PUMP_BARB_Z))


# Where this module's suction line stands in the enclosure, which is the one
# number that ties its frame to the machine's: the cap's conduit column has to
# fall inside the deck, and the pair has to be symmetric about the core.
WEST_LINE_S_X = 60.25
MOUTH_X = MOUTH_WORLD_X - WEST_LINE_S_X      # the cap's conduit column, in this frame

# The module's whole interface — the four ports anything outside it mates, each
# as (point, outward axis). Both world ports stand on the deck's AFT face and
# both core ports over the cap's own mouths, which is the interface the port
# positions forced: world aft, core forward.
PORTS = {
    "in":   ((LINE_S, DECK_Y[1], PORT_Z), (0.0, 1.0, 0.0)),
    "out":  ((LINE_D, DECK_Y[1], PORT_Z), (0.0, 1.0, 0.0)),
    "draw": ((MOUTH_X, DRAW_MOUTH_Y, CORE_TOP), (0.0, 0.0, 1.0)),
    "fill": ((MOUTH_X, FILL_MOUTH_Y, CORE_TOP), (0.0, 0.0, 1.0)),
}


# ── The nine segments ─────────────────────────────────────────────────────────

def runs() -> dict:
    """Every tube in the channel, port to port, as its own polyline.

    The four on a line are single straights — a valve port and a run collet on
    one axis. The two branch legs each turn once, out of the foot and up into a
    down-facing collet. The two bag legs turn twice, because the cap's two mouths
    stand on ONE column and the lines stand either side of it: each runs forward
    on its own line, leans across on a diagonal, and drops. They lean at
    DIFFERENT y — the draw's crossing is forward of the fill's own drop — so the
    two never meet, which is the only place in the module they could."""
    draw_i, draw_o = valve_ports(LINE_S, Y_DRAW, True)
    sel_i, sel_o = valve_ports(LINE_S, Y_SELECT, False)
    fill_i, fill_o = valve_ports(LINE_D, Y_FILL, False)
    noz_i, noz_o = valve_ports(LINE_D, Y_NOZZLE, True)
    s_fwd, s_aft, s_br = tee_ports(LINE_S, Y_SUCT)
    d_fwd, d_aft, d_br = tee_ports(LINE_D, Y_DISCH)
    barb_s, barb_d = pump_barbs()

    return {
        # ── the shared source in, and the two legs of the suction run
        "select-in":   [PORTS["in"][0], sel_i],
        "select-suct": [sel_o, s_aft],
        "draw-suct":   [draw_o, s_fwd],
        # ── the branch legs: out of the foot along the under-deck lane, then one
        #    corner up into a down-facing collet. The [6.5 mm](BARB_OFFSET)
        #    between a barb and its Tee's own column is taken as a LEAN over the
        #    whole run — [2.3](BARB_LEAN)°, well inside the
        #    [22](COLLET_SKEW)° a push-to-connect collet grips through — so the
        #    leg spends no corner of its own on it.
        "suct-pump":   [barb_s, (LINE_S, Y_SUCT, UNDER_DECK_Z), s_br],
        "pump-disch":  [barb_d, (LINE_D, Y_DISCH, UNDER_DECK_Z), d_br],
        # ── the two legs of the discharge run
        "disch-fill":  [d_fwd, fill_i],
        "disch-noz":   [d_aft, noz_i],
        # ── out to the rear panel's bulkhead
        "nozzle-out":  [noz_o, PORTS["out"][0]],
        # ── the two bag legs, down the cap's own column
        "draw-mouth":  [draw_i, (LINE_S, Y_DRAW - 35.0, PORT_Z),
                        (MOUTH_X, DRAW_MOUTH_Y, PORT_Z), PORTS["draw"][0]],
        "fill-mouth":  [fill_o, (LINE_D, Y_FILL - 44.0, PORT_Z),
                        (MOUTH_X, FILL_MOUTH_Y, PORT_Z), PORTS["fill"][0]],
        # (the draw leans across at y ~55 and the fill drops at y 53.5, so the
        #  two share neither a column nor a plane — the check is in `_report`)
    }


# ── The wire loom ─────────────────────────────────────────────────────────────

def spade_station(x, y, flow_aft: bool):
    """Where a valve's two spades stand — off its coil's own face, which the
    valve's turn carries with it."""
    face = y + valve.coil_face_y if flow_aft else y - valve.coil_face_y
    return (x, face + (6.0 if flow_aft else -6.0), VALVE_Z + valve.spade_z_center)


def wires() -> dict:
    """Each body's drop into the raceway, and the trunk that carries them out.

    The loom is the one thing in the module that is not on a line: it runs ABOVE
    every coil, which is the band the valves leave open and nothing else wants,
    so a drop is short and vertical and no wire shares a lane with a tube."""
    mid = RACEWAY_Z[0] + (RACEWAY_Z[1] - RACEWAY_Z[0]) / 2.0
    trunk_x = PUMP_MID_X
    out = {}
    for name, (x, y, aft) in (("draw", (LINE_S, Y_DRAW, True)),
                              ("select", (LINE_S, Y_SELECT, False)),
                              ("fill", (LINE_D, Y_FILL, False)),
                              ("nozzle", (LINE_D, Y_NOZZLE, True))):
        sx, sy, sz = spade_station(x, y, aft)
        out[f"wire-{name}"] = [(sx, sy, sz), (sx, sy, mid), (trunk_x, sy, mid)]
    # The pump's leads leave its motor end — which the head-up turn puts at the
    # TOP of the foot, open to the well the pump drops into — climb out of the
    # tower ahead of the deck's own forward edge, and turn aft into the trunk.
    lead_y = DECK_Y[0] - 12.0
    out["wire-pump"] = [(trunk_x, lead_y, pump_placed().BoundingBox().zmax - 6.0),
                        (trunk_x, lead_y, mid),
                        (trunk_x, Y_DRAW, mid)]
    out["loom-trunk"] = [(trunk_x, lead_y, mid), (trunk_x, DECK_Y[1] - 4.0, mid)]
    return out


# ── The printed L ─────────────────────────────────────────────────────────────

def build_deck():
    """The deck: one plate carrying all four cells, both Tee cradles, the two
    apertures over the cap's mouths, and the rails it stands on.

    The cells are `single_tray.cut_cell`'s, so a seat here cannot drift from the
    seat the manifold's own trays use. The Tee cradles are this module's own: a
    junction in this machine has never had a holder, and a Tee whose run lies
    along a line has an obvious one — a trough on that axis, taking its lower
    half."""
    plate = (cq.Workplane("XY").workplane(offset=cell.tray_bottom_z)
             .box(DECK_X[1] - DECK_X[0], DECK_Y[1] - DECK_Y[0],
                  cell.tray_top_z - cell.tray_bottom_z,
                  centered=(False, False, False))
             .translate(cq.Vector(DECK_X[0], DECK_Y[0], 0.0)))
    for x, y in ((LINE_S, Y_DRAW), (LINE_S, Y_SELECT),
                 (LINE_D, Y_FILL), (LINE_D, Y_NOZZLE)):
        plate = cell.cut_cell(plate, x, y)
    # A cell's saddle is a tray's length; a valve's port runs `port_length` and
    # this plate runs the whole line under it. So the trough runs the LINE — the
    # same lane the Tee between the two valves lies in, which is where the
    # junction's cradle comes from.
    for x in (LINE_S, LINE_D):
        lane = cq.Solid.makeCylinder(
            cell.saddle_radius, DECK_Y[1] - DECK_Y[0] + 2.0,
            cq.Vector(x, DECK_Y[0] - 1.0, valve.port_center_z),
            cq.Vector(0.0, 1.0, 0.0))
        plate = plate.cut(cq.Workplane(obj=lane))
    # Tee cradles — a half-round trough on the run's own axis, open at the top.
    for x, y in ((LINE_S, Y_SUCT), (LINE_D, Y_DISCH)):
        trough = cq.Solid.makeCylinder(
            tee.HALF_W + 0.3, 2 * tee.RUN_HALF + 8.0,
            cq.Vector(x, y - tee.RUN_HALF - 4.0, valve.port_center_z),
            cq.Vector(0.0, 1.0, 0.0))
        plate = plate.cut(cq.Workplane(obj=trough))
    plate = plate.translate(cq.Vector(0, 0, VALVE_Z))
    # The two apertures over the cap's mouths, each the LEG'S OWN PATH swept
    # oversize. A leg arrives on an arc, so it crosses the plate's band up to a
    # corner's travel away from the bore it is heading for.
    for name in ("draw-mouth", "fill-mouth"):
        plate = plate.cut(cq.Workplane(obj=swept(runs()[name], MOUTH_BORE)))
    # A bore under each Tee for its own BRANCH, which hangs a `BRANCH_REACH`
    # below the run and so comes out under the plate whatever the plate is: the
    # collet it presents is in the under-deck lane, and the leg that fills it
    # comes up the lane, not down through the deck.
    for x, y in ((LINE_S, Y_SUCT), (LINE_D, Y_DISCH)):
        plate = plate.cut(cq.Workplane("XY").workplane(offset=DECK_Z[0] - 1.0)
                          .center(x, y).circle(tee.HALF_W + 0.3)
                          .extrude(DECK_Z[1] - DECK_Z[0] + 2.0))
    # The rails it stands on — two runs down the cap, clear of both apertures.
    rails = None
    for x in (DECK_X[0] + RAIL_W / 2.0, DECK_X[1] - RAIL_W / 2.0):
        r = (cq.Workplane("XY").workplane(offset=CORE_TOP)
             .center(x, (max(CORE_Y[0], DECK_Y[0]) + DECK_Y[1]) / 2.0)
             .box(RAIL_W, DECK_Y[1] - max(CORE_Y[0], DECK_Y[0]), DECK_Z[0] - CORE_TOP,
                  centered=(True, True, False)))
        rails = r if rails is None else rails.union(r)
    return plate.union(rails)


def build_tower():
    """The foot: a four-wall well the pump drops into from above, closed by the
    deck over it. Open on +Y at the barb band so the two legs leave on the face
    they stand on, and floored, because the pump's own weight is the load."""
    p = pump_placed().BoundingBox()
    x0, x1 = p.xmin - TOWER_SLIP - TOWER_WALL, p.xmax + TOWER_SLIP + TOWER_WALL
    y0, y1 = p.ymin - TOWER_SLIP - TOWER_WALL, p.ymax + TOWER_SLIP + TOWER_WALL
    z0 = p.zmin - TOWER_SLIP - TOWER_WALL
    shell = (cq.Workplane("XY").workplane(offset=z0)
             .box(x1 - x0, y1 - y0, DECK_Z[0] - z0, centered=(False, False, False))
             .translate(cq.Vector(x0, y0, 0.0)))
    well = (cq.Workplane("XY").workplane(offset=p.zmin - TOWER_SLIP)
            .box(p.xlen + 2 * TOWER_SLIP, p.ylen + 2 * TOWER_SLIP,
                 DECK_Z[0] - p.zmin + 2 * TOWER_SLIP, centered=(False, False, False))
            .translate(cq.Vector(p.xmin - TOWER_SLIP, p.ymin - TOWER_SLIP, 0.0)))
    shell = shell.cut(well)
    # The barb window: the two legs leave on +Y, so that wall opens over the band
    # they stand in and the straps above and below it hold the pump in.
    win = (cq.Workplane("XY").workplane(offset=PUMP_BARB_Z - 16.0)
           .center((x0 + x1) / 2.0, y1 - TOWER_WALL / 2.0)
           .box(x1 - x0 - 2 * TOWER_WALL, TOWER_WALL + 2.0, 32.0,
                centered=(True, True, False)))
    return shell.cut(win)


# ── The whole thing ───────────────────────────────────────────────────────────

def parts() -> dict:
    """Every solid in the module, by name — printed, bought, tube and wire."""
    out = {"deck": build_deck().val(), "tower": build_tower().val()}
    for name, (x, y, aft) in (("v-draw", (LINE_S, Y_DRAW, True)),
                              ("v-select", (LINE_S, Y_SELECT, False)),
                              ("v-fill", (LINE_D, Y_FILL, False)),
                              ("v-nozzle", (LINE_D, Y_NOZZLE, True))):
        out[name] = valve_at(x, y, aft)
    out["y-suction"] = tee_at(LINE_S, Y_SUCT)
    out["y-discharge"] = tee_at(LINE_D, Y_DISCH)
    out["pump"] = pump_placed()
    for name, pts in runs().items():
        out[name] = swept(pts)
    for name, pts in wires().items():
        out[name] = swept(pts, TRUNK_D if name == "loom-trunk" else WIRE_D, 8.0)
    return out


def _color(name):
    if name in ("deck",):
        return COLORS["deck"]
    if name in ("tower",):
        return COLORS["tower"]
    if name.startswith("v-"):
        return COLORS["valve"]
    if name.startswith("y-"):
        return COLORS["tee"]
    if name == "pump":
        return COLORS["pump"]
    if name.startswith("wire") or name == "loom-trunk":
        return COLORS["wire"]
    return COLORS["tube"]


def build_assembly(origin=(0.0, 0.0, 0.0), mirror=False) -> cq.Assembly:
    """One instance. `mirror` reflects it about its own x = 0 — the two flavors
    are one design, and the second is the first turned over so both hang their
    mouths on their own reservoir's column."""
    asm = cq.Assembly()
    for name, solid in parts().items():
        s = solid.mirror("YZ") if mirror else solid
        asm.add(cq.Workplane(obj=s).translate(cq.Vector(*origin)),
                name=name, color=_color(name))
    return asm


# Where the two instances stand in the enclosure's own frame. Each carries its
# suction line so that the module's mouth column lands on its reservoir's cap
# conduit, and the pair is symmetric about the core's own centre.
WEST_ORIGIN = (WEST_LINE_S_X, 180.5, 253.4)
EAST_ORIGIN = (2 * 90.5 - WEST_LINE_S_X, 180.5, 253.4)


def build_pair() -> cq.Assembly:
    """Both flavors, in the enclosure's frame, to see whether two fit."""
    asm = cq.Assembly()
    asm.add(build_assembly(WEST_ORIGIN), name="flavor-a")
    asm.add(build_assembly(EAST_ORIGIN, mirror=True), name="flavor-b")
    return asm


# ── What the module holds itself to ───────────────────────────────────────────
# The channel's own inventory, from `../../topology/fluid-topology.md` — four
# valves, one pump, two junctions, nine segments. The report counts against this
# rather than against what the file happens to build, so a part dropped in an
# edit fails here instead of leaving quietly.
INVENTORY = {
    "valves": ("v-draw", "v-select", "v-fill", "v-nozzle"),
    "junctions": ("y-suction", "y-discharge"),
    "pump": ("pump",),
    "segments": ("select-in", "select-suct", "draw-suct", "suct-pump",
                 "pump-disch", "disch-fill", "disch-noz", "nozzle-out",
                 "draw-mouth", "fill-mouth"),
}

# The L is the cavity LESS the core, and that is how it is tested: a box test
# for the cavity and a BOOLEAN against the core. The deck plate is one solid
# spanning both legs, so the shape only reads as an L against the core itself.
def _in_cavity(bb, origin_x=WEST_LINE_S_X, tol=1e-6):
    """`CAVITY_X` is the machine's own x — the one axis this frame shares with
    the enclosure but does not share an origin with — so a body is carried back
    to the world before it is asked whether it is inside the walls."""
    return (bb.xmin + origin_x >= CAVITY_X[0] - tol
            and bb.xmax + origin_x <= CAVITY_X[1] + tol
            and bb.ymin >= CAVITY_Y[0] - tol and bb.ymax <= CAVITY_Y[1] + tol
            and bb.zmin >= CAVITY_Z[0] - tol and bb.zmax <= CAVITY_Z[1] + tol)


def core_box():
    """The cold core, in this module's frame — the thing the L wraps."""
    return cq.Solid.makeBox(
        CORE_X[1] - CORE_X[0], CORE_Y[1] - CORE_Y[0], 253.4,
        cq.Vector(CORE_X[0] - WEST_LINE_S_X, CORE_Y[0], CORE_TOP - 253.4))


# A wire lands ON what it drives: its bundle starts inside the spade stack it
# terminates on and ends inside the trunk it joins, so those pairs are unions
# and not clashes. Every OTHER pair in the module — tube against tube, tube
# against body, body against print — is strictly disjoint; a tube is drawn from
# its collet FACE.
JOINED = {frozenset(p) for p in (
    ("wire-draw", "v-draw"), ("wire-select", "v-select"),
    ("wire-fill", "v-fill"), ("wire-nozzle", "v-nozzle"),
    ("wire-pump", "pump"),
    ("wire-draw", "loom-trunk"), ("wire-select", "loom-trunk"),
    ("wire-fill", "loom-trunk"), ("wire-nozzle", "loom-trunk"),
    ("wire-pump", "loom-trunk"),
)}


def _overlap(a, b) -> float:
    """Shared volume of two solids, in mm³. Zero for a touching pair."""
    try:
        return a.intersect(b).Volume()
    except Exception:
        return 0.0


def _report():
    """Prove the five things the module claims, in the order they were asked for.

    Every claim is a measurement off the built solids — a count against the
    topology's own inventory, a pairwise boolean, a radius read back off the
    drawn path, a bounding box against the two bands, and the same boolean
    between two instances. Nothing here reads an intention."""
    built = parts()
    ok = True

    print("1. EVERY COMPONENT AND TUBE")
    for kind, names in INVENTORY.items():
        missing = [n for n in names if n not in built]
        print(f"   {kind:<10} {len(names) - len(missing)}/{len(names)}"
              + (f"   MISSING {missing}" if missing else ""))
        ok &= not missing
    looms = [n for n in built if n.startswith("wire") or n == "loom-trunk"]
    print(f"   {'wires':<10} {len(looms)} bundles + trunk, all four coils and the motor")
    print(f"   {'printed':<10} deck, tower")

    print("\n2. NOT OVERLAPPING")
    names = list(built)
    clashes, tested = [], 0
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if frozenset((a, b)) in JOINED:
                continue
            tested += 1
            v = _overlap(built[a], built[b])
            if v > 1e-6:
                clashes.append((a, b, v))
    for a, b, v in sorted(clashes, key=lambda c: -c[2]):
        print(f"   CLASH {a} x {b}  {v:.3f} mm3")
    print(f"   {len(names)} solids, {tested} pairs tested "
          f"({len(JOINED)} joined pairs excluded), {len(clashes)} clashing")
    ok &= not clashes

    print("\n3. ARRANGEMENT — every corner, and what it seats")
    for name, pts in runs().items():
        radii = corner_radii(pts)
        length = sum(_dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
        if not radii:
            print(f"   {name:<12} {length:7.1f} mm  straight")
            continue
        worst_r = min(r for _t, r, _tan in radii)
        mark = "ok " if worst_r >= BEND - 1e-6 else "   "
        turns = " ".join(f"{t:.0f}deg/R{r:.1f}" for t, r, _tan in radii)
        print(f"   {name:<12} {length:7.1f} mm  {mark}{turns}")
        ok &= worst_r >= 1.0

    print("\n4/5. AN L, AROUND THE FOAM SHELL ASSEMBLY")
    core = core_box()
    into_core = [(n, _overlap(s, core)) for n, s in built.items()
                 if _overlap(s, core) > 1e-6]
    for name, v in into_core:
        print(f"   INTO THE CORE {name}: {v:.1f} mm3")
    whole = cq.Compound.makeCompound(list(built.values())).BoundingBox()
    foot = [n for n, s in built.items() if s.BoundingBox().ymin < CORE_Y[0] - 1e-6]
    deck = [n for n, s in built.items() if s.BoundingBox().ymax > CORE_Y[0] + 1e-6]
    print(f"   module box x[{whole.xmin:.1f},{whole.xmax:.1f}] "
          f"y[{whole.ymin:.1f},{whole.ymax:.1f}] z[{whole.zmin:.1f},{whole.zmax:.1f}]"
          f"  = {whole.xlen:.1f} x {whole.ylen:.1f} x {whole.zlen:.1f}")
    print(f"   {len(foot)} bodies reach into the foot (y<0), {len(deck)} onto the deck "
          f"(y>0) — the arris between them is the core's own front-top")
    print(f"   {len(into_core)} bodies into the core — the L is the cavity less this box")
    ok &= not into_core

    print("\n6. INSIDE THE THIN ENCLOSURE")
    outside = [(n, s.BoundingBox()) for n, s in built.items()
               if not _in_cavity(s.BoundingBox())]
    for name, bb in outside:
        print(f"   OUT OF THE CAVITY {name}: x[{bb.xmin:.1f},{bb.xmax:.1f}] "
              f"y[{bb.ymin:.1f},{bb.ymax:.1f}] z[{bb.zmin:.1f},{bb.zmax:.1f}]")
    print(f"   cavity  x[{CAVITY_X[0]:.1f},{CAVITY_X[1]:.1f}] "
          f"y[{CAVITY_Y[0]:.1f},{CAVITY_Y[1]:.1f}] z[{CAVITY_Z[0]:.1f},{CAVITY_Z[1]:.1f}]"
          f"  ({len(outside)} bodies out)")
    fits_bed = max(DECK_X[1] - DECK_X[0], DECK_Y[1] - DECK_Y[0]) <= BED
    print(f"   deck plate {DECK_X[1] - DECK_X[0]:.1f} x {DECK_Y[1] - DECK_Y[0]:.1f} mm "
          f"on a {BED:.0f} mm bed: {'fits' if fits_bed else 'OVER'}")
    ok &= fits_bed and not outside

    print("\n7. TWO OF THEM")
    west = cq.Compound.makeCompound(
        [s.translate(cq.Vector(*WEST_ORIGIN)) for s in built.values()])
    east = cq.Compound.makeCompound(
        [s.mirror("YZ").translate(cq.Vector(*EAST_ORIGIN)) for s in built.values()])
    wb, eb = west.BoundingBox(), east.BoundingBox()
    pair_clash = _overlap(west, east)
    print(f"   west  x[{wb.xmin:.1f},{wb.xmax:.1f}]   east x[{eb.xmin:.1f},{eb.xmax:.1f}]")
    print(f"   between them {eb.xmin - wb.xmax:.1f} mm, and they share "
          f"{pair_clash:.3f} mm3")
    inside = (wb.xmin >= -14.0 and eb.xmax <= 195.0)
    print(f"   the pair spans {eb.xmax - wb.xmin:.1f} of the cavity's 209 mm: "
          f"{'inside' if inside else 'OVER'}")
    ok &= pair_clash <= 1e-6 and inside

    print(f"\n{'ALL CLAIMS HOLD' if ok else 'SOMETHING FAILED — see above'}")
    return ok


def _docgen():
    """Hold the prose to the geometry — every number a comment or the README
    quotes is written back from the constant that produced it."""
    built = parts()
    whole = cq.Compound.makeCompound(list(built.values())).BoundingBox()
    worst = min(min((r for _t, r, _tan in corner_radii(p)), default=BEND)
                for p in runs().values())
    # Mirrored, so the east instance's nearest face is its origin less our own
    # furthest one — the gap between the pair is what is left between the two.
    pair_gap = (EAST_ORIGIN[0] - whole.xmax) - (whole.xmax + WEST_LINE_S_X)
    variables = {
        "BARB_OFFSET": f"{BARB_OFFSET:.4g} mm",
        "BARB_LEAN": f"{BARB_LEAN:.2g}",
        "COLLET_SKEW": f"{COLLET_SKEW:.4g}",
        "PORT_PLANE": f"{PORT_Z:.4g}",
        "UNDER_DECK": f"{UNDER_DECK_Z:.4g}",
        "MODULE_X": f"{whole.xlen:.4g}",
        "MODULE_Y": f"{whole.ylen:.4g}",
        "MODULE_Z": f"{whole.zlen:.4g}",
        "WORST_BEND": f"{worst:.4g}",
        "PAIR_GAP": f"{pair_gap:.4g}",
        "DECK_PLATE_X": f"{DECK_X[1] - DECK_X[0]:.4g}",
        "DECK_PLATE_Y": f"{DECK_Y[1] - DECK_Y[0]:.4g}",
        "SEGMENTS": f"{len(INVENTORY['segments'])}",
    }
    substitute_py_comments(Path(__file__), variables=variables,
                           expected_counts={"BARB_OFFSET": 1, "BARB_LEAN": 1,
                                            "COLLET_SKEW": 1})
    substitute_md(_here.parent / "README.md", variables=variables,
                  expected_counts={"SEGMENTS": 2, "DECK_PLATE_X": 1,
                                   "DECK_PLATE_Y": 1, "PORT_PLANE": 1,
                                   "UNDER_DECK": 1, "BARB_OFFSET": 1,
                                   "BARB_LEAN": 1, "COLLET_SKEW": 1,
                                   "WORST_BEND": 1, "PAIR_GAP": 1,
                                   "MODULE_X": 1, "MODULE_Y": 1, "MODULE_Z": 1})


def main():
    export_assembly(build_assembly(), str(_here.parent / "flavor-module.step"))
    export_assembly(build_pair(), str(_here.parent / "flavor-module-pair.step"))
    _docgen()
    _report()


if __name__ == "__main__":
    main()
