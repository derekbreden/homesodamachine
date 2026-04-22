"""
Carbonator tank: hollow sphere, first iteration.

Simplest shape that occupies the target space — no ports, no bosses,
no retention features on the main tank.  Ports come in later rounds.

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

Alongside the main tank, a smaller test sphere with a plain through-hole
at the top pole is generated for dialing in print settings (layer
adhesion, support strategy, overfill, temps) and for pressure-testing
the fitting.  The hole accepts a John Guest PP1208E 1/4" OD push-to-
connect bulkhead union — its O-ring seats directly against the curved
outer sphere wall, so no flat boss is needed on the print.
"""

import math
from pathlib import Path
import cadquery as cq


# ═══════════════════════════════════════════════════════
# SPHERE DIMENSIONS
# ═══════════════════════════════════════════════════════

WALL = 5.0

# Main tank: 1.5 L interior
INTERIOR_VOLUME_ML = 1500.0
R_INNER = (3 * INTERIOR_VOLUME_ML * 1000 / (4 * math.pi)) ** (1/3)  # 71.0 mm
R_OUTER = R_INNER + WALL                                            # 76.0 mm

# Test sphere: same wall, smaller diameter for dialing in print settings
# (layer adhesion, support removal, overfill, temps).  Real 5 mm walls so
# the tuning translates directly to the full-size part.  A plain through-
# hole at the top pole passes the JG bulkhead shank; the fitting's O-ring
# seals against the curved outer wall.
TEST_R_OUTER = 40.0
TEST_R_INNER = TEST_R_OUTER - WALL


# ═══════════════════════════════════════════════════════
# JOHN GUEST PP1208E BULKHEAD UNION — PORT GEOMETRY
# ═══════════════════════════════════════════════════════
#
# Published dimensions for the PP1208E (1/4" OD black polypropylene
# push-to-connect bulkhead union, ASIN B00JYFU8MM):
#   Panel hole:       5/8"      = 15.875 mm
#   Body OD / flange: ~0.875"   = 22.2 mm
#   Overall length:   ~1.375"   = 34.9 mm
#
# Through-hole: 5/8" + print-tolerance clearance so the shank passes
# cleanly without being a press fit.

JG_HOLE_DIA = 5/8 * 25.4 + 0.25        # 16.13 mm (hole w/ tolerance)


# ═══════════════════════════════════════════════════════
# BUILDS
# ═══════════════════════════════════════════════════════

def build_hollow_sphere(r_outer, r_inner):
    return (
        cq.Workplane("XY").sphere(r_outer)
        .cut(cq.Workplane("XY").sphere(r_inner))
    )


def build_test_sphere():
    """Test sphere with a plain axial through-hole at the top pole.

    The JG bulkhead's O-ring seals directly against the curved outer
    sphere wall — no flat boss.  The cutter cylinder overshoots both
    the outer sphere surface (above the +Z pole at TEST_R_OUTER) and
    the inner cavity surface (below the +Z inner pole at TEST_R_INNER)
    by ~2 mm on each side.  The overshoot guarantees clean breakthrough
    on both sides and avoids the thin tessellation sliver OCCT can leave
    when a cylindrical cutter just barely grazes a spherical surface.
    """
    part = build_hollow_sphere(TEST_R_OUTER, TEST_R_INNER)
    z_top    = TEST_R_OUTER + 2.0           # 42.0 — 2 mm past outer pole
    z_bottom = TEST_R_INNER - 2.0           # 33.0 — 2 mm past inner pole
    hole = (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .circle(JG_HOLE_DIA / 2)
        .extrude(z_top - z_bottom)
    )
    return part.cut(hole)


# ═══════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════

out_dir = Path(__file__).resolve().parent

main_tank = build_hollow_sphere(R_OUTER, R_INNER)
test_part = build_test_sphere()

PARTS = [
    ("carbonator-tank-sphere",      main_tank, R_INNER,      R_OUTER),
    ("carbonator-tank-sphere-test", test_part, TEST_R_INNER, TEST_R_OUTER),
]

for name, part, r_in, r_out in PARTS:
    volume_ml = (4/3) * math.pi * r_in**3 / 1000
    s = part.val()
    bb = s.BoundingBox()
    print(f"{name}")
    print(f"  interior: Ø {2*r_in:5.1f} mm  ({volume_ml:7.1f} mL)")
    print(f"  exterior: Ø {2*r_out:5.1f} mm  (wall {r_out - r_in:.1f} mm)")
    print(f"  bbox:     X[{bb.xmin:.1f},{bb.xmax:.1f}] "
          f"Y[{bb.ymin:.1f},{bb.ymax:.1f}] Z[{bb.zmin:.1f},{bb.zmax:.1f}]")
    print(f"  volume:   {s.Volume():.1f} mm³   "
          f"(solids={len(part.solids().vals())}, valid={s.isValid()})")
    out_path = out_dir / f"{name}.step"
    cq.exporters.export(part, str(out_path))
    print(f"  exported: {out_path}\n")
