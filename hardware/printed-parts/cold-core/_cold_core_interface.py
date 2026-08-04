"""Shared interface for the cold-core's geometry modules — dimensional
constants and hole-punch helpers that every sibling part (foam shell,
foam cap stack, reservoir, copper plugs, coil mandrel) needs to stay
in sync against."""

import math
import sys
from collections import namedtuple
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))

import cadquery as cq

from world_workplane import xy_plane_z_up, xz_plane_y_up, xz_plane_y_down, WorldWorkplane


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
# Y of the bulkhead pass-through (and the cable hole that shares its y so
# the reed cable runs straight from channel to outside). 10 mm inboard
# of the bag-pocket −Y (front, toward the user) wall outer face.
reservoir_bulkhead_port_y = -(bag_pocket_width / 2 - 10)

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

# CO2 inlet: one bore straight in through the −Y outer wall and the tank
# support ring, level with the vessel's bottom-plate elbows. The 1/4" OD
# LLDPE line arrives horizontally out of the appliance's front-panel CO2
# chain and lands on the PP010822E collet made up on that port's TAISHER
# elbow, which hangs inboard of the ring's bore — so the tube is the only
# thing that crosses shell material, no bend is taken in-cavity, and nothing
# traverses the cap stack. The CO2 port takes the port pair's LANE-SIDE hole, so
# the bore runs down the shell's own centreline from the port to the lane and the
# port, its elbow, the ring bore and the wall bore all stand on one line.
co2_inlet_y = -vessel_port_offset
co2_inlet_tube_radius = port_hole_radius

# The top plate's two, by the same pair: the water inlet takes the +Y hole, which is the
# one the cap can carry a conduit over, and the PRV takes the −Y hole above the CO2's.
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
# in the appliance it is yawed onto the machine's front (`_contents.FOAM_YAW`) —
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
# bands leave the same strip. It carries ONE line and it has no field: reservoir B's flavor
# line crosses its pocket's +Y wall, comes about in this band and climbs it to the TOP, out
# through the cap's own `reservoir-b` conduit. So the two features that line runs between are
# a bore in a pocket wall and a hole in the cap, and this lane is what joins them.
west_lane_mid_y = -port_lane_mid_y
# PETG left either side of a bore on the lane, and under the lowest one over the
# floor slab. Below this the wall between two features stops being printable.
port_lane_wall = 1.5
assert port_lane_inner_y - port_lane_outer_y >= 2 * (port_hole_radius + port_lane_wall), (
    f"the port lane is {port_lane_inner_y - port_lane_outer_y:g} mm wide, which cannot carry a "
    f"⌀{2 * port_hole_radius:g} bore with {port_lane_wall:g} mm of PETG either side")

# Where the evaporator coil's two tails leave the tank: the low one one
# `hole_shift_from_edge` above the bottom-plate elbow band, the high one the same
# below the top's. These are the COIL's heights — what the mandrel is wound to and
# what the reed bridge's wrap band spans — and they are NOT the heights their copper
# crosses the shell wall at. Each tail turns onto the port lane and climbs or drops
# to its own station in the slot, so compressing the field can never compress the
# coil.
evap_tail_low_z = hole_shift_from_edge + wall_and_floor_thickness + below_tank_elbows_height
evap_tail_high_z = (foam_shell_outer_height - hole_shift_from_edge
                    - wall_and_floor_thickness - above_tank_elbows_height)

# The FRONT PORT FIELD — where each penetration crosses the −X wall. One column,
# pitched a bore plus one wall, climbing from the floor. What sets a station's Z is
# NOT the height of the fitting it serves: a line leaves its fitting, turns into the
# lane and climbs it freely, so the field is ordered by what leaves together —
# first reservoir A and the two reed cables (all three out of the pockets' bulkhead
# band), then the vessel's two bottom-plate lines. Everything above the field belongs
# to the copper/PRV SLOT, which takes the rest of the column.
#   Reservoir B is NOT here, and the field is one pitch shorter for it: its line leaves
# by the +Y band and the cap's own conduit (`west_lane_mid_y`, `cap_conduits`), because
# the fitting it feeds hangs in the loft directly over that band and a station on this
# face would send it across the machine and back.
front_port_pitch = 2 * port_hole_radius + port_lane_wall
front_port_order = ("reservoir-a", "reed-cable-a", "reed-cable-b",
                    "carb-water-out", "co2-in")
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

    All five stand on the port lane's centreline, in the wall's own plane, each at its own
    height up the column. The lane is one bore wide (above), so X and Y are the field's and
    only Z is the station's."""
    return ((front_wall_x, port_lane_mid_y, front_port_z(name)), front_port_axis)


def front_port_stations() -> dict:
    """All five, under the names the machine knows them by. The three ABOVE the field are the
    copper/PRV slot's, and `copper_plugs.slot_stations` declares those on this same lane."""
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
for _bx, _by in attachment_xy_positions:
    assert abs(_by) - screw_boss_size / 2 >= outer_shell_y_length / 2 - screw_boss_size, (
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
assert cap_screw_beyond_face >= insert_length, (
    f"an M3 × {cap_screw_length:g} reaches {cap_screw_beyond_face:g} mm past the shell "
    f"face, short of its {insert_length:g} mm insert")
assert cap_screw_beyond_face <= insert_pocket_depth, (
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
# is printed in. The enclosure reads its world poses off them (`_contents.deck_mount`).
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
# another is not mounted, so neither carries a row here. `deck-mounts-land` on the enclosure's
# scorecard re-derives every column that IS here against the cap's own field each build, and
# `deck_mount_cap_room` holds each one [1.5 mm](DECK_MOUNT_CAP_GAP) off whatever else stands in
# the cup for the pour to reach between them.
#   The GROUND STUD stands alone in the aft-east corner, which is also where its three earths
# are: the hub's inlet lug, the brick's chassis, and the relay's own row. It is the only mount
# here tall enough to want a lug fan.
#   The MANIFOLD'S AFT STAND takes the last four rows — the loft's valve trays, each a
# printed plate flat on the lid's outer face like the PSU's brick, bolted down through the
# mount ears its own module carries (`two_valve_tray.mount_stations`,
# `single_valve_tray.mount_stations`). Every ear in the family stands at the same `ear_y` on
# the plate's own centreline, so one station pattern answers for all four. These rows read
# the OTHER way from every row above: a module is placed BY its station, but the trays are
# placed by the enclosure's own fences — the bag-B pair on the rear column's priced face, and
# each lone valve by its own two runs — and these stations stand where the placed ears land.
# The figures are that derivation's result, not a choice; the enclosure's `deck-mounts-land`
# check re-derives them from the placed trays every build and fails with the row a moved tray
# wants, so a drift cannot land silently. The bag-B pair's west cell overhangs the core into
# the −X rib band, past the cap's cavity wall. Every plate seats 9 mm of PETG under the head,
# so the stations take an M3 × 16.
DeckMount = namedtuple("DeckMount", "centre pitch_x pitch_y standoff seat screw")
deck_mounts = {
    #                        centre            pitch_x pitch_y  proud  seat  screw
    "bag-b-tray":  DeckMount((105.25,  17.02),   0.00,  49.50,   0.0,  9.00, 16.0),
    "vk-tray":     DeckMount((  4.00,  61.87),  49.50,   0.00,   0.0,  9.00, 16.0),
    "nozzle-b-tray": DeckMount((-59.48, 27.62), 49.50,   0.00,   0.0,  9.00, 16.0),
    "nozzle-tray": DeckMount((  65.62, -37.51),   0.00,  49.50,   0.0,  9.00, 16.0),
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
    """The tallest standoff in the pack — the foam assembly's own top over its lid's face."""
    return max(deck_mount_standoff(name) for name in deck_mounts)


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
    deck_mount_reach(name) for name in deck_mounts) + deck_mount_bore_relief
for _name in deck_mounts:
    assert deck_mount_reach(_name) >= deck_mount_insert_length, (
        f"deck mount {_name}: an M3 × {deck_mounts[_name].screw:g} through "
        f"{deck_mounts[_name].seat:g} mm of seat reaches {deck_mount_reach(_name):g} mm "
        f"into the column, short of its {deck_mount_insert_length:g} mm insert")


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


for _name in deck_mounts:
    _room, _what = deck_mount_cap_room(_name)
    assert _room >= deck_mount_cap_gap - 1e-9, (
        f"deck mount {_name}: a column stands {_room:.3f} mm off {_what}, inside the "
        f"{deck_mount_cap_gap:g} mm the pour needs to reach between them")


# --- Cap conduits ------------------------------------------------------------
#
# A conduit is one of the cup's own full-height columns carrying a THROUGH bore: liquid
# foam pours around its shank the way it pours around a deck mount's, the lid passes it,
# and a line runs up it from the shell's open top out onto the lid's outer face. The
# service bay stands on that face.
cap_conduit_bore_radius = port_hole_radius   # the ⌀[6.5](PORT_HOLE_DIAMETER) every shell penetration takes
cap_conduit_wall = 2.0
cap_conduit_boss_radius = cap_conduit_bore_radius + cap_conduit_wall
cap_conduit_lid_slip = deck_mount_lid_slip   # per side, a standing column to the lid's clearance hole

# Per conduit: its centre in the CAP'S OWN frame. The cap installs spun a half turn about
# Z (`foam_assembly.spin_xy`), and a half turn is its own inverse — so a conduit that
# stands over a vessel port at (x, y) in the shell's frame is authored at (−x, −y) here,
# and `foam_assembly.cap_conduit_station` turns it back.
#   water-in stands over the TOP BAND, not over its port. Its line leaves the vessel's
# top-plate +Y port LATERALLY — the port carries one of the four TAISHER street elbows every
# vessel port takes (`ledger/bom.md`), with a PTC adapter made up on its female end — runs the
# band between that plate and the cap's floor (`top_band_to_cap`), and climbs this bore to the
# deck. What puts it here is the run
# above the lid: the discharge chain hands the water over on the deck's own west end, and a
# bore on the plate's own column stands under the SeaFlo — which lies across the bay on that
# lid — so a line reaching it has to thread the slot the casting leaves and take its corners
# in there. On this column the run off the chain is one horizontal leg and one fall, and both
# legs seat a stock arc. The band is [14](TOP_BAND) mm against the [25.4 mm](LLDPE_BEND_R) a
# stock arc wants, so the corner OFF THE ELBOW is the one this move buys with, and it is
# potted where it turns.
#   reservoir-b stands over the +Y BAND, not over a port: its line crosses the pocket wall at
# the bulkhead's own height, comes about in the band and climbs the shell's whole height in
# it, potted where it crosses, and this bore is where it reaches the deck. Its X in the cap's
# frame is set by the FITTING it feeds and by the conduit beside it: the divider's stem faces
# −X across the deck, so the run above the lid wants this bore on the stem's own plane, and
# `water-in` stands a millimetre away in the other axis with a line falling the deck's whole
# height on it — so the two bores hold a `LINE_PITCH` between them and this one takes the plane
# nearest the stem that leaves it. Its Y is the band's own lane, held off the corner boss by
# the pour gap. Nothing else uses the +Y band, so the lane is a bore wide the whole way.
cap_conduits = {
    "water-in": (102.0, -80.5),
    "reservoir-b": (109.35, -79.5),
}

# What a line arriving off-axis turns in: the band from a top-plate elbow's own lateral
# axis up to the cap's floor, against the rise a corner of 1/4" LLDPE takes.
tank_top_plate_z = wall_and_floor_thickness + tank_support_ring_height + tank_height
top_band_to_cap = foam_shell_outer_height - (tank_top_plate_z + hole_shift_from_edge)
lldpe_bend_radius = 4.0 * 6.35   # [25.4 mm](LLDPE_BEND_R) — 4 × OD, `_routing.BEND_RATIO`


def cap_conduit_room(name):
    """The least room this conduit leaves to anything else standing in the cup:
    `(mm, what)` — a screw boss, the cavity wall, a deck mount's column."""
    x, y = cap_conduits[name]
    room = [(min(outer_shell_x_length / 2.0 - abs(x), outer_shell_y_length / 2.0 - abs(y))
             - wall_and_floor_thickness - cap_conduit_boss_radius, "the cavity wall")]
    for bx, by in attachment_xy_positions:
        room.append((math.hypot(x - bx, y - by)
                     - screw_boss_size / 2.0 - cap_conduit_boss_radius, "a screw boss"))
    for other in deck_mounts:
        for ox, oy in deck_mount_xy(other):
            room.append((math.hypot(x - ox, y - oy)
                         - deck_mount_boss_radius - cap_conduit_boss_radius,
                         f"the {other} mount"))
    return min(room)


for _name in cap_conduits:
    _room, _what = cap_conduit_room(_name)
    assert _room >= deck_mount_cap_gap - 1e-9, (
        f"cap conduit {_name}: the column stands {_room:.3f} mm off {_what}, inside the "
        f"{deck_mount_cap_gap:g} mm the pour needs to reach between them")


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
        build_hole_punch(
            origin=(pocket_hole_x, y, z),
            hole_punch_radius=hole_punch_radius,
            hole_punch_height=y - port_lane_mid_y,
            direction=-1,
        )
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


def port_to_shell(solid):
    """Carry a solid from the PORT FRAME into the shell's.

    The port frame is the one every penetration is authored in, the copper-plug
    stack among them: x lateral across the face, −y out through it, z the shell's
    own. One quarter turn about Z puts its −y on the shell's −X, and one slide puts
    its lateral centreline on the port lane. Authoring there is what keeps the plug
    stack and the slot it fills a single reading — a plug is a part that plugs a slot
    in a wall, and that is the frame that says so; a pose turned by hand alongside a
    slot cut by hand is two implementations of one transform."""
    return (solid.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), -90.0)
                 .translate(cq.Vector(0.0, port_lane_mid_y, 0.0)))


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
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "WALL_AND_FLOOR_THICKNESS": 1,
            "COIL_RADIAL_CLEARANCE": 1,
            "ABOVE_TANK_ELBOWS_HEIGHT": 1,
            "BELOW_TANK_ELBOWS_HEIGHT": 1,
            "PORT_HOLE_DIAMETER": 2,
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
        },
    )
    print("-> _cold_core_interface.py (self)")
