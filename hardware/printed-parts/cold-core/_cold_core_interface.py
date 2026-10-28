"""Shared interface for the cold-core's geometry modules — dimensional
constants and hole-punch helpers that every sibling part (foam shell,
foam cap stack, reservoir, copper ports, coil mandrel) needs to stay
in sync against.

The constants carry claims about each other — a screw long enough for its insert, a band wide
enough for its bore, two columns far enough apart for foam to reach between them — and those are
settled here, as this file is read, with no solid yet to measure. `_stated_bounds` is the ledger
they record into; `enclosure_assembly.carry_stated_bounds` drains it onto the machine's card, where
an open one is a red row a reader can see beside the geometry it describes. The siblings that
import this module take `bound` and `state` from here rather than reaching for the ledger
themselves, because this is already the path they read every other shared name off."""

import itertools
import math
import sys
from collections import namedtuple
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(0, str(_here.parent / "enclosure" / "enclosure"))
sys.path.insert(0, str(_here.parent / "valve-seat"))
sys.path.insert(0, str(_here.parents[1] / "reference" / "g-ganen-pump" / "installation"))

import cadquery as cq

import fits
import valve_seat as _valve_seat
import g_ganen_installation as _water_pump
import _above_core_mounts as _above_mounts
from world_workplane import xy_plane_z_up, xz_plane_y_up, xz_plane_y_down, WorldWorkplane
from _stated_bounds import bound, state
from _enclosure_interface import (manifold_rise, inner_limb_drop,
                                  rear_plane_y, rear_seam_clear)
import _anchor_cap_interface as _anchor_cap


# Standing casing walls and pocket walls share a section; floors and stack
# datums have their own thickness. Changing stock must not resize a mating cavity.
wall_thickness = 2.38
floor_thickness = 2.0
# Public floor/height datum consumed by the assembly and its installation reviews.
wall_and_floor_thickness = floor_thickness
hole_shift_from_edge = 15.0


# Plain outside faces reserve room for the foil within the enclosure envelope.
outer_shell_wall = wall_thickness


# The cold cylinder + its evaporator coil. [7 mm](COIL_RADIAL_CLEARANCE) of
# radial clearance out from the cylinder OD holds the 1/4" ACR copper coil +
# thermal tape; the carbonator support ring cradles the carbonator rim at this envelope.
carbonator_outer_radius = 63.5
coil_radial_clearance = 7.0
carbonator_coil_envelope_radius = carbonator_outer_radius + coil_radial_clearance

# The reservoir-facing arc is a mating datum. Pocket stock grows toward the
# carbonator, and the remaining radial space contains the coil and pour foam.
pocket_centerward_arc_outer_radius = 80.5  # reservoir-facing mating arc
foam_thickness_around_cylinder = (
    pocket_centerward_arc_outer_radius - wall_thickness - carbonator_outer_radius
)

# Foam-shell outer height. Carbonator height + [30 mm](ABOVE_TANK_ELBOWS_HEIGHT) above for top-side elbow
# fittings + [30 mm](BELOW_TANK_ELBOWS_HEIGHT) below for bottom-side elbow fittings + 1 mm
# wall-thickness compensation.
carbonator_height = 152.4
below_carbonator_elbows_height = 30.0
above_carbonator_elbows_height = 30.0
foam_shell_outer_height = (
    carbonator_height + below_carbonator_elbows_height + above_carbonator_elbows_height + 1.0
)

carbonator_support_ring_height = 30.0
support_ring_radial_width = 9.0

# Passive cold-core passages leave 0.5 mm radial air around the measured 6.5 mm
# tube, including the blind crossing below a reservoir. These holes guide a line
# through the shell; they do not grip it or seal the foam pour. Mask pour gaps
# temporarily. Faucet, organizer, fitting and copper passage fits have their own sizes.
passage_tube_od = 6.5
port_hole_radius = passage_tube_od / 2.0 + 0.5

# Reed-channel cavity depth (radial, out from the bag-pocket far wall). The reed
# column drops into this cavity; the outer_shell X width is sized so the cavity +
# its wall butt the outer shell wall (see outer_shell_x_length). Consumed by
# _reed_channels.py too.
reed_x_depth = 6.0
# Half the cavity's reach along the reservoir, either side of the column's own station. The
# cavity carries the laced column and the cable that leaves up it, and `reed_cable_conduit_xy`
# stands on the same two figures — one lane, read here rather than in two places.
reed_y_half_w = 4.0

# WHERE THE LEVEL SENSOR STANDS along the reservoir — the float rod inside
# (`reservoir.rod_position_y`) and the reed column outside (`_reed_channels.reed_y_center`),
# which are ONE station and not two: a reed reads the float's magnet across the pocket wall
# and nothing else, so the two cannot drift apart (`reservoir/level-sensing.md` carries the
# bench-measured magnet-to-reed path). The pair rides the reservoir's +Y half, and the donut
# has its whole travel clear of both cavity walls anywhere along that half; the cap's vent and
# both of its bores stand off it (`reservoir.py`).
level_rod_y = 32.5

# Reservoir mating extents are fixed independently of the PET-GF wall stock.
# The outer pocket extents follow the stock on their foam-facing sides.
bag_pocket_far_inner_x = 129.5
bag_pocket_y_inner_max = 70.5
bag_pocket_width = 2 * (bag_pocket_y_inner_max + wall_thickness)
bag_pocket_depth = (bag_pocket_far_inner_x - pocket_centerward_arc_outer_radius
                    + 2 * wall_thickness)
bag_pocket_floor_top_z = floor_thickness
bag_pocket_walls_top_z = foam_shell_outer_height
# The reed cavity and its cap passage are functional datums, independent of
# the pocket wall's foam-facing face.
reed_channel_inner_x = 131.5
reed_column_axis_x = reed_channel_inner_x + reed_x_depth / 2.0

# Matches the reservoir's outer +X × ±Y fillet (R=6) with reservoir_clearance
# on top, so the reservoir's outer arc slides into a snugly-mated arc on
# the pocket's inner corner with uniform clearance.
reservoir_clearance = fits.running
bag_pocket_corner_inner_radius = 6.0 + reservoir_clearance
reservoir_floor_thickness = 3.0

# BOTH OF A RESERVOIR'S MOUTHS ARE IN ITS OWN CAP. The fill ends in the headspace, above
# the liquid; the draw is a dip tube — the line itself, carried on down through its bore to
# the floor — so everything entering has to cross the cavity to leave. The cap reads each
# station (`reservoir.build_reservoir_cap`) and so does the conduit standing over it
# (`cap_conduits`) — in two different frames, neither part seeing the other, so
# `reservoir_fill_conduit_xy` and `reservoir_draw_conduit_xy` are the whole of what holds
# them together. A conduit that misses its bore is a hole into a sealed pocket; a bore that
# misses its conduit is a blind one.
#   EACH RESERVOIR TAKES ITS OWN STATIONS, and only half of what picks them lives
# in this file. THIS half is the cap's: anywhere the vent boss, the rod's
# register boss, the screw bosses and the other bore leave empty, standing over open
# cavity, and for the draw a dip tube clear of the float's whole travel.
#   The OTHER half is what stands on the crown over each pocket, and this module
# cannot see it — the machine imports the cold core, not the reverse. So the
# fence is measured where the bodies are, in `manifold-layout/enclosure_assembly.py`,
# and what arrives here is the answer rather than the reasoning. B's pocket has
# a clear crown: its fill takes the corner furthest from its draw. A's carries the
# pump: its draw takes the bay between the pump's two east feet.
#   The conduit's own boss does not pay that fence either way: it is a column
# INSIDE the cap, under the crown those bodies stand on. What has to find room
# up there is the tube.
reservoir_fill_port = {
    -1: (-90.5, 43.5),      # B, forward pocket — the corner opposite its draw
    +1: (102.5, -61.0),     # A, aft pocket — the strip between the pump and the brick
}
reservoir_fill_sides = tuple(sorted(reservoir_fill_port))
reservoir_draw_port = {
    -1: (-94.3, 6.0),       # B — between the lid's pour hole and V-B's plinth
    +1: (84.2, -45.0),      # A — between the pump's two east feet
}


def reservoir_fill_conduit_xy(side):
    """The CAP-frame station of the conduit standing over one reservoir's cap fill bore.

    The bore is authored in the RESERVOIR's frame (`reservoir._add_port`) and the
    conduit in the CAP's, and the cap installs spun a half turn about Z
    (`foam_assembly.spin_xy`) — so the station is the anchor negated in both coordinates."""
    x, y = reservoir_fill_port[side]
    return (-x, -y)


def reservoir_draw_conduit_xy(side):
    """The CAP-frame station of the conduit the dip tube comes down — the draw bore's anchor
    negated, for the same half turn."""
    x, y = reservoir_draw_port[side]
    return (-x, -y)

# Foil sits on the plain casing within a 0.30 mm per-face envelope allowance.
casing_foil_allowance = 0.30
outer_shell_x_length = 282.4
outer_shell_y_length = 180.4
bag_pocket_outermost_x = bag_pocket_far_inner_x + wall_thickness
outer_shell_foam_gap = (
    outer_shell_y_length / 2 - outer_shell_wall - bag_pocket_width / 2
)

# Open routing room between the pocket's foam-facing wall and the casing.
forward_band_width = outer_shell_x_length / 2 - outer_shell_wall - bag_pocket_outermost_x
forward_band_mid_x = bag_pocket_outermost_x + forward_band_width / 2.0

# The −Y pour band — the open gap between the bag-pocket wall's outer face
# and the outer shell's inner face, poured full of foam around the
# reservoirs.
pour_band_pocket_side_y = -(bag_pocket_width / 2)
pour_band_shell_side_y = -(outer_shell_y_length / 2 - outer_shell_wall)


# Foam-cap stack — the pour trays that close both ends of the shell (one
# mouth-up on top, one mouth-down underneath), each with a thin pour lid.
# The interior height is the cap's foam depth; the printed cup adds one
# floor.
foam_cap_interior_height = 16.0  # fixed pour depth and stack-height datum
foam_cap_height = foam_cap_interior_height + wall_and_floor_thickness
foam_cap_lid_pour_radius = 10.0
foam_cap_lid_vent_radius = 3.0
foam_cap_lid_hole_inset = 30.0
# The TOP lid's pour hole stands in its fore-west quarter, over open cavity: west of the
# reed-B cable column and the B-fill carrier, clear of the PCB's fore-west post. At the
# centreline station it would open onto that cable column's top and under a WAGO well.
top_lid_pour_xy = (outer_shell_x_length / 2 - foam_cap_lid_hole_inset, -64.0)
# The top lid's vents stand this much nearer its −X end, clear of the A-fill guide's entry
# countersink.
top_lid_vent_setback = 2.5

# --- The carbonator's clocking --------------------------------------------------
#
# Four 1/4" NPT ports, two per end plate, each pair [1.5"](CARBONATOR_PORT_PITCH) centre to
# centre on a diameter (`hole_offset` in cut-parts/carbonation/endcaps-circular). Both
# plates carry the float rod's blind register beyond the −Y port on their common
# port axis, the rod is tack-welded into the bottom plate's register and enters the top plate's
# at closure, so the plates are clocked together and the carbonator has ONE port axis.
#   That axis is the shell's ±Y. All four ports stand [19.05 mm](CARBONATOR_PORT_OFFSET) off
# the shell's own axis on it, two under the carbonator and two over it.
carbonator_port_offset = 0.750 * 25.4
# The register and external bridge share -Y, opposite the reservoirs' +Y sensing stations.
carbonator_sensor_azimuth = -90.0
carbonator_sensor_axis = (0.0, -1.0)
# The upper register's stainless stop holds the float below the inlet-jet tip.
carbonator_float_top_stop_height = 4.0
carbonator_float_top_stop_diameter = 9.5

# CO2 inlet — the bottom plate's LANE-SIDE port, open into the vessel. Gas enters below
# the liquid and rises to replenish the headspace; the top water-inlet jet provides the
# intended gas/water contact during refill (`assembly/water-inlet-jet.md`).
#   Outside the carbonator it is one bore on the shell's own centreline, level with the
# bottom-plate elbows, run from the port out through the carbonator support ring to the
# port lane. The port, its TAISHER elbow, the PI010822S collet made up on it and
# the ring bore all stand on that one line, so the tube is the only thing that
# crosses shell material and no bend is taken in-cavity. The line reaches the
# bore's lane end from ABOVE — down the port lane from the cap's `co2-in`
# conduit — so it is laid before the top cap goes on, not pushed in from outside.
co2_inlet_y = -carbonator_port_offset
co2_inlet_tube_radius = port_hole_radius

# The top plate's two, by the same pair. Filtered tap water arrives at the top plate ABOVE the
# liquid and falls into the headspace against the CO2 back-pressure; the carbonated draw leaves
# at the bottom plate, below it. So the carbonator is filled high and drawn low, the same way both
# reservoirs are.
# Port 4 and its shroud stand on +Y. The barrel vent points down the west lane,
# turns once and crosses the +Y shell flank into the enclosure's exterior relief
# chase (`_internal_routes.prv_vent_flank_y`). The top water inlet stands on -Y;
# its tube crosses the carbonator top to the +Y cap band.
water_inlet_port_y = -carbonator_port_offset
prv_port_y = +carbonator_port_offset

# Cap-to-outer-shell joinery: one attachment point per station in
# `attachment_stations`, per face × 2 faces, each screw passing lid + cap into an
# insert pressed from the shell face it mates. The dry casing seams are
# sealed externally with 3M 425 foil tape. See bom.md for hardware SKUs.
cap_shell_clearance = fits.slip
cap_lid_clearance = fits.slip
screw_clearance_radius = 3.0 / 2.0 + fits.slip
insert_pocket_radius = 2.0  # ⌀[4](INSERT_POCKET_DIAMETER), ruthex's own recommended hole
insert_pocket_depth = 10.5  # 5.7 mm insert; room for the M3×25 tip beyond it
screw_boss_size = 8.0  # ⌀[8 × 8 mm](SCREW_BOSS_SIZE) cylindrical boss at each attachment

# The head sits in the lid, and a lid is [5.4 mm](FOAM_CAP_LID_H) thick where it takes one —
# one wall of PET-GF under the head, the boss section under that, and the lid's outer face a
# plane. EACH END OF THE STACK BUYS THAT HEIGHT ITS OWN WAY. The bottom cup's boss columns stop
# [3.4 mm](HEAD_PAD_H) short of its mouth and the lid's pad, of the boss's own cross-section,
# fills that relief. The TOP lid is solid to the same height over its whole footprint — it is
# the plate the service bay stands on, so its underside is one plane and the band is the cup's
# to give up (`_foam_cap.top_cap_height`).
screw_head_height = 3.0  # DIN 912 M3 nominal
head_seat_recess = fits.slip
head_cbore_radius = 5.5 / 2.0 + fits.slip
head_cbore_depth = screw_head_height + head_seat_recess
# A pad as tall as the counterbore is deep leaves the land at one wall exactly.
# The bottom lid prints outer-face-down. Its supported screw-seat roofs need
# the bridge allowance, backed by the same full plate thickness. The matching
# cup relief follows this pad; top cup/lid share the band at fixed stack height.
head_pad_height = head_cbore_depth + fits.supported_surface
head_pad_slip = fits.slip  # pad to the boss relief that receives it
# A lid, plate and pad in one. `_foam_cap.lid_total_height` builds on this name.
foam_cap_lid_height = wall_and_floor_thickness + head_pad_height

# --- The front face, and the lane that reaches it ---------------------------
#
# Every penetration opens on the shell's −X face. That face is the SHORT one, and
# in the appliance it is yawed onto the machine's front (`enclosure_assembly.FOAM_YAW`) —
# which is why the shell's short axis is what sets the appliance's width.
#
# Nothing reaches that face head-on: the reservoir pockets fill both ±X ends of the
# shell, so a line from the carbonator gets there along the −Y POUR
# BAND, which runs the shell's whole length outboard of both pockets. What a line
# may use of that band is the LANE: the strip inboard of every attachment boss.
# Every boss on a ±Y wall stands hard against it (`attachment_stations`) and reaches
# `screw_boss_size` in from its outer face, so the lane is exactly what they leave,
# and it runs clear end to end at every height above the floor slab. The two bosses on
# the ±X walls stand on the face the lanes arrive at, clear of both bands in y.
#
# Each copper tail has its own routing lane and a fixed exit axis.
front_wall_x = -141.5  # fixed copper port frame
port_lane_outer_y = -82.5  # fixed tube-routing lane
port_lane_inner_y = -72.5  # tube-routing datum; pocket stock grows outside it
port_lane_mid_y = (port_lane_outer_y + port_lane_inner_y) / 2

# The +Y band's lane, which is this one mirrored — the bosses stand at both signs, so both
# bands leave the same strip. The evaporator's WARM tail drops this band to its own station
# low on the front wall (`_copper_ports.stations()`).
west_lane_mid_y = -port_lane_mid_y

# Where the evaporator coil's two tails leave the carbonator: the low one one
# `hole_shift_from_edge` above the bottom-plate elbow band, the high one the same
# below the top's. These are the COIL's heights — what the mandrel is wound to and
# what the reed bridge's wrap band spans — and they are NOT the heights their copper
# crosses the shell wall at. Each tail turns onto a LANE OF ITS OWN — the inlet's onto
# the port lane, the outlet's onto the west (`_copper_ports.stations()`) — and both drop
# from there to their exit stations, so moving a passage cannot compress
# the coil.
evap_tail_low_z = hole_shift_from_edge + wall_and_floor_thickness + below_carbonator_elbows_height
evap_tail_high_z = (foam_shell_outer_height - hole_shift_from_edge
                    - wall_and_floor_thickness - above_carbonator_elbows_height)

# The two copper exits cross the front wall; their axes and bore clearance are
# declared in `_copper_ports`. The seven fluid lines and two reed cables leave
# through their cap conduits, above the adjacent refrigeration base.

# Rounded outer-shell corners. Each corner's exterior wall is a true arc:
# the outer face is a quarter-round of [11.7 mm](CORNER_ROUND_R) radius, the
# inner face concentric one wall-thickness inboard.
corner_round_radius = 11.7


state("forward-band-takes-a-bore", "The forward band still passes a line",
      f"{forward_band_width:g} >= {passage_tube_od:g} mm",
      forward_band_width >= passage_tube_od,
      f"the open routing band is {forward_band_width:g} mm wide for the "
      f"{passage_tube_od:g} mm measured tube; enlarged bores cross printed walls and caps")

# A STATION NAMES THE WALL IT LEANS ON, and that is the whole of this table. A boss is a
# cylinder tangent to one exterior face with a web run out to it, and WHICH face cannot be
# read off the sign of the boss's own coordinates: a station on a ±X wall stands at y = 0,
# where the sign is neither. `attachment_stations` carries it; `attachment_xy_positions` is
# the same table read as bare points, which is what every clearance reading in the tree wants.
#
# Every boss on a ±Y wall stands HARD against it — none in a corner, and none inboard.
# The ±Y bands are the only place a line running to the front face can travel, and a boss
# reaching further in than `screw_boss_size` would narrow the lane below one bore. A boss
# seated diagonally IN a corner (its cylinder tangent to the exterior arc, which is the
# deepest seat available) reaches diagonally into the band, and that is what closed the corner
# the lane has to turn through. Held against the wall instead, every one of them leaves the
# same lane and the ±X ends of both bands run clear to the wall.
#   THE FOUR CORNER BOSSES stand over the reservoir pockets' own far walls, which is the
# furthest out they can go and still keep one wall of PET-GF around their insert pockets
# inside the corner's rounded skin.
#   THE FOUR MID BOSSES stand two to a wall, clamping its cap edge between the corners.
# Two to a wall also settles the shroud, which is the one body standing where a single centred
# boss would go: the PRV's ⌀23 cup lies on the carbonator's +Y port axis (`prv-shroud/`) and
# its closed end reaches within ~3 mm of the +Y wall, so its section spans x ±11.5 there. At
# `mid_screw_x_offset` neither boss is near it, and neither ±Y wall is a special case of the
# other.
#   THE TWO END BOSSES stand centred on a ±X wall, the only station either ±X run has. Their
# cylinder is tangent to the ±X face the same way a ±Y boss is tangent to its own, and the web
# runs out to that face instead. Both centres are clear: in the shell the two copper feed-throughs
# the front face is cut for stand at y ±77.5 and nothing else reaches it, and on the TOP LID's
# outer face — the deck the machine stands on — the one body that would cover a centre is
# `water-3`'s tie post, which stands along its own run and is set where this station is not
# (`cap_side_anchors`, `cap_side_anchor_room`).
#
# The whole pattern is symmetric under a 180° turn about Z — balanced cap clamping, and
# the top cap free to install either way round. Two bosses to a ±Y wall is what makes that
# free: one to a wall bought the same symmetry only by standing the pair on a diagonal.
_boss_wall_y = 86.5
_boss_wall_x = 137.5
# Rounded-corner insert pilots retain ruthex's 1.6 mm surrounding wall
# behind the smooth 0.30 mm exterior foil land.
_corner_boss_y = _boss_wall_y - 0.25
_end_boss_x = 131.5  # cap/shell screw datum, independent of pocket stock
# The mid bosses stand at ±40 mm on each long wall. The soda tube turns in
# the main body below the cup and rises through its aligned straight guide.
mid_screw_x_offset = 40.0
#: Every attachment station as `((x, y), wall)`, `wall` naming the exterior face its cylinder
#: stands tangent to and its web runs out to — "x", "y", or "corner" for one against both.
attachment_stations = (
    tuple(((x_sign * _end_boss_x, y_sign * _corner_boss_y), "corner")
          for x_sign in (1, -1) for y_sign in (1, -1))
    + tuple(((x_sign * mid_screw_x_offset, y_sign * _boss_wall_y), "y")
            for x_sign in (1, -1) for y_sign in (1, -1))
    + tuple(((x_sign * _boss_wall_x, 0.0), "x") for x_sign in (1, -1))
)
attachment_xy_positions = [_xy for _xy, _wall in attachment_stations]

# A STATION IS PRICED AGAINST THE LANE IT IS NOT IN. A ±Y boss shares the ±Y band with every
# line running to the front face, so it is held to the outer `screw_boss_size` of it and the
# lane is exactly what it leaves. A ±X boss is in neither band — it stands on the face those
# lines arrive AT, clear of both lanes in y.

# Foil seals wrap the plain casing at both ends, spanning shell/cup and cup/lid seams.
# The foil stays off the horizontal seating and bearing faces.
#
# The clamp screw, end to end. From under its head an M3 × [25](CAP_SCREW_L)
# crosses the land, then the one continuous PET-GF section the lid and the cap's
# boss column and seating clearances make between them — whatever is left is what
# it has to give the insert on the far side of the shell's face. The recess
# spends none of that: the head carries the land down with it, so the screw
# arrives deeper by exactly the pad it sank.
#   BOTH ENDS MEASURE THE SAME, and not for the same reason. At the bottom the cup
# stands its full height and its boss column stops a pad short of the mouth; at the
# top the column runs to the rim and the CUP is a pad shorter. Either way a station
# carries one pad of lid over the rest of `foam_cap_height` in column.
cap_screw_length = 25.0
insert_length = 5.7  # ruthex RX-M3x5.7, set flush with the face
cap_screw_beyond_face = cap_screw_length - (
    wall_and_floor_thickness  # the land under the head
    + (foam_cap_height - head_pad_height)  # the boss column under the pad
)
state(
    "cap-screw-reach", "The clamp screw reaches the whole of its insert",
    f"{insert_length:g} mm past the shell face",
    cap_screw_beyond_face >= insert_length,
    f"an M3 × {cap_screw_length:g} reaches {cap_screw_beyond_face:g} mm past the shell "
    f"face, short of its {insert_length:g} mm insert")
state(
    "cap-screw-bottom", "The clamp screw pulls its head down before it bottoms",
    f"{insert_pocket_depth:g} mm past the shell face at most",
    cap_screw_beyond_face <= insert_pocket_depth,
    f"an M3 × {cap_screw_length:g} reaches {cap_screw_beyond_face:g} mm past the shell "
    f"face and bottoms in a {insert_pocket_depth:g} mm pocket before its head is down")

# Deck mounts — the pump and PCB carried on columns of the TOP CAP.
# Each column grows from the cup floor and takes a full RX-M3x5.7 heat-set.
# Foam fills the cup around the columns.
#   A station with no standoff stops at the cap's mouth rim, under the lid, and its module
# seats on the lid's outer face. A station with a standoff carries its column on through
# the lid, and its module seats on the column tops.
#   The stations live here, in the cap's own frame, because the mount belongs to the part it
# is printed in. `foam_assembly.deck_mount_station` carries them into the stack's own frame,
# and whoever seats the stack carries them from there into the world.
deck_mount_boss_radius = 5.0     # Ø10 column; 3 mm stock around the Ø4 insert pilot
deck_mount_bore_radius = 2.0     # ⌀4 for a ruthex M3 heat-set
deck_mount_lid_slip = fits.slip  # a standing column to the lid's clearance hole
deck_mount_insert_length = 5.7   # ruthex RX-M3x5.7, set flush with the column top
deck_mount_bore_relief = 1.0     # ruthex minimum blind relief; also reserve travel past the screw tip

# The pour gap, [1.5 mm](DECK_MOUNT_CAP_GAP): the least room a conduit column standing in the cup
# leaves to the cavity wall or to another standing conduit, so liquid foam reaches between them
# (`cap_conduit_wall_neck`, `cap_conduit_pair_neck`). The lid's pour hole stands the same gap off
# the deck mounts' lid holes and the valve plinths (`foam_cap_lid_pour_xy`).
deck_mount_cap_gap = 1.5

# Each row carries native-reference holes through the production above-core
# placement into this cap's frame. It gives the column standoff, head-bearing
# thickness and screw length. The PCB's columns pass through the lid to its
# underside; the pump bears on the lid above flush columns. The PSU mounts
# on back-top's dry sidewall.
#   THE PATTERN IS THE CAP'S ROTATION KEY. The top cap installs spun a half turn about Z
# (`foam_assembly._spin`) and its clamp bosses are symmetric under that turn, so the thing
# that tells a builder which way the cup goes on is what is NOT symmetric — this station and the
# seven conduit columns beside it. `assembly/cold-core.md` CC-06 and CC-15 both read the cap
# that way.
# The pump's four identical rubber sliders stand at their fully engaged
# fore/aft rail ends. Screw axes sit 1.5 mm outward within the elongated slots,
# with a Ø9 × 0.8 washer on each 7 mm pad. Actual rubber compression remains
# an installed observation. V-B has an integral upright socket wall on the
# lid; V-A, V-K, the PSU and both relay modules are carried by back-top.
DeckMount = namedtuple("DeckMount", "points standoff seat screw seat_min")
deck_mounts = {name: DeckMount(*row) for name, row in _above_mounts.deck_mounts().items()}


def deck_mount_xy(name):
    """Explicit selected boss centres in the cap's own frame."""
    return tuple(sorted(set(deck_mounts[name].points)))


def deck_mount_standoff(name):
    """How far proud of the lid's outer face this mount's column tops stand."""
    return deck_mounts[name].standoff


def deck_mount_proud():
    """The tallest standoff in the pack — the foam assembly's own top over its lid's face.
    PCB columns pass through the lid; the pump columns stop below it."""
    return max((deck_mount_standoff(name) for name in deck_mounts), default=0.0)


def deck_mount_reach(name):
    """How far a seated screw runs past this mount's column top. A flush station's screw
    crosses the WHOLE lid on its way down — the top lid is solid to `foam_cap_lid_height`,
    and that is what a station under it spends before it reaches the column. A standing one
    meets its column at the head and crosses nothing. `seat` is what the head bears on before
    either — a board's own thickness, a hub's floor, or the fan of ring terminals that is the
    ground bus."""
    m = deck_mounts[name]
    over = m.seat
    if m.standoff == 0.0:
        over += foam_cap_lid_height + cap_lid_clearance
    return m.screw - over


# The pump's minimum blind depth leaves screw-tip travel below its nominal stack.
deck_mount_bore_depth = max(9.75, deck_mount_insert_length + deck_mount_bore_relief,
    _water_pump.SCREW_BORE_MIN_DEPTH, max(
    (m.screw - m.seat_min - (foam_cap_lid_height + cap_lid_clearance
                           if m.standoff == 0.0 else 0.0)
     for m in deck_mounts.values()), default=0.0) + deck_mount_bore_relief)
_mount_reach = bound(
    "deck-mount-reach", "Every deck mount's screw reaches the whole of its insert",
    f"{deck_mount_insert_length:g} mm into the column")
for _name in deck_mounts:
    _mount_reach(
        deck_mount_reach(_name) >= deck_mount_insert_length,
        f"deck mount {_name}: an M3 × {deck_mounts[_name].screw:g} through "
        f"{deck_mounts[_name].seat:g} mm of seat reaches {deck_mount_reach(_name):g} mm "
        f"into the column, short of its {deck_mount_insert_length:g} mm insert")


def deck_lid_hole_radius(name):
    """The lid's opening at a deck-mount station: a slip fit around a column standing
    through it, a screw clearance over one that stops beneath it."""
    if deck_mount_standoff(name) == 0.0:
        return screw_clearance_radius
    return deck_mount_boss_radius + deck_mount_lid_slip


# --- Horizontal valve cradles -----------------------------------------------
#
# The lid carries V-B's upright valve wall, supplied by `_above_core_mounts`.
# Horizontal plinth stations use this table; the current cap has none.
Cradle = namedtuple("Cradle", "centre yaw seat")
cap_cradles = {}

# Where a boss stands off the valve's centre, and how wide it is: a socket with a wall around it.
cap_cradle_corner_inset_x = _valve_seat.corner_inset_x
cap_cradle_corner_inset_y = _valve_seat.corner_inset_y
cap_cradle_socket_radius = _valve_seat.socket_radius
cap_cradle_wall = _valve_seat.wall
cap_cradle_boss_radius = _valve_seat.boss_radius
cap_cradle_half_x = _valve_seat.seat_half_x
cap_cradle_half_y = _valve_seat.seat_half_y
cap_cradle_corner_radius = _valve_seat.seat_corner_radius

# What a cradle holds off every other thing cut in the lid's outer face. Nothing is poured
# between them — this face is the machine's room, not the cup's — so the fence is the
# machine's own clearance floor rather than the pour gap the cavity keeps.
cap_cradle_room_gap = 1.0


def cap_cradle_xy(name):
    """A cradle's four socket centres, in the cap's own frame."""
    (cx, cy) = cap_cradles[name].centre
    th = math.radians(cap_cradles[name].yaw + 90.0)
    c, s = math.cos(th), math.sin(th)
    return tuple((cx + c * sx * cap_cradle_corner_inset_x - s * sy * cap_cradle_corner_inset_y,
                  cy + s * sx * cap_cradle_corner_inset_x + c * sy * cap_cradle_corner_inset_y)
                 for sx in (-1, 1) for sy in (-1, 1))


def cap_cradle_half_extents(name):
    """Axis-aligned half extents of the plinth in the cap's frame."""
    th = math.radians(cap_cradles[name].yaw + 90.0)
    c, s = abs(math.cos(th)), abs(math.sin(th))
    return (c * cap_cradle_half_x + s * cap_cradle_half_y,
            s * cap_cradle_half_x + c * cap_cradle_half_y)


def cap_cradle_circle_gap(name, x, y, radius):
    """Plan clearance from a circular opening to the rounded plinth outline."""
    (cx, cy), yaw, _seat = cap_cradles[name]
    th = math.radians(yaw + 90.0)
    dx, dy = x - cx, y - cy
    px = abs(math.cos(th) * dx + math.sin(th) * dy)
    py = abs(-math.sin(th) * dx + math.cos(th) * dy)
    qx = px - (cap_cradle_half_x - cap_cradle_corner_radius)
    qy = py - (cap_cradle_half_y - cap_cradle_corner_radius)
    return (math.hypot(max(qx, 0.0), max(qy, 0.0))
            + min(max(qx, qy), 0.0) - cap_cradle_corner_radius - radius)


def cap_cradle_rectangle_gap(name, x0, x1, y0, y1):
    """Plan clearance to an axis-aligned rectangle at these cap stations."""
    (cx, cy), yaw, _seat = cap_cradles[name]
    assert math.isclose(yaw % 90.0, 0.0), "plinth rectangle reading needs an axial station"
    hx, hy = cap_cradle_half_extents(name)
    core_x, core_y = hx - cap_cradle_corner_radius, hy - cap_cradle_corner_radius
    dx = max(x0 - (cx + core_x), (cx - core_x) - x1, 0.0)
    dy = max(y0 - (cy + core_y), (cy - core_y) - y1, 0.0)
    return math.hypot(dx, dy) - cap_cradle_corner_radius


def cap_cradle_room(name):
    """Least plan clearance around the plinth and its conduit edge passages."""
    room = []
    for cname, (x, y) in cap_conduits.items():
        gap = cap_cradle_circle_gap(name, x, y, cap_conduit_entry_relief_radius)
        # The plinth opens a full-height passage with this radial clearance.
        room.append((max(gap, cap_cradle_room_gap), f"the {cname} conduit passage"))
    for x, y in attachment_xy_positions:
        room.append((cap_cradle_circle_gap(name, x, y, head_cbore_radius),
                     "a clamp screw's counterbore"))
    for dname in deck_mounts:
        for x, y in deck_mount_xy(dname):
            room.append((cap_cradle_circle_gap(name, x, y, deck_lid_hole_radius(dname)),
                         f"the {dname} mount's lid hole"))
    cx, cy = cap_cradles[name].centre
    hx, hy = cap_cradle_half_extents(name)
    room.append((min(outer_shell_x_length / 2.0 - abs(cx) - hx,
                     outer_shell_y_length / 2.0 - abs(cy) - hy),
                 "the lid's own edge"))
    for other, station in cap_cradles.items():
        if other == name:
            continue
        ox, oy = station.centre
        ohx, ohy = cap_cradle_half_extents(other)
        # The rectangle includes the other plinth's rounded corners.
        room.append((cap_cradle_rectangle_gap(name, ox-ohx, ox+ohx, oy-ohy, oy+ohy),
                     f"the {other} plinth"))
    return min(room)


# --- Cap conduits ------------------------------------------------------------
#
# A conduit is one of the cup's own full-height columns carrying a THROUGH bore: liquid
# foam pours around its shank the way it pours around a deck mount's, the lid passes it,
# and a line runs up it from the shell's open top out onto the lid's outer face. The
# service bay stands on that face.
lldpe_tube_od = 6.35                         # the 1/4" line every fluid port on the core takes
cap_conduit_bore_radius = port_hole_radius   # the ⌀[7.5](PORT_HOLE_DIAMETER) every shell penetration takes
cap_conduit_wall = wall_thickness
cap_conduit_boss_radius = cap_conduit_bore_radius + cap_conduit_wall
cap_conduit_lid_slip = deck_mount_lid_slip   # per side, a standing column to the lid's clearance hole

# How far off its own bore axis a line leaves a conduit — a bore's `manifold_layout.FLAVOR_SKEW`.
# The LID'S HOLE IS COUNTERSUNK to this angle: the lip a leaning line crosses lies along it, and
# what the tube bears on there is a face. Everything under that countersink carries the bore on
# its own axis — the rest of the lid's plate and the column beneath it, one straight run.
# `_lines.CAP_BORE_SKEW` is bound to this name.
cap_conduit_entry_skew = 38.0
# The countersink's mouth on the lid's outer face — the bore opened at that angle through the
# one wall of plate the cone is sunk into: ⌀[10.63](ENTRY_RELIEF_D).
cap_conduit_entry_relief_radius = (
    cap_conduit_bore_radius
    + wall_and_floor_thickness * math.tan(math.radians(cap_conduit_entry_skew)))
# The relief stands inside the boss its own column carries, so `cap_conduit_wall_neck` and
# `cap_conduit_pair_neck` fence the cone where they fence the column. A wall of boss over a cone
# one wall deep puts that ceiling at [45°](ENTRY_SKEW_CEILING).
cap_conduit_entry_skew_ceiling = math.degrees(
    math.atan2(cap_conduit_wall, wall_and_floor_thickness))
# The mouth passes the tube's SECTION and not just its centreline: a ⌀[6.35](LLDPE_TUBE_OD) line
# crossing the outer face at that lean reads `r / cos(skew)` wide in the face's own plane.
state(
    "entry-passes-section", "The countersink's mouth passes the leaning tube's whole section",
    f"⌀{lldpe_tube_od / math.cos(math.radians(cap_conduit_entry_skew)):.2f} across the face",
    cap_conduit_entry_relief_radius >= (
        0.5 * lldpe_tube_od / math.cos(math.radians(cap_conduit_entry_skew)) - 1e-9),
    f"cap conduit entry: a ⌀{lldpe_tube_od:g} line leaning {cap_conduit_entry_skew:g}° reads "
    f"{lldpe_tube_od / math.cos(math.radians(cap_conduit_entry_skew)):.2f} mm across the lid's "
    f"face, over the ⌀{2.0 * cap_conduit_entry_relief_radius:.2f} the relief opens to")

# Per conduit: its centre in the CAP'S OWN frame. The cap installs spun a half turn about
# Z (`foam_assembly.spin_xy`), and a half turn is its own inverse — so a conduit that
# stands over a carbonator port at (x, y) in the shell's frame is authored at (−x, −y) here,
# and `foam_assembly.cap_conduit_station` turns it back.
#   A CONDUIT IS ONE END OF A LINE, and what the line does at the far end is what this table
# is for; `_internal_routes` draws every one of them and measures it against the shell. Seven
# stand here, and they answer to the carbonator and the two reservoirs. TWO ENTER THE
# CARBONATOR (water at the top plate, CO2 at the bottom) and one draws it; each reservoir is
# entered once at its cap and drawn once from its floor, by a dip tube down through that same
# cap. Every line that ENTERS one of the three arrives above that one's liquid and every line
# that LEAVES takes its lowest point, so nothing can enter and leave without crossing it. That
# is what the air-purge and clean-flush service modes run on.
#
#   water-in retains the carbonator's TOP-plate elbow and push-connect adapter.
# Its tube leaves on the fixed lateral clocking line and turns upward in
# the open body before the cup floor. The aligned cup and lid guide is straight.
# An accessible R18 arch above the lid joins the upward check elbow. The
# plain guide adds no socket or tube break; its cylindrical wall is 3 mm.
#   reservoir-a-fill and reservoir-b-fill, the two FILLS, stand over their own reservoirs rather
# than over a band, and have no run inside the shell at all: each is the column between a valve
# on the deck and the bore in the cap of the reservoir it fills, and that cap's own outer face is
# the last thing under this one, so the two features meet across the pour clearance over the
# reservoir and nothing else (`_internal_routes` draws and measures the stub). The bore it lands
# on opens into the reservoir's HEADSPACE, above the liquid and clear of the vent boss, the rod
# register and every screw boss — so what arrives falls into the cavity and can only leave by the
# draw. `reservoir_fill_conduit_xy` is the station, and `reservoir_fill_sides` is which
# reservoirs have one.
#   reservoir-a and reservoir-b, the two DRAWS, stand over their own reservoirs the same way, and
# the line that comes down one does not stop at the cap: it is its own dip tube, down the cap's
# draw bore to the reservoir's floor, so the column over it is the top of one straight drop and
# the internal route is that drop (`_internal_routes`). `reservoir_draw_conduit_xy` is the station.
#   carb-water-out — the carbonator's BOTTOM-PLATE +Y port, under the liquid, which is the
# carbonator's own drain and the dispense line's source. The elbow turns it laterally, it crosses
# under the carbonator inboard of the support ring, leaves the ring through the ring's OWN SLOT on
# this bore's column (`_port_cuts.water_outlet_ring_crossing_x` — no bore, and the four bearing
# segments stay whole), and climbs beside the coil clear of the port lane until the carbonator's top
# plate is under it. Only there does it step out onto the lane and into this bore. That climb is
# inboard because the CO2 owns the lane's own strip at the bottom of the shell.
#   Its X answers to THE COIL'S OWN TAIL: the climb runs
# in the annulus between the wrapped coil and a reservoir pocket's centreward arc, which is
# where the evaporator's inlet tail turns off its helix, and one bore of that annulus holds one
# run. The column stands clear of the tail's own, and far enough round that the ring crossing
# under it still falls inside one ring slot (`_port_cuts.water-outlet-slot`) — those two fences
# leave a 2.5 mm band and this is in it.
#   co2-in stands over the PORT LANE and its line runs DOWN it, the one conduit here that feeds
# rather than drains. It falls the shell's whole height, turns along the lane's floor and leans
# in to `_port_cuts.co2_inlet_xyz` through one of the support ring's slots, to land on the
# collet made up under the bottom plate's lane-side port. That port opens directly into the
# water column; gas rises to the headspace. Because the line arrives from above, it is laid
# down the lane before the top cap goes on.
#   ITS FALL IS THE ONLY RISER THE LANE CARRIES. A lane is one bore wide, so a riser in it is a
# wall to everything crossing that column, and the lane's other traffic all runs WEST at one
# storey each: the evaporator's inlet copper drops onto the lane beside the carbonator and takes it to
# its exit station (`_copper_ports.stations()`), and the carbonated water joins only once it is over
# the carbonator.
# The PRV shroud lies on the west lane and its vent leaves through the +Y flank.
#   WHERE THE LEAN CROSSES is the Carbonator SUPPORT RING's business, not this file's. The reach in
# from the lane to the bottom plate's port crosses the ring, and the ring is four bearing
# segments with four slots between them (`_support_ring`); a reach that misses a slot would have
# to be bored through a segment that carries the carbonator. `_port_cuts.co2-inlet-slot` is that
# fence, and `co2_lane_x` is the column whose lean lands inside slot four. Reservoir A stands on
# its pocket's floor, so the lean also keeps out of that pocket: struck from here it passes
# outboard of the pocket's centreward corner, and the ring's slots are clocked to meet it
# (`_support_ring.slot_clock`).
co2_lane_x = 48.0
# The cap guide follows the above-core gas chain. Its descent stays in the
# existing port lane and reaches the independently fixed support-ring approach
# below it; the carbonator port and its fitting retain their own stations.
co2_cap_x = _above_mounts.gas_guide_xy()[0]
# THE CARBONATED WATER IS SPLIT THE SAME WAY, at the other end of its line. Its CLIMB is
# pinned: it crosses the carbonator support ring at one of the ring's own four slots, so the column
# it rises on may not wander without notching a bearing segment, and the slot leaves it under
# 8 mm of travel — all of it under the same deck body its bore has to dodge. Its cap bore has
# no such tie: the run is already on the lane by then, and a jog ALONG a lane costs it nothing.
# So the ring reads this column and the appliance reads the bore's, and neither is the other's.
water_outlet_climb_x = -48.5
# The lower climb clears the inlet copper tail. Once over the tail's lead — it runs at
# `evap_tail_low_z`, and both lines are 1/4" OD, so one OD and a 2 mm foam hug clear it —
# the tube drifts along the coil standoff to the column where its climb and its lean out to
# the lane stand clear of reservoir B's −Y centerward pocket corner, so that pocket's wall is
# never opened. Every turn keeps the stock bend radius.
water_outlet_upper_climb_x = -35.0
water_outlet_drift_z = (evap_tail_low_z + lldpe_tube_od + 2.0, 140.0)
# THE TWO REED CABLES LEAVE BY THE LID, each up the channel its own column stands in. A reed
# channel is a cavity open from the shell's floor to its top face (`_reed_channels`), so the
# cable's way out is the slot it is already lying in and a bore in the cap over the mouth of it.
# The column drops into the channel at `assembly/cold-core.md` step 7 and the cap goes on after
# it, so what this bore passes is the cable and never the column. It stands on the cavity's own
# centre, one figure for both sides.
#   The bore is wider than the cavity and stands proud of it either side in X; what it owes is
# that it OPEN on the cavity rather than clip its corner, which is `_reed_channels` bound
# `reed-cable-conduit-stands-over-its-channel`.
reed_cable_conduit_x = reed_column_axis_x
reed_cable_conduit_y = level_rod_y


def reed_cable_conduit_xy(side):
    """One side's reed-cable conduit in the CAP's frame — the cap installs spun a half turn,
    so a bore over the shell-frame station `(x, y)` is authored at `(−x, −y)` here."""
    return (-side * reed_cable_conduit_x, -reed_cable_conduit_y)


cap_fluid_conduits = {
    "water-in": _above_mounts.cap_guide_xy("water-in", (86.2532889963965, 32.80179966121266)),
    "reservoir-a": reservoir_draw_conduit_xy(+1),
    "reservoir-b": _above_mounts.cap_guide_xy("B-draw", reservoir_draw_conduit_xy(-1)),
    "reservoir-a-fill": _above_mounts.cap_guide_xy("A-fill", reservoir_fill_conduit_xy(+1)),
    "reservoir-b-fill": _above_mounts.cap_guide_xy("B-fill", reservoir_fill_conduit_xy(-1)),
    "carb-water-out": _above_mounts.cap_guide_xy("carb-water-out", (52.2, -port_lane_mid_y)),
    "co2-in": _above_mounts.gas_guide_xy(),
}
# Cable passages use the same column and bore construction as fluid conduits.
# The reservoir passages open over their reed channels; the shared sensor
# passage opens into the main foam cavity.
cap_cable_floor_conduits = {
    "reed-cable-a": reed_cable_conduit_xy(+1),
    "reed-cable-b": reed_cable_conduit_xy(-1),
    # The potted temperature probes and earth lead leave
    # the main foam cavity through one shared passage, west of the pump.
    "sensor-cable": (-36.0, -74.0),
    # The carbonator's three reed conductors rise outside the coil on -Y.
    "carbonator-reeds": (0.0, 74.0),
}
cap_cable_conduits = {name: _above_mounts.cap_guide_xy(name, xy)
                      for name, xy in cap_cable_floor_conduits.items()}
cap_conduits = {**cap_fluid_conduits, **cap_cable_conduits}
# Water, soda, A-fill, both draws and gas have aligned straight cap entries.
# B-fill retains its separate lower reservoir entry and fitted cap link.
# Flexible cable entries retain their independently routed upper guides.
cap_conduit_floor_xy = {
    **cap_conduits,
    **cap_cable_floor_conduits,
    "water-in": _above_mounts.water_in_floor_xy(),
    "reservoir-b": reservoir_draw_conduit_xy(-1),
    "reservoir-a-fill": reservoir_fill_conduit_xy(+1),
    "reservoir-b-fill": reservoir_fill_conduit_xy(-1),
    "carb-water-out": cap_conduits["carb-water-out"],
}
cap_passive_guides = ()
cap_cable_guides = tuple(cap_cable_conduits)
# A full-height web closes a foam gap between two columns too narrow to pour; the bore axes and
# their 7.5 mm clear passages are independent of that stock. Every pair here stands the pour gap
# apart, so none is linked.
cap_conduit_links = ()
cap_conduit_link_width = 5.0

# Names pair the core's fill connections with their reservoir bores. Their
# upper guides can differ from the lower entries while the cap joins them.
_fill_conduits = {n for n in cap_conduits if n.endswith("-fill")}
_fill_wanted = {f"reservoir-{'ab'[s < 0]}-fill" for s in reservoir_fill_sides}
state(
    "fill-conduits-paired", "Every fill bore has a conduit over it and every conduit a bore",
    f"the cap's fills naming {sorted(_fill_wanted)}",
    _fill_conduits == _fill_wanted,
    f"reservoir fills: {sorted(_fill_conduits)} stand on the cap, but "
    f"`reservoir_fill_sides` cuts {reservoir_fill_sides} — a conduit with no bore under it "
    f"is a hole into a sealed pocket, and a bore with no conduit over it is a blind one")
# What a line arriving off-axis turns in: the band from a top-plate elbow's own lateral
# axis up to the cap's floor, against the rise a corner of 1/4" LLDPE takes.
carbonator_top_plate_z = wall_and_floor_thickness + carbonator_support_ring_height + carbonator_height
top_band_to_cap = foam_shell_outer_height - (carbonator_top_plate_z + hole_shift_from_edge)
# [25.4 mm](LLDPE_BEND_R) — the cold core's 4 × OD routing allowance. Actual drawn corner
# radii follow `_routing.stock_min`; the cured foam retains the internal routes.
# A bend radius alone does not specify the unloaded shape of an exposed tube.
lldpe_bend_radius = 4.0 * lldpe_tube_od


def cap_conduit_wall_neck(x, y):
    """What a conduit standing near the cup's PERIMETER leaves: `(mm, what)`.

    The same two states a pair of conduits has (`cap_conduit_pair_neck`), read against the
    wall instead of against another column. APART, with the pour gap between the column and
    the wall's inner face, so foam reaches down behind it. Or MERGED into the wall, and then
    what carries the joint is the material left OUTBOARD of the bore, which must be a wall
    thick — the column is no longer a post in the pour, it is a local thickening of the wall
    the bore runs up.
    A column that neither clears the wall nor reaches it stands tangent, which closes the
    same knife edge a tangent pair does."""
    to_outer = min(outer_shell_x_length / 2.0 - abs(x), outer_shell_y_length / 2.0 - abs(y))
    if to_outer - outer_shell_wall >= cap_conduit_boss_radius:
        return (to_outer - outer_shell_wall - cap_conduit_boss_radius,
                "the pour gap behind a standing column")
    return (to_outer - cap_conduit_bore_radius, "the wall left outboard of a merged bore")


_conduit_wall = bound(
    "cap-conduit-wall", "Every conduit column stands the pour gap off the wall or merges in",
    f"the pour gap apart or a {cap_conduit_wall:g} mm neck")
for _name in cap_conduits:
    _neck, _what = cap_conduit_wall_neck(*cap_conduits[_name])
    _want = deck_mount_cap_gap if _what.startswith("the pour") else cap_conduit_wall
    _conduit_wall(
        _neck >= _want - 1e-9,
        f"cap conduit {_name}: {_what} is {_neck:.3f} mm, under the {_want:g} mm it takes "
        f"— a column either stands the pour gap off the wall or merges into it")


def foam_cap_lid_pour_xy(top=False):
    """The top lid's fore-west pour station, or the bottom lid's: nearest the cap centreline
    with room beside mounts and plinths."""
    if top:
        return top_lid_pour_xy
    x = outer_shell_x_length / 2 - foam_cap_lid_hole_inset
    bands = []

    def fence(sx, sy, need):
        reach = need ** 2 - (x - sx) ** 2
        if reach > 0.0:
            half = math.sqrt(reach)
            bands.append((sy - half, sy + half))

    for name in deck_mounts:
        for sx, sy in deck_mount_xy(name):
            fence(sx, sy, foam_cap_lid_pour_radius + screw_clearance_radius
                  + deck_mount_cap_gap)
    for name, station in cap_cradles.items():
        assert math.isclose(station.yaw % 90.0, 0.0)
        cx, cy = station.centre
        hx, hy = cap_cradle_half_extents(name)
        core_x, core_y = hx - cap_cradle_corner_radius, hy - cap_cradle_corner_radius
        reach = foam_cap_lid_pour_radius + deck_mount_cap_gap + cap_cradle_corner_radius
        dx = max(abs(x - cx) - core_x, 0.0)
        if dx < reach:
            half = core_y + math.sqrt(reach * reach - dx * dx)
            bands.append((cy - half, cy + half))
    # MERGE FIRST, THEN STEP. Two stations near each other throw overlapping bands, and a
    # hole stepped off one lands inside the next — so the bands are run together into the
    # spans they actually close before the offset is read, and the answer is the nearer edge
    # of the one span that holds the centreline.
    merged: list = []
    for lo, hi in sorted(bands):
        if merged and lo <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], hi)
        else:
            merged.append([lo, hi])
    y = 0.0
    for lo, hi in merged:
        if lo < y < hi:
            y = lo if (y - lo) <= (hi - y) else hi
            break
    return (x, y)


def foam_cap_lid_vent_xy(top=False):
    """Both vent holes' centres in the lid — the −X corners, mirrored across y, where the
    pour hole is not and nothing stands. Air leaves by whichever is uppermost."""
    x = -(outer_shell_x_length / 2 - foam_cap_lid_hole_inset
          + (top_lid_vent_setback if top else 0.0))
    y = outer_shell_y_length / 2 - foam_cap_lid_hole_inset
    return ((x, y), (x, -y))


_mount_pour = bound(
    "deck-mount-pour", "Every deck mount's lid hole leaves a land under its screw head",
    f"{deck_mount_cap_gap:g} mm off the pour hole")
for _name in deck_mounts:
    _px, _py = foam_cap_lid_pour_xy(top=True)
    for _sx, _sy in deck_mount_xy(_name):
        _room = (math.hypot(_px - _sx, _py - _sy)
                 - foam_cap_lid_pour_radius - screw_clearance_radius)
        _mount_pour(
            _room >= deck_mount_cap_gap - 1e-9,
            f"deck mount {_name}: its lid clearance hole at ({_sx:g}, {_sy:g}) stands "
            f"{_room:.3f} mm off the pour hole, inside the {deck_mount_cap_gap:g} mm that "
            f"leaves a land under the screw's head")


# Clearances are read on the complete plinth outline. Its conduit passages are
# cut separately; each socket keeps its complete surrounding wall beside them.
_cradle_room = bound(
    "cradle-room", "Every plinth clears the other openings on the lid",
    f"{cap_cradle_room_gap:g} mm off the nearest")
_cradle_pour = bound(
    "cradle-pour", "Every plinth leaves a land beside the pour hole",
    f"{cap_cradle_room_gap:g} mm off the pour hole")
for _name in cap_cradles:
    _room, _what = cap_cradle_room(_name)
    _cradle_room(_room >= cap_cradle_room_gap - 1e-9,
                 f"valve plinth {_name}: {_room:.3f} mm off {_what}")
    _room = cap_cradle_circle_gap(_name, *foam_cap_lid_pour_xy(top=True),
                                  foam_cap_lid_pour_radius)
    _cradle_pour(_room >= cap_cradle_room_gap - 1e-9,
                 f"valve plinth {_name}: {_room:.3f} mm off the pour hole")
    for _sx, _sy in cap_cradle_xy(_name):
        for _hx, _hy in cap_conduits.values():
            _room = (math.hypot(_sx - _hx, _sy - _hy)
                     - cap_cradle_boss_radius - cap_conduit_entry_relief_radius)
            _cradle_room(_room >= cap_cradle_room_gap - 1e-9,
                         f"valve plinth {_name}: conduit passage preserves each socket wall")


# --- Body and tube cradles on the lid's outer face ---------------------------
#
# The single water check's fixed barrel rests in a round cradle. A tie through
# the channel beneath it prevents lift-out and leaves both collets accessible.
# The pump and check share this lid; their tube spans no enclosure joint.
# Tube cradles use the existing removable anchor caps.
#
# Centres and bore radii are in the cap frame. A stated `over_face` holds the
# installed axis at its required height; otherwise the floor and channel stock
# determine it. `anchor_rows` compares the bore and the sections under its span.
CapAnchor = namedtuple("CapAnchor", "centre seat_r over_face along closure")
CapAnchor.__new__.__defaults__ = (None, "x", "tie")
cap_anchors = {
    #                             centre         seat_r                  over_face along closure
    # The tie sits on the fixed barrel, clear of both operating collets.
    "discharge-chain": CapAnchor(_above_mounts.check_anchor()[0],
                                  _above_mounts.check_anchor()[1] + fits.slip,
                                  _above_mounts.check_anchor()[2]),
}

# What a zip tie is, wherever one is cut for on this cap. `enclosure.tie_w` is the same
# fastener stated for the other box; `enclosure_assembly.check_tie_vocabulary` holds the two
# against each other.
# `cap_anchor_tie_loop` gives the nominal water-check/body loop recorded in
# foam-cap/above-core-native-review.json.
# Its 2.5 mm band crosses only the fixed barrel, clear of both moving collets.
cap_anchor_tie_w = 2.5              # the 18 lb zip tie, across its width — 0.1"
cap_anchor_cav_buffer = 2.0 * fits.slip
cap_anchor_cav_w = cap_anchor_tie_w + cap_anchor_cav_buffer
# Solid either side of the channel, ALONG the run: what the rib keeps of itself at each end.
cap_anchor_cav_wall = 3.0
# ITS LENGTH ALONG THE BODY IS ITS CHANNEL'S. One zip tie crosses one anchor, so the rib is that
# zip tie's cavity with `cap_anchor_cav_wall` of itself at each end of it.
cap_anchor_len = cap_anchor_cav_w + 2.0 * cap_anchor_cav_wall
# One wall of material under the bore's floor, and one more from there down to the lid's face —
# the height the rib's two ends stand, and the zip tie's channel between them. `valve_seat`'s is
# the wall this face already carries.
cap_anchor_wall = cap_cradle_wall
# Leave the supported-surface allowance at the roof, above the flat lid floor.
cap_anchor_channel_height = cap_anchor_wall + fits.supported_surface


def cap_anchor_axis_over_face(name):
    """How far the seated body's AXIS stands over the lid's outer face.

    Three layers of the rib, read from the face up: the channel the zip tie is pushed through, one
    `cap_anchor_channel_height`; the material under the bore, one `cap_anchor_wall`; then the bore's own radius. A body
    seated lower than that sits on its own zip tie. A capped rib has no channel, so its two
    layers are the material under the bore and the bore.

    A row that STATES its own height is one whose body cannot move to meet the rib, so the rib is
    built up to it. What it must not do is come out under its layers, which is the same floor a
    seated body has."""
    row = cap_anchors[name]
    stated = row.over_face
    least = row.seat_r + cap_anchor_wall + (0.0 if row.closure == "cap" else cap_anchor_channel_height)
    if stated is None:
        return least
    if stated < least - 1e-9:
        raise ValueError(
            f"cap_anchor_axis_over_face: {name} states {stated:.3f} mm over the lid's face and "
            f"the rib's own layers come to {least:.3f}. A seat lower than that stands the body on "
            f"the lid or on its own zip tie.")
    return stated


def cap_anchor_tie_loop(name):
    """The shortest zip tie that closes round the seated body and the rib together.

    A zip tie turns INSIDE the channel, so what it reaches round is the body with the rib's own
    back behind it — the convex perimeter of that pair, and not of the lid the rib stands on.
    Read on the bore rather than on the body, which is the section this part knows.

    The hull uses the rib's actual height beneath the stated axis, with the bore above it: its floor, its two flanks,
    a tangent from each top corner onto the bore, and the arc between the two tangent points."""
    r = cap_anchors[name].seat_r
    if name == 'discharge-chain':
        data = _above_mounts.check_support_datums()
        w = data['half_width_mm']
        h = data['centre_world_mm'][2]-data['tie_route_z_mm']
        # Convex loop around the circle and the lower-east rectangular
        # quarter bearing: bottom, east face, two tangents and retained arc.
        return (w+h+math.sqrt(w*w-r*r)+math.sqrt(h*h-r*r)
                +r*(1.5*math.pi-math.acos(r/w)-math.acos(r/h)))
    else:
        w = r + cap_anchor_wall
        h = cap_anchor_axis_over_face(name) - cap_anchor_channel_height
    return 2.0 * w + 2.0 * h + 2.0 * math.sqrt(w * w - r * r) + r * (math.pi - 2.0 * math.acos(r / w))


def cap_anchor_slotted(name):
    """Whether a capped rib's lid gives the cap's wings their slots: its face standing inside the
    wings' reach (`_anchor_cap_interface.wing_room`)."""
    return (cap_anchors[name].closure == "cap"
            and cap_anchor_axis_over_face(name) < _anchor_cap.SLOT_TOP - _anchor_cap.HEADROOM / 2.0)


def cap_anchor_room(name):
    """The least room this rib leaves to anything else opening on the lid's outer face:
    `(mm, what)` — a conduit's entry countersink, a clamp screw's counterbore, a deck mount's
    lid hole, a cradle boss, the pour hole, a vent, the lid's own edge.

    Read on the rib's own rectangle, which is the whole of it: its length down the row's own
    axis and one `reach` either side of the centre across it — a tied rib's `cap_anchor_len`, a
    capped rib's `_anchor_cap_interface.RIB_LEN` and, where the lid gives the cap's wings their
    slots, the slots' outer walls."""
    row = cap_anchors[name]
    (cx, cy) = row.centre
    if row.closure == "cap":
        length = _anchor_cap.RIB_LEN
        reach = _anchor_cap.RIB_R + (_anchor_cap.SLOT_W if cap_anchor_slotted(name) else 0.0)
    else:
        length, reach = cap_anchor_len, row.seat_r + cap_anchor_wall
    along, across = (length / 2.0, reach) if row.along == "x" else (reach, length / 2.0)
    x0, x1 = cx - along, cx + along
    y0, y1 = cy - across, cy + across

    def off(px, py, r):
        """How far a disc of radius `r` at (px, py) stands off the rib's rectangle."""
        dx = max(x0 - px, 0.0, px - x1)
        dy = max(y0 - py, 0.0, py - y1)
        return math.hypot(dx, dy) - r

    room = []
    for cname, (bx, by) in cap_conduits.items():
        room.append((off(bx, by, cap_conduit_entry_relief_radius),
                     f"the {cname} conduit's entry"))
    for bx, by in attachment_xy_positions:
        room.append((off(bx, by, head_cbore_radius), "a clamp screw's counterbore"))
    for dname in deck_mounts:
        for dx, dy in deck_mount_xy(dname):
            room.append((off(dx, dy, deck_lid_hole_radius(dname)),
                         f"the {dname} mount's lid hole"))
    for vname in cap_cradles:
        room.append((cap_cradle_rectangle_gap(vname, x0, x1, y0, y1),
                     f"the {vname} plinth"))
    room.append((off(*foam_cap_lid_pour_xy(top=True), foam_cap_lid_pour_radius), "the pour hole"))
    for hx, hy in foam_cap_lid_vent_xy(top=True):
        room.append((off(hx, hy, foam_cap_lid_vent_radius), "a vent"))
    room.append((min(outer_shell_x_length / 2.0 - abs(x0),
                     outer_shell_x_length / 2.0 - abs(x1),
                     outer_shell_y_length / 2.0 - abs(y0),
                     outer_shell_y_length / 2.0 - abs(y1)), "the lid's own edge"))
    return min(room)


# The rib stands on a plate it only touches, so everything the face opens has to be somewhere
# else: a rib over a hole is a channel with no floor and a zip tie that falls into the cup.
_anchor_room = bound(
    "anchor-room", "Every chain anchor stands its room off everything else the face opens",
    f"{cap_cradle_room_gap:g} mm off the nearest")
for _name in cap_anchors:
    _room, _what = cap_anchor_room(_name)
    _anchor_room(
        _room >= cap_cradle_room_gap - 1e-9,
        f"chain anchor {_name}: the rib stands {_room:.3f} mm off {_what}, inside the "
        f"{cap_cradle_room_gap:g} mm this face keeps between two things it opens")


# --- the anchors that grip SIDEWAYS -----------------------------------------
#
# The ribs above open at the sky: a run is laid down into the trough and the zip tie comes up round
# it. A run laid ACROSS this lid cannot be held that way. `water-3` crosses the machine along the
# cap's own Y, one lane off the core's front face, and an upward trough on that line would open
# its mouth at the funnel — a tube dropped into it would come down through the storey the
# source valves fill.
#
# SO THIS ONE STANDS ON THE STEP AND GRIPS THE RUN FROM BEHIND. A post, its FORWARD face the run's
# own axis plane, a half pipe cut into that face, and the tube pushed in horizontally.
#
# THE POST GROWS ALONG THE CAP'S OWN −X, which the machine lays on world +Y: the pipe's axis
# plane is its forward face and everything behind it is between the run and the core the run is
# assembled onto. `centre` is that axis plane, so the post is on the far side of it from the room.
#
# THE TIE'S TUNNEL IS A WINDOW CUT THROUGH THE POST, front to back, hung one wall under the pipe.
# The tie goes through the window, out the front, round the tube and back over the post's crown,
# and buckles in the channel down its back — so the loop closes on the tube, and every millimetre
# the window stands off the pipe is a millimetre added to that loop and taken out of the post.
# Each station's `depth` runs aft from its front face along the cap's −X.
SideAnchor = namedtuple("SideAnchor", "centre over_face seat_r axis_off depth")

cap_side_wall = cap_anchor_wall           # every solid section in the post
cap_side_len = cap_anchor_len             # along the run, one tie's tunnel and its two flanks
cap_side_cav_w = cap_anchor_cav_w         # the tunnel's width, on the zip tie and its slip
cap_side_flank = (cap_side_len - cap_side_cav_w) / 2.0
# The 18 lb zip tie through its thickness — `enclosure.tie_t`, and the one figure the window
# has to leave standing.
cap_side_tie_t = 1.0
# WHAT THE WINDOW IS NOT IS THE WHOLE COLUMN UNDER THE PIPE. The up-opening ribs take their
# channel as the remainder between two feet, and a post that did the same would give the whole of
# its height to one: this post stands as tall as the run it grips, so on a high crossing the
# remainder is two `cap_side_flank` blades running the post's length with nothing but the roof
# joining them — a pair of towers to print where the section wants to be one block.
#   So the window is a STATED height and the rest of that column is the post's own stock, which
# is `enclosure.tube_anchor_cavity_depth`'s bargain read on this face: a 1 mm zip tie needs its
# own thickness and routing air, not every millimetre between a low run and a tall post.
cap_side_cav_h = cap_side_wall
# And a post whose pipe runs low keeps all the air it has. Capping a window that is already
# compact buys a fraction of channel back as a floor thinner than the room the cavity is cut
# with — `enclosure.tube_anchor_backing_min` again, and the same figure.
cap_side_cav_backing_min = 1.0  # printable stock, independent of tie clearance
# The tie's own channel down the post's back face, so the buckle seats and the zip tie cannot walk
# along the run.
cap_side_back_relief = 1.2
# The bore and the rear tie channel retain one nominal wall between them. The
# zip tie pulls the tube into that section; this geometric floor does not qualify
# its retention load or endurance.
cap_side_web = cap_side_wall

cap_side_anchors = {}


def cap_side_axis_y(name) -> float:
    """The pipe's axis in the cap's own X — the post's front face, stood `axis_off` forward of
    it. The cap's +X is the world's forward, so the axis is at the greater figure."""
    a = cap_side_anchors[name]
    return a.centre[0] + a.axis_off


def cap_side_wrap_deg(name) -> float:
    """How much of the tube's own circle the seat closes on, in degrees. A pipe on the face
    itself takes half; one stood proud of it takes less, and what makes up the difference is the
    tie."""
    a = cap_side_anchors[name]
    return 2.0 * math.degrees(math.acos(a.axis_off / a.seat_r))


def cap_side_tunnel_roof(name) -> float:
    """The tunnel's roof over the lid's outer face — one wall under the pipe, which is the whole
    of the column the post has to hand the zip tie."""
    a = cap_side_anchors[name]
    return a.over_face - a.seat_r - cap_side_wall


def cap_side_tunnel_h(name) -> float:
    """The tunnel's own height, hung under that roof.

    A post with the column to spend gives the window `cap_side_cav_h` of it and stands its own
    stock under the rest, so what prints below the pipe is one block and not two blades. A post
    whose pipe runs low keeps all the air it has, since a window capped there would trade the
    channel for a floor thinner than `cap_side_cav_backing_min`."""
    roof = cap_side_tunnel_roof(name)
    if roof - cap_side_cav_h >= cap_side_cav_backing_min - 1e-9:
        return cap_side_cav_h
    return roof


def cap_side_anchor_height(name) -> float:
    """How tall the post stands over the lid's outer face — the axis, the pipe's own radius over
    it, and one wall over that."""
    a = cap_side_anchors[name]
    return a.over_face + a.seat_r + fits.supported_surface + cap_side_wall


def cap_side_anchor_holds(name) -> None:
    """The post's own stack, against what the run's height gives it.

    A run laid closer to the lid's face than the pipe, one wall and the zip tie together is a run
    with no tie path under it, and the post would stand on its own zip tie."""
    a = cap_side_anchors[name]
    roof = cap_side_tunnel_roof(name)
    if roof < cap_side_tie_t - 1e-9:
        raise ValueError(
            f"cap_side_anchor_holds: {name} runs {a.over_face:.3f} mm over the lid's face; the "
            f"pipe takes {a.seat_r:.3f} of that and one wall {cap_side_wall:.3f} more, leaving "
            f"{roof:.3f} mm under it where the zip tie is {cap_side_tie_t:g} thick. What gives "
            f"way here is the run's own lane, not the lid: route it further off that face.")
    # The bore eats forward from the front face and the tie's channel eats back from the rear one,
    # and they meet over the pipe: what is left between them is the whole of the web, so the
    # relief comes off the reading the same way the seat does.
    web = a.depth + a.axis_off - a.seat_r - cap_side_back_relief
    if web < cap_side_web - 1e-9:
        raise ValueError(
            f"cap_side_anchor_holds: the post runs {a.depth:.3f} mm back from its face; "
            f"the pipe takes {a.seat_r - a.axis_off:.3f} of that and the tie's channel "
            f"{cap_side_back_relief:g} more, leaving a web of {web:.3f} where this face wants "
            f"{cap_side_web:g}. What caps the depth is the body behind the post, so what gives "
            f"is the pipe or the lane — not the web.")


def cap_side_anchor_tie_loop(name) -> float:
    """The shortest tie that closes round the tube and the post's own back together.

    A tie turns INSIDE the window, so what it reaches round is everything ABOVE the window: the
    tube, and the block of post between the window's roof and the post's own crown. That crown
    is one wall PROUD OF THE TUBE'S TOP, so the loop clears the post there and not the pipe, and
    the figure is not the up-opening ribs' — theirs stops on the axis plane.
      The hull is that block's rectangle with the pipe bulging out of one face: the window's own
    floor, the crown, the back face between them, a tangent from each front corner onto the pipe,
    and the arc the two tangent points leave. Read on the post's own faces, so the back channel's
    relief is slack the tie does not have to reach round.
      IT IS THE WINDOW'S HEIGHT THAT SETS IT, which is why the window is stated rather than left:
    a window taken as the remainder under the pipe carries the loop up with the post."""
    a = cap_side_anchors[name]
    w = a.seat_r + cap_side_wall
    tun_h = cap_side_tunnel_h(name)
    axis = tun_h + w                              # the pipe's axis over the window's floor
    crown = tun_h + 2.0 * w                       # and the post's crown over that same floor
    d_lo = math.hypot(a.axis_off, axis)           # the two front corners' reach to the axis
    d_hi = math.hypot(a.axis_off, crown - axis)
    sweep = (math.atan2(crown - axis, -a.axis_off)
             - math.atan2(-axis, -a.axis_off)) % (2.0 * math.pi)
    return (2.0 * a.depth + crown
            + math.sqrt(d_lo * d_lo - a.seat_r * a.seat_r)
            + math.sqrt(d_hi * d_hi - a.seat_r * a.seat_r)
            + a.seat_r * (sweep - math.acos(a.seat_r / d_lo) - math.acos(a.seat_r / d_hi)))


def cap_side_anchor_room(name):
    """The least room this post leaves to anything else opening on the lid's outer face:
    `(mm, what)` — a clamp screw's counterbore, a conduit's entry countersink, a deck mount's
    lid hole, a cradle boss, the pour hole, a vent, the up-opening ribs.

    A POST IS THE ONE THING ON THIS FACE THAT STANDS ON IT WITHOUT BEING CUT INTO IT, and that
    is why it needs saying. Every other body here opens THROUGH the plate, so two of them
    fouling shows up as a hole in the wrong shape; a post fouling one shows up as nothing at
    all — the lid comes off the plate correct and the screw under the post cannot be driven.
    `cap_anchor_room` reads the up-opening ribs the same way and this is its twin, on the
    family that stands on the cap's side instead.

    Read on the post's own rectangle, which is the whole of its footing. `centre` is NOT the
    middle of it in both axes: in the cap's X it is the post's FRONT FACE, the plane
    `axis_off` stands the pipe forward of, and the block runs the station's `depth` aft of that.
    In the cap's Y it is the middle, and the block is `cap_side_len` long about it."""
    a = cap_side_anchors[name]
    (cx, cy) = a.centre
    x0, x1 = cx - a.depth, cx
    y0, y1 = cy - cap_side_len / 2.0, cy + cap_side_len / 2.0

    def off(px, py, r):
        """How far a disc of radius `r` at (px, py) stands off the post's rectangle."""
        dx = max(x0 - px, 0.0, px - x1)
        dy = max(y0 - py, 0.0, py - y1)
        return math.hypot(dx, dy) - r

    room = []
    for bx, by in attachment_xy_positions:
        room.append((off(bx, by, head_cbore_radius), "a clamp screw's counterbore"))
    for cname, (bx, by) in cap_conduits.items():
        room.append((off(bx, by, cap_conduit_entry_relief_radius),
                     f"the {cname} conduit's entry"))
    for dname in deck_mounts:
        for dx, dy in deck_mount_xy(dname):
            room.append((off(dx, dy, deck_lid_hole_radius(dname)),
                         f"the {dname} mount's lid hole"))
    for vname in cap_cradles:
        room.append((cap_cradle_rectangle_gap(vname, x0, x1, y0, y1),
                     f"the {vname} plinth"))
    for aname in cap_anchors:
        room.append((off(*cap_anchors[aname].centre,
                         cap_anchors[aname].seat_r + cap_anchor_wall),
                     f"the {aname} rib"))
    room.append((off(*foam_cap_lid_pour_xy(top=True), foam_cap_lid_pour_radius), "the pour hole"))
    for hx, hy in foam_cap_lid_vent_xy(top=True):
        room.append((off(hx, hy, foam_cap_lid_vent_radius), "a vent"))
    return min(room)


_side_anchor_room = bound(
    "cap-side-anchor-room", "Every side post stands clear of what the lid's face opens",
    f"{cap_cradle_room_gap:g} mm off the nearest")
for _name in cap_side_anchors:
    _room, _what = cap_side_anchor_room(_name)
    _side_anchor_room(
        _room >= cap_cradle_room_gap - 1e-9,
        f"cap side anchor {_name}: its post stands {_room:.3f} mm off {_what}, inside the "
        f"{cap_cradle_room_gap:g} mm this face keeps between two things it opens — a post over "
        f"one of them is a body no plate reads as fouled")


def cap_conduit_pair_neck(a, b):
    """What a PAIR of conduits leaves between them: `(mm, what)`.

    A pair is one of two things and never a third. APART, with at least the pour gap
    between the two columns, so foam reaches down between them. Or MERGED, the two bores
    standing nearer than a boss diameter and their columns fusing into one post — and then
    what matters is the NECK the lens leaves, which carries the joint and must be a wall
    thick. What neither may be is tangent: two circles meeting near a point close a knife
    edge that prints as a void and holds no load."""
    pair = frozenset((tuple(a), tuple(b)))
    for first, second in cap_conduit_links:
        if pair == frozenset((cap_conduits[first], cap_conduits[second])):
            return (cap_conduit_link_width, "the connecting web")
    r = cap_conduit_boss_radius
    d = math.hypot(a[0] - b[0], a[1] - b[1])
    if d >= 2.0 * r:
        return (d - 2.0 * r, "the pour gap between two standing columns")
    return (2.0 * math.sqrt(max(r * r - (d / 2.0) ** 2, 0.0)), "the neck their lens leaves")


_pair_neck = bound(
    "cap-conduit-pair", "Every pair of conduits stands apart or merges on a neck, never tangent",
    f"the pour gap apart or a {cap_conduit_wall:g} mm neck")
for _a, _b in itertools.combinations(sorted(cap_conduits), 2):
    _neck, _what = cap_conduit_pair_neck(cap_conduits[_a], cap_conduits[_b])
    _want = (deck_mount_cap_gap
             if _what.startswith("the pour") else cap_conduit_wall)
    _pair_neck(
        _neck >= _want - 1e-9,
        f"cap conduits {_a} and {_b}: {_what} is {_neck:.3f} mm, under the "
        f"{_want:g} mm it takes — a pair either stands the pour gap apart or merges on a "
        f"neck a wall thick")


def cap_conduit_shell_xy(name):
    """One cap conduit's station in the SHELL's own frame — where the line coming down it
    lands in the shell, which is the frame every band and lane in this file is stated in.

    The cap installs spun a half turn about Z (`foam_assembly.spin_xy`) and a half turn is
    its own inverse, so this is the authored pair negated. Everything that has to meet a
    conduit from BELOW reads it here."""
    x, y = cap_conduits[name]
    return (-x, -y)


# The face a cap conduit opens on, as a direction: the TOP cap's own +Z.
cap_conduit_axis = (0.0, 0.0, 1.0)


def cap_conduit_station(name):
    """One cap conduit's mouth in the CAP'S OWN frame: `(position, outward axis)`, with Z
    left at the lid's outer face for whoever seats the stack to carry."""
    x, y = cap_conduits[name]
    return ((x, y, 0.0), cap_conduit_axis)



def make_box(x_range, y_range, z_range):
    """Axis-aligned box from world-coordinate ranges in each axis."""
    x_min, x_max = min(x_range), max(x_range)
    y_min, y_max = min(y_range), max(y_range)
    z_min, z_max = min(z_range), max(z_range)
    return (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=z_min)
        .moveTo(((x_min + x_max) / 2, (y_min + y_max) / 2))
        .rect(x_max - x_min, y_max - y_min)
        .extrude(z_max - z_min)
        .unwrap()
    )


def build_z_axis_hole_punch(
    *,
    origin=(0, 0, 0),
    hole_punch_radius,
    hole_punch_height=40,
):
    """Z-axis ⌀ × height cylindrical cut, centered at `origin`'s X/Y and
    starting at `origin`'s Z, extruded in +Z."""
    x, y, z = origin
    return (
        cq.Workplane(xy_plane_z_up)
        .workplane(origin=(x, y, 0), offset=z)
        .circle(hole_punch_radius)
        .extrude(hole_punch_height)
    )


if __name__ == "__main__":
    sys.path.insert(
        0,
        str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
    )
    from docgen import substitute_py_comments

    variables = {
        "WALL_AND_FLOOR_THICKNESS": f"{wall_and_floor_thickness:.4g} mm",
        "COIL_RADIAL_CLEARANCE": f"{coil_radial_clearance:.4g} mm",
        "ABOVE_TANK_ELBOWS_HEIGHT": f"{above_carbonator_elbows_height:.4g} mm",
        "BELOW_TANK_ELBOWS_HEIGHT": f"{below_carbonator_elbows_height:.4g} mm",
        "PORT_HOLE_DIAMETER": f"{port_hole_radius * 2:.4g}",
        "SCREW_CLEARANCE_DIAMETER": f"{screw_clearance_radius * 2:.4g}",
        "INSERT_POCKET_DIAMETER": f"{insert_pocket_radius * 2:.4g}",
        "SCREW_BOSS_SIZE": f"{screw_boss_size:.4g} × {screw_boss_size:.4g} mm",
        "SCREW_HEAD_H": f"{screw_head_height:.4g} mm",
        "HEAD_PAD_H": f"{head_pad_height:.4g} mm",
        "FOAM_CAP_LID_H": f"{foam_cap_lid_height:.4g} mm",
        "HEAD_CBORE_D": f"{head_cbore_radius * 2:.4g} mm",
        "CAP_SCREW_L": f"{cap_screw_length:.4g}",
        "DECK_MOUNT_CAP_GAP": f"{deck_mount_cap_gap:.4g} mm",
        "CARBONATOR_PORT_PITCH": f"{2 * carbonator_port_offset / 25.4:.4g}\"",
        "CARBONATOR_PORT_OFFSET": f"{carbonator_port_offset:.4g} mm",
        "LLDPE_BEND_R": f"{lldpe_bend_radius:.4g} mm",
        "FORWARD_BAND": f"{forward_band_width:.4g} mm",
        "LLDPE_TUBE_OD": f"{lldpe_tube_od:.4g}",
        "ENTRY_RELIEF_D": f"{2.0 * cap_conduit_entry_relief_radius:.4g}",
        "ENTRY_SKEW_CEILING": f"{cap_conduit_entry_skew_ceiling:.4g}°",
        "ANCHOR_LOOP": f"{cap_anchor_tie_loop('discharge-chain'):.3g} mm",
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
    )
    print("-> _cold_core_interface.py (self)")
