"""Kitchen Edition enclosure contents — every internal subsystem packed.

Detailed STEP imports where they exist (cold-core foam shell, the four
valve-manifold tray assemblies with their seated valves, two pump-case
assemblies, the compressor shroud). Placeholder boxes for parts that have no
STEP yet (condenser+fan, SeaFlo diaphragm pump).

Coordinate frame: +X right, +Y back, +Z up. Origin at the lower-front-left
corner of the cold core.

Layout is a first-fit-decreasing pack on bounding-box bricks: cold core spans
the lower-front block; the compressor shroud sits behind it across the back
strip; source-select stands on its long edge beside the compressor; bag-circuit
stands vertical in the back corner; the condenser, SeaFlo, two pump cases, and
the bib-gate + nozzle-gate trays form a second layer above the cold core.
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
# third (airflow axis) is the fan + finstack stack depth, calipered 56 mm
# combined.
CONDENSER_FACE_A, CONDENSER_FACE_B, CONDENSER_AIRFLOW = 178.0, 151.0, 56.0
# SeaFlo 22-Series diaphragm pump, body only (sans mounting brackets).
SEAFLO_DIMS = (75.0, 60.0, 175.0)


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

    # Cold core — front-left, on the floor.
    placed["foam-shell"] = _at(_load(FOAM_SHELL), 0.0, 0.0, 0.0)

    # Compressor shroud — behind the cold core, rotated 90 about Z (178 x 133).
    comp = _rot(_load(COMP_SHROUD), (0, 0, 1), 90.0)
    placed["compressor-shroud"] = _at(comp, 0.0, 181.0, 0.0)

    # Source-select tray — standing on its long edge beside the compressor.
    src = _cycle_xyz_to_yzx(_load(TRAY_STEPS["source-select"]))
    placed["source-select"] = _at(src, 178.0, 181.0, 0.0)

    # Condenser + fan — above cold core, left half.
    cond = _box(CONDENSER_FACE_A, CONDENSER_FACE_B, CONDENSER_AIRFLOW)
    placed["condenser+fan"] = _at(cond, 0.0, 0.0, 213.4)

    # SeaFlo — above cold core, right of the condenser column.
    sf_dx, sf_dy, sf_dz = SEAFLO_DIMS              # 75 x 60 x 175
    placed["seaflo-pump"] = _at(_box(sf_dy, sf_dz, sf_dx), 178.0, 0.0, 213.4)

    # Pump cases — on their long sides, on top of the cold core.
    placed["pump-case-1"] = _at(_cycle_xyz_to_yzx(_load(PUMP_CASE)), 238.0, 0.0, 213.4)
    placed["pump-case-2"] = _at(_cycle_xyz_to_yzx(_load(PUMP_CASE)),   0.0, 151.0, 213.4)

    # Bag-circuit — standing vertical in the back corner.
    bag = _cycle_xyz_to_yzx(_load(TRAY_STEPS["bag-circuit"]))
    placed["bag-circuit"] = _at(bag, 178.0, 244.0, 0.0)

    # Bib-gate — flat, on top of source-select.
    placed["bib-gate"] = _at(_load(TRAY_STEPS["bib-gate"]), 178.0, 181.0, 224.9)

    # Nozzle-gate — flat, on top of cold core.
    placed["nozzle-gate"] = _at(_load(TRAY_STEPS["nozzle-gate"]), 74.0, 151.0, 213.4)

    return {n: (s, COLORS[n]) for n, s in placed.items()}
