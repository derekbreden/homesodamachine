"""Thin Edition enclosure — a tall, narrow PETG box, split into four printable
pieces (front/back × bottom/top) that telescope and cross-pin together.

WIDTH, HEIGHT and DEPTH are all BOUNDS, not consequences — `appliance_width` struck
symmetric about x = 0, `appliance_height` from the floor slab's underside to the top
wall's outer face, and `rear_plane_y` from the front wall to the back. The contents do
not set them; they have to fit inside, and `_dims` measures every one of them against
the pack and enters the reading in `BOUNDS`. The box comes out at its stated size
either way, so a pack that overran it gets a wall drawn through it.

Three bodies stand on the floor slab — the compressor and the condenser side by side
across the front, and the cold core behind them. A boss is a pipe `2 * socket_r` across
and the same TALL, so what the ±X band costs a body is a question about the body's own
height as much as its depth: it is held one `side_band_inset` off the wall where it meets
one in both, and beside one — over or under one — the band is the wall's own air. The cold
core meets the chain and is held off it; the compressor stands under the front column's
collars and the condenser is not on the slab at all. The core is the widest of the three
even yawed a quarter turn (`enclosure_assembly.FOAM_YAW`), which is what puts its 181 mm
short face across the machine instead of its 283 mm long one. The pack is placed by
`../../../manifold-layout/enclosure_assembly.py`. Features:

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
    wall with a screw clearance through it. The
    FRONT piece's lip carries the SOCKET (faucet shell-bottom idiom): a
    collar bored to receive the plug, open on its +Y face so the plug drops
    in as the pieces close, with a ruthex M3 heat-set at the deep end.
  * A bottom↔top split per column — the same joint rotated 90°, at a
    different height each side of the Y seam (the seams stagger like a
    brick bond; the front pair joins, the back pair joins, then the front
    assembly telescopes into the back). The BOTTOM pieces carry the lip — a
    3-sided band (their outer ±Y wall + both side walls, stopping short of
    the Y-seam overlap) telescoping +Z into the top pieces — with the
    socket collars; the TOP pieces carry the pins. Four X-axis screws cross
    each seam (one per side wall per Y column: front pins at the front-wall
    corners, back pins just behind the Y-seam mouth).

The walls stand off the bodies rather than on them — one boss chain at the ±X
walls, one wall at the back — because a body on the floor spans the interior wall
to wall, so a wall on its face would leave the seam machinery nowhere to stand.
The cold core seats flush against the seams instead, and stands flat on the floor slab — its bottom cap's lid is a plane and
every cap screw is down in a counterbore, so nothing goes under it. The ±X bands'
own seam furniture fences it sideways, the back Z seam's lip behind, and the floor's
two core lugs (`_core_fence`) ahead. The floor that core stands on is flat: the
Y seam's floor overlap is a shiplap within the slab, not a proud tongue.

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

Inside those same verticals stand the COLUMNS, and each is that relief MIRRORED.
The wall carries its round through as a cove one `wall` in — the arc the cavity
turns from one inner face round to the other — and the column is that arc folded
across its own chord: the same radius the other way, off the same two points on
the same two faces. So the section is a LENS, two sharp corners opposite each
other on the walls and two round sides opposite each other, and it runs floor slab
to ceiling. They are the cavity's own shape (`_cavity`), so everything held inside
it meets a column the way it meets a wall: a Z seam's lip wraps the face and
telescopes on it, a pod's collar is clipped by it, and a mount inside the
footprint is the column's material with only its bore left. Where a lens would
hole the collar at a seam station, the station stands off its cusp instead
(`_z_front_station_y`).

A plug is the wall it drives through and the reach it needs past it: the first
`wall` of its length is that wall's own material and the rest a stub off it, its
mouth-side face on the mouth that receives it. A socket is a pipe round that plug —
one `wall` of material, a `socket_cap` over the insert's blind end — its rim-side
face on the lip rim and its far face a hair inside the lip's own fusion shoulder,
so it stands on the lip band down its whole length. Those are the two matings the
overlap depth is struck from. Between two levels the corner is the wall's own air.
A level stands where its socket has a body to be bored into (`_level_clear`).

Each seam is pinned at BOTH ends of every piece that crosses it, so nothing can
hinge open at its far end: the Z seams at both ends of their column, and the Y
seam at a level for each end of each piece — which, with two staggered Z seams,
is six levels rather than one pair near the top. Levels are searched per side
wall against what stands against it, so the two walls need not carry the same
ones; main() prints what each ended up with.

main() exports the four printable pieces (enclosure-front-bottom.step,
enclosure-front-top.step, enclosure-back-bottom.step, enclosure-back-top.step)
plus enclosure.step — the four as separate solids in assembled position,
seams intact (mirrors `touch_flo_shell.py`). All five come through the same
code from a `Box`.
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
sys.path.insert(0, str(_repo / "hardware" / "printed-parts" / "valve-seat"))
sys.path.insert(0, str(_repo / "hardware" / "printed-parts" / "enclosure" / "valve-panel"))
sys.path.insert(0, str(_repo / "hardware" / "printed-parts" / "enclosure" / "pump-tray"))
from _cadq_export import export_assembly
from _materials import WALL_COLORS as PIECE_COLORS, one_body
from docgen import substitute_md, substitute_py_comments
import _boxes
import _realized
import hopper_funnel as _funnel
import wago_221 as _wago
import mq6_gas_sensor as _mq6
import valve_seat as _seat
import valve_panel as _panel
import pump_tray as _tray

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

# --- the standing corners' columns ------------------------------------------
#
# THE COLUMN IS A LENS, and the lens is the wall's own rounding MIRRORED. Each standing
# vertical is relieved `corner_round` outside and carries that relief through the wall as a
# cove one `wall` in — the arc the cavity turns from one inner face round to the other,
# springing from a point on each. FOLD THAT ARC ACROSS ITS OWN CHORD and the column is what
# comes back: the same radius curving the other way, off the same two points on the same two
# faces. Its centre lands on the interior corner itself, which is what mirroring that arc
# does to the centre it was struck on.
#
# The two arcs meet at 90° where they land, so the section is a LENS — two SHARP corners
# opposite each other, one on each wall, and two ROUND sides opposite each other: the cove
# it seats in behind, and that cove's mirror bulging into the room ahead. Nothing is tangent
# and nothing is filled in; the column is the fold and no more.
#
# It is a pillar and not a feature at a station: it runs floor slab to ceiling, so every Z
# seam crosses it and the seam's own lip wraps its face the way it wraps a wall (`_cavity`).
# What stands in a corner is ABSORBED — a boss inside the footprint is the column's own
# material and keeps only its bore — and a seam station whose collar would be holed by the
# lens stands off its cusp instead (`_z_front_station_y`).
column_round = corner_round - wall
# The corners that carry one, as the (x, y) signs of the interior corner each stands in.
column_corners = ((-1, -1), (1, -1), (-1, 1), (1, 1))

# H2C left-nozzle build envelope; each printed HALF must fit inside this.
H2C_X, H2C_Y, H2C_Z = 325.0, 320.0, 320.0

# Display-mounting facet — a flat 45° SOLID surface chamfered into the top-front
# arris for the Waveshare ESP32-S3-Touch-LCD-4.3B config display
# (../../../reference/waveshare-43b-display/), facing up-and-forward (−Y front /
# +Z up) toward the standing user.
#
# The facet runs the box's FULL WIDTH, wall to wall, and the display is CENTRED on
# it: the machine is 215 mm wide and the inset the cover plate fills 153.5, so what
# is left is ~31 mm of flat 45° face either side of it. That corner is unpackable at any width
# — the chamfer is inside the box's own silhouette — so spending all of it buys a
# face that reads square from the front, and the geometry gets simpler for it: no
# end wall closing a recess, no shoulder where a window stops, no bed relief on the
# arris a shoulder would raise. The window's lateral size is therefore the box's,
# not a parameter; `display_facet_x` is the display FEATURE's own footprint — the
# inset the cover plate fills plus a buffer all around,
# [157.3 mm](DISPLAY_FACET_X) × [86.8 mm](DISPLAY_FACET_SLOPE) up the slope — which is
# what `_report_facet` prints beside the measured face.
display_bezel_x = 113.5           # bezel glass, lateral (X)
display_bezel_slope = 77.0        # bezel glass, up the slope
# The glass is the datum (centered on the facet); the PCB body sits offset behind
# it because the glass overhangs the body unevenly (up-and-left). This is the
# body's own offset from the centered glass.
display_body_offset_x = 0.5      # PCB body offset from the centered glass, lateral (+X)
display_body_offset_slope = -1.0 # PCB body offset, down-slope
display_corner_r = 2.5           # corner rounding, matching the display bezel
# THE FACE CLOSES FLAT. The display is let into the facet down TWO steps, and a printed
# cover plate fills the outer one — so what a hand meets is one unbroken 45° plane with a
# border let into it, and the two screws that hold the border are countersunk into their own
# lands. Nothing stands proud of the face anywhere.
#
#   45° face  ─────────┐                       ┌─────────  ← the plate's top, flush
#                      │  inset, 2 mm          │
#                      └──────┐         ┌──────┘
#                             │ bezel   │         ← the glass, 2 mm further in
#                             └─────────┘
#
# The plate laps the glass by `display_inset_lap`, which is the same figure the inset stands
# outside the glass up the slope — so the border is that lap twice over, and one number
# states both halves of it.
display_inset_lap = 3.0          # the plate's lap over the glass, and the inset's land past it
display_inset_reach = 20.0       # how far the inset runs past the glass laterally — the land
                                 # the two cover screws stand in, since a countersunk M3 head
                                 # is wider than the border it would otherwise sit in
display_inset_depth = 2.0        # inset floor, down from the 45° face — the plate's seat
display_inset_x = display_bezel_x + 2 * display_inset_reach       # [153.5 mm](DISPLAY_INSET_X)
display_inset_slope = display_bezel_slope + 2 * display_inset_lap # [83 mm](DISPLAY_INSET_SLOPE)
# Every millimetre of plain face down the slope carries the facet √2 further aft along Y, and
# with it the seats let into it — which is what `display-housing-seats` reads the housing's
# own back cut against.
display_facet_buffer = 1.9       # plain 45° face kept outside the inset, all around
display_facet_x = display_inset_x + 2 * display_facet_buffer          # [157.3 mm](DISPLAY_FACET_X)
display_facet_slope = display_inset_slope + 2 * display_facet_buffer  # [86.8 mm](DISPLAY_FACET_SLOPE)
display_facet_angle_deg = 45.0
# The facet is a display housing this deep (the wall behind it, set to the
# display's overall depth) with the display let into it: a bezel counterbore on
# the user face and a PCB through-hole down the full thickness.
display_facet_thickness = 19.0   # facet wall depth = display envelope depth
# THE HOUSING'S BACK IS A VERTICAL PLANE, the full width of the box — one cut with no X term,
# the way the facet itself is one cut. Stated as a reach aft of the box's FRONT FACE, so it is
# struck off the face rather than off the box. Behind the display the slab keeps its full
# `display_facet_thickness` on the 45°; this takes the top corner off square, where the slab
# stands over the funnel and carries nothing. What it may not do is come forward into what the
# face carries: the inset and the bezel counterbore are the display's SEATS, and
# `display-housing-seats` keeps a wall of slab behind the deeper of the two.
display_housing_back = 83.25
display_bezel_depth = 4.0        # bezel counterbore depth, user face
display_pcb_x = 106.0            # PCB body through-hole, lateral (X)
display_pcb_slope = 69.0         # PCB body through-hole, up the 45° slope
display_pcb_cut_through = 3.0    # extra depth past the facet back, cutting a socket collar
                                 # clean through (it overhangs the hole otherwise)
# The cover plate and the two screws through it — the same DIN 912 M3 cap screw every seam in
# this machine takes, in the same ⌀`head_cbore_dia` flat-bottomed counterbore, landing
# `display_cover_seat_recess` under the 45° face so the plane closes over it.
#
# THE PAD IS WHAT THE COUNTERBORE STANDS IN: a head seat deeper than the plate would leave no
# land under the head at all, so the plate thickens under each screw by exactly the
# counterbore's own depth and the inset floor is pocketed to take it. The land is then the
# plate's own section. Everything else about the plate stays the border it is.
display_cover_thickness = 2.0    # = display_inset_depth, so the plate's top lies in the face
display_cover_slip = 0.30        # per side, plate edge into the inset it drops in
display_cover_head_h = 3.0       # DIN 912 M3 head, nominal
display_cover_seat_recess = 0.2  # how far under the 45° face the head lands
display_cover_cbore_depth = display_cover_head_h + display_cover_seat_recess
display_screw_pad_dia = 12.0     # the plate's local thickening under each head
display_screw_pad_depth = display_cover_cbore_depth   # so the land is the plate's own section
display_screw_pad_slip = 0.30    # per side, pad into its pocket
# Each screw stands in the middle of the lateral land, halfway between the glass's edge and
# the inset's own — the widest material either has.
display_screw_x = (display_bezel_x + display_inset_x) / 4.0           # [66.75 mm](DISPLAY_SCREW_X)

# Hopper funnel opening (Zone C) — one rectangular opening through the top wall
# BEHIND the display facet, cut at the placed funnel's collar: the funnel is a
# static part (../../zone-c/hopper-funnel/, its own frame) placed at
# the box's own `funnel` centre with its brim on the box top, and with_funnel
# measures the top-wall frame against it (the housing's back cut ahead, the
# ±X boss chains either side, the back wall behind). The collar stands on
# `funnel_front_y` and reaches aft for its capacity, so it may CROSS the Y
# seam — both halves take their share of the cut.
# Air between the funnel's collar frame and the ±X boss chains it runs beside. CHOSEN, not
# derived: the two are printed in the same piece, so this is clearance for the eye and the
# deburring tool rather than a fit.
hopper_chain_gap = 1.0
# The collar's front edge, read by `enclosure_assembly.funnel_centre`. What fences it is under
# the drain rather than over the brim: the union on the spout stands in the window between
# `_lines.CROSS_Y`'s crossing and the cold core's front face, and neither rides the display.
funnel_front_y = 88.25
# The top wall between the display housing's back plane and the throat, read on
# `funnel-collar-frame`. The brim's overhang lands on the housing slab at zero.
hopper_front_ledge = 0.0

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
# What that section keeps round its insert, which is the material any boss in this machine
# stands a heat-set in.
boss_ligament = (mount_boss_dia - heatset_dia) / 2.0
# Air past the screw tip at the bore's blind end, so a screw longer than the insert has
# somewhere to go rather than bottoming on printed material.
mount_bore_relief = 1.0

# --- the floor slab's posts -------------------------------------------------
#
# THE POST IS THE SLEEVE. It rises through the bore of the rubber grommet the donor's plate
# carries, and it stops just under that grommet's crown — so drawing the screw up squeezes the
# top flange by the difference and then lands on printed material. The preload and the limit on
# it are the one dimension (`enclosure_assembly.FLOOR_GROMMET_SQUEEZE`). The rubber between the
# post and the metal hole it is wrapped through is the isolator.
#
# The section is the donor's: each station carries its own diameter, struck off that bore in
# `enclosure_assembly.floor_mounts`. What the post holds is a ruthex M5, and `_floor_bosses`
# reads the two against each other every build.
floor_heatset_dia = 6.8      # ruthex M5, Ø7.0 knurl
floor_heatset_depth = 9.5

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

# --- the condenser block's four flanges -------------------------------------
#
# THE BLOCK IS HELD AT ITS FOUR FLANGES AND NOWHERE ELSE. Each of its two Y faces stands back
# over the block's whole width, leaving a folded sheet at the crown and one at the base, and
# both recesses open on their own face and both flanks — so the box can reach in at either end
# of the block without reaching round it.
#
# ONE END SLIDES AND THE OTHER SCREWS. The FORE flanges carry no hole, so what takes them is a
# GROOVE: a rail off the front wall at each end, the pair of them straddling nothing but air,
# and the block goes in aft-first and forward until its fore face meets the rail's own shoulder.
# THE RAIL IS THE DATUM IN Y. In Z each groove closes over its flange with air on both faces of
# the sheet, and what stands the block off the floor is the bore under its base flange. The lower
# rail's underside is the slab, which makes it a corner bracket rather than a shelf.
#
# The AFT flanges carry the donor's own two holes, one line through both, and each takes a screw
# DOWN into a ruthex M3. So both bosses stand under the sheet their screw passes through, and
# the geometry that carries them is one fin on the +X wall with a finger reaching west off it
# into the recess at either end. The lower finger runs to the slab and is what the block's aft
# end stands on; the upper one is a finger and nothing else.
#
# THE FIN IS EAST BECAUSE THE RECESS'S OWN FLOOR IS THE BASE FLANGE. Nothing can stand on the
# slab inside that recess — the sheet is in the way at every point of it — so the column that
# reaches the crown flange has to root outside the block's own flanks, and the lane between the
# block and the +X wall is the one that is free.
cond_rail_wall = 3.0        # rail and finger section around a groove or a bore
cond_slot_grip = 3.0        # how much of a fore flange's own depth each groove swallows
cond_mount_clear = 1.0      # air off the block: the fin's own lane, and each end of the band
# A GROOVE IS STRUCK ON THE SHEET THAT STANDS IN IT. Two figures meet in `cond_slot_half`: the
# SLIP, which is what the gas sensor's [1.6 mm](MQ6_CARD_T) card gets either side of it in its
# own [1.9 mm](MQ6_SLOT_OPEN) slot, and the OPENING, which is what a groove stands at least,
# however thin the sheet it takes. The block keeps its own sheet thickness and the box keeps
# what it will open for one.
cond_slot_press = 0.15      # per-side slip in a groove, the wells' own figure
cond_slot_open = 1.0        # [1 mm](COND_SLOT_OPEN) — the least a groove may stand open


def cond_slot_half(sheet: float) -> float:
    """The air a groove keeps on EACH side of the sheet standing in it: the slip, or what the
    opening leaves over that sheet, whichever is the wider."""
    return max(cond_slot_press, (cond_slot_open - sheet) / 2.0)


# --- what holds the cold core ------------------------------------------------
#
# THE CORE HAS NO HOLE IN IT. It is a foamed cup with a screwed cap at each end and a plain
# rounded-rectangular skin the whole way round — the heaviest single body in the machine, and
# the one on the floor with nothing to bolt through. What holds it is the box shut on it: every
# quadrant is screwed to the two beside it, so a feature printed on one piece stands over a body
# sitting in another.
#
# TWO FEATURES, EACH ON THE PIECE WHOSE OWN MATERIAL REACHES THE FACE IT TAKES, and each a
# mirror pair about x = 0:
#
#   `_core_stops`  on **enclosure-front-bottom** — a block in each front corner of the slab,
#                  pocketed to the core's own plan outline: the corner round outboard of the
#                  tangent and one round of the flat front face inboard of it. The flat takes the
#                  core FORWARD and the round takes it in X and in yaw, and the pair leaves it no
#                  lateral travel.
#   `_core_holds`  on **enclosure-back-top** — a bracket standing in the `rear_seam_clear` band
#                  behind the core and turning over the aft edge of its cap. It takes the core
#                  UP: the slab is under it, so a pad on the crown stands in the way of a
#                  straight lift and of either tip, whose far end carries this pad with it.
#
# The floor takes the weight and the back wall the aft. `enclosure_assembly.check_core_held`
# reads all four off the built pieces and the placed core.
#
# THE CORE ENTERS THE POCKET FROM AHEAD OR FROM ABOVE. The pocket is that outline carried
# straight down, so it stands clear of the core at every stand-off and closes on it at the slip:
# the front assembly slides aft onto a core already down, or the core comes straight down into a
# box already telescoped.
#
# The fit is the diametral slide the seam's own plug takes in its socket, and it is one figure on
# the round and on the flat — one offset of one outline.
core_stop_slip = split_slip
core_stop_web = 6.0           # material ahead of that outline, at every point of the pocket
# How far the block stands off the slab. The lane in front of the core belongs to the refrigerant
# loop — both drawn legs cross it and land on the core's front face — so the block takes the depth
# of it that is empty and stops under them. A leg that came down into it is a `pack-closes` clash.
core_stop_rise = 40.0
core_hold_reach = 12.0        # how far a bracket's foot runs onto the cap off the core's aft face
core_hold_land = 8.0          # that foot's own thickness where it leaves the gusset
# How far the bracket's leg carries UP the back wall behind the foot, standing in the band
# `rear_seam_clear` holds open. The foot's load arrives at the wall over the leg's whole height.
#
# THE SECTION IS A TRIANGLE AND NOT AN L. One face runs from the foot's own tip to the head of
# that leg, so the corner between them is solid and the foot is a flange on a web rather than a
# cantilever. It takes no envelope the L's two arms did not already reach, and printed
# ceiling-down it falls `core_hold_reach + rear_seam_clear` in `core_hold_rise - core_hold_land`
# — 25° off vertical — so the foot is drawn out of the air rather than off a support strip.
core_hold_rise = 40.0


# THE BORE SWALLOWS THE WHOLE SCREW. Every other insert in this box is reached through a body
# that holds a share of the screw's own length; this one is reached through four tenths of sheet,
# which holds none of it. So the bore is the screw and the air past its tip, and the grip inside
# it is still the ruthex's own `heatset_depth`.
cond_screw_len = screw_len - 2.0                    # M3 × 8, the box's own shelf screw
cond_bore_depth = cond_screw_len + mount_bore_relief
# What a finger keeps under that bore: the bore itself and a wall beneath it.
cond_boss_t = cond_bore_depth + cond_rail_wall
# How far one of those bosses stands OFF the wall's inner face — which is the standoff a body
# hung on the flank gets, and every millimetre of it is insert: the bore runs the boss's whole
# length and stops on the wall's own inner face, so the wall behind is what caps its blind end.
# Nothing here is spent holding the body away from the wall. That is the point — a body bolted
# to a wall wants to be ON it, and this is the shortest column an M3 heat-set can live in.
mount_boss_out = heatset_depth + mount_bore_relief
# How far a boss stands inboard of the wall it drives through: the whole chain
# of head counterbore, pin body, heat-set and cap, less the wall the counterbore
# is sunk into. This is the socket collar's own depth off the wall.
boss_in = head_cbore_depth + screw_len + socket_cap - wall
# The band down each ±X wall IS that chain: what a floor body stands off the wall where the
# seam's bosses are, so each mouth, plug and collar seats at full section and the body seats
# flush against them. One name for the reader who is thinking about the band and one for the
# reader thinking about a single boss, and one number under both — an M3 of another length
# moves the chain and the band together.
side_band_inset = boss_in
# The telescoping overlap is NOT a free dimension. It is exactly what makes the
# back plug's −Y face mate the back mouth (y_joint) AND the front socket collar's
# +Y face mate the lip rim, with the two bosses coaxial for the cross-screw.
# With y_boss = y_joint + plug_dia/2 (plug −Y on the mouth), the collar's +Y face
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
# `box-width`. What sets the number is the cold core standing its own `side_band_inset`
# off both walls: 181 across, 14 either side, and one wall each side of that.
appliance_width = 215.0


# WHAT A STATED BOUND IS READ TO. Each of the three is a placed body's own box against a plane,
# and that box is an OPTIMAL one — on a filleted or splined body it converges rather than closing
# exactly. The cold core is `outer_shell_y_length` = 181.0 by construction and its box reads
# 181.0000002, so it stands flush on this width and answers a finer bound by two ten-millionths
# of a millimetre. A bound struck under the reading's own precision measures the solver, not the
# machine. This is the figure the rest of this file reads a solid to.
stated_bound_tol = 1e-6


def interior_x():
    """The ±X interior faces, struck off the stated width alone. `_dims` builds the box on
    these and every body seated on a flank reads them through the same call, so the wall and
    the things that stand against it cannot come apart."""
    return (-(appliance_width / 2.0 - wall), appliance_width / 2.0 - wall)
# The interior REAR PLANE — the inner face of the back wall, stated the same way. A
# component dragged forward inside the machine does not make the machine shallower,
# a pack that outgrows this plane reads red on `box-depth` instead of quietly resizing
# the appliance.
rear_plane_y = 464.0
# And the interior FRONT PLANE, holding the other end, with the 45° facet and its display
# hanging on it and `box-front` reading the pack against it. Every millimetre aft carries
# `housing_back_y` aft too, so what it spends is `hopper_front_ledge`.
front_plane_y = 8.0

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
# The front column's seam stands clear UNDER the flavour pack's two pumps. Its lip carries
# `lip_len` up into the cavity one wall proud of the interior face, and a pump head's front
# face is on that face — so the plane is struck low enough that the lip's rim passes beneath
# the head rather than against it (`z-seam-under-pumps`).
front_z_seam = 150.0

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


# The whole description of one box — what `build_pieces` cuts the four pieces from:
#   inner/outer   the cavity and the shell, (x0, x1, y0, y1, z0, z1)
#   y_joint       the front↔back seam plane
#   splits        the bottom↔top seam height per Y column, (front, back)
#   front_ports   / back_ports   panel through-holes, in the pack's format
#   east_ports    +X side-wall through-holes, (kind, y, z, *size)
#   west_ports    −X side-wall through-holes, same shape — the drip tray's slot
#   funnel        the placed hopper funnel's plan centre, or None for no throat
#   pan_sleeve    the drip tray's carry, `(adds, cuts)` of world boxes — the solid block fused
#                 onto the −X wall, and the berth cut back out of it
#   c14           the mains inlet's heat-set stations on the back wall, (x, z)
#   east_bosses   the +X wall's mounting bosses, (y, z, the plane the boss top reaches)
#   side_wells    the side walls' Wago wells, (side, y, z, size) — one press-fit pocket
#                 per lever nut, on the flank its own cluster stands on
#   floor_bosses  the floor slab's mounting bosses, (x, y, the plane the boss top reaches, the
#                 section the donor's own bore leaves the post standing in it)
#   west_cradle   the −X wall's MQ-6 card slot, (y, z) — the card's plane and its centre
#   cond_cradle   the front wall's condenser rails, one (face, x0, x1, fz0, fz1, root) per fore
#                 flange — the plane the block's fore face rests on, that flange's width, its
#                 two faces in height, and how far the rail runs down under it
#   cond_mount    the condenser's aft mount, (flank, y0, y1, bosses) — the fin's own west face,
#                 the Y band it stands in, and one (x, y, the flange face it reaches) per hole
#   asse_cradle   the −X wall's tap-water cradle, (axis_z, sections, ties, reach_down) — the
#                 axis the trough is struck on, one (y0, y1, apex_x) per section of the chain,
#                 the Y of each tie band, and how far under the axis its flanks run
#   digiten_saddles  the top wall's two flow-meter saddles, (axis_x, axis_z, seat_r, bands) —
#                 the arm axis the Vs are struck on, the barrel they seat, and the run of
#                 each arm one takes
#   tube_anchors  the runs' own seats, one (mid, along, root, seat_r) each — the middle of the
#                 leg a rib is centred on, which way the tube points there, which way the face
#                 it stands on lies, and the section it seats
#   port_field    the pockets the back wall's outer face carries and the bosses behind them,
#                 (proud, rim, pockets) — how deep a pocket is cut and how far its boss stands
#                 inboard, the wall the field keeps around each chip, and one (x, z, width,
#                 rise) per pocket. A pocket is a D on its back: a half circle below the bore's
#                 axis and a rectangle above it, so it takes its chip one way up and no other.
#                 The boss is that shape one rim larger, and makes back exactly what the pocket
#                 took, so the wall keeps its whole thickness under every chip
#   nameplate     the plate's own pocket on that same face, and the two screw bosses behind it —
#                 its station and outline, the two stations on it, and everything one screw
#                 costs the wall: the pad's pocket, the collar round it, the stem under that and
#                 the insert's bore through both
#   valve_panels  the flavour manifold's decks, one (plane, sign, seats) each — the world Y a
#                 deck's valves stand their mounting faces on, which way their own +Z runs off
#                 it, and one (x, z) per valve. A panel is a plate wall to wall carrying one
#                 four-boss `valve_seat` per valve (`valve_panel`), and it is this piece's own
#                 material the way the trough and the saddles are
#   pump_trays    the flavour manifold's two pumps, one world `centre` each — the point a pump's
#                 own axis meets the +Z face of its head, which is `pump_case`'s own base plane.
#                 A tray is that case with its cylinder cut off (`pump_tray`), run from the axis
#                 to the front wall, and it is this piece's own material like a panel
#   core_stops    the cold core's two front corners, one (cx, cy, r, tip) each — the centre and
#                 radius of the core's own corner round, and the plane the block over it reaches
#   core_holds    the cold core's two hold-downs, one (x0, x1, aft, crown) each — the lane on the
#                 cap a bracket stands in, the core's aft face, and the plane its cap presents
#   vent_chase    the cold core's PRV relief line, one (x, y, z) — the core's west flank, which
#                 the chase's lip lands on, and the tube's own axis where it comes through
#   column_reliefs what the standing corners' COLUMNS give up to the pack standing in them, one
#                 (sx, sy, name, room) per body — the corner's own signs, whose body it is, and
#                 the world box the column is cut back to. Struck by `_dims` off the placed
#                 parts rather than passed in by the pack, because it is the one question that
#                 needs the bodies AND the walls at once; main() prints every one of them.
#
#                 A COLUMN GIVES WAY TO A BODY AND NOT THE OTHER WAY ROUND. It is a print-corner
#                 feature — what it buys is a fat vertical on the bed, and it buys that over the
#                 height it does have. A body hung on a wall answers to the boss that holds it
#                 and to whatever the pack packed it against, and by the time one reaches a
#                 corner both of those are already spent.
Box = namedtuple(
    "Box", "inner outer y_joint splits front_ports back_ports east_ports west_ports "
           "funnel pan_sleeve c14 east_bosses side_wells floor_bosses west_cradle cond_cradle "
           "cond_mount asse_cradle digiten_saddles tube_anchors port_field nameplate "
           "valve_panels pump_trays core_stops core_holds vent_chase column_reliefs")

# What a box is built AROUND: the placed bodies, and every station they put on a wall.
# A pack that does not carry a subsystem yet carries no stations for it, and the wall
# comes out blank there rather than carrying a hole with nothing behind it.
#   placed        {name: (solid, colour)} — the same shape a CadQuery assembly reads
# The rest are the Box fields above, and the box passes them through.
Pack = namedtuple(
    "Pack", "placed front_ports back_ports east_ports west_ports funnel pan_sleeve c14 "
            "east_bosses side_wells floor_bosses west_cradle cond_cradle cond_mount "
            "asse_cradle digiten_saddles tube_anchors port_field nameplate valve_panels "
            "pump_trays core_stops core_holds vent_chase")
Pack.__new__.__defaults__ = ((), (), (), (), None, (), ((), ()), (), (), (), (), (), (),
                             (), (), (), (), None, (), (), (), (), ())


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


def _yz_prism(x0, x1, section):
    """A prism along X from x0 to x1, whose `section` is a closed `(y, z)` polygon.

    `_ybox` with one of its four section corners free. The `YZ` workplane's own axes are the
    world's Y and Z, so the points are read in the frame every station is stated in."""
    return (
        cq.Workplane("YZ", origin=(min(x0, x1), 0.0, 0.0))
        .polyline(list(section)).close()
        .extrude(abs(x1 - x0))
        .val()
    )


def _xz_prism(y0, y1, section):
    """A prism along Y from y0 to y1, whose `section` is a closed `(x, z)` polygon.

    `_yz_prism` turned a quarter. The `XZ` workplane faces −Y, so the extrusion is taken back
    the other way and the prism set down at y0 — and its axes are the world's X and Z, which
    is the plane a feature on a ±X wall is drawn in."""
    return (
        cq.Workplane("XZ")
        .polyline(list(section)).close()
        .extrude(-(y1 - y0))
        .val()
        .translate((0.0, y0, 0.0))
    )


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


def _column_arcs(inner, sx, sy):
    """The two centres one corner column's two arcs are struck on: the INTERIOR CORNER,
    which the mirrored arc is swung from, and the centre the cavity turns its own corner
    on, one `column_round` in from each of the two inner faces.

    Mirroring an arc across its chord mirrors the centre with it, and for a quarter turn
    between two faces that lands the image on the corner the two faces meet at. So one
    radius and these two points are the whole of the lens."""
    ix0, ix1, iy0, iy1, _iz0, _iz1 = inner
    px = ix0 if sx < 0 else ix1
    py = iy0 if sy < 0 else iy1
    return (px, py), (px + (column_round if sx < 0 else -column_round),
                      py + (column_round if sy < 0 else -column_round))


def _corner_column(inner, sx, sy, grow, z):
    """One corner column as a solid over the height span `z`, grown `grow` into the room.

    THE LENS IS WHAT THE TWO DISCS SHARE. Both arcs bound it from OUTSIDE — the cavity's
    own arc holds it off the corner, the arc swung from the corner holds it out of the
    room — so the column is the intersection and not the difference. Take the difference
    and what comes back is the crescent on the far side of the cove, which is the wall's
    material already and cuts nothing out of the air.

    Two circles of one radius meet in exactly two points whatever their centres, and here
    those are the cusps, one on each inner face. Growing swells both discs, which is the
    one offset read on each arc's own side."""
    (px, py), (qx, qy) = _column_arcs(inner, sx, sy)
    z0, z1 = z
    r = column_round + grow
    return _zcyl(r, px, py, z0, z1).intersect(_zcyl(r, qx, qy, z0 - 1.0, z1 + 1.0))


def _column_along():
    """How far along a wall, from the interior corner, a column reaches.

    Its CUSP stands on that wall's inner face, one radius from the corner, and the lens
    closes back toward the corner from there — so a feature standing anywhere on the wall
    meets the cusp and nothing of the column is further along than it."""
    return column_round


def _cavity(inner, inset=0.0, z=None):
    """The box's AIR at `inset` in from every interior face — the rounded cavity less the
    columns standing in its corners.

    Everything that has to stand inside the cavity is held inside this, so a collar or a
    lip segment meets a column exactly the way it meets a wall. The wall rounds shrink with
    the inset (square once one reaches zero) and the columns grow by it: one offset, read
    from the two sides of the same surface."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    z0, z1 = (iz0, iz1) if z is None else z
    air = _round_z(_ybox(ix0 + inset, ix1 - inset, iy0 + inset, iy1 - inset, z0, z1),
                   corner_round - wall - inset)
    for sx, sy in column_corners:
        air = air.cut(_corner_column(inner, sx, sy, inset, (z0 - 1.0, z1 + 1.0)))
    return air


# --- box dimensions, driven by the placed contents -------------------------

# What stands in each ±X wall's Y-seam corner, measured — not tabulated — so it
# follows the contents instead of drifting from them. Filled by _dims() (the one
# function that reads the placed parts), keyed by the footprint and depth probed,
# and read by `_level_clear` to ask whether one particular height is usable. A
# wall with nothing in the way gets no entry.
#
# THIS DICT IS EMPTY IN THE RUN THAT EXPORTS THE PIECES, and what makes that safe is that a
# missing key is a reading here: `_level_clear` answers True on one, which is "nothing known
# to be in the way". Run this module directly and it is `__main__`; `machine_of` then imports
# `enclosure_assembly`, which imports `enclosure` — a SECOND copy of this file — so `_dims`
# fills that copy's dict while `main()` builds the pieces out of this one's. Both boxes come
# out the same today, measured piece by piece, because the one entry the pack puts here
# changes no level's verdict.
#
# SO NOTHING THAT DOES NOT DEGRADE THAT WAY MAY LIVE HERE. A record whose absence would
# silently drop a cut — a relief, a pocket, a station — rides the `Box` instead, which is
# built in one copy and passed to the other. `Box.column_reliefs` is here for that reason.
_wall_block = {}

# Air round a body where a column is cut back for it, per side. The pocket is struck on the
# body's own BOX and not its solid: what stands in a column is a body's corner, a corner is
# what a hand has to get past, and a pocket that hugged a casting's every feature would be a
# pocket nothing could be lowered into.
column_relief_slip = 1.0


def _block_key(x_in, sx, y0, y1, depth):
    return (round(x_in, 3), sx, round(y0, 3), round(y1, 3), round(depth, 3))


def _measure_wall_block(placed, inner, y0, y1, depth):
    """For each side wall, probe a Y-seam corner feature's own footprint against
    the placed contents and keep whatever stands inside it. Only what stands
    inside THIS footprint at THIS depth counts — a part may cross the wall's
    height band and still leave the corner alone, so a bounding box is not enough
    to judge it by."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    for x_in, sx in ((ix0, +1.0), (ix1, -1.0)):
        xa, xb = sorted((x_in, x_in + sx * depth))
        prism = _ybox(xa, xb, y0, y1, iz0, iz1)
        hits = [h for h in (prism.intersect(s) for s, _c in placed.values())
                if h.Volume() > 1.0]
        if not hits:
            continue
        block = hits[0]
        for h in hits[1:]:
            block = block.fuse(h)
        _wall_block[_block_key(x_in, sx, y0, y1, depth)] = block


def _y_corner(inner, y_joint):
    """The Y extent of the FRONT half's socket collar — one socket_r either side
    of the bore axis. Aft that is the lip rim, where the collar's face lands;
    forward it is the sliver of front wall the collar's own root takes, a hair
    ahead of the lip's fusion shoulder.

    One definition, read by the band _dims probes, the heights _bosses may place a
    level at, and the collar `_front_socket` builds — so a change to the boss
    cannot move one of the three and leave the others measuring somewhere else."""
    return (max(inner[2], _y_boss(y_joint) - socket_r), y_joint + lip_len)


def _y_corner_back(iy1, y_joint):
    """The Y extent of the BACK half's plug — one plug radius either side of the
    bore axis, so it stands on the seam mouth and runs one plug diameter aft of
    it."""
    return _y_boss(y_joint) - plug_dia / 2.0, min(iy1, _y_boss(y_joint) + plug_dia / 2.0)


def wall_band_corner_y(reach):
    """How far aft a body standing `reach` inboard of a ±X wall's inner face reaches before
    the box's own standing-vertical relief curves that wall away from it.

    The cavity is rounded `corner_round - wall` about a centre one radius in from each face,
    so at a back corner the wall leaves the body's plane along an arc. This is where the arc
    crosses that plane — and unlike a boss it is a bound at EVERY height, which makes it the
    aft end of what the band has to give. A body reaching further inboard than the radius is
    clear of the arc entirely and answers to the rear wall itself.

    WHERE THAT CORNER CARRIES A COLUMN the arc is no longer what a body meets first: the lens
    stands in the air the arc left open, and its room-facing side is swung from the corner. The
    −X wall's back corner carries one and this still reads the arc, because nothing on that
    flank comes near either — the tap-water cradle stands 9.9 mm off the wall where the lens
    reaches 9, and every body aft of it stops 20 mm short of the rear plane. The reading this
    owes a column is owed on the flank whose bodies are IN it."""
    r = corner_round - wall
    if reach >= r:
        return rear_plane_y
    return (rear_plane_y - r) + math.sqrt(r * r - (r - reach) * (r - reach))


def wall_boss_aft_limit():
    """The aftmost station on a ±X wall that carries a boss its whole `mount_boss_out` long.

    THE STANDING CORNER IS THE FENCE HERE. The cavity's vertical corners are relieved
    `corner_round - wall` for the bed, so from that arc's centre plane aft the wall is no
    longer at `interior_x`: it curves inboard, a boss on it is shorter than the heat-set it
    carries, and where the arc crosses the boss tip there is no boss at all. The centre plane
    is the last station with the whole length under it, and it is a bound at every height, the
    relief running the box's full standing depth.

    A mounting pattern answers to this; an envelope answers to `wall_band_corner_y`, which is
    where the same arc crosses the plane the BODY stands on, further aft.

    A COLUMN IN THAT CORNER DOES NOT MOVE THIS. A boss is printed material and so is a lens,
    so a boss standing inside one comes out of the print as one body with it and keeps only
    its bore — absorbed, the way the condenser's cradle rail is. What a lens does fence is the
    BODY hung on that boss, whose own overhang is in air; that is `wall_band_corner_y`."""
    return rear_plane_y - (corner_round - wall)


def east_band_free_y():
    """The BACK half's free run of the ±X boss-chain bands, as `(y0, y1)` — the depth a body
    hung on that flank has aft of the Y seam.

    ONE Y SPAN CARRIES EVERY Y-SEAM LEVEL. The levels differ in height and share a station,
    so `y_seam + lip_len` is the aft face of all of them at once and no height has to be
    named to say where they stop. Aft of it the band meets the back corner's own relief
    (`wall_band_corner_y` at a wall seat's reach), which is the one thing on this flank that
    stands at every height.

    THE Z-SEAM STATIONS ARE NOT IN IT. Each is a collar `2 * socket_r` tall at the height its
    own seam lands on, and that height is searched rather than stated (`_z_joints`) — so a
    body standing clear of it in z passes it, and whether one does is a question about a
    placed pack. `enclosure_assembly.check_east_band` asks that against `seam_bosses`, which
    carries each boss's height as well as its station.

    Struck off the stated planes alone, `y_seam` and `rear_plane_y` — so a body reads it
    before the box that carries it has been sized, the same way it reads the wall itself
    through `interior_x`."""
    return (y_seam + lip_len, wall_band_corner_y(mount_boss_out))


def front_band_collar_z():
    """The FRONT column's collars in height, as `(z0, z1)` — the only thing the seam stands in
    a ±X boss-chain band forward of the Y seam's own station.

    THIS SEAM'S HEIGHT IS STATED where the back column's is searched (`front_z_seam`,
    `_z_joints`), so the one boss the front half's bands carry has a height a body can be
    placed against BEFORE the box is sized. `front_band_free_y` turns it into a depth; a caller
    that wants to stand under it rather than beside it asks for it directly."""
    zc = _z_pin_z(front_z_seam)
    return (zc - socket_r, zc + socket_r)


def _z_front_station_y(iy0):
    """The FRONT column's front X-pin station in Y — the front-wall corner.

    Its own function because it is read twice, the way `_z_back_station_y` is: once to build
    the stations and once by `front_band_free_y`, which answers before there is a box.

    THE COLUMN TAKES THIS CORNER. With nothing standing there the collar's own −Y face lies
    on the front wall's inner face and the station is one bore radius behind it. Where the
    standing vertical carries a column, the lens runs up that wall to its cusp and would be
    a leaf-shaped hole through the collar's root — so the station stands one socket_r behind
    that cusp, which is the same clearance the aft station keeps from the lip's Y gap. The
    collar comes out whole and the corner keeps its pillar."""
    plain = iy0 + wall + socket_bore_dia / 2.0
    if not any(sy < 0 for _sx, sy in column_corners):
        return plain
    return max(plain, iy0 + _column_along() + socket_r)


def front_band_free_y(front_face, z0=None, z1=None):
    """The FRONT half's free run of the ±X boss-chain bands, as `(y0, y1)` — the run
    `east_band_free_y` says this half has and is not.

    The front column's two Z stations are its ends, and this seam's height IS stated
    (`front_z_seam`), so a caller that says what height it stands at gets the answer for that
    height: a body clear of the collars in z has the column from the front wall to the Y
    seam's own bosses. A caller that names no height gets the run with both collars standing.

    IT TAKES THE FRONT FACE because it cannot state it. The back half's two ends are both
    struck on planes the box states about itself — `y_seam` and `rear_plane_y` — but the front
    wall stands off whatever the pack puts nearest it, so a caller reading this before the box
    is sized has to say what that is. Everything after it is the same stated chain `_dims`
    builds the wall on."""
    iy0 = front_face - interior_clearance - front_seam_clear
    yf = _z_front_station_y(iy0)
    yfr = y_seam - wall - z_lip_y_margin - socket_r
    cz0, cz1 = front_band_collar_z()
    if z0 is not None and (z1 <= cz0 or z0 >= cz1):
        return (iy0, yfr + socket_r)          # clear of both collars in height
    return (yf + socket_r, yfr - socket_r)


def _level_clear(inner, y0, y1, z_boss, x_in, sx, depth):
    """Whether this wall can carry a cross-pin at this height. The test is the
    SOCKET's whole body — bore, heat-set and cap, out to `depth` and one socket_r
    either side of the axis — against what `_measure_wall_block` found standing in
    that corner. A level whose socket has no body is not a fastener, it is a hole
    in a wall."""
    block = _wall_block.get(_block_key(x_in, sx, y0, y1, depth))
    if block is None:
        return True
    xa, xb = sorted((x_in, x_in + sx * depth))
    probe = _ybox(xa, xb, y0, y1, z_boss - socket_r, z_boss + socket_r)
    return probe.intersect(block).Volume() <= 1e-6


def seam_bosses(inner, y_joint, splits):
    """Every boss the seam stands in a ±X boss-chain band, as `(y0, y1, z0, z1)` — what each
    one actually occupies of that wall, both walls' taken together.

    A boss is a collar round a bore, so what it takes of the band is `2 * socket_r` across
    and the same tall, at the station its own screw is on. Read from the definitions that
    BUILD them (`_bosses`, `_y_corner`, `_z_stations`, `_z_station_y`), so a footprint cannot
    drift from the geometry it stands for.

    THE HEIGHT IS HALF THE ANSWER. A body hung on a flank clears a boss by standing beside it
    or by standing over it, and a reading with no z in it can only see the first — it would
    charge a body the whole height of a wall for a collar 16 mm tall. Between two bosses, and
    above and below every one of them, the band is the wall's own air."""
    r = socket_r
    yb0, yb1 = _y_corner(inner, y_joint)
    out = [(yb0, yb1, z - r, z + r)
           for _x_in, _x_ext, _sx, z in _bosses(inner, splits, y_joint)]
    for _x_in, _x_ext, _sx, ys, col in _z_stations(inner, y_joint):
        zp = _z_pin_z(splits[0] if col == "front" else splits[1])
        y0, y1 = _z_station_y(ys)
        out.append((y0, y1, zp - r, zp + r))
    return out


def _in_a_boss(b, bosses):
    """Whether a placed body's bounding box meets any of `bosses` in BOTH y and z."""
    return any(b.ymin < y1 and b.ymax > y0 and b.zmin < z1 and b.zmax > z0
               for y0, y1, z0, z1 in bosses)


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
    where the station collars stop too); the top piece runs the seam plane to the top
    wall's outer face. Both print standing on a Z face, so the bed's Z bounds each of
    them, and each bound is one end of this band."""
    oz0, oz1 = inner[4] - wall, inner[5] + wall
    return oz1 - H2C_Z, oz0 + H2C_Z - lip_len


def _lip_band(inner, z):
    """The Z-seam lip's own shape over a height span: the cavity's one-`wall` skin.

    THE LIP IS NOT A BOX. It is struck as the cavity's skin (`_cavity`), so it carries the
    wall rounds at the standing verticals and WRAPS whatever column stands in one — the
    pillar telescopes into the piece above on the same one wall of overlap every other face
    uses. A rectangular band drawn to the same figures is neither: it reaches into corners
    the cavity has rounded away, and it misses the wrap entirely, which is the part that
    stands furthest inboard.

    `_z_lip` fuses this onto a piece and `_lip_denied` measures what stands in its way, and
    they have to be the same shape or the second is answering about a lip the box does not
    build."""
    z0, z1 = z
    return _cavity(inner, 0.0, (z0, z1)).cut(_cavity(inner, wall, (z0 - 1.0, z1 + 1.0)))


def _lip_denied(placed, inner, y_span):
    """The seam heights the pack denies ONE Y column's Z seam, as z spans.

    The lip is the one part of a Z seam whose position rides the seam height: the
    cavity's own one-`wall` skin (`_lip_band`), running from its fusion shoulder
    (`zj − wall`) up to its rim (`zj + lip_len`). The four station collars ride with
    it, in the ±X boss-chain bands the lip's own side segments run down, so they
    occupy the same lane wherever the seam lands.

    IT IS THE SKIN AND NOT A BOX, so it WRAPS every column standing in a vertical, and
    that wrap stands a whole `column_round` further inboard than any wall segment does.
    A body clear of all four walls can still be in the lip's way there — the PSU's aft
    corner is, at the X+/Y+ column — and a rectangular ring drawn to the cavity's own
    figures cannot see it.

    A Z SEAM IS PER Y COLUMN AND SO IS ITS LIP. The front pair joins at one height and
    the back pair at another, and `_z_lip`'s band is intersected with the piece's own
    column before it is fused — so each piece carries a 3-sided lip over its own half of
    the box and nothing over the other half. A body is measured against the ring of the
    column being searched and no other; charging the back column's search for a body
    standing in the front is a denial the back seam never had to answer for.

    `y_span` is that column's half, cut at the Y joint. Nothing is filtered by which
    column a body's centre falls in — the ring is the column's own and the intersection
    says the rest, so a body spanning the joint is charged to both, as it should be. The
    span is a hair wider than the lip it stands for, since `_z_lip` also drops a gap
    around the joint that this does not model; that is conservative in the direction
    that denies more.

    So this measures the ring: what reaches into it, and the seam heights that reach
    would put the lip on. What holds the rest of the ring open is the pack's own
    standoffs — one `wall` at the front and back walls (`front_seam_clear`,
    `rear_seam_clear`) and one boss chain at the sides (`side_band_inset`)."""
    ix0, ix1, _iy0, _iy1, iz0, iz1 = inner
    cy0, cy1 = y_span
    ring = _lip_band(inner, (iz0, iz1)).intersect(
        _ybox(ix0 - 1.0, ix1 + 1.0, cy0, cy1, iz0 - 1.0, iz1 + 1.0))
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
    bands = whole or _open_bands(
        _lip_denied(placed, inner, (y_seam, inner[3])), bed_lo, bed_hi, 0.0)
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
    # The cavity every one of these bounds is measured against, and the seam heights that
    # ride it. Struck first because a boss's FOOTPRINT is what the width and height checks
    # both ask after, and a footprint is a station and a height together — the height comes
    # off the seams, and the seams come off the pack.
    ix0, ix1 = interior_x()
    iy0 = front_plane_y
    iy1 = rear_plane_y
    iz0 = min(czmin, 0.0) - interior_clearance
    iz1 = (iz0 - wall) + appliance_height - wall
    inner = (ix0, ix1, iy0, iy1, iz0, iz1)
    y_joint = y_seam
    splits = _z_joints(placed, inner, front_z_seam)
    band_bosses = seam_bosses(inner, y_joint, splits)
    # What the pack still has to earn is the clearance. A body on the slab is held one
    # `side_band_inset` off the ±X walls where the seam's bosses stand — `seam_bosses`, the
    # same footprints the ceiling's own band takes below. Beside one, and over or under one,
    # the band is the wall's own air, and a body clear of all of them answers on `cxmax`.
    floor = [b for b in bbs
             if b.zmin < wall + 1e-6 and _in_a_boss(b, band_bosses)]
    wide_need = max([cxmax + interior_clearance, -(cxmin - interior_clearance)]
                    + [b.xmax + side_band_inset for b in floor]
                    + [-(b.xmin - side_band_inset) for b in floor])
    record_bound(Bound(
        "box-width", "The pack stands inside the appliance's stated width",
        wide_need <= ix1 + stated_bound_tol,
        f"pack reaches x ±{wide_need:.2f}, wall at ±{ix1:.2f}",
        f"inside a {appliance_width:g} mm appliance",
        ([] if wide_need <= ix1 + stated_bound_tol else [
            f"the pack reaches x ±{wide_need:.2f} but a {appliance_width:g} mm appliance walls "
            f"in at ±{ix1:.2f} — {wide_need - ix1:.2f} mm over. Raise `appliance_width` or "
            f"repack inboard"])))
    # The FRONT wall is the stated `front_plane_y`, and what the pack owes it is one
    # `front_seam_clear`: the seam's lip carries into the cavity there, and a lip missing a
    # side is a butt joint over the box's most visible run. A body mounted on the front wall
    # seats on the plane this opens.
    #
    # The BACK wall is the stated `rear_plane_y`, for the same reason the ceiling is the
    # stated `appliance_height`: depth is a bound, not a consequence. Taken off the pack it
    # would follow whichever body reached furthest back, and anything seated on this plane
    # would follow that body too, holding every clearance between the two constant.
    front_need = cymin - interior_clearance - front_seam_clear
    record_bound(Bound(
        "box-front", "The pack stands behind the appliance's stated front plane",
        front_need >= iy0 - stated_bound_tol,
        f"pack reaches y {front_need:.2f}, front wall at {iy0:.2f}",
        f"behind `front_plane_y` {front_plane_y:g}",
        ([] if front_need >= iy0 - stated_bound_tol else [
            f"the pack reaches y {front_need:.2f} but the front wall stands at {iy0:.2f} — "
            f"{iy0 - front_need:.2f} mm over. Lower `front_plane_y` or repack aft"])))
    rear_need = cymax + interior_clearance + rear_seam_clear
    record_bound(Bound(
        "box-depth", "The pack stands inside the appliance's stated depth",
        rear_need <= iy1 + stated_bound_tol,
        f"pack reaches y {rear_need:.2f}, back wall at {iy1:.2f}",
        f"ahead of `rear_plane_y` {rear_plane_y:g}",
        ([] if rear_need <= iy1 + stated_bound_tol else [
            f"the pack reaches y {rear_need:.2f} but the back wall stands at {iy1:.2f} — "
            f"{rear_need - iy1:.2f} mm over. Raise `rear_plane_y` or repack forward"])))
    # The floor is a fixed Z=0 datum, not the lowest content — so parts can stand
    # on feet above it (the floor and the seam lip stay put). The CEILING is
    # the stated `appliance_height` measured from the floor slab's underside: the
    # thin machine's height is a bound, not a consequence, so the tallest content
    # does not lift it and slack above the pack is the column the unpacked
    # subsystems go in.
    #
    # What the contents demand, measured against the bound rather than setting it, so a pack
    # that outgrows it says so instead of quietly poking through the top wall. The ±X wall
    # bands are measured separately: ONE boss on each of them hugs the ceiling — the Y seam's
    # top level, `2 * socket_r` of collar hanging off the top wall — so content inside its
    # station and inside a boss chain of the wall answers for that collar as well as for its
    # own height.
    #
    # IT IS THAT COLLAR AND NO OTHER. Every other boss on the flank stands somewhere down the
    # wall with air over it, and charging a body the ceiling's collar because it shares a
    # station with one of them would reserve headroom for material a hundred millimetres
    # below. The body that answers here is the one standing under the top collar.
    pod_stack = 2.0 * socket_r + 1.5              # ceiling → top collar's underside + margin
    ceiling_boss = [b for b in band_bosses if b[3] >= iz1 - 1e-6]
    wall_band_top = max(
        (b.zmax for b in bbs
         if (b.xmin < ix0 + boss_in or b.xmax > ix1 - boss_in)
         and _in_a_boss(b, ceiling_boss)),
        default=iz0)
    need = max(czmax + interior_clearance, wall_band_top + pod_stack)
    record_bound(Bound(
        "box-height", "The pack stands under the appliance's stated ceiling",
        need <= iz1 + stated_bound_tol,
        f"pack reaches z {need:.2f}, ceiling at {iz1:.2f}",
        f"under a {appliance_height:g} mm appliance",
        ([] if need <= iz1 + stated_bound_tol else [
            f"the pack reaches z {need:.2f} but a {appliance_height:g} mm appliance ceilings at "
            f"{iz1:.2f} — {need - iz1:.2f} mm over. Raise `appliance_height` or repack "
            f"downward"])))
    ox0, ox1 = ix0 - wall, ix1 + wall
    oy0, oy1 = iy0 - wall, iy1 + wall
    outer = (ox0, ox1, oy0, oy1, iz0 - wall, iz1 + wall)
    # The one thing the Y seam cannot do is cut the display housing: the facet is a
    # solid surface chamfered into the top-front arris and it prints as part of the
    # front-top piece, so the seam stands behind its back plane.
    facet_back = housing_back_y(outer)
    record_bound(Bound(
        "y-seam-clears-facet", "The Y seam stands behind the display housing",
        y_joint >= facet_back + 2.0,
        f"seam at {y_joint:.2f}, housing back plane at {facet_back:.2f}",
        f"aft of {facet_back + 2.0:.2f}",
        ([] if y_joint >= facet_back + 2.0 else [
            f"the Y seam at {y_joint:.2f} cuts the display housing, whose back plane is at "
            f"{facet_back:.2f} — the facet has to stay whole in the front pieces. Move "
            f"`y_seam` aft of {facet_back + 2.0:.2f}, or bring `display_housing_back` "
            f"forward"])))
    # The vertical cut squares off slab the funnel's throat wants, and what stops it is the
    # display's own SEATS — the inset the cover plate drops into and the bezel counterbore
    # under it. The PCB hole is not one of them: `display_pcb_cut_through` drives it past the
    # back on purpose, to take a socket collar clean through.
    seats = max(_seat_back(display_inset_depth, display_inset_slope / 2.0),
                _seat_back(display_bezel_depth, display_bezel_slope / 2.0))
    record_bound(Bound(
        "display-housing-seats", "The housing's back cut keeps a wall behind the display's seats",
        display_housing_back >= seats + wall,
        f"cut at {display_housing_back:.2f} aft of the front face, seats reach {seats:.2f}",
        f"a {wall:g} mm wall behind them, so aft of {seats + wall:.2f}",
        ([] if display_housing_back >= seats + wall else [
            f"`display_housing_back` {display_housing_back:.2f} stands "
            f"{seats + wall - display_housing_back:.2f} mm forward of where the display's "
            f"seats leave room — the deeper of the inset and the bezel counterbore reaches "
            f"{seats:.2f} aft of the front face, and the cut opens its back into the box. "
            f"Take `display_housing_back` aft of {seats + wall:.2f}"])))
    # What the seam's own furniture lands in: the socket collar's footprint, at the full
    # section the screw chain needs, which is the band `_bosses` places a level inside.
    # The plug opposite it stands within that same footprint at a shallower reach.
    fy0, fy1 = _y_corner(inner, y_joint)
    _measure_wall_block(placed, inner, fy0, fy1, boss_in)
    # WHAT THE COLUMNS GIVE UP. Measured here with everything else the placed pack decides,
    # against the same `inner` the columns are struck on.
    reliefs = []
    for sx, sy in column_corners:
        post = _corner_column(inner, sx, sy, 0.0, (iz0 - 1.0, iz1 + 1.0))
        for name, (solid, _c) in placed.items():
            hit = post.intersect(solid)
            if hit.Volume() <= 1e-6:
                continue
            # ONE POCKET PER LUMP THE BODY ACTUALLY STANDS IN, and not one for its whole
            # envelope. A brick's box is the brick; a condenser block's box is mostly air, and
            # a pocket struck on it would hollow the column over its whole height for the two
            # sheet flanges that are really in there. Each lump the intersection comes back in
            # gets its own box, so what a column gives up is what a body occupies.
            for lump in hit.Solids():
                b = lump.BoundingBox()
                # NO SLIP TOWARD THE TWO WALLS THIS COLUMN STANDS ON. A body in a corner has
                # its own standoff from each of them already — on the ±X wall that standoff IS
                # the tip of the boss it seats on, and a millimetre of air taken there is a
                # millimetre off the seat. The slip is for the faces a hand comes at.
                reliefs.append((sx, sy, name, _ybox(
                    b.xmin - (0.0 if sx < 0 else column_relief_slip),
                    b.xmax + (0.0 if sx > 0 else column_relief_slip),
                    b.ymin - (0.0 if sy < 0 else column_relief_slip),
                    b.ymax + (0.0 if sy > 0 else column_relief_slip),
                    b.zmin - column_relief_slip, b.zmax + column_relief_slip)))

    return Box(inner, outer, y_joint, splits,
               pack.front_ports, pack.back_ports, pack.east_ports, pack.west_ports,
               pack.funnel, pack.pan_sleeve, pack.c14, pack.east_bosses,
               pack.side_wells, pack.floor_bosses, pack.west_cradle, pack.cond_cradle,
               pack.cond_mount, pack.asse_cradle,
               pack.digiten_saddles, pack.tube_anchors, pack.port_field, pack.nameplate,
               pack.valve_panels, pack.pump_trays, pack.core_stops, pack.core_holds,
               pack.vent_chase, tuple(reliefs))


# --- display facet (solid surface) -----------------------------------------

def _facet_geom(outer):
    ox0, ox1, oy0, oy1, oz0, oz1 = outer
    a = math.radians(display_facet_angle_deg)
    dy = display_facet_slope * math.sin(a)   # back from the front face
    dz = display_facet_slope * math.cos(a)   # down from the top face
    normal = (0.0, -math.sin(a), math.cos(a))
    origin = (0.0, oy0 + dy / 2.0, oz1 - dz / 2.0)
    return a, normal, origin, dy, dz


def housing_back_y(outer):
    """The Y the display housing reaches back to — the vertical plane
    `display_housing_back` aft of the box's front face, cut the full width. The
    frontmost the Y seam may sit, since the whole facet belongs to the front top
    piece; and where the top wall resumes, which is the forward wall of the frame
    the funnel's collar stands in.

    ONE PLANE, NOT A REACH OFF THE 45°. The slab behind the face is
    `display_facet_thickness` thick measured perpendicular to it, which would put
    its back plane at a Y that walks with the slope and with the thickness — and
    at the top face that plane stands aft of everything the display needs, over
    the funnel's own throat. This states where the slab stops instead."""
    return outer[2] + display_housing_back


def _seat_back(depth, half_slope):
    """How far aft of the box's front face a pocket of `depth`, reaching
    `half_slope` up the 45° from the facet's centre, drives into the slab. Both
    terms are on the 45°, so each costs `sin 45°` of itself along Y."""
    s = math.sin(math.radians(display_facet_angle_deg))
    return display_facet_slope * s / 2.0 + (half_slope + depth) * s


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
    Re-cut after the socket collars so they too are chamfered to the facet plane rather
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
    `corner_round`, cavity one wall less (square once the inset reaches zero).

    THE HOUSING IS BOUNDED BEHIND BY TWO SURFACES: the 45° plane one
    `display_facet_thickness` in, and the vertical `housing_back_y` that squares
    off its top corner. Aft of that cut the cavity runs on to the ceiling, which
    is the room the funnel's throat drops through."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    ox0, ox1, oy0, oy1, oz0, oz1 = outer
    a, normal, origin, dy, dz = _facet_geom(outer)
    extent = max(ox1 - ox0, oy1 - oy0, oz1 - oz0) + 100.0

    inner_box = _cavity(inner)
    outer_chamfered = _rounded_outer(outer)

    back_origin = (origin[0] - display_facet_thickness * normal[0],
                   origin[1] - display_facet_thickness * normal[1],
                   origin[2] - display_facet_thickness * normal[2])
    keepout = _halfspace(back_origin, normal, extent).intersect(
        _ybox(ox0 - extent, ox1 + extent,
              oy0 - extent, housing_back_y(outer),
              oz0 - extent, oz1 + extent))
    inner_clipped = inner_box.cut(keepout)

    return cq.Workplane(obj=outer_chamfered.cut(inner_clipped))


def display_plane(outer):
    """The 45° face as a workplane centred on the glass — the frame everything let into the
    facet is struck in, and the frame `enclosure_assembly` poses the cover plate onto. Its
    +X is the box's, its +Y runs UP the slope, and its normal points out at the user, so a
    feature cut to depth `d` is extruded `-d`."""
    _a, normal, origin, _dy, _dz = _facet_geom(outer)
    center = (display_centre_x(outer), origin[1], origin[2])
    return cq.Plane(origin=cq.Vector(*center), xDir=cq.Vector(1, 0, 0), normal=cq.Vector(*normal))


def _display_cuts(outer):
    """The display let into the facet, down two steps, plus the lands its cover plate is
    screwed to. All of it is struck on `display_plane` and cut along the facet's 45° normal,
    starting one mm proud of the face for a clean break.

    THE INSET IS THE OUTER STEP and the bezel counterbore the inner one, so the glass sits
    `display_inset_depth` below the plate that laps it and the plate's own top lies in the
    45° plane. The inset runs `display_inset_reach` past the glass laterally — that land is
    what a countersunk head needs — and `display_inset_lap` past it up the slope, which is
    the border's own width.

    The glass is the datum: both rectangles are centred on the facet, which means centred on
    the BOX (`display_centre_x`), with flat 45° face all around. The glass overhangs the body
    unevenly, so the PCB hole sits offset by display_body_offset — and is cut
    display_pcb_cut_through past the back to take a socket collar (which would otherwise
    overhang it) clean through. Corners rounded to the display radius."""
    plane = display_plane(outer)
    normal = plane.zDir.toTuple()
    along_normal = cq.selectors.ParallelDirSelector(cq.Vector(*normal))
    inset = (
        cq.Workplane(plane).workplane(offset=1.0)
        .rect(display_inset_x, display_inset_slope)
        .extrude(-(display_inset_depth + 1.0))
        .edges(along_normal).fillet(display_corner_r).val()
    )
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
    cut = inset.fuse(bezel).fuse(pcb)
    for sx in (-1.0, +1.0):
        # The pocket the plate's pad drops into, and under it the insert the screw pulls
        # against. The bore starts at the pocket's floor, so the insert is set in printed
        # material and not in the air over the pad.
        px = sx * display_screw_x
        pad_floor = display_inset_depth + display_screw_pad_depth
        pocket = (
            cq.Workplane(plane).workplane(offset=-display_inset_depth)
            .center(px, 0.0)
            .circle((display_screw_pad_dia + 2.0 * display_screw_pad_slip) / 2.0)
            .extrude(-display_screw_pad_depth).val()
        )
        bore = (
            cq.Workplane(plane).workplane(offset=-pad_floor)
            .center(px, 0.0).circle(heatset_dia / 2.0)
            .extrude(-(heatset_depth + mount_bore_relief)).val()
        )
        cut = cut.fuse(pocket).fuse(bore)
    return cut


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


def _nameplate(solid, plate, outer, y_outer, zlo, zhi):
    """The nameplate's pocket, cut into a ±Y wall's outer face, and the two screw bosses standing
    behind it on the inner one.

    THE POCKET TAKES THE PLATE'S WHOLE THICKNESS and the wall keeps what is left under it. At each
    screw it goes one `pad_depth` deeper for the plate's own local thickening, and the boss behind
    that pocket is what the insert is set in: a collar as wide as the pocket needs a wall round it,
    and under it a stem round the insert alone.

    The plate lies wholly on one piece — `nameplate-field` is the reading that keeps it off the
    seam — so the station's own Z decides which piece carries all of it."""
    if plate is None or not (zlo <= plate.z <= zhi):
        return solid
    y_inner = y_outer - wall
    floor = y_outer - plate.thick - plate.pad_depth
    for dx, dz in plate.screws:
        sx, sz = plate.x + dx, plate.z + dz
        solid = solid.fuse(_ycyl(plate.collar_d / 2.0, sx, sz, floor, y_inner))
        solid = solid.fuse(_ycyl(plate.stem_d / 2.0, sx, sz, floor - plate.bore_depth, floor))
    solid = solid.cut(_rect_cut_y(plate.x, plate.z,
                                  plate.width + 2.0 * plate.slip,
                                  plate.height + 2.0 * plate.slip,
                                  plate.corner + plate.slip,
                                  y_outer - plate.thick, y_outer + 1.0))
    for dx, dz in plate.screws:
        sx, sz = plate.x + dx, plate.z + dz
        solid = solid.cut(_ycyl((plate.pad_d + 2.0 * plate.pad_slip) / 2.0, sx, sz,
                                floor, y_outer + 1.0))
        solid = solid.cut(_ycyl(plate.bore_d / 2.0, sx, sz, floor - plate.bore_depth, floor))
    return solid


def _port_chip(px, pz, width, rise, y0, y1):
    """One station's outline as a solid spanning `y0..y1` — a D lying on its back: a half circle
    of `width` below the bore's axis, and a rectangle that wide standing `rise` above it.

    The pocket and the boss behind it are the same shape at two sizes, so both are struck here.
    Built from primitives rather than sketched, so no plane's own chirality reaches the shape."""
    r = width / 2.0
    barrel = cq.Solid.makeCylinder(r, y1 - y0, cq.Vector(px, y0, pz), cq.Vector(0, 1, 0))
    return (barrel.intersect(_ybox(px - r, px + r, y0, y1, pz - r, pz))
            .fuse(_ybox(px - r, px + r, y0, y1, pz, pz + rise)))


def _port_field(solid, field, ports, outer, y_outer, zlo, zhi):
    """The pocket each port chip lies in, cut INTO a ±Y wall's outer face, and the boss standing
    behind it on the inner one — one pair per station.

    THE POCKET IS `proud` DEEP AND THE BOSS IS `proud` TALL, so the boss makes back exactly what
    the pocket took and the stock under every chip is the wall's own full thickness. What the
    customer meets is a flush face: colour and wall in one plane, with no pad standing off it.

    THE BOSS IS `rim` LARGER THAN THE CHIP ALL ROUND, and at this pitch two neighbours on one row
    run into each other and fuse into one longer boss. `enclosure_assembly.PORT_FIELD_WEB` is the
    reading that keeps the POCKETS apart.

    A boss goes on after the clip, on whichever piece holds its Z — `zlo..zhi` is that piece's
    band — and is clipped to the print silhouette, which is what runs the top row's three out into
    the top wall instead of standing them past it. The pocket is cut on every piece it reaches, so
    one straddling the seam is cut on both halves of it. Everything the wall carries through a
    station it carries through that station's boss too, so `ports` is bored here across the boss's
    own depth: the wall's holes are the wall's, and these are the bosses'."""
    if field is None:
        return solid
    ox0, ox1, _oy0, _oy1, _oz0, _oz1 = outer
    silhouette = _rounded_outer(outer)
    y_inner = y_outer - wall
    boss_y0 = y_inner - field.proud
    band = _ybox(ox0 - 1.0, ox1 + 1.0, boss_y0, y_inner, zlo, zhi)
    for px, pz, width, rise in field.pockets:
        boss = _port_chip(px, pz, width + 2.0 * field.rim, rise + field.rim, boss_y0, y_inner)
        solid = solid.fuse(boss.intersect(silhouette).intersect(band))
    for px, pz, width, rise in field.pockets:
        solid = solid.cut(_port_chip(px, pz, width, rise,
                                     y_outer - field.proud, y_outer + 1.0))
    for cutter in _port_cuts(ports, boss_y0 - 1.0, y_inner + 1.0):
        solid = solid.cut(cutter)
    return solid


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
    display facet's own back plane, inboard of the ±X boss chains, and ahead of the back
    wall.

    THE FRONT IS A DIFFERENT KIND OF EDGE FROM THE OTHER THREE. On those three the frame runs
    out into a free edge, and the collar stands one `hopper_funnel.brim_margin` inside it: the
    flange overhangs the collar by `brim_overhang` to catch the wall and hold the funnel out of
    the box, and the margin is the wider of the two, so a full overhang's width of top wall
    still remains outboard of the brim's edge. Forward the wall runs straight on into the
    display housing, whose back is the vertical `housing_back_y` — and the slab ahead of that
    cut is what the brim's front flange lands on. The front's requirement is
    `hopper_front_ledge`, the top wall kept between that plane and the throat itself, and it
    stands in this frame. `with_funnel` asks the margin of the three free edges."""
    ix0, ix1, _iy0, iy1, _iz0, _iz1 = inner
    return (ix0 + boss_in + hopper_chain_gap,           # clear of the −X chain's bosses
            ix1 - boss_in - hopper_chain_gap,           # clear of the +X chain's bosses
            housing_back_y(outer) + hopper_front_ledge, # behind the display housing
            iy1 - wall)                                 # ahead of the back wall


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
# back mouth, the front socket collar's +Y face on the lip rim — and the two are
# COAXIAL by construction (one y_boss, one z_boss feed both halves); the overlap
# (lip_len) is derived from exactly those matings, not chosen freely. An M3 SHCS
# drives in from the ±X exterior; outboard→inboard the joint reads: head
# counterbore, then the pin body (screw_len − heatset_depth of material the shank
# crosses), then the heat-set, then a one-wall cap.
#   * BACK half = PIN: a round cylinder from the ±X exterior to the heat-set,
#     registering in the socket bore. Sized to the screw SHANK, not the head (the
#     head sits in the wall counterbore); screw-clearance + head counterbore bored
#     in.
#   * FRONT lip = SOCKET: a collar round the bore — one `wall` of material and no
#     more — bored to receive the round pin (slide fit) with the heat-set + cap at
#     the deep inboard end.
# The head seats in the back wall; the shank crosses the pin body into the front
# heat-set, cross-pinning the two halves along X.
#
# Each stands on the joint's own overlap down its whole length: the plug in the back
# wall, the collar on the front lip's side band, which runs the piece's full height
# the way a telescoping lip does. Between two levels the corner is the wall's own air.

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
    """Per-boss tuple (x_in, x_ext, sx, z_boss): the inner ±X wall face the screw
    passes through, its matching exterior face, sx = +1 (left) / −1 (right)
    inboard, and the bore-axis height.

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

    The end levels sit one `wall` plus a bore radius off the floor and the ceiling,
    where a collar of one wall round the bore comes tangent to each."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    r = socket_bore_dia / 2.0
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
            out.append((x_in, x_in - sx * wall, sx, z_boss))
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
    registers in the front socket bore. Its −Y face stands on the seam mouth, and
    the wall it drives through carries it — the pin is that wall's own material for
    the first `wall` of its length and a stub of the same section beyond."""
    _xs, x_tip, _xh, _xc = _boss_x(x_ext, sx)
    return _xcyl(plug_dia / 2.0, y_boss, z_boss, x_ext, x_tip)


def _front_socket(x_in, x_ext, sx, z_boss, y_joint):
    """FRONT socket: a collar round the bore — a pipe standing off the ±X wall's
    inner face, from that face out to the cap over the insert's blind end, one
    `wall` of material round the bore its whole length.

    Its aft face lands on the lip rim (`_y_boss` + socket_r, which is what `lip_len`
    is struck from) and its forward face a hair ahead of the lip's own fusion
    shoulder, so it stands on the lip band down its whole length.

    Bore, heat-set and the plug's slide path are cut afterwards."""
    _xs, _xt, _xh, x_cap = _boss_x(x_ext, sx)
    xa, xb = sorted((x_in, x_cap))
    return _xcyl(socket_r, _y_boss(y_joint), z_boss, xa, xb)


def _front_cuts(x_in, x_ext, sx, z_boss, y_boss, y_joint):
    """Front-socket inner cuts at one level: the bore that receives the plug, the
    heat-set pocket at its deep end, and the +Y channel the plug travels down to
    reach the bore as the halves close — open at the rim, so it is a slide path and
    not a pocket.

    The slip lives on the +Y (slide-in) side: the bore is shifted +slip/2 so its −Y
    wall registers on the plug's −Y face at the mouth, instead of overshooting past
    the seam. The heat-set stays coaxial with the screw at y_boss, past the deep end
    of the channel."""
    _xs, x_tip, x_heat, _xc = _boss_x(x_ext, sx)
    bore_y = y_boss + split_slip / 2.0
    bore = _xcyl(socket_bore_dia / 2.0, bore_y, z_boss, x_in, x_tip)
    heat = _xcyl(heatset_dia / 2.0, y_boss, z_boss, x_tip, x_heat)
    bx0, bx1 = sorted((x_in, x_tip))
    chan = _ybox(bx0, bx1, bore_y, y_joint + lip_len + 1.0,
                 z_boss - socket_bore_dia / 2.0, z_boss + socket_bore_dia / 2.0)
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
# the derived lip_len then lands the socket collar's +Y face on the lip rim.
def _y_boss(y_joint):
    return y_joint + plug_dia / 2.0


# --- bottom↔top joint: the same telescoping lip + X-axis pins, rotated ------
#
# The BOTTOM pieces carry the lip and the socket collars; the TOP pieces carry the
# pins. The pin axis sits at z_pin = z_joint + plug_dia/2 (pin −Z face on the top
# piece's mouth), the collar's +Z face lands on the lip rim at z_joint + lip_len,
# and the top piece slides down over the lip — the pin dropping into the collar's
# +Z-open channel. Each is held by what it stands on: the pin by the wall it drives
# through, the collar by the lip band under it.


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
    piece; with it the pod keeps a full wall each side of its bore.

    AT THE REAR WALL the collar's own +Y face lies on that wall's inner face — unless the
    standing corner there carries a column, and then the lens runs forward to its cusp and
    would hole the collar's root. So that end answers the way the front column's front-wall
    station does (`_z_front_station_y`): one socket_r ahead of the cusp."""
    r = socket_bore_dia / 2.0
    plain = iy1 - wall - r
    if any(sy > 0 for _sx, sy in column_corners):
        plain = min(plain, iy1 - _column_along() - socket_r)
    return (y_joint + lip_len + z_lip_y_margin + wall + r, plain)


def _z_stations(inner, y_joint):
    """X-axis pin stations along the Z seams — TWO per ±X wall per Y column, one
    at each END of that column's seam, so a seam pinned only at one end cannot
    hinge open at the other.

    Front column: the front-wall corner — or, where that corner carries a column,
    behind it (`_z_front_station_y`) — and the aft end of its own lip, just
    ahead of where the Y-seam furniture starts. Back column: just behind the
    Y-seam mouth (where the telescoped front lip stops) and the rear-wall
    corner. Every station stands in the ±X band the walls' standoff opens off
    the cold core, and the depth between the two columns is what `east_band_free_y`
    hands a body hung on that wall. Each column's stations ride that column's own
    seam height."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    yf = _z_front_station_y(iy0)                    # front column, front wall
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
    THROUGH the box's standing-vertical arrises, so it is struck as the cavity's
    own one-`wall` skin (`_cavity`) rather than as a box: square corners would
    bite the rounded top-piece wall, and where a standing vertical carries a
    COLUMN the band wraps that column's face too — the pillar telescopes into the
    piece above it on the same one wall of overlap every other face uses."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    z0, z1 = zj - wall, zj + lip_len
    ring = _lip_band(inner, (z0, z1))
    gap = _ybox(ix0 - 1.0, ix1 + 1.0,
                y_joint - wall - z_lip_y_margin, y_joint + lip_len + z_lip_y_margin,
                z0 - 1.0, z1 + 1.0)
    return ring.cut(gap)


def _z_station_y(ys):
    """The Y band a Z station occupies — its collar's own reach, one socket_r
    either side of the bore axis, which is also what the pin inside it needs. Read
    by `_seam_furniture_spans` to say where the ±X chain bands have to stand clear,
    off the same figure the collar is built from."""
    return (ys - socket_r, ys + socket_r)


def _z_pod(x_in, x_ext, sx, ys, inner, zj):
    """BOTTOM socket: the Y-seam collar rotated — one pipe round the bore, off the
    ±X wall's inner face out to the cap, one `wall` of material round the bore its
    whole length. Its +Z face lands on the lip rim and its −Z face a hair under the
    lip's own fusion shoulder, so it stands on the lip band the whole way.

    Its upper half telescopes into the top piece, and a station abutting a wall sits
    in one of the box's rounded verticals — so the collar is held inside the cavity
    that piece rounds, concentric with it, and clear of whatever column stands in
    that cavity's corners."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    _xs, _xt, _xh, x_cap = _boss_x(x_ext, sx)
    xa, xb = sorted((x_in, x_cap))
    collar = _xcyl(socket_r, ys, _z_pin_z(zj), xa, xb)
    return collar.intersect(_cavity(inner, 0.0, (iz0 - 1.0, iz1 + 1.0)))


def _z_pin(x_ext, sx, ys, zj):
    """TOP pin: a round cylinder from the ±X exterior to the heat-set, registering
    in the bottom socket's bore. Its −Z face stands on the top piece's own mouth,
    so the wall it drives through carries the whole of it, and it drops down the
    socket's +Z channel as the pieces close."""
    _xs, x_tip, _xh, _xc = _boss_x(x_ext, sx)
    return _xcyl(plug_dia / 2.0, ys, _z_pin_z(zj), x_ext, x_tip)


def _z_pod_cuts(x_in, x_ext, sx, ys, zj):
    """Bottom-socket inner cuts: the bore that receives the pin, the heat-set
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
    # One collar per level, each standing on the lip band the lip has already put
    # down that wall.
    for x_in, x_ext, sx, z_boss in bosses:
        front = front.fuse(_front_socket(x_in, x_ext, sx, z_boss, y_joint))
    # A collar's forward face stands ahead of the seam plane, so the topmost one can
    # poke into the display facet; trim it to that plane. The facet runs wall to
    # wall, so it needs no end wall — both ends are the exterior side walls, which
    # seal themselves.
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
    for x_in, x_ext, sx, z_boss in bosses:
        front = front.cut(_front_cuts(x_in, x_ext, sx, z_boss, yb, y_joint))
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
    # One plug per level, standing on the back mouth off the wall it drives through.
    # The corner ahead of that mouth is the front lip's, whole.
    for x_in, x_ext, sx, z_boss in bosses:
        back = back.fuse(_back_plug(x_ext, sx, z_boss, yb))
    # Clip any corner feature that pokes past the rounded print silhouette.
    back = back.intersect(_rounded_outer(outer))
    for x_in, x_ext, sx, z_boss in bosses:
        back = back.cut(_screw_cut(x_ext, sx, z_boss, yb))
    # Panel through-holes for the appliance's external connections — the
    # faucet umbilical (carb-water + two flavor), the tap-water inlet, and
    # the C14 mains inlet, all through the back wall in the band above the
    # cold core; their bodies hang in the band's open rear half.
    for cutter in _port_cuts(box.back_ports, inner[3] - 5.0, outer[3] + 5.0):
        back = back.cut(cutter)
    back = _c14_bosses(back, inner, outer, box.c14, outer[4] - 1.0, outer[5] + 1.0)
    # The drip tray's withdrawal slot through the −X wall, and the sleeve it lies in. The
    # sleeve's own cuts reach back through this wall, so the slot is opened here and reopened
    # there at the one shape.
    for cutter in _x_port_cuts(box.west_ports, outer[0] - 5.0, inner[0] + 5.0):
        back = back.cut(cutter)
    back = _pan_sleeve(back, box.pan_sleeve, outer[4] - 1.0, outer[5] + 1.0)
    return cq.Workplane(obj=back)


def _pan_sleeve(solid, sleeve, z0, z1):
    """The drip tray's sleeve fused onto a −X wall and its berth cut back out, for a piece whose
    Z band holds the block's own top.

    The pack states the block as one world box rooted on that wall's inner face, and the berth
    as the two boxes the tray's own section makes. Fused THEN cut: the block closes the wall's
    slot on its way past and the berth reopens it, so the opening a hand meets from outside is
    the berth's own shape end to end."""
    adds, cuts = sleeve
    blocks = [b for b in adds if z0 <= b[5] <= z1]
    for x0, x1, y0, y1, bz0, bz1 in blocks:
        solid = solid.fuse(_ybox(x0, x1, y0, y1, bz0, bz1))
    for x0, x1, y0, y1, cz0, cz1 in (cuts if blocks else ()):
        solid = solid.cut(_ybox(x0, x1, y0, y1, cz0, cz1))
    return solid


def _floor_bosses(solid, inner, stations, y0, y1, z0, z1):
    """The floor slab's mounting bosses added to a PIECE, for the stations whose plan point
    the piece owns and whose slab it holds.

    Each station is `(x, y, tip, dia)`: the two plan coordinates the boss stands on, the plane
    its top face reaches, and the section the donor's own bore leaves it. The plane is where
    the screw's washer comes to rest — just under the crown of the grommet the post rises
    through — so the post runs UP from the slab's own inner face to it and the insert bore is
    cut back down from it. What the slab gives a screw is the standoff the body asked for, and
    what it gives the rubber is a squeeze that stops where the printed material does.

    The ±X walls take their bodies on the flank and the slab takes them from underneath, which
    is the whole difference between this and `_east_bosses`: the shaft runs on Z, the band that
    selects a station is the piece's Y column, and a station only lands on a piece whose Z band
    reaches the floor."""
    if z0 > inner[4] + 1e-6:
        return solid                       # a top piece has no slab to stand a post on
    for sx, sy, tip, dia in stations:
        if not (y0 <= sy <= y1):
            continue
        if (dia - floor_heatset_dia) / 2.0 < boss_ligament:
            raise ValueError(
                f"the floor post at ({sx:g}, {sy:g}) is Ø{dia:g}, which leaves "
                f"{(dia - floor_heatset_dia) / 2.0:g} of material round a Ø{floor_heatset_dia:g} "
                f"insert bore — under the {boss_ligament:g} a ±X wall boss keeps round its own. "
                f"This station's donor bore takes a smaller insert than the M5.")
        solid = solid.fuse(_zcyl(dia / 2.0, sx, sy, inner[4], tip))
        solid = solid.cut(_zcyl(floor_heatset_dia / 2.0, sx, sy,
                                tip - floor_heatset_depth - mount_bore_relief, tip))
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

    ON THE PIECE AND NOT ON THE HALF, because the Z seam's own socket collar is fused
    piece-side: where a station's height meets a mounting boss's, the two share the same
    material, and a bore cut before that collar is fused is a bore the collar fills back in.
    Cut here, the boss fuses nothing where the collar already stands and is bored through it
    all the same."""
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


# --- the PRV's chase, down the OUTSIDE of the west wall ----------------------
#
# The cold core's relief line leaves that core by a flank (`_internal_routes.prv_vent_cross_z`)
# and is cut flush with it. It arrives here pointing west, and this is what carries the
# discharge OUT OF THE BOX.
#
# ITS DEPTH COMES OUT OF A WALL THICKENED FROM THE INSIDE, into the band the core already
# stands off, and the outer face stays the plane `outer` names.
#
# THE LIP LANDS ON THE CORE. The rib's east face is the core's own west flank, so the mouth
# closes on that flank all round the tube's cut end. The core is located by its own two corner
# blocks and comes down as one unit (`cards/en-05-seat-cold-core`), so what the wall presents
# it is a target and not a fit: the mouth is `vent_channel_w` on a side against a tube less
# than half that across, and the balance is the room the core has to land in.
#
# Behind the mouth the passage turns DOWN. It is roofed by the rib and the wall's SKIN stands
# outboard of it, so the flank is unbroken at that height. `vent_duct_drop` under the mouth the
# skin opens, and the passage carries on as a three-walled groove.
#
# AND THE GROOVE ENDS BY RUNNING OUT. Its floor ramps back to the outer face over
# `vent_ramp_rise`, so the recess grows shallower until it is gone, and the flow reaches the
# face travelling away from it, well above the foot. CO2 is heavier than air and falls from
# there on its own.
vent_channel_w = 12.0          # the channel, across — and the mouth, square on it
vent_rib_wall = 2.0            # PETG either side of the channel, behind it, and over the mouth
vent_duct_drop = 25.0          # the closed fall under the mouth, before the skin opens
vent_groove_drop = 25.0        # the open groove under that, which the duct discharges into
vent_ramp_rise = 40.0          # over which the floor runs back out and turns the flow west


def _vent_chase(solid, inner, outer, stations, y0, y1, z0, z1):
    """The PRV vent's chase on a −X wall PIECE, for the station inside the band it owns.

    One station, `(x, y, z)`: the core's own west flank and the tube's own axis where it comes
    through, in the machine's own frame. A RIB is fused up the wall's inner face OUT TO THAT
    FLANK, and the whole passage is cut back out of it in ONE profile — mouth, roofed duct, open
    groove and run-out ramp are one polygon, one passage, and what changes down it is how much
    of the wall is still standing outboard of it. The mouth is `vent_channel_w` square, on the
    tube's own axis, and its lip is the rib's east face — the face that lands on the core.

    THE RIB RUNS OUT WITH THE RAMP. It stands behind the channel's floor, so it reaches as far
    down as that floor is still inboard of what the skin alone stands `vent_rib_wall` behind.
    Under that the ramp is cutting skin the wall already had, and the rib ends on the ramp's
    own slope."""
    for sx, sy, sz in stations:
        if not (y0 <= sy <= y1 and z0 <= sz <= z1):
            continue
        half = vent_channel_w / 2.0 + vent_rib_wall
        rib_x = sx                                  # the lip, on the core's own flank
        floor_x = rib_x - vent_rib_wall             # the channel's back face, all the way down
        mouth_top = sz + vent_channel_w / 2.0
        mouth_bot = sz - vent_channel_w / 2.0
        groove_top = sz - vent_duct_drop            # where the skin opens
        ramp_top = groove_top - vent_groove_drop
        ramp_bot = ramp_top - vent_ramp_rise        # where the floor has met the outer face
        # The ramp is carried one more millimetre of DEPTH past that, out into air.
        over = vent_ramp_rise / (floor_x - outer[0])
        # And the rib to where the skin alone stands `vent_rib_wall` behind the floor.
        rib_end = ramp_top - vent_ramp_rise * ((floor_x - (inner[0] - vent_rib_wall))
                                               / (floor_x - outer[0]))
        solid = solid.fuse(_xz_prism(sy - half, sy + half,
                                     [(inner[0], sz + half), (rib_x, sz + half),
                                      (rib_x, ramp_top), (inner[0], rib_end)]))
        solid = solid.cut(_xz_prism(sy - vent_channel_w / 2.0, sy + vent_channel_w / 2.0,
                                    [(rib_x + 1.0, mouth_top),       # the mouth, through the lip
                                     (rib_x + 1.0, mouth_bot),
                                     (floor_x, mouth_bot),           # \ the floor, straight down
                                     (floor_x, ramp_top),            # /  behind duct and groove
                                     (outer[0] - 1.0, ramp_bot - over),   # the ramp, run out
                                     (outer[0] - 1.0, groove_top),   # the groove's open side
                                     (inner[0], groove_top),         # over it the skin stands,
                                     (inner[0], mouth_top)]))        # and that roofs the duct
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


def _cond_cradle(solid, inner, stations, y0, y1, z0, z1):
    """The condenser block's FORE rails added to a PIECE, one per fore flange, for the stations
    inside the depth and height band that piece owns.

    Each station is `(face, x0, x1, fz0, fz1, root)`: the plane the block's fore face comes to
    rest on, that flange's own width, its two faces in height, and how far the rail runs DOWN
    under it. A rail is one slab off the front wall's inner face, out to `cond_slot_grip` past
    the face — and the groove is cut out of that last stretch alone, so what stands fore of the
    block is solid material and the flange bottoms on it. THE RAIL IS THE DATUM: the block's
    reach into the bay is its own depth and not a number typed here.

    The BASE rail's `root` is the slab, so it comes out of the print as a corner bracket in one
    piece with both faces it stands on. The CROWN rail's is one section under its own groove, and
    it hangs off the wall.

    THE GROOVE IS STRUCK OFF THE FLANGE IT TAKES and not off a figure typed here: `cond_slot_half`
    reads the station's own sheet. The rail's crown stands one section over that opening, so it
    follows the groove wherever the sheet in it puts it."""
    for face, cx0, cx1, fz0, fz1, root in stations:
        if not (y0 <= face <= y1 and z0 <= (fz0 + fz1) / 2.0 <= z1):
            continue
        half = cond_slot_half(fz1 - fz0)
        solid = solid.fuse(_ybox(cx0, cx1, inner[2], face + cond_slot_grip,
                                 root, fz1 + half + cond_rail_wall))
        # The groove runs out past the rail's own aft end, so the flange enters from the bay.
        solid = solid.cut(_ybox(cx0 - 1.0, cx1 + 1.0, face, face + cond_slot_grip + 1.0,
                                fz0 - half, fz1 + half))
    return solid


def _cond_mount(solid, inner, station, y0, y1, z0, z1):
    """The condenser block's AFT mount added to a PIECE: one fin on the +X wall and a finger
    reaching west off it under each of the block's two mount holes.

    The station is `(flank, my0, my1, bosses)`: the plane the fin's own west face stands on —
    the block's east flank and one `cond_mount_clear` — the Y band the whole of this occupies,
    and one `(x, y, tip)` per hole, where `tip` is the face of the flange that screw pulls down.

    THE LOWEST FINGER RUNS TO THE SLAB, because nothing stands between its own tip and the floor
    and the block's aft end comes down on it. Every other is one `cond_boss_t` deep and hangs off
    the fin, which is the only thing it can hang off: the recess it reaches into has the base
    flange for a floor, so no column may root inside the block's own flanks."""
    if not station:
        return solid
    flank, my0, my1, bosses = station
    if not (y0 <= (my0 + my1) / 2.0 <= y1 and z0 <= inner[4] <= z1):
        return solid
    crown = max(t for _bx, _by, t in bosses)
    floor_tip = min(t for _bx, _by, t in bosses)
    if floor_tip - inner[4] < cond_bore_depth - 1e-6:
        raise ValueError(
            f"the lowest condenser flange stands {floor_tip - inner[4]:g} over the slab and the "
            f"boss under it carries a {cond_bore_depth:g} bore — a body set down closer than its "
            f"own insert is a body whose screw has nowhere to close. Stand it off by at least "
            f"that, or capture that flange the way the fore pair is captured.")
    west = min(bx for bx, _by, _t in bosses) - mount_boss_dia
    for bx, by, _tip in bosses:
        room = min(bx - west, inner[1] - bx, by - my0, my1 - by) - heatset_dia / 2.0
        if room < boss_ligament:
            raise ValueError(
                f"the condenser boss at ({bx:g}, {by:g}) keeps {room:g} of material round its "
                f"Ø{heatset_dia:g} insert bore, under the {boss_ligament:g} every boss in this "
                f"box keeps round one. The hole has moved off the band this finger stands in.")
    solid = solid.fuse(_ybox(flank, inner[1], my0, my1, inner[4], crown))
    for bx, by, tip in bosses:
        root = inner[4] if tip == floor_tip else tip - cond_boss_t
        solid = solid.fuse(_ybox(west, inner[1], my0, my1, root, tip))
    for bx, by, tip in bosses:
        solid = solid.cut(_zcyl(heatset_dia / 2.0, bx, by, tip - cond_bore_depth, tip))
    return solid


def _core_stops(solid, inner, stations, y0, y1, z0, z1):
    """The cold core's two front corner blocks added to a PIECE, for the stations whose plan
    point the piece owns and whose slab it holds.

    Each station is `(cx, cy, r)`: the centre of the core's own corner round and that round's
    radius. Everything else the block is comes off those three and the box's own faces — it runs
    the ±X wall inboard to one round past the tangent, the slab up `core_stop_rise`, and one
    `core_stop_web` ahead of the core's outline the whole way.

    THE POCKET IS THAT OUTLINE, OFFSET ONE SLIP AND NOT A SHAPE OF ITS OWN: a bore on the round's
    own axis outboard of the tangent, a plane on the core's own front face inboard of it. So the
    web is the same 6 mm at the tangent, where a bore alone leaves it thinnest, and along the
    whole lap — and the block bears flat where the core is flat and round where it is round.

    Its underside is the slab and its outboard face the wall, so it comes out of the print as a
    corner bracket in one piece with both faces it stands on — the card slot's own form, on the
    body that needs no slot. The band test is `_floor_bosses`': the Y column selects the station
    and only a piece reaching the floor grows one."""
    if z0 > inner[4] + 1e-6:
        return solid                       # a top piece has no slab to stand one on
    for cx, cy, r in stations:
        if not (y0 <= cy <= y1):
            continue
        side = 1.0 if cx > 0.0 else -1.0
        slip = core_stop_slip / 2.0
        wall_x = inner[1] if side > 0 else inner[0]
        lap, face = cx - side * r, cy - r - slip
        tip = inner[4] + core_stop_rise
        solid = solid.fuse(_ybox(min(lap, wall_x), max(lap, wall_x),
                                 face - core_stop_web, cy, inner[4], tip))
        solid = solid.cut(_ybox(min(lap, cx), max(lap, cx), face, cy + 1.0,
                                inner[4] - 1.0, tip + 1.0))
        solid = solid.cut(_zcyl(r + slip, cx, cy, inner[4] - 1.0, tip + 1.0))
    return solid


def _core_holds(solid, inner, stations, y0, y1, z0, z1):
    """The cold core's two hold-down brackets added to a PIECE, for the stations inside the
    depth and height band that piece owns.

    Each station is `(x0, x1, aft, crown)`: the lane on the cap the bracket stands in, the
    core's own aft face, and the plane its cap presents. Its section is a right trapezoid on
    those two planes — the BEARING FACE along the crown from `core_hold_reach` forward of the
    core's aft face back to the wall, the LEG up the wall's inner face for `core_hold_rise`, and
    one straight from the head of that leg down to the foot's own tip, which is `core_hold_land`
    over the crown. The foot lands on the cap at 0, the way every other seat in this box lands
    on the face it takes.

    THAT STRAIGHT IS BOTH THE GUSSET AND THE PRINT. It leaves no re-entrant corner for the foot
    to bend at, and printed ceiling-down it descends toward the tip at 25° off vertical, so every
    layer of the foot is laid on the one above it and nothing under this bracket needs support."""
    for sx0, sx1, aft, crown in stations:
        if not (y0 <= aft <= y1 and z0 <= crown <= z1):
            continue
        tip, back = aft - core_hold_reach, inner[3]
        solid = solid.fuse(_yz_prism(sx0, sx1, (
            (tip, crown), (back, crown), (back, crown + core_hold_rise),
            (tip, crown + core_hold_land))))
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
# TWO STRAPS, AND WHAT PICKS BETWEEN THEM IS THE LOOP. A strap turns INSIDE the cavity, so what it
# reaches round is the body together with the web between that body and the cavity — the convex
# perimeter of the pair, and not of the wall the rib stands on:
#
#     carb-1 tube in its rib      [40.1 mm](LOOP_CARB_1)
#     DIGITEN arm in its saddle   55.2 mm
#     WR1110 barrel in its rib    [84.1 mm](LOOP_WR1110)
#     ASSE barrel in its trough  100.6 mm
#
# A 4" tie closes about 69 mm of loop, which takes the first two; the regulator's takes the 6",
# which closes about 110. The ASSE barrel's passes both and takes the 8", and an 8" tie is a 50 lb
# tie at 0.19" where the rest are 18 lb at 0.1" — so that trough's cavity, alone on this box, is
# cut to the wider strap. Every other cavity here takes the same 0.1" section at any length.
tie_strap_w = 2.5           # the 18 lb strap, across its width — 0.1"
tie_strap_wide_w = 4.826    # and the 50 lb strap's — 0.19"
tie_strap_t = 1.0           # both, through the thickness
tie_cav_buffer = 1.0        # the room a cavity carries over the strap
tie_cav_w = tie_strap_w + tie_cav_buffer
tie_cav_wide_w = tie_strap_wide_w + tie_cav_buffer
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
    #
    # IT IS THE WIDE STRAP'S CAVITY. The barrel and this trough make a 100 mm loop, past what a 4"
    # tie closes, so what shuts it is the 8" — and an 8" is a 50 lb tie, half again as wide as the
    # 18 lb strap the meter's saddles and the runs' ribs take.
    for ty in ties:
        if not (sections[0][0] <= ty <= sections[-1][1]):
            raise ValueError(
                f"_asse_cradle: tie band {ty:.2f} falls outside the trough's run "
                f"[{sections[0][0]:.2f}, {sections[-1][1]:.2f}]. The cavity a strap passes through "
                f"is the trough's whole length, so a band off either end has no cavity at all.")
    return solid.cut(_asse_tie_cavity(min(w for _y0, _y1, w, _r, _a in sections), inner[0], z_axis,
                                      min(ties) - tie_cav_wide_w / 2.0,
                                      max(ties) + tie_cav_wide_w / 2.0, up, dn))


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


# --- the flavour manifold's valve panels ------------------------------------
#
# A PANEL IS A PLATE WALL TO WALL, carrying one four-boss `valve_seat` per valve on the deck it
# stands under. `valve_panel` states its thickness, its margin and its seat height and draws one
# in its own frame; this turns that onto the deck's own plane and fuses it into the piece, the
# way `_asse_cradle` fuses the trough and `_digiten_saddles` the meter's two Vs.
#
# NOTHING FASTENS A VALVE TO IT. The four corner posts press into their sockets and the valve's
# own round body boss lands on the boss tops, which is what sets its height — the same bargain
# the cold core's cap lid strikes under its own three valves.
def _valve_panels(solid, inner, stations, y0, y1, z0, z1):
    """Every valve panel whose deck falls in the depth and height band this piece owns.

    Each station is `(plane, sign, seats)`: the world Y the deck's valves stand their mounting
    faces on, which way their own +Z runs off it, and one `(x, z)` per valve. The plate's own
    extent is the seats' — wall to wall across, and one `valve_panel.reach` plus a margin either
    way along — so nothing here is a dimension this module chose."""
    for plane, sign, seats in stations:
        zs = [z for _x, z in seats]
        mid_z = (min(zs) + max(zs)) / 2.0
        half = _panel.height() / 2.0
        if not (y0 <= plane <= y1 and z0 <= mid_z <= z1):
            continue
        # The plate: its valve-side face on the deck's own plane, its back one `THICK` outboard.
        face = plane - sign * _panel.SEAT
        near, far = sorted((face, face - sign * _panel.THICK))
        solid = solid.fuse(_ybox(inner[0], inner[1], near, far, mid_z - half, mid_z + half))
        # And a seat under each valve, drawn in the valve's own frame and turned onto the deck.
        for sx, sz in seats:
            seat = _seat.build_seat(_panel.SEAT).val()
            seat = seat.moved(cq.Location(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0),
                                          -90.0 if sign > 0 else 90.0))
            solid = solid.fuse(seat.moved(cq.Location(cq.Vector(sx, face, sz))))
    return solid


# --- the flavour manifold's pump trays --------------------------------------
#
# A TRAY IS THE PUMP CASE WITH ITS CYLINDER CUT OFF — `pump_case`'s base plate, its ramp, its
# octagon bore wall and one shoulder of its tower, so it wraps the head's crown AND the boss's.
# `pump_tray` states what that cut adds and draws one in the pump's own frame; this roots it on
# the front wall and fuses it into the piece, the way `_valve_panels` fuses a plate and
# `_digiten_saddles` the meter's two Vs.
#
# THE STRAPS ARE WHAT HOLD A PUMP UP. It hangs under its tray, so two close round it and the
# tray together through the plate's four channels, reaching under the bracket the part carries at
# that crown — the meter's bargain, on the heaviest body either wall carries.
def _pump_trays(solid, inner, stations, y0, y1, z0, z1):
    """Every pump tray whose whole run falls in the depth and height band this piece owns.

    Each station is the world point a pump's axis meets the +Z face of its head, which is
    `pump_case`'s own base plane. The pumps stand their cans on +Z and their trays run to the
    FRONT wall, so a tray reaches from that point to `inner[2]` and `pump_tray`'s own frame lands
    on it with no turn in it."""
    for cx, cy, cz in stations:
        root = cy - inner[2]
        if not (y0 <= inner[2] and cy + _tray.far_reach() <= y1
                and z0 <= cz and cz + _tray.depth() <= z1):
            continue
        tray = _tray.build_pump_tray(root).val()
        solid = solid.fuse(tray.moved(cq.Location(cq.Vector(cx, cy, cz))))
    return solid


# A TRAY IS A CANTILEVER OFF THE FRONT WALL AND NOTHING ELSE, and these are what it meets on
# every other side: one web to each side wall, one between the two trays, and one aft onto the
# valve panel the fold stands behind them. Each is the trays' own plate — `pump_tray.PLATE`
# thick, in that plate's own band — so the whole storey comes out one plate wall to wall.
def _tray_webs(solid, inner, stations, panels, y0, y1, z0, z1):
    """The webs that tie every pump tray in this piece's band to what stands beside it.

    The trays stand their plates on ONE storey — they are the same pump on one deck — so the
    band is theirs and every web is a box in it. Across, the gaps are what the plates leave
    between the two interior faces; aft, it is what one leaves in front of the nearest panel
    plate crossing that same band."""
    live = [(cx, cy, cz) for cx, cy, cz in stations
            if (y0 <= inner[2] and cy + _tray.far_reach() <= y1
                and z0 <= cz and cz + _tray.depth() <= z1)]
    if not live:
        return solid
    storey = {(round(cy, 6), round(cz, 6)) for _cx, cy, cz in live}
    if len(storey) != 1:
        raise ValueError(
            f"_tray_webs: the trays in this piece stand on {len(storey)} storeys ({storey}). A "
            f"web is one box in one band, so trays on their own decks each want their own.")
    cy, cz = storey.pop()
    zb0, zb1 = cz, cz + _tray.PLATE
    far, hw = cy + _tray.far_reach(), _tray.half_width()
    # A WEB IS THE AIR BETWEEN A TRAY AND WHAT IT REACHES, and the air stops where the cavity
    # does. Its standing corners are relieved for the print bed (`corner_round`), so a box run to
    # the nominal interior planes stands OUTSIDE the shell at every corner it reaches. Each web
    # is clipped to the cavity itself rather than to those planes.
    cavity = _round_z(_ybox(*inner), corner_round - wall)
    # ACROSS: the wall, each tray's two flanks in turn, and the far wall. What the pairs leave
    # between them is exactly the air, so a tray that grows closes its own web rather than
    # overlapping it.
    edges = ([inner[0]]
             + [v for cx in sorted(cx for cx, _y, _z in live) for v in (cx - hw, cx + hw)]
             + [inner[1]])
    for a, b in zip(edges[0::2], edges[1::2]):
        if b - a > 1e-9:
            solid = solid.fuse(_ybox(a, b, inner[2], far, zb0, zb1).intersect(cavity))
    # AND AFT onto the nearest panel plate that crosses this same band — its own near face, so
    # the two meet plane to plane and the web is the gap and not a millimetre more.
    reach = None
    for plane, sign, seats in panels:
        zs = [z for _x, z in seats]
        mid_z, half = (min(zs) + max(zs)) / 2.0, _panel.height() / 2.0
        if mid_z + half <= zb0 or mid_z - half >= zb1:
            continue                       # a panel on another storey is not this web's
        face = plane - sign * _panel.SEAT
        near = min(face, face - sign * _panel.THICK)
        if near >= far - 1e-9 and (reach is None or near < reach):
            reach = near
    if reach is not None and reach - far > 1e-9:
        solid = solid.fuse(_ybox(inner[0], inner[1], far, reach, zb0, zb1).intersect(cavity))
    return solid


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


def tube_anchor_strap_loop(seat_r: float) -> float:
    """The shortest strap that closes round a seated body and its rib together.

    A strap turns INSIDE the channel, so what it reaches round is the body with the rib's own
    back behind it — the convex perimeter of that pair, and not of the wall the rib stands on.
    Read on the bore, which is the section this box knows.

    The hull is the rib's rectangle with a cap of the bore over it: the channel's floor, the
    rib's two flanks down to the axis plane, a tangent from each corner onto the bore, and the
    arc between the two tangent points. Floor and flank are both `seat_r + wall`, so the
    rectangle is square and the whole figure is a function of the seat."""
    w = seat_r + wall
    return (4.0 * w + 2.0 * math.sqrt(w * w - seat_r * seat_r)
            + seat_r * (math.pi - 2.0 * math.acos(seat_r / w)))

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
    lip + socket collars, the top taking the pins + X-axis screw bores.
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
        for x_in, x_ext, sx, ys, _c in stations:
            piece = piece.fuse(_z_pod(x_in, x_ext, sx, ys, inner, zj))
        for x_in, x_ext, sx, ys, _c in stations:
            piece = piece.cut(_z_pod_cuts(x_in, x_ext, sx, ys, zj))
    else:
        piece = solid.intersect(_ybox(ox0 - 1.0, ox1 + 1.0, oy0 - 1.0, oy1 + 1.0,
                                      zj, oz1 + 1.0))
        for _x_in, x_ext, sx, ys, _c in stations:
            piece = piece.fuse(_z_pin(x_ext, sx, ys, zj))
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
        # The port field goes on here too, but INSIDE that silhouette: its pockets are cut into
        # the wall's outer face and its bosses stand off the inner one, so the face the customer
        # meets is flush. The bosses carry the face's own through-holes across their depth, so a
        # bore that crosses the wall crosses them too.
        piece = _port_field(piece, box.port_field, box.back_ports, outer, oy1, zlo, zhi)
        # And the nameplate's own pocket on that same face, with its two screw bosses behind it.
        # After the field, so a boss standing on this wall stands on a wall the field has already
        # finished with.
        piece = _nameplate(piece, box.nameplate, outer, oy1, zlo, zhi)
    # The +X wall's mounting bosses, on whichever piece holds each one's station. Last of
    # all, so a bore is cut through every column that has already been fused around it.
    ylo, yhi = ((oy0 - 1.0, y_joint) if y_side == "front" else (y_joint, oy1 + 1.0))
    piece = _east_bosses(piece, inner, box.east_bosses, ylo, yhi, zlo, zhi)
    # The +X wall's Wago wells, on whichever piece holds each one's station. After the
    # bosses for the same reason those go after the seam's own bosses: a pocket cut here is a
    # pocket nothing later fuses back in.
    piece = _side_wells(piece, inner, box.side_wells, ylo, yhi, zlo, zhi)
    # The floor slab's, on whichever piece holds each one's plan station. Only the bottom
    # pieces have a slab to stand one on, and `_floor_bosses` drops any station outside.
    piece = _floor_bosses(piece, inner, box.floor_bosses, ylo, yhi, zlo, zhi)
    # The −X wall's card slot, last of all: its bottom rail lands on the same slab those posts
    # rise from, so cutting its grooves after them is what keeps a groove a groove.
    piece = _west_cradle(piece, inner, box.west_cradle, ylo, yhi, zlo, zhi)
    # The condenser block's four flanges, on the same slab and the walls either side of it: the
    # fore rails off the front wall, the aft fin off the +X one. After the floor's posts for the
    # card slot's own reason — a rail rooted on the slab is rooted on whatever is standing there.
    piece = _cond_cradle(piece, inner, box.cond_cradle, ylo, yhi, zlo, zhi)
    piece = _cond_mount(piece, inner, box.cond_mount, ylo, yhi, zlo, zhi)
    # The cold core's own two: the front corner blocks on the same slab those rails root on, and
    # the hold-down brackets a storey up on the back wall. The blocks carry a bore, so they go on
    # with the other pockets — after everything that could fuse material back into one.
    piece = _core_stops(piece, inner, box.core_stops, ylo, yhi, zlo, zhi)
    piece = _core_holds(piece, inner, box.core_holds, ylo, yhi, zlo, zhi)
    # And the core's relief, which leaves it by a flank and needs somewhere to go: the rib is
    # fused before the channel is cut out of it, which is the same order the card slot takes.
    piece = _vent_chase(piece, inner, outer, box.vent_chase, ylo, yhi, zlo, zhi)
    # And the tap-water chain's, on the same wall a storey up. After the tray's rails, whose
    # band it stands over, and last like every other pocket: its tie slots are cut out of the
    # trough this fuses, so nothing may fuse into them afterwards.
    piece = _asse_cradle(piece, inner, box.asse_cradle, ylo, yhi, zlo, zhi)
    # And the flow meter's two saddles off the same piece's ceiling.
    piece = _digiten_saddles(piece, inner, box.digiten_saddles, ylo, yhi, zlo, zhi)
    # And the flavour manifold's valve panels, on whichever piece owns each deck's band. A plate
    # wall to wall with its seats standing on it, so it goes on after the wells and the bosses
    # for the same reason they go after the seam's own bosses.
    piece = _valve_panels(piece, inner, box.valve_panels, ylo, yhi, zlo, zhi)
    # And that manifold's two pump trays, on the piece that owns the band each plate lies in.
    # After the panels, whose own plate stands one behind them on the same storey.
    piece = _pump_trays(piece, inner, box.pump_trays, ylo, yhi, zlo, zhi)
    # And the webs that tie those trays to the walls, to each other and aft onto the panel —
    # after both, because what each one spans is the air the two left between them.
    piece = _tray_webs(piece, inner, box.pump_trays, box.valve_panels, ylo, yhi, zlo, zhi)
    # And the runs' own anchors, on whichever face each one stands nearest. Last, for the same
    # reason the trough is: every one of these is a rib with a cavity cut through it.
    piece = _tube_anchors(piece, inner, box.tube_anchors, ylo, yhi, zlo, zhi)
    # And then the columns give up whatever the pack stands in them (`_column_relief`), which is
    # last of everything: a relief is air, and air a later step fuses back in is not a relief.
    # Clipped to the column itself, so what a pocket can ever take is the pillar and never the
    # wall behind it or the boss beside it.
    for sx, sy, _name, room in box.column_reliefs:
        post = _corner_column(inner, sx, sy, 0.0, (inner[4] - 1.0, inner[5] + 1.0))
        piece = piece.cut(room.intersect(post))
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
        zs = sorted(z for _xi, _xe, s, z in bosses if s == sx)
        print(f"  Y-seam levels {label} wall: {len(zs)} — "
              + ", ".join(f"{z:.0f}" for z in zs))


def build_pieces(box):
    """The four printable pieces of one box, and the assembly of them in place
    with the seams intact — one box description in, four pieces out.

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
    assy = cq.Assembly(name="enclosure")
    for name, piece in pieces.items():
        assy.add(piece, name=f"enclosure-{name}".replace("-", "_"),
                 color=PIECE_COLORS[name])
    return pieces, assy


def _export_pieces(pieces, assy):
    for name, piece in pieces.items():
        export_assembly(one_body(piece, f"enclosure-{name}", PIECE_COLORS[name]),
                        str(_here.parent / f"enclosure-{name}.step"))
        print(f"-> enclosure-{name}.step")
    export_assembly(assy, str(_here.parent / "enclosure.step"))
    print("-> enclosure.step (assembled pieces)")


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


def _report_columns(box):
    """Each standing corner's column, and what it gave up to the pack standing in it.

    A relief is a decision the pack made for the box, so it is printed rather than assumed:
    a column quietly hollowed over most of its height is one to look at."""
    for sx, sy in column_corners:
        label = f"{'X-' if sx < 0 else 'X+'}/{'Y-' if sy < 0 else 'Y+'}"
        gave = [(n, r) for csx, csy, n, r in box.column_reliefs if (csx, csy) == (sx, sy)]
        if not gave:
            print(f"  column {label}:   whole")
            continue
        print(f"  column {label}:   relieved for " +
              ", ".join(f"{n} (z {r.BoundingBox().zmin:.1f}..{r.BoundingBox().zmax:.1f})"
                        for n, r in gave))


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

    _export_pieces(pieces, assy)

    print("enclosure:")
    _report_columns(box)
    _report_facet(pieces["front-top"], box)
    _report_seams(box)
    _report_levels(box)
    _report_split(pieces, machine.placed["foam-assembly"][0])

    bo = box.outer
    # The loops this box's ribs close, read off the seats the pack actually bored. Every rib
    # holding a RUN is bored for the one stock; the ribs holding a BODY are bored for whatever
    # section that body offers, so the radii are as many as the pack has kinds of seat. The
    # smallest is the runs' own and the largest is the widest body's, and a strap cut to the
    # largest closes on every one of them — which is what the table quotes.
    seats = sorted({round(r, 6) for *_s, r in (machine.tube_anchors or ())})
    if not seats:
        raise ValueError(
            "the box bores no tube anchor at all, and the strap table quotes a loop for them. "
            "Either the pack stands a rib again or the table stops reading one.")
    variables = {
        "LOOP_CARB_1": f"{tube_anchor_strap_loop(seats[0]):.3g} mm",
        "LOOP_WR1110": f"{tube_anchor_strap_loop(seats[-1]):.3g} mm",
        "ANCHOR_SEATS": ", ".join(f"{2 * r:.4g}" for r in seats),
        "DISPLAY_FACET_X": f"{display_facet_x:.4g} mm",
        "DISPLAY_FACET_SLOPE": f"{display_facet_slope:.4g} mm",
        "DISPLAY_INSET_X": f"{display_inset_x:.4g} mm",
        "DISPLAY_INSET_SLOPE": f"{display_inset_slope:.4g} mm",
        "DISPLAY_SCREW_X": f"{display_screw_x:.4g} mm",
        "MQ6_CARD_T": f"{mq6_card_y:.4g} mm",
        "MQ6_SLOT_OPEN": f"{mq6_card_y + 2 * mq6_slot_press:.4g} mm",
        "COND_SLOT_OPEN": f"{cond_slot_open:.4g} mm",
        "CORE_STOP_BORE": (f"{2.0 * (machine.core_stops[0][2] + core_stop_slip / 2.0):.4g} mm"
                           if machine.core_stops else "no station"),
        "CORE_STOP_WEB": f"{core_stop_web:.4g} mm",
        "CORE_STOP_RISE": f"{core_stop_rise:.4g} mm",
        # The block runs the wall inboard to one round past the tangent, and both are mirrored.
        "CORE_STOP_WIDE": (
            f"{interior_x()[1] - (abs(machine.core_stops[0][0]) - machine.core_stops[0][2]):.4g} mm"
            if machine.core_stops else "no station"),
        "CORE_HOLD_LAND": f"{core_hold_land:.4g} mm",
        "CORE_HOLD_REACH": f"{core_hold_reach:.4g} mm",
        "CORE_HOLD_RISE": f"{core_hold_rise:.4g} mm",
        "CORE_HOLD_WIDE": (f"{machine.core_holds[0][1] - machine.core_holds[0][0]:.4g} mm"
                           if machine.core_holds else "no station"),
        "APPLIANCE_HEIGHT": f"{appliance_height:.4g} mm",
        "PLUG_DIA": f"{plug_dia:.4g} mm",
        "SOCKET_BORE": f"{socket_bore_dia:.4g} mm",
        "SOCKET_OD": f"{2.0 * socket_r:.4g} mm",
        "BOX_SIZE": (f"{bo[1] - bo[0]:.0f} × {bo[3] - bo[2]:.0f} × "
                     f"{bo[5] - bo[4]:.0f} mm"),
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
    )
    substitute_md(
        _here.parent / "README.md",
        variables=variables,
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
