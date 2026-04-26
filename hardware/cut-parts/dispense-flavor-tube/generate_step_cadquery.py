"""
Dispense flavor tube — bent 1/4" OD 304 SS visual-companion tube.

PURPOSE
=======
Two of these bent stainless tubes flank the existing factory gooseneck on a
Westbrass A2031-NL-62 8" Touch-Flo cold-water dispenser faucet (see
`hardware/purchases.md` §7 — A2031-NL-62, ASIN B0BXFW1J38, ACQUIRED). They
pass through 1/4" holes drilled in the back of the faucet's MOUNTING PLATE
(opposite the user) and arch up-and-over to terminate near the factory
spout tip. Each tube carries one flavor injection line. The factory faucet
is kept 100% intact — no harvest, no machining of the faucet body.

THIS STEP IS FOR XOMETRY ROUGH-QUOTING ONLY
============================================
Geometry is approximate, hand-eyeballed by the user against the installed
faucet on 2026-04-24. Final dimensions await physical measurement (and
ideally a refinement pass against a dimensioned product drawing or a
photo-measurement agent run). Goal here is a price + lead-time ballpark
for tube bending + powder coating, not a production-ready part.

GEOMETRY (per user, 2026-04-24)
================================
Two-bend gooseneck, bottom-up:

  1. 105 mm vertical straight at the bottom
       (= 40 mm extension below the mounting-plate base
        + 65 mm above the base, before the first bend starts)
  2. 30° bend, centerline radius 31.75 mm  (1.25", was 40 mm — Xometry caps CLR/OD at 5:1)
  3. 100 mm straight (rises forward at 30° from vertical)
  4. 90° bend, centerline radius 31.75 mm  (same)
  5. 15 mm tip straight (continues forward + downward)

Coordinate system:
  +Z = up (vertical away from the deck)
  +X = forward (toward the user, away from the back of the faucet)
   Y = unused (tube lies in the X-Z plane)

The deck (faucet base) sits at Z = 40, since the bottom 40 mm of the tube
extends below the deck. Apex of the bent path lands at roughly Z = 222 mm
(8.7" above the tube bottom, or 7.2" above the deck). Forward reach to
the tip lands at roughly X = 130 mm (~5.1") forward of the deck-mount.

XOMETRY DFM COMPLIANCE
======================
Per `hardware/harvested/touch-flo-faucet/xometry-submission-notes.md`:
  - Tube: 1/4" OD (6.35 mm) × 0.035" wall (0.889 mm) — thinner of the
    two standard 1/4" wall options
  - Min centerline bend radius: 0.500" (12.7 mm) — both bends are above
  - Min straight between bends: 0.500" (12.7 mm) — all straights are above
  - One single-solid STEP per tube, AP214 (CadQuery default), in mm
  - Square ends, no fittings

QUOTE SUBMISSION
================
Upload this single STEP, set quantity = 2 (one tube per flavor side for
one machine). Material: 304 SS. Wall: 0.035". Finish: powder coat,
matte black (RAL 9005 or 9011) to match the A2031-NL-62 matte-black faucet.
Attach a one-page drawing PDF requesting grit-blast pre-treatment per the
submission notes (passive 304 SS resists powder adhesion without it).

Run with: tools/cad-venv/bin/python generate_step_cadquery.py
"""

from pathlib import Path
import math
from dataclasses import dataclass

import cadquery as cq


# ═══════════════════════════════════════════════════════
# CONSTANTS — TUBE STOCK
# ═══════════════════════════════════════════════════════

IN = 25.4  # mm per inch

OD = 0.250 * IN          # 6.35 mm — 1/4" OD
# Xometry's live quoter rejected the OD/wall combo at 0.035" wall as not
# in their bender's tube-stock library; bumped to 0.049" (next standard up).
WALL = 0.049 * IN        # 1.245 mm
ID = OD - 2.0 * WALL     # 3.861 mm

# ═══════════════════════════════════════════════════════
# CONSTANTS — GOOSENECK GEOMETRY (per user, 2026-04-24)
# ═══════════════════════════════════════════════════════

# Bottom straight = 40 mm below deck + 65 mm above deck.
BOTTOM_STRAIGHT_LEN = 105.0   # mm

# First bend: gentle forward lean.
# Xometry's quoter requires CLR-to-OD ratio between 2:1 and 5:1 AND
# CLR in 0.25" increments. 1.25" (31.75 mm) is exactly 5:1 — at the
# upper edge, but explicitly listed as a valid CLR option for 0.25" OD
# in Xometry's tube-bending DFM page. Closest legal value to the user's
# original 40 mm eyeball.
BEND1_RADIUS = 1.25 * IN      # 31.75 mm — 5:1 CLR/OD, 0.25" increment
BEND1_SWEEP_DEG = 30.0

MID_STRAIGHT_LEN = 100.0      # mm — rises forward at 30° from vertical

# Second bend: arches forward and over.
BEND2_RADIUS = 1.25 * IN      # 31.75 mm — same justification as BEND1
BEND2_SWEEP_DEG = 90.0

TIP_STRAIGHT_LEN = 15.0       # mm — continues forward + downward at 60° below horizontal


# ═══════════════════════════════════════════════════════
# DFM SANITY CHECKS
# ═══════════════════════════════════════════════════════

MIN_CLR_MM = 0.500 * IN      # 12.7 mm — Xometry min centerline bend radius
MIN_STRAIGHT_MM = 0.500 * IN # 12.7 mm — Xometry min straight

assert BEND1_RADIUS >= MIN_CLR_MM, (
    f"Bend 1 radius {BEND1_RADIUS} mm below Xometry min CLR {MIN_CLR_MM} mm"
)
assert BEND2_RADIUS >= MIN_CLR_MM, (
    f"Bend 2 radius {BEND2_RADIUS} mm below Xometry min CLR {MIN_CLR_MM} mm"
)
for name, length in [
    ("bottom straight", BOTTOM_STRAIGHT_LEN),
    ("mid straight", MID_STRAIGHT_LEN),
    ("tip straight", TIP_STRAIGHT_LEN),
]:
    assert length >= MIN_STRAIGHT_MM, (
        f"{name.capitalize()} {length} mm below min {MIN_STRAIGHT_MM} mm"
    )


# ═══════════════════════════════════════════════════════
# 2-D PATH WALKER
# ═══════════════════════════════════════════════════════
#
# The centerline lives in the X-Z plane. We walk along it segment by
# segment, accumulating waypoints that CadQuery will stitch into a wire.
# Each "right-bending" arc curves toward +X (the forward direction),
# which matches a single-plane gooseneck.

@dataclass
class Walker:
    """Mutable cursor on the X-Z plane: position + unit tangent."""
    x: float = 0.0
    z: float = 0.0
    tx: float = 0.0   # tangent x
    tz: float = 1.0   # tangent z (default: pointing +Z)

    @property
    def pos(self) -> tuple[float, float]:
        return (self.x, self.z)


def perpendicular_right(tx: float, tz: float) -> tuple[float, float]:
    """Right-hand perpendicular: rotate (tx, tz) by -90° in the XZ plane.
    For tangent (0, 1) this gives (1, 0) — i.e., points +X (forward),
    matching the inside of a forward-bending arc.
    """
    return (tz, -tx)


def rotate(vx: float, vz: float, theta_rad: float) -> tuple[float, float]:
    """Rotate vector (vx, vz) by +theta_rad in the X-Z plane (CCW
    when viewed from +Y looking toward origin)."""
    c = math.cos(theta_rad)
    s = math.sin(theta_rad)
    return (vx * c - vz * s, vx * s + vz * c)


def walk_straight(w: Walker, length: float) -> tuple[float, float]:
    """Advance the walker by `length` along its tangent. Return the
    new position (also stored on the walker)."""
    w.x += w.tx * length
    w.z += w.tz * length
    return w.pos


def walk_arc(w: Walker, radius: float, sweep_deg: float):
    """Advance the walker through a right-bending arc. Returns
    (start, mid, end) waypoints — the three points CadQuery's
    `threePointArc` needs."""
    sweep_rad = math.radians(sweep_deg)

    start = w.pos

    # Center of curvature is to the right of the tangent, at distance radius.
    perp_x, perp_z = perpendicular_right(w.tx, w.tz)
    cx = w.x + perp_x * radius
    cz = w.z + perp_z * radius

    # Vector from center to current position.
    rx = w.x - cx
    rz = w.z - cz

    # For a right-bending arc, the radial vector rotates by -sweep_rad
    # as we sweep along the arc.
    mid_rx, mid_rz = rotate(rx, rz, -sweep_rad / 2.0)
    end_rx, end_rz = rotate(rx, rz, -sweep_rad)

    mid = (cx + mid_rx, cz + mid_rz)
    end = (cx + end_rx, cz + end_rz)

    # Update walker: position is end, tangent rotates by -sweep_rad too.
    w.x, w.z = end
    w.tx, w.tz = rotate(w.tx, w.tz, -sweep_rad)

    return start, mid, end


# ═══════════════════════════════════════════════════════
# GEOMETRY BUILDERS
# ═══════════════════════════════════════════════════════

def make_centerline_path() -> cq.Workplane:
    """Walk the centerline through:
        bottom straight → bend 1 → mid straight → bend 2 → tip straight
    Returns a single 2D wire on the XZ workplane.
    """
    w = Walker()  # starts at (0, 0) pointing +Z

    # Segment 1: bottom straight.
    p_bot_end = walk_straight(w, BOTTOM_STRAIGHT_LEN)

    # Segment 2: first bend.
    _, mid1, end1 = walk_arc(w, BEND1_RADIUS, BEND1_SWEEP_DEG)

    # Segment 3: mid straight.
    p_mid_end = walk_straight(w, MID_STRAIGHT_LEN)

    # Segment 4: second bend.
    _, mid2, end2 = walk_arc(w, BEND2_RADIUS, BEND2_SWEEP_DEG)

    # Segment 5: tip straight.
    p_tip_end = walk_straight(w, TIP_STRAIGHT_LEN)

    # Build the path on the XZ workplane.
    path = (
        cq.Workplane("XZ")
        .moveTo(0.0, 0.0)
        .lineTo(*p_bot_end)
        .threePointArc(mid1, end1)
        .lineTo(*p_mid_end)
        .threePointArc(mid2, end2)
        .lineTo(*p_tip_end)
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
    # at the origin is correct: cq.Workplane("XY") has +Z normal.
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

    arc1_len = BEND1_RADIUS * math.radians(BEND1_SWEEP_DEG)
    arc2_len = BEND2_RADIUS * math.radians(BEND2_SWEEP_DEG)
    centerline_len = (
        BOTTOM_STRAIGHT_LEN + arc1_len + MID_STRAIGHT_LEN + arc2_len + TIP_STRAIGHT_LEN
    )

    print()
    print("Dispense flavor tube — bent 1/4\" OD 304 SS")
    print(f"  Stock:        {OD/IN:.3f}\" OD × {WALL/IN:.3f}\" wall")
    print(f"                ({OD:.3f} mm OD × {WALL:.3f} mm wall, ID {ID:.3f} mm)")
    print(f"  Centerline:   {centerline_len:.1f} mm  ({centerline_len/IN:.2f}\")")
    print(f"                bottom {BOTTOM_STRAIGHT_LEN}"
          f" + arc1 {arc1_len:.1f} (R{BEND1_RADIUS}, {BEND1_SWEEP_DEG}°)"
          f" + mid {MID_STRAIGHT_LEN}"
          f" + arc2 {arc2_len:.1f} (R{BEND2_RADIUS}, {BEND2_SWEEP_DEG}°)"
          f" + tip {TIP_STRAIGHT_LEN}")
    print(f"  Bounding box: {dx:.1f} × {dy:.1f} × {dz:.1f} mm")
    print(f"                ({dx/IN:.2f} × {dy/IN:.2f} × {dz/IN:.2f} in)")
    print(f"  Volume:       {vol_cm3:.2f} cm³")
    print(f"  Mass (304 SS, 7.93 g/cm³): {mass_g:.1f} g")

    fname = "dispense-flavor-tube-quarter-od-0p049wall.step"
    path = out_dir / fname
    cq.exporters.export(tube, str(path))
    print(f"  Exported:     {path}")
