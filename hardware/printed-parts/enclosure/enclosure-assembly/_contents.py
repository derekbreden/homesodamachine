"""Kitchen Edition enclosure contents — the core subsystems packed.

Detailed STEP imports where they exist (cold-core foam assembly — shell +
top/bottom foam-cap stacks — the compressor shroud, the source-select
assembly, the bag-circuit assembly, both Kamoer pump assemblies, the PCBA
assembly, the power assembly, the DC distribution block, the DERPIPE CO2
inlet, the MQ-6 gas sensor, the panel bulkheads + C14). One placeholder
primitive remains (condenser+fan). Not everything is packed — deferred,
tracked by the fluid topology (/hardware/topology/fluid-topology.md) and
the scorecard's connection table, never silently dropped, while the front
column settles around the tray stack and the pump row: the water deck
(SeaFlo diaphragm pump, Multiplex BFP, drip pan + moisture plate, the
SeaFlo outlet check), the DIGITEN flow sensor, the CO2 chain's GASHER
check + WR1110 regulator, and the other two valve-manifold trays
(pump-inlet tees, nozzle-gates).

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
             tray, outlet elbows up, V-A/V-B east) spanning the front
             width with its tall walls' backs on the foam's front face,
             its floor resting on the bag-circuit assembly (Tray 2:
             V-E/V-F/V-H/V-I + Tees Y-E/Y-H, outlet elbows up, bag
             branches out ±Y) one 63 mm tray pitch below, whose own floor
             rides one stack gap over the floor stratum. Ahead of the
             stack, the PUMP ROW: both Kamoer KPHM400 assemblies lying
             depth-along-X, motors outboard, heads nose-to-nose at the
             interior's x centre, flush outlet ports facing aft at the
             stack — the row seated one wall above the front Z-seam plane
             (crossing the wall corners above the seam's boss-pod band)
             and capped under the funnel's descending spout. The funnel
             drain hangs over the row's inter-pump gap, 1.1 above the
             V-B-I collet plane far to its aft-east — segment 4's
             gravity/purge fall is that 1.1 (unresolved tension). Holders
             TBD (held).
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

from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
_hw = _repo / "hardware"


# --- Source STEPs ---------------------------------------------------------
FOAM_ASSEMBLY = _hw / "printed-parts" / "cold-core" / "foam-assembly" / "foam-assembly.step"
COMP_SHROUD   = _hw / "cut-parts" / "compressor-shroud" / "compressor-shroud.step"
SOURCE_SELECT = _hw / "printed-parts" / "valve-manifold" / "source-select-tray" / "source-select-assembly.step"
BAG_CIRCUIT   = _hw / "printed-parts" / "valve-manifold" / "bag-circuit-tray" / "bag-circuit-assembly.step"
# Kamoer KPHM400 peristaltic pump, its two +Y outlet ports flush (no fittings).
PUMP_ASSEMBLY = _hw / "reference" / "kamoer-kphm400" / "pump-assembly.step"
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
# about its own Z — the rectangular collar seats the opening either way, so
# the rotation picks which side the spout descends. At 180° the spout drops
# WEST of centre, descending ahead of the tray stack to cap the pump row
# (the pumps' `clear` keep-out holds its fall corridor open), and the ramp
# rises eastward. The static funnel (zone-c/hopper-funnel, local frame)
# seats with its brim underside on the box's outer top; enclosure.py cuts
# the top-wall opening from this same centre + the funnel's own collar
# dims, and asserts the top-wall frame (display gusset, corner pod, front
# ledge, Y-seam lip) accommodates it.
FUNNEL_CX, FUNNEL_CY = 193.75, 63.3
FUNNEL_ROT = 180.0
# The source-select assembly's placement: local origin (cell centre, valve
# mounting plane) in world, rotated 180° about Z. The flip puts V-A/V-B —
# and their up-facing inlet collets — on the EAST end, V-C/V-D west; the
# pressurized tap line (segment 2) takes the long west run to V-A. Pressed
# aft until its tall walls' back faces meet the cold core's front face
# (the scorecard's `near foam-assembly` rule, a declared contact) — the
# dog-bone's central pinch leaves the foam's mid-face slot ports
# breathing room — at the height the stack sets from below: its floor on
# the bag tray's walls, the bag tray's floor riding just over the floor
# stratum. In X the assembly (elbow tip to elbow tip) spans the interior
# wall-to-wall; its +X elbows stop one wall clearance short of the foam's
# edge.
SRC_SEL_POS = (147.0, 135.55, 223.8)
# The bag-circuit assembly's placement: local origin (cell centre, valve
# mounting plane) in world, unrotated — the manifold's designed stack, one
# tray pitch (bag_circuit_tray stack_pitch, the wall-top-to-floor module)
# below the source-select assembly, so the source-select tray's floor lands
# on this tray's column wall tops (the walls exist to carry it — a declared
# contact). Unrotated, Y-E's bag branch faces aft toward the cold core's
# reservoir-A port, Y-H's forward; the four outlet elbows turn up, well
# under the tray above.
BAG_CIRCUIT_POS = (SRC_SEL_POS[0], SRC_SEL_POS[1], SRC_SEL_POS[2] - 63.0)

# The pump row: both Kamoer KPHM400 assemblies (P-A west, P-B east) lying
# depth-along-X ahead of the tray stack, motors outboard, heads
# nose-to-nose about the interior's x centre with a working gap between,
# flush outlet ports facing aft (+Y) at the stack — the aft port faces
# stop one stack gap ahead of the bag tray's front columns (the `near
# bag-circuit-assembly` rule; the source-select's slanted walls above
# recede farther). The row seats one wall above the front Z-seam plane
# (enclosure.py z_joint_front), so the long bodies cross the ±X wall
# corners ABOVE the seam's boss-pod band (which reaches ~14 mm inboard
# below the seam), and its top stops under the funnel's descending spout
# (the `clear hopper-funnel` keep-out — the drain's fall corridor).
PUMP_ROW_Y = 33.2            # body front faces; the aft port faces land at +62.6
PUMP_ROW_Z = 189.0           # z_joint_front + one wall
PUMP_A_X, PUMP_B_X = 11.62, 144.5   # west ends: symmetric about x 141.5, 6 mm nose gap

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
    "pump-a":            cq.Color(0.72, 0.28, 0.30),
    "pump-b":            cq.Color(0.72, 0.28, 0.30),
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
    # on its printed tray, outlet elbows turned +Z), spanning the front width,
    # pressed aft against the cold core's front face. Rotated 180° about Z
    # (V-A/V-B east) then translated: the assembly's own frame (cell centre,
    # valve mounting plane) is the placement datum, so SRC_SEL_POS reads as
    # its world pose. Its wall backs on the foam face are a declared contact,
    # held by the scorecard's `near foam-assembly` rule on the real solids.
    placed["source-select-assembly"] = _rot(_load(SOURCE_SELECT), (0, 0, 1), 180.0).translate(SRC_SEL_POS)

    # One tray pitch below it, the bag-circuit assembly (Tray 2 — V-E/V-F/
    # V-H/V-I + Tees Y-E/Y-H on the dog-bone tray, outlet elbows turned +Z,
    # bag branches outward along ±Y through the hug-wall notches): the
    # manifold's designed stack — the source-select tray's floor rests on
    # this tray's column wall tops (a declared contact), and the floor
    # stratum below stays one stack gap open under its own floor.
    placed["bag-circuit-assembly"] = _load(BAG_CIRCUIT).translate(BAG_CIRCUIT_POS)

    # Ahead of the stack, the pump row: both Kamoer assemblies lying
    # depth-along-X (a ∓90° turn about Y points each motor outboard, flush
    # +Y outlet ports still facing aft at the stack), seated at the
    # PUMP_ROW anchors. Each pump's two ports land one above the other on
    # its aft face; the funnel's spout descends over the nose gap between
    # the heads, held clear by the pumps' keep-out rule.
    pump = _load(PUMP_ASSEMBLY)
    placed["pump-a"] = _at(_rot(pump, (0, 1, 0), -90.0), PUMP_A_X, PUMP_ROW_Y, PUMP_ROW_Z)
    placed["pump-b"] = _at(_rot(pump, (0, 1, 0), 90.0), PUMP_B_X, PUMP_ROW_Y, PUMP_ROW_Z)

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
