"""
Flavor-foam shell: rigid 3D-printed PETG shell containing the carbonated
water tank (wrapped in its refrigerant coil) plus two integrated 1 L
rigid flavor-syrup reservoirs on the +Y flat face of the tank.

Layout (cross-section, from -Y to +Y):
    outer shell wall  |  25.4 mm foam  |  tank racetrack  |  6.35 mm foam  |
    container inner wall  |  92 mm syrup cavity  |  container outer wall  |
    6.35 mm foam  |  outer shell wall

The shell is a single monolithic print with an open top.  The user
pre-wraps the carbonator tank with the refrigerant coil, drops it into
the shell from above, then pours closed-cell polyurethane foam around it
through the same opening.  The two syrup reservoirs sit above the flat
+Y face of the tank; they have:

  - A 5 mm sump at the (X=0, Y=+156.50) corner of each container,
    with the floor sloping toward the sump from all three other sides
    at ~30 deg.
  - A JG-bulkhead through-hole (11 mm) from each sump out the +Y face,
    passing through the container outer wall, the 6.35 mm foam gap, and
    the shell outer wall.  Local bosses thicken the walls around the
    hole for a 1/4" NPT tap to bite into.
  - A 45 deg tent ceiling running along X, ridge at Y=+110.5.
  - A vent standpipe rising from the ridge peak, terminating ~10 mm
    above the shell's open top.

Coordinate system:
  X: along the racetrack's long axis
  Y: along the racetrack's short axis (flat faces at +/-Y)
  Z: along the tank's long axis (print build direction, +Z is up)
"""

import math
from pathlib import Path
import cadquery as cq


# ═══════════════════════════════════════════════════════
# WALLS, CLEARANCES, FOAM LAYERS
# ═══════════════════════════════════════════════════════

WALL            = 1.0     # printed wall thickness
FLOOR           = 1.0     # printed floor thickness
OVERLAP         = 0.1     # boolean overlap for reliable unions / cuts

FOAM_INCH       = 25.4    # 1-inch foam layer (sides, floor, ceiling of tank)
FOAM_QUARTER    = 6.35    # 1/4-inch foam layer (gap between container & shell, etc.)


# ═══════════════════════════════════════════════════════
# TANK RACETRACK (reserved space; not modeled here)
# ═══════════════════════════════════════════════════════

TANK_SEMI_R     = 50.8    # racetrack semicircle radius
TANK_FLAT_LEN   = 40.64   # flat length between semicircles
TANK_Y_FLAT     = TANK_SEMI_R            # +/- 50.8 on Y for tank flat faces
COIL_OD         = FOAM_QUARTER           # 6.35 mm copper coil wraps tank
# Tank+coil on +Y flat side ends at: TANK_Y_FLAT + COIL_OD = 57.15


# ═══════════════════════════════════════════════════════
# CONTAINER CAVITY Y LAYERS  (all absolute Y coordinates)
# ═══════════════════════════════════════════════════════

CONTAINER_INNER_WALL_Y0 = 63.50          # foam-facing face of inner wall
CONTAINER_INNER_WALL_Y1 = 64.50          # syrup-facing face of inner wall
CONTAINER_OUTER_WALL_Y0 = 156.50         # syrup-facing face of outer wall
CONTAINER_OUTER_WALL_Y1 = 157.50         # foam-facing face of outer wall
CONTAINER_CAVITY_DEPTH  = CONTAINER_OUTER_WALL_Y0 - CONTAINER_INNER_WALL_Y1  # 92.0

SHELL_INNER_Y_MINUS     = -77.2          # inner face of shell -Y wall
SHELL_OUTER_Y_MINUS     = -78.2          # outer face of shell -Y wall
SHELL_INNER_Y_PLUS      = 163.85         # inner face of shell +Y wall
SHELL_OUTER_Y_PLUS      = 164.85         # outer face of shell +Y wall


# ═══════════════════════════════════════════════════════
# CONTAINER X FOOTPRINT  (two containers share a divider at X=0)
# ═══════════════════════════════════════════════════════

CONTAINER_X_HALF        = 71.12          # each container extends 71.12 in X
# Container A: X = -CONTAINER_X_HALF .. 0
# Container B: X = 0 .. +CONTAINER_X_HALF
DIVIDER_HALF_THICKNESS  = WALL / 2       # shared wall at X=0

# Shell outer X extent: container X-span plus 1" foam plus 1 mm wall on each end
SHELL_INNER_X_PLUS      =  CONTAINER_X_HALF + FOAM_INCH          # 96.52
SHELL_OUTER_X_PLUS      =  SHELL_INNER_X_PLUS + WALL             # 97.52
SHELL_INNER_X_MINUS     = -SHELL_INNER_X_PLUS
SHELL_OUTER_X_MINUS     = -SHELL_OUTER_X_PLUS


# ═══════════════════════════════════════════════════════
# Z LEVELS
# ═══════════════════════════════════════════════════════

Z_FLOOR_BOTTOM   = 0.0                   # outer floor of shell
Z_FLOOR_TOP      = FLOOR                 # 1.0 - top of shell floor
Z_TANK_BOTTOM    = Z_FLOOR_TOP + FOAM_INCH        # 26.4
TANK_HEIGHT      = 152.4                 # 6" tank
Z_TANK_TOP       = Z_TANK_BOTTOM + TANK_HEIGHT    # 178.8
Z_CEILING_FOAM   = Z_TANK_TOP + FOAM_INCH         # 204.2
Z_SHELL_TOP      = 205.0                 # shell outer-wall top

# Container interior Z span
Z_CONTAINER_FLOOR   = Z_TANK_BOTTOM      # 26.4 — sump floor depth
Z_CONTAINER_SLOPE_TOP = Z_CONTAINER_FLOOR + 5.0   # 31.4 — nominal floor height outside sump
Z_CEILING_START  = 158.0                 # tent ceiling starts (edges of Y span)
TENT_RISE        = (CONTAINER_CAVITY_DEPTH / 2)   # 46 mm — 45 deg tent
Z_CEILING_PEAK   = Z_CEILING_START + TENT_RISE    # 204.0


# ═══════════════════════════════════════════════════════
# SUMP GEOMETRY
# ═══════════════════════════════════════════════════════

SUMP_X_EXTENT       = 20.0               # 20 mm footprint in X (inward from divider)
SUMP_Y_EXTENT       = 20.0               # 20 mm footprint in Y (inward from outer wall)
SUMP_DEPTH          = 5.0                # sump floor 5 mm below main floor level

# For container A (X < 0), sump occupies X = [-SUMP_X_EXTENT, 0],
#   Y = [CONTAINER_OUTER_WALL_Y0 - SUMP_Y_EXTENT, CONTAINER_OUTER_WALL_Y0]
# For container B (X > 0), sump occupies X = [0, +SUMP_X_EXTENT],
#   Y = [CONTAINER_OUTER_WALL_Y0 - SUMP_Y_EXTENT, CONTAINER_OUTER_WALL_Y0]


# ═══════════════════════════════════════════════════════
# JG BULKHEAD BOSS
# ═══════════════════════════════════════════════════════

BOSS_HOLE_DIA       = 11.0               # 11 mm through-hole for 1/4" NPT tap
BOSS_Z              = Z_CONTAINER_FLOOR + SUMP_DEPTH / 2   # 28.9 - center of sump depth
BOSS_X_A            = -15.0              # container A boss X
BOSS_X_B            = +15.0              # container B boss X
BOSS_LOCAL_WALL     = 3.0                # local wall thickness around hole
BOSS_LOCAL_HALF     = 7.0                # half-size of local thickening box (X/Z)


# ═══════════════════════════════════════════════════════
# VENT STANDPIPE
# ═══════════════════════════════════════════════════════

STANDPIPE_OD        = 6.0                # outer diameter
STANDPIPE_ID        = 4.0                # inner diameter
STANDPIPE_TOP_Z     = Z_SHELL_TOP + 10.0 # terminates 10 mm above shell top
STANDPIPE_Y         = (CONTAINER_INNER_WALL_Y1 + CONTAINER_OUTER_WALL_Y0) / 2  # 110.5
STANDPIPE_X_A       = -CONTAINER_X_HALF / 2    # -35.56
STANDPIPE_X_B       =  CONTAINER_X_HALF / 2    # +35.56


# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════

def box(x0, x1, y0, y1, z0, z1):
    """Axis-aligned box from min/max coordinates."""
    dx, dy, dz = x1 - x0, y1 - y0, z1 - z0
    return (
        cq.Workplane("XY")
        .transformed(offset=(x0 + dx / 2, y0 + dy / 2, z0))
        .box(dx, dy, dz, centered=(True, True, False))
    )


# ═══════════════════════════════════════════════════════
# OUTER SHELL (open top)
# ═══════════════════════════════════════════════════════
#
# Floor + four walls.  The +Y wall is the one pierced by both JG
# bulkhead through-holes (plus local bosses for material).

def build_shell_floor():
    """Solid 1 mm floor covering the full outer XY footprint."""
    return box(SHELL_OUTER_X_MINUS, SHELL_OUTER_X_PLUS,
               SHELL_OUTER_Y_MINUS, SHELL_OUTER_Y_PLUS,
               Z_FLOOR_BOTTOM, Z_FLOOR_TOP)


def build_shell_walls():
    """Four vertical walls, floor-to-top, 1 mm thick, open at the top."""
    # -Y wall
    w_ymn = box(SHELL_OUTER_X_MINUS, SHELL_OUTER_X_PLUS,
                SHELL_OUTER_Y_MINUS, SHELL_INNER_Y_MINUS,
                Z_FLOOR_TOP, Z_SHELL_TOP)
    # +Y wall
    w_ypl = box(SHELL_OUTER_X_MINUS, SHELL_OUTER_X_PLUS,
                SHELL_INNER_Y_PLUS, SHELL_OUTER_Y_PLUS,
                Z_FLOOR_TOP, Z_SHELL_TOP)
    # -X wall (between the +/-Y walls)
    w_xmn = box(SHELL_OUTER_X_MINUS, SHELL_INNER_X_MINUS,
                SHELL_INNER_Y_MINUS, SHELL_INNER_Y_PLUS,
                Z_FLOOR_TOP, Z_SHELL_TOP)
    # +X wall
    w_xpl = box(SHELL_INNER_X_PLUS, SHELL_OUTER_X_PLUS,
                SHELL_INNER_Y_MINUS, SHELL_INNER_Y_PLUS,
                Z_FLOOR_TOP, Z_SHELL_TOP)
    walls = w_ymn.union(w_ypl, tol=0.05).union(w_xmn, tol=0.05).union(w_xpl, tol=0.05)
    return walls


# ═══════════════════════════════════════════════════════
# CONTAINER WALLS (inner, outer, end caps, shared divider)
# ═══════════════════════════════════════════════════════
#
# Each container is a rectangular box on the +Y flat face of the tank.
# The four walls are:
#   - Inner wall  (Y=63.50..64.50)   shared by both containers
#   - Outer wall  (Y=156.50..157.50) shared by both containers
#   - End cap     at X = +/- CONTAINER_X_HALF
#   - Divider     at X = 0 (shared between A and B, single 1 mm wall)
# Each wall runs from the shell floor up to the ceiling peak.

Z_CONTAINER_WALL_BOTTOM = Z_FLOOR_TOP    # walls continue down to the floor
Z_CONTAINER_WALL_TOP    = Z_CEILING_PEAK # walls extend up to ceiling peak

def build_container_walls():
    """Inner, outer, end-cap, and shared divider walls for both containers."""
    # Inner wall spans the full X of both containers
    inner = box(-CONTAINER_X_HALF, +CONTAINER_X_HALF,
                CONTAINER_INNER_WALL_Y0, CONTAINER_INNER_WALL_Y1,
                Z_CONTAINER_WALL_BOTTOM, Z_CONTAINER_WALL_TOP)
    # Outer wall spans the full X of both containers
    outer = box(-CONTAINER_X_HALF, +CONTAINER_X_HALF,
                CONTAINER_OUTER_WALL_Y0, CONTAINER_OUTER_WALL_Y1,
                Z_CONTAINER_WALL_BOTTOM, Z_CONTAINER_WALL_TOP)
    # -X end cap
    end_mn = box(-CONTAINER_X_HALF, -CONTAINER_X_HALF + WALL,
                 CONTAINER_INNER_WALL_Y0, CONTAINER_OUTER_WALL_Y1,
                 Z_CONTAINER_WALL_BOTTOM, Z_CONTAINER_WALL_TOP)
    # +X end cap
    end_pl = box(CONTAINER_X_HALF - WALL, CONTAINER_X_HALF,
                 CONTAINER_INNER_WALL_Y0, CONTAINER_OUTER_WALL_Y1,
                 Z_CONTAINER_WALL_BOTTOM, Z_CONTAINER_WALL_TOP)
    # Shared divider at X=0
    divider = box(-DIVIDER_HALF_THICKNESS, +DIVIDER_HALF_THICKNESS,
                  CONTAINER_INNER_WALL_Y1, CONTAINER_OUTER_WALL_Y0,
                  Z_CONTAINER_WALL_BOTTOM, Z_CONTAINER_WALL_TOP)
    walls = inner.union(outer, tol=0.05) \
                 .union(end_mn, tol=0.05) \
                 .union(end_pl, tol=0.05) \
                 .union(divider, tol=0.05)
    return walls


# ═══════════════════════════════════════════════════════
# CONTAINER FLOOR FILL & SLOPED FLOOR / SUMP
# ═══════════════════════════════════════════════════════
#
# Each container has a filled "floor deck" built up from Z_FLOOR_TOP to
# Z_CONTAINER_SLOPE_TOP (the nominal syrup-cavity floor level) with a
# 5 mm sump carved into the deck at the (X=0, Y=+outer) corner.
#
# On top of the deck, extra material forms the slope: syrup surface
# drains down toward the sump from three directions.  To keep the CAD
# simple we build the deck as a solid, then carve out:
#   (a) the sump pocket (a box, 20 x 20 x 5, in each container)
#   (b) three wedge cuts that drop the floor 0 mm at the sump face and
#       increase the drop as you move away, reaching SUMP_DEPTH at the
#       far edge... wait, that's the OPPOSITE direction.
#
# The design intent is: deck surface sits at Z = Z_CONTAINER_SLOPE_TOP
# far from the sump, and slopes DOWNWARD toward the sump.  The sump
# bottom is at Z_CONTAINER_FLOOR (5 mm below the main floor).  So the
# slope should drop in elevation as you approach the sump.
#
# Implementation: build a deck that is SOLID from Z_FLOOR_TOP to the
# sloped upper surface.  The simplest correct geometry is a union of
# three wedges:
#   - The "far" block far from the sump, top at Z_CONTAINER_SLOPE_TOP
#   - Sloped wedges connecting far block to sump rim on the three
#     approaches (the X=+/- end walls, the inner +Y wall, the divider)
#
# Since we need at least 30 deg slopes, the slope runs from the sump
# rim outward SUMP_DEPTH / tan(30 deg) ~= 8.66 mm.  We use 10 mm for
# some margin.  Everything beyond SLOPE_RUN from the sump is at the
# full deck level.

SLOPE_RUN = 10.0  # horizontal run of the sloping section (rise = SUMP_DEPTH)

def build_container_deck(x_sump_min, x_sump_max, sump_y_min, sump_y_max,
                         container_x_min, container_x_max):
    """Build the floor deck (inside-the-cavity) for one container.

    Geometry strategy:
      1. Start with a full-container-footprint solid slab at deck height
         (Z_FLOOR_TOP .. Z_CONTAINER_SLOPE_TOP).
      2. Cut out the sump pocket (lowers it by SUMP_DEPTH).
      3. Cut three "ramp" wedges adjacent to the sump that taper the
         deck's top face down to meet the sump's rim.
    """
    # 1. Slab covering entire container interior footprint
    slab = box(container_x_min, container_x_max,
               CONTAINER_INNER_WALL_Y1, CONTAINER_OUTER_WALL_Y0,
               Z_FLOOR_TOP, Z_CONTAINER_SLOPE_TOP)

    # 2. Cut the sump pocket: from the deck top down SUMP_DEPTH, over
    #    the sump's XY footprint.  This leaves only FLOOR thickness of
    #    printed material under the sump (Z_FLOOR_TOP to Z_TANK_BOTTOM
    #    is actually 25.4 of foam-pad space; the sump floor is at
    #    Z_TANK_BOTTOM == Z_CONTAINER_FLOOR).  We cut the deck only.
    sump_pocket = box(x_sump_min, x_sump_max,
                      sump_y_min, sump_y_max,
                      Z_CONTAINER_SLOPE_TOP - SUMP_DEPTH, Z_CONTAINER_SLOPE_TOP + OVERLAP)
    slab = slab.cut(sump_pocket)

    # 3. Ramp wedges.  Each wedge is a right triangular prism whose
    #    hypotenuse is the sloped deck surface.  We cut them out of the
    #    slab using a triangular cross-section extruded along one axis.
    #
    # Ramp A: along +Y side (sump's inner Y edge) extending Y toward
    #         the container's inner wall (sump_y_min outward).  Triangle
    #         in YZ plane: top corner (sump_y_min - SLOPE_RUN, top),
    #         hypotenuse to (sump_y_min, top - SUMP_DEPTH), vertical back
    #         down, closed.  Cut out the region above the hypotenuse.
    #
    # We'll build each wedge as: cut out the tetrahedron-like region
    # ABOVE a sloped plane, using a solid that fills the wedge.

    # Ramp going in -Y direction from sump_y_min toward inner wall
    # (only exists within sump's X range)
    ramp_y_len = max(0.0, sump_y_min - CONTAINER_INNER_WALL_Y1)
    ramp_y_run = min(SLOPE_RUN, ramp_y_len)
    if ramp_y_run > 0:
        # Triangle in YZ: (sump_y_min - ramp_y_run, Z_CONTAINER_SLOPE_TOP),
        #                 (sump_y_min, Z_CONTAINER_SLOPE_TOP),
        #                 (sump_y_min, Z_CONTAINER_SLOPE_TOP - SUMP_DEPTH)
        wedge = (
            cq.Workplane("YZ")
            .moveTo(sump_y_min - ramp_y_run, Z_CONTAINER_SLOPE_TOP + OVERLAP)
            .lineTo(sump_y_min + OVERLAP,     Z_CONTAINER_SLOPE_TOP + OVERLAP)
            .lineTo(sump_y_min + OVERLAP,     Z_CONTAINER_SLOPE_TOP - SUMP_DEPTH)
            .close()
            .extrude(x_sump_max - x_sump_min + 2 * OVERLAP)
            .translate((x_sump_min - OVERLAP, 0, 0))
        )
        slab = slab.cut(wedge)

    # Ramp going in +/-X direction from the sump's far-X edge toward
    # the container's end wall.  For container A the sump is at X=[-20,0]
    # so the ramp extends from x_sump_min in the -X direction.  For
    # container B, ramp extends from x_sump_max in +X direction.
    if x_sump_min > container_x_min + WALL:
        # Container A case: ramp in -X from x_sump_min
        ramp_x_len = x_sump_min - (container_x_min + WALL)
        ramp_x_run = min(SLOPE_RUN, ramp_x_len)
        if ramp_x_run > 0:
            wedge = (
                cq.Workplane("XZ")
                .moveTo(x_sump_min - ramp_x_run, Z_CONTAINER_SLOPE_TOP + OVERLAP)
                .lineTo(x_sump_min + OVERLAP,    Z_CONTAINER_SLOPE_TOP + OVERLAP)
                .lineTo(x_sump_min + OVERLAP,    Z_CONTAINER_SLOPE_TOP - SUMP_DEPTH)
                .close()
                .extrude(sump_y_max - sump_y_min + 2 * OVERLAP)
                .translate((0, sump_y_min - OVERLAP, 0))
            )
            slab = slab.cut(wedge)
    if x_sump_max < container_x_max - WALL:
        # Container B case: ramp in +X from x_sump_max
        ramp_x_len = (container_x_max - WALL) - x_sump_max
        ramp_x_run = min(SLOPE_RUN, ramp_x_len)
        if ramp_x_run > 0:
            wedge = (
                cq.Workplane("XZ")
                .moveTo(x_sump_max - OVERLAP,            Z_CONTAINER_SLOPE_TOP + OVERLAP)
                .lineTo(x_sump_max + ramp_x_run,         Z_CONTAINER_SLOPE_TOP + OVERLAP)
                .lineTo(x_sump_max - OVERLAP,            Z_CONTAINER_SLOPE_TOP - SUMP_DEPTH)
                .close()
                .extrude(sump_y_max - sump_y_min + 2 * OVERLAP)
                .translate((0, sump_y_min - OVERLAP, 0))
            )
            slab = slab.cut(wedge)

    return slab


# ═══════════════════════════════════════════════════════
# TENT CEILING (45 deg, ridge along X at Y = 110.5)
# ═══════════════════════════════════════════════════════
#
# The ceiling is a solid cap above the syrup cavity: its lower surface
# is the inverted-V tent (starts at Z_CEILING_START on Y=64.50 and
# Y=156.50 edges, peaks at Z_CEILING_PEAK along ridge at Y=110.5).  Its
# upper surface sits at Z_CONTAINER_WALL_TOP (= Z_CEILING_PEAK).
#
# Build as: a full box from Z_CEILING_START to Z_CEILING_PEAK over the
# container's XY cavity, minus the triangular-prism cavity below the
# tent.  Wait — we want the CEILING to be a thin skin, not a full block.
# Shell walls are 1 mm; the ceiling skin should also be 1 mm.
#
# Simpler: extrude a 1 mm thick ceiling along the tent path.  We do
# that by sweeping/extruding a triangular strip.
#
# Implementation:
#   - Build a triangular prism that fills the volume between the tent
#     surface and the plane Z = Z_CEILING_PEAK + WALL.
#   - The tent surface goes from (Y=64.50, Z=158) up to (Y=110.5,
#     Z=204) and back down to (Y=156.50, Z=158).
#   - For a 1 mm thick skin, offset the tent upward by WALL.
#
# We build it as two sloped slabs (one per side of the ridge), each a
# thin rectangular parallelepiped tilted 45 deg.

def build_tent_ceiling(container_x_min, container_x_max):
    """One container's 45 deg tent ceiling as a 1 mm skin."""
    # Two sloped slabs meeting at the ridge.
    # Side 1: Y from inner-wall (64.50) to ridge (110.5), slope goes
    #         from (Y=64.50, Z=158) to (Y=110.5, Z=204).
    # Side 2: Y from ridge to outer-wall (156.50), slope goes from
    #         (Y=110.5, Z=204) to (Y=156.50, Z=158).
    #
    # Each skin slab: extrude a parallelogram in YZ plane along X.
    # Parallelogram has:
    #   bottom edge on the tent surface (sloped)
    #   top edge parallel, offset by WALL normal to the slope
    # For 45 deg slope, normal offset of WALL means shift by
    # (WALL / sqrt(2)) in Y and Z for each face of the parallelogram.
    #
    # Simpler: make each slab as a trapezoid whose upper edge is
    # horizontal at Z = Z_CEILING_PEAK, clipped to the container XY.

    ridge_y = (CONTAINER_INNER_WALL_Y1 + CONTAINER_OUTER_WALL_Y0) / 2

    # Side 1: inner half (Y from 64.50 to ridge_y)
    profile_1 = (
        cq.Workplane("YZ")
        .moveTo(CONTAINER_INNER_WALL_Y1,              Z_CEILING_START)
        .lineTo(ridge_y,                              Z_CEILING_PEAK)
        .lineTo(ridge_y,                              Z_CEILING_PEAK + WALL)
        .lineTo(CONTAINER_INNER_WALL_Y1,              Z_CEILING_START + WALL)
        .close()
        .extrude(container_x_max - container_x_min)
        .translate((container_x_min, 0, 0))
    )

    # Side 2: outer half (Y from ridge_y to 156.50)
    profile_2 = (
        cq.Workplane("YZ")
        .moveTo(ridge_y,                              Z_CEILING_PEAK)
        .lineTo(CONTAINER_OUTER_WALL_Y0,              Z_CEILING_START)
        .lineTo(CONTAINER_OUTER_WALL_Y0,              Z_CEILING_START + WALL)
        .lineTo(ridge_y,                              Z_CEILING_PEAK + WALL)
        .close()
        .extrude(container_x_max - container_x_min)
        .translate((container_x_min, 0, 0))
    )

    return profile_1.union(profile_2, tol=0.05)


# ═══════════════════════════════════════════════════════
# VENT STANDPIPE
# ═══════════════════════════════════════════════════════

def build_standpipe(x, y):
    """Hollow tube from a container ceiling peak up above the shell top."""
    outer = (
        cq.Workplane("XY")
        .transformed(offset=(x, y, Z_CEILING_PEAK - 2.0))  # extend slightly below peak
        .circle(STANDPIPE_OD / 2)
        .extrude(STANDPIPE_TOP_Z - (Z_CEILING_PEAK - 2.0))
    )
    inner = (
        cq.Workplane("XY")
        .transformed(offset=(x, y, Z_CEILING_PEAK - 2.0 - OVERLAP))
        .circle(STANDPIPE_ID / 2)
        .extrude(STANDPIPE_TOP_Z - (Z_CEILING_PEAK - 2.0) + 2 * OVERLAP)
    )
    return outer.cut(inner)


# ═══════════════════════════════════════════════════════
# JG BOSS LOCAL THICKENING + THROUGH-HOLE
# ═══════════════════════════════════════════════════════

def build_boss_local_thickening(x_center):
    """Thickened boss around the through-hole on the container outer wall
    and on the shell outer wall, for 1/4\" NPT tap engagement."""
    # Inward-facing thickening on container outer wall (pokes into syrup).
    # Walls are 1 mm; with local boss we add BOSS_LOCAL_WALL more,
    # so thickening = BOSS_LOCAL_WALL - WALL = 2 mm extra material on
    # the inside face.
    container_boss = box(
        x_center - BOSS_LOCAL_HALF, x_center + BOSS_LOCAL_HALF,
        CONTAINER_OUTER_WALL_Y0 - (BOSS_LOCAL_WALL - WALL),
        CONTAINER_OUTER_WALL_Y0,
        BOSS_Z - BOSS_LOCAL_HALF, BOSS_Z + BOSS_LOCAL_HALF,
    )
    # Inward-facing thickening on shell +Y outer wall (pokes into foam).
    # Inner face of shell +Y wall is at SHELL_INNER_Y_PLUS; thickening
    # grows in the -Y direction (into the foam cavity).
    shell_boss = box(
        x_center - BOSS_LOCAL_HALF, x_center + BOSS_LOCAL_HALF,
        SHELL_INNER_Y_PLUS - (BOSS_LOCAL_WALL - WALL),
        SHELL_INNER_Y_PLUS,
        BOSS_Z - BOSS_LOCAL_HALF, BOSS_Z + BOSS_LOCAL_HALF,
    )
    return container_boss.union(shell_boss, tol=0.05)


def cut_boss_holes(solid, x_center):
    """Cut the 11 mm through-holes in container outer wall + shell +Y wall.

    Build a Y-aligned cylinder from a Z-aligned one via rotation.  This
    avoids any confusion about which way "XZ" workplane normals point.
    """
    y_start = CONTAINER_OUTER_WALL_Y0 - 2.0
    y_end   = SHELL_OUTER_Y_PLUS     + 2.0
    length = y_end - y_start

    # Build a cylinder along +Z, length `length`, centered at origin base.
    cyl = (
        cq.Workplane("XY")
        .circle(BOSS_HOLE_DIA / 2)
        .extrude(length)
    )
    # Rotate so axis goes along +Y instead of +Z: rotate -90 deg about X axis.
    cyl = cyl.rotate((0, 0, 0), (1, 0, 0), -90)
    # After this rotation, the cylinder extends from Y=0 to Y=+length, centered
    # on the X axis at Z=0. Translate to desired position.
    cyl = cyl.translate((x_center, y_start, BOSS_Z))
    return solid.cut(cyl)


# ═══════════════════════════════════════════════════════
# ASSEMBLE
# ═══════════════════════════════════════════════════════

def build_flavor_foam_shell():
    # --- outer shell ---
    part = build_shell_floor()
    part = part.union(build_shell_walls(), tol=0.1)

    # --- container walls ---
    part = part.union(build_container_walls(), tol=0.1)

    # --- container floor decks (separate per container) ---
    # Container A: X = [-CONTAINER_X_HALF, 0], sump at (X=[-20, 0], Y=[136.5, 156.5])
    deck_a = build_container_deck(
        x_sump_min=-SUMP_X_EXTENT,
        x_sump_max=-DIVIDER_HALF_THICKNESS,
        sump_y_min=CONTAINER_OUTER_WALL_Y0 - SUMP_Y_EXTENT,
        sump_y_max=CONTAINER_OUTER_WALL_Y0,
        container_x_min=-CONTAINER_X_HALF,
        container_x_max=-DIVIDER_HALF_THICKNESS,
    )
    # Container B: mirror of A
    deck_b = build_container_deck(
        x_sump_min=+DIVIDER_HALF_THICKNESS,
        x_sump_max=+SUMP_X_EXTENT,
        sump_y_min=CONTAINER_OUTER_WALL_Y0 - SUMP_Y_EXTENT,
        sump_y_max=CONTAINER_OUTER_WALL_Y0,
        container_x_min=+DIVIDER_HALF_THICKNESS,
        container_x_max=+CONTAINER_X_HALF,
    )
    part = part.union(deck_a, tol=0.1).union(deck_b, tol=0.1)

    # --- tent ceilings (per container) ---
    tent_a = build_tent_ceiling(-CONTAINER_X_HALF, -DIVIDER_HALF_THICKNESS)
    tent_b = build_tent_ceiling(+DIVIDER_HALF_THICKNESS, +CONTAINER_X_HALF)
    part = part.union(tent_a, tol=0.1).union(tent_b, tol=0.1)

    # --- vent standpipes ---
    sp_a = build_standpipe(STANDPIPE_X_A, STANDPIPE_Y)
    sp_b = build_standpipe(STANDPIPE_X_B, STANDPIPE_Y)
    part = part.union(sp_a, tol=0.1).union(sp_b, tol=0.1)

    # --- local bosses around JG through-holes ---
    part = part.union(build_boss_local_thickening(BOSS_X_A), tol=0.1)
    part = part.union(build_boss_local_thickening(BOSS_X_B), tol=0.1)

    # --- cut JG through-holes (11 mm dia, along +Y) ---
    part = cut_boss_holes(part, BOSS_X_A)
    part = cut_boss_holes(part, BOSS_X_B)

    return part


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    part = build_flavor_foam_shell()

    solids = part.solids().vals()
    print(f"Flavor-foam shell: {len(solids)} solid(s)")
    for i, s in enumerate(solids):
        bb = s.BoundingBox()
        print(f"  Solid {i}: X[{bb.xmin:.1f},{bb.xmax:.1f}] "
              f"Y[{bb.ymin:.1f},{bb.ymax:.1f}] Z[{bb.zmin:.1f},{bb.zmax:.1f}]")

    # Overall bounding box of the compound
    bb = part.val().BoundingBox()
    print(f"Bounding box: X[{bb.xmin:.2f},{bb.xmax:.2f}] "
          f"Y[{bb.ymin:.2f},{bb.ymax:.2f}] Z[{bb.zmin:.2f},{bb.zmax:.2f}]")

    out_dir = Path(__file__).resolve().parent
    out_path = out_dir / "flavor-foam-shell.step"
    cq.exporters.export(part, str(out_path))
    print(f"\nExported: {out_path}")
