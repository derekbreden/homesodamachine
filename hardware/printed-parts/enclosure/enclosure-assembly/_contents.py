"""Kitchen Edition enclosure contents — every internal subsystem packed.

Detailed STEP imports where they exist (cold-core foam shell, the four
valve-manifold tray assemblies with their seated valves, two pump assemblies
(Kamoer pump + outlet elbows), the compressor shroud). Placeholder boxes for
parts that have no STEP yet (condenser+fan, SeaFlo diaphragm pump).

Coordinate frame: +X right, +Y back, +Z up. Origin at the lower-front-left
corner.

Layout follows the enclosure zone map (see ../../README.md), a roughly-packed
stand-in (not collision-validated):
  * Zone A (back-bottom):  cold core (foam shell), on the floor, its −Y
    dispense/service ports facing forward toward the front zones.
  * Zone D (front-bottom): compressor shroud + condenser/fan + SeaFlo pump.
  * Zone C (front-top):    the two flavor pumps (under the funnel).
  * Zone B (back-top):     the four valve-manifold trays, above the cold core.
"""

from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
_hw = _repo / "hardware"


# --- Source STEPs ---------------------------------------------------------
FOAM_SHELL    = _hw / "printed-parts" / "cold-core" / "foam-shell" / "foam-shell.step"
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

# --- Placeholder dimensions ----------------------------------------------
# Condenser + fan harvested from the donor ice maker. Two dimensions match
# the compressor envelope (face flush against the same shroud plane); the
# third (airflow axis) is the fan + finstack stack depth, calipered [56 mm](CONDENSER_AIRFLOW)
# combined.
CONDENSER_FACE_A, CONDENSER_FACE_B, CONDENSER_AIRFLOW = 178.0, 151.0, 56.0
# SeaFlo 22-Series diaphragm pump, body only (sans mounting brackets).
SEAFLO_DIMS = (75.0, 60.0, 175.0)

# Front block (Zones C/D) Y depth — the cold core (Zone A) seats behind it.
# With the floor parts raised clear of the seam lip, the cold core pulls in to
# just behind the condenser (the deepest front part), leaving only a small gap
# ahead of the cold core.
FRONT_DEPTH = 155.0
# Vertical gap between the bottom layer (cold core + front-bottom) and the
# top layer (pump assemblies + trays).
LAYER_GAP = 5.0
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

# --- Rear-panel ports (Zone B: the back wall ABOVE the cold core) ----------
# The appliance's external connections penetrate the back wall in the band above
# the cold core — the cold core's own +Y rear stays clean (foam-shell README).
# enclosure.py cuts these holes into the back half (back_wall_ports below); the
# receptacle / bulkhead BODIES that seat through them are a Zone-B packing task
# still open (the back-adjacent trays sit where the bodies land). Hole inventory
# and specs: ../back-panel/README.md.
#   * C14 mains inlet (rect) — the +X/+Z corner of the back face, the usual spot
#     for an appliance mains inlet (viewed from behind, facing the panel, it
#     reads top-left). Held clear of the corner cross-pin brace + the print
#     fillet, and up out of the way of the fluid lines (any condensate/leak runs
#     down, toward the water ports, away from the mains).
#   * The fluid ports condense on the -X side, centered in the band's height: the
#     3-tube faucet umbilical (carb-water + 2 flavor) as a triangular cluster
#     (carb-water at the top vertex), the tap-water inlet, and 2 BiB syrup ports.
PORT_BULKHEAD_D = 18.0        # JG 1/4" bulkhead panel hole (clears the Ø17.14 barrel)
PORT_BIB_D = 9.525            # BiB syrup port — presumed 3/8" for a 3/8" barb (placeholder)
PORT_C14_W, PORT_C14_H = 25.0, 19.0   # C14 body 24x18 cross-section + 0.5/side clearance
# C14 in the +X/+Z corner: center inboard/down from the +X wall / ceiling, enough
# to clear the corner cross-pin brace (its -Z face sits ~9 mm below the ceiling)
# and the vertical print fillet.
C14_INSET_X = 16.0            # C14 center, this far -X (inboard) of the +X inner wall
C14_DROP_Z = 26.0            # C14 center, this far -Z (down) from the ceiling
# Fluid-port cluster: columns measured +X from the -X inner wall, all riding the
# band's vertical center. Umbilical triangle, then tap-water, then the BiB pair.
UMBIL_COL_X = 33.0            # umbilical triangle center column
UMBIL_PITCH = 24.0           # umbilical center pitch (Ø18 hole + bulkhead-nut gap)
WATER_COL_X = 66.0           # tap-water inlet column
BIB_COL_X = 90.0             # BiB pair column
BIB_PAIR_DZ = 13.0           # BiB pair vertical half-separation


# --- Colors ---------------------------------------------------------------
COLORS = {
    "foam-shell":        cq.Color(0.55, 0.75, 0.95, 0.55),
    "compressor-shroud": cq.Color(0.60, 0.62, 0.66),
    "condenser+fan":     cq.Color(0.78, 0.55, 0.35),
    "seaflo-pump":       cq.Color(0.20, 0.35, 0.55),
    "pump-assembly-1":   cq.Color(0.45, 0.45, 0.50),
    "pump-assembly-2":   cq.Color(0.55, 0.55, 0.60),
    "source-select":     cq.Color(0.45, 0.70, 0.45),
    "bag-circuit":       cq.Color(0.90, 0.66, 0.32),
    "bib-gate":          cq.Color(0.62, 0.47, 0.82),
    "nozzle-gate":       cq.Color(0.84, 0.42, 0.42),
    "power-tray":        cq.Color(0.80, 0.50, 0.20),
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


def _cycle_xyz_to_yzx(shape):
    """Two 90 deg rotations: bbox (dx, dy, dz) -> (dy, dz, dx)."""
    return _rot(_rot(shape, (1, 0, 0), 90.0), (0, 1, 0), 90.0)


def build():
    placed = {}

    foam = _load(FOAM_SHELL)
    fb = foam.BoundingBox()
    cold_w, cold_h = fb.xlen, fb.zlen          # ~283 wide, ~213 tall
    top_z = cold_h + LAYER_GAP                  # front top-layer floor
    # The lifted cold core's top rises into the back-top tray band; the trays
    # sit just above it (a smaller gap than LAYER_GAP, to stay under the ceiling).
    back_top_z = FOAM_LIFT + cold_h + 2.0

    # --- Zone A: cold core, back, lifted clear of the back half's floor braces.
    # Seated behind the front block; its −Y service/dispense ports face forward.
    placed["foam-shell"] = _at(foam, 0.0, FRONT_DEPTH, FOAM_LIFT)

    # --- Zone D: refrigeration on the floor — compressor shroud front-left,
    # condenser/fan as a panel front-right (airflow axis across X). Both inset
    # from their side walls to clear the front half's corner ribs.
    comp = _rot(_load(COMP_SHROUD), (0, 0, 1), 90.0)   # 178 x 133 x 151
    placed["compressor-shroud"] = _at(comp, SIDE_RIB_INSET, 0.0, SEAM_CLEAR_LIFT)
    comp_top_z = SEAM_CLEAR_LIFT + comp.BoundingBox().zlen
    cond = _box(CONDENSER_AIRFLOW, CONDENSER_FACE_B, CONDENSER_FACE_A)  # 56 x 151 x 178
    placed["condenser+fan"] = _at(cond, cold_w - CONDENSER_AIRFLOW - SIDE_RIB_INSET, 0.0, SEAM_CLEAR_LIFT)
    cond_top_z = SEAM_CLEAR_LIFT + CONDENSER_FACE_A

    # --- The two flavor pumps sit on the compressor top; the SeaFlo lies flat
    # across their tops (the dead air above the pumps), its back edge against the
    # hopper funnel.
    pa1 = _rot(_load(PUMP_ASSEMBLY), (1, 0, 0), 90.0)  # depth axis along Y, elbows up
    pa2 = _rot(_load(PUMP_ASSEMBLY), (1, 0, 0), 90.0)
    placed["pump-assembly-1"] = _at(pa1, 14.0, 12.0, comp_top_z)
    placed["pump-assembly-2"] = _at(pa2, 86.0, 12.0, comp_top_z)
    pump_top_z = comp_top_z + pa1.BoundingBox().zlen
    sf_w, sf_d, sf_h = SEAFLO_DIMS                      # [75 x 60 x 175](SEAFLO_DIMS)
    seaflo = _box(sf_h, sf_w, sf_d)                    # 175 x 75 x 60, long axis along X
    placed["seaflo-pump"] = _at(seaflo, 14.0, 84.0, pump_top_z)

    # --- Valve-manifold trays, packed across the whole top with no spare layer.
    # The two long dumbbell trays tile the cold-core top in two depth rows
    # (bag-circuit front, source-select behind). The two short trays take the
    # front-right the fixed parts leave open: both sit low on the condenser-top
    # band (z = cond_top_z), front-to-back — bib-gate at the front, nozzle-gate
    # behind it — under the SeaFlo and the hollow hopper funnel, whose thin cone
    # leaves the volume around it free.
    # bag-circuit is flipped 180° about X (elbows pointing down), same footprint,
    # so its right-cluster elbows drop out of the power-tray floor band beside it.
    bag = _rot(_load(TRAY_STEPS["bag-circuit"]), (1, 0, 0), 180.0)
    placed["bag-circuit"]   = _at(bag,                                  0.0, 161.0, back_top_z)
    placed["source-select"] = _at(_load(TRAY_STEPS["source-select"]),  0.0, 238.0, back_top_z)
    placed["bib-gate"]      = _at(_load(TRAY_STEPS["bib-gate"]),      154.0,   0.0, cond_top_z)
    placed["nozzle-gate"]   = _at(_load(TRAY_STEPS["nozzle-gate"]),   164.0,  78.0, cond_top_z)

    # --- Power tray (Zone-B AC/PSU shelf), turned 90° about Z so the Mean
    # Well PSU's long axis lies along enclosure-Y. It threads the right-side
    # channel: along Y between the funnel back and source-select's front; along X
    # between bag-circuit's right elbows and the +X wall; resting at the short-tray
    # height so the PSU clears the back corner boss. Terminal ends face the back
    # panel (the C14 inlet).
    pw = _rot(_load(POWER_ASSEMBLY), (0, 0, 1), 90.0)
    placed["power-tray"]    = _at(pw, 207.0, 85.0, 244.0)

    return {n: (s, COLORS[n]) for n, s in placed.items()}


def back_wall_ports():
    """Through-holes the rear panel needs, in the Zone-B band above the cold
    core: (kind, x, z, *size) in world coords — 'round' (a diameter) or 'rect'
    (x, z size). enclosure.py cuts these through the back half's +Y wall. The
    band runs from the cold-core top up to the ceiling; every port sits inside it,
    so none breaks into the cold core's clean rear. Inventory:
    ../back-panel/README.md."""
    placed = build()
    bbs = [s.BoundingBox() for s, _c in placed.values()]
    foam_top = placed["foam-shell"][0].BoundingBox().zmax
    ceil_z = max(b.zmax for b in bbs)              # enclosure ceiling (interior_clearance 0)
    x_lo = min(b.xmin for b in bbs)                # -X inner wall
    x_hi = max(b.xmax for b in bbs)                # +X inner wall
    z_mid = (foam_top + ceil_z) / 2.0              # band vertical center

    d = PORT_BULKHEAD_D
    p = UMBIL_PITCH
    dz = p * (3.0 ** 0.5) / 2.0                    # triangular-cluster vertical span
    ux = x_lo + UMBIL_COL_X
    return [
        # Faucet umbilical: two flavor bulkheads on the lower row, the carb-water
        # (blue-ringed) bulkhead at the top vertex — the densest-three-circle
        # triangle the tube bundle packs into (back-panel README §"Bulkhead array").
        ("round", ux - p / 2.0, z_mid - dz / 2.0, d),   # flavor A
        ("round", ux + p / 2.0, z_mid - dz / 2.0, d),   # flavor B
        ("round", ux,           z_mid + dz / 2.0, d),   # carb-water (top vertex)
        # Tap-water inlet.
        ("round", x_lo + WATER_COL_X, z_mid, d),
        # Two BiB syrup ports (3/8" barb), a vertical pair beside the water lines.
        ("round", x_lo + BIB_COL_X, z_mid + BIB_PAIR_DZ, PORT_BIB_D),
        ("round", x_lo + BIB_COL_X, z_mid - BIB_PAIR_DZ, PORT_BIB_D),
        # C14 mains inlet — the +X/+Z corner of the back face (the usual spot),
        # clear of the corner cross-pin brace and the vertical print fillet.
        ("rect", x_hi - C14_INSET_X, ceil_z - C14_DROP_Z, PORT_C14_W, PORT_C14_H),
    ]
