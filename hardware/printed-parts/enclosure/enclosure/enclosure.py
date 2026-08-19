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
    standing just over the floor (so it pins the two bottom pieces), the top
    pair under the ceiling, and between them the two FOUR-CORNER screws, one
    per side wall at the seam plane, each crossing all four pieces. Each boss is on an X axis: the screw
    drives in from the left/right EXTERIOR face. The BACK piece carries the
    PLUG (faucet mounting-plate idiom): a cylinder reaching inward from the
    wall with a screw clearance through it. The
    FRONT piece's lip carries the SOCKET (faucet shell-bottom idiom): a
    collar bored to receive the plug, open on its +Y face so the plug drops
    in as the pieces close, with a ruthex M3 heat-set at the deep end.
  * A bottom↔top split per column — the same joint rotated 90°, at ONE
    stated height both sides of the Y seam (`z_seam`, one level line round
    the box; the front pair joins, the back pair joins, then the front
    assembly telescopes into the back). The BOTTOM pieces carry the lip — a
    3-sided band (their outer ±Y wall + both side walls, stopping short of
    the Y-seam overlap) telescoping +Z into the top pieces — with the
    socket collars; the TOP pieces carry the pins. Four X-axis screws cross
    each seam: the wall-end stations (front-wall corners for the front
    column, rear-wall for the back) and the two four-corner screws, each
    crossing all four pieces — the back pair's split plug, the front lip's
    channel, front-bottom's proud socket. A WALL THAT LIP STANDS
    ON IS `2 * wall` THICK, floor slab to lip rim (`_lip_underwall`): the lip
    is a skin standing proud of the interior face, and a skin that began at
    the seam would land its underside in air — a soffit round three sides of
    a piece that prints floor-down. Carried to the slab it is a wall instead,
    and there is nothing in a bottom piece for the bed to bridge.

The walls stand off the bodies rather than on them — one boss chain at the ±X
walls, one wall at the back — because a body on the floor spans the interior wall
to wall, so a wall on its face would leave the seam machinery nowhere to stand.
The cold core seats flush against the seams instead, and stands flat on the floor slab — its bottom cap's lid is a plane and
every cap screw is down in a counterbore, so nothing goes under it. The ±X bands'
own seam furniture fences it sideways, the back Z seam's lip behind, and the floor's
two core lugs (`_core_fence`) ahead. The floor that core stands on is flat: the
Y seam's floor overlap is a shiplap within the slab, not a proud tongue.

Every piece prints on its Z− FACE — the bottom pieces floor-down on the slab,
the top pieces mouth-down on the seam rim. One bed plane for all four, read in
the box's own frame, so the build axis is +Z everywhere and the face that hangs
is always the one looking DOWN. That is the side every 45° relief in this file
is struck on. The anti-warp corner relief goes on the arrises that run along the
build axis: the box's four standing verticals. Each quadrant owns only two of them —
its other two "corners" are the Y-seam, a telescoping mating face with no
exterior arris to relieve — so the front pieces round the front-left/right
verticals, the back pieces the back-left/right, and every seam stays square.
The full-width facet raises no new standing vertical: it ends on the ±X
exterior walls, which are already relieved, so the chamfer runs out into their
own rounds.

Inside those same verticals stand the COLUMNS, and each is that relief MIRRORED —
congruent with it, a QUARTER TURN of the same radius, swung from the interior
corner because that is the only place such a turn fits with its ends on the two
inner faces. Two sharp corners and one arc between them, the corner behind it
solid, floor slab to ceiling. They are the cavity's own shape (`_cavity`), so everything held inside
it meets a column the way it meets a wall: a Z seam's lip wraps the face and
telescopes on it, a pod's collar is clipped by it, and a mount inside the
footprint is the column's material with only its bore left. Where a lens would
hole the collar at a seam station, the station stands off its cusp instead
(`_z_front_station_y`).

A plug is the wall it drives through and the reach it needs past it: the first
`wall` of its length is that wall's own material and the rest a stub off it, its
mouth-side face on the mouth that receives it. A socket is a pipe round that plug —
one `wall` of material, a `socket_cap` over the insert's blind end — its rim-side
face on the lip rim and its far face a hair under the seam mouth, so it stands on
that band — lip above the mouth, wall under it below — down its whole length. Those are the two matings the
overlap depth is struck from. Between two levels the corner is the wall's own air.
A level stands where its socket has a body to be bored into (`_level_clear`).

Each seam is pinned at BOTH ends of every piece that crosses it, so nothing can
hinge open at its far end: the Z seams at both ends of their column, and the Y
seam at a level for each end of each piece — the floor and ceiling levels
close the outer ends, and the four-corner screw closes the inner ends of all
four pieces at once. Levels are searched per side wall against what stands
against it, so the two walls need not carry the same ones; main() prints what
each ended up with.

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
# THE COLUMN IS THE RELIEF MIRRORED, AND A MIRROR IS CONGRUENT OR IT IS NOT ONE. Each
# standing vertical is relieved `corner_round` outside — a QUARTER TURN tangent to both outer
# faces — so the column's face is a quarter turn of the same radius, the same arc and the same
# length. The only place such a turn fits inside the cavity with its ends on the two inner
# faces is swung from the corner they meet at, and that is the whole of it: one radius, one
# centre, the interior corner.
#
# It lands on each face at 90°, so the corner presents TWO SHARP CORNERS opposite each other,
# [12 mm](COLUMN_ALONG) along each face, with the arc between them. The section stands
# [8.27 mm](COLUMN_DEPTH) out of the cove at the corner's diagonal.
#
# THE CORNER BEHIND IT IS SOLID. The face is the column's only free surface: a second arc back
# there — the mirror's own mirror — would leave a through slot the column's whole height, so
# the column is everything within the radius and `_cavity` hands the wall the rest. The cove
# the wall had turned stops being a surface at all; what the room meets at a standing vertical
# is one arc, congruent with the one it meets outside.
#
# It is a pillar and not a feature at a station: it runs floor slab to ceiling, so every Z
# seam crosses it and the seam's own lip wraps its face the way it wraps a wall (`_cavity`).
# What stands in a corner is ABSORBED — a boss inside the footprint is the column's own
# material and keeps only its bore — and a seam station whose collar would be holed by the
# lens stands off its cusp instead (`_z_front_station_y`).
column_round = corner_round
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
display_housing_back = 71.38
display_bezel_depth = 4.0        # bezel counterbore depth, user face
display_pcb_x = 106.0            # PCB body through-hole, lateral (X)
display_pcb_slope = 69.0         # PCB body through-hole, up the 45° slope
display_pcb_cut_through = 3.0    # extra depth past the facet back, cutting a socket collar
                                 # clean through (it overhangs the hole otherwise)
# THAT HOLE LEAVES A RIDGE, AND THE RIDGE IS CARRIED. Where the hole's up-slope end wall breaks
# out of the slab's back the two planes meet in a line `display_pcb_x` long, and BOTH face down
# off it — the bottom vertex of a wedge, inside a closed cavity, which is the one line on this
# piece a nozzle would have to lay in air. `_ridge_wall` stands under it, `pcb_ridge` is where,
# and `ridge-carried` is the reading. Its section is the thickness of a rib and nothing more:
# what it carries is one bead's start, not a load.
ridge_wall_t = 3.0               # the rib under `pcb_ridge`, measured across it
# THE RIB RUNS WALL TO WALL, so the loom that crosses it is bored through it. SIG-7 is the
# config display's own run — four 22 AWG in the 1/2" PET expandable braid `ledger/bom.md` §11
# buys (`assembly/cable-assemblies.md`) — and a braid of that kind is BOUGHT by its nominal and
# PASSES at what it opens to. The bore takes the opened figure, which is the braid's own ceiling,
# so a loom never has to be squeezed through one. Nothing here is a fit: the bore locates
# nothing, carries nothing, and the loom is dressed after it is through.
cable_sleeve_nom = 12.7          # 1/2" PET expandable braid, SIG-7's own
cable_sleeve_open = 1.5 * cable_sleeve_nom   # a 50% expandable braid's ceiling — [19.05 mm](CABLE_BORE)
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
# The collar's front edge, read by `enclosure_assembly.funnel_centre`. THE HOPPER IS WHERE THE
# USER POURS, so it stands as far forward as the top wall lets it — this is `housing_back_y` for
# this box, the plane the display housing's slab stops on, and what stops THAT is the brim rather
# than the throat: the flange overhangs the collar by `hopper_funnel.brim_overhang` and has to
# land on top wall, which begins at the display facet's own arris. `funnel-brim-lands` is that
# reading.
funnel_front_y = 76.38
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
# The well's roof is two tabs, this wide, one at each end of the pocket's span — each
# catches the lug's lift and prints as its own short bridge.
wago_roof_tab = 2.0


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
# cantilever. It takes no envelope the L's two arms did not already reach, and it falls
# `core_hold_reach + rear_seam_clear` in `core_hold_rise - core_hold_land` — 25° off vertical,
# which is the bracket's own UPPER face, laid on the section beneath it the whole way out.
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


def lip_face_x():
    """The ±X interior faces BELOW a Z seam, one `wall` inboard of `interior_x`.

    A wall a Z-seam lip stands on is `2 * wall` thick from the floor slab to the lip rim
    (`_lip_underwall`), so what a body seated low on a flank meets is this plane and not
    the other one. The MQ-6's card bottoms on it (`_west_cradle`), which is the whole of
    what holds the card in X."""
    ix0, ix1 = interior_x()
    return (ix0 + wall, ix1 - wall)
# The interior REAR PLANE — the inner face of the back wall, stated the same way. A
# component dragged forward inside the machine does not make the machine shallower,
# a pack that outgrows this plane reads red on `box-depth` instead of quietly resizing
# the appliance.
rear_plane_y = 464.0
# And the interior FRONT PLANE, holding the other end. The front wall is `front_wall` thick —
# the face a user hauls the pump cartridge out by, so it carries section the way the facet
# does — and it grows INWARD: the exterior stays where the appliance's stated depth put it
# and the interior face stands here. What noses into the section gets a RELIEF, 45°-chamfered
# like every pocket on this box (`front_reliefs`): the refrigeration stratum keeps the face it
# was packed against, and each pump tray roots on a pocket floor struck by its own wrap rule.
# `box-front` reads the pack against the relieved surface, region by region, not one plane.
front_wall = 9.0
front_plane_y = 14.0
# The refrigeration stratum's relief: one stated pocket across THE COMPRESSOR ALONE, floored on
# the face it packs to. It is the only body in this stratum that stands fore of the front wall's
# own interior plane — the condenser bears on that plane through its rails and the fuse clamp
# stands clear behind it — so the wall keeps its full `front_wall` section everywhere else along
# the front. Stated as (x0, x1, z0, z1, floor).
fridge_relief = (-78.0, 36.0, -1.0, 148.0, 11.0)
# And each pump's relief in the cartridge face, floored where the tray's own wrap rule wants
# its root: `pump_tray` demands root ≥ head_half + MARGIN off the pump's axis, and the floor
# is what the root is struck to. The face over a pump keeps this floor less the exterior
# plane (`front_plane_y − front_wall`) of section, which is the thinnest the user-facing
# surface gets anywhere.
pump_relief_floor = 8.9
relief_chamfer = 45.0        # every relief ceiling rises at this angle to the mouth

# Where the box splits front from back, and where both columns split bottom from
# top. Both are STATED planes: which pieces the box comes apart into is a decision
# about the pieces — what each has to carry, and what a hand reaches when the front
# assembly is off — and the depth and height each piece comes to is what the plane
# leaves. `_dims` measures them against the facet, the bed, the pack and each column's
# own lip lane, and records what it reads (`y-seam-clears-facet`, `z-seam-bed`,
# `z-seam-two-pieces`, `z-seam-front-lane`, `z-seam-back-lane`, `z-seam-under-deck`).
y_seam = 200.0
# The bottom↔top seam: ONE plane, both Y columns — the seam line runs level round the box
# and the four pieces meet at a four-way corner on each side wall. The plane stands where
# its own machinery fits the pack: the seam ring's foot over the condenser's fin
# crown (`z-seam-front-lane`) and the rim under the forward valve panel's plate
# (`z-seam-under-deck`). Across the bay the ring's front segment goes to the bay floor and
# the pump heads over it (`_front_flat_lip_drop`), and the seam's own MOUTH is the plane
# that floor lies on (`bay-floor-bedded`); the pumps ride behind the cartridge face's own
# reliefs (`pumps-in-bay`, `enclosure_assembly.PACK_Y`) and sweep out over the floor's top
# (`heads-sweep-out`).
z_seam = 160.0

# A seam landing in an open band keeps this much air off every body in its own column,
# so a body there lands whole in one piece and its mounts have one piece to stand on.
# `_z_joints` reads each column's open bands against it for `_report_seams`.
z_joint_clear = 3.0
# The Z lip stops this short of the Y-seam overlap on each side, so the two
# telescopes never share a wall surface.
z_lip_y_margin = 2.0

# THE FOUR-CORNER SCREW: one M3 per side wall at (`_y_boss`, `z_seam`), where all four
# pieces meet, crossing every one of them — the Y-boss idiom with the seam plane through
# it. The back pair carries the plug as two half-cylinders, each piece its own half; the
# front lip's two halves carry the slide channel; and FRONT-BOTTOM alone carries the
# socket, a pedestal standing proud through the plane off its own lip face, so the bore
# and the insert live in one piece's solid. The head sits in the standard counterbore,
# astride the visible seam line. It pins fb↔bb over the floor level, ft↔bt under the
# ceiling one, and each column's Z seam against its far station — every pair at both
# ends of its span.
corner_screw_len = 12.0      # M3×12 SHCS — the corner's own length
# The corner chain, read the way `boss_in` is: head seat, pin, heat-set and cap, less the
# wall the counterbore is sunk into. TWO walls stand at the corner (the back piece's own
# with the front lip inside it), so the socket roots one `wall` deeper than a Y-boss
# collar and the cap lands past `boss_in` — the reach the cold core's flank slot
# receives (`_cold_core_interface.corner_boss_slots`, `corner-slot-lands`).
corner_boss_in = head_cbore_depth + corner_screw_len + socket_cap - wall
corner_core_reach = corner_boss_in - boss_in

# --- THE PUMP BAY AND ITS CARTRIDGE ------------------------------------------
#
# THE PUMPS SLIDE OUT OF THE FRONT OF THE BOX. The front wall's flat span — corner column to
# corner column — and the tray storey that hangs the pumps come out of front-top as one
# piece, the PUMP CARTRIDGE: the face, the block, both trays, both pumps. It rides the floor
# standing on the bay's floor and nothing latches it: the four barb tubes gripped in the
# anchor tees' branch collets are the retention, and the collet plate
# (`enclosure_assembly.build_collet_plate`) is the release — pull the cartridge and the tees
# come with it until their collets press the plate, the tubes come free, and the pumps are
# in your hand. Pushing it home threads the four tubes back through the plate's holes into
# the same collets, the cap's own aft face landing on the plate's.
#
# FRONT-TOP CARRIES A FLOOR ACROSS THE BAY (`_bay_floor`), and everything in this storey
# slides across it, and the collet plate is sunk in its own seat.
# THE FLOOR IS THIS PIECE'S FIRST LAYERS — front-top beds on the seam plane, so a floor
# struck there lies on the bed with nothing under it to hang. Its thickness is the only
# thing above it: the cartridge reaches down to the plane its pump reliefs floor on, and
# the floor's top is that plane. Front-bottom's side lip is given up over this whole run
# (`_flank_lip_drop`), so the floor crosses it wall to wall and only the front boss's own
# plinth still stands over the mouth here.
#
# The BAY is the opening all that leaves through: the flat front wall between the corner
# columns' along-wall edges, from the floor's top up past the motor cans' crowns. The
# columns are the jambs; the floor's own top is the sill, washed fore so what runs down the
# face runs out; the wall over the bay is the lintel, carrying the facet and the display.
# Front-bottom's front lip drops across the whole flat span, because the floor stands in
# that band — so the front Z-joint is the corner columns' pillar telescopes and a butt at
# the seam, and the wall keeps its single `front_wall` section from slab to seam.
#
# BOTH FLANKS OPEN ACROSS THE SAME STOREY (`_flank_opening`), and the CORNER COLUMNS ARE THE
# ONLY THING LEFT STANDING IN THEM. A column here is the whole of the box's corner — the side
# wall's section, the front wall's, and the quarter-round between them, one post — so the
# opening begins where that post's arc lands on the side wall's inner face and runs aft from
# there. Its floor is the Z-seam rim: under that plane the side wall is the outer register
# front-bottom's lip telescopes into.
#
# THE CARTRIDGE STAYS BETWEEN THE JAMBS. It is the flat span and what stands behind it, out
# to `bay_x_span` and no further at any height, so the posts it slides between are untouched
# and the front of the box outboard of the bay is theirs.
bay_crown_air = 1.7          # bay top over the tallest motor can's crown
bay_face_slip = 0.4          # cartridge face inside the opening, per side — its running fit
# HOW FAR A CORNER POST REACHES ALONG THE FRONT WALL'S INNER FACE. The post is the whole of
# the box's corner and the bay stops on it, so this is what the front of the machine keeps
# outboard of the opening. It is carried past the column's own arc — which lands one
# `column_round` in — far enough that the cartridge's face clears front-bottom's Z-seam wrap
# without stepping in under the rim.
post_along = 14.676
face_reveal = 0.4            # the face's edge reveal at the sill and under the lintel
sill_wash = 1.4              # the sill's top face falls this much fore, so the reveal drains
# THE CARTRIDGE HAS ONE OUTLINE AND NOT TWO. Face, deck and cap all stand `bay_face_slip`
# inside the jambs and `face_reveal` under the lintel, because they are one printed block and
# the thing that has to pass the opening is the block. Giving the deck air of its own put the
# face 0.6 proud of it down every flank and the deck 0.4 proud of the face along its top —
# steps in opposite directions, neither outline containing the other, and a thin ledge at
# every junction. What the face fits through, the block behind it fits through.
cap_kiss = 0.1               # the cap's aft face off the collet plate's, at full seat
plate_slot_slip = 0.2        # air fore and aft of the collet plate in the floor's seat. NOT
                             # across it: the seat's ends are the side walls themselves, and
                             # what holds the steel off those is `PLATE_END_AIR` alone

# --- THE CARTRIDGE IS A BLOCK, AND IT PARTS ON THE BRACKET PLANE -------------
#
# THE CARTRIDGE IS SOLID AND THE PUMPS STAND IN IT. What the bay leaves between the face and
# the collet plate is filled, sparse infill under a printed skin, and the two Kamoers are
# voids in that fill. A block reads and carries as one object in the hand, which is what a
# part a user hauls on wants to be.
#
# IT PARTS ON THE PUMP'S OWN BRACKET PLANE (`cap_split_z`) — the head-to-boss junction, the
# plane the tray's plate already lands on. Above it the block is `enclosure-pump-cartridge`
# and each pump stands in the tray that takes its boss; below it the block is
# `enclosure-pump-cap`, one piece for both pumps, and what it closes on is each head. The
# cap's top face IS that plane, so the stamped bracket the part carries there — `bracket_w`
# across against a head of `head_w`, standing proud all round — lands on the cap's own
# material and the screws carry it.
#
# AND THE HEAD IS CARRIED BY ITS OWN FLANKS, not by that lip alone. The part's flanks ramp in
# twice on the way down — `pump_case.flank_ramp_bands`, the two levels the case that printed
# and held this pump closed on it — leaving a 45 degree face on each side at each band, four
# faces looking down and outboard. The cap keeps the wedge under every one of them
# (`pump_tray.head_seats`), so the weight stands on the flanks and the lip over it only keeps
# the part from lifting off them. Nothing reaches under a head's FRONT face, which stands one
# millimetre over the bay floor's own top.
#
# WHAT STAYS OPEN IS A COST. The motor cans open through the block's ceiling: the bay top
# stands `bay_crown_air` over their crowns and the display facet sets that plane. The head's
# front face stands on the sill at the other end. Covering either asks the box for width past
# the corner columns or height past the display, so the block covers what there is room to
# cover and no more.
#
# THE SCREWS RUN UP THE LANE BETWEEN THE PUMPS. `cap_band_x` is that lane — the two heads'
# own inboard faces, less air — and it is the one column of this piece with no pump, no barb
# tube and no fitting in it at any height. The cap gives up its fill there and keeps
# `cap_web_t`, so a screw crosses one web into a heat-set in the block above it and the
# driver comes up the lane the fill gave up.
cap_pump_air = 0.4           # air round a pump body where the block closes on it
cap_band_air = 1.0           # the screw lane's edge off each head's inboard face
cap_web_t = 4.0              # the cap's section across that lane — what a screw crosses
cap_screw_off = 18.0         # each screw off the lane's own mid-depth, fore and aft


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
#   side_wells    the side walls' Wago wells, (side, y, z, size, clear_z) — one press-fit pocket
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
#   column_reliefs what the standing corners' PILLARS give up to the pack standing in them, one
#                 (sx, sy, name, room) per body — the corner's own signs, whose body it is, and
#                 the world box the column is cut back to, as the six plain bounds
#                 `(x0, x1, y0, y1, z0, z1)` every other station on this tuple is written in.
#                 A STATION IS NUMBERS: `_facts` serialises this whole Box for the eight doc
#                 drivers that read it, and `build_piece` strikes the box where it cuts.
#                 Struck by `_dims` off the placed parts rather than passed in by the pack,
#                 because it is the one question that needs the bodies AND the walls at once;
#                 main() prints each.
#
#                 A COLUMN GIVES WAY TO A BODY AND NOT THE OTHER WAY ROUND. It is a print-corner
#                 feature — what it buys is a fat vertical on the bed, and it buys that over the
#                 height it does have. A body hung on a wall answers to the boss that holds it
#                 and to whatever the pack packed it against, and by the time one reaches a
#                 corner both of those are already spent.
#   collet_plate  the steel plate the barb tubes release against, as the dict
#                 `enclosure_assembly.collet_plate_spec` strikes off the four anchor tees'
#                 branch collets: its two Y faces, its Z band, its X ends, and one (x, z)
#                 per hole. The bay floor's seat takes its foot (`_bay_floor`)
#   pump_bay      the cartridge's opening in the flat front span, (x0, x1, z_top) — jamb to
#                 jamb between the corner columns' cusps, topped over the motor cans' crowns.
#                 None when the pack stands no pumps
Box = namedtuple(
    "Box", "inner outer y_joint splits front_ports back_ports east_ports west_ports "
           "funnel pan_sleeve c14 east_bosses side_wells floor_bosses west_cradle cond_cradle "
           "cond_mount asse_cradle digiten_saddles tube_anchors port_field nameplate "
           "valve_panels pump_trays core_stops core_holds vent_chase column_reliefs "
           "collet_plate pump_bay")

# What a box is built AROUND: the placed bodies, and every station they put on a wall.
# A pack that does not carry a subsystem yet carries no stations for it, and the wall
# comes out blank there rather than carrying a hole with nothing behind it.
#   placed        {name: (solid, colour)} — the same shape a CadQuery assembly reads
# The rest are the Box fields above, and the box passes them through.
Pack = namedtuple(
    "Pack", "placed front_ports back_ports east_ports west_ports funnel pan_sleeve c14 "
            "east_bosses side_wells floor_bosses west_cradle cond_cradle cond_mount "
            "asse_cradle digiten_saddles tube_anchors port_field nameplate valve_panels "
            "pump_trays core_stops core_holds vent_chase collet_plate")
Pack.__new__.__defaults__ = ((), (), (), (), None, (), ((), ()), (), (), (), (), (), (),
                             (), (), (), (), None, (), (), (), (), (), None)


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


def _column_arc(inner, sx, sy):
    """The centre one corner column's face arc is swung from — the INTERIOR CORNER.

    THE COLUMN IS THE RELIEF'S CONGRUENT TWIN. The relief outside is a QUARTER TURN of
    `corner_round` tangent to both outer faces; a mirror is congruent or it is not a mirror,
    so the face is a quarter turn of the same radius — same arc, same length — and the only
    place such a turn fits inside the cavity with its ends on the two inner faces is swung
    from the corner they meet at."""
    ix0, ix1, iy0, iy1, _iz0, _iz1 = inner
    return (ix0 if sx < 0 else ix1), (iy0 if sy < 0 else iy1)


def _corner_column(inner, sx, sy, grow, z):
    """One corner column as a solid over the height span `z`, grown `grow` into the room.

    THE ARC IS THE WHOLE OF IT AND THE CORNER BEHIND IT IS SOLID. The column is everything
    within `column_round` of the interior corner; `_cavity` takes the difference, so what
    becomes material is that disc's share of the AIR and the wall keeps the rest. Nothing
    stands between the column and the cove it rises out of — a second arc back there would
    be a through slot the column's whole height, and its only free surface is the face.

    Growing swells the disc, which is the offset read on that one surface."""
    px, py = _column_arc(inner, sx, sy)
    z0, z1 = z
    return _zcyl(column_round + grow, px, py, z0, z1)


def _column_pillar(inner, sx, sy, zj):
    """One column AND the lip's own skin where it wraps it — the whole of what a body meets
    at a standing vertical, and the whole of what gives way to one.

    The lip and the wall under it are struck as the cavity's skin (`_lip_band`), so at a
    vertical they do not stop at the column: they WRAP its face and stand one `wall` further
    inboard than the pillar does, floor slab to rim. A body reaching into a corner meets that
    wrap before it meets the column, and a relief measured on the column alone is a relief
    that leaves the thing actually in the way standing.

    `zj` is that Y column's own seam, so the wrap ends where its lip's rim does. Above it the
    pillar is the column and nothing else."""
    z = (inner[4] - 1.0, inner[5] + 1.0)
    post = _corner_column(inner, sx, sy, 0.0, z)
    wrap = _lip_band(inner, (inner[4], zj + lip_len)).intersect(
        _corner_column(inner, sx, sy, wall, z))
    return post.fuse(wrap)


def _column_along():
    """How far along a wall's INNER face a column reaches, from the interior corner.

    Its CUSP stands on that face at one radius — where the quarter turn lands — and the lens
    closes back toward the corner from there, so a body anywhere on that wall meets the cusp
    and nothing of the column is further along than it."""
    return column_round


def wall_flat_from_corner():
    """How far in from a standing vertical a wall's inner face is FLAT — what anything
    BEARING on that face has to stand clear of.

    The relief rolls the face away `corner_round - wall` from each corner. Where that corner
    carries a COLUMN the flat ends sooner still: the lens's cusp stands on this face and the
    section closes back toward the corner from there, so a flange carried past it bears on
    curve either way. Struck across every corner rather than one, the way `wall_band_corner_y`
    is, because the ±X walls answer as a pair and a body reads the fence before it knows which
    end it is at."""
    flat = corner_round - wall
    return max(flat, _column_along()) if column_corners else flat


def _column_depth():
    """How far a column reaches out of the cove it rises from, across the corner's diagonal.

    The face stands one radius off the corner there; the cove the wall already turned stands
    `(corner_round - wall) * (sqrt2 - 1)` off it, and the column is everything between."""
    return column_round - (corner_round - wall) * (math.sqrt(2.0) - 1.0)


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
# wall with nothing in the way gets no entry, and `_level_clear` reads that absence as
# "nothing known to be in the way".
#
# THE MODULE STATE HERE IS ONE COPY'S, which is what the `__main__` guard's alias at the foot
# of this file is for: `_dims` fills this dict and `_level_clear` reads it, and a run that
# exported the pieces out of a second copy of this module would read an empty one. What a
# measurement wants instead is the `Box`, which is struck once and passed to whatever builds
# from it — `Box.column_reliefs` is a measurement for that reason and not a dict here.
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

    THE Z-SEAM STATIONS ARE NOT IN IT. Each is a collar `2 * socket_r` tall at the stated
    plane's own height (`z_seam`) — so a body standing clear of it in z passes it, and
    whether one does is a question about a placed pack. `enclosure_assembly.check_east_band`
    asks that against `seam_bosses`, which carries each boss's height as well as its
    station.

    Struck off the stated planes alone, `y_seam` and `rear_plane_y` — so a body reads it
    before the box that carries it has been sized, the same way it reads the wall itself
    through `interior_x`."""
    return (y_seam + lip_len, wall_band_corner_y(mount_boss_out))


def front_band_collar_z():
    """The front-wall station's collar in height, as `(z0, z1)` — the one thing the seam
    stands in a ±X boss-chain band forward of `front_band_free_y`'s aft fence. The
    four-corner boss and its web stand wholly behind that fence, so they never enter
    this answer.

    THE SEAM'S HEIGHT IS STATED (`z_seam`), so the collar has a height a body can be
    placed against BEFORE the box is sized. `front_band_free_y` turns it into a depth;
    a caller that wants to stand under it rather than beside it asks directly."""
    zc = _z_pin_z(z_seam)
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

    The front-wall station and the four-corner boss are its ends, and the seam's height
    IS stated (`z_seam`), so a caller that says what height it stands at gets the answer
    for that height: a body clear of the seam's furniture in z has the column from the
    front wall to the corner boss's own fore face. A caller that names no height gets the
    run with the front-wall collar standing.

    IT TAKES THE FRONT FACE because it cannot state it. The back half's two ends are both
    struck on planes the box states about itself — `y_seam` and `rear_plane_y` — but the front
    wall stands off whatever the pack puts nearest it, so a caller reading this before the box
    is sized has to say what that is. Everything after it is the same stated chain `_dims`
    builds the wall on."""
    iy0 = front_face - interior_clearance - front_seam_clear
    yf = _z_front_station_y(iy0)
    aft = _y_boss(y_seam) - socket_r
    cz0, cz1 = front_band_collar_z()
    if z0 is not None and (z1 <= cz0 or z0 >= cz1):
        return (iy0, aft)                     # clear of the seam's furniture in height
    return (yf + socket_r, aft)


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
    and the same tall, at the station its own screw is on — and the four-corner boss takes
    its 45° web's run below the collar too. Read from the definitions that BUILD them
    (`_bosses`, `_y_corner`, `_z_stations`, `_z_station_y`, `_corner_socket`), so a
    footprint cannot drift from the geometry it stands for.

    THE HEIGHT IS HALF THE ANSWER. A body hung on a flank clears a boss by standing beside it
    or by standing over it, and a reading with no z in it can only see the first — it would
    charge a body the whole height of a wall for a collar 16 mm tall. Between two bosses, and
    above and below every one of them, the band is the wall's own air."""
    r = socket_r
    yb0, yb1 = _y_corner(inner, y_joint)
    out = [(yb0, yb1, z - r, z + r)
           for _x_in, _x_ext, _sx, z in _bosses(inner, y_joint)]
    for _x_in, _x_ext, _sx, ys, col in _z_stations(inner, y_joint):
        zp = _z_pin_z(splits[0] if col == "front" else splits[1])
        y0, y1 = _z_station_y(ys)
        out.append((y0, y1, zp - r, zp + r))
    # The four-corner boss: its collar, and the 45° web running from the collar's
    # underside down to the lip face.
    ycb = _y_boss(y_joint)
    out.append((ycb - r, ycb + r,
                z_seam - r - (corner_boss_in - wall), z_seam + r))
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
    cavity's own one-`wall` skin (`_lip_band`), read from one `wall` under the mouth
    (`zj − wall`) up to the rim (`zj + lip_len`). The lip proper starts on the mouth; the
    `wall` below it is the top of `_lip_underwall`, and reading the two together is what
    keeps this conservative — the skin really is continuous there, and a body in it is in
    the seam's way whichever of the two it touches. The four station collars ride with
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
    # The front flat span carries no lip at any height — it is the bay's, and the pieces
    # drop it (`_front_flat_lip_drop`) — so the ring measured here is the ring the box
    # builds. Gated the way the bay itself is: on the pack standing pumps.
    if any(n.startswith("pump-") and n.endswith("-motor") for n in placed):
        bx0, bx1 = bay_x_span(inner)
        ring = ring.cut(_ybox(bx0, bx1,
                              inner[2] - 0.1, inner[2] + wall + 0.1,
                              iz0 - 1.0, iz1 + 1.0))
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


def _z_joints(placed, inner, stated):
    """The bottom↔top seam height per Y column: `(front, back)` — the one stated plane,
    both.

    `stated` is `z_seam`, and what is measured here is what it lands in: the band the bed
    leaves a column's two pieces (`_bed_band`), each column's own lip lane — the heights
    the pack leaves the lip's ring (`_lip_denied`) — and the open bands the column's
    bodies leave, which is what `_report_seams` reads. None of the bounds stops the cut:
    whatever the readings say, both seam heights come back and the box is cut on them."""
    iz0, iz1 = inner[4], inner[5]
    y_mid = (inner[2] + inner[3]) / 2.0
    bed_lo, bed_hi = _bed_band(inner)
    on_bed = bed_lo - 1e-9 <= stated <= bed_hi + 1e-9
    record_bound(Bound(
        "z-seam-bed", "The Z seam leaves every piece on the H2C's bed", on_bed,
        f"seam at {stated:.2f}, band {bed_lo:.2f}..{bed_hi:.2f}",
        f"inside the H2C's {H2C_Z:g} mm Z",
        ([] if on_bed else [
            f"the Z seam at {stated:.2f} leaves a piece off the H2C's {H2C_Z:g} mm bed: "
            f"the top pieces want it at or below {bed_hi:.2f} and the bottoms at or above "
            f"{bed_lo:.2f}. Move `z_seam` into that band"])))
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
    for col, y_span in (("front", (inner[2], y_seam)), ("back", (y_seam, inner[3]))):
        whole = _clipped(_open_bands(spans[col], iz0, iz1, z_joint_clear), bed_lo, bed_hi)
        _z_seam_passes[col] = not any(lo - 1e-9 <= stated <= hi + 1e-9 for lo, hi in whole)
        lanes = _open_bands(_lip_denied(placed, inner, y_span), bed_lo, bed_hi, 0.0)
        in_lane = any(lo - 1e-9 <= stated <= hi + 1e-9 for lo, hi in lanes)
        record_bound(Bound(
            f"z-seam-{col}-lane", f"The {col} column's lip ring is clear at the seam height",
            in_lane,
            f"seam at {stated:.2f}, lane "
            + (", ".join(f"{lo:.2f}..{hi:.2f}" for lo, hi in lanes) or "nowhere"),
            "a lane containing it",
            ([] if in_lane else [
                f"the {col} column's lip cannot run at {stated:.2f}: what reaches into its "
                f"ring leaves "
                + (", ".join(f"{lo:.2f}..{hi:.2f}" for lo, hi in lanes) or "no height")
                + " — move `z_seam`, or repack what stands in the ring"])))
    return stated, stated


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
    splits = _z_joints(placed, inner, z_seam)
    # THE RIM'S OWN CEILING. Wall-rooted furniture stands on a piece's wall, and below the
    # rim the wall's inner face is the bottom piece's lip — so a valve panel's seat plate
    # spans wall to wall whole above the rim, and its FOOT runs below it inset on the lip's
    # own face (`_valve_panels`). The lip's ring cannot read one: it is printed material,
    # not pack, and a plate standing ON the rim is a touch with no volume in it. This reads
    # the wall-to-wall storeys off the same stations the pieces build them from. The bay's
    # floor is the one span that does stand on the rim and answers elsewhere
    # (`enclosure_assembly.check_bay_floor`); the trays' storey roots on the cartridge, so
    # no wall of this box carries it.
    rim = max(splits) + lip_len
    decks = [mz - _panel.height() / 2.0
             for _plane, _sign, seats in pack.valve_panels
             for mz in [(min(z for _x, z in seats) + max(z for _x, z in seats)) / 2.0]]
    deck_floor = min(decks) if decks else iz1
    record_bound(Bound(
        "z-seam-under-deck", "The Z-seam rim stays under the flavour deck's lowest plate",
        rim < deck_floor - stated_bound_tol,
        f"rim at {rim:.2f}, deck floor at {deck_floor:.2f}",
        "air between them",
        ([] if rim < deck_floor - stated_bound_tol else [
            f"the lip's rim at {rim:.2f} reaches the deck's lowest wall-rooted plate at "
            f"{deck_floor:.2f} — a plate roots on a wall only above the rim. Lower "
            f"`z_seam`, or raise the deck"])))
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
    # The FRONT wall is the stated `front_plane_y` with its stated reliefs, and the pack is
    # read against the RELIEVED surface, body by body: a body whose footprint stands wholly
    # inside a relief answers to that relief's floor, and every other body to the plane
    # itself. The compressor's reading is its stated kiss on the refrigeration bay's floor.
    #
    # The BACK wall is the stated `rear_plane_y`, for the same reason the ceiling is the
    # stated `appliance_height`: depth is a bound, not a consequence. Taken off the pack it
    # would follow whichever body reached furthest back, and anything seated on this plane
    # would follow that body too, holding every clearance between the two constant.
    regions = _front_relief_regions(pack.pump_trays)
    front_rows = sorted(
        (b.ymin - _front_floor(regions, b), name)
        for name, b in zip(placed.keys(), bbs))
    front_ok = front_rows[0][0] >= -stated_bound_tol
    record_bound(Bound(
        "box-front", "The pack stands behind the front wall's relieved surface",
        front_ok,
        f"least air {front_rows[0][0]:.2f} mm, at {front_rows[0][1]}",
        f"on or behind the wall's own surface, plane {front_plane_y:g} and its reliefs",
        ([] if front_ok else [
            f"{name} stands {-air:.2f} mm inside the front wall's surface — deepen its "
            f"relief in `_front_relief_regions`, or repack it aft"
            for air, name in front_rows if air < -stated_bound_tol])))
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
    oy0, oy1 = iy0 - front_wall, iy1 + wall
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
    # WHAT EACH LIP'S OWN WALL COSTS THE CAVITY. A flank under a Z seam is `2 * wall` thick
    # from the slab to the rim (`_lip_underwall`), so on three sides of each bottom piece the
    # room stops one `wall` inboard of `inner`. The pack already stands that far off every one
    # of them — `front_seam_clear` and `rear_seam_clear` at the ±Y walls, `side_band_inset` at
    # the ±X ones — and the MQ-6, the one body that touches a flank at all, is seated on this
    # skin's own face (`lip_face_x`). A body that stands in it anyway is a body the wall is
    # drawn through, which is a reading and not an assumption.
    #
    # WHAT IS MEASURED IS THE FLAT WALL AND NOT THE PILLARS. This skin wraps every column
    # standing in a vertical, and a pillar GIVES WAY to a body standing in it — the wrap with
    # the column, since a body meets the two as one thing (`_column_pillar`). Charging a body
    # for the corner it is already relieved out of would report a clash the box does not build,
    # so the pillars come out and `_report_columns` says what they gave.
    under = []
    for zj, (cy0, cy1) in ((splits[0], (iz0 - 1.0, y_joint)),
                           (splits[1], (y_joint, iy1 + 1.0))):
        band = _lip_underwall(inner, y_joint, zj).intersect(
            _ybox(ix0 - 1.0, ix1 + 1.0, cy0, cy1, iz0 - 1.0, iz1 + 1.0))
        if zj == splits[0] and pack.pump_trays:
            # The front flat's skin goes to the bay (`_front_flat_lip_drop`), so the band
            # read here is the band the pieces build.
            band = band.cut(_front_flat_lip_drop(inner, zj))
        for sx, sy in column_corners:
            band = band.cut(_column_pillar(inner, sx, sy, splits[0] if sy < 0 else splits[1]))
        for name, (solid, _c) in placed.items():
            hit = band.intersect(solid)
            if hit.Volume() > 1e-3:
                b = hit.BoundingBox()
                under.append((name, hit.Volume(), b.zmin, b.zmax))
    record_bound(Bound(
        "wall-under-lip", "The pack stands clear of the wall under each Z-seam lip",
        not under,
        (f"{len(under)} bodies in it" if under else "clear on all three sides of both pieces"),
        f"one `wall` ({wall:g} mm) off the ±Y walls and the ±X ones below each seam",
        ([] if not under else
         [f"{name} stands {vol:.1f} mm³ inside it, z {z0:.1f}..{z1:.1f}"
          for name, vol, z0, z1 in under]
         + ["the lip's wall carries to the slab so its shoulder is not a soffit, so a body "
            "against a flank down there is a body the wall runs through. Repack it inboard, "
            "or seat it on `lip_face_x` the way the MQ-6's card is"])))
    # WHAT THE COLUMNS GIVE UP. Measured here with everything else the placed pack decides,
    # against the same `inner` the columns are struck on.
    reliefs = []
    for sx, sy in column_corners:
        pillar = _column_pillar(inner, sx, sy, splits[0] if sy < 0 else splits[1])
        for name, (solid, _c) in placed.items():
            hit = pillar.intersect(solid)
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
                reliefs.append((sx, sy, name, (
                    b.xmin - (0.0 if sx < 0 else column_relief_slip),
                    b.xmax + (0.0 if sx > 0 else column_relief_slip),
                    b.ymin - (0.0 if sy < 0 else column_relief_slip),
                    b.ymax + (0.0 if sy > 0 else column_relief_slip),
                    b.zmin - column_relief_slip, b.zmax + column_relief_slip)))

    # THE PUMP BAY: the flat front span between the corner columns' cusps, topped one
    # `bay_crown_air` over the tallest motor can's crown — what the cartridge leaves
    # through, struck off the placed cans the way every station is struck off its body.
    bx0, bx1 = bay_x_span(inner)
    crowns = [b.zmax for name, b in zip(placed.keys(), bbs)
              if name.startswith("pump-") and name.endswith("-motor")]
    pump_bay = (bx0, bx1, max(crowns) + bay_crown_air) if crowns else None
    return Box(inner, outer, y_joint, splits,
               pack.front_ports, pack.back_ports, pack.east_ports, pack.west_ports,
               pack.funnel, pack.pan_sleeve, pack.c14, pack.east_bosses,
               pack.side_wells, pack.floor_bosses, pack.west_cradle, pack.cond_cradle,
               pack.cond_mount, pack.asse_cradle,
               pack.digiten_saddles, pack.tube_anchors, pack.port_field, pack.nameplate,
               pack.valve_panels, pack.pump_trays, pack.core_stops, pack.core_holds,
               pack.vent_chase, tuple(reliefs), pack.collet_plate, pump_bay)


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


def pcb_ridge(outer):
    """The RIDGE the display's PCB through-hole leaves across that slab's back, as one
    `(y, z)` station on it. The line itself runs `display_pcb_x` in X, centred on the body's
    own offset — `_ridge_wall` spans exactly that and `ridge-carried` reads exactly that.

    The hole is cut perpendicular to the 45° face and the slab's back is parallel to it, so
    the hole's up-slope end wall and that back meet in a line — and BOTH FACE DOWN OFF IT.
    That makes the line the bottom vertex of a wedge: 45° either side of it is self-supporting
    once laid, but the line itself has nothing under it, and it stands inside a closed cavity
    where support is not reachable. It is one station because it is one intersection: the
    hole's own up-slope face (`display_pcb_slope` past `display_body_offset_slope`) taken
    `display_facet_thickness` in, which is where the slab's back is."""
    p = display_plane(outer)
    r = (p.origin
         + p.yDir * (display_body_offset_slope + display_pcb_slope / 2.0)
         - p.zDir * display_facet_thickness)
    return r.y, r.z


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
        r = plate.collar_d / 2.0
        deep = floor - plate.bore_depth
        solid = solid.fuse(_ycyl(r, sx, sz, floor, y_inner))
        solid = solid.fuse(_ycyl(plate.stem_d / 2.0, sx, sz, deep, floor))
        # The pair is a D below its axis on a 45° web down the wall, the box's one boss
        # shape — held to the `rear_seam_clear` band, the air the pack stands off this
        # wall; the stem past it keeps its own round. The pocket cuts below take back
        # whatever stands in the plate's own seat.
        shallow = y_inner - rear_seam_clear
        solid = solid.fuse(_ybox(sx - r, sx + r, shallow, y_inner, sz - r, sz))
        solid = solid.fuse(_yz_prism(sx - r, sx + r,
                                     [(y_inner, sz - r), (shallow, sz - r),
                                      (y_inner, sz - r - rear_seam_clear)]))
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
        # The boss is a D below its bore's axis, on a 45° web run down the wall — squared
        # and webbed the way every boss on this box is, so its underside prints off the
        # wall it stands on.
        w2 = width / 2.0 + field.rim
        zb = pz - w2
        boss = boss.fuse(_ybox(px - w2, px + w2, boss_y0, y_inner, zb, pz))
        boss = boss.fuse(_yz_prism(px - w2, px + w2,
                                   [(y_inner, zb), (boss_y0, zb),
                                    (y_inner, zb - field.proud)]))
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
    # AND THE FRONT EDGE, WHICH IS NOT A FREE ONE. Forward the flange runs out over the display
    # housing's roof, and that roof stops at the facet's own arris — the line where the 45°
    # meets the top face. A brim reaching past it overhangs the chamfer and bears on nothing.
    # The landing asked for is one `wall`, the same ligament `display-housing-seats` keeps
    # behind the display's own seats: at the arris itself the slab under the flange is a
    # feather edge, and a wall in from it the wedge is the wall's own section deep.
    arris = box.outer[2] + display_facet_slope * math.sin(math.radians(display_facet_angle_deg))
    brim_y0 = y0 - _funnel.brim_overhang
    lands = brim_y0 >= arris + wall - tol
    record_bound(Bound(
        "funnel-brim-lands", "The funnel's brim lands on top wall ahead of the throat", lands,
        f"brim front at y {brim_y0:.2f}, facet arris at {arris:.2f}",
        f"a {wall:g} mm landing, so at or aft of {arris + wall:.2f}",
        ([] if lands else [
            f"the brim's front edge stands at y {brim_y0:.2f} and the top face begins at the "
            f"facet's arris, y {arris:.2f} — the flange reaches "
            f"{arris + wall - brim_y0:.2f} mm past the landing it owes and hangs over the 45°. "
            f"Take `funnel_front_y` aft of {arris + wall + _funnel.brim_overhang:.2f}, or "
            f"shorten the facet"])))
    return box._replace(funnel=centre)


def _hopper_cut(inner, outer, centre):
    """The funnel throat punched clean through the top wall — one wall deeper
    than the ceiling, so the Y-seam's top-wall lip/mouth shelf (hanging one
    wall below it) is relieved across the hole span the seam crosses.

    The opening is the collar, whole: the basin is a full rectangle and the wall carries
    nothing over the tap-water sequence that the throat has to be cut around."""
    x0, x1, y0, y1 = _hopper_hole(centre)
    return _ybox(x0, x1, y0, y1, inner[5] - wall - 1.0, outer[5] + 1.0)


def _ceiling_corbels(solid, inner, outer, centre, y_joint):
    """The flat ceiling's two side strips on a top piece, corbelled: a 45° underside
    rising off each ±X wall to nothing at the hopper opening's edge, so a top piece —
    printing mouth-down — lays every ceiling layer on the one below it. The strip's own
    span is wall-rooted on one side and open over the opening on the other.

    The corbel runs the housing's back plane to the Y-seam furniture's fore face, and a
    second one carries the lip's ceiling tongue, struck one `wall` lower on the tongue's
    own underside: it roots on the ceiling collar's own chain-deep face — the column the
    collar's web already carries — and rides with the tongue into the mouth it
    telescopes into. The collar band itself (chain-deep at the wall) is the collar's own
    D, fill and web."""
    cx, _cy = centre
    hole_x0, hole_x1 = cx - _funnel.collar_w / 2.0, cx + _funnel.collar_w / 2.0
    iz1 = inner[5]
    y0 = housing_back_y(outer)
    yb = _y_boss(y_joint)
    for hole_x, wall_x in ((hole_x1, inner[1]), (hole_x0, inner[0])):
        deep = abs(wall_x - hole_x)
        solid = solid.fuse(_xz_prism(y0, yb - socket_r,
                                     [(hole_x, iz1), (wall_x, iz1),
                                      (wall_x, iz1 - deep)]))
        chain = wall_x - (boss_in if wall_x > 0 else -boss_in)
        tz = iz1 - wall
        solid = solid.fuse(_xz_prism(yb - socket_r, y_joint + lip_len,
                                     [(hole_x, tz), (chain, tz),
                                      (chain, tz - abs(chain - hole_x))]))
    return solid


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


def _bosses(inner, y_joint):
    """Per-boss tuple (x_in, x_ext, sx, z_boss): the inner ±X wall face the screw
    passes through, its matching exterior face, sx = +1 (left) / −1 (right)
    inboard, and the bore-axis height.

    The Y seam runs the box's whole height and BOTH columns cross it, so it is
    pinned at a level for each end of each piece that crosses it. The floor and
    ceiling levels close the outer ends — the under-floor level pins the two
    bottom pieces, the under-ceiling one the two tops — and the FOUR-CORNER
    screw at the seam plane itself closes the inner ends of all four at once
    (`_corner_socket`).

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


def _boss_x(x_ext, sx, length=None):
    """Inboard X stations from the ±X exterior, each sized to its job: the
    screw-head seat (recess), the pin/heat-set boundary (the screw spans the seat
    to the heat-set, so the pin body is the screw's length − heatset_depth long),
    the heat-set end, and the pod cap one wall past it. `length` is `screw_len`
    unless the boss carries its own — the four-corner's `corner_screw_len`."""
    length = screw_len if length is None else length
    x_seat = x_ext + sx * head_cbore_depth
    x_tip = x_seat + sx * (length - heatset_depth)
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


def _front_socket(x_in, x_ext, sx, z_boss, y_joint, inner):
    """FRONT socket: a collar round the bore — a pipe standing off the ±X wall's
    inner face, from that face out to the cap over the insert's blind end, one
    `wall` of material round the bore its whole length.

    Its aft face lands on the lip rim (`_y_boss` + socket_r, which is what `lip_len`
    is struck from) and its forward face a hair ahead of the lip's own fusion
    shoulder, so it stands on the lip band down its whole length.

    THE COLLAR IS A D BELOW ITS AXIS. A round pipe tangent to a flat leaves a crevice
    either side of the tangent line — an overhang that starts at zero degrees — so the
    lower half is squared to the flat it meets: the floor collar's fill stands on the
    slab, and any other level's stands on a 45° web run down the lip's own face, the
    corner pedestal's idiom. A collar whose crown reaches the ceiling squares its upper
    half into it the same way.

    Bore, heat-set and the plug's slide path are cut afterwards."""
    _xs, _xt, _xh, x_cap = _boss_x(x_ext, sx)
    xa, xb = sorted((x_in, x_cap))
    yb = _y_boss(y_joint)
    iz0, iz1 = inner[4], inner[5]
    boss = _xcyl(socket_r, yb, z_boss, xa, xb)
    boss = boss.fuse(_ybox(xa, xb, yb - socket_r, yb + socket_r,
                           z_boss - socket_r, z_boss))
    if z_boss - socket_r > iz0 + 0.01:
        lip_in = x_in + sx * wall
        drop = abs(x_cap - lip_in)
        floor = z_boss - socket_r
        boss = boss.fuse(_xz_prism(yb - socket_r, yb + socket_r,
                                   [(lip_in, floor), (x_cap, floor),
                                    (lip_in, floor - drop)]))
    if z_boss + socket_r > iz1 - 0.01:
        boss = boss.fuse(_ybox(xa, xb, yb - socket_r, yb + socket_r,
                               z_boss, z_boss + socket_r))
    return boss


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


def _screw_cut(x_ext, sx, z_boss, y_boss, length=None):
    """M3 shank clearance from the ±X exterior through the plug to the heat-set,
    plus the SHCS head counterbore at the exterior — the seat one wall outboard
    of the heat-set."""
    _xs, x_tip, _xh, _xc = _boss_x(x_ext, sx, length)
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


def _z_back_station_y(iy1):
    """The BACK column's X-pin station in Y — the rear-wall corner.

    The collar's own +Y face lies on that wall's inner face — unless the standing corner
    there carries a column, and then the lens runs forward to its cusp and would hole the
    collar's root. So that end answers the way the front column's front-wall station does
    (`_z_front_station_y`): one socket_r ahead of the cusp."""
    r = socket_bore_dia / 2.0
    plain = iy1 - wall - r
    if any(sy > 0 for _sx, sy in column_corners):
        plain = min(plain, iy1 - _column_along() - socket_r)
    return plain


def _z_stations(inner, y_joint):
    """X-axis pin stations along the Z seams — ONE per ±X wall per Y column, at the
    wall end of that column's seam. The seam's other end is the four-corner screw
    (`_corner_socket`), so each column is pinned at both ends of its span and cannot
    hinge open.

    Front column: the front-wall corner — or, where that corner carries a column,
    behind it (`_z_front_station_y`). Back column: the rear-wall corner. Every
    station stands in the ±X band the walls' standoff opens off the cold core, and
    the depth between the two columns is what `east_band_free_y` hands a body hung
    on that wall. The stations ride the stated seam plane."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    yf = _z_front_station_y(iy0)                    # front column, front wall
    ybr = _z_back_station_y(iy1)                    # back column, rear wall
    out = []
    for ys, col in ((yf, "front"), (ybr, "back")):
        out.append((ix0, ix0 - wall, +1.0, ys, col))
        out.append((ix1, ix1 + wall, -1.0, ys, col))
    return out


def _lip_ring(inner, gap, z0, z1):
    """One `_lip_band` skin over a height span, less the `gap` y-span — the shape both the
    lip and the wall under it are cut from, so the two come out of one figure and fuse into
    one wall with no step where they meet.

    THE TWO ASK FOR DIFFERENT GAPS, which is the whole reason this takes one rather than
    striking it. A gap is room for a telescope, and only the lip is one."""
    ix0, ix1 = inner[0], inner[1]
    ring = _lip_band(inner, (z0, z1))
    return ring.cut(_ybox(ix0 - 1.0, ix1 + 1.0, gap[0], gap[1], z0 - 1.0, z1 + 1.0))


def _z_lip(inner, y_joint, zj):
    """The bottom pieces' seam lip: a full-wall band whose outer faces are
    flush with the body's inner walls, standing on the seam mouth and running
    up over the overlap to the rim. The segment
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
    piece above it on the same one wall of overlap every other face uses.

    THIS BAND IS WHAT STANDS PROUD OF THE MOUTH AND NOTHING ELSE. It begins on the seam
    plane, because that is where the piece it belongs to ends: below the mouth there is no
    telescope, only wall, and `_lip_underwall` carries it. A band reaching one `wall` down
    past the mouth would be describing the wall it is standing on.

    ITS GAP IS OPENED BOTH WAYS off the joint. Aft, for the other piece's Y lip to pass;
    FORWARD, because this band is proud on the same wall surface its own piece's Y lip is
    proud on, and two telescopes that meet on one surface have nowhere to go — the front
    piece's Z lip would rise into the front-TOP piece's Y lip. `z_lip_y_margin` is the air
    either side of that."""
    return _lip_ring(inner,
                     (y_joint - wall - z_lip_y_margin, y_joint + lip_len + z_lip_y_margin),
                     zj, zj + lip_len)


def _lip_underwall(inner, y_joint, zj):
    """The wall under a bottom piece's lip: the same skin, floor slab to the fusion
    shoulder, so the wall is `2 * wall` thick from the slab to the lip rim.

    THE LIP'S UNDERSIDE WOULD OTHERWISE BE A SOFFIT — one `wall` wide, pointing at the
    bed, running three sides of a piece that prints floor-down, with nothing under it to
    print on. A band fused onto a one-`wall` wall is a ledge; a band the wall has been
    that thick all the way up to is a wall. This is the material that makes it the second
    one, and the piece comes off the bed with no bridge in it and no support to pick out.

    IT IS NOT PART OF THE SEAM. The lip's own band rides the seam height, which is what
    `_lip_denied` reasons about and what the search moves; this stands between the floor
    and that band wherever the band ends up. What has to be clear of it is the pack, and
    the pack already stands one `wall` off both ±Y walls (`front_seam_clear`,
    `rear_seam_clear`) and one boss chain off both ±X ones (`side_band_inset`) — every
    face this skin is on. It runs to the SEAM MOUTH and not to one `wall` under it: the
    last `wall` before the mouth is no more a telescope than the first one off the slab,
    and stopping short of the mouth is what put a slit down the flank the first time. `wall-under-lip` measures that rather than assuming it, and
    `lip_face_x` is the flank a body down there meets.

    AND ITS GAP IS OPENED ONE WAY, which is where it parts from the lip's. This is wall,
    not a telescope: nothing it meets has to slide anywhere, so the only thing it owes room
    to is the OTHER piece's Y lip, aft of the joint. Carried to the joint on its own side it
    simply fuses into its own piece's Y lip and the flank comes out one unbroken `2 * wall`
    from the front wall to the Y rim. Opened the lip's way instead — off the joint in BOTH
    directions — it would stop `wall + z_lip_y_margin` short of a tongue that starts one
    `wall` short, and what stands between the two is nothing: a `z_lip_y_margin`-wide,
    one-`wall`-deep channel running the flank's whole height, blind on the slab and open
    only at the rim. That is not a gap for anything, it is a slit down the piece's most
    loaded corner, and it is narrower than two extrusions of the nozzle this box prints
    with."""
    return _lip_ring(inner, (y_joint, y_joint + lip_len + z_lip_y_margin),
                     inner[4], zj)


def _z_station_y(ys):
    """The Y band a Z station occupies — its collar's own reach, one socket_r
    either side of the bore axis, which is also what the pin inside it needs. Read
    by `_seam_furniture_spans` to say where the ±X chain bands have to stand clear,
    off the same figure the collar is built from."""
    return (ys - socket_r, ys + socket_r)


def _z_pod(x_in, x_ext, sx, ys, inner, zj):
    """BOTTOM boss: the plastic round the bore, off the ±X wall's inner face out to the
    cap, at least one `wall` of material round the bore its whole length. Its +Z face
    lands ON the lip rim and its −Z face a hair under the seam mouth, so it stands on the
    band the whole way — on the lip above the mouth and on the wall under it below, which
    is one surface and not two.

    ITS SECTION IS A SQUARE AND NOT A CIRCLE, and that is the whole of why the rim is
    clean. `lip_len` is derived (`plug_dia/2 + socket_r`) so the boss's far face lands on
    the rim — but a pipe has no face there, only the line where it grazes the plane, and a
    graze is a wedge that thins to nothing. Every wall crossing near it — the slide
    channel, the pin's flanks, a column's own round — then cuts a feather off that wedge.
    A flat top makes the derivation true instead of nearly true, and the feathers have
    nowhere to form.

    Its upper half telescopes into the top piece, and a station abutting a wall sits in one
    of the box's rounded verticals — the cavity intersect holds it inside whatever column
    stands in that cavity's corners, and against flats that clip is arcs and lines where
    against a pipe it was a b-spline.

    IT STANDS ON A 45° WEB run its whole reach down the wall — the box's one boss shape.
    At the front-wall stations the condenser's crown stands under the band, one
    `cond_mount_clear` off the lip face, and the 45° passes over it on that lane."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    _xs, _xt, _xh, x_cap = _boss_x(x_ext, sx)
    xa, xb = sorted((x_in, x_cap))
    zp = _z_pin_z(zj)
    zb = zp - socket_r
    lip_in = x_in + sx * wall
    boss = _ybox(xa, xb, ys - socket_r, ys + socket_r, zb, zp + socket_r)
    boss = boss.fuse(_xz_prism(ys - socket_r, ys + socket_r,
                               [(lip_in, zb), (x_cap, zb),
                                (lip_in, zb - abs(x_cap - lip_in))]))
    return boss.intersect(_cavity(inner, 0.0, (iz0 - 1.0, iz1 + 1.0)))


def _z_pin(x_ext, sx, ys, zj):
    """TOP tongue: ONE prism from the ±X exterior to the heat-set — a half-round nose
    below its axis, parallel flanks from that axis up to the lip rim. The nose registers
    in the bottom socket's bore; the flanks stand in the +Z channel the nose swept coming
    down. Its lowest point is the top piece's own mouth, so the wall it drives through
    carries the whole of it.

    THE FLANKS ARE THE NOSE'S OWN TANGENT PLANES, one `plug_dia` apart, so the section is
    a slot's shape and the two meet with material either side and no edge between them —
    the box's boss idiom (`_corner_socket`'s D) stood on its head. Set
    the flanks on the crown instead of the axis and they bear on the nose along one line:
    a blade hung off a tangent, which slices in the model and prints as nothing.

    ONE `plug_dia` IS ALSO THE CHANNEL LESS ITS SLIP, since the bore is the plug plus
    `split_slip` — so the same width that continues the nose rides the channel free."""
    _xs, x_tip, _xh, _xc = _boss_x(x_ext, sx)
    zp = _z_pin_z(zj)
    r = plug_dia / 2.0
    xa, xb = sorted((x_ext, x_tip))
    nose = _xcyl(r, ys, zp, x_ext, x_tip)
    shank = _ybox(xa, xb, ys - r, ys + r, zp, zj + lip_len)
    return _unified(nose.fuse(shank)).val()


def _z_pod_cuts(x_in, x_ext, sx, ys, zj):
    """Bottom-socket inner cuts: the bore that receives the tongue's nose, the heat-set
    pocket at the deep end, and a +Z channel for the slide-down — struck at the bore's own
    axis carrying the bore's width, so the channel's walls continue the bore's sides.

    THE SLIP LIVES ON THE +Z (SLIDE-IN) SIDE: the bore is shifted +slip/2, which puts its
    lowest line on the mouth (`zj`) where the nose's own lowest line lands. Seated, the two
    bear on that plane and the whole slip is overhead — and the channel, a slip wider than
    the tongue that fills it, is closed to the rim."""
    _xs, x_tip, x_heat, _xc = _boss_x(x_ext, sx)
    zp = _z_pin_z(zj)
    bore_z = zp + split_slip / 2.0
    bore = _xcyl(socket_bore_dia / 2.0, ys, bore_z, x_in, x_tip)
    heat = _xcyl(heatset_dia / 2.0, ys, zp, x_tip, x_heat)
    bx0, bx1 = sorted((x_in, x_tip))
    chan = _ybox(bx0, bx1, ys - socket_bore_dia / 2.0, ys + socket_bore_dia / 2.0,
                 bore_z, zj + lip_len + 1.0)
    return bore.fuse(heat).fuse(chan)


# --- the four-corner screw: the Y-boss idiom with the seam plane through it --
#
# One per side wall at (`_y_boss`, `z_seam`). The BACK pair carries the plug — each piece
# its own half-cylinder, the flat on the plane (the bottom's half prints at its rim, the
# top's flat-face-down on its own mouth). The FRONT lip's two halves carry the slide
# channel, and FRONT-BOTTOM alone carries the socket: a pedestal off its own lip face,
# proud through the plane the way the lip itself is, so the bore and the insert live in
# one piece's solid and the heat-set presses into a whole mouth. A 45° web under the
# pedestal carries it to the lip face, so the piece prints floor-down with nothing
# hanging. The screw crosses all four pieces; the plug registers in the bore the way
# every Y-boss plug does.


def _corner_plug(x_ext, sx, zlo, zhi):
    """The back pair's pin at the four-corner, clipped to the piece band it is fused
    into — each back piece carries the half the seam plane leaves it."""
    _xs, x_tip, _xh, _xc = _boss_x(x_ext, sx, corner_screw_len)
    yb = _y_boss(y_seam)
    xa, xb = sorted((x_ext, x_tip))
    return _xcyl(plug_dia / 2.0, yb, z_seam, x_ext, x_tip).intersect(
        _ybox(xa - 1.0, xb + 1.0, yb - plug_dia, yb + plug_dia, zlo, zhi))


def _corner_socket(x_in, x_ext, sx):
    """Front-bottom's socket at the four-corner: the pedestal — a collar off the lip's
    own inner face out to the cap, a D below its axis, with the 45° web under it.

    The D is the merge: a round pipe tangent to the web's flat top leaves a crevice
    either side of the tangent line, so the lower half is squared and the two meet on
    one flat."""
    _xs, _xt, _xh, x_cap = _boss_x(x_ext, sx, corner_screw_len)
    yb = _y_boss(y_seam)
    lip_in = x_in + sx * wall
    xa, xb = sorted((lip_in, x_cap))
    collar = _xcyl(socket_r, yb, z_seam, xa, xb)
    floor = z_seam - socket_r
    fill = _ybox(xa, xb, yb - socket_r, yb + socket_r, floor, z_seam)
    drop = abs(x_cap - lip_in)
    web = _xz_prism(yb - socket_r, yb + socket_r,
                    [(lip_in, floor), (x_cap, floor), (lip_in, floor - drop)])
    return collar.fuse(fill).fuse(web)


def _corner_cuts(x_in, x_ext, sx):
    """The corner socket's inner cuts — bore, insert pocket, and the +Y slide channel,
    the Y-boss cuts one wall deeper. Cut from BOTH front pieces: the channel crosses the
    lip, so each piece's own half comes out of its own solid."""
    _xs, x_tip, x_heat, _xc = _boss_x(x_ext, sx, corner_screw_len)
    yb = _y_boss(y_seam)
    bore_y = yb + split_slip / 2.0
    bore = _xcyl(socket_bore_dia / 2.0, bore_y, z_seam, x_in, x_tip)
    heat = _xcyl(heatset_dia / 2.0, yb, z_seam, x_tip, x_heat)
    bx0, bx1 = sorted((x_in, x_tip))
    chan = _ybox(bx0, bx1, bore_y, y_seam + lip_len + 1.0,
                 z_seam - socket_bore_dia / 2.0, z_seam + socket_bore_dia / 2.0)
    return bore.fuse(heat).fuse(chan)


# --- the pump bay's own machinery -------------------------------------------

def bay_x_span(inner):
    """The bay's two jambs: the flat front wall between the corner columns' along-wall
    posts' own reach (`post_along`). The columns ARE the jambs — nothing of the
    front wall's flat span survives outside the cartridge's face."""
    return inner[0] + post_along, inner[1] - post_along


def _soffit_c(outer):
    """The display housing's soffit as the constant of its own 45° plane, z = y + c —
    the facet's back plane, `display_facet_thickness` behind the face along its normal."""
    _a, _n, origin, _dy, _dz = _facet_geom(outer)
    return (origin[2] - origin[1]) - display_facet_thickness * math.sqrt(2.0)


def _pump_relief_regions(pump_trays):
    """One pocket per pump in the front wall's section, as (x0, x1, z0, z1, floor), struck
    off its own tray station — across, the tray's own half-width and a slip; in height, the
    head's hang under the station to the tray's crown over it; floored on
    `pump_relief_floor`, the plane the tray's root is struck to.

    ITS OWN Z0 IS THE LOWEST PLANE THE CARTRIDGE REACHES, so the bay floor's top is struck
    on it (`bay_floor_z`) and the sill and the face's bottom reveal come off one figure."""
    out = []
    for cx, _cy, cz in pump_trays:
        hw = _tray.half_width() + 1.0
        out.append((cx - hw, cx + hw, cz - _tray.head_depth - 1.0,
                    cz + _tray.depth() + 1.0, pump_relief_floor))
    return out


def _front_relief_regions(pump_trays):
    """Every region the front wall's section is relieved over: the stated refrigeration
    bay and the pumps' own pockets."""
    return [fridge_relief] + _pump_relief_regions(pump_trays)


def _front_relief_cuts(inner, pump_trays):
    """The relief pockets cut out of the front wall: a box to each region's floor, its
    ceiling rising at `relief_chamfer` to the mouth so the pocket prints in a standing
    wall with no flat over it."""
    iy0 = inner[2]
    cuts = []
    for x0, x1, z0, z1, floor in _front_relief_regions(pump_trays):
        depth = iy0 - floor
        cuts.append(_ybox(x0, x1, floor, iy0 + 1.0, z0, z1))
        cuts.append(_yz_prism(x0, x1, [(floor, z1), (iy0 + 1.0, z1 + depth + 1.0),
                                       (iy0 + 1.0, z1)]))
    return cuts


def _front_floor(regions, b):
    """The front-wall surface one placed body faces: the deepest relief whose region holds
    its whole (x, z) footprint, or the interior plane itself."""
    floors = [front_plane_y]
    for x0, x1, z0, z1, floor in regions:
        if (b.xmin >= x0 - 1e-6 and b.xmax <= x1 + 1e-6
                and b.zmin >= z0 - 1e-6 and b.zmax <= z1 + 1e-6):
            floors.append(floor)
    return min(floors)


def _front_flat_lip_drop(inner, zj):
    """The front wall's share of the Z lip and its underwall skin, given up across the bay.

    THE BAY FLOOR STANDS IN THIS BAND AND THE PUMP HEADS RUN DOWN THROUGH IT ON THEIR WAY
    OUT, so the flat span cannot carry a lip there at any height. Below the seam the wall is
    one `front_wall` section, slab to mouth. The corner columns keep their wraps — the front
    Z-joint is their pillar telescopes and the butt at the seam."""
    bx0, bx1 = bay_x_span(inner)
    # THE AFT FACE IS THE SKIN'S OWN, not a hair past it. The skin stands exactly one `wall`
    # proud of the cavity face, so a cut to `inner[2] + wall` takes all of it and stops; the
    # tenth that used to be added reached into the cavity beyond, and where that overshoot
    # ran out at the jamb it left faces of no width at all — six edges under a micron.
    return _ybox(bx0, bx1,
                 inner[2] - 0.1, inner[2] + wall,
                 inner[4] - 1.0, zj + lip_len + 1.0)


def _sill_wash(inner, outer, z_sill):
    """The sill's top face cut falling `sill_wash` toward the exterior, across the bay —
    the reveal's drain. What runs down the face and gets past the reveal lands on this
    slope and runs back out the front. The sill is the bay floor's own top, so the drain is
    a cut in the wall the floor's fore edge roots on."""
    bx0, bx1 = bay_x_span(inner)
    return _yz_prism(bx0, bx1,
                     [(outer[2] - 0.1, z_sill - sill_wash), (outer[2] - 0.1, z_sill + 0.001),
                      (inner[2] + 0.1, z_sill + 0.001)])


def _bay_cut(inner, outer, bay, pump_trays, plate):
    """The bay's opening through front-top: the flat wall band jamb to jamb from the
    floor's own top to the bay top, both flanks over the rim (`_flank_opening`), and the soffit
    wedge's share where the facet slab leans into the cans' path above the cavity ceiling
    line."""
    bx0, bx1, top = bay
    c = _soffit_c(outer)
    wall_box = _ybox(bx0, bx1, outer[2] - 1.0, inner[2] + 0.5,
                     bay_floor_z(pump_trays)[1], top)
    wedge_box = _ybox(bx0, bx1, inner[2] + 0.4, top - c + 1.5,
                      inner[2] + c - 1.5, top)
    return wall_box.fuse(wedge_box).fuse(
        _flank_opening(inner, plate["aft_y"], z_seam + lip_len + wall, top))


def _rim_cap(inner, outer, plate, zj):
    """THE SEAM'S CEILING, both flanks — a `wall`-thick slab bedded on the lip rim, from the
    exterior face in to the bay's own jamb, front wall back to the collet plate's fore face.

    Everything the Z seam carries stands under it: the lip rim, the boss's flat crown, the
    channel the pin rides down. Those all top out on ONE plane, because `lip_len` is derived
    (`plug_dia/2 + socket_r`) to land the boss's far face on the rim — so the cap beds on the
    whole of it at once rather than bridging anything.

    IT STOPS ON THE JAMB. `bay_x_span` is the cartridge's own span and this is what stands
    outboard of it, so nothing of the cap is ever in the withdrawal path. AFT IT STOPS ON THE
    PLATE'S FORE FACE, and not because the opening over it does — the opening runs on past to
    the tee wall. It stops there because the steel's own berth is what is aft of it: the cap
    is the last printed thing under the plate's end, and a millimetre more of it is a
    millimetre the plate cannot come down through.

    AND THE SILHOUETTE TAKES ITS OUTBOARD END. Struck as a rectangle it reaches the exterior
    plane, which the box's front corners do not — `corner_round` has turned away from it by
    then — so the slab is cut to `_rounded_outer` and the corner it ends on is the box's own,
    not a square one standing proud of it."""
    bx0, bx1 = bay_x_span(inner)
    rim = zj + lip_len
    out = None
    for x0, x1 in ((outer[0], bx0), (bx1, outer[1])):
        slab = _ybox(x0, x1, inner[2], plate["fore_y"], rim, rim + wall)
        out = slab if out is None else out.fuse(slab)
    return out.intersect(_rounded_outer(outer))


def _flank_opening(inner, y_aft, z0, z1):
    """Front-top's ±X faces, open across the cartridge's own storey — and THE CORNER COLUMNS
    ARE THE ONLY THING LEFT IN THEM.

    A column here is the whole of the box's corner post: the side wall's own section, the
    front wall's, and the quarter-round between them. So the opening does not begin at the
    exterior — it begins where that post's arc lands on the side wall's inner face, one
    `_column_along` aft of `front_plane_y`, and runs from there to the TEE WALL's fore face.
    Nothing of the box stands in it after that.

    IT RUNS PAST THE PLATE AND STOPS ON THE WALL BEHIND IT. Ending on `plate["fore_y"]` left
    the plate's own thickness of side wall standing aft of the opening — a band one `wall`
    deep and the whole storey tall, whose only job was to be the outboard end of a berth the
    plate already keeps `enclosure_assembly.PLATE_END_AIR` off. `plate["aft_y"]` is where the
    section behind it starts, so the opening ends on printed wall rather than on a free edge
    of its own, and the plate's ends stand in the opening the way everything else in this
    storey does.
    ITS FLOOR IS THE SEAM'S CAP (`_rim_cap`), one `wall` over the rim. Under the rim
    front-bottom's lip telescopes into this wall and an opening cut there is a seam that does
    not close; between the two planes stands the cap, and cutting THAT would open the seam's
    cavity to the storey it is meant to be shut off from."""
    out = None
    for x_in, sx in ((inner[0], +1.0), (inner[1], -1.0)):
        x_out = x_in - sx * (wall + 1.0)
        box = _ybox(min(x_in, x_out), max(x_in, x_out),
                    inner[2] + _column_along(), y_aft, z0, z1)
        out = box if out is None else out.fuse(box)
    return out


def _cartridge_face_region(inner, outer, bay, pump_trays, plate):
    """The bay region the cartridge's face keeps: the same figures one slip and one reveal
    smaller, so the face rides its opening on stated air."""
    bx0, bx1, top = bay
    fx0, fx1 = bx0 + bay_face_slip, bx1 - bay_face_slip
    z0, z1 = bay_floor_z(pump_trays)[1] + face_reveal, top - face_reveal
    c = _soffit_c(outer)
    return (_ybox(fx0, fx1, outer[2] - 1.0, inner[2] + 0.5, z0, z1)
            .fuse(_ybox(fx0, fx1, inner[2] + 0.4, z1 - c + 1.5, inner[2] + c - 1.5, z1)))


def cap_split_z(pump_trays):
    """The plane the cartridge parts on — the pump's own BRACKET plane.

    `pump_tray` roots each tray's plate on the head's crown, which `kamoer_kphm400` calls
    `base_plane_z`: the head-to-boss junction, and the plane the part's stamped bracket sits
    in. Above it a pump is boss and can, held by the tray that bores them; below it a pump is
    head, and what closes on it is the cap. Taking the split there means the piece that holds
    the pump up and the lip it holds it by are on one plane instead of two."""
    return min(cz for _cx, _cy, cz in pump_trays)


def cap_band_x(pump_trays):
    """The screw lane between the two heads, as (x0, x1) — each head's own inboard face,
    less `cap_band_air`.

    THIS IS THE ONE COLUMN OF THE CARTRIDGE WITH NOTHING IN IT AT ANY HEIGHT. No pump, no
    barb tube, no fitting: the inboard barbs stand outboard of it and their tubes leave aft
    of the block entirely. So it is where the cap gives up its fill, where a screw crosses,
    and where a driver reaches the screw's head."""
    edge = min(abs(cx) for cx, _cy, _cz in pump_trays) - _tray.head_half
    return -(edge - cap_band_air), edge - cap_band_air


def cap_screw_ys(inner, plate):
    """The two screws' own Y, fore and aft of the lane's mid-depth.

    The lane runs from the front wall's interior face to the block's aft edge, and a pair
    struck `cap_screw_off` either side of its middle puts both in material the block carries
    on both faces of the split."""
    mid = (inner[2] + (plate["fore_y"] - 2.0)) / 2.0
    return mid - cap_screw_off, mid + cap_screw_off


def _pump_voids(pump_trays, z_top):
    """What each pump takes out of the block, one figure per storey it stands in.

    BELOW THE SPLIT the head is a square prism on the pump's own axis, `cap_pump_air` round
    it, opening out of the cap's underside — the head's front face stands one millimetre over
    the bay floor and no section fits there, so what would be a floor under it is the air the
    part shows through instead. AND THE PRISM GIVES ITS SEATS BACK: `pump_tray.head_seats` is
    the wedge under each of the head's four ramped flanks, and the void keeps none of it, so
    the cap closes on those four faces and the pump stands on them.

    ABOVE THE SPLIT there are two more, one per storey the part carries: the boss over the
    split to its own crown, and the can from that crown up through the ceiling, so the can
    opens out of the block's top.

    ALL THREE ARE CUT FROM THE FILL AND THE TRAY IS FUSED AFTER. A tray conforms to the boss on
    the case's own figure and carries the air that fit belongs to; a void struck here is the
    block's, and the tray puts its own material back inside it."""
    out = []
    half = _tray.head_half + cap_pump_air
    boss = _tray.boss_half + cap_pump_air
    can_r = _tray.can_half + cap_pump_air
    seats = _tray.head_seats(cap_pump_air)
    for cx, cy, cz in pump_trays:
        at = cq.Location(cq.Vector(cx, cy, cz))
        head = _ybox(cx - half, cx + half, cy - half, cy + half,
                     cz - _tray.head_depth - 1.0, cz)
        for seat in seats:
            head = head.cut(seat.moved(at))
        out.append(head)
        out.append(_ybox(cx - boss, cx + boss, cy - boss, cy + boss,
                         cz, cz + _tray.boss_depth))
        out.append(_zcyl(can_r, cx, cy, cz + _tray.boss_depth, z_top + 1.0))
    return out


def _cap_x_span(bay):
    """The cap's own two edges — the deck's own, since nothing of the box stands inside the
    jambs at this storey."""
    _bx0, bx1, _top = bay
    edge = bx1 - bay_face_slip
    return -edge, edge


def bay_floor_z(pump_trays):
    """The bay floor's two planes: its underside on front-top's own seam mouth, and its top
    on the plane the cartridge reaches down to.

    THE FLOOR IS THIS PIECE'S FIRST LAYERS. Front-top beds on the seam plane, so a floor
    struck there lies on the bed and nothing under it hangs. What sets its section is the
    only thing over it: the cartridge's own pump reliefs floor on
    `_pump_relief_regions`' z0, one millimetre under the heads, and the floor's top is that
    plane — so the sill, the face's bottom reveal and the room the heads pass in are one
    figure and not three."""
    return z_seam, min(z0 for _x0, _x1, z0, _z1, _floor in _pump_relief_regions(pump_trays))


def _flank_lip_drop(inner, plate, y_joint, zj):
    """The Z-seam lip given up on BOTH FLANKS over the front run — front-bottom stops
    standing a wall up into front-top there, and nothing above has to open for one.

    `_front_flat_lip_drop`'s twin, turned a quarter: that one gives the lip up across the
    bay's own flat, this one gives it up round the corners and back down each flank as far
    as the tee wall's aft face (`plate["wall_aft_y"]`). What the telescope was doing over
    that run is done better by what stands there now — the seam's cap over it, the bay
    floor bedded through it, the tee wall across it — and a lip that registers nothing is
    a wall poking into a cavity cut to receive it.

    THE BOSS KEEPS ITS PLINTH. Its own `2 * socket_r` of lip is the one thing over this run
    still crossing the seam, because it is what carries the screw and the heat-set — so the
    drop is cut back off each front station and the boss stands on a run of lip its own
    width and no more."""
    # Down to the mouth and NOT past it: below the seam this run is front-bottom's own wall,
    # which the drop has no business in — only the lip standing proud of the mouth.
    lo, hi = zj, zj + lip_len + wall + 1.0
    # WALL TO WALL, and not jamb to jamb. Between the jambs the front flat has already given
    # its lip up (`_front_flat_lip_drop`) and nothing else of the bottom piece stands over
    # the mouth here, so reaching across costs nothing — and stopping ON the jamb would put
    # this cut's own side plane on the one plane three other cuts already end on.
    drop = _ybox(inner[0] - wall - 1.0, inner[1] + wall + 1.0,
                 inner[2] - wall - 1.0, plate["wall_aft_y"], lo, hi)
    for x_in, _x_ext, sx, ys, col in _z_stations(inner, y_joint):
        if col != "front":
            continue
        xa, xb = sorted((x_in - sx * (wall + 1.0), x_in + sx * (wall + 1.0)))
        drop = drop.cut(_ybox(xa, xb, ys - socket_r, ys + socket_r, lo, hi))
    return drop


def _z_seam_berth(inner, plate, y_joint):
    """What front-bottom's Z seam occupies inside front-top's own walls, over the storey the
    bay floor stands in: the lip — the cavity's one-`wall` skin from the seam mouth to the
    rim, less the front-flat span it gives up (`_front_flat_lip_drop`) and less both flanks
    over the front run (`_flank_lip_drop`) — and the front column's socket collars standing
    proud of it.

    Everything front-top stands in this storey opens for it, and over this run that is one
    pocket per collar and nothing else: the lip is not here to be opened for. Every one is
    cut with this one solid, so what a piece has to dodge is never worked out twice.

    OVER THE RIM IT FLARES AT 45°. A notch this deep would otherwise leave a `wall`-wide
    flat looking down at the bed on whatever spans back to the side wall above it; the
    flare rises off the lip's own inner face out to the wall, so the material over the
    notch is laid on the layer under it like every other relief on this box."""
    rim = z_seam + lip_len
    berth = (_lip_band(inner, (z_seam, rim))
             .cut(_front_flat_lip_drop(inner, z_seam)))
    for x_in, sx in ((inner[0], +1.0), (inner[1], -1.0)):
        face = x_in + sx * wall
        berth = berth.fuse(_xz_prism(inner[2] - 1.0, y_joint,
                                     [(face, rim), (x_in, rim), (x_in, rim + wall)]))
    berth = berth.cut(_flank_lip_drop(inner, plate, y_joint, z_seam))
    for x_in, x_ext, sx, ys, col in _z_stations(inner, y_joint):
        if col == "front":
            berth = berth.fuse(_z_pod(x_in, x_ext, sx, ys, inner, z_seam))
    return berth


def _bay_floor(inner, y_joint, plate, pump_trays):
    """THE BAY'S FLOOR: front-top's own storey across the front, from the front wall's
    interior face aft past the collet plate, on the bed and under everything else.

    The collet plate is SUNK IN IT: a blind seat down the floor's top takes the steel's
    foot, so the plate is located fore, aft and across by printed material and carried on
    the seat's own bottom, and nothing over it is closed — with the cartridge out it lifts
    straight up through the bay. The seat's floor is the plate's own z0, struck in
    `enclosure_assembly.collet_plate_spec`, so the steel and the pocket that takes it are
    one figure.

    ONE POCKET PER COLLAR PASSES THE Z SEAM (`_z_seam_berth`), and nothing else does. The
    lip is given up over this whole run (`_flank_lip_drop`), so the floor runs the walls
    whole instead of surrendering `wall` of itself down each flank — what still stands over
    the mouth here is the front boss on its own plinth, and the floor opens for that alone.

    OUTBOARD OF THE BAY IT STANDS TO THE RIM. The cartridge sweeps the span between the
    posts and nothing else does, so either side of that span the floor carries on up to the
    Z-seam rim — and the seam's cap (`_rim_cap`) stands one `wall` on top of that, which is
    what the flank opening floors on. The opening then reads as one ledge from the exterior
    in to the bay's edge instead of the wall's own section and a drop behind it.

    ITS SEAT ENDS ON THE SIDE WALL AND NOT ON THE STEEL. Struck at the plate's own edge plus
    `plate_slot_slip`, the seat stopped 0.1 mm short of the wall — because the plate is
    already `enclosure_assembly.PLATE_END_AIR` inboard of it, and the two clearances were
    stacked on one gap without ever being struck against each other. What stood in the
    difference was a rib 0.1 mm wide and the seat's whole height, which is not a thin wall
    but no wall: below one extrusion the slicer lays nothing there at all. There is nothing
    outboard of the side wall for this seat to hold, so the wall is its end."""
    z0, z1 = bay_floor_z(pump_trays)
    rim = z_seam + lip_len
    bx0, bx1 = bay_x_span(inner)
    slab = _ybox(inner[0], inner[1], front_plane_y,
                 plate["aft_y"] + plate_slot_slip + wall, z0, z1)
    for x_in, edge in ((inner[0], bx0), (inner[1], bx1)):
        slab = slab.fuse(_ybox(min(x_in, edge), max(x_in, edge), front_plane_y,
                               plate["aft_y"] + plate_slot_slip + wall, z1, rim))
    slab = slab.cut(_z_seam_berth(inner, plate, y_joint))
    return slab.cut(_ybox(inner[0], inner[1],
                          plate["fore_y"] - plate_slot_slip,
                          plate["aft_y"] + plate_slot_slip, plate["z0"], rim + 1.0))


def _tee_wall(inner, y_joint, plate, bay):
    """THE WALL THE ANCHOR TEES STAND IN: front-top's own section behind the collet plate,
    wall to wall and the whole height of the bay, with one bore per tee.

    A BORE HOLDS ITS TEE ACROSS ITS OWN AXIS AND LEAVES IT FREE ALONG IT. Each arm carries a
    round collar (`tee_connector.branch_collar`) and the bore closes on that, so a tee is
    located in X and Z by printed material and free in Y — which is the one direction the
    release moves it. What a tee otherwise hangs from is the valve butted onto its run, two
    joints away and answering to a press fit; what it stands in is this.

    ITS FORE FACE IS THE STEEL'S AFT FACE, struck once as one figure
    (`enclosure_assembly.collet_plate_spec`). The plate drops down in front of it, so every
    bore is stopped at its fore mouth by steel and the collet nose that lands there lands on
    steel and not on plastic.

    ITS AFT FACE STOPS SHORT OF THE TEE, ON PURPOSE. A tee travels WITHIN this wall, and the
    wall is not allowed to be what ends that travel: the face stands one whole stroke plus
    `TEE_WALL_BODY_AIR` fore of the tee's own body, so at full release there is still air
    between the two. Depth past that plane is not the wall's to take — it is the tee's, and a
    wall standing in it lands the tee's shoulder before the grip has opened. What the wall
    holds is the collar, across the bore; what stops the tee is the steel, and nothing else.

    AND IT IS THE BAY'S BACK. Over the plate's own band the steel closes the bay; above and
    below it nothing does, and the berth the cartridge leaves looks into the cavity. This
    stands the whole storey, so what is behind the bay is a wall.

    AND THE Z SEAM DOES NOT PASS IT AT ALL, so this wall opens for nothing but its own bores.
    The lip is given up over this whole band (`_flank_lip_drop`) and the front bosses stand
    fore of it, so `_z_seam_berth` is empty across the wall's own slab — measured, 0.0 mm3 of
    it — and the wall comes out solid flank to flank. It therefore takes no berth cut: a cut
    that removes nothing is not a guard, because nothing here re-reads it if the lip ever
    comes back. What would bring the lip back is a change to `_flank_lip_drop`, and this
    wall's slab is struck on the plate's own two planes, so the two would part in silence."""
    slab = _ybox(inner[0], inner[1], plate["aft_y"], plate["wall_aft_y"], z_seam, bay[2])
    for hx, hz in plate["holes"]:
        slab = slab.cut(_tee_bore(plate, hx, hz))
    return slab


def _ridge_wall(inner, outer, plate, bay):
    """THE RIB THAT CARRIES THE RIDGE: front-top's own section from the tee wall's crown up to
    the display housing's back, wall to wall, standing under `pcb_ridge` over the whole of it.

    WHAT IT CARRIES IS A STARTING LINE. Both faces meeting at that ridge point down, so the
    first bead laid along it is laid on air — 106 mm of it, in a cavity that closes before the
    piece is finished, which is why it cannot be supported and has to be built. Everything
    above the ridge is 45° and lays itself.

    ITS FORE FACE IS TWO PLANES THE BOX ALREADY HAS, AND NO THIRD ONE. Below, the bay's own
    back (`plate["aft_y"]`) carried straight up off the tee wall's crown, so the storey over
    the bay reads as the same plane the bay does. Above, THE HOLE'S OWN END WALL, carried on
    past the slab's back until it reaches that plane — 45°, which is both the steepest a face
    may hang at and the plane the display's body already lies against, so the rib presents the
    part the surface its hole presents and no new fit. The two meet where they meet; that
    corner is read, not chosen.

    ITS AFT FACE IS THOSE TWO OFFSET ONE `ridge_wall_t`, and its top is the slab's own back —
    struck on that plane rather than into it, so the rib and the housing meet on one figure.
    The jog is what keeps it off the funnel: a rib of this section run straight up would stand
    in the hopper's throat, and one slanted straight from crown to ridge would run into the
    display's own body where it stands proud of the slab.

    IT RUNS WALL TO WALL AND NOT THE RIDGE'S OWN LENGTH. What it carries is `display_pcb_x` of
    line, but a rib ending in free air at each end of that line would stand on the tee wall's
    crown with two free ends and nothing at its own; run out to the flanks it lands in the side
    walls and the storey over the bay is closed rather than partly closed. THAT CLOSING IS THE
    COST: this is now the only section between the bay's storey and the cavity aft of it, so
    anything crossing crosses through it.

    ONE THING DOES. The bore is the config display's loom (`cable_sleeve_open`), teardropped
    (`_teardrop_y`) for the reason a tee's bore is: the rib beds on Z and a bore on Y lies
    horizontal in it.
    It stands at the middle of the rib's own straight run, on the box's centreline, which is
    where the display's back is and where the loom leaves it: read, not chosen. The straight run
    is where it goes because the run has two parallel faces to bore between, and the ramp above
    it is what the ridge stands on — the bore is not allowed near that, and `ridge-carried` is
    what says so."""
    ry, rz = pcb_ridge(outer)
    fore, foot, t = plate["aft_y"], bay[2], ridge_wall_t
    ramp, back = ry + rz, rz - ry     # the hole's end wall, y + z; the slab's back, z - y
    d = t * math.sqrt(2.0)            # that ramp offset one thickness, along Y
    jog = ramp - fore                 # where the fore face leaves the bay's plane for the ramp
    slab = _yz_prism(
        inner[0], inner[1],
        [(fore, foot),                                          # the bay's back, on the crown
         (fore, jog),                                           # where it meets the end wall
         (ry, rz),                                              # the ridge
         ((ramp + d - back) / 2.0, (ramp + d + back) / 2.0),    # the top face's aft end
         (fore + t, ramp + d - (fore + t)),                     # the aft face's own jog
         (fore + t, foot)])
    return slab.cut(_teardrop_y(cable_sleeve_open / 2.0, display_centre_x(outer),
                                (foot + jog) / 2.0, fore - 1.0, fore + t + 1.0))


def _teardrop_y(r, x, z, y0, y1):
    """The cutter for a bore on Y, TEARDROPPED — a horizontal hole in a piece bedded on Z.

    A ROUND HOLE ON A HORIZONTAL AXIS HAS NO TOP. Its crown is where the arc turns over, and
    the layer that closes it is laid across the chord beneath with nothing under it. The roof
    is two 45 degree planes standing on the bore's own tangent points and meeting over its
    axis: 45 degrees is the steepest the arc itself reaches before it turns over, so the planes
    take the hole from exactly where it stops being printable, and nothing over it is laid on
    air. The three lower quarters — which is what a bore bears on — are untouched."""
    t = r / math.sqrt(2.0)
    return _ycyl(r, x, z, y0, y1).fuse(
        _xz_prism(y0, y1, [(x - t, z + t), (x + t, z + t), (x, z + r * math.sqrt(2.0))]))


def _tee_bore(plate, hx, hz):
    """One tee's bore through that wall, teardropped (`_teardrop_y`) because this piece beds on
    the seam plane and a bore on Y lies horizontal in it.

    AND IT STEPS. Fore of `collar_in_y` it is bored for the COLLAR, which is what it journals;
    aft of that station for the ARM alone, which is narrower. The collar cannot pass into the
    smaller bore, so the ring between the two is what the tee rests against — its aft stop, and
    the reason a tube can be pushed into its branch collet without driving the tee out of the
    way. The release travels the other direction and never touches it."""
    y0, y1 = plate["aft_y"] - 1.0, plate["wall_aft_y"] + 1.0
    cut = None
    for r, a, b in ((plate["bore_r"], y0, plate["collar_in_y"]),
                    (plate["arm_bore_r"], plate["collar_in_y"], y1)):
        part = _teardrop_y(r, hx, hz, a, b)
        cut = part if cut is None else cut.fuse(part)
    return cut


def _unified(solid):
    """One printed piece, with its coincident-plane seams merged.

    EVERY BOOLEAN LEAVES SPLITTERS. A cutter that fuses a bore to a channel standing on that
    bore's own axis lands the tangent arc on the piece as a seam across one plane, and the two
    faces either side of it are one surface reported as two. A volume cannot see them and a
    clash cannot either; on a section they read as a hole that is not there. The box carries
    them in the hundreds otherwise, so this is one call at the end of a piece rather than a
    guard at every fuse that makes one."""
    return cq.Workplane(obj=solid).clean()


def build_cartridge(box, halves_cache=None):
    """THE PUMP CARTRIDGE: the bay's face and the tray deck behind it, one printed piece.

    The face is the front half's own material inside `_cartridge_face_region` — the flat
    span jamb to jamb, one slip inside the opening the bay cut removes from front-top, pump
    reliefs and all — so the opening and the thing that fills it come out of one figure. It
    stops at `bay_x_span` at every height: the corner posts stand in this piece's own
    withdrawal path, and nothing of it reaches their x. The deck is the two pump trays rooted
    on the reliefs' floor, webbed across by `_tray_webs`' own boxes.

    WHAT STOPS IT ON THE STEEL IS THE CAP'S OWN AFT FACE, one storey down — this piece owns
    no feature below `cap_split_z`. Printed face-down: the outer skin is the bed, the block
    stands off it, and every pocket rises as a plateau's absence with nothing hanging."""
    inner, outer, plate = box.inner, box.outer, box.collet_plate
    solid = _cartridge_gross(box, halves_cache).cut(_cap_room(box))
    # ITS BOTTOM IS ONE PLANE, AND THAT PLANE IS THE FACE'S OWN SILL REVEAL. Where no head
    # noses in, the front wall's section runs back to `front_plane_y`, and that section is
    # still the face — but the fill under the split carried it down onto the bay floor while
    # the face beside it stood one `face_reveal` up, so the piece's underside stepped and a
    # riser of exactly `face_reveal` ran along every band to carry the step. What rides the
    # floor is the cap; nothing of this piece reaches below the reveal that keeps its face
    # off the sill.
    floor_top = bay_floor_z(box.pump_trays)[1]
    solid = solid.cut(_ybox(outer[0] - 1.0, outer[1] + 1.0, outer[2] - 1.0, box.y_joint,
                            outer[4] - 1.0, floor_top + face_reveal))
    for bore in _cap_screws(inner, plate, box.pump_trays)[1]:
        solid = solid.cut(bore)
    return _unified(solid)


def _cartridge_gross(box, halves_cache=None):
    """THE CARTRIDGE AND ITS CAP AS ONE SOLID, before `cap_split_z` parts them.

    The bay's own room, FILLED. The face comes out of the front
    half's own material, the two trays root on the reliefs' floor and web across, and then
    the block takes everything between the face and the collet plate that no pump stands in
    — the deck's own width, both sides of the split. `_pump_voids` cuts the pumps out last,
    so each can opens through the ceiling and each head through the underside.

    ONE FIGURE, TWO PIECES. `build_cartridge` keeps what is over the split and
    `build_pump_cap` what is under it, so the joint is a plane through one solid rather than
    two solids drawn to meet on one."""
    inner, outer = box.inner, box.outer
    bay, plate = box.pump_bay, box.collet_plate
    if not bay or not plate:
        raise ValueError("a pump cartridge wants a bay and a collet plate, and this box "
                         "carries neither station — the pack has no pumps to pull")
    if halves_cache is not None and "cartridge-gross" in halves_cache:
        return halves_cache["cartridge-gross"]
    if halves_cache is not None and "front" in halves_cache:
        half = halves_cache["front"]
    else:
        half = build_front_half(box)
        if halves_cache is not None:
            halves_cache["front"] = half
    face = _cartridge_face_region(inner, outer, bay, box.pump_trays, plate)
    solid = half.val().intersect(face)
    bx0, bx1, top = bay
    dx0, dx1 = bx0 + bay_face_slip, bx1 - bay_face_slip
    cx0, cx1 = _cap_x_span(bay)
    # THE CAP'S OWN AFT FACE IS THE STOP. Its whole storey stands under the plate's top, so
    # the face it presents to the steel is the piece's own — no pad hangs off anything to
    # reach it — and `cap_kiss` is the air left at that face when the cartridge is home.
    #
    # BOTH STOREYS PRESENT THAT SAME FACE. The deck stood further fore than the cap for no
    # stated reason, which put a step across the block's whole back and a ledge at the split
    # to carry it. One plane for both is one face against the steel and no ledge at all.
    deck_aft = cap_aft = plate["fore_y"] - cap_kiss
    split = cap_split_z(box.pump_trays)
    floor_top = bay_floor_z(box.pump_trays)[1]
    # The fill, both sides of the split. It starts on `pump_relief_floor` — the plane the
    # front wall presents wherever a head noses into it, and the surface the face carries
    # across the whole of both pockets. Under the split it beds on the bay floor's own top,
    # because the piece that comes out of it there is the cap and the cap is what rides
    # that plane; `build_cartridge` takes its own share back to the face's sill reveal.
    solid = solid.fuse(_ybox(dx0, dx1, pump_relief_floor, deck_aft, split,
                             top - face_reveal))
    solid = solid.fuse(_ybox(cx0, cx1, pump_relief_floor, cap_aft, floor_top,
                             split))
    for void in _pump_voids(box.pump_trays, top):
        solid = solid.cut(void)
    for cx, cy, cz in box.pump_trays:
        tray = _tray.build_pump_tray(cy - pump_relief_floor).val()
        solid = solid.fuse(tray.moved(cq.Location(cq.Vector(cx, cy, cz))))
    solid = _tray_webs(solid, inner, box.pump_trays, (), 0.0, 1e4, -1e4, 1e4)
    solid = solid.intersect(
        face.fuse(_ybox(dx0, dx1, outer[2], cap_aft, floor_top, top)))
    if halves_cache is not None:
        halves_cache["cartridge-gross"] = solid
    return solid


def _cap_room(box):
    """Everything under the split AND BEHIND THE FACE — the volume `build_pump_cap` keeps and
    `build_cartridge` gives up.

    THE FACE IS NEVER SPLIT. It is the front of the machine, sill to lintel, and it comes off
    the plate whole on the piece a hand pulls; what parts on `cap_split_z` is the block behind
    it. So this room is cut back by the front wall's own section — the relieved section, so a
    pump pocket's floor is where the cap begins over that pump and the face's own skin stays
    ahead of it."""
    outer, inner = box.outer, box.inner
    room = _ybox(outer[0] - 1.0, outer[1] + 1.0, outer[2] - 1.0, box.y_joint,
                 outer[4] - 1.0, cap_split_z(box.pump_trays))
    wall_solid = _ybox(outer[0] - 1.0, outer[1] + 1.0, outer[2] - 1.0, front_plane_y,
                       outer[4] - 1.0, outer[5] + 1.0)
    for cutter in _front_relief_cuts(inner, box.pump_trays):
        wall_solid = wall_solid.cut(cutter)
    return room.cut(wall_solid)


def _cap_screws(inner, plate, pump_trays):
    """The two screws that draw the cap up onto the block, on the lane's own centreline —
    as (clearance bores, heat-set bores).

    Each crosses one `cap_web_t` of cap and lands in a ruthex M3 heat-set in the block over
    it, so the run is the `screw_len` every other joint on this box takes and the head sits
    in the lane the fill gave up, where a driver reaches it. The heat-set's bore carries the
    thread past the insert, because the screw is longer than web and insert together."""
    split = cap_split_z(pump_trays)
    clear, sets = [], []
    for y in cap_screw_ys(inner, plate):
        clear.append(_zcyl(screw_clear_dia / 2.0, 0.0, y,
                           split - cap_web_t - 1.0, split + 0.1))
        sets.append(_zcyl(heatset_dia / 2.0, 0.0, y, split - 0.1,
                          split + screw_len - cap_web_t + 0.5))
    return clear, sets


def build_pump_cap(box, halves_cache=None):
    """THE PUMP CAP: what closes on both heads and screws up onto the cartridge.

    It is the cartridge's own solid under `cap_split_z` and nothing else — one piece for two
    pumps. WHAT HOLDS A PUMP UP IS THE FOUR WEDGES IT CLOSES INTO THAT HEAD'S FLANKS: the part
    ramps in on each side at each of `pump_case.flank_ramp_bands`, and this piece keeps the
    material under all four of those 45 degree faces, so the load stands on the flanks the
    case that printed this pump held it by. Its top face takes the rest: the stamped bracket
    the part carries in that same plane stands `bracket_w` across against a head of `head_w`,
    so it laps this piece all round the head's void and the two screws hold the seat shut.
    Nothing reaches under a head's front face, which stands one millimetre over the bay
    floor's top.

    IT GIVES UP THE LANE BETWEEN THE PUMPS and keeps `cap_web_t` over it, so the screws are
    short and their heads are reachable. Printed face-down on its own share of the face, the
    same pose the cartridge takes."""
    inner, plate = box.inner, box.collet_plate
    solid = _cartridge_gross(box, halves_cache).intersect(_cap_room(box))
    split = cap_split_z(box.pump_trays)
    bx0, bx1 = cap_band_x(box.pump_trays)
    solid = solid.cut(_ybox(bx0, bx1, front_plane_y, plate["fore_y"],
                            bay_floor_z(box.pump_trays)[1] - 1.0, split - cap_web_t))
    # THE FOUR BARB TUBES CROSS THIS PIECE'S OWN AFT LIP, on their way from the barbs into the
    # anchor tees' collets, so it carries the steel's four holes on the steel's own figure.
    for hx, hz in plate["holes"]:
        solid = solid.cut(_ycyl(plate["hole_d"] / 2.0, hx, hz,
                                plate["fore_y"] - 12.0, plate["aft_y"] + 1.0))
    for bore in _cap_screws(inner, plate, box.pump_trays)[0]:
        solid = solid.cut(bore)
    return _unified(solid)


def build_front_half(box):
    """The whole front column, both pieces still joined at its Z seam."""
    inner, outer, y_joint = box.inner, box.outer, box.y_joint
    shell = _shell_with_facet(inner, outer).val()
    front = shell.intersect(_ybox(outer[0], outer[1], outer[2], y_joint, outer[4], outer[5]))
    # The front wall's reliefs, out of the section before anything stands on it: the
    # refrigeration bay and the pump pockets, each floored on its own stated plane.
    for cutter in _front_relief_cuts(inner, box.pump_trays):
        front = front.cut(cutter)
    front = front.fuse(_front_lip(inner, y_joint))
    # The floor's overlap: the front's aft upper-half floor tongue, lapping the
    # back half's slab within the slab (the core rides the cavity side, so the
    # floor cannot tongue proud like the walls). Lands in the bottom piece.
    front = front.fuse(_floor_lap(inner, y_joint)[0])
    yb = _y_boss(y_joint)
    bosses = _bosses(inner, y_joint)
    # One collar per level, each standing on the lip band the lip has already put
    # down that wall.
    for x_in, x_ext, sx, z_boss in bosses:
        front = front.fuse(_front_socket(x_in, x_ext, sx, z_boss, y_joint, inner))
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
    bosses = _bosses(inner, y_joint)
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
    all the same.

    A boss is a D below its axis, on a 45° web run down the wall — the seam collars'
    own shape (`_front_socket`) at the mount's scale — and the web stops on the boss's
    own tip plane, which is the body's mounting face."""
    for sy, sz, tip in stations:
        if not (y0 <= sy <= y1 and z0 <= sz <= z1):
            continue
        r = mount_boss_dia / 2.0
        # The fill and the web stop one `wall` short of the tip plane: the plane is the
        # body's mounting face, and past it is the body's own back side — solder tails,
        # potting lips — which only the bore's own pad annulus may meet.
        stop = tip + wall
        drop = inner[1] - stop
        solid = solid.fuse(_xcyl(r, sy, sz, tip, inner[1]))
        solid = solid.fuse(_ybox(stop, inner[1], sy - r, sy + r, sz - r, sz))
        solid = solid.fuse(_xz_prism(sy - r, sy + r,
                                     [(inner[1], sz - r), (stop, sz - r),
                                      (inner[1], sz - r - drop)]))
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
    the wall is the datum, so the ports stand at a height the wall states.

    THE ROOF IS TWO TABS, NOT A SOFFIT. The band over the pocket keeps `wago_roof_tab`
    at each end and opens between them: each tab catches the lug's lift and prints as
    its own short bridge, with nothing hanging the pocket's full width.

    A 45° WEDGE CARRIES THE TOWER'S UNDERSIDE to the wall. `clear_z` is the plane the
    flank's air stops being the well's — the crown of whatever the station stands over —
    and a wedge that would cross it is cut off flat there instead."""
    for side, sy, sz, size, clear_z in stations:
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
        zb = sz - half_z
        drop = engage if clear_z is None else min(engage, zb - clear_z)
        if drop > 0.3:
            prof = [(face, zb), (face - side * engage, zb)]
            if drop < engage - 1e-9:
                prof.append((face - side * (engage - drop), zb - drop))
            prof.append((face, zb - drop))
            solid = solid.fuse(_xz_prism(sy - half_y, sy + half_y, prof))
        pk_y = stand_y / 2.0 + wago_well_press
        solid = solid.cut(_ybox(pocket[0], pocket[1],
                                sy - pk_y, sy + pk_y,
                                sz - (stand_z / 2.0 + wago_well_press),
                                sz + (stand_z / 2.0 + wago_well_press)))
        solid = solid.cut(_ybox(pocket[0], pocket[1],
                                sy - pk_y + wago_roof_tab,
                                sy + pk_y - wago_roof_tab,
                                sz + stand_z / 2.0 + wago_well_press,
                                sz + half_z + 1.0))
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
    """The PRV vent's chase on a −X wall PIECE, for the station whose DISCHARGE opens
    through the wall this piece owns.

    One station, `(x, y, z)`: the core's own west flank and the tube's own axis where it comes
    through, in the machine's own frame. A RIB is fused up the wall's inner face OUT TO THAT
    FLANK, and the whole passage is cut back out of it in ONE profile — mouth, roofed duct, open
    groove and run-out ramp are one polygon, one passage, and what changes down it is how much
    of the wall is still standing outboard of it. The mouth is `vent_channel_w` square, on the
    tube's own axis, and its lip is the rib's east face — the face that lands on the core.

    THE DISCHARGE IS THE OWNER. The passage opens through the wall at the ramp's foot, so
    the chase goes on the piece whose band holds that foot — the bottom piece wherever the
    Z seam crosses the chase — and the rib stands proud past that piece's own rim the way
    the lip does, into the cavity the descending top wall closes: above the rim the duct's
    west face is that wall's own inner face, pressed on the rib the way every telescope
    face in this box is, and the groove's through-wall band above the seam stays walled by
    it.

    THE RIB RUNS OUT WITH THE RAMP. It stands behind the channel's floor, so it reaches as far
    down as that floor is still inboard of what the skin alone stands `vent_rib_wall` behind.
    Under that the ramp is cutting skin the wall already had, and the rib ends on the ramp's
    own slope."""
    for sx, sy, sz in stations:
        vent = sz - vent_duct_drop - vent_groove_drop - vent_ramp_rise
        if not (y0 <= sy <= y1 and z0 <= vent <= z1):
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
    which of the two the header ends up in is the card's turn to state and not this slot's.

    THE WALL IT BOTTOMS ON IS THE ONE THAT IS THERE. The card stands as low as a 32 mm card
    stands, which is under a Z seam, and a flank under a seam carries its lip's own wall down
    to the slab — so the datum is `lip_face_x` and not `interior_x`, `2 * wall` of flank and
    not one. `enclosure_assembly.build_mq6` seats the board on the same call."""
    span, _off = _mq6.header_span()
    for sy, sz in stations:
        if not (y0 <= sy <= y1 and z0 <= sz <= z1):
            continue
        cx0, cx1 = lip_face_x()[0], lip_face_x()[0] + mq6_card_x
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
        # The rail roots on the wall surface actually behind the block, which is the front
        # wall's own interior plane where no relief is struck over this station's span.
        root_y = min([front_plane_y] + [f for rx0, rx1, rz0, rz1, f in (fridge_relief,)
                                        if cx0 >= rx0 - 1e-6 and cx1 <= rx1 + 1e-6
                                        and rz0 <= (fz0 + fz1) / 2.0 <= rz1])
        solid = solid.fuse(_ybox(cx0, cx1, root_y, face + cond_slot_grip,
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

    THAT STRAIGHT IS THE GUSSET. It leaves no re-entrant corner for the foot to bend at, and it
    is the bracket's upper face — 25° off vertical, every layer of it laid on the one below.

    THE BEARING FACE HANGS. It is flat and it is the lowest thing on the bracket, so printed
    Z−-down it is a soffit `core_hold_reach + rear_seam_clear` off the wall and it takes print
    support, the way the tap-water trough on this same wall does."""
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

    THE BLOCK'S UNDERSIDE HANGS. Printed Z−-down that face is a horizontal soffit under the
    lane, and it takes print support the way the drip tray's rails do — the V's own two flanks
    stand 30° off vertical and carry themselves. The cavity is one opening from the first tie
    band to the last, and what is left in it draws out end to end.

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
# A PANEL IS A PLATE WALL TO WALL, with one four-socket `valve_seat` SUNK into it per valve on
# the deck it stands under. `valve_panel` states its thickness, its margin and its seat height
# and draws one in its own frame; this turns that onto the deck's own plane and fuses the plate
# into the piece, the way `_asse_cradle` fuses the trough and `_digiten_saddles` the meter's two
# Vs — and then cuts the seats and the ports' channels out of it.
#
# THE PLATE IS THE BOSS. A boss is material round a socket, and a plate one socket and one wall
# thick is that material: a seat sunk into it leaves nothing standing off its face. Which is the
# whole point on this piece — it prints the plate VERTICAL, so a boss on it would be a Ø13.2
# cylinder cantilevered into air with its own underside to bridge, and there are thirty-two of
# them. Sunk, the seat is a blind hole in solid material and the port's channel a notch running
# up the plate's own section: no overhang in the feature and no support in it to pick out.
#
# NOTHING FASTENS A VALVE TO IT. The four corner posts press into their sockets and the valve's
# own round body boss lands on the plate's face, which is what sets its height — the same
# bargain the cold core's cap lid strikes under its own three valves, whose thinner lid stands
# the bosses instead.
def _valve_panels(solid, inner, stations, y0, y1, z0, z1):
    """Every valve panel whose deck falls in the depth and height band this piece owns.

    Each station is `(plane, sign, seats)`: the world Y the deck's valves stand their mounting
    faces on, which way their own +Z runs off it, and one `(x, z)` per valve. The plate's own
    extent is the seats' — wall to wall across, and one `valve_panel.reach` plus a margin either
    way along — so nothing here is a dimension this module chose.

    THE SEATS ARE SUNK AND SO IS THE PORT'S OWN CHANNEL. The plate is a socket and a wall thick
    (`valve_panel.THICK`), which is the material a boss would have been, so nothing is fused onto
    its face: the sockets and the channel are CUT, and the face itself is the plane the valve's
    round body boss lands on. Everything is struck in the valve's own frame at `plane`, its
    mounting plane, and turned onto the deck — the plate's face follows from `SEAT` and is not
    the datum anything here is placed on."""
    for plane, sign, seats in stations:
        zs = [z for _x, z in seats]
        mid_z = (min(zs) + max(zs)) / 2.0
        half = _panel.height() / 2.0
        if not (y0 <= plane <= y1 and z0 <= mid_z <= z1):
            continue
        # The plate: its valve-side face on the plane the valve lands on, its back one `THICK`
        # outboard of that.
        face = plane - sign * _panel.SEAT
        near, far = sorted((face, face - sign * _panel.THICK))
        solid = solid.fuse(_ybox(inner[0], inner[1], near, far, mid_z - half, mid_z + half))
        # THE PLATE'S FOOT: the plate's own whole section carried down to the piece's bed
        # face, its valve-side face one plane with the plate's, so the plate prints as a
        # wall standing on the bed with nothing left hanging. The valves' bottom ports and
        # the runs on them leave through the same channels the plate carries, run on down
        # to the foot's own bed edge. Inset one `wall` to the lip's own face — below the
        # rim that face is the bottom piece's lip, and the foot telescopes down it the way
        # every interior face does. The fore-facing panel's alone: under an aft-facing
        # plate the same band is the fold's own junction field, tees crossing every
        # section of it. The seats' wall-to-wall span stays above the rim
        # (`z-seam-under-deck`).
        foot_z0 = max(z0, inner[4])
        footed = sign < 0 and foot_z0 < mid_z - half - 1e-9
        if footed:
            lx0, lx1 = lip_face_x()
            solid = solid.fuse(_ybox(lx0, lx1, near, far, foot_z0, mid_z - half))
        turn = cq.Location(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0),
                           -90.0 if sign > 0 else 90.0)
        for sx, sz in seats:
            at = cq.Location(cq.Vector(sx, plane, sz))
            solid = solid.cut(_seat.build_sockets().val().moved(turn).moved(at))
            chan = _panel.height() if not footed else max(
                _panel.height(), 2.0 * (sz - foot_z0))
            solid = solid.cut(_panel.build_port_channel(chan + 2.0)
                              .val().moved(turn).moved(at))
    return solid


# --- the flavour manifold's pump trays --------------------------------------
#
# A TRAY IS THE PUMP CASE WITH ITS CYLINDER CUT OFF — `pump_case`'s base plate, its ramp, its
# octagon bore wall and one shoulder of its tower, so it wraps the head's crown AND the boss's.
# `pump_tray` states what that cut adds and draws one in the pump's own frame; `build_cartridge`
# roots it on the cartridge's face and fuses it into that piece.
#
# THE STRAPS ARE WHAT HOLD A PUMP UP. It hangs under its tray, so two close round it and the
# tray together through the plate's four channels, reaching under the bracket the part carries at
# that crown — the meter's bargain, on the heaviest body either wall carries.
#
# A TRAY IS A CANTILEVER OFF THE CARTRIDGE'S FACE AND NOTHING ELSE, and one web between the two
# trays and the across-runs to the deck's own edges are what it meets. Each is the trays' own
# plate — `pump_tray.PLATE` thick, in that plate's own band — so the storey comes out one plate,
# and its edge strips ride the bay's rails. The webs to the side walls and the aft web onto a
# panel are not drawn: the rails carry the deck instead, and its aft edge stops short of the
# collet plate, and the cap's own aft face one storey down is what lands on the steel.
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

    Printed Z−-down the rib HANGS OFF THE TOP WALL and starts on its two lips — one
    `digiten_saddle_wall` strip either side of the bore, the saddle's whole length, with nothing
    under them. Everything over those lips is the arc closing inward on itself, so the hood
    carries its own crown and the lips are the only thing in it support has to reach."""
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
    its seam (`box.splits` — the one stated plane, both columns), the bottom
    taking the Z lip + socket collars, the top taking the pins + X-axis screw
    bores. The Y-seam bosses' under-seam level sits under that plane, so it
    lands in — and pins — the two bottom pieces; the over-rim level the two
    tops."""
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
        # And the wall that carries that lip down to the slab, so the lip stands on a wall
        # and not in air. Fused here with the lip and before every pocket, so a
        # well or a groove cut into this flank later is cut out of the whole `2 * wall` of it.
        piece = piece.fuse(_lip_underwall(inner, y_joint, zj).intersect(col))
        if y_side == "front" and box.pump_bay:
            # The front flat's share of both skins goes to the bay's floor and the heads
            # that pass through its berth; the sill and its drain are front-top's.
            piece = piece.cut(_front_flat_lip_drop(inner, zj))
            # And both flanks over the same run, round the corners to the tee wall's aft
            # face — the boss's own plinth is all that still crosses the seam there.
            piece = piece.cut(_flank_lip_drop(inner, box.collet_plate, y_joint, zj))
        for x_in, x_ext, sx, ys, _c in stations:
            piece = piece.fuse(_z_pod(x_in, x_ext, sx, ys, inner, zj))
        for x_in, x_ext, sx, ys, _c in stations:
            piece = piece.cut(_z_pod_cuts(x_in, x_ext, sx, ys, zj))
        for x_in, sx in ((inner[0], +1.0), (inner[1], -1.0)):
            x_ext = x_in - sx * wall
            if y_side == "front":
                # The four-corner socket: front-bottom's alone, proud through the plane.
                piece = piece.fuse(_corner_socket(x_in, x_ext, sx))
                piece = piece.cut(_corner_cuts(x_in, x_ext, sx))
            else:
                # The back-bottom half of the four-corner pin, flat on the plane.
                piece = piece.fuse(_corner_plug(x_ext, sx, oz0 - 1.0, zj))
            piece = piece.cut(_screw_cut(x_ext, sx, z_seam, _y_boss(y_joint),
                                         corner_screw_len))
    else:
        piece = solid.intersect(_ybox(ox0 - 1.0, ox1 + 1.0, oy0 - 1.0, oy1 + 1.0,
                                      zj, oz1 + 1.0))
        for _x_in, x_ext, sx, ys, _c in stations:
            piece = piece.fuse(_z_pin(x_ext, sx, ys, zj))
        for _x_in, x_ext, sx, ys, _c in stations:
            piece = piece.cut(_screw_cut(x_ext, sx, _z_pin_z(zj), ys))
        for x_in, sx in ((inner[0], +1.0), (inner[1], -1.0)):
            x_ext = x_in - sx * wall
            if y_side == "front":
                # The corner's slide channel through front-top's half of the lip.
                piece = piece.cut(_corner_cuts(x_in, x_ext, sx))
            else:
                # The back-top half of the four-corner pin, flat-face on its own mouth.
                piece = piece.fuse(_corner_plug(x_ext, sx, zj, oz1 + 1.0))
            piece = piece.cut(_screw_cut(x_ext, sx, z_seam, _y_boss(y_joint),
                                         corner_screw_len))
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
    # The wall the anchor tees stand in, behind the collet plate — BEFORE the panels, because
    # a panel's seats are cut out of whatever stands on that plane and this stands on it.
    if y_side == "front" and z_side == "top" and box.pump_bay and box.collet_plate:
        piece = piece.fuse(_tee_wall(inner, y_joint, box.collet_plate, box.pump_bay))
        # And the rib that stands on that wall's crown, carrying the ridge the display's
        # through-hole leaves across the housing's back. With the wall, because it stands on
        # it — and after the facet's own cuts, which the half took before it was split.
        piece = piece.fuse(_ridge_wall(inner, outer, box.collet_plate, box.pump_bay))
    piece = _valve_panels(piece, inner, box.valve_panels, ylo, yhi, zlo, zhi)
    # The pump trays are the cartridge's (`build_cartridge`); what this piece carries for
    # them is the bay's own furniture — the floor across the front and the seat the collet
    # plate drops into — and then the opening itself, cut last of the wall's work.
    if y_side == "front" and z_side == "top" and box.pump_bay and box.collet_plate:
        tray_z = min(cz for _cx, _cy, cz in box.pump_trays)
        piece = piece.fuse(_bay_floor(inner, y_joint, box.collet_plate, box.pump_trays))
    # And the runs' own anchors, on whichever face each one stands nearest. Last, for the same
    # reason the trough is: every one of these is a rib with a cavity cut through it.
    piece = _tube_anchors(piece, inner, box.tube_anchors, ylo, yhi, zlo, zhi)
    # And the flat ceiling's two strips over the hopper opening's flanks, on the front
    # top alone — the piece whose ceiling is nothing but those strips.
    if y_side == "front" and z_side == "top" and box.funnel:
        piece = _ceiling_corbels(piece, inner, outer, box.funnel, y_joint)
    # The bay's opening, after every fuse that stands near it: what leaves through it is
    # the cartridge, and what it takes from this piece is what `build_cartridge` keeps.
    if y_side == "front" and z_side == "top" and box.pump_bay:
        # The seam's ceiling first: the opening's floor is this slab's top, so it has to be
        # standing before the opening is cut or the cut would take the plane it stands on.
        piece = piece.fuse(_rim_cap(inner, outer, box.collet_plate, z_seam))
        piece = piece.cut(_bay_cut(inner, outer, box.pump_bay, box.pump_trays,
                                   box.collet_plate))
        # And the sill it leaves — the floor's own top — washed fore, so what runs down the
        # face and gets past the reveal runs back out the front.
        piece = piece.cut(_sill_wash(inner, outer, bay_floor_z(box.pump_trays)[1]))
    # And then the columns give up whatever the pack stands in them (`_column_relief`), which is
    # last of everything: a relief is air, and air a later step fuses back in is not a relief.
    # Clipped to the pillar — the column AND the lip's skin wrapping it (`_column_pillar`) —
    # so what a pocket can ever take is that and never the wall behind it or the boss beside it.
    for sx, sy, _name, room in box.column_reliefs:
        pillar = _column_pillar(inner, sx, sy, box.splits[0] if sy < 0 else box.splits[1])
        piece = piece.cut(_ybox(*room).intersect(pillar))
    return _unified(piece)


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
    bosses = _bosses(box.inner, box.y_joint)
    for sx, label in ((+1.0, "−X"), (-1.0, "+X")):
        zs = sorted(z for _xi, _xe, s, z in bosses if s == sx)
        print(f"  Y-seam levels {label} wall: {len(zs)} — "
              + ", ".join(f"{z:.0f}" for z in zs))


def build_pieces(box):
    """The printable pieces of one box — the four quadrants and, when the pack stands
    pumps, the cartridge that slides out of the front pair — and the assembly of them in
    place with the seams intact.

    DRAWING A PIECE TAKES NO READING. Every bound the box states is in the ledger before this
    runs — `_dims` states its own as it sizes the shells, `with_funnel` states the throat's as
    it seats the centre — so the four pieces are a pure function of the Box and a piece handed
    back unbuilt is a piece nothing on the card was waiting for. That is what lets `_realized`
    keep them: a build that moves a body inside the walls moves neither the box, which is its
    stated size, nor the code that cuts it, and a station moves only when the body carrying it
    does."""
    cache = {}

    def _product(n):
        if n == "pump-cartridge":
            return build_cartridge(box, halves_cache=cache)
        if n == "pump-cap":
            return build_pump_cap(box, halves_cache=cache)
        return build_piece(box, *n.split("-"), halves_cache=cache)

    names = [n for n in PIECE_COLORS
             if n not in ("pump-cartridge", "pump-cap")
             or (box.pump_bay and box.collet_plate)]
    pieces = {name: _realized.realized(
                  _realized.key(__name__, box, name),
                  lambda n=name: _product(n))
              for name in names}
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
              ", ".join(f"{n} (z {r[4]:.1f}..{r[5]:.1f})" for n, r in gave))


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
        "COLUMN_ARC": f"{column_round:.3g} mm",
        # What a hand gets on a flank: the return's own section and the lane the box keeps
        # open behind it, off the exterior side face.
        "COLUMN_ALONG": f"{_column_along():.3g} mm",
        "COLUMN_DEPTH": f"{_column_depth():.3g} mm",
        "APPLIANCE_HEIGHT": f"{appliance_height:.4g} mm",
        # The Y-seam ladder as the walls came out — per wall, and one figure when they agree.
        "Y_LEVELS": "/".join(str(c) for c in sorted({
            sum(1 for _xi, _xe, s, _z in _bosses(box.inner, box.y_joint)
                if s == sx) for sx in (+1.0, -1.0)})),
        "PLUG_DIA": f"{plug_dia:.4g} mm",
        "RIDGE_WALL_T": f"{ridge_wall_t:.4g} mm",
        "RIDGE_LEN": f"{display_pcb_x:.4g} mm",
        "CABLE_BORE": f"{cable_sleeve_open:.4g} mm",
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
    # THIS FILE, UNDER THE NAME EVERYTHING ELSE IMPORTS IT BY — the same line
    # `enclosure_assembly` carries for itself, and for the same reason. Run as a script this
    # is `__main__`, so `machine_of`'s `enclosure_assembly` does `import enclosure` and gets a
    # SECOND copy: `_dims` fills that one's module state and `main()` builds the pieces out of
    # this one's. `_wall_block` survives that because a missing key reads as "nothing known in
    # the way"; `_z_seam_passes` did not — `main()` reads it with `.get`, so the empty copy
    # answered None for every seam and the run printed the back one as landing "in an open
    # band" when it runs through its column, which is what the README beside this file has
    # said all along. A record that degrades quietly is the exception here and not the rule,
    # and a REPORT that degrades quietly is what a person reads to decide the box is sound.
    # One name, one module, one box.
    sys.modules.setdefault(__name__ if __name__ != "__main__" else "enclosure", sys.modules[__name__])
    main()
