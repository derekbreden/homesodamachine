"""Kitchen Edition enclosure — a PETG box sized to the placed contents, split
into two printable halves (front + back) that telescope and cross-pin together.

Dimensions follow the contents at build time: the bounding box of the parts
placed by `../enclosure-assembly/_contents.py` is computed live, padded by an
interior clearance, then walled out. Features:

  * A flat 45° display-mounting facet (a solid surface) chamfered into the
    top-front-left corner, flush to the −X edge.
  * A front↔back split: the front half's rear wall telescopes (a full-wall
    lip, nothing shaved) into the back half, and four interlocking screw
    bosses cross the seam — one in each top/bottom corner, on the ±X (left /
    right) side walls. Each boss is on an X axis: the screw drives in from the
    left/right EXTERIOR face, and the boss is tucked into the corner so it is
    part of the top/bottom (±Z) wall. The BACK half carries the PLUG (faucet
    mounting-plate idiom): a cylinder reaching inward from the corner with a
    screw clearance through it — no web tail. The FRONT half's lip carries the
    SOCKET (faucet shell-bottom idiom): a pod bored to receive the plug, open
    on its +Y face so the plug drops in as the halves close, with a ruthex M3
    heat-set at the deep end. An M3 SHCS from the ±X exterior passes through the
    plug into the heat-set, cross-pinning the two halves. The back half is
    sized so the cold core seats behind the bosses, clear.

main() exports the two printable halves (enclosure-front.step,
enclosure-back.step) plus enclosure.step — the two halves as separate solids
in assembled position, seams intact (mirrors `touch_flo_shell.py`).
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
corner_round = 12.0         # vertical (Y) print-corner relief, matching the foam
                            # shell's outer corner radius (anti-warp on the bed)

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

# Split + boss parameters — every dimension sized to its function, nothing
# inherited from the faucet. The seam is a Y plane; the front half's full-wall
# rear lip telescopes into the back; four corner bosses cross-pin the seam with
# M3 screws from the ±X exterior. Each boss is a D-section pin: round where it
# registers in the front socket bore, with a flat tab running +Y to the lip rim
# where the back-half corner brace backs it. The screw spans the head seat to the
# front heat-set, so the pin body is screw_len − heatset_depth long.
boss_to_coldcore = 14.0      # clear gap from the lip's +Y tip back to the cold core
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
    corner relief, about the Y axis the halves print along."""
    return cq.Workplane(obj=solid).edges("|Y").fillet(r).val()


def _round_corner_y(solid, xc, zc, r):
    """Round only the single vertical (Y) corner edge of a box at (xc, zc)."""
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
    # still follows the tallest content.
    iz0 = min(czmin, 0.0) - interior_clearance
    iz1 = czmax + interior_clearance
    ox0, ox1 = ix0 - wall, ix1 + wall
    oy0, oy1 = iy0 - wall, iy1 + wall
    oz0, oz1 = iz0 - wall, iz1 + wall
    # Split plane: as far forward as the print allows — just behind the display
    # housing, so the whole facet stays in the front half. The floor parts are
    # raised clear of the seam lip, so nothing on the floor limits it.
    inner = (ix0, ix1, iy0, iy1, iz0, iz1)
    outer = (ox0, ox1, oy0, oy1, oz0, oz1)
    _fa, _fn, _fo, _fdy, _fdz = _facet_geom(outer)
    facet_back_y = oy0 + _fdy + display_facet_thickness * math.sqrt(2.0)
    y_joint = facet_back_y + 2.0
    cold_front_y = placed["foam-shell"][0].BoundingBox().ymin
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
    vertical corners round concentrically — outer `corner_round`, cavity one wall
    inboard — so the wall is preserved around the print-bed corner relief."""
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

def _bosses(inner):
    """Per-boss tuple (x_in, x_ext, sx, z_boss, sz): the inner ±X wall face the
    screw passes through, its matching exterior face, sx = +1 (left) / −1
    (right) inboard, the bore-axis height (bottom one wall above the floor, top
    one wall below the ceiling), and sz = +1 (bottom) / −1 (top) for the ±Z
    wall the boss is integral with."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    zb = iz0 + wall + socket_bore_dia / 2.0   # bottom
    zt = iz1 - wall - socket_bore_dia / 2.0   # top
    return [
        (ix0, ix0 - wall, +1.0, zb, +1.0),  # bottom-left
        (ix1, ix1 + wall, -1.0, zb, +1.0),  # bottom-right
        (ix0, ix0 - wall, +1.0, zt, -1.0),  # top-left
        (ix1, ix1 + wall, -1.0, zt, -1.0),  # top-right
    ]


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


def _front_pod(x_in, x_ext, sx, z_boss, sz, y_joint, inner):
    """FRONT socket pod (solid): a corner rib bounded by the faces it mates — in
    Y from the front wall's inner face (iy0) all the way to the rim, in X the
    side wall to the cap, in Z the bore out to the floor/ceiling. Running full
    depth to the front wall, it has no −Y overhang when the front half prints
    −Y-down — it grows straight up from the wall. Bore / heat-set / channel are
    cut afterwards; the facet trims the top-front-left pod back to its plane."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    _xs, _xt, _xh, x_cap = _boss_x(x_ext, sx)
    xa, xb = sorted((x_in, x_cap))
    za, zb = (iz0, z_boss + socket_r) if sz > 0 else (z_boss - socket_r, iz1)
    # Round the outer corner (the one at the side wall) concentric with the
    # cavity, one wall in, so the pod's telescoping reach fits the back's rounded
    # corner instead of fouling it.
    zc = iz0 if sz > 0 else iz1
    return _round_corner_y(_ybox(xa, xb, iy0, y_joint + lip_len, za, zb),
                           x_in, zc, corner_round - wall)


def _back_brace(x_in, x_ext, sx, z_boss, sz, y_joint, outer, inner):
    """BACK corner brace (solid): a corner rib in each top/bottom corner of the
    ±X side walls, running the back half's free Y length — from the lip rim (where
    the telescoped front lip + sockets stop, so it never fouls them) to the rear
    wall. Sized to the pin it backs (in X to the pin's inboard end, in Z to the
    pin — no further toward centre) and butting the pin's flat tab at the rim, so
    it supports the X-axis pin in Y and anchors the corner against peeling."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    ox0, ox1, oy0, oy1, oz0, oz1 = outer
    _xs, x_tip, _xh, _xc = _boss_x(x_ext, sx)
    xa, xb = sorted((x_in, x_tip))
    za, zb = (iz0, z_boss + plug_dia / 2.0) if sz > 0 else (z_boss - plug_dia / 2.0, iz1)
    return _ybox(xa, xb, y_joint + lip_len, oy1, za, zb)


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


def build_front_half(dims=None):
    inner, outer, y_joint, _ = dims if dims is not None else _dims()
    shell = _shell_with_facet(inner, outer).val()
    front = shell.intersect(_ybox(outer[0], outer[1], outer[2], y_joint, outer[4], outer[5]))
    front = front.fuse(_front_lip(inner, y_joint))
    yb = _y_boss(y_joint)
    for x_in, x_ext, sx, z_boss, sz in _bosses(inner):
        front = front.fuse(_front_pod(x_in, x_ext, sx, z_boss, sz, y_joint, inner))
    # The full-depth pods can poke into the display facet; trim them to its plane.
    front = front.cut(_facet_wedge(outer))
    # Close the facet recess at its +X edge (the −X edge is sealed by the left wall).
    front = front.fuse(_facet_end_wall(inner, outer))
    # Let the display into the facet (bezel counterbore + PCB through-hole); this
    # also clears whatever rib/wall material sits behind the facet in its path.
    front = front.cut(_display_cuts(outer))
    for x_in, x_ext, sx, z_boss, _sz in _bosses(inner):
        front = front.cut(_front_cuts(x_in, x_ext, sx, z_boss, yb, y_joint))
    # Clip any corner feature that pokes past the rounded print silhouette.
    front = front.intersect(_rounded_outer(outer))
    return cq.Workplane(obj=front)


def build_back_half(dims=None):
    inner, outer, y_joint, _ = dims if dims is not None else _dims()
    shell = _shell_with_facet(inner, outer).val()
    back = shell.intersect(_ybox(outer[0], outer[1], y_joint, outer[3], outer[4], outer[5]))
    yb = _y_boss(y_joint)
    for x_in, x_ext, sx, z_boss, _sz in _bosses(inner):
        back = back.fuse(_back_plug(x_ext, sx, z_boss, yb, y_joint))
    for x_in, x_ext, sx, z_boss, sz in _bosses(inner):
        back = back.fuse(_back_brace(x_in, x_ext, sx, z_boss, sz, y_joint, outer, inner))
    # Clip any corner feature that pokes past the rounded print silhouette.
    back = back.intersect(_rounded_outer(outer))
    for x_in, x_ext, sx, z_boss, _sz in _bosses(inner):
        back = back.cut(_screw_cut(x_ext, sx, z_boss, yb))
    return cq.Workplane(obj=back)


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


def _report_split(front, back):
    fb = front.val().BoundingBox()
    bb = back.val().BoundingBox()
    print(f"  front half:       Y[{fb.ymin:.0f}, {fb.ymax:.0f}] = {fb.ylen:.0f} mm  "
          f"({fb.xlen:.0f}×{fb.zlen:.0f} face)")
    print(f"  back half:        Y[{bb.ymin:.0f}, {bb.ymax:.0f}] = {bb.ylen:.0f} mm  "
          f"({bb.xlen:.0f}×{bb.zlen:.0f} face)")
    for tag, h in (("front", front), ("back", back)):
        b = h.val().BoundingBox()
        fits = b.xlen <= H2C_X + 1 and b.ylen <= H2C_Y + 1 and b.zlen <= H2C_Z + 1
        print(f"  {tag} fits H2C bed: {fits}")
    overlap = front.val().intersect(back.val()).Volume()
    print(f"  front ∩ back:     {overlap:.1f} mm³  ({'CLEAR slip-fit' if overlap < 5 else 'INTERFERENCE'})")
    inner, _o, y_joint, _c = _dims()
    yb = _y_boss(y_joint)
    cold = _contents.build()["foam-shell"][0]
    clash = sum(
        cold.intersect(
            _back_plug(x_ext, sx, z_boss, yb, y_joint).fuse(
                _front_pod(x_in, x_ext, sx, z_boss, sz, y_joint, inner))
        ).Volume()
        for x_in, x_ext, sx, z_boss, sz in _bosses(inner)
    )
    print(f"  cold core vs bosses: {clash:.1f} mm³ overlap  ({'CLEAR' if clash < 1 else 'CLASH'})")


def main():
    front = build_front_half()
    back = build_back_half()

    assy = cq.Assembly(name="enclosure")
    assy.add(front, name="enclosure_front", color=cq.Color(0.80, 0.84, 0.90))
    assy.add(back, name="enclosure_back", color=cq.Color(0.70, 0.74, 0.82))

    coupon = build_front_half(coupon_dims())
    coupon_back = build_back_half(coupon_dims())

    export_step(front, str(_here.parent / "enclosure-front.step"))
    export_step(back, str(_here.parent / "enclosure-back.step"))
    export_assembly(assy, str(_here.parent / "enclosure.step"))
    export_step(coupon, str(_here.parent / "enclosure-front-coupon.step"))
    export_step(coupon_back, str(_here.parent / "enclosure-back-coupon.step"))
    print("-> enclosure-front.step")
    print("-> enclosure-back.step")
    print("-> enclosure.step (assembled halves)")
    print("-> enclosure-front-coupon.step (test print)")
    print("-> enclosure-back-coupon.step (test print)")
    _report_facet(front)
    _report_split(front, back)
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
