"""
Carbonator tank: hollow sphere, first iteration.

Simplest shape that occupies the target space — no ports, no bosses,
no retention features.  Ports and printability features come in later
rounds.

Sized for 1.5 L interior at 5 mm wall (PETG at 100 psi sustained):

  r_inner = (3 V / 4π)^(1/3)
          = (3 · 1 500 000 / 4π)^(1/3)
          = 71.0 mm

Wall rationale (thin-wall sphere, σ = P·r/(2t)):
  P = 0.689 MPa (100 psi)
  r = 71 mm
  σ·t = 24.5 MPa·mm
  At t = 5 mm  →  σ = 4.9 MPa.
  Against ~15 MPa creep-adjusted allowable for well-printed PETG,
  that's SF ~3 long-term.
"""

import math
from pathlib import Path
import cadquery as cq


# ═══════════════════════════════════════════════════════
# DIMENSIONS
# ═══════════════════════════════════════════════════════

WALL = 5.0

# Main tank: 1.5 L interior
INTERIOR_VOLUME_ML = 1500.0
R_INNER = (3 * INTERIOR_VOLUME_ML * 1000 / (4 * math.pi)) ** (1/3)  # 71.0 mm
R_OUTER = R_INNER + WALL                                            # 76.0 mm

# Test sphere: same wall, smaller diameter for dialing in print settings
# (layer adhesion, support removal, overfill, temps).  Real 5 mm walls so
# the tuning translates directly to the full-size part.
TEST_R_OUTER = 20.0
TEST_R_INNER = TEST_R_OUTER - WALL


# ═══════════════════════════════════════════════════════
# BUILD
# ═══════════════════════════════════════════════════════

def build_hollow_sphere(r_outer, r_inner):
    outer = cq.Workplane("XY").sphere(r_outer)
    inner = cq.Workplane("XY").sphere(r_inner)
    return outer.cut(inner)


# ═══════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════

out_dir = Path(__file__).resolve().parent

PARTS = [
    ("carbonator-tank-sphere",      R_OUTER,      R_INNER),
    ("carbonator-tank-sphere-test", TEST_R_OUTER, TEST_R_INNER),
]

for name, r_out, r_in in PARTS:
    part = build_hollow_sphere(r_out, r_in)
    volume_ml = (4/3) * math.pi * r_in**3 / 1000
    bb = part.val().BoundingBox()
    print(f"{name}")
    print(f"  interior: Ø {2*r_in:5.1f} mm  ({volume_ml:7.1f} mL)")
    print(f"  exterior: Ø {2*r_out:5.1f} mm  (wall {r_out - r_in:.1f} mm)")
    print(f"  bbox:     X[{bb.xmin:.1f},{bb.xmax:.1f}] "
          f"Y[{bb.ymin:.1f},{bb.ymax:.1f}] Z[{bb.zmin:.1f},{bb.zmax:.1f}]")
    out_path = out_dir / f"{name}.step"
    cq.exporters.export(part, str(out_path))
    print(f"  exported: {out_path}\n")
