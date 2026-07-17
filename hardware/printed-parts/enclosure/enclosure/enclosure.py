"""Kitchen Edition enclosure — a PETG box sized to the placed contents, split
into four printable pieces (front/back × bottom/top) that telescope and
cross-pin together.

Dimensions follow the contents at build time: the bounding box of the parts
placed by `../enclosure-assembly/_contents.py` is computed live, padded by an
interior clearance, then walled out. Features:

  * A flat 45° display-mounting facet (a solid surface) chamfered into the
    top-front-left corner, flush to the −X edge.
  * A front↔back split (a Y-plane seam pushed as far back as the cold core
    allows): the front pieces' rear walls telescope (a full-wall lip,
    nothing shaved) into the back pieces, and four interlocking screw
    bosses cross the seam — one per ±X side wall per level, the bottom pair
    tucked just under the front Z seam (so it pins the two bottom pieces),
    the top pair under the ceiling. Each boss is on an X axis: the screw
    drives in from the left/right EXTERIOR face. The BACK piece carries the
    PLUG (faucet mounting-plate idiom): a cylinder reaching inward from the
    corner with a screw clearance through it, backed by a corner brace. The
    FRONT piece's lip carries the SOCKET (faucet shell-bottom idiom): a pod
    bored to receive the plug, open on its +Y face so the plug drops in as
    the pieces close, with a ruthex M3 heat-set at the deep end.
  * A bottom↔top split per column — the same joint rotated 90°, at a
    different height each side of the Y seam (the seams stagger like a
    brick bond; the front pair joins, the back pair joins, then the front
    assembly telescopes into the back). The BOTTOM pieces carry the lip — a
    3-sided band (their outer ±Y wall + both side walls, stopping short of
    the Y-seam overlap) telescoping +Z into the top pieces — with the
    socket pods; the TOP pieces carry the D-pins, their tabs rising to the
    lip rim where corner braces back them. Four X-axis screws cross each
    seam (one per side wall per Y column: front pins at the front-wall
    corners, back pins just behind the Y-seam mouth).

main() exports the four printable pieces (enclosure-front-bottom.step,
enclosure-front-top.step, enclosure-back-bottom.step, enclosure-back-top.step)
plus enclosure.step — the four as separate solids in assembled position,
seams intact (mirrors `touch_flo_shell.py`).
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
sys.path.insert(0, str(_repo / "hardware" / "scripts"))
sys.path.insert(0, str(_repo / "tools"))
sys.path.insert(0, str(_repo / "hardware" / "printed-parts" / "enclosure" / "enclosure-assembly"))
from _cadq_export import export_step, export_assembly
from docgen import substitute_md, substitute_py_comments
import _contents

# Shell parameters.
wall = 3.0                  # PETG wall thickness
interior_clearance = 0.0    # gap between contents bbox and inner wall
corner_round = 12.          # vertical (Y) print-corner relief radius (anti-warp on the bed)

# H2C left-nozzle build envelope; each printed HALF must fit inside this.
H2C_X, H2C_Y, H2C_Z = 325.0, 320.0, 320.0

# Display-mounting facet — a flat 45° SOLID surface chamfered into the
# top-front-left corner for the Waveshare ESP32-S3-Touch-LCD-4.3B config
# display (../../../reference/waveshare-43b-display/), facing up-and-forward
# (−Y front / +Z up) toward the standing user. The glass is the datum — centered
# on the facet, which is the glass + a 3 mm buffer all around:
# [119.5 mm](DISPLAY_FACET_X) (X, lateral) × [83 mm](DISPLAY_FACET_SLOPE) (along
# the 45° slope). The glass overhangs the PCB body unevenly, so the body sits
# offset behind it; the facet is flush to the −X (left) edge, so the
# top-front-left corner comes off.
display_bezel_x = 113.5           # bezel glass, lateral (X)
display_bezel_slope = 77.0        # bezel glass, up the slope
# The glass is the datum (centered on the facet); the PCB body sits offset behind
# it because the glass overhangs the body unevenly (up-and-left). This is the
# body's own offset from the centered glass.
display_body_offset_x = 0.5      # PCB body offset from the centered glass, lateral (+X)
display_body_offset_slope = -1.0 # PCB body offset, down-slope
display_corner_r = 2.5           # corner rounding, matching the display bezel
display_facet_buffer = 3.0       # facet buffer around the glass, all around
display_facet_x = display_bezel_x + 2 * display_facet_buffer          # [119.5 mm](DISPLAY_FACET_X)
display_facet_slope = display_bezel_slope + 2 * display_facet_buffer  # [83 mm](DISPLAY_FACET_SLOPE)
display_facet_angle_deg = 45.0
# The facet is a display housing this deep (the wall behind it, set to the
# display's overall depth) with the display let into it: a shallow bezel
# counterbore on the user face and a PCB through-hole down the full thickness.
display_facet_thickness = 19.0   # facet wall depth = display envelope depth
display_bezel_depth = 2.0        # bezel counterbore depth, user face
display_pcb_x = 106.0            # PCB body through-hole, lateral (X)
display_pcb_slope = 69.0         # PCB body through-hole, up the 45° slope
display_pcb_cut_through = 3.0    # extra depth past the facet back, cutting the
                                 # corner pod clean through (it overhangs the hole otherwise)

# Hopper funnel opening (Zone C) — one rectangular opening through the top
# wall spanning the whole zone right of the display, where the removable
# silicone funnel basin (../../zone-c/hopper-funnel/) drops in and floors
# just above the front towers. The nominals below are oversized so the cut
# derives to everything its neighbors allow: the display end-wall gusset
# left, the top-right corner pod's inboard end, the Y-seam lip band behind
# — and a front ledge kept along the front edge, so a wall frame remains
# all around for the basin's rim flange to rest on.
hopper_hole_x = 200.0   # opening width (X), nominal before the corner-pod clamp
hopper_hole_y = 200.0   # opening depth (Y), nominal before the Y-seam clamp
hopper_front_ledge = 8.0  # top wall kept along the front edge
# The funnel's basin depth is a ceiling law: the interior reserves this much
# height above the tallest content under the opening (the pump-1 tower, read
# in _dims the same way hopper_funnel.py reads it), so the basin — straight
# chute + drain loft — swallows a full 440 mL SodaStream bottle poured in one
# go (hopper_funnel.py prints the real capacity at export).
hopper_min_depth = 41.0

# Split + boss parameters — every dimension sized to its function, nothing
# inherited from the faucet. The seam is a Y plane; the front half's full-wall
# rear lip telescopes into the back; four corner bosses cross-pin the seam with
# M3 screws from the ±X exterior. Each boss is a D-section pin: round where it
# registers in the front socket bore, with a flat tab running +Y to the lip rim
# where the back-half corner brace backs it. The screw spans the head seat to the
# front heat-set, so the pin body is screw_len − heatset_depth long.
split_slip = 0.40            # diametral slide fit, plug into socket bore
screw_clear_dia = 3.9        # M3 shank clearance
head_cbore_dia = 6.15        # M3 SHCS head counterbore
head_cbore_depth = 4.0       # head recess depth from the ±X exterior (the head seat)
screw_len = 10.0             # M3 SHCS under-head length (M3x10), head seat → heat-set
plug_dia = screw_clear_dia + 2.0 * wall          # 9.9 — the shank + one wall each side
socket_bore_dia = plug_dia + split_slip          # 10.3 — slide fit over the plug
socket_r = socket_bore_dia / 2.0 + wall          # pod half-size: one wall around the bore
heatset_dia = 4.0            # ruthex M3 short heat-set
heatset_depth = 5.25
socket_cap = wall            # one wall capping the insert's deep end
# The telescoping overlap is NOT a free dimension. It is exactly what makes the
# back plug's −Y face mate the back mouth (y_joint) AND the front socket pod's
# +Y face mate the lip rim, with the two bosses coaxial for the cross-screw.
# With y_boss = y_joint + plug_dia/2 (plug −Y on the mouth), the pod's +Y face
# (y_boss + socket_r) lands on the rim iff lip_len = plug_dia/2 + socket_r.
lip_len = plug_dia / 2.0 + socket_r              # = (plug+bore)/2 + wall = 13.1

# The bottom↔top seam planes, one per Y column. The seam machinery (a
# one-wall lip + the cross-pin pods) protrudes into the cavity at the walls,
# so each seam must cross a band the contents leave open there.
#   * Back: the cold core spans the full interior width and touches the ±X
#     and rear walls all the way up to its foam-cap top, and the rear
#     bulkhead field begins just above the lip rim (_contents
#     UMBILICAL_Z_FLOOR is derived from it) — the seam sits in the one band
#     between foam and ports.
#   * Front: at the front stack's waist — above the condenser (which stands
#     against the front wall), below the pump-2/electronics tower — which
#     also splits the front column's height far more evenly than the back's
#     foam-locked seam can.
# Every printed piece's bed face fits the H2C envelope with these cuts.
z_joint_front = 186.0
z_joint_back = 266.0
# The Z lip stops this short of the Y-seam overlap on each side, so the two
# telescopes never share a wall surface.
z_lip_y_margin = 2.0


# --- primitives -------------------------------------------------------------

def _ybox(x0, x1, y0, y1, z0, z1):
    return (
        cq.Workplane("XY")
        .box(x1 - x0, y1 - y0, z1 - z0, centered=False)
        .translate((x0, y0, z0))
        .val()
    )


def _xcyl(r, y, z, x0, x1):
    """Cylinder of radius r along X from x0 to x1, axis at (y, z)."""
    return cq.Solid.makeCylinder(r, abs(x1 - x0), cq.Vector(min(x0, x1), y, z), cq.Vector(1, 0, 0))


def _round_y(solid, r):
    """Round a box solid's four vertical (Y) corner edges by r — the print-bed
    corner relief, about the Y axis the halves print along. r <= 0 leaves the
    corners square (an inset radius can shrink past nothing)."""
    if r <= 0:
        return solid
    return cq.Workplane(obj=solid).edges("|Y").fillet(r).val()


def _round_corner_y(solid, xc, zc, r):
    """Round only the single vertical (Y) corner edge of a box at (xc, zc).
    r <= 0 leaves the corner square."""
    if r <= 0:
        return solid
    wp = cq.Workplane(obj=solid)
    edges = [e for e in wp.edges("|Y").vals()
             if abs(e.Center().x - xc) < 1e-6 and abs(e.Center().z - zc) < 1e-6]
    return wp.newObject(edges).fillet(r).val()


# --- box dimensions, driven by the placed contents -------------------------

def _dims():
    placed = _contents.build()
    bbs = [s.BoundingBox() for s, _c in placed.values()]
    cxmin = min(b.xmin for b in bbs); cxmax = max(b.xmax for b in bbs)
    cymin = min(b.ymin for b in bbs); cymax = max(b.ymax for b in bbs)
    czmin = min(b.zmin for b in bbs); czmax = max(b.zmax for b in bbs)
    ix0, ix1 = cxmin - interior_clearance, cxmax + interior_clearance
    iy0, iy1 = cymin - interior_clearance, cymax + interior_clearance
    # The floor is a fixed Z=0 datum, not the lowest content — so parts can stand
    # on feet above it (the floor, seam lip, and braces stay put). The ceiling
    # follows the tallest content — EXCEPT along the ±X walls, where the
    # Y-seam's top cross-pin pods hug the ceiling and reach one boss chain
    # inboard: content inside that reach sets the ceiling at its top plus the
    # pod stack, so the pods never land on it. What actually fixes the box
    # height is the hopper law below: the funnel's basin is content too.
    iz0 = min(czmin, 0.0) - interior_clearance
    iz1 = czmax + interior_clearance
    boss_in = head_cbore_depth + screw_len + socket_cap - wall   # pod reach inboard of the wall
    pod_stack = wall + socket_bore_dia / 2.0 + socket_r + 1.5    # ceiling → pod bottom + margin
    wall_band_top = max(
        (b.zmax for b in bbs if b.xmin < ix0 + boss_in or b.xmax > ix1 - boss_in),
        default=iz0)
    iz1 = max(iz1, wall_band_top + pod_stack)
    ox0, ox1 = ix0 - wall, ix1 + wall
    oy0, oy1 = iy0 - wall, iy1 + wall
    # Split plane: as close to the box's Y midpoint as its neighbors allow,
    # for four near-quarter pieces. The display housing bounds it from the
    # front (the whole facet stays in the front pieces); the cold core bounds
    # it from the back — the back Z-seam pods sit behind the Y-seam mouth
    # (bore axis at lip_len + wall + bore radius past y_joint, pod reaching
    # socket_r further) and must stop ahead of the foam. (No Z terms: the
    # provisional tuples below are final in X and Y.)
    inner = (ix0, ix1, iy0, iy1, iz0, iz1)
    outer = (ox0, ox1, oy0, oy1, iz0 - wall, iz1 + wall)
    _fa, _fn, _fo, _fdy, _fdz = _facet_geom(outer)
    facet_back_y = oy0 + _fdy + display_facet_thickness * math.sqrt(2.0)
    cold_front_y = placed["foam-assembly"][0].BoundingBox().ymin
    y_free = cold_front_y - 2.0 - (lip_len + wall + socket_bore_dia / 2.0 + socket_r)
    y_joint = max(facet_back_y + 2.0, min((iy0 + iy1) / 2.0, y_free))
    # The hopper ceiling law: the top wall right of the display is one open
    # rectangle the funnel drops through, and the interior keeps
    # hopper_min_depth of basin above the tallest content under it.
    hx0, hx1, hy0, hy1 = _hopper_hole(inner, outer, y_joint)
    under_top = max(
        (b.zmax for b in bbs
         if min(b.xmax, hx1) > max(b.xmin, hx0)
         and min(b.ymax, hy1) > max(b.ymin, hy0)),
        default=iz0)
    iz1 = max(iz1, under_top + hopper_min_depth)
    inner = (ix0, ix1, iy0, iy1, iz0, iz1)
    outer = (ox0, ox1, oy0, oy1, iz0 - wall, iz1 + wall)
    return inner, outer, y_joint, cold_front_y


# --- display facet (solid surface) -----------------------------------------

def _facet_geom(outer):
    ox0, ox1, oy0, oy1, oz0, oz1 = outer
    a = math.radians(display_facet_angle_deg)
    dy = display_facet_slope * math.sin(a)   # back from the front face
    dz = display_facet_slope * math.cos(a)   # down from the top face
    normal = (0.0, -math.sin(a), math.cos(a))
    origin = (0.0, oy0 + dy / 2.0, oz1 - dz / 2.0)
    return a, normal, origin, dy, dz


def _halfspace(origin, normal, extent):
    """Solid filling the +normal side of the plane through origin."""
    plane = cq.Plane(origin=cq.Vector(*origin), xDir=cq.Vector(1, 0, 0), normal=cq.Vector(*normal))
    return cq.Workplane(plane).rect(4 * extent, 4 * extent).extrude(extent).val()


def _facet_x_slab(outer, extent):
    """The facet's lateral window: flush to the −X edge, display_facet_x wide."""
    ox0 = outer[0]
    return _ybox(ox0, ox0 + display_facet_x, -2 * extent, 2 * extent, -2 * extent, 2 * extent)


def _facet_wedge(outer):
    """The solid removed to cut the display facet — the +normal half-space in
    the facet's lateral window. Re-cut after the corner pods so they too are
    chamfered to the facet plane rather than poking through it."""
    ox0, ox1, oy0, oy1, oz0, oz1 = outer
    a, normal, origin, dy, dz = _facet_geom(outer)
    extent = max(ox1 - ox0, oy1 - oy0, oz1 - oz0) + 100.0
    return _halfspace(origin, normal, extent).intersect(_facet_x_slab(outer, extent))


def _rounded_outer(outer):
    """The outer box with rounded vertical corners and the facet chamfered in —
    the print silhouette the half is clipped to so nothing pokes past it."""
    ox0, ox1, oy0, oy1, oz0, oz1 = outer
    box = _round_y(_ybox(ox0, ox1, oy0, oy1, oz0, oz1), corner_round)
    return box.cut(_facet_wedge(outer))


def _shell_with_facet(inner, outer):
    """Hollow box with the 45° facet as a SOLID `wall`-thick surface: chamfer
    the outer box, and hold the cavity one wall back from the facet plane. The
    vertical corners are relieved for the print bed — outer by `corner_round`,
    cavity one wall less (square once the inset reaches zero)."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    ox0, ox1, oy0, oy1, oz0, oz1 = outer
    a, normal, origin, dy, dz = _facet_geom(outer)
    extent = max(ox1 - ox0, oy1 - oy0, oz1 - oz0) + 100.0

    inner_box = _round_y(_ybox(ix0, ix1, iy0, iy1, iz0, iz1), corner_round - wall)
    outer_chamfered = _rounded_outer(outer)

    back_origin = (origin[0] - display_facet_thickness * normal[0],
                   origin[1] - display_facet_thickness * normal[1],
                   origin[2] - display_facet_thickness * normal[2])
    keepout = _halfspace(back_origin, normal, extent).intersect(_facet_x_slab(outer, extent))
    inner_clipped = inner_box.cut(keepout)

    return cq.Workplane(obj=outer_chamfered.cut(inner_clipped))


def _display_cuts(outer):
    """The display let into the facet: a shallow bezel counterbore on the user
    face and a PCB through-hole down the full facet thickness — both cut along
    the facet's 45° normal, starting one mm proud of the face for a clean break.
    The glass is the datum: the bezel counterbore is centered on the facet (a
    uniform buffer all around). The glass overhangs the body unevenly, so the PCB
    hole sits offset by display_body_offset — and is cut display_pcb_cut_through
    past the back to take the corner pod (which would otherwise overhang it)
    clean through. Counterbore corners rounded to the display radius."""
    a, normal, origin, dy, dz = _facet_geom(outer)
    center = (outer[0] + display_facet_x / 2.0, origin[1], origin[2])
    plane = cq.Plane(origin=cq.Vector(*center), xDir=cq.Vector(1, 0, 0), normal=cq.Vector(*normal))
    along_normal = cq.selectors.ParallelDirSelector(cq.Vector(*normal))
    bezel = (
        cq.Workplane(plane).workplane(offset=1.0)
        .rect(display_bezel_x, display_bezel_slope)
        .extrude(-(display_bezel_depth + 1.0))
        .edges(along_normal).fillet(display_corner_r).val()
    )
    pcb = (
        cq.Workplane(plane).workplane(offset=1.0)
        .center(display_body_offset_x, display_body_offset_slope)  # body sits opposite the glass overhang
        .rect(display_pcb_x, display_pcb_slope)
        .extrude(-(display_facet_thickness + display_pcb_cut_through + 1.0)).val()  # through the pod
    )
    return bezel.fuse(pcb)


def _facet_end_wall(inner, outer):
    """Close the facet recess at its +X edge, where the recessed facet panel
    meets the resumed square corner. A one-`wall` gusset just inboard of the
    edge fills the corner bounded by the inner front wall, the inner top wall,
    and the housing BACK plane — spanning the full housing depth so it is flush
    and continuous with the slab, not tangent to the facet at a knife edge.
    (The −X edge needs no such wall — the left exterior wall seals it.)"""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    ox0, ox1, oy0, oy1, oz0, oz1 = outer
    a, normal, origin, dy, dz = _facet_geom(outer)
    extent = max(ox1 - ox0, oy1 - oy0, oz1 - oz0) + 100.0
    x_edge = ox0 + display_facet_x
    back = tuple(origin[i] - display_facet_thickness * normal[i] for i in range(3))
    c = back[2] - back[1]   # housing back plane: z − y = c
    bbox = _ybox(x_edge, x_edge + wall, iy0, iz1 - c, c + iy0, iz1)
    return bbox.intersect(_halfspace(back, normal, extent))


# --- hopper funnel opening (Zone C) -----------------------------------------

def _hopper_hole(inner, outer, y_joint):
    """Rectangle (x0, x1, y0, y1) of the funnel opening in the top wall: its
    −X edge flush past the display end-wall gusset (right of the facet), its
    −Y edge one front ledge behind the inner front wall, width/depth from the
    hopper parameters — the +X edge clamped to clear the top-right corner
    pod's inboard end, the +Y edge clamped ahead of the Y-seam lip band (the
    hole must live whole in the front-top piece). The companion funnel
    (../../zone-c/hopper-funnel/) derives its basin from this same rect."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    ox0, ox1, oy0, oy1, oz0, oz1 = outer
    x0 = ox0 + display_facet_x + wall                  # just past the facet gusset
    pod_in = ix1 + wall - (head_cbore_depth + screw_len + socket_cap)
    x1 = min(x0 + hopper_hole_x, pod_in - 1.0)         # clear the top-right pod
    y0 = iy0 + hopper_front_ledge
    y1 = min(y0 + hopper_hole_y, y_joint - wall - 2.0)  # clear the Y-seam lip
    return x0, x1, y0, y1


def _hopper_cut(inner, outer, y_joint):
    """The funnel throat punched clean through the top wall."""
    x0, x1, y0, y1 = _hopper_hole(inner, outer, y_joint)
    return _ybox(x0, x1, y0, y1, inner[5] - 1.0, outer[5] + 1.0)


# --- split joint: telescoping lip + X-axis corner cross-pins ----------------
#
# Four bosses cross the seam, one in each top/bottom corner of the ±X side
# walls. Each mates the walls of the overlap — the back plug's −Y face on the
# back mouth, the front socket pod's +Y face on the lip rim — and the two are
# COAXIAL by construction (one y_boss, one z_boss feed both halves); the overlap
# (lip_len) is derived from exactly those matings, not chosen freely. An M3 SHCS
# drives in from the ±X exterior; outboard→inboard the joint reads: head
# counterbore, then the pin body (screw_len − heatset_depth of material the shank
# crosses), then the heat-set, then a one-wall cap.
#   * BACK half = D-PIN: a round cylinder from the ±X exterior to the heat-set
#     (registers in the socket bore), fused to a flat +Y tab running to the lip
#     rim where the corner brace backs it. Sized to the screw SHANK, not the head
#     (the head sits in the wall counterbore); screw-clearance + head counterbore
#     bored in.
#   * FRONT lip = SOCKET: a corner pod, integral with the ±Z wall, bored to
#     receive the round pin (slide fit), the heat-set + cap at the deep inboard
#     end, and a +Y channel the pin's tab slides through as the lip telescopes
#     into the back.
# The head seats in the back wall; the shank crosses the pin body into the front
# heat-set, cross-pinning the two halves along X.

def _bosses(inner, split=None, brace_y_short=None):
    """Per-boss tuple (x_in, x_ext, sx, z_boss, pod_z, zc, brace_z, brace_y1):
    the inner ±X wall face the screw passes through, its matching exterior
    face, sx = +1 (left) / −1 (right) inboard, the bore-axis height, the
    socket pod's z-span + the box corner it rounds to (None mid-wall), and the
    back brace's z-span + its +Y reach. Two levels per side: with a Z seam
    (`split`) the lower pair rides just under it — the floor corners stay
    clear for the cold core, and the lower braces stop ahead of it
    (`brace_y_short`); without one (the coupon) the lower pair sits one wall
    above the floor."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    r = socket_bore_dia / 2.0
    zt = iz1 - wall - r
    top = ((zt - socket_r, iz1), iz1, (zt - plug_dia / 2.0, iz1), None)
    if split is None:
        zb = iz0 + wall + r
        bot = ((iz0, zb + socket_r), iz0, (iz0, zb + plug_dia / 2.0), None)
    else:
        zb = split - wall - r
        bot = ((zb - socket_r, split), None, (zb - plug_dia / 2.0, split), brace_y_short)
    out = []
    for z_boss, (pod_z, zc, brace_z, by1) in ((zb, bot), (zt, top)):
        out.append((ix0, ix0 - wall, +1.0, z_boss, pod_z, zc, brace_z, by1))
        out.append((ix1, ix1 + wall, -1.0, z_boss, pod_z, zc, brace_z, by1))
    return out


def _boss_x(x_ext, sx):
    """Inboard X stations from the ±X exterior, each sized to its job: the
    screw-head seat (recess), the pin/heat-set boundary (the screw spans the seat
    to the heat-set, so the pin body is screw_len − heatset_depth long), the
    heat-set end, and the pod cap one wall past it."""
    x_seat = x_ext + sx * head_cbore_depth
    x_tip = x_seat + sx * (screw_len - heatset_depth)
    x_heat = x_tip + sx * heatset_depth
    x_cap = x_heat + sx * socket_cap
    return x_seat, x_tip, x_heat, x_cap


def _back_plug(x_ext, sx, z_boss, y_boss, y_joint):
    """BACK D-pin: a round cylinder from the ±X exterior to the heat-set (it
    registers in the front socket bore), fused to a flat tab running +Y to the
    lip rim, so the corner brace butting that rim backs the X-axis pin in Y. The
    tab is the pin diameter wide and slides through the socket's +Y channel."""
    _xs, x_tip, _xh, _xc = _boss_x(x_ext, sx)
    cyl = _xcyl(plug_dia / 2.0, y_boss, z_boss, x_ext, x_tip)
    xa, xb = sorted((x_ext, x_tip))
    tab = _ybox(xa, xb, y_boss, y_joint + lip_len,
                z_boss - plug_dia / 2.0, z_boss + plug_dia / 2.0)
    return cyl.fuse(tab)


def _front_pod(x_in, x_ext, sx, pod_z, zc, y_joint, inner):
    """FRONT socket pod (solid): a rib bounded by the faces it mates — in Y
    from the front wall's inner face (iy0) all the way to the rim, in X the
    side wall to the cap, in Z the pod's span (out to the floor/ceiling when
    it lives in a box corner). Running full depth to the front wall, it has no
    −Y overhang when the front piece prints −Y-down — it grows straight up
    from the wall. Bore / heat-set / channel are cut afterwards; the facet
    trims the top-front-left pod back to its plane."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    _xs, _xt, _xh, x_cap = _boss_x(x_ext, sx)
    xa, xb = sorted((x_in, x_cap))
    za, zb = pod_z
    pod = _ybox(xa, xb, iy0, y_joint + lip_len, za, zb)
    if zc is None:
        return pod
    # Round the outer corner (the one at the side wall) concentric with the
    # cavity, one wall in, so the pod's telescoping reach fits the back's rounded
    # corner instead of fouling it.
    return _round_corner_y(pod, x_in, zc, corner_round - wall)


def _back_brace(x_in, x_ext, sx, brace_z, brace_y1, y_joint, outer):
    """BACK brace (solid): a rib on the ±X side wall behind each pin, running
    the back piece's free Y length — from the lip rim (where the telescoped
    front lip + sockets stop, so it never fouls them) to the rear wall, or to
    `brace_y1` where the cold core stands in the way. Sized to the pin it
    backs (in X to the pin's inboard end, in Z to the pin — no further toward
    centre) and butting the pin's flat tab at the rim, so it supports the
    X-axis pin in Y and anchors the wall against peeling."""
    ox0, ox1, oy0, oy1, oz0, oz1 = outer
    _xs, x_tip, _xh, _xc = _boss_x(x_ext, sx)
    xa, xb = sorted((x_in, x_tip))
    za, zb = brace_z
    return _ybox(xa, xb, y_joint + lip_len, brace_y1 if brace_y1 is not None else oy1, za, zb)


def _front_cuts(x_in, x_ext, sx, z_boss, y_boss, y_joint):
    """Front-socket inner cuts: the bore that receives the plug, the heat-set
    pocket at the deep end, and a +Y channel for slide-in. The slip lives on the
    +Y (slide-in) side: the bore is shifted +slip/2 so its −Y wall registers on
    the plug's −Y face at the mouth, instead of overshooting past the seam. The
    heat-set stays coaxial with the screw at y_boss."""
    _xs, x_tip, x_heat, _xc = _boss_x(x_ext, sx)
    bore_y = y_boss + split_slip / 2.0
    bore = _xcyl(socket_bore_dia / 2.0, bore_y, z_boss, x_in, x_tip)
    heat = _xcyl(heatset_dia / 2.0, y_boss, z_boss, x_tip, x_heat)
    bx0, bx1 = sorted((x_in, x_tip))
    cz0, cz1 = z_boss - socket_bore_dia / 2.0, z_boss + socket_bore_dia / 2.0
    chan = _ybox(bx0, bx1, bore_y, y_joint + lip_len + 1.0, cz0, cz1)
    return bore.fuse(heat).fuse(chan)


def _screw_cut(x_ext, sx, z_boss, y_boss):
    """M3 shank clearance from the ±X exterior through the plug to the heat-set,
    plus the SHCS head counterbore at the exterior — the seat one wall outboard
    of the heat-set."""
    _xs, x_tip, _xh, _xc = _boss_x(x_ext, sx)
    shank = _xcyl(screw_clear_dia / 2.0, y_boss, z_boss, x_ext - sx * 1.0, x_tip)
    cbore = _xcyl(head_cbore_dia / 2.0, y_boss, z_boss, x_ext - sx * 1.0, x_ext + sx * head_cbore_depth)
    return shank.fuse(cbore)


def _front_lip(inner, y_joint):
    """The front half's rear lip: a full-`wall` perimeter band whose outer face
    is flush with the body's inner wall — one solid with the body, nothing
    shaved — telescoping +Y into the back half and mating its inner wall. It runs
    one `wall` back into the body cavity (the fusion shoulder / telescoping stop)
    and forward over the overlap to the rim. Its −Y end is a 45° frame bevel (the
    cavity mouth flares out to the outer over one wall), not a flat downward
    ring, so it prints with no steeper-than-45° overhang −Y-down."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    y0, y1 = y_joint - wall, y_joint + lip_len
    # Outer face flush with (and corners concentric to) the cavity it telescopes
    # into; inner one wall further in.
    outer = _round_y(_ybox(ix0, ix1, y0, y1, iz0, iz1), corner_round - wall)
    # Cavity cutter: a 45° flare at the −Y end (mouth widens from the inner
    # rectangle out to the outer over one wall in Y), then the straight inner
    # box. Subtracting it bevels the lip's −Y inner edge into the ramp.
    cx, cz = (ix0 + ix1) / 2.0, (iz0 + iz1) / 2.0
    flare = (
        cq.Workplane(cq.Plane(origin=(cx, y0, cz), xDir=(1, 0, 0), normal=(0, 1, 0)))
        .rect(ix1 - ix0, iz1 - iz0)
        .workplane(offset=wall)
        .rect((ix1 - ix0) - 2.0 * wall, (iz1 - iz0) - 2.0 * wall)
        .loft(combine=True)
        .val()
    )
    inner_box = _round_y(
        _ybox(ix0 + wall, ix1 - wall, y0 + wall, y1 + 1.0, iz0 + wall, iz1 - wall),
        corner_round - 2.0 * wall,
    )
    return outer.cut(flare.fuse(inner_box))


# Boss Y position — one value feeds the plug AND the socket, so they are
# coaxial by construction. Placed so the plug's −Y face mates the back mouth;
# the derived lip_len then lands the socket pod's +Y face on the lip rim.
def _y_boss(y_joint):
    return y_joint + plug_dia / 2.0


# --- bottom↔top joint: the same telescoping lip + X-axis pins, rotated ------
#
# The BOTTOM pieces carry the lip and the socket pods; the TOP pieces carry
# the D-pins and the braces that back them from above. The pin axis sits at
# z_pin = z_joint + plug_dia/2 (pin −Z face on the top piece's mouth), the
# pod's +Z face lands on the lip rim at z_joint + lip_len, and the top piece
# slides down over the lip — the pin dropping into the pod's +Z-open channel.


def _z_pin_z(zj):
    return zj + plug_dia / 2.0


def _z_stations(inner, y_joint):
    """X-axis pin stations along the Z seams, one per ±X wall per Y column:
    front pins in the front-wall corners (their pods grow from the front
    wall), back pins just behind the Y-seam mouth (their pods and braces
    start where the telescoped front lip stops). Each column's stations ride
    that column's own seam height."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    yf = iy0 + wall + socket_bore_dia / 2.0
    yb = y_joint + lip_len + wall + socket_bore_dia / 2.0
    return [
        (ix0, ix0 - wall, +1.0, yf, "front"),
        (ix1, ix1 + wall, -1.0, yf, "front"),
        (ix0, ix0 - wall, +1.0, yb, "back"),
        (ix1, ix1 + wall, -1.0, yb, "back"),
    ]


def _z_lip(inner, y_joint, zj):
    """The bottom pieces' seam lip: a full-wall band whose outer faces are
    flush with the body's inner walls, running one wall down into the body
    (the fusion shoulder) and up over the overlap to the rim. The segment
    crossing the Y-seam overlap is dropped, so each piece carries a 3-sided
    lip and the two telescopes never stack on one wall surface."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    z0, z1 = zj - wall, zj + lip_len
    ring = _ybox(ix0, ix1, iy0, iy1, z0, z1).cut(
        _ybox(ix0 + wall, ix1 - wall, iy0 + wall, iy1 - wall, z0 - 1.0, z1 + 1.0))
    gap = _ybox(ix0 - 1.0, ix1 + 1.0,
                y_joint - wall - z_lip_y_margin, y_joint + lip_len + z_lip_y_margin,
                z0 - 1.0, z1 + 1.0)
    return ring.cut(gap)


def _z_pod(x_in, x_ext, sx, ys, col, y_joint, inner, zj):
    """BOTTOM socket pod: the Y-pod rotated — a rib on the ±X wall reaching
    +Z to the lip rim. The front-column pod grows from the front wall (no
    print overhang, front pieces printing −Y-down); the back-column pod
    starts where the lip does, behind the Y-seam overlap."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    _xs, _xt, _xh, x_cap = _boss_x(x_ext, sx)
    xa, xb = sorted((x_in, x_cap))
    za = _z_pin_z(zj) - socket_r
    zb = zj + lip_len
    if col == "front":
        ya, yb = iy0, ys + socket_r
    else:
        ya, yb = y_joint + lip_len + z_lip_y_margin, ys + socket_r
    return _ybox(xa, xb, ya, yb, za, zb)


def _z_pin(x_ext, sx, ys, zj):
    """TOP D-pin: a round cylinder from the ±X exterior to the heat-set, fused
    to a flat tab rising +Z to the lip rim, where the top piece's brace backs
    it. The tab is the pin diameter wide and slides down the socket's +Z
    channel as the pieces close."""
    _xs, x_tip, _xh, _xc = _boss_x(x_ext, sx)
    zp = _z_pin_z(zj)
    cyl = _xcyl(plug_dia / 2.0, ys, zp, x_ext, x_tip)
    xa, xb = sorted((x_ext, x_tip))
    tab = _ybox(xa, xb, ys - plug_dia / 2.0, ys + plug_dia / 2.0,
                zp, zj + lip_len)
    return cyl.fuse(tab)


def _z_brace(x_in, x_ext, sx, ys, col, inner, outer, zj):
    """TOP brace: a rib on the ±X wall over each pin, from the lip rim up to
    the ceiling. The front-column brace grows from the front wall; the back
    column's stands alone behind the mouth."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    ox0, ox1, oy0, oy1, oz0, oz1 = outer
    _xs, x_tip, _xh, _xc = _boss_x(x_ext, sx)
    xa, xb = sorted((x_in, x_tip))
    if col == "front":
        ya, yb = iy0, ys + plug_dia / 2.0
    else:
        ya, yb = ys - plug_dia / 2.0, ys + plug_dia / 2.0
    return _ybox(xa, xb, ya, yb, zj + lip_len, oz1)


def _z_pod_cuts(x_in, x_ext, sx, ys, zj):
    """Bottom-pod inner cuts: the bore that receives the pin, the heat-set
    pocket at the deep end, and a +Z channel for the slide-down. The slip
    lives on the +Z (slide-in) side: the bore is shifted +slip/2 so its −Z
    wall registers on the pin's −Z face at the mouth."""
    _xs, x_tip, x_heat, _xc = _boss_x(x_ext, sx)
    zp = _z_pin_z(zj)
    bore_z = zp + split_slip / 2.0
    bore = _xcyl(socket_bore_dia / 2.0, ys, bore_z, x_in, x_tip)
    heat = _xcyl(heatset_dia / 2.0, ys, zp, x_tip, x_heat)
    bx0, bx1 = sorted((x_in, x_tip))
    chan = _ybox(bx0, bx1, ys - socket_bore_dia / 2.0, ys + socket_bore_dia / 2.0,
                 bore_z, zj + lip_len + 1.0)
    return bore.fuse(heat).fuse(chan)


def coupon_dims():
    """Dims for the front-half test-print coupon — a reduced-size box carrying
    every feature (display housing, telescoping lip, the four corner bosses, the
    full-depth ribs) at full size."""
    ix0, ix1 = 0.0, 150.0          # facet 118.5 flush-left, right boss clear
    iy0, iy1 = 0.0, 122.0          # back coupon's depth behind the joint
    iz0, iz1 = 0.0, 110.0
    y_joint = 85.0                 # lip + rear bosses sit behind the housing
    inner = (ix0, ix1, iy0, iy1, iz0, iz1)
    outer = (ix0 - wall, ix1 + wall, iy0 - wall, iy1 + wall, iz0 - wall, iz1 + wall)
    return inner, outer, y_joint, None


def build_front_half(dims=None, split=None):
    inner, outer, y_joint, _ = dims if dims is not None else _dims()
    shell = _shell_with_facet(inner, outer).val()
    front = shell.intersect(_ybox(outer[0], outer[1], outer[2], y_joint, outer[4], outer[5]))
    front = front.fuse(_front_lip(inner, y_joint))
    yb = _y_boss(y_joint)
    bosses = _bosses(inner, split=split)
    for x_in, x_ext, sx, _zb, pod_z, zc, _bz, _by1 in bosses:
        front = front.fuse(_front_pod(x_in, x_ext, sx, pod_z, zc, y_joint, inner))
    # The full-depth pods can poke into the display facet; trim them to its plane.
    front = front.cut(_facet_wedge(outer))
    # Close the facet recess at its +X edge (the −X edge is sealed by the left wall).
    front = front.fuse(_facet_end_wall(inner, outer))
    # Let the display into the facet (bezel counterbore + PCB through-hole); this
    # also clears whatever rib/wall material sits behind the facet in its path.
    front = front.cut(_display_cuts(outer))
    # Punch the hopper funnel throat through the top wall, right of the display.
    front = front.cut(_hopper_cut(inner, outer, y_joint))
    # Front-panel through-holes — the CO2 inlet the DERPIPE threads through.
    # _contents owns the port layout (mirrors the back-wall ports).
    y0, y1 = outer[2] - 5.0, inner[2] + 5.0
    for hole in _contents.front_wall_ports():
        kind, hx, hz = hole[0], hole[1], hole[2]
        if kind == "round":
            front = front.cut(cq.Solid.makeCylinder(hole[3] / 2.0, y1 - y0,
                                                    cq.Vector(hx, y0, hz), cq.Vector(0, 1, 0)))
        else:
            wx, wz = hole[3], hole[4]
            front = front.cut(_ybox(hx - wx / 2.0, hx + wx / 2.0, y0, y1, hz - wz / 2.0, hz + wz / 2.0))
    for x_in, x_ext, sx, z_boss, _pz, _zc, _bz, _by1 in bosses:
        front = front.cut(_front_cuts(x_in, x_ext, sx, z_boss, yb, y_joint))
    # Clip any corner feature that pokes past the rounded print silhouette.
    front = front.intersect(_rounded_outer(outer))
    return cq.Workplane(obj=front)


def build_back_half(dims=None, split=None, brace_y_short=None):
    inner, outer, y_joint, _ = dims if dims is not None else _dims()
    shell = _shell_with_facet(inner, outer).val()
    back = shell.intersect(_ybox(outer[0], outer[1], y_joint, outer[3], outer[4], outer[5]))
    yb = _y_boss(y_joint)
    bosses = _bosses(inner, split=split, brace_y_short=brace_y_short)
    for x_in, x_ext, sx, z_boss, _pz, _zc, _bz, _by1 in bosses:
        back = back.fuse(_back_plug(x_ext, sx, z_boss, yb, y_joint))
    for x_in, x_ext, sx, _zb, _pz, _zc, brace_z, brace_y1 in bosses:
        back = back.fuse(_back_brace(x_in, x_ext, sx, brace_z, brace_y1, y_joint, outer))
    # Clip any corner feature that pokes past the rounded print silhouette.
    back = back.intersect(_rounded_outer(outer))
    for x_in, x_ext, sx, z_boss, _pz, _zc, _bz, _by1 in bosses:
        back = back.cut(_screw_cut(x_ext, sx, z_boss, yb))
    # Panel through-holes for the appliance's external connections — the
    # faucet umbilical (carb-water + two flavor), the tap-water inlet, and
    # the C14 mains inlet, all through the back wall in the band above the
    # cold core; their bodies hang in the band's open rear half. _contents
    # owns the port layout, since it places the contents the band is
    # measured from (../back-panel/README.md).
    y0, y1 = inner[3] - 5.0, outer[3] + 5.0
    for hole in _contents.back_wall_ports():
        kind, hx, hz = hole[0], hole[1], hole[2]
        if kind == "round":
            cutter = cq.Solid.makeCylinder(hole[3] / 2.0, y1 - y0,
                                           cq.Vector(hx, y0, hz), cq.Vector(0, 1, 0))
        else:
            wx, wz = hole[3], hole[4]
            cutter = _ybox(hx - wx / 2.0, hx + wx / 2.0, y0, y1, hz - wz / 2.0, hz + wz / 2.0)
        back = back.cut(cutter)
    return cq.Workplane(obj=back)


def build_piece(y_side, z_side, dims=None, halves_cache=None):
    """One of the four printable pieces: the full front/back column split at
    its own z_joint (front at z_joint_front, back at z_joint_back — the
    staggered seams), the bottom taking the Z lip + socket pods, the top
    taking the D-pins + braces + X-axis screw bores. The Y-seam bosses'
    bottom pair sits under the LOWER seam (the front's), so it lands in — and
    pins — the two bottom pieces."""
    dims = dims if dims is not None else _dims()
    inner, outer, y_joint, cold_front_y = dims
    ox0, ox1, oy0, oy1, oz0, oz1 = outer
    zj = z_joint_front if y_side == "front" else z_joint_back
    short = (cold_front_y - 2.0) if cold_front_y is not None else None
    if halves_cache is not None and y_side in halves_cache:
        half = halves_cache[y_side]
    else:
        half = (build_front_half(dims, split=z_joint_front) if y_side == "front"
                else build_back_half(dims, split=z_joint_front, brace_y_short=short))
        if halves_cache is not None:
            halves_cache[y_side] = half
    solid = half.val()
    stations = [s for s in _z_stations(inner, y_joint)
                if (s[4] == "front") == (y_side == "front")]
    if z_side == "bottom":
        piece = solid.intersect(_ybox(ox0 - 1.0, ox1 + 1.0, oy0 - 1.0, oy1 + 1.0,
                                      oz0 - 1.0, zj))
        col = _ybox(ox0 - 1.0, ox1 + 1.0,
                    oy0 - 1.0 if y_side == "front" else y_joint,
                    y_joint if y_side == "front" else oy1 + 1.0,
                    oz0 - 1.0, oz1 + 1.0)
        piece = piece.fuse(_z_lip(inner, y_joint, zj).intersect(col))
        for x_in, x_ext, sx, ys, c in stations:
            piece = piece.fuse(_z_pod(x_in, x_ext, sx, ys, c, y_joint, inner, zj))
        for x_in, x_ext, sx, ys, _c in stations:
            piece = piece.cut(_z_pod_cuts(x_in, x_ext, sx, ys, zj))
    else:
        piece = solid.intersect(_ybox(ox0 - 1.0, ox1 + 1.0, oy0 - 1.0, oy1 + 1.0,
                                      zj, oz1 + 1.0))
        for x_in, x_ext, sx, ys, c in stations:
            piece = piece.fuse(_z_pin(x_ext, sx, ys, zj))
            piece = piece.fuse(_z_brace(x_in, x_ext, sx, ys, c, inner, outer, zj))
        if y_side == "front":
            # The braces near the facet corner trim to its plane + display cuts.
            piece = piece.cut(_facet_wedge(outer)).cut(_display_cuts(outer))
        for x_in, x_ext, sx, ys, _c in stations:
            piece = piece.cut(_screw_cut(x_ext, sx, _z_pin_z(zj), ys))
    piece = piece.intersect(_rounded_outer(outer))
    return cq.Workplane(obj=piece)


# --- reporting --------------------------------------------------------------

def _report_facet(half):
    a = math.radians(display_facet_angle_deg)
    target = cq.Vector(0.0, -math.sin(a), math.cos(a))
    # The lip's +Z bevel ramp shares this normal; restrict to the facet's region
    # (the front of the part) so only the display facet is measured.
    _i, outer, _y, _c = _dims()
    _a, _n, _o, dy, _dz = _facet_geom(outer)
    y_hi = outer[2] + dy + 5.0
    boxes = []
    for f in half.val().Faces():
        try:
            n = f.normalAt()
        except Exception:
            continue
        if (n - target).Length < 1e-3 and f.Center().y < y_hi:
            boxes.append(f.BoundingBox())
    if not boxes:
        print("  display facet:    NOT FOUND")
        return
    xspan = max(b.xmax for b in boxes) - min(b.xmin for b in boxes)
    slope = (max(b.ymax for b in boxes) - min(b.ymin for b in boxes)) / math.sin(a)
    print(f"  display facet:    {xspan:.1f} mm wide (X) × {slope:.1f} mm slope, solid surface "
          f"(target {display_facet_x:g} × {display_facet_slope:g})")


def _report_split(pieces):
    for name, p in pieces.items():
        b = p.val().BoundingBox()
        fits = b.xlen <= H2C_X + 1 and b.ylen <= H2C_Y + 1 and b.zlen <= H2C_Z + 1
        print(f"  {name + ':':14s} X {b.xlen:5.0f} × Y {b.ylen:5.0f} × Z {b.zlen:5.0f} mm  "
              f"(Y[{b.ymin:.0f},{b.ymax:.0f}] Z[{b.zmin:.0f},{b.zmax:.0f}])  "
              f"H2C bed: {'fits' if fits else 'OVER'}")
    names = list(pieces)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            v = pieces[a].val().intersect(pieces[b].val()).Volume()
            tag = "CLEAR slip-fit" if v < 5 else "INTERFERENCE"
            print(f"  {a} ∩ {b}: {v:.1f} mm³  ({tag})")
    cold = _contents.build()["foam-assembly"][0]
    clash = max(cold.intersect(p.val()).Volume() for p in pieces.values())
    print(f"  cold core vs pieces: {clash:.1f} mm³ max overlap  ({'CLEAR' if clash < 1 else 'CLASH'})")


def main():
    dims = _dims()
    cache = {}
    pieces = {
        "front-bottom": build_piece("front", "bottom", dims, cache),
        "front-top":    build_piece("front", "top", dims, cache),
        "back-bottom":  build_piece("back", "bottom", dims, cache),
        "back-top":     build_piece("back", "top", dims, cache),
    }

    assy = cq.Assembly(name="enclosure")
    piece_colors = {
        "front-bottom": cq.Color(0.80, 0.84, 0.90),
        "front-top":    cq.Color(0.86, 0.89, 0.94),
        "back-bottom":  cq.Color(0.70, 0.74, 0.82),
        "back-top":     cq.Color(0.76, 0.80, 0.87),
    }
    for name, p in pieces.items():
        assy.add(p, name=f"enclosure_{name.replace('-', '_')}", color=piece_colors[name])

    coupon = build_front_half(coupon_dims())
    coupon_back = build_back_half(coupon_dims())

    for name, p in pieces.items():
        export_step(p, str(_here.parent / f"enclosure-{name}.step"))
        print(f"-> enclosure-{name}.step")
    export_assembly(assy, str(_here.parent / "enclosure.step"))
    export_step(coupon, str(_here.parent / "enclosure-front-coupon.step"))
    export_step(coupon_back, str(_here.parent / "enclosure-back-coupon.step"))
    print("-> enclosure.step (assembled pieces)")
    print("-> enclosure-front-coupon.step (test print)")
    print("-> enclosure-back-coupon.step (test print)")
    _report_facet(pieces["front-top"])
    _report_split(pieces)
    for tag, c in (("front coupon", coupon), ("back coupon", coupon_back)):
        b = c.val().BoundingBox()
        print(f"  {tag}:     {b.xlen:.0f}×{b.ylen:.0f}×{b.zlen:.0f} mm, {len(c.val().Solids())} solid")
    cpair = coupon.val().intersect(coupon_back.val()).Volume()
    print(f"  coupon ∩:         {cpair:.1f} mm³  ({'CLEAR slip-fit' if cpair < 5 else 'INTERFERENCE'})")

    variables = {
        "DISPLAY_FACET_X": f"{display_facet_x:.4g} mm",
        "DISPLAY_FACET_SLOPE": f"{display_facet_slope:.4g} mm",
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={"DISPLAY_FACET_X": 2, "DISPLAY_FACET_SLOPE": 2},
    )
    substitute_md(
        _here.parent / "README.md",
        variables=variables,
        expected_counts={"DISPLAY_FACET_X": 1, "DISPLAY_FACET_SLOPE": 1},
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
