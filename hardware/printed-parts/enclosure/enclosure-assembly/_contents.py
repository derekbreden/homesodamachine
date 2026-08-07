"""Kitchen Edition enclosure contents — the refrigeration stratum at the front, the flavor
manifold standing on its crown, the cold core behind the pair, and the service deck on the
core's cap.

Four bodies mate face to face with nothing between them, and that mating is the machine's
whole plan:

    compressor-shroud   on the floor at the front, its INTAKE-side face against
    condenser+fan       beside it at the +X end of the same band
    manifold-layout     set down on the crown of those two, on its four spine hairpins
    foam-assembly       on the same floor, its front face on the plane the front pair ends at

The gaps are 0 by intent, and each mating face carries the joint that crosses it: the
compressor's discharge meets the condenser's inlet on the plane between them, the condenser's
liquid line meets the evaporator's inlet on the plane behind it, and the evaporator's outlet
meets the compressor's suction on the same plane at the other flank. No copper is visible
between any two of them.

[`/hardware/manifold-layout/front_half.py`](/hardware/manifold-layout/front_half.py) is that
stack on its own, mirror-symmetric about x = 0 and standing at the origin. Here it takes the
machine's frame: +X right/east, +Y back/aft, +Z up, origin at the lower-front-left corner of
the cavity. `MIRROR_X` is the plane the study's own x = 0 lands on — the cold core's plan
centre, which every one of the manifold's four limbs is placed about.

Strata, floor to ceiling:
  * Zone D:  the refrigeration stratum, front to `FRONT_DEPTH`, floor to `shroud_roof_z()`.
             The compressor upright in its shroud — the can's oil sits in its bottom and its
             pickup is gravity-fed, so upright is the compressor's constraint and the turn can
             only be a yaw — and the condenser beside it, its finstack's air axis across the
             machine.
  * Zone C:  the VALVE MANIFOLD, on that crown. Ten valves in four limbs, two pumps, eight
             junctions and the tube between them, all of it placed by
             [`manifold_layout`](/hardware/manifold-layout/manifold_layout.py) in its own frame
             and carried here on one seat. Two decks, the upper folded onto the lower about the
             hinge the four barb tees stand on; the pumps forward, the decks aft, six mouths
             leaving.
  * Zone A:  the COLD CORE behind them, floor to its cap top. Its port lanes run up the shell's
             ±Y walls at `MIRROR_X` ∓ `_cc.port_lane_mid_y` — world x 13 and 168 — which is
             where the manifold's own outer limbs stand.
  * Zone B:  the SERVICE DECK on the foam cap, in three lanes across the machine. West: the
             tap-water sequence — the ASSE 1022 chain on its own axis, the drip pan under its
             vent, the split and the flow regulator forward of it. Centre: the SeaFlo, motor
             axis front to back, the only axis it fits. East: the power block on the +X wall —
             brick, relay, hub and ground stud in one column, with the controller board forward
             of them on the same flank.
  * Zone C top: the hopper funnel, on the box's top wall directly behind the display facet.

Components only: no tubes, no wires, no mount features. The tube between the placed bodies is
[`_lines.py`](_lines.py); `enclosure_assembly.py` verifies the pack pairwise non-intersecting
at every export.
"""

import hashlib
import json
import math
import os
import sys
from pathlib import Path

import cadquery as cq
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
# _repo is this EDITION's root; tools/ is shared machinery with one copy at the
# repo root, so it gets its own anchor rather than a tools/ per edition.
_tools = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"
_hw = _repo / "hardware"

for _p in (_hw / "scripts", _tools,
           _hw / "manifold-layout",
           _hw / "printed-parts" / "cold-core",
           _hw / "printed-parts" / "cold-core" / "foam-assembly",
           _hw / "cut-parts" / "compressor-shroud",
           _hw / "reference" / "condenser-block",
           _hw / "reference" / "jg-bulkhead-union", _hw / "reference" / "iec-c14-inlet",
           _hw / "reference" / "derpipe-co2-inlet",
           _hw / "reference" / "gasher-check-valve", _hw / "reference" / "wr1110-regulator",
           _hw / "printed-parts" / "zone-c" / "hopper-funnel",
           _hw / "reference" / "asse1022-assembly",
           _hw / "reference" / "water-split", _hw / "reference" / "neofit-flow-control",
           _hw / "reference" / "seaflo-discharge-chain", _hw / "reference" / "seaflo-suction-chain",
           _hw / "reference" / "seaflo-22-pump",
           _hw / "reference" / "digiten-flow-sensor",
           _hw / "reference" / "beduan-solenoid", _hw / "reference" / "meanwell-irm90",
           _hw / "reference" / "wago-221-413", _hw / "reference" / "teyleten-relay",
           _hw / "reference" / "ground-ring-stack", _hw / "reference" / "kamoer-kphm400",
           _hw / "printed-parts" / "enclosure" / "drip-pan",
           _hw / "printed-parts" / "electronics",
           _hw / "printed-parts" / "electronics" / "ac-hub",
           _hw / "printed-parts" / "electronics" / "pcba-tray",
           _hw / "printed-parts" / "valve-manifold" / "single-valve-tray",
           _hw / "printed-parts" / "enclosure" / "enclosure"):   # `enclosure`, in placed_funnel
    sys.path.insert(0, str(_p))
import _boxes                            # noqa: E402
import _seating                          # noqa: E402  — a turn as a seat, for what carries a
                                         #   coordinate before the pack holds the body
import _placing                          # noqa: E402  — the seats every body in `_build` takes
from _placing import at, between, flush, off   # noqa: E402  — the planes those seats land on
import hopper_funnel as _funnel          # noqa: E402  — its neck offset, so the drain rides the part
import _cold_core_interface as _cc       # noqa: E402  — the shell's own footprint and port constants
import compressor_shroud as _shroud      # noqa: E402  — the shroud's four wall penetrations
import asse1022_assembly as _bfp         # noqa: E402  — its three terminals, in its own frame
import water_split as _split             # noqa: E402  — its three 1/4" collets, the same way
import neofit_flow_control as _flowreg   # noqa: E402  — its two 1/4" collets and its stem
import seaflo_discharge_chain as _disch  # noqa: E402  — its barb tip and its 1/4" collet
import seaflo_suction_chain as _suct     # noqa: E402  — the same two, less the check between
import seaflo_22_pump as _seaflo         # noqa: E402  — its two head barbs
import digiten_flow_sensor as _digiten   # noqa: E402  — its two 1/4" PTC collets, coaxial on ±X
import beduan_solenoid as _vk            # noqa: E402  — V-K's two 1/4" QC collets
import drip_pan as _pan                  # noqa: E402  — its lift, its section, its rail offset
import ac_hub as _achub                  # noqa: E402  — its lug stations and its plate's layout
import pcba_tray as _pcba                # noqa: E402  — the board's outline, holes and thickness
import single_valve_tray as _tray1       # noqa: E402  — the one-seat plate's reach and its two collets
import single_valve_assembly as _tray1_asm  # noqa: E402  — the plate with its valve on it
import ac_hub_assembly as _achub_asm     # noqa: E402  — the hub with its three lugs in
import meanwell_irm90 as _psu_ref        # noqa: E402  — the PSU's section and its two terminal ledges
import teyleten_relay as _relay_ref      # noqa: E402  — the relay's ends and its PCB
import ground_ring_stack as _gnd_ref     # noqa: E402  — the lug fan's own stack pitch
import condenser_block as _cond          # noqa: E402  — the block's envelope and its three picks
import foam_assembly as _foam_asm        # noqa: E402  — the cap's deck mounts, at its install spin
import jg_bulkhead_union as _jg          # noqa: E402  — the union's panel hole and its nut
import iec_c14_inlet as _iec             # noqa: E402  — the receptacle's cutout and its bezel
import derpipe_co2_inlet as _derpipe     # noqa: E402  — the CO2 inlet's collet and its stub tip
import gasher_check_valve as _gasher     # noqa: E402  — the check's socket mouth and its stub tip
import wr1110_regulator as _wr1110       # noqa: E402  — the regulator's two sockets
sys.path.insert(0, str(_hw / "printed-parts" / "cold-core" / "copper-plugs"))
import copper_plugs as _plugs            # noqa: E402  — the slot's three stations
from copper_plugs import slot_width_x as _slot_width  # noqa: E402  — and how wide the lane is


def _ml():
    """The manifold study, imported at call time — it reads this module's own collet figures,
    so the two meet through a function rather than through import order."""
    import manifold_layout
    return manifold_layout


# --- Room a derivation states and does not have ---------------------------
# A pose derived from a band, a strip, a lane or a standoff measures what it stands in. Where the
# measure comes up short the pose is still derived — the body lands where the arithmetic puts it,
# and `pack-closes`, `clearance-floor` and `lines-clear` read the overlap it makes — and the
# shortfall is recorded here for `room-holds` on the card. Keyed by the derivation that took the
# measurement, since two poses can be short in the same band.
#
# A reference STEP disagreeing with the module that draws it (`_metal_holds`) is not room: no
# body moving fixes it, so that one raises.
SHORT: dict = {}


def _short(who: str, why: str) -> None:
    """Record a derivation's own stated requirement coming up short."""
    SHORT[who] = why


# --- Source STEPs ---------------------------------------------------------
FOAM_ASSEMBLY = _hw / "printed-parts" / "cold-core" / "foam-assembly" / "foam-assembly.step"
COMP_SHROUD   = _hw / "cut-parts" / "compressor-shroud" / "compressor-shroud.step"
FUNNEL_STEP = _hw / "printed-parts" / "zone-c" / "hopper-funnel" / "hopper-funnel.step"
SEAFLO_STEP      = _hw / "reference" / "seaflo-22-pump" / "seaflo-22-pump.step"
DISCH_CHAIN_STEP = _hw / "reference" / "seaflo-discharge-chain" / "seaflo-discharge-chain.step"
SUCT_CHAIN_STEP  = _hw / "reference" / "seaflo-suction-chain" / "seaflo-suction-chain.step"
ASSE_STEP        = _hw / "reference" / "asse1022-assembly" / "asse1022-assembly.step"
WATER_SPLIT_STEP = _hw / "reference" / "water-split" / "water-split.step"
FLOWREG_STEP     = _hw / "reference" / "neofit-flow-control" / "neofit-flow-control.step"
DRIP_PAN_STEP    = _hw / "printed-parts" / "enclosure" / "drip-pan" / "drip-pan.step"
MEANWELL_STEP    = _hw / "reference" / "meanwell-irm90" / "meanwell-irm90.step"
PCBA_BOARD       = _hw / "printed-parts" / "electronics" / "pcba-tray" / "pcba-board.step"
AC_HUB_ASSEMBLY  = (_hw / "printed-parts" / "electronics" / "ac-hub"
                    / "ac-hub-assembly.step")
RELAY_STEP       = _hw / "reference" / "teyleten-relay" / "teyleten-relay.step"
GND_STACK        = _hw / "reference" / "ground-ring-stack" / "ground-ring-stack.step"
JG_BULKHEAD      = _hw / "reference" / "jg-bulkhead-union" / "jg-bulkhead-union.step"
IEC_C14          = _hw / "reference" / "iec-c14-inlet" / "iec-c14-inlet.step"
TRAY1_ASSEMBLY   = (_hw / "printed-parts" / "valve-manifold" / "single-valve-tray"
                    / "single-valve-assembly.step")
# The CO2 inlet chain — the DERPIPE panel fitting, the GASHER check threaded onto its stub,
# and the WR1110 secondary regulator one tube hop behind it. All three are authored +Y = flow.
DERPIPE_STEP     = _hw / "reference" / "derpipe-co2-inlet" / "derpipe-co2-inlet.step"
GASHER_STEP      = _hw / "reference" / "gasher-check-valve" / "gasher-check-valve.step"
WR1110_STEP      = _hw / "reference" / "wr1110-regulator" / "wr1110-regulator.step"
# The DIGITEN FL-S402B Hall-effect turbine meter, inline on the carb-water riser. Its own
# frame is +X = flow, the two 1/4" PTC collets coaxial on ±X, the pigtail boss leaving +Z.
DIGITEN_STEP     = _hw / "reference" / "digiten-flow-sensor" / "digiten-flow-sensor.step"


# --- The frame ------------------------------------------------------------
# Enclosure wall thickness (mirrors ../enclosure/enclosure.py `wall`).
WALL = 3.0
# The ±X walls stand one boss chain off the cold core, not against it. The core spans the
# interior wall to wall and floor to its cap, so a wall on its face leaves the seam machinery —
# corner posts, boss chains, Z-seam pods — nowhere to stand.
SIDE_RIB_INSET = 14.0
# The cold core's own two faces, and the datum the whole pack is struck off in X. The ±X boss
# band reaches one `enclosure.boss_in` back inboard from each wall and those two are the same
# number, so the band ends exactly on these faces — "clear of the seam furniture" and "standing
# over the core" are one test.
CORE_WEST_FACE = 0.0
CORE_EAST_FACE = _cc.outer_shell_y_length
# The machine's mirror plane. `manifold_layout` is drawn symmetric about its own x = 0 and the
# cold core is symmetric about its own long axis, so both land on this one plane and every
# twinned pair in the machine is a reflection in it.
MIRROR_X = (CORE_WEST_FACE + CORE_EAST_FACE) / 2.0
# The core's port LANES, in world. The shell keeps a bore-wide channel up each of its ±Y walls,
# clear of the reservoir pockets and inside the boss ring, and the yaw lays them across the
# machine. The manifold's outer limbs stand at ±`ml.OUTER_X` off the same mirror plane, which is
# these two columns to within half a millimetre — so a reservoir mouth aloft and the conduit it
# falls into share a column.
PORT_LANE_EAST = MIRROR_X + _cc.port_lane_mid_y
PORT_LANE_WEST = MIRROR_X - _cc.port_lane_mid_y
# The clearance floor a line keeps off a body, and the pitch two parallel lines run at.
LINE_HUG = 1.0                          # = scorecard.CLEARANCE_FLOOR
LINE_PITCH = 6.35 + LINE_HUG
# Degrees off a collet's own axis a straight tube still enters it unbent.
FLAVOR_SKEW = 22.0
CAP_BORE_SKEW = _cc.cap_conduit_entry_skew
# 1/4" LLDPE: the radius stock bends to on the bench, the radius a spool holds on its own, and
# what a corner is drawn to when nothing else asks.
LLDPE_MIN_BEND = 14.0
LLDPE_STOCK_BEND = 25.4
LLDPE_BEND = 4.0
LINE_STEP = max(LINE_PITCH, 2.0 * LLDPE_BEND)
WALL_SEQ_STRAIGHT = 2.0 * LLDPE_BEND
JUNCTION_LEG_LEAD = 2.0 * LLDPE_BEND
DIVIDER_LEG_STRAIGHT = 3.0
# The front wall stands one wall off the pack, for the front column's Z-seam lip.
FRONT_STANDOFF = 3.0
# The back wall stands one wall behind the rearmost content, so that content seats flush against
# the rear Z-seam lip's inner face rather than against the wall itself. enclosure.py reads it
# from here as `rear_seam_clear`.
REAR_STANDOFF = 3.0
# How far forward of the rear standoff the back piece's corner furniture reaches INTO the ±X
# boss band. Stated rather than derived: the wall's furniture is a function of the box's size,
# the box is sized to the pack, and the pack is what this seats. `pack-closes` is the check.
REAR_CORNER_POST = 13.3
REAR_CORNER_COLUMN = 16.3               # = 2 × enclosure.socket_r
# The plane a body MOUNTED ON THE +X WALL stands its outer face on.
EAST_WALL_SEAT = CORE_EAST_FACE + SIDE_RIB_INSET - REAR_STANDOFF
# The interior REAR PLANE — the inner face of the back wall, STATED, the way
# `enclosure.appliance_height` states the ceiling. Depth is a bound, not a consequence.
REAR_PLANE_Y = 470.0
# And where the box splits front from back, on the same footing: the front half carries the
# refrigeration stratum and the manifold standing on it, the back half the cold core and the
# service deck on its cap. `enclosure._dims` seats the seam here and `_report_split` prints
# what each half then comes to against the H2C bed.
Y_SEAM = 200.0


# --- Zone D: the refrigeration stratum -------------------------------------
# The compressor stands UPRIGHT in its shroud on the floor, its own feet under it. Upright is
# the compressor's constraint, not the shroud's, so the turn can only be a yaw. `SHROUD_YAW` is
# the machine's own: it carries the shroud's native −X wall — the one the copper crosses — onto
# world +X, the plane the condenser stands against.
#
# The condenser takes the +X end of the same band, its west face on that plane, its 178 mm
# FACE_A front to back and its 151 mm FACE_B standing up. `BASE_YAW` is what the pair takes as
# ONE body: the mating is between the two of them and the turn is about where the block's own
# `AIRFLOW` axis ends up, so it is taken about the pair's combined centre and the plane between
# them rides along.
CONDENSER_AIRFLOW = _cond.AIRFLOW            # fan + finstack stack depth, along the flow
CONDENSER_FACE_A, CONDENSER_FACE_B = _cond.FACE_A, _cond.FACE_B
SHROUD_YAW = -90.0
BASE_YAW = -90.0
# Depth of the whole front stratum — the plane the cold core's front face lands on, and the one
# every joint crossing between the two of them stands on.
FRONT_DEPTH = CONDENSER_FACE_A
# The gap between the shroud's roof and the manifold standing on it. 0: the four spine hairpins
# ARE the mating surface, and the pump-head faces stand off the crown by what the hairpins reach.
CROWN_GAP = 0.0
# The gap between the shroud's roof and the condenser's, which is neither's business — the two
# bodies stand side by side on one floor and their crowns differ by whatever the parts are.
STACK_GAP = 6.0                              # = 2 × enclosure.z_joint_clear


# --- Zone A: the cold core -------------------------------------------------
# +90° about Z carries the shell's local +X axis onto world +Y, so its long axis runs front to
# back and its SHORT axis (`outer_shell_y_length`, 181) runs across the machine — which is the
# whole edition. `foam_shell_port` carries a station through this turn, so nothing downstream
# repeats it by hand.
FOAM_YAW = 90.0
# Floor parts are raised one wall, clearing the front pieces' bottom seam lip so the split can
# pull forward past them. The box floors to a fixed z = 0 datum, so raising them leaves the
# floor in place.
SEAM_CLEAR_LIFT = 3.0


# --- Zone B: the service deck ----------------------------------------------
# The SeaFlo lies motor-axis along Y with its base flat on the foam cap — the only axis its
# 187 mm fits. The yaw's SIGN is the tap-water sequence's: the head's two barbs leave the
# casting's ±Y side faces, and 270° lands the SUCTION on the machine's west, the lane the ASSE
# chain, the split and V-K all stand in, so the whole tap-water path is one lane and crosses
# nothing. The discharge then faces east, where the carb riser climbs.
SEAFLO_YAW = 270.0
# The chain on the pump's discharge, and the one on its suction. Both are authored +Z = flow;
# the turn swings that onto the machine's own horizontal.
DISCH_CHAIN_TURN = ((1.0, 0.0, 0.0), -90.0)
SUCT_CHAIN_TURN = ((1.0, 0.0, 0.0), -90.0)
DISCH_CHAIN_DROP = 16.7
DISCH_CHAIN_AFT = 17.7

# The ASSE 1022 chain runs FRONT TO BACK in the west lane, hard against the −X wall's inset,
# with the drip pan under it. `ASSE1022_YAW` puts its inlet AFT at the bulkhead that feeds it
# and its outlet forward at the split; `ASSE1022_ROLL` lays the vent HORIZONTAL and turns it
# INBOARD, so the stub sheds off its own outside into a basin standing over the cold core
# rather than over the machine's west face.
ASSE1022_YAW = -90.0
ASSE1022_ROLL = -90.0
ASSE_INLET_HOP = 10.0        # the least tube between the panel's mouth and the chain's
# The basin's own plan, wall face to wall face; the rim reaches one `_pan.FLANGE_W` past each.
DRIP_PAN_X, DRIP_PAN_Y = _pan.PAN_X, _pan.PAN_Y
DRIP_RAIL_H = 3.0
DRIP_STOP_T = 3.0
# The split, inline on the chain's own flow axis: supply to the aft end of the run, branch off
# −X onto +X.
SPLIT_ROLL = 0.0
SPLIT_PITCH = 180.0
# The regulator, the sequence's third fitting, inline on the split's flavor collet.
FLOWREG_TURNS = (((0.0, 0.0, 1.0), -90.0), ((0.0, 1.0, 0.0), 90.0))
FLOWREG_DROP = 3.0
FLOWREG_RUN = FLOWREG_DROP / math.tan(math.radians(21.0)) - 4.0
# V-K, the fill/shutoff solenoid between the split and the SeaFlo's suction, on the family's
# one-seat plate. Its lane is the same west one, forward of the pump's own suction barb.
VK_TRAY_YAW = 0.0
# The carb riser's flow meter, aloft over the pump's east flank on the riser's own aft leg.
DIGITEN_YAW = 90.0

# The power block on the +X wall, in one column off the cap: the brick, the relay on its crown,
# the hub over that and the ground stud over that. Each takes `EAST_WALL_SEAT` as its east face
# — the plane the ±X rib band ends on — so the whole column stands clear of every post, pod and
# plug the Y seam puts in that band.
PCBA_YAW = 270.0 + FOAM_YAW
RELAY_YAW = 180.0 + FOAM_YAW
PCBA_TURN = (((0.0, 0.0, 1.0), PCBA_YAW), ((0.0, 1.0, 0.0), -90.0),
             ((0.0, 0.0, 1.0), 180.0))
RELAY_TURN = (((0.0, 0.0, 1.0), RELAY_YAW), ((0.0, 1.0, 0.0), 270.0))
PSU_TURN = (((0.0, 0.0, 1.0), 270.0 + FOAM_YAW), ((0.0, 1.0, 0.0), -90.0))
AC_HUB_TURN = (((0.0, 0.0, 1.0), 90.0), ((0.0, 1.0, 0.0), 270.0))

# The CO2 chain, wall-hung off the rear panel and running forward over the pump's crown, both
# bodies yawed a half turn so their flow runs forward.
CO2_YAW = 180.0
CO2_HOP = 10.0
CO2_HOLE_D = _derpipe.SHANK_D + 0.8   # clears the DERPIPE's 1/4" NPT shank
CO2_MADE_UP_TOL = 1e-6
DERPIPE_WRENCH_CLEAR = 2.0

FUNNEL_ROT = 0.0


# --- Colors ---------------------------------------------------------------
# The manifold's bodies keep the study's own colours (`ml.posed_bodies`); everything the machine
# adds around them is here.
COLORS = {
    "foam-assembly":     cq.Color(0.55, 0.75, 0.95, 0.55),
    "compressor-shroud": cq.Color(0.60, 0.62, 0.66),
    "condenser+fan":     cq.Color(0.78, 0.55, 0.35),
    # Zone B — the water deck
    "seaflo-pump":       cq.Color(0.30, 0.45, 0.70),
    "discharge-chain":   cq.Color(0.72, 0.72, 0.76),
    "suction-chain":     cq.Color(0.72, 0.72, 0.76),
    "digiten-flow":      cq.Color(0.92, 0.92, 0.94),
    # The CO2 chain — red, the customer-wayfinding color the inlet carries
    "gasher-co2":        cq.Color(0.85, 0.35, 0.30),
    "wr1110":            cq.Color(0.72, 0.30, 0.26),
    "asse1022-assembly": cq.Color(0.80, 0.68, 0.35),
    "water-split":       cq.Color(0.85, 0.85, 0.88),
    "flow-regulator":    cq.Color(0.85, 0.85, 0.88),
    "vk-tray-assembly":  cq.Color(0.85, 0.78, 0.62),
    "drip-pan":          cq.Color(0.35, 0.55, 0.75, 0.60),
    # Zone B — the electronics column
    "pcba":              cq.Color(0.15, 0.45, 0.25),
    "psu":               cq.Color(0.20, 0.20, 0.24),
    "ac-hub":            cq.Color(0.90, 0.55, 0.20),
    "relay-1":           cq.Color(0.15, 0.35, 0.65),
    "ground-stack":      cq.Color(0.25, 0.60, 0.30),
    # Panel bodies, seated through the walls
    "bulkhead-flavor-a": cq.Color(0.85, 0.85, 0.88),
    "bulkhead-flavor-b": cq.Color(0.85, 0.85, 0.88),
    "bulkhead-carb":     cq.Color(0.55, 0.70, 0.90),
    "bulkhead-water":    cq.Color(0.85, 0.85, 0.88),
    "c14-inlet":         cq.Color(0.18, 0.18, 0.20),
    "co2-inlet":         cq.Color(0.85, 0.35, 0.30),
}


def _load(path):
    return cq.importers.importStep(str(path)).val()


def _rot(shape, axis, deg):
    return shape.rotate(cq.Vector(0, 0, 0), cq.Vector(*axis), deg)


# The core's quarter turn as a move. What rides the cap — a deck-mount station, the hub's own
# hold-down centroid — is an OFFSET from the core's plan centre, and takes this turn about it.
_FOAM_TURN = _seating.Seat.turn((0, 0, 1), FOAM_YAW)


def _face_of(axis):
    """The enclosure port convention (x±/y±/z±) for an outward axis. A rolled port
    points between two of them; it is named for the one it leans on hardest, ties
    going to the later axis, so a vent turned off vertical still reads as facing
    down rather than raising."""
    ax = [round(float(c), 9) + 0.0 for c in axis]
    i = max(range(3), key=lambda k: (abs(ax[k]), k))
    return "xyz"[i] + ("+" if ax[i] > 0 else "-")


_PLACED: dict | None = None
_PACK: _placing.Pack | None = None

# --- The editor's moves ------------------------------------------------------
# The 3D viewer's component editor drags a body and writes the move here, beside the .step:
#   { "<body>": [ { "translate": [dx,dy,dz], "rotate": {"axis":[x,y,z], "deg": d} }, … ] }
# Each entry is a list of steps in the order they were applied; a lone dict is one step. The
# pack takes them at `place` time and composes each onto the seat its body took, so a dragged
# body carries its own stations and every body seated on it (`_placing.Pack`). The moves load
# HERE, in the file that packs the machine, because `_lines`, `scorecard` and `enclosure` all
# read this one pack. An absent or empty file places the machine as authored.
MOVES_PATH = _here.parent / "enclosure-assembly.overrides.json"


def _moves() -> dict:
    try:
        data = json.loads(MOVES_PATH.read_text())
    except (FileNotFoundError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def build():
    """The placed pack: name → (solid, colour). Memoized — `enclosure._dims`, `_lines._frames`,
    `scorecard.PORTS` and the assembly all ask for it."""
    global _PLACED
    if _PLACED is None:
        _PLACED = _build()
    return _PLACED


def packed() -> _placing.Pack:
    """The pack itself — the placed bodies and the seat each took.

    `_build` fills it as it goes, so a pose derived mid-build reads the bodies placed ahead of
    it and `Pack` names any that are not."""
    if _PACK is None:
        build()
    return _PACK


def _world(body: str, station) -> tuple:
    """A placed body's own station in world, under this pack's port convention: `(pos, face)`.

    `station` is the `(position, outward axis)` pair the body's own module declares, in the
    body's own frame; the seat the body took carries it."""
    pos, axis = packed().port(body, station)
    return pos, _face_of(axis)


def _box(dx, dy, dz):
    return cq.Workplane("XY").box(dx, dy, dz, centered=(False, False, False)).val()


# --- Metal against the module that draws it --------------------------------
# A reference STEP and the python that declares its stations are two copies of one part. Where
# the pack seats a body BY a station, a STEP that has drifted from its module moves the metal
# and leaves the station behind — so the two are measured against each other at every build.
PORTED_BODIES = {
    "asse1022-assembly":     (_bfp.build,           ASSE_STEP),
    "water-split":           (_split.build,         WATER_SPLIT_STEP),
    "flow-regulator":        (_flowreg.build,       FLOWREG_STEP),
    "seaflo-pump":           (_seaflo.build,        SEAFLO_STEP),
    "discharge-chain":       (_disch.build,         DISCH_CHAIN_STEP),
    "suction-chain":         (_suct.build,          SUCT_CHAIN_STEP),
    "digiten-flow":          (_digiten.build_assembly, DIGITEN_STEP),
    "psu":                   (_psu_ref.build,       MEANWELL_STEP),
    "relay-1":               (_relay_ref.build,     RELAY_STEP),
    "ground-stack":          (_gnd_ref.build,       GND_STACK),
    "gasher-co2":            (_gasher.build,        GASHER_STEP),
    "wr1110":                (_wr1110.build,        WR1110_STEP),
    "pcba":                  (_pcba._build_board,   PCBA_BOARD),
    "ac-hub":                (lambda: _achub_asm.build_assembly(_achub.LAYOUT), AC_HUB_ASSEMBLY),
    "vk-tray-assembly":      (lambda: _tray1_asm.build(), TRAY1_ASSEMBLY),
}
PORTED_METAL_TOL = 1e-6
PORTED_VOLUME_TOL = 1.0


def _solid_of(shape):
    if hasattr(shape, "toCompound"):
        return shape.toCompound()
    return shape.val() if hasattr(shape, "val") else shape


def _measure(shape) -> dict:
    s = _solid_of(shape)
    b = s.BoundingBox()
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(s.wrapped, props)
    return {"box": (b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax),
            "vol": props.Mass()}


def _metal_holds():
    """Every ported body's committed STEP against the module that draws it."""
    for name, (build_fn, path) in PORTED_BODIES.items():
        if not path.is_file():
            raise FileNotFoundError(f"{name}: {path} is not on disk — rebuild it")
        a, b = _measure(_load(path)), _measure(build_fn())
        drift = max(abs(x - y) for x, y in zip(a["box"], b["box"]))
        if drift > PORTED_METAL_TOL or abs(a["vol"] - b["vol"]) > PORTED_VOLUME_TOL:
            raise ValueError(
                f"{name}: {path.name} and the module that draws it disagree — box off by "
                f"{drift:.4f} mm, volume by {abs(a['vol'] - b['vol']):.1f} mm³. The pack seats "
                f"this body by a station its module declares; rebuild the STEP.")


def _stations_hold():
    """Every reference module's own station check, before anything is placed."""
    _cond.stations_hold()


# --- The pack --------------------------------------------------------------

def manifold_pose() -> _seating.Seat:
    """The seat the whole manifold study takes in the machine: its own crown pose, then the
    mirror plane across and the climb onto the refrigeration stratum's roof.

    `MANIFOLD_LIFT` is what the four spine hairpins reach — the pack's own lowest point once
    turned — so the pack sets down on the crown by construction."""
    ml = _ml()
    pose = ml.crown_pose()
    low = min(_boxes.boxed(seat.then(pose).solid(s)).zmin
              for s, seat, _c in {**ml.posed_bodies(), **ml.posed_tubes()}.values())
    return pose.then(_seating.Seat.shift((MIRROR_X, 0.0, shroud_roof_z() + CROWN_GAP - low)))


_MANIFOLD_POSE = None


def manifold_seat() -> _seating.Seat:
    global _MANIFOLD_POSE
    if _MANIFOLD_POSE is None:
        _MANIFOLD_POSE = manifold_pose()
    return _MANIFOLD_POSE


# The study draws a valve in two solids and a pump in three, because a study is a picture. The
# machine's registry is one row per PART, so each group arrives here as one compound under the
# name `fluid-topology.md` calls it.
MANIFOLD_GROUPS = {f"v-{v}": (f"valve-v-{v}", f"coil-v-{v}") for v in "abcdefghij"}
MANIFOLD_GROUPS.update({p: (f"{p}-head", f"{p}-bracket", f"{p}-motor")
                        for p in ("pump-a", "pump-b")})
MANIFOLD_COLORS = {**{f"v-{v}": cq.Color(0.93, 0.93, 0.91) for v in "abcdefghij"},
                   "pump-a": cq.Color(0.55, 0.35, 0.55),
                   "pump-b": cq.Color(0.55, 0.35, 0.55)}


def manifold_bodies():
    """The manifold's parts as the machine registers them: `{name: (solid, seat, colour)}` —
    ten valves, eight tees, two elbows and two pumps."""
    ml = _ml()
    parts = ml.posed_bodies()
    seat = manifold_seat()
    grouped = {n for names in MANIFOLD_GROUPS.values() for n in names}
    out = {}
    for name, members in MANIFOLD_GROUPS.items():
        solid = cq.Compound.makeCompound(
            [parts[m][1].solid(parts[m][0]) for m in members])
        out[name] = (solid, seat, MANIFOLD_COLORS[name])
    for name, (solid, own, color) in parts.items():
        if name not in grouped:
            out[name] = (solid, own.then(seat), color)
    return out


def _build():
    global _PACK, _MANIFOLD_POSE
    _MANIFOLD_POSE = None
    _stations_hold()
    _metal_holds()
    pack = _PACK = _placing.Pack(_moves())
    placed = pack.solids
    ml = _ml()

    # --- Zone D: the refrigeration stratum, on the floor at the front. The pair is mated first
    # and turned as ONE body about its own centre, because the mating is between the two of them
    # and the turn is about where the block's air goes.
    shroud, cond = _base_solids()
    pack.pose("compressor-shroud", shroud[0], shroud[1])
    pack.pose("condenser+fan", cond[0], cond[1])

    # --- Zone C: the flavor manifold on their crown, every part on the study's own seat
    # composed onto the machine's.
    for name, (solid, seat, _c) in manifold_bodies().items():
        pack.pose(name, solid, seat)

    # --- Zone A: the cold core behind the pair, flat on the floor slab, its front face on the
    # plane the front stratum ends at. X is fenced by the seam posts standing on the footprint's
    # own ±X edges, +Y by the back Z-seam lip.
    pack.place("foam-assembly", _load(FOAM_ASSEMBLY), yaw=FOAM_YAW,
               west=at(CORE_WEST_FACE), front=at(FRONT_DEPTH), foot=at(0.0))

    # --- Zone B: the power block on the +X wall, seated first because the water deck's own
    # lane is what it leaves. Three faces of the machine and not three numbers: EAST on
    # `EAST_WALL_SEAT`, AFT on the rear seam lip's own standoff, FOOT on the cap's lid.
    pack.place("psu", _load(MEANWELL_STEP), turn=PSU_TURN,
               east=at(EAST_WALL_SEAT),
               aft=at(REAR_PLANE_Y - REAR_STANDOFF - REAR_CORNER_POST - LINE_HUG),
               foot=at(foam_cap_top()))
    # The relay STANDS ON THE +X WALL over the brick, its board's face to that wall and its
    # cans looking inboard — the face a screwdriver reaches and the face a boss lands on.
    pack.place("relay-1", _load(RELAY_STEP), turn=RELAY_TURN,
               east=at(EAST_WALL_SEAT), aft=flush("psu", "aft"),
               foot=off("psu", "crown", LINE_HUG))
    # The hub sits ON THE RELAY, its wells opening INBOARD off the wall, its aft face on the
    # C14's — the receptacle is the one body on this flank that comes inboard at this height.
    pack.place("ac-hub", _load(AC_HUB_ASSEMBLY), turn=AC_HUB_TURN,
               east=flush("relay-1", "east"), aft=at(c14_inboard_y() - LINE_HUG),
               foot=off("relay-1", "crown", LINE_HUG))
    pack.place("ground-stack", _load(GND_STACK), turn=RELAY_TURN,
               east=at(EAST_WALL_SEAT), aft=flush("ac-hub", "aft"),
               foot=off("ac-hub", "crown", LINE_HUG))
    # The controller board joins that column rather than standing forward of the deck: same
    # flank, same floor, one clearance floor ahead of the brick. The ROLL is what fits it —
    # a quarter turn about its own long axis lays that axis fore and aft down the flank, so
    # only the board's thickness reaches inboard.
    pack.place("pcba", _load(PCBA_BOARD), turn=PCBA_TURN,
               east=at(CORE_EAST_FACE - LINE_HUG),
               aft=off("psu", "front", LINE_HUG), foot=at(foam_cap_top()))

    # --- Zone B: the SeaFlo, in the lane the power block leaves, base flat on the cap and its
    # back face flush with the core's own.
    pack.place("seaflo-pump", _load(SEAFLO_STEP), yaw=SEAFLO_YAW,
               east=off("psu", "west", LINE_HUG),
               aft=flush("foam-assembly", "aft"), foot=at(foam_cap_top()))

    # --- Zone B: the tap-water sequence, all of it in the west lane. The chain hangs on the
    # station it is FED from, in all three coordinates: its inlet mouth and `bulkhead-water`'s
    # stand on one line, and `water-1` is the tube between them.
    pack.place("asse1022-assembly", _load(ASSE_STEP),
               # The roll is about the axis the YAW left the flow on — world Y, not world X.
               turn=(((0, 0, 1), ASSE1022_YAW), ((0, 1, 0), ASSE1022_ROLL)),
               station=_bfp.flow_axis(), port=asse_axis())
    # The split: its own RUN on the chain's flow axis — one plane with the outlet that feeds it,
    # so water-2 is a step and no fall.
    _out = bfp_terminal("tube-out")[0]
    pack.place("water-split", _load(WATER_SPLIT_STEP),
               turn=(((1, 0, 0), SPLIT_ROLL), ((0, 1, 0), SPLIT_PITCH)),
               org_x=at(_out[0]), org_y=at(split_y()), org_z=at(_out[2]))
    _flv = split_terminal("to-flavor")[0]
    pack.place("flow-regulator", _load(FLOWREG_STEP), turn=FLOWREG_TURNS,
               org_x=at(_flv[0]), org_y=at(flowreg_lane()),
               org_z=at(_flv[2] - FLOWREG_DROP))
    # The basin hangs off the CHAIN'S OWN PLAN BOX. X is the WALL's: the tray draws west through
    # the slot in it on rails rooted in its inner face, so the face it withdraws through is what
    # fixes it across the machine. Y CENTRES ON THE VENT and answers to nothing else.
    _vent_xy = bfp_terminal("vent-tip")[0]
    _pan_x = drip_pan_west()
    _pan_y = _vent_xy[1] - DRIP_PAN_Y / 2.0
    _pan_z = drip_pan_seat()
    _pan_room(_pan_x, _pan_y, _vent_xy)
    pack.place("drip-pan", _load(DRIP_PAN_STEP),
               org_x=at(_pan_x), org_y=at(_pan_y), org_z=at(_pan_z))
    # The two chains made up on the pump's own barbs, LYING ON ITS CROWN and running fore and
    # aft — one down each flank, each on the side of the barb it clamps onto. The crown is the
    # one plane on this deck as long as the chains are, and the hose between a barb and its
    # chain is what lets them ride it: nothing about either casting fixes the chain across the
    # machine, so what each owes the pump is reach and what it owes the box is to stay inboard.
    pack.place("discharge-chain", _load(DISCH_CHAIN_STEP), turn=(DISCH_CHAIN_TURN,),
               east=flush("seaflo-pump", "east") - LINE_HUG,
               aft=flush("seaflo-pump", "aft"),
               foot=off("seaflo-pump", "crown", LINE_HUG))
    pack.place("suction-chain", _load(SUCT_CHAIN_STEP), turn=(SUCT_CHAIN_TURN,),
               west=flush("seaflo-pump", "west") + LINE_HUG,
               aft=flush("seaflo-pump", "aft"),
               foot=off("seaflo-pump", "crown", LINE_HUG))
    # The carb riser's flow meter, on the same crown east of the discharge chain, its own flow
    # across the machine at the head of the riser's aft leg.
    pack.place("digiten-flow", _load(DIGITEN_STEP), yaw=DIGITEN_YAW,
               east=flush("seaflo-pump", "east") - LINE_HUG,
               aft=off("discharge-chain", "front", LINE_HUG),
               foot=off("seaflo-pump", "crown", LINE_HUG))
    # V-K on the family's one-seat plate, on the same crown INLINE WITH THE SUCTION CHAIN: its
    # outlet collet and the chain's face each other down one lane, one junction lead apart, and
    # its inlet looks forward at the split that feeds it. The whole tap-water path — bulkhead,
    # chain, split, this valve, the suction chain, the pump — then runs one way down the west
    # lane and crosses nothing.
    pack.place("vk-tray-assembly", _load(TRAY1_ASSEMBLY), yaw=VK_TRAY_YAW,
               west=off("suction-chain", "east", LINE_HUG),
               aft=off("suction-chain", "front", JUNCTION_LEG_LEAD),
               foot=off("seaflo-pump", "crown", LINE_HUG))

    # The CO2 chain's two inline bodies, wall-hung off the rear panel and running FORWARD over
    # the pump's crown. Each is seated by the MOUTH the chain closes on rather than by the face
    # its envelope ends at.
    pack.place("gasher-co2", _load(GASHER_STEP), yaw=CO2_YAW, station=_gasher.inlet(),
               port=co2_axis())
    pack.place("wr1110", _load(WR1110_STEP), yaw=CO2_YAW, station=_wr1110.inlet(),
               port=(co2_axis()[0], pack.port("gasher-co2", _gasher.outlet())[0][1] - CO2_HOP,
                     co2_axis()[2]))

    _joints_hold()
    colors = {**{n: c for n, (_s, _seat, c) in manifold_bodies().items()}, **COLORS}
    return {n: (s, colors[n]) for n, s in placed.items()}


def _base_solids():
    """The refrigeration pair, mated and then turned as ONE body about its own vertical centre,
    then seated — centred on the mirror plane and its front face on y = 0.

    Each comes back as `(solid as drawn, seat)`, so the ports both bodies declare reach world on
    the same move the metal took."""
    shroud = _load(COMP_SHROUD)
    s_seat = _seating.Seat.turn((0, 0, 1), SHROUD_YAW)
    s_box = _boxes.boxed(s_seat.solid(shroud))
    s_seat = s_seat.then(_seating.Seat.shift(
        (-(s_box.xmin + s_box.xmax) / 2.0, -s_box.ymin, SEAM_CLEAR_LIFT - s_box.zmin)))

    cond = _cond.build()
    cond = cond.toCompound() if hasattr(cond, "toCompound") else cond
    c_seat = _seating.Seat.turn((0, 0, 1), 90.0)
    c_box = _boxes.boxed(c_seat.solid(cond))
    s_now = _boxes.boxed(s_seat.solid(shroud))
    c_seat = c_seat.then(_seating.Seat.shift(
        (-(c_box.xmin + c_box.xmax) / 2.0, s_now.ymax - c_box.ymin, SEAM_CLEAR_LIFT - c_box.zmin)))

    # The pair's own combined box, and the yaw about the vertical through its centre. A yaw
    # about a centre is not a placement: the turn leaves the pair's front wherever its own width
    # used to reach, so the pair is seated again after it.
    boxes = [_boxes.boxed(s_seat.solid(shroud)), _boxes.boxed(c_seat.solid(cond))]
    cx = (min(b.xmin for b in boxes) + max(b.xmax for b in boxes)) / 2.0
    cy = (min(b.ymin for b in boxes) + max(b.ymax for b in boxes)) / 2.0
    spin = (_seating.Seat.shift((-cx, -cy, 0.0))
            .then(_seating.Seat.turn((0, 0, 1), BASE_YAW))
            .then(_seating.Seat.shift((cx, cy, 0.0))))
    s_seat, c_seat = s_seat.then(spin), c_seat.then(spin)
    turned = [_boxes.boxed(s_seat.solid(shroud)), _boxes.boxed(c_seat.solid(cond))]
    step = _seating.Seat.shift((
        MIRROR_X - (min(b.xmin for b in turned) + max(b.xmax for b in turned)) / 2.0,
        -min(b.ymin for b in turned), 0.0))
    return (shroud, s_seat.then(step)), (cond, c_seat.then(step))


# --- Zone D's own readings --------------------------------------------------

_SHROUD_ROOF = None


def shroud_roof_z():
    """The refrigeration stratum's crown — the higher of the shroud's roof and the condenser's,
    which is what the manifold's hairpins set down on."""
    global _SHROUD_ROOF
    if _SHROUD_ROOF is None:
        (sh, ss), (co, cs) = _base_solids()
        _SHROUD_ROOF = max(_boxes.boxed(ss.solid(sh)).zmax, _boxes.boxed(cs.solid(co)).zmax)
    return _SHROUD_ROOF


def shroud_port(name):
    """A compressor-shroud penetration in world: `(pos, face)`."""
    return _world("compressor-shroud", _shroud.port(name))


def condenser_port(name):
    """A condenser+fan pick in world, the same way."""
    return _world("condenser+fan", _cond.stations()[name])


# The three planes two bodies already share. Each is a mating face the machine is built on —
# the stratum's two halves against each other, and both against the cold core — so the gap
# across it is 0 and the pair is not a clearance to hold but a joint to make.
MATED_FACES = (
    ("compressor-shroud", "condenser+fan"),
    ("condenser+fan", "foam-assembly"),
    ("compressor-shroud", "foam-assembly"),
)


def butted_pairs():
    """Every pair of manifold bodies joined COLLET TO COLLET — tube in both quick-connects and
    none between them, so the two faces meet on one plane.

    Read off `manifold_layout.SEGMENTS`, which says how each of the manifold's twenty-one
    connections is made, so the pairs cannot drift from the chain that makes them."""
    ml = _ml()
    out = set()
    for _cid, frm, to, how in ml.SEGMENTS:
        if how != "butt" and not (how in ml.RUNS and ml.dist(*ml.RUNS[how]) <= 1e-9):
            continue
        a, b = (_manifold_body(frm), _manifold_body(to))
        if a and b and a != b:
            out.add(tuple(sorted((a, b))))
    return out


def _manifold_body(port_name):
    """The pack's own name for the body a manifold port stands on."""
    body = port_name.rsplit("-", 1)[0]
    if body.startswith("Y-"):
        return f"tee-{body.lower()}"
    if body.startswith("V-"):
        return body.lower()
    return {"P-A": "pump-a", "P-B": "pump-b"}.get(body)


# The refrigerant loop's three joints, each named by the two stations that make it up. Every
# one crosses a plane two bodies already share, so the pair is one point read twice and the
# copper between them is the length of the union, not a run.
REFRIGERANT_JOINTS = (
    ("compressor-shroud.refrig-discharge", "condenser+fan.refrig-inlet"),
    ("condenser+fan.refrig-outlet", "foam-assembly.evap-inlet"),
    ("foam-assembly.evap-outlet", "compressor-shroud.refrig-suction"),
)
JOINT_TOL = 0.05


def _joint_station(anchor):
    body, port = anchor.split(".", 1)
    return {"compressor-shroud": shroud_port, "condenser+fan": condenser_port,
            "foam-assembly": foam_shell_port}[body](port)


def refrigerant_joints():
    """Each joint's two stations and how far apart they stand: `[(a, b, mm), ...]`."""
    out = []
    for a, b in REFRIGERANT_JOINTS:
        pa, pb = _joint_station(a)[0], _joint_station(b)[0]
        out.append((a, b, math.dist(pa, pb)))
    return out


def _joints_hold():
    """The three joints measured, and the short recorded for any that does not close."""
    for a, b, gap in refrigerant_joints():
        if gap > JOINT_TOL:
            _short(f"refrigerant-joint-{a.split('.')[0]}",
                   f"{a} and {b} stand {gap:.2f} mm apart — the joint crosses a plane the two "
                   f"bodies share, so the pair is one point read twice and that distance is "
                   f"copper drawn in the open. Move one station onto the other.")


# --- Zone A's own readings --------------------------------------------------

def core_plan_centre():
    """The cold core's plan centre — the machine's own mirror plane, and the core's mid-depth."""
    b = packed().box("foam-assembly")
    return ((b.xmin + b.xmax) / 2.0, (b.ymin + b.ymax) / 2.0)


def foam_cap_top():
    """The service deck's floor: the foam cap's lid, less whatever a deck-mount column stands
    proud of it."""
    return packed().box("foam-assembly").zmax - _cc.deck_mount_proud()


def deck_mount(name):
    """One of the cap's deck-mount rectangles in world: `(centre, station points, top_z)`."""
    cx, cy = core_plan_centre()
    mount = _cc.deck_mounts[name]
    centre = _FOAM_TURN.point((mount.centre[0], mount.centre[1], 0.0))
    pts = [_FOAM_TURN.point((p[0], p[1], 0.0)) for p in _foam_asm.deck_mount_station(name)]
    return ((cx + centre[0], cy + centre[1]),
            [(cx + p[0], cy + p[1]) for p in pts],
            foam_cap_top() + mount.standoff)


TRAY_MOUNTS = {"vk-tray": "vk-tray-assembly"}


def tray_mount_holes(mount):
    """The two screw columns one tray mount stands on, in world plan."""
    return deck_mount(mount)[1]


def tray_mount_seat():
    """The plane a tray's own plate lands on."""
    return foam_cap_top()


def foam_cap_frame(p):
    """A world plan point back in the foam cap's own authoring frame."""
    cx, cy = core_plan_centre()
    back = _seating.Seat.turn((0, 0, 1), -FOAM_YAW)
    q = back.point((p[0] - cx, p[1] - cy, 0.0))
    return _foam_asm.spin_xy((q[0], q[1]))


# What the loop calls the three lines the copper slot carries. The slot names them by the plug
# whose low end each is; the machine names them by what they are.
SLOT_LINES = {"evap-inlet": "lower", "evap-outlet": "middle", "prv-vent": "top"}


def _foam_station(station):
    """The cold core's own `(position, outward axis)` for a named penetration, in the shell's
    frame — the front field's bores, the slot's three, and the cap conduits."""
    if station in _cc.front_port_order:
        return _cc.front_port_station(station)
    if station in _cc.cap_conduits:
        x, y = _foam_asm.cap_conduit_station(station)
        return ((x, y, _stack_lid_top_z()), _foam_asm.cap_conduit_axis_out())
    return _plugs.slot_station(SLOT_LINES.get(station, station))


def _stack_lid_top_z():
    """The top cap's lid crown in the shell's own frame — the plane a cap conduit opens on."""
    return _cc.foam_shell_outer_height + _cc.foam_cap_height + _cc.wall_and_floor_thickness


def foam_shell_port(station):
    """A cold-core penetration in world: ((position, outward axis), face)."""
    return _world("foam-assembly", _foam_station(station))


def foam_shell_stations():
    """Every cold-core penetration, in the order their stations climb."""
    names = list(_cc.front_port_order) + list(SLOT_LINES) + list(_cc.cap_conduits)
    return sorted(names, key=lambda n: _foam_station(n)[0][2])


def foam_shell_bore():
    """The one bore every cold-core penetration takes."""
    d = 2.0 * _cc.port_hole_radius
    if abs(d - _slot_width) > 1e-9:
        raise ValueError(
            f"the shell's bores are {d:g} mm and the copper slot is {_slot_width:g} — one "
            f"lane, one width")
    return d


# --- Zone B: the water deck -------------------------------------------------

SEAFLO_TERMINALS = {"suction": _seaflo.suction, "discharge": _seaflo.discharge}


def seaflo_terminal(name):
    """One of the pump's two head barbs in world."""
    return _world("seaflo-pump", SEAFLO_TERMINALS[name]())


def bulkhead_water_mouth():
    """The tap-water bulkhead's INBOARD mouth in world — the station the ASSE chain is fed
    from, and the one its own axis is struck off."""
    return (WATER_BACK_X, REAR_PLANE_Y - _jg.PROUD_LENGTH, port_row_z())


def _asse_axis_drop():
    """How far the chain hangs under its own flow axis AT THE ROLL IT IS BUILT WITH."""
    ax, d = _bfp.flow_axis()
    seat = (_seating.Seat.turn((0, 0, 1), ASSE1022_YAW)
            .then(_seating.Seat.turn((0, 1, 0), ASSE1022_ROLL)))
    return seat.port((ax, d))[0][2] - _boxes.boxed(seat.solid(_load(ASSE_STEP))).zmin


def _asse_axis_west():
    """How far west of its own flow axis the chain reaches, at that same roll."""
    ax, d = _bfp.flow_axis()
    seat = (_seating.Seat.turn((0, 0, 1), ASSE1022_YAW)
            .then(_seating.Seat.turn((0, 1, 0), ASSE1022_ROLL)))
    return seat.port((ax, d))[0][0] - _boxes.boxed(seat.solid(_load(ASSE_STEP))).xmin


def asse_axis():
    """The line every fitting on the tap-water sequence stands on: `(x, y, z)`.

    X and Z are the rear port row's own; Y is that row's plane less the tube the panel's mouth
    and the chain's owe each other."""
    inlet = _bfp.port("tube-in")[0][0]
    return (WATER_BACK_X, bulkhead_water_mouth()[1] - ASSE_INLET_HOP + inlet, port_row_z())


def asse_underside():
    return packed().box("asse1022-assembly").zmin


def bfp_terminal(name):
    """One of the ASSE chain's three terminals in world."""
    return _world("asse1022-assembly", _bfp.port(name))


def split_y():
    outlet = _bfp.port("tube-out")[0][0]
    return asse_axis()[1] - outlet - WALL_SEQ_STRAIGHT - _split.REACH


SPLIT_TERMINALS = {"supply": _split.supply, "to-vk": _split.to_vk,
                   "to-flavor": _split.to_flavor}


def split_terminal(name):
    return _world("water-split", SPLIT_TERMINALS[name]())


def flowreg_lane():
    return (split_terminal("to-flavor")[0][1] - WALL_SEQ_STRAIGHT
            - _flowreg.REACH - FLOWREG_RUN)


FLOWREG_TERMINALS = {"inlet": _flowreg.inlet, "outlet": _flowreg.outlet}


def flowreg_terminal(name):
    return _world("flow-regulator", FLOWREG_TERMINALS[name]())


# --- The tap-water stack, read down from the chain's own axis ---------------
# The rear port row's height is the whole west lane read from the CAP UP: the basin's floor
# stands one `LINE_HUG` over the cap, the basin is its own depth, the chain's vent needs
# `_pan.VENT_GAP` of splash-and-service air over the rim, and the chain hangs
# `_asse_axis_drop()` under its own flow axis. That axis is the port row.
PORT_ROW_RAILS = None      # filled by `drip_pan_seat()`, which is where the stack starts


def drip_pan_seat():
    """The basin's own floor plane — one clearance floor over the foam cap it stands on."""
    return foam_cap_top() + LINE_HUG


def port_row_z():
    """The rear port row's centreline, and the ASSE chain's own flow axis with it."""
    return drip_pan_seat() + _pan.PAN_Z + _pan.VENT_GAP + _asse_axis_drop()


def _pan_room(pan_x, pan_y, vent):
    """The vent's tip read back against the basin's inner floor."""
    x0, x1 = pan_x + _pan.WALL, pan_x + DRIP_PAN_X - _pan.WALL
    y0, y1 = pan_y + _pan.WALL, pan_y + DRIP_PAN_Y - _pan.WALL
    if not (x0 <= vent[0] <= x1 and y0 <= vent[1] <= y1):
        _short("drip-pan-room",
               f"the ASSE vent's tip stands at ({vent[0]:.2f}, {vent[1]:.2f}) and the basin's "
               f"inner floor runs x[{x0:.2f}, {x1:.2f}] y[{y0:.2f}, {y1:.2f}] — a drip off that "
               f"stub lands outside the basin it is meant for.")


def west_wall_x():
    return CORE_WEST_FACE - SIDE_RIB_INSET


def drip_pan_west():
    """The basin's own west wall — the rim lands its west edge on the −X wall's inner face, the
    face the tray withdraws through."""
    return west_wall_x() + _pan.FLANGE_W


def drip_pan_rails():
    """The pair of rails the basin's flange bears on, rooted in the −X wall's inner face."""
    pan = packed().box("drip-pan")
    top = pan.zmax - _pan.FLANGE_T
    x0, x1 = west_wall_x(), pan.xmax
    band = _pan.bearing_w()
    return [(x0, x1, pan.ymin, pan.ymin + band, top - DRIP_RAIL_H, top),
            (x0, x1, pan.ymax - band, pan.ymax, top - DRIP_RAIL_H, top)]


def drip_pan_stop():
    """The stop bar at the east end of that pair — what the push lands on."""
    pan = packed().box("drip-pan")
    foot = pan.zmax - _pan.FLANGE_T - DRIP_RAIL_H
    return (pan.xmax, pan.xmax + DRIP_STOP_T, pan.ymin, pan.ymax, foot, pan.zmax)


def west_wall_ports():
    """Through-holes the −X side wall needs: (kind, y, z, *size), the shapes of
    `back_wall_ports` read on that wall's own plane.

    ONE OPENING IN TWO RECTANGLES, cut at what the tray is WIDEST at each height. Above the
    flange's underside that is the rim. Below it, it is the HAUNCH — the 45° flare carries the
    section past the basin's wall on the way up to the rim.

    The two meet on the flange's underside, the plane the tray bears on, and the lower one's
    flank falls exactly where `drip_pan_rails` puts the rail's inboard face — both are the
    haunch's toe less the fit. The slip goes where the tray can move: a `PAN_SLIP` on both
    flanks of each rectangle, under the floor and over the rim. Square corners — `CORNER_R`
    rounds the tray in PLAN, and this is the section across it."""
    pan = packed().box("drip-pan")
    s = _pan.PAN_SLIP
    reach = _pan.FLANGE_W - _pan.FLANGE_HAUNCH      # rim edge inboard to the haunch's toe
    haunch_y0, haunch_y1 = pan.ymin + reach, pan.ymax - reach
    z_flange = pan.zmax - _pan.FLANGE_T
    return [
        ("rect", (haunch_y0 + haunch_y1) / 2.0, (pan.zmin - s + z_flange) / 2.0,
         haunch_y1 - haunch_y0 + 2 * s, z_flange - pan.zmin + s, 0.0),
        ("rect", (pan.ymin + pan.ymax) / 2.0, (z_flange + pan.zmax + s) / 2.0,
         pan.ymax - pan.ymin + 2 * s, pan.zmax + s - z_flange, 0.0),
    ]


# --- V-K, and the two chains made up on the pump ---------------------------

# The plate seats its valve flow arrow +Y, so the inlet is the collet at the smaller y.
VK_TERMINALS = {"inlet": "xc-yn", "outlet": "xc-yp"}


def vk_terminal(name):
    """One of V-K's two collets in world."""
    return _world("vk-tray-assembly", _tray1.port_collets()[VK_TERMINALS[name]])


DISCH_TERMINALS = {"barb-tip": _disch.barb_tip, "tube-port": _disch.tube_port}


def disch_terminal(name):
    return _world("discharge-chain", DISCH_TERMINALS[name]())


SUCT_TERMINALS = {"barb-tip": _suct.barb_tip, "tube-port": _suct.tube_port}


def suct_terminal(name):
    return _world("suction-chain", SUCT_TERMINALS[name]())


# --- The carb riser's meter -------------------------------------------------

DIGITEN_TERMINALS = {"inlet": _digiten.inlet, "outlet": _digiten.outlet,
                     "wire-exit": _digiten.wire_exit}


def digiten_terminal(name):
    return _world("digiten-flow", DIGITEN_TERMINALS[name]())


# --- The CO2 chain ----------------------------------------------------------

def _co2_axis_drop():
    """How far the CO2 chain hangs under the line its two sockets stand on, at the turn it is
    built with — whichever of the two bodies reaches lowest."""
    turn = _seating.Seat.turn((0, 0, 1), CO2_YAW)
    return max(turn.port(station)[0][2] - _boxes.boxed(turn.solid(_load(step))).zmin
               for step, station in ((GASHER_STEP, _gasher.inlet()),
                                     (WR1110_STEP, _wr1110.inlet())))


def co2_row_z():
    """The CO2 row's own height on the rear panel — one clearance floor over the pump's crown,
    which is what the chain runs forward across."""
    return packed().box("seaflo-pump").zmax + LINE_HUG + _co2_axis_drop()


def co2_axis():
    """The line the CO2 chain stands on: the rear panel's own column for it, and that row."""
    return (CO2_BACK_X, REAR_PLANE_Y - _derpipe.SHANK_LENGTH - CO2_HOP, co2_row_z())


CO2_CHAIN_TERMINALS = {"gasher-co2": _gasher.stations, "wr1110": _wr1110.stations}


def co2_chain_port(body, name):
    return _world(body, CO2_CHAIN_TERMINALS[body]()[name])


def co2_inlet_seat():
    """The DERPIPE's own seat: its NPT stub made up into the check's socket, on the rear wall's
    own column for it."""
    pos = packed().port("gasher-co2", _gasher.inlet())[0]
    turn = _seating.Seat.turn((0, 0, 1), CO2_YAW)
    tip = turn.port(_derpipe.stub_tip())[0]
    return turn.then(_seating.Seat.shift((pos[0] - tip[0], pos[1] - tip[1], pos[2] - tip[2])))


def co2_inlet_port(name):
    st = {"collet": _derpipe.collet, "npt-out": _derpipe.stub_tip}[name]()
    pos, axis = co2_inlet_seat().port(st)
    return pos, _face_of(axis)


# --- Zone B: the electronics column -----------------------------------------

PSU_TERMINALS = {"ac-in": _psu_ref.ac_in, "dc-out": _psu_ref.dc_out}


def psu_terminal(name):
    return _world("psu", PSU_TERMINALS[name]())


def ac_hub_lug(pole):
    return _world("ac-hub", _achub.lug(pole))


RELAY_TERMINALS = {"contacts": _relay_ref.contacts, "logic": _relay_ref.logic}


def relay_terminal(name):
    return _world("relay-1", RELAY_TERMINALS[name]())


def ground_stud():
    return _world("ground-stack", _gnd_ref.landing())


def pcba_pose():
    """The board's own seat in the machine, for a station given in the board's frame."""
    return packed().seat("pcba")


def pcba_port(px, py):
    """A board connector in world, given its station in the board's own frame."""
    pos, axis = pcba_pose().port(_pcba.port(px, py))
    return pos, _face_of(axis)


# --- The manifold's own ports ----------------------------------------------
# Every collet in Zone C reaches world on the seat its body took inside the study, composed
# onto `manifold_seat()`. The three families read the same way: a valve's two collets are the
# ends of its own limb, a tee's three are two run ends and a branch, and a pump's two are the
# barbs its anchor tees sit on.

# Which of a tee's three numbered ports is which collet. Y-D and Y-G are numbered from the
# BARB — `fluid-topology.md`'s tables put the pump on port 1 there — and the rest from the end
# their own run starts at.
TEE_ENDS = {
    "Y-A": {"1": "front", "2": "back", "3": "branch"},
    "Y-B": {"1": "front", "2": "back", "3": "branch"},
    "Y-C": {"1": "front", "2": "back", "3": "branch"},
    "Y-D": {"1": "branch", "2": "back", "3": "front"},
    "Y-E": {"1": "front", "2": "back", "3": "branch"},
    "Y-F": {"1": "front", "2": "back", "3": "branch"},
    "Y-G": {"1": "branch", "2": "front", "3": "back"},
    "Y-H": {"1": "front", "2": "back", "3": "branch"},
}
# Which anchor tee stands on which pump barb, so a pump port reads off the tee that meets it.
PUMP_BARBS = {"P-B-I": "Y-C", "P-B-O": "Y-D", "P-A-I": "Y-F", "P-A-O": "Y-G"}


def manifold_port(name):
    """One manifold collet in world by its topology name — `V-A-I`, `Y-C-3`, `P-B-O` — as
    `(pos, face)`.

    `manifold_layout` states each in its own frame and `manifold_seat()` carries it here, so a
    port and the metal it is drawn on cannot drift apart."""
    ml = _ml()
    if name in PUMP_BARBS:
        p, d = ml.barb_station(PUMP_BARBS[name]), (0.0, 0.0, 1.0)
    else:
        body, end = name.rsplit("-", 1)
        if body.startswith("Y-"):
            which = TEE_ENDS[body][end]
            if which == "branch":
                p, d = ml.branch_port(body)
            else:
                p, d = ml.port(body, which), ml.port_axis(body, which)
        else:
            flow = ml.P[body]["arg"]
            which = "front" if (end == "I") == (flow > 0) else "back"
            p, d = ml.port(body, which), ml.port_axis(body, which)
    pos, axis = manifold_seat().port((p, d))
    return pos, _face_of(axis)


def manifold_mouths():
    """The six connections that leave the manifold, `{connection id: (port name, what)}`."""
    ml = _ml()
    return {cid: (p, what) for cid, p, what, _b, _e in ml.MOUTHS}


# --- Panel ports -----------------------------------------------------------
# The fluid four and the mains inlet penetrate the REAR wall in one row over the water deck;
# the CO2 inlet takes its own row over the pump's crown, the height the chain it feeds runs at.
#   Each fitting declares what it needs of a panel: the hole its barrel passes, and the room its
# nut or bezel clamps with. What this file adds is the SLIP — how much air a printed hole leaves
# around a moulded body.
PORT_HOLE_SLIP = 0.86        # a printed hole to the barrel it passes, on the diameter
PORT_BULKHEAD_D = _jg.panel_hole_d(PORT_HOLE_SLIP)      # JG 1/4" bulkhead panel hole
# The C14's cutout is calipered AS A HOLE, so it takes no slip.
PORT_C14_W, PORT_C14_H, PORT_C14_R = _iec.panel_cutout()
PORT_NUT_D, _ = _jg.panel_footprint()               # JG bulkhead nut, across the panel face
PORT_C14_FLANGE_W, PORT_C14_FLANGE_H = _iec.panel_footprint()
PORT_NUT_GAP = 7.0           # clear gap between adjacent bulkhead nuts (the margin)
PORT_ROW_MARGIN = 6.0        # nut or flange edge to the wall's own corner furniture
UMBILICAL_PITCH = PORT_NUT_D + PORT_NUT_GAP
# The tap-water station is the one on this wall that carries a BODY as well as a nut: the ASSE
# chain hangs on it, in line with it, and the chain's barrel is far wider than the bulkhead nut.
WATER_BACK_X = max(-SIDE_RIB_INSET + PORT_ROW_MARGIN + PORT_NUT_D / 2.0,
                   CORE_WEST_FACE + _asse_axis_west() + LINE_HUG)
UMBILICAL_X = WATER_BACK_X + 2.0 * UMBILICAL_PITCH
# The mains inlet at the far +X end, its flange the widest thing on this wall.
C14_BACK_X = min(CORE_EAST_FACE + SIDE_RIB_INSET
                 - PORT_ROW_MARGIN - PORT_C14_FLANGE_W / 2.0,
                 CORE_EAST_FACE - LINE_HUG - PORT_C14_FLANGE_W / 2.0)
# The CO2 inlet's own column, on the mirror plane: the chain it feeds runs forward down the
# machine's centreline over the pump, where nothing else stands.
CO2_BACK_X = MIRROR_X


def c14_inboard_y():
    """How far the mains inlet reaches INTO the bay, in world Y."""
    return REAR_PLANE_Y + _boxes.boxed(_load(IEC_C14)).ymin


def port_row_split():
    """The blank band between the fluid cluster and the mains inlet: `(west_edge, east_edge)`."""
    return (UMBILICAL_X + UMBILICAL_PITCH + PORT_NUT_D / 2.0,
            C14_BACK_X - PORT_C14_FLANGE_W / 2.0)


BACK_PORT_ORDER = ("bulkhead-water", "bulkhead-flavor-b", "bulkhead-carb",
                   "bulkhead-flavor-a", "c14-inlet", "co2-inlet")


def back_port_station(name):
    """Where a rear-panel body sits on the wall: (x, z)."""
    holes = {n: h for n, h in zip(BACK_PORT_ORDER, back_wall_ports())}
    return holes[name][1], holes[name][2]


def back_wall_ports():
    """Through-holes the rear panel needs: (kind, x, z, *size) in world coords — 'round' (a
    diameter) or 'rect' (x, z size)."""
    d, p, z = PORT_BULKHEAD_D, UMBILICAL_PITCH, port_row_z()
    west, east = port_row_split()
    if east <= west:
        _short("port-row-split",
               f"the fluid cluster reaches x {west:.2f} and the mains flange starts at {east:.2f} "
               f"— they overlap by {west - east:.2f}. This wall splits by kind: four bulkheads in "
               f"the west cluster, the C14 alone at the east end, blank wall between. Narrow "
               f"`PORT_NUT_GAP` by {(west - east) / 3.0:.2f} across the three pitches, or take "
               f"{west - east:.2f} off `UMBILICAL_X`.")
    return [
        # The fluid cluster, west end: the tap-water bulkhead on the ASSE chain's own column,
        # then the faucet umbilical's three at the nut pitch. Carb-water sits BETWEEN the two
        # flavor bulkheads, so the accented (blue-ringed) hole is the middle one.
        ("round", WATER_BACK_X,    z, d),
        ("round", UMBILICAL_X - p, z, d),   # flavor B
        ("round", UMBILICAL_X,     z, d),   # carb-water
        ("round", UMBILICAL_X + p, z, d),   # flavor A
        # The mains inlet alone at the east end, a band of blank wall off the last nut.
        ("rect",  C14_BACK_X,      z, PORT_C14_W, PORT_C14_H, PORT_C14_R),
        # And the CO2 inlet on its own row over the pump's crown, on the mirror plane.
        ("round", CO2_BACK_X, co2_row_z(), CO2_HOLE_D),
    ]


def c14_screw_stations():
    """The C14's two screw stations on the rear panel, in world `(x, z)`."""
    cx, cz = back_port_station("c14-inlet")
    return tuple((cx + sx, cz + sz) for sx, sz in _iec.panel_screws())


def port_footprint(hole):
    """(width, height) the clamping hardware of one back_wall_ports() hole occupies on the
    panel FACE."""
    if hole[0] == "rect":
        return PORT_C14_FLANGE_W, PORT_C14_FLANGE_H
    return PORT_NUT_D, PORT_NUT_D


def front_wall_ports():
    """Through-holes the front panel needs. None: the display facet spans the front-top and the
    refrigeration stratum stands against the front-bottom."""
    return []


def east_wall_ports():
    """Through-holes the +X side wall needs. None: the condenser stands against it for the
    whole of the front stratum, and the power column against it above the deck."""
    return []


def east_wall_x():
    """The +X side wall's INNER face."""
    return packed().box("foam-assembly").xlen + SIDE_RIB_INSET


def _port_frame():
    """The shared port-band geometry: (x_lo, x_hi, y_wall)."""
    placed = build()
    bbs = [_boxes.boxed(s) for s, _c in placed.values()]
    return min(b.xmin for b in bbs), max(b.xmax for b in bbs), REAR_PLANE_Y


def front_wall_y():
    """The front wall's INNER face."""
    placed = build()
    return min(_boxes.boxed(s).ymin for s, _c in placed.values()) - FRONT_STANDOFF


_PANEL: dict | None = None


def panel_bodies():
    """The connector bodies seated through the enclosure walls — four JG bulkhead unions, the
    C14 receptacle and the CO2 inlet on the rear panel."""
    global _PANEL
    if _PANEL is None:
        _PANEL = _panel_bodies()
    return _PANEL


def _panel_bodies():
    import enclosure                       # imports this module: deferred to call time

    _x_lo, _x_hi, y_wall = _port_frame()
    y_out = y_wall + WALL                              # rear-panel outer face
    # The row stands clear of the back column's Z-seam lip band, so every hole is cut in one
    # piece and every nut clamps onto unbroken wall.
    lip_top = enclosure._dims().splits[1] + enclosure.lip_len
    floor = min(h[2] - port_footprint(h)[1] / 2.0 for h in back_wall_ports())
    if floor < lip_top:
        _short("port-row-lip",
               f"the rear port row's lowest clamping edge is z={floor:.2f}, inside the back "
               f"Z-seam lip band that tops out at {lip_top:.2f} — a hole cut there straddles "
               f"the joint. Raise `port_row_z()` by {lip_top - floor:.2f}, or take that much "
               f"height back off the water deck.")

    jg = _load(JG_BULKHEAD)                            # +Y outward, origin on the panel face
    bodies = {}
    for name, hole in zip(BACK_PORT_ORDER, back_wall_ports()):
        kind, hx, hz = hole[0], hole[1], hole[2]
        if name == "co2-inlet":
            continue
        if kind == "rect":
            # The C14 is fastened from inside — its flange bears on the panel's INNER face.
            bodies[name] = _load(IEC_C14).translate((hx, y_wall, hz))
        else:
            bodies[name] = jg.translate((hx, y_out, hz))
    bodies["co2-inlet"] = co2_inlet_seat().solid(_load(DERPIPE_STEP))
    return {n: (s, COLORS[n]) for n, s in bodies.items()}


# --- The funnel ------------------------------------------------------------

_FUNNEL = None
_FUNNEL_CENTRE = None


def funnel_centre():
    """The funnel collar's centre in plan: (x, y).

    Centred across the box, and pushed as far FORWARD as the display housing allows: the top
    wall resumes at the facet's back plane, keeps one `enclosure.hopper_front_ledge` of itself
    there, and the collar's front edge stands one `hopper_funnel.brim_margin` behind that."""
    global _FUNNEL_CENTRE
    if _FUNNEL_CENTRE is None:
        import enclosure                            # imports this module: deferred to call time
        box = enclosure._dims()
        ix0, ix1 = box.inner[0], box.inner[1]
        y_front = (enclosure.facet_back_y(box.outer) + enclosure.hopper_front_ledge
                   + _funnel.brim_margin)
        _FUNNEL_CENTRE = ((ix0 + ix1) / 2.0, y_front + _funnel.collar_d / 2.0)
    return _FUNNEL_CENTRE


def placed_funnel():
    """The static funnel seated in the top-wall opening."""
    global _FUNNEL
    if _FUNNEL is None:
        _FUNNEL = _placed_funnel()
    return _FUNNEL


def _placed_funnel():
    import enclosure                                # imports this module: deferred to call time

    cx, cy = funnel_centre()
    return (_load(FUNNEL_STEP)
            .rotate((0, 0, 0), (0, 0, 1), FUNNEL_ROT)
            .translate((cx, cy, enclosure._dims().outer[5])))


def funnel_drain():
    """The hopper's drain in world: the spout exit annulus centre."""
    cx, cy = funnel_centre()
    return (cx + _funnel.neck_dx, cy, _boxes.boxed(placed_funnel()).zmin)


# --- The display -----------------------------------------------------------

def display_harness():
    """The display's harness exit in world: the centre of its interior BACK face."""
    import enclosure                                # imports this module: deferred to call time

    outer = enclosure._dims().outer
    _a, n, origin, _dy, _dz = enclosure._facet_geom(outer)
    t = enclosure.display_facet_thickness
    return (enclosure.display_centre_x(outer),
            origin[1] - n[1] * t, origin[2] - n[2] * t)
