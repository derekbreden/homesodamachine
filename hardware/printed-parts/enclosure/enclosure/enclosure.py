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
    corner with a screw clearance through it, its column interlocked with the
    socket's. The
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
    lip rim where posts of the pod's own section carry them to the
    ceiling. Four X-axis screws cross each
    seam (one per side wall per Y column: front pins at the front-wall
    corners, back pins just behind the Y-seam mouth).

The walls stand off the cold core rather than on it — one boss chain at the ±X
walls, one wall at the back — because the core spans the interior wall to wall
and floor to its cap and is what sizes the box, so a wall on its face would leave
the seam machinery nowhere to stand. The core seats flush against the seams
instead, and sits flat on the floor.

Every piece prints on a Z face — the bottom pieces floor-down, the top pieces
ceiling-down, each lying on its closed face with its seam mouth up. So the build
axis is Z, and the anti-warp corner relief goes on the arrises that run along
it: the box's four standing verticals. Each quadrant owns only two of them —
its other two "corners" are the Y-seam, a telescoping mating face with no
exterior arris to relieve — so the front pieces round the front-left/right
verticals, the back pieces the back-left/right, and every seam stays square.
The bosses follow the same axis. Every one stands on a post of its OWN section —
the whole socket footprint, not a stalk under a collar — run the full height of
its piece, bed face to the seam, at CONSTANT section the whole way: a post that
narrows below its boss, or stops short of the wall its neighbour reaches, leaves
exactly the ledge the post was there to avoid. So there is material under every
part of a boss the whole way to the bed and the piece simply stacks; the two
pieces' posts meet at the seam, and the corner doubles as the stiffener a shell
this size wants. Where the seam furniture at one corner belongs to the other
piece — the Y seam's overlap, and the floor and ceiling strata over it — the two
INTERLOCK, each half's column running the other's relief, so both print standing
and assemble solid. Where a wall is crowded the post necks to what is measured
clear there with 45° run-outs, and no boss is placed in that band, since a socket
needs a body to be bored into.

Each seam is pinned at BOTH ends of every piece that crosses it, so nothing can
hinge open at its far end: the Z seams at both ends of their column, and the Y
seam at a level for each end of each piece — which, with two staggered Z seams,
is six levels rather than one pair near the top. Levels are searched per side
wall against what stands against it, so the two walls need not carry the same
ones; main() prints what each ended up with.

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
sys.path.insert(0, str(_repo / "hardware" / "printed-parts" / "zone-c" / "hopper-funnel"))
from _cadq_export import export_step, export_assembly
from docgen import substitute_md, substitute_py_comments
import _contents
import hopper_funnel as _funnel

# Shell parameters.
wall = 3.0                  # PETG wall thickness
interior_clearance = 0.0    # gap between contents bbox and inner wall
# The back wall stands one wall off the rearmost content — the cold core, the
# only thing near the back — so the core seats flush against the rear Z-seam
# lip's inner face rather than against the wall the lip hangs off. Read from
# _contents, which seats the rear panel bodies against the same wall: one number,
# so the wall they mount through and the wall this builds cannot drift apart.
rear_seam_clear = _contents.REAR_STANDOFF
corner_round = 12.          # standing-vertical (Z) print-corner relief radius (anti-warp on the bed)

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
# wall right of the display, cut at the placed funnel's collar: the funnel
# is a static part (../../zone-c/hopper-funnel/, its own frame) placed at
# _contents.FUNNEL_CX/CY with its brim on the box top, and _hopper_hole
# asserts the top-wall frame accommodates it (display gusset left, the
# top-right corner pod, the Y-seam lip band behind, and a front ledge kept
# along the front edge, so a wall frame remains all around for the basin's
# rim flange to rest on).
hopper_front_ledge = 8.0  # top wall kept along the front edge

# Split + boss parameters — every dimension sized to its function, nothing
# inherited from the faucet. The seam is a Y plane; the front half's full-wall
# rear lip telescopes into the back; four corner bosses cross-pin the seam with
# M3 screws from the ±X exterior. Each boss is a round pin registering in the
# front socket bore, meeting the back half's own corner web along its whole +Y
# side. The screw spans the head seat to the front heat-set, so the pin body is
# screw_len − heatset_depth long.
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
# How far a boss stands inboard of the wall it drives through: the whole chain
# of head counterbore, pin body, heat-set and cap, less the wall the counterbore
# is sunk into. This is the socket's section, so it is also its post's.
boss_in = head_cbore_depth + screw_len + socket_cap - wall
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
#   * Front: in the band between the floor stratum and the manifold stack.
#     The compressor and the tipped condenser are each inset one corner-rib
#     chain off their side wall, so the floor's whole height stands clear at
#     both walls; above them the stack runs a few millimetres inboard of each
#     wall — the source tray's east bank, both trays' west outlet elbows, and
#     the pump-inlet tees hanging between them all clear the seam furniture —
#     from its floor at z ~165 up. The seam's wall-hugging lip + boss pods
#     occupy the gap beneath that floor.
# Every printed piece's bed face fits the H2C envelope with these cuts.
z_joint_front = 172.0
# Clear of the cold core's foam cap by the rear station's reach: that station's
# socket collar hangs socket_r below the pin axis, i.e. to z_joint_back − 3.2, so
# the seam sits high enough that the collar lands ON the band above the foam
# rather than in it.
z_joint_back = 267.0
# The Z lip stops this short of the Y-seam overlap on each side, so the two
# telescopes never share a wall surface.
z_lip_y_margin = 2.0
# The manifold stack is inset from both side walls — the source+bag trays sit off
# the −X wall (their west outlet elbows and the junction tees clear it) and the
# nozzle-gate tray off the +X wall (its bare outer ports clear the front Y-lip) —
# so every tray fitting misses the seam furniture (Y-lip / Z-lip / boss pods) at
# both walls. The seam machinery runs unbroken all the way to the corners.


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


def _round_z(solid, r):
    """Round a box solid's four standing-vertical (Z) corner edges by r — the
    print-bed corner relief, about the Z axis the pieces print along. r <= 0
    leaves the corners square (an inset radius can shrink past nothing).

    Each quadrant owns only two of the box's four vertical arrises; its other
    two are the Y-seam, a telescoping mating face with no exterior corner to
    relieve. Rounding the whole box here and letting the Y-split hand each
    piece its share gives front pieces their front-left/right verticals, back
    pieces their back-left/right, and leaves the seam square by construction."""
    if r <= 0:
        return solid
    return cq.Workplane(obj=solid).edges("|Z").fillet(r).val()


def _round_corner_z(solid, xc, yc, r):
    """Round only the single standing-vertical (Z) corner edge of a box at
    (xc, yc) — for a boss that sits in one of the box's rounded verticals and
    must stay concentric with the cavity there. r <= 0 leaves it square."""
    if r <= 0:
        return solid
    wp = cq.Workplane(obj=solid)
    edges = [e for e in wp.edges("|Z").vals()
             if abs(e.Center().x - xc) < 1e-6 and abs(e.Center().y - yc) < 1e-6]
    if not edges:
        return solid          # this boss does not sit in that corner
    return wp.newObject(edges).fillet(r).val()


def _wall_waist(x_in, x_cap, sx, y0, y1):
    """The bite a corner post takes out of itself where the contents crowd its
    wall — a cutter, or None where that wall is clear.

    The manifold stack is the case: the source tray alone runs 272 mm of the
    283 mm interior, so no X position for it leaves a full post section at both
    walls, and the tray it would take to open one is the tray the LLDPE runs are
    routed to. The post necks to what is measured clear over that band instead.

    The transitions are 45°, which is what keeps the post printable either way
    up: descending from a ceiling bed the section narrows into the band (always
    supported) and flares back out below it at 45°; from a floor bed the same in
    reverse. So the boss still has material under it the whole way to the bed —
    just less of it across the band."""
    depth = abs(x_cap - x_in)
    relief = _wall_relief.get(_relief_key(x_in, sx, y0, y1, depth))
    if relief is None:
        return None
    z0, z1, clear = relief
    if clear >= depth:
        return None
    taper = depth - clear                      # 45°: rise equals run
    over = depth + 5.0                         # past the post, so the cut is clean
    pts = [(clear, z0), (clear, z1), (depth, z1 + taper),
           (over, z1 + taper), (over, z0 - taper), (depth, z0 - taper)]
    return (cq.Workplane("XZ", origin=(0.0, y1, 0.0))
            .polyline([(x_in + sx * u, z) for u, z in pts]).close()
            .extrude(y1 - y0).val())


# --- box dimensions, driven by the placed contents -------------------------

# What each ±X wall denies the features standing in its Y-seam corner, measured
# — not tabulated — so it follows the contents instead of drifting from them.
# Filled by _dims() (the one function that reads the placed parts), keyed by the
# footprint and depth probed. `_wall_relief` holds (z0, z1, clear) for necking a
# post; `_wall_block` holds the obstruction itself, for asking whether one
# particular height is usable. A wall with nothing in the way gets no entry.
_wall_relief = {}
_wall_block = {}


def _relief_key(x_in, sx, y0, y1, depth):
    return (round(x_in, 3), sx, round(y0, 3), round(y1, 3), round(depth, 3))


def _measure_wall_relief(placed, inner, y0, y1, depth):
    """For each side wall, probe a Y-seam corner feature's own footprint against
    the placed contents: the z band something reaches into it over, and the clear
    depth left at the wall. Only what stands inside THIS footprint at THIS depth
    counts — a part may cross the wall's height band and still leave the corner
    alone, so a bounding box is not enough to judge it by."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    for x_in, sx in ((ix0, +1.0), (ix1, -1.0)):
        xa, xb = sorted((x_in, x_in + sx * depth))
        prism = _ybox(xa, xb, y0, y1, iz0, iz1)
        hits = [h for h in (prism.intersect(s) for s, _c in placed.values())
                if h.Volume() > 1.0]
        if not hits:
            continue
        key = _relief_key(x_in, sx, y0, y1, depth)
        block = hits[0]
        for h in hits[1:]:
            block = block.fuse(h)
        _wall_block[key] = block
        bbs = [h.BoundingBox() for h in hits]
        reach = min(b.xmin for b in bbs) if sx > 0 else max(b.xmax for b in bbs)
        _wall_relief[key] = (min(b.zmin for b in bbs), max(b.zmax for b in bbs),
                             abs(reach - x_in))


def _plug_reach():
    """How far a cross-pin's body stands inboard of the wall it drives through —
    the depth it must have to register in the socket, so it cannot be necked."""
    return head_cbore_depth + screw_len - heatset_depth - wall


def _y_corner(inner, y_joint):
    """The Y extent of the FRONT half's corner column — the socket pod and the
    post carrying it. Aft it is the lip rim, where the pod's face lands. Forward
    it reaches the Z lip's Y-seam gap, which is exactly where that column's own Z
    station stops: one socket_r ahead of the bore would leave the two standing a
    sliver apart on the same wall, which is neither a post nor a gap anything can
    use.

    One definition, read by the band _dims probes, the heights _bosses may place a
    level at, and the column _front_pod builds — so a change to the corner cannot
    move one of the three and leave the others measuring somewhere else."""
    return (max(inner[2], min(_y_boss(y_joint) - socket_r,
                              y_joint - wall - z_lip_y_margin)),
            y_joint + lip_len)


def _y_corner_back(inner, y_joint):
    """The Y extent of the BACK half's corner column — the web standing in the
    front pod's slot, and the post behind the lip rim. It starts at the bore axis
    (the slot opens there) and runs one pod-depth past the rim."""
    return _y_boss(y_joint), min(inner[3], y_joint + lip_len + 2.0 * socket_r)


def _level_clear(inner, y0, y1, z_boss, x_in, sx, depth):
    """Whether this wall can carry a cross-pin at this height. The test is the
    SOCKET's whole body — bore, heat-set and cap, out to `depth` and one socket_r
    either side of the axis — against the very waist that necks the post, so the
    two cannot disagree: wherever the post is necked, including its 45° run-outs,
    there is no body to bore and so no level. A level whose socket has no body is
    not a fastener, it is a hole in a wall."""
    waist = _wall_waist(x_in, x_in + sx * depth, sx, y0, y1)
    if waist is None:
        return True
    xa, xb = sorted((x_in, x_in + sx * depth))
    probe = _ybox(xa, xb, y0, y1, z_boss - socket_r, z_boss + socket_r)
    return probe.intersect(waist).Volume() <= 1e-6


def _seam_bands_clear(placed, inner):
    """How far aft each part of the Y seam may reach before it meets content:
    (chain, ceiling) — the frontmost thing standing in the ±X boss-chain bands,
    and in the ceiling band the lip's top segment sweeps.

    Those are the only two places the seam occupies. The chain bands are the
    walls' own standoff off the cold core, so they run content-free alongside it;
    the ceiling band rides above everything packed. Measured rather than
    tabulated, so the seam follows the contents instead of drifting from them."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner

    def frontmost(prism):
        limit = iy1
        for s, _c in placed.values():
            hit = prism.intersect(s)
            if hit.Volume() > 1.0:
                limit = min(limit, hit.BoundingBox().ymin)
        return limit

    chain = iy1
    for x_in, sx in ((ix0, +1.0), (ix1, -1.0)):
        xa, xb = sorted((x_in, x_in + sx * boss_in))
        chain = min(chain, frontmost(_ybox(xa, xb, iy0, iy1, iz0, iz1)))
    return chain, frontmost(_ybox(ix0, ix1, iy0, iy1, iz1 - wall, iz1))


def _dims():
    placed = _contents.build()
    bbs = [s.BoundingBox() for s, _c in placed.values()]
    cxmin = min(b.xmin for b in bbs); cxmax = max(b.xmax for b in bbs)
    cymin = min(b.ymin for b in bbs); cymax = max(b.ymax for b in bbs)
    czmin = min(b.zmin for b in bbs); czmax = max(b.zmax for b in bbs)
    # The ±X walls stand one boss chain off the COLD CORE, not against it. The
    # core spans the interior wall to wall and it is what sets the box width, so
    # a wall on its face leaves the seam machinery — corner posts, boss chains,
    # Z-seam pods — nowhere to stand, which is what forced them to thin slivers
    # and denied one wall a fastener height outright. Held off by their own
    # reach, every one of them seats at full section and the core seats flush
    # against them instead of against the wall. Read from _contents, which insets
    # wall-adjacent floor content by the same number.
    cold = placed["foam-assembly"][0].BoundingBox()
    ix0 = min(cxmin - interior_clearance, cold.xmin - _contents.SIDE_RIB_INSET)
    ix1 = max(cxmax + interior_clearance, cold.xmax + _contents.SIDE_RIB_INSET)
    iy0, iy1 = cymin - interior_clearance, cymax + interior_clearance + rear_seam_clear
    # The floor is a fixed Z=0 datum, not the lowest content — so parts can stand
    # on feet above it (the floor, seam lip, and posts stay put). The ceiling
    # follows the tallest content — EXCEPT along the ±X walls, where the
    # Y-seam's top cross-pin pods hug the ceiling and reach one boss chain
    # inboard: content inside that reach sets the ceiling at its top plus the
    # pod stack, so the pods never land on it. What actually fixes the box
    # height is the hopper law below: the funnel's basin is content too.
    iz0 = min(czmin, 0.0) - interior_clearance
    iz1 = czmax + interior_clearance
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
    cold_front_y = cold.ymin
    # The seam sits at the box's middle, for four near-quarter pieces, unless
    # something stands where one of its two parts needs to be: the mouth, plugs,
    # pods and posts in the ±X boss-chain bands, and the lip's ceiling segment
    # in the band under the top wall. The cold core caps neither — the bands run
    # clear alongside it, and the lip carries no floor segment to sweep it — so
    # the seam passes BEHIND the core's front face rather than stopping at it.
    chain_clear, ceiling_clear = _seam_bands_clear(placed, inner)
    chain = lip_len + wall + socket_bore_dia / 2.0 + socket_r
    y_chain = chain_clear - 2.0 - chain
    y_ceiling = ceiling_clear - 2.0 - lip_len
    y_joint = max(facet_back_y + 2.0,
                  min((iy0 + iy1) / 2.0, y_chain, y_ceiling))
    # The rear-panel port field is content too: every clamping nut/flange seats
    # on the outer wall face, so the wall must reach past the field's topmost
    # hardware edge (its bottom edge rides the lip band — _contents
    # UMBILICAL_Z_FLOOR); the margin mirrors that floor's 2 mm stance.
    port_top = max(
        (z + (_contents.PORT_C14_FLANGE_H if kind == "rect" else _contents.PORT_NUT_D) / 2.0
         for kind, _x, z, *_size in _contents.back_wall_ports()),
        default=iz0)
    iz1 = max(iz1, port_top + 2.0)
    inner = (ix0, ix1, iy0, iy1, iz0, iz1)
    outer = (ox0, ox1, oy0, oy1, iz0 - wall, iz1 + wall)
    # The Y-seam corner, probed at each depth something stands there: the front
    # half's column at the socket's full section (which also fixes where a level
    # may sit, since a level needs a socket body), and the back half's column —
    # web through the pod's slot, post behind the rim — at the pin's.
    fy0, fy1 = _y_corner(inner, y_joint)
    _measure_wall_relief(placed, inner, fy0, fy1, boss_in)
    by0, by1 = _y_corner_back(inner, y_joint)
    _measure_wall_relief(placed, inner, by0, by1, _plug_reach())
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
    """The outer box with rounded standing-vertical corners and the facet
    chamfered in — the print silhouette the half is clipped to so nothing
    pokes past it."""
    ox0, ox1, oy0, oy1, oz0, oz1 = outer
    box = _round_z(_ybox(ox0, ox1, oy0, oy1, oz0, oz1), corner_round)
    return box.cut(_facet_wedge(outer))


def _shell_with_facet(inner, outer):
    """Hollow box with the 45° facet as a SOLID `wall`-thick surface: chamfer
    the outer box, and hold the cavity one wall back from the facet plane. The
    standing-vertical corners are relieved for the print bed — outer by
    `corner_round`, cavity one wall less (square once the inset reaches zero)."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    ox0, ox1, oy0, oy1, oz0, oz1 = outer
    a, normal, origin, dy, dz = _facet_geom(outer)
    extent = max(ox1 - ox0, oy1 - oy0, oz1 - oz0) + 100.0

    inner_box = _round_z(_ybox(ix0, ix1, iy0, iy1, iz0, iz1), corner_round - wall)
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
    """Rectangle (x0, x1, y0, y1) of the funnel opening in the top wall: the
    placed funnel's collar — hopper_funnel.py's own dims at
    _contents.FUNNEL_CX/CY. The placement must clear the display end-wall
    gusset (right of the facet), the top-right corner pod's inboard end, and
    the front ledge — asserted, so a bad placement fails the build instead of
    silently deforming the hole. The hole CROSSES the Y-seam (y_joint ducks
    ahead of the manifold's aft elbow columns, under the basin): both top
    pieces take the cut, the top-wall lip/mouth are relieved across the
    funnel span, and the collar bridges the seam; the seam stays pinned by
    the corner bosses west of the hole and the top-wall strip east of it —
    the aft limit is the back piece's rear pod band."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    ox0, ox1, oy0, oy1, oz0, oz1 = outer
    x0 = _contents.FUNNEL_CX - _funnel.collar_w / 2.0
    x1 = _contents.FUNNEL_CX + _funnel.collar_w / 2.0
    y0 = _contents.FUNNEL_CY - _funnel.collar_d / 2.0
    y1 = _contents.FUNNEL_CY + _funnel.collar_d / 2.0
    pod_in = ix1 + wall - (head_cbore_depth + screw_len + socket_cap)
    lims = (ox0 + display_facet_x + wall,              # past the facet gusset
            pod_in - 1.0,                              # clear of the top-right pod
            iy0 + hopper_front_ledge,                  # behind the front ledge
            _contents.FRONT_DEPTH - 2.0)               # ahead of the cold core's band
    tol = 1e-6
    if x0 < lims[0] - tol or x1 > lims[1] + tol or y0 < lims[2] - tol or y1 > lims[3] + tol:
        raise ValueError(
            f"funnel collar (x {x0:.2f}..{x1:.2f}, y {y0:.2f}..{y1:.2f}) violates the "
            f"top-wall frame (x {lims[0]:.2f}..{lims[1]:.2f}, y {lims[2]:.2f}..{lims[3]:.2f})")
    return x0, x1, y0, y1


def _hopper_cut(inner, outer, y_joint):
    """The funnel throat punched clean through the top wall — one wall deeper
    than the ceiling, so the Y-seam's top-wall lip/mouth shelf (hanging one
    wall below it) is relieved across the hole span the seam crosses."""
    x0, x1, y0, y1 = _hopper_hole(inner, outer, y_joint)
    return _ybox(x0, x1, y0, y1, inner[5] - wall - 1.0, outer[5] + 1.0)


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
#   * BACK half = PIN: a round cylinder from the ±X exterior to the heat-set,
#     registering in the socket bore. Sized to the screw SHANK, not the head (the
#     head sits in the wall counterbore); screw-clearance + head counterbore bored
#     in.
#   * FRONT lip = SOCKET: a corner pod, integral with the ±Z wall, bored to
#     receive the round pin (slide fit) with the heat-set + cap at the deep
#     inboard end.
# The head seats in the back wall; the shank crosses the pin body into the front
# heat-set, cross-pinning the two halves along X.
#
# The corner the pair stands in is SHARED, not owned. The overlap belongs to the
# front half — its lip and pod fill the corner floor to ceiling — so a pin
# standing in it has nothing under it on the back piece, and the back's own post
# can only begin behind the rim. The two INTERLOCK instead: a slot the pod's full
# height, and the back half's web filling it. Each piece then carries the corner
# at constant section from its own bed face to every boss on it, and assembled
# the two read as one solid column. The floor and ceiling strata interlock the
# same way, the front post's foot and head coming through a relief in the back's.

def _seam_level(inner, y0, y1, want, away, limit, x_in, sx, depth):
    """A cross-pin level as close to `want` as the side walls allow, searched in
    the `away` direction (−1 below a seam, +1 above its rim) and no further than
    `limit`. The pin wants to be near the end of the piece it pins, but the
    manifold stack denies this wall a socket body over one band, so the level
    slides along the seam to the nearest height that can actually hold one. Each
    wall is searched on its own — the two are independent screws, and a height
    one wall cannot use is no reason to move the other off its seam. Returns
    None where the wall has no usable height at all; main() reports the levels
    each wall ended up with, so an absent one is visible rather than silent."""
    z = want
    while (z - limit) * away <= 0:
        if _level_clear(inner, y0, y1, z, x_in, sx, depth):
            return z
        z += away * 1.0
    return None


def _bosses(inner, splits=(), y_joint=None):
    """Per-boss tuple (x_in, x_ext, sx, z_boss, pod_z): the inner ±X wall face
    the screw passes through, its matching exterior face, sx = +1 (left) / −1
    (right) inboard, the bore-axis height, and the post's z-span.

    The Y seam runs the box's whole height and BOTH columns cross it, so it is
    pinned at a level for each end of each piece that crosses it — which means
    both Z seams count, not just one. `splits` is every Z-seam height; each
    contributes a level just under it and one just over its lip rim, and the
    floor and ceiling close the ends. With the two staggered seams that is six
    levels, and every piece then carries a level at each end of its own span:
    the front pieces meet at the front seam, the back pieces at the back seam,
    and the stagger pairs whichever front and back piece share a height — the
    brick bond. Without a Z seam (the coupon) it is the floor and ceiling only.

    A level sits as near the end it pins as its OWN wall allows — the two walls
    are independent screws, so each is searched separately and they need not
    agree. The manifold stack denies the −X wall a socket body over one band, so
    its levels there slide to the nearest height that can hold one.

    Every level's post spans the box's full height; `build_piece` clips it to the
    piece, so each piece gets a post from its own bed face to its seam and the
    corner reads floor-to-ceiling assembled."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    r = socket_bore_dia / 2.0
    post = (iz0, iz1)
    zt = iz1 - wall - r
    zf = iz0 + wall + r
    fy0, fy1 = _y_corner(inner, y_joint) if y_joint is not None else (0.0, 0.0)
    out = []
    for x_in, sx in ((ix0, +1.0), (ix1, -1.0)):
        if y_joint is None:                      # the coupon: no contents to dodge
            at = lambda want, away, limit: want
        else:
            at = (lambda want, away, limit, x=x_in, s=sx:
                  _seam_level(inner, fy0, fy1, want, away, limit, x, s, boss_in))
        wanted = [(zf, +1.0, zt)]                                  # a wall above the floor
        for sp in sorted(splits):
            wanted.append((sp - wall - r, -1.0, zf))               # just under that Z seam
            wanted.append((sp + lip_len + wall + r, +1.0, zt))     # just over its lip rim
        wanted.append((zt, -1.0, zf))                              # under the ceiling
        levels = []
        for want, away, limit in wanted:
            z = at(want, away, limit)
            # A level shoved this near one already placed is the same fastener
            # twice, with the two collars merged into one blob — drop it and let
            # the wall carry one there.
            if z is None or any(abs(z - k) < 2.0 * socket_r for k in levels):
                continue
            levels.append(z)
        for z_boss in sorted(levels):
            out.append((x_in, x_in - sx * wall, sx, z_boss, post))
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


def _back_plug(x_ext, sx, z_boss, y_boss):
    """BACK pin: a round cylinder from the ±X exterior to the heat-set, where it
    registers in the front socket bore. It needs no tab of its own to reach the
    rim — the corner's web runs the whole height at the tab's own section, so the
    pin meets it at every level and is backed in Y along its full +Y side."""
    _xs, x_tip, _xh, _xc = _boss_x(x_ext, sx)
    return _xcyl(plug_dia / 2.0, y_boss, z_boss, x_ext, x_tip)


def _sides(bosses):
    """The boss tuples reduced to one per ±X wall — for the features a wall
    carries once (its column) rather than once per level (bore, pin)."""
    seen, out = set(), []
    for b in bosses:
        if b[2] not in seen:
            seen.add(b[2])
            out.append(b)
    return out


def _front_pod(x_in, x_ext, sx, pod_z, y_joint, inner):
    """FRONT socket boss and its POST: one column of the socket's own section,
    running the piece's whole height (`pod_z`) — floor to the seam below, seam
    to the ceiling above.

    The section is the socket: in X the side wall to the cap, in Y one socket_r
    ahead of the bore axis back to the rim the plug's tab slides to. Carrying
    exactly that section to the bed face is the point — anything narrower leaves
    the socket cantilevered over open air on the layer it starts, which is the
    overhang that needs print support. With the full section there is material
    under every part of the boss all the way down, so the piece just stacks; and
    the two pieces' posts meet at the seam, so assembled the corner reads one
    column floor to ceiling. It is also the box's corner stiffener, which a
    printed shell this size needs.

    A post standing on the wall face alone would sit inside the Y lip, which is
    already there — the section has to reach inboard of it to be structure at
    all. Bore, heat-set and the corner's slot are cut afterwards."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    _xs, _xt, _xh, x_cap = _boss_x(x_ext, sx)
    xa, xb = sorted((x_in, x_cap))
    za, zb = pod_z
    ya, yb = _y_corner(inner, y_joint)
    post = _ybox(xa, xb, ya, yb, za, zb)
    waist = _wall_waist(x_in, x_cap, sx, ya, yb)
    return post if waist is None else post.cut(waist)


def _socket_slot(x_in, x_ext, sx, y_joint, outer):
    """The +Y slot through the front socket pod — the path the back half's column
    takes as the halves close, and the reason that column can exist at all.

    The overlap band belongs to the front half: its lip and its pod fill the
    corner floor to ceiling, so a back-half pin standing in it has nothing
    beneath it. Running the slot the pod's WHOLE height rather than just the
    pin's gives the back half a channel it can stand a column in, and costs the
    pod only the outboard limb of its section over the aft third of its depth —
    the limb the slot's own occupant restores once the two are together.

    Open at the rim, so it is a slide path and not a pocket. The slip is on the
    −Y face, the one the column registers against."""
    ox0, ox1, oy0, oy1, oz0, oz1 = outer
    _xs, x_tip, _xh, _xc = _boss_x(x_ext, sx)
    xa, xb = sorted((x_in, x_tip))
    return _ybox(xa, xb, _y_boss(y_joint) - split_slip / 2.0, y_joint + lip_len + 1.0,
                 oz0 - 1.0, oz1 + 1.0)


def _front_pod_ends(x_in, x_ext, sx, y_joint, inner, outer, slip=0.0):
    """The front corner post's FOOT and HEAD — its section carried through the
    floor and ceiling strata over the overlap, out to the printed piece's own bed
    face; with `slip`, the relief the back half's floor and ceiling give up to
    receive them.

    The Y lip is three-sided and the shell it hangs off stops at the seam plane,
    so over the overlap the post had nothing under it at the floor and nothing
    over it at the ceiling — printed, its first layer began an overlap's length
    out over open air. These carry it to the bed, and the back half is relieved
    to take them, so both strata read continuous through the corner instead of
    stepping at it.

    Only the boss chain's own width at each wall — the band the cold core stands
    off — so the core still seats on unbroken floor. Open at the seam plane, so
    it is a slide path and not a pocket."""
    _xs, _xt, _xh, x_cap = _boss_x(x_ext, sx)
    xa, xb = sorted((x_in, x_cap + sx * slip))
    ya = y_joint - (1.0 if slip else 0.0)
    yb = y_joint + lip_len + slip
    pad = 1.0 if slip else 0.0
    return (_ybox(xa, xb, ya, yb, outer[4] - pad, inner[4])
            .fuse(_ybox(xa, xb, ya, yb, inner[5], outer[5] + pad)))


def _back_post(x_in, x_ext, sx, y_joint, inner, zj):
    """BACK Y-seam COLUMN: the web standing in the front pod's slot, and the post
    behind the lip rim, as one body — the column the back half's cross-pins stand
    on.

    The post alone starts at the rim, because the overlap ahead of it is the
    front half's. That left every pin cantilevered off the ±X wall over its own
    length of open air: on the back pieces this corner carried no material under
    a boss at all. The WEB is the fix — the pin's own tab section, run the
    piece's whole height through the slot cut for it, so each pin stands on
    material all the way to the bed and the two halves interlock into one solid
    corner once assembled.

    The web reaches back to where the Z lip's Y-seam gap ends, which is as far as
    a full-height column may run before that lip crosses it. The post beyond it
    skips its own column's seam band for exactly that reason — the bottom piece's
    Z lip rises through it — and picks up at the rim, where the top piece's
    material starts anyway."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    _xs, x_tip, _xh, _xc = _boss_x(x_ext, sx)
    xa, xb = sorted((x_in, x_tip))
    ya, yb = _y_corner_back(inner, y_joint)
    web = _ybox(xa, xb, ya, min(yb, y_joint + lip_len + z_lip_y_margin), iz0, iz1)
    ya = y_joint + lip_len
    if zj is None:
        return web.fuse(_ybox(xa, xb, ya, yb, iz0, iz1))
    return (web.fuse(_ybox(xa, xb, ya, yb, iz0, zj))
               .fuse(_ybox(xa, xb, ya, yb, zj + lip_len, iz1)))


def _front_cuts(x_in, x_ext, sx, z_boss, y_boss):
    """Front-socket inner cuts at one level: the bore that receives the plug and
    the heat-set pocket at its deep end. The slide-in path is not here — that is
    the corner's slot, cut once for the whole wall. The slip lives on the +Y
    (slide-in) side: the bore is shifted +slip/2 so its −Y wall registers on the
    plug's −Y face at the mouth, instead of overshooting past the seam. The
    heat-set stays coaxial with the screw at y_boss, in the pod's inboard limb —
    the one the slot leaves standing."""
    _xs, x_tip, x_heat, _xc = _boss_x(x_ext, sx)
    bore = _xcyl(socket_bore_dia / 2.0, y_boss + split_slip / 2.0, z_boss, x_in, x_tip)
    heat = _xcyl(heatset_dia / 2.0, y_boss, z_boss, x_tip, x_heat)
    return bore.fuse(heat)


def _screw_cut(x_ext, sx, z_boss, y_boss):
    """M3 shank clearance from the ±X exterior through the plug to the heat-set,
    plus the SHCS head counterbore at the exterior — the seat one wall outboard
    of the heat-set."""
    _xs, x_tip, _xh, _xc = _boss_x(x_ext, sx)
    shank = _xcyl(screw_clear_dia / 2.0, y_boss, z_boss, x_ext - sx * 1.0, x_tip)
    cbore = _xcyl(head_cbore_dia / 2.0, y_boss, z_boss, x_ext - sx * 1.0, x_ext + sx * head_cbore_depth)
    return shank.fuse(cbore)


def _front_lip(inner, y_joint):
    """The front half's rear lip: a full-`wall` band whose outer face is flush
    with the body's inner wall — one solid with the body, nothing shaved —
    telescoping +Y into the back half and mating its inner wall. It runs one
    `wall` back into the body cavity (the fusion shoulder / telescoping stop) and
    forward over the overlap to the rim. Printed Z-down the side segments are
    vertical bands and the −Y mouth is a vertical face, so it needs no frame
    bevel; corners stay square, concentric with the square seam mouth it
    telescopes into (the box's rounded verticals are at the front/back walls, not
    the seam). The bore stays open its whole length — the fusion shoulder is the
    one-wall overlap where the band meets the body wall (out to y_joint), NOT a
    slab across the seam.

    THREE-SIDED: both side walls and the ceiling, no floor segment — the same
    shape the Z lip takes for the same kind of reason. A floor segment is the one
    part of the seam that spans the box down at content height, and the cold core
    stands on the floor, so carrying one would hold the whole seam ahead of the
    core. Without it the seam is free to sit behind the core's face, and the
    floor meets in a butt joint registered by the cross-pins at the walls. It is
    also the one part of the lip that could never be printed supported: it juts
    one overlap past the body into the space the back piece's own floor fills, so
    nothing may stand under it."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    y0, y1 = y_joint - wall, y_joint + lip_len
    outer = _ybox(ix0, ix1, y0, y1, iz0, iz1)
    inner_box = _ybox(ix0 + wall, ix1 - wall, y0 - 1.0, y1 + 1.0, iz0 - 1.0, iz1 - wall)
    return outer.cut(inner_box)


# Boss Y position — one value feeds the plug AND the socket, so they are
# coaxial by construction. Placed so the plug's −Y face mates the back mouth;
# the derived lip_len then lands the socket pod's +Y face on the lip rim.
def _y_boss(y_joint):
    return y_joint + plug_dia / 2.0


# --- bottom↔top joint: the same telescoping lip + X-axis pins, rotated ------
#
# The BOTTOM pieces carry the lip and the socket pods; the TOP pieces carry
# the D-pins and the posts that carry them from above. The pin axis sits at
# z_pin = z_joint + plug_dia/2 (pin −Z face on the top piece's mouth), the
# pod's +Z face lands on the lip rim at z_joint + lip_len, and the top piece
# slides down over the lip — the pin dropping into the pod's +Z-open channel.


def _z_pin_z(zj):
    return zj + plug_dia / 2.0


def _z_stations(inner, y_joint):
    """X-axis pin stations along the Z seams — TWO per ±X wall per Y column, one
    at each END of that column's seam, so a seam pinned only at one end cannot
    hinge open at the other.

    Front column: the front-wall corner and the aft end of its own lip, just
    ahead of where the Y-seam furniture starts. Back column: just behind the
    Y-seam mouth (where the telescoped front lip stops) and the rear-wall
    corner. Every station stands in the ±X band the walls' standoff opens off
    the cold core, which runs clear the full depth, so none of them has to dodge
    the pack. Each column's stations ride that column's own seam height."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    r = socket_bore_dia / 2.0
    yf = iy0 + wall + r                             # front column, front wall
    yfr = y_joint - wall - z_lip_y_margin - socket_r  # front column, aft end of its lip
    yb = y_joint + lip_len + wall + r               # back column, behind the mouth
    ybr = iy1 - wall - r                            # back column, rear wall
    out = []
    for ys, col in ((yf, "front"), (yfr, "front"), (yb, "back"), (ybr, "back")):
        out.append((ix0, ix0 - wall, +1.0, ys, col))
        out.append((ix1, ix1 + wall, -1.0, ys, col))
    return out


def _z_lip(inner, y_joint, zj):
    """The bottom pieces' seam lip: a full-wall band whose outer faces are
    flush with the body's inner walls, running one wall down into the body
    (the fusion shoulder) and up over the overlap to the rim. The segment
    crossing the Y-seam overlap is dropped, so each piece carries a 3-sided
    lip and the two telescopes never stack on one wall surface.

    Unlike the Y-seam lip, this band is horizontal and telescopes +Z straight
    THROUGH the box's standing-vertical arrises, so its corners are relieved on
    |Z concentric with the cavity it enters — outer one wall in (matching the
    body's rounded inner wall), inner one wall further — or its square corners
    would bite the rounded top-piece wall."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    z0, z1 = zj - wall, zj + lip_len
    outer = _round_z(_ybox(ix0, ix1, iy0, iy1, z0, z1), corner_round - wall)
    cavity = _round_z(_ybox(ix0 + wall, ix1 - wall, iy0 + wall, iy1 - wall, z0 - 1.0, z1 + 1.0),
                      corner_round - 2.0 * wall)
    ring = outer.cut(cavity)
    gap = _ybox(ix0 - 1.0, ix1 + 1.0,
                y_joint - wall - z_lip_y_margin, y_joint + lip_len + z_lip_y_margin,
                z0 - 1.0, z1 + 1.0)
    return ring.cut(gap)


def _z_station_y(inner, y_joint, ys, col):
    """The Y extent a Z station's column occupies. ONE definition for the bottom
    piece's pod and the top piece's post: they are the two halves of a single
    column and a station whose halves disagree reads as a step at the seam, with
    the narrower one hanging over open air on the layer it starts.

    Local to the station, not the column — a Y column carries a station at each
    end, so spanning from the column's end would make one slab of the whole
    depth. The bound only clamps: the front-wall station still reaches the front
    wall, the rear-wall station the rear, and the behind-the-mouth station still
    starts where the Z lip does."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    if col == "front":
        return max(iy0, ys - socket_r), ys + socket_r
    return (max(y_joint + lip_len + z_lip_y_margin, ys - socket_r),
            min(iy1, ys + socket_r))


def _z_pod(x_in, x_ext, sx, ys, col, y_joint, inner, zj):
    """BOTTOM socket pod: the Y-pod rotated — a POST on the ±X wall carrying the
    socket up to the lip rim, sized in Y to the socket it carries. The
    front-column pod runs from the front wall to one socket_r past its bore; the
    back-column pod starts where the lip does, behind the Y-seam overlap.

    It stands on the floor, not on the wall: the bottom pieces print floor-down,
    so a pod that started at the socket would hang the whole height of the piece
    in open air. Running it to iz0 feeds it off the first layer instead."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    _xs, _xt, _xh, x_cap = _boss_x(x_ext, sx)
    xa, xb = sorted((x_in, x_cap))
    zb = zj + lip_len
    ya, yb = _z_station_y(inner, y_joint, ys, col)
    # The collar around the socket, and the POST carrying it to the floor at the
    # collar's own section — so there is material under every part of the boss
    # the whole way down and the piece just stacks. The post stops where the
    # collar starts, so it stays wholly below the seam: only the collar crosses
    # into the top piece, and only the collar needs the corner relief.
    collar_lo = _z_pin_z(zj) - socket_r
    collar = _ybox(xa, xb, ya, yb, collar_lo, zb)
    # A station that abuts a wall sits in one of the box's rounded verticals;
    # relieve the collar's corner there concentric with the cavity (one wall in)
    # so its +Z reach telescopes into the top piece instead of biting its wall.
    # The front-wall station lands on iy0, the rear-wall station on iy1.
    if abs(ya - iy0) < 1e-6:
        collar = _round_corner_z(collar, x_in, iy0, corner_round - wall)
    if abs(yb - iy1) < 1e-6:
        collar = _round_corner_z(collar, x_in, iy1, corner_round - wall)
    # The post runs the collar's own footprint the whole way down, the rear
    # station included: the side walls stand one boss chain off the cold core, so
    # the corner it drops through is clear of the core at every height.
    return collar.fuse(_ybox(xa, xb, ya, yb, iz0, collar_lo))


def _z_pin(x_ext, sx, ys, zj):
    """TOP D-pin: a round cylinder from the ±X exterior to the heat-set, fused
    to a flat tab rising +Z to the lip rim, where the top piece's post takes
    over. The tab is the pin diameter wide and slides down the socket's +Z
    channel as the pieces close."""
    _xs, x_tip, _xh, _xc = _boss_x(x_ext, sx)
    zp = _z_pin_z(zj)
    cyl = _xcyl(plug_dia / 2.0, ys, zp, x_ext, x_tip)
    xa, xb = sorted((x_ext, x_tip))
    tab = _ybox(xa, xb, ys - plug_dia / 2.0, ys + plug_dia / 2.0,
                zp, zj + lip_len)
    return cyl.fuse(tab)


def _z_post(x_in, x_ext, sx, ys, col, y_joint, inner, outer, zj):
    """TOP post: the column over each pin, from the lip rim up to the ceiling —
    the same station's pod, upside down — the POD's section, not the pin's,
    because the two are one column across the seam and a column that steps at
    the joint leaves the wider half's shoulders standing on nothing. Printed
    ceiling-down it runs from the bed to the seam at constant section, so it
    carries the pin under it with no overhang of its own."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    ox0, ox1, oy0, oy1, oz0, oz1 = outer
    _xs, _xt, _xh, x_cap = _boss_x(x_ext, sx)
    xa, xb = sorted((x_in, x_cap))
    ya, yb = _z_station_y(inner, y_joint, ys, col)
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


def build_front_half(dims=None, splits=(), hopper=True):
    """`hopper=False` skips the funnel opening — the coupon's reduced box does
    not host the funnel, and the placed collar would not fit its frame."""
    inner, outer, y_joint, _ = dims if dims is not None else _dims()
    shell = _shell_with_facet(inner, outer).val()
    front = shell.intersect(_ybox(outer[0], outer[1], outer[2], y_joint, outer[4], outer[5]))
    front = front.fuse(_front_lip(inner, y_joint))
    yb = _y_boss(y_joint)
    bosses = _bosses(inner, splits=splits, y_joint=y_joint)
    # One post per side wall, not per level: every level on a wall shares the
    # same column, and the levels are just where it is bored.
    for x_in, x_ext, sx, _zb, pod_z in _sides(bosses):
        front = front.fuse(_front_pod(x_in, x_ext, sx, pod_z, y_joint, inner))
        front = front.fuse(_front_pod_ends(x_in, x_ext, sx, y_joint, inner, outer))
    # The full-depth pods can poke into the display facet; trim them to its plane.
    front = front.cut(_facet_wedge(outer))
    # Close the facet recess at its +X edge (the −X edge is sealed by the left wall).
    front = front.fuse(_facet_end_wall(inner, outer))
    # Let the display into the facet (bezel counterbore + PCB through-hole); this
    # also clears whatever rib/wall material sits behind the facet in its path.
    front = front.cut(_display_cuts(outer))
    # Punch the hopper funnel throat through the top wall, right of the display.
    if hopper:
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
    for x_in, x_ext, sx, z_boss, _pz in bosses:
        front = front.cut(_front_cuts(x_in, x_ext, sx, z_boss, yb))
    # The slide-in path is the corner's, not the level's: one full-height slot per
    # wall, so the back half's column has somewhere to stand at every height. Cut
    # last, so it takes its share of the foot and head too.
    for x_in, x_ext, sx, _zb, _pz in _sides(bosses):
        front = front.cut(_socket_slot(x_in, x_ext, sx, y_joint, outer))
    # Clip any corner feature that pokes past the rounded print silhouette.
    front = front.intersect(_rounded_outer(outer))
    return cq.Workplane(obj=front)


def build_back_half(dims=None, splits=(), hopper=True):
    """`hopper=False` skips the funnel opening (the coupon's reduced box).
    The opening crosses the Y-seam, so the back half takes its share of the
    cut — the collar bridges the seam."""
    inner, outer, y_joint, _ = dims if dims is not None else _dims()
    shell = _shell_with_facet(inner, outer).val()
    back = shell.intersect(_ybox(outer[0], outer[1], y_joint, outer[3], outer[4], outer[5]))
    if hopper:
        back = back.cut(_hopper_cut(inner, outer, y_joint))
    yb = _y_boss(y_joint)
    bosses = _bosses(inner, splits=splits, y_joint=y_joint)
    # The back half is the back column, so its own seam is the one its post
    # steps around.
    zj = z_joint_back if splits else None
    # The front post's foot and head come through the floor and ceiling here, so
    # this half stands out of their way — everywhere but the slot, which is this
    # half's own column and stays.
    for x_in, x_ext, sx, _zb, _pz in _sides(bosses):
        relief = _front_pod_ends(x_in, x_ext, sx, y_joint, inner, outer,
                                 slip=split_slip / 2.0)
        back = back.cut(relief.cut(_socket_slot(x_in, x_ext, sx, y_joint, outer)))
    for x_in, x_ext, sx, _zb, _pz in _sides(bosses):
        back = back.fuse(_back_post(x_in, x_ext, sx, y_joint, inner, zj))
    for x_in, x_ext, sx, z_boss, _pz in bosses:
        back = back.fuse(_back_plug(x_ext, sx, z_boss, yb))
    # The column and the pins stand in the same corner, so the manifold's bite
    # comes out of that corner as a whole, once both are on.
    for x_in, x_ext, sx, _zb, _pz in _sides(bosses):
        _xs, x_tip, _xh, _xc = _boss_x(x_ext, sx)
        waist = _wall_waist(x_in, x_tip, sx, *_y_corner_back(inner, y_joint))
        if waist is not None:
            back = back.cut(waist)
    # Clip any corner feature that pokes past the rounded print silhouette.
    back = back.intersect(_rounded_outer(outer))
    for x_in, x_ext, sx, z_boss, _pz in bosses:
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
    taking the D-pins + posts + X-axis screw bores. The Y-seam bosses'
    bottom pair sits under the LOWER seam (the front's), so it lands in — and
    pins — the two bottom pieces."""
    dims = dims if dims is not None else _dims()
    inner, outer, y_joint, cold_front_y = dims
    ox0, ox1, oy0, oy1, oz0, oz1 = outer
    zj = z_joint_front if y_side == "front" else z_joint_back
    if halves_cache is not None and y_side in halves_cache:
        half = halves_cache[y_side]
    else:
        splits = (z_joint_front, z_joint_back)
        half = (build_front_half(dims, splits=splits) if y_side == "front"
                else build_back_half(dims, splits=splits))
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
            piece = piece.fuse(_z_post(x_in, x_ext, sx, ys, c, y_joint, inner, outer, zj))
        if y_side == "front":
            # The posts near the facet corner trim to its plane + display cuts.
            piece = piece.cut(_facet_wedge(outer)).cut(_display_cuts(outer))
        for x_in, x_ext, sx, ys, _c in stations:
            piece = piece.cut(_screw_cut(x_ext, sx, _z_pin_z(zj), ys))
    piece = piece.intersect(_rounded_outer(outer))
    return cq.Workplane(obj=piece)


# --- reporting --------------------------------------------------------------

def _report_facet(half):
    a = math.radians(display_facet_angle_deg)
    target = cq.Vector(0.0, -math.sin(a), math.cos(a))
    # The lip's +Z bevel ramp shares this normal (excluded by the front-region
    # y filter) and the pod's east shoulder shares it one wall lower (excluded
    # by the on-plane filter) — only the display facet itself is measured.
    _i, outer, _y, _c = _dims()
    _a, _n, origin, dy, _dz = _facet_geom(outer)
    y_hi = outer[2] + dy + 5.0
    boxes = []
    for f in half.val().Faces():
        try:
            n = f.normalAt()
        except Exception:
            continue
        c = f.Center()
        off = (c - cq.Vector(*origin)).dot(target)
        if (n - target).Length < 1e-3 and c.y < y_hi and abs(off) < 1e-3:
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


def _report_levels(dims):
    """The Y-seam cross-pin heights each ±X wall ended up with. They are searched
    per wall against what stands against it, so the two can differ — printing
    them keeps a wall that had to give up a level visible instead of silent."""
    inner, _outer, y_joint, _cf = dims
    bosses = _bosses(inner, splits=(z_joint_front, z_joint_back), y_joint=y_joint)
    for sx, label in ((+1.0, "−X"), (-1.0, "+X")):
        zs = sorted(b[3] for b in bosses if b[2] == sx)
        print(f"  Y-seam levels {label} wall: {len(zs)} — "
              + ", ".join(f"{z:.0f}" for z in zs))


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

    coupon = build_front_half(coupon_dims(), hopper=False)
    coupon_back = build_back_half(coupon_dims(), hopper=False)

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
    _report_levels(dims)
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
