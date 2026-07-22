"""Kitchen Edition enclosure contents — the core subsystems packed.

Detailed STEP imports where they exist (cold-core foam assembly — shell +
top/bottom foam-cap stacks — the compressor shroud, the source-select
assembly, the bag-circuit assembly, the nozzle-gate assembly, both Kamoer
pump assemblies, both pump-inlet union tees, both pump-discharge dividers
(Y-D/Y-G) and their four turn elbows, the PCBA assembly, the power
assembly, the DC distribution block, the DERPIPE CO2 inlet, the MQ-6 gas
sensor, the panel bulkheads + C14). One placeholder primitive remains
(condenser+fan). Not everything is packed — deferred, tracked by the fluid
topology (/hardware/topology/fluid-topology.md) and the scorecard's
connection table, never silently dropped, while the front column settles
around the tray stack and the pump row: the water deck (SeaFlo diaphragm
pump, Multiplex BFP, drip pan + moisture plate, the SeaFlo outlet check),
the DIGITEN flow sensor, and the CO2 chain's GASHER check + WR1110 regulator.

Components only: no tubes, no wires, no mount features. enclosure_assembly.py
verifies the pack pairwise non-intersecting at every export.

The Waterdrop 15UC-UF inline filter (~Ø63 × 311 mm) mounts outside the
enclosure, inline on the customer's 1/4" LLDPE feed upstream of the
rear-panel water-inlet bulkhead (/hardware/assembly/internal-plumbing.md §2).

Coordinate frame: +X right, +Y back, +Z up. Origin at the lower-front-left
corner. The enclosure is four printed pieces — a Y seam as far back as the
cold core allows, and a Z seam per column: at the front stack's waist over
the condenser in the front pieces, above the foam-cap top in the back
(enclosure.py `z_joint_front` / `z_joint_back`) — whose lips and cross-pin
pods hug the walls; the wall-adjacent insets below keep content clear of
them.

The band above the cold core — foam-cap top to ceiling, the foam's full
footprint — is the appliance's service bay. The electronics shelf (power
assembly, PCBA, DC distribution block) lies flat on the foam-cap top in
its front half, and every external connection (the faucet umbilical, the
C14 mains inlet, the tap-water inlet) penetrates the rear wall above the
cold core, its body reaching ~28–35 mm forward into the band's open rear
half. The risers' tube-and-cord traffic climbs the foam's front face and
crosses the band to those terminations. The cold core seats directly
against the rear wall.

The cold core's tube connections are defined by the foam shell's
penetrations (/hardware/printed-parts/cold-core/foam-shell/README.md
§Penetrations), all on its −Y front wall except the CO2 top entry — in
enclosure world coordinates:
  * carbonated-water outlet at (141.5, 182, 46.5) — the riser runs up the
    foam front face past the DIGITEN flow sensor to the rear umbilical;
  * reservoir (bag) lines at (44.5, 182, 35.5) and (238.5, 182, 35.5) —
    they climb the foam front face to the bag-circuit loops;
  * the shared slot at x 141.5 spanning z ~72–246 — both copper evaporator
    stubs (to the compressor), the water inlet (from the SeaFlo discharge),
    and the PRV vent;
  * CO2 entry down through the foam-cap top at (141.5, 199.8).

Strata, floor to ceiling:
  * Floor:   compressor shroud (front-left) + condenser/fan (front-right,
             cross-flow along X, the donor block tipped on its back so its
             long dimension runs along Y and the floor stratum tops out
             level with the compressor; the donor's factory filter-drier is
             brazed to its outlet, inside this harvested block), the MQ-6
             on the floor between the compressor and the cold core
             (isobutane sinks).
  * Zone A:  cold core (foam assembly: bottom cap + shell + top cap) on the
             floor at the back, its −Y dispense/service ports facing
             forward.
  * Zone C (the front column's upper band): the valve-manifold tray stack,
             pressed aft against the cold core — the source-select
             assembly (Tray 1: V-A, V-B, Y-A, Y-B, V-C, V-D on a printed
             tray) FLOORING the stack, plate down and valves up, spanning
             the front width with its tall walls' backs on the foam's
             front face and its east collets facing up at the tap feed
             and the funnel drain that arrive from above; the bag-circuit
             assembly (Tray 2: V-E/V-F/V-H/V-I + Tees Y-E/Y-H) INVERTED
             on top of it, wall-top to wall-top, its bare east ports
             facing the nozzle-gate pocket and its bag branches out ±Y;
             and the nozzle-gate assembly (Tray 3: V-G/V-J, all ports
             bare) INVERTED the same way in that pocket — east of the
             bag assembly on the stack's second-story plane — its
             inner ports facing west at the bag east bank across the
             seats reserved for the pump-discharge tees (Y-D/Y-G,
             deferred), its outer ports facing east at the wall. The
             lower trays' west outlet elbows are rolled off their port
             axes to face each other — the source's inward, the bag's
             outward — down one leaning line: the JUNCTION COLUMN, with
             the pump-inlet union tees standing on that line and one
             straight stub joining each collet to the tee it butts. The
             stack floats over the floor stratum,
             leaving an open under-stack corridor for the manifold's
             cross-machine lines, and its floor clears the front Z-seam's
             lip band. Ahead of the stack, the PUMP ROW: both Kamoer
             KPHM400 assemblies lying depth-along-X in one pose — motors
             west, outlet elbows standing on the +Z faces, free collets
             facing west at the row's crest. P-A's head is nose-in at
             mid-row, its aft elbow one clearance ahead of the bag tray's
             Y-E bag branch; P-B sits one slot east and forward, ahead of
             the source-select east bank. The funnel's centred drain
             hangs over the row with the stack's whole height below it
             before segment 4 reaches V-B-I. Holders TBD (held).
  * Zone B (the band above the cold core): the electronics shelf lying
             flat on the foam-cap top in the band's front half — power
             assembly at −X, PCBA at +X, the DC distribution block behind
             the power row — leaving the CO2 top entry in open air ahead
             of it; the rear half open for the panel bodies reaching in
             from the rear wall (the umbilical triangle, the tap-water
             bulkhead, and the C14) and the riser traffic crossing to
             them.
  * Zone C top: the top wall right of the display is one open rectangle
             cut at the placed funnel's collar (enclosure.py
             `_hopper_hole` reads FUNNEL_CX/CY + the funnel's own dims) —
             the funnel is a static part (hopper_funnel.py, local frame)
             whose brim rests on the box top. The rear-panel port field is
             what sets the box height.
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
_hw = _repo / "hardware"

# The manifold trays' own modules: the junction column's aim is solved in
# bag_circuit_tray, and the tee poses below stand on the same elbow rolls the
# tray STEPs are built with.
_VM = _hw / "printed-parts" / "valve-manifold"
for _p in (_hw / "scripts", _repo / "tools", _hw / "reference" / "beduan-solenoid",
           _VM / "single-tray", _VM / "bag-circuit-tray", _VM / "source-select-tray",
           _VM / "nozzle-gate-tray"):
    sys.path.insert(0, str(_p))
import bag_circuit_tray as _bag          # noqa: E402
import source_select_tray as _src        # noqa: E402
import nozzle_gate_tray as _noz          # noqa: E402


# --- Source STEPs ---------------------------------------------------------
FOAM_ASSEMBLY = _hw / "printed-parts" / "cold-core" / "foam-assembly" / "foam-assembly.step"
COMP_SHROUD   = _hw / "cut-parts" / "compressor-shroud" / "compressor-shroud.step"
SOURCE_SELECT = _hw / "printed-parts" / "valve-manifold" / "source-select-tray" / "source-select-assembly.step"
BAG_CIRCUIT   = _hw / "printed-parts" / "valve-manifold" / "bag-circuit-tray" / "bag-circuit-assembly.step"
NOZZLE_GATE   = _hw / "printed-parts" / "valve-manifold" / "nozzle-gate-tray" / "nozzle-gate-assembly.step"
# Kamoer KPHM400 peristaltic pump assembly — a PP0308E 90° elbow on each of its two +Y outlets.
PUMP_ASSEMBLY = _hw / "reference" / "kamoer-kphm400" / "pump-assembly.step"
# JG PP0208E union tee — the pump-inlet junctions Y-C / Y-F, tube-hung.
TEE_CONNECTOR = _hw / "reference" / "tee-connector" / "tee-connector.step"
# JG PP0308E 90° elbow — turns the bag east / nozzle-gate west ports −Y toward the dividers.
ELBOW_CONNECTOR = _hw / "reference" / "elbow-connector" / "elbow-connector.step"
# JG PP2308E two-way divider (reference/y-divider — McMaster 51055K417 stand-in) — the actual
# Y connector for the pump-discharge junctions Y-D / Y-G. A trident: one stem and two parallel
# outlets 14.7 mm apart, all three ports on the one axis.
DIVIDER_CONNECTOR = _hw / "reference" / "y-divider" / "y-divider.step"
# AC/PSU tray — wide-shallow layout (PSU turned 90°).
POWER_ASSEMBLY = _hw / "printed-parts" / "electronics" / "power-tray" / "power-assembly.step"
PCBA_ASSEMBLY  = _hw / "printed-parts" / "electronics" / "pcba-tray" / "pcba-assembly.step"
DC_DIST        = _hw / "reference" / "dc-dist-block" / "dc-dist-block.step"
MQ6_STEP       = _hw / "reference" / "mq6-gas-sensor" / "mq6-gas-sensor.step"
DERPIPE_STEP   = _hw / "reference" / "derpipe-co2-inlet" / "derpipe-co2-inlet.step"
JG_BULKHEAD    = _hw / "reference" / "jg-bulkhead-union" / "jg-bulkhead-union.step"
IEC_C14        = _hw / "reference" / "iec-c14-inlet" / "iec-c14-inlet.step"

# --- Primitive dimensions + placement anchors ----------------------------
# Condenser+fan and the SeaFlo pump are packed as primitive boxes (dimensions
# below); the rest are placement anchors — nominal dims that position the
# STEP-loaded parts against their datums.
# Condenser + fan harvested from the donor ice maker, with the donor's own
# factory filter-drier + capillary-tube subassembly brazed to its outlet and
# kept in service (hardware/reference/ice-maker/README.md "Filter-drier" — the
# small donor drier, NOT the shelf-spare Supco SUD8358): one harvested block,
# so the drier is not packed as its own solid. The block lies tipped on its
# back (a −90° turn about X): FACE_A (178, matching the compressor envelope)
# runs along Y as the front block's depth, FACE_B (151) stands as the height —
# topping out level with the compressor, so the whole column above the floor
# stratum stays open. The airflow axis rides the tip unchanged: the fan +
# finstack stack depth, calipered [56 mm](CONDENSER_AIRFLOW) combined, along X.
CONDENSER_FACE_A, CONDENSER_FACE_B, CONDENSER_AIRFLOW = 178.0, 151.0, 56.0
# The funnel's placement: its collar-rect centre in plan, plus a rotation
# about its own Z. This is the CENTRE OF THE TOP-WALL FRAME — the basin sits
# the same `hopper_funnel.brim_margin` off the display gusset, the corner pod,
# the front ledge and the cold core's band alike, so the brim reads square in
# its opening from above instead of crowding one edge. Plan area — not depth —
# carries its volume: the shallow floor (hopper_funnel.ramp_angle) and the
# centred spout's short runs keep the drain high, hanging over the pump row
# with the segment-4 fall banked in open air below it (the pumps' `clear`
# keep-out holds that drop corridor open). With the spout centred the
# rotation picks nothing; 0 keeps the frame axis-aligned. The static
# funnel (zone-c/hopper-funnel, local frame) seats with its brim underside
# on the box's outer top; enclosure.py cuts the top-wall opening from this
# same centre + the funnel's own collar dims, and asserts both the collar and
# the brim that overhangs it land inside that frame.
FUNNEL_CX, FUNNEL_CY = 193.75, 94.0
FUNNEL_ROT = 0.0
# The source-select assembly is the stack's anchor and its FLOOR: local
# origin (cell centre, valve mounting plane) in world, rotated 180° about Z,
# which keeps the plate down and the valves up while swapping its ends —
# V-A/V-B east, V-C/V-D west. Its east collets face UP, where both the lines
# that feed them arrive from: the tap-water chain off the rear bulkhead into
# V-A, and the hopper funnel's drain into V-B, a fall the height of the
# stack. Pressed aft until its tall
# walls' back faces meet the cold core's front face (the `near foam-assembly`
# rule, a declared contact); the aft-station elbow columns set how far forward
# the back pieces' Y-seam machinery must stop (enclosure _dims y_elbows). In X
# the full-width foam behind the stack pins both interior walls; the stack itself
# rides a few millimetres inboard of each — its −X outlet-elbow column (and the
# junction tees below) clear the −X wall's seam furniture, its +X elbows clear the
# +X wall — so the enclosure seam machinery runs unbroken there (no wall relief).
SRC_SEL_POS = (143.0, 135.55, 167.8)
# The bag-circuit assembly rides INVERTED on top of it — rotated 180° about Y,
# seated wall-tops-to-wall-tops on the source tray's stacking walls (a
# declared contact), both trays' walls meeting at z 227.8 — which lands each
# pump-inlet Tee's two valve ports on ONE side of the machine (V-E/V-H west,
# V-F/V-I east) and turns the west collets DOWN into the junction column and
# the east collets UP toward the pump row that discharges into them. The X
# slide puts its west elbow column on the source tray's: the two trays' elbow
# corners disagree by the junction aim's `junction_dx`, because each west
# elbow is rolled off its port axis to face the other (bag_circuit_tray
# `_junction_aim`). Y-H's bag branch faces aft toward the cold core, Y-E's
# forward; the floor stratum below stays open under the stack — the
# under-stack corridor.
_SRC_CORNER_X = _src.valve_x + (_bag.port_half + _bag.elbow_reach) * (_src._ox / _src._on)
_BAG_CORNER_X = _bag.valve_x + _bag.port_half + _bag.elbow_reach
JUNCTION_SLIDE = _SRC_CORNER_X - _BAG_CORNER_X - _bag.junction_dx
STACK_PITCH_Z = 2 * _bag.wall_top_z       # wall top to wall top, the stack contact
BAG_CIRCUIT_POS = (SRC_SEL_POS[0] - JUNCTION_SLIDE,
                   SRC_SEL_POS[1],
                   SRC_SEL_POS[2] + STACK_PITCH_Z)

# The nozzle-gate assembly (Tray 3 — V-G/V-J, every port bare) rides INVERTED
# in the pocket EAST of the bag assembly: the same 180°-about-Y hang and the
# same second story — its hanging wall tops reach the source tray's wall-top
# plane, though the source's east wall slabs (which follow its aimed valves)
# stop just outboard of them, so the tray floats in the pocket until its
# holder. The shared story lands its ports on the bag tray's own port plane,
# inner ports facing west at the bag east bank across the pocket, outer
# (nozzle-outlet) ports facing east, inset well off the +X wall (GATE_WALL_INSET)
# so their outlet elbows have room to turn aft to the rear umbilical. The X slide
# holds the gate one clearance east of the bag tray's bare V-F/V-I port tips,
# opening the pocket the discharge fittings (bag + gate outlet elbows and the
# Y-connector tees) settle into between the two banks.
TEE_BODY_CLEAR = 2.5
# The gate is anchored on its own X (it does NOT ride the bag/source slide): its
# west inner ports and outlet elbows stay put while the bag and its own outlet
# elbows translate, so the two elbow banks face across the pocket at the
# Y-connector tees hung between them.
_GATE_ANCHOR_BAG_X = 144.0 - JUNCTION_SLIDE
# The gate sits inset from the +X wall: GATE_WALL_INSET is how far its bare east
# ports (V-G-O/V-J-O, the nozzle outlets) stand off the wall, opening the pocket
# their outlet elbows turn aft into on the way to the rear umbilical. The foam
# pins the +X wall at the full interior width regardless, so this only insets the
# gate — it does not shrink the box. Bounded west by the source-select east bank
# and the bag's east discharge elbows (the scorecard's clearance floor).
GATE_WALL_INSET = 11.0
NOZZLE_GATE_POS = (_GATE_ANCHOR_BAG_X + 2.0 * _bag.port_half + _bag.tee_branch_reach
                   + _bag.tee_radius + TEE_BODY_CLEAR - GATE_WALL_INSET,
                   SRC_SEL_POS[1],
                   SRC_SEL_POS[2] + STACK_PITCH_Z)

# The pump row: both Kamoer KPHM400 assemblies (P-A west, P-B east) lying
# depth-along-X ahead of the tray stack, in ONE pose — a −90° turn about Y
# lays the depth axis west (motor at −X), then a +90° roll about X turns
# the outlet face up, so each pump's two elbows stand on its +Z face, legs
# turning west over the head, free collets facing −X at the row's crest.
# The POS tuples are the pump's local origin (base-plate bore-opening
# face, case centre) in world; the row rides at the tray stack's height,
# P-A dropped off it by the display clearance below (the row's stack ties
# are z-tight otherwise — the two lift together):
#   * P-A: head nose-in at mid-row, the segment-4 drop corridor under the
#     funnel's centred drain held open over it (the `clear hopper-funnel`
#     rule), the long body crossing the ±X wall corners well above the
#     front Z-seam's boss-pod band (which reaches ~14 mm inboard below the
#     seam), aft elbow one clearance ahead of the inverted bag tray's Y-E
#     bag branch (the `near bag-circuit-assembly` rule). It rides below P-B
#     because its FORWARD outlet elbow stands under the display housing's
#     back plane: the facet is flush to the front wall, so that plane cuts
#     down through the row's crest and the elbow drops to pass beneath it.
#   * P-B: the same pose one slot east — head at the east end, under the
#     funnel's floor — and slid forward, its aft elbow threading ahead of
#     the source-select east bank's walls (the `clear
#     source-select-assembly` rule); its row tie is the nose gap to P-A
#     (the `near pump-a` rule).
PUMP_A_POS = (89.62, 96.00, 190.31)
PUMP_B_POS = (222.50, 85.51, 192.31)

# The pump-inlet union tees (fluid topology Y-C / Y-F) hang in the junction
# column between the trays' facing west collets. Both elbows are rolled off
# their port axes to aim at each other (bag_circuit_tray `_junction_aim`), so
# the column does not stand vertical — it leans off Z, and each tee is turned
# to stand on the lean: its RUN collinear with the pair of collets it butts, so
# segments 9/10 and 19/20 are straight tube with no bend anywhere and one stub
# at each end. Its BRANCH starts perpendicular-east, then rolls about the run
# axis by JUNCTION_ROLL to swing forward (−Y), into the open band ahead of the
# pump row where its suction leg (segments 11/21) picks it up and carries it over
# pump A — a spin about the run leaves the two run ports untouched, so the
# source/bag legs stay straight. Tube-hung PTC fittings, carried by their lines:
# no tray, no holder. Every number derives from the trays' own layout, so a tray
# move carries the tees with it.
JUNCTION = {                      # tee → the (source, bag) collets its run butts
    "tee-y-c": ("VC", "VE"),
    "tee-y-f": ("VD", "VH"),
}
JUNCTION_ROLL = {                 # extra roll of a tee about its run axis: branch swung forward off the pump row
    "tee-y-c": -90.0,             # fully −Y: branch faces straight into the open band ahead of the pumps
    "tee-y-f": -55.0,             # −Y-dominant, canted east just enough to thread its run past tee-y-c
}
JUNCTION_LIFT = {                 # slide a tee's centre this far up its run toward the bag port, raising its
    "tee-y-c": 7.0,              # branch exit so the suction stem leaves gently (fluid-11 needs no sharp climb)
}


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _unit(v):
    m = math.sqrt(_dot(v, v))
    return (v[0] / m, v[1] / m, v[2] / m)


def src_collet(name):
    """A source-tray boundary collet in world: (position, outward axis). The
    tray sits 180° about Z, so local X and Y negate and local Z carries."""
    p, d = _src.boundary_collets()[name]
    return ((SRC_SEL_POS[0] - p[0], SRC_SEL_POS[1] - p[1], SRC_SEL_POS[2] + p[2]),
            (-d[0], -d[1], d[2]))


def bag_collet(name):
    """A bag-tray boundary collet in world — an outer elbow's, a bare east
    port's, or a Tee's bag branch. The tray rides inverted (180° about Y), so
    local Y carries and local X and Z negate."""
    p, d = (_bag.bag_branches() if name.startswith("Y") else _bag.boundary_collets())[name]
    return ((BAG_CIRCUIT_POS[0] - p[0], BAG_CIRCUIT_POS[1] + p[1], BAG_CIRCUIT_POS[2] - p[2]),
            (-d[0], d[1], -d[2]))


# The nozzle-gate tray is flipped a further 180° about X, in place (about its own
# centre), so the valves that hung down now stand up but the tray keeps its exact
# Z-envelope — clearing the hopper funnel above exactly as the un-flipped tray did —
# while the west inner ports drop from the top of that envelope to the bottom, into
# the discharge tees' reach. The flip axis passes through the tray centre: its Y
# centre is NOZZLE_GATE_POS[1] (the tray is symmetric there) and its Z centre is
# measured off the placed solid.
_GATE_CZ_CACHE = None


def _gate_cz():
    global _GATE_CZ_CACHE
    if _GATE_CZ_CACHE is None:
        bb = _rot(_load(NOZZLE_GATE), (0, 1, 0), 180.0).translate(NOZZLE_GATE_POS).BoundingBox()
        _GATE_CZ_CACHE = (bb.zmin + bb.zmax) / 2.0
    return _GATE_CZ_CACHE


def noz_collet(name):
    """A nozzle-gate-tray bare port collet in world: (position, outward axis) —
    `VG-I`/`VJ-I` the inner (tee-side) ports facing west, `VG-O`/`VJ-O` the outer
    (nozzle-outlet) ports facing east. The tray rides inverted (180° about Y) then
    flipped 180° about X in place: local X negates (the inversion), local Y and Z
    reflect about the tray centre (NOZZLE_GATE_POS[1], `_gate_cz()`)."""
    p, d = _noz.port_collets()[name]
    return ((NOZZLE_GATE_POS[0] - p[0], NOZZLE_GATE_POS[1] - p[1], 2.0 * _gate_cz() - (NOZZLE_GATE_POS[2] - p[2])),
            (-d[0], -d[1], d[2]))


def junction(tee):
    """A pump-inlet tee's pose: (centre, run axis, branch axis, stub). The run is the line joining
    the two collets it butts. Centred on that line the tube left over splits evenly into a stub at
    each end, less any JUNCTION_LIFT that slides the fitting up the run toward the bag port (which
    lengthens the source stub and shortens the bag one). The branch is east made perpendicular to
    that run."""
    ps, _ns = src_collet(JUNCTION[tee][0])
    pb, _nb = bag_collet(JUNCTION[tee][1])
    span = tuple(pb[i] - ps[i] for i in range(3))
    run = _unit(span)
    east = (1.0, 0.0, 0.0)
    branch = _unit(tuple(east[i] - _dot(east, run) * run[i] for i in range(3)))
    roll = JUNCTION_ROLL.get(tee, 0.0)
    if roll:
        branch = _unit(_spin(branch, run, roll))
    lift = JUNCTION_LIFT.get(tee, 0.0)
    centre = tuple((ps[i] + pb[i]) / 2.0 + lift * run[i] for i in range(3))
    return (centre, run, branch, math.sqrt(_dot(span, span)) / 2.0 - _bag.tee_run_half)


def tee_port(tee, port):
    """A pump-inlet tee's port in world: (position, outward axis). `port` is 1
    (run, facing the source), 2 (run, facing the bag) or 3 (the branch, facing
    its pump) — the fluid topology's own numbering for Y-C / Y-F."""
    centre, run, branch, _stub = junction(tee)
    axis, reach = {1: (tuple(-c for c in run), _bag.tee_run_half),
                   2: (run, _bag.tee_run_half),
                   3: (branch, _bag.tee_branch_reach)}[port]
    return tuple(centre[i] + reach * axis[i] for i in range(3)), axis

# Front block (Zones C/D) Y depth — the cold core (Zone A) seats behind it.
# With the floor parts raised clear of the seam lip, the cold core pulls in to
# just behind the condenser (the deepest front part — the tipped donor block's
# CONDENSER_FACE_A now runs as depth), leaving only a small gap ahead of the
# cold core.
FRONT_DEPTH = 182.0
# The whole boss chain — head counterbore + pin body + heat-set + cap, less the
# wall the counterbore sinks into — reaches this far inboard of a side wall, and
# so does the corner post carrying it. The ±X walls therefore stand this far off
# the COLD CORE rather than against it: the core spans the interior wall to wall
# and floor to its cap, so a wall on its face leaves the seam machinery nowhere
# to go, and it is the core that sets the box width. enclosure.py reads this as
# the side-wall standoff. Front floor content set against a side wall is inset
# the same, to clear the ribs.
SIDE_RIB_INSET = 14.0
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
# Vertical gap between a stratum's tallest part and the parts seated above it.
STACK_GAP = 2.5

# --- Electronics shelf + rear-panel ports -----------------------------------
# The shelf lies flat on the foam-cap top in the front half of the band
# above the cold core — the rear-wall port bodies reach ~28–35 mm forward
# into the band's rear half, and the shelf may not stand under them (the
# assembly check intersects the real bodies). The shelf parts also stay
# inset off the ±X walls (the Z-seam lip band hugs the walls at the
# foam-top level, and the corner-boss chains reach ~14 in), and clear of
# the CO2 top entry at (141.5, 199.8), which stays in open air.
# Every external connection penetrates the REAR wall (back_wall_ports
# below), in the band above the cold core (the foam tops out at ~263; the
# rear Z-seam lip band tops out at ~279) — their bodies hang in the band's
# open rear half. enclosure.py cuts the holes into the back pieces;
# panel_bodies() seats the receptacle / bulkhead bodies through them. Hole
# inventory and specs: ../back-panel/README.md.
PORT_BULKHEAD_D = 18.0        # JG 1/4" bulkhead panel hole (clears the Ø17.14 barrel)
PORT_C14_W, PORT_C14_H = 28.5, 25.5   # C14 through-body 27.5 wide, z −10.2/+12.2 about
                                      # its axis (measured off the reference STEP) +
                                      # clearance; the 30.5-wide flange seats proud on
                                      # the outer face
# The panel-clamping NUT / flange footprints are far wider than the through-holes,
# so the cluster is spaced to the NUTS (not the holes) or the real hardware fouls.
# Measured off the reference STEPs: JG bulkhead nut 22.86 sq (jg-bulkhead-union),
# C14 flange 30.5 x 23.5 (iec-c14-inlet).
PORT_NUT_D = 22.86           # JG bulkhead nut, across the panel face (measured)
PORT_C14_FLANGE_H = 23.5     # C14 flange height across the panel face (measured)
PORT_NUT_GAP = 7.0           # clear gap between adjacent bulkhead nuts (the margin)
UMBILICAL_Z_FLOOR = 281.0    # lowest bulkhead-nut edge: the rear Z-seam lip band
                             # tops out at z_joint_back + lip_len (~279) on the back wall
# Rear-wall stations, left to right: the C14 on the power assembly's column
# (its cordage drops the rear wall and runs forward over the foam top to
# the AC hub), then the tap-water bulkhead, then the umbilical triangle —
# every body hangs in the band's open rear half, behind the shelf row.
UMBILICAL_X = 210.0          # triangle column center
WATER_BACK_X = 145.0
WATER_BACK_Z = 293.0         # nut rides just above the rear Z-seam lip band
C14_BACK_X = 90.0            # over the power assembly, mid-row
C14_BACK_Z = 295.0
# CO2 inlet — the DERPIPE 5/16"-tube PTC × 1/4" NPT M fitting on the front
# panel, front-left, NPT side facing inboard to carry its GASHER → WR1110
# chain (internal-plumbing.md §1), below the front pieces' Z-seam band; the
# chain's outlet tube runs on to the foam-cap top entry at (141.5, 172.8).
CO2_INLET_X = 46.0
CO2_INLET_Z = 234.0
CO2_HOLE_D = 14.5            # clears the DERPIPE's 1/4" NPT shank (Ø~13.7 major)
# DERPIPE_BODY_L: the outboard reach that seats the collet face proud of the
# front wall (the model's outboard face is at its Y origin).
DERPIPE_BODY_L = 17.0


# --- Colors ---------------------------------------------------------------
COLORS = {
    "foam-assembly":     cq.Color(0.55, 0.75, 0.95, 0.55),
    "compressor-shroud": cq.Color(0.60, 0.62, 0.66),
    "condenser+fan":     cq.Color(0.78, 0.55, 0.35),
    "mq6-sensor":        cq.Color(0.30, 0.45, 0.85),
    "source-select-assembly": cq.Color(0.60, 0.40, 0.70),
    "bag-circuit-assembly":   cq.Color(0.35, 0.62, 0.55),
    "nozzle-gate-assembly":   cq.Color(0.75, 0.62, 0.30),
    "pump-a":            cq.Color(0.72, 0.28, 0.30),
    "pump-b":            cq.Color(0.72, 0.28, 0.30),
    "tee-y-c":           cq.Color(0.92, 0.92, 0.92),
    "tee-y-f":           cq.Color(0.92, 0.92, 0.92),
    "y-d":               cq.Color(0.30, 0.55, 0.85),
    "y-g":               cq.Color(0.30, 0.55, 0.85),
    "elbow-y-d":         cq.Color(0.85, 0.85, 0.88),
    "elbow-y-g":         cq.Color(0.85, 0.85, 0.88),
    "elbow-bag-y-d":     cq.Color(0.85, 0.85, 0.88),
    "elbow-bag-y-g":     cq.Color(0.85, 0.85, 0.88),
    "power-tray":        cq.Color(0.80, 0.50, 0.20),
    "pcba":              cq.Color(0.15, 0.45, 0.25),
    "dc-dist":           cq.Color(0.20, 0.20, 0.22),
    # Panel bodies wear the customer wayfinding colors — blue = carb water,
    # white = tap water, red = CO2 (back-panel README + unboxing brief).
    "bulkhead-carb":     cq.Color(0.25, 0.45, 0.90),
    "bulkhead-flavor-a": cq.Color(0.20, 0.20, 0.22),
    "bulkhead-flavor-b": cq.Color(0.20, 0.20, 0.22),
    "bulkhead-water":    cq.Color(0.92, 0.92, 0.92),
    "c14-inlet":         cq.Color(0.12, 0.12, 0.14),
    "co2-inlet":         cq.Color(0.85, 0.35, 0.30),
}


def _load(path):
    return cq.importers.importStep(str(path)).val()


def _rot(shape, axis, deg):
    return shape.rotate((0, 0, 0), axis, deg)


def _spin(v, axis, deg):
    """Rodrigues: turn a vector `deg` about a unit axis through the origin."""
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    x = _cross(axis, v)
    return tuple(v[i] * c + x[i] * s + axis[i] * _dot(axis, v) * (1.0 - c) for i in range(3))


def _aim(shape, run, branch):
    """Turn a union tee — native run +Z, native branch +Y — so its run lies
    along `run` and its branch along `branch` (unit, perpendicular). Two turns:
    swing +Z onto the run, then spin about the run until the carried +Y lands
    on the branch."""
    y = (0.0, 1.0, 0.0)
    axis = _cross((0.0, 0.0, 1.0), run)
    if _dot(axis, axis) > 1e-18:
        axis = _unit(axis)
        turn = math.degrees(math.acos(max(-1.0, min(1.0, run[2]))))
        shape, y = shape.rotate((0, 0, 0), axis, turn), _spin(y, axis, turn)
    elif run[2] < 0.0:
        shape = shape.rotate((0, 0, 0), (0, 1, 0), 180.0)
    spin = math.degrees(math.atan2(_dot(_cross(y, branch), run), _dot(y, branch)))
    return shape.rotate((0, 0, 0), run, spin)


def _flip_x_in_place(shape):
    """Rotate a placed solid 180° about the X axis through its own bbox centre —
    a flip that keeps its exact position/envelope, only turning it top-to-bottom."""
    bb = shape.BoundingBox()
    cy, cz = (bb.ymin + bb.ymax) / 2.0, (bb.zmin + bb.zmax) / 2.0
    return shape.rotate((0.0, cy, cz), (1.0, cy, cz), 180.0)


def _place_elbow(shape, port_pos, port_dir, free_dir, stub=2.0):
    """A 90° elbow butting a port (world pos, outward `port_dir`): one collet faces
    back into the port (stub off it), the free leg runs along `free_dir` (⊥ port_dir).
    Native elbow collets are +Y (butt) and +Z (free), so `_aim` places it."""
    butt = tuple(-c for c in port_dir)
    reach = tuple(port_pos[i] + (stub + _bag.elbow_reach) * port_dir[i] for i in range(3))
    return _aim(shape, free_dir, butt).translate(reach)


def _elbow_free_port(collet, free_dir, stub=2.0):
    """The world position of the free (empty) port of an elbow placed by `_place_elbow`
    on `collet` (a (pos, outward-dir) pair) with the given free direction."""
    port_pos, port_dir = collet
    corner = tuple(port_pos[i] + (stub + _bag.elbow_reach) * port_dir[i] for i in range(3))
    return tuple(corner[i] + _bag.elbow_reach * free_dir[i] for i in range(3))


# ── Pump-discharge junctions Y-D / Y-G ───────────────────────────────────────────────────────
# Each pump merges a flavor's two sources — its bag valve and its nozzle-gate valve — through a
# JG PP2308E two-way divider (the `y-divider`), then feeds its pump. The netlist is DIAGONAL
# because the two trays seat a flavor's valves on opposite rows: Y-D (flavor A → pump A) joins
# bag V-F and nozzle V-G; Y-G (flavor B → pump B) joins bag V-I and nozzle V-J.
#
# The four turn-elbows sit at the corners of a rectangle in the Y-Z plane — the bag ports high
# (z≈277), the nozzle ports low (z≈242) — and the diagonal netlist runs two CROSSING tubes across
# it. Each divider is placed by hand over the pump row (DISCHARGE_DIV) and aimed so its two parallel
# outlets face back at the mean of the two elbow CORNERS it receives (`_divider_out_sep`); each elbow
# then aims its free leg straight at the outlet it feeds (`elbow_free_dir`) — mating face to mating
# face — plus a hand-set upward LIFT (DISCHARGE_LIFT) for the two long crossing legs, so they leave
# climbing and clear the near flavor's fitting instead of driving through it. Soft LLDPE takes up the
# residual: straight where it can be, gently bent where a run has to step over a fitting (_lines.py).
# The dividers' stems point −out (≈−Y) at the pump discharge they'll later take (segments 12/22,
# unauthored).
DIV_HALF     = 19.25                          # divider stem/outlet reach from centre (off the STEP)
DIV_OUTLET_Y = 7.35                           # each outlet's offset from the divider axis
ELBOW_STUB   = 2.0                            # tube between a valve port and its turn elbow

DISCHARGE_ELBOW = {                           # turn elbow → (tray, bare valve-port key it turns)
    "elbow-bag-y-d": ("bag", "VF"),
    "elbow-y-d":     ("noz", "VJ-I"),
    "elbow-bag-y-g": ("bag", "VI"),
    "elbow-y-g":     ("noz", "VG-I"),
}
DISCHARGE_NET = {                             # divider → (bag elbow → upper outlet 2, noz elbow → lower outlet 3)
    "y-d": ("elbow-bag-y-d", "elbow-y-g"),
    "y-g": ("elbow-bag-y-g", "elbow-y-d"),
}
# Each turn elbow's free leg first AIMS at the outlet it feeds (in the Y-Z plane ⊥ its ±X valve
# axis — so the mating faces point at each other and the run leaves nearly straight), then tilts UP
# by DISCHARGE_LIFT[name]°. The lift is 0 for a short leg that shoots straight into its outlet, and
# positive for a long crossing leg that must climb OVER the near flavor's fitting before it drops
# into its outlet — the gentle over-the-top the diagonal netlist needs.
DISCHARGE_LIFT = {
    "elbow-bag-y-d":  0.0,                     # short leg → y-d, straight in
    "elbow-y-d":      0.0,                     # short leg → y-g, straight in
    "elbow-bag-y-g": 15.0,                     # long leg → y-g, climbs over elbow-bag-y-d
    "elbow-y-g":     22.0,                     # long leg → y-d, climbs over elbow-y-d
}
# Divider → centre, over the pump row, aimed at its elbows. Both ride LOW in the pump-row band —
# their crowns tucked under the hopper funnel's basin floor with room to spare above, so the
# channel-A suction leg (fluid-11) can cross OVER them on its way from tee-y-c to pump B's inlet
# without driving through their bodies or the funnel. y-g drops furthest (fluid-11 crosses right
# over its crown); y-d rides a touch higher so its own body keeps clear of pump B just below it.
DISCHARGE_DIV = {
    "y-d": (214.0, 58.0, 267.5),
    "y-g": (186.0, 54.0, 266.0),
}
DISCHARGE_YAW = {                             # extra Z-turn of a divider: stem toward its pump, outlets the same off their elbows
    "y-d": 16.0,
}


def _discharge_collet(name):
    kind, key = DISCHARGE_ELBOW[name]
    return bag_collet(key) if kind == "bag" else noz_collet(key)


def _perp(v, ax):
    """Component of v perpendicular to unit axis `ax`."""
    d = _dot(v, ax)
    return tuple(v[i] - d * ax[i] for i in range(3))


def _elbow_corner(collet, stub=ELBOW_STUB):
    """The elbow's turn centre: `stub` + one reach out along the valve port, where the free leg
    pivots. Independent of the elbow's roll."""
    pos, d = collet
    return tuple(pos[i] + (stub + _bag.elbow_reach) * d[i] for i in range(3))


def _elbow_outlet(name):
    """The (divider, port) an elbow feeds — the bag elbow → upper outlet 2, the nozzle elbow → lower
    outlet 3."""
    for div, (be, ne) in DISCHARGE_NET.items():
        if name == be:
            return div, 2
        if name == ne:
            return div, 3
    raise KeyError(name)


def elbow_free_dir(name):
    """A discharge elbow's free-leg direction: aim the free leg (in the Y-Z plane ⊥ its ±X valve
    axis) straight at the OUTLET it feeds — so a short leg is one straight tube, mating face to mating
    face — then tilt it up by DISCHARGE_LIFT[name]° (a rotation in that Y-Z plane, toward +Z). Lift 0
    stays aimed at the outlet; a positive lift makes a long crossing leg climb before it drops in."""
    corner = _elbow_corner(_discharge_collet(name))
    div, port = _elbow_outlet(name)
    target = divider_port(div, port)[0]
    d = tuple(target[i] - corner[i] for i in range(3))
    base = _unit((0.0, d[1], d[2]))                    # point the free leg at the outlet (Y-Z only)
    th = math.radians(DISCHARGE_LIFT[name])
    c, s = math.cos(th), math.sin(th)
    return (0.0, base[1] * c + base[2] * s, -base[1] * s + base[2] * c)   # tilt up toward +Z


def elbow_free_pose(name):
    """A discharge elbow's free (empty) port in world: (position, outward axis) — where its tube
    to the divider leaves."""
    free = elbow_free_dir(name)
    return _elbow_free_port(_discharge_collet(name), free, ELBOW_STUB), free


def _divider_out_sep(name):
    """Aim divider `name`: its outlets face `out` — from the centre toward the mean of the two elbow
    CORNERS it receives — and split along `sep`, the vertical ⊥ out (so the upper outlet takes the
    high bag leg, the lower the low nozzle leg). The centres sit far enough apart on X that this aim
    only leans each trident modestly toward the shared cluster without the two bodies meeting; and
    because the outlet face looks straight back at the cluster, each elbow can aim its free leg right
    into its outlet. Aimed at the CORNERS (fixed, independent of the elbow rolls that aim back at
    these outlets — so there is no circular solve). Stem faces −out (−Y) at the pump."""
    centre = DISCHARGE_DIV[name]
    be, ne = DISCHARGE_NET[name]
    cb = _elbow_corner(_discharge_collet(be))
    cn = _elbow_corner(_discharge_collet(ne))
    mean = tuple((cb[i] + cn[i]) / 2.0 for i in range(3))
    out = _unit(tuple(mean[i] - centre[i] for i in range(3)))
    yaw = DISCHARGE_YAW.get(name, 0.0)
    if yaw:
        th = math.radians(yaw)
        c, s = math.cos(th), math.sin(th)
        out = _unit((out[0] * c - out[1] * s, out[0] * s + out[1] * c, out[2]))
    sep = _unit(_perp((0.0, 0.0, 1.0), out))
    return out, sep


def _place_divider(shape, name):
    """Divider `name` at its centre, aimed by `_divider_out_sep`: outlets face `out`, stem −out,
    outlets split ±DIV_OUTLET_Y along `sep`. Native long axis +Z (stem) / −Z (outlets), outlets
    offset ±Y — `_aim` maps native +Z onto −out and native +Y onto sep."""
    out, sep = _divider_out_sep(name)
    return _aim(shape, tuple(-c for c in out), sep).translate(DISCHARGE_DIV[name])


def divider_port(name, port):
    """A discharge divider's port in world: (position, outward axis). `port` is 1 (stem, −out at
    the pump), 2 (upper outlet, +sep — the bag leg) or 3 (lower outlet, −sep — the gate leg)."""
    c = DISCHARGE_DIV[name]
    out, sep = _divider_out_sep(name)
    if port == 1:
        return tuple(c[i] - DIV_HALF * out[i] for i in range(3)), tuple(-x for x in out)
    s = DIV_OUTLET_Y if port == 2 else -DIV_OUTLET_Y
    pos = tuple(c[i] + DIV_HALF * out[i] + s * sep[i] for i in range(3))
    return pos, out


# ── Pump-discharge outlet elbow re-aim ───────────────────────────────────────────────────────
# PUMP_OUTLET_AIM re-rolls a pump's discharge outlet elbow about its vertical port axis to the
# free-leg heading its stem run leaves along. pump-a aims east at y-g; pump-b aims northwest at
# y-d's yawed stem, so segment 12 leaves straight at the divider.
PUMP_ELBOW_REACH = 19.56                          # outlet elbow free-leg: collet face to bend corner
_PUMP_OUTLET_BASE = {                             # as-placed outlet collet CENTRE: (pos, free-leg dir)
    "pump-a": ((98.56, 32.50, 278.17), (-1.0, 0.0, 0.0)),
    "pump-b": ((231.44, 22.01, 278.17), (-1.0, 0.0, 0.0)),
}
PUMP_OUTLET_AIM = {                               # re-rolled free-leg heading (horizontal); absent = as placed
    "pump-a": (0.97, -0.22, 0.0),
    "pump-b": (-0.847, 0.532, 0.0),
}


def _pump_outlet_corner(name):
    """The outlet elbow's bend corner: one free-leg reach back from the collet, on the vertical
    axis the elbow rolls about."""
    pos, d = _PUMP_OUTLET_BASE[name]
    return tuple(pos[i] - PUMP_ELBOW_REACH * d[i] for i in range(3))


def pump_outlet_pose(name):
    """A pump's discharge outlet collet in world: (position, outward axis) — where segment 12/22
    leaves. Re-rolled to PUMP_OUTLET_AIM[name] where present, else as placed."""
    base_pos, base_d = _PUMP_OUTLET_BASE[name]
    aim = PUMP_OUTLET_AIM.get(name)
    if aim is None:
        return base_pos, base_d
    t = _unit(aim)
    corner = _pump_outlet_corner(name)
    return tuple(corner[i] + PUMP_ELBOW_REACH * t[i] for i in range(3)), t


def _pump_outlet_roll(name):
    """CCW degrees about +Z from the as-placed free leg to PUMP_OUTLET_AIM[name]."""
    _p, base_d = _PUMP_OUTLET_BASE[name]
    t = _unit(PUMP_OUTLET_AIM[name])
    return math.degrees(math.atan2(t[1], t[0]) - math.atan2(base_d[1], base_d[0]))


def _reaim_pump_outlet(shape, name):
    """Roll `name`'s discharge outlet elbow — the high-Z front sub-solid — about its vertical port
    axis to PUMP_OUTLET_AIM[name]."""
    corner = _pump_outlet_corner(name)
    roll = _pump_outlet_roll(name)
    base_pos, _d = _PUMP_OUTLET_BASE[name]
    solids = shape.Solids()

    def outlet_key(s):
        b = s.BoundingBox()
        if b.zmax < 260.0:                        # a low pump body, not an elbow
            return 1e9
        cx, cy = (b.xmin + b.xmax) / 2.0, (b.ymin + b.ymax) / 2.0
        return (cx - base_pos[0]) ** 2 + (cy - base_pos[1]) ** 2

    outlet = min(solids, key=outlet_key)
    turned = outlet.rotate((corner[0], corner[1], 0.0), (corner[0], corner[1], 1.0), roll)
    return cq.Compound.makeCompound([s for s in solids if s is not outlet] + [turned])


# ── Pump-suction inlet elbow re-aim ──────────────────────────────────────────────────────────
# PUMP_INLET_AIM re-rolls a pump's suction inlet elbow (the aft, west-facing station) about its
# vertical port axis to face the tee its suction leg comes from. pump-b stands east of the bag
# tray, with room to roll northwest at tee-y-c. pump-a's inlet stays west: the bag tray fills the
# space between it and tee-y-f, which hangs behind the tray, so fluid-21 reaches it from the west.
_PUMP_INLET_BASE = {                              # as-placed inlet collet CENTRE: (pos, free-leg dir)
    "pump-a": ((98.56, 89.50, 278.17), (-1.0, 0.0, 0.0)),
    "pump-b": ((231.44, 79.01, 278.17), (-1.0, 0.0, 0.0)),
}
PUMP_INLET_AIM = {                                # re-rolled free-leg heading (horizontal); absent = as placed
    "pump-b": (-0.940, 0.342, 0.0),
}


def _pump_inlet_corner(name):
    """The inlet elbow's bend corner: one free-leg reach back from the collet, on the vertical
    axis the elbow rolls about."""
    pos, d = _PUMP_INLET_BASE[name]
    return tuple(pos[i] - PUMP_ELBOW_REACH * d[i] for i in range(3))


def pump_inlet_pose(name):
    """A pump's suction inlet collet in world: (position, outward axis) — where segment 11/21
    closes. Re-rolled to PUMP_INLET_AIM[name] where present, else as placed."""
    base_pos, base_d = _PUMP_INLET_BASE[name]
    aim = PUMP_INLET_AIM.get(name)
    if aim is None:
        return base_pos, base_d
    t = _unit(aim)
    corner = _pump_inlet_corner(name)
    return tuple(corner[i] + PUMP_ELBOW_REACH * t[i] for i in range(3)), t


def _pump_inlet_roll(name):
    """CCW degrees about +Z from the as-placed free leg to PUMP_INLET_AIM[name]."""
    _p, base_d = _PUMP_INLET_BASE[name]
    t = _unit(PUMP_INLET_AIM[name])
    return math.degrees(math.atan2(t[1], t[0]) - math.atan2(base_d[1], base_d[0]))


def _reaim_pump_inlet(shape, name):
    """Roll `name`'s suction inlet elbow — the high-Z aft sub-solid — about its vertical port axis
    to PUMP_INLET_AIM[name]."""
    corner = _pump_inlet_corner(name)
    roll = _pump_inlet_roll(name)
    base_pos, _d = _PUMP_INLET_BASE[name]
    solids = shape.Solids()

    def inlet_key(s):
        b = s.BoundingBox()
        if b.zmax < 260.0:                        # a low pump body, not an elbow
            return 1e9
        cx, cy = (b.xmin + b.xmax) / 2.0, (b.ymin + b.ymax) / 2.0
        return (cx - base_pos[0]) ** 2 + (cy - base_pos[1]) ** 2

    inlet = min(solids, key=inlet_key)
    turned = inlet.rotate((corner[0], corner[1], 0.0), (corner[0], corner[1], 1.0), roll)
    return cq.Compound.makeCompound([s for s in solids if s is not inlet] + [turned])


def _at(shape, xmin, ymin, zmin):
    bb = shape.BoundingBox()
    return shape.translate((xmin - bb.xmin, ymin - bb.ymin, zmin - bb.zmin))


def _box(dx, dy, dz):
    return cq.Workplane("XY").box(dx, dy, dz, centered=(False, False, False)).val()


def _cyl(d, length, axis):
    """Cylinder of diameter d along a unit axis, base at the origin."""
    return cq.Solid.makeCylinder(d / 2.0, length, cq.Vector(0, 0, 0), cq.Vector(*axis))


def build():
    placed = {}

    foam = _load(FOAM_ASSEMBLY)
    fb = foam.BoundingBox()
    cold_w = fb.xlen                            # ~283 wide (shell + cap stacks, 253.4 tall)
    foam_top = fb.zlen                          # ~253.4 — the shelf floor

    # --- Zone A: cold core on the floor at the back, sitting flat on it — the
    # cavity's print-corner relief runs on the standing verticals now, so the
    # floor is square and nothing has to be cleared to seat on it. Its −Y
    # service/dispense ports face forward.
    placed["foam-assembly"] = _at(foam, 0.0, FRONT_DEPTH, 0.0)

    # --- Floor: compressor shroud front-left, condenser/fan front-right,
    # tipped on its back (airflow axis still across X): the donor block's
    # FACE_A dimension runs along Y — the front block is as deep as it — and
    # FACE_B stands as the height, level with the compressor top, leaving the
    # whole front column above the floor stratum open. Both sit one corner-rib
    # chain inboard of the cold core's own side faces, and the side walls stand a
    # further chain outboard of those — so the floor stratum keeps SIDE_RIB_INSET
    # of free width at each wall beyond what the ribs need. Closing that would
    # move refrig-1's lane with them. The donor's factory
    # filter-drier rides the condenser block (brazed to its outlet), not packed
    # separately; the MQ-6 sits on the floor between the compressor and the
    # cold core, low, where leaked isobutane pools.
    # −90° about Z so the shroud's single copper-bearing face (native −X) points +Y,
    # toward the foam/cold-core it mates to — not −Y toward the removable front shell.
    # The AC gland (native +Y) then faces +X, into the inter-part channel. Same 178×133×151
    # footprint either way (a Z-rotation of the box), so the pack is unchanged.
    comp = _rot(_load(COMP_SHROUD), (0, 0, 1), -90.0)
    placed["compressor-shroud"] = _at(comp, SIDE_RIB_INSET, 0.0, SEAM_CLEAR_LIFT)
    cond = _box(CONDENSER_AIRFLOW, CONDENSER_FACE_A, CONDENSER_FACE_B)  # the tipped block
    placed["condenser+fan"] = _at(cond, cold_w - CONDENSER_AIRFLOW - SIDE_RIB_INSET, 0.0, SEAM_CLEAR_LIFT)
    placed["mq6-sensor"] = _at(_load(MQ6_STEP), 100.0, 134.0, SEAM_CLEAR_LIFT)

    # --- Zone C: the source-select assembly (Tray 1 — V-A/V-B/Y-A/Y-B/V-C/V-D
    # on its printed tray) floors the manifold stack, spanning the front width,
    # pressed aft against the cold core's front face. Rotated 180° about Z
    # (plate down, valves up, V-A/V-B east) then translated: the assembly's own
    # frame (cell centre, valve mounting plane) is the placement datum, so
    # SRC_SEL_POS reads as its world pose. Its wall backs on the foam face are
    # a declared contact, held by the scorecard's `near foam-assembly` rule on
    # the real solids.
    placed["source-select-assembly"] = _rot(_load(SOURCE_SELECT), (0, 0, 1), 180.0).translate(SRC_SEL_POS)

    # Above it, the bag-circuit assembly (Tray 2 — V-E/V-F/V-H/V-I + Tees
    # Y-E/Y-H on the dog-bone tray, bag branches outward along ±Y through the
    # hug-wall notches) rides INVERTED: rotated 180° about Y, which puts each
    # pump-inlet Tee's pair of valve ports on one side (V-E/V-H west, in the
    # junction column over the source west bank they tee with), turns those
    # west collets DOWN into the column and the east collets UP toward the
    # pump row. Its wall tops seat on the source tray's (a declared contact);
    # the floor stratum stays open below the stack.
    placed["bag-circuit-assembly"] = _rot(_load(BAG_CIRCUIT), (0, 1, 0), 180.0).translate(BAG_CIRCUIT_POS)

    # East of it, the nozzle-gate assembly (Tray 3 — V-G/V-J, bare ports) rides
    # INVERTED, then flipped 180° about X in place (`_flip_x_in_place`): same
    # envelope, but the valves stand up and the west inner ports drop to the
    # discharge tees below (NOZZLE_GATE_POS + noz_collet).
    placed["nozzle-gate-assembly"] = _flip_x_in_place(
        _rot(_load(NOZZLE_GATE), (0, 1, 0), 180.0).translate(NOZZLE_GATE_POS))

    # Ahead of the stack, the pump row: both Kamoer assemblies in one lying
    # pose (depth west about Y, then rolled +90° about X so the elbows ride
    # the +Z face, free collets facing west at the crest), each translated
    # by its POS tuple. Each pump's two elbow stations straddle its width;
    # the funnel's spout descends between P-A's stations onto its head-top
    # clearance, and P-B's forward slide keeps its aft elbow ahead of the
    # source-select east bank.
    pump = _load(PUMP_ASSEMBLY)
    lay = _rot(_rot(pump, (0, 1, 0), -90.0), (1, 0, 0), 90.0)
    placed["pump-a"] = lay.translate(PUMP_A_POS)
    placed["pump-b"] = lay.translate(PUMP_B_POS)
    for name in PUMP_OUTLET_AIM:
        placed[name] = _reaim_pump_outlet(placed[name], name)
    for name in PUMP_INLET_AIM:
        placed[name] = _reaim_pump_inlet(placed[name], name)

    # The pump-inlet union tees, hanging in the junction column: each one
    # stands on the line between the two collets it butts (`junction`), run
    # collinear with the pair and branch swung east at its pump.
    tee = _load(TEE_CONNECTOR)
    for name in JUNCTION:
        centre, run, branch, _stub = junction(name)
        placed[name] = _aim(tee, run, branch).translate(centre)

    # Pump-discharge junctions Y-D/Y-G (topology + solved poses in the DISCHARGE_* block above).
    # A 90° elbow turns each source valve's port off the stack, rolled so its free leg aims at the
    # divider outlet it feeds; each flavor's two elbows meet at a PP2308E two-way divider — the real
    # Y connector — seated in the open air over the pump row, tilted so its two parallel outlets
    # face back at the elbows (stem −Y toward the pump discharge it will later take). Each LLDPE run
    # is then one straight tube from an elbow's free collet into a divider outlet.
    elbow = _load(ELBOW_CONNECTOR)
    for name in DISCHARGE_ELBOW:
        collet = _discharge_collet(name)
        placed[name] = _place_elbow(elbow, collet[0], collet[1], elbow_free_dir(name), ELBOW_STUB)
    divider = _load(DIVIDER_CONNECTOR)
    for name in DISCHARGE_DIV:
        placed[name] = _place_divider(divider, name)

    # --- Zone B, the band above the cold core: the electronics shelf lying
    # flat on the foam-cap top, tray/board planes horizontal, everything in
    # the band's front half (so the rear-wall port bodies hang in open air
    # behind it) — the power assembly at −X on the
    # C14's column, the PCBA beside it at +X, the DC distribution block
    # behind the power row. The power row starts behind the CO2 top entry
    # at (141.5, 199.8), which stays open to the tube dropping into it.
    shelf_z = foam_top + STACK_GAP
    placed["power-tray"] = _at(_load(POWER_ASSEMBLY), 24.0, 212.0, shelf_z)
    placed["pcba"]       = _at(_load(PCBA_ASSEMBLY), 185.0, 192.0, shelf_z)
    placed["dc-dist"]    = _at(_load(DC_DIST), 24.0, 292.0, shelf_z)

    return {n: (s, COLORS[n]) for n, s in placed.items()}


def _port_frame():
    """The shared port-band geometry: (x_lo, x_hi, y_wall) — the pack's inner
    walls the panel bodies seat against."""
    placed = build()
    bbs = [s.BoundingBox() for s, _c in placed.values()]
    x_lo = min(b.xmin for b in bbs)                # -X inner wall
    x_hi = max(b.xmax for b in bbs)                # +X inner wall
    # The back wall does NOT sit on the foam's back face — it stands one
    # REAR_STANDOFF behind it, and the panel bodies seat against the wall.
    y_wall = max(b.ymax for b in bbs) + REAR_STANDOFF
    return x_lo, x_hi, y_wall


def back_wall_ports():
    """Through-holes the rear panel needs: (kind, x, z, *size) in world
    coords — 'round' (a diameter) or 'rect' (x, z size). enclosure.py cuts
    these through the back pieces' +Y wall. Every external connection lands
    here, in the band above the cold core; the bodies hang in the band's
    open rear half. Inventory: ../back-panel/README.md."""
    d = PORT_BULKHEAD_D
    r = PORT_NUT_D / 2.0
    p = PORT_NUT_D + PORT_NUT_GAP                  # umbilical pitch: nut + margin, so nuts clear
    dz = p * (3.0 ** 0.5) / 2.0                    # triangular-cluster vertical span
    z_mid = UMBILICAL_Z_FLOOR + r + dz / 2.0       # lower nuts ride the lip band
    return [
        # Faucet umbilical: two flavor bulkheads on the lower row, the carb-water
        # (blue-ringed) bulkhead at the top vertex — the densest-three-circle
        # triangle the tube bundle packs into (back-panel README §"Bulkhead array").
        ("round", UMBILICAL_X - p / 2.0, z_mid - dz / 2.0, d),   # flavor A
        ("round", UMBILICAL_X + p / 2.0, z_mid - dz / 2.0, d),   # flavor B
        ("round", UMBILICAL_X,           z_mid + dz / 2.0, d),   # carb-water (top vertex)
        # The utility pair: the tap-water bulkhead mid-panel, and the C14
        # mains inlet over the power assembly its cordage drops to.
        ("round", WATER_BACK_X, WATER_BACK_Z, d),
        ("rect", C14_BACK_X, C14_BACK_Z, PORT_C14_W, PORT_C14_H),
    ]


def front_wall_ports():
    """Through-holes the front panel needs: (kind, x, z, *size), same shapes
    as back_wall_ports. enclosure.py cuts these through the front pieces' −Y
    wall. One port: the CO2 inlet the DERPIPE threads through."""
    return [("round", CO2_INLET_X, CO2_INLET_Z, CO2_HOLE_D)]


def panel_bodies():
    """The connector bodies seated through the enclosure walls — four JG
    bulkhead unions and the C14 receptacle on the rear panel (the faucet
    umbilical, the tap-water inlet, the mains inlet), the DERPIPE CO2 inlet
    on the front panel. Their outboard ends stand proud of the walls, and
    enclosure.py sizes the box from build()'s bbox — so they place here and
    enclosure_assembly.py adds them to the rendered assembly."""
    _x_lo, _x_hi, y_wall = _port_frame()
    y_out = y_wall + WALL                          # rear-panel outer face
    bodies = {}

    jg = _load(JG_BULKHEAD)                        # +Y outward, origin on the panel face
    names = ["bulkhead-flavor-a", "bulkhead-flavor-b", "bulkhead-carb",
             "bulkhead-water", "c14-inlet"]
    for hole in back_wall_ports():
        kind, hx, hz = hole[0], hole[1], hole[2]
        if kind == "rect":
            bodies[names.pop(0)] = _load(IEC_C14).translate((hx, y_out, hz))
        else:
            bodies[names.pop(0)] = jg.translate((hx, y_out, hz))

    # DERPIPE CO2 inlet on the front panel: 5/16" PTC collet outboard, wrench
    # hex, NPT stub through the hole reaching inboard toward the GASHER → WR1110
    # chain. The reference model's outboard collet face is at its Y origin, so
    # it seats the same outboard reach the two placeholder cylinders did.
    bodies["co2-inlet"] = _load(DERPIPE_STEP).translate(
        (CO2_INLET_X, -WALL - 2.0 - DERPIPE_BODY_L, CO2_INLET_Z))

    return {n: (s, COLORS[n]) for n, s in bodies.items()}
