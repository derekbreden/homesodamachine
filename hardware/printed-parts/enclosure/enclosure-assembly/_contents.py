"""Thin Edition enclosure contents — the cold core, the refrigeration stratum,
and the service bay above them.

The appliance is tall and narrow. What makes it narrow is the pose of the one
part that spans the box: the foam assembly (cold-core shell + both foam-cap
stacks) is YAWED a quarter turn about Z, so the 181 mm across its short axis —
not the 283 mm across its long one — is what the ±X walls have to clear. The box
is a consequence of what is placed here (`../enclosure/enclosure.py` `_dims`),
so that pose IS the appliance's width.

Seated in the BACK-BOTTOM CORNER: bbox min on the floor slab's cavity face
(z = 0 — the bottom cap's lid is a plane and every cap screw is down in a
counterbore, so nothing goes under it) at `FRONT_DEPTH`, the depth of the zone
ahead of it.

Components only: no tubes, no wires, no mount features. enclosure_assembly.py
verifies the pack pairwise non-intersecting at every export.

Coordinate frame: +X right, +Y back, +Z up. Origin at the lower-front-left
corner of the cavity. The enclosure is four printed pieces — one Y seam, and a
Z seam per column — whose lips and cross-pin pods hug the walls.

Strata, floor to ceiling:
  * Zone A:  the cold core, floor to its cap top, spanning the interior wall to
             wall. All ten of its penetrations are on one face — the shell's own
             −X, which the yaw puts at the machine's FRONT
             (/hardware/printed-parts/cold-core/foam-shell/README.md
             §Penetrations) — six on its front port field and four sharing the
             slot above them. `foam_shell_port` is the one reading of where.
  * Zone D:  the refrigeration stratum ahead of it — the compressor upright in
             its shroud on the floor, the condenser standing on the shroud.
  * Zone B:  the SERVICE BAY, on the foam cap. The turn puts the cap's five
             deck-mount stations in the bay's FRONT THIRD, so the electronics
             SHELF lands there by construction and the rear of the cap opens for
             the WATER DECK: the SeaFlo running front to back in the east lane —
             the only axis it fits, and the one body the box's depth gives way to
             — with the ASSE chain, V-K, the split, the regulator and the drip
             pan in the fittings lane west of it. Above all of it, the rear
             PORT FIELD in one row (`back_wall_ports`).
  * Zone C:  the VALVE MANIFOLD. It does not all stand in one place, and the
             split is by CHANNEL. Its HEAD COLUMN is in the front column ahead
             of the core, under the funnel: three of the four identical
             two-valve trays, one under the next — the SOURCE pair (V-A on tap
             water, V-B on the hopper), the SELECTS pair (V-C, V-D) one stack
             pitch under it, and the BAG-A pair (V-E, V-F) one more, at Y-E. The
             source pair and the selects pair share their two seats, so the four
             ports between them stand in two columns and Y-A and Y-B are a TEE
             on each, joined by a crossbar — an upright H. The column STANDS on
             the refrigeration stratum's roof (`bag_a_tray_pos`), each seat one
             stack pitch over the one below it, coils up under the plate above,
             so every stage falls away from the head. The top tray hangs on the
             hopper spout's own column, because V-B gates a gravity drain and
             that is the one line here that cannot be routed around anything,
             and the basin roofs it. Nothing crosses in the band under the
             bottom plate (`tray_column_floor`): fluid-15 reaches Y-E's run
             from reservoir A by passing the column on the OUTSIDE, up the lane
             east of it. BOTH PUMPS stand upright in the lane west of it, side by
             side, all four barbs on the bag-A pair's own port plane and their
             feet the lowest thing the column puts over that roof.
  * Zone C aloft: the rest of the manifold, in the LOFT — the band between the
             water deck's crown and the ceiling, over the whole of Zone B. The
             BAG-B pair with Y-H ahead of it and the NOZZLE GATES (V-G, V-J)
             behind it take its west lane, parted by a JUNCTION BAY: the two
             pairs face each other collet for collet, so what stands between
             them is a fitting and not a gap — Y-G, whose run is the one straight
             line V-I-I and V-J-I already share. CHANNEL B'S PUMP is not up
             here — both stand in the front column — and the strip east of the
             loft's trays is its own PUMP LANE, where Y-F stands. The
             nozzle gates are up here because their two outlets are the only
             lines the manifold sends OUT of the machine, and what they leave
             through is the rear panel's own port row.
  * Zone C top: the funnel, on the box's top wall directly behind the display
             facet — full interior width, as far forward as the facet's own
             housing allows, reaching aft for whatever plan area its capacity
             needs. It may cross the Y seam; both halves take their share of
             the opening (`enclosure.build_back_half`).

THE PLENUM — what the front column has left, and why the manifold has two stands.

Zone C's head column stands in the condenser's INTAKE: the block draws across the
cabinet from its −X face, so the front column west of x = `CONDENSER_LANE`'s end
is both the space the manifold has there and the air path the refrigeration loop
runs on. Its extent, measured against the printed pieces rather than assumed —

    fit.py slab --z 170.6,241.6 --x=-17,198 --y=-6,180.5 --step 3 \\
        --exact enclosure_front_top,enclosure_back_top,enclosure_back_bottom

is x[-11, 123.3] y[-3, 180.5] z[170.6, 311.5], the Z-seam lip's rim to the
block's crown. The ±X margins run to the wall here: the boss chains stand in the
Y-seam corner, aft of this column, so the `SIDE_RIB_INSET` a floor part takes is
not what bounds a body at this height — the pieces are, and the scan measures
them. In height it is TWO LAYERS: 140.9 mm against a tray's 59.6 and a lying
pump's 62.6.

What stands in it, and the measurement for each:

  * The HEAD COLUMN, x[37.13, 109.63] y[101, 160] — three trays, and a seat down
    it costs the intake nothing new in plan, because it stands in the shadow the
    seat above already casts. `tray_column_floor()` is what the bottom plate has
    left over the shroud's roof.
  * BOTH PUMPS upright in the west-forward box, side by side on one lane and one
    plane: x[-10, 52.6] and x[54.4, 117], both y[14.3, 76.9] z[160.5, 287.4]. The
    whole column, four orientations, one grid —

        fit.py search kamoer-kphm400 --x=-14,180,10 --y=-3,175,10 --z 156,320,12 \\
            --pitch 0,90 --roll 0,90 --anchor bbmin --clearance 1

    returns 23 free of 20160 poses, in three places: this box, which is the only
    one of them that takes the body ON END, and two bands lying ACROSS the core's
    front face at z ~300-375, which are the loft read from the front. So the
    front column takes exactly one more BODY of that size, and this is it.
  * The PUMP ROW's two tees, in the lane behind that pump — two 13.7 mm bodies in
    the 32.4 mm between the front column's lip rim and the tray column's own west
    face, on the bag-A pair's port plane. They cost the intake only what a
    fitting's own section costs; the lines that close on them cost more.

The intake's cost, by the same bounding-box convention the scans use, with each
run measured as the band its legs sweep, is in `../README.md`.

Which body it takes is decided by the JUNCTION and not by the plan area. A tray
yawed a quarter turn is 59 mm wide and the lane between the −X wall and the head
column's own west face is 70, so the tray itself fits — and what a pair that
meets at a divider wants beyond it is `divider_reach()` plus a body length past its
far collet, with a turn's worth of room beyond each end for the tube to leave on:
7 + 59 + 56.1 + 7 = 129.1 mm against the 139 the column has west of the block's
intake face. That arithmetic is a function of `DIVIDER_LEAN`: this is the one place
in the pack where the lean decides which BODY may stand where rather than only how
far a fitting hangs, and a lean shallow enough carries it past 139 and leaves the
lane to the pump alone. The pump is the one body that wants only its own 73,
because its two barbs already face down the lane its lines run in and neither needs
a fitting turned onto it.

Both pumps have the lane, side by side, and the bag-B pair and the nozzle gates go
aloft. Width does not exclude the alternative — standing a divider-joined pair in
that lane instead would put the bag-B pair back beside its own reservoir port at
the cost of a pump going aloft — so this is a choice and not a finding, and
`../README.md`'s levers carry it with its numbers.

"""

import hashlib
import json
import os
import shutil
import math
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
           _hw / "printed-parts" / "cold-core",
           _hw / "printed-parts" / "cold-core" / "foam-assembly",
           _hw / "cut-parts" / "compressor-shroud",
           _hw / "reference" / "condenser-block",
           _hw / "reference" / "jg-bulkhead-union", _hw / "reference" / "iec-c14-inlet",
           _hw / "reference" / "derpipe-co2-inlet",
           _hw / "reference" / "gasher-check-valve", _hw / "reference" / "wr1110-regulator",
           _hw / "reference" / "tee-connector", _hw / "reference" / "y-divider",
           _hw / "printed-parts" / "zone-c" / "hopper-funnel",
           _hw / "reference" / "asse1022-assembly",
           _hw / "reference" / "water-split", _hw / "reference" / "neofit-flow-control",
           _hw / "reference" / "seaflo-discharge-chain", _hw / "reference" / "seaflo-22-pump",
           _hw / "reference" / "digiten-flow-sensor",
           _hw / "reference" / "beduan-solenoid", _hw / "reference" / "meanwell-irm90",
           _hw / "reference" / "wago-221-413", _hw / "reference" / "teyleten-relay",
           _hw / "reference" / "ground-ring-stack", _hw / "reference" / "kamoer-kphm400",
           _hw / "printed-parts" / "enclosure" / "drip-pan",
           _hw / "printed-parts" / "electronics",
           _hw / "printed-parts" / "electronics" / "ac-hub",
           _hw / "printed-parts" / "electronics" / "pcba-tray",
           _hw / "printed-parts" / "valve-manifold" / "single-tray",
           _hw / "printed-parts" / "valve-manifold" / "single-valve-tray",
           _hw / "printed-parts" / "valve-manifold" / "two-valve-tray",
           _hw / "printed-parts" / "valve-manifold" / "three-valve-tray",
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
import seaflo_22_pump as _seaflo         # noqa: E402  — its two head barbs
import digiten_flow_sensor as _digiten   # noqa: E402  — its two 1/4" PTC collets, coaxial on ±X
import beduan_solenoid as _vk            # noqa: E402  — V-K's two 1/4" QC collets
import drip_pan as _pan                  # noqa: E402  — its lift, its section, its rail offset
import ac_hub as _achub                  # noqa: E402  — its lug stations and its plate's layout
import ac_hub_assembly as _achub_asm     # noqa: E402  — the hub with its three lugs in
import pcba_tray as _pcba                # noqa: E402  — the board's outline, holes and thickness
import two_valve_tray as _tray           # noqa: E402  — the tray's seat pitch and its four bare collets
import two_valve_assembly as _tray_asm   # noqa: E402  — the plate with both valves on it
import single_valve_tray as _tray1       # noqa: E402  — the one-seat plate's reach and its two collets
import tee_connector as _tee_ref         # noqa: E402  — the junction fitting's own three ports
import y_divider as _ydiv                # noqa: E402  — the trident's stem and its two outlets
import meanwell_irm90 as _psu_ref        # noqa: E402  — the PSU's section and its two terminal ledges
import teyleten_relay as _relay_ref      # noqa: E402  — the relay's ends and its PCB
import ground_ring_stack as _gnd_ref     # noqa: E402  — the lug fan's own stack pitch
import kamoer_kphm400 as _kamoer         # noqa: E402  — the pump's two barb stations on its head
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
ASSE_STEP        = _hw / "reference" / "asse1022-assembly" / "asse1022-assembly.step"
WATER_SPLIT_STEP = _hw / "reference" / "water-split" / "water-split.step"
FLOWREG_STEP     = _hw / "reference" / "neofit-flow-control" / "neofit-flow-control.step"
BEDUAN_STEP      = _hw / "reference" / "beduan-solenoid" / "beduan-solenoid.step"
DRIP_PAN_STEP    = _hw / "printed-parts" / "enclosure" / "drip-pan" / "drip-pan.step"
DRIP_RAILS_STEP  = _hw / "printed-parts" / "enclosure" / "drip-pan" / "drip-pan-rails.step"
MEANWELL_STEP    = _hw / "reference" / "meanwell-irm90" / "meanwell-irm90.step"
PCBA_BOARD       = _hw / "printed-parts" / "electronics" / "pcba-tray" / "pcba-board.step"
AC_HUB_ASSEMBLY  = (_hw / "printed-parts" / "electronics" / "ac-hub"
                    / "ac-hub-assembly.step")
RELAY_STEP       = _hw / "reference" / "teyleten-relay" / "teyleten-relay.step"
GND_STACK        = _hw / "reference" / "ground-ring-stack" / "ground-ring-stack.step"
JG_BULKHEAD      = _hw / "reference" / "jg-bulkhead-union" / "jg-bulkhead-union.step"
IEC_C14          = _hw / "reference" / "iec-c14-inlet" / "iec-c14-inlet.step"
TRAY_ASSEMBLY    = (_hw / "printed-parts" / "valve-manifold" / "two-valve-tray"
                    / "two-valve-assembly.step")
TRAY1_ASSEMBLY   = (_hw / "printed-parts" / "valve-manifold" / "single-valve-tray"
                    / "single-valve-assembly.step")
Y_DIVIDER        = _hw / "reference" / "y-divider" / "y-divider.step"
TEE_CONNECTOR    = _hw / "reference" / "tee-connector" / "tee-connector.step"
KAMOER_STEP      = _hw / "reference" / "kamoer-kphm400" / "kamoer-kphm400.step"
# The CO2 inlet chain — the DERPIPE panel fitting, the GASHER check threaded onto its stub,
# and the WR1110 secondary regulator one tube hop behind it. All three are authored +Y = flow.
DERPIPE_STEP     = _hw / "reference" / "derpipe-co2-inlet" / "derpipe-co2-inlet.step"
GASHER_STEP      = _hw / "reference" / "gasher-check-valve" / "gasher-check-valve.step"
WR1110_STEP      = _hw / "reference" / "wr1110-regulator" / "wr1110-regulator.step"
# The DIGITEN FL-S402B Hall-effect turbine meter, inline on the carb-water riser. Its own
# frame is +X = flow, the two 1/4" PTC collets coaxial on ±X, the pigtail boss leaving +Z.
DIGITEN_STEP     = _hw / "reference" / "digiten-flow-sensor" / "digiten-flow-sensor.step"


# --- Placement anchors ----------------------------------------------------
# The quarter turn. +90° about Z carries the shell's local +X axis onto world +Y,
# so its long axis runs front-to-back and its SHORT axis (outer_shell_y_length,
# 181) runs across the machine — which is the whole edition. The face the shell
# cuts every penetration in is its local −X, and the same turn puts that face on
# world −Y: facing the user. `foam_shell_port` is what carries a station through
# this, so nothing downstream repeats the turn by hand.
FOAM_YAW = 90.0

# --- Zone D: the refrigeration stratum -------------------------------------
# The compressor stands UPRIGHT in its shroud on the floor, its own feet under it, and
# the condenser block stands on the shroud. Upright is the compressor's constraint, not
# the shroud's: the can's oil sits in its bottom and the pickup is gravity-fed, so the
# open face of the shroud is the face that must point down. That fixes the turn to a
# yaw, and a yaw leaves the copper-bearing face (native −X) horizontal — SHROUD_YAW
# points it at +Y, across the machine corridor at the core it feeds, and carries the AC
# gland (native +Y) to +X. The condenser stands its 151 up and lays its 56 mm AIRFLOW
# AXIS ACROSS the machine at the +X end of the band, so the air crosses the cabinet: in
# at the −X side face, out at the +X one it stands against — the hot end leaves by the
# nearest wall and what crosses the cabinet is the cool intake. That leaves
# `CONDENSER_LANE` open at the −X end of the band. The cold core's ten ports all stand
# at x 168, which both bodies span, so what keeps them clear is height and not the lane:
# the whole column crosses the wall below the shroud's roof and opens into
# `MACHINE_CORRIDOR`. See ../README.md.
# The block's own three dimensions, off the module that draws it — the machine reads them,
# it does not hold them.
CONDENSER_AIRFLOW = _cond.AIRFLOW            # fan + finstack stack depth, along the flow
CONDENSER_FACE_A, CONDENSER_FACE_B = _cond.FACE_A, _cond.FACE_B
SHROUD_YAW = -90.0
SHROUD_DEPTH = 133.0                         # the turned shroud's Y footprint
CONDENSER_LANE = 181.0 - CONDENSER_AIRFLOW
# Air between the front block's aft face and the cold core's front face — the
# condenser is the loop's hot end and the core is its cold one, and they stand at the
# same Y.
CORE_FACE_CLEAR = 2.5
# Depth of the zone AHEAD of the cold core, and the MACHINE CORRIDOR left behind the
# shroud inside it — the band the refrigerant loop turns in on its way to the core's
# front face, and the one the manifold's cross-machine lines run along. Every station
# forward of the core reads its Y off this.
FRONT_DEPTH = CONDENSER_FACE_A + CORE_FACE_CLEAR
MACHINE_CORRIDOR = FRONT_DEPTH - SHROUD_DEPTH

# The ±X walls stand one boss chain off the cold core, not against it. The core
# spans the interior wall to wall and floor to its cap, so a wall on its face
# leaves the seam machinery — corner posts, boss chains, Z-seam pods — nowhere to
# stand. enclosure.py reads this as the side-wall standoff. Front floor content
# set against a side wall is inset the same, to clear the ribs.
SIDE_RIB_INSET = 14.0
# The cold core's own WEST FACE, and the datum the whole pack is struck off in X: the core is
# seated on it (`_build`), the −X wall stands one `SIDE_RIB_INSET` outboard of it, and the
# ±X boss-chain band reaches one `enclosure.boss_in` back inboard from that wall. Those two
# are the same number, so the band ends exactly HERE — and "clear of the seam furniture" and
# "standing over the core" are one test. A body on the loft that reaches west of this face is
# a body the Y-seam's posts, pods and plugs have to be routed around.
CORE_WEST_FACE = 0.0
# The same face at the other flank, and the same test: the +X wall stands one `SIDE_RIB_INSET`
# outboard of the core and the boss-chain band reaches one `enclosure.boss_in` back inboard, so
# the band ends HERE. A body reaching east of this is a body the seam's furniture has to be
# routed around — which is why the widest thing on either wall is read against it and not
# against the interior's own rim.
CORE_EAST_FACE = _cc.outer_shell_y_length
# What that band carries at the BACK WALL: the back piece's ±X corner column — the Y-seam's
# cross-pin pod and the web under it — standing the full height of the piece, this deep off
# the wall's inner face. It is the aft end of the rib band, and `rear_column_face` is the
# plane a body overhanging the core sideways runs aft to.
REAR_CORNER_COLUMN = 16.3               # = 2 × enclosure.socket_r
# Floor parts are raised one wall, clearing the front pieces' bottom seam lip
# so the split can pull forward past them. The box floors to a fixed Z=0
# datum, so raising them leaves the floor in place.
SEAM_CLEAR_LIFT = 3.0
# Enclosure wall thickness (mirrors ../enclosure/enclosure.py `wall`) — used to
# seat content against the seam lips' inner faces, one wall in from the walls.
WALL = 3.0
# The back wall stands one wall behind the rearmost content — the cold core —
# instead of hard against it, so the core seats flush against the rear Z-seam
# lip's inner face rather than against the wall itself. enclosure.py reads it
# from here as `rear_seam_clear`, so the wall the panel bodies seat against and
# the wall the box is built to are one number and cannot drift apart.
REAR_STANDOFF = 3.0
# How far forward of the rear standoff the back piece's corner furniture reaches INTO the ±X
# boss band. The band is empty along the machine's whole flank except here, where the seam's
# post and pod stand: `x[181, 195] y[455.70, 469.00]`, read off the built piece. A body seated
# on the wall may take the band anywhere forward of this and nowhere aft of it.
#   Stated rather than derived, and it is the one figure on this flank that is. The wall's
# furniture is a function of the box's size, the box is sized to the pack, and the pack is what
# this seats — so a body cannot ask the wall where its posts are while the wall is still asking
# the body how big to be. `pack-closes` is the check: seated aft of this the brick reports
# `enclosure_back_top ∩ psu` and says by how much.
REAR_CORNER_POST = 13.3
# The plane a body MOUNTED ON THE +X WALL stands its outer face on: the wall's own inner face,
# less what a boss off that wall reaches inboard. `SIDE_RIB_INSET` is the band the enclosure
# strikes its width by (`enclosure._dims`, `ix1 = cold.xmax + SIDE_RIB_INSET`), so the inner
# face is the core's east flank plus that band, and the standoff is the rear seam lip's — the
# same figure the back wall's bodies stand on, because it is the same kind of joint.
EAST_WALL_SEAT = CORE_EAST_FACE + SIDE_RIB_INSET - REAR_STANDOFF

# The interior REAR PLANE — the inner face of the back wall, STATED, the way
# `enclosure.appliance_height` states the ceiling. Depth is a bound, not a consequence: a
# component dragged forward inside the machine does not make the machine shallower, and the
# pack that outgrows this plane fails the build instead of quietly resizing the appliance.
#   The aft stand's own Y comes out of this plane (`rear_column_face`), and the stand stands
# 14.3 mm ahead of the SeaFlo's back face while the SeaFlo's suction barb stands 56.9 mm ahead
# of it. A plane read off the rearmost body is a plane that body carries, and the stand with
# it, holding those two 42.6 mm apart against V-K's 32.25 mm body whatever the pump is given.
REAR_PLANE_Y = 472.0
# The FRONT wall stands the same one wall off the pack, for the front column's
# Z-seam lip: a lip missing a side is a butt joint over that run, on the box's
# most visible face. Held off, the segment runs the full width.
FRONT_STANDOFF = 3.0
# The gap between the shroud's roof and the condenser standing on it, and it is the
# MINIMUM: nothing leaves that roof — the shroud's four penetrations are all on its
# sides — so what holds the block off is the front column's Z seam, which has nowhere
# else to go. The band above the stack stands the piece under the seam over the H2C bed;
# below the shroud there is no band at all. So the seam runs BETWEEN them, and the band
# it needs is one `enclosure.z_joint_clear` either side of it. Exactly two, and the band
# is a single height — there is no slack here, and either body growing costs the front
# column the seam that leaves both of them whole in one piece.
STACK_GAP = 6.0                              # = 2 × enclosure.z_joint_clear

# --- Zone B: the service bay above the cold core ---------------------------
# The band from the foam cap's lid to the ceiling, in strata:
#
#   THE SHELF is not posed here at all. The cap owns its five deck-mount stations, the yaw
# carries them, and each module lands on its own rectangle of columns — `deck_mount()` is
# the whole placement. Every station sits in the deck's FRONT THIRD. Nothing here picks a
# coordinate for a module.
#
#   THE WATER DECK takes the rear band, in two lanes. The SeaFlo divides it: its motor axis
# is longer than the cap is wide, and longer than the clear cap the shelf leaves behind it,
# so it runs FRONT TO BACK and reaches past the core's own rear face. `_port_frame` stands
# the back wall off the pack, so the appliance's DEPTH follows the pump. It takes the EAST
# lane, where the shelf's aftmost column is the board's and where its discharge stands over
# the column the cold core's front-face ports climb; the fittings take the west one.
#
#   THE PORT FIELD is one row over the deck. See `back_wall_ports`.
#
#   The back column runs solid from the floor slab to the bay's crown, so its Z seam runs
# THROUGH it, on the lip clearance the standoffs hold open at every height. The cold core
# spans that seam. ../README.md carries the measurement.

# The SeaFlo lies motor-axis along Y with its base flat on the foam cap, head and feet
# FORWARD and the motor can cantilevering aft over the clear cap behind it. The head's two
# barbs are molded into the casting and leave its ±Y side faces, so this yaw lands them on
# the machine's ±X: the suction EAST at the aft stand that feeds it, and the discharge WEST
# at the tap-water column. Its base foot is a fraction of the body's footprint — the motor
# overhangs it — and the foot is what the cap carries; mounts TBD.
#   The yaw's SIGN is the stand's. The pump and the valve stand share this storey and one of
# them has each flank, so the barb has to look at the lane the other one is in.
SEAFLO_YAW = 90.0
# The pump's plan centre across the machine — struck so its WEST flank lands on
# `CORE_WEST_FACE`, the plane the ±X rib band ends on at that flank. The pump takes the west
# lane of this storey and the manifold's aft stand takes the east, which is what keeps the
# mains block, the board and the supply on ONE side of the machine and every wet body on the
# other: a fluid line crossing to the electronics has to be authored to do it rather than
# arriving there because the two lanes were interleaved.
#   Both flanks of the casting sit inboard of the core's own plan, so nothing here reaches
# west of `-SIDE_RIB_INSET`, `enclosure._dims` strikes the interior off the inset at both
# flanks, `funnel_centre` is that interior's midpoint, and the midpoint IS the core's
# centreline — the column the gravity drain stands on (`_tray_column_plan`, `_funnel_column`).
#   The DISCHARGE CHAIN is the one thing on this flank the lane does not answer for: its hex
# is wider than the barb it screws onto, so it hangs `_disch.MAAC_HEX` west of a discharge
# that stands `_seaflo.PORT_SPAN / 2` off this centre, and 8.00 mm of it is in the rib band.
# The lane cannot simply take that up — the 10.50 mm between this casting and the stand is
# also the nozzle gate's outlet lead, which wants 7.35 of it, so the two together want 24.35
# of a band that holds 18.50.
SEAFLO_LANE_X = CORE_WEST_FACE + _seaflo.FOOT_SPAN / 2.0
# The pump's front face is `seaflo_front_y()` — not a number. The barb faces west across the
# aft stand at V-K, the fill valve that feeds it, so the pump is carried BY THAT STAND: pack the
# stand forward and the pump walks with it, and water-4 stays the length it was instead of
# growing the distance between them. A stated front face does not travel, and what it costs is
# that run's whole Y.
# The FITTINGS LOFT, west of the pump and OVER the deck: everything the tap-water path needs
# between the rear bulkhead and the pump's suction. The lane is narrower than the ASSE chain
# is long, so that chain runs FRONT TO BACK, hard against the −X wall's inset, and the pan
# lies under it — the vent weeps off its own stub onto the basin's ground.
#   Everything the chain carries sideways it carries INBOARD. Its axis stands one port row off
# the −X wall by construction (`WATER_BACK_X`), so the wall is the one direction it has no room
# in: a stub turned that way reaches further past the axis than the wall stands from it, and the
# basin hung off that stub's column reaches further still — the machine's whole west face would
# be struck off a drip tray. Turned east the same three bodies stand over the cold core, and the
# west wall is the rib inset it is supposed to be.
ASSE1022_YAW = -90.0         # flow +X onto −Y: inlet AFT at the bulkhead, outlet forward at the split
ASSE1022_ROLL = -90.0        # vent HORIZONTAL and turned INBOARD, off the chain's own axis into
                             # the bay. It weeps sideways and the pan lies under the whole chain,
                             # so a drip lands in the basin wherever it leaves, and the basin that
                             # hangs off the vent's column hangs over the shell.
# The chain hangs on the STATION IT IS FED FROM, in all three coordinates. Its inlet mouth and
# `bulkhead-water`'s stand on one line — same column across the machine, same height up the
# wall, facing each other — and `water-1` is the tube between them. X and Z are the port row's
# own (`WATER_BACK_X`, `port_row_z()`); Y is that row's plane less the tube the two mouths owe
# each other, and `asse_axis()` is the reading.
#   The panel is the one END of this sequence that cannot move — the wall is `REAR_PLANE_Y`, a
# stated datum — so it is the end the sequence is measured from, and everything downstream is a
# consequence: the split off the chain (`split_y`), the regulator off the split
# (`flowreg_lane`). What is left at the FORWARD end, between the regulator's outlet and V-A's
# inlet, is `fluid-2`'s whole budget, and it buys that run's two corners
# (`_lines.lean_leads`) — so a millimetre this sequence does not spend standing off the panel
# is a millimetre of bend radius down there.
#   The tap-water stack hangs from this line and reads down it: the chain, the air the vent
# needs, the basin (`drip_pan_seat`), its rails, and then the cap the manifold's aft stand
# stands on.
ASSE_INLET_HOP = 10.0        # the least tube between the panel's mouth and the chain's
# What holds all three is OPEN. They are 1/4" push-fit fittings with no mounting ear between
# them, tube-hung on one line down the west wall, and nothing on them is designed to bolt to
# anything. Holder TBD — and it does not come out of the top wall: a collar grown down from
# there stands beside the hopper's collar for its whole height, and the basin is a whole
# rectangle (`assembly/enclosure-mechanical.md`).
# The drip pan is not posed. In X the basin CENTRES ON THE CHAIN'S PLAN BOX, so what stands
# over the floor is the whole length a drip can leave from; in Y the vent falls on the basin's
# own centre — the axis the basin has depth to spare on, and the one it withdraws along. The
# basin is SECTIONED to the vent and STATIONED to the chain: `ASSE1022_ROLL` lays that stub
# horizontal so it sheds off its own outside rather than straight down, and `_pan_room` is the
# reading that the tip still stands over the inner floor. `drip_pan_seat()` hangs it off the
# placed chain's underside.
DRIP_PAN_X, DRIP_PAN_Y = _pan.PAN_X, _pan.PAN_Y
# V-K — the fill/shutoff solenoid, between the split and the SeaFlo suction — is not posed
# here. It is the same Beduan the manifold's trays carry, and it rides a ONE-SEAT plate of its
# own (`vk-tray-assembly`, `VK_TRAY_COLLETS`) on the aft stand's middle row; `vk_terminal` reads
# its two collets off that plate. It takes the stand's MIDDLE row, and the SeaFlo's front face
# is read off it (`seaflo_front_y`) — so the pump stands on the middle row's own plane, with a
# row of the stand ahead of the casting and a row behind it.

# The split hangs in the fittings loft under the chain it is fed from, on the chain's OWN
# PLANE, with its run down the lane and its BRANCH HANGING DOWN. Two turns say that: the roll
# puts the supply collet at the aft end of the run, facing the outlet that feeds it, and
# the pitch swings the branch off the deck onto −Z. The run stays on the plane the supply
# arrives on; the branch falls to V-K on the aft stand and to the regulator under the chain.
SPLIT_ROLL = 0.0                         # supply to the aft end of the run
SPLIT_PITCH = 180.0                      # branch off −X, onto +X
# X is not a number here: the split stands ON the column of the outlet that feeds it — the
# chain, the split and the regulator are one sequence down the west wall, each fitting's
# mouth looking at the next one's, so the whole tap-water/flavor spine reads (and later
# mounts) as one family on one line. Water-2 is the short inline hop between the first two;
# nothing falls down this column any more, so nothing contests it.
# Y is not a number here either: the run's aft end looks down the lane at the chain's own
# outlet across one `JUNCTION_LEG_LEAD` of straight, which is what a collet owes a line pressed
# into it (`scorecard.port_leads`), and `split_y()` is that reading.
# Z is the chain's own axis, carried through the whole sequence — the funnel's aft-west
# corner is closed around it (`hopper_funnel.notch_x`), so the basin's floor is no longer
# the ceiling here and the three fittings share one line in all three coordinates.
# The flow regulator is the wall sequence's third fitting: INLINE on the split's flavor tap,
# quarter-turned so both collets lie on Y, standing on the split's own column and plane with
# its inlet looking at the flavor collet across one `JUNCTION_LEG_LEAD` of straight — so
# fluid-1 is that straight, and the throttle's outlet fires forward down the open strip at
# V-A, one lean away. Its needle stem stands up where a screwdriver reaches it over the
# shelf. Its own frame is +X = flow; the quarter turn about Z lays flow on −Y, and the half
# turn about Y hangs the STEM DOWN — the fitting stands deeper under the hopper's cone than
# the split does, and the sheet there is lower than a standing stem's crown. Hung, the
# knurled head sits in the open strip over the shelf, facing the bay's own opening. X, Y and
# Z all read off the split's collet (`flowreg_lane` for the depth), so the fitting follows
# the sequence wherever it goes.
FLOWREG_TURNS = (((0.0, 0.0, 1.0), -90.0), ((0.0, 1.0, 0.0), 90.0))
# The regulator steps DOWN off the split's plane, out from under the basin: it is the one
# fitting of the three standing wholly inside the hopper's footprint, and the basin is a whole
# collar with no corner taken out of it for this sequence.
#   The step is small because it is bought from FLUID-2. `FLOWREG_RUN` is Y the sequence spends
# standing further forward, and what is left between the regulator's outlet and V-A's inlet is
# that run's price — at 16.5 mm of run the strip comes to 25.09 and is 12.25 short of the two
# arcs its lean has to seat. So what bounds this pair is fluid-2's budget, and it is about 3 mm
# of drop rather than the 34 that putting the fitting wholly under the basin would want.
FLOWREG_DROP = 3.0
# The Y that step needs to lean no harder than `_lines.FLAVOR_SKEW` (22°), a degree in hand,
# less the lead the two collets already stand apart on. Off the angle rather than picked, so a
# bigger drop widens its own run instead of steepening the leg into a corner it cannot seat.
FLOWREG_RUN = FLOWREG_DROP / math.tan(math.radians(21.0)) - 4.0
# The discharge chain. The pump's barbs are molded into its head — no thread, and the 90°
# barbed accessory does not fit it — so a stub of 3/8" braided PVC is the only thing that can
# leave the discharge, and it clamps onto this chain's barb, where the 3/8" ends. It LIES
# DOWN along Y on the pump's own crown, over the discharge that feeds it: barb aft at the
# pump, collet forward over the deck, where the fall to the core's water-in begins. Standing
# it in its native pose is not available — it is taller than the discharge stands over a cap
# it would have to drop through. Bracket TBD.
DISCH_CHAIN_TURN = ((1.0, 0.0, 0.0), -90.0)  # the native +Z barb swung onto +Y, at the pump
# The AC hub lies FLAT, which is the pose a tray of three lever nuts is drawn in: its plate on
# the horizontal, its wells opening UP, and each lug's wire half standing proud where a hand
# and a ferrule can reach it. So the turn has one duty — swing the plate's long axis off the
# part's own X onto world Y, the axis the aft-east band is deep on. Nothing rolls: the wells
# stay open to the ceiling and the stack under it stays a stack.
AC_HUB_TURN = (((0.0, 0.0, 1.0), 90.0), ((0.0, 1.0, 0.0), 270.0))
                                             # before the condenser: the run leaving it takes two
                                             # bend radii of its own bore off the mouth
                                             # (`scorecard.PORT_LEAD_BENDS` × R4.0 for 1/4"), so
                                             # the gap the chain packs into is its own depth plus
                                             # this plus one clearance floor behind it
# Every electrical body stands ON EDGE, and the machine's east flank is why: what the pump's
# can leaves on this storey is a strip, not a shelf, so a body laid flat spends its whole
# plan on a lane that has none to give and a body on edge spends its thickness. The two
# BOARDS go off the deck entirely and up the +X wall — the supply on the wall itself, the
# controller a storey over it on the same plane — which leaves the deck band for the relay
# and the hub and puts every electrical body on one flank with every wet one on the other.
#   Each turn is a yaw and then a roll about the axis the yaw laid down: the yaw is the
# module's OWN yaw plus `FOAM_YAW`, and the roll is what stands the board on the edge it
# is carried by. The controller takes a THIRD turn, a quarter roll about its own long axis,
# which lays that axis fore-and-aft down the wall instead of standing it up into the top.
PCBA_YAW = 270.0 + FOAM_YAW
RELAY_YAW = 180.0 + FOAM_YAW
PCBA_TURN = (((0.0, 0.0, 1.0), PCBA_YAW), ((0.0, 1.0, 0.0), -90.0),
             ((1.0, 0.0, 0.0), 270.0))
# The relay LIES DOWN under the hub, so its yaw is the whole of its turn: the module's long
# axis lands on world Y, the band's own deep axis, and the shallowest of its three dimensions
# stands up. What that buys is the hub's floor — a body on end here would be taller than the
# pair together and would carry nothing on its crown.
# The relay's roll is about X rather than Y because what it is short of is Y, not width: the
# ground stud shares this lane and stands aft of it, so the relay spends its 70 UP.
RELAY_TURN = (((0.0, 0.0, 1.0), RELAY_YAW), ((0.0, 1.0, 0.0), 270.0))
# The power block does not stand on the deck at all: it hangs on the +X WALL, and what makes
# that the cheap face is the brick's own proportions against the band it stands in. The Mean
# Well is 109 long, 52 wide and 33.5 deep, and the band between the pump's aft casting and
# the rear seam lip is 109 of Y at this flank — so the LONG axis lies fore and aft, the 52
# stands up, and only the 33.5 reaches inboard. A brick laid flat on the deck spends its 109
# across the machine and its whole plan area under whatever crosses above it; stood on the
# wall it spends none.
#   The turn's two steps are the two axes that changes: the yaw swings the long axis onto Y,
# and the roll about it stands the brick on the face that bolts. AC primary and DC secondary
# sit at opposite ends of the casting, so the end the yaw puts AFT is the end the C14 is on.
# The roll's SIGN is the terminals': at −90 both blocks look INBOARD, off the face a hand and
# a screwdriver reach, rather than into the wall the brick is bolted to.
PSU_TURN = (((0.0, 0.0, 1.0), 270.0 + FOAM_YAW), ((0.0, 1.0, 0.0), -90.0))

# --- Zone C: the valve manifold's HEAD COLUMN, in the front column ----------
# The manifold is five trays: four identical two-valve (`../../valve-manifold/two-valve-tray`)
# and one plate a seat wider, whose third seat carries the nozzle gates
# (`../../valve-manifold/three-valve-tray`). Three of the two-valve four stand here, one under
# the next in a single column: the SOURCE pair — V-A on tap water, V-B on the hopper — the
# SELECTS pair — V-C and V-D, the two channel gates — one stack pitch under it, and the BAG-A
# pair — V-E drawing from reservoir A, V-F returning to it — one more. Three is the column's
# whole depth: the roof it stands on is the compressor shroud's, and what a fourth seat would
# need is a pitch where `tray_column_floor()` has less. The other two — the fourth two-valve
# and the wide plate — stand aloft, over the water deck; the docstring above carries why.
#
# Every tray in the machine lies FLAT and unturned — plate down, valves up, ports along Y,
# the pose the part is cut for. Flat is not a preference: nothing holds a valve down, so the
# tray only carries one plate-up (`../../valve-manifold/two-valve-tray/README.md` §Open), and
# a yaw is the only turn any of the five has. What differs between them is which end of each
# port is the inlet, and that is the cell's own half-turn symmetry
# (`two_valve_tray.place_valve`, `*_TRAY_COLLETS` below) rather than anything about the pose.
TRAY_YAW = 0.0
# THE BAG-B PAIR stands turned a quarter, so its four collets open on ±X and its length lies
# across the west lane rather than along it.
#   Its EAST face carries V-I's fill and V-H's draw-out, looking across the strip the east
# lane's forward row opens on: Y-G stands in that strip (`y_g_pos`) and Y-F over V-H-O's own
# collet (`aft_lane_x`). Its WEST face carries V-I's return and V-H's inlet, looking down the
# flank reservoir B's port opens on at x 11: Y-H hangs off that flank (`y_h_pos`) with the
# bag on its stem.
BAG_B_TRAY_YAW = 270.0
# THE NOZZLE-A GATE stands turned a quarter, alone in the west lane's aft end rather than on
# the aft stand. It carries one valve, so its plate is the family's one-seat part.
#   Turned, its collets face ±X and its length lies ACROSS the lane. That is what both its runs
# want, and they want it in opposite directions: the inlet opens WEST down the front column's
# own lane, which is the lane that feeds it, and the outlet opens EAST toward the column its
# bulkhead stands on. Unturned, both would leave along the lane and each would owe a corner to
# get across it.
#   Standing here rather than on the stand is what makes the outlet's run one straight length:
# the plate is FORWARD of the pump's front face, so the bulkhead's whole column is open from
# this row's port plane to the panel's own stratum and nothing of the aft field stands in it.
NOZZLE_TRAY_YAW = 270.0
#
# THE SOURCE PAIR is the pair whose pose is not chosen: V-B gates a GRAVITY drain, so its
# inlet has to stand under the funnel's spout with nothing between, and the spout's column
# is the one line in this machine that cannot be re-routed around an obstacle. So the tray
# hangs its EAST seat on the drain's own X and the fall is a straight drop and one corner.
#
# It is clocked with both INLETS aft and both OUTLETS forward: the two feeds arrive from
# the back of the machine and the pair leaves toward the rest of the manifold, which
# stands ahead of and below it. Each outlet stands directly over its own select
# (`../../../topology/fluid-topology.md`), so the junction between them is a column.
# The band between the tray's aft collets and the cold core's front face. It is the whole
# approach to every aft-facing collet in the column, and its depth is set by the height that
# carries the MOST lines rather than by the pair that names it. Three run abreast at the
# pump row's two planes: the leg that turns west to its channel's suction tee, the leg that
# turns east off its channel's discharge tee, and reservoir B's climb, which crosses every
# one of these heights on its way to the loft. Three 1/4" tubes at the pack's clearance
# floor, held off the tray's own face and the core's by the same floor, is
# 2 × (1 + 3.175) + 2 × 7.35 = 23.05 mm; this is that with a millimetre to spare, and the
# spare rides the TRAY end: the lanes ladder off the core's face at one pitch (`_lines`), so
# everything the ladder leaves is the near lane's own turn radius — the whole of fluid-10's
# R. The band is priced at both faces. Aft is the core's stated plane. Forward is the
# machine's front chain, every link at its floor: the front-wall station's pod
# (`FRONT_CORNER_POD`), the pumps one `LINE_HUG` off it (`PUMP_B_FRONT_BAND`), and the
# junction's two tees one more off their aft faces (`junction_tee_pos`) — so a millimetre on
# the band is no longer through a pump but through the junction itself: the column's ports
# advance on the chain-fixed tee plane, and each millimetre comes off the four column legs'
# forward standoff, which stands level with their drop budget and buys those eight corners
# nothing back. Y-E recentres in the strip behind the pumps and follows
# ([3.4](FRONT_CHAIN_GAP) to their aft faces). The source pair's own two feeds turn in the
# same band a storey up, where only the climb shares it.
SOURCE_TRAY_AFT_BAND = 24.0
# The column stands on the refrigeration stratum's ROOF, and this is the band its LOWEST body
# leaves over it. No line crosses in it — every corridor `_lines` uses passes the column on the
# outside (`tray_column_floor`) — and what it holds instead is the FRONT Z SEAM. That band is
# `STACK_GAP`, the one the condenser already leaves over the same roof, and the seam is the
# reason for both: it is the only height in this column with nothing standing in it, so a body
# reaching down into it takes the box's front split with it (`enclosure._z_joints`).
#
# The body that reaches lowest is channel A's PUMP: it stands in this column too, and
# `_build` levels its two barbs with the bag pair's own port plane, which hangs its foot
# `pump_foot_drop` below that pair's plate. Its isolation mounts and cradle are `scorecard`'s
# own open item on it, and they go in the band the seam does not use.
FRONT_COLUMN_FLOOR = STACK_GAP
# What the column's crown leaves under the basin. The funnel ROOFS this column, so this is a
# minimum the source pair's coils stand clear of, held by `scorecard`'s `clear hopper-funnel`
# and measured against the funnel's REAL UNDERSIDE: the basin's floor slopes up toward the
# front, so the surface over these coils stands well above the spout tip that sets the funnel's
# own zmin, and the spout is aft of the tray besides.
#
# The basin is REMOVABLE SILICONE and it carries syrup, so what stands under it holds off by
# the deflection a compliant part loaded with liquid takes up rather than by the pack's rigid-
# body clearance floor.
SOURCE_TRAY_HEADROOM = 3.0

# THE SELECTS PAIR — V-C and V-D, the two channel gates — stands in the source pair's own
# COLUMN, one `tray_stack_pitch()` under it: X and Y off the tray above, Z the pack. It stands
# in the source pair's SEATS as well, which is what puts V-C under V-A and V-D under V-B and
# leaves the junction two vertical runs to take; every stage of the manifold falls away from
# the hopper that heads it.
#
# Its clocking is the source pair's turned round — both INLETS forward at the junction, both
# OUTLETS aft at the pump row still to come. The junction's two tees stand
# `JUNCTION_LEG_LEAD` off the collet plane the two pairs share; behind the aft collets lie
# `SOURCE_TRAY_AFT_BAND` and then the cold core's front face.
#
# THE BAG-A PAIR — V-E drawing from reservoir A, V-F returning to it — takes the column's
# BOTTOM seat, one more `tray_stack_pitch()` down.
#
# The bag's two ends are V-E's INLET and V-F's OUTLET, so this pair's two valves are seated
# opposite ways round, which neither pair above is. Those two ends face FORWARD at Y-E; V-E-O
# and V-F-I face aft at the pump row. Two ports side by side is a trident's shape again, but what
# is ahead of this pair is the pump row, so Y-E is a TEE standing across what they leave between
# them (`y_e_pos`) — numbered from the bag's own end all the same.
#
# The gap over a tray's coils, under the next tray's plate. A valve is located by four corner
# posts standing `two_valve_tray.top_z` deep in the plate's sockets and nothing holds it down,
# so at this gap a valve lifts straight out of its seat with the stack made up.
TRAY_STACK_GAP = _tray.top_z

# The Y-DIVIDER — Y-H, where reservoir B's fill and draw meet. It is the JG PP2308E
# (`reference/y-divider`), it joins the bag-B pair, and the bag rides its STEM — one line out to
# that reservoir's port on the cold core's face, with the fill and the draw the two outlets that
# share it. Reservoir A's junction is the same three connections in the same order and it is a
# TEE, because the room it stands in is a band and not a column (`y_e_pos`).
# A TRIDENT: stem and two parallel outlets, all three coaxial, the outlets
# 2 × `DIVIDER_OUTLET_X` apart. Native long axis is +Z with the stem up, so two turns carry
# it: the yaw lays the outlet offsets onto world X, and the roll stands the axis along Y with
# the OUTLETS AFT at the pair it joins and the STEM FORWARD, down the column the manifold
# goes in.
DIVIDER_YAW = -90.0
DIVIDER_ROLL = 90.0
DIVIDER_HALF = _ydiv.HALF          # stem / outlet collet face from the body centre
DIVIDER_OUTLET_X = _ydiv.OUTLET_Y  # each outlet's offset from the divider axis, once turned
# The divider's outlets are 14.7 apart and the valve collets they join are a seat pitch
# (34.25) apart, so each leg closes `(pitch − 2 × DIVIDER_OUTLET_X) / 2` on its way through.
# How far AHEAD the divider stands is that offset over the tangent of the lean its collets
# allow, and at that reach EACH LEG IS ONE STRAIGHT LENGTH OF TUBE: a push-to-connect collet
# grips all round and takes a run up to `FLAVOR_SKEW` off its own axis, so a straight leaving
# both mouths at that lean closes `reach · tan(FLAVOR_SKEW)` of cross between them, and where
# that equals the offset the two leans are collinear and no corner stands between them.
#
# The reach places the forward face of the pair that meets at the divider: it hangs
# `divider_reach()` off its own collets, and the slab that leaves is as wide as the tray column
# and as tall as the pair leaning through it, holding nothing but their legs.
DIVIDER_LEG_STRAIGHT = 3.0  # tube still running straight after an arc seats, at either end
# How far off a collet's own axis a soft-LLDPE run may leave or enter as ONE STRAIGHT LENGTH,
# past the rigid-copper `COLLET_SKEW`. `_lines.FLAVOR_SKEW` is bound to this name.
FLAVOR_SKEW = 22.0
# The radius 1/4" LLDPE is drawn at, and `_lines.WBEND` is this. It lives on the PACK's side
# because a divider's pose depends on it: the reach above is bounded by what each leg's two
# corners cost at this radius, and a pack that read the routing module back to place a
# fitting would be a cycle in a graph the build order is topologically sorted from.
LLDPE_BEND = 4.0
# The same stock's own published minimum (`scorecard.STOCKS`, 1/4" LLDPE), restated on the
# pack's side for the same no-cycle reason: a leg drawn at the radius the stock WANTS costs
# its corners more than one drawn at the radius a hand pigtail takes, and a pose stood off
# for the second does not seat the first.
LLDPE_STOCK_BEND = 25.4
# The pack's own part↔part floor as a LINE sees it — what a run leaves the body it passes.
LINE_HUG = 1.0                          # = scorecard.CLEARANCE_FLOOR
# Centre to centre between two 1/4" lines that share a corridor, or cross a stratum apart: a
# tube's width and that floor over it. Under this they are one line.
LINE_PITCH = 6.35 + LINE_HUG
# The same separation taken as a LEG — a step carrying a corner at EACH end. A square corner
# seats one bend radius of tangent down each of its legs, so a step shorter than two radii has
# no straight left between them. Here for `LLDPE_BEND`'s own reason: a POSE depends on it —
# the water split stands one of these off the column that feeds it. `_lines` reads both back.
LINE_STEP = max(LINE_PITCH, 2.0 * LLDPE_BEND)

# --- The TEES --------------------------------------------------------------------
# The other seven junctions are JG PP0208E union tees (`reference/tee-connector`) — an in-line
# run and a branch square to it, all three collets meeting at the body centre. Which two ports
# take the run is not a choice: a tee's run is a LANE, one straight length of tube passing
# through the fitting, and its branch is the leg that leaves that lane. So the run takes the two
# ports the same corridor serves and the branch takes the one that departs it. Six of the seven
# reach BETWEEN trays; the seventh — Y-E — joins one tray's own pair, and stands the one way a
# fitting can stand in the room that pair leaves it (`y_e_pos`).
#
# For both of channel A's, that corridor is the same: the PUMP LANE, the strip west of the
# tray column and aft of the pump where both of pump B's lines run. Each tee stands in it
# with its RUN ALONG Y — the lane's own axis — and its BRANCH UP, which is the axis every
# third leg here leaves on: Y-C's climbs a stack pitch to the selects pair, Y-D's climbs a
# storey to the nozzle gate in the loft. One construction, twice (`pump_row_tee_pos`).
TEE_RUN_HALF = _tee_ref.RUN_HALF          # run collet face from the body centre
TEE_BRANCH_REACH = _tee_ref.BRANCH_REACH  # branch collet face from the same centre
TEE_HALF_W = _tee_ref.HALF_W              # the body's own radius about the run axis
# Native run is +Z and native branch +Y, so one roll carries both: +90° about X lays the run
# along Y and stands the branch up.
TEE_ROLL = 90.0
#
# THE MANIFOLD'S OWN JUNCTION — Y-A and Y-B — is the other two, and its corridor is a COLUMN.
# The source pair stands one `tray_stack_pitch()` over the selects pair in the same seats, so
# the four ports it joins lie in two columns of two: V-A over V-C on the west seat, V-B over
# V-D on the east. Two ports in line is a run, so each column is one tee, and the two branches
# face each other across the seat pitch with one length of tube between them — an upright H.
# `../../valve-manifold/selects-source/` is that pair on its own, with the four modes measured.
JUNCTION_TEES = ("tee-y-a", "tee-y-b")
# The straight a column leg runs off its collet before it turns: a radius of tangent for the
# corner, and one more so that tangent lands off the stub's own end rather than exactly on it.
# It is the LEAST the columns stand forward of the port plane — the tees themselves stand as
# far ahead as the front chain allows (`junction_tee_pos`), and a leg leaves on axis for one
# lead, then turns down its column in one gentle move that carries the drop, the rest of the
# standoff, and whatever the columns stand off their seats by.
JUNCTION_LEG_LEAD = 2.0 * LLDPE_BEND
# The turns each tee takes. The two that stand in channel A's pump lane take the roll alone:
# run along the lane, branch up.
TEE_TURNS = {
    "tee-y-c": (((1.0, 0.0, 0.0), TEE_ROLL),),
    "tee-y-d": (((1.0, 0.0, 0.0), TEE_ROLL),),
    # Y-F takes a second roll, about the run axis the first one laid down. It stands OVER the
    # aft stand rather than in a lane beside it (`aft_row_tee_pos`), and the hopper's floor
    # closes that column [19](LOFT_TEE_HEADROOM) mm over the fitting's own crown — against a
    # branch collet standing `TEE_RUN_HALF` off the body centre. So the branch lies WEST, out
    # over the plate, in the open band between the stand's crown and the regulator's floor:
    # the one side of this fitting a line reaches along its own axis.
    "tee-y-f": (((1.0, 0.0, 0.0), TEE_ROLL), ((0.0, 1.0, 0.0), -90.0)),
    # Y-E stands ACROSS its band rather than along one, so it is the one tee here whose RUN is
    # not a corridor a line already runs down — see `y_e_pos`. The roll lays the run over onto
    # world Y and drops the branch, and the yaw swings the run round onto X; the branch is on
    # the yaw's own axis and stays pointing DOWN.
    "tee-y-e": (((1.0, 0.0, 0.0), -TEE_ROLL), ((0.0, 0.0, 1.0), 90.0)),
    # The junction's two take a YAW alone. The STEP is already stood the right way up for a
    # column, so the turn is there for the branch: local +Y goes to −sign X, which lays the
    # west tee's branch east and the east tee's west, and the two face each other down the
    # crossbar's line.
    "tee-y-a": (((0.0, 0.0, 1.0), -90.0),),
    "tee-y-b": (((0.0, 0.0, 1.0), +90.0),),
}
# The pump lane's west limit — the front column's Z-seam lip rim, off the same
# `fit.py slab --z 170.6,241.6` the docstring above quotes. A tee's body is held one
# `scorecard.CLEARANCE_FLOOR` off it, which is what moves Y-C off pump B's own inlet column:
# the barb sits nearer the wall than the fitting's body fits.
FRONT_COLUMN_WEST = -11.0
# The 1/4" LLDPE the whole manifold is plumbed in, on the PACK's side: a pose held off a LINE
# rather than off another body owes it this radius, and the poses that are read it here.
TUBE_HALF = 6.35 / 2.0
# A hugging line's centre off the face it rides: a tube radius and the floor. `_lines` seats
# a lane off its own wall by it wherever a band's end is a body — the loft bay's crossing
# lanes, the SeaFlo's flank, the nozzle shelf's outlet lanes.
PUMP_ROW_TURN = TUBE_HALF + LINE_HUG

# --- Zone C's second stand: channel A's pump, and the LOFT over the water deck -----
# The manifold does not all fit in one column, and it does not all fit in the front column.
# What is left after the head column takes its three trays is ONE body-sized void ahead of
# the core — the west-forward box, which takes a Kamoer standing on end and nothing else —
# and the LOFT: the band between the water deck's crown and the ceiling, over the whole of
# Zone B. So the manifold stands in two places and the split is by CHANNEL: channel A's
# pump joins channel A's trays in the front column, and the whole of channel B — the bag-B
# pair, its divider and its pump — takes the loft, with the nozzle gates beside them at the
# rear panel's own flavor bulkheads.
#
# CHANNEL A'S PUMP stands upright in the west-forward box. Upright is what the box takes:
# a `fit.py search` over the whole front column —
#
#     fit.py search kamoer-kphm400 --x=-14,180,10 --y=-3,175,10 --z 156,320,12 \
#         --pitch 0,90 --roll 0,90 --anchor bbmin --clearance 1
#
# — returns 23 free poses of 20160, in three places: this box, and two bands that lie ACROSS
# the core's front face at z ~300-375, which the loft takes instead.
#
# X centres the pump in the lane between the −X wall and the head column's west face, so
# neither of them is its own margin. Y packs it FORWARD into the front column's corner, on the
# band the corner's seam furniture leaves, so the whole 100 mm of lane behind it is the corridor
# its two lines run down to Y-C and Y-D in the aft band. Z stands its two barbs on the BAG-A
# PAIR'S OWN PORT PLANE: Y-C and Y-D each join this pump to a collet on that plane, so the
# junctions lie in one plane with the ports they join and no leg climbs — the same relation
# `_divider_pos` gives Y-H.
PUMP_B_LANE_X = -10.0
# The pumps' front faces, at the pack's floor off the FRONT-WEST CORNER's seam furniture: the
# front wall's inner face (the shroud's stated front less `FRONT_STANDOFF`, −3), the front-wall
# Z-station's pod standing `FRONT_CORNER_POD` off it — floor post, collar and ceiling post, so
# the pumps meet it at every height they span — and one `LINE_HUG`. The pod is the chain's
# first link and it is priced: 16.3 is the cross-pin's own jacket (a Ø10.3 socket wants a wall
# each side), and its inboard reach (x 0, screw seat 4 + M3×10 + insert cap through the west
# wall) overlaps the pump's own west face at −10, so no shorter screw clears it. The one
# re-cut that shortens the link is a pin through the FRONT wall — pod depth 11, the pumps to
# 12, an M3 head on the box's most visible face — and the junction it serves saturates first:
# the column legs' drop budget is (tray_stack_pitch − 2·TEE_RUN_HALF)/2 = 12.73, so their
# R ≈ 11.9 here rises only to ≈ 12.05 at a front band of 12, and ≈ 12.7 is the ceiling at any
# standoff. The millimetres go where the saturation says: forward to the pod's floor, none
# through the wall.
FRONT_CORNER_POD = 16.3                 # = 2 × enclosure.socket_r, as REAR_CORNER_COLUMN aft
PUMP_B_FRONT_BAND = FRONT_CORNER_POD - FRONT_STANDOFF + LINE_HUG              # 14.3
# How far a barb stands over the pump's own bounding box, off the part
# (`kamoer_kphm400`): the arch plane over the head's front face. One number for both pumps —
# they are one part twice — and it is what lets a pump's SEAT be derived from the plane its
# barbs have to land on rather than picked and then measured.
PUMP_PORT_RISE = _kamoer.arch_plane_z - _kamoer.head_front_z

# THE AFT STAND — the manifold's second stand, on the foam cap in the deck's aft-west
# quarter: THREE ROWS of the same two-valve plate, the BAG-B PAIR forward, V-K on the middle
# row, the NOZZLE GATES aft, and the tees in the bays between them. Both pumps stand in the
# front column, seated on each other.
#   Each plate's underside lands on the cap's own face, the seat the PSU and the SeaFlo take,
# and bolts to it through its own mount ears — the cap's deck-mount table carries a station
# under every ear (`TRAY_MOUNTS`), and the ears are the authority the table follows.
# The basin roofs the stand (`aft_tray_headroom`), and the nozzle pair's two outlets leave
# through the rear panel a lane behind it.
#   In X all three rows stand on ONE west face and it is the EAST one that is pinned
# (`aft_tray_x`): packed forward the plates lie alongside the SeaFlo's BASE FOOT rather than
# behind its motor can, and the foot is the westmost thing the casting has. So a plate stands
# one `LINE_HUG` off that flank and the west end lands where one plate's own width leaves it.
# The stand is `two_valve_tray` three times over, so that width is the same in every row and
# the whole lane is a single plate's.
# The stand PACKS FORWARD (`bag_b_tray_y`): its forward face stands on
# `fore_deck_column_face`, and the deck's slack lies BEHIND it — the whole aft half of the
# cap, which is the electronics shelf's and the C14's cordage's. Nothing wet stands over the
# mains gear, and the run from the panel's inlet to the PSU's AC block is a lead, not a
# crossing.
# The JUNCTION BAY — the band between the two trays. The bag pair's two aft collets look
# straight down the nozzle pair's two forward ones and Y-G feeds both, standing ACROSS the
# bay rather than along it: a trident on its own native axis, stem up at the pump and both
# outlets facing DOWN, so what the bay carries in Y is `2 × y_divider.HALF_W`, the fitting's
# own short section, and not its length. Y-G stands on the bay's midpoint (`y_g_pos`), so each
# leg has half the bay to reach it in: an `AFT_BAY_LEAD` of straight off its collet, then the
# diagonal that climbs `Y_G_CLIMB` into the outlet standing over it.
#   A corner turns at what its own two legs carry — an arc eats `R·tan(turn/2)` off each —
# so the pair's four corners are bound below by the LEAD and above by the CLIMB, and the
# bay that sets the lead is pinned at both faces, each link priced by instrument:
#   * not FORWARD: the pin is the bag pair's own forward MOUNT EAR standing on
#     `fore_deck_column_face` — the cup wants `deck_mount_cap_gap` of liquid foam between a
#     column and the cavity wall beside it, and that gap read on the cap's FRONT edge is the
#     forwardmost plane any station on this deck can take. Y-H reaches past that edge, over
#     the front column's air, and is not what pins this any more.
#   * not AFT: nothing pins it. The stand's aft face used to ride the rear corner column's
#     face; the whole band behind it is now the outlet lane's and the shelf's, and it runs
#     [188](OUTLET_LANE) mm deep — the three aft-facing outlets turn on it and climb to the
#     rear panel a lane behind the deck they leave.
#   * the LEAD is the bay's own turn construction: two legs come about on the shared
#     column and pass a `LINE_PITCH` apart, so each turn stands
#     `(AFT_TRAY_BAY − LINE_PITCH) / 2` off its own face — the bay is exactly two leads
#     and a pitch, nothing spare. fluid-20's and fluid-17's crossing lanes are the same
#     figure read across the other axis (fluid-20 leaving V-H's draw, fluid-17 falling
#     into V-G's gate), and water-3's fall stands the second pitch ahead of the lane.
TEE_RUN_LEAD = 4.0          # the exposed tube between a tee's run collet and the one it butts
AFT_TRAY_BAY = 16.0
AFT_BAY_LEAD = (AFT_TRAY_BAY - LINE_PITCH) / 2.0   # the straight a bay leg turns off its collet on
# The stand's SECOND bay — V-K's row to the nozzle gates'. No fitting stands in it, but THREE
# RUNS do, and they are what strikes it: water-4 crosses it end to end from V-K's outlet to the
# suction barb in the far lane, fluid-28 climbs in it out of V-J's outlet, and fluid-17 falls
# down it into V-G's gate, which faces onto the bay. Three lines abreast is three lanes of a
# tube and its own floor, and the bay stands one more off each plate face — under that the
# outer two are inside the plates and the middle one is inside its neighbours.
VK_TRAY_BAY = 3.0 * LINE_PITCH + 2.0 * LINE_HUG
# Outlet face over the stand's own port plane — the long side of the diagonal fluid-23 and
# fluid-27's corners turn on, and the figure the whole tap-water stack stands on: Y-G's stem
# faces UP needing its `JUNCTION_LEG_LEAD` of clear bore under the basin's rails, and
# `port_row_z` reads this climb up through the rails and the basin to the chain and the rear
# port row. 9.5 is where the outlet legs' own solve stops: the diagonal keeps the 5.0 of
# rise that leaves its bay-lead corner the whole cap, the half-millimetre over that rides
# the approach lead (`_lines`), and the corner that lead lengthens caps on the diagonal's
# remainder once the lead corner has taken its share — so more climb lifts the row for
# corners that cannot rise. The row itself has ceiling left and this figure does not spend
# it: at 9.5 the row lands at 373.7, the tallest thing riding it is the C14's flange
# topping out at 388.3, and the interior ceiling is stated at 394 — ≈ 4.7 mm at the pack's
# floor, the wall sequence's mount stint's to spend, stated here so it is not re-measured.
Y_G_CLIMB = 9.5
# CHANNEL B'S PUMP stands in the FRONT COLUMN beside channel A's, and the two are one pose read
# twice: same part, same native turn, motor down and both barbs out the +Y face at the lane
# behind them. What the pack has to find for the second one is a strip 62.61 mm wide, which is
# the MOTOR's own square and not the body's box — the part is three stacked solids and only its
# bottom 48.88 mm is that wide (`kamoer_kphm400`).
#
# X hugs its twin. The lane from pump B's east face to the condenser's intake face carries both
# motors and the gap between them, and standing this one AGAINST pump B is what leaves the rest
# of that lane on the intake side rather than splitting it between the two. What stands in the
# gap is not air: the two pumps' INNER BARBS both face aft into the same strip, so what the pose
# is held to is the pitch between those two barbs — a tube's width and the pack's floor, which
# is what the two legs leaving them need of each other. The bodies clear by construction, and
# `pump_twin_gap()` is what they end up with.
PUMP_TWIN_PITCH = 2.0 * TUBE_HALF + 1.0
# Y and Z are its twin's, face for face: both pumps stand on one lane, front-packed on the same
# band with their barbs on the same plane, and nothing else places this one. What its foot leaves
# over the refrigeration stratum's roof is `FRONT_COLUMN_FLOOR`, which is the front Z seam's own
# band — the two pumps are the only bodies this column stands in it.

# --- The CO2 inlet chain, through the EAST wall into the machine corridor ---
# The corridor behind the refrigeration stratum is the one pocket in the machine with the
# straight-line depth a rigid NPT chain wants: 47.5 mm of Y between the shroud's aft face and
# the core's front one, floor to the shroud's roof, with only tube crossings in it. The chain
# hangs there INLINE, all three bodies on one axis off the +X wall: the DERPIPE's NPT stub
# reaches inboard pointing west, the GASHER check threads straight onto it (a made-up joint,
# no line), a PP450822E + one short hop of tube leaves its stub, and the WR1110 takes that hop
# on its inlet. The customer's cylinder stands beside the machine, and its short red tether
# lands low on this side face.
#   Y holds the chain's fattest hex between the shroud's aft face and the lane co2-2 crosses
# east on; Z lays it under every line the corridor floor carries, and LOW enough that the one
# lean in co2-2 seats a stock arc at both ends. The regulator's outlet fires west, away from
# the bore at the corridor's east end, so the run's shape is fixed — out on the axis, one lean
# up-and-aft, east over its own chain, a stock close into the bore — and the lean is the only
# leg its two mid corners have: √(Δy² + Δz²) against the 2 × 25.4 two stock tangents take.
# Δy is spent (8.1 mm, this axis to the lane one stock radius off the core's face), so the
# climb carries the length: the axis stands ≥ √(50.8² − 8.1²) = 50.15 under the bore's 66.75,
# and 16 is that with margin. The hex still hangs clear over the floor slab, and the
# customer's short red tether lands lower on the side face — the direction that face already
# wants. The regulator's cradle is enclosure-mechanical's open item, and it hangs in this
# pocket.
CO2_INLET_Y = 147.0
CO2_INLET_Z = 16.0
CO2_HOLE_D = _derpipe.SHANK_D + 0.8   # clears the DERPIPE's 1/4" NPT shank
# Air between the wrench hex's inboard end and the east wall's outer face — the room a socket
# needs to get on the flats. `_panel_bodies` seats the fitting on its stub tip and holds it
# to this.
DERPIPE_WRENCH_CLEAR = 2.0
# Where the made-up joint stands: the GASHER's socket mouth on the DERPIPE's stub shoulder, an
# envelope butt for a made-up thread, so the pair reads as one body off the wall. Stated in
# build()'s own frame rather than read off the wall, because the wall is derived FROM build().
# Both bodies are seated ON this station — the check by its inlet, the fitting by its stub tip —
# so the joint is construction and nothing has to close it.
CO2_GASHER_X = 190.0
# The closest the two placed solids are held to, which is a made-up thread's whole gap. The
# scorecard's placement rule for the check reads it, so the joint answers to one tolerance and
# not two, and it is what catches the pair parting if either seat stops reading its station.
CO2_MADE_UP_TOL = 1e-6
# The hop co2-1 closes, mouth to mouth: the GASHER's stub tip to the WR1110's inlet socket. It
# holds a PP450822E on the check's male stub, a PP010822E in the regulator's female one, and the
# stretch of 1/4" tube between the two collets. The pack seats the regulator this far inboard of
# the check's own outlet station, so both fittings' reaches stay in one figure.
CO2_HOP = 10.0

# --- The carb riser's flow meter, in the loft over the water deck ------------
# The DIGITEN lies INLINE on the carb-water riser where the riser crosses the loft: yawed a
# quarter turn so its flow runs +Y (aft, the riser's own direction there) and its pigtail
# boss stands up, where the J4 loom crosses the loft to reach it. It stands in the loft's
# EAST pocket, over the SeaFlo's crown and clear east of pump A's two loft lines.
#   The loft's WEST lane is what puts it there, not a preference: pump A's suction and its
# discharge both run that lane's whole length a tube's width over the pump's crown, and the
# meter's rigid body laid in there stands in one or the other at every height it can be
# given. The east pocket is the only stretch of the riser long enough to hold it.
#   It costs the riser a second crossing — carb-1 climbs the west column, because the
# condenser fills the front column under this pocket, and comes east over the block's crown
# to arrive. That leg is the price of the pocket, and `_lines.py` states where it lies.
DIGITEN_YAW = 90.0
DIGITEN_POS = (140.0, 375.0)             # the meter's own plan origin; its collets sit ±30 off it in Y
# How far under the rear port row the meter's own origin stands. `carb-2` leaves its outlet,
# comes aft under the row's clamping bodies and climbs to the collet, and the reach it turns
# on at each end is half that climb — so the drop is what those two corners are seated on and
# it rides the row rather than being read off it a second time (`digiten_seat`).
DIGITEN_DROP = 19.0

# The funnel's rotation about its own Z. Its spout is on the collar centre, so
# the turn picks nothing; 0 keeps the collar axis-aligned with the top wall.
FUNNEL_ROT = 0.0


# --- Colors ---------------------------------------------------------------
COLORS = {
    "foam-assembly":     cq.Color(0.55, 0.75, 0.95, 0.55),
    "compressor-shroud": cq.Color(0.60, 0.62, 0.66),
    "condenser+fan":     cq.Color(0.78, 0.55, 0.35),
    # Zone B — the water deck
    "seaflo-pump":       cq.Color(0.30, 0.45, 0.70),
    "discharge-chain":   cq.Color(0.72, 0.72, 0.76),
    "digiten-flow":      cq.Color(0.92, 0.92, 0.94),
    # The CO2 chain — red, the customer-wayfinding color the inlet carries
    "gasher-co2":        cq.Color(0.85, 0.35, 0.30),
    "wr1110":            cq.Color(0.72, 0.30, 0.26),
    "asse1022-assembly": cq.Color(0.80, 0.68, 0.35),
    "water-split":       cq.Color(0.85, 0.85, 0.88),
    "vk-fill-valve":     cq.Color(0.45, 0.45, 0.50),
    "flow-regulator":    cq.Color(0.85, 0.85, 0.88),
    "drip-pan":          cq.Color(0.35, 0.55, 0.75, 0.60),
    "drip-pan-rails":    cq.Color(0.35, 0.55, 0.75),
    # Zone B — the electronics shelf
    "pcba":              cq.Color(0.15, 0.45, 0.25),
    "psu":               cq.Color(0.20, 0.20, 0.24),
    "ac-hub":            cq.Color(0.90, 0.55, 0.20),
    "relay-1":           cq.Color(0.15, 0.35, 0.65),
    "ground-stack":      cq.Color(0.25, 0.60, 0.30),
    # Zone C — the valve manifold, in the front column
    "source-tray-assembly": cq.Color(0.85, 0.78, 0.62),
    "selects-tray-assembly": cq.Color(0.85, 0.78, 0.62),
    # The junction between them, one tee on each column
    "tee-y-a":              cq.Color(0.92, 0.92, 0.92),
    "tee-y-b":              cq.Color(0.92, 0.92, 0.92),
    "bag-a-tray-assembly":  cq.Color(0.85, 0.78, 0.62),
    "tee-y-e":              cq.Color(0.92, 0.92, 0.92),
    # Zone C — channel A's pump, in the front column's west lane, and the two pump-row tees
    # that stand in the lane behind it
    "pump-b":               cq.Color(0.55, 0.35, 0.55),
    "tee-y-c":              cq.Color(0.92, 0.92, 0.92),
    "tee-y-d":              cq.Color(0.92, 0.92, 0.92),
    # Zone C — the manifold's second stand, in the service bay's loft
    "bag-b-tray-assembly":  cq.Color(0.85, 0.78, 0.62),
    "divider-y-h":          cq.Color(0.85, 0.85, 0.88),
    "nozzle-tray-assembly": cq.Color(0.85, 0.78, 0.62),
    "nozzle-b-tray-assembly": cq.Color(0.85, 0.78, 0.62),
    "vk-tray-assembly": cq.Color(0.85, 0.78, 0.62),
    "pump-a":               cq.Color(0.55, 0.35, 0.55),
    "tee-y-f":              cq.Color(0.92, 0.92, 0.92),
    "divider-y-g":          cq.Color(0.92, 0.92, 0.92),
    # Panel bodies, seated through the rear wall
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
# read this one pack — a move the assembly applied on its own would move metal the routes and
# the gates never heard about. An absent or empty file places the machine as authored.
MOVES_PATH = _here.parent / "enclosure-assembly.overrides.json"


def _moves() -> dict:
    try:
        data = json.loads(MOVES_PATH.read_text())
    except (FileNotFoundError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def build():
    """The pack as placed solids: {name: (solid, color)}.

    Memoized for the life of the process. The port frame, the enclosure's own
    sizing, `_lines._frames()` and the scorecard each ask for the pack, and every
    one of them would otherwise re-import the same STEPs; a rebuild is always a
    fresh process."""
    global _PLACED
    if _PLACED is None:
        _PLACED = _build()
    return _PLACED


def packed() -> _placing.Pack:
    """The pack itself — the placed bodies and the seat each took. A part's own station
    reaches world through `packed().port(name, station)`.

    `_build` fills it as it goes, so a pose derived mid-build reads the bodies placed
    ahead of it and `Pack` names any that are not."""
    if _PACK is None:
        build()
    return _PACK


def _world(body: str, station) -> tuple:
    """A placed body's own station in world, under this pack's port convention: `(pos, face)`.

    `station` is the `(position, outward axis)` pair the body's own module declares, in the
    body's own frame; the seat the body took carries it. Every terminal on every placed body
    in this file is this one line."""
    pos, axis = packed().port(body, station)
    return pos, _face_of(axis)


def _box(dx, dy, dz):
    return cq.Workplane("XY").box(dx, dy, dz, centered=(False, False, False)).val()


# Every body this file reads BOTH ways: its ports off a module, its metal off that module's
# committed STEP. Each entry is what draws the part, and `_metal_holds` asks it at every build
# whether the STEP beside it is still the same solid.
PORTED_BODIES = {
    "asse1022-assembly":     (_bfp.build,           ASSE_STEP),
    "water-split":           (_split.build,         WATER_SPLIT_STEP),
    "vk-fill-valve":         (_vk.build_beduan_solenoid, BEDUAN_STEP),
    "flow-regulator":        (_flowreg.build,       FLOWREG_STEP),
    "seaflo-pump":           (_seaflo.build,        SEAFLO_STEP),
    "discharge-chain":       (_disch.build,         DISCH_CHAIN_STEP),
    "digiten-flow":          (_digiten.build_assembly, DIGITEN_STEP),
    "psu":                   (_psu_ref.build,       MEANWELL_STEP),
    "relay-1":               (_relay_ref.build,     RELAY_STEP),
    "ground-stack":          (_gnd_ref.build,       GND_STACK),
    "pump-a":                (_kamoer.build_assembly, KAMOER_STEP),
    "gasher-co2":            (_gasher.build,        GASHER_STEP),
    "wr1110":                (_wr1110.build,        WR1110_STEP),
    "pcba":                  (_pcba._build_board,   PCBA_BOARD),
    "ac-hub":                (lambda: _achub_asm.build_assembly(_achub.LAYOUT), AC_HUB_ASSEMBLY),
    "source-tray-assembly":  (lambda: _tray_asm.build(), TRAY_ASSEMBLY),
}
# The two readings agree to this — one round-trip of the module's own numbers through a file
# format. Volume is a cubic measure, so it is held to the same figure scaled by the largest
# envelope any of these bodies has.
PORTED_METAL_TOL = 1e-6
PORTED_VOLUME_TOL = 1.0


def _solid_of(shape):
    """One shape off whatever a module's builder hands back — an assembly, a workplane, or a
    shape. The three are all in use across the reference modules."""
    if isinstance(shape, cq.Assembly):
        return shape.toCompound()
    if isinstance(shape, cq.Workplane):
        return shape.val()
    return shape


def _measure(shape) -> dict:
    """What a solid is, to the depth this file can compare: the six faces of its box, and the
    material inside them. The box moves when a part changes size; the volume moves when it
    changes anywhere, including inside its own envelope."""
    solid = _solid_of(shape)
    bb = solid.BoundingBox()
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(solid.wrapped, props)
    return {**{f: getattr(bb, f) for f in ("xmin", "ymin", "zmin", "xmax", "ymax", "zmax")},
            "volume": props.Mass()}


def _metal_holds():
    """Hold every ported body's committed solid to the module that declares its ports.

    The pack seats these bodies from STEPs and carries their stations out of the same modules'
    live Python; nothing in this build re-exports them.

    Box and volume: a part that changed size moves its faces, and a part that changed only
    inside its own envelope moves its material."""
    for body, (builder, step) in PORTED_BODIES.items():
        fresh, stale = _measure(builder()), _measure(_load(step))
        for what, a in fresh.items():
            b, tol = stale[what], (PORTED_VOLUME_TOL if what == "volume" else PORTED_METAL_TOL)
            if abs(a - b) > tol:
                raise ValueError(
                    f"{body}: its module draws {what} = {a:.6f} and {step.name} carries "
                    f"{b:.6f} — {abs(a - b):.6f} apart. The pack seats that STEP and reads this "
                    f"file's ports out of the module, so the two have parted: re-export "
                    f"{step.name} from its own module, or the ports stand off the metal.")


def _stations_hold():
    """Every part that holds its own declared figures to a solid, beside the figures it holds.

    The two harvested fittings and the three panel bodies read theirs back off the STEPs they
    were measured from — the same two-readings gap `_metal_holds` closes for the pack, on the
    bodies `_panel_bodies` seats instead. The condenser and the board have no file to disagree
    with: their modules draw them, and what each holds is the datum its stations stand on."""
    _tee_ref.stations_hold()
    _ydiv.stations_hold()
    _cond.stations_hold()
    _pcba.stations_hold()
    _jg.stations_hold()
    _iec.stations_hold()
    _derpipe.stations_hold()
    _gasher.stations_hold()
    _wr1110.stations_hold()


# --- Pack cache -----------------------------------------------------------
# Placing the pack is 18.4 s a process and every process pays it. What comes out is 34 solids
# and the seat each took — 4 MB of BRep, which writes and reads back in 0.1 s apiece — so the
# pack keeps as cheaply as the scorecard verdict does.
#
# A seat is one `cq.Location`; it keeps as its transformation's twelve values rather than as
# `toTuple`'s Euler angles, which name the same pose more than one way.
#
# OFF unless `HSM_PACK_CACHE=1`. A key that misses something that moves a body serves geometry
# from before it moved, and every gate on the card would then be measuring the wrong machine.
# The key is `fresh.inputs` — every module of this repo imported by the time the pack is
# placed, which is all thirty-odd reference modules, plus the STEPs it seats and the editor's
# overrides — so it is the same reading `fresh.py` stamps a card with.
_PACK_CACHE_DIR = Path(__file__).resolve().with_name(".enclosure-assembly.pack-cache")


def _pack_cache_key() -> str:
    import fresh

    steps = [str(v) for v in globals().values()
             if isinstance(v, Path) and v.suffix == ".step" and v.is_file()]
    return hashlib.sha256(
        repr(fresh.inputs(steps + [str(MOVES_PATH)])).encode()).hexdigest()


def _seat_values(seat) -> list:
    t = seat.loc.wrapped.Transformation()
    return [t.Value(i, j) for i in range(1, 4) for j in range(1, 5)]


def _seat_of(values: list):
    from OCP.gp import gp_Trsf

    t = gp_Trsf()
    t.SetValues(*values)
    return _seating.Seat(cq.Location(t))


def _pack_cache_load(key: str):
    """The placed pack as it was last written under this key, or None."""
    from OCP.BRep import BRep_Builder
    from OCP.BRepTools import BRepTools
    from OCP.TopoDS import TopoDS_Shape

    d = _PACK_CACHE_DIR
    try:
        if (d / "key").read_text().strip() != key:
            return None
        rows = json.loads((d / "manifest.json").read_text())
    except (OSError, ValueError):
        return None
    pack = _placing.Pack(_moves())
    placed = {}
    for row in rows:
        shape = TopoDS_Shape()
        if not BRepTools.Read_s(shape, str(d / f"{row['name']}.brep"), BRep_Builder()):
            return None
        solid = cq.Shape.cast(shape)
        pack.solids[row["name"]] = solid
        pack.seats[row["name"]] = _seat_of(row["seat"])
        placed[row["name"]] = (solid, cq.Color(*row["color"]))
    return pack, placed


def _pack_cache_save(key: str, pack, placed: dict) -> None:
    from OCP.BRepTools import BRepTools

    d = _PACK_CACHE_DIR
    try:
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True, exist_ok=True)
        rows = []
        for name, (solid, color) in placed.items():
            BRepTools.Write_s(solid.wrapped, str(d / f"{name}.brep"))
            rows.append({"name": name, "color": list(color.toTuple()),
                         "seat": _seat_values(pack.seats[name])})
        (d / "manifest.json").write_text(json.dumps(rows))
        (d / "key").write_text(key + "\n")
    except (OSError, AttributeError, KeyError):
        shutil.rmtree(d, ignore_errors=True)


def _build():
    global _PACK
    if os.environ.get("HSM_PACK_CACHE"):
        key = _pack_cache_key()
        hit = _pack_cache_load(key)
        if hit is not None:
            _PACK = hit[0]
            return hit[1]
    _stations_hold()
    _metal_holds()
    pack = _PACK = _placing.Pack(_moves())
    placed = pack.solids

    # --- Zone A: the cold core, yawed a quarter turn and seated in the
    # back-bottom corner, flat on the floor slab. X is fenced by the seam posts
    # standing on the footprint's own ±X edges, +Y by the back Z-seam lip.
    pack.place("foam-assembly", _load(FOAM_ASSEMBLY), yaw=FOAM_YAW,
               west=at(CORE_WEST_FACE), front=at(FRONT_DEPTH), foot=at(0.0))

    # --- Zone D: the compressor on the floor, the condenser standing above it.
    # The shroud stands one SEAM_CLEAR_LIFT off the floor slab, centred across the
    # band the cold core's own footprint opens; the condenser takes the +X end of
    # that band, one STACK_GAP over the shroud's roof. The shroud's copper face
    # reads +Y across the machine corridor at the core; the condenser's exhaust
    # face reads +X at the side wall it stands against.
    pack.place("compressor-shroud", _load(COMP_SHROUD), yaw=SHROUD_YAW,
               centre_x=between(flush("foam-assembly", "west"),
                                flush("foam-assembly", "east")),
               front=at(0.0), foot=at(SEAM_CLEAR_LIFT))
    pack.place("condenser+fan", _cond.build(),
               east=flush("foam-assembly", "east"), front=at(0.0),
               foot=off("compressor-shroud", "crown", STACK_GAP))
    _band = pack.box("foam-assembly")

    # --- Zone B, the service bay above the cold core: the WATER DECK in the rear band,
    # the electronics shelf on the cap's own deck mounts in the front third.
    # The pump: its lane's centreline in X, its FRONT FACE on the band the deck opens at,
    # its base on the cap. The yaw turns the 187 mm motor axis onto Y, so the face the band
    # holds is the one that turn put there.
    pack.place("seaflo-pump", _load(SEAFLO_STEP), yaw=SEAFLO_YAW,
               org_x=at(SEAFLO_LANE_X), front=at(seaflo_front_y()), foot=at(foam_cap_top()))
    # The chain on the pump's crown: its west face one `LINE_HUG` inboard of `CORE_WEST_FACE`,
    # its aft face on the discharge barb's own y, its foot one `LINE_HUG` off the roof. Its
    # BARB points +Y at a molded discharge pointing −X, and the 3/8" stub between them comes
    # about in the wall pocket on the hose's own radius and climbs the pump's west flank onto it.
    # The chain is joined to the pump by a HOSE (`water-6`, 3/8" braided PVC) and not screwed
    # to its barb, so nothing about the casting fixes it across the machine — what it owes the
    # pump is reach, and what it owes the box is to stand out of the ±X rib band. It rides the
    # casting's crown and holds its west face one `LINE_HUG` inboard of `CORE_WEST_FACE`; its
    # aft end still stands on the discharge's own plane, which is the axis the hose leaves on.
    pack.place("discharge-chain", _load(DISCH_CHAIN_STEP), turn=(DISCH_CHAIN_TURN,),
               west=at(CORE_WEST_FACE + LINE_HUG),
               aft=at(seaflo_terminal("discharge")[0][1]),
               foot=off("seaflo-pump", "crown", LINE_HUG))
    # The carb riser's flow meter, aloft over the pump on the riser's own aft leg.
    pack.place("digiten-flow", _load(DIGITEN_STEP), yaw=DIGITEN_YAW,
               org=(DIGITEN_POS[0], DIGITEN_POS[1], digiten_seat()))
    # The CO2 chain's two inline bodies, wall-hung in the machine corridor off the east
    # wall, both yawed a quarter turn so their flow runs west. Each is seated by the MOUTH
    # the chain closes on rather than by the face its envelope ends at: the check by the
    # socket the DERPIPE's stub threads into (`_panel_bodies` seats that fitting on the same
    # station and holds the joint), the regulator by the socket co2-1 reaches, one hop
    # inboard of the check's own stub tip.
    pack.place("gasher-co2", _load(GASHER_STEP), yaw=90.0, station=_gasher.inlet(),
               port=(CO2_GASHER_X, CO2_INLET_Y, CO2_INLET_Z))
    pack.place("wr1110", _load(WR1110_STEP), yaw=90.0, station=_wr1110.inlet(),
               port=(pack.port("gasher-co2", _gasher.outlet())[0][0] - CO2_HOP,
                     CO2_INLET_Y, CO2_INLET_Z))
    # The ASSE chain, seated by its own flow axis: the line every fitting on it stands on,
    # laid onto `asse_axis()`, which is the bulkhead's own column and stratum. The turns carry
    # that line, so the roll swings the chain about the axis it protects instead of about the
    # part's zero.
    pack.place("asse1022-assembly", _load(ASSE_STEP),
               # The roll is about the axis the YAW left the flow on — world Y, not world X.
               # About X it is a pitch, and it swings the chain's whole length off the lane.
               turn=(((0, 0, 1), ASSE1022_YAW), ((0, 1, 0), ASSE1022_ROLL)),
               station=_bfp.flow_axis(), port=asse_axis())
    # The split: its plan station, and its own RUN on the chain's flow axis — one plane with
    # the outlet that feeds it, so water-2 is a step east and no fall. Turned as it is, the
    # face that lands is the hub's, and the branch hangs off it at the deck below.
    _out = bfp_terminal("tube-out")[0]
    pack.place("water-split", _load(WATER_SPLIT_STEP),
               turn=(((1, 0, 0), SPLIT_ROLL), ((0, 1, 0), SPLIT_PITCH)),
               org_x=at(_out[0]), org_y=at(split_y()), org_z=at(_out[2]))
    # The regulator: the sequence's third fitting, inline on the split's flavor collet — same
    # column, same plane, its inlet a `JUNCTION_LEG_LEAD` of straight ahead of that mouth.
    # Placed off the split's own collet, so it follows the sequence.
    _flv = split_terminal("to-flavor")[0]
    pack.place("flow-regulator", _load(FLOWREG_STEP), turn=FLOWREG_TURNS,
               org_x=at(_flv[0]), org_y=at(flowreg_lane()),
               org_z=at(_flv[2] - FLOWREG_DROP))
    # The basin hangs off the CHAIN'S OWN PLAN BOX — the whole of it, because the vent is
    # horizontal and sheds down the fitting's outside, so a drip leaves anywhere along the
    # length rather than off one column. X centres on that box; Y on the vent's own column,
    # the axis the basin has depth to spare on and the one it withdraws along; Z is the
    # chain's underside (`drip_pan_seat`). `_pan_room` is the reading that the tip still
    # stands over the inner floor.
    _vent_xy = bfp_terminal("vent-tip")[0]
    _rail_dx, _rail_dy, _rail_dz = _pan.rail_offset()
    # The RAIL is the widest thing this assembly has, so it and not the basin is what answers
    # to the rib inset — the basin may not set the machine's width, which is what keeps
    # `enclosure._dims` striking the width off the core at both flanks. That inset is a FLOOR
    # under the station and not the station itself: driven onto it the basin leaves the vent
    # it is under, so the chain's own centre stands the pan and the inset only catches it.
    _asse_box = pack.box("asse1022-assembly")
    _pan_x = max((_asse_box.xmin + _asse_box.xmax) / 2.0 - DRIP_PAN_X / 2.0,
                 -SIDE_RIB_INSET - _rail_dx)
    # Y centres on the vent, held off the DISCHARGE CHAIN'S BARB by what a hose leaving that
    # barb needs on its own axis. The barb faces aft into this basin's front wall, so a basin
    # centred on the vent alone stands in the mouth of the line it is nothing to do with. The
    # vent's column has the basin's whole depth to sit anywhere in, and the barb's lead has
    # none — so the barb sets the floor and the vent takes what is left, which `_pan_room`
    # reads back. The floor is the lead PLUS the stub's own half-section and a hug: what has
    # to clear this wall is the hose, and a hose on its lead is a tube and not a centreline —
    # its OUTSIDE, over the barb, and not the bore the barb is sized by.
    _pan_y = max(_vent_xy[1] - DRIP_PAN_Y / 2.0,
                 disch_terminal("barb-tip")[0][1] + JUNCTION_LEG_LEAD
                 + _disch.HOSE_OD / 2.0 + LINE_HUG)
    _pan_z = drip_pan_seat()
    _pan_room(_pan_x, _pan_y, _vent_xy)
    pack.place("drip-pan", _load(DRIP_PAN_STEP),
               west=at(_pan_x), front=at(_pan_y), foot=at(_pan_z))
    pack.place("drip-pan-rails", _load(DRIP_RAILS_STEP),
               west=flush("drip-pan", "west") + _rail_dx,
               front=flush("drip-pan", "front") + _rail_dy,
               foot=flush("drip-pan", "foot") + _rail_dz)

    # The power block on the +X wall. Its three seats are three faces of the machine and not
    # three numbers: EAST on `CORE_EAST_FACE`, the plane the ±X rib band ends on, so the brick
    # stands clear of every post, pod and plug the Y seam puts in that band; AFT on the rear
    # seam lip's own standoff, the plane every interior body stops at; and FOOT on the cap's
    # lid, the floor this whole storey stands on. Nothing here is chosen — each is a face the
    # machine already had.
    pack.place("psu", _load(MEANWELL_STEP), turn=PSU_TURN,
               east=at(EAST_WALL_SEAT),
               aft=at(REAR_PLANE_Y - REAR_STANDOFF - REAR_CORNER_POST - LINE_HUG),
               foot=at(foam_cap_top()))
    # The relay STANDS ON THE +X WALL over the brick, its board's face to that wall and its
    # cans looking inboard — the face a screwdriver reaches and the face a boss lands on.
    # Three seats: EAST on `EAST_WALL_SEAT`, AFT on the brick's own aft plane, FOOT one
    # clearance floor over its crown.
    pack.place("relay-1", _load(RELAY_STEP), turn=RELAY_TURN,
               east=at(EAST_WALL_SEAT),
               aft=flush("psu", "aft"),
               foot=off("psu", "crown", LINE_HUG))
    # The hub sits ON THE RELAY, one clearance floor over its crown and on that module's own
    # east face, its wells opening INBOARD off the wall — one column of five bodies up this
    # flank where the deck once held four, with nothing wet anywhere over any of it.
    #   Its aft face reads the C14 rather than the brick's: the receptacle is the one body on
    # this flank that comes inboard at the hub's own height.
    #   It carries NO HOLD-DOWN of its own (`ac_hub`) — it is a tray, and whatever body ends up
    # carrying it grows this footprint into itself — so nothing here reads a screw pattern and
    # no row in `scorecard.MOUNTED_BY` claims one.
    pack.place("ac-hub", _load(AC_HUB_ASSEMBLY), turn=AC_HUB_TURN,
               east=flush("relay-1", "east"),
               aft=at(c14_inboard_y() - LINE_HUG),
               foot=off("relay-1", "crown", LINE_HUG))
    # The stud goes up the same wall, over the hub — the last of the electrical bodies off the
    # cap. It stands on the hub's own aft plane, which is what keeps it forward of the C14's
    # body: the receptacle reaches inboard at exactly this height and is the only thing on this
    # flank that does.
    pack.place("ground-stack", _load(GND_STACK), turn=RELAY_TURN,
               east=at(EAST_WALL_SEAT),
               aft=flush("ac-hub", "aft"),
               foot=off("ac-hub", "crown", LINE_HUG))

    # --- Zone C: the manifold's first three trays, stacked in the front column under the
    # funnel, a junction standing ahead of each. Not one of the six poses picks a coordinate
    # off a wall: the source tray hangs on the hopper drain's own column and on the core's
    # front face, each tray under it on the tray above, and each junction on the pair it joins.
    for name, tray_pos in (("source-tray-assembly", source_tray_pos()),
                           ("selects-tray-assembly", selects_tray_pos()),
                           ("bag-a-tray-assembly", bag_a_tray_pos())):
        pack.place(name, _load(TRAY_ASSEMBLY), yaw=TRAY_YAW, org=tray_pos)
    # --- Zone C's second stand: both pumps under the head column's own lane, and the AFT STAND
    # on the water deck carrying the rest of channel B — the bag-B pair with Y-H ahead of it,
    # and three LONE VALVES each on the family's one-seat plate (`single_valve_tray`): the
    # tap-water fill valve and the two nozzle gates. The bag pair is the one pair here, so it
    # is the one two-seat plate, and each of the other three is placed by its OWN runs.
    pack.place("bag-b-tray-assembly", _load(TRAY_ASSEMBLY), yaw=BAG_B_TRAY_YAW,
               org=bag_b_tray_pos())
    pack.place("vk-tray-assembly", _load(TRAY1_ASSEMBLY), yaw=TRAY_YAW, org=vk_tray_pos())
    pack.place("nozzle-b-tray-assembly", _load(TRAY1_ASSEMBLY), yaw=TRAY_YAW,
               org=nozzle_b_tray_pos())
    pack.place("nozzle-tray-assembly", _load(TRAY1_ASSEMBLY), yaw=NOZZLE_TRAY_YAW,
               org=nozzle_tray_pos())
    pack.place("divider-y-g", _load(Y_DIVIDER), turn=DIVIDER_G_TURNS, org=y_g_pos())
    # The controller board STANDS ON THE WET SIDE'S OWN FLANK, forward of the electrical stack
    # rather than over it. The air above the brick is spoken for three bodies deep — the relay
    # on its crown, the hub over that, the ground stack over that — and this board is longer
    # than what they leave.
    #   THE ROLL IS WHAT PUTS IT HERE. A quarter turn about its own long axis lays that axis
    # fore and aft down the flank instead of standing it up into the top, so only the board's
    # thickness reaches inboard. It also makes the board 90.8 long in Y, and the front and back
    # tops carry side ribs down onto `CORE_EAST_FACE` at two stations in this band — a board out
    # on the wall would have to clear both and would then have less than its own length left
    # before the receptacle. So it stands INBOARD of the rib line, on the flank they leave open.
    #   Three seats. EAST one clearance floor inside `CORE_EAST_FACE` — the rib line, and the
    # plane the whole electrical flank already takes. AFT one floor forward of the V-K row's own
    # forward face: that row is the one wet body standing at this height on this flank, the two
    # overlap in plan, and Y is what parts them. FOOT on the cap's top, the plane every body on
    # this deck stands from.
    pack.place("pcba", _load(PCBA_BOARD), turn=PCBA_TURN,
               east=at(CORE_EAST_FACE - LINE_HUG),
               aft=at(pack.box("vk-tray-assembly").ymin - LINE_HUG),
               foot=at(foam_cap_top()))
    # Both pumps, side by side in the front column on ONE lane and one plane. Channel B is
    # seated FIRST because channel A stands on it. B's Z is not a pick: it stands the two barbs
    # on the BAG-A PAIR'S OWN PORT PLANE, so Y-C and Y-D — the two tees that join this pump to
    # that tray and to the selects pair — lie in one plane with the collets they join and no leg
    # climbs. A is that pose stepped EAST by the twin's own barb SPAN plus one `PUMP_TWIN_PITCH`,
    # which puts the two inner barbs of the row a tube's width and a floor apart, and it takes
    # its front and its foot off the twin's own faces — so all four barbs are one row across the
    # strip. Both take the same turns, so the span carries over.
    pack.place("pump-b", turned_pump("pump-b"),
               west=at(PUMP_B_LANE_X), front=at(PUMP_B_FRONT_BAND),
               foot=at(bag_a_tray_pos()[2] + _tray.port_z - PUMP_PORT_RISE))
    pack.place("pump-a", turned_pump("pump-a"),
               west=flush("pump-b", "west") + pump_barb_span("pump-b") + PUMP_TWIN_PITCH,
               front=flush("pump-b", "front"), foot=flush("pump-b", "foot"))
    # The seven tees. The manifold's own junction stands on the two columns its four ports make
    # (`junction_tee_pos`); channel A's pump row stands in the lane pump B's own two lines run
    # down (`pump_row_tee_pos`); channel B's stands on the aft stand — Y-G on the column its
    # run joins, Y-F in the lane pump A's lines run down (`aft_row_tee_pos`); Y-E stands across
    # the strip ahead of the bag-A pair (`y_e_pos`). Each takes the turns `TEE_TURNS` gives it,
    # the same ones its ports are carried through.
    for name in JUNCTION_TEES + tuple(TEE_LANE) + AFT_ROW_TEES + ("tee-y-e",):
        pack.place(name, _load(TEE_CONNECTOR), turn=TEE_TURNS[name],
                   org=junction_tee_pos(name) if name in JUNCTION_TEES
                   else aft_row_tee_pos(name) if name in AFT_ROW_TEES
                   else y_e_pos() if name == "tee-y-e"
                   else pump_row_tee_pos(name))

    # Y-H last, and seated by its EAST FACE rather than its origin. It stands on the pair's west
    # flank, so what has to hold is the reach between two placed bodies — and a divider's origin
    # is not its own bbox centre. Read off the seated plate, the reach is the reach whatever the
    # fitting's frame calls its middle.
    _yh = y_h_pos()
    pack.place("divider-y-h", _load(Y_DIVIDER), turn=DIVIDER_H_TURNS,
               east=at(pack.box("bag-b-tray-assembly").xmin - divider_reach()),
               org_y=at(_yh[1]), org_z=at(_yh[2]))

    out = {n: (s, COLORS[n]) for n, s in placed.items()}
    if os.environ.get("HSM_PACK_CACHE"):
        _pack_cache_save(key, pack, out)
    return out


def _asse_axis_drop():
    """How far the chain hangs under its own flow axis AT THE ROLL IT IS BUILT WITH.

    The body is rolled about its flow axis and measured, so whatever is lowest answers — the
    vent stub while it points down, the barrel once the stub is turned off the bottom. Yaw is
    not applied: a turn about Z moves nothing vertically."""
    ax, d = _bfp.flow_axis()
    solid = _bfp.build()
    solid = solid.toCompound() if hasattr(solid, "toCompound") else solid
    solid = solid.val() if hasattr(solid, "val") else solid
    rolled = solid.rotate(tuple(ax), tuple(ax[i] + d[i] for i in range(3)), ASSE1022_ROLL)
    return ax[2] - rolled.BoundingBox().zmin


def _asse_axis_west():
    """How far the chain reaches WEST of its own flow axis, at the turns it is built with.

    Both turns are applied, and in the order and about the axes the placement uses: the yaw
    first, about world Z, which is what lays the flow axis across the machine; then the roll
    about world Y, the line the yaw left that axis on. Unlike the drop, this reading DOES turn
    on the roll's sign — the barrel answers on one side and the vent stub on the other, and
    they are half the machine's rib band apart — so it cannot be taken about the part's own
    axis the way `_asse_axis_drop` is."""
    ax, _d = _bfp.flow_axis()
    solid = _bfp.build()
    solid = solid.toCompound() if hasattr(solid, "toCompound") else solid
    solid = solid.val() if hasattr(solid, "val") else solid
    yawed = solid.rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), ASSE1022_YAW)
    rolled = yawed.rotate(tuple(ax), (ax[0], ax[1] + 1.0, ax[2]), ASSE1022_ROLL)
    return ax[0] - rolled.BoundingBox().xmin


def port_row_z():
    """The stratum the rear port field stands on, and the top of the TAP-WATER STACK.

    That stack hangs off this row and reads DOWN to the manifold's aft stand — the ASSE chain,
    `drip_pan.VENT_GAP` of air under the vent it weeps from, the basin, the rails that carry
    it, and then the stand. So the row is that column read the other way up, from the highest
    reach anything on the stand takes: Y-G's stem faces UP out of the junction bay, and what it
    needs over its own collet face is the `JUNCTION_LEG_LEAD` its run turns on
    (`scorecard.port_leads`) and a clearance floor over that for the rails.

    `drip_pan_seat()` is the same column read back down, and it raises when it runs out."""
    stem = (aft_port_z()                             # the stand's own port plane
            + Y_G_CLIMB + 2.0 * DIVIDER_HALF)        # up through the trident to its stem face
    rails = stem + JUNCTION_LEG_LEAD + LINE_HUG      # the stem's own lead, and a floor over it
    # The chain's own drop — flow axis to whatever of it hangs lowest at the roll it is built
    # with. The vent stub is that only while it points DOWN, so this row cannot go on paying
    # for a stub that has been rolled off the bottom (`_asse_axis_drop`).
    return rails + _pan.RAIL_LIFT + _pan.PAN_Z + _pan.VENT_GAP + _asse_axis_drop()


def foam_cap_top():
    """The foam cap's LID outer face — the water deck's floor, the Z the pump's base sits
    on and the Z the PSU's does. The foam assembly's own top is higher: the modules'
    deck-mount columns stand `deck_mount_proud()` through the lid, and those modules ride
    their tops.

    Off the placed body's crown. The core is the first thing `_build` seats, and every stratum
    above it reads that seat."""
    return packed().box("foam-assembly").zmax - _cc.deck_mount_proud()


def shroud_roof_z():
    """The compressor shroud's roof in world — the front column's own floor above the
    refrigeration stratum, and the plane the front Z seam's band opens over.

    Off the placed body — seated second, long before the manifold that stands over it."""
    return packed().box("compressor-shroud").zmax


def core_plan_centre():
    """The cold core's plan centre in world: `(x, y)` — the centreline every station that
    hangs on the core reads. Off the placed body's own box."""
    b = packed().box("foam-assembly")
    return ((b.xmin + b.xmax) / 2.0, (b.ymin + b.ymax) / 2.0)


def deck_mount(name):
    """A cap deck mount in world: `(centre, stations, top_z)`.

    Two turns stand between the cap's own frame and world: the cap's install spin, which the
    foam assembly carries (`foam_assembly.deck_mount_station`), and `FOAM_YAW`, which the
    pack's seat carries. A module's world yaw is its own plus `FOAM_YAW` — the
    rectangle it bolts to turned, so the module turns with it or sits across its own columns.

    `top_z` is where the module's underside seats — the column tops of a mount that stands
    through the lid, the lid's own face of one that stops beneath it."""
    pts = tuple(packed().point("foam-assembly", (px, py, 0.0))[:2]
                for px, py in _foam_asm.deck_mount_station(name))
    ctr = (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))
    return ctr, pts, foam_cap_top() + _cc.deck_mount_standoff(name)


# The aft stand's two deck mounts, and the placed tray each one bolts. These two rows of
# the cap's table read the OTHER way from the modules': a module is placed BY its station,
# but a tray is placed by the enclosure's own fences and the station stands where the
# tray's mount ears land — so the ears are the authority, and the table's figures are held
# to them by the scorecard's `deck-mounts-land` check, whose fail row carries the stations
# a moved tray wants.
TRAY_MOUNTS = {"bag-b-tray": "bag-b-tray-assembly", "vk-tray": "vk-tray-assembly",
               "nozzle-b-tray": "nozzle-b-tray-assembly",
               "nozzle-tray": "nozzle-tray-assembly"}


def tray_mount_holes(mount):
    """One aft-stand plate's M3 clearance holes in world plan: a tuple of `(x, y)`.

    The tray module owns the stations (`two_valve_tray.mount_stations`) and the seat the pack
    gave the plate carries them out — so the holes follow the tray wherever its fences send it,
    and the cap's table is what has to keep up. The one-seat plate carries the family's ears at
    the family's `ear_y` (`single_valve_tray`), so one station pattern answers for every row of
    the stand whichever part the row is."""
    body = TRAY_MOUNTS[mount]
    return tuple(packed().point(body, (x, y, 0.0))[:2] for x, y in _tray.mount_stations())


def tray_mount_seat():
    """The plate thickness an aft-stand mount's screw crosses before the lid — the `seat`
    figure the cap's table must carry for both tray rows. One part family, one figure,
    read off the part so a rethickened plate is a drift the alignment check can see."""
    return _tray.top_z - _tray.bot_z


def foam_cap_frame(p):
    """A world plan point in the TOP CAP's own authoring frame: `(x, y)` — the frame
    `_cold_core_interface.deck_mounts` is written in. The inverse of `deck_mount`'s two
    turns, built off the placed body so it cannot drift from them: the pack's seat read
    at three probe points, then the install spin, which is its own inverse. This is the
    voice of the `deck-mounts-land` fail row — the row a moved tray wants, in the frame
    the table wants it in."""
    o = packed().point("foam-assembly", (0.0, 0.0, 0.0))
    ex = packed().point("foam-assembly", (1.0, 0.0, 0.0))
    ey = packed().point("foam-assembly", (0.0, 1.0, 0.0))
    d = (p[0] - o[0], p[1] - o[1])
    ax = d[0] * (ex[0] - o[0]) + d[1] * (ex[1] - o[1])
    ay = d[0] * (ey[0] - o[0]) + d[1] * (ey[1] - o[1])
    return _foam_asm.spin_xy((ax, ay))


def foam_shell_port(station):
    """One station of the foam assembly, in world: `(pos, face)`.

    Nine open on the shell's own −X face, on the port lane, at their own height up the column
    — the six on the front port field (`_cold_core_interface.front_port_stations`) and the
    three the copper/PRV slot carries (`copper_plugs.slot_stations`). The yaw puts that face
    on world −Y, facing the user, where the machine corridor runs under the shroud's roof.
    The rest are CAP CONDUITS (`_cold_core_interface.cap_conduits`), opening +Z on the lid's
    outer face, which is the service bay's own floor.

    Each is declared by the part that draws it; the seat the pack gave the assembly carries
    the position and the way out alike."""
    return _world("foam-assembly", _foam_station(station))


# The two copper bores are ONE BORE TWICE, so which stub is suction and which discharge is
# piped inside the shroud and the assignment is made here, for the runs: the DISCHARGE takes
# the EAST hole, under the tray-east lane refrig-1 climbs to the condenser's crown, and the
# SUCTION the WEST one, at the end of the low corridor sweep refrig-3 comes home on. The
# shroud's own module names the two by the wall position it bores them at.
SHROUD_PORTS = {
    "refrig-suction":   "refrig-west",
    "refrig-discharge": "refrig-east",
    "ac-mains":         "ac-mains",
    "earth-bond":       "earth-bond",
}


def shroud_port(name):
    """One compressor-shroud penetration in world: `(x, y, z)`. The shroud's own module
    declares each on the wall face it crosses; the seat the pack gave the body carries it."""
    return _world("compressor-shroud", _shroud.port(SHROUD_PORTS[name]))[0]


def condenser_port(name):
    """One condenser+fan penetration in world: `(x, y, z)`. The block's own module declares
    all three, each on the face it crosses; the seat the block took carries them. Each stands
    where a 1/4" copper leg can arrive: the block's +Y face stands `CORE_FACE_CLEAR` off the
    cold core and nothing routes in that sheet.

    Which face the hot gas enters by is the block's; which wall it stands against is Zone D's
    above. Refrig-1's climb up the tray-east lane turns in over the crown, and refrig-2 steps
    west out of the intake face into the same lane and falls to the evaporator's stratum."""
    return _world("condenser+fan", _cond.stations()[name])[0]


def _foam_station(station):
    """One of the foam assembly's stations, in its OWN frame — a front-field station by
    name, the line under one of the slot's three plugs, or a cap conduit. Each is declared
    by the part that draws it; this only says which of the three owns the name.

    A conduit is authored in the cap's frame and the cap installs spun, so
    `foam_assembly.cap_conduit_station` is what carries it here; its Z is the lid's own
    outer face, which the stack's crown less the tallest deck standoff gives."""
    if station in _cc.front_port_order:
        return _cc.front_port_station(station)
    if station in _cc.cap_conduits:
        x, y = _foam_asm.cap_conduit_station(station)
        return ((x, y, _stack_lid_top_z()), _foam_asm.cap_conduit_axis_out())
    return _plugs.slot_station(station)


def _stack_lid_top_z():
    """The top lid's outer face in the foam assembly's OWN frame — the plane a cap conduit
    opens on, and the one the deck stands on. The shell's own height, the cap seated on it,
    and the lid's plate closing its mouth."""
    return (_cc.foam_shell_outer_height + _cc.foam_cap_height
            + _cc.wall_and_floor_thickness)


def foam_shell_stations():
    """Every station the foam assembly carries, low → high: the six on the front port
    field, the three the slot carries above them, and the cap conduits over the top."""
    return sorted(list(_cc.front_port_stations()) + list(_plugs.slot_stations())
                  + list(_cc.cap_conduits),
                  key=lambda s: _foam_station(s)[0][2])


def foam_shell_bore():
    """The one ⌀ every front-face station crosses. The port lane is one bore wide,
    which is what makes the field a column rather than a grid — so the six round
    bores and the shared slot's width are the same number, and the shell has one
    answer for how fat a line crossing it may be. What is wider than this has a
    warm-side fitting standing in for the line at the wall; `assembly/cold-core.md`
    is explicit that every transition happens out there and every penetration
    through the shell wall is 1/4" OD."""
    bore, slot = _cc.port_hole_radius * 2, _slot_width
    assert abs(bore - slot) < 1e-9, (
        f"the round bores are ⌀{bore:g} and the slot is ⌀{slot:g} — the lane no longer "
        f"has one width, so a port cannot be checked against a single number")
    return bore


# --- Zone B poses and terminals --------------------------------------------
# Each body's pose is stated once, and every station on it is carried through that same
# pose rather than typed again beside it. A port that reads its world coordinates through
# these moves when the pose does, instead of being retyped after it.

SEAFLO_TERMINALS = {"suction": _seaflo.suction, "discharge": _seaflo.discharge}


def seaflo_terminal(name):
    """One of the SeaFlo's two head barbs in world: `(pos, face)`. They leave the head's
    ±Y side faces, so the yaw that turns the pump turns them with it."""
    return _world("seaflo-pump", SEAFLO_TERMINALS[name]())


def bulkhead_water_mouth():
    """The tap-water bulkhead's INBOARD collet face, in world: `(x, y, z)`.

    The one station in the wall sequence that is not a consequence of the pack — the union is
    made up through the rear panel, so its mouth stands where `REAR_PLANE_Y` and the fitting's
    own inboard reach put it. `scorecard.PORTS` reads the same three figures for `tube-in`."""
    return (WATER_BACK_X, REAR_PLANE_Y + WALL + _jg.port(-1)[0][1], port_row_z())


def asse_axis():
    """The line the ASSE chain is laid on, in world: `(x, y, z)`.

    X and Z are the station it is fed from — `bulkhead-water`'s own column across the machine
    and its own height up the wall, read off the port row. Move the row and the chain moves
    with it.

    Y is the same station: the chain's inlet mouth stands `ASSE_INLET_HOP` of tube ahead of the
    bulkhead's own, and the whole sequence hangs forward off that hop. The wall is the one end
    of this chain that cannot move, so it is the end the chain is measured from — every
    millimetre the sequence does NOT spend standing off the panel is a millimetre at the far
    end, where `fluid-2`'s two leads are what the forward budget buys (`_lines.lean_leads`)."""
    inlet = _bfp.port("tube-in")[0][0]              # the inlet mouth's own station, upstream
    return (WATER_BACK_X,
            bulkhead_water_mouth()[1] - ASSE_INLET_HOP + inlet,
            port_row_z())


def split_y():
    """The Y of the water split's run centre: its supply collet one `JUNCTION_LEG_LEAD` of
    straight ahead of the chain's outlet, which faces back up the lane at it. `water-2` is that
    straight. Read off the chain rather than picked, so the split follows the sequence."""
    outlet = _bfp.port("tube-out")[0][0]            # the outlet mouth's own station, downstream
    return asse_axis()[1] - outlet - JUNCTION_LEG_LEAD - _split.REACH


def asse_underside():
    """The lowest point anywhere on the placed chain — the ceiling over the drip pan."""
    return packed().box("asse1022-assembly").zmin


def bfp_terminal(name):
    """One of the ASSE 1022 assembly's three terminals in world: `(pos, face)`.

    The reference assembly owns all three — `tube-in` off the PP010822E's own port,
    `tube-out` off the flare38-14ptc's 1/4" collet, `vent-tip` at the stub's open end — and
    the pack carries them on the seat the chain took."""
    pos, axis = packed().port("asse1022-assembly", _bfp.port(name))
    return pos, _face_of(axis)


def drip_pan_seat():
    """The Z the drip pan's floor stands at — the top face of its rails.

    The basin hangs off the chain, `drip_pan.VENT_GAP` of air between its rim and the placed
    chain's underside. The rail is the bracket that carries a shelf out to the plane that
    leaves; its mount is `drip_pan.py`'s own open item.

    The column that leaves runs out of deck when the basin's rails — hanging
    `drip_pan.RAIL_LIFT` under its floor — reach past the cap the manifold's aft stand stands
    on. `room-holds` carries that reading; the seat is the chain's either way."""
    # The chain sets it, unless the CASTING under it sets it higher: the basin's rails run
    # the length of the pump's own aft half, so their feet have to clear its crown. Both
    # floors stay in the reading and whichever binds is the answer.
    seat = max(asse_underside() - _pan.VENT_GAP - _pan.PAN_Z,
               packed().box("seaflo-pump").zmax + LINE_HUG + _pan.RAIL_LIFT)
    under = seat - _pan.RAIL_LIFT - foam_cap_top()
    if under < 0.0:
        _short("drip-pan-seat",
               f"the basin hangs off a chain whose underside is z={asse_underside():.4f}, which "
               f"puts its floor at {seat:.4f} and its rails' feet {-under:.4f} mm BELOW the foam "
               f"cap at {foam_cap_top():.4f}. Raise `asse_axis()`'s stratum, or take section off "
               f"the basin.")
    return seat


def aft_tray_z():
    """The Z the manifold's aft stand takes — its own tray origin, so a plate's underside
    lands on the foam cap's face, the seat the PSU, the pump and the ac hub take."""
    return foam_cap_top() - _tray.bot_z


def aft_stand_crown():
    """The crown the aft stand's seated valves stand to — the fittings loft's floor."""
    return aft_tray_z() + tray_crown()


def aft_tray_headroom():
    """The air between the aft stand's coils and the basin's rails over them. The chain hangs
    on the bulkhead, the basin hangs off the chain, the stand stands on the cap; this is what
    the column leaves between the last two.

    What the stand puts in it is not the coils but Y-G — its stem stands proud of the crown and
    faces up, so `port_row_z()` sizes this band on that stem's own reach rather than on this
    figure."""
    return (drip_pan_seat() - _pan.RAIL_LIFT) - aft_stand_crown()


def flowreg_lane():
    """The Y of the regulator's centre: its inlet mouth one `JUNCTION_LEG_LEAD` of straight
    ahead of the split's flavor collet, so fluid-1 is that straight and the sequence packs
    the wall — every millimetre of depth it does not spend here is fluid-2's, whose lean to
    V-A spends all of it."""
    return (split_terminal("to-flavor")[0][1] - JUNCTION_LEG_LEAD - _flowreg.REACH
            - FLOWREG_RUN)


SPLIT_TERMINALS = {"supply": _split.supply, "to-vk": _split.to_vk,
                   "to-flavor": _split.to_flavor}


def split_terminal(name):
    """One of the water split's three 1/4" collets in world: `(pos, face)`. The reference
    module owns each station — `supply` and `to_flavor` (the run, the ASSE feed carried
    straight through) and `to_vk` (the branch); the seat the body took carries them."""
    return _world("water-split", SPLIT_TERMINALS[name]())


def vk_terminal(name):
    """One of V-K's two 1/4" QC collets in world: `(pos, face)`.

    V-K rides a plate of its own on the stand's middle row, so its two ports are two of that
    tray's four and they read the same way every other seated valve's do — through the tray
    module's own collets and the seat the pack gave the plate. The valve has no pose of its
    own to carry them."""
    return vk_tray_port(f"V-K-{name[0].upper()}")


FLOWREG_TERMINALS = {"inlet": _flowreg.inlet, "outlet": _flowreg.outlet}


def flowreg_terminal(name):
    """One of the flow regulator's two 1/4" collets in world: `(pos, face)`. Its own frame
    is +X = flow; the yaw that turns the valve turns its ports with it."""
    return _world("flow-regulator", FLOWREG_TERMINALS[name]())


DISCH_TERMINALS = {"barb-tip": _disch.barb_tip, "tube-port": _disch.tube_port}


def disch_terminal(name):
    """One of the discharge chain's two ends in world: `(pos, face)`. The chain is laid
    down by `DISCH_CHAIN_TURN`, and the seat that lays it down carries both stations."""
    return _world("discharge-chain", DISCH_TERMINALS[name]())


CO2_CHAIN_TERMINALS = {"gasher-co2": _gasher.stations, "wr1110": _wr1110.stations}


def co2_chain_port(body, name):
    """One mouth on the CO2 chain's two packed bodies in world: `(pos, face)`. Each module
    owns its own pair — the check's female socket and its male stub tip, the regulator's two
    female sockets — and the quarter turn that lays the chain's flow west carries them."""
    return _world(body, CO2_CHAIN_TERMINALS[body]()[name])


def co2_inlet_seat():
    """The seat the DERPIPE takes through the east wall: a quarter turn laying its flow axis
    on −X, then its own STUB TIP onto the GASHER's socket mouth.

    `build()` places that check before the wall it hangs off exists, so the joint is made up
    here, where both bodies are in hand. `panel_bodies()` seats the metal on this and
    `co2_inlet_port` reads the fitting's two ends through it."""
    turn = _seating.Seat.turn((0, 0, 1), 90.0)
    tip = turn.port(_derpipe.stub_tip())[0]
    return turn.then(_seating.Seat.shift(
        tuple(p - t for p, t in zip((CO2_GASHER_X, CO2_INLET_Y, CO2_INLET_Z), tip))))


def co2_inlet_port(name):
    """One end of the DERPIPE in world: `(pos, face)`. Its module owns both — the 5/16" PTC
    collet outboard, the NPT stub tip inboard — and the seat the wall gave it carries them."""
    pos, axis = co2_inlet_seat().port(_derpipe.stations()[name])
    return pos, _face_of(axis)


def digiten_seat():
    """The Z the DIGITEN's own origin stands at — one `DIGITEN_DROP` under the rear port row,
    so the climb `carb-2` makes out of its outlet is the same whatever stratum the row takes."""
    return port_row_z() - DIGITEN_DROP


DIGITEN_TERMINALS = {"inlet": _digiten.inlet, "outlet": _digiten.outlet,
                     "wire-exit": _digiten.wire_exit}


def digiten_terminal(name):
    """One of the flow meter's two 1/4" PTC collets, or its pigtail boss tip, in world:
    `(pos, face)`. The reference module owns each station; the yaw that lays the flow
    along the riser's own axis carries them, so the collets land fore and aft and the
    boss stays up."""
    return _world("digiten-flow", DIGITEN_TERMINALS[name]())


PSU_TERMINALS = {"ac-in": _psu_ref.ac_in, "dc-out": _psu_ref.dc_out}


def psu_terminal(name):
    """One of the PSU's two terminal blocks in world: `(pos, face)`. The Mean Well's own
    frame puts the AC primary on +Y and the DC secondary on −Y, each a screw block standing
    on its stepped end ledge; the seat the shelf gave the module carries them, and both land
    face-up, which is how a ferrule goes under a captive screw."""
    return _world("psu", PSU_TERMINALS[name]())


def ac_hub_lug(pole):
    """One of the AC hub's three Wago lever nuts in world: `(pos, face)`. H / N / G run
    along the row. Each lug stands on its butt end in its well, so the wire ports face up
    off its top face."""
    return _world("ac-hub", _achub.lug(pole))


RELAY_TERMINALS = {"contacts": _relay_ref.contacts, "logic": _relay_ref.logic}


def relay_terminal(name):
    """One of relay #1's two terminal groups in world: `(pos, face)`. The Teyleten's own
    frame puts the COM/NO/NC screw block on +X and the VCC/GND/IN header on −X; both land
    face-up over the PCB, which is the plane a ferrule goes down onto."""
    return _world("relay-1", RELAY_TERMINALS[name]())


def ground_stud():
    """The ground bus's landing in world: `(pos, face)` — the top of the lug fan, where the
    next ring terminal goes on and the screw comes down."""
    return _world("ground-stack", _gnd_ref.landing())


def pcba_pose():
    """Where the board's OWN origin lands in world: `(x, y, z)`. Seating the board is putting
    the centre of its four MH holes on the centre of the cap's `pcba` deck mount — then every
    hole is over its own column by construction, and nothing here chooses a coordinate.

    The offset is where the hole centroid has to come FROM: that centroid under the board's own
    yaw, subtracted. `_build` gives the pack the yaw, so the seat it keeps is the whole of the
    move and `pcba_port` reads a board station through it."""
    ctr, _pts, top = deck_mount("pcba")
    holes = _pcba.board.holes
    cx, cy, _ = _seating.Seat.turn((0, 0, 1), PCBA_YAW).point(
        (sum(h[0] for h in holes) / len(holes), sum(h[1] for h in holes) / len(holes), 0.0))
    return (ctr[0] - cx, ctr[1] - cy, top)


def pcba_port(px, py):
    """A point in the board's OWN pcb frame — `pcbX`/`pcbY` exactly as written in
    [`pcba.tsx`](/hardware/pcb/pcba/pcba.tsx) — carried to world. The board's own module puts
    the point on its TOP FACE, the plane every one of its wafers and both edge connectors mate
    off, and the seat the shelf gave the board carries it."""
    return packed().port("pcba", _pcba.port(px, py))[0]


# --- Zone C poses and terminals ---------------------------------------------

_TRAY_CROWN = None


def tray_crown():
    """How far a seated tray's tallest point stands over its own origin — the valve coils'
    crown, measured off the STEP that is placed rather than read back through the cell the
    seats were cut from. One number for all five: they are one part."""
    global _TRAY_CROWN
    if _TRAY_CROWN is None:
        _TRAY_CROWN = _boxes.boxed(_load(TRAY_ASSEMBLY)).zmax
    return _TRAY_CROWN


def tray_stack_pitch():
    """Origin to origin down the manifold's column — a tray's own crown over its own plate
    underside, plus the `TRAY_STACK_GAP` that keeps the valves under it liftable. One part
    five times, so one pitch carries the whole stack."""
    return tray_crown() - _tray.bot_z + TRAY_STACK_GAP


def _tray_column_plan():
    """The head column's X and Y — one footprint, one holder column, all three seats. Neither
    coordinate is picked off a wall.

    X hangs the EAST seat on the hopper spout's own column, so V-B's inlet stands under the
    drain and the fall never has to cross the machine. The spout sits `neck_dx` off the
    funnel's collar centre, and the collar is centred across an interior whose ±X faces are
    the cold core's own plus one boss chain each (`enclosure._dims`) — so that column is the
    CORE's centreline carrying the spout's own offset, and it is read off the core here
    because the funnel is seated in a box sized from this pack and asking it would recur.
    What holds the two on one line is `_lines`' fluid-4: it falls down the drain's own column
    and closes into V-B-I, and `route` refuses that close the day they part.

    Y stands the aft collets `SOURCE_TRAY_AFT_BAND` ahead of the cold core's front face."""
    cx, _cy = core_plan_centre()
    return (cx + _funnel.neck_dx - _tray.seat_x,
            FRONT_DEPTH - SOURCE_TRAY_AFT_BAND - _tray.port_half)


def pump_foot_drop():
    """How far channel A's pump hangs BELOW the bag-A plate it is levelled with — the part of
    the column that reaches lowest. `_build` stands the pump's barbs on that pair's own port
    plane (`_tray.port_z`) and the barbs sit `PUMP_PORT_RISE` up its own body, so the difference
    is what the foot drops. Positive: the foot is under the plate."""
    return PUMP_PORT_RISE - _tray.port_z


def bag_a_tray_pos():
    """The bag-A tray's own origin in world — the column's BOTTOM seat, and the seat the two
    above it hang off.

    The column stands on the refrigeration stratum's ROOF, so Z is the height that leaves one
    `FRONT_COLUMN_FLOOR` under the lowest thing standing in it. That is channel A's pump:
    `pump_foot_drop()` is how far its foot hangs below this plate. What the plate itself is
    left is `tray_column_floor()`.

    X and Y are the column's (`_tray_column_plan`). Its two valves are seated opposite ways
    round, Y-E hangs ahead on the pair's own port plane, and the aft collets stand on
    `SOURCE_TRAY_AFT_BAND`. The manifold's other two pairs stand aloft (`bag_b_tray_pos`,
    `nozzle_tray_pos`)."""
    x, y = _tray_column_plan()
    return (x, y, shroud_roof_z() + FRONT_COLUMN_FLOOR + pump_foot_drop())


def selects_tray_pos():
    """The selects tray's own origin in world — one `tray_stack_pitch()` UP the column from the
    bag pair, which is the pack: this tray's coils under the plate above, the bag pair's coils
    under this one. X and Y are the column's, so Y-B lands directly under Y-A and the merge
    falls into the split in a single plane."""
    x, y, z = bag_a_tray_pos()
    return (x, y, z + tray_stack_pitch())


def source_tray_pos():
    """The source tray's own origin in world — the column's TOP seat, one more
    `tray_stack_pitch()` up, midway between its two seats on the valve mounting plane.

    It is the pair whose pose is not chosen in X: `_tray_column_plan` hangs its east seat on
    the hopper spout's column. In Z it is the seat nearest the basin, which roofs the column at
    the minimum `scorecard`'s `clear hopper-funnel` holds it to."""
    x, y, z = selects_tray_pos()
    return (x, y, z + tray_stack_pitch())


def source_tray_crown_z():
    """The crown the source pair's seated valves stand to — the top of the head column, and the
    part of it the funnel overhead bears on."""
    return source_tray_pos()[2] + tray_crown()


def tray_column_floor():
    """The band under the manifold column's bottom plate: the shroud's roof to the bag-A tray's
    plate underside. No line crosses in it — every corridor `_lines` uses passes the column on
    the outside — so this is service space.

    `bag_a_tray_pos` stands the column so its lowest body clears the roof by
    `FRONT_COLUMN_FLOOR`, and this plate is that floor plus what the pump's foot hangs below it.
    Both of those can move, and the plate that ends up in the roof names itself here.

    The roof is boxed from the same load-turn-lift `_build` seats it by rather than read off the
    pack, for `core_plan_centre`'s reason: the manifold is placed DURING that build, so a
    manifold pose asking the pack for the shroud would recur."""
    roof = shroud_roof_z()
    plate = bag_a_tray_pos()[2] + _tray.bot_z
    band = plate - roof
    if band < 0.0:
        _short("tray-column-floor",
               f"the manifold column's bottom plate is at z={plate:.2f}, under the compressor "
               f"shroud's roof at {roof:.2f}. `FRONT_COLUMN_FLOOR` is {FRONT_COLUMN_FLOOR:.2f} and "
               f"the pump's foot drops {pump_foot_drop():.2f} below the plate, so one of those two "
               f"has gone negative — the column cannot stand on a floor it is under.")
    return band


# The four collets each tray hands out, under the names the manifold knows them by. Both
# pairs read WEST to EAST in the topology's own order — V-A then V-B, V-C then V-D.
#   The SOURCE pair is clocked INLET AFT, OUTLET FORWARD: its two feeds come from the back
# of the machine and Y-A stands ahead. Its east seat takes V-B, the hopper gate, on the
# drain's column.
#   The SELECTS pair is clocked the other way round — INLET FORWARD, OUTLET AFT — because
# Y-B has to stand ahead of it (`selects_tray_pos`) and the pump row it feeds is aft. The
# cell is symmetric under a half turn, so the tray permits either at either seat and never
# fixes which end of a port is the inlet; this is the only thing that differs between the
# two poses.
#   The BAG-A pair has its two valves seated OPPOSITE ways round: V-E draws from the bag and
# V-F returns to it, so the bag is V-E's INLET and V-F's OUTLET. Those two are the pair Y-E
# joins and they face FORWARD, where a junction has the `divider_reach()` and body half-length
# it stands off by; aft of them lie `SOURCE_TRAY_AFT_BAND` and then the cold core's front
# face. V-E-O and V-F-I face aft, both at the pump row, with the rest of channel A.
BAG_A_TRAY_COLLETS = {
    "V-E-I": "xn-yn", "V-E-O": "xn-yp",
    "V-F-I": "xp-yp", "V-F-O": "xp-yn",
}
SOURCE_TRAY_COLLETS = {
    "V-A-I": "xn-yp", "V-A-O": "xn-yn",
    "V-B-I": "xp-yp", "V-B-O": "xp-yn",
}
SELECTS_TRAY_COLLETS = {
    "V-C-I": "xn-yn", "V-C-O": "xn-yp",
    "V-D-I": "xp-yn", "V-D-O": "xp-yp",
}


def _tray_port(body, name, collets, mod=_tray):
    """One of a tray's bare collets in world: `(pos, face)`. The tray module owns every one
    of them (`two_valve_tray.port_collets`, `three_valve_tray.port_collets`), so a seat pitch
    or a port length changed there moves the world station with it; the seat the pack gave
    that tray carries it out. Two plates, four off and one off, one reading for both."""
    return _world(body, mod.port_collets()[collets[name]])


def source_tray_port(name):
    return _tray_port("source-tray-assembly", name, SOURCE_TRAY_COLLETS)


def selects_tray_port(name):
    return _tray_port("selects-tray-assembly", name, SELECTS_TRAY_COLLETS)


def bag_a_tray_port(name):
    return _tray_port("bag-a-tray-assembly", name, BAG_A_TRAY_COLLETS)


_DIVIDER_REACH: float | None = None


def divider_reach():
    """How far off the collets it joins a divider's own outlet faces stand: the offset each
    leg closes, over the tangent of the lean the collet allows.

    Each leg is ONE STRAIGHT LENGTH OF TUBE at this reach. The outlet and the collet face each
    other down their own axis with the offset square to it, so a straight between them leaves
    each mouth `atan(offset / reach)` off that axis; at `offset / tan(FLAVOR_SKEW)` that angle
    is the whole of what a push-to-connect collet grips through, and the leg carries the offset
    with no corner in it. `_lines` draws both of Y-H's legs to exactly this.

    Shorter, and the leg breaks into two corners — and the reach it takes then is the LEAST
    that seats a stock arc in them, because every millimetre past that is deck spent on the
    other side of the pair, where the collets facing east have their own runs to leave in.
    `_lines` builds both legs to whichever this returns."""
    offset = (_tray.pitch - 2.0 * DIVIDER_OUTLET_X) / 2.0
    straight_reach = offset / math.tan(math.radians(FLAVOR_SKEW))

    def seats(reach):
        """The roundest arc the two corners hold at this reach, over every lead and lean the
        collet allows. Symmetric: the two mouths face each other with the offset square
        between them, so what one lead takes the other takes."""
        best = 0.0
        for i in range(1, 61):                        # the lean, up to the collet's own
            th = math.radians(FLAVOR_SKEW * i / 60.0)
            for j in range(1, 121):                   # the lead, out to half the reach
                lead = DIVIDER_LEG_STRAIGHT + 0.25 * j
                px, py = lead * math.cos(th), lead * math.sin(th)
                gx, gy = reach - 2.0 * px, offset - 2.0 * py
                leg = math.hypot(gx, gy)
                if gx <= 0.0 or leg < LINE_HUG:        # the leg must travel toward the far mouth
                    continue
                turn = abs(math.atan2(gy, gx) - th)
                k = math.tan(turn / 2.0)
                r = min(LLDPE_STOCK_BEND, (lead - DIVIDER_LEG_STRAIGHT) / k) if k > 1e-6 \
                    else LLDPE_STOCK_BEND
                if 2.0 * r * k <= leg - LINE_HUG:      # a straight still left between the arcs
                    best = max(best, r)
        return best

    global _DIVIDER_REACH
    if _DIVIDER_REACH is None:
        lo, hi = 0.0, straight_reach
        for _ in range(30):
            mid = (lo + hi) / 2.0
            lo, hi = (lo, mid) if seats(mid) >= LLDPE_STOCK_BEND - 1e-9 else (mid, hi)
        _DIVIDER_REACH = hi
    return _DIVIDER_REACH


def _divider_pos(origin, collet):
    """A divider's body centre in world, given its tray's origin and one of the two collets
    it joins. On the pair's own centreline in X and on their port plane in Z — the junction
    lies in one plane with the two valves it joins, so neither leg climbs — and
    `divider_reach()` FORWARD of them in Y, one divider half-length past its outlet faces."""
    return (origin[0], collet[0][1] - divider_reach() - DIVIDER_HALF, collet[0][2])


def junction_column_x():
    """The two junction columns' X in world: `(west, east)`.

    A column stands on its own two ports' X where the fitting lets it. Two branches facing each
    other put `2 × TEE_BRANCH_REACH` between their body centres before there is any tube at
    all, and the seats are a valve body apart (`two_valve_tray`'s pitch is the Beduan's own
    width), so the wider of the two is what the columns take. The day the junction is built
    from a fitting that fits between the seats, `max` returns the seat and the columns come
    home to their ports with a longer crossbar for it.

    That fitting is PRICED, not stocked, and the search has been run: home means branch
    reach ≤ (pitch − TEE_RUN_LEAD)/2 = 15.13 mm from run axis to branch collet face, and no
    published dimensional drawing reaches it — a 1/4" PTC cartridge is 13.5 mm of collet
    stack before any body wall. The incumbent PP0208E class measures 20.07 and is the one
    Prime-purchasable NSF-listed part (PP0208WP). The nearest defensible real figure is
    18.5 — Parker LIQUIfit 6304 56 00WP2, derived from Parker's own 6304 drawing (H24 −
    G11/2 on the 1/4" row), NSF 51/FDA, run L/2 = 18 against the PP0208E's 20.07, no Prime
    channel — which closes 1.57 of the 4.95 spread and hands the run legs 2.07 of drop
    back. The one architecture that could dip under 15.13 is o-rings moulded into the body
    (KegLand Monotight KL21944); it has no drawing and needs calipers on a physical part —
    an owner measurement, recorded here, not designed around. Until one of those lands,
    the spread is 4.95 a side and each column leg carries it inside its one leaning move."""
    west = source_tray_port("V-A-O")[0][0]
    east = source_tray_port("V-B-O")[0][0]
    half = max((east - west) / 2.0, TEE_BRANCH_REACH + TEE_RUN_LEAD / 2.0)
    mid = (west + east) / 2.0
    return (mid - half, mid + half)


def junction_crossbar():
    """The exposed tube between the two branch collet faces — the H's bar. Short when the
    columns have closed to where a butted joint has no tube left to make."""
    west, east = junction_column_x()
    span = (east - west) - 2.0 * TEE_BRANCH_REACH
    if span < TEE_RUN_LEAD - 1e-9:
        _short("junction-crossbar",
               f"the crossbar comes out {span:.2f} mm, under the {TEE_RUN_LEAD:.2f} mm of exposed "
               f"tube a butted joint needs — the branch reach ({TEE_BRANCH_REACH:.2f}) has "
               f"outgrown the column spacing ({east - west:.2f}). Widen the columns by "
               f"{TEE_RUN_LEAD - span:.2f}, or take reach off the branch.")
    return span


def junction_tee_pos(tee):
    """A junction tee's body centre in world: on its own column in X, as far AHEAD of the
    port plane in Y as the front chain lets a body stand, and midway down the stack pitch in
    Z so the two legs off it are one length.

    Y is the whole radius budget the four column legs share, and it is spent to its wall:
    every millimetre of standoff is forward tangent for the two corners each leg turns, and
    the wall is the machine's front chain — the pumps front-packed on the corner's seam
    furniture (`PUMP_B_FRONT_BAND`), the motor's own square behind that, the pack's floor,
    and then this fitting's own radius about its run. The tee stands ON that plane, never
    nearer the ports than the lead a leg must leave its collet on. Short when the fitting's
    run has filled the pitch and a leg has no room left to leave its collet on axis and
    turn."""
    west, east = junction_column_x()
    src = source_tray_port("V-A-O")[0]
    sel = selects_tray_port("V-C-I")[0]
    standoff = (src[2] - sel[2]) / 2.0 - TEE_RUN_HALF
    if standoff < JUNCTION_LEG_LEAD + LLDPE_BEND:
        _short("junction-tee-standoff",
               f"a junction tee's run collet stands {standoff:.2f} mm off the port plane, under "
               f"the {JUNCTION_LEG_LEAD + LLDPE_BEND:.2f} mm its leg needs to leave on axis and "
               f"turn — the fitting's run ({2 * TEE_RUN_HALF:.2f}) has filled the stack pitch "
               f"({src[2] - sel[2]:.2f}). Open the pitch by "
               f"{2 * (JUNCTION_LEG_LEAD + LLDPE_BEND - standoff):.2f}.")
    chain = PUMP_B_FRONT_BAND + _kamoer.head_w + LINE_HUG + TEE_HALF_W
    if chain > src[1] - JUNCTION_LEG_LEAD:
        _short("junction-tee-chain",
               f"the front chain's floor plane ({chain:.2f}) stands nearer the port plane "
               f"({src[1]:.2f}) than the {JUNCTION_LEG_LEAD:.2f} a column leg leaves its collet "
               f"on — the pumps have packed aft past the junction's lead. Step the column aft by "
               f"{chain - (src[1] - JUNCTION_LEG_LEAD):.2f}, or the pumps forward.")
    return (west if tee == "tee-y-a" else east,
            chain,
            (src[2] + sel[2]) / 2.0)


# The sequence a Y-divider is clocked through: the yaw that turns its outlets onto the seat
# pitch, then the roll that lays its axis down along Y. `build` places the divider through it,
# so the order is written once.
DIVIDER_TURNS = (((0, 0, 1), DIVIDER_YAW), ((1, 0, 0), DIVIDER_ROLL))
# Y-G takes the trident on its NATIVE axis — stem up, outlets down — and the yaw alone, which
# lays the outlet offsets across the machine. Standing on its short section it costs the
# junction bay 2 x `y_divider.HALF_W` of depth instead of its own length.
DIVIDER_G_TURNS = (((0, 0, 1), -90.0),)
# Y-H takes the sequence and then the QUARTER TURN ITS OWN PAIR TOOK (`BAG_B_TRAY_YAW`), so its
# two outlets come to rest on the axis of the two collets they feed. The turn rides the plate's
# own figure: a pair re-clocked carries this fitting round with it.
DIVIDER_H_TURNS = DIVIDER_TURNS + (((0, 0, 1), BAG_B_TRAY_YAW),)


# A divider's three ports in its OWN frame: the stem on the axis at +Z, the two outlets
# facing −Z, offset ±Y. The two turns put local −Y on the machine's WEST, so the west outlet
# is the one that reaches the west seat. The topology numbers the fitting from its own end —
# Y-H takes the bag on its stem with a valve on each outlet.
def _divider_local(stem, west, east):
    at = _ydiv.stations()
    return {west: at["-y"], east: at["+y"], stem: at["stem"]}


def _divider_port(body, name, local):
    """One of a divider's three collets in world: `(pos, face)`. It reads out on the seat
    `DIVIDER_TURNS` made, which is the seat the solid is standing on."""
    return _world(body, local[name])


# --- The pump row's tees, in the pump lane ---------------------------------
# Y-C is channel A's SUCTION junction — the shared source and the bag draw meeting at pump
# B's inlet — and Y-D its DISCHARGE junction, splitting that pump's outlet between the bag
# and the nozzle. Neither joins one tray's own pair, so neither is a divider: each reaches
# between two trays, or between a tray and the pump, and what joins those is a run and a
# branch (`../../../topology/fluid-topology.md`).
#
# The pose is not three coordinates picked per fitting. A tee's run is a LANE and its centre
# stands on it, so all three fall out of the lane the pump's own two lines already run down:
#   X — the barb's own column, so the leg between pump and tee is one straight length; held
#       off the front column's west rim by the body's own radius where the barb sits nearer
#       the wall than the body fits, and off the tray column's face the same way.
#   Y — midway between the barb it stands off and the aft band its tray leg turns in, so
#       neither of the run's two legs is the short one.
#   Z — the plane of the two ports the run joins, which for both of these is the bag-A
#       pair's own port plane: `_build` stood the barbs on it for exactly this reason, so
#       no leg of the run climbs and the only climb is the branch's.
TEE_LANE = {                          # tee → the pump barb whose column its run stands on
    "tee-y-c": ("pump-b", "P-B-I"),
    "tee-y-d": ("pump-b", "P-B-O"),
}


def pump_lane_x():
    """The pump lane's two rims: `(west, east)` — the front column's Z-seam lip on one side
    and the tray column's own west face on the other. A tee's body centre lives between them
    by its own radius and the clearance floor."""
    return (FRONT_COLUMN_WEST + TEE_HALF_W + 1.0,
            bag_a_tray_pos()[0] - _tray.half_x - TEE_HALF_W - 1.0)


def pump_row_tee_pos(tee):
    """A pump-row tee's body centre in world. See the block above: the barb's plane in Z, its
    own column in X, midway between barb and band in Y.

    Each tee stands on the column of the barb its run butts, so that leg is one straight
    length — and where the barb sits nearer a rim than the fitting's body fits, the tee is the
    one that gives way and the leg leans. Pump B's two barbs straddle the lane: the inlet is
    outboard of the west rim, the outlet inboard of the tray column, so both tees are pushed
    in and the lane's own width is what holds them apart. Short when the two rims cross, which
    is the day the lane stops being wide enough for a fitting at all — the tee is drawn on the
    east rim and the lane's overlap read off `room-holds`."""
    pump, barb = TEE_LANE[tee]
    (bx, by, bz), _face = pump_port(pump, barb)
    west, east = pump_lane_x()
    if east < west:
        _short("pump-lane",
               f"the pump lane's rims have crossed — its west is x={west:.2f} and its east "
               f"x={east:.2f}, so no tee body fits between the front column's lip and the tray "
               f"column. Move the tray column {west - east:.2f} east, or stand the pump row "
               f"elsewhere.")
    band = FRONT_DEPTH - SOURCE_TRAY_AFT_BAND + PUMP_ROW_TURN
    return (min(max(bx, west), east), (by + band) / 2.0, bz)


# A tee's three ports in its OWN frame: the run's two on ±Z, the branch out +Y. The topology
# numbers each fitting from its own end — Y-C merges two feeds into the pump and Y-D splits one
# out of it — so which name lands on the branch is the numbering's business and not the
# geometry's, and this is where the two meet. Where those axes point in world is `TEE_TURNS`'
# business: `TEE_ROLL` lays the run along Y and stands the branch up, and a yaw alone leaves
# the run standing and swings only the branch.
def _tee_local(zp, zn, branch):
    """The fitting's own three ports under the names the manifold knows."""
    at = _tee_ref.stations()
    return {zp: at["+z"], zn: at["-z"], branch: at["branch"]}


# Y-C: the run carries the bag draw forward into the pump's inlet, and the branch takes the
# fall from the selects pair a stack pitch above. Under `TEE_ROLL`, +Z is the forward collet.
_Y_C_LOCAL = _tee_local(zp="Y-C-3", zn="Y-C-2", branch="Y-C-1")
# Y-D: the run takes the pump's outlet aft and on to the bag's fill valve, and the branch is
# the storey-high climb to the nozzle gate in the loft.
_Y_D_LOCAL = _tee_local(zp="Y-D-1", zn="Y-D-2", branch="Y-D-3")
# Y-A and Y-B: the run stands UP the column, +Z at the source pair and −Z at the selects pair a
# stack pitch below, and the branch is the crossbar between them. Numbered from the source end.
_Y_A_LOCAL = _tee_local(zp="Y-A-1", zn="Y-A-2", branch="Y-A-3")
_Y_B_LOCAL = _tee_local(zp="Y-B-1", zn="Y-B-2", branch="Y-B-3")


def _tee_port(tee, name, local):
    """One of a tee's three collets in world: `(pos, face)`. It reads out on the seat
    `TEE_TURNS[tee]` made, which is the seat the solid is standing on."""
    return _world(tee, local[name])


def y_a_port(name):
    return _tee_port("tee-y-a", name, _Y_A_LOCAL)


def y_b_port(name):
    return _tee_port("tee-y-b", name, _Y_B_LOCAL)


def y_c_port(name):
    return _tee_port("tee-y-c", name, _Y_C_LOCAL)


def y_d_port(name):
    return _tee_port("tee-y-d", name, _Y_D_LOCAL)


# --- Y-E: the bag-A junction, across the strip ahead of its pair -----------
# Y-E joins what Y-H joins, in the same order: V-F's outlet where the pump returns to the bag,
# V-E's inlet where the bag draws, and one line out to reservoir A's port on the cold core's
# face. It stands in the STRIP between the pump row's aft faces and the tray column's forward
# one, and it stands ACROSS it — both collet axes square to Y, all three collets in one vertical
# plane, the body's own diameter the whole of the depth it takes.
#
# So the RUN lies along X, the axis that strip runs on, and the BRANCH points DOWN.
#   The run's two collets face OUTBOARD, `2 × TEE_RUN_HALF` apart against a seat pitch of
# `_tray.pitch`: a leg handed the collet standing outboard of its own seat has to come about to
# enter it. So one valve joins on the BRANCH, and the run carries the reservoir line — the one
# of the three that arrives along the strip rather than off a seat.
#   A down-facing collet is entered by a RISING leg, so the branch collet stands one
# `JUNCTION_LEG_LEAD` OVER the port plane the two seats share, and the leg that takes it leaves
# its collet on axis for that lead and turns once — the relation the manifold's own junction
# columns are built on (`junction_tee_pos`).
#   Y-E-2, the reservoir's, is the run's EAST collet: the line comes west out of the tray-east
# lane and straight in. Y-E-3, the draw, is the run's WEST. Y-E-1, the fill, is the branch, and
# the tee stands on V-F's own column so that leg runs forward under the branch and climbs in.
def y_e_pos():
    """Y-E's body centre in world.
      X — V-F's own column, so the leg that takes the branch never leaves it.
      Y — the middle of the strip, so the body owes the pump row and the tray column the same.
      Z — one `JUNCTION_LEG_LEAD` over the pair's port plane at the BRANCH collet, which stands
          the run one `TEE_BRANCH_REACH` above that.

    Short when the strip has closed to where this fitting no longer stands across it."""
    collet, _face = bag_a_tray_port("V-F-O")
    twin = packed().box("pump-b")
    strip = collet[1] - twin.ymax
    body = 2.0 * TEE_HALF_W + 2.0 * 1.0        # one `scorecard.CLEARANCE_FLOOR` either side
    if strip < body:
        _short("y-e-strip",
               f"the strip between the pump row's aft face (y={twin.ymax:.2f}) and the bag pair's "
               f"forward collets (y={collet[1]:.2f}) is {strip:.2f} mm, and Y-E across it is "
               f"{2 * TEE_HALF_W:.2f} mm of body with a clearance floor owed either side "
               f"({body:.2f}). Step the pump row {body - strip:.2f} forward, or the head column "
               f"that much aft.")
    return (collet[0],
            (twin.ymax + collet[1]) / 2.0,
            collet[2] + JUNCTION_LEG_LEAD + TEE_BRANCH_REACH)


# Under `TEE_TURNS`, local +Z is the run's WEST collet and local −Z its EAST; the branch is DOWN.
_Y_E_LOCAL = _tee_local(zp="Y-E-3", zn="Y-E-2", branch="Y-E-1")


def y_e_port(name):
    return _tee_port("tee-y-e", name, _Y_E_LOCAL)


# --- Zone C's second stand: the two pumps, the bag-B pair and the nozzle gates ---
# The turns each pump takes. BOTH stand NATIVE — depth axis up, motor down, barbs out the +Y
# face at the lane behind them. They are one pose read twice, side by side in the front column,
# which is the one place in this machine with the height a KPHM400 standing on end wants.
PUMP_TURNS = {
    "pump-a": (),
    "pump-b": (),
}
# Which barb each pump's suction and discharge takes. A peristaltic head has no fixed sense
# — the rotor's direction is the motor's wiring — so this is an assignment and not a
# property of the part, and each is made so the two legs do not cross.
#
# Channel A's inlet takes the EAST barb. Each of its tees stands on its own barb's column
# (`pump_row_tee_pos`), so this puts the SUCTION tee east and the DISCHARGE tee west — and
# that is the order the bag-A pair presents: the draw is on the tray's west seat and the fill
# on its east, so the suction leg turns west across the aft band and the discharge leg turns
# east under it, each crossing the other's lane once and neither crossing the other's stub.
# Read the other way round, both legs run the length of the band and cross twice.
#
# Channel B's inlet takes the LOW barb, at Y-F, which its line climbs to from the front column.
PUMP_PORT_INDEX = {
    "pump-a": {"P-A-I": 1, "P-A-O": 0},
    "pump-b": {"P-B-I": 1, "P-B-O": 0},
}


def pump_twin_gap():
    """What the two pumps' flanks are left with once their inner barbs stand a
    `PUMP_TWIN_PITCH` apart. The pack does not pick it — the barb pitch does."""
    return packed().box("pump-a").xmin - packed().box("pump-b").xmax


def _pump_turns(pump) -> _seating.Seat:
    """The seat a pump's own turns make, before it is seated anywhere."""
    seat = _seating.Seat()
    for axis, deg in PUMP_TURNS[pump]:
        seat = seat.then(_seating.Seat.turn(axis, deg))
    return seat


def turned_pump(name):
    """The pump under its own turns, before the seat."""
    return _pump_turns(name).solid(_load(KAMOER_STEP))


def _pump_station(pump, name):
    """One of a pump's two barbs in the PUMP'S OWN frame: `(position, outward axis)`. The pump's
    own module declares both (`kamoer_kphm400.barb`); which of the two takes the suction is
    `PUMP_PORT_INDEX`'s assignment, because a peristaltic head has no fixed sense."""
    return _kamoer.barb(PUMP_PORT_INDEX[pump][name])


def pump_barb_span(pump):
    """Across a pump's two barbs, under its own turns — the X its twin steps by.

    A DIFFERENCE between two stations on one body: the seat cancels out of it, and it is known
    before either pump stands anywhere."""
    turns = _pump_turns(pump)
    inlet, outlet = (turns.port(_pump_station(pump, n))[0] for n in PUMP_PORT_INDEX[pump])
    return inlet[0] - outlet[0]


def pump_port(pump, name):
    """One of a pump's two barbs in world: `(pos, face)`. The seat the pack gave the pump
    carries the part's own station, so a barb cannot drift off its head."""
    return _world(pump, _pump_station(pump, name))


_SEAFLO_STEP: tuple | None = None


def seaflo_aft_step():
    """Where the SeaFlo's crown steps down, and what it stands at behind that: `(y, z)`.

    The pump is ONE BOX in every table this repo prints and TWO HEIGHTS in the machine — the
    head and its pressure switch reach the box's `zmax`, and the motor can behind them stands
    a storey lower. Every line that crosses the aft stand up here passes BEHIND that step, so
    a lane hung off the box's crown is hung off a part of the casting nowhere near it — this
    is what that lane is entitled to instead, and the difference is the two figures returned.

    Read off the placed solid, not off a typed station: the aftmost reach of the material at
    full height, and the crown of everything behind that plane. Memoized — the shelf's floor
    and the gates' approach both ask, and the boolean is not free."""
    global _SEAFLO_STEP
    if _SEAFLO_STEP is None:
        sea = build()["seaflo-pump"][0]
        bb = sea.BoundingBox()
        crest = sea.intersect(_box(bb.xlen + 2.0, bb.ylen + 2.0, 0.5).located(
            cq.Location(cq.Vector(bb.xmin - 1.0, bb.ymin - 1.0, bb.zmax - 0.5))))
        step_y = crest.BoundingBox().ymax
        aft = sea.intersect(_box(bb.xlen + 2.0, bb.ymax - step_y + 1.0, bb.zlen + 2.0).located(
            cq.Location(cq.Vector(bb.xmin - 1.0, step_y, bb.zmin - 1.0))))
        _SEAFLO_STEP = (step_y, aft.BoundingBox().zmax)
    return _SEAFLO_STEP


_SEAFLO_SLOT: dict = {}


def seaflo_lid_slot(x: float, y: float) -> float:
    """The clear height over the cap lid at one plan column before the SeaFlo's casting closes
    it, measured off the placed solid.

    The pump stands on the lid on a foot pad and its head, flange and switch all start a storey
    above that, so the band under them is OPEN and a line may cross it — which is the only way
    anything reaches the core's water inlet, since the head's own block stands over that port's
    column. A bounding box says none of this: the box is solid from the foot to the crown, and
    a run priced against it reads a port under this casting as unreachable when it is a
    thirteen-millimetre slot.

    Returns the lid-to-material height at `(x, y)`, or the full lid-to-crown height where the
    casting has nothing over that column. Memoized per column; the boolean is not free."""
    key = (round(x, 3), round(y, 3))
    if key not in _SEAFLO_SLOT:
        sea = build()["seaflo-pump"][0]
        bb = sea.BoundingBox()
        column = sea.intersect(_box(0.1, 0.1, bb.zlen + 2.0).located(
            cq.Location(cq.Vector(x - 0.05, y - 0.05, bb.zmin - 1.0))))
        over = column.BoundingBox().zmin if column.Solids() else bb.zmax
        _SEAFLO_SLOT[key] = over - bb.zmin
    return _SEAFLO_SLOT[key]


def seaflo_front_y():
    """The pump's front face — the west lane's own far end read forward.

    The pump and the bag pair share the west lane one behind the other, and the casting is the
    aft one — so it packs AFT, its own back on the core's, and the whole of the lane's slack
    falls between it and the pair ahead rather than behind it. That band is what the bag pair's
    junctions and the tap-water column stand in.
    The valve it draws from is in the OTHER lane and is positioned by that lane's own fitting
    (`vk_tray_y`), so what stands between them is a crossing water-4 makes on its own terms."""
    return packed().box("foam-assembly").ymax - _seaflo.OVERALL_L


def vk_tray_y():
    """The middle row's origin in Y — the east lane's FORWARD row, standing on the plane its
    own junction opens on.

    FORWARD is where this lane's slack belongs. These rows have a junction plane to answer to
    and the electrical block behind them has three joints still to build, so a lane packed
    forward onto its own fence leaves the band aft of it deep enough to take a bracket as well
    as a body.

    THE BAND IN FRONT OF THIS FACE IS Y-G'S. V-J's inlet collet faces −Y and Y-G is what feeds
    it, so what stands between this plate and the west lane's aft face is that one trident on
    its own two floors — the fitting's own section, a `LINE_HUG` off each plate. The strip is
    the whole gap between the two lanes' facing rows, and `y_g_pos` stands the trident in it.

    Everything forward of that band is open: the condenser's aft face is a lane's length ahead
    and nothing of this row's reaches it."""
    return (packed().box("bag-b-tray-assembly").ymax
            + LINE_HUG + 2.0 * _ydiv.HALF_W + LINE_HUG + _tray.port_half)


def nozzle_tray_y():
    """The nozzle-A gate's plate's origin in Y — PACKED AFT AGAINST THE PUMP'S FRONT FACE.

    The plate stands in the one band the west lane leaves between the bag pair's own flank and
    the casting: Y-H hangs forward of it in the pair's port plane, the SeaFlo packs aft against
    the core (`seaflo_front_y`), and what is left between them is this plate's whole allowance.
    Turned, the plate spends its NARROW side on that band.

    IT TAKES THE AFT END OF THE BAND, a line's clearance off the casting, because the slack
    belongs FORWARD. Forward is where `fluid-17` comes down off Y-H's crown into this plate's
    own bay, and a fall wants every millimetre it can get between the trident it clears and the
    collet it lands on — the two corners that fall share that leg and each turns on half of it.
    Aft of the plate there is nothing to give the slack to: the casting's face is a wall."""
    return seaflo_front_y() - LINE_HUG - _tray1.half_x


def _pan_room(pan_x, pan_y, vent):
    """The basin stands under the vent it catches, and does not set the machine's width.

    Two readings, and neither is about the chain. The basin catches the atmospheric vent's own
    stub, so the tip stands over water — measured to the basin's INNER wall face, because a drip
    landing on the rim's top edge can go either way.

    And `enclosure._dims` strikes the interior's west face off whatever body reaches furthest
    west, while `funnel_centre` is that interior's midpoint and the gravity drain stands on it
    (`_funnel_column`). The rail is this part's outermost feature, so it stays inboard of the rib
    inset: a basin that sets the width takes the drain off its own column two derivations later."""
    w = _pan.WALL
    for axis, i, lo, hi in (("x", 0, pan_x + w, pan_x + DRIP_PAN_X - w),
                            ("y", 1, pan_y + w, pan_y + DRIP_PAN_Y - w)):
        if not lo - 1e-9 <= vent[i] <= hi + 1e-9:
            _short(f"drip-pan-catch ({axis})",
                   f"the vent tip stands at {axis} {vent[i]:.2f} and the basin's inner floor spans "
                   f"[{lo:.2f}, {hi:.2f}] — the drip lands outside the basin it is meant for. The "
                   f"basin hangs on this tip in both plan axes, so a tip outside it means the "
                   f"chain has moved out from over its own catch. Walk the chain "
                   f"{min(abs(vent[i] - lo), abs(vent[i] - hi)):.2f} back over the basin in "
                   f"{axis}, or widen the basin to reach it.")


def rear_column_face():
    """The forward face of the back piece's −X CORNER COLUMN — the rearmost plane anything
    standing in the −X rib band may reach.

    The back wall's inner face is `REAR_PLANE_Y` and `REAR_CORNER_COLUMN` of the piece's own
    seam furniture hangs off it in the `SIDE_RIB_INSET` band either side. Read off the stated
    plane rather than off a placed body, because the aft stand's own Y comes out of this and a
    stand seated on a body is a stand that body carries with it."""
    return REAR_PLANE_Y - REAR_CORNER_COLUMN


def aft_stand_depth():
    """The whole stand front to back — three port spans and the two junction bays between them.
    All three plates are one part and every span is read off it, so the stand's depth cannot
    drift from the trays it is made of."""
    return (3.0 * 2.0 * _tray.port_half + AFT_TRAY_BAY + VK_TRAY_BAY)


def fore_deck_column_face():
    """The forwardmost world Y a cap deck column may stand on — the FORWARD analogue of
    `rear_column_face`, and the plane the aft stand packs against.

    The rear one is seam furniture hanging off a stated wall. This one is the CAP'S own: a
    deck mount is a column of the cup, and liquid foam has to reach between that column and
    the cavity wall beside it, so a station stands one wall, one boss radius and one
    `deck_mount_cap_gap` inside the cup's plan edge — the same figure
    `_cold_core_interface`'s deck-mount assert holds every station in the machine to. Read on
    the cap's FRONT edge off the placed body: the stand bolts to the cap, and a stand packed
    against a plane the cap does not carry is a stand that leaves its own columns behind."""
    return (packed().box("foam-assembly").ymin
            + _cc.wall_and_floor_thickness
            + _cc.deck_mount_boss_radius
            + _cc.deck_mount_cap_gap)


def bag_b_tray_y():
    """The plane the aft stand's forward collets open on — V-H's inlet, where the bag draws,
    and V-I's outlet, where the pump returns.

    The pair packs FORWARD onto the LID'S OWN FRONT EDGE — the deck it stands on runs out
    there, and forward of that plane a plate has nothing under it. Turned, its length lies
    across the lane, so the depth this plane carries is `_tray.half_x` either side of the
    origin rather than `port_half`.

    Its two mount ears stand on the turned pattern, both on the origin's own Y, so the plane
    a cap deck column may reach (`fore_deck_column_face`) is read here as a second floor and
    the aft of the two wins.

    Reservoir B's port opens +Z out of the cap at x 11, on the flank this plate's west face
    looks down; the column it stands in is Y-H's (`y_h_pos`), west of the plate entirely."""
    return max(packed().box("foam-assembly").ymin,
               fore_deck_column_face() - _tray.half_x)


def aft_outlet_lane():
    """The band behind the wide plate, where the plate's three aft-facing outlets turn off
    their collets before they climb.

    ONE lane carries all three. The two nozzle gates and V-K stand a seat pitch apart across
    the plate, so their three turns never come near each other in X and none of them owes the
    others a plane of its own — what the band has to hold is a single tube standing one
    `PUMP_ROW_TURN` off the plate's face and one off the wall, `2 × PUMP_ROW_TURN` in all.
    The wall is `REAR_PLANE_Y`, the stated plane the panel bodies seat against, not the
    pump-derived plane the box's depth once followed. What is left is the band's spare, and
    the PLATE cannot take it — the stand packs against the cap's FORWARD column limit
    (`bag_b_tray_y`) — so the lane does: `_lines` strikes it off this same wall and the whole
    spare rides the three leads that turn on it. The band is the deck's whole aft half now,
    and it carries the electronics shelf as well as these three runs."""
    return (REAR_PLANE_Y
            - packed().box("nozzle-tray-assembly").ymax
            - 2.0 * PUMP_ROW_TURN)


def aft_tray_x():
    """The middle row's WEST face — the plane V-K's plate takes across the machine.

    IT PACKS WEST, onto the SeaFlo's own east flank, one `LINE_HUG` off the casting. This row
    stands beside the casting for its whole width and its aft face looks at the pump's suction
    barb, so west is where its own crossing is shortest.
    What that leaves is the strip between its east face and the +X wall's electrical column,
    and the body standing in that column at this row's Y is the PCBA — `pack-closes` is what
    holds the two apart."""
    return packed().box("seaflo-pump").xmax + LINE_HUG


def bag_b_tray_pos():
    """The bag-B pair's own origin in world — the WEST lane's forward seat.

    This pair is the one row of the manifold that is not on the east lane. It takes the band
    forward of the pump, and its WEST FACE STANDS WHERE THE FLANK ENDS: the two cap conduits'
    own column, the standoff the stem's corner takes off it (`stem_standoff`), Y-H's body, and
    the `divider_reach()` the trident's two legs run straight through. Turned, the plate's own
    reach to that face is `port_half`.

    Nothing else is on this deck between the conduits and the +X wall, so the flank is cut to
    the stack that stands in it and the rest of the deck is east of the plate.

    Y is `bag_b_tray_y()` plus the turned plate's own half-depth; Z is the cap."""
    return (min(y_h_stem_x() + 2.0 * DIVIDER_HALF + divider_reach() + _tray.port_half,
                bag_b_east_limit() - _tray.port_half),
            bag_b_tray_y() + _tray.half_x,
            aft_tray_z())


def bag_b_east_limit():
    """The eastmost the pair's own EAST FACE goes — what the deck on that side is worth.

    V-I-I opens east off the turned plate and water-3 falls down V-K's own column across that
    deck on its way into the valve, so what a leg leaving that collet has to turn in is the
    band between the two: a `LINE_PITCH` off the fall, and the collet's own
    `JUNCTION_LEG_LEAD` of straight before anything turns. The flank west of the plate wants
    more travel than this; the deck is what there is."""
    # Read off the row's own seat rather than a placed plate: the middle row packs onto the
    # SeaFlo's flank (`aft_tray_x`) and this pair is seated before it, so the column is the
    # stand's west face, one one-seat plate's reach and one seat pitch — which stands before
    # either plate is in.
    return (aft_tray_x() + _tray1.half_x + _tray.pitch) - LINE_PITCH - JUNCTION_LEG_LEAD


def y_h_stem_x():
    """Where Y-H's STEM collet stands in X, and with it the divider's own west face.

    `stem_standoff()` east of reservoir B's bore — the reach the corner off that conduit turns
    on. That standoff already clears `conduit_column_east()`, which `_short` holds."""
    stem = foam_shell_port("reservoir-b")[0][0] + stem_standoff()
    if stem < conduit_column_east():
        _short("y-h-stem",
               f"Y-H's stem stands at x {stem:.2f}, west of the {conduit_column_east():.2f} the "
               f"cap conduits' own column leaves a body. The standoff the corner wants is "
               f"under the tube and floor the column is.")
    return stem


def conduit_column_east():
    """The east side of the CAP CONDUITS' column, as a body sees it — the westmost plane
    anything on this deck can stand on.

    Two lines leave the lid on this flank: water-5 falls the deck's whole height on `water-in`'s
    bore and fluid-25 climbs out of `reservoir-b`'s. The conduits stand a millimetre apart in X,
    so the two bores are one column, and what a body holds off is the westerly of them with a
    tube's half-section and the pack's own floor over it."""
    bores = [foam_shell_port(c)[0][0] for c in ("water-in", "reservoir-b")]
    return max(bores) + 6.35 / 2.0 + LINE_HUG


def stem_standoff():
    """How far east of the conduits' column Y-H's STEM stands — the corner between reservoir
    B's climb out of the lid and the run east into the stem.

    The conduit opens +Z on the lid and the stem faces −X on the pair's port plane, so the two
    mouths are square to each other and the leg between them is one corner with a rise and a
    reach for legs. The rise is the port plane's own height over the lid, and the reach is
    struck equal to it: the corner sits square in section and neither leg binds before the
    other."""
    return aft_port_z() - foam_shell_port("reservoir-b")[0][2]


def vk_tray_pos():
    """V-K's plate's own origin in world — the stand's middle row, one `AFT_TRAY_BAY` behind the
    bag-B pair, on the west face all three rows share.

    Its outlet faces the SeaFlo's suction barb and its inlet the fall out of the fittings loft,
    and BOTH OF THOSE STAND WEST OF IT — the pump in the lane beside the stand, the split at the
    far end of the machine — so the plate packs west onto the casting's own flank (`aft_tray_x`)
    like every row of this stand, and the one-seat plate's reach to that face is its own
    half-length. The pump's front face is read off its outlet's plane (`seaflo_front_y`)."""
    _bx, _y, z = bag_b_tray_pos()
    return (aft_tray_x() + _tray1.half_x, vk_tray_y(), z)


def nozzle_b_tray_pos():
    """The nozzle-B gate's plate's own origin in world — the middle row's WEST column, back at
    the panel its outlet feeds.

    It packs west onto the SeaFlo's own flank like every row of this stand (`aft_tray_x`), and
    the one-seat plate's reach to that face is its own half-length. Y is `nozzle_b_tray_y`."""
    _bx, _y, z = bag_b_tray_pos()
    return (aft_tray_x() + _tray1.half_x, nozzle_b_tray_y(), z)


def nozzle_b_tray_y():
    """The nozzle-B gate's plate's origin in Y — its OUTLET one come-about forward of the band
    that carries it, which stands the plate as far aft as the machine has room for.

    The outlet faces aft at `bulkhead-flavor-b`, and the FIRST thing the run does is turn: aft
    off the collet onto the AFT OUTLET LANE, the one band all three of the stand's aft-facing
    outlets turn on, a `PUMP_ROW_TURN` off `REAR_PLANE_Y`. That turn is this plate's ONLY
    fence. Its own corridor — the plate's X band, at the plate's own storey — carries no body
    at all between the collet and the cap's aft edge, so nothing behind the plate stops it and
    the come-about is what places it: one stock arc's tangent and the `JUNCTION_LEG_LEAD` the
    collet takes, with the plate's own `port_half` standing its origin ahead of the collet.

    Aft of here the leg between the collet and the lane is shorter than the arc it seats, and
    the run's first corner comes off stock.

    Restated on the pack's side rather than read back from `_lines`, for `LLDPE_BEND`'s own
    reason — a pose that read the routing module would be a cycle in the build order."""
    lane = REAR_PLANE_Y - PUMP_ROW_TURN
    return lane - LLDPE_STOCK_BEND - JUNCTION_LEG_LEAD - _tray1.port_half


def nozzle_gate_in_x():
    """V-G's INLET COLUMN — the westmost X at which `fluid-17`'s closing corner is still bound
    by its own FALL and not by the straight it closes on.

    The gate's inlet faces west down the front column's lane, and that lane cannot run at this
    plate's port plane: the cap conduit's column stands in it (`water-in`, a `LINE_PITCH`
    wide) and Y-H's west flank stands east of that, and the two fences cross. So the feed
    crosses OVER Y-H's crown instead and takes its fall in this plate's own bay — and the two
    corners that fall share the fall's whole length, each turning on half.

    That halves is the figure this column is struck from. West of here the closing straight is
    shorter than the fall leaves those corners and it becomes the binder; east of here the
    straight is slack the corners cannot use, and every millimetre of it comes off the lead
    `fluid-18` turns its own first corner on. So the column stands exactly where the two stop
    trading: the conduit's lane, plus half the fall.

    Restated on the pack's side rather than read back from `_lines`, for `LLDPE_BEND`'s own
    reason — a pose that read the routing module would be a cycle in the build order."""
    lane = foam_shell_port("water-in")[0][0] + LINE_PITCH
    fall = _ydiv.HALF_W + LINE_HUG + TUBE_HALF      # Y-H's crown over the port plane, at the hug
    return lane + fall / 2.0


def nozzle_tray_pos():
    """The nozzle-A gate's own origin in world — turned, in the WEST LANE'S AFT END, forward of
    the pump's face and on the port plane the whole loft shares.

    It carries no junction of its own and it joins no row: V-G-I is fed by Y-D, a storey and a
    half down in the front column, and V-G-O runs alone to its bulkhead. So the plate is placed
    by the two runs and by nothing else — its X by the inlet's column (`nozzle_gate_in_x`), its
    Y by the band the lane leaves it (`nozzle_tray_y`), and its Z by the loft's own plane.

    The inlet collet stands on the plate's own WEST face, so the column and the face are one
    figure and the plate reaches east from it by its own half-length."""
    _bx, _y, z = bag_b_tray_pos()
    return (nozzle_gate_in_x() + _tray.port_half, nozzle_tray_y(), z)


# The bag-B pair reads like bag A in its clocking — the bag's two ends are V-H's INLET and
# V-I's OUTLET, so those two face FORWARD at Y-H and V-H-O and V-I-I face AFT into the bay —
# but its two valves are seated the other way ROUND on the tray, and that is what makes the
# bay work. V-I-I takes the WEST seat, which is the seat V-J-I takes on the tray facing it
# (`NOZZLE_TRAY_COLLETS`), so the two collets Y-G feeds sit on ONE COLUMN with the bay between
# them — and a tee's run is exactly that: one straight length of tube passing through the
# fitting. Read the other way round, the column pairs a fill with a nozzle gate off the other
# channel and no junction can stand between them.
BAG_B_TRAY_COLLETS = {
    "V-I-I": "xn-yp", "V-I-O": "xn-yn",
    "V-H-I": "xp-yn", "V-H-O": "xp-yp",
}
# The nozzle-A gate carries V-G ALONE, so it is the family's one-seat plate and not a two-seat
# plate with a seat left empty — an unfilled seat is not a smaller tray, it is a valve that is
# not in the machine standing in every elevation and absent from the BOM (`single_valve_tray`).
#   Its seats are declared in the PART'S OWN FRAME and `NOZZLE_TRAY_YAW` carries them: turned,
# the inlet opens WEST down the lane that feeds it and the outlet EAST toward its bulkhead's
# column, so the plate's two faces answer the two runs and neither owes a corner to reach the
# one it wants. Its west seat is bare.
NOZZLE_TRAY_COLLETS = {
    "V-G-I": "xc-yn", "V-G-O": "xc-yp",
}
# V-K, the tap-water fill valve, ALONE on the one-seat plate. Its outlet and the SeaFlo's
# suction barb share the plane `vk_tray_y` opens on and `water-4` is the crossing between them;
# its inlet faces forward at the fall `water-3` makes out of the fittings loft.
VK_TRAY_COLLETS = {
    "V-K-I": "xc-yn", "V-K-O": "xc-yp",
}
# The nozzle-B gate, V-J, alone on its own one-seat plate — the twin of the nozzle-A gate's,
# and clocked the same way its runs are: the inlet faces FORWARD at the bay Y-G stands in, the
# outlet AFT at the panel field its bulkhead is in.
#   Both flavor gates stand EAST of both flavor bulkheads: V-J gates nozzle B at
# `bulkhead-flavor-b`, V-G gates nozzle A at `bulkhead-flavor-a`, and all four panel stations
# stand west of the gate that feeds them. `fluid-18` and `fluid-28` each cross the aft-east
# field the electronics block stands in.
NOZZLE_B_TRAY_COLLETS = {
    "V-J-I": "xc-yn", "V-J-O": "xc-yp",
}


def bag_b_tray_port(name):
    return _tray_port("bag-b-tray-assembly", name, BAG_B_TRAY_COLLETS)


def nozzle_tray_port(name):
    return _tray_port("nozzle-tray-assembly", name, NOZZLE_TRAY_COLLETS, _tray1)


def vk_tray_port(name):
    return _tray_port("vk-tray-assembly", name, VK_TRAY_COLLETS, _tray1)


def nozzle_b_tray_port(name):
    return _tray_port("nozzle-b-tray-assembly", name, NOZZLE_B_TRAY_COLLETS, _tray1)


def y_h_pos():
    """Y-H's body centre in world — `_divider_pos`'s relation, read across the machine because
    the pair it joins is turned. Ahead of the bag-B pair's two WEST collets, V-I's outlet where
    the pump returns to the bag and V-H's inlet where the bag draws; reservoir B is on its
    STEM, so one line reaches the cold core's face and the fill and the draw share it.

    It stands on the FLANK WEST OF THE PAIR, the face those two collets open on once the plate
    is turned (`BAG_B_TRAY_YAW`), one `divider_reach()` off them and a body half-length past
    its own outlet faces. The trident takes the pair's own quarter turn with it
    (`DIVIDER_H_TURNS`), which is what puts its outlets back on the axis of the collets they
    feed. X is the axis the reach lies on here; Y is the midpoint of the two collets it joins;
    Z is their own port plane, so the junction lies in one plane with the two valves and
    neither leg climbs.

    The flank it stands in is the width `bag_b_tray_pos` cuts for it: the two cap conduits'
    column on one side and the plate's west face on the other, with the stem's own corner
    between the conduit and the collet."""
    fore, aft = bag_b_tray_port("V-H-I")[0], bag_b_tray_port("V-I-O")[0]
    return (packed().box("bag-b-tray-assembly").xmin - divider_reach() - DIVIDER_HALF,
            (fore[1] + aft[1]) / 2.0,
            fore[2])


# V-I sits on the WEST seat here where V-F sits on the EAST one at bag A, so the two outlets
# are numbered the other way round from Y-E's: the geometry is the same trident, and which
# outlet reaches which valve is the seating's business.
_Y_H_LOCAL = _divider_local("Y-H-2", west="Y-H-1", east="Y-H-3")   # Y-H-1 takes V-I, Y-H-3 feeds V-H


def y_h_port(name):
    return _divider_port("divider-y-h", name, _Y_H_LOCAL)


# --- The AFT STAND'S PUMP ROW: channel B's two tees --------------------------
# Y-F is channel B's SUCTION junction — the shared source and the bag draw meeting at pump A's
# inlet — and Y-G its DISCHARGE junction, splitting that pump's outlet between the bag and the
# nozzle. Both of channel B's pumps' barbs are a storey and a half below, in the FRONT COLUMN
# beside channel A's, so each of these two junctions carries one leg that leaves the loft.
#
#   Y-G is a TRIDENT and not a tee, and it stands IN THE BAY on its own native axis: stem UP
# at the pump's discharge, both outlets facing DOWN on the column V-I-I and V-J-I share, their
# offsets laid across the machine so each leg leans `DIVIDER_OUTLET_X` onto that column. In
# that pose the fitting costs the bay its own section rather than its length.
#   The bay carries no second fitting. It is two `JUNCTION_LEG_LEAD`s deep and the four collets
# facing across it spend the whole of that depth on their own leads, so a body 40.14 mm along
# its run and 20.07 mm out its branch stands in the LOFT'S PUMP LANE instead — the strip
# between the trays' east face and the SeaFlo's west flank, which runs the stand's whole depth
# with nothing in it. Y-F takes that lane on the front column's own construction (`TEE_ROLL`):
# RUN along the lane, BRANCH UP. The branch takes the shared source's climb out of the front
# column, the run's aft collet takes the bag draw coming about in the bay, and the run's fore
# collet sends fluid-21 forward down the machine to the pump's inlet — the leg that leaves the
# loft, and it leaves on the level and falls.
AFT_ROW_TEES = ("tee-y-f",)


# How far west of the box's own rim the lane's column stands. Two bodies bound that column and
# a box describes neither: the bag pair's east face on one side, and on the other the tube that
# falls on V-K's column, which passes this fitting where the fitting is narrower than its box.
# Standing the column on the box half-width alone leaves the tray a gap wider than the floor
# needs and hands the tube the whole shortfall — it stood ON the fitting, touching. This is half
# the room the box overstates, so the two gaps come out equal and neither sits at the floor.
# `_lines.clearances()` is what reports them.
AFT_LANE_SHARE = 1.6975


def aft_lane_x():
    """The column Y-F stands on — V-H'S OWN, the east seat of the bag pair whose draw arrives at
    this tee's aft collet.

    A fitting 2 × `TEE_HALF_W` across does not stand beside this plate at the port plane — the
    lane it sits in is the plate's own width. What is open is the band OVER it, so the tee
    stands over the very collet it serves and the draw is a straight fall down one column
    instead of a come-about across a corridor.
    Read off the collet rather than off the plate's seat pitch: the pair is turned
    (`BAG_B_TRAY_YAW`) and the pitch it is seated on lies in Y now."""
    return bag_b_tray_port("V-H-O")[0][0]


def aft_port_z():
    """The plane every one of the aft stand's ten collets presents on — the tray's own port
    height off its seat. Y-F's run lies on it, so neither of that run's two legs climbs.

    Off the stand's own seat rather than off a placed plate: `port_row_z()` reads this before
    the stand is in the pack, and the seat is the cap."""
    return aft_tray_z() + _tray.port_z


def aft_row_tee_pos(tee):
    """An aft-stand tee's body centre in world.

    Y-F's run lies along V-H's own column (`aft_lane_x`), in the band OVER the stand's crown —
    the tee clears the plate below it by one `LINE_HUG` on its own run radius. IT STANDS OVER
    THE COLLET IT SERVES in both plan axes, V-H-O's own station: the draw's climb is then a
    lane beside this body rather than a reach across the deck, and the band aft of the port
    the climb turns in is the bay's mouth, clear of the crossings the bay itself carries."""
    return (aft_lane_x(), bag_b_tray_port("V-H-O")[0][1],
            aft_stand_crown() + LINE_HUG + TEE_HALF_W)


# Y-F: the run lies along the lane with the bag draw arriving at its aft collet and the pump's
# suction leaving the fore one, and the branch stands UP under the shared source's crossing.
_Y_F_LOCAL = _tee_local(zp="Y-F-3", zn="Y-F-2", branch="Y-F-1")
# Y-G: the stem is the climb to the pump's high barb, and the two outlets fall between the bag's
# fill valve and the nozzle gate — the EAST outlet over the bag pair, whose plate takes the deck
# east of the flank Y-H stands in, and the WEST over the nozzle pair packed on the SeaFlo's own
# flank. Which outlet reaches which valve is the seating's, the same way Y-H's two are numbered
# the other way round from Y-E's.
_Y_G_LOCAL = _divider_local("Y-G-1", west="Y-G-3", east="Y-G-2")


def y_f_port(name):
    return _tee_port("tee-y-f", name, _Y_F_LOCAL)


def y_g_pos():
    """Y-G's body centre in world — in the STRIP BETWEEN THE LANES, east of the bag-B pair and
    forward of the pump, on the stand's own port plane.

    IT STANDS IN THE STRIP THE TWO LANES' FACING ROWS LEAVE. V-I-I opens EAST off the west
    pair's turned east face and V-J-I opens −Y off the east row's forward face, so the strip
    between those two plates is the one band both collets look into, and `vk_tray_y` cuts it
    to this fitting's own section with a `LINE_HUG` at each plate.
    IN X IT STANDS ON V-I-I'S OWN COLUMN — one of the two collets it feeds, and the one whose
    leg opens along the strip rather than across it. A junction standing on a port it joins is
    a leg with no plan to cross: `fluid-23` leaves that collet and climbs, and the whole of the
    crossing between the two collets goes to V-J-I's leg, which opens ALONG the bay and has the
    bay's own lead to turn it in. Read off the collet, so a re-clocked or re-stood bag-B pair
    carries the trident with it.
    In Z it keeps the climb its stem makes to the pump's barb."""
    return (bag_b_tray_port("V-I-I")[0][0],
            packed().box("bag-b-tray-assembly").ymax + LINE_HUG + _ydiv.HALF_W,
            aft_port_z() + Y_G_CLIMB + DIVIDER_HALF)


def y_g_port(name):
    return _divider_port("divider-y-g", name, _Y_G_LOCAL)


def _port_frame():
    """The shared port-band geometry: (x_lo, x_hi, y_wall) — the pack's inner
    walls the panel bodies seat against."""
    placed = build()
    bbs = [_boxes.boxed(s) for s, _c in placed.values()]
    x_lo = min(b.xmin for b in bbs)                # -X inner wall
    x_hi = max(b.xmax for b in bbs)                # +X inner wall
    # The back wall is `REAR_PLANE_Y`, the stated plane the box is built to, and the panel
    # bodies seat against the wall. Read from the plane rather than re-derived off the
    # rearmost body: a body that moves would carry these fittings with it while the wall
    # they penetrate stayed where the box put it.
    return x_lo, x_hi, REAR_PLANE_Y


def front_wall_y():
    """The front wall's INNER face — the pack's frontmost point stood off by
    FRONT_STANDOFF, the same rule enclosure.py sizes the box by."""
    placed = build()
    return min(_boxes.boxed(s).ymin for s, _c in placed.values()) - FRONT_STANDOFF


# --- Panel ports -----------------------------------------------------------
# Every external connection penetrates the REAR wall, in the band OVER the water deck.
# The deck fills this wall's whole width below that band — the pump stands against it for
# the pump's whole length, the chain and the basin take what is west of it — and the band
# itself runs clear wall to wall. So the field is ONE ROW, on one centreline, spread; the
# bodies hang in that column and the risers climb to them.
#   Its floor is the BACK Z-SEAM's lip band. A hole cut inside that band is cut in two
# pieces and clamped across a joint; `_panel_bodies` measures the seam the box actually
# got and refuses a field inside it.
#   Each fitting declares what it needs of a panel: the hole its barrel passes, and the room
# its nut or bezel clamps with. What this file adds is the SLIP — how much air a printed hole
# leaves around a moulded body.
PORT_HOLE_SLIP = 0.86        # a printed hole to the barrel it passes, on the diameter
PORT_BULKHEAD_D = _jg.panel_hole_d(PORT_HOLE_SLIP)      # JG 1/4" bulkhead panel hole
# The C14's cutout is calipered AS A HOLE, so it takes no slip: the figure already is the
# air the part wants, corner radius and all.
PORT_C14_W, PORT_C14_H, PORT_C14_R = _iec.panel_cutout()
# The panel-clamping NUT / flange footprints are far wider than the through-holes, so the
# row is spaced to the NUTS (not the holes) or the real hardware fouls.
PORT_NUT_D, _ = _jg.panel_footprint()               # JG bulkhead nut, across the panel face
PORT_C14_FLANGE_W, PORT_C14_FLANGE_H = _iec.panel_footprint()      # and the C14's bezel
PORT_NUT_GAP = 7.0           # clear gap between adjacent bulkhead nuts (the margin)
# The row's own height, shared by every station: one centreline, because a row this wide
# has no reason to stagger and a stagger would cost it the clearance overhead. What that
# height IS, is `port_row_z()` — the tap-water stack read from the bottom.
# Rear-wall stations, WEST TO EAST, and the wall splits by KIND: all four fluid bulkheads
# in the −X cluster, the mains inlet alone at the +X end, and a band of blank wall between
# them. A joint that can weep and a live receptacle do not share a stretch of panel — and
# the split falls the way the machine already leans, because everything the fluid four
# connect to is west (the ASSE chain on the tap-water column, the nozzle plate the umbilical's
# three come off) and the supply the mains feeds is what follows the C14 east.
#   The tap-water bulkhead takes the −X end, on the ASSE chain's own inlet column, so that
# pigtail turns a single corner and climbs. Then the umbilical's three at the nut pitch,
# with carb-water between the two flavors so the blue-ringed hole is the middle one and
# neither flavor can be mistaken for it.
#   Neither end is a picked number. Both are struck off the same stated inset the interior's
# own walls are: the west cluster stands `PORT_ROW_MARGIN` in from `-SIDE_RIB_INSET`, and the
# C14's flange the same margin in from the core's east face plus that inset. The blank band
# between them is what is left, and it is reported rather than set.
PORT_ROW_MARGIN = 6.0        # nut or flange edge to the wall's own corner furniture
UMBILICAL_PITCH = PORT_NUT_D + PORT_NUT_GAP
# The tap-water station is the one on this wall that carries a BODY as well as a nut. The ASSE
# chain hangs on it, in line with it, and the chain's barrel is far wider than the bulkhead nut
# whose edge the margin above measures — so what this column has to clear is not the wall's
# corner furniture but the ±X boss-chain band, which ends on `CORE_WEST_FACE`. The nut's own
# floor stays in the reading: whichever of the two binds is the answer, so the station cannot
# drift inside either the wall's furniture or the seam's.
WATER_BACK_X = max(-SIDE_RIB_INSET + PORT_ROW_MARGIN + PORT_NUT_D / 2.0,
                   CORE_WEST_FACE + _asse_axis_west() + LINE_HUG)
# The umbilical's three, clustered at that pitch east of the water station — the whole west
# cluster one chain of gaps rather than four picked columns.
UMBILICAL_X = WATER_BACK_X + 2.0 * UMBILICAL_PITCH
# The mains inlet at the far +X end, its flange the widest thing on this wall — so it is the
# station the ±X boss-chain band binds, the way the ASSE chain's barrel binds the tap-water one
# at the other flank. The bezel bears on the wall's INNER face for its whole width, so what it
# has to stand clear of is not the wall's corner furniture but the band's own posts and pods:
# the flange's east edge holds one `LINE_HUG` inside `CORE_EAST_FACE`. The corner-furniture
# floor stays in the reading and whichever binds is the answer, so the station cannot drift
# into either.
C14_BACK_X = min(CORE_EAST_FACE + SIDE_RIB_INSET
                 - PORT_ROW_MARGIN - PORT_C14_FLANGE_W / 2.0,
                 CORE_EAST_FACE - LINE_HUG - PORT_C14_FLANGE_W / 2.0)


def c14_inboard_y():
    """How far the mains inlet reaches INTO the bay, in world Y.

    The receptacle is fastened from inside and its own frame is drawn about the plane its
    bezel bears on, which `_panel_bodies` seats on `REAR_PLANE_Y` — so the housing and its
    spade terminals hang off that plane by whatever the part itself is, and this reads the
    part rather than restating it. It is the aft bound for anything standing high on the +X
    flank: the brick below it clears the receptacle entirely, the board over the brick does
    not."""
    return REAR_PLANE_Y + _boxes.boxed(_load(IEC_C14)).ymin


def port_row_split():
    """The blank band between the fluid cluster and the mains inlet: `(west_edge, east_edge)`.

    Reported, not set — it is what the two ends leave. A wall that splits by kind is only
    split while this is positive, and `back_wall_ports` raises when it is not."""
    return (UMBILICAL_X + UMBILICAL_PITCH + PORT_NUT_D / 2.0,
            C14_BACK_X - PORT_C14_FLANGE_W / 2.0)


# The AC hub LIES FLAT in the aft-east deck band with the relay under it, its length running
# fore-and-aft down that band and its wells opening UP — which is the pose a tray of three
# lever nuts wants, and the pose that lets the relay take the same footprint below it. The
# mains distribution block is then beside the one live receptacle it distributes, with the
# fluid cluster's whole width of wall between it and any joint that can weep, and nothing wet
# over it at all.
#   Its aft face stands one `REAR_STANDOFF` off the wall's inner plane — the Z-seam lip's own
# ring, which every wall holds open — so the pair stands in the bay rather than in the ring and
# the seam keeps every height it had. Nothing fastens either: the hub is a tray, and the joint
# that will hold it is a printed one in whatever body ends up carrying it.


# The order back_wall_ports() returns its holes in, and so the order panel_bodies()
# seats the through-wall bodies in.
BACK_PORT_ORDER = ("bulkhead-water", "bulkhead-flavor-b", "bulkhead-carb",
                   "bulkhead-flavor-a", "c14-inlet")


def back_port_station(name):
    """Where a rear-panel body sits on the wall: (x, z), by the name it is seated
    under. The one reading of a station — the hole, the body and the port share it."""
    holes = {n: h for n, h in zip(BACK_PORT_ORDER, back_wall_ports())}
    return holes[name][1], holes[name][2]


def back_wall_ports():
    """Through-holes the rear panel needs: (kind, x, z, *size) in world
    coords — 'round' (a diameter) or 'rect' (x, z size). enclosure.py cuts
    these through the back pieces' +Y wall. One row, on `port_row_z()`."""
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
        # flavor bulkheads, so the accented (blue-ringed) hole is the middle one and neither
        # flavor can be mistaken for it. Neither flavor hole carries a ring, so which one is A
        # is free: B takes the west station and A the east, the order their runs arrive in.
        ("round", WATER_BACK_X,    z, d),
        ("round", UMBILICAL_X - p, z, d),   # flavor B
        ("round", UMBILICAL_X,     z, d),   # carb-water
        ("round", UMBILICAL_X + p, z, d),   # flavor A
        # And the mains inlet alone at the east end, a band of blank wall off the last nut.
        ("rect",  C14_BACK_X,      z, PORT_C14_W, PORT_C14_H, PORT_C14_R),
    ]


def c14_screw_stations():
    """The C14's two screw stations on the rear panel, in world `(x, z)`.

    The receptacle's own module owns the pattern — both on its cutout's Z centreline, one
    either side of the hole — and the station the panel gives the body places them. The
    wall bores its heat-sets on these, so the hole, the body and its two screws share one
    reading."""
    cx, cz = back_port_station("c14-inlet")
    return tuple((cx + sx, cz + sz) for sx, sz in _iec.panel_screws())


def port_footprint(hole):
    """(width, height) the clamping hardware of one back_wall_ports() hole
    occupies on the panel FACE — a bulkhead nut, or a receptacle's flange. Far
    wider than the through-hole, and it is what crowds the neighbours, the walls
    and the ceiling, so anything sizing a wall to the port field measures this."""
    if hole[0] == "rect":
        return PORT_C14_FLANGE_W, PORT_C14_FLANGE_H
    return PORT_NUT_D, PORT_NUT_D


def front_wall_ports():
    """Through-holes the front panel needs: (kind, x, z, *size), same shapes
    as back_wall_ports. enclosure.py cuts these through the front pieces' −Y wall.
    None: the display facet spans the front-top and the refrigeration stratum stands
    against the front-bottom, so the front wall carries no connection. The CO2 chain
    enters the EAST wall (`east_wall_ports`), into the machine corridor."""
    return []


def east_wall_ports():
    """Through-holes the +X side wall needs: (kind, y, z, *size), the shapes of
    back_wall_ports read on the wall's own plane. enclosure.py cuts these through the
    front pieces' +X wall. One: the CO2 inlet — the DERPIPE's NPT shank crosses here,
    low in the machine corridor, and the whole chain hangs inboard off it. The hole
    sits in the front-bottom piece, forward of the Y seam and below the front Z-seam
    band, so it is cut in one piece and clamped on unbroken wall."""
    return [("round", CO2_INLET_Y, CO2_INLET_Z, CO2_HOLE_D)]


def east_wall_x():
    """The +X side wall's INNER face — the cold core's east face plus the boss chain
    the ±X walls stand off it, the same rule enclosure.py sizes the box by."""
    return packed().box("foam-assembly").xlen + SIDE_RIB_INSET


_PANEL: dict | None = None


def panel_bodies():
    """The connector bodies seated through the enclosure walls — four JG bulkhead unions
    and the C14 receptacle on the rear panel (the faucet umbilical, the tap-water inlet,
    the mains inlet). Their outboard ends stand proud of the wall, and enclosure.py sizes
    the box from build()'s bbox — so they place here and enclosure_assembly.py adds them
    to the rendered assembly.

    Memoized like build(): the port frame, `_lines._frames()` and the scorecard each ask
    for these, and every one would otherwise reload the same fitting STEPs."""
    global _PANEL
    if _PANEL is None:
        _PANEL = _panel_bodies()
    return _PANEL


def _panel_bodies():
    import enclosure                       # imports this module: deferred to call time

    _x_lo, _x_hi, y_wall = _port_frame()
    y_out = y_wall + WALL                              # rear-panel outer face
    # The row stands clear of the back column's Z-seam lip band, so every hole is cut in
    # one piece and every nut clamps onto unbroken wall. The seam is a consequence of the
    # pack, not a constant, so this is measured against the box that was actually built.
    lip_top = enclosure._dims().splits[1] + enclosure.lip_len
    floor = min(h[2] - port_footprint(h)[1] / 2.0 for h in back_wall_ports())
    if floor < lip_top:
        _short("port-row-lip",
               f"the rear port row's lowest clamping edge is z={floor:.2f}, inside the back "
               f"Z-seam lip band that tops out at {lip_top:.2f} — a hole cut there straddles "
               f"the joint. Raise `port_row_z()` by {lip_top - floor:.2f}, or take that much "
               f"height back off the water deck.")

    jg = _load(JG_BULKHEAD)                            # +Y outward, origin on the panel face
    names = list(BACK_PORT_ORDER)
    bodies = {}
    for hole in back_wall_ports():
        kind, hx, hz = hole[0], hole[1], hole[2]
        if kind == "rect":
            # The C14 is fastened from inside — its flange bears on the panel's INNER face,
            # which is the plane its own frame is drawn about, and only its shroud reaches
            # out through the cutout.
            bodies[names.pop(0)] = _load(IEC_C14).translate((hx, y_wall, hz))
        else:
            bodies[names.pop(0)] = jg.translate((hx, y_out, hz))

    # DERPIPE CO2 inlet on the east side wall: 5/16" PTC collet outboard, wrench hex, NPT
    # stub through the hole reaching inboard, pointing west into the machine corridor at
    # the GASHER → WR1110 chain, on the seat its own stub tip takes on that check's socket.
    bodies["co2-inlet"] = co2_inlet_seat().solid(_load(DERPIPE_STEP))
    # What the wall owes it: the push-in cartridge and the wrench flats stand OUTSIDE, with
    # air behind them. The wall is derived from the pack.
    x_east_out = east_wall_x() + WALL                  # east-panel outer face
    _collet_face = co2_inlet_port("collet")[0][0]
    _clear = _collet_face - _derpipe.PROUD_LENGTH - x_east_out
    if _clear < DERPIPE_WRENCH_CLEAR - CO2_MADE_UP_TOL:
        _short("co2-wrench-clear",
               f"the DERPIPE's wrench hex ends {_clear:.2f} mm outside the east wall's face at "
               f"x={x_east_out:.2f}, under the {DERPIPE_WRENCH_CLEAR:g} mm a socket needs to get "
               f"on it — the box has grown out to the fitting. Move `CO2_GASHER_X` "
               f"{DERPIPE_WRENCH_CLEAR - CO2_MADE_UP_TOL - _clear:.2f} outboard, or take that "
               f"much depth off the pack.")
    return {n: (s, COLORS[n]) for n, s in bodies.items()}


# --- The funnel ------------------------------------------------------------

_FUNNEL = None
_FUNNEL_CENTRE = None


def funnel_centre():
    """The funnel collar's centre in plan: (x, y).

    Centred across the box, and pushed as far FORWARD as the display housing
    allows: the top wall resumes at the facet's back plane, keeps one
    `enclosure.hopper_front_ledge` of itself there, and the collar's front edge
    stands one `hopper_funnel.brim_margin` behind that — the brim's own bearing.
    So the basin is the first thing behind the glass and the wall a deeper box
    adds runs behind it, not in front. Read off the box rather than typed, because
    the box is a consequence of the pack and the facet's own depth;
    `enclosure._hopper_hole` asserts the frame this lands in."""
    global _FUNNEL_CENTRE
    if _FUNNEL_CENTRE is None:
        import enclosure                            # imports this module: deferred to call time
        box = enclosure._dims()
        ix0, ix1 = box.inner[0], box.inner[1]
        y_front = (enclosure.facet_back_y(box.outer) + enclosure.hopper_front_ledge
                   + _funnel.brim_margin)
        _FUNNEL_CENTRE = ((ix0 + ix1) / 2.0, y_front + _funnel.collar_d / 2.0)
    return _FUNNEL_CENTRE


def _funnel_column(cx):
    """How far the collar's column and the CORE's stand apart, as a sentence, or "" when they agree.

    `_tray_column_plan` stands the source tray's east seat on `core_plan_centre` and V-B's inlet
    under the funnel's spout, so `_lines`' fluid-4 falls straight down one line. Those two agree
    only while the interior is symmetric about the core — and it is symmetric only while nothing
    in the pack reaches west of the rib inset, because `enclosure._dims` strikes the interior's
    west face off whatever does and its east face off the core plus that same inset. Reported,
    not gated: a machine whose widest body sits west of the core reads a lateral here."""
    core = core_plan_centre()[0]
    if abs(cx - core) <= 1e-6:
        return ""
    who = min(packed().solids, key=lambda n: packed().box(n).xmin)
    west = packed().box(who)
    return (
        f"the funnel's collar centres at x {cx:.3f} and the cold core at {core:.3f} — "
        f"{cx - core:+.3f}. `_tray_column_plan` stands the gravity drain on the core as the "
        f"funnel's column, and fluid-4 falls between them, so that difference IS the drain's "
        f"lateral. The interior is centred on the core only while nothing reaches west of "
        f"-{SIDE_RIB_INSET:g}; `{who}` reaches {west.xmin:.3f}. Move it east, or move the "
        f"funnel onto the core and let the collar sit off the machine's own centreline.")


def placed_funnel():
    """The static funnel (hopper_funnel.py, its own frame: collar-centre origin, z 0 = brim
    underside) seated in the top-wall opening: rotated FUNNEL_ROT about its own Z, then
    translated to `funnel_centre()` with the brim underside on the box's outer top.
    enclosure.py cuts the opening from the same placement, so funnel and hole cannot
    drift apart."""
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
    """The hopper's drain in world: the spout exit annulus centre. The neck stands on the
    funnel's own offset off the collar centre, and the spout tip is the placed body's lowest
    point — so the port rides the part, whatever the basin is sized to or seated on."""
    cx, cy = funnel_centre()
    return (cx + _funnel.neck_dx, cy, _boxes.boxed(placed_funnel()).zmin)


# --- The display -----------------------------------------------------------

def display_harness():
    """The display's harness exit in world: the centre of its interior BACK face.

    The facet is a housing one display-depth thick, so the display's own back face
    lies on the housing's back plane — the 45° facet plane carried one thickness in
    along its normal — at the window's own centre. Read off the facet rather than
    picked, so it rides the housing whatever the box's width or the pack's depth
    turns out to be. The connector is not in the reference STEP; this is the face it
    leaves, not the plug."""
    import enclosure                                # imports this module: deferred to call time

    outer = enclosure._dims().outer
    _a, n, origin, _dy, _dz = enclosure._facet_geom(outer)
    t = enclosure.display_facet_thickness
    return (enclosure.display_centre_x(outer),
            origin[1] - n[1] * t, origin[2] - n[2] * t)
