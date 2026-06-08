"""Kitchen Edition device assembly — every internal subsystem packed inside the
H2C left-nozzle build envelope (325 x 320 x 320, the limit for a single-piece
printed enclosure).

Detailed STEP imports where they exist (cold core foam shell, the four
valve-manifold tray assemblies with their seated valves, two pump-case
assemblies, the compressor shroud). Two placeholder boxes for parts that have
no STEP yet (condenser+fan, SeaFlo diaphragm pump).

Coordinate frame: +X right, +Y back, +Z up. Origin at the lower-front-left
corner of the H2C build envelope.

Layout is the first-fit-decreasing pack that fits inside a 319 x 314 x 314 mm
inner volume (a 3 mm-walled enclosure that fits the H2C left-nozzle envelope).
Cold core spans the lower-front block; compressor shroud sits behind it across
the back strip; source-select tray stands on end beside the compressor; the
condenser, SeaFlo, pump cases, and remaining trays form a second layer above
the cold core.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "_cadq_export.py").is_file())
_hw = _repo / "hardware"
sys.path.insert(0, str(_hw))
from _cadq_export import export_assembly


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
# Condenser + fan harvested from the donor ice maker. Two of its three
# dimensions match the compressor envelope (the same back and side faces sit
# flush against the same shroud plane); the third axis (airflow) is the fan +
# finstack stack depth, calipered at 56 mm combined.
CONDENSER_FACE_A, CONDENSER_FACE_B, CONDENSER_AIRFLOW = 178.0, 151.0, 56.0

# SeaFlo 22-Series diaphragm pump, body only (sans mounting brackets).
SEAFLO_DIMS = (75.0, 60.0, 175.0)


# --- H2C left-nozzle build envelope --------------------------------------
H2C_X, H2C_Y, H2C_Z = 325.0, 320.0, 320.0       # outer print envelope
ENC_WALL = 3.0                                  # enclosure wall thickness
INNER_X = H2C_X - 2 * ENC_WALL                  # 319
INNER_Y = H2C_Y - 2 * ENC_WALL                  # 314
INNER_Z = H2C_Z - 2 * ENC_WALL                  # 314


# --- Colors ---------------------------------------------------------------
COLORS = {
    "foam-shell":       cq.Color(0.55, 0.75, 0.95, 0.55),  # translucent ice blue
    "compressor-shroud":cq.Color(0.60, 0.62, 0.66),        # galvanized
    "condenser+fan":    cq.Color(0.78, 0.55, 0.35),        # copper-ish
    "seaflo-pump":      cq.Color(0.20, 0.35, 0.55),        # SeaFlo navy
    "pump-case-1":      cq.Color(0.45, 0.45, 0.50),
    "pump-case-2":      cq.Color(0.55, 0.55, 0.60),
    "source-select":    cq.Color(0.45, 0.70, 0.45),        # green
    "bag-circuit":      cq.Color(0.90, 0.66, 0.32),        # amber
    "bib-gate":         cq.Color(0.62, 0.47, 0.82),        # violet
    "nozzle-gate":      cq.Color(0.84, 0.42, 0.42),        # red
    "h2c-envelope":     cq.Color(0.85, 0.85, 0.85, 0.04),
}


# --- Helpers --------------------------------------------------------------
def _load(path):
    return cq.importers.importStep(str(path)).val()


def _rot(shape, axis, deg):
    return shape.rotate((0, 0, 0), axis, deg)


def _at(shape, xmin, ymin, zmin):
    """Translate so the shape's bbox lower-corner lands at (xmin, ymin, zmin)."""
    bb = shape.BoundingBox()
    return shape.translate((xmin - bb.xmin, ymin - bb.ymin, zmin - bb.zmin))


def _box(dx, dy, dz):
    return cq.Workplane("XY").box(dx, dy, dz, centered=(False, False, False)).val()


def _swap_xy(shape):
    """Rotate 90 deg about Z so the bbox X and Y swap."""
    return _rot(shape, (0, 0, 1), 90.0)


def _cycle_xyz_to_yzx(shape):
    """Two 90 deg rotations: bbox (dx, dy, dz) -> (dy, dz, dx)."""
    return _rot(_rot(shape, (1, 0, 0), 90.0), (0, 1, 0), 90.0)


# --- Build ----------------------------------------------------------------
def build():
    placed = {}

    # Cold core: native bbox 283 x 181 x 213.4. Lower-front-left corner.
    foam = _load(FOAM_SHELL)
    placed["foam-shell"] = _at(foam, 0.0, 0.0, 0.0)

    # Compressor shroud: native 133 x 178 x 151.5. Rotate 90 about Z -> 178 x 133.
    # Sits behind the cold core in Y, on the floor.
    comp = _swap_xy(_load(COMP_SHROUD))
    placed["compressor-shroud"] = _at(comp, 0.0, 181.0, 0.0)

    # Source-select tray: native 224.86 x 89.22 x 63. Cycle -> 89.22 x 63 x 224.86.
    # Stands vertical beside the compressor in the back strip.
    src = _cycle_xyz_to_yzx(_load(TRAY_STEPS["source-select"]))
    placed["source-select"] = _at(src, 178.0, 181.0, 0.0)

    # Condenser + fan: box 178 x 151 x 56. Above cold core, left-front.
    cond = _box(CONDENSER_FACE_A, CONDENSER_FACE_B, CONDENSER_AIRFLOW)
    placed["condenser+fan"] = _at(cond, 0.0, 0.0, 213.4)

    # SeaFlo: box reoriented to 60 x 175 x 75 (lay on its side, long axis = Y).
    sf_dx, sf_dy, sf_dz = SEAFLO_DIMS  # 75 x 60 x 175
    seaflo = _box(sf_dy, sf_dz, sf_dx) # 60 x 175 x 75
    placed["seaflo-pump"] = _at(seaflo, 178.0, 0.0, 213.4)

    # Pump cases: native 76 x 74 x 135.5. Cycle -> 74 x 135.5 x 76. Lying on
    # their long sides, end-to-end on top of the cold core.
    pump1 = _cycle_xyz_to_yzx(_load(PUMP_CASE))
    placed["pump-case-1"] = _at(pump1, 238.0, 0.0, 213.4)

    pump2 = _cycle_xyz_to_yzx(_load(PUMP_CASE))
    placed["pump-case-2"] = _at(pump2, 0.0, 151.0, 213.4)

    # Bag-circuit: native 158.14 x 72.5 x 63. Cycle -> 72.5 x 63 x 158.14.
    # Stands vertical in the back-right corner above the floor.
    bag = _cycle_xyz_to_yzx(_load(TRAY_STEPS["bag-circuit"]))
    placed["bag-circuit"] = _at(bag, 178.0, 244.0, 0.0)

    # Bib-gate: native 139.28 x 72.5 x 63. Flat, on top of source-select.
    bib = _load(TRAY_STEPS["bib-gate"])
    placed["bib-gate"] = _at(bib, 178.0, 181.0, 224.9)

    # Nozzle-gate: native 99.14 x 72.5 x 63. Flat, on top of cold core.
    noz = _load(TRAY_STEPS["nozzle-gate"])
    placed["nozzle-gate"] = _at(noz, 74.0, 151.0, 213.4)

    # H2C build envelope — translucent reference cuboid (the outer 325x320x320).
    env = _box(H2C_X, H2C_Y, H2C_Z)
    placed["h2c-envelope"] = _at(env, -ENC_WALL, -ENC_WALL, -ENC_WALL)

    assy = cq.Assembly(name="kitchen-edition-device-assembly")
    for name, shape in placed.items():
        assy.add(shape, name=name, color=COLORS[name])
    return assy, placed


def _report(placed):
    print("\n  part               X range            Y range            Z range")
    xs, ys, zs = [], [], []
    skip = {"h2c-envelope"}
    for name, shape in placed.items():
        b = shape.BoundingBox()
        if name not in skip:
            xs += [b.xmin, b.xmax]; ys += [b.ymin, b.ymax]; zs += [b.zmin, b.zmax]
        print("  %-18s [%7.1f,%7.1f]  [%7.1f,%7.1f]  [%7.1f,%7.1f]"
              % (name, b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax))
    env = (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
    print("\n  Contents envelope:  %.1f (X) x %.1f (Y) x %.1f (Z) mm" % env)
    print("  H2C left nozzle:    %.1f (X) x %.1f (Y) x %.1f (Z) mm  (build volume)"
          % (H2C_X, H2C_Y, H2C_Z))
    print("  3 mm-wall inside:   %.1f (X) x %.1f (Y) x %.1f (Z) mm"
          % (INNER_X, INNER_Y, INNER_Z))
    fits_3mm = env[0] <= INNER_X + 1e-3 and env[1] <= INNER_Y + 1e-3 and env[2] <= INNER_Z + 1e-3
    fits_raw = env[0] <= H2C_X + 1e-3   and env[1] <= H2C_Y + 1e-3   and env[2] <= H2C_Z + 1e-3
    print("  Fits 3 mm-wall H2C: %s" % fits_3mm)
    print("  Fits raw H2C bed:   %s" % fits_raw)

    def bbox_overlap(a, b):
        return min(min(a.xmax, b.xmax) - max(a.xmin, b.xmin),
                   min(a.ymax, b.ymax) - max(a.ymin, b.ymin),
                   min(a.zmax, b.zmax) - max(a.zmin, b.zmin))
    names = [n for n in placed if n not in skip]
    clash = False
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = placed[names[i]], placed[names[j]]
            if bbox_overlap(a.BoundingBox(), b.BoundingBox()) <= 1e-6:
                continue
            vol = a.intersect(b).Volume()
            if vol > 1.0:
                clash = True
                print("  ** SOLID clash %s / %s = %.2f mm^3" % (names[i], names[j], vol))
    print("  no solid collisions" if not clash else "  ** CLASHES PRESENT **")


def main():
    assy, placed = build()
    out = _here.parent / "device-assembly.step"
    export_assembly(assy, str(out))
    print("-> %s" % out.name)
    _report(placed)


if __name__ == "__main__":
    main()
