"""Shared interface for the cold-core's geometry modules — dimensional
constants and hole-punch helpers that every sibling part (foam shell,
foam cap stack, reservoir, copper plugs, coil mandrel) needs to stay
in sync against.

The constants carry claims about each other — a screw long enough for its insert, a lane wide
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

import cadquery as cq

from world_workplane import xy_plane_z_up, xz_plane_y_up, xz_plane_y_down, WorldWorkplane
from _stated_bounds import bound, state


# All structural walls and floors are [2 mm](WALL_AND_FLOOR_THICKNESS) PETG.
wall_and_floor_thickness = 2.0
hole_shift_from_edge = 15.0


# The cold cylinder + its evaporator coil. [7 mm](COIL_RADIAL_CLEARANCE) of
# radial clearance out from the cylinder OD holds the 1/4" ACR copper coil +
# thermal tape; the tank support ring cradles the tank rim at this envelope.
tank_outer_radius = 63.5
coil_radial_clearance = 7.0
tank_coil_envelope_radius = tank_outer_radius + coil_radial_clearance

# Foam blanket around the cylinder — the pour-foam standoff measured from the
# cylinder OD out to the reservoir's tank-facing wall, uniform around the wrapped
# arc (that wall is a concentric arc), with the coil embedded in its inner slice
# (so it must be >= coil_radial_clearance). This VALUE is not a thermal target:
# it is set so the reservoir, shifted out by it, keeps the 283 mm outer width
# (outer_shell_x_length below) with its reed channel butted against the outer
# wall — i.e. the foam that used to sit outboard of the reed moved to the
# cylinder side. The reservoir-facing (cavity) face is one wall further out.
foam_thickness_around_cylinder = 15.0
pocket_centerward_arc_outer_radius = (
    tank_outer_radius + foam_thickness_around_cylinder + wall_and_floor_thickness
)

# Foam-shell outer height. Tank height + [30 mm](ABOVE_TANK_ELBOWS_HEIGHT) above for top-side elbow
# fittings + [30 mm](BELOW_TANK_ELBOWS_HEIGHT) below for bottom-side elbow fittings + 1 mm
# wall-thickness compensation.
tank_height = 152.4
below_tank_elbows_height = 30.0
above_tank_elbows_height = 30.0
foam_shell_outer_height = (
    tank_height + below_tank_elbows_height + above_tank_elbows_height + 1.0
)

tank_support_ring_height = 30.0
support_ring_radial_width = 9.0

# ⌀[6.5](PORT_HOLE_DIAMETER) — the project-wide standard for small through-shell features
# (water outlet, reservoir bulkheads, reed cable holes, CO2 tube clearance).
port_hole_radius = 3.25

# Reed-channel cavity depth (radial, out from the bag-pocket far wall). The reed
# column drops into this cavity; the outer_shell X width is sized so the cavity +
# its wall butt the outer shell wall (see outer_shell_x_length). Consumed by
# _reed_channels.py too.
reed_x_depth = 6.0

# WHERE THE LEVEL SENSOR STANDS along the reservoir — the float rod inside
# (`reservoir.rod_position_y`) and the reed column outside (`_reed_channels.reed_y_center`),
# which are ONE station and not two: a reed reads the float's magnet across the pocket wall
# and nothing else, so the two cannot drift apart (`reservoir/level-sensing.md` carries the
# bench-measured magnet-to-reed path). The pair rides the reservoir's +Y half, clear of the
# bulkhead exit on the −Y front, and the donut has its whole travel clear of both cavity
# walls anywhere along that half.
#   What pins it HERE is the FORWARD BAND overhead: the reed channel's envelope and
# reservoir B's draw conduit both stand in that band's 8 mm, on the same face of the shell,
# and a ⌀6.5 bore and a reed cavity cannot share one lane. The conduit takes the lane its
# own deck wants and the reed column steps off it.
level_rod_y = 32.5

# Bag pocket. Width and depth are the reservoir's own dimensions — sized to the
# flavor charge it carries (each usable window, Reed 1 low → Reed 4 full over
# 135 mm of float travel, holds 2 × SodaStream 0.44 L bottles). They are NOT tied
# to the tank geometry: the ±Y width stands on its own so growing the cylinder's
# foam blanket slides the pocket outward without resizing the reservoir.
bag_pocket_width = 145.0
bag_pocket_depth = 49 + 2 * wall_and_floor_thickness
bag_pocket_far_inner_x = (
    pocket_centerward_arc_outer_radius + bag_pocket_depth - 2 * wall_and_floor_thickness
)
bag_pocket_y_inner_max = bag_pocket_width / 2 - wall_and_floor_thickness
bag_pocket_floor_top_z = wall_and_floor_thickness
bag_pocket_walls_top_z = foam_shell_outer_height

# Matches the reservoir's outer +X × ±Y fillet (R=6) with reservoir_clearance
# on top, so the reservoir's outer arc slides into a snugly-mated arc on
# the pocket's inner corner with uniform clearance.
bag_pocket_corner_inner_radius = 6.5

reservoir_clearance = 0.5
reservoir_floor_thickness = 3.0
# Bulkhead vertical scheme. The PureSec mounts elbow-DOWN: the integral 90°
# elbow + its dry-side flange + the below-side printed-TPU washer hang below
# the reservoir's flat exterior floor bottom (the wet-side primary seal is a
# purchased silicone flat washer in a wet/cavity-side counterbore, compressed
# by the nut on the wet/cavity side, above; the dry-side TPU washer is the
# secondary seal under the elbow flange). The reservoir's weight rides on the
# corner support posts; the
# elbow's lowest point clears the bag-pocket floor by bulkhead_floor_clearance
# and bears no load. The flavor-line wall holes and the reed cable holes both
# pin their Z to bulkhead_elbow_exit_z (the elbow's lateral-port center), so
# the tube and the cable run level out of the open pocket.
bulkhead_floor_clearance = 1.0  # gap from the lowest bulkhead hardware down to the bag-pocket floor — non-load-bearing
bulkhead_elbow_bottom_z = bag_pocket_floor_top_z + bulkhead_floor_clearance
bulkhead_elbow_exit_z = bulkhead_elbow_bottom_z + 3.0  # elbow's lateral-PTC-port Z center
reservoir_bulkhead_port_x = (bag_pocket_far_inner_x + pocket_centerward_arc_outer_radius) / 2
# Y of a pocket-wall pass-through, 10 mm inboard of the bag pocket's ±Y wall outer
# face. Reservoir A's draw and BOTH reed cables cross the −Y wall at this y, onto
# the port lane; reservoir B's draw crosses the +Y wall at its mirror, onto the west
# lane. Which wall a line takes is which lane its cap conduit stands over.
reservoir_bulkhead_port_y = -(bag_pocket_width / 2 - 10)

# The reservoir's SECOND mouth, in its own cap. The draw leaves by the bulkhead
# at the bottom of the wet V; the fill arrives up here, above the liquid, so the
# two never share a mouth and everything entering has to cross the cavity to
# leave by the trough. The cap reads its station (`reservoir.build_reservoir_cap`)
# and so does the conduit standing over it (`cap_conduits`) — in two different
# frames, neither part seeing the other, so `reservoir_fill_conduit_xy` is the
# whole of what holds them together and the assertion under `cap_conduits` is
# what enforces it. A conduit that misses its bore is a hole into a sealed
# pocket; a bore that misses its conduit is a blind one.
#   EACH RESERVOIR TAKES ITS OWN STATION, and only half of what picks it lives
# in this file. THIS half is the cap's: anywhere the vent boss, the rod's
# register boss and the six screw bosses leave empty, standing over open cavity
# so the bore lands in the headspace rather than in a wall. Both stations answer
# that, and it leaves a wide choice.
#   The OTHER half is what stands on the crown over each pocket, and this module
# cannot see it — the machine imports the cold core, not the reverse. So the
# fence is measured where the bodies are, in `manifold-layout/enclosure_assembly.py`,
# and what arrives here is the answer rather than the reasoning. B's pocket has
# a clear crown and takes the corner furthest from its own drain. A's carries
# the pump and the power brick, and its station is the strip they leave between
# them.
#   The conduit's own boss does not pay that fence either way: it is a column
# INSIDE the cap, under the crown those bodies stand on. What has to find room
# up there is the tube.
reservoir_fill_port = {
    -1: (-88.0, 43.5),      # B, forward pocket — the corner opposite its drain
    +1: (102.5, -56.0),     # A, aft pocket — the strip between the pump and the brick
}
reservoir_fill_sides = tuple(sorted(reservoir_fill_port))


def reservoir_fill_conduit_xy(side):
    """The CAP-frame station of the conduit standing over one reservoir's cap fill bore.

    The bore is authored in the RESERVOIR's frame (`reservoir._add_fill_port`) and the
    conduit in the CAP's, and the cap installs spun a half turn about Z
    (`foam_assembly.spin_xy`) — so the station is the anchor negated in both coordinates."""
    x, y = reservoir_fill_port[side]
    return (-x, -y)

# Outer footprint. The ±Y (front/back) gap is the tank's foam blanket out to the
# shell wall. The ±X width is set by the reservoir + its reed channel butted
# against the shell wall — no outboard foam there; it moved to the cylinder side.
outer_shell_foam_gap = 16.0  # ±Y front/back foam-pour gap
bag_pocket_outermost_x = (
    pocket_centerward_arc_outer_radius + bag_pocket_depth - wall_and_floor_thickness
)
# ±X: reservoir far wall + reed cavity + reed wall + shell wall (reed butted).
outer_shell_x_length = 2 * (
    bag_pocket_outermost_x + reed_x_depth + 2 * wall_and_floor_thickness
)
# ±Y: reservoir side wall (its own half-width) + front/back foam + shell wall.
outer_shell_y_length = 2 * (
    bag_pocket_width / 2 + outer_shell_foam_gap + wall_and_floor_thickness
)

# The ±X FORWARD BAND — what is left between the bag pocket's far wall and the outer shell's
# inner face. It is the reed channel's own depth and wall and nothing else, because that pair
# is what set `outer_shell_x_length`: the band exists at every y BECAUSE the reed channel is
# in it at one. A line climbing this band is potted in the pour beside the reed column, and
# there is a bore's width of it to climb.
forward_band_width = reed_x_depth + wall_and_floor_thickness

# The −Y pour band — the open gap between the bag-pocket wall's outer face
# and the outer shell's inner face, poured full of foam around the
# reservoirs. Every front-wall pass-through crosses it, so each is two
# bores rather than one: the pocket-wall bore stays where the fitting
# inside points, the outer-shell bore goes where the cabinet needs it, and
# the line turns through the band between them. The band is what lets the
# two sit at different X.
pour_band_pocket_side_y = -(bag_pocket_width / 2)
pour_band_shell_side_y = -(outer_shell_y_length / 2 - wall_and_floor_thickness)
pour_band_mid_y = (pour_band_pocket_side_y + pour_band_shell_side_y) / 2


# Foam-cap stack — the pour trays that close both ends of the shell (one
# mouth-up on top, one mouth-down underneath), each with a thin pour lid.
# The interior height is the cap's foam depth; the printed cup adds one
# floor.
foam_cap_interior_height = outer_shell_foam_gap
foam_cap_height = foam_cap_interior_height + wall_and_floor_thickness
foam_cap_lid_pour_radius = 10.0
foam_cap_lid_vent_radius = 3.0
foam_cap_lid_hole_inset = 30.0

# --- The vessel's clocking --------------------------------------------------
#
# Four 1/4" NPT ports, two per end plate, each pair [1.5"](VESSEL_PORT_PITCH) centre to
# centre on a diameter (`hole_offset` in cut-parts/carbonation/endcaps-circular). Both
# plates carry the float rod's blind register on the axis at right angles to their own
# pair, the rod is tack-welded into the bottom plate's register and enters the top plate's
# at closure, so the plates are clocked together and the vessel has ONE port axis.
#   That axis is the shell's ±Y. All four ports stand [19.05 mm](VESSEL_PORT_OFFSET) off
# the shell's own axis on it, two under the vessel and two over it.
vessel_port_offset = 0.750 * 25.4

# CO2 inlet — the bottom plate's LANE-SIDE port. Inside the vessel it feeds the
# barb adapter, the silicone stub and the 0.5 µm sintered sparge stone hanging in
# the water column (`assembly/pressure-vessel.md`): the gas enters BELOW the
# liquid and dissolves on the way up, which is what makes the carbonation the
# CO2 supply pressure sets.
#   Outside the vessel it is one bore on the shell's own centreline, level with the
# bottom-plate elbows, run from the port out through the tank support ring to the
# port lane. The port, its TAISHER elbow, the PP010822E collet made up on it and
# the ring bore all stand on that one line, so the tube is the only thing that
# crosses shell material and no bend is taken in-cavity. The line reaches the
# bore's lane end from ABOVE — down the port lane from the cap's `co2-in`
# conduit — so it is laid before the top cap goes on, not pushed in from outside.
co2_inlet_y = -vessel_port_offset
co2_inlet_tube_radius = port_hole_radius

# The top plate's two, by the same pair: the water inlet takes the +Y hole, which is the
# one the cap can carry a conduit over, and the PRV takes the −Y hole above the CO2's.
# Filtered tap water arrives at the top plate ABOVE the liquid and falls into the
# headspace against the CO2 back-pressure; the carbonated draw leaves at the bottom
# plate, below it. So the vessel is filled high and drawn low, the same way both
# reservoirs are.
water_inlet_port_y = +vessel_port_offset
prv_port_y = -vessel_port_offset

# Cap-to-outer-shell joinery: 6 attachment points per face × 2 faces =
# 12 inserts / 12 M3×25 SHCS, each screw passing lid + cap into an insert
# pressed from the shell face it mates. TPU gasket per cap
# (foam-cap-gasket.step). See bom.md for hardware SKUs.
screw_clearance_radius = 1.95  # ⌀[3.9](SCREW_CLEARANCE_DIAMETER) clearance for M3 SHCS shank
insert_pocket_radius = 2.0  # ⌀[4](INSERT_POCKET_DIAMETER) for ruthex M3 short heat-set
insert_pocket_depth = 8.0  # 4 mm insert engagement + 4 mm relief
screw_boss_size = 8.0  # ⌀[8 × 8 mm](SCREW_BOSS_SIZE) cylindrical boss at each attachment

# The head sits in the lid. Each of the cap's six boss columns stops
# [3.2 mm](HEAD_PAD_H) short of its mouth; the lid's pad, of the boss's own
# cross-section, fills that relief and carries the counterbore the
# [3 mm](SCREW_HEAD_H) head lands in. One wall of PETG under the head, the boss
# section under that, and the lid's outer face a plane.
screw_head_height = 3.0  # DIN 912 M3 nominal
head_seat_recess = 0.2  # how far under the lid's outer face the head lands
head_cbore_radius = 3.075  # ⌀[6.15](HEAD_CBORE_D) over the ⌀5.5 head
head_cbore_depth = screw_head_height + head_seat_recess
# A pad as tall as the counterbore is deep leaves the land at one wall exactly.
head_pad_height = head_cbore_depth
head_pad_slip = 0.2  # per side, pad to the boss relief that receives it

# --- The front face, and the lane that reaches it ---------------------------
#
# Every penetration opens on the shell's −X face. That face is the SHORT one, and
# in the appliance it is yawed onto the machine's front (`enclosure_assembly.FOAM_YAW`) —
# which is why the shell's short axis is what sets the appliance's width.
#
# Nothing reaches that face head-on: the reservoir pockets fill both ±X ends of the
# shell, so a line from the tank or from either pocket gets there along the −Y POUR
# BAND, which runs the shell's whole length outboard of both pockets. What a line
# may use of that band is the LANE: the strip inboard of every attachment boss.
# All six bosses stand hard against a ±Y wall (`attachment_xy_positions`) and reach
# `screw_boss_size` in from its outer face, so the lane is exactly what they leave,
# and it runs clear end to end at every height above the floor slab.
#
# The lane is ONE BORE WIDE. That is what makes the front port field a column
# rather than a grid — see `front_port_stations`.
front_wall_x = -outer_shell_x_length / 2
port_lane_outer_y = -(outer_shell_y_length / 2 - screw_boss_size)
port_lane_inner_y = pour_band_pocket_side_y
port_lane_mid_y = (port_lane_outer_y + port_lane_inner_y) / 2

# The +Y band's lane, which is this one mirrored — the bosses stand at both signs, so both
# bands leave the same strip. Two lines use it, and they use it end to end rather than
# crossing: reservoir B's flavor line comes out of its pocket's +Y wall, comes about in this
# band and climbs it to the TOP, out through the cap's own `reservoir-b` conduit; and the
# evaporator's WARM tail drops this band to its own station low on the front wall
# (`copper_plugs.columns`).
west_lane_mid_y = -port_lane_mid_y
# PETG left either side of a bore on the lane, and under the lowest one over the
# floor slab. Below this the wall between two features stops being printable.
port_lane_wall = 1.5
state(
    "port-lane-width", "The port lane carries a bore with a wall either side of it",
    f"{2 * (port_hole_radius + port_lane_wall):g} mm of lane",
    port_lane_inner_y - port_lane_outer_y >= 2 * (port_hole_radius + port_lane_wall),
    f"the port lane is {port_lane_inner_y - port_lane_outer_y:g} mm wide, which cannot carry a "
    f"⌀{2 * port_hole_radius:g} bore with {port_lane_wall:g} mm of PETG either side")

# Where the evaporator coil's two tails leave the tank: the low one one
# `hole_shift_from_edge` above the bottom-plate elbow band, the high one the same
# below the top's. These are the COIL's heights — what the mandrel is wound to and
# what the reed bridge's wrap band spans — and they are NOT the heights their copper
# crosses the shell wall at. Each tail turns onto a LANE OF ITS OWN — the inlet's onto
# the port lane, the outlet's onto the west (`copper_plugs.columns`) — and both drop
# from there to their stations in the slot, so compressing the field can never compress
# the coil.
evap_tail_low_z = hole_shift_from_edge + wall_and_floor_thickness + below_tank_elbows_height
evap_tail_high_z = (foam_shell_outer_height - hole_shift_from_edge
                    - wall_and_floor_thickness - above_tank_elbows_height)

# The FRONT PORT FIELD — where each penetration crosses the −X wall on the PORT LANE.
# One column, pitched a bore plus one wall, climbing from the floor. What sets a
# station's Z is NOT the height of the fitting it serves: a line leaves its fitting,
# turns into a lane and climbs it freely. The field carries the two reed cables, which
# leave together out of the pockets' bulkhead band. Everything above the field belongs to
# that lane's SLOT, which takes the rest of the column (`copper_plugs.columns`).
front_port_pitch = 2 * port_hole_radius + port_lane_wall
# NO FLUID LINE IS HERE. The front wall is mated face to face with the refrigeration base —
# the condenser against it and the compressor's own plate just short of that plane — so a bore
# struck here opens into that base rather than into the machine. Every one of the seven fluid lines leaves by
# the TOP instead, up its own band to a conduit in the cap (`cap_conduits`). What is left on
# this face is the two reed cables and the copper/PRV slot above them.
front_port_order = ("reed-cable-a", "reed-cable-b")
front_port_floor_z = bag_pocket_floor_top_z + port_lane_wall + port_hole_radius


def front_port_z(name):
    """The Z one front-field station crosses the −X wall at."""
    return front_port_floor_z + front_port_pitch * front_port_order.index(name)


front_port_field_top_z = front_port_z(front_port_order[-1]) + port_hole_radius

# The face every penetration opens on, as a direction: the shell's own −X. A station is a
# position and the way out of it, so a turn that moves the shell moves both.
front_port_axis = (-1.0, 0.0, 0.0)


def front_port_station(name):
    """One front-field station in the SHELL'S OWN frame: `(position, outward axis)`.

    Both stand on the port lane's centreline, in the wall's own plane, each at its own
    height up the column. The lane is one bore wide (above), so X and Y are the field's and
    only Z is the station's."""
    return ((front_wall_x, port_lane_mid_y, front_port_z(name)), front_port_axis)


def front_port_stations() -> dict:
    """Both, under the names the machine knows them by. What crosses ABOVE the field belongs
    to a lane's slot, and `copper_plugs.slot_stations` declares those — the two on this lane
    and the one on the west."""
    return {name: front_port_station(name) for name in front_port_order}


# Rounded outer-shell corners. Each corner's exterior wall is a true arc:
# the outer face is a quarter-round of [12 mm](CORNER_ROUND_R) radius, the
# inner face concentric one wall-thickness inboard.
corner_round_radius = 12.0

# Every attachment boss stands hard against a ±Y wall — none in a corner, and none
# on a ±X wall. Two reasons, and they are the same reason twice: the ±Y bands are
# the only place a line running to the front face can travel, and a boss reaching
# further in than `screw_boss_size` would narrow the lane below one bore. A boss
# seated diagonally IN a corner (its cylinder tangent to the exterior arc, which is
# the deepest seat available) reaches diagonally into the band, and that is what
# closed the corner the lane has to turn through. Held against the wall instead, all
# six leave the same lane and the ±X ends of both bands run clear to the wall.
#   The four end bosses stand over the reservoir pockets' own far walls, which is
# the furthest out they can go and still keep one wall of PETG around their insert
# pockets inside the corner's rounded skin. Opposite signs at ±Y preserve 180°
# rotational symmetry about Z (balanced gasket compression, and the top cap free to
# install either way round).
mid_screw_x_offset = 15.0
_boss_wall_y = outer_shell_y_length / 2 - screw_boss_size / 2
_end_boss_x = bag_pocket_outermost_x
attachment_xy_positions = (
    [(x_sign * _end_boss_x, y_sign * _boss_wall_y)
     for x_sign in (1, -1) for y_sign in (1, -1)]
    + [(y_sign * mid_screw_x_offset, y_sign * _boss_wall_y)
       for y_sign in (1, -1)]
)
_boss_lane = bound(
    "boss-clears-lane", "Every attachment boss stands clear of the port lane",
    "every boss inboard of the lane's outer edge")
for _bx, _by in attachment_xy_positions:
    _boss_lane(
        abs(_by) - screw_boss_size / 2 >= outer_shell_y_length / 2 - screw_boss_size,
        f"attachment boss at ({_bx:g}, {_by:g}) reaches past the port lane's outer edge "
        f"({port_lane_outer_y:g}) — the lane every front penetration runs along")
gasket_thickness = 2.0
gasket_strip_width = 5.0

# The clamp screw, end to end. From under its head an M3 × [25](CAP_SCREW_L)
# crosses the land, then the one continuous PETG section the lid's pad and the
# cap's boss column make between them, then the gasket — and whatever is left
# is what it has to give the insert on the far side of the shell's face. The
# recess spends none of that: the head carries the land down with it, so the
# screw arrives deeper by exactly the pad it sank.
cap_screw_length = 25.0
insert_length = 4.0  # ruthex RX-M3Sx4.0, set flush with the face
cap_screw_beyond_face = cap_screw_length - (
    wall_and_floor_thickness  # the land under the head
    + (foam_cap_height - head_pad_height)  # the boss column under the pad
    + gasket_thickness
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

# Deck mounts — the service bay's electronics, carried on columns of the TOP CAP. The cap
# is already a foam-poured cup with six screw-boss columns spanning its full height; a deck
# mount is that same column at four more stations. Foam pours around the shanks, a ruthex
# short sits flush in each column's top bore, and the module bolts down into it. Nothing is
# bonded and no tray floor stands between the module and the cap.
#   A station with no standoff stops at the cap's mouth rim, under the lid, and its module
# seats on the lid's outer face. A station with a standoff carries its column on through
# the lid, and its module seats on the column tops.
#   The stations live here, in the cap's own frame, because the mount belongs to the part it
# is printed in. `foam_assembly.deck_mount_station` carries them into the stack's own frame,
# and whoever seats the stack carries them from there into the world.
deck_mount_boss_radius = 3.5     # column radius
deck_mount_bore_radius = 2.0     # ⌀4 for a ruthex M3 short heat-set
deck_mount_lid_slip = 0.4        # per side, a standing column to the lid's clearance hole
deck_mount_insert_length = 4.0   # ruthex RX-M3Sx4.0, set flush with the column top
deck_mount_bore_relief = 0.6     # air past the screw tip at the bore's blind end

# The least room a deck column leaves to anything else standing in the cup — a screw boss,
# the cavity wall, another column. Liquid foam reaches between them.
deck_mount_cap_gap = 1.5

# Per module: the mount rectangle's centre in the cap's frame, the module's own hole pitch
# across X and Y, how far proud of the lid's outer face its column tops stand, what the
# screw head clamps down onto the column, and the screw that does it. A pitch of zero
# collapses the rectangle onto a line or a point, so a mount is however many DISTINCT
# columns its pitches leave: the ground stud rides one.
#   NO ELECTRICAL BODY IS ON THIS CAP but the ground stud. The supply and the controller hang
# on the enclosure's +X wall, one over the other; the relay lies on the lid in the band they
# left and the AC hub lies on the relay's back, and neither has a joint yet — a body resting on
# another is not mounted, so neither carries a row here. `deck_mount_cap_room` holds each
# column [1.5 mm](DECK_MOUNT_CAP_GAP) off whatever else stands in the cup for the pour to reach
# between them.
#   THE PATTERN IS THE CAP'S ROTATION KEY. The top cap installs spun a half turn about Z
# (`foam_assembly._spin`) and its six clamp bosses are symmetric under that turn, so the thing
# that tells a builder which way the cup goes on is what is NOT symmetric — these four stations
# and the seven conduit columns beside them. `assembly/cold-core.md` CC-06 and CC-15 both read
# the cap that way.
#   THE WATER PUMP IS THE ONE MODULE THAT BOLTS TO THEM. Its bracket's rubber pad carries four
# Ø6 bores on its own 59 x 79 pattern (`seaflo_22_pump.mount_holes`), the pad bears on the lid's
# outer face, and an M3 SHCS with a plain washer under its head passes down each bore, through
# the lid, into the insert below. The pad is the pump's isolator and the washer is what spreads
# the head over it, so `seat` on that row is the pad plus that washer.
#   The four tray rows carry nothing yet. Every other body standing on this cap is carried some
# other way: the power column hangs on the enclosure's own wall bosses
# (`enclosure_assembly.wall_mounts`), and the three valves that stand on the lid press into the
# cradles below. So those eight are bored columns and inserts standing ready, which is what
# `bom.md` §7 bills them as.
DeckMount = namedtuple("DeckMount", "centre pitch_x pitch_y standoff seat screw")
deck_mounts = {
    #                        centre            pitch_x pitch_y  proud  seat  screw
    "seaflo-pump": DeckMount((-93.20,   0.00),  59.00,  79.00,   0.0,  8.50, 16.0),
    "bag-b-tray":  DeckMount((105.25,  17.02),   0.00,  49.50,   0.0,  9.00, 16.0),
    "vk-tray":     DeckMount((  6.30,  37.62),  49.50,   0.00,   0.0,  9.00, 16.0),
    "nozzle-b-tray": DeckMount((-82.92, 25.00), 49.50,   0.00,   0.0,  9.00, 16.0),
    "nozzle-tray": DeckMount(( 109.75, -68.325), 49.50,   0.00,   0.0,  9.00, 16.0),
}


def deck_mount_xy(name):
    """The boss centres of a deck mount, in the cap's own frame. A zero pitch makes the
    rectangle degenerate, and the duplicate corners it produces are one column."""
    m = deck_mounts[name]
    (cx, cy) = m.centre
    return tuple(sorted({(cx + sx * m.pitch_x / 2.0, cy + sy * m.pitch_y / 2.0)
                         for sx in (-1, 1) for sy in (-1, 1)}))


def deck_mount_standoff(name):
    """How far proud of the lid's outer face this mount's column tops stand."""
    return deck_mounts[name].standoff


def deck_mount_proud():
    """The tallest standoff in the pack — the foam assembly's own top over its lid's face.
    Every station stands at `standoff = 0.0`, so the columns top out flush with the lid."""
    return max((deck_mount_standoff(name) for name in deck_mounts), default=0.0)


def deck_mount_reach(name):
    """How far a seated screw runs past this mount's column top. A flush station's screw
    crosses the lid on its way down; a standing one meets the column at the head. `seat`
    is what the head bears on before it gets there — a board's own thickness, a hub's
    floor, or the fan of ring terminals that is the ground bus."""
    m = deck_mounts[name]
    over = m.seat
    if m.standoff == 0.0:
        over += wall_and_floor_thickness
    return m.screw - over


# One bore serves every station, sunk to the deepest reach any of them presents.
deck_mount_bore_depth = max(
    (deck_mount_reach(name) for name in deck_mounts), default=0.0) + deck_mount_bore_relief
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


def deck_mount_cap_room(name):
    """The least room this station's columns leave to anything else standing in the cup:
    `(mm, what)` — a screw boss, the cavity wall, another mount's column."""
    room = []
    for x, y in deck_mount_xy(name):
        for bx, by in attachment_xy_positions:
            room.append((math.hypot(x - bx, y - by)
                         - screw_boss_size / 2.0 - deck_mount_boss_radius, "a screw boss"))
        room.append((min(outer_shell_x_length / 2.0 - abs(x),
                         outer_shell_y_length / 2.0 - abs(y))
                     - wall_and_floor_thickness - deck_mount_boss_radius, "the cavity wall"))
        for other in deck_mounts:
            for ox, oy in deck_mount_xy(other):
                if (ox, oy) != (x, y):
                    room.append((math.hypot(x - ox, y - oy) - 2.0 * deck_mount_boss_radius,
                                 f"the {other} mount"))
    return min(room)


_mount_room = bound(
    "deck-mount-room", "Every deck-mount column leaves the pour its gap in the cup",
    f"{deck_mount_cap_gap:g} mm off everything standing in the cup")
for _name in deck_mounts:
    _room, _what = deck_mount_cap_room(_name)
    _mount_room(
        _room >= deck_mount_cap_gap - 1e-9,
        f"deck mount {_name}: a column stands {_room:.3f} mm off {_what}, inside the "
        f"{deck_mount_cap_gap:g} mm the pour needs to reach between them")


# --- Valve cradles on the lid's outer face -----------------------------------
#
# A CRADLE IS THE VALVE-MANIFOLD FAMILY'S OWN CELL PRINTED INTO THE TOP LID rather than into a
# plate that bolts to it: a pad standing off the lid's outer face, the Beduan's port saddle
# troughed the length of it, and a blind socket at each of the four corner posts. The valve
# presses in. Nothing bolts it and nothing is bonded — the four posts in their sockets are the
# whole of the retention, and the valve's own round boss lands on the pad top. So a cradle
# takes no insert, no screw and no lid hole, which is what a bolted tray took three of.
#   `single_tray.cut_cell` cuts the sockets and the saddle, and `foam_cap.build_cradles` holds
# the reach below against that cell's own geometry, so the pad cannot shrink under the sockets
# it carries.
#
# Per cradle: the valve's centre in the CAP'S OWN frame, the yaw its port axis takes off the
# cap's +X, and the SEAT — how far the valve's own mounting plane (the Beduan's Z = 0) stands
# over the lid's outer face, which is what sets the pad's height.
#   THE SEAT IS THE MACHINE'S, not a choice. Two of these valves ride the flavour pack, which
# stands on the refrigeration base's crown, so where they land over this cap is that stack's
# arithmetic; `enclosure_assembly.cradles_land` re-derives all three rows off the placed valves at
# every build and raises with the row a moved valve wants, so a drift cannot land silently.
# V-K is the one this cap gets to choose, and it takes the shallowest seat there is: one
# `-single_tray.socket_floor_z`, which lands its socket floors on the lid's own outer face
# and bores nothing into the plate.
Cradle = namedtuple("Cradle", "centre yaw seat")
cap_cradles = {
    #                      centre           yaw    seat
    "vk-solenoid": Cradle((111.500,  65.050), 0.0, 1.0000),
    "valve-v-a":   Cradle((105.920,  20.070), 0.0, 2.6150),
    "valve-v-b":   Cradle((105.920, -20.070), 0.0, 2.6150),
}

# The pad's own reach off the valve's centre, and the radius its corners are struck on. The
# corners ARE the four sockets: a rectangle of `corner_inset + socket_radius + wall` filleted
# on `socket_radius + wall` puts an arc centre on each socket, so the pad is the least plate
# that carries them and every millimetre of it is under something.
cap_cradle_corner_inset = 12.2       # `beduan_solenoid.corner_inset`
cap_cradle_socket_radius = 3.6       # `single_tray.socket_radius`
cap_cradle_wall = 3.0                # `single_tray.wall`
cap_cradle_corner_radius = cap_cradle_socket_radius + cap_cradle_wall
cap_cradle_reach = cap_cradle_corner_inset + cap_cradle_corner_radius

# What a cradle holds off every other thing cut in the lid's outer face. Nothing is poured
# between them — this face is the machine's room, not the cup's — so the fence is the
# machine's own clearance floor rather than the pour gap the cavity keeps.
cap_cradle_room_gap = 1.0


def cap_cradle_xy(name):
    """A cradle's four socket centres, in the cap's own frame."""
    (cx, cy) = cap_cradles[name].centre
    th = math.radians(cap_cradles[name].yaw)
    c, s = math.cos(th), math.sin(th)
    return tuple((cx + c * sx * cap_cradle_corner_inset - s * sy * cap_cradle_corner_inset,
                  cy + s * sx * cap_cradle_corner_inset + c * sy * cap_cradle_corner_inset)
                 for sx in (-1, 1) for sy in (-1, 1))


def cap_cradle_room(name):
    """The least room this cradle leaves to anything else opening on the lid's outer face:
    `(mm, what)` — a conduit's entry countersink, a clamp screw's counterbore, the pour hole,
    a vent, another cradle. Read on the pad's corner arcs, which are its nearest material to
    everything around it."""
    room = []
    for x, y in cap_cradle_xy(name):
        for cname, (bx, by) in cap_conduits.items():
            room.append((math.hypot(x - bx, y - by)
                         - cap_conduit_entry_relief_radius - cap_cradle_corner_radius,
                         f"the {cname} conduit's entry"))
        for bx, by in attachment_xy_positions:
            room.append((math.hypot(x - bx, y - by)
                         - head_cbore_radius - cap_cradle_corner_radius,
                         "a clamp screw's counterbore"))
        for dname in deck_mounts:
            for dx, dy in deck_mount_xy(dname):
                room.append((math.hypot(x - dx, y - dy)
                             - deck_lid_hole_radius(dname) - cap_cradle_corner_radius,
                             f"the {dname} mount's lid hole"))
        room.append((min(outer_shell_x_length / 2.0 - abs(x),
                         outer_shell_y_length / 2.0 - abs(y))
                     - cap_cradle_corner_radius, "the lid's own edge"))
        for other in cap_cradles:
            if other == name:
                continue
            for ox, oy in cap_cradle_xy(other):
                room.append((math.hypot(x - ox, y - oy) - 2.0 * cap_cradle_corner_radius,
                             f"the {other} cradle"))
    return min(room)


# --- Cap conduits ------------------------------------------------------------
#
# A conduit is one of the cup's own full-height columns carrying a THROUGH bore: liquid
# foam pours around its shank the way it pours around a deck mount's, the lid passes it,
# and a line runs up it from the shell's open top out onto the lid's outer face. The
# service bay stands on that face.
lldpe_tube_od = 6.35                         # the 1/4" line every fluid port on the core takes
cap_conduit_bore_radius = port_hole_radius   # the ⌀[6.5](PORT_HOLE_DIAMETER) every shell penetration takes
cap_conduit_wall = 2.0
cap_conduit_boss_radius = cap_conduit_bore_radius + cap_conduit_wall
cap_conduit_lid_slip = deck_mount_lid_slip   # per side, a standing column to the lid's clearance hole

# How far off its own bore axis a line leaves a conduit — a bore's `manifold_layout.FLAVOR_SKEW`.
# The LID'S HOLE IS COUNTERSUNK to this angle: the lip a leaning line crosses lies along it, and
# what the tube bears on there is a face. The column under the lid carries the bore on its own
# axis. `_lines.CAP_BORE_SKEW` is bound to this name.
cap_conduit_entry_skew = 38.0
# The countersink's mouth on the lid's outer face — the bore opened at that angle through the
# one wall of plate the lid is: ⌀[9.625](ENTRY_RELIEF_D).
cap_conduit_entry_relief_radius = (
    cap_conduit_bore_radius
    + wall_and_floor_thickness * math.tan(math.radians(cap_conduit_entry_skew)))
# The relief stands inside the boss its own column carries, so `cap_conduit_room`,
# `cap_conduit_wall_neck` and `cap_conduit_pair_neck` fence the cone where they fence the
# column. A wall and a lid of one thickness put that ceiling at [45°](ENTRY_SKEW_CEILING).
cap_conduit_entry_skew_ceiling = math.degrees(
    math.atan2(cap_conduit_wall, wall_and_floor_thickness))
state(
    "entry-skew-ceiling", "The countersink stands inside the boss its own column carries",
    f"{cap_conduit_entry_skew_ceiling:.1f}° at most",
    cap_conduit_entry_skew <= cap_conduit_entry_skew_ceiling + 1e-9,
    f"cap conduit entry: {cap_conduit_entry_skew:g}° opens the lid's hole to "
    f"⌀{2.0 * cap_conduit_entry_relief_radius:.2f}, past the ⌀{2.0 * cap_conduit_boss_radius:g} "
    f"column under it — a relief stands inside its own boss, which is "
    f"{cap_conduit_entry_skew_ceiling:.1f}° here")
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
# stands over a vessel port at (x, y) in the shell's frame is authored at (−x, −y) here,
# and `foam_assembly.cap_conduit_station` turns it back.
#   A CONDUIT IS ONE END OF A LINE, and what the line does at the far end is what this table
# is for; `_internal_routes` draws every one of them and measures it against the shell. Seven
# stand here, and they answer to three vessels. TWO ENTER THE CARBONATOR (water at the top
# plate, CO2 at the bottom) and one draws it; each reservoir is entered once at its cap and
# drawn once at its floor. Every line that ENTERS a vessel arrives above that vessel's liquid
# and every line that LEAVES takes its lowest point, so nothing can enter and leave without
# crossing the vessel. That is what the air-purge and clean-flush service modes run on.
#
#   water-in — the carbonator's TOP-PLATE +Y port, above the water line, where filtered tap
# water is pumped in against the CO2 back-pressure and falls into the headspace. The port
# carries one of the four TAISHER street elbows every vessel port takes (`ledger/bom.md`) with
# a PTC adapter made up on its female end; the line leaves it laterally, runs the band between
# that plate and the cap's floor (`top_band_to_cap`), comes about in the +Y band and turns into
# the FORWARD BAND, where this bore stands. The top band is [14](TOP_BAND) mm against the
# [25.4 mm](LLDPE_BEND_R) a stock arc wants, so the corner off the elbow is the one that reach
# buys with, and it is potted where it turns. It shares the forward strip with both reservoir
# draws, each climbing its own bore `cap_conduit_pair_neck` away.
#   water-in's X in the cap's frame is that strip's own centreline. Its Y is THE DECK ABOVE:
# the discharge chain lies fore and aft in the lane the water split leaves it, collet forward,
# and this bore stands on the chain's own column at the far end of the fall. So the run off the
# collet is one straight and one slant, the slant entering the bore inside its own
# `cap_conduit_entry_skew`, and the lid's countersink is what lays the lip along it.
#   reservoir-b and reservoir-a are the two DRAWS, and both stand over that same FORWARD BAND —
# the strip between a pocket's own wall and the shell's, [8 mm](FORWARD_BAND) of it
# (`forward_band_width`). Each line starts on its reservoir's floor bulkhead, at the bottom of
# the wet V and the lowest drainable point in the cavity; the elbow under the raised floor turns
# it laterally, it crosses its pocket's own ±Y wall at `bulkhead_elbow_exit_z` into the band
# behind it, comes about, and climbs the forward strip potted to this bore. B takes the +Y band
# and A the −Y one, because that is the wall each one's elbow points at, and A's climb is the
# longer for it — its pocket is the far one from this strip.
#   A ⌀[6.5](PORT_HOLE_DIAMETER) bore leaves the tube a `LINE_HUG` of foam either side; what
# pins the two stations in Y is that and the reed channels, whose envelopes stand in this same
# strip and which both bores clear (`_reed_channels` measures it).
#   THE FORWARD STRIP'S COLUMNS ARE MERGED and not standing. The strip is forward of everything
# in the cup, so a post over it stands inside the pour gap the perimeter wall wants — and a
# conduit has the same two states against that wall it has against another conduit
# (`cap_conduit_wall_neck`): the column fuses into the wall and the bore runs up a local
# thickening of it, carrying a wall's material outboard.
#   A RESERVOIR FILL stands over its own reservoir rather than over a band, and has no run
# inside the shell at all: it is the column between a valve on the deck and the bore in the cap
# of the reservoir it fills, and that cap's own outer face is the last thing under this one, so
# the two features meet across the pour clearance over the reservoir and nothing else
# (`_internal_routes` draws and measures the stub). The bore it lands on opens
# into the reservoir's HEADSPACE, above the liquid and clear of the vent boss, the rod register
# and every screw boss — so what arrives falls into the cavity and can only leave by the trough.
# `reservoir_fill_conduit_xy` is the station, and `reservoir_fill_sides` is which reservoirs
# have one.
#   carb-water-out — the carbonator's BOTTOM-PLATE +Y port, under the liquid, which is the
# vessel's own drain and the dispense line's source. The elbow turns it laterally, it crosses
# under the tank inboard of the support ring, leaves the ring through the ring's OWN SLOT on
# this bore's column (`_port_cuts.water_outlet_ring_crossing_x` — no bore, and the four bearing
# segments stay whole), and climbs beside the coil clear of the port lane until the tank's top
# plate is under it. Only there does it step out onto the lane and into this bore. That climb is
# inboard because the CO2 owns the lane's own strip at the bottom of the shell.
#   Its X answers to THE DECK ABOVE, the same fence co2-in takes. The +X flank stands a column
# of bodies on the lid — V-K, the controller board, the power brick — and each leaves the lane
# a window rather than a lane; this bore takes the widest of them, the band between the board's
# forward face and the run its own riser has to clear. `cap_conduit_pair_neck` is what holds
# the two bores apart inside that one lane.
#   co2-in stands over the PORT LANE and its line runs DOWN it, the one conduit here that feeds
# rather than drains. It falls the shell's whole height, turns along the lane's floor to the
# shell's centreline, and enters `_port_cuts.co2_inlet_xyz` — the one bore through the support
# ring — to land on the collet made up under the bottom plate's lane-side port. Inside the vessel
# that port feeds the barb, the silicone stub and the sparge stone hanging in the water column,
# so the gas enters BELOW the liquid and dissolves on the way up. Because the line arrives from
# above, it is laid down the lane before the top cap goes on.
#   Its X is the DECK ABOVE. The +X flank carries a column of bodies standing on the lid from
# the cap to the ceiling, and this bore takes the one window in that column — the strip between
# V-K's own footprint and the controller board's. `cap_conduit_pair_neck` is what holds it off
# the carb water's climb.
cap_conduits = {
    "water-in": (135.5, -56.0),
    "reservoir-a": (135.5, 43.5),
    "reservoir-b": (135.5, -43.5),
    "reservoir-a-fill": reservoir_fill_conduit_xy(+1),
    "reservoir-b-fill": reservoir_fill_conduit_xy(-1),
    "carb-water-out": (45.5, -port_lane_mid_y),
    "co2-in": (72.5, -port_lane_mid_y),
}

# Every cut cap has a conduit over its bore, and every fill conduit has a cut cap under it.
# Naming is what carries the pairing across the two frames, so the name is checked too: the
# conduit for `side` is `reservoir-<x>-fill`, and it stands exactly on that side's anchor.
_fill_conduits = {n for n in cap_conduits if n.endswith("-fill")}
_fill_wanted = {f"reservoir-{'ab'[s < 0]}-fill" for s in reservoir_fill_sides}
state(
    "fill-conduits-paired", "Every fill bore has a conduit over it and every conduit a bore",
    f"the cap's fills naming {sorted(_fill_wanted)}",
    _fill_conduits == _fill_wanted,
    f"reservoir fills: {sorted(_fill_conduits)} stand on the cap, but "
    f"`reservoir_fill_sides` cuts {reservoir_fill_sides} — a conduit with no bore under it "
    f"is a hole into a sealed pocket, and a bore with no conduit over it is a blind one")
# The station is read only where the pairing above found a conduit to read it off. An unpaired
# side has already said so on its own row, and a lookup that is not there would take the whole
# module down with it — the one thing this ledger exists to stop.
_fill_station = bound(
    "fill-conduit-station", "Every fill conduit stands on its own side's anchor",
    "each conduit on the station its anchor strikes")
for _s in reservoir_fill_sides:
    _n = f"reservoir-{'ab'[_s < 0]}-fill"
    _at = cap_conduits.get(_n)
    if _at is None:
        continue
    _fill_station(
        _at == reservoir_fill_conduit_xy(_s),
        f"{_n} stands at {_at}, off the side {_s:+d} anchor's own station "
        f"{reservoir_fill_conduit_xy(_s)}")

# What a line arriving off-axis turns in: the band from a top-plate elbow's own lateral
# axis up to the cap's floor, against the rise a corner of 1/4" LLDPE takes.
tank_top_plate_z = wall_and_floor_thickness + tank_support_ring_height + tank_height
top_band_to_cap = foam_shell_outer_height - (tank_top_plate_z + hole_shift_from_edge)
# [25.4 mm](LLDPE_BEND_R) — 4 × OD, the corner 1/4" LLDPE holds unsupported. The machine
# draws its own runs at half of it (`_routing.BEND_RATIO`), and so does `_internal_routes`,
# because a potted line is held at its corner by the foam round it.
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
    if to_outer - wall_and_floor_thickness >= cap_conduit_boss_radius:
        return (to_outer - wall_and_floor_thickness - cap_conduit_boss_radius,
                "the pour gap behind a standing column")
    return (to_outer - cap_conduit_bore_radius, "the wall left outboard of a merged bore")


def cap_conduit_room(name):
    """The least room this conduit leaves to anything else STANDING in the cup:
    `(mm, what)` — a screw boss, a deck mount's column. The perimeter wall is not one of
    these: a column may merge into it, and `cap_conduit_wall_neck` is what prices that."""
    x, y = cap_conduits[name]
    room = []
    for bx, by in attachment_xy_positions:
        room.append((math.hypot(x - bx, y - by)
                     - screw_boss_size / 2.0 - cap_conduit_boss_radius, "a screw boss"))
    for other in deck_mounts:
        for ox, oy in deck_mount_xy(other):
            room.append((math.hypot(x - ox, y - oy)
                         - deck_mount_boss_radius - cap_conduit_boss_radius,
                         f"the {other} mount"))
    return min(room)


_conduit_room = bound(
    "cap-conduit-room", "Every conduit column leaves the pour its gap in the cup",
    f"{deck_mount_cap_gap:g} mm off everything else standing in the cup")
_conduit_wall = bound(
    "cap-conduit-wall", "Every conduit column stands the pour gap off the wall or merges in",
    f"the pour gap apart or a {cap_conduit_wall:g} mm neck")
for _name in cap_conduits:
    _room, _what = cap_conduit_room(_name)
    _conduit_room(
        _room >= deck_mount_cap_gap - 1e-9,
        f"cap conduit {_name}: the column stands {_room:.3f} mm off {_what}, inside the "
        f"{deck_mount_cap_gap:g} mm the pour needs to reach between them")
    _neck, _what = cap_conduit_wall_neck(*cap_conduits[_name])
    _want = deck_mount_cap_gap if _what.startswith("the pour") else cap_conduit_wall
    _conduit_wall(
        _neck >= _want - 1e-9,
        f"cap conduit {_name}: {_what} is {_neck:.3f} mm, under the {_want:g} mm it takes "
        f"— a column either stands the pour gap off the wall or merges into it")


def foam_cap_lid_pour_xy():
    """The pour hole's centre in the lid — the +X half, on the LEAST offset off the cap's
    own centreline that clears every deck-mount station and every valve cradle.

    A station this hole swallows is a tray ear with no lid under its screw, and a cradle it
    swallows is a valve seat with a hole through the middle of it: either way the pad would
    stand on nothing. So the hole holds its own radius, the thing it is clearing and the pour
    gap off each of them, and takes the smallest shift that buys it — the pour wants the cap's
    middle, and every millimetre off it is spent.

    `deck_mount_cap_room` prices a station against everything standing in the CUP and
    `cap_cradle_room` prices a cradle against everything cut in the LID; this is the same fence
    read from the pour's side, which is what is free to move."""
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
    for name in cap_cradles:
        for sx, sy in cap_cradle_xy(name):
            fence(sx, sy, foam_cap_lid_pour_radius + cap_cradle_corner_radius
                  + deck_mount_cap_gap)
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


def foam_cap_lid_vent_xy():
    """Both vent holes' centres in the lid — the −X corners, mirrored across y, where the
    pour hole is not and nothing stands. Air leaves by whichever is uppermost."""
    x = -(outer_shell_x_length / 2 - foam_cap_lid_hole_inset)
    y = outer_shell_y_length / 2 - foam_cap_lid_hole_inset
    return ((x, y), (x, -y))


_mount_pour = bound(
    "deck-mount-pour", "Every deck mount's lid hole leaves a land under its screw head",
    f"{deck_mount_cap_gap:g} mm off the pour hole")
for _name in deck_mounts:
    _px, _py = foam_cap_lid_pour_xy()
    for _sx, _sy in deck_mount_xy(_name):
        _room = (math.hypot(_px - _sx, _py - _sy)
                 - foam_cap_lid_pour_radius - screw_clearance_radius)
        _mount_pour(
            _room >= deck_mount_cap_gap - 1e-9,
            f"deck mount {_name}: its lid clearance hole at ({_sx:g}, {_sy:g}) stands "
            f"{_room:.3f} mm off the pour hole, inside the {deck_mount_cap_gap:g} mm that "
            f"leaves a land under the screw's head")


# Every cradle stands its own room off everything else the lid's outer face opens — including
# the pour hole, which moved to make it. This is read after the conduits and the pour, because
# it is read against them.
_cradle_room = bound(
    "cradle-room", "Every cradle pad stands its room off everything else the face opens",
    f"{cap_cradle_room_gap:g} mm off the nearest")
_cradle_pour = bound(
    "cradle-pour", "Every cradle pad has a floor under it where the pour hole is",
    f"{cap_cradle_room_gap:g} mm off the pour hole")
_cradle_vent = bound(
    "cradle-vent", "Every cradle pad has a floor under it where the vents are",
    f"{cap_cradle_room_gap:g} mm off either vent")
for _name in cap_cradles:
    _room, _what = cap_cradle_room(_name)
    _cradle_room(
        _room >= cap_cradle_room_gap - 1e-9,
        f"valve cradle {_name}: a pad corner stands {_room:.3f} mm off {_what}, inside the "
        f"{cap_cradle_room_gap:g} mm this face keeps between two things it opens")
    _px, _py = foam_cap_lid_pour_xy()
    for _sx, _sy in cap_cradle_xy(_name):
        _room = (math.hypot(_px - _sx, _py - _sy)
                 - foam_cap_lid_pour_radius - cap_cradle_corner_radius)
        _cradle_pour(
            _room >= cap_cradle_room_gap - 1e-9,
            f"valve cradle {_name}: a pad corner at ({_sx:g}, {_sy:g}) stands {_room:.3f} mm "
            f"off the pour hole, inside the {cap_cradle_room_gap:g} mm that leaves the pad a "
            f"floor under it")
    for _hx, _hy in foam_cap_lid_vent_xy():
        for _sx, _sy in cap_cradle_xy(_name):
            _room = (math.hypot(_hx - _sx, _hy - _sy)
                     - foam_cap_lid_vent_radius - cap_cradle_corner_radius)
            _cradle_vent(
                _room >= cap_cradle_room_gap - 1e-9,
                f"valve cradle {_name}: a pad corner at ({_sx:g}, {_sy:g}) stands "
                f"{_room:.3f} mm off a vent, inside the {cap_cradle_room_gap:g} mm that "
                f"leaves the pad a floor under it")


def cap_conduit_pair_neck(a, b):
    """What a PAIR of conduits leaves between them: `(mm, what)`.

    A pair is one of two things and never a third. APART, with at least the pour gap
    between the two columns, so foam reaches down between them. Or MERGED, the two bores
    standing nearer than a boss diameter and their columns fusing into one post — and then
    what matters is the NECK the lens leaves, which carries the joint and must be a wall
    thick. What neither may be is tangent: two circles meeting near a point close a knife
    edge that prints as a void and holds no load.

    `cap_conduit_room` prices a conduit against everything else standing in the cup; this
    is the one pair it cannot price, because for a pair overlap is a design and not a
    clash."""
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


def build_hole_punch(
    *,
    origin=(0, 0, 0),
    hole_punch_radius,
    hole_punch_height=40,
    direction=1,
):
    """Y-axis ⌀ × height cylindrical cut, centered at `origin`'s X/Z and
    starting at `origin`'s Y, extruded in `direction`·Y (+1 = +Y, −1 = −Y —
    so a port on the −Y wall punches outward toward −Y)."""
    x, y, z = origin
    return (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(x, 0, z), offset=y)
        .circle(hole_punch_radius)
        .extrude(direction * hole_punch_height)
    )


def build_x_axis_hole_punch(
    *,
    origin=(0, 0, 0),
    hole_punch_radius,
    hole_punch_height=40,
    direction=1,
):
    """X-axis ⌀ × height cylindrical cut, centered at `origin`'s Y/Z and starting
    at `origin`'s X, extruded in `direction`·X (+1 = +X, −1 = −X — so a port on the
    −X wall punches outward toward −X)."""
    x, y, z = origin
    return cq.Solid.makeCylinder(
        hole_punch_radius, hole_punch_height,
        cq.Vector(x, y, z), cq.Vector(direction, 0, 0))


def cut_front_exit(foam_shell, *, z, hole_punch_radius, lateral=0.0):
    """One penetration's mouth: a bore straight out through the −X wall, on the
    port lane at `lateral` off its centre. The line inside reaches it along the
    lane, so this bore's Z is the field's station and has nothing to do with the
    height of the fitting it serves."""
    overshoot = 1.0                                    # a through-cut, both faces cleared
    return foam_shell.cut(
        build_x_axis_hole_punch(
            origin=(front_wall_x + wall_and_floor_thickness + overshoot,
                    port_lane_mid_y + lateral, z),
            hole_punch_radius=hole_punch_radius,
            hole_punch_height=wall_and_floor_thickness + 2.0 * overshoot,
            direction=-1,
        )
    )


def pour_band_pocket_punch(*, pocket_hole_x, y, z, hole_punch_radius):
    """The pocket-side half of a pour-band pass-through, as a SOLID: a bore through the
    bag-pocket (or ring) wall at `pocket_hole_x`, starting at `y` and stopping on the port
    lane.

    Named apart from the cut so that whatever prices a neighbouring opening against this
    hole is reading the hole itself and not a second construction of it."""
    return build_hole_punch(
        origin=(pocket_hole_x, y, z),
        hole_punch_radius=hole_punch_radius,
        hole_punch_height=y - port_lane_mid_y,
        direction=-1,
    )


def cut_pour_band_pass_through(
    foam_shell,
    *,
    pocket_hole_x,
    y,
    z,
    exit_z,
    hole_punch_radius,
):
    """Cut one pass-through as two bores that do not meet: through the bag-pocket
    (or ring) wall at `pocket_hole_x`, starting at `y` and stopping on the port
    lane, and out through the −X wall at the field station `exit_z`. Between them
    the line turns and runs along the open lane — west to the wall, and up it from
    the fitting's own height to the station's. The lane is what lets the two sit at
    different X *and* different Z."""
    foam_shell = foam_shell.cut(
        pour_band_pocket_punch(
            pocket_hole_x=pocket_hole_x, y=y, z=z, hole_punch_radius=hole_punch_radius)
    )
    return cut_front_exit(foam_shell, z=exit_z, hole_punch_radius=hole_punch_radius)


def build_slot_punch(
    origin=(0, 0, 0),
    slot_length=1.0,
    slot_diameter=6.5,
    slot_punch_height=40,
    direction=1,
):
    """Z-elongated, Y-extruded rounded slot (circle-rect-circle), centered
    at `origin`'s X/Z and starting at `origin`'s Y, extruded in `direction`·Y
    (+1 = +Y, −1 = −Y). Long axis runs along world Z. The rounded ends each
    contribute slot_diameter/2 of additional Z reach beyond `slot_length`."""
    x, y, z = origin
    return (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(x, 0, z), offset=y)
        .slot2D(slot_length, slot_diameter, angle=90)
        .extrude(direction * slot_punch_height)
    )


def port_to_shell(solid, lane_y=None):
    """Carry a solid from the PORT FRAME into the shell's, onto one of the front wall's
    two lanes.

    The port frame is the one every penetration is authored in, the copper-plug
    stack among them: x lateral across the face, −y out through it, z the shell's
    own. One quarter turn about Z puts its −y on the shell's −X, and one slide puts
    its lateral centreline on a lane. Authoring there is what keeps the plug
    stack and the slot it fills a single reading — a plug is a part that plugs a slot
    in a wall, and that is the frame that says so; a pose turned by hand alongside a
    slot cut by hand is two implementations of one transform.

    ONE FRAME SERVES BOTH LANES because both are the same wall: `lane_y` is the only
    thing that differs, so a plug printed for one lane fits the other."""
    return (solid.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), -90.0)
                 .translate(cq.Vector(0.0, port_lane_mid_y if lane_y is None else lane_y, 0.0)))


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
        "ABOVE_TANK_ELBOWS_HEIGHT": f"{above_tank_elbows_height:.4g} mm",
        "BELOW_TANK_ELBOWS_HEIGHT": f"{below_tank_elbows_height:.4g} mm",
        "PORT_HOLE_DIAMETER": f"{port_hole_radius * 2:.4g}",
        "SCREW_CLEARANCE_DIAMETER": f"{screw_clearance_radius * 2:.4g}",
        "INSERT_POCKET_DIAMETER": f"{insert_pocket_radius * 2:.4g}",
        "SCREW_BOSS_SIZE": f"{screw_boss_size:.4g} × {screw_boss_size:.4g} mm",
        "SCREW_HEAD_H": f"{screw_head_height:.4g} mm",
        "HEAD_PAD_H": f"{head_pad_height:.4g} mm",
        "HEAD_CBORE_D": f"{head_cbore_radius * 2:.4g}",
        "CAP_SCREW_L": f"{cap_screw_length:.4g}",
        "DECK_MOUNT_CAP_GAP": f"{deck_mount_cap_gap:.4g} mm",
        "VESSEL_PORT_PITCH": f"{2 * vessel_port_offset / 25.4:.4g}\"",
        "VESSEL_PORT_OFFSET": f"{vessel_port_offset:.4g} mm",
        "LLDPE_BEND_R": f"{lldpe_bend_radius:.4g} mm",
        "FORWARD_BAND": f"{forward_band_width:.4g} mm",
        "LLDPE_TUBE_OD": f"{lldpe_tube_od:.4g}",
        "ENTRY_RELIEF_D": f"{2.0 * cap_conduit_entry_relief_radius:.4g}",
        "ENTRY_SKEW_CEILING": f"{cap_conduit_entry_skew_ceiling:.4g}°",
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "WALL_AND_FLOOR_THICKNESS": 1,
            "COIL_RADIAL_CLEARANCE": 1,
            "ABOVE_TANK_ELBOWS_HEIGHT": 1,
            "BELOW_TANK_ELBOWS_HEIGHT": 1,
            "PORT_HOLE_DIAMETER": 3,
            "SCREW_CLEARANCE_DIAMETER": 1,
            "INSERT_POCKET_DIAMETER": 1,
            "SCREW_BOSS_SIZE": 1,
            "SCREW_HEAD_H": 1,
            "HEAD_PAD_H": 1,
            "HEAD_CBORE_D": 1,
            "CAP_SCREW_L": 1,
            "DECK_MOUNT_CAP_GAP": 1,
            "VESSEL_PORT_PITCH": 1,
            "VESSEL_PORT_OFFSET": 1,
            "LLDPE_BEND_R": 2,
            "FORWARD_BAND": 1,
            "LLDPE_TUBE_OD": 1,
            "ENTRY_RELIEF_D": 1,
            "ENTRY_SKEW_CEILING": 1,
        },
    )
    print("-> _cold_core_interface.py (self)")
