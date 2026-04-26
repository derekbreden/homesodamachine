"""
Dispense flavor tube — bent 1/4" OD 304 SS visual-companion tube.

PURPOSE
=======
Two of these bent stainless tubes flank the existing factory gooseneck on a
Westbrass A2031-NL-62 8" Touch-Flo cold-water dispenser faucet (see
`hardware/purchases.md` §7 — A2031-NL-62, ASIN B0BXFW1J38, ACQUIRED). They
pass through 1/4" holes drilled in the back of the faucet's MOUNTING PLATE
(opposite the user) and arch up-and-over to terminate at roughly the same
height + forward reach as the factory spout tip. Each tube carries one
flavor injection line. The factory faucet is kept 100% intact — no harvest,
no machining of the faucet body.

THIS STEP IS FOR XOMETRY ROUGH-QUOTING ONLY
============================================
Geometry is approximate. Final dimensions await physical measurement of
the installed faucet. Goal here is a price + lead-time ballpark for tube
bending + powder coating, not a production-ready part.

ASSUMPTIONS (to be refined against the physical part)
=====================================================
Westbrass does not publish a dimensioned drawing for the A2031 gooseneck.
We back the geometry out from the "8\"" model designation + the standard
Touch-Flo silhouette (apex of arc above deck ≈ "8 inch" model name;
factory spout tip exits below the apex pointing downward):

  - Bend centerline radius: 60 mm (~2.36") — well above Xometry's
    0.500" (12.7 mm) min CLR; gives a reach of 2*R = ~120 mm (~4.7")
    forward of the deck-mount, matching typical Touch-Flo silhouette.
  - Bend sweep angle: 180° (vertical-up → vertical-down)
  - Bottom straight (rises from the mounting plate):  165 mm
  - Tip straight (downward at dispense end):           15 mm
  - Resulting apex height above deck: 165 + 60 = 225 mm (~8.86")
  - Resulting tip height above deck:  165 - 15 = 150 mm (~5.9")
  - Resulting forward reach to tip:   2 * 60 = 120 mm (~4.7")

Tolerance on any of these: ±10 mm. That is fine for an instant quote.
The Xometry quoter reads the geometry, snaps to standard sizes, and
returns a price; ±10 mm does not change the price tier.

Tolerance on any of these: ±10 mm. That is fine for an instant quote.
The Xometry quoter reads the geometry, snaps to standard sizes, and
returns a price; ±10 mm does not change the price tier.

XOMETRY DFM COMPLIANCE
======================
Per `hardware/harvested/touch-flo-faucet/xometry-submission-notes.md`:
  - Tube: 1/4" OD (6.35 mm) × 0.035" wall (0.889 mm) — thinner of the
    two standard 1/4" wall options
  - Min centerline bend radius: 0.500" (12.7 mm) — we use 60 mm
  - Min straight between bends: 0.500" (12.7 mm) — only one bend in
    this part, so the constraint is the end-straights, both >= 15 mm
  - One single-solid STEP per tube, AP214 (CadQuery default), in mm
  - Square ends, no fittings

QUOTE SUBMISSION
================
Upload this single STEP, set quantity = 2 (one tube per flavor side for
one machine). Material: 304 SS. Wall: 0.035". Finish: powder coat,
matte black RAL 9005 (matches the A2031-NL-62 matte-black faucet).

Run with: tools/cad-venv/bin/python generate_step_cadquery.py
"""

from pathlib import Path
import math

import cadquery as cq


# ═══════════════════════════════════════════════════════
# CONSTANTS — TUBE STOCK
# ═══════════════════════════════════════════════════════

IN = 25.4  # mm per inch

OD = 0.250 * IN          # 6.35 mm — 1/4" OD
WALL = 0.035 * IN        # 0.889 mm — thinner of two Xometry 1/4" walls
ID = OD - 2.0 * WALL     # 4.572 mm

# ═══════════════════════════════════════════════════════
# CONSTANTS — GOOSENECK GEOMETRY (approximate)
# ═══════════════════════════════════════════════════════

# Centerline geometry of the bent tube. Coordinate system:
#   +Z = up (vertical away from the deck)
#   +X = forward (away from the back of the faucet, toward the user)
#   Y  = unused (tube lies in the X-Z plane)

BOTTOM_STRAIGHT_LEN = 165.0   # mm — vertical riser, passes through mounting plate
TIP_STRAIGHT_LEN = 15.0       # mm — downward at the dispense end
BEND_RADIUS = 60.0            # mm — centerline radius of the gooseneck arc
BEND_SWEEP_DEG = 180.0        # vertical-up → vertical-down

# Sanity envelope (informational only; not enforced):
#   Overall height = BOTTOM_STRAIGHT_LEN + BEND_RADIUS + (BEND_RADIUS - 0) wait
#   Actually for a 180° arc starting tangent to +Z and ending tangent to -Z:
#     arc tops out at z = BOTTOM_STRAIGHT_LEN + BEND_RADIUS
#     arc tip ends at  z = BOTTOM_STRAIGHT_LEN, x = 2*BEND_RADIUS
#     tip straight drops to z = BOTTOM_STRAIGHT_LEN - TIP_STRAIGHT_LEN

# ═══════════════════════════════════════════════════════
# DFM SANITY CHECKS
# ═══════════════════════════════════════════════════════

MIN_CLR_MM = 0.500 * IN      # 12.7 mm — Xometry min centerline bend radius
MIN_STRAIGHT_MM = 0.500 * IN # 12.7 mm — Xometry min straight

assert BEND_RADIUS >= MIN_CLR_MM, (
    f"Bend radius {BEND_RADIUS} mm below Xometry min CLR {MIN_CLR_MM} mm"
)
assert BOTTOM_STRAIGHT_LEN >= MIN_STRAIGHT_MM, (
    f"Bottom straight {BOTTOM_STRAIGHT_LEN} mm below min {MIN_STRAIGHT_MM} mm"
)
assert TIP_STRAIGHT_LEN >= MIN_STRAIGHT_MM, (
    f"Tip straight {TIP_STRAIGHT_LEN} mm below min {MIN_STRAIGHT_MM} mm"
)


# ═══════════════════════════════════════════════════════
# GEOMETRY BUILDERS
# ═══════════════════════════════════════════════════════

def make_centerline_path() -> cq.Workplane:
    """Build the centerline as a 2D wire in the X-Z plane:
        - vertical straight up (length BOTTOM_STRAIGHT_LEN)
        - tangent arc (radius BEND_RADIUS, sweep BEND_SWEEP_DEG)
        - vertical straight down (length TIP_STRAIGHT_LEN)

    The sweep starts tangent to +Z (going up) and (for 180°) ends
    tangent to -Z (coming down) at x = 2*BEND_RADIUS.
    """
    # Key waypoints in the X-Z plane:
    p0 = (0.0, 0.0)                                           # start of bottom straight
    p1 = (0.0, BOTTOM_STRAIGHT_LEN)                           # end of bottom straight / start of arc
    arc_center = (BEND_RADIUS, BOTTOM_STRAIGHT_LEN)           # center of bend
    sweep_rad = math.radians(BEND_SWEEP_DEG)
    # Arc parameterized from angle pi (left of center) sweeping toward angle 0 (right of center)
    # for a 180° clockwise-when-viewed-from-+Y bend. Use a midpoint to fully specify.
    mid_angle = math.pi - (sweep_rad / 2.0)
    p_mid = (
        arc_center[0] + BEND_RADIUS * math.cos(mid_angle),
        arc_center[1] + BEND_RADIUS * math.sin(mid_angle),
    )
    end_angle = math.pi - sweep_rad
    p2 = (
        arc_center[0] + BEND_RADIUS * math.cos(end_angle),
        arc_center[1] + BEND_RADIUS * math.sin(end_angle),
    )
    # Tip straight: continue tangent from p2. At end_angle = 0, tangent is -Z.
    # General tangent direction (continuing the sweep): rotate radial by -90°.
    tangent = (math.sin(end_angle), -math.cos(end_angle))
    p3 = (
        p2[0] + tangent[0] * TIP_STRAIGHT_LEN,
        p2[1] + tangent[1] * TIP_STRAIGHT_LEN,
    )

    # Build the path as a single wire on the XZ plane.
    # CadQuery's "XZ" workplane: local (x, y) maps to world (x, z).
    path = (
        cq.Workplane("XZ")
        .moveTo(*p0)
        .lineTo(*p1)
        .threePointArc(p_mid, p2)
        .lineTo(*p3)
    )
    return path


def make_bent_tube() -> cq.Workplane:
    """Sweep an annular cross-section (1/4" OD, 0.035" wall) along the
    gooseneck centerline path. Produces a single hollow solid with
    square-cut ends.
    """
    path = make_centerline_path()

    # Build the cross-section on a workplane perpendicular to the start
    # of the path. The path starts going +Z, so a workplane normal to +Z
    # at the origin is correct. Use cq.Workplane("XY") which has +Z normal.
    profile = (
        cq.Workplane("XY")
        .circle(OD / 2.0)
        .circle(ID / 2.0)
    )

    tube = profile.sweep(path, transition="round")
    return tube


# ═══════════════════════════════════════════════════════
# BUILD + DIAGNOSTICS + EXPORT
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent

    tube = make_bent_tube()

    bb = tube.val().BoundingBox()
    dx = bb.xmax - bb.xmin
    dy = bb.ymax - bb.ymin
    dz = bb.zmax - bb.zmin

    vol_cm3 = tube.val().Volume() / 1000.0
    mass_g = vol_cm3 * 7.93   # 304 SS density

    # Centerline length (rough): bottom straight + arc + tip straight
    arc_len = BEND_RADIUS * math.radians(BEND_SWEEP_DEG)
    centerline_len = BOTTOM_STRAIGHT_LEN + arc_len + TIP_STRAIGHT_LEN

    print()
    print("Dispense flavor tube — bent 1/4\" OD 304 SS")
    print(f"  Stock:        {OD/IN:.3f}\" OD × {WALL/IN:.3f}\" wall")
    print(f"                ({OD:.3f} mm OD × {WALL:.3f} mm wall, ID {ID:.3f} mm)")
    print(f"  Centerline:   {centerline_len:.1f} mm  ({centerline_len/IN:.2f}\")")
    print(f"                bottom {BOTTOM_STRAIGHT_LEN} + arc {arc_len:.1f} (R{BEND_RADIUS}, {BEND_SWEEP_DEG}°) + tip {TIP_STRAIGHT_LEN}")
    print(f"  Bounding box: {dx:.1f} × {dy:.1f} × {dz:.1f} mm")
    print(f"                ({dx/IN:.2f} × {dy/IN:.2f} × {dz/IN:.2f} in)")
    print(f"  Volume:       {vol_cm3:.2f} cm³")
    print(f"  Mass (304 SS, 7.93 g/cm³): {mass_g:.1f} g")

    fname = "dispense-flavor-tube-quarter-od-0p035wall.step"
    path = out_dir / fname
    cq.exporters.export(tube, str(path))
    print(f"  Exported:     {path}")
