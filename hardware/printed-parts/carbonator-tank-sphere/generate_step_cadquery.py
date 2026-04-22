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

Alongside the main tank, a smaller test sphere with a port for a John
Guest PP1208E 1/4" OD push-to-connect bulkhead union is generated for
dialing in print settings (layer adhesion, support strategy, overfill,
temps) and for pressure-testing the fitting.  The previous printed
1/4 NPT thread was a weep point; the JG bulkhead replaces that printed
thread with a proper mechanical seal (flange + O-ring + jam nut).

A JG bulkhead clamps between its flange and a jam nut against two flat
faces — a sphere's outside surface is curved, so the fitting cannot seat
on the naked sphere.  Flat bosses on both the outside (for the flange
face) and inside (for the jam nut) are added around the through-hole.
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
# the tuning translates directly to the full-size part.  The JG bulkhead
# passes through a boss at the top pole — see the JG section below.
TEST_R_OUTER = 30.0
TEST_R_INNER = TEST_R_OUTER - WALL


# ═══════════════════════════════════════════════════════
# JOHN GUEST PP1208E BULKHEAD UNION — PORT GEOMETRY
# ═══════════════════════════════════════════════════════
#
# Published dimensions for the PP1208E (1/4" OD black polypropylene
# push-to-connect bulkhead union, ASIN B00JYFU8MM):
#   Panel hole:       5/8"      = 15.875 mm
#   Body OD / flange: ~0.875"   = 22.2 mm (both flange and jam-nut hex
#                                 fit within this envelope)
#   Overall length:   ~1.375"   = 34.9 mm
#   Max panel thickness: not published by JG, but the overall length
#                     minus flange thickness and collet engagement
#                     leaves ~10–14 mm of thread, well over our 5 mm
#                     wall even after adding a boss on each side.
#
# Boss design:
#   Outside: flat-topped cylindrical pedestal tangent-merged into the
#            sphere, wide enough that the flange (~22 mm OD) sits fully
#            on flat plastic with margin.
#   Inside:  matching cylindrical pedestal for the jam nut.  At
#            TEST_R_INNER = 25 mm the interior curvature is steep enough
#            that a 22 mm hex nut would rock on a bare sphere wall.
#
#   Through-hole: 5/8" + print-tolerance clearance so the shank passes
#            cleanly without being a press fit.

JG_HOLE_DIA         = 5/8 * 25.4 + 0.25        # 16.13 mm (hole w/ tolerance)
JG_FLANGE_OD        = 22.2                     # published body/flange OD
JG_BOSS_OD          = JG_FLANGE_OD + 4.0       # 26.2 mm — flange + 2 mm margin
JG_BOSS_HEIGHT_OUT  = 4.0                      # apex rise above outer pole
JG_BOSS_HEIGHT_IN   = 3.0                      # apex drop below inner pole


def build_boss(od, height, z_base, direction):
    """Cylindrical pedestal along +Z, merged into the sphere.

    Parameters
    ----------
    od        : boss outer diameter
    height    : axial thickness of the pedestal above/below the pole
    z_base    : axial coordinate of the sphere surface at the axis
                (TEST_R_OUTER for the outside boss,  TEST_R_INNER for
                 the inside boss)
    direction : +1 for an outside boss rising in +Z away from the
                sphere, -1 for an inside boss descending in -Z from the
                inner pole into the cavity
    """
    # The cylinder base is sunk well into the sphere so the boss stays
    # connected to the wall after the through-hole is cut.  At the boss
    # bottom (z = z_base - overlap on the outside case) the sphere's
    # own material extends from r=0 out to sqrt(r_sphere² - z²); we
    # need that radius to exceed the hole radius, or the hole will
    # trim the boss off at the neck.  overlap=3 mm easily clears the
    # 5/8" hole for both TEST_R_OUTER=30 and TEST_R_INNER=25.
    overlap = 3.0
    bottom = z_base - overlap if direction > 0 else z_base - height
    length = height + overlap
    return (
        cq.Workplane("XY")
        .workplane(offset=bottom)
        .circle(od / 2)
        .extrude(length)
    )


# ═══════════════════════════════════════════════════════
# BUILDS
# ═══════════════════════════════════════════════════════

def build_hollow_sphere(r_outer, r_inner):
    return (
        cq.Workplane("XY").sphere(r_outer)
        .cut(cq.Workplane("XY").sphere(r_inner))
    )


def build_test_sphere_with_jg_port():
    part = build_hollow_sphere(TEST_R_OUTER, TEST_R_INNER)

    # Outside flat-top boss for the flange face.  Merges into the sphere
    # at the top pole and rises JG_BOSS_HEIGHT_OUT above it.
    outer_boss = build_boss(
        od=JG_BOSS_OD,
        height=JG_BOSS_HEIGHT_OUT,
        z_base=TEST_R_OUTER,
        direction=+1,
    )
    part = part.union(outer_boss)

    # Inside flat-bottom boss for the jam-nut face.  Descends into the
    # cavity from the inner pole by JG_BOSS_HEIGHT_IN.  TEST_R_INNER is
    # 25 mm; the boss OD is 26.2 mm — fits easily without touching the
    # opposite wall.
    inner_boss = build_boss(
        od=JG_BOSS_OD,
        height=JG_BOSS_HEIGHT_IN,
        z_base=TEST_R_INNER,
        direction=-1,
    )
    part = part.union(inner_boss)

    # Clean through-hole sized for the JG shank.  Enters the outer
    # boss face at +Z, breaches the sphere wall, emerges through the
    # inner boss face into the cavity.  It stops there — it does NOT
    # continue down to the south pole, because the hole diameter is
    # large enough that a full-axis cut would clip off the south-pole
    # cap of the shell (where the sphere's wall-material at the axis
    # is thinner than the hole radius).
    z_top    = TEST_R_OUTER + JG_BOSS_HEIGHT_OUT + 1.0       # 35.0
    z_bottom = TEST_R_INNER - JG_BOSS_HEIGHT_IN - 1.0        # 21.0
    hole = (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .circle(JG_HOLE_DIA / 2)
        .extrude(z_top - z_bottom)
    )
    part = part.cut(hole)

    return part


# ═══════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════

out_dir = Path(__file__).resolve().parent

main_tank = build_hollow_sphere(R_OUTER, R_INNER)
test_part = build_test_sphere_with_jg_port()

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
