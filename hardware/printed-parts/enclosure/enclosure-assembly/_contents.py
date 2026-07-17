"""Kitchen Edition enclosure contents — every internal subsystem packed.

Detailed STEP imports where they exist (cold-core foam assembly — shell +
top/bottom foam-cap stacks — the three shipping valve-manifold tray
assemblies with their seated valves, two pump assemblies (Kamoer pump +
outlet elbows), the compressor shroud, the PCBA assembly, the power
assembly, the DC distribution block, the DIGITEN flow sensor, the
rear-panel bulkheads + C14). Placeholder primitives for parts that have no
STEP yet (condenser+fan, SeaFlo diaphragm pump, Multiplex backflow
preventer, WR1110 regulator, GASHER check valves, DERPIPE CO2 inlet, drip
pan + moisture sensor, MQ-6 gas sensor, SUD8358 filter-drier). The bib-gate
tray is not packed — the bag-in-box path is de-scoped from the shipping
product (its README), and the rear panel carries no BiB ports.

Components only: no tubes, no wires, no mount features. enclosure_assembly.py
verifies the pack pairwise non-intersecting at every export.

The Waterdrop 15UC-UF inline filter (~Ø63 × 311 mm) mounts outside the
enclosure, inline on the customer's 1/4" LLDPE feed upstream of the
rear-panel water-inlet bulkhead (/hardware/assembly/internal-plumbing.md §2).

Coordinate frame: +X right, +Y back, +Z up. Origin at the lower-front-left
corner. The enclosure is four printed pieces — a Y seam ahead of the cold
core and a Z seam above its foam-cap top (enclosure.py `z_joint`) — whose
lips and cross-pin pods hug the walls; the wall-adjacent insets below keep
content clear of them.

Each tray sits nearest the things its valves plumb to
(/hardware/topology/fluid-topology.md):
  * source-select (V-A tap + V-B hopper in, V-C/V-D out to the pump-inlet
    Tees) rides the foam-cap top's front row — under the funnel spout's
    drop, over the water deck where the V-A branch taps in, its outputs a
    short drop to the pump inlets ahead of it.
  * bag-circuit (V-E/V-F + V-H/V-I, the reservoir fill/return loops) rides
    the foam-cap top's back row, over the reservoir caps it plumbs.
  * nozzle-gate (V-G/V-J, pump outlets → nozzle risers) stands in the
    front-left column beside the pump outlets.

Strata, floor to ceiling:
  * Floor:   compressor shroud (front-left) + condenser/fan (front-right,
             cross-flow along X), the SUD8358 filter-drier standing in the
             gap between them, the MQ-6 on the floor between the compressor
             and the cold core (isobutane sinks).
  * Zone A:  cold core (foam assembly: bottom cap + shell + top cap) on the
             floor at the back, its −Y dispense/service ports facing
             forward.
  * Water deck (compressor top): drip pan + moisture sensor under the
             Multiplex's atmospheric-vent barb; SeaFlo lying flat behind
             them against the cold-core front, its outlet check + the
             DIGITEN flow sensor (on the carb-water riser's path) riding
             its top.
  * Front-left column: the CO2 chain — off the front-panel DERPIPE inlet's
             inboard NPT stub, GASHER check → WR1110 secondary regulator
             running +Y — with the nozzle-gate tray above it.
  * Zone C:  the two flavor pumps spanning the front width above the water
             deck, directly under the funnel opening; the funnel's loft +
             spout drop into the clear column between them.
  * Zone B:  source-select + bag-circuit rows seated on the foam-cap top.
  * Termination stratum (top-back): power assembly on the +X side, PCBA
             (USB-C west edge open, J10 screw throats facing east) and the
             DC distribution block beside it — with the rear-panel ports in
             the back wall: the umbilical triangle in the window right of
             the bag-circuit row, the tap-water inlet above the source row,
             the C14 in the +X/+Z corner.
"""

from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
_hw = _repo / "hardware"


# --- Source STEPs ---------------------------------------------------------
FOAM_ASSEMBLY = _hw / "printed-parts" / "cold-core" / "foam-assembly" / "foam-assembly.step"
COMP_SHROUD   = _hw / "cut-parts" / "compressor-shroud" / "compressor-shroud.step"
PUMP_ASSEMBLY = _hw / "reference" / "kamoer-kphm400" / "pump-assembly.step"
_VM = _hw / "printed-parts" / "valve-manifold"
TRAY_STEPS = {
    "source-select": _VM / "source-select-tray" / "source-select-assembly.step",
    "bag-circuit":   _VM / "bag-circuit-tray"   / "bag-circuit-assembly.step",
    "nozzle-gate":   _VM / "nozzle-gate-tray"   / "nozzle-gate-assembly.step",
}
# Zone-B AC/PSU shelf — wide-shallow layout (PSU turned 90°).
POWER_ASSEMBLY = _hw / "printed-parts" / "electronics" / "power-tray" / "power-assembly.step"
PCBA_ASSEMBLY  = _hw / "printed-parts" / "electronics" / "pcba-tray" / "pcba-assembly.step"
DC_DIST        = _hw / "reference" / "dc-dist-block" / "dc-dist-block.step"
DIGITEN_FLOW   = _hw / "reference" / "digiten-flow-sensor" / "digiten-flow-sensor.step"
JG_BULKHEAD    = _hw / "reference" / "jg-bulkhead-union" / "jg-bulkhead-union.step"
IEC_C14        = _hw / "reference" / "iec-c14-inlet" / "iec-c14-inlet.step"

# --- Placeholder dimensions ----------------------------------------------
# Condenser + fan harvested from the donor ice maker. Two dimensions match
# the compressor envelope (face flush against the same shroud plane); the
# third (airflow axis) is the fan + finstack stack depth, calipered [56 mm](CONDENSER_AIRFLOW)
# combined.
CONDENSER_FACE_A, CONDENSER_FACE_B, CONDENSER_AIRFLOW = 178.0, 151.0, 56.0
# SeaFlo 22-Series diaphragm pump, body only (sans mounting brackets).
SEAFLO_DIMS = (75.0, 60.0, 175.0)
# Multiplex 19-0897 ASSE 1022 backflow preventer — body along its flow axis
# plus the downward atmospheric-vent barb. Listing-photo estimate, not yet
# calipered.
MULTIPLEX_D, MULTIPLEX_L = 44.0, 112.0
MULTIPLEX_VENT_D, MULTIPLEX_VENT_L = 8.0, 10.5
# Interstate Pneumatics WR1110 fixed 90 PSI secondary regulator (1.31" hex,
# 3.19" long per its listing) and the GASHER 1/4" NPT SS check valves.
WR1110_D, WR1110_L = 33.4, 81.0
GASHER_D, GASHER_L = 22.0, 57.0
# Supco SUD8358 filter-drier body (brazed into the refrigerant loop between
# the condenser outlet and the cap tube).
DRIER_D, DRIER_L = 19.0, 95.0
# Printed drip pan under the Multiplex vent (no CAD yet) and the Shutao
# moisture-sensor pad inside it.
PAN_X, PAN_Y, PAN_Z, PAN_WALL, PAN_FLOOR = 130.0, 75.0, 22.0, 2.5, 3.0
MOIST_X, MOIST_Y, MOIST_Z = 40.0, 16.0, 8.0
# ACEIRMC MQ-6 combustible-gas sensor module.
MQ6_X, MQ6_Y, MQ6_Z = 32.0, 20.0, 22.0

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
# The Z-seam lip band hugs the walls from z_joint − wall up ~16 (lip_len +
# slip); trays on the foam-cap top are inset one lip reach + a gap off the
# ±X walls to clear it (enclosure.py `z_joint`).
TRAY_WALL_INSET = 6.5
# Vertical gap between a stratum's tallest part and the parts seated above it.
STACK_GAP = 2.5

# --- Rear-panel ports -------------------------------------------------------
# The appliance's external connections penetrate the back wall around the
# Zone-B trays — off the cold core's clean rear (foam-shell README), each in
# a window the pack leaves against the back wall. enclosure.py cuts these
# holes into the back pieces (back_wall_ports below); panel_bodies() seats
# the receptacle / bulkhead bodies through them. Hole inventory and specs:
# ../back-panel/README.md.
#   * The 3-tube faucet umbilical (carb-water + 2 flavor) as a triangular
#     cluster (carb-water at the top vertex), in the window right of the
#     bag-circuit row.
#   * The tap-water inlet above the source-select row, high on the -X side.
#   * C14 mains inlet (rect) — the +X/+Z corner of the back face, the usual
#     spot for an appliance mains inlet. Held clear of the corner cross-pin
#     brace, and up out of the way of the fluid lines (any condensate/leak
#     runs down, away from the mains).
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
PORT_NUT_GAP = 7.0           # clear gap between adjacent bulkhead nuts (the margin)
UMBILICAL_WINDOW_GAP = 3.5   # bag-row edge → flavor-A nut edge
UMBILICAL_Z_FLOOR = 281.0    # lowest bulkhead-nut edge: the rear Z-seam lip band
                             # tops out at z_joint + lip_len (~279) on the back wall
WATER_PORT_X = 25.0          # tap-water inlet center, off the -X wall
WATER_PORT_DROP = 27.0       # tap-water center, down from the ceiling
C14_INSET_X = 19.5           # C14 center, this far -X (inboard) of the +X inner wall
C14_DROP_Z = 28.0            # C14 center, down from the ceiling (clears the corner brace
                             # above it and the carb-water nut below)
# CO2 inlet — the DERPIPE 5/16"-tube PTC × 1/4" NPT M fitting on the front
# panel, front-left, NPT side facing inboard to carry its GASHER → WR1110
# chain (internal-plumbing.md §1), below the front pieces' Z-seam band.
CO2_INLET_X = 46.0
CO2_INLET_Z = 240.0
CO2_HOLE_D = 14.5            # clears the DERPIPE's 1/4" NPT shank (Ø~13.7 major)
DERPIPE_SHANK_D, DERPIPE_SHANK_L = 13.7, 18.0   # NPT stub, wall + inboard thread
DERPIPE_BODY_D, DERPIPE_BODY_L = 20.0, 18.0     # 5/16" PTC collet body, outboard


# --- Colors ---------------------------------------------------------------
COLORS = {
    "foam-assembly":     cq.Color(0.55, 0.75, 0.95, 0.55),
    "compressor-shroud": cq.Color(0.60, 0.62, 0.66),
    "condenser+fan":     cq.Color(0.78, 0.55, 0.35),
    "filter-drier":      cq.Color(0.72, 0.60, 0.45),
    "mq6-sensor":        cq.Color(0.30, 0.45, 0.85),
    "drip-pan":          cq.Color(0.90, 0.90, 0.92),
    "moisture-sensor":   cq.Color(0.25, 0.55, 0.85),
    "multiplex":         cq.Color(0.80, 0.70, 0.30),
    "seaflo-pump":       cq.Color(0.20, 0.35, 0.55),
    "gasher-water":      cq.Color(0.75, 0.75, 0.78),
    "gasher-co2":        cq.Color(0.75, 0.75, 0.78),
    "wr1110":            cq.Color(0.55, 0.58, 0.62),
    "digiten-flow":      cq.Color(0.25, 0.25, 0.28),
    "pump-assembly-1":   cq.Color(0.45, 0.45, 0.50),
    "pump-assembly-2":   cq.Color(0.55, 0.55, 0.60),
    "source-select":     cq.Color(0.45, 0.70, 0.45),
    "bag-circuit":       cq.Color(0.90, 0.66, 0.32),
    "nozzle-gate":       cq.Color(0.84, 0.42, 0.42),
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


def _drip_pan():
    """Open-top pan: outer box minus the cavity, floor PAN_FLOOR thick."""
    outer = _box(PAN_X, PAN_Y, PAN_Z)
    cavity = _box(PAN_X - 2 * PAN_WALL, PAN_Y - 2 * PAN_WALL, PAN_Z).translate(
        (PAN_WALL, PAN_WALL, PAN_FLOOR))
    return outer.cut(cavity)


def _multiplex():
    """Body cylinder along X, the atmospheric-vent barb pointing down at
    mid-body — the vent tip reaches into the drip pan below."""
    body = _cyl(MULTIPLEX_D, MULTIPLEX_L, (1, 0, 0)).translate(
        (0, 0, MULTIPLEX_D / 2.0 + MULTIPLEX_VENT_L))
    vent = _cyl(MULTIPLEX_VENT_D, MULTIPLEX_VENT_L + 5.0, (0, 0, 1)).translate(
        (MULTIPLEX_L / 2.0, 0, 0))
    return body.fuse(vent)


def build():
    placed = {}

    foam = _load(FOAM_ASSEMBLY)
    fb = foam.BoundingBox()
    cold_w = fb.xlen                            # ~283 wide (shell + cap stacks, 253.4 tall)
    foam_top = FOAM_CORNER_LIFT + fb.zlen       # ~262.9 — the Zone-B tray floor

    # --- Zone A: cold core on the floor at the back, seated above the cavity
    # corner arcs (the back pieces' cross-pin braces sit at the Z-seam, above
    # and ahead of it). Its −Y service/dispense ports face forward.
    placed["foam-assembly"] = _at(foam, 0.0, FRONT_DEPTH, FOAM_CORNER_LIFT)

    # --- Floor: compressor shroud front-left, condenser/fan as a panel
    # front-right (airflow axis across X), both inset from their side walls to
    # clear the front pieces' corner ribs. The filter-drier stands in the gap
    # between them; the MQ-6 sits on the floor between the compressor and the
    # cold core, low, where leaked isobutane pools.
    comp = _rot(_load(COMP_SHROUD), (0, 0, 1), 90.0)   # 178 x 133 x 151
    placed["compressor-shroud"] = _at(comp, SIDE_RIB_INSET, 0.0, SEAM_CLEAR_LIFT)
    comp_top_z = SEAM_CLEAR_LIFT + comp.BoundingBox().zlen
    cond = _box(CONDENSER_AIRFLOW, CONDENSER_FACE_B, CONDENSER_FACE_A)  # 56 x 151 x 178
    placed["condenser+fan"] = _at(cond, cold_w - CONDENSER_AIRFLOW - SIDE_RIB_INSET, 0.0, SEAM_CLEAR_LIFT)
    placed["filter-drier"] = _at(_cyl(DRIER_D, DRIER_L, (0, 0, 1)), 193.0, 8.0, SEAM_CLEAR_LIFT)
    placed["mq6-sensor"] = _at(_box(MQ6_X, MQ6_Y, MQ6_Z), 100.0, 134.0, SEAM_CLEAR_LIFT)

    # --- Water deck, on the compressor top: the drip pan + moisture sensor
    # along the left wall, the Multiplex over the pan with its vent barb
    # reaching down into it, the SeaFlo lying flat behind them against the
    # cold-core front (suction from the Multiplex outlet, discharge up to the
    # cold-core top). The water-path GASHER check and the DIGITEN flow sensor
    # (inline on the carb-water riser's path to the rear umbilical) ride the
    # SeaFlo's top.
    placed["drip-pan"] = _at(_drip_pan(), SIDE_RIB_INSET, 3.0, comp_top_z)
    placed["moisture-sensor"] = _at(_box(MOIST_X, MOIST_Y, MOIST_Z), 30.0, 55.0, comp_top_z + PAN_FLOOR)
    placed["multiplex"] = _at(_multiplex(), 25.0, 21.0, comp_top_z + PAN_Z - 10.0)
    sf_w, sf_d, sf_h = SEAFLO_DIMS                      # [75 x 60 x 175](SEAFLO_DIMS)
    seaflo = _box(sf_h, sf_w, sf_d)                    # 175 x 75 x 60, long axis along X
    placed["seaflo-pump"] = _at(seaflo, SIDE_RIB_INSET, 79.0, comp_top_z + 1.0)
    seaflo_top = comp_top_z + 1.0 + sf_d
    placed["gasher-water"] = _at(_cyl(GASHER_D, GASHER_L, (0, 1, 0)), 68.0, 84.0, seaflo_top)
    placed["digiten-flow"] = _at(_load(DIGITEN_FLOW), 91.0, 132.0, seaflo_top + 0.5)

    # --- CO2 chain, front-left: the DERPIPE inlet's inboard NPT stub carries
    # the GASHER check, then the WR1110 secondary regulator, running +Y over
    # the Multiplex.
    placed["gasher-co2"] = _at(_cyl(GASHER_D, GASHER_L, (0, 1, 0)),
                               CO2_INLET_X - GASHER_D / 2.0, 14.0, CO2_INLET_Z - GASHER_D / 2.0)
    placed["wr1110"] = _at(_cyl(WR1110_D, WR1110_L, (0, 1, 0)),
                           CO2_INLET_X - WR1110_D / 2.0, 14.0 + GASHER_L + 1.0, CO2_INLET_Z - WR1110_D / 2.0)

    # --- Nozzle-gate tray, turned 90°, standing over the CO2 chain beside the
    # pump outlets; its nozzle risers run up to the rear umbilical.
    placed["nozzle-gate"] = _at(_rot(_load(TRAY_STEPS["nozzle-gate"]), (0, 0, 1), 90.0),
                                14.0, 40.0, 258.5)

    # --- Zone C: the two flavor pumps spanning the front width over the water
    # deck, directly under the funnel opening. hopper_funnel.py necks its
    # spout to the tallest content under its mouth (the pump tops, read live)
    # and its loft + spout tube drop into the column between the two pumps —
    # the pump spacing keeps that column clear.
    pump_z = seaflo_top + STACK_GAP + 0.5
    pa1 = _rot(_load(PUMP_ASSEMBLY), (1, 0, 0), 90.0)  # depth axis along Y, elbows up
    pa2 = _rot(_load(PUMP_ASSEMBLY), (1, 0, 0), 90.0)
    placed["pump-assembly-1"] = _at(pa1, 91.0, 4.0, pump_z)
    placed["pump-assembly-2"] = _at(pa2, 197.0, 4.0, pump_z)

    # --- Zone B: the two long trays seated on the foam-cap top — the
    # source-select row at the front, the bag-circuit row behind it over the
    # reservoir caps — inset off the ±X walls to clear the Z-seam lip.
    tray_z = foam_top + STACK_GAP
    placed["source-select"] = _at(_load(TRAY_STEPS["source-select"]), TRAY_WALL_INSET, 160.0, tray_z)
    placed["bag-circuit"]   = _at(_load(TRAY_STEPS["bag-circuit"]),   TRAY_WALL_INSET, 256.0, tray_z)
    zoneb_tray_top = tray_z + 63.0

    # --- Termination stratum, top-back: the electronics shelf. The power
    # assembly rides the +X side with its terminal ends facing the back panel
    # (the C14 lands beside them, and the shelf's top is the ceiling); the
    # PCBA lies to its left, USB-C west edge open, J10 screw throats facing
    # east; the DC distribution block sits between them.
    shelf_z = zoneb_tray_top + STACK_GAP
    pw = _rot(_load(POWER_ASSEMBLY), (0, 0, 1), 90.0)
    placed["power-tray"] = _at(pw, 196.6, FRONT_DEPTH, shelf_z)
    placed["pcba"]       = _at(_load(PCBA_ASSEMBLY), 20.0, 225.0, shelf_z)
    placed["dc-dist"]    = _at(_load(DC_DIST), 115.0, 250.0, shelf_z)

    return {n: (s, COLORS[n]) for n, s in placed.items()}


def _port_frame():
    """The shared port-band geometry: (x_lo, x_hi, bag_xmax, tray_top, ceil_z,
    y_wall). The ports land in the back-wall windows the pack leaves open —
    right of the bag-circuit row, and above the tray tops."""
    placed = build()
    bbs = [s.BoundingBox() for s, _c in placed.values()]
    bag_xmax = placed["bag-circuit"][0].BoundingBox().xmax
    tray_top = max(placed[n][0].BoundingBox().zmax for n in ("bag-circuit", "source-select"))
    ceil_z = max(b.zmax for b in bbs)              # enclosure ceiling (interior_clearance 0)
    x_lo = min(b.xmin for b in bbs)                # -X inner wall
    x_hi = max(b.xmax for b in bbs)                # +X inner wall
    y_wall = max(b.ymax for b in bbs)              # +Y inner wall
    return x_lo, x_hi, bag_xmax, tray_top, ceil_z, y_wall


def back_wall_ports():
    """Through-holes the rear panel needs: (kind, x, z, *size) in world
    coords — 'round' (a diameter) or 'rect' (x, z size). enclosure.py cuts
    these through the back pieces' +Y wall. Inventory:
    ../back-panel/README.md."""
    _x_lo, x_hi, bag_xmax, tray_top, ceil_z, _y = _port_frame()

    d = PORT_BULKHEAD_D
    r = PORT_NUT_D / 2.0
    p = PORT_NUT_D + PORT_NUT_GAP                  # umbilical pitch: nut + margin, so nuts clear
    dz = p * (3.0 ** 0.5) / 2.0                    # triangular-cluster vertical span
    # Umbilical triangle in the window right of the bag-circuit row: flavor-A
    # nut one window-gap off the row's edge, the lower (flavor) nuts riding
    # just above the rear Z-seam lip band.
    ux = bag_xmax + UMBILICAL_WINDOW_GAP + r + p / 2.0    # umbilical column center
    z_mid = UMBILICAL_Z_FLOOR + r + dz / 2.0
    return [
        # Faucet umbilical: two flavor bulkheads on the lower row, the carb-water
        # (blue-ringed) bulkhead at the top vertex — the densest-three-circle
        # triangle the tube bundle packs into (back-panel README §"Bulkhead array").
        ("round", ux - p / 2.0, z_mid - dz / 2.0, d),   # flavor A
        ("round", ux + p / 2.0, z_mid - dz / 2.0, d),   # flavor B
        ("round", ux,           z_mid + dz / 2.0, d),   # carb-water (top vertex)
        # Tap-water inlet, high on the -X side above the source-select row.
        ("round", WATER_PORT_X, ceil_z - WATER_PORT_DROP, d),
        # C14 mains inlet — the +X/+Z corner of the back face (the usual spot),
        # clear of the corner cross-pin brace.
        ("rect", x_hi - C14_INSET_X, ceil_z - C14_DROP_Z, PORT_C14_W, PORT_C14_H),
    ]


def front_wall_ports():
    """Through-holes the front panel needs: (kind, x, z, *size), same shapes
    as back_wall_ports. enclosure.py cuts these through the front pieces' −Y
    wall. One port: the CO2 inlet the DERPIPE threads through."""
    return [("round", CO2_INLET_X, CO2_INLET_Z, CO2_HOLE_D)]


def panel_bodies():
    """The connector bodies seated through the enclosure walls — four JG
    bulkhead unions + the C14 receptacle on the rear panel (at the
    back_wall_ports coordinates), the DERPIPE CO2 inlet on the front panel.
    Their outboard ends stand proud of the walls, and enclosure.py sizes the
    box from build()'s bbox — so they place here and enclosure_assembly.py
    adds them to the rendered assembly."""
    _x_lo, _x_hi, _bx, _tt, _ceil, y_wall = _port_frame()
    y_out = y_wall + WALL                          # rear-panel outer face
    bodies = {}

    jg = _load(JG_BULKHEAD)                        # +Y outward, origin on the panel face
    umb_names = ["bulkhead-flavor-a", "bulkhead-flavor-b", "bulkhead-carb"]
    for hole in back_wall_ports():
        kind, hx, hz = hole[0], hole[1], hole[2]
        if kind == "rect":
            # C14 flange seated on the panel's outer face, body through the hole.
            bodies["c14-inlet"] = _load(IEC_C14).translate((hx, y_out, hz))
        else:
            name = umb_names.pop(0) if umb_names else "bulkhead-water"
            bodies[name] = jg.translate((hx, y_out, hz))

    # DERPIPE CO2 inlet on the front panel: 5/16" PTC collet body outboard,
    # NPT stub through the hole reaching inboard toward the GASHER → WR1110
    # chain.
    shank = _cyl(DERPIPE_SHANK_D, DERPIPE_SHANK_L, (0, 1, 0)).translate(
        (CO2_INLET_X, -WALL - 2.0, CO2_INLET_Z))
    collet = _cyl(DERPIPE_BODY_D, DERPIPE_BODY_L, (0, 1, 0)).translate(
        (CO2_INLET_X, -WALL - 2.0 - DERPIPE_BODY_L, CO2_INLET_Z))
    bodies["co2-inlet"] = shank.fuse(collet)

    return {n: (s, COLORS[n]) for n, s in bodies.items()}
