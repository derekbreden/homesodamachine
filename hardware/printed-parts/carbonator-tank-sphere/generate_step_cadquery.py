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

Alongside the main tank, a smaller test sphere with a 1/4 NPT female
port is generated for dialing in print settings (layer adhesion, support
strategy, overfill, temps) and for pressure-testing a real NPT fitting
against printed threads.
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
# the tuning translates directly to the full-size part.  The 1/4 NPT
# female thread is cut directly through the 5 mm wall at the top pole —
# no boss.  With 18 TPI that gives ~3 turns of thread engagement, which
# plus PTFE tape is enough for a pressure test.
TEST_R_OUTER = 25.0
TEST_R_INNER = TEST_R_OUTER - WALL


# ═══════════════════════════════════════════════════════
# 1/4 NPT FEMALE THREAD
# ═══════════════════════════════════════════════════════
#
# Modeled as TWO separate cutter solids — a tapered root cone and a
# helical V ridge — that are subtracted from the part in sequence.
#
# Two separate cuts (not a pre-unioned plug) and cut-order = ridge-first:
#   OCCT's boolean fuse silently drops one input when a helical-bspline
#   sweep shares a surface with a cone (they coincide radially).  And
#   cutting the cone BEFORE the ridge lets OCCT lose track of the
#   ridge's intersection with the (now missing) cone boundary, so the
#   ridge cut becomes a no-op.  Cutting the ridge first, then the cone,
#   produces the thread flanks cleanly.
#
# Taper angle is relaxed from the NPT spec 1.79° down to 1.00°:
#   At ≥1.5° the tapered-helix tessellation produces thousands of
#   non-manifold edges (T-junctions) where the helix flank bsplines
#   meet the cone; below 1.0° the mesh comes out effectively manifold.
#   A real 1/4 NPT male fitting will deform the plastic to take up the
#   0.79° difference — not perfect NPT but close enough for a printed
#   test that gets cleaned up with a real tap post-print anyway.
#
# Geometry:
#   pitch    = 25.4/18 = 1.411 mm   (18 TPI, per NPT)
#   taper    = 1.00° per side       (relaxed from NPT's 1.79° — see above)
#   r_minor  = 5.55 mm at the opening (wider end), narrowing with depth
#   V-depth  = 1.22 mm              (60° included angle, full pitch width)
#   r_major  = r_minor + V-depth
#
# Handedness: cq.Wire.makeHelix with lefthand=False builds a RH helix
# (ascending CCW viewed from +Z).  After cutting, the female groove is
# RH — a standard 1/4 NPT male fitting threads in CW.

NPT14_PITCH          = 25.4 / 18
NPT14_TAPER_HALF_DEG = 1.00                                          # relaxed; see header
NPT14_TAPER          = math.tan(math.radians(NPT14_TAPER_HALF_DEG))
NPT14_R_MINOR        = 11.10 / 2                                    # 5.55 mm (opening)
NPT14_V_DEPTH        = (NPT14_PITCH / 2) / math.tan(math.radians(30))  # 1.222 mm
NPT14_R_MAJOR        = NPT14_R_MINOR + NPT14_V_DEPTH                # 6.77 mm
# Axial threaded length.  The test sphere's wall is 5 mm, so we cut
# slightly longer than the wall to guarantee breakthrough on both ends
# (outside air at the top pole, interior cavity at the bottom) with no
# tessellation slivers left spanning the wall.
NPT14_THREAD_LEN     = 7.0


def build_npt14_cutters(length=NPT14_THREAD_LEN):
    """Return (core_solid, ridge_solid) for cutting 1/4 NPT female threads.

    Both solids are placed in their local frame with the deep tip at z=0
    and the opening at z=+length.  The caller translates them by
    (z_opening - length) so the opening lands at z_opening.

    Core is a tapered cone (see NPT14_TAPER_HALF_DEG in the module
    header — the taper is relaxed from the NPT 1.79° spec for cleaner
    meshes).  Radius R_MINOR at the deep tip (z=0) grows to
    R_MINOR + TAPER·length at the opening.

    Ridge is a helical V-shape swept along a right-handed helix that rides
    on the core's surface.  The V extends radially outward from the helix
    out to R_MAJOR on the bore-opening side.

    These two cutters are intentionally NOT unioned here — see the module
    header for why.  Cut them as two sequential .cut() operations.
    """
    core = (
        cq.Workplane("XY")
        .circle(NPT14_R_MINOR)
        .workplane(offset=length)
        .circle(NPT14_R_MINOR + NPT14_TAPER * length)
        .loft()
    ).val()

    helix = cq.Wire.makeHelix(
        pitch=NPT14_PITCH,
        height=length,
        radius=NPT14_R_MINOR,
        center=cq.Vector(0, 0, 0),
        dir=cq.Vector(0, 0, 1),
        angle=NPT14_TAPER_HALF_DEG,
        lefthand=False,      # RH thread per NPT convention
    )

    # V-profile in the plane perpendicular to the helix tangent at its start.
    # Helix starts at (R_MINOR, 0, 0); the start tangent is ~(0, +1, 0), so
    # xDir=radial and normal=tangential gives a plane whose local X is
    # radial outward and whose local Y is along the helix axis.
    profile_plane = cq.Plane(
        origin=(NPT14_R_MINOR, 0, 0),
        xDir=(1, 0, 0),
        normal=(0, 1, 0),
    )
    profile_wire = (
        cq.Workplane(profile_plane)
        .moveTo(0, -NPT14_PITCH / 2)
        .lineTo(NPT14_V_DEPTH, 0)
        .lineTo(0, NPT14_PITCH / 2)
        .close()
        .wire()
        .val()
    )
    # cq.Solid.sweep with makeSolid=True is more reliable than
    # Workplane.sweep for tapered helical paths; the Workplane wrapper has
    # a history of producing ridge solids that silently fail boolean ops.
    ridge = cq.Solid.sweep(
        profile_wire, [], helix, makeSolid=True, isFrenet=True,
    )

    return core, ridge


# ═══════════════════════════════════════════════════════
# BUILDS
# ═══════════════════════════════════════════════════════

def build_hollow_sphere(r_outer, r_inner):
    return (
        cq.Workplane("XY").sphere(r_outer)
        .cut(cq.Workplane("XY").sphere(r_inner))
    )


def build_test_sphere_with_npt_port():
    # Plain hollow sphere — no boss.  The NPT thread is cut directly
    # through the 5 mm wall at the top pole.
    part = build_hollow_sphere(TEST_R_OUTER, TEST_R_INNER)

    # Cut the 1/4 NPT female thread.  Ridge (thread flanks) first, then
    # core (bore) — see the NPT header for why the order matters.
    #
    # The thread cutters are built in local coords with the deep tip at
    # z=0 and the opening at z=+NPT14_THREAD_LEN.  With THREAD_LEN > WALL,
    # we place the opening slightly above the outer pole (z_opening >
    # TEST_R_OUTER) so the tip pokes through the inner surface into the
    # cavity.  That guarantees a true through-hole and avoids leaving a
    # paper-thin tessellation sliver spanning the wall.
    z_opening = TEST_R_OUTER + 1.0                 # 1 mm overshoot above pole
    z_tip     = z_opening - NPT14_THREAD_LEN       # 1 mm below inner surface
    core, ridge = build_npt14_cutters()
    core  = core.translate(cq.Vector(0, 0, z_tip))
    ridge = ridge.translate(cq.Vector(0, 0, z_tip))
    part = part.cut(ridge)
    part = part.cut(core)

    return part


# ═══════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════

out_dir = Path(__file__).resolve().parent

main_tank = build_hollow_sphere(R_OUTER, R_INNER)
test_part = build_test_sphere_with_npt_port()

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
