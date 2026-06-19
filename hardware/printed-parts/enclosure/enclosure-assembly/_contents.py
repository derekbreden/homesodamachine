"""Kitchen Edition enclosure contents — every internal subsystem packed.

Detailed STEP imports where they exist (cold-core foam shell, the four
valve-manifold tray assemblies with their seated valves, two pump-case
assemblies, the compressor shroud). Placeholder boxes for parts that have no
STEP yet (condenser+fan, SeaFlo diaphragm pump).

Coordinate frame: +X right, +Y back, +Z up. Origin at the lower-front-left
corner.

Layout follows the enclosure zone map (see ../../README.md), a roughly-packed
stand-in (not collision-validated):
  * Zone A (back-bottom):  cold core (foam shell), on the floor, its −Y
    dispense/service ports facing forward toward the front zones.
  * Zone D (front-bottom): compressor shroud + condenser/fan + SeaFlo pump.
  * Zone C (front-top):    the two pump cases (cartridge under the funnel).
  * Zone B (back-top):     the four valve-manifold trays, above the cold core.
"""

from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
_hw = _repo / "hardware"


# --- Source STEPs ---------------------------------------------------------
FOAM_SHELL  = _hw / "printed-parts" / "cold-core" / "foam-shell" / "foam-shell.step"
COMP_SHROUD = _hw / "cut-parts" / "compressor-shroud" / "compressor-shroud.step"
PUMP_CASE   = _hw / "printed-parts" / "flavor" / "pump-case" / "pump-case-assembly.step"
_VM = _hw / "printed-parts" / "valve-manifold"
TRAY_STEPS = {
    "source-select": _VM / "source-select-tray" / "source-select-assembly.step",
    "bag-circuit":   _VM / "bag-circuit-tray"   / "bag-circuit-assembly.step",
    "bib-gate":      _VM / "bib-gate-tray"      / "bib-gate-assembly.step",
    "nozzle-gate":   _VM / "nozzle-gate-tray"   / "nozzle-gate-assembly.step",
}

# --- Placeholder dimensions ----------------------------------------------
# Condenser + fan harvested from the donor ice maker. Two dimensions match
# the compressor envelope (face flush against the same shroud plane); the
# third (airflow axis) is the fan + finstack stack depth, calipered [56 mm](CONDENSER_AIRFLOW)
# combined.
CONDENSER_FACE_A, CONDENSER_FACE_B, CONDENSER_AIRFLOW = 178.0, 151.0, 56.0
# SeaFlo 22-Series diaphragm pump, body only (sans mounting brackets).
SEAFLO_DIMS = (75.0, 60.0, 175.0)

# Front block (Zones C/D) Y depth — the cold core (Zone A) seats behind it,
# so the cold core lands in the enclosure's back half. Sized to leave a clear
# gap between the deepest front-zone content and the cold core for the
# front↔back split joint + heatset bosses to live in.
FRONT_DEPTH = 190.0
# Vertical gap between the bottom layer (cold core + front-bottom) and the
# top layer (pump cases + trays).
LAYER_GAP = 5.0
# The front half's corner ribs reach ~12.25 mm inboard from each side wall
# (the boss chain: head counterbore + heat-set + cap). Front-bottom content set
# against a side wall is inset this much, plus a gap, to clear them.
SIDE_RIB_INSET = 14.0
# The back half's floor braces stand ~13 mm tall in the rear ±X corners; the
# cold core is lifted clear of them.
FOAM_LIFT = 14.0


# --- Colors ---------------------------------------------------------------
COLORS = {
    "foam-shell":        cq.Color(0.55, 0.75, 0.95, 0.55),
    "compressor-shroud": cq.Color(0.60, 0.62, 0.66),
    "condenser+fan":     cq.Color(0.78, 0.55, 0.35),
    "seaflo-pump":       cq.Color(0.20, 0.35, 0.55),
    "pump-case-1":       cq.Color(0.45, 0.45, 0.50),
    "pump-case-2":       cq.Color(0.55, 0.55, 0.60),
    "source-select":     cq.Color(0.45, 0.70, 0.45),
    "bag-circuit":       cq.Color(0.90, 0.66, 0.32),
    "bib-gate":          cq.Color(0.62, 0.47, 0.82),
    "nozzle-gate":       cq.Color(0.84, 0.42, 0.42),
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
    placed["compressor-shroud"] = _at(comp, SIDE_RIB_INSET, 0.0, 0.0)
    comp_top_z = comp.BoundingBox().zlen               # 151
    cond = _box(CONDENSER_AIRFLOW, CONDENSER_FACE_B, CONDENSER_FACE_A)  # 56 x 151 x 178
    placed["condenser+fan"] = _at(cond, cold_w - CONDENSER_AIRFLOW - SIDE_RIB_INSET, 0.0, 0.0)

    # --- Zone C: the pump cartridge sits low on the compressor top, two cases
    # side by side and centered, so the band above them is open to the ceiling
    # for the hopper funnel — which pours down the front edge into the pumps.
    # The SeaFlo moves to the right pocket, the open column above the condenser.
    pc1 = _cycle_xyz_to_yzx(_load(PUMP_CASE))          # 74 x 136 x 76
    pc2 = _cycle_xyz_to_yzx(_load(PUMP_CASE))
    placed["pump-case-1"] = _at(pc1, 20.0, 18.0, comp_top_z)
    placed["pump-case-2"] = _at(pc2, 98.0, 18.0, comp_top_z)
    sf_w, sf_d, sf_h = SEAFLO_DIMS                      # [75 x 60 x 175](SEAFLO_DIMS)
    seaflo = _rot(_box(sf_h, sf_w, sf_d), (0, 0, 1), 90.0)      # 75 x 175 x 60
    placed["seaflo-pump"] = _at(seaflo, 193.0, 0.0, 178.0)

    # --- Zone B: valve-manifold trays back-top above the lifted cold core,
    # nudged off the ±X corners (clear of the back half's top braces) and
    # gathered to the left so the front-right corner opens for the electronics
    # shelf. The bib-gate tray rides in the funnel reserve, behind the funnel
    # mouth over the pump backs.
    pump_top_z = comp_top_z + pc1.BoundingBox().zlen
    placed["bib-gate"]      = _at(_load(TRAY_STEPS["bib-gate"]), 20.0, 80.0, pump_top_z)
    placed["source-select"] = _at(_load(TRAY_STEPS["source-select"]), 10.0, FRONT_DEPTH, back_top_z)
    placed["bag-circuit"]   = _at(_load(TRAY_STEPS["bag-circuit"]),   10.0, FRONT_DEPTH + 97.0, back_top_z)
    placed["nozzle-gate"]   = _at(_load(TRAY_STEPS["nozzle-gate"]),  172.0, FRONT_DEPTH + 97.0, back_top_z)

    return {n: (s, COLORS[n]) for n, s in placed.items()}
