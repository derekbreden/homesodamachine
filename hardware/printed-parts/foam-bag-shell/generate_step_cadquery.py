"""
Foam-bag shell (plan A) — minimal first feature: a round floor disc.

Sized just to fit the pressure vessel and the copper evaporator coil that
wraps around it.  No walls, no inner shell, no pockets — just the floor.
"""

from pathlib import Path
import cadquery as cq


# ═══════════════════════════════════════════════════════
# CONSTANTS  (provenance: hardware/printed-parts/foam-bag-shell/README.md)
# ═══════════════════════════════════════════════════════

TANK_OUTER_R    = 63.5                          # 5" OD / 2
COIL_ZONE       = 7.0                           # 1/4" copper coil + tolerance
FLOOR_R         = TANK_OUTER_R + COIL_ZONE      # 70.5
FLOOR_THICKNESS = 1.0


# ═══════════════════════════════════════════════════════
# FEATURES
# ═══════════════════════════════════════════════════════

def build_floor():
    """Round disc, radius FLOOR_R, thickness FLOOR_THICKNESS, sitting on z=0."""
    return (
        cq.Workplane("XY")
        .circle(FLOOR_R)
        .extrude(FLOOR_THICKNESS)
    )


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

def main():
    floor = build_floor()

    bb = floor.solids().val().BoundingBox()
    print(f"floor: X[{bb.xmin:7.2f},{bb.xmax:7.2f}] "
          f"Y[{bb.ymin:7.2f},{bb.ymax:7.2f}] "
          f"Z[{bb.zmin:7.2f},{bb.zmax:7.2f}]")

    out = Path(__file__).resolve().parent / "foam-bag-shell-floor.step"
    cq.exporters.export(floor, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
