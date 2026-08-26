"""The enclosure assembly — the refrigeration stratum, the flavor manifold standing on it,
and the cold core behind the pair.

Four bodies, mated face to face with nothing between them:

    compressor          its shell's +X tangent against
    condenser+fan       turned onto it, off the floor on its own mount, and the pair yawed as
                        one by `BASE_YAW`
    manifold-layout     set down on the crown of those two, on the four SPINE HAIRPINS
    foam-assembly       at the machine's own `FOAM_YAW`, on the floor, its front face on the
                        plane the bodies ahead of it end at

The gaps along that chain are 0 by intent, and where a mating closes a leg of the refrigerant
loop no copper is drawn between the two bodies: the compressor is an oblong can whose two stubs
stand on its own tangent lines, and the condenser is an envelope whose serpentine headers are
re-dressed to reach whichever face is convenient, so such a joint crosses a plane its two bodies
already share and both of its stations are ONE POINT READ TWICE.

NEITHER OF THE TWO REACHES THE CORE. It is packed off the +Y wall of back-top (`rear_seam_clear`) rather
than butted against the stratum, so what stands between them is a LANE, and the loop's two legs
that cross it are cut and brazed copper `_lines` draws like any other run — the condenser's
liquid line straight across it on one column and one plane, the compressor's suction out of its
own west tangent and back across the lane on a diagonal. `JOINT_STATIONS` names the two mouths of
all three legs;
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
be a yaw. That yaw lays its discharge tangent EAST at the condenser, its suction tangent WEST at
the side wall, and its power box at the front.

The **condenser** turns a quarter about Z to bring its west face onto the compressor's tangent.
That carries its `AIRFLOW` axis with it — across the machine before, front-to-back after — so
the air crosses the cabinet the short way and the finstack faces the two side walls.

It is also the one body on this floor that does not stand on it. The block is a donor envelope
whose two Y faces are a recess between folded sheet flanges, and those four flanges are its
whole purchase — so the box takes them: a groove off the front wall at the fore pair, a bored
boss under each of the aft pair's own two holes. It stands `COND_LIFT` off the slab, which is
what the boss under its base flange needs to hold an insert and nothing else.

The **manifold** turns a quarter about X and a half about Z, which is the one pose that lays
its pump-head front face down. Its own +Z — the axis its two valve decks stack on — comes to
+Y, so the decks stand aft of the pumps rather than over them, and every mouth that faced the
back now faces up.

The storey it stands at is `PACK_CROWN`, a plane the machine states. What lands on that plane
is the fold's four spine hairpins — the lowest thing the pack has, put on its own underside at
the AFT end under the valve decks — so they are what the lift is measured to and the pump faces
stand clear of it by what they reach. THEY CARRY NOTHING. What holds this pack is a printed
seat under each of its ten valves, eight in the valve trays and three in the cap's own
cradles; its six tees and both pump heads hang on the tube between those valves, and the
`mounted` axis carries a row apiece for them.

Run it
------
    tools/cad-venv/bin/python hardware/manifold-layout/enclosure_assembly.py
"""

import collections
import math
import os
import sys
from pathlib import Path

import cadquery as cq
from OCP.BRepExtrema import BRepExtrema_DistShapeShape as _BRepDist

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts", _here.parent,
           _hw / "reference" / "compressor",
           _hw / "reference" / "condenser-block",
           _hw / "printed-parts" / "cadlib",
           _hw / "printed-parts" / "valve-seat",
           _hw / "printed-parts" / "zone-c" / "funnel",
           _hw / "reference" / "worm-clamp",
           _hw / "reference" / "jg-pp0408w",
           _hw / "reference" / "elbow-connector",
           _hw / "reference" / "funnel-drain-stub",
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
           _hw / "printed-parts" / "enclosure" / "asse-drip-pan",
           _hw / "reference" / "shutao-moisture-plate",
           _hw / "reference" / "mq6-gas-sensor",
           _hw / "reference" / "sf76e-thermal-fuse",
           _hw / "printed-parts" / "refrigeration" / "fuse-clamp",
           _hw / "reference" / "water-split",
           _hw / "reference" / "neofit-flow-control",
           _hw / "reference" / "beduan-solenoid",
           _hw / "reference" / "jg-bulkhead-union",
           _hw / "reference" / "iec-c14-inlet",
           _hw / "reference" / "neofit-bulkhead",
           _hw / "reference" / "gasher-check-valve",
           _hw / "reference" / "wr1110-regulator",
           _hw / "reference" / "digiten-flow-sensor",
           _hw / "cold-core-layout",
           _hw / "printed-parts" / "cold-core",
           _hw / "printed-parts" / "cold-core" / "copper-plugs",
           _hw / "printed-parts" / "cold-core" / "foam-assembly",
           _hw / "printed-parts" / "enclosure" / "bulkhead-ring",
           _hw / "printed-parts" / "faucet" / "tube-collar",
           _hw / "printed-parts" / "enclosure" / "nameplate",
           _hw / "printed-parts" / "enclosure" / "valve-tray",
           _hw / "printed-parts" / "enclosure" / "pump-tray",
           _hw / "printed-parts" / "enclosure" / "y-wall-of-back-top",
           _hw / "printed-parts" / "enclosure" / "display-cover",
           _hw / "printed-parts" / "enclosure" / "display-gasket",
           _hw / "printed-parts" / "enclosure" / "enclosure",
           _hw / "printed-parts" / "enclosure" / "ceiling-panel"):
    sys.path.insert(0, str(_p))
from _cadq_export import (SOLID_INDEX_SEP, export_assembly, export_dxf,  # noqa: E402
                          import_step)
import _boxes                                         # noqa: E402
import _clearing                                      # noqa: E402
import _lines                                         # noqa: E402
import _meshes                                        # noqa: E402
import _routing                                       # noqa: E402
import _overlap                                       # noqa: E402
# The import-time ledger. Every module below that states a bound about its own constants has
# already recorded into it by the time this import list is through, so `carry_stated_bounds`
# reads a complete list. Imported HERE, before them, so the name is bound whichever of them
# reaches for it first.
import _stated_bounds as _stated                      # noqa: E402
import compressor as _comp                            # noqa: E402
import condenser_block as _cond                       # noqa: E402
import copper_plugs as _plugs                         # noqa: E402
import display_cover as _cover                        # noqa: E402
import display_gasket as _dgasket                     # noqa: E402
import enclosure as _enc                              # noqa: E402
import reeding as _reeding                            # noqa: E402
import ceiling_panel as _cpanel                       # noqa: E402
import funnel as _funnel                       # noqa: E402
import funnel_drain_stub as _stub                     # noqa: E402
import elbow_connector as _elbow                      # noqa: E402
import valve_seat as _vseat                           # noqa: E402
import jg_pp0408w as _jgu                             # noqa: E402
import manifold_layout as ml                          # noqa: E402
import seaflo_suction_chain as _suct                  # noqa: E402
import seaflo_discharge_chain as _dis                 # noqa: E402
import waveshare_43b_display as _disp                 # noqa: E402
import asse1022_assembly as _asse                     # noqa: E402
import flare38_14ptc as _oad                          # noqa: E402
import asse_drip_pan as _pan                          # noqa: E402
import shutao_moisture_plate as _plate                # noqa: E402
import mq6_gas_sensor as _mq6                         # noqa: E402
import sf76e_thermal_fuse as _fuse                    # noqa: E402
import fuse_clamp as _clamp                           # noqa: E402
import foam_assembly as _foam                         # noqa: E402
# The bodies inside that foam. `foam_assembly` draws the envelope; this draws what the
# envelope is the outside of, in the envelope's own frame — see `core_bodies`.
import cold_core_assembly as _cca                     # noqa: E402
import _cold_core_interface as _cci                   # noqa: E402
import beduan_solenoid as _beduan                     # noqa: E402
import iec_c14_inlet as _c14                          # noqa: E402
import jg_bulkhead_union as _jg                       # noqa: E402
import bulkhead_ring as _ring                         # noqa: E402
# The same word and the same two filaments, on the customer's own tube outboard of the ring.
import tube_collar as _collar                         # noqa: E402
import nameplate as _np                               # noqa: E402
import valve_tray as _vtray                           # noqa: E402
import pump_tray as _tray                             # noqa: E402
# One table: what a colour MEANS on the rear face. The iso line-art paints its discs from it and
# the quick-start sheet aims its arrows by it, and the ring this module lays in the wall is the
# third reader. It reaches for `enclosure_assembly` inside its own functions and never at import,
# so the arrow points one way.
import _y_wall_dimensions as _rear                    # noqa: E402
import neofit_flow_control as _flowreg                # noqa: E402
import water_split as _split                          # noqa: E402
import neofit_bulkhead as _neofit                      # noqa: E402
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
# own cluster stands on rather than beside the main board the trunk leaves:
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
# THE LAST THREE ARE ONE BLOCK, aft on the west wall on one storey, at the same `wago_pitch`
# the five poles keep on the wall opposite. `wago-sensors` stands where its own cluster lands
# and the two reed nuts close up forward of it, which clears the whole band ahead for the tap
# water's split and the flavour tap under it. Every station clears the side walls' seam
# furniture (`enclosure.seam_bosses`) by the lever swing as well as the well, so a lug can be
# worked in place.
#
# THE STOREY IS THE COLD CORE'S OWN CROWN, and it is as low as this wall goes. What used to hold
# the block up was a tube: `fluid-28` ran the west outboard strip and its section fenced this
# band for the whole height it crossed at. That run now holds its union's own column three
# millimetres further inboard than these wells reach, so nothing of the plumbing is under them
# and the block comes down onto the one thing that is — the shell of the core itself. Re-read
# what is left by dropping a lug onto it:
#
#     w.travel("wago-reeds-b", (0, 0, -1))
CLUSTER_WAGOS = {
    "wago-mana": (+1, 113.0, 290.0, "420"),
    "wago-manb": (-1, 119.0, 281.0, "415"),
    "wago-reeds-b": (-1, 335.0 - 2.0 * _enc.wago_pitch, 270.0, "420"),
    "wago-reeds-a": (-1, 335.0 - 1.0 * _enc.wago_pitch, 270.0, "415"),
    "wago-sensors": (-1, 335.0, 270.0, "415"),
}

FOAM_STEP = _hw / "printed-parts" / "cold-core" / "foam-assembly" / "foam-assembly.step"
SEAFLO_STEP = _hw / "reference" / "seaflo-22-pump" / "seaflo-22-pump.step"
FUNNEL_STEP = _hw / "printed-parts" / "zone-c" / "funnel" / "funnel.step"

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
# one carries its discharge tangent to +X and its suction tangent to -X, the can's two flanks.
COMPRESSOR_YAW = 90.0
# The water pump lies flat on the core's crown. Its barbs are molded into the casting
# and leave its ±Y side faces, so this yaw lands them on the machine's ±X, and lays its
# 187 mm long axis front-to-back.
SEAFLO_YAW = 90.0
# The funnel's spout is on its collar centre, so a turn about Z picks nothing; 0 keeps
# the collar's own axes on the top wall's.
FUNNEL_ROT = 0.0

# THE MATERIAL IS THE COLOUR. `ledger/bom.md` is where each part is bought and what it says it is
# made of, and every part of one material takes one constant here.
#
# A COLOUR IS THREE COMPONENTS by the time it is drawn: `_mesh_payload` hands over the RGB a STEP
# carries and occt-import-js reads back the same three. The pack is read through X-RAY, a mode the
# viewer enters over the whole model (web/public/js/viewer/xray.js). These say what a part looks
# like with the lights on.
# The material colours are `hardware/scripts/_materials.py`, which the generators that cut these
# bodies' own STEPs read too.
from _materials import (C_AC_HUB, C_C14, C_COMP, C_COND, C_DIGITEN,  # noqa: E402
                        C_DISPLAY_GLASS, C_GND, C_MQ6, C_PCBA, C_PLATE,
                        C_PSU, C_RELAY, C_SEAFLO, C_STEEL_PLATE,
                        M_ALUMINIUM, M_BRASS, M_JG_BLACK_PP,
                        M_NEOFIT_ACETAL, M_PETG_BLACK, M_PETGF_BLACK, M_SILICONE_BLACK,
                        M_STAINLESS, M_TINNED_STEEL, M_TPU_BLACK)
# The refrigeration donor's own two. A hermetic compressor is a painted-steel can; the condenser is
# a plate-fin block, aluminium fins on a copper tube (`reference/ice-maker/README.md`), and it
# carries the fan on ONE body — so the fin face is what the pair is drawn as, the fan with it.
# The cold core is shells, caps and lids, and every one of them comes off the black spool.
C_FOAM = M_PETG_BLACK
# SEAFLO's own orange, which is the head casting — the whole outside of the pump but the white
# motor can behind it and the black feet under it.
# Cast platinum silicone, pigmented to hide concentrate staining.
C_FUNNEL = M_SILICONE_BLACK
# The funnel's own length of tube, off the roll `fluid-4` carries on below the union.
C_STUB = _routing.tube_color("fluid-4")
# The LOKMAN band closing that spout, 304 SS by its own listing (`reference/worm-clamp.MATERIAL`).
C_WORM = M_STAINLESS
# Each pump-port chain is a made-up run of SS adapter, check valve and reinforced PVC, and it is
# drawn as the metal that is most of it.
C_SUCT = M_STAINLESS
# The border over that glass, in the enclosure's own black stock.
C_COVER = M_PETG_BLACK
# And the soft ring under its lap, in the same TPU 90A as every other seal here.
C_DGASKET = M_TPU_BLACK
# `pcb/pcba/order.md` places the main board at "black mask / white silk".
# The Teyleten board itself, which is green; the SRD can standing on it is the blue, and the
# module is drawn as one envelope.
# WAGO 221 lever nuts, and the levers are the orange (`reference/wago-221`).
# The bolted fan of ring terminals that IS the ground bus. The smseace #4 rings are sold in one
# colour and it is red; the green in this corner is the bond wire, which is not drawn.
C_ASSE = M_BRASS
C_PAN = M_PETG_BLACK
# The Shutao module's conductivity plate — bare copper-clad, which its listing states as the brown
# half of "Brown and Blue"; the blue is the LM393 board, which stays out of the pan.
C_FUSE = M_TINNED_STEEL
C_CLAMP = M_PETG_BLACK
# The PP0208E union tee on the ASSE chain's outlet.
C_SPLIT = M_JG_BLACK_PP
# The ABCVU44-E flow-control bulkhead throttling the flavour leg.
C_FLOWREG = M_NEOFIT_ACETAL
# V-K is the same Beduan solenoid as the ten on the manifold, so it is the same body.
C_VK = ml.C_VALVE
# The four PP1208E unions the +Y wall of back-top clamps — the fittings the customer meets.
C_BULKHEAD = M_JG_BLACK_PP
# The ABU44-E the customer's CO2 tether pushes into, and the SS check one hop inboard of it.
C_CO2_INLET = M_NEOFIT_ACETAL
C_GASHER = M_STAINLESS
C_WR1110 = M_ALUMINIUM
# The meter's white rotor housing, the colour `reference/digiten-flow-sensor` draws it.
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
    the metal it is a hole in. `carry.where` is that same map for a whole SHAPE rather than a
    station: one placement, the two forms a caller can want.

    THE POSE IS HUNG ON THE SHAPE, NOT FOLDED INTO IT. `Shape.rotate` and `Shape.translate` go
    through `BRepBuilderAPI_Transform` and hand back a body whose coordinates ARE its pose;
    `moved` hangs a `TopLoc_Location` over the drawn geometry instead. `_meshes` names a body's
    kept triangles after the shape under that location, so a body that moves is re-seated by a
    matrix multiply rather than re-tessellated: of the pack's 137 solids, 122 keep their
    triangles across a move where 97 did when the pose reached the coordinates."""
    turn = cq.Location()
    for axis, deg in turns:
        step = cq.Location(cq.Vector(0, 0, 0), cq.Vector(*axis), deg)
        shape, turn = shape.moved(step), step * turn
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

    # THE SAME PLACEMENT, FOR A BODY INSTEAD OF A MOUTH. `cold-core-layout` draws the inside of
    # this `foam-assembly` in that body's own frame, and its solids stand in the machine under
    # this location.
    carry.where = cq.Location(shift) * turn
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


# The plane the compressor's plate stands on, stated the way `rear_plane_y` is, and level with
# the pump heads. Every reach on this can is on its −X flank (`compressor.process_tube`).
#
# IT STANDS FORE OF THE FRONT WALL'S OWN INTERIOR PLANE, and what holds it there is the far end
# of the machine: the −X core stop (`enclosure._core_stops`) is a floor block 39.9 mm tall
# standing `core_stop_web` ahead of the core's front face, and it already spends 6.1 mm of the
# 7 mm between this can and that core. The free lane is the 0.9 mm left over, so a can packed
# back to `front_plane_y` lands its aft-west corner in that block. The wall takes a relief
# across the can instead (`enclosure.fridge_relief`).
COMPRESSOR_FRONT = 11.0


def suction_lane_x() -> float:
    """The plane the compressor's WEST TANGENT stands on — the lane its suction leg needs off
    the −X wall's inner face.

    THE LEG IS WHY THIS BODY IS WHERE IT IS IN X. The suction fires west out of that tangent and
    turns aft in the lane, and a turn reaches one bend radius PAST the straight it leaves on — the
    arc's own centre stands square to the run, so the far side of it lies a radius further west
    than the tangent point does. `_lines.CU_SUCTION_LANE` is that reach in copper.

    Struck on the wall and not on the pair's combined box. Centred as a pair, the can's lane was
    whatever the condenser's width left over — so a condenser measured again moved the can, its
    four floor posts and this leg together, and narrowing the appliance took the lane away.

    IT IS THE FACE THAT IS THERE AT THIS HEIGHT. The can stands on the slab, under a Z seam, and
    a flank under a seam carries its lip's own wall down to the floor — so the lane is measured
    off `lip_face_x` and not `interior_x`, and the leg keeps its turn against the face the copper
    actually meets."""
    return _enc.lip_face_x()[0] + _lines.CU_SUCTION_LANE


def build_compressor():
    """The compressor as the machine turns it, its plate on the floor.

    `(placed, carry)` like every other seated body: its two loop stubs and its four mount
    holes are tables in its own frame and the carry is what puts them in the machine."""
    return seat_body(_comp.build(), (((0.0, 0.0, 1.0), COMPRESSOR_YAW),),
                     cx=0.0, y0=0.0, z0=0.0)


# THE PLANE THE FLAVOUR PACK SETS DOWN ON, stated the way `rear_plane_y` and `COMPRESSOR_FRONT`
# are. What it is worth is the AIR OVER THE COLD CORE'S CAP: the pack's two source valves take a
# quarter turn that carries them aft over that lid, and this plane is what holds them off it
# (`check_pack_over_core`). Struck instead on whatever body happens to stand tallest under it,
# the pack's whole storey would follow a donor block being calipered again.
PACK_CROWN = 151.0
# WHAT THE CONDENSER STANDS OFF THE SLAB, and it is the insert under its own base flange and
# nothing else. Both mount screws come DOWN the one line the donor drilled, so the lower one
# closes on a boss UNDER a sheet that would otherwise be lying on the floor. This is the depth
# that boss needs (`enclosure.cond_bore_depth`), so its bore ends on the slab's own inner face
# and the floor is never breached.
COND_LIFT = _enc.cond_bore_depth


def east_lane_free(cond) -> float:
    """How far the block may go east off the plane the mating puts it on, read off the placed
    body and the wall it is going toward.

    THE SEAM'S FURNITURE IS NOT THE FENCE HERE, and saying so is the whole of this. The front
    column's seam furniture on a flank is the hooked rail, and the rail lives in the seam's
    own storey — `z_seam` up to the rim — while this block's crown comes up UNDER that mouth.
    A body under the storey is beside nothing, and charging it the rail's whole reach would be
    charging it for a lane it never enters.

    WHAT IS THERE IS ITS OWN AFT MOUNT. The block hangs off a fin fused to the wall's inner face
    (`condenser_mount`, `enclosure._cond_mount`), standing one `enclosure.cond_mount_clear` off
    the block's east flank — so the lane the block may take is the lane that leaves the fin one
    printable `enclosure.wall` of section. The block answers to the thing that holds it.

    AND THAT FIN IS THE WALL. The block stands wholly under the front Z seam, and a flank under a
    seam carries its lip's own wall down to the slab (`enclosure._lip_underwall`) — `2 * wall` of
    it. So the section the fin needs is section the wall already has: what the lane leaves is one
    `enclosure.cond_mount_clear` of air off `front_bottom_flank_face`, and the fingers root on
    the flank itself. The two readings come to the same plane, so the block RIDES the thickening
    — it stands off whatever section that flank carries, into the lane it has always had between
    its own west flank and the compressor's tangent. What crosses the lane behind it is
    `_lines._refrig_2`, which leaves and enters on its ports\' own normals and turns between
    them."""
    b = box(cond)
    storey_z = _enc.z_seam
    # The block's own front face is what goes in: the fore end of the run comes back struck on
    # it and is not read, this block being cradled on the front wall already. What is read is
    # the aft end, which the box states about itself.
    band_aft = _enc.front_band_free_y(b.ymin)[1]
    if b.zmax > storey_z + 1e-9 or b.ymax > band_aft + 1e-9:
        raise ValueError(
            f"the condenser reaches y {b.ymax:g} and z {b.zmax:g}, out of the corner of the ±X "
            f"band the front column leaves empty — under z {storey_z:g}, forward of y "
            f"{band_aft:g}. A block that stands up into the slide's storey answers to the "
            f"rail's whole reach and not to its own fin, so it stands off "
            f"`enclosure.side_band_inset` instead.")
    return (_enc.front_bottom_flank_face()[1] - _enc.cond_mount_clear) - b.xmax


def slide_east(solid, carry, dx: float):
    """The block and its carry, moved `dx` east. A station rides it, the way it rides a seat."""
    moved = solid.translate(cq.Vector(dx, 0.0, 0.0))

    def carried(station):
        (px, py, pz), axis = carry(station)
        return ((px + dx, py, pz), axis)

    return moved, carried


def build_condenser(comp):
    """The block turned a quarter about Z, which brings the WEST face the mating names round
    onto the compressor's own tangent, and stood off the same floor on its own mount.

    The two are struck on the same centre, so the shallower of the pair stands off the plane the
    core butts at both ends and its liquid line reaches the evaporator as drawn copper."""
    c = _cond.build()
    c = c.toCompound() if hasattr(c, "toCompound") else c
    return seat_body(c, (((0.0, 0.0, 1.0), 90.0),),
                     cx=0.0, y0=box(comp).ymax, z0=COND_LIFT)


# The turn that lays the cutoff's seating plane on a face looking down +X. Its own frame runs
# the case along X with Z = 0 the generatrix it lies on, and Y up. Two quarters carry that:
# the one about X stands the part up — its own Y onto world Z, where the leaves have to press a
# gap that is a Z gap in the machine — and the one about Z swings the seating plane round onto
# the +X normal, which leaves the case's axis running fore and aft along the flank's own
# `compressor.POWER_Y`.
FUSE_TURN = (((1.0, 0.0, 0.0), 90.0), ((0.0, 0.0, 1.0), 90.0))
FUSE_FACE_NORMAL = (1.0, 0.0, 0.0)


def power_face_station(comp_carry):
    """The centre of the compressor's power face in the machine, for a body laid flat on it.

    Both bodies that go there — the cutoff and the clamp that holds it — are drawn in ONE frame
    with Z = 0 on that face, and `FUSE_TURN` is the pair of quarters that lays that plane on it.
    So both read this one station, and a yaw that swung the face off +X is caught once here
    rather than seating one of them on a wall and the other in the open."""
    (pos, normal) = comp_carry(_comp.power_face())
    got = tuple(round(v, 9) for v in normal)
    if got != FUSE_FACE_NORMAL:
        raise ValueError(
            f"the compressor's power face looks {got} in the machine and the cutoff's quarters "
            f"lay its contact line on {FUSE_FACE_NORMAL} — the base has been turned out "
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
    # The case has to land ON the cover, both ways: a case longer than the flank is deep, or
    # taller than the box stands, hangs off the face it is there to read.
    note_room("thermal-fuse", "cover either side of the case",
              0.0, (_comp.POWER_Y - _fuse.LENGTH) / 2.0)
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


def build_foam(front_y: float):
    """The cold core at the machine's own `FOAM_YAW` and on the machine's own floor, its front
    face on `front_y`. Its native box hangs 20 mm below its origin, so the floor is the box's own
    bottom and not that origin.

    Returns `(placed, carry)` like every other seated body, so the cap's conduit mouths ride the
    placement — a line reaching one is drawn to where the bore actually comes out."""
    f = import_step(str(FOAM_STEP)).val()
    return seat_body(f, (((0.0, 0.0, 1.0), FOAM_YAW),), seat="foam-assembly",
                     cx=0.0, y0=front_y, z0=0.0)


#: THE SUB-ASSEMBLY THE CORE'S BODIES STAND IN. The machine exports them under this name and
#: the separator a solid index already uses, so `cold-core/evap-coil` is the coil of the core
#: and `cold-core/evap-coil/2` is that body's second solid. Nothing in the tree has to be told:
#: `bodyName` in the viewer, `_SOLID_INDEX_RE` in `_cadq_export` and `_LEAF_NAME` in
#: `render_scenes` all take an index off by asking for DIGITS, so what is left is a name that
#: says what holds it. That is the whole of the containment — one string, read by everything
#: that already reads names, and carried alike by both routes the viewer loads a model through.
CORE = "cold-core"

#: The core's own bodies are the same for every machine that seats the core alike, and building
#: them costs about six seconds, so one placement is built once.
_CORE_BODIES: dict = {}


def core_bodies(carry):
    """Every body the cold core places, stood where this machine stands the core.

    `cold_core_assembly` builds in `foam-assembly`'s own frame — the same frame `build_foam`
    imports the envelope in — and `carry.where` is where the machine stands that frame, so
    moving each body by it is the whole of the transform.

    IT IS THE CARRY AND NEVER THE CORE'S OWN BOX. Re-seating the stack the way `build_foam`
    seats the envelope would shift it: the core measures 285.0 x 184.2 where the foam measures
    283.0 x 181.0, and every clearance in the pack is struck off the foam's faces."""
    key = repr(carry.where.toTuple())
    if key not in _CORE_BODIES:
        _CORE_BODIES[key] = [(f"{CORE}{SOLID_INDEX_SEP}{c.name}",
                              c.obj.moved(carry.where), c.color)
                             for c in _cca.build_assembly().children]
    return _CORE_BODIES[key]


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
# board reads gas, and the gate that enforces it is on the main board rather than in firmware
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
# THE CARD LIES ALONG THE STRIP, its plane parallel to the flank: the long side runs fore-aft
# down the strip, the short side is the height, and the board's own thickness is the whole of
# what it spends across the strip. THE CAN LOOKS WEST, into a well cut back through
# front-bottom's own flank section (`enclosure._front_bottom_flank_skin`), and bottoms on
# `lip_face_x` — so the wall is still the datum in X and what stands the card off it is the
# can's own height. THE HEADER LOOKS EAST, out of the strip and into the bay the front assembly
# opens onto, so the loom lands on it out of the room rather than reaching round the board to a
# face held against a wall.
#
# AND THAT IS WHAT THE CRADLE IS FOR. A card standing ACROSS the strip has to be held by rails
# reaching horizontally off the wall, printed over air. A card lying ALONG it is held by two
# POSTS STANDING ON THE SLAB, one at each end of its long run, and every layer of them lands on
# the one below (`enclosure._west_cradle`). The card drops in from above between them.
#
# The turn is two quarters: −90° about X stands the card up on its long side with the can facing
# aft, then +90° about Z swings that long side into the strip and the can into the wall.
MQ6_STEP = _hw / "reference" / "mq6-gas-sensor" / "mq6-gas-sensor.step"
MQ6_TURN = ((X_AXIS[1].toTuple(), -90.0), (Z_AXIS[1].toTuple(), 90.0))
# The card's own fore edge, stated: the long side runs aft off it. Nothing on this flank is a
# remainder off the card — the cradle's posts stop under the grille's own band, so the vent
# neither steps around them nor pays for them — and the card owns its Y the way every stated
# station here does.
MQ6_Y0 = 38.3


def build_mq6(comp, cond):
    """The MQ-6 along the −X strip, as low as the card stands.

    WEST until the CAN bottoms in its well, not on the boss plane every body on the other flank
    stands on — nothing bolts this card down, it drops into a slot printed on the wall
    (`enclosure._west_cradle`) and the wall is what the far end of it lands on. That face is
    `lip_face_x` and not `interior_x`: the card stands under a Z seam, and a flank under a seam
    carries its lip's own wall down to the slab, `2 * wall` of it. The well through the flank's
    own extra section is what lets the can reach that plane.

    FORE on its own stated `MQ6_Y0`, which is the card's fore edge — the long side runs aft off
    it. The grille costs this station nothing and is costed nothing by it: the cradle's posts
    stop at the card's crown, under the band the intake is pierced over (`flank-vent-mullions`),
    and the card's loom dresses off its east face into the open bay. So the station is the card's
    own fact, not a remainder off the seam machinery or the vent's.

    LOW on the slab the compressor stands on, one post section up — the shoulder at the foot of
    each groove is what the card lands on, and the whole of what lifts it. The mesh comes out
    under the power box's floor, so the layer reaches this board before it reaches the one
    ignition source in the compartment."""
    body = import_step(str(MQ6_STEP)).val()
    return seat_body(body, MQ6_TURN, seat="mq6-sensor",
                     x0=_enc.lip_face_x()[0], y0=MQ6_Y0,
                     z0=box(comp).zmin + _enc.mq6_rail_wall)


def mq6_cradle(carry):
    """The strip's card-slot station, `(x, y, z)` — the card's own mid-plane, and its centre
    along the strip and in height. Nothing else, because nothing else varies: the slot is one
    board's envelope and one slip fit, and both the cradle and the flank's well read those off
    the reference module itself.

    STRUCK ON `mq6_gas_sensor.card_plane` and not on the placed box, because the box is the pins
    and the can as well, and the two are not the same depth — its centre stands west of the card
    they hang off. The slot cannot land anywhere but on the card."""
    pos = carry(_mq6.card_plane())[0]
    return ((pos[0], pos[1], pos[2]),)


# --- the bounds the machine states about itself -----------------------------
#
# Several constructions in this module measure a bound the MACHINE STATES rather than a bound
# its own construction meets: every printed valve cradle stands under its valve, every leg of
# the refrigerant loop closes, the vent's drip lands on the ASSE drip pan's flat
# floor, the pan's west lip lands inside the −X wall, the power column stands in the depth the
# +X wall runs free, and a body seated through a wall stands under the box's own ceiling.
# A printed part may state one about itself too: `asse_drip_pan.check_plate` measures the pan's
# flat floor against the moisture plate it receives, and `build_pan` enters that reading here.
# `enclosure` states more of them about the box it draws and keeps
# its own ledger, which `carry_enclosure_bounds` reads into this one. Every one of them can be
# opened by a move made somewhere else in the pack.
#
# A THIRD GROUP IS SETTLED BEFORE ANY OF THIS RUNS. `manifold_layout`, `funnel` and the
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


# --- the flavour manifold's valve trays ------------------------------------
#
# TWO PLATES, ONE PER VALVE DECK (`valve_tray`). The fold stands the manifold's eight
# non-cap valves on two planes, four to a plane, and each plate reaches the box's two side
# walls carrying one `valve_seat` per valve — four bosses, sockets the corner posts press into.
#
# NOTHING BELOW IS A STATION. A valve's plane, the columns its seats stand on and the plate's
# own extent are all read off the placed valves at every build: `manifold_layout` folds the pack
# and this module stands it on the base's crown, so where a deck lands is that stack's
# arithmetic. A tray table would be a second machine's.
#   Which face of a valve is its mounting plane is read off ITS OWN COIL. The Beduan's coil
# stands on the body's crown, so the axis from the valve's centre to its coil's IS the valve's
# own +Z, and the plane the four posts stand on is the box face at the other end of it.
#
# How far off contact a valve on a tray may read. It is the same figure every seat on this card
# is held to — the ASSE anchor's, the flow-meter anchors' and both ribs' — and what it measures
# gap is taken across, so a valve resting on its boss tops reads just under it.
TRAY_SEAT_SLIP = 0.2


def _valve_up(placed: dict, name: str) -> tuple:
    """One valve's own +Z in world, as `(axis, sign)` — the way its coil stands off it."""
    coil = name.replace("valve-", "coil-")
    if coil not in placed:
        raise KeyError(
            f"{name} is placed and {coil} is not, so nothing says which way it faces — a "
            f"Beduan's coil stands on its crown and that is what tells a tray which of the "
            f"body's six faces its four posts stand on.")
    vb, cb = box(placed[name]), box(placed[coil])
    d = [(cb.xmin + cb.xmax - vb.xmin - vb.xmax) / 2.0,
         (cb.ymin + cb.ymax - vb.ymin - vb.ymax) / 2.0,
         (cb.zmin + cb.zmax - vb.zmin - vb.zmax) / 2.0]
    axis = max(range(3), key=lambda i: abs(d[i]))
    return axis, (1.0 if d[axis] > 0.0 else -1.0)


def _bodies(placed: dict) -> dict:
    """`placed` reaches these readers in either of the two shapes the tree hands round —
    `{name: solid}` from the stand, and the pack's own `{name: (solid, colour)}`. Both mean
    the same bodies, so take the solid either way rather than making every caller remember
    which one it is holding."""
    return {n: (b[0] if isinstance(b, tuple) else b) for n, b in placed.items()}


def valve_tray_decks(placed: dict) -> dict:
    """The valves a tray holds, grouped by the plane they stand on.

    `name -> (axis, sign, plane, ((valve, u, v), …))` — which world axis the valves' own +Z
    runs on, which way it points, the world coordinate of their shared mounting plane, and each
    valve's centre in the plate's two in-plane axes.

    The cap's three valves are not here: the cold core's lid prints their seats
    (`_cold_core_interface.cap_cradles`), and a body is held once."""
    placed = _bodies(placed)
    groups = collections.defaultdict(list)
    for name in placed:
        if not name.startswith("valve-v-") or name in _cci.cap_cradles:
            continue
        axis, sign = _valve_up(placed, name)
        b = box(placed[name])
        centre = ((b.xmin + b.xmax) / 2.0, (b.ymin + b.ymax) / 2.0, (b.zmin + b.zmax) / 2.0)
        # The mounting plane is the box face the coil stands away from.
        plane = ([b.xmin, b.ymin, b.zmin] if sign > 0 else [b.xmax, b.ymax, b.zmax])[axis]
        groups[(axis, sign, round(plane, 6))].append((name, centre))
    out = {}
    for (axis, sign, plane), members in sorted(groups.items()):
        # The plate's own two axes: X across the machine wherever it can be, and whichever of
        # the remaining two is not the valves' own +Z.
        across = 0 if axis != 0 else 1
        along = next(i for i in range(3) if i not in (axis, across))
        seats = tuple((n, c[across], c[along]) for n, c in sorted(members))
        out[tray_name(axis, sign, plane, out)] = (axis, sign, plane, seats)
    return out


def tray_name(axis: int, sign: float, plane: float, taken: dict) -> str:
    """The body name one tray goes into the assembly under — where in the machine the plate
    itself stands, which is opposite the way its valves' coils point."""
    where = {(0, 1.0): "west", (0, -1.0): "east", (1, 1.0): "fore", (1, -1.0): "aft",
             (2, 1.0): "bottom", (2, -1.0): "top"}[(axis, sign)]
    name = f"valve-tray-{where}"
    return name if name not in taken else f"{name}-{plane:.0f}"


def valve_tray_stations(placed: dict) -> tuple:
    """Every deck as `enclosure.Box.valve_trays` — `(plane, sign, ((x, z), …))` per tray.

    The world Y a deck's valves stand their mounting faces on, which way their own +Z runs off
    it, and each valve's footprint centre. This is the whole of what the wall is handed: the
    plate's extent is the seats' own, and its thickness, margin and seat height are
    `valve_tray`'s.

    EVERY DECK IS STRUCK THE SAME AND NO VALVE MOVES. A valve seats its whole post in its
    socket and lands its body on its plate's face, on this deck as on every other — the
    release moves the TEE, and the millimetre it takes is absorbed by the tube stub between
    them, not by anything the plate does."""
    out = []
    for _name, (axis, sign, plane, seats) in sorted(valve_tray_decks(placed).items()):
        if axis != 1:
            raise ValueError(
                f"a valve deck stands its valves' own +Z on {'xyz'[axis]} and "
                f"`enclosure._valve_trays` fuses a plate across the box's width on a Y plane — "
                f"a deck on another axis needs the builder to learn it, not this table.")
        out.append((plane, sign,
                    tuple((round(u, 6), round(v, 6)) for _n, u, v in seats)))
    return tuple(out)


def valve_tray_plans(a=None) -> dict:
    """`name -> (width, seats)` in each plate's own frame — what `valve_tray` draws.

    The seats are centred on the plate: across, on the box's own centreline, because the plate
    runs wall to wall; along, on the row the valves stand in.

    `a` is a machine somebody already stood; without one this stands the pack itself. The
    valves are read out of it by name, so a whole assembly answers what a bare pack does."""
    a = build_pack() if a is None else a
    placed = {n: s for n, (s, _c) in _solids(a).items()}
    x0, x1 = _enc.interior_x()
    out = {}
    for name, (_axis, _sign, _plane, seats) in valve_tray_decks(placed).items():
        mid_v = (min(v for _n, _u, v in seats) + max(v for _n, _u, v in seats)) / 2.0
        out[name] = (x1 - x0, tuple((round(u - (x0 + x1) / 2.0, 6), round(v - mid_v, 6))
                                    for _n, u, v in seats))
    return out


def check_valve_trays_hold(pieces: dict, placed: dict) -> Bound:
    """Whether every valve on a tray is standing in the piece that carries its seats.

    Read as the seat is: a valve's four corner posts hang in four sockets and its round body
    boss lands on the plate's face, so the valve and the printed piece TOUCH. Anything else is
    a plate drawn beside a valve rather than under it. EVERY VALVE ON THE MACHINE IS HELD THIS
    ONE WAY — the release moves tees, not valves — so one figure is the right figure here and
    a second reading would be a distinction the machine does not make.

    The detail is the table, so a deck that has moved prints what it now is."""
    rows, worst = [], 0.0
    solids = [p.val() if hasattr(p, "val") else p for p in pieces.values()]
    for name, (_axis, sign, plane, seats) in sorted(valve_tray_decks(placed).items()):
        for valve, _u, _v in seats:
            gap = min(_clearing.gap(placed[valve], piece, 1.0) for piece in solids)
            worst = max(worst, gap)
            rows.append((name, valve, plane, sign, gap))
    bad = [r for r in rows if r[4] > TRAY_SEAT_SLIP]
    return record_bound(Bound(
        "valve-trays-hold", "Every valve on a printed valve tray is standing in its seats", not bad,
        f"{len(rows) - len(bad)}/{len(rows)} valves seated, furthest off {worst:.3f} mm",
        f"every valve within {TRAY_SEAT_SLIP:g} mm of the plate under it",
        [f"{n:18} {v:12} y-plane {p:8.3f} {'+' if s > 0 else '-'}Z   off {g:.4f}"
         for n, v, p, s, g in rows]))


# --- the flavour manifold's pump trays --------------------------------------
#
# ONE PLATE PER KAMOER (`pump_tray`). A tray lies flat on the +Z face of its pump's head with
# that head's own rear boss standing up through the octagon cut in it, and runs from the pump's
# axis to the front wall it is printed off.
#
# NOTHING BELOW IS A STATION. Which way a pump stands and where the face its tray lies on is are
# read off the placed bodies at every build, the way a valve deck's plane is.
#   Which face of a pump its tray takes is read off ITS OWN MOTOR CAN. The can stands on the
# boss and the boss on the head, so the axis from the head's centre to the can's IS the pump's
# depth axis, and the head's face at the far end of it is the face the plate lies on.
#
# How far off contact a pump under its tray may read — the same figure every seat on this card
# is held to, the ASSE anchor's, the flow-meter anchors' and both valve trays'.
PUMP_TRAY_SLIP = 0.2


def _pump_up(placed: dict, head: str) -> tuple:
    """One pump's own depth axis in world, as `(axis, sign)` — the way its motor can stands off
    its head."""
    can = head.replace("-head", "-motor")
    if can not in placed:
        raise KeyError(
            f"{head} is placed and {can} is not, so nothing says which way it faces — a Kamoer's "
            f"can stands on the boss behind its head, and that is what tells a tray which of the "
            f"head's six faces it lies on.")
    hb, cb = box(placed[head]), box(placed[can])
    d = [(cb.xmin + cb.xmax - hb.xmin - hb.xmax) / 2.0,
         (cb.ymin + cb.ymax - hb.ymin - hb.ymax) / 2.0,
         (cb.zmin + cb.zmax - hb.zmin - hb.zmax) / 2.0]
    axis = max(range(3), key=lambda i: abs(d[i]))
    return axis, (1.0 if d[axis] > 0.0 else -1.0)


def pump_tray_seats(placed: dict) -> dict:
    """The trays the box stands, `head -> (axis, sign, centre)`.

    `centre` is the world point the pump's own axis meets the face its tray lies on: the head's
    centre in the two axes across the pump, and the head's own face in the third."""
    out = {}
    for head in sorted(placed):
        if not (head.startswith("pump-") and head.endswith("-head")):
            continue
        axis, sign = _pump_up(placed, head)
        b = box(placed[head])
        centre = [(b.xmin + b.xmax) / 2.0, (b.ymin + b.ymax) / 2.0, (b.zmin + b.zmax) / 2.0]
        centre[axis] = ([b.xmax, b.ymax, b.zmax] if sign > 0
                        else [b.xmin, b.ymin, b.zmin])[axis]
        out[head] = (axis, sign, tuple(round(c, 6) for c in centre))
    return out


def pump_tray_stations(placed: dict) -> tuple:
    """Every pump as `enclosure.Box.pump_trays` — one world `centre` each.

    This is the whole of what the wall is handed: how far a plate runs to the wall is the box's
    own figure, and its depth, its margin and its zip tie band are `pump_tray`'s."""
    out = []
    for head, (axis, sign, centre) in sorted(pump_tray_seats(placed).items()):
        if (axis, sign) != (2, 1.0):
            raise ValueError(
                f"{head} stands its can on {'+' if sign > 0 else '-'}{'xyz'[axis]} and "
                f"`enclosure.build_pump_cartridge` lays a plate on a Z face — a pump on another "
                f"axis "
                f"needs the builder to learn it, not this table.")
        out.append(centre)
    return tuple(out)


def pump_tray_plans(a=None, shell=None) -> dict:
    """`head -> root` — how far each tray runs off its pump's axis to the wall it stands on,
    which is what `pump_tray` draws one from.

    `a` and `shell` are a machine and its box somebody already stood; without them this stands
    one. The heads are read out by name, so a whole assembly answers what `machine` does."""
    if a is None or shell is None:
        a, _p, shell = machine()
    placed = {n: s for n, (s, _c) in _solids(a).items()}
    # A tray roots on the pump cartridge face's own pump relief, whose floor is the plane the
    # wrap rule struck (`enclosure.pump_relief_floor`), not on the interior wall plane.
    return {head: round(centre[1] - _enc.pump_relief_floor, 6)
            for head, (_axis, _sign, centre) in pump_tray_seats(placed).items()}


def check_cap_laps_bracket(pieces: dict, placed: dict) -> Bound:
    """Whether the cap has material under every pump's bracket, on the three sides that close.

    The bracket steadies a pump: `bracket_w` across against a head of `head_w`, sitting in the
    plane the cap parts from the pump cartridge on. What it bears on is the cap's own top face, in
    the annulus between the head's void and the bracket's edge. `kamoer_kphm400` states that
    lip and draws none of it, so this reads the printed piece rather than the pump: one probe
    per side, a `wall` deep under the split, and a side with no material under it is a corner
    of the bracket hanging over the head's own opening.

    THE AFT SIDE IS OPEN AT THIS PLANE AND IT IS NOT READ. `enclosure.build_pump_cap` gives up
    its aft face from the barbs' own level to the split, so a made-up tube can come down it as
    the cap rises; the split is where the bracket sits, so the lap there is gone by that
    decision and reading for it would be reading for the thing given up. WHAT CARRIES A PUMP
    IS NOT THIS LAP EITHER: the head stands on the four flank seats `pump_tray.head_room` cuts
    for it, and the lap only keeps the part square on them — three sides do that, and the
    fourth was 0.525 mm wide."""
    cap = pieces.get("pump-cap")
    if cap is None:
        return record_bound(Bound(
            "pump-cap-laps-bracket", "The cap has material under every pump's bracket", True,
            "no cap in this box", "material under all four sides of each bracket", []))
    solid = cap.val() if hasattr(cap, "val") else cap
    stations = tuple(c for _h, (_a, _s, c) in sorted(pump_tray_seats(placed).items()))
    split = _enc.cap_split_z(stations)
    inner = _tray.head_half + _enc.cap_pump_air
    outer = _tray.bracket_half
    rows, worst = [], None
    for cx, cy, _cz in stations:
        for name, box in (
                ("+X", (cx + inner, cx + outer, cy - inner, cy + inner)),
                ("-X", (cx - outer, cx - inner, cy - inner, cy + inner)),
                ("-Y", (cx - inner, cx + inner, cy - outer, cy - inner))):
            probe = _enc._ybox(box[0], box[1], box[2], box[3], split - _enc.wall, split)
            vol = solid.intersect(probe).Volume()
            worst = vol if worst is None else min(worst, vol)
            rows.append((f"({cx:+.1f}) {name}", vol))
    bad = [r for r in rows if r[1] <= 0.0]
    return record_bound(Bound(
        "pump-cap-laps-bracket", "The cap has material under every pump's bracket", not bad,
        f"{len(rows) - len(bad)}/{len(rows)} closed sides land, least {worst:.1f} mm³",
        "material under the three closed sides of each bracket (the aft face is open)",
        [f"{who}: the cap has {vol:.1f} mm³ under this side of the bracket — the lip that "
         f"carries the pump hangs over the head's own opening here" for who, vol in bad]))


def check_cap_passes_tubes(pieces: dict, placed: dict, plate: dict) -> Bound:
    """Whether each barb tube leaves the cap through the opening rather than through material.

    `enclosure.build_pump_cap` opens its aft face as one slot over each head and bores nothing
    for the four tubes. THAT IS A CLAIM ABOUT THE BARB PITCH AND NOTHING ELSE HERE READS IT:
    the tubes are stationed off the placed pumps, while the opening starts at `head_half` and
    carries `cap_tube_relief` past the room at both edges. A wider pitch or a fatter tube can
    therefore walk into the web without another card saying so. A bore struck to catch it
    would lap that web by a fraction of its radius and feather the section to nothing at the
    two levels it grazed, which is why there is no bore.

    Read as the tube's own outer wall against the opening's edge, per barb, on the axis the
    opening is struck on."""
    cap = pieces.get("pump-cap")
    if cap is None:
        return record_bound(Bound(
            "cap-passes-tubes", "Each barb tube leaves the cap through its opening", True,
            "no cap in this box", "every tube inside the opening it leaves by", []))
    edge = _enc.cap_slot_half
    r = ml.TUBE_D / 2.0
    rows, worst = [], None
    for cx, _cy, _cz in (c for _h, (_a, _s, c) in sorted(pump_tray_seats(placed).items())):
        for hx, _hz in plate["holes"]:
            if (hx > 0.0) != (cx > 0.0):
                continue
            air = edge - (abs(hx - cx) + r)
            worst = air if worst is None else min(worst, air)
            rows.append((f"({cx:+.1f}) barb x {hx:+.2f}", air))
    bad = [row for row in rows if row[1] < _enc.cap_tube_relief - 1e-9]
    return record_bound(Bound(
        "cap-passes-tubes", "Each barb tube leaves the cap through its opening", not bad,
        f"{len(rows) - len(bad)}/{len(rows)} clear, least {worst:.3f} mm off the edge",
        f"at least {_enc.cap_tube_relief:g} mm round every Ø{ml.TUBE_D:g} tube at the "
        "opening's two outer edges",
        [f"{who}: the tube has {air:.2f} mm to the opening's edge, under the "
         f"{_enc.cap_tube_relief:g} mm printed running clearance — carry the slot's edge "
         "farther without opening the flank seat" for who, air in bad]))


def check_trays_hold(pieces: dict, placed: dict) -> Bound:
    """Whether every pump is standing in the tray its head's face lies against.

    Read as the tray is: the plate lands on the head's +Z face all the way round the boss it
    takes, so the pump and the printed piece TOUCH. Anything else is a plate drawn beside a pump
    rather than on it."""
    rows, worst = [], 0.0
    solids = [p.val() if hasattr(p, "val") else p for p in pieces.values()]
    for head, (_axis, _sign, centre) in sorted(pump_tray_seats(placed).items()):
        gap = min(_clearing.gap(placed[head], piece, 1.0) for piece in solids)
        worst = max(worst, gap)
        rows.append((head, centre, gap))
    bad = [r for r in rows if r[2] > PUMP_TRAY_SLIP]
    return record_bound(Bound(
        "trays-hold", "Every pump is standing in its printed tray", not bad,
        f"{len(rows) - len(bad)}/{len(rows)} pumps seated, furthest off {worst:.3f} mm",
        f"every pump within {PUMP_TRAY_SLIP:g} mm of the plate on it",
        [f"{h:14} axis ({c[0]:8.3f}, {c[1]:8.3f}) face z {c[2]:8.3f}   off {g:.4f}"
         for h, c, g in rows]))


# --- the collet plate --------------------------------------------------------
#
# THE PUMP CARTRIDGE'S RELEASE, and the one piece of this machine that is steel. A flat of 1/8"
# 304 stands one rest gap fore of the four anchor tees' branch collets, wall to wall, standing
# in the slot `enclosure._plate_slot` cuts clean through the bay floor — the slot takes it fore
# and aft over the floor's whole section, and its own TOP EDGE lands wall to wall on the
# wall over it (`enclosure._plate_cap`), which is what stops it going in. IT GOES IN THROUGH FRONT-TOP'S OWN Z− FACE, the
# seam plane the piece beds on, before the front column closes. Over `enclosure.seam_cap_z` its
# ends run to `PLATE_END_AIR` off the side walls; under that plane they step in to
# `enclosure.plate_step_in`, the band the Z seam's joint takes down each flank. Four holes pass
# the barb tubes and nothing wider. Pull the pump cartridge and the gripped tubes drag the tees
# forward
# until each collet's nose lands on the steel — the body keeps coming, the nose is held,
# the grip opens, and the tubes draw out through the holes they entered by. Pushing the
# pump cartridge home threads them back into the same collets, the cap's own aft face landing on
# the plate's fore face, the tees braced by the deck lattice their own butted valves hang
# them from. The user's two hands are the whole mechanism: one pulls the pump cartridge, the
# other braces the box, and the box carries the brace to this plate through the floor.
PLATE_T = 3.175              # 1/8" 304, waterjet from `collet-plate.dxf`
PLATE_REST_GAP = 1.5         # collet nose air off the plate's aft face, pump cartridge seated
PLATE_HOLE_D = 8.0           # passes the tube, stops the nose
COLLET_NOSE_R = 5.715        # the release nose's rim, measured off tee-connector.step
PLATE_END_AIR = 0.3          # each end off the side wall
TEE_WALL_BORE_SLIP = 0.25    # a bore's air on the collar's own radius — a running fit, not a grip
TEE_WALL_BODY_AIR = 1.0      # the wall's aft face off the tee's own body, at FULL travel
TEE_WALL_ARM_SLIP = 0.10     # the aft bore's air on the ARM — what leaves the collar a ledge


def collet_plate_spec(mcarry, tray_stations) -> dict:
    """The plate as the four branch collets and the walls place it — faces, band, ends,
    holes — the one figure the steel, the bay floor's slot and the waterjet's own outline
    all read.

    ITS Z BAND IS STRUCK ON THE HOLES. The bottom is the seam plane — the foot fills the slot
    to its Z− mouth and stops there; the top is then whatever puts the four collet holes in
    the middle of the band, which is the only place a hole is as far from one edge as from the
    other. Over that top the guides' heads stand one `slide_slip` clear
    (`enclosure._plate_fore_guides`).

    ACROSS, IT IS TWO WIDTHS. Over `seam_cap_z` its ends stand `PLATE_END_AIR` off the side
    walls and the outline is whole between them — the one thing that ever stood proud of the
    floor down these flanks was front-bottom's Z-seam lip, and it is given up over this whole
    run (`enclosure._flank_lip_drop`). Under that plane each end steps in to
    `enclosure.plate_step_in`, because there the steel is standing in the Z seam's own storey
    and that band down each flank belongs to the joint.

    AND THAT IS EVERY NOTCH IN IT. What stops the steel is its own TOP EDGE, landing wall to
    wall on `enclosure._plate_cap`'s land — so nothing down here has to be a stop, the slot
    through the bay floor is one width, and the waterjet cuts two steps and four holes."""
    holes, faces = [], []
    for t in sorted(ml.BARB_OF):
        (px, py, pz), _axis = mcarry(ml.branch_port(t))
        holes.append((round(px, 6), round(pz, 6)))
        faces.append(py)
    if max(faces) - min(faces) > 1e-6:
        raise ValueError(
            f"the four branch collets stand on {len(set(round(f, 4) for f in faces))} planes "
            f"({sorted(set(round(f, 4) for f in faces))}) — one plate presses one plane")
    aft = faces[0] - PLATE_REST_GAP
    z0 = _enc.z_seam
    hole_z = holes[0][1]
    if max(abs(hz - hole_z) for _hx, hz in holes) > 1e-6:
        raise ValueError(
            f"the four branch collets stand on {len(set(round(hz, 4) for _hx, hz in holes))} "
            f"heights ({sorted(set(round(hz, 4) for _hx, hz in holes))}) — one band centres "
            f"one row")
    x1 = _enc.interior_x()[1] - PLATE_END_AIR
    z1 = round(2.0 * hole_z - z0, 6)
    # AND THE WALL BEHIND IT, off the same four collets — the steel's aft face IS the wall's
    # fore face, so the two are one figure and cannot be struck apart. What the wall reads is
    # the arm the tee carries through it. `CAP_NEAR` is where the collar the bore journals on
    # begins, so the wall must reach past that at rest or a bore holds nothing — and
    # `collar_in_y` is that station in the world, which is where the BORE STEPS. Fore of it the
    # bore takes the collar, which is what it journals; aft of it the bore takes the ARM alone,
    # `ARM_R` being what the tee stands between its collar and its body. The collar cannot pass
    # into the smaller of the two, so it lands on the ring between them, and that ring is the
    # tee's AFT stop. It costs the release nothing, the release travelling the other way. It is
    # the stop this machine has never had: a tube pushed into a branch collet pushes the tee
    # AFT, and until now nothing took that push but friction.
    #
    # THE WALL DOES NOT RESTRAIN THE TEE ALONG ITS OWN AXIS, and its aft face is struck so
    # that it cannot. A tee travels WITHIN this wall: the collar runs in its bore and the
    # STEEL in front is the only thing that stops it, which is the one surface meant to.
    # `HALF_W` is the run's radius, so `BRANCH_REACH - HALF_W` off the collet face is where
    # the arm ends and the body it grows out of begins — the first thing on a tee that a wall
    # behind it could ever land on. Take the wall back from there by the whole stroke AND
    # `TEE_WALL_BODY_AIR` on top, so at full travel there is still air between the tee's
    # shoulder and this face rather than a kiss. Depth past that point is not room the wall
    # may take: it is the tee's, and a wall standing in it is a wall the tee lands on before
    # its own grip has opened.
    #
    # `stroke` IS THE TRAVEL THE RELEASE ASKS OF A TEE: its rest gap off the steel, plus how
    # far its collet sleeve moves before the grip opens. That second figure is NOT on the
    # tee's STEP — a harvested solid carries the sleeve where it was when it was scanned and
    # has no way to say how far it slides — so it is read from the one member of this collet
    # family measured in hand, `jg_pp0408w.COLLET_TRAVEL`, off the caliper record at
    # `off-the-shelf-parts/john-guest-union/`: extended 41.80, pressed 39.13, half the
    # difference each end. `stroke_ceiling` is the same sum against the sleeve's own proud
    # length instead, which is as far as it could POSSIBLY be pressed — a sleeve cannot travel
    # further than it stands out — so the two bracket the answer and `collet-travel-fits`
    # holds one under the other.
    tee = ml.tee
    branch_face = faces[0]
    stroke = PLATE_REST_GAP
    step_x = round(_enc.interior_x()[1] - _enc.plate_step_in(), 6)
    return {"holes": tuple(sorted(holes)),
            "aft_y": round(aft, 6), "fore_y": round(aft - PLATE_T, 6),
            "z0": round(z0, 6), "z1": z1,
            "x0": round(-x1, 6), "x1": round(x1, 6), "hole_d": PLATE_HOLE_D,
            "step_x0": -step_x, "step_x1": step_x,
            "step_z": round(_enc.seam_cap_z(), 6),
            "seat_z": round(_enc.bay_floor_z(tray_stations)[1], 6),
            "wall_aft_y": round(branch_face + tee.BRANCH_REACH - tee.HALF_W
                                - stroke - TEE_WALL_BODY_AIR, 6),
            "collar_in_y": round(branch_face + tee.BRANCH_REACH - tee.CAP_NEAR, 6),
            "collar_r": tee.BARREL_R,
            "bore_r": round(tee.BARREL_R + TEE_WALL_BORE_SLIP, 6),
            "arm_bore_r": round(tee.ARM_R + TEE_WALL_ARM_SLIP / 2.0, 6),
            "stroke": round(stroke, 6),
            "stroke_ceiling": round(PLATE_REST_GAP + tee.COLLET_PROUD, 6)}


def build_collet_plate(spec):
    """The steel itself: `enclosure.plate_outline` stood up on edge, and four tube bores."""
    plate = _enc._xz_prism(spec["fore_y"], spec["aft_y"], _enc.plate_outline(spec))
    for hx, hz in spec["holes"]:
        plate = plate.cut(cq.Solid.makeCylinder(
            spec["hole_d"] / 2.0, PLATE_T + 2.0,
            cq.Vector(hx, spec["fore_y"] - 1.0, hz), cq.Vector(0, 1, 0)))
    return plate


def export_collet_plate_dxf(spec, path):
    """The waterjet's own file: outline and four tube holes, flat — the
    section of a unit slab cut the way the steel is, so the loops cannot disagree with the solid.

    Written through `export_dxf`, so the header's save-time stamps and GUIDs come out
    canonical and a rebuild that moves no dimension leaves the file alone."""
    flat = (cq.Workplane("XY")
            .polyline(list(_enc.plate_outline(spec))).close().extrude(1.0))
    for hx, hz in spec["holes"]:
        flat = flat.cut(cq.Workplane("XY").workplane(offset=-0.5)
                        .center(hx, hz).circle(spec["hole_d"] / 2.0).extrude(2.0))
    export_dxf(flat.section(0.5), str(path))


def check_collet_plate(spec, mcarry) -> None:
    """The plate against the joints it works: the nose it must catch, the tube it must
    pass, the berth the standoff opened for it between the barbs and the collets, and where
    its four holes fall in the band the floor and the rim leave it."""
    hole_r = spec["hole_d"] / 2.0
    mid = (spec["z0"] + spec["z1"]) / 2.0
    hole_z = spec["holes"][0][1]
    off = abs(hole_z - mid)
    record_bound(Bound(
        "plate-holes-centred", "The collet holes stand centred in the plate's band",
        off <= 1e-6,
        f"holes at z {hole_z:g}, band {spec['z0']:g}..{spec['z1']:g}, off {off:.3f} mm",
        "the row on the band's own middle",
        ([] if off <= 1e-6 else [
            f"a hole {off:.2f} mm off centre has {hole_z - spec['z0']:.2f} mm of steel under "
            f"it and {spec['z1'] - hole_z:.2f} over — the nose is caught by whichever edge "
            f"is nearer, and the plate bows about the other"])))
    record_bound(Bound(
        "plate-stops-collets", "The plate's holes catch the collet noses",
        hole_r + 1.0 <= COLLET_NOSE_R + 1e-9,
        f"hole r {hole_r:g} against a nose of r {COLLET_NOSE_R:g}",
        "one millimetre of annulus under the nose, all round",
        ([] if hole_r + 1.0 <= COLLET_NOSE_R + 1e-9 else [
            f"a Ø{spec['hole_d']:g} hole leaves {COLLET_NOSE_R - hole_r:.2f} mm of nose on "
            f"the steel — the collet follows its tube into the hole and nothing releases"])))
    record_bound(Bound(
        "plate-passes-tubes", "The plate's holes pass the barb tubes",
        hole_r >= ml.TUBE_D / 2.0 + 0.5,
        f"hole r {hole_r:g} over a Ø{ml.TUBE_D:g} tube",
        "half a millimetre of air round the tube",
        ([] if hole_r >= ml.TUBE_D / 2.0 + 0.5 else [
            f"a Ø{spec['hole_d']:g} hole closes on the Ø{ml.TUBE_D:g} tube it must let "
            f"slide — the plate would carry the tube instead of releasing it"])))
    barb = max(mcarry((ml.barb_station(t), (0.0, 0.0, 1.0)))[0][1] for t in ml.BARB_OF)
    air = spec["fore_y"] - barb
    record_bound(Bound(
        "plate-berth", "The standoff holds the plate off the barbs",
        air >= 0.7 - 1e-9,
        f"{air:.2f} mm between the barb plane and the steel",
        "at least 0.7 mm — `manifold_layout.BARB_STANDOFF` is the whole berth",
        ([] if air >= 0.7 - 1e-9 else [
            f"the steel's fore face stands {air:.2f} mm off the barb plane — the standoff "
            f"is spent before the plate and its rest gap fit in it. Raise "
            f"`BARB_STANDOFF`, or thin the plate"])))


EXTRUSION_W = 0.42           # the outer-wall bead the box's own profile lays
                             # (`printed-parts/enclosure/enclosure/print-log.md`)


def check_panel_web() -> Bound:
    """The wall left between a valve seat's sockets and the port channel that runs past them.

    A WALL THINNER THAN ONE EXTRUSION IS NOT A THIN WALL, IT IS NOTHING. A web the model draws
    at a quarter of the bead this piece is printed with is a web the slicer lays no material in
    at all: the socket opens into the channel and the post loses its inboard flank
    over that stretch. The solid says the post is surrounded; the bed says otherwise, and no
    clash check, no volume and no `post-engagement` reading can tell the difference — they all
    measure the model, and the model is right.

    THE TWO COME CLOSE BY CONSTRUCTION, so this is worth reading rather than assuming. A
    socket's inner edge stands `corner_inset - socket_radius` off the plate's centreline and
    the channel stands `port_radius + PORT_SLIP` — a tenth of a millimetre apart if they ever
    met at the same height. What keeps them apart is height alone: the channel's widest station
    is above the sockets' mouths. Anything that drags it down into their band spends that tenth
    at once, and nothing about a solid says it has been spent.

    Read off the cutters rather than the piece: they are what the plate is hollowed by, so the
    distance between them IS the web, and reading it here does not depend on finding the right
    two faces in a solid that has been through thirty other booleans.

    AND IT IS THE ONLY THING ON THIS CARD HELD TO WHAT THE MACHINE CAN LAY. Several bounds here
    keep a minimum wall — `plug-web` at 1 mm, `port-field-web` at a rim's own width, and
    `port-pocket-floor` at `enclosure.wall` — but every one of those figures is the design's,
    chosen so a feature reads right and stands up. `EXTRUSION_W` is not: it is the printer's,
    and it is the width below which a wall is not thin but absent. A solid states material at
    any width whatever, so nothing that reads the model can tell the two apart; only a figure
    from outside the model can.

    AND A NAME IS NOT A NOZZLE. `copper_plugs.min_printable_thickness` is 1.0 and its bound
    says PRINTABLE, but no nozzle stands behind it — `ledger/machine-time.md` names one for
    two of its four print groups, and the group the plug stack prints in is not one of them.
    It is not wrong today, because 1.0 is over one bead on anything this shop runs; it is
    unheld, which is a different thing and reads more confident for saying printable. The
    figure to copy is `faucet_shell.display_line_width` — 0.62, its own part's bead, on the
    0.4 group `machine-time.md` does name."""
    a = _vseat.build_sockets()
    b = _vtray.build_port_channel(_vtray.height() + 2.0)
    a = a.val() if hasattr(a, "val") else a
    b = b.val() if hasattr(b, "val") else b
    d = _BRepDist(a.wrapped, b.wrapped)
    worst = d.Value() if d.IsDone() else 0.0
    rows = [("seat", worst)]
    bad = [r for r in rows if r[1] < EXTRUSION_W - 1e-9]
    return record_bound(Bound(
        "tray-web", "A valve seat's sockets keep a printable wall to the port channel",
        not bad,
        f"{worst:.4f} mm of wall, {100.0 * worst / EXTRUSION_W:.0f}% of an extrusion",
        f"at least one {EXTRUSION_W:g} mm extrusion of wall between socket and channel",
        [f"socket to port channel   {w:.4f} mm   {100.0 * w / EXTRUSION_W:.0f}% of an "
         f"extrusion of {EXTRUSION_W:g}" for _lab, w in rows]))


POST_GRIP_FLOOR = 3.0        # of a post inside its plate at rest — see `check_post_engagement`


def check_post_engagement(pieces, placed, spec) -> Bound:
    """How much of each valve's corner post is standing INSIDE its plate, at rest.

    `valve-trays-hold` reads whether a valve is near the plate that holds it. This reads how much
    of it is HELD, which is a different quantity and the one `valve_seat`'s own headline turns
    on: the posts in their sockets are the whole of the retention. A post engaged half a
    millimetre sits at exactly the same radial clearance from its socket wall as one engaged
    six, so proximity cannot tell them apart and nothing else on this card was looking.

    Measured rather than computed: a sleeve around each post's own axis, just outside its
    socket AND NO LONGER THAN THE POST, intersected with the printed piece. What comes back is
    the stretch of that post's length the plate actually surrounds — so a socket shortened by a port channel crossing it,
    or by any later cut, reads short here even though the arithmetic still says six."""
    solids = [q.val() if hasattr(q, "val") else q for q in pieces.values()]
    inset, r = _vseat.corner_inset, _vseat.socket_radius
    rows, bad = [], []
    for _name, (_axis, sign, plane, seats) in sorted(valve_tray_decks(placed).items()):
        for valve, u, v in seats:
            worst = None
            for du in (-inset, inset):
                for dv in (-inset, inset):
                    # CLIPPED TO THE POST'S OWN LENGTH, and that clip is the whole reading.
                    # A sleeve run further than the post measures how long the SOCKET is,
                    # which is a fact about the plate and not about what holds the valve —
                    # the two differ by whatever the plate's face stands off the mounting
                    # plane, and the longer number is the flattering one. From the mounting
                    # plane, `seat_top_z` along the valve's own +Z.
                    base = cq.Vector(u + du, plane, v + dv)
                    axis = cq.Vector(0, sign, 0)
                    sleeve = (cq.Solid.makeCylinder(r + 0.8, _vseat.seat_top_z, base, axis)
                              .cut(cq.Solid.makeCylinder(r + 0.02, _vseat.seat_top_z,
                                                         base, axis)))
                    held = 0.0
                    for solid in solids:
                        try:
                            bb = sleeve.intersect(solid).BoundingBox()
                            held = max(held, bb.ylen)
                        except Exception:
                            pass
                    worst = held if worst is None else min(worst, held)
            rows.append((valve, worst))
            if worst < POST_GRIP_FLOOR - 1e-6:
                bad.append(valve)
    return record_bound(Bound(
        "post-engagement", "Every valve's posts stand in their plate at rest", not bad,
        f"{len(rows) - len(bad)}/{len(rows)} valves gripped, least "
        f"{min((w for _v, w in rows), default=0.0):.3f} mm",
        f"at least {POST_GRIP_FLOOR:g} mm of every post inside its plate with the valve at rest",
        [f"{v:12} {w:6.3f} mm of {_vseat.seat_top_z:g} in the plate" for v, w in rows]))


def check_release_travel(pieces, placed, spec) -> Bound:
    """Whether the pump cartridge's release has ROOM TO HAPPEN.

    EVERY OTHER BOUND ON THIS CARD READS WHERE A BODY STANDS. This one reads whether one can
    MOVE, which is a different question, and the only one that can fail on a machine whose
    every body is standing exactly where it should. The release is a MOTION: the gripped
    tubes drag each anchor tee forward until its collet nose lands on the steel, and then the
    body keeps coming while the nose is held, which is what opens the grip. `spec["stroke"]`
    is the whole of that travel — the rest gap off the plate plus the sleeve's own measured
    slide. A tee that cannot make it does not let its tube go, and nothing about the seated
    machine looks wrong.

    THE VALVE BUTTED ON THE RUN DOES NOT TRAVEL AND IS NOT READ HERE. What gives is the tube
    stub between the two collets, which bends over the millimetre the tee takes — so a valve
    stays seated on its own plate exactly as every other valve does, and only the tee is
    offered the stroke.

    THAT THE STUB BENDS IS STATED, NOT DERIVED, AND NOTHING IN THIS TREE CAN CHECK IT. Every
    body in the model is rigid: there is no compliance anywhere in it, so a chain of reasoning
    over it can only ever conclude that something rigid has to move, and reading `BUTT` as 0
    says the two collet faces meet with no tube between them — which is a fact about a gap and
    not about whether the tube INSIDE them can articulate. The mechanism here is the account of
    someone who has handled the fittings. It is the one premise under the release that no bound
    on this card reaches, and anything downstream describing the stub rests on it rather than
    on geometry.

    Each body is offered the stroke, fore, against every printed piece — AND THAT SCOPE IS A
    DISCOUNT THIS BOUND DEPENDS ON. A released body is already touching its own tube at rest,
    by construction: the barb tube the collet grips stands half a millimetre fore of the tee
    and travels out with it. A sweep counting every placed body would meet the workpiece
    before it met anything actually in the way, and report the joint as the obstruction. What
    can stop a tee is the box, so the box is what this reads. Widening it means first saying
    what a joint is."""
    stroke = spec["stroke"]
    solids = [q.val() if hasattr(q, "val") else q for q in pieces.values()]
    rows, bad = [], []
    for tee in sorted(ml.BARB_OF):
        name = ml.body_name(tee)
        if name not in placed:
            continue
        moved = placed[name].translate(cq.Vector(0.0, -stroke, 0.0))
        worst, into = 0.0, ""
        for piece, solid in zip(pieces, solids):
            try:
                vol = moved.intersect(solid).Volume()
            except Exception:
                vol = 0.0
            if vol > worst:
                worst, into = vol, piece
        rows.append((tee, name, worst, into))
        if worst > 1e-6:
            bad.append((tee, name, worst, into))
    return record_bound(Bound(
        "release-travel", "Every anchor tee can make the release stroke",
        not bad,
        f"{len(rows) - len(bad)}/{len(rows)} tees clear {stroke:.3f} mm fore",
        f"every tee the release moves free over its whole {stroke:.3f} mm",
        [f"{t:5} {b:14} {'CLEAR' if v <= 1e-6 else f'{v:10.1f} mm3 into {i}'}"
         for t, b, v, i in rows]))


def check_insertion_backing(pieces, placed, spec) -> Bound:
    """Whether an anchor tee is BACKED against the push that seats a tube in it.

    THE SIBLING OF `release-travel`, AND IT READS THE OTHER DIRECTION. That bound offers each
    tee the stroke fore, because fore is where the release goes. But a barb tube is pushed INTO
    a branch collet, and the tube comes from the pump ahead of it, so seating one pushes the tee
    AFT. A tee free that way does not seat its tube — it simply moves out of the tube's path,
    and the tube stops short of the fitting's own tube stop with nothing anywhere saying so.
    (The tee is a harvested solid and states no insertion depth of its own; the figure named
    here is the concept, not another fitting's constant.)

    What backs it is the step in the wall's own bore (`enclosure._tee_bore`): fore of the
    collar's rest station the bore takes the collar, aft of it only the narrower arm, and the
    collar lands on the ring between. So this bound wants each tee STOPPED rather than free —
    a reading of zero here is the pass, and travel is the failure. It is the one bound on this
    card whose success is an interference."""
    probe = spec["stroke"]
    solids = {n: (q.val() if hasattr(q, "val") else q) for n, q in pieces.items()}
    rows, bad = [], []
    for tee in sorted(ml.BARB_OF):
        name = ml.body_name(tee)
        if name not in placed:
            continue
        moved = placed[name].translate(cq.Vector(0.0, probe, 0.0))
        worst, into = 0.0, ""
        for piece, solid in solids.items():
            try:
                vol = moved.intersect(solid).Volume()
            except Exception:
                vol = 0.0
            if vol > worst:
                worst, into = vol, piece
        rows.append((tee, name, worst, into))
        if worst <= 1e-6:
            bad.append(tee)
    return record_bound(Bound(
        "insertion-backing", "An anchor tee is backed against the push that seats its tube",
        not bad,
        f"{len(rows) - len(bad)}/{len(rows)} tees stopped going aft",
        "every anchor tee landing on printed material before it can travel aft",
        [f"{t:5} {n:14} " + (f"backed by {i}, {v:9.1f} mm3 at {probe:.3f} mm"
                             if v > 1e-6 else
                             "FREE — nothing takes the tube's own insertion push")
         for t, n, v, i in rows]))


def check_bay_floor(pieces, shell) -> Bound:
    """Whether the bay floor lies on front-top's own bed plane and stops the collet plate.

    Two readings on the one solid. FIRST, the bed: a slab one probe over the seam mouth,
    across the floor's whole plan LESS the rail channels' own lane
    (`enclosure._z_rail_channels` — the section the slide's lane is cut to, which this
    floor's flank bands stop short of) and LESS the plate's own slot
    (`enclosure._plate_slot` — the opening the steel comes in by, which is a gap in the
    first layers and not a hole over them), is the piece's first layers, and full means
    the floor lies on the bed rather than hanging in the piece. SECOND, the land: a slab
    one probe over the steel's own top edge, across the whole width, is `enclosure._plate_cap`
    — the flat the plate comes up onto and stops on, which is the only stop in this joint."""
    spec = shell.collet_plate
    z_bed, top = _enc.bay_floor_z(shell.pump_trays)
    probe = 0.5
    ft = pieces["front-top"]
    ft = ft.val() if hasattr(ft, "val") else ft
    berth = _enc._z_rail_channels(shell.inner, shell.y_joint, shell.splits[0],
                                  "front", spec, shell.vent_chase).fuse(
        _enc._plate_slot(shell.inner, spec, top + 1.0))
    lx0, lx1 = _enc.lip_face_x()
    aft = spec["aft_y"] + _enc.plate_slot_slip + _enc.wall
    rows = [("bed", _enc._ybox(lx0, lx1, _enc.front_plane_y, aft, z_bed, z_bed + probe)
             .cut(berth))]
    # AND THE LAND THE STEEL STOPS ON, one storey up: `enclosure._plate_cap`'s flat off the
    # tee wall's fore face, wall to wall, with the guides' two heads carrying the same plane
    # out to the side walls. It is the plate's Z datum, so it is read across the whole width
    # rather than at the two ends the old shoulders bore on.
    land = spec["aft_y"] - _enc.plate_cap_land
    rows.append(("land", _enc._ybox(spec["x0"], spec["x1"], land, spec["aft_y"],
                                    spec["z1"], spec["z1"] + probe)))
    rows = [(n, plug.intersect(ft).Volume() / plug.Volume()) for n, plug in rows]
    worst = min(g for _n, g in rows)
    ok = worst >= 1.0 - 1e-6
    return record_bound(Bound(
        "bay-floor-bedded", "The bay floor lies on the bed and seats the collet plate", ok,
        ", ".join(f"{n} {g * 100:.1f}% solid" for n, g in rows),
        f"the floor whole on the seam plane {z_bed:g} and the cap's land whole over the "
        f"steel's top edge at {spec['z1']:g}",
        ([] if ok else
         [f"{n}: {g * 100:.1f}% of its plan" for n, g in rows if g < 1.0 - 1e-6]
         + ["the floor is this piece's first layers and the cap's land is the one thing the "
            "steel stops on — a hole in the first is material the print has to bridge, a "
            f"hole in the second is a plate that goes in further than its holes allow. The "
            f"floor runs {z_bed:g} to {top:g}"])))


def check_column_face(pieces, shell) -> Bound:
    """Whether the front columns' face across the bay is the turn it is drawn as, and whether
    the side wall behind it is still there.

    A WALL THAT VANISHES MAKES NOTHING INTERSECT. Every other reading on this card asks
    whether two things collide, and taking material AWAY passes all of them: the piece pairs
    still read 0.0 mm3, the meshes still come back watertight, the bed still fits. So this
    reads presence, not clearance, at the one station where the column's face is thinnest —
    the plane the flank opening ends on, `front_plane_y + enclosure._column_along()`, which
    the turn is tangent to.

    Two readings on the one solid. FIRST, THE WALL: a probe slab just forward of that plane,
    from the exterior face in to where the turn lands, is that piece's section between this
    corner and the outside of the machine, and full means it stands. SECOND, THE LANDING: the
    inboard-most material in the same slab is where the face is, and a turn of `column_round`
    tangent to the plane sweeps `sqrt(2 * column_round * probe)` inboard over the slab's own
    depth — so the expected station is the landing plus that sweep, and it is arithmetic off
    the radius rather than a figure fitted to what came out. A face that stops short of its
    landing reads inboard of it; a face swung from anywhere but the jamb does not obey the
    sweep at all."""
    bay = shell.pump_bay
    if not bay:
        return None
    bx0, bx1, bay_top = bay
    r = _enc.column_round
    y_land = _enc.front_plane_y + _enc._column_along()
    # BETWEEN the storey's own ends and not on them. The seam's cap closes this corner one
    # `wall` under the opening's floor and the bay's soffit closes it at the top, and both
    # stand full to the jamb — so a slab taken ON either plane reads the thing on the far side
    # of it rather than the post, and one micron of that reaches the whole reading.
    edge = 1.0
    z0 = _enc.seam_cap_z() + edge
    z1 = bay_top - edge
    probe = 0.05
    sweep = math.sqrt(2.0 * r * probe)
    ft = pieces["front-top"]
    ft = ft.val() if hasattr(ft, "val") else ft
    rows = []
    for label, bx, ex, sx in (("X-", bx0, shell.outer[0], -1.0),
                              ("X+", bx1, shell.outer[1], +1.0)):
        land = bx + sx * r                       # where the turn meets the opening's end plane
        keep = _enc._ybox(min(land, ex), max(land, ex), y_land - probe, y_land, z0, z1)
        full = keep.intersect(ft).Volume() / keep.Volume()
        lane = _enc._ybox(min(land, bx), max(land, bx), y_land - probe, y_land, z0, z1)
        got = lane.intersect(ft)
        face = (got.BoundingBox().xmax if sx < 0 else got.BoundingBox().xmin) \
            if got.Volume() > 1e-9 else land
        rows.append((label, full, face, land - sx * sweep))
    slip = 0.2
    ok = all(f >= 1.0 - 1e-6 and abs(face - want) <= slip for _l, f, face, want in rows)
    return record_bound(Bound(
        "column-face-lands", "The column's turn lands on the flank opening, and the wall "
        "behind it stands", ok,
        "; ".join(f"{l} {f * 100:.1f}% solid, face at {face:.3f}" for l, f, face, _w in rows),
        f"solid to the landing, face within {slip:g} mm of "
        f"{rows[0][3]:.3f} / {rows[1][3]:.3f}",
        ([] if ok else
         [f"{l}: the wall outboard of the landing is {f * 100:.1f}% solid — material taken "
          f"from it collides with nothing and shows on no other reading"
          for l, f, _face, _w in rows if f < 1.0 - 1e-6]
         + [f"{l}: the face stands at {face:.3f} where a turn of {r:g} tangent to "
            f"y={y_land:g} puts it at {want:.3f}, {abs(face - want):.3f} off"
            for l, _f, face, want in rows if abs(face - want) > slip])))


def check_cap_stop(pieces, spec) -> Bound:
    """Whether the cap's aft face actually lands on the collet plate's fore face.

    A STOP THAT DOES NOT TOUCH WHAT IT STOPS IS NOT A STOP. The cap is the piece whose
    storey stands against the steel, and the face it presents is the whole of the stop, so
    this reads both halves of that: the AREA standing against the plate's own band one
    `cap_kiss` off its fore face, and that the kiss itself is air — a face through the steel
    is no better than one that misses it."""
    cart = pieces["pump-cap"]
    cart = cart.val() if hasattr(cart, "val") else cart
    probe = 0.4
    band = (spec["x0"], spec["x1"], spec["z0"], spec["z1"])
    land = _enc._ybox(band[0], band[1], spec["fore_y"] - _enc.cap_kiss - probe,
                      spec["fore_y"] - _enc.cap_kiss, band[2], band[3])
    kiss = _enc._ybox(band[0], band[1], spec["fore_y"] - _enc.cap_kiss,
                      spec["fore_y"], band[2], band[3])
    area = land.intersect(cart).Volume() / probe
    bite = kiss.intersect(cart).Volume()
    ok = area > 1e-6 and bite <= 1e-6
    return record_bound(Bound(
        "pump-cap-stops-on-plate", "The cap's aft face lands on the collet plate", ok,
        f"{area:.1f} mm² on the steel, {bite:.3f} mm³ inside the kiss",
        f"the cap's face on the plate's and `cap_kiss` {_enc.cap_kiss:g} mm of air at it",
        ([] if ok else
         ([f"no pad stands against the plate's band z {spec['z0']:g}..{spec['z1']:g} — the "
           f"pump cartridge has no aft stop against the steel and nothing but the anchor tees "
           f"limits how far it pushes home"] if area <= 1e-6 else [])
         + ([f"{bite:.2f} mm³ of the pump cartridge stands inside the kiss — the pad is through "
             f"the steel, not on it"] if bite > 1e-6 else []))))


def check_head_sweep(solids: dict, pieces) -> Bound:
    """Whether each pump head can leave through the front of the box.

    The bay's sill is the floor's top and the head bottoms one millimetre over it, so what
    is read here is not a clearance at rest — `pack-closes` has that — but the SWEEP: the
    head's own box carried fore to the exterior, against the piece it has to pass through."""
    ft = pieces["front-top"]
    ft = ft.val() if hasattr(ft, "val") else ft
    rows = []
    for n, s in sorted(solids.items()):
        if not (n.startswith("pump-") and n.endswith("-head")):
            continue
        b = box(s)
        sweep = _enc._ybox(b.xmin, b.xmax, _enc.front_plane_y - _enc.front_wall, b.ymax,
                           b.zmin, b.zmax)
        rows.append((n, sweep.intersect(ft).Volume()))
    worst = max([v for _n, v in rows], default=0.0)
    ok = worst <= 1e-3
    return record_bound(Bound(
        "heads-sweep-out", "Every pump head sweeps out through the bay", ok,
        f"{len(rows)} heads, most in the way {worst:.1f} mm³",
        "nothing of front-top in a head's path to the front",
        ([] if ok else
         [f"{n} meets {v:.1f} mm³ of front-top on its way out" for n, v in rows if v > 1e-3]
         + ["the bay's sill is the bay floor's top, and the floor's top is the plane the "
            "pump cartridge's own pump reliefs floor on. A head in the way is a head hanging "
            "under that plane — raise it, or thin the floor"])))


def check_pump_cartridge_sweep(pieces) -> Bound:
    """Whether the two printed pump cartridge pieces can pass bodily through the front mouth.

    A PUMP-HEAD SWEEP IS NOT A DRAWER SWEEP. The head is smaller than the filled block that
    carries it, and a mouth can clear both heads while a reveal, rounded plan corner or jamb
    catches the block behind the face. Sweep each piece's complete bounding envelope from its
    installed aft face through the exterior plane. This is intentionally conservative: every
    bit of air cut inside the block is treated as material, because the opening owes clearance
    to the block's outer envelope rather than to its pump voids.
    """
    front = pieces["front-top"]
    front = front.val() if hasattr(front, "val") else front
    y_out = _enc.front_plane_y - _enc.front_wall - 1.0
    rows = []
    for name in ("pump-cartridge", "pump-cap"):
        body = pieces[name]
        body = body.val() if hasattr(body, "val") else body
        b = box(body)
        sweep = _enc._ybox(b.xmin, b.xmax, y_out, b.ymax, b.zmin, b.zmax)
        rows.append((name, sweep.intersect(front).Volume()))
    worst = max(v for _name, v in rows)
    ok = worst <= 1e-3
    return record_bound(Bound(
        "pump-cartridge-sweep-out",
        "The complete pump cartridge and cap pass through the bay mouth",
        ok,
        f"{len(rows)} pieces, most in the way {worst:.3f} mm³",
        "no front-top material in either complete withdrawal envelope",
        ([] if ok else [
            f"{name} meets {volume:.3f} mm³ of front-top between its installed aft face and "
            "the exterior — the pump heads can clear while the filled drawer still binds"
            for name, volume in rows if volume > 1e-3])))


# What a standing post's annulus may read short by. A post is fused as one cylinder and bored
# as another, so this is the mesh's own error on the two.
FLOOR_POST_TOL = 0.02


def check_floor_mounts(stations, pieces: dict) -> Bound:
    """Whether every floor post the slab was stationed for is standing, off the built pieces.

    `enclosure._floor_bosses` grows a post for the stations whose Y falls in the piece's own
    column, and for no others.

    Read as a probe of the piece's own material: a plug on the station's axis, from the crown
    down one insert's depth, is solid where the post stands and empty where it does not. The
    insert's bore takes its own share out of that plug, so a whole post reads the annulus."""
    rows = []
    solids = [p.val() if hasattr(p, "val") else p for p in pieces.values()]
    for sx, sy, tip, dia in stations:
        plug = cq.Solid.makeCylinder(
            dia / 2.0, _enc.floor_heatset_depth,
            cq.Vector(sx, sy, tip - _enc.floor_heatset_depth), cq.Vector(0, 0, 1))
        filled = max(_overlap.volume(plug, s) for s in solids) / plug.Volume()
        # The annulus this station's own bore leaves — each post is bored the same, and each
        # stands in whatever section its donor's hole gave it.
        want = 1.0 - (_enc.floor_heatset_dia / dia) ** 2
        rows.append((sx, sy, tip, dia, filled, filled >= want - FLOOR_POST_TOL))
    bad = [r for r in rows if not r[5]]
    return record_bound(Bound(
        "floor-mounts-land", "Every floor post under a bolted-down body is printed",
        bool(rows) and not bad,
        "no post stationed" if not rows else
        f"{len(rows) - len(bad)}/{len(rows)} posts standing",
        "a printed post at every hole the donor presents",
        [f"x {x:8.3f}  y {y:8.3f}  Ø{d:<5.1f} to z {t:7.3f}   "
         f"{'standing' if ok else 'NOT PRINTED — no piece owns this station'}"
         f"   ({f * 100:.1f}% of the annulus)" for x, y, t, d, f, ok in rows]))


# The same reading `check_floor_mounts` takes, and the same mesh error either way.
COND_MOUNT_TOL = 0.02
# What a probe stands in from the edge of the feature it reads, so a face the box drew exactly
# on the probe's own is not a coin toss between material and air.
COND_PROBE_INSET = 0.5
# The same, for the probe that stands inside a groove's OPENING rather than in the material
# either side of it.
COND_AIR_INSET = 0.05
_COND_UNPRINTED = "NOT PRINTED — no piece owns this station"


def check_cond_mount(cradle, mount, pieces: dict) -> Bound:
    """Whether all four of the condenser block's flanges have printed material to land on.

    The block is a donor envelope and these four sheets are its whole purchase, so what the box
    owes each is a face. FORE, that is a groove: material under the flange, material over it, and
    AIR BETWEEN THE TWO for the sheet to enter — all three across the block's own width and the
    whole of `cond_slot_grip`. AFT, it is a boss: the annulus a ruthex bore leaves in a finger,
    read from the flange face down one insert.

    Read the way `check_floor_mounts` reads a post — a probe volume against the printed pieces —
    because a station that no piece's band owns is a station nothing prints, and the assembly
    would otherwise stand a block on air and say nothing. The opening is read the same way and
    against the same solids: a groove the box has drawn something into is a groove the block's
    flange does not enter."""
    rows, ins = [], COND_PROBE_INSET
    solids = [p.val() if hasattr(p, "val") else p for p in pieces.values()]

    def filled(vol):
        return max(_overlap.volume(vol, s) for s in solids) / vol.Volume()

    grip, sect = _enc.cond_slot_grip, _enc.cond_rail_wall
    for face, cx0, cx1, fz0, fz1, _root in cradle:
        half = _enc.cond_slot_half(fz1 - fz0)
        for what, z0 in (("under", fz0 - half - sect), ("over", fz1 + half)):
            probe = (cq.Workplane("XY", origin=(cx0 + ins, face + ins, z0 + ins))
                     .box(cx1 - cx0 - 2 * ins, grip - 2 * ins, sect - 2 * ins,
                          centered=False).val())
            got = filled(probe)
            rows.append((f"fore flange at z {fz0:7.3f}, {what} its groove", got,
                         got >= 1.0 - COND_MOUNT_TOL, _COND_UNPRINTED))
        air = COND_AIR_INSET
        probe = (cq.Workplane("XY", origin=(cx0 + ins, face + ins, fz0 - half + air))
                 .box(cx1 - cx0 - 2 * ins, grip - 2 * ins,
                      (fz1 - fz0) + 2 * half - 2 * air, centered=False).val())
        got = filled(probe)
        rows.append((f"fore flange at z {fz0:7.3f}, {(fz1 - fz0) + 2 * half:.2f} mm open",
                     1.0 - got, got <= COND_MOUNT_TOL,
                     "OBSTRUCTED — a piece stands in the opening the flange enters"))
    _flank, _my0, _my1, bosses = mount
    for bx, by, tip in bosses:
        plug = cq.Solid.makeCylinder(
            _enc.mount_boss_dia / 2.0, _enc.heatset_depth,
            cq.Vector(bx, by, tip - _enc.heatset_depth), cq.Vector(0, 0, 1))
        got = filled(plug)
        want = 1.0 - (_enc.heatset_dia / _enc.mount_boss_dia) ** 2
        rows.append((f"aft boss under the hole at z {tip:7.3f}", got,
                     got >= want - COND_MOUNT_TOL, _COND_UNPRINTED))
    bad = [r for r in rows if not r[2]]
    return record_bound(Bound(
        "cond-mount-lands", "The condenser block's four flanges all have printed material "
        "to land on, and both fore grooves stand open for the sheet", bool(rows) and not bad,
        "nothing stationed" if not rows else f"{len(rows) - len(bad)}/{len(rows)} standing",
        "a groove standing open at each fore flange and a bored boss under each aft one",
        [f"{what:44s} {'standing' if ok else bad_msg}"
         f"   ({got * 100:.1f}% of the probe)" for what, got, ok, bad_msg in rows]))


def check_flank_vents(box, pieces: dict) -> Bound:
    """What the condenser's vents owe, read off the piece they were cut in.

    THE MULLION IS THE GOVERNING NUMBER and the section behind the groove floor is not. A slot
    takes its width out of the pitch, and the exterior profile lays `reeding.pierce_shell` of
    loops across what is left — 2 × 0.42 outer + 2 × 0.45 inner, the four that wall already
    carries (`enclosure/print-log.md`). The section moves the OTHER way with slot width: a wider
    slot puts its jamb further out on the groove's own half-ellipse, where the groove is
    shallower and the wall behind it thicker, so widening a slot never thins the wall and only
    ever thins the mullion.

    Read HERE and not while the piece is cut, because `_realized` keeps a piece between builds
    and a reading taken while drawing is one the second build never takes. `enclosure.build_pieces`
    draws and measures nothing; every reading off a built piece is asked of it afterwards, the way
    `check_cond_mount` asks after the block's four flanges. Both bounds this owes are recorded
    here for that reason — a bound recorded inside a cached builder is absent from the card on
    every build that does not redraw the piece."""
    reads = _enc.vent_readings(pieces, box)
    rows = {sx: r for sx, r in reads.items() if r["slots"] and r["mullions"]}
    check_flank_vent_towers(box, rows)
    least = min((min(r["mullions"]) for r in rows.values()), default=None)
    jamb = _enc.flute_depth * float(_reeding.groove(_reeding.pierce_width / 2.0))
    ok = least is not None and least >= _reeding.pierce_shell - _enc.stated_bound_tol
    pitch = _enc.flute_pitch(box.outer)
    return record_bound(Bound(
        "flank-vent-mullions",
        "Every mullion the condenser's vents leave carries the exterior's four wall loops",
        ok,
        ("no vent on this pack" if least is None
         else f"thinnest of {sum(len(r['mullions']) for r in rows.values())} mullions is "
              f"{least:.4f} mm across, on a {2.0 * _enc.wall - jamb:.4f} mm section"),
        f"at least {_reeding.pierce_shell:g} mm across, the loops the profile lays",
        ([f"{'+X exhaust' if sx > 0 else '−X intake':10s} "
          f"{len(r['slots']):2d} slots {min(r['slots']):.4f}–{max(r['slots']):.4f} mm, "
          f"{len(r['mullions'])} mullions {min(r['mullions']):.4f}–{max(r['mullions']):.4f} mm, "
          f"{r['open_mm2'] / 100.0:.2f} cm² free over the fan's own band"
          for sx, r in sorted(rows.items())]
         + ([] if ok else [
             f"a {_reeding.pierce_width:g} mm slot on {pitch:.4f} mm centres leaves "
             f"{_reeding.mullion(pitch, _reeding.pierce_width, 1):.4f} mm of mullion, and the "
             f"widest this field carries is "
             f"{_reeding.pierce_max(_reeding.pierce_shell, pitch):.4f}"]))))


def check_flank_vent_towers(box, rows: dict) -> Bound:
    """No mullion the vents leave stands free of the wall for longer than one slot segment.

    THIS IS WHAT THE TRANSOMS ARE FOR. A mullion is `reeding.mullion` across and the fan's band
    is `enclosure.vent_band` tall, so a slot run the whole height leaves a picket fifty-odd times
    as tall as it is thick. The brace is that the wall is NOT PIERCED at
    `enclosure.cond_vent_transoms` heights (`enclosure.vent_transoms`): every mullion and both
    jambs run into a full-section plate there, so what any of them stands free over is one
    segment — `enclosure.vent_segment`, and nothing wider.

    THE TARGET IS THE LAYOUT'S OWN SEGMENT, not a number typed here. The reading is the tallest
    OPENING on either flank, taken off the built piece; the segment is what the band divided by
    the transoms comes to. They agree when every transom landed and every slot was interrupted,
    and the reading falls BELOW the segment wherever something rooted on the flank already broke
    that slot — an obstruction and a transom compose, and neither is special-cased.

    Recorded off `check_flank_vents`' one reading, and never from inside `build_piece`."""
    tall = max((r["tallest"] for r in rows.values()), default=None)
    thin = min((min(r["mullions"]) for r in rows.values()), default=None)
    seg = _enc.vent_segment(box.cond_airway) if box.cond_airway else None
    band = _enc.vent_band(box.cond_airway) if box.cond_airway else None
    ok = tall is None or tall <= seg + _enc.stated_bound_tol
    return record_bound(Bound(
        "flank-vent-towers",
        "No mullion the condenser's vents leave stands free for more than one slot segment",
        ok,
        ("no vent on this pack" if tall is None
         else f"tallest of {sum(len(r['runs']) for r in rows.values())} openings is "
              f"{tall:.4f} mm, on a {thin:.4f} mm mullion — {tall / thin:.3g}:1"),
        ("no block on this pack" if seg is None
         else f"at most {seg:.4f} mm, the segment "
              f"{_enc.cond_vent_transoms} transoms leave in a {band[1] - band[0]:g} mm band"),
        ([f"{'+X exhaust' if sx > 0 else '−X intake':10s} "
          f"{len(r['runs']):2d} openings {min(r['runs']):.4f}–{max(r['runs']):.4f} mm tall "
          f"in {len(r['slots'])} slots"
          for sx, r in sorted(rows.items())]
         + ([] if band is None else [
             f"the band is z {band[0]:g}..{band[1]:g} — the fan's own footprint, "
             f"{_enc.cond_fan_rise:g} mm up from the block's base and {_enc.cond_fan_drop:g} "
             f"down from its crown"]
             + [f"transom {i + 1} of {_enc.cond_vent_transoms}: z {a:g}..{b:g}, "
                f"{b - a:g} mm of unpierced wall tying every mullion and both jambs"
                for i, (a, b) in enumerate(_enc.vent_transoms(box.cond_airway))])
         + ([] if ok else [
             f"unpierced at {_enc.cond_vent_transoms} heights the band leaves {seg:.4f} mm "
             f"segments, and something on this flank is open {tall:.4f} mm — a transom did not "
             f"land in the band, or a slot was not interrupted"]))))


def check_pack_over_core(stood, foam) -> Bound:
    """Every body of the flavour pack that stands over the cold core's cap clears its lid.

    `PACK_CROWN` is what buys that air. The pack's two source valves take a quarter turn that
    carries them aft over the core, and a body standing over the lid is only not in the core's
    way while it is standing OVER it — one storey down and it is resting on it, which is a clash
    the seam between the two halves is not measured to catch.

    Read in plan and not in box: a body whose footprint misses the cap is a body this says
    nothing about, however low it hangs."""
    lid = cap_face(foam)
    c = box(foam)
    rows = []
    for name, solid, _colour in stood:
        b = box(solid)
        if b.xmin >= c.xmax or b.xmax <= c.xmin or b.ymin >= c.ymax or b.ymax <= c.ymin:
            continue
        rows.append((name, b.zmin - lid))
    worst = min((g for _n, g in rows), default=None)
    over = [r for r in rows if r[1] < _card.CLEARANCE_FLOOR]
    return record_bound(Bound(
        "pack-over-core", "Every pack body reaching over the cold core clears its cap", not over,
        "nothing reaches over it" if worst is None else
        f"{len(rows)} over the lid at z {lid:.2f}, lowest clears by {worst:.3f} mm",
        f"at least {_card.CLEARANCE_FLOOR:g} mm over the cap",
        [f"{n} hangs {-g:.3f} mm INTO the cap's own lid — the pack sets down on `PACK_CROWN` "
         f"and the core's crown is the core's. Raise that plane, or carry that body's own turn "
         f"higher" if g < 0 else
         f"{n} clears the cap by {g:.3f} mm, under the {_card.CLEARANCE_FLOOR:g} the machine holds"
         for n, g in sorted(over, key=lambda r: r[1])]))


def check_core_lane(front_y: float, ahead) -> Bound:
    """Nothing on the floor ahead of the cold core reaches into it.

    The core is packed off the +Y wall of back-top, so the lane in front of it is what the stratum leaves
    rather than what it butts — and the refrigerant loop's two drawn legs are cut and brazed in
    that lane. A body that grew into it is a body the core is standing on."""
    over = [(n, y - front_y) for n, y in ahead if y > front_y + 1e-9]
    lane = min((front_y - y for _n, y in ahead), default=0.0)
    return record_bound(Bound(
        "core-lane", "The floor ahead of the cold core stops short of it", not over,
        f"core front at {front_y:.2f}, nearest body {lane:.2f} mm ahead of it",
        "every body on the floor short of the core's front face",
        [f"{n} reaches {much:.2f} mm past the core's front face — the core is packed off "
         f"`rear_plane_y` and does not give way. Move that body forward, or raise "
         f"`rear_plane_y`" for n, much in sorted(over, key=lambda r: -r[1])]))


# --- what fastens the cold core ---------------------------------------------
#
# The core presents no hole, so the box shuts on it instead: `enclosure._core_stops` blocks a
# corner of the slab in front of each of its front corners, and `enclosure._core_holds` turns a
# bracket off the +Y wall of back-top over the aft edge of its cap. The stations below are the planes
# those two are struck on, read off the placed core.
#
# THE LANE THE HOLD-DOWNS STAND IN, off the machine's own centreline. The aft cap carries the
# water pump inboard of it, the power column outboard on the +X flank, and the +Y wall of back-top's two
# flavour unions run through the band on the −X one; this is the strip clear of all four, taken
# on both flanks so the pair is a mirror.
CORE_HOLD_LANE = (58.0, 67.0)


def core_stops(foam) -> tuple:
    """The core's two FRONT corners as `enclosure.Box.core_stops` — `(cx, cy, r)` each.

    `cx, cy` is the centre the core's own corner round is struck on and `r` that round's radius,
    read off `_cold_core_interface` through the placement, so a block is pocketed about the same
    axis the corner is. Those three are the whole of what the wall is handed: how far the block
    laps, stands and webs is the box's own figure.

    THE CORNER IS READ OVER THE COURSE THE BLOCK STANDS AGAINST, and not off the body's box. The
    core carries printed features on its cap — valve cradles, tube anchors — and one of those
    standing proud of the shell's footprint moves that box in a plane no block is near. A station
    struck on the box carries BOTH blocks forward off a corner that has not moved, at
    ±(flank − r), where nothing is proud at all: 3 mm on the centreline reads `cy` 187 for a
    corner still at 190. So the footprint is taken over the block's own height, which is the
    outline the pocket wraps and the only part of the core it can touch."""
    b, r = box(foam), _cci.corner_round_radius
    course = foam.intersect(_boxed(b.xmin - 1.0, b.xmax + 1.0, b.ymin - 1.0, b.ymax + 1.0,
                                   b.zmin, b.zmin + _enc.core_stop_rise))
    foot = box(course)
    return tuple((sign * (foot.xmax - r), foot.ymin + r, r) for sign in (-1.0, 1.0))


def vent_chase(foam, foam_carry) -> tuple:
    """Where the cold core's PRV relief line arrives at the west wall, as
    `enclosure.Box.vent_chase` — one `(x, y, z)` in the machine's own frame.

    The X is the core's own WEST FLANK, which is the plane the chase's lip lands on and the
    plane the tube is cut off at; the Y and Z are that tube's own axis where it comes through.

    THE CORE STATES BOTH, NOT THE BOX. `_internal_routes` draws the line out through the shell's
    +Y flank, and the placed body carries the flank the line leaves by. So they come from the
    core's own placement, the same way a cap conduit does: move the core, re-yaw it, or move the
    station the shroud's bore lands on, and the chase follows without a number being retyped.

    Reached THROUGH `foam_assembly` rather than imported. `_internal_routes` puts the cold
    core's own directories on `sys.path` when it loads, and a module that does that at this
    one's import time changes what every later import in this process resolves to — the same
    hazard a walk taken in a cold process runs into. `_foam` already holds it."""
    tip = _foam.routes.routes["prv-vent"][-1]
    at, _axis = foam_carry((tip, (0.0, 1.0, 0.0)))
    return ((box(foam).xmin, at[1], at[2]),)


def core_holds(foam) -> tuple:
    """The core's aft crown as `enclosure.Box.core_holds` — `(x0, x1, aft, crown)` each.

    The lane is `CORE_HOLD_LANE` struck on both flanks; `aft` is the core's own aft face, which
    is the plane `rear_seam_clear` is measured to, and `crown` is `cap_face` — the lid's outer
    face, not the box's top, which carries the valve cradles."""
    b, crown = box(foam), cap_face(foam)
    lo, hi = CORE_HOLD_LANE
    return tuple((min(sign * lo, sign * hi), max(sign * lo, sign * hi), b.ymax, crown)
                 for sign in (-1.0, 1.0))


# How far off contact a face of the core may read from the grip that takes it — the same figure
# every seat on this card is held to, the ASSE anchor's, the flow-meter anchors' and both
# valve trays'.
CORE_GRIP_SLIP = TRAY_SEAT_SLIP


def _core_grip_windows(foam, shell) -> tuple:
    """One `(what, window)` per grip — the room a grip stands in, as a world box.

    A window holds that grip and nothing else of the piece it is printed on, so what the piece
    leaves inside one is the grip itself and the gap to the core is the grip's own fit."""
    b, out = box(foam), []
    for cx, cy, r in core_stops(foam):
        side = 1.0 if cx > 0.0 else -1.0
        x0, x1 = sorted((cx - side * r, shell.inner[1] if side > 0 else shell.inner[0]))
        face = cy - r - _enc.core_stop_slip / 2.0
        out.append((f"front block at x {cx:+8.2f}",
                    _boxed(x0, x1, face - _enc.core_stop_web, cy,
                           b.zmin, b.zmin + _enc.core_stop_rise)))
    for x0, x1, aft, crown in core_holds(foam):
        out.append((f"aft bracket at x {(x0 + x1) / 2.0:+8.2f}",
                    _boxed(x0, x1, aft - _enc.core_hold_reach, shell.inner[3],
                           crown, crown + _enc.core_hold_land)))
    return tuple(out)


def _boxed(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))


def check_slides(pieces, box) -> None:
    """The Z slides swept and their catches lifted, on the exact pieces this assembly
    carries — `enclosure._report_slide`'s own readings, entered in this ledger the way
    `carry_enclosure_bounds` enters the box's. That report ran piece against piece;
    `check_slide_lanes` and `check_core_ride` below are the sweeps only this module can
    take, because only it knows what is standing in the box when each motion happens."""
    _enc._report_slide(pieces, box)
    for b in _enc.BOUNDS:
        if b.id.startswith("z-slide-"):
            record_bound(Bound(*b))


# What rides FRONT-TOP into its own close: the flavour pack is made up into the trays
# and the tee wall on the bench (`internal-plumbing.md` §3), so the piece arrives
# carrying it and the sweep has to carry it too — LESS the bodies cradled on the cold
# core's own cap, which are the core's riders and nobody else's. The crossing runs to
# the bulkheads and the pumps' own tubes are made up later and are not in the box yet.
# THE COLLET PLATE IS ONE OF THESE. It goes into front-top through that piece's Z− face
# before the column closes (`enclosure._plate_slot`), so the steel rides the piece through
# the whole of its travel and this is the reading that carries it.
FRONT_RIDERS = ("valve-v-", "coil-v-", "tee-y-", "turn-", "step-", "collet-plate")
# What rides THE CORE on its cart — everything standing on or cradled in the cap's lid
# when the back assembly comes over: the water pump, its two made-up chains, and the
# three cap-cradled valves with their coils and port stubs. They sweep with the core,
# so the ride carries them.
CORE_RIDERS = ("seaflo-pump", "valve-v-a", "valve-v-b", "vk-solenoid",
               "coil-v-a", "coil-v-b", "stub-fluid-2", "stub-fluid-4",
               "discharge-chain", "suction-chain")
# And what is NOT in the box at all when the core rides in: the pan and its plate come
# through the −X wall after, the pump cartridge later still, and every crossing run is
# internal-plumbing's, made up at the mouth. Everything else in the back — the chain,
# the meter, the wall electronics, the bulkheads and their rings — rides back-top or
# clamps its walls and is already standing, which is what the sweep is against.
CORE_RIDE_LATER = ("foam-assembly", "moisture-plate",
                   "funnel", "nameplate", "asse-drip-pan")
CORE_RIDE_RUNS = ("tube-", "turn-", "step-")


def _swept_worst(mover_parts, fixed_parts, axis, travel):
    """The worst contested volume over one linear motion — the movers translated along
    `axis` from `travel` out down a ladder of stations to home, dense where the joint
    closes, intersected with each fixed member at each. `(worst_mm³, at_mm)`, the rung
    count, and the per-member worst readings for whoever has to name a blocker.

    MEMBER-WISE, NEVER FUSED. A fuse chain over thirty placed castings can come back
    subtly broken — a solid whose intersections report phantom volume — and a sweep
    against it fails loud on clean geometry. A compound carries the same bodies with no
    boolean taken, and each fixed member answers for itself."""
    rungs = [d for d in (0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0) if d < travel]
    d = 24.0
    while d < travel:
        rungs.append(d)
        d += 16.0
    rungs.append(travel)
    # THE STATIONS ARE MEASURED ON MESHES, through `_overlap`. `Shape.intersect` reports
    # 0.00 mm³ for two surfaces tangent along their crossing and raises nothing, and a mover
    # grazing a fixed member holds that tangency the length of the lane. A mesh reading stands
    # within ~2 × `_meshes.DEFLECTION` of the exact one, under-reporting where the surface is
    # convex.
    #
    # MESHED ONCE, MOVED MANY TIMES. `_meshes.meshed` memoizes on the shape's identity, and
    # translating a compound hands back a new shape. A manifold translates itself, so the
    # mover is tessellated once and the ladder moves it; the fixed members do not move.
    mover = _meshes.meshed(cq.Compound.makeCompound([s for _n, s in mover_parts]))
    fixed = [(name, m, _meshes.box(m))
             for name, m in ((n, _meshes.meshed(s)) for n, s in fixed_parts)]
    # THE BOXES ARE A PRE-FILTER AND ONLY THAT, as in `manifold_layout.clashes`: boxes that
    # miss are solids that miss, boxes that meet prove nothing, and every pair that survives
    # is asked. The mover's box rides with the mover, so a station's box is the home box
    # offset.
    mbb = _meshes.box(mover)
    worst, hits = (0.0, 0.0), {}
    for d in rungs:
        ox, oy, oz = axis[0] * d, axis[1] * d, axis[2] * d
        at = mover.translate([ox, oy, oz])
        mx0, mx1 = mbb.xmin + ox, mbb.xmax + ox
        my0, my1 = mbb.ymin + oy, mbb.ymax + oy
        mz0, mz1 = mbb.zmin + oz, mbb.zmax + oz
        total = 0.0
        for name, m, bb in fixed:
            if (mx0 > bb.xmax or bb.xmin > mx1
                    or my0 > bb.ymax or bb.ymin > my1
                    or mz0 > bb.zmax or bb.zmin > mz1):
                continue
            v = _overlap.volume(at, m)
            if v > 1e-6:
                total += v
                if v > hits.get(name, (0.0, 0.0))[0]:
                    hits[name] = (v, d)
        if total > worst[0]:
            worst = (total, d)
    return worst, len(rungs), hits


def check_slide_lanes(pieces, solids, ebox) -> Bound:
    """The FRONT column's close, swept with its cargo: front-top arrives carrying the
    flavour pack, so what slides is the piece AND the manifold made up into it, and what
    it slides over is front-bottom AND the refrigeration stratum already seated there.
    `z-slide-front-clear` proved the pieces; this is the same travel with the bodies in.

    IT COMES IN FROM THE FRONT, so the cargo sweeps AFT over the stratum — the axis
    here is the entry offset, fore of home, and it is the one `_z_rail_runs` closes the
    rails against.

    THE BACK COLUMN TAKES NO SUCH ROW because its tub is EMPTY when it closes: the core
    cannot pass under back-top's own +Y wall, so it enters through the Y-seam mouth
    after the column is one piece (`check_core_ride`), and everything back-top carries
    — the chain, the meter, the panel, the wall electronics — rides with it over
    nothing. The piece-on-piece sweep is the whole of that close."""
    plate = ebox.collet_plate if (ebox.pump_bay and ebox.collet_plate) else None
    travel = _enc._z_rail_travel(ebox.inner, ebox.y_joint, "front", plate,
                                 ebox.vent_chase)
    movers = [("front-top", pieces["front-top"].val())]
    for name, s in solids.items():
        if name.startswith(FRONT_RIDERS) and not name.startswith(CORE_RIDERS):
            movers.append((name, s))
    fixed = [("front-bottom", pieces["front-bottom"].val())]
    for name in ("compressor", "condenser+fan", "mq6-sensor", "thermal-fuse",
                 "fuse-clamp"):
        if name in solids:
            fixed.append((name, solids[name]))
    (worst, at), n, hits = _swept_worst(movers, fixed, (0.0, -1.0, 0.0), travel)
    ok = worst <= 2.0
    return record_bound(Bound(
        "z-slide-front-lanes", "The front top slides home carrying the flavour pack",
        ok,
        f"worst {worst:.1f} mm³ contested, {at:.2f} mm out, {n} stations over "
        f"{travel:.1f} mm",
        "0 mm³ at every station of the loaded travel",
        ([] if ok else [
            f"front-top with the flavour pack aboard contests {worst:.1f} mm³ "
            f"{at:.2f} mm out of home — in the lane: "
            + "; ".join(f"{k}: {v:.1f} mm³ at {d:.1f}" for k, (v, d) in
                        sorted(hits.items(), key=lambda r: -r[1][0])[:4])
            + ". A blocker either rides the piece (add it to `FRONT_RIDERS`) or the "
            f"pack has to open its lane"])))


def check_core_ride(pieces, solids, ebox) -> Bound:
    """The cold core's ride IN: through the open Y-seam mouth, aft over back-bottom's
    slab to its seat on the rear lip, under the hold-down feet and past everything
    back-top brought with it. The whole travel is swept against the closed back column
    and its riders, because this is the one motion in the build that crosses the box's
    whole depth loaded.

    THE LID'S TENANTS RIDE WITH IT. The water pump, its two chains and the three
    cap-cradled valves stand on the core before the back assembly comes over, so the
    mover here is the core AND its riders, and the lane proved open is the loaded one.

    Its service twin is the same sweep backwards: four screws, the back assembly aft
    and off the core, and the bay is cart work again."""
    movers = [("foam-assembly", solids["foam-assembly"])]
    for name in CORE_RIDERS:
        if name in solids:
            movers.append((name, solids[name]))
    travel = (max(box(s).ymax for _n, s in movers) - ebox.y_joint) + 5.0
    members = [("back-bottom", pieces["back-bottom"].val()),
               ("back-top", pieces["back-top"].val())]
    if "ceiling-panel" in pieces:
        panel = pieces["ceiling-panel"]
        panel = panel.val() if hasattr(panel, "val") else panel
        members.append(("ceiling-panel", panel))
    for name, s in solids.items():
        bb = box(s)
        if bb.ymax <= ebox.y_joint - 5.0:
            continue                       # the front column's; not standing in this lane
        if name.replace("_", "-").startswith("enclosure-"):
            continue                       # the box's own pieces, under either spelling an
                                           # assembly child carries: the back pair is already
                                           # fused above, and the front pair is the core's
                                           # own train — it rides at the core's side of the
                                           # motion, and the last 13 mm it shares with the
                                           # back column is the Y telescope the home fits
                                           # already prove
        if name.startswith(CORE_RIDE_LATER + CORE_RIDERS) or name.startswith(CORE_RIDE_RUNS):
            continue
        if name.endswith("-word") or name.endswith("-ink"):
            continue
        members.append((name, s))
    (worst, at), n, hits = _swept_worst(movers, members, (0.0, -1.0, 0.0), travel)
    ok = worst <= 2.0
    return record_bound(Bound(
        "core-rides-in", "The cold core rides in through the mouth to its seat", ok,
        f"worst {worst:.1f} mm³ contested, {at:.2f} mm out, {n} stations over "
        f"{travel:.1f} mm",
        "0 mm³ down the whole lane",
        ([] if ok else [
            f"the core contests {worst:.1f} mm³ at {at:.2f} mm fore of its seat — "
            f"standing in its lane: "
            + "; ".join(f"{k}: {v:.1f} mm³ at {d:.1f}" for k, (v, d) in
                        sorted(hits.items(), key=lambda r: -r[1][0])[:4])
            + ". Either it goes on after the core (add it to `CORE_RIDE_LATER`) or the "
            f"lane has genuinely closed and the pack has to open it"])))


def check_core_held(pieces: dict, foam, shell) -> Bound:
    """Whether all four of the cold core's grips are closed on it.

    Read inside each grip's own window, off the built pieces: the piece's material in there IS
    the grip, so the distance from it to the core is the fit the grip was drawn at — one
    `enclosure.core_stop_slip` on a front block's bore, 0 on an aft bracket's foot. Read over the
    whole piece instead and a box drawn round the core with no grip in it still returns 0, from
    the slab under it.

    A window no piece has material in is a grip nothing prints, and reads as the full horizon."""
    rows, solids = [], [p.val() if hasattr(p, "val") else p for p in pieces.values()]
    for what, window in _core_grip_windows(foam, shell):
        grip = [g for g in (s.intersect(window) for s in solids) if g.Volume() > 1.0]
        rows.append((what, sum(g.Volume() for g in grip),
                     min((_clearing.gap(foam, g, 1.0) for g in grip), default=1.0)))
    bad = [r for r in rows if r[2] > CORE_GRIP_SLIP]
    worst = max((g for _w, _v, g in rows), default=0.0)
    return record_bound(Bound(
        "core-held", "Every grip on the cold core is closed on it", bool(rows) and not bad,
        "nothing stationed" if not rows else
        f"{len(rows) - len(bad)}/{len(rows)} grips closed, furthest off {worst:.3f} mm",
        f"every grip within {CORE_GRIP_SLIP:g} mm of the core",
        [f"{what} holds {vol:.0f} mm³ of printed material and stands {g:.4f} mm off the core — "
         f"the grip is drawn beside the core rather than on it"
         for what, vol, g in rows if g > CORE_GRIP_SLIP]))


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
    and a cutoff reading cabinet air.

    BOTH HOPS ARE TAKEN ALONG THE FACE'S OWN NORMAL, which `FUSE_FACE_NORMAL` names and
    `power_face_station` has already held the machine to. The cover is a box and the pair goes
    on whichever of its faces costs the machine least; a reading struck on a fixed axis instead
    would go quietly meaningless the moment that face changed, which is the one failure this
    row exists to catch."""
    out = 0 if abs(FUSE_FACE_NORMAL[0]) > 0.5 else 1
    sign = 1.0 if FUSE_FACE_NORMAL[out] > 0.0 else -1.0
    # The case's own axis is the other horizontal one, and its mid-height is Z either way.
    case = 1 - out

    def span(bb, i):
        return ((bb.xmin, bb.ymin, bb.zmin)[i], (bb.xmax, bb.ymax, bb.zmax)[i])

    def s(v):                       # a coordinate as a distance OUT of the face
        return sign * (v - face[out])

    fb, cb = box(fuse), box(clamp)
    f_lo, f_hi = span(fb, out)
    near, far = (f_lo, f_hi) if sign > 0.0 else (f_hi, f_lo)
    crown = max(s(v) for v in span(cb, out))
    bed = s(near)
    # A slab on the case's own axis, over the case's own length, from the cover's face out past
    # everything the clamp has: what stands in it is the crown and nothing else the part is.
    mid = [0.0, 0.0, (fb.zmin + fb.zmax) / 2.0]
    mid[out] = face[out] + sign * crown / 2.0
    mid[case] = sum(span(fb, case)) / 2.0
    dims = [0.0, 0.0, 2.0 * BEDDED_TOL]
    dims[out] = crown
    dims[case] = _fuse.BODY_L
    slab = cq.Workplane("XY", origin=tuple(mid)).box(*dims)
    over, vol = _overlap.common(clamp, slab.val())
    grip = (None if vol <= 0.0
            else min(s(v) for v in span(ml.extents(over), out)) - s(far))
    ok = abs(bed) <= BEDDED_TOL and grip is not None and abs(grip) <= BEDDED_TOL
    return record_bound(Bound(
        "cutoff-bedded", "The cutoff's case is pinched between the power box and its clamp", ok,
        (f"case on the cover {bed:+.3f} mm, clamp on the case "
         + ("nothing over it" if grip is None else f"{grip:+.3f} mm")),
        f"both 0 within {BEDDED_TOL:g} mm",
        ([] if ok else [
            f"thermal-fuse: the case's contact line stands {bed:+.3f} mm off the power box's "
            f"face at {'xyz'[out]} {face[out]:.2f}, and the clamp's crown "
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


def cap_anchor(name: str):
    """One of the cold core's chain anchors as a station in the CORE'S OWN frame:
    `((x, y, z), the way the body comes into it)`.

    `foam_assembly` authors the rib in the cap's frame and turns it back through the cap's own
    half-turn install, so its `(x, y)` is already the assembly's; the Z is the seat's own axis,
    which stands `_cold_core_interface.cap_anchor_axis_over_face` over the lid's outer face. The
    seat opens on the cap's +Z, which is the way the body is laid into it."""
    x, y = _foam.cap_anchor_station(name)
    return ((x, y, _foam.cap_face_z + _cci.cap_anchor_axis_over_face(name)),
            _foam.cap_conduit_axis_out())


def cap_side_anchor(name: str):
    """One of the cold core's SIDEWAYS anchors as a station in the CORE'S OWN frame:
    `((x, y, z), the way the run comes into it)`.

    The pipe opens on the core's own −Y, so a run beds into it from the room rather than being
    laid down into it. Its Z stands `_cold_core_interface.cap_side_anchor_height`'s own axis term
    over the lid's outer face, and its Y is the pipe's axis — `axis_off` forward of the post's
    face, which `foam_assembly.cap_side_anchor_station` already carries."""
    x, y = _foam.cap_side_anchor_station(name)
    return ((x, y, _foam.cap_face_z + _cci.cap_side_anchors[name].over_face),
            (0.0, -1.0, 0.0))


def cap_conduit(name: str):
    """One of the cold core's cap conduits as a station in the CORE'S OWN frame:
    `((x, y, z), outward axis)`.

    `foam_assembly` authors the bore in the cap's frame and turns it back through the cap's own
    half-turn install, so its `(x, y)` is already the assembly's; the mouth's Z is the lid's
    outer face, which is the top of that same solid. The way out is the cap's +Z."""
    x, y = _foam.cap_conduit_station(name)
    return ((x, y, _foam.cap_face_z), _foam.cap_conduit_axis_out())


def seaflo_west_limit() -> float:
    """The westmost the pump's casting may reach on the tray's storey.

    THE TRAY IS THE BODY WITH A WALL TO GET THROUGH. It draws out through a slot in the −X wall
    (`west_wall_ports`), so it is stated off that wall and not off whatever lies east of it: the
    tab standing outside the skin, one rim — `asse_drip_pan`'s own outline and the flange turned out
    either way — the sleeve's backstop behind it, and one `FOOT_CLEAR` is the lane it takes, and
    the casting begins where that lane ends. The pump has air on its east flank and the tray has
    a wall on its west, so the millimetre is the tray's to keep."""
    return (pan_west_x() + _pan.PAN_X + 2.0 * _pan.FLANGE_W
            + _pan.PAN_SLIP + DRIP_SLEEVE_T + FOOT_CLEAR)


def seaflo_port_lane_limit() -> float:
    """The westmost the pump's casting may reach on the FLAVOUR UNIONS' OWN STOREY.

    THE CASTING IS THE EAST FLANK OF THE PORT LANE. The two flavour unions cross the +Y wall of back-top
    between the rear seam's boss chain and this casting, `PORT_WEST_COLUMN` stands the pair off
    that chain by one `PORT_LANE_CLEAR`, and this is the same millimetre owed on the other side.
    Read off the east column and the union's own body — the station the field actually stands
    on, which is where `check_port_pair` takes its own reading."""
    return PANEL_X["bulkhead-flavor-a"] + _jg.BODY_D / 2.0 + PORT_LANE_CLEAR


def build_seaflo(foam, gate: float):
    """The water pump at the machine's own `SEAFLO_YAW`, lying flat on the core's crown, its aft
    face flush with the core's own back, and standing east of both the tray and the port lane.

    IT IS SITED BY WHAT LIES WEST, not by the mirror plane. Centred, the pump left the tray
    whatever the −X wall happened to be, which made the tray's rim a function of the appliance's
    stated width; stood off `seaflo_west_limit`, the tray keeps its lane at any width and the
    pump spends the air on its own east flank instead. `check_pan_lane` reads back the lip that
    leaves, and the pump stays centred wherever the lane is already wide enough.

    TWO ROOMS READ THE SAME CASTING and it is one body, so the shift is the wider of what they
    ask. The tray lies alongside the pump at its own storey; the flavour unions cross the wall
    aft of it and a storey up, in the band `flavor_storey` carries their barrels over the feet.
    `check_port_pair` reads that second flank back off the placed body.

    The casting is measured over each room's own four planes — above the feet and aft of the
    discharge barb for the tray, in the rear band at the pair's own storey for the unions, the
    places the box would answer for the whole part and be wrong (the feet are 8 mm of a 72 mm
    casting, the barb one 10 mm band of a 187 mm one)."""
    b = box(foam)
    shape = import_step(str(SEAFLO_STEP)).val()
    turns = (((0, 0, 1), SEAFLO_YAW),)
    planes = dict(y1=b.ymax, z0=cap_face(foam))
    probe, probe_carry = seat_body(shape, turns, cx=0.0, **planes)
    pb = box(probe)
    west = pump_west_face(probe, pb.zmin + _lines._pump.FOOT_T, pb.zmax,
                          pan_front_y(probe_carry), pb.ymax)
    storey = flavor_storey(gate, probe)
    lane = pump_west_face(probe, storey - _jg.BODY_D / 2.0, storey + _jg.BODY_D / 2.0,
                          bulkhead_mouth_y(), _enc.rear_plane_y)
    return seat_body(shape, turns, seat="seaflo-pump",
                     cx=max(0.0, seaflo_west_limit() - west,
                            seaflo_port_lane_limit() - lane), **planes)


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
# and none of its solids do.
#
# Its column is the rib's — `cap_anchors["suction-chain"]` — which hugs the pump rather than the
# core's east edge and leaves the wall side of the strip open. `clearance-floor` is what holds it
# off the pump's casting, the same reading it takes of every other pair.
# How far FORWARD of the pump's suction mouth the chain's barb stands. `water-7` turns from east
# to forward in this gap, and a 3/8" corner needs its whole radius as tangent in each leg it
# touches.
SUCT_CORNER_ROOM = 24.0


def build_suction_chain(foam_carry, suction):
    """The chain lying in its printed seat on the cold core's cap, east of the pump.

    TWO OF ITS COORDINATES ARE THE SEAT'S, the same bargain its discharge twin takes: X and Z
    come off `cap_anchor("suction-chain")`. Y stands its barb one `SUCT_CORNER_ROOM` forward of
    the pump's suction mouth, which is what buys `water-7`'s corner.

    WHAT FOLLOWS THIS PLANE IS V-K. `build_vk` seats the valve on this chain's own collet, so the
    two mouths stay on one plane and the joint stays a butt — there is tube in both grips and
    none between them. `cap_cradles["vk-solenoid"].seat` is
    what carries the valve up to meet it, and `cradles-land` is where the two are held together.

    What holds it off the pump's own casting is `clearance-floor`, the reading every other pair
    on this card answers to."""
    axis = foam_carry(cap_anchor("suction-chain"))[0]
    chain = _suct.build()
    # The chain's own Ø, read on X because the box is measured BEFORE the turn: unturned the
    # chain stands its length on Z and its widest section across X, and the turn is about X.
    half = box(chain).xlen / 2.0
    return seat_body(chain, SUCT_CHAIN_TURN, seat="suction-chain",
                     x0=axis[0] - half,
                     y1=suction[0][1] - SUCT_CORNER_ROOM,
                     z0=axis[2] - half)


# --- the discharge chain, in the lane west of the pump ---------------------
#
# The three fittings that carry the pump's outlet off its moulded 3/8" barb, hold the
# carbonator's pressure off it when it is idle, and hand the water over on 1/4" tube:
# MAACFLOW barb, GASHER check, PP450822E collet, made up on the bench as one piece.
#
# It lies BARB AFT, COLLET FORWARD in the lane west of the pump, which is the suction chain's
# own pose read across the machine — so it takes the suction chain's own turn.
DISCH_CHAIN_TURN = SUCT_CHAIN_TURN
# How far FORWARD of the pump's discharge mouth the chain's barb stands — the suction side's
# `SUCT_CORNER_ROOM` read across the machine. `water-6` turns from west to forward and falls in
# this gap, and a 3/8" corner needs its whole radius as tangent in each leg it touches.
DISCH_CORNER_ROOM = 24.0
# What a printed rib holds its chain off itself, radially. `chains-seated` reads it back.
CHAIN_SEAT_SLIP = 0.2
def build_discharge_chain(foam_carry, seaflo_carry):
    """The chain lying in its printed seat on the cold core's cap, west of the pump.

    TWO OF ITS COORDINATES ARE THE SEAT'S. X and Z come off `cap_anchor("discharge-chain")` —
    the rib the top lid stands, carried out of the cap's own frame — so the body lies where the
    printed part says and the two cannot drift apart. Y stands its barb one `DISCH_CORNER_ROOM`
    forward of the pump's discharge mouth, which is what buys `water-6` its corner.

    `check_anchor_lands` is where the rib is held against the section it seats: the seat's radius
    is read off the placed chain's own stack, and the rib's whole length has to lie inside one
    section of it.

    THE COLLET FIRES AT THE FLOW REGULATOR'S BACK, on the storey that body stands on. What its
    straight comes to against the 2 × `TUBE_BEND` a collet asks for is the `port-leads` row for
    `discharge-chain.tube-port`, read there off the regulator's own solid."""
    disch = seaflo_carry(_lines._pump.discharge())[0]
    axis = foam_carry(cap_anchor("discharge-chain"))[0]
    chain = _dis.build()
    # The chain's own Ø, read on X because the box is measured BEFORE the turn: unturned the
    # chain stands its length on Z and its widest section across X, and the turn is about X.
    half = box(chain).xlen / 2.0
    return seat_body(chain, DISCH_CHAIN_TURN, seat="discharge-chain",
                     x0=axis[0] - half,
                     y1=disch[1] - DISCH_CORNER_ROOM,
                     z0=axis[2] - half)


# --- the tap-water bulkhead, through the +Y wall of back-top -------------------------
#
# The union the customer's supply line pushes into, clamped through the +Y wall of back-top. Its own frame
# already runs the flow down ±Y with the seating face on Y = 0, which is the axis and the plane
# the +Y wall of back-top gives it, so it takes NO TURN: the flange bears on the wall's outer face, the
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
    """The plane the union's flange bears on — the +Y wall of back-top's OWN OUTER FACE, and the face of the
    ring lying flush in it.

    The pocket is cut one `bulkhead_ring.THICK` INTO that face and the ring fills it, so wall stock and
    colour come out one plane and a flange landing here lands on both at once."""
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
    onto, and the only part of the machine behind its own +Y wall of back-top."""
    inlet = asse_carry(_asse.port("tube-in"))[0]
    body = import_step(str(BULKHEAD_STEP)).val()
    return seat_body(body, (), seat="bulkhead-water",
                     station=(_jg.port(-1.0),
                              (inlet[0], bulkhead_mouth_y(), inlet[2])))


def y_wall_ports(*bulkhead_carries):
    """Through-holes the +Y wall of back-top carries, as `(kind, x, z, *size)` on its own plane.

    One per union: the bore its threading passes. Each is struck on the fitting's own inboard
    collet, so hole and barrel cannot land on two different columns, and it is bored one
    `PORT_HOLE_SLIP` over the barrel that goes through it."""
    return [("round", carry(_jg.port(-1.0))[0][0], carry(_jg.port(-1.0))[0][2],
             _jg.panel_hole_d(PORT_HOLE_SLIP)) for carry in bulkhead_carries]


# EVERY CROSSING THE +Y WALL OF BACK-TOP PASSES A TUBE THROUGH, as `station -> (the module that states
# that fitting's own panel figures, the ring station in `bulkhead_ring.STATIONS`, that ring's own
# name, the fluid a colour names it by)`. Two families and one construction: each bears a flange
# on a ring of its own, each is bored one `PORT_HOLE_SLIP` over its own barrel, and each
# fitting's own nut clamps it from inboard.
#
# EVERY STATION WEARS A CHIP AND EVERY CHIP CARRIES A COLOUR — the colour of the tube that goes
# into it. The fluid is the key into `_y_wall_dimensions.port_colors`, so the pocket, the chip
# lying in it, the tube it receives and the mark the drawing paints are one station struck once.
# Both flavour ports take black because the flavour lines are black; what that pair does not do is
# tell A from B, and the word they wear says so by being the same word.
Y_WALL_FITTINGS = {
    "bulkhead-water": (_jg, "union", "water", "water"),
    "bulkhead-carb": (_jg, "union", "carb", "carb"),
    "bulkhead-flavor-a": (_jg, "union", "flavor-a", "flavor"),
    "bulkhead-flavor-b": (_jg, "union", "flavor-b", "flavor"),
    "co2-inlet": (_neofit, "neofit", "co2", "co2"),
}
MARKED_UNIONS = {n: fluid for n, (_m, _r, _nm, fluid) in Y_WALL_FITTINGS.items() if fluid}


def ring_name(which: str) -> str:
    """The body name one chip goes into the assembly under."""
    return f"bulkhead-ring-{which}"


def word_name(which: str) -> str:
    """The body name that chip's lettering goes in under — a second solid in a second colour,
    lying in the recess the chip carries for it."""
    return f"bulkhead-ring-{which}-word"


# The slip a pocket keeps around the chip that drops into it.
BULKHEAD_RING_SLIP = 0.2
# THE WALL THE FIELD KEEPS AROUND EVERY CHIP, and it is one figure read on BOTH faces of the wall.
# Outboard it is the web of stock standing between two neighbouring pockets, which is the only
# thing holding one colour off the next — `port-field-web` reads the pitch against it. Inboard it
# is how far the boss reaches past the chip it backs.
BULKHEAD_RING_RIM = 3.0
# How far the boss stands INBOARD off the wall's inner face, and it is the chip's own thickness:
# exactly what the pocket took out of the outer face. So the stock under every chip is the wall's
# own full thickness and the clamped stack is the same at every station.
PORT_BOSS_PROUD = _ring.THICK
def port_pocket_d(ring: str = "union") -> float:
    """What one station's pocket measures ACROSS — the chip's own width and the slip it takes in
    it. The wall cuts it and `port-field-web` reads it against the pitch, off this one call."""
    return _ring.od(ring) + 2.0 * BULKHEAD_RING_SLIP


def port_pocket_rise() -> float:
    """How far a pocket stands ABOVE the bore's axis — the chip's own rise and its slip. The top
    row runs out past the box's top face and is cut off by it, which is what leaves those three
    chips open at the top."""
    return _ring.RISE + BULKHEAD_RING_SLIP


def port_boss_d(ring: str = "union") -> float:
    """What one station's boss measures across — the chip it backs and a rim either side.

    It is wider than `PORT_PITCH`, so two neighbours on one row merge into one longer boss.
    `port-field-web` is the reading that keeps the POCKETS apart."""
    return _ring.od(ring) + 2.0 * BULKHEAD_RING_RIM


def wall_stations(bulkhead_carry, panel_carries, co2_carry) -> dict:
    """Every `Y_WALL_FITTINGS` station on the wall, as
    `name -> (x, z, fitting, ring, ring name, fluid)`.

    Each column is read off the FITTING'S OWN INBOARD COLLET, which is what `y_wall_ports` and
    `co2_wall_port` bore from — so a pad, a ring and the hole through both cannot land on two
    different columns."""
    carries = {"bulkhead-water": bulkhead_carry, **panel_carries, "co2-inlet": co2_carry}
    out = {}
    for name, (fitting, ring, which, fluid) in Y_WALL_FITTINGS.items():
        x, _y, z = carries[name](fitting.port(-1.0))[0]
        out[name] = (x, z, fitting, ring, which, fluid)
    return out


def y_wall_field(stations):
    """The pocket each chip lies in, as `enclosure.Box.port_field` — one per station, not one field
    across them. `enclosure._port_field` cuts each into the wall's outer face and stands a boss one
    `BULKHEAD_RING_RIM` larger on the inner one."""
    return _enc.PortField(PORT_BOSS_PROUD, BULKHEAD_RING_RIM,
                          tuple((x, z, port_pocket_d(ring), port_pocket_rise())
                                for x, z, _fitting, ring, _which, _fluid in stations.values()))


# TWO OF THE FIVE CROSSINGS TAKE A TUBE THE CUSTOMER CUTS, in their own kitchen and to their own
# length: the tap-water run up to their angle stop, and the tether back to the regulator on their
# cylinder. Each leaves by a collet on this wall and ends on hardware that carries no ring, so the
# station's word goes out with it on a printed collar — `printed-parts/faucet/tube-collar/`, the
# chip's own outline bored for the tube. The collar's frame is the fitting's, so it seats down the
# same axis with no turn of its own, exactly as the chip does.
#
# What is drawn outboard is the CUSTOMER'S TUBE and not a part of the machine, the way
# `faucet_layout`'s slab is their countertop: enough of it to carry the collar and no more.
CUSTOMER_TUBE_STATIONS = ("bulkhead-water", "co2-inlet")
# Thumb room at the release ring before the collar starts — a collet is pushed in to let the tube
# go, and a collar on the ring is a collar in the way of that.
COLLAR_OFF_COLLET = 8.0
# Tube drawn past the collar, so the stub reads as a run leaving and not as an end.
COLLAR_TUBE_TAIL = 10.0


def customer_tube_name(which: str) -> str:
    """The body name one customer-cut tube goes into the assembly under.

    IT CARRIES THE TUBE PREFIX BECAUSE IT IS TUBE. `_scorecard._split_placed` reads the placed
    world into its three populations off these names, and what it asks of a body it does not ask
    of a length of tube: a tube is fastened by the collet it seats in, so it owes no row in the
    fastening table, it stands at 0.00 against the fitting it is pushed into by construction, and
    it is not an obstruction in front of the port it leaves. Named outside the prefix it enrols
    as a body and is charged all three."""
    return f"tube-customer-{which}"


def collar_name(which: str) -> str:
    """The body name one collar goes into the assembly under."""
    return f"tube-collar-{which}"


def collar_word_name(which: str) -> str:
    """The body name that collar's lettering goes in under — a second solid in a second colour,
    lying in the flats the collar carries for it."""
    return f"{collar_name(which)}-word"


def build_customer_tubes(bulkhead_carry, panel_carries, co2_carry):
    """The two customer-cut tubes outboard of the wall and the collar on each, as
    `(name, solid, colour)`.

    Both are read off the fitting's OUTBOARD collet — the same mouth `wall_stations` reads its
    columns off, one end further along — so a stub and the fitting it leaves cannot land on two
    different axes. The tube takes the identification colour off `_routing.SPOOLS`, the same spool
    the run inboard of the ring is cut from; the collar takes the filaments its chip prints in."""
    carries = {"bulkhead-water": bulkhead_carry, **panel_carries, "co2-inlet": co2_carry}
    out = []
    for name in CUSTOMER_TUBE_STATIONS:
        fitting, _ring, which, fluid = Y_WALL_FITTINGS[name]
        x, y, z = carries[name](fitting.port(+1.0))[0]
        length = COLLAR_OFF_COLLET + _collar.LENGTH + COLLAR_TUBE_TAIL
        # The spool by its own colour, so a stub cut off a table that moved has no spool at all.
        spool = next(s for s in _routing.SPOOLS.values() if s.rgb == _rear.port_colors[fluid])
        out.append((customer_tube_name(which),
                    cq.Solid.makeCylinder(_collar.TUBE_OD / 2.0, length,
                                          cq.Vector(x, y, z), cq.Vector(0.0, 1.0, 0.0)),
                    cq.Color(*(c / 255.0 for c in spool.rgb))))
        body, lettering = _collar.split(import_step(str(_collar.STEPS[which])).val())
        for name, solid, rgb in ((collar_name, body, _rear.chip_color(fluid)),
                                 (collar_word_name, lettering, _rear.word_color(fluid))):
            out.append((name(which),
                        solid.translate((x, y + COLLAR_OFF_COLLET, z)),
                        cq.Color(*(c / 255.0 for c in rgb))))
    return out


def build_bulkhead_rings(stations):
    """The chips and their words, two solids per station, as `(name, solid, colour)`.

    Each is seated on the same column its pocket was struck on, with its own inboard face on that
    POCKET'S FLOOR — one chip's thickness inside the +Y wall of back-top's outer face. So the chip's outboard
    face and the wall's come out one plane, the fitting's flange lands on the chip where the bare
    wall would otherwise carry it, and the chip is in the clamped stack the way the wall is.

    THE WORD RIDES THE CHIP IT IS CUT INTO, on that same seating: one station is ONE file holding
    both bodies in one frame, with the word already lying in its recess, so the pair cannot come
    apart here. `bulkhead_ring.split` is what takes them out of it."""
    floor = _enc.rear_plane_y + _enc.wall - _ring.THICK
    out = []
    for x, z, _fitting, _ring_family, which, fluid in stations.values():
        station = (_ring.seat(), (x, floor, z))
        cut, lettering = _ring.split(import_step(str(_ring.STEPS[which])).val())
        chip, _carry = seat_body(cut, (), seat=ring_name(which), station=station)
        word, _wcarry = seat_body(lettering, (), seat=word_name(which), station=station)
        out.append((ring_name(which), chip,
                    cq.Color(*(c / 255.0 for c in _rear.chip_color(fluid)))))
        out.append((word_name(which), word,
                    cq.Color(*(c / 255.0 for c in _rear.word_color(fluid)))))
    return out


# --- the nameplate, in the field the port row leaves east of the flavour chips ---
#
# A plate lying flush in a pocket of this same wall, held by two M3 cap screws. The pocket and
# the plate are `bulkhead_ring`'s construction at another size; what the screws need is depth behind
# the wall, and that is the one thing this face is short of.
#
# WHAT THE WALL LEAVES IT is a rectangle on three struck edges: the flavour pair's own pocket
# edge west, the flat rear face's tangent east, and the top row's pockets north. The fourth is
# the back column's Z seam, which the box searches — so the plate is stood off the other three
# and `nameplate-field` reads it back against the seam once the box is standing.
NAMEPLATE_MARGIN = 5.0
# What a boss keeps off the cold core's cap, on the radius. `nameplate.boss_stem_d` is the part
# of the boss that reaches deep, so it is that one and not the collar the line is struck on.
NAMEPLATE_BOSS_CLEAR = 1.5
# The two bodies the plate goes into the assembly under — the part and the filament lying in it.
NAMEPLATE = "nameplate"
NAMEPLATE_INK = "nameplate-ink"
def nameplate_field() -> tuple:
    """The rectangle the wall leaves the plate, as `(west, east, north)`.

    West is the flavour pair's own POCKET edge, not its chip's — what stands on the wall there is
    the pocket. East is the flat rear face's tangent, the same plane `c14_flat_column` runs the
    inlet's flange out on. North is the top row's pockets, read on the deck's own storey."""
    return (PANEL_X["bulkhead-flavor-a"] + port_pocket_d() / 2.0,
            _enc.interior_x()[1] - (_enc.corner_round - _enc.wall),
            deck_storey() - port_pocket_d() / 2.0)


def nameplate_screw_line(foam) -> float:
    """The Z both screws stand on: the lowest a boss can, over the cold core's own cap.

    The plate's boss reaches `nameplate.boss_reach` inboard and the core's foam stands
    `enclosure.wall` off this wall for the whole of the field below — so a boss over the cap is a
    boss in the core. This is the cap's face, half a stem, and the air past it."""
    return cap_face(foam) + _np.boss_stem_d() / 2.0 + NAMEPLATE_BOSS_CLEAR


def nameplate_station(foam) -> tuple:
    """The plate's own centre on the wall, as `(x, z)` — centred across the field, and standing
    ON the screw line, which is what puts its two screws at mid-height."""
    west, east, _north = nameplate_field()
    return ((west + east) / 2.0, nameplate_screw_line(foam))


def nameplate_cut(foam) -> _enc.Nameplate:
    """Everything the wall does for the plate, as `enclosure.Box.nameplate`."""
    x, z = nameplate_station(foam)
    return _enc.Nameplate(x, z, _np.WIDTH, _np.HEIGHT, _np.CORNER_R, _np.BEVEL, _np.SLIP,
                          _np.THICK, _np.WALL, _np.screw_stations(),
                          _np.boss_stem_d(), _np.boss_reach(),
                          _enc.heatset_dia, _enc.heatset_depth + _np.bore_relief())


def build_nameplate(foam, unit: int = 1):
    """The plate and its lettering, two solids, seated on the pocket's own floor — one plate's
    thickness inside the wall's outer face, so its face and the wall's come out one plane."""
    x, z = nameplate_station(foam)
    floor = _enc.rear_plane_y + _enc.wall - _np.THICK
    plate, ink = _np.split(import_step(str(_np.step_path(unit))).val())
    body, _c = seat_body(plate, (), seat="nameplate", station=(_np.seat(), (x, floor, z)))
    letters, _w = seat_body(ink, (), seat="nameplate-ink",
                            station=(_np.seat(), (x, floor, z)))
    return ((NAMEPLATE, body, cq.Color(*(c / 255.0 for c in _rear.chip_color("flavor")))),
            (NAMEPLATE_INK, letters,
             cq.Color(*(c / 255.0 for c in _rear.word_color("flavor")))))


def check_nameplate(foam, box) -> Bound:
    """The plate against the field the wall leaves it, and its screws against the line the cold
    core's cap leaves them.

    `nameplate.WIDTH` and `HEIGHT` are the part's own figures — it is sized on the type it
    carries — and the field is this wall's. This is where the two are read against each other."""
    west, east, north = nameplate_field()
    seam = box.splits[1]
    x, z = nameplate_station(foam)
    rows = []
    room = east - west - 2.0 * NAMEPLATE_MARGIN
    if _np.WIDTH > room + 1e-6:
        rows.append(f"the plate is {_np.WIDTH:g} across and the field between the flavour "
                    f"pockets and the flat face's tangent leaves {room:.2f} inside its margins")
    low = z - _np.HEIGHT / 2.0
    if low < seam + NAMEPLATE_MARGIN - 1e-6:
        rows.append(f"the plate's foot lands at z {low:.2f} and the back column's seam is at "
                    f"{seam:.2f} — a plate crossing it is two prints")
    high = z + _np.HEIGHT / 2.0
    if high > north - NAMEPLATE_MARGIN + 1e-6:
        rows.append(f"the plate's head reaches z {high:.2f} and the top row's pockets come down "
                    f"to {north:.2f} — the two would meet with no wall between them")
    return record_bound(Bound(
        "nameplate-field", "The plate stands in the field this wall leaves it", not rows,
        f"{_np.WIDTH:g} x {_np.HEIGHT:g} at ({x:.2f}, {z:.2f}), z {low:.2f}..{high:.2f}",
        f"inside x {west:.2f}..{east:.2f}, z {seam:.2f}..{north:.2f}", rows))


# --- the panel deck: the three unions the machine dispenses through ---------
#
# Everything the customer draws leaves by these: carbonated water to the faucet, and the two
# flavour lines to their flavour mouths. All three cross the +Y wall of back-top on ONE STOREY.
#
# Below that storey the cold core reaches nearly to the +Y wall of back-top, and what it leaves there is
# less than
# `jg_bulkhead_union.far_ring_face_y` — a union seated on that band has its collet inside the
# foam. The +X flank is the power block and the C14, floor to ceiling. The pump fills the middle
# to its own crown. What is left is the band OVER THAT CROWN and under the top wall, and it is
# open from the west boss chain across to the C14's own corner — one room, wall to wall. THE GAS
# CHAIN STANDS IN IT, on the column past the carb union's; `CO2_COLUMN` is where. Re-read the room
# by sweeping the union's own body over the wall:
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
# TWO DEMANDS STAND ON ONE PITCH, and the column takes the wider of them.
#
# What the HARDWARE asks, read at the nut on the inboard side: each fitting's own panel
# footprint, the gap two nuts need, and what the bodies hanging off them ask for over that.
PORT_HARDWARE_PITCH = _jg.panel_footprint()[0] + PORT_NUT_GAP + PORT_DECK_EXTRA
# What the FIELD asks, read on the face the customer meets, where it is pockets cut side by side
# in one wall and not nuts: a whole pocket, and one rim's width of standing wall past it.
PORT_FIELD_PITCH = port_pocket_d() + BULKHEAD_RING_RIM
# The pitch two columns stand at.
PORT_PITCH = max(PORT_HARDWARE_PITCH, PORT_FIELD_PITCH)
# WHAT THE PITCH LEAVES BETWEEN TWO POCKETS IS STANDING WALL, and a pocket that runs into its
# neighbour leaves one colour touching the next with nothing printed between them. `bulkhead_ring.RING_W`
# is what a chip spends the pitch on and `BULKHEAD_RING_RIM` is the wall the field keeps around it, so
# the three are read against each other here rather than in any one module alone. The two union
# columns are the tightest pair on the wall — both pockets take the same width — so the pitch is
# read against that one.
PORT_FIELD_WEB = PORT_PITCH - port_pocket_d()
_stated.state(
    "port-field-web", "Two neighbouring pockets leave standing wall between them",
    f"a web of {BULKHEAD_RING_RIM:g} mm or more, one rim's own width",
    PORT_FIELD_WEB >= BULKHEAD_RING_RIM - 1e-9,
    f"one PORT_PITCH of {PORT_PITCH:.2f} carries a pocket of {port_pocket_d():.2f} — a chip of "
    f"Ø{_ring.od('union'):.2f} and its {BULKHEAD_RING_SLIP:g} slip — and leaves "
    f"{PORT_FIELD_WEB:.3f} mm of wall between two of them. `bulkhead_ring.RING_W` "
    f"{_ring.RING_W:g} is what a chip shows past the fitting's own flange, and shrinking it is "
    f"what buys the web back.")
# AND THE POCKET STOPS INSIDE THE WALL. It is cut the chip's own thickness into a face that has
# only `enclosure.wall` to give, and what is left under it is the floor every flange's load
# crosses. Cut to the full thickness there is no floor, the pocket is a hole, and the boss standing
# inboard is holding the fitting on its own.
_stated.state(
    "port-pocket-floor", "Every pocket leaves wall under the chip it holds",
    f"a chip under `enclosure.wall` {_enc.wall:g} mm",
    _ring.THICK < _enc.wall - 1e-9,
    f"the pocket is cut {_ring.THICK:g} mm into a wall {_enc.wall:g} mm thick and leaves "
    f"{_enc.wall - _ring.THICK:.2f} mm of floor under the chip.")
# AND THE CLAMPED STACK IS WALL PLUS RING, at every station on this wall. Each fitting states how
# much of its own barrel stands bare between flange and nut, and that is the whole of what the
# stack may take — the one figure a thicker wall or a thicker ring spends.
#
# AND THE WALL IS NOT ONE FIGURE ANY MORE. back-top carries `enclosure.back_top_wall_t` and the
# CO2's own station is relieved back to `enclosure.wall` for exactly this reason, so what a
# fitting spends is the section at ITS station and not the box's thinnest or its thickest.
# `enclosure.back_wall_t_at` is that reading; `check_wall_clamped` takes it again at the placed
# station, which is what catches a relief that has drifted off the hole it was cut for.
_port_stack = _stated.bound(
    "port-clamp-stack", "Every fitting's bare barrel takes the wall and its ring",
    f"a stack of the wall at its own station plus {_ring.THICK:g} mm of ring")
for _n, (_fit, _r, _w, _f) in Y_WALL_FITTINGS.items():
    _bare = getattr(_fit, "PANEL_THREAD", None) or _fit.THREAD_LEN
    _relieved = {_r[0] for _r in _enc.back_top_wall_reliefs}
    _t = _enc.wall if _n in _relieved else _enc.back_top_wall_t
    _port_stack(_t + _ring.THICK <= _bare + 1e-9,
                f"{_n} offers {_bare:.2f} mm of bare barrel and the wall it passes and its ring "
                f"stack {_t + _ring.THICK:g} mm, leaving the nut none of it")
def west_interior_face():
    """The −X wall's own inner face, off the stated width — the same face `enclosure._dims`
    builds the box on."""
    return _enc.interior_x()[0]


def west_exterior_face():
    """And that wall's OUTER face — the machine's own skin on this flank, one `enclosure.wall`
    further west. It is the plane the ASSE drip pan's pull stands proud of (`pan_west_x`)."""
    return west_interior_face() - _enc.wall


def west_seam_crown():
    """What actually fences the west lane at the +Y wall of back-top: the crown of the seam's own boss
    chain, one `enclosure.boss_in` inboard of that face.

    THE WALL IS NOT THE FENCE THERE. `enclosure.boss_in` is how far the rear seam's own socket
    collar reaches inboard on this flank, and at the +Y wall of back-top — which is exactly where the
    unions cross it, at the height that collar stands — the collar is what a body on the west
    lane meets first. A lane measured to the bare face reports fourteen millimetres that are
    not there."""
    return west_interior_face() + _enc.boss_in


# THE WEST LANE CARRIES TWO COLUMNS AND EVERY UNION IS ON ONE OF THEM. The lane runs from the
# seam column's crown to the pump's casting, and the two flavour unions stand side by side across
# it at `PORT_PITCH` — so `check_port_pair` is where that span is measured, against the column on
# one flank and the casting on the other.
#
# THE EAST COLUMN IS THE ONE THE PUMP FENCES. It stands as far east as the casting leaves it at
# the flavour storey, and the west column takes one pitch beyond that. Swept over the wall by
# dropping the union's own body down the lane:
#
#     enclosure_assembly.pump_west_face(seaflo, z0, z1, bulkhead_mouth_y(), rear_plane_y)
PORT_LANE_CLEAR = 1.0
# THE WEST COLUMN IS STRUCK, NOT CHOSEN. What fences this lane on that flank is not the −X wall
# but the seam's own furniture standing off it — `west_seam_crown` — and a union clamped through
# the +Y wall of back-top reaches its widest at the flange. So the column is that crown, one
# `PORT_LANE_CLEAR`, and half a flange: the narrowest lane the rule allows, and no number of its
# own. Every body on it follows — the tap-water union stands on the ASSE chain's inlet and the
# chain on this column, so what the wall gives the flavour pair it gives the storey above too.
#
# THE EAST COLUMN IS WHERE THE TWO OF THESE LEAVE IT. This and `PORT_DECK_EXTRA` both reach it —
# one as the origin the pitch is measured from, the other as a term of that pitch — so the
# storey's east column stands at `PORT_WEST_COLUMN + PORT_PITCH` and reading it off the pair is
# how a change to either is checked against the flank the pump fences.
PORT_WEST_COLUMN = west_seam_crown() + PORT_LANE_CLEAR + _jg.BODY_D / 2.0
PANEL_X = {"bulkhead-flavor-b": PORT_WEST_COLUMN,
           "bulkhead-flavor-a": PORT_WEST_COLUMN + PORT_PITCH,
           "bulkhead-carb": PORT_WEST_COLUMN + PORT_PITCH}
# What a union's barrel keeps off the pump's BRACKET where the two pass. The feet are the widest
# section the casting has and they are only `seaflo_22_pump.FOOT_T` tall — above them the casting
# steps back across the machine and the port lane opens by twenty millimetres. So a barrel
# carried over the feet has the lane and one struck through them does not.
PORT_FOOT_CLEAR = 1.0


def flavor_storey(gate: float, seaflo) -> float:
    """The storey the two flavour unions cross the wall on: their own runs' cruise lane, or the
    plane that carries their barrels over the pump's bracket, whichever is higher."""
    return max(gate, box(seaflo).zmin + _lines._pump.FOOT_T
               + PORT_FOOT_CLEAR + _jg.BODY_D / 2.0)
# THE WEST COLUMN CARRIES THE TAP WATER UNION TOO, one storey up: the chain, the split, the
# regulator and the ASSE drip pan under the vent all hang off that union, and the column is what
# stands them in the lane.
#
# THE STOREY THE FLAVOUR UNIONS TAKE IS THEIR OWN RUNS'. `_lines.gate_cruise` is the plane the
# west gate climbs to under the reservoir line crossing its column, and it is the plane both runs
# arrive on: `fluid-28` cruises its union's own column onto it and `fluid-18` comes down that
# column onto it, so each run's last move into its collet is flat. `flavor_storey` then carries
# both barrels clear over the pump's bracket, and what the runs spend on that is one short lean
# apiece at the aft end.
PANEL_ON_GATE_LANE = ("bulkhead-flavor-b", "bulkhead-flavor-a")


def check_port_pair(placed, west_face, seaflo) -> Bound:
    """The two flavour unions across the west lane, measured against the two things that fence it:
    the seam column's crown on one flank and the pump's own casting on the other, read at the
    storey the pair stands on.

    `west_seam_crown` and not the wall, because the wall is not what the pair meets there."""
    pair = [box(placed[n]) for n in PANEL_ON_GATE_LANE]
    lo, hi = min(b.xmin for b in pair), max(b.xmax for b in pair)
    face = pump_west_face(seaflo, min(b.zmin for b in pair), max(b.zmax for b in pair),
                          bulkhead_mouth_y(), _enc.rear_plane_y)
    left, right = lo - west_face, face - hi
    got = min(left, right)
    ok = got >= PORT_LANE_CLEAR - 1e-6
    return record_bound(Bound(
        "port-pair", "The flavour unions' pair stands inside the west lane", ok,
        f"{left:.3f} mm to the seam column, {right:.3f} mm to the casting",
        f"{PORT_LANE_CLEAR:g} mm each flank",
        ([] if ok else [
            f"the flavour pair spans x[{lo:.2f}, {hi:.2f}] between a column at {west_face:.2f} and "
            f"the pump's casting at {face:.2f} — {got:.3f} mm on its tightest flank. The span is "
            f"one `PORT_PITCH` plus a barrel; move `PANEL_X`'s two flavour columns, or give the "
            f"pair back the width by moving the pump."])))


def check_top_row(stations) -> Bound:
    """The top row's chips run out FLUSH with the box's own top face.

    `bulkhead_ring.RISE` is how far a chip stands over its bore axis, and it is not a figure that
    module can derive: it is this row's own storey read against the ceiling, and the two modules
    cannot import each other. So it is stated there and read back here, off the stations the wall
    was actually bored on. Every chip takes it, and this is the row it answers to.

    Struck short, a strip of wall stands over the colour too thin for a nozzle to lay. Struck long,
    the pocket cuts up into the top wall past the face it runs out on."""
    top = interior_ceiling() + _enc.wall
    rows = []
    for name, (_x, z, _fitting, _ring_family, which, _fluid) in stations.items():
        if not _ring.STATIONS[which].top_row:
            continue
        got = z + _ring.RISE
        if abs(got - top) > 1e-3:
            rows.append(
                f"{name}'s chip reaches z {got:.3f} and the box's top face is {top:.3f} — "
                f"`bulkhead_ring.RISE` is {_ring.RISE:g} and this row is bored on {z:.3f}, so that "
                f"figure owes {top - z:.3f}.")
    return record_bound(Bound(
        "bulkhead-ring-top-row", "The top row's chips run out on the box's top face", not rows,
        f"{sum(1 for _n, s in stations.items() if _ring.STATIONS[s[4]].top_row)} chips flush "
        f"at z {top:.3f}", "no wall standing over the colour", rows))


def check_nameplate_pocket(plate, pieces, foam) -> Bound:
    """The pocket the wall CUT against the pocket the plate needs, read off the two solids.

    `pack-closes` catches a pocket that is too SMALL — the plate cannot get into it, so the two
    share volume. Nothing catches one that is too LARGE: a plate rattling in a pocket ten
    millimetres too tall overlaps nothing, seats nowhere in particular, and every other reading
    on this card comes back green. That is the case this one is here for.

    THE READING IS THE POCKET'S OWN FOUR EDGES, taken at the MOUTH. The wall stands where the
    plate's outline is not and gives way where it is — so each edge is asked twice, a hair
    outside and a hair inside. A pocket cut to the wrong figure fails on whichever pair of probes
    it moved past. It is read on the straight rim rather than at mid-thickness because deeper in
    the pocket is the chamfer, where the outline is not the outline yet."""
    wall = pieces.get("back-top")
    if wall is None or plate is None:
        return record_bound(Bound(
            "nameplate-pocket", "The wall's pocket is the plate's own outline", False,
            "no wall to read" if wall is None else "no plate to read", "both standing",
            ["the nameplate or `enclosure-back-top` is not in this machine"]))
    wall = wall.val() if hasattr(wall, "val") else wall
    plate = plate.val() if hasattr(plate, "val") else plate
    x, z = nameplate_station(foam)
    y = _enc.rear_plane_y + _enc.wall - (_np.THICK - _np.BEVEL) / 2.0
    half_w = (_np.WIDTH + 2.0 * _np.SLIP) / 2.0
    half_h = (_np.HEIGHT + 2.0 * _np.SLIP) / 2.0
    # A probe small enough to sit inside the slip, offset by its own reach either side of an edge.
    reach = 0.5

    def stands(px, pz) -> bool:
        cube = cq.Solid.makeBox(0.4, 0.4, 0.4, cq.Vector(px - 0.2, y - 0.2, pz - 0.2))
        return _overlap.volume(cube, wall) > 1e-9

    rows = []
    for name, out, inn in (
            ("west", (x - half_w - reach, z), (x - half_w + reach, z)),
            ("east", (x + half_w + reach, z), (x + half_w - reach, z)),
            ("foot", (x, z - half_h - reach), (x, z - half_h + reach)),
            ("head", (x, z + half_h + reach), (x, z + half_h - reach))):
        if not stands(*out):
            rows.append(f"the wall gives way {reach:g} mm OUTSIDE the plate's {name} edge — the "
                        f"pocket is cut wider than the plate that lies in it")
        if stands(*inn):
            rows.append(f"the wall stands {reach:g} mm INSIDE the plate's {name} edge — the "
                        f"pocket is cut narrower than the plate that lies in it")
    return record_bound(Bound(
        "nameplate-pocket", "The wall's pocket is the plate's own outline", not rows,
        f"{_np.WIDTH:g} x {_np.HEIGHT:g} and one {_np.SLIP:g} slip, on all four edges",
        "wall outside every edge, air inside it", rows))


def check_wall_clamped(bodies, rings, pieces, stations) -> Bound:
    """Whether each rear-wall fitting is CLAMPED THROUGH the wall, read off the placed solids.

    This is the reading that makes `wall-capture` a mount and not a word. A fitting drawn in front
    of a hole and a fitting clamped through one are the same to every other row on this card: the
    bore is bored either way, the pad stands either way, and `port-clamp-stack` holds a stack of
    stated figures that the machine may not actually be built to. Two numbers tell them apart, and
    both are the joint itself:

        bear   the flange against the RING lying in its pocket. A clamp has a bearing face, and
               this is it — the ring bottoms on the wall's own outer face, so the flange's load
               crosses ring and wall together and the ring is in the stack the way the wall is.
        slip   the barrel against the WALL it passes. One `PORT_HOLE_SLIP` on the diameter is a
               barrel standing in its own bore; anything wider is a fitting hanging in a hole, and
               anything closed is a barrel fouling the wall it is meant to pass freely.

    THE SLIP IS READ IN THE STATION'S OWN COLUMN, not against the whole piece. A wall this full
    carries furniture that comes nearer a fitting than its own bore does — the west column's two
    unions pass within a tenth of a millimetre of what stands off the −X wall — so a reading taken
    against `enclosure-back-top` entire reports that neighbour and not this joint. The column is
    the pad's own footprint carried through wall and pad, so what is left in it is the bore, its
    pocket and nothing else.

    What the nut does is not read here — it is not modelled, and `port-clamp-stack` is where the
    barrel it runs down is held against the stack these two numbers measure."""
    def solid(s):
        s = s.toCompound() if hasattr(s, "toCompound") else s
        return s.val() if hasattr(s, "val") else s
    wall = pieces.get("back-top")
    want = PORT_HOLE_SLIP / 2.0
    rows, worst_bear, tight = [], 0.0, want
    # `_kind` and not `_ring`: the module of that name is what `THICK` is read off below,
    # and a loop target shadows it for the whole function.
    for name, (_fitting, _kind, which, _fluid) in Y_WALL_FITTINGS.items():
        body, ring = bodies.get(name), rings.get(ring_name(which))
        if body is None or ring is None or wall is None:
            rows.append(f"{name}: no {'fitting' if body is None else 'ring'} to read")
            worst_bear = max(worst_bear, 1.0)
            continue
        x, z, _fit, ring_kind, _which, _f = stations[name]
        column = cq.Solid.makeCylinder(
            port_boss_d(ring_kind) / 2.0, _enc.wall + PORT_BOSS_PROUD + 2.0,
            cq.Vector(x, _enc.rear_plane_y - PORT_BOSS_PROUD - 1.0, z), cq.Vector(0, 1, 0))
        bear = _clearing.gap(solid(body), solid(ring), 5.0)
        slip = _clearing.gap(solid(body), solid(wall).intersect(column), 5.0)
        worst_bear, tight = max(worst_bear, bear), min(tight, slip)
        if bear > 1e-3:
            rows.append(
                f"{name}'s flange stands {bear:.3f} mm off `{ring_name(which)}` and bears on "
                f"nothing. A fitting that does not land on its ring is not clamping the wall "
                f"through it — either the ring's pocket is deeper than the ring, or the fitting's "
                f"seat plane no longer reads `bulkhead_seat_y`.")
        if abs(slip - want) > 1e-2:
            rows.append(
                f"{name}'s barrel stands {slip:.3f} mm off the wall in its own column, where its "
                f"bore is struck one `PORT_HOLE_SLIP` over it — {want:.3f} on the radius. Either "
                f"the bore is no longer the barrel's, or the fitting is off the column "
                f"`wall_stations` bored on.")
        # AND THE SECTION IT ACTUALLY PASSES, read where the pack put it. `port-clamp-stack`
        # states this off the relief's own figures; this takes it again at the placed station,
        # so a relief that has drifted off the hole it was cut for reads here rather than
        # nowhere — the wall would simply be thicker than the barrel can clamp.
        bare = getattr(_fitting, "PANEL_THREAD", None) or _fitting.THREAD_LEN
        stack = _enc.back_wall_t_at(x, z) + _ring.THICK
        if stack > bare + 1e-9:
            rows.append(
                f"{name} passes {_enc.back_wall_t_at(x, z):.2f} mm of wall at its own station "
                f"(x {x:.2f}, z {z:.2f}) and stacks {stack:.2f} mm with its ring, against "
                f"{bare:.2f} mm of bare barrel — the nut has none of it. Either the wall is "
                f"thicker here than this fitting can clamp, or `enclosure.back_top_wall_relief` "
                f"no longer stands on this hole.")
    return record_bound(Bound(
        "wall-clamped", "Every rear-wall fitting is clamped through the wall it passes", not rows,
        f"{len(Y_WALL_FITTINGS)} clamped, furthest off its ring {worst_bear:.3f} mm, "
        f"tightest in its bore {tight:.3f} mm",
        f"bearing at 0.000 mm and {want:.3f} mm of bore", rows))


def panel_z(name: str, deck: float, gate: float) -> float:
    """The storey one union of the row crosses the wall on — the deck, or its own run's lane."""
    return gate if name in PANEL_ON_GATE_LANE else deck


def build_panel_bulkhead(name: str, x: float, z: float):
    """One union clamped through the +Y wall of back-top on `(x, z)`, seated on its INBOARD COLLET.

    The same fitting and the same seating as the tap-water union: the flange bears on the wall's
    outer face, the threading passes through, and the nut clamps inside. What it reaches inboard
    is `jg_bulkhead_union.far_ring_face_y`, and `bulkhead_mouth_y` is where that leaves the
    collet the run pushes into."""
    body = import_step(str(BULKHEAD_STEP)).val()
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
# main board it plugs into stands on the +X flank.
DIGITEN_STEP = _hw / "reference" / "digiten-flow-sensor" / "digiten-flow-sensor.step"
DIGITEN_TURN = (((0.0, 0.0, 1.0), 90.0), ((0.0, 1.0, 0.0), 90.0))
# The straight between the meter's outlet and the union's inboard collet — `carb-2`, which has no
# corner in it for the same reason `water-2` has none: two collets facing each other down one
# axis seat no arc, and what the gap has to be is enough tube for both to take hold of.
CARB_2 = 22.0


def build_digiten(carb_carry, seat: bool = True):
    """The meter seated on its OUTLET, one `CARB_2` forward of the carb union's inboard collet
    and on that collet's own column and plane.

    A fitting answers to its mouth: both ends of this body are collets, and the one that has to
    land in the right place is the one the union is waiting on. Where the inlet ends up is
    `digiten_flow_sensor.port_face` ahead of the body centre, and that is where `carb-1` closes.

    The two anchors it hangs in are `digiten_anchors`, printed off the top wall."""
    pos, axis = carb_carry(_jg.port(-1.0))
    target = tuple(pos[i] + axis[i] * CARB_2 for i in range(3))
    body = import_step(str(DIGITEN_STEP)).val()
    return seat_body(body, DIGITEN_TURN, seat="digiten-flow" if seat else None,
                     station=(_digiten.outlet(), target))


# --- the anchors the meter hangs in ----------------------------------------
#
# TWO ANCHORS OFF THE TOP WALL, ONE PER ARM, AND NOTHING OVER THE BODY. The meter is a round
# ⌀26 body with a ⌀12 collet barrel out of each rim, and the body is the part with no room: it
# reaches to within `DECK_CEILING_CLEAR` and change of the top wall, while the barrels leave the
# best part of a centimetre. So the arms are what a anchor can reach, and each takes the same 120°
# V the ASSE anchor takes, read off a round section's tangent — apex up, opening down.
#
# WHAT THE ZIP TIE CARRIES HERE IS THE METER. A V that opens downward holds nothing on its own, so
# unlike the anchor's two ties these are the load path, and what they carry is a purchased part of
# a few tens of grams on two nylon zip ties.
DIGITEN_SEAT_SLIP = 0.2
# Off the body's own rim. The rim is a circle in plan, so it stands closest to a anchor at the
# arm's own column and falls away either side of it; this is struck on the closest.
DIGITEN_BODY_CLEAR = 1.0
# HOW MUCH OF EACH BARREL IS LEFT ALONE at its outer end. That end is a push-fit collet: a tube
# goes into it and the ring that lets the tube back out is on the face. A anchor over that ring is
# a joint that cannot be broken without cutting the zip tie first.
DIGITEN_COLLET_FREE = 6.0


def digiten_anchors(carry) -> tuple:
    """The station `enclosure._flow_meter_anchors` builds from — `(axis_x, axis_z, seat_r, bands)`.

    `seat_r` is the barrel the V is struck on, one `DIGITEN_SEAT_SLIP` over its own radius, so the
    anchor stands off the arm by that slip on the V's own normal. `bands` is the run of each arm a
    anchor takes: from the body's rim out to where the collet's ring begins, which is the whole of
    the barrel that is neither the body nor the joint."""
    axis = carry(_digiten.inlet())[0]
    rim = _digiten.body_dia / 2.0
    r = _digiten.port_dia / 2.0
    bands = []
    for port in (_digiten.inlet, _digiten.outlet):
        face, out = carry(port())
        # `out` points out of the collet, so the barrel runs INBOARD from that face — both ends of
        # the band are struck against it.
        inner_end = face[1] - out[1] * (_digiten.port_face - rim - DIGITEN_BODY_CLEAR)
        outer_end = face[1] - out[1] * DIGITEN_COLLET_FREE
        bands.append(tuple(sorted((inner_end, outer_end))))
    return (axis[0], axis[2], r + DIGITEN_SEAT_SLIP, tuple(bands))


# --- the tube anchors -------------------------------------------------------
#
# WHAT A RUN DOES BETWEEN ITS TWO COLLETS. It is pushed into a fitting at each end and held by
# nothing in between, so a long one sags — and a run that sags is not on the centreline
# `lines-clear` cleared it on. An anchor is a stop on that span.
#
# The span an anchor breaks. A tube carrying its own weight and its water sags `5wL⁴/384EI`
# between supports; for 1/4" LLDPE that reaches the millimetre `clearance-floor` keeps somewhere
# in 181..284 mm, over the stock's modulus range with creep allowed for and on pinned ends. A
# collet gripping ten millimetres of straight is stiffer than pinned.
TUBE_ANCHOR_SPAN = 200.0
# The V stands off the tube by this on its own normal, the same slip the meter's anchors take.
TUBE_ANCHOR_SLIP = 0.2
# A run over the span needs an anchor; a run with a printed face within reach of a straight length
# of it can have one. Most of this machine's long runs cruise through the pack with no piece near
# enough to reach them.
#
# Each row is a run, the index of the leg the rib is centred on, the face it roots on, and the
# piece that owns that face there. `check_tube_seated` reads the last of those back off the two
# solids, so a rib that lands in a different piece than its row names is a red row and not a
# silent one.
TUBE_ANCHOR_SITES = (
    # The carb-water line's crossing, under the top wall it runs 12.6 mm below for 123 mm. THE
    # WALL THERE IS THE SLIDE-IN CEILING PANEL and not back-top: back-top keeps only the two side
    # strips of its ceiling, so a rib rooted over the field between them roots on the panel
    # (`enclosure.ceiling_stations`, which is what splits the stations between the two).
    ("carb-1", 1, (0.0, 0.0, 1.0), "enclosure-ceiling-panel"),
    # And the gas line's, on that same deck and under that same wall, one cap conduit aft of it.
    ("co2-2", 1, (0.0, 0.0, 1.0), "enclosure-ceiling-panel"),
    # Flavor B's cruise aft, off the −X wall it runs 26.4 mm inboard of. That leg is the run's
    # longest and it is dead straight, so the wall lies one distance down the whole of it — and
    # `_lines.GATE_B_STEP_Y` places its MIDDLE, which is where the rib goes, in the one band of
    # that wall neither the tap-water split nor the cluster wells are in.
    ("fluid-28", 2, (-1.0, 0.0, 0.0), "enclosure-back-top"),
)


def tube_anchors(runs) -> tuple:
    """One station per anchor — `(mid, along, root, seat_r)`, all four read off the run itself.

    A LEG AND NOT A POINT. The rib is centred on the middle of the leg its row names, so the
    anchor rides every move of the run that drew it and there is no coordinate here to go stale.
    What the piece adds is the face: `enclosure._tube_anchors` stops the rib on the wall, and
    nothing about the anchor's own height is stated on either side."""
    by_id = {r.id: r for r in runs}
    stations = []
    for rid, leg, root, _piece in TUBE_ANCHOR_SITES:
        r = by_id.get(rid)
        if r is None:
            continue                        # a run whose bodies are not both placed yet
        if leg + 1 >= len(r.pts):
            raise ValueError(
                f"tube_anchors: {rid} has {len(r.pts) - 1} legs and this row names leg {leg}. "
                f"`TUBE_ANCHOR_SITES` names a leg of the route as `_lines` draws it.")
        p, q = r.pts[leg], r.pts[leg + 1]
        length = math.dist(p, q)
        u = tuple((q[k] - p[k]) / length for k in range(3))
        # A LEG NEED NOT BE AXIAL, only square to the face. The rib is extruded along the tube and
        # its two ends are cut square to that, so what it asks of the leg is that the face it
        # roots on lies at one distance down the whole of it — which is the test below and not
        # this one. A leg that leans in the plane of its own wall passes both.
        if abs(sum(u[k] * root[k] for k in range(3))) > 1e-9:
            raise ValueError(
                f"tube_anchors: {rid} leg {leg} runs along {u} and this row roots it on {root}. "
                f"An anchor stands ACROSS its tube, never off the face the tube points at.")
        if length < _enc.tube_anchor_len:
            raise ValueError(
                f"tube_anchors: {rid} leg {leg} is {length:.2f} mm and a rib is "
                f"{_enc.tube_anchor_len:.2f}. A seat longer than the straight it stands on would "
                f"close on the corners either side of it.")
        stations.append((tuple((p[k] + q[k]) / 2.0 for k in range(3)), u, tuple(root),
                         r.diam / 2.0 + TUBE_ANCHOR_SLIP))
    return tuple(stations)


# --- the anchors a BODY hangs in --------------------------------------------
#
# THE SAME RIB, BORED FOR A FITTING INSTEAD OF A TUBE. `enclosure._tube_anchors` is handed an
# axis, a direction along it and a radius, and knows nothing about what is on that axis — so a
# round section of a placed body is a station like any other.
#
# A ROW NAMES the body, the section of it the seat closes on, the face the rib roots on, and the
# piece that owns that face. `check_body_seated` reads the last of those back off the two solids.
BODY_ANCHOR_SLIP = 0.2
BODY_ANCHOR_SITES = (
    # The regulator's barrel, between its two wrench hexes — off the ceiling, which over this
    # field is the slide-in panel's and not back-top's.
    ("wr1110", _wr1110.barrel, (0.0, 0.0, 1.0), "enclosure-ceiling-panel"),
    # THE FLAVOUR TAP'S OWN TWO, one over the other on one column off the −X wall. The split and
    # the regulator stand on one vertical with a hairpin joining them, and each takes a rib on the
    # run between its hub and the collet the tap arrives by — the one round section on either body
    # that is neither a box, a branch, nor the adjuster a hand has to reach.
    #   ONE FACE TAKES BOTH AND TWO PIECES BUILD THEM. The pair's axes are parallel and level in
    # X, so a rib off this face stands across each run the same way — but the tap runs forward
    # across the Y seam, and a piece builds only the ribs whose whole length it owns. The split is
    # aft of the seam and the regulator forward of it, so each seat prints on the piece its own
    # body stands in and the two are one column of material across the joint.
    ("water-split", _split.run_barrel, (-1.0, 0.0, 0.0), "enclosure-back-top"),
    ("flow-regulator", _flowreg.run_barrel, (-1.0, 0.0, 0.0), "enclosure-back-top"),
)


def body_anchors(carries) -> tuple:
    """One station per body anchor — `(mid, along, root, seat_r)`, the shape `_tube_anchors`
    builds a rib from, all of it read off the body's own section.

    THE SECTION IS THE REFERENCE MODULE'S, and that module holds it to the file the pack seats.
    So the seat rides every move of the body, and there is no radius stated here to go stale.

    THE RIB LIES INSIDE ITS SECTION. A run is one radius its whole length and a fitting is not: a
    rib longer than the barrel it is bored for closes on the hex next to it, which is a wrench
    flat clocked by a made-up thread."""
    stations = []
    for name, section, root, _piece in BODY_ANCHOR_SITES:
        carry = carries.get(name)
        if carry is None:
            continue                        # a body that is not placed yet
        station, r, length = section()
        mid, u = carry(station)
        if abs(sum(u[k] * root[k] for k in range(3))) > 1e-9:
            raise ValueError(
                f"body_anchors: {name}'s section runs along {u} and this row roots it on {root}. "
                f"An anchor stands ACROSS the body, never off the face the body points at.")
        if length < _enc.tube_anchor_len:
            raise ValueError(
                f"body_anchors: {name}'s section is {length:.2f} mm and a rib is "
                f"{_enc.tube_anchor_len:.2f}. A seat longer than the section it bears on closes "
                f"on whatever is either side of it.")
        stations.append((tuple(mid), tuple(u), tuple(root), r + BODY_ANCHOR_SLIP))
    return tuple(stations)


def check_body_seated(bodies, pieces) -> Bound:
    """Whether every body-anchored fitting is up in the rib its row names, off the placed solids.

    The reading `check_digiten_seated` takes, on a bore rather than a V — so the gap it holds is
    the slip itself, with no angle in it. And like the meter's anchors this seat opens DOWNWARD:
    what it says is that the zip tie has the body to pull up against and the bore to pull it into,
    not that the rib is carrying it.

    It reads back WHICH piece, the same way `check_tube_seated` does: a rib is built by whichever
    piece owns the whole of it, and a body seated against a piece its row does not name is a body
    whose rib landed somewhere else."""
    def solid(s):
        s = s.toCompound() if hasattr(s, "toCompound") else s
        return s.val() if hasattr(s, "val") else s
    want = BODY_ANCHOR_SLIP
    rows, worst = [], 0.0
    for name, _section, _root, piece in BODY_ANCHOR_SITES:
        body, part = bodies.get(name), pieces.get(piece.removeprefix("enclosure-"))
        if body is None or part is None:
            rows.append(f"{name}: no {'body' if body is None else piece} to read")
            worst = max(worst, want + 1.0)
            continue
        got = _clearing.gap(solid(body), solid(part), 5.0)
        worst = max(worst, got)
        if got > want + 1e-3:
            rows.append(
                f"{name} stands {got:.3f} mm off {piece} and its rib is drawn to close on the "
                f"barrel at {want:.3f}. Either the body moved off the storey the rib roots at, "
                f"or the rib landed in a piece this row does not name.")
    return record_bound(Bound(
        "body-seated", "Every body-anchored fitting lies in its printed rib", not rows,
        f"{len(BODY_ANCHOR_SITES)} anchored, furthest off {worst:.3f} mm",
        f"{want:.3f} mm at most", rows))


def cap_tube_anchors(foam_carry, runs) -> tuple:
    """Every rib the cold core's cap stands for a RUN, as `unsupported_spans` reads a station.

    A row in `_cold_core_interface.cap_anchors` named for a run is one; a row named for a body is
    the chains', and holds nothing this counts. The seat's world axis is the cap's own station
    carried out, and the tube lies along whichever of its legs passes through it."""
    by_id = {r.id: r for r in runs}
    out = []
    for name in _cci.cap_anchors:
        r = by_id.get(name)
        if r is None:
            continue
        mid = foam_carry(cap_anchor(name))[0]
        for i in range(len(r.pts) - 1):
            p, q = r.pts[i], r.pts[i + 1]
            if not _on_leg(mid, p, q, 1e-3):
                continue
            d = math.dist(p, q)
            out.append((mid, tuple((q[k] - p[k]) / d for k in range(3)),
                        (0.0, 0.0, -1.0), _cci.cap_anchors[name].seat_r))
            break
        else:
            raise ValueError(
                f"cap_tube_anchors: the rib for {name} stands at {mid} and no leg of that run "
                f"passes through it. `_cold_core_interface.cap_anchors[{name!r}].centre` is in "
                f"the cap's own frame, and the run is where its two ports put it.")
    # AND THE POSTS THAT GRIP SIDEWAYS. Same reading, one axis over: the seat's root is the core
    # behind it rather than the lid under it, so the station carries −Y where the anchors carry
    # −Z, and the run has to pass through the pipe's own axis just the same.
    for name in _cci.cap_side_anchors:
        r = by_id.get(name)
        if r is None:
            continue
        mid, root = foam_carry(cap_side_anchor(name))
        for i in range(len(r.pts) - 1):
            p, q = r.pts[i], r.pts[i + 1]
            if not _on_leg(mid, p, q, 1e-3):
                continue
            d = math.dist(p, q)
            out.append((mid, tuple((q[k] - p[k]) / d for k in range(3)),
                        tuple(root), _cci.cap_side_anchors[name].seat_r))
            break
        else:
            raise ValueError(
                f"cap_tube_anchors: the side post for {name} stands its pipe at {mid} and no leg "
                f"of that run passes through it. "
                f"`_cold_core_interface.cap_side_anchors[{name!r}]` is in the cap's own frame, "
                f"and the run is where its two ports put it.")
    return tuple(out)


def unsupported_spans(runs, stations) -> dict:
    """The longest stretch of each run that nothing holds — the reading `tube-anchored` grades.

    A run is held at its two ends and wherever an anchor sits on it. Between those points it is
    one continuous elastic member, free to turn at every corner, so what spans is the DEVELOPED
    length from one held point to the next."""
    out = {}
    for r in runs:
        # Each corner's own shortening, taken at the waypoint it turns about, so the stations walk
        # the DEVELOPED length `Run.length` reports and this goal cannot disagree with the card
        # about how long a run is.
        short = {i: 2.0 * r.radii[i] * math.tan(math.radians(turn) / 2.0)
                    - r.radii[i] * math.radians(turn)
                 for i, turn, _li, _lo in r.bends}
        cuts, s = [0.0], 0.0
        for i in range(len(r.pts) - 1):
            s -= short.get(i, 0.0)
            for mid, _u, _n, _seat in stations:
                if _on_leg(mid, r.pts[i], r.pts[i + 1]):
                    cuts.append(s + math.dist(r.pts[i], mid))
            s += math.dist(r.pts[i], r.pts[i + 1])
        if abs(s - r.length) > 1e-6:
            raise ValueError(
                f"unsupported_spans: {r.id} walks to {s:.4f} mm and `Run.length` reports "
                f"{r.length:.4f}. The two read the same polyline and the same arcs.")
        cuts.append(s)
        cuts.sort()
        out[r.id] = max(b - a for a, b in zip(cuts, cuts[1:]))
    return out


def _on_leg(pt, p, q, tol=1e-6) -> bool:
    """Whether `pt` lies on the segment `p..q` — an anchor's own leg and no other."""
    d = math.dist(p, q)
    if d < tol:
        return False
    return abs(math.dist(p, pt) + math.dist(pt, q) - d) < tol


# --- the storey those four stand on ----------------------------------------

def build_deck(z: float, gate: float, seat: bool = False):
    """The four bodies the deck carries off the storey `z`: the three unions across the +Y
    wall of back-top, each on its own `panel_z`, and the meter inline one `CARB_2` ahead of the
    carb one.

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
    rebuilt at each station: it is the same body at every one of them.

    THE PLAN IS ASKED FIRST: a body comes down only on what its own outline covers, so a pair
    whose outlines miss is struck before the first stride."""
    best = None
    for other in under:
        if not _clearing.shadows(body, other):
            continue
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
# anchor the chain lies in (`asse_cradle`), and a tie is a closed loop: the zip tie has to cross
# the chain's top flat, which is the highest thing on this storey. The zip tie is THREADED through
# the anchor's bore and then LAID across this channel — the piece is populated INVERTED on the
# bench, ceiling down, so the zip tie lies on the ceiling's inner face and the chain comes
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
    """The plane the top wall's inner face lies on, off the appliance's own stated height.

    The height is struck from the floor slab's underside, so the cavity is what the stated
    number leaves once the slab and the top wall are both out of it — and the slab is the
    thicker of the two (`enclosure.floor_t`)."""
    return _enc.appliance_height - _enc.floor_t - _enc.wall


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


def deck_storey() -> float:
    """The Z the panel deck lies on, off the ceiling alone.

    The top wall is a stated plane and the tap-water chain's crown is the tallest thing the storey
    carries, so this is arithmetic on two figures and stands before anything is placed. `deck_z`
    is the strike: it takes this and measures the floor under it."""
    return interior_ceiling() - asse_crown_over_axis() - DECK_CEILING_CLEAR


def deck_z(placed, gate: float):
    """The Z the panel deck lies on: the top of the band its own two bounds leave it.

    THE CEILING BINDS AND THE STOREY TAKES IT. Everything hanging off this storey wants the
    height — the chain, the split and the regulator on the chain's own axis, and the ASSE drip pan
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
    z = deck_storey()
    trial = max(box(s).zmax for s in placed) + DECK_CLEAR + _jg.BODY_D / 2.0
    falls = {name: descent(s, _would_land_on(box(s), placed))
             for name, s in build_deck(trial, gate)[0].items()
             if name not in PANEL_ON_GATE_LANE}
    landing = [d for d in falls.values() if d is not None]
    check_deck_floor(z, trial - min(landing) + DECK_CLEAR if landing else None)
    return z, {n: None if d is None else d - (trial - z) for n, d in falls.items()}


# --- the mains inlet, through the +Y wall of back-top --------------------------------
#
# The C14 the customer's cord plugs into. It lands FROM INSIDE — two screws hold its flange
# against the fore face of `enclosure._c14_tunnel`, the block of wall standing round the cutout
# — so its housing stands in the box and only the shroud reaches back out through the hole. Its
# own frame already faces the mating axis down +Y with the seating plane on Y = 0, which is what
# that face gives it, so it takes no turn either.
C14_STEP = _hw / "reference" / "iec-c14-inlet" / "iec-c14-inlet.step"


def c14_flat_column() -> float:
    """The eastmost column the inlet can stand on: the one that leaves its FLANGE — the widest
    thing it has, and the outline the tunnel under it is drawn to — wholly on the wall's own flat
    rear face.

    `enclosure.corner_round` relieves the box's standing verticals for the bed, so the rear face
    is flat only between the two tangents and rolls away to the side walls past them — and where
    a standing vertical carries a COLUMN the flat ends at its cusp instead, further in again.
    `enclosure.wall_flat_from_corner` is whichever of those the wall actually presents. A tunnel
    rooted past it is a tunnel rooted on curve."""
    return (_enc.interior_x()[1] - _enc.wall_flat_from_corner()) - _c14.FLANGE_W / 2.0


# WHERE IT SITS ON THAT WALL IS STRUCK ON BOTH AXES, and neither figure is its own.
#
# THE STOREY IS THE PORT ROW'S. `deck_storey` is the plane the three top-row unions cross this
# wall on, so the inlet crosses it on that same one and the four mating axes the customer meets
# stand on one line — the cord goes in level with the tubes rather than under them.
#
# THE COLUMN IS THE END OF THE FLAT FACE. What the wall carries runs out on its own tangent at
# each end: `PORT_WEST_COLUMN` puts the tap-water chip's edge on the west one, and this puts the
# inlet's flange on the east one. The two ends are not the same distance from the side walls,
# because a chip is Ø`bulkhead_ring.od` and this flange is `iec_c14_inlet.FLANGE_W` — the moulding is
# wider than the chip and eats the difference. The face they both run out on is the shared figure.
C14_STATION = (c14_flat_column(), deck_storey())
# A printed cutout to the moulded shroud that passes it, on each side. It is what the CORD is
# drawn to as well: the tunnel behind this hole is bored to the same rectangle, so the housing
# on the end of the C13 cordset comes down the whole depth of it to reach the blades.
C14_CUTOUT_SLIP = 0.5


def c14_seat_y() -> float:
    """The plane the receptacle's flange bears on — the FORE face of `enclosure._c14_tunnel`,
    and not the +Y wall of back-top's inner face.

    It is struck from the outside in, off the two things that have to stand between that flange
    and the customer: `enclosure.heatset_depth` of insert entering this face from inside the
    machine, and `enclosure.socket_cap` over its blind end. Where the boundary between tunnel and
    wall falls inside that stack does not move the plane — the wall carries the cap and the
    tunnel carries the insert, and the sum is what the receptacle sits behind."""
    x, z = C14_STATION
    return (_enc.rear_plane_y + _enc.wall) - _enc.back_wall_t_at(x, z) - _enc.c14_tunnel_len


def build_c14():
    """The receptacle seated on the tunnel's fore face, its shroud back out through the cutout.

    `iec_c14_inlet` states the seating planes: the flange's outboard face is its own Y = 0 and
    bears on `c14_seat_y`, the housing hangs `BODY_DEPTH` inboard of it, and the shroud rises
    `SHROUD_PROUD` the other way — up the tunnel's whole bore and through the wall behind it."""
    body = import_step(str(C14_STEP)).val()
    return seat_body(body, (), seat="c14-inlet",
                     station=(((0.0, 0.0, 0.0), (0.0, 1.0, 0.0)),
                              (C14_STATION[0], c14_seat_y(), C14_STATION[1])))


def c14_stations():
    """The two heat-set screw stations on the +Y wall of back-top, as `(x, z)` — `enclosure._c14_tunnel`
    bores one into its fore face at each. Both sit ON the mating axis, so the pair follows the
    one station the receptacle is placed at, and the tunnel's own width across X is struck to
    reach them."""
    return tuple((C14_STATION[0] + dx, C14_STATION[1] + dz) for dx, dz in _c14.panel_screws())


def c14_cutout():
    """The rounded rectangle the shroud reaches out through, in `back_ports` shape — struck on
    the same station the body is, one `C14_CUTOUT_SLIP` over the moulding on every side."""
    wx, wz, r = _c14.panel_cutout()
    return ("rect", C14_STATION[0], C14_STATION[1],
            wx + 2 * C14_CUTOUT_SLIP, wz + 2 * C14_CUTOUT_SLIP, r)


# --- the CO2 inlet chain, through the +Y wall of back-top ----------------------------
#
# The customer's cylinder stands beside the machine and its red tether lands here. Three bodies
# on one axis, inline off the wall: the ABU44 bulkhead clamps through it with a collet on each
# face, the GASHER check stands one hop of tube ahead of the inboard collet, and the WR1110
# stands one more hop ahead of the check, holding the appliance side at 90 PSI.
#
# The axis is the WALL'S OWN NORMAL, so the chain takes a half turn about Z and nothing else:
# each fitting's frame already runs its flow down +Y with the upstream mouth on −Y, and the half
# turn lays that on world −Y — collet outboard, gas running forward into the machine. The
# bulkhead is the one body that takes NO turn: its own frame already runs +Y outboard toward
# the customer's tube, which is the axis and the plane the +Y wall of back-top gives it.
CO2_CHAIN_TURN = (((0.0, 0.0, 1.0), 180.0),)
NEOFIT_STEP = _hw / "reference" / "neofit-bulkhead" / "neofit-bulkhead.step"
GASHER_STEP = _hw / "reference" / "gasher-check-valve" / "gasher-check-valve.step"
WR1110_STEP = _hw / "reference" / "wr1110-regulator" / "wr1110-regulator.step"
# WHERE IT CROSSES THE +Y WALL OF BACK-TOP IS THE UNION ROW'S OWN NEXT COLUMN. `PORT_PITCH` is what a
# column costs on this wall — a fitting's panel footprint, the gap two nuts leave a socket, and
# the room the bodies hanging off each column ask for over it — and the gas inlet is a fitting on
# that same wall with a body hanging off it. So it stands one pitch EAST of the carb union, on
# `deck_storey`: the meter's own axis, one column over, parallel and level with it.
CO2_COLUMN = PANEL_X["bulkhead-carb"] + PORT_PITCH
# The hop `co2-0` closes, mouth to mouth: the bulkhead's inboard collet to the check's inlet
# socket. It holds a PI010822S in the check's female inlet and the stretch of 1/4" tube the
# bulkhead's collet and the adapter's collet both take hold of.
CO2_INLET_HOP = 8.0
# The hop `co2-1` closes, mouth to mouth: the check's stub tip to the regulator's inlet socket.
# It holds a PP450822E on the check's male stub, a PP010822E in the regulator's female one, and
# the stretch of 1/4" tube between the two collets.
CO2_HOP = 10.0


def co2_inlet_mouth_y():
    """The Y of the ABU44's INBOARD collet face — the mouth `co2-0` leaves by, and so where the
    whole chain starts. Read off `bulkhead_seat_y` through the fitting's own reach, exactly as
    `bulkhead_mouth_y` reads the unions: the flange bears on the port field's crown and what the
    fitting takes inboard of that is its own business."""
    return bulkhead_seat_y() + _neofit.far_ring_face_y


def build_co2_inlet(deck: float):
    """The 1/4" bulkhead union the customer's CO2 tether goes into, clamped through the +Y wall of back-top
    one `PORT_PITCH` east of the carb union and on the deck's own storey, seated on its INBOARD
    COLLET — the same seating the four PP1208E unions take, on the same plane."""
    body = import_step(str(NEOFIT_STEP)).val()
    return seat_body(body, (), seat="co2-inlet",
                     station=(_neofit.port(-1.0),
                              (CO2_COLUMN, co2_inlet_mouth_y(), deck)))


def build_gasher_co2(inlet_carry):
    """The check standing one `CO2_INLET_HOP` ahead of the bulkhead on the chain's own axis,
    seated on its INLET socket. Its arrow points away from the bulkhead: the carbonator's
    pressure never reaches the customer's regulator."""
    pos, axis = inlet_carry(_neofit.port(-1.0))
    target = tuple(pos[i] + axis[i] * CO2_INLET_HOP for i in range(3))
    body = import_step(str(GASHER_STEP)).val()
    return seat_body(body, CO2_CHAIN_TURN, seat="gasher-co2",
                     station=(_gasher.inlet(), target))


def build_wr1110(gasher_carry):
    """The secondary regulator standing one `CO2_HOP` ahead of the check on the chain's own
    axis, seated on its INLET socket. Nothing threads onto it and nothing holds it — the cradle
    is an open item; this is where it hangs."""
    pos, axis = gasher_carry(_gasher.outlet())
    target = tuple(pos[i] + axis[i] * CO2_HOP for i in range(3))
    body = import_step(str(WR1110_STEP)).val()
    return seat_body(body, CO2_CHAIN_TURN, seat="wr1110",
                     station=(_wr1110.inlet(), target))


def co2_wall_port(inlet_carry):
    """The bore the ABU44's M17 barrel passes, as a `back_ports` entry. Struck on the fitting's
    own inboard collet so hole and barrel cannot land on two different columns, and bored one
    `PORT_HOLE_SLIP` over that barrel — the same construction the four unions' bores take."""
    pos = inlet_carry(_neofit.port(-1.0))[0]
    return ("round", pos[0], pos[2], _neofit.panel_hole_d(PORT_HOLE_SLIP))


# The assembly's non-manifold members, by name. `report` measures the manifold pack as
# one box — the clearances the core and the pump stand off are struck against it — so a
# body added to the assembly that is not part of that pack has to be named here or it
# joins the box and moves every one of them.
STANDALONE = ("compressor", "condenser+fan", "foam-assembly", "seaflo-pump",
              "funnel", "suction-chain", "discharge-chain", "display", "display-cover",
              "display-gasket",
              "psu", "pcba",
              "relay-1", "relay-2", "ground-stack", "asse1022-assembly", "asse-drip-pan",
              "moisture-plate", "mq6-sensor", "thermal-fuse", "fuse-clamp",
              ) + WAGO_POLES + tuple(CLUSTER_WAGOS) + (
              "water-split", "flow-regulator", "vk-solenoid", "bulkhead-water",
              "c14-inlet", "co2-inlet", "gasher-co2", "wr1110",
              "nameplate", "nameplate-ink",
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
# The seam's own furniture reaches a whole `enclosure.boss_in` further inboard, and each piece
# of it is a block round its own screw, one `enclosure.socket_r` about the level it pins. A body
# seated here meets one where its own height crosses one of theirs, which is a question about
# two placed solids and is `pack-closes`'s to answer.
#
# What fences this flank at EVERY height is the standing corner's relief, and
# `enclosure.wall_boss_aft_limit` is the station where it takes the wall out from under a
# boss. The power
# block closes its aft end on that plane, through the brick's own rear mount hole.
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


# What a floor post stands off the wall of the bore it rises through, on the radius. The bore
# is rubber — a grommet wrapped through the donor's own metal hole, flanged over both faces —
# and that rubber is the isolator, working in shear round the post's whole standing length.
FLOOR_BOSS_SLIP = 1.0

# HOW FAR THE WASHER SQUEEZES THE GROMMET BEFORE THE POST STOPS IT. The post's crown stands
# this far UNDER the donor's own crown, so drawing the screw up pulls the top flange down by
# this much and then lands on printed material. An elastomeric mount wants preload — a flange
# left at its free height lifts off between cycles and the plate chatters on it — and it wants
# a limit, because rubber taken far up its curve stiffens and stops isolating. Both come out of
# one printed dimension here rather than out of a torque spec, so every unit gets the same
# squeeze and no operator judges it. The flange's own thickness is what turns this into a
# percentage; the number is the one to move once a donor grommet is under calipers.
FLOOR_GROMMET_SQUEEZE = 0.4


def floor_mounts(*mounted):
    """The floor slab's boss stations, as `(x, y, tip, dia)`.

    `wall_mounts`' analogue for a body bolted DOWN onto the slab rather than hung on the
    flank. One `(carry, holes, face_z, bore_d)` per body: the placement, the body's own hole
    pattern, the height in that body's own frame of its grommet's crown, and the bore each post
    rises through. A body standing on the floor has that crown at the TOP of whatever the hole
    passes through, not at its own Z = 0 — the post rises through the hole to it, which is what
    locates the body as well as fastens it.

    THE POST'S SECTION IS THE DONOR'S, struck off that bore less one `FLOOR_BOSS_SLIP` on the
    radius, so a body whose holes are measured again moves its own posts with it and no
    diameter for them is typed anywhere. ITS CROWN IS THE DONOR'S LESS THE SQUEEZE: the post
    stops the washer one `FLOOR_GROMMET_SQUEEZE` under the grommet's own crown, which is the
    preload the flange carries."""
    out = []
    for carry, holes, face_z, bore_d in mounted:
        for hx, hy in holes:
            pos, _axis = carry(((hx, hy, face_z), (0.0, 0.0, 1.0)))
            out.append((pos[0], pos[1], pos[2] - FLOOR_GROMMET_SQUEEZE,
                        bore_d - 2.0 * FLOOR_BOSS_SLIP))
    return tuple(out)


# --- the condenser block's own two ends -------------------------------------
#
# The block is a donor envelope with four sheet flanges on it and no other purchase, so both
# stations below are read straight out of `condenser_block`'s own tables through the placement.
# Nothing here says where a flange is; the block does, and the box takes it from here.

def condenser_cradle(cond, cond_carry, floor: float) -> tuple:
    """The front wall's rails, as `enclosure._cond_cradle` reads them — one
    `(face, x0, x1, fz0, fz1, root)` per FORE flange.

    `face` is the plane the block's own fore face comes to rest on, so the rail's shoulder is
    where the block stops and its reach into the bay is the block's own depth. THE BASE RAIL
    ROOTS ON THE SLAB and the crown one hangs off the wall a section under its GROOVE, which is
    the difference between a corner bracket carrying the block's standoff and a shelf. That root
    is struck under the groove's own lower face, not under the flange's."""
    b = box(cond)
    rows = []
    for i, (fz0, fz1) in enumerate(_cond.flange_z()):
        face = cond_carry(((0.0, 0.0, fz0), (0.0, -1.0, 0.0)))[0][1]
        z0, z1 = sorted(cond_carry(((0.0, 0.0, fz), (0.0, 0.0, 1.0)))[0][2]
                        for fz in (fz0, fz1))
        half = _enc.cond_slot_half(z1 - z0)
        rows.append((face, b.xmin, b.xmax, z0, z1,
                     floor if i == 0 else z0 - half - _enc.cond_rail_wall))
    return tuple(rows)


def condenser_mount(cond, cond_carry) -> tuple:
    """The +X wall's fin and its two fingers, as `enclosure._cond_mount` reads them:
    `(flank, y0, y1, ((x, y, tip), …))`.

    The band is the AFT RECESS'S OWN, less one `cond_mount_clear` at its inner end and the
    block's own slide at its mouth — so the fingers stand inside the recess with the room to
    draw the block back off them. The tips are `condenser_block.mount_seats()`, which is the
    face under each hole rather than the hole itself: what a screw closes on is the sheet, and
    what the sheet lands on is the boss."""
    clear = _enc.cond_mount_clear
    _fore, aft = _cond.recess_y()
    band = sorted(cond_carry(((0.0, y, 0.0), (0.0, 1.0, 0.0)))[0][1]
                  for y in (aft[0] + clear, aft[1] - _enc.cond_slot_grip - clear))
    seats = tuple(cond_carry(st)[0] for st in _cond.mount_seats().values())
    return (box(cond).xmax + clear, band[0], band[1], seats)


def condenser_airway(cond, cond_carry) -> tuple:
    """The block's own AIRWAY, as `enclosure._flank_vents` reads it — `(y0, y1, z0, z1)`, the
    band on either flank that actually passes air.

    THE RECESSES ARE NOT AIRWAY. Each Y face stands `condenser_block.RECESS_Y` back over the
    block's whole width, and what that leaves at either end is the folded sheet the box holds
    the block by — a groove at one end, a boss at the other. The fan draws through neither. The
    band between them is the finstack, and it is the only part of the block's flank a vent cut
    opposite it is opening onto.

    IN HEIGHT IT IS THE WHOLE BLOCK, less nothing: the flanges the recesses leave are
    `condenser_block.PLATE_T` of sheet at the crown and the base, which is four tenths of a
    millimetre against 137, and the serpentine runs to both of them."""
    fore, aft = _cond.recess_y()
    ys = sorted(cond_carry(((0.0, y, 0.0), (0.0, 1.0, 0.0)))[0][1] for y in (fore[1], aft[0]))
    b = box(cond)
    return (ys[0], ys[1], b.zmin, b.zmax)


# The brick lies on its side against that wall: a quarter about Y stands its 52 mm width up as
# height and lays its 33.5 mm depth across the machine, so only that much of the lane reaches
# inboard and its 109 mm long axis runs fore and aft down the flank.
PSU_TURN = (((0.0, 1.0, 0.0), -90.0),)


def build_psu(foam, wall_seat):
    """The MeanWell brick on the +X wall, standing on the cold core's cap.

    Three faces of the machine and not three numbers: EAST on the wall seat, FOOT on the cap's
    own lid, and AFT its own rear mount hole on `enclosure.wall_boss_aft_limit` — the brick
    answers to the corner with the hole pattern it has, so its aft face lands wherever that
    puts it. The lane it lies in is what the SeaFlo leaves east of itself on that cap.

    THE COLUMN AHEAD OF IT HAS NOTHING TO TAKE. Relay #2 and the main board are packed one
    `WIRED_CLEAR` at a time off this brick's own fore face and the main board stands about a
    millimetre off `carb-1` there, which `clearance-floor` reads — so this plane is the whole of
    the brick's travel, and what gives to the row on its crown is the row (`build_wago_row`)."""
    return seat_body(import_step(str(PSU_STEP)).val(), PSU_TURN, seat="psu",
                     x1=wall_seat,
                     y1=_enc.wall_boss_aft_limit() + (_psu.length / 2.0 - _psu.hole_dy),
                     z0=cap_face(foam))


# The main board joins the brick's column rather than standing forward of the deck: same
# flank, same seat, same floor. Two turns put it there. The ROLL stands it off the flat — a
# quarter about Y brings its faces onto ±X, so only its 19.1 mm of thickness and components
# reaches into the lane, and the flat back is the face that meets the wall it mounts to. The SPIN
# is in that plane — a quarter about X lays the main board's LONG edge fore and aft down the flank, so
# the short edge is what stands, and the corner that meets the cap is the one nearest the brick.
PCBA_TURN = (((0.0, 1.0, 0.0), -90.0), ((1.0, 0.0, 0.0), -90.0))
# What one wired body on the cap storey stands off the next along this flank. Brick, relay and
# board all take their conductors on the faces that look down the column at each other, and a
# hand making off a connector between two of them needs the gap to be a gap — a working reach
# rather than the `STACK_CLEAR` the boss between them would leave on its own.
WIRED_CLEAR = 6.0


def build_pcba(foam, ahead_of, wall_seat):
    """The main board on the +X wall, forward of whatever the brick's column presents.

    EAST on the same wall seat the brick takes, so the two stand in one plane and one length of
    boss holds them both; AFT one `WIRED_CLEAR` ahead of `ahead_of`'s own front face — which is
    relay #2, not the brick, since the relay stands between them; FOOT on the cap. What holds it
    is the pcba-tray, which is not placed — this is the main board's envelope."""
    return seat_body(import_step(str(PCBA_STEP)).val(), PCBA_TURN, seat="pcba",
                     x1=wall_seat, y1=box(ahead_of).ymin - WIRED_CLEAR, z0=cap_face(foam))


# The rest of the power block, on the two crowns: relay #1 on the MAIN BOARD'S crown with the ground
# stud one clearance forward of it, and the five Wago wells on the BRICK'S. Each takes the same
# wall seat as its east face, so the whole group stands on one plane against the wall, in the
# depth `enclosure.east_band_free_y` leaves aft of the Y seam's own bosses — the lever nuts
# excepted, which seat on the wall itself because a well is not a boss.
#
# Each turn lays the body's own long axis fore and aft down the flank and its board facing
# INBOARD — the face a screwdriver reaches, and the face a boss would land on.
RELAY_TURN = (((0.0, 0.0, 1.0), 270.0), ((0.0, 1.0, 0.0), 270.0))
# The floor between one body on this column and the next, and it is not air for its own sake:
# what stands in it is the WALL BOSS that fastens the body between them. The relay is the body
# that sets it — its mount pattern runs closest to its own edge, so the boss standing on that
# pattern reaches furthest past the main board — and the gap is that reach with a clearance past it.
STACK_CLEAR = (_enc.mount_boss_dia / 2.0
               - (_relay.width / 2.0 - _relay.hole_dy) + 1.0)


# Relay #2 stands the same body ON END: a further quarter about X carries its long axis from
# fore-and-aft onto Z, so it presents 17 mm of depth to the band instead of 70. That is the only
# way a third body fits between the main board and the brick, and standing it costs nothing — its
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
    """Relay #2 on end, in the band between the brick and the main board.

    EAST on the wall seat every body on this flank takes; AFT one `WIRED_CLEAR` ahead of the
    brick's own front face; FOOT on the cap, the same lid the brick and the main board stand on. Its
    screw block and its header stand one over the other, both facing the room."""
    return seat_body(import_step(str(RELAY_STEP)).val(), RELAY2_TURN, seat="relay-2",
                     x1=wall_seat, y1=box(psu).ymin - WIRED_CLEAR, z0=cap_face(foam))


def wago_row_reach() -> float:
    """How far aft the last lug of a five-wide 221-413 row reaches from the row's own origin —
    four pitches, the well wall the first lug starts past, and one lug's own height."""
    return 4.0 * _enc.wago_pitch + _enc.wago_well_wall + _enc.wago_stand("413")[0]


def check_wago_row(lugs, psu, inlet) -> Bound:
    """The row against the crown it lies on. It is drawn forward off centre by the inlet, and
    what it may not do is walk off the brick: a lug hanging past the brick's own front face is a
    body over air, and the wall's well is holding it there on its own.

    AND THE GAP IT KEPT ON THE OTHER SIDE, which is what the brick's fore face is charged
    against. `WIRED_CLEAR` is a hand's working reach at the receptacle's own terminals and the
    row takes what is left of it once every lug is over the crown (`build_wago_row`), so the
    figure is READ here rather than assumed: the row's aft end against the inlet's fore face,
    on the card, every build."""
    pb, ib = box(psu), box(inlet)
    lo = min(box(s).ymin for _n, s, _c in lugs)
    hi = max(box(s).ymax for _n, s, _c in lugs)
    reach = ib.ymin - hi
    ok = lo >= pb.ymin - 1e-6 and hi <= pb.ymax + 1e-6
    return record_bound(Bound(
        "wago-row-on-brick", "The lever-nut row lies over the brick it stands on", ok,
        f"row spans y {lo:.2f}..{hi:.2f}, crown {pb.ymin:.2f}..{pb.ymax:.2f}, "
        f"{reach:.2f} mm of reach at the inlet",
        "every lug over the crown",
        ([] if ok else [
            f"the row spans y {lo:.2f}..{hi:.2f} and the brick's crown runs {pb.ymin:.2f}.."
            f"{pb.ymax:.2f}. The C14's housing is what draws the row forward of centre, so what "
            f"is out of room is the brick's depth against `wago_row_reach` and `WIRED_CLEAR`."])))


def build_wago_row(psu, wall_seat, inlet):
    """The five 221-413 lever nuts on the brick's crown, as `[(name, solid, carry)]`.

    They are the only bodies on this flank that no boss holds: each presses into a well printed
    on the wall itself (`enclosure._side_wells`), so what locates them is the wall, and what this
    places is the lug that goes in it. The row runs fore and aft on the brick's own depth, one
    `WAGO_CLEAR` over its crown.

    WHERE ON THAT CROWN IS THE INLET'S TO SAY. Centred is where five wells sit squarest on the
    body under them, and that is where the row goes — unless the C14 reaches into the span, and
    it does: the receptacle whose live, neutral and earth these lugs splice stands its housing
    and its terminals off a +Y wall of back-top the brick runs the whole way to. So the row is centred, or
    drawn forward until its last lug stands one `WIRED_CLEAR` ahead of those terminals, whichever
    is further forward.

    AND THE BRICK'S FORE FACE IS WHERE THAT DRAW STOPS. A lug's height is struck off the crown
    (`WAGO_CLEAR` over it), so a lug past the brick's fore end is at a Z justified by nothing
    under it — `check_wago_row` is that reading. The brick cannot give the ground back either:
    the column ahead of it is packed one `WIRED_CLEAR` at a time onto a board that stands about a
    millimetre off `carb-1` (`build_psu`). So the row lies over the crown whole and the working
    reach at the terminals is what is left of `WIRED_CLEAR` once it does, which `check_wago_row`
    reads onto the card rather than leaving to the reader.

    THEY SEAT ON THE WALL AND NOT ON `east_wall_seat`. Every other body on this flank stands its
    outer face on a boss TIP, one `mount_boss_out` inboard of the wall, because a boss is what
    holds it. Nothing holds a lever nut but the pocket, and the pocket bottoms on the wall — so
    the lug's butt goes to `interior_x`, and seating it on the boss plane instead would leave it
    floating that same `mount_boss_out` clear of the well built to receive it."""
    pb = box(psu)
    span = 5 * _enc.wago_pitch
    y0 = max(pb.ymin - _enc.wago_well_wall,
             min((pb.ymin + pb.ymax) / 2.0 - span / 2.0,
                 box(inlet).ymin - WIRED_CLEAR - wago_row_reach()))
    out = []
    for i, name in enumerate(WAGO_POLES):
        solid, carry = seat_body(import_step(str(wago_step("413"))).val(), WAGO_TURN,
                                 seat=name, x1=_enc.interior_x()[1],
                                 y0=y0 + i * _enc.wago_pitch + _enc.wago_well_wall,
                                 z0=pb.zmax + WAGO_CLEAR + _wago_skirt())
        out.append((name, solid, carry))
    check_wago_row(out, psu, inlet)
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
        solid, carry = seat_body(import_step(str(wago_step(size))).val(), turn,
                                 seat=name, y0=y - stand_y / 2.0, z0=z - stand_z / 2.0, **face)
        out.append((name, solid, carry, size))
    return out


def build_stack(psu, pcba, wagos, wall_seat):
    """What stands on the two crowns, as `[(name, solid, colour, carry)]`.

    Relay #1 takes the MAIN BOARD'S crown — the main board is the tallest body on the cap and the shortest
    in depth, so the room over it is the one room a 70 mm relay lies down in. The ground stud
    takes what that relay leaves of the same shelf, forward of it, because a ring stack is the
    one body here that will go wherever there is a corner. Relay #2 is not on either crown; it
    stands on the cap between the main board and the brick (`build_relay2`)."""
    out = []
    relay1, r1_carry = seat_body(import_step(str(RELAY_STEP)).val(), RELAY_TURN,
                                 seat="relay-1", x1=wall_seat, y1=box(pcba).ymax,
                                 z0=box(pcba).zmax + STACK_CLEAR)
    out.append(("relay-1", relay1, C_RELAY, r1_carry))
    stud, stud_carry = seat_body(import_step(str(GND_STACK_STEP)).val(), RELAY_TURN,
                                 seat="ground-stack", x1=wall_seat,
                                 y1=box(relay1).ymin - STACK_CLEAR, z0=box(relay1).zmin)
    out.append(("ground-stack", stud, C_GND, stud_carry))
    return out


def wago_wells(row, cluster, over):
    """Every wall's well stations, `(side, y, z, size, clear_z)` — one per placed lug, read off
    the lug's own box so a well cannot end up anywhere but under the thing it holds. `clear_z`
    is the plane the flank's air stops being the well's — `over` is the row's, the crown of the
    brick it runs along, and a cluster well carries None: its wall is open beneath it."""
    out = []
    for _name, solid, _carry in row:
        b = box(solid)
        out.append((+1, (b.ymin + b.ymax) / 2.0, (b.zmin + b.zmax) / 2.0, "413", over))
    for name, solid, _carry, size in cluster:
        b = box(solid)
        out.append((CLUSTER_WAGOS[name][0],
                    (b.ymin + b.ymax) / 2.0, (b.zmin + b.zmax) / 2.0, size, None))
    return tuple(out)


# --- what fastens the power column to the +X wall --------------------------
#
# Every body on that flank is turned so its own MOUNTING PLANE faces the wall and stands on
# the wall seat: the brick's potted base, the main board's underside, the relay's PCB underside,
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
    """Every body hung on the +X wall stands in the depth that wall states.

    Standing ON the wall puts a body INSIDE the ±X boss-chain band, which is the whole of what
    `east_wall_seat` buys and the whole of what it costs. What it costs is two STATED planes,
    and they are the two this measures: forward, the aft face every Y-seam level shares
    (`y_seam + lip_len` — the levels differ in height and share one station, so one plane
    stops all of them); aft, the back corner's own relief, which curves the wall away from the
    seat plane at every height. `enclosure.east_band_free_y` strikes both.

    IT DOES NOT MEASURE THE Z-SEAM COLLARS, and that is the shape of the answer rather than a
    gap in it. Each is a block `2 * socket_r` tall at a height its own seam is SEARCHED to
    (`_z_joints`), so whether a body meets one is a question about where two solids stand — and
    the body clears it by standing over or under it as readily as beside it. `pack-closes`
    answers that, against the printed pieces themselves. This runs while the pack is being
    built, before the box has been sized, so it asks only what the box states about itself."""
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
        "east-band", "The +X wall's column stands in the depth that wall states", not out,
        f"column spans y {fore:.2f}..{aft:.2f}, band {y0:.2f}..{y1:.2f}",
        f"inside y {y0:.2f}..{y1:.2f}",
        ([] if not out else [
            f"{n} reaches {much:.2f} mm {where} the stated depth — forward of it the Y seam's "
            f"own bosses stand at every level, and aft of it the corner takes the wall out "
            f"from under the boss. Move the column along the flank, or seat that body back on "
            f"`enclosure.boss_in` and let it stand off the wall instead"
            for n, where, much in sorted(out, key=lambda r: -r[2])])))


# --- the tap-water sequence, in the west lane ------------------------------
#
# The backflow preventer and everything that threads or clamps onto it, made up as one chain.
# Its own frame runs the flow down +X with the VENT ON −Z, so any turn that keeps the vent
# pointing at the floor is a yaw and nothing else — and the vent has to point at the floor,
# because it weeps to atmosphere and that drip is the machine's cross-contamination telltale.
#
# The yaw lays the 140 mm chain fore and aft in the lane west of the pump, INLET AFT: the tap
# water comes in through the +Y wall of back-top, so the mouth that faces the bulkhead is the upstream
# one and the flow runs forward down the lane to the split.
ASSE1022_YAW = -90.0
# The chain's aft end is THE BULKHEAD'S REACH and nothing else, because the joint between them is
# flush: the union hangs `jg_bulkhead_union.far_ring_face_y` inboard of the wall it clamps
# through, and the chain's inlet collet meets that face. So a longer union, or a thicker wall,
# moves the chain forward — and the whole west lane, which hangs off this chain, comes with it.
# THE PUMP IS NOT ITS BOX, and the lane west of it is a different width at every height. The
# bracket's splayed feet are the widest thing on the casting and they are only
# `seaflo_22_pump.FOOT_T` tall; over them the cradle steps in, and the head's flange steps back
# out. The chain and its pan stand on the deck's storey, high over the bracket, and what
# fences them there is whatever the casting presents AT THEIR OWN HEIGHT.
#
# `check_pan_lane` holds the tray's SLEEVE off the casting's west flank by this, read over the
# room the sleeve itself stands in.
FOOT_CLEAR = 1.0
# How far the tray's west end stands OUTSIDE the machine's own skin. The pull face extends back
# from that outer plane and stops one running-fit slip before the wall, so it masks the berth
# without becoming the tray's insertion stop. This is the whole of the tray a hand meets: thumb
# on the flange's top, fingertip under the floor, draw west.
#   IT CARRIES THE PROBE WITH IT. The plate rides the tray, so the vent's tip lands this far
# east of the plate's own centre, and `check_drip_reads` takes that reading.
PAN_PROUD = _pan.PULL_FACE_DEPTH + _pan.PAN_SLIP
# The probe plate has two individual 22 AWG silicone leads soldered on 2.54 mm centres. They
# rise in the open pan and turn WEST through one notch in the withdrawal wall. It is not a
# close wire bore: the top is absent and this clear width takes the pair plus hand-routed slack.
PAN_LEAD_RACE_W = 5.0
PAN_LEAD_RACE_INNER_OVERLAP = 1.0


def pan_rim_z(asse):
    """The Z the ASSE drip pan's RIM stands at: the vent's own fall, less what stands over the rim.

    THE TRAY HANGS OFF THE CHAIN. `build_asse` stands the chain on the panel deck and one
    `VENT_GAP` of splash-and-service air hangs under its underside — over the SLEEVE'S LID,
    which is the topmost thing in this column. The rim takes station one lid and one slip below
    that lid, so a change to any of the three moves the pan and nothing else."""
    return box(asse).zmin - _pan.VENT_GAP - DRIP_SLEEVE_T - _pan.PAN_SLIP


def pan_floor(asse):
    """The Z the pan's own floor stands at — its rim, less its depth. The rim is the plane the
    chain fixes, so `PAN_Z` hangs DOWN from it, into the strip over the pump's casting."""
    return pan_rim_z(asse) - _pan.PAN_Z


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


def pan_west_x():
    """The X the tray's west lip stands at: one `PAN_PROUD` outside the −X wall's own outer face.

    THE TRAY IS HUNG ON THE WALL IT COMES OUT THROUGH. Everything a hand does to this body
    happens at that face — the tab it takes hold of, the slot it draws through — and the plate
    the tray carries rides the same station east. What the lane has left of it east of the
    sleeve is `check_pan_lane`."""
    return west_exterior_face() - PAN_PROUD


def build_asse(deck):
    """The ASSE 1022 chain in the west lane, seated on its INLET COLLET at the tap-water union's
    own station on the +Y wall of back-top.

    ALL THREE COORDINATES ARE THAT UNION'S. The two collets butt face to face with nothing
    between them to turn around, so the chain answers to the mouth it meets and to nothing else:
    the wall's WEST COLUMN in X — the column `PANEL_X` gives the flavor-B union, which the
    tap-water one stands directly over — `bulkhead_mouth_y` in Y, and the panel deck's own storey
    in Z, the storey the row's other unions cross the wall on.

    The ASSE drip pan then takes station under the vent, and the split and the regulator off the
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
# axis — so a anchor cut at the widest of them holds nothing, and one cut at the narrowest takes
# only the narrowest. Cut at each section's own, the steps BETWEEN sections are faces square to
# the axis, and the barrel is trapped between two of them.
#
# EVERY SECTION IS THE SAME 120° V AND ONLY ITS APEX MOVES, which is what makes those steps fall
# out rather than be drawn: a V of this angle is the two flanks of a hex read off its corner, and
# it is also the tangent seat of any circle. So the same anchor beds a hex on two whole flats and
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
    """The chain's own sections, forward to aft, as `(y0, y1, west_x, seat_r, axis_x)` — the band
    each occupies down the lane, how far west its seat reaches, the bore radius a round one takes,
    and the axis a bore is struck on. `seat_r` is None where the section is seated on a V.

    A HEX GETS A V AND A CIRCLE GETS A BORE. The hex's V is read off the corner it lies on, so its
    apex stands one circumradius under the axis; a round section is held in a bore concentric with
    it, one `ASSE_SEAT_SLIP` over its own circumradius, stopped at the axis plane where its lip is
    still a lip. That is the whole of why the barrel steps out of its neighbours and not a number
    chosen here.

    Read through `asse_carry`, so a fitting whose length changes moves its own step."""
    axis = asse_carry(_asse.flow_axis())[0]
    def band(part_x0, part_x1, across, hexed):
        # +X in the chain's frame is the machine's −Y: the yaw lays the flow forward down the
        # lane, so a section's upstream end is its AFT end.
        ends = sorted(asse_carry(((x, 0.0, _asse.bfp.BODY_CENTER_Z), (1.0, 0.0, 0.0)))[0][1]
                      for x in (part_x0, part_x1))
        if hexed:
            west = axis[0] - across / 2.0 - ASSE_SEAT_SLIP / math.sin(math.radians(60.0))
            return (ends[0], ends[1], west, None, axis[0])
        seat_r = across / 2.0 + ASSE_SEAT_SLIP
        return (ends[0], ends[1], axis[0] - seat_r, seat_r, axis[0])
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
    # and the millimetre either side of it belongs to the deeper of the two sections it divides —
    # so the deep section is longer than the fitting in it and the step is a stop that fitting
    # travels to.
    # BOTH END SECTIONS RUN THE SHORTER OF THE TWO FITTINGS' LENGTHS. What the anchor puts at each
    # end of the barrel is a face square to the axis, and the fitting past that face is seated on
    # the section it presents rather than followed down its length.
    reach = min(r[1] - r[0] for r in (rows[0], rows[-1]))
    rows = ((rows[0][1] - reach, rows[0][1], *rows[0][2:]), rows[1],
            (rows[-1][0], rows[-1][0] + reach, *rows[-1][2:]))
    out = [list(r) for r in rows]
    for i in range(len(out) - 1):
        deep = i if out[i][2] < out[i + 1][2] else i + 1
        edge = out[i][1] + (ASSE_STEP_SLIP if deep == i else -ASSE_STEP_SLIP)
        out[i][1], out[i + 1][0] = edge, edge
    return tuple(tuple(r) for r in out)




# Where the two ties close the anchor's mouth. The barrel is the only section a tie may cinch on
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
    """How far under the axis the anchor's flanks run — the chain's OWN lowest arris, and not a
    millimetre past it.

    Every section's lowest point below the axis is its apothem if the anchor reads its flats and
    its radius if it reads its tangent, so the deepest of the three is what the anchor has to
    reach and anything under that is PETG holding air. It is the barrel's, being both the widest
    section and the one seated on flats.

    The vent stub hangs far below all of this and is not in it: the anchor would have to be
    notched around the fall, and what stands under the barrel is the tray."""
    return max(axis_z_drop for axis_z_drop in _asse_section_drops(asse_carry))


def _asse_section_drops(asse_carry):
    """Each section's own reach under the axis — apothem for the one read off flats, radius for
    the ones read off their tangent."""
    yield _asse.bfp.HEX_ACROSS_CORNERS / 2.0 * math.cos(math.radians(30.0))
    yield _oad.NUT_ACROSS_CORNERS / 2.0
    yield _asse.coupling.HEX_ACROSS_CORNERS / 2.0


def asse_cradle(asse_carry) -> tuple:
    """The whole station `enclosure._asse_cradle` builds from: the axis the ASSE anchor is struck on,
    its sections, the two tie bands, and how far under the axis its flanks reach."""
    axis = asse_carry(_asse.flow_axis())[0]
    return (axis[2], asse_sections(asse_carry), asse_ties(asse_carry),
            asse_reach_down(asse_carry))


def check_asse_seated(chain, piece, asse_carry) -> Bound:
    """Whether the chain is actually IN its anchor, read off the two placed solids.

    A body drawn beside a groove is not a body lying in one, and every reading this card takes of
    the tap-water chain is satisfied by a chain floating in air — `placed` sees a seat it holds,
    `vent-lands` sees a drip that falls where it should, `clearance-floor` sees a millimetre it
    keeps. None of them can tell a cradle that closes on the barrel from one drawn a centimetre
    off it, because nothing about the pack changes.

    So this reads the STACK ACROSS THE V, in the one direction the anchor is meant to stop:

        seat   how far west the chain stands off the wall's own furniture — one
               `ASSE_SEAT_SLIP` on the V's normal is the anchor closed on the barrel's two
               flats, and anything more is a chain resting on nothing

    Measured on the solids and not on the sections table, because the table is what DREW the
    anchor: a bound read back off its own inputs is a bound that cannot fail."""
    def solid(s):
        s = s.toCompound() if hasattr(s, "toCompound") else s
        return s.val() if hasattr(s, "val") else s
    # `_clearing.gap` reports a floor past its reach, so ask it for more than the anchor may
    # have: a chain resting on nothing has to come back with the number, not with the reach.
    got = _clearing.gap(solid(chain), solid(piece), 5.0)
    # The tightest of the anchor's three seats: a bore stands off its section radially, so the two
    # round ones close on the slip itself while the barrel's V closes on it along the V's normal.
    want = ASSE_SEAT_SLIP
    ok = got <= want + 1e-3
    return record_bound(Bound(
        "asse-seated", "The tap-water chain lies in its printed anchor", ok,
        f"{got:.3f} mm off the wall's furniture", f"{want:.3f} mm at most",
        ([] if ok else [
            f"the chain stands {got:.3f} mm off everything `enclosure-back-top` puts near it, "
            f"and the anchor is drawn to close on it at {want:.3f}. Either the cradle's sections "
            f"no longer read the chain's own — `asse_sections` — or the chain moved and the "
            f"station did not follow it."])))


def check_digiten_seated(meter, piece) -> Bound:
    """Whether the meter is up in its two anchors, read off the two placed solids.

    The same reading `check_asse_seated` takes and for the same reason: a anchor drawn near a
    barrel and a anchor closed on one are the same to every other row on this card. Two things
    differ. The seat here is a BORE, concentric with the barrel, so the gap it holds is the slip
    itself — the anchor's V holds its slip on the V's own normal and reads `slip / sin 60°` between
    two axis-aligned solids, and a bore has no such angle in it. And this seat opens DOWNWARD, so it
    is not carrying the meter: the two zip ties are, and this is the reading that says they have
    something to pull it up against."""
    def solid(s):
        s = s.toCompound() if hasattr(s, "toCompound") else s
        return s.val() if hasattr(s, "val") else s
    got = _clearing.gap(solid(meter), solid(piece), 5.0)
    want = DIGITEN_SEAT_SLIP
    ok = got <= want + 1e-3
    return record_bound(Bound(
        "digiten-seated", "The flow meter hangs in its two printed anchors", ok,
        f"{got:.3f} mm off the ceiling's furniture", f"{want:.3f} mm at most",
        ([] if ok else [
            f"the meter stands {got:.3f} mm off everything `enclosure-ceiling-panel` puts near "
            f"it, and its anchors are drawn to close on the two barrels at {want:.3f}. Either "
            f"`digiten_anchors` no longer reads the meter's own ports, or the meter moved and the "
            f"station did not follow it."])))


def anchor_rows(foam_carry, bodies: dict) -> list:
    """Each chain anchor as `(name, label, has, wants, fouls)` — the rib the cap carries against
    the sections of the placed body it stands under.

    A RIB MAY BE LONGER THAN THE SECTION IT BEARS ON, and the suction chain's is: what its twin
    seats on is an 18 mm check hex, and that fitting is only on the discharge side. So the test is
    not containment but clearance — exactly one section under the rib FILLS the bore, and every
    other one it overhangs onto has to pass under it. `fouls` names any that does not.

    `wants` is the filling section's own circumradius plus `CHAIN_SEAT_SLIP`, read off the body's
    own stack. The cap prints a rib it never sees the body of, so the body is what corrects it.

    A RIB BORED FOR A RUN IS NOT ROWED HERE. A tube is one section its whole length, so there is
    no stack to read and nothing for a rib to foul; what holds those honest is
    `check_run_seated`, which reads the contact itself."""
    rows = []
    for name, station in _cci.cap_anchors.items():
        if name not in bodies:
            continue
        carry, mod = bodies[name]
        axis = foam_carry(cap_anchor(name))[0]
        tip = carry(mod.barb_tip())[0]
        half = _cci.cap_anchor_len / 2.0
        # `s` runs from the barb tip down the chain, and both chains are laid barb aft — so a rib
        # standing at `axis` covers this stretch of the stack.
        s0, s1 = (tip[1] - axis[1]) - half, (tip[1] - axis[1]) + half
        under = [(lab, r) for lab, r, a, b in mod.sections() if a < s1 - 1e-9 and s0 + 1e-9 < b]
        fills = [(lab, r) for lab, r in under if abs(r + CHAIN_SEAT_SLIP - station.seat_r) <= 1e-3]
        fouls = [lab for lab, r in under if r + CHAIN_SEAT_SLIP > station.seat_r + 1e-3]
        label, r = fills[0] if fills else (
            max(under, key=lambda s: s[1]) if under else ("nothing", 0.0))
        rows.append((name, label, station.seat_r, r + CHAIN_SEAT_SLIP, fouls if fouls or fills
                     else ["no section fills the bore"]))
    return rows


def check_anchor_lands(rows) -> Bound:
    """Whether every cap rib is bored for a section that fills it and clears the rest.

    The detail is the row `_cold_core_interface.cap_anchors` should carry, so a body that has
    moved or changed section corrects the cap from the machine rather than being guessed at."""
    bad = [r for r in rows if r[4] or abs(r[2] - r[3]) > 1e-3]
    return record_bound(Bound(
        "anchor-lands", "Every cap rib is bored for a section that fills it", bool(rows) and not bad,
        "no rib stood" if not rows else f"{len(rows)} ribs, {len(rows) - len(bad)} on section",
        "one section filling each bore, the rest passing under it",
        ([] if rows and not bad else
         [f"chain anchor {n}: the rib bears on {lab} and is bored {has:.3f}, where that section "
          f"asks {want:.3f}"
          + (f"; and {', '.join(f)} will not pass under it" if f else "")
          + ". This is the row `_cold_core_interface.cap_anchors` should carry:"
          for n, lab, has, want, f in bad]
         + [f'    "{n}": CapAnchor({_cci.cap_anchors[n].centre}, {want:.3f}),'
            for n, _lab, _has, want, _f in bad])))


def check_chains_seated(chains: dict, foam) -> Bound:
    """Whether every chain lies in its printed rib, read off the placed solids.

    The same reading the tap-water chain's and the meter's take. These seats are bores, so the gap
    each holds is the slip itself — and they open UP, so the reading says the body is DOWN in its
    rib and the zip tie has something to pull against rather than something to carry."""
    def solid(s):
        s = s.toCompound() if hasattr(s, "toCompound") else s
        return s.val() if hasattr(s, "val") else s
    want = CHAIN_SEAT_SLIP
    got = {n: _clearing.gap(solid(c), solid(foam), 5.0) for n, c in chains.items()}
    bad = {n: g for n, g in got.items() if g > want + 1e-3}
    worst = max(got.values(), default=0.0)
    return record_bound(Bound(
        "chains-seated", "Every made-up chain lies in its printed rib on the core's cap", not bad,
        f"{len(got)} seated, furthest off {worst:.3f} mm", f"{want:.3f} mm at most",
        ([] if not bad else [
            f"{n} stands {g:.3f} mm off everything the cold core puts near it, and its rib is "
            f"drawn to close on one section at {want:.3f}. Either `cap_anchors` no longer reads "
            f"that section's own radius, or the chain moved and the rib did not follow it — "
            f"`anchor-lands` is the row that says which." for n, g in bad.items()])))


def check_tie_vocabulary() -> Bound:
    """Whether every module that cuts a zip tie cavity cuts it for the same zip tie.

    `enclosure` and `_cold_core_interface` each state the fastener their own features read,
    and the box imports the core's interface rather than the other way round. This is the
    module that seats both, so it is where they are held together."""
    pairs = (("width", "_cold_core_interface", _enc.tie_w, _cci.cap_anchor_tie_w),
             ("cavity", "_cold_core_interface", _enc.tie_cav_w, _cci.cap_anchor_cav_w),
             ("end wall", "_cold_core_interface", _enc.tie_cav_wall, _cci.cap_anchor_cav_wall))
    bad = [(what, who, a, b) for what, who, a, b in pairs if abs(a - b) > 1e-9]
    return record_bound(Bound(
        "tie-vocabulary", "Every box cuts its zip tie cavities for the same zip tie", not bad,
        f"{len(pairs) - len(bad)}/{len(pairs)} agree", "every figure the same in both",
        [f"the zip tie's {what}: `enclosure` cuts for {a:.3f} and `{who}` for {b:.3f}. One tie "
         f"goes through both, so one of these is a cavity the zip tie in the BOM does not pass."
         for what, who, a, b in bad]))


def check_tube_seated(tubes, pieces) -> Bound:
    """Whether every anchored run lies in the rib its row names, read off the placed solids.

    The same reading the chain's and the meter's take, on the one body the machine has twenty of.
    It also reads back WHICH piece: the site names one, the rib is built by whichever piece owns
    the whole of it, and a run seated against a piece its row does not name is a run whose
    exemption in `_scorecard.anchored_pairs` is pointed at the wrong solid."""
    def solid(s):
        s = s.toCompound() if hasattr(s, "toCompound") else s
        return s.val() if hasattr(s, "val") else s
    want = TUBE_ANCHOR_SLIP          # a bore concentric with the tube stands off it radially
    rows, worst = [], 0.0
    for rid, _leg, _root, piece in TUBE_ANCHOR_SITES:
        tube, part = tubes.get(f"tube-{rid}"), pieces.get(piece.removeprefix("enclosure-"))
        if tube is None or part is None:
            rows.append(f"{rid}: no {'run' if tube is None else piece} to read")
            worst = max(worst, want + 1.0)
            continue
        got = _clearing.gap(solid(tube), solid(part), 5.0)
        worst = max(worst, got)
        if got > want + 1e-3:
            rows.append(
                f"{rid} stands {got:.3f} mm off {piece} and its rib is drawn to close on the tube "
                f"at {want:.3f}. Either the route moved off the leg `TUBE_ANCHOR_SITES` names, or "
                f"the rib landed in a piece that row does not name.")
    return record_bound(Bound(
        "tube-seated", "Every anchored run lies in its printed rib", not rows,
        f"{len(TUBE_ANCHOR_SITES)} anchored, furthest off {worst:.3f} mm",
        f"{want:.3f} mm at most", rows))


def check_tie_channels(anchors, meter_anchor, cradle, pieces) -> Bound:
    """Whether a tie can still reach through every cavity the box cuts one for.

    THE CHANNEL IS A REMAINDER AND NOT A CUT (`enclosure._tube_anchors`, `_flow_meter_anchors`): the
    rib's two ends climb to the face it roots on and what they do not span IS the zip tie's room.
    Nothing is drawn for it, so nothing about it can fail loudly — a wall that grows inboard of
    the plane the rib was measured against simply arrives standing in that room, and the rib comes
    through as a lump with a bore in it. Every other reading on this card stays green: the seat
    still closes on its body at the slip, the piece is still one watertight solid, the pack still
    stands clear of the walls. Nothing here measures a hole, and this is a hole.

    SO IT ASKS FOR THE ZIP TIE AND NOT FOR THE CHANNEL. What is read is the seat a tie actually
    needs — `tie_t` off the bore's own crown, the cavity's width along the body, the rib's
    full reach across it — and that volume is struck off the STATION, with no root face in it at
    all. A rib buried in a wall and a rib standing proud of one are the same arithmetic; what
    differs is whether the answer is air.

    THE ASSE ANCHOR'S TWO ARE A CUT AND CANNOT FILL, so what is read there is the ROUTE
    INSTEAD: each zip tie comes west over the chain's top flat and drops into its channel through
    the block's back, and that channel's mouth is out at the −X wall. So the column between the
    mouth and the ceiling is the room the loop comes down, and it is what a ceiling corbel
    standing on the strip's outboard run would close (`enclosure.back_top_ceiling_reliefs`)."""
    def solid(x):
        x = x.toCompound() if hasattr(x, "toCompound") else x
        return x.val() if hasattr(x, "val") else x
    parts = {n: solid(v) for n, v in pieces.items()}
    rows, seen, worst = [], 0, 0.0

    def read(what, vol):
        nonlocal seen, worst
        seen += 1
        want, box = vol.Volume(), _boxes.boxed(vol)
        for name, part in parts.items():
            # A seat is a few tens of mm3 and a piece is a quadrant of the machine, so the box
            # settles all but one or two of these without meshing anything.
            pb = _boxes.boxed(part)
            if (pb.xmax < box.xmin or box.xmax < pb.xmin
                    or pb.ymax < box.ymin or box.ymax < pb.ymin
                    or pb.zmax < box.zmin or box.zmax < pb.zmin):
                continue
            got = _overlap.volume(vol, part)
            if got <= 1e-6:
                continue
            worst = max(worst, 100.0 * got / want)
            rows.append(
                f"{what}: {100.0 * got / want:.0f}% of the room a zip tie needs is inside {name} — "
                f"{got:.1f} of {want:.1f} mm3. On a rib, the two ends are drawn to a plane that "
                f"piece stands inboard of, so what is left between them is in its stock "
                f"(`enclosure.piece_root_faces`); on the anchor, a corbel has closed over the "
                f"channel's mouth (`enclosure.back_top_ceiling_reliefs`).")

    for mid, u, n, seat_r in anchors:
        # The zip tie's seat in the anchor's own frame: one `tie_t` slab off the bore's crown,
        # spanning the cavity's length along the body and the rib's whole reach across it.
        origin = tuple(mid[k] - u[k] * _enc.tube_anchor_len / 2.0 + u[k] * _enc.tie_cav_wall
                       for k in range(3))
        reach, crown = seat_r + _enc.wall, seat_r + _enc.wall
        read(f"anchor at {tuple(round(c, 1) for c in mid)}",
             _enc._anchor_rib(origin, u, n, _enc.tie_cav_w, reach, crown,
                              crown + _enc.tie_t))
    if meter_anchor:
        x_axis, z_axis, seat_r, bands = meter_anchor
        reach = seat_r + _enc.flow_meter_anchor_wall
        crown = z_axis + seat_r + _enc.wall
        for by0, by1 in bands:
            m = (by0 + by1) / 2.0
            read(f"anchor at y {m:.1f}",
                 _enc._ybox(x_axis - reach, x_axis + reach, m - _enc.tie_cav_w / 2.0,
                            m + _enc.tie_cav_w / 2.0, crown, crown + _enc.tie_t))
    if cradle:
        z_ax, sections, ties, _dn = cradle
        run = 1.0 / math.tan(math.radians(_enc.asse_v_half))
        apex = min(w for _y0, _y1, w, _r, _a in sections)
        # The channel's own top mouth (`enclosure._asse_tie_cavity`): west face on the box's
        # interior plus a `wall`, east edge where the flare meets the block's crown.
        x_w = _enc.interior_x()[0] + _enc.wall
        x_e = apex - _enc.wall / math.sin(math.radians(_enc.asse_v_half)) \
            + (_enc.asse_cradle_up + 1.0) * run
        top = z_ax + _enc.asse_cradle_up + 1.0
        for ty in ties:
            read(f"tap-water zip tie at y {ty:.1f}",
                 _enc._ybox(x_w, x_e, ty - _enc.tie_wide_w / 2.0,
                            ty + _enc.tie_wide_w / 2.0, top, interior_ceiling()))
    return record_bound(Bound(
        "tie-channels", "A tie still reaches through every cavity cut for one", not rows,
        f"{seen} read, worst {worst:.0f}% filled", "0% filled", rows))


def check_run_seated(tubes, foam) -> Bound:
    """Whether every run the cap is bored for lies in its rib, read off the placed solids.

    The reading `check_tube_seated` takes on the box's own ribs, on the cap's. What differs is
    which way the correction runs: a chain is seated ON its rib, so a gap there is the body's to
    fix; a run's plane is its two ports', so a gap here is the ROW'S — `over_face` is what the rib
    was built up to, and the tube is where it already was."""
    def solid(s):
        s = s.toCompound() if hasattr(s, "toCompound") else s
        return s.val() if hasattr(s, "val") else s
    want = TUBE_ANCHOR_SLIP
    rows, worst, seen = [], 0.0, 0
    for name in _cci.cap_anchors:
        tube = tubes.get(f"tube-{name}")
        if tube is None:
            continue                       # a rib bored for a body, which `anchor-lands` holds
        seen += 1
        got = _clearing.gap(solid(tube), solid(foam), 5.0)
        worst = max(worst, got)
        if got > want + 1e-3:
            rows.append(
                f"{name} stands {got:.3f} mm off the cold core and its rib is bored to close on "
                f"the tube at {want:.3f}. `_cold_core_interface.cap_anchors[{name!r}].over_face` "
                f"is what the rib reaches, and the run lies {got - want:+.3f} off it.")
    return record_bound(Bound(
        "run-seated", "Every run the cap is bored for lies in its rib", not rows,
        f"{seen} bored, furthest off {worst:.3f} mm", f"{want:.3f} mm at most", rows))


# THE TRAY STANDS CLEAR OF THE PUMP'S DISCHARGE. The barb fires west into this same lane and the
# chain that hangs off it takes the lane's forward end, so the SLEEVE's forward face is struck on
# the barb's own aft edge with this much daylight past it. That plane fixes the tray in Y — the
# vent does not, and has only to fall inside the floor from wherever the chain leaves it.
PAN_PORT_CLEAR = 10.0


def pan_front_y(seaflo_carry):
    """The Y the tray's sleeve stands its forward face on: one `PAN_PORT_CLEAR` aft of the pump's
    discharge. The pan's own forward rim is one sleeve section and one slip further aft.

    The barb is a cylinder firing along ±X, so what it stands in down the lane is its centreline
    and its own radius. Moving the pump moves the tray that clears it."""
    pos = seaflo_carry(_lines._pump.discharge())[0]
    return pos[1] + _lines._pump.PORT_D / 2.0 + PAN_PORT_CLEAR


def check_vent_lands(pan, tip) -> Bound:
    """Where the drip falls against the pan's FLAT FLOOR, inside the coves.

    The pan's outer rim to that flat is the flange, the wall and the cove together. A drip
    landing on a cove or a wall runs down the outside of the tray instead of onto the moisture
    plate, and the plate stays dry however long the vent weeps."""
    b = box(pan)
    inset = _pan.FLANGE_W + _pan.WALL + _pan.FLOOR_COVE
    y0, y1 = b.ymin + inset, b.ymax - inset
    ok = y0 <= tip[1] <= y1
    return record_bound(Bound(
        "vent-lands", "The atmospheric vent drips on the pan's flat floor", ok,
        f"drips at y {tip[1]:.2f}" + ("" if ok else f", {min(abs(tip[1] - y0), abs(tip[1] - y1)):.2f} mm outside"),
        f"y[{y0:.2f}, {y1:.2f}]",
        ([] if ok else [
            f"asse-drip-pan: the vent drips at y {tip[1]:.2f}, off the flat floor y[{y0:.2f}, "
            f"{y1:.2f}]. The forward rim comes off the pump's discharge through "
            f"`PAN_PORT_CLEAR`; the vent's Y comes off the ASSE chain, which the bulkhead's "
            f"reach through the +Y wall of back-top fixes; the flat between them is `PAN_Y` less its "
            f"flange, its walls and its coves."])))


def check_pan_lane(pan, seaflo) -> Bound:
    """What the lane leaves between the tray's SLEEVE and the pump's casting, read over the room
    the sleeve itself stands in.

    The tray is hung on the −X wall — the tab a hand takes and the slot it comes out through are
    both on that face — so the sleeve's backstop is the end of the lane the tray asks for, and
    the casting is what it meets. Everything east of that face is ceiling the west column's
    crossing ladder buys radius from."""
    b = box(pan)
    east = b.xmax + _pan.PAN_SLIP + DRIP_SLEEVE_T
    casting = pump_west_face(seaflo, b.zmin - _pan.PAN_SLIP - DRIP_SLEEVE_T,
                             b.zmax + _pan.PAN_SLIP + DRIP_SLEEVE_T,
                             b.ymin - _pan.PAN_SLIP - DRIP_SLEEVE_T,
                             b.ymax + _pan.PAN_SLIP + DRIP_SLEEVE_T)
    got = casting - east
    ok = got >= FOOT_CLEAR - 1e-6
    return record_bound(Bound(
        "pan-lane", "The ASSE drip pan's sleeve stands clear of the pump's casting", ok,
        f"backstop at x {east:.2f}, casting at {casting:.2f} — {got:.2f} mm",
        f"≥ {FOOT_CLEAR:g} mm",
        ([] if ok else [
            f"asse-drip-pan: the sleeve's backstop reaches x {east:.2f} and the casting stands at "
            f"{casting:.2f} over the sleeve's own room — {got:.2f} mm, against the "
            f"{FOOT_CLEAR:g} the lane owes. The west lip is fixed at one PAN_PROUD = "
            f"{PAN_PROUD:g} outside the wall's skin, so what gives is `asse_drip_pan.PAN_X`, "
            f"`asse_drip_pan.FLANGE_W`, or the pump's own station through `seaflo_west_limit`."])))


def build_pan(asse, seaflo, seaflo_carry, asse_carry):
    """The ASSE drip pan, under the atmospheric vent and over the pump's casting.

    IN Y THE PUMP'S DISCHARGE BOUNDS IT AND THE VENT DOES NOT. The sleeve's forward face is
    `pan_front_y` and the pan's rim stands one sleeve section and one slip aft of it, and the
    vent falls where the chain's own standoff from the +Y wall of back-top leaves it — so where the drip
    lands is a check, and `check_vent_lands` is where it is made.

    IN X THE WALL BOUNDS IT. The west lip is `pan_west_x`, one `PAN_PROUD` outside the machine's
    skin; the sleeve's backstop takes what the rim leaves and `check_pan_lane` reads that against
    the casting. The tip lands `PAN_PROUD` east of the floor's own centre — 6 mm of a ±21 mm
    floor, so the drip still falls well inside the coves. The slot the tray draws out through is
    a wall port, struck off this body's own box in `west_wall_ports`.

    Z is `pan_floor` — the chain's underside, one `VENT_GAP` down to the sleeve's lid, that lid
    and one slip down to the rim, and one `PAN_Z` down to the floor."""
    pan = _pan.build()
    pan = pan.val() if hasattr(pan, "val") else pan
    # The bound the PAN states about itself — its flat floor against the moisture plate it
    # receives — read off `asse_drip_pan`'s own ledger and entered here, so it is a card row beside
    # the two this module states about where the pan stands.
    record_bound(Bound(*_pan.check_plate()))
    placed, carry = seat_body(
        pan, (), seat="asse-drip-pan", x0=pan_west_x(), z0=pan_floor(asse),
        y0=pan_front_y(seaflo_carry) + DRIP_SLEEVE_T + _pan.PAN_SLIP)
    check_vent_lands(placed, asse_carry(_asse.port("vent-tip"))[0])
    check_pan_lane(placed, seaflo)
    return placed, carry


# --- the moisture plate, lying in the ASSE drip pan ------------------------
#
# The Shutao module is two boards: the LM393 comparator, which mounts dry off elsewhere, and the
# interdigitated probe plate, which is the half that has to be WET to read. This is that half.
#
# THE PLATE IS TURNED A QUARTER and `asse_drip_pan.check_plate` is the reason: its 54 mm runs down the
# pan's Y, the axis the aft strip has depth to spare on, and its 40 mm across the X the west
# lane has to buy from the pump. Sizing the floor and standing the body on it read ONE turn, so a
# pan that passes its own bound is a pan this plate lies flat in.
#
# The quarter is +90, which carries the plate's own −X edge — the edge its two lead holes sit
# behind — onto the pan's FORWARD end. That is the end away from the ASSE chain the tray hangs
# under: the leads leave the pan in the open, not under the body that drips into it, and the
# solder joints are the last thing a pool standing in the pan reaches.
PLATE_YAW = 90.0


def check_drip_reads(plate, tip) -> Bound:
    """Where the drip falls against the PLATE, which is a narrower target than the floor.

    `check_vent_lands` holds the drip on the pan's flat floor and that is a different bound
    with a different failure: a drip on a cove runs down the outside of the tray. This one is
    the sensor's own. The flat floor is 43 x 67 and the plate is 40 x 54, so there is a band the
    tray catches and the probe never reads — the vent weeps, the pan does its job, and the alarm
    the weep exists to raise stays silent until the pan has pooled deep enough to reach the
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
            f"y[{b.ymin:.2f}, {b.ymax:.2f}]. The plate is centred on the pan's flat floor and "
            f"the pan is struck off the pump's discharge in Y and its casting in X, so what "
            f"moves the target is `PAN_PORT_CLEAR` or `FOOT_CLEAR`; what moves the drip is the "
            f"ASSE chain's own standoff from the +Y wall of back-top."])))


def build_moisture_plate(pan_carry, asse_carry):
    """The probe plate lying flat on the pan's floor, centred on the flat inside the coves.

    ITS ONE STATION IS ITS OWN UNDERSIDE CENTRE, seated on the flat floor's centre carried out of
    the tray's frame — so the plate rides the tray. `build_pan` hangs the pan off the ASSE
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
# pump and the manifold are on. WHICH IS THE WHOLE POINT OF THE BRANCH — `water-3` leaves by it
# and has to get to the floor before it can cross the machine, so a branch pointing anywhere but
# down buys the crossing a descent it would otherwise not make.
SPLIT_TURN = (((0.0, 1.0, 0.0), -90.0),)
# THE FUNNEL'S BOWL IS THE FORWARD LANE'S CEILING. The chain crosses the wall on the panel deck
# and the lane it hands the water to runs forward under that bowl, so the tap steps down out of
# the deck between the chain and the split, in the open room aft of the funnel. Everything
# forward of the split — the regulator, its tap and the tube down to the flavour gates — lies on
# the storey this step lands on.
#
# `check_bowl_clear` measures what the step leaves once the funnel is in the box, which is the
# first moment the bowl exists to measure against: the box is sized around this pack and the
# funnel is then set in its top.
#
# `water-3`'s OWN CORNER IS THE FLOOR, and this figure moves with `_lines.CROSS_RISE`. The tee
# stands one tangent over the corner its branch falls into, so a deeper step wants a deeper fall
# under the crossing's lane, and a deeper fall turns through a wider angle on a longer tangent.
# What bounds the pair is the cap lid's outer face, which that corner's belly runs over —
# `_lines.CROSS_RISE` carries the reading.
#
# The flavor-B gate line stands clear of this tee in plan: it runs its own union's column aft at
# x[−81.2, −74.9] and this tee's collet cap reaches x −85.1, so what that pair reads is a solid
# distance rather than a height. Re-read it —
#
#     w.gap(split, tube_fluid_28, 8.0, offset=(0, 0, -d))
FLAVOR_STEP = 45.40
# What the tap's own headroom under that bowl has to be.
BOWL_CLEAR = 1.0
# The reach between the chain's outlet collet and the split's supply collet — `water-2`. The two
# mouths face each other down one column with the step between them, so what this has to be is
# the run that step's two corners and the lean between them take.
WATER_2 = 42.0
# THE SPLIT STANDS ON ITS OWN COLUMN AND `water-2` IS WHAT CROSSES TO IT. The chain answers to
# the +Y wall of back-top — all three of its coordinates are the tap-water union's, and `PORT_WEST_COLUMN`
# is what stands that union's pair in the lane. The storey below is a different room: the gate
# line holds its own union's column inboard of this one the whole way aft, `water-3` falls out of
# this split's own downward branch on whatever column the split stands on, and neither is under
# the other. So the sequence forward of the step keeps its column when the wall's moves, and the
# lean already in `water-2` for the step carries the offset across as well as down.
SPLIT_COLUMN = -92.0


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
#
# THE STEM IS THE ONLY PART OF THIS BODY UNDER THE FUNNEL. The valve stands west of the funnel's
# collar and its run and hub stand there with it; what reaches east past the collar's wall is the
# nut, the barrel and the adjuster, and the bowl's cone comes down over exactly that reach. It
# runs LEVEL under it, on the pair's own storey — the cone stands clear of the whole reach at this
# height, so nothing has to be tipped out of its way and the adjuster faces the machine's centre
# square, where a hand comes in over the cold core's cap. `check_bowl_clear` reads what is left.
FLOWREG_TURN = (((0.0, 0.0, 1.0), -90.0), ((0.0, 1.0, 0.0), 90.0),
                ((1.0, 0.0, 0.0), 180.0))
# `fluid-1` IS A HAIRPIN. The regulator stands OVER the split on the split's own column with its
# inlet facing the way the split's flavour collet faces, so the run leaves one mouth, turns 180°
# and comes back into the other — two stock quarter-turns, no straight between them or at either
# end. WHAT THAT COSTS IS TWO RADII OF Z and nothing else, so this is not a figure to pick: a
# semicircle's ends are one diameter apart across the turn.
FLUID_1_RISE = 2.0 * _lines.TUBE_BEND


def check_bowl_clear(flowreg, funnel) -> Bound:
    """What the flavour tap keeps under the funnel's bowl — the exact solid gap between the
    regulator's crown and the funnel hanging over it.

    Measured rather than derived, because the two are on opposite sides of the box: the box is
    sized around the pack the regulator is in, and the funnel is then seated in its top. So
    `FLAVOR_STEP` is the reach the lane is given and this is what it turns out to be worth."""
    got = _clearing.gap(flowreg, funnel, FLAVOR_STEP)
    ok = got >= BOWL_CLEAR - 1e-6
    return record_bound(Bound(
        "bowl-clear", "The flavour tap runs under the funnel's bowl", ok,
        f"{got:.3f} mm to the funnel", f"{BOWL_CLEAR:g} mm",
        ([] if ok else [
            f"flow-regulator: the tap's crown leaves {got:.3f} mm under the funnel's bowl, "
            f"under the {BOWL_CLEAR:g} mm the lane is drawn for. `FLAVOR_STEP` is the step "
            f"`water-2` takes off the panel deck onto this lane; deepen it by what is short."])))


def build_flowreg(split_carry):
    """The regulator seated on its INLET, one `FLUID_1_RISE` OVER the split and on the split's own
    centre across — so the two bodies stand on ONE VERTICAL, both flows lie fore and aft along it,
    and `fluid-1` is the hairpin between the two mouths.

    SEATED OFF THE SPLIT'S CENTRE AND NOT OFF ITS COLLET. What the stack is is two bodies on one
    column, so the thing that has to land on that column is the body — and a fitting's centre is
    the only point of it that stands on its own axes. Seating off the collet instead puts the two
    centres one reach apart in Y and leans the hairpin.

    THE PAIR IS A STACK AND THE SPLIT IS ITS DATUM. Everything about where this body goes is read
    off the split, so the regulator rides it wherever the chain carries it and the hairpin between
    them never changes shape."""
    hub, _axis = split_carry(((0.0, 0.0, 0.0), (0.0, 1.0, 0.0)))
    target = (hub[0], hub[1] - _flowreg.REACH, hub[2] + FLUID_1_RISE)
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
# and what is left between its outlet and the chain's collet is nothing: both mouths lie on that
# plane and on one column and meet face to face, so the joint is a butt. The cap prints its
# three cradles on that same row (`_cold_core_interface.cap_cradles`), and `cap-valve-row`
# measures it.
# THE VALVE'S SEAT is the cradle's. The cap prints four bosses (`valve_seat`) at this
# valve's own station (`_cold_core_interface.cap_cradles`), and what a seat says is where the
# Beduan's Z = 0 — the underside of its white body — stands once its four posts are pressed
# home. So the seat is read off the part that carries it rather than stated here, and a cradle
# that moves takes the valve and the chain behind it with it.


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
    the plane its rib lays the chain on, so the valve comes back down onto its own
    seat — and on `row_y`, the face the source pair stands its own ends on.

    The outlet is this valve's aft collet, so the whole body stands in the pair's own depth and
    the outlet lands on the chain's own collet."""
    pos, _axis = chain_carry(_suct.tube_port())
    target = (pos[0], row_y, pos[2])
    body = _beduan.build_beduan_solenoid()
    body = body.val() if hasattr(body, "val") else body
    return seat_body(body, (), seat="vk-solenoid", station=(_beduan.outlet(), target))


# --- what carries the tray, and the slot it draws out through --------------
#
# The sleeve's own section, every way — the block's floor under the tray, its two flanks, its
# lid and its backstop. It is `enclosure.wall`: the sleeve is the box's material and prints in
# the box's gauge.
DRIP_SLEEVE_T = _enc.wall


def pan_berth(pan):
    """The room the tray runs in, as the two rectangles its own section makes, each one
    `asse_drip_pan.PAN_SLIP` proud of the tray on every side: the WELL the pan's body runs in, and
    the REBATE its rim runs in over the well's shoulders.

    Each is `(y0, y1, z0, z1, x1)` — the opening across the withdrawal axis, and the east end
    the tray's own outline reaches. The well's `z1` is the flange's underside, which is where
    the wall's slot stops; `pan_sleeve` carries its own cut on up through the lid, where the
    same opening is the pan's mouth.

    ONE STATEMENT, READ TWICE. `pan_sleeve` cuts the block on it and `west_wall_ports` cuts the
    −X wall on it, so the slot cannot be a different shape from the berth behind it."""
    s = _pan.PAN_SLIP
    flange, rim = _pan.FLANGE_W, _pan.FLANGE_T
    well = (pan.ymin + flange - s, pan.ymax - flange + s,
            pan.zmin - s, pan.zmax - rim, pan.xmax - flange + s)
    rebate = (pan.ymin - s, pan.ymax + s,
              pan.zmax - rim - s, pan.zmax + s, pan.xmax + s)
    return well, rebate


def pan_sleeve(pan, west_face):
    """The tray's carry, as `(adds, cuts)` of world boxes for `enclosure._pan_sleeve`: ONE SOLID
    BLOCK fused onto the −X wall's inner face, and the berth cut back out of it.

    THE BLOCK IS THE CARRY. It runs the tray's own rim plus one slip and one section every way,
    from the wall east past the tray's east end, so it is rooted on the wall over its whole west
    face and there is one continuous flat surface on each of its outsides. The pan lies on the
    block's floor the way a drawer lies in its carcase.

    FOUR CUTS TAKE IT BACK, AND THEY REACH DIFFERENT DISTANCES WEST. The WELL and the REBATE are
    the tray's own two sections — the pan's body, and the rim over its shoulders — and both run
    west THROUGH the wall, because that is the silhouette the tray travels on. The MOUTH is the
    pan's opening carried up through the lid for the drip to fall in, and it stops at the wall's
    INNER face: the tray is nowhere near this tall, so an opening cut this high in the wall is a
    hole nothing passes through. The LEAD RACE is the narrow open-top notch through the
    withdrawal wall, on the Y of the plate's two solder holes. Inboard of it the leads rise in
    the already-open pan mouth; at the wall they turn west through this one short notch. The
    pan stays whole and watertight — this cuts only the roof that otherwise pinches the leads
    over the tray's rim.

    What none of the four reaches is solid: the block's floor under the pan, its flanks
    outboard of the rim, its lid over the flange, and — east of where the tray's own outline ends
    — the BACKSTOP, full section from floor to lid, which is what the tray comes to rest
    against."""
    (wy0, wy1, wz0, wz1, wx1), (ry0, ry1, rz0, rz1, rx1) = pan_berth(pan)
    s, t = _pan.PAN_SLIP, DRIP_SLEEVE_T
    z1 = pan.zmax + s + t
    block = (west_face, pan.xmax + s + t,
             pan.ymin - s - t, pan.ymax + s + t, pan.zmin - s - t, z1)
    # The berth's two cuts start west of the wall's own outer face, so the slot the wall carries
    # and the room behind it are opened by one geometry rather than two that have to agree.
    x0 = west_face - _enc.wall - 1.0
    # The plate is centred on the pan and turned +90 degrees (`PLATE_YAW`), so both holes share
    # one Y station near the pan's forward end. The pan mouth is already open above them;
    # only the short run through the wall needs taking out. One millimetre of overlap makes the
    # notch and mouth unambiguously continuous instead of leaving a zero-thickness knife edge.
    lead_y = ((pan.ymin + pan.ymax) / 2.0
              - (_plate.PLATE_X / 2.0 - _plate.HOLE_INSET))
    lead_race = (
        x0, west_face + PAN_LEAD_RACE_INNER_OVERLAP,
        lead_y - PAN_LEAD_RACE_W / 2.0, lead_y + PAN_LEAD_RACE_W / 2.0,
        # Its floor is the rim's own top and its roof is deliberately absent.
        pan.zmax, z1 + 1.0,
    )
    return [block], [(x0, wx1, wy0, wy1, wz0, wz1),
                     (x0, rx1, ry0, ry1, rz0, rz1),
                     (west_face, wx1, wy0, wy1, rz1, z1),
                     lead_race]


def west_wall_ports(pan):
    """Through-holes the −X wall carries, as `(kind, y, z, *size)` on that wall's own plane —
    the slot the tray draws out through.

    ONE OPENING IN TWO RECTANGLES, which are `pan_berth`'s own: the well below the flange's
    underside and the rebate at the rim. The tray stands `PAN_PROUD` outside this wall, so its
    west end is through the slot and its floor spans the wall's thickness.

    Square corners — `CORNER_R` rounds the tray in PLAN, and this is the section across it,
    where floor meets wall at a right angle."""
    return [("rect", (r[0] + r[1]) / 2.0, (r[2] + r[3]) / 2.0,
             r[1] - r[0], r[3] - r[2], 0.0)
            for r in pan_berth(pan)]


def _whole(bodies):
    out = None
    for s in bodies:
        b = box(s)
        out = b if out is None else out.add(b)
    return out


def place_base(seated, names=()):
    """Turn the mated pair `BASE_YAW` about the vertical through their own combined centre, then
    seat it — centred on x = 0 and the COMPRESSOR's own front face on `COMPRESSOR_FRONT`. Both
    moves are rigid and taken on the pair, so the plane between them rides along and the crown
    does not change.

    A yaw about a centre is not a placement: the turn leaves the pair's front wherever its own
    width used to reach, which is not the front of the machine.

    THE STAND IS STRUCK ON THE CAN AND NOT ON THE PAIR'S BOX. The compressor is the sited body on
    this floor — four posts under its feet, a service valve reaching off its front, a suction leg
    drawn off its west tangent — so it holds still and the condenser is placed relative to it. Off
    the pair's box, a condenser measured again moves the can, and every one of those follows.
    `seated[0]` is that body, which is the order `build_pack` hands them in and the order the
    ledger's row names them in.

    `seated` is each body as `(solid, carry)` off its own seat, and this hands back the same
    pair with the yaw and the stand composed onto each carry: a penetration declared in either
    body's own frame rides both moves, so a station cannot fall off the metal it is a hole in."""
    bodies = [s for s, _c in seated]
    w = _whole(bodies)
    cx, cy = (w.xmin + w.xmax) / 2.0, (w.ymin + w.ymax) / 2.0
    axis = (cq.Vector(cx, cy, 0.0), cq.Vector(cx, cy, 1.0))
    turned = [s.rotate(*axis, BASE_YAW) for s in bodies]
    step = cq.Vector(suction_lane_x() - box(turned[0]).xmin,
                     COMPRESSOR_FRONT - box(turned[0]).ymin, 0.0)
    stood = [s.translate(step) for s in turned]
    if names:
        # ONE BOX, AND IT IS THE CAN'S. Both planes the pair is stood on read off the compressor
        # alone — its west tangent on the suction's own lane, its front face on
        # `COMPRESSOR_FRONT` — so the row is struck on the geometry each was asked of, and a
        # condenser measured again moves neither.
        record_seat("refrigeration-base", turns=(((0.0, 0.0, 1.0), BASE_YAW),),
                    planes={"x0": suction_lane_x(), "z0": 0.0},
                    got=box(stood[0]), members=names)
        record_seat("refrigeration-base depth", planes={"y0": COMPRESSOR_FRONT},
                    got=box(stood[0]), members=(names[0],))

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

# WHERE THE PACK STANDS IN DEPTH, the companion to `PACK_CROWN` and stated the same way. The
# pose above turns the pack's own +Z — the axis its two decks stack on — onto +Y, and that axis
# has no datum inside the pack: `manifold_layout` pins each chain on its pump's barb plane and
# lets the rest fall out either side, so the depth the whole of it lands at is the machine's to
# say. This is that figure. It carries every body in the pack, both valve trays, both pump
# trays and the eight runs `_lines` anchors on the pack's own mouths.
#
# IT GOES ON THE STATIONS AS WELL AS ON THE SOLIDS. `manifold_carry` is the same move for a
# collet as `build_pack`'s translate is for the metal, and a run reaches a mouth by the station
# — so a figure spent on one and not the other takes every tube off its fitting while every
# picture still looks made up.
#
# THE ROW OF THREE ON THE COLD CORE'S CAP DOES NOT RIDE IT. V-A, V-B and V-K stand in cradles
# the cap prints, and the cap is not this pack — so `manifold_layout.SOURCE_TRAVEL` gives back
# exactly what this takes, millimetre for millimetre, and the three stay in their seats while
# the eight valves and the two pumps go aft. THE TWO FIGURES ARE ONE FIGURE: spend one without
# the other and either the row comes out of its cradles or the runs come off their ports.
# `cradles-land` is what reads the seats against the valves, and `runs-drawn` the ports against
# the tubes.
#
# WHAT THE STEP TO V-A COSTS IS LENGTH, NOT ROOM. Taking travel off it makes the run LONGER: it
# carries a hairpin ahead of the step, which turns through the whole circle to put the run
# behind where it started, and the less travel there is the more of it the hairpin has to hand
# back. `manifold_layout.hairpin_flat` is why a route can do that at all, and
# `manifold_layout.HAIRPIN_TILT` is the lane it spends doing it in.
#
# THE FIGURE: the pump heads ride ONE MILLIMETRE of air off `enclosure.pump_relief_floor`,
# the pocket floor the pump cartridge's face carries them behind — the pass-by `pumps-in-bay`
# reads off the placed heads. The decks stand aft of the heads by
# `manifold_layout.BARB_STANDOFF` on top of what the fold asks, which is the collet
# plate's whole berth; this figure carries the pumps, and the standoff sets everything
# aft of their barbs.
PACK_Y = 12.0


def pose_manifold(shape):
    return shape.rotate(*X_AXIS, 90.0).rotate(*Z_AXIS, 180.0)


def manifold_carry(lift: float):
    """The same two turns, the same depth and the same lift, as a `carry` for a STATION.

    `manifold_layout.port` and its siblings answer in the pack's OWN world — the frame the fold
    leaves it in — and `build_pack` then poses that whole world and stands it on the base's
    crown. A line reaching a valve's collet has to arrive where the collet ends up, so the
    station rides the same transform the solid does: `(x, y, z) → (−x, z + PACK_Y, y + lift)`,
    which is what the two rotations and the two datums compose to."""
    def carry(station):
        (px, py, pz), (ax, ay, az) = station
        return ((-px, pz + PACK_Y, py + lift), (-ax, az, ay))
    return carry


# The lowest thing the pack has is the four spine hairpins: the fold turned them onto its own
# underside and they hang past the pump-head faces, so THEY are what `PACK_CROWN` is measured
# to and the pump faces stand off that plane by whatever is left. Being lowest is not carrying
# anything — what holds this pack is the seat under each of its valves.
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
    # AND THEN THE BLOCK ALONE GOES EAST. The mating above is what PLACES it — the pair is
    # struck on the can's tangent and centred as one, which is what sites the compressor — and
    # this is the slide off that plane into the lane the +X wall leaves free. It is the last
    # move on this body, so the seat's own row still reads the pair the rule was struck on.
    cond, cond_carry = slide_east(cond, cond_carry, east_lane_free(cond))
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

    posed = [(c.name, pose_manifold((c.obj.val() if hasattr(c.obj, "val") else c.obj).moved(
        cq.Location(c.loc.wrapped.Transformation()))), c.color) for c in ml.build_assembly().children]
    lift = PACK_CROWN - min(box(s).zmin for _n, s, _c in posed)
    # The pack's own stations in world, from the moment it is stood: a run anchors on these, and
    # so does anything the machine stands ON one of them.
    mcarry = manifold_carry(lift)
    stood = [(n, s.translate(cq.Vector(0.0, PACK_Y, lift)), c) for n, s, c in posed]
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
                planes={"z0": PACK_CROWN}, got=_whole([s for _n, s, _c in stood]),
                members=tuple(in_pack))
    # THE TWO VALVE TRAYS' STATIONS, on the planes the fold left the manifold's eight non-cap
    # valves standing on. They are read straight off the pack: the deck a plate lands on and the
    # columns its seats stand on are the placed valves', and nothing here is a chosen number.
    # `enclosure._valve_trays` is what fuses each plate into the piece that owns its band.
    a.valve_trays = valve_tray_stations({n: s for n, s, _c in stood})
    # AND THE TWO PUMP TRAYS' STATIONS, on the faces the fold left each Kamoer's head standing
    # its boss off. Read straight off the pack the same way: the point a plate lies on is the
    # placed pump's own, and how far it runs to the wall is the box's.
    a.pump_trays = pump_tray_stations({n: s for n, s, _c in stood})
    # AND THE COLLET PLATE, in the berth `BARB_STANDOFF` opened between the barbs and the
    # anchor tees' branch collets — the steel the pump cartridge's four grips release against.
    a.collet_plate = collet_plate_spec(mcarry, a.pump_trays)
    plate_solid = build_collet_plate(a.collet_plate)
    a.add(plate_solid, name="collet-plate", color=C_STEEL_PLATE)
    record_seat("collet-plate", turns=(),
                planes={"y1": a.collet_plate["aft_y"], "z0": a.collet_plate["z0"],
                        "x0": a.collet_plate["x0"]},
                got=box(plate_solid))
    check_collet_plate(a.collet_plate, mcarry)
    # THE CORE IS PACKED AGAINST THE BACK. It is the body `rear_seam_clear` is written about —
    # the rearmost content, seated flush on the inner face of the rear Z-seam lip that hangs off
    # the +Y wall of back-top — so its aft face stands that one number inside `rear_plane_y`, which is the
    # same standoff `enclosure._dims` measures the depth bound against. The gap left in FRONT of
    # it is what the refrigerant loop's two drawn legs cross.
    top = cap_face(build_foam(0.0)[0])
    core = box(build_foam(0.0)[0])
    foam, foam_carry = build_foam(
        _enc.rear_plane_y - _enc.rear_seam_clear - (core.ymax - core.ymin))
    # What still has to hold is that nothing ahead of it reaches INTO it — measured at the core's
    # own height, since the source valves' quarter turns carry them aft OVER its crown and a body
    # standing over the cap is not a body in its way.
    check_pack_over_core(stood, foam)
    check_core_lane(
        box(foam).ymin,
        [("compressor", box(comp).ymax), ("condenser+fan", box(cond).ymax)]
        + [(n, box(s).ymax) for n, s, _c in stood if box(s).zmin < top])
    # THE CORE STANDS IN THE MACHINE AS ONE NODE, and its own bodies stand inside that node.
    # Opening the appliance reaches the carbonator, the coil, both reservoirs, every fitting and
    # the lines among them; each is picked where it is, and the core is taken in one where a
    # reader wants the whole of it. That is a real sub-assembly: the STEP carries the nesting,
    # `_placed` in `_mesh_payload` descends it, and every pass over this machine descends it too.
    #
    # THE NAME SAYS IT AS WELL, because one reader cannot see it. occt-import-js 0.0.23 — the
    # STEP reader the viewer runs — reports a component node as childless, so the tree reaches
    # the page flattened whatever the file holds. It carries NAMES faithfully, so `core_bodies`
    # composes the node into each one and the structure survives the flattening. Both of the
    # viewer's routes then say the same thing, which is the contract `_mesh_payload`'s selftest
    # holds them to.
    #
    # THE ENVELOPE IS NOT INSIDE IT. `solids["foam-assembly"]` below still holds it, and it is
    # what every port, station, line-route and geometry gate measures against; but a body cannot
    # be exported beside the bodies it is the outside of without sharing volume with all of them.
    a.core_envelope = foam
    core = cq.Assembly(name=CORE)
    for _name, _solid, _colour in core_bodies(foam_carry):
        core.add(_solid, name=_name, color=_colour)
    a.add(core, name=CORE)
    a.core_body_names = frozenset(n for n, _s, _c in core_bodies(foam_carry))
    # WHAT THE BOX SHUTS ON IT WITH. The core carries no hole, so its two front corners go into
    # blocks on the front-bottom's slab and its aft crown under brackets off the back-top's rear
    # wall — both struck on the core's own faces here, and grown by `enclosure._core_stops` /
    # `_core_holds` in whichever piece owns each station.
    a.core_stops = core_stops(foam)
    a.core_holds = core_holds(foam)
    a.vent_chase = vent_chase(foam, foam_carry)
    # The gate lane's own cruise, off the placed manifold — the plane the flavour pair climbs to.
    # Two bodies take it: `build_seaflo` carries it into `flavor_storey` for the band its casting
    # is measured over, and `a.gate_z` stands the pair itself on what that storey comes out at.
    gate_cruise = _lines.gate_cruise(mcarry(_lines.station("valve-v-i", "outlet"))[0][2])
    seaflo, seaflo_carry = build_seaflo(foam, gate_cruise)
    a.add(seaflo, name="seaflo-pump", color=C_SEAFLO)
    chain, chain_carry = build_suction_chain(foam_carry, seaflo_carry(_lines._pump.suction()))
    a.add(chain, name="suction-chain", color=C_SUCT)
    wall_seat = east_wall_seat()
    psu, psu_carry = build_psu(foam, wall_seat)
    a.add(psu, name="psu", color=C_PSU)
    # The band, fore to aft: board, relay #2 on end, brick. The relay is placed off the brick and
    # the main board off the relay, so the three close up on one chain and none of them carries a
    # typed Y of its own.
    relay2, relay2_carry = build_relay2(psu, foam, wall_seat)
    a.add(relay2, name="relay-2", color=C_RELAY)
    pcba, pcba_carry = build_pcba(foam, relay2, wall_seat)
    a.add(pcba, name="pcba", color=C_PCBA)
    # The inlet stands before the row that splices it: `build_wago_row` is drawn forward off the
    # brick's centre by this housing, so the receptacle has to be in world before the lugs are.
    # It answers to two stated planes and nothing on the floor, so it can be placed here as
    # readily as anywhere.
    c14, _c14_carry = build_c14()
    a.add(c14, name="c14-inlet", color=C_C14)
    wagos = build_wago_row(psu, wall_seat, c14)
    for name, solid, _carry in wagos:
        a.add(solid, name=name, color=C_AC_HUB)
    stack = build_stack(psu, pcba, wagos, wall_seat)
    for name, solid, colour, _carry in stack:
        a.add(solid, name=name, color=colour)
    stack_carry = {name: carry for name, _s, _c, carry in stack}
    cluster = build_cluster_wagos()
    for name, solid, _carry, _size in cluster:
        a.add(solid, name=name, color=C_AC_HUB)
    a.side_wells = wago_wells(wagos, cluster, over=box(psu).zmax + 1.0)
    check_east_band([("psu", psu), ("pcba", pcba), ("relay-2", relay2)]
                    + [(n, s) for n, s, _c in wagos]
                    + [(n, s) for n, s, _c, _k in stack])
    # The compressor is the one body on the floor that is bolted DOWN to it, so its four
    # holes are the slab's own boss stations. The plate's crown is where the washer lands and
    # its Ø14 grommet bore is what the post stands in, so both figures are the donor's.
    a.floor_bosses = floor_mounts(
        (comp_carry, _comp.mount_pattern(), _comp.BASE_Z, _comp.MOUNT_D))
    # The condenser is the other body on this slab the box holds, and it is held at its own four
    # flanges: two in a groove off the front wall, two on a boss apiece off the +X one.
    a.cond_cradle = condenser_cradle(cond, cond_carry, box(comp).zmin)
    a.cond_mount = condenser_mount(cond, cond_carry)
    # And the two flanks the air goes in and out by, which the block states the same way it
    # states its flanges: the finstack's own footprint, and the box pierces the flutes opposite
    # it (`enclosure._flank_vents`).
    a.cond_airway = condenser_airway(cond, cond_carry)
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
    # THE DECK COMES DOWN ONTO WHAT IS ALREADY STANDING, so its four bodies are struck against
    # the assembly as it is at this point. THE WEST LANE HANGS OFF IT and is not in the strike:
    # the tap-water union takes the deck's own storey, the chain butts that union, and the
    # split, the regulator and the ASSE drip pan all take station off the chain. NEITHER IS THE GAS
    # CHAIN: it takes that same storey rather than standing under it, so it goes up after the
    # strike and answers to `deck_storey` the way the union row does.
    a.gate_z = flavor_storey(gate_cruise, seaflo)
    under_deck = [s for s, _c in _solids(a).values()]
    a.deck_z, deck_fall = deck_z(under_deck, a.gate_z)
    co2in, co2in_carry = build_co2_inlet(a.deck_z)
    a.add(co2in, name="co2-inlet", color=C_CO2_INLET)
    gasher, gasher_carry = build_gasher_co2(co2in_carry)
    a.add(gasher, name="gasher-co2", color=C_GASHER)
    wr1110, wr1110_carry = build_wr1110(gasher_carry)
    a.add(wr1110, name="wr1110", color=C_WR1110)
    a.co2_inlet_carry = co2in_carry
    asse, asse_carry = build_asse(a.deck_z)
    a.add(asse, name="asse1022-assembly", color=C_ASSE)
    pan, pan_carry = build_pan(asse, seaflo, seaflo_carry, asse_carry)
    a.add(pan, name="asse-drip-pan", color=C_PAN)
    mplate, _mplate_carry = build_moisture_plate(pan_carry, asse_carry)
    a.add(mplate, name="moisture-plate", color=C_PLATE)
    split, split_carry = build_split(asse_carry)
    a.add(split, name="water-split", color=C_SPLIT)
    flowreg, flowreg_carry = build_flowreg(split_carry)
    a.add(flowreg, name="flow-regulator", color=C_FLOWREG)
    disch, disch_carry = build_discharge_chain(foam_carry, seaflo_carry)
    a.add(disch, name="discharge-chain", color=C_SUCT)
    # Each rib the cap prints against the sections of the chain it stands under, read back off
    # the placed body — the same reading the pump's four columns take. Both chains are down by
    # here, and a rib answers to the one it holds.
    a.anchors = anchor_rows(foam_carry, {"discharge-chain": (disch_carry, _dis),
                                         "suction-chain": (chain_carry, _suct)})
    check_anchor_lands(a.anchors)
    check_tie_vocabulary()
    bulkhead, bulkhead_carry = build_bulkhead(asse_carry)
    a.add(bulkhead, name="bulkhead-water", color=C_BULKHEAD)
    deck_solids, panel_carries = build_deck(a.deck_z, a.gate_z, seat=True)
    meter_carry = panel_carries.pop("digiten-flow")
    for name, solid in deck_solids.items():
        a.add(solid, name=name, color=C_DIGITEN if name == "digiten-flow" else C_BULKHEAD)
        # THE BAND IS THE ONE THAT BODY'S OWN STOREY WAS STRUCK ON, and the two storeys here were
        # struck on two different ones. `deck_z` drops its four and stands them where the least
        # still has a `DECK_CLEAR` of fall; `flavor_storey` carries the gate lane's pair over the
        # pump's FEET, which is `PORT_FOOT_CLEAR` — a barrel passing the widest section the
        # casting has, above which the lane opens by twenty millimetres.
        note_room(name, "fall onto what stands under it",
                  PORT_FOOT_CLEAR if name in PANEL_ON_GATE_LANE else DECK_CLEAR,
                  deck_fall[name] if name in deck_fall
                  else descent(solid, _would_land_on(box(solid), under_deck)))
    trays = {n: s for n, s in deck_solids.items() if n != "digiten-flow"}
    check_port_pair(trays, west_seam_crown(), seaflo)
    meter = deck_solids["digiten-flow"]
    a.panel_carries = panel_carries
    # The wall's five crossings, all placed by here. The field, the rings and the bores are all
    # struck off this one reading.
    a.wall_stations = wall_stations(bulkhead_carry, panel_carries, co2in_carry)
    # The rings go down after the fittings that trap them, on the same columns their pockets were
    # struck on. They lie OUTBOARD of the +Y wall of back-top's outer face, in the field the wall raises.
    for name, solid, colour in build_bulkhead_rings(a.wall_stations):
        a.add(solid, name=name, color=colour)
    # And outboard of two of them, the tube the customer cuts and the collar that carries the
    # station's word out to the end they cut it at.
    for name, solid, colour in build_customer_tubes(bulkhead_carry, panel_carries, co2in_carry):
        a.add(solid, name=name, color=colour)
    # And the nameplate, in the field those rings leave east of the flavour pair — the same
    # pocket floor, one plate's thickness inside the wall's outer face.
    for name, solid, colour in build_nameplate(foam):
        a.add(solid, name=name, color=colour)

    # The runs between placed bodies. Their frames come off the poses above, so a waypoint
    # measured off a port moves when the body it is on moves.
    carries = {"foam-assembly": foam_carry, "seaflo-pump": seaflo_carry, "suction-chain": chain_carry,
               "discharge-chain": disch_carry,
               "compressor": comp_carry, "condenser+fan": cond_carry,
               "asse1022-assembly": asse_carry, "water-split": split_carry,
               "flow-regulator": flowreg_carry, "vk-solenoid": vk_carry,
               "bulkhead-water": bulkhead_carry, "co2-inlet": co2in_carry,
               "gasher-co2": gasher_carry,
               "wr1110": wr1110_carry, "digiten-flow": meter_carry, **panel_carries}
    solids = {"foam-assembly": foam, "seaflo-pump": seaflo, "suction-chain": chain,
              "discharge-chain": disch,
              "compressor": comp, "condenser+fan": cond,
              "asse1022-assembly": asse, "water-split": split,
              "flow-regulator": flowreg, "vk-solenoid": vk,
              "bulkhead-water": bulkhead, "co2-inlet": co2in, "gasher-co2": gasher,
              "wr1110": wr1110, "digiten-flow": meter, **trays}
    # The pack's own bodies, so a run may anchor on one or measure off one. The stations answer
    # in `manifold_layout`'s world and ride the pose this module stood them in.
    for name, solid, _colour in stood:
        solids[name] = solid
        if name in _lines.STATIONS:
            carries[name] = mcarry
    a.bulkhead_carry = bulkhead_carry
    a.asse_cradle = asse_cradle(asse_carry)
    a.digiten_anchors = digiten_anchors(meter_carry)
    a.runs = []
    # The bodies and their placements, carried on the assembly: a run whose other mouth is on
    # something the BOX seats is drawn after the box exists, and it anchors on these same frames.
    a.pack_solids, a.carries = solids, carries
    draw_runs(a, _lines.build_runs(solids, carries))
    # AND THE ANCHORS ON THOSE LINES, struck on the runs themselves so a reroute carries them.
    a.tube_anchors = tube_anchors(a.runs)
    # The cold core's own ribs that hold a run are kept apart from those: `a.tube_anchors` is what
    # the BOX builds from, and a station on the core has no business being handed to a wall. Both
    # hold a run, so `tube-anchored` counts them together.
    a.cap_tube_anchors = cap_tube_anchors(carries["foam-assembly"], a.runs)
    # And the ribs the box stands for a BODY. The wall builds these from the same station shape,
    # and `tube-anchored` counts none of them: they hold no run.
    a.body_anchors = body_anchors(carries)
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
    a.seats = dict(SEATS)
    a.bounds = list(BOUNDS)
    return a


def draw_runs(a: cq.Assembly, runs) -> None:
    """Sweep each run at its own bore, add it to the assembly in the colour of the spool it is
    cut off (`_routing.SPOOLS`), and carry the runs and the port frames they were drawn from.
    Called once for the pack's own runs and again for the ones a body the box seats is an end
    of."""
    for run, (name, solid) in zip(runs, _lines.tubes(runs)):
        _ROUTED.add(name)
        a.add(solid, name=name, color=_routing.tube_color(run.id))
    a.runs = list(a.runs) + list(runs)
    a.frames = _lines.frames(a.pack_solids, a.carries)


def check_bodies_colored(a: cq.Assembly) -> Bound:
    """Whether every body in the machine says what it is made of.

    A body carrying no colour is drawn in the viewer's own default gray. THE MATERIAL IS THE
    COLOUR, so this reads the half that is stated here; what carries a stated colour through to
    the viewer is `_cadq_export._per_solid_color`, and `_mesh_payload`'s selftest is what holds
    it."""
    drawn = _solids(a)
    bare = sorted(n for n, (_s, color) in drawn.items() if color is None)
    return record_bound(Bound(
        "bodies-colored", "Every body carries the colour of what it is made of", not bare,
        f"{len(drawn) - len(bare)}/{len(drawn)} coloured", "every body coloured",
        [f"`{n}` names no colour and draws default gray. Give it the `M_*` constant for its own "
         f"material, or state one for a material this file does not carry yet." for n in bare]))


def _solids(a: cq.Assembly):
    """The bodies a box reads a pack in, world-placed and keyed by name.

    THE CORE IS ONE BODY TO THE PACK. The assembly exports the core's own bodies so a reader
    can open the machine and reach them, but nothing in this file is measured against them:
    every lane, clearance, stop, hold and station is struck off `foam-assembly`'s faces, and
    the core is a closed block of foam to all of them. So the core's bodies come out of this
    reading and the envelope goes back in, and a pass over a machine reads what it always did.

    What reads the bodies themselves is the STEP, and `manifold_layout.clashes`, which walks
    `a.children` because a solid nobody can see is still a solid in the way."""
    inside = getattr(a, "core_body_names", frozenset())
    out = {name: (shape, colour) for name, shape, colour in ml.placed_leaves(a)
           if name not in inside}
    if getattr(a, "core_envelope", None) is not None:
        out["foam-assembly"] = (a.core_envelope, C_FOAM)
    return out


def _core_solids(a: cq.Assembly):
    """The cold core's own bodies as the machine stands them — the half `_solids` leaves out.

    `_solids` reads the pack, where the core is one envelope. This is its complement: the bodies
    the STEP carries, already placed, for a reader that wants the core where the machine puts it
    rather than the block it fills. Together the two are every child of the assembly.

    UNDER THE CORE'S OWN NAMES. The STEP stands them in a `cold-core/` sub-assembly so a reader
    of the appliance can take the core in one, but that prefix is the machine's way of saying
    what holds them. The core's card, its payload and the scene tables all speak the plain
    names, and so does this."""
    inside = getattr(a, "core_body_names", frozenset())
    return {name: (shape, colour) for name, shape, colour in ml.placed_leaves(a)
            if name in inside}


# Bodies seated THROUGH a wall rather than standing inside it. Each one takes a hole in the skin
# and reaches out the far side — the six fittings clamped in theirs, the ASSE drip pan drawing in and
# out of its slot with `PAN_PROUD` of tab standing outside. So its box is not a box the interior
# has to hold: a pack sized to contain one is a pack built around its own skin. They come back as
# stations on the wall instead, and the wall is cut for them.
#
# The funnel is the same case and is not listed, because it is added after the box exists
# (`build_enclosure_assembly`) rather than to the pack.
THROUGH_WALL = ("bulkhead-water", "c14-inlet", "co2-inlet",
                "bulkhead-flavor-a", "bulkhead-flavor-b", "bulkhead-carb", "asse-drip-pan")
# And the bodies seated IN a wall rather than inside the box. A chip and its word lie in a pocket
# cut into the +Y wall of back-top's own outer face, so every millimetre of both is inside the wall's
# thickness and none of it is in the room the pack stands in. They are left out of what the box is
# sized on for the same reason as `THROUGH_WALL` and measured against the ceiling for none of them
# — a body with nothing inside the skin is under no ceiling of the interior.
IN_THE_WALL = tuple(name(which)
                    for _m, _r, which, _fluid in Y_WALL_FITTINGS.values()
                    for name in (ring_name, word_name))
# And the bodies standing OUTBOARD of it: on two of the five crossings, the tube the customer cuts
# in their own kitchen and the collar that carries the station's word out to the end they cut it
# at. The wall's outer face is where the machine stops, so none of this is in the room the pack
# stands in — it is the customer's own plumbing, drawn as far as the collar and no further
# (`build_customer_tubes`). Left out of what the box is SIZED on for that reason: sized on it, the
# depth the appliance states would be the depth of the appliance plus a stub of someone's kitchen,
# and the +Y wall of back-top would be drawn out to enclose a tube that has to leave the box to be any use.
OUTBOARD = tuple(name(Y_WALL_FITTINGS[station][2])
                 for station in CUSTOMER_TUBE_STATIONS
                 for name in (customer_tube_name, collar_name, collar_word_name))


# The bodies intentionally admitted into the ceiling's deeper structural field and captured
# rails. A relief is derived from the exact purchased solid where it enters that raw moving
# envelope; naming this population keeps an unrelated future encroachment visible to
# `pack-closes` instead of silently pocketing around it. Two millimetres in plan is assembly slip
# and one above the hit is the roof clearance.
CEILING_RELIEF_BODIES = (
    "c14-inlet", "asse1022-assembly", "co2-inlet",
    "bulkhead-water", "bulkhead-carb", "digiten-flow",
)
CEILING_RELIEF_PLAN_SLIP = 2.0
CEILING_RELIEF_Z_CLEAR = 1.0


def ceiling_reliefs(placed: dict) -> tuple:
    """Body-derived pockets in the ceiling panel's unrelieved field and rails."""
    raw = _cpanel.structural_stock().fuse(_cpanel.rail_stock())
    reliefs = []
    for name in CEILING_RELIEF_BODIES:
        if name not in placed:
            continue
        hit = raw.intersect(placed[name][0])
        if hit.Volume() <= 1e-6:
            continue
        b = hit.BoundingBox()
        reliefs.append((
            name,
            b.xmin - CEILING_RELIEF_PLAN_SLIP,
            b.xmax + CEILING_RELIEF_PLAN_SLIP,
            b.ymin - CEILING_RELIEF_PLAN_SLIP,
            b.ymax + CEILING_RELIEF_PLAN_SLIP,
            min(_cpanel.underside_z, b.zmax + CEILING_RELIEF_Z_CLEAR),
        ))
    return tuple(reliefs)


def pack(a: cq.Assembly = None) -> "_enc.Pack":
    """What the box is SIZED ON: the bodies that have to fit inside it.

    `THROUGH_WALL`, `IN_THE_WALL` and `OUTBOARD` are what that excludes — a body crossing the
    wall, one lying in its thickness, and one standing beyond it — and the funnel is the same
    case by a different route.

    `front_ports` is empty and stays empty. The box is four printed pieces and every face is a
    wall of one of them — there is no front panel to cut through — so that field is settled,
    not unfinished."""
    a = build_pack() if a is None else a
    placed = _solids(a)
    pan = box(placed["asse-drip-pan"][0])
    west = west_interior_face()
    outside = (set(THROUGH_WALL) | set(IN_THE_WALL) | set(OUTBOARD)
               | {NAMEPLATE, NAMEPLATE_INK})
    return _enc.Pack(placed={n: v for n, v in placed.items() if n not in outside},
                     west_ports=west_wall_ports(pan), pan_sleeve=pan_sleeve(pan, west),
                     back_ports=(y_wall_ports(a.bulkhead_carry, *a.panel_carries.values())
                                 + [c14_cutout(), co2_wall_port(a.co2_inlet_carry)]),
                     c14=c14_stations(), east_bosses=a.east_bosses,
                     side_wells=a.side_wells, floor_bosses=a.floor_bosses,
                     west_cradle=a.west_cradle, cond_cradle=a.cond_cradle,
                     cond_mount=a.cond_mount, cond_airway=a.cond_airway,
                     asse_cradle=a.asse_cradle,
                     flow_meter_anchors=a.digiten_anchors,
                     tube_anchors=a.tube_anchors + a.body_anchors,
                     ceiling_reliefs=ceiling_reliefs(placed),
                     port_field=y_wall_field(a.wall_stations),
                     nameplate=nameplate_cut(placed["foam-assembly"][0]),
                     valve_trays=a.valve_trays, pump_trays=a.pump_trays,
                     core_stops=a.core_stops, core_holds=a.core_holds,
                     vent_chase=a.vent_chase, collet_plate=a.collet_plate)


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


def check_ceiling_panel_insertion(back_top) -> Bound:
    """Whether the ceiling's deeper field and rails can slide through back-top's open Y seam.

    This is a continuous motion bound, represented conservatively by the whole prism swept
    from the first pose with the panel aft edge at the seam through the installed pose. The
    C14 tunnel's upper cap travels on the panel; any fixed back-top material in this prism is
    therefore a real obstruction, even when both pieces are disjoint after assembly."""
    fixed = back_top.val() if hasattr(back_top, "val") else back_top
    volume = _cpanel.insertion_sweep().intersect(fixed).Volume()
    ok = volume <= 1e-3
    return record_bound(Bound(
        "ceiling-panel-slides-in", "The deep ceiling panel and rails slide through back-top",
        ok, f"{volume:.3f} mm³ of fixed back-top in its continuous sweep",
        "no fixed back-top material in the field-and-rail complete Y sweep",
        ([] if ok else [
            f"{volume:.3f} mm³ of back-top stands in the panel's insertion prism — move that "
            f"feature onto the panel or open the fixed piece; a clear installed pose does not "
            f"show that the ceiling can reach it."])))


def check_ceiling_fastener_direction() -> Bound:
    """The complete ceiling fastener stack, read in its installation direction.

    The assembly imports `ceiling_panel` without running that module's command-line assertions,
    so this repeats the one order that matters at machine level: head and bearing seat in fixed
    back-top first, panel insert and blind show-face cap above. A positive tip-air reading says
    the standard M3x10 stops before the blind end rather than jacking against the cap.
    """
    stack = (
        _cpanel.screw_head_face_z,
        _cpanel.screw_head_seat_z,
        _cpanel.screw_insert_open_z,
        _cpanel.screw_insert_end_z,
        _cpanel.screw_insert_bore_end_z,
        _cpanel.show_z,
    )
    ordered = all(a < b for a, b in zip(stack, stack[1:]))
    cap = _cpanel.show_z - _cpanel.screw_insert_bore_end_z
    ok = (ordered
          and _cpanel.screw_tip_air >= -1e-9
          and abs(cap - _enc.socket_cap) <= 1e-9)
    return record_bound(Bound(
        "ceiling-screws-enter-from-below",
        "Both ceiling screws enter from Z− and travel +Z into blind panel inserts",
        ok,
        (f"head z {_cpanel.screw_head_face_z:.2f}..{_cpanel.screw_head_seat_z:.2f}, "
         f"insert z {_cpanel.screw_insert_open_z:.2f}..{_cpanel.screw_insert_end_z:.2f}, "
         f"{_cpanel.screw_tip_air:.2f} mm tip air, {cap:.2f} mm blind cap"),
        "head below fixed seat below panel insert below an unpierced show face",
        ([] if ok else [
            "The ceiling fastener stack is not strictly ordered from its Z− head through the "
            "fixed boss and upward panel insert to a full blind cap, or M3x10 reaches the blind "
            "end. Restore the below-driven stack in `ceiling_panel` and `_back_top_ceiling`."])))


# --- the box those bodies stand in, and what is seated in its walls ---------

# THE BOX PRINTS IN ONE FILAMENT, and it is `M_PETGF_BLACK` — the exterior's own spool. Every
# piece takes that one value, so the standing box is the one colour it is; a seam is told by the
# geometry that makes one, and the pack behind the walls is read through x-ray.
from _materials import WALL_COLORS                     # noqa: E402


def funnel_centre(box):
    """The funnel collar's centre in plan: (x, y).

    Centred across the box, and standing its front edge on the box's own stated
    `enclosure.funnel_front_y`.

    THE FUNNEL IS WHERE THE USER POURS, so the funnel stands as far forward as the top wall
    lets it: `enclosure.funnel_front_y` is the display housing's own back plane, and what stops
    that plane going further forward is the BRIM rather than the throat — the flange overhangs
    the collar and has to land on top wall, which begins at the display facet's arris
    (`funnel-brim-lands`). What the housing then leaves the throat is `funnel-collar-frame`.

    THE DRAIN RIDES THE FUNNEL WHEREVER THAT PUTS IT, and the elbow under the spout turns the
    fall aft inside its own envelope — so nothing under the top wall has to be a berth wide
    enough for a fitting to hang in, and `drain-over-deck` is the reading that says the foot
    of it stands over the folded deck rather than in it."""
    ix0, ix1 = box.inner[0], box.inner[1]
    return ((ix0 + ix1) / 2.0, _enc.funnel_front_y + _funnel.collar_d / 2.0)


def build_funnel(box):
    """The static funnel (`funnel.py`, its own frame: collar-centre origin, z 0 the
    brim underside) seated in the top-wall opening — turned `FUNNEL_ROT` about its own Z,
    then set at `funnel_centre` with that underside on the box's outer top. `enclosure.py`
    cuts the opening from the same centre, so funnel and hole cannot drift apart.

    THE BRIM RIDES THE CEILING, AND SO DOES THE DRAIN. The funnel's underside bears on the top
    wall's outer face and `funnel.drop` is fixed, so every millimetre off
    `enclosure.appliance_height` is a millimetre off the drain's own height — and what that comes
    out of is the HEAD the gravity feed runs on. The elbow turns the fall itself, so no corner of
    the run is waiting on that height; what is left of it is the drop from the elbow's own mouth
    to V-B's collet, and `room-holds` on the card is where a ceiling that took one more millimetre
    would show up.

    Returns `(placed, carry)` like every other seated body, so the drain the funnel empties
    through rides the funnel."""
    cx, cy = funnel_centre(box)
    return seat_body(import_step(str(FUNNEL_STEP)).val(),
                     (((0.0, 0.0, 1.0), FUNNEL_ROT),), seat="funnel",
                     station=(((0.0, 0.0, 0.0), (0.0, 0.0, 1.0)),
                              (cx, cy, box.outer[5])))


def build_drain_joint(funnel_carry):
    """The funnel's disconnect, seated on the spout the funnel carries.

    Three bodies on one column, all of them read off `reference/funnel-drain-stub`'s own frame —
    origin the spout's exit face, +Z up into the funnel — so the joint's stack is stated once
    beside the parts and placed here:

      * the stub, up inside the silicone and down into the fitting, hidden at both ends;
      * the worm clamp, closed on the spout's land above the exit face;
      * the union ELBOW, its +Z collet face ON that exit face.

    THE FITTING IS WHAT TURNS THE FALL. The elbow turns inside its own envelope, so it stands
    one `elbow_connector.LEG` under the spout's exit face and hands `fluid-4` out along +Y —
    aft, on the storey the cap's open air is, heading the way the run is going. What that keeps
    the joint out of is the bay under the spout: the folded deck's two anchor tees crown one
    storey down there and the cold core packs the column in from behind, and `drain-over-deck`
    is the reading that says the fitting's foot stands over them.

    The funnel is turned about Z alone, so the spout's axis is still the world's, and the joint
    frame differs from the world by the drain's own position. Both of the elbow's legs lie on
    world axes there: +Z takes the stub the funnel carries, +Y hands the drain aft.

    Returns `(name, solid, colour, carry)` per body — the elbow's carry is what `fluid-4`
    anchors on now that it starts at a collet rather than at silicone."""
    _stub.joint_holds()
    drain, _axis = funnel_carry((_funnel.drain_local, (0.0, 0.0, -1.0)))
    origin = ((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    stub, _ = seat_body(_stub.build_stub().val(), seat="funnel-drain-stub",
                        station=(origin, drain))
    clamp, _ = seat_body(_stub.build_clamp().val(), seat="funnel-drain-clamp",
                         station=(origin, drain))
    union, union_carry = seat_body(_elbow.build_elbow_connector().val(),
                                   seat="funnel-drain-union",
                                   station=(_elbow.port("z"), drain))
    return (("funnel-drain-stub", stub, C_STUB, None),
            ("funnel-drain-clamp", clamp, C_WORM, None),
            ("funnel-drain-union", union, M_JG_BLACK_PP, union_carry))


def check_drain_over_deck(joint, pack) -> Bound:
    """Whether the funnel's drain joint stands clear over everything the pack puts beneath it.

    THE JOINT HANGS IN THE FOLDED DECK'S OWN BAY and not over open air. The spout comes down on a
    column the two anchor tees stand fore of, and their barrels crown one storey under the top
    wall; a fitting that reaches that storey is a fitting with nowhere to go, since the cold core
    packs the column in from behind. What buys the room is the ELBOW's own reach: it hangs one
    `elbow_connector.LEG` under the spout, and its foot stands over the barrels rather than
    beside them.

    Read in plan and not in box — a body the joint does not stand over is a body this says nothing
    about, however high it reaches."""
    j = box(cq.Compound.makeCompound(list(joint)))
    rows = []
    for name, solid in pack.items():
        # THE JOINT'S OWN FAMILY IS NOT SOMETHING IT STANDS OVER. The elbow is placed off the
        # funnel's spout by `funnel_carry`, and the clamp and stub are made up on it — so the
        # funnel is above its own drain by construction, and reading it as headroom under that
        # drain reports the design as a fault. Four bodies carry the name and only three of
        # them are hyphenated: `funnel-drain-clamp`, `-stub`, `-union`, and `funnel` itself.
        if name == "funnel" or name.startswith("funnel-"):
            continue
        b = box(solid)
        if b.xmin >= j.xmax or b.xmax <= j.xmin or b.ymin >= j.ymax or b.ymax <= j.ymin:
            continue
        rows.append((name, j.zmin - b.zmax))
    worst = min((g for _n, g in rows), default=None)
    under = [r for r in rows if r[1] < _card.CLEARANCE_FLOOR]
    return record_bound(Bound(
        "drain-over-deck", "The funnel's drain joint stands over the pack under its column",
        not under,
        "nothing stands under it" if worst is None else
        f"{len(rows)} under the joint's foot at z {j.zmin:.2f}, nearest {worst:.3f} mm",
        f"at least {_card.CLEARANCE_FLOOR:g} mm under the fitting's foot",
        [f"{n} crowns {-g:.3f} mm INTO the joint's own envelope" if g < 0 else
         f"{n} leaves {g:.3f} mm under the joint, inside the {_card.CLEARANCE_FLOOR:g} the "
         f"machine holds — `funnel.chute_h` and `ramp_angle` are what lower the drain, "
         f"and the fitting's own reach is `elbow_connector.LEG`"
         for n, g in sorted(under, key=lambda r: r[1])]))


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


# The cover plate is drawn in `enclosure.display_plane`'s own frame — +X the box's, +Y up the
# slope, +Z out at the user — so one turn about X lays its +Z on the facet's normal and its +Y
# up the slope. The display faces the user along its own −Y and the plate along its +Z, so the
# two tilts are the same quarter opposite ways about.
COVER_TILT = ((1.0, 0.0, 0.0), +45.0)

# The plate's origin is the centre of its TOP face, and its top face IS the 45° plane — so the
# point that origin lands on is `display_plane`'s own, and the seat has no offset of its own to
# state. `display_plane` is what the facet's own cuts are struck on, so the pocket and the pad
# that drops into it cannot land on two different frames.
COVER_ORIGIN = ((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))


def build_display_cover(box):
    """The printed border that fills the display inset and closes the 45° face flat.

    Its top face lies IN that face, and its back is one plane either side of a single step: the
    lap, one `display_inset_depth` down where the glass is under it, and the seat, one
    `display_cover_seat` down everywhere else, bearing on the land `_display_cuts` sinks to meet
    it. No pad stands off it. Two DIN 912 M3s come down through that seat into ruthex inserts in
    `enclosure-front-top`, each head landing in a flat counterbore under the 45° plane, so the
    glass under the border is captured between the bezel it sits in and the plate over it."""
    plane = _enc.display_plane(box.outer)
    return seat_body(_cover.build_display_cover().val(), turns=(COVER_TILT,),
                     seat="display-cover",
                     station=(COVER_ORIGIN, plane.origin.toTuple()))


def build_display_gasket(box):
    """The TPU ring under the plate's lap, which is what the plate closes onto.

    It is drawn in the plate's own frame and seated on the same station, so the three of them —
    glass, ring, plate — stand on one origin and the stack is read off one plane."""
    plane = _enc.display_plane(box.outer)
    return seat_body(_dgasket.build_display_gasket().val(), turns=(COVER_TILT,),
                     seat="display-gasket",
                     station=(COVER_ORIGIN, plane.origin.toTuple()))


def _seated(box):
    """The box with every station its walls carry, seated. Each is read off the box itself,
    so the wall and the body it is cut for come out of one number. `enclosure.with_funnel`
    takes the throat's own reading against the frame the top wall has left as it seats it."""
    return _enc.with_funnel(box, funnel_centre(box))


def check_pumps_in_bay(placed: dict, shell) -> Bound:
    """Whether the pumps stand inside their bay's opening with air on the face they ride
    behind.

    The heads face the pump cartridge's own pump reliefs — one millimetre of air off each
    pocket's floor — and everything of a pump sweeps out through the bay, so its whole
    footprint stands inside the jambs by the deck's own sweep air. A touch has no volume,
    so `pack-closes` cannot see one; this reads both off the placed pumps."""
    bx0, bx1, top = shell.pump_bay
    rows, msgs = [], []
    for n, (s, _c) in placed.items():
        if not n.startswith("pump-"):
            continue
        b = box(s)
        if n.endswith("-head"):
            rows.append((n, b.ymin - _enc.pump_relief_floor))
            if b.ymin - _enc.pump_relief_floor <= 1.0 - 1e-6:
                msgs.append(f"{n} stands {b.ymin - _enc.pump_relief_floor:.2f} mm off its "
                            f"relief's floor — under the millimetre the pass-by keeps")
        margin = min(b.xmin - bx0, bx1 - b.xmax)
        rows.append((n, margin - _enc.bay_face_slip))
        if margin < _enc.bay_face_slip - 1e-6:
            msgs.append(f"{n} stands {margin:.2f} mm inside a jamb — the block's own edge is "
                        f"`bay_face_slip` {_enc.bay_face_slip:g} in from the jamb, and what "
                        f"the block carries has to stand inside that")
        if b.zmax > top - _enc.bay_crown_air + 1e-6:
            msgs.append(f"{n} crowns at z {b.zmax:.2f} against a bay top of {top:.2f}")
    ok = not msgs
    return record_bound(Bound(
        "pumps-in-bay", "The pumps stand inside the bay with air at the face and the jambs",
        ok,
        f"least air {min(g for _n, g in rows):.2f} mm" if rows else "no pumps placed",
        "a millimetre at the face, the deck's slip at the jambs, the crown air above",
        msgs))


def check_bay_lintel(shell, display_solid) -> Bound:
    """Whether the lintel over the bay keeps a ligament under the display's own envelope —
    the bay top is struck off the cans, and this is the wall the display answers for."""
    top = shell.pump_bay[2]
    dz = box(display_solid).zmin
    ok = dz - top >= 2.0 - 1e-9
    return record_bound(Bound(
        "bay-under-display", "The bay's lintel keeps a ligament under the display",
        ok,
        f"{dz - top:.2f} mm between the bay top and the display's envelope",
        "at least 2 mm of lintel",
        ([] if ok else [
            f"the bay tops at z {top:.2f} and the display's envelope begins at {dz:.2f} — "
            f"the opening cuts the wall the display stands in. Lower the cans, or raise "
            f"the display"])))


# How far down the reading looks before it says NOTHING IS THERE. Struck long on purpose: a
# ridge with nothing under it should report the drop it actually has, not the limit of the
# instrument, and the cavity under this one is the whole storey over the pump bay.
RIDGE_REACH = 60.0


def check_ridge_carried(pieces: dict, shell) -> Bound:
    """Whether the ridge the display's through-hole leaves is laid on printed material.

    `enclosure.pcb_ridge` is a line `display_pcb_x` long where the hole's up-slope end wall
    breaks out of the housing slab's back, and BOTH FACES POINT DOWN OFF IT. That makes it the
    bottom vertex of a wedge: 45° either side lays itself once the line exists, but the line
    itself is the one bead on this piece with nothing beneath it. It is not a wall too thin to
    print and it is not a clash — every volume in the box is right, every piece pair is clear,
    and the model is exactly what was drawn. It is a line the machine cannot begin.

    A THIRD THING SUPPORT CANNOT REACH IT. The ridge stands in the cavity behind the display
    housing, closed on five sides by the time the piece is off the bed, so the answer is
    printed section rather than a setting in the slicer — `enclosure._ridge_wall`.

    Read as a DROP: at stations across the ridge's own width, how far below it the piece's own
    material first stands, looking in a column one `EXTRUSION_W` wide hung off the ridge and
    aft of it. A carried ridge reads zero, because the rib's ramp contains the ridge line.
    An uncarried one reads the cavity, which is what it is — and if nothing stands within
    `RIDGE_REACH` the reading says so rather than reporting the instrument's own limit."""
    piece = pieces["front-top"]
    piece = piece.val() if hasattr(piece, "val") else piece
    ry, rz = _enc.pcb_ridge(shell.outer)
    half = _enc.display_pcb_x / 2.0
    cx = _enc.display_centre_x(shell.outer) + _enc.display_body_offset_x
    w = EXTRUSION_W
    rows = []
    for i in range(9):
        x = cx - half + w + (2.0 * half - 2.0 * w) * i / 8.0
        col = (cq.Workplane("XY").box(w, w, RIDGE_REACH, centered=False)
               .translate((x - w / 2.0, ry, rz - RIDGE_REACH)).val())
        got, vol = _overlap.common(piece, col)
        if vol < 1e-9:
            rows.append((x, None))
        else:
            rows.append((x, rz - _meshes.box(got).zmax))
    bad = [r for r in rows if r[1] is None or r[1] > w + 1e-9]
    worst = max((d for _x, d in rows if d is not None), default=None)
    return record_bound(Bound(
        "ridge-carried", "The ridge the display's through-hole leaves is laid on material",
        not bad,
        (f"{len(rows) - len(bad)}/{len(rows)} stations carried"
         + (f", furthest drop {worst:.4f} mm" if worst is not None else "")),
        f"material within one {w:g} mm extrusion under every station",
        [(f"x {x:8.3f}   nothing within {RIDGE_REACH:g} mm below" if d is None
          else f"x {x:8.3f}   drop {d:.4f} mm") for x, d in bad]))


def check_loom_passes(pieces: dict, shell) -> Bound:
    """Whether the enclosure display's loom still has its way through the ridge rib.

    `enclosure._ridge_wall` runs wall to wall, so it is the only section between the bay's
    storey and the cavity behind it, and SIG-7 crosses it. That makes the bore a PASSAGE, and a
    passage is the one thing this card's other readings cannot see: every one of them measures
    where a body stands, and no body stands in a hole. A later fuse landing in it — a boss, a
    rib, an anchor on that same face — closes the only route the loom has and moves nothing
    that anything else here reads.

    Measured as the passage's OWN RADIUS and measured exactly: the bore's axis, struck across
    the rib's thickness, at its exact distance from the printed piece. What comes back is the
    largest thing that goes through — so a boss fused into the bore reads as a smaller bore
    rather than as a volume, and the failure names the size that still passes.

    NOT AS OCCUPANCY. A cylinder of the bore's own diameter intersected with the piece reads
    0.09 mm3 on a bore that is perfectly clear: the wall is round, the boolean is meshed, and
    the facets of a tessellated cylinder fall inside the true one. That is the instrument
    talking, not the geometry, and thresholding it means picking a number that means nothing.
    An exact distance has no such term.

    The segment spans the rib and no further, so what this reads is the SECTION and not the
    corridor either side of it — a body standing off the bore's mouth is `clearance-floor`'s
    and `pack-closes`'s to find, not this one's."""
    piece = pieces["front-top"]
    piece = piece.val() if hasattr(piece, "val") else piece
    ry, rz = _enc.pcb_ridge(shell.outer)
    fore, t = shell.collet_plate["aft_y"], _enc.ridge_wall_t
    jog = (ry + rz) - fore
    axis_z = (shell.pump_bay[2] + jog) / 2.0
    d = _enc.cable_sleeve_open
    cx = _enc.display_centre_x(shell.outer)
    axis = cq.Edge.makeLine(cq.Vector(cx, fore, axis_z), cq.Vector(cx, fore + t, axis_z))
    dist = _BRepDist(axis.wrapped, piece.wrapped)
    if not dist.IsDone():
        raise RuntimeError(
            "loom-passes: the exact distance from the bore's axis to front-top failed — "
            "the passage is unknown, not clear")
    got = 2.0 * dist.Value()
    ok = got >= d - 1e-6
    return record_bound(Bound(
        "loom-passes", "The enclosure display's loom has a clear bore through the ridge rib", ok,
        f"{got:.4f} mm passes at x {cx:g}, z {axis_z:.3f}",
        f"a {d:.4g} mm bore clean through {_enc.ridge_wall_t:g} mm of rib",
        ([] if ok else [
            f"only {got:.4f} mm passes where the loom crosses — SIG-7 is four 22 AWG in a "
            f"{_enc.cable_sleeve_nom:g} mm expandable braid that opens to {d:.4g}, and this "
            f"rib is the only section it can cross. Move whatever narrowed the bore, or "
            f"move the bore"])))


def machine():
    """The pack, and the box around it. One build: the box is sized on the pack's bodies,
    and then carries the stations they seat in its walls.

    The box is SEATED before its ledger is carried, so the card holds the throat's three rows
    whether or not a wall is ever cut from this box."""
    a = build_pack()
    p = pack(a)
    box = _seated(_enc.stated_box(p))
    check_pumps_in_bay(p.placed, box)
    carry_enclosure_bounds()
    check_through_wall_headroom(a, box)
    a.bounds = list(BOUNDS)
    return a, p, box


def _materialized_enclosure_pieces(box, materialized=False) -> dict:
    """The enclosure producer's exact B-reps when the primary assembly action requests them.

    Direct design and presentation runs cut from source. The primary assembly action explicitly
    requests its declared producer outputs, preventing an ambient action environment from making
    another caller reach for files it did not stage.
    """
    if not materialized:
        return _enc.build_pieces(box)[0]
    root = _hw / "printed-parts" / "enclosure" / "enclosure"
    return {
        name: import_step(str(root / f"enclosure-{name}.step"))
        for name in _enc.PIECE_COLORS
        if name not in ("pump-cartridge", "pump-cap") or (box.pump_bay and box.collet_plate)
    }


def _materialized_ceiling_panel(box, materialized=False):
    """The ceiling producer's exact B-rep when explicitly requested; otherwise source geometry."""
    if not materialized:
        return _cpanel.build(box)
    return import_step(str(
        _hw / "printed-parts" / "enclosure" / "ceiling-panel" / "ceiling-panel.step"))


def build_enclosure_assembly(*, require_box_spec=False) -> cq.Assembly:
    """The pack, what is seated in the walls, and the four printable pieces of the box."""
    a, _p, live_box = machine()
    box = live_box
    if require_box_spec:
        import _box_spec

        box, bounds = _box_spec.read(
            _enc.Box, _enc.Bound, (_enc.PortField, _enc.Nameplate))
        if _box_spec.document(live_box, _enc.BOUNDS) != _box_spec.document(box, bounds):
            raise ValueError(
                "the materialized enclosure Box differs from the freshly derived placement; "
                "rebuild enclosure-box before composing the assembly")
        # Every materialized wall below was cut from this instance. Carry it through the
        # composition even when an equal live tuple happens to compare the same.
        _enc.BOUNDS[:] = bounds
    funnel, funnel_carry = build_funnel(box)
    a.add(funnel, name="funnel", color=C_FUNNEL)
    # The funnel is not in the pack — the box is sized on the pack and the funnel is seated in
    # the box — so the line it drains through is drawn HERE, off the same frames the pack's own
    # runs anchor on, with the funnel's now among them.
    a.pack_solids["funnel"], a.carries["funnel"] = funnel, funnel_carry
    check_bowl_clear(a.pack_solids["flow-regulator"], funnel)
    # The disconnect, on the spout the funnel carries. `fluid-4` starts at the union's lower
    # collet, so the joint goes in before the run is drawn.
    joint = build_drain_joint(funnel_carry)
    for name, solid, colour, carry in joint:
        a.add(solid, name=name, color=colour)
        if carry is not None:
            a.pack_solids[name], a.carries[name] = solid, carry
    # And what the joint stands over — the reading the elbow is in the machine for.
    check_drain_over_deck([s for _n, s, _c, _y in joint], a.pack_solids)
    draw_runs(a, _lines.build_seated_runs(a.pack_solids, a.carries))
    # WHERE THE MACHINE'S HEIGHT IS SPENT, recorded against the seat that spends it. The funnel's
    # brim bears on the top wall, so the drain hangs a fixed drop under the ceiling and the elbow
    # hands the line aft one leg below that — and what is left is the HEAD the gravity feed runs
    # on, the drop from that mouth to V-B's own collet. Every millimetre off
    # `enclosure.appliance_height`, and every millimetre `funnel.chute_h` takes for
    # capacity, comes out of this one.
    # THE DROP, AND NOT THE LENGTH. `fluid-4` carries head and is the funnel's air-purge path, so
    # what it owes is a line that never ends higher than it starts. A run measured by distance
    # reads a rise as room; measured by drop, a rise reads negative and the gate says so. The
    # band is the line's own bore: under one diameter of fall across a run this long there is no
    # grade left once the corners have taken their tangents, and the funnel stops draining dry.
    for r in a.runs:
        if r.id == "fluid-4":
            note_room("funnel", "the drop off the elbow `fluid-4` reaches V-B on",
                      _elbow.TUBE_D, r.pts[0][2] - r.pts[-1][2])
    display = build_display(box)
    # THE MODULE IS ONE BODY HERE AND TWO MATERIALS IN ITS OWN CARD. `waveshare_43b_display`
    # draws the main board in its own blue solder mask and the cover glass over it, and this
    # assembly compounds the pair into the one body every name-keyed reading downstream calls
    # `display` — a scene member, a scorecard pair, a probe tag. So it takes the colour of the
    # face the appliance shows: the glass in the facet, which is the whole of what a customer
    # ever sees of this part.
    a.add(display, name="display", color=C_DISPLAY_GLASS)
    # The bay's lintel against the display standing over it — the bay top rides the cans,
    # and this is the reading that says the opening stopped under the wall the display owns.
    check_bay_lintel(box, display.val() if hasattr(display, "val") else display)
    cover, _cover_carry = build_display_cover(box)
    a.add(cover, name="display-cover", color=C_COVER)
    dgasket, _dgasket_carry = build_display_gasket(box)
    a.add(dgasket, name="display-gasket", color=C_DGASKET)
    pieces = _materialized_enclosure_pieces(box, require_box_spec)
    for name, piece in pieces.items():
        a.add(piece, name=f"enclosure-{name}", color=WALL_COLORS[name])
    # AND BACK-TOP'S CEILING, which is a part of its own. It is built here rather than in
    # `build_pieces` because it is not one of the box's quadrants: `ceiling_panel` states the
    # joint's mating figures and back-top is cut to them, and what the panel needs from this
    # assembly is the two ceiling stations it carries.
    pieces["ceiling-panel"] = _materialized_ceiling_panel(box, require_box_spec)
    a.add(pieces["ceiling-panel"], name="enclosure-ceiling-panel", color=M_PETGF_BLACK)
    # Installed clearance is not insertion clearance: the panel traverses the whole rear
    # column before it reaches this pose. Read the deeper field's continuous sweep against the
    # fixed piece, including the C14 ownership split that makes the aft end pass.
    check_ceiling_panel_insertion(pieces["back-top"])
    # The fasteners answer to that same joint: both heads remain on fixed back-top's Z− face,
    # and both threads travel upward into blind inserts carried by the moving panel.
    check_ceiling_fastener_direction()
    # The chain against the piece that cradles it, once that piece exists — the one reading on
    # this card that can tell a anchor closed on the barrel from a anchor drawn near it.
    check_asse_seated(a.pack_solids["asse1022-assembly"], pieces["back-top"],
                      a.carries["asse1022-assembly"])
    check_digiten_seated(a.pack_solids["digiten-flow"], pieces["ceiling-panel"])
    # And every valve on a tray against the piece whose plate carries its four sockets — the
    # same reading, one storey forward: a plate drawn beside a valve rather than under it is a
    # plate nothing on this card would otherwise name.
    check_valve_trays_hold(pieces, a.pack_solids)
    # And each pump against the piece whose plate lies on its head, one storey up from those.
    check_trays_hold(pieces, a.pack_solids)
    check_cap_laps_bracket(pieces, a.pack_solids)
    check_cap_passes_tubes(pieces, a.pack_solids, box.collet_plate)
    # And the one line in that piece a nozzle would otherwise have to begin in air, against the
    # rib built to carry it — a reading of whether a body can be LAID, not of where it stands.
    check_ridge_carried(pieces, box)
    # And the one route through it, since that rib is now the only section between the
    # bay's storey and the cavity aft of it — a hole nothing else on this card can see.
    check_loom_passes(pieces, box)
    # And the floor that whole storey stands on, against the rim it stands on — then each
    # pump head against the lane it leaves the box through.
    check_bay_floor(pieces, box)
    # And the two posts that storey leaves standing either side of it — a reading of whether
    # section is PRESENT, which every clearance check on this card passes by definition.
    check_column_face(pieces, box)
    # And whether the release those figures serve can actually happen — the one reading on
    # this card that asks a body to move rather than asking where it is.
    check_release_travel(pieces, a.pack_solids, box.collet_plate)
    # And the same question asked backwards — what takes the push that seats a tube in a tee.
    check_insertion_backing(pieces, a.pack_solids, box.collet_plate)
    # And how much of each valve's post the plate actually surrounds, which is what holds a
    # valve — `valve-trays-hold` reads that one is near its plate and cannot read that.
    check_post_engagement(pieces, a.pack_solids, box.collet_plate)
    # And whether the wall between a seat's sockets and its port channel is thick enough for
    # the nozzle to lay anything in — the one reading here the solid itself cannot give.
    check_panel_web()
    check_head_sweep(a.pack_solids, pieces)
    check_pump_cartridge_sweep(pieces)
    # And the pump cartridge's own joint with what it lands against: the cap's aft face on the
    # steel.
    check_cap_stop(pieces, box.collet_plate)
    # And every floor post against the piece that grows it: a station outside every piece's
    # own Y column is not printed.
    check_floor_mounts(a.floor_bosses, pieces)
    # And the condenser's own four, which are a groove at one end of the block and a bored boss
    # at the other — the same question asked of a body with no hole to boss and one with two.
    check_cond_mount(a.cond_cradle, a.cond_mount, pieces)
    # And the two vents opposite that same block, which are its flanks' own flutes pierced — read
    # for the mullion between two slots, which is what a slot's width is measured against, and
    # for the height any one of those mullions stands free, which is what the transoms set. Both
    # bounds come off the one reading `check_flank_vents` takes.
    check_flank_vents(box, pieces)
    # And the cold core's four, which are the same question asked of a body with no hole at all:
    # two blocks on one piece's slab and two brackets off another's +Y wall of back-top, each read inside
    # the room it stands in.
    check_core_held(pieces, a.pack_solids["foam-assembly"], box)
    # And the slides themselves: each column's top swept its whole travel against its
    # bottom piece and lifted off its catch; the front column again with the flavour
    # pack aboard against the seated stratum; and the core's own ride in through the
    # mouth against the closed, populated back column.
    check_slides(pieces, box)
    check_slide_lanes(pieces, {**a.pack_solids,
                               **{n: s for n, (s, _c) in _solids(a).items()}}, box)
    check_core_ride(pieces, {**a.pack_solids,
                             **{n: s for n, (s, _c) in _solids(a).items()}}, box)
    # And every rear-wall fitting against the chip it bears on and the bore it passes. The chips
    # go into the assembly rather than the pack — they lie in the wall's own thickness — so they
    # come back off the placed children the way the runs do.
    check_wall_clamped(a.pack_solids,
                       {n: s for n, (s, _c) in _solids(a).items()
                        if n.startswith("bulkhead-ring-")}, pieces, a.wall_stations)
    # And the top row against the ceiling it runs out on, which is the one figure `bulkhead_ring`
    # cannot derive for itself.
    check_top_row(a.wall_stations)
    # And the nameplate against the field this wall leaves it — the one reading that can tell
    # `nameplate.WIDTH`, `HEIGHT` and `SCREW_Z` from figures this wall would actually take.
    check_nameplate(a.pack_solids["foam-assembly"], box)
    # And the pocket the wall actually cut against the outline that plate has. `pack-closes`
    # answers a pocket too small; this is the one that answers a pocket too large.
    check_nameplate_pocket({n: s for n, (s, _c) in _solids(a).items()}.get(NAMEPLATE),
                           pieces, a.pack_solids["foam-assembly"])
    # And both made-up chains against the cap they lie on, which needs no piece — the ribs are
    # printed in the core's own lid, so every solid in the reading is in the pack.
    check_chains_seated({n: a.pack_solids[n] for n in _cci.cap_anchors if n in a.pack_solids},
                        a.pack_solids["foam-assembly"])
    # And every anchored run against the rib its own site names.
    tubes = {n: s for n, (s, _c) in _solids(a).items() if n.startswith("tube-")}
    check_tube_seated(tubes, pieces)
    # And every body the box stands a rib for, against the same pieces.
    check_body_seated(a.pack_solids, pieces)
    # And every one of those ribs' zip tie channels, against the piece that built it. A seat that
    # reads closed on its body says nothing about whether a tie can reach round it.
    check_tie_channels(a.tube_anchors + a.body_anchors, a.digiten_anchors,
                         a.asse_cradle, pieces)
    # And every run the COLD CORE's cap is bored for, against the cap it lies on.
    check_run_seated(tubes, a.pack_solids["foam-assembly"])
    # And every body against the material it is made of, now that the box's own four stand among
    # them — the last body added is the last one that can be bare.
    check_bodies_colored(a)
    # The box's own group reads LAST on the card, under the pack's. `record_bound` carries an
    # id to the end of the ledger each time it is entered, so reading `enclosure`'s ledger again
    # here — after the bodies the box seats have stated theirs — is what puts it there.
    carry_enclosure_bounds()
    a.bounds = list(BOUNDS)
    # The box the pieces were cut from, carried like `runs` and `frames`.
    a.box = box
    # And the pack it was sized on, so a reader that wants both does not stand the
    # appliance a second time to get the half this one already has.
    a.pack = _p
    a.pieces = pieces
    a.seats = dict(SEATS)
    return a


def report(a: cq.Assembly, clashes=None) -> None:
    # THE PACK AND NOT THE EXPORT. `_solids` is where the two part company: the machine reports
    # on the core as the one body it seats, stops and holds, and what is inside that body is
    # reported by the core's own card beside `cold-core-assembly.step`.
    named = {n: s for n, (s, _c) in _solids(a).items()}
    placed = list(named.items())
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
    if "funnel" in named:
        line("funnel", box(named["funnel"]))
    if "suction-chain" in named:
        line("suction-chain", box(named["suction-chain"]))
    if "display" in named:
        line("display", box(named["display"]))
    if "display-cover" in named:
        line("display-cover", box(named["display-cover"]))
    if "psu" in named:
        line("psu", box(named["psu"]))
    for n in ("pcba", "relay-1", "relay-2") + WAGO_POLES + (
              "ground-stack", "asse1022-assembly", "asse-drip-pan",
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

    bad, unanswered = ml.clashes(a) if clashes is None else clashes
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
    # THIS FILE, UNDER THE NAME EVERYTHING ELSE IMPORTS IT BY. Run as a script it is `__main__`,
    # so a module that does `import enclosure_assembly` gets a SECOND copy — one that has built
    # nothing, whose `_ROUTED`, `TUBE_ANCHOR_SITES` and `BODY_ANCHOR_SITES` are empty, and which
    # therefore answers about a different machine. `_facts` read 67 manifold bodies where there
    # are 45; the scenes drew a different set of bodies and cropped to it. Both took a picture of
    # a machine nobody built. One name, one module, one machine.
    sys.modules.setdefault(__name__ if __name__ != "__main__" else "enclosure_assembly",
                           sys.modules[__name__])
    import _scorecard as _card
    if sys.argv[1:] == ["selftest"]:
        for line in selftest():
            print(" ", line)
        print("enclosure_assembly selftest OK")
        return
    # A trace models the action, including its producer handoffs. Ordinary direct runs set
    # neither variable and always rebuild the live Box and cold core from source.
    action = bool(os.environ.get("HSM_INPUT_DIGEST")
                  or os.environ.get("HSM_BUILD_SOURCE") == "trace")
    a = build_enclosure_assembly(require_box_spec=action)
    out = _here.parent / "enclosure-assembly.step"
    export_assembly(a, str(out))
    print(f"-> {out.name}")
    # `export_assembly` keeps the last good sidecar when tessellation fails so a drawing can
    # still be made from the STEP. That fallback is not safe here: the service scenes below
    # are composed from this payload, and grafting the flute skin would otherwise refresh an
    # old sidecar's mtime and make stale machine geometry look current.
    mesh = Path(str(out) + ".mesh")
    import _mesh_payload                                            # noqa: E402
    try:
        mesh_mtime = mesh.stat().st_mtime_ns
        step_mtime = out.stat().st_mtime_ns
        mesh_version = _mesh_payload.read_version(mesh)
    except Exception as exc:
        raise RuntimeError(f"{out.name} did not produce a readable mesh payload") from exc
    if mesh_version != _mesh_payload.VERSION or mesh_mtime < step_mtime:
        raise RuntimeError(
            f"{out.name} did not produce a current v{_mesh_payload.VERSION} mesh payload"
        )
    # AND THE FLUTED SURFACES BACK INTO THE PAYLOAD THE VIEWER READS. The export above writes
    # `<out>.mesh` off this B-rep, and the six enclosure pieces in it are smooth prisms there —
    # their show surfaces are in the printed mesh and not in the solid
    # (`printed-parts/enclosure/enclosure/flute_skin.py`). `loadStepFile` prefers that payload to
    # the STEP, so this is what the appliance looks like on /3d and in every picture posed off it.
    #
    # IMPORTED HERE AND NOT AT THE TOP. This module is imported by most of the generators in the
    # tree, and `flute_payload` pulls in a decimator and a proximity index that only the run
    # which cuts the appliance ever uses. The read is still traced, so the graph declares it.
    import flute_payload                                                # noqa: E402
    grafted = flute_payload.graft(mesh, flute_payload.surfaces())
    if grafted:
        print(f"-> {out.name}.mesh  ({grafted} fluted piece(s))")
    # The waterjet's file for the one steel piece, off the same spec the pockets and the
    # pump cartridge's stops were struck from.
    dxf = _here.parent / "collet-plate.dxf"
    export_collet_plate_dxf(a.collet_plate, dxf)
    print(f"-> {dxf.name}")
    report(a, _card.pack_clashes(a))
    _card.report(a)
    print(f"-> {_card.write(a, out).name}")
    # AND WHAT THE READERS READ, off this same machine. Eight doc drivers take their figures
    # from the artifact rather than standing an appliance apiece; writing it here is what makes
    # that one derivation instead of two.
    import _facts
    print(f"-> {_facts.write(whole=a, module=sys.modules[__name__]).name}")
    # THE VIEWER SCENES COME OFF THIS NAMED MACHINE while it is still in memory. Rebuilding the
    # same 296-solid appliance in a second action added minutes and could only restate what this
    # producer already knows. Card photographs remain their own browser-driven action.
    scene_dir = _hw / "assembly" / "scenes"
    if str(scene_dir) not in sys.path:
        sys.path.insert(0, str(scene_dir))
    import render_scenes
    render_scenes.write_glbs(a, require_core_payload=action)


if __name__ == "__main__":
    main()
