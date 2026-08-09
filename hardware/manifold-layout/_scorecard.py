"""The enclosure assembly's requirements as a single pass/fail scorecard — the one place the
arrangement's rules are enumerated as executable checks, computed from the placed geometry
the pack already builds. Printed at the tail of every `enclosure_assembly.py` run and written
beside the STEP as `enclosure-assembly.scorecard.json`, which the 3D viewer's bottom bar reads
([`web/contracts/scorecard-sidecar.js`](/web/contracts/scorecard-sidecar.js)).

Two kinds of check:

  - GATE — a requirement that must hold for the machine as it stands to be built.
  - GOAL — the work this effort is converting, reported as a `score` (0..100) rather than a
           gate, so the pack still builds while it converts.

THE FOCUS IS `bend-radius`, AND THE AXIS BEHIND IT IS `mounted`. Both are answered by where a
body STANDS, which is what makes them one piece of work: `bend-radius` says whether what is
drawn turns at a radius its stock takes, a corner short of that minimum is a tube nobody can
build, and most corners are bound by where their two ends stand — so driving the gate is
usually moving something rather than raising a number. `mounted` is what fastens the body once
it is there, and it is the largest open gap the assembly still carries.

WHICH thing to move is what each bend row's `need` says, and the grade cannot: a run far above
1× the span its own two ends stand at is riding infrastructure its ends never asked for, and
there the route is the thing to move rather than the corner or the body beside it.

`FOCUS_IDS` names the pair, `web/contracts/scorecard-sidecar.js` names it for the viewer, and
`web/tests/scorecard-focus.test.js` holds the two to each other — a card whose two surfaces
lead with different axes points two readers at different work.

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
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_repo = _hw.parent
for _p in (_hw / "scripts", _here.parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import _boxes                                          # noqa: E402
import _clearing                                       # noqa: E402
import _overlap                                        # noqa: E402
import _routing as R                                   # noqa: E402

_TOPOLOGY = _hw / "topology" / "fluid-topology.md"

# Grade bands on `radius ÷ the stock's minimum`. B is the requirement — a run AT its stock's
# floor is buildable and nothing more; A is the room that survives a part moving a millimetre.
GRADE_BANDS = ((1.5, "A"), (1.0, "B"), (0.75, "C"), (0.5, "D"), (0.0, "F"))
BEND_GRADE_PASS = "B"       # the worst grade a run may carry and still clear the gate
# The two axes the work is ON, in the order both surfaces lead with them. Their detail prints to
# `FOCUS_DETAIL_MAX` rows rather than `DETAIL_MAX`, and `to_dict` marks the goal among them as
# the card's live one. `web/contracts/scorecard-sidecar.js` carries the same pair for the viewer.
FOCUS_IDS = ("bend-radius", "mounted")
DETAIL_MAX = 8
FOCUS_DETAIL_MAX = 24

# How close two bodies the machine does not seat against each other may stand.
CLEARANCE_FLOOR = 1.0
# Only pairs nearer than this are ranked, so the clearance detail reads as the tight end of the
# pack rather than as every pair in it.
REPORT_NEAR = 6.0
# The straight a run leaves a fitting on, as a multiple of the line's own bend radius: one reach
# for the stub and one for the tangent its first corner is seated on — `_routing.route`'s own
# two, and the shortest straight any turn off a port can be built in.
PORT_LEAD_BENDS = 2.0
# How far under its own stated band a MEASURED pose may read and still hold. A strike closes on
# the band it states, so this is float noise across that closing and nothing else.
ROOM_TOL = 1e-6


def grade_of(ratio: float) -> str:
    return next(g for lo, g in GRADE_BANDS if ratio >= lo)


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
WATER_SEGMENTS = (
    ("water-2", "asse1022-assembly tube-out", "water-split supply"),
    ("water-3", "water-split to-vk", "vk-solenoid inlet"),
    ("water-4", "vk-solenoid outlet", "suction-chain tube-port"),
    ("water-5", "discharge-chain tube-port", "foam-assembly water-in"),
    ("water-6", "seaflo-pump discharge (3/8\" barb, moulded)", "discharge-chain barb-tip"),
    ("water-7", "seaflo-pump suction (3/8\" barb, moulded)", "suction-chain barb-tip"),
)

# The gas, from the back-panel DERPIPE through the GASHER check and the WR1110 secondary
# regulator to the carbonator's bottom-plate CO2 port — `assembly/internal-plumbing.md` §1. The
# DERPIPE → GASHER joint is a made-up 1/4" NPT thread and carries no line.
CO2_SEGMENTS = (
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
# One row per body `enclosure_assembly` seats, as `(component, by, held)`.
#
#   `by`   — the part whose PRINTED FEATURE fastens it. A boss a screw goes into, a socket a
#            thread makes up in. `None` is a joint still to design, and every `None` here is
#            one unit of the `mounted` axis's gap.
#   `held` — what holds it today, which is a different question. A body resting on a crown or
#            hanging off its own two collets is HELD and is not MOUNTED: nothing about either
#            survives the machine being picked up by one corner.
#
# The flavour manifold's own bodies are not typed here. They are still COUNTED — `pack_mounts`
# reads them off `manifold_layout` and adds a row apiece, so the denominator every fastening
# axis reports is the whole machine and not the part of it this module seats by hand.
MOUNTS = (
    ("compressor", None, "floor"),
    ("condenser+fan", None, "floor"),
    ("foam-assembly", None, "floor"),
    ("seaflo-pump", "foam-assembly", "deck-mount"),
    ("hopper-funnel", None, "wall-capture"),
    ("display", None, "wall-capture"),
    ("suction-chain", None, "none"),
    ("discharge-chain", None, "none"),
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
    ("asse1022-assembly", None, "none"),
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
    # The piercing valve is a saddle: two screws pull its halves together round the
    # compressor's process tube, and the grip on that copper holds it. The fastening ships
    # with the part and closes on a body no printed feature of this machine touches.
    ("bpv31", None, "tube-clamp"),
    # The two cap-sense clamshells close on the flavour lines themselves: dowel pins at the
    # cut plane pull the halves together and the bore grips the tube. The tube is what holds
    # them, and it is the tube they are there to read.
    ("cap-sleeve-a", None, "tube-clamp"),
    ("cap-sleeve-b", None, "tube-clamp"),
    # The controller lies between the two risers with a lead to each sleeve and the J8 loom
    # aft. Nothing printed reaches it and nothing else does either — the leads and the loom
    # carry its weight, which is not a fastening.
    ("mpr121", None, "none"),
    ("water-split", None, "tube-hung"),
    ("flow-regulator", None, "tube-hung"),
    ("vk-solenoid", "foam-assembly", "cradle"),
    ("bulkhead-water", None, "wall-capture"),
    ("c14-inlet", "enclosure-back-top", "bosses"),
    ("co2-inlet", None, "wall-capture"),
    ("gasher-co2", None, "wall-capture"),
    ("wr1110", None, "none"),
    ("bulkhead-flavor-a", None, "wall-capture"),
    ("bulkhead-flavor-b", None, "wall-capture"),
    ("bulkhead-carb", None, "wall-capture"),
    ("digiten-flow", None, "none"),
)


# THE PACK'S OWN BODIES A PRINTED FEATURE FASTENS. Everything else in the pack rides the pack:
# `pack_mounts` types no row, so a body that gains a joint is named here and nowhere else.
#   The cold core's cap lid prints a cradle under each valve that stands on it
# (`_cold_core_interface.cap_cradles`), and the valve's four corner posts press into it. The
# cap is inside `foam-assembly`, which is the placed body the cradle is a feature of, so that
# is what fastens them — the same way a wall boss fastens the power column.
PACK_MOUNTS = {
    "valve-v-a": ("foam-assembly", "cradle"),
    "valve-v-b": ("foam-assembly", "cradle"),
}


def pack_mounts() -> tuple:
    """The flavour manifold's own bodies, one fastening row each.

    `manifold_layout` arranges them on the pack's four spine hairpins and this module stands
    that whole pose on the base's crown, so what carries every one of them is THE PACK: the
    hairpins are what the machine sets it down on, and no printed feature fastens a body inside
    it. They are placed bodies of this machine and no other card grades their fastening, so they
    are counted here rather than left out of the denominator — a card whose `mounted` figure
    omits the flavour pumps is measuring a different machine from the one it draws.

    Derived rather than typed, so the ten valves, their coils, the two pumps and the junction
    tees ride whatever the pack does next."""
    return tuple((name, *PACK_MOUNTS.get(name, (None, "pack")))
                 for name in sorted(pack_bodies()))


def mounts() -> tuple:
    """Every placed body's fastening row — the bodies this module seats, then the pack's."""
    return MOUNTS + pack_mounts()


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
    # A made-up 1/4" NPT thread: `enclosure_assembly.build_gasher_co2` stations the check valve's
    # inlet on the DERPIPE's own stub tip. `co2-inlet` states no port table, so the pair is named
    # on the end that has one.
    ("gasher-co2.inlet", "co2-inlet"),
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
    # The base's own two bodies, on the seam `enclosure_assembly.report` prints as a mate at 0 by
    # intent.
    ("compressor", "condenser+fan"),
    # The cold core's front face stands on the base's aft face: `enclosure_assembly.build_pack`
    # strikes `aft` off the bodies that reach below the core's crown, and `build_foam` seats it
    # there.
    ("compressor", "foam-assembly"),
    ("condenser+fan", "foam-assembly"),
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
    # THE PROBE PLATE LIES ON THE BASIN'S FLOOR, which is the whole of what it does: a plate
    # standing a millimetre off the floor reads only once the pool is a millimetre deep, and the
    # weep this watches for is a drip at a time. `enclosure_assembly.build_moisture_plate` seats
    # its underside on that floor and `drip_pan.check_plate` holds the floor wide enough to take
    # it, so the pair reads 0 and it is the sensor working.
    ("drip-pan", "moisture-plate"),
    # EACH CAP-SENSE SLEEVE CLOSES ROUND ITS OWN LINE. The clamshell's bore is the tube's OD
    # plus `cap_sense_sleeve.bore_clearance` on the radius, so the pair reads that clearance
    # and it is the sleeve gripping. A sleeve standing a millimetre off the tube is two foil
    # rings reading air. The pair is named by the run's connection id, which is how
    # `run_clearances` names a tube.
    ("fluid-18", "cap-sleeve-a"),
    ("fluid-28", "cap-sleeve-b"),
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
        ratio = tightest / st.min_bend
        rows.append({
            "id": r.id, "kind": r.kind, "frm": r.frm, "to": r.to,
            "stock": st.name, "od": r.diam, "length": round(r.length, 2),
            "radius": round(tightest, 3), "cap": round(r.bend, 3), "minBend": st.min_bend,
            "ratio": round(ratio, 4),
            "grade": grade_of(ratio) if turns else None,
            "corners": corners,
            "atSpec": sum(1 for c in corners if c["radius"] >= st.min_bend - 1e-9),
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

@dataclass
class Check:
    id: str
    label: str
    kind: str            # "gate" | "goal"
    status: str          # "pass" | "fail" | "warn"
    value: str
    target: str
    detail: list = field(default_factory=list)
    active: bool = True


def _verdict(ok: bool) -> str:
    return "pass" if ok else "fail"


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
    return [Check(b.id, b.label, "gate", _verdict(b.ok), b.value, b.target, list(b.detail))
            for b in getattr(a, "bounds", ())]


def _pack_closes(a) -> Check:
    import manifold_layout as ml
    bad, unanswered = ml.clashes(a)
    detail = [f"{c.a} ∩ {c.b}   {c.volume:.1f} mm³, {c.where}" for c in bad]
    detail += [f"{ni} ? {nj}   {why}" for ni, nj, why in unanswered]
    return Check("pack-closes", "No two solids overlap (pack closes)", "gate",
                 _verdict(not detail), f"{len(bad)} clash, {len(unanswered)} unanswered",
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
                 _verdict(not short), f"{sum(rows) - 0}/{len(rows)} on the bed",
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
    tbb = {i: _boxes.boxed(t) for i, t in tubes.items()}
    rbb = {n: _boxes.boxed(s) for n, s in rest.items()}
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
                 "gate", _verdict(not detail), f"{len(detail)} clash", "0 clash", detail)


def port_leads(a, runs, placeholders=frozenset()) -> list[dict]:
    """Every port's clear lead, worst first: what it meets along its own axis, how far it got,
    and how much straight a run leaving it needs.

    `pack-closes` says two bodies do not overlap and `located` says a port is carried into world.
    Neither asks the question a connector exists to answer — whether a line can LEAVE it. A port
    is a bore with a direction, and a bore with a body parked in front of it is a bore nothing
    can be plugged into: two fittings a clean millimetre apart with their collets facing each
    other clear every other gate on this card and clear nothing a tube can be built through.

    So the port's own bore is cast along its own axis, at its own Ø, for `PORT_LEAD_BENDS` of the
    line's bend radius, and the cast has to reach. The radius is the LINE's and not the port's:
    the run that mates the port says what stock is drawn there, and a port with no run yet is
    read against the coarsest stock its own bore takes — 1/4" LLDPE asks 28 mm of straight where
    3/8" braided PVC asks 31.8.

    WHAT THE CAST MAY END ON is the body the port is JOINED to, read off the authored runs rather
    than from prose, plus the `MADE_UP` joints that have no run to read. A port whose connection
    is still un-authored is held to the full lead against everything, which is the useful
    direction — that is the state every undrawn segment's two ends are in.

    THE PACK'S OWN MOUTHS ARE NOT CAST. `PORT_LEAD_BENDS` is `_routing.route`'s own shape — one
    bend radius of stub off the port, and the tangent of the corner it turns in next — and
    `manifold_layout.INTERIOR_MOUTHS` is every port the pack sweeps its own line off instead,
    with no stub. Those rows carry a lead of 0. The swept line goes into the assembly, where
    `pack-closes` reads it against every body in the machine.

    A CLOSED MATING is the same case on the refrigerant loop. `enclosure_assembly.refrigerant_mates`
    is the legs a shared plane shut — two stations that are one point read twice, with no copper
    between them to bend. A mating standing OPEN is not in that list and stays held to the full
    lead, because an open mating is copper the machine still owes.

    Tube is out of the population. A port's own line lies on its axis by construction, and a
    foreign one crossing there is `lines-clear`'s question, not this one.

    A lead that ends on a body still standing in as a bare primitive says so. The cast is an
    exact boolean and the contact is real, but what it is real against is a BOX someone drew to
    reserve room — so the number is a reading of the placeholder, and a pack redrawn around it
    is a pack redrawn around a guess."""
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
    rows = []
    for name, fr in sorted((getattr(a, "frames", {}) or {}).items()):
        for port in sorted(fr.ports):
            pos, face, diam = fr.ports[port]
            if pos is None or diam is None:
                continue
            anchor = f"{name}.{port}"
            drawn = mating.get(anchor)
            interior = anchor in ml.INTERIOR_MOUTHS
            if interior:
                who, free, need = None, 0.0, 0.0
            else:
                if drawn:
                    bend = max(R.stock_of(r.kind, r.diam).min_bend for r in drawn)
                else:
                    takes = [s.min_bend for s in R.STOCKS if abs(s.od - diam) < 0.05]
                    bend = max(takes) if takes else R.BEND_RATIO * diam
                need = PORT_LEAD_BENDS * bend
                who, free = _clearing.cast(pos, R.normal_of(face), diam, need, solids,
                                           skip={name} | mates.get(anchor, set()))
            rows.append({"component": name, "port": port, "meets": who,
                         "free": round(free, 3), "need": round(need, 3),
                         "ok": who is None, "gated": anchor not in TERMINI,
                         "routed": bool(drawn) or interior,
                         "onPlaceholder": who in placeholders})
    rows.sort(key=lambda d: (d["ok"], d["free"]))
    return rows


def _port_leads(rows) -> Check:
    gated = [d for d in rows if d["gated"]]
    short = [d for d in gated if not d["ok"]]
    detail = [f"a port needs {PORT_LEAD_BENDS:g} bend radii of its own bore along its own axis, "
              f"clear of every body but the one its own line joins it to — the pack's own "
              f"interior mouths carry a swept line off the collet and ask for none"]
    detail += [f"{d['component']}.{d['port']}: {d['free']:.2f} mm to {d['meets']}, needs "
               f"{d['need']:.2f}" + ("" if d["routed"] else " — no run authored on it yet")
               + (" — and that body is still a placeholder box" if d["onPlaceholder"] else "")
               for d in short]
    detail += [f"{d['component']}.{d['port']}: {d['free']:.2f} mm to "
               f"{d['meets'] or 'nothing'} — opens to atmosphere, not gated"
               for d in rows if not d["gated"]]
    return Check("port-leads", "Every tube port has the straight a run off it needs", "gate",
                 _verdict(not short), f"{len(gated) - len(short)}/{len(gated)} clear",
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
    `pack-closes`'s reading, and there is no clearance to hold. It IS in the run pass: nothing
    seats a tube against a wall, so a run passing one owes it the same millimetre it owes
    anything else.

    NEITHER IS A PAIR INSIDE THE FLAVOUR MANIFOLD. `manifold_layout` arranges that pack on its
    own hairpins and reports its own inner gap; this module seats it as one thing, so what is
    measured here is how it stands off everything else. A run reaching in from outside is not
    such a pair, and is held to the floor against every body in the pack."""
    bodies, _tubes, _pieces = _split_placed(a)
    pack = pack_bodies()
    names = list(bodies)
    boxes = {n: _boxes.boxed(bodies[n]) for n in names}
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

    A body seated ON a run mid-length rather than at an end — a sleeve closing round the tube —
    is in `TOUCHING_OK` by the run's own connection id, the same declaration a body pair makes."""
    tubes, ends, rest = run_world(a, runs)
    tbb = {i: _boxes.boxed(t) for i, t in tubes.items()}
    rbb = {n: _boxes.boxed(s) for n, s in rest.items()}
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
                out.append((i, name, g, frozenset((i, name)) in TOUCHING_OK))
    return out


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
                 "millimetre apart", "gate", _verdict(not short),
                 f"{len(short)} under, tightest {tightest:.3f} mm" if tightest is not None
                 else "no pair in reach", f"≥ {CLEARANCE_FLOOR:g} mm", detail)


def _runs_drawn(runs) -> Check:
    short = [f"{cid}: {why}" for cid, why in sorted(R.BLOCKED.items())]
    return Check("runs-drawn", "Every authored run is drawn as its author asked", "gate",
                 _verdict(not short), f"{len(runs) - len(short)}/{len(runs)} as drawn",
                 "0 short", short)


def _bend_radius(bends) -> Check:
    order = {g: i for i, (_lo, g) in enumerate(GRADE_BANDS)}
    limit = order[BEND_GRADE_PASS]
    graded = [d for d in bends if d["grade"]]
    corners = sum(len(d["corners"]) for d in graded)
    at_spec = sum(d["atSpec"] for d in graded)
    worst = min((order[d["grade"]] for d in graded), default=limit)
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
                 "gate", _verdict(worst <= limit),
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
                 "goal", _verdict(not missing), f"{len(done)}/{len(conns)} made",
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
                 "goal", _verdict(not bad), f"{sum(rows)}/{len(rows)} located",
                 "every declared port positioned and sized", bad)


def _coverage(a) -> Check:
    """Every body the assembly places has a fastening row. A body added without one is a body
    whose fastening nobody has been asked about.

    The population is every child that is not a length of tube and not a piece of the printed
    box: a tube is fastened by the collets it seats in, and a wall is what the rest fastens TO."""
    bodies, _tubes, _pieces = _split_placed(a)
    placed = set(bodies)
    declared = {name for name, _by, _held in mounts()}
    detail = [f"placed, undeclared: {n}" for n in sorted(placed - declared)]
    detail += [f"declared, unplaced: {n}" for n in sorted(declared - placed)]
    return Check("coverage", "Every placed body is declared in the fastening table",
                 "gate", _verdict(not detail),
                 f"{len(placed & declared)}/{len(placed)} declared", "all declared", detail)


def _mounted() -> Check:
    rows = mounts()
    open_joints = [(n, held) for n, by, held in rows if by is None]
    # A body already held by something looser sorts last — that joint is a conversion, and one
    # nothing holds at all is a joint to invent.
    open_joints.sort(key=lambda r: (r[1] != "none", r[0]))
    detail = [f"{n}: held by {held}" for n, held in open_joints]
    done = len(rows) - len(open_joints)
    return Check("mounted",
                 "A printed feature of another placed part fastens every body", "goal",
                 _verdict(not open_joints), f"{done}/{len(rows)} mounted",
                 "a printed joint per body", detail)


def _held() -> Check:
    """Something holds every body — the looser axis `mounted` is measured against.

    A body captured in a wall's bore, resting on a crown, riding on rails, hanging off its own
    two collets or standing in the pack is HELD. What is not held is a body the machine has
    nowhere to put down: it is where it is because the model says so, and an assembler handed
    the parts could not reproduce the pose."""
    rows = mounts()
    loose = sorted(n for n, _by, held in rows if held == "none")
    by_holder: dict = {}
    for name, _by, held in rows:
        if held != "none":
            by_holder.setdefault(held, []).append(name)
    detail = [f"{held} holds {len(ns)}: {', '.join(sorted(ns))}"
              for held, ns in sorted(by_holder.items())]
    detail += [f"{n}: nothing holds it at all" for n in loose]
    return Check("held", "Something holds every body", "goal", _verdict(not loose),
                 f"{len(rows) - len(loose)}/{len(rows)} held", "a holder per body", detail)


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
                 "goal", _verdict(covered == set(bodies) and not off),
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
                 "gate", _verdict(not short),
                 f"{len(rows) - len(short)}/{len(rows)} bands held"
                 + ("" if tightest is None else f", tightest {tightest:+.3f} mm"),
                 "every band held", detail)


def is_primitive(shape) -> bool:
    """True when the geometry is still a bare box or cylinder.

    `makeBox` leaves one solid with six planar faces and `makeCylinder` one with three — two
    planar caps and a round side. Authored geometry carries holes, bosses and fillets on top of
    that, so anything else has been drawn rather than stood in for."""
    if len(shape.Solids()) != 1:
        return False
    faces = shape.Faces()
    planar = sum(1 for f in faces if f.geomType() == "PLANE")
    return (len(faces) == 6 and planar == 6) or (len(faces) == 3 and planar == 2)


def shape_rows(a) -> list[dict]:
    """Per body: the boxes it really occupies, how much of them is material, and whether the
    geometry is still a bare primitive.

    ONE BOX PER SOLID THE BODY IS BUILT FROM, following the part's own construction. The single
    box drawn around all of them is a different object and for a hollow or conical body mostly
    air — the hopper funnel's is nearly all air, and `fill` is the figure that says so: how much
    of the boxes IS material. At 1.0 they are the part, and the lower it runs the less a box
    stands in for the shape and the more only the solid will answer."""
    bodies, _tubes, _pieces = _split_placed(a)
    rows = []
    for name, solid in sorted(bodies.items()):
        boxes = _boxes.boxed_solids(solid)
        total = sum(b.xlen * b.ylen * b.zlen for b in boxes)
        rows.append({
            "component": name,
            "boxes": [[round(b.xmin, 3), round(b.ymin, 3), round(b.zmin, 3),
                       round(b.xmax, 3), round(b.ymax, 3), round(b.zmax, 3)] for b in boxes],
            "fill": round(solid.Volume() / total, 4) if total > 0 else 0.0,
            "primitive": is_primitive(solid),
            "declared": None,
        })
    rows.sort(key=lambda d: (not d["primitive"], d["fill"], d["component"]))
    return rows


def _shaped(rows) -> Check:
    prim = [d for d in rows if d["primitive"]]
    detail = [f"{d['component']}: still a bare "
              + ("box" if len(d["boxes"]) == 1 and d["fill"] > 0.99 else "primitive")
              + f", {len(d['boxes'])} solid" + ("" if len(d["boxes"]) == 1 else "s")
              for d in prim]
    # The bodies a single box describes worst, which are the ones whose box must never be read
    # as their shape — every clearance on this card takes them as solids for that reason.
    detail += [f"{d['component']}: {len(d['boxes'])} "
               + ("box holds" if len(d["boxes"]) == 1 else "boxes hold")
               + f" {d['fill'] * 100:.0f}% material"
               for d in [r for r in rows if not r["primitive"]][:6]]
    return Check("shaped", "Every body is real geometry rather than a placeholder", "goal",
                 _verdict(not prim), f"{len(rows) - len(prim)}/{len(rows)} authored",
                 "no placeholder solids", detail)


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


def _score(check: Check) -> int:
    lo, hi = check.value.split("/")[0], check.value.split("/")[-1]
    try:
        done = int(re.findall(r"(\d+)", lo)[-1])
        total = int(re.findall(r"(\d+)", hi)[0])
    except (IndexError, ValueError):
        return 0
    return 0 if not total else round(100.0 * done / total)


# --- the card --------------------------------------------------------------

@dataclass
class Scorecard:
    checks: list
    bends: list
    conns: list
    ports: list
    shapes: list
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
    shapes = shape_rows(a)
    leads = port_leads(a, runs, {d["component"] for d in shapes if d["primitive"]})
    clearances = part_clearances(a, runs)
    lanes = lane_notes(a, runs, clearances)
    ports = []
    for name, fr in sorted((getattr(a, "frames", {}) or {}).items()):
        for port in sorted(fr.ports):
            pos, face, diam = fr.ports[port]
            ports.append({
                "component": name, "name": port, "kind": "fluid",
                "pos": None if pos is None else [round(v, 3) for v in pos],
                # The FACE ITSELF and not a rendering of it: a body-face name where the port
                # declares one, the outward normal where it is clocked off the world axes.
                # `web/contracts/port-format.js` reads a direction out of this.
                "face": face if isinstance(face, str) else [round(v, 6) for v in face],
                "diam": diam,
                "mates": ", ".join(sorted(r.id for r in runs
                                          if f"{name}.{port}" in (r.frm, r.to))) or "—",
                "status": "ok" if pos is not None and diam is not None else "no-pos",
                "note": "",
            })
    checks = [_coverage(a), _room_holds(a), _pack_closes(a), _lines_clear(a, runs),
              _port_leads(leads), _clearance_floor(clearances, lanes), _bed_fit(a),
              *_bounds(a),
              _runs_drawn(runs), _bend_radius(bends),
              _mounted(), _placed(a), _routed(conns), _located(a), _shaped(shapes), _held()]
    return Scorecard(checks, bends, conns, ports, shapes, size_rows(a))


def _source() -> dict:
    """When this card was built, and off what HEAD.

    ORIENTATION ONLY. The commit is what the tree was at, not what the card was built from: a
    dirty tree stamps exactly as a clean one, and nothing here fingerprints a file. So a stamp
    can never say the card still describes the tree — the way to know is to run the build."""
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(_repo),
                                capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        commit = ""
    return {"generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "commit": commit or None}


def to_dict(sc: Scorecard) -> dict:
    """The sidecar the 3D viewer reads — `web/contracts/scorecard-sidecar.js` is the contract.

    The goal in `FOCUS_IDS` is the live one and every other goal is deferred, which the viewer
    renders gray. Each deferred one still carries its measured score, so the bar reads what it
    is rather than a zero. Read off `FOCUS_IDS` rather than named again here: an axis spelt in
    two places is an axis that drifts between them."""
    by_id = {c.id: c for c in sc.checks}
    # A mount row's `kind` is the body's geometry authorship, which the shape table measures —
    # a joint designed against a placeholder is a joint designed against a guess.
    prim = {d["component"]: d["primitive"] for d in sc.shapes}
    return {
        "gatesPass": sc.gates_pass,
        "size": sc.sizes,
        "placed": _score(by_id["placed"]),
        "located": _score(by_id["located"]),
        "shaped": _score(by_id["shaped"]),
        "routed": _score(by_id["routed"]),
        "held": _score(by_id["held"]),
        "mounted": _score(by_id["mounted"]),
        "checks": [
            {"id": c.id, "label": c.label, "kind": c.kind, "status": c.status,
             "value": c.value, "target": c.target, "detail": list(c.detail),
             # A goal in `FOCUS_IDS` is the axis the work is on; every other goal is a reading
             # the card takes but is not converting yet.
             "active": c.active and c.id in FOCUS_IDS if c.kind == "goal" else c.active}
            for c in sc.checks
        ],
        "ports": sc.ports,
        "shapes": sc.shapes,
        "bends": sc.bends,
        "mounts": [{"component": n, "by": by, "held": h,
                    "kind": "placeholder" if prim.get(n) else "real"}
                   for n, by, h in mounts()],
        "source": _source(),
    }


def write(a, step: Path) -> Path:
    sc = build(a)
    out = step.with_suffix("").with_suffix(".scorecard.json") if step.suffix else step
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
        limit = FOCUS_DETAIL_MAX if c.id in FOCUS_IDS else DETAIL_MAX
        for line in c.detail[:limit]:
            print(f"         {line}")
        if len(c.detail) > limit:
            print(f"         … {len(c.detail) - limit} more")
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
