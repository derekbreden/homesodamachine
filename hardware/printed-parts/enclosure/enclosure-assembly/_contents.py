"""Kitchen Edition enclosure contents — the core subsystems packed.

Detailed STEP imports where they exist (cold-core foam assembly — shell +
top/bottom foam-cap stacks — the compressor shroud, the source-select
assembly, the bag-circuit assembly, the nozzle-gate assembly, both Kamoer
pump assemblies, the four pump union tees, the PCBA assembly, the power
assembly, the DC distribution block, the DERPIPE CO2 inlet, the MQ-6 gas
sensor, the panel bulkheads + C14). One placeholder primitive remains
(condenser+fan). Not everything is packed — deferred, tracked by the fluid
topology (/hardware/topology/fluid-topology.md) and the scorecard's
connection table, never silently dropped, while the front column settles
around the tray stack and the pump row: the water deck (SeaFlo diaphragm
pump, Multiplex BFP, drip pan + moisture plate, the SeaFlo outlet check),
the DIGITEN flow sensor, and the CO2 chain's GASHER check + WR1110
regulator.

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
             on top of it, wall-top to wall-top, its bag branches out ±Y;
             and the nozzle-gate assembly (Tray 3: V-G/V-J) INVERTED
             again over the bag tray's east bank, sharing its X/Y origin.
             Both lower trays' west outlet elbows are rolled off their
             port axes to face each other — the source's inward, the
             bag's outward — down one leaning line: the JUNCTION COLUMN,
             with the pump-inlet union tees standing on that line and one
             straight stub joining each collet to the tee it butts. On
             the east, the bag tray's elbows turn UP and the nozzle-gate
             tray's inlet elbows turn DOWN onto the same verticals: the
             DISCHARGE COLUMNS, each pump-discharge tee (Y-D/Y-G)
             standing run-vertical between the facing collet pair, branch
             swung at the pump outlet that will feed it, one straight
             stub at every collet. The stack floats over the floor
             stratum, leaving an open under-stack corridor for the
             manifold's cross-machine lines, and its floor clears the
             front Z-seam's lip band. Ahead of the stack, the PUMP ROW:
             both Kamoer KPHM400 assemblies lying depth-along-X in one
             pose — motors west, outlet elbows standing on the +Z faces,
             free collets facing west at the row's crest. P-A's head is
             nose-in at mid-row, its aft elbow one clearance ahead of the
             bag tray's Y-E bag branch; P-B sits one slot east and
             forward, ahead of the source-select east bank. The funnel's
             centred drain hangs over the row with the stack's whole
             height below it before segment 4 reaches V-B-I; the funnel's
             basin is content too — the HOPPER LAW (hopper_ceiling_z)
             lifts the box ceiling until its tapered underside clears the
             nozzle-gate stack standing under its aft-east quarter.
             Holders TBD (held).
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
# tray STEPs are built with. The hopper funnel's module supplies the basin's
# underside profile the hopper law reads.
_VM = _hw / "printed-parts" / "valve-manifold"
for _p in (_hw / "scripts", _repo / "tools", _hw / "reference" / "beduan-solenoid",
           _VM / "single-tray", _VM / "bag-circuit-tray", _VM / "source-select-tray",
           _VM / "nozzle-gate-tray", _hw / "printed-parts" / "zone-c" / "hopper-funnel"):
    sys.path.insert(0, str(_p))
import bag_circuit_tray as _bag          # noqa: E402
import source_select_tray as _src        # noqa: E402
import nozzle_gate_tray as _noz          # noqa: E402
import hopper_funnel as _funnel          # noqa: E402


# --- Source STEPs ---------------------------------------------------------
FOAM_ASSEMBLY = _hw / "printed-parts" / "cold-core" / "foam-assembly" / "foam-assembly.step"
COMP_SHROUD   = _hw / "cut-parts" / "compressor-shroud" / "compressor-shroud.step"
SOURCE_SELECT = _hw / "printed-parts" / "valve-manifold" / "source-select-tray" / "source-select-assembly.step"
BAG_CIRCUIT   = _hw / "printed-parts" / "valve-manifold" / "bag-circuit-tray" / "bag-circuit-assembly.step"
NOZZLE_GATE   = _hw / "printed-parts" / "valve-manifold" / "nozzle-gate-tray" / "nozzle-gate-assembly.step"
# Kamoer KPHM400 peristaltic pump, its two +Y outlet ports flush (no fittings).
PUMP_ASSEMBLY = _hw / "reference" / "kamoer-kphm400" / "pump-assembly.step"
# JG PP0208E union tee — the pump-inlet junctions Y-C / Y-F, tube-hung.
TEE_CONNECTOR = _hw / "reference" / "tee-connector" / "tee-connector.step"
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
# about its own Z. The basin runs the top-wall frame's full width AND depth
# (front ledge to the Y-seam lip band), so plan area — not depth — carries
# its volume: the shallow floor (hopper_funnel.ramp_angle) and the centred
# spout's short runs keep the drain high, hanging over the pump row with
# the segment-4 fall banked in open air below it (the pumps' `clear`
# keep-out holds that drop corridor open). With the spout centred the
# rotation picks nothing; 0 keeps the frame axis-aligned. The static
# funnel (zone-c/hopper-funnel, local frame) seats with its brim underside
# on the box's outer top; enclosure.py cuts the top-wall opening from this
# same centre + the funnel's own collar dims, and asserts the top-wall
# frame (display gusset, corner pod, front ledge, Y-seam lip) accommodates
# it.
FUNNEL_CX, FUNNEL_CY = 193.75, 76.8
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
# the assembly (elbow tip to elbow tip) spans the interior wall-to-wall; its
# +X elbows stop one wall clearance short of the foam's edge.
SRC_SEL_POS = (147.0, 135.55, 167.8)
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

# The nozzle-gate assembly (Tray 3 — V-G/V-J + four elbows) rides INVERTED
# directly over the bag tray's east bank, the same 180°-about-Y hang, sharing
# its X and Y origin: the inversion lands each inlet-elbow corner on a bag
# east elbow column, its collet facing straight DOWN, coaxial with the
# up-facing V-F-I / V-I-I collet below. Z stands the DISCHARGE COLUMN in the
# gap: bag collet, one straight stub, the pump-discharge tee's run, another
# stub, nozzle collet — every leg vertical (segments 13/17 and 23/27), no
# bend anywhere. The bag collet rides elbow_reach below its corner (the
# roll-180 up-turn), this tray's collet elbow_reach above its own (the
# roll-0 turn, inverted), so the two offsets below place the column exactly.
DISCHARGE_STUB = 2.0                          # straight tube at each column collet
_BAG_EAST_RISE = _bag.elbow_reach - _bag.port_z   # bag east collet above the bag origin
_NOZ_INLET_DROP = _bag.port_z + _bag.elbow_reach  # inlet collet below this tray's origin
NOZZLE_GATE_POS = (BAG_CIRCUIT_POS[0],
                   BAG_CIRCUIT_POS[1],
                   BAG_CIRCUIT_POS[2] + _BAG_EAST_RISE + 2.0 * DISCHARGE_STUB
                   + 2.0 * _bag.tee_run_half + _NOZ_INLET_DROP)

# The pump row: both Kamoer KPHM400 assemblies (P-A west, P-B east) lying
# depth-along-X ahead of the tray stack, in ONE pose — a −90° turn about Y
# lays the depth axis west (motor at −X), then a +90° roll about X turns
# the outlet face up, so each pump's two elbows stand on its +Z face, legs
# turning west over the head, free collets facing −X at the row's crest.
# The POS tuples are the pump's local origin (base-plate bore-opening
# face, case centre) in world; the row rides at the tray stack's height
# (the two lift together — the row's stack ties are z-tight):
#   * P-A: head nose-in at mid-row, the segment-4 drop corridor under the
#     funnel's centred drain held open over it (the `clear hopper-funnel`
#     rule), the long body crossing the ±X wall corners well above the
#     front Z-seam's boss-pod band (which reaches ~14 mm inboard below the
#     seam), aft elbow one clearance ahead of the inverted bag tray's Y-E
#     bag branch (the `near bag-circuit-assembly` rule).
#   * P-B: the same pose one slot east — head at the east end, under the
#     funnel's floor — and slid forward, its aft elbow threading ahead of
#     the source-select east bank's walls (the `clear
#     source-select-assembly` rule); its row tie is the nose gap to P-A
#     (the `near pump-a` rule).
PUMP_A_POS = (89.62, 96.00, 192.31)
PUMP_B_POS = (222.50, 85.51, 192.31)

# The pump-inlet union tees (fluid topology Y-C / Y-F) hang in the junction
# column between the trays' facing west collets. Both elbows are rolled off
# their port axes to aim at each other (bag_circuit_tray `_junction_aim`), so
# the column does not stand vertical — it leans off Z, and each tee is turned
# to stand on the lean: its RUN collinear with the pair of collets it butts, so
# segments 9/10 and 19/20 are straight tube with no bend anywhere and one stub
# at each end, and its BRANCH swung as far east as perpendicular allows, at the
# pump inlet it feeds (segments 11/21, unauthored). Tube-hung PTC fittings,
# carried by their lines: no tray, no holder. Every number derives from the
# trays' own layout, so a tray move carries the tees with it.
JUNCTION = {                      # tee → the (source, bag) collets its run butts
    "tee-y-c": ("VC", "VE"),
    "tee-y-f": ("VD", "VH"),
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
    """A bag-tray boundary collet in world — an outer elbow's, or a Tee's bag
    branch. The tray rides inverted (180° about Y), so local Y carries and
    local X and Z negate."""
    p, d = (_bag.bag_branches() if name.startswith("Y") else _bag.boundary_collets())[name]
    return ((BAG_CIRCUIT_POS[0] - p[0], BAG_CIRCUIT_POS[1] + p[1], BAG_CIRCUIT_POS[2] - p[2]),
            (-d[0], d[1], -d[2]))


def junction(tee):
    """A pump-inlet tee's pose: (centre, run axis, branch axis, stub). The run
    is the line joining the two collets it butts — the tee sits centred on it,
    so the tube left over splits evenly into a stub at each end. The branch is
    east made perpendicular to that run."""
    ps, _ns = src_collet(JUNCTION[tee][0])
    pb, _nb = bag_collet(JUNCTION[tee][1])
    span = tuple(pb[i] - ps[i] for i in range(3))
    run = _unit(span)
    east = (1.0, 0.0, 0.0)
    branch = _unit(tuple(east[i] - _dot(east, run) * run[i] for i in range(3)))
    return (tuple((ps[i] + pb[i]) / 2.0 for i in range(3)),
            run, branch, math.sqrt(_dot(span, span)) / 2.0 - _bag.tee_run_half)


def tee_port(tee, port):
    """A pump-inlet tee's port in world: (position, outward axis). `port` is 1
    (run, facing the source), 2 (run, facing the bag) or 3 (the branch, facing
    its pump) — the fluid topology's own numbering for Y-C / Y-F."""
    centre, run, branch, _stub = junction(tee)
    axis, reach = {1: (tuple(-c for c in run), _bag.tee_run_half),
                   2: (run, _bag.tee_run_half),
                   3: (branch, _bag.tee_branch_reach)}[port]
    return tuple(centre[i] + reach * axis[i] for i in range(3)), axis


def noz_collet(name):
    """A nozzle-gate-tray boundary collet in world: (position, outward axis) —
    `VG-I`/`VJ-I` the down-turned inlets over the discharge columns, `VG-O`/
    `VJ-O` the aft-turned outlets. The tray rides inverted (180° about Y),
    the same transform the bag tray's collets carry."""
    p, d = _noz.boundary_collets()[name]
    return ((NOZZLE_GATE_POS[0] - p[0], NOZZLE_GATE_POS[1] + p[1], NOZZLE_GATE_POS[2] - p[2]),
            (-d[0], d[1], -d[2]))


# The pump-discharge tees (fluid topology Y-D / Y-G) stand on the discharge
# columns: RUN vertical between the bag tray's up-facing collet (port 2, one
# stub below) and the nozzle-gate tray's down-facing collet (port 3, one stub
# above), BRANCH (port 1) horizontal at the pump outlet that will discharge
# into it (segments 12/22, unauthored), swung just far enough off that
# bearing — the shorter way — to keep its stub one clearance floor off the
# twin column's run. Tube-hung PTC fittings, carried by their lines, like the
# junction column's; every number derives from the trays' own layout. The
# pump-outlet stations here mirror the scorecard's P-A-O / P-B-O port table
# entries (asserted there), pending pump ports deriving from the pump module.
DISCHARGE = {                     # tee → (bag collet, nozzle collet, pump-outlet station)
    "tee-y-d": ("VF", "VG-I", (98.56, 36.01)),
    "tee-y-g": ("VI", "VJ-I", (231.44, 22.01)),
}


def _discharge_branch(centre, pump_xy, twin_xy):
    """The discharge tee's branch azimuth: the pump outlet's plan bearing,
    swung the least amount that holds the branch stub's nearest approach to
    the twin column's run axis at one fitting diameter plus a clearance
    floor. Returns a horizontal unit vector."""
    need = 2.0 * _bag.tee_radius + 1.3    # two fitting radii + the floor and margin
    bearing = math.atan2(pump_xy[1] - centre[1], pump_xy[0] - centre[0])
    wx, wy = twin_xy[0] - centre[0], twin_xy[1] - centre[1]

    def clear(phi):
        ux, uy = math.cos(phi), math.sin(phi)
        t = max(0.0, min(_bag.tee_branch_reach, wx * ux + wy * uy))
        return math.hypot(wx - t * ux, wy - t * uy) >= need

    if clear(bearing):
        return (math.cos(bearing), math.sin(bearing), 0.0)
    step = math.radians(0.5)
    for k in range(1, 360):
        for sgn in (+1.0, -1.0):
            phi = bearing + sgn * k * step
            if clear(phi):
                return (math.cos(phi), math.sin(phi), 0.0)
    raise ValueError("discharge branch cannot clear the twin column at any azimuth")


def discharge(tee):
    """A pump-discharge tee's pose: (centre, run axis, branch axis, stub). The
    run is the vertical between the two collets it butts — the tee centred on
    it, the leftover splitting into one stub at each end — and the branch is
    `_discharge_branch`'s swung pump bearing, made exactly perpendicular."""
    bag_name, noz_name, pump_xy = DISCHARGE[tee]
    pb, _nb = bag_collet(bag_name)
    pn, _nn = noz_collet(noz_name)
    span = tuple(pn[i] - pb[i] for i in range(3))
    run = _unit(span)
    twin = next(n for n in DISCHARGE if n != tee)
    twin_xy = bag_collet(DISCHARGE[twin][0])[0][:2]
    centre = tuple((pb[i] + pn[i]) / 2.0 for i in range(3))
    aim = _discharge_branch(centre, pump_xy, twin_xy)
    branch = _unit(tuple(aim[i] - _dot(aim, run) * run[i] for i in range(3)))
    return centre, run, branch, math.sqrt(_dot(span, span)) / 2.0 - _bag.tee_run_half


def discharge_port(tee, port):
    """A pump-discharge tee's port in world: (position, outward axis). `port`
    is 1 (the branch, facing its pump outlet), 2 (run, facing the bag collet
    below) or 3 (run, facing the nozzle-gate collet above) — the fluid
    topology's own numbering for Y-D / Y-G."""
    centre, run, branch, _stub = discharge(tee)
    axis, reach = {1: (branch, _bag.tee_branch_reach),
                   2: (tuple(-c for c in run), _bag.tee_run_half),
                   3: (run, _bag.tee_run_half)}[port]
    return tuple(centre[i] + reach * axis[i] for i in range(3)), axis


# The hopper law's clearance: how far the funnel's basin underside must stand
# above the tallest discharge-stack content beneath its plan.
HOPPER_CLEAR = 1.5


def hopper_ceiling_z(placed):
    """The interior ceiling the hopper law demands, from the placed pack. The
    funnel's brim rides the box's outer top and its basin hangs
    `hopper_funnel.underside_drop` deep across the collar plan — and the
    nozzle-gate stack stands under the basin's aft-east quarter. For every
    solid of the discharge stack, the ceiling must lift the basin's underside
    at the solid's nearest plan approach HOPPER_CLEAR above its top;
    enclosure._dims takes the max of this and its content/port terms, and the
    funnel's `clear nozzle-gate-assembly` placement rule verifies the real
    solids. Offsets are read in the funnel's own frame (FUNNEL_ROT stays 0,
    the frame axis-aligned)."""
    need = 0.0
    for name in ("nozzle-gate-assembly", *DISCHARGE):
        if name not in placed:
            continue
        for s in placed[name][0].Solids():
            b = s.BoundingBox()
            dx = 0.0 if b.xmin <= FUNNEL_CX <= b.xmax else min(
                abs(b.xmin - FUNNEL_CX), abs(b.xmax - FUNNEL_CX))
            dy = 0.0 if b.ymin <= FUNNEL_CY <= b.ymax else min(
                abs(b.ymin - FUNNEL_CY), abs(b.ymax - FUNNEL_CY))
            drop = _funnel.underside_drop(dx, dy)
            if drop > 0.0:
                need = max(need, b.zmax + drop + HOPPER_CLEAR - WALL)
    return need

# Front block (Zones C/D) Y depth — the cold core (Zone A) seats behind it.
# With the floor parts raised clear of the seam lip, the cold core pulls in to
# just behind the condenser (the deepest front part — the tipped donor block's
# CONDENSER_FACE_A now runs as depth), leaving only a small gap ahead of the
# cold core.
FRONT_DEPTH = 182.0
# The front pieces' corner ribs reach ~12.25 mm inboard from each side wall
# (the boss chain: head counterbore + heat-set + cap). Front floor content set
# against a side wall is inset this much, plus a gap, to clear them.
SIDE_RIB_INSET = 14.0
# Floor parts are raised one wall, clearing the front pieces' bottom seam lip
# so the split can pull forward past them. The box floors to a fixed Z=0
# datum, so raising them leaves the floor in place.
SEAM_CLEAR_LIFT = 3.0
# The cold core spans the full interior width, and the enclosure cavity's
# print-corner relief arcs (radius corner_round − wall = 9, on the four long
# |Y| edges) intrude past the square walls below z = 9 — the foam seats just
# above them.
FOAM_CORNER_LIFT = 9.5
# Enclosure wall thickness (mirrors ../enclosure/enclosure.py `wall`) — used to
# seat content against the seam lips' inner faces, one wall in from the walls.
WALL = 3.0
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
    "tee-y-d":           cq.Color(0.92, 0.92, 0.92),
    "tee-y-g":           cq.Color(0.92, 0.92, 0.92),
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
    foam_top = FOAM_CORNER_LIFT + fb.zlen       # ~262.9 — the shelf floor

    # --- Zone A: cold core on the floor at the back, seated above the cavity
    # corner arcs (the back pieces' cross-pin braces sit at the Z-seam, above
    # and ahead of it). Its −Y service/dispense ports face forward.
    placed["foam-assembly"] = _at(foam, 0.0, FRONT_DEPTH, FOAM_CORNER_LIFT)

    # --- Floor: compressor shroud front-left, condenser/fan front-right,
    # tipped on its back (airflow axis still across X): the donor block's
    # FACE_A dimension runs along Y — the front block is as deep as it — and
    # FACE_B stands as the height, level with the compressor top, leaving the
    # whole front column above the floor stratum open. Both inset from their
    # side walls to clear the front pieces' corner ribs. The donor's factory
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

    # Over its east bank, the nozzle-gate assembly (Tray 3 — V-G/V-J + four
    # elbows) rides INVERTED again, same hang, same X/Y origin: inlet collets
    # straight down the discharge columns onto the tees below, outlet collets
    # turned aft toward the nozzle lines. Z is the discharge column's own
    # derivation (NOZZLE_GATE_POS): collet, stub, tee run, stub, collet.
    placed["nozzle-gate-assembly"] = _rot(_load(NOZZLE_GATE), (0, 1, 0), 180.0).translate(NOZZLE_GATE_POS)

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

    # The pump union tees, tube-hung on their columns: the pump-inlet pair
    # (Y-C/Y-F) each standing on the junction column's line between the two
    # collets it butts, run collinear with the pair and branch swung east at
    # its pump; the pump-discharge pair (Y-D/Y-G) each standing run-vertical
    # on a discharge column, branch swung at its pump outlet.
    tee = _load(TEE_CONNECTOR)
    for name in JUNCTION:
        centre, run, branch, _stub = junction(name)
        placed[name] = _aim(tee, run, branch).translate(centre)
    for name in DISCHARGE:
        centre, run, branch, _stub = discharge(name)
        placed[name] = _aim(tee, run, branch).translate(centre)

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
    y_wall = max(b.ymax for b in bbs)              # +Y inner wall (the foam's back face)
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
