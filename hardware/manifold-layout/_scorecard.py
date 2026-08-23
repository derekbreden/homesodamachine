"""The enclosure assembly's requirements as a single pass/fail scorecard — the one place the
arrangement's rules are enumerated as executable checks, computed from the placed geometry
the pack already builds. Printed at the tail of every `enclosure_assembly.py` run and written
beside the STEP as `enclosure-assembly.scorecard.json`, which the 3D viewer's bottom bar reads
([`web/contracts/scorecard-sidecar.js`](/web/contracts/scorecard-sidecar.js)).

Two kinds of check:

  - GATE — a requirement that must hold for the machine as it stands to be built.
  - GOAL — a reading the card takes and does not gate on, carried as a `score` (0..100).

FOUR OF THE GATES ARE EXACT QUERIES AGAINST THE SOLIDS, not readings off their boxes, and that
is most of what the run costs. `pack-closes` and `lines-clear` ask what two bodies share,
`clearance-floor` how far apart they stand, and `port-leads` how far a bore cast off a port
gets. A box appears in each only as a prefilter: two boxes that miss are two solids that miss,
and two boxes that overlap say nothing at all.

Every check's detail is printed to `DETAIL_MAX` rows and carried whole in the sidecar, so a
list ending in "… n more" is a terminal cap and never the end of the finding.

Run it through the assembly:
    tools/cad-venv/bin/python hardware/manifold-layout/enclosure_assembly.py

The need figure's own controls, against known-answer geometry:
    tools/cad-venv/bin/python hardware/manifold-layout/_scorecard.py selftest
"""
# The leading underscore is what `_lines.py` has: a private module of this pack, and the name
# `scorecard` on the import path already belongs to the retired enclosure assembly.

from __future__ import annotations

import json
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_repo = _hw.parent
for _p in (_hw / "scripts", _here.parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import _boxes                                          # noqa: E402
from _card import Check, GRADE_BANDS, grade_of, verdict  # noqa: E402
import _clearing                                       # noqa: E402
import _overlap                                        # noqa: E402
import _routing as R                                   # noqa: E402

_TOPOLOGY = _hw / "topology" / "fluid-topology.md"

BEND_GRADE_PASS = "B"       # the worst grade a run may carry and still clear the gate
DETAIL_MAX = 8

# How close two bodies the machine does not seat against each other may stand.
CLEARANCE_FLOOR = 1.0
# Only pairs nearer than this are ranked, so the clearance detail reads as the tight end of the
# pack rather than as every pair in it. Every pair inside it is an exact solid distance.
REPORT_NEAR = 2.0
# The straight a run leaves a fitting on — how far down its own axis a turn off this port reaches.
# The tube begins curving at the collet face, so a quarter turn carries its axis one bend radius
# along the port's own and its outer surface the tube's half-diameter past that. Shallower turns
# stop short of it; a turn past 90° comes back up.
def port_lead(bend: float, diam: float) -> float:
    return bend + diam / 2.0
# How far under its own stated band a MEASURED pose may read and still hold. A strike closes on
# the band it states, so this is float noise across that closing and nothing else.
ROOM_TOL = 1e-6


# The names a length of TUBE goes into the assembly under. `_lines.tubes` names each authored run
# `tube-<connection>`, and `manifold_layout` names the pack's own segments and the placeholder
# stubs off its free mouths the same way. Everything else the assembly carries is a body.
TUBE_PREFIXES = ("tube-", "turn-", "step-", "stub-")


def pack_bodies() -> frozenset:
    """The flavour manifold's own bodies, by the name they go into the assembly under.

    Read off `manifold_layout`'s own assembly rather than retyped, so a body the pack gains
    arrives with it. Its solids are built and cached by the time this is asked, so a second ask
    for the arrangement costs nothing."""
    import manifold_layout as ml
    return frozenset(c.name for c in ml.build_assembly().children
                     if not c.name.startswith(TUBE_PREFIXES))


_placed_cache: dict = {}


def _split_placed(a) -> tuple:
    """The placed world in the three populations the checks read it in: `(bodies, tubes,
    pieces)` — the machine's parts, the tube drawn between them, and the printed box.

    Held against the assembly it was taken from, because `.moved()` hands back a NEW shape every
    time and `_boxes` memoizes a box against the shape's identity: taken fresh per check, every
    body's optimal box would be meshed again for each one."""
    import cadquery as cq

    hit = _placed_cache.get(id(a))
    if hit is not None and hit[0] is a:
        return hit[1]
    bodies, tubes, pieces = {}, {}, {}
    for c in a.children:
        solid = (c.obj.val() if hasattr(c.obj, "val") else c.obj).moved(
            cq.Location(c.loc.wrapped.Transformation()))
        target = (pieces if c.name.startswith("enclosure-")
                  else tubes if c.name.startswith(TUBE_PREFIXES) else bodies)
        target[c.name] = solid
    _placed_cache[id(a)] = (a, (bodies, tubes, pieces))    # pin `a` so its id stays its own
    return bodies, tubes, pieces


# --- what the machine owes -------------------------------------------------
#
# The FLAVOR MANIFOLD's segments are `fluid-1` … `fluid-28` and they live in
# [`fluid-topology.md`](/hardware/topology/fluid-topology.md)'s own tables, read below.
# Everything upstream of the carbonator lives in no segment table — that doc starts at "Tap
# water source", which is the far end of the paths here — so the four below are declared,
# each against the procedure that builds it.

# The sealed loop the whole cold core exists to run, verified by disassembly in
# `reference/ice-maker/README.md` and built in `assembly/refrigerant-loop.md`. The drier and
# the capillary tube ride the condenser → evaporator leg.
#
# THESE THREE IDS ARE THE LOOP'S WHOLE POPULATION, and `enclosure_assembly.REFRIGERANT_IDS` is this
# tuple: the gate that measures the loop and the goal that counts it read one list, so a connection
# cannot go quiet on one while the other still owes it. THERE ARE TWO WAYS TO MAKE A LEG and the
# gate grades both. A leg made by MATING crosses a plane two of its bodies already share, so both
# of its stations are one point read twice and the copper between them is the length of the union;
# a leg made in COPPER is a run `_lines` draws, and what it owes is the gap between the tube's two
# ends and the mouths they are brazed into. `enclosure_assembly.refrigerant_joints` takes whichever
# reading the machine earned over all three at every build, `check_refrigerant_joints` reads red
# for any leg standing open and for any with no pair of placed stations to measure, and
# `load_connections` counts as MATED only the matings that shut — a drawn leg it counts off the
# run, like every other line.
REFRIGERANT_SEGMENTS = (
    ("refrig-1", "compressor discharge", "condenser+fan inlet"),
    ("refrig-2", "condenser+fan outlet (drier + cap tube)", "foam-assembly evaporator inlet"),
    ("refrig-3", "foam-assembly evaporator outlet", "compressor suction"),
)

# The tap water, from the rear-panel bulkhead through the backflow preventer, the split and the
# V-K fill/shutoff to the carbonator's own water inlet — `assembly/internal-plumbing.md` §2. All
# 1/4" LLDPE, stepping back up to 3/8" only at the SeaFlo's two moulded barbs. The ASSE 1022's
# vent is not here: it terminates to atmosphere over the drip pan.
#
# THERE IS NO `water-1`. The rear bulkhead's inboard collet and the ASSE chain's inlet collet
# meet face to face, so the first tube in the machine is a length of stock cut to the two grips
# and swallowed whole by them (`enclosure_assembly.py`, the bulkhead block).
#
# AND THERE IS NO `water-4`, for the same reason. V-K's outlet and the suction chain's collet
# stand on one column and one plane — `enclosure_assembly.build_vk` seats the valve on that
# collet — and the source row's own depth brings the two faces together, so what joins them is
# the tube inside each grip and nothing between.
WATER_SEGMENTS = (
    ("water-2", "asse1022-assembly tube-out", "water-split supply"),
    ("water-3", "water-split to-vk", "vk-solenoid inlet"),
    ("water-5", "discharge-chain tube-port", "foam-assembly water-in"),
    ("water-6", "seaflo-pump discharge (3/8\" barb, moulded)", "discharge-chain barb-tip"),
    ("water-7", "seaflo-pump suction (3/8\" barb, moulded)", "suction-chain barb-tip"),
)

# The gas, from the back-panel ABU44 bulkhead through the GASHER check and the WR1110 secondary
# regulator to the carbonator's bottom-plate CO2 port — `assembly/internal-plumbing.md` §1. Three
# hops of 1/4" LLDPE, each fitting standing apart from its neighbour.
CO2_SEGMENTS = (
    ("co2-0", "co2-inlet inboard", "gasher-co2 inlet"),
    ("co2-1", "gasher-co2 outlet", "wr1110 inlet"),
    ("co2-2", "wr1110 outlet", "foam-assembly co2-in"),
)

# The dispense leg — `P3 --> Faucet` in `fluid-topology-carbonator.mmd`, built in
# `assembly/internal-plumbing.md` §4. The DIGITEN turbine meter is a placed body with a collet
# at each end, so it splits the riser in two rather than being drawn on one run.
CARB_SEGMENTS = (
    ("carb-1", "foam-assembly carb-water-out", "digiten-flow inlet"),
    ("carb-2", "digiten-flow outlet", "bulkhead-carb tube-in"),
)


# --- what fastens each body ------------------------------------------------
#
# One row per body `enclosure_assembly` seats, as `(component, by, joint)`.
#
#   `by`    — the part whose PRINTED FEATURE fastens it. A boss a screw goes into, a socket a
#             thread makes up in. `None` is no printed feature, which reads two ways: one unit
#             of the `mounted` axis's gap, or — where `NEVER` names the row — a body nothing
#             can fasten, which `never_holds` requires to be null. IT IS THE ONLY FASTENING
#             MEASURE: a body
#             resting on a crown is not mounted, because nothing about that survives the
#             machine being picked up by one corner.
#             A TUPLE IS TWO PIECES CLOSING ON ONE BODY, and the fastening is the pair: each
#             piece is screwed to the ones beside it, so a feature printed on one stands over a
#             body sitting in another and neither could be lifted off without the seam coming
#             apart first. `_scenes.holders` reads such a body's unit off `BEARS_ON` — it is in
#             neither piece by the fact of being held by both.
#             WHAT A COLLET CHAIN IS WORTH IS WHERE IT ENDS. A body made up onto one whose own
#             far end is a printed seat is held through that seat; a body made up onto one that
#             ends on nothing is held by nothing, and both read the same from the body itself.
#             So a chain that lands is a `NEVER` row naming what it lands on, and a chain that
#             does not is an open joint under the name of the body it hangs from.
#   `joint` — the CONSTRUCTION, which is a different question from whether it fastens. `bosses`,
#             `well`, `cradle`, `saddle`, `tray`, `channel`, `wall-capture`, `seam-capture`,
#             `plate-capture`, `tube-clamp`,
#             `deck-mount`, `basin`, `gap-press`, `tube-hung`, `pack`. Not an axis and not a score —
#             it is how the machine puts this body down, and it is what lets a card count the
#             bodies bossed to a piece apart from the ones captured in its wall
#             (`assembly/cards/_cards_sync.py`) and a scene tell a pack body from an orphan.
#
# WHERE A BODY IS DRAWN IS NOT WHAT HOLDS IT. Rows for the flavour manifold's own bodies stand
# in this table beside every other, because what fastens a valve is a printed seat under it and
# not the sub-assembly it was arranged in. `derived_mounts` adds a row for each placed body this
# table does not name, so the denominator is the whole machine.
MOUNTS = (
    # THE ONE BODY ON THE FLOOR THE SLAB FASTENS. Four posts stand on the front piece's slab
    # under the four holes in the compressor's own plate, each rising through its grommet's
    # bore to that grommet's crown and bored there for a ruthex M5
    # (`enclosure_assembly.floor_mounts` / `enclosure._floor_bosses`, read by
    # `floor-mounts-land`). The screw's washer bottoms on the post and the rubber carries the
    # can, so the joint is a printed feature under a body and the isolation is the donor's.
    ("compressor", "enclosure-front-bottom", "bosses"),
    # THE OTHER BODY ON THIS FLOOR, held at the four sheet flanges its two recesses leave and
    # nowhere else. The FORE pair slides into a groove off the front wall, one rail at the base
    # and one at the crown, and the base rail's crown is what stands the block off the slab. The
    # AFT pair takes a screw apiece DOWN into a ruthex M3, in a finger reaching west off a fin on
    # the +X wall — the fin roots outside the block's own flanks because the recess it reaches
    # into has the base flange for a floor (`enclosure_assembly.condenser_cradle` /
    # `condenser_mount`, `enclosure._cond_cradle` / `_cond_mount`, read by `cond-mount-lands`).
    # Two screws close the whole joint: the groove takes everything but the pull off them.
    ("condenser+fan", "enclosure-front-bottom", "bosses"),
    # THE HEAVIEST BODY IN THE MACHINE, AND THE ONE WITH NO HOLE IN IT. The core is a foamed cup
    # under a screwed cap, plain skin the whole way round, so what closes on it is the box: a
    # block on the FRONT-BOTTOM's slab bored at each of its front corner rounds
    # (`enclosure._core_stops`), and a bracket off the BACK-TOP's rear wall turning over the aft
    # edge of its cap (`enclosure._core_holds`), read by `core-held`. The blocks take it forward,
    # in X and in yaw; the brackets take it up; the slab under it takes the weight and the back
    # wall the aft. Neither piece holds it alone and both are screwed to the back-bottom it
    # stands in, so the fastening is the three quadrants pinned together.
    ("foam-assembly", ("enclosure-front-bottom", "enclosure-back-top"), "seam-capture"),
    ("seaflo-pump", "foam-assembly", "deck-mount"),
    ("hopper-funnel", None, "wall-capture"),
    # THE BASIN'S DISCONNECT, THREE BODIES ON THE SPOUT'S OWN AXIS. The stub stands inside the
    # silicone under the clamp's band; the clamp closes silicone onto steel; the union takes the
    # stub in its upper collet and starts `fluid-4` at its lower one. The first two are made up
    # at the factory and never come apart; the third is the joint the customer opens.
    ("hopper-drain-stub", None, "tube-clamp"),
    ("hopper-drain-clamp", None, "tube-clamp"),
    ("hopper-drain-union", None, "tube-hung"),
    # THE ONE STEEL PIECE, SUNK IN A PRINTED SEAT. The collet plate's foot stands in the seat
    # `enclosure._bay_floor` cuts down the bay floor's top, one `wall` deep, its two bottom
    # corners notched round front-bottom's Z-seam lip — gravity onto the seat's own bottom, the
    # seat's walls fore and aft, the side walls across, and open at the top. What loads it is the
    # cartridge's own release: the four anchor-tee collets press its aft face as the cartridge is
    # pulled, the seat's fore wall carries that into a floor lying on the print bed, and the
    # user's aft brace on the box closes the loop. It lifts out through the bay with the
    # cartridge removed.
    ("collet-plate", "enclosure-front-top", "well"),
    # THE DISPLAY IS CAPTURED BETWEEN TWO PRINTED PARTS. Its glass sits in the bezel counterbore
    # of the front-top piece's 45° facet, and the cover plate's border laps that glass on all
    # four sides, drawn down by two DIN 912 M3s into ruthex inserts in the facet's own inset
    # floor (`enclosure._display_cuts`, `printed-parts/enclosure/display-cover/`). Neither part
    # holds it alone: lift the plate off and the display comes out of its hole by hand.
    ("display", ("enclosure-front-top", "display-cover"), "plate-capture"),
    # And the plate itself on those same two screws, which are the whole of what holds it — it
    # drops into the inset on a slip fit and bears on the floor.
    ("display-cover", "enclosure-front-top", "bosses"),
    # The soft ring between the two. It is what the plate closes onto, so the screws reach the
    # glass through it rather than standing over it.
    ("display-gasket", ("display-cover", "display"), "gap-press"),
    # Both chains lie in ribs printed on the cold core's cap lid — the same plate the pump bolts
    # to, so the hose stub at each of its barbs spans no joint
    # (`_cold_core_interface.cap_anchors`, read by `chains-seated`).
    ("suction-chain", "foam-assembly", "cradle"),
    ("discharge-chain", "foam-assembly", "cradle"),
    ("psu", "enclosure-back-top", "bosses"),
    ("pcba", "enclosure-back-top", "bosses"),
    ("relay-1", "enclosure-back-top", "bosses"),
    ("relay-2", "enclosure-back-top", "bosses"),
    ("ground-stack", "enclosure-back-top", "bosses"),
    # The lever nuts are the one column that no boss holds: a 221-413 is a free splice with
    # no hole in it, so the wall's own printed well IS the mount and there is nothing to bolt.
    ("wago-h", "enclosure-back-top", "well"),
    ("wago-n", "enclosure-back-top", "well"),
    ("wago-g", "enclosure-back-top", "well"),
    ("wago-v12", "enclosure-back-top", "well"),
    ("wago-gnd", "enclosure-back-top", "well"),
    # The five device-cluster nuts take the same well in whichever wall their own cluster
    # stands against, so the piece that holds each one is the piece that owns its band.
    ("wago-mana", "enclosure-front-top", "well"),
    ("wago-manb", "enclosure-front-top", "well"),
    ("wago-reeds-b", "enclosure-back-top", "well"),
    ("wago-reeds-a", "enclosure-back-top", "well"),
    ("wago-sensors", "enclosure-back-top", "well"),
    # THE TAP-WATER CHAIN LIES IN A TROUGH PRINTED ON THE −X WALL. `enclosure._asse_cradle` cuts
    # a 120° V to each of the chain's own three sections, so the steps between them are faces
    # square to the axis and the brass barrel is trapped between two of them. What the V beds on
    # is that barrel's own two flats, which is the one section on the run whose clock the vent is
    # machined into — so keying it is what holds the drip over the pan. Two zip ties through the
    # trough's lips shut its mouth; nothing about the chain's weight is theirs to carry.
    ("asse1022-assembly", "enclosure-back-top", "cradle"),
    ("drip-pan", "enclosure-back-top", "channel"),
    # The probe plate lies loose in the basin the way the basin rides loose in its rails: what
    # fastens it is the tray's own printed floor and coves, which fence it on four sides at
    # `drip_pan.PLATE_SLIP`. Nothing screws down — a plate bolted flat could not be lifted out
    # to wipe, and the tray is drawn and emptied on service with the plate still in it.
    ("moisture-plate", "drip-pan", "basin"),
    # The gas sensor slides into a slot printed on the −X wall of the bay it watches
    # (`enclosure._west_cradle`) and bottoms on the wall itself. The board carries no mounting
    # hole, so a slot is the only way it is ever held — the same bargain the lever nuts strike,
    # and the same wall-as-datum.
    ("mq6-sensor", "enclosure-front-bottom", "cradle"),
    # The thermal cutoff lies in a channel printed through the clamp's head
    # (`printed-parts/refrigeration/fuse-clamp`), whose crown lands on the case's outboard
    # generatrix — so the case is pinched between that crown and the compressor's power box, and
    # the contact that makes a 77 °C cutoff a cutoff is a printed feature of a placed part. The
    # channel is open at both ends and the cutoff threads out along it, which is the whole of
    # what a one-shot part's service is.
    ("thermal-fuse", "fuse-clamp", "channel"),
    # The clamp itself presses into the COMPRESSOR'S OWN `POWER_GAP`, the air the power box hangs
    # over its mounting plate: two leaves, one on the box's underside and one on the plate's
    # crown. Both faces of that slot belong to the compressor, so the clamp rides the can and no
    # running hour of it is relative motion at the case. That is a real joint and a donor's, not
    # a printed one — the plate's four holes carry the floor's posts and the grommets that
    # isolate the can, so a clamp on one of those screws would be bolted to the cabinet. This
    # axis counts a PRINTED feature, so the row is open on it and the joint is not.
    ("fuse-clamp", None, "gap-press"),
    # THE FLAVOUR TAP'S PAIR, one over the other in two ribs off the −X wall
    # (`enclosure_assembly.BODY_ANCHOR_SITES`, read by `body-seated`). Each seat closes on the run
    # between that fitting's hub and the collet the tap arrives by — the one round section on
    # either body that is not a box, a branch or the adjuster a hand has to reach.
    ("water-split", "enclosure-back-top", "cradle"),
    ("flow-regulator", "enclosure-back-top", "cradle"),
    ("vk-solenoid", "foam-assembly", "cradle"),
    # EVERY FITTING ON THE REAR WALL IS CLAMPED THROUGH IT. The flange lands on the ring in its
    # pad, the barrel passes a bore struck one `PORT_HOLE_SLIP` over it, and the fitting's own nut
    # draws up on the inside — so the printed material is the clamped member and the joint is a
    # thread made up on it. `enclosure_assembly.check_wall_clamped` reads both faces of that off
    # the placed solids, and `port-clamp-stack` holds the barrel against what the stack spends.
    ("bulkhead-water", "enclosure-back-top", "wall-capture"),
    ("c14-inlet", "enclosure-back-top", "bosses"),
    ("co2-inlet", "enclosure-back-top", "wall-capture"),
    # THE CHECK STANDS BETWEEN THE TWO OF THEM, one `CO2_INLET_HOP` inboard of the bulkhead and
    # one `CO2_HOP` short of the regulator, fed and drained by tube. Each hop is a stretch of
    # 1/4" LLDPE in its own pair of collets, off a body the box holds.
    ("gasher-co2", None, "tube-hung"),
    # THE REGULATOR LIES IN A RIB OFF THE TOP WALL. `enclosure._tube_anchors` bores it for the
    # barrel between the two wrench hexes — `enclosure_assembly.BODY_ANCHOR_SITES` — and a strap
    # through the rib's own cavity closes round the barrel and the rib's back together. The seat
    # opens downward, so the strap is the load path and the bore is what it pulls into.
    ("wr1110", "enclosure-back-top", "cradle"),
    ("bulkhead-flavor-a", "enclosure-back-top", "wall-capture"),
    ("bulkhead-flavor-b", "enclosure-back-top", "wall-capture"),
    ("bulkhead-carb", "enclosure-back-top", "wall-capture"),
    # A CHIP LIES IN A POCKET CUT INTO THE BACK WALL'S OUTER FACE. `enclosure._port_field` sinks
    # each one the chip's own thickness and stands the boss that backs it on the inboard face, and
    # the fitting's flange lands on the chip's outboard face — so the chip is fenced by wall on
    # every side its outline has and shut in by a flange whose bore is narrower than it is. What
    # holds it is that pocket: the same bargain the lever nuts strike in their wells, with a placed
    # body's flange over the mouth. The three on the top row are fenced on three sides and open at
    # the ceiling, which `enclosure_assembly.check_top_row` is what reads.
    ("port-ring-water", "enclosure-back-top", "well"),
    ("port-ring-carb", "enclosure-back-top", "well"),
    ("port-ring-co2", "enclosure-back-top", "well"),
    ("port-ring-flavor-a", "enclosure-back-top", "well"),
    ("port-ring-flavor-b", "enclosure-back-top", "well"),
    # AND THE WORD LIES IN A RECESS OF THE CHIP, by the same bargain one step in. A two-colour
    # print is ONE part in two materials: `port_ring.build_ring` cuts the recess and
    # `port_ring.build_word` fills it in the same layers, so nothing joins the pair but the print
    # that lays them both. `RIDES` is what keeps this from counting as a second joint.
    ("port-ring-water-word", "port-ring-water", "well"),
    ("port-ring-carb-word", "port-ring-carb", "well"),
    ("port-ring-co2-word", "port-ring-co2", "well"),
    ("port-ring-flavor-a-word", "port-ring-flavor-a", "well"),
    ("port-ring-flavor-b-word", "port-ring-flavor-b", "well"),
    # AND THE NAMEPLATE LIES IN A POCKET OF THAT SAME WALL, by the same bargain with one
    # difference: nothing places a flange over it, so two M3 cap screws do what a fitting's nut
    # does for a chip. Each lands in a counterbore sunk into the plate's own local thickening and
    # pulls down into a ruthex M3 short, set in a boss the wall stands behind the pocket
    # (`enclosure._nameplate`) — so the head, the plate and the wall come out one plane.
    ("nameplate", "enclosure-back-top", "screw"),
    ("nameplate-ink", "nameplate", "well"),
    # THE METER HANGS IN TWO SADDLES OFF THE TOP WALL. `enclosure._digiten_saddles` puts the
    # same 120° V over each of its two collet barrels — the body reaches to within a hair of that
    # wall and the barrels leave the best part of a centimetre, so the arms are what a printed
    # feature can reach. A strap through each saddle's own cavity closes it, and here the straps
    # are the load path: a V that opens downward carries nothing.
    ("digiten-flow", "enclosure-back-top", "saddle"),
    # THE CAP LID PRINTS A CRADLE UNDER EACH VALVE THAT STANDS ON IT
    # (`_cold_core_interface.cap_cradles`) — four bosses, and the valve's own corner posts press
    # into their sockets. The cap is inside `foam-assembly`, which is the placed body the cradle
    # is a feature of, so that is what fastens them.
    ("valve-v-a", "foam-assembly", "cradle"),
    ("valve-v-b", "foam-assembly", "cradle"),
    # AND THE OTHER EIGHT STAND ON TWO VALVE PANELS — a plate wall to wall on each plane the
    # fold left a deck on, carrying that same four-boss seat per valve. A panel is not a part:
    # it is `enclosure-front-top`'s own material, fused the way the tap-water trough and the
    # meter's saddles are (`enclosure._valve_panels` off
    # `enclosure_assembly.valve_panel_stations`, read by `panels-hold`).
    ("valve-v-c", "enclosure-front-top", "bosses"),
    ("valve-v-d", "enclosure-front-top", "bosses"),
    ("valve-v-g", "enclosure-front-top", "bosses"),
    ("valve-v-j", "enclosure-front-top", "bosses"),
    ("valve-v-e", "enclosure-front-top", "bosses"),
    ("valve-v-f", "enclosure-front-top", "bosses"),
    ("valve-v-h", "enclosure-front-top", "bosses"),
    ("valve-v-i", "enclosure-front-top", "bosses"),
    # AND BOTH PUMPS STAND IN A CASE THAT IS TWO PRINTED PIECES — the pump cartridge and the
    # cap screwed under it, parting on the pump's own bracket plane
    # (`enclosure.cap_split_z`). Above that plane the cartridge is a block the pump stands in,
    # and its tray takes the boss on the octagon bore and the boss's crown on a shoulder of
    # tower; below it the cap closes on the head. What carries the pump is the stamped bracket
    # the part holds in that same plane, `bracket_w` across against a head of `head_w`: it laps
    # the cap's top face all round the head, and two M3×10 on the lane between the pumps draw
    # the cap up onto the block (`enclosure._cap_screws`, read by `trays-hold`). The surfaces
    # that fit the part in `pump-tray/pump_case.py` fit it here, closed on screws. The whole
    # case rides out of the front bay with both pumps aboard.
    ("pump-a-head", "enclosure-pump-cartridge", "case"),
    ("pump-b-head", "enclosure-pump-cartridge", "case"),
)


# A BODY THAT IS PART OF ANOTHER BODY, as `rider -> host`. What holds a rider is whatever holds
# its host: the fastening it answers to is one its host's own hardware makes, shipped with the
# part and closed on the part.
#   These are one purchased thing apiece drawn as several. `manifold_layout.flat_bodies` gives a
# Beduan two solids so the coil takes its own colour, and `build_pump` gives a Kamoer the three
# its STEP carries — head, rear boss and motor can. `hardware/ledger/bom.md` bills one row for
# each of those, and `hardware/reference/beduan-solenoid` fuses body, coil and port into one
# solid. A rider takes its host's row, so a colour never reads as an open joint.
RIDES = {
    **{f"coil-v-{v}": f"valve-v-{v}" for v in "abcdefghij"},
    **{f"pump-{p}-{part}": f"pump-{p}-head"
       for p in ("a", "b") for part in ("boss", "motor")},
    **{f"port-ring-{w}-word": f"port-ring-{w}"
       for w in ("water", "carb", "co2", "flavor-a", "flavor-b")},
    "nameplate-ink": "nameplate",
}


def rides_hold(rows) -> None:
    """Every rider and every host in `RIDES` is a placed body, and no host is itself a rider."""
    have = {name for name, _by, _joint in rows}
    for rider, host in sorted(RIDES.items()):
        for who, what in ((rider, "rider"), (host, "host")):
            if who not in have:
                raise ValueError(
                    f"`RIDES` names {who!r} as the {what} of {rider!r} → {host!r} and no placed "
                    f"body carries that name — the body has been renamed or has left the "
                    f"machine, and this row is what is still holding a place for it.")
        if host in RIDES:
            raise ValueError(
                f"`RIDES` has {rider!r} riding {host!r}, which rides {RIDES[host]!r} — a rider "
                f"takes its host's row, and a chain of them takes no row at all.")


def derived_mounts() -> tuple:
    """One row for every placed body `MOUNTS` does not name.

    `manifold_layout` arranges the flavour manifold's own bodies on the pack's four spine
    hairpins and this module stands that whole pose on the base's crown, so a body no printed
    feature reaches is carried by THE PACK — the hairpins are what the machine sets it down on.

    Read off the placed assembly rather than typed, so a body the machine gains arrives with a
    row instead of waiting for one."""
    typed = {name for name, _by, _joint in MOUNTS}
    return tuple((name, None, "pack") for name in sorted(pack_bodies()) if name not in typed)


def mounts() -> tuple:
    """Every placed body's fastening row — the ones this module types, then the rest."""
    return MOUNTS + derived_mounts()


def fastened_by(name: str):
    """What actually fastens one body: its own row's `by`, or its host's if it rides one."""
    by_name = {n: by for n, by, _joint in mounts()}
    return by_name[RIDES.get(name, name)]


# --- the rows nothing can fasten -------------------------------------------
#
# A name here is a body already fastened — by a clamp that ships with it, onto a donor the
# machine stands on grommets to hold off itself. Its row's `by` is null and `never_holds` keeps
# it null. These rows come out of the axis's denominator, and their text goes out on the card.
NEVER = {
    # THE BASIN AND THE THREE BODIES ON ITS SPOUT'S COLUMN. The basin lifts out of the top wall
    # and goes into the dishwasher with the stub and the clamp still on it. Its brim bears on the
    # top wall's outer face and its collar fills the opening cut for it, and the union's collet
    # grips the stub through the wall — thumb on the collet and the whole basin comes away. The
    # union stays behind on its two collets. A printed feature closing on any of the four would be
    # a feature the customer has to work past every time the basin is washed.
    "hopper-funnel":
        "The brim bears on the top wall's outer face, the collar fills `enclosure._hopper_hole`, "
        "and the elbow's own collet grips the stub the spout carries — so the basin is held down by "
        "the joint it releases from. It is a dishwasher part and comes out by hand.",
    "hopper-drain-stub":
        "The worm clamp closes the basin's silicone spout onto it over the whole of the spout's "
        "land, and the pair is made up at the factory. Nothing printed is in the path: the stub "
        "leaves the machine with the basin every time it is washed.",
    "hopper-drain-clamp":
        "A worm clamp closes on itself — the band draws through its own housing and the housing "
        "rides the band. What it lands on is silicone, and it goes to the dishwasher with it.",
    "hopper-drain-union":
        "Both its collets land on held bodies — the +Z leg takes the stub the basin carries, the "
        "+Y leg hands `fluid-4` aft to V-B in its cradle on the cold core's cap — so the elbow "
        "hangs between two seats with nothing printed closing on it. It is the joint the customer "
        "opens, and a thumb on that collet is the whole of the motion.",
    # THE CHECK IN THE GAS CHAIN, the middle body of three standing on one axis at one height.
    # The bulkhead ahead of it is clamped through the back wall and the regulator behind it lies
    # in a rib off the top one, so both ends of the chain are the box's and the check is the span
    # between them.
    "gasher-co2":
        "Both its hops land on held bodies — `co2-0` back to the ABU44 clamped through the rear "
        "wall, `co2-1` on to the WR1110 strapped into its rib off the top one — and each is ten "
        "millimetres of 1/4\" LLDPE in a pair of collets, so the check is fixed on the chain's "
        "own axis with nothing printed closing on it. A seat under the middle body of three "
        "made-up ones would fight the two either side of it for where the chain stands.",
    "fuse-clamp":
        "Both faces of the slot the clamp presses into are the compressor's own — the air its "
        "power box hangs over its mounting plate — so the clamp rides the can. The plate's "
        "four holes carry the floor's posts and the grommets, and every printed feature in "
        "reach of the clamp stands on the cabinet side of them.",
    # THE SIX Y-TEES, EACH BUTTED ONTO A VALVE IN A PRINTED SEAT. A butt is two collet faces
    # meeting on one stub of tube with no tube between them (`manifold_layout.SEGMENTS`), so a
    # tee and the valve it butts are one made-up body. Every one of these six lands on a valve
    # the two panels hold, which is what makes the chain worth something: `tees_butt_held` reads
    # each row's named partner back off the pack and off this table's own `by`, so a valve that
    # loses its seat takes its tee's exemption with it.
    **{tee: (f"Its collets make up onto {valve.upper()[len('VALVE-'):]}'s, face to face on one "
             f"stub with no tube between them, and that valve stands in four printed sockets — "
             f"so what holds this tee is the seat under the valve it butts. Nothing printed "
             f"reaches the tee itself, and a second seat on a body already made up onto a held "
             f"one would fight it for the joint's own position.")
       for tee, valve in (("tee-y-a", "valve-v-c"), ("tee-y-b", "valve-v-d"),
                          ("tee-y-c", "valve-v-e"), ("tee-y-d", "valve-v-f"),
                          ("tee-y-f", "valve-v-h"), ("tee-y-g", "valve-v-i"))},
}


# Which valve each exempt tee butts, so the exemption is a claim the machine can refuse. A tee's
# reason names a valve; this is that pairing as data, and `tees_butt_held` holds it to two
# things — the pack still draws the butt, and the valve still has a printed seat.
TEE_BUTTS = {"tee-y-a": "valve-v-c", "tee-y-b": "valve-v-d", "tee-y-c": "valve-v-e",
             "tee-y-d": "valve-v-f", "tee-y-f": "valve-v-h", "tee-y-g": "valve-v-i"}


# Every exemption a LENGTH OF TUBE rests on, as `(body, port, run, what the run lands on)` — the
# disconnect's lower end, and both of the gas check's. Each reason names a run and the body it
# reaches the same way a tee's names the valve it butts, and `chains_land` reads all three back
# off the machine. A body hung at both ends states a row per end: what makes it held is that
# NEITHER of them lands on nothing.
CHAIN_LANDS = (
    ("hopper-drain-union", "outlet", "fluid-4", "valve-v-b"),
    ("gasher-co2", "inlet", "co2-0", "co2-inlet"),
    ("gasher-co2", "outlet", "co2-1", "wr1110"),
)


def chains_land(rows, runs) -> None:
    """Every hung body's collet still starts the run it names, and that run still ends on a seat."""
    by_name = {n: by for n, by, _joint in rows}
    for name, port, rid, lands in CHAIN_LANDS:
        run = next((r for r in runs if r.id == rid), None)
        if run is None or f"{name}.{port}" not in (run.frm, run.to):
            raise ValueError(
                f"{name} is held out of the mounted axis because {rid} leaves its {port!r} "
                f"collet, and no run by that name starts there — the chain the exemption rests "
                f"on has been rerouted, so the row is claiming a hold that is not there.")
        if lands not in {end.split(".")[0] for end in (run.frm, run.to)}:
            raise ValueError(
                f"{name} is held out of the mounted axis because {rid} lands on {lands}, and that "
                f"run now ends {run.frm} → {run.to} — a chain is worth where it ends, and this "
                f"one ends somewhere else.")
        if by_name.get(lands) is None:
            raise ValueError(
                f"{name} is held out of the mounted axis because {rid} lands on {lands} in a "
                f"printed seat, and {lands} is now fastened by nothing — so it hangs off a body "
                f"that hangs off nothing, and the row is an open joint again rather than an "
                f"exemption.")


def tees_butt_held(rows) -> None:
    """Every exempt tee butts a valve the pack still draws, and that valve is still fastened."""
    import manifold_layout as ml

    by_name = {name: by for name, by, _joint in rows}
    butts = {(a.rsplit("-", 1)[0], b.rsplit("-", 1)[0])
             for _cid, a, b, how in ml.SEGMENTS if how == "butt"}
    for tee, valve in sorted(TEE_BUTTS.items()):
        pair = (tee[len("tee-"):].upper(), valve[len("valve-"):].upper())
        if pair not in butts and pair[::-1] not in butts:
            raise ValueError(
                f"{tee} is held out of the mounted axis because it butts {valve}, and "
                f"`manifold_layout.SEGMENTS` no longer draws a butt between them — the joint "
                f"the exemption rests on has been rerouted, so the row is claiming a hold that "
                f"is not there.")
        if by_name.get(valve) is None:
            raise ValueError(
                f"{tee} is held out of the mounted axis because {valve} stands in a printed "
                f"seat, and {valve} is now fastened by nothing — a chain is worth where it "
                f"ends, so this tee is an open joint again rather than an exemption.")


def never_holds(rows) -> None:
    """Every name in `NEVER` is a row of the fastening table, unfastened, carrying its reason."""
    by_name = {name: by for name, by, _joint in rows}
    for name, why in NEVER.items():
        if name not in by_name:
            raise ValueError(
                f"`NEVER` holds {name!r} out of the mounted axis and no row of the fastening "
                f"table carries that name — the body has been renamed or has left the machine, "
                f"and this exemption is what is still holding a place for it.")
        if by_name[name] is not None:
            raise ValueError(
                f"{name!r} is fastened by {by_name[name]!r}, and `NEVER` says nothing can "
                f"fasten it. Drop the exemption if the joint is real, or the row's `by` if it "
                f"is not.")
        if not why.strip():
            raise ValueError(
                f"{name!r} is held out of the mounted axis with no reason given, and the card "
                f"prints this text.")


# --- the joints that carry no line -----------------------------------------
#
# Two mouths meeting with nothing between them are still joined, and `port-leads` has to read
# them as joined or it asks each end for a straight it will never turn in.
MADE_UP = (
    # The rear bulkhead's inboard collet and the ASSE chain's inlet collet meet face to face —
    # `enclosure_assembly.build_asse` seats the chain on `bulkhead_mouth_y`, "the inlet collet
    # butts the union's inboard collet". The first tube in the machine is a length of stock cut to
    # the two grips and swallowed whole by them, which is why there is no `water-1`.
    ("bulkhead-water.inboard", "asse1022-assembly.tube-in"),
    # V-K's outlet and the suction chain's collet, which meet the same way —
    # `enclosure_assembly.build_vk` seats the valve ON that collet, and the source row's own depth
    # brings the two faces together. The tube is cut to the two grips and swallowed whole by them,
    # which is why there is no `water-4` either.
    ("vk-solenoid.outlet", "suction-chain.tube-port"),
    # The basin's stub and the elbow's +Z collet. The stub IS the tube in that grip — it runs
    # `hopper_drain_stub.UNION_INSERTION` down inside the fitting — so the collet's lead is
    # filled by the thing it is a grip on.
    ("hopper-drain-stub.spout", "hopper-drain-union.stub"),
    # And the same stub in the basin's own spout, `hopper_drain_stub.FUNNEL_ENGAGEMENT` up the
    # bore under the clamp's band. The basin drains THROUGH the stub, so the drain's lead is the
    # stub's own bore and there is no length of anything else to leave room for.
    ("hopper-funnel.drain", "hopper-drain-stub.funnel"),
    # The spout's exit face and the elbow's +Z collet face, which meet. That contact is what
    # leaves no stub standing in the room between the silicone and the fitting.
    ("hopper-funnel.drain", "hopper-drain-union.stub"),
)

# Ports that open to ATMOSPHERE rather than onto a line. Nothing is ever bent onto one, so a bend
# radius is the wrong thing to ask of it — what the vent owes is that its drip falls on the basin's
# flat floor, and `enclosure_assembly.check_vent_lands` measures where it falls and reports it as
# the `vent-lands` gate row.
TERMINI = ("asse1022-assembly.vent-tip",)


# --- what stands against what ----------------------------------------------
#
# `clearance-floor` holds every body pair a millimetre apart. These are the pairs the machine
# SEATS against each other, each named against the construction that seats it — a contact by
# intent, not a pack closing on itself.
TOUCHING_OK = {frozenset(p) for p in (
    # What stands on the core's cap — `build_seaflo` and `build_psu` both take its crown as `z0`.
    ("foam-assembly", "seaflo-pump"),
    ("foam-assembly", "psu"),
    # THE THREE VALVES IN THE CAP'S OWN CRADLES. A press fit is a contact by construction: the
    # bosses' sockets take the valve's four corner posts on `valve_seat.socket_clearance` and
    # its round boss lands on the boss tops, so the pair reads 0 and it is the joint working.
    # `enclosure_assembly.check_cradles` is what holds each of them over its own cradle.
    ("foam-assembly", "vk-solenoid"),
    ("foam-assembly", "valve-v-a"),
    ("foam-assembly", "valve-v-b"),
    # THE COVER PLATE ON THE INSET IT FILLS. Its underside lies on the inset floor and each of
    # its two pads bottoms in the pocket sunk for it, so the plate reads 0 against the piece on
    # three faces at once — which is the seat, and what puts its own top face in the 45° plane.
    ("enclosure-front-top", "display-cover"),
    # AND THE SOFT RING BETWEEN PLATE AND GLASS. It fills what the lap passes over, so it reads
    # 0 against both of them — which is the whole of why it is there.
    ("display-cover", "display-gasket"),
    ("display", "display-gasket"),
    # The plate and the glass therefore stand one ring apart, which is a seat and not a gap:
    # `display_gasket.thickness` IS this distance, taken off the same two depths.
    ("display-cover", "display"),
    # AND THE EIGHT IN THE TWO VALVE PANELS' — the same seat and the same press, on a plate the
    # front-top piece carries instead of a lid. `enclosure_assembly.check_panels_hold` is what
    # reads each valve against that plate.
    *(("enclosure-front-top", f"valve-v-{v}") for v in "cdefghij"),
    # BOTH MADE-UP CHAINS IN THE RIBS THAT LID STANDS. A bore closed on a section reads its own
    # slip, and that reading IS the seat holding: `enclosure_assembly.check_chains_seated` takes
    # it, and `anchor-lands` holds each rib over the section it is bored for.
    ("foam-assembly", "discharge-chain"),
    ("foam-assembly", "suction-chain"),
    # THE PROBE PLATE LIES ON THE BASIN'S FLOOR, which is the whole of what it does: a plate
    # standing a millimetre off the floor reads only once the pool is a millimetre deep, and the
    # weep this watches for is a drip at a time. `enclosure_assembly.build_moisture_plate` seats
    # its underside on that floor and `drip_pan.check_plate` holds the floor wide enough to take
    # it, so the pair reads 0 and it is the sensor working.
    ("drip-pan", "moisture-plate"),
    # THE CUTOFF LIES ON THE COMPRESSOR'S POWER BOX. A one-shot fuse opens on the temperature of
    # its own case, so a millimetre of air between the case and the cover is a millimetre that
    # puts it on cabinet air instead. `enclosure_assembly.build_thermal_fuse` seats it on its own
    # contact line — the case is round, so the pair reads 0 along one line and stands apart
    # everywhere else.
    ("compressor", "thermal-fuse"),
    # AND THE CLAMP CLOSES THAT CONTACT. Its channel's crown lands on the case's outboard
    # generatrix and its head lies flat on the cover, so it reads 0 against both — the pinch is
    # cover, case, crown, with the case's whole diameter between the two.
    # `enclosure_assembly.check_cutoff_bedded` measures both ends of that stack and is the only
    # row on this card that can see a clamp standing proud of the thing it holds.
    ("compressor", "fuse-clamp"),
    ("thermal-fuse", "fuse-clamp"),
    # A RING IN ITS PAD, UNDER THE FLANGE THAT SHUTS IT IN. Every flange is narrower than the
    # pocket it stands in, so what it lands on is the ring's own face and nothing else.
    # `enclosure_assembly.bulkhead_seat_y` is that plane, and the nut on the far side of the wall
    # draws flange, ring and wall into one stack — so the pair reads 0 and it is the clamp
    # holding.
    ("bulkhead-water", "port-ring-water"),
    ("bulkhead-carb", "port-ring-carb"),
    ("co2-inlet", "port-ring-co2"),
    ("bulkhead-flavor-a", "port-ring-flavor-a"),
    ("bulkhead-flavor-b", "port-ring-flavor-b"),
    # AND THE WORD AGAINST THE CHIP IT IS LETTERED INTO. The recess is cut to the word and the
    # word fills it, so the pair reads 0 across the whole of its back and every flank — which is
    # not two bodies closing on each other but one printed part in two colours.
    *((f"port-ring-{w}", f"port-ring-{w}-word")
      for w in ("water", "carb", "co2", "flavor-a", "flavor-b")),
    # And the nameplate's lettering against the plate it is lettered into, the same print in the
    # same two filaments at another size.
    ("nameplate", "nameplate-ink"),
    # THE BASIN'S DISCONNECT, WHICH IS THREE CONTACTS ON ONE AXIS. The stub is inside the spout's
    # bore for the whole of the spout's land; the band lies on the spout's outer face and closes
    # the silicone between the two; and the union's collet face meets that same spout's exit
    # face, which is what leaves no stub showing in the room between them.
    # V-K'S OUTLET AND THE SUCTION CHAIN'S COLLET, which `water-4` butts. `enclosure_assembly
    # .build_vk` seats the valve on that collet's own column and plane and the source row's
    # depth brings the two faces together, so what the run carries is the tube inside each
    # quick-connect and nothing between them.
    ("suction-chain", "vk-solenoid"),
    ("hopper-funnel", "hopper-drain-stub"),
    ("hopper-funnel", "hopper-drain-clamp"),
    ("hopper-funnel", "hopper-drain-union"),
)} | {frozenset((x.partition(".")[0], y.partition(".")[0])) for x, y in MADE_UP}


# HOW A CONNECTION IS MADE. A length of tube between two placed bodies is one way and not the
# only one: most of the flavour manifold is butted collet to collet, the hinge carries four
# segments round a hairpin, the two source valves are reached by a quarter turn and the step off
# it, and a leg of the refrigerant loop whose two bodies meet on one plane is made up across
# that plane rather than drawn. A butt between two collets, or a joint whose two mouths are
# ONE POINT READ TWICE, is MORE
# finished than a tube — there is nothing left to draw — so every one of these counts as made,
# and `routed`'s gap is what none of them reaches.
#
# THIS TABLE IS THE VOCABULARY. `_fluid_topology_sync.Seg` holds every segment it labels a chart
# edge with to these names, and `selftest` holds every way the pack states a segment is made to
# them from this side, because the chart's edge labels and this card must not disagree about what
# exists.
MADE_AS = {
    "drawn":     "drawn as a run",
    "straight":  "made by a lane's own straight",
    "butt":      "made by a butt between two collets",
    "mate":      "made up across the plane its two bodies share",
    "fold":      "made by the fold's hairpin",
    "turn":      "made by a quarter turn and the step off it",
    "not drawn": "still to route",
}
UNMADE = "not drawn"


def made_of(how: str) -> str:
    """One `manifold_layout.SEGMENTS` row's own `how` column, as one of `MADE_AS`'s names.

    Not a second classification: `SEGMENTS` already says how the pack makes each of its interior
    connections, and this only renames the two entries whose column word describes the CARRIER
    rather than the joint — a `spine` is the fold's hairpin, and a lane's key is the lane's."""
    import manifold_layout as ml
    if how == "spine":
        return "fold"
    if how in ("turn", "butt"):
        return how
    # A lane's own straight. `manifold_layout.build_assembly` draws a solid for one only past
    # 1e-9, and under that the lane's two collets are face to face.
    return "straight" if ml.dist(*ml.RUNS[how]) > 1e-9 else "butt"


@dataclass
class Connection:
    id: str
    kind: str
    frm: str
    to: str
    made: str = UNMADE
    blocked: str = ""
    note: str = ""        # what the construction measured, where it measured anything

    @property
    def routed(self) -> bool:
        """The machine holds a path for this connection — by any of the ways it makes one."""
        return self.made != UNMADE


def load_connections(runs, joints=()) -> list[Connection]:
    """Every TUBE connection the machine owes, and how the machine makes it.

    The flavour manifold's own segments come out of `fluid-topology.md`'s tables so the
    inventory cannot drift from the topology; the four paths upstream of the carbonator are
    declared above. A run `_lines.py` authors is `drawn`, one `manifold_layout` builds inside the
    pack carries that construction's own name, and what is left is owed. A run that `_routing`
    could not draw as asked carries the shortfall with it.

    `joints` is `enclosure_assembly.refrigerant_mates` — the legs a shared plane CLOSED, `(id,
    from, to, mm apart)` apiece — and a connection it names is MATED: its two mouths are one point
    read twice across a plane its bodies already share, so there is no line to draw and nothing
    left to route. The measurement rides the row. Nothing here re-tests it: `enclosure_assembly`
    takes the reading over the whole loop and hands on only what its own tolerance shut, so a leg
    that stands open or was never measured is still owed here and reads red on its own gate. The
    loop's DRAWN leg is not in this list and does not need to be — it arrives in `runs` like every
    other line. A card built without the reading counts none of them, which is the honest default:
    an assembly nobody measured holds no path anybody has seen.

    The wiring schedule is not here. It is a separate axis and nothing in this pack routes a
    conductor yet, so counting it would only bury the tube reading this card is for."""
    import manifold_layout as ml

    conns: list[Connection] = []
    if _TOPOLOGY.is_file():
        row = re.compile(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|")
        for line in _TOPOLOGY.read_text().splitlines():
            m = row.match(line)
            if m:
                conns.append(Connection(f"fluid-{m.group(1)}", "fluid",
                                        m.group(2).strip(), m.group(3).strip()))
    for table, kind in ((REFRIGERANT_SEGMENTS, "refrigerant"), (WATER_SEGMENTS, "water"),
                        (CO2_SEGMENTS, "co2"), (CARB_SEGMENTS, "water")):
        for cid, frm, to in table:
            conns.append(Connection(cid, kind, frm, to))
    drawn = {r.id for r in runs}
    mated = {cid: gap for cid, _a, _b, gap in joints}
    interior = {f"fluid-{cid}": made_of(how) for cid, _f, _t, how in ml.SEGMENTS}
    for c in conns:
        c.made = ("drawn" if c.id in drawn else
                  "mate" if c.id in mated else
                  interior.get(c.id, UNMADE))
        c.note = f", {mated[c.id]:.3f} mm apart" if c.made == "mate" else ""
        c.blocked = R.BLOCKED.get(c.id, "")
    return conns


# --- what a run connects ---------------------------------------------------

def need_of(run) -> dict:
    """What one run CONNECTS, before what it rides.

    Every diagnosis of a blocked run names what pins the route it currently takes. This is the
    other half: where the run's two ends stand, how far apart that is — SPLIT BY WORLD AXIS,
    because a run draining a reservoir owes its Z whatever its plan does or does not owe — and
    how much path the drawn route spends covering it.

    `detour` is path ÷ span. A run near 1 spends its length on its own need; a run far above it
    is riding infrastructure its ends do not ask for, WHICH NO CORNER-BY-CORNER GRADE WILL SAY.
    A corner short of its stock's minimum is a real defect either way, but on a high-detour run
    the move is the route and not the corner — `calibration/Fences.md`, *The route as
    requirement*.

    WHAT THIS DOES NOT ANSWER, and the card must not be read as answering:

      - A detour near 1 IS NOT HEALTH. A short run can be pinned at both ends and still red.
      - It does not say which lanes and shelves the extra path rides, or who else rides them.
        A lane's customer count is read where the lane is authored, `_lines.py`.
      - The figure says where to look, not what to do.

    `span` is the ENDPOINT separation and nothing else, so the axis split reads off the two end
    waypoints alone and says nothing about the axes the route spends its length on — a route
    that climbs 280 mm in y and comes back reports Δy 0. That gap between the two IS the
    reading. `detour` is None where the ends coincide, rather than a division by zero."""
    a, b = run.pts[0], run.pts[-1]
    span = math.dist(a, b)
    return {
        "ends": [[round(v, 2) for v in a], [round(v, 2) for v in b]],
        "axis": {ax: round(abs(b[i] - a[i]), 2) for i, ax in enumerate("xyz")},
        "span": round(span, 2),
        "path": round(run.length, 2),
        "detour": None if span < 1e-9 else round(run.length / span, 3),
    }


def need_clause(need: dict) -> str:
    """One run's need as the clause a detail row ends with. Empty for a run whose ends
    coincide, which has no ratio to state."""
    if need["detour"] is None:
        return ""
    return (f" — {need['detour']:.2f}× its need: {need['path']:.0f} mm of path for ends "
            f"{need['span']:.0f} mm apart")


# --- the bend grading ------------------------------------------------------

def bend_radii(runs) -> list[dict]:
    """Every authored run graded on the radius it turns at, worst first.

    Two grades, because two different things are wrong when a bend is too tight:

      `drawn` — the radius the run is authored at over its stock's minimum. This is the
                buildable/not question, and the gate reads it.
      `reach` — the largest radius the run's own INTERIOR legs could seat, over the same
                minimum (`_routing.leg_caps`). This is the ceiling the PACK imposes: how gentle
                the run could be made if only its `bend=` were raised.

    The pair is the diagnostic. `drawn` F with `reach` A is an authoring number — one edit in
    `_lines.py` and the run is legal. `drawn` F with `reach` F is a placement: the lane the run
    passes through is too short to turn in at any legal radius, and something on either side of
    it has to move. The leads are held out of `reach` on purpose: a run's exit and approach
    stubs are reaches the author picks, so counting them would blame the pack for a number it
    does not own.

    HOLDING THE LEADS OUT CUTS BOTH WAYS. A high `reach` on a run whose worst corner sits on an
    END leg says the interior is roomy and says nothing about whether that end leg can grow —
    which is read at the call in `_lines.py`, not off this row.

    `reach` bounds the CENTRELINE and nothing else. A run redrawn at its reach sweeps a wider
    tube through different air, so `pack-closes` is what answers that, after the edit.

    A run with no corner carries no bend to grade: `grade` is None and it is out of the gate's
    population. The radius on a straight run is the one it would turn at if it turned."""
    rows = []
    for r in runs:
        st = R.stock_of(r.kind, r.diam)
        caps = R.leg_caps(r)
        inner = [c for c in caps if c[4] == "interior"]
        seat = min((c[0] for c in caps), default=float("inf"))
        hold = min((c[0] for c in inner), default=float("inf"))
        binding = min(inner, key=lambda c: c[0]) if inner else None
        turns = [t for _i, t, _a, _b in r.bends]
        # Each CORNER is graded on the radius IT turns at, and the run reports its worst. A run
        # holds as many radii as it has corners (`_routing.seat_radii`), so one number for the
        # whole run is the tightest of them and says nothing about the rest.
        corners = [{"at": i, "turn": round(t, 1), "radius": round(r.radii[i], 3),
                    "ratio": round(r.radii[i] / st.min_bend, 4),
                    "grade": grade_of(r.radii[i] / st.min_bend),
                    "legs": [round(a, 2), round(b, 2)]}
                   for i, t, a, b in r.bends]
        tightest = min((c["radius"] for c in corners), default=r.bend)
        # THE FLOOR IS THE RUN'S OWN WHERE IT STATES ONE. A stock's figure is about the tool the
        # stock is usually formed on; a leg that is formed by hand says so and is graded against
        # what a hand does (`_routing.Run.min_bend`).
        floor = r.min_bend if r.min_bend else st.min_bend
        ratio = tightest / floor
        rows.append({
            "id": r.id, "kind": r.kind, "frm": r.frm, "to": r.to,
            "stock": st.name, "od": r.diam, "length": round(r.length, 2),
            "radius": round(tightest, 3), "cap": round(r.bend, 3), "minBend": floor,
            "ratio": round(ratio, 4),
            "grade": grade_of(ratio) if turns else None,
            "corners": corners,
            "atSpec": sum(1 for c in corners if c["radius"] >= floor - 1e-9),
            "bends": len(turns), "worstTurn": round(max(turns), 1) if turns else None,
            "seat": None if seat == float("inf") else round(seat, 3),
            "reach": None if hold == float("inf") else round(hold, 3),
            "reachRatio": None if hold == float("inf") else round(hold / st.min_bend, 4),
            "reachGrade": None if not turns else ("A" if hold == float("inf")
                                                  else grade_of(hold / st.min_bend)),
            "binding": None if binding is None else {
                "leg": binding[1], "length": round(binding[2], 3),
                "demand": round(binding[3], 4),
                "from": [round(v, 2) for v in r.pts[binding[1]]],
                "to": [round(v, 2) for v in r.pts[binding[1] + 1]],
            },
            # What the run CONNECTS, beside how well it turns — the reading a corner-by-corner
            # grade cannot give. See `need_of`.
            "need": need_of(r),
        })
    order = {g: i for i, (_lo, g) in enumerate(GRADE_BANDS)}
    # Worst first, and within a grade the run with the least room to improve — which is the
    # order the work wants: a run whose lanes cannot hold a legal bend is a part to move, one
    # whose lanes can is a number to raise. The ungraded straights sort last.
    rows.sort(key=lambda d: (0 if d["grade"] else 1,
                             -order.get(d["grade"], 0), -order.get(d["reachGrade"], 0),
                             d["reachRatio"] if d["reachRatio"] is not None else 1e9))
    return rows


# --- the checks ------------------------------------------------------------

def _bounds(a) -> list:
    """One gate per bound the machine states about itself — every
    leg of the refrigerant loop closing, the vent's drip landing on
    the basin's flat, the drip tray's lip landing inside the −X wall, a through-wall body
    standing under the ceiling, a printed valve cradle standing under its valve, the drip
    basin's own flat floor taking the moisture plate, and the
    enclosure's own: the pack inside the stated width, depth and height, the two seam planes
    clear of the display housing and on the print bed, the funnel throat inside the frame the
    top wall has left. `enclosure_assembly.carry_enclosure_bounds` brings that group over.

    A THIRD GROUP WAS SETTLED BEFORE THE BUILD STARTED. `manifold_layout`, `hopper_funnel` and the
    cold core's modules state bounds about their own CONSTANTS, which are fixed the moment each
    file is read — the crossbar leaving Y-A and Y-B their own tube, the two limbs standing a valve
    body apart, the spine turn holding its stock's corner, a clamp screw reaching the whole of its
    insert, a conduit column leaving the pour its gap, a plug leaving a printable web between its
    arches. Those are read at import into `_stated_bounds` and
    `enclosure_assembly.carry_stated_bounds` brings them over. A bound stated over a population —
    every conduit, every cradle, every pair — is ONE row: its value tallies the readings and its
    detail carries the note each failing one wrote.

    NONE OF THEM STOPS A BUILD, and that is the whole reason they arrive here. A bound the machine
    violates is a thing to LOOK AT, and what a reader looks at is the STEP, the three elevations
    and this card — every one of which a raise destroys, leaving the only account of the fault in a
    terminal nobody commits. An import-time raise destroys them EARLIER, before the build has drawn
    a line, so there is even less to look at. So the check hands its reading back instead,
    `enclosure_assembly.BOUNDS` carries it onto the assembly, and it is red HERE, in the committed
    artifact, with the message the check wrote and the geometry beside it — two limbs pitched under
    a valve body come out as this row AND as `pack-closes` naming both valves with the volume they
    share, which is the picture a raise cannot leave.

    An assembly built by something that states no bounds contributes no rows rather than a
    silent pass: nothing measured is not the same claim as nothing wrong."""
    return [Check(b.id, b.label, "gate", verdict(b.ok), b.value, b.target, list(b.detail))
            for b in getattr(a, "bounds", ())]


_clash_cache: dict = {}


def pack_clashes(a) -> tuple:
    """The one exact pairwise-clash reading for an assembled machine.

    The assembly report prints the detailed pairs and the scorecard publishes the same verdict.
    Holding the result against the assembly keeps those two consumers from repeating every solid
    boolean while pinning the object prevents a recycled ``id`` from receiving another machine's
    answer.
    """
    import manifold_layout as ml

    hit = _clash_cache.get(id(a))
    if hit is not None and hit[0] is a:
        return hit[1]
    result = ml.clashes(a)
    _clash_cache[id(a)] = (a, result)
    return result


def _pack_closes(a) -> Check:
    bad, unanswered = pack_clashes(a)
    detail = [f"{c.a} ∩ {c.b}   {c.volume:.1f} mm³, {c.where}" for c in bad]
    detail += [f"{ni} ? {nj}   {why}" for ni, nj, why in unanswered]
    return Check("pack-closes", "No two solids overlap (pack closes)", "gate",
                 verdict(not detail), f"{len(bad)} clash, {len(unanswered)} unanswered",
                 "0 clash, 0 unanswered", detail)


def _bed_fit(a) -> Check:
    import enclosure as _enc
    bed = (_enc.H2C_X, _enc.H2C_Y, _enc.H2C_Z)
    rows, short = [], []
    for c in a.children:
        if not c.name.startswith("enclosure-"):
            continue
        b = (c.obj.val() if hasattr(c.obj, "val") else c.obj).moved(
            __import__("cadquery").Location(c.loc.wrapped.Transformation())).BoundingBox()
        fits = b.xlen <= bed[0] and b.ylen <= bed[1] and b.zlen <= bed[2]
        rows.append(fits)
        if not fits:
            short.append(f"{c.name}: {b.xlen:.1f} × {b.ylen:.1f} × {b.zlen:.1f} over "
                         f"{bed[0]:g} × {bed[1]:g} × {bed[2]:g}")
    return Check("bed-fit", "Every printed piece fits the bed", "gate",
                 verdict(not short), f"{sum(rows) - 0}/{len(rows)} on the bed",
                 "every piece on the bed", short)


def run_world(a, runs) -> tuple:
    """The drawn world a run is held against, as `(tubes, ends, rest)`.

      `tubes` — each authored run's swept tube, by run id. A run whose sweep is not in the
                assembly is not here: it is not drawn, so there is nothing to ask about.
      `ends`  — the two bodies each run TERMINATES on. A tube seats into their collets by
                design, which is the one contact on this card that is not a defect, so both
                checks below hold that pair out rather than reporting a 0 they built on purpose.
      `rest`  — everything a run must stand clear of: every placed body, the printed box, and
                `manifold_layout`'s own segments and the stubs off its free mouths. No authored
                run terminates on one of those, so they stand as bodies here.

    `lines-clear` asks what any two of these SHARE and `clearance-floor` how far apart they
    STAND. Two questions on either side of zero, one population — read once here so a run cannot
    be in the overlap gate and out of the clearance gate."""
    bodies, drawn, pieces = _split_placed(a)
    tubes = {r.id: drawn[f"tube-{r.id}"] for r in runs if f"tube-{r.id}" in drawn}
    ends = {r.id: {r.frm.partition(".")[0], r.to.partition(".")[0]} for r in runs}
    rest = {**bodies, **pieces,
            **{n: s for n, s in drawn.items() if n not in {f"tube-{i}" for i in tubes}}}
    return tubes, ends, rest


def _lines_clear(a, runs) -> Check:
    """The tube-interpenetration gate, read over the run population on its own.

    `pack-closes` reads every pair in the assembly, tubes included. This asks the runs again —
    tube against tube, and tube against every body, piece and manifold segment it does not
    TERMINATE on. The two bodies a run ends on are held out because a tube seats into their
    collets by design, which is the one overlap here that is not a defect.

    The swept solids come off the assembly rather than being swept again: `_lines.tubes` already
    built each run's tube and `enclosure_assembly` added it under `tube-<connection>`, and a second
    sweep of every run costs more than every boolean below."""
    tubes, ends, rest = run_world(a, runs)
    tbb = {i: _boxes.loose(t) for i, t in tubes.items()}
    rbb = {n: _boxes.loose(s) for n, s in rest.items()}
    detail = []
    ids = list(tubes)
    for i, x in enumerate(ids):
        for y in ids[i + 1:]:
            if _clearing.box_gap(tbb[x], tbb[y]) > 0:
                continue
            v = _overlap.volume(tubes[x], tubes[y])
            if v > _clearing.HIT_VOL:
                detail.append(f"{x} ∩ {y}: {v:.1f} mm³")
    for i in ids:
        for name, solid in rest.items():
            if name in ends[i] or _clearing.box_gap(tbb[i], rbb[name]) > 0:
                continue
            v = _overlap.volume(tubes[i], solid)
            if v > _clearing.HIT_VOL:
                detail.append(f"{i} ∩ {name}: {v:.1f} mm³")
    return Check("lines-clear", "No routed tube intersects a body, a piece or another tube",
                 "gate", verdict(not detail), f"{len(detail)} clash", "0 clash", detail)


def port_leads(a, runs) -> list[dict]:
    """Every port's clear lead, worst first: what it meets along its own axis, how far it got,
    and how much straight a run leaving it needs.

    `pack-closes` says two bodies do not overlap and `located` says a port is carried into world.
    Neither asks the question a connector exists to answer — whether a line can LEAVE it. A port
    is a bore with a direction, and a bore with a body parked in front of it is a bore nothing
    can be plugged into: two fittings a clean millimetre apart with their collets facing each
    other clear every other gate on this card and clear nothing a tube can be built through.

    So the port's own bore is cast along its own axis, at its own Ø, for one `port_lead`, and the
    cast has to reach. The bend radius in it is the LINE's and not the port's: the run that mates
    the port says what stock is drawn there, and a port with no run yet is read against the
    coarsest stock its own bore takes — 1/4" LLDPE asks 17.18 mm of straight where 3/8" braided
    PVC asks 20.66.

    WHAT THE CAST MAY END ON is the body the port is JOINED to, read off the authored runs rather
    than from prose, plus the `MADE_UP` joints that have no run to read. A port whose connection
    is still un-authored is held to the full lead against everything, which is the useful
    direction — that is the state every undrawn segment's two ends are in.

    A CLOSED MATING is the same case on the refrigerant loop. `enclosure_assembly.refrigerant_mates`
    is the legs a shared plane shut — two stations that are one point read twice, with no copper
    between them to bend. A mating standing OPEN is not in that list and stays held to the full
    lead, because an open mating is copper the machine still owes.

    Tube is out of the population. A port's own line lies on its axis by construction, and a
    foreign one crossing there is `lines-clear`'s question, not this one."""
    bodies, _drawn, pieces = _split_placed(a)
    solids = {**bodies, **pieces}
    mates, mating = {}, {}
    for r in runs:
        for anchor, other in ((r.frm, r.to), (r.to, r.frm)):
            mates.setdefault(anchor, set()).add(other.partition(".")[0])
            mating.setdefault(anchor, []).append(r)
    for x, y in MADE_UP:
        mates.setdefault(x, set()).add(y.partition(".")[0])
        mates.setdefault(y, set()).add(x.partition(".")[0])
    for _cid, x, y, _mm in getattr(a, "refrigerant_mates", ()):
        mates.setdefault(x, set()).add(y.partition(".")[0])
        mates.setdefault(y, set()).add(x.partition(".")[0])
    import manifold_layout as ml
    for mouth, bodies_ in ml.MOUTH_MATES.items():
        mates.setdefault(mouth, set()).update(bodies_)
    rows = []
    for name, fr in sorted((getattr(a, "frames", {}) or {}).items()):
        for port in sorted(fr.ports):
            pos, face, diam = fr.ports[port]
            if pos is None or diam is None:
                continue
            anchor = f"{name}.{port}"
            drawn = mating.get(anchor)
            if drawn:
                bend = max(R.stock_of(r.kind, r.diam).min_bend for r in drawn)
            else:
                takes = [s.min_bend for s in R.STOCKS if abs(s.od - diam) < 0.05]
                bend = max(takes) if takes else R.BEND_RATIO * diam
            need = port_lead(bend, diam)
            who, free = _clearing.cast(pos, R.normal_of(face), diam, need, solids,
                                       skip={name} | mates.get(anchor, set()))
            rows.append({"component": name, "port": port, "meets": who,
                         "free": round(free, 3), "need": round(need, 3),
                         "ok": who is None, "gated": anchor not in TERMINI,
                         "routed": bool(drawn)})
    rows.sort(key=lambda d: (d["ok"], d["free"]))
    return rows


def _port_leads(rows) -> Check:
    gated = [d for d in rows if d["gated"]]
    short = [d for d in gated if not d["ok"]]
    detail = ["a port needs the reach of a quarter turn off it — one bend radius of its line plus "
              "the tube's own half-diameter — clear of every body but the one its line joins it to"]
    detail += [f"{d['component']}.{d['port']}: {d['free']:.2f} mm to {d['meets']}, needs "
               f"{d['need']:.2f}" + ("" if d["routed"] else " — no run authored on it yet")
               for d in short]
    detail += [f"{d['component']}.{d['port']}: {d['free']:.2f} mm to "
               f"{d['meets'] or 'nothing'} — opens to atmosphere, not gated"
               for d in rows if not d["gated"]]
    return Check("port-leads", "Every tube port has the straight a run off it needs", "gate",
                 verdict(not short), f"{len(gated) - len(short)}/{len(gated)} clear",
                 "all clear", detail)


def part_clearances(a, runs=()) -> list[tuple]:
    """Every pair standing nearer than `REPORT_NEAR`, tightest first, as `(a, b, gap, allowed)`.
    `allowed` marks a `TOUCHING_OK` seat. A row names a run by its connection id and everything
    else by the name it goes into the assembly under.

    TWO POPULATIONS, ONE FLOOR — body against body, and every drawn run against what it does not
    join. A run is as much a part of the machine as the fittings it joins, and the lane it
    threads is usually the tightest air in the pack. `lines-clear` does not measure it: that gate
    asks what two solids SHARE, and a tube grazing a body at a twentieth of a millimetre shares
    nothing and clears it.

    The gap is the exact solid distance. The boxes are a prefilter and only that: two boxes that
    miss are two solids that miss, so skipping on them is sound, while two boxes that overlap
    say nothing at all.

    THE PRINTED BOX IS NOT IN THE BODY PASS. Bodies seat against walls by design and six of them
    clamp THROUGH one, so a wall is never a body to stand off — an overlap there is
    `pack-closes`'s reading, and there is no clearance to hold. It IS in the run pass: a run
    passing a wall owes it the same millimetre it owes anything else, and the one contact
    between the two that is by intent is an ANCHOR, which is declared as such
    (`anchored_pairs`) and read back by `check_tube_seated`.

    NEITHER IS A PAIR INSIDE THE FLAVOUR MANIFOLD. `manifold_layout` arranges that pack on its
    own hairpins and reports its own inner gap; this module seats it as one thing, so what is
    measured here is how it stands off everything else. A run reaching in from outside is not
    such a pair, and is held to the floor against every body in the pack."""
    bodies, _tubes, _pieces = _split_placed(a)
    pack = pack_bodies()
    names = list(bodies)
    boxes = {n: _boxes.loose(bodies[n]) for n in names}
    out = []
    for i, x in enumerate(names):
        for y in names[i + 1:]:
            if x in pack and y in pack:
                continue
            if _clearing.box_gap(boxes[x], boxes[y]) >= REPORT_NEAR:
                continue
            g = _clearing.gap(bodies[x], bodies[y], REPORT_NEAR)
            if g < REPORT_NEAR:
                out.append((x, y, g, frozenset((x, y)) in TOUCHING_OK))
    out += run_clearances(a, runs)
    out.sort(key=lambda r: r[2])
    return out


def run_clearances(a, runs) -> list[tuple]:
    """Every drawn run against what it does not join, nearer than `REPORT_NEAR`, in
    `part_clearances`' own row shape.

    A run's own two end bodies are out of its population: the tube seats into their collets by
    construction and reads 0 there, which is a contact the machine builds on purpose. It is the
    same exemption `lines-clear` takes, off the same `run_world`, so the two gates cannot
    disagree about which contact is by design.

    A PIECE seated on a run mid-length rather than at an end — an anchor's rib closing on the
    tube at its seat slip — is in `TOUCHING_OK` by the run's own connection id, the same
    declaration a body pair makes, and `anchored_pairs` makes it off the sites that build
    those ribs."""
    anchored = anchored_pairs()
    tubes, ends, rest = run_world(a, runs)
    tbb = {i: _boxes.loose(t) for i, t in tubes.items()}
    rbb = {n: _boxes.loose(s) for n, s in rest.items()}
    out = []
    ids = list(tubes)
    for i, x in enumerate(ids):
        for y in ids[i + 1:]:
            if _clearing.box_gap(tbb[x], tbb[y]) >= REPORT_NEAR:
                continue
            g = _clearing.gap(tubes[x], tubes[y], REPORT_NEAR)
            if g < REPORT_NEAR:
                out.append((x, y, g, False))
    for i in ids:
        for name, solid in rest.items():
            if name in ends[i] or _clearing.box_gap(tbb[i], rbb[name]) >= REPORT_NEAR:
                continue
            g = _clearing.gap(tubes[i], solid, REPORT_NEAR)
            if g < REPORT_NEAR:
                out.append((i, name, g,
                            frozenset((i, name)) in TOUCHING_OK
                            or frozenset((i, name)) in anchored))
    return out


def anchored_pairs() -> set:
    """Every run one of the box's own ribs seats, as the pair `run_clearances` reads.

    A rib closes on its tube at `enclosure_assembly.TUBE_ANCHOR_SLIP`, under the floor by
    construction, and `check_tube_seated` is what holds that contact to the figure the seat is
    drawn at. A rib bored for a BODY never matches here: this set is read in the run pass, where
    the names are runs, and `enclosure_assembly.check_body_seated` is what holds those."""
    import enclosure_assembly as _ea
    pairs = {frozenset((rid, piece)) for rid, _leg, _root, piece in _ea.TUBE_ANCHOR_SITES}
    # And the cold core's own ribs. A row there may be bored for a RUN rather than a body, and
    # that rib stands on the cap — so the pair is the run against `foam-assembly`. A row bored for
    # a body never matches here: this set is only read in the run pass, where the names are runs.
    #   BOTH OF THE CAP'S SEATS COUNT, and they are two tables because they stand on two faces:
    # `cap_anchors` is a rib off the lid's crown, `cap_side_anchors` a post off its front step.
    # What either one does to the run in it is the same contact at the same slip, so a run held
    # by one is as seated as a run held by the other, and reading only the first leaves a run
    # charged for touching the very part that carries it.
    return pairs | {frozenset((name, "foam-assembly"))
                    for name in (*_ea._cci.cap_anchors, *_ea._cci.cap_side_anchors)}


def lane_notes(a, runs, rows) -> list[str]:
    """What CHARGES for a run pinched under the floor: the two bodies it threads between, and
    how far apart they stand.

    A run under the floor against two bodies at once is in a lane too narrow for its own stock,
    and the number that explains it belongs to the two bodies rather than to the run. Half of
    what the lane leaves over the tube's Ø is the best a centred run can do there, so a run
    already at that figure is one to move a BODY for, which is what puts a FORCED tightness on
    the record as forced.

    The pair inside the flavour manifold that a lane is made of is measured HERE and nowhere
    else. `part_clearances` skips it — the pack reports its own inner gaps — but a run threading
    between two of the pack's own bodies is charged by exactly that gap.

    A NOTE AT THE LANE'S OWN BEST CARRIES THE RUN'S NEED. That nothing moves inside the lane is
    a fact about the lane, and it says nothing about whether the run belongs in it: read alone
    it names the pins of the route the run currently takes and reads as a body to move, which
    for a pack body is the move that cascades through everything. So `need_of`'s ratio rides
    beside it, and a run far above 1 there is a route to move before it is a body to move."""
    bodies, _tubes, _pieces = _split_placed(a)
    od = {r.id: r.diam for r in runs}
    need = {r.id: need_of(r) for r in runs}
    tight: dict = {}
    for x, y, g, ok in rows:
        if ok or g >= CLEARANCE_FLOOR:
            continue
        for rid, other in ((x, y), (y, x)):
            if rid in od and other in bodies:
                tight.setdefault(rid, []).append((g, other))
    out = []
    for rid, hits in sorted(tight.items()):
        if len(hits) < 2:
            continue
        hits.sort()
        (ga, p), (gb, q) = hits[0], hits[1]
        # The tube stands `ga` off one body and `gb` off the other, so the two cannot be further
        # apart than the stack they sandwich — a horizon the lane is bound to fall inside.
        lane = _clearing.gap(bodies[p], bodies[q], ga + od[rid] + gb)
        side = (lane - od[rid]) / 2.0
        note = (f"{rid} threads {p} — {q}: they leave {lane:.3f} mm and the tube is "
                f"Ø{od[rid]:g}, so {side:.3f} mm a side")
        out.append(f"{note} is that lane's own best — nothing moves inside it, so the fix is a "
                   f"body or the route itself{need_clause(need[rid])}"
                   if abs(side - ga) < 5e-3 and abs(side - gb) < 5e-3
                   else f"{note} if it were centred, and it is not")
    return out


def _clearance_floor(rows, lanes=()) -> Check:
    short = [r for r in rows if not r[3] and r[2] < CLEARANCE_FLOOR]
    seen = {(x, y, g) for x, y, g, _ok in short}
    # The violations lead, each with what charges for it, then the tight end of the pack either
    # way — a reader taking the first few rows off a capped list has to be reading the ones a fix
    # acts on.
    detail = ["every body pair, and every drawn run against what its own line does not join it "
              "to — the exact solid distance, with boxes only as a prefilter"]
    detail += [f"{x} — {y}: {g:.3f} mm — ✗ under the floor, and nothing seats them together"
               for x, y, g, _ok in short]
    detail += list(lanes)
    detail += [f"{x} — {y}: {g:.3f} mm" + (" — seated against it" if ok else "")
               for x, y, g, ok in rows if (x, y, g) not in seen]
    tightest = min((r[2] for r in rows if not r[3]), default=None)
    return Check("clearance-floor", "Two things the machine does not seat together stand a "
                 "millimetre apart", "gate", verdict(not short),
                 f"{len(short)} under, tightest {tightest:.3f} mm" if tightest is not None
                 else "no pair in reach", f"≥ {CLEARANCE_FLOOR:g} mm", detail)


def _runs_drawn(runs) -> Check:
    short = [f"{cid}: {why}" for cid, why in sorted(R.BLOCKED.items())]
    return Check("runs-drawn", "Every authored run is drawn as its author asked", "gate",
                 verdict(not short), f"{len(runs) - len(short)}/{len(runs)} as drawn",
                 "0 short", short)


def _bend_radius(bends) -> Check:
    order = {g: i for i, (_lo, g) in enumerate(GRADE_BANDS)}
    limit = order[BEND_GRADE_PASS]
    graded = [d for d in bends if d["grade"]]
    corners = sum(len(d["corners"]) for d in graded)
    at_spec = sum(d["atSpec"] for d in graded)
    # The WORST grade any run carries, which is the LARGEST index: `GRADE_BANDS` runs best
    # first, so a higher index is a poorer grade and the gate is only as good as the run
    # that turns tightest.
    worst = max((order[d["grade"]] for d in graded), default=limit)
    hist = {g: sum(1 for d in graded if d["grade"] == g) for _lo, g in GRADE_BANDS}
    tally = " ".join(f"{g}:{hist[g]}" for _lo, g in GRADE_BANDS if hist[g])
    detail = [
        "grade = radius ÷ the stock's minimum — "
        + "; ".join(f"{s.name} R{s.min_bend:g}" for s in R.STOCKS),
        f"runs by grade: {tally or 'none with a corner'}",
        "each row ends with its need — path ÷ the span its own two ends stand at. Far above 1 "
        "is a run riding infrastructure its ends do not ask for, and there the move is the "
        "route rather than the corner. Near 1 is not health: a short run can be pinned at both "
        "ends and still red",
    ]
    for d in bends:
        if not d["grade"] or order[d["grade"]] <= limit:
            continue
        b = d["binding"]
        where = ("" if b is None
                 else f", bound by leg {b['leg']} at {b['length']:.1f} mm")
        detail.append(f"{d['grade']}/{d['reachGrade']} {d['id']} ({d['frm']} → {d['to']}): "
                      f"R{d['radius']:.1f} against R{d['minBend']:g}{where}"
                      + need_clause(d["need"]))
    return Check("bend-radius", "Every routed tube turns at or above its stock's minimum radius",
                 "gate", verdict(worst <= limit),
                 f"{[g for _lo, g in GRADE_BANDS][worst]} — {at_spec}/{corners} corners at spec",
                 f"every corner ≥ its stock's minimum ({BEND_GRADE_PASS})", detail)


def _routed(conns) -> Check:
    """How much of the machine's tube inventory the machine holds a path for, and by what.

    ONE NUMBER, WITH THE BREAKDOWN UNDER IT. A reader takes `routed` as how much is left to
    route, so what it counts has to be every connection the machine already carries fluid
    through, not only the ones drawn as tube — and the detail then has to say which is which, so
    "still to route" can be told from "made by the fold" without opening the pack."""
    done = [c for c in conns if c.routed]
    missing = [c for c in conns if not c.routed]
    by_kind: dict = {}
    for c in conns:
        d, t = by_kind.setdefault(c.kind, [0, 0])
        by_kind[c.kind] = [d + (1 if c.routed else 0), t + 1]
    by_how: dict = {}
    for c in done:
        by_how[c.made] = by_how.get(c.made, 0) + 1
    detail = [
        "a connection is MADE when the machine holds a path for it: a run `_lines.py` draws, one "
        "of the pack's own constructions — a butt between two collets, the fold's hairpin, a "
        "quarter turn and the step off it — or a joint made up across a plane two bodies already "
        "share",
        ", ".join(f"{h} {n}" for h, n in sorted(by_how.items(), key=lambda kv: (-kv[1], kv[0])))
        + f" — {len(missing)} still to route",
        "by circuit — " + ", ".join(f"{k} {d}/{t}" for k, (d, t) in sorted(by_kind.items())),
    ]

    def row(c) -> str:
        return f"{c.id} ({c.kind}): {c.frm} → {c.to} — {MADE_AS[c.made]}{c.note}"

    # What is owed leads, then the joints the build MEASURES, then the rest of what the pack
    # makes without a tube — a measured row carries a figure taken off this assembly, and a
    # declared one carries a construction's own name. The runs are left out: they are the
    # `bend-radius` table's whole population, one row each, measured.
    detail += [row(c) for c in missing]
    detail += [row(c) for c in done if c.made == "mate"]
    detail += [row(c) for c in done if c.made not in ("drawn", "mate")]
    return Check("routed", "Every tube connection the machine owes, made as a real 3-D path",
                 "goal", verdict(not missing), f"{len(done)}/{len(conns)} made",
                 "every connection made", detail)


def _located(a) -> Check:
    """Every port a placed body declares, carried to a world position with its bore."""
    frames = getattr(a, "frames", {}) or {}
    rows, bad = [], []
    for name, fr in sorted(frames.items()):
        for port in sorted(fr.ports):
            pos, _face, diam = fr.ports[port]
            ok = pos is not None and diam is not None
            rows.append(ok)
            if not ok:
                bad.append(f"{name}.{port}")
    return Check("located", "Every port a placed body declares is carried into world",
                 "goal", verdict(not bad), f"{sum(rows)}/{len(rows)} located",
                 "every declared port positioned and sized", bad)


def _coverage(a) -> Check:
    """Every body the assembly places has a fastening row. A body added without one is a body
    whose fastening nobody has been asked about.

    The population is every child that is not a length of tube and not a piece of the printed
    box: a tube is fastened by the collets it seats in, and a wall is what the rest fastens TO."""
    bodies, _tubes, _pieces = _split_placed(a)
    placed = set(bodies)
    declared = {name for name, _by, _joint in mounts()}
    detail = [f"placed, undeclared: {n}" for n in sorted(placed - declared)]
    detail += [f"declared, unplaced: {n}" for n in sorted(declared - placed)]
    return Check("coverage", "Every placed body is declared in the fastening table",
                 "gate", verdict(not detail),
                 f"{len(placed & declared)}/{len(placed)} declared", "all declared", detail)


def _mounted(runs) -> Check:
    """The one fastening axis: a printed feature of another placed part, or nothing.

    The construction each open row stands on today rides in the detail, so the list says what
    a joint would be converting FROM. `pack` is the flavour manifold's own bodies, butted collet
    to collet down its limbs, standing on the hairpins the machine sets the whole pose down on.

    A RIDER IS NOT A JOINT. `RIDES`'s rows are part of another placed body and answer to its
    fastening, so counting them would be counting one joint as many times as its part is drawn.
    They are out of this axis entirely; `coverage` is what holds every one of them declared.
    `NEVER`'s rows are counted apart too: out of the denominator, and last in the detail with
    the reason each carries."""
    rows = mounts()
    never_holds(rows)
    rides_hold(rows)
    tees_butt_held(rows)
    chains_land(rows, runs)
    own = [(n, by, joint) for n, by, joint in rows if n not in RIDES]
    open_joints = sorted((n, joint) for n, by, joint in own
                         if by is None and n not in NEVER)
    detail = [f"{n}: {joint}" for n, joint in open_joints]
    detail += [f"{n}: {joint} — nothing fastens it; {NEVER[n]}"
               for n, _by, joint in sorted(own, key=lambda r: r[0]) if n in NEVER]
    total = len(own) - len(NEVER)
    done = total - len(open_joints)
    return Check("mounted",
                 "A printed feature of another placed part fastens every body", "gate",
                 verdict(not open_joints),
                 f"{done}/{total} mounted, {len(RIDES)} part of another body, "
                 f"{len(NEVER)} nothing fastens",
                 "a printed joint per body", detail)


# --- where each body stands ------------------------------------------------
#
# `enclosure_assembly.seat_body` records BOTH SIDES of a placement as it closes it — the rule the
# construction asked for, and the same rule read back off the geometry that came out of it. So
# nothing below says what a pose ought to be: there is no second table here to drift from the
# pack, only the ledger's own two sides held against each other, and the one question the ledger
# cannot ask of itself — whether every placed body is in it.


def seat_misses(seat) -> list[tuple]:
    """One row per coordinate a seat's rule names, as `(what, wanted, got, off)`.

    A PLANE rule names whole faces of the body's own box and is read per key. A STATION rule
    names the world point one of the body's own mouths goes to, and is read on all three
    coordinates — a mouth the turns do not carry where the seat says shows up here and nowhere
    else."""
    if "station" in seat.rule:
        return [(f"mouth {ax}", w, g, abs(g - w))
                for ax, w, g in zip("xyz", seat.rule["station"], seat.got["station"])]
    return [(k, w, seat.got[k], abs(seat.got[k] - w))
            for k, w in sorted(seat.rule.items()) if k in seat.got]


def seat_tol(seats):
    """`enclosure_assembly.SEAT_TOL` — how far a face may land off the plane its seat named before
    the row is off.

    Taken off the module the ledger's own rows were struck in, which is `enclosure_assembly` under
    whichever name it is running as, so the card cannot hold the pack to a different number from
    the one the pack prints. `None` when the ledger is empty: no row to measure, and no module to
    ask."""
    row = next(iter(seats.values()), None)
    return None if row is None else sys.modules[type(row).__module__].SEAT_TOL


def _placed(a) -> Check:
    """Every placed body's pose, stated as a rule and read back off the placed solid.

    TWO FAILURES ON ONE AXIS. A body with NO ROW is a body whose pose nobody stated — it is where
    it is because the model says so, and an assembler handed the parts could not reproduce it. A
    body whose row MISSED was given a rule its own construction did not close on: two planes named
    on one axis, or a mouth the turns do not carry to the target. A plane rule closes by
    construction, so anything over `enclosure_assembly.SEAT_TOL` is one of those and not import
    noise.

    ONE ROW MAY COVER A GROUP. The refrigeration base is turned and stood as a pair and the
    flavour manifold is posed and lifted whole, so those two rows name every body they carry.
    What the pack carries is not all bodies — its placeholder stubs and fold segments are tube on
    this card — so the coverage is the intersection with the population this card counts, never
    the length of the names."""
    bodies, _tubes, _pieces = _split_placed(a)
    seats = getattr(a, "seats", {}) or {}
    tol = seat_tol(seats)
    covered = {n for s in seats.values() for n in s.members} & set(bodies)
    off = [] if tol is None else [
        (name, what, want, got, d) for name, s in sorted(seats.items())
        for what, want, got, d in seat_misses(s) if d > tol]
    detail = [f"{n}: no seat states where it stands" for n in sorted(set(bodies) - covered)]
    detail += [f"{name}: {what} was asked for {want:.4f} and reads {got:.4f} — {d:.2e} mm off"
               for name, what, want, got, d in sorted(off, key=lambda r: -r[4])]
    return Check("placed", "Every placement is stated as a rule, and the solid lands on it",
                 "goal", verdict(covered == set(bodies) and not off),
                 f"{len(covered)}/{len(bodies)} stated",
                 "a stated rule per body, each landing on it", detail)


def _room_holds(a) -> Check:
    """Every DERIVED pose against the band its own construction states.

    A pose stated as a plane is met by construction, and `placed` reads that. A pose stated as "one
    clearance off whatever stands under it" is a MEASUREMENT — the strike drops a body and takes
    what is left — and `enclosure_assembly.note_room` is where the construction records what it
    actually got. A pose short of its own band still lands and still clears `pack-closes`; what it
    has lost is the room its derivation claimed, and the body that has to move to give it back is
    usually not the one the shortfall is measured on.

    A band with nothing under it holds. That is a body the strike found no landing for inside its
    own reach, so there is nothing for it to fall short of."""
    seats = getattr(a, "seats", {}) or {}
    rows = [(name, what, want, got) for name, s in sorted(seats.items())
            for what, want, got in s.room]
    short = [r for r in rows if r[3] is not None and r[3] < r[2] - ROOM_TOL]
    slack = [got - want for _n, _w, want, got in rows if got is not None]
    tightest = min(slack, default=None)
    # Tightest first, so the band the machine is actually spending sits at the top of the list
    # and the ones with nothing under them sort off the end.
    detail = [f"{name}: {what} — wants {want:g}, has "
              + ("nothing under it" if got is None else f"{got:.3f}")
              + (" — ✗ short of its own band" if got is not None and got < want - ROOM_TOL
                 else "")
              for name, what, want, got in
              sorted(rows, key=lambda r: (r[3] is None, 0.0 if r[3] is None else r[3] - r[2]))]
    return Check("room-holds", "Every derived pose has the room its own construction states",
                 "gate", verdict(not short),
                 f"{len(rows) - len(short)}/{len(rows)} bands held"
                 + ("" if tightest is None else f", tightest {tightest:+.3f} mm"),
                 "every band held", detail)


# --- the runs nothing holds on purpose --------------------------------------
#
# A run over `TUBE_ANCHOR_SPAN` with no rib on it is a run that sags. A name here is one the
# machine leaves loose because a HAND takes it — the same shape as `NEVER` on the mounted axis:
# out of the denominator, and its text goes out on the card.
LOOSE = {
    "fluid-4":
        "The basin's own drain, and the one line in the machine a customer handles. It parts at "
        "the union under the spout every time the hopper goes to the dishwasher and is pushed "
        "back at the same collet, so the length between that joint and V-B has to give: a rib "
        "strapped across it would be a fixed point the customer works against, and the run would "
        "take the load at the collet instead of along its own length.",
    "fluid-18":
        "Nozzle A's line to its rear union. The cold core's side post grips its crossing fore "
        "of the pump (`_cold_core_interface.cap_side_anchors`), and what runs loose past it is "
        "the fall and the union column's own straight — a column whose overhead is the drip "
        "tray's sleeve, the flow meter and the meter's down-line, and whose flanks are the "
        "pump's casting and the moisture plate's lane: nothing printed stands within a rib's "
        "reach of it. The slack sags toward the cap's open air below, away from every line "
        "beside it.",
}


def loose_holds(spans) -> None:
    """Every name in `LOOSE` is a run the machine still draws."""
    for rid, why in LOOSE.items():
        if rid not in spans:
            raise ValueError(
                f"`LOOSE` leaves {rid!r} unanchored on purpose and the machine draws no run by "
                f"that name — it has been renamed or rerouted away, and this exemption is what "
                f"is still holding a place for it.")
        if not why.strip():
            raise ValueError(
                f"{rid!r} is left unanchored with no reason given, and the card prints this text.")


def _tube_anchored(a, runs) -> Check:
    """How far each run goes with nothing holding it.

    THE OTHER HALF OF `mounted`. That axis counts BODIES a printed feature fastens; twenty tubes
    are placed in this machine and none of them is a row on it. A run is fastened by the collet at
    each of its ends and, between them, by whatever rib it lies in — and between held points it
    sags, which puts it off the centreline the clearance gates cleared it on.

    `enclosure_assembly.TUBE_ANCHOR_SPAN` is the stretch one may go. A run needs an anchor when it
    is longer than that and can carry one where a printed face comes within reach of a straight
    length of it; most of the long ones here cruise through the pack with neither."""
    import enclosure_assembly as _ea
    spans = _ea.unsupported_spans(runs, tuple(getattr(a, "tube_anchors", ()))
                                  + tuple(getattr(a, "cap_tube_anchors", ())))
    cap = _ea.TUBE_ANCHOR_SPAN
    loose_holds(spans)
    over = sorted(((s, rid) for rid, s in spans.items() if s > cap and rid not in LOOSE),
                  reverse=True)
    anchored = {rid for rid, _leg, _root, _piece in _ea.TUBE_ANCHOR_SITES}
    detail = [f"{rid}: {s:.1f} mm unheld, {s - cap:.1f} over"
              + (" — anchored once already" if rid in anchored else "")
              for s, rid in over]
    detail += [f"{rid}: {spans[rid]:.1f} mm, held at its anchor" for rid in sorted(anchored)]
    detail += [f"{rid}: {spans[rid]:.1f} mm unheld — left loose; {LOOSE[rid]}"
               for rid in sorted(LOOSE)]
    return Check("tube-anchored", "No run goes further than one span with nothing holding it",
                 "goal", verdict(not over),
                 f"{len(spans) - len(over) - len(LOOSE)}/{len(spans) - len(LOOSE)} within span, "
                 f"{len(LOOSE)} left loose",
                 f"{cap:.0f} mm between held points", detail)


# --- how big it is ---------------------------------------------------------

MM_PER_INCH = 25.4


def _extent(solids) -> tuple:
    """The one box a population of placed solids stands in — `((xmin, ymin, zmin), (xmax, …))`
    in world mm, off `_boxes`' memoized optimal boxes."""
    bbs = [_boxes.boxed(s) for s in solids]
    return ((min(b.xmin for b in bbs), min(b.ymin for b in bbs), min(b.zmin for b in bbs)),
            (max(b.xmax for b in bbs), max(b.ymax for b in bbs), max(b.zmax for b in bbs)))


def size_rows(a) -> list[dict]:
    """How big the machine is: the box the printed shells stand in, and the box everything
    placed stands in. Width is x, depth is y, height is z — the axes `enclosure_assembly`
    packs on.

    BOTH ROWS ARE THE OUTSIDE OF WHAT WAS DRAWN, off the placed solids. So a shell whose
    corners round short reads here, and so does a body seated through a wall and standing
    proud of it: the assembly row standing past the enclosure row on an axis is what is
    outside the box on that axis, in millimetres. The three figures the box is DRAWN to —
    `enclosure.appliance_width` and its two siblings — are the other question, and
    `box-width`, `box-depth` and `box-height` measure the pack against them.

    mm is what is stored. Inches are divided out where they are printed: `report` here,
    `web/contracts/scorecard-sidecar.js` for the viewer.

    A population with nothing in it contributes no row."""
    bodies, tubes, pieces = _split_placed(a)
    rows = []
    for rid, label, solids in (
            ("enclosure", "the printed box, outside face to outside face", pieces.values()),
            ("assembly", "every placed body, the box around them included",
             [*bodies.values(), *tubes.values(), *pieces.values()])):
        solids = list(solids)
        if not solids:
            continue
        lo, hi = _extent(solids)
        rows.append({
            "id": rid, "label": label,
            "min": [round(v, 3) for v in lo], "max": [round(v, 3) for v in hi],
            "mm": [round(h - l, 3) for l, h in zip(lo, hi)],
        })
    return rows


def _size_line(d: dict) -> str:
    """One size row as the terminal prints it, both units."""
    mm = " × ".join(f"{v:.1f}" for v in d["mm"])
    inch = " × ".join(f"{v / MM_PER_INCH:.2f}" for v in d["mm"])
    return f"{mm} mm   {inch} in"


# --- the card --------------------------------------------------------------

@dataclass
class Scorecard:
    checks: list
    bends: list
    conns: list
    sizes: list

    @property
    def gates_pass(self) -> bool:
        return all(c.status == "pass" for c in self.checks if c.kind == "gate")


_card_cache: dict = {}


def build(a) -> Scorecard:
    """The card for one assembly, held against it. A run prints the card and then writes it, and
    the two are one verdict — the gates cast a bore off every port and take an exact distance
    across the pack, and taking them twice would say the same thing at twice the price."""
    hit = _card_cache.get(id(a))
    if hit is not None and hit[0] is a:
        return hit[1]
    sc = _build(a)
    _card_cache[id(a)] = (a, sc)                      # pin `a` so its id stays its own
    return sc


def _build(a) -> Scorecard:
    runs = list(getattr(a, "runs", []))
    bends = bend_radii(runs)
    # `enclosure_assembly` measures every leg of the refrigerant loop, and the ones a shared plane
    # SHUT ride each row: the millimetres a closed mating stands apart print beside the segment it
    # makes. A mating standing open, or a leg with no reading at all, counts here only if a line
    # was actually drawn for it; otherwise it is copper the machine owes and stays in `routed`'s
    # owed column, rather than counting as made because somebody looked at it. Either way it reads
    # red on `refrigerant-joints`, which grades the whole loop — a mating on its two stations, a
    # drawn leg on both its mouths.
    conns = load_connections(runs, getattr(a, "refrigerant_mates", ()))
    leads = port_leads(a, runs)
    clearances = part_clearances(a, runs)
    lanes = lane_notes(a, runs, clearances)
    checks = [_coverage(a), _room_holds(a), _pack_closes(a), _lines_clear(a, runs),
              _port_leads(leads), _clearance_floor(clearances, lanes), _bed_fit(a),
              *_bounds(a),
              _runs_drawn(runs), _bend_radius(bends),
              _mounted(runs), _placed(a), _routed(conns), _located(a),
              _tube_anchored(a, runs)]
    return Scorecard(checks, bends, conns, size_rows(a))


def to_dict(sc: Scorecard) -> dict:
    """The sidecar the 3D viewer reads — `web/contracts/scorecard-sidecar.js` is the contract.

    EVERY FIELD IS A READING. A card built twice off one tree is one file both times, so `git
    status` on it answers what moved: a scorecard that comes back dirty is a scorecard whose
    numbers changed, and whether it still describes the tree is what running the build says.

    Every goal on this card is deferred, which the viewer renders gray. Each one carries its own
    reading in its row."""
    return {
        "gatesPass": sc.gates_pass,
        "size": sc.sizes,
        "checks": [
            {"id": c.id, "label": c.label, "kind": c.kind, "status": c.status,
             "value": c.value, "target": c.target, "detail": list(c.detail),
             # Every requirement the machine is held to is a gate; a goal is a reading beside it.
             "active": c.active and c.kind != "goal"}
            for c in sc.checks
        ],
    }


def write(a, step: Path) -> Path:
    """The card beside `step` — every reading this build took, and nothing else."""
    sc = build(a)
    out = step.parent / (step.stem + ".scorecard.json")
    out.write_text(json.dumps(to_dict(sc), indent=1) + "\n")
    return out


def report(a) -> Scorecard:
    """The card, printed. One line per check, then the bend table — every run and every corner
    in it, because a run holds one radius per corner and its worst says nothing about the
    rest."""
    sc = build(a)
    if sc.sizes:
        print("\nsize                     width × depth × height")
        for d in sc.sizes:
            print(f"  {d['id']:12} {_size_line(d)}   {d['label']}")
    print("\nscorecard")
    for c in sc.checks:
        mark = {"pass": "OK  ", "fail": "FAIL", "warn": "    "}[c.status]
        print(f"  {mark} {c.id:14} {c.value:34} {c.label}")
        for line in c.detail[:DETAIL_MAX]:
            print(f"         {line}")
        if len(c.detail) > DETAIL_MAX:
            print(f"         … {len(c.detail) - DETAIL_MAX} more")
    if sc.bends:
        # `need` rides the same table rather than a second one: the corner grade and what the
        # run connects answer different halves of "is this run the work", and a reader holding
        # only the grade will move a body for a route that should not be in the lane at all.
        print("\nbend radii")
        print(f"  {'run':12} {'grade':7} {'stock':18} {'R drawn':>9} {'min':>6} "
              f"{'reach':>7} {'need':>6} corners")
        for d in sc.bends:
            reach = "—" if d["reach"] is None else f"{d['reach']:.1f}"
            grade = f"{d['grade']}/{d['reachGrade']}" if d["grade"] else "straight"
            per = " ".join(f"{c['grade']}{c['radius']:.1f}" for c in d["corners"]) or "—"
            det = d["need"]["detour"]
            print(f"  {d['id']:12} {grade:7} {d['stock']:18} {d['radius']:9.1f} "
                  f"{d['minBend']:6.1f} {reach:>7} "
                  f"{'    — ' if det is None else f'{det:5.2f}×'} {per}")
    return sc


# --- the controls ----------------------------------------------------------

def selftest() -> int:
    """The card's two readings against known answers — what a run NEEDS, and how a connection is
    MADE.

    NEED, against known-answer geometry — what makes it a measurement and not a number. A
    straight run's path IS its span. A route that goes out and comes back reports the excursion
    its ends do not span. The axis split reads off the ENDPOINTS alone, so a route spending its
    whole length in y between two ends that share a y reports Δy 0 — that gap is the reading, not
    a defect in it. A run whose ends coincide reports no ratio rather than dividing by zero. And
    the figures a real `_routing.route` gives back are the run's own `pts` and `length`, so the
    card grades the same centreline the build sweeps.

    MADE, against the pack and the vocabulary. `MADE_AS` is the table this card and the
    fluid-topology charts share, so every way the pack states a segment is made has to land on
    one of its names — a `how` the card has no word for is a connection one surface counts and
    the other does not. And a joint the build measures across a plane its two bodies already
    share reads as made, while a card handed no such reading counts none of them."""
    import cadquery as cq

    failures = 0

    def check(label, ok, detail=""):
        nonlocal failures
        if not ok:
            failures += 1
        print(f"  {'✓' if ok else '✗'} {label}" + (f" — {detail}" if detail else ""))

    def synthetic(pts):
        return R.Run(id="t", kind="fluid", frm="A.p", to="B.p", pts=list(pts),
                     diam=6.35, bend=25.4)

    print("need (span, axis split, detour)")

    straight = need_of(synthetic([(0.0, 0.0, 0.0), (0.0, 130.0, 0.0)]))
    check("a straight run's path is its span", abs(straight["detour"] - 1.0) < 1e-9,
          f"detour {straight['detour']}")

    out_and_back = need_of(synthetic([(0.0, 0.0, 0.0), (100.0, 0.0, 0.0),
                                      (100.0, 50.0, 0.0), (0.0, 50.0, 0.0)]))
    check("a route out and back reports the excursion its ends do not span",
          out_and_back["span"] == 50.0 and out_and_back["detour"] > 4.0,
          f"span {out_and_back['span']}, path {out_and_back['path']} = "
          f"{out_and_back['detour']}×")

    climb = need_of(synthetic([(10.0, 20.0, 0.0), (10.0, 300.0, 0.0), (10.0, 300.0, 250.0),
                               (10.0, 20.0, 250.0)]))
    check("the axis split reads off the endpoints alone",
          climb["axis"] == {"x": 0.0, "y": 0.0, "z": 250.0},
          f"axis {climb['axis']} on a route spending {climb['path']:.0f} in y")

    loop = need_of(synthetic([(0.0, 0.0, 0.0), (50.0, 0.0, 0.0), (50.0, 50.0, 0.0),
                              (0.0, 0.0, 0.0)]))
    check("coincident ends report no ratio rather than dividing by zero",
          loop["detour"] is None and loop["span"] == 0.0, f"span {loop['span']}")
    check("a run with no ratio states no clause, rather than a blank one",
          need_clause(loop) == "" and need_clause(straight) != "")

    # A real route: the figures must be the run's own pts and length — the same centreline the
    # build sweeps and every other row of the bend table grades. `_routing`'s registries are
    # module state, so they are put back: a control that leaves the world it borrowed emptied
    # is a landmine for whatever calls it next.
    frames, blocked = dict(R._frames), dict(R.BLOCKED)
    R._frames.clear()
    try:
        R.frame("A", cq.Solid.makeBox(10, 10, 10, cq.Vector(0, 0, 0)),
                {"p": ((0.0, 0.0, 0.0), "y+", 6.35)})
        R.frame("B", cq.Solid.makeBox(10, 10, 10, cq.Vector(0, 0, 0)),
                {"p": ((200.0, 130.0, 0.0), "y-", 6.35)})
        run = R.route("t", "A.p", {"x": 200.0}, "B.p", stub=40.0, bend=6.0)
    finally:
        R._frames.clear()
        R._frames.update(frames)
        R.BLOCKED.clear()
        R.BLOCKED.update(blocked)
    n = need_of(run)
    check("a real route's figures are its own pts and length",
          n["span"] == round(math.dist(run.pts[0], run.pts[-1]), 2)
          and n["path"] == round(run.length, 2) and n["detour"] > 1.0,
          f"span {n['span']}, path {n['path']} = {n['detour']}×")

    print("\nmade (the vocabulary this card and the charts share)")

    import manifold_layout as ml

    # The terminal report and JSON card consume one expensive pairwise-solid reading.  This
    # fixture has no geometry: it holds the ownership rule directly, including object identity.
    class _Assembly:
        pass

    assembly = _Assembly()
    calls = 0
    real_clashes = ml.clashes

    def counted_clashes(got):
        nonlocal calls
        calls += 1
        return (["held"], [])

    _clash_cache.clear()
    ml.clashes = counted_clashes
    try:
        first = pack_clashes(assembly)
        second = pack_clashes(assembly)
    finally:
        ml.clashes = real_clashes
        _clash_cache.clear()
    check("the report and card share one exact clash reading",
          calls == 1 and first is second and first == (["held"], []),
          f"{calls} calls, {first!r}, {second!r}")

    # Every `how` the pack states, through the card's own renaming, must land on a name in
    # `MADE_AS` — which is what `_fluid_topology_sync.Seg` labels its edges with. A pack that
    # gains a construction the card has no word for is caught here rather than by a chart and a
    # card quietly reporting different inventories.
    unknown = sorted({how for _cid, _f, _t, how in ml.SEGMENTS if made_of(how) not in MADE_AS})
    check("every way the pack states a segment is made has a word on this card",
          not unknown, ", ".join(unknown) if unknown
          else " ".join(sorted({made_of(how) for _c, _f, _t, how in ml.SEGMENTS})))

    # The refrigerant loop's own shape: three ids the topology tables never carry. The gaps are
    # this control's, not the build's.
    refrig = tuple(cid for cid, _f, _t in REFRIGERANT_SEGMENTS)
    mated = {c.id: c for c in load_connections(
        [], [(cid, "a.p", "b.p", 0.001) for cid in refrig])}
    check("a joint made up across a plane its two bodies share reads as made",
          all(mated[cid].made == "mate" and mated[cid].routed for cid in refrig),
          ", ".join(f"{cid} {mated[cid].made}" for cid in refrig))
    check("and the row carries what the joint measured",
          all(mated[cid].note == ", 0.001 mm apart" for cid in refrig),
          f"{refrig[0]}{mated[refrig[0]].note}")

    bare = {c.id: c for c in load_connections([])}
    check("a card handed no reading counts none of them",
          all(bare[cid].made == UNMADE and not bare[cid].routed for cid in refrig),
          ", ".join(f"{cid} {bare[cid].made}" for cid in refrig))

    # There are two ways to make a leg of that loop and `enclosure_assembly` reads each in its own
    # words. They are THIS CARD'S words, so the gate that grades the loop and the row `routed`
    # prints for the same leg cannot come out under different names.
    import enclosure_assembly as _ea

    check("both ways `enclosure_assembly` makes a leg of the loop have a word on this card",
          {_ea.MADE_BY_MATE, _ea.MADE_BY_TUBE} <= set(MADE_AS),
          f"{_ea.MADE_BY_MATE} {_ea.MADE_BY_TUBE}")
    # And the gate's population is this table's own, not a list kept beside it.
    check("the loop's gate and this card count the same legs",
          _ea.REFRIGERANT_IDS == refrig, " ".join(_ea.REFRIGERANT_IDS))

    print("PASS" if failures == 0 else f"FAIL — {failures}")
    return 0 if failures == 0 else 1


def main(argv) -> int:
    """`selftest` and nothing else. An unrecognised argument EXITS 2 rather than printing
    nothing and exiting 0 — a silent success is what an unattended loop reads as a pass."""
    if argv == ["selftest"]:
        return selftest()
    print("usage: _scorecard.py selftest", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
