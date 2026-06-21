"""Narrow-Edition enclosure contents — the same Kitchen-Edition subsystems, but
with the cold core, compressor shroud, and hopper funnel each rotated 90° about
Z relative to the wide build. The rotations trade X width for Y depth: the box
ends up much narrower (it follows the rotated cold core's 181 mm footprint plus
the refrigeration row) and correspondingly longer front-to-back.

Detailed STEP imports where they exist (cold-core foam shell, the four
valve-manifold tray assemblies with their seated valves, two pump assemblies,
the compressor shroud). Placeholder boxes for parts that have no STEP yet
(condenser+fan, SeaFlo diaphragm pump). The hopper funnel is not a content here
— like the display, it is seated into the box's carved opening by the assembly.

Coordinate frame: +X right, +Y back, +Z up. Origin at the lower-front-left
corner.

Layout — packed against the actual solid geometry (see _audit.py), not bboxes:
  * Zone A (back-bottom):  cold core (foam shell), rotated 90° about Z so it is
    181 wide × 283 deep, on the floor, lifted clear of the back braces.
  * Zone D (front-bottom): compressor shroud (rotated 90° more than the wide
    build → 133 wide × 178 deep) + condenser/fan beside it.
  * Zone C (front-top):    the two flavor pumps; the SeaFlo laid over their backs,
    set clear of every valve tray (it grazes only the soft funnel above it).
  * Zone B (back-top):     the four valve-manifold trays above the cold core.
    They are sparse dog-bones, so they NEST: two per column, a deep tray plus a
    shorter one (one flipped 180° so its tees interleave with the other's) slid
    over the deep tray's empty bridge. The residual overlap is small bucket-edge
    contact, not elbows ramming elbows.
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

# --- Placeholder dimensions ----------------------------------------------
# Condenser + fan harvested from the donor ice maker. Two dimensions match
# the compressor envelope; the third (airflow axis) is the fan + finstack stack
# depth, calipered [56 mm](CONDENSER_AIRFLOW) combined.
CONDENSER_FACE_A, CONDENSER_FACE_B, CONDENSER_AIRFLOW = 178.0, 151.0, 56.0
# SeaFlo 22-Series diaphragm pump, body only (sans mounting brackets).
SEAFLO_DIMS = (75.0, 60.0, 175.0)

# Cold-core front Y — the front block (Zones C/D, deepest part the rotated
# compressor at 178 mm) seats ahead of it, the cold core behind. The split is
# placed just ahead of this so the front half holds the front block and the back
# half houses the cold core.
FRONT_DEPTH = 199.0
# The back half's floor + corner braces stand in the rear corners; the cold core
# is lifted clear of them.
FOAM_LIFT = 14.0
# The compressor is raised one wall, clearing the front half's bottom seam lip.
SEAM_CLEAR_LIFT = 3.0
# The condenser sits over the bottom-right corner pods; lift it clear of them.
COND_LIFT = 17.0
# The front half's corner ribs reach ~12.25 mm inboard from each side wall;
# front-bottom content against a side wall is inset this much, plus a gap.
SIDE_RIB_INSET = 14.0
# Condenser right edge — sets the box width: compressor (inset, 133 wide) + a
# gap + the 56-wide condenser, leaving a side-rib inset to the right wall.
COND_RIGHT = 213.0
# Enclosure wall thickness (mirrors ../narrow-enclosure/narrow_enclosure.py).
WALL = 3.0


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


def build():
    placed = {}

    # --- Zone A: cold core, rotated 90° about Z (narrow X / deep Y), back-bottom,
    # left-anchored, lifted clear of the back half's floor + corner braces.
    foam = _rot(_load(FOAM_SHELL), (0, 0, 1), 90.0)    # 181 x 283 x 213
    fbb = foam.BoundingBox()
    cold_w, cold_d, cold_h = fbb.xlen, fbb.ylen, fbb.zlen
    back_top_z = FOAM_LIFT + cold_h + 2.0              # back-top tray floor
    placed["foam-shell"] = _at(foam, 0.0, FRONT_DEPTH, FOAM_LIFT)

    # --- Zone D: refrigeration on the floor. Compressor shroud rotated 90° more
    # than the wide build (133 wide × 178 deep), inset to clear the front corner
    # pods; condenser as a panel to its right (airflow across X), lifted to clear
    # the bottom-right corner pods it sits over.
    comp = _rot(_load(COMP_SHROUD), (0, 0, 1), 180.0)  # 133 x 178 x 151
    placed["compressor-shroud"] = _at(comp, SIDE_RIB_INSET + 1.0, 0.0, SEAM_CLEAR_LIFT)
    comp_top_z = SEAM_CLEAR_LIFT + comp.BoundingBox().zlen
    cond = _box(CONDENSER_AIRFLOW, CONDENSER_FACE_B, CONDENSER_FACE_A)  # 56 x 151 x 178
    placed["condenser+fan"] = _at(cond, COND_RIGHT - CONDENSER_AIRFLOW, 0.0, COND_LIFT)

    # --- Zone C: the two flavor pumps stand on the compressor top (elbows up),
    # the SeaFlo laid flat over their backs above. A 175 mm pump has no channel
    # that clears BOTH the rigid valve trays (back) and the display+funnel depth
    # (front) — the gap between them is only ~47 mm. It is set forward to clear
    # every tray (no contact with their elbows); it grazes only the soft silicone
    # funnel, which sits directly above it.
    pa1 = _rot(_load(PUMP_ASSEMBLY), (1, 0, 0), 90.0)  # 71.7 x 126.9 x 89.5
    pa2 = _rot(_load(PUMP_ASSEMBLY), (1, 0, 0), 90.0)
    placed["pump-assembly-1"] = _at(pa1, SIDE_RIB_INSET + 2.0, 14.0, comp_top_z)
    placed["pump-assembly-2"] = _at(pa2, SIDE_RIB_INSET + 74.0, 14.0, comp_top_z)
    pump_top_z = comp_top_z + pa1.BoundingBox().zlen
    sf_w, sf_d, sf_h = SEAFLO_DIMS                     # [75 x 60 x 175](SEAFLO_DIMS)
    seaflo = _box(sf_h, sf_w, sf_d)                    # 175 x 75 x 60, long axis along X
    placed["seaflo-pump"] = _at(seaflo, SIDE_RIB_INSET + 2.0, 123.0, pump_top_z)

    # --- Zone B: the four valve-manifold trays back-top above the cold core.
    # Each tray is a sparse (~quarter-fill) dog-bone: dense valve buckets at the
    # two ends with the elbows/tees rising out the top, joined by an empty pinched
    # bridge. The bbox is mostly air, so the trays NEST rather than tile — two per
    # column, a deep tray (source-select, bag-circuit) plus a shorter one slid
    # over the deep tray's sparse bridge. The bib-gate is flipped 180° about X
    # (floor up, tees pointing down) so its tees interleave with bag-circuit's
    # instead of colliding; the residual solid overlap lives at bucket edges, not
    # elbow-on-elbow. See _audit.py for the measured overlaps.
    ss = _rot(_load(TRAY_STEPS["source-select"]), (0, 0, 1), 90.0)  # 93 x 271, col L deep
    bc = _rot(_load(TRAY_STEPS["bag-circuit"]),   (0, 0, 1), 90.0)  # 74.5 x 212, col R deep
    ng = _rot(_load(TRAY_STEPS["nozzle-gate"]),   (0, 0, 1), 90.0)  # 74.5 x 126, nested col L
    bg = _rot(_load(TRAY_STEPS["bib-gate"]),      (0, 0, 1), 90.0)  # 74.5 x 166, nested col R
    bg = _rot(bg, (1, 0, 0), 180.0)                                 # flip floor-up, tees down
    placed["source-select"] = _at(ss,  2.0, FRONT_DEPTH + 1.0,   back_top_z)  # col L deep
    placed["nozzle-gate"]   = _at(ng, 14.0, FRONT_DEPTH + 0.0,   back_top_z)  # col L nested over bridge
    placed["bag-circuit"]   = _at(bc, 98.0, FRONT_DEPTH + 1.0,   back_top_z)  # col R deep
    placed["bib-gate"]      = _at(bg, 114.0, FRONT_DEPTH + 117.0, back_top_z)  # col R nested, flipped

    return {n: (s, COLORS[n]) for n, s in placed.items()}
