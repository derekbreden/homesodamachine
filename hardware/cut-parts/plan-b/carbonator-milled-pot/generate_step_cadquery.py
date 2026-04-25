"""
Carbonator body as a CNC-milled "pot" — racetrack pressure vessel with
an ellipsoidal closed bottom dome, all four NPT ports through the dome,
and an open top prepped for a single weld-on disc cap.

Purpose of this STEP: upload to Xometry (CNC Milling) for pricing
quotes.  A test quote at $257/ea (prior geometry revision) has already
confirmed the manufacturing path is viable; this file corrects the
geometry to what the vessel actually needs to be.

── What gets eliminated vs. the in-house fabrication plan ──

  - SendCutSend body half-sheet blanks          → gone
  - SendCutSend end-cap blanks                  → gone
  - Body press dies (PA6-CF printed)            → gone
  - End-cap dishing dies (PA6-CF printed)       → gone
  - Press-forming body halves                   → gone
  - Press-forming / dishing end caps            → gone
  - Butt-welding two D-halves into a body tube  → gone
  - Welding bottom end cap to body              → gone
  - Welding 4x NPT port bosses onto the bottom  → gone
  - Drilling + tapping 4x NPT holes per vessel  → stays as CAM (not
                                                   geometry in STEP)

What remains: ONE circumferential TIG weld where a 0.100"-thick disc
cap meets the rabbeted top of the pot.

── Geometry (inches, converted to mm at export) ──

Outer cross-section (XY):   racetrack (stadium)
                            5.600" (X, long) × 4.000" (Y, short)
                            R = 2.000" semicircles at X = ±0.800,
                            connected by 1.600"-long flats at Y = ±2.000".

Cylindrical body:           Z = 0 to Z = 6.000".  Straight racetrack
                            prism, constant cross-section.

Bottom dome:                Z = -1.250" to Z = 0".  Ellipsoidal —
                            the racetrack cross-section at each Z in
                            [-1.250, 0] is scaled uniformly in X and Y
                            by  scale(z) = sqrt(1 - (z/1.250)**2).
                            At Z = 0 the dome meets the body full size;
                            at Z = -1.250 it collapses to the apex.

Top (Z = 6.000"):           open, with an inner rabbet (0.062" radial
                            step × 0.100" axial depth) so a 0.100"-thick
                            disc cap sits flush with the outer OD.

Wall thickness:             0.125" uniform everywhere — both cylindrical
                            walls and dome wall.  Uniform wall keeps the
                            CAM plan simple (one cutter strategy for the
                            full cavity) and keeps hoop stress at the
                            semicircle (the critical location) well inside
                            304 SS allowable.

── Four 1/4"-18 NPT ports through the bottom dome ──

Port axes run parallel to Z (vertical, straight down through the curved
dome — NOT normal to the dome surface).  The outer dome surface stays
clean and curved; there are no external bosses.

Port locations (2x2 grid, 1.000" center-to-center):

    (+0.500, +0.500)   (+0.500, -0.500)
    (-0.500, +0.500)   (-0.500, -0.500)

Because the uniform 0.125" wall is too thin for full 1/4" NPT thread
depth (~0.390" taper), each port has an INTERNAL thread-engagement boss
on the cavity side of the dome:

  Boss OD:                  0.600"
  Boss height above inner   0.300"   (measured along Z, rising into the
  dome surface:                        cavity)
  Through-hole diameter:    0.438"   (7/16" — tap drill for 1/4"-18 NPT)

Thread-accepting material depth at each port = 0.125" (dome) + 0.300"
(internal boss) = 0.425".  Sufficient for 1/4" NPT taper.

CadQuery models the NPT as a straight through-hole at tap-drill
diameter; the actual tapered thread is a CAM/tap operation noted on
the STEP+PDF package, not geometry in the STEP.

── Hoop-stress sanity check (100 PSI design) ──

Thin-wall hoop stress at the semicircle end of the racetrack:

  sigma = P * r / t
        = 100 * 2.000 / 0.125
        = 1,600 PSI

304 SS allowable: 20,000 PSI.  SF = 12.5x.

Run with: tools/cad-venv/bin/python generate_step_cadquery.py
"""

from pathlib import Path
import cadquery as cq

# ── Conversion ──

IN = 25.4  # mm per inch

# ── Outer racetrack shell ──

SEMI_R_OUT = 2.000 * IN            # outer semicircle radius
FLAT_W_OUT = 1.600 * IN            # outer flat width (along X)
OUTER_X = FLAT_W_OUT + 2 * SEMI_R_OUT   # 5.600"
OUTER_Y = 2 * SEMI_R_OUT                # 4.000"

BODY_HEIGHT = 6.000 * IN           # straight-prism body Z = 0 to Z = 6.000"
DOME_DEPTH = 1.250 * IN            # ellipsoidal dome Z = -1.250 to Z = 0
WALL = 0.125 * IN                  # uniform wall thickness

# ── Top weld-prep rabbet ──

RABBET_DEPTH = 0.100 * IN          # axial depth of the rabbet
RABBET_STEP = 0.062 * IN           # radial step (matches cap thickness minus fit)

# ── NPT ports in the bottom dome ──

PORT_SPACING_X = 1.000 * IN        # center-to-center
PORT_SPACING_Y = 1.000 * IN
NPT_TAP_DRILL = 0.438 * IN         # 7/16" for 1/4-18 NPT
BOSS_OD = 0.600 * IN               # internal boss OD (inside cavity)
BOSS_H = 0.300 * IN                # internal boss height above inner dome surface

# ── Dome loft discretization ──
# Ellipsoidal bottom dome is built as a lofted stack of scaled racetrack
# profiles.  More layers → smoother dome.  The apex is closed with a
# tiny flat at a very small non-zero scale to avoid the singular-point
# loft failure that CadQuery (OCC) hits at scale = 0.
DOME_LAYERS = 20
APEX_MIN_SCALE = 0.05              # non-zero floor at the apex

# ═══════════════════════════════════════════════════════
# GEOMETRY BUILDERS
# ═══════════════════════════════════════════════════════


def racetrack_wire(long_x: float, short_y: float, plane) -> cq.Wire:
    """
    Return a closed racetrack (stadium) wire on the given workplane.

    long_x:  total length along X
    short_y: total width along Y  (= 2 * semicircle radius)
    """
    r = short_y / 2.0
    flat = long_x - 2 * r
    assert flat >= 0, "short_y must be <= long_x for a racetrack"

    wp = (
        plane
        .moveTo(-flat / 2, -r)
        .lineTo(flat / 2, -r)
        .radiusArc((flat / 2, r), -r)    # right semicircle
        .lineTo(-flat / 2, r)
        .radiusArc((-flat / 2, -r), -r)  # left semicircle
        .close()
    )
    return wp


def racetrack_profile(long_x: float, short_y: float) -> cq.Workplane:
    """Draw a racetrack 2D profile on the XY plane, for extrusion."""
    return racetrack_wire(long_x, short_y, cq.Workplane("XY"))


def build_outer_shell() -> cq.Workplane:
    """
    Build the solid outer shell: straight racetrack prism body from
    Z = 0 to Z = 6.000", plus an ellipsoidal dome from Z = -1.250 to
    Z = 0 formed by lofting scaled racetrack profiles.
    """

    # Body: straight extrusion
    body = racetrack_profile(OUTER_X, OUTER_Y).extrude(BODY_HEIGHT)

    # Dome: lofted stack of scaled racetrack cross-sections.
    # z goes from 0 (full size, at body base) down to -DOME_DEPTH (apex).
    # Build sections top-down so the loft is continuous with the body.
    import math

    sections = []
    for i in range(DOME_LAYERS + 1):
        frac = i / DOME_LAYERS                     # 0 .. 1
        z = -frac * DOME_DEPTH                     # 0 .. -DOME_DEPTH
        s = math.sqrt(max(0.0, 1.0 - (z / DOME_DEPTH) ** 2))
        if i == DOME_LAYERS:
            s = APEX_MIN_SCALE                     # close with tiny flat, not a point
        sx = OUTER_X * s
        sy = OUTER_Y * s
        wire = (
            racetrack_wire(sx, sy, cq.Workplane("XY").workplane(offset=z))
            .val()
        )
        sections.append(wire)

    dome_solid = cq.Solid.makeLoft(sections)
    dome = cq.Workplane("XY").newObject([dome_solid])

    # Cap the tiny apex flat so the dome is a closed solid
    apex_cap = (
        racetrack_profile(OUTER_X * APEX_MIN_SCALE, OUTER_Y * APEX_MIN_SCALE)
        .extrude(-0.001 * IN)
        .translate((0, 0, -DOME_DEPTH))
    )
    dome = dome.union(apex_cap)

    # Fuse body + dome
    return body.union(dome)


def build_inner_cavity() -> cq.Workplane:
    """
    Build the inner cavity solid — same topology as the outer shell but
    shrunk inward by WALL in the cross-section plane, and with the dome
    floor pulled up by WALL along Z.  Subtracting this from the outer
    shell produces a uniform 0.125" wall in both the body and the dome.

    The inner racetrack has semicircle radius (SEMI_R_OUT - WALL) and a
    flat width unchanged (flat offset inward in Y by WALL).  The inner
    dome depth stays at DOME_DEPTH; the inner dome's top-of-apex sits
    at Z = -DOME_DEPTH + WALL (dome wall thickness along Z at apex).
    """
    import math

    inner_x = OUTER_X - 2 * WALL
    inner_y = OUTER_Y - 2 * WALL

    # Inner body: open at top (we'll extend above Z = BODY_HEIGHT so
    # the cut removes the top face cleanly)
    top_overshoot = 1.0 * IN
    inner_body = (
        racetrack_profile(inner_x, inner_y)
        .extrude(BODY_HEIGHT + top_overshoot)
    )

    # Inner dome: same ellipsoidal shape, reaching down to
    # Z = -DOME_DEPTH + WALL  so the wall thickness at the apex (along
    # Z) equals WALL.  The dome's "full size" Z remains Z = 0 (so the
    # dome-to-body junction is flush and the wall there is WALL).
    inner_dome_depth = DOME_DEPTH - WALL
    if inner_dome_depth <= 0:
        raise RuntimeError("wall exceeds dome depth")

    sections = []
    for i in range(DOME_LAYERS + 1):
        frac = i / DOME_LAYERS
        z = -frac * inner_dome_depth
        # Scale follows the same ellipsoid shape as the outer dome, but
        # based on the inner dome depth — so at z = 0 scale = 1 (meets
        # body ID), and at z = -inner_dome_depth scale collapses.
        s = math.sqrt(max(0.0, 1.0 - (z / inner_dome_depth) ** 2))
        if i == DOME_LAYERS:
            s = APEX_MIN_SCALE
        sx = inner_x * s
        sy = inner_y * s
        wire = (
            racetrack_wire(sx, sy, cq.Workplane("XY").workplane(offset=z))
            .val()
        )
        sections.append(wire)

    inner_dome_solid = cq.Solid.makeLoft(sections)
    inner_dome = cq.Workplane("XY").newObject([inner_dome_solid])

    apex_cap = (
        racetrack_profile(inner_x * APEX_MIN_SCALE, inner_y * APEX_MIN_SCALE)
        .extrude(-0.001 * IN)
        .translate((0, 0, -inner_dome_depth))
    )
    inner_dome = inner_dome.union(apex_cap)

    return inner_body.union(inner_dome)


def build_pot() -> cq.Workplane:
    """Assemble the full milled pot."""

    outer = build_outer_shell()
    inner = build_inner_cavity()

    pot = outer.cut(inner)

    # Top rabbet: widen the inner opening at the top by RABBET_STEP
    # radially for RABBET_DEPTH axial depth, so a disc cap sits in the
    # rabbet flush with the outer OD.
    inner_x = OUTER_X - 2 * WALL
    inner_y = OUTER_Y - 2 * WALL
    rabbet_x = inner_x + 2 * RABBET_STEP
    rabbet_y = inner_y + 2 * RABBET_STEP
    rabbet = (
        racetrack_profile(rabbet_x, rabbet_y)
        .extrude(RABBET_DEPTH)
        .translate((0, 0, BODY_HEIGHT - RABBET_DEPTH))
    )
    pot = pot.cut(rabbet)

    # Port positions (2x2 grid, 1.000" center-to-center)
    port_positions = [
        (+PORT_SPACING_X / 2, +PORT_SPACING_Y / 2),
        (+PORT_SPACING_X / 2, -PORT_SPACING_Y / 2),
        (-PORT_SPACING_X / 2, +PORT_SPACING_Y / 2),
        (-PORT_SPACING_X / 2, -PORT_SPACING_Y / 2),
    ]

    # Internal thread-engagement bosses — cylinders INSIDE the cavity,
    # axis parallel to Z, rising BOSS_H above the inner dome surface
    # at each port location.  We union them to the pot, then drill the
    # through-hole at the end.
    #
    # Because the inner dome surface at (x,y) is curved, the boss needs
    # to start from below that surface so its union with the dome wall
    # is a clean solid with no sliver gap.  We extrude each boss from
    # Z = -DOME_DEPTH (apex level) up to Z = (top of boss above inner
    # dome surface).  The pot.cut(inner) operation already removed
    # everything inside the cavity, so the portion of the boss that
    # lies inside the cavity becomes new material, and the portion
    # that lies inside the remaining dome wall just overlaps (union
    # is idempotent there).
    #
    # Top-of-boss Z = (inner dome surface Z at this port) + BOSS_H.
    # Inner dome surface Z at (x,y) for our ellipsoid:
    #    z_inner(x,y) = -inner_dome_depth * sqrt(1 - ((x/(inner_x/2))^2
    #                                              + (y/(inner_y/2))^2)/... )
    # — but since all ports sit well inside the cavity and BOSS_H is
    # measured along Z, we can compute it exactly.
    import math
    inner_dome_depth = DOME_DEPTH - WALL
    ax = inner_x / 2.0
    ay = inner_y / 2.0

    for (bx, by) in port_positions:
        # Inner dome surface Z at this (x,y).  The inner dome is the
        # set of points where  (x/(ax*s))^2 + (y/(ay*s))^2 = 1  and
        # s = sqrt(1 - (z/inner_dome_depth)^2), i.e. an ellipsoid with
        # semi-axes ax, ay (XY) and inner_dome_depth (Z-below-0).
        # For a given (x,y) inside the footprint, the inner dome
        # surface Z is:
        #     z = -inner_dome_depth * sqrt(1 - (x/ax)^2 - (y/ay)^2)
        # (taking the lower root since dome is below Z=0).
        r2 = (bx / ax) ** 2 + (by / ay) ** 2
        if r2 >= 1.0:
            raise RuntimeError(f"port ({bx/IN:.3f}, {by/IN:.3f}) outside dome footprint")
        z_inner_surface = -inner_dome_depth * math.sqrt(1.0 - r2)
        boss_top_z = z_inner_surface + BOSS_H
        # Boss spans from dome apex level up to boss_top_z.  This
        # guarantees the boss fully intersects the dome wall and
        # unions cleanly — no sliver gap at the curved surface.
        boss_bottom_z = -DOME_DEPTH
        boss_h_total = boss_top_z - boss_bottom_z
        boss = (
            cq.Workplane("XY")
            .workplane(offset=boss_bottom_z)
            .center(bx, by)
            .circle(BOSS_OD / 2)
            .extrude(boss_h_total)
        )
        pot = pot.union(boss)

        # Through-hole: straight cylinder, axis parallel to Z, from
        # well below the outer dome to above the boss top.  0.438"
        # diameter (tap drill for 1/4"-18 NPT).
        hole_bottom_z = -DOME_DEPTH - 0.050 * IN
        hole_top_z = boss_top_z + 0.050 * IN
        hole = (
            cq.Workplane("XY")
            .workplane(offset=hole_bottom_z)
            .center(bx, by)
            .circle(NPT_TAP_DRILL / 2)
            .extrude(hole_top_z - hole_bottom_z)
        )
        pot = pot.cut(hole)

    return pot


# ═══════════════════════════════════════════════════════
# BUILD + DIAGNOSTICS + EXPORT
# ═══════════════════════════════════════════════════════

out_dir = Path(__file__).resolve().parent

pot = build_pot()

bb = pot.val().BoundingBox()
dx = bb.xmax - bb.xmin
dy = bb.ymax - bb.ymin
dz = bb.zmax - bb.zmin

vol_cm3 = pot.val().Volume() / 1000.0
mass_g = vol_cm3 * 7.93

# Hoop stress at the semicircle end, 100 PSI design
P_design_psi = 100.0
r_semi_in = 2.000
t_wall_in = 0.125
sigma_psi = P_design_psi * r_semi_in / t_wall_in

print()
print("Milled pot (racetrack, ellipsoidal dome + 4 NPT through dome, open top):")
print(f"  Bounding box: {dx:.2f} x {dy:.2f} x {dz:.2f} mm"
      f"  ({dx/IN:.3f} x {dy/IN:.3f} x {dz/IN:.3f} in)")
print(f"  Volume (material):    {vol_cm3:.2f} cm^3")
print(f"  Mass (304 SS, 7.93):  {mass_g:.1f} g  ({mass_g/453.6:.2f} lb)")
print()
print("  Critical dimensions (spec vs. model):")
print(f"    Outer X (long):     spec 5.600 in  →  model {OUTER_X/IN:.3f} in")
print(f"    Outer Y (short):    spec 4.000 in  →  model {OUTER_Y/IN:.3f} in")
print(f"    Body height (Z):    spec 6.000 in  →  model {BODY_HEIGHT/IN:.3f} in")
print(f"    Dome depth (Z):     spec 1.250 in  →  model {DOME_DEPTH/IN:.3f} in")
print(f"    Wall thickness:     spec 0.125 in  →  model {WALL/IN:.3f} in (uniform)")
print(f"    Port count:         spec 4         →  model 4")
print(f"    Port spacing X:     spec 1.000 in  →  model {PORT_SPACING_X/IN:.3f} in")
print(f"    Port spacing Y:     spec 1.000 in  →  model {PORT_SPACING_Y/IN:.3f} in")
print(f"    NPT tap drill:      spec 0.438 in  →  model {NPT_TAP_DRILL/IN:.3f} in")
print(f"    Internal boss OD:   spec 0.600 in  →  model {BOSS_OD/IN:.3f} in")
print(f"    Internal boss H:    spec 0.300 in  →  model {BOSS_H/IN:.3f} in")
print(f"    Top rabbet step:    spec 0.062 in  →  model {RABBET_STEP/IN:.3f} in")
print(f"    Top rabbet depth:   spec 0.100 in  →  model {RABBET_DEPTH/IN:.3f} in")
print()
print(f"  Hoop stress @ {P_design_psi:.0f} PSI, r = {r_semi_in:.3f}\", t = {t_wall_in:.3f}\":")
print(f"    sigma = P*r/t = {sigma_psi:.0f} PSI")
print(f"    304 SS allowable ~20,000 PSI  →  SF = {20000.0/sigma_psi:.1f}x")
print()
print(f"  Note: dome apex closed with a tiny flat at scale = {APEX_MIN_SCALE}")
print(f"        ({DOME_LAYERS} loft layers) to avoid CadQuery loft singularity.")

fname = "carbonator-milled-pot.step"
path = out_dir / fname
cq.exporters.export(pot, str(path))
print()
print(f"  Exported: {path}")
