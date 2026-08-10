"""The enclosure assembly — the refrigeration stratum, the flavor manifold standing on it,
and the cold core behind the pair.

Four bodies, mated face to face with nothing between them:

    compressor          its shell's +X tangent against
    condenser+fan       turned onto it, and the pair yawed as one by `BASE_YAW`
    manifold-layout     set down on the crown of those two, on the four SPINE HAIRPINS
    foam-assembly       at the machine's own `FOAM_YAW`, on the floor, its front face on the
                        plane the bodies ahead of it end at

The gaps along that chain are 0 by intent, and where a mating closes a leg of the refrigerant
loop no copper is drawn between the two bodies: the compressor is an oblong can whose two stubs
stand on its own tangent lines, and the condenser is an envelope whose serpentine headers are
re-dressed to reach whichever face is convenient, so such a joint crosses a plane its two bodies
already share and both of its stations are ONE POINT READ TWICE.

THE COMPRESSOR IS THE BODY THAT DOES NOT REACH THE CORE. The condenser is the deeper of the
pair and both are struck on the same centre, so the condenser alone lands on the plane the core
butts and the compressor's plate stands inset from it at both ends. Its suction therefore cannot
be made up across a shared plane, and reaches the evaporator's outlet as cut and brazed copper
that `_lines` draws like any other run. `JOINT_STATIONS` names the two mouths of all three legs;
which of them the machine mates and which it draws is settled by `_lines` having authored a run,
so no leg is read twice and none falls between the two. `refrigerant_joints` takes the reading
over the whole loop at every build — `REFRIGERANT_IDS` is the card's own population — grading a
mating by the gap between its two stations and a tube by how far its two ends stand off the
mouths they are brazed into, and `check_refrigerant_joints` reads red for any leg standing open
and for any leg with no pair of placed stations to measure.

Frame
-----
- X = width, everything centred on x = 0 — the manifold is mirror-symmetric about it.
- Y = depth, 0 at the front. The refrigeration base, then the cold core behind it; on the
  base, the manifold's pumps forward and its two valve decks aft.
- Z = height, 0 at the floor the compressor and the core both stand on.

What the mating does to each body
---------------------------------
The **compressor** keeps the machine's own `COMPRESSOR_YAW`: the can's oil sits in its bottom
and its pickup is gravity-fed, so upright is the compressor's constraint and the turn can only
be a yaw. That yaw lays its discharge tangent EAST at the condenser, its suction tangent NORTH
at the cold core, and its power box at the front.

The **condenser** turns a quarter about Z to bring its west face onto the compressor's tangent.
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
    tools/cad-venv/bin/python hardware/manifold-layout/enclosure_assembly.py
"""

import collections
import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts", _here.parent,
           _hw / "reference" / "compressor",
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
           _hw / "reference" / "asse1022-assembly",
           _hw / "reference" / "flare38-14ptc",
           _hw / "printed-parts" / "enclosure" / "drip-pan",
           _hw / "reference" / "shutao-moisture-plate",
           _hw / "reference" / "mq6-gas-sensor",
           _hw / "reference" / "sf76e-thermal-fuse",
           _hw / "printed-parts" / "refrigeration" / "fuse-clamp",
           _hw / "reference" / "supco-bpv31",
           _hw / "reference" / "mpr121-breakout",
           _hw / "printed-parts" / "flavor" / "cap-sense-sleeve",
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
import _boxes                                         # noqa: E402
import _clearing                                      # noqa: E402
import _lines                                         # noqa: E402
import _overlap                                       # noqa: E402
# The import-time ledger. Every module below that states a bound about its own constants has
# already recorded into it by the time this import list is through, so `carry_stated_bounds`
# reads a complete list. Imported HERE, before them, so the name is bound whichever of them
# reaches for it first.
import _stated_bounds as _stated                      # noqa: E402
import compressor as _comp                            # noqa: E402
import condenser_block as _cond                       # noqa: E402
import copper_plugs as _plugs                         # noqa: E402
import enclosure as _enc                              # noqa: E402
import hopper_funnel as _funnel                       # noqa: E402
import manifold_layout as ml                          # noqa: E402
import seaflo_suction_chain as _suct                  # noqa: E402
import seaflo_discharge_chain as _dis                 # noqa: E402
import waveshare_43b_display as _disp                 # noqa: E402
import asse1022_assembly as _asse                     # noqa: E402
import flare38_14ptc as _oad                          # noqa: E402
import drip_pan as _pan                               # noqa: E402
import shutao_moisture_plate as _plate                # noqa: E402
import mq6_gas_sensor as _mq6                         # noqa: E402
import sf76e_thermal_fuse as _fuse                    # noqa: E402
import fuse_clamp as _clamp                           # noqa: E402
import supco_bpv31 as _bpv                            # noqa: E402
import mpr121_breakout as _mpr                        # noqa: E402
import cap_sense_sleeve as _css                       # noqa: E402
import foam_assembly as _foam                         # noqa: E402
import _cold_core_interface as _cci                   # noqa: E402
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
# The card's own declaration of what the machine owes. Imported for one table —
# `REFRIGERANT_SEGMENTS`, the loop's whole population — so the gate that measures the loop and
# the goal that counts it are populated from ONE list. `_scorecard` reads this module only off
# a built assembly, never by import, so the arrow points one way.
import _scorecard as _card                             # noqa: E402

PSU_STEP = _hw / "reference" / "meanwell-irm90" / "meanwell-irm90.step"
PCBA_STEP = _hw / "printed-parts" / "electronics" / "pcba-tray" / "pcba-board.step"
RELAY_STEP = _hw / "reference" / "teyleten-relay" / "teyleten-relay.step"
MPR121_STEP = _hw / "reference" / "mpr121-breakout" / "mpr121-breakout.step"
GND_STACK_STEP = _hw / "reference" / "ground-ring-stack" / "ground-ring-stack.step"


# Spelled out rather than built from the size, because `web/dev-server/deps.js` finds a
# STEP-load edge by matching the filename as literal text in the script that loads it. A name
# assembled at runtime is a name the scan cannot see, and the edge it would have drawn is what
# rebuilds this assembly when the lever nut's own module changes.
WAGO_STEPS = {
    "413": _hw / "reference" / "wago-221" / "wago-221-413.step",
    "415": _hw / "reference" / "wago-221" / "wago-221-415.step",
    "420": _hw / "reference" / "wago-221" / "wago-221-420.step",
}


def wago_step(size):
    return WAGO_STEPS[size]


# The five lever nuts, in the order the row runs fore to aft. Three carry the mains poles and
# two the 12 V rails; they are one row because they are one part in one kind of well, and the
# wall does not care which conductor a lug splices.
WAGO_POLES = ("wago-h", "wago-n", "wago-g", "wago-v12", "wago-gnd")

# The five DEVICE-CLUSTER lever nuts, as `name: (side, y, z, size)`. Each is the far end of one
# board loom, where a single `COM` or `GND` conductor becomes the fan-out its cluster's devices
# land on — `wiring/ac-wiring-schedule.md` "Loom terminations". So each stands on the flank its
# own cluster stands on rather than beside the board the trunk leaves:
#
#   wago-mana     J1 MANIFOLD A `COM` → V-A…V-H, on the east flank the manifold's own
#                 outboard pair (V-F, V-G) stands against
#   wago-manb     J2 MANIFOLD B `COM` → V-I, V-J, the condenser fan and V-K, mirrored on
#                 the west flank V-I and V-J stand against
#   wago-reeds-b  J7 REEDS B `GND` → reservoir B's four reeds plus the carbonator's two
#   wago-reeds-a  J6 REEDS A `GND` → reservoir A's four reeds
#   wago-sensors  J4 SENSORS `GND` → the 1-wire bus, the DIGITEN meter and the moisture
#                 plate, all three of which land aft and west
#
# The last three run fore to aft down the west wall in the order the cold core's own harness
# does, in the band between the flavour riser under them and the drip tray over them. Every
# station clears the side walls' seam furniture (`enclosure._seam_furniture_spans`) by the
# lever swing as well as the well, so a lug can be worked in place.
CLUSTER_WAGOS = {
    "wago-mana": (+1, 113.0, 290.0, "420"),
    "wago-manb": (-1, 119.0, 275.0, "415"),
    "wago-reeds-b": (-1, 248.0, 296.0, "420"),
    "wago-reeds-a": (-1, 300.0, 310.0, "415"),
    "wago-sensors": (-1, 335.0, 300.0, "415"),
}

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
# The compressor stands UPRIGHT: the can's oil sits in its bottom and the pickup is
# gravity-fed, so upright is the constraint and the only turn it is free in is a yaw. This
# one carries its discharge tangent to +X and its suction tangent to +Y.
COMPRESSOR_YAW = 90.0
# The water pump lies flat on the core's crown. Its barbs are molded into the casting
# and leave its ±Y side faces, so this yaw lands them on the machine's ±X, and lays its
# 187 mm long axis front-to-back.
SEAFLO_YAW = 90.0
# The funnel's spout is on its collar centre, so a turn about Z picks nothing; 0 keeps
# the collar's own axes on the top wall's.
FUNNEL_ROT = 0.0

C_COMP = cq.Color(0.60, 0.62, 0.66)          # the enclosure pack's own three
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
C_PLATE = cq.Color(0.20, 0.55, 0.35)
C_MQ6 = cq.Color(0.25, 0.40, 0.70)
C_FUSE = cq.Color(0.88, 0.72, 0.22)
C_CLAMP = cq.Color(0.30, 0.32, 0.36)
C_BPV = cq.Color(0.78, 0.78, 0.82)
C_MPR = cq.Color(0.20, 0.50, 0.35)
C_SLEEVE = cq.Color(0.30, 0.32, 0.36)
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
Y_AXIS = (cq.Vector(0, 0, 0), cq.Vector(0, 1, 0))


def box(shape):
    # Through `_boxes` rather than straight at the shape. An optimal box costs
    # ~0.2 s on a pack solid and this is the layout's own way of asking for one:
    # the arrangement reads a body's faces every time it stands something against
    # them, and the same body is asked about nine times over a build.
    return _boxes.boxed(shape)


def sit(shape, *, cx=None, y0=None, y1=None, z0=None, dz=None):
    """Move a shape by whole planes: centre it in X, put its near face at `y0` or its far face
    at `y1`, its floor at `z0`, or step it `dz`. Each argument names where a face of its own box
    lands. Hung over the drawn geometry, as `seat_body` hangs it."""
    return shape.moved(cq.Location(_shift(box(shape), cx=cx, y0=y0, y1=y1, z0=z0, dz=dz)))


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
    the metal it is a hole in.

    THE POSE IS HUNG ON THE SHAPE, NOT FOLDED INTO IT. `Shape.rotate` and `Shape.translate` go
    through `BRepBuilderAPI_Transform` and hand back a body whose coordinates ARE its pose;
    `moved` hangs a `TopLoc_Location` over the drawn geometry instead. `_meshes` names a body's
    kept triangles after the shape under that location, so a body that moves is re-seated by a
    matrix multiply rather than re-tessellated: of the pack's 137 solids, 122 keep their
    triangles across a move where 97 did when the pose reached the coordinates."""
    for axis, deg in turns:
        shape = shape.moved(cq.Location(cq.Vector(0, 0, 0), cq.Vector(*axis), deg))
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

    placed = shape.moved(cq.Location(shift))
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
# so the quarter that brings its west face onto the compressor's tangent also lays the fan on +Y,
# and this puts it back across the cabinet.
BASE_YAW = -90.0


def build_compressor():
    """The compressor as the machine turns it, its plate on the floor.

    `(placed, carry)` like every other seated body: its two loop stubs and its four mount
    holes are tables in its own frame and the carry is what puts them in the machine."""
    return seat_body(_comp.build(), (((0.0, 0.0, 1.0), COMPRESSOR_YAW),),
                     cx=0.0, y0=0.0, z0=0.0)


def build_condenser(comp):
    """The block turned a quarter about Z, which brings the WEST face the mating names round
    onto the compressor's own tangent, and stood on the same floor."""
    c = _cond.build()
    c = c.toCompound() if hasattr(c, "toCompound") else c
    return seat_body(c, (((0.0, 0.0, 1.0), 90.0),),
                     cx=0.0, y0=box(comp).ymax, z0=0.0)


# The turn that lays the cutoff's seating plane on a face looking down -Y. Its own frame runs
# the case along X with Z = 0 the generatrix it lies on, and a quarter about X carries that
# generatrix onto the -Y normal with the case's axis left on X — across the box, along the
# cover's own `compressor.POWER_X`.
FUSE_TURN = (((1.0, 0.0, 0.0), 90.0),)
FUSE_FACE_NORMAL = (0.0, -1.0, 0.0)


def power_face_station(comp_carry):
    """The centre of the compressor's power face in the machine, for a body laid flat on it.

    Both bodies that go there — the cutoff and the clamp that holds it — are drawn in ONE frame
    with Z = 0 on that face, and `FUSE_TURN` is the quarter that lays that plane on it. So both
    read this one station, and a yaw that swung the face off −Y is caught once here rather than
    seating one of them on a wall and the other in the open."""
    (pos, normal) = comp_carry(_comp.power_face())
    got = tuple(round(v, 9) for v in normal)
    if got != FUSE_FACE_NORMAL:
        raise ValueError(
            f"the compressor's power face looks {got} in the machine and the cutoff's quarter "
            f"turn lays its contact line on {FUSE_FACE_NORMAL} — the base has been turned out "
            f"from under this pose, and the case is now bedded in the cover rather than on it.")
    return pos


def build_thermal_fuse(comp_carry):
    """The SF76E lying on the compressor's power box, on the station `compressor.power_face`
    states and this carry puts in the machine.

    Seated on ITS OWN CONTACT LINE rather than on a face of its box: what has to land on the
    cover is the generatrix the case touches it along, and the case is round, so its box
    touches the cover at one line and everywhere else stands off it."""
    placed, carry = seat_body(_fuse.build(), FUSE_TURN, seat="thermal-fuse",
                              station=(((0.0, 0.0, 0.0), (0.0, 0.0, 1.0)),
                                       power_face_station(comp_carry)))
    # The case has to land ON the cover, both ways: a case longer than the box is wide, or
    # taller than the box stands, hangs off the face it is there to read.
    note_room("thermal-fuse", "cover either side of the case",
              0.0, (_comp.POWER_X - _fuse.LENGTH) / 2.0)
    note_room("thermal-fuse", "cover above and below the case",
              0.0, (_comp.POWER_Z - _fuse.BODY_D) / 2.0)
    return placed, carry


def build_fuse_clamp(comp_carry, fuse):
    """The printed clamp over the cutoff, on the same station and the same quarter turn.

    ONE STATION FOR THE PAIR. `fuse_clamp` is drawn in the cutoff's own frame — same axis, same
    seating plane — so seating both on the power face's centre is what puts the channel over the
    case, and nothing here restates where either of them goes.

    What holds the clamp there is the compressor's own `POWER_GAP` — the air the power box hangs
    over its plate — which the clamp's two leaves press. Both faces of that slot belong to the
    compressor, so the clamp RIDES THE CAN: the running vibration is common to the clamp, the
    cutoff and the face it presses them onto, and nothing crosses to the cabinet. The plate's
    four holes could not do it — the floor's own posts rise through them and the donor grommet
    in each is the isolation element, so a clamp landing on one of those screws would be fastened
    to the CABINET the cover is moving inside."""
    face = power_face_station(comp_carry)
    placed, carry = seat_body(_clamp.build(), FUSE_TURN, seat="fuse-clamp",
                              station=(((0.0, 0.0, 0.0), (0.0, 0.0, 1.0)), face))
    check_cutoff_bedded(placed, fuse, face)
    return placed, carry


# --- the piercing valve, on the compressor's process tube -------------------
#
# The Supco BPV31 goes on at `assembly/refrigerant-loop.md` step 2 and stays for the life
# of the appliance: it vents the donor's factory R-600a, carries the argon purge from the
# first cut to the start of vacuum, takes the manifold for the pull-down, takes the charge,
# and is then closed and capped. Every later service of the sealed loop comes back to this
# one fitting, so what the placement owes it is REACH — the 2" Supco states the part needs
# to install and operate, measured out of the tube along the valve's own axis, and read as
# `check_bpv_reach`.
#
# The saddle bands the process stub where `compressor.process_tube` states it leaves the
# shell, over the terminal cover. The valve stands UP off it, into the band between the
# compressor's crown and the flavour pack's pump heads, which keeps the whole fitting
# inside the compressor's own plan footprint.
#
# The turn is a single quarter about Z: it lays the part's tube axis on the stub's own Y,
# leaves its valve axis on +Z, and swings the flare port WEST, down the lane between the
# compressor's front and the -X wall.
BPV_TURN = (((0.0, 0.0, 1.0), 90.0),)
# What the stub has to look like in the machine for that turn to mean what it says.
BPV_STUB_AXIS = (0.0, -1.0, 0.0)


def build_bpv31(comp_carry):
    """The BPV31 banded on the process tube, standing up off it.

    Seated on its SADDLE: what has to land in the right place is the clamp's grip on the
    copper, and `compressor.process_tube` is where that copper is. The stub is not drawn,
    the way the suction and discharge stubs are not, so this valve is the only body in the
    machine that says where the process tube runs."""
    pos, axis = comp_carry(_comp.process_tube())
    got = tuple(round(v, 9) for v in axis)
    if got != BPV_STUB_AXIS:
        raise ValueError(
            f"the compressor's process stub points {got} in the machine and this valve's "
            f"quarter turn lays its clamp on {BPV_STUB_AXIS} — the base has been turned "
            f"out from under this pose, and the saddle now bands the tube across its axis "
            f"rather than round it.")
    return seat_body(_bpv.build(), BPV_TURN, seat="bpv31",
                     station=(_bpv.saddle(), pos))


def build_foam(front_y: float):
    """The cold core at the machine's own `FOAM_YAW` and on the machine's own floor, its front
    face on the plane the bodies ahead of it end at. Its native box hangs 20 mm below its
    origin, so the floor is the box's own bottom and not that origin.

    Returns `(placed, carry)` like every other seated body, so the cap's conduit mouths ride the
    placement — a line reaching one is drawn to where the bore actually comes out."""
    f = cq.importers.importStep(str(FOAM_STEP)).val()
    return seat_body(f, (((0.0, 0.0, 1.0), FOAM_YAW),), seat="foam-assembly",
                     cx=0.0, y0=front_y, z0=0.0)


def cap_face(foam):
    """The Z THE CORE PRESENTS TO THE MACHINE — its top lid's outer face, which is the plane
    every body standing on the core is placed off.

    NOT the box's own top, and the difference is the whole of this function: the cap prints a
    valve cradle at each station in `_cold_core_interface.cap_cradles`, those pads stand off
    that face, and so the solid's `zmax` is a valve seat. A body seated on it would be standing
    on one. `foam_assembly` states how far the face stands over the floor the stack is set down
    on, and this reads it there."""
    return box(foam).zmin + _foam.cap_face_over_floor


# --- the gas sensor, low in the refrigeration bay --------------------------
#
# The hardware-only half of the leak backstop: the compressor relay cannot close while this
# board reads gas, and the gate that enforces it is on the PCBA rather than in firmware
# (`assembly/refrigerant-loop.md` "Safety"). What the placement owes that circuit is a board
# standing in the layer a leak actually makes.
#
# R-600A FALLS. It is half again heavier than air, so it leaves whichever brazed joint let it
# go, drops, and spreads over the slab as one layer — and this bay's floor is one connected
# pool: the compressor's plate and the condenser's block stand on it, and the −X strip, the
# channel between them and the slot behind them are all open to each other. Every leak site
# the loop has drains into that one pool, which is why the sensor answers to HEIGHT and not
# to aim. It stands in the strip down the −X flank, the one stretch of floor no body occupies.
#
# THE MESH LOOKS AFT, down the length of that strip, and the header faces fore into the bay
# the front assembly opens onto. That is what standing the card on edge buys. Flat on the wall
# the can would spend the strip's whole depth and the loom would still have to reach a header
# facing the wall behind it; on edge, the reach off the wall is the board's own short side and
# both of its faces are in open air.
#
# The turn is two quarters: −90° about X lays the card down with its can facing aft, then +90°
# about Y stands it back up on its long edge with its short side reaching inboard.
MQ6_STEP = _hw / "reference" / "mq6-gas-sensor" / "mq6-gas-sensor.step"
MQ6_TURN = ((X_AXIS[1].toTuple(), -90.0), (Y_AXIS[1].toTuple(), 90.0))
# What the card's own pin tips stand off the post that fences the fore end of this band. The
# clearance is on the PINS and not on the cradle, because they are what reaches furthest
# forward — the header hangs off the card's fore face and the rails begin behind it.
MQ6_FORE_CLEAR = 2.0


def build_mq6(comp, cond):
    """The MQ-6 on edge in the −X strip, as low as the card stands.

    WEST on the wall's own inner face, not on the boss plane every body on the other flank
    stands on — nothing bolts this card down, it slides into a slot printed on the wall
    (`enclosure._west_cradle`) and bottoms on the wall itself, so the wall is where it goes.

    FORE one `MQ6_FORE_CLEAR` behind the front Z seam's own post. That post is a cross-pin
    column and `enclosure._z_pod` carries it to the floor, so it stands in this band at every
    height a low body would want — `enclosure.front_band_free_y` is where the band reopens
    behind it. The pack's frontmost body is what the front wall stands off, so the two bodies
    on this floor are what the run is struck from.

    LOW on the slab the compressor stands on, one rail section up — which is the whole of what
    lifts it. The mesh comes out under the power box's floor, so the layer reaches this board
    before it reaches the one ignition source in the compartment."""
    body = cq.importers.importStep(str(MQ6_STEP)).val()
    fore, _aft = _enc.front_band_free_y(min(box(comp).ymin, box(cond).ymin))
    return seat_body(body, MQ6_TURN, seat="mq6-sensor",
                     x0=_enc.interior_x()[0], y0=fore + MQ6_FORE_CLEAR,
                     z0=box(comp).zmin + _enc.mq6_rail_wall)


def mq6_cradle(carry):
    """The wall's card-slot station, `(y, z)` — the card's own mid-plane and its centre,
    carried out of the board's frame so the slot cannot land anywhere but on the card.

    Struck on `mq6_gas_sensor.card_plane` and not on the placed box, because the box is the
    pins and the can as well, and its centre is behind the card they hang off."""
    pos = carry(_mq6.card_plane())[0]
    return ((pos[1], pos[2]),)


# --- the bounds the machine states about itself -----------------------------
#
# Several constructions in this module measure a bound the MACHINE STATES rather than a bound
# its own construction meets: every printed valve cradle stands under its valve, every leg of
# the refrigerant loop closes, the vent's drip lands on the basin's flat
# floor, the basin's west lip lands inside the −X wall, the power column stands in the depth the
# +X wall runs free, and a body seated through a wall stands under the box's own ceiling.
# A printed part may state one about itself too: `drip_pan.check_plate` measures the basin's
# flat floor against the moisture plate it receives, and `build_pan` enters that reading here.
# `enclosure` states more of them about the box it draws and keeps
# its own ledger, which `carry_enclosure_bounds` reads into this one. Every one of them can be
# opened by a move made somewhere else in the pack.
#
# A THIRD GROUP IS SETTLED BEFORE ANY OF THIS RUNS. `manifold_layout`, `hopper_funnel` and the
# cold core's own modules state bounds about their CONSTANTS — a screw long enough for its
# insert, a lane wide enough for its bore, two limbs far enough apart for the valves on them —
# and those are read as each file is, with no assembly yet to hang a reading on.
# `_stated_bounds` is the ledger they record into at import and `carry_stated_bounds` reads it
# into this one, so a constant edited into a fault arrives on the same card by the same route
# as a body moved into one.
#
# A VIOLATED BOUND IS A THING TO LOOK AT, and what a reader looks at is the STEP, the three
# elevations and the scorecard a run writes. So none of these stops the build: each hands back
# a `Bound` whether it holds or not, `build_pack` collects them onto the assembly the way it
# collects `seats` and `refrigerant`, and `_scorecard` renders one gate row apiece carrying the
# message the check wrote. The card is committed and a terminal is not, so the red row is the
# louder of the two — and the artifact that shows WHY it is red still exists.

Bound = collections.namedtuple("Bound", "id label ok value target detail")

BOUNDS: list = []


def record_bound(bound: Bound) -> Bound:
    """Enter one bound's reading in the ledger, replacing any of the same id."""
    BOUNDS[:] = [b for b in BOUNDS if b.id != bound.id] + [bound]
    return bound


def check_bpv_reach(bpv_carry, solids) -> Bound:
    """What the piercing valve is left along its own axis, against the 2" Supco asks for.

    *Requires only 2" clearance for installation and operation* is the manufacturer's line
    and `supco_bpv31.SERVICE_CLEAR` is that figure. The valve spends `STANDOFF` of it
    standing up; the rest is the allen key on the needle and the flare nut on the port.

    The column is cast from the TUBE, which is where Supco measures from, at the valve's
    own width across it. What comes back is the first body in the way.

    `pack-closes` reads solids sharing volume and `clearance-floor` holds every pair a
    millimetre apart. A body parked 2 mm over the needle passes both, and the loop is
    charged once and never opened again."""
    pos, axis = bpv_carry(_bpv.saddle())
    who, free = _clearing.cast(pos, axis, _bpv.CLAMP_W, 3.0 * _bpv.SERVICE_CLEAR,
                               solids, skip=("bpv31",))
    ok = free >= _bpv.SERVICE_CLEAR - 1e-6
    # The hose's own lead off the flare port, on the radius the roll aimed it down — the
    # second thing a service call needs, riding the seat rather than the card.
    fpos, faxis = bpv_carry(_bpv.flare())
    _who, port_free = _clearing.cast(fpos, faxis, _bpv.PORT_D, 3.0 * _bpv.SERVICE_CLEAR,
                                     solids, skip=("bpv31",))
    note_room("bpv31", "free straight off the flare port", _bpv.SERVICE_CLEAR, port_free)
    return record_bound(Bound(
        "bpv-reach", "The piercing valve keeps the 2\" Supco asks to work it", ok,
        (f"{free:.2f} mm of column" + ("" if who is None else f", then {who}")),
        f"{_bpv.SERVICE_CLEAR:g} mm off the tube",
        ([] if ok else [
            f"bpv31: the service column off the process tube runs {free:.2f} mm and then "
            f"meets {who}, under the {_bpv.SERVICE_CLEAR:g} mm Supco states the valve "
            f"needs to install and operate. The body alone is {_bpv.STANDOFF:g} of that, "
            f"so what is left over the needle is {free - _bpv.STANDOFF:.2f}. The column "
            f"rises from where `compressor.process_tube` puts the stub; move {who} off "
            f"it, or the loop is charged once and never opened again."])))


def carry_enclosure_bounds() -> None:
    """The bounds `enclosure` states about the box it draws, entered in this ledger — its
    stated width, depth and height against what the pack demands, the two seam planes against
    the print bed and the display housing, and the funnel throat against the frame the top wall
    has left. Same record, same rendering, and the same reason for not raising.

    `enclosure` keeps its own list rather than importing this one, because this module is what
    places the pack it sizes the box on and the import only runs one way."""
    for b in _enc.BOUNDS:
        record_bound(Bound(*b))


def carry_stated_bounds() -> None:
    """The bounds the pack's own modules state about their constants, entered in this ledger.

    They were read when those modules were imported — the manifold's crossbar and limb pitch
    against the valve bodies they carry, the spine turn against its stock, the funnel's collar
    against the grade its floor claims, and the cold core's screws, lanes, conduit columns, cradles
    and plug webs against each other. A raise there would take the STEP, the three elevations and
    this card with it before `build_enclosure_assembly` ran a line, which is why they do not raise;
    this is where they arrive instead.

    `_stated_bounds` keeps the list rather than this module keeping it, because the modules
    that record into it are the ones this module imports and the import only runs one way."""
    for b in _stated.records():
        record_bound(Bound(*b))


# --- the valve cradles printed in the core's cap ---------------------------
#
# Every valve standing on the cap face presses into a cradle printed there
# (`_cold_core_interface.cap_cradles`) — four bosses (`valve_seat`) standing off the lid's own
# off the lid's outer face. The stations live in the CAP'S frame, because a seat belongs to the
# part it is printed in; what this holds is that the printed seat and the placed valve are the
# same place.
#   NOTHING HERE CHOOSES A POSE. Two of the three valves ride the flavour pack, which is stood
# on the refrigeration base's crown, so where they land over this cap is that stack's arithmetic
# and not the cap's — and the third hangs off the pump's suction chain. So the row is
# re-derived off the placed valve at every build, and a build whose valves have moved fails
# with the rows the cap should carry rather than seating them on air.
CRADLE_TOL = 0.001


def _core_frame(foam_carry):
    """The cold core's own frame in world — `(origin, +X, +Y)` — read off the placement the
    core actually took rather than restated from the yaw that produced it."""
    o = cq.Vector(*foam_carry(((0.0, 0.0, 0.0), (0.0, 0.0, 1.0)))[0])
    ex = cq.Vector(*foam_carry(((1.0, 0.0, 0.0), (0.0, 0.0, 1.0)))[0]) - o
    ey = cq.Vector(*foam_carry(((0.0, 1.0, 0.0), (0.0, 0.0, 1.0)))[0]) - o
    return o, ex, ey


def cap_xy(foam_carry, world_xy) -> tuple:
    """A world `(x, y)` in the CAP'S OWN frame — the frame `_cold_core_interface` authors in.

    Two hops: the core's placement carries the assembly's frame, and the cap installs spun a
    half turn inside it (`foam_assembly.spin_xy`), which is its own inverse."""
    o, ex, ey = _core_frame(foam_carry)
    d = cq.Vector(world_xy[0] - o.x, world_xy[1] - o.y, 0.0)
    return _foam.spin_xy((d.dot(ex), d.dot(ey)))


def cradle_rows(foam, foam_carry, placed: dict) -> list:
    """Each cradle as `(name, has, wants)` — the row the cap carries and the row the placed
    valve asks for, both `(x, y, yaw, seat)` in the cap's own frame.

    A valve is read off its own placed box: the Beduan is symmetric about both horizontal axes
    of that box — its four posts, its port and its coil all are — so the box centre IS the seat
    centre, its long horizontal span is the port axis, and its `zmin` is the mounting plane the
    cradle has to put under it."""
    o, ex, ey = _core_frame(foam_carry)
    face = cap_face(foam)
    rows = []
    for name, station in _cci.cap_cradles.items():
        b = box(placed[name])
        # The valve's own spans along the cap's two axes. Both frames are axis-aligned in
        # world, so a span reads off the box directly.
        along = tuple(abs(v.x) * b.xlen + abs(v.y) * b.ylen for v in (ex, ey))
        yaw = 0.0 if along[0] >= along[1] else 90.0
        x, y = cap_xy(foam_carry, ((b.xmin + b.xmax) / 2.0, (b.ymin + b.ymax) / 2.0))
        rows.append((name, station, (x, y, yaw, b.zmin - face), max(along), min(along)))
    return rows


def check_cradles(rows) -> Bound:
    """Whether every cradle the cap prints is under the valve it was printed for.

    The detail is the table: a moved valve prints the row `_cold_core_interface.cap_cradles`
    should carry, so the cap is corrected from the machine and never guessed at."""
    bad, worst = [], 0.0
    for name, has, wants, long_span, short_span in rows:
        off = max(abs(wants[0] - has.centre[0]), abs(wants[1] - has.centre[1]),
                  abs(wants[2] - has.yaw), abs(wants[3] - has.seat))
        lying = (abs(long_span - _beduan.port_length) > CRADLE_TOL
                 or abs(short_span - _beduan.body_width_x) > CRADLE_TOL)
        worst = max(worst, off)
        if off > CRADLE_TOL or lying:
            bad.append((name, wants, lying))
    return record_bound(Bound(
        "cradles-land", "Every printed valve cradle is under the valve it holds", not bad,
        f"{len(rows) - len(bad)}/{len(rows)} seated, furthest off {worst:.3f} mm",
        f"every cradle within {CRADLE_TOL:g} mm",
        ([] if not bad else
         ["the cold core's cap prints a valve cradle where no valve stands — these are the "
          "rows `_cold_core_interface.cap_cradles` should carry. A cradle is a printed seat "
          "and a valve is placed by the pack that carries it, so the cap follows the machine."]
         + [f'    "{n}": Cradle(({w[0]:.3f}, {w[1]:.3f}), {w[2]:g}, {w[3]:.4f}),'
            + ("   \u2190 and this valve is on its side; no cradle in the family holds that"
               if lying else "")
            for n, w, lying in bad])))


# How far a cap valve may stand off the row before the row is not one. The three are placed by
# three different rules — two ride the pack, one is stood on the chain's column — so this is what
# those three rules agree to within.
ROW_TOL = 1e-3


def check_valve_row(placed: dict) -> Bound:
    """The three Beduans on the cap, read across the cap's own face: one depth, one pitch.

    THE PITCH IS THE PACK'S TO GIVE. V-B sits on the manifold's west inner limb and V-K on the
    suction chain's column, and neither of those two answers to the other; what stands between
    them is V-A, which the pack's `manifold_layout.SOURCE_SPREAD` carries outboard. So the
    middle valve is the one number in the row, and the detail names the spread that centres it."""
    row = [(n, box(placed[n])) for n in ("valve-v-b", "valve-v-a", "vk-solenoid") if n in placed]
    if len(row) < 3:
        return record_bound(Bound(
            "cap-valve-row", "The three valves on the cap stand in one row", False,
            f"{len(row)}/3 placed", "three valves", []))
    depths = [b.ymax for _n, b in row]
    pitch = [(row[i + 1][1].xmin + row[i + 1][1].xmax) / 2.0
             - (row[i][1].xmin + row[i][1].xmax) / 2.0 for i in range(2)]
    off_y, off_x = max(depths) - min(depths), abs(pitch[1] - pitch[0])
    ok = off_y <= ROW_TOL and off_x <= ROW_TOL
    detail = [f"{n}: x {(b.xmin + b.xmax) / 2.0:8.3f}   aft face y {b.ymax:8.3f}"
              for n, b in row]
    if not ok:
        centre = ((row[0][1].xmin + row[0][1].xmax) / 2.0
                  + (row[2][1].xmin + row[2][1].xmax) / 2.0) / 2.0
        here = (row[1][1].xmin + row[1][1].xmax) / 2.0
        detail = ([f"the middle valve stands {here:.3f} and the pair either side of it centre "
                   f"on {centre:.3f}; `manifold_layout.SOURCE_SPREAD['V-A']` carries it out "
                   f"from {ml.INNER_X:.3f}, so the row wants {centre - ml.INNER_X:.3f}."]
                  + detail)
    return record_bound(Bound(
        "cap-valve-row", "The three valves on the cap stand in one row, evenly spaced", ok,
        f"pitch {pitch[0]:.3f} / {pitch[1]:.3f} mm, depths within {off_y:.3f} mm",
        f"one depth and one pitch within {ROW_TOL:g} mm", detail))


# How far off contact either end of the pinch may read. A stack drawn to close on the case has
# nothing in it to take up, so this is the closing's own float and nothing else.
BEDDED_TOL = 0.01


def check_cutoff_bedded(clamp, fuse, face) -> Bound:
    """Whether the cutoff's case is actually pinched between the cover and the clamp.

    A body drawn beside another is not a body held against it, and the whole of what makes a
    77 °C cutoff a cutoff is that its case is at the temperature of the face it lies on. So this
    reads the STACK ACROSS THE FACE NORMAL, off the placed solids, in two hops:

        bed    the cover's own plane to the case's near generatrix — 0 is the case ON the face
        grip   the case's far generatrix to the clamp's crown over it — 0 is the clamp ON the
               case, measured by cutting a slab out of the clamp along the case's own axis and
               taking the innermost material in it

    Both at 0 is the pinch closed: cover — case — crown, with the case's whole diameter between
    the face and the clamp and nothing of the clamp inside it. A clamp that drifts out opens
    `grip`; a case that lifts off opens `bed`; a clamp drawn into the case closes `grip` past 0
    and shows up in `pack-closes` as well. NOTHING ELSE ON THIS CARD SEES ANY OF THAT — a clamp
    standing a millimetre proud is a clamp with no clash, no clearance fault and no seat miss,
    and a cutoff reading cabinet air."""
    fb, cb = box(fuse), box(clamp)
    mid_x, mid_z = (fb.xmin + fb.xmax) / 2.0, (fb.zmin + fb.zmax) / 2.0
    bed = face[1] - fb.ymax
    # A slab on the case's own axis, over the case's own length, from the cover's face out past
    # everything the clamp has: what stands in it is the crown and nothing else the part is.
    slab = cq.Workplane("XY", origin=(mid_x, (face[1] + cb.ymin) / 2.0, mid_z)).box(
        _fuse.BODY_L, face[1] - cb.ymin, 2.0 * BEDDED_TOL)
    over, vol = _overlap.common(clamp, slab.val())
    grip = None if vol <= 0.0 else ml.extents(over).ymax - fb.ymin
    ok = abs(bed) <= BEDDED_TOL and grip is not None and abs(grip) <= BEDDED_TOL
    return record_bound(Bound(
        "cutoff-bedded", "The cutoff's case is pinched between the power box and its clamp", ok,
        (f"case on the cover {bed:+.3f} mm, clamp on the case "
         + ("nothing over it" if grip is None else f"{grip:+.3f} mm")),
        f"both 0 within {BEDDED_TOL:g} mm",
        ([] if ok else [
            f"thermal-fuse: the case's contact line stands {bed:+.3f} mm off the power box's "
            f"face at y {face[1]:.2f}, and the clamp's crown "
            + ("stands nowhere over the case at all"
               if grip is None else f"stands {grip:+.3f} mm off the case's far generatrix")
            + f". The pair is seated on ONE station — `power_face_station` — and drawn in one "
            f"frame, so what opens this is `fuse_clamp.CHANNEL_Z` no longer being the case's own "
            f"Ø{_fuse.BODY_D:g}, or a body seated on something other than that station. A "
            f"cutoff off its face reads cabinet air and never opens."])))


# --- The refrigerant loop's joints -------------------------------------------
#
# BOTH ENDS OF EVERY LEG, each a penetration its own module declares — `compressor.stations()`,
# `condenser_block.stations()`, `copper_plugs.slot_stations()`. Nothing here restates a
# coordinate; what this table holds is which two mouths each leg joins, because a station that
# has drifted is copper drawn in the open and no other gate on this pack would say so.
JOINT_STATIONS = {
    "refrig-1": ("compressor.refrig-discharge", "condenser+fan.refrig-inlet"),
    "refrig-2": ("condenser+fan.refrig-outlet", "foam-assembly.evap-inlet"),
    "refrig-3": ("foam-assembly.evap-outlet", "compressor.refrig-suction"),
}
# THE READING IS TAKEN OVER THE WHOLE LOOP AND NOT OVER THAT TABLE. The loop's population is
# the card's own — `_scorecard.REFRIGERANT_SEGMENTS`, the same three connections `routed`
# counts — so a leg with no pair above, or one whose stations are not both placed, comes back
# UNMEASURED and reads red. A circuit cannot go quiet on this gate by leaving one table while
# another still carries it.
REFRIGERANT_IDS = tuple(cid for cid, _f, _t in _card.REFRIGERANT_SEGMENTS)
# THERE ARE TWO WAYS TO MAKE A LEG, and `_lines` drawing a run for it is what decides which —
# so no leg is read twice and none falls between the two. A leg with a run is made in COPPER,
# cut and brazed, and what it owes is the gap between the tube's own two ends and the mouths
# they are brazed into. Every other leg is made by MATING: it crosses a plane two of its bodies
# already share, so its two stations are ONE POINT READ TWICE and what it owes is the distance
# between them. Both readings are millimetres of copper nothing draws, which is why one
# tolerance grades both.
#
# The two words are the card's own (`_scorecard.MADE_AS`), so a leg's reading here and the row
# `routed` prints for it cannot come out under different names.
MADE_BY_MATE, MADE_BY_TUBE = "mate", "drawn"
# How far a leg's own reading may stand open. It is import and boolean noise and nothing else: a
# mating is struck on one plane and a braze seats in its own mouth, so anything above this is a
# station or a tube end that moved.
JOINT_TOL = 0.05

# One leg as the build reads it: which of the two ways the machine makes it, the two stations it
# is made on, and the millimetres that reading leaves open. `mm` is `None` where there is no pair
# of placed stations to read against — unmeasured, which is a third case and not a closed one.
Joint = collections.namedtuple("Joint", "id made frm to mm")


def refrigerant_stations(carries: dict) -> dict:
    """Every station a leg of the loop is made on, in world, keyed `body.port`.

    `carries` is the placement each body was seated by, so a station is its own module's
    table taken through the move the metal took."""
    tables = {"compressor": _comp.stations(),
              "condenser+fan": _cond.stations(),
              "foam-assembly": {f"evap-{end}": st
                                for end, st in (("inlet", _plugs.slot_station("evap-inlet")),
                                                ("outlet", _plugs.slot_station("evap-outlet")))}}
    return {f"{body}.{port}": carries[body](station)
            for body, table in tables.items() if body in carries
            for port, station in table.items()}


def refrigerant_joints(carries: dict, runs=()) -> list:
    """Every leg the loop is, as a `Joint` — the measurement, taken at every build over
    `REFRIGERANT_IDS` and not over `JOINT_STATIONS`.

    WHICH READING A LEG GETS IS THE MACHINE'S ANSWER AND NOT A TABLE'S: a leg `runs` holds a run
    for is read as copper, off the tube's own two ends, and every other leg is read as a mating,
    off the two stations that are meant to be one point. A leg with no pair of placed stations to
    read against carries `None` — which is a reading and not an absence: the connection is still
    owed and the gate still has to account for it.

    A DRAWN LEG CLOSES ON BOTH MOUTHS OR IT CLOSES ON NEITHER, so each of the leg's two stations
    is measured against whichever end of the tube is nearer it. A run re-anchored onto some other
    port leaves the mouth it left behind standing as far open as the port it went to, and the
    same tolerance that grades a mating says so."""
    at = refrigerant_stations(carries)
    drawn = {r.id: r for r in runs}
    out = []
    for cid in REFRIGERANT_IDS:
        a, b = JOINT_STATIONS.get(cid, (None, None))
        run = drawn.get(cid)
        made = MADE_BY_TUBE if run is not None else MADE_BY_MATE
        if a not in at or b not in at:
            mm = None
        elif run is None:
            mm = math.dist(at[a][0], at[b][0])
        else:
            ends = (run.pts[0], run.pts[-1])
            mm = max(min(math.dist(at[m][0], p) for p in ends) for m in (a, b))
        out.append(Joint(cid, made, a, b, mm))
    return out


def refrigerant_mates(joints) -> list:
    """The legs a shared plane CLOSED, as `(id, from, to, mm apart)` — what
    `_scorecard.load_connections` may count as made without a line drawn for it.

    A leg the machine draws is not here and does not belong here: `routed` counts that one off
    the run itself, and counting it twice would let a tube stand in for the mating it is drawn
    instead of. A mating standing open is copper the machine owes, so it belongs with the
    connections still to route and not with the ones already made."""
    return [(j.id, j.frm, j.to, j.mm) for j in joints
            if j.made == MADE_BY_MATE and j.mm is not None and j.mm <= JOINT_TOL]


def check_refrigerant_joints(joints) -> Bound:
    """Every leg of the loop against `JOINT_TOL`, each in the reading its own way of being made
    earns — so the gate accounts for the whole circuit rather than the part of it one
    construction covers.

    A MATING over the tolerance is two stations that were one point on a shared plane and no
    longer are. A DRAWN leg over it is a tube whose end does not land in the mouth it is brazed
    into. Both are a length of copper the machine owes and nothing draws, which is why one
    tolerance grades both.

    A leg with no reading at all is the third case and the one this gate was built for: owed by
    the circuit, made by nothing, and measured by nobody. It reads red and says which leg."""
    mated = [j for j in joints if j.made == MADE_BY_MATE and j.mm is not None]
    drawn = [j for j in joints if j.made == MADE_BY_TUBE and j.mm is not None]
    blind = [j for j in joints if j.mm is None]
    open_mate = [j for j in mated if j.mm > JOINT_TOL]
    open_tube = [j for j in drawn if j.mm > JOINT_TOL]
    widest = max((j.mm for j in joints if j.mm is not None), default=0.0)
    return record_bound(Bound(
        "refrigerant-joints", "Every leg of the refrigerant loop closes, mated or drawn",
        not open_mate and not open_tube and not blind,
        f"{len(mated) - len(open_mate)} mated, {len(drawn) - len(open_tube)} drawn "
        f"of {len(joints)}"
        + (f", {len(open_mate) + len(open_tube)} open" if open_mate or open_tube else "")
        + (f", {len(blind)} unmeasured" if blind else "")
        + f", widest {widest:.3f} mm",
        f"every leg within {JOINT_TOL:g} mm — a mating on its two stations, a tube on both "
        f"its mouths",
        ([] if not open_mate else [
            "the refrigerant loop is made up across the planes its bodies already share, and "
            + ", ".join(f"{j.id} stands {j.mm:.3f} mm open ({j.frm} to {j.to})"
                        for j in open_mate)
            + f" — over the {JOINT_TOL:g} mm a shared plane leaves. That distance is copper "
              f"drawn in the open between two bodies with nothing between them: move the "
              f"station that shifted back onto the one it is read against."])
        + ([] if not open_tube else [
            "the loop's drawn legs are cut and brazed into the two mouths they join, and "
            + ", ".join(f"{j.id}'s tube ends {j.mm:.3f} mm off ({j.frm} to {j.to})"
                        for j in open_tube)
            + f" — over the {JOINT_TOL:g} mm a braze seats in. `_lines` draws that run to "
              f"somewhere other than the mouths this leg joins, so one of them has nothing "
              f"brazed into it: anchor the run on the leg's own two stations, or move the "
              f"station the tube no longer reaches."])
        + ([] if not blind else [
            "the loop owes "
            + ", ".join(j.id for j in blind)
            + f" and nothing on this pack measures {'them' if len(blind) > 1 else 'it'}: "
              f"`JOINT_STATIONS` names no pair of stations for "
              f"{'those ids' if len(blind) > 1 else 'that id'}, or a station it names is not "
              f"placed — so neither a mating nor a tube can be read against them. `routed` "
              f"counts the same {len(joints)} connections "
              f"(`_scorecard.REFRIGERANT_SEGMENTS`), so {len(blind)} of {len(joints)} legs of "
              f"the circuit {'are' if len(blind) > 1 else 'is'} made by nothing rather than the "
              f"circuit having fewer joints — give each the two mouths it joins, and mate them "
              f"or draw the run between them."])))


MOUNT_TOL = 0.001


def pump_mount_rows(foam_carry, seaflo_carry) -> list:
    """Each of the pump's four mounting bores against the cap column bored for it, as
    `(has, wants)` in the cap's own frame.

    `wants` is the bore taken through the pump's placement and back into the cap's frame;
    `has` is the station `_cold_core_interface.deck_mounts` prints. Both are re-derived off the
    placed pump at every build, the same way the valve cradles are, because the pump is stood on
    the core's crown by this module and the column is printed by a part that never sees it."""
    printed = sorted(_cci.deck_mount_xy("seaflo-pump"))
    wanted = sorted(cap_xy(foam_carry, seaflo_carry(
        ((hx, hy, _lines._pump.mount_seat_z()), (0.0, 0.0, 1.0)))[0][:2])
        for hx, hy in _lines._pump.mount_holes())
    return list(zip(printed, wanted))


def check_pump_mount(rows) -> Bound:
    """Whether every column the cap bores stands under the bore it takes a screw through.

    The detail is the row `_cold_core_interface.deck_mounts` should carry, so a pump that has
    moved corrects the cap from the machine rather than being guessed at."""
    off = max((max(abs(h[0] - w[0]), abs(h[1] - w[1])) for h, w in rows), default=None)
    xs = sorted({round(w[0], 4) for _h, w in rows})
    ys = sorted({round(w[1], 4) for _h, w in rows})
    return record_bound(Bound(
        "pump-mount-lands", "Every cap column the water pump bolts to is under its own bore",
        bool(rows) and off is not None and off <= MOUNT_TOL,
        "no column bored" if not rows else f"{len(rows)} columns, furthest off {off:.3f} mm",
        f"every column within {MOUNT_TOL:g} mm of the bore over it",
        ([] if rows and off is not None and off <= MOUNT_TOL else [
            "the cold core's cap bores the columns the pump's bracket bolts down into, and the "
            "pump is stood on that cap by this module — so the cap follows the machine. This is "
            "the row `_cold_core_interface.deck_mounts` should carry:",
            f'    "seaflo-pump": DeckMount(({(xs[0]+xs[-1])/2:.2f}, {(ys[0]+ys[-1])/2:.2f}), '
            f'{xs[-1]-xs[0]:.2f}, {ys[-1]-ys[0]:.2f},   0.0,  8.50, 16.0),'])))


def cap_conduit(name: str):
    """One of the cold core's cap conduits as a station in the CORE'S OWN frame:
    `((x, y, z), outward axis)`.

    `foam_assembly` authors the bore in the cap's frame and turns it back through the cap's own
    half-turn install, so its `(x, y)` is already the assembly's; the mouth's Z is the lid's
    outer face, which is the top of that same solid. The way out is the cap's +Z."""
    x, y = _foam.cap_conduit_station(name)
    return ((x, y, _foam.cap_face_z), _foam.cap_conduit_axis_out())


def build_seaflo(foam):
    """The water pump at the machine's own `SEAFLO_YAW`, lying flat on the core's crown, centred
    on the mirror plane, its aft face flush with the core's own back."""
    b = box(foam)
    return seat_body(cq.importers.importStep(str(SEAFLO_STEP)).val(),
                (((0, 0, 1), SEAFLO_YAW),), seat="seaflo-pump",
                cx=0.0, y1=b.ymax, z0=cap_face(foam))


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
def build_discharge_chain(split, flowreg, seaflo_carry):
    """The chain laid in the lane west of the pump, on the discharge's own plane.

    Its three coordinates answer to the run it carries and the lane it lies in: X one
    `DISCH_SPLIT_CLEAR` east of the split's own east face, Y standing its barb one
    `DISCH_CORNER_ROOM` forward of the pump's discharge mouth, and Z ON THAT MOUTH'S OWN
    PLANE — the barb fires due west and the chain's axis lies at its height, so `water-6`
    turns once in plan and climbs nothing. `_lines._water_6` is where that plane is held: the
    hose's two legs seat one `HOSE_BEND` apiece and no more, so it takes no fall at all.

    THE COLLET FIRES AT THE FLOW REGULATOR'S BACK, on the storey that body stands on. What its
    straight comes to against the 2 × `TUBE_BEND` a collet asks for is the `port-leads` row for
    `discharge-chain.tube-port`, read there off the regulator's own solid.

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
# Clear wall between two nuts on this face: a hand has to get a socket onto each one after its
# neighbour is made up. The wall spends it, so it is stated here and `_enclosure_mechanical_sync`
# prices its row of nuts off it.
PORT_NUT_GAP = 7.0
# What the two columns carry BESIDE their nuts, and it is wider than they are: the ASSE chain
# hangs off the west column and the DIGITEN meter lies on the east one, both on the deck's own
# storey and both broader about their column than a union's nut. `clearance-floor` measures that
# pair, and this is the extra the pitch carries for them. It is what stands between the chain's
# own east corner and the meter's west face, and a bracket closing on either body reaches across
# it — so the pitch buys a working lane between the two bodies and not just air between two nuts.
PORT_DECK_EXTRA = 7.5
# The pitch two columns stand at — each fitting's own panel footprint, the gap two nuts need, and
# what the bodies hanging off them ask for over that.
PORT_PITCH = _jg.panel_footprint()[0] + PORT_NUT_GAP + PORT_DECK_EXTRA
# THE WEST LANE CARRIES TWO COLUMNS AND EVERY UNION IS ON ONE OF THEM. The lane runs from the −X
# wall's inner face to the pump's casting, and the two nozzle unions stand side by side across it
# at `PORT_PITCH` — so `check_port_pair` is where that span is measured, against the wall on one
# flank and the casting on the other.
#
# THE EAST COLUMN IS THE ONE THE PUMP FENCES. It stands as far east as the casting leaves it at
# the nozzle storey, and the west column takes one pitch beyond that. Swept over the wall by
# dropping the union's own body down the lane:
#
#     enclosure_assembly.pump_west_face(seaflo, z0, z1, bulkhead_mouth_y(), rear_plane_y)
PORT_LANE_CLEAR = 1.0
# The west column, and the widest body it carries: the ASSE chain hangs off the tap-water union
# on this column and is broader than any union, so it is what stands the pair off the wall's own
# ribs. `check_port_pair` measures both flanks of the pair against the lane they are given.
#
# THE EAST COLUMN IS WHERE THE TWO OF THESE LEAVE IT. This number and `PORT_DECK_EXTRA` both
# reach it — one as the origin the pitch is measured from, the other as a term of that pitch —
# so the storey's east column stands at `PORT_WEST_COLUMN + PORT_PITCH` = -45.64 and reading it
# off the pair is how a change to either is checked against the flank the pump fences.
PORT_WEST_COLUMN = -83.0
PANEL_X = {"bulkhead-flavor-b": PORT_WEST_COLUMN,
           "bulkhead-flavor-a": PORT_WEST_COLUMN + PORT_PITCH,
           "bulkhead-carb": PORT_WEST_COLUMN + PORT_PITCH}
# What a union's barrel keeps off the pump's BRACKET where the two pass. The feet are the widest
# section the casting has and they are only `seaflo_22_pump.FOOT_T` tall — above them the casting
# steps back across the machine and the port lane opens by twenty millimetres. So a barrel
# carried over the feet has the lane and one struck through them does not.
PORT_FOOT_CLEAR = 1.0


def nozzle_storey(gate: float, seaflo) -> float:
    """The storey the two nozzle unions cross the wall on: their own runs' cruise lane, or the
    plane that carries their barrels over the pump's bracket, whichever is higher."""
    return max(gate, box(seaflo).zmin + _lines._pump.FOOT_T
               + PORT_FOOT_CLEAR + _jg.BODY_D / 2.0)
# THE WEST COLUMN CARRIES THE TAP WATER UNION TOO, one storey up: the chain, the split, the
# regulator and the drip tray under the vent all hang off that union, and the column is what
# stands them in the lane.
#
# THE STOREY THE NOZZLE UNIONS TAKE IS THEIR OWN RUNS'. `fluid-28` and `fluid-18` cruise the
# outboard lanes at `_lines.gate_cruise` — the plane the two gates climb to under the reservoir
# lines that cross their columns — so a union standing there is reached by a leg that crosses to
# its column without changing height, and each run's last move into its collet is flat. It also
# carries both barrels clear under the drip tray's channel.
PANEL_ON_GATE_LANE = ("bulkhead-flavor-b", "bulkhead-flavor-a")


def check_port_pair(placed, west_face, seaflo) -> Bound:
    """The two nozzle unions across the west lane, measured against the two things that fence it:
    the −X wall's inner face on one flank and the pump's own casting on the other, read at the
    storey the pair stands on."""
    pair = [box(placed[n]) for n in PANEL_ON_GATE_LANE]
    lo, hi = min(b.xmin for b in pair), max(b.xmax for b in pair)
    face = pump_west_face(seaflo, min(b.zmin for b in pair), max(b.zmax for b in pair),
                          bulkhead_mouth_y(), _enc.rear_plane_y)
    left, right = lo - west_face, face - hi
    got = min(left, right)
    ok = got >= PORT_LANE_CLEAR - 1e-6
    return record_bound(Bound(
        "port-pair", "The nozzle unions' pair stands inside the west lane", ok,
        f"{left:.3f} mm to the wall, {right:.3f} mm to the casting",
        f"{PORT_LANE_CLEAR:g} mm each flank",
        ([] if ok else [
            f"the nozzle pair spans x[{lo:.2f}, {hi:.2f}] between a wall at {west_face:.2f} and "
            f"the pump's casting at {face:.2f} — {got:.3f} mm on its tightest flank. The span is "
            f"one `PORT_PITCH` plus a barrel; move `PANEL_X`'s two nozzle columns, or give the "
            f"pair back the width by moving the pump."])))


def panel_z(name: str, deck: float, gate: float) -> float:
    """The storey one union of the row crosses the wall on — the deck, or its own run's lane."""
    return gate if name in PANEL_ON_GATE_LANE else deck


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

def build_deck(z: float, gate: float, seat: bool = False):
    """The four bodies the deck carries off the storey `z`: the three unions across the back
    wall, each on its own `panel_z`, and the meter inline one `CARB_2` ahead of the carb one.

    One function, called with a trial storey to strike the deck and again with the struck one to
    place it, so the bodies the strike measures are the bodies the machine gets. `seat` is what
    tells the two apart for the ledger: the trial is a MEASUREMENT and not a pose, and only the
    placement the machine keeps is entered."""
    solids, carries = {}, {}
    for name, px in PANEL_X.items():
        solids[name], carries[name] = build_panel_bulkhead(
            name if seat else None, px, panel_z(name, z, gate))
    solids["digiten-flow"], carries["digiten-flow"] = build_digiten(
        carries["bulkhead-carb"], seat=seat)
    return solids, carries


def descent(body, under, limit=DECK_FALL_LIMIT):
    """How far `body` falls before it lands on one of `under`, or `None` if it never does.

    EXACT STRIDES, not a grid. `_clearing.gap` is 1-Lipschitz under translation, so advancing the
    body by its own current gap cannot step over a contact: the walk closes on the landing itself
    rather than sampling near it, and a body that never lands says so instead of reporting the
    limit as a clearance.

    THE HORIZON IS THE FALL THE BODY HAS LEFT, and a reading that reaches it is read as the
    fall running out rather than as a contact. A gap asked for no further than nothing comes
    back 0.00, which is the same 0.00 a landing reads, so the two are told apart by which
    question was asked and not by what came back. The body is carried by `offset` rather than
    rebuilt at each station: it is the same body at every one of them."""
    best = None
    for other in under:
        t = 0.0
        while t < limit:
            room = limit - t
            g = _clearing.gap(body, other, room, offset=(0.0, 0.0, -t))
            if g >= room:                    # at least the whole remaining fall away
                break
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


# The zip tie's own stock, and the room it needs to lie in. Two of them shut the mouth of the
# trough the chain lies in (`asse_cradle`), and a tie is a closed loop: the strap has to cross
# the chain's top flat, which is the highest thing on this storey. The strap is THREADED through
# the trough's bore and then LAID across this channel — the piece prints ceiling-down and is
# populated the same way up, so the strap lies on the ceiling's inner face and the chain comes
# down onto it. Nothing is pulled through here, which is why the room is a clearance and not a
# working reach.
ASSE_TIE_T = 1.0
ASSE_TIE_CLEAR = 0.5
# What the tap-water chain's crown keeps under the top wall's inner face. The appliance's height
# is STATED (`enclosure.appliance_height`) rather than grown from the pack, so this ceiling is a
# fixed plane and the storey under it is a room the deck can be given rather than one it takes.
#
# IT IS GIVEN TO THE TIE, and to nothing else. A millimetre here is a millimetre of air the pack
# cannot use for anything, so the number is the one thing that has to pass through it — and the
# wall is never cut for it. `enclosure.wall` stays whole over this band; the storey moves instead,
# which costs the deck's own headroom and is measured by `check_deck_floor`.
DECK_CEILING_CLEAR = ASSE_TIE_T + ASSE_TIE_CLEAR


def interior_ceiling() -> float:
    """The plane the top wall's inner face lies on, off the appliance's own stated height."""
    return _enc.appliance_height - 2.0 * _enc.wall


def asse_crown_over_axis() -> float:
    """How far the ASSE chain's body stands over the tube axis its two collets are on — the
    tallest thing the deck's storey carries. The yaw that lays the chain down the lane is about
    Z, so this reads the same turned or not."""
    chain = _asse.build()
    chain = chain.toCompound() if hasattr(chain, "toCompound") else chain
    chain = chain.val() if hasattr(chain, "val") else chain
    return box(chain).zmax - _asse.port("tube-in")[0][2]


def check_deck_floor(z: float, floor) -> Bound:
    """The deck against the storey the descent leaves under it — the lowest it may lie."""
    ok = floor is None or z >= floor - 1e-6
    return record_bound(Bound(
        "deck-floor", "The panel deck lies over the storey its own descent leaves", ok,
        "nothing lands under it" if floor is None else f"deck {z:.2f}, floor {floor:.2f}",
        "the deck at or over its floor",
        ([] if ok else [
            f"the panel deck lies at z {z:.2f} and the row it carries wants {floor:.2f} to keep "
            f"one DECK_CLEAR = {DECK_CLEAR:g} over what it would land on. The ceiling sets the "
            f"deck through `asse_crown_over_axis`; the floor is the descent."])))


def deck_z(placed, gate: float):
    """The Z the panel deck lies on: the top of the band its own two bounds leave it.

    THE CEILING BINDS AND THE STOREY TAKES IT. Everything hanging off this storey wants the
    height — the chain, the split and the regulator on the chain's own axis, and the drip tray
    under the vent, which has the pump's bracket to clear — so the deck lies as high as the top
    wall lets the chain's crown. `check_deck_floor` is where the other bound is made.

    `placed` is everything already standing, which is what the row would come down onto. The
    trial storey they are dropped from is that pack's own crown, one union half-section — the
    fattest the deck carries — and a clearance over it, so each starts in air whatever stands
    below it, and the floor is that trial less what the first of them to land would fall.

    ONLY THE BODIES THE STOREY MOVES. A union on `PANEL_ON_GATE_LANE` stands on a plane of its
    own and rides the trial nowhere, so its fall says nothing about where the deck can go; it
    would answer with the distance from its own fixed storey and drag the strike up to the trial.
    `build_pack` measures that one's own room against what is under it instead, and the row it
    enters `room-holds` with reads the same as the rest.

    Returns `(z, {body: the fall it still has at that storey})`. The second is the band this
    strike states — one body is left standing on exactly `DECK_CLEAR` and the rest on whatever
    their own descent leaves — and it is what the ledger's `room` side records."""
    z = interior_ceiling() - asse_crown_over_axis() - DECK_CEILING_CLEAR
    trial = max(box(s).zmax for s in placed) + DECK_CLEAR + _jg.BODY_D / 2.0
    falls = {name: descent(s, _would_land_on(box(s), placed))
             for name, s in build_deck(trial, gate)[0].items()
             if name not in PANEL_ON_GATE_LANE}
    landing = [d for d in falls.values() if d is not None]
    check_deck_floor(z, trial - min(landing) + DECK_CLEAR if landing else None)
    return z, {n: None if d is None else d - (trial - z) for n, d in falls.items()}


# --- the mains inlet, through the back wall --------------------------------
#
# The C14 the customer's cord plugs into. It lands FROM INSIDE — the flange bears on the wall's
# inner face and two screws hold it there — so its housing stands in the box and only the shroud
# reaches out through the cutout. Its own frame already faces the mating axis down +Y with the
# seating plane on Y = 0, which is what the back wall gives it, so it takes no turn either.
C14_STEP = _hw / "reference" / "iec-c14-inlet" / "iec-c14-inlet.step"
# Where it sits on that wall. The receptacle's wires reach the Wago row, so it wants that row's
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
STANDALONE = ("compressor", "condenser+fan", "foam-assembly", "seaflo-pump",
              "hopper-funnel", "suction-chain", "discharge-chain", "display", "psu", "pcba",
              "relay-1", "relay-2", "ground-stack", "asse1022-assembly", "drip-pan",
              "moisture-plate", "mq6-sensor", "thermal-fuse", "fuse-clamp", "bpv31",
              "mpr121", "cap-sleeve-a", "cap-sleeve-b",
              ) + WAGO_POLES + tuple(CLUSTER_WAGOS) + (
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
# The power column hangs ON the +X wall, not off it. Its seat is one `enclosure.mount_boss_out`
# inboard of the interior face the STATED `appliance_width` opens — the length of an M3
# heat-set and the air past the screw tip, and nothing else, because that is the whole of what
# a boss carrying a body has to be. The wall's inner face is what caps the bore's blind end.
#
# The seam's own furniture caps a whole `enclosure.boss_in` further inboard, so a body seated
# here stands INSIDE the band the rail's columns occupy. It gets away with that because those
# columns stand only where the seam puts them: the Y-seam corner column at one end and the
# rear wall's cross-pin column at the other, with the wall's own air between. That free depth
# is `enclosure.east_band_free_y`, and every body on this flank is placed inside it — which is
# what `PSU_REAR_CLEAR` closes the column's aft end on.
#
# Read off the wall and not off the pack, so a body here can be seated before the box that
# carries it has been sized, and nothing arriving on the floor moves it afterwards.

def east_wall_seat():
    """The plane a body hung on the east wall stands its outer face on: one
    `enclosure.mount_boss_out` inboard of the stated wall, which is its own boss and no more.

    Read off the wall and not off whichever body is widest on the floor. The boss is built on
    the wall, so a body that seats on the boss's own tip seats on the wall whatever else is
    packed beside it — and a narrower body arriving on the floor moves neither."""
    return _enc.interior_x()[1] - _enc.mount_boss_out


def floor_mounts(*mounted):
    """The floor slab's boss stations, as `(x, y, tip)`.

    `wall_mounts`' analogue for a body bolted DOWN onto the slab rather than hung on the
    flank. One `(carry, holes, face_z)` per body: the placement, the body's own hole pattern,
    and the height in that body's own frame of the face a screw head lands on. A body standing
    on the floor has that face at the TOP of whatever the hole passes through, not at its own
    Z = 0 — the post rises through the hole to it, which is what locates the body as well as
    fastens it."""
    out = []
    for carry, holes, face_z in mounted:
        for hx, hy in holes:
            pos, _axis = carry(((hx, hy, face_z), (0.0, 0.0, 1.0)))
            out.append((pos[0], pos[1], pos[2]))
    return tuple(out)


def west_interior_face():
    """The −X wall's own inner face, off the stated width — the same face `enclosure._dims`
    builds the box on."""
    return _enc.interior_x()[0]


# The brick lies on its side against that wall: a quarter about Y stands its 52 mm width up as
# height and lays its 33.5 mm depth across the machine, so only that much of the lane reaches
# inboard and its 109 mm long axis runs fore and aft down the flank.
PSU_TURN = (((0.0, 1.0, 0.0), -90.0),)
# What the brick stands off the rear wall's cross-pin column, which is where the free depth on
# this flank ENDS: standing on the wall, the whole power block is inside that column's own band,
# so the column is the aft face the block closes on and not the rear seam behind it.
#
# IT IS ZERO, AND THAT IS THE PRICE OF RELAY #2. Three bodies now stand in this band where two
# did — board, relay, brick — and what they leave over is every gap there is. Spent aft, the
# relay has nowhere to stand; spent between the bodies it clears `STACK_CLEAR` either side of
# it. So the brick closes on the column, and its AC screw block is made off from INBOARD, off
# the open lane, rather than from behind. What the band has left is the `east-band` gate's to
# report, off the placed column, every run.
PSU_REAR_CLEAR = 0.0


def build_psu(foam, wall_seat):
    """The MeanWell brick on the +X wall, standing on the cold core's cap.

    Three faces of the machine and not three numbers: EAST on the wall seat, AFT one
    `PSU_REAR_CLEAR` ahead of where `enclosure.east_band_free_y` ends, FOOT on the cap's own
    lid. The lane it lies in is what the SeaFlo leaves east of itself on that cap."""
    return seat_body(cq.importers.importStep(str(PSU_STEP)).val(), PSU_TURN, seat="psu",
                     x1=wall_seat,
                     y1=_enc.east_band_free_y()[1] - PSU_REAR_CLEAR,
                     z0=cap_face(foam))


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


def build_pcba(foam, ahead_of, wall_seat):
    """The controller board on the +X wall, forward of whatever the brick's column presents.

    EAST on the same wall seat the brick takes, so the two stand in one plane and one length of
    boss holds them both; AFT one `STACK_CLEAR` ahead of `ahead_of`'s own front face — which is
    relay #2, not the brick, since the relay stands between them; FOOT on the cap. What holds it
    is the pcba-tray, which is not placed — this is the board's envelope."""
    return seat_body(cq.importers.importStep(str(PCBA_STEP)).val(), PCBA_TURN, seat="pcba",
                     x1=wall_seat, y1=box(ahead_of).ymin - STACK_CLEAR, z0=cap_face(foam))


# The rest of the power block, on the two crowns: relay #1 on the BOARD'S crown with the ground
# stud one clearance forward of it, and the five Wago wells on the BRICK'S. Each takes the same
# wall seat as its east face, so the whole group stands on one plane against the wall, in the
# depth `enclosure.east_band_free_y` leaves between the seam's two columns — the lever nuts
# excepted, which seat on the wall itself because a well is not a boss.
#
# Each turn lays the body's own long axis fore and aft down the flank and its board facing
# INBOARD — the face a screwdriver reaches, and the face a boss would land on.
RELAY_TURN = (((0.0, 0.0, 1.0), 270.0), ((0.0, 1.0, 0.0), 270.0))
# The floor between one body on this column and the next, and it is not air for its own sake:
# what stands in it is the WALL BOSS that fastens the body between them. The relay is the body
# that sets it — its mount pattern runs closest to its own edge, so the boss standing on that
# pattern reaches furthest past the board — and the gap is that reach with a clearance past it.
STACK_CLEAR = (_enc.mount_boss_dia / 2.0
               - (_relay.width / 2.0 - _relay.hole_dy) + 1.0)


# Relay #2 stands the same body ON END: a further quarter about X carries its long axis from
# fore-and-aft onto Z, so it presents 17 mm of depth to the band instead of 70. That is the only
# way a third body fits between the board and the brick, and standing it costs nothing — its
# screw block and its header end up one above the other, both facing the room.
RELAY2_TURN = RELAY_TURN + (((1.0, 0.0, 0.0), 90.0),)
# A lever nut turned for the WALL: the quarter about X stands it butt-first as the hub did, and
# the quarter about −Y lays its wire-entry axis onto −X, so it presses west into the wall's own
# well with its ports and levers facing the room. Its 18.8 mm lever-hinge axis stands on Z and
# its 8.4 mm body lies along Y — the narrow face to the row, which is what fits five of them in
# the depth three would take lying the other way.
WAGO_TURN = (((1.0, 0.0, 0.0), 90.0), ((0.0, 1.0, 0.0), -90.0))
# The same lug for the WEST wall: the quarter about +Y instead of −Y lays its wire-entry axis
# onto +X, so it presses east and its ports again face the room.
WAGO_TURN_WEST = (((1.0, 0.0, 0.0), 90.0), ((0.0, 1.0, 0.0), 90.0))
# What the Wago row stands off the brick's crown, and what the relay above it stands off the row.
WAGO_CLEAR = STACK_CLEAR


def _wago_skirt(size="413"):
    """What a well reaches PAST its lug on the row's cross axis — the wall it wraps the lug in,
    plus that wall's press clearance.

    The lug is what gets placed and the WELL is what can foul a neighbour, and the well is the
    bigger of the two. Clearing the brick's crown by the lug's own bottom face would bury the
    skirt in it, so every clearance struck against this row is struck against the tower."""
    return _enc.wago_half(size)[1] - _enc.wago_stand(size)[1] / 2.0


def build_relay2(psu, foam, wall_seat):
    """Relay #2 on end, in the band between the brick and the board.

    EAST on the wall seat every body on this flank takes; AFT one `STACK_CLEAR` ahead of the
    brick's own front face; FOOT on the cap, the same lid the brick and the board stand on. It
    is the body the band was reorganised around — see `PSU_REAR_CLEAR`."""
    return seat_body(cq.importers.importStep(str(RELAY_STEP)).val(), RELAY2_TURN, seat="relay-2",
                     x1=wall_seat, y1=box(psu).ymin - STACK_CLEAR, z0=cap_face(foam))


def build_wago_row(psu, wall_seat):
    """The five 221-413 lever nuts on the brick's crown, as `[(name, solid, carry)]`.

    They are the only bodies on this flank that no boss holds: each presses into a well printed
    on the wall itself (`enclosure._side_wells`), so what locates them is the wall, and what this
    places is the lug that goes in it. The row runs fore and aft on the brick's own depth,
    CENTRED on it, one `WAGO_CLEAR` over its crown.

    THEY SEAT ON THE WALL AND NOT ON `east_wall_seat`. Every other body on this flank stands its
    outer face on a boss TIP, one `mount_boss_out` inboard of the wall, because a boss is what
    holds it. Nothing holds a lever nut but the pocket, and the pocket bottoms on the wall — so
    the lug's butt goes to `interior_x`, and seating it on the boss plane instead would leave it
    floating that same `mount_boss_out` clear of the well built to receive it."""
    pb = box(psu)
    span = 5 * _enc.wago_pitch
    y0 = (pb.ymin + pb.ymax) / 2.0 - span / 2.0
    out = []
    for i, name in enumerate(WAGO_POLES):
        solid, carry = seat_body(cq.importers.importStep(str(wago_step("413"))).val(), WAGO_TURN,
                                 seat=name, x1=_enc.interior_x()[1],
                                 y0=y0 + i * _enc.wago_pitch + _enc.wago_well_wall,
                                 z0=pb.zmax + WAGO_CLEAR + _wago_skirt())
        out.append((name, solid, carry))
    return out


def build_cluster_wagos():
    """The five device-cluster lever nuts, as `[(name, solid, carry, size)]`.

    Each is stationed on the flank of the cluster it fans out to (`CLUSTER_WAGOS`) and seats the
    same way the row on the brick's crown does: the butt goes to `interior_x` on its own side,
    because the pocket bottoms on the wall and the wall is the datum. The station names the well's
    CENTRE, so the lug is placed off its own half rather than a face."""
    out = []
    for name, (side, y, z, size) in CLUSTER_WAGOS.items():
        stand_y, stand_z, _sx = _enc.wago_stand(size)
        turn = WAGO_TURN if side > 0 else WAGO_TURN_WEST
        face = {"x1": _enc.interior_x()[1]} if side > 0 else {"x0": _enc.interior_x()[0]}
        solid, carry = seat_body(cq.importers.importStep(str(wago_step(size))).val(), turn,
                                 seat=name, y0=y - stand_y / 2.0, z0=z - stand_z / 2.0, **face)
        out.append((name, solid, carry, size))
    return out


def build_stack(psu, pcba, wagos, wall_seat):
    """What stands on the two crowns, as `[(name, solid, colour, carry)]`.

    Relay #1 takes the BOARD'S crown — the board is the tallest body on the cap and the shortest
    in depth, so the room over it is the one room a 70 mm relay lies down in. The ground stud
    takes what that relay leaves of the same shelf, forward of it, because a ring stack is the
    one body here that will go wherever there is a corner. Relay #2 is not on either crown; it
    stands on the cap between the board and the brick (`build_relay2`)."""
    out = []
    relay1, r1_carry = seat_body(cq.importers.importStep(str(RELAY_STEP)).val(), RELAY_TURN,
                                 seat="relay-1", x1=wall_seat, y1=box(pcba).ymax,
                                 z0=box(pcba).zmax + STACK_CLEAR)
    out.append(("relay-1", relay1, C_RELAY, r1_carry))
    stud, stud_carry = seat_body(cq.importers.importStep(str(GND_STACK_STEP)).val(), RELAY_TURN,
                                 seat="ground-stack", x1=wall_seat,
                                 y1=box(relay1).ymin - STACK_CLEAR, z0=box(relay1).zmin)
    out.append(("ground-stack", stud, C_GND, stud_carry))
    return out


def wago_wells(row, cluster):
    """Every wall's well stations, `(side, y, z, size)` — one per placed lug, read off the lug's
    own box so a well cannot end up anywhere but under the thing it holds."""
    out = []
    for _name, solid, _carry in row:
        b = box(solid)
        out.append((+1, (b.ymin + b.ymax) / 2.0, (b.zmin + b.zmax) / 2.0, "413"))
    for name, solid, _carry, size in cluster:
        b = box(solid)
        out.append((CLUSTER_WAGOS[name][0],
                    (b.ymin + b.ymax) / 2.0, (b.zmin + b.zmax) / 2.0, size))
    return tuple(out)


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
# in. It takes its bosses' LENGTH with it too: the shaft runs from the body's own mounting
# plane out to the wall, so seating the body on the wall is what makes the boss short — there
# is no separate number to keep in step, and a body left standing off the wall would print
# itself the stilt it stood on.

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


def check_east_band(seated) -> Bound:
    """Every body hung on the +X wall stands inside the depth that wall runs free.

    Standing ON the wall puts a body INSIDE the ±X boss-chain band, which is the whole of what
    `east_wall_seat` buys and the whole of what it costs: the band is free air only between the
    Y-seam corner column and the rear wall's cross-pin column, and either one fills it floor to
    ceiling. `enclosure.east_band_free_y` is where they leave off.

    `pack-closes` would report a body past either end as a clash against a printed piece, once
    the piece exists. This says which body left the lane and by how much, off planes the box
    states before it is drawn — so the answer is the same whether or not the walls are on."""
    y0, y1 = _enc.east_band_free_y()
    out = []
    for name, solid in seated:
        b = box(solid)
        if b.ymin < y0 - 1e-9:
            out.append((name, "forward of", y0 - b.ymin))
        if b.ymax > y1 + 1e-9:
            out.append((name, "aft of", b.ymax - y1))
    fore = min((box(s).ymin for _n, s in seated), default=y0)
    aft = max((box(s).ymax for _n, s in seated), default=y1)
    return record_bound(Bound(
        "east-band", "The +X wall's column stands in the depth that wall runs free", not out,
        f"column spans y {fore:.2f}..{aft:.2f}, band {y0:.2f}..{y1:.2f}",
        f"inside y {y0:.2f}..{y1:.2f}",
        ([] if not out else [
            f"{n} reaches {much:.2f} mm {where} the free depth — the seam's own column stands "
            f"there floor to ceiling, so a body on the wall meets it. Move the column along "
            f"the flank, or seat that body back on `enclosure.boss_in` and let it stand off "
            f"the wall instead" for n, where, much in sorted(out, key=lambda r: -r[2])])))


# --- the tap-water sequence, in the west lane ------------------------------
#
# The backflow preventer and everything that threads or clamps onto it, made up as one chain.
# Its own frame runs the flow down +X with the VENT ON −Z, so any turn that keeps the vent
# pointing at the floor is a yaw and nothing else — and the vent has to point at the floor,
# because it weeps to atmosphere and that drip is the machine's cross-contamination telltale.
#
# The yaw lays the 140 mm chain fore and aft in the lane west of the pump, INLET AFT: the tap
# water comes in through the rear wall, so the mouth that faces the bulkhead is the upstream
# one and the flow runs forward down the lane to the split.
ASSE1022_YAW = -90.0
# The chain's aft end is THE BULKHEAD'S REACH and nothing else, because the joint between them is
# flush: the union hangs `jg_bulkhead_union.far_ring_face_y` inboard of the wall it clamps
# through, and the chain's inlet collet meets that face. So a longer union, or a thicker wall,
# moves the chain forward — and the whole west lane, which hangs off this chain, comes with it.
# THE PUMP IS NOT ITS BOX, and the lane west of it is a different width at every height. The
# bracket's splayed feet are the widest thing on the casting and they are only
# `seaflo_22_pump.FOOT_T` tall; over them the cradle steps in, and the head's flange steps back
# out. The chain and its basin stand on the deck's storey, high over the bracket, and what
# fences them there is whatever the casting presents AT THEIR OWN HEIGHT.
#
# `pan_east_x` holds the basin's rim off the casting's west flank by this, read at the tray's
# own height. It is the bound that binds — the tray's own width is what the lane has left over.
FOOT_CLEAR = 1.0


def pan_floor(asse):
    """The Z the basin's own floor stands at: the vent's own fall, less the basin's depth.

    THE TRAY HANGS OFF THE CHAIN. `build_asse` stands the chain on the panel deck and the
    basin's rim takes station one `VENT_GAP` under its underside, so the drip falls the gap the
    basin was drawn for and a change to either number moves both bodies together."""
    return box(asse).zmin - _pan.VENT_GAP - _pan.PAN_Z


def pump_west_face(seaflo, z0, z1, y0, y1):
    """The westmost the pump's casting reaches inside a room — the fence a body lying beside the
    pump in that room actually has.

    MEASURED ON THE SOLID over the room's OWN FOUR PLANES, because the box would answer with the
    feet at every height and with the discharge barb at every station: the feet are 8 mm of a
    72 mm casting, and the barb fires west out of one 10 mm band of a 187 mm one."""
    b = box(seaflo)
    slab = (cq.Workplane("XY")
            .box(b.xlen + 2.0, y1 - y0, z1 - z0, centered=False)
            .translate((b.xmin - 1.0, y0, z0)).val())
    return box(seaflo.intersect(slab)).xmin


def pan_east_x(seaflo, floor, front_y):
    """The X the basin's east rim stands at: one `FOOT_CLEAR` west of the casting, read over the
    room the tray itself occupies — its floor up to its rim, its forward rim back to its aft."""
    return pump_west_face(seaflo, floor, floor + _pan.PAN_Z,
                          front_y, front_y + _pan.PAN_Y) - FOOT_CLEAR


def build_asse(deck):
    """The ASSE 1022 chain in the west lane, seated on its INLET COLLET at the tap-water union's
    own station on the back wall.

    ALL THREE COORDINATES ARE THAT UNION'S. The two collets butt face to face with nothing
    between them to turn around, so the chain answers to the mouth it meets and to nothing else:
    the wall's WEST COLUMN in X — the column `PANEL_X` gives the nozzle-B union, which the
    tap-water one stands directly over — `bulkhead_mouth_y` in Y, and the panel deck's own storey
    in Z, the storey the row's other unions cross the wall on.

    The drip pan then takes station under the vent, and the split and the regulator off the
    chain's own outlet."""
    chain = _asse.build()
    chain = chain.toCompound() if hasattr(chain, "toCompound") else chain
    chain = chain.val() if hasattr(chain, "val") else chain
    return seat_body(chain, (((0.0, 0.0, 1.0), ASSE1022_YAW),), seat="asse1022-assembly",
                     station=(_asse.port("tube-in"),
                              (PANEL_X["bulkhead-flavor-b"], bulkhead_mouth_y(), deck)))


# --- the cradle the tap-water chain lies in --------------------------------
#
# A HALF-PIPE ON THE −X WALL, STEPPED TO THE CHAIN'S OWN SECTIONS. The chain is a made-up
# assembly of five fittings on one axis, and every one of them is a different diameter about that
# axis — so a trough cut at the widest of them holds nothing, and one cut at the narrowest takes
# only the narrowest. Cut at each section's own, the steps BETWEEN sections are faces square to
# the axis, and the barrel is trapped between two of them.
#
# EVERY SECTION IS THE SAME 120° V AND ONLY ITS APEX MOVES, which is what makes those steps fall
# out rather than be drawn: a V of this angle is the two flanks of a hex read off its corner, and
# it is also the tangent seat of any circle. So the same trough beds a hex on two whole flats and
# a barrel on two lines, and the section that is deepest in the wall is the section that is
# widest — the stair the chain lies in.
#
# ONLY THE BARREL'S V KEYS THE CLOCK, and only the barrel's may. `flare38_14ptc` says its nut "is
# a wrench hex that spins on the body" and the GAGIRA's clock is wherever its thread stopped, so
# a V cut to either one's flats would demand an angle the assembly does not control and bind on
# the build that landed 30° off. Those sections are seated on their CIRCUMSCRIBED circle, which
# takes any clock. The Multiplex's hex does not spin — its vent is machined into it — so its V is
# read off the corner, and keying that one hex is what holds the vent over the pan.
ASSE_SEAT_SLIP = 0.2
# And what the STEPS give it along the axis. The same hand makes up five joints to "snug + 1
# turn", so the run's own length is not a number this wall knows either — a step struck on the
# barrel's drawn face is a step the next build's barrel does not reach or does not clear. The
# deeper section takes this much past each of its ends, so the barrel drops in with play and the
# steps stop it travelling rather than hold it still. Aft it does not have to: the chain's inlet
# collet butts the tap-water union's, and that joint is where the run's length is taken up.
ASSE_STEP_SLIP = 0.5


def asse_sections(asse_carry) -> tuple:
    """The chain's own sections, forward to aft, as `(y0, y1, apex_x)` — the band each occupies
    down the lane and the apex the 120° V takes under it.

    A HEX READS OFF ITS CORNER AND A CIRCLE OFF ITS TANGENT. The V's apex lies one circumradius
    under a hex's axis and `R / sin 60°` under a round one's, so a section this seats on its
    flats sits `1 - sin 60°` of its own radius deeper than one it seats on two lines. That is the
    whole of why the barrel steps down out of its neighbours and not a number chosen here.

    Read through `asse_carry`, so a fitting whose length changes moves its own step."""
    axis = asse_carry(_asse.flow_axis())[0]
    def band(part_x0, part_x1, across, hexed):
        # +X in the chain's frame is the machine's −Y: the yaw lays the flow forward down the
        # lane, so a section's upstream end is its AFT end.
        ends = sorted(asse_carry(((x, 0.0, _asse.bfp.BODY_CENTER_Z), (1.0, 0.0, 0.0)))[0][1]
                      for x in (part_x0, part_x1))
        drop = across / 2.0 if hexed else across / 2.0 / math.sin(math.radians(60.0))
        return (ends[0], ends[1], axis[0] - drop - ASSE_SEAT_SLIP / math.sin(math.radians(60.0)))
    rows = (
        # the PI4512F6S's swivel nut, forward of the barrel — round, because it spins
        band(_asse.OUTLET_X, _asse.OUTLET_X + _oad.NUT_LENGTH, _oad.NUT_ACROSS_CORNERS, False),
        # the Multiplex's brass hex barrel, and the one section whose flats are read as flats
        band(_asse.BARREL_UPSTREAM, _asse.BARREL_DOWNSTREAM,
             _asse.bfp.HEX_ACROSS_CORNERS, True),
        # the GAGIRA coupling, aft. NOT the 3/8" NPT inlet stub it threads onto: the coupling's
        # `LARGE_SOCKET_DEPTH` is the whole of that stub, so the stub is never a section this
        # wall sees — what stands in the band is the coupling's own hex, round-seated because
        # its clock is wherever its thread stopped.
        band(_asse.COUPLING_X, _asse.COUPLING_X + _asse.coupling.LENGTH,
             _asse.coupling.HEX_ACROSS_CORNERS, False),
    )
    # THE DEEPER SECTION TAKES THE SLIP AT EVERY BOUNDARY. A step is a face square to the axis,
    # and which of its two sections owns the millimetre either side decides whether the run drops
    # in: give it to the shallow one and the deep section is a socket the drawn length has to
    # hit, give it to the deep one and it is a stop the run travels to.
    # THE END SECTIONS ARE THERE TO MAKE THE STEPS AND FOR NOTHING ELSE. What the trough owes the
    # chain is a face square to the axis at each end of the barrel; the fitting past that face
    # only has to be seated, not followed. So both ends run the SHORTER of the two fittings'
    # lengths — the coupling is more than twice the nut and the extra is trough over a section
    # already held, printed in PETG and paid for in the deck's own headroom.
    reach = min(r[1] - r[0] for r in (rows[0], rows[-1]))
    rows = ((rows[0][1] - reach, rows[0][1], rows[0][2]), rows[1],
            (rows[-1][0], rows[-1][0] + reach, rows[-1][2]))
    out = [list(r) for r in rows]
    for i in range(len(out) - 1):
        deep = i if out[i][2] < out[i + 1][2] else i + 1
        edge = out[i][1] + (ASSE_STEP_SLIP if deep == i else -ASSE_STEP_SLIP)
        out[i][1], out[i + 1][0] = edge, edge
    return tuple(tuple(r) for r in out)


# Where the two ties close the trough's mouth. The barrel is the only section a tie may cinch on
# — the JG acetal nut and the PP reducer would take a collet out of round — and its vent stub
# stands out of the middle of it, so `multiplex_asse1022.BARREL_LENGTH` offers exactly two bands.
# One each side of the fall, struck on the stub's OD and not on the barb's.
ASSE_TIE_VENT_CLEAR = 1.5


def asse_ties(asse_carry) -> tuple:
    """The Y of each tie band — the middle of the clear run the vent leaves on either side of it.

    BOTH ARE ON THE BRASS. The barrel is the one section a tie may close on: the JG acetal nut
    and the PP reducer go out of round under one, and the nut is the part whose clock means
    nothing anyway. Its vent stub stands out of the middle of it, so the barrel's own length
    offers exactly these two bands and no others."""
    _fwd, barrel, _aft = asse_sections(asse_carry)
    vent = asse_carry(_asse.port("vent-tip"))[0]
    edge = _asse.VENT_STUB_OD / 2.0 + ASSE_TIE_VENT_CLEAR
    return ((barrel[0] + (vent[1] - edge)) / 2.0, ((vent[1] + edge) + barrel[1]) / 2.0)


def asse_reach_down(asse_carry) -> float:
    """How far under the axis the trough's flanks run — the chain's OWN lowest arris, and not a
    millimetre past it.

    Every section's lowest point below the axis is its apothem if the trough reads its flats and
    its radius if it reads its tangent, so the deepest of the three is what the trough has to
    reach and anything under that is PETG holding air. It is the barrel's, being both the widest
    section and the one seated on flats.

    The vent stub hangs far below all of this and is not in it: the trough would have to be
    notched around the fall, and what stands under the barrel is the tray."""
    return max(axis_z_drop for axis_z_drop in _asse_section_drops(asse_carry))


def _asse_section_drops(asse_carry):
    """Each section's own reach under the axis — apothem for the one read off flats, radius for
    the ones read off their tangent."""
    yield _asse.bfp.HEX_ACROSS_CORNERS / 2.0 * math.cos(math.radians(30.0))
    yield _oad.NUT_ACROSS_CORNERS / 2.0
    yield _asse.coupling.HEX_ACROSS_CORNERS / 2.0


def asse_cradle(asse_carry) -> tuple:
    """The whole station `enclosure._asse_cradle` builds from: the axis the trough is struck on,
    its sections, the two tie bands, and how far under the axis its flanks reach."""
    axis = asse_carry(_asse.flow_axis())[0]
    return (axis[2], asse_sections(asse_carry), asse_ties(asse_carry),
            asse_reach_down(asse_carry))


def check_asse_seated(chain, piece, asse_carry) -> Bound:
    """Whether the chain is actually IN its trough, read off the two placed solids.

    A body drawn beside a groove is not a body lying in one, and every reading this card takes of
    the tap-water chain is satisfied by a chain floating in air — `placed` sees a seat it holds,
    `vent-lands` sees a drip that falls where it should, `clearance-floor` sees a millimetre it
    keeps. None of them can tell a cradle that closes on the barrel from one drawn a centimetre
    off it, because nothing about the pack changes.

    So this reads the STACK ACROSS THE V, in the one direction the trough is meant to stop:

        seat   how far west the chain stands off the wall's own furniture — one
               `ASSE_SEAT_SLIP` on the V's normal is the trough closed on the barrel's two
               flats, and anything more is a chain resting on nothing

    Measured on the solids and not on the sections table, because the table is what DREW the
    trough: a bound read back off its own inputs is a bound that cannot fail."""
    def solid(s):
        s = s.toCompound() if hasattr(s, "toCompound") else s
        return s.val() if hasattr(s, "val") else s
    # `_clearing.gap` reports a floor past its reach, so ask it for more than the trough may
    # have: a chain resting on nothing has to come back with the number, not with the reach.
    got = _clearing.gap(solid(chain), solid(piece), 5.0)
    want = ASSE_SEAT_SLIP / math.sin(math.radians(60.0))
    ok = got <= want + 1e-3
    return record_bound(Bound(
        "asse-seated", "The tap-water chain lies in its printed trough", ok,
        f"{got:.3f} mm off the wall's furniture", f"{want:.3f} mm at most",
        ([] if ok else [
            f"the chain stands {got:.3f} mm off everything `enclosure-back-top` puts near it, "
            f"and the trough is drawn to close on it at {want:.3f}. Either the cradle's sections "
            f"no longer read the chain's own — `asse_sections` — or the chain moved and the "
            f"station did not follow it."])))


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


def check_vent_lands(pan, tip) -> Bound:
    """Where the drip falls against the basin's FLAT FLOOR, inside the coves.

    The basin's outer rim to that flat is the flange, the wall and the cove together. A drip
    landing on a cove or a wall runs down the outside of the tray instead of onto the moisture
    plate, and the plate stays dry however long the vent weeps."""
    b = box(pan)
    inset = _pan.FLANGE_W + _pan.WALL + _pan.FLOOR_COVE
    y0, y1 = b.ymin + inset, b.ymax - inset
    ok = y0 <= tip[1] <= y1
    return record_bound(Bound(
        "vent-lands", "The atmospheric vent drips on the basin's flat floor", ok,
        f"drips at y {tip[1]:.2f}" + ("" if ok else f", {min(abs(tip[1] - y0), abs(tip[1] - y1)):.2f} mm outside"),
        f"y[{y0:.2f}, {y1:.2f}]",
        ([] if ok else [
            f"drip-pan: the vent drips at y {tip[1]:.2f}, off the flat floor y[{y0:.2f}, "
            f"{y1:.2f}]. The forward rim comes off the pump's discharge through "
            f"`PAN_PORT_CLEAR`; the vent's Y comes off the ASSE chain, which the bulkhead's "
            f"reach through the back wall fixes; the flat between them is `PAN_Y` less its "
            f"flange, its walls and its coves."])))


def check_pan_lane(pan, west_face) -> Bound:
    """Where the tray's west lip lands, stood off the pump by `FOOT_CLEAR`, against the −X
    wall's inner face.

    The lane has two bounds and the tray is hung on the EAST one, because that is the bound a
    millimetre matters on: everything the tray gives back in X is ceiling the west column's
    crossing ladder buys radius from, and the pump does not move for it. Where the west lip
    then falls is what is left over — and a lip landing outboard of the wall's inner face is a
    tray the wall would have to be widened around, which is `drip_pan.PAN_X`'s answer to give
    and not this module's."""
    b = box(pan)
    ok = b.xmin >= west_face - 1e-6
    return record_bound(Bound(
        "pan-lane", "The drip tray's west lip lands inside the −X wall", ok,
        f"lip at x {b.xmin:.2f}, wall at {west_face:.2f}",
        "the lip inboard of the wall",
        ([] if ok else [
            f"drip-pan: the tray's west lip lands at x {b.xmin:.2f}, {west_face - b.xmin:.2f} "
            f"mm outboard of the −X wall's inner face at {west_face:.2f}. Its east rim stands "
            f"one FOOT_CLEAR = {FOOT_CLEAR:g} off the pump's casting at the tray's own height, "
            f"so the lane holds a rim of {b.xmax - west_face:.2f}; shrink `drip_pan.PAN_X` by "
            f"what is over."])))


def build_pan(asse, seaflo, seaflo_carry, asse_carry, west_face):
    """The catch basin under the atmospheric vent, over the pump's casting.

    IN Y THE PUMP'S DISCHARGE BOUNDS IT AND THE VENT DOES NOT. The forward rim is `pan_front_y`,
    and the vent falls where the chain's own standoff from the back wall leaves it — so where the
    drip lands is a check, and `check_vent_lands` is where it is made.

    IN X THE PUMP BOUNDS IT AND THE VENT DOES NOT EITHER. The east rim is `pan_east_x`, one
    clearance off the casting's own west flank at the tray's height; the west lip takes what
    the lane has left, and `check_pan_lane` is where that is made. The tip lands 2 mm off the
    floor's own centre — 2 mm of a ±22 mm floor, so the drip still falls well inside the coves.
    The slot the tray draws out through is a wall port, struck off this body's own box in
    `west_wall_ports`.

    Z is `pan_floor` — the chain's underside, one `VENT_GAP` down to the rim and one `PAN_Z`
    down to the floor — so the drip falls exactly the gap the basin was drawn for."""
    pan = _pan.build()
    pan = pan.val() if hasattr(pan, "val") else pan
    # The bound the BASIN states about itself — its flat floor against the moisture plate it
    # receives — read off `drip_pan`'s own ledger and entered here, so it is a card row beside
    # the two this module states about where the basin stands.
    record_bound(Bound(*_pan.check_plate()))
    floor = pan_floor(asse)
    front = pan_front_y(seaflo_carry)
    placed, carry = seat_body(pan, (), seat="drip-pan",
                              x1=pan_east_x(seaflo, floor, front), y0=front, z0=floor)
    check_vent_lands(placed, asse_carry(_asse.port("vent-tip"))[0])
    check_pan_lane(placed, west_face)
    return placed, carry


# --- the cap-sense sleeves, and the controller that reads them --------------
#
# Two printed clamshells, one on each flavour line, each holding two copper foil rings
# against the tube wall; the MPR121 measures between a pair of rings and reads water
# (~80 dielectric) against air (~1). `printed-parts/flavor/cap-sense-sleeve/README.md` is
# the part and `assembly/firmware-and-commissioning.md` "MPR121 cap-sense" is the check.
#
# THE RINGS ARE THE ELECTRODES, so the wire between a ring and the controller is inside the
# measurement. That is what puts the MPR121 off the board: `wiring/ac-wiring-schedule.md`
# SIG-8 runs 300 mm of I²C out to the manifold so the electrode leads do not run back.
# `check_cap_leads` is where that arrangement is held to itself.
#
# EACH SLEEVE GOES ON ITS LINE'S FIRST RISER, the straight out of the nozzle gate's own
# outlet — the length of tube that is full when the channel is primed and empty when it is
# not. `check_sleeve_grips` holds the bore on that straight: the bore is a cylinder
# `cap_sense_sleeve.sleeve_length` long, and a corner under it is a sleeve that will not
# close.
SLEEVE_LINES = {"cap-sleeve-a": "fluid-18", "cap-sleeve-b": "fluid-28"}
# The leg of each line the sleeve rides, and the axis that leg has to run on for the roll
# below to mean anything.
SLEEVE_LEG = 0
SLEEVE_AXIS = (0.0, 0.0, 1.0)


def sleeve_seat(run):
    """Where a clamshell closes on a run, as `(the bore's mid-point, the leg's axis, the
    straight the leg leaves)`.

    A leg's own length is not its straight: each end that turns a corner spends the run's
    bend radius on the arc, and what is left between the two tangent points is what a body
    with a straight bore can sit on. The sleeve takes the middle of it."""
    p, q = run.pts[SLEEVE_LEG], run.pts[SLEEVE_LEG + 1]
    v = cq.Vector(*[q[i] - p[i] for i in range(3)])
    length = v.Length
    v = v.normalized()
    head = run.bend if SLEEVE_LEG > 0 else 0.0
    tail = run.bend if SLEEVE_LEG < len(run.pts) - 2 else 0.0
    free = length - head - tail
    mid = cq.Vector(*p) + v * (head + free / 2.0)
    return (mid.x, mid.y, mid.z), (v.x, v.y, v.z), free


def check_sleeve_grips(rows) -> Bound:
    """How much straight each sleeve is left standing on, against its own length.

    The clamshell's bore is a cylinder `cap_sense_sleeve.sleeve_length` long. A run's leg
    that is shorter than that once its corners have taken their arcs cannot be gripped at
    all; one only a little longer is gripped on tube that is still bending, and the two
    halves close on an oval.

    Nothing else on the card reads it. The bore is one `cap_sense_sleeve.bore_clearance`
    over the tube's own radius, so the two share no volume however the tube runs under them
    — `pack-closes` and `lines-clear` both come back empty, and `clearance-floor` reads the
    bore clearance and is told it is a seat."""
    worst = min((free for _n, free, _s in rows), default=0.0)
    short = [(n, free, span) for n, free, span in rows if free < span]
    return record_bound(Bound(
        "sleeve-grips", "Each cap-sense sleeve closes on a straight length of its line",
        not short,
        f"{worst:.2f} mm of straight, least of {len(rows)}",
        f"{_css.sleeve_length:g} mm per sleeve",
        ([] if not short else [
            f"{n}: the leg it rides leaves {free:.2f} mm of straight between its corners' "
            f"arcs and the sleeve is {span:g} long — the clamshell would close on "
            f"{span - free:.2f} mm of bend. The leg is `{SLEEVE_LINES[n]}` leg "
            f"{SLEEVE_LEG}; lengthen it, or move the sleeve to a leg that has the room."
            for n, free, span in short])))


def build_sleeve(name, run):
    """One cap-sense clamshell closed on its line's first riser, both halves.

    The bore's own axis is the part's +Z and the run's leg is already vertical, so the
    only turn is the ROLL: `cap_sense_sleeve`'s +X is the side the two wire-exit slots
    breach, and this points it at the machine's mirror plane, where the controller stands.
    The leads leave the sleeve facing the part that reads them."""
    mid, axis, _free = sleeve_seat(run)
    got = tuple(round(v, 9) for v in axis)
    if got != SLEEVE_AXIS:
        raise ValueError(
            f"{name} rides `{SLEEVE_LINES[name]}` leg {SLEEVE_LEG}, which runs {got} — the "
            f"line has been rerouted off the vertical this sleeve's roll is struck on, and "
            f"the bore no longer lies on the tube it is drawn round.")
    body = cq.Compound.makeCompound(
        [_css.build_pos_y_half().val(), _css.build_neg_y_half().val()])
    roll = 180.0 if mid[0] > 0.0 else 0.0
    return seat_body(body, (((0.0, 0.0, 1.0), roll),), seat=name,
                     station=(((0.0, 0.0, _css.sleeve_length / 2.0), SLEEVE_AXIS), mid))


def sleeve_exit():
    """The sleeve's two wire-exit slots, as one station in the part's own frame: the +X
    side of the +Y half, on the plane midway between the two foil grooves. This is where
    an electrode lead leaves the sleeve, and the point a lead's length is measured from."""
    return ((_css.outer_radius, 0.0, sum(_css.groove_centers_z) / 2.0), (1.0, 0.0, 0.0))


def check_cap_leads(mpr_carry, sleeve_carries, pcba) -> Bound:
    """The electrode leads against the I²C run that buys them.

    An electrode lead is part of the electrode; an I²C conductor is not. That trade is the
    whole reason this controller is off the board, and `ac-wiring-schedule.md` SIG-8 is the
    300 mm of loom it costs. A controller sitting further from a sleeve than from the PCBA
    is a controller that has spent the loom and kept the leads.

    Both figures come off placed geometry — the sleeves' own wire-exit slots, the board's
    two header rows, and the PCBA where the wall hangs it."""
    row = mpr_carry(_mpr.electrode_row())[0]
    bus = mpr_carry(_mpr.bus())[0]
    loom = math.dist(bus, box(pcba).center.toTuple())
    leads = [(math.dist(carry(sleeve_exit())[0], row), n) for n, carry in sleeve_carries]
    worst, worst_n = max(leads, default=(0.0, "—"))
    ok = worst <= loom
    return record_bound(Bound(
        "cap-leads", "The cap-sense electrode leads are shorter than the I²C loom that buys them",
        ok,
        f"longest lead {worst:.2f} mm ({worst_n}), loom {loom:.2f} mm",
        "every lead under the loom",
        ([] if ok else [
            f"mpr121: the lead to {worst_n} reaches {worst:.2f} mm and the J8 loom back to "
            f"the PCBA is {loom:.2f} — the controller stands further from the sleeve it "
            f"reads than from the board it reports to. It lies on the mirror plane between "
            f"the two risers; what moved is a riser, the board, or this seat."])))


def build_mpr121(tee_a, foam):
    """The controller lying flat on the mirror plane, between the two nozzle risers.

    IN X IT IS CENTRED, which is the whole of the rule on that axis: the two sleeves stand
    mirrored either side of the plane, so the point equidistant from both is the plane
    itself. `check_cap_leads` reads back what it leaves.

    IN Y it takes the middle of the band the junction tees leave in front of the cold core
    — the one stretch of the upper storey's mirror line with nothing standing in it. IN Z
    it lies on the plane the tees stand on, which is that band's own floor.

    The board's own frame puts the bus row on +Y and the electrodes on -Y, and no turn is
    made: the J8 loom leaves aft, at the wall the PCBA hangs on, and the electrode row
    faces forward at the two risers it reads."""
    band = (box(tee_a).ymax, box(foam).ymin)
    board, carry = seat_body(cq.importers.importStep(str(MPR121_STEP)).val(), (),
                             seat="mpr121",
                             cx=0.0, cy=sum(band) / 2.0, z0=box(tee_a).zmin)
    note_room("mpr121", "the band it lies in, either side",
              _mpr.PCB_Y / 2.0, (band[1] - band[0]) / 2.0)
    return board, carry


# --- the moisture plate, lying in the basin ---------------------------------
#
# The Shutao module is two boards: the LM393 comparator, which mounts dry off elsewhere, and the
# interdigitated probe plate, which is the half that has to be WET to read. This is that half.
#
# THE PLATE IS TURNED A QUARTER and `drip_pan.check_plate` is the reason: its 54 mm runs down the
# basin's Y, the axis the aft strip has depth to spare on, and its 40 mm across the X the west
# lane has to buy from the pump. Sizing the floor and standing the body on it read ONE turn, so a
# basin that passes its own bound is a basin this plate lies flat in.
#
# The quarter is +90, which carries the plate's own −X edge — the edge its two lead holes sit
# behind — onto the basin's FORWARD end. That is the end away from the ASSE chain the tray hangs
# under: the leads leave the basin in the open, not under the body that drips into it, and the
# solder joints are the last thing a pool standing in the basin reaches.
PLATE_YAW = 90.0


def check_drip_reads(plate, tip) -> Bound:
    """Where the drip falls against the PLATE, which is a narrower target than the floor.

    `check_vent_lands` holds the drip on the basin's flat floor and that is a different bound
    with a different failure: a drip on a cove runs down the outside of the tray. This one is
    the sensor's own. The flat floor is 43 x 67 and the plate is 40 x 54, so there is a band the
    tray catches and the probe never reads — the vent weeps, the pan does its job, and the alarm
    the weep exists to raise stays silent until the basin has pooled deep enough to reach the
    comb sideways. THAT IS THE FAILURE THIS GATE IS FOR, and it is invisible in every other one."""
    b = box(plate)
    ok = (b.xmin <= tip[0] <= b.xmax) and (b.ymin <= tip[1] <= b.ymax)
    return record_bound(Bound(
        "drip-reads", "The atmospheric vent drips on the moisture plate itself", ok,
        f"drips at x {tip[0]:.2f}, y {tip[1]:.2f}",
        f"x[{b.xmin:.2f}, {b.xmax:.2f}] y[{b.ymin:.2f}, {b.ymax:.2f}]",
        ([] if ok else [
            f"moisture-plate: the vent drips at x {tip[0]:.2f}, y {tip[1]:.2f}, off the "
            f"{_plate.PLATE_Y:g} x {_plate.PLATE_X:g} plate at x[{b.xmin:.2f}, {b.xmax:.2f}] "
            f"y[{b.ymin:.2f}, {b.ymax:.2f}]. The plate is centred on the basin's flat floor and "
            f"the basin is struck off the pump's discharge in Y and its casting in X, so what "
            f"moves the target is `PAN_PORT_CLEAR` or `FOOT_CLEAR`; what moves the drip is the "
            f"ASSE chain's own standoff from the back wall."])))


def build_moisture_plate(pan_carry, asse_carry):
    """The probe plate lying flat on the basin's floor, centred on the flat inside the coves.

    ITS ONE STATION IS ITS OWN UNDERSIDE CENTRE, seated on the flat floor's centre carried out of
    the tray's frame — so the plate rides the tray. `build_pan` hangs the basin off the ASSE
    chain and fences it off the pump's casting, and every one of those moves arrives here through
    `pan_carry` rather than being struck again off a box.

    Centred is the whole of the rule. The plate has no station of its own to answer to — nothing
    threads it, nothing bolts it — so the only thing to say about where it lies is that it lies
    in the middle of what receives it, which is also what leaves the drip the most margin on
    every side. `check_drip_reads` is where that margin is read back."""
    plate = _plate.build()
    plate = plate.val() if hasattr(plate, "val") else plate
    floor_centre = pan_carry((
        (_pan.PAN_X / 2.0, _pan.PAN_Y / 2.0, _pan.FLOOR), (0.0, 0.0, 1.0)))[0]
    placed, carry = seat_body(plate, (((0.0, 0.0, 1.0), PLATE_YAW),), seat="moisture-plate",
                              station=(((0.0, 0.0, 0.0), (0.0, 0.0, 1.0)), floor_centre))
    check_drip_reads(placed, asse_carry(_asse.port("vent-tip"))[0])
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
# THE HOPPER'S BOWL IS THE FORWARD LANE'S CEILING. The chain crosses the wall on the panel deck
# and the lane it hands the water to runs forward under that bowl, so the tap steps down out of
# the deck between the chain and the split, in the open room aft of the hopper. Everything
# forward of the split — the regulator, its tap and the tube down to the flavour gates — lies on
# the storey this step lands on.
#
# `check_bowl_clear` measures what the step leaves once the funnel is in the box, which is the
# first moment the bowl exists to measure against: the box is sized around this pack and the
# funnel is then set in its top.
FLAVOR_STEP = 32.0
# What the tap's own headroom under that bowl has to be.
BOWL_CLEAR = 1.0
# The reach between the chain's outlet collet and the split's supply collet — `water-2`. The two
# mouths face each other down one column with the step between them, so what this has to be is
# the run that step's two corners and the lean between them take.
WATER_2 = 44.0
# THE SPLIT STANDS ON ITS OWN COLUMN AND `water-2` IS WHAT CROSSES TO IT. The chain answers to
# the rear wall — all three of its coordinates are the tap-water union's, and `PORT_WEST_COLUMN`
# is what stands that union's pair in the lane. The storey below is a different room: the gate
# line takes the outboard strip at `_lines.GATE_LANE_X` on its way aft, `water-3` falls out of
# this split's own downward branch on whatever column the split stands on, and the two pass tube
# over tube. So the sequence forward of the step keeps its column when the wall's moves, and the
# lean already in `water-2` for the step carries the offset across as well as down.
SPLIT_COLUMN = -77.0


def build_split(asse_carry):
    """The split seated on its SUPPLY COLLET, one `WATER_2` forward of the chain's outlet, one
    `FLAVOR_STEP` under it and on `SPLIT_COLUMN` across.

    A fitting answers to its mouth and not to a face of its box: what has to land in the right
    place is the collet the tube pushes into. Its reach and its storey are read off the chain's
    own outlet, so the split rides the chain fore and aft wherever the chain goes; its column is
    its own, because what fences the lane it stands in is not what fences the wall above."""
    out_pos, out_axis = asse_carry(_asse.port("tube-out"))
    target = tuple(out_pos[i] + out_axis[i] * WATER_2 - (FLAVOR_STEP if i == 2 else 0.0)
                   for i in range(3))
    target = (SPLIT_COLUMN, target[1], target[2])
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
# has no corner in it because both mouths face each other down one line on one storey: the split
# already took the step down out of the deck.
FLUID_1 = 24.0


def check_bowl_clear(flowreg, funnel) -> Bound:
    """What the flavour tap keeps under the hopper's bowl — the exact solid gap between the
    regulator's crown and the basin hanging over it.

    Measured rather than derived, because the two are on opposite sides of the box: the box is
    sized around the pack the regulator is in, and the funnel is then seated in its top. So
    `FLAVOR_STEP` is the reach the lane is given and this is what it turns out to be worth."""
    got = _clearing.gap(flowreg, funnel, FLAVOR_STEP)
    ok = got >= BOWL_CLEAR - 1e-6
    return record_bound(Bound(
        "bowl-clear", "The flavour tap runs under the hopper's bowl", ok,
        f"{got:.3f} mm to the basin", f"{BOWL_CLEAR:g} mm",
        ([] if ok else [
            f"flow-regulator: the tap's crown leaves {got:.3f} mm under the hopper's basin, "
            f"under the {BOWL_CLEAR:g} mm the lane is drawn for. `FLAVOR_STEP` is the step "
            f"`water-2` takes off the panel deck onto this lane; deepen it by what is short."])))


def build_flowreg(split_carry):
    """The regulator seated on its INLET, one `FLUID_1` forward of the split's flavour collet
    and on that collet's own line — so the tap runs split, regulator down one axis under the
    hopper's bowl, and the joint between them is a straight."""
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
#
# V-K STANDS IN THE ROW THE SOURCE PAIR MAKES. Three Beduans sit on this cap — V-A, V-B and this
# one — and the two the pack carries land on one plane facing one way. V-K's depth is theirs,
# and `water-4` is what is left between its outlet and the chain's collet: both mouths lie on
# that plane and on one column, so it is a length of tube and not a route. The cap prints its
# three cradles on that same row (`_cold_core_interface.cap_cradles`), and `cap-valve-row`
# measures it.
# THE VALVE'S SEAT is the cradle's. The cap prints four bosses (`valve_seat`) at this
# valve's own station (`_cold_core_interface.cap_cradles`), and what a seat says is where the
# Beduan's Z = 0 — the underside of its white body — stands once its four posts are pressed
# home. So the seat is read off the part that carries it rather than stated here, and a cradle
# that moves takes the valve, the chain behind it and `water-4` with it.


def vk_port_z(foam):
    """The Z V-K's two collets open on — its own `port_center_z` over the seat its cradle
    stands it at, over the cold core's cap face.

    The suction chain lies on this same plane, so `water-4` is a straight between two mouths
    facing each other, and a change to the cradle moves the pair together."""
    return cap_face(foam) + _cci.cap_cradles["vk-solenoid"].seat + _beduan.port_center_z


def source_row_y(stood) -> float:
    """The aft face of the row the two source valves make, in world.

    Both stand the same Beduan the same way up on the same plane. The face is a body's end,
    `_beduan.port_length` from its other one; on a source valve it is the inlet's — the collet
    `fluid-2` and `fluid-4` come at — and on V-K it is the outlet's."""
    faces = [box(s).ymax for n, s, _c in stood if n in ("valve-v-a", "valve-v-b")]
    assert len(faces) == 2 and abs(faces[0] - faces[1]) < 1e-6, (
        f"the two source valves are not on one plane ({faces}), so there is no row for V-K to "
        f"stand in — `manifold_layout.SHIFT` carries them and it carries them together.")
    return faces[0]


def build_vk(chain_carry, row_y: float):
    """V-K seated on its OUTLET, on the suction chain's own column and plane — which is
    `vk_port_z`, the plane the chain was laid on, so the valve comes back down onto its own
    seat — and on `row_y`, the face the source pair stands its own ends on.

    The outlet is this valve's aft collet, so the whole body stands in the pair's own depth and
    `water-4` is what is left back to the chain."""
    pos, _axis = chain_carry(_suct.tube_port())
    target = (pos[0], row_y, pos[2])
    body = _beduan.build_beduan_solenoid()
    body = body.val() if hasattr(body, "val") else body
    return seat_body(body, (), seat="vk-solenoid", station=(_beduan.outlet(), target))


# --- what carries the tray, and the slot it draws out through --------------
#
# The rail's own section, the stop's, and the section of the lap that closes each rail into a
# channel.
DRIP_RAIL_H = 3.0
DRIP_STOP_T = 3.0
DRIP_LIP_T = 2.0


def pan_rails(pan, west_face):
    """The tray's carry, as world boxes fused onto the −X wall's inner face
    (`enclosure._pan_rails`): a CHANNEL under each of the rim's outer bands, and the stop the
    tray comes to rest against.

    THE RAILS TAKE THE RIM, and nothing reaches under the floor. Each rail's top face IS the
    flange's underside, and each RUNS FROM THE WALL — its root, and the only thing it is fused
    to — out to the tray's own east edge, so a seated tray stands on rail end to end and a
    withdrawing one keeps rail under it until the rim is clear of the wall. Rooting them on the
    wall rather than on the tray's west lip is what makes them printable at all: the lip stands
    off the wall by whatever the lane left it, and a rail begun there would be a bar hanging in
    air. The band each takes is `drip_pan.bearing_w()`, the flat of that underside inboard of
    the haunch, and the two inboard arrises take the tray's two 45° haunches and hold it on its
    column.

    EACH RAIL CLOSES OVER THE RIM. An upright stands in the daylight outboard of the flange —
    the strip the tray's own edge leaves against the lane — and carries a lap back inboard over
    the same band the rail bears on, one `drip_pan.PAN_SLIP` clear of the flange's top. So the
    rim runs in a channel: the rail under it, the upright beside it and the lap over it. The
    tray goes in and comes out the one way the channel is open, which is west through the wall's
    own slot, and what it cannot do is lift out of its carry.

    THE STOP RUNS UNDER THE RIM, in the pocket the flange overhangs its basin by, and it
    catches the HAUNCH — the outermost face the tray presents below its rim, one
    `drip_pan.PAN_SLIP` off the bar's own. It runs the rim's whole length, reaching both rails,
    which are what it is fused to the wall through. The rim rides over it the way it rides the
    rails, and its plan arcs carry the tray away from it at both ends — `CORNER_R` plus the
    flange rounds the rim, plus the haunch rounds the section beneath, so the corners are clear
    and the straight between them is what butts."""
    top = pan.zmax - _pan.FLANGE_T              # the flange's underside — the bearing plane
    band = _pan.bearing_w()
    toe = pan.xmax - _pan.FLANGE_W + _pan.FLANGE_HAUNCH     # the haunch's outermost face
    stop_x = toe + _pan.PAN_SLIP
    lap0 = pan.zmax + _pan.PAN_SLIP             # the lap's underside, one slip over the rim
    lap1 = lap0 + DRIP_LIP_T
    members = [(stop_x, stop_x + DRIP_STOP_T, pan.ymin, pan.ymax, top - DRIP_RAIL_H, top)]
    for edge, out in ((pan.ymin, -1.0), (pan.ymax, 1.0)):
        rail = sorted((edge, edge - out * band))            # inboard, under the flange
        upright = sorted((edge, edge + out * DRIP_LIP_T))   # outboard, beside it
        members += [(west_face, pan.xmax, *rail, top - DRIP_RAIL_H, top),
                    (west_face, pan.xmax, *upright, top - DRIP_RAIL_H, lap1),
                    (west_face, pan.xmax, min(rail[0], upright[0]),
                     max(rail[1], upright[1]), lap0, lap1)]
    return members


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
    a = cq.Assembly(name="enclosure-assembly")
    SEATS.clear()
    BOUNDS.clear()
    # The import-time group first, so a pack that never reaches the box still carries them.
    carry_stated_bounds()
    seated_comp = build_compressor()
    ((comp, comp_carry),
     (cond, cond_carry)) = place_base([seated_comp, build_condenser(seated_comp[0])],
                                      names=("compressor", "condenser+fan"))
    a.add(comp, name="compressor", color=C_COMP)
    a.add(cond, name="condenser+fan", color=C_COND)
    # The gas sensor goes down with the bodies it watches, off the compressor's own plate: it
    # is placed here rather than with the box because the wall's slot is struck on where it
    # lands, the way every well on the other flank is struck on its lug.
    mq6, mq6_carry = build_mq6(comp, cond)
    a.add(mq6, name="mq6-sensor", color=C_MQ6)
    a.west_cradle = mq6_cradle(mq6_carry)
    # The cutoff goes down with the compressor too, and for the same reason the sensor does:
    # its whole job is a temperature, and the temperature it reads is the one at the face it
    # is lying on.
    fuse, fuse_carry = build_thermal_fuse(comp_carry)
    a.add(fuse, name="thermal-fuse", color=C_FUSE)
    # And the clamp on top of it, which is the whole of why the cutoff reads that face rather
    # than the air around it. It goes down after the body it closes on, because the gate it
    # earns is taken between the two.
    clamp, clamp_carry = build_fuse_clamp(comp_carry, fuse)
    a.add(clamp, name="fuse-clamp", color=C_CLAMP)
    # The service port goes down with the compressor as well: the stub it bands is the
    # can's own, and `check_bpv_reach` reads the column over it once the pack is standing.
    bpv, bpv_carry = build_bpv31(comp_carry)
    a.add(bpv, name="bpv31", color=C_BPV)

    posed = [(c.name, pose_manifold((c.obj.val() if hasattr(c.obj, "val") else c.obj).moved(
        cq.Location(c.loc.wrapped.Transformation()))), c.color) for c in ml.build_assembly().children]
    crown = max(box(comp).zmax, box(cond).zmax)
    lift = crown - min(box(s).zmin for _n, s, _c in posed)
    # The pack's own stations in world, from the moment it is stood: a run anchors on these, and
    # so does anything the machine stands ON one of them.
    mcarry = manifold_carry(lift)
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
    # What the core butts is whatever stands ahead of it AT THE CORE'S OWN HEIGHT. The
    # source valves' quarter turns carry them aft over the core's crown, and a body standing
    # over it is not a body in its way — so the seam is measured against the bodies that reach
    # below that crown, and the ones above it are left to overhang.
    top = cap_face(build_foam(0.0)[0])
    aft = max([box(comp).ymax, box(cond).ymax]
              + [box(s).ymax for _n, s, _c in stood if box(s).zmin < top])
    foam, foam_carry = build_foam(aft)
    a.add(foam, name="foam-assembly", color=C_FOAM)
    seaflo, seaflo_carry = build_seaflo(foam)
    a.add(seaflo, name="seaflo-pump", color=C_SEAFLO)
    chain, chain_carry = build_suction_chain(seaflo, seaflo_carry(_lines._pump.suction()),
                                             vk_port_z(foam))
    a.add(chain, name="suction-chain", color=C_SUCT)
    wall_seat = east_wall_seat()
    psu, psu_carry = build_psu(foam, wall_seat)
    a.add(psu, name="psu", color=C_PSU)
    # The band, fore to aft: board, relay #2 on end, brick. The relay is placed off the brick and
    # the board off the relay, so the three close up on one chain and none of them carries a
    # typed Y of its own.
    relay2, relay2_carry = build_relay2(psu, foam, wall_seat)
    a.add(relay2, name="relay-2", color=C_RELAY)
    pcba, pcba_carry = build_pcba(foam, relay2, wall_seat)
    a.add(pcba, name="pcba", color=C_PCBA)
    wagos = build_wago_row(psu, wall_seat)
    for name, solid, _carry in wagos:
        a.add(solid, name=name, color=C_AC_HUB)
    stack = build_stack(psu, pcba, wagos, wall_seat)
    for name, solid, colour, _carry in stack:
        a.add(solid, name=name, color=colour)
    stack_carry = {name: carry for name, _s, _c, carry in stack}
    cluster = build_cluster_wagos()
    for name, solid, _carry, _size in cluster:
        a.add(solid, name=name, color=C_AC_HUB)
    a.side_wells = wago_wells(wagos, cluster)
    check_east_band([("psu", psu), ("pcba", pcba), ("relay-2", relay2)]
                    + [(n, s) for n, s, _c in wagos]
                    + [(n, s) for n, s, _c, _k in stack])
    # The compressor is the one body on the floor that is bolted DOWN to it, so its four
    # holes are the slab's own boss stations.
    a.floor_bosses = floor_mounts(
        (comp_carry, _comp.mount_pattern(), _comp.BASE_Z))
    # The Wago row is absent here on purpose: a lever nut has no hole to stand a boss on. Its
    # well IS its mount, and that goes on the wall through `side_wells`.
    a.east_bosses = wall_mounts(
        (psu_carry, _psu.holes), (pcba_carry, _pcba.board.holes),
        (relay2_carry, _relay.holes),
        (stack_carry["relay-1"], _relay.holes),
        (stack_carry["ground-stack"], _gnd.holes))
    vk, vk_carry = build_vk(chain_carry, source_row_y(stood))
    a.add(vk, name="vk-solenoid", color=C_VK)
    # The cradles, measured the moment the last valve standing on the cap is placed. The other
    # two came up with the pack, so this is the first point at which all three are in world.
    on_cap = {**{n: s for n, s, _c in stood}, "vk-solenoid": vk}
    a.cradles = cradle_rows(foam, foam_carry, on_cap)
    check_cradles(a.cradles)
    check_valve_row(on_cap)
    # The pump's own joint, read the same way: the four cap columns against the four bores in
    # the bracket's pad, both taken back into the frame the cap is authored in.
    a.pump_mount = pump_mount_rows(foam_carry, seaflo_carry)
    check_pump_mount(a.pump_mount)
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
    # the assembly as it is at this point. THE WEST LANE HANGS OFF IT and is not in the strike:
    # the tap-water union takes the deck's own storey, the chain butts that union, and the
    # split, the regulator and the drip tray all take station off the chain.
    a.gate_z = nozzle_storey(
        _lines.gate_cruise(mcarry(_lines.station("valve-v-i", "outlet"))[0][2]), seaflo)
    under_deck = [s for s, _c in _solids(a).values()]
    a.deck_z, deck_fall = deck_z(under_deck, a.gate_z)
    asse, asse_carry = build_asse(a.deck_z)
    a.add(asse, name="asse1022-assembly", color=C_ASSE)
    pan, pan_carry = build_pan(asse, seaflo, seaflo_carry, asse_carry,
                               west_interior_face())
    a.add(pan, name="drip-pan", color=C_PAN)
    mplate, _mplate_carry = build_moisture_plate(pan_carry, asse_carry)
    a.add(mplate, name="moisture-plate", color=C_PLATE)
    split, split_carry = build_split(asse_carry)
    a.add(split, name="water-split", color=C_SPLIT)
    flowreg, flowreg_carry = build_flowreg(split_carry)
    a.add(flowreg, name="flow-regulator", color=C_FLOWREG)
    disch, disch_carry = build_discharge_chain(split, flowreg, seaflo_carry)
    a.add(disch, name="discharge-chain", color=C_SUCT)
    bulkhead, bulkhead_carry = build_bulkhead(asse_carry)
    a.add(bulkhead, name="bulkhead-water", color=C_BULKHEAD)
    deck_solids, panel_carries = build_deck(a.deck_z, a.gate_z, seat=True)
    meter_carry = panel_carries.pop("digiten-flow")
    for name, solid in deck_solids.items():
        a.add(solid, name=name, color=C_DIGITEN if name == "digiten-flow" else C_BULKHEAD)
        note_room(name, "fall onto what stands under it", DECK_CLEAR,
                  deck_fall[name] if name in deck_fall
                  else descent(solid, _would_land_on(box(solid), under_deck)))
    panels = {n: s for n, s in deck_solids.items() if n != "digiten-flow"}
    check_port_pair(panels, west_interior_face(), seaflo)
    meter = deck_solids["digiten-flow"]
    a.panel_carries = panel_carries

    # The runs between placed bodies. Their frames come off the poses above, so a waypoint
    # measured off a port moves when the body it is on moves.
    carries = {"foam-assembly": foam_carry, "seaflo-pump": seaflo_carry, "suction-chain": chain_carry,
               "discharge-chain": disch_carry,
               "compressor": comp_carry, "condenser+fan": cond_carry,
               "asse1022-assembly": asse_carry, "water-split": split_carry,
               "flow-regulator": flowreg_carry, "vk-solenoid": vk_carry,
               "bulkhead-water": bulkhead_carry, "gasher-co2": gasher_carry,
               "wr1110": wr1110_carry, "digiten-flow": meter_carry, **panel_carries}
    solids = {"foam-assembly": foam, "seaflo-pump": seaflo, "suction-chain": chain,
              "discharge-chain": disch,
              "compressor": comp, "condenser+fan": cond,
              "asse1022-assembly": asse, "water-split": split,
              "flow-regulator": flowreg, "vk-solenoid": vk,
              "bulkhead-water": bulkhead, "gasher-co2": gasher, "wr1110": wr1110,
              "digiten-flow": meter, **panels}
    # The pack's own bodies, so a run may anchor on one or measure off one. The stations answer
    # in `manifold_layout`'s world and ride the pose this module stood them in.
    for name, solid, _colour in stood:
        solids[name] = solid
        if name in _lines.STATIONS:
            carries[name] = mcarry
    a.bulkhead_carry = bulkhead_carry
    a.asse_cradle = asse_cradle(asse_carry)
    a.runs = []
    # The bodies and their placements, carried on the assembly: a run whose other mouth is on
    # something the BOX seats is drawn after the box exists, and it anchors on these same frames.
    a.pack_solids, a.carries = solids, carries
    draw_runs(a, _lines.build_runs(solids, carries))
    # THE CAP-SENSE PAIR, ONCE THE LINES THEY GRIP EXIST. A sleeve closes on a length of
    # tube, so it can only be placed after the run that tube is; the controller then goes
    # between the two of them and the leads are read against the loom.
    by_id = {r.id: r for r in a.runs}
    sleeve_carries, grips = [], []
    for name, line in SLEEVE_LINES.items():
        sleeve, sleeve_carry = build_sleeve(name, by_id[line])
        a.add(sleeve, name=name, color=C_SLEEVE)
        sleeve_carries.append((name, sleeve_carry))
        grips.append((name, sleeve_seat(by_id[line])[2], _css.sleeve_length))
    check_sleeve_grips(grips)
    mpr, mpr_carry = build_mpr121(solids["tee-y-a"], foam)
    a.add(mpr, name="mpr121", color=C_MPR)
    check_cap_leads(mpr_carry, sleeve_carries, pcba)
    # THE SEALED LOOP, READ ONCE THE MACHINE HAS DRAWN WHAT IT DRAWS. Two of its legs cross a
    # plane their bodies already share and no copper is drawn between them; the third is cut and
    # brazed like any other run. Which is which is not this module's to declare — `_lines` having
    # authored a run settles it — so the reading waits for the runs and then grades every leg by
    # what the machine actually made it with. Nothing else on this pack stands between a station
    # that moved and a leg nobody notices has come apart.
    a.refrigerant_at = refrigerant_stations(carries)
    # The whole loop's reading rides the assembly, and the MATED subset of it rides beside: the
    # gate accounts for every leg, and the card is handed only the ones a shared plane actually
    # shut — it counts the drawn one off the run itself, like every other line.
    a.refrigerant = refrigerant_joints(carries, a.runs)
    a.refrigerant_mates = refrigerant_mates(a.refrigerant)
    check_refrigerant_joints(a.refrigerant)
    # The service column over the piercing valve, read against everything the pack put in
    # the bay — the bodies and the tube swept between them. The three bodies the BOX adds
    # afterwards stand in the top wall, the display facet and the walls themselves.
    check_bpv_reach(bpv_carry, {n: s for n, (s, _c) in _solids(a).items()})
    a.seats = dict(SEATS)
    a.bounds = list(BOUNDS)
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
# (`build_enclosure_assembly`) rather than to the pack.
THROUGH_WALL = ("bulkhead-water", "c14-inlet", "co2-inlet",
                "bulkhead-flavor-a", "bulkhead-flavor-b", "bulkhead-carb")


def pack(a: cq.Assembly = None) -> "_enc.Pack":
    """What the box is SIZED ON: the bodies that have to fit inside it.

    `THROUGH_WALL` is what that excludes, and the funnel is the same case by a different route.

    `front_ports` is empty and stays empty. The box is four printed pieces and every face is a
    wall of one of them — there is no front panel to cut through — so that field is settled,
    not unfinished."""
    a = build_pack() if a is None else a
    placed = _solids(a)
    pan = box(placed["drip-pan"][0])
    west = west_interior_face()
    return _enc.Pack(placed={n: v for n, v in placed.items() if n not in THROUGH_WALL},
                     west_ports=west_wall_ports(pan), pan_rails=pan_rails(pan, west),
                     back_ports=(back_wall_ports(a.bulkhead_carry, *a.panel_carries.values())
                                 + [c14_cutout(), co2_wall_port(a.co2_inlet_carry)]),
                     c14=c14_stations(), east_bosses=a.east_bosses,
                     side_wells=a.side_wells, floor_bosses=a.floor_bosses,
                     west_cradle=a.west_cradle, asse_cradle=a.asse_cradle)


def check_through_wall_headroom(a, shell) -> Bound:
    """How far each body seated through a wall stands under the box's own ceiling.

    `pack` leaves these out of what the box is sized on, which is right in plan — a body that
    reaches out through its own skin cannot also set that skin. IN Z IT LEAVES THEM UNMEASURED,
    and what is inboard of the wall is under the top wall like anything else. The panel deck is
    where that bites: the union's Ø22.86 barrel is the fattest thing the deck carries, so it is
    what touches the ceiling first, and `enclosure._dims` never sees it.

    The ceiling is a STATED bound: `enclosure.appliance_height` is the machine's own height and
    the top wall is cut out of it, so a body over that line is inside the wall."""
    placed = _solids(a)
    ceiling = shell.inner[5]
    reach = {n: box(placed[n][0]).zmax for n in THROUGH_WALL}
    over = [(n, z) for n, z in reach.items() if z > ceiling + 1e-9]
    tallest = max(reach.values(), default=ceiling)
    return record_bound(Bound(
        "wall-headroom", "Every body seated through a wall stands under the ceiling", not over,
        f"tallest reaches z {tallest:.2f}, ceiling {ceiling:.2f}",
        "every body under the ceiling",
        ([] if not over else [
            f"{max(over, key=lambda nz: nz[1])[0]} reaches z "
            f"{max(over, key=lambda nz: nz[1])[1]:.2f} but the interior ceilings at "
            f"{ceiling:.2f} — {max(over, key=lambda nz: nz[1])[1] - ceiling:.2f} mm into the "
            f"top wall. Every body seated through a wall is left out of what "
            f"`enclosure._dims` sizes the box on, so raise `enclosure.appliance_height` or "
            f"drop the storey it stands on: "
            + ", ".join(f"{n} {z:.2f}" for n, z in sorted(over))])))


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
    so the wall and the body it is cut for come out of one number. `enclosure.with_funnel`
    takes the throat's own reading against the frame the top wall has left as it seats it."""
    return _enc.with_funnel(box, funnel_centre(box))


def machine():
    """The pack, and the box around it. One build: the box is sized on the pack's bodies,
    and then carries the stations they seat in its walls.

    The box is SEATED before its ledger is carried, so the card holds the throat's three rows
    whether or not a wall is ever cut from this box."""
    a = build_pack()
    p = pack(a)
    box = _seated(_enc.stated_box(p))
    carry_enclosure_bounds()
    check_through_wall_headroom(a, box)
    a.bounds = list(BOUNDS)
    return a, p, box


def build_enclosure_assembly() -> cq.Assembly:
    """The pack, what is seated in the walls, and the four printable pieces of the box."""
    a, _p, box = machine()
    funnel, funnel_carry = build_funnel(box)
    a.add(funnel, name="hopper-funnel", color=C_FUNNEL)
    # The basin is not in the pack — the box is sized on the pack and the funnel is seated in
    # the box — so the line it drains through is drawn HERE, off the same frames the pack's own
    # runs anchor on, with the funnel's now among them.
    a.pack_solids["hopper-funnel"], a.carries["hopper-funnel"] = funnel, funnel_carry
    check_bowl_clear(a.pack_solids["flow-regulator"], funnel)
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
    pieces = _enc.build_pieces(box)[0]
    for name, piece in pieces.items():
        a.add(piece, name=f"enclosure-{name}", color=WALL_COLORS[name])
    # The chain against the piece that cradles it, once that piece exists — the one reading on
    # this card that can tell a trough closed on the barrel from a trough drawn near it.
    check_asse_seated(a.pack_solids["asse1022-assembly"], pieces["back-top"],
                      a.carries["asse1022-assembly"])
    # The box's own group reads LAST on the card, under the pack's. `record_bound` carries an
    # id to the end of the ledger each time it is entered, so reading `enclosure`'s ledger again
    # here — after the bodies the box seats have stated theirs — is what puts it there.
    carry_enclosure_bounds()
    a.bounds = list(BOUNDS)
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
    sh, co = box(named["compressor"]), box(named["condenser+fan"])
    fo, sf = box(named["foam-assembly"]), box(named["seaflo-pump"])
    line("compressor", sh)
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
    for n in ("pcba", "relay-1", "relay-2") + WAGO_POLES + (
              "ground-stack", "asse1022-assembly", "drip-pan", "bpv31",
              "mpr121", "cap-sleeve-a", "cap-sleeve-b",
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
    print(f"  compressor tangent {seam} {lo:.2f}   condenser intake face {seam} {hi:.2f}   "
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
    for j in getattr(a, "refrigerant", []):
        if j.mm is None:
            print(f"  {j.id:16} {'—':16}    {'—':16} "
                  f"{'':26}  unmeasured — no pair of placed stations")
            continue
        p = a.refrigerant_at[j.frm][0]
        print(f"  {j.id:16} {j.frm.split('.')[1]:16} {j.made:5} {j.to.split('.')[1]:16} "
              f"({p[0]:7.2f},{p[1]:7.2f},{p[2]:6.2f})  off {j.mm:.3f}")
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
        on = "compressor" if sh.xmin <= (b.xmin + b.xmax) / 2 <= sh.xmax else "condenser"
        under = sh.zmax if on == "compressor" else co.zmax
        print(f"  {n:16} x {(b.xmin + b.xmax) / 2:7.2f} sets down on the {on:9} "
              f"crown z {under:.2f}  gap {b.zmin - under:.2f}")
    print(f"\nmachine           {whole.xlen:.2f} × {whole.ylen:.2f} × {whole.zlen:.2f}   "
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


def selftest():
    """What `seat_body` promises about the body it hands back."""
    import _meshes

    part = cq.Workplane("XY").box(18.0, 11.0, 7.0).faces(">Z").workplane().hole(4.0).val()
    turns = (((0, 0, 1), 90.0), ((1, 0, 0), -37.0))
    drawn = _meshes._named(part.wrapped, _meshes.DEFLECTION)

    # A SEAT IS A LOCATION OVER THE DRAWN BODY. `_meshes` names a body's kept triangles after
    # the shape under its location, so a seat that reached the coordinates would name a new
    # mesh — and every rule that moves a body would redraw it.
    for label, where in (("plane rule", dict(cx=0.0, y0=40.0, z0=12.0)),
                         ("the same rule, one constant moved", dict(cx=0.0, y0=95.5, z0=12.0))):
        placed, _carry = seat_body(part, turns=turns, **where)
        got = _meshes._named(_meshes._unplaced(placed)[0], _meshes.DEFLECTION)
        if got != drawn:
            raise AssertionError(
                f"a body seated by {label} names a mesh the drawn body does not — the pose is in "
                f"its coordinates, so every seat redraws it and no scene has a transform to carry")
    yield "a seated body's kept triangles are the drawn body's, wherever the rule puts it"

    # And the seat still lands where it says: the ledger reads the rule back off the geometry.
    placed, _carry = seat_body(part, turns=turns, cx=0.0, y0=40.0, z0=12.0, seat="selftest-body")
    off = seat_off(SEATS.pop("selftest-body"))
    if off > SEAT_TOL:
        raise AssertionError(f"a hung seat lands {off:.2e} off its own rule, past {SEAT_TOL:g}")
    yield f"a hung seat lands {off:.1e} off the rule it was given"


def main():
    import _scorecard as _card
    if sys.argv[1:] == ["selftest"]:
        for line in selftest():
            print(" ", line)
        print("enclosure_assembly selftest OK")
        return
    a = build_enclosure_assembly()
    out = _here.parent / "enclosure-assembly.step"
    export_assembly(a, str(out))
    print(f"-> {out.name}")
    report(a)
    _card.report(a)
    print(f"-> {_card.write(a, out, __file__).name}")
    ml.render_elevations(out, xray="enclosure*")


if __name__ == "__main__":
    main()
