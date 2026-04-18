# Vase-mode orientation: Z = tube axis, prints standing up (spiral rises along Z).

from pathlib import Path
import cadquery as cq


# ═══════════════════════════════════════════════════════
# PHYSICAL DIMENSIONS
# ═══════════════════════════════════════════════════════

INNER_DIAMETER_MM = 3.2      # Kamoer KPP small standard bore
OUTER_DIAMETER_MM = 6.4      # 1.6 mm wall thickness
LENGTH_MM         = 150.0


# ═══════════════════════════════════════════════════════
# DERIVED GEOMETRY
# ═══════════════════════════════════════════════════════

INNER_RADIUS = INNER_DIAMETER_MM / 2
OUTER_RADIUS = OUTER_DIAMETER_MM / 2


# ═══════════════════════════════════════════════════════
# GEOMETRY
# ═══════════════════════════════════════════════════════

def build_tube():
    """Plain hollow cylinder, tube axis along Z."""
    outer = (
        cq.Workplane("XY")
        .circle(OUTER_RADIUS)
        .extrude(LENGTH_MM)
    )
    inner = (
        cq.Workplane("XY")
        .circle(INNER_RADIUS)
        .extrude(LENGTH_MM)
    )
    return outer.cut(inner)


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

tube = build_tube()

solids = tube.solids().vals()
print(f"Tube: {len(solids)} solid(s)")
for i, s in enumerate(solids):
    bb = s.BoundingBox()
    print(f"  Solid {i}: X[{bb.xmin:.2f},{bb.xmax:.2f}] "
          f"Y[{bb.ymin:.2f},{bb.ymax:.2f}] Z[{bb.zmin:.2f},{bb.zmax:.2f}]")

out_dir = Path(__file__).resolve().parent
out_path = out_dir / "peristaltic-tube.step"
cq.exporters.export(tube, str(out_path))
print(f"\nExported: {out_path}")
