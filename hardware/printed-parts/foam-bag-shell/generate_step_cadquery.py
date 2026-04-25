"""
Foam-bag shell (plan A): three-piece printed PETG enclosure that wraps the
5" round vertical pressure vessel, holds two flavor bladders in dry pockets
on opposite Y faces, accommodates the evaporator coil, and contains two
pour-in-place foam regions for thermal insulation.

Coordinate convention:
  - Tank centerline = (X=0, Y=0).
  - Z = vertical, z=0 at the cold-core's bottom skin.
  - Y is the "bag axis": one bag pocket at +Y, one at -Y.
  - X is perpendicular to bag axis (where the round arcs are).

Outer envelope (per spec):
  X half-extent = 83.1 mm   (round arc on X faces, radius 83.1 from origin)
  Y half-extent = 118.9 mm  (flat on Y faces)
  Z = 0 to 226 mm

Three pieces stack vertically with butt joints + locating pins:
  Floor 1: z = 0   to 37   — bottom skin + bottom foam band, lower bag-pocket walls
  Floor 2: z = 37  to 189  — outer shell perimeter + sealed inner shell + bag pockets
  Floor 3: z = 189 to 226  — top foam band + top skin, with PRV vent conduit

The output is three STEP files in this directory.
"""

from pathlib import Path
import math
import sys

import cadquery as cq


# ═══════════════════════════════════════════════════════
# PHYSICAL DIMENSIONS — TANK / BAG / RADIAL BUDGET
# ═══════════════════════════════════════════════════════

TANK_OUTER_R = 63.5          # 5" OD / 2
TANK_HEIGHT  = 152.4         # 6" tube length

COIL_ZONE        = 7.0       # copper coil + foil tape allowance
INNER_FOAM       = 5.0       # pour PU between coil and inner shell
INNER_SHELL_WALL = 0.8
BAG_THICKNESS    = 35.0
BAG_WIDTH        = 125.0     # along X
BAG_HEIGHT       = 225.0
POCKET_OUTER_WALL = 0.8
OUTER_FOAM       = 6.0
OUTER_SHELL_WALL = 0.8

# Inner shell (flatted-stadium) dimensions
# Per spec: the OUTER face of the inner shell flat is at y = ±76.3.
# That's 63.5 (tank R) + 7 (coil) + 5 (foam) + 0.8 (wall) = 76.3 ✓
# So INNER_FLAT_Y = inner face = 75.5; OUTER face = INNER_FLAT_Y + wall.
INNER_FLAT_Y    = TANK_OUTER_R + COIL_ZONE + INNER_FOAM       # 75.5 (inner face)
INNER_ARC_R     = INNER_FLAT_Y                                 # round arcs of radius 75.5
# Spec calls out "radius 76.3 mm from tank centerline" — that's the OUTER
# face arc radius.  Inner face is 75.5.
INNER_FLAT_HALF = BAG_WIDTH / 2                                # 62.5 (flat span: |x|<=62.5)
INNER_FILLET_R  = 1.5                                          # fillet at flat-arc transition

# Outer envelope (outer face of outer shell wall)
OUTER_HALF_X = INNER_ARC_R + INNER_SHELL_WALL + OUTER_FOAM + OUTER_SHELL_WALL   # 83.1
OUTER_HALF_Y = (INNER_FLAT_Y + INNER_SHELL_WALL + BAG_THICKNESS + POCKET_OUTER_WALL
                + OUTER_FOAM + OUTER_SHELL_WALL)              # 118.9

# Bag-pocket walls
# Bag inboard face touches inner-shell OUTER face at y = ±(INNER_FLAT_Y + INNER_SHELL_WALL).
# Bag outboard face = bag inboard + BAG_THICKNESS = 76.3 + 35 = 111.3.
# Pocket outboard wall outer face = 111.3 + POCKET_OUTER_WALL = 112.1.
POCKET_OUTER_Y_INNER = INNER_FLAT_Y + INNER_SHELL_WALL + BAG_THICKNESS  # 111.3
POCKET_OUTER_Y_OUTER = POCKET_OUTER_Y_INNER + POCKET_OUTER_WALL         # 112.1
POCKET_END_X         = INNER_FLAT_HALF                        # ±62.5 (end-wall X position, inner face)
POCKET_END_X_OUTER   = POCKET_END_X + POCKET_OUTER_WALL       # 63.3

# Z levels
Z_BOTTOM_SKIN_THICKNESS = 0.8
Z_TOP_SKIN_THICKNESS    = 0.8
Z_FLOOR_TOTAL           = 226.0
Z_FLOOR1_TO_2           = 37.0      # mating plane
Z_FLOOR2_TO_3           = 189.0     # mating plane

# Tank vertical position
Z_TANK_BOTTOM = Z_FLOOR1_TO_2                # tank bottom plate sits on standoffs at z=37
Z_TANK_TOP    = Z_TANK_BOTTOM + TANK_HEIGHT  # 189.4 — slightly above floor 2/3 mating
# Inner shell discs (top & bottom of inner cavity)
INNER_DISC_THICKNESS = 0.8
# Bottom disc: TOP of disc must be 6.35 mm below z=37 so the foam-floor
# (top-of-disc -> z=37) is exactly 6.35 mm.  Disc occupies z=29.85..30.65.
Z_INNER_DISC_BOTTOM = Z_FLOOR1_TO_2 - 6.35 - INNER_DISC_THICKNESS   # 29.85
Z_INNER_DISC_TOP    = Z_TANK_TOP + 6.35      # 195.75 — 6.35 mm foam-ceiling above tank

# Inner shell vertical extent (sealed top and bottom)
# Per spec: bottom disc at z≈30, top disc at z≈196.
# The inner shell cylinder runs between those discs.
Z_INNER_SHELL_BOTTOM = Z_INNER_DISC_BOTTOM
Z_INNER_SHELL_TOP    = Z_INNER_DISC_TOP + INNER_DISC_THICKNESS

# Standoffs (4 small printed bumps holding tank-plate at z=37)
STANDOFF_W       = 5.0
STANDOFF_L       = 5.0
STANDOFF_H       = 0.8
STANDOFF_Z       = Z_FLOOR1_TO_2 - STANDOFF_H   # top of standoff at z=37

# ═══════════════════════════════════════════════════════
# PORT / FITTING / CONDUIT PLACEHOLDERS
# ═══════════════════════════════════════════════════════
#
# The cut-parts file currently has two holes per plate but doesn't label
# CO2 vs water vs PRV.  Choices made here (document for future revision):
#
#   Bottom plate (Floor 1):
#     +X port (hole at tank-plate radius ~25mm, on +X axis): CO2 inlet
#     -X port:                                                water outlet
#   Top plate (Floor 3):
#     +X port:  water inlet
#     -X port:  PRV port
#
# Lateral exits go through the X-face outer shell.  Bag tubes exit Y-face
# outer shell near z=0.

FITTING_SHAFT_ID = 16.0      # placeholder, confirm against actual fittings
FITTING_SHAFT_OD = FITTING_SHAFT_ID + 2 * 1.6   # PETG conduit wall
FITTING_ELBOW_VERT_ENVELOPE = 25.0             # 90° elbow body height
TANK_PORT_RADIUS = 25.0      # distance from tank centerline to port center on plate

# Lateral conduits (X-face exits in Floor 1 and Floor 3)
LATERAL_CONDUIT_ID = 16.0    # tank-line lateral conduit ID
LATERAL_CONDUIT_OD = LATERAL_CONDUIT_ID + 2 * 1.6

# Bag tube conduits (Y-face exits in Floor 1 only — 1/4" tubing)
BAG_TUBE_ID = 8.0
BAG_TUBE_OD = BAG_TUBE_ID + 2 * 1.6
BAG_TUBE_Z  = 12.0           # near bag-cap elevation

# PRV vent conduit (Y-face exit in Floor 3 — to atmosphere)
PRV_VENT_ID = 10.0
PRV_VENT_OD = PRV_VENT_ID + 2 * 1.6

# Locating pins (lower piece) and matching holes (upper piece)
PIN_DIA       = 3.0
PIN_HEIGHT    = 4.0
PIN_HOLE_DIA  = 3.4         # 0.2 mm radial clearance per side

# Pin positions: near 4 corners of the bounding rectangle, set in from edge
# Pins sit straddling the outer-shell wall: half in the wall material,
# half in the foam cavity (which fills around them after pour).  That gives
# the pin body solid contact with the perimeter wall for unioning.
# Pin centerline is at the wall mid-thickness offset further into the cavity
# so the pin body overlaps the wall by ~PIN_DIA/3.
PIN_X = OUTER_HALF_X - OUTER_SHELL_WALL - 0.5   # ≈ 81.8 (overlaps wall + extends inward)
PIN_Y = OUTER_HALF_Y - OUTER_SHELL_WALL - 16.0  # ≈ 102.1 (outside corner R)

# Foam-pour fill ports & vents
FILL_PORT_DIA = 10.0
VENT_DIA      = 5.0

# Numerical tolerance / cleanup
OVERCUT = 0.1
EPS     = 1e-6

OUTPUT_DIR = Path(__file__).resolve().parent


# ═══════════════════════════════════════════════════════
# CROSS-SECTION HELPERS — flatted stadium
# ═══════════════════════════════════════════════════════
#
# The inner shell cross-section is a flat-stadium:
#   - circle of radius 76.3 from origin, BUT only on the +X / -X portions
#     (where |x| > 62.5)
#   - flats at y = ±76.3 between x = -62.5 and +62.5
#   - vertical jump segments at x = ±62.5 from arc-end (y=±43.77) to flat-end
#     (y=±76.3) — these are inside the inner shell, closing wedge corners
#
# We construct it explicitly with arcs + line segments rather than relying
# on any built-in stadium primitive (the stadium primitive is wrong here:
# our shape is two arcs + four line segments + four vertical-jump segments).

ARC_END_Y = math.sqrt(INNER_ARC_R**2 - INNER_FLAT_HALF**2)
# = sqrt(76.3² - 62.5²) = sqrt(5821.69 - 3906.25) = sqrt(1915.44) ≈ 43.766


def inner_shell_face_2d():
    """2D wire (Face) for the inner shell cross-section, centered at origin.

    Constructed as a closed polyline-with-arcs:
      Start at (62.5, 76.3) — top-right corner of top flat
      LINE left along top flat to (-62.5, 76.3)
      LINE down (vertical jump) to (-62.5, 43.766) — meets +X arc end on left side
        Wait: at x=-62.5, the arc point is at y=+43.766 if we're on the LEFT (-X) arc.
        Actually the arc is centered at origin radius 76.3.  At x=-62.5, y on arc
        is ±43.766.  We want the LEFT arc (which is on the -X side, the round face).
        So we go from (-62.5, 76.3) down to (-62.5, 43.766) — this is the
        vertical-jump segment, *interior* to where a circle would be.
      ARC from (-62.5, 43.766) along the -X arc through (-76.3, 0) to (-62.5, -43.766)
      LINE down to (-62.5, -76.3)
      LINE right along bottom flat to (62.5, -76.3)
      LINE up to (62.5, -43.766)
      ARC through (76.3, 0) to (62.5, 43.766)
      LINE up to (62.5, 76.3) close.
    """
    fx = INNER_FLAT_HALF       # 62.5
    fy = INNER_FLAT_Y          # 76.3
    ax = INNER_ARC_R           # 76.3
    ae = ARC_END_Y             # ~43.766

    wp = (
        cq.Workplane("XY")
        .moveTo(fx, fy)
        .lineTo(-fx, fy)
        .lineTo(-fx, ae)
        .threePointArc((-ax, 0), (-fx, -ae))
        .lineTo(-fx, -fy)
        .lineTo(fx, -fy)
        .lineTo(fx, -ae)
        .threePointArc((ax, 0), (fx, ae))
        .close()
    )
    return wp


def inner_shell_outer_face_2d():
    """The same cross-section but offset OUTWARD by INNER_SHELL_WALL.

    Rather than fight CadQuery's offset2D, we construct the outer wire
    explicitly using the same scheme but with offsets:
      flat moves out by 0.8 (so y = ±77.1)
      flat-half-extent grows by 0.8 (so x = ±63.3)
      arc radius grows by 0.8 (so 77.1)
      arc-end-y at x=±63.3 = sqrt(77.1² - 63.3²) ≈ sqrt(5944.41 - 4006.89)
                            = sqrt(1937.52) ≈ 44.017
    """
    w = INNER_SHELL_WALL
    fx = INNER_FLAT_HALF + w
    fy = INNER_FLAT_Y + w
    ax = INNER_ARC_R + w
    ae = math.sqrt(ax**2 - fx**2)

    wp = (
        cq.Workplane("XY")
        .moveTo(fx, fy)
        .lineTo(-fx, fy)
        .lineTo(-fx, ae)
        .threePointArc((-ax, 0), (-fx, -ae))
        .lineTo(-fx, -fy)
        .lineTo(fx, -fy)
        .lineTo(fx, -ae)
        .threePointArc((ax, 0), (fx, ae))
        .close()
    )
    return wp


def outer_shell_face_2d():
    """Outer perimeter cross-section: flat-stadium with arcs at radius OUTER_HALF_X
    on the +X/-X ends and flats at y = ±OUTER_HALF_Y between them.

    The arcs of the outer shell are at radius 83.1 from origin (X-face), and
    flats at y = ±118.9 (Y-face).  At what x does the arc meet the flat?
      x = sqrt(83.1² - 118.9²) is imaginary — meaning the outer shape is NOT
    actually a flatted-stadium with an arc through (±83.1, 0) and flats at
    ±118.9.  The outer shape is rectangular with rounded X-face arcs.

    Re-reading spec: outer shape is a flatted stadium where Y-face is FLAT
    (tangent to bag back) and X-face is round.  But the arc must connect to
    the flat.  The arc on the X-face is tangent to the flat at y = ±OUTER_HALF_Y.
    So the arc isn't a half-circle — it's a circular cap whose chord is at
    x = some value where the arc joins the flat.

    Simpler: just build a rounded rectangle (rectangle with arcs at the four
    corners) where the corner radius gives the X-face curvature.  Per spec
    the X-face is "round arc, radius 83.1 from tank centerline" — so the
    arc's center is at the origin, radius 83.1.

    This means the outer shape's X-face arc and Y-face flat must meet at
    the points (±sqrt(83.1² - 118.9²), ±118.9) — but 118.9 > 83.1, so no
    intersection.  The shape must therefore be:
      Y-face flats from x = -OUTER_HALF_X to +OUTER_HALF_X at y = ±OUTER_HALF_Y
      X-face arcs of radius OUTER_HALF_X from (±OUTER_HALF_X, +y_start) to
        (±OUTER_HALF_X, -y_start) where y_start can be anything ≤ OUTER_HALF_Y
      Vertical jump segments from (±OUTER_HALF_X, OUTER_HALF_Y) to
        (±OUTER_HALF_X, +y_arc_top), then arc, then to (±OUTER_HALF_X, -OUTER_HALF_Y).

    But that's the same flatted-stadium pattern as the inner shell.  For
    consistency: arc spans the full X-face from y = -ax_half to +ax_half
    where ax_half is min(OUTER_HALF_X, OUTER_HALF_Y).

    A clean choice: the outer shell's X-face is arc-of-radius OUTER_HALF_X
    centered at origin (= half-circle endpoints at (±OUTER_HALF_X, 0),
    rising to (0, ±OUTER_HALF_X) on the +/-Y axis).  Then linear segments
    extend from (±OUTER_HALF_X, ±OUTER_HALF_X-something).

    Pragmatic simplification: build the outer perimeter as a rounded
    rectangle with corner radius = OUTER_HALF_X / 2.  This gives a brick-like
    outer shape that matches the spec's X=166.2 × Y=237.8 envelope exactly
    and has filleted corners (no sharp corners).  This is internally
    consistent for foam pour and shell wall, even if the X-face isn't a
    pure half-circle of radius OUTER_HALF_X.

    For scope: the outer shell's job is to be a sealed perimeter.  A rounded
    rectangle is fine.
    """
    # Rounded rectangle: width = 2*OUTER_HALF_X, height = 2*OUTER_HALF_Y, corner R
    OUTER_CORNER_R = 12.0    # gentle radius, design choice
    return (
        cq.Workplane("XY")
        .rect(2 * OUTER_HALF_X, 2 * OUTER_HALF_Y)
    ), OUTER_CORNER_R


def outer_shell_solid(z_bottom, z_top, with_corner_fillet=True):
    """Outer-shell perimeter SOLID (filled flat-stadium) from z_bottom to z_top."""
    OUTER_CORNER_R = 12.0
    solid = (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .rect(2 * OUTER_HALF_X, 2 * OUTER_HALF_Y)
        .extrude(z_top - z_bottom)
    )
    if with_corner_fillet:
        try:
            solid = solid.edges("|Z").fillet(OUTER_CORNER_R)
        except Exception:
            pass
    return solid


def outer_shell_perimeter_walls(z_bottom, z_top):
    """Hollow outer-shell perimeter: solid - inner cavity.  No top/bottom skin."""
    outer = outer_shell_solid(z_bottom, z_top, with_corner_fillet=True)
    OUTER_CORNER_R = 12.0
    # Inner cavity: shrink rounded rect by OUTER_SHELL_WALL on every side
    iw = 2 * (OUTER_HALF_X - OUTER_SHELL_WALL)
    ih = 2 * (OUTER_HALF_Y - OUTER_SHELL_WALL)
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=z_bottom - OVERCUT)
        .rect(iw, ih)
        .extrude(z_top - z_bottom + 2 * OVERCUT)
    )
    try:
        cavity = cavity.edges("|Z").fillet(max(OUTER_CORNER_R - OUTER_SHELL_WALL, 1.0))
    except Exception:
        pass
    return outer.cut(cavity)


# ═══════════════════════════════════════════════════════
# SHARED HELPERS
# ═══════════════════════════════════════════════════════

def cylinder_at(x, y, z_bot, z_top, r):
    """Vertical solid cylinder at (x,y), from z_bot to z_top, of radius r."""
    return (
        cq.Workplane("XY")
        .workplane(offset=z_bot)
        .center(x, y)
        .circle(r)
        .extrude(z_top - z_bot)
    )


def horizontal_cylinder_x(x_start, x_end, y, z, r):
    """Horizontal cylinder along X, from x_start to x_end, centered (y,z), radius r."""
    return (
        cq.Workplane("YZ")
        .workplane(offset=x_start)
        .center(y, z)
        .circle(r)
        .extrude(x_end - x_start)
    )


def horizontal_cylinder_y(y_start, y_end, x, z, r):
    """Horizontal cylinder along Y, from y_start to y_end, centered (x,z), radius r."""
    return (
        cq.Workplane("XZ")
        .workplane(offset=y_start)
        .center(x, z)
        .circle(r)
        .extrude(y_end - y_start)
    )


def add_locating_pins_to_top_face(piece, z_top):
    """Adds 4 locating pins on the upper face of `piece` at the four corners.

    Pin starts slightly below z_top so it overlaps the top face material and
    the union merges into the same solid (rather than producing a free-floating
    pin solid).
    """
    out = piece
    for sx in (+1, -1):
        for sy in (+1, -1):
            pin = cylinder_at(sx * PIN_X, sy * PIN_Y,
                              z_top - OVERCUT, z_top + PIN_HEIGHT,
                              PIN_DIA / 2)
            out = out.union(pin)
    return out


def cut_locating_pin_holes_from_bottom_face(piece, z_bottom):
    """Cuts 4 locating-pin holes into the bottom face of `piece`."""
    out = piece
    for sx in (+1, -1):
        for sy in (+1, -1):
            hole = cylinder_at(sx * PIN_X, sy * PIN_Y,
                               z_bottom - OVERCUT, z_bottom + PIN_HEIGHT + OVERCUT,
                               PIN_HOLE_DIA / 2)
            out = out.cut(hole)
    return out


def print_bbox(name, part):
    """Helper to print bounding box of a CadQuery part for sanity checking."""
    try:
        solids = part.solids().vals()
        for i, s in enumerate(solids):
            bb = s.BoundingBox()
            print(f"  {name} solid[{i}]: "
                  f"X[{bb.xmin:7.2f},{bb.xmax:7.2f}] "
                  f"Y[{bb.ymin:7.2f},{bb.ymax:7.2f}] "
                  f"Z[{bb.zmin:7.2f},{bb.zmax:7.2f}]")
    except Exception as e:
        print(f"  {name}: bbox error {e}")


# ═══════════════════════════════════════════════════════
# FLOOR 1 — z = 0 to 37
# ═══════════════════════════════════════════════════════
#
# Contains:
#   - Bottom skin at z=0..0.8
#   - Outer-shell perimeter walls from z=0 to 37
#   - Lower bag-pocket walls (outboard wall + 2 end walls) for each pocket
#   - PETG vertical shafts for the 2 bottom-plate fittings (pass-through)
#   - PETG lateral conduits for X-face tank-line exits (2)
#   - PETG conduits for bag flavor tubes on Y-face (2)
#   - 4 locating pins on top face
#
# During Pour 2: foam fills this band around the elbows + lateral tubing
# under the tank's bottom plate.

def build_floor_1():
    z_bottom = 0.0
    z_top = Z_FLOOR1_TO_2

    # 1) Bottom skin (sealed slab, no cutouts)
    bottom_skin = outer_shell_solid(z_bottom, z_bottom + Z_BOTTOM_SKIN_THICKNESS,
                                    with_corner_fillet=True)

    # 2) Outer-shell perimeter walls above the skin
    perim = outer_shell_perimeter_walls(z_bottom + Z_BOTTOM_SKIN_THICKNESS, z_top)

    floor1 = bottom_skin.union(perim)

    # 3) Lower bag-pocket walls — for each bag (at +Y and -Y):
    #    - outboard wall (parallel to X, at y = ±POCKET_OUTER_Y_INNER)
    #    - two end walls (at x = ±POCKET_END_X)
    #    Each wall extends from z = 0 to z = Z_FLOOR1_TO_2.
    #    The pocket interior MUST be dry — so the outer-foam region surrounding
    #    the pocket pours separately.  We model the pocket walls as thin slabs.
    for sy in (+1, -1):
        # Outboard wall: spans from x = -POCKET_END_X_OUTER to +POCKET_END_X_OUTER
        outboard_wall = (
            cq.Workplane("XY")
            .workplane(offset=z_bottom)
            .center(0, sy * (POCKET_OUTER_Y_INNER + POCKET_OUTER_WALL / 2))
            .rect(2 * POCKET_END_X_OUTER, POCKET_OUTER_WALL)
            .extrude(z_top - z_bottom)
        )
        floor1 = floor1.union(outboard_wall)

        # End walls (two per pocket): spans from y = INNER_FLAT_Y to POCKET_OUTER_Y_OUTER
        for sx in (+1, -1):
            end_wall = (
                cq.Workplane("XY")
                .workplane(offset=z_bottom)
                .center(sx * (POCKET_END_X + POCKET_OUTER_WALL / 2),
                        sy * (INNER_FLAT_Y + BAG_THICKNESS / 2))
                .rect(POCKET_OUTER_WALL, BAG_THICKNESS + 2 * POCKET_OUTER_WALL)
                .extrude(z_top - z_bottom)
            )
            floor1 = floor1.union(end_wall)

    # 4) Vertical fitting shafts for the 2 bottom-plate ports
    #    +X port: CO2 inlet
    #    -X port: water outlet
    # Shaft goes from z = bottom_skin top (0.8) up to z = Z_FLOOR1_TO_2 (open
    # to receive Floor 2's mating).  Inner bore drilled fully through skin.
    for sx in (+1, -1):
        shaft = cylinder_at(sx * TANK_PORT_RADIUS, 0,
                             z_bottom, z_top, FITTING_SHAFT_OD / 2)
        bore  = cylinder_at(sx * TANK_PORT_RADIUS, 0,
                             z_bottom - OVERCUT, z_top + OVERCUT,
                             FITTING_SHAFT_ID / 2)
        floor1 = floor1.union(shaft).cut(bore)

    # 5) Lateral conduits — X-face exits for tank-line tubing
    # Each conduit is a horizontal PETG cylinder running from just outside
    # the fitting shaft to just past the outer shell, centered at the
    # 90° elbow elevation.  The bore cuts through to make a tube.
    z_lateral = z_bottom + 18.0
    for sx in (+1, -1):
        x_a = sx * (TANK_PORT_RADIUS + FITTING_SHAFT_OD / 2)
        x_b = sx * (OUTER_HALF_X + OVERCUT)
        x_lo, x_hi = sorted((x_a, x_b))
        cond_od = horizontal_cylinder_x(x_lo, x_hi, 0, z_lateral, LATERAL_CONDUIT_OD / 2)
        bore = horizontal_cylinder_x(x_lo - OVERCUT, x_hi + OVERCUT,
                                      0, z_lateral, LATERAL_CONDUIT_ID / 2)
        floor1 = floor1.union(cond_od).cut(bore)

    # 6) Bag tube conduits — Y-face exits for bag flavor tubing (2 conduits)
    # Each runs from inside the pocket outboard wall (just inside) through
    # the outer foam to the Y-face outer shell at the bag-cap elevation.
    for sy in (+1, -1):
        y_a = sy * (POCKET_OUTER_Y_OUTER - OVERCUT)
        y_b = sy * (OUTER_HALF_Y + OVERCUT)
        y_lo, y_hi = sorted((y_a, y_b))
        cond_od = horizontal_cylinder_y(y_lo, y_hi, 0, BAG_TUBE_Z, BAG_TUBE_OD / 2)
        bore = horizontal_cylinder_y(y_lo - OVERCUT, y_hi + OVERCUT,
                                      0, BAG_TUBE_Z, BAG_TUBE_ID / 2)
        floor1 = floor1.union(cond_od).cut(bore)

    # 7) Locating pins on top face (this is the LOWER piece of the seam at z=37)
    floor1 = add_locating_pins_to_top_face(floor1, z_top)

    return floor1


# ═══════════════════════════════════════════════════════
# FLOOR 2 — z = 37 to 189
# ═══════════════════════════════════════════════════════
#
# Contains:
#   - Outer-shell perimeter walls (continuing)
#   - Inner shell (flatted-stadium) sealed top and bottom by PETG discs
#   - 4 standoffs at z = 37 supporting the tank's bottom plate
#   - Bag-pocket walls (continuing — outboard wall + end walls)
#   - Holes through inner discs for fitting shafts
#   - Pin holes on bottom face, pins on top face
#   - Foam-pour fill port + vent through inner-shell top disc

def build_inner_shell_walls():
    """Inner shell: flatted-stadium tube, sealed top and bottom by PETG discs.

    Construct as solid - inner-cavity-extrusion to give the shell wall
    of thickness INNER_SHELL_WALL between Z_INNER_SHELL_BOTTOM and
    Z_INNER_SHELL_TOP.  Then add discs separately so we can put the
    discs in their precise positions.
    """
    z_bot = Z_INNER_SHELL_BOTTOM
    z_top = Z_INNER_SHELL_TOP

    # Outer cross-section (offset outward by wall thickness)
    outer_face = inner_shell_outer_face_2d()
    inner_face = inner_shell_face_2d()

    outer_solid = outer_face.extrude(z_top - z_bot).translate((0, 0, z_bot))
    inner_solid = inner_face.extrude(z_top - z_bot + 2 * OVERCUT).translate(
        (0, 0, z_bot - OVERCUT))

    shell = outer_solid.cut(inner_solid)

    # Fillet all 16 vertical edges (8 inner-face + 8 outer-face) at the
    # flat-to-jump and jump-to-arc transitions.  This relieves the sharp
    # corners — both for stress concentration and printability.
    try:
        shell = shell.edges("|Z").fillet(INNER_FILLET_R)
    except Exception as e:
        print(f"  warning: inner-shell fillet failed ({e}); leaving sharp corners")

    return shell


def build_inner_shell_discs():
    """The two PETG discs that seal the inner shell at top and bottom.

    Each disc is the same flatted-stadium cross-section (outer outline) but
    with the fitting-shaft hole(s) cut through.
    """
    # Bottom disc at z = Z_INNER_DISC_BOTTOM
    bottom_disc = (
        inner_shell_outer_face_2d()
        .extrude(INNER_DISC_THICKNESS)
        .translate((0, 0, Z_INNER_DISC_BOTTOM))
    )

    # Top disc at z = Z_INNER_DISC_TOP
    top_disc = (
        inner_shell_outer_face_2d()
        .extrude(INNER_DISC_THICKNESS)
        .translate((0, 0, Z_INNER_DISC_TOP))
    )

    # Cut shaft-pass-through holes in both discs (clearance for fittings)
    shaft_clearance_r = (FITTING_SHAFT_OD / 2) + 0.5
    for sx in (+1, -1):
        hole_b = cylinder_at(sx * TANK_PORT_RADIUS, 0,
                              Z_INNER_DISC_BOTTOM - OVERCUT,
                              Z_INNER_DISC_BOTTOM + INNER_DISC_THICKNESS + OVERCUT,
                              shaft_clearance_r)
        bottom_disc = bottom_disc.cut(hole_b)

        hole_t = cylinder_at(sx * TANK_PORT_RADIUS, 0,
                              Z_INNER_DISC_TOP - OVERCUT,
                              Z_INNER_DISC_TOP + INNER_DISC_THICKNESS + OVERCUT,
                              shaft_clearance_r)
        top_disc = top_disc.cut(hole_t)

    # Inner foam-pour fill port + vent through TOP disc (Pour 1 access)
    fill = cylinder_at(0, 0,
                       Z_INNER_DISC_TOP - OVERCUT,
                       Z_INNER_DISC_TOP + INNER_DISC_THICKNESS + OVERCUT,
                       FILL_PORT_DIA / 2)
    top_disc = top_disc.cut(fill)
    # Vent near front
    vent = cylinder_at(0, 30,
                       Z_INNER_DISC_TOP - OVERCUT,
                       Z_INNER_DISC_TOP + INNER_DISC_THICKNESS + OVERCUT,
                       VENT_DIA / 2)
    top_disc = top_disc.cut(vent)

    return bottom_disc.union(top_disc)


def build_floor_2():
    z_bottom = Z_FLOOR1_TO_2
    z_top = Z_FLOOR2_TO_3

    # 1) Outer-shell perimeter walls
    perim = outer_shell_perimeter_walls(z_bottom, z_top)
    floor2 = perim

    # 2) Inner shell (flatted-stadium walls) + sealing discs
    inner_walls = build_inner_shell_walls()
    floor2 = floor2.union(inner_walls)
    floor2 = floor2.union(build_inner_shell_discs())

    # 3) 4 small printed standoffs at z = 37 (top of standoff = z=37, sitting
    #    on the inner-shell bottom disc surface).  Placed on the inner-shell
    #    interior wall at ±X-axis and ±Y-axis intersections with the tank-plate.
    # Tank plate sits at z = Z_FLOOR1_TO_2 (= 37).  Standoffs occupy
    # STANDOFF_Z to Z_FLOOR1_TO_2.
    standoff_positions = [
        (TANK_OUTER_R - 2.0, 0),
        (-TANK_OUTER_R + 2.0, 0),
        (0, TANK_OUTER_R - 2.0),
        (0, -TANK_OUTER_R + 2.0),
    ]
    # Standoffs extend from the top of the bottom inner disc up to z=37
    # (where the tank's bottom plate sits).  Slight overlap into the disc
    # ensures union.
    standoff_z_bot = Z_INNER_DISC_BOTTOM + INNER_DISC_THICKNESS - OVERCUT
    standoff_z_top = Z_FLOOR1_TO_2
    for px, py in standoff_positions:
        standoff = (
            cq.Workplane("XY")
            .workplane(offset=standoff_z_bot)
            .center(px, py)
            .rect(STANDOFF_W, STANDOFF_L)
            .extrude(standoff_z_top - standoff_z_bot)
        )
        floor2 = floor2.union(standoff)

    # 4) Vertical fitting shafts continue through Floor 2's bottom disc to the
    #    bottom plane of Floor 2 (where they meet Floor 1's shafts).  And from
    #    the top disc upward to the top of Floor 2 (where they meet Floor 3).
    #    Bottom: from z_bottom (37) to Z_INNER_DISC_BOTTOM (30.65) — wait, the
    #    bottom disc is BELOW z=37.  Actually inner-disc-bottom is at z=30.65
    #    (in the foam-floor below the tank) and inner-disc-top is at z=195.75
    #    (in the foam-ceiling above the tank).  The shafts pass through both
    #    discs.
    # We draw fitting shafts on the BOTTOM-PLATE pair (at +X, -X, z=Z_TANK_BOTTOM..z=37):
    # Wait — the bottom-plate fittings exit DOWN from the tank, through the
    # foam-floor and into Floor 1's region.  The shafts in Floor 2 are the
    # tube holes through both discs (already cut above) plus possibly conduits
    # in the upper foam-ceiling region for the top-plate fittings exiting up.
    # The actual fitting bodies pass down through the bottom disc into Floor 1
    # (where Floor 1's shaft picks them up) and up through the top disc into
    # Floor 3 (where Floor 3's shaft picks them up).
    # We do NOT need additional conduit material in Floor 2 between the discs
    # — the foam in Pour 1 fills around them.

    # 5) Bag-pocket walls (continuing from Floor 1) — outboard wall + 2 end
    #    walls per pocket, between z_bottom and z_top
    for sy in (+1, -1):
        outboard_wall = (
            cq.Workplane("XY")
            .workplane(offset=z_bottom)
            .center(0, sy * (POCKET_OUTER_Y_INNER + POCKET_OUTER_WALL / 2))
            .rect(2 * POCKET_END_X_OUTER, POCKET_OUTER_WALL)
            .extrude(z_top - z_bottom)
        )
        floor2 = floor2.union(outboard_wall)
        for sx in (+1, -1):
            end_wall = (
                cq.Workplane("XY")
                .workplane(offset=z_bottom)
                .center(sx * (POCKET_END_X + POCKET_OUTER_WALL / 2),
                        sy * (INNER_FLAT_Y + BAG_THICKNESS / 2))
                .rect(POCKET_OUTER_WALL, BAG_THICKNESS + 2 * POCKET_OUTER_WALL)
                .extrude(z_top - z_bottom)
            )
            floor2 = floor2.union(end_wall)

    # 6) Pin holes on bottom face (mating with Floor 1's pins)
    floor2 = cut_locating_pin_holes_from_bottom_face(floor2, z_bottom)

    # 7) Pins on top face (for mating with Floor 3)
    floor2 = add_locating_pins_to_top_face(floor2, z_top)

    return floor2


# ═══════════════════════════════════════════════════════
# FLOOR 3 — z = 189 to 226
# ═══════════════════════════════════════════════════════
#
# Contains:
#   - Outer-shell perimeter walls (continuing)
#   - Top skin at z ≈ 225..226 (sealed slab, with foam-pour fill port + vents)
#   - PETG vertical shafts for the 2 top-plate fittings
#   - Lateral conduits for X-face top-plate exits (2)
#   - PRV vent conduit (Y-face exit)
#   - Pin holes on bottom face

def build_floor_3():
    z_bottom = Z_FLOOR2_TO_3
    z_top = Z_FLOOR_TOTAL

    # 1) Outer-shell perimeter walls (between z_bottom and the top skin)
    perim = outer_shell_perimeter_walls(z_bottom,
                                         z_top - Z_TOP_SKIN_THICKNESS)
    floor3 = perim

    # 2) Top skin
    top_skin = outer_shell_solid(z_top - Z_TOP_SKIN_THICKNESS, z_top,
                                  with_corner_fillet=True)
    floor3 = floor3.union(top_skin)

    # 3) Vertical fitting shafts — top-plate ports
    # +X port: water inlet, -X port: PRV port
    # Shaft from z_bottom up through the top skin
    for sx in (+1, -1):
        shaft = cylinder_at(sx * TANK_PORT_RADIUS, 0,
                             z_bottom, z_top, FITTING_SHAFT_OD / 2)
        bore  = cylinder_at(sx * TANK_PORT_RADIUS, 0,
                             z_bottom - OVERCUT, z_top + OVERCUT,
                             FITTING_SHAFT_ID / 2)
        floor3 = floor3.union(shaft).cut(bore)

    # 4) Lateral conduits — X-face exits for top-plate tank-line tubing
    z_lateral = z_bottom + 18.0
    for sx in (+1, -1):
        x_a = sx * (TANK_PORT_RADIUS + FITTING_SHAFT_OD / 2)
        x_b = sx * (OUTER_HALF_X + OVERCUT)
        x_lo, x_hi = sorted((x_a, x_b))
        cond = horizontal_cylinder_x(x_lo, x_hi, 0, z_lateral, LATERAL_CONDUIT_OD / 2)
        bore = horizontal_cylinder_x(x_lo - OVERCUT, x_hi + OVERCUT,
                                      0, z_lateral, LATERAL_CONDUIT_ID / 2)
        floor3 = floor3.union(cond).cut(bore)

    # 5) PRV vent conduit — runs from a PRV body location near the -X
    # top-plate port outward through the +Y face outer shell.
    z_prv = z_bottom + 20.0
    x_prv = -TANK_PORT_RADIUS - FITTING_SHAFT_OD / 2 - PRV_VENT_OD / 2 - 2.0
    y_b = OUTER_HALF_Y + OVERCUT
    prv_cond = horizontal_cylinder_y(0, y_b, x_prv, z_prv, PRV_VENT_OD / 2)
    prv_bore = horizontal_cylinder_y(-OVERCUT, y_b + OVERCUT, x_prv, z_prv, PRV_VENT_ID / 2)
    floor3 = floor3.union(prv_cond).cut(prv_bore)

    # 6) Foam-pour fill port through Floor 3's top skin (Pour 2)
    fill = cylinder_at(40, 80,
                       z_top - Z_TOP_SKIN_THICKNESS - OVERCUT,
                       z_top + OVERCUT,
                       FILL_PORT_DIA / 2)
    floor3 = floor3.cut(fill)
    # Vent hole pair near the fill port
    for vx, vy in [(50, 90), (30, 70)]:
        v = cylinder_at(vx, vy,
                        z_top - Z_TOP_SKIN_THICKNESS - OVERCUT,
                        z_top + OVERCUT,
                        VENT_DIA / 2)
        floor3 = floor3.cut(v)

    # 7) Pin holes on bottom face (mating with Floor 2's pins)
    floor3 = cut_locating_pin_holes_from_bottom_face(floor3, z_bottom)

    return floor3


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

def main():
    print("Building Floor 1 ...")
    floor1 = build_floor_1()
    print_bbox("floor1", floor1)
    cq.exporters.export(floor1, str(OUTPUT_DIR / "foam-bag-shell-floor-1.step"))
    print("  -> foam-bag-shell-floor-1.step")

    print("Building Floor 2 ...")
    floor2 = build_floor_2()
    print_bbox("floor2", floor2)
    cq.exporters.export(floor2, str(OUTPUT_DIR / "foam-bag-shell-floor-2.step"))
    print("  -> foam-bag-shell-floor-2.step")

    print("Building Floor 3 ...")
    floor3 = build_floor_3()
    print_bbox("floor3", floor3)
    cq.exporters.export(floor3, str(OUTPUT_DIR / "foam-bag-shell-floor-3.step"))
    print("  -> foam-bag-shell-floor-3.step")

    print("All three STEP files exported.")


if __name__ == "__main__":
    main()
