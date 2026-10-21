"""Two-channel flavor manifold with permanent asymmetric TPU pump junctions.

The four wall junctions feed straight upper links and four scanned PP0308E
elbows. Each lower socket feeds one bent LLDPE tube into an upright elbow beneath
its rear valve; a short straight tube joins the two purchased push-fit fittings. Pump replacement withdraws only the prepared pump stubs.

Authoring frame: X spans the two channels; +Y becomes enclosure +Z; +Z becomes
enclosure +Y. The pump station retains its fitted physical datum. The fore
valves retain their deck stations; the rear row stands 8 mm higher for elbow clearance. The two source turns
retain their own construction independently of the pump-port connections.
"""

import math
import os
import sys
from pathlib import Path
from typing import NamedTuple

import cadquery as cq
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
_tools = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"
for _p in (_hw / "scripts",
           _hw / "reference" / "beduan-solenoid",
           _hw / "reference" / "tee-connector",
           _hw / "reference" / "y-divider",
           _hw / "reference" / "kamoer-kphm400",
           _hw / "printed-parts" / "cadlib",
           _hw / "printed-parts" / "enclosure" / "enclosure",
           _hw / "printed-parts" / "enclosure" / "pump-dock",
           _hw / "printed-parts" / "enclosure" / "pump-tray"):
    sys.path.insert(0, str(_p))
sys.path.insert(0, str(_tools))
from _cadq_export import export_assembly, import_step              # noqa: E402
from docgen import substitute_md                      # noqa: E402
import beduan_solenoid as vlv                         # noqa: E402
import kamoer_kphm400 as kp                           # noqa: E402
import tee_connector as tee                           # noqa: E402
import y_divider as ydiv                              # noqa: E402
# The routing kit owns the stock table — the tube on the machine and the floor each one's
# corners answer to — so this study reads its own bend radius off the same row every run
# drawn in that stock is graded against.
import _routing                                       # noqa: E402
# The bound this file states about its own figures — settled here, at import, before any solid
# exists to hang a reading on. `_stated_bounds` is the ledger it records into and
# `enclosure_assembly.carry_stated_bounds` is what puts it on the card.
import _stated_bounds as _bounds                      # noqa: E402
import _boxes                                         # noqa: E402
import _overlap                                       # noqa: E402
import _enclosure_interface as _enc_if                # noqa: E402
import fixed_returns as _returns                      # noqa: E402
import pump_receiver as _receiver                     # noqa: E402

ELBOW_STEP = _hw / "reference" / "elbow-connector" / "elbow-connector.step"
TEE_STEP = _hw / "reference" / "tee-connector" / "tee-connector.step"
KAMOER_STEP = _hw / "reference" / "kamoer-kphm400" / "kamoer-kphm400.step"
# The reference pump's two shaped solids, read off its STEP once and held.
_KAMOER = None
# What brings them out of `kamoer_kphm400`'s case frame into this study's: the quarter
# lays the pump's depth axis down onto +Y, and the half rolls its barb face up onto +Z.
PUMP_TURNS = (((1.0, 0.0, 0.0), -90.0), ((0.0, 1.0, 0.0), 180.0))

# --- The parts' own figures ------------------------------------------------
VALVE_LEN = vlv.port_length                  # collet face to collet face
VALVE_PITCH = vlv.body_width_x               # the X keep-out two valves pack to
VALVE_PORT_Z = vlv.port_center_z             # port axis over the valve's own mounting plane
VALVE_TOP_Z = vlv.coil_z_range[1]            # coil crown over that same plane
TEE_RUN = tee.RUN_HALF                       # run collet face from the tee's centre
TEE_BRANCH = tee.BRANCH_REACH                # branch collet face from the same centre
TUBE_D = tee.TUBE_D                          # the 1/4" OD LLDPE every port takes
STOCK = _routing.stock_of("fluid", TUBE_D)   # the 1/4" LLDPE row of the machine's stock table
MIN_BEND = STOCK.min_bend                    # its tightest centreline radius
# How far off a collet's own axis a soft-LLDPE run may leave or enter as ONE STRAIGHT LENGTH —
# the whole of what a push-to-connect grips through, well past the rigid-copper
# `_routing.COLLET_SKEW`. It is what lets a limb reach a barb off its own column on one leaning
# tube, so the fold's own `BARB_LEAD_FLOOR` is measured against it.
FLAVOR_SKEW = 22.0
LINE_HUG = 1.0                               # the clearance floor a line keeps off a body

HEAD_W = kp.head_w                           # the pump head, square across
MOTOR_D = kp.motor_dia
BARB_PITCH = kp.arch_xs[1] - kp.arch_xs[0]   # the two barbs' separation across the head face
BARB_INSET = kp.arch_plane_z - kp.head_front_z   # barb plane back from the head's front face

# --- The study's own figures, all four free --------------------------------
BUTT = 0.0            # tube left outside a pair of butted quick-connects
# In the enclosure pose the limb's +Y is world +Z. The four pump junction axes
# sit below the fold datum; the fore valves retain their independent elevation.
# The junction inlets follow the observed seated pump outlet row, preserving
# the straight, coaxial cartridge stems.
CARRIER_DROP = (_enc_if.pump_station_drop + _enc_if.manifold_rise
                + _enc_if.pump_seated_drop - kp.outlet_above_skirt_bottom)
INNER_LIMB_DROP = _enc_if.inner_limb_drop
FORE_VALVE_RISE = 10.0
FORE_STUB_GAP = FORE_VALVE_RISE + CARRIER_DROP
# EXPOSED tube between the two sleeve faces, not the cut length swallowed by their collets.
# The valve's own insertion depth is not measured, so the cut length remains a bench figure.
FORE_VALVES = frozenset(("V-E", "V-F", "V-H", "V-I"))
# The two outer aft valves stand inboard of their pump ports. The clocked lower
# junction outlets align straight links with the fixed return planes.
OUTER_AFT_X = 73.82  # valve axes retain the seam-rail running room
# Pump-junction authoring reference retained by the valve placement construction.
CARRIER_DATUM_SHIFT = -1.75
FIXED_TEE_AFT_SHIFT = 0.0
FORE_DECK_AFT_SHIFT = 0.0
AFT_DECK_AFT_SHIFT = 0.0
# Clearance for the scanned PP0308E bodies below the rear valve ports.
# The cold-core valves retain their existing seats.
AFT_PACK_RISE = 8.0
# Existing world lift is independent of the fixed routing's lowest surface.
WORLD_LIFT = 191.425
PACK_ORIGIN_Y = 14.48
CUSTOMER_STUB_PROJECTION = 12.851
CUSTOMER_TIP_TO_FACTORY_TIP = 1.5
# Reference span preserving the fitted pump/skirt datum. The permanent junction
# mouths and fixed returns have separately derived stations.
PUMP_BARBS_TO_RELEASE_PLANE = 5.526
BARB_PLATE_BERTH = (PUMP_BARBS_TO_RELEASE_PLANE - _enc_if.pump_station_lead
                    - CARRIER_DATUM_SHIFT - tee.BRANCH_COLLET_TRAVEL)
PUMP_BARB_Z = HEAD_W - _enc_if.pump_station_lead
# World Z is this study's Y after `enclosure_assembly.pose_manifold` stands the pack.
# The fitted outlet height, pump drop and manifold rise place the two ends on one tube plane
# while retaining the bracket's independent support datum.
PUMP_Y = (kp.outlet_above_skirt_bottom - _enc_if.pump_station_drop - _enc_if.pump_seated_drop
          - _enc_if.manifold_rise)
# Pump-to-deck reference span preserving the fitted pump placement.
# Customer stub tips are set independently by `customer_tip()`.
BARB_STANDOFF = BARB_PLATE_BERTH + _enc_if.pump_station_lead
CROSSBAR = 0.0        # exposed tube between Y-A's and Y-B's branches. At 0 the two fittings
                      # meet face to face across the mirror plane and no tube is drawn.
# The two fixed receiver axes follow each pump's measured `BARB_PITCH`;
# `LIMB_PITCH` is the authoring lane parameter.
LIMB_PITCH = float(os.environ.get("HSM_LIMB_PITCH", BARB_PITCH))

# --- What follows from them ------------------------------------------------
# The inner limbs are what the crossbar spans, so THEY are what it places: each stands one
# branch reach and half a crossbar off the mirror plane, and the pumps hang off them.
INNER_X = TEE_BRANCH + CROSSBAR / 2.0        # the inner limbs' axes
PUMP_DX = INNER_X + LIMB_PITCH / 2.0         # each pump's centre off the mirror plane
OUTER_X = PUMP_DX + LIMB_PITCH / 2.0         # the outer limbs'
OUTER_AFT_INSET = OUTER_X - OUTER_AFT_X
LIMB_STEP = (BARB_PITCH - LIMB_PITCH) / 2.0  # how far a limb reference steps toward its pump's axis,
                                             # off the barb's column, when the pitch is closed
# One straight tube leaning `LIMB_STEP` across as it climbs enters both its mouths at
# `atan(LIMB_STEP / climb)`, so the climb the skew allows is the floor under the lead.
BARB_LEAD_FLOOR = LIMB_STEP / math.tan(math.radians(FLAVOR_SKEW))
BARB_LEAD = BARB_LEAD_FLOOR + BARB_STANDOFF
DECK_Z = PUMP_BARB_Z + BARB_LEAD + TEE_BRANCH  # the LOWER deck's port-axis height
STUB = MIN_BEND                              # what a free mouth is drawn reaching, so the
                                             # first corner past it has a leg to seat in

# --- The fold --------------------------------------------------------------
# Valve placement starts with four flat limbs, folded180° around their reference
# run-face plane. `fold_radius()` derives the deck separation from the flat
# purchased-body envelopes. The permanent junction/return layout connects the
# resulting valve ports with straight links and a printed fluid passage.
HINGE_Y = -TEE_RUN
FOLD_CLEAR = LINE_HUG   # what the closest folded body is left standing off the one beneath it

ELBOW_LEG = 19.56                            # bend corner to collet face, both legs

# --- Colours ---------------------------------------------------------------
# Purchased bodies use the reference stock colours from `_materials`. The wet
# modules supply the printed junctions' and returns' material colours.
from _materials import (C_COIL, C_PUMP_BOSS, C_PUMP_HEAD,  # noqa: E402
                        C_PUMP_MOTOR, C_VALVE, M_JG_BLACK_PP)
C_TEE = M_JG_BLACK_PP
C_HEAD = C_PUMP_HEAD
C_BOSS = C_PUMP_BOSS
C_MOTOR = C_PUMP_MOTOR


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
# Each logical limb establishes valve authoring stations from reference body
# lengths. A valve tuple gives flow+1 aft or−1 forward; a Y tuple gives its
# reference branch direction. `anchor` identifies the pump-junction reference
# at y=0. Inner limbs take the draw ports; outer limbs take the discharge ports.

LIMBS = {
    "A1": dict(x=-INNER_X, anchor=3, chain=[
        ("V-A", +1), ("Y-A", (+1.0, 0.0, 0.0)), ("V-C", +1),
        ("Y-C", (0.0, 0.0, -1.0)), ("V-E", -1)]),
    "A2": dict(x=-OUTER_X, anchor=1, chain=[
        ("V-G", -1), ("Y-D", (0.0, 0.0, -1.0)), ("V-F", +1)]),
    "B1": dict(x=+INNER_X, anchor=3, chain=[
        ("V-B", +1), ("Y-B", (-1.0, 0.0, 0.0)), ("V-D", +1),
        ("Y-F", (0.0, 0.0, -1.0)), ("V-H", -1)]),
    "B2": dict(x=+OUTER_X, anchor=1, chain=[
        ("V-J", -1), ("Y-G", (0.0, 0.0, -1.0)), ("V-I", +1)]),
}

PUMPS = {"pump-a": -PUMP_DX, "pump-b": +PUMP_DX}   # each pump under its own channel's limbs

# Each pump junction's inlet, as (pump centre, which of the two ports).
BARB_OF = {"Y-C": (-PUMP_DX, +1), "Y-D": (-PUMP_DX, -1),
           "Y-F": (+PUMP_DX, -1), "Y-G": (+PUMP_DX, +1)}

# Four permanent pump-connected junctions. Compatibility offsets identify legacy
# callers; fixed station functions do not apply a service motion.
PUMP_JUNCTIONS = frozenset(BARB_OF)
FIXED_TEES = PUMP_JUNCTIONS
PUMP_VALVES = {"Y-C": ("V-E", "V-C"), "Y-D": ("V-F", "V-G"),
               "Y-F": ("V-H", "V-D"), "Y-G": ("V-I", "V-J")}
PUMP_PART_SUFFIX = {"Y-C": "east-inner", "Y-D": "east-outer",
                    "Y-F": "west-inner", "Y-G": "west-outer"}
# Compatibility names for callers that identify the four pump-connected nodes.
CARRIER_TEES = FIXED_TEES
CARRIER_RELEASE = tee.CARRIER_RELEASE_OFFSET
CARRIER_SQUEEZE = tee.CARRIER_SQUEEZE_OFFSET
CARRIER_CONNECTED = tee.CARRIER_CONNECTED_OFFSET
CARRIER_PARK = tee.CARRIER_PARK_OFFSET
CARRIER_STATES = {name: offset for name, (offset, _depth) in tee.CARRIER_STATES.items()}


def barb_station(tee: str) -> tuple:
    """A fitted pump barb's tube plane, on the independent pump and manifold Z datums,
    and offset `BARB_PITCH/2` either side of the pump's centre."""
    px, side = BARB_OF[tee]
    return (px + side * BARB_PITCH / 2.0, PUMP_Y, PUMP_BARB_Z)


def body_name(chain: str) -> str:
    """A chain entry's name as the assembly carries it. `build_assembly` labels a valve's body
    `valve` and a tee's `tee`, then hangs the chain's own name off it in lower case."""
    if chain in PUMP_JUNCTIONS:
        return "pump-receiver-" + PUMP_PART_SUFFIX[chain]
    return f"{'valve' if chain.startswith('V-') else 'tee'}-{chain.lower()}"


def _half(name: str) -> float:
    """Half a body's own length along the limb, collet face to centre."""
    return VALVE_LEN / 2.0 if name.startswith("V-") else TEE_RUN


def lay_out() -> dict:
    """Every body's centre and both its collet faces along its limb, FLAT, keyed by name.

    A chain is butted: each body's near collet face sits `BUTT` past its neighbour's far one.
    The anchor tee's centre is pinned at y = 0 — the plane its pump's barbs stand on — and the
    rest of the chain falls out either side of it. Everything ahead of the anchor is `fold`:
    it is what the hinge turns over."""
    out = {}
    for limb, spec in LIMBS.items():
        names = [n for n, _ in spec["chain"]]
        centres, y = [], 0.0
        for n in names:                                  # forward pass from the chain's nose
            centres.append(y + _half(n))
            y = centres[-1] + _half(n) + BUTT
        shift = -centres[spec["anchor"]]
        for i, ((n, arg), c) in enumerate(zip(spec["chain"], centres)):
            out[n] = dict(limb=limb, x=spec["x"], y=c + shift, arg=arg,
                          fold=i < spec["anchor"],
                          front=c + shift - _half(n), back=c + shift + _half(n))
    return out


FLAT = lay_out()
P = FLAT
PURCHASED_TEES = frozenset(n for n in P if n.startswith("Y-") and n not in PUMP_JUNCTIONS)

_tee_solid = None


def tee_solid():
    global _tee_solid
    if _tee_solid is None:
        _tee_solid = import_step(str(TEE_STEP)).val()
    return _tee_solid


_flat_cache = None


def flat_bodies() -> dict:
    """Every valve and tee placed FLAT — one deck, before the hinge turns anything. Built once:
    `fold_radius` boxes these, and `build_assembly` turns the folded ones about the hinge, so
    each solid is drawn a single time and the fold is a rigid move of it."""
    global _flat_cache
    if _flat_cache is not None:
        return _flat_cache
    out = {}
    # All ten stations share one purchased valve geometry.
    valve_body = vlv.build_body().union(vlv.build_port()).val()
    valve_coil = cq.Compound.makeCompound(
        [vlv.build_coil().val()] + [part.val() for part in vlv.build_spades()])
    for name, b in P.items():
        if name in PUMP_JUNCTIONS:
            continue
        if name.startswith("V-"):
            origin, (x_dir, z_dir) = (b["x"], b["y"], DECK_Z - VALVE_PORT_Z), valve_dirs(b["arg"])
            out[name] = [
                ("valve", place(valve_body, origin, x_dir, z_dir), C_VALVE),
                ("coil", place(valve_coil, origin, x_dir, z_dir), C_COIL)]
        else:
            x_dir, z_dir = tee_dirs(b["arg"])
            out[name] = [("tee", place(tee_solid(), (b["x"], b["y"], DECK_Z), x_dir, z_dir),
                          C_TEE)]
    _flat_cache = out
    return out


# How far apart the two decks stand. CHOSEN, and the build is what says whether it is enough.
#
# A bounding box will not answer this. What stands over what here is a folded valve's own
# underside against the SPADE TERMINALS of the valve beneath it — two 0.8 mm tabs reaching
# 15 mm past a coil face, at z 121, in a band 1.4 mm wide. Every box that contains those tabs
# also contains the coil crown 6 mm above them, so a box solve asks for 91.6 where the metal
# needs 58.4. `clashes()` measures the placed solids at full precision on every build, so the
# number below is chosen against it and not against a reach.
#
# `HSM_DECK_SEP` builds another.
DECK_SEP = float(os.environ.get("HSM_DECK_SEP", 60.95))
FOLD_BINDS = ("a folded valve's underside", "the spades of the one beneath it")
HINGE_Z = DECK_Z + DECK_SEP / 2.0
UPPER_Z = DECK_Z + DECK_SEP                  # the folded deck's port-axis height
FOLD_AXIS = (cq.Vector(0.0, HINGE_Y, HINGE_Z), cq.Vector(1.0, HINGE_Y, HINGE_Z))

# Compatibility figure: this is the printed return's internal flow radius;
# the connected LLDPE members are straight.
SPINE_R = _returns.TUBE_BEND_R


def fold_pt(p) -> tuple:
    """A point turned 180° about the hinge — the line x, y = HINGE_Y, z = HINGE_Z."""
    return (p[0], 2.0 * HINGE_Y - p[1], 2.0 * HINGE_Z - p[2])


def fold_dir(d) -> tuple:
    return (d[0], -d[1], -d[2])


def folded(solid):
    """A flat solid turned 180° about the hinge."""
    return solid.rotate(FOLD_AXIS[0], FOLD_AXIS[1], 180.0)


# --- The quarter turns -----------------------------------------------------
#
# Two of the butts open into a 90° turn instead, and both of them stand on ONE plane:
# `BEND_Y`, the far collet of the valve that ends a limb. Each joint's fixed collet opens +Y
# there, so the tube leaves along +Y, turns `BEND_R` onto +Z, and whatever was butted to it
# comes round with the turn — a quarter about the X-parallel line through the arc's own centre.
#
#   fluid-3, fluid-5     the source valves, off Y-A and Y-B on the folded deck
#
# X does not enter it: the axis runs along X, so the pair shares one (y, z) transform, and two
# turns that faced each other across the machine still do.
#
# NEITHER CHANNEL HAS A RESERVOIR TURN, because neither has a reservoir junction: each pair's
# fill and draw gates reach their reservoir's own two mouths, so all four collets are mouths of
# this study and leave on their own axes.
BEND_R = MIN_BEND
BEND_Y = TEE_RUN + VALVE_LEN                 # the plane both of them stand on
BENT = {"V-A": UPPER_Z, "V-B": UPPER_Z}


# The two source valves step again once they are round: `SOURCE_TRAVEL` further along the run
# and `SOURCE_JOG` across it, toward the foam shell's crown. Two arcs of one radius with a
# straight between them do that and leave the run pointing where it was, and the pair is fixed
# by the two distances:
#
#     travel = 2R·sinθ + s·cosθ        jog = 2R(1 − cosθ) + s·sinθ
#
# which solve to `(2R − jog)·cosθ + travel·sinθ = 2R`. A 90° pair is the member with no
# straight in it, and it puts the jog EQUAL to the travel — each quarter spends R on both axes.
#
# THE TRAVEL IS THE SOURCE RUN'S INTERNAL STEP. V-A and V-B occupy the source row at its far
# end; `enclosure_assembly.PACK_Y` carries that row, the other eight valves, both pumps and every
# pack fitting together. The cold core's three cradle stations are authored at the resulting
# row. `BARB_STANDOFF` fixes the pump-to-deck spacing inside the same rigid arrangement, while
# this figure is the whole longitudinal distance the two-arc step itself has to spend.
#
# THE JOG IS. `two_arc_floor` is `sqrt(jog·(4R − jog))`, which climbs with the jog for every jog
# under `2R` — so the jog alone says whether the two-arc family has a member at the travel there
# is, and it stands where BOTH channels' crosses clear that floor by `SOURCE_SLACK`. It is also
# where the two valves sit: the pose turns the pack's own −Y onto the machine's −Z, so a
# millimetre of jog is a millimetre of height the row on the cap gives up and a millimetre its
# printed cradles stand lower (`_cold_core_interface.cap_cradles`).
SOURCE_TRAVEL = 46.72
SOURCE_JOG = 13.625
# The step also carries each source valve OUTBOARD, off its own limb's column. A CROSS-MOVE IS A
# VECTOR AND NOT A DISTANCE: both arcs and the straight lie in the one plane that holds the run
# and the way it steps, so leaning that plane about the run costs the step nothing and only its
# length is solved for.
#
# V-A's spread is what centres it in the row of three the cold core's cap carries — V-B on this
# pack's west inner limb, V-A, then V-K on its own cap cradle. V-K is not in this study, so the
# figure is stated here and measured there:
# `enclosure_assembly.check_valve_row` prints the spread the row wants.
SOURCE_SPREAD = {"V-A": 1.92, "V-B": 0.0}


# WHAT A RUN DOES WHEN THE TRAVEL WILL NOT REACH IS GO BACKWARD. A hairpin — half a turn, a
# straight, and the other half — leaves the heading exactly where it found it and puts the run
# BEHIND where it started, which is travel handed back to the two-arc step that follows. The
# half-turns cancel between them (a heading that sweeps the whole circle sums its arcs to
# nothing), so the hairpin costs `2πR` and moves the run by its straight alone.
#
# THIS FIGURE IS THE MARGIN THE STEP KEEPS OVER `two_arc_floor`, AND WHAT IT BUYS IS A STRAIGHT.
# `sbend_solve` takes `acos(c / m)`, and at the floor that argument is exactly 1: the two arcs
# meet at a single point, the straight between them is zero, and the angle's slope against the
# travel is vertical — a pair solved there is a pair that a hundredth of a millimetre swings by
# a degree. Above the floor by this much each channel has a straight to stand on and an angle
# that answers its travel smoothly. Under it `hairpin_back` asks the hairpin for exactly what
# restores the margin; `hairpins_drawn` reports how many runs need one, and at the travel and
# the jog above it is none.
SOURCE_SLACK = 0.5
# WHERE A HAIRPIN LEAVES THE RUN, offset from the column it came down. The run climbs back past
# the height its own quarter turn is at, so it climbs in a different column than the one the
# quarter is in, and this is the gap between them. The step that follows spends it: what the
# hairpin puts out the step has to bring back, and its cross-move carries both.
#
# The lane it stands in leans between OUTBOARD and AWAY FROM THE CROWN: 0° is straight outboard,
# 90° straight away, and the sign of outboard is away from the mirror plane. The turn stands
# `2·BEND_R` off the run whichever way it faces, and the lean is what aims that reach into the
# room the bay has rather than at `fluid-18`'s crown lane or the channel's own quarter. ONE
# FIGURE SERVES BOTH CHANNELS, because until a hairpin is drawn nothing tells the two bays
# apart — and `hairpins_drawn` is 0 at the travel and the jog above.
HAIRPIN_OUT = 15.0
HAIRPIN_TILT = 49.0


def two_arc_floor(r: float, jog: float) -> float:
    """The least travel a PAIR of arcs of radius `r` can step `jog` across in. Under this the
    two-arc family has no member at all."""
    return math.sqrt(max(0.0, (2.0 * r) ** 2 - (2.0 * r - jog) ** 2))


def sbend_solve(r: float, travel: float, jog: float) -> tuple:
    """The arc angle and the straight between two of them that step `jog` across a run while
    it goes `travel` along, leaving the direction alone."""
    a, b, c = 2.0 * r - jog, travel, 2.0 * r
    m = math.hypot(a, b)
    if c > m:
        raise ValueError(
            f"a step of {jog:g} across in {travel:g} along cannot be made from two arcs of "
            f"R{r:g}: the pair reaches {m:.2f} where it needs {c:g}.")
    th = math.atan2(b, a) - math.acos(c / m)
    return th, (travel - 2.0 * r * math.sin(th)) / math.cos(th)


def source_offset(name: str) -> tuple:
    """The hairpin's own move, `(dx, dy)` in the pack's frame — `HAIRPIN_OUT` along the lane
    `HAIRPIN_TILT` names, which is also the plane the hairpin turns in. Zero when the travel
    needs no hairpin, and then the step is the whole run and has the whole cross."""
    if hairpin_back(MIN_BEND, SOURCE_TRAVEL, math.hypot(*source_cross(name))) <= 1e-9:
        return (0.0, 0.0)
    t = math.radians(HAIRPIN_TILT)
    return (math.copysign(HAIRPIN_OUT * math.cos(t), P[name]["x"]),
            HAIRPIN_OUT * math.sin(t))


def step_cross(name: str) -> tuple:
    """What is left for the two-arc step once the hairpin has had its move: the whole cross to
    the valve, less the hairpin's. The step brings the run back inboard as it drops it."""
    cross, off = source_cross(name), source_offset(name)
    return (cross[0] - off[0], cross[1] - off[1])


def hairpin_back(r: float, travel: float, jog: float) -> float:
    """How far behind its start the hairpin has to put the run, so that what is left for the
    two-arc step clears `two_arc_floor` by `SOURCE_SLACK`. Zero is the answer whenever the
    travel already clears it, and then there is no hairpin and the step is the whole run."""
    return max(0.0, two_arc_floor(r, jog) + SOURCE_SLACK - travel)


def source_valve_shift(name: str) -> tuple:
    """A source valve's cross-move, `(dx, dy)` in the pack's own frame: `SOURCE_JOG` toward the
    crown, which is −Y, and its own `SOURCE_SPREAD` away from the mirror plane."""
    return (math.copysign(SOURCE_SPREAD[name], P[name]["x"]), -SOURCE_JOG)


def source_cross(name: str) -> tuple:
    """Tube step from the raised crossbar to the unchanged cold-core valve."""
    x, y = source_valve_shift(name)
    return x, y - AFT_PACK_RISE


def source_step(name: str) -> tuple:
    """The step that carries one source valve off its quarter, as `(angle, straight, length)`,
    the length carrying the hairpin ahead of it when there is one. Each valve solves its own,
    because the spread is its own."""
    jog = math.hypot(*step_cross(name))
    back = hairpin_back(MIN_BEND, SOURCE_TRAVEL, jog)
    th, s = sbend_solve(MIN_BEND, SOURCE_TRAVEL + back, jog)
    length = 2.0 * MIN_BEND * th + s
    if back > 1e-9:
        length += 2.0 * math.pi * MIN_BEND + math.hypot(*source_offset(name), back)
    return th, s, length


# In the pack's own frame the source valves run along +Z once they are round, and the crown
# they are stepping toward is −Y.
SHIFT = {n: source_valve_shift(n) + (SOURCE_TRAVEL,) for n in SOURCE_SPREAD}
SHIFT.update({n: (0.0, FORE_VALVE_RISE, 0.0) for n in FORE_VALVES})
SHIFT.update({n: (0.0, -CARRIER_DROP, 0.0) for n in CARRIER_TEES})
SHIFT.update({n: (-math.copysign(OUTER_AFT_INSET, P[n]["x"]), 0.0, 0.0)
              for n in ("V-G", "V-J")})
for _name in ('V-C', 'V-D', 'V-G', 'V-J', 'Y-A', 'Y-B'):
    _dx, _dy, _dz = SHIFT.get(_name, (0., 0., 0.))
    SHIFT[_name] = (_dx, _dy + AFT_PACK_RISE, _dz)
for _name in ("V-A", "V-B", "Y-A", "Y-B", "V-C", "V-D"):
    _dx, _dy, _dz = SHIFT.get(_name, (0.0, 0.0, 0.0))
    SHIFT[_name] = (_dx, _dy - INNER_LIMB_DROP, _dz)


def bend_pt(p, z0: float) -> tuple:
    """A point taken round the quarter whose fixed collet sits at (`BEND_Y`, `z0`)."""
    dy, dz = p[1] - BEND_Y, p[2] - (z0 + BEND_R)
    return (p[0], BEND_Y - dz, z0 + BEND_R + dy)


def bend_dir(d) -> tuple:
    return (d[0], -d[2], d[1])


def bent(solid, z0: float):
    return solid.rotate(cq.Vector(0.0, BEND_Y, z0 + BEND_R),
                        cq.Vector(1.0, BEND_Y, z0 + BEND_R), 90.0)


def hairpin_flat(r: float, across: float, back: float) -> list:
    """The hairpin in its own plane's `(across, along)`, as `("arc", a, mid, b)` and
    `("line", a, b)`. It starts at the origin heading +along and ends on `(across, −back)`
    heading +along again, its arcs bearing toward +across.

    THE ARCS ARE NOT ANYONE'S TO SPEND. The heading sweeps the whole circle, so the arcs sum to
    nothing at all between them and the route lands entirely on the straight — one straight,
    aimed straight down the chord, at a cost of `2πr` and the chord. THAT is what puts the run
    BEHIND where it started, which no route of one heading-sweep less can do: the chord may
    point wherever it likes, backward included.

    A heading `h` on a turn of this hand has its centre at `p + r·(cos h, −sin h)` and its
    point back at `centre + r·(−cos h, sin h)`, which is all the tracing this needs."""
    aim = math.atan2(across, -back)
    segs, p, h = [], (0.0, 0.0), 0.0
    for turn, straight in ((aim, math.hypot(across, back)), (2.0 * math.pi - aim, 0.0)):
        c = (p[0] + r * math.cos(h), p[1] - r * math.sin(h))
        at = lambda hh: (c[0] - r * math.cos(hh), c[1] + r * math.sin(hh))     # noqa: E731
        # A three-point arc is only itself over a quarter or less, so the turn is cut into them.
        n = max(1, int(math.ceil(turn / (math.pi / 2.0) - 1e-9)))
        for k in range(n):
            h0, h1 = h + turn * k / n, h + turn * (k + 1) / n
            segs.append(("arc", at(h0), at((h0 + h1) / 2.0), at(h1)))
        p, h = at(h + turn), h + turn
        if straight > 1e-9:
            q = (p[0] + straight * math.sin(h), p[1] + straight * math.cos(h))
            segs.append(("line", p, q))
            p = q
    return segs


def hairpins_drawn() -> int:
    """How many of the source runs carry a hairpin. Zero whenever the travel is its own."""
    return sum(1 for v in SBENDS.values()
               if hairpin_back(MIN_BEND, SOURCE_TRAVEL, math.hypot(*step_cross(v))) > 1e-9)


def sbend_flat(r: float, travel: float, jog: float) -> list:
    """The two-arc step in its own plane's `(across, along)`, in the same segments. It starts at
    the origin heading +along and ends on `(jog, travel)` heading +along again, and here the
    arcs bear toward +across — which is where the step is going."""
    th, s = sbend_solve(r, travel, jog)
    c1 = (r, 0.0)
    e1 = (c1[0] - r * math.cos(th), c1[1] + r * math.sin(th))
    m1 = (c1[0] - r * math.cos(th / 2.0), c1[1] + r * math.sin(th / 2.0))
    e2 = (e1[0] + s * math.sin(th), e1[1] + s * math.cos(th))
    c2 = (e2[0] - r * math.cos(th), e2[1] + r * math.sin(th))
    e3 = (c2[0] + r, c2[1])
    ba, bz = (e2[0] - c2[0]) + (e3[0] - c2[0]), (e2[1] - c2[1]) + (e3[1] - c2[1])
    bl = math.hypot(ba, bz)
    segs = [("arc", (0.0, 0.0), m1, e1)]
    if s > 1e-9:
        segs.append(("line", e1, e2))
    segs.append(("arc", e2, (c2[0] + r * ba / bl, c2[1] + r * bz / bl), e3))
    return segs


def source_run(name: str, start, travel: float):
    """The whole run off one quarter, heading +Z at `start` and ending heading +Z on
    `start + source_cross(name) + travel`.

    TWO PLANES, ONE RUN. The hairpin is drawn in the plane the pack's X and the run span, and
    the step in the one `step_cross` and the run span; each is solved in its own
    `(across, along)` and stood up along its own across. They meet heading +Z, which is the
    only heading either of them ever ends on, so the tube is smooth through the joint without
    either knowing the other. The hairpin comes first, and what it hands the step is a travel
    that clears `two_arc_floor` and a column that is not the quarter's."""
    off, cross = source_offset(name), step_cross(name)
    jog = math.hypot(*cross)
    back = hairpin_back(BEND_R, travel, jog)
    o, edges = cq.Vector(*start), []
    lanes = [(cq.Vector(off[0], off[1], 0.0).normalized(),
              hairpin_flat(BEND_R, math.hypot(*off), back))] if back > 1e-9 else []
    lanes.append((cq.Vector(cross[0], cross[1], 0.0).normalized(),
                  sbend_flat(BEND_R, travel + back, jog)))
    for axis, segs in lanes:
        V = lambda p: o + axis * p[0] + cq.Vector(0.0, 0.0, p[1])              # noqa: E731
        for s in segs:
            edges.append(cq.Edge.makeThreePointArc(V(s[1]), V(s[2]), V(s[3])) if s[0] == "arc"
                         else cq.Edge.makeLine(V(s[1]), V(s[2])))
        o = edges[-1].endPoint()
    prof = cq.Wire.makeCircle(TUBE_D / 2.0, cq.Vector(*start), cq.Vector(0.0, 0.0, 1.0))
    return cq.Solid.sweep(prof, [], cq.Wire.assembleEdges(edges), makeSolid=True, isFrenet=True)


def quarter(x: float, z0: float):
    """One 90° turn: off the collet at (x, `BEND_Y`, z0) along +Y, round `BEND_R` onto +Z. It
    meets both collets on their own axes and carries no straight at either end."""
    r, k = BEND_R, BEND_R * math.sqrt(0.5)
    a = cq.Vector(x, BEND_Y, z0)
    b = cq.Vector(x, BEND_Y + r, z0 + r)
    mid = cq.Vector(x, BEND_Y + k, z0 + r - k)
    prof = cq.Wire.makeCircle(TUBE_D / 2.0, a, cq.Vector(0.0, 1.0, 0.0))
    return cq.Solid.sweep(prof, [], cq.Wire.assembleEdges([cq.Edge.makeThreePointArc(a, mid, b)]),
                          makeSolid=True, isFrenet=True)


def fixed_aft_shift(name: str) -> float:
    """Stationary pack translation in authoring +Z / enclosure +Y."""
    if name in FIXED_TEES:
        return FIXED_TEE_AFT_SHIFT
    return FORE_DECK_AFT_SHIFT if name in FORE_VALVES else AFT_DECK_AFT_SHIFT


def enclosure_point(point):
    """Authoring coordinates carried to the enclosure's fitted pump datum."""
    x, y, z = point
    return (-x, z + PACK_ORIGIN_Y, y + WORLD_LIFT)


def authoring_point(point):
    x, y, z = point
    return (-x, z - WORLD_LIFT, y - PACK_ORIGIN_Y)


def enclosure_axis(axis):
    x, y, z = axis
    return (-x, z, y)


def authoring_axis(axis):
    x, y, z = axis
    return (-x, z, y)


def authoring_shape(shape):
    """Invert the complete fitted enclosure pose for a native wet solid."""
    return (shape.translate((0., -PACK_ORIGIN_Y, -WORLD_LIFT))
            .rotate((0., 0., 0.), (0., 0., 1.), 180.)
            .rotate((0., 0., 0.), (1., 0., 0.), -90.))


def pump_wall_fore_y():
    """The fixed wall derived from the prepared stub's fitted tip station."""
    tip = enclosure_point(customer_tip(next(iter(sorted(PUMP_JUNCTIONS)))))
    return tip[1] - _receiver.CUSTOMER_TIP_Y


def pump_plumbing():
    """World-frame junctions, returns and straight links from their actual ports."""
    out = {}
    fore = pump_wall_fore_y()
    for name, (upper_valve, return_valve) in PUMP_VALVES.items():
        x, _y, z = enclosure_point(barb_station(name))
        upper = {"point": enclosure_point(port(upper_valve, "front")),
                 "axis": enclosure_axis(port_axis(upper_valve, "front"))}
        lower = {"point": enclosure_point(port(return_valve, "back")),
                 "axis": enclosure_axis(port_axis(return_valve, "back"))}
        out[name] = _returns.station(fore,x,z,upper,lower,_enc_if.z_seam+_enc_if.slide_slip)
    return out


def fixed_tee_centers(carry=None):
    """Compatibility accessor for the four printed junctions' inlet-gallery meets."""
    return {name: (carry((authoring_point(data["junction"]["gallery"]["inlet"]),
                          (0., 0., 1.)))[0] if carry is not None else
                   authoring_point(data["junction"]["gallery"]["inlet"]))
            for name, data in pump_plumbing().items()}


def _posed(name: str, p, d, carrier_offset: float = CARRIER_SQUEEZE):
    """A point and a direction taken through whichever of the two moves this body rides: the
    fold, and then the quarter turn if it is one of the six that got one."""
    b = P[name]
    if b["fold"]:
        p, d = fold_pt(p), fold_dir(d)
    if name in BENT:
        p, d = bend_pt(p, BENT[name]), bend_dir(d)
    if name in SHIFT:
        p = tuple(p[i] + SHIFT[name][i] for i in range(3))
    if name in CARRIER_TEES:
        p = (p[0], p[1], p[2] + CARRIER_DATUM_SHIFT + CARRIER_CONNECTED)
    p = (p[0], p[1], p[2] + fixed_aft_shift(name))
    return p, d


def port(name: str, end: str, carrier_offset: float = CARRIER_SQUEEZE):
    """A named body's collet face at one end of its limb, in the world it ends up in. `end` is
    the flat-state name — "front" is the collet at the smaller y before the fold, which for a
    folded body is the larger y after it."""
    if name in PUMP_JUNCTIONS:
        which = "lower" if end == "front" else "upper"
        return authoring_point(pump_plumbing()[name]["junction"][which]["point"])
    return _posed(name, (P[name]["x"], P[name][end], DECK_Z),
                  (0.0, -1.0, 0.0) if end == "front" else (0.0, 1.0, 0.0),
                  carrier_offset)[0]


def port_axis(name: str, end: str, carrier_offset: float = CARRIER_SQUEEZE):
    """The outward normal of that collet, in the world it ends up in."""
    if name in PUMP_JUNCTIONS:
        which = "lower" if end == "front" else "upper"
        return authoring_axis(pump_plumbing()[name]["junction"][which]["axis"])
    return _posed(name, (P[name]["x"], P[name][end], DECK_Z),
                  (0.0, -1.0, 0.0) if end == "front" else (0.0, 1.0, 0.0),
                  carrier_offset)[1]


def branch_port(name: str, carrier_offset: float = CARRIER_SQUEEZE):
    """A tee's branch collet face, as (point, outward axis), in the world it ends up in."""
    if name in PUMP_JUNCTIONS:
        x, _y, z = enclosure_point(barb_station(name))
        return authoring_point((x, pump_wall_fore_y(), z)), authoring_axis((0., -1., 0.))
    b, d = P[name], P[name]["arg"]
    return _posed(name, (b["x"] + d[0] * TEE_BRANCH, b["y"], DECK_Z + d[2] * TEE_BRANCH), d,
                  carrier_offset)


def carrier_collet_port(name: str, carrier_offset: float = CARRIER_SQUEEZE):
    """Compatibility accessor for a printed junction inlet or purchased branch."""
    if name in PUMP_JUNCTIONS:
        return branch_port(name, carrier_offset)
    p, axis = branch_port(name, carrier_offset)
    reach = tee_solid().BoundingBox().ymax
    inset = TEE_BRANCH - reach
    return tuple(p[i] - axis[i] * inset for i in range(3)), axis


def carrier_tee(name: str, carrier_offset: float = CARRIER_SQUEEZE):
    """One fixed fitting with its branch sleeve extended."""
    b = P[name]
    x_dir, z_dir = tee_dirs(b['arg'])
    solid = tee_solid()
    solid = place(solid, (b['x'], b['y'], DECK_Z), x_dir, z_dir)
    if b['fold']:
        solid = folded(solid)
    if name in BENT:
        solid = bent(solid, BENT[name])
    if name in SHIFT:
        solid = solid.translate(cq.Vector(*SHIFT[name]))
    return solid.translate((0, 0, CARRIER_DATUM_SHIFT + CARRIER_CONNECTED + FIXED_TEE_AFT_SHIFT))


# Each reservoir has separate draw and fill mouths, reached directly by its two
# valve paths. The four reservoir gate collets are external mouths of this study.
JOINS = {}


def _cross(a, b) -> tuple:
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def elbow_pose(gate: str, side: float) -> tuple:
    """The elbow on a draw gate's collet: `(corner, mouth, x_dir, z_dir, seat)`. Leg 2 opens
    across the pump, `side` picking which way; leg 1 — the fitting's own local +Y — runs onto
    the quarter turn that comes up off the gate.

    BOTH direction vectors go through `bend_dir`. `z_dir` alone rides it unchanged, because the
    turn's axis IS X and that is the axis `z_dir` lies on — so passing only that one leaves the
    fitting MOVED to the bent position and not TURNED into it, and leg 2 still lands because it
    is the leg on the axis. `seat` is where leg 1 ends up, taken off the placement frame itself,
    so `turns_meet` is checking the pose rather than a second copy of this arithmetic."""
    corner = bend_pt((P[gate]["x"], P[gate]["back"] + ELBOW_LEG, DECK_Z), ELBOW_BEND)
    mouth = (corner[0] + side * ELBOW_LEG, corner[1], corner[2])
    x_dir, z_dir = bend_dir((0.0, 0.0, side)), bend_dir((side, 0.0, 0.0))
    leg1 = _cross(z_dir, x_dir)                  # the fitting's local +Y, once placed
    seat = tuple(corner[i] + leg1[i] * ELBOW_LEG for i in range(3))
    return corner, mouth, x_dir, z_dir, seat


# --- Bodies ----------------------------------------------------------------

def lower_links() -> dict:
    """Stub and formed tube centerline segments in the manifold authoring frame."""
    def author(segment):
        return {k:authoring_point(v) if k in ('start_mm','end_mm','midpoint_mm') else
                authoring_axis(v) if k in ('start_tangent','end_tangent') else v
                for k,v in segment.items()}
    return {cid:{member:tuple(author(s) for s in pump_plumbing()[name]['elbow'][source])
                 for member,source in (('junction','formed_tube'),('valve','stub'))}
            for cid,name in LOWER_CONNECTIONS.items()}


def lower_tube(segments):
    return _receiver._sweep(TUBE_D,segments).cut(_receiver._sweep(_returns.TUBE_ID,segments)).clean()


def lower_link_length(cid: int) -> float:
    e=pump_plumbing()[LOWER_CONNECTIONS[cid]]['elbow']
    return e['stub_cut_nominal_mm']+e['formed_cut_nominal_mm']


def _junction_at_author_x(x):
    return min(PUMP_JUNCTIONS, key=lambda name: abs(P[name]["x"] - x))


def spine_radius(carrier_offset: float = CARRIER_SQUEEZE, x: float = 0.0) -> float:
    """Centerline bend radius of the formed lower tube."""
    return _returns.TUBE_BEND_R


def spine_offset_x(x: float) -> float:
    name = _junction_at_author_x(x)
    data = pump_plumbing()[name]
    return authoring_point(data["elbow"]["target"]["point"])[0] - x


def spine_middle_length(x: float) -> float:
    """Straight run between the elbow departure and valve approach turns."""
    return sum(s['length_mm'] for s in pump_plumbing()[_junction_at_author_x(x)]['elbow']['formed_tube'][:-1] if s['kind']=='line')


def spine_tube_length(x: float) -> float:
    """Nominal cut stock for the stub and formed run, including insertion allowances."""
    name = _junction_at_author_x(x)
    return lower_link_length(next(cid for cid, junction in LOWER_CONNECTIONS.items()
                                  if junction == name))


def build_elbow(gate: str, side: float):
    """One draw gate's elbow. Native frame: legs out +Y and +Z, bend corner at the origin."""
    corner, _mouth, x_dir, z_dir, _seat = elbow_pose(gate, side)
    solid = import_step(str(ELBOW_STEP)).val()
    return place(solid, corner, x_dir, z_dir)


def kamoer_bodies():
    """The reference pump's three solids — head, rear boss, then motor can — in the frame
    `kamoer_kphm400` draws them in, read once off its STEP.

    Sorted along that frame's depth axis, which is what tells them apart: the head is the
    solid in front of the base plane, the boss the one behind it, and the can behind that."""
    global _KAMOER
    if _KAMOER is None:
        solids = sorted(import_step(str(KAMOER_STEP)).val().Solids(),
                        key=lambda s: s.BoundingBox().zmin)
        _KAMOER = tuple(solids[:3])
    return _KAMOER


def build_pump(px: float):
    """Head, rear boss and motor as three solids, seated on the pump's own BARBS: both stand
    on `barb_station`'s lowered plane while the limbs' anchor tees keep the fold plane.

    All three are `kamoer_kphm400`'s solids, turned out of that module's case frame into this
    study's. There the pump's depth runs along +Z with the barbs on the head's +Y face; here
    the depth runs aft along +Y and the barbs stand on the head's crown. The quarter about X
    lays the depth axis down and the half about Y rolls the barb face up off it — which also
    swaps the two barbs across the head, and a peristaltic head has no fixed sense to swap."""
    y0 = -BARB_INSET + PUMP_Y
    parts = []
    for solid in kamoer_bodies():
        for axis, deg in PUMP_TURNS:
            solid = solid.rotate(cq.Vector(0, 0, 0), cq.Vector(*axis), deg)
        parts.append(solid.translate(cq.Vector(
            px + kp.cx, y0 - kp.head_front_z, PUMP_BARB_Z - kp.body_y_face)))
    return parts[0], parts[1], parts[2]


def straight(a, b, d: float = TUBE_D):
    """One length of tube between two collet faces."""
    v = cq.Vector(*[b[i] - a[i] for i in range(3)])
    return cq.Solid.makeCylinder(d / 2.0, v.Length, cq.Vector(*a), v.normalized())


def fore_stub_path(a, b, radius: float = MIN_BEND):
    """The straight, coaxial upper link between the junction and fore valve."""
    av, bv = cq.Vector(*a), cq.Vector(*b)
    return cq.Wire.assembleEdges([cq.Edge.makeLine(av, bv)])


def fore_stub_length(a, b, radius: float = MIN_BEND) -> float:
    return math.dist(a, b)


def bowed(a, b, developed=None, d: float = TUBE_D):
    """Compatibility entry point for a straight upper link."""
    return straight(a, b, d)


# --- The lines -------------------------------------------------------------
#
# Every connection `fluid-topology.md` names between the bodies in this study, and how it is
# made. A BUTT is two collet faces meeting: there is tube in both quick-connects and none
# between them, so the study draws no solid for it. The other two are straight lengths.

def customer_tip(name: str) -> tuple:
    start = barb_station(name)
    return (start[0], start[1], start[2] + CUSTOMER_STUB_PROJECTION)


def factory_tail_runs() -> dict:
    """No tail is needed inside the one-piece pump junction."""
    return {}


def factory_tail_length(name: str) -> float:
    """Compatibility accounting value for the one-piece junction."""
    return 0.0


def runs(carrier_offset: float = CARRIER_SQUEEZE) -> dict:
    """Fixed external paths; service-state argument is retained for callers."""
    out = {"crossbar": (branch_port("Y-A")[0], branch_port("Y-B")[0])}
    out.update({name: (barb_station(name), customer_tip(name)) for name in BARB_OF})
    out.update({name: (branch_port(name)[0], elbow_pose(*JOINS[name])[1]) for name in JOINS})
    return out


RUNS = runs()
BARB_TUBE_LEN = CUSTOMER_STUB_PROJECTION
PUMP_TUBE_PROJECTION = CUSTOMER_STUB_PROJECTION

# Four straight links from each printed junction to the fore valve above it.
# Their lengths exclude insertion inside both fittings.
def fore_stubs(carrier_offset: float = CARRIER_SQUEEZE) -> dict:
    return {
        "fore-y-c": (port("Y-C", "back", carrier_offset), port("V-E", "front")),
        "fore-y-d": (port("Y-D", "back", carrier_offset), port("V-F", "front")),
        "fore-y-f": (port("Y-F", "back", carrier_offset), port("V-H", "front")),
        "fore-y-g": (port("Y-G", "back", carrier_offset), port("V-I", "front")),
    }


FORE_STUBS = fore_stubs()
FORE_STUB_EXPOSED = fore_stub_length(*next(iter(FORE_STUBS.values())))


def turns_meet() -> list:
    """Each quarter turn's far end against the collet it is supposed to land on.

    A turn is only a connection if the body that came round with it came round BY THE SAME
    ROTATION. Moving a fitting to the bent position without turning it leaves the leg on the
    turn's own axis landing correctly and the other one pointing where it started, which reads
    as connected from every direction but the one that matters."""
    lands = {3: port("V-A", "back"), 5: port("V-B", "back")}
    out = []
    for cid, (x, z0) in sorted(QUARTERS.items()):
        end = (x, BEND_Y + BEND_R - INNER_LIMB_DROP + AFT_PACK_RISE, z0 + BEND_R + AFT_DECK_AFT_SHIFT)
        if cid in SBENDS:                                  # the step carries on from the quarter
            dx, dy = source_cross(SBENDS[cid])
            end = (end[0] + dx, end[1] + dy, end[2] + SOURCE_TRAVEL)
        out.append((cid, dist(end, lands[cid])))
    return out

SEGMENTS = [
    (3, "V-A-O", "Y-A-1", "turn"), (5, "V-B-O", "Y-B-1", "turn"),
    (6, "Y-A-3", "Y-B-3", "crossbar"),
    (7, "Y-A-2", "V-C-I", "butt"), (8, "Y-B-2", "V-D-I", "butt"),
    (9, "V-C-O", "Y-C-1", "spine"), (10, "V-E-O", "Y-C-2", "fore-y-c"),
    (11, "Y-C-3", "P-A-I", "Y-C"), (12, "P-A-O", "Y-D-1", "Y-D"),
    (13, "Y-D-2", "V-F-I", "fore-y-d"), (17, "Y-D-3", "V-G-I", "spine"),
    (19, "V-D-O", "Y-F-1", "spine"), (20, "V-H-O", "Y-F-2", "fore-y-f"),
    (21, "Y-F-3", "P-B-I", "Y-F"), (22, "P-B-O", "Y-G-1", "Y-G"),
    (23, "Y-G-3", "V-I-I", "fore-y-g"), (27, "Y-G-2", "V-J-I", "spine"),
]

# Where each quarter turn stands: the column its fixed collet is on, and which deck.
QUARTERS = {3: (-INNER_X, UPPER_Z), 5: (INNER_X, UPPER_Z)}
QUARTER_LEN = math.pi * BEND_R / 2.0
# The two that carry a step as well, off the far end of their own quarter — and the valve each
# one of those steps takes round with it, which is whose `SOURCE_SPREAD` the step is drawn to.
SBENDS = {3: "V-A", 5: "V-B"}

# The step's own room, on the card. `SOURCE_TRAVEL` is the step's longitudinal allowance and
# `SOURCE_JOG` sets the floor it has to clear, so this reads the two against each other on both
# channels at once. `enclosure_assembly.PACK_Y` seats the complete arrangement outside this
# construction, and `BARB_STANDOFF` fixes its pump-to-deck spacing. A run that falls under the
# floor grows a hairpin, `2πR` and a chord of tube spent going backward, and a step whose arcs
# meet at a point; the margin is what says neither is happening.
_bounds.state(
    "source-step-room", "Both source runs step on two arcs alone",
    f"the travel over the two-arc floor by {SOURCE_SLACK:g} mm on each channel",
    hairpins_drawn() == 0,
    "; ".join(
        f"{v} steps {math.hypot(*source_cross(v)):.2f} across, whose floor is "
        f"{two_arc_floor(MIN_BEND, math.hypot(*source_cross(v))):.2f} — "
        f"{SOURCE_TRAVEL - two_arc_floor(MIN_BEND, math.hypot(*source_cross(v))):+.2f} mm of "
        f"travel against the {SOURCE_SLACK:g} the step holds"
        for v in SBENDS.values())
    + ". `SOURCE_JOG` is the lever: the floor climbs with the cross, and the travel is the "
      "pack's to give, not this run's.")

# Each lower connection contains an upright valve elbow, short valve link and bent tube.
LOWER_CONNECTIONS = {9: "Y-C", 17: "Y-D", 19: "Y-F", 27: "Y-G"}
# Compatibility station lookup for topology/accounting callers.
SPINE = {cid: LIMBS[P[frm.rsplit("-", 1)[0]]["limb"]]["x"]
         for cid, frm, _to, how in SEGMENTS if how == "spine"}
SPINE_LEN = spine_tube_length(INNER_X)
SPINE_MIDDLE_LEN = spine_middle_length(INNER_X)
SPINE_STRAIGHT = SPINE_MIDDLE_LEN

# The eight mouths that leave this study. Each is drawn one `STUB` along its own axis, which is
# the straight its first corner needs before it can turn at all.
MOUTHS = [(cid, p, what, port(body, end), port_axis(body, end)) for cid, p, what, body, end in (
    ("fluid-2", "V-A-I", "tap water in", "V-A", "front"),
    ("fluid-4", "V-B-I", "funnel in", "V-B", "front"),
    ("fluid-18", "V-G-O", "flavor A", "V-G", "front"),
    ("fluid-28", "V-J-O", "flavor B", "V-J", "front"),
    ("fluid-14", "V-F-O", "reservoir A fill", "V-F", "back"),
    ("fluid-16", "V-E-I", "reservoir A draw", "V-E", "back"),
    ("fluid-24", "V-I-O", "reservoir B fill", "V-I", "back"),
    ("fluid-26", "V-H-I", "reservoir B draw", "V-H", "back"),
)]


def build_assembly(carrier_offset: float = CARRIER_SQUEEZE, *, include_fixed_wet=True) -> cq.Assembly:
    a = cq.Assembly(name="manifold-layout")
    state_runs = runs(carrier_offset)
    state_stubs = fore_stubs(carrier_offset)
    for name, parts in flat_bodies().items():
        for label, solid, color in parts:
            if P[name]["fold"]:
                solid = folded(solid)
            if name in BENT:
                solid = bent(solid, BENT[name])
            if name in SHIFT:
                solid = solid.translate(cq.Vector(*SHIFT[name]))
            solid = solid.translate(cq.Vector(0.0, 0.0, fixed_aft_shift(name)))
            a.add(solid, name=f"{label}-{name.lower()}", color=color)
    for tee_name, (gate, side) in JOINS.items():
        a.add(build_elbow(gate, side), name=f"elbow-{gate.lower()}-i", color=C_TEE)
    for pname, px in PUMPS.items():
        head, boss, motor = build_pump(px)
        a.add(head, name=f"{pname}-head", color=C_HEAD)
        a.add(boss, name=f"{pname}-boss", color=C_BOSS)
        a.add(motor, name=f"{pname}-motor", color=C_MOTOR)
    # Only the segments that carry tube outside their collets get a solid; the rest are butts.
    # Each is drawn in the colour of the spool it is cut off (`_routing.SPOOLS`), which on this
    # deck is black everywhere but `fluid-3` — V-A's outlet into Y-A, the last of the tap water
    # before the funnel's syrup meets it.
    for cid, _f, _t, how in SEGMENTS:
        if how in state_runs and dist(*state_runs[how]) > 1e-9:
            start, end = state_runs[how]
            a.add(straight(start, end), name=f"tube-fluid-{cid}",
                  color=_routing.tube_color(f"fluid-{cid}"))
        elif how in state_stubs:
            a.add(bowed(*state_stubs[how]), name=f"tube-fluid-{cid}",
                  color=_routing.tube_color(f"fluid-{cid}"))
    for cid, links in lower_links().items():
        for member, pair in links.items():
            a.add(lower_tube(pair), name=f"tube-fluid-{cid}-{member}",
                  color=_routing.tube_color(f"fluid-{cid}"))
    if include_fixed_wet:
        import dock_structure
        fore = pump_wall_fore_y()
        for name, data in pump_plumbing().items():
            junction = data["junction"]
            x, z = junction["pump_axis"]
            suffix = PUMP_PART_SUFFIX[name]
            wet = _receiver.build_receiver(fore, x, z, installed=True, junction=junction)
            a.add(authoring_shape(wet), name="pump-receiver-" + suffix, color=_receiver.COLOR)
            elbow = dock_structure.elbow_shape(data["elbow"])
            a.add(authoring_shape(elbow), name="pump-elbow-" + suffix, color=dock_structure.part_color("pump-elbow-"+suffix))
    for cid, (x, z0) in QUARTERS.items():
        a.add(quarter(x, z0).translate((0.0, -INNER_LIMB_DROP + AFT_PACK_RISE, AFT_DECK_AFT_SHIFT)),
              name=f"turn-fluid-{cid}", color=_routing.tube_color(f"fluid-{cid}"))
    for cid, name in SBENDS.items():
        x, z0 = QUARTERS[cid]
        a.add(source_run(name, (x, BEND_Y + BEND_R - INNER_LIMB_DROP + AFT_PACK_RISE,
                                 z0 + BEND_R + AFT_DECK_AFT_SHIFT), SOURCE_TRAVEL),
              name=f"step-fluid-{cid}", color=_routing.tube_color(f"fluid-{cid}"))
    # A mouth's stub is the first bend radius of the run that leaves on it, and carries that
    # run's own colour.
    for cid, _p, _what, p, axis in MOUTHS:
        a.add(straight(p, tuple(p[i] + axis[i] * STUB for i in range(3))),
              name=f"stub-{cid}", color=_routing.tube_color(cid))
    return a


# --- Controls --------------------------------------------------------------

class Extents(NamedTuple):
    """A box in world coordinates. Read as a clash it is the answer: the smallest side is how
    far a body has to go to be out, and the axis it lies on is which way. A volume is neither
    — 3 mm³ is a 30 x 1 x 0.1 graze along a face or a 1.4 mm cube driven through a wall, and
    those two want opposite corrections."""

    xmin: float
    ymin: float
    zmin: float
    xmax: float
    ymax: float
    zmax: float

    @property
    def escape(self) -> tuple:
        """`(axis, mm)` — the shortest translation that ends the overlap. Two convex bodies
        moved that far along that axis are exactly clear of each other; for the rest it is the
        first move to try, not a promise."""
        d = (self.xmax - self.xmin, self.ymax - self.ymin, self.zmax - self.zmin)
        i = min(range(3), key=lambda k: d[k])
        return "xyz"[i], d[i]

    def __str__(self) -> str:
        return (f"x[{self.xmin:8.2f},{self.xmax:8.2f}] y[{self.ymin:8.2f},{self.ymax:8.2f}] "
                f"z[{self.zmin:8.2f},{self.zmax:8.2f}]")


class Clash(NamedTuple):
    a: str
    b: str
    volume: float
    where: Extents


def extents(shape) -> Extents:
    """A shape's box, as `(xmin, ymin, zmin, xmax, ymax, zmax)`.

    Takes either a `Manifold` — what `_overlap.common` hands back — or a cq shape, whose box is
    read off its surface poles without meshing."""
    if hasattr(shape, "bounding_box"):
        return Extents(*shape.bounding_box())
    bb = Bnd_Box()
    BRepBndLib.Add_s(shape.wrapped, bb, False)
    return Extents(*bb.Get())


def placed_leaves(assy: cq.Assembly):
    """Every shape-bearing node of an assembly, world-placed, as `(name, shape, colour)`.

    AN ASSEMBLY MAY HOLD AN ASSEMBLY, and a pass that reads `children` one level deep does not
    see through one: a sub-assembly node carries no shape of its own, so such a pass either
    skips everything inside it or raises on the shape it has not got. This descends, composing
    each node's location down the branch, and hands back the leaves.

    A LEAF IS NAMED WHERE IT IS ADDED, path and all — `cold-core/evap-coil` is one body of the
    core. The name is the branch spelled out, stated once by whoever built the tree, so nothing
    here recomposes it and nothing downstream has to take it apart.
    """
    def walk(node, loc):
        here = loc * node.loc
        if node.obj is not None:
            shape = node.obj.val() if hasattr(node.obj, "val") else node.obj
            yield (node.name, shape.moved(cq.Location(here.wrapped.Transformation())),
                   node.color)
        for child in node.children:
            yield from walk(child, here)

    for child in assy.children:
        yield from walk(child, assy.loc)


def clashes(assy: cq.Assembly, floor: float = 1.0, bodies: dict = None):
    """Every pair of placed solids that shares more than `floor` mm³ — as `Clash(a, b, volume,
    where)`, `where` being the extents of the shared solid itself and not of either body — and
    every pair the boolean would not answer for. Butted collets meet on a plane and share
    nothing, so a clean arrangement returns two empty lists, and a pair OCCT raised on lands in
    the second one rather than passing for clean.

    The pair's boxes are a pre-filter and only that. Disjoint boxes prove disjoint solids, so
    skipping on them is sound; overlapping boxes prove nothing at all, which is why no pair is
    ever reported without the boolean having been asked.

    `bodies` names the placed solids to read INSTEAD of the assembly's own children — what a
    card hands in when the assembly exports a body some other card is what checks."""
    solids = (list(bodies.items()) if bodies is not None else
              [(name, shape) for name, shape, _colour in placed_leaves(assy)])
    boxes = [(n, s, _boxes.loose(s)) for n, s in solids]
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
                inter, v = _overlap.common(si, sj)
            except Exception as exc:
                unanswered.append((ni, nj, str(exc).splitlines()[0]))
                continue
            # `floor` is above zero, so the shared solid is never the empty one a void box
            # would be taken from.
            if v > floor:
                hits.append(Clash(ni, nj, v, extents(inter)))
    return hits, unanswered


def envelope(assy: cq.Assembly, stubs: bool):
    """The pack's box. Without `stubs` it is the bodies and the tube between them — what has to
    be found room for. With them it adds one bend radius off each of the eight mouths, which is
    the straight whatever routes them next has to leave in."""
    box = None
    for name, shape, _colour in placed_leaves(assy):
        if not stubs and name.startswith("stub-"):
            continue
        b = shape.BoundingBox()
        box = b if box is None else box.add(b)
    return box


# Channel A's body and channel B's. A mirrored pack puts each pair at ±x on one y and one z;
# `mirror_off` is how far it misses by.
#
# EVERY BODY IS IN A PAIR. Both reservoirs are reached the same way — each one's fill and draw
# gates land on its own two mouths — so the two channels hold the same bodies in the same
# order, and the table covers `P` with nothing left over.
TWINS = [("V-A", "V-B"), ("V-C", "V-D"), ("V-E", "V-H"), ("V-F", "V-I"), ("V-G", "V-J"),
         ("Y-A", "Y-B"), ("Y-C", "Y-F"), ("Y-D", "Y-G")]


def mirror_off() -> list:
    """Per twinned pair, how far the arrangement is from mirror-symmetric about x = 0: the two
    x's that should sum to zero, and the y they should share."""
    out = []
    for a, b in TWINS:
        out.append((a, b, abs(P[a]["x"] + P[b]["x"]), abs(P[a]["y"] - P[b]["y"])))
    out.append(("pump-a", "pump-b", abs(PUMPS["pump-a"] + PUMPS["pump-b"]), 0.0))
    return out


def dist(a, b) -> float:
    return sum((a[i] - b[i]) ** 2 for i in range(3)) ** 0.5


def skew_deg(a, b, axis) -> float:
    import math
    v = [b[i] - a[i] for i in range(3)]
    m = sum(c * c for c in v) ** 0.5
    dot = sum(v[i] * axis[i] for i in range(3)) / m
    return math.degrees(math.acos(max(-1.0, min(1.0, dot))))


def report(assy: cq.Assembly) -> dict:
    bb, reach = envelope(assy, stubs=False), envelope(assy, stubs=True)
    print("\nlimbs (front → back, y at each body's centre)")
    for limb, spec in LIMBS.items():
        row = "  ".join(f"{n}@{P[n]['y']:+.1f}" for n, _ in spec["chain"])
        print(f"  {limb}  x{LIMBS[limb]['x']:+7.2f}   {row}")

    made = {k: dist(*v) for k, v in RUNS.items()}
    made.update({k: FORE_STUB_EXPOSED for k in FORE_STUBS})
    print(f"\n{len(SEGMENTS)} connections")
    for cid, frm, to, how in SEGMENTS:
        if how == "spine":
            links = lower_links()[cid]
            note = (f"{sum(s['length_mm'] for s in links['valve']):.3f} mm short valve link + "
                    f"{sum(s['length_mm'] for s in links['junction']):.3f} mm formed LLDPE, scanned PP0308E elbow")
        elif how == "turn":
            note = f"{QUARTER_LEN:.2f} mm — one 90° turn at R{BEND_R:g}"
            if cid in SBENDS:
                th, s, length = source_step(SBENDS[cid])
                v = SBENDS[cid]
                back = hairpin_back(MIN_BEND, SOURCE_TRAVEL, math.hypot(*step_cross(v)))
                lead = (f"a hairpin {back:.2f} back and {math.hypot(*source_offset(v)):.2f} "
                        f"out, then " if back > 1e-9 else "")
                note = (f"{QUARTER_LEN + length:.2f} mm — one 90° turn at R{BEND_R:g}, then "
                        f"{lead}two of {math.degrees(th):.3f}° with {s:.2f} mm "
                        f"between: {SOURCE_TRAVEL:g} along and "
                        f"{math.hypot(*source_cross(v)):.2f} across")
        elif how in FORE_STUBS:
            note = f"{FORE_STUB_EXPOSED:.3f} mm straight coaxial upper link"
        else:
            length = made.get(how, 0.0)
            note = ("butt — 0 mm outside the collets" if length < 1e-9
                    else f"{length:.2f} mm straight"
                         + (" + one 90° elbow" if how in JOINS else ""))
            if cid in QUARTERS:
                note += f" + one 90° turn at R{BEND_R:g} ({QUARTER_LEN:.2f} mm)"
        print(f"  fluid-{cid:<3} {frm:>7} → {to:<7}  {note}")
    print(f"\n{len(MOUTHS)} mouths leave the study")
    for cid, p, what, (x, y, z), axis in MOUTHS:
        way = {(0.0, -1.0, 0.0): "front", (0.0, 1.0, 0.0): "back",
               (0.0, 0.0, 1.0): "up", (0.0, 0.0, -1.0): "down"}.get(
                   tuple(round(c, 6) + 0.0 for c in axis), str(axis))
        print(f"  {cid:<9} {p:>7}  ({x:7.2f}, {y:7.2f}, {z:6.2f})  {way:>5}  {what}")

    print(f"\nenvelope  X {bb.xlen:7.2f}   Y {bb.ylen:7.2f}   Z {bb.zlen:7.2f}    "
          f"({bb.xlen * bb.ylen * bb.zlen / 1e6:.2f} L)   bodies and the tube between them")
    print(f"          x[{bb.xmin:7.2f}, {bb.xmax:7.2f}]  y[{bb.ymin:7.2f}, {bb.ymax:7.2f}]  "
          f"z[{bb.zmin:7.2f}, {bb.zmax:7.2f}]")
    print(f"          X {reach.xlen:7.2f}   Y {reach.ylen:7.2f}   Z {reach.zlen:7.2f}    "
          f"({reach.xlen * reach.ylen * reach.zlen / 1e6:.2f} L)   with one {STUB:g} mm mouth "
          f"stub on each of the {len(MOUTHS)}")
    print(f"deck at z {DECK_Z:.2f}, {DECK_Z - VALVE_PORT_Z - PUMP_BARB_Z:.2f} mm over the pump heads; "
          f"each mm of BARB_LEAD lifts it one")
    print(f"LIMB_PITCH {LIMB_PITCH:g} of a {BARB_PITCH:g} barb pitch — each tee stands "
          f"{LIMB_STEP:.2f} mm off its barb's column on a {BARB_LEAD:.2f} mm lead, which is the "
          f"climb {FLAVOR_SKEW:g}° of skew asks for. HSM_LIMB_PITCH= builds another.")
    print(f"crossbar {CROSSBAR:.2f} mm exposed; the two reservoir crossings enter their collets "
          + ", ".join(f"{skew_deg(*RUNS[t], branch_port(t)[1]):.1f}°" for t in JOINS)
          + " off axis")
    print(f"upper links: {len(FORE_STUBS)} straight, {FORE_STUB_EXPOSED:g} mm exposed")
    f, u = FOLD_BINDS
    print(f"fold: hinge at y {HINGE_Y:.2f} z {HINGE_Z:.2f}, decks at z {DECK_Z:.2f} and "
          f"{UPPER_Z:.2f} — {DECK_SEP:g} apart, which {f} standing over {u} sets")
    print(f"lower links: {len(SPINE)} purchased elbows, each beneath its rear valve with a short valve link and bent LLDPE tube; "
          f"{spine_tube_length(INNER_X):.3f} mm inner and {spine_tube_length(OUTER_X):.3f} mm outer "
          f"nominal tube stock including insertion; formed tube radius R{SPINE_R:g}")
    steps = [(v, *source_step(v)) for v in SBENDS.values()]
    hairpins = hairpins_drawn()
    print(f"step: {len(SBENDS)} two-arc steps at R{BEND_R:g}, each {SOURCE_TRAVEL:g} along the "
          f"run and {abs(source_cross('V-B')[1]):g} across it toward the crown, {hairpins} behind a hairpin — "
          + "; ".join(f"{v} {math.degrees(th):.3f}° each side of {s:.2f} mm, {ln:.2f} mm of tube"
                      + (f", spread {SOURCE_SPREAD[v]:g} outboard" if SOURCE_SPREAD[v] else "")
                      for v, th, s, ln in steps))
    print(f"turns: {len(QUARTERS)} quarters at R{BEND_R:g}, {QUARTER_LEN:.2f} mm each — "
          f"all on the plane y {BEND_Y - INNER_LIMB_DROP + AFT_PACK_RISE:.2f}, {sum(1 for _c, (_x, z) in QUARTERS.items() if z == DECK_Z)} "
          f"on the lower deck and {sum(1 for _c, (_x, z) in QUARTERS.items() if z != DECK_Z)} on the folded one")
    print(f"source tube corners: {len(QUARTERS) + 2 * len(SBENDS) + 2 * hairpins}, at R{BEND_R:g}; "
          f"the recorded stock basis is {STOCK.source}. "
          "Pump-junction links use their documented straight or formed paths.")

    meets = turns_meet()
    worst_turn = max(d for _c, d in meets)
    print(f"\nturns meet their collets: {len(meets)} checked, worst {worst_turn:.4f} mm apart")
    for cid, d in meets:
        if d > 1e-6:
            print(f"  fluid-{cid} lands {d:.3f} mm off the collet it turns onto")

    off = mirror_off()
    worst = max(max(dx, dy) for _a, _b, dx, dy in off)
    print(f"\nmirror about x=0: {len(off)} twinned pairs, worst off by {worst:.4f} mm")
    for a, b, dx, dy in off:
        if max(dx, dy) > 1e-6:
            print(f"  {a} / {b}   x sums to {dx:.4f}, y differs by {dy:.4f}")

    bad, unanswered = clashes(assy)
    print(f"\nclash check: {len(bad)} pair(s) sharing volume, "
          f"{len(unanswered)} the boolean would not answer for")
    for c in bad:
        axis, d = c.where.escape
        print(f"  {c.a} ∩ {c.b}\n      {c.where}   {c.volume:.1f} mm³, "
              f"{d:.2f} on {axis} clears it")
    for ni, nj, why in unanswered:
        print(f"  {ni} ? {nj}   {why}")
    return dict(bb=bb, reach=reach, bad=bad + unanswered, made=made, mirror=off)


def selftest() -> int:
    """Manual geometry review of the fixed fluid pack, with no recurring hook."""
    failures = []
    for name in sorted(FIXED_TEES):
        a, b = RUNS[name]
        _mouth, axis = carrier_collet_port(name)
        if abs(skew_deg(a, b, axis) - 180) > 1e-6:
            failures.append(f"{name} customer stub is not on its receiver axis")
        if abs(dist(a, b) - CUSTOMER_STUB_PROJECTION) > 1e-8:
            failures.append(f"{name} customer stub misses its prepared-tip datum")
    for name, (a, b) in FORE_STUBS.items():
        shape = bowed(a, b)
        path = fore_stub_path(a, b)
        if not shape.isValid() or len(shape.Solids()) != 1:
            failures.append(f"{name} is not one valid straight upper link")
        if abs(path.Length() - fore_stub_length(a, b)) > 1e-6:
            failures.append(f"{name} fixed path length disagrees")
        if dist(path.startPoint().toTuple(), a) > 1e-8 or dist(path.endPoint().toTuple(), b) > 1e-8:
            failures.append(f"{name} misses its collet")
    for cid, links in lower_links().items():
        junction = LOWER_CONNECTIONS[cid]
        valve = PUMP_VALVES[junction][1]
        if dist(links["junction"][0]["start_mm"], port(junction, "front")) > 1e-8 \
                or dist(links["valve"][-1]["end_mm"], port(valve, "back")) > 1e-8:
            failures.append(f"fluid-{cid} inserted tubes miss their junction or valve")
        for member, pair in links.items():
            shape = lower_tube(pair)
            if not shape.isValid() or len(shape.Solids()) != 1:
                failures.append(f"fluid-{cid}-{member} is not one valid tube member")
    for failure in failures:
        print(f"FAIL: {failure}")
    if failures:
        return 1
    print("PASS: four prepared pump spans, four straight upper links and four short valve links and four single-bend lower tubes meet their stations")
    return 0


def main():
    assy = build_assembly()
    out = _here.parent / "manifold-layout.step"
    export_assembly(assy, str(out))
    print(f"-> {out.name}")
    r = report(assy)
    bb, reach = r["bb"], r["reach"]
    straight_lldpe_count = len(FORE_STUBS) + len(LOWER_CONNECTIONS)
    swallowed_lldpe_count = sum(
        how == "butt" or (how == "crossbar" and dist(*RUNS[how]) < 1e-9)
        for _cid, _frm, _to, how in SEGMENTS)
    lldpe_cut_count = (straight_lldpe_count + len(LOWER_CONNECTIONS) + len(QUARTERS) + len(JOINS)
                       + swallowed_lldpe_count)
    substitute_md(
        _here.parent / "README.md",
        variables={
            "ENV_X": f"{bb.xlen:.0f}", "ENV_Y": f"{bb.ylen:.0f}", "ENV_Z": f"{bb.zlen:.0f}",
            "ENV_L": f"{bb.xlen * bb.ylen * bb.zlen / 1e6:.2f}",
            "REACH_X": f"{reach.xlen:.0f}", "REACH_Y": f"{reach.ylen:.0f}",
            "REACH_Z": f"{reach.zlen:.0f}", "STUB_LEN": f"{STUB:g}",
            "DECK_Z": f"{DECK_Z:.2f}", "DECK_Z2": f"{DECK_Z:.2f}",
            "UPPER_Z": f"{UPPER_Z:.2f}", "UPPER_Z2": f"{UPPER_Z:.2f}",
            "SPINE_R": f"{SPINE_R:g}", "SPINE_LEN": f"{SPINE_LEN:.2f}",
            "SPINE_STRAIGHT": f"{SPINE_STRAIGHT:.2f}",
            "SPINE_MIDDLE_LEN": f"{SPINE_MIDDLE_LEN:.2f}",
            "OUTER_AFT_INSET": f"{OUTER_AFT_INSET:g}",
            "OUTER_SPINE_MIDDLE_LEN": f"{spine_middle_length(OUTER_X):.2f}",
            "OUTER_SPINE_LEN": f"{spine_tube_length(OUTER_X):.2f}",
            "DECK_SEP": f"{DECK_SEP:g}",
            "SPINE_COUNT": str(len(SPINE)), "MIN_BEND2": f"{MIN_BEND:g}",
            "QUARTER_R": f"{BEND_R:g}", "QUARTER_LEN": f"{QUARTER_LEN:.2f}",
            "QUARTER_COUNT": str(len(QUARTERS)), "QUARTER_COUNT2": str(len(QUARTERS)),
            "QUARTER_COUNT4": str(len(QUARTERS)), "MOUTH_COUNT2": str(len(MOUTHS)),
            "BEND_Y": f"{BEND_Y - INNER_LIMB_DROP + AFT_PACK_RISE:.2f}",
            "CORNER_COUNT": str(len(QUARTERS) + 2 * len(SBENDS)
                                + 2 * hairpins_drawn()),
            "STEP_ANGLE": f"{math.degrees(source_step('V-B')[0]):.3f}",
            "STEP_STRAIGHT": f"{source_step('V-B')[1]:.2f}",
            "STEP_LEN": f"{source_step('V-B')[2]:.2f}",
            "STEP_TRAVEL": f"{SOURCE_TRAVEL:g}", "STEP_JOG": f"{abs(source_cross('V-B')[1]):g}",
            "STEP_TRAVEL2": f"{SOURCE_TRAVEL:g}", "STEP_TRAVEL3": f"{SOURCE_TRAVEL:g}",
            "STEP_JOG2": f"{abs(source_cross('V-B')[1]):g}",
            "STEP_FLOOR": f"{two_arc_floor(MIN_BEND, abs(source_cross('V-B')[1])):.2f}",
            "HAIRPIN_COUNT": str(hairpins_drawn()),
            "BARB_STANDOFF": f"{BARB_STANDOFF:g}",
            "BARB_TUBE_LEN": f"{BARB_TUBE_LEN:.2f}",
            "BARB_PLATE_BERTH": f"{BARB_PLATE_BERTH:g}",
            "FORE_STUB_GAP": f"{FORE_STUB_GAP:g}",
            "FORE_STUB_EXPOSED": f"{FORE_STUB_EXPOSED:g}",
            "FORE_STUB_COUNT": str(len(FORE_STUBS)),
            "PUMP_STATION_LEAD": f"{_enc_if.pump_station_lead:g}",
            "PUMP_DROP": f"{_enc_if.pump_station_drop:g}",
            "STEP_SPREAD": f"{SOURCE_SPREAD['V-A']:g}",
            "STEP_CROSS_A": f"{math.hypot(*source_cross('V-A')):.2f}",
            "STEP_ANGLE_A": f"{math.degrees(source_step('V-A')[0]):.3f}",
            "STEP_STRAIGHT_A": f"{source_step('V-A')[1]:.2f}",
            "STEP_LEN_A": f"{source_step('V-A')[2]:.2f}",
            "DECK_GAP": f"{DECK_Z - VALVE_PORT_Z - PUMP_BARB_Z:.2f}",
            "CROSSBAR": f"{CROSSBAR:.2f}",
            "TEE_COUNT": str(len(PURCHASED_TEES)),
            "TEE_COUNT2": str(len(PURCHASED_TEES)),
            "TUBE_COUNT2": str(lldpe_cut_count),
            "TWIN_COUNT": str(len(r["mirror"])),
            "MIRROR_OFF": f"{max(max(dx, dy) for _a, _b, dx, dy in r['mirror']):.4f}",
            "SEGMENT_COUNT": str(len(SEGMENTS)),
            # A butt is a lane segment whose drawn length is zero. The fold and quarter-turn
            # constructions carry their lengths outside ``made`` and are not butts.
            "BUTT_COUNT": str(sum(1 for s in SEGMENTS
                                  if s[3] not in ("spine", "turn")
                                  and r["made"].get(s[3], 0.0) < 1e-9)),
            "TUBE_COUNT": str(lldpe_cut_count),
            "STRAIGHT_LLDPE_COUNT": str(straight_lldpe_count),
            "STRAIGHT_COUNT": str(sum(1 for s in SEGMENTS if s[3] in RUNS
                                      and r["made"].get(s[3], 0.0) >= 1e-9)),
            "MOUTH_COUNT": str(len(MOUTHS)),
            "MIN_BEND": f"{MIN_BEND:g}",
            "BARB_PITCH": f"{BARB_PITCH:g}", "BARB_PITCH2": f"{BARB_PITCH:g}",
            "BARB_INSET": f"{BARB_INSET:g}",
            "VALVE_PITCH": f"{VALVE_PITCH:g}", "VALVE_PORT_Z": f"{VALVE_PORT_Z:g}",
            "VALVE_LEN": f"{VALVE_LEN:g}",
            "TEE_RUN": f"{TEE_RUN:g}", "TEE_SPAN": f"{2 * TEE_RUN:g}",
            "DIVIDER_PITCH": f"{2 * ydiv.OUTLET_Y:g}",
            "LIMB_OUT_XW": f"{-OUTER_X:.2f}", "LIMB_IN_XW": f"{-INNER_X:.2f}",
            "LIMB_IN_XE": f"{INNER_X:+.2f}", "LIMB_OUT_XE": f"{OUTER_X:+.2f}",
            "INNER_GAP": f"{2 * INNER_X - VALVE_PITCH:.2f}",
            "CLASHES": str(len(r["bad"])),
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    if sys.argv[1:] == ["selftest"]:
        sys.exit(selftest())
    if sys.argv[1:]:
        sys.exit("usage: manifold_layout.py [selftest]")
    sys.exit(main())
