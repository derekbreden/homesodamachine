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
the widest of the three even yawed a quarter turn (`enclosure_assembly.FOAM_YAW`), which
is what puts its 181 mm short face across the machine instead of its 283 mm long one. The
pack is placed by `../../../manifold-layout/enclosure_assembly.py`. Features:

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
sys.path.insert(0, str(_repo / "hardware" / "reference" / "wago-221"))
sys.path.insert(0, str(_repo / "hardware" / "reference" / "mq6-gas-sensor"))
from _cadq_export import export_step, export_assembly
from docgen import substitute_md, substitute_py_comments
import _boxes
import _realized
import hopper_funnel as _funnel
import wago_221 as _wago
import mq6_gas_sensor as _mq6

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
# the box's own `funnel` centre with its brim on the box top, and with_funnel
# measures the top-wall frame against it (the facet's back plane ahead, the
# ±X top corner pods either side, the back wall behind). The funnel is pushed as
# far forward as that frame allows and reaches aft for its capacity, so it may
# CROSS the Y seam — both halves take their share of the cut.
# Air between the funnel's collar frame and the ±X pods it runs beside. CHOSEN, not derived:
# the two are printed in the same piece, so this is clearance for the eye and the deburring
# tool rather than a fit.
hopper_pod_gap = 1.0
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

# --- the side walls' Wago wells ---------------------------------------------
#
# The ten lever nuts this machine splices in are HELD BY THE WALL. There is no tray: a
# well is printed on a wall's inner face and the lug presses into it, which is one part
# fewer, two hold-down bosses fewer, and no plate between the lug and the thing that
# locates it. A lever nut has no mounting hole of its own — it is a free splice — so a
# printed pocket is the only way it is ever held, and the wall is as good a place to
# print one as a plate is.
#
# The lug goes in BUTT-FIRST, pushed onto the wall, ports facing the room. Its
# lever-hinge axis stands on Z and its closed-body height lies along Y, so the +X row
# runs fore and aft down the flank on the narrow face — five abreast in the depth three
# would take lying the other way. The well wraps the butt half on ±Y and ±Z and is open
# inboard, where the wire half stands proud and the levers swing.
#
# The rear half of a 221's depth is blank on every face; ports and levers are all in the
# front half. So the well takes the rear half and grips all four sides of it, at every
# size — including the 221-420, whose two lever rows hinge off the faces a well would
# otherwise wrap.
wago_well_wall = 3.0        # well wall thickness
wago_well_press = 0.15      # per-side press-fit clearance, validated on the valve trays


def wago_stand(size="413"):
    """One lug's own axes in a side wall's frame, as `(y, z, x)` — the closed-body
    height along the row, the lever-hinge axis across it, the wire-entry axis reaching
    inboard."""
    s = _wago.SIZES[size]
    return (s["height"], s["width"], s["depth"])


def wago_engage(size="413"):
    """How far into the well the lug's butt half goes, which is how far the tower
    stands off the wall."""
    return wago_stand(size)[2] / 2.0


def wago_half(size="413"):
    """The well's outer half-extents on the wall, as `(y, z)` — the lug's own half plus
    the wall it is wrapped in and that wall's press clearance."""
    sy, sz, _sx = wago_stand(size)
    return (sy / 2.0 + wago_well_wall + wago_well_press,
            sz / 2.0 + wago_well_wall + wago_well_press)


def wago_swing(size="413"):
    """How far a lug reaches on ±Y with its levers worked — the closed body plus the
    swing off each face that hinges one. The 221-420 hinges on both."""
    sy, _sz, _sx = wago_stand(size)
    rows = _wago.SIZES[size]["rows"]
    return sy + rows * _wago.lever_swing


# What each lug in the +X row costs the flank. Wells sharing a wall face would stand
# neighbours 14.70 apart and a lever standing fully up reaches `wago_swing` — so the row is
# spaced by the LEVER and not by the wall, and a lug can be opened and re-wired where it
# sits. Neighbouring towers stop touching at that spacing; each stands on its own.
wago_lever_clear = 1.0      # air past the swept lever, so its tip does not graze the next lug
wago_pitch = max(2.0 * wago_half("413")[0], wago_swing("413") + wago_lever_clear)

# --- the −X wall's MQ-6 cradle ----------------------------------------------
#
# The combustible-gas sensor stands ON EDGE low in the refrigeration bay, in the open strip
# down the −X flank beside the compressor. R-600a is half again heavier than air: it falls
# off whichever brazed joint let it go and spreads as one layer over the slab, so what the
# sensor owes that layer is HEIGHT, and the floor of this bay is one connected pool — every
# leak site the loop has feeds it. The card sits as low as a 32 mm card stands.
#
# The board carries no mounting hole, so what holds it is a SLOT ITS OWN EDGES SLIDE INTO —
# the same bargain the Wago wells strike, for the same reason. Two rails reach inboard off
# the wall, one under the card's bottom edge and one over its top, and the card goes in
# sideways until its west edge meets the wall: THE WALL IS THE DATUM in X, the grooves in Y
# and Z. The bottom rail's underside is the slab itself, so the cradle comes out of the print
# as a corner bracket in one piece with both faces it stands on, and no fastener is bought.
#
# The can is centred on the card and reaches within half a millimetre of each short edge,
# which is what settles the rest: the long edges are the only ones with material to grip, so
# the rails take those and the card enters from the room rather than from above.
mq6_rail_wall = 3.0         # rail section around the groove
mq6_slot_press = 0.15       # per-side slip in the groove, the wells' own figure
mq6_grip = 5.0              # how much of the card's long edge each groove swallows
# The pins face the card's BACK and the loom lands on them there, so the cheek on that side
# is cut away across the header — this is what the cut leaves either side of the pin field.
mq6_header_relief = 2.0
# The card's own axes in the wall's frame. It stands on edge, so the board's long side is its
# height and its short side is the whole reach inboard off the wall.
mq6_card_x = _mq6.PCB_Y     # 20 — reach inboard, the card's short side
mq6_card_y = _mq6.PCB_T     # 1.6 — the card itself, what the groove grips
mq6_card_z = _mq6.PCB_X     # 32 — height, the card's long side
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
# The band down each ±X wall IS that chain: what a floor body stands off the wall where the
# seam's columns are, so each post, chain and pod seats at full section and the body seats
# flush against them. One name for the reader who is thinking about the band and one for the
# reader thinking about a single boss, and one number under both — an M3 of another length
# moves the chain and the band together.
side_rib_inset = boss_in
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
#   side_wells    the side walls' Wago wells, (side, y, z, size) — one press-fit pocket
#                 per lever nut, on the flank its own cluster stands on
#   floor_bosses  the floor slab's mounting bosses, (x, y, the plane the boss top reaches)
#   west_cradle   the −X wall's MQ-6 card slot, (y, z) — the card's plane and its centre
#   asse_cradle   the −X wall's tap-water cradle, (axis_z, sections, ties, reach_down) — the
#                 axis the trough is struck on, one (y0, y1, apex_x) per section of the chain,
#                 the Y of each tie band, and how far under the axis its flanks run
#   digiten_saddles  the top wall's two flow-meter saddles, (axis_x, axis_z, seat_r, bands) —
#                 the arm axis the Vs are struck on, the barrel they seat, and the run of
#                 each arm one takes
#   tube_anchors  the runs' own seats, one (mid, along, root, seat_r) each — the middle of the
#                 leg a rib is centred on, which way the tube points there, which way the face
#                 it stands on lies, and the section it seats
Box = namedtuple(
    "Box", "inner outer y_joint splits front_ports back_ports east_ports west_ports "
           "funnel pan_rails c14 east_bosses side_wells floor_bosses west_cradle asse_cradle "
           "digiten_saddles tube_anchors")

# What a box is built AROUND: the placed bodies, and every station they put on a wall.
# A pack that does not carry a subsystem yet carries no stations for it, and the wall
# comes out blank there rather than carrying a hole with nothing behind it.
#   placed        {name: (solid, colour)} — the same shape a CadQuery assembly reads
# The rest are the Box fields above, and the box passes them through.
Pack = namedtuple(
    "Pack", "placed front_ports back_ports east_ports west_ports funnel pan_rails c14 "
            "east_bosses side_wells floor_bosses west_cradle asse_cradle digiten_saddles "
            "tube_anchors")
Pack.__new__.__defaults__ = ((), (), (), (), None, (), (), (), (), (), (), (), (), ())


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
# `enclosure_assembly.machine` and `enclosure_assembly.build_enclosure_assembly` carry these
# onto the assembly beside the bounds that module states itself. The ledger lives here
# because `enclosure` cannot import that module back — `machine_of` imports it inside the
# call for the same reason.
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

    The bite is MEASURED, never stated. `_measure_wall_relief` probes this
    corner's own footprint at this depth against the placed contents, so the
    section the post keeps is whatever the pack leaves it — a body may cross the
    post's whole height band and still stand clear of the corner, which is why a
    bounding box cannot answer it. A wall nothing reaches gets no cutter at all.

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


def front_band_free_y(front_face):
    """The FRONT half's free run of the ±X boss-chain bands, as `(y0, y1)` — the run
    `east_band_free_y` says this half has and is not.

    Same two facts either side of the seam: `_z_pod` runs its post from the socket it carries
    down to the floor, so a Z station on a ±X wall stands in that band FLOOR TO CEILING, and
    what is between two of them is the wall's own air. The front column's are the front-wall
    corner and the aft end of its own lip, and a body hung low on either flank outside this
    run is a body standing in one of those posts.

    IT TAKES THE FRONT FACE because it cannot state it. The back half's two ends are both
    struck on planes the box states about itself — `y_seam` and `rear_plane_y` — but the front
    wall stands off whatever the pack puts nearest it, so a caller reading this before the box
    is sized has to say what that is. Everything after it is the same stated chain `_dims`
    builds the wall on."""
    iy0 = front_face - interior_clearance - front_seam_clear
    yf = iy0 + wall + socket_bore_dia / 2.0
    yfr = y_seam - wall - z_lip_y_margin - socket_r
    return (yf + socket_r, yfr - socket_r)


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
    # What the pack still has to earn is the clearance. A body on the slab is held one
    # `side_rib_inset` off the ±X walls at the depths the seam's columns stand there —
    # `_seam_furniture_spans`, the spans `_chain_spans_clear` reads and the ceiling's pod
    # stack takes below. Between those stations the band is the wall's own air, and a body
    # clear of all of them answers on `cxmax`.
    ix0, ix1 = interior_x()
    iy0_probe = cymin - interior_clearance - front_seam_clear
    band_spans = _seam_furniture_spans(
        (ix0, ix1, iy0_probe, rear_plane_y, czmin, czmax), y_seam)
    floor = [b for b in bbs
             if b.zmin < wall + 1e-6
             and any(b.ymin < sy1 and b.ymax > sy0 for sy0, sy1 in band_spans)]
    wide_need = max([cxmax + interior_clearance, -(cxmin - interior_clearance)]
                    + [b.xmax + side_rib_inset for b in floor]
                    + [-(b.xmin - side_rib_inset) for b in floor])
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
               pack.side_wells, pack.floor_bosses, pack.west_cradle, pack.asse_cradle,
               pack.digiten_saddles, pack.tube_anchors)


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
    `enclosure_assembly`'s placement of the reference body, so the housing and
    the part in it cannot land on two different centres."""
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

def _hopper_frame(inner, outer):
    """What the top wall has left to give the collar, `(x_lo, x_hi, y_lo, y_hi)`: BEHIND the
    display facet's own back plane, inboard of the ±X top corner pods, and ahead of the back
    wall.

    THE FRONT IS A DIFFERENT KIND OF EDGE FROM THE OTHER THREE. On those three the frame runs
    out into a free edge, and the collar stands one `hopper_funnel.brim_margin` inside it: the
    flange overhangs the collar by `brim_overhang` to catch the wall and hold the funnel out of
    the box, and the margin is the wider of the two, so a full overhang's width of top wall
    still remains outboard of the brim's edge. Forward the wall runs straight on into the
    display housing — `display_facet_thickness` of solid slab between the facet's back plane
    and its 45° face — and that slab is what the brim's front flange lands on. The front's
    requirement is `hopper_front_ledge`, the top wall kept between the housing's back plane and
    the throat itself, and it stands in this frame. `with_funnel` asks the margin of the three
    free edges."""
    ix0, ix1, _iy0, iy1, _iz0, _iz1 = inner
    return (ix0 + boss_in + hopper_pod_gap,            # clear of the top-left pod
            ix1 - boss_in - hopper_pod_gap,            # clear of the top-right pod
            facet_back_y(outer) + hopper_front_ledge,  # behind the facet's housing
            iy1 - wall)                                # ahead of the back wall


def _hopper_hole(centre):
    """Rectangle (x0, x1, y0, y1) of the funnel opening in the top wall: the placed funnel's
    collar — hopper_funnel.py's own dims at the box's own `funnel` centre.

    The funnel is pushed as far FORWARD as `_hopper_frame` allows, and reaches aft for
    whatever plan area its capacity needs — so the opening may cross the Y seam. Both halves
    take their share of the cut and the collar bridges it; what the seam gives up there is its
    top-wall lip over the hole's span, which the mouth shelf's own relief already accounts
    for (`_hopper_cut`).

    Plan arithmetic off one centre. `with_funnel` states what that collar owes its frame."""
    cx, cy = centre
    return (cx - _funnel.collar_w / 2.0, cx + _funnel.collar_w / 2.0,
            cy - _funnel.collar_d / 2.0, cy + _funnel.collar_d / 2.0)


def with_funnel(box, centre):
    """`box` carrying the funnel collar's plan centre, and the three bounds that centre states
    against the frame the top wall has left.

    SEATING THE THROAT IS MEASURING IT, and this is the one door: a Box carries a funnel centre
    only by coming through here. The three readings are plan arithmetic on `centre` and the
    box's own two shells, taken the moment the centre is known and owing nothing to the cut the
    throat is later punched with.

    THE COLLAR IS SEATED WHICHEVER WAY THEY READ. One outside its frame is cut where it stands,
    so the throat that runs into a pod or off the facet is in the pieces to look at, beside the
    row that names it."""
    x0, x1, y0, y1 = _hopper_hole(centre)
    lims = _hopper_frame(box.inner, box.outer)
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
    return box._replace(funnel=centre)


def _hopper_cut(inner, outer, centre):
    """The funnel throat punched clean through the top wall — one wall deeper
    than the ceiling, so the Y-seam's top-wall lip/mouth shelf (hanging one
    wall below it) is relieved across the hole span the seam crosses.

    The opening is the collar, whole: the basin is a full rectangle and the wall carries
    nothing over the tap-water sequence that the throat has to be cut around."""
    x0, x1, y0, y1 = _hopper_hole(centre)
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
    return Box(inner, outer, y_joint, (zjf, zjb), (), (), (), (), None, (), (), (), (), (), (),
               None, None, ())


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
        front = front.cut(_hopper_cut(inner, outer, box.funnel))
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
        back = back.cut(_hopper_cut(inner, outer, box.funnel))
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


def _side_wells(solid, inner, stations, y0, y1, z0, z1):
    """A side wall's Wago wells added to a PIECE, for the stations inside the depth and
    height band that piece owns — the same band test `_east_bosses` makes, so a well lands
    whole in the piece whose wall carries it.

    Each station is `(side, y, z, size)`: which flank the well is grown on (+1 east,
    −1 west), its centre on that wall, and the 221 it takes.

    The tower stands off the wall's inner face and the cavity is cut from that face
    outward past its own end, so the pocket opens INBOARD and bottoms on the wall. What
    the lug meets at the bottom of its travel is the wall itself, not a printed floor —
    the wall is the datum, so the ports stand at a height the wall states."""
    for side, sy, sz, size in stations:
        if not (y0 <= sy <= y1 and z0 <= sz <= z1):
            continue
        face = inner[1] if side > 0 else inner[0]
        engage = wago_engage(size)
        half_y, half_z = wago_half(size)
        stand_y, stand_z, _sx = wago_stand(size)
        # inboard is −X on the east wall and +X on the west, so the tower and the pocket
        # both run from the wall towards the room
        tower = sorted((face, face - side * engage))
        pocket = sorted((face, face - side * (engage + 1.0)))
        solid = solid.fuse(_ybox(tower[0], tower[1],
                                 sy - half_y, sy + half_y,
                                 sz - half_z, sz + half_z))
        solid = solid.cut(_ybox(pocket[0], pocket[1],
                                sy - (stand_y / 2.0 + wago_well_press),
                                sy + (stand_y / 2.0 + wago_well_press),
                                sz - (stand_z / 2.0 + wago_well_press),
                                sz + (stand_z / 2.0 + wago_well_press)))
    return solid


def _west_cradle(solid, inner, stations, y0, y1, z0, z1):
    """The −X wall's MQ-6 card slot added to a PIECE, for the stations inside the depth and
    height band that piece owns — the same band test `_side_wells` makes.

    Each station is `(y, z)`: the card's own plane, and its centre in height. Nothing else is
    passed, because nothing else varies — the slot is one board's envelope and one slip fit,
    read off the reference solid.

    Two rails reach inboard off the wall's inner face, grooved on the faces they turn toward
    each other, and the card slides west between them until its west edge meets the wall.
    What stops it is the wall itself, the way a lever nut bottoms in its well — so the card's
    reach into the room is the board's own short side and not a number typed here. The bottom
    rail's underside is the slab, which is what makes this a corner bracket rather than a
    shelf: it is in one piece with both faces it stands on.

    THE BACK CHEEK IS CUT ACROSS THE HEADER. The pins face the card's back and the loom lands
    on them there, so a cheek running unbroken past them is a cheek nothing can reach through.
    The cut is struck on the pin field's own reach off the wall and runs both rails, because
    which of the two the header ends up in is the card's turn to state and not this slot's."""
    span, _off = _mq6.header_span()
    for sy, sz in stations:
        if not (y0 <= sy <= y1 and z0 <= sz <= z1):
            continue
        cx0, cx1 = inner[0], inner[0] + mq6_card_x
        gy0 = sy - mq6_card_y / 2.0 - mq6_slot_press
        gy1 = sy + mq6_card_y / 2.0 + mq6_slot_press
        ry0, ry1 = gy0 - mq6_rail_wall, gy1 + mq6_rail_wall
        zb, zt = sz - mq6_card_z / 2.0, sz + mq6_card_z / 2.0
        solid = solid.fuse(_ybox(cx0, cx1, ry0, ry1, zb - mq6_rail_wall, zb + mq6_grip))
        solid = solid.fuse(_ybox(cx0, cx1, ry0, ry1, zt - mq6_grip, zt + mq6_rail_wall))
        # Both grooves run out past the rails' inboard end, so the card enters from the room.
        solid = solid.cut(_ybox(cx0 - 1.0, cx1 + 1.0, gy0, gy1, zb, zb + mq6_grip + 1.0))
        solid = solid.cut(_ybox(cx0 - 1.0, cx1 + 1.0, gy0, gy1, zt - mq6_grip - 1.0, zt))
        hx = (cx0 + cx1) / 2.0
        solid = solid.cut(_ybox(hx - span - mq6_header_relief, hx + span + mq6_header_relief,
                                ry0 - 1.0, gy0,
                                zb - mq6_rail_wall - 1.0, zt + mq6_rail_wall + 1.0))
    return solid


# --- the tap-water chain's cradle on the −X wall ---------------------------
#
# The trough's own section, and what it spends on either side of the chain's axis.
# How far the trough's upper flank runs off the axis. It is SHORT: the chain's own top flat
# stands one `clearance-floor` under the ceiling, so a lip carried up to that flat's arris is a
# lip standing in the only air a tie could have used, and the strap climbs past this lip on its
# way over the chain. The lower flank's reach is not stated here at all — the station carries it,
# struck on the chain's own lowest arris, because a trough deeper than the body it holds is PETG
# holding air.
asse_cradle_up = 9.0
asse_v_half = 60.0          # half the V's included angle, off the axis plane
asse_cradle_lip = 4.0       # block carried past the flanks, so the V cut is never clipped
# THE STRAP'S CAVITY THROUGH THE TROUGH'S BACK, closed on every side but its two mouths.
#
# STRAIGHT ON THE WEST, THE TROUGH'S OWN V ON THE EAST. The V's apex stands closest to that
# straight, so the cavity is narrowest at the axis and flares to both mouths: each mouth opens
# `wall / sin 60°` off its lip's own arris, on the block's face, and at the axis the flare
# leaves a strap pushed through the room to turn the vertex by cutting its corner.
#
# It is ONE opening from the first tie band to the last, half a cavity past each. The two bands
# are what it has to serve, so the block's back is solid fore and aft of them, and what is left in
# the one opening draws out end to end.
#
# ITS TWO FLANKS ARE BOTH ONE `wall`. The cavity is what is LEFT between them — a `wall` off the
# trough on the east and a `wall` off the side wall's own inner face on the west — so its width is
# a remainder and not a number, and every face of it is the section the rest of this box is.

# --- what a strap is, wherever one is cut for on this box --------------------
#
# Every cavity on this wall carries the same fastener, so its section is stated once here and the
# features read it. `enclosure_assembly.ASSE_TIE_T` is the same strap's THICKNESS, and it is stated
# over there because what it sets is the deck's own storey rather than anything printed.
tie_strap_w = 2.5           # the strap, across its width
tie_strap_t = 1.0           # and through its thickness
tie_cav_buffer = 1.0        # the room a cavity carries over the strap
tie_cav_w = tie_strap_w + tie_cav_buffer
# Solid either side of a cavity, ALONG the run. A cavity is a hole through a rib, and this is what
# the rib keeps of itself at each end of that hole.
tie_cav_wall = 3.0


def _asse_v(x_apex, z_axis, y0, y1, up, dn, x_east):
    """The room the chain lies in: a 120° V, apex west on its own axis, open east.

    ONE SHAPE FOR EVERY SECTION. Read off a hex's corner it lies on two whole flats; read off a
    round one's tangent it lies on two lines; and either way the section that sits deepest is
    the section that is widest, which is what makes the steps between them faces square to the
    axis rather than anything drawn here."""
    run = 1.0 / math.tan(math.radians(asse_v_half))
    return (
        cq.Workplane("XZ")
        .polyline([(x_apex, z_axis),
                   (x_apex + up * run, z_axis + up),
                   (x_east, z_axis + up),
                   (x_east, z_axis - dn),
                   (x_apex + dn * run, z_axis - dn)])
        .close()
        .extrude(-(y1 - y0))
        .val()
        .translate((0.0, y0, 0.0))
    )


def _asse_cradle(solid, inner, station, y0, y1, z0, z1):
    """The tap-water chain's cradle fused onto the −X wall, if this piece owns its band.

    THE CHAIN IS MADE UP BY HAND AND THIS IS WHAT THAT COSTS. Five fittings on one axis, each
    threaded to its neighbour "snug + 1 turn", so neither the length of the run nor the clock any
    one of them lands at is a number this wall can know. What the wall can know is the SECTION
    each one presents about the axis, because that is the fitting's own — so the trough is cut to
    each in turn, the steps between them catch the barrel fore and aft, and the fit across the V
    is a slip and not a socket.

    WHAT A TIE CAN AND CANNOT DO HERE. A tie is a closed loop, and a loop round this chain has to
    pass over its top flat — so the storey the chain lies on is struck to leave that channel under
    the top wall, and the wall itself is never cut for it
    (`enclosure_assembly.DECK_CEILING_CLEAR`). The loop runs down the CAVITY through the back of
    this trough, out under the block, east beneath the barrel, up its east flank, over the top flat
    through that channel, and back into the cavity. So it closes round the chain and the trough's
    own back together, and what it pulls is the chain into the V.

    THE CAVITY IS CLOSED ON EVERY SIDE BUT ITS TWO MOUTHS. It stands west of the apex with
    one `wall` of PETG between it and the trough, so at no station is it anything but a hole
    through solid material, and a strap in it stays where it was put.

    THE BLOCK'S TOP FACE HANGS. Printed ceiling-down that face is a horizontal soffit over the
    lane, and it takes print support the way the drip tray's rails do. The cavity is one opening
    from the first tie band to the last, and what is left in it draws out end to end.

    NOTHING HERE HOLDS THE CHAIN UP. The V does that, on two faces of a section machined into the
    part; the ties only shut its mouth. Cut every tie and the chain still lies where it lies,
    which is the whole point of putting the load on printed geometry and the preload on nylon."""
    if not station:
        return solid
    z_axis, sections, ties, dn = station
    up = asse_cradle_up
    run = 1.0 / math.tan(math.radians(asse_v_half))
    if not (y0 <= sections[0][0] and sections[-1][1] <= y1):
        return solid                       # a piece that does not own the whole run builds none
    if not (z0 <= z_axis - dn and z_axis + up <= z1):
        return solid
    for sy0, sy1, apex, seat_r, x_axis in sections:
        if seat_r is None:
            east = apex + dn * run + asse_cradle_lip
            solid = solid.fuse(_ybox(inner[0], east, sy0, sy1, z_axis - dn, z_axis + up))
            solid = solid.cut(_asse_v(apex, z_axis, sy0, sy1, up, dn, east + 1.0))
            continue
        # A ROUND SECTION LIES IN A BORE, cut out of the same block on the same storey the V takes.
        # The block's own top face crosses the arc INSIDE its widest point, so the two meet in a
        # wedge rather than along a tangent — which is what a feather is, and what a lip is not.
        # Below the axis the block runs past the circle entirely and the arc closes on the block's
        # east face at a right angle.
        solid = solid.fuse(_ybox(inner[0], x_axis, sy0, sy1, z_axis - dn, z_axis + up))
        solid = solid.cut(_ycyl(seat_r, x_axis, z_axis, sy0, sy1))
    # THE STRAP'S CAVITY, cut after every section is fused so a neighbour's block cannot fill it
    # back in. Struck on the DEEPEST section's apex, which is the barrel's: that V stands furthest
    # west, so a cavity clear of it by one `wall` is clear of the other two by more and the
    # web comes out no thinner than stated at any station.
    for ty in ties:
        if not (sections[0][0] <= ty <= sections[-1][1]):
            raise ValueError(
                f"_asse_cradle: tie band {ty:.2f} falls outside the trough's run "
                f"[{sections[0][0]:.2f}, {sections[-1][1]:.2f}]. The cavity a strap passes through "
                f"is the trough's whole length, so a band off either end has no cavity at all.")
    return solid.cut(_asse_tie_cavity(min(w for _y0, _y1, w, _r, _a in sections), inner[0], z_axis,
                                      min(ties) - tie_cav_w / 2.0,
                                      max(ties) + tie_cav_w / 2.0, up, dn))


def _asse_tie_cavity(x_apex, x_wall, z_axis, y0, y1, up, dn):
    """The strap's cavity: STRAIGHT on the west, the trough's own V on the east.

    Five points and one cut. The V's apex stands closest to that straight, so the cavity comes out
    narrowest in the middle and flared at both mouths — which is the reach where a hand needs it
    and the room to turn the vertex where a strap needs that, out of one shape rather than out of a
    chamfer and a round.

    Both ends run one millimetre past the block's faces, so each mouth is cut open rather than
    closed by a plane coincident with the face it opens on."""
    run = 1.0 / math.tan(math.radians(asse_v_half))
    x_in = x_apex - wall / math.sin(math.radians(asse_v_half))   # a `wall` west of the trough
    x_w = x_wall + wall                                          # and a `wall` off the side wall
    over_up, over_dn = up + 1.0, dn + 1.0
    return (
        cq.Workplane("XZ")
        .polyline([(x_w, z_axis + over_up),
                   (x_in + over_up * run, z_axis + over_up),
                   (x_in, z_axis),
                   (x_in + over_dn * run, z_axis - over_dn),
                   (x_w, z_axis - over_dn)])
        .close()
        .extrude(-(y1 - y0))
        .val()
        .translate((0.0, y0, 0.0))
    )


# --- the flow meter's two saddles, off the top wall -------------------------
#
# A BORE, CONCENTRIC WITH THE BARREL IT TAKES. The arms are round, so the seat is round: half a
# cylinder on the arm's own axis, opening downward, and the arm comes straight up into it.
#
# THE ARC STOPS ON THE ARM'S OWN AXIS PLANE AND THE RIB CARRIES ONE `wall` PAST ITS WIDEST POINT.
# That plane is where the arc is widest, so the rib's own flanks stand `seat_r + wall` off the axis
# and each lip comes out a flat strip one `wall` across. An arc carried past its widest point runs
# out to nothing against the flank and leaves a feather no nozzle can lay down.
digiten_saddle_wall = 3.0
# ITS LENGTH ALONG THE ARM IS ITS CAVITY'S. One strap crosses each saddle, so the rib is that
# strap's cavity with `tie_cav_wall` of itself at each end of it, and the band `digiten_saddles`
# reads off the barrel is what that rib is centred in.
digiten_saddle_len = tie_cav_w + 2.0 * tie_cav_wall
# The strap's cavity through each saddle, over the bore. Its floor is the SEAT'S OWN ARC offset out
# by one `wall` — concentric, so the web reads `wall` all the way round — and ITS CEILING IS THE
# TOP WALL'S OWN INNER FACE. The channel is everything left between them, deepest over the crown
# and flaring as the arc falls away to each mouth.
#
# The strap bears straight on that face and what stands over it is `wall`: the top wall's own
# section, which is already there. A plate of this rib's under it would be a second `wall` doing
# the first one's job.


def _digiten_bore(x_axis, z_axis, r, y0, y1, reach):
    """A saddle's own room: half a cylinder on the arm's axis, opening DOWNWARD, and the whole of
    the room under it.

    The arc runs from one axis-plane lip round the crown to the other, and the box under it carries
    the opening down clear of the rib — so what this cuts is the barrel's room and the air it comes
    up through, and the rib is left as a half-round hood with a flat lip on each side."""
    bore = cq.Solid.makeCylinder(r, y1 - y0, cq.Vector(x_axis, y0, z_axis), cq.Vector(0, 1, 0))
    under = _ybox(x_axis - r, x_axis + r, y0, y1, z_axis - r - reach, z_axis)
    return bore.fuse(under)


def _digiten_saddles(solid, inner, station, y0, y1, z0, z1):
    """The flow meter's two saddles hung off the top wall, for the piece that owns the ceiling.

    ONE PER ARM AND NONE OVER THE BODY. The round body reaches to within a hair of the top wall
    and the two collet barrels leave the best part of a centimetre under it, so the arms are the
    only part of this meter a printed feature can reach without the storey moving.

    THE SEAT IS A BORE AND NOT A V, because the thing it takes is round. Half a cylinder on the
    barrel's own axis, `seat_r` across, so the seat and the barrel share a surface all the way round
    instead of touching on two lines. It stops on the barrel's own axis plane — the widest the arc
    gets — and the rib carries `digiten_saddle_wall` past that, so each lip is a flat strip one wall
    across. Carried any further round, the arc would run out to nothing against the flank.

    THE STRAP IS THE LOAD PATH. A bore that opens downward carries nothing, so the two ties here
    are not the trough's ties: cut them and the meter comes out of its saddles. What is hanging is
    a purchased part of a few tens of grams on two nylon straps.

    Printed ceiling-down the rib stands up off the bed and the bore's crown is the deepest thing in
    it, facing up all the way round — so there is no overhang anywhere in this feature and no
    support in it to pick out."""
    if not station or z1 < inner[5] - 1e-6:
        return solid
    x_axis, z_axis, seat_r, bands = station
    reach = seat_r + digiten_saddle_wall
    for by0, by1 in bands:
        if not (y0 <= by0 and by1 <= y1):
            continue
        if by1 - by0 < digiten_saddle_len - 1e-6:
            raise ValueError(
                f"_digiten_saddles: the barrel leaves {by1 - by0:.2f} mm between the body's rim "
                f"and the collet's ring, and a saddle is {digiten_saddle_len:.2f} — one strap's "
                f"cavity with `tie_cav_wall` at each end of it. Either the band gives way "
                f"(`DIGITEN_BODY_CLEAR`, `DIGITEN_COLLET_FREE`) or the rib does.")
        mid = (by0 + by1) / 2.0
        sy0, sy1 = mid - digiten_saddle_len / 2.0, mid + digiten_saddle_len / 2.0
        z_crown = z_axis + seat_r + wall          # one `wall` over the bore's own crown
        if inner[5] - z_crown < tie_strap_t + 1e-6:
            raise ValueError(
                f"_digiten_saddles: a `wall` off the bore's crown leaves {inner[5] - z_crown:.3f} "
                f"mm under the top wall's inner face, and the strap is {tie_strap_t:.3g} thick. The "
                f"storey the meter stands on is what gives way here "
                f"(`enclosure_assembly.DECK_CEILING_CLEAR`), not the wall.")
        # THE CAVITY IS WHAT IS NEVER FUSED, and nothing is cut for it. The rib is ONE box its whole
        # length up to `z_crown`, the two ends carried on up to the top wall, and ONE bore through
        # all of it. What the ends do not span IS the strap's channel — so it has no floor to draw,
        # no cut to make it, and no face for either to graze.
        #
        # The lower box runs the rib's whole length so the seat's own lip is ONE edge, and the rib
        # is UNIFIED before it joins the piece. A fuse imprints the seam of every solid that went
        # into it, so a rib fused straight onto the wall carries its lip in as many pieces as it
        # was laid down in — three here — and its bore in as many again.
        cy0, cy1 = mid - tie_cav_w / 2.0, mid + tie_cav_w / 2.0
        rib = _ybox(x_axis - reach, x_axis + reach, sy0, sy1, z_axis, z_crown)
        for ry0, ry1 in ((sy0, cy0), (cy1, sy1)):
            rib = rib.fuse(_ybox(x_axis - reach, x_axis + reach, ry0, ry1, z_crown, inner[5]))
        rib = rib.cut(_digiten_bore(x_axis, z_axis, seat_r, sy0, sy1, reach))
        solid = solid.fuse(rib.clean() if hasattr(rib, "clean") else rib)
    return solid


# --- the tube anchors, one pattern wherever a wall can reach a run ----------
#
# THE SAME 120° V AGAIN, on the one body in this machine there are twenty of. A run is held at its
# two ends by the collets it is pushed into and by nothing between them, so what it does between
# them is sag — and a run that sags is not on the centreline `lines-clear` cleared. An anchor is a
# stop on that span: a seat the tube lies in, and a strap's cavity behind the seat, standing on
# whichever face of the box comes near enough to reach it.
#
# A ROUND SEAT ON A ROUND BODY. The section is struck in the anchor's own frame — `u` along the
# tube, `n` from the tube toward the face the rib roots on — and the seat is a bore concentric
# with the tube, half of one, taken from the crown round to the tube's own AXIS PLANE. Stopping
# there is what keeps the lip printable: an arc run past its widest point closes back on the tube
# and ends in a feather, and an arc stopped on the axis plane ends in a flat face one `wall` wide.
#
# EVERY THICKNESS IN IT IS ONE `wall`. The rib reaches `seat_r + wall` off the axis, so the lip is
# a wall-wide strip; the cavity's floor is the seat's own arc offset one `wall`, so the web is a
# half-annulus of that thickness at every station of it; the roof stands one `wall` under the face
# the rib roots on. Nothing between them is stated — the strap's channel is what is left.
#
# THESE PIECES ARE POPULATED INVERTED ON THE BENCH. A seat hanging off the top wall is an
# upward-opening cradle at the moment a tube is laid in it and its strap threaded.
#
# ITS LENGTH ALONG THE RUN IS ITS CAVITY'S, the bargain `digiten_saddle_len` strikes: one strap
# crosses one anchor, so the rib is that strap's cavity with `tie_cav_wall` of itself at each end.
tube_anchor_len = tie_cav_w + 2.0 * tie_cav_wall

# Which interior face each root direction names. The anchor states no height of its own: it is
# handed the tube, and the wall it stands on is where its rib stops.
_ROOT_FACE = {(-1, 0, 0): 0, (1, 0, 0): 1, (0, -1, 0): 2,
              (0, 1, 0): 3, (0, 0, -1): 4, (0, 0, 1): 5}


def _anchor_plane(origin, u, n):
    """The anchor's own workplane — profile drawn in (`t`, `n`), extruded along the tube.

    `t = n × u` rather than `u × n`, so the workplane's second axis comes out as `n` itself and a
    profile point's second coordinate is its own distance toward the root face."""
    t = (n[1] * u[2] - n[2] * u[1], n[2] * u[0] - n[0] * u[2], n[0] * u[1] - n[1] * u[0])
    return cq.Plane(origin=cq.Vector(*origin), xDir=cq.Vector(*t), normal=cq.Vector(*u))


def _anchor_bore(origin, u, r, length):
    """The seat — a cylinder on the tube's own axis.

    The rib stands entirely on the root side of the axis plane, so a whole cylinder cut from it
    takes exactly the half the seat is and needs no half-space to trim it."""
    return cq.Solid.makeCylinder(r, length, cq.Vector(*origin), cq.Vector(*u))


def _anchor_rib(origin, u, n, length, reach, b0, b1):
    """The material the seat and its cavity are cut out of, root face to the seat's own flanks."""
    return (
        cq.Workplane(_anchor_plane(origin, u, n))
        .polyline([(-reach, b0), (reach, b0), (reach, b1), (-reach, b1)])
        .close()
        .extrude(length)
        .val()
    )


def _tube_anchors(solid, inner, stations, y0, y1, z0, z1):
    """Every tube anchor whose whole rib this piece owns.

    A station carries the tube and only the tube — where its axis runs, which way it points, what
    it seats on — and the box carries the face. So an anchor moves when its run moves and stops
    where the wall stops. A piece that owns only part of a rib builds none of it, the way every
    other station on these walls behaves.

    THE CAVITY IS A REMAINDER: the rib stands one `wall` over the bore's crown down its whole
    length and only its two ends carry on up to the face it roots on, so the strap's channel is
    the room between those ends. That face is the channel's roof and the crown is its floor —
    neither is drawn, and there is no cut anywhere in it to graze a face with.

    THE STRAP CLOSES ROUND THE TUBE AND THE RIB'S OWN BACK TOGETHER: through the cavity, out one
    flank, round the far side of the tube and back in the other. What it pulls is the tube into
    the bore, and the bore is what says where the tube is."""
    if not stations:
        return solid
    for mid, u, n, seat_r in stations:
        face = _ROOT_FACE.get(tuple(int(round(c)) for c in n))
        if face is None:
            raise ValueError(
                f"_tube_anchors: root direction {n} names no interior face. An anchor stands on "
                f"one of the box's six faces, and that face is what its rib stops on.")
        b_root = (inner[face] - mid[face // 2]) * (1.0 if face % 2 else -1.0)
        reach = seat_r + wall              # the lip's outer edge
        b_crown = seat_r + wall            # one `wall` over the bore's own crown
        if b_root - b_crown < tie_strap_t:
            raise ValueError(
                f"_tube_anchors: a `wall` off the bore's crown leaves {b_root - b_crown:.3f} mm "
                f"under the face this rib roots on, and the strap is {tie_strap_t:.3g} thick. What "
                f"gives way here is the run's own lane, not the wall: route it further off that "
                f"face, or anchor it to another one.")
        origin = tuple(mid[k] - u[k] * tube_anchor_len / 2.0 for k in range(3))
        # The rib's own extent, so a piece that owns part of it builds none of it.
        t = (n[1] * u[2] - n[2] * u[1], n[2] * u[0] - n[0] * u[2], n[0] * u[1] - n[1] * u[0])
        span = [[origin[k] + u[k] * s + n[k] * b + t[k] * aa
                 for k in range(3)]
                for s in (0.0, tube_anchor_len)
                for b in (0.0, b_root)
                for aa in (-reach, reach)]
        if not (y0 <= min(p[1] for p in span) and max(p[1] for p in span) <= y1
                and z0 <= min(p[2] for p in span) and max(p[2] for p in span) <= z1):
            continue
        # THE CAVITY IS WHAT IS NEVER FUSED, and nothing is cut for it. The rib is ONE box its
        # whole length up to `b_crown`, the two ends carried on up to the face it roots on, and
        # ONE bore through all of it. What the ends do not span IS the strap's channel — so it has
        # no floor to draw, no cut to make it, and no face for either to graze. The face the rib
        # roots on is its roof, and a plate of our own under that face would be a second one.
        #
        # The lower box runs the rib's whole length so the seat's own lip is ONE edge, and the rib
        # is UNIFIED before it joins the piece. A fuse imprints the seam of every solid that went
        # into it, so a rib fused straight onto the wall carries its lip in as many pieces as it
        # was laid down in — three here — and its bore in as many again.
        rib = _anchor_rib(origin, u, n, tube_anchor_len, reach, 0.0, b_crown)
        for s0, s1 in ((0.0, tie_cav_wall), (tie_cav_wall + tie_cav_w, tube_anchor_len)):
            end = tuple(origin[k] + u[k] * s0 for k in range(3))
            rib = rib.fuse(_anchor_rib(end, u, n, s1 - s0, reach, b_crown, b_root))
        rib = rib.cut(_anchor_bore(origin, u, seat_r, tube_anchor_len))
        solid = solid.fuse(rib.clean() if hasattr(rib, "clean") else rib)
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
    # The +X wall's Wago wells, on whichever piece holds each one's station. After the
    # bosses for the same reason those go after the seam columns: a pocket cut here is a
    # pocket nothing later fuses back in.
    piece = _side_wells(piece, inner, box.side_wells, ylo, yhi, zlo, zhi)
    # The floor slab's, on whichever piece holds each one's plan station. Only the bottom
    # pieces have a slab to stand one on, and `_floor_bosses` drops any station outside.
    piece = _floor_bosses(piece, inner, box.floor_bosses, ylo, yhi, zlo, zhi)
    # The −X wall's card slot, last of all: its bottom rail lands on the same slab those posts
    # rise from, so cutting its grooves after them is what keeps a groove a groove.
    piece = _west_cradle(piece, inner, box.west_cradle, ylo, yhi, zlo, zhi)
    # And the tap-water chain's, on the same wall a storey up. After the tray's rails, whose
    # band it stands over, and last like every other pocket: its tie slots are cut out of the
    # trough this fuses, so nothing may fuse into them afterwards.
    piece = _asse_cradle(piece, inner, box.asse_cradle, ylo, yhi, zlo, zhi)
    # And the flow meter's two saddles off the same piece's ceiling.
    piece = _digiten_saddles(piece, inner, box.digiten_saddles, ylo, yhi, zlo, zhi)
    # And the runs' own anchors, on whichever face each one stands nearest. Last, for the same
    # reason the trough is: every one of these is a rib with a cavity cut through it.
    piece = _tube_anchors(piece, inner, box.tube_anchors, ylo, yhi, zlo, zhi)
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
    alike — one box description in, four pieces out.

    DRAWING A PIECE TAKES NO READING. Every bound the box states is in the ledger before this
    runs — `_dims` states its own as it sizes the shells, `with_funnel` states the throat's as
    it seats the centre — so the four pieces are a pure function of the Box and a piece handed
    back unbuilt is a piece nothing on the card was waiting for. That is what lets `_realized`
    keep them: a build that moves a body inside the walls moves neither the box, which is its
    stated size, nor the code that cuts it, and a station moves only when the body carrying it
    does."""
    cache = {}
    pieces = {name: _realized.realized(
                  _realized.key(__name__, box, name),
                  lambda n=name: build_piece(box, *n.split("-"), halves_cache=cache))
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


def stated_box(pack):
    """The box at `appliance_width` × `rear_plane_y` × `appliance_height`, with `pack` measured
    against it — the description `build_pieces` turns into the four printable pieces.

    THE PACK DOES NOT SIZE IT. Where the bodies stand decides what `_dims` puts in `BOUNDS`,
    and a pack that reaches past a wall gets that wall drawn through it, a red row saying by
    how much, and a clash in `pack-closes` at the body that overran. Moving a body moves the
    reading, never the wall."""
    return _dims(pack)


def machine_of():
    """The machine's pack and the box around it.
    `hardware/manifold-layout/enclosure_assembly.py` places the bodies and seats the wall
    stations, so both come from there and the box this prints is the box that pack stands in.

    Imported here rather than at module scope so that enclosure_assembly, which builds its
    own assembly around these walls, is not importing a module that is importing it back."""
    sys.path.insert(0, str(_repo / "hardware" / "manifold-layout"))
    import enclosure_assembly
    _assy, pack, box = enclosure_assembly.machine()
    return pack, box


def _report_bounds():
    """Every bound in the ledger that is open, and nothing when they all hold.

    The card `enclosure_assembly` writes is the committed account of these; this is the same
    reading for whoever ran this module on its own, where there is no card."""
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
