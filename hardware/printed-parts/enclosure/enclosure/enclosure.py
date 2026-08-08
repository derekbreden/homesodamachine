"""Thin Edition enclosure — a tall, narrow PETG box, split into four printable
pieces (front/back × bottom/top) that telescope and cross-pin together.

WIDTH, HEIGHT and DEPTH are all BOUNDS, not consequences — `appliance_width` struck
symmetric about x = 0, `appliance_height` from the floor slab's underside to the top
wall's outer face, and `rear_plane_y` from the front wall to the back. The contents do
not set them; they have to fit inside, and `_dims` measures every one of them against
the pack and enters the reading in `BOUNDS`. The box comes out at its stated size
either way, so a pack that overran it gets a wall drawn through it.

Three bodies stand on the floor slab — the compressor and the condenser side by side
across the front, and the cold core behind them — and each is held one `side_rib_inset`
off the ±X walls, so the corner posts, boss chains and Z-seam pods all seat at full
section and the body seats against them rather than against the wall. The cold core is
the widest of the three even yawed a quarter turn (`front_half.FOAM_YAW`), which is what
puts its 181 mm short face across the machine instead of its 283 mm long one. The pack
is placed by `../../../manifold-layout/front_half.py`. Features:

  * A flat 45° display-mounting facet (a solid surface) chamfered into the
    top-front arris across the box's FULL WIDTH, with the display's glass
    centred on it and flat facet either side. That corner cannot be packed
    anyway, and a chamfer that runs wall to wall needs no end wall, no shoulder
    and no shoulder relief.
  * A front↔back split at the stated `y_seam`, so its machinery is aft of the
    front pack and a front-quadrant tray never has to be notched around it:
    the front pieces' rear walls telescope (a full-wall lip,
    nothing shaved) into the back pieces — a proud tongue on the side walls and
    ceiling, and on the floor, where the cold core rides the cavity side and a
    proud tongue cannot, a shiplap within the slab (`_floor_lap`), so every seam
    laps and none butts — and four interlocking screw
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

The walls stand off the bodies rather than on them — one boss chain at the ±X
walls, one wall at the back — because a body on the floor spans the interior wall
to wall, so a wall on its face would leave the seam machinery nowhere to stand.
The cold core seats flush against the seams instead, and stands flat on the floor slab — its bottom cap's lid is a plane and
every cap screw is down in a counterbore, so nothing goes under it. The ±X bands'
own seam posts fence it sideways, the back Z seam's lip behind, and the floor's
two core lugs (`_core_fence`) ahead. The floor those posts and that core stand on
is flat: the Y seam's floor overlap is a shiplap within the slab, not a proud
tongue.

Every piece prints on a Z face — the bottom pieces floor-down, the top pieces
ceiling-down, each lying on its closed face with its seam mouth up. So the build
axis is Z, and the anti-warp corner relief goes on the arrises that run along
it: the box's four standing verticals. Each quadrant owns only two of them —
its other two "corners" are the Y-seam, a telescoping mating face with no
exterior arris to relieve — so the front pieces round the front-left/right
verticals, the back pieces the back-left/right, and every seam stays square.
The full-width facet raises no new standing vertical: it ends on the ±X
exterior walls, which are already relieved, so the chamfer runs out into their
own rounds.
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
seams intact (mirrors `touch_flo_shell.py`). It exports the same five files
again for the test-print COUPON (enclosure-coupon-*.step): the smallest box
that still carries the display housing and all three seams with their full
ladder of cross-pins, every one of them at full size — the whole four-piece
assembly, printable in an evening, to prove the fit before the real box is
committed. Both come through the same code from a `Box`.
"""

import math
import sys
from collections import namedtuple
from pathlib import Path

import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
# _repo is this EDITION's root; tools/ is shared machinery with one copy at the
# repo root, so it gets its own anchor rather than a tools/ per edition.
_tools = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"
sys.path.insert(0, str(_repo / "hardware" / "scripts"))
sys.path.insert(0, str(_tools))
sys.path.insert(0, str(_repo / "hardware" / "printed-parts" / "zone-c" / "hopper-funnel"))
from _cadq_export import export_step, export_assembly
from docgen import substitute_md, substitute_py_comments
import _boxes
import hopper_funnel as _funnel

# Shell parameters.
wall = 3.0                  # PETG wall thickness
interior_clearance = 0.0    # gap between contents bbox and inner wall
# The back wall stands one wall off the rearmost content — the cold core, the
# only thing near the back — so the core seats flush against the rear Z-seam
# lip's inner face rather than against the wall the lip hangs off. A body mounted
# on the back wall seats on this same plane.
rear_seam_clear = 3.0
# The same standoff at the front, so the front column's Z lip keeps a full-width
# front segment behind the refrigeration stratum instead of giving it up.
front_seam_clear = 3.0
# What the ±X walls stand off the widest body on the floor: one boss chain, so the
# corner posts, boss chains and Z-seam pods all seat at full section and the body
# seats flush against them instead of against the wall. Floor content set against a
# side wall is inset the same, to clear the ribs.
side_rib_inset = 14.0
corner_round = 12.          # standing-vertical (Z) print-corner relief radius (anti-warp on the bed)

# H2C left-nozzle build envelope; each printed HALF must fit inside this.
H2C_X, H2C_Y, H2C_Z = 325.0, 320.0, 320.0

# Display-mounting facet — a flat 45° SOLID surface chamfered into the top-front
# arris for the Waveshare ESP32-S3-Touch-LCD-4.3B config display
# (../../../reference/waveshare-43b-display/), facing up-and-forward (−Y front /
# +Z up) toward the standing user.
#
# The facet runs the box's FULL WIDTH, wall to wall, and the display is CENTRED on
# it: the machine is 215 mm wide and the glass 113.5, so what is left is
# ~47 mm of flat 45° face either side of it. That corner is unpackable at any width
# — the chamfer is inside the box's own silhouette — so spending all of it buys a
# face that reads square from the front, and the geometry gets simpler for it: no
# end wall closing a recess, no shoulder where a window stops, no bed relief on the
# arris a shoulder would raise. The window's lateral size is therefore the box's,
# not a parameter; `display_facet_x` remains the glass + a 3 mm buffer all around —
# [119.5 mm](DISPLAY_FACET_X) × [83 mm](DISPLAY_FACET_SLOPE) up the slope — which is
# what the COUPON is sized to carry and what `_report_facet` prints beside the
# measured face.
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

# Hopper funnel opening (Zone C) — one rectangular opening through the top wall
# BEHIND the display facet, cut at the placed funnel's collar: the funnel is a
# static part (../../zone-c/hopper-funnel/, its own frame) placed at
# the pack's own `funnel` centre with its brim on the box top, and _hopper_hole
# measures the top-wall frame against it (the facet's back plane ahead, the
# ±X top corner pods either side, the back wall behind). The funnel is pushed as
# far forward as that frame allows and reaches aft for its capacity, so it may
# CROSS the Y seam — both halves take their share of the cut.
hopper_front_ledge = 6.0  # top wall kept between the facet's back plane and the throat —
                          # the whole of what stands between the two, since the wall forward
                          # of it thickens into the housing rather than running out to an edge

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
# The C14's two bosses. Its insert enters from the wall's INNER face, so what stands proud
# outboard is the length of insert the wall itself cannot hold, plus the cap over its blind
# end. One wall of material around the bore is the section.
c14_boss_dia = heatset_dia + 2.0 * wall
c14_boss_proud = heatset_depth - wall + socket_cap
# The ±X walls' own mounting bosses — what a body hung on a side wall is fastened by. Each
# stands off the wall's INNER face and reaches inboard to the body's own mounting plane,
# bored for a ruthex M3 short from that end; the screw comes the other way, in through the
# body from the room, so nothing is driven from outside the machine.
#
# The section is the one `printed-parts/electronics/module_tray` gives every M3 board boss in
# this machine, and it is not the C14's: these land on a board's own hole pattern, between its
# pin fields, and a boss that carried a whole wall around its insert would foul them.
mount_boss_dia = 7.0
# Air past the screw tip at the bore's blind end, so a screw longer than the insert has
# somewhere to go rather than bottoming on printed material.
mount_bore_relief = 1.0
# How far one of those bosses stands OFF the wall's inner face — which is the standoff a body
# hung on the flank gets, and every millimetre of it is insert: the bore runs the boss's whole
# length and stops on the wall's own inner face, so the wall behind is what caps its blind end.
# Nothing here is spent holding the body away from the wall. That is the point — a body bolted
# to a wall wants to be ON it, and this is the shortest column an M3 heat-set can live in.
mount_boss_out = heatset_depth + mount_bore_relief
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

# The appliance's stated HEIGHT — floor slab's underside (z = −wall) to the top
# wall's outer face. It is the machine's silhouette, the one dimension a counter
# appliance is judged by before it is opened, and this is the number the thin machine
# is FOR. The contents live under it; `_dims` measures whether they do (`box-height`).
appliance_height = 358.0
# The stated WIDTH — ±X outer faces, struck symmetric about x = 0, which is the axis
# the whole pack is centred on. A body that leaves the floor, or a narrower one taking
# its place, does not make the machine narrower; a pack that outgrows this is a red
# `box-width`. The ±X walls still stand one `side_rib_inset` off the widest body on the
# floor — that is what the check measures, rather than what the wall follows.
appliance_width = 223.0


def interior_x():
    """The ±X interior faces, struck off the stated width alone. `_dims` builds the box on
    these and every body seated on a flank reads them through the same call, so the wall and
    the things that stand against it cannot come apart."""
    return (-(appliance_width / 2.0 - wall), appliance_width / 2.0 - wall)
# The interior REAR PLANE — the inner face of the back wall, stated the same way. A
# component dragged forward inside the machine does not make the machine shallower,
# a pack that outgrows this plane reads red on `box-depth` instead of quietly resizing
# the appliance.
rear_plane_y = 472.0

# Where the box splits front from back, and where the front column splits bottom from
# top. Both are STATED planes: which pieces the box comes apart into is a decision
# about the pieces — what each has to carry, and what a hand reaches when the front
# assembly is off — and the depth and height each piece comes to is what the plane
# leaves. `_dims` measures them against the facet, the bed and the pack, and records what
# it reads (`y-seam-clears-facet`, `z-seam-front-bed`, `z-seam-two-pieces`).
#
# The BACK column's Z seam is the one that is searched (`_z_joints`): the cold core
# stands from the floor slab and the service bay stands on its lid, so that column runs
# solid and its seam has to take whatever height the bed and the lip's own ring allow.
y_seam = 200.0
front_z_seam = 160.0

# The bottom↔top seam planes, one per Y column. The seam machinery (a one-wall lip
# + the cross-pin pods) protrudes into the cavity at the walls, and every body in the
# box stands inboard of it — the cold core one boss chain off each side wall, the
# refrigeration stratum the same — so a lip segment and a pod run at full section at
# any height, and what picks these two numbers is the pack and the print bed. A 400 mm
# column split in two leaves each piece around half the height on its bed face against
# the H2C's 320, so a seam takes the height nearest the half-height that its own
# column leaves open, inside the band that leaves both its pieces on the bed
# (`_bed_band`). Where a column leaves no such height, the seam takes the nearest one
# the bed allows and runs its lip through the clearance the standoffs open
# (`_lip_denied`). They STAGGER — the front pair joins, the back pair joins, then
# the front assembly telescopes into the back — so a single plane never runs the box's
# whole depth, and the offset between them is at least one cross-pin pitch, so neither
# column's stations crowd the other's across the Y overlap. main() prints each piece's
# bed face and the fit.
# A seam landing in an open band keeps one `z_joint_clear` off every body in its own
# column, so every body there lands whole in one piece and its mounts have one piece to
# stand on — and a body standing clear ABOVE such a seam is one it passes under, the way
# the front seam passes under the hopper funnel. `_dims` reads both off the pack
# (`_z_joints`).
z_joint_clear = 3.0
# Each Y-seam level stands one (wall + bore radius) clear of a seam plane or a lip
# rim, and `_bosses` DROPS a level landing within 2*socket_r of one already placed —
# so two seams closer than this silently cost the Y seam a fastener. The front seam's
# OVER-rim level and the back seam's UNDER-seam level are the pair that meet.
# `_z_joints` picks the pair to clear it — the column with the least room to move goes
# first and the other stands off it; main() prints what each wall got.
z_joint_pitch = lip_len + 4.0 * socket_r + 2.0
# The Z lip stops this short of the Y-seam overlap on each side, so the two
# telescopes never share a wall surface.
z_lip_y_margin = 2.0


# The whole description of one box, so the appliance and its test coupon are
# the same geometry read from different numbers rather than two code paths:
#   inner/outer   the cavity and the shell, (x0, x1, y0, y1, z0, z1)
#   y_joint       the front↔back seam plane
#   splits        the bottom↔top seam height per Y column, (front, back)
#   front_ports   / back_ports   panel through-holes, in the pack's format
#   east_ports    +X side-wall through-holes, (kind, y, z, *size)
#   west_ports    −X side-wall through-holes, same shape — the drip tray's slot
#   funnel        the placed hopper funnel's plan centre, or None for no throat
#   pan_rails     the drip tray's carry, world boxes fused onto the −X wall
#   c14           the mains inlet's heat-set stations on the back wall, (x, z)
#   east_bosses   the +X wall's mounting bosses, (y, z, the plane the boss top reaches)
#   floor_bosses  the floor slab's mounting bosses, (x, y, the plane the boss top reaches)
Box = namedtuple(
    "Box", "inner outer y_joint splits front_ports back_ports east_ports west_ports "
           "funnel pan_rails c14 east_bosses floor_bosses")

# What a box is built AROUND: the placed bodies, and every station they put on a wall.
# A pack that does not carry a subsystem yet carries no stations for it, and the wall
# comes out blank there rather than carrying a hole with nothing behind it.
#   placed        {name: (solid, colour)} — the same shape a CadQuery assembly reads
# The rest are the Box fields above, and the box passes them through.
Pack = namedtuple(
    "Pack", "placed front_ports back_ports east_ports west_ports funnel pan_rails c14 "
            "east_bosses floor_bosses")
Pack.__new__.__defaults__ = ((), (), (), (), None, (), (), (), ())


# --- the bounds this box states ---------------------------------------------
#
# Width, depth and height are BOUNDS the appliance states, and the seams and the funnel throat
# are cut on frames the pack has to leave open. Every one is measured against the placed
# contents at each build, so a pack that grows opens one.
#
# A VIOLATED BOUND IS A THING TO LOOK AT, and what a reader looks at is the STEP, the three
# elevations and the scorecard a run writes. So none of these stops the build: each hands back
# a `Bound` whether it holds or not, and THE BOX COMES OUT AT ITS STATED SIZE — too small for
# the pack that overran it. The overrun is then a red row on the card carrying this module's
# own message, and the walls standing through the bodies that overran them are clashes in
# `pack-closes`, which is where a reader should see them. A box quietly grown to fit would
# show neither.
#
# `front_half.machine` and `front_half.build_front_half` carry these onto the assembly beside
# the bounds that module states itself. The ledger lives here because `enclosure` cannot
# import that module back — `machine_of` imports it inside the call for the same reason.
Bound = namedtuple("Bound", "id label ok value target detail")

BOUNDS: list = []


def record_bound(bound: Bound) -> Bound:
    """Enter one bound's reading in the ledger, replacing any of the same id."""
    BOUNDS[:] = [b for b in BOUNDS if b.id != bound.id] + [bound]
    return bound


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


def _ycyl(r, x, z, y0, y1):
    """Cylinder of radius r along Y from y0 to y1, axis at (x, z)."""
    return cq.Solid.makeCylinder(r, abs(y1 - y0), cq.Vector(x, min(y0, y1), z), cq.Vector(0, 1, 0))


def _zcyl(r, x, y, z0, z1):
    """Cylinder of radius r along Z from z0 to z1, axis at (x, y)."""
    return cq.Solid.makeCylinder(r, abs(z1 - z0), cq.Vector(x, y, min(z0, z1)), cq.Vector(0, 0, 1))


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
    """Round only the single standing-vertical (Z) corner edge of a solid at
    (xc, yc) — the facet window's +X shoulder, or a boss that sits in one of the
    box's rounded verticals and must stay concentric with the cavity there.
    r <= 0 leaves it square."""
    if r <= 0:
        return solid
    wp = cq.Workplane(obj=solid)
    edges = [e for e in wp.edges("|Z").vals()
             if abs(e.Center().x - xc) < 1e-6 and abs(e.Center().y - yc) < 1e-6]
    if not edges:
        return solid          # nothing stands in that corner
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


def _y_corner_back(iy1, y_joint):
    """The Y extent of the BACK half's corner column — the web standing in the
    front pod's slot, and the post behind the lip rim. It starts at the bore axis
    (the slot opens there) and runs one pod-depth past the rim."""
    return _y_boss(y_joint), min(iy1, y_joint + lip_len + 2.0 * socket_r)


def east_band_free_y():
    """The BACK half's free run of the ±X boss-chain bands, as `(y0, y1)`.

    What stands in those bands stands there floor to ceiling — `_front_pod` and `_z_post` both
    carry their column the whole height of their piece — and behind the seam there are two of
    them: the Y-seam corner group at `y0`, and the rear wall's own cross-pin column at `y1`.
    Between the two the band is nothing but the wall's air, so a body hung on this flank may
    stand OUTBOARD of where that furniture caps — on the wall itself, on a boss no longer than
    its insert — for exactly this depth, and meets a printed column either side of it. (The
    front half has its own free run ahead of the Y seam; this is not it.)

    Struck off the stated planes those columns are built on, `y_seam` and `rear_plane_y`, and
    not off a placed piece — so a body reads it before the box that carries it has been
    sized, the same way it reads the wall itself through `interior_x`."""
    yb, ybr = _z_back_station_y(rear_plane_y, y_seam)
    return (max(_y_corner_back(rear_plane_y, y_seam)[1],   # the Y-seam corner column's aft face
                yb + socket_r),                            # the station behind its mouth
            ybr - socket_r)                                # the rear wall's own station


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


def _chain_bands(inner):
    """The two ±X boss-chain bands as (x0, x1) pairs — the walls' own standoff off
    the cold core, where the seam's corner posts, mouth, plugs and pods stand."""
    ix0, ix1 = inner[0], inner[1]
    return [tuple(sorted((x_in, x_in + sx * boss_in)))
            for x_in, sx in ((ix0, +1.0), (ix1, -1.0))]


def _seam_bands_clear(placed, inner):
    """How far aft each part of the Y seam may reach before it meets content:
    (chain, ceiling) — the frontmost thing standing in the ±X boss-chain bands,
    and in the ceiling band the lip's top segment sweeps.

    Those are the only two places the seam occupies. This is the y_joint-free
    reading of them — it asks where content STARTS, not whether content stands
    where the furniture lands, so it can be measured before the seam is chosen.
    It bounds the seam whenever the band ahead of the content is all the seam
    can have; `_chain_span_clear` is what lets the seam pass content that sits
    forward of the furniture entirely."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner

    def frontmost(prism):
        limit = iy1
        for s, _c in placed.values():
            hit = prism.intersect(s)
            if hit.Volume() > 1.0:
                limit = min(limit, hit.BoundingBox().ymin)
        return limit

    chain = iy1
    for xa, xb in _chain_bands(inner):
        chain = min(chain, frontmost(_ybox(xa, xb, iy0, iy1, iz0, iz1)))
    return chain, frontmost(_ybox(ix0, ix1, iy0, iy1, iz1 - wall, iz1))


def _chain_spans_clear(placed, inner, spans):
    """Whether both ±X boss-chain bands run empty over every Y span the seam's own
    columns occupy (`_seam_furniture_spans`).

    The bands are a lane, not a keep-out: what matters is that nothing stands
    where the furniture lands, not that the furniture sits ahead of everything in
    the lane. A fitting parked between two stations leaves both their full section
    and never meets either, so it does not move the seam."""
    _ix0, _ix1, _iy0, _iy1, iz0, iz1 = inner
    for xa, xb in _chain_bands(inner):
        for y0, y1 in spans:
            prism = _ybox(xa, xb, y0, y1, iz0, iz1)
            for s, _c in placed.values():
                if prism.intersect(s).Volume() > 1.0:
                    return False
    return True


def _seam_furniture_spans(inner, y_joint):
    """Every Y span the seam occupies in the ±X boss-chain bands at `y_joint` — the
    Y-seam corner column (front half through back), plus each Z-seam pin station's
    own column, which stands in the same band at its own station.

    Read from the definitions that BUILD them (`_y_corner`, `_y_corner_back`,
    `_z_station_y`), so a span cannot drift from the geometry it stands for. The
    stations are why the band is not free depth: it runs clear between them, not
    along its whole length."""
    spans = [(_y_corner(inner, y_joint)[0], _y_corner_back(inner[3], y_joint)[1])]
    for _x_in, _x_ext, _sx, ys, col in _z_stations(inner, y_joint):
        spans.append(_z_station_y(inner, y_joint, ys, col))
    return spans


def _open_bands(spans, z0, z1, clear):
    """The heights in `[z0, z1]` a seam may land on, given the Z spans standing in
    that column: what the bodies leave open, inset `clear` at each end so the seam
    plane lands on neither. `[(lo, hi), ...]`, lowest first; a gap too thin to inset
    is not a band.

    A gap of exactly `2 * clear` IS a band — one height, no slack — because that is
    what a pack squeezed to its minimum leaves, and refusing it on a rounding bit
    would refuse a box that closes."""
    out, edge = [], z0
    for lo, hi in sorted(spans) + [(z1, z1)]:
        if lo > edge and lo - clear >= edge + clear - 1e-9:
            out.append((edge + clear, max(lo - clear, edge + clear)))
        edge = max(edge, hi)
    return out


def _clipped(bands, lo, hi):
    """`bands` held inside `[lo, hi]` — what falls wholly outside it drops out."""
    out = [(max(a, lo), min(b, hi)) for a, b in bands]
    return [(a, b) for a, b in out if b >= a - 1e-9]


def _outside(bands, lo, hi):
    """`bands` with the OPEN interval `(lo, hi)` taken out — the heights left to a
    seam once the other column's has taken one. The ends stay: `z_joint_pitch` is a
    minimum, so a seam standing exactly that far off is far enough."""
    out = []
    for a, b in bands:
        if a < lo:
            out.append((a, min(b, lo)))
        if b > hi:
            out.append((max(a, hi), b))
    return out


def _bed_band(inner):
    """The heights a Z seam may take and leave both its pieces printable.

    The bottom piece runs the floor slab's underside to its lip RIM (`zj + lip_len`,
    where the station pods' collars stop too); the top piece runs the seam plane to
    the top wall's outer face. Both print standing on a Z face, so the bed's Z bounds
    each of them, and each bound is one end of this band."""
    oz0, oz1 = inner[4] - wall, inner[5] + wall
    return oz1 - H2C_Z, oz0 + H2C_Z - lip_len


def _lip_denied(placed, inner):
    """The seam heights the pack denies a Z seam, as z spans.

    The lip is the one part of a Z seam whose position rides the seam height: a
    one-`wall` ring inset from the cavity, running from its fusion shoulder
    (`zj − wall`) up to its rim (`zj + lip_len`). The four station pods and the posts
    over them stand in the ±X boss-chain bands over their piece's WHOLE height, so
    they occupy the same lane wherever the seam lands.

    So this measures the ring: what reaches into it, and the seam heights that reach
    would put the lip on. What holds the rest of the ring open is the pack's own
    standoffs — one `wall` at the front and back walls (`front_seam_clear`,
    `rear_seam_clear`) and one boss chain at the sides (`side_rib_inset`)."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    ring = _ybox(ix0, ix1, iy0, iy1, iz0, iz1).cut(
        _ybox(ix0 + wall, ix1 - wall, iy0 + wall, iy1 - wall, iz0 - 1.0, iz1 + 1.0))
    out = []
    for solid, _c in placed.values():
        hit = ring.intersect(solid)
        if hit.Volume() > 1.0:
            b = hit.BoundingBox()
            out.append((b.zmin - lip_len, b.zmax + wall))
    return out


# Which columns' Z seams run THROUGH their own bodies rather than land in a band those
# bodies leave open. Filled by `_z_joints`, printed by main().
_z_seam_passes = {}


def _z_joints(placed, inner, front):
    """The bottom↔top seam height per Y column: `(front, back)`.

    `front` is the stated plane. It is checked against the bed — both its pieces have
    to print — and then the BACK column is searched around it.

    `_bed_band` is the band both of a column's pieces print inside; a seam lands in
    it. Within it a seam wants the box's own half-height — the split that leaves both
    pieces their best chance on the bed — and takes the nearest height in an OPEN BAND
    of its own column, where no body straddles the seam and neither does whatever
    holds one, and a body standing clear ABOVE the seam is one it passes under. A
    column with nothing in it is one open band.

    The back column has no open band inside the bed's: the cold core stands from the
    floor slab and the whole service bay stands on its lid, so the column runs solid
    to the bay's crown and what it leaves open is above all of it. That seam runs
    THROUGH its column, on the lane its lip needs (`_lip_denied`).

    The two stand `z_joint_pitch` apart, or the Y seam quietly comes out with fewer
    cross-pins than it has levels for.

    Four bounds are measured here and none of them stops the search: whatever the readings
    say, both seam heights come back and the box is cut on them. A seam that has to run
    through its column runs through it, and the pieces show that."""
    iz0, iz1 = inner[4], inner[5]
    y_mid = (inner[2] + inner[3]) / 2.0
    z_mid = (iz0 + iz1) / 2.0
    bed_lo, bed_hi = _bed_band(inner)
    on_bed = bed_lo - 1e-9 <= front <= bed_hi + 1e-9
    record_bound(Bound(
        "z-seam-front-bed", "The front Z seam leaves both its pieces on the H2C's bed", on_bed,
        f"seam at {front:.2f}, band {bed_lo:.2f}..{bed_hi:.2f}",
        f"inside the H2C's {H2C_Z:g} mm Z",
        ([] if on_bed else [
            f"the front Z seam at {front:.2f} leaves a piece off the H2C's {H2C_Z:g} mm bed: "
            f"the top piece wants it at or below {bed_hi:.2f} and the bottom at or above "
            f"{bed_lo:.2f}. Move `front_z_seam` into that band"])))
    record_bound(Bound(
        "z-seam-two-pieces", "A column splits into two pieces the H2C can print",
        bed_hi >= bed_lo,
        f"{iz1 - iz0 + 2.0 * wall:.2f} mm column, band {bed_lo:.2f}..{bed_hi:.2f}",
        f"a band inside the H2C's {H2C_Z:g} mm Z",
        ([] if bed_hi >= bed_lo else [
            f"a {iz1 - iz0 + 2.0 * wall:.2f} mm column has no seam height leaving two pieces "
            f"inside the H2C's {H2C_Z:g} mm Z: the top piece wants the seam at or below "
            f"{bed_hi:.2f} and the bottom at or above {bed_lo:.2f}. It needs a third piece"])))
    spans = {"front": [], "back": []}
    for _n, (solid, _c) in placed.items():
        b = _boxes.boxed(solid)
        col = "front" if (b.ymin + b.ymax) / 2.0 < y_mid else "back"
        spans[col].append((b.zmin, b.zmax))
    whole = _clipped(_open_bands(spans["back"], iz0, iz1, z_joint_clear), bed_lo, bed_hi)
    _z_seam_passes["front"] = None                 # stated, so there is nothing to report
    _z_seam_passes["back"] = not whole
    bands = whole or _open_bands(_lip_denied(placed, inner), bed_lo, bed_hi, 0.0)
    record_bound(Bound(
        "z-seam-back-band", "The back column leaves the bed a height its seam can take",
        bool(bands),
        f"{len(bands)} band(s) inside {bed_lo:.2f}..{bed_hi:.2f}", "at least one",
        ([] if bands else [
            f"the back column has no seam height the bed allows: inside "
            f"{bed_lo:.2f}..{bed_hi:.2f} its bodies leave no band "
            f"{2 * z_joint_clear:.2f} mm clear, and something stands in the lip's own "
            f"ring at every height there. Repack, or split this column in three"])))
    # THE SEAM STILL HAS TO LAND. With no band open it takes the bed's whole span, so the box
    # is split where the bed allows and the lip runs through whatever stands in its ring —
    # a clash in `pack-closes`, standing next to the row above.
    bands = bands or [(min(bed_lo, bed_hi), max(bed_lo, bed_hi))]
    # Nearest reachable height to the half-height, band by band; ties take the lower —
    # and a full `z_joint_pitch` clear of the stated front seam, or the Y seam quietly
    # comes out with fewer cross-pins than it has levels for.
    left = _outside(bands, front - z_joint_pitch, front + z_joint_pitch)
    # The pitch gives way and the band does not: a seam off its own column's open band cuts a
    # body, and one too near the front's only costs the Y seam cross-pins it has levels for.
    back = min((min(max(z_mid, lo), hi) for lo, hi in (left or bands)),
               key=lambda z: (abs(z - z_mid), z))
    record_bound(Bound(
        "z-seam-pitch", "The two Z seams stand the pitch two Y-seam levels need apart",
        bool(left),
        f"back seam at {back:.2f}, {abs(back - front):.2f} mm off the front's {front:.2f}",
        f"at least {z_joint_pitch:.2f} mm apart",
        ([] if left else [
            f"the back column's Z seam cannot stand the {z_joint_pitch:.2f} mm two Y-seam "
            f"levels need off the front's stated {front:.2f}: every height it has "
            f"({', '.join(f'{lo:.2f}..{hi:.2f}' for lo, hi in bands)}) is inside that pitch — "
            f"move `front_z_seam`, or the back column's bodies have to leave a band elsewhere"])))
    return front, back


def _dims(pack):
    """The box `pack` stands inside — its two shells, the plane it splits on, and the
    stations its walls carry. `pack` is a Pack (see `machine_of`).

    THE BOX IS ITS STATED SIZE and the pack has to fit in it. Width, depth and height are
    each measured against what the contents demand and each reading goes in the ledger, but
    the box that comes back is the one those three numbers describe — so a pack that overruns
    one gets a wall drawn through it, a red row saying by how much, and a clash in
    `pack-closes` at the body that overran. This is the only function that reads the placed
    parts, so it is where the ledger starts: `BOUNDS` is cleared here and refilled."""
    BOUNDS.clear()
    placed = pack.placed
    bbs = [_boxes.boxed(s) for s, _c in placed.values()]
    cxmin = min(b.xmin for b in bbs); cxmax = max(b.xmax for b in bbs)
    cymin = min(b.ymin for b in bbs); cymax = max(b.ymax for b in bbs)
    czmin = min(b.zmin for b in bbs); czmax = max(b.zmax for b in bbs)
    # WIDTH — the appliance's headline dimension, and the whole point of the yaw. Stated
    # as `appliance_width` and struck symmetric about x = 0, the axis the pack is centred
    # on, the same way depth is `rear_plane_y` and height is `appliance_height`.
    #
    # What the pack still has to earn is the clearance: a body standing on the slab spans
    # the interior wall to wall, so a wall on its face leaves the seam machinery — corner
    # posts, boss chains, Z-seam pods — nowhere to stand. Every floor body is held off by
    # one `side_rib_inset` so each of those seats at full section, and the body seats flush
    # against them instead of against the wall. Anything standing clear of the slab is above
    # the ±X bands' floor stations and needs only its own clearance.
    floor = [b for b in bbs if b.zmin < wall + 1e-6] or bbs
    ix0, ix1 = interior_x()
    wide_need = max(max(b.xmax for b in floor) + side_rib_inset,
                    -(min(b.xmin for b in floor) - side_rib_inset),
                    cxmax + interior_clearance, -(cxmin - interior_clearance))
    record_bound(Bound(
        "box-width", "The pack stands inside the appliance's stated width",
        wide_need <= ix1 + 1e-9,
        f"pack reaches x ±{wide_need:.2f}, wall at ±{ix1:.2f}",
        f"inside a {appliance_width:g} mm appliance",
        ([] if wide_need <= ix1 + 1e-9 else [
            f"the pack reaches x ±{wide_need:.2f} but a {appliance_width:g} mm appliance walls "
            f"in at ±{ix1:.2f} — {wide_need - ix1:.2f} mm over. Raise `appliance_width` or "
            f"repack inboard"])))
    # The FRONT wall stands one wall off the pack, for the same kind of reason
    # the ±X walls stand a boss chain off the widest floor body: a lip missing a side
    # is a butt joint over that run — nothing registering the two pieces, nothing
    # closing the line — and this run is the box's most visible face, so the wall
    # gives way, not the segment. A body mounted on the front wall seats on the plane
    # this opens.
    iy0 = cymin - interior_clearance - front_seam_clear
    # The BACK wall is the stated `rear_plane_y`, for the same reason the ceiling is the
    # stated `appliance_height`: depth is a bound, not a consequence. Taken off the pack it
    # would follow whichever body reached furthest back, and anything seated on this plane
    # would follow that body too, holding every clearance between the two constant.
    iy1 = rear_plane_y
    rear_need = cymax + interior_clearance + rear_seam_clear
    record_bound(Bound(
        "box-depth", "The pack stands inside the appliance's stated depth",
        rear_need <= iy1 + 1e-9,
        f"pack reaches y {rear_need:.2f}, back wall at {iy1:.2f}",
        f"ahead of `rear_plane_y` {rear_plane_y:g}",
        ([] if rear_need <= iy1 + 1e-9 else [
            f"the pack reaches y {rear_need:.2f} but the back wall stands at {iy1:.2f} — "
            f"{rear_need - iy1:.2f} mm over. Raise `rear_plane_y` or repack forward"])))
    # The floor is a fixed Z=0 datum, not the lowest content — so parts can stand
    # on feet above it (the floor, seam lip, and posts stay put). The CEILING is
    # the stated `appliance_height` measured from the floor slab's underside: the
    # thin machine's height is a bound, not a consequence, so the tallest content
    # does not lift it and slack above the pack is the column the unpacked
    # subsystems go in.
    iz0 = min(czmin, 0.0) - interior_clearance
    iz1 = (iz0 - wall) + appliance_height - wall
    inner = (ix0, ix1, iy0, iy1, iz0, iz1)
    y_joint = y_seam
    # What the contents demand, measured against the bound rather than setting it, so a pack
    # that outgrows it says so instead of quietly poking through the top wall. The ±X wall
    # bands are measured separately: the seam's top cross-pin pods hug the ceiling and reach
    # one boss chain inboard, so content inside that reach needs the pod stack over it as well
    # as its own height.
    #
    # THE REACH IS IN Y AS MUCH AS IN X. Those pods stand in a band only where the seam puts a
    # column there — `_seam_furniture_spans`, the same spans the seam's own furniture is built
    # over — and between them the band is the wall's own air the whole way to the ceiling.
    # Charging that stack to a body parked in the free depth would reserve headroom for a pod
    # that is nowhere near it, and the body that answers for it is the one hung on the wall.
    pod_stack = wall + socket_bore_dia / 2.0 + socket_r + 1.5    # ceiling → pod bottom + margin
    seam_spans = _seam_furniture_spans(inner, y_joint)
    wall_band_top = max(
        (b.zmax for b in bbs
         if (b.xmin < ix0 + boss_in or b.xmax > ix1 - boss_in)
         and any(b.ymin < sy1 and b.ymax > sy0 for sy0, sy1 in seam_spans)),
        default=iz0)
    need = max(czmax + interior_clearance, wall_band_top + pod_stack)
    record_bound(Bound(
        "box-height", "The pack stands under the appliance's stated ceiling",
        need <= iz1 + 1e-9,
        f"pack reaches z {need:.2f}, ceiling at {iz1:.2f}",
        f"under a {appliance_height:g} mm appliance",
        ([] if need <= iz1 + 1e-9 else [
            f"the pack reaches z {need:.2f} but a {appliance_height:g} mm appliance ceilings at "
            f"{iz1:.2f} — {need - iz1:.2f} mm over. Raise `appliance_height` or repack "
            f"downward"])))
    ox0, ox1 = ix0 - wall, ix1 + wall
    oy0, oy1 = iy0 - wall, iy1 + wall
    outer = (ox0, ox1, oy0, oy1, iz0 - wall, iz1 + wall)
    splits = _z_joints(placed, inner, front_z_seam)
    # The one thing the Y seam cannot do is cut the display housing: the facet is a
    # solid surface chamfered into the top-front arris and it prints as part of the
    # front-top piece, so the seam stands behind its back plane.
    facet_back = facet_back_y(outer)
    record_bound(Bound(
        "y-seam-clears-facet", "The Y seam stands behind the display housing",
        y_joint >= facet_back + 2.0,
        f"seam at {y_joint:.2f}, housing back plane at {facet_back:.2f}",
        f"aft of {facet_back + 2.0:.2f}",
        ([] if y_joint >= facet_back + 2.0 else [
            f"the Y seam at {y_joint:.2f} cuts the display housing, whose back plane is at "
            f"{facet_back:.2f} — the facet has to stay whole in the front pieces. Move "
            f"`y_seam` aft of {facet_back + 2.0:.2f}, or shorten `display_facet_slope`"])))
    # What the seam's own furniture lands in, at each depth something stands there: the
    # front half's column at the socket's full section (which also fixes where a level may
    # sit, since a level needs a socket body), and the back half's column — web through the
    # pod's slot, post behind the rim — at the pin's.
    fy0, fy1 = _y_corner(inner, y_joint)
    _measure_wall_relief(placed, inner, fy0, fy1, boss_in)
    by0, by1 = _y_corner_back(inner[3], y_joint)
    _measure_wall_relief(placed, inner, by0, by1, _plug_reach())
    return Box(inner, outer, y_joint, splits,
               pack.front_ports, pack.back_ports, pack.east_ports, pack.west_ports,
               pack.funnel, pack.pan_rails, pack.c14, pack.east_bosses,
               pack.floor_bosses)


# --- display facet (solid surface) -----------------------------------------

def _facet_geom(outer):
    ox0, ox1, oy0, oy1, oz0, oz1 = outer
    a = math.radians(display_facet_angle_deg)
    dy = display_facet_slope * math.sin(a)   # back from the front face
    dz = display_facet_slope * math.cos(a)   # down from the top face
    normal = (0.0, -math.sin(a), math.cos(a))
    origin = (0.0, oy0 + dy / 2.0, oz1 - dz / 2.0)
    return a, normal, origin, dy, dz


def facet_back_y(outer):
    """The Y the display housing reaches back to — the 45° face's own run aft
    plus the housing wall behind it, measured along Y. The frontmost the Y seam
    may sit, since the whole facet belongs to the front top piece; and where the
    top wall resumes, which is what the pack's own funnel centre pushes the basin
    forward against."""
    _a, _n, _o, dy, _dz = _facet_geom(outer)
    return outer[2] + dy + display_facet_thickness * math.sqrt(2.0)


def display_centre_x(outer):
    """The X the display's glass is centred on — the box's own middle, since the
    facet runs wall to wall. Read by the counterbore that receives it and by
    front_half's placement of the reference body, so the housing and the
    part in it cannot land on two different centres."""
    return (outer[0] + outer[1]) / 2.0


def _halfspace(origin, normal, extent):
    """Solid filling the +normal side of the plane through origin."""
    plane = cq.Plane(origin=cq.Vector(*origin), xDir=cq.Vector(1, 0, 0), normal=cq.Vector(*normal))
    return cq.Workplane(plane).rect(4 * extent, 4 * extent).extrude(extent).val()


def _facet_wedge(outer):
    """The solid removed to cut the display facet — the +normal half-space, over the
    box's WHOLE WIDTH. There is no lateral window: the chamfer runs wall to wall, so
    the top-front arris comes off in one plane and the cut needs no X term at all.
    Re-cut after the corner pods so they too are chamfered to the facet plane rather
    than poking through it."""
    ox0, ox1, oy0, oy1, oz0, oz1 = outer
    a, normal, origin, dy, dz = _facet_geom(outer)
    extent = max(ox1 - ox0, oy1 - oy0, oz1 - oz0) + 100.0
    return _halfspace(origin, normal, extent)


def _rounded_outer(outer):
    """The outer box with rounded standing-vertical corners and the facet
    chamfered in — the print silhouette the half is clipped to so nothing
    pokes past it. A full-width facet raises no new standing vertical: it runs
    out into the ±X walls' own rounds, which are already relieved."""
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
    keepout = _halfspace(back_origin, normal, extent)
    inner_clipped = inner_box.cut(keepout)

    return cq.Workplane(obj=outer_chamfered.cut(inner_clipped))


def _display_cuts(outer):
    """The display let into the facet: a shallow bezel counterbore on the user
    face and a PCB through-hole down the full facet thickness — both cut along
    the facet's 45° normal, starting one mm proud of the face for a clean break.
    The glass is the datum: the bezel counterbore is centred on the facet, which
    now means centred on the BOX (`display_centre_x`), with flat 45° face either
    side of it. The glass overhangs the body unevenly, so the PCB hole sits offset
    by display_body_offset — and is cut display_pcb_cut_through past the back to
    take a corner pod (which would otherwise overhang it) clean through.
    Counterbore corners rounded to the display radius."""
    a, normal, origin, dy, dz = _facet_geom(outer)
    center = (display_centre_x(outer), origin[1], origin[2])
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


# --- panel through-holes ----------------------------------------------------

def _port_cuts(ports, y0, y1):
    """The through-holes of one panel's port list, as cutters spanning y0..y1
    (a wall's thickness with a margin either side). The pack owns both layouts,
    since it places the bodies the bands are measured from
    (../back-panel/README.md); the two walls differ only in which list and
    which span, so they are cut by the same code."""
    out = []
    for kind, hx, hz, *size in ports:
        if kind == "round":
            out.append(cq.Solid.makeCylinder(size[0] / 2.0, y1 - y0,
                                             cq.Vector(hx, y0, hz), cq.Vector(0, 1, 0)))
        else:
            wx, wz, *radius = size
            out.append(_rect_cut_y(hx, hz, wx, wz, radius[0] if radius else 0.0, y0, y1))
    return out


def _rect_cut_y(hx, hz, wx, wz, radius, y0, y1):
    """One rectangular through-hole in a ±Y wall, spanning y0..y1, with the corner radius
    its port declares. A hole given none is cut square."""
    cut = (cq.Workplane("XY").box(wx, y1 - y0, wz)
           .translate((hx, (y0 + y1) / 2.0, hz)))
    return (cut.edges("|Y").fillet(radius) if radius else cut).val()


def _rect_cut_x(hy, hz, wy, wz, radius, x0, x1):
    """The same read on a ±X side wall, spanning x0..x1."""
    cut = (cq.Workplane("XY").box(x1 - x0, wy, wz)
           .translate(((x0 + x1) / 2.0, hy, hz)))
    return (cut.edges("|X").fillet(radius) if radius else cut).val()


def _x_port_cuts(ports, x0, x1):
    """`_port_cuts` read on a ±X side wall: each hole is (kind, y, z, *size) on the
    wall's own plane, and the cutter spans x0..x1 through it."""
    out = []
    for kind, hy, hz, *size in ports:
        if kind == "round":
            out.append(cq.Solid.makeCylinder(size[0] / 2.0, x1 - x0,
                                             cq.Vector(x0, hy, hz), cq.Vector(1, 0, 0)))
        else:
            wy, wz, *radius = size
            out.append(_rect_cut_x(hy, hz, wy, wz, radius[0] if radius else 0.0, x0, x1))
    return out


# --- hopper funnel opening (Zone C) -----------------------------------------

def _hopper_hole(inner, outer, y_joint, centre):
    """Rectangle (x0, x1, y0, y1) of the funnel opening in the top wall: the
    placed funnel's collar — hopper_funnel.py's own dims at
    the pack's own `funnel` centre.

    The frame is what the top wall has left to give: BEHIND the display facet's own
    back plane, inboard of the ±X top corner pods, and ahead of the back wall.

    THE FRONT IS A DIFFERENT KIND OF EDGE FROM THE OTHER THREE. On those, the frame
    runs out into a free edge, so the collar stands one `hopper_funnel.brim_margin`
    inside it — the flange overhangs the collar by `brim_overhang` to catch the wall
    and hold the funnel out of the box, and the margin is the wider of the two so a
    full overhang's width of top wall still remains outboard of the brim's edge.
    Forward there is no free edge: the wall runs straight on into the display
    housing, `display_facet_thickness` of solid slab between the facet's back plane
    and its 45° face, and that slab is what the brim's front flange lands on. So the
    whole of the front's requirement is `hopper_front_ledge` — the top wall kept
    between the housing's back plane and the throat itself — and that is asserted on
    the hole rather than on a frame the margin then sits inside.

    The funnel is pushed as far FORWARD as this frame allows, and reaches aft for
    whatever plan area its capacity needs — so the opening may cross the Y seam.
    Both halves take their share of the cut and the collar bridges it; what the
    seam gives up there is its top-wall lip over the hole's span, which the mouth
    shelf's own relief already accounts for (`_hopper_cut`).

    Three bounds are measured on that frame and the rectangle comes back whichever way they
    read — a collar outside its frame is cut where it stands, so the throat that runs into a
    pod or off the facet is in the pieces to look at, beside the row that names it."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    ox0, ox1, oy0, oy1, oz0, oz1 = outer
    cx, cy = centre
    x0 = cx - _funnel.collar_w / 2.0
    x1 = cx + _funnel.collar_w / 2.0
    y0 = cy - _funnel.collar_d / 2.0
    y1 = cy + _funnel.collar_d / 2.0
    pod_out = ix0 - wall + (head_cbore_depth + screw_len + socket_cap)
    pod_in = ix1 + wall - (head_cbore_depth + screw_len + socket_cap)
    lims = (pod_out + 1.0,                             # clear of the top-left pod
            pod_in - 1.0,                              # clear of the top-right pod
            facet_back_y(outer) + hopper_front_ledge,  # behind the facet's housing
            iy1 - wall)                                # ahead of the back wall
    tol = 1e-6
    inside = not (x0 < lims[0] - tol or x1 > lims[1] + tol
                  or y0 < lims[2] - tol or y1 > lims[3] + tol)
    record_bound(Bound(
        "funnel-collar-frame", "The funnel collar stands in the frame the top wall has left",
        inside,
        f"collar x {x0:.2f}..{x1:.2f}, y {y0:.2f}..{y1:.2f}",
        f"frame x {lims[0]:.2f}..{lims[1]:.2f}, y {lims[2]:.2f}..{lims[3]:.2f}",
        ([] if inside else [
            f"funnel collar (x {x0:.2f}..{x1:.2f}, y {y0:.2f}..{y1:.2f}) violates the "
            f"top-wall frame (x {lims[0]:.2f}..{lims[1]:.2f}, "
            f"y {lims[2]:.2f}..{lims[3]:.2f})"])))
    # One margin of top wall on the three sides that run out into a free edge, and the
    # brim fits it. The front is the ledge above and is measured on `lims[2]` instead.
    fits = _funnel.brim_overhang <= _funnel.brim_margin + tol
    record_bound(Bound(
        "funnel-brim-overhang", "The funnel's brim overhang fits its top-wall margin", fits,
        f"overhang {_funnel.brim_overhang:.2f} mm",
        f"within brim_margin {_funnel.brim_margin:.2f} mm",
        ([] if fits else [
            f"funnel brim overhang {_funnel.brim_overhang:.2f} exceeds its top-wall "
            f"margin {_funnel.brim_margin:.2f} — the flange hangs off the frame"])))
    got = (x0 - lims[0], lims[1] - x1, lims[3] - y1)
    clear = not any(g < _funnel.brim_margin - 1e-6 for g in got)
    record_bound(Bound(
        "funnel-brim-margin", "The funnel collar keeps a brim margin at each free edge", clear,
        f"−X {got[0]:.2f}, +X {got[1]:.2f}, +Y {got[2]:.2f} mm",
        f"each at least brim_margin {_funnel.brim_margin:.2f} mm",
        ([] if clear else [
            f"funnel collar crowds the top-wall frame: free-edge margins "
            f"(−X {got[0]:.2f}, +X {got[1]:.2f}, +Y {got[2]:.2f}) "
            f"— each owes brim_margin {_funnel.brim_margin:.2f}. Frame is "
            f"x {lims[0]:.2f}..{lims[1]:.2f}, y {lims[2]:.2f}..{lims[3]:.2f}; the collar it "
            f"has room for is {lims[1] - lims[0] - 2.0 * _funnel.brim_margin:.1f} × "
            f"{lims[3] - lims[2] - _funnel.brim_margin:.1f}"])))
    return x0, x1, y0, y1


def _hopper_cut(inner, outer, y_joint, centre):
    """The funnel throat punched clean through the top wall — one wall deeper
    than the ceiling, so the Y-seam's top-wall lip/mouth shelf (hanging one
    wall below it) is relieved across the hole span the seam crosses.

    The opening is the collar, whole: the basin is a full rectangle and the wall carries
    nothing over the tap-water sequence that the throat has to be cut around."""
    x0, x1, y0, y1 = _hopper_hole(inner, outer, y_joint, centre)
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


def _bosses(inner, splits, y_joint):
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
    brick bond.

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
    fy0, fy1 = _y_corner(inner, y_joint)
    out = []
    for x_in, sx in ((ix0, +1.0), (ix1, -1.0)):
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
    ya, yb = _y_corner_back(inner[3], y_joint)
    web = _ybox(xa, xb, ya, min(yb, y_joint + lip_len + z_lip_y_margin), iz0, iz1)
    ya = y_joint + lip_len
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

    THREE-SIDED here: both side walls and the ceiling. The floor is lapped too —
    every seam laps, none butts — but by a different means, because the floor is
    the one seam face whose inner side is not free. This proud tongue is the wall
    or ceiling continuing one `wall` INTO the cavity, and on the free faces that
    space is empty; on the floor the cold core rides there, so a proud floor tongue
    would drive straight into it. The floor's overlap therefore lives inside the
    slab as a shiplap (`_floor_lap`), not standing proud — the right lap for a
    bearing face. So the lip proper stays three-sided, and the floor carries its
    own lap. What that costs the ceiling segment — a cantilever that juts one
    overlap past the body over the back piece's floor, wanting print support — the
    floor shiplap shares (its front half runs one overlap aft over open air the
    same way); the side-wall segments, vertical to the bed, are free."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    y0, y1 = y_joint - wall, y_joint + lip_len
    outer = _ybox(ix0, ix1, y0, y1, iz0, iz1)
    inner_box = _ybox(ix0 + wall, ix1 - wall, y0 - 1.0, y1 + 1.0, iz0 - 1.0, iz1 - wall)
    return outer.cut(inner_box)


def _floor_lap(inner, y_joint):
    """The Y seam's FLOOR overlap, as a shiplap within the floor slab.

    The floor is the one seam face whose inner side is not free — the cold core
    rides on it — so it cannot carry the proud, cavity-side tongue the walls and
    ceiling do (`_front_lip`): that tongue would stand up into the core. Instead
    the two floors lap within the slab's own one-`wall` thickness. The FRONT
    floor's upper (cavity-side) half runs one overlap aft past the seam; the BACK
    floor keeps its lower (bed-side) half there and gives its upper half up to
    receive the tongue. Assembled, the slab is one unbroken run across the seam
    with no straight-through line, and the core still seats on a flush z=iz0 top —
    the front tongue fills the top over the overlap, the back floor everywhere
    else. This is the floor's answer to the wall shiplap: an overlap on every seam,
    the form suited to the face.

    Returns (tongue, relief): the solid the FRONT half fuses (its aft upper-half
    tongue) and the solid the BACK half cuts (its upper half over the overlap,
    plus a split_slip slide clearance so the tongue telescopes in freely)."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    zmid = iz0 - wall / 2.0                          # slab mid-plane (bed-side | cavity-side)
    y0, y1 = y_joint, y_joint + lip_len
    tongue = _ybox(ix0, ix1, y0, y1, zmid, iz0)
    relief = _ybox(ix0, ix1, y0 - 1.0, y1 + split_slip, zmid - split_slip / 2.0, iz0)
    return tongue, relief


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


def _z_back_station_y(iy1, y_joint):
    """The BACK column's two X-pin stations in Y — behind the Y-seam mouth (where the
    telescoped front lip stops) and the rear-wall corner.

    Its own function because it is read twice: once here, to build the stations, and once by
    `east_band_free_y`, to say where the columns they carry leave the ±X band free. Struck off
    the rear plane and the seam alone, so the second reader needs no placed piece.

    Behind the mouth, the station stands off the Z-lip's Y-gap edge (y_joint + lip_len +
    z_lip_y_margin) by a full socket_r — the same clearance the front column's aft station
    keeps from that gap on its side. Drop the z_lip_y_margin term and the pod's −Y wall
    pinches to (wall − z_lip_y_margin) against the gap, too thin to telescope into the top
    piece; with it the pod keeps a full wall each side of its bore."""
    r = socket_bore_dia / 2.0
    return (y_joint + lip_len + z_lip_y_margin + wall + r, iy1 - wall - r)


def _z_stations(inner, y_joint):
    """X-axis pin stations along the Z seams — TWO per ±X wall per Y column, one
    at each END of that column's seam, so a seam pinned only at one end cannot
    hinge open at the other.

    Front column: the front-wall corner and the aft end of its own lip, just
    ahead of where the Y-seam furniture starts. Back column: just behind the
    Y-seam mouth (where the telescoped front lip stops) and the rear-wall
    corner. Every station stands in the ±X band the walls' standoff opens off
    the cold core, and the depth between the two columns is what `east_band_free_y`
    hands a body hung on that wall. Each column's stations ride that column's own
    seam height."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    r = socket_bore_dia / 2.0
    yf = iy0 + wall + r                             # front column, front wall
    yfr = y_joint - wall - z_lip_y_margin - socket_r  # front column, aft end of its lip
    yb, ybr = _z_back_station_y(iy1, y_joint)
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

    Every other side is carried whole. A missing side is a butt joint over
    that run — nothing registering the two pieces, nothing closing the line —
    so where content stands in a segment's way it is the WALL that is held off
    it (`_dims`), not the segment that is given up.

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


# --- test-print coupon ------------------------------------------------------
#
# The same box shrunk to the smallest one that still carries, at FULL size,
# every feature the four-piece assembly is judged on: the display housing, and all
# three seams (the Y seam and the two staggered Z seams) with their full ladder of
# cross-pins. It splits into the same four pieces by the same code, so a print of
# it proves the assembly before the real one is committed.
#
# What it does NOT carry is anything the reduced box cannot host honestly: the
# contents (there is nothing to pack, so nothing to dodge — the walls' relief and
# the seam's stand-off have no meaning here), the panel through-holes (there are
# none yet), and the hopper throat (the placed funnel's collar would not fit the
# shrunken top-wall frame).
#
# Its facet runs the coupon's own full width, the way the appliance's runs the
# appliance's — but the coupon is only as wide as the display window plus a corner
# chain either side, because the extra flat 45° face the appliance spends its width
# on proves nothing about the housing and only makes the coupon wider.
#
# No dimension below is chosen. Each is the minimum its own feature allows, so
# the coupon shrinks and grows with the features rather than drifting from them.
coupon_margin = 2.0        # clear air wherever a coupon dimension is a minimum


def _level_pitch():
    """The least a coupon may stand two cross-pin levels (or two Z-seam
    stations) apart: two socket collars, plus air. `_bosses` DROPS a level
    landing within 2*socket_r of one already placed — so a box packed tighter
    than this does not fail, it silently comes out with fewer fasteners than
    the seam is supposed to have."""
    return 2.0 * socket_r + coupon_margin


def coupon_box():
    """The coupon's Box — every number a minimum, derived from the feature that
    sets it.

    DEPTH is the display: the front column is the facet's own run aft plus its
    housing wall, and the seam a margin behind that; the back column is the two
    Z-seam stations `_z_stations` puts at the ends of its seam, stood far enough
    apart that their pods do not merge into one blob.

    WIDTH is the display's own window — `display_facet_x` — with a corner chain and
    a margin clear at BOTH walls, so the housing is proved to fit between the
    columns that flank it.

    HEIGHT is the cross-pin ladder up the Y seam — a level over the floor, one
    under each Z seam, one over each lip rim, one under the ceiling, each a
    clear pitch from the last — raised, if the facet wants more, so the whole
    housing falls above the front seam's lip rim."""
    r = socket_bore_dia / 2.0
    pitch = _level_pitch()
    ix0 = iy0 = iz0 = 0.0

    # Depth. The seam clears the display housing's back plane; the rear wall
    # stands where the back column's aft Z station (iy1 − wall − r) falls a
    # clear pitch behind its forward one (y_joint + lip_len + z_lip_y_margin +
    # wall + r, standing off the Z-lip gap — see _z_stations). How far
    # the housing reaches — aft and down — depends only on where the front face
    # and the top face are, so it can be asked of a box not yet sized: the front
    # face is fixed the moment iy0 is, and the fall is measured off the top face
    # wherever that lands.
    front_face = (ix0, ix0, iy0 - wall, iy0, iz0, iz0)
    y_joint = facet_back_y(front_face) + coupon_margin
    iy1 = y_joint + lip_len + z_lip_y_margin + 2.0 * (wall + r) + pitch

    # Width. The display window, with a chain's width and a margin clear at both
    # walls.
    ix1 = ix0 + display_facet_x + 2.0 * (boss_in + coupon_margin)

    # Height. Each seam sits a pitch's worth of ladder above the last rung:
    # floor level → front seam → its lip rim → back seam → its lip rim →
    # ceiling. Then the ceiling is raised if the facet wants more, since the whole
    # housing must fall above the front seam's lip rim.
    zjf = (iz0 + wall + r) + pitch + wall + r
    zjb = (zjf + lip_len + wall + r) + pitch + wall + r
    _a, _n, _o, _dy, facet_dz = _facet_geom(front_face)     # the facet's fall
    iz1 = max((zjb + lip_len + wall + r) + pitch + wall + r,
              zjf + lip_len + coupon_margin + facet_dz - wall)

    inner = (ix0, ix1, iy0, iy1, iz0, iz1)
    outer = (ix0 - wall, ix1 + wall, iy0 - wall, iy1 + wall, iz0 - wall, iz1 + wall)
    return Box(inner, outer, y_joint, (zjf, zjb), (), (), (), (), None, (), (), ())


def build_front_half(box):
    """The whole front column, both pieces still joined at its Z seam."""
    inner, outer, y_joint = box.inner, box.outer, box.y_joint
    shell = _shell_with_facet(inner, outer).val()
    front = shell.intersect(_ybox(outer[0], outer[1], outer[2], y_joint, outer[4], outer[5]))
    front = front.fuse(_front_lip(inner, y_joint))
    # The floor's overlap: the front's aft upper-half floor tongue, lapping the
    # back half's slab within the slab (the core rides the cavity side, so the
    # floor cannot tongue proud like the walls). Lands in the bottom piece.
    front = front.fuse(_floor_lap(inner, y_joint)[0])
    yb = _y_boss(y_joint)
    bosses = _bosses(inner, box.splits, y_joint)
    # One post per side wall, not per level: every level on a wall shares the
    # same column, and the levels are just where it is bored.
    for x_in, x_ext, sx, _zb, pod_z in _sides(bosses):
        front = front.fuse(_front_pod(x_in, x_ext, sx, pod_z, y_joint, inner))
        front = front.fuse(_front_pod_ends(x_in, x_ext, sx, y_joint, inner, outer))
    # The full-depth pods can poke into the display facet; trim them to its plane.
    # The facet runs wall to wall, so it needs no end wall — both ends are the
    # exterior side walls, which seal themselves.
    front = front.cut(_facet_wedge(outer))
    # Let the display into the facet (bezel counterbore + PCB through-hole); this
    # also clears whatever rib/wall material sits behind the facet in its path.
    front = front.cut(_display_cuts(outer))
    # Punch the hopper funnel throat through the top wall, behind the display.
    if box.funnel:
        front = front.cut(_hopper_cut(inner, outer, y_joint, box.funnel))
    # Front-panel through-holes.
    for cutter in _port_cuts(box.front_ports, outer[2] - 5.0, inner[2] + 5.0):
        front = front.cut(cutter)
    # East side-wall through-holes — the CO2 inlet's, low in the machine corridor.
    for cutter in _x_port_cuts(box.east_ports, inner[1] - 5.0, outer[1] + 5.0):
        front = front.cut(cutter)
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


def build_back_half(box):
    """The whole back column, both pieces still joined at its Z seam. The
    hopper opening crosses the Y seam, so this half takes its share of the
    cut — the collar bridges the seam."""
    inner, outer, y_joint = box.inner, box.outer, box.y_joint
    shell = _shell_with_facet(inner, outer).val()
    back = shell.intersect(_ybox(outer[0], outer[1], y_joint, outer[3], outer[4], outer[5]))
    # Give up the slab's upper half over the overlap to receive the front floor
    # tongue (the shiplap's other half); the back keeps its bed-side half, which
    # the core still rides. Lands in the bottom piece.
    back = back.cut(_floor_lap(inner, y_joint)[1])
    if box.funnel:
        back = back.cut(_hopper_cut(inner, outer, y_joint, box.funnel))
    yb = _y_boss(y_joint)
    bosses = _bosses(inner, box.splits, y_joint)
    # The back half is the back column, so its own seam is the one its post
    # steps around.
    zj = box.splits[1]
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
        waist = _wall_waist(x_in, x_tip, sx, *_y_corner_back(inner[3], y_joint))
        if waist is not None:
            back = back.cut(waist)
    # Clip any corner feature that pokes past the rounded print silhouette.
    back = back.intersect(_rounded_outer(outer))
    for x_in, x_ext, sx, z_boss, _pz in bosses:
        back = back.cut(_screw_cut(x_ext, sx, z_boss, yb))
    # Panel through-holes for the appliance's external connections — the
    # faucet umbilical (carb-water + two flavor), the tap-water inlet, and
    # the C14 mains inlet, all through the back wall in the band above the
    # cold core; their bodies hang in the band's open rear half.
    for cutter in _port_cuts(box.back_ports, inner[3] - 5.0, outer[3] + 5.0):
        back = back.cut(cutter)
    back = _c14_bosses(back, inner, outer, box.c14, outer[4] - 1.0, outer[5] + 1.0)
    # The drip tray's withdrawal slot through the −X wall, and the rail pair it rides. Cut the
    # slot first: the rails stand on the wall the two rectangles leave between them.
    for cutter in _x_port_cuts(box.west_ports, outer[0] - 5.0, inner[0] + 5.0):
        back = back.cut(cutter)
    back = _pan_rails(back, box.pan_rails, outer[4] - 1.0, outer[5] + 1.0)
    return cq.Workplane(obj=back)


def _pan_rails(solid, members, z0, z1):
    """The drip tray's carry fused onto a −X wall, for the members whose top lies in `z0..z1`.

    The pack states each member as a world box, rooted on the wall's inner face and running
    east under the tray's rim, and closes their east ends with the bar the tray comes to
    rest against. Three members and one U — the tray hangs
    between the rails off its own flange, and nothing stands under its floor."""
    for x0, x1, y0, y1, rz0, rz1 in members:
        if not z0 <= rz1 <= z1:
            continue
        solid = solid.fuse(_ybox(x0, x1, y0, y1, rz0, rz1))
    return solid


def _floor_bosses(solid, inner, stations, y0, y1, z0, z1):
    """The floor slab's mounting bosses added to a PIECE, for the stations whose plan point
    the piece owns and whose slab it holds.

    Each station is `(x, y, tip)`: the two plan coordinates the boss stands on, and the plane
    its top face reaches — the mounting plane of the body bolted down onto it, which is where
    that body's hole pattern lies. The post runs UP from the slab's own inner face to that
    plane and the insert bore is cut back down from it, so what the slab gives a screw is the
    standoff the body asked for.

    The ±X walls take their bodies on the flank and the slab takes them from underneath, which
    is the whole difference between this and `_east_bosses`: the shaft runs on Z, the band that
    selects a station is the piece's Y column, and a station only lands on a piece whose Z band
    reaches the floor."""
    if z0 > inner[4] + 1e-6:
        return solid                       # a top piece has no slab to stand a post on
    for sx, sy, tip in stations:
        if not (y0 <= sy <= y1):
            continue
        solid = solid.fuse(_zcyl(mount_boss_dia / 2.0, sx, sy, inner[4], tip))
        solid = solid.cut(_zcyl(heatset_dia / 2.0, sx, sy,
                                tip - heatset_depth - mount_bore_relief, tip))
    return solid


def _east_bosses(solid, inner, stations, y0, y1, z0, z1):
    """The +X wall's mounting bosses added to a PIECE, for the stations inside the depth and
    height band that piece owns — so a boss lands in the piece whose wall carries it, whole,
    and no piece grows a column standing in another's air.

    Each station is `(y, z, tip)`: the two plan coordinates the boss stands on, and the plane
    its top face reaches — the body's own mounting face, which is where that body's hole
    pattern lies. The shaft runs from the wall's inner face out to it and the insert bore is
    cut back from that face, so the length the wall gives a screw is the standoff the body
    asked for and not a number typed here.

    ON THE PIECE AND NOT ON THE HALF, because the Z seam's own column is fused piece-side:
    the rear station's post reaches the same plane the bodies on this flank seat on, so a bore
    cut before that post is fused is a bore the post fills back in. Cut here, the two share
    their material — the boss fuses nothing where the post already stands, and is bored
    through it all the same."""
    for sy, sz, tip in stations:
        if not (y0 <= sy <= y1 and z0 <= sz <= z1):
            continue
        solid = solid.fuse(_xcyl(mount_boss_dia / 2.0, sy, sz, tip, inner[1]))
        solid = solid.cut(_xcyl(heatset_dia / 2.0, sy, sz, tip,
                                tip + heatset_depth + mount_bore_relief))
    return solid


def _c14_bosses(solid, inner, outer, stations, z0, z1):
    """The C14's two heat-set bosses added to a back wall, for the stations whose Z lies in
    `z0..z1`.

    That receptacle is fastened from INSIDE — its flange bears on this wall's inner face —
    so its insert enters flush with that face and the length of it the wall cannot hold
    stands proud OUTWARD, past the print silhouette. The bore is cut after the boss, so it
    runs the insert's whole depth from the inner face."""
    for sx, sz in stations:
        if z0 <= sz <= z1:
            solid = solid.fuse(_ycyl(c14_boss_dia / 2.0, sx, sz,
                                     inner[3], outer[3] + c14_boss_proud))
            solid = solid.cut(_ycyl(heatset_dia / 2.0, sx, sz,
                                    inner[3], inner[3] + heatset_depth))
    return solid


def build_piece(box, y_side, z_side, halves_cache=None):
    """One of the four printable pieces: the full front/back column split at
    its own seam (`box.splits` — the staggered pair), the bottom taking the Z
    lip + socket pods, the top taking the D-pins + posts + X-axis screw bores.
    The Y-seam bosses' bottom pair sits under the LOWER seam (the front's), so
    it lands in — and pins — the two bottom pieces."""
    inner, outer, y_joint = box.inner, box.outer, box.y_joint
    ox0, ox1, oy0, oy1, oz0, oz1 = outer
    zj = box.splits[0] if y_side == "front" else box.splits[1]
    if halves_cache is not None and y_side in halves_cache:
        half = halves_cache[y_side]
    else:
        half = build_front_half(box) if y_side == "front" else build_back_half(box)
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
    zlo, zhi = (oz0 - 1.0, zj) if z_side == "bottom" else (zj, oz1 + 1.0)
    if y_side == "back":
        # The C14's bosses stand OUTSIDE the print silhouette — the receptacle is fastened
        # from inside, so the insert enters flush with the inner face and the length the
        # wall cannot hold stands outboard. They go on after the clip, on whichever piece
        # holds their Z.
        piece = _c14_bosses(piece, inner, outer, box.c14, zlo, zhi)
    # The +X wall's mounting bosses, on whichever piece holds each one's station. Last of
    # all, so a bore is cut through every column that has already been fused around it.
    ylo, yhi = ((oy0 - 1.0, y_joint) if y_side == "front" else (y_joint, oy1 + 1.0))
    piece = _east_bosses(piece, inner, box.east_bosses, ylo, yhi, zlo, zhi)
    # The floor slab's, on whichever piece holds each one's plan station. Only the bottom
    # pieces have a slab to stand one on, and `_floor_bosses` drops any station outside.
    piece = _floor_bosses(piece, inner, box.floor_bosses, ylo, yhi, zlo, zhi)
    return cq.Workplane(obj=piece)


# --- reporting --------------------------------------------------------------

def _report_facet(half, box):
    a = math.radians(display_facet_angle_deg)
    target = cq.Vector(0.0, -math.sin(a), math.cos(a))
    # The lip's +Z bevel ramp shares this normal (excluded by the front-region
    # y filter) and the pod's east shoulder shares it one wall lower (excluded
    # by the on-plane filter) — only the display facet itself is measured.
    outer = box.outer
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
    want_x = outer[1] - outer[0]                      # the facet runs the box's full width
    print(f"  display facet:    {xspan:.1f} mm wide (X) × {slope:.1f} mm slope, solid surface "
          f"(want {want_x:g} × {display_facet_slope:g}; the display window is "
          f"{display_facet_x:g} × {display_facet_slope:g}, centred at "
          f"x {display_centre_x(outer):g})")


def _report_split(pieces, core=None):
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
    if core is not None:
        clash = max(core.intersect(p.val()).Volume() for p in pieces.values())
        print(f"  cold core vs pieces: {clash:.1f} mm³ max overlap  "
              f"({'CLEAR' if clash < 1 else 'CLASH'})")


def _report_seams(box):
    """Each Z seam's height, whether it landed in a band its own column left open or
    runs through that column on a clear lip, and the band the bed allowed it."""
    lo, hi = _bed_band(box.inner)
    for col, zj in zip(("front", "back"), box.splits):
        how = "runs through its column" if _z_seam_passes.get(col) else "in an open band"
        print(f"  Z seam {col + ':':7s} {zj:6.1f} mm  ({how}; the bed allows "
              f"{lo:.1f}..{hi:.1f})")


def _report_levels(box):
    """The Y-seam cross-pin heights each ±X wall ended up with. They are searched
    per wall against what stands against it, so the two can differ — printing
    them keeps a wall that had to give up a level visible instead of silent."""
    bosses = _bosses(box.inner, box.splits, box.y_joint)
    for sx, label in ((+1.0, "−X"), (-1.0, "+X")):
        zs = sorted(b[3] for b in bosses if b[2] == sx)
        print(f"  Y-seam levels {label} wall: {len(zs)} — "
              + ", ".join(f"{z:.0f}" for z in zs))


PIECE_COLORS = {
    "front-bottom": cq.Color(0.80, 0.84, 0.90),
    "front-top":    cq.Color(0.86, 0.89, 0.94),
    "back-bottom":  cq.Color(0.70, 0.74, 0.82),
    "back-top":     cq.Color(0.76, 0.80, 0.87),
}


def build_pieces(box, stem="enclosure"):
    """The four printable pieces of one box, and the assembly of them in place
    with the seams intact. The appliance and its coupon come through here
    alike — one box description in, four pieces out."""
    cache = {}
    pieces = {name: build_piece(box, *name.split("-"), halves_cache=cache)
              for name in PIECE_COLORS}
    assy = cq.Assembly(name=stem.replace("-", "_"))
    for name, piece in pieces.items():
        assy.add(piece, name=f"{stem}-{name}".replace("-", "_"),
                 color=PIECE_COLORS[name])
    return pieces, assy


def _export_pieces(pieces, assy, stem, note):
    for name, piece in pieces.items():
        export_step(piece, str(_here.parent / f"{stem}-{name}.step"))
        print(f"-> {stem}-{name}.step{note}")
    export_assembly(assy, str(_here.parent / f"{stem}.step"))
    print(f"-> {stem}.step (assembled pieces){note}")


def box_around(pack):
    """The box `pack` stands inside — the description `build_pieces` turns into the four
    printable pieces."""
    return _dims(pack)


def machine_of():
    """The machine's pack and the box around it. `hardware/manifold-layout/front_half.py`
    places the bodies and seats the wall stations, so both come from there and the box this
    prints is the box that pack stands in.

    Imported here rather than at module scope so that front_half, which builds its own
    assembly around these walls, is not importing a module that is importing it back."""
    sys.path.insert(0, str(_repo / "hardware" / "manifold-layout"))
    import front_half
    _assy, pack, box = front_half.machine()
    return pack, box


def _report_bounds():
    """Every bound in the ledger that is open, and nothing when they all hold.

    The card `front_half` writes is the committed account of these; this is the same reading
    for whoever ran this module on its own, where there is no card."""
    open_ = [b for b in BOUNDS if not b.ok]
    if not open_:
        return
    print(f"\n{len(open_)} of {len(BOUNDS)} bounds open — the box is drawn at its stated size "
          f"anyway, so the overrun is in the pieces:")
    for b in open_:
        print(f"  {b.id}: {b.value}   (wants {b.target})")
        for line in b.detail:
            print(f"    {line}")
    print()


def main():
    machine, box = machine_of()
    pieces, assy = build_pieces(box)
    _report_bounds()          # the machine's, with its pieces cut and its throat measured
    coupon = coupon_box()
    coupon_pieces, coupon_assy = build_pieces(coupon, "enclosure-coupon")

    _export_pieces(pieces, assy, "enclosure", "")
    _export_pieces(coupon_pieces, coupon_assy, "enclosure-coupon", " (test print)")

    print("enclosure:")
    _report_facet(pieces["front-top"], box)
    _report_seams(box)
    _report_levels(box)
    _report_split(pieces, machine.placed["foam-assembly"][0])
    print("coupon:")
    _report_facet(coupon_pieces["front-top"], coupon)
    _report_levels(coupon)
    _report_split(coupon_pieces)

    co, bo = coupon.outer, box.outer
    variables = {
        "DISPLAY_FACET_X": f"{display_facet_x:.4g} mm",
        "DISPLAY_FACET_SLOPE": f"{display_facet_slope:.4g} mm",
        "APPLIANCE_HEIGHT": f"{appliance_height:.4g} mm",
        "BOX_SIZE": (f"{bo[1] - bo[0]:.0f} × {bo[3] - bo[2]:.0f} × "
                     f"{bo[5] - bo[4]:.0f} mm"),
        "COUPON_SIZE": (f"{co[1] - co[0]:.0f} × {co[3] - co[2]:.0f} × "
                        f"{co[5] - co[4]:.0f} mm"),
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={"DISPLAY_FACET_X": 2, "DISPLAY_FACET_SLOPE": 2},
    )
    substitute_md(
        _here.parent / "README.md",
        variables=variables,
        expected_counts={"DISPLAY_FACET_X": 1, "DISPLAY_FACET_SLOPE": 1,
                         "APPLIANCE_HEIGHT": 1, "BOX_SIZE": 1, "COUPON_SIZE": 1},
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
