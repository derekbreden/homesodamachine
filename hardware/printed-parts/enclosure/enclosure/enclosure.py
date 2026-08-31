"""Thin Edition enclosure — a tall, narrow PETG box, split into four printable
pieces (front/back × bottom/top) that telescope and cross-pin together.

WIDTH, HEIGHT and DEPTH are all BOUNDS, not consequences — `appliance_width` struck
symmetric about x = 0, `appliance_height` from the floor slab's underside to the top
wall's outer face, and `rear_plane_y` from the front wall to the back. The contents do
not set them; they have to fit inside, and `_dims` measures every one of them against
the pack and enters the reading in `BOUNDS`. The box comes out at its stated size
either way, so a pack that overran it gets a wall drawn through it.

Three bodies stand on the floor slab — the compressor and the condenser side by side
across the front, and the cold core behind them. A boss is a block `2 * socket_r` across
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
    the front pieces' aft walls telescope (a full-wall lip,
    nothing shaved) into the back pieces — a proud tongue on the side walls and
    ceiling, and on the floor, where the cold core rides the cavity side and a
    proud tongue cannot, a full-thickness tongue with a 45° scarf nose
    (`_floor_scarf`), so every seam laps and none butts — and FOUR screw
    bosses cross the seam, the box's only screws: one per ±X side wall per
    level, the bottom pair standing just over the floor (so it pins the two
    bottom pieces), the top pair under the ceiling. Each boss is on an X axis:
    the screw drives in from the left/right EXTERIOR face. The BACK piece
    carries the PLUG (faucet mounting-plate idiom): a square prism reaching
    inward from the wall with a screw clearance through it. The FRONT piece's
    lip carries the SOCKET (faucet shell-bottom idiom): a collar slotted to
    receive the plug, open on its +Y face so the plug drops in as the pieces
    close, with a ruthex M3 heat-set at the deep end.
  * A bottom↔top split per column that SLIDES HOME and takes no screw, at ONE
    stated height both sides of the Y seam (`z_seam`, one level line round the
    box). The BOTTOM pieces carry the lip — a 3-sided band, their outer ±Y
    wall + both side walls, stopping short of the Y-seam overlap — with a
    HOOKED RAIL on each flank's straight run: an ARM standing on the mouth
    whose HEAD steps outboard over the groove (`_z_rail_heads`). The TOP
    pieces run their wall to the mouth at full section — the FOOT — with a
    notch above it that swallows that head (`_z_rail_feet`,
    `_z_rail_channels`). THE TWO COLUMNS ARE MIRRORED: front-top enters fore of
    home and slides AFT over the front wall's own plane, back-top enters aft of
    home and slides FORE over the rear wall's — each to the stop block closing
    its own far end; the end walls and corner turns close head-on behind it, the
    same telescoping mate the Y seam makes, arrived at along Y. Lifting a seated
    top lands each foot's flat top on its head's flat underside down both whole
    runs. A top comes off the way it went on, toward the end of the box it
    stands at — front-top forward into open air, back-top aft — so neither is
    lifted over the other and neither asks the box to come out from under
    whatever it is built under. Front-top is held by the upper pair of Y-seam
    screws alone, so two screws draw it off the front. A WALL THAT
    LIP STANDS ON IS `2 * wall` THICK, floor slab to lip rim
    (`_lip_underwall`): the lip is a skin standing proud of the interior
    face, and a skin that began at the seam would land its underside in air —
    a soffit round three sides of a piece that prints floor-down. Carried to
    the slab it is a wall instead, and there is nothing in a bottom piece for
    the bed to bridge.

The walls stand off the bodies rather than on them — one boss chain at the ±X
walls, one wall at the back — because a body on the floor spans the interior wall
to wall, so a wall on its face would leave the seam machinery nowhere to stand.
The cold core seats flush against the seams instead, and stands flat on the floor slab — its bottom cap's lid is a plane and
every cap screw is down in a counterbore, so nothing goes under it. The ±X bands'
own seam furniture fences it sideways, the back Z seam's lip behind, and the floor's
two core lugs (`_core_fence`) ahead. The floor that core stands on is flat: the
Y seam's floor tongue stays within the slab, with a 45° scarf nose rather than a
feature standing proud of its cavity-side face.

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
it meets a column the way it meets a wall: a mount inside the footprint is the
column's material with only its bore left. At a front corner the rail channel's
deep lane passes through the pillar's flank side on its way to the stop, the one
mark the slide leaves on one.

A plug is the wall it drives through and the reach it needs past it: the first
`wall` of its length is that wall's own material and the rest a stub off it, its
mouth-side face on the mouth that receives it. A socket is a block round that plug —
one `wall` of material, a `socket_cap` over the insert's blind end — its rim-side
face on the lip rim and its far face a hair under the seam mouth, so it stands on
that band — lip above the mouth, wall under it below — down its whole length. Those are the two matings the
overlap depth is struck from. Between two levels the corner is the wall's own air.
A level stands where its socket has a body to be bored into (`_level_clear`).

A Z seam is held shut along its whole run rather than pinned at its ends: the
rails' hooks bear over every millimetre both flanks carry, and the stop
blocks and end walls close the travel. The Y seam is pinned at a level for each
end of each piece — the floor level closes the two bottoms, the ceiling level
the two tops — and those four screws are also the slides' lock, each column's
top standing in the way of the other's way out. Levels are searched per side
wall against what stands against it, so the two walls need not carry the same
ones; main() prints what each ended up with.

main() exports the four printable pieces (enclosure-front-bottom.step,
enclosure-front-top.step, enclosure-back-bottom.step, enclosure-back-top.step)
plus enclosure.step — the four as separate solids in assembled position,
seams intact (mirrors `faucet_shell.py`). All five come through the same
code from a `Box`.
"""

import functools
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
sys.path.insert(0, str(_repo / "hardware" / "printed-parts" / "cadlib"))
sys.path.insert(0, str(_repo / "hardware" / "printed-parts" / "zone-c" / "funnel"))
sys.path.insert(0, str(_repo / "hardware" / "reference" / "wago-221"))
sys.path.insert(0, str(_repo / "hardware" / "reference" / "mq6-gas-sensor"))
sys.path.insert(0, str(_repo / "hardware" / "reference" / "riteav-keystone"))
sys.path.insert(0, str(_repo / "hardware" / "reference" / "iec-c14-inlet"))
sys.path.insert(0, str(_repo / "hardware" / "printed-parts" / "valve-seat"))
sys.path.insert(0, str(_repo / "hardware" / "printed-parts" / "enclosure" / "valve-tray"))
sys.path.insert(0, str(_repo / "hardware" / "printed-parts" / "enclosure" / "ceiling-panel"))
sys.path.insert(0, str(_repo / "hardware" / "printed-parts" / "enclosure" / "pump-tray"))
from _cadq_export import export_assembly
from _materials import WALL_COLORS as PIECE_COLORS, one_body
from docgen import substitute_md, substitute_py_comments
import _boxes
import _realized
import fits
import reeding
import trimesh
import flute_skin as _flute_skin
import funnel as _funnel
import wago_221 as _wago
import mq6_gas_sensor as _mq6
import riteav_keystone as _keystone
import iec_c14_inlet as _c14
import valve_seat as _seat
import valve_tray as _valve_tray
import pump_tray as _tray
import _enclosure_interface as _interface

# Shell parameters.
wall = _interface.wall      # PETG wall thickness
pump_pull_wall = _interface.pump_pull_wall
pump_cartridge_proud = _interface.pump_cartridge_proud
# THE FLOOR SLAB IS NOT A WALL AND IS NOT ONE WALL THICK. It is the face the machine's whole
# mass stands on, the face a body bolted DOWN rather than hung on a flank is anchored to
# (`_floor_bosses`), and the one face of the box that prints flat on the bed — where section
# is filament and nothing else: no bridge, no support, no standing wall to warp.
# `appliance_height` is struck to its UNDERSIDE and the cavity keeps its own floor plane at
# the pack's z = 0, so the slab stands in the silhouette: the machine is `floor_t`, the
# cavity, and one `wall` of top.
floor_t = 6.0
# The +Y wall stands one wall off the rearmost content — the cold core, the
# only thing near the back — so the core seats flush against the rear Z-seam
# lip's inner face rather than against the wall the lip hangs off. A body mounted
# on the +Y wall seats on this same plane.
rear_seam_clear = _interface.rear_seam_clear
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
# material and keeps only its bore.
column_round = corner_round
# The corners that carry one, as the (x, y) signs of the interior corner each stands in.
column_corners = ((-1, -1), (1, -1), (-1, 1), (1, 1))

# --- the reeded skin --------------------------------------------------------
#
# THE FOUR STANDING WALLS ARE FLUTED, and it is ONE field, not four. Half-round grooves are
# struck by ARC LENGTH round the whole outer plan from a datum on the front wall's centreline,
# and arc length is what makes them one field: it does not know where a face ends, so a flute
# crosses `corner_round`'s quarter turn at exactly the spacing it keeps on the flat, and the
# four pieces cut their own z bands out of the same plan — which is why the grooves register
# across the Z seam without either piece being told the other exists.
#
# THE PROFILE IS `reeding.groove`, shared with the corner coupon at `c14bb2fff`. That coupon is the box's
# own corner at the box's own `wall` and `corner_round`, so what printed there is what prints
# here, and neither can drift from the other while they read one function.
#
# THE FIELD CLOSES ON ITSELF. `flute_count` is a whole number of grooves round the whole
# perimeter, so no station restarts the array and no two arrays meet anywhere — but which
# whole number is not free, because the pitch is what it lands on and WHERE THE FIELD LANDS
# DECIDES WHAT THE BOX'S OWN LINES ARE MADE OF. Two bounds spend it:
#
#   `flute-closes`       the pitch stays within a hair of the coupon's
#   `flute-hides-seam`   the Y seam — the one straight line running the full height of both
#                        side walls — falls in a groove's own shadow rather than on a land
#
# AND THE FIELD IS SYMMETRIC IN X, because the datum is a groove centre on x = 0, the plane
# the whole machine is struck about. Whatever `flute_count` is, the half-perimeter carries
# the same grooves the other way round.
#
# AND THE BOX HAS A SECOND FIELD, INDOORS. The bay's storey shows two mouth ledges, and those
# two actual surfaces are two open rails. `_bay_storey_segments` carries their one global phase
# path across the intervening open flanks and hidden tee span, which are never cutter paths.
# Both are struck at THIS pitch from a datum on the same x = 0, so their phase remains the
# machine's phase inside as it is outside. `flute_rails` is where the box says which runs it
# has, and `flute_skin.py` reads nothing else about either of them.
flute_count = 260
# THE DEPTH IS THE COUPON'S. the corner coupon at `c14bb2fff` cut this into a `wall`-thick standing wall
# and printed it; going deeper is a new question, not a free one.
flute_depth = _interface.flute_depth
# THE SOLID A FLUTE MUST HAVE BEHIND IT — the whole `wall`, not what is left after something
# else has taken its share. A groove cut where less than this stands behind it telegraphs
# through to the show face; the coupon proved it on the 0.6 mm its engraved label took out of
# the far side, which read on the outside as a mark you could find. So nothing may relieve
# into the outermost `flute_backing` of a fluted face, and `flute-backed` reads every stated
# section on those faces against it.
flute_backing = wall
# How many stations the groove's own curve is drawn through, half-width to half-width. The
# spline through them measures 1.1986 of the stated 1.2 at its deepest, which is a hundredth
# of the 0.42 mm the nozzle draws.
flute_samples = 13
# THE FIELD STOPS SHORT OF AN EDGE, and this is how far short — the corner coupon at `c14bb2fff`'s own
# `texture_rise`, ramped on the same smoothstep, so the box stops its flutes the way the
# coupon stopped its. WHICH edges is not a list: `flute_skin.py` measures, over the whole
# surface at once, how far every station stands from the nearest place the show face ends,
# and ramps on that. A seam, an opening's rim, a pocket's edge and the facet's own diagonal
# arris are the same fact to it, which is why none of them is named anywhere.
flute_rise = _interface.flute_rise
# WHAT A BAND GETS FOR BEING AS TALL AS IT IS. A band's own two faces are both edges of the show
# face, so its deepest station stands half the height from one and reaches `flute_depth` only
# once that clears `flute_rise`. The pieces let into the box's faces read these to say which side
# of that they fall on — `display_cover.display-cover-reveal`, `ceiling_panel.ceiling-panel-reveal`.
flute_full_depth_height = _interface.flute_full_depth_height
flute_reach = _interface.flute_reach
# Stations the ramp is drawn through, and the loft between them is RULED — a straight taper
# from each station to the next, which is the only kind of loft a 2 * `flute_count`-edge
# section survives being booleaned against afterwards. So the smoothstep is a polyline, and
# what matters is how far that polyline departs from the curve: at `flute_depth` over
# `flute_rise` the worst gap is about 0.9 / steps^2 mm, which at four steps is 56 microns and
# reads across a room as bands. Twelve is 6 microns — a seventieth of the bead the wall is
# drawn with — and the kink between two facets is 6.8°, against the 60° the groove's own arc
# turns through. Past that the sections cost more than anything they buy: the skin is
# 2 * `flute_count` edges and every station is that many ruled faces again.
flute_fade_steps = 12
# How far the pitch `flute_count` lands on may sit from the coupon's, and how far off a
# groove's centre the Y seam may fall. Both are what picks one count out of the several that
# close near 5 mm; `flute-closes` and `flute-hides-seam` are where they are read.
flute_pitch_drift = 0.15
flute_seam_miss = 0.5


def flute_backed_sections():
    """Every stated section a FLUTED face stands on, as (what, mm) — what a groove is cut into,
    read by `flute-backed` against `flute_backing`.

    A SURVEY IS NOT A GATE. Every one of these was measured on the built solids, by ray sweep
    and again by boolean, and measuring is also what found the three the file did not state:
    the front face under the display facet's arris, the east bosses' bores where the corner
    round carries the surface inboard, and a port pocket running off that same tangent. The
    first two became figures of their own — `facet-arris-backed` and `east_boss_bore_end` —
    because they are computed rather than typed. This is the rest, stated so that a section
    thinned in the file goes red here instead of on the next print."""
    return (
        ("a top piece's seam lane, where the mating head laps its inner face", wall),
        ("front-top's own ±X flank", front_top_flank_t),
        ("back-top's own ±X flank", back_top_flank_t),
        ("back-top's own +Y wall", back_top_wall_t),
        ("a bottom piece's lipped side, the lip's skin carried to the slab", 2.0 * wall),
        ("the front wall", front_wall),
        ("the +Y wall inside a stated relief", wall),
        ("behind a Wago well, which bottoms on `interior_x`", wall),
        ("front-top's collet-plate lift lane", wall),
        ("the pump cartridge's lower face over its relief floor",
         pump_relief_floor - pump_cartridge_front_y),
        ("the front face under the display facet's arris",
         display_facet_buffer * math.sqrt(2.0)),
        # AND THE MULLION THE CONDENSER'S VENTS LEAVE, which is the one row here a SLOT sets
        # rather than a wall does. The jamb stands `reeding.pierce_width / 2` off the groove's
        # own centre, out on the half-ellipse where the groove is shallower than at its floor —
        # so a WIDER slot thickens this and only ever thins the mullion (`enclosure_assembly.check_flank_vents`).
        # The depth at an offset is the profile's and not the pitch's, every offset here being
        # well inside one groove, so this reads the same whatever `flute_count` lands on.
        ("the flank behind a vent slot's jamb",
         2.0 * wall - flute_depth * float(reeding.groove(reeding.pierce_width / 2.0))),
    )

# H2C left-nozzle build envelope; each printed HALF must fit inside this.
H2C_X, H2C_Y, H2C_Z = 325.0, 320.0, 320.0

# Display-mounting facet — a flat 45° SOLID surface chamfered into the top-front
# arris for the Waveshare ESP32-S3-Touch-LCD-4.3B enclosure display
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
# [158 mm](DISPLAY_FACET_X) × [87.5 mm](DISPLAY_FACET_SLOPE) up the slope — which is
# what `_report_facet` prints beside the measured face.
display_bezel_x = _interface.display_bezel_x           # bezel glass, lateral (X)
display_bezel_slope = _interface.display_bezel_slope   # bezel glass, up the slope
# The glass is the datum (centered on the facet); the PCB body sits offset behind
# it because the glass overhangs the body unevenly (up-and-left). This is the
# body's own offset from the centered glass.
display_body_offset_x = 0.5      # PCB body offset from the centered glass, lateral (+X)
display_body_offset_slope = -1.0 # PCB body offset, down-slope
display_corner_r = _interface.display_corner_r         # corner rounding, matching the display bezel
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
display_inset_lap = _interface.display_inset_lap       # the plate's lap over the glass, and the inset's land past it
display_inset_reach = _interface.display_inset_reach   # how far the inset runs past the glass laterally — the land
                                 # the two cover screws stand in, since a countersunk M3 head
                                 # is wider than the border it would otherwise sit in
display_inset_depth = _interface.display_inset_depth   # inset floor, down from the 45° face — the plate's seat
display_inset_x = _interface.display_inset_x                       # [153.5 mm](DISPLAY_INSET_X)
display_inset_slope = _interface.display_inset_slope               # [83 mm](DISPLAY_INSET_SLOPE)
# Every millimetre of plain face down the slope carries the facet √2 further aft along Y, and
# with it the seats let into it — which is what `display-housing-seats` reads the housing's
# own back cut against.
# The plain 45° face kept outside the inset, all around — and WHAT SETS IT is not how wide a
# border looks right. The inset is sunk normal to the facet, so its own down-slope END WALL is
# a 45° plane the other way, and where that plane and the front wall's arris come together is
# the thinnest the front face ever gets. Work it out and the ligament there is exactly this
# buffer times root two, wherever the facet stands and however big it is — so the border's
# width IS the wall behind the top of the front face. Under `flute_backing` a flute cut into
# that face has less than one `wall` behind it and telegraphs; `facet-arris-backed` reads it.
display_facet_buffer = 2.25      # >= flute_backing / sqrt(2)
display_facet_x = display_inset_x + 2 * display_facet_buffer          # [158 mm](DISPLAY_FACET_X)
display_facet_slope = display_inset_slope + 2 * display_facet_buffer  # [87.5 mm](DISPLAY_FACET_SLOPE)
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
display_bezel_depth = _interface.display_bezel_depth   # bezel counterbore depth, user face
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
# enclosure display's own run — four 22 AWG in the 1/2" PET expandable braid `ledger/bom.md` §11
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
# THE COVER IS TWO SECTIONS, and which one it carries is decided by what is under it. Over the
# glass it is `display_cover_thickness`, because what stands in the step there is the gasket;
# everywhere else it is `display_cover_seat`, a whole screw seat, and the inset is sunk to that
# over the same ground. So no pad stands off the plate's back and its own back is one plane
# either side of the bezel's outline — see `_display_cuts` and `display_cover.py`.
display_cover_thickness = _interface.display_cover_thickness  # the plate WHERE IT LAPS THE GLASS; = display_inset_depth, so
                                 # the plate's top lies in the face
display_cover_slip = _interface.display_cover_slip        # per side, plate edge into the inset it drops in
display_cover_head_h = _interface.display_cover_head_h    # DIN 912 M3 head, nominal
display_cover_seat_recess = _interface.display_cover_seat_recess  # how far under the 45° face the head lands
display_cover_cbore_depth = _interface.display_cover_cbore_depth
# The head's own counterbore and the lap's section under it — the plate everywhere the glass is
# not beneath it, and the depth the inset's land is sunk to.
display_cover_seat = _interface.display_cover_seat
# Each screw stands in the middle of the lateral land, halfway between the glass's edge and
# the inset's own — the widest material either has.
display_screw_x = _interface.display_screw_x                         # [66.75 mm](DISPLAY_SCREW_X)

# Funnel opening (Zone C) — one rectangular opening through the top wall
# BEHIND the display facet, cut at the placed funnel's collar: the funnel is a
# static part (../../zone-c/funnel/, its own frame) placed at
# the box's own `funnel` centre with its brim on the box top, and with_funnel
# measures the top-wall frame against it (the housing's back cut ahead, the
# ±X boss chains either side, the +Y wall of back-top behind). The collar stands on
# `funnel_front_y` and reaches aft for its capacity, so it may CROSS the Y
# seam — both halves take their share of the cut.
# Air between the funnel's collar frame and the ±X boss chains it runs beside. CHOSEN, not
# derived: the two are printed in the same piece, so this is clearance for the eye and the
# deburring tool rather than a fit.
funnel_chain_gap = 1.0
# The collar's front edge, read by `enclosure_assembly.funnel_centre`. THE FUNNEL IS WHERE THE
# USER POURS, so it stands as far forward as the top wall lets it — and what stops it is the
# BRIM rather than the throat: the flange overhangs the collar by `funnel.brim_overhang`
# and has to land on top wall, which begins at the display facet's own arris. So the figure is
# that arris, one `wall` of landing, and the overhang — 66.87 + 3 + 7 — and it stands aft of
# `housing_back_y`, which is the other plane that could have stopped it. `funnel-brim-lands`
# reads it back against the facet the box actually cuts, which is what catches it when the
# facet's own size moves.
funnel_front_y = 77.0
# The top wall between the display housing's back plane and the throat, read on
# `funnel-collar-frame`. The brim's overhang lands on the housing slab at zero.
funnel_front_ledge = 0.0

# Split + boss parameters — every dimension sized to its function, nothing
# inherited from the faucet. The seam is a Y plane; the front half's full-wall
# rear lip telescopes into the back; four corner bosses cross-pin the seam with
# M3 screws from the ±X exterior. Each boss is a round pin registering in the
# front socket bore, meeting the back half's own corner web along its whole +Y
# side. The screw spans the head seat to the front heat-set, so the pin body is
# screw_len − heatset_depth long.
split_slip = 2.0 * fits.slip # diametral slide fit, plug into socket bore
# What a 45 degree lap gives up along the axis it is driven home on, so the two raked faces
# stand one `fits.slip` apart where they pass.
scarf_axial = fits.slip * math.sqrt(2.0)
screw_clear_dia = _interface.screw_clear_dia  # M3 shank clearance
head_cbore_dia = _interface.head_cbore_dia    # M3 SHCS head counterbore
head_cbore_depth = 4.0       # head recess depth from the ±X exterior (the head seat)
screw_len = 10.0             # M3 SHCS under-head length (M3x10), head seat → heat-set
plug_dia = screw_clear_dia + 2.0 * wall          # 9.9 — the shank + one wall each side
socket_bore_dia = plug_dia + split_slip          # 10.2 — slide fit over the plug
socket_r = socket_bore_dia / 2.0 + wall          # pod half-size: one wall around the bore
heatset_dia = _interface.heatset_dia  # ruthex M3 short heat-set
heatset_len = 4.0            # ruthex RX-M3Sx4.0 brass body, set flush at its opening
heatset_depth = _interface.heatset_depth
socket_cap = wall            # one wall capping the insert's deep end
# HOW FAR THE PIN'S OWN FACE STANDS OFF THE END WALL IT PINS UNDER. A full-width 45-degree
# corbel carries each back plug's underside from its wall to its inboard tip, and the front
# slide channel gives up the same profile one `fits.slip` lower. The pin therefore keeps its
# square registration faces and the two pieces keep their full insertion travel without a
# support contact in this slot.
#
# BOTH ENDS FENCE IT AND IT IS ONE FIGURE, so one reach clears all four bosses. Walked nearer
# its own end wall, the lower collar's carve (`_y_lip_channel`) leaves a corner of the front lip
# standing in the back half's register and the two bottom pieces stop being a slip fit — 0.5 mm3
# of contact at 13, 3.3 at 12, 10.4 at 11, which `_report_split` reads on every build. Walked
# further from it, the upper collar's own 45° underside comes down the −X wall into `fluid-1`'s
# lane — 1.16 mm of air at 13, 0.47 at 14, against the assembly's one-millimetre clearance
# floor. Thirteen is the height between the two.
boss_end_clear = 13.0
# The ±X walls' own mounting bosses — what a body hung on a side wall is fastened by. Each
# stands off the wall's INNER face and reaches inboard to the body's own mounting plane,
# bored for a ruthex M3 short from that end; the screw comes the other way, in through the
# body from the room, so nothing is driven from outside the machine.
#
# The section is the one `printed-parts/electronics/module_tray` gives every M3 board boss in
# this machine: these land on a board's own hole pattern, between its pin fields, and a boss
# that carried a whole wall around its insert would foul them.
mount_boss_dia = _interface.mount_boss_dia
# What that section keeps round its insert, which is the material any boss in this machine
# stands a heat-set in.
boss_ligament = _interface.boss_ligament
# Assembly air between a power-column body's exact envelope and a corbel that has to begin
# behind it. Most corbels reach their mounting face; this is spent only where the body itself
# crosses the otherwise printable 45 degree wedge.
east_boss_corbel_clear = 1.0
# Air past the screw tip at the bore's blind end, so a screw longer than the insert has
# somewhere to go rather than bottoming on printed material.
mount_bore_relief = _interface.mount_bore_relief

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
# catches the lug's lift and prints as its own short bridge. What opens BETWEEN them is
# roofed on ONE 45 degree plane folded on the wall: the opening runs past the tower's
# own crown into whatever stands over it, and squared off there it would lay that
# thing's underside on air across the opening's full width.
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

# --- the −X strip's MQ-6 cradle ---------------------------------------------
#
# The combustible-gas sensor lies ALONG the open strip down the −X flank, low in the
# refrigeration bay beside the compressor. R-600a is half again heavier than air: it falls
# off whichever brazed joint let it go and spreads as one layer over the slab, so what the
# sensor owes that layer is HEIGHT, and the floor of this bay is one connected pool — every
# leak site the loop has feeds it. Laid along the strip the card sits as low as a 20 mm card
# stands, which is as low as this board goes.
#
# The card carries no mounting hole, so what holds it is a SLOT ITS OWN EDGES SLIDE INTO —
# the same bargain the Wago wells strike, for the same reason. TWO POSTS STAND ON THE SLAB,
# one at each end of the card's long run, grooved on the faces they turn toward each other,
# and the card DROPS IN FROM ABOVE until it lands on the shoulder at the foot of each groove.
# The grooves hold it in X and along the strip; the shoulders hold it in height.
#
# EVERY LAYER OF THAT LANDS ON THE ONE BELOW IT. A post is rooted on the slab and on the wall
# at once — a corner bracket in one piece with both faces it stands on, first layer on the bed,
# nothing printed over air and no support to pick out of a groove. That is the whole reason the
# card lies along the strip rather than across it: a card across the strip has to be caught by
# rails reaching horizontally off the wall, and a rail reaching off a wall is a rail printed
# over nothing.
#
# The can is centred on the card and reaches within half a millimetre of each long edge, which
# is what settles the rest: only the ENDS of the long run have material clear of the can, so the
# grooves take those, and what a groove may swallow there is what the can leaves and no more.
mq6_rail_wall = 3.0         # post section around the groove, and the shoulder under the card
mq6_slot_press = 0.15       # per-side slip in the groove, the wells' own figure
mq6_grip = 5.0              # how much of the card's long run each groove swallows at its end
# The pins face EAST off the card and the loom lands on them out of the bay, so the cheek on
# that side is cut away across the header — this is what the cut leaves either side of the pin
# field.
mq6_header_relief = 2.0
# The card's own axes in the strip's frame. It lies along the strip with its plane parallel to
# the flank, so its long side runs fore-aft, its short side is the height, and the whole of what
# it spends across the strip is its own thickness.
mq6_card_x = _mq6.PCB_T     # 1.6 — the card itself, what the groove grips
mq6_card_y = _mq6.PCB_X     # 32 — the long run down the strip
mq6_card_z = _mq6.PCB_Y     # 20 — height, the card's short side
# And the can, which is the only part of the board that reaches into the flank's own section: it
# bottoms in a well cut back to `lip_face_x` (`_front_bottom_flank_skin`), so THE WALL IS STILL
# THE DATUM IN X and what stands the card off it is the can's own height. Across, the can is what
# the well opens and what the two posts stand clear of, and both read this one figure.
mq6_can_yz = _mq6.CAN_D     # 19 — the can's diameter, in the plane the well is cut on

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


# --- the condenser's two vents ----------------------------------------------
#
# THE VENT IS THE FLUTES, PIERCED. The block's fan draws through one flank and blows out the
# other, and both flanks already carry the reeded field — so a slot narrower than the groove is
# struck down the groove's own FLOOR, on the same centres, clean through the section under it.
# Both jambs run WITH the flute and the groove carries on past both ends of the slot at full
# depth, so nothing crosses a flute anywhere in this feature and no `_flute_stop` treatment is
# owed at any edge it makes — the skin's own rule, that a rim running with the flutes is not one
# of them. Off-normal the wall reads as unbroken reeding; head-on it is a grille.
#
# EVERY GROOVE, NOT ALTERNATE. The coupon at `c14bb2fff` printed the three schemes side by side on a
# section of this same flank at this same pitch, and the widest slot down every groove is both the
# more open of them and the thicker at its thinnest: what a slot is measured against is the MULLION
# left between two of them (`reeding.mullion`, `reeding.pierce_max`) and not the section behind the
# groove floor, and the two move OPPOSITE ways. A wider slot puts its jamb further out on the
# half-ellipse, where the groove is shallower and the wall behind it thicker.
#
# THE STATIONS ARE THE FIELD'S OWN. A slot is struck at a groove centre found by walking arc
# length (`flute_centres`, `plan_at`), not at a Y typed here, so the vent follows the field if
# `flute_count` is ever retuned and a jamb can never land off a groove's floor.
#
# IN HEIGHT THE BAND IS THE FAN, not the airway. What moves air through this wall is the axial
# fan bolted to the block's own flank; the finstack either side of it is served by whatever that
# fan pushes, and wall opened opposite it is opening on metal. So the band is the block's placed
# extent (`cond_airway`) brought in `cond_fan_rise` at the base and `cond_fan_drop` at the crown
# — the fan's own footprint on the flank and nothing wider (`vent_band`).
#
# LESS WHATEVER THE FLANK CARRIES BEHIND THAT PARTICULAR GROOVE. Nothing is listed: the piece is
# asked, groove by groove, what stands rooted on its inner face there, with `cond_vent_clear`
# round the root in Y and Z. The transoms are the opening vocabulary, so a root touching part of
# one segment leaves that whole segment as fluted wall; a lone opening beyond such a land stays
# wall as well. THE MQ-6'S CRADLE IS NOT ONE OF THE ROOTS THE INTAKE ANSWERS FOR: its two posts
# stop at the card's crown and the band starts one `cond_fan_rise` over the block's base, so the
# whole cradle stands under the vent with the clearance to spare and the lowest course runs the
# full segment across like every other.
#
# AND THE BAND IS CROSSED BY TRANSOMS, which is what makes it printable. A mullion is
# `reeding.mullion` across on a `2 * wall` wall, so a slot run the whole height of the fan leaves
# a picket fifty-odd times as tall as it is thick, with nothing tying its top to anything. The
# brace is NOT a bar between two of them: at `cond_vent_transoms` heights the wall is simply NOT
# PIERCED (`vent_transoms`), so every mullion and both jambs run into one full-section plate
# `cond_vent_transom_h` tall. Nothing bridges, nothing stands at 45° across a groove, and nothing
# grows out of a tower. The GROOVE runs through a transom unbroken — only the piercing stops —
# so the field reads continuous down the flank and a transom is invisible off-normal.
cond_vent_clear = wall       # the root the vent leaves round anything standing on the flank
cond_vent_probe = wall       # how far inboard the flank is read for what stands on it. A rail,
                             # a fin or a pod web is ROOTED on the inner face, so its first
                             # `wall` is what a slot behind it would break out of; a body
                             # standing free of that face is not the vent's to answer for
cond_vent_island_min = 2     # one opening marooned past a solid land is a nick, not a grille
cond_fan_rise = 22.0         # the fan's own bottom over the block's, measured on the block
cond_fan_drop = 5.0          # and its top under the block's crown. The two and the fan's 110 mm
                             # close on `condenser_block.FACE_B`, which is what says they are a
                             # reading of one face and not three numbers
cond_vent_transoms = 3       # unpierced bands crossing the vent, each one tying all 22 mullions
                             # and both jambs into a single plate of full section
cond_vent_transom_h = 4.0    # how tall each one stands — more than an exterior loop pair either
                             # side of the groove's own floor, so a transom is wall and not skin


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
# The floor takes the weight and the +Y wall the aft. `enclosure_assembly.check_core_held`
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
# How far the bracket's leg carries UP the +Y wall behind the foot, standing in the band
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

# The appliance's stated HEIGHT — floor slab's underside (z = −floor_t) to the top
# wall's outer face. It is the machine's silhouette, the one dimension a counter
# appliance is judged by before it is opened, and this is the number the thin machine
# is FOR. The contents live under it; `_dims` measures whether they do (`box-height`).
appliance_height = 361.0
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


def back_top_wall_face():
    """back-top's own interior rear plane — `back_top_wall_t` in from the exterior, where the
    box's own is one `wall` in.

    `rear_plane_y` is still the interior of the machine and every body is packed to it; this is
    the plane back-top's own +Y wall and its furniture stand on. back-bottom needs no such
    figure: its wall is the lip's own skin carried to the slab and already measures the same."""
    return rear_plane_y - (back_top_wall_t - wall)


def back_wall_t_at(x, z):
    """The section the +Y wall carries at one station — what a fitting's clamped stack is struck
    from, and the figure `enclosure_assembly.port_clamp_stack` reads it off.

    A RELIEF IS A FACT ABOUT THE WALL, not a note beside it. The CO2 station's barrel cannot take
    `back_top_wall_t`, so the wall is thinner there and this says so by measuring the same figure
    the solid is cut on rather than by naming an exception."""
    if z < z_seam:
        return 2.0 * wall              # back-bottom: the wall and its lip's own skin
    for _who, rx, rz, wx, wz in back_top_wall_reliefs:
        if abs(x - rx) <= wx / 2.0 and abs(z - rz) <= wz / 2.0:
            return wall
    return back_top_wall_t


def back_top_flank_face():
    """back-top's own ±X interior faces — `back_top_flank_t` in from the exterior, where the
    box's own is one `wall` in.

    `interior_x` is still the box's interior and every seated body is packed to it; this is the
    plane back-top's own flank furniture stands on, and the plane `_dims` reads back against the
    pack (`back-top-flank-clear`).

    FOUR THINGS OUTSIDE BACK-TOP STAND ON THIS PLANE, so `back_top_flank_t` is not back-top's
    alone to move. `_rail_nominal_foot_face` takes the shallower of this and back-bottom's for
    the foot the two of them share; `ceiling_panel.rail_run` measures its rail in from it;
    and the assembly datums both `SPLIT_COLUMN` and the exposed rib's wall root on it. Changing
    the section carries all four, which is why `back-top-flank-clear` reads a body's built solid
    against this face rather than the column it was placed on."""
    ix0, ix1 = interior_x()
    grown = back_top_flank_t - wall
    return (ix0 + grown, ix1 - grown)


def back_bottom_flank_face():
    """back-bottom's own ±X interior faces — `back_bottom_flank_t` in from the exterior, where
    the box's own is one `wall` in and the lip's underwall is `2 * wall`.

    NOTHING OUTSIDE THAT PIECE READS THIS. `interior_x` is still the box's interior and
    `lip_face_x` is still what a body seated low on a flank meets; this is the plane
    back-bottom's own flank stands on, and the plane `piece_root_faces` hands a feature built
    on it."""
    ix0, ix1 = interior_x()
    grown = back_bottom_flank_t - wall
    return (ix0 + grown, ix1 - grown)


def front_bottom_flank_face():
    """front-bottom's own ±X interior faces — `front_bottom_flank_t` in from the exterior.

    `lip_face_x` DOES NOT FOLLOW IT. The card that bottoms on the west flank and the copper lane
    struck off that same plane both keep the face they had, which is what makes the west side a
    well and not a move; the east side has only the condenser against it and that block reads
    this plane, so it comes west with the wall."""
    ix0, ix1 = interior_x()
    grown = front_bottom_flank_t - wall
    return (ix0 + grown, ix1 - grown)


def vent_flank_face(sx):
    """The interior face a vent slot is struck from — the plane the cut has to start at for the
    grille to come out the other side.

    IT IS THE FACE THAT IS THERE AND NOT `lip_face_x`. The airway stands in front-bottom's own
    bands, and that piece carries `front_bottom_flank_t` down both flanks where the lip's own
    underwall would leave `2 * wall` — so a slot struck on the lip's plane stops short of the
    room, and what it leaves is a blind pocket with the wall still closed behind it. Read by
    the cutter, by the run finder and by the measure, so all three agree about the same wall."""
    ix0, ix1 = front_bottom_flank_face()
    return ix1 if sx > 0.0 else ix0


def front_top_flank_face():
    """front-top's own ±X interior faces — `front_top_flank_t` in from the exterior, where the
    box's own is one `wall` in.

    `interior_x` is still the box's interior, and the bodies and the seams are all struck on it;
    this is the plane front-top's own flank furniture stands on and the plane its openings are
    cut to. All four pieces carry their own section in from it, and `_rail_nominal_foot_face`
    takes the shallower of this and front-bottom's for the foot the two of them share, so the
    front column's two sections answer to each other."""
    ix0, ix1 = interior_x()
    grown = front_top_flank_t - wall
    return (ix0 + grown, ix1 - grown)


def lip_face_x():
    """The ±X interior faces BELOW a Z seam, one `wall` inboard of `interior_x`.

    A wall a Z-seam lip stands on is `2 * wall` thick from the floor slab to the lip rim
    (`_lip_underwall`), so what a body seated low on a flank meets is this plane and not
    the other one. The MQ-6's can bottoms on it through the well cut back to it
    (`_west_cradle`), which is what stands its card off the flank in X."""
    ix0, ix1 = interior_x()
    return (ix0 + wall, ix1 - wall)


def piece_root_faces(inner, y_side, z_side):
    """The six interior planes a feature built on THIS PIECE actually roots on — `inner` with
    each face that piece carries thicker than the box's own standing where that piece puts it.

    `inner` IS THE BOX'S INTERIOR and every seated body is packed to it, which is what makes it
    the right frame for a station: a run's lane, an anchor's band and a boss's plan are all struck
    against the plane the pack stands in. IT IS NOT THE FRAME A RIB STOPS IN. Four faces on this
    box stand inboard of it on the piece that carries them — back-top's two flanks
    (`back_top_flank_face`), front-top's (`front_top_flank_face`), back-top's +Y wall
    (`back_top_wall_face`), and a bottom piece's flanks, which are the lip's own underwall
    (`lip_face_x`) — so a feature drawn to the box's plane on one of those is drawn to a plane
    that piece has already filled in.

    WHAT THAT COSTS IS THE ZIP TIE'S CHANNEL. A rib's two ends climb from the bore's crown to the
    face it roots on and the channel is the room LEFT between them (`_tube_anchors`): measured to
    a plane the wall stands inboard of, the whole of it comes out inside that wall's own stock,
    and the rib arrives buried to its crown with nowhere for a tie to pass."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    if z_side == "top":
        ix0, ix1 = front_top_flank_face() if y_side == "front" else back_top_flank_face()
        if y_side == "back":
            iy1 = back_top_wall_face()
    else:
        ix0, ix1 = (back_bottom_flank_face() if y_side == "back"
                    else front_bottom_flank_face())
        if y_side == "back":
            iy1 = rear_plane_y - wall      # the lip's own skin, already `2 * wall` of section
    return (ix0, ix1, iy0, iy1, iz0, iz1)
# The interior REAR PLANE — the inner face of the +Y wall, stated the same way. A
# component dragged forward inside the machine does not make the machine shallower,
# a pack that outgrows this plane reads red on `box-depth` instead of quietly resizing
# the appliance.
rear_plane_y = 464.0
# --- back-top's own +Y section ------------------------------------------------
#
# THE +Y WALL IS ALREADY TWO WALLS THICK WHERE IT IS A BOTTOM PIECE. `_lip_underwall` carries
# the lip's own skin from the floor slab to the rim on all three of back-bottom's sides, so that
# wall measures `2 * wall` from the slab up. Above the rim it is back-top's, one `wall`, and this
# is what makes the two agree: one section for the whole back of the machine.
#
# IT IS TAKEN INWARD, off `rear_plane_y`, and 6 is the whole of what there is. The cold core and
# the water pump both end at y 461.00 and the PSU at 460.50, so the room behind them is exactly
# `rear_seam_clear` — which is the standoff this wall was given in the first place, and which
# back-bottom already spends. A seventh millimetre is a wall drawn through the core.
back_top_wall_t = 6.0
# AND ONE STATION CANNOT AFFORD IT. What clamps a rear-wall fitting is its own bare barrel
# between flange and nut, and what that barrel spans is the wall's outer face down to whatever the
# nut lands on (`enclosure_assembly.port_clamp_stack`). The four umbilical unions offer 15.29 mm
# of barrel and do not care; the CO2 neoFit offers 7.90, and a 6 mm wall spends six of them — an
# M17 × 1.5 nut left holding 290 psi on 1.90 mm of thread. So the wall gives that one station back
# to `rear_plane_y` — the plane it is struck off — and the port field stands its whole boss on the
# section that leaves, so the nut lands on the boss with 2.90 mm of barrel under it.
#
# AND THE C14 IS THE SAME BARGAIN FOR A DIFFERENT REASON. Its receptacle bears on the fore face
# of a TUNNEL standing off this wall (`c14_tunnel_len`) and not on the wall itself, and the two
# M3 heat-sets holding it enter that fore face from inside the machine. Each one bottoms on this
# wall's inner face, so what stands over its blind end is the wall — and `socket_cap` is what an
# insert on this box is given over a blind end, which `wall` is and `back_top_wall_t` is not.
#
# THE RULE UNDER BOTH: what a fastening lands on keeps the plane it lands on. Stated as
# (station, x, z, across_x, across_z) — whose relief it is, where it stands, and the rectangle it
# takes. The name is carried because a relief that drifts off the thing it was cut for is a
# relief for nothing, and `back_wall_t_at` read at the placed station is what says whether it
# still lands on it (`enclosure_assembly.check_wall_clamped`, `_c14_tunnel`).
# AND THE COLUMN THE WHOLE C14 CHAIN HANGS ON IS SET BY THE CEILING ABOVE IT. The receptacle's
# exact moulded rim stands under the +X ceiling strip, and this is the station at which it clears
# the COMPLETE wall-rooted 45 degree corbel by the card's own clearance floor — so that wedge runs
# over the inlet whole, with no relief band cut in it and no short roof left over the printed
# collar (`enclosure_assembly.check_c14_ceiling_corbel` reads the air off the unrelieved wedge).
# The cutout, tunnel, collar, both screws and the wall relief below all read this one name.
c14_station_x = 66.9
# The wall relief ends inside the rounded tunnel on both X sides.  That retained overlap is
# structural stock, not running air: it makes the wall and the R3 tunnel one unambiguous solid
# through the rounded upper corners instead of enclosing a sub-nozzle air pocket at an exactly
# tangent square-cut/round-fill boundary.  The aperture and both insert stations lie inside the
# relieved field and their cutters still run after the tunnel is fused.
c14_wall_relief_overlap = 0.3
back_top_wall_reliefs = (
    ("co2-inlet", 2.65, 336.21, 30.0, 30.0),      # the neoFit's nut, across its corners
    ("c14-inlet", c14_station_x, 336.21,
     47.0 - 2.0 * c14_wall_relief_overlap, 35.15),
)

# --- what stands on that relief: the C14's tunnel ------------------------------
#
# THE HOLE IN THIS WALL IS A TUNNEL AND NOT A BORE. `_c14_tunnel` wraps the cutout in material
# on the wall's inner face and the receptacle screws to that block's FORE face, so what the
# customer pushes the cord down is the aperture's own rectangle carried the whole depth of wall
# and tunnel together, and what stands outboard of the back face is nothing.
#
# ITS LENGTH IS THE INSERT'S OWN DEPTH. Each of the two M3 heat-sets enters the fore face —
# from inside, the way every insert on this box goes in — and bottoms on the wall's inner face
# under `socket_cap` of wall.
c14_tunnel_len = heatset_depth
# THE SECTION IT KEEPS ROUND THE BORE, and it is the section this wall already carries: the
# tunnel is the +Y wall of back-top made deep. What stands in it is the mouth a cord is pushed into a few
# thousand times, and what a millimetre of it costs is infill.
#
# ACROSS X THE INSERTS ASK FOR MORE and the tunnel gives it: each stands off the axis at its own
# station with `heatset_dia` of bore and `boss_ligament` round it, which reaches further than
# this section does. `_c14_tunnel` takes whichever is further per axis, so the bore keeps its
# own rectangle and both stations land in material.
c14_tunnel_wall = back_top_wall_t
c14_tunnel_r = 3.0
# --- and the collar the receptacle drops into ---------------------------------
#
# THE FLANGE LANDS IN A PROFILED POCKET AND NOT ON A FLAT FACE. A separate collar continues
# inboard from the established tunnel's fore face. Its inner and outer silhouettes come from
# `iec_c14_inlet.flange_profile`, the same rounded/tapered wire that draws the purchased part,
# so a rectangular restatement cannot shave an angled edge or hide a thin corner.
#
# THE POCKET IS 0.5 MM OFF THE MOULDING. The outer wire is another 3 mm beyond it everywhere
# in XZ, and the collar continues one 3 mm section past the flange's own inboard edge in Y-.
# A sheared copy of that outer wire runs from the collar mouth to the wall, making the collar
# and its print corbel one continuous load path without widening the tunnel behind it. The floor
# remains the established seating plane: none of these moves the part or its screws.
c14_collar_slip = 0.5
c14_collar_wall = 3.0
c14_collar_extension = 3.0
# THE FLANGE ENTERS THROUGH THE FIXED +X STRIP before it reaches that collar. Carry its exact
# slipped profile another 9 mm in Y- so the two-ear moulding can be held square and translated
# into its seat. One further millimetre is a boolean overcut past the stated running clearance,
# not assembly travel.
c14_insertion_relief = 9.0
c14_pocket_overcut = 1.0


def c14_mount_half(bore_w, bore_h, screw_reach):
    """Half extents of the established tunnel carrying the bore and two inserts."""
    return (max(bore_w / 2.0 + c14_tunnel_wall,
                screw_reach + heatset_dia / 2.0 + boss_ligament),
            bore_h / 2.0 + c14_tunnel_wall)


def c14_collar_half():
    """XZ half extents of the exact-profile collar's outer offset."""
    offset = c14_collar_slip + c14_collar_wall
    return (_c14.FLANGE_W / 2.0 + offset, _c14.FLANGE_H / 2.0 + offset)

# --- back-top's own ±X section ------------------------------------------------
#
# BOTH FLANKS CARRY THE SAME NINE-MILLIMETRE SECTION AS THE OTHER THREE PIECES. It is taken
# INWARD off `interior_x`, so the appliance's stated width and every exterior show face stay
# fixed. The nominal band begins past both telescopes and above the Z-seam rim
# (`_back_top_flanks`). At that seam `_z_rail_feet` carries the same section down to each
# caught face, and the back-bottom head spends the three millimetres gained past its lip wall
# on a five-millimetre overlap over that foot. The complete back joint therefore carries the
# grown section without moving an exterior face.
#
# WHAT STANDS ON A FLANK READS THE FACE THAT IS ACTUALLY THERE. Wago wells and the drip-pan
# sleeve cut their own berths through the whole section; the two fitting anchors give their zip
# tie lanes back to `interior_x`; and the +X power column keeps its full insert-length boss datum
# clear of this face. The one routed tube that crosses the new stock gets the named support-free
# relief below.
back_top_flank_t = 9.0

# The `water-3` run crosses the front/back joint in the west strip. Its front-top share already
# has the same relief; this is the aft continuation, on back-top from the first plane past the Y
# telescope until the route has turned inboard. The floor is `lip_face_x`, leaving six
# millimetres of wall, and the roof rises at `relief_chamfer` to the nominal nine-millimetre face.
# Stated as (placed-body name, side, y0, y1, z0, z1).
back_top_flank_reliefs = (
    ("tube-water-3", -1.0, 215.0, 245.0, 248.0, 273.0),
)
# --- back-bottom's own ±X section ---------------------------------------------
#
# AND THE STOREY UNDER IT CARRIES MORE, because down there nothing is in the way. The only
# body on this floor is the cold core, and it packs `side_band_inset` off `interior_x` — so
# where back-top's flank has the vent slots' mullions and the power column against it, this
# one has 14 mm of air on both sides and spends 3 of it.
#
# IT IS TAKEN INWARD off `lip_face_x`, the face the lip's own underwall would otherwise leave.
# The back rail follows it: its arm stands at the grown face and its head spends the same added
# section on the overlap over back-top's foot. What the strip leaves at the rim is a step facing
# UP, on a piece that prints floor-down — the one direction a step costs nothing.
back_bottom_flank_t = 9.0
# --- front-bottom's own ±X section --------------------------------------------
#
# THE FRONT PIECE CARRIES THE SAME 9 DOWN BOTH FLANKS, and neither body against them moves the
# way you would expect. The MQ-6's can bottoms on `lip_face_x` and the suction lane is struck off
# that same plane, so the WEST face cannot move without carrying the card inboard and the
# compressor east with it — the section closes ROUND the can instead
# (`_front_bottom_flank_skin` wells it off the station's own silhouette). The condenser's block
# already answers to the EAST wall
# (`enclosure_assembly.east_lane_free` stands it `cond_mount_clear` off this face), so that face
# moving carries the block west into the lane it has always had off the compressor's tangent.
#
# AND THE VENT STILL GOES CLEAN THROUGH. A slot is struck from the face that is actually there
# (`vent_flank_face`), so the grille pierces whatever this wall measures rather than a stated
# `2 * wall`; what a deeper wall costs the intake is throat, which `VENT_ASPECT` reads.
front_bottom_flank_t = 9.0
# AND IT OWES ITS ROOM TO THINGS THAT WERE ALREADY THERE. The front half's Y lip telescopes into
# this piece on this wall surface and back-bottom's Z lip rises into it on the same one, and the
# lane each rises into is exactly the `wall` this would add — so the section begins past the one
# and above the other, and neither telescope is ever asked about. The Wago wells bore from
# `interior_x` as they always did, so a lever nut bottoms where it bottomed and simply sits in a
# deeper pocket. And the ASSE drip pan's sleeve keeps its whole block: the pan withdraws through
# this flank, so what stands round it is the sleeve's own section and not this one.

# --- back-top's own ceiling ---------------------------------------------------
#
# THE REAR CEILING HAS ITS OWN PHYSICAL FACE, the same way this piece's grown flanks do. The
# box's established interior-ceiling lane remains where the packed bodies, ports and anchor
# stations were laid out; the printed strip carries another wall inward from that lane. The
# appliance's exterior top face and every packed world datum therefore stay fixed.
back_top_ceiling_t = 2.0 * wall
back_top_ceiling_growth = back_top_ceiling_t - wall
#
# WHAT THIS PIECE KEEPS OF ITS CEILING is the two side strips either side of the slide-in panel
# (`../ceiling-panel/ceiling_panel.py`), `rail_run` wide, and each is CORBELLED the way front-top's
# two are either side of the throat (`_ceiling_corbels`): a 45 degree underside rising off the
# flank face to nothing at the panel's edge, so a piece that prints mouth-down lays every layer of
# that strip on the one below it. The field between them is the panel's, and this piece takes it
# away rather than printing a slab in mid air over the whole service bay.
#
# AND WHAT STANDS IN THE CORBEL KEEPS THE PLANE IT STANDS ON. The corbel descends a millimetre for
# every millimetre it runs outboard, so it is DEEPEST AT THE WALL — which is exactly where the rear
# storey's own furniture stands, and shallowest at the panel's edge, where nothing does. A RELIEF
# IS A FACT ABOUT THE STRIP, not a note beside it, and `ceiling_corbel_at` measures the same figure
# the solid is cut on. Stated as (station, sx, y0, y1, keep, out): whose relief it is, which flank
# it stands on, the band it takes, and THE RUN BAND IT GIVES UP — everything from `keep` out to
# `out`. Inboard of `keep` and outboard of `out` the strip keeps its corbel; between them it is
# the top wall's own section alone and takes print support unless a stated Y gable closes that
# short band from its two intact ends.
#
# A RELIEF IS A BAND AND NOT A CUT-OFF because a body is a band. Where a fitting stands hard
# against the panel's edge the two are the same thing — `out` is the strip's whole run and what is
# left is the wedge's thin end, which is what a body a millimetre under the ceiling leaves room
# for. Where a body stands in the MIDDLE of the strip, taking everything outboard of it as well
# throws away the one part of the corbel that is rooted on the flank and self-supporting, and
# leaves the whole strip's width hanging. So a row gives up what its body occupies and no more.
#
# THE TWO ELECTRONICS ROWS ARE MEASURED AGAINST THE PLACED SOLIDS AND NOT AGAINST THEIR BOXES, and the
# difference is most of what they say. A bounding box on this pack stands well inside its own
# metal, and a strip read off boxes is a strip with no corbel left in it. What the exact solids
# reach — the y band the metal is actually in, how far inboard it comes, and the clearance the
# kept run then stands off it — against the box each row would have been read off:
#
#   relay-1        y 252.50..322.50, in to |x| 86.50, gives up 3..19    (box y 252.5..322.5)
#   ground-stack   y 327.68..340.32, in to |x| 86.45, gives up 5..19    (box y 325..343, x 84.45)
#
# THE GROUND ROW CLOSES AGAIN FROM ITS TWO Y ENDS. The ring stack is short enough in Y for the
# intact wall corbel immediately fore and aft of it to carry a pair of 45 degree roof planes to
# a ridge over the stack's centre. The X relief still gives the purchased body its exact room,
# but there is no horizontal roof left over that room and therefore no support body on its crown.
#
# THE C14 KEEPS THE COMPLETE +X WEDGE. `c14_station_x` is struck for this: at that column the
# purchased moulded rim stands one assembly clearance clear of the exact 45° ceiling corbel, with
# its Z on the top port row. Its tunnel, screws and wall relief all read that one station, so no
# ceiling-relief row is needed and no short roof is left over the printed collar below.
#
# THE TAP-WATER CHAIN IS THE ONE THAT STANDS IN THE MIDDLE, and it takes four rows because what
# it occupies is four different things. Read off the placed chain against the full wedge, the
# metal inside the corbel is:
#
#   y 354..394     run  1.50..14.09      the Multiplex barrel, its crown one
#                                        `DECK_CEILING_CLEAR` under the ceiling
#   y 394..424     run  4.67.. 5.42      the ASSE body aft of the anchor — three quarters of a
#                                        millimetre of run, in a strip 19 wide
#   y 424..425     nothing
#
# 1275 mm3 of a 12816 mm3 corbel, and NONE of it outboard of run 14.09. So the outboard run is
# given back: it is the half of the wedge that roots on the flank and carries itself, and taking
# it left the strip's whole width hanging over the rear storey for 71 mm of depth.
#
# WHAT STILL TAKES THE WHOLE RUN IS THE TWO TIE BANDS. Each zip tie is a closed loop that comes west
# over the chain's top flat in the `DECK_CEILING_CLEAR` lane and drops into the cavity through the
# anchor's back — and that cavity's top mouth is out at the wall (`_asse_tie_cavity`), so a corbel
# standing over the outboard run would roof the one opening the zip tie has. `_asse_cradle` reads
# these two rows back against the ties it was handed, so a band that moves off its zip tie says so.
# The run the side strip actually has: the nominal flank face to the panel's own edge. A thicker
# flank spends its added section outboard and shortens only the exposed corbel; the panel and the
# appliance silhouette do not move.
_RAIL = back_top_flank_face()[1] - _funnel.collar_w / 2.0
back_top_ceiling_reliefs = (
    # THE BAND STANDS OFF THE BOSSES AT ITS OWN ENDS. The relay's two upper mounting bosses are
    # `mount_boss_dia` cylinders centred y 254.5 and 320.5, so their end faces lie ON y 251 and
    # 324 — and a relief ending there would put the cut's own face on a boss's, which is four
    # faces on one edge and a mesh a slicer refuses. A millimetre past each is a plain face. The
    # stack's own single boss is centred y 334.0, so its end faces lie on y 330.5 and 337.5.
    ("relay-1",        +1.0, 250.0, 325.0, 3.0, _RAIL),   # the relay's crown, mid-strip
    ("ground-stack",   +1.0, 327.0, 341.5, 5.0, _RAIL),   # the +X ground bar's stack, aft of it
    # The tap-water chain's four. The barrel and the body give up what they stand in; the two tie
    # bands give up the whole run, so the zip tie's cavity opens on air out to the wall.
    ("asse1022-barrel",   -1.0, 354.0, 394.0, 0.0, 16.0),
    ("asse1022-body",     -1.0, 394.0, 424.5, 0.0,  7.0),
    ("asse1022-tie-fore", -1.0, 358.0, 364.5, 0.0, _RAIL),
    ("asse1022-tie-aft",  -1.0, 384.0, 390.5, 0.0, _RAIL),
)

# Relief bands whose flat ceiling is filled back with two 45 degree planes rooted in the intact
# X corbel at their Y ends. The value is the ridge Y. A body belongs here only when its exact
# placed solid clears that roof; `ground-ceiling-gable` reads this one back against the purchased
# stack and against the finished back-top piece.
back_top_ceiling_gables = {"ground-stack": 334.0}


@functools.lru_cache(maxsize=1)
def _ceiling():
    """The slide-in ceiling panel, as a module — the part that STATES this joint's mating
    figures, and the one this file reads them from rather than restating any of them.

    Imported here rather than at module scope for `machine_of`'s reason: that module is drawn on
    this one's planes, so reading it at import time would have it importing a module that is
    importing it back."""
    import ceiling_panel
    return ceiling_panel


def ceiling_corbel_at(x, y, growth_reliefs=()):
    """How deep back-top's ceiling strip hangs below the ceiling plane at one station — the
    corbel's own reach under the top wall's section.

    `back_wall_t_at` one storey down, keyed on (x, y) rather than (x, z): it is the strip's run
    outboard of the panel's edge where the strip is corbelled, and NOTHING where a body stands in
    it or inboard of that edge, where the ceiling is the panel's and not this piece's."""
    run = abs(x) - _ceiling().panel_half_w
    if run <= 0.0:
        return 0.0                         # the panel's own field — no strip, and no corbel
    for _who, sx, y0, y1, keep, out in back_top_ceiling_reliefs:
        if sx * x > 0.0 and y0 <= y <= y1 and keep < run <= out:
            return 0.0
    grown = back_top_ceiling_growth
    for _who, rsx, x0, x1, y0, y1 in growth_reliefs:
        if rsx * x > 0.0 and x0 <= x <= x1 and y0 <= y <= y1:
            grown = 0.0                    # the established wedge remains; only growth leaves
            break
    return grown + run


def ceiling_stations(digiten, anchors, panel: bool):
    """Which of the ceiling's own stations each side of that joint builds — the slide-in panel's
    when `panel`, back-top's otherwise.

    A rib roots on the face it is handed, and back-top's ceiling over the panel's field IS the
    panel, so a station standing there is the panel's to build and this piece's to leave alone.
    BOTH SIDES READ THIS ONE CALL, so neither can grow a rib the other grew too and no station can
    fall between them. A rib rooted on a WALL is never the panel's, whatever its plan.

    AND WHAT BACK-TOP KEEPS OF ITS CEILING IS CORBELLED. Outboard of the panel's edge the strip
    hangs `ceiling_corbel_at` below the ceiling plane, so a station out there roots on a slope and
    not on the plane its rib would be drawn to — and a rib drawn to the plane arrives buried, the
    zip tie's channel filled with the corbel's own stock. There is no such station and this is what
    keeps it that way: a ceiling rib either stands over the field, where the panel takes it, or on
    a run of strip the corbel has left flat."""
    cp = _ceiling()

    def over_field(x, y):
        return abs(x) <= cp.panel_half_w and cp.fore_y <= y <= cp.aft_y

    meter_anchors = None
    if digiten:
        bands = digiten[3]
        if over_field(digiten[0], (bands[0][0] + bands[-1][1]) / 2.0) == panel:
            meter_anchors = digiten
    ribs = tuple(s for s in (anchors or ())
                 if (tuple(int(round(c)) for c in s[2]) == (0, 0, 1)
                     and over_field(s[0][0], s[0][1])) == panel)
    if not panel:
        plans = [(s[0][0], s[0][1]) for s in ribs
                 if tuple(int(round(c)) for c in s[2]) == (0, 0, 1)]
        if meter_anchors:
            plans.append((meter_anchors[0],
                          (meter_anchors[3][0][0] + meter_anchors[3][-1][1]) / 2.0))
        for station in plans:
            deep = ceiling_corbel_at(*station)
            if deep > 0.0:
                raise ValueError(
                    f"ceiling_stations: a rib rooted on the ceiling stands at x {station[0]:.2f}, "
                    f"y {station[1]:.2f}, where back-top's strip hangs {deep:.2f} mm below the "
                    f"ceiling plane. What that rib would stop on is the corbel's slope, and the "
                    f"channel its ends leave under the plane is inside the corbel's own stock. "
                    f"Move the station over the panel's field or onto a wall.")
    return meter_anchors, ribs


# And the interior FRONT PLANE, holding the other end. The front wall is `front_wall` thick —
# the face a user hauls the pump cartridge out by, so it carries section the way the facet
# does — and it grows INWARD: the exterior stays where the appliance's stated depth put it
# and the interior face stands here. What noses into the section gets a RELIEF, 45°-chamfered
# like every pocket on this box (`front_reliefs`): the refrigeration stratum keeps the face it
# was packed against, and the pump bay roots on pocket floors struck by its own wrap rule.
# `box-front` reads the pack against the relieved surface, region by region, not one plane.
front_wall = 9.0
front_plane_y = 14.0
# The refrigeration stratum's relief: one stated pocket across THE COMPRESSOR ALONE, floored on
# the face it packs to. It is the only body in this stratum that stands fore of the front wall's
# own interior plane — the condenser bears on that plane through its rails and the fuse clamp
# stands clear behind it — so the wall keeps its full `front_wall` section everywhere else along
# the front.
#
# WHAT KEEPS THE CAN OUT HERE is the −X core stop: `_core_stops` stands a floor block
# `core_stop_web` ahead of the cold core's front face, which spends all but 0.9 mm of the room
# between the two bodies, so a can packed back to `front_plane_y` lands its aft corner in it.
# Stated as (x0, x1, z0, z1, floor).
fridge_relief = (-78.0, 36.0, -1.0, 148.0, 11.0)
# And each pump's relief in the cradle face. Its floor follows the pump station: behind the
# pumps, that travel leaves `pump_pull_wall` of printed aft wall for the cartridge to carry
# when its pulls draw the pumps against the collet plate.
pump_relief_skin = 3.9
pump_station_front_y = front_plane_y - front_wall - pump_cartridge_proud
# The complete flute field continues over the removable show face. One full groove depth moves
# that surface ahead of the pump datum, so its groove floors land on `pump_station_front_y`
# while the pumps, fitting axes, relief floor and aft pull wall remain on their own stations.
pump_show_growth = flute_depth
pump_show_proud = pump_cartridge_proud + pump_show_growth
pump_cartridge_front_y = front_plane_y - front_wall - pump_show_proud
pump_relief_floor = pump_station_front_y + pump_relief_skin
relief_chamfer = _interface.relief_chamfer  # every relief ceiling rises at this angle to the mouth

# --- front-top's own ±X section ----------------------------------------------
#
# THE ONE WALL ON THIS BOX THAT IS NOT `wall`, and the only piece that carries it. front-top is
# the piece a hand works: the pump cartridge is hauled out through its face, and `_bay_cut`
# removes the complete front and flank band the cartridge owns. What is left stands 195 mm tall
# on a seam rim it prints mouth-down on; the wall aft of the collet plate and the lintel over
# the cradle keep its two flanks joined.
#
# IT IS TAKEN INWARD, and that is the whole of why nothing else on this box moves. The exterior
# is `appliance_width`, the silhouette a counter appliance is judged by, and it stands where it
# stands; `interior_x` is the plane every other piece and every seated body reads, and it stands
# where it stands too. What moves is this one piece's own inner face, and only this piece knows
# about it (`front_top_flank_face`).
#
# WHAT IT OWES, IT OWES TO THINGS THAT WERE ALREADY THERE: its main band begins at the Z-seam
# rim and its rail feet carry the same face through the storey below; the collet plate clears
# the rails' complete moving envelope; the openings are cut to the face this leaves; and the
# Wago wells bore through it to bottom on `interior_x`, so a lever nut sits where the box's own
# interior puts it and simply has more wall behind it.
front_top_flank_t = 9.0
# And its one relief. `tube-water-3` runs down the −X flank inside the section this adds, so the
# wall gives that run its lane back over a stated band and keeps the rest. Floored on
# `lip_face_x` — the plane this box already states one `wall` inboard of `interior_x` — which
# leaves 6 mm of wall standing there and clears the tube by better than a millimetre. Stated as
# (y0, y1, z0, z1); the roof rises at `relief_chamfer` to the mouth, like every pocket here.
front_top_flank_relief = (180.0, 215.0, 248.0, 266.0)

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
# crown (`z-seam-front-lane`) and the rim under the forward valve tray's plate
# (`z-seam-under-deck`). Across the bay the ring's front segment goes to the bay floor and
# the pump heads over it (`_front_flat_lip_drop`), and the seam's own MOUTH is the plane
# that floor lies on (`bay-floor-bedded`); the pumps ride behind the pump cartridge face's own
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

# THE Z SEAMS SLIDE HOME, AND TAKE NO SCREW. Each top piece enters off the end of the box
# it stands at and slides the length of its own column — front-top fore of home over the
# front wall's own plane and aft to its stop, back-top aft of home over the rear wall's and
# fore to its own — riding a HOOKED RAIL down each ±X flank: the bottom
# piece raises an ARM on its mouth down each straight run, and the arm's HEAD steps
# outboard over the groove the top's FOOT slides in — the top's wall carried to the
# mouth at full section, with a notch above the foot that swallows the head. Lifting the
# top lands the foot's flat top face on the head's flat underside along the whole of
# both runs — horizontal printed face on horizontal printed face — so the seam is held
# closed continuously down every millimetre both flanks carry.
# The slide stops on a STOP BLOCK closing each rail's far end — the foot's end face on
# the block's, the one nominal contact in the joint and the column's Y datum — with the
# end walls and corner turns closing head-on one `slide_slip` behind it. THE TWO COLUMNS
# GO ON TOWARD EACH OTHER AND ESCAPE APART: front-top draws off the front of the box, into
# open air, and back-top off the back. What holds front-top is the Y seam's upper pair of
# screws — the plug back-top carries, in the socket front-top's lip carries. Four M3×10
# close the whole box, and the two upper ones are what front-top hangs on.
#
# EVERY FACE OF THE JOINT PRINTS AT ITS OWN RULE, and the CATCH faces are square. The
# head's underside — the catch — is the joint's one down-looking flat, an abrupt
# `hook_lap + slide_slip` ledge at the top of a piece that prints floor-down. The notch's roof closes the top's wall
# back to full section at 45° over (that piece prints mouth-down on the same +Z build
# axis); the arm's base falls back to the lip's underwall at 45° under; every sliding
# face is vertical or horizontal. No channel anywhere in the joint closes over the bed
# of the piece that prints it — the notch is an open rebate in the wall's own inboard
# face, not a cavity.
slide_slip = fits.slip       # per-face running clearance on every sliding face of a Z seam
hook_foot = 8.7              # the foot: the top's full section, mouth face to caught face
hook_lap = 2.0               # the catch overlap before a thick flank spends its added section
# Both columns spend the same three millimetres they gain past the six-millimetre lip wall on
# their catches too. Five millimetres still lie wholly over each six-millimetre foot past
# `interior_x`, leaving the fixed exterior skin untouched while both pieces answer to the same
# grown section.
front_hook_lap = hook_lap + (front_bottom_flank_t - 2.0 * wall)
back_hook_lap = hook_lap + (back_bottom_flank_t - 2.0 * wall)
# THE Z SEAM'S OWN STOREY, mouth to rim, and THE FLAVOUR DECK IS ITS CEILING: the rim
# stands under the lowest valve plate (`z-seam-under-deck`), so this is the whole height
# the box has to spend on the joint. What it buys first is the GROOVE — `hook_foot` is
# the top piece's own sliding tongue, the part of the joint a hand can break — and the
# head takes the remainder over the catch. It is a HEIGHT; `lip_len` is the Y seam's
# overlap struck off its own boss, and the two are independent figures.
z_rise = 14.8
# The arm's own section behind its sliding face. It also sets the channel's width, and
# through it the gable's ridge height: the ridge stands PROUD of the bay storey's one
# ledge plane (`rim + wall` — the seam cap's top and the sill), so the roof leaves that
# plane through a slot instead of meeting it edge-on in a zero-thickness line.
hook_arm = 4.0
rail_stop_len = 4.0          # the stop block closing each rail's far end, along Y
rail_entry = 5.0             # approach past full disengagement, entry to first engagement
rail_lead = 2.0              # 45° plan taper easing the head's open end over the foot
# HOW FAR THE RAIL REACHES BELOW ITS SEAM, the way `z_rise` is how far it reaches above. The
# arm's base falls back to the lip's underwall on a 45° under-flare, so the fall equals its own
# run: the arm's back stands `slide_slip + hook_arm` inboard of the nominal foot face and the
# underwall half a millimetre outboard of it. `_z_rail_heads` builds that fall and `_lip_denied`
# denies seam heights by it — a body's crown has to clear the flare, not merely the wall over it.
rail_flare_drop = slide_slip + hook_arm + 0.5
# The deepest plane either hooked profile reaches inboard of `interior_x`: its full nominal
# foot first, then the arm clearance and the arm itself. Both complete envelopes remain inside
# the pack's `side_band_inset`; the collet plate spends this exact figure for its moving berth.
# EITHER means the deeper of the two columns' top sections, because everything reading this
# reads it for both: the plate is held off by the deepest thing it ever passes and holds that
# offset at every height, and `_lip_denied` measures the same band down whichever column it is
# given. Taking one column's section would make the figure true of both only while they agree.
rail_reach_in = (max(front_top_flank_t, back_top_flank_t) - wall) + slide_slip + hook_arm

# --- THE PUMP BAY AND ITS PUMP CARTRIDGE ------------------------------------------
#
# THE PUMPS SLIDE OUT OF THE FRONT OF THE BOX. The front wall's flat span — corner column to
# corner column — and the large lower cradle come out of front-top as one piece, the PUMP
# CARTRIDGE. Both pumps drop into that cradle and one top clamp closes on their stamped
# brackets. The cradle's filled bearing block rides the bay floor while the fixed shell perimeter
# stays 0.5 mm below its exterior face for Z clearance. Nothing latches it: four
# barb tubes gripped in the anchor tees' branch collets are the retention, and the collet plate
# (`enclosure_assembly.build_collet_plate`) is the release — pull the pump cartridge and the tees
# come with it until their collets press the plate, the tubes come free, and the pumps are
# in your hand. Pushing it home threads the four tubes back through the plate's holes into
# the same collets, the cradle's own aft face landing on the plate's.
#
# FRONT-TOP CARRIES A FLOOR ACROSS THE BAY (`_bay_floor`), and everything in this storey
# slides across it. THE FLOOR IS THIS PIECE'S FIRST LAYERS — front-top beds on the seam
# plane, so a floor struck there lies on the bed with nothing under it to hang. Its thickness
# is the only thing above it: the pump cartridge reaches down to the plane its pump reliefs
# floor on, and the floor's top is that plane. Front-bottom's side lip is given up over this
# whole run (`_flank_lip_drop`), so the floor crosses it wall to wall and only the front
# boss's own plinth still stands over the mouth here.
#
# THE COLLET PLATE COMES IN THROUGH THAT BED FACE. Its slot (`_plate_slot`) passes clean
# through the floor and opens on the seam plane, and the steel goes up it until its two
# tails land on the guides' heads. Front-bottom's mouth then closes under the foot, so what
# holds the plate in the machine is the seam itself.
#
# The BAY is the opening all that leaves through: the complete exterior front-wall width from
# the floor's top up past the motor cans' crowns. The two display-support columns and both fixed
# side skins are absent through this storey; the floor's own top is one flat sill and the wall
# over the bay is the lintel carrying the facet and display. Front-bottom's front lip drops
# across the cavity span because the floor stands in that band.
#
# BOTH FLANKS OPEN AS PART OF THAT SAME `_bay_cut`. The opening takes the two front corner
# columns and the exterior side skins with it; at the aft outer edges,
# two narrow fixed plate-retention cheeks overlap the steel's tails and the cartridge carries
# local clearance notches round them (`_plate_fore_guides`,
# `_plate_retention_clearance_notches`). Its floor is the Z-seam
# floor: the installed cradle closes the front-top opening over the seam furniture below it.
#
# THE PUMP CARTRIDGE TAKES THE WHOLE FRONT-WALL WIDTH. Its outer skin follows the enclosure's
# rounded silhouette all the way to both exterior side faces. Its lower edge shares the filled
# block's bed plane, 0.5 mm above the stationary sill, and its crown keeps the same Z clearance
# below the lintel. Its filled interior reaches the side-wall planes and bears
# on the bay floor. The only departures from that full-width envelope are the two hand pockets,
# the pump wells and the aft plate-retention notches.
bay_crown_air = 1.7          # bay top over the tallest motor can's crown
pump_cartridge_z_clearance = 0.5  # Z air above the fixed sill and below the fixed lintel; this
                                  # is not an X/Y inset or a cosmetic surface offset
pump_bay_side_air = 0.5      # pump-body air inside each cavity throat plane
sweep_step_max = 0.25        # largest interval in pump, clamp and withdrawal motion proofs
# THE LOWER CRADLE HAS ONE RECTANGULAR Z OUTLINE. The exterior shell reaches the appliance's
# complete plan silhouette and its filled body reaches both cavity planes without a side taper.
# The monolithic clamp remains inside the cradle's two vertical wells throughout insertion and
# withdrawal.
cap_kiss = 0.1               # the cradle's aft face off the collet plate's, at full seat
# THE STEEL'S OWN AIR, on every edge it presents to printed material. `fits.slip` is the
# figure for a printed face on a printed face; this is the figure for the one part of this
# box that is cut rather than printed — 1/8" 316 off a fiber laser, square-edged, carrying no
# support residue and no elephant's foot, and bought to a lead time.
steel_air = 0.2
plate_slot_slip = steel_air  # air fore and aft of the collet plate in the floor's slot, and
                             # across it too: the slot's constant ends locate the steel in X
                             # and leave `plate_end_stock` printed beyond them
# Each fixed fore cheek overlaps this much of the collet plate's unperforated outer tail. Ten
# millimetres of steel face bears on each cheek; the full-width pump cartridge clears them in
# two local aft-corner notches instead of spending its whole X span inside them. Each notch
# follows the cheek's own plan rake one `fits.slip` fore of it.
plate_guide_tail_land = 10.0
plate_slot_lead = 1.0        # 45 degree flare at the plate lane's Z− mouth, taken out of
                             # the tee wall's fore face (`_plate_lead`) and not the floor's
plate_end_stock = 4.3        # continuous printed X return from either slot end to the
                             # cavity-side wall; the 3 mm outer wall continues beyond it
plate_cap_land = 1.0         # the flat the steel's top edge lands on, taken off the tee wall's
                             # fore face — the plate's Z datum, wall to wall (`_plate_cap`)
plate_shelf_land = 3.0       # front-bottom's shelf inboard of the steel's END, per end — the
                             # bearing the plate's bottom edge rides on (`_plate_shelf`), one
                             # `steel_air` under the land that is the plate's datum
plate_shelf_t = 1.2          # that shelf's own section at its inboard edge, before the 45°
                             # under it takes it back into the flank
plate_guide_wedge = 3.0      # the cheek's extra section at the fixed outer wall, raked away
                             # to nothing at its inboard face over the guide's whole height

# --- THE PUMP CARTRIDGE IS ONE CRADLE AND ONE TOP CLAMP ---------------------
#
# THE LOWER CRADLE IS THE CARTRIDGE. It owns the complete front face, the full-height block
# behind it, both bracket lands and both hand pulls. Each pump drops through
# its open well until the stamped bracket at the head-to-boss junction lands on the cradle.
# Nothing under the head carries it; the front of each head remains one millimetre over the
# bay floor and the bracket puts the load into the block around the well.
#
# THE TOP CAP IS A CLAMP. One filled field spans both pump heads, begins on the stamped
# brackets' upper face and reaches the cradle's common top plane over its complete fore/aft
# depth. The complete boss octagons and motor cans are cut from that field, leaving the
# case-derived locating walls and pressing lands wherever the pumps allow material. One joined
# recess opens down from the crown around both centre screw stations; the individual
# counterbores continue from its floor to the M3 seats. Those screws run DOWN into heat-sets in
# the cradle, so the cap captures both brackets without becoming a second thing the hand pulls
# on.
#
# BOTH PARTS INSTALL IN Z. With the clamp off, the stamped bracket, head and two tube-side
# fittings have straight open paths from the top of the cradle to their seats. The clamp
# follows the same path over the cans. Its plate footprint
# is therefore the well above the bracket plane; below that plane the smaller head room leaves
# the bracket's three closed sides standing on material.
cap_pump_air = 0.4           # running air round the head in the cradle's lower well
cap_tube_axial_air = 0.15    # insertion air along the casing axes; the 13 mm shaft already
                             # includes its radial fit allowance
cap_slot_half = _tray.outlet_open_half
cap_fitting_half = _tray.shaft_w / 2.0
cap_web_land = 4.0           # clamp section under each recessed M3 head
cap_web_t = head_cbore_depth + cap_web_land  # bracket datum to retained access-well floor
cap_screw_off = 18.0         # the two screws fore/aft of the centre access-well midpoint
clamp_bridge_half_y = 6.0    # access well past each screw axis, fore and aft
clamp_bridge_overlap = 2.0   # access-well edge into each pump opening's inner margin
clamp_drop_air = 0.2         # clamp footprint and bracket air through the cradle well

# --- THE HAND PULLS ONLY THE LOWER CRADLE -----------------------------------
#
# ONE PAIR OF SIDE PULLS IS CUT INTO THAT ONE PIECE. Their centre plane is not chosen from
# the block: it is the four tube centres in the collet plate, because those four collets are
# the resistance the hand is overcoming. Pulling on that plane produces translation instead
# of pitching the cartridge against its rails.
#
# Each pull is a plain, stout pocket in an exposed ±X flank. Fingers enter from the side and
# hook the pocket's fore wall; its roof rises one-for-one to the open flank, so it prints
# without a flat bridge. The pocket is entirely in the cradle and the top clamp has no hand
# feature at all.
pull_depth = 18.0            # fingertip reach inboard from each exposed flank
pull_min_run = 22.0          # clear opening from the ledge to the retention clearance's Y− tip
pull_rise = 48.0             # complete side-mouth height, including the 45-degree roof
pull_floor_below_tubes = 12.0  # bed-rooted stock first; then the tube plane inside the mouth


# The whole description of one box — what `build_pieces` cuts the four pieces from: the pack it
# stands around, and the figures the shell measures for itself once it knows what is inside.
#   pack          the placed bodies and every station they put on a wall, as `Pack` states them
#   inner/outer   the cavity and the shell, (x0, x1, y0, y1, z0, z1)
#   y_joint       the front↔back seam plane
#   splits        the bottom↔top seam height per Y column, (front, back)
#   y_bosses      the placement-cleared Y-seam fasteners, one
#                 (inner_x, outer_x, inboard_sign, z) per screw. These are measured while the
#                 placed solids are present and carried on the Box; rebuilding them later from
#                 module state would make a serialized Box a different machine.
#   z_seam_passes whether each (front, back) Z seam crosses its column rather than an open band;
#                 a report reading taken with the placed solids, carried for the same reason
#   column_reliefs what the standing corners' PILLARS give up to the pack standing in them, one
#                 (sx, sy, name, room) per body — the corner's own signs, whose body it is, and
#                 the world box the column is cut back to, as the six plain bounds
#                 `(x0, x1, y0, y1, z0, z1)` every station on the pack is written in.
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
#   pump_bay      the pump cartridge's opening in the flat front span, (x0, x1, z_top) —
#                 side-wall interior plane to side-wall interior plane, topped over the motor
#                 cans' crowns.
#                 None when the pack stands no pumps
# The two structured fields placement strikes for this description. They live with Box rather
# than with the placement pass so a serialized Box can be restored without importing the whole
# machine that produced it.
PortField = namedtuple("PortField", "proud rim pockets")
Nameplate = namedtuple(
    "Nameplate", "x z width height corner bevel slip thick wall screws "
                 "stem_d reach bore_d bore_depth")

Box = namedtuple(
    "Box", "pack inner outer y_joint splits y_bosses z_seam_passes column_reliefs pump_bay")


def documented(box):
    """The Box as `_box_spec` writes and reads it: its pack's stations without the placed solids.

    A station is numbers and a body is not, so the description a producer hands another action
    carries the walls and not the bodies that sized them. Both sides of a comparison between a
    freshly derived box and a restored one take this form, because the restored one has no
    solids to compare against."""
    return box._replace(pack=box.pack._replace(placed={}))

# What a box is built AROUND: the placed bodies, and every station they put on a wall.
# A pack that does not carry a subsystem yet carries no stations for it, and the wall
# comes out blank there rather than carrying a hole with nothing behind it. A Box stands
# one of these and reads its stations through it.
#   placed        {name: (solid, colour)} — the same shape a CadQuery assembly reads
#   front_ports   / back_ports   wall through-holes, in the pack's format
#   east_ports    +X side-wall through-holes, (kind, y, z, *size)
#   west_ports    −X side-wall through-holes, same shape — the ASSE drip pan's slot
#   funnel        the placed funnel's plan centre, or None for no throat
#   pan_sleeve    the ASSE drip pan's carry, `(adds, cuts)` of world boxes — the solid block fused
#                 onto the −X wall, and the berth cut back out of it
#   c14           the mains inlet's heat-set stations on the +Y wall of back-top, (x, z)
#   east_bosses   the +X wall's mounting bosses, (y, z, the plane the boss top reaches, the
#                 X plane its underside corbel reaches, optional clear Y bands where it reaches
#                 the mounting plane after all). The X planes normally agree. A body crossing
#                 only part of the candidate wedge holds that part back by
#                 `east_boss_corbel_clear`; the clear bands keep their wall-rooted corbel all
#                 the way to the body, and the D-shaped stem still reaches the whole hole
#   side_wells    the side walls' Wago wells, (side, y, z, size, clear_z) — one press-fit pocket
#                 per lever nut, on the flank its own cluster stands on
#   floor_bosses  the floor slab's mounting bosses, (x, y, the plane the boss top reaches, the
#                 section the donor's own bore leaves the post standing in it)
#   west_cradle   the −X strip's MQ-6 card slot, (x, y, z) — the card's own mid-plane, and its
#                 centre along the strip and in height. The can's silhouette is read off the
#                 reference module round that centre, and is what the flank wells
#   cond_cradle   the front wall's condenser rails, one (face, x0, x1, fz0, fz1, root) per fore
#                 flange — the plane the block's fore face rests on, that flange's width, its
#                 two faces in height, and how far the rail runs down under it
#   cond_mount    the condenser's aft mount, (flank, y0, y1, bosses) — the fin's own west face,
#                 the Y band it stands in, and one (x, y, the flange face it reaches) per hole
#   cond_airway   the condenser's own airway, (y0, y1, z0, z1) — the finstack's footprint on
#                 either flank, which is the band the ±X vents are pierced over. The recesses
#                 at each Y end are not in it: they are the sheet the box holds the block by
#                 and the fan draws through neither
#   asse_cradle   the −X wall's tap-water cradle, (axis_z, sections, ties, reach_down) — the
#                 axis the ASSE anchor is struck on, one (y0, y1, apex_x) per section of the chain,
#                 the Y of each tie band, and how far under the axis its flanks run
#   flow_meter_anchors  the top wall's two flow-meter anchors, (axis_x, axis_z, seat_r, bands) —
#                 the arm axis the Vs are struck on, the barrel they seat, and the run of
#                 each arm one takes
#   tube_anchors  the runs' own seats, one (mid, along, root, seat_r) each — the middle of the
#                 leg a rib is centred on, which way the tube points there, which way the face
#                 it stands on lies, and the section it seats
#   ceiling_reliefs  the purchased bodies' pockets in the ceiling panel's structural field,
#                 one `(name, x0, x1, y0, y1, pocket_top_z)` each. The plan is the body's exact
#                 intersection with that field plus assembly slip; the last number is the roof
#                 left over it. This is geometry struck by the pack, not another placement.
#   ceiling_growth_reliefs  the exact plan bands where fixed purchased bodies need the added
#                 three-millimetre ceiling-strip growth removed while retaining the established
#                 printable wedge below them, one `(name, side, x0, x1, y0, y1)` each
#   port_field    the pockets the +Y wall of back-top's outer face carries and the bosses behind them,
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
#   valve_trays   the flavour manifold's decks, one (plane, sign, seats) each — the world Y a
#                 deck's valves stand their mounting faces on, which way their own +Z runs off
#                 it, and one (x, z) per valve. A valve tray is a plate wall to wall carrying one
#                 four-boss `valve_seat` per valve (`valve_tray`), and it is this piece's own
#                 material the way the ASSE anchor and the flow-meter anchors are
#   pump_trays    the flavour manifold's two pump stations, one world `centre` each — the point
#                 a pump's own axis meets the +Z face of its head. The legacy field name is kept
#                 at the assembly boundary; the lower cradle and top clamp are built from these
#                 stations and from `pump_tray`'s case-derived collar section
#   core_stops    the cold core's two front corners, one (cx, cy, r, tip) each — the centre and
#                 radius of the core's own corner round, and the plane the block over it reaches
#   core_holds    the cold core's two hold-downs, one (x0, x1, aft, crown) each — the lane on the
#                 cap a bracket stands in, the core's aft face, and the plane its cap presents
#   vent_chase    the cold core's PRV relief line, one (x, y, z) — the core's west flank, which
#                 the chase's lip lands on, and the tube's own axis where it comes through
#   collet_plate  the steel plate the barb tubes release against, as the dict
#                 `enclosure_assembly.collet_plate_spec` strikes off the four anchor tees'
#                 branch collets: its two Y faces, its Z band, its X ends, and one (x, z)
#                 per hole. The bay floor's slot takes it (`_plate_slot`)
Pack = namedtuple(
    "Pack", "placed front_ports back_ports east_ports west_ports funnel pan_sleeve c14 "
            "east_bosses side_wells floor_bosses west_cradle cond_cradle cond_mount "
            "cond_airway asse_cradle flow_meter_anchors tube_anchors ceiling_reliefs "
            "ceiling_growth_reliefs "
            "port_field nameplate keystone "
            "valve_trays pump_trays core_stops core_holds vent_chase collet_plate")
Pack.__new__.__defaults__ = (
    (),             # front_ports
    (),             # back_ports
    (),             # east_ports
    (),             # west_ports
    None,           # funnel
    (),             # pan_sleeve
    ((), ()),       # c14
    (),             # east_bosses
    (),             # side_wells
    (),             # floor_bosses
    (),             # west_cradle
    (),             # cond_cradle
    (),             # cond_mount
    None,           # cond_airway
    (),             # asse_cradle
    (),             # flow_meter_anchors
    (),             # tube_anchors
    (),             # ceiling_reliefs
    (),             # ceiling_growth_reliefs
    (),             # port_field
    None,           # nameplate
    None,           # keystone
    (),             # valve_trays
    (),             # pump_trays
    (),             # core_stops
    (),             # core_holds
    (),             # vent_chase
    None,           # collet_plate
)


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


def _y_wall_corbel(stock, fore, wall):
    """A 45 degree underside carrying ``stock`` from its free face back to a +Y wall.

    THE SUPPORT IS A SHEARED COPY OF THE SHAPE IT CARRIES, not a prism struck on that
    shape's bounding box. At ``fore`` the copy coincides with ``stock``; toward ``wall`` it
    falls one millimetre in Z for every millimetre in Y. Fusing the two therefore puts
    material directly under every point of the lower outline — including a rounded corner —
    while presenting one 45 degree underside to the bed. A square prism under a rounded
    outline instead leaves a flat ledge with an air channel above it at every lower corner.
    """
    if wall <= fore:
        raise ValueError(f"a +Y-wall corbel runs from {fore:g} to {wall:g}, not toward its wall")
    shear = cq.Matrix([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, -1.0, 1.0, fore],
    ])
    return stock.transformGeometry(shear)


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


def _xy_prism(z0, z1, section):
    """A prism along Z from z0 to z1, whose `section` is a closed `(x, y)` polygon.

    The third of the trio, and the one a feature drawn IN PLAN wants — a wall raked about a
    standing vertical is one line in this section and a fitted surface in either other."""
    return (
        cq.Workplane("XY")
        .polyline(list(section)).close()
        .extrude(abs(z1 - z0))
        .val()
        .translate((0.0, 0.0, min(z0, z1)))
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
    wrap = _lip_band(inner, (inner[4], zj + z_rise)).intersect(
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


def _column_relief(inner, sx, sy, room, zj):
    """One column's pocket for the body standing in it. Clipped to the PILLAR — the column and
    the lip's skin wrapping it (`_column_pillar`) — so what a pocket can ever take is that and
    never the wall behind it or the boss beside it."""
    return _ybox(*room).intersect(_column_pillar(inner, sx, sy, zj))


def _column_relief_rise(inner, sx, sy, room, zj):
    """The walk one pocket's CEILING takes into the column over it, and the piece that decides
    how much of it survives.

    A POCKET IS A BITE OUT OF A CORNER, and the corner is where its material is: the two faces
    toward it have column under them the whole height, and the two away from it open on the
    cavity. Cut flat, the ceiling is a shelf hanging off that corner. Walked in off both HELD
    faces at `relief_chamfer` it stands one millimetre higher for every millimetre it reaches
    away from one, and the column closes back over the pocket a layer at a time. Its height is
    the pocket's own plan: at `min(width, depth)` the two walks have met.

    IT IS CUT BEFORE THE PIECE FUSES ANYTHING AND AGAIN WITH THE POCKET AFTER EVERYTHING. The
    first cut walks the shell itself; the second walks any rail or boss that subsequently grew
    over that same air. This makes the final ceiling a question about the finished piece rather
    than a figure a row carries, and prevents an overlapping feature from restoring a short flat
    roof over the pocket."""
    x0, x1, y0, y1, _z0, z1 = room
    held_x, free_x = (x1, x0) if sx > 0 else (x0, x1)
    held_y, free_y = (y1, y0) if sy > 0 else (y0, y1)
    return (_xz_prism(y0, y1, [(free_x, z1), (held_x, z1), (free_x, z1 + abs(x1 - x0))])
            .intersect(_yz_prism(x0, x1,
                                 [(free_y, z1), (held_y, z1), (free_y, z1 + abs(y1 - y0))]))
            .intersect(_column_pillar(inner, sx, sy, zj)))


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
    clear of the arc entirely and answers to the +Y wall itself.

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


def front_band_free_y(front_face):
    """The FRONT half's free run of the ±X boss-chain bands, as `(y0, y1)` — the run
    `east_band_free_y` says this half has and is not.

    ITS ENDS ARE THE FRONT WALL AND THE Y SEAM'S OWN CORNER. The Z seam stands no collar
    in this band any more: the rail is the seam's furniture on a flank, it lives in the
    seam's own `z_seam..z_seam + z_rise` storey, and a body under the mouth never meets
    it — `z-slide-lanes` is what reads a body that stands up into the storey the slide
    sweeps. So the run is the whole flank, front face to the Y boss's fore face.

    IT TAKES THE FRONT FACE because it cannot state it. The back half's two ends are both
    struck on planes the box states about itself — `y_seam` and `rear_plane_y` — but the front
    wall stands off whatever the pack puts nearest it, so a caller reading this before the box
    is sized has to say what that is. Everything after it is the same stated chain `_dims`
    builds the wall on."""
    iy0 = front_face - front_seam_clear
    return (iy0, _y_boss(y_seam) - socket_r)


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
    BUILD them (`_bosses`, `_y_corner`, `_z_rail_runs`), so a footprint cannot drift from
    the geometry it stands for.

    THE HEIGHT IS HALF THE ANSWER. A body hung on a flank clears a boss by standing beside it
    or by standing over it, and a reading with no z in it can only see the first — it would
    charge a body the whole height of a wall for a collar 16 mm tall. Between two bosses, and
    above and below every one of them, the band is the wall's own air.

    THE RAILS ARE IN THE ANSWER TOO. Each column's hooked rail runs its flanks' straight
    runs over the seam's own storey, mouth to rim. Both carry their full nominal foot first
    and place the hook at that foot's inboard edge. Both remain inside `side_band_inset`, so
    the band the pack keeps covers them. A row per column says so, at the run each column's
    rail actually takes."""
    r = socket_r
    yb0, yb1 = _y_corner(inner, y_joint)
    out = [(yb0, yb1, z - r, z + r)
           for _x_in, _x_ext, _sx, z in _bosses(inner, y_joint)]
    for col, zj in (("front", splits[0]), ("back", splits[1])):
        for _x_in, _sx, ry0, ry1, _lane in _z_rail_runs(inner, y_joint, col, None):
            out.append((ry0, ry1, zj, zj + z_rise))
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

    The bottom piece runs the floor slab's underside to its seam RIM (`zj + z_rise`,
    where the station collars stop too); the top piece runs the seam plane to the top
    wall's outer face. Both print standing on a Z face, so the bed's Z bounds each of
    them, and each bound is one end of this band."""
    oz0, oz1 = inner[4] - floor_t, inner[5] + wall
    return oz1 - H2C_Z, oz0 + H2C_Z - z_rise


def _lip_band(inner, z, inset=0.0):
    """The Z-seam lip's own shape over a height span: the cavity's one-`wall` skin.

    `inset` pulls the skin's OUTER surface inboard and keeps its inner one — the lip the
    box builds stands `slide_slip` off every face the top piece slides along, because a
    slide the length of a column cannot run printed face on printed face the way a 13 mm
    drop could. The nominal skin (inset 0) is what the measures read: it is the lane the
    seam OWNS, a hair wider than the lip standing in it, conservative the way a probe
    should be.

    THE LIP IS NOT A BOX. It is struck as the cavity's skin (`_cavity`), so it carries the
    wall rounds at the standing verticals and WRAPS whatever column stands in one — the
    pillar telescopes into the piece above on the same one wall of overlap every other face
    uses. A rectangular band drawn to the same figures is neither: it reaches into corners
    the cavity has rounded away, and it misses the wrap entirely, which is the part that
    stands furthest inboard.

    `_lip_underwall` is struck from this same figure, so the wall below the mouth and the
    measures that read the seam's lane come off one shape."""
    z0, z1 = z
    return _cavity(inner, inset, (z0, z1)).cut(_cavity(inner, wall, (z0 - 1.0, z1 + 1.0)))


def _lip_denied(placed, inner, y_span, plate, y_joint):
    """The seam heights the pack denies ONE Y column's Z seam, as z spans.

    The seam's furniture on a flank is the RAIL: groove, arm and head together span
    `rail_reach_in` from `interior_x` over the seam's own storey, on the runs that column's
    rails take, wherever the seam lands. Both channel walls follow the inboard portion of
    their full nominal feet. So the lane measured is the actual profile on those runs, over
    the full height of the box — and a body standing in one
    denies the seam heights that would put the slide through it: from `z_rise` under its foot (the
    rim would be below it) to one `rail_flare_drop` over its crown, which is how far the arm's
    under-flare hangs below the seam and therefore how high above a crown a seam can still drop
    rail through it.

    A Z SEAM IS PER Y COLUMN AND SO IS ITS LANE. `y_span` is that column's half, cut
    at the Y joint; a body spanning the joint is charged to both columns, as it
    should be. What holds the rest of the lane open is the pack's own standoffs —
    `side_band_inset` at the flanks, which the rail stands inside."""
    ix0, ix1, _iy0, _iy1, iz0, iz1 = inner
    cy0, cy1 = y_span
    col = "front" if cy1 <= y_joint + 1.0 else "back"
    ring = None
    for x_in, sx, ry0, ry1, _lane in _z_rail_runs(inner, y_joint, col, plate):
        ya, yb = max(ry0, cy0), min(ry1, cy1)
        if yb <= ya + 1e-6:
            continue
        x_hk, _x_f, _x_a, x_h1 = _rail_x(x_in, sx, col)
        x_open = x_hk - sx * slide_slip
        lane = _ybox(min(x_open, x_h1), max(x_open, x_h1),
                     ya, yb, iz0, iz1)
        ring = lane if ring is None else ring.fuse(lane)
    out = []
    if ring is None:
        return out
    for solid, _c in placed.values():
        hit = ring.intersect(solid)
        if hit.Volume() > 1.0:
            b = hit.BoundingBox()
            out.append((b.zmin - z_rise, b.zmax + rail_flare_drop))
    return out


# Which columns' Z seams run THROUGH their own bodies rather than land in a band those
# bodies leave open. Filled by `_z_joints`, printed by main().
_z_seam_passes = {}


def _z_joints(placed, inner, stated, plate, y_joint):
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
        f"{iz1 - iz0 + floor_t + wall:.2f} mm column, band {bed_lo:.2f}..{bed_hi:.2f}",
        f"a band inside the H2C's {H2C_Z:g} mm Z",
        ([] if bed_hi >= bed_lo else [
            f"a {iz1 - iz0 + floor_t + wall:.2f} mm column has no seam height leaving two pieces "
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
        lanes = _open_bands(_lip_denied(placed, inner, y_span, plate, y_joint),
                            bed_lo, bed_hi, 0.0)
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
    _wall_block.clear()
    _z_seam_passes.clear()
    placed = pack.placed
    bbs = [_boxes.boxed(s) for s, _c in placed.values()]
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
    iz0 = min(czmin, 0.0)
    iz1 = (iz0 - floor_t) + appliance_height - wall
    inner = (ix0, ix1, iy0, iy1, iz0, iz1)
    y_joint = y_seam
    splits = _z_joints(placed, inner, z_seam, pack.collet_plate, y_joint)
    # THE RIM'S OWN CEILING. Wall-rooted furniture stands on a piece's wall, and below the
    # rim the wall's inner face is the bottom piece's lip — so a valve tray's seat plate
    # spans wall to wall whole above the rim, and its FOOT runs below it inset on the lip's
    # own face (`_valve_trays`). The lip's ring cannot read one: it is printed material,
    # not pack, and a plate standing ON the rim is a touch with no volume in it. This reads
    # the wall-to-wall storeys off the same stations the pieces build them from. The bay's
    # floor is the one span that does stand on the rim and answers elsewhere
    # (`enclosure_assembly.check_bay_floor`); the pump clamp's collar storey belongs to the
    # removable assembly, so no fixed wall carries it.
    rim = max(splits) + z_rise
    decks = [mz - _valve_tray.height() / 2.0
             for _plane, _sign, seats in pack.valve_trays
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
    # the band is the wall's own air, and a body clear of all of them answers on its own reach.
    #
    # EVERY TERM CARRIES THE BODY IT CAME OFF, and on this axis both of them close flush. The
    # cold core packs its `side_band_inset` off `interior_x` on the slab, and the Wago wells
    # bore through the thickened ±X flanks to bottom on `interior_x` itself
    # (`front_top_flank_t`, `front_bottom_flank_t`), so a lever nut's back face IS that plane.
    # A reading with no air in it is a seat, and the name beside it is what says which.
    floor = [(n, b) for n, b in zip(placed.keys(), bbs)
             if b.zmin < wall + 1e-6 and _in_a_boss(b, band_bosses)]
    wide_need, wide_who = max(
        [(max(b.xmax, -b.xmin), n) for n, b in zip(placed.keys(), bbs)]
        + [(max(b.xmax, -b.xmin) + side_band_inset, n) for n, b in floor])
    record_bound(Bound(
        "box-width", "The pack stands inside the appliance's stated width",
        wide_need <= ix1 + stated_bound_tol,
        f"pack reaches x ±{wide_need:.2f} at {wide_who}, wall at ±{ix1:.2f}",
        f"inside a {appliance_width:g} mm appliance",
        ([] if wide_need <= ix1 + stated_bound_tol else [
            f"the pack reaches x ±{wide_need:.2f} but a {appliance_width:g} mm appliance walls "
            f"in at ±{ix1:.2f} — {wide_need - ix1:.2f} mm over. Raise `appliance_width` or "
            f"repack inboard"])))
    # AND BACK-TOP'S OWN FLANKS STAND FURTHER IN THAN THAT. `back_top_flank_face` is
    # `back_top_flank_t - wall` inboard of `interior_x` on that one piece, so a body that clears
    # the appliance's width can still be standing in its wall — and `box-width` cannot see it,
    # because the width it reads is the box's own. What this section may stand in is what the
    # wall gives a LANE to and nothing else: a Wago in its own well, bored back to `interior_x`,
    # whatever lies in the ASSE drip pan's sleeve, and the named run in
    # `back_top_flank_reliefs`. A body is matched to a geometric well by its CENTRE; the named
    # route relief is verified against the exact finished piece by `pack-closes`, so this
    # pre-piece ledger recognizes its intent without pretending the nominal face remains there.
    bt0, bt1 = back_top_flank_face()
    bt_y0 = y_joint + lip_len + z_lip_y_margin
    bt_z0 = splits[1] + z_rise
    lanes = ([(sy - hy, sy + hy, sz - hz, sz + hz)
              for _sd, sy, sz, size, _cz in pack.side_wells
              for hy, hz in (wago_half(size),)]
             + [(by0, by1, bz0, bz1) for _bx0, _bx1, by0, by1, bz0, bz1 in pack.pan_sleeve[0]])
    relieved_names = {who for who, _side, _y0, _y1, _z0, _z1
                      in back_top_flank_reliefs}
    flank_rows = []
    for name, b in zip(placed.keys(), bbs):
        if b.ymax <= bt_y0 or b.zmax <= bt_z0:
            continue
        if name in relieved_names:
            continue
        cy, cz = (b.ymin + b.ymax) / 2.0, (b.zmin + b.zmax) / 2.0
        if any(ly0 <= cy <= ly1 and lz0 <= cz <= lz1 for ly0, ly1, lz0, lz1 in lanes):
            continue
        flank_rows.append((max(bt0 - b.xmin, b.xmax - bt1), name))
    flank_rows.sort(reverse=True)
    flank_over, flank_who = flank_rows[0] if flank_rows else (-bt1, "nothing")
    flank_ok = flank_over <= stated_bound_tol
    record_bound(Bound(
        "back-top-flank-clear", "The pack stands clear of back-top's own flank face", flank_ok,
        f"least air {-flank_over:.2f} mm, at {flank_who}",
        f"outside x ±{bt1:.2f}, a {back_top_flank_t:g} mm flank",
        ([] if flank_ok else [
            f"{flank_who} stands {flank_over:.2f} mm inside back-top's flank at ±{bt1:.2f}. "
            f"Give it a lane the way the tray's sleeve has one, seat it in a well, or lower "
            f"`back_top_flank_t`"])))
    # The FRONT wall is the stated `front_plane_y` with its stated reliefs, and the pack is
    # read against the RELIEVED surface, body by body: a body whose footprint stands wholly
    # inside a relief answers to that relief's floor, and every other body to the plane
    # itself. The compressor's reading is its stated kiss on the refrigeration bay's floor.
    #
    # The +Y wall is the stated `rear_plane_y`, for the same reason the ceiling is the
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
    rear_need, rear_who = max((b.ymax + rear_seam_clear, n)
                              for n, b in zip(placed.keys(), bbs))
    record_bound(Bound(
        "box-depth", "The pack stands inside the appliance's stated depth",
        rear_need <= iy1 + stated_bound_tol,
        f"pack reaches y {rear_need:.2f} at {rear_who}, +Y wall at {iy1:.2f}",
        f"ahead of `rear_plane_y` {rear_plane_y:g}",
        ([] if rear_need <= iy1 + stated_bound_tol else [
            f"the pack reaches y {rear_need:.2f} but the +Y wall stands at {iy1:.2f} — "
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
    need = max(czmax, wall_band_top + pod_stack)
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
    outer = (ox0, ox1, oy0, oy1, iz0 - floor_t, iz1 + wall)
    # The one thing the Y seam cannot do is cut the display housing: the facet is a
    # solid surface chamfered into the top-front arris and it prints as part of the
    # front-top piece, so the seam stands behind its back plane.
    # NOTHING RELIEVES INTO THE OUTERMOST `flute_backing` OF A FLUTED FACE. This is the rule the
    # whole skin stands on and the one a reader would otherwise have to take on trust.
    sections = flute_backed_sections()
    thin = [(what, mm) for what, mm in sections if mm < flute_backing - stated_bound_tol]
    record_bound(Bound(
        "flute-backed", "Every fluted face keeps a whole wall behind its grooves", not thin,
        f"thinnest of {len(sections)} stated sections is "
        f"{min(mm for _what, mm in sections):.4f} mm",
        f"at least {flute_backing:g} mm",
        [f"{what} carries {mm:.4f} mm, so a {flute_depth:g} mm groove leaves "
         f"{mm - flute_depth:.4f} behind it" for what, mm in thin]))
    # AND WHAT BACKS THE TOP OF THE FRONT FACE is the display's own plain border, because the
    # inset's down-slope end wall and the facet's arris close on each other at 45°. This is the
    # thinnest station on a fluted face that is not a stated relief, so it is read rather than
    # assumed.
    arris_back = display_facet_buffer * math.sqrt(2.0)
    record_bound(Bound(
        "facet-arris-backed", "The front face keeps a wall behind it at the facet's arris",
        arris_back >= flute_backing - stated_bound_tol,
        f"{arris_back:.4f} mm of ligament, from a {display_facet_buffer:g} mm plain border",
        f"at least {flute_backing:g} mm",
        ([] if arris_back >= flute_backing - stated_bound_tol else [
            f"the front face closes to {arris_back:.4f} mm under the facet's arris, where a "
            f"{flute_depth:g} mm flute would leave {arris_back - flute_depth:.4f}. "
            f"`display_facet_buffer` wants at least "
            f"{flute_backing / math.sqrt(2.0):.4f}"])))
    # THE REEDED SKIN CLOSES ON THE BOX. `flute_count` is a whole number of grooves round the
    # whole outer plan, so the field has no station where it restarts and no seam where two
    # arrays meet — but the pitch that count lands on is a CONSEQUENCE and not a choice, and it
    # has to stay the coupon's or this box is not carrying the texture that was settled on.
    pitch = flute_pitch(outer)
    drift = abs(pitch - reeding.flute_pitch)
    record_bound(Bound(
        "flute-closes", "The reeded field closes on the box at the coupon's own pitch",
        drift <= flute_pitch_drift,
        f"{flute_count} grooves round {plan_perimeter(outer):.2f} mm, {pitch:.4f} mm centres",
        f"within {flute_pitch_drift:g} mm of the coupon's {reeding.flute_pitch:g}",
        ([] if drift <= flute_pitch_drift else [
            f"the field lands on {pitch:.4f} mm centres, {drift:.4f} off the coupon's "
            f"{reeding.flute_pitch:g}. `flute_count` wants to be near "
            f"{plan_perimeter(outer) / reeding.flute_pitch:.1f}"])))
    # AND IT PUTS THE Y SEAM IN A GROOVE. That seam is the one straight line running the full
    # height of both side walls, and it runs ALONG the flutes rather than across them — so it
    # can be put where a joint reads as the shadow already there instead of a line on a flat.
    # This is what picks one `flute_count` out of the several that close near the coupon's
    # pitch, and without it the choice would be arbitrary.
    segments = _plan_segments(outer)
    seam_arc = segments[0][1] + segments[1][1] + (y_joint - (outer[2] + corner_round))
    miss = min(seam_arc % pitch, pitch - seam_arc % pitch)
    record_bound(Bound(
        "flute-hides-seam", "The Y seam runs down a groove, not across a land",
        miss <= flute_seam_miss,
        f"{miss:.4f} mm off a groove centre, in a groove {reeding.flute_width:g} mm wide",
        f"within {flute_seam_miss:g} mm of a centre",
        ([] if miss <= flute_seam_miss else [
            f"the Y seam lands {miss:.4f} mm off the nearest groove centre, which puts the "
            f"joint on a land where it is a line on a flat. Retune `flute_count`"])))
    # AND THE PUMP BAY'S INTERIOR THROAT TAKES THE COMPLETE CAVITY WIDTH. The removable
    # cartridge continues out through both former side skins; this bound names only the
    # unobstructed interior planes, while `pump-cartridge-full-front-wall` reads ownership of
    # the complete exterior front-wall band from the built solids.
    bx0, bx1 = bay_x_span(inner)
    record_bound(Bound(
        "pump-bay-cavity-throat", "The pump bay throat reaches both cavity side planes",
        abs(bx0 - inner[0]) <= stated_bound_tol and abs(bx1 - inner[1]) <= stated_bound_tol,
        f"bay x {bx0:.3f}..{bx1:.3f}, cavity x {inner[0]:.3f}..{inner[1]:.3f}",
        "the same two planes",
        ([] if (abs(bx0 - inner[0]) <= stated_bound_tol
                and abs(bx1 - inner[1]) <= stated_bound_tol) else [
            "a fixed jamb stands inside a cavity plane and narrows the withdrawal throat. "
            "Carry `bay_x_span` to the cavity's complete X span"])))
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
            "or seat it on `lip_face_x` the way the MQ-6's can is"])))
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

    # THE PUMP BAY: the complete span between the side-wall interior planes, topped one
    # `bay_crown_air` over the tallest motor can's crown — what the pump cartridge leaves
    # through, struck off the placed cans the way every station is struck off its body.
    bx0, bx1 = bay_x_span(inner)
    crowns = [b.zmax for name, b in zip(placed.keys(), bbs)
              if name.startswith("pump-") and name.endswith("-motor")]
    pump_bay = (bx0, bx1, max(crowns) + bay_crown_air) if crowns else None
    # The wall-block probes above are solids and deliberately do not escape this placement
    # pass. What the drawing needs from them is the numeric ladder they admitted; carry that
    # ladder on the Box so a downstream action can reproduce the same joint without the pack.
    y_bosses = tuple(_bosses(inner, y_joint))
    z_passes = tuple(_z_seam_passes[col] for col in ("front", "back"))
    return Box(pack, inner, outer, y_joint, splits, y_bosses, z_passes,
               tuple(reliefs), pump_bay)


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


def flank_x_at(y, outer):
    """The ±X exterior SURFACE's own distance from x = 0 at depth `y` — the wall's plane down
    the flat, and `corner_round`'s arc wherever the turn has begun.

    A BORE STRUCK ON A PLANE LEAVES LESS BEHIND A TURN. `interior_x` stands one `wall` in from
    the flat, so anything run to it leaves exactly `wall` down the middle of a face and less
    than that anywhere the round has carried the surface inboard. What has to leave a stated
    section behind the surface — `flute_backing` above all, since a flute is cut into that
    same surface — reads this and not the plane."""
    ox1, oy0, oy1 = outer[1], outer[2], outer[3]
    if oy0 + corner_round <= y <= oy1 - corner_round:
        return ox1
    off = min(abs(y - (oy0 + corner_round)), abs(y - (oy1 - corner_round)), corner_round)
    return (ox1 - corner_round) + math.sqrt(corner_round ** 2 - off ** 2)


def _plan_segments(outer):
    """The outer plan boundary as (kind, length, data), walked from the FRONT WALL'S
    CENTRELINE heading +X — four straight runs and the four `corner_round` quarter turns
    between them, in order, each carrying its own length so a walk is an arc-length walk.

    THE DATUM IS x = 0 ON THE FRONT WALL, which is the plane the whole machine is struck
    about. A field whose datum sits there is symmetric in x whatever its pitch, because the
    half-perimeter either way round is the same walk mirrored.

    There is no turn at the Y seam and none is wanted: that arris is a telescoping mating
    face, square by construction (`_round_z`), and the two pieces that meet on it present one
    continuous plan between them."""
    ox0, ox1, oy0, oy1 = outer[0], outer[1], outer[2], outer[3]
    r = corner_round
    run_x = (ox1 - ox0) - 2.0 * r
    run_y = (oy1 - oy0) - 2.0 * r
    turn = math.pi * r / 2.0
    return (
        ("line", run_x / 2.0, ((0.0, oy0), (1.0, 0.0), (0.0, -1.0))),
        ("arc", turn, ((ox1 - r, oy0 + r), -math.pi / 2.0, r)),
        ("line", run_y, ((ox1, oy0 + r), (0.0, 1.0), (1.0, 0.0))),
        ("arc", turn, ((ox1 - r, oy1 - r), 0.0, r)),
        ("line", run_x, ((ox1 - r, oy1), (-1.0, 0.0), (0.0, 1.0))),
        ("arc", turn, ((ox0 + r, oy1 - r), math.pi / 2.0, r)),
        ("line", run_y, ((ox0, oy1 - r), (0.0, -1.0), (-1.0, 0.0))),
        ("arc", turn, ((ox0 + r, oy0 + r), math.pi, r)),
        ("line", run_x / 2.0, ((ox0 + r, oy0), (1.0, 0.0), (0.0, -1.0))),
    )


def _bay_storey_segments(inner, outer, bay, plate):
    """The phase path round the INSIDE of the bay's storey, from −X mouth edge to +X.

    IT IS THE OPEN BOX'S PLAN WALKED INDOORS. Material on the left, so the normal it hands
    back points into the room: the two front-wall cut edges, the two open flanks and the tee
    wall between them. Every segment carries its own length, so this is an arc-length walk
    like the closed outer field even though this run has no corner turns.

    ITS DATUM IS x = 0 ON THE TEE WALL — the plane the whole machine is struck about, and the
    same plane the outer plan's datum stands on, so both fields put a groove there and each is
    symmetric in x about it. It is walked from the middle out (`flute_rails`), which is why
    the segments read from one mouth edge straight through to the other.

    ITS TWO LONG OUTBOARD STRETCHES ARE AIR. From the front-wall interior plane to the tee wall
    the side wall is cut away over this whole storey (`_bay_cut`), so these two segments carry
    the global arc coordinate across each window but never become flute rails. The central
    segment carries phase across the lower tee face, which is berthed or hidden; above it the
    final closure face is on another Y plane. `flute_rails` therefore strikes only two separate
    open runs, one on each actual mouth ledge.

    AND IT DOES NOT CLOSE. What lies between the two mouth edges is the drawer, not a surface; a run
    stops at its own two ends and the field ramps out on them the way it ramps out on any edge,
    which is what keeps the flutes off the mouth arris (`flute-clears-jamb`)."""
    bx0, bx1 = bay_x_span(inner)
    fore = inner[2]                        # the flank opening begins on the front-wall plane
    aft = plate["aft_y"]                   # the tee wall's fore face, the storey's back
    ledge = bx0 - outer[0]                 # exposed front-wall section, mouth to exterior
    window = aft - fore
    return (
        ("line", ledge, ((bx0, fore), (-1.0, 0.0), (0.0, 1.0))),
        ("line", window, ((outer[0], fore), (0.0, 1.0), (1.0, 0.0))),
        ("line", outer[1] - outer[0], ((outer[0], aft), (1.0, 0.0), (0.0, -1.0))),
        ("line", window, ((outer[1], aft), (0.0, -1.0), (-1.0, 0.0))),
        ("line", ledge, ((outer[1], fore), (-1.0, 0.0), (0.0, 1.0))),
    )


def seam_cap_z():
    """THE PLANE THE Z SEAM'S OWN FURNITURE TOPS OUT UNDER, one `wall` over the lip rim.

    Under it stand the lip, the rail heads, the stop blocks and every lane the top piece
    sweeps them in; over it front-bottom stands nothing at all. So it is the plane a body
    riding in front-top has to be above before it may reach out to the side wall, and the
    floor the bay's interior flute storey is struck on. Across the removable front band the
    cradle replaces this closure; aft of the opening the ordinary seam furniture remains."""
    return z_seam + z_rise + wall


def plate_step_in():
    """HOW FAR EACH END OF THE COLLET PLATE STANDS IN FROM THE CAVITY-SIDE WALL.

    THE PLATE COMES THROUGH FRONT-TOP'S Z− FACE. It has no X travel and its slot has no
    reason to open into the side-wall bays above the lead-in. The steel therefore takes the
    cavity width less one substantial printed return at each end: `plate_end_stock` of solid
    between the slot and `interior_x`, plus `plate_slot_slip` between that solid and the cut
    steel. On this box that puts the plate ends at x = ±100.000, the slot ends at ±100.200,
    4.300 mm of printed material inboard of each cavity wall, and the enclosure's own 3 mm
    wall beyond it.

    THE RECTANGLE KEEPS THAT WIDTH OVER ITS WHOLE HEIGHT. Its four holes remain on their
    pack-struck X/Z datums, while each widened unperforated tail bears on ten millimetres of
    fixed Y− cheek. The front column's rails begin aft of the tee wall; the plate and its
    insertion slot stand fore of that run and do not spend their width on rail clearance."""
    return plate_end_stock + plate_slot_slip


def plate_outline(plate):
    """THE COLLET PLATE'S OWN OUTLINE, as an `(x, z)` polygon — the one figure the steel, the
    cut file and every body that stands beside it read.

    IT IS A RECTANGLE. Every plane it stands on is one the box already has: `plate_step_in`
    off each side wall at every height, `z_seam` under it, and over it the height that
    centres the four collet holes in the band.

    NOTHING IS CUT OUT OF IT. A notch in a part is a thing something else is standing in, and
    after the flip there is nothing standing in this one: what stops the steel is its own TOP
    EDGE on `_plate_cap`'s land, so the outline owes the stop no shoulder; the lane its bottom
    edge needs is the lane the whole part travels, so the ends owe the joint no step; and over
    `seam_cap_z` the flank comes in to the steel rather than the steel out to the flank. Four
    corners and four holes."""
    x0, x1, z0, z1 = plate["x0"], plate["x1"], plate["z0"], plate["z1"]
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]


def bay_storey_z(bay):
    """The interior bay-surround band carrying its own flute run.

    The removable cradle itself begins lower, on the bay floor. This narrower band begins at
    the seam furniture's ceiling because that is where an exposed interior surround exists
    behind the installed cradle."""
    return seam_cap_z(), bay[2]


#: A run's point and outward normal at an arc length — `flute_skin.walk`, which is where it
#: lives because the cold core's skin is struck along runs of the same kind.
_walk = _flute_skin.walk


def plan_perimeter(outer):
    """How far it is round the box's outer plan once — what `flute_count` divides."""
    return sum(length for _kind, length, _data in _plan_segments(outer))


def flute_pitch(outer):
    """The spacing the field actually lands on. It is a CONSEQUENCE of `flute_count`, not a
    figure of its own, because a stated pitch would leave the perimeter with a remainder and
    the remainder has to go somewhere — one wrong land, at whichever station the array
    happened to close on. `flute-closes` is what holds it near the coupon's."""
    return plan_perimeter(outer) / flute_count


def plan_at(s, outer):
    """The outer plan boundary's point and OUTWARD normal at arc length `s` from the datum.

    THE PLAN CLOSES, so any `s` is on it: the walk is taken modulo the perimeter and the box
    has no station where the field restarts."""
    segments = _plan_segments(outer)
    return _walk(segments, s % sum(length for _k, length, _d in segments))


def flute_rails(box, berthed=()):
    """Every run this box's field is struck along.

    THE OUTER PLAN IS ONE OF THEM. The bay storey's two mouth ledges are two more open rails;
    its intervening windows and hidden tee span only advance the global arc coordinate
    (`_bay_storey_segments`). Every surface is struck at the same `flute_pitch` from a datum on
    x = 0, so each keeps the same phase and neither is told the other exists.

    `berthed` is what the assembly stands in that storey — the lower cradle, top clamp and steel
    plate. What a fitted body hides is not show face and gets no flutes
    (`flute_skin._shadow_mask`); which of them hides what is measured, not listed."""
    outer = box.outer
    rails = [_flute_skin.Rail(at=lambda s: plan_at(s, outer),
                              length=plan_perimeter(outer))]
    if box.pump_bay and box.pack.collet_plate:
        segments = _bay_storey_segments(box.inner, outer, box.pump_bay, box.pack.collet_plate)
        run = sum(length for _kind, length, _data in segments)
        cursor = -run / 2.0
        # Segments 1 and 3 cross the two open flanks, and segment 2 crosses the lower tee face
        # hidden by the installed cartridge/plate. They preserve phase between the two real
        # mouth ledges but are not cutter paths: late-fused guide and cap faces stand on their
        # opposite sides. Each ledge is open, so its two actual free edges fade normally.
        for index, segment in enumerate(segments):
            length = segment[1]
            if index in (0, 4):
                start = cursor
                one = (segment,)
                rails.append(_flute_skin.Rail(
                    at=lambda s, one=one, start=start: _walk(one, s - start),
                    length=length, start=start, closed=False,
                    band=bay_storey_z(box.pump_bay), berthed=tuple(berthed),
                    mouth=(0.0, -1.0)))
            cursor += length
    return rails


def flute_centres(outer):
    """Every groove's arc length, the datum's first. `flute_count` of them, closing on the
    perimeter exactly."""
    pitch = flute_pitch(outer)
    return tuple(k * pitch for k in range(flute_count))


@functools.lru_cache(maxsize=8)
def _rounded_outer(outer):
    """The outer box with rounded standing-vertical corners and the facet chamfered in — the
    print silhouette the half is clipped to so nothing pokes past it. A full-width facet raises
    no new standing vertical: it runs out into the ±X walls' own rounds, which are already
    relieved.

    IT IS A PLAIN BOX AND THE SHOW SURFACE IS NOT. The flutes are cut into the MESH the printer
    reads (`flute_skin.py`), not into this solid, because the fade that stops them is a field
    over the whole surface and not a figure a prism can carry: it has to follow an opening's
    rim, a diagonal arris and a level seam with one rule. What this shape is, then, is the
    surface the flutes are measured FROM — every station in that field is struck on the plan
    this returns.
    """
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

    AND THE LAND IS SUNK PAST IT, to `display_cover_seat`, over everything OUTSIDE the bezel's
    own outline. The cover carries a whole screw seat of section there rather than a pad under
    each head, so what the land takes is the plate's own back and not two circles of it. It
    stops ON that outline because inside it the bezel counterbore is already cut and the glass
    is already in it: the plate has to stay `display_cover_thickness` there, bearing on the
    gasket and through it on the glass, so there is nothing to sink and nothing that could be.
    The bores follow the land down and are struck from its floor, so an insert is still set in
    printed material.

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
    # The land, sunk from the inset's floor to the plate's own seat and stopped on the bezel's
    # outline — one ring of void round a rectangle of standing floor, not two pad pockets.
    land = (
        cq.Workplane(plane).workplane(offset=-display_inset_depth)
        .rect(display_inset_x, display_inset_slope)
        .extrude(-(display_cover_seat - display_inset_depth))
        .edges(along_normal).fillet(display_corner_r).val()
        .cut(cq.Workplane(plane).workplane(offset=-display_inset_depth + 1.0)
             .rect(display_bezel_x, display_bezel_slope)
             .extrude(-(display_cover_seat - display_inset_depth + 2.0))
             .edges(along_normal).fillet(display_corner_r).val())
    )
    cut = inset.fuse(bezel).fuse(pcb).fuse(land)
    for sx in (-1.0, +1.0):
        # And the insert the screw pulls against, struck from the land's own floor.
        bore = (
            cq.Workplane(plane).workplane(offset=-display_cover_seat)
            .center(sx * display_screw_x, 0.0).circle(heatset_dia / 2.0)
            .extrude(-(heatset_depth + mount_bore_relief)).val()
        )
        cut = cut.fuse(bore)
    return cut


# --- wall through-holes -----------------------------------------------------

# The roof angle of every horizontal round through-hole, measured up from the print bed.
#
# THE COMMITTED BACK-TOP PET-GF PROFILE IS THE LIMIT. Its automatic-support threshold is 35
# degrees. The 36-degree exact-profile coupon is support-free, so the cutter keeps one whole
# degree of margin. The line is tangent to the nominal circle: the fitting still gets its whole
# round pass envelope below it, while no wider or taller peak is cut than this angle requires.
teardrop_roof_angle = 36.0


def _port_cuts(ports, y0, y1):
    """The through-holes of one wall's port list, as cutters spanning y0..y1
    (a wall's thickness with a margin either side). The pack owns both layouts,
    since it places the bodies the bands are measured from
    (../y-wall-of-back-top/README.md); the two walls differ only in which list and
    which span, so they are cut by the same code.

    A ROUND port is round through its working lower section and closes on the same tangent
    teardrop roof as every other Y-axis bore in these standing prints. Rectangular connectors
    keep the aperture their own housings require."""
    out = []
    for kind, hx, hz, *size in ports:
        if kind == "round":
            out.append(_teardrop_y(size[0] / 2.0, hx, hz, y0, y1))
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


def _nameplate_support(plate, sx, sz, y_pad):
    """One support-free nameplate insert stem and its full-width 45° wall corbel.

    The upper half stays round around the insert. The lower half is squared to the circle's
    tangents, giving the corbel a full-width face to carry."""
    stem_r = plate.stem_d / 2.0
    y_tip = y_pad - plate.reach
    stem = _ycyl(stem_r, sx, sz, y_tip, y_pad).fuse(
        _ybox(sx - stem_r, sx + stem_r, y_tip, y_pad, sz - stem_r, sz))
    support = stem.fuse(_yz_prism(
        sx - stem_r, sx + stem_r,
        [(y_tip, sz - stem_r), (y_pad, sz - stem_r),
         (y_pad, sz - stem_r - plate.reach)]))
    # Remove the cylinder/box imprint on the free face: the lower arc lies inside the D's
    # material and is not a surface edge for the mesh viewer to expose.
    return support.clean()


def _nameplate(solid, plate, outer, y_outer, zlo, zhi):
    """The nameplate's pocket, cut into a ±Y wall's outer face, and the two screw bosses standing
    behind it on the inner one.

    THE POCKET TAKES THE PLATE'S WHOLE THICKNESS, and the plate is a screw seat thick — deeper
    than this wall's own stock. So THE WALL THICKENS BEHIND IT: a plateau on the inner face
    standing to `plate.wall`, which is one `wall` and one `rear_seam_clear`. That second figure is
    the band the pack already stands off this face, so the plateau reaches exactly the plane the
    rear Z seam's lip presents the core and stops — it takes nothing the pack was using, and what
    it buys is a floor under the WHOLE pocket instead of a pad pocket punched clean through the
    wall at each screw. Nothing then stands off the plate's own back, which is the face the plate
    prints on.

    ITS UNDERSIDE IS STRUCK AT 45°. This piece prints on its Z− face with the +Y wall vertical
    on the bed, so a plateau's down-facing edge is the plate's whole width of ceiling starting in
    air. Cut back at 45° it is a ramp the wall reaches under instead — the relief every hanging
    face on this box gets.

    AND SO IS THE POCKET'S OWN CEILING, for the same reason and by the same figure. The pocket is
    the plate's whole SILHOUETTE and not just its outline: the plate's back edge is chamfered
    `plate.bevel` at 45° and the pocket answers it, its floor that much in from the outline all
    round and opening out to full size at 45°. Cut square, a pocket one `plate.thick` deep hangs
    that whole depth of flat ceiling off its head. Ramped, it hangs `plate.thick - plate.bevel`
    of rim and no more — this is `_front_relief_cuts`' bargain, a ceiling rising at
    `relief_chamfer` to the mouth, taken as far as an inlay can take it. It stops short of the
    mouth where that one runs past it, because THE RIM HAS TO STAY SQUARE: a 45° opening at the
    face would read as a V-groove round the plate instead of the flush inlay this face is. What
    is left hanging is narrower than the square pocket hung before the plate ever thickened.

    WHAT IS LEFT STANDING IS A D-STEM AND A 45° CORBEL UNDER IT. The plateau carries the first
    `nameplate.floor_under` of the depth an insert's bore wants and the boss stands for the rest,
    one standard M3 section wide. Its upper half stays round around the insert; its lower half is
    squared to the circle's tangents. The stem's whole underside is one face, and a full-stem-width
    wedge carries that face back to the plateau, falling one millimetre for every millimetre of
    reach. There is no collar: a collar closes a pad pocket and there is no pad.

    The plate lies wholly on one piece — `nameplate-field` is the reading that keeps it off the
    seam — so the station's own Z decides which piece carries all of it."""
    if plate is None or not (zlo <= plate.z <= zhi):
        return solid
    y_inner = y_outer - wall
    y_pad = y_outer - plate.wall
    floor = y_outer - plate.thick
    rise = y_inner - y_pad
    # The pocket's own outline, and the plateau one `wall` proud of it all round, so the pocket is
    # walled for the whole of a depth the wall's own stock could not have walled.
    pw = plate.width + 2.0 * plate.slip
    ph = plate.height + 2.0 * plate.slip
    pr = plate.corner + plate.slip
    pad = _rect_cut_y(plate.x, plate.z, pw + 2.0 * wall, ph + 2.0 * wall, pr + wall,
                      y_pad, y_inner)
    zfoot = plate.z - ph / 2.0 - wall
    xhalf = pw / 2.0 + wall
    pad = pad.cut(_yz_prism(plate.x - xhalf - 1.0, plate.x + xhalf + 1.0,
                            [(y_pad, zfoot), (y_pad, zfoot + rise), (y_inner, zfoot)]))
    solid = solid.fuse(pad)
    for dx, dz in plate.screws:
        sx, sz = plate.x + dx, plate.z + dz
        solid = solid.fuse(_nameplate_support(plate, sx, sz, y_pad))
    mouth = (cq.Workplane("XY").rect(pw, ph).extrude(plate.thick + 1.0)
             .edges("|Z").fillet(pr).faces("<Z").chamfer(plate.bevel).val()
             .rotate((0, 0, 0), (1, 0, 0), -90.0)
             .translate(cq.Vector(plate.x, floor, plate.z)))
    solid = solid.cut(mouth)
    for dx, dz in plate.screws:
        sx, sz = plate.x + dx, plate.z + dz
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


def _port_field(solid, field, ports, outer, y_outer, zlo, zhi, wall_at=None):
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
    at = (lambda _x, _z: wall) if wall_at is None else wall_at
    deep = y_outer
    for px, pz, width, rise in field.pockets:
        # THE BOSS MAKES BACK WHAT THE POCKET TOOK, AND NO MORE. `proud` is what a chip's pocket
        # costs a `wall`-thick face; a wall carrying more section than that has already made it
        # back, and a boss standing proud of THAT is a boss standing in the room — which is
        # where the water pump and the cold core are. Read at the station, because this wall is
        # not one thickness (`back_wall_t_at`).
        t = at(px, pz)
        y_inner = y_outer - t
        proud = max(0.0, field.proud - (t - wall))
        deep = min(deep, y_inner - proud)
        if proud <= 1e-9:
            continue
        boss_y0 = y_inner - proud
        band = _ybox(ox0 - 1.0, ox1 + 1.0, boss_y0, y_inner, zlo, zhi)
        boss = _port_chip(px, pz, width + 2.0 * field.rim, rise + field.rim, boss_y0, y_inner)
        # The boss is a D below its bore's axis, on a 45° web run down the wall — squared
        # and webbed the way every boss on this box is, so its underside prints off the
        # wall it stands on.
        w2 = width / 2.0 + field.rim
        zb = pz - w2
        boss = boss.fuse(_ybox(px - w2, px + w2, boss_y0, y_inner, zb, pz))
        boss = boss.fuse(_yz_prism(px - w2, px + w2,
                                   [(y_inner, zb), (boss_y0, zb),
                                    (y_inner, zb - proud)]))
        solid = solid.fuse(boss.intersect(silhouette).intersect(band))
    for px, pz, width, rise in field.pockets:
        solid = solid.cut(_port_chip(px, pz, width, rise,
                                     y_outer - field.proud, y_outer + 1.0))
    for cutter in _port_cuts(ports, deep - 1.0, y_outer + 1.0):
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


# --- funnel opening (Zone C) ------------------------------------------------

def _funnel_frame(inner, outer):
    """What the top wall has left to give the collar, `(x_lo, x_hi, y_lo, y_hi)`: BEHIND the
    display facet's own back plane, inboard of the ±X boss chains, and ahead of the back
    wall.

    THE FRONT IS A DIFFERENT KIND OF EDGE FROM THE OTHER THREE. On those three the frame runs
    out into a free edge, and the collar stands one `funnel.brim_margin` inside it: the
    flange overhangs the collar by `brim_overhang` to catch the wall and hold the funnel out of
    the box, and the margin is the wider of the two, so a full overhang's width of top wall
    still remains outboard of the brim's edge. Forward the wall runs straight on into the
    display housing, whose back is the vertical `housing_back_y` — and the slab ahead of that
    cut is what the brim's front flange lands on. The front's requirement is
    `funnel_front_ledge`, the top wall kept between that plane and the throat itself, and it
    stands in this frame. `with_funnel` asks the margin of the three free edges."""
    ix0, ix1, _iy0, iy1, _iz0, _iz1 = inner
    return (ix0 + boss_in + funnel_chain_gap,           # clear of the −X chain's bosses
            ix1 - boss_in - funnel_chain_gap,           # clear of the +X chain's bosses
            housing_back_y(outer) + funnel_front_ledge, # behind the display housing
            iy1 - wall)                                 # ahead of the +Y wall


def _funnel_hole(centre):
    """Rectangle (x0, x1, y0, y1) of the funnel opening in the top wall: the placed funnel's
    collar — funnel.py's own dims at the box's own `funnel` centre.

    The funnel is pushed as far FORWARD as `_funnel_frame` allows, and reaches aft for
    whatever plan area its capacity needs — so the opening may cross the Y seam. Both halves
    take their share of the cut and the collar bridges it; what the seam gives up there is its
    top-wall lip over the hole's span, which the mouth shelf's own relief already accounts
    for (`_funnel_cut`).

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
    x0, x1, y0, y1 = _funnel_hole(centre)
    lims = _funnel_frame(box.inner, box.outer)
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
    # AND THE +Y EDGE IS THE CEILING PANEL'S, not the frame's. Aft of the throat the top surface
    # is the slide-in panel (`../ceiling-panel/ceiling_panel.py`), whose fore edge IS the collar's
    # own aft edge and whose show face carries the top wall's section back to the +Y wall — so
    # what the brim lands on there is that panel, and the margin is the panel's own depth. A panel
    # whose fore edge stood AFT of the collar would leave the flange over the throat, and the
    # reading comes back negative by however far it had drifted.
    cp = _ceiling()
    aft = (cp.aft_y - y1) if cp.fore_y <= y1 + tol else (y1 - cp.fore_y)
    got = (x0 - lims[0], lims[1] - x1, aft)
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
    return box._replace(pack=box.pack._replace(funnel=centre))


def _funnel_cut(inner, outer, centre):
    """The funnel throat punched clean through the top wall — one wall deeper
    than the ceiling, so the Y-seam's top-wall lip/mouth shelf (hanging one
    wall below it) is relieved across the hole span the seam crosses.

    The opening is the collar, whole: the funnel is a full rectangle and the wall carries
    nothing over the tap-water sequence that the throat has to be cut around."""
    x0, x1, y0, y1 = _funnel_hole(centre)
    return _ybox(x0, x1, y0, y1, inner[5] - wall - 1.0, outer[5] + 1.0)


def _ceiling_corbels(solid, inner, outer, centre, y_joint, y_bosses=()):
    """The flat ceiling's two side strips on a top piece, corbelled: a 45° underside
    rising off each ±X wall to nothing at the funnel opening's edge, so a top piece —
    printing mouth-down — lays every ceiling layer on the one below it. The strip's own
    span is wall-rooted on one side and open over the opening on the other.

    The corbel runs the housing's back plane to the Y-seam furniture's fore face, and a
    second one carries the lip's ceiling tongue, struck one `wall` lower on the tongue's
    own underside: its funnel-side span roots on the ceiling collar's chain-deep face and
    its wall-side span reaches the plug tip. Together they carry the whole tongue into the
    mouth it telescopes into; the collar band itself is the collar's own D, fill and web.

    OVER THE BOSS THE TONGUE STANDS ON THE COLLAR. The socket collar is a box `2 * socket_r`
    about its bore, so its crown is a flat land the whole width of the boss and the whole
    depth of the lip, one `socket_r` over the level the wall was pinned at, and the tongue's
    section runs straight up off it. Where a wall carries no pinned level under the tongue
    the 45° walk from the plug tip is what roots it."""
    cx, _cy = centre
    hole_x0, hole_x1 = cx - _funnel.collar_w / 2.0, cx + _funnel.collar_w / 2.0
    iz1 = inner[5]
    y0 = housing_back_y(outer)
    yb = _y_boss(y_joint)
    for hole_x, wall_x, sx in ((hole_x1, inner[1], -1.0),
                               (hole_x0, inner[0], +1.0)):
        deep = abs(wall_x - hole_x)
        solid = solid.fuse(_xz_prism(y0, yb - socket_r,
                                     [(hole_x, iz1), (wall_x, iz1),
                                      (wall_x, iz1 - deep)]))
        chain = wall_x - (boss_in if wall_x > 0 else -boss_in)
        tz = iz1 - wall
        solid = solid.fuse(_xz_prism(yb - socket_r, y_joint + lip_len,
                                     [(hole_x, tz), (chain, tz),
                                      (chain, tz - abs(chain - hole_x))]))
        _xs, x_tip, _xh, x_cap = _boss_x(wall_x - sx * wall, sx)
        # THE BOSS CORBEL STANDS ON THE COLLAR'S WHOLE CROWN. The half-slip belongs
        # to the plug's slide path, not to this solid collar; both sections share
        # `yb - socket_r` as their fore face, with no half-slip land between them.
        by0, by1 = yb - socket_r, y_joint + lip_len
        walk = tz - abs(x_cap - x_tip)
        crown = max((z_boss + socket_r for x_in, _x_ext, bsx, z_boss in y_bosses
                     if x_in == wall_x and bsx == sx and z_boss + socket_r < tz),
                    default=walk)
        if crown > walk:
            solid = solid.fuse(_ybox(min(x_tip, x_cap), max(x_tip, x_cap),
                                     by0, by1, crown, tz))
        else:
            solid = solid.fuse(_xz_prism(by0, by1,
                                         [(x_tip, tz), (x_cap, tz), (x_tip, walk)]))
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
#   * BACK half = PIN: a `plug_dia` square prism from the ±X exterior to the
#     heat-set, seating in the socket's slot. Sized to the screw SHANK, not the head
#     (the head sits in the wall counterbore); screw-clearance + head counterbore
#     bored in.
#   * FRONT lip = SOCKET: a collar round the slot — one `wall` of material and no
#     more — bored to receive the round pin (slide fit) with the heat-set + cap at
#     the deep inboard end.
# The head seats in the +Y wall; the shank crosses the pin body into the front
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
    pinned at a level for each end of each piece that crosses it: the under-floor
    level pins the two bottom pieces, the under-ceiling one the two tops. Their
    inner ends need no screw — each column's hooked rails hold its own Z seam
    closed along the whole run, and the two levels here stand the columns against
    each other.

    A level sits as near the end it pins as its OWN wall allows — the two walls
    are independent screws, so each is searched separately and they need not
    agree. The manifold stack denies the −X wall a socket body over one band, so
    its levels there slide to the nearest height that can hold one.

    The end levels stand the PIN'S OWN FACE `boss_end_clear` off the floor and the
    ceiling. What is in that slot is print support, and both walls carry the same
    figure at both ends, so one reach clears all four."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    r = socket_bore_dia / 2.0
    zt = iz1 - boss_end_clear - plug_dia / 2.0
    zf = iz0 + boss_end_clear + plug_dia / 2.0
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
    the heat-set end, and the pod cap one wall past it."""
    length = screw_len if length is None else length
    x_seat = x_ext + sx * head_cbore_depth
    x_tip = x_seat + sx * (length - heatset_depth)
    x_heat = x_tip + sx * heatset_depth
    x_cap = x_heat + sx * socket_cap
    return x_seat, x_tip, x_heat, x_cap


def _back_plug(x_ext, sx, z_boss, y_boss):
    """BACK pin: a `plug_dia` SQUARE prism from the ±X exterior to the heat-set, where
    it registers in the front socket's slot. Its −Y face stands on the seam mouth, and
    the wall it drives through carries it — the pin is that wall's own material for
    the first `wall` of its length and a stub of the same section beyond.

    IT IS A BOX AND NOT A PIPE — the box's one boss section. A pipe meets the mouth on
    the line where it grazes it and closes on a crown laid over its own axis. The square
    pin keeps the flat registration faces the socket wants, and a full-width 45° corbel
    carries its lower face from the wall to the pin's inboard tip. `_y_lip_channel` takes
    the same profile, one `fits.slip` lower, out of the front socket's whole travel."""
    _xs, x_tip, _xh, _xc = _boss_x(x_ext, sx)
    r = plug_dia / 2.0
    x_in = x_ext + sx * wall
    xa, xb = sorted((x_ext, x_tip))
    pin = _ybox(xa, xb, y_boss - r, y_boss + r, z_boss - r, z_boss + r)
    floor = z_boss - r
    drop = abs(x_tip - x_in)
    corbel = _xz_prism(y_boss - r, y_boss + r,
                       [(x_in, floor), (x_tip, floor), (x_in, floor - drop)])
    return pin.fuse(corbel)


def _front_socket(x_in, x_ext, sx, z_boss, y_joint, inner):
    """FRONT socket: a collar round the slot — a block standing off the ±X wall's
    inner face, from that face out to the cap over the insert's blind end, one
    `wall` of material round the slot its whole length.

    Its aft face lands on the lip rim (`_y_boss` + socket_r, which is what `lip_len`
    is struck from) and its forward face a hair ahead of the lip's own fusion
    shoulder, so it stands on the lip band down its whole length.

    THE COLLAR IS A BOX, `2 * socket_r` on a side about the bore's axis. A round pipe
    has no printable half on a standing print: tangent to the flat under it, it leaves a
    crevice either side of the touching line — an overhang that starts at zero degrees —
    and it closes overhead on a crown laid across its own bore. So the section is squared
    onto the flats it meets, the floor collar's onto the slab and every other level's onto
    a 45° web run down the lip's own face, the corner pedestal's idiom. It is also the
    footprint `seam_bosses` already reports, so what a check reads and what stands on the
    wall are one shape.

    Bore, heat-set and the plug's slide path are cut afterwards."""
    _xs, _xt, _xh, x_cap = _boss_x(x_ext, sx)
    xa, xb = sorted((x_in, x_cap))
    yb = _y_boss(y_joint)
    iz0 = inner[4]
    boss = _ybox(xa, xb, yb - socket_r, yb + socket_r,
                 z_boss - socket_r, z_boss + socket_r)
    if z_boss - socket_r > iz0 + 0.01:
        lip_in = x_in + sx * wall
        drop = abs(x_cap - lip_in)
        floor = z_boss - socket_r
        boss = boss.fuse(_xz_prism(yb - socket_r, yb + socket_r,
                                   [(lip_in, floor), (x_cap, floor),
                                    (lip_in, floor - drop)]))
    return boss


def _front_cuts(x_in, x_ext, sx, z_boss, y_boss, y_joint):
    """Front-socket inner cuts at one level: ONE slot that receives the plug and carries
    it down to its seat, and the heat-set pocket at the deep end. Open at the rim, so it
    is a slide path and not a pocket.

    THE SEAT AND THE CHANNEL ARE ONE CONTINUOUS SLOT. The channel is struck at the bore's
    axis carrying the bore's width, so the plug rides one section its whole travel. Above
    its square pass envelope the cutter rises 45 degrees in X to the inboard tip: that adds
    plug clearance while replacing the slot's horizontal printed roof with a self-supporting
    one.

    The slip lives on the +Y (slide-in) side: the slot is shifted +slip/2 so its −Y wall
    registers on the plug's −Y face at the mouth, instead of overshooting past the seam.
    The heat-set stays coaxial with the screw at y_boss, past the slot's deep end."""
    _xs, x_tip, x_heat, _xc = _boss_x(x_ext, sx)
    b = socket_bore_dia / 2.0
    bore_y = y_boss + split_slip / 2.0
    heat = _xcyl(heatset_dia / 2.0, y_boss, z_boss, x_tip, x_heat)
    bx0, bx1 = sorted((x_in, x_tip))
    y0, y1 = bore_y - b, y_joint + lip_len + 1.0
    roof = z_boss + b
    slot = _ybox(bx0, bx1, y0, y1, z_boss - b, roof)
    slot = slot.fuse(_xz_prism(
        y0, y1,
        [(x_in, roof), (x_tip, roof),
         (x_tip, roof + abs(x_tip - x_in))]))
    return slot.fuse(heat)


def _screw_cut(x_ext, sx, z_boss, y_boss, length=None):
    """M3 shank clearance from the ±X exterior through the plug to the heat-set,
    plus the SHCS head counterbore at the exterior — the seat one wall outboard
    of the heat-set. The head keeps its complete round pass and bearing envelope;
    `_teardrop_x` gives only its unsupported crown a tangent printable roof."""
    _xs, x_tip, _xh, _xc = _boss_x(x_ext, sx, length)
    shank = _xcyl(screw_clear_dia / 2.0, y_boss, z_boss, x_ext - sx * 1.0, x_tip)
    cbore = _teardrop_x(head_cbore_dia / 2.0, y_boss, z_boss,
                        x_ext - sx * 1.0, x_ext + sx * head_cbore_depth)
    return shank.fuse(cbore)


def _front_lip(inner, y_joint):
    """The front half's rear lip: a full-`wall` band telescoping +Y into the back
    half and running on its inner wall. It runs one `wall` back into the body
    cavity (the fusion shoulder / telescoping stop) and forward over the overlap
    to the rim.

    THE SHOULDER IS FLUSH AND THE TONGUE IS NOT, and the step between them is at
    the mouth. Fore of `y_joint` the band's outer face is the body's own inner
    wall — one solid with the body, nothing shaved. Aft of it the band stands in
    the other piece, so its three outer faces come in one `fits.slip`, and the
    step they come in on is the plane the back half's mouth is struck on: it
    passes the mouth in the first millimetre of travel and leads the rest of the
    lip in behind it. Printed Z-down the side segments are
    vertical bands and the −Y mouth is a vertical face, so it needs no frame
    bevel; corners stay square, concentric with the square seam mouth it
    telescopes into (the box's rounded verticals are at the front and +Y walls, not
    the seam). The bore stays open its whole length — the fusion shoulder is the
    one-wall overlap where the band meets the body wall (out to y_joint), NOT a
    slab across the seam.

    THREE-SIDED here: both side walls and the ceiling. The floor is lapped too —
    every seam laps, none butts — but by a different means, because the floor is
    the one seam face whose inner side is not free. This proud tongue is the wall
    or ceiling continuing one `wall` INTO the cavity, and on the free faces that
    space is empty; on the floor the cold core rides there, so a proud floor tongue
    would drive straight into it. The floor's overlap therefore lives inside the
    slab as a full-thickness tongue with a 45° scarf nose (`_floor_scarf`), not
    standing proud — the right overlap for a bearing face. So the lip proper stays
    three-sided, and the floor carries its own joint. The ceiling segment remains
    a cantilever that juts one overlap past the body and wants print support; the
    floor tongue lies on the bed, and only its scarf nose rises at 45°. The side-wall
    segments, vertical to the bed, are free."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    y0, y1 = y_joint - wall, y_joint + lip_len
    shoulder = _ybox(ix0, ix1, y0, y_joint, iz0, iz1)
    tongue = _ybox(ix0 + fits.slip, ix1 - fits.slip, y_joint, y1,
                   iz0, iz1 - fits.slip)
    inner_box = _ybox(ix0 + wall, ix1 - wall, y0 - 1.0, y1 + 1.0, iz0 - 1.0, iz1 - wall)
    return shoulder.fuse(tongue).cut(inner_box)


def _y_lip_channel(inner, y_joint, bosses):
    """THE Y TELESCOPE'S OWN CARVING — cut LAST of a front piece's work, so the section
    standing aft of the mouth is the section that runs in the back half's register,
    whatever the piece has since fused into that band: its own flank stock
    (`_front_top_flanks`), a socket's web, a corbel, a tray's foot. `_front_lip` draws
    the tongue at that section and this is what holds it there. `_z_rail_channels` is
    the same cut on the other seam.

    THE FOUR COLLARS STAND OUT OF ITS FLANKS. Fore of the mouth each collar roots on the
    box's interior face; through the overlap it finishes on the tongue's slipped outer face,
    the surface which actually enters the back half. Four broad collars across two walls locate
    this joint in X. The lip runs clear of the wall between them, and their crowns are carved
    with everything else; no one-running-fit strip continues past the tongue beside a collar.

    THE PIN CORBELS TRAVEL IN THIS CHANNEL TOO. Each back pin's lower face rises 45°
    from its wall to its inboard tip. The matching cut runs the lip's whole travel and
    stands one `fits.slip` below that profile, so the corbel enters with the square pin
    and the socket keeps its full screw and heat-set section inboard of it."""
    ix0, ix1, _iy0, _iy1, iz0, iz1 = inner
    y0, y1 = y_joint, y_joint + lip_len + 1.0
    zlo, zhi = iz0 - floor_t - 1.0, iz1 + wall + 1.0
    flanks = _ybox(ix0 - 1.0, ix0 + fits.slip, y0, y1, zlo, zhi).fuse(
        _ybox(ix1 - fits.slip, ix1 + 1.0, y0, y1, zlo, zhi))
    yb = _y_boss(y_joint)
    for x_in, x_ext, sx, z_boss in bosses:
        _xs, _xt, _xh, x_cap = _boss_x(x_ext, sx)
        tongue_face = x_in + sx * fits.slip
        xa, xb = sorted((tongue_face, x_cap))
        flanks = flanks.cut(_ybox(xa, xb, yb - socket_r, yb + socket_r,
                                  z_boss - socket_r, z_boss + socket_r))
        _xs, x_tip, _xh, _xc = _boss_x(x_ext, sx)
        floor = z_boss - plug_dia / 2.0 - fits.slip
        drop = abs(x_tip - x_in)
        flanks = flanks.fuse(_xz_prism(
            y_joint, y_joint + lip_len,
            [(x_in, floor), (x_tip, floor), (x_in, floor - drop)]))
    return flanks.fuse(_ybox(ix0 - 1.0, ix1 + 1.0, y0, y1, iz1 - fits.slip, zhi))


def _floor_scarf(inner, y_joint):
    """The Y seam's FLOOR overlap: a bed-supported, full-thickness tongue with
    a 45° scarf nose.

    The floor is the one seam face whose cavity side is occupied — the cold core
    rides on it — so it cannot carry the proud tongue the walls and ceiling do
    (`_front_lip`). Its overlap stays within the slab instead. The FRONT floor runs
    aft at the slab's whole `floor_t` thickness, then tapers to the cavity-side datum
    over one `floor_t` — the run is the rise, which is what makes the nose 45° on a
    slab of any section; the BACK floor gives up that envelope and keeps the matching
    bed-side wedge under the nose. The tongue's broad underside is on the print bed
    and the only rising face is 45°, so neither half asks support for the core's
    bearing surface. Assembled, the top remains one plane at z=iz0.

    Each flank is a plumb face standing one `fits.slip` off the side wall beside
    it. The nose is raked, and the tongue's is struck `scarf_axial` short of the
    relief's, which stands the two rakes one `fits.slip` apart where they pass.

    Returns (tongue, relief): the solid the FRONT half fuses and the matching
    envelope the BACK half cuts."""
    ix0, ix1, _iy0, _iy1, iz0, _iz1 = inner
    zbed = iz0 - floor_t
    root = y_joint - 1.0                              # robust face overlap into front slab
    tongue_tip = y_joint + lip_len - scarf_axial
    tongue_flat = tongue_tip - floor_t
    relief_tip = y_joint + lip_len
    relief_flat = relief_tip - floor_t
    tongue = _yz_prism(
        ix0 + fits.slip, ix1 - fits.slip,
        [(root, zbed), (tongue_flat, zbed), (tongue_tip, iz0), (root, iz0)])
    relief = _yz_prism(
        ix0, ix1,
        [(root, zbed - 1.0), (relief_flat, zbed - 1.0),
         (relief_flat, zbed), (relief_tip, iz0), (root, iz0)])
    return tongue, relief


# Boss Y position — one value feeds the plug AND the socket, so they are
# coaxial by construction. Placed so the plug's −Y face mates the back mouth;
# the derived lip_len then lands the socket collar's +Y face on the lip rim.
def _y_boss(y_joint):
    return y_joint + plug_dia / 2.0


# --- bottom↔top joint: the HOOKED SLIDE --------------------------------------
#
# The BOTTOM piece carries the lip, the hooked arms on its straight flank runs, the
# stop blocks at their closed ends and the corner fills; the TOP piece carries the
# foot each head stands over and the notch that swallows it. BOTH TOPS ENTER FORE OF
# HOME AND SLIDE AFT — front-top over the front wall's own plane, in open air ahead
# of the box; back-top over the open Y-seam mouth — each foot's aft end face landing
# on its stop block's, which is the column's Y datum. Everything else closes one
# `slide_slip` behind that contact.
#
# A TOP COMES OFF THE WAY IT WENT ON, FORWARD. Back-top's escape is fore into
# front-top, which stands in it. Front-top's escape is fore into open air, and what
# holds it there is the Y seam's upper pair of screws — the plug back-top carries,
# in the socket front-top's lip carries. Two screws out and front-top draws straight
# off the front of the box, the back column and whatever the box is built under
# never touched.


def _z_rail_runs(inner, y_joint, col, plate, chase=()):
    """The runs one column's rails occupy, one row per ±X flank:
    `(x_in, sx, y0, y1, lane_aft)` — where that flank carries the head, the stop
    block and the top piece's foot. Every run is OPEN at `y0` and CLOSED at `y1`, and
    which way round those fall is which way that column travels: `lane_aft` is how
    far PAST the stop the channel carries its FULL section (`_z_rail_channels`).

    THE TWO COLUMNS ARE MIRRORED, AND EACH TOP DRAWS OFF THE END OF THE BOX IT STANDS
    AT. Front-top enters fore of home and slides aft; back-top enters aft of home and
    slides fore. So the front pair parts toward the room and the back pair toward the
    wall, and neither has to be lifted over the other to come apart.

    A RUN IS WHAT THE SWEEP LEAVES, and the sweep is the whole question: a top piece
    passes over every station of the flank on the side it comes FROM, so a rail may
    stand only where that piece's own solid can open for it. On both columns what
    stands on that side is the Y-seam band — front-top's carries the TONGUE with it —
    and every one of those faces is inboard, which a channel may cut. So on both the
    lane runs clear off the piece's own end, NOTHING has to be swept around, and each
    run reaches a structural limit rather than a horizon: the front's is
    `wall + z_lip_y_margin` short of the joint, where the Y telescope's overlap
    begins; the back's is the rear wall's own corner round. The front opens on the
    tee wall (`plate["wall_aft_y"]`), the back on that same corner."""
    iy0, iy1 = inner[2], inner[3]
    out = []
    for x_in, sx in ((inner[0], +1.0), (inner[1], -1.0)):
        if col == "front":
            y0 = plate["wall_aft_y"] if plate else iy0 + column_round + wall
            y1 = y_joint - wall - z_lip_y_margin
            lane_aft = y_joint + lip_len + z_lip_y_margin
        else:
            # BACK-TOP ENTERS AFT AND SLIDES FORE — the front column mirrored, so a hand
            # draws either top off the end of the box it already stands at. WHAT SWEEPS A
            # RUN IS WHAT THE TOP CARRIES ON THE SIDE IT COMES FROM, and on this column
            # that is its own Y-seam band alone: an inboard surface a channel may open, the
            # way front-top's tongue is. So this run needs no horizon either — it reaches
            # the rear wall's own corner, and the lane runs clear off the piece's fore end.
            y0 = iy1 - corner_round
            y1 = y_joint + lip_len + z_lip_y_margin
            lane_aft = y_joint - 1.0
        out.append((x_in, sx, y0, y1, lane_aft))
    return out


def _z_rail_travel(inner, y_joint, col, plate, chase=()):
    """How far a column's top slides, entry to home — the longest run's engagement
    plus `rail_entry` of approach. One figure per column, because the piece is
    rigid and the longest rail is the one that has to clear its channel first."""
    runs = _z_rail_runs(inner, y_joint, col, plate, chase)
    return max(abs(r[3] - r[2]) for r in runs) - rail_stop_len + rail_entry


def _rail_nominal_foot_face(col, sx):
    """The common nominal flank face one column can carry through its Z-seam foot.

    A foot belongs to BOTH pieces: the top presents its caught face and the bottom carries the
    head under it. Use the shallower of their two nominal sections if those ever differ, so the
    joint never invents stock one of its pieces does not have."""
    top, bottom = ((front_top_flank_face(), front_bottom_flank_face()) if col == "front"
                   else (back_top_flank_face(), back_bottom_flank_face()))
    return min(top[0], bottom[0]) if sx > 0.0 else max(top[1], bottom[1])


def _rail_foot_face(x_in, sx, col):
    """The inboard edge of one top foot.

    Both columns carry their full nominal flank section to the caught face and place the arm
    there. The front column derives its collet-plate ends from this moving envelope, so the
    steel clears the deeper foot through the whole slide instead of truncating the wall."""
    return _rail_nominal_foot_face(col, sx)


def _rail_hook_lap(col):
    """The overlap one column's head carries over its top foot."""
    return back_hook_lap if col == "back" else front_hook_lap


def _rail_x(x_in, sx, col):
    """The rail's X stations about the foot's inboard face, read inboard: the head's
    outboard face one column-specific hook overlap back over that foot, the arm's sliding face
    `slide_slip` past it, and the arm's back."""
    x_f = _rail_foot_face(x_in, sx, col)
    x_hk = x_f - sx * _rail_hook_lap(col)
    x_a = x_f + sx * slide_slip
    x_h1 = x_a + sx * hook_arm
    return x_hk, x_f, x_a, x_h1


def _z_rail_heads(inner, y_joint, zj, col, plate, chase=()):
    """The BOTTOM piece's whole share of its Z seam above the mouth: the hooked
    rails — an ARM standing on the mouth down each straight run, its HEAD stepping
    outboard over the groove the top's foot slides in — and the stop block closing
    each run's far end. There is no other lip: the top's own walls sweep every
    station of the flank on the way in, and outside the runs the seam is the mouth
    bearing on the shoulder with nothing proud of it.

    THE HEAD IS THE CATCH, AND ITS FACES ARE SQUARE. Its underside is flat and the
    foot's top face under it is flat: lifting the top lands the two on each other
    along the whole run, full faces bearing from the first micron. That underside
    is the joint's one down-looking flat — the column's hook overlap plus `slide_slip` proud, an
    abrupt ledge at the TOP of a piece that prints floor-down. The arm's
    base falls back to the lip's underwall on a 45° under-flare. The head's open
    end tapers `rail_lead` in plan, so the foot finds the head before the head
    finds it.

    THE STOP BLOCK IS THE DATUM. It fills the arm's whole section plus the head's
    lap over `rail_stop_len` at the closed end, and the foot's end face landing on
    it is the slide's home: the one nominal contact in the joint, a flat printed
    face on a flat printed face, once per rail."""
    z_foot, rim = zj + hook_foot, zj + z_rise
    out = None
    for x_in, sx, y0, y1, _lane in _z_rail_runs(inner, y_joint, col, plate, chase):
        sy = 1.0 if y1 > y0 else -1.0        # open end to closed: the way this column goes
        x_hk, x_f, x_a, x_h1 = _rail_x(x_in, sx, col)
        arm = _xz_prism(y0, y1, [(x_a, zj), (x_a, z_foot + slide_slip),
                                 (x_hk, z_foot + slide_slip), (x_hk, rim),
                                 (x_h1, rim), (x_h1, zj)])
        # The arm's base falls back to the lip's underwall on a 45° under-flare, its
        # hanging face at the one angle a floor-down piece hangs anything at.
        # The under-flare roots half a millimetre outboard of the common nine-millimetre
        # face that carries this column, with the broad head lying over its full-section foot.
        wall_face = _rail_nominal_foot_face(col, sx)
        x_uw = wall_face - sx * 0.5
        drop = rail_flare_drop                    # equals abs(x_h1 - x_uw): the fall is the run
        arm = arm.fuse(_xz_prism(y0, y1, [(x_uw, zj), (x_h1, zj), (x_uw, zj - drop)]))
        # The plan taper at the OPEN end, whichever end that is: the head's lap falls back
        # to the arm's own sliding face over `rail_lead`, the cut reaching INTO the run,
        # every face of it vertical.
        lead = _xy_prism(z_foot - 1.0, rim + 1.0, (
            (x_a, y0), (x_hk - sx * 1.0, y0),
            (x_hk - sx * 1.0, y0 + sy * rail_lead)))
        arm = arm.cut(lead)
        yb0, yb1 = sorted((y1 - sy * rail_stop_len, y1))
        block = _ybox(min(x_hk, x_h1), max(x_hk, x_h1), yb0, yb1, zj, rim)
        piece = arm.fuse(block)
        out = piece if out is None else out.fuse(piece)
    return out


def _z_rail_feet(inner, y_joint, zj, col, plate, chase=()):
    """The TOP piece's foot slabs, one per rail — the material past its own wall's
    inner face that makes the mouth band a full-section FOOT for the head to stand
    over, fused before every pocket and carved to the slide's own section by the
    channel cut at the END of the piece's work.

    Each is one box: the box interior face out to the foot's face, mouth to the
    caught face, the run less the stop block — so its end face at the closed end IS
    the face that lands home. It lies on the bed of a piece that prints mouth-down,
    rooted to the wall down its whole height. On both columns it carries the full nominal
    flank section to the seam, and the hook lies over the inboard part of that foot. The
    collet plate's ends are derived from the front rail's complete moving envelope."""
    z_foot = zj + hook_foot
    out = None
    for x_in, sx, y0, y1, _lane in _z_rail_runs(inner, y_joint, col, plate, chase):
        y1 -= (1.0 if y1 > y0 else -1.0) * rail_stop_len
        _hk, x_f, _a, _h1 = _rail_x(x_in, sx, col)
        x_root = x_in - sx * 1.0
        slab = _ybox(min(x_root, x_f), max(x_root, x_f),
                     min(y0, y1), max(y0, y1), zj, z_foot)
        out = slab if out is None else out.fuse(slab)
    return out


def _rail_keep(inner):
    """The region a channel cut may reach — everything standing at least one `wall`
    inside the box's EXTERIOR surface, corner rounds included, struck off the outer
    faces rather than the interior ones so a wall thicker than `wall` is still openable
    behind its own show skin. A channel clipped to this can open the flank's own seam
    band and turn a corner into a pillar's base without ever nicking the surface it
    sweeps past."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    return _round_z(_ybox(ix0, ix1, (iy0 - front_wall) + wall, iy1,
                          iz0 - floor_t - 1.0, iz1 + wall + 1.0),
                    corner_round - wall)


def _z_rail_channels(inner, y_joint, zj, col, plate, chase=()):
    """The TOP piece's channel voids, one per rail — cut LAST of the piece's work, so
    everything the piece fused near a flank is carved to the slide's own section.

    TWO PROFILES DOWN ONE LANE. Fore of the stop face the void is the arm's berth
    and the NOTCH over the foot: inboard of the foot's face it opens from the mouth —
    the arm's own lane, `slide_slip` off its back — and outboard it opens from the
    foot's caught face up, `slide_slip` deeper than the head, stopping one slip outboard
    of the head; a 45° GABLE closes the roof `slide_slip` over the arm's cap, two
    faces rising off the channel's walls and meeting over it, so a piece that prints
    mouth-down lays nothing flat across the void — and the gable's outboard face is
    the notch's own roof, carrying the wall back out to its full section. AFT of the
    stop face the front column's void is the FULL section, mouth to gable: everything
    of that piece standing aft of the stop — the flank's own seam band, the wall
    under the lip's cavity, the Y-seam tongue's own flank segment — sweeps over the
    stop block, the head and the arm on its way in, and this is the lane it does it
    in. The back column needs no deep zone: its `lane_aft` is the stop itself,
    because the rear horizon has already emptied the lane behind it.

    THE LANE RUNS OFF THE FRONT PIECE'S AFT END. It carries the full section as far
    as `lane_aft`, past the tongue's own tip, so the flank's mouth band comes out as
    one unbroken rebate from the run to the end of the piece with no blunt face
    standing in it — and nothing aft of the run is left to be swept around, which is
    what lets the run reach its own structural limit instead of a horizon. The
    tongue crosses the seam at full section ABOVE THE GABLE, which is the height the
    Y telescope actually bears on. At the front column's Y/Z crossing the ordinary
    outboard half-gable cannot stop on the tongue's slipped outer face: that would leave
    a 0.7 mm wall standing from the bed to the roof. Its complete dependent half rises
    aft at 45 degrees from the supported Y-joint face instead, opening that remnant and
    returning the tongue as one printable corbel above it.
    The cut is CLIPPED to `_rail_keep`, so at a corner it
    stops one `wall` inside the exterior round instead of slotting the show skin. The
    channels occupy only the inboard portion of their full-section feet and leave a complete
    exterior wall plus the uncut outer edge of the foot. Both keep the flutes' whole backing
    (`flute_backed_sections`)."""
    z_foot, rim = zj + hook_foot, zj + z_rise
    z_roof = rim + slide_slip
    keep = _rail_keep(inner)
    out = None
    for x_in, sx, y0, y1, lane_aft in _z_rail_runs(inner, y_joint, col, plate,
                                                   chase):
        sy = 1.0 if y1 > y0 else -1.0
        stop = y1 - sy * rail_stop_len
        x_hk, x_f, _a, x_h1 = _rail_x(x_in, sx, col)
        # One slip outboard of the head is the channel's own standing wall. It lies in the
        # full-section foot, carrying the nominal flank through the seam while leaving a fixed
        # exterior skin and the foot's outer edge intact.
        x_open = x_hk - sx * slide_slip
        x_d = x_h1 + sx * slide_slip
        x_peak = (x_open + x_d) / 2.0
        z_peak = z_roof + abs(x_d - x_open) / 2.0
        void = _xz_prism(y0, stop, [
            (x_open, z_foot), (x_f, z_foot), (x_f, zj - 1.0), (x_d, zj - 1.0),
            (x_d, z_roof), (x_peak, z_peak), (x_open, z_roof)])
        if (lane_aft - stop) * sy > 0:
            void = void.fuse(_xz_prism(stop, lane_aft, [
                (x_open, zj - 1.0), (x_d, zj - 1.0), (x_d, z_roof),
                (x_peak, z_peak), (x_open, z_roof)]))
        if col == "front":
            # THE TWO SEAMS CROSS HERE. Front-top's Y tongue ends one running-fit slip
            # inside `x_in`, while this channel's standing wall ends at `x_open`; below
            # the ordinary roof the difference is free stock, not a bearing surface. Open
            # the outboard half all the way to `x_in`, whose clip in `_rail_keep` leaves
            # the complete exterior wall fore of the joint. Carry the inboard boundary to
            # `x_f`, the established interior face of that wall: stopping at the gable's
            # peak leaves the narrow strip between the peak and the wall face standing as
            # a separate sheet through the tongue.
            #
            # THE OUTBOARD HALF-GABLE COMES WITH IT. That roof formerly grew from the
            # thin strip, so removing only the strip would leave the gable's first lines
            # unsupported. Shear the whole dependent half upward one-for-one in Y from
            # the full wall at `y_joint`. At that root its section is exactly the old
            # half-gable and strip cap; aft of it every returning line lies on the line
            # before it. The untouched inboard half keeps its support from its own side.
            rise = lane_aft - y_joint
            floor = zj - 1.0 - rise
            crossing = _xz_prism(y_joint, lane_aft, [
                (x_f, floor), (x_in, floor), (x_in, z_roof),
                (x_open, z_roof), (x_peak, z_peak), (x_f, z_peak)])
            crossing = crossing.transformGeometry(cq.Matrix([
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 1.0, 1.0, -y_joint],
            ]))
            void = void.fuse(crossing)
        void = void.intersect(keep)
        out = void if out is None else out.fuse(void)
    return out


def _lip_ring(inner, gap, z0, z1, inset=0.0):
    """One `_lip_band` skin over a height span, less the `gap` y-span — the shape both the
    lip and the wall under it are cut from, so the two come out of one figure and fuse into
    one wall with no step where they meet.

    THE TWO ASK FOR DIFFERENT GAPS, which is the whole reason this takes one rather than
    striking it. A gap is room for a telescope, and only the lip is one. And only the lip
    takes the `inset`: it is the piece that slides."""
    ix0, ix1 = inner[0], inner[1]
    ring = _lip_band(inner, (z0, z1), inset)
    return ring.cut(_ybox(ix0 - 1.0, ix1 + 1.0, gap[0], gap[1], z0 - 1.0, z1 + 1.0))


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
    loaded corner — a blind channel down the one place the piece is asked to hold, and the
    slicer would draw its two faces as separate walls with nothing tying them."""
    return _lip_ring(inner, (y_joint, y_joint + lip_len + z_lip_y_margin),
                     inner[4], zj)


def _front_bottom_flank_skin(inner, west_cradle, y_joint, zj):
    """The extra skin inboard of front-bottom's two flanks, slab to seam mouth, WELLED on the
    west where the MQ-6's can reaches into it.

    The strips are struck like back-bottom's. THE WELL IS THE CAN AND NOT THE BOARD: the card
    itself stands the can's whole height off this flank and never enters the section, and what
    does enter is one Ø`mq6_can_yz` cylinder — so the well is that silhouette off the station
    (`enclosure_assembly.mq6_cradle`), opened one `mq6_slot_press` round, and the can bottoms on
    `lip_face_x` at the back of it.

    AND IT IS A CHUTE, not a pocket. The card comes down into its posts from above, carrying the
    can with it, so the well runs from the can's seat clear up to the seam mouth: a well closed
    over the can's crown is a well the can cannot enter. Cut here rather than left to the cradle,
    because what the cradle builds is posts standing on a face and this is the face they stand
    on. THE EAST STRIP NEEDS NO WELL: the only body against that flank is the condenser's block,
    and the block is stood off this very face."""
    lx0, lx1 = lip_face_x()
    fx0, fx1 = front_bottom_flank_face()
    west = _ybox(lx0, fx0, inner[2], y_joint, inner[4], zj)
    half = mq6_can_yz / 2.0 + mq6_slot_press
    for _sx, sy, sz in west_cradle:
        west = west.cut(_ybox(lx0 - 1.0, fx0 + 1.0,
                              sy - half, sy + half, sz - half, zj + 1.0))
    return west.fuse(_ybox(fx1, lx1, inner[2], y_joint, inner[4], zj))


def _plate_shelf(inner, plate, zj):
    """THE TWO SHELVES THE COLLET PLATE RESTS ON — front-bottom's own, at the seam mouth,
    one down each flank over the front run.

    THE STEEL IS CARRIED BY THE SEAM. Nothing in front-top holds it down: it goes in through
    that piece's bed face and `_plate_cap`'s land is over it, not under it, so what stops the
    plate falling back out the way it came is the piece the mouth closes onto. Front-bottom is
    a hollow tub across the bay at this station — it stands nothing under the steel's middle —
    but its two FLANKS run to the mouth here, `_front_bottom_flank_skin` having carried them
    to `front_bottom_flank_face`. This brings that face in the last few millimetres, under the
    plate's own ends.

    EACH END HAS ONE CONTINUOUS BEARING LAND. The widened steel reaches 1.5 mm into the flank's
    own section; `plate_shelf_land` continues another 1.5 mm inboard from that face. Together
    the standing wall and this shelf carry the outer three millimetres of the plate at each
    end, with no isolated pad and no edge supported on a line.

    ITS FORE EXTENSION ROOTS IT IN THE FLANK. The plate itself enters in Z through front-top's
    bed face and occupies only `plate["fore_y"]..plate["aft_y"]`; both actual end footprints
    stand on the complete shelf. Fore of them the prism runs to the front wall's inner plane,
    meeting the flank wherever the full-width bay and rounded exterior leave that skin.

    AND IT STANDS ONE `steel_air` UNDER THE SEAM PLANE, WHICH IS THE STEEL'S OWN BOTTOM EDGE.
    This face and `_plate_cap`'s land OPPOSE each other across the whole height of the plate,
    and only one of them may be a datum. THE LAND IS THE ONE: front-top carries both the tee
    bores the four holes have to meet and the stop the steel is pushed onto, so a datum struck
    there keeps the Z seam out of the stack entirely. This face is the other, on the other
    piece, and closing the seam is what brings it up — so struck at nominal the two would
    capture the steel's whole height between two printed faces with nothing between them, and
    a shelf that came off the bed a tenth proud would not make the plate rattle, it would stop
    the box shutting. Two opposed faces are a fit and not a datum, and the one that is not the
    datum takes the air.

    AND ITS UNDERSIDE IS A 45° BACK TO THE FLANK. This piece prints floor-down and builds in
    +Z, so a shelf struck square here would be a `plate_shelf_land + LIP_UNDERWALL` soffit
    running the length of the flank with nothing under it. Taken back at that angle it is a
    surface the print grows into off the wall it stands on — and a gusset down the flank's
    top corner besides."""
    fx0, fx1 = front_bottom_flank_face()
    t, top = plate_shelf_t, zj - steel_air
    out = None
    for x_face, x_in in ((fx0, plate["x0"] + plate_shelf_land),
                         (fx1, plate["x1"] - plate_shelf_land)):
        reach = abs(x_face - x_in)
        shelf = _xz_prism(inner[2], plate["aft_y"], [
            (x_in, top), (x_face, top),
            (x_face, top - t - reach), (x_in, top - t)])
        out = shelf if out is None else out.fuse(shelf)
    return out


def _back_bottom_flank_skin(inner, y_joint, zj):
    """The extra skin inboard of back-bottom's two flanks, slab to seam mouth.

    IT IS TWO PLAIN STRIPS and not the cavity's own offset shell, because it is not a
    telescope and it meets no corner: the lip above it still rides `lip_face_x` and still
    wraps the standing verticals, and this stands under that, between the slab and the mouth,
    where the piece is already `2 * wall` and simply becomes `back_bottom_flank_t`.

    ITS Y RUN STARTS AFT OF THE OTHER PIECE'S Y LIP and runs to the +Y wall's inner face, so
    it fuses into that wall at one end and clears the telescope at the other. That start is the
    same plane `_lip_underwall` opens its own gap to — front-bottom's tongue reaches `lip_len`
    past the joint, and a skin struck on the joint itself is a skin drawn through it."""
    lx0, lx1 = lip_face_x()
    fx0, fx1 = back_bottom_flank_face()
    y0 = y_joint + lip_len + z_lip_y_margin
    return (_ybox(lx0, fx0, y0, inner[3], inner[4], zj)
            .fuse(_ybox(fx1, lx1, y0, inner[3], inner[4], zj)))


# --- the pump bay's own machinery -------------------------------------------

def bay_x_span(inner):
    """The bay's two mouth edges: the side walls' interior planes.

    The pump-cartridge storey carries no front corner columns. This is the interior throat;
    the removable cradle continues through the former side skins to the appliance's exterior
    planes (`_cap_x_span`)."""
    return inner[0], inner[1]


def _pump_relief_regions(pump_trays):
    """One pocket per pump in the front wall's section, as (x0, x1, z0, z1, floor), struck
    off its station — across, the clamp collar's own half-width and a slip; in height, the
    head's hang under the station to the collar's crown over it; floored on
    `pump_relief_floor`, the plane the cradle's aft body reaches.

    ITS OWN Z0 IS THE LOWEST PLANE THE PUMP CARTRIDGE'S FILLED BEARING BLOCK AND EXTERIOR FACE
    REACH, so the bay floor's top is struck on it (`bay_floor_z`). `_bay_cut` recesses only the
    fixed shell perimeter below that plane for the lower running gap."""
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


def _front_relief_cuts(inner, pump_trays, slip=0.0):
    """The relief pockets cut out of the front wall: a box to each region's floor, its
    ceiling rising at `relief_chamfer` to the mouth so the pocket prints in a standing
    wall with no flat over it.

    `slip` closes each pocket in by that much on all four of its standing faces and
    stands its floor that much aft — the outline a piece standing in these pockets is
    held off the wall by, which is what the cartridge face follows."""
    iy0 = inner[2]
    cuts = []
    for x0, x1, z0, z1, floor in _front_relief_regions(pump_trays):
        x0, x1, z0, z1 = x0 + slip, x1 - slip, z0 + slip, z1 - slip
        floor = floor + slip
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
    one `front_wall` section, slab to mouth. The exterior corner skins keep their wraps and
    the front Z-joint closes in those skins rather than in an inboard pump-bay jamb."""
    bx0, bx1 = bay_x_span(inner)
    # EVERY FACE OF THIS CUT IS THE SKIN'S OWN, not a hair past it. The skin (`_lip_band`)
    # stands exactly one `wall` proud of the cavity face and bears on the slab, so a cut struck
    # on `inner[2]`, `inner[2] + wall` and `inner[4]` takes all of it and stops. Each of those
    # three planes is a face of a body this has no business in — the front wall fore, the
    # cavity aft, the floor slab below — and two of them are datums the box stands things ON.
    # `_cond_cradle`'s fore rail stands on both: it roots on `front_plane_y`, which IS
    # `inner[2]`, and its base runs down to `inner[4]`. Reaching past either leaves that rail
    # bearing on air over the whole bay span — a tenth of a millimetre clear of the wall it is
    # the datum off, bridging a millimetre notch in the slab — and joined to the piece along
    # the one line y = inner[2] + wall, z = inner[4]. That line is an edge with four faces:
    # rail and slab meeting along an arris with no volume between them, which is a
    # non-manifold edge and what a slicer refuses the file for. Aft the same rule reads off
    # the cavity — an overshoot there runs out at the jamb, where the wall has already turned,
    # and leaves faces of no width at all, six edges under a micron.
    return _ybox(bx0, bx1,
                 inner[2], inner[2] + wall,
                 inner[4], zj + z_rise + 1.0)


def _pump_full_width_band(inner, outer, bay, pump_trays, y_aft,
                          lower_inset=0.0, upper_inset=None):
    """The complete removable front-wall band, clipped only by the appliance silhouette.

    It begins on the outside of the front face, runs aft to `y_aft`, and owns both former
    front-top side skins as well as the flat face between them. The fixed opening uses neither
    inset. The cradle uses `lower_inset` and `upper_inset` for its flat running gaps above the
    sill and below the lintel. Omitting `upper_inset` keeps a symmetric inset for callers that
    state one figure."""
    upper_inset = lower_inset if upper_inset is None else upper_inset
    z0 = bay_floor_z(pump_trays)[1] + lower_inset
    z1 = bay[2] - upper_inset
    return _rounded_outer(outer).intersect(
        _ybox(outer[0] - 1.0, outer[1] + 1.0,
              outer[2] - 1.0, y_aft, z0, z1))


def _pump_cartridge_outer(outer):
    """The lower cradle's proud plan silhouette.

    Only the show plane moves. Both X faces, the rear of the appliance and the corner radius
    remain the enclosure's, so the proud face returns into the existing side skins without a
    width change or an extra corner. The pump station stays on `pump_cartridge_proud`; this
    surface carries one additional full flute depth ahead of it."""
    return (outer[0], outer[1], outer[2] - pump_show_proud,
            outer[3], outer[4], outer[5])


def _pump_upper_x_span(cx):
    """One upper insertion well's X faces, on the tube pair's exact outer boundary."""
    return cx - cap_slot_half, cx + cap_slot_half


def _pump_front_smooth_skin(pump_trays):
    """Smooth stock between the proud face and the upper insertion wells."""
    well_fore = min(cy - _tray.half_width() for _cx, cy, _cz in pump_trays) - clamp_drop_air
    return well_fore - pump_cartridge_front_y


def _pump_cartridge_front_flute_rail(outer):
    """The proud face and its two front corner returns, on the enclosure's flute datum.

    The fixed outer rail still cuts the unchanged side planes from their original tangencies
    aft. This open rail covers only the translated face and corners; the short plain side
    returns between them state the cartridge's proud step without shifting the fixed walls'
    groove phase. The show plane stands one complete groove depth ahead of the pump datum, so
    this rail carries the same uninterrupted full-depth field as the rest of the enclosure."""
    proud = _pump_cartridge_outer(outer)
    front_run = (proud[1] - proud[0] - 2.0 * corner_round) + math.pi * corner_round
    return _flute_skin.Rail(
        at=lambda s: plan_at(s, proud), length=front_run,
        start=-front_run / 2.0, closed=False)


def _pump_cartridge_side_flute_rail(outer):
    """The enclosure-phase field on the cartridge's two outer side faces.

    This open run starts at the +X front tangency, walks round the back of the box and ends at
    the -X front tangency. The proud-front rail carries the translated face and its two corner
    turns; the short returns between those turns and this run stay plain. The box's fixed front
    plane passes through the proud cartridge and is therefore not a surface of this rail."""
    segments = _plan_segments(outer)
    start = sum(length for _kind, length, _data in segments[:2])
    length = sum(length for _kind, length, _data in segments[2:7])
    return _flute_skin.Rail(
        at=lambda s: plan_at(s, outer), length=length,
        start=start, closed=False)


def _bay_cut(inner, outer, bay, pump_trays, plate):
    """The bay's opening through front-top: the complete exterior width and complete cradle
    height, from the bay floor to the bay top and from the show face to the steel's aft face.

    The lower cradle replaces every part of the fixed front wall and both fixed side skins in
    this band. The opening's own lower edge is `bay_floor_z`'s top, which is the plane the
    cradle beds on and the plane the fixed shell perimeter stops on — the cartridge begins on
    one print-bed plane and the sill it stands over is that same plane. The plate-retention
    cheeks are added after this cut and the cradle carries two local clearance notches."""
    return _pump_full_width_band(
        inner, outer, bay, pump_trays, plate["aft_y"], lower_inset=0.0)


def _plate_fore_guides(inner, outer, bay, plate, pump_trays):
    """The fixed cheeks that retain the collet plate against fore pitch, with two stop heads.

    THE RELEASE LOAD EXISTS AFTER THE PUMP CARTRIDGE HAS MOVED. Four tee noses press the steel
    fore as their tubes draw out, so the plate cannot answer to a pump-cartridge-mounted keeper:
    what stays with the box is what must take that moment. Two fore cheeks stand on the
    plate's outer tails, wholly outside the pump cartridge's X sweep, and leave `plate_slot_slip`
    to the steel. Together with the tee wall behind it they make a vertical channel: the
    plate rises in Z on the way in, and its top cannot rotate fore about the floor's slot.

    THE CHEEK IS A WEDGE IN PLAN, AND IT IS ONE PRISM. Its fore face stands
    `plate_guide_wedge` further fore at the fixed outer wall than at its inboard face, so the
    section taking that moment is deepest where the cheek is rooted in the side wall and
    thinnest where it has the tee wall closest behind it. The rake is the cheek's WHOLE
    HEIGHT and not a band in it: a plan that never changes with Z extrudes, every face of it
    is a plane, every wall is vertical and supported, and nothing anywhere in it overhangs.

    AND IT STANDS THE WHOLE STOREY. The cheek is rooted in the fixed side wall and loaded at
    the top of the steel, so height is section where the moment is: taken to the bay's own
    ceiling it is a post between two slabs rather than a fin cantilevered off the floor, and
    it gives the flank opening the aft jamb that opening otherwise has only up to the plate.
    The full-width pump cartridge carries an aft-corner notch round each cheek. Its edge follows
    the cheek's exact rake one `fits.slip` fore of it; fore of those notches the drawer still
    takes the whole cavity width, including both grip ledges. Any guidance the cheeks
    incidentally give the cartridge is not their function.

    EACH CHEEK RETURNS IMMEDIATELY OUTSIDE THE PLATE'S SLOT. At the slot-end plane — one
    `plate_slot_slip` beyond the cut steel — the same prism turns aft past the plate and
    carries the complete `plate_end_stock` band into the outer wall. That return stands from
    the bay floor through the whole storey: there is no horizontal shelf at the floor and no
    open column left over from a plate inserted from the other direction.

    THE HEAD CLOSES THE CHANNEL OVER THE STEEL'S TAIL. Over each of them the head reaches aft
    to the tee wall's fore face and stands from the steel's own top edge to the same ceiling:
    what `_plate_cap` does across the middle, this does at the ends, and here it is a square
    land rather than a raked one because the cheek is standing under its fore side. That
    underside spans `PLATE_T + plate_slot_slip` between two standing walls, the cheek fore and
    the tee wall aft.

    AND IT STANDS ON THE CHEEK'S OWN FORE PLANE, `y_front`, so the cheek's inboard face is ONE
    plane the whole storey — from the bay floor to the ceiling, at `x_inner`, on `y_front`.
    What is fore of the steel's top edge there is the head's, and it is the same section the
    cheek carries under it."""
    guide_x0, guide_x1 = plate_guide_inner_xs(plate)
    slot_x0 = plate["x0"] - plate_slot_slip
    slot_x1 = plate["x1"] + plate_slot_slip
    y_back = plate["fore_y"] - plate_slot_slip
    y_front = y_back - wall
    z0 = bay_floor_z(pump_trays)[1] - 1.0
    z_stop = plate["z1"]
    z1 = bay_storey_z(bay)[1]
    out = None
    for (x_inner, x_outer, return_inner), (hx0, hx1) in zip(
            ((guide_x0, outer[0], slot_x0),
             (guide_x1, outer[1], slot_x1)),
            plate_head_spans(inner, plate)):
        spine_aft = plate["aft_y"] + wall
        guide = _xy_prism(z0, z1, (
            (x_inner, y_front), (x_inner, y_back),
            (return_inner, y_back), (return_inner, spine_aft),
            (x_outer, spine_aft), (x_outer, y_front - plate_guide_wedge)))
        head = _ybox(hx0, hx1, y_front, plate["aft_y"], z_stop, z1)  # the tail's own cap
        out = guide.fuse(head) if out is None else out.fuse(guide).fuse(head)
    return out


def plate_guide_fore_y(plate):
    """THE BAY'S AFT WALL OVER THE STEEL'S TOP EDGE — one plane, wall to wall.

    `plate_slot_slip` and one `wall` fore of the plate's own fore face: the plane
    `_plate_fore_guides` stands both cheeks on for their whole height, carried across the
    middle by `_plate_cap` above its printable 45° underside and out over each tail by that
    guide's own head. The cheeks therefore keep this face from the bay floor to the ceiling;
    the middle wall reaches the same plane where its corbel ends."""
    return plate["fore_y"] - plate_slot_slip - wall


def plate_guide_notch_fore_y(plate):
    """The outermost Y− edge of the cradle's raked plate-retention clearance."""
    return plate_guide_fore_y(plate) - plate_guide_wedge - fits.slip


def plate_guide_inner_xs(plate):
    """Each fixed fore cheek's inboard X face, struck on the collet plate's outer tails."""
    return plate["x0"] + plate_guide_tail_land, plate["x1"] - plate_guide_tail_land


def plate_head_spans(inner, plate):
    """The X span of each of the two heads the collet plate is pushed up to
    (`_plate_fore_guides`) — the cheek's own inboard face out to the side wall.

    One per outer tail. The pump cartridge's aft-corner notches pass these heads while the
    rest of the drawer keeps the full cavity span."""
    guide_x0, guide_x1 = plate_guide_inner_xs(plate)
    return [(inner[0], guide_x0), (guide_x1, inner[1])]


def _plate_retention_clearance_notches(outer, bay, plate, pump_trays):
    """Two raked corner clearances for the fixed plate-retention cheeks.

    Each four-sided prism follows its cheek's exact plan angle, shifted one ``fits.slip``
    toward Y−. The cartridge's Y=``pump_cartridge_aft_y`` plane truncates that rake, so only
    the actual corner overlap is removed; no rectangular slot runs to the cheek's inboard X
    face. The fixed material retains the stainless plate. Any guidance it incidentally gives
    the cartridge is not its function."""
    guide_x0, guide_x1 = plate_guide_inner_xs(plate)
    y_inner = plate_guide_fore_y(plate) - fits.slip
    y_aft = pump_cartridge_aft_y(pump_trays) + 1.0
    z0 = bay_floor_z(pump_trays)[1] - 1.0
    z1 = bay[2] + 1.0
    run = outer[1] - guide_x1
    if run <= 0.0:
        raise ValueError("a plate-retention cheek needs positive X run to the outer wall")
    rake = plate_guide_wedge / run
    left_outer = outer[0] - 1.0
    right_outer = outer[1] + 1.0
    left_outer_y = y_inner - rake * (guide_x0 - left_outer)
    right_outer_y = y_inner - rake * (right_outer - guide_x1)
    return (
        _xy_prism(z0, z1, (
            (left_outer, left_outer_y), (guide_x0, y_inner),
            (guide_x0, y_aft), (left_outer, y_aft))),
        _xy_prism(z0, z1, (
            (guide_x1, y_inner), (right_outer, right_outer_y),
            (right_outer, y_aft), (guide_x1, y_aft))),
    )


def plate_cap_fore_z(plate):
    """The one uninterrupted front edge of the plate cap's 45-degree underside."""
    fore, aft = plate_guide_fore_y(plate), plate["aft_y"]
    land = aft - plate_cap_land
    return plate["z1"] + (land - fore)


def _plate_cap(inner, plate, bay, pump_trays):
    """THE WALL OVER THE COLLET PLATE: the steel's lane filled from its top edge to the bay's
    ceiling, standing on the tee wall's fore face.

    THE STEEL COMES IN THROUGH THE BED FACE, so what is over it is the box's to keep. A plate
    dropped in from Z+ needs its lane open above it for the whole of its own height — that is
    what a drop-in IS — and every millimetre of that lane is a millimetre the piece cannot
    carry. Fed up from the seam plane the plate needs no room over its head at all, and this
    is what stands in the room it gives back.

    ITS LAND IS THE PLATE'S Z DATUM. `plate_cap_land` of flat, taken off the tee wall's fore
    face at the steel's own `z1`, runs the whole width: the top edge comes up onto it and
    stops there, which is the one stop in this joint and the only reason the outline needs no
    shoulder. Over the two tails `_plate_fore_guides`' heads carry that same plane out to the
    side walls, so the seat is one continuous land from wall to wall.

    FORE OF THE LAND ITS UNDERSIDE RAKES AT 45°, to `plate_guide_fore_y`. The pumps' forward
    station leaves their loaded brackets clear of this nominal corbel, so its front edge is one
    straight line across the complete width. The lane under it
    is air at print time — the steel is not in the piece yet — so a square ceiling `PLATE_T`
    wide would be a ledge hanging off the tee wall for the whole width of the machine. Raked,
    it is a surface the print grows into off the wall it stands on, and the lowest line of it
    sits directly over the steel's aft top arris, which is the arris the land is already on.

    AND ITS FORE FACE IS `plate_guide_fore_y`, the plane the two fixed cheeks already stand
    on. The cheeks, their heads and the cap present the drawer one surface with no arris at
    either cheek. The pump cartridge's back stands `cap_kiss` fore of it there, and `cap_kiss`
    fore of the steel below."""
    z_land = plate["z1"]
    fore, aft = plate_guide_fore_y(plate), plate["aft_y"]
    land = aft - plate_cap_land
    return _yz_prism(inner[0], inner[1], (
        (aft, z_land), (land, z_land), (fore, plate_cap_fore_z(plate)),
        (fore, bay[2]), (aft, bay[2])))


def _front_top_flank_bedding_cut(inner, y0, y1, zj):
    """The air under front-top's two grown flank faces over one Y band.

    Each physical flank begins on the seam rim at the box's interior face and rises at 45
    degrees to its own six-millimetre-inboard face. Below that start the room side is open all
    the way to the bed. Material belonging to another construction may meet the face, but may
    not continue below either part of that boundary as a second, offset skin. Keeping the exact
    two prisms in one helper lets the flank itself, the Y tongue and a wall-to-wall valve tray
    all finish on the same planes."""
    ix0, ix1 = inner[0], inner[1]
    fx0, fx1 = front_top_flank_face()
    rim = zj + z_rise
    out = None
    for x_in, x_face in ((ix0, fx0), (ix1, fx1)):
        cut = _xz_prism(y0, y1, [
            (x_in, zj - 1.0), (x_face, zj - 1.0),
            (x_face, rim + abs(x_face - x_in)),
            (x_in, rim),
        ])
        out = cut if out is None else out.fuse(cut)
    return out


def _front_top_flanks(inner, outer, box, y_joint, zj):
    """THE SECTION FRONT-TOP'S ±X WALLS CARRY BEYOND `wall`, standing inboard of `interior_x`
    (`front_top_flank_t`). Fused before any of this piece's flank furniture, so a pocket, a
    well or a port cut afterwards is cut out of the whole of it.

    THE FACE CONTINUES THROUGH THE SEAM AS EACH RAIL'S FOOT. `_z_rail_feet` carries the
    section from `interior_x` to this same nominal face, mouth to caught face. Front-bottom's
    head overlaps the inboard five millimetres of that foot and places its arm one
    `slide_slip` beyond it (`_z_rail_heads`). The channel cut then carves the arm's berth and
    its 45° roof out of only that inboard stock. The mouth bears on the shoulder; the rails
    register and retain.

    AND THE COLLET PLATE KEEPS ITS BERTH. The steel stands `plate_step_in` off `interior_x`,
    beyond the rail's deepest moving face and its two distinct clearances. Its own band comes
    out of this section — `PLATE_T` of depth over the steel's height and nothing above it,
    which is why the plate is not a figure this reads: it is a berth cut through it."""
    ix0, ix1, _iy0, _iy1, _iz0, iz1 = inner
    fx0, fx1 = front_top_flank_face()
    plate = box.pack.collet_plate
    y0, y1 = outer[2] - 1.0, y_joint + lip_len
    rim = zj + z_rise
    band = None
    for x_in, x_face in ((ix0, fx0), (ix1, fx1)):
        seg = _ybox(min(x_in, x_face), max(x_in, x_face), y0, y1, rim, iz1)
        band = seg if band is None else band.fuse(seg)
    # AND ITS UNDERSIDE RISES AT `relief_chamfer` INSTEAD OF HANGING. This piece beds on
    # its own seam rim and builds in +Z, so a section square at the rim would put a
    # `depth`-wide ledge over the tongue's lane pointing straight at the plate — the
    # soffit `_lip_underwall` exists one storey down to avoid. Taken back at 45° it is a
    # wall the print grows into off the flank it stands on. The same helper finishes every
    # construction which meets this face.
    band = band.cut(_front_top_flank_bedding_cut(inner, y0 - 1.0, y1 + 1.0, zj))
    # The steel's own berth, up to its top edge and no further: over that plane the lane is
    # `_plate_cap`'s and this section may stand in it.
    band = band.cut(_ybox(ix0 - 1.0, ix1 + 1.0, plate["fore_y"], plate["aft_y"],
                          plate["z0"] - 1.0, plate["z1"]))
    # Everything this piece's own walls were already bored for, struck out before the section
    # is fused rather than re-cut after it: the Y seam's bosses, whose cuts were made in
    # `build_front_half`, and the panel holes through both faces.
    yb = _y_boss(y_joint)
    for x_in, x_ext, sx, z_boss in box.y_bosses:
        band = band.cut(_front_cuts(x_in, x_ext, sx, z_boss, yb, y_joint))
    for cutter in _port_cuts(box.pack.front_ports, outer[2] - 5.0, inner[2] + 5.0):
        band = band.cut(cutter)
    for cutter in _x_port_cuts(box.pack.east_ports, fx1 - 5.0, outer[1] + 5.0):
        band = band.cut(cutter)
    for cutter in _x_port_cuts(box.pack.west_ports, outer[0] - 5.0, fx0 + 5.0):
        band = band.cut(cutter)
    return band.cut(_front_top_flank_relief_cut())


def _front_top_flank_relief_cut():
    """The −X flank's one relief, floored on `lip_face_x` with its roof rising at
    `relief_chamfer` to the mouth.

    THE ROOF IS THE ONLY FACE THAT NEEDS THE ANGLE. front-top prints mouth-down on its seam
    rim, so it builds in +Z: the pocket's floor is printed on, its two ends are vertical, and
    what would otherwise be laid over air is the run at `z1`. The ramp takes that back to the
    mouth over its own depth, so nothing in it is flat over a hole."""
    y0, y1, z0, z1 = front_top_flank_relief
    face = front_top_flank_face()[0]
    floor = lip_face_x()[0]
    depth = abs(face - floor)
    box_ = _ybox(min(face, floor), max(face, floor), y0, y1, z0, z1 - depth)
    ramp = _xz_prism(y0, y1, [(face, z1 - depth), (floor, z1 - depth), (face, z1)])
    return box_.fuse(ramp)


def _back_top_wall(inner, outer, box, zj):
    """THE SECTION BACK-TOP'S +Y WALL CARRIES BEYOND `wall`, standing inboard of `rear_plane_y`
    (`back_top_wall_t`). Fused before this piece's own back-wall work, so the port field's
    pockets, the C14's bores and the nameplate's seat are all cut out of the whole of it.

    IT BEGINS AT THE RIM AND NOT AT THE MOUTH. What stands in this wall below the rim is
    back-bottom's own tongue, and the lane it rises into is exactly the section this would add —
    so there is nothing to add there. Below the rim that wall is already `2 * wall`, carried to
    the slab as the lip's own skin (`_lip_underwall`); above it, this. One section, top to
    bottom, and the rim is where the two meet rather than a step in either.

    AND ITS UNDERSIDE RISES AT `relief_chamfer` INSTEAD OF HANGING, the way `_back_top_flanks`'
    does on the two walls that turn out of this one. This piece beds on its own seam rim and
    builds in +Z, so a section that began square at the rim would put a `depth`-wide soffit the
    machine's whole width over the lip's lane. Taken back at 45° it is a wall the print grows
    into, and what the ramp gives up is `depth` of height in a band the lip's travel never
    reaches."""
    ix0, ix1, _iy0, iy1, _iz0, iz1 = inner
    rim, depth = zj + z_rise, back_top_wall_t - wall
    band = _ybox(ix0, ix1, back_top_wall_face(), iy1, rim, iz1)
    band = band.cut(_yz_prism(ix0 - 1.0, ix1 + 1.0,
                              [(iy1, rim), (back_top_wall_face(), rim),
                               (back_top_wall_face(), rim + depth)]))
    # The wall's own holes, bored in `build_back_half` before this stood here.
    for cutter in _port_cuts(box.pack.back_ports, iy1 - 5.0, outer[3] + 5.0):
        band = band.cut(cutter)
    return band.cut(_back_top_wall_relief_cut())


def _back_top_wall_relief_cut():
    """Every station's relief, floored on `rear_plane_y` with its roof rising at
    `relief_chamfer` to the mouth — what clamps on this face lands on the section it always had.

    THE ROOF IS THE ONLY FACE THAT NEEDS THE ANGLE, the same way the pump reliefs' ceilings do:
    back-top prints mouth-down on its seam rim and builds in +Z, so the pocket's floor is printed
    on and its two sides are vertical, and what would be laid over air is the run at the top."""
    face, floor = back_top_wall_face(), rear_plane_y
    depth = floor - face
    out = None
    for _who, rx, rz, wx, wz in back_top_wall_reliefs:
        hx, hz = wx / 2.0, wz / 2.0
        cut = _ybox(rx - hx, rx + hx, face, floor, rz - hz, rz + hz - depth)
        cut = cut.fuse(_yz_prism(rx - hx, rx + hx,
                                 [(face, rz + hz - depth), (floor, rz + hz - depth),
                                  (face, rz + hz)]))
        out = cut if out is None else out.fuse(cut)
    return out


def back_top_flank_start(y_joint):
    """Where back-top's own flank section begins — past BOTH telescopes, so it costs the seams
    nothing. The front half's Y lip runs to `y_joint + lip_len` on this wall surface
    (`_front_lip`); `z_lip_y_margin` past that rim is the first plane the closing front half
    never lands on, and everything this piece stands on its own flank starts there."""
    return y_joint + lip_len + z_lip_y_margin


def _back_top_flank_relief_cut(box):
    """The named pockets in back-top's nominal ±X section.

    Each floor is the corresponding `lip_face_x` plane, so six millimetres of wall remain at
    the relieved station. Back-top prints on its Z-seam rim and grows in +Z: the routed pocket's
    floor and ends are supported faces, while its roof rises 45 degrees from the six-millimetre
    floor to the nine-millimetre nominal face instead of bridging the pocket's depth.

    The ASSE anchor's two zip-tie cavities open upward into the service air under the ceiling.
    Their bands come from the placed cradle, so the added flank stock gives up exactly those two
    mouths from the cavity's own west edge to the nominal face. They run to the ceiling and need
    no roof: the ceiling-strip corbel gives up the same bands in `back_top_ceiling_reliefs`."""
    faces, floors = back_top_flank_face(), lip_face_x()
    out = None
    for _who, side, y0, y1, z0, z1 in back_top_flank_reliefs:
        i = 1 if side > 0 else 0
        face, floor = faces[i], floors[i]
        depth = abs(face - floor)
        cut = _ybox(min(face, floor), max(face, floor), y0, y1, z0, z1 - depth)
        cut = cut.fuse(_xz_prism(
            y0, y1, [(face, z1 - depth), (floor, z1 - depth), (face, z1)]))
        out = cut if out is None else out.fuse(cut)
    if box.pack.asse_cradle:
        z_axis, _sections, ties, _dn = box.pack.asse_cradle
        face, floor = faces[0], floors[0]
        mouth_z = z_axis + asse_cradle_up + 1.0
        for ty in ties:
            cut = _ybox(min(face, floor), max(face, floor),
                        ty - tie_cav_wide_w / 2.0, ty + tie_cav_wide_w / 2.0,
                        mouth_z, box.inner[5] + 1.0)
            out = cut if out is None else out.fuse(cut)
    return out


def _back_top_flanks(inner, outer, box, y_joint, zj):
    """THE SECTION BACK-TOP'S ±X WALLS CARRY BEYOND `wall`, standing inboard of `interior_x`
    (`back_top_flank_t`). Fused before any of this piece's flank furniture, so the Wago wells,
    the +X mounting bosses and every bore below are cut out of the whole of it.

    IT BEGINS PAST THE Y TELESCOPE. The front half's lip runs to `y_joint + lip_len` on this
    wall surface (`_front_lip`), and in Y the band starts where `_lip_underwall` starts one
    storey down, `z_lip_y_margin` past that rim, so the closing front half never lands on its
    step. In Z the nominal band starts over the hooked rail's rim, the way `_back_top_wall`
    does; below it `_z_rail_feet` carries the full nominal section from the seam mouth to the
    caught face, with the arm and its broad back-column head placed at that face's inboard edge.
    The channel cut runs last and opens exactly that moving profile. Every Y-seam screw stands
    fore of this Y, so none of its plug or socket geometry grows.

    AND THE PAN'S SLEEVE KEEPS ITS BLOCK. The ASSE drip pan withdraws through this flank, and the
    pack states the sleeve as one box rooted on the wall's own inner face with the berth cut back
    out of it (`_pan_sleeve`). Struck out of this section rather than re-cut through it: the tray
    stays where it is and at the size it is, and what stands round it is the sleeve's own section
    instead of this one."""
    ix0, ix1, _iy0, iy1, _iz0, iz1 = inner
    fx0, fx1 = back_top_flank_face()
    y0, rim = back_top_flank_start(y_joint), zj + z_rise
    depth = back_top_flank_t - wall
    band = None
    for x_in, x_face in ((ix0, fx0), (ix1, fx1)):
        seg = _ybox(min(x_in, x_face), max(x_in, x_face), y0, iy1, rim, iz1)
        # AND ITS UNDERSIDE RISES AT `relief_chamfer` INSTEAD OF HANGING. This piece beds on
        # its own seam rim and builds in +Z, so a section that began square at the rim would
        # put a `depth`-wide ledge over the lip's lane pointing straight at the plate — the
        # soffit `_lip_underwall` exists one storey down to avoid. Taken back at 45° it is a
        # wall the print grows into, and what the ramp gives up is `depth` of height in a band
        # that has nothing standing in it.
        seg = seg.cut(_xz_prism(y0 - 1.0, iy1 + 1.0,
                                [(x_in, rim), (x_face, rim), (x_face, rim + depth)]))
        band = seg if band is None else band.fuse(seg)
    for bx0, bx1, by0, by1, bz0, bz1 in box.pack.pan_sleeve[0]:
        band = band.cut(_ybox(bx0 - 1.0, bx1 + 1.0, by0, by1, bz0, bz1))
        # AND WHERE IT RESUMES OVER THE BLOCK'S LID IT RISES AT `relief_chamfer` TOO, the same
        # ramp on the same plane it takes at the rim: what the block's mouth leaves standing
        # here is this section's `depth`, and struck square it is a ledge over the pan's opening.
        band = band.cut(_xz_prism(by0, by1,
                                  [(bx0, bz1), (fx0, bz1), (fx0, bz1 + depth)]))
    # The PRV chase stands its own share of this band later (`_vent_chase`): each piece
    # carries the height of the rib it owns, so neither crosses into the other's travel.
    # The one thing this wall was already bored for on the back half: the tray's own withdrawal
    # slot, cut in `build_back_half` before this stood here.
    for cutter in _x_port_cuts(box.pack.west_ports, outer[0] - 5.0, fx0 + 5.0):
        band = band.cut(cutter)
    relief = _back_top_flank_relief_cut(box)
    return band.cut(relief) if relief is not None else band


def _back_top_ceiling_corbel_at(inner, y_joint, sx, face_z):
    """One complete back-top ceiling-strip corbel on the physical face handed in."""
    cp = _ceiling()
    lane_z = inner[5]
    half, wall_x = cp.panel_half_w, back_top_flank_face()[1 if sx > 0.0 else 0]
    edge, deep = sx * half, abs(wall_x) - half

    def section(edge_x, depth):
        points = [(edge_x, face_z)]
        if face_z < lane_z - 1e-9:
            points.append((edge_x, lane_z))
        points.extend(((wall_x, lane_z), (wall_x, face_z - depth)))
        return points

    corbel = _xz_prism(cp.fore_y, cp.aft_y, section(edge, deep))
    fore_deep = abs(wall_x) - cp.dado_blind_x
    return corbel.fuse(_xz_prism(
        back_top_flank_start(y_joint), cp.fore_y,
        section(sx * cp.dado_blind_x, fore_deep)))


def _back_top_ceiling_corbel(inner, y_joint, sx):
    """One complete, grown and unrelieved back-top ceiling-strip corbel.

    The main run rises from the six-millimetre physical face to the slide-in panel's edge. Ahead of the
    panel it follows the dado's blind edge instead, ending at the first plane the Y telescope
    cannot reach. `_back_top_ceiling` cuts only the named body bands from this exact solid, and
    the assembly clearance gates use it unchanged when a placed body is expected to need no
    relief at all."""
    return _back_top_ceiling_corbel_at(inner, y_joint, sx, _ceiling().fixed_under_z)


def _back_top_ceiling_growth(inner, y_joint, sx):
    """Only the three-millimetre shell added below the established printable corbel."""
    grown = _back_top_ceiling_corbel(inner, y_joint, sx)
    established = _back_top_ceiling_corbel_at(inner, y_joint, sx, inner[5])
    return grown.cut(established)


def _back_top_ceiling_grown_for_pack(inner, y_joint, sx, growth_reliefs):
    """The grown corbel after exact placed-body plans withhold only its added shell."""
    cp = _ceiling()
    wall_x = back_top_flank_face()[1 if sx > 0.0 else 0]
    deep = abs(wall_x) - cp.panel_half_w
    corbel = _back_top_ceiling_corbel(inner, y_joint, sx)
    growth = _back_top_ceiling_growth(inner, y_joint, sx)
    for _who, rsx, x0, x1, y0, y1 in growth_reliefs:
        if rsx == sx:
            corbel = corbel.cut(growth.intersect(_ybox(
                x0, x1, y0, y1,
                cp.fixed_under_z - deep - 1.0, inner[5] + 1.0)))
    return corbel


def _back_top_ceiling_relief_gables(inner, who):
    """The two 45 degree roof prisms which close one named ceiling relief in Y.

    The relief still removes the X-wall corbel where the purchased body stands. This solid fills
    the resulting flat roof from both untouched Y ends to a zero-area ridge, so its first layers
    root in the wall corbel and every following layer advances at 45 degrees. Keeping this as a
    production helper lets the assembly gate compare the exact same solid to the exact body.
    """
    try:
        ridge = back_top_ceiling_gables[who]
        _name, sx, y0, y1, keep, out = next(
            row for row in back_top_ceiling_reliefs if row[0] == who)
    except (KeyError, StopIteration) as exc:
        raise ValueError(f"{who!r} has no stated back-top ceiling relief gable") from exc
    cp = _ceiling()
    iz1 = inner[5]
    wall_x = back_top_flank_face()[1 if sx > 0.0 else 0]
    # A six-millimetre tongue moves the dado's blind wall through the old gable's inboard edge.
    # The printable roof begins on the fixed side of that groove: leaving the nominal gable in
    # the moving lane would only let the later dado cutter silently remove it.
    xa = sx * max(cp.panel_half_w + keep, cp.dado_blind_x)
    xb = sx * min(cp.panel_half_w + out, abs(wall_x))
    x0, x1 = min(xa, xb), max(xa, xb)
    return (
        _yz_prism(x0, x1, [
            (y0, iz1 - (ridge - y0)), (ridge, iz1), (y0, iz1)]),
        _yz_prism(x0, x1, [
            (ridge, iz1), (y1, iz1 - (y1 - ridge)), (y1, iz1)]),
    )


def _back_top_ceiling_for_pack(inner, y_joint, sx, box, *, grown=True):
    """One finished fixed-strip corbel, with growth and every named relief applied.

    This is the production solid before unrelated back-top furniture cuts it. Keeping the
    complete ceiling operation in one helper gives the assembly gates the same exact B-rep the
    piece receives: the established wedge, its added three-millimetre shell, local growth-only
    body pockets, the older run-band reliefs and their printable Y gables.
    """
    cp = _ceiling()
    wall_x = back_top_flank_face()[1 if sx > 0.0 else 0]
    deep = abs(wall_x) - cp.panel_half_w
    corbel = (_back_top_ceiling_grown_for_pack(
        inner, y_joint, sx, box.pack.ceiling_growth_reliefs)
        if grown else _back_top_ceiling_corbel_at(inner, y_joint, sx, inner[5]))
    for who, rsx, y0, y1, keep, out in back_top_ceiling_reliefs:
        if rsx != sx:
            continue
        if not 0.0 <= keep <= out <= deep + 1e-9:
            raise ValueError(
                f"_back_top_ceiling: the {who} relief gives up the run band {keep:g}..{out:g} "
                f"of a strip that is {deep:g} mm wide. A relief takes a BAND of the run and "
                "leaves the strip either side of it, so both figures stand between nothing "
                "and `ceiling_panel.rail_run` and the inboard one comes first.")
        # A band reaching the strip's own edge is cut a millimetre past it, so the corbel and
        # the wall it roots on never meet along a coincident plane.
        kept = sx * (cp.panel_half_w + keep)
        outb = sx * (abs(wall_x) + 1.0 if out >= deep - 1e-9
                     else cp.panel_half_w + out)
        corbel = corbel.cut(_ybox(
            min(kept, outb), max(kept, outb), y0, y1,
            cp.fixed_under_z - deep - 1.0, inner[5] + 1.0))
        if who in back_top_ceiling_gables:
            for roof in _back_top_ceiling_relief_gables(inner, who):
                corbel = corbel.fuse(roof)
    return corbel


def _back_top_ceiling(solid, inner, y_joint, box):
    """WHAT BACK-TOP KEEPS OF ITS CEILING, and what it gives the slide-in panel — the field taken
    away between the two side strips, each strip corbelled and relieved where a body stands in it,
    the panel's dado down each strip's inboard face, and a transverse keeper socket immediately
    ahead of each tongue end.

    FUSED AND CUT BEFORE THIS PIECE'S OWN FURNITURE, the way its two sections are: the ASSE anchor's V,
    the chain's bores, the Wago wells and every bore below are cut AFTER this, so each is cut out
    of whatever the corbel put there rather than filling a pocket back in.

    THE DADO RUNS FROM THE OPEN Y− MOUTH AFT, and that is the whole of how the panel gets in: it
    is slid the length of the piece with its tongues in these two grooves, before back-top meets
    another quadrant. So the groove starts on the seam plane, not on the panel's own fore edge.

    THE KEEPER IS A CROSS-PIN, NOT A CLAMP. The dados already carry X and Z and the +Y wall is the
    home stop; only travel back toward the open mouth remains. Once the panel is home, one
    headless M3 screw is driven outboard across each empty dado mouth into a horizontal heat-set
    buried in the existing corbel. The tongue bears on the steel pin, and the pin bears directly
    in the fixed strip around its approach tunnel. Nothing hangs below the field, nothing is
    added to the moving panel, and both show faces remain whole.

    THE INSERTS ENTER FROM THE SAME OPEN FIELD. Their larger guide tunnels start at the dado's
    blind wall and step down to the knurl bores where the corbel has the standard ligament around
    them. The panel crosses these stations before the pins exist; the two screws are installed
    only after its aft edge has reached the +Y wall."""
    cp = _ceiling()
    half = cp.panel_half_w
    mouth_x, blind_x, floor_z, roof_z, chamfer = cp.dado()

    # THE FIELD. The panel carries the top wall's own section over its whole footprint, so what
    # this piece gives up is exactly that footprint and nothing under it.
    solid = solid.cut(_ybox(
        -half, half, cp.fore_y, cp.aft_y, cp.fixed_under_z, cp.show_z + 1.0))

    # THE TWO STRIPS. Each corbel is cut to its reliefs BEFORE it is fused, so a relief takes the
    # corbel and never the anchor, the flank section or the wall standing behind it.
    #
    # AND THE STRIP RUNS FORE OF THE FIELD, on the DADO'S BLIND END rather than the panel's edge.
    # There is no panel beside it there and no field to take away: the top wall fore of `fore_y`
    # is what the dado's own cut leaves of it, so that plane is the strip's inboard edge and the
    # wedge is struck from it. It stops fore where the flank section does
    # (`back_top_flank_start`), which is the first plane the closing front half never lands on —
    # ahead of that the ceiling is the mouth the front lip telescopes through, and a corbel there
    # would be drawn inside the lip's own lane.
    for sx in (+1.0, -1.0):
        solid = solid.fuse(_back_top_ceiling_for_pack(inner, y_joint, sx, box))

    # THE DADO, one down each strip's inboard face, on the section the panel states. It is cut
    # OPEN at both ends: its mouth one millimetre into the field, which is the panel's own lane,
    # and its blind end its own depth INTO the +Y wall, which is the panel's stop. A groove
    # ending exactly on either plane would leave the strip and the thing it runs out on meeting
    # along a line, which is a knife edge in the solid and a non-manifold edge in the mesh.
    #
    # THE RAMP IS THE FIELD'S AND THE LAST `depth` IS A RUN-OUT. Beside the field the groove's
    # roof rises to the show face at the mouth, and both the rise and the millimetre of overrun
    # past the mouth are the panel's own lane: this piece has no top wall inboard of that plane
    # to carry either. AFT OF THE FIELD IT HAS ONE. The blind end runs its own depth INTO the
    # +Y wall, and there the section is continuous across the mouth plane — there is no free
    # standing lip to feather and nothing to stand a ramp under. A ramp cut there lands its apex
    # in the MIDDLE of the show face rather than on its edge, which is three faces on one line
    # and a mesh a slicer refuses, and an overrun cut there opens a slot straight through the top
    # wall. So the last `depth` is the groove's RUN-OUT and takes the blind end's own section
    # carried square through it — floor to `roof_z`, with the rest of the top wall bridging the
    # mouth plane over it — a `depth`-wide bridge from the strip to the wall, `wall - lip_t`
    # thick, where beside the field that same section is the lip that feathers to nothing.
    slope, depth = math.tan(math.radians(chamfer)), blind_x - mouth_x
    over = 1.0
    for sx in (+1.0, -1.0):
        solid = solid.cut(_xz_prism(y_joint, cp.aft_y, [
            (sx * (mouth_x - over), floor_z),
            (sx * blind_x, floor_z),
            (sx * blind_x, roof_z),
            (sx * (mouth_x - over), roof_z + (depth + over) * slope)]))
        solid = solid.cut(_ybox(min(sx * mouth_x, sx * blind_x), max(sx * mouth_x, sx * blind_x),
                                cp.aft_y, cp.aft_y + depth, floor_z, roof_z))

    # THE TWO HORIZONTAL INSERT SOCKETS. The guide is large enough to pass a ruthex short from
    # the open field and steps down to the insert's Ø4 knurl bore only where the existing corbel
    # has `boss_ligament` below it. Both cuts keep their complete nominal circles and add the same
    # tangent 36-degree roof every other horizontal X bore in this standing print takes: the
    # insert and screw still pass in a round bore, while no circular crown asks the slicer for a
    # short support grown from the dado below. The bore continues one `mount_bore_relief` past the
    # insert, so the keeper's cup point cannot bottom on PET-GF and jack the pin back into the
    # field. A headless screw later occupies the same axis, crossing the wall-square rail lane
    # immediately ahead of the panel; no fixed material crosses that lane.
    for sx, cy, cz in cp.retainer_stations():
        guide0, guide1 = sorted((sx * cp.retainer_guide_face_x,
                                  sx * cp.retainer_insert_face_x))
        bore0, bore1 = sorted((sx * cp.retainer_insert_face_x,
                               sx * cp.retainer_bore_end_x))
        solid = solid.cut(_teardrop_x(cp.retainer_approach_d / 2.0,
                                      cy, cz, guide0, guide1))
        solid = solid.cut(_teardrop_x(heatset_dia / 2.0, cy, cz, bore0, bore1))
    return solid


def _pump_cartridge_face_region(inner, outer, bay, pump_trays):
    """The exterior shell the lower cradle owns.

    It spans the complete rounded front and both side skins through the cradle's Y+ edge.
    Its show face stands `pump_show_proud` ahead of the fixed enclosure while the pumps remain
    on `pump_cartridge_proud`; the same corner radius returns into the unchanged side planes.
    That complete plan begins on the cradle's own bed plane and continues plumb to one flat
    `pump_cartridge_z_clearance` below the lintel, without a bevel, ramp, starter strip or shelf.
    The matching lower Z clearance is cut into the fixed shell perimeter by `_bay_cut`, outside
    the interior bearing floor."""
    proud = _pump_cartridge_outer(outer)
    return _pump_full_width_band(
        inner, proud, bay, pump_trays, pump_cartridge_aft_y(pump_trays),
        lower_inset=0.0, upper_inset=pump_cartridge_z_clearance)


def cap_split_z(pump_trays):
    """The stamped bracket's lower bearing plane.

    The lower cradle carries the bracket from below; its top clamp presses from the bracket's
    opposite face."""
    return min(cz for _cx, _cy, cz in pump_trays)


def cap_drop_start_z(pump_trays):
    """The upper insertion wells' tolerance-overlapped start below the bracket plane."""
    return cap_split_z(pump_trays) - 0.001


def cap_base_z(pump_trays):
    """The top clamp's broad Z-minus face, on the stamped bracket's upper face."""
    return cap_split_z(pump_trays) + _tray.bracket_t


def cap_crown_z(box):
    """The complete top clamp's common crown, with Z clearance below the bay lintel."""
    return box.pump_bay[2] - pump_cartridge_z_clearance


def cap_access_z(pump_trays):
    """The joined screw-access well's retained floor above the bracket datum."""
    return cap_split_z(pump_trays) + cap_web_t


def pump_skirt_support_z(pump_trays):
    """The flat cradle land under each 8 mm pump skirt, with 0.15 mm Z clearance."""
    return cap_drop_start_z(pump_trays) - _tray.skirt_depth - _tray.skirt_support_air


def pump_cartridge_aft_y(pump_trays):
    """The lower cradle's complete Y+ extent: the skirt opening plus its 3 mm upper band."""
    return max(cy + _tray.skirt_open_y_max + _tray.skirt_upper_band
               for _cx, cy, _cz in pump_trays)


def _clamp_bridge_edge(pump_trays):
    """The joined screw-access well's X edge, overlapping both pump openings."""
    inner = min(abs(cx) - _tray.half_width() for cx, _cy, _cz in pump_trays)
    if inner <= 0.0:
        raise ValueError(
            "the two pump openings overlap across the centre lane, leaving no filled field "
            "for the top-clamp screws")
    return inner + clamp_bridge_overlap


def cap_screw_ys(inner, plate):
    """The top clamp's two screw stations, fore and aft of the access-well midpoint.

    Both stand between the pumps, clear of their bosses, fittings and tubes."""
    mid = (inner[2] + (plate["fore_y"] - 2.0)) / 2.0
    return mid - cap_screw_off, mid + cap_screw_off


def _pump_drop_voids(box):
    """The two straight Z insertion wells through the lower cradle.

    BELOW THE BRACKET the well is `pump_tray.drop_well` on `cap_pump_air` — the two-piece
    bench case's own cavity, the solid `kamoer_kphm400.build_head` clips this pump to, carried
    up its axis so every station stands as open as the widest one under it. It brings the
    case's figures with it: 56 mm across at the narrow half, 64 at the centre, 70 at the
    outlet face where the fittings stand, the corner radii, and the flat step under the 8 mm
    skirt. The step supports X-, Y- and X+ continuously; on Y+ it supports only the centre
    between the two tube passages. From that outlet face, two individual
    fitting passages run aft to the block's own face. Each keeps a circular lower half around
    its tube axis and a straight 13 mm shaft above it. The two shafts' outside edges, the
    tube-side case room and the upper well share one 72.75 mm opening boundary. The wall between
    and outside them remains printed stock.

    ABOVE THE BRACKET the well continues each pump's 72.75 mm opening span around the
    72.50 mm physical tube-casing span. That one opening passes the stamped bracket,
    the fittings, the pump and then the complete clamp. One full-Y centre clearance joins those
    openings and follows every part of the clamp's filled centre field through the cradle. At
    the seat the upper wells stop exactly on the bracket plane, leaving the case's own room
    below and therefore a land under the bracket on its three closed sides."""
    trays, plate = box.pack.pump_trays, box.pack.collet_plate
    drop_start = cap_drop_start_z(trays)
    top = box.pump_bay[2] + 1.0
    fore = min(cy - _tray.half_width() for _cx, cy, _cz in trays)
    support_top = pump_skirt_support_z(trays) - min(cz for _cx, _cy, cz in trays)
    lower_source = _tray.drop_well(cap_pump_air, support_top=support_top).val()
    out = []
    for cx, cy, cz in trays:
        lower = lower_source.moved(cq.Location(cq.Vector(cx, cy, cz)))
        outlet_face = cy + _tray.head_half - _tray.outlet_relief
        outlet_axis = cz + _tray.outlet_axis_z
        fittings = None
        for sx in (-1.0, 1.0):
            hx = cx + sx * _tray.outlet_pitch / 2.0
            # Carry the complete circle-and-shaft passage through the tube-side body room.
            # Its overlap with that room is free volume, but it joins the 13 mm tangent to the
            # 72.75 mm upper boundary without the old 0.975 mm face on the tube-axis plane.
            y0 = cy + _tray.outlet_passage_start_y(cap_pump_air)
            y1 = pump_cartridge_aft_y(trays) + 1.0
            circle = _ycyl(cap_fitting_half, hx, outlet_axis, y0, y1)
            shaft = _ybox(
                hx - cap_fitting_half, hx + cap_fitting_half,
                y0, y1, outlet_axis, top)
            opening = circle.fuse(shaft)
            fittings = opening if fittings is None else fittings.fuse(opening)
        # The upper well carries the same exact tube-pair boundary as the lower room and shafts.
        upper_x0, upper_x1 = _pump_upper_x_span(cx)
        upper = _ybox(upper_x0, upper_x1,
                      cy - _tray.half_width() - clamp_drop_air,
                      cy + _tray.far_reach() + clamp_drop_air,
                      drop_start, top)
        out.append(lower.fuse(fittings).fuse(upper))

    edge = _clamp_bridge_edge(trays)
    aft = plate_guide_fore_y(plate) - cap_kiss
    out.append(_ybox(-(edge + clamp_drop_air), edge + clamp_drop_air,
                     fore - clamp_drop_air, aft + clamp_drop_air,
                     drop_start, top))
    return out


def _cap_x_span(bay):
    """The lower cradle's exterior side faces: the appliance's complete stated width."""
    _bx0, bx1, _top = bay
    edge = bx1 + wall
    return -edge, edge


def _pull_center_z(plate):
    """The common Z of the four tube holes in the collet plate."""
    zs = [z for _x, z in plate["holes"]]
    if not zs or max(zs) - min(zs) > 1e-6:
        raise ValueError(
            "the pump cartridge's side pulls require one tube-centre elevation, but the "
            f"collet plate carries {zs}")
    return sum(zs) / len(zs)


def _cradle_pulls(box):
    """The two new hand pockets, both cut wholly from the lower cradle.

    Their fore wall is the pulling ledge. The floor stays `pull_floor_below_tubes` under the
    tube-axis plane, leaving a bed-rooted lower ligament; at the inboard wall the pocket has
    `pull_rise - pull_depth` of plumb finger room, then its roof climbs at 45 degrees to the
    open flank. Nothing is split across the clamp joint."""
    edge = _cap_x_span(box.pump_bay)[1]
    deep = edge - pull_depth
    z_mid = _pull_center_z(box.pack.collet_plate)
    z0 = z_mid - pull_floor_below_tubes
    z1 = z0 + pull_rise
    if pull_depth >= pull_rise:
        raise ValueError(
            f"a {pull_depth:g} mm-deep cradle pull has no printable roof inside its "
            f"{pull_rise:g} mm opening")
    y0 = plate_guide_notch_fore_y(box.pack.collet_plate) - pull_min_run
    # Open through the cartridge's actual aft plane. Ending this cutter on the former
    # rectangular-notch plane left a broad, unnecessary Y-normal wall across each pocket.
    y1 = pump_cartridge_aft_y(box.pack.pump_trays) + 1.0
    out = []
    for sx in (+1.0, -1.0):
        section = ((sx * (edge + 1.0), z0), (sx * deep, z0),
                   (sx * deep, z1 - pull_depth), (sx * (edge + 1.0), z1 + 1.0))
        out.append(_xz_prism(y0, y1, section))
    return out


def pump_cartridge_figures(box):
    """The cradle, clamp, fitting opening and pull dimensions written into the docs."""
    if not (box.pump_bay and box.pack.pump_trays):
        return {}
    bay, trays, plate = box.pump_bay, box.pack.pump_trays, box.pack.collet_plate
    edge = _cap_x_span(bay)[1]
    y0 = plate_guide_notch_fore_y(plate) - pull_min_run
    y1 = pump_cartridge_aft_y(trays)
    z_mid = _pull_center_z(plate)
    pull_floor = z_mid - pull_floor_below_tubes
    pull_top = pull_floor + pull_rise
    clamp_edge = max(abs(cx) + _tray.half_width() for cx, _cy, _cz in trays)
    clamp_fore = min(cy - _tray.half_width() for _cx, cy, _cz in trays)
    clamp_aft = plate_guide_fore_y(plate) - cap_kiss
    clamp_base = cap_base_z(trays)
    clamp_crown = cap_crown_z(box)
    return {
        "PULL_RISE": f"{pull_rise:.4g} mm",
        "PULL_RUN": f"{(y1 - y0):.4g} mm",
        "PULL_DEPTH": f"{pull_depth:.4g} mm",
        "PULL_PLUMB": f"{(pull_rise - pull_depth):.4g} mm",
        "PULL_FLOOR_Z": f"{pull_floor:.5g} mm",
        "PULL_TOP_Z": f"{pull_top:.5g} mm",
        "PULL_FLOOR_LIGAMENT": f"{(pull_floor - bay_floor_z(trays)[1]):.4g} mm",
        "PULL_CENTER_Z": f"{z_mid:.5g} mm",
        "PULL_LEDGE": f"{y0:.4g} mm",
        "PULL_AFT_OPEN": f"{y1:.4g} mm",
        "PULL_TRAVEL": f"{y0 - box.inner[2]:.4g} mm",
        "CLAMP_SPAN": f"{2.0 * clamp_edge:.4g} mm",
        "CLAMP_RISE": f"{(clamp_crown - clamp_base):.5g} mm",
        "CLAMP_BASE_Z": f"{clamp_base:.5g} mm",
        "CLAMP_CROWN_Z": f"{clamp_crown:.5g} mm",
        "CLAMP_ACCESS_FLOOR_Z": f"{cap_access_z(trays):.5g} mm",
        "CLAMP_ACCESS_BASE": f"{(cap_access_z(trays) - clamp_base):.4g} mm",
        "CLAMP_HEAD_LAND": f"{cap_web_land:.4g} mm",
        "CLAMP_ACCESS_W": f"{2.0 * _clamp_bridge_edge(trays):.4g} mm",
        "CLAMP_ACCESS_RUN": f"{(max(cap_screw_ys(box.inner, plate))
                                 - min(cap_screw_ys(box.inner, plate))
                                 + 2.0 * clamp_bridge_half_y):.4g} mm",
        "CLAMP_FRONT_SKIN": f"{(clamp_fore - clamp_drop_air - pump_cartridge_front_y):.4g} mm",
        "CLAMP_AFT_WALL": f"{(clamp_aft - max(cy + _tray.boss_half
                                                for _cx, cy, _cz in trays)):.4g} mm",
        "CLAMP_WEB": f"{cap_web_t:.4g} mm",
        "CLAMP_BRACKET_T": f"{_tray.bracket_t:.4g} mm",
        "CAP_TUBE_OPEN_SPAN": f"{2.0 * cap_slot_half:.4g} mm",
        "CAP_TUBE_PART_SPAN": f"{2.0 * _tray.outlet_half:.4g} mm",
        "CAP_TUBE_OPEN": f"{2.0 * cap_fitting_half:.5g} mm",
        "CAP_TUBE_PART": f"{_tray.fitting_w:.4g} mm",
        "CAP_TUBE_PITCH": f"{_tray.outlet_pitch:.4g} mm",
        "CAP_TUBE_AXIAL_AIR": f"{cap_tube_axial_air:.4g} mm",
        "PUMP_SKIRT_DEPTH": f"{_tray.skirt_depth:.4g} mm",
        "PUMP_SKIRT_SUPPORT_AIR": f"{_tray.skirt_support_air:.4g} mm",
        "PUMP_SKIRT_SUPPORT_Z": f"{pump_skirt_support_z(trays):.6g} mm",
        "PUMP_SKIRT_BODY_Y": f"{_tray.skirt_body_y:.4g} mm",
        "PUMP_SKIRT_OPEN_Y": f"{_tray.skirt_body_open_y:.4g} mm",
        "PUMP_SKIRT_XY_AIR": f"{_tray.skirt_support_xy_air:.4g} mm",
        "PUMP_SKIRT_BODY_Y_MINUS_EDGE":
            f"{(trays[0][1] + _tray.skirt_body_open_y_bounds[0]):.6g} mm",
        "PUMP_SKIRT_BODY_Y_PLUS_EDGE":
            f"{(trays[0][1] + _tray.skirt_body_open_y_bounds[1]):.6g} mm",
        "PUMP_SKIRT_Y": f"{_tray.skirt_y:.4g} mm",
        "PUMP_SKIRT_Y_MINUS_EDGE":
            f"{(trays[0][1] + _tray.skirt_open_y_max
                  - _tray.skirt_y_plus_air - _tray.skirt_y):.6g} mm",
        "PUMP_SKIRT_Y_PLUS_EDGE":
            f"{(trays[0][1] + _tray.skirt_open_y_max
                  - _tray.skirt_y_plus_air):.6g} mm",
        "PUMP_SKIRT_Y_PLUS_AIR": f"{_tray.skirt_y_plus_air:.4g} mm",
        "PUMP_SKIRT_Y_MINUS_LAND": f"{_tray.skirt_support_y_minus:.4g} mm",
        "PUMP_SKIRT_Y_PLUS_LAND": f"{_tray.skirt_support_y_plus:.4g} mm",
        "PUMP_SKIRT_Y_PLUS_OPEN_EDGE":
            f"{(trays[0][1] + _tray.skirt_open_y_max):.6g} mm",
        "PUMP_SKIRT_UPPER_BAND": f"{_tray.skirt_upper_band:.4g} mm",
        "PUMP_SKIRT_UPPER_BAND_AFT":
            f"{(trays[0][1] + _tray.skirt_open_y_max
                  + _tray.skirt_upper_band):.6g} mm",
        "PUMP_CARTRIDGE_AFT_Y": f"{pump_cartridge_aft_y(trays):.6g} mm",
        "PUMP_PULL_WALL": f"{pump_pull_wall:.4g} mm",
        "PUMP_PROUD": f"{pump_show_proud:.4g} mm",
        "PUMP_STATION_PROUD": f"{pump_cartridge_proud:.4g} mm",
        "PUMP_SHOW_GROWTH": f"{pump_show_growth:.4g} mm",
        "PUMP_FACE_SKIN": f"{(pump_relief_floor - pump_cartridge_front_y):.4g} mm",
        "PUMP_UPPER_SMOOTH_SKIN": f"{_pump_front_smooth_skin(trays):.4g} mm",
        "PUMP_UPPER_FLUTED_SKIN": f"{(_pump_front_smooth_skin(trays) - flute_depth):.4g} mm",
        "CRADLE_EDGE": f"{edge:.4g} mm",
        "CRADLE_WIDE": f"{2.0 * edge:.4g} mm",
        "PLATE_SLOT_LEAD": f"{plate_slot_lead:.4g} mm",
        "PLATE_CAP_LAND": f"{plate_cap_land:.4g} mm",
        "PLATE_STEP_IN": f"{plate_step_in():.4g} mm",
        "PLATE_STEP_Z": f"{seam_cap_z():.4g} mm",
        "PLATE_GUIDE_WEDGE": f"{plate_guide_wedge:.4g} mm",
        "PLATE_CAP_Z": f"{plate['z1']:.4g} mm",
        "PLATE_CAP_FORE_Z": f"{plate_cap_fore_z(plate):.6g} mm",
        "PLATE_CAP_TOP": f"{bay[2]:.4g} mm",
    }


def bay_floor_z(pump_trays):
    """The bay floor's two planes: its underside on front-top's own seam mouth, and its top
    on the plane the pump cartridge's filled bearing block reaches down to.

    THE FLOOR IS THIS PIECE'S FIRST LAYERS. Front-top beds on the seam plane, so a floor
    struck there lies on the bed and nothing under it hangs. What sets its section is the
    only thing over it: the pump cartridge's own pump reliefs floor on
    `_pump_relief_regions`' z0, one millimetre under the heads, and the floor's top is one
    `pump_cartridge_z_clearance` under that plane.

    AND IT IS ONE PLANE ACROSS THE WHOLE MOUTH. The filled block's flat bearing sill, the
    stationary sill the fixed shell perimeter stops on, and the removable exterior face's own
    bed plane are all this figure, so the bay's floor reads flat from the front wall's section
    through to the collet plate's slot."""
    return z_seam, (min(z0 for _x0, _x1, z0, _z1, _floor in _pump_relief_regions(pump_trays))
                    - pump_cartridge_z_clearance)


def _flank_lip_drop(inner, plate, y_joint, zj):
    """The Z-seam lip given up on BOTH FLANKS over the front run — front-bottom stops
    standing a wall up into front-top there, and nothing above has to open for one.

    `_front_flat_lip_drop`'s twin, turned a quarter: that one gives the lip up across the
    bay's own flat, this one gives it up round the corners and back down each flank as far
    as the tee wall's aft face (`plate["wall_aft_y"]`) — which is where the front column's
    RAIL then starts (`_z_rail_runs`). What the telescope was doing over that run is done
    better by what stands there now — the seam's cap over it, the bay floor bedded through
    it, the tee wall across it — and a lip that registers nothing is a wall poking into a
    cavity cut to receive it."""
    # Down to the mouth and NOT past it: below the seam this run is front-bottom's own wall,
    # which the drop has no business in — only the lip standing proud of the mouth.
    return _flank_lip_run(inner, plate, y_joint, (zj, zj + z_rise + wall + 1.0))


def _flank_lip_run(inner, plate, y_joint, z):
    """The drop's OUTLINE over a z band given: wall to wall and back to the tee wall's aft
    face.

    `_flank_lip_drop` asks for the lip's own band, which is what a piece is cut on.
    `_lip_denied` asks for the whole column, because it reads which seam HEIGHTS a body
    denies rather than what one seam cuts — and the two have to come off this one outline
    or the second is answering about a lip the box does not build."""
    lo, hi = z
    # WALL TO WALL, and not jamb to jamb. Between the jambs the front flat has already given
    # its lip up (`_front_flat_lip_drop`) and nothing else of the bottom piece stands over
    # the mouth here, so reaching across costs nothing — and stopping ON the jamb would put
    # this cut's own side plane on the one plane three other cuts already end on.
    return _ybox(inner[0] - wall - 1.0, inner[1] + wall + 1.0,
                 inner[2] - wall - 1.0, plate["wall_aft_y"], lo, hi)


def _bay_floor(inner, y_joint, plate, pump_trays):
    """THE BAY'S FLOOR: front-top's own storey across the front, from the front wall's
    interior face aft past the collet plate, on the bed and under everything else.

    THE COLLET PLATE'S SLOT PASSES THROUGH IT (`_plate_slot`), and that slot's mouth is
    this piece's own Z− FACE — the seam plane, which is also the bed. The steel comes up from
    there and goes clean through: this floor holds it fore and aft, on the slot's two faces,
    which are the floor's own section. WHAT STOPS IT IS A STOREY UP — the steel's top edge on
    `_plate_cap`'s land — so the floor takes no shoulder, the mouth takes no step, and the
    slot is one width from the bed face to this plane.

    NOTHING OF THE SEAM PASSES IT. The seam's skin is given up over this whole run
    (`_flank_lip_drop`, `_front_flat_lip_drop`), so the floor runs the walls whole — and
    the rail channel, cut last, is what opens its flank bands for the slide.

    AT THE TWO SIDE-WALL PLANES THE SHELL STANDS TO THE RIM. The pump cartridge sweeps the
    complete cavity width, so there is no separate floor strip outboard of it; the installed
    cradle closes the opening out to both exterior side faces above this floor.

    AND ITS SLOT'S TWO ENDS ARE WHAT LOCATE THE STEEL ACROSS. Over `seam_cap_z` the flank the
    plate's ends would otherwise stand against is opened whole by `_bay_cut`, so the ends
    reach into that opening and touch nothing; here, in the floor, they run one
    `plate_slot_slip` off each end of a slot cut in solid material. This is the only station
    in the machine that holds the plate in X."""
    z0, z1 = bay_floor_z(pump_trays)
    rim = z_seam + z_rise
    bx0, bx1 = bay_x_span(inner)
    slab = _ybox(inner[0], inner[1], front_plane_y,
                 plate["aft_y"] + plate_slot_slip + wall, z0, z1)
    for x_in, edge in ((inner[0], bx0), (inner[1], bx1)):
        if abs(edge - x_in) > 1e-9:
            slab = slab.fuse(_ybox(min(x_in, edge), max(x_in, edge), front_plane_y,
                                   plate["aft_y"] + plate_slot_slip + wall, z1, rim))
    return slab.cut(_plate_slot(inner, plate, rim + 1.0))


def _plate_slot(_inner, plate, z_top):
    """THE COLLET PLATE'S OWN SLOT — ONE RECTANGULAR X SPAN THROUGH THE WHOLE FLOOR.

    Fore and aft it is the steel, `plate_slot_slip` off each face, at every height. ACROSS, it
    is the steel's own width plus `plate_slot_slip` at both ends, the same from the Z− mouth
    through the floor and every fixed wall the lane crosses. The 4.3 mm returns between those
    ends and `interior_x` remain printed material; the slot never expands sideways into them.

    IT HOLDS NOTHING BACK. What stops the steel is its own top edge on `_plate_cap`, one
    storey up and wall to wall, so this slot is a lane and not a seat: no step in it, no
    shoulder standing at the mouth, and the same section from the bed face to the floor's top.

    AND ITS MOUTH IS SQUARE ON THE FORE FACE, which stands at `plate_slot_slip` off the steel
    from the bed face to the seat. What eases the steel in is taken off the lane's aft side
    alone (`_plate_lead`), and the floor gives that flare up here because its own section runs
    aft of the slot over the ground the flare stands in."""
    y0, y1 = plate["fore_y"] - plate_slot_slip, plate["aft_y"] + plate_slot_slip
    x0, x1 = plate["x0"] - plate_slot_slip, plate["x1"] + plate_slot_slip
    return _ybox(x0, x1, y0, y1, z_seam - 1.0, z_top).fuse(_plate_lead(plate))


def _tee_wall(inner, y_joint, plate, bay):
    """THE WALL THE ANCHOR TEES STAND IN: front-top's own section behind the collet plate,
    wall to wall and the whole height of the bay, with one bore per tee.

    A BORE HOLDS ITS TEE ACROSS ITS OWN AXIS AND LEAVES IT free along the release direction.
    Each arm carries a round collar (`tee_connector.branch_collar`), so one collar-clear bore
    passes through the wall's complete section. Printed material locates that collar in X and Z;
    the open bore leaves Y to the release motion.

    ITS FORE FACE IS THE STEEL'S AFT FACE, struck once as one figure
    (`enclosure_assembly.collet_plate_spec`). The plate stands in front of it, so every
    bore is stopped at its fore mouth by steel and the collet nose that lands there lands on
    steel and not on plastic.

    ITS BROAD AFT FACE STOPS SHORT OF THE TEE, ON PURPOSE. A tee travels WITHIN this wall, and
    the wall is not allowed to be what ends that travel: the face stands one whole stroke plus
    `TEE_WALL_BODY_AIR` fore of the tee's own body, so at full release there is still air
    between the two. The collar-clear bore opens directly through that face.

    AND IT IS THE BAY'S BACK. Over the plate's own band the steel closes the bay; above and
    below it nothing does, and the berth the pump cartridge leaves looks into the cavity. This
    stands the whole storey, so what is behind the bay is a wall.

    AND THE Z SEAM DOES NOT PASS IT, so this wall opens for nothing but its own bores. The
    rail channel's lane BEGINS ON THIS WALL'S OWN AFT FACE — `_z_rail_runs` starts the front
    run there — so the cut that carries the slide runs away from this wall and never reaches
    into its two feet."""
    slab = _ybox(inner[0], inner[1], plate["aft_y"], plate["wall_aft_y"], z_seam, bay[2])
    slab = slab.cut(_plate_lead(plate))
    for hx, hz in plate["holes"]:
        slab = slab.cut(_tee_bore(plate, hx, hz))
    return slab


def _plate_lead(plate):
    """THE FLARE THAT LEADS THE STEEL INTO ITS LANE, taken off the lane's AFT side.

    At the seam plane the lane's aft wall stands `plate_slot_lead` back off the steel's own
    plane and closes onto it over the same rise, so the mouth is that much wider than the lane
    it opens into and the face a print climbing off its bed lays there is at 45 degrees. Above
    the flare the wall is the steel's plane again, which is what every bore through it is
    stopped on.

    BOTH BODIES ON THAT SIDE GIVE IT UP. The tee wall's fore face IS the lane's aft wall
    (`_tee_wall`), and the bay floor carries its own section aft of the slot over the same
    ground (`_plate_slot`) — so this one cutter is what each of them takes.

    IT IS THE SLOT'S OWN X SPAN. Outside the steel's ends the wall carries `plate_end_stock`
    into the side walls and there is nothing there to lead in."""
    aft, lead = plate["aft_y"], plate_slot_lead
    return _yz_prism(plate["x0"] - plate_slot_slip, plate["x1"] + plate_slot_slip,
                     [(aft - 1.0, z_seam - 1.0), (aft + lead, z_seam - 1.0),
                      (aft + lead, z_seam), (aft, z_seam + lead),
                      (aft - 1.0, z_seam + lead)])


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
    in the funnel's throat, and one slanted straight from crown to ridge would run into the
    display's own body where it stands proud of the slab.

    IT RUNS WALL TO WALL AND NOT THE RIDGE'S OWN LENGTH. What it carries is `display_pcb_x` of
    line, but a rib ending in free air at each end of that line would stand on the tee wall's
    crown with two free ends and nothing at its own; run out to the flanks it lands in the side
    walls and the storey over the bay is closed rather than partly closed. THAT CLOSING IS THE
    COST: this is now the only section between the bay's storey and the cavity aft of it, so
    anything crossing crosses through it.

    ONE THING DOES. The bore is the enclosure display's loom (`cable_sleeve_open`), teardropped
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
    the layer that closes it is laid across the chord beneath with nothing under it. Two planes
    at `teardrop_roof_angle` stand on their tangent points and meet over the axis. Tangency makes
    this the smallest roof at that printable angle: half-width `r sin(a)`, tangent height
    `r cos(a)`, apex height `r / cos(a)`. The lower circle — which is what a bore locates and
    bears on — is untouched."""
    a = math.radians(teardrop_roof_angle)
    half = r * math.sin(a)
    tangent = z + r * math.cos(a)
    apex = z + r / math.cos(a)
    return _ycyl(r, x, z, y0, y1).fuse(
        _xz_prism(y0, y1, [(x - half, tangent), (x + half, tangent), (x, apex)]))


def _teardrop_x(r, y, z, x0, x1):
    """The same support-free horizontal bore as `_teardrop_y`, carried on X.

    The nominal circle remains whole below the roof, so a round screw head or tool passes
    and bears exactly as it does in a cylindrical counterbore. Two tangent planes at
    `teardrop_roof_angle` replace only the circular crown a standing print cannot close."""
    a = math.radians(teardrop_roof_angle)
    half = r * math.sin(a)
    tangent = z + r * math.cos(a)
    apex = z + r / math.cos(a)
    return _xcyl(r, y, z, x0, x1).fuse(
        _yz_prism(x0, x1, [(y - half, tangent), (y + half, tangent), (y, apex)]))


def _tee_bore(plate, hx, hz):
    """One tee's support-free collar-clear bore through the wall's complete section."""
    return _teardrop_y(
        plate["bore_r"], hx, hz,
        plate["aft_y"] - 1.0,
        plate["wall_aft_y"] + 1.0)


def _unified(solid):
    """One printed piece, with its coincident-plane seams merged.

    EVERY BOOLEAN LEAVES SPLITTERS. A cutter that fuses a bore to a channel standing on that
    bore's own axis lands the tangent arc on the piece as a seam across one plane, and the two
    faces either side of it are one surface reported as two. A volume cannot see them and a
    clash cannot either; on a section they read as a hole that is not there. The box carries
    them in the hundreds otherwise, so this is one call at the end of a piece rather than a
    guard at every fuse that makes one."""
    return cq.Workplane(obj=solid).clean()


def build_pump_cartridge(box, halves_cache=None):
    """THE LOWER CRADLE: the complete front face and the load-bearing cartridge body.

    Its filled block rides the bay floor while its exterior face begins on the same bed plane
    over a recessed fixed sill, ends on the skirt band's Y+ plane, and remains one piece through
    the complete removable front-wall height. Two open wells admit
    the pumps and top clamp in Z. Below the bracket plane those wells close to the head
    clearance, leaving the stamped brackets on three cradle lands; four fitting-sized passages
    stay open through the whole drop path while the aft pull wall remains between them.

    Both side pulls are cut from this piece at the tube-centre elevation. The clamp has no
    pull feature. Two heat-set bores open upward from the centre spine for the clamp screws."""
    inner, plate = box.inner, box.pack.collet_plate
    solid = _pump_cartridge_gross(box, halves_cache)
    for void in _pump_drop_voids(box):
        solid = solid.cut(void)
    for pull in _cradle_pulls(box):
        solid = solid.cut(pull)
    for bore in _cap_screws(inner, plate, box.pack.pump_trays)[1]:
        solid = solid.cut(bore)
    return _unified(solid)


def _pump_cartridge_gross(box, halves_cache=None):
    """The lower cradle before its pump wells, hand pulls and clamp fasteners are cut.

    The detachable face begins with its filled block on one common bed plane, above the fixed
    sill's Z-clearance gap, and ends one equal Z clearance below the lintel. It bears on the bay
    floor back to the skirt band's Y+ plane. Pump and clamp openings are cuts in this one body; the
    top clamp is built independently from the conformal collars it needs."""
    inner, outer = box.inner, box.outer
    bay, plate = box.pump_bay, box.pack.collet_plate
    if not bay or not plate:
        raise ValueError("a pump cartridge wants a bay and a collet plate, and this box "
                         "carries neither station — the pack has no pumps to pull")
    if halves_cache is not None and "pump-cartridge-gross" in halves_cache:
        return halves_cache["pump-cartridge-gross"]
    if halves_cache is not None and "front" in halves_cache:
        half = halves_cache["front"]
    else:
        half = build_front_half(box)
        if halves_cache is not None:
            halves_cache["front"] = half
    face = _pump_cartridge_face_region(inner, outer, bay, box.pack.pump_trays)
    # Keep every cut and relief the fixed half already gives the band, then add only the proud
    # nose. The nose overlaps the old rounded corners through their side tangencies, so it joins
    # them with volume rather than meeting either flank on a line.
    solid = half.val().intersect(face)
    nose = face.intersect(_ybox(
        outer[0] - 1.0, outer[1] + 1.0,
        pump_cartridge_front_y - 1.0, outer[2] + corner_round + 0.01,
        bay_floor_z(box.pack.pump_trays)[1], bay[2]))
    solid = solid.fuse(nose)
    bx0, bx1, top = bay
    aft = pump_cartridge_aft_y(box.pack.pump_trays)
    floor_top = bay_floor_z(box.pack.pump_trays)[1]
    # The filled body bears on the floor and reaches both cavity planes. The exterior shell's
    # complete proud front, rounded corners and side faces begin on that same bed plane and stand
    # plumb from there. The lower running gap is in the fixed shell perimeter, outside this
    # bearing floor. No fixed side skin frames the cradle.
    fill = _ybox(
        bx0, bx1, pump_relief_floor, aft,
        floor_top, top - pump_cartridge_z_clearance)
    solid = solid.fuse(fill).intersect(face.fuse(
        _ybox(bx0, bx1, pump_cartridge_front_y, aft, floor_top, top)))
    for notch in _plate_retention_clearance_notches(
            outer, bay, plate, box.pack.pump_trays):
        solid = solid.cut(notch)
    if halves_cache is not None:
        halves_cache["pump-cartridge-gross"] = solid
    return solid


def _pump_clamp_gross(box, halves_cache=None):
    """One filled clamp field, cut only where its two fitted pumps and access well require.

    The field begins as one broad Z-minus face on top of both stamped brackets. Each complete
    case-profile octagon locates a boss, and each motor can opens the remaining height. There
    is no shallow bracket pocket or narrow rail under the field: the bracket itself lies below
    the print. The complete field reaches one common crown below the bay lintel. A single joined
    recess reaches down around both top-access M3 heads."""
    if halves_cache is not None and "pump-clamp-gross" in halves_cache:
        return halves_cache["pump-clamp-gross"]
    trays, plate = box.pack.pump_trays, box.pack.collet_plate
    split = cap_split_z(trays)
    base = cap_base_z(trays)
    crown = cap_crown_z(box)
    fore = min(cy - _tray.half_width() for _cx, cy, _cz in trays)
    aft = plate_guide_fore_y(plate) - cap_kiss
    x0 = min(cx - _tray.half_width() for cx, _cy, _cz in trays)
    x1 = max(cx + _tray.half_width() for cx, _cy, _cz in trays)
    solid = _ybox(x0, x1, fore, aft, base, crown)
    for cx, cy, cz in trays:
        solid = solid.cut(_tray.boss_room(0.0).moved(
            cq.Location(cq.Vector(cx, cy, split))))
        solid = solid.cut(_zcyl(
            _tray.can_half, cx, cy,
            split + _tray.boss_depth - 0.1, crown + 1.0))

    ys = cap_screw_ys(box.inner, plate)
    edge = _clamp_bridge_edge(trays)
    solid = solid.cut(_ybox(
        -edge, edge,
        min(ys) - clamp_bridge_half_y, max(ys) + clamp_bridge_half_y,
        cap_access_z(trays), crown + 1.0))
    if halves_cache is not None:
        halves_cache["pump-clamp-gross"] = solid
    return solid


def _cap_screws(inner, plate, pump_trays):
    """The clamp's top-down screw bores and the cradle's downward heat-set bores.

    Each recessed M3 head leaves `cap_web_land` under its seat. The M3×10 crosses that land,
    the stamped-bracket-height service gap, and takes the complete four-millimetre heat-set
    opened from the cradle's bracket plane."""
    split = cap_split_z(pump_trays)
    base = cap_base_z(pump_trays)
    top, seat = cap_access_z(pump_trays), base + cap_web_land
    screw_tip = seat - screw_len
    bore_tip = min(screw_tip, split - heatset_len) - 0.5
    clear, sets = [], []
    for y in cap_screw_ys(inner, plate):
        clear.append(_zcyl(screw_clear_dia / 2.0, 0.0, y, base - 0.1, top + 1.0)
                     .fuse(_zcyl(head_cbore_dia / 2.0, 0.0, y, seat, top + 1.0)))
        sets.append(_zcyl(heatset_dia / 2.0, 0.0, y, bore_tip, split + 0.1))
    return clear, sets


def build_pump_cap(box, halves_cache=None):
    """THE TOP CLAMP: one filled field fitted around both pump heads.

    With the cartridge withdrawn from the enclosure, it lowers over both motor cans after the
    pumps stand in the cradle. Each opening takes its boss on the complete case-profile octagon
    and closes with one shoulder round the can; the bottom field presses both stamped brackets
    onto the cradle lands. The whole field reaches the cradle's top plane, and one joined recess
    reaches both M3 heads from above. This piece carries no show face, plate stop or pull."""
    inner, plate = box.inner, box.pack.collet_plate
    solid = _pump_clamp_gross(box, halves_cache)
    for bore in _cap_screws(inner, plate, box.pack.pump_trays)[0]:
        solid = solid.cut(bore)
    return _unified(solid)


def build_front_half(box):
    """The whole front column, both pieces still joined at its Z seam."""
    inner, outer, y_joint = box.inner, box.outer, box.y_joint
    shell = _shell_with_facet(inner, outer).val()
    front = shell.intersect(_ybox(outer[0], outer[1], outer[2], y_joint, outer[4], outer[5]))
    # The front wall's reliefs, out of the section before anything stands on it: the
    # refrigeration bay and the pump pockets, each floored on its own stated plane.
    for cutter in _front_relief_cuts(inner, box.pack.pump_trays):
        front = front.cut(cutter)
    front = front.fuse(_front_lip(inner, y_joint))
    # The floor's overlap: a full-thickness tongue on the bed, ending in a 45°
    # scarf nose within the slab (the core rides the cavity side, so the floor
    # cannot tongue proud like the walls). Lands in the bottom piece.
    front = front.fuse(_floor_scarf(inner, y_joint)[0])
    yb = _y_boss(y_joint)
    bosses = box.y_bosses
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
    # Punch the funnel's throat through the top wall, behind the display.
    if box.pack.funnel:
        front = front.cut(_funnel_cut(inner, outer, box.pack.funnel))
    # The front wall's through-holes.
    for cutter in _port_cuts(box.pack.front_ports, outer[2] - 5.0, inner[2] + 5.0):
        front = front.cut(cutter)
    # East side-wall through-holes — the CO2 inlet's, low in the machine corridor.
    for cutter in _x_port_cuts(box.pack.east_ports, inner[1] - 5.0, outer[1] + 5.0):
        front = front.cut(cutter)
    for x_in, x_ext, sx, z_boss in bosses:
        front = front.cut(_front_cuts(x_in, x_ext, sx, z_boss, yb, y_joint))
    # Clip any corner feature that pokes past the rounded print silhouette.
    front = front.intersect(_rounded_outer(outer))
    return cq.Workplane(obj=front)


def build_back_half(box):
    """The whole back column, both pieces still joined at its Z seam. The
    funnel opening crosses the Y seam, so this half takes its share of the
    cut — the collar bridges the seam."""
    inner, outer, y_joint = box.inner, box.outer, box.y_joint
    shell = _shell_with_facet(inner, outer).val()
    back = shell.intersect(_ybox(outer[0], outer[1], y_joint, outer[3], outer[4], outer[5]))
    # Give up the tongue envelope and keep the bed-side 45° wedge under its nose.
    # The assembled top stays flat under the core. Lands in the bottom piece.
    back = back.cut(_floor_scarf(inner, y_joint)[1])
    if box.pack.funnel:
        back = back.cut(_funnel_cut(inner, outer, box.pack.funnel))
    yb = _y_boss(y_joint)
    bosses = box.y_bosses
    # One plug per level, standing on the back mouth off the wall it drives through.
    # The corner ahead of that mouth is the front lip's, whole.
    for x_in, x_ext, sx, z_boss in bosses:
        back = back.fuse(_back_plug(x_ext, sx, z_boss, yb))
    # Clip any corner feature that pokes past the rounded print silhouette.
    back = back.intersect(_rounded_outer(outer))
    for x_in, x_ext, sx, z_boss in bosses:
        back = back.cut(_screw_cut(x_ext, sx, z_boss, yb))
    # Wall through-holes for the appliance's external connections — the
    # faucet umbilical (carb-water + two flavor), the tap-water inlet, and
    # the C14 mains inlet, all through the +Y wall of back-top in the band above the
    # cold core; their bodies hang in the band's open rear half.
    for cutter in _port_cuts(box.pack.back_ports, inner[3] - 5.0, outer[3] + 5.0):
        back = back.cut(cutter)
    # The ASSE drip pan's withdrawal slot through the −X wall, and the sleeve it lies in. The
    # sleeve's own cuts reach back through this wall, so the slot is opened here and reopened
    # there at the one shape.
    for cutter in _x_port_cuts(box.pack.west_ports, outer[0] - 5.0, inner[0] + 5.0):
        back = back.cut(cutter)
    back = _pan_sleeve(back, box.pack.pan_sleeve, outer[4] - 1.0, outer[5] + 1.0)
    return cq.Workplane(obj=back)


# HOW FAR THE SLEEVE'S CORBEL RUNS OUT FROM THE WALL. The block's floor is one `wall` under the
# tray and the tray's own length carries it east off the flank, so printed Z−-down the whole
# plate arrives over air. Struck on the plane the block is stated on — the box's own interior —
# so a piece carrying a thicker flank there stands that much less of it proud; what stops it is
# the flavour line's lane, which is what crosses the band under the block (`fluid-28`).
pan_sleeve_corbel = 20.0


def _pan_sleeve(solid, sleeve, z0, z1):
    """The ASSE drip pan's sleeve fused onto a −X wall and its berth cut back out, for a piece whose
    Z band holds the block's own top.

    The pack states the block as one world box rooted on that wall's inner face, and the berth
    as the two boxes the tray's own section makes. Fused THEN cut: the block closes the wall's
    slot on its way past and the berth reopens it, so the opening a hand meets from outside is
    the berth's own shape end to end.

    A 45° CORBEL CARRIES THE BLOCK'S FLOOR, run the block's whole depth and rooted on the flank
    the block is rooted on, tapering to nothing `pan_sleeve_corbel` off it. What the corbel does
    not reach stays a soffit: the tray is longer than any wedge off that one wall can hold, and
    nothing stands under the block's east half to root a second one on.

    THE RIM REBATE'S ROOF DOES HAVE FOUR ROOTS. Its outer strip rises into the central mouth from
    the exterior skin, its fore and aft strips rise from their jambs, and its east strip rises
    from the block's backstop. Those four 45° cuts leave the exterior opening and the seated
    flange gap exactly where the pack states them, then spend only free clearance as they run
    into the already-open mouth. No short roof remains over material printed below it.

    AND A NOTCH CARRIED PAST THE BLOCK'S OWN LID crosses the wall alone — the lead race does,
    over the moisture plate's solder holes — so its head takes the 45° hip, struck on the notch's
    own half-width, and the lintel over it is a ridge rather than a plate."""
    adds, cuts = sleeve
    blocks = [b for b in adds if z0 <= b[5] <= z1]
    for x0, x1, y0, y1, bz0, bz1 in blocks:
        solid = solid.fuse(_ybox(x0, x1, y0, y1, bz0, bz1))
        solid = solid.fuse(_xz_prism(y0, y1,
                                     [(x0 + pan_sleeve_corbel, bz0), (x0, bz0),
                                      (x0, bz0 - pan_sleeve_corbel)]))
    lid = max((b[5] for b in blocks), default=None)
    for x0, x1, y0, y1, cz0, cz1 in (cuts if blocks else ()):
        solid = solid.cut(_ybox(x0, x1, y0, y1, cz0, cz1))
        if cz1 > lid:
            solid = solid.cut(_yz_prism(x0, x1,
                                        ((y0, cz1), ((y0 + y1) / 2.0, cz1 + (y1 - y0) / 2.0),
                                         (y1, cz1))))
    # The rebate is the larger plan box whose roof is exactly the central mouth's floor. Find
    # that relationship in the pack rather than naming either cut by position: the well overlaps
    # the rebate in Z, and the narrow lead race crosses several levels, but neither has this one
    # contained, face-to-face transition.
    roof_pairs = [
        (rebate, mouth)
        for rebate in cuts for mouth in cuts
        if abs(rebate[5] - mouth[4]) < 1e-6
        and rebate[0] <= mouth[0] + 1e-6 and rebate[1] >= mouth[1] - 1e-6
        and rebate[2] <= mouth[2] + 1e-6 and rebate[3] >= mouth[3] - 1e-6
        and (rebate[0] < mouth[0] - 1e-6 or rebate[1] > mouth[1] + 1e-6
             or rebate[2] < mouth[2] - 1e-6 or rebate[3] > mouth[3] + 1e-6)
    ] if blocks else []
    if blocks and len(roof_pairs) != 1:
        raise ValueError(
            f"the pan sleeve has {len(roof_pairs)} contained rebate-to-mouth roof transitions; "
            "exactly one is required")
    if roof_pairs:
        rebate, mouth = roof_pairs[0]
        rx0, rx1, ry0, ry1, _rz0, roof = rebate
        mx0, mx1, my0, my1, _mz0, _mz1 = mouth
        outer_x = min(b[0] for b in blocks) - wall
        # Fore and aft jambs, across the rebate's whole X span.
        solid = solid.cut(_yz_prism(
            rx0, rx1,
            ((ry0, roof), (my0, roof + (my0 - ry0)), (my0, roof))))
        solid = solid.cut(_yz_prism(
            rx0, rx1,
            ((my1, roof), (my1, roof + (ry1 - my1)), (ry1, roof))))
        # The east backstop and the real exterior skin. The rebate cutter deliberately overcuts
        # west of the part, so its own x0 is not a printable root; `outer_x` is.
        solid = solid.cut(_xz_prism(
            my0, my1,
            ((rx1, roof), (mx1, roof + (rx1 - mx1)), (mx1, roof))))
        solid = solid.cut(_xz_prism(
            my0, my1,
            ((outer_x, roof), (mx0, roof + (mx0 - outer_x)), (mx0, roof))))
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


def _east_boss_stem(wall_x, station):
    """One +X-wall boss's D-shaped horizontal stem, before its insert bore is cut.

    The circle is the insert's annulus. Its lower half is filled out to a flat chord over the
    boss's whole run, so the free face is a D rather than a circle and its underside is one
    printable plane. The body still meets only the boss's own `mount_boss_dia`-wide footprint:
    the two filled corners lie inside the same square and grow wallward, away from the body.
    """
    sy, sz, tip = station[:3]
    r = mount_boss_dia / 2.0
    return _xcyl(r, sy, sz, tip, wall_x).fuse(
        _ybox(tip, wall_x, sy - r, sy + r, sz - r, sz))


def _east_boss_d_fill(wall_x, station):
    """Only the two lower corners that turn the established round stem into a D."""
    sy, sz, tip = station[:3]
    r = mount_boss_dia / 2.0
    cylinder = _xcyl(r, sy, sz, tip, wall_x)
    floor = _ybox(tip, wall_x, sy - r, sy + r, sz - r, sz)
    return floor.cut(cylinder)


def _east_boss_corbel(wall_x, station):
    """One boss's object-profiled 45 degree underside from its carried floor to the +X wall.

    `station[3]` is the inboard plane the wedge may reach. It is the mounting face unless an
    installed body crosses that wedge; `enclosure_assembly.wall_mounts` derives a setback from
    that body's exact solid. Optional `station[4]` Y bands are the parts of that same boss width
    outside the blocker: there the wall-rooted wedge still reaches the mounting face instead of
    holding an entire seven-millimetre boss back for a blocker that occupies only one side. The
    D stem remains whole over the blocker itself, where the purchased body already leaves too
    little Z room for a slicer to grow support.
    """
    sy, sz, tip = station[:3]
    web_tip = station[3] if len(station) > 3 else tip
    clear_bands = station[4] if len(station) > 4 else ()
    r = mount_boss_dia / 2.0
    if not (tip <= web_tip < wall_x):
        raise ValueError(
            f"east boss at ({sy:g}, {sz:g}) has corbel tip x={web_tip:g}; "
            f"expected {tip:g}..{wall_x:g}")

    def wedge(ylo, yhi, reach):
        drop = wall_x - reach
        return _xz_prism(
            ylo, yhi,
            [(wall_x, sz - r), (reach, sz - r), (wall_x, sz - r - drop)])

    out = wedge(sy - r, sy + r, web_tip)
    for ylo, yhi in clear_bands:
        if ylo < sy - r - 1e-6 or yhi > sy + r + 1e-6 or yhi <= ylo:
            raise ValueError(
                f"east boss at ({sy:g}, {sz:g}) has invalid clear corbel band "
                f"y={ylo:g}..{yhi:g}; expected inside {sy-r:g}..{sy+r:g}")
        out = out.fuse(wedge(ylo, yhi, tip))
    return out


def _east_boss_support(wall_x, station):
    """The material one +X-wall mounting station adds, before its bore."""
    return _east_boss_stem(wall_x, station).fuse(_east_boss_corbel(wall_x, station))


def _east_bosses(solid, inner, outer, stations, y0, y1, z0, z1):
    """The +X wall's mounting bosses added to a PIECE, for the stations inside the depth and
    height band that piece owns — so a boss lands in the piece whose wall carries it, whole,
    and no piece grows a column standing in another's air.

    Each station is `(y, z, tip, web_tip, clear_bands)`: the two plan coordinates the boss
    stands on, the plane its top face reaches — the body's own mounting face, where its hole
    pattern lies — the plane its 45 degree underside may reach across the blocker, and any Y
    bands where it can reach the mounting face. The last two are omitted when the whole wedge
    reaches. Where an installed body crosses only part of the candidate wedge, `wall_mounts`
    keeps assembly air around that part without throwing away the clear side's corbel; the
    D-shaped stem still reaches the mounting face across the whole hole.

    ON THE PIECE AND NOT ON THE HALF, because the Z seam's own socket collar is fused
    piece-side: where a station's height meets a mounting boss's, the two share the same
    material, and a bore cut before that collar is fused is a bore the collar fills back in.
    Cut here, the boss fuses nothing where the collar already stands and is bored through it
    all the same.

    The stem's flat, `mount_boss_dia`-wide floor matches the wedge it carries. Its upper half
    stays round around the insert, so the body's mounting pad remains compact; no arbitrary
    round pipe is left between the support and the mounting face."""
    for station in stations:
        sy, sz, tip = station[:3]
        if not (y0 <= sy <= y1 and z0 <= sz <= z1):
            continue
        solid = solid.fuse(_east_boss_support(inner[1], station))
        # AND THE BORE STOPS WHERE THE SURFACE SAYS, not where the plane does. Run its full
        # relief it ends on `interior_x`, which is one `wall` behind the flat and less than
        # that behind a corner round — and a flute is cut into that same surface, so a station
        # standing on the turn would put a groove over an insert with too little between them.
        # It gives up relief before it gives up `flute_backing`; `boss-bore-seats` reads what
        # is left against the insert's own depth.
        solid = solid.cut(_xcyl(heatset_dia / 2.0, sy, sz, tip,
                                east_boss_bore_end(sy, tip, outer)))
    return solid


def east_boss_bore_end(sy, tip, outer):
    """How far out a +X mounting boss's insert bore may run — its full relief, or as far as
    `flute_backing` behind the shallowest surface over the bore's own footprint, whichever
    stops first."""
    edge = min(flank_x_at(sy - heatset_dia / 2.0, outer),
               flank_x_at(sy + heatset_dia / 2.0, outer))
    return min(tip + heatset_depth + mount_bore_relief, edge - flute_backing)


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

    AND THE OPENING IS ROOFED ON ONE 45° PLANE, folded on the wall at the pocket's own
    roof — the plane the tabs bridge on, so the roof is one height where it meets the
    lug and the ramp starts where they do. It rises inboard off that fold, and the wall
    carries it the way the wall carries the wedge under the tower: same angle, same
    fold, mirrored over the lug, every layer inboard laid one layer-height out over the
    one below. Roofed flat instead, the opening hands its ceiling to whatever stands
    over the well — the flank's own section, the ceiling's soffit on the +X row — and
    that thing spans the opening on air.

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
        reach = engage + 1.0
        tower = sorted((face, face - side * engage))
        pocket = sorted((face, face - side * reach))
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
        roof_z = sz + stand_z / 2.0 + wago_well_press
        solid = solid.cut(_ybox(pocket[0], pocket[1],
                                sy - pk_y, sy + pk_y,
                                sz - (stand_z / 2.0 + wago_well_press), roof_z))
        gap = pk_y - wago_roof_tab
        solid = solid.cut(_xz_prism(sy - gap, sy + gap,
                                    [(face, roof_z), (face - side * reach, roof_z),
                                     (face - side * reach, roof_z + reach)]))
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
# AND THE GROOVE ENDS BY RUNNING OUT. Its floor returns to the outer face on the same 45 degree
# support-free slope used by every relief on this standing print. The ramp is therefore exactly
# as tall as the chase is deep: enough to turn the flow west without dragging a long, accidental-
# looking scar down the show face. CO2 is heavier than air and falls from there on its own.
vent_channel_w = 12.0          # the channel, across — and the mouth, square on it
vent_rib_wall = 2.0            # PETG either side of the channel, behind it, and over the mouth
vent_duct_drop = 25.0          # the closed fall under the mouth, before the skin opens
vent_groove_drop = 25.0        # the open groove under that, which the duct discharges into
vent_ramp_angle = relief_chamfer  # support-free run-out from the channel floor to the show face


def _vent_chase(solid, inner, outer, stations, y0, y1, z0, z1):
    """The PRV vent's chase on a −X wall PIECE — the rib the piece whose band holds the
    discharge stands, and this piece's own height of the passage through it.

    One station, `(x, y, z)`: the core's own west flank and the tube's own axis where it comes
    through, in the machine's own frame. A RIB is fused up the wall's inner face OUT TO THAT
    FLANK, and the whole passage is cut back out of it in ONE profile — mouth, roofed duct, open
    groove and run-out ramp are one polygon, one passage, and what changes down it is how much
    of the wall is still standing outboard of it. The mouth is `vent_channel_w` square, on the
    tube's own axis, and its lip is the rib's east face — the face that lands on the core.

    INSIDE THE FLANK ITS CEILING IS A 45° HIP off the channel's own two jambs, so the hidden
    tunnel closes course by course rather than bridging. At the flank's interior face that hip
    has reached its apex and leaves a solid transom over the whole opening. THE EXPOSED ROOF
    RAMPS FROM THAT WALL IN X: one millimetre up for every millimetre it reaches to the core,
    with the rib's cap parallel above it. The chase therefore follows the box's wall-furniture
    rule wherever it is actually furniture, while the buried part uses its jambs where no wall
    root crosses the opening.

    NEITHER THE RIB NOR THE PASSAGE CROSSES THE SEAM. They part on different planes and for
    different reasons, and between them nothing of one piece stands in the other's travel.
    THE RIB PARTS ON THE RIM, which is the bottom piece's own top: below it the rib is the
    bottom's, above it there is no bottom piece to sweep and the top carries its own share
    with a `vent_rib_wall` liner on the west side. THE PASSAGE PARTS ON THE SEAM AND BOTH
    PIECES CUT IT. A piece keeping its own material in
    the duct's plan is a piece narrowing the duct, and below `groove_top` it is the wall
    itself that has to open — the discharge leaves through the flank there, and half that
    opening is the top piece's to give. Below the rim the piece's own skin is the duct's west
    face, as it is for the groove; above it the liner is.

    AND WHERE THE PASSAGE MEETS THE Z SEAM'S OWN BAND, THE RIB YIELDS AND THE PASSAGE DOES
    NOT. The rib is `vent_rib_wall` longer than its passage at each end, so a rib standing in
    the actual back rail band — the full-section foot followed by the hook profile — is two
    solid slabs swept the length of the rail as the top comes home. The passage is the hole
    through it and sweeps nothing, so it goes straight across: the rail gives up
    `vent_channel_w` where the one opening that has to cross it does, and the duct keeps its
    whole section.

    THE RIB RUNS OUT WITH THE RAMP. It stands behind the channel's floor, so it reaches as far
    down as that floor is still inboard of what the skin alone stands `vent_rib_wall` behind.
    Under that the ramp is cutting skin the wall already had, and the rib ends on the ramp's
    own slope."""
    for sx, sy, sz in stations:
        half = vent_channel_w / 2.0 + vent_rib_wall
        rib_x = sx                                  # the lip, on the core's own flank
        floor_x = rib_x - vent_rib_wall             # the channel's back face, all the way down
        ramp_depth = floor_x - outer[0]
        ramp_rise = ramp_depth / math.tan(math.radians(vent_ramp_angle))
        vent = sz - vent_duct_drop - vent_groove_drop - ramp_rise
        # THE RIB IS ONE PIECE'S AND THE PASSAGE IS THE COLUMN'S. The discharge opens
        # through the wall at the ramp's foot, so the piece whose band holds that foot is
        # the one that stands the rib — but the passage crosses the Z seam, and a piece
        # that keeps its own material in the duct's plan is a piece narrowing the duct. So
        # both cut, and the joint gives up the same `vent_channel_w` on either side of it.
        if not (y0 <= sy <= y1 and vent < z1 and sz + half > z0):
            continue
        owns = z0 <= vent <= z1
        mouth_top = sz + vent_channel_w / 2.0
        mouth_bot = sz - vent_channel_w / 2.0
        groove_top = sz - vent_duct_drop            # where the skin opens
        ramp_top = groove_top - vent_groove_drop
        ramp_bot = ramp_top - ramp_rise              # where the floor has met the outer face
        # The ramp is carried one more millimetre of DEPTH past that, out into air.
        over = ramp_rise / ramp_depth
        # And the rib to where the skin alone stands `vent_rib_wall` behind the floor.
        rib_end = ramp_top - ramp_rise * ((floor_x - (inner[0] - vent_rib_wall))
                                          / ramp_depth)
        rim = z_seam + z_rise                       # the back column's own; the chase is its
        liner_x = inner[0] + slide_slip + vent_rib_wall
        hip = vent_channel_w / 2.0                  # the buried 45° close on the channel half-width
        root_x = back_top_flank_face()[0]           # the exposed rib's actual wall root
        roof_root = mouth_top + hip                 # the buried hip's apex, solid all across above
        roof_run = rib_x - root_x
        if roof_run <= 0.0:
            raise ValueError(
                f"the PRV chase lip at x={rib_x:g} does not stand inboard of its "
                f"wall root x={root_x:g}")
        rib = _xz_prism(sy - half, sy + half,
                        [(inner[0], sz + half), (rib_x, sz + half),
                         (rib_x, ramp_top), (inner[0], rib_end)])
        # THE EXPOSED CAP RAMPS FROM THE WALL. At `root_x` the buried hip has already reached
        # `roof_root`, so material stands across the channel's whole width and the ramp has a real
        # root rather than a first layer bridging between its jambs. It then rises in X to the
        # core's flank, with the same four millimetres of vertical roof section the old parallel
        # Y hips kept. The lower rectangle is already inside `rib`; including it here makes this
        # one closed wedge before the two are fused.
        cap_root = roof_root + 2.0 * vent_rib_wall
        rib = rib.fuse(_xz_prism(
            sy - half, sy + half,
            ((root_x, sz + half), (rib_x, sz + half),
             (rib_x, cap_root + roof_run), (root_x, cap_root))))
        # THE RIB KEEPS OUT OF THE JOINT'S BAND AND THE DUCT DOES NOT, because one of them
        # is material and the other is air. Over the seam's own storey the joint reaches
        # `rail_reach_in + slide_slip` inboard of the flank — head, foot, arm and channel —
        # and the rib is `vent_rib_wall` longer than its passage at each end, so a rib
        # standing in that band is two slabs that sweep the length of the rail as the top
        # comes home. The passage sweeps nothing: it is the hole. So the rib stops at the
        # band and the duct goes straight through it, `vent_channel_w` of the rail given up
        # to the one opening that has to cross it, and the duct keeps its whole section.
        _x_hk, _x_f, _x_a, x_h1 = _rail_x(inner[0], +1.0, "back")
        joint_lane = _ybox(inner[0] - 1.0, x_h1 + slide_slip,
                           sy - half - 1.0, sy + half + 1.0, z_seam, rim)
        rib = rib.cut(joint_lane)
        # AND EACH PIECE STANDS ITS OWN HEIGHT OF IT, the two parting on the seam's RIM,
        # which is the bottom piece's own top. Below the rim the rib is the bottom's and the
        # top's flank clears it — the band above is what `joint_lane` already took. Above the
        # rim there is no bottom piece at all, so the top carries its share and sweeps air.
        # NOTHING OF EITHER CROSSES INTO THE OTHER'S TRAVEL, so the top needs no berth cut
        # down its flank for a rib that was never in it.
        band = ((outer[4] - 1.0, rim) if owns else (rim, outer[5] + 1.0))
        share = rib.intersect(
            _ybox(outer[0] - 1.0, outer[1] + 1.0,
                  sy - half - 1.0, sy + half + 1.0, band[0], band[1]))
        if not owns:
            # AND THE TOP SHARE'S RIB ROOTS ON THE WALL AT ITS OWN FLOOR. Its underside begins
            # on `rim` at the actual flank face and rises one-for-one to the lip, where more
            # than `vent_rib_wall` remains below the square mouth, so the whole projection grows
            # from wall stock. IT IS TAKEN OUT OF THE SHARE AND NOT OUT OF THE RIB, because a
            # cutter carried below `rim` to keep off a coincident plane reaches the ground half's
            # own crest there — `joint_lane` clears that band only as far inboard as the rail
            # reaches, and the run from the rail to the lip is the piece below's to stand.
            share = share.cut(_xz_prism(
                sy - half - 1.0, sy + half + 1.0,
                ((root_x, rim - 1.0), (rib_x + 1.0, rim - 1.0),
                 (rib_x + 1.0, rim + (rib_x + 1.0 - root_x)),
                 (root_x, rim))))
        solid = solid.fuse(share)
        solid = solid.cut(_xz_prism(sy - vent_channel_w / 2.0, sy + vent_channel_w / 2.0,
                                    [(rib_x + 1.0, mouth_top),       # the mouth, through the lip
                                     (rib_x + 1.0, mouth_bot),
                                     (floor_x, mouth_bot),           # \ the floor, straight down
                                     (floor_x, ramp_top),            # /  behind duct and groove
                                     (outer[0] - 1.0, ramp_bot - over),   # the ramp, run out
                                     # The groove's open side closes on a 45-degree X roof.
                                     # Its visible root stays at `groove_top` on the show face;
                                     # the one-millimetre cutter overrun starts one lower, and
                                     # the inner point rises by the wall's exact three-millimetre
                                     # section, making the complete down-facing transition
                                     # support-free.
                                     (outer[0] - 1.0, groove_top - 1.0),
                                     (inner[0], groove_top + (inner[0] - outer[0])),
                                     (inner[0], rim),                # is the duct's west face;
                                     (liner_x, rim),                 # above it the liner is,
                                     (liner_x, mouth_top)]))         # and the rib roofs the duct
        # THE BURIED ROOF CLOSES FROM ITS JAMBS. The flat square would otherwise bridge between
        # them inside the flank, so this short part keeps the compact Y hip up to the wall's actual
        # interior face. There the hip's apex is the transom the exposed ramp roots on.
        solid = solid.cut(_yz_prism(
            liner_x, root_x,
            ((sy - hip, mouth_top), (sy, roof_root), (sy + hip, mouth_top))))
        # AND THE EXPOSED ROOF LEANS IN X FROM THAT WALL. Its root is the buried hip's apex, where
        # the wall is solid over the opening's full width; from there every layer advances one
        # millimetre toward the core for every millimetre it rises. The square passage remains the
        # minimum section, then gains headroom toward the lip rather than carrying a Y gable out
        # over an eight-millimetre wall-rooted projection.
        solid = solid.cut(_xz_prism(
            sy - hip, sy + hip,
            ((root_x, mouth_top), (rib_x + 1.0, mouth_top),
             (rib_x + 1.0, roof_root + (rib_x + 1.0 - root_x)),
             (root_x, roof_root))))
    return solid


def _west_cradle(solid, inner, stations, y0, y1, z0, z1):
    """The −X strip's MQ-6 card slot added to a PIECE, for the stations inside the depth and
    height band that piece owns — the same band test `_side_wells` makes.

    Each station is `(x, y, z)`: the card's own mid-plane, and its centre along the strip and in
    height. Nothing else is passed, because nothing else varies — the slot is one board's
    envelope and one slip fit, read off the reference solid.

    TWO POSTS STAND ON THE SLAB, one at each end of the card's long run, rooted on the wall as
    well and grooved on the faces they turn toward each other. The card DROPS IN FROM ABOVE and
    lands on the shoulder at the foot of each groove — so a groove is blind at the bottom and
    open at the top, and the whole cradle grows UP off the slab: first layer on the bed, every
    layer after it on the one below, nothing over air and no support to pick out of a groove.
    That is what standing the card along the strip buys, and it is why it lies that way.

    THE GROOVES TAKE THE ENDS OF THE LONG RUN, and how much they may take is the CAN'S to say.
    The can is centred on the board and leaves half a millimetre at each long edge, so the ends
    are the only material clear of it — a post reaching further in than the can leaves is a post
    driven into the sensor. So the grip is `mq6_grip` or what the can leaves, whichever is less,
    and the two posts pass either side of the can rather than through it.

    THE EAST CHEEK IS CUT ACROSS THE HEADER. The pins face east off the card and the loom lands
    on them out of the bay, so a cheek running unbroken past them is a cheek nothing can reach
    through. The cut is struck on the header's own band — `header_span` states both how far in
    off the card's end the row stands and how far it runs — and it is taken at BOTH ends,
    because which end of the card the header lands at is the card's turn to state and not this
    slot's. IT RUNS TO THE TOP OF THE POST: up is where the loom comes from, and a cut closed at
    its crown would leave the cheek above it reaching sideways off the post over open air, which
    is the one thing this cradle exists to have none of.

    THE WALL IT IS STRUCK FROM IS THE ONE THAT IS THERE. The card stands under a Z seam, and a
    flank under a seam carries its lip's own wall down to the slab — so the datum is
    `lip_face_x` and not `interior_x`, `2 * wall` of flank and not one. The can bottoms on that
    plane, through the well `_front_bottom_flank_skin` opens for it, and
    `enclosure_assembly.build_mq6` seats the card on the same call."""
    span, off = _mq6.header_span()
    across = _mq6.PIN_SQ / 2.0 + mq6_header_relief
    grip = min(mq6_grip, (mq6_card_y - mq6_can_yz) / 2.0)
    for sx, sy, sz, *_foot in stations:
        if not (y0 <= sy <= y1 and z0 <= sz <= z1):
            continue
        gx0 = sx - mq6_card_x / 2.0 - mq6_slot_press
        gx1 = sx + mq6_card_x / 2.0 + mq6_slot_press
        px0, px1 = lip_face_x()[0], gx1 + mq6_rail_wall
        zb, zt = sz - mq6_card_z / 2.0, sz + mq6_card_z / 2.0
        for into in (1.0, -1.0):
            end = sy - into * mq6_card_y / 2.0
            # The post: slab to the card's own crown, rooted on the wall over its whole depth.
            pa, pb = sorted((end - into * mq6_rail_wall, end + into * grip))
            solid = solid.fuse(_ybox(px0, px1, pa, pb, inner[4], zt))
            # And its groove, open at the top so the card comes in from above and blind at the
            # bottom so it lands: what it lands ON is the post's own first `mq6_rail_wall`.
            ga, gb = sorted((end - into * mq6_slot_press, end + into * (grip + 1.0)))
            solid = solid.cut(_ybox(gx0, gx1, ga, gb, zb, zt + 1.0))
            # And the east cheek off the header's own band, from the pin field's foot CLEAR TO
            # THE TOP. Up, because the loom comes down out of the bay onto the pins and a cheek
            # over them is a cheek it cannot pass — and because a cut closed at its crown would
            # leave the cheek above it standing on nothing, reaching sideways off the post over
            # open air. Everything this cradle keeps runs to the bed.
            ha, hb = sorted((end + into * (mq6_card_y / 2.0 - off - across),
                             end + into * (mq6_card_y / 2.0 - off + across)))
            solid = solid.cut(_ybox(gx1, px1 + 1.0, ha, hb,
                                    sz - span - mq6_header_relief, zt + 1.0))
    return solid


def _cond_cradle_corbel(inner, station):
    """The crown rail's full-width 45° underside, rooted on the front wall."""
    face, cx0, cx1, fz0, fz1, root = station
    root_y = min([front_plane_y] + [f for rx0, rx1, rz0, rz1, f in (fridge_relief,)
                                    if cx0 >= rx0 - 1e-6 and cx1 <= rx1 + 1e-6
                                    and rz0 <= (fz0 + fz1) / 2.0 <= rz1])
    free_y = face + cond_slot_grip
    reach = free_y - root_y
    return _yz_prism(cx0, cx1, ((root_y, root - reach),
                                (root_y, root), (free_y, root)))


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
    piece with both faces it stands on. The CROWN rail is one section under its own groove and its
    whole flat underside is carried back to the front wall on a 45° corbel. The rail reaches only
    `cond_slot_grip` past that wall, so the wedge is the same three millimetres deep and leaves the
    condenser's upper flange more than one wall above it.

    THE GROOVE IS STRUCK OFF THE FLANGE IT TAKES and not off a figure typed here: `cond_slot_half`
    reads the station's own sheet. At the seated wall stop its roof keeps that exact opening;
    from there it rises toward the bay at 45° until it runs through the rail's crown. The flange
    therefore keeps its datum and fit while the one-millimetre opening is never closed by a flat
    roof printed over material below it."""
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
        if root > inner[4] + 1e-6:
            solid = solid.fuse(_cond_cradle_corbel(
                inner, (face, cx0, cx1, fz0, fz1, root)))
        # The groove runs out past the rail's own aft end, so the flange enters from the bay. Its
        # floor remains flat; its roof rises one-for-one from the seated wall stop into that open
        # end, preserving the exact fit at `face` and removing the short material-rooted bridge.
        mouth = face + cond_slot_grip + 1.0
        run = mouth - face
        solid = solid.cut(_yz_prism(
            cx0 - 1.0, cx1 + 1.0,
            ((face, fz0 - half), (mouth, fz0 - half),
             (mouth, fz1 + half + run), (face, fz1 + half))))
    return solid


def _cond_mount_corbel(inner, station):
    """The upper condenser finger's 45° underside, rooted on its standing east fin."""
    flank, my0, my1, bosses = station
    west = min(bx for bx, _by, _tip in bosses) - mount_boss_dia
    tip = max(t for _bx, _by, t in bosses)
    root = tip - cond_boss_t
    return _xz_prism(my0, my1, ((west, root), (flank, root),
                                (flank, root - (flank - west))))


def _cond_mount(solid, inner, station, y0, y1, z0, z1):
    """The condenser block's AFT mount added to a PIECE: one fin on the +X wall and a finger
    reaching west off it under each of the block's two mount holes.

    The station is `(flank, my0, my1, bosses)`: the plane the fin's own west face stands on —
    the block's east flank and one `cond_mount_clear` — the Y band the whole of this occupies,
    and one `(x, y, tip)` per hole, where `tip` is the face of the flange that screw pulls down.

    THE LOWEST FINGER RUNS TO THE SLAB, because nothing stands between its own tip and the floor
    and the block's aft end comes down on it. The upper one is one `cond_boss_t` deep and its
    whole underside is carried at 45° back to the standing fin. The wedge occupies the empty aft
    recess and stops on the fin's west face, one `cond_mount_clear` off the condenser; no column
    roots inside the block's own flanks."""
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
    if crown > floor_tip + 1e-6:
        solid = solid.fuse(_cond_mount_corbel(inner, station))
    for bx, by, tip in bosses:
        solid = solid.cut(_zcyl(heatset_dia / 2.0, bx, by, tip - cond_bore_depth, tip))
    return solid


def vent_band(airway):
    """The height the condenser's vents are pierced over, as `(z0, z1)` — THE FAN'S FOOTPRINT
    ON THE FLANK, taken off the block where it stands.

    `cond_airway`'s last two figures are the placed block's own crown and base, so the fan's
    two insets are read against metal that is already somewhere rather than against a station
    typed here: raise the block and the vent rises with it. Everything else in the feature —
    the transoms, the free area, the window a reading is taken over — is struck off this one
    pair."""
    return airway[2] + cond_fan_rise, airway[3] - cond_fan_drop


def vent_transoms(airway):
    """The unpierced bands crossing that vent, as `((z0, z1), ...)`.

    THE LAYOUT IS THE BAND DIVIDED, not a list of stations. `cond_vent_transoms` transoms of
    `cond_vent_transom_h` leave `cond_vent_transoms + 1` equal slot segments, so the band closes
    on itself exactly and stays symmetric about its own mid-height whichever of the three figures
    moves. The assertion is that closure: it is the one thing arithmetic here can get wrong."""
    z0, z1 = vent_band(airway)
    run = (z1 - z0 - cond_vent_transoms * cond_vent_transom_h) / (cond_vent_transoms + 1)
    bands = tuple((z0 + (k + 1) * run + k * cond_vent_transom_h,
                   z0 + (k + 1) * run + (k + 1) * cond_vent_transom_h)
                  for k in range(cond_vent_transoms))
    closed = (cond_vent_transoms + 1) * run + cond_vent_transoms * cond_vent_transom_h
    assert abs(closed - (z1 - z0)) < 1e-9, "the vent's transoms do not close on its band"
    assert all(abs(lo + hi - (z0 + z1)) < 1e-9
               for (lo, _t), (_b, hi) in zip(bands, reversed(bands))), \
        "the vent's transoms are not symmetric about the band"
    return bands


def vent_segment(airway):
    """One slot segment — what a mullion stands free over between two transoms."""
    z0, z1 = vent_band(airway)
    return (z1 - z0 - cond_vent_transoms * cond_vent_transom_h) / (cond_vent_transoms + 1)


def vent_segments(airway):
    """The full-height opening courses between the transoms, bottom to top."""
    z0, z1 = vent_band(airway)
    out, lo = [], z0
    for tz0, tz1 in vent_transoms(airway):
        out.append((lo, tz0))
        lo = tz1
    out.append((lo, z1))
    return tuple(out)


def vent_grooves(outer, airway):
    """Every groove the condenser's vents pierce, as `((sx, y), ...)` — the flank's own sign and
    the groove's station on it, WALKED OFF ARC LENGTH and not counted off a wall.

    `flute_centres` is the field's own list and `plan_at` is what puts each one somewhere; a
    groove is on a flank when the plan's outward normal there is ±X. So the vent lands on groove
    centres by construction and follows the field if `flute_count` is ever retuned — there is no
    Y station typed anywhere in this feature.

    A GROOVE IS IN WHEN ITS WHOLE SLOT IS. The block's airway stops where its two recesses begin
    (`cond_airway`), and a slot running past that line opens on the sheet the box holds the block
    by rather than on the finstack."""
    if not airway:
        return ()
    ay0, ay1 = airway[0], airway[1]
    half = reeding.pierce_width / 2.0
    out = []
    for arc in flute_centres(outer):
        (_px, py), (nx, _ny) = plan_at(arc, outer)
        if abs(abs(nx) - 1.0) > 1e-9:
            continue
        if ay0 - stated_bound_tol <= py - half and py + half <= ay1 + stated_bound_tol:
            out.append((1.0 if nx > 0.0 else -1.0, py))
    return tuple(sorted(out))


def _vent_runs(solid, outer, airway, sx, y):
    """One groove's slot on one flank, as the (z0, z1) runs it comes out as.

    THE PIECE IS ASKED, not told. What the slot is cut out of is the flank, and what it must not
    break out of is anything ROOTED on the flank's inner face behind that same groove — so the
    reading is one probe `cond_vent_probe` deep and `cond_vent_clear` past both jambs. Whatever
    it finds takes its own height plus that same clearance above and below out of the band. A
    body standing free of that face is not in it and is not the vent's to answer for.

    THE TRANSOMS DIVIDE THE ONLY OPENING VOCABULARY. A rooted feature does not leave an odd short
    slit above itself: if its clearance reaches into one of the four equal segments, that whole
    segment stays solid. The outside therefore sees full segments or a deliberate fluted land,
    while the feature gets a wall-height root instead of a thin remnant between its crown and a
    one-off slot."""
    band = list(vent_band(airway))
    face = vent_flank_face(sx)
    half = reeding.pierce_width / 2.0
    xs = sorted((face - sx * cond_vent_probe, face - sx * stated_bound_tol))
    probe = _ybox(xs[0], xs[1], y - half - cond_vent_clear, y + half + cond_vent_clear,
                  band[0] - cond_vent_clear, band[1] + cond_vent_clear)
    occupied = tuple((b.zmin - cond_vent_clear, b.zmax + cond_vent_clear)
                     for b in (s.BoundingBox() for s in probe.intersect(solid).Solids()))
    segments = vent_segments(airway)

    def clear(segment):
        z0, z1 = segment
        return not any(max(z0, oz0) < min(z1, oz1) - stated_bound_tol
                       for oz0, oz1 in occupied)

    return tuple(segment for segment in segments if clear(segment))


def _vent_cutter(outer, sx, y, z0, z1):
    """One run, as the prism that cuts it: `reeding.pierce_width` across, struck down the
    groove's own centre, carried clean through the flank, and CLOSED AT BOTH ENDS BY A 45° HIP.

    The hip is `relief_chamfer`, the angle every relief on this box rises at, and it costs the
    show face nothing — a slot is narrower than the groove it lies in, so both hips sit down
    inside the groove's own shadow. It is also what makes the piece printable at either end: the
    piece stands on its floor and the build axis runs up this wall, so the sill only takes
    material away as the print climbs and the ceiling closes at exactly the angle the box
    supports nothing steeper than."""
    face = vent_flank_face(sx)
    skin = outer[1] if sx > 0.0 else outer[0]
    half = reeding.pierce_width / 2.0
    hip = half * math.tan(math.radians(relief_chamfer))
    return _yz_prism(face - sx * 1.0, skin + sx * 1.0,
                     ((y, z0), (y + half, z0 + hip), (y + half, z1 - hip), (y, z1),
                      (y - half, z1 - hip), (y - half, z0 + hip)))


def vent_measure(solid, outer, airway, sx):
    """One flank's vent, read off a BUILT PIECE — every opening the wall actually came out with,
    and from those the slots, the mullions between them, the height each mullion stands free
    over, and the free area the whole window opens.

    A READING, AND NOT PART OF THE DRAWING. `_realized` keeps a piece between builds, so a
    reading taken while cutting is a reading the second build never takes and no row says so —
    `build_pieces` draws and measures nothing. This is asked of the piece afterwards, by
    `enclosure_assembly.check_flank_vents` for the ledger and by `main` for the page, off one
    derivation either way.

    ONE CUT, AND EVERY FIGURE OFF IT. The flank's own mid-section is taken as a slab over the
    whole window and the whole band, and the piece is CUT OUT of it: what comes back is one solid
    per OPENING, which is what the vent is. So a run's height is that solid's height and no
    transom station is read back here, a slot's width is its width across the groove, a mullion is
    the gap between two neighbouring slots, and the free area is what all of them come to. Read at
    the mid-section because that is where a slot is a slot the whole way through.

    A MULLION STANDS FREE OVER THE OPENING BESIDE IT. Between two transoms the wall holds a
    mullion at its two ends and nowhere in between, so the tallest opening on the flank IS the
    tallest unbraced picket on it — the figure the transoms exist to set."""
    ay0, ay1 = airway[0], airway[1]
    bz0, bz1 = vent_band(airway)
    face = vent_flank_face(sx)
    skin = outer[1] if sx > 0.0 else outer[0]
    xs = sorted(((face + skin) / 2.0 - 0.1, (face + skin) / 2.0 + 0.1))
    window = _ybox(xs[0], xs[1], ay0, ay1, bz0, bz1)
    opened = window.cut(solid)
    boxes = sorted((b.ymin, b.ymax, b.zmin, b.zmax)
                   for b in (o.BoundingBox() for o in opened.Solids()))
    # The openings gathered back into the slots they belong to: two runs of one slot share a Y
    # span, and two slots never overlap in Y because a mullion stands between them.
    columns = []
    for ymin, ymax, zmin, zmax in boxes:
        if columns and ymin < columns[-1][1] - stated_bound_tol:
            columns[-1][1] = max(columns[-1][1], ymax)
            columns[-1][2].append((zmin, zmax))
        else:
            columns.append([ymin, ymax, [(zmin, zmax)]])
    slots = [hi - lo for lo, hi, _r in columns]
    mullions = [lo1 - hi0 for (_l0, hi0, _r0), (lo1, _h1, _r1) in zip(columns, columns[1:])]
    runs = [(hi - lo) for _l, _h, rs in columns for lo, hi in rs]
    return {"slots": slots, "mullions": mullions, "runs": runs,
            "tallest": max(runs, default=0.0),
            "open_mm2": opened.Volume() / (xs[1] - xs[0]),
            "band": (bz0, bz1)}


def _vent_clears_west_chute(sx, y, west_cradle):
    """Whether one complete groove stays at least one wall from the MQ-6 chute.

    The chute is cut only from front-bottom's added inner skin. A vent in the next groove can
    therefore leave an unnamed strip of that skin between its slot jamb and the chute edge even
    though both openings are individually valid. Keep that whole groove solid when the strip
    would be thinner than `wall`; opening further into the chute would trade the nib for a leak
    in the sensor well. Grooves crossing the chute itself remain vents, because there is no
    intervening material to protect."""
    if sx > 0.0 or not west_cradle:
        return True
    slot_lo = y - reeding.pierce_width / 2.0
    slot_hi = y + reeding.pierce_width / 2.0
    chute_half = mq6_can_yz / 2.0 + mq6_slot_press
    for _x, cy, _z in west_cradle:
        chute_lo, chute_hi = cy - chute_half, cy + chute_half
        if slot_hi <= chute_lo:
            gap = chute_lo - slot_hi
        elif chute_hi <= slot_lo:
            gap = slot_lo - chute_hi
        else:
            continue
        if gap < wall - stated_bound_tol:
            return False
    return True


def _flank_vents(solid, inner, outer, airway, y0, y1, z0, z1, west_cradle=()):
    """The condenser's INTAKE and EXHAUST cut into a piece's ±X flanks, for the piece whose
    bands hold the block's airway.

    THE VENT IS THE FLUTES, PIERCED — one slot down the floor of every groove standing over the
    finstack, `reeding.pierce_width` across on the field's own centres, clean through the
    `2 * wall` a bottom piece's lipped flank carries (`_lip_underwall`). Both jambs run WITH the
    flute and the groove carries on past both ends of the slot at full depth, so nothing crosses
    a flute anywhere here and no edge this makes is one the skin stops on — which is a fact
    `flute_skin` reads for itself off the run's own two ends rather than being told.

    EVERY GROOVE AND NOT ALTERNATE. What a slot is measured against is the MULLION between two
    of them, and the coupon at `c14bb2fff` printed the schemes side by side: at this pitch a 3.1 mm
    slot down every groove leaves `reeding.mullion` of material carrying the exterior's four wall
    loops with `reeding.pierce_max` still overhead, and it is both more open and thicker at its
    thinnest than the same field pierced down alternate grooves at the full groove width.

    NO ORPHAN OPENING. If a rooted feature leaves a single aperture marooned beyond its solid
    land in one course, that aperture stays fluted wall too. Two adjacent openings are a grille;
    one isolated slit is the same accidental-looking nick the full-segment rule removes in Z.

    NO THIN STRIP BESIDE THE MQ-6 CHUTE. On the intake flank the two grooves whose slot jambs
    would stop less than one wall from that chute remain whole for every course. The chute keeps
    its fitted outline and the wall keeps complete stock; neither opening is widened into the
    other merely to erase their narrow intersection.

    LAST OF THE FLANK'S WORK, after every rail, fin, pod and pocket either wall carries — because
    a slot is air, air a later step fuses back in is not a slot, and because what decides where
    each slot stops is what the piece has standing on that face when the cut is made."""
    if not airway:
        return solid
    ay0, ay1, az0, az1 = airway
    if not (y0 <= (ay0 + ay1) / 2.0 <= y1 and z0 <= (az0 + az1) / 2.0 <= z1):
        return solid
    runs = {}
    for sx, y in vent_grooves(outer, airway):
        if not _vent_clears_west_chute(sx, y, west_cradle):
            continue
        got = _vent_runs(solid, outer, airway, sx, y)
        runs.setdefault(sx, []).append((y, got))
    courses = vent_segments(airway)
    for sx, columns in runs.items():
        for course in courses:
            present = [course in got for _y, got in columns]
            for i, is_open in enumerate(present):
                neighbours = ((i > 0 and present[i - 1])
                              + (i + 1 < len(present) and present[i + 1]))
                if is_open and neighbours < cond_vent_island_min - 1:
                    y, got = columns[i]
                    columns[i] = (y, tuple(run for run in got if run != course))
    cutters = [_vent_cutter(outer, sx, y, rz0, rz1)
               for sx, columns in runs.items() for y, got in columns for rz0, rz1 in got]
    if not cutters:
        return solid
    return solid.cut(*cutters)


def vent_readings(pieces, box):
    """What the condenser's vents came out as, per flank sign, off the piece that carries them.

    THE PIECE IS FOUND THE WAY THE CUT FOUND IT — by whose own bands hold the block's airway
    (`_piece_bands`), which is the same test `build_piece` makes when it hands a station to the
    feature that cuts it. So this asks the piece that was cut and not a piece named here."""
    if not box.pack.cond_airway:
        return {}
    ay0, ay1, az0, az1 = box.pack.cond_airway
    for name, piece in pieces.items():
        if name.count("-") != 1:
            continue
        y0, y1, z0, z1 = _piece_bands(box, name)
        if y0 <= (ay0 + ay1) / 2.0 <= y1 and z0 <= (az0 + az1) / 2.0 <= z1:
            solid = piece.val() if hasattr(piece, "val") else piece
            return {sx: vent_measure(solid, box.outer, box.pack.cond_airway, sx)
                    for sx in (-1.0, 1.0)}
    return {}


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
        # The fuse above already welds the block to the slab at `inner[4]`, so that plane is
        # no longer a face of `solid` there — the notch's floor wants no overshoot past it, only
        # the block's own free top (`tip`) does. A cutter reaching below `inner[4]` would carve
        # into the slab itself rather than the block that stands on it.
        solid = solid.cut(_ybox(min(lap, cx), max(lap, cx), face, cy + 1.0,
                                inner[4], tip + 1.0))
        solid = solid.cut(_zcyl(r + slip, cx, cy, inner[4], tip + 1.0))
    return solid


def _core_holds(solid, inner, stations, y0, y1, z0, z1, face=None):
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
    support, the way the ASSE anchor on this same wall does.

    AND ITS TIP CARRIES A LEAD. The core rides IN under these feet — through the open
    Y-seam mouth, aft to its seat, the crown sliding under the bearing face at the same
    zero the seat closes at — so the foot's fore arris is eased 45° up toward the tip.
    A crown arriving a hair high meets a ramp and is pressed down onto the slab's own
    datum instead of stopping on an edge."""
    face = inner[3] if face is None else face
    lead = 1.0
    for sx0, sx1, aft, crown in stations:
        if not (y0 <= aft <= y1 and z0 <= crown <= z1):
            continue
        tip, back = aft - core_hold_reach, face
        solid = solid.fuse(_yz_prism(sx0, sx1, (
            (tip + lead, crown), (back, crown), (back, crown + core_hold_rise),
            (tip, crown + core_hold_land), (tip, crown + lead))))
    return solid


# --- the tap-water chain's cradle on the −X wall ---------------------------
#
# The ASSE anchor's own section, and what it spends on either side of the chain's axis.
# How far the anchor's upper flank runs off the axis. It is SHORT: the chain's own top flat
# stands one `clearance-floor` under the ceiling, so a lip carried up to that flat's arris is a
# lip standing in the only air a tie could have used, and the zip tie climbs past this lip on its
# way over the chain. The lower flank's reach is not stated here at all — the station carries it,
# struck on the chain's own lowest arris, because an anchor deeper than the body it holds is PETG
# holding air.
asse_cradle_up = 9.0
asse_v_half = 60.0          # half the V's included angle, off the axis plane
asse_cradle_lip = 4.0       # block carried past the flanks, so the V cut is never clipped
# THE ZIP TIE'S CAVITY THROUGH THE ANCHOR'S BACK, closed on every side but its two mouths.
#
# STRAIGHT ON THE WEST, THE ANCHOR'S OWN V ON THE EAST. The V's apex stands closest to that
# straight, so the cavity is narrowest at the axis and flares to both mouths: each mouth opens
# `wall / sin 60°` off its lip's own arris, on the block's face, and at the axis the flare
# leaves a zip tie pushed through the room to turn the vertex by cutting its corner.
#
# ONE CHANNEL PER ZIP TIE, `tie_cav_wide_w` long and centred on its own tie band. Two zip ties go
# through this block, so what it owes them is two holes: the back stands solid fore and aft of
# each and between them, and the ceiling over the run keeps whatever corbel the strip has
# (`back_top_ceiling_reliefs`). A single opening spanning the pair would give up all of that for
# thirty millimetres of block nothing passes through.
#
# ITS TWO FLANKS ARE BOTH ONE `wall`. The cavity is what is LEFT between them — a `wall` off the
# anchor on the east and a `wall` off the side wall's own inner face on the west — so its width is
# a remainder and not a number, and every face of it is the section the rest of this box is.

# --- what a zip tie is, wherever one is cut for on this box --------------------
#
# Every cavity on this wall carries the same fastener, so its section is stated once here and the
# features read it. `enclosure_assembly.ASSE_TIE_T` is the same zip tie's THICKNESS, and it is stated
# over there because what it sets is the deck's own storey rather than anything printed.
# TWO ZIP TIES, AND WHAT PICKS BETWEEN THEM IS THE LOOP. A zip tie turns INSIDE the cavity, so what it
# reaches round is the body together with the web between that body and the cavity — the convex
# perimeter of the pair, and not of the wall the rib stands on:
#
#     carb-1 tube in its rib      [40.1 mm](LOOP_CARB_1)
#     DIGITEN arm in its anchor   [59.6 mm](LOOP_DIGITEN)
#     WR1110 barrel in its rib    [84.1 mm](LOOP_WR1110)
#     ASSE barrel in its anchor   105.2 mm
#
# A 4" tie closes about 69 mm of loop, which takes the first two; the regulator's takes the 6",
# which closes about 110. The ASSE barrel's passes both and takes the 8", and an 8" tie is a 50 lb
# tie at 0.19" where the rest are 18 lb at 0.1" — so that anchor's cavity, alone on this box, is
# cut to the wider zip tie. Every other cavity here takes the same 0.1" section at any length.
tie_w = 2.5           # the 18 lb zip tie, across its width — 0.1"
tie_wide_w = 4.826    # and the 50 lb zip tie's — 0.19"
tie_t = 1.0           # both, through the thickness
tie_cav_buffer = 1.0        # the room a cavity carries over the zip tie
tie_cav_w = tie_w + tie_cav_buffer
tie_cav_wide_w = tie_wide_w + tie_cav_buffer
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
    each one presents about the axis, because that is the fitting's own — so the anchor is cut to
    each in turn, the steps between them catch the barrel fore and aft, and the fit across the V
    is a slip and not a socket.

    WHAT A TIE CAN AND CANNOT DO HERE. A tie is a closed loop, and a loop round this chain has to
    pass over its top flat — so the storey the chain lies on is struck to leave that channel under
    the top wall, and the wall itself is never cut for it
    (`enclosure_assembly.DECK_CEILING_CLEAR`). The loop runs down the CAVITY through the back of
    this anchor, out under the block, east beneath the barrel, up its east flank, over the top flat
    through that channel, and back into the cavity. So it closes round the chain and the anchor's
    own back together, and what it pulls is the chain into the V.

    ONE CHANNEL PER ZIP TIE, AND EACH IS CLOSED ON EVERY SIDE BUT ITS TWO MOUTHS. It stands west of
    the apex with one `wall` of PETG between it and the anchor, so at no station is it anything
    but a hole through solid material, and a zip tie in it stays where it was put. Two zip ties, two
    holes: the block's back is solid fore and aft of each and between them.

    A 45° CORBEL CARRIES THE BLOCK'S UNDERSIDE, run the anchor's whole length and rooted on the
    wall the block is rooted on. It tapers to nothing at the DEEPEST SECTION'S OWN V FOOT — the
    same apex the tie cavities are struck on — so under the barrel it carries that underside
    whole, and under a bored section, where the block reaches further east than any wedge off
    this wall may stand without meeting what hangs off the chain, it carries what it reaches.
    The V's own two flanks stand 30° off vertical and carry themselves.

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
    # THE CORBEL UNDER ALL OF THEM, on the deepest section's own V foot: that flank is the
    # furthest west anything of this anchor comes down to, so a 45° struck to it is the wedge the
    # narrowest section can carry whole and every wider one can stand on. Fused before the ties'
    # channels so each channel goes on through it.
    apex = min(w for _y0, _y1, w, _r, _a in sections)
    foot = apex + dn * run
    corbel = foot - inner[0]
    solid = solid.fuse(_xz_prism(sections[0][0], sections[-1][1],
                                 [(foot, z_axis - dn), (inner[0], z_axis - dn),
                                  (inner[0], z_axis - dn - corbel)]))
    # THE ZIP TIES' CHANNELS, ONE EACH, cut after every section is fused so a neighbour's block
    # cannot fill one back in. Struck on the DEEPEST section's apex, which is the barrel's: that V
    # stands furthest west, so a cavity clear of it by one `wall` is clear of the other two by more
    # and the web comes out no thinner than stated at any station.
    #
    # IT IS THE WIDE ZIP TIE'S CAVITY. The barrel and this anchor make a 105 mm loop, past what a 4"
    # tie closes, so what shuts it is the 8" — and an 8" is a 50 lb tie, half again as wide as the
    # 18 lb zip tie the flow-meter anchors and the runs' ribs take.
    for ty in ties:
        if not (sections[0][0] <= ty <= sections[-1][1]):
            raise ValueError(
                f"_asse_cradle: tie band {ty:.2f} falls outside the anchor's run "
                f"[{sections[0][0]:.2f}, {sections[-1][1]:.2f}]. A zip tie's channel is cut through "
                f"the block at its own band, so a band off either end has no channel at all.")
    for ty in ties:
        solid = solid.cut(_asse_tie_cavity(apex, inner[0], z_axis,
                                           ty - tie_cav_wide_w / 2.0,
                                           ty + tie_cav_wide_w / 2.0, up, dn + corbel))
    return solid


def _asse_tie_cavity(x_apex, x_wall, z_axis, y0, y1, up, dn):
    """The zip tie's cavity: STRAIGHT on the west, the ASSE anchor's own V on the east.

    Five points and one cut. The V's apex stands closest to that straight, so the cavity comes out
    narrowest in the middle and flared at both mouths — which is the reach where a hand needs it
    and the room to turn the vertex where a zip tie needs that, out of one shape rather than out of a
    chamfer and a round.

    Both ends run one millimetre past the faces they open on, so each mouth is cut open rather
    than closed by a plane coincident with that face. `dn` is what the caller has standing under
    the axis — the block's own storey and the corbel below it — because a tie's loop leaves this
    cavity by running east UNDER all of it, and a channel that stopped at the block would be
    stopped by the corbel."""
    run = 1.0 / math.tan(math.radians(asse_v_half))
    x_in = x_apex - wall / math.sin(math.radians(asse_v_half))   # a `wall` west of the anchor
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


# --- the flow meter's two anchors, off the top wall ------------------------
#
# A BORE, CONCENTRIC WITH THE BARREL IT TAKES. The arms are round, so the seat is round: half a
# cylinder on the arm's own axis, opening downward, and the arm comes straight up into it.
#
# THE ARC STOPS ON THE ARM'S OWN AXIS PLANE AND THE RIB CARRIES ONE `wall` PAST ITS WIDEST POINT.
# That plane is where the arc is widest, so the rib's own flanks stand `seat_r + wall` off the axis
# and each lip comes out a flat strip one `wall` across. An arc carried past its widest point runs
# out to nothing against the flank and leaves a feather no nozzle can lay down.
flow_meter_anchor_wall = 3.0
# ITS LENGTH ALONG THE ARM IS ITS CAVITY'S. One zip tie crosses each anchor, so the rib is that
# zip tie's cavity with `tie_cav_wall` of itself at each end of it, and the band `flow_meter_anchors`
# reads off the barrel is what that rib is centred in.
flow_meter_anchor_len = tie_cav_w + 2.0 * tie_cav_wall
# The zip tie's cavity through each anchor, over the bore. Its floor is the SEAT'S OWN ARC offset out
# by one `wall` — concentric, so the web reads `wall` all the way round — and ITS CEILING IS THE
# TOP WALL'S OWN INNER FACE. The channel is everything left between them, deepest over the crown
# and flaring as the arc falls away to each mouth.
#
# The zip tie bears straight on that face and what stands over it is `wall`: the top wall's own
# section, which is already there. A plate of this rib's under it would be a second `wall` doing
# the first one's job.


def _digiten_bore(x_axis, z_axis, r, y0, y1, reach):
    """An anchor's own room: half a cylinder on the arm's axis, opening DOWNWARD, and the whole of
    the room under it.

    The arc runs from one axis-plane lip round the crown to the other, and the box under it carries
    the opening down clear of the rib — so what this cuts is the barrel's room and the air it comes
    up through, and the rib is left as a half-round hood with a flat lip on each side."""
    bore = cq.Solid.makeCylinder(r, y1 - y0, cq.Vector(x_axis, y0, z_axis), cq.Vector(0, 1, 0))
    under = _ybox(x_axis - r, x_axis + r, y0, y1, z_axis - r - reach, z_axis)
    return bore.fuse(under)


# --- the flavour manifold's valve trays -------------------------------------
#
# A VALVE TRAY IS A PLATE WALL TO WALL, with one four-socket `valve_seat` SUNK into it per valve
# on the deck it stands under. `valve_tray` states its thickness, its margin and its seat height
# and draws one in its own frame; this turns that onto the deck's own plane and fuses the plate
# into the piece, the way `_asse_cradle` fuses the ASSE anchor and `_flow_meter_anchors` the flow
# meter's two Vs — and then cuts the seats and the ports' channels out of it.
#
# THE PLATE IS THE BOSS. A boss is material round a socket, and a plate one socket and one wall
# thick is that material: a seat sunk into it leaves nothing standing off its face. Which is the
# whole point on this piece — it prints the plate VERTICAL, so a boss on it would be a Ø13.2
# cylinder cantilevered into air with its own underside to bridge, and there are thirty-two of
# them. Sunk, the port's channel is a notch running up the plate's own section. The socket is
# still a horizontal blind bore, though, and a round crown on that axis has no layer under it:
# `_valve_socket_cutters` carries its complete circular post room into the same tangent roof as
# every other horizontal bore on this box.
#
# NOTHING FASTENS A VALVE TO IT. The four corner posts press into their sockets and the valve's
# own round body boss lands on the plate's face, which is what sets its height — the same
# bargain the cold core's cap lid strikes under its own three valves, whose thinner lid stands
# the bosses instead.
def _valve_socket_cutters(plane, sign, seat_x, seat_z):
    """One tray seat's four complete post rooms with support-free roofs, in world coordinates.

    `valve_seat` owns the nominal socket: its radius, corner inset and axial floor/top. Turning
    that seat onto a Y deck puts its socket axes on Y and maps a local `(dx, dy)` corner to
    `(seat_x + dx, seat_z - sign*dy)`. The whole nominal circle remains inside `_teardrop_y`;
    only the unsupported world-Z crown is opened above its tangent points. Thus every round post
    still enters to the same floor and bears on the same lower and lateral arcs, while none of
    the thirty-two crowns asks the slicer for a separate interface island.
    """
    along = sorted((plane + sign * _seat.socket_floor_z,
                    plane + sign * (_seat.seat_top_z + 1.0)))
    return tuple(
        _teardrop_y(_seat.socket_radius, seat_x + dx, seat_z - sign * dz,
                    along[0], along[1])
        for dx in (-_seat.corner_inset, _seat.corner_inset)
        for dz in (-_seat.corner_inset, _seat.corner_inset)
    )


def _valve_trays(solid, inner, stations, y0, y1, z0, z1,
                 wall_aft_y=None, flank_bed_z=None):
    """Every valve tray whose deck falls in the depth and height band this piece owns.

    Each station is `(plane, sign, seats)`: the world Y the deck's valves stand their mounting
    faces on, which way their own +Z runs off it, and one `(x, z)` per valve. The plate's own
    extent is the seats' — wall to wall across, and one `valve_tray.reach` plus a margin either
    way along — so nothing here is a dimension this module chose.

    THE SEATS ARE SUNK AND SO IS THE PORT'S OWN CHANNEL. The plate is a socket and a wall thick
    (`valve_tray.THICK`), which is the material a boss would have been, so nothing is fused onto
    its face: the sockets and the channel are CUT, and the face itself is the plane the valve's
    round body boss lands on. A socket's nominal circle is carried whole into a tangent
    world-Z roof by `_valve_socket_cutters`, because the plate stands on Z and its bore lies on
    Y. Everything is struck in the valve's own frame at `plane`, its mounting plane, and turned
    onto the deck — the plate's face follows from `SEAT` and is not the datum anything here is
    placed on.

    A PLATE THAT OUTRUNS ITS OWN WALL IS CORBELLED AT THE ROOT. `wall_aft_y` is
    `collet_plate_spec`'s own `wall_aft_y` — the tee wall's aft face, the plane wall support
    actually ends at (`_tee_wall`). Where that plane falls strictly inside a plate's own
    near/far span, the plate stands on the wall for the inboard share of its thickness and
    overhangs open bay air for the rest: `far - wall_aft_y`, read off the two planes and never
    typed. The corbel rises 45° off the wall's own aft face and closes at the plate's own far
    face, so the flat downward band between the two stops existing — what a hand meets at
    either arris is the corbel meeting a vertical face, not a square step off the wall's crown.
    Struck before the per-seat sockets and port channels below, so a station that already
    breaks the plate's own edge breaks the corbel the same way. A footed plate's own near/far
    never brackets `wall_aft_y` (it stands on a different wall entirely), so this is a
    no-op there rather than a case split.

    THE SOCKET ANSWERS FOR THE POSTS, THE CHANNEL FOR THE PORT, AND NEITHER FOR THE BOSS OR
    THE BOX BEHIND THEM. `valve_tray.build_body_clearance` is what a fuse struck after them
    (the root corbel above) is cut on account of instead: the valve's boss and top box, read
    off `beduan_solenoid` again and grown one `PORT_SLIP`, wherever a station's own transform
    puts it — the four posts stay out of it on purpose, because they are exactly what the
    socket is cut to GRIP, and a second, looser cutter at the same station reams the grip out
    from under it. THE CHANNEL DOES ANSWER FOR THE PORT, BUT ONLY
    AS FAR AS THE PLATE'S OWN FLOOR — its length is struck to reach the plate, which is all a
    port ever used to graze. `wedge_depth` is carried into it below so the same channel reaches
    the corbel's own floor too: a wall the corbel roots on stands nowhere near a valve's port,
    so this only ever lengthens the channel where the root corbel actually adds one.

    THE WALL-TO-WALL PLATE ENDS ON FRONT-TOP'S OWN FLANK BEDDING PLANES. `flank_bed_z` is that
    piece's bed face when this tray belongs to it. The tray crosses the two grown flank sections,
    but it does not grow a second skin below either 45-degree underside; its plate, foot and any
    root corbel are trimmed as one feature before they join the enclosure."""
    for plane, sign, seats in stations:
        zs = [z for _x, z in seats]
        mid_z = (min(zs) + max(zs)) / 2.0
        half = _valve_tray.height() / 2.0
        if not (y0 <= plane <= y1 and z0 <= mid_z <= z1):
            continue
        # The plate: its valve-side face on the plane the valve lands on, its back one `THICK`
        # outboard of that.
        face = plane - sign * _valve_tray.SEAT
        near, far = sorted((face, face - sign * _valve_tray.THICK))
        tray = _ybox(inner[0], inner[1], near, far, mid_z - half, mid_z + half)
        floor = mid_z - half
        wedge_depth = 0.0
        if wall_aft_y is not None and near < wall_aft_y < far:
            wedge_depth = far - wall_aft_y
            tray = tray.fuse(_yz_prism(inner[0], inner[1], [
                (far, floor), (wall_aft_y, floor), (wall_aft_y, floor - wedge_depth),
            ]))
        # THE PLATE'S FOOT: the plate's own whole section carried down to the piece's bed
        # face, its valve-side face one plane with the plate's, so the plate prints as a
        # wall standing on the bed with nothing left hanging. The valves' bottom ports and
        # the runs on them leave through the same channels the plate carries, run on down
        # to the foot's own bed edge. Inset one `wall` to the lip's own face — below the
        # rim that face is the bottom piece's lip, and the foot telescopes down it the way
        # every interior face does. The fore-facing tray's alone: under an aft-facing
        # plate the same band is the fold's own junction field, tees crossing every
        # section of it. The seats' wall-to-wall span stays above the rim
        # (`z-seam-under-deck`).
        foot_z0 = max(z0, inner[4])
        footed = sign < 0 and foot_z0 < mid_z - half - 1e-9
        if footed:
            lx0, lx1 = lip_face_x()
            tray = tray.fuse(_ybox(lx0, lx1, near, far, foot_z0, mid_z - half))
        if flank_bed_z is not None:
            tray = tray.cut(_front_top_flank_bedding_cut(
                inner, near - 1.0, far + 1.0, flank_bed_z))
        solid = solid.fuse(tray)
        turn = cq.Location(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0),
                           -90.0 if sign > 0 else 90.0)
        for sx, sz in seats:
            at = cq.Location(cq.Vector(sx, plane, sz))
            solid = solid.cut(_valve_tray.build_body_clearance().val().moved(turn).moved(at))
            for socket in _valve_socket_cutters(plane, sign, sx, sz):
                solid = solid.cut(socket)
            chan = (_valve_tray.height() if not footed else max(
                _valve_tray.height(), 2.0 * (sz - foot_z0))) + 2.0 * wedge_depth
            solid = solid.cut(_valve_tray.build_port_channel(chan + 2.0)
                              .val().moved(turn).moved(at))
    return solid


def _flow_meter_anchors(solid, roots, station, y0, y1, z0, z1):
    """The flow meter's two anchors hung off the top wall, for the piece that owns the ceiling.

    `roots` IS THE PIECE'S OWN INTERIOR AND NOT THE BOX'S (`piece_root_faces`). The rib's two
    ends climb to the face it roots on and the zip tie's channel is the room left between them, so
    the plane handed in here is the one that piece actually presents.

    ONE PER ARM AND NONE OVER THE BODY. The round body reaches to within a hair of the top wall
    and the two collet barrels leave the best part of a centimetre under it, so the arms are the
    only part of this meter a printed feature can reach without the storey moving.

    THE SEAT IS A BORE AND NOT A V, because the thing it takes is round. Half a cylinder on the
    barrel's own axis, `seat_r` across, so the seat and the barrel share a surface all the way round
    instead of touching on two lines. It stops on the barrel's own axis plane — the widest the arc
    gets — and the rib carries `flow_meter_anchor_wall` past that, so each lip is a flat strip one wall
    across. Carried any further round, the arc would run out to nothing against the flank.

    THE ZIP TIE IS THE LOAD PATH. A bore that opens downward carries nothing, so the two ties here
    are not the ASSE anchor's ties: cut them and the meter comes out of its anchors. What is hanging is
    a purchased part of a few tens of grams on two nylon zip ties.

    Printed Z−-down the rib HANGS OFF THE TOP WALL and starts on its two lips — one
    `flow_meter_anchor_wall` strip either side of the bore, the anchor's whole length, with nothing
    under them. Everything over those lips is the arc closing inward on itself, so the hood
    carries its own crown and the lips are the only thing in it support has to reach."""
    if not station or z1 < roots[5] - 1e-6:
        return solid
    x_axis, z_axis, seat_r, bands = station
    reach = seat_r + flow_meter_anchor_wall
    for by0, by1 in bands:
        if not (y0 <= by0 and by1 <= y1):
            continue
        if by1 - by0 < flow_meter_anchor_len - 1e-6:
            raise ValueError(
                f"_flow_meter_anchors: the barrel leaves {by1 - by0:.2f} mm between the body's rim "
                f"and the collet's ring, and an anchor is {flow_meter_anchor_len:.2f} — one zip tie's "
                f"cavity with `tie_cav_wall` at each end of it. Either the band gives way "
                f"(`DIGITEN_BODY_CLEAR`, `DIGITEN_COLLET_FREE`) or the rib does.")
        mid = (by0 + by1) / 2.0
        sy0, sy1 = mid - flow_meter_anchor_len / 2.0, mid + flow_meter_anchor_len / 2.0
        z_crown = z_axis + seat_r + wall          # one `wall` over the bore's own crown
        if roots[5] - z_crown < tie_t + 1e-6:
            raise ValueError(
                f"_flow_meter_anchors: a `wall` off the bore's crown leaves {roots[5] - z_crown:.3f} "
                f"mm under the top wall's inner face, and the zip tie is {tie_t:.3g} thick. The "
                f"storey the meter stands on is what gives way here "
                f"(`enclosure_assembly.DECK_CEILING_CLEAR`), not the wall.")
        # THE CAVITY IS WHAT IS NEVER FUSED, and nothing is cut for it. The rib is ONE box its whole
        # length up to `z_crown`, the two ends carried on up to the top wall, and ONE bore through
        # all of it. What the ends do not span IS the zip tie's channel — so it has no floor to draw,
        # no cut to make it, and no face for either to graze.
        #
        # The lower box runs the rib's whole length so the seat's own lip is ONE edge, and the rib
        # is UNIFIED before it joins the piece. A fuse imprints the seam of every solid that went
        # into it, so a rib fused straight onto the wall carries its lip in as many pieces as it
        # was laid down in — three here — and its bore in as many again.
        cy0, cy1 = mid - tie_cav_w / 2.0, mid + tie_cav_w / 2.0
        rib = _ybox(x_axis - reach, x_axis + reach, sy0, sy1, z_axis, z_crown)
        for ry0, ry1 in ((sy0, cy0), (cy1, sy1)):
            rib = rib.fuse(_ybox(x_axis - reach, x_axis + reach, ry0, ry1, z_crown, roots[5]))
        rib = rib.cut(_digiten_bore(x_axis, z_axis, seat_r, sy0, sy1, reach))
        solid = solid.fuse(rib.clean() if hasattr(rib, "clean") else rib)
    return solid


# --- the tube anchors, one pattern wherever a wall can reach a run ----------
#
# THE SAME 120° V AGAIN, on the one body in this machine there are twenty of. A run is held at its
# two ends by the collets it is pushed into and by nothing between them, so what it does between
# them is sag — and a run that sags is not on the centreline `lines-clear` cleared. An anchor is a
# stop on that span: a seat the tube lies in, and a zip tie's cavity behind the seat, standing on
# whichever face of the box comes near enough to reach it.
#
# A ROUND SEAT ON A ROUND BODY. The section is struck in the anchor's own frame — `u` along the
# tube, `n` from the tube toward the face the rib roots on — and the seat is a bore concentric
# with the tube, half of one, taken from the crown round to the tube's own AXIS PLANE. Stopping
# there is what keeps the lip printable: an arc run past its widest point closes back on the tube
# and ends in a feather, and an arc stopped on the axis plane ends in a flat face one `wall` wide.
#
# EVERY WORKING SECTION IN IT IS ONE `wall`. The rib reaches `seat_r + wall` off the axis, so the
# lip is a wall-wide strip; the cavity's floor is the seat's own arc offset one `wall`, so the web
# is a half-annulus of that thickness at every station of it; and the zip tie gets one `wall` of
# depth over that floor. If the body stands further from its root face, the rest is solid backing
# into that face rather than a needlessly deep void hanging the seat from its two end webs.
#
# THESE PIECES ARE POPULATED INVERTED ON THE BENCH. A seat hanging off the top wall is an
# upward-opening cradle at the moment a tube is laid in it and its zip tie threaded.
#
# ITS LENGTH ALONG THE RUN IS ITS CAVITY'S, the bargain `flow_meter_anchor_len` strikes: one zip tie
# crosses one anchor, so the rib is that zip tie's cavity with `tie_cav_wall` of itself at each end.
tube_anchor_len = tie_cav_w + 2.0 * tie_cav_wall
# A 1 mm zip tie needs its own thickness plus routing air, not every millimetre between a small tube
# and a distant wall. One structural section leaves 2 mm beyond the zip tie and keeps a deep anchor
# boxed back into its root; shallower fitting anchors keep all the air they actually have.
tube_anchor_cavity_depth = wall
# Do not add a skin-thin backing merely to shave a fraction from an already compact channel.
# A capped channel must put at least the cavity's routing buffer back into the load path.
tube_anchor_backing_min = tie_cav_buffer
# A CORBEL IS A WEDGE THAT HAS TO FIT, and what it grows into is the band the box keeps clear
# against its own interior: `side_band_inset`, what a body on the floor stands off the wall where
# the seam's boss chain runs. A rib whose axis stands inside that band gets the whole wedge; a
# deeper one gets a truncated one, tapering out at the band's edge.
tube_anchor_corbel_reach = side_band_inset


def tube_anchor_tie_loop(seat_r: float) -> float:
    """The shortest zip tie that closes round a seated body and its rib together.

    A zip tie turns INSIDE the channel, so what it reaches round is the body with the rib's own
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


def _anchor_corbel(origin, u, n, length, a_hang, b_root, deep):
    """The 45 degree gusset under a rib's flank — `deep` under it at the root face, tapering to
    nothing `deep` off that face and standing nowhere past there.

    `a_hang` is the flank it stands under, and it grows outboard of that flank."""
    return (
        cq.Workplane(_anchor_plane(origin, u, n))
        .polyline([(a_hang, b_root - deep), (a_hang + math.copysign(deep, a_hang), b_root),
                   (a_hang, b_root)])
        .close()
        .extrude(length)
        .val()
    )


def _tube_anchors(solid, roots, lane, stations, y0, y1, z0, z1):
    """Every tube anchor whose whole rib this piece owns.

    A station carries the tube and only the tube — where its axis runs, which way it points, what
    it seats on — and the box carries the face. So an anchor moves when its run moves and stops
    where the wall stops. A piece that owns only part of a rib builds none of it, the way every
    other station on these walls behaves.

    AND THE FACE IS THE PIECE'S OWN (`piece_root_faces`), not the box's interior. A station is
    struck in the box's frame because that is the frame the run is in; the plane its rib STOPS on
    is whatever the piece carrying it presents, and on the two pieces with a grown flank those two
    stand three and six millimetres apart. Measured to the wrong one the channel below is drawn
    inside the wall's own stock, which is a rib with no cavity in it at all.

    AND WHERE THAT FACE LEAVES NO CHANNEL, THE WALL GIVES THE RIB ITS LANE BACK. `lane` is the
    box's own interior — one `wall` inside the exterior, the plane every station was struck
    against — and a piece carrying stock inboard of it carries stock the rib was drawn to use. So
    that piece gives it up and the rib roots on `lane` instead, which is `front_top_flank_relief`'s
    bargain read off the station rather than stated: the wall keeps its full section everywhere the
    rib does not need it, and one `wall` stands behind the relief because `lane` is one `wall` in.

    THE RELIEF IS WIDER THAN THE RIB OVER THE TIE BAND ALONE, and there by the zip tie. What the
    loop runs down is the rib's two FLANKS, from the channel's floor to the tube's own axis plane
    (`tube_anchor_tie_loop`), so a relief cut to the rib's own reach would hand the zip tie a
    channel it could not leave. Over the cavity's own `tie_cav_w` it is carried
    `tie_t + tie_cav_buffer` past each flank instead — the same room over the zip tie every cavity
    on this box carries — and those two lobes are what the loop comes down. The rib's two
    `tie_cav_wall` ends take the rib's own reach, which the rib fills back: the wall keeps its
    full section everywhere the zip tie never arrives.

    THE CAVITY IS A REMAINDER: the rib stands one `wall` over the bore's crown down its whole
    length and its two `tie_cav_wall` ends carry on to the face it roots on. The `tie_cav_w`
    between them is the tie band, the one band the relief takes wide, and there the zip tie keeps
    at most `tube_anchor_cavity_depth` once there is enough excess reach to add substantial
    backing; that excess is filled from the root face. The crown is therefore always its floor and
    either the root face or that backing is its roof — neither is cut, so there is no cutter face
    to graze the opening.

    A FLANK THAT LOOKS DOWN CARRIES A CORBEL — a 45 degree wedge rooted on the same face the rib
    is, growing off that face into `tube_anchor_corbel_reach`. A rib whose axis stands inside that
    band is a triangle, `b_root` deep at the root face and nothing at the tube's axis plane; a
    deeper one is a truncated wedge, out to the band's edge and no further, and the deep end of
    its flank keeps its flat. Which flank hangs comes off the profile's own `a` axis read in the
    box's frame, so a rib rooted on the floor or the ceiling, or with its tube running along the
    build axis, has neither flank down and takes none. It stands over the same two `tie_cav_wall`
    ends and stops at the tie band, because the tie comes down that flank to the axis plane over
    `tie_cav_w` and a corbel there is the one path it has closed. The band of flank between the
    two corbels bridges.

    THE ZIP TIE CLOSES ROUND THE TUBE AND THE RIB'S OWN BACK TOGETHER: through the cavity, out one
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
        sign = 1.0 if face % 2 else -1.0
        b_face = (roots[face] - mid[face // 2]) * sign      # the face this piece presents
        b_lane = (lane[face] - mid[face // 2]) * sign       # and the box's own, at or outboard of it
        reach = seat_r + wall              # the lip's outer edge
        b_crown = seat_r + wall            # one `wall` over the bore's own crown
        b_root, relief = b_face, b_face < b_lane - 1e-9 and b_face - b_crown < tie_t
        if relief:
            b_root = b_lane                # the wall gives this rib its lane back
        if b_root - b_crown < tie_t:
            raise ValueError(
                f"_tube_anchors: a `wall` off the bore's crown leaves {b_root - b_crown:.3f} mm "
                f"under the face this rib roots on, and the zip tie is {tie_t:.3g} thick. What "
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
        # ONE bore through all of it. In the central zip tie band, material comes back from a remote
        # root until only `tube_anchor_cavity_depth` remains, provided that backing itself is at
        # least `tube_anchor_backing_min`. That boxes a small tube's long rib into the wall without
        # changing either threading mouth or putting a fragile skin against them.
        #
        # The lower box runs the rib's whole length so the seat's own lip is ONE edge, and the rib
        # is UNIFIED before it joins the piece. A fuse imprints the seam of every solid that went
        # into it, so a rib fused straight onto the wall carries its lip in as many pieces as it
        # was laid down in — three here — and its bore in as many again.
        band = tuple(origin[k] + u[k] * tie_cav_wall for k in range(3))
        # The flank that looks down — None where the profile's `a` axis is level — and how far
        # off the root face its corbel grows: to the band's edge or the axis plane, whichever it
        # arrives at first.
        a_hang = None if abs(t[2]) < 1e-9 else math.copysign(reach, -t[2])
        corbel = min(b_root, b_root - b_lane + tube_anchor_corbel_reach)
        if relief:
            # THE RELIEF, cut before the rib is fused so the rib is what fills it. Its floor is
            # `lane`, so what stands behind it is the one `wall` this box carries everywhere. The
            # rib's own reach runs the whole length; the two lobes the zip tie comes down are the
            # tie band's, and the wall keeps its full section at the rib's two ends.
            solid = solid.cut(_anchor_rib(origin, u, n, tube_anchor_len,
                                          reach, b_face, b_lane))
            solid = solid.cut(_anchor_rib(band, u, n, tie_cav_w,
                                          reach + tie_t + tie_cav_buffer, b_face, b_lane))
        rib = _anchor_rib(origin, u, n, tube_anchor_len, reach, 0.0, b_crown)
        for s0, s1 in ((0.0, tie_cav_wall), (tie_cav_wall + tie_cav_w, tube_anchor_len)):
            end = tuple(origin[k] + u[k] * s0 for k in range(3))
            rib = rib.fuse(_anchor_rib(end, u, n, s1 - s0, reach, b_crown, b_root))
            if a_hang is not None and corbel > 1e-9:
                rib = rib.fuse(_anchor_corbel(end, u, n, s1 - s0, a_hang, b_root, corbel))
        if b_root - b_crown >= tube_anchor_cavity_depth + tube_anchor_backing_min:
            rib = rib.fuse(_anchor_rib(
                band, u, n, tie_cav_w, reach,
                b_crown + tube_anchor_cavity_depth, b_root))
        rib = rib.cut(_anchor_bore(origin, u, seat_r, tube_anchor_len))
        solid = solid.fuse(rib.clean() if hasattr(rib, "clean") else rib)
    return solid


def _c14_aperture(stations, ports):
    """The rounded rectangle the C14's shroud reaches out through, picked out of a wall's own
    port list by the two heat-set stations that straddle it — `(x, z, across_x, across_z, r)`.

    THE HOLE AND THE STATIONS ARE ONE PLACEMENT: `enclosure_assembly.c14_cutout` and
    `enclosure_assembly.c14_stations` are both struck on `C14_STATION`, and both screws sit ON
    the mating axis, so the aperture is the rect port standing midway between them. A tunnel
    built round a hole that is not cut is a plug, and this is where that reads."""
    (x0, z0), (x1, z1) = stations[0], stations[-1]
    cx, cz = (x0 + x1) / 2.0, (z0 + z1) / 2.0
    for kind, hx, hz, *size in ports:
        if kind == "rect" and abs(hx - cx) < 1e-6 and abs(hz - cz) < 1e-6:
            wx, wz, *radius = size
            return cx, cz, wx, wz, (radius[0] if radius else 0.0)
    raise ValueError(
        f"the C14's two stations straddle (x {cx:.4g}, z {cz:.4g}) and this wall's port list "
        f"carries no rounded rectangle there. A tunnel built round a hole that is not cut is a "
        f"plug, so the pack states one or the other and not both halves of a placement.")


def _c14_tunnel_geometry(inner, outer, stations, ports, z0, z1):
    """The C14 tunnel's material and cutters — for the stations in `z0..z1`.

    THE RECEPTACLE DOES NOT BEAR ON THIS WALL. It bears on the tunnel's FORE face, one
    `c14_tunnel_len` inboard of the wall, and the customer's cord reaches it down a bore that is
    the aperture itself and nothing else: the tunnel grows entirely OUTWARD of the hole, so
    neither its section nor its two bores ever stand in the plug's way.

    AND IT DROPS INTO A PROFILED COLLAR ON THAT FACE. The collar's pocket is the purchased
    flange's exact rounded/tapered profile at `c14_collar_slip`; its outer profile is another
    `c14_collar_wall` beyond that everywhere in XZ. It wraps the flange's whole thickness and
    continues `c14_collar_extension` further inboard. A sheared copy of that outer profile spans
    from the open mouth to the wall: both end ears therefore root in the unrelieved wall outside
    the wall relief, while that relief stops `c14_wall_relief_overlap` inside each side of the
    rounded tunnel so the two are fused stock rather than tangent shells. The pocket stops at the
    fore face — the plane the flange bears on does not move, and neither does either insert.

    THE SEATING FACE HAS A STRAIGHT BACKING TO THE WALL. The same outer profile runs unsheared
    from `fore` to `aft`, filling the space above the print corbel at this short joint. The C14
    bore and both insert sockets are applied after the fuse, so each functional opening wins
    wherever these simple solids meet.

    THE INSERTS ENTER THE FORE FACE, from inside the machine like every other insert on this box,
    and bottom on the wall's own inner face. The station is relieved back to `wall`
    (`back_top_wall_reliefs`), so what stands over each blind end is `socket_cap` of wall and the
    tunnel is the whole of what is left.

    THE FLANGE POCKET CONTINUES THROUGH THE +X STRIP IN Y-. Its exact slipped outline runs
    `c14_insertion_relief` past the collar-mouth overcut, so the purchased two-ear flange has a
    straight approach before it reaches the printed collar. The exterior seating plane, tunnel
    bore and surrounding crown do not move.

    ITS UNDERSIDE RISES AT 45° INSTEAD OF HANGING. This piece prints on its Z− face with the +Y
    wall standing on the bed. `_y_wall_corbel` shears each outline that it carries: the tunnel's
    R3 rectangle from its fore face to the wall, and the collar's exact rounded/tapered profile
    over the whole 10.25 mm from its open mouth to the wall. The first leaves no square ledge or
    air channel under either rounded tunnel corner; the second puts material directly under the
    flange surround and carries both of its wider ends into the existing wall. The crown needs
    no such thing — it is clipped to the room, so above the aperture the section runs out into
    the top wall the way the port field's top row of bosses does.

    IT ROOTS ON `back_wall_t_at` AND NOT ON `inner`. The piece holding these stations carries
    `back_top_wall_t` over most of this wall, so the plane the tunnel stands on is the section
    read at the aperture — a tunnel rooted on the box's own rear plane would start a section
    inside a wall that is thicker than that plane anywhere the relief does not reach."""
    if not stations or not all(z0 <= sz <= z1 for _sx, sz in stations):
        return None
    cx, cz, wx, wz, r = _c14_aperture(stations, ports)
    cap = back_wall_t_at(cx, cz)
    if abs(cap - socket_cap) > stated_bound_tol:
        raise ValueError(
            f"the C14's aperture passes {cap:.2f} mm of wall and the cap over an insert's blind "
            f"end is {socket_cap:g}. The tunnel runs one `heatset_depth` off that wall, so at "
            f"any other section it holds either half an insert or a cap and half a tunnel.")
    for sx, sz in stations:
        if abs(back_wall_t_at(sx, sz) - cap) > stated_bound_tol:
            raise ValueError(
                f"the C14's station at (x {sx:.4g}, z {sz:.4g}) stands on "
                f"{back_wall_t_at(sx, sz):.2f} mm of wall and the aperture it straddles on "
                f"{cap:.2f} — one relief no longer covers this tunnel's fastening field, so an "
                f"insert would bottom on a plane the tunnel does not root on.")
    aft = outer[3] - cap
    fore = aft - c14_tunnel_len
    mouth = fore - _c14.FLANGE_T - c14_collar_extension
    hx, hz = c14_mount_half(wx, wz, max(abs(sx - cx) for sx, _sz in stations))
    tunnel = _rect_cut_y(cx, cz, 2.0 * hx, 2.0 * hz, c14_tunnel_r, fore, aft)
    tunnel = tunnel.fuse(_y_wall_corbel(tunnel, fore, aft)).clean()
    collar_outer = c14_collar_slip + c14_collar_wall
    collar = (_c14.flange_prism(
        collar_outer, mouth, fore)
        .translate((cx, 0.0, cz)).val())
    collar_corbel = (_c14.flange_prism(
        collar_outer, mouth, aft)
        .translate((cx, 0.0, cz)).val())
    collar_corbel = _y_wall_corbel(collar_corbel, mouth, aft)
    collar_backing = (_c14.flange_prism(collar_outer, fore, aft)
                      .translate((cx, 0.0, cz)).val())
    feature = tunnel.fuse(collar).fuse(collar_corbel).fuse(collar_backing).clean().intersect(
        _ybox(inner[0], inner[1], mouth, aft, inner[4], inner[5]))
    # The original cord bore continues through the wall and tunnel. The exact flange pocket
    # opens through the collar and continues inboard through the +X strip for assembly access;
    # its stopped +Y end is still the face the flange bears on.
    flange_pocket = (_c14.flange_prism(
        c14_collar_slip,
        mouth - c14_pocket_overcut - c14_insertion_relief,
        fore)
                      .translate((cx, 0.0, cz)).val())
    bore = _rect_cut_y(cx, cz, wx, wz, r, fore, outer[3] + 1.0).fuse(
        flange_pocket)
    inserts = tuple(_ycyl(heatset_dia / 2.0, sx, sz, fore, fore + heatset_depth)
                    for sx, sz in stations)
    return feature, bore, inserts, collar_backing


def c14_ceiling_land(inner, outer, stations, ports, stock):
    """The fixed C14 surround that reaches the ceiling panel's underside.

    The tunnel and collar are one back-top feature all the way to the interior-ceiling plane.
    This is the part of that opened feature which enters a moving ceiling envelope. The panel
    removes its matching aft-open pocket, leaving the show skin above this land and carrying no
    fragment of the inlet surround itself."""
    geometry = _c14_tunnel_geometry(inner, outer, stations, ports, inner[4], outer[5])
    if geometry is None:
        return None
    feature, bore, inserts, _backing = geometry
    land = feature.cut(bore)
    for cutter in inserts:
        land = land.cut(cutter)
    return land.intersect(stock)


def c14_ceiling_pocket(inner, outer, stations, ports, stock):
    """The aft-open underside pocket by which the ceiling slides over the fixed C14 surround.

    Its XZ section contains the tunnel and exact flange-collar outlines with one running-fit
    clearance. Carrying that section unchanged to the panel's aft edge makes the pocket open in
    the insertion direction: before the surround enters it, the surround is behind the panel;
    after it enters, every remaining millimetre of travel stays inside the same section. The
    cutter stops on the interior-ceiling plane, so the complete 3 mm show skin remains and rests
    directly on the surround's crown at the installed pose."""
    geometry = _c14_tunnel_geometry(inner, outer, stations, ports, inner[4], outer[5])
    if geometry is None:
        return None
    feature, bore, inserts, _backing = geometry
    opened = feature.cut(bore)
    for cutter in inserts:
        opened = opened.cut(cutter)

    cx, cz, wx, wz, _r = _c14_aperture(stations, ports)
    cap = back_wall_t_at(cx, cz)
    aft = outer[3] - cap
    fore = aft - c14_tunnel_len
    mouth = fore - _c14.FLANGE_T - c14_collar_extension
    hx, hz = c14_mount_half(wx, wz, max(abs(sx - cx) for sx, _sz in stations))
    slip = fits.slip
    y1 = stock.BoundingBox().ymax + 1.0
    tunnel_room = _rect_cut_y(
        cx, cz, 2.0 * (hx + slip), 2.0 * (hz + slip), c14_tunnel_r + slip,
        mouth - slip, y1)
    collar_room = (_c14.flange_prism(
        c14_collar_slip + c14_collar_wall + slip, mouth - slip, y1)
        .translate((cx, 0.0, cz)).val())
    b = stock.BoundingBox()
    under_skin = _ybox(
        b.xmin - 1.0, b.xmax + 1.0, mouth - slip, y1,
        b.zmin - 1.0, inner[5])
    # Include the exact opened feature as well as its running-fit envelope. The explicit union
    # makes a future profile change fail open into the pocket rather than leave coincident
    # printed material simply because the clearance reconstruction was not changed with it.
    # Do not clip this cutter back to `stock`: its extra millimetre past `stock.ymax` is what
    # makes the aft mouth an overcut instead of a coincident-face boolean at the panel edge.
    return tunnel_room.fuse(collar_room).fuse(opened).intersect(under_skin)


def _keystone_receptacle_geometry(inner, outer, station, z0, z1):
    """The keystone receptacle's fixed material and cutter.

    The pocket needs the full module-standard height. Its printed surround is clipped to the
    interior-ceiling plane if a station ever carries it that high; `keystone_ceiling_land` and
    `keystone_ceiling_pocket` then give the sliding panel a matching aft-open running clearance.
    At a lower station the clip is inert and the whole receptacle remains in this fixed wall.

    Returns ``(feature, cutter, catches)``. The cutter is kept separate because it has to pass
    through both the additive boss and the wall already present in the piece; the catches are
    kept separate because they are fused only after that cut."""
    if station is None:
        return None
    x, z = station
    if not z0 <= z <= z1:
        return None
    y_face = outer[3]
    block, catches = _keystone.receptacle_boss(x, z, y_face, y_face - back_wall_t_at(x, z))
    feature = block
    if block is not None:
        b = block.BoundingBox()
        feature = feature.fuse(_yz_prism(
            b.xmin, b.xmax,
            [(b.ymax, b.zmin), (b.ymin, b.zmin),
             (b.ymax, b.zmin - (b.ymax - b.ymin))]))
        below_ceiling = _ybox(
            outer[0] - 1.0, outer[1] + 1.0,
            outer[2] - 1.0, outer[3] + 1.0,
            outer[4] - 1.0, inner[5])
        feature = feature.intersect(below_ceiling)
        if catches is not None:
            catches = catches.intersect(below_ceiling)
    cutter, _bands = _keystone.receptacle_cut(x, z, y_face)
    return feature, cutter, catches


def keystone_ceiling_land(inner, outer, station, stock):
    """Fixed opened keystone material which reaches the ceiling panel's underside."""
    geometry = _keystone_receptacle_geometry(
        inner, outer, station, inner[4], outer[5])
    if geometry is None:
        return None
    feature, cutter, catches = geometry
    opened = None if feature is None else feature.cut(cutter)
    if catches is not None:
        opened = catches if opened is None else opened.fuse(catches)
    return None if opened is None else opened.intersect(stock)


def keystone_ceiling_pocket(inner, outer, station, stock):
    """The aft-open running-clearance pocket around the fixed keystone receptacle.

    The boss is rectangular where it crosses the ceiling field. Carrying that XZ section from
    one printed-fit clearance ahead of its fore face through the panel's aft edge lets the panel
    slide over it while leaving the complete 3 mm show skin above the interior-ceiling plane."""
    land = keystone_ceiling_land(inner, outer, station, stock)
    if land is None or land.Volume() <= 1e-6:
        return None
    b, s = land.BoundingBox(), stock.BoundingBox()
    slip = fits.slip
    # Keep the aft millimetre as real cutter, rather than intersecting it back to the panel's
    # bounding box and relying on coincident faces to open the mouth.
    return _ybox(
        b.xmin - slip, b.xmax + slip,
        b.ymin - slip, s.ymax + 1.0,
        s.zmin - 1.0, inner[5])


def _keystone_receptacle(solid, inner, outer, station, z0, z1):
    """Fuse the keystone's receptacle to its back-wall piece and open it.

    A KEYSTONE IS HELD BY A RECEPTACLE AND NOT BY A HOLE. `riteav_keystone` states the whole of
    it — an aperture at the show face, a lip behind it, a pocket taller than the aperture, an
    ease over the aperture's top edge the body swings through, and two catches at the pocket's
    back the tang and the latch snap over. This wall gives the lip its depth out of its own
    section, and a boss standing inboard gives the rest.

    THE BOSS IS FUSED, THEN THE POCKET IS CUT, THEN THE CATCHES ARE FUSED BACK. The catches
    stand inside the pocket, and a cut running after them would take them off again.

    AND THE BOSS STANDS ON A 45° WEB, the same one a port chip's boss and a +X mounting boss
    stand on. This piece prints on its Z− face with the +Y wall on the bed, so the block's own
    underside is its reach off that wall of ceiling starting in air; the web is that reach taken
    back down to the wall at `relief_chamfer`. ITS FIGURE IS THE BLOCK'S OWN BOX — the wall face
    it roots on, the free face it ends at, and the soffit between them."""
    geometry = _keystone_receptacle_geometry(inner, outer, station, z0, z1)
    if geometry is None:
        return solid
    feature, cutter, catches = geometry
    if feature is not None:
        solid = solid.fuse(feature)
    solid = solid.cut(cutter)
    if catches is not None:
        solid = solid.fuse(catches)
    return solid


def _c14_tunnel(solid, inner, outer, stations, ports, z0, z1):
    """Fuse the complete C14 surround to its back-wall piece and open its bores."""
    geometry = _c14_tunnel_geometry(inner, outer, stations, ports, z0, z1)
    if geometry is None:
        return solid
    feature, bore, inserts, _backing = geometry
    # The collar, tunnel and crown are one fixed surround. The ceiling panel has an aft-opening
    # underside pocket around the part of this feature that reaches its structural field; its
    # uncut show skin lands on the crown at the installed pose.
    solid = solid.fuse(feature)
    # The bore, opened through everything standing round it. The wall's own cutters run to its
    # inner face and this one runs to the tunnel's, so the hole is one rectangle end to end.
    solid = solid.cut(bore)
    for cutter in inserts:
        solid = solid.cut(cutter)
    return solid


def _piece_bands(box, name):
    """The Y and Z bands one quadrant owns, as `(y0, y1, z0, z1)` — what every station is tested
    against before the piece grows or cuts it. Each band runs a millimetre past the shell at its
    outer end and stops on the seam at its inner one, so a station on a seam plane belongs to
    exactly one piece."""
    y_side, z_side = name.split("-")
    zj = box.splits[0] if y_side == "front" else box.splits[1]
    y0, y1 = ((box.outer[2] - 1.0, box.y_joint) if y_side == "front"
              else (box.y_joint, box.outer[3] + 1.0))
    z0, z1 = ((box.outer[4] - 1.0, zj) if z_side == "bottom"
              else (zj, box.outer[5] + 1.0))
    return y0, y1, z0, z1


def build_piece(box, y_side, z_side, halves_cache=None):
    """One of the four printable pieces: the full front/back column split at
    its seam (`box.splits` — the one stated plane, both columns), the bottom
    taking the Z lip, the hooked rails, the stop blocks and the corner fills, the
    top taking the foot slabs, the channel and the corner reliefs. The Y-seam
    bosses' under-seam level sits under that plane, so it lands in — and pins —
    the two bottom pieces; the over-rim level the two tops."""
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
    plate = box.pack.collet_plate if (box.pump_bay and box.pack.collet_plate) else None
    if z_side == "bottom":
        piece = solid.intersect(_ybox(ox0 - 1.0, ox1 + 1.0, oy0 - 1.0, oy1 + 1.0,
                                      oz0 - 1.0, zj))
        col = _ybox(ox0 - 1.0, ox1 + 1.0,
                    oy0 - 1.0 if y_side == "front" else y_joint,
                    y_joint if y_side == "front" else oy1 + 1.0,
                    oz0 - 1.0, oz1 + 1.0)
        # The wall that carries the seam's furniture down to the slab, so a head stands
        # on a wall and not in air. Fused before every pocket, so a well or a groove cut
        # into this flank later is cut out of the whole `2 * wall` of it.
        piece = piece.fuse(_lip_underwall(inner, y_joint, zj).intersect(col))
        if y_side == "front":
            # And front-bottom's own extra section on the west flank, welled round the card.
            piece = piece.fuse(_front_bottom_flank_skin(
                inner, box.pack.west_cradle, y_joint, zj).intersect(col))
            # And the two shelves that carry the collet plate, which bring that same face in
            # the last millimetre under the steel's ends. Fused with the skin, before every
            # pocket, so anything cut into this flank later is cut out of the whole of it.
            if box.pump_bay and box.pack.collet_plate:
                piece = piece.fuse(
                    _plate_shelf(inner, box.pack.collet_plate, zj).intersect(col))
        if y_side == "back":
            # And back-bottom's own extra section inboard of that, on the two flanks only.
            # Fused with them and before every pocket for the same reason: a well cut into
            # this flank later is cut out of the whole `back_bottom_flank_t` of it.
            piece = piece.fuse(_back_bottom_flank_skin(inner, y_joint, zj).intersect(col))
        if y_side == "front" and box.pump_bay:
            # The front flat's share of both skins goes to the bay's floor and the heads
            # that pass through its berth; the flat sill is front-top's.
            piece = piece.cut(_front_flat_lip_drop(inner, zj))
            # And both flanks over the same run, round the corners to the tee wall's aft
            # face — the rail starts on that face and nothing crosses the seam fore of it.
            piece = piece.cut(_flank_lip_drop(inner, box.pack.collet_plate, y_joint, zj))
        # The rail heads and their stop blocks — the whole of what stands proud of this
        # piece's mouth, what the top's channel swallows on the way in and its return
        # rides at home.
        piece = piece.fuse(_z_rail_heads(inner, y_joint, zj, y_side, plate,
                                         box.pack.vent_chase))
    else:
        piece = solid.intersect(_ybox(ox0 - 1.0, ox1 + 1.0, oy0 - 1.0, oy1 + 1.0,
                                      zj, oz1 + 1.0))
        # FRONT-TOP'S OWN ±X SECTION, first of everything this piece does to its flanks. The
        # wells, the trays and every bore below are struck on `interior_x` and cut AFTER this,
        # so each one is cut out of the whole section rather than out of the skin it replaced —
        # which is what leaves a lever nut bottoming exactly where it bottomed before.
        if y_side == "front" and box.pack.collet_plate:
            piece = piece.fuse(_front_top_flanks(inner, outer, box, y_joint, zj))
            # The Y tongue is part of these same two flanks. Its shoulder and slipped overlap
            # continue through the seam, but their bed-facing edge stays on the flank's one
            # established 45-degree plane; no separate strip or end cap hangs below it where
            # the Z-rail channel crosses the tongue.
            piece = piece.cut(_front_top_flank_bedding_cut(
                inner, y_joint - wall - 1.0, y_joint + lip_len + 1.0, zj))
        # AND BACK-TOP'S OWN, first of everything that piece does to its flanks, for the same
        # reason: the wells and the +X bosses below are struck on `interior_x` and cut after
        # this, so each is cut out of the whole section rather than out of the skin it replaced.
        if y_side == "back":
            piece = piece.fuse(_back_top_flanks(inner, outer, box, y_joint, zj))
        # The rails' foot slabs, one per flank — fused with the sections above, before
        # every pocket, and carved to the slide's own profile by the channel cut at the
        # END of this piece's work, so everything later fused near a flank is carved too.
        piece = piece.fuse(_z_rail_feet(inner, y_joint, zj, y_side, plate,
                                        box.pack.vent_chase))
        if y_side == "back":
            # BACK-TOP'S OWN +Y SECTION, first of everything this piece does to that wall — so
            # the port field, the C14's bores and the nameplate's seat are cut out of the
            # section rather than out of the skin it replaced.
            piece = piece.fuse(_back_top_wall(inner, outer, box, zj))
            # AND ITS CEILING, which is two corbelled side strips with the slide-in panel
            # between them. Here for the same reason the two sections above are: the ASSE anchor's V,
            # the chain's bores, the wells and every bore below are cut AFTER this, so each is
            # cut out of what the corbel left rather than filling a pocket back in.
            piece = _back_top_ceiling(piece, inner, y_joint, box)
    piece = piece.intersect(_rounded_outer(outer))
    # THE COLUMN RELIEFS' CEILINGS, ahead of every fuse this piece makes. The pockets are cut
    # last, where a relief has to be; the 45° walk their ceilings take into the column is cut
    # HERE, so a pocket the piece goes on to roof is roofed and one nothing stands over keeps
    # the walk (`_column_relief_rise`).
    for sx, sy, _name, room in box.column_reliefs:
        piece = piece.cut(_column_relief_rise(
            inner, sx, sy, room, box.splits[0] if sy < 0 else box.splits[1]))
    zlo, zhi = _piece_bands(box, f"{y_side}-{z_side}")[2:]
    if y_side == "back":
        rear = back_top_wall_face() if z_side == "top" else None
        # The port field, INSIDE the print silhouette: its pockets are cut into the wall's outer
        # face and its bosses stand off the inner one, so the face the customer meets is flush.
        # The bosses carry the face's own through-holes across their depth, so a bore that
        # crosses the wall crosses them too.
        piece = _port_field(piece, box.pack.port_field, box.pack.back_ports, outer, oy1, zlo, zhi,
                            None if rear is None else back_wall_t_at)
        # And the C14's tunnel, on whichever piece holds its two stations. Last on this wall
        # because its bore reaches further inboard than the field's own cutters do — those run
        # to the boss each stands behind, and this one runs the whole depth of the tunnel.
        piece = _c14_tunnel(piece, inner, outer, box.pack.c14, box.pack.back_ports, zlo, zhi)
        # And the keystone's receptacle, reaching further inboard again — the boss carrying the
        # pocket the jack snaps into stands past where the field's own bosses stop.
        piece = _keystone_receptacle(piece, inner, outer, box.pack.keystone, zlo, zhi)
    # The +X wall's mounting bosses, on whichever piece holds each one's station. Last of
    # all, so a bore is cut through every column that has already been fused around it.
    ylo, yhi = _piece_bands(box, f"{y_side}-{z_side}")[:2]
    piece = _east_bosses(piece, inner, outer, box.pack.east_bosses, ylo, yhi, zlo, zhi)
    # The +X wall's Wago wells, on whichever piece holds each one's station. After the
    # bosses for the same reason those go after the seam's own bosses: a pocket cut here is a
    # pocket nothing later fuses back in.
    piece = _side_wells(piece, inner, box.pack.side_wells, ylo, yhi, zlo, zhi)
    # The floor slab's, on whichever piece holds each one's plan station. Only the bottom
    # pieces have a slab to stand one on, and `_floor_bosses` drops any station outside.
    piece = _floor_bosses(piece, inner, box.pack.floor_bosses, ylo, yhi, zlo, zhi)
    # The −X wall's card slot, last of all: its bottom rail lands on the same slab those posts
    # rise from, so cutting its grooves after them is what keeps a groove a groove.
    piece = _west_cradle(piece, inner, box.pack.west_cradle, ylo, yhi, zlo, zhi)
    # The condenser block's four flanges, on the same slab and the walls either side of it: the
    # fore rails off the front wall, the aft fin off the +X one. After the floor's posts for the
    # card slot's own reason — a rail rooted on the slab is rooted on whatever is standing there.
    piece = _cond_cradle(piece, inner, box.pack.cond_cradle, ylo, yhi, zlo, zhi)
    piece = _cond_mount(piece, inner, box.pack.cond_mount, ylo, yhi, zlo, zhi)
    # The cold core's own two: the front corner blocks on the same slab those rails root on, and
    # the hold-down brackets a storey up on the +Y wall. The blocks carry a bore, so they go on
    # with the other pockets — after everything that could fuse material back into one.
    piece = _core_stops(piece, inner, box.pack.core_stops, ylo, yhi, zlo, zhi)
    piece = _core_holds(piece, inner, box.pack.core_holds, ylo, yhi, zlo, zhi,
                        back_top_wall_face() if (y_side, z_side) == ("back", "top") else None)
    # And the core's relief, which leaves it by a flank and needs somewhere to go: the rib is
    # fused before the channel is cut out of it, which is the same order the card slot takes.
    piece = _vent_chase(piece, inner, outer, box.pack.vent_chase, ylo, yhi, zlo, zhi)
    # And the tap-water chain's, on the same wall a storey up. After the tray's rails, whose
    # band it stands over, and last like every other pocket: its tie slots are cut out of the
    # ASSE anchor this fuses, so nothing may fuse into them afterwards.
    piece = _asse_cradle(piece, inner, box.pack.asse_cradle, ylo, yhi, zlo, zhi)
    # And the flow meter's two anchors off the same piece's ceiling — the stations `ceiling_stations`
    # leaves this piece, because back-top's ceiling over the panel's field is the PANEL and a rib
    # rooted there roots on it (`../ceiling-panel/ceiling_panel.py`).
    #
    # BOTH BUILDERS ROOT ON THIS PIECE'S OWN INTERIOR and not on the box's. A rib's cavity is the
    # room its two ends leave under the face it stops on, so the plane they are drawn to has to be
    # the plane this piece puts there (`piece_root_faces`).
    roots = piece_root_faces(inner, y_side, z_side)
    meter_anchors, ribs = ceiling_stations(box.pack.flow_meter_anchors, box.pack.tube_anchors, panel=False)
    piece = _flow_meter_anchors(piece, roots, meter_anchors, ylo, yhi, zlo, zhi)
    # And the flavour manifold's valve trays, on whichever piece owns each deck's band. A plate
    # wall to wall with its seats standing on it, so it goes on after the wells and the bosses
    # for the same reason they go after the seam's own bosses.
    # The wall the anchor tees stand in, behind the collet plate — BEFORE the valve trays,
    # because a tray's seats are cut out of whatever stands on that plane and this stands on it.
    if y_side == "front" and z_side == "top" and box.pump_bay and box.pack.collet_plate:
        piece = piece.fuse(_tee_wall(inner, y_joint, box.pack.collet_plate, box.pump_bay))
        # And the rib that stands on that wall's crown, carrying the ridge the display's
        # through-hole leaves across the housing's back. With the wall, because it stands on
        # it — and after the facet's own cuts, which the half took before it was split.
        piece = piece.fuse(_ridge_wall(inner, outer, box.pack.collet_plate, box.pump_bay))
    piece = _valve_trays(
        piece, inner, box.pack.valve_trays, ylo, yhi, zlo, zhi,
        wall_aft_y=(box.pack.collet_plate["wall_aft_y"] if box.pack.collet_plate else None),
        flank_bed_z=(zj if (y_side, z_side) == ("front", "top") else None),
    )
    # The pump cradle and clamp are removable; what this fixed piece carries for them is the
    # bay's floor and the seat the collet plate drops into, followed by the opening itself.
    if y_side == "front" and z_side == "top" and box.pump_bay and box.pack.collet_plate:
        piece = piece.fuse(_bay_floor(inner, y_joint, box.pack.collet_plate, box.pack.pump_trays))
    # And the runs' own anchors, on whichever face each one stands nearest. Last, for the same
    # reason the ASSE anchor is: every one of these is a rib with a cavity cut through it.
    piece = _tube_anchors(piece, roots, inner, ribs, ylo, yhi, zlo, zhi)
    # And the nameplate — the pocket on the +Y wall's outer face, the plateau that floors it on
    # the inner one, and the two screw bosses standing off that. LAST of this wall's work, like
    # every other pocket: it is cut a screw seat deep, which is deeper than the wall's own stock,
    # so anything fused onto this face afterwards would stand in the plate's own seat. The cold
    # core's aft bracket is the one that does — its leg climbs this face right through the
    # plate's lane, and cut here it roots on the pocket's floor with the plateau, one continuous
    # section, instead of poking through into the plate.
    if y_side == "back":
        piece = _nameplate(piece, box.pack.nameplate, outer, oy1, zlo, zhi)
    # And the flat ceiling's two strips over the funnel opening's flanks, on the front
    # top alone — the piece whose ceiling is nothing but those strips.
    if y_side == "front" and z_side == "top" and box.pack.funnel:
        piece = _ceiling_corbels(piece, inner, outer, box.pack.funnel, y_joint, box.y_bosses)
    # The bay's opening, after every fuse that stands near it: what leaves through it is
    # the pump cartridge, and what it takes from this piece is what `build_pump_cartridge` keeps.
    if y_side == "front" and z_side == "top" and box.pump_bay:
        piece = piece.cut(_bay_cut(inner, outer, box.pump_bay, box.pack.pump_trays,
                                   box.pack.collet_plate))
        # The plate's fore restraint must survive the release, so it belongs to front-top and
        # stands OUTSIDE the pump cartridge sweep. Fused after the opening and its sill are cut:
        # these cheeks intentionally stand at the opening's aft outer edges.
        piece = piece.fuse(_plate_fore_guides(
            inner, outer, box.pump_bay, box.pack.collet_plate, box.pack.pump_trays))
        # And the wall over the steel — the full-width land its top edge stops on and one
        # uninterrupted 45-degree underside above the loaded brackets.
        piece = piece.fuse(_plate_cap(
            inner, box.pack.collet_plate, box.pump_bay, box.pack.pump_trays))
    # And then the columns give up whatever the pack stands in them (`_column_relief`), which is
    # last of everything: a relief is air, and air a later step fuses back in is not a relief.
    # Clipped to the pillar — the column AND the lip's skin wrapping it (`_column_pillar`) —
    # so what a pocket can ever take is that and never the wall behind it or the boss beside it.
    # Their ceilings' 45° walk was first taken at the head of this piece's work. Take it again
    # here with the final pocket so a rail or boss fused since cannot put a flat roof back over
    # that air (`_column_relief_rise`).
    for sx, sy, _name, room in box.column_reliefs:
        piece = piece.cut(_column_relief(
            inner, sx, sy, room, box.splits[0] if sy < 0 else box.splits[1]))
        piece = piece.cut(_column_relief_rise(
            inner, sx, sy, room, box.splits[0] if sy < 0 else box.splits[1]))
    # And the condenser's two vents, which are the last cut this piece takes for the same reason
    # a relief is: they are air, and air a later step fuses back in is not a vent. What stops
    # each slot is read off the piece as it stands HERE — every rail, fin, pod, pocket and
    # relief on those two flanks already in it.
    piece = _flank_vents(piece, inner, outer, box.pack.cond_airway, ylo, yhi, zlo, zhi,
                         box.pack.west_cradle)
    if z_side == "top":
        # THE SLIDE'S OWN CARVING, after everything a top piece fuses. The channel is cut
        # through whatever now stands in the rail's lane — the foot slabs, the flank
        # sections, a valve tray's foot — so the section
        # the head sweeps is the section the piece actually presents, whatever later grew
        # there. The corner reliefs the same: the pillars stand off the band the bottom's
        # corner fills and flank rails sweep, and regrow on their 45° pair above it.
        piece = piece.cut(_z_rail_channels(inner, y_joint, zj, y_side, plate,
                                           box.pack.vent_chase))
    if y_side == "front":
        # AND THE Y TELESCOPE'S, on both storeys and for the same reason: the lip's own
        # section is the section this piece presents aft of the mouth, whatever has grown
        # into that band since the lip was drawn.
        piece = piece.cut(_y_lip_channel(inner, y_joint, box.y_bosses))
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
    for col, zj, crosses in zip(("front", "back"), box.splits, box.z_seam_passes):
        how = "runs through its column" if crosses else "in an open band"
        print(f"  Z seam {col + ':':7s} {zj:6.1f} mm  ({how}; the bed allows "
              f"{lo:.1f}..{hi:.1f})")


def _report_levels(box):
    """The Y-seam cross-pin heights each ±X wall ended up with. They are searched
    per wall against what stands against it, so the two can differ — printing
    them keeps a wall that had to give up a level visible instead of silent."""
    bosses = box.y_bosses
    for sx, label in ((+1.0, "−X"), (-1.0, "+X")):
        zs = sorted(z for _xi, _xe, s, z in bosses if s == sx)
        print(f"  Y-seam levels {label} wall: {len(zs)} — "
              + ", ".join(f"{z:.0f}" for z in zs))


def _report_slide(pieces, box):
    """Each column's slide, PROVED on the built pieces: the top swept from entry to home
    against its bottom piece, and lifted off its catch at home.

    THE SWEEP IS THE CLAIM. A slide the length of a column is clear only if every station
    of the travel is, so the top piece is intersected with its bottom at a ladder of
    displacements from full entry down to home, dense where the joint closes — contested
    volume at every rung is the reading and 0 is the only passing figure. LIFTED a
    millimetre off home, the hooks are what has to answer: the contested volume IS the
    catch engaging, and 0 there is a top that lifts straight off. Both go in `BOUNDS`,
    so the scorecard carries the slide the way it carries every other claim."""
    out = {}
    for col, names in (("front", ("front-top", "front-bottom")),
                       ("back", ("back-top", "back-bottom"))):
        if names[0] not in pieces or names[1] not in pieces:
            continue
        plate = box.pack.collet_plate if (box.pump_bay and box.pack.collet_plate) else None
        travel = _z_rail_travel(box.inner, box.y_joint, col, plate, box.pack.vent_chase)
        # AND IT ENTERS FROM THE SIDE THIS COLUMN ENTERS FROM. The two columns are mirrored,
        # so a displacement that is entry on one is a piece driven past home on the other.
        _runs = _z_rail_runs(box.inner, box.y_joint, col, plate, box.pack.vent_chase)
        dy = 1.0 if _runs[0][3] > _runs[0][2] else -1.0
        top, bot = pieces[names[0]].val(), pieces[names[1]].val()
        rungs = [d for d in (0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0) if d < travel]
        d = 24.0
        while d < travel:
            rungs.append(d)
            d += 16.0
        rungs.append(travel)
        worst = (0.0, 0.0)
        for d in rungs:
            v = top.translate(cq.Vector(0.0, -dy * d, 0.0)).intersect(bot).Volume()
            if v > worst[0]:
                worst = (v, d)
        clear = worst[0] <= 1.0
        record_bound(Bound(
            f"z-slide-{col}-clear",
            f"The {col} top slides its whole travel onto its bottom clear", clear,
            f"worst {worst[0]:.1f} mm³ contested, {worst[1]:.2f} mm out of home, "
            f"{len(rungs)} stations over {travel:.1f} mm",
            "0 mm³ at every station",
            ([] if clear else [
                f"the {col} column's slide is blocked {worst[1]:.2f} mm out of home — "
                f"{worst[0]:.1f} mm³ of the two pieces contest the lane. Something grew "
                f"into the channel after the rail was drawn; the channel cut runs last, "
                f"so look for material fused after it or a bottom-piece feature standing "
                f"proud of the mouth outside the lip's own runs"])))
        lift = top.translate(cq.Vector(0.0, 0.0, 1.0)).intersect(bot)
        lifted = lift.Volume()
        # AND IT IS READ ON EACH FLANK, because a column caught on one of them reads as a
        # column caught: the runs are down both ±X sides and one of them answering for the
        # whole seam is the reading a single figure cannot tell from two.
        ox0, ox1, oy0, oy1, oz0, oz1 = box.outer
        flanks = {
            side: lift.intersect(_ybox(fx0, fx1, oy0 - 1.0, oy1 + 1.0,
                                       oz0 - 1.0, oz1 + 1.0)).Volume()
            for side, (fx0, fx1) in (("west", (ox0 - 1.0, 0.0)), ("east", (0.0, ox1 + 1.0)))}
        least = min(flanks.values())
        caught = lifted > 5.0 and least > 5.0
        record_bound(Bound(
            f"z-slide-{col}-catch",
            f"The {col} top's rails catch it against a lift, on both flanks", caught,
            f"{lifted:.1f} mm³ engaged at a 1 mm lift — "
            f"{flanks['west']:.1f} west, {flanks['east']:.1f} east",
            "the hooks bearing down both flanks, so more than 5 mm³ on each",
            ([] if caught else [
                f"lifted 1 mm off home, the {col} top contests {flanks['west']:.1f} mm³ on "
                f"its west flank and {flanks['east']:.1f} mm³ on its east — a flank reading "
                f"nothing has no foot over its head, so that run is a rail the other piece "
                f"never entered. Read the channel cuts that run last on the top piece "
                f"(`_z_rail_channels`) against the runs `_z_rail_runs` "
                f"gives that flank, and `_rail_hook_lap` against both"])))
        foot_depths = [abs(_rail_foot_face(x_in, sx, col) - x_in)
                       for x_in, sx, _y0, _y1, _lane in _runs]
        rail_depths = [abs(_rail_x(x_in, sx, col)[3] - x_in)
                       for x_in, sx, _y0, _y1, _lane in _runs]
        catch_depths = [_rail_hook_lap(col) for _run in _runs]
        channel_skins = [
            wall + abs((_rail_x(x_in, sx, col)[0] - sx * slide_slip) - x_in)
            for x_in, sx, _y0, _y1, _lane in _runs]
        top_flank_t = front_top_flank_t if col == "front" else back_top_flank_t
        bottom_flank_t = front_bottom_flank_t if col == "front" else back_bottom_flank_t
        expected_lap = front_hook_lap if col == "front" else back_hook_lap
        nominal = top_flank_t - wall
        full_feet = (len(foot_depths) == 2
                     and all(abs(depth - nominal) <= stated_bound_tol
                             for depth in foot_depths)
                     and max(rail_depths) <= side_band_inset + stated_bound_tol)
        record_bound(Bound(
            f"z-slide-{col}-foot-section",
            f"Both {col}-top slide feet carry the nominal flank section to the seam",
            full_feet,
            f"{foot_depths[0]:.2f} mm west, {foot_depths[1]:.2f} mm east; "
            f"arm reaches {max(rail_depths):.2f} mm into a {side_band_inset:g} mm band",
            f"{nominal:.2f} mm inward of interior_x on both flanks, rail inside its band",
            ([] if full_feet else [
                f"the {col} feet reach {foot_depths}, but a {top_flank_t:g} mm wall needs "
                f"{nominal:.2f} mm past `interior_x`. Carry the nominal wall section to "
                f"the foot's face and place the hook and arm at its inboard edge"])))
        full_catches = (
            len(catch_depths) == 2
            and all(abs(depth - expected_lap) <= stated_bound_tol
                    for depth in catch_depths)
            and min(channel_skins) >= wall - stated_bound_tol)
        record_bound(Bound(
            f"z-slide-{col}-catch-section",
            f"Both {col}-bottom heads spend the grown flank section on their catches",
            full_catches,
            f"{catch_depths[0]:.2f} mm west, {catch_depths[1]:.2f} mm east; "
            f"least outer skin {min(channel_skins):.2f} mm",
            f"{expected_lap:.2f} mm overlap on both flanks and at least "
            f"{wall:.2f} mm outside the channel",
            ([] if full_catches else [
                f"the {col} catches reach {catch_depths} and leave outer skins "
                f"{channel_skins}. Carry the {bottom_flank_t - 2.0 * wall:.2f} mm grown "
                f"past the lip wall into the hook while keeping one full wall outside "
                f"its channel"])))
        out[col] = (worst, travel, len(rungs), lifted)
        print(f"  Z slide {col + ':':7s} travel {travel:6.1f} mm, worst contested "
              f"{worst[0]:6.1f} mm³ at {worst[1]:.2f} mm out; catch {lifted:8.1f} mm³ "
              f"at a 1 mm lift")
    return out


def build_pieces(box):
    """The printable pieces of one box — the four quadrants and, when the pack stands
    pumps, the pump cartridge that slides out of the front pair — and the assembly of them in
    place with the seams intact.

    DRAWING A PIECE TAKES NO READING. Every bound the box states is in the ledger before this
    runs — `_dims` states its own as it sizes the shells, `with_funnel` states the throat's as
    it seats the centre — so the four pieces are a pure function of the Box and a piece handed
    back unbuilt is a piece nothing on the card was waiting for. That is what lets `_realized`
    keep them: a build that moves a body inside the walls moves neither the box, which is its
    stated size, nor the code that cuts it, and a station moves only when the body carrying it
    does."""
    _last_box[0] = box
    cache = {}

    def _product(n):
        if n == "pump-cartridge":
            return build_pump_cartridge(box, halves_cache=cache)
        if n == "pump-cap":
            return build_pump_cap(box, halves_cache=cache)
        return build_piece(box, *n.split("-"), halves_cache=cache)

    names = [n for n in PIECE_COLORS
             if n not in ("pump-cartridge", "pump-cap")
             or (box.pump_bay and box.pack.collet_plate)]
    pieces = {name: _realized.realized(
                  _realized.key(__name__, box, name),
                  lambda n=name: _product(n))
              for name in names}
    assy = cq.Assembly(name="enclosure")
    for name, piece in pieces.items():
        assy.add(piece, name=f"enclosure-{name}".replace("-", "_"),
                 color=PIECE_COLORS[name])
    return pieces, assy


# HOW FINELY A PIECE IS TESSELLATED FOR THE BED. The show surface is fluted now, so the mesh a
# slicer reads has to hold a curve the nozzle can draw: the deviation allowed is a fraction of
# the 0.42 mm bead, and the angle is tight enough that a groove's own arc does not come back as
# a few flats. It costs file size and nothing else — a slicer reads the triangles once.
piece_mesh_tol = 0.02
piece_mesh_angle = 0.15


# The box the pieces were last drawn from, so `_export_pieces` can strike the flute field on the
# same rails they were clipped to without being handed it through three call sites.
_last_box = [None]


def _piece_mesh(solid):
    """One solid as the mesh that goes to a bed.

    TESSELLATED, NOT ROUND-TRIPPED THROUGH STL. An STL is a triangle soup with no shared
    vertices, and what comes back from re-merging one is a surface with edges that hold one
    face where they should hold two — which a mesh boolean rightly refuses to treat as a
    volume. `tessellate` hands back the indices directly."""
    points, tris = solid.tessellate(piece_mesh_tol, piece_mesh_angle)
    mesh = trimesh.Trimesh(vertices=[(p.x, p.y, p.z) for p in points],
                           faces=tris, process=True)
    mesh.merge_vertices()
    return mesh


def _collet_plate_body(plate):
    """The steel that stands in front of the tee wall, as the outline its own spec strikes.

    IT IS THE ONE BODY IN THE BAY'S STOREY THIS MODULE DOES NOT PRINT — the plate is cut from
    sheet (`enclosure_assembly.build_collet_plate`) — and the storey's run of flutes has to
    know it stands there, because the wall behind it is a bearing face and not a show face."""
    return _xz_prism(plate["fore_y"], plate["aft_y"], plate_outline(plate))


def _export_pieces(pieces, assy):
    refused = []
    box = _last_box[0]
    outer = box.outer
    # EVERY BODY THE ASSEMBLY STANDS, MESHED ONCE. A piece is cut against the rails; the rest
    # of them are what stands berthed in the room a rail runs round, and the steel is the one
    # that is not a piece.
    bodies = {name: _piece_mesh(piece.val()) for name, piece in pieces.items()}
    steel = ([_piece_mesh(_collet_plate_body(box.pack.collet_plate))]
             if box.pack.collet_plate else [])
    for name, piece in pieces.items():
        export_assembly(one_body(piece, f"enclosure-{name}", PIECE_COLORS[name]),
                        str(_here.parent / f"enclosure-{name}.step"))
        print(f"-> enclosure-{name}.step")
        # AND THE SHOW SURFACES ARE FLUTED HERE, in the mesh, on the way to the bed. See
        # `flute_skin.py` for why they are not in the solid.
        berthed = [m for other, m in bodies.items() if other != name] + steel
        rails = flute_rails(box, berthed)
        # The top clamp is an interior mechanical part and carries no show field. The
        # full-width cradle owns the translated front face and both outer flanks: its proud
        # rail carries the face and front corners, while the enclosure-phase side rail starts
        # only at their old tangencies. No rail is struck on the fixed front plane inside it.
        if name == "pump-cap":
            rails = []
        elif name == "pump-cartridge":
            rails = [_pump_cartridge_side_flute_rail(outer),
                     _pump_cartridge_front_flute_rail(outer)]
        mesh = _flute_skin.flute(bodies[name], rails,
                                 flute_pitch(outer), flute_depth, flute_rise)
        # WHAT IS CHECKED IS WHAT COMES OUT. A piece tessellates with a handful of edges
        # carrying four faces rather than two — the solid touching itself along a line, which is
        # a fact about the solid — and refusing the cut for it would refuse every piece. The
        # engine takes that and repairs it; a mesh that is still not closed after it is one no
        # slicer should be handed.
        # WHAT IS CHECKED IS WHAT A SLICER REFUSES. `is_watertight` is the easier question and
        # a mesh can pass it while Bambu Studio rejects the file outright: winding can close
        # over an edge that four faces share. This asks the harder one, because these meshes go
        # in the release bundle and out to a bed.
        stl = _here.parent / f"enclosure-{name}.stl"
        mesh.export(str(stl))
        # AND THE READING IS TAKEN OFF THE FILE, re-read the way a slicer reads it. Everything
        # before this is in memory and in double precision; what goes to the bed is neither.
        written = trimesh.load_mesh(str(stl))
        loose = _flute_skin.non_manifold_edges(written)
        if loose or not written.is_watertight:
            # EVERY PIECE IS STILL WRITTEN, and the build still fails. A piece that comes back
            # refusable says nothing about the five beside it, and raising on the first one
            # withholds five good files over a sixth — including, on the day this was written,
            # the one piece somebody was waiting to print.
            refused.append(
                f"enclosure-{name}.stl: {loose} non-manifold edge(s), watertight="
                f"{written.is_watertight}, over {len(written.faces)} facets")
        print(f"-> enclosure-{name}.stl  ({len(mesh.faces)} facets, "
              f"{'watertight' if mesh.is_watertight else 'NOT WATERTIGHT'})")
    export_assembly(assy, str(_here.parent / "enclosure.step"))
    print("-> enclosure.step (assembled pieces)")
    if refused:
        raise ValueError(
            "meshes a slicer refuses, read back off the file and merged by position the way a "
            "slicer reads one:\n    " + "\n    ".join(refused))


def stated_box(pack):
    """The box at `appliance_width` × `rear_plane_y` × `appliance_height`, with `pack` measured
    against it — the description `build_pieces` turns into the four printable pieces.

    THE PACK DOES NOT SIZE IT. Where the bodies stand decides what `_dims` puts in `BOUNDS`,
    and a pack that reaches past a wall gets that wall drawn through it, a red row saying by
    how much, and a clash in `pack-closes` at the body that overran. Moving a body moves the
    reading, never the wall."""
    return _dims(pack)


def machine_of():
    """The cold core, when directly derived, and the box around the placed machine.

    A build action receives the exact output of `enclosure_box.py`, which derives the pack once
    for both enclosure producers. It needs no core: the standalone overlap report is diagnostic
    output, not part of a wall's geometry. A direct design run derives the live pack and reports
    against its placed core; it never accepts a potentially old description from the source tree.

    Imported here rather than at module scope so that enclosure_assembly, which builds its
    own assembly around these walls, is not importing a module that is importing it back."""
    import _box_spec

    if _box_spec.in_action():
        box, bounds = _box_spec.read(Box, Bound, (Pack, PortField, Nameplate))
        BOUNDS[:] = bounds
        return None, box
    sys.path.insert(0, str(_repo / "hardware" / "manifold-layout"))
    import enclosure_assembly
    _assy, pack, box = enclosure_assembly.machine()
    return pack.placed["foam-assembly"][0], box


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
    core, box = machine_of()
    pieces, assy = build_pieces(box)
    print("enclosure:")
    _report_slide(pieces, box)     # the slides swept and the catches lifted, into BOUNDS
    _report_bounds()          # the machine's, with its pieces cut and its slides swept

    _export_pieces(pieces, assy)

    _report_columns(box)
    _report_facet(pieces["front-top"], box)
    _report_seams(box)
    _report_levels(box)
    _report_split(pieces, core)

    bo = box.outer
    # The loops this box's ribs close, read off the seats the pack actually bored. Every rib
    # holding a RUN is bored for the one stock; the ribs holding a BODY are bored for whatever
    # section that body offers, so the radii are as many as the pack has kinds of seat. The
    # smallest is the runs' own and the largest is the widest body's, and a zip tie cut to the
    # largest closes on every one of them — which is what the table quotes.
    seats = sorted({round(r, 6) for *_s, r in (box.pack.tube_anchors or ())})
    if not seats:
        raise ValueError(
            "the box bores no tube anchor at all, and the zip tie table quotes a loop for them. "
            "Either the pack stands a rib again or the table stops reading one.")
    # And the meter's, off the one station its two anchors are struck from. A flow-meter anchor
    # reaches `flow_meter_anchor_wall` off the arm's axis where a rib reaches `wall`, and both are
    # the box's own three millimetres, so the hull is the same figure of the seat and one function
    # reads both families.
    meter = box.pack.flow_meter_anchors
    if not meter:
        raise ValueError(
            "the box hangs no flow-meter anchor, and the zip tie table quotes the loop one closes. "
            "Either the pack stands them again or the table stops reading one.")
    # The vents as the piece came out, for the page — the same reading `flank-vent-mullions` is
    # graded on, asked of the same solid after it was drawn.
    vent_read = vent_readings(pieces, box)
    plate = box.pack.collet_plate if (box.pump_bay and box.pack.collet_plate) else None
    front_runs = _z_rail_runs(box.inner, box.y_joint, "front", plate, box.pack.vent_chase)
    back_runs = _z_rail_runs(box.inner, box.y_joint, "back", plate, box.pack.vent_chase)
    front_rail_foot = abs(_rail_foot_face(front_runs[0][0], front_runs[0][1], "front")
                          - front_runs[0][0])
    front_rail_inboard = max(abs(_rail_x(x_in, sx, "front")[3] - x_in)
                              for x_in, sx, _y0, _y1, _lane in front_runs)
    back_rail_foot = abs(_rail_foot_face(back_runs[0][0], back_runs[0][1], "back")
                         - back_runs[0][0])
    back_rail_inboard = max(abs(_rail_x(x_in, sx, "back")[3] - x_in)
                             for x_in, sx, _y0, _y1, _lane in back_runs)
    # WHAT A FLANK ACTUALLY BEARS ON, which is its run less anything crossing it: the PRV
    # passage takes `vent_channel_w` of the flank it stands on (`_vent_chase`), so the two
    # back flanks do not read the same figure and the card should not say they do.
    def _borne(run):
        _x, sx, y0, y1, _lane = run
        lo, hi = min(y0, y1), max(y0, y1)
        cut = sum(vent_channel_w for cx, cy, _cz in (box.pack.vent_chase or ())
                  if (cx < 0.0) == (sx > 0.0) and lo <= cy <= hi)
        return abs(y1 - y0) - rail_stop_len - cut
    back_len = sorted(_borne(r) for r in back_runs)
    if box.pack.vent_chase:
        _vent_x, _vent_y, _vent_z = box.pack.vent_chase[0]
        vent_rib_base = _vent_x - back_top_flank_face()[0]
        vent_rib_land = ((_vent_z - vent_channel_w / 2.0)
                         - (z_seam + z_rise + vent_rib_base))
    else:
        vent_rib_base = vent_rib_land = None
    variables = {
        "SLIDE_SLIP": f"{slide_slip:g} mm",
        "PUMP_CARTRIDGE_Z_CLEARANCE": f"{pump_cartridge_z_clearance:g} mm",
        "HOOK_LAP": f"{hook_lap:g} mm",
        "FRONT_HOOK_LAP": f"{front_hook_lap:g} mm",
        "BACK_HOOK_LAP": f"{back_hook_lap:g} mm",
        "HOOK_FOOT": f"{hook_foot:g} mm",
        "Z_RISE": f"{z_rise:g} mm",
        "HOOK_NECK": f"{hook_foot + slide_slip:g} mm",
        "RAIL_REACH": f"{rail_reach_in:.1f} mm",
        "FRONT_RAIL_FOOT": f"{front_rail_foot:.4g} mm",
        "FRONT_RAIL_INBOARD": f"{front_rail_inboard:.4g} mm",
        "BACK_RAIL_FOOT": f"{back_rail_foot:.4g} mm",
        "BACK_RAIL_INBOARD": f"{back_rail_inboard:.4g} mm",
        "VENT_CHANNEL_W": f"{vent_channel_w:g} mm",
        "VENT_GROOVE_ROOF": f"{box.inner[0] - box.outer[0]:.4g} mm",
        "VENT_RIB_BASE": (f"{vent_rib_base:.4g} mm" if vent_rib_base is not None
                          else "no station"),
        "VENT_RIB_LAND": (f"{vent_rib_land:.4g} mm" if vent_rib_land is not None
                          else "no station"),
        "RAIL_RUN_FRONT": f"{_borne(front_runs[0]):.0f} mm",
        "RAIL_RUN_BACK": f"{back_len[-1]:.0f} mm",
        "RAIL_RUN_BACK_W": f"{back_len[0]:.0f} mm",
        "LOOP_CARB_1": f"{tube_anchor_tie_loop(seats[0]):.3g} mm",
        "LOOP_WR1110": f"{tube_anchor_tie_loop(seats[-1]):.3g} mm",
        "LOOP_DIGITEN": f"{tube_anchor_tie_loop(meter[2]):.3g} mm",
        "ANCHOR_SEATS": ", ".join(f"{2 * r:.4g}" for r in seats),
        "DISPLAY_FACET_X": f"{display_facet_x:.4g} mm",
        "DISPLAY_FACET_SLOPE": f"{display_facet_slope:.4g} mm",
        "DISPLAY_INSET_X": f"{display_inset_x:.4g} mm",
        "DISPLAY_INSET_SLOPE": f"{display_inset_slope:.4g} mm",
        "DISPLAY_SCREW_X": f"{display_screw_x:.4g} mm",
        "MQ6_CARD_T": f"{mq6_card_x:.4g} mm",
        "MQ6_SLOT_OPEN": f"{mq6_card_x + 2 * mq6_slot_press:.4g} mm",
        "COND_SLOT_OPEN": f"{cond_slot_open:.4g} mm",
        "COND_SLOT_GRIP": f"{cond_slot_grip:.4g} mm",
        "CORE_STOP_BORE": (f"{2.0 * (box.pack.core_stops[0][2] + core_stop_slip / 2.0):.4g} mm"
                           if box.pack.core_stops else "no station"),
        "CORE_STOP_WEB": f"{core_stop_web:.4g} mm",
        "CORE_STOP_RISE": f"{core_stop_rise:.4g} mm",
        # The block runs the wall inboard to one round past the tangent, and both are mirrored.
        "CORE_STOP_WIDE": (
            f"{interior_x()[1] - (abs(box.pack.core_stops[0][0]) - box.pack.core_stops[0][2]):.4g} mm"
            if box.pack.core_stops else "no station"),
        "CORE_HOLD_LAND": f"{core_hold_land:.4g} mm",
        "CORE_HOLD_REACH": f"{core_hold_reach:.4g} mm",
        "CORE_HOLD_RISE": f"{core_hold_rise:.4g} mm",
        "CORE_HOLD_WIDE": (f"{box.pack.core_holds[0][1] - box.pack.core_holds[0][0]:.4g} mm"
                           if box.pack.core_holds else "no station"),
        "COLUMN_ARC": f"{column_round:.3g} mm",
        # What a hand gets on a flank: the return's own section and the lane the box keeps
        # open behind it, off the exterior side face.
        "COLUMN_ALONG": f"{_column_along():.3g} mm",
        "COLUMN_DEPTH": f"{_column_depth():.3g} mm",
        "APPLIANCE_HEIGHT": f"{appliance_height:.4g} mm",
        # The sections on this box that are not `wall`, and the piece each belongs to. Every
        # WALL grows INWARD off the plane the box states, so the silhouette and `interior_x`
        # both stand still and only the piece carrying the section knows about it. The FLOOR
        # is the one that does not: `appliance_height` is struck to its underside, so its
        # section stands in the silhouette and the cavity keeps its floor plane at z = 0.
        "WALL_T": f"{wall:.4g} mm",
        "FLOOR_T": f"{floor_t:.4g} mm",
        "FLUTE_COUNT": f"{flute_count:d}",
        "FLUTE_PERIM": f"{plan_perimeter(bo):.5g} mm",
        "FLUTE_PITCH": f"{flute_pitch(bo):.5g} mm",
        "COUPON_PITCH": f"{reeding.flute_pitch:.4g} mm",
        "FLUTE_WIDTH": f"{reeding.flute_width:.4g} mm",
        "FLUTE_DEPTH": f"{flute_depth:.4g} mm",
        "FLUTE_BACKING": f"{flute_backing:.4g} mm",
        "FLUTE_LEFT": f"{flute_backing - flute_depth:.4g} mm",
        "FLUTE_RISE": f"{flute_rise:.4g} mm",
        "FLUTE_STEPS": f"{flute_fade_steps:d}",
        "FLUTE_RAMP": f"{math.degrees(math.atan(1.5 * flute_depth / flute_rise)):.3g}°",
        # The bay storey's complete phase path, including its two uncut air spans.
        "STOREY_RUN": (
            f"{sum(l for _k, l, _d in _bay_storey_segments(box.inner, bo, box.pump_bay, box.pack.collet_plate)):.5g} mm"
            if box.pump_bay and box.pack.collet_plate else "no bay on this pack"),
        "STOREY_BAND": (f"{bay_storey_z(box.pump_bay)[0]:.4g}..{bay_storey_z(box.pump_bay)[1]:.4g} mm"
                        if box.pump_bay else "no bay on this pack"),
        # The condenser's own two vents, pierced down the flutes those flanks already carry.
        # Every one of these is READ OFF THE BUILT PIECE (`vent_readings`) or off the field
        # the slot was struck on, so the page and `flank-vent-mullions` quote one derivation.
        "VENT_SLOT": f"{reeding.pierce_width:.4g} mm",
        "VENT_MULLION": f"{reeding.mullion(flute_pitch(bo), reeding.pierce_width, 1):.4f} mm",
        "VENT_CEILING": f"{reeding.pierce_max(reeding.pierce_shell, flute_pitch(bo)):.4f} mm",
        "VENT_SHELL": f"{reeding.pierce_shell:.4g} mm",
        "VENT_SPARE": (
            f"{reeding.mullion(flute_pitch(bo), reeding.pierce_width, 1) - reeding.pierce_shell:.4f} mm"),
        "VENT_JAMB": (
            f"{2.0 * wall - flute_depth * float(reeding.groove(reeding.pierce_width / 2.0)):.4f} mm"),
        "VENT_OPEN_PCT": f"{100.0 * reeding.open_fraction(flute_pitch(bo), reeding.pierce_width, 1):.1f} %",
        "VENT_CLEAR": f"{cond_vent_clear:.4g} mm",
        "VENT_FLANK_T": f"{2.0 * wall:.4g} mm",
        "VENT_WINDOW": (f"{box.pack.cond_airway[0]:.4g}..{box.pack.cond_airway[1]:.4g} mm"
                        if box.pack.cond_airway else "no block"),
        "VENT_BAND": (f"{vent_band(box.pack.cond_airway)[0]:.4g}..{vent_band(box.pack.cond_airway)[1]:.4g} mm"
                      if box.pack.cond_airway else "no block"),
        "VENT_BAND_H": (f"{vent_band(box.pack.cond_airway)[1] - vent_band(box.pack.cond_airway)[0]:.4g} mm"
                        if box.pack.cond_airway else "no block"),
        "VENT_FAN_RISE": f"{cond_fan_rise:.4g} mm",
        "VENT_FAN_DROP": f"{cond_fan_drop:.4g} mm",
        "VENT_TRANSOMS": f"{cond_vent_transoms:d}",
        "VENT_TRANSOM_H": f"{cond_vent_transom_h:.4g} mm",
        "VENT_TRANSOM_Z": (", ".join(f"{(a + b) / 2.0:.4g}" for a, b in
                                     vent_transoms(box.pack.cond_airway)) + " mm"
                           if box.pack.cond_airway else "no block"),
        "VENT_SEGMENTS": f"{cond_vent_transoms + 1:d}",
        "VENT_SEGMENT": (f"{vent_segment(box.pack.cond_airway):.4g} mm"
                         if box.pack.cond_airway else "no block"),
        "VENT_GROOVES": (f"{sum(1 for sx, _y in vent_grooves(bo, box.pack.cond_airway) if sx > 0):g}"
                         if box.pack.cond_airway else "0"),
        "VENT_SLOTS_IN": (f"{len(vent_read[-1.0]['slots']):g}" if -1.0 in vent_read else "0"),
        "VENT_SLOTS_OUT": (f"{len(vent_read[1.0]['slots']):g}" if 1.0 in vent_read else "0"),
        "VENT_RUNS_IN": (f"{len(vent_read[-1.0]['runs']):g}" if -1.0 in vent_read else "0"),
        "VENT_RUNS_OUT": (f"{len(vent_read[1.0]['runs']):g}" if 1.0 in vent_read else "0"),
        "VENT_TOWER": (f"{max(r['tallest'] for r in vent_read.values()):.4g} mm"
                       if vent_read else "no vent"),
        "VENT_TOWER_IN": (f"{vent_read[-1.0]['tallest']:.4g} mm" if -1.0 in vent_read else "no vent"),
        "VENT_TOWER_OUT": (f"{vent_read[1.0]['tallest']:.4g} mm" if 1.0 in vent_read else "no vent"),
        # And what the flank's own obstruction took out of that layout, read the same way: a run
        # the sweep left SHORT of a full segment is a run something rooted on this wall stopped.
        "VENT_SHORT": ((lambda seg: f"{sum(1 for r in vent_read.values() for v in r['runs'] if v < seg - stated_bound_tol):g}")(
            vent_segment(box.pack.cond_airway)) if vent_read and box.pack.cond_airway else "0"),
        "VENT_SHORTEST": ((lambda v: f"{v:.4g} mm")(
            min(min(r["runs"]) for r in vent_read.values())) if vent_read else "no vent"),
        "VENT_ASPECT": ((lambda tall, thin: f"{tall / thin:.3g}:1")(
            max(r["tallest"] for r in vent_read.values()),
            min(min(r["mullions"]) for r in vent_read.values()))
            if vent_read else "no vent"),
        "VENT_ASPECT_BARE": ((lambda tall, thin: f"{tall / thin:.3g}:1")(
            vent_band(box.pack.cond_airway)[1] - vent_band(box.pack.cond_airway)[0],
            min(min(r["mullions"]) for r in vent_read.values()))
            if vent_read and box.pack.cond_airway else "no vent"),
        "VENT_MEAS_MULLION": (
            f"{min(min(r['mullions']) for r in vent_read.values()):.4f} mm"
            if vent_read else "no vent"),
        "VENT_OPEN_IN": (f"{vent_read[-1.0]['open_mm2'] / 100.0:.1f} cm²"
                         if -1.0 in vent_read else "no vent"),
        "VENT_OPEN_OUT": (f"{vent_read[1.0]['open_mm2'] / 100.0:.1f} cm²"
                          if 1.0 in vent_read else "no vent"),
        "FLUTE_SEAM_MISS": (
            lambda arc, pitch: f"{min(arc % pitch, pitch - arc % pitch):.2g} mm")(
                _plan_segments(bo)[0][1] + _plan_segments(bo)[1][1]
                + (y_seam - (bo[2] + corner_round)), flute_pitch(bo)),
        "FRONT_TOP_FLANK": f"{front_top_flank_t:.4g} mm",
        "BACK_TOP_FLANK": f"{back_top_flank_t:.4g} mm",
        "BACK_TOP_WALL": f"{back_top_wall_t:.4g} mm",
        # And back-top's own ceiling: what the piece keeps of it either side of the slide-in
        # panel, the channel the panel fills, and the most any relief still leaves corbelled.
        "CEILING_STRIP": f"{_ceiling().rail_run:.4g} mm",
        "CEILING_PANEL_W": f"{_ceiling().panel_w:.4g} mm",
        "BACK_TOP_CEILING_T": f"{back_top_ceiling_t:.4g} mm",
        "BACK_TOP_CEILING_GROWTH": f"{back_top_ceiling_growth:.4g} mm",
        "CEILING_PANEL_T": f"{_ceiling().structural_t:.4g} mm",
        "CEILING_TONGUE_T": f"{_ceiling().tongue_t:.4g} mm",
        "CEILING_DADO_DEPTH": f"{_ceiling().dado_depth:.4g} mm",
        "CEILING_KEEP": f"{max(r[4] for r in back_top_ceiling_reliefs):.4g} mm",
        "RELAY_CEILING_KEEP": f"{next(r[4] for r in back_top_ceiling_reliefs
                                        if r[0] == 'relay-1'):.4g} mm",
        "GROUND_CEILING_KEEP": f"{next(r[4] for r in back_top_ceiling_reliefs
                                         if r[0] == 'ground-stack'):.4g} mm",
        "BOSS_END_CLEAR": f"{boss_end_clear:.4g} mm",
        # How much stock each grown flank stands INBOARD of the box's own interior — the room a
        # rib rooted on that piece loses, and the room its relief gives back.
        "BACK_TOP_FLANK_GROWN": f"{back_top_flank_t - wall:.4g} mm",
        "FRONT_TOP_FLANK_GROWN": f"{front_top_flank_t - wall:.4g} mm",
        "PIECE_H": f"{_ceiling().piece_h:.4g} mm",
        # And the section a bottom piece's three lipped sides carry for free — the lip's own
        # skin carried to the slab (`_lip_underwall`), which is what the two flanks above are
        # brought level with.
        "LIP_UNDERWALL": f"{2.0 * wall:.4g} mm",
        # The Y-seam ladder as the walls came out — per wall, and one figure when they agree.
        "Y_LEVELS": "/".join(str(c) for c in sorted({
            sum(1 for _xi, _xe, s, _z in box.y_bosses
                if s == sx) for sx in (+1.0, -1.0)})),
        "PLUG_DIA": f"{plug_dia:.4g} mm",
        "RIDGE_WALL_T": f"{ridge_wall_t:.4g} mm",
        "RIDGE_LEN": f"{display_pcb_x:.4g} mm",
        "CABLE_BORE": f"{cable_sleeve_open:.4g} mm",
        "TEARDROP_ROOF": f"{teardrop_roof_angle:.4g}°",
        "SOCKET_BORE": f"{socket_bore_dia:.4g} mm",
        "SOCKET_OD": f"{2.0 * socket_r:.4g} mm",
        "BOX_SIZE": (f"{bo[1] - bo[0]:.0f} × {bo[3] - bo[2]:.0f} × "
                     f"{bo[5] - bo[4]:.0f} mm"),
        **pump_cartridge_figures(box),
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
    # THIS FILE, UNDER THE NAME EVERYTHING ELSE IMPORTS IT BY. A direct run imports
    # `enclosure_assembly` inside `machine_of`; that module imports `enclosure` back and must
    # receive this same copy so the Box and the bounds ledger it fills come back to `main`.
    # The ceiling joint makes the same round trip. One name, one module, one box.
    sys.modules.setdefault(__name__ if __name__ != "__main__" else "enclosure", sys.modules[__name__])
    main()
