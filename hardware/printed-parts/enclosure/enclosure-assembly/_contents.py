"""Kitchen Edition enclosure contents — every internal subsystem packed.

Detailed STEP imports where they exist (cold-core foam assembly — the shell
with its thin top lid — the four valve-manifold tray assemblies with their
seated valves, two pump assemblies (Kamoer pump + outlet elbows), the
compressor shroud, the PCBA assembly, the power assembly, the DC distribution
block, the DIGITEN flow sensor, the rear-panel bulkheads + C14, the CO2
coupling body). Placeholder primitives for parts that have no STEP yet
(condenser+fan, SeaFlo diaphragm pump, Multiplex backflow preventer, WR1110
regulator, GASHER check valves, drip pan + moisture sensor, MQ-6 gas sensor,
SUD8358 filter-drier).

Components only: no tubes, no wires, no mount features. enclosure_assembly.py
verifies the pack pairwise non-intersecting at every export.

The Waterdrop 15UC-UF inline filter (~Ø63 × 311 mm) mounts outside the
enclosure, inline on the customer's 1/4" LLDPE feed upstream of the
rear-panel water-inlet bulkhead (/hardware/assembly/internal-plumbing.md §2).

Coordinate frame: +X right, +Y back, +Z up. Origin at the lower-front-left
corner.

Strata, floor to ceiling (zone map: ../../README.md):
  * Floor:   compressor shroud (front-left) + condenser/fan (front-right,
             cross-flow along X), the SUD8358 filter-drier standing in the
             gap between them, the MQ-6 on the floor between the compressor
             and the cold core (isobutane sinks).
  * Zone A:  cold core (foam assembly) on the floor at the back, its −Y
             dispense/service ports facing forward.
  * Water deck (compressor top): drip pan + moisture sensor under the
             Multiplex's atmospheric-vent barb; SeaFlo lying flat behind
             them, its outlet check riding on top.
  * Right deck (condenser top): the bib-gate tray.
  * Left column (stacked over the Multiplex): the nozzle-gate tray turned
             90°, then the CO2 chain — off the front-panel coupling body's
             inboard NPT stub, GASHER check → WR1110 secondary regulator
             running +Y, left of the pumps. The DIGITEN flow sensor sits
             behind them against the cold-core front face, on the carb-water
             riser's path.
  * Zone C:  the two flavor pumps side by side directly under the funnel
             opening; the funnel's loft + spout drop into the clear column
             between them.
  * Zone B:  the two long valve trays over the cold core (bag-circuit front,
             source-select behind), above the cap-service band (the
             reservoir caps + foam-lid penetrations reach through it).
  * Termination stratum (top-back): power assembly with terminal ends facing
             the back panel, PCBA (USB-C west edge open, J10 screw throats
             facing east), DC distribution block — with the rear-panel port
             band in the back wall beside them (back_wall_ports).
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
    "bib-gate":      _VM / "bib-gate-tray"      / "bib-gate-assembly.step",
    "nozzle-gate":   _VM / "nozzle-gate-tray"   / "nozzle-gate-assembly.step",
}
# Zone-B AC/PSU shelf — wide-shallow layout (PSU turned 90°).
POWER_ASSEMBLY = _hw / "printed-parts" / "electronics" / "power-tray" / "power-assembly.step"
PCBA_ASSEMBLY  = _hw / "printed-parts" / "electronics" / "pcba-tray" / "pcba-assembly.step"
DC_DIST        = _hw / "reference" / "dc-dist-block" / "dc-dist-block.step"
DIGITEN_FLOW   = _hw / "reference" / "digiten-flow-sensor" / "digiten-flow-sensor.step"
JG_BULKHEAD    = _hw / "reference" / "jg-bulkhead-union" / "jg-bulkhead-union.step"
IEC_C14        = _hw / "reference" / "iec-c14-inlet" / "iec-c14-inlet.step"
CO2_COUPLING   = _hw / "reference" / "co2-coupling-body" / "co2-coupling-body.step"

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
# BiB syrup port bodies (hardware TBD, presumed 3/8" barb): a shank through
# the panel hole + a fatter barrel inboard.
BIB_SHANK_D = 9.4
BIB_BODY_D, BIB_BODY_L = 16.0, 28.0

# Front block (Zones C/D) Y depth — the cold core (Zone A) seats behind it.
# With the floor parts raised clear of the seam lip, the cold core pulls in to
# just behind the condenser (the deepest front part), leaving only a small gap
# ahead of the cold core.
FRONT_DEPTH = 155.0
# The front half's corner ribs reach ~12.25 mm inboard from each side wall
# (the boss chain: head counterbore + heat-set + cap). Front-bottom content set
# against a side wall is inset this much, plus a gap, to clear them.
SIDE_RIB_INSET = 14.0
# The back half's floor braces stand ~13 mm tall in the rear ±X corners; the
# cold core is lifted clear of them.
FOAM_LIFT = 14.0
# The compressor and condenser are raised one wall, clearing the front half's
# bottom seam lip so the split can pull forward past them. The box floors to a
# fixed Z=0 datum, so raising them leaves the floor in place.
SEAM_CLEAR_LIFT = 3.0
# Enclosure wall thickness (mirrors ../enclosure/enclosure.py `wall`) — used to
# seat content against the seam lip's inner face, one wall in from the inner wall.
WALL = 3.0
# Clear band above the cold-core top, under the Zone-B trays — the reservoir
# caps and the foam-lid penetrations are reached through it.
CAP_SERVICE_BAND = 38.0
# Vertical gap between a stratum's tallest part and the parts seated above it.
STACK_GAP = 2.5
# Zone-B tray tops → electronics-shelf floor. The shelf's power assembly sets
# the ceiling, so this lift also sets the rear-panel port band (tray tops →
# ceiling): 12 + the power assembly's 40.5 opens 52.5 for the umbilical nut
# triangle (22.86 nut + 25.9 triangle rise + clearance).
SHELF_LIFT = 12.0

# --- Rear-panel ports (the back-wall band ABOVE the Zone-B trays) ----------
# The appliance's external connections penetrate the back wall in the
# termination band between the Zone-B tray tops and the ceiling — above the
# tray stratum, off the cold core's clean rear (foam-shell README).
# enclosure.py cuts these holes into the back half (back_wall_ports below);
# panel_bodies() seats the receptacle / bulkhead bodies through them. Hole
# inventory and specs: ../back-panel/README.md.
#   * C14 mains inlet (rect) — the +X/+Z corner of the back face, the usual spot
#     for an appliance mains inlet (viewed from behind, facing the panel, it
#     reads top-left). Held clear of the corner cross-pin brace + the print
#     fillet, and up out of the way of the fluid lines (any condensate/leak runs
#     down, toward the water ports, away from the mains).
#   * The fluid ports condense on the -X side: the 3-tube faucet umbilical
#     (carb-water + 2 flavor) as a triangular cluster (carb-water at the top
#     vertex), the tap-water inlet, and 2 BiB syrup ports.
PORT_BULKHEAD_D = 18.0        # JG 1/4" bulkhead panel hole (clears the Ø17.14 barrel)
PORT_BIB_D = 9.525            # BiB syrup port — presumed 3/8" for a 3/8" barb (placeholder)
PORT_C14_W, PORT_C14_H = 28.5, 23.5   # C14 through-body 27.5x22.5 (measured off the
                                      # reference STEP) + 0.5/side; the 30.5-wide flange
                                      # seats proud on the outer face
# The panel-clamping NUT / flange footprints are far wider than the through-holes,
# so the cluster is spaced to the NUTS (not the holes) or the real hardware fouls.
# Measured off the reference STEPs: JG bulkhead nut 22.86 sq (jg-bulkhead-union),
# C14 flange 30.5 x 23.5 (iec-c14-inlet). BiB nut is TBD — presumed = the JG nut.
PORT_NUT_D = 22.86           # JG bulkhead nut, across the panel face (measured)
PORT_NUT_GAP = 7.0           # clear gap between adjacent bulkhead nuts (the margin)
PORT_GROUP_GAP = 9.0         # equal clear gap between the umbilical / water / BiB nut groups
PORT_CLUSTER_INSET_X = 6.0   # -X-most nut, this far off the -X inner wall
# C14 in the +X/+Z corner: center inboard/down enough that its 30.5 x 23.5 FLANGE
# (not just the cutout) clears the +X wall, the corner cross-pin brace (its -Z face
# sits ~9 mm below the ceiling), and the vertical print fillet.
C14_INSET_X = 19.5           # C14 center, this far -X (inboard) of the +X inner wall
C14_DROP_Z = 28.0            # C14 center, this far -Z (down) from the ceiling
# CO2 inlet — the CPC coupling body on the front panel, front-left, at the
# height of its inboard GASHER → WR1110 chain. The display housing's 19 mm
# facet wall runs a 45° wedge down the interior of the front wall (its
# underside crosses this height at z ≈ 304 + y); the inlet height and the
# chain's inboard stagger keep the chain under it.
CO2_INLET_X = 46.0
CO2_INLET_Z = 300.0
CO2_HOLE_D = 14.5            # clears the coupling's 1/4" NPT shank (Ø~13.7 major)


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
    "bib-gate":          cq.Color(0.62, 0.47, 0.82),
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
    "bib-port-1":        cq.Color(0.45, 0.45, 0.48),
    "bib-port-2":        cq.Color(0.45, 0.45, 0.48),
    "c14-inlet":         cq.Color(0.12, 0.12, 0.14),
    "co2-coupling":      cq.Color(0.85, 0.35, 0.30),
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
    cold_w, cold_h = fb.xlen, fb.zlen          # ~283 wide, ~216 tall (shell + thin top lid)
    foam_top = FOAM_LIFT + cold_h              # ~230 — the cap-service band starts here

    # --- Zone A: cold core, back, lifted clear of the back half's floor braces.
    # Seated behind the front block; its −Y service/dispense ports face forward.
    placed["foam-assembly"] = _at(foam, 0.0, FRONT_DEPTH, FOAM_LIFT)

    # --- Floor: compressor shroud front-left, condenser/fan as a panel
    # front-right (airflow axis across X), both inset from their side walls to
    # clear the front half's corner ribs. The filter-drier stands in the gap
    # between them; the MQ-6 sits on the floor between the compressor and the
    # cold core, low, where leaked isobutane pools.
    comp = _rot(_load(COMP_SHROUD), (0, 0, 1), 90.0)   # 178 x 133 x 151
    placed["compressor-shroud"] = _at(comp, SIDE_RIB_INSET, 0.0, SEAM_CLEAR_LIFT)
    comp_top_z = SEAM_CLEAR_LIFT + comp.BoundingBox().zlen
    cond = _box(CONDENSER_AIRFLOW, CONDENSER_FACE_B, CONDENSER_FACE_A)  # 56 x 151 x 178
    placed["condenser+fan"] = _at(cond, cold_w - CONDENSER_AIRFLOW - SIDE_RIB_INSET, 0.0, SEAM_CLEAR_LIFT)
    cond_top_z = SEAM_CLEAR_LIFT + CONDENSER_FACE_A
    placed["filter-drier"] = _at(_cyl(DRIER_D, DRIER_L, (0, 0, 1)), 193.0, 8.0, SEAM_CLEAR_LIFT)
    placed["mq6-sensor"] = _at(_box(MQ6_X, MQ6_Y, MQ6_Z), 100.0, 134.0, SEAM_CLEAR_LIFT)

    # --- Water deck, on the compressor top: the drip pan + moisture sensor at
    # the front edge, the Multiplex over the pan with its vent barb reaching
    # down into it, the SeaFlo lying flat behind them against the cold-core
    # front (suction from the Multiplex outlet, discharge up to the cold-core
    # top), and the water-path GASHER check riding on the SeaFlo's top.
    placed["drip-pan"] = _at(_drip_pan(), SIDE_RIB_INSET, 3.0, comp_top_z)
    placed["moisture-sensor"] = _at(_box(MOIST_X, MOIST_Y, MOIST_Z), 55.0, 30.0, comp_top_z + PAN_FLOOR)
    placed["multiplex"] = _at(_multiplex(), 25.0, 21.0, comp_top_z + PAN_Z - 14.0)
    sf_w, sf_d, sf_h = SEAFLO_DIMS                      # [75 x 60 x 175](SEAFLO_DIMS)
    seaflo = _box(sf_h, sf_w, sf_d)                    # 175 x 75 x 60, long axis along X
    placed["seaflo-pump"] = _at(seaflo, SIDE_RIB_INSET, 79.0, comp_top_z + 0.5)
    seaflo_top = comp_top_z + 0.5 + sf_d
    placed["gasher-water"] = _at(_cyl(GASHER_D, GASHER_L, (0, 1, 0)), 100.0, 84.0, seaflo_top)

    # --- Right deck, on the condenser top: the bib-gate tray (the funnel
    # spout's landing zone). The nozzle-gate tray turns 90° and rides the
    # left column instead, above the Multiplex and under the CO2 chain.
    placed["bib-gate"]    = _at(_load(TRAY_STEPS["bib-gate"]), 154.0, 0.0, cond_top_z + SEAM_CLEAR_LIFT)
    placed["nozzle-gate"] = _at(_rot(_load(TRAY_STEPS["nozzle-gate"]), (0, 0, 1), 90.0),
                                15.0, 0.0, 218.0)
    right_deck_top = cond_top_z + SEAM_CLEAR_LIFT + 63.0

    # --- Zone C: the two flavor pumps side by side directly under the funnel
    # opening, seated above the right-deck trays. hopper_funnel.py necks its
    # spout to the tallest content under its mouth (the pump tops, read live)
    # and its loft + spout tube drop into the column between the two pumps —
    # the pump spacing keeps that column clear.
    pump_z = right_deck_top + STACK_GAP
    pa1 = _rot(_load(PUMP_ASSEMBLY), (1, 0, 0), 90.0)  # depth axis along Y, elbows up
    pa2 = _rot(_load(PUMP_ASSEMBLY), (1, 0, 0), 90.0)
    placed["pump-assembly-1"] = _at(pa1, 95.0, 4.0, pump_z)
    placed["pump-assembly-2"] = _at(pa2, 206.0, 4.0, pump_z)

    # --- CO2 chain, front-left: the coupling body's inboard NPT stub carries
    # the GASHER check, then the WR1110 secondary regulator, running +Y in the
    # clear column left of the pumps. The DIGITEN flow sensor sits behind the
    # chain against the cold-core front face, on the carb-water riser's path
    # up to the rear-panel umbilical.
    placed["gasher-co2"] = _at(_cyl(GASHER_D, GASHER_L, (0, 1, 0)),
                               CO2_INLET_X - GASHER_D / 2.0, 14.0, CO2_INLET_Z - GASHER_D / 2.0)
    placed["wr1110"] = _at(_cyl(WR1110_D, WR1110_L, (0, 1, 0)),
                           CO2_INLET_X - WR1110_D / 2.0, 14.0 + GASHER_L + 1.0, CO2_INLET_Z - WR1110_D / 2.0)
    placed["digiten-flow"] = _at(_load(DIGITEN_FLOW), 30.0, 132.0, 250.0)

    # --- Zone B: the two long dumbbell trays tile the cold-core top in two
    # depth rows (bag-circuit front, source-select behind), above the
    # cap-service band.
    back_top_z = foam_top + CAP_SERVICE_BAND
    placed["bag-circuit"]   = _at(_load(TRAY_STEPS["bag-circuit"]),   0.0, 156.0, back_top_z)
    placed["source-select"] = _at(_load(TRAY_STEPS["source-select"]), 0.0, 233.0, back_top_z)
    zoneb_tray_top = back_top_z + 63.0

    # --- Termination stratum, top-back: the electronics shelf. The power
    # assembly rides the +X side with its terminal ends facing the back panel
    # (the C14 lands beside them); the PCBA lies to its left, USB-C west edge
    # open, J10 screw throats facing east; the DC distribution block sits
    # between them. The rear-panel bulkhead bodies land in this band's back
    # wall (back_wall_ports).
    shelf_z = zoneb_tray_top + SHELF_LIFT
    pw = _rot(_load(POWER_ASSEMBLY), (0, 0, 1), 90.0)
    placed["power-tray"] = _at(pw, 205.0, FRONT_DEPTH, shelf_z)
    placed["pcba"]       = _at(_load(PCBA_ASSEMBLY), 20.0, 225.0, shelf_z)
    placed["dc-dist"]    = _at(_load(DC_DIST), 115.0, 250.0, shelf_z)

    return {n: (s, COLORS[n]) for n, s in placed.items()}


def _port_frame():
    """The shared port-band geometry: (x_lo, x_hi, tray_top, ceil_z, y_wall).
    The band runs from the Zone-B tray tops up to the ceiling."""
    placed = build()
    bbs = [s.BoundingBox() for s, _c in placed.values()]
    tray_top = max(placed[n][0].BoundingBox().zmax for n in ("bag-circuit", "source-select"))
    ceil_z = max(b.zmax for b in bbs)              # enclosure ceiling (interior_clearance 0)
    x_lo = min(b.xmin for b in bbs)                # -X inner wall
    x_hi = max(b.xmax for b in bbs)                # +X inner wall
    y_wall = max(b.ymax for b in bbs)              # +Y inner wall
    return x_lo, x_hi, tray_top, ceil_z, y_wall


def back_wall_ports():
    """Through-holes the rear panel needs, in the termination band above the
    Zone-B trays: (kind, x, z, *size) in world coords — 'round' (a diameter)
    or 'rect' (x, z size). enclosure.py cuts these through the back half's +Y
    wall. Inventory: ../back-panel/README.md."""
    x_lo, x_hi, tray_top, ceil_z, _y = _port_frame()
    z_mid = (tray_top + ceil_z) / 2.0              # band vertical center

    d = PORT_BULKHEAD_D
    r = PORT_NUT_D / 2.0
    p = PORT_NUT_D + PORT_NUT_GAP                  # umbilical pitch: nut + margin, so nuts clear
    dz = p * (3.0 ** 0.5) / 2.0                    # triangular-cluster vertical span
    # Three nut-groups, left→right in +X, with EQUAL nut-envelope gaps between
    # them: umbilical triangle, then tap-water, then the BiB pair. Chain each
    # group's center off the previous group's +X nut edge + one PORT_GROUP_GAP.
    ux = x_lo + PORT_CLUSTER_INSET_X + r + p / 2.0        # umbilical column (flavor-A nut off the wall)
    wx = ux + p / 2.0 + r + PORT_GROUP_GAP + r            # tap-water, one group-gap past the triangle
    bx = wx + r + PORT_GROUP_GAP + r                      # BiB pair, one group-gap past the water nut
    bib_dz = (PORT_NUT_D + PORT_NUT_GAP) / 2.0            # BiB pair vertical half-sep (nut + margin)
    return [
        # Faucet umbilical: two flavor bulkheads on the lower row, the carb-water
        # (blue-ringed) bulkhead at the top vertex — the densest-three-circle
        # triangle the tube bundle packs into (back-panel README §"Bulkhead array").
        ("round", ux - p / 2.0, z_mid - dz / 2.0, d),   # flavor A
        ("round", ux + p / 2.0, z_mid - dz / 2.0, d),   # flavor B
        ("round", ux,           z_mid + dz / 2.0, d),   # carb-water (top vertex)
        # Tap-water inlet.
        ("round", wx, z_mid, d),
        # Two BiB syrup ports (3/8" barb), a vertical pair beside the water lines.
        ("round", bx, z_mid + bib_dz, PORT_BIB_D),
        ("round", bx, z_mid - bib_dz, PORT_BIB_D),
        # C14 mains inlet — the +X/+Z corner of the back face (the usual spot),
        # clear of the corner cross-pin brace and the vertical print fillet.
        ("rect", x_hi - C14_INSET_X, ceil_z - C14_DROP_Z, PORT_C14_W, PORT_C14_H),
    ]


def front_wall_ports():
    """Through-holes the front panel needs: (kind, x, z, *size), same shapes
    as back_wall_ports. enclosure.py cuts these through the front half's −Y
    wall. One port: the CO2 inlet the coupling body threads through."""
    return [("round", CO2_INLET_X, CO2_INLET_Z, CO2_HOLE_D)]


def panel_bodies():
    """The connector bodies seated through the enclosure walls — four JG
    bulkhead unions + two BiB barrels + the C14 receptacle on the rear panel
    (at the back_wall_ports coordinates), the CPC CO2 coupling body on the
    front panel. Their outboard ends stand proud of the walls, and enclosure.py
    sizes the box from build()'s bbox — so they place here and
    enclosure_assembly.py adds them to the rendered assembly."""
    _x_lo, _x_hi, _tt, _ceil, y_wall = _port_frame()
    y_out = y_wall + WALL                          # rear-panel outer face
    bodies = {}

    jg = _load(JG_BULKHEAD)                        # +Y outward, origin on the panel face
    umb_names = ["bulkhead-flavor-a", "bulkhead-flavor-b", "bulkhead-carb"]
    bib_n = 0
    for hole in back_wall_ports():
        kind, hx, hz = hole[0], hole[1], hole[2]
        if kind == "rect":
            # C14 flange seated on the panel's outer face, body through the hole.
            bodies["c14-inlet"] = _load(IEC_C14).translate((hx, y_out, hz))
        elif hole[3] == PORT_BULKHEAD_D:
            name = umb_names.pop(0) if umb_names else "bulkhead-water"
            bodies[name] = jg.translate((hx, y_out, hz))
        else:
            bib_n += 1
            shank = _cyl(BIB_SHANK_D, WALL + 12.0, (0, 1, 0)).translate(
                (hx, y_out - WALL - 2.0, hz))
            body = _cyl(BIB_BODY_D, BIB_BODY_L, (0, 1, 0)).translate(
                (hx, y_out - WALL - BIB_BODY_L, hz))
            bodies[f"bib-port-{bib_n}"] = shank.fuse(body)

    # CO2 coupling on the front panel: mouth facing −Y (outward), mounting
    # plane (the back face of its hex) on the panel's outer face, NPT stub
    # reaching inboard toward the GASHER → WR1110 chain.
    co2 = _rot(_load(CO2_COUPLING), (0, 0, 1), 180.0)
    bodies["co2-coupling"] = co2.translate((CO2_INLET_X, -WALL, CO2_INLET_Z))

    return {n: (s, COLORS[n]) for n, s in bodies.items()}
