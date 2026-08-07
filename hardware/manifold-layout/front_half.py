"""Front half — the refrigeration stratum, the flavor manifold standing on it, and the cold
core behind the pair.

Four bodies, mated face to face with nothing between them:

    compressor-shroud   its INTAKE-side face against
    condenser+fan       turned onto it, and the pair yawed as one by `BASE_YAW`
    manifold-layout     set down on the crown of those two, on the four SPINE HAIRPINS
    foam-assembly       at the machine's own `FOAM_YAW`, on the floor, its front face on the
                        plane the front half ends at

The gaps are 0 by intent. The compressor stands well inside its shroud and its ports go
wherever they are put; the condenser's inlet and outlet are cornered but leave by whichever
of that corner's faces is convenient; the cold core's ten ports all stand on one column of
its own. So the bodies touching is what makes the runs between them short.

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
           _hw / "reference" / "waveshare-43b-display",
           _hw / "reference" / "meanwell-irm90",
           _hw / "reference" / "teyleten-relay",
           _hw / "reference" / "ground-ring-stack",
           _hw / "reference" / "asse1022-assembly",
           _hw / "printed-parts" / "enclosure" / "drip-pan",
           _hw / "reference" / "water-split",
           _hw / "reference" / "neofit-flow-control",
           _hw / "printed-parts" / "enclosure" / "enclosure"):
    sys.path.insert(0, str(_p))
from _cadq_export import export_assembly              # noqa: E402
import _lines                                         # noqa: E402
import condenser_block as _cond                       # noqa: E402
import enclosure as _enc                              # noqa: E402
import hopper_funnel as _funnel                       # noqa: E402
import manifold_layout as ml                          # noqa: E402
import seaflo_suction_chain as _suct                  # noqa: E402
import waveshare_43b_display as _disp                 # noqa: E402
import asse1022_assembly as _asse                     # noqa: E402
import drip_pan as _pan                               # noqa: E402
import neofit_flow_control as _flowreg                # noqa: E402
import water_split as _split                          # noqa: E402

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


def seat_body(shape, turns=(), station=None, **planes):
    """A body's whole placement: turned through each `(axis, degrees)` in `turns`, then moved by
    whole planes (`sit`).

    `planes` moves it by whole faces of its own box; `station` instead seats one of its own
    mouths on a world point, which is what a fitting actually answers to.

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

    return shape.translate(shift), carry


# --- The base: two bodies, one plane between them --------------------------
#
# The pair is built mated and then turned as ONE body about its own centre, because the mating
# is between the two of them and the turn is about where the air goes. `BASE_YAW` is that turn:
# the condenser's `AIRFLOW` axis is its native X and the fan is on the face the air leaves by,
# so the quarter that brings its west face onto the shroud's aft plane also lays the fan on +Y,
# and this puts it back across the cabinet.
BASE_YAW = -90.0


def build_shroud():
    """The shroud as the machine turns it, its front face on y = 0 and its feet on the floor."""
    s = cq.importers.importStep(str(SHROUD_STEP)).val().rotate(*Z_AXIS, SHROUD_YAW)
    return sit(s, cx=0.0, y0=0.0, z0=0.0)


def build_condenser(shroud):
    """The block turned a quarter about Z, which brings the WEST face the mating names round
    onto the shroud's own aft plane, and stood on the same floor."""
    c = _cond.build()
    c = c.toCompound() if hasattr(c, "toCompound") else c
    return sit(c.rotate(*Z_AXIS, 90.0), cx=0.0, y0=box(shroud).ymax, z0=0.0)


def build_foam(front_y: float):
    """The cold core at the machine's own `FOAM_YAW` and on the machine's own floor, its front
    face on the plane the front half ends at. Its native box hangs 20 mm below its origin, so
    the floor is the box's own bottom and not that origin."""
    f = cq.importers.importStep(str(FOAM_STEP)).val().rotate(*Z_AXIS, FOAM_YAW)
    return sit(f, cx=0.0, y0=front_y, z0=0.0)


def build_seaflo(foam):
    """The water pump at the machine's own `SEAFLO_YAW`, lying flat on the core's crown, centred
    on the mirror plane, its aft face flush with the core's own back."""
    b = box(foam)
    return seat_body(cq.importers.importStep(str(SEAFLO_STEP)).val(),
                (((0, 0, 1), SEAFLO_YAW),), cx=0.0, y1=b.ymax, z0=b.zmax)


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


def build_suction_chain(seaflo, suction):
    """The chain laid in the lane east of the pump, on the crown the pump itself stands on.

    Its three coordinates answer to the run it carries and the lane it lies in: X one
    `SUCT_PUMP_GAP` east of the pump's casting, Y standing its barb `SUCT_CORNER_ROOM` forward
    of the pump's suction mouth so `water-7`'s corner seats a whole arc, and Z on the core's
    crown — the plane the pump's own feet stand on, so the chain needs no stand of its own
    height.

    What holds it there is an open item: nothing threads onto this chain and nothing clamps it.
    It has a measured datum and measured room; it does not have a bracket."""
    b = box(seaflo)
    return seat_body(_suct.build(), SUCT_CHAIN_TURN,
                cx=b.xmax + SUCT_PUMP_GAP + _suct.HOSE_OD / 2.0,
                y1=suction[0][1] - SUCT_CORNER_ROOM, z0=b.zmin)


# The assembly's non-manifold members, by name. `report` measures the manifold pack as
# one box — the clearances the core and the pump stand off are struck against it — so a
# body added to the assembly that is not part of that pack has to be named here or it
# joins the box and moves every one of them.
STANDALONE = ("compressor-shroud", "condenser+fan", "foam-assembly", "seaflo-pump",
              "hopper-funnel", "suction-chain", "display", "psu", "pcba",
              "relay-1", "ac-hub", "ground-stack", "asse1022-assembly", "drip-pan",
              "water-split", "flow-regulator")


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
    return seat_body(cq.importers.importStep(str(PSU_STEP)).val(), PSU_TURN,
                     x1=wall_seat,
                     y1=_enc.rear_plane_y - _enc.rear_seam_clear - PSU_REAR_CLEAR,
                     z0=b.zmax)


# The controller board joins the brick's column rather than standing forward of the deck: same
# flank, same seat, same floor. The ROLL is what fits it — a quarter about Y stands the board on
# its long edge and lays that edge fore and aft down the flank, so only its 19.1 mm of thickness
# and components reaches into the lane. The YAW is which face meets the wall: the board's flat
# back is what mounts, so it faces +X. A flat side is only useful pointed at the thing it lies
# against; turned the other way it is 19.1 mm of components pressed into the wall and a bare
# board staring into the lane.
PCBA_TURN = (((0.0, 1.0, 0.0), -90.0), ((0.0, 0.0, 1.0), 0.0))
# What the board stands off the brick along the flank. Both are wired, and a hand making off a
# connector between them needs the gap to be a gap.
PCBA_PSU_CLEAR = 6.0


def build_pcba(foam, psu, wall_seat):
    """The controller board on the +X wall, forward of the brick on the same cap.

    EAST on the same wall seat the brick takes, so the two stand in one plane and the boss band
    holds them both; AFT one `PCBA_PSU_CLEAR` ahead of the brick's own front face; FOOT on the
    cap. What holds it is the pcba-tray, which is not placed — this is the board's envelope."""
    return seat_body(cq.importers.importStep(str(PCBA_STEP)).val(), PCBA_TURN,
                     x1=wall_seat, y1=box(psu).ymin - PCBA_PSU_CLEAR, z0=box(foam).zmax)


# The rest of the power block, stacked on the brick's crown in one column: the relay, the AC
# hub over it, the ground stud over that. Each takes the same wall seat as its east face, so the
# whole column stands clear of every post, pod and plug the Y seam puts in that band, and each
# stands on the one below with a clearance floor between them.
#
# Each turn lays the body's own long axis fore and aft down the flank and its board or wells
# facing INBOARD — the face a screwdriver reaches, and the face a boss would land on.
RELAY_TURN = (((0.0, 0.0, 1.0), 270.0), ((0.0, 1.0, 0.0), 270.0))
AC_HUB_TURN = (((0.0, 0.0, 1.0), 90.0), ((0.0, 1.0, 0.0), 270.0))
STACK_CLEAR = 1.0


def build_stack(psu, wall_seat):
    """The three bodies over the brick, each on the crown of the one below, as
    `[(name, solid, colour)]`.

    They stack aft-flush with the brick. The hub's aft face wants the C14 receptacle's, which is
    the one body on this flank that comes inboard at this height — it is a back-panel body and it
    is not placed, so the brick is what they line up on until it is."""
    aft = box(psu).ymax
    out, floor = [], box(psu).zmax
    for name, step, turn, colour in (
            ("relay-1", RELAY_STEP, RELAY_TURN, C_RELAY),
            ("ac-hub", AC_HUB_STEP, AC_HUB_TURN, C_AC_HUB),
            ("ground-stack", GND_STACK_STEP, RELAY_TURN, C_GND)):
        solid, _carry = seat_body(cq.importers.importStep(str(step)).val(), turn,
                                  x1=wall_seat, y1=aft, z0=floor + STACK_CLEAR)
        out.append((name, solid, colour))
        floor = box(solid).zmax
    return out


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
# What the chain stands off the rear seam — room for the bulkhead it is fed from and for
# `water-1` to turn out of it. The bulkhead is a back-panel body and is not placed.
ASSE_REAR_CLEAR = 20.0
# THE PUMP'S WIDTH IS ITS BRACKET'S, AND ONLY FOR THE 8 mm THE BRACKET IS TALL. The splayed
# feet reach x ±49 from the cap up to `seaflo_22_pump.FOOT_T`; above that the casting's own west
# face stands at −28 aft of the motor's mid-length and −40 at its widest. So the lane west of the
# pump is 59.5 mm wide at the feet and 80.5 mm wide over them, and the basin — 73 over its rim,
# `PAN_X` struck off the moisture plate and ten of flange each way for the fingertip that draws
# the tray out — fits the second and not the first.
#
# So the chain and its basin RIDE OVER THE FEET rather than standing beside them. Both floors
# come off this one plane.
FOOT_CLEAR = 1.0


def pan_floor(foam, seaflo):
    """The Z the basin's own floor stands at: one clearance over the pump's bracket."""
    return max(box(foam).zmax, box(seaflo).zmin + _lines._pump.FOOT_T) + FOOT_CLEAR


def build_asse(foam, seaflo):
    """The ASSE 1022 chain in the west lane, high enough over the cold core's cap that the drip
    pan stands under its vent.

    Its HEIGHT is the pan's, read off the pan's own module rather than typed: the basin's floor
    lies on the cap, its rim one `PAN_Z` above that, and the chain's underside one
    `VENT_GAP` of air over the rim. So the vent's drip falls the gap the basin was drawn for,
    and a change to either number moves both bodies together.

    Its X hugs the cold core's west face, leaving the rest of the lane between it and the pump.
    Its Y stands the inlet `ASSE_REAR_CLEAR` ahead of the rear seam's standoff, which puts the
    vent aft of the bracket's own forward edge — the band where the lane is at its widest.

    What holds it is the wall clamps, which are a top-wall feature and an open item."""
    chain = _asse.build()
    chain = chain.toCompound() if hasattr(chain, "toCompound") else chain
    chain = chain.val() if hasattr(chain, "val") else chain
    return seat_body(chain, (((0.0, 0.0, 1.0), ASSE1022_YAW),),
                     x0=box(foam).xmin,
                     y1=_enc.rear_plane_y - _enc.rear_seam_clear - ASSE_REAR_CLEAR,
                     z0=pan_floor(foam, seaflo) + _pan.PAN_Z + _pan.VENT_GAP)


def build_pan(foam, seaflo, asse_carry, west_face):
    """The catch basin under the atmospheric vent, standing on the cold core's cap.

    THE VENT IS THE DATUM in both plan axes: the drip leaves the stub's tip and falls straight
    down, so the tip has to stand over the basin's inner floor and not merely over its rim.
    `drip_pan.check_plate` is what fixes the basin's size — the moisture plate lying flat in it
    sets the floor, and the rim flange adds the fingertip lip the tray is drawn out by.

    IN X THE WALL BOUNDS IT AND THE VENT DOES NOT. Centred on the tip the rim flange stands
    2 mm inside the −X wall, so the basin sits with its flange ON that wall's inner face and the
    tip lands 2 mm off the floor's own centre — which is 2 mm of a ±22 mm floor, and the drip
    still falls well inside the coves. Drawing the tray out wants a slot through that wall; the
    slot is a wall port and the pack carries none yet.

    Z is `pan_floor` — one clearance over the pump's bracket, not on the cap — with the rim one
    `PAN_Z` up and the chain's underside one `VENT_GAP` over that. `build_asse` stands the chain
    on the same three numbers, so the drip falls exactly the gap the basin was drawn for."""
    tip = asse_carry(_asse.port("vent-tip"))[0]
    pan = _pan.build()
    pan = pan.val() if hasattr(pan, "val") else pan
    return seat_body(pan, (), x0=west_face, cy=tip[1], z0=pan_floor(foam, seaflo))


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
    return seat_body(_split.build(), SPLIT_TURN, station=(_split.supply(), target))


# --- the flow regulator, inline on the flavour tap -------------------------
#
# The needle valve that throttles the flavour side. Its own frame runs the flow down ±X with
# the adjuster on +Z, so a yaw of a quarter lays that flow along the lane and leaves the
# adjuster looking at the ceiling. It is set once on the bench and `design-pressures.md` does
# not buy access after assembly, but a stem pointing up is the one direction that costs
# nothing to leave open.
FLOWREG_TURN = (((0.0, 0.0, 1.0), -90.0),)
# The straight between the split's flavour collet and the regulator's inlet — `fluid-1`, which
# has no corner in it for the same reason `water-2` has none.
FLUID_1 = 24.0


def build_flowreg(split_carry):
    """The regulator seated on its INLET, one `FLUID_1` forward of the split's flavour collet
    and on that collet's own line — so the tap runs ASSE, split, regulator down one axis and
    every joint between them is a straight."""
    pos, axis = split_carry(_split.to_flavor())
    target = tuple(pos[i] + axis[i] * FLUID_1 for i in range(3))
    return seat_body(_flowreg.build(), FLOWREG_TURN, station=(_flowreg.inlet(), target))


def _whole(bodies):
    out = None
    for s in bodies:
        b = box(s)
        out = b if out is None else out.add(b)
    return out


def place_base(bodies):
    """Turn the mated pair `BASE_YAW` about the vertical through their own combined centre, then
    seat the PAIR — centred on x = 0 and its front face on y = 0. Both moves are rigid and taken
    on the pair's own box, so the plane between them rides along and the crown does not change.

    A yaw about a centre is not a placement: the turn leaves the pair's front wherever its own
    width used to reach, which is not the front of the machine."""
    w = _whole(bodies)
    cx, cy = (w.xmin + w.xmax) / 2.0, (w.ymin + w.ymax) / 2.0
    axis = (cq.Vector(cx, cy, 0.0), cq.Vector(cx, cy, 1.0))
    turned = [s.rotate(*axis, BASE_YAW) for s in bodies]
    t = _whole(turned)
    step = cq.Vector(-(t.xmin + t.xmax) / 2.0, -t.ymin, 0.0)
    return [s.translate(step) for s in turned]


# --- The manifold, laid on their crown -------------------------------------
#
# `(x, y, z) → (−x, z, y)`: a quarter about X puts the pack's own front face — the plane the
# pump heads open on — face down, and a half about Z brings the pumps to the front of it and
# the valve decks behind them. X is negated by the pair, which the mirror does not notice.

def pose_manifold(shape):
    return shape.rotate(*X_AXIS, 90.0).rotate(*Z_AXIS, 180.0)


# What the pack actually sets down on is not a body at all — it is the four spine hairpins.
# The fold turned them onto the pack's own underside, and they hang past the pump-head faces,
# so THEY are the mating surface and the pump faces stand off the crown by whatever is left.
PUMP_FACE_Z = -ml.BARB_INSET                 # where that face lands once the pack is turned


def build_pack() -> cq.Assembly:
    """The bodies, with no box around them. `enclosure` sizes itself off this, so it
    cannot be in it."""
    a = cq.Assembly(name="front-half")
    shroud, cond = place_base([build_shroud(), build_condenser(build_shroud())])
    a.add(shroud, name="compressor-shroud", color=C_SHROUD)
    a.add(cond, name="condenser+fan", color=C_COND)

    posed = [(c.name, pose_manifold((c.obj.val() if hasattr(c.obj, "val") else c.obj).moved(
        cq.Location(c.loc.wrapped.Transformation()))), c.color) for c in ml.build_assembly().children]
    crown = max(box(shroud).zmax, box(cond).zmax)
    lift = crown - min(box(s).zmin for _n, s, _c in posed)
    stood = [(n, s.translate(cq.Vector(0.0, 0.0, lift)), c) for n, s, c in posed]
    for name, solid, color in stood:
        a.add(solid, name=name, color=color)
    # What the core butts is whatever the front half presents AT THE CORE'S OWN HEIGHT. The
    # source valves' quarter turns carry them aft over the core's crown, and a body standing
    # over it is not a body in its way — so the seam is measured against the bodies that reach
    # below that crown, and the ones above it are left to overhang.
    top = box(build_foam(0.0)).zmax
    aft = max([box(shroud).ymax, box(cond).ymax]
              + [box(s).ymax for _n, s, _c in stood if box(s).zmin < top])
    foam = build_foam(aft)
    a.add(foam, name="foam-assembly", color=C_FOAM)
    seaflo, seaflo_carry = build_seaflo(foam)
    a.add(seaflo, name="seaflo-pump", color=C_SEAFLO)
    chain, chain_carry = build_suction_chain(seaflo, seaflo_carry(_lines._pump.suction()))
    a.add(chain, name="suction-chain", color=C_SUCT)
    wall_seat = east_wall_seat(shroud, cond)
    psu, _psu_carry = build_psu(foam, wall_seat)
    a.add(psu, name="psu", color=C_PSU)
    pcba, _pcba_carry = build_pcba(foam, psu, wall_seat)
    a.add(pcba, name="pcba", color=C_PCBA)
    for name, solid, colour in build_stack(psu, wall_seat):
        a.add(solid, name=name, color=colour)
    asse, asse_carry = build_asse(foam, seaflo)
    a.add(asse, name="asse1022-assembly", color=C_ASSE)
    pan, _pan_carry = build_pan(foam, seaflo, asse_carry, west_interior_face(shroud, cond))
    a.add(pan, name="drip-pan", color=C_PAN)
    split, split_carry = build_split(asse_carry)
    a.add(split, name="water-split", color=C_SPLIT)
    flowreg, flowreg_carry = build_flowreg(split_carry)
    a.add(flowreg, name="flow-regulator", color=C_FLOWREG)

    # The runs between placed bodies. Their frames come off the poses above, so a waypoint
    # measured off a port moves when the body it is on moves.
    carries = {"seaflo-pump": seaflo_carry, "suction-chain": chain_carry,
               "asse1022-assembly": asse_carry, "water-split": split_carry,
               "flow-regulator": flowreg_carry}
    solids = {"seaflo-pump": seaflo, "suction-chain": chain,
              "asse1022-assembly": asse, "water-split": split,
              "flow-regulator": flowreg}
    runs = _lines.build_runs(solids, carries)
    for name, solid in _lines.tubes(runs):
        _ROUTED.add(name)
        a.add(solid, name=name, color=C_HOSE)
    a.runs = runs
    return a


def _solids(a: cq.Assembly):
    """The assembly's children as world-placed solids, keyed by name — the shape a box
    reads a pack in."""
    return {c.name: ((c.obj.val() if hasattr(c.obj, "val") else c.obj).moved(
        cq.Location(c.loc.wrapped.Transformation())), c.color) for c in a.children}


def pack(a: cq.Assembly = None) -> "_enc.Pack":
    """What the box is SIZED ON: the bodies that have to fit inside it.

    The funnel is not among them. It is seated IN the top wall — brim on the outer face,
    chute hanging through — so it stands above the ceiling the pack has to live under, and
    a box sized to contain it would be a box built around its own lid. It comes back as a
    station on that wall (`_seated`).

    The station fields left empty are the ones this pack has no body for: the drip tray's
    rails and slot, the mains inlet's bosses, the panel through-holes. Each arrives with
    the body it is for."""
    return _enc.Pack(placed=_solids(build_pack() if a is None else a))


# --- the box those bodies stand in, and what is seated in its walls ---------

WALL_COLORS = {"front-bottom": cq.Color(0.72, 0.74, 0.78, 0.30),
               "front-top": cq.Color(0.80, 0.82, 0.86, 0.30),
               "back-bottom": cq.Color(0.66, 0.68, 0.72, 0.30),
               "back-top": cq.Color(0.74, 0.76, 0.80, 0.30)}


def funnel_centre(box):
    """The funnel collar's centre in plan: (x, y).

    Centred across the box, and pushed as far FORWARD as the display housing allows: the
    top wall resumes at the facet's back plane, keeps one `enclosure.hopper_front_ledge` of
    itself there, and the collar's front edge stands one `hopper_funnel.brim_margin` behind
    that — the brim's own bearing. So the basin is the first thing behind the glass and the
    wall a deeper box adds runs behind it, not in front. Read off the box, because the box
    is a consequence of the pack and the facet's own depth; `enclosure._hopper_hole` asserts
    the frame this lands in."""
    ix0, ix1 = box.inner[0], box.inner[1]
    y_front = (_enc.facet_back_y(box.outer) + _enc.hopper_front_ledge + _funnel.brim_margin)
    return ((ix0 + ix1) / 2.0, y_front + _funnel.collar_d / 2.0)


def build_funnel(box):
    """The static funnel (`hopper_funnel.py`, its own frame: collar-centre origin, z 0 the
    brim underside) seated in the top-wall opening — turned `FUNNEL_ROT` about its own Z,
    then set at `funnel_centre` with that underside on the box's outer top. `enclosure.py`
    cuts the opening from the same centre, so funnel and hole cannot drift apart."""
    cx, cy = funnel_centre(box)
    return (cq.importers.importStep(str(FUNNEL_STEP)).val()
            .rotate(*Z_AXIS, FUNNEL_ROT)
            .translate(cq.Vector(cx, cy, box.outer[5])))


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
    return (body.rotate(cq.Vector(0, 0, 0), cq.Vector(*DISPLAY_TILT[0]), DISPLAY_TILT[1])
            .translate(seat_pt))


def _seated(box):
    """The box with every station its walls carry, seated. Each is read off the box itself,
    so the wall and the body it is cut for come out of one number."""
    return box._replace(funnel=funnel_centre(box))


def machine():
    """The pack, and the box around it. One build: the box is sized on the pack's bodies,
    and then carries the stations they seat in its walls."""
    a = build_pack()
    p = pack(a)
    return a, p, _seated(_enc.box_around(p))


def build_front_half() -> cq.Assembly:
    """The pack, what is seated in the walls, and the four printable pieces of the box."""
    a, _p, box = machine()
    a.add(build_funnel(box), name="hopper-funnel", color=C_FUNNEL)
    a.add(build_display(box), name="display", color=C_DISPLAY)
    for name, piece in _enc.build_pieces(box)[0].items():
        a.add(piece, name=f"enclosure-{name}", color=WALL_COLORS[name])
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
              "water-split", "flow-regulator"):
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


def main():
    a = build_front_half()
    out = _here.parent / "front-half.step"
    export_assembly(a, str(out))
    print(f"-> {out.name}")
    report(a)
    ml.render_elevations(out, xray="enclosure*")


if __name__ == "__main__":
    main()
