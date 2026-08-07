"""Manifold layout — the ten flavor valves, both KPHM400 pumps and the eight junctions
between them, placed with nothing else in the box.

Nothing here is seated in the enclosure, no tray carries anything, and no reservoir, nozzle,
hopper or carbonator is present: the six mouths that reach them are drawn one stub long and
stop. The connections are `../topology/fluid-topology.md`'s, with one difference — each
reservoir has ONE port here and meets its channel's fill and draw gates at a junction, so
segments 24, 25 and 26 mirror 14, 15 and 16. The machine gives reservoir B two mouths of its
own instead. What is free is where every body stands, how it is turned, and which of a
junction's three ports takes its run.

Frame
-----
- X = width, mirrored about x = 0. Channel A (pump B) west, channel B (pump A) east.
- Y = depth. −Y is the front: the tap, the hopper and both nozzles leave that way.
  +Y is the back: both reservoir lines leave that way.
- Z = height, 0 at the pumps' own floor. The valves stand on one deck above them.

The arrangement
---------------
Each pump's two barbs stand `BARB_PITCH` apart on one face, both facing the same way. A tee
dropped on a barb by its BRANCH puts its RUN across that face, so one pump hands out two
parallel lanes, `BARB_PITCH` apart, one `TEE_BRANCH` off its own skin. Every valve is a
straight-through body and every junction's run takes two valve ports, so a lane is one line of
valves and tees butted collet to collet — and the two channels are the same line mirrored:

    A1  V-A · Y-A · V-C · Y-C · V-E          B1  V-B · Y-B · V-D · Y-F · V-H
    A2        V-G · Y-D · V-F · Y-E          B2        V-J · Y-G · V-I · Y-H

Y-C, Y-D, Y-F and Y-G sit on the four barbs. Y-A and Y-B stand on the two INNER limbs' own
axes, one valve forward of the selects they feed, and their branches meet face to face across
the mirror plane. Y-E and Y-H stand at the far end of the OUTER limbs behind the fill gates,
each carrying its reservoir's own line out the back on its run and crossing the pump on its
branch to the draw gate, which an elbow on that collet turns onto.

Every other connection is collet butted to collet. No run in this arrangement turns: the
tightest centreline radius 1/4" LLDPE takes is `MIN_BEND`, and no corner is drawn at all.

`BUTT` is the tube left OUTSIDE a pair of butted quick-connects, and it is 0 — there is still
tube in both collets, there is none between them. `BARB_STANDOFF` is the same figure where a
tee meets a pump barb, and it is 0 as well; a barb is not a quick-connect, and the deck's
height rides on this number one for one.

The envelope, the deck, the two tube lengths, the mirror check and the clash check are in
`README.md`, written back by this file, and printed by every run.

Run it
------
    tools/cad-venv/bin/python hardware/manifold-layout/manifold_layout.py
    HSM_LIMB_PITCH=34.25 tools/cad-venv/bin/python hardware/manifold-layout/manifold_layout.py
"""

import hashlib
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
_tools = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"
_edition = "kitchen" if _repo == _tools.parent else _repo.name
for _p in (_hw / "scripts",
           _hw / "reference" / "beduan-solenoid",
           _hw / "reference" / "tee-connector",
           _hw / "reference" / "y-divider",
           _hw / "reference" / "kamoer-kphm400",
           _hw / "printed-parts" / "cadlib",
           _hw / "printed-parts" / "flavor" / "pump-case"):
    sys.path.insert(0, str(_p))
sys.path.insert(0, str(_tools))
from _cadq_export import export_assembly              # noqa: E402
from docgen import substitute_md                      # noqa: E402
import beduan_solenoid as vlv                         # noqa: E402
import kamoer_kphm400 as kp                           # noqa: E402
import tee_connector as tee                           # noqa: E402
import y_divider as ydiv                              # noqa: E402

ELBOW_STEP = _hw / "reference" / "elbow-connector" / "elbow-connector.step"
TEE_STEP = _hw / "reference" / "tee-connector" / "tee-connector.step"

# --- The parts' own figures ------------------------------------------------
VALVE_LEN = vlv.port_length                  # collet face to collet face
VALVE_PITCH = vlv.body_width_x               # the X keep-out two valves pack to
VALVE_PORT_Z = vlv.port_center_z             # port axis over the valve's own mounting plane
VALVE_TOP_Z = vlv.coil_z_range[1]            # coil crown over that same plane
TEE_RUN = tee.RUN_HALF                       # run collet face from the tee's centre
TEE_BRANCH = tee.BRANCH_REACH                # branch collet face from the same centre
TUBE_D = tee.TUBE_D                          # the 1/4" OD LLDPE every port takes
MIN_BEND = 25.4                              # 1/4" LLDPE's tightest centreline radius
                                             # (`enclosure-assembly/scorecard.py` STOCKS)
FLAVOR_SKEW = 22.0                           # degrees off a collet's own axis a straight tube
                                             # still enters it unbent (`_contents.FLAVOR_SKEW`)

HEAD_W = kp.head_w                           # the pump head, square across
HEAD_D = kp.head_depth                       # head front face to the bracket
MOTOR_D = kp.motor_dia
PUMP_LEN = 111.43                            # head front to motor end cap, no shaft nub
BRACKET_W = 68.6                             # the mounting bracket, ~3 mm proud per side in X
BRACKET_T = 2.0
BARB_PITCH = kp.arch_xs[1] - kp.arch_xs[0]   # the two barbs' separation across the head face
BARB_INSET = kp.arch_plane_z - kp.head_front_z   # barb plane back from the head's front face

# --- The study's own figures, all four free --------------------------------
BUTT = 0.0            # tube left outside a pair of butted quick-connects
BARB_STANDOFF = 0.0   # the climb a barb is given over and above what `LIMB_PITCH` demands.
                      # A barb is not a quick-connect, so 0 here is a modelling convenience
                      # rather than a fact; the deck rides on it one millimetre for one.
CROSSBAR = 0.0        # exposed tube between Y-A's and Y-B's branches. At 0 the two fittings
                      # meet face to face across the mirror plane and no tube is drawn.
# The two lanes one pump hands out. At `BARB_PITCH` each tee sits on its own barb and the
# connection is a butt. Below it both tees step toward the pump's axis and each barb reaches
# its tee on one straight leaning tube — which is what the deck then has to climb to carry.
# `HSM_LIMB_PITCH` sets it for a run without editing, so the trade is a build and not arithmetic.
LIMB_PITCH = float(os.environ.get("HSM_LIMB_PITCH", BARB_PITCH))

# --- What follows from them ------------------------------------------------
# The inner limbs are what the crossbar spans, so THEY are what it places: each stands one
# branch reach and half a crossbar off the mirror plane, and the pumps hang off them.
INNER_X = TEE_BRANCH + CROSSBAR / 2.0        # the inner limbs' axes
PUMP_DX = INNER_X + LIMB_PITCH / 2.0         # each pump's centre off the mirror plane
OUTER_X = PUMP_DX + LIMB_PITCH / 2.0         # the outer limbs'
LIMB_STEP = (BARB_PITCH - LIMB_PITCH) / 2.0  # how far a tee steps toward its pump's own axis,
                                             # off the barb's column, when the pitch is closed
# One straight tube leaning `LIMB_STEP` across as it climbs enters both its mouths at
# `atan(LIMB_STEP / climb)`, so the climb the skew allows is the floor under the lead.
BARB_LEAD_FLOOR = LIMB_STEP / math.tan(math.radians(FLAVOR_SKEW))
BARB_LEAD = BARB_LEAD_FLOOR + BARB_STANDOFF
DECK_Z = HEAD_W + BARB_LEAD + TEE_BRANCH     # the four limbs' shared port-axis height
STUB = MIN_BEND                              # what a free mouth is drawn reaching, so the
                                             # first corner past it has a leg to seat in

ELBOW_LEG = 19.56                            # bend corner to collet face, both legs

if CROSSBAR < 0.0:
    raise ValueError(
        f"CROSSBAR {CROSSBAR:g} would stand Y-A's and Y-B's branch collets past each other, so "
        f"the two fittings occupy the same tube.")
if 2.0 * INNER_X < VALVE_PITCH:
    raise ValueError(
        f"CROSSBAR {CROSSBAR:g} puts the inner limbs {2 * INNER_X:.2f} mm apart, under the "
        f"{VALVE_PITCH:g} mm two valve bodies pack to — V-A and V-B would occupy each other.")

if LIMB_PITCH < VALVE_PITCH:
    raise ValueError(
        f"LIMB_PITCH {LIMB_PITCH:g} is under the {VALVE_PITCH:g} mm two valve bodies pack to, so "
        f"the two lanes' valves would occupy each other.")
if LIMB_PITCH > BARB_PITCH:
    raise ValueError(
        f"LIMB_PITCH {LIMB_PITCH:g} is over the {BARB_PITCH:g} mm barb pitch — the lanes would "
        f"stand outboard of the barbs and this file only draws the step inward.")

# --- Colours ---------------------------------------------------------------
C_VALVE = cq.Color(0.93, 0.93, 0.91)
C_COIL = cq.Color(0.20, 0.20, 0.23)
C_TEE = cq.Color(0.12, 0.12, 0.14)
C_HEAD = cq.Color(0.16, 0.16, 0.18)
C_BRACKET = cq.Color(0.35, 0.36, 0.38)
C_MOTOR = cq.Color(0.74, 0.76, 0.80)
C_TUBE = cq.Color(0.85, 0.88, 0.92)
C_STUB = cq.Color(0.62, 0.70, 0.78)


# --- Placement -------------------------------------------------------------

def place(solid, origin, x_dir, z_dir):
    """A solid moved out of its own frame into the world: its local +X onto `x_dir`, its
    local +Z onto `z_dir`, its local origin onto `origin`. Local +Y follows as z × x."""
    return solid.moved(cq.Location(cq.Plane(origin=origin, xDir=x_dir, normal=z_dir)))


def valve_dirs(flow: int):
    """A valve standing coil-up with its flow along world ±Y, as (x_dir, z_dir). The body's
    own +Y is its flow axis — inlet at −Y, outlet at +Y, the way the boss arrow points."""
    return (float(flow), 0.0, 0.0), (0.0, 0.0, 1.0)


def tee_dirs(branch):
    """A tee whose RUN lies along world Y and whose BRANCH faces `branch`, as (x_dir, z_dir).
    The fitting's own run is its local Z and its branch its local +Y."""
    bx, _by, bz = branch
    if bz:
        return (1.0, 0.0, 0.0), (0.0, 1.0, 0.0) if bz < 0 else (0.0, -1.0, 0.0)
    return (0.0, 0.0, bx), (0.0, 1.0, 0.0)


# --- The chains ------------------------------------------------------------
#
# Each limb is one line of bodies butted end to end, front to back. A valve is
# ("V-x", flow) with flow +1 running aft and −1 running forward; a tee is ("Y-x", branch).
# `anchor` is the index of the tee that sits on a pump barb — the body the whole chain is
# hung off, at y = 0. The inner limb takes its pump's draw barb, the outer limb the discharge.

LIMBS = {
    "A1": dict(x=-INNER_X, anchor=3, chain=[
        ("V-A", +1), ("Y-A", (+1.0, 0.0, 0.0)), ("V-C", +1),
        ("Y-C", (0.0, 0.0, -1.0)), ("V-E", -1)]),
    "A2": dict(x=-OUTER_X, anchor=1, chain=[
        ("V-G", -1), ("Y-D", (0.0, 0.0, -1.0)), ("V-F", +1),
        ("Y-E", (+1.0, 0.0, 0.0))]),
    "B1": dict(x=+INNER_X, anchor=3, chain=[
        ("V-B", +1), ("Y-B", (-1.0, 0.0, 0.0)), ("V-D", +1),
        ("Y-F", (0.0, 0.0, -1.0)), ("V-H", -1)]),
    "B2": dict(x=+OUTER_X, anchor=1, chain=[
        ("V-J", -1), ("Y-G", (0.0, 0.0, -1.0)), ("V-I", +1),
        ("Y-H", (-1.0, 0.0, 0.0))]),
}

PUMPS = {"pump-b": -PUMP_DX, "pump-a": +PUMP_DX}   # channel A west, channel B east

# The barb each anchor tee is fed by, as (pump centre, which of the two barbs).
BARB_OF = {"Y-C": (-PUMP_DX, +1), "Y-D": (-PUMP_DX, -1),
           "Y-F": (+PUMP_DX, -1), "Y-G": (+PUMP_DX, +1)}


def barb_station(tee: str) -> tuple:
    """A pump barb's collet plane, in world. It stands on the head's crown at the limb's own
    y, offset `BARB_PITCH/2` either side of the pump's centre."""
    px, side = BARB_OF[tee]
    return (px + side * BARB_PITCH / 2.0, 0.0, HEAD_W)


def _half(name: str) -> float:
    """Half a body's own length along the limb, collet face to centre."""
    return VALVE_LEN / 2.0 if name.startswith("V-") else TEE_RUN


def lay_out() -> dict:
    """Every body's centre and both its collet faces along its limb, keyed by name.

    A chain is butted: each body's near collet face sits `BUTT` past its neighbour's far one.
    The anchor tee's centre is pinned at y = 0 — the plane its pump's barbs stand on — and the
    rest of the chain falls out either side of it."""
    out = {}
    for limb, spec in LIMBS.items():
        names = [n for n, _ in spec["chain"]]
        centres, y = [], 0.0
        for n in names:                                  # forward pass from the chain's nose
            centres.append(y + _half(n))
            y = centres[-1] + _half(n) + BUTT
        shift = -centres[spec["anchor"]]
        for (n, arg), c in zip(spec["chain"], centres):
            out[n] = dict(limb=limb, x=spec["x"], y=c + shift, arg=arg,
                          front=c + shift - _half(n), back=c + shift + _half(n))
    return out


P = lay_out()


def port(name: str, end: str):
    """A named body's collet face at one end of its limb: ("front"|"back"), as a world point."""
    b = P[name]
    return (b["x"], b[end], DECK_Z)


def branch_port(name: str):
    """A tee's branch collet face, as (point, outward axis)."""
    b, d = P[name], P[name]["arg"]
    return (b["x"] + d[0] * TEE_BRANCH, b["y"], DECK_Z + d[2] * TEE_BRANCH), d


# Each reservoir meets its channel's two gates at one junction standing in line behind the FILL
# gate, on the outer limb: the tee's run carries the fill leg and the reservoir's own line, and
# its branch crosses the pump to the DRAW gate on the inner limb. The draw gate faces down its
# own limb, so an elbow on that collet turns it onto the branch's axis. The pair is the whole
# mirror — reservoir A at Y-E off V-F, reservoir B at Y-H off V-I.
#
# Elbow corner one leg behind the draw gate, second leg opening across at the tee. The two axes
# are offset by `ELBOW_LEG` against `TEE_RUN`, which the run reads out as a collet skew.
JOINS = {"Y-E": ("V-E", -1.0), "Y-H": ("V-H", +1.0)}


def elbow_pose(gate: str, side: float) -> tuple:
    """The elbow on a draw gate's collet: (corner, mouth, x_dir, z_dir). Leg 1 runs back down
    the limb onto the gate; leg 2 opens across the pump, `side` picking which way."""
    corner = (P[gate]["x"], P[gate]["back"] + ELBOW_LEG, DECK_Z)
    mouth = (corner[0] + side * ELBOW_LEG, corner[1], corner[2])
    return corner, mouth, (0.0, 0.0, side), (side, 0.0, 0.0)


# --- Bodies ----------------------------------------------------------------

def build_valve(name: str):
    b = P[name]
    x_dir, z_dir = valve_dirs(b["arg"])
    origin = (b["x"], b["y"], DECK_Z - VALVE_PORT_Z)
    body = place(vlv.build_body().union(vlv.build_port()).union(vlv.build_arrow()).val(),
                 origin, x_dir, z_dir)
    coil = place(cq.Compound.makeCompound([vlv.build_coil().val()] +
                                          [s.val() for s in vlv.build_spades()]),
                 origin, x_dir, z_dir)
    return body, coil


def build_tee(name: str):
    b = P[name]
    x_dir, z_dir = tee_dirs(b["arg"])
    solid = cq.importers.importStep(str(TEE_STEP)).val()
    return place(solid, (b["x"], b["y"], DECK_Z), x_dir, z_dir)


def build_elbow(gate: str, side: float):
    """One draw gate's elbow. Native frame: legs out +Y and +Z, bend corner at the origin."""
    corner, _mouth, x_dir, z_dir = elbow_pose(gate, side)
    solid = cq.importers.importStep(str(ELBOW_STEP)).val()
    return place(solid, corner, x_dir, z_dir)


def build_pump(px: float):
    """Head, bracket and motor as three solids, the head's floor at z = 0 and its front face
    at y = −BARB_INSET so both barbs stand on the plane the limbs' anchor tees do."""
    y0 = -BARB_INSET
    head = cq.Solid.makeBox(HEAD_W, HEAD_D, HEAD_W, cq.Vector(px - HEAD_W / 2, y0, 0.0))
    bracket = cq.Solid.makeBox(BRACKET_W, BRACKET_T, HEAD_W,
                               cq.Vector(px - BRACKET_W / 2, y0 + HEAD_D, 0.0))
    motor = cq.Solid.makeCylinder(
        MOTOR_D / 2.0, PUMP_LEN - HEAD_D - BRACKET_T,
        cq.Vector(px, y0 + HEAD_D + BRACKET_T, HEAD_W / 2.0), cq.Vector(0.0, 1.0, 0.0))
    return head, bracket, motor


def straight(a, b, d: float = TUBE_D):
    """One length of tube between two collet faces."""
    v = cq.Vector(*[b[i] - a[i] for i in range(3)])
    return cq.Solid.makeCylinder(d / 2.0, v.Length, cq.Vector(*a), v.normalized())


# --- The lines -------------------------------------------------------------
#
# Every connection `fluid-topology.md` names between the bodies in this study, and how it is
# made. A BUTT is two collet faces meeting: there is tube in both quick-connects and none
# between them, so the study draws no solid for it. The other two are straight lengths.

RUNS = {"crossbar": (branch_port("Y-A")[0], branch_port("Y-B")[0])}
RUNS.update({t: (barb_station(t), branch_port(t)[0]) for t in BARB_OF})
RUNS.update({t: (branch_port(t)[0], elbow_pose(*JOINS[t])[1]) for t in JOINS})

SEGMENTS = [
    (3, "V-A-O", "Y-A-1", "butt"), (5, "V-B-O", "Y-B-1", "butt"),
    (6, "Y-A-3", "Y-B-3", "crossbar"),
    (7, "Y-A-2", "V-C-I", "butt"), (8, "Y-B-2", "V-D-I", "butt"),
    (9, "V-C-O", "Y-C-1", "butt"), (10, "V-E-O", "Y-C-2", "butt"),
    (11, "Y-C-3", "P-B-I", "Y-C"), (12, "P-B-O", "Y-D-1", "Y-D"),
    (13, "Y-D-2", "V-F-I", "butt"), (14, "V-F-O", "Y-E-1", "butt"),
    (16, "Y-E-3", "V-E-I", "Y-E"), (17, "Y-D-3", "V-G-I", "butt"),
    (19, "V-D-O", "Y-F-1", "butt"), (20, "V-H-O", "Y-F-2", "butt"),
    (21, "Y-F-3", "P-A-I", "Y-F"), (22, "P-A-O", "Y-G-1", "Y-G"),
    (23, "Y-G-3", "V-I-I", "butt"), (24, "V-I-O", "Y-H-1", "butt"),
    (26, "Y-H-3", "V-H-I", "Y-H"), (27, "Y-G-2", "V-J-I", "butt"),
]

# The seven mouths that leave this study. Each is drawn one `STUB` along its own axis, which is
# the straight its first corner needs before it can turn at all.
MOUTHS = [
    ("fluid-2", "V-A-I", "tap water in", port("V-A", "front"), (0.0, -1.0, 0.0)),
    ("fluid-4", "V-B-I", "hopper in", port("V-B", "front"), (0.0, -1.0, 0.0)),
    ("fluid-18", "V-G-O", "nozzle A", port("V-G", "front"), (0.0, -1.0, 0.0)),
    ("fluid-28", "V-J-O", "nozzle B", port("V-J", "front"), (0.0, -1.0, 0.0)),
    ("fluid-15", "Y-E-2", "reservoir A", port("Y-E", "back"), (0.0, 1.0, 0.0)),
    ("fluid-25", "Y-H-2", "reservoir B", port("Y-H", "back"), (0.0, 1.0, 0.0)),
]


def build_assembly() -> cq.Assembly:
    a = cq.Assembly(name="manifold-layout")
    for name in P:
        if name.startswith("V-"):
            body, coil = build_valve(name)
            a.add(body, name=f"valve-{name.lower()}", color=C_VALVE)
            a.add(coil, name=f"coil-{name.lower()}", color=C_COIL)
        else:
            a.add(build_tee(name), name=f"tee-{name.lower()}", color=C_TEE)
    for tee, (gate, side) in JOINS.items():
        a.add(build_elbow(gate, side), name=f"elbow-{gate.lower()}-i", color=C_TEE)
    for pname, px in PUMPS.items():
        head, bracket, motor = build_pump(px)
        a.add(head, name=f"{pname}-head", color=C_HEAD)
        a.add(bracket, name=f"{pname}-bracket", color=C_BRACKET)
        a.add(motor, name=f"{pname}-motor", color=C_MOTOR)
    # Only the segments that carry tube outside their collets get a solid; the rest are butts.
    for cid, _f, _t, how in SEGMENTS:
        if how in RUNS and dist(*RUNS[how]) > 1e-9:
            a.add(straight(*RUNS[how]), name=f"tube-fluid-{cid}", color=C_TUBE)
    for cid, _p, _what, p, axis in MOUTHS:
        a.add(straight(p, tuple(p[i] + axis[i] * STUB for i in range(3))),
              name=f"stub-{cid}", color=C_STUB)
    return a


# --- Controls --------------------------------------------------------------

def clashes(assy: cq.Assembly, floor: float = 1.0):
    """Every pair of placed solids that shares more than `floor` mm³, and every pair the boolean
    would not answer for. Butted collets meet on a plane and share nothing, so a clean
    arrangement returns two empty lists — and a pair OCCT raised on lands in the second one
    rather than passing for clean."""
    solids = [(c.name, (c.obj.val() if hasattr(c.obj, "val") else c.obj)
               .moved(cq.Location(c.loc.wrapped.Transformation()))) for c in assy.children]
    boxes = [(n, s, s.BoundingBox()) for n, s in solids]
    hits, unanswered = [], []
    for i in range(len(boxes)):
        ni, si, bi = boxes[i]
        for j in range(i + 1, len(boxes)):
            nj, sj, bj = boxes[j]
            if (bi.xmin > bj.xmax - 1e-6 or bj.xmin > bi.xmax - 1e-6
                    or bi.ymin > bj.ymax - 1e-6 or bj.ymin > bi.ymax - 1e-6
                    or bi.zmin > bj.zmax - 1e-6 or bj.zmin > bi.zmax - 1e-6):
                continue
            try:
                v = si.intersect(sj).Volume()
            except Exception as exc:
                unanswered.append((ni, nj, str(exc).splitlines()[0]))
                continue
            if v > floor:
                hits.append((ni, nj, v))
    return hits, unanswered


def envelope(assy: cq.Assembly, stubs: bool):
    """The pack's box. Without `stubs` it is the bodies and the tube between them — what has to
    be found room for. With them it adds one bend radius off each of the seven mouths, which is
    the straight whatever routes them next has to leave in."""
    box = None
    for c in assy.children:
        if not stubs and c.name.startswith("stub-"):
            continue
        s = c.obj.val() if hasattr(c.obj, "val") else c.obj
        b = s.moved(cq.Location(c.loc.wrapped.Transformation())).BoundingBox()
        box = b if box is None else box.add(b)
    return box


# Channel A's body and channel B's, for every one that has a twin. A mirrored pack puts each
# pair at ±x on one y and one z; `mirror_off` is how far it misses by.
TWINS = [("V-A", "V-B"), ("V-C", "V-D"), ("V-E", "V-H"), ("V-F", "V-I"), ("V-G", "V-J"),
         ("Y-A", "Y-B"), ("Y-C", "Y-F"), ("Y-D", "Y-G"), ("Y-E", "Y-H")]


def mirror_off() -> list:
    """Per twinned pair, how far the arrangement is from mirror-symmetric about x = 0: the two
    x's that should sum to zero, and the y they should share."""
    out = []
    for a, b in TWINS:
        out.append((a, b, abs(P[a]["x"] + P[b]["x"]), abs(P[a]["y"] - P[b]["y"])))
    out.append(("pump-b", "pump-a", abs(PUMPS["pump-b"] + PUMPS["pump-a"]), 0.0))
    return out


def dist(a, b) -> float:
    return sum((a[i] - b[i]) ** 2 for i in range(3)) ** 0.5


def skew_deg(a, b, axis) -> float:
    import math
    v = [b[i] - a[i] for i in range(3)]
    m = sum(c * c for c in v) ** 0.5
    dot = sum(v[i] * axis[i] for i in range(3)) / m
    return math.degrees(math.acos(max(-1.0, min(1.0, dot))))


ELEVATIONS = "top,front,right"


def render_elevations(step: Path) -> None:
    """Plan, front and right beside the STEP — the same three `enclosure-assembly` draws, and
    for the same reason: an isometric thumbnail cannot be read off with a ruler."""
    if os.environ.get("HSM_SKIP_VIEWS"):
        return
    stamp = step.with_name(f".{step.stem}.views.sha")
    drawn = [step.with_suffix("").with_suffix(f".{v}.png") for v in ELEVATIONS.split(",")]
    digest = hashlib.sha256(step.read_bytes()).hexdigest()
    try:
        if stamp.read_text().strip() == digest and all(p.is_file() for p in drawn):
            print("  (elevations unchanged)")
            return
    except OSError:
        pass
    node, tool = shutil.which("node"), _tools / "render" / "render-view.js"
    if node is None or not tool.is_file():
        print("  (elevations skipped: no render tool)")
        return
    try:
        r = subprocess.run(
            [node, str(tool), str(step.relative_to(_repo / "hardware")),
             str(step.with_suffix(".png")), "--edition", _edition,
             "--views", ELEVATIONS, "--ortho", "--size", "1600x1200"],
            cwd=str(_tools.parent), stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            timeout=900, check=False)
        if r.returncode:
            print(f"  (elevations skipped: render-view exited {r.returncode})")
            return
    except Exception as exc:
        print(f"  (elevations skipped: {exc})")
        return
    try:
        stamp.write_text(digest + "\n")
    except OSError:
        pass
    for v in ELEVATIONS.split(","):
        print(f"-> manifold-layout.{v}.png")


def report(assy: cq.Assembly) -> dict:
    bb, reach = envelope(assy, stubs=False), envelope(assy, stubs=True)
    print("\nlimbs (front → back, y at each body's centre)")
    for limb, spec in LIMBS.items():
        row = "  ".join(f"{n}@{P[n]['y']:+.1f}" for n, _ in spec["chain"])
        print(f"  {limb}  x{LIMBS[limb]['x']:+7.2f}   {row}")

    made = {k: dist(*v) for k, v in RUNS.items()}
    print(f"\n{len(SEGMENTS)} connections")
    for cid, frm, to, how in SEGMENTS:
        length = made.get(how, 0.0)
        note = ("butt — 0 mm outside the collets" if length < 1e-9
                else f"{length:.2f} mm straight" + (" + one 90° elbow" if how in JOINS else ""))
        print(f"  fluid-{cid:<3} {frm:>7} → {to:<7}  {note}")
    print(f"\n{len(MOUTHS)} mouths leave the study")
    for cid, p, what, (x, y, z), axis in MOUTHS:
        print(f"  {cid:<9} {p:>7}  ({x:7.2f}, {y:7.2f}, {z:6.2f})  "
              f"{'front' if axis[1] < 0 else 'back':>5}  {what}")

    print(f"\nenvelope  X {bb.xlen:7.2f}   Y {bb.ylen:7.2f}   Z {bb.zlen:7.2f}    "
          f"({bb.xlen * bb.ylen * bb.zlen / 1e6:.2f} L)   bodies and the tube between them")
    print(f"          x[{bb.xmin:7.2f}, {bb.xmax:7.2f}]  y[{bb.ymin:7.2f}, {bb.ymax:7.2f}]  "
          f"z[{bb.zmin:7.2f}, {bb.zmax:7.2f}]")
    print(f"          X {reach.xlen:7.2f}   Y {reach.ylen:7.2f}   Z {reach.zlen:7.2f}    "
          f"({reach.xlen * reach.ylen * reach.zlen / 1e6:.2f} L)   with one {STUB:g} mm mouth "
          f"stub on each of the {len(MOUTHS)}")
    print(f"deck at z {DECK_Z:.2f}, {DECK_Z - VALVE_PORT_Z - HEAD_W:.2f} mm over the pump heads; "
          f"each mm of BARB_LEAD lifts it one")
    print(f"LIMB_PITCH {LIMB_PITCH:g} of a {BARB_PITCH:g} barb pitch — each tee stands "
          f"{LIMB_STEP:.2f} mm off its barb's column on a {BARB_LEAD:.2f} mm lead, which is the "
          f"climb {FLAVOR_SKEW:g}° of skew asks for. HSM_LIMB_PITCH= builds another.")
    print(f"crossbar {CROSSBAR:.2f} mm exposed; the two reservoir crossings enter their collets "
          + ", ".join(f"{skew_deg(*RUNS[t], branch_port(t)[1]):.1f}°" for t in JOINS)
          + " off axis")
    print(f"corners: 0, against a {MIN_BEND:g} mm floor for the stock")

    off = mirror_off()
    worst = max(max(dx, dy) for _a, _b, dx, dy in off)
    print(f"\nmirror about x=0: {len(off)} twinned pairs, worst off by {worst:.4f} mm")
    for a, b, dx, dy in off:
        if max(dx, dy) > 1e-6:
            print(f"  {a} / {b}   x sums to {dx:.4f}, y differs by {dy:.4f}")

    bad, unanswered = clashes(assy)
    print(f"\nclash check: {len(bad)} pair(s) sharing volume, "
          f"{len(unanswered)} the boolean would not answer for")
    for ni, nj, v in bad:
        print(f"  {ni} ∩ {nj}   {v:.1f} mm³")
    for ni, nj, why in unanswered:
        print(f"  {ni} ? {nj}   {why}")
    return dict(bb=bb, reach=reach, bad=bad + unanswered, made=made, mirror=off)


def main():
    assy = build_assembly()
    out = _here.parent / "manifold-layout.step"
    export_assembly(assy, str(out))
    print(f"-> {out.name}")
    r = report(assy)
    bb, reach = r["bb"], r["reach"]
    substitute_md(
        _here.parent / "README.md",
        variables={
            "ENV_X": f"{bb.xlen:.0f}", "ENV_Y": f"{bb.ylen:.0f}", "ENV_Z": f"{bb.zlen:.0f}",
            "ENV_L": f"{bb.xlen * bb.ylen * bb.zlen / 1e6:.2f}",
            "REACH_X": f"{reach.xlen:.0f}", "REACH_Y": f"{reach.ylen:.0f}",
            "REACH_Z": f"{reach.zlen:.0f}", "STUB_LEN": f"{STUB:g}",
            "DECK_Z": f"{DECK_Z:.2f}", "DECK_Z2": f"{DECK_Z:.2f}",
            "DECK_GAP": f"{DECK_Z - VALVE_PORT_Z - HEAD_W:.2f}",
            "CROSSBAR": f"{CROSSBAR:.2f}", "F16_LEN": f"{r['made']['Y-E']:.2f}",
            "TEE_COUNT": str(sum(1 for n in P if n.startswith("Y-"))),
            "TEE_COUNT2": str(sum(1 for n in P if n.startswith("Y-"))),
            "ELBOW_COUNT": str(len(JOINS)),
            "TUBE_COUNT2": str(sum(1 for s in SEGMENTS if r["made"].get(s[3], 0.0) >= 1e-9)),
            "TWIN_COUNT": str(len(r["mirror"])),
            "MIRROR_OFF": f"{max(max(dx, dy) for _a, _b, dx, dy in r['mirror']):.4f}",
            "JOIN_SKEW": f"{skew_deg(*RUNS['Y-E'], branch_port('Y-E')[1]):.1f}",
            "SEGMENT_COUNT": str(len(SEGMENTS)),
            # A butt is a segment whose drawn length is zero, whoever its two ends are — so
            # closing LIMB_PITCH moves four of them out of this count and into TUBE_COUNT.
            "BUTT_COUNT": str(sum(1 for s in SEGMENTS if r["made"].get(s[3], 0.0) < 1e-9)),
            "TUBE_COUNT": str(sum(1 for s in SEGMENTS if r["made"].get(s[3], 0.0) >= 1e-9)),
            "MOUTH_COUNT": str(len(MOUTHS)),
            "MIN_BEND": f"{MIN_BEND:g}",
            "BARB_PITCH": f"{BARB_PITCH:g}", "BARB_PITCH2": f"{BARB_PITCH:g}",
            "BARB_INSET": f"{BARB_INSET:g}",
            "VALVE_PITCH": f"{VALVE_PITCH:g}", "VALVE_PORT_Z": f"{VALVE_PORT_Z:g}",
            "VALVE_LEN": f"{VALVE_LEN:g}",
            "TEE_RUN": f"{TEE_RUN:g}", "TEE_SPAN": f"{2 * TEE_RUN:g}",
            "ELBOW_LEG": f"{ELBOW_LEG:g}",
            "DIVIDER_PITCH": f"{2 * ydiv.OUTLET_Y:g}",
            "LIMB_OUT_XW": f"{-OUTER_X:.2f}", "LIMB_IN_XW": f"{-INNER_X:.2f}",
            "LIMB_IN_XE": f"{INNER_X:+.2f}", "LIMB_OUT_XE": f"{OUTER_X:+.2f}",
            "INNER_GAP": f"{2 * INNER_X - VALVE_PITCH:.2f}",
            "CLASHES": str(len(r["bad"])),
        },
        expected_counts={
            "ENV_X": 1, "ENV_Y": 1, "ENV_Z": 1, "ENV_L": 1,
            "REACH_X": 1, "REACH_Y": 1, "REACH_Z": 1, "STUB_LEN": 1,
            "DECK_Z": 1, "DECK_Z2": 1, "DECK_GAP": 1, "CROSSBAR": 1, "F16_LEN": 1,
            "TEE_COUNT": 1, "TEE_COUNT2": 1, "ELBOW_COUNT": 1, "TUBE_COUNT2": 1,
            "TWIN_COUNT": 1, "MIRROR_OFF": 1, "JOIN_SKEW": 1,
            "SEGMENT_COUNT": 1, "BUTT_COUNT": 1, "TUBE_COUNT": 1, "MOUTH_COUNT": 1,
            "MIN_BEND": 1,
            "BARB_PITCH": 1, "BARB_PITCH2": 1, "BARB_INSET": 1,
            "VALVE_PITCH": 1, "VALVE_PORT_Z": 1, "VALVE_LEN": 1,
            "TEE_RUN": 1, "TEE_SPAN": 1, "ELBOW_LEG": 1, "DIVIDER_PITCH": 1,
            "LIMB_OUT_XW": 1, "LIMB_IN_XW": 1, "LIMB_IN_XE": 1, "LIMB_OUT_XE": 1,
            "INNER_GAP": 1, "CLASHES": 1,
        },
    )
    print("-> README.md")
    render_elevations(out)


if __name__ == "__main__":
    main()
