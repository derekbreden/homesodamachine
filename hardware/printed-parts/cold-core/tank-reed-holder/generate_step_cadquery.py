"""Carbonator tank reed-holder strip.

Vertical printed PETG strip that hugs the outside of the carbonator's
316L SS pressure-vessel wall and holds 3 reed switches for level sensing.
The reeds detect the position of an internal magnetic donut float that
slides up and down a 1/8" SS rod welded to the vessel's bottom plate
(316L is austenitic and non-magnetic, so the magnet's field passes
through the tube wall).

Reed count: 3 (low / mid / high).
  - LOW (refill threshold): firmware triggers a pump-on fill cycle.
  - HIGH (full threshold): firmware terminates the fill cycle.
  - MID (diagnostic sentinel): MUST trigger between LOW and HIGH
    within an expected time window during every fill. If LOW
    triggers but MID does not within ~N seconds, the float is
    stuck — firmware aborts the fill rather than overflowing.
    Also gives a coarse fill-rate measurement (LOW→MID time vs
    MID→HIGH time) to detect a clogged inlet or weak pump.

Why 3 (and not 2 or 4):
  - 2 is the control-only minimum; gives no sanity check against a
    stuck float, which is the single failure mode that matters here.
  - 3 adds a meaningful diagnostic at the cost of ~$1 + 1 GPIO + a
    bit of strip length. Net win.
  - 4+ has diminishing returns: the user doesn't see this level
    (no "X% full" display for the carbonator — only flavor reservoirs
    show that). A second mid-point doesn't catch a failure mode that
    the first didn't.

Mounting: the strip is captured by two standard stainless hose clamps
that wrap the SS tube + the strip together (commodity #16 or #20 worm-
drive band clamps). The strip has two clamp-band channels (shallow
transverse grooves on the outer face, 12 mm wide × 1 mm deep) at the
top and bottom of the strip so the clamp band sits in the groove and
can't slide axially. No adhesive. Simple, removable for service before
foam encapsulation, and the hose clamps stay in place during the foam
pour where they get permanently encapsulated alongside the strip.

The strip sits radially against the SS tube at the cardinal +X face
(facing the front of the appliance, opposite the flavor reservoirs
which occupy the ±Z bag pockets). The reed leads route up out of the
top of the strip in a longitudinal wire channel cut into the outer
face of the strip, exiting into the foam pour above the carbonator
where they join the rest of the cold-core harness.

References:
  - hardware/future.md "Level sensing" — carbonator architecture.
  - hardware/printed-parts/cold-core/reservoir/level-sensing.md —
    flavor-reservoir version of the same architecture (with 10 reeds
    and a custom PCB instead of 3 reeds in a printed strip).
  - hardware/bom.md §12 "Level sensing" — Gebildet B0CW9418F6 reed
    switches, 14 mm glass body, 22 per build.
"""

import math
import sys
from pathlib import Path
import cadquery as cq

_here = Path(__file__).resolve().parent
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware")),
)
sys.path.insert(0, str(_here.parent))
from _cadq_export import export_step
from _foam_shell_geometry import (
    tank_outer_radius as _shell_tank_outer_radius,
    tank_height as _shell_tank_height,
    wall_and_floor_thickness as _shell_wall_and_floor_thickness,
)


# ═══════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════


# -------------------------------------------------------
# General
# -------------------------------------------------------
#
# Same coordinate convention as the sibling cold-core parts:
#   +Y vertical (the tank's long axis)
#   +X is the strip's outward radial direction at the cardinal mount
#     position (the strip lives on the +X face of the SS tube)
#   +Z perpendicular to the strip's radial axis (circumferential)
#
# The tank's center axis is on +Y through origin. Y=0 is the floor of
# the surrounding foam shell's tank-copper-shell cavity. The SS tube's
# actual cylinder occupies Y in [below_tank_elbows_height,
# below_tank_elbows_height + tank_height] = [30, 182.4] in tank-copper-
# shell coordinates, but the float's useful water column inside the
# tube is shorter than the tube's outer height (end caps + dead volume
# below the level-sensing rod + air space above the high reed). We
# reference the strip's reed positions to the SS tube's outer-bottom
# Y face for clarity, then offset to the foam-shell coordinate frame
# in main().
xz_plane_y_up = cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, 1, 0))


def _wp_at(x, y, z):
    """A Workplane parallel to the xz plane at world point (x, y, z), normal
    +Y. Use this instead of ``cq.Workplane(xz_plane_y_up).workplane(origin=(x, y, z))``
    — the latter silently drops the Y component, leaving every
    extrusion stuck at world Y=0. Same helper as in ../reservoir/."""
    return cq.Workplane(
        cq.Plane(origin=(x, y, z), xDir=(1, 0, 0), normal=(0, 1, 0))
    )
#
# -------------------------------------------------------


# -------------------------------------------------------
# Tank geometry (imported from the shared geometry module)
# -------------------------------------------------------
#
# tank_outer_radius (63.5 mm) is the OUTER radius of the SS carbonator
# tube — the strip's inner concave face mates flush against this
# cylinder. tank_height (152.4 mm = 6") is the tube's outer length;
# the float's useful Y travel is shorter (see USEFUL_RANGE constants
# below).
tank_outer_radius = _shell_tank_outer_radius
tank_height = _shell_tank_height
#
# -------------------------------------------------------


# -------------------------------------------------------
# Reed switch (Gebildet B0CW9418F6) body geometry
# -------------------------------------------------------
#
# 14 mm glass tube, ~2.0 mm OD typical for this NO reed style. We
# size the press-fit pocket slightly oversize to accept the glass
# tube without crushing it during install. The press-fit comes from
# the pocket's two short walls clamping the body, not from squeezing
# the glass. Use a small interference on the SHORT axis only (the
# axis perpendicular to the pocket length), with generous slip-fit
# on the long axis and a snug fit on the depth.
REED_BODY_LENGTH = 14.0          # along the strip's Y axis (vertical)
REED_BODY_DIAMETER = 2.0         # nominal OD of the glass tube; pocket short-axis = this + a tiny bit
#
# Pocket size: 14 mm long × 3 mm wide (Z) × 3 mm deep (X-radial).
# The 3 × 3 cross-section accepts the ~2 mm glass tube with 0.5 mm
# slack on each short axis — light press-fit via PETG layer-line
# friction, not interference. (A true interference fit on glass is a
# bad idea: glass cracks before PETG yields.) The reeds are foam-
# encapsulated soon after install, so the pocket's job is just to hold
# the reed in position during the foam pour, not for life of service.
REED_POCKET_LENGTH = 14.0        # along Y (vertical)
REED_POCKET_WIDTH = 3.0          # along Z (circumferential)
REED_POCKET_DEPTH = 3.0          # along X (radial, into the strip)
#
# -------------------------------------------------------


# -------------------------------------------------------
# Reed count + spacing
# -------------------------------------------------------
#
# 3 reeds: LOW (refill threshold), MID (diagnostic sentinel), HIGH
# (full threshold).
#
# Useful water-column Y range inside the tank: the tube is 152.4 mm
# tall outer dimension. End caps consume ~6 mm each (1/4" plates),
# leaving ~140 mm of interior height. The level-sensing rod's anchor
# weld + the float's own height consume another ~10 mm of dead range
# at the bottom; the float can't ride higher than the underside of
# the top plate's interior register, taking another ~5–10 mm at the
# top. Useful float Y range inside the tube is ~120 mm.
#
# In strip-local coordinates (Y measured from the strip's bottom
# face), the strip's bottom is aligned to the SS tube's outer bottom
# face, plus a small margin. Reeds sit at:
#   LOW:  ~25 mm above the strip's bottom (= ~25 mm above tube outer
#         bottom = ~19 mm above tube interior bottom, ~9 mm above the
#         float's lowest position = pump-on threshold).
#   HIGH: ~25 mm below the strip's top (= ~25 mm below tube outer
#         top = ~19 mm below tube interior top, accounting for end-
#         cap dead range = ~9 mm below the float's highest position
#         = pump-off threshold, with a margin against overshoot).
#   MID:  centered between LOW and HIGH.
#
# Strip total Y length = HIGH position + ~10 mm of margin above the
# top reed pocket (for the wire channel routing + a small flange).
REED_COUNT = 3
LOW_REED_Y = 25.0                                          # strip-local Y of the LOW reed pocket center
HIGH_REED_Y = tank_height - 25.0                           # strip-local Y of the HIGH reed pocket center
MID_REED_Y = (LOW_REED_Y + HIGH_REED_Y) / 2.0              # midpoint between LOW and HIGH
REED_Y_POSITIONS = (LOW_REED_Y, MID_REED_Y, HIGH_REED_Y)   # bottom-up
#
# Pitch implied by the above (~50 mm between adjacent reeds at the
# current tank_height); informational only — the positions are
# anchored to LOW and HIGH rather than to a fixed pitch, so the
# layout adapts automatically if tank_height ever changes.
REED_PITCH = HIGH_REED_Y - MID_REED_Y                      # ≈ (tank_height − 50) / 2
#
# -------------------------------------------------------


# -------------------------------------------------------
# Strip footprint (radial, circumferential, axial)
# -------------------------------------------------------
#
# RADIAL: the strip is bounded by two concentric cylinders sharing
# the tank's axis. Inner cylinder = tank_outer_radius (63.5 mm) so
# the strip's concave inner face mates flush against the SS tube.
# Outer cylinder = inner + STRIP_RADIAL_THICKNESS. Bringing the reed
# pocket's bottom (radially deepest face) close to the SS tube
# minimizes the magnet-to-reed gap.
#
# The reed pocket consumes REED_POCKET_DEPTH (3 mm) of the strip's
# radial thickness. We add 2 mm of PETG behind the pocket as a back
# wall (so the pocket isn't open on the outer face) and ~0 mm of
# PETG in front (the reed sits right against the SS tube — the
# pocket's inner-radial face is the same cylinder as the strip's
# inner face). Net strip thickness = REED_POCKET_DEPTH + back wall:
STRIP_BACK_WALL_THICKNESS = 2.0
STRIP_RADIAL_THICKNESS = REED_POCKET_DEPTH + STRIP_BACK_WALL_THICKNESS  # 5 mm
strip_outer_radius = tank_outer_radius + STRIP_RADIAL_THICKNESS         # 68.5
#
# CIRCUMFERENTIAL: the strip's angular extent. Wide enough for the
# reed pocket (3 mm) plus a small flange on each side for the hose-
# clamp groove walls and overall strip stiffness. 18 mm of arc length
# at the tank's outer radius corresponds to an angular extent of
# 18 / 63.5 ≈ 0.283 rad ≈ 16.2°. Strip is centered on the +X axis
# (z = 0).
STRIP_ARC_LENGTH = 18.0
strip_half_angle = STRIP_ARC_LENGTH / 2.0 / tank_outer_radius   # rad, half-angle subtended at tank axis
#
# AXIAL: the strip extends from a few mm below LOW to a few mm above
# HIGH, with end caps that carry the hose-clamp grooves.
STRIP_END_MARGIN_BELOW = 15.0   # margin below LOW reed for the bottom hose-clamp groove
STRIP_END_MARGIN_ABOVE = 15.0   # margin above HIGH reed for the top hose-clamp groove + wire exit
STRIP_BOTTOM_Y = LOW_REED_Y - STRIP_END_MARGIN_BELOW           # strip-local Y of the strip's bottom face
STRIP_TOP_Y = HIGH_REED_Y + STRIP_END_MARGIN_ABOVE             # strip-local Y of the strip's top face
STRIP_LENGTH = STRIP_TOP_Y - STRIP_BOTTOM_Y                    # total Y span
#
# -------------------------------------------------------


# -------------------------------------------------------
# Hose-clamp grooves
# -------------------------------------------------------
#
# Two transverse channels in the strip's outer face accept commodity
# stainless worm-drive band clamps (size #16 / #20, ~12 mm band
# width). The band wraps the SS tube circumferentially and crosses
# the strip's outer face in the groove; the groove walls prevent the
# clamp from sliding axially during the foam pour and during service.
#
# Groove cross-section: 12.5 mm wide along Y (Z direction in the
# tank frame), 1.0 mm deep radially. The 12.5 mm width accepts a
# nominal 12 mm band with light side clearance. The 1 mm depth is
# enough to capture the band edge without weakening the strip.
HOSE_CLAMP_BAND_WIDTH = 12.5
HOSE_CLAMP_GROOVE_DEPTH = 1.0
#
# Groove positions: centered axially at the strip's bottom-margin
# midpoint and the strip's top-margin midpoint, so the band lands
# below LOW and above HIGH and clears every reed pocket.
HOSE_CLAMP_LOW_Y = (STRIP_BOTTOM_Y + LOW_REED_Y) / 2.0   # centered in the bottom margin
HOSE_CLAMP_HIGH_Y = (HIGH_REED_Y + STRIP_TOP_Y) / 2.0    # centered in the top margin
HOSE_CLAMP_Y_POSITIONS = (HOSE_CLAMP_LOW_Y, HOSE_CLAMP_HIGH_Y)
#
# -------------------------------------------------------


# -------------------------------------------------------
# Wire channel (longitudinal)
# -------------------------------------------------------
#
# A small longitudinal channel cut into the OUTER face of the strip
# carries the reed leads upward to the top of the strip, where they
# exit into the foam pour above the tank. Channel is along Y, ~2 mm
# wide (Z) × 1 mm deep (X), offset to one side of the reed pockets
# so it doesn't intersect them.
#
# 6 reed leads (2 per reed × 3 reeds) easily fit in a 2 mm channel
# at this gauge (~28 AWG silicone-insulated, ~1.2 mm OD).
WIRE_CHANNEL_WIDTH = 2.0          # Z (circumferential)
WIRE_CHANNEL_DEPTH = 1.0          # X (radial, into the outer face)
WIRE_CHANNEL_Z_OFFSET = 4.0       # +Z offset of the channel's center from the reed-pocket centerline (z=0)
#
# Wire channel runs from the bottom of the lowest reed pocket up to
# the top face of the strip — every reed lead pair joins the channel
# at the height of its reed.
WIRE_CHANNEL_BOTTOM_Y = LOW_REED_Y - REED_POCKET_LENGTH / 2.0   # bottom edge of the LOW pocket
WIRE_CHANNEL_TOP_Y = STRIP_TOP_Y                                  # top face of the strip
#
# -------------------------------------------------------


# ═══════════════════════════════════════════════════════
# BUILD HELPERS
# ═══════════════════════════════════════════════════════


def _build_curved_strip_blank(bottom_y, top_y, r_inner, r_outer,
                              half_angle):
    """Build the strip's curved outer envelope as the angular wedge of an
    annulus, swept along Y. Inner radius = r_inner, outer radius =
    r_outer, angular half-extent = half_angle radians on either side of
    the +X axis (z = 0), Y range [bottom_y, top_y].

    Implementation: build the 2D wedge profile in the XZ plane (an
    annulus sector) and extrude it along +Y. The wedge profile has
    four bounding edges:
      - outer arc on r_outer from (r_outer cos(-h), r_outer sin(-h))
        through (r_outer, 0) to (r_outer cos(+h), r_outer sin(+h))
      - inner arc on r_inner from (r_inner cos(+h), r_inner sin(+h))
        through (r_inner, 0) to (r_inner cos(-h), r_inner sin(-h))
        (traversed in the opposite angular direction to close the wedge)
      - two radial line segments at z = ±r·sin(h), connecting the
        endpoints of the two arcs.

    z (sign convention): on xz_plane_y_up, the workplane's local Y is
    along world −Z (the plane's normal is +Y, xDir = +X). So a
    workplane local-Y value of +h*r corresponds to world z = −h*r.
    Build the profile in world (x, z) and let the workplane handle the
    mapping by flipping the z component when emitting workplane-local
    points.
    """
    # Workplane in the XZ plane (Y up). Sketch points are emitted as
    # (workplane_local_x, workplane_local_y) = (world_x, −world_z).
    def wp_xy(world_x, world_z):
        return (world_x, -world_z)

    # Endpoints (world coords) at the four arc/line corners.
    x_outer_pz = r_outer * math.cos(half_angle)   # +z side, outer
    z_outer_pz = r_outer * math.sin(half_angle)
    x_outer_nz = x_outer_pz                       # −z side, outer
    z_outer_nz = -z_outer_pz
    x_inner_pz = r_inner * math.cos(half_angle)
    z_inner_pz = r_inner * math.sin(half_angle)
    x_inner_nz = x_inner_pz
    z_inner_nz = -z_inner_pz

    profile = (
        cq.Workplane(xz_plane_y_up)
        .moveTo(*wp_xy(x_outer_nz, z_outer_nz))
        # outer arc from (-z corner) through +X apex to (+z corner)
        .threePointArc(wp_xy(r_outer, 0.0), wp_xy(x_outer_pz, z_outer_pz))
        # +z radial line: outer corner inward to inner corner
        .lineTo(*wp_xy(x_inner_pz, z_inner_pz))
        # inner arc back from (+z corner) through +X apex to (-z corner)
        .threePointArc(wp_xy(r_inner, 0.0), wp_xy(x_inner_nz, z_inner_nz))
        # close: −z radial line, inner corner outward to outer corner
        .close()
    )
    # Extrude UP by the strip's Y length, starting at bottom_y. CadQuery's
    # default extrude direction is the workplane normal (+Y here), so we
    # translate the profile up to bottom_y before extruding.
    return profile.extrude(top_y - bottom_y).translate((0, bottom_y, 0))


def _build_reed_pocket_cutter(reed_center_y):
    """Build the negative-volume cutter for one reed pocket centered at
    (x = tank_outer_radius + REED_POCKET_DEPTH/2, y = reed_center_y, z = 0).

    The pocket is a rectangular slot oriented with its long axis along
    Y. Open on the inner-radial face (where the reed body presses
    against the SS tube) and closed on the back wall + on all four
    perimeter walls. Build as a Y-extruded XZ rectangle, then position.

    Pocket inner-radial face = tank_outer_radius (the strip's inner
    face). Pocket back wall = tank_outer_radius + REED_POCKET_DEPTH.
    Pocket Z extent = ± REED_POCKET_WIDTH/2 around z = 0.
    """
    # Rectangle in the XZ plane: X = [tank_outer_radius,
    # tank_outer_radius + REED_POCKET_DEPTH], Z = [-W/2, +W/2].
    x_min = tank_outer_radius
    x_max = tank_outer_radius + REED_POCKET_DEPTH
    z_half = REED_POCKET_WIDTH / 2.0
    y_min = reed_center_y - REED_POCKET_LENGTH / 2.0
    cutter_height = REED_POCKET_LENGTH
    return (
        cq.Workplane(xz_plane_y_up)
        .moveTo((x_min + x_max) / 2.0, 0)
        # rect(width_along_local_x, width_along_local_y)
        # local X = world X, local Y = −world Z, so rect width along
        # local Y corresponds to world Z extent.
        .rect(x_max - x_min, REED_POCKET_WIDTH)
        .extrude(cutter_height)
        .translate((0, y_min, 0))
    )


def _build_hose_clamp_groove_cutter(groove_center_y):
    """Build the negative-volume cutter for one hose-clamp groove. The
    groove is a transverse channel along Z (circumferential) in the
    strip's outer face, HOSE_CLAMP_BAND_WIDTH wide in Y and
    HOSE_CLAMP_GROOVE_DEPTH deep radially.

    Built as a thin angular wedge of an annulus (matching the strip's
    own cross-section) at the outer face, swept along Y. The cutter's
    radial extent is [strip_outer_radius − HOSE_CLAMP_GROOVE_DEPTH,
    strip_outer_radius + 1.0] — the small +1 mm outside the strip
    keeps the cut clean past the surface even with rounding noise.

    Angular extent: same as the strip (so the groove crosses the
    strip's entire outer face).
    """
    r_inner = strip_outer_radius - HOSE_CLAMP_GROOVE_DEPTH
    r_outer = strip_outer_radius + 1.0
    return _build_curved_strip_blank(
        bottom_y=groove_center_y - HOSE_CLAMP_BAND_WIDTH / 2.0,
        top_y=groove_center_y + HOSE_CLAMP_BAND_WIDTH / 2.0,
        r_inner=r_inner,
        r_outer=r_outer,
        half_angle=strip_half_angle,
    )


def _build_wire_channel_cutter():
    """Build the negative-volume cutter for the longitudinal wire
    channel on the strip's outer face. The channel is a rectangular
    slot oriented along Y, offset in Z, recessed radially.

    Implementation: a small box in (x, y, z) world coords with x range
    spanning the channel depth into the strip's outer face. Built as a
    Y-extruded XZ rectangle.

    The +Z offset places the channel beside the reed pockets (which
    are centered at z = 0); the channel never intersects a pocket.
    """
    z_center = WIRE_CHANNEL_Z_OFFSET
    z_half = WIRE_CHANNEL_WIDTH / 2.0
    x_min = strip_outer_radius - WIRE_CHANNEL_DEPTH
    x_max = strip_outer_radius + 1.0     # over-cut slightly past the outer surface
    return (
        cq.Workplane(xz_plane_y_up)
        .moveTo((x_min + x_max) / 2.0, -z_center)   # local Y = −world Z
        .rect(x_max - x_min, WIRE_CHANNEL_WIDTH)
        .extrude(WIRE_CHANNEL_TOP_Y - WIRE_CHANNEL_BOTTOM_Y)
        .translate((0, WIRE_CHANNEL_BOTTOM_Y, 0))
    )


# ═══════════════════════════════════════════════════════
# TOP-LEVEL BUILD
# ═══════════════════════════════════════════════════════


def build_tank_reed_holder():
    """Build the tank reed-holder strip as a single PETG part.

    Steps:
      1. Build the strip's curved blank (annular-sector prism).
      2. Cut REED_COUNT reed pockets into the inner face.
      3. Cut two hose-clamp grooves into the outer face.
      4. Cut the longitudinal wire channel into the outer face.

    Returned object is in strip-local coordinates (Y measured from the
    strip's bottom face; the tank's axis is on +Y through origin).
    """
    strip = _build_curved_strip_blank(
        bottom_y=STRIP_BOTTOM_Y,
        top_y=STRIP_TOP_Y,
        r_inner=tank_outer_radius,
        r_outer=strip_outer_radius,
        half_angle=strip_half_angle,
    )

    # Reed pockets (one per reed)
    for reed_y in REED_Y_POSITIONS:
        strip = strip.cut(_build_reed_pocket_cutter(reed_y))

    # Hose-clamp grooves
    for clamp_y in HOSE_CLAMP_Y_POSITIONS:
        strip = strip.cut(_build_hose_clamp_groove_cutter(clamp_y))

    # Wire channel
    strip = strip.cut(_build_wire_channel_cutter())

    return strip


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════


def main():
    strip = build_tank_reed_holder()
    out_path = _here / "tank-reed-holder.step"
    export_step(strip, str(out_path))
    print(f"-> {out_path.name}")


if __name__ == "__main__":
    main()
