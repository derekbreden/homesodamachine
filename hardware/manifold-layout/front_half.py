"""Front half — the refrigeration stratum, the flavor manifold standing on it, and the cold
core behind the pair.

Four bodies, mated face to face with nothing between them:

    compressor-shroud   its INTAKE-side face against
    condenser+fan       turned onto it, and the pair yawed as one by `BASE_YAW`
    manifold-layout     set down on the crown of those two, on the four SPINE HAIRPINS
    foam-assembly       at the machine's own `FOAM_YAW`, on the floor, its front face on the
                        plane the front half ends at

The gaps are 0 by intent, and the mating is what closes the refrigerant loop. The compressor
stands well inside its shroud and its stubs go wherever they are put; the condenser is an
envelope whose serpentine headers are re-dressed to reach whichever face is convenient; the
cold core's front wall has a lane on each side of it and each lane carries one of the
evaporator's coppers. So all three of the loop's joints cross a plane two of these bodies
already share, both stations of each are ONE POINT READ TWICE, and no copper is drawn between
any two of them — `refrigerant_joints` measures all three at every build and
`check_refrigerant_joints` fails the build when one opens.

Frame
-----
- X = width, everything centred on x = 0 — the manifold is mirror-symmetric about it.
- Y = depth, 0 at the front. The refrigeration base, then the cold core behind it; on the
  base, the manifold's pumps forward and its two valve decks aft.
- Z = height, 0 at the floor the shroud and the core both stand on.

What the mating does to each body
---------------------------------
The **shroud** keeps the machine's own `SHROUD_YAW`: the compressor is a can whose oil sits
in its bottom and whose pickup is gravity-fed, so upright is the compressor's constraint and
the turn can only be a yaw.

The **condenser** turns a quarter about Z to bring its west face onto the shroud's aft plane.
That carries its `AIRFLOW` axis with it — across the machine before, front-to-back after — so
the air crosses the cabinet the short way and the finstack faces the two side walls.

The **manifold** turns a quarter about X and a half about Z, which is the one pose that lays
its pump-head front face down. Its own +Z — the axis its two valve decks stack on — comes to
+Y, so the decks stand aft of the pumps rather than over them, and every mouth that faced the
back now faces up.

What it then sets down ON is the four spine hairpins, not any body: the fold put them on the
pack's own underside and they reach past the pump-head faces. They sit at the AFT end, under
the valve decks, where the pumps are forward — so the pack rests on four tube arcs and the
pump faces stand clear of the crown by what the hairpins reach.

Run it
------
    tools/cad-venv/bin/python hardware/manifold-layout/front_half.py
"""

import collections
import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts", _here.parent,
           _hw / "cut-parts" / "compressor-shroud",
           _hw / "reference" / "condenser-block",
           _hw / "printed-parts" / "cadlib",
           _hw / "printed-parts" / "zone-c" / "hopper-funnel",
           _hw / "reference" / "seaflo-suction-chain",
           _hw / "reference" / "seaflo-discharge-chain",
           _hw / "reference" / "waveshare-43b-display",
           _hw / "reference" / "meanwell-irm90",
           _hw / "reference" / "teyleten-relay",
           _hw / "reference" / "ground-ring-stack",
           _hw / "printed-parts" / "electronics",
           _hw / "printed-parts" / "electronics" / "pcba-tray",
           _hw / "printed-parts" / "electronics" / "ac-hub",
           _hw / "reference" / "asse1022-assembly",
           _hw / "printed-parts" / "enclosure" / "drip-pan",
           _hw / "reference" / "water-split",
           _hw / "reference" / "neofit-flow-control",
           _hw / "reference" / "beduan-solenoid",
           _hw / "reference" / "jg-bulkhead-union",
           _hw / "reference" / "iec-c14-inlet",
           _hw / "reference" / "derpipe-co2-inlet",
           _hw / "reference" / "gasher-check-valve",
           _hw / "reference" / "wr1110-regulator",
           _hw / "reference" / "digiten-flow-sensor",
           _hw / "printed-parts" / "cold-core",
           _hw / "printed-parts" / "cold-core" / "copper-plugs",
           _hw / "printed-parts" / "cold-core" / "foam-assembly",
           _hw / "printed-parts" / "enclosure" / "enclosure"):
    sys.path.insert(0, str(_p))
from _cadq_export import export_assembly              # noqa: E402
import _clearing                                      # noqa: E402
import _lines                                         # noqa: E402
import compressor_shroud as _shroud                   # noqa: E402
import condenser_block as _cond                       # noqa: E402
import copper_plugs as _plugs                         # noqa: E402
import enclosure as _enc                              # noqa: E402
import hopper_funnel as _funnel                       # noqa: E402
import manifold_layout as ml                          # noqa: E402
import seaflo_suction_chain as _suct                  # noqa: E402
import seaflo_discharge_chain as _dis                 # noqa: E402
import waveshare_43b_display as _disp                 # noqa: E402
import asse1022_assembly as _asse                     # noqa: E402
import drip_pan as _pan                               # noqa: E402
import foam_assembly as _foam                         # noqa: E402
import beduan_solenoid as _beduan                     # noqa: E402
import iec_c14_inlet as _c14                          # noqa: E402
import jg_bulkhead_union as _jg                       # noqa: E402
import neofit_flow_control as _flowreg                # noqa: E402
import water_split as _split                          # noqa: E402
import derpipe_co2_inlet as _derpipe                   # noqa: E402
import gasher_check_valve as _gasher                   # noqa: E402
import wr1110_regulator as _wr1110                     # noqa: E402
import digiten_flow_sensor as _digiten                 # noqa: E402
import meanwell_irm90 as _psu                          # noqa: E402
import teyleten_relay as _relay                        # noqa: E402
import ground_ring_stack as _gnd                       # noqa: E402
import pcba_tray as _pcba                              # noqa: E402
import ac_hub as _hub                                  # noqa: E402

PSU_STEP = _hw / "reference" / "meanwell-irm90" / "meanwell-irm90.step"
PCBA_STEP = _hw / "printed-parts" / "electronics" / "pcba-tray" / "pcba-board.step"
RELAY_STEP = _hw / "reference" / "teyleten-relay" / "teyleten-relay.step"
AC_HUB_STEP = _hw / "printed-parts" / "electronics" / "ac-hub" / "ac-hub-assembly.step"
GND_STACK_STEP = _hw / "reference" / "ground-ring-stack" / "ground-ring-stack.step"

SHROUD_STEP = _hw / "cut-parts" / "compressor-shroud" / "compressor-shroud.step"
FOAM_STEP = _hw / "printed-parts" / "cold-core" / "foam-assembly" / "foam-assembly.step"
SEAFLO_STEP = _hw / "reference" / "seaflo-22-pump" / "seaflo-22-pump.step"
FUNNEL_STEP = _hw / "printed-parts" / "zone-c" / "hopper-funnel" / "hopper-funnel.step"

# The placement anchors. Each is a turn a body is installed at, and the machine holds
# them rather than the bodies: two bodies mating face to face agree about one turn.
#
# `FOAM_YAW` is the whole edition. +90° about Z carries the cold core's local +X onto
# world +Y, so its long axis runs front-to-back and its SHORT axis (181) runs across
# the machine. The face the shell cuts every penetration in is its local −X, and the
# same turn puts that face on world −Y, facing the user.
FOAM_YAW = 90.0
# The compressor stands UPRIGHT in its shroud: the can's oil sits in its bottom and the
# pickup is gravity-fed, so upright is the compressor's constraint and the turn the
# shroud is free in is a yaw.
SHROUD_YAW = -90.0
# The water pump lies flat on the core's crown. Its barbs are molded into the casting
# and leave its ±Y side faces, so this yaw lands them on the machine's ±X, and lays its
# 187 mm long axis front-to-back.
SEAFLO_YAW = 90.0
# The funnel's spout is on its collar centre, so a turn about Z picks nothing; 0 keeps
# the collar's own axes on the top wall's.
FUNNEL_ROT = 0.0

C_SHROUD = cq.Color(0.60, 0.62, 0.66)        # the enclosure pack's own three
C_COND = cq.Color(0.78, 0.55, 0.35)
C_FOAM = cq.Color(0.55, 0.75, 0.95, 0.55)
C_SEAFLO = cq.Color(0.30, 0.45, 0.70)
C_FUNNEL = cq.Color(0.90, 0.90, 0.92, 0.65)
C_SUCT = cq.Color(0.72, 0.72, 0.76)
C_HOSE = cq.Color(0.35, 0.55, 0.85)
C_DISPLAY = cq.Color(0.16, 0.17, 0.20)
C_PSU = cq.Color(0.20, 0.20, 0.24)
C_PCBA = cq.Color(0.15, 0.45, 0.25)
C_RELAY = cq.Color(0.15, 0.35, 0.65)
C_AC_HUB = cq.Color(0.90, 0.55, 0.20)
C_GND = cq.Color(0.55, 0.55, 0.58)
C_ASSE = cq.Color(0.85, 0.78, 0.45)
C_PAN = cq.Color(0.62, 0.66, 0.72)
C_SPLIT = cq.Color(0.80, 0.72, 0.40)
C_FLOWREG = cq.Color(0.70, 0.60, 0.30)
C_VK = cq.Color(0.45, 0.50, 0.58)
C_BULKHEAD = cq.Color(0.86, 0.86, 0.89)
C_C14 = cq.Color(0.18, 0.18, 0.20)
C_CO2 = cq.Color(0.85, 0.35, 0.30)
C_WR1110 = cq.Color(0.70, 0.30, 0.26)
C_DIGITEN = cq.Color(0.92, 0.92, 0.94)

Z_AXIS = (cq.Vector(0, 0, 0), cq.Vector(0, 0, 1))
X_AXIS = (cq.Vector(0, 0, 0), cq.Vector(1, 0, 0))


def box(shape):
    return shape.BoundingBox()


def sit(shape, *, cx=None, y0=None, y1=None, z0=None, dz=None):
    """Move a shape by whole planes: centre it in X, put its near face at `y0` or its far face
    at `y1`, its floor at `z0`, or step it `dz`. Each argument names where a face of its own box
    lands."""
    return shape.translate(_shift(box(shape), cx=cx, y0=y0, y1=y1, z0=z0, dz=dz))


def _shift(b, *, cx=None, x0=None, x1=None, cy=None, y0=None, y1=None, z0=None, dz=None):
    return cq.Vector(
        (0.0 if cx is None else cx - (b.xmin + b.xmax) / 2.0)
        + (0.0 if x0 is None else x0 - b.xmin) + (0.0 if x1 is None else x1 - b.xmax),
        (0.0 if cy is None else cy - (b.ymin + b.ymax) / 2.0)
        + (0.0 if y0 is None else y0 - b.ymin) + (0.0 if y1 is None else y1 - b.ymax),
        (0.0 if z0 is None else z0 - b.zmin) + (dz or 0.0))


def _turned(v, axis, deg):
    """Rodrigues: the vector `v` turned `deg` about the unit `axis` through the origin — the same
    turn `Shape.rotate` gives the body, applied to a point or a direction on it."""
    a = cq.Vector(*axis).normalized()
    th = math.radians(deg)
    c, s_ = math.cos(th), math.sin(th)
    return (cq.Vector(*v) * c) + (a.cross(cq.Vector(*v)) * s_) + (a * (a.dot(cq.Vector(*v)) * (1.0 - c)))


# --- the seat ledger -------------------------------------------------------
#
# WHAT EACH BODY WAS CLOSED ON, recorded as it is closed. Every pose in this module is stated
# one of two ways — planes of the body's own box, or a station on one of its own mouths — and
# `seat_body` is where both are known. Keeping the statement beside the result is what lets a
# reader grade a placement without a second table to say what the placement was supposed to be:
# the rule and the measurement come out of the same call, so they cannot drift.
#
# Three things a row carries:
#
#   rule    what the construction asked for — `{"x1": 94.50, "z0": 253.40}`, or the world point
#           a mouth was seated on
#   got     the same faces read off the PLACED solid, and a station read back through the body's
#           own `carry`. A seat that names two planes on one axis, or a mouth the turns do not
#           actually carry to the target, shows up here and nowhere else.
#   room    where a DERIVED pose fell against the band its construction states — `(what, the
#           clearance asked for, the clearance measured)`. A rule stated as a plane is met by
#           construction; a rule stated as "one clearance off whatever is under it" is a
#           measurement, and this is the only record of how much was actually left.
#
# `members` is the bodies one seat places. Most seats place one body; the refrigeration base is
# turned and stood as a pair, and the manifold pack is posed and stood as a whole, so those two
# rows are struck on a combined box and name everything they carry.

Seat = collections.namedtuple("Seat", "turns rule got room members")

SEATS: dict = {}

# Where each plane name reads on a box — the ledger's `got` side, and the same faces `_shift`
# closes on.
_FACE = {"cx": lambda b: (b.xmin + b.xmax) / 2.0,
         "x0": lambda b: b.xmin, "x1": lambda b: b.xmax,
         "cy": lambda b: (b.ymin + b.ymax) / 2.0,
         "y0": lambda b: b.ymin, "y1": lambda b: b.ymax,
         "z0": lambda b: b.zmin}


def record_seat(name, *, turns=(), planes=None, station=None, got=None, members=()):
    """Enter one placement in the ledger, replacing any row of the same name.

    `got` is the placed geometry the rule is read back off: a bounding box for a plane rule, a
    world point for a station. A row is entered by the construction that owns the pose, so a
    body placed by something other than `seat_body` — the base pair, the manifold pack — is in
    the ledger on the same terms as one that is."""
    if station is None:
        rule = {k: v for k, v in (planes or {}).items() if v is not None}
        read = {k: _FACE[k](got) for k in rule if k in _FACE}
    else:
        rule, read = {"station": tuple(station)}, {"station": tuple(got)}
    SEATS[name] = Seat(tuple(turns), rule, read, [], tuple(members) or (name,))
    return SEATS[name]


def note_room(name, what, want, got):
    """Record where a derived pose fell against a band its construction states.

    `want` is the clearance the construction asked for and `got` is what the placed geometry
    actually leaves, measured the same way the strike measured it. `None` for `got` is a pose
    with nothing to fall short of — a body the band does not bound."""
    if name in SEATS:
        SEATS[name].room.append((what, want, got))


def seat_body(shape, turns=(), station=None, seat=None, **planes):
    """A body's whole placement: turned through each `(axis, degrees)` in `turns`, then moved by
    whole planes (`sit`).

    `planes` moves it by whole faces of its own box; `station` instead seats one of its own
    mouths on a world point, which is what a fitting actually answers to.

    `seat` is the name the body goes into the assembly under, and naming it enters the placement
    in `SEATS` — the rule this call was given, beside the same rule read back off the geometry
    it produced.

    Returns `(placed, carry)`. `carry` takes a `(position, outward axis)` station in the body's
    OWN frame through the same turns and the same move — so a port table written once in a
    reference module rides every placement of the body it is on, and a port cannot drift from
    the metal it is a hole in."""
    for axis, deg in turns:
        shape = shape.rotate(cq.Vector(0, 0, 0), cq.Vector(*axis), deg)
    if station is None:
        shift = _shift(box(shape), **planes)
    else:
        # A FITTING IS SEATED ON ITS MOUTH, not on a face of its box: what has to land in the
        # right place is the collet the tube pushes into, and the body is wherever that leaves
        # it. `station` is (a station in the body's own frame, the world point its position
        # goes to) — the turns above carry the station, and the shift closes on the target.
        local, target = station
        pos = _turned(local[0], *turns[0]) if len(turns) == 1 else cq.Vector(*local[0])
        if len(turns) != 1:
            for ax, deg in turns:
                pos = _turned(pos, ax, deg)
        shift = cq.Vector(*target) - cq.Vector(pos.x, pos.y, pos.z)

    def carry(station):
        pos, axis = station
        for ax, deg in turns:
            pos, axis = _turned(pos, ax, deg), _turned(axis, ax, deg)
        p = cq.Vector(*pos) + shift if not isinstance(pos, cq.Vector) else pos + shift
        a = axis if isinstance(axis, cq.Vector) else cq.Vector(*axis)
        return ((p.x, p.y, p.z), (a.x, a.y, a.z))

    placed = shape.translate(shift)
    if seat is not None:
        if station is None:
            record_seat(seat, turns=turns, planes=planes, got=box(placed))
        else:
            record_seat(seat, turns=turns, station=station[1], got=carry(station[0])[0])
    return placed, carry


# --- The base: two bodies, one plane between them --------------------------
#
# The pair is built mated and then turned as ONE body about its own centre, because the mating
# is between the two of them and the turn is about where the air goes. `BASE_YAW` is that turn:
# the condenser's `AIRFLOW` axis is its native X and the fan is on the face the air leaves by,
# so the quarter that brings its west face onto the shroud's aft plane also lays the fan on +Y,
# and this puts it back across the cabinet.
BASE_YAW = -90.0


def build_shroud():
    """The shroud as the machine turns it, its front face on y = 0 and its feet on the floor.

    `(placed, carry)` like every other seated body: the shroud's four wall penetrations are
    a table in its own frame and the carry is what puts them in the machine."""
    return seat_body(cq.importers.importStep(str(SHROUD_STEP)).val(),
                     (((0.0, 0.0, 1.0), SHROUD_YAW),), cx=0.0, y0=0.0, z0=0.0)


def build_condenser(shroud):
    """The block turned a quarter about Z, which brings the WEST face the mating names round
    onto the shroud's own aft plane, and stood on the same floor."""
    c = _cond.build()
    c = c.toCompound() if hasattr(c, "toCompound") else c
    return seat_body(c, (((0.0, 0.0, 1.0), 90.0),),
                     cx=0.0, y0=box(shroud).ymax, z0=0.0)


def build_foam(front_y: float):
    """The cold core at the machine's own `FOAM_YAW` and on the machine's own floor, its front
    face on the plane the front half ends at. Its native box hangs 20 mm below its origin, so
    the floor is the box's own bottom and not that origin.

    Returns `(placed, carry)` like every other seated body, so the cap's conduit mouths ride the
    placement — a line reaching one is drawn to where the bore actually comes out."""
    f = cq.importers.importStep(str(FOAM_STEP)).val()
    return seat_body(f, (((0.0, 0.0, 1.0), FOAM_YAW),), seat="foam-assembly",
                     cx=0.0, y0=front_y, z0=0.0)


# --- The refrigerant loop's three joints ------------------------------------
#
# The sealed loop is the one circuit in the machine with NO TUBE DRAWN FOR IT, and that is
# the arrangement rather than an omission: each of its three joints crosses a plane two
# bodies already share — the shroud against the condenser, the condenser against the cold
# core, the shroud against the same core at the other flank — so both of a joint's stations
# are ONE POINT READ TWICE and the copper between them is the length of the union.
#
# Each end is a penetration its own module declares: `compressor_shroud.STATIONS`,
# `condenser_block.stations()`, `copper_plugs.slot_stations()`. Nothing here restates a
# coordinate; what this holds is that the two readings land together, and `_joints_hold`
# fails the build when one opens, because a station that has drifted is copper drawn in the
# open and no other gate on this pack would say so.
REFRIGERANT_JOINTS = (
    ("refrig-1", "compressor-shroud.refrig-discharge", "condenser+fan.refrig-inlet"),
    ("refrig-2", "condenser+fan.refrig-outlet", "foam-assembly.evap-inlet"),
    ("refrig-3", "foam-assembly.evap-outlet", "compressor-shroud.refrig-suction"),
)
# How far apart a joint's two stations may stand. It is import and boolean noise and nothing
# else: both are struck on one plane, so anything above this is a station that moved.
JOINT_TOL = 0.05


def refrigerant_stations(carries: dict) -> dict:
    """Every station the loop's three joints are made on, in world, keyed `body.port`.

    `carries` is the placement each body was seated by, so a station is its own module's
    table taken through the move the metal took."""
    tables = {"compressor-shroud": _shroud.STATIONS,
              "condenser+fan": _cond.stations(),
              "foam-assembly": {f"evap-{end}": st
                                for end, st in (("inlet", _plugs.slot_station("evap-inlet")),
                                                ("outlet", _plugs.slot_station("evap-outlet")))}}
    return {f"{body}.{port}": carries[body](station)
            for body, table in tables.items() if body in carries
            for port, station in table.items()}


def refrigerant_joints(carries: dict) -> list:
    """Each joint as `(id, from, to, mm apart)` — the measurement, taken at every build."""
    at = refrigerant_stations(carries)
    return [(cid, a, b, math.dist(at[a][0], at[b][0])) for cid, a, b in REFRIGERANT_JOINTS]


def check_refrigerant_joints(joints) -> None:
    """Raises unless every joint closes. A joint that has opened is a length of copper the
    machine now owes and nothing draws, so it fails the build rather than being noted."""
    open_ = [j for j in joints if j[3] > JOINT_TOL]
    if open_:
        raise ValueError(
            "the refrigerant loop is made up across the planes its bodies already share, and "
            + ", ".join(f"{cid} stands {gap:.3f} mm open ({a} to {b})"
                        for cid, a, b, gap in open_)
            + f" — over the {JOINT_TOL:g} mm a shared plane leaves. That distance is copper "
              f"drawn in the open between two bodies with nothing between them: move the "
              f"station that shifted back onto the one it is read against.")


def cap_conduit(name: str):
    """One of the cold core's cap conduits as a station in the CORE'S OWN frame:
    `((x, y, z), outward axis)`.

    `foam_assembly` authors the bore in the cap's frame and turns it back through the cap's own
    half-turn install, so its `(x, y)` is already the assembly's; the mouth's Z is the lid's
    outer face, which is the top of that same solid. The way out is the cap's +Z."""
    x, y = _foam.cap_conduit_station(name)
    top = box(cq.importers.importStep(str(FOAM_STEP)).val()).zmax
    return ((x, y, top), _foam.cap_conduit_axis_out())


def build_seaflo(foam):
    """The water pump at the machine's own `SEAFLO_YAW`, lying flat on the core's crown, centred
    on the mirror plane, its aft face flush with the core's own back."""
    b = box(foam)
    return seat_body(cq.importers.importStep(str(SEAFLO_STEP)).val(),
                (((0, 0, 1), SEAFLO_YAW),), seat="seaflo-pump",
                cx=0.0, y1=b.ymax, z0=b.zmax)


# --- the suction chain, lying in the lane beside the pump ------------------
#
# The chain is the two fittings that carry the pump's inlet from the 1/4" LLDPE that reaches it
# down onto its 3/8" hose barb, made up on the bench as one piece.
#
# It is LAID, not stood. Stood on end its barb faces the ceiling and a hose fed from a mouth
# below it has to turn over to come down; laid, both of its mouths face along the machine and a
# run reaches either square on.
#
# It lies BARB AFT, COLLET FORWARD. The barb faces back at the pump because that is where its
# hose comes from — `SEAFLO_YAW` lays the motor axis front-to-back, which puts the moulded
# suction barb on the head's EAST face pointing east, so `water-7` leaves across the machine and
# turns forward onto a mouth facing it. The collet then faces FORWARD, down the machine at the
# tap-water column that will feed it, rather than into the rear band.
SUCT_CHAIN_TURN = (((1.0, 0.0, 0.0), -90.0),)
# The lane it lies in is the strip of the cold core's crown EAST of the pump, and the strip is
# EMPTY: probed in 20 mm slices from y 180 to the rear plane, nothing stands in
# x[49, 90.5] z[253.4, 313.4] anywhere along it. The manifold's box reaches y 257 at this height
# and none of its solids do. So the chain is placed on the run it carries, not on a fence.
#
# It hugs the pump rather than the core's east edge, leaving the wall side of the strip open.
SUCT_PUMP_GAP = 8.0
# How far FORWARD of the pump's suction mouth the chain's barb stands. `water-7` turns from east
# to forward in this gap, and a 3/8" corner needs its whole radius as tangent in each leg it
# touches.
SUCT_CORNER_ROOM = 24.0


def build_suction_chain(seaflo, suction, port_z):
    """The chain laid in the lane east of the pump, on the crown the pump itself stands on.

    Its three coordinates answer to the run it carries and the lane it lies in: X one
    `SUCT_PUMP_GAP` east of the pump's casting, Y standing its barb `SUCT_CORNER_ROOM` forward
    of the pump's suction mouth so `water-7`'s corner seats a whole arc, and Z ON THE PLANE
    V-K'S OUTLET OPENS ON — `vk_port_z`, which is the valve's own port height over the seat
    the valve stands on.

    Laying both mouths on that one plane is what makes `water-4` a straight. The two stand
    `WATER_4` apart down one lane and a collet grips a tube through 3°; a step of a couple of
    millimetres across that gap is over 10°, which no lean that short can take out.

    What holds it there is an open item: nothing threads onto this chain and nothing clamps it.
    It has a measured datum and measured room; it does not have a bracket."""
    b = box(seaflo)
    chain = _suct.build()
    return seat_body(chain, SUCT_CHAIN_TURN, seat="suction-chain",
                cx=b.xmax + SUCT_PUMP_GAP + _suct.HOSE_OD / 2.0,
                y1=suction[0][1] - SUCT_CORNER_ROOM,
                # The chain's own Ø, read on X because the box is measured BEFORE the turn:
                # unturned the chain stands its length on Z and its diameter across X.
                z0=port_z - box(chain).xlen / 2.0)


# --- the discharge chain, in the lane west of the pump ---------------------
#
# The three fittings that carry the pump's outlet off its moulded 3/8" barb, hold the
# carbonator's pressure off it when it is idle, and hand the water over on 1/4" tube:
# MAACFLOW barb, GASHER check, PP450822E collet, made up on the bench as one piece.
#
# It lies BARB AFT, COLLET FORWARD in the lane west of the pump, which is the suction chain's
# own pose read across the machine — so it takes the suction chain's own turn.
DISCH_CHAIN_TURN = SUCT_CHAIN_TURN
# What its west face stands off the water split's east face. The lane it lies in is the strip
# of the core's crown between that split and the pump's own casting; the chain takes the split
# side of it, and what is left over is `water-6`'s corner.
DISCH_SPLIT_CLEAR = 1.0
# How far FORWARD of the pump's discharge mouth the chain's barb stands — the suction side's
# `SUCT_CORNER_ROOM` read across the machine. `water-6` turns from west to forward in this
# gap, and a 3/8" corner needs its whole radius as tangent in each leg it touches.
DISCH_CORNER_ROOM = 24.0


def build_discharge_chain(split, seaflo_carry):
    """The chain laid in the lane west of the pump, on the discharge's own plane.

    Its three coordinates answer to the run it carries and the lane it lies in: X one
    `DISCH_SPLIT_CLEAR` east of the split's own east face, Y standing its barb one
    `DISCH_CORNER_ROOM` forward of the pump's discharge mouth, and Z ON THAT MOUTH'S OWN
    PLANE — the barb fires due west and the chain's axis lies at its height, so `water-6`
    turns once in plan and climbs nothing.

    What holds it there is an open item: nothing threads onto this chain and nothing clamps
    it. It has a measured datum and measured room; it does not have a bracket."""
    disch = seaflo_carry(_lines._pump.discharge())[0]
    chain = _dis.build()
    return seat_body(chain, DISCH_CHAIN_TURN, seat="discharge-chain",
                     x0=box(split).xmax + DISCH_SPLIT_CLEAR,
                     y1=disch[1] - DISCH_CORNER_ROOM,
                     # The chain's own Ø, read on X because the box is measured BEFORE the
                     # turn: unturned the chain stands its length on Z, its Ø across X.
                     z0=disch[2] - box(chain).xlen / 2.0)


# --- the tap-water bulkhead, through the back wall -------------------------
#
# The union the customer's supply line pushes into, clamped through the rear wall. Its own frame
# already runs the flow down ±Y with the seating face on Y = 0, which is the axis and the plane
# the back wall gives it, so it takes NO TURN: the flange bears on the wall's outer face, the
# threading passes through, and the nut clamps inside.
#
# What it reaches inboard is the fitting's own business and not a choice: `far_ring_face_y` off
# that seating face, every millimetre of it inside the box. That reach is what `ASSE_REAR_CLEAR`
# was holding open.
BULKHEAD_STEP = _hw / "reference" / "jg-bulkhead-union" / "jg-bulkhead-union.step"
# A printed hole to the moulded barrel it passes, on the diameter.
PORT_HOLE_SLIP = 0.86
# THE FIRST JOINT IS FLUSH, so there is no `water-1` to draw. The union's inboard collet and the
# ASSE chain's inlet collet face each other down one axis with nothing between them to turn
# around, and a push-to-connect grips whatever reaches its grab ring — so the tube is cut to the
# two grips together, pushed home in the union, and the chain pushed onto what protrudes. The two
# release-ring faces meet, the tap water's first length of tube lives entirely inside the two
# fittings, and the chain stands as far aft as the wall it is fed through allows.


def bulkhead_seat_y():
    """The plane the union's flange bears on — the back wall's OUTER face."""
    return _enc.rear_plane_y + _enc.wall


def bulkhead_mouth_y():
    """The Y of its INBOARD collet face — the plane the ASSE chain's own inlet collet butts on.
    Read off the fitting's own seating planes, so a longer union moves the chain it feeds rather
    than closing on it."""
    return bulkhead_seat_y() + _jg.far_ring_face_y


def build_bulkhead(asse_carry):
    """The union seated on its INBOARD COLLET, on the ASSE chain's own column and stratum.

    A fitting answers to its mouth: the two collets face each other down one line, so the chain's
    inlet is what fixes this body in X and Z and the wall is what fixes it in Y. It stands
    `jg_bulkhead_union.PROUD_LENGTH` outboard of the box — the collet the customer's line pushes
    onto, and the only part of the machine behind its own back wall."""
    inlet = asse_carry(_asse.port("tube-in"))[0]
    body = cq.importers.importStep(str(BULKHEAD_STEP)).val()
    return seat_body(body, (), seat="bulkhead-water",
                     station=(_jg.port(-1.0),
                              (inlet[0], bulkhead_mouth_y(), inlet[2])))


def back_wall_ports(*bulkhead_carries):
    """Through-holes the back wall carries, as `(kind, x, z, *size)` on its own plane.

    One per union: the bore its threading passes. Each is struck on the fitting's own inboard
    collet, so hole and barrel cannot land on two different columns, and it is bored one
    `PORT_HOLE_SLIP` over the barrel that goes through it."""
    return [("round", carry(_jg.port(-1.0))[0][0], carry(_jg.port(-1.0))[0][2],
             _jg.panel_hole_d(PORT_HOLE_SLIP)) for carry in bulkhead_carries]


# --- the panel deck: the three unions the machine dispenses through ---------
#
# Everything the customer draws leaves by these: carbonated water to the faucet, and the two
# flavour lines to their nozzles. All three cross the back wall on ONE STOREY.
#
# Below that storey the cold core reaches nearly to the back wall, and what it leaves there is
# less than
# `jg_bulkhead_union.far_ring_face_y` — a union seated on that band has its collet inside the
# foam. The +X flank is the power block, the C14 and the CO2 chain, floor to ceiling. The pump
# fills the middle to its own crown. What is left is the band OVER THAT CROWN and under the top
# wall, and it is open from the west boss chain across to the C14's own corner — one room, wall
# to wall, with nothing standing in it. Re-read it by sweeping the union's own body over the
# wall:
#
#     w.cast((x, enclosure.rear_plane_y, z), (0, -1, 0), dia=jg_bulkhead_union.BODY_D)
#
# SO THE DECK IS STRUCK ON ITS OWN DESCENT. What the storey has to clear is not a crown but
# whatever each of its four bodies would land on if it fell, and a box answers neither half of
# that: the meter's round housing hangs over a round motor and the two nearest surfaces are not
# over each other, while the C14 standing beside the carb union is a body the union would slide
# past and never touch. So the four are dropped and the deck is the storey on which the least of
# them still has one `DECK_CLEAR` of fall left in it.
DECK_CLEAR = 6.0
# How far a deck body is dropped before the strike gives up on it. A body that never lands inside
# this reach has nothing under it, and does not fence the storey.
DECK_FALL_LIMIT = 60.0
# Where each union crosses the wall, west to east. The two gates take the ends — `fluid-28` comes
# down the WEST outboard column and `fluid-18` the EAST one, so each lands on the side it arrives
# from — and the carb riser takes the middle, where its meter lies inline ahead of it.
#
# The order across the row is what keeps the two deck crossings apart. Both `carb-1` and
# `fluid-18` come west along this deck and then turn aft down their own union's column, and the
# carb union standing OUTBOARD of the nozzle-A one is what lets the nozzle line pass under the
# riser's turn rather than through it: `fluid-18` crosses the carb column ahead of where the
# riser reaches it, and its own column stands west of everything the riser touches.
PANEL_X = {"bulkhead-flavor-b": -80.0, "bulkhead-flavor-a": -32.0, "bulkhead-carb": 16.0}


def build_panel_bulkhead(name: str, x: float, z: float):
    """One union clamped through the back wall on `(x, z)`, seated on its INBOARD COLLET.

    The same fitting and the same seating as the tap-water union: the flange bears on the wall's
    outer face, the threading passes through, and the nut clamps inside. What it reaches inboard
    is `jg_bulkhead_union.far_ring_face_y`, and `bulkhead_mouth_y` is where that leaves the
    collet the run pushes into."""
    body = cq.importers.importStep(str(BULKHEAD_STEP)).val()
    return seat_body(body, (), seat=name,
                     station=(_jg.port(-1.0), (x, bulkhead_mouth_y(), z)))


# --- the DIGITEN meter, inline on the carb riser ---------------------------
#
# The Hall-effect turbine the faucet's flow is read on: the pulse train is what tells the machine
# a glass is being poured, so the flavour pumps start with the water and stop with it.
#
# It lies FORE AND AFT on the panel deck, inlet forward and outlet aft, on the carb union's own
# column and stratum — so `carb-2` is a length of tube between two mouths facing each other down
# one line, and the riser's only route is on the other side of the meter.
#
# The YAW lays its flow axis along the machine; the ROLL then turns the wire boss off the ceiling
# onto +X, which is both the room the top wall leaves and the way the pigtail has to go — the
# controller board it plugs into stands on the +X flank.
DIGITEN_STEP = _hw / "reference" / "digiten-flow-sensor" / "digiten-flow-sensor.step"
DIGITEN_TURN = (((0.0, 0.0, 1.0), 90.0), ((0.0, 1.0, 0.0), 90.0))
# The straight between the meter's outlet and the union's inboard collet — `carb-2`, which has no
# corner in it for the same reason `water-2` has none: two collets facing each other down one
# axis seat no arc, and what the gap has to be is enough tube for both to take hold of.
CARB_2 = 24.0


def build_digiten(carb_carry, seat: bool = True):
    """The meter seated on its OUTLET, one `CARB_2` forward of the carb union's inboard collet
    and on that collet's own column and plane.

    A fitting answers to its mouth: both ends of this body are collets, and the one that has to
    land in the right place is the one the union is waiting on. Where the inlet ends up is
    `digiten_flow_sensor.port_face` ahead of the body centre, and that is where `carb-1` closes.

    Nothing threads onto it and nothing clamps it — the bracket is an open item; this is where
    it hangs."""
    pos, axis = carb_carry(_jg.port(-1.0))
    target = tuple(pos[i] + axis[i] * CARB_2 for i in range(3))
    body = cq.importers.importStep(str(DIGITEN_STEP)).val()
    return seat_body(body, DIGITEN_TURN, seat="digiten-flow" if seat else None,
                     station=(_digiten.outlet(), target))


# --- the storey those four stand on ----------------------------------------

def build_deck(z: float, seat: bool = False):
    """The four bodies the deck carries, on the storey `z`: the three unions across the back
    wall, and the meter inline one `CARB_2` ahead of the carb one.

    One function, called with a trial storey to strike the deck and again with the struck one to
    place it, so the bodies the strike measures are the bodies the machine gets. `seat` is what
    tells the two apart for the ledger: the trial is a MEASUREMENT and not a pose, and only the
    placement the machine keeps is entered."""
    solids, carries = {}, {}
    for name, px in PANEL_X.items():
        solids[name], carries[name] = build_panel_bulkhead(name if seat else None, px, z)
    solids["digiten-flow"], carries["digiten-flow"] = build_digiten(
        carries["bulkhead-carb"], seat=seat)
    return solids, carries


def descent(body, under, limit=DECK_FALL_LIMIT):
    """How far `body` falls before it lands on one of `under`, or `None` if it never does.

    EXACT STRIDES, not a grid. `_clearing.gap` is 1-Lipschitz under translation, so advancing the
    body by its own current gap cannot step over a contact: the walk closes on the landing itself
    rather than sampling near it, and a body that never lands says so instead of reporting the
    limit as a clearance."""
    best = None
    for other in under:
        t = 0.0
        while t <= limit:
            g = _clearing.gap(body.translate(cq.Vector(0.0, 0.0, -t)), other)
            if g <= 1e-9:
                best = t if best is None else min(best, t)
                break
            t += g
    return best


def _would_land_on(b, placed):
    """The bodies a body of box `b` could come down on: the ones its plan footprint overlaps that
    do not stand entirely above it.

    A body it only stands BESIDE is not a floor. The C14 is the case that matters — it shares the
    carb union's stratum and reaches within a few millimetres of its barrel across the machine,
    and a strike that read that standoff as headroom would push the deck up rather than let the
    union slide past it."""
    return [s for s in placed
            if not (box(s).xmax <= b.xmin or box(s).xmin >= b.xmax
                    or box(s).ymax <= b.ymin or box(s).ymin >= b.ymax
                    or box(s).zmin >= b.zmax)]


def deck_z(placed):
    """The Z the panel deck lies on: the storey on which the least of the four bodies it carries
    still has one `DECK_CLEAR` of fall left in it.

    `placed` is everything already standing, which is what the deck has to come down onto. The
    trial storey the four are dropped from is that pack's own crown, one union half-section — the
    fattest the deck carries — and a clearance over it, so all four start in air whatever stands
    below them, and the strike is that trial less what the first of them to land would fall.

    Returns `(z, {body: the fall it still has at that storey})`. The second is the band this
    strike states — one body is left standing on exactly `DECK_CLEAR` and the rest on whatever
    their own descent leaves — and it is what the ledger's `room` side records."""
    trial = max(box(s).zmax for s in placed) + DECK_CLEAR + _jg.BODY_D / 2.0
    falls = {name: descent(s, _would_land_on(box(s), placed))
             for name, s in build_deck(trial)[0].items()}
    landing = [d for d in falls.values() if d is not None]
    z = trial - min(landing) + DECK_CLEAR if landing else trial
    return z, {n: None if d is None else d - (trial - z) for n, d in falls.items()}


# --- the mains inlet, through the back wall --------------------------------
#
# The C14 the customer's cord plugs into. It lands FROM INSIDE — the flange bears on the wall's
# inner face and two screws hold it there — so its housing stands in the box and only the shroud
# reaches out through the cutout. Its own frame already faces the mating axis down +Y with the
# seating plane on Y = 0, which is what the back wall gives it, so it takes no turn either.
C14_STEP = _hw / "reference" / "iec-c14-inlet" / "iec-c14-inlet.step"
# Where it sits on that wall. The receptacle's wires reach the AC hub, so it wants the hub's own
# height and as much of its column as the pack leaves — and the pack leaves very little: the
# power block fills the +X flank from the cap to z 361.79, and the housing is 22 mm of body
# reaching inboard off the wall. Swept over the wall in 6 mm steps, the eastmost station whose
# housing clears every placed body at this height is this one.
C14_STATION = (54.0, 330.0)
# A printed cutout to the moulded shroud that passes it, on each side.
C14_CUTOUT_SLIP = 0.5


def build_c14():
    """The receptacle seated on the back wall's INNER face, its shroud out through the cutout.

    `iec_c14_inlet` states the seating planes: the flange's outboard face is its own Y = 0 and
    bears on that inner face, the housing hangs `BODY_DEPTH` inboard of it, and the shroud rises
    `SHROUD_PROUD` the other way — through a wall of `enclosure.wall` and standing proud of the
    outside by what is left."""
    body = cq.importers.importStep(str(C14_STEP)).val()
    return seat_body(body, (), seat="c14-inlet",
                     station=(((0.0, 0.0, 0.0), (0.0, 1.0, 0.0)),
                              (C14_STATION[0], _enc.rear_plane_y, C14_STATION[1])))


def c14_stations():
    """The two heat-set screw stations on the back wall, as `(x, z)` — `enclosure._c14_bosses`
    stands a boss on each. Both sit ON the mating axis, so the pair follows the one station the
    receptacle is placed at."""
    return tuple((C14_STATION[0] + dx, C14_STATION[1] + dz) for dx, dz in _c14.panel_screws())


def c14_cutout():
    """The rounded rectangle the shroud reaches out through, in `back_ports` shape — struck on
    the same station the body is, one `C14_CUTOUT_SLIP` over the moulding on every side."""
    wx, wz, r = _c14.panel_cutout()
    return ("rect", C14_STATION[0], C14_STATION[1],
            wx + 2 * C14_CUTOUT_SLIP, wz + 2 * C14_CUTOUT_SLIP, r)


# --- the CO2 inlet chain, through the back wall ----------------------------
#
# The customer's cylinder stands beside the machine and its red tether lands here. Three bodies
# on one axis, inline off the wall: the DERPIPE's NPT stub reaches inboard, the GASHER check
# threads straight onto it — a made-up joint, no line — and the WR1110 stands one hop of tube
# ahead of the check on the same axis, holding the appliance side at 90 PSI.
#
# The axis is the WALL'S OWN NORMAL, so the chain takes a half turn about Z and nothing else:
# each fitting's frame already runs its flow down +Y with the upstream mouth on −Y, and the half
# turn lays that on world −Y — collet outboard, gas running forward into the machine.
CO2_CHAIN_TURN = (((0.0, 0.0, 1.0), 180.0),)
DERPIPE_STEP = _hw / "reference" / "derpipe-co2-inlet" / "derpipe-co2-inlet.step"
GASHER_STEP = _hw / "reference" / "gasher-check-valve" / "gasher-check-valve.step"
WR1110_STEP = _hw / "reference" / "wr1110-regulator" / "wr1110-regulator.step"
# Where it crosses the back wall — EAST OF THE PUMP AND UNDER THE MAINS INLET. What the station
# has to buy is straight-line depth for a rigid chain, so it is swept on the regulator's own hex,
# the fattest body the chain carries —
#
#     w.cast((x, enclosure.rear_plane_y, z), (0, -1, 0), dia=wr1110.HEX_ACROSS_CORNERS)
#
# — and read against what the three bodies and their hop stand. The three that close the sweep
# around this station are the pump's casting west, the power block's brick east, and `water-7`
# ahead; the C14's own housing is what takes the wall above it.
CO2_STATION = (48.0, 290.0)
# Air between the wrench hex's inboard end and the wall's outer face — the room a socket needs
# to get on the flats. The fitting is seated on this, so its stub tip is wherever that leaves it.
DERPIPE_WRENCH_CLEAR = 2.0
# The hop `co2-1` closes, mouth to mouth: the check's stub tip to the regulator's inlet socket.
# It holds a PP450822E on the check's male stub, a PP010822E in the regulator's female one, and
# the stretch of 1/4" tube between the two collets.
CO2_HOP = 10.0


def co2_inlet_mouth_y():
    """The Y of the DERPIPE's INBOARD stub tip — the shoulder the GASHER's socket makes up
    against, and so where the whole chain starts. Read off the wall's outer face through the
    fitting's own reach, so a thicker wall moves the chain it carries."""
    outer = _enc.rear_plane_y + _enc.wall
    return outer + DERPIPE_WRENCH_CLEAR + _derpipe.PROUD_LENGTH - _derpipe.BODY_LENGTH


def build_co2_inlet():
    """The 5/16" push-to-connect the customer's CO2 line goes into, clamped through the back
    wall on `CO2_STATION`, seated on its own INBOARD STUB TIP."""
    body = cq.importers.importStep(str(DERPIPE_STEP)).val()
    return seat_body(body, CO2_CHAIN_TURN, seat="co2-inlet",
                     station=(_derpipe.stub_tip(),
                              (CO2_STATION[0], co2_inlet_mouth_y(), CO2_STATION[1])))


def build_gasher_co2(inlet_carry):
    """The check on the DERPIPE's stub, seated by its INLET on that same station — so the
    made-up thread is construction and there is no line to close. Its arrow points away from
    the bulkhead: the carbonator's pressure never reaches the customer's regulator."""
    body = cq.importers.importStep(str(GASHER_STEP)).val()
    return seat_body(body, CO2_CHAIN_TURN, seat="gasher-co2",
                     station=(_gasher.inlet(), inlet_carry(_derpipe.stub_tip())[0]))


def build_wr1110(gasher_carry):
    """The secondary regulator standing one `CO2_HOP` ahead of the check on the chain's own
    axis, seated on its INLET socket. Nothing threads onto it and nothing holds it — the cradle
    is an open item; this is where it hangs."""
    pos, axis = gasher_carry(_gasher.outlet())
    target = tuple(pos[i] + axis[i] * CO2_HOP for i in range(3))
    body = cq.importers.importStep(str(WR1110_STEP)).val()
    return seat_body(body, CO2_CHAIN_TURN, seat="wr1110",
                     station=(_wr1110.inlet(), target))


def co2_wall_port(inlet_carry):
    """The bore the DERPIPE's threading passes, as a `back_ports` entry. Struck on the
    fitting's own collet so hole and shank cannot land on two different columns."""
    pos = inlet_carry(_derpipe.collet())[0]
    return ("round", pos[0], pos[2], _derpipe.SHANK_D + 2 * PORT_HOLE_SLIP)


# The assembly's non-manifold members, by name. `report` measures the manifold pack as
# one box — the clearances the core and the pump stand off are struck against it — so a
# body added to the assembly that is not part of that pack has to be named here or it
# joins the box and moves every one of them.
STANDALONE = ("compressor-shroud", "condenser+fan", "foam-assembly", "seaflo-pump",
              "hopper-funnel", "suction-chain", "discharge-chain", "display", "psu", "pcba",
              "relay-1", "ac-hub", "ground-stack", "asse1022-assembly", "drip-pan",
              "water-split", "flow-regulator", "vk-solenoid", "bulkhead-water",
              "c14-inlet", "co2-inlet", "gasher-co2", "wr1110",
              "bulkhead-flavor-a", "bulkhead-flavor-b", "bulkhead-carb", "digiten-flow")


def _manifold(name):
    return (name not in STANDALONE and not name.startswith("enclosure-")
            and name not in _ROUTED)


# The runs this module authors, by the name they go into the assembly under. `manifold_layout`'s
# own segments come in as `tube-fluid-*` and are part of the pack; these are between bodies.
_ROUTED: set = set()


# --- the +X wall's own seat ------------------------------------------------
#
# The plane a body hung on the east wall stands its outer face on. `enclosure._dims` strikes the
# interior's east face one `side_rib_inset` outboard of the widest body ON THE FLOOR, and the ±X
# boss band reaches one `enclosure.boss_in` back inboard from the wall it builds there. Those two
# are the same 14 mm, so the band ends exactly on that body's own east face — which makes "clear
# of the Y seam's posts, pods and plugs" and "in line with the refrigeration stratum" one test,
# and lets a body on this flank be seated before the box that carries it has been sized.

def east_wall_seat(*floor_bodies):
    return max(box(s).xmax for s in floor_bodies)


def west_interior_face(*floor_bodies):
    """The −X wall's own inner face. `enclosure._dims` strikes it one `side_rib_inset` outboard
    of the westmost body on the floor, so it is knowable from the pack alone."""
    return min(box(s).xmin for s in floor_bodies) - _enc.side_rib_inset


# The brick lies on its side against that wall: a quarter about Y stands its 52 mm width up as
# height and lays its 33.5 mm depth across the machine, so only that much of the lane reaches
# inboard and its 109 mm long axis runs fore and aft down the flank.
PSU_TURN = (((0.0, 1.0, 0.0), -90.0),)
# What the brick stands off the rear seam: the back wall's own standoff, and a clearance floor
# past it. Its AC end wants the C14 inlet above it, which is a back-panel body and not placed.
PSU_REAR_CLEAR = 6.0


def build_psu(foam, wall_seat):
    """The MeanWell brick on the +X wall, standing on the cold core's cap.

    Three faces of the machine and not three numbers: EAST on the wall seat, AFT one
    `PSU_REAR_CLEAR` ahead of the rear seam's standoff, FOOT on the cap's own lid. The lane it
    lies in is what the SeaFlo leaves east of itself on that cap."""
    b = box(foam)
    return seat_body(cq.importers.importStep(str(PSU_STEP)).val(), PSU_TURN, seat="psu",
                     x1=wall_seat,
                     y1=_enc.rear_plane_y - _enc.rear_seam_clear - PSU_REAR_CLEAR,
                     z0=b.zmax)


# The controller board joins the brick's column rather than standing forward of the deck: same
# flank, same seat, same floor. Two turns put it there. The ROLL stands it off the flat — a
# quarter about Y brings its faces onto ±X, so only its 19.1 mm of thickness and components
# reaches into the lane, and the flat back is the face that meets the wall it mounts to. The SPIN
# is in that plane — a quarter about X lays the board's LONG edge fore and aft down the flank, so
# the short edge is what stands, and the corner that meets the cap is the one nearest the brick.
PCBA_TURN = (((0.0, 1.0, 0.0), -90.0), ((1.0, 0.0, 0.0), -90.0))
# What the board stands off the brick along the flank. Both are wired, and a hand making off a
# connector between them needs the gap to be a gap.
PCBA_PSU_CLEAR = 6.0


def build_pcba(foam, psu, wall_seat):
    """The controller board on the +X wall, forward of the brick on the same cap.

    EAST on the same wall seat the brick takes, so the two stand in one plane and the boss band
    holds them both; AFT one `PCBA_PSU_CLEAR` ahead of the brick's own front face; FOOT on the
    cap. What holds it is the pcba-tray, which is not placed — this is the board's envelope."""
    return seat_body(cq.importers.importStep(str(PCBA_STEP)).val(), PCBA_TURN, seat="pcba",
                     x1=wall_seat, y1=box(psu).ymin - PCBA_PSU_CLEAR, z0=box(foam).zmax)


# The rest of the power block on the brick's crown: the relay aft-flush with the brick, the AC hub
# on the relay's crown, and the ground stud on the relay's own floor one clearance forward of it.
# Each takes the same wall seat as its east face, so the whole group stands clear of every post,
# pod and plug the Y seam puts in that band.
#
# Each turn lays the body's own long axis fore and aft down the flank and its board or wells
# facing INBOARD — the face a screwdriver reaches, and the face a boss would land on.
RELAY_TURN = (((0.0, 0.0, 1.0), 270.0), ((0.0, 1.0, 0.0), 270.0))
AC_HUB_TURN = (((0.0, 0.0, 1.0), 90.0), ((0.0, 1.0, 0.0), 270.0))
# The floor between one body on this column and the next, and it is not air for its own sake:
# what stands in it is the WALL BOSS that fastens the body between them. The relay is the body
# that sets it — its mount pattern runs closest to its own edge, so the boss standing on that
# pattern reaches furthest past the board — and the gap is that reach with a clearance past it.
STACK_CLEAR = (_enc.mount_boss_dia / 2.0
               - (_relay.width / 2.0 - _relay.hole_dy) + 1.0)


def build_stack(psu, wall_seat):
    """The three bodies the brick's crown carries, as `[(name, solid, colour, carry)]`.

    The relay and the hub stack aft-flush with the brick, each on the crown of the one below with
    a `STACK_CLEAR` floor between them. The stud stands on the RELAY'S floor, one `STACK_CLEAR`
    forward of the FRONTMOST face the pair presents — the hub's, which overhangs the relay it sits
    on — so the stud's own height answers to nothing above it."""
    aft = box(psu).ymax
    out, floor = [], box(psu).zmax
    for name, step, turn, colour in (
            ("relay-1", RELAY_STEP, RELAY_TURN, C_RELAY),
            ("ac-hub", AC_HUB_STEP, AC_HUB_TURN, C_AC_HUB)):
        solid, carry = seat_body(cq.importers.importStep(str(step)).val(), turn, seat=name,
                                 x1=wall_seat, y1=aft, z0=floor + STACK_CLEAR)
        out.append((name, solid, colour, carry))
        floor = box(solid).zmax
    fore = min(box(s).ymin for _n, s, _c, _k in out)
    stud, stud_carry = seat_body(cq.importers.importStep(str(GND_STACK_STEP)).val(), RELAY_TURN,
                                 seat="ground-stack", x1=wall_seat, y1=fore - STACK_CLEAR,
                                 z0=box(out[0][1]).zmin)
    out.append(("ground-stack", stud, C_GND, stud_carry))
    return out


# --- what fastens the power column to the +X wall --------------------------
#
# Every body on that flank is turned so its own MOUNTING PLANE faces the wall and stands on
# the wall seat: the brick's potted base, the board's underside, the relay's PCB underside,
# the hub plate's underside, the ground stud's landing face. Each of those planes is the
# body's own Z = 0 and each carries the body's hole pattern, so what holds it is one printed
# boss per hole — `enclosure._east_bosses` reaching in off the wall to that plane, bored for a
# ruthex M3 short, with the screw driven the other way, in through the body from the room.
#
# The pattern is READ OFF EACH MODULE and carried through that module's own placement. A body
# that moves takes its bosses with it, and a boss cannot land on a column the part has no hole
# in.

def wall_mounts(*mounted):
    """The +X wall's boss stations, as `(y, z, tip)`.

    `mounted` is one `(carry, holes)` per body: the placement `seat_body` handed back, and the
    body's own mount pattern in its own frame. Each hole is carried as a station on that body's
    Z = 0 — the plane every one of these modules draws its bores from — so `(y, z)` is where
    the boss stands on the wall and `tip` is the plane its top face reaches."""
    out = []
    for carry, holes in mounted:
        for hx, hy in holes:
            pos, _axis = carry(((hx, hy, 0.0), (0.0, 0.0, 1.0)))
            out.append((pos[1], pos[2], pos[0]))
    return tuple(out)


# --- the tap-water sequence, in the west lane ------------------------------
#
# The backflow preventer and everything that threads or clamps onto it, made up as one chain.
# Its own frame runs the flow down +X with the VENT ON −Z, so any turn that keeps the vent
# pointing at the floor is a yaw and nothing else — and the vent has to point at the floor,
# because it weeps to atmosphere and that drip is the machine's cross-contamination telltale.
#
# The yaw lays the 140 mm chain fore and aft in the lane west of the pump, INLET AFT: the tap
# water comes in through the back panel, so the mouth that faces the bulkhead is the upstream
# one and the flow runs forward down the lane to the split.
ASSE1022_YAW = -90.0
# The chain's aft end is THE BULKHEAD'S REACH and nothing else, because the joint between them is
# flush: the union hangs `jg_bulkhead_union.far_ring_face_y` inboard of the wall it clamps
# through, and the chain's inlet collet meets that face. So a longer union, or a thicker wall,
# moves the chain forward — and the whole west lane, which hangs off this chain, comes with it.
# THE PUMP IS NOT ITS BOX, and the lane west of it is a different width at every height. The
# bracket's splayed feet are the widest thing on the casting and they are only
# `seaflo_22_pump.FOOT_T` tall; over them the cradle steps in, and the head's flange steps back
# out. So the chain and its basin RIDE OVER THE FEET rather than standing beside them, and what
# fences them once they are up there is whatever the casting presents AT THEIR OWN HEIGHT.
#
# One clearance, struck twice on two different surfaces: `pan_floor` holds the basin off the
# feet's top face, and `pan_east_x` holds its rim off the casting's west flank. The second is
# the one that binds — the tray's own width is what the lane has left over.
FOOT_CLEAR = 1.0


def pan_floor(foam, seaflo):
    """The Z the basin's own floor stands at: one clearance over the pump's bracket."""
    return max(box(foam).zmax, box(seaflo).zmin + _lines._pump.FOOT_T) + FOOT_CLEAR


def pump_west_face(seaflo, z0, z1):
    """The westmost the pump's casting reaches between two heights — the fence a body lying
    beside the pump in that band actually has.

    MEASURED ON THE SOLID, because the box would answer with the feet at every height and the
    feet are 8 mm of a 72 mm casting."""
    b = box(seaflo)
    slab = (cq.Workplane("XY")
            .box(b.xlen + 2.0, b.ylen + 2.0, z1 - z0, centered=False)
            .translate((b.xmin - 1.0, b.ymin - 1.0, z0)).val())
    return box(seaflo.intersect(slab)).xmin


def pan_east_x(seaflo, floor):
    """The X the basin's east rim stands at: one `FOOT_CLEAR` west of the casting, read over
    the band the tray itself occupies — its floor up to its rim."""
    return pump_west_face(seaflo, floor, floor + _pan.PAN_Z) - FOOT_CLEAR


def build_asse(foam, seaflo):
    """The ASSE 1022 chain in the west lane, high enough over the cold core's cap that the drip
    pan stands under its vent.

    Its HEIGHT is the pan's, read off the pan's own module rather than typed: the basin's floor
    lies on the cap, its rim one `PAN_Z` above that, and the chain's underside one
    `VENT_GAP` of air over the rim. So the vent's drip falls the gap the basin was drawn for,
    and a change to either number moves both bodies together.

    Its X hugs the cold core's west face, leaving the rest of the lane between it and the pump.

    Its Y is the BULKHEAD'S OWN MOUTH: the inlet collet butts the union's inboard collet, so the
    chain stands off the back wall by exactly what the union reaching through it leaves, and by
    nothing else."""
    chain = _asse.build()
    chain = chain.toCompound() if hasattr(chain, "toCompound") else chain
    chain = chain.val() if hasattr(chain, "val") else chain
    return seat_body(chain, (((0.0, 0.0, 1.0), ASSE1022_YAW),), seat="asse1022-assembly",
                     x0=box(foam).xmin,
                     y1=bulkhead_mouth_y(),
                     z0=pan_floor(foam, seaflo) + _pan.PAN_Z + _pan.VENT_GAP)


# THE TRAY STANDS CLEAR OF THE PUMP'S DISCHARGE. The barb fires west into this same lane and the
# chain that hangs off it takes the lane's forward end, so the basin's forward rim is struck on
# the barb's own aft edge with this much daylight past it. That plane fixes the tray in Y — the
# vent does not, and has only to fall inside the floor from wherever the chain leaves it.
PAN_PORT_CLEAR = 10.0


def pan_front_y(seaflo_carry):
    """The Y the basin's forward rim stands on: one `PAN_PORT_CLEAR` aft of the pump's discharge.

    The barb is a cylinder firing along ±X, so what it stands in down the lane is its centreline
    and its own radius. Moving the pump moves the tray that clears it."""
    pos = seaflo_carry(_lines._pump.discharge())[0]
    return pos[1] + _lines._pump.PORT_D / 2.0 + PAN_PORT_CLEAR


def check_vent_lands(pan, tip):
    """Raises unless the drip falls on the FLAT FLOOR, inside the coves.

    The basin's outer rim to that flat is the flange, the wall and the cove together. A drip
    landing on a cove or a wall runs down the outside of the tray instead of onto the moisture
    plate, and the plate stays dry however long the vent weeps."""
    b = box(pan)
    inset = _pan.FLANGE_W + _pan.WALL + _pan.FLOOR_COVE
    y0, y1 = b.ymin + inset, b.ymax - inset
    if not y0 <= tip[1] <= y1:
        raise ValueError(
            f"drip-pan: the vent drips at y {tip[1]:.2f}, off the flat floor y[{y0:.2f}, "
            f"{y1:.2f}]. The forward rim comes off the pump's discharge through "
            f"`PAN_PORT_CLEAR`; the vent's Y comes off the ASSE chain, which the bulkhead's "
            f"reach through the back wall fixes; the flat between them is `PAN_Y` less its "
            f"flange, its walls and its coves.")


def check_pan_lane(pan, west_face):
    """Raises unless the tray, stood off the pump by `FOOT_CLEAR`, still lands inside the −X
    wall.

    The lane has two bounds and the tray is hung on the EAST one, because that is the bound a
    millimetre matters on: everything the tray gives back in X is ceiling the west column's
    crossing ladder buys radius from, and the pump does not move for it. Where the west lip
    then falls is what is left over — and a lip landing outboard of the wall's inner face is a
    tray the wall would have to be widened around, which is `drip_pan.PAN_X`'s answer to give
    and not this module's."""
    b = box(pan)
    if b.xmin < west_face - 1e-6:
        raise ValueError(
            f"drip-pan: the tray's west lip lands at x {b.xmin:.2f}, {west_face - b.xmin:.2f} "
            f"mm outboard of the −X wall's inner face at {west_face:.2f}. Its east rim stands "
            f"one FOOT_CLEAR = {FOOT_CLEAR:g} off the pump's casting at the tray's own height, "
            f"so the lane holds a rim of {b.xmax - west_face:.2f}; shrink `drip_pan.PAN_X` by "
            f"what is over.")


def build_pan(foam, seaflo, seaflo_carry, asse_carry, west_face):
    """The catch basin under the atmospheric vent, standing over the pump's bracket.

    IN Y THE PUMP'S DISCHARGE BOUNDS IT AND THE VENT DOES NOT. The forward rim is `pan_front_y`,
    and the vent falls where the chain's own standoff from the back wall leaves it — so where the
    drip lands is a check, and `check_vent_lands` is where it is made.

    IN X THE PUMP BOUNDS IT AND THE VENT DOES NOT EITHER. The east rim is `pan_east_x`, one
    clearance off the casting's own west flank at the tray's height; the west lip takes what
    the lane has left, and `check_pan_lane` is where that is made. The tip lands 2 mm off the
    floor's own centre — 2 mm of a ±22 mm floor, so the drip still falls well inside the coves.
    The slot the tray draws out through is a wall port, struck off this body's own box in
    `west_wall_ports`.

    Z is `pan_floor` — one clearance over the pump's bracket, not on the cap — with the rim one
    `PAN_Z` up and the chain's underside one `VENT_GAP` over that. `build_asse` stands the chain
    on the same three numbers, so the drip falls exactly the gap the basin was drawn for."""
    pan = _pan.build()
    pan = pan.val() if hasattr(pan, "val") else pan
    floor = pan_floor(foam, seaflo)
    placed, carry = seat_body(pan, (), seat="drip-pan", x1=pan_east_x(seaflo, floor),
                              y0=pan_front_y(seaflo_carry), z0=floor)
    check_vent_lands(placed, asse_carry(_asse.port("vent-tip"))[0])
    check_pan_lane(placed, west_face)
    return placed, carry


# --- the split, on the chain's own flow axis --------------------------------
#
# The union tee that takes the ASSE's outlet and parts it two ways: on to V-K and the pump's
# suction, and on to the flow regulator and the flavour tap. Its own frame runs ±Y with the
# branch on −X, and the run is already the axis the chain hands the water over on — so the
# turn is about the BRANCH, which is the one of its three ports that can be given a level the
# other two are not on.
#
# A roll about Y leaves the run where it is and swings the branch from −X to −Z: the split's
# two run collets stay on the chain's line and its third looks straight DOWN, at the storey the
# pump and the manifold are on.
SPLIT_TURN = (((0.0, 1.0, 0.0), -90.0),)
# The straight between the chain's outlet collet and the split's supply collet — `water-2`,
# which is one length of tube and no bend at all, because the two mouths face each other down
# one line. A collet grips the tube all round, so what this has to be is enough tube for both
# to take hold of.
WATER_2 = 24.0


def build_split(asse_carry):
    """The split seated on its SUPPLY COLLET, one `WATER_2` forward of the chain's outlet.

    A fitting answers to its mouth and not to a face of its box: what has to land in the right
    place is the collet the tube pushes into. Both are read off the chain's own outlet, so the
    split rides the chain wherever the chain goes."""
    out_pos, out_axis = asse_carry(_asse.port("tube-out"))
    target = tuple(out_pos[i] + out_axis[i] * WATER_2 for i in range(3))
    return seat_body(_split.build(), SPLIT_TURN, seat="water-split",
                     station=(_split.supply(), target))


# --- the flow regulator, inline on the flavour tap -------------------------
#
# The needle valve that throttles the flavour side. Its own frame runs the flow down ±X with the
# adjuster on +Z. The YAW lays that flow fore and aft along the lane; the ROLL then lays the stem
# over onto +X, so the valve reads 14.72 mm tall and 40.85 mm across the lane rather than the
# other way round, and the knurled head faces the machine's centre where a hand comes in over the
# cold core's cap. `design-pressures.md` sets it once on the bench.
FLOWREG_TURN = (((0.0, 0.0, 1.0), -90.0), ((0.0, 1.0, 0.0), 90.0))
# The straight between the split's flavour collet and the regulator's inlet — `fluid-1`, which
# has no corner in it for the same reason `water-2` has none.
FLUID_1 = 24.0


def build_flowreg(split_carry):
    """The regulator seated on its INLET, one `FLUID_1` forward of the split's flavour collet
    and on that collet's own line — so the tap runs ASSE, split, regulator down one axis and
    every joint between them is a straight."""
    pos, axis = split_carry(_split.to_flavor())
    target = tuple(pos[i] + axis[i] * FLUID_1 for i in range(3))
    return seat_body(_flowreg.build(), FLOWREG_TURN, seat="flow-regulator",
                     station=(_flowreg.inlet(), target))


# --- V-K, the fill/shutoff on the way to the pump's suction ----------------
#
# Normally closed, so a leak alarm or a power loss stops all water reaching the carbonator. Its
# own frame runs the flow down ±Y — inlet forward, outlet aft — with the coil standing over it,
# and that is already the direction the water goes here, so it takes NO TURN AT ALL: it stands
# forward of the suction chain, firing aft into the collet that feeds the pump.
# The gap between V-K's outlet and the chain's collet — `water-4`. Both mouths lie on one plane
# and one column, so this is a length of tube and not a route.
WATER_4 = 15.0
# THE VALVE'S SEAT — what its own mounting face stands off the cold core's cap. The Beduan's
# Z = 0 is the underside of its white body, and the cap is the only thing under it; the tray
# that will fasten it there is queued work, and until it is printed the seat is this clearance.
# Stating it is what keeps the valve OFF the cap: the two mouths of this valve are what the
# chain and the run behind it are hung from, so without a seat of its own the column falls to
# wherever `beduan_solenoid.port_center_z` happens to land it, which is flat on the foam.
VK_SEAT = 1.0


def vk_port_z(foam):
    """The Z V-K's two collets open on — its own `port_center_z` over the seat its foot
    stands on, which is one `VK_SEAT` over the cold core's cap.

    The suction chain lies on this same plane, so `water-4` is a straight between two mouths
    facing each other, and a change to the seat moves the pair together."""
    return box(foam).zmax + VK_SEAT + _beduan.port_center_z


def build_vk(chain_carry):
    """V-K seated on its OUTLET, one `WATER_4` forward of the suction chain's collet and on
    that collet's own column and plane — which is `vk_port_z`, the plane the chain was laid
    on, so the valve comes back down onto its own seat."""
    pos, axis = chain_carry(_suct.tube_port())
    target = (pos[0], pos[1] + axis[1] * WATER_4, pos[2])
    body = _beduan.build_beduan_solenoid()
    body = body.val() if hasattr(body, "val") else body
    return seat_body(body, (), seat="vk-solenoid", station=(_beduan.outlet(), target))


# --- what carries the tray, and the slot it draws out through --------------
#
# The rail's own section, and the stop's.
DRIP_RAIL_H = 3.0
DRIP_STOP_T = 3.0


def pan_rails(pan, west_face):
    """The tray's carry, as world boxes fused onto the −X wall's inner face
    (`enclosure._pan_rails`): a rail under each of the rim's outer bands, and the stop the tray
    comes to rest against.

    THE RAILS TAKE THE RIM, and nothing reaches under the floor. Each rail's top face IS the
    flange's underside, and each RUNS FROM THE WALL — its root, and the only thing it is fused
    to — out to the tray's own east edge, so a seated tray stands on rail end to end and a
    withdrawing one keeps rail under it until the rim is clear of the wall. Rooting them on the
    wall rather than on the tray's west lip is what makes them printable at all: the lip stands
    off the wall by whatever the lane left it, and a rail begun there would be a bar hanging in
    air. The band each takes is `drip_pan.bearing_w()`, the flat of that underside inboard of
    the haunch, and the two inboard arrises take the tray's two 45° haunches and hold it on its
    column.

    THE STOP RUNS UNDER THE RIM, in the pocket the flange overhangs its basin by, and it
    catches the HAUNCH — the outermost face the tray presents below its rim, one
    `drip_pan.PAN_SLIP` off the bar's own.

    East of the rim there is nowhere to stand. The pump's casting steps west over this lane and
    reaches x −35.0 against a rim edge at −35.5, so the half millimetre between them is all
    there is, and it closes across exactly the span a stop has to bridge. What a bar needs is
    BOTH RAILS: it is fused to the −X wall through them and through nothing else, so a bar that
    does not reach them is a solid hanging in the air 73 mm from its only root. The three
    members make one U, and the pocket under the flange is where that U closes.

    So the bar runs the rim's whole length. The rim rides over it the way it rides the rails,
    and its plan arcs carry the tray away from it at both ends — `CORNER_R` plus the flange
    rounds the rim, plus the haunch rounds the section beneath, so the corners are clear and the
    straight between them is what butts."""
    top = pan.zmax - _pan.FLANGE_T              # the flange's underside — the bearing plane
    band = _pan.bearing_w()
    toe = pan.xmax - _pan.FLANGE_W + _pan.FLANGE_HAUNCH     # the haunch's outermost face
    stop_x = toe + _pan.PAN_SLIP
    return [(west_face, pan.xmax, pan.ymin, pan.ymin + band, top - DRIP_RAIL_H, top),
            (west_face, pan.xmax, pan.ymax - band, pan.ymax, top - DRIP_RAIL_H, top),
            (stop_x, stop_x + DRIP_STOP_T, pan.ymin, pan.ymax, top - DRIP_RAIL_H, top)]


def west_wall_ports(pan):
    """Through-holes the −X wall carries, as `(kind, y, z, *size)` on that wall's own plane —
    the slot the tray draws out through.

    ONE OPENING IN TWO RECTANGLES, each cut at what the tray is WIDEST at its own height. Above
    the flange's underside that is the rim. Below it, it is the HAUNCH: the 45° flare carries
    the section `drip_pan.FLANGE_HAUNCH` past the basin's wall on the way up to the rim, so a
    rectangle cut at the basin alone stops the tray a corner's length out of the wall.

    The two meet on the flange's underside — the plane the tray bears on — and the lower one's
    flank falls where `pan_rails` puts the rail's inboard face. So the rail stands beside the
    opening at full width, and the wall under the rim outboard of it is what carries the pair.

    The slip goes where the tray can move: one `drip_pan.PAN_SLIP` on both flanks of each
    rectangle, under the floor and over the rim. Square corners — `CORNER_R` rounds the tray in
    PLAN, and this is the section across it, where floor meets wall at a right angle."""
    s = _pan.PAN_SLIP
    reach = _pan.FLANGE_W - _pan.FLANGE_HAUNCH      # rim edge inboard to the haunch's toe
    hy0, hy1 = pan.ymin + reach, pan.ymax - reach
    z_flange = pan.zmax - _pan.FLANGE_T
    return [
        ("rect", (hy0 + hy1) / 2.0, (pan.zmin - s + z_flange) / 2.0,
         hy1 - hy0 + 2 * s, z_flange - pan.zmin + s, 0.0),
        ("rect", (pan.ymin + pan.ymax) / 2.0, (z_flange + pan.zmax + s) / 2.0,
         pan.ymax - pan.ymin + 2 * s, pan.zmax + s - z_flange, 0.0),
    ]


def _whole(bodies):
    out = None
    for s in bodies:
        b = box(s)
        out = b if out is None else out.add(b)
    return out


def place_base(seated, names=()):
    """Turn the mated pair `BASE_YAW` about the vertical through their own combined centre, then
    seat the PAIR — centred on x = 0 and its front face on y = 0. Both moves are rigid and taken
    on the pair's own box, so the plane between them rides along and the crown does not change.

    A yaw about a centre is not a placement: the turn leaves the pair's front wherever its own
    width used to reach, which is not the front of the machine.

    ONE SEAT FOR THE TWO, because the rule is struck on the combined box and neither body has it
    on its own — the ledger's row names both.

    `seated` is each body as `(solid, carry)` off its own seat, and this hands back the same
    pair with the yaw and the stand composed onto each carry: a penetration declared in either
    body's own frame rides both moves, so a station cannot fall off the metal it is a hole in."""
    bodies = [s for s, _c in seated]
    w = _whole(bodies)
    cx, cy = (w.xmin + w.xmax) / 2.0, (w.ymin + w.ymax) / 2.0
    axis = (cq.Vector(cx, cy, 0.0), cq.Vector(cx, cy, 1.0))
    turned = [s.rotate(*axis, BASE_YAW) for s in bodies]
    t = _whole(turned)
    step = cq.Vector(-(t.xmin + t.xmax) / 2.0, -t.ymin, 0.0)
    stood = [s.translate(step) for s in turned]
    if names:
        record_seat("refrigeration-base", turns=(((0.0, 0.0, 1.0), BASE_YAW),),
                    planes={"cx": 0.0, "y0": 0.0, "z0": 0.0}, got=_whole(stood), members=names)

    def compose(carry):
        def carried(station):
            (px, py, pz), axis_ = carry(station)
            p = _turned((px - cx, py - cy, pz), (0.0, 0.0, 1.0), BASE_YAW)
            a = _turned(axis_, (0.0, 0.0, 1.0), BASE_YAW)
            return ((p.x + cx + step.x, p.y + cy + step.y, p.z + step.z), (a.x, a.y, a.z))
        return carried

    return list(zip(stood, [compose(c) for _s, c in seated]))


# --- The manifold, laid on their crown -------------------------------------
#
# `(x, y, z) → (−x, z, y)`: a quarter about X puts the pack's own front face — the plane the
# pump heads open on — face down, and a half about Z brings the pumps to the front of it and
# the valve decks behind them. X is negated by the pair, which the mirror does not notice.

def pose_manifold(shape):
    return shape.rotate(*X_AXIS, 90.0).rotate(*Z_AXIS, 180.0)


def manifold_carry(lift: float):
    """The same two turns and the same lift, as a `carry` for a STATION.

    `manifold_layout.port` and its siblings answer in the pack's OWN world — the frame the fold
    leaves it in — and `build_pack` then poses that whole world and stands it on the base's
    crown. A line reaching a valve's collet has to arrive where the collet ends up, so the
    station rides the same transform the solid does: `(x, y, z) → (−x, z, y + lift)`, which is
    what the two rotations compose to."""
    def carry(station):
        (px, py, pz), (ax, ay, az) = station
        return ((-px, pz, py + lift), (-ax, az, ay))
    return carry


# What the pack actually sets down on is not a body at all — it is the four spine hairpins.
# The fold turned them onto the pack's own underside, and they hang past the pump-head faces,
# so THEY are the mating surface and the pump faces stand off the crown by whatever is left.
PUMP_FACE_Z = -ml.BARB_INSET                 # where that face lands once the pack is turned


def build_pack() -> cq.Assembly:
    """The bodies, with no box around them. `enclosure` sizes itself off this, so it
    cannot be in it."""
    a = cq.Assembly(name="front-half")
    SEATS.clear()
    seated_shroud = build_shroud()
    ((shroud, shroud_carry),
     (cond, cond_carry)) = place_base([seated_shroud, build_condenser(seated_shroud[0])],
                                      names=("compressor-shroud", "condenser+fan"))
    a.add(shroud, name="compressor-shroud", color=C_SHROUD)
    a.add(cond, name="condenser+fan", color=C_COND)

    posed = [(c.name, pose_manifold((c.obj.val() if hasattr(c.obj, "val") else c.obj).moved(
        cq.Location(c.loc.wrapped.Transformation()))), c.color) for c in ml.build_assembly().children]
    crown = max(box(shroud).zmax, box(cond).zmax)
    lift = crown - min(box(s).zmin for _n, s, _c in posed)
    stood = [(n, s.translate(cq.Vector(0.0, 0.0, lift)), c) for n, s, c in posed]
    in_pack = []
    for name, solid, color in stood:
        # A MOUTH THAT HAS A RUN ON IT IS NOT A FREE MOUTH. `manifold_layout` draws one bend
        # radius off each of the seven lines that leave its study — the straight their first
        # corner needs before it can turn — and `_lines` authoring that line is what replaces
        # the placeholder with the tube itself.
        if name.startswith("stub-") and name[len("stub-"):] in _lines.authored():
            continue
        a.add(solid, name=name, color=color)
        in_pack.append(name)
    # ONE SEAT FOR THE WHOLE PACK. It is posed and lifted as a body, and what it sets down on is
    # the four spine hairpins — so the rule is `z0` on the base's own crown, struck on the
    # combined box, and every body in the pack rides it.
    record_seat("manifold-layout",
                turns=((X_AXIS[1].toTuple(), 90.0), (Z_AXIS[1].toTuple(), 180.0)),
                planes={"z0": crown}, got=_whole([s for _n, s, _c in stood]),
                members=tuple(in_pack))
    # What the core butts is whatever the front half presents AT THE CORE'S OWN HEIGHT. The
    # source valves' quarter turns carry them aft over the core's crown, and a body standing
    # over it is not a body in its way — so the seam is measured against the bodies that reach
    # below that crown, and the ones above it are left to overhang.
    top = box(build_foam(0.0)[0]).zmax
    aft = max([box(shroud).ymax, box(cond).ymax]
              + [box(s).ymax for _n, s, _c in stood if box(s).zmin < top])
    foam, foam_carry = build_foam(aft)
    a.add(foam, name="foam-assembly", color=C_FOAM)
    # The sealed loop, measured the moment its three bodies are all placed. Nothing is drawn
    # between them — every joint crosses a plane two of them already share — so this reading
    # is the only thing standing between a station that moved and copper nobody notices.
    refrig_carries = {"compressor-shroud": shroud_carry, "condenser+fan": cond_carry,
                      "foam-assembly": foam_carry}
    a.refrigerant_at = refrigerant_stations(refrig_carries)
    a.refrigerant = refrigerant_joints(refrig_carries)
    check_refrigerant_joints(a.refrigerant)
    seaflo, seaflo_carry = build_seaflo(foam)
    a.add(seaflo, name="seaflo-pump", color=C_SEAFLO)
    chain, chain_carry = build_suction_chain(seaflo, seaflo_carry(_lines._pump.suction()),
                                             vk_port_z(foam))
    a.add(chain, name="suction-chain", color=C_SUCT)
    wall_seat = east_wall_seat(shroud, cond)
    psu, psu_carry = build_psu(foam, wall_seat)
    a.add(psu, name="psu", color=C_PSU)
    pcba, pcba_carry = build_pcba(foam, psu, wall_seat)
    a.add(pcba, name="pcba", color=C_PCBA)
    stack = build_stack(psu, wall_seat)
    for name, solid, colour, _carry in stack:
        a.add(solid, name=name, color=colour)
    stack_carry = {name: carry for name, _s, _c, carry in stack}
    a.east_bosses = wall_mounts(
        (psu_carry, _psu.holes), (pcba_carry, _pcba.board.holes),
        (stack_carry["relay-1"], _relay.holes), (stack_carry["ac-hub"], _hub.holes),
        (stack_carry["ground-stack"], _gnd.holes))
    asse, asse_carry = build_asse(foam, seaflo)
    a.add(asse, name="asse1022-assembly", color=C_ASSE)
    pan, _pan_carry = build_pan(foam, seaflo, seaflo_carry, asse_carry,
                                west_interior_face(shroud, cond))
    a.add(pan, name="drip-pan", color=C_PAN)
    split, split_carry = build_split(asse_carry)
    a.add(split, name="water-split", color=C_SPLIT)
    disch, disch_carry = build_discharge_chain(split, seaflo_carry)
    a.add(disch, name="discharge-chain", color=C_SUCT)
    flowreg, flowreg_carry = build_flowreg(split_carry)
    a.add(flowreg, name="flow-regulator", color=C_FLOWREG)
    vk, vk_carry = build_vk(chain_carry)
    a.add(vk, name="vk-solenoid", color=C_VK)
    bulkhead, bulkhead_carry = build_bulkhead(asse_carry)
    a.add(bulkhead, name="bulkhead-water", color=C_BULKHEAD)
    c14, _c14_carry = build_c14()
    a.add(c14, name="c14-inlet", color=C_C14)
    co2in, co2in_carry = build_co2_inlet()
    a.add(co2in, name="co2-inlet", color=C_CO2)
    gasher, gasher_carry = build_gasher_co2(co2in_carry)
    a.add(gasher, name="gasher-co2", color=C_CO2)
    wr1110, wr1110_carry = build_wr1110(gasher_carry)
    a.add(wr1110, name="wr1110", color=C_WR1110)
    a.co2_inlet_carry = co2in_carry
    # THE DECK COMES DOWN ONTO WHAT IS ALREADY STANDING, so its four bodies are struck against
    # the assembly as it is at this point and are the last things into it.
    a.deck_z, deck_fall = deck_z([s for s, _c in _solids(a).values()])
    deck_solids, panel_carries = build_deck(a.deck_z, seat=True)
    meter_carry = panel_carries.pop("digiten-flow")
    for name, solid in deck_solids.items():
        a.add(solid, name=name, color=C_DIGITEN if name == "digiten-flow" else C_BULKHEAD)
        note_room(name, "fall onto what stands under it", DECK_CLEAR, deck_fall[name])
    panels = {n: s for n, s in deck_solids.items() if n != "digiten-flow"}
    meter = deck_solids["digiten-flow"]
    a.panel_carries = panel_carries

    # The runs between placed bodies. Their frames come off the poses above, so a waypoint
    # measured off a port moves when the body it is on moves.
    carries = {"foam-assembly": foam_carry, "seaflo-pump": seaflo_carry, "suction-chain": chain_carry,
               "discharge-chain": disch_carry,
               "asse1022-assembly": asse_carry, "water-split": split_carry,
               "flow-regulator": flowreg_carry, "vk-solenoid": vk_carry,
               "bulkhead-water": bulkhead_carry, "gasher-co2": gasher_carry,
               "wr1110": wr1110_carry, "digiten-flow": meter_carry, **panel_carries}
    solids = {"foam-assembly": foam, "seaflo-pump": seaflo, "suction-chain": chain,
              "discharge-chain": disch,
              "asse1022-assembly": asse, "water-split": split,
              "flow-regulator": flowreg, "vk-solenoid": vk,
              "bulkhead-water": bulkhead, "gasher-co2": gasher, "wr1110": wr1110,
              "digiten-flow": meter, **panels}
    # The pack's own bodies, so a run may anchor on one or measure off one. The stations answer
    # in `manifold_layout`'s world and ride the pose this module stood them in.
    mcarry = manifold_carry(lift)
    for name, solid, _colour in stood:
        solids[name] = solid
        if name in _lines.STATIONS:
            carries[name] = mcarry
    a.bulkhead_carry = bulkhead_carry
    a.runs = []
    # The bodies and their placements, carried on the assembly: a run whose other mouth is on
    # something the BOX seats is drawn after the box exists, and it anchors on these same frames.
    a.pack_solids, a.carries = solids, carries
    draw_runs(a, _lines.build_runs(solids, carries))
    a.seats = dict(SEATS)
    return a


def draw_runs(a: cq.Assembly, runs) -> None:
    """Sweep each run at its own bore, add it to the assembly, and carry the runs and the port
    frames they were drawn from. Called once for the pack's own runs and again for the ones a
    body the box seats is an end of."""
    for name, solid in _lines.tubes(runs):
        _ROUTED.add(name)
        a.add(solid, name=name, color=C_HOSE)
    a.runs = list(a.runs) + list(runs)
    a.frames = _lines.frames(a.pack_solids, a.carries)


def _solids(a: cq.Assembly):
    """The assembly's children as world-placed solids, keyed by name — the shape a box
    reads a pack in."""
    return {c.name: ((c.obj.val() if hasattr(c.obj, "val") else c.obj).moved(
        cq.Location(c.loc.wrapped.Transformation())), c.color) for c in a.children}


# Bodies seated THROUGH a wall rather than standing inside it. Each one clamps in a hole and
# reaches out the far side, so its box is not a box the interior has to hold — a pack sized to
# contain one is a pack built around its own skin. They come back as stations on the wall
# instead, and the wall is cut for them.
#
# The funnel is the same case and is not listed, because it is added after the box exists
# (`build_front_half`) rather than to the pack.
THROUGH_WALL = ("bulkhead-water", "c14-inlet", "co2-inlet",
                "bulkhead-flavor-a", "bulkhead-flavor-b", "bulkhead-carb")


def pack(a: cq.Assembly = None) -> "_enc.Pack":
    """What the box is SIZED ON: the bodies that have to fit inside it.

    `THROUGH_WALL` is what that excludes, and the funnel is the same case by a different route.

    The station fields left empty are the ones this pack has no body for: the front panel's
    through-holes. Each arrives with the body it is for."""
    a = build_pack() if a is None else a
    placed = _solids(a)
    pan = box(placed["drip-pan"][0])
    west = west_interior_face(placed["compressor-shroud"][0], placed["condenser+fan"][0])
    return _enc.Pack(placed={n: v for n, v in placed.items() if n not in THROUGH_WALL},
                     west_ports=west_wall_ports(pan), pan_rails=pan_rails(pan, west),
                     back_ports=(back_wall_ports(a.bulkhead_carry, *a.panel_carries.values())
                                 + [c14_cutout(), co2_wall_port(a.co2_inlet_carry)]),
                     c14=c14_stations(), east_bosses=a.east_bosses)


def check_through_wall_headroom(a, shell):
    """Raises unless every body seated through a wall still stands under the box's own ceiling.

    `pack` leaves these out of what the box is sized on, which is right in plan — a body that
    reaches out through its own skin cannot also set that skin. IN Z IT LEAVES THEM UNMEASURED,
    and what is inboard of the wall is under the top wall like anything else. The panel deck is
    where that bites: the union's Ø22.86 barrel is the fattest thing the deck carries, so it is
    what touches the ceiling first, and `enclosure._dims` never sees it.

    The ceiling is a STATED bound, so this fails the build rather than lifting it."""
    placed = _solids(a)
    ceiling = shell.inner[5]
    over = [(n, box(placed[n][0]).zmax) for n in THROUGH_WALL
            if box(placed[n][0]).zmax > ceiling + 1e-9]
    if over:
        worst = max(over, key=lambda nz: nz[1])
        raise ValueError(
            f"{worst[0]} reaches z {worst[1]:.2f} but the interior ceilings at {ceiling:.2f} — "
            f"{worst[1] - ceiling:.2f} mm into the top wall. Every body seated through a wall is "
            f"left out of what `enclosure._dims` sizes the box on, so raise "
            f"`enclosure.appliance_height` or drop the storey it stands on: "
            + ", ".join(f"{n} {z:.2f}" for n, z in sorted(over)))


# --- the box those bodies stand in, and what is seated in its walls ---------

WALL_COLORS = {"front-bottom": cq.Color(0.72, 0.74, 0.78, 0.30),
               "front-top": cq.Color(0.80, 0.82, 0.86, 0.30),
               "back-bottom": cq.Color(0.66, 0.68, 0.72, 0.30),
               "back-top": cq.Color(0.74, 0.76, 0.80, 0.30)}


def funnel_centre(box):
    """The funnel collar's centre in plan: (x, y).

    Centred across the box, and pushed as far FORWARD as the display housing allows: the
    ceiling reaches the top face at the facet's back plane, and the collar's front edge
    stands one `enclosure.hopper_front_ledge` of top wall behind that. Nothing else fences
    it — the brim's front flange bears on the housing slab, which is the thickest wall in
    the box, so the throat's stand-off from the housing IS the whole requirement. The basin
    is the first thing behind the glass and the wall a deeper box adds runs behind it, not
    in front. Read off the box, because the box is a consequence of the pack and the facet's
    own depth; `enclosure._hopper_hole` asserts the frame this lands in."""
    ix0, ix1 = box.inner[0], box.inner[1]
    y_front = _enc.facet_back_y(box.outer) + _enc.hopper_front_ledge
    return ((ix0 + ix1) / 2.0, y_front + _funnel.collar_d / 2.0)


def build_funnel(box):
    """The static funnel (`hopper_funnel.py`, its own frame: collar-centre origin, z 0 the
    brim underside) seated in the top-wall opening — turned `FUNNEL_ROT` about its own Z,
    then set at `funnel_centre` with that underside on the box's outer top. `enclosure.py`
    cuts the opening from the same centre, so funnel and hole cannot drift apart.

    THE BRIM RIDES THE CEILING, AND SO DOES THE DRAIN. The basin's underside bears on the top
    wall's outer face and `hopper_funnel.drop` is fixed, so every millimetre off
    `enclosure.appliance_height` is a millimetre off the drain's own height — and what that comes
    out of is the fall `fluid-4` leaves the spout with before its first corner. That corner is
    the last one in the run to reach its stock radius, so THE CEILING IS SPENT ON A BEND: the
    height stands where the drop off the spout to the slot the source pair leaves is still one
    `_lines.TUBE_BEND`, and `bend-radius` on the card is where a ceiling that took one more
    millimetre would show up.

    Returns `(placed, carry)` like every other seated body, so the drain the basin empties
    through rides the basin."""
    cx, cy = funnel_centre(box)
    return seat_body(cq.importers.importStep(str(FUNNEL_STEP)).val(),
                     (((0.0, 0.0, 1.0), FUNNEL_ROT),), seat="hopper-funnel",
                     station=(((0.0, 0.0, 0.0), (0.0, 0.0, 1.0)),
                              (cx, cy, box.outer[5])))


# The display's own frame faces its screen along −Y with the glass on Y = 0; the facet faces
# up-and-forward at `enclosure.display_facet_angle_deg`. One turn about X carries the screen
# normal onto the facet's and the up-screen axis up the slope with it.
DISPLAY_TILT = ((1.0, 0.0, 0.0), -45.0)


def build_display(box):
    """The Waveshare 4.3B let into the display facet — the part that goes in the hole
    `enclosure._display_cuts` already makes, seated off the same numbers so the two cannot land
    on two different centres.

    The glass is the datum. It sits in the bezel counterbore, `display_bezel_depth` deep, so the
    cover glass's own face lies that depth less its own thickness below the 45° surface. The
    BODY hangs behind it, offset on the glass by `display_body_offset_*` because the glass
    overhangs the body unevenly."""
    a, normal, origin, _dy, _dz = _enc._facet_geom(box.outer)
    n = cq.Vector(*normal)                                  # out of the facet, up-and-forward
    x_dir = cq.Vector(1.0, 0.0, 0.0)
    up = cq.Vector(0.0, math.cos(a), math.sin(a))            # up the 45° slope
    glass = (cq.Vector(_enc.display_centre_x(box.outer), origin[1], origin[2])
             - n * (_enc.display_bezel_depth - _disp.bezel_depth))
    seat_pt = (glass
               + x_dir * _enc.display_body_offset_x
               + up * _enc.display_body_offset_slope)
    body = _disp.build_assembly().toCompound()
    placed = (body.rotate(cq.Vector(0, 0, 0), cq.Vector(*DISPLAY_TILT[0]), DISPLAY_TILT[1])
              .translate(seat_pt))
    # Seated on a POINT and not on planes: the datum is the glass, carried off the facet's own
    # geometry and offset onto the body it stands behind, so the ledger's row is that point.
    record_seat("display", turns=(DISPLAY_TILT,), station=seat_pt.toTuple(),
                got=seat_pt.toTuple())
    return placed


def _seated(box):
    """The box with every station its walls carry, seated. Each is read off the box itself,
    so the wall and the body it is cut for come out of one number."""
    return box._replace(funnel=funnel_centre(box))


def machine():
    """The pack, and the box around it. One build: the box is sized on the pack's bodies,
    and then carries the stations they seat in its walls."""
    a = build_pack()
    p = pack(a)
    shell = _enc.box_around(p)
    check_through_wall_headroom(a, shell)
    return a, p, _seated(shell)


def build_front_half() -> cq.Assembly:
    """The pack, what is seated in the walls, and the four printable pieces of the box."""
    a, _p, box = machine()
    funnel, funnel_carry = build_funnel(box)
    a.add(funnel, name="hopper-funnel", color=C_FUNNEL)
    # The basin is not in the pack — the box is sized on the pack and the funnel is seated in
    # the box — so the line it drains through is drawn HERE, off the same frames the pack's own
    # runs anchor on, with the funnel's now among them.
    a.pack_solids["hopper-funnel"], a.carries["hopper-funnel"] = funnel, funnel_carry
    draw_runs(a, _lines.build_seated_runs(a.pack_solids, a.carries))
    # WHERE THE MACHINE'S HEIGHT IS SPENT, recorded against the seat that spends it. The basin's
    # brim bears on the top wall, so the drain hangs a fixed drop under the ceiling and the fall
    # `fluid-4` leaves the spout with is what the run's first corner has to turn its stock radius
    # in. Every millimetre off `enclosure.appliance_height` comes out of this one.
    for r in a.runs:
        if r.id == "fluid-4":
            note_room("hopper-funnel", "the fall off the spout `fluid-4`'s first corner turns in",
                      r.bend, math.dist(r.pts[0], r.pts[1]))
    a.add(build_display(box), name="display", color=C_DISPLAY)
    for name, piece in _enc.build_pieces(box)[0].items():
        a.add(piece, name=f"enclosure-{name}", color=WALL_COLORS[name])
    # The box the pieces were cut from, carried like `runs` and `frames`.
    a.box = box
    a.seats = dict(SEATS)
    return a


def report(a: cq.Assembly) -> None:
    placed = [(c.name, (c.obj.val() if hasattr(c.obj, "val") else c.obj).moved(
        cq.Location(c.loc.wrapped.Transformation()))) for c in a.children]
    named = dict(placed)
    whole = None
    for _n, s in placed:
        b = box(s)
        whole = b if whole is None else whole.add(b)

    def line(label, b):
        print(f"  {label:20} x[{b.xmin:8.2f},{b.xmax:8.2f}] y[{b.ymin:7.2f},{b.ymax:7.2f}] "
              f"z[{b.zmin:7.2f},{b.zmax:7.2f}]   {b.xlen:6.2f} × {b.ylen:6.2f} × {b.zlen:6.2f}")

    print("\nbodies")
    sh, co = box(named["compressor-shroud"]), box(named["condenser+fan"])
    fo, sf = box(named["foam-assembly"]), box(named["seaflo-pump"])
    line("compressor-shroud", sh)
    line("condenser+fan", co)
    pack = None
    for n, s in placed:
        if not _manifold(n):
            continue
        b = box(s)
        pack = b if pack is None else pack.add(b)
    line("manifold-layout", pack)
    line("foam-assembly", fo)
    line("seaflo-pump", sf)
    if "hopper-funnel" in named:
        line("hopper-funnel", box(named["hopper-funnel"]))
    if "suction-chain" in named:
        line("suction-chain", box(named["suction-chain"]))
    if "display" in named:
        line("display", box(named["display"]))
    if "psu" in named:
        line("psu", box(named["psu"]))
    for n in ("pcba", "relay-1", "ac-hub", "ground-stack", "asse1022-assembly", "drip-pan",
              "water-split", "flow-regulator", "vk-solenoid", "bulkhead-water",
              "c14-inlet", "discharge-chain", "co2-inlet", "gasher-co2", "wr1110",
              "bulkhead-flavor-b", "bulkhead-flavor-a", "bulkhead-carb", "digiten-flow"):
        if n in named:
            line(n, box(named[n]))
    walls = None
    for n, s in placed:
        if not n.startswith("enclosure-"):
            continue
        b = box(s)
        walls = b if walls is None else walls.add(b)
    if walls is not None:
        line("enclosure", walls)
    print(f"\nmates (0 by intent)")
    seam = "y" if abs(BASE_YAW) % 180.0 < 1e-9 else "x"
    lo, hi = (sh.ymax, co.ymin) if seam == "y" else (sh.xmax, co.xmin)
    print(f"  shroud face      {seam} {lo:.2f}   condenser intake face {seam} {hi:.2f}   "
          f"gap {hi - lo:.2f}")
    crown = max(sh.zmax, co.zmax)
    pump_face = min(box(s).zmin for n, s in placed if n.endswith("-head"))
    print(f"  base crown       z {crown:.2f}   spine hairpins       z {pack.zmin:.2f}   "
          f"gap {pack.zmin - crown:.2f}")
    print(f"  the pump-head faces stand z {pump_face:.2f}, {pump_face - crown:.2f} mm over the "
          f"crown — that band is what the hairpins reach, and they are aft of the pumps")
    print(f"  the base's own two crowns differ by {abs(sh.zmax - co.zmax):.2f}")
    base_aft = max(sh.ymax, co.ymax)
    print(f"  base aft face    y {base_aft:.2f}   foam front face      y {fo.ymin:.2f}   "
          f"gap {fo.ymin - base_aft:.2f}")
    for cid, frm, to, gap in getattr(a, "refrigerant", []):
        p = a.refrigerant_at[frm][0]
        print(f"  {cid:16} {frm.split('.')[1]:16} on {to.split('.')[1]:16} "
              f"({p[0]:7.2f},{p[1]:7.2f},{p[2]:6.2f})  gap {gap:.3f}")
    print(f"  core crown       z {fo.zmax:.2f}   seaflo floor         z {sf.zmin:.2f}   "
          f"gap {sf.zmin - fo.zmax:.2f}")
    print(f"  core aft face    y {fo.ymax:.2f}   seaflo aft face      y {sf.ymax:.2f}   "
          f"flush by {sf.ymax - fo.ymax:.2f}; it clears the pack by {sf.ymin - pack.ymax:.2f} mm")
    over = [(n, box(s)) for n, s in placed
            if _manifold(n) and box(s).ymax > fo.ymin + 1e-6]
    if over:
        reach = max(b.ymax for _n, b in over) - fo.ymin
        floor = min(b.zmin for _n, b in over)
        print(f"  {len(over)} pack bodies overhang the core by up to {reach:.2f} mm, "
              f"clearing its crown by {floor - fo.zmax:.2f}: "
              + ", ".join(sorted(n for n, _b in over)))
    # Which body each hairpin sets down on, and whether it reaches — the two crowns are not
    # level, so a hairpin over the lower one is bearing on nothing.
    for n, s in sorted(placed):
        if not n.startswith("tube-fluid-"):
            continue
        b = box(s)
        if b.zmin - pack.zmin > 1e-6:
            continue
        on = "shroud" if sh.xmin <= (b.xmin + b.xmax) / 2 <= sh.xmax else "condenser"
        under = sh.zmax if on == "shroud" else co.zmax
        print(f"  {n:16} x {(b.xmin + b.xmax) / 2:7.2f} sets down on the {on:9} "
              f"crown z {under:.2f}  gap {b.zmin - under:.2f}")
    print(f"\nfront half        {whole.xlen:.2f} × {whole.ylen:.2f} × {whole.zlen:.2f}   "
          f"({whole.xlen * whole.ylen * whole.zlen / 1e6:.2f} L)")
    print(f"                  x[{whole.xmin:.2f},{whole.xmax:.2f}] "
          f"y[{whole.ymin:.2f},{whole.ymax:.2f}] z[{whole.zmin:.2f},{whole.zmax:.2f}]")


    _lines.report(getattr(a, "runs", []))

    bad, unanswered = ml.clashes(a)
    print(f"\nclash check: {len(bad)} pair(s) sharing volume, "
          f"{len(unanswered)} the boolean would not answer for")
    for c in bad:
        axis, d = c.where.escape
        print(f"  {c.a} ∩ {c.b}\n      {c.where}   {c.volume:.1f} mm³, "
              f"{d:.2f} on {axis} clears it")
    for ni, nj, why in unanswered:
        print(f"  {ni} ? {nj}   {why}")

    report_seats(a, [n for n, _s in placed if not n.startswith(NOT_A_BODY)])


# How far a face may land off the plane its seat named before the row is off. A plane rule closes
# by construction, so this is import and boolean noise and nothing else — a row over it is a seat
# that named two planes on one axis, or a mouth the turns do not carry where the seat says.
SEAT_TOL = 1e-6
# What is not a body: a length of tube swept along a run, the pack's own placeholder stubs and
# fold segments, and the box's four printed pieces. None of them is seated, so none of them is a
# row the ledger owes.
NOT_A_BODY = ("tube-", "turn-", "step-", "stub-", "enclosure-")


def seat_off(seat) -> float:
    """The worst a seat's own rule missed by, in mm — 0 when every face and every mouth landed
    where the rule named."""
    if "station" in seat.rule:
        return max(abs(g - w) for g, w in zip(seat.got["station"], seat.rule["station"]))
    return max((abs(seat.got[k] - v) for k, v in seat.rule.items() if k in seat.got),
               default=0.0)


def report_seats(a: cq.Assembly, placed_names) -> None:
    """The seat ledger: what each body was closed on, read back off what the closing produced.

    One row per SEAT, not per body — the base pair and the manifold pack are each posed and stood
    as one, so their rule is struck on a combined box and the row names everything it carries.

    `placed_names` is the BODIES: the tubes are swept along a run and the box's four pieces are
    cut out of the shell, and neither is a seated body."""
    seats = getattr(a, "seats", {})
    if not seats:
        return
    held = {n for s in seats.values() for n in s.members}
    loose = sorted(set(placed_names) - held)
    print(f"\nseats             {len(seats)} rules covering {len(held & set(placed_names))} of "
          f"{len(placed_names)} placed bodies")
    for name, s in sorted(seats.items()):
        if "station" in s.rule:
            rule = "mouth → " + ", ".join(f"{v:.2f}" for v in s.rule["station"])
        else:
            rule = " ".join(f"{k} {v:.2f}" for k, v in sorted(s.rule.items()))
        off = seat_off(s)
        turns = "".join(f" {d:+.0f}°" for _ax, d in s.turns) or " —"
        extra = f"  ({len(s.members)} bodies)" if len(s.members) > 1 else ""
        print(f"  {name:22} {rule:44} off {off:8.2e}  turns{turns}{extra}")
        for what, want, got in s.room:
            mark = "—" if got is None else ("✓" if got >= want - 1e-6 else "✗")
            g = "nothing under it" if got is None else f"{got:.3f}"
            print(f"      {mark} {what}: wants {want:g}, has {g}")
    over = [n for n, s in seats.items() if seat_off(s) > SEAT_TOL]
    if over:
        print(f"  {len(over)} seat(s) landed off their own rule: " + ", ".join(sorted(over)))
    if loose:
        print(f"  {len(loose)} body(s) with no seat: " + ", ".join(loose))


def main():
    import _scorecard as _card
    a = build_front_half()
    out = _here.parent / "front-half.step"
    export_assembly(a, str(out))
    print(f"-> {out.name}")
    report(a)
    _card.report(a)
    print(f"-> {_card.write(a, out).name}")
    ml.render_elevations(out, xray="enclosure*")


if __name__ == "__main__":
    main()
