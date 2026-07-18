"""Kitchen Edition enclosure contents — the core subsystems packed.

Detailed STEP imports where they exist (cold-core foam assembly — shell +
top/bottom foam-cap stacks — the compressor shroud, the source-select
assembly, the PCBA assembly, the power assembly, the DC distribution block,
the DERPIPE CO2 inlet, the MQ-6 gas sensor, the panel bulkheads + C14). One
placeholder primitive remains (condenser+fan). Not everything is packed —
deferred, tracked by the fluid topology
(/hardware/topology/fluid-topology.md) and the scorecard's connection
table, never silently dropped, while the front column settles around the
source-select assembly: the water deck (SeaFlo diaphragm pump, Multiplex
BFP, drip pan + moisture plate, the SeaFlo outlet check), the DIGITEN flow
sensor, both Kamoer pump assemblies (P-A, P-B), the CO2 chain's GASHER
check + WR1110 regulator (their front-left column is the assembly's west
bank; the chain needs a route around it), and the other three
valve-manifold trays (bag-circuit, pump-inlet tees, nozzle-gates).

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
  * carbonated-water outlet at (141.5, 155, 46.5) — the riser runs up the
    foam front face past the DIGITEN flow sensor to the rear umbilical;
  * reservoir (bag) lines at (44.5, 155, 35.5) and (238.5, 155, 35.5) —
    they climb the foam front face to the bag-circuit loops;
  * the shared slot at x 141.5 spanning z ~72–246 — both copper evaporator
    stubs (to the compressor), the water inlet (from the SeaFlo discharge),
    and the PRV vent;
  * CO2 entry down through the foam-cap top at (141.5, 172.8).

Strata, floor to ceiling:
  * Floor:   compressor shroud (front-left) + condenser/fan (front-right,
             cross-flow along X; the donor's factory filter-drier is brazed
             to its outlet, inside this harvested block), the MQ-6 on the
             floor between the compressor and the cold core (isobutane sinks).
  * Zone A:  cold core (foam assembly: bottom cap + shell + top cap) on the
             floor at the back, its −Y dispense/service ports facing
             forward.
  * Zone C (the front column's upper band): the source-select assembly —
             Tray 1 of the valve manifold (V-A, V-B, Y-A, Y-B, V-C, V-D on
             a printed tray, outlet elbows up) — hung spanning the front
             width, flipped so V-A/V-B and their up-facing inlet collets
             sit on the EAST end where the funnel's spout descends into
             the V-gap between them: the drain ends above V-B's collet
             with fall to spare for the segment-4 gravity/purge tube. Its
             wall tops stay below the display's lowest point, keeping the
             under-display wedge open as the front-left utility channel
             (display harness, CO2-chain crossing). The compressor and
             condenser tops below it are open (the deferred water deck
             returns there). Holder TBD (held).
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
# so the drier is not packed as its own solid. Two dimensions match the
# compressor envelope (face flush against the same shroud plane); the third
# (airflow axis) is the fan + finstack stack depth, calipered [56 mm](CONDENSER_AIRFLOW)
# combined.
CONDENSER_FACE_A, CONDENSER_FACE_B, CONDENSER_AIRFLOW = 178.0, 151.0, 56.0
# The funnel's placement: its collar-rect centre in plan. The static funnel
# (zone-c/hopper-funnel, local frame) seats here with its brim underside on
# the box's outer top; enclosure.py cuts the top-wall opening from this same
# centre + the funnel's own collar dims, and asserts the top-wall frame
# (display gusset, corner pod, front ledge, Y-seam lip) accommodates it.
FUNNEL_CX, FUNNEL_CY = 193.75, 63.3
# The source-select assembly's placement: local origin (cell centre, valve
# mounting plane) in world, rotated 180° about Z. The flip puts V-A/V-B —
# and their up-facing inlet collets — on the EAST end, under the funnel's
# reach, so segment 4 (the gravity drain + air-purge path, the one line
# that may not rise) falls from the funnel drain into V-B; the pressurized
# tap line (segment 2) takes the long west run to V-A instead. The height
# keeps the assembly's wall tops below the display's lowest point, holding
# the whole under-display wedge open as the front-left utility channel
# (display harness drop, CO2-chain crossing headroom) — the `clear` display
# rule and the funnel `near` rule in the scorecard pin both choices. In X
# the assembly (elbow tip to elbow tip) spans the interior wall-to-wall;
# its +X elbows stop one wall clearance short of the foam's edge.
SRC_SEL_POS = (147.0, 63.3, 200.0)

# Front block (Zones C/D) Y depth — the cold core (Zone A) seats behind it.
# With the floor parts raised clear of the seam lip, the cold core pulls in to
# just behind the condenser (the deepest front part), leaving only a small gap
# ahead of the cold core.
FRONT_DEPTH = 155.0
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
# the CO2 top entry at (141.5, 172.8), which stays in open air.
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

    # --- Floor: compressor shroud front-left, condenser/fan as a panel
    # front-right (airflow axis across X), both inset from their side walls to
    # clear the front pieces' corner ribs. The donor's factory filter-drier
    # rides the condenser block (brazed to its outlet), not packed separately;
    # the MQ-6 sits on the floor between the compressor and the cold core, low,
    # where leaked isobutane pools.
    # −90° about Z so the shroud's single copper-bearing face (native −X) points +Y,
    # toward the foam/cold-core it mates to — not −Y toward the removable front shell.
    # The AC gland (native +Y) then faces +X, into the inter-part channel. Same 178×133×151
    # footprint either way (a Z-rotation of the box), so the pack is unchanged.
    comp = _rot(_load(COMP_SHROUD), (0, 0, 1), -90.0)
    placed["compressor-shroud"] = _at(comp, SIDE_RIB_INSET, 0.0, SEAM_CLEAR_LIFT)
    cond = _box(CONDENSER_AIRFLOW, CONDENSER_FACE_B, CONDENSER_FACE_A)  # 56 x 151 x 178
    placed["condenser+fan"] = _at(cond, cold_w - CONDENSER_AIRFLOW - SIDE_RIB_INSET, 0.0, SEAM_CLEAR_LIFT)
    placed["mq6-sensor"] = _at(_load(MQ6_STEP), 100.0, 134.0, SEAM_CLEAR_LIFT)

    # --- Zone C: the source-select assembly (Tray 1 — V-A/V-B/Y-A/Y-B/V-C/V-D
    # on its printed tray, outlet elbows turned +Z), hung spanning the front
    # width in the column's upper band. Rotated 180° about Z (V-A/V-B east,
    # toward the funnel) then translated: the assembly's own frame (cell
    # centre, valve mounting plane) is the placement datum, so SRC_SEL_POS
    # reads as its world pose. The funnel descends into its east V-gap and
    # the display channel stays open above its west bank — both held by the
    # scorecard's `near`/`clear` placement rules against the real solids.
    placed["source-select-assembly"] = _rot(_load(SOURCE_SELECT), (0, 0, 1), 180.0).translate(SRC_SEL_POS)

    # --- Zone B, the band above the cold core: the electronics shelf lying
    # flat on the foam-cap top, tray/board planes horizontal, everything in
    # the band's front half (so the rear-wall port bodies hang in open air
    # behind it) — the power assembly at −X on the
    # C14's column, the PCBA beside it at +X, the DC distribution block
    # behind the power row. The power row starts behind the CO2 top entry
    # at (141.5, 172.8), which stays open to the tube dropping into it.
    shelf_z = foam_top + STACK_GAP
    placed["power-tray"] = _at(_load(POWER_ASSEMBLY), 24.0, 185.0, shelf_z)
    placed["pcba"]       = _at(_load(PCBA_ASSEMBLY), 185.0, 165.0, shelf_z)
    placed["dc-dist"]    = _at(_load(DC_DIST), 24.0, 265.0, shelf_z)

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
