"""Reservoir — open-top `[`-shaped PETG cup that stands on the floor of each
bag pocket of the foam shell, closed by a separately-printed cap clamped
through a TPU gasket. Mirrored ±X. Carries the level-sensing rod, and its
cap carries flush TPU tube grips and a separate bidirectional air tube.

Same coordinate convention as ../foam-shell/: +Z vertical, +X is
the bag-pocket axis (two cavities sit on opposite sides), +Y is
perpendicular to it."""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(0, str(_here.parent))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))

from world_workplane import WorldWorkplane, xy_plane_z_up
import fits
from _cadq_export import export_assembly
import _reservoir_ports as tube_ports
import _materials as _mat
from _materials import one_body
from docgen import substitute_md, substitute_py_comments
from _cold_core_interface import (
    cap_conduit_shell_xy,
    bag_pocket_far_inner_x,
    bag_pocket_y_inner_max,
    bag_pocket_floor_top_z,
    bag_pocket_walls_top_z,
    pocket_centerward_arc_outer_radius,
    port_hole_radius,
    reservoir_clearance,
    reservoir_floor_thickness,
    reservoir_draw_port,
    reservoir_fill_port,
    reservoir_fill_sides,
    level_rod_y,
    lldpe_tube_od,
)
from _reed_channels import reeds_per_reservoir
import _float_interface as _float


def _z_cylinder(anchor_xy, z_range, diameter):
    """Solid cylinder, axis along world +Z, centered at anchor_xy =
    (world_x, world_y), spanning z_range = (z_bottom, z_top)."""
    x, y = anchor_xy
    z_bottom, z_top = z_range
    return (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=z_bottom)
        .center(x, y)
        .circle(diameter / 2)
        .extrude(z_top - z_bottom)
    )


# The body is an OPEN-TOP `[` cup: floor + four walls (far, +Y, −Y,
# centerward concave-curve) of uniform wall-thickness PETG, closed at the
# top by a separately-printed cap clamped through a TPU gasket with six M3
# screws into heat-set inserts. The floor is one flat slab of that same
# thickness, and its underside stands on the bag pocket's own floor, one
# reservoir_clearance over it — the body fills its pocket floor to rim.
#
# Equals reservoir_floor_thickness on the shell side.
# [3 mm](RESERVOIR_WALL_T) — uniform PETG thickness for floor + every wall.
reservoir_wall_thickness = reservoir_floor_thickness


# Fillets where the centerward curve meets the ±Y walls. At
# y = ±[70.25 mm](OUTER_Y_MAX) the outer centerward curve (radius
# [80.75 mm](OUTER_CENTERWARD_R)) meets the outer ±Y walls at a [30°](OUTER_TAB_ANGLE)
# interior-angle tab; at y = ±[67.25 mm](INNER_Y_MAX) the inner centerward curve
# meets the inner ±Y walls inside the syrup volume at [37°](INNER_CORNER_ANGLE).
# [6 mm](OUTER_FILLET_R) is at least body_boss_radius ([5 mm](BODY_BOSS_R)), so the
# corner bosses (positions 4/5, centered on the outer fillet) sit fully inside
# the post-fillet wall material.
outer_corner_fillet_radius = 6.0
inner_corner_fillet_radius = 6.0


# Cap geometry. Base plate (top, the flat surface) + perimeter wall
# (bottom, the "lip" hanging down around the gasket joint). The base
# plate hosts the counterbored screw heads on its flat top face; the
# perimeter wall provides depth for the screw shaft to pass through to
# the gasket + body insert below.
cap_base_thickness = tube_ports.plate_thickness  # flat top spans the cavity unsupported and hosts the screw counterbores
cap_wall_height = 5.0
cap_wall_width = 6.0

# Screw recess geometry. M3 SHCS head OD ~5.5 mm → ⌀[5.8 mm](CAP_COUNTERBORE_D)
# counterbore. The counterbore recesses the head through the full base plate;
# the clearance hole through the perimeter wall carries the shaft to the
# gasket + body insert below.
cap_counterbore_diameter = 5.5 + 2.0 * fits.slip
# Cap prints exterior-face-down (-Z). The supported screw seats retreat into
# the 5 mm perimeter wall; screw axes and the gasket rim retain their datums.
cap_counterbore_depth = cap_base_thickness + fits.supported_surface
cap_clearance_hole_diameter = 3.0 + 2.0 * fits.slip


# TPU 85A flat gasket between the body wall top and the cap base plate
# bottom, compressed by the six M3 × 12 screws. [5 mm](GASKET_STRIP_W)-wide perimeter ring
# covering the body wall top and extending inward over the cavity opening;
# circular pads at each insert position give the screw clamp a uniform
# compressed disk; ⌀[3.3 mm](CAP_CLEARANCE_HOLE_D) clearance holes through each pad.
gasket_thickness = 2.0
gasket_strip_width = 5.0


# Cap-local Z ranges, anchored at the cap's own z=0 (perimeter wall
# bottom). In the assembled stack the cap sits at world z = outer_z_range[1]
# + gasket_thickness.
cap_perimeter_z_range = (0, cap_wall_height)
cap_base_z_range = (cap_wall_height, cap_wall_height + cap_base_thickness)
# [9 mm](CAP_TOTAL_H) — perimeter-wall height + base-plate thickness.
cap_total_height = cap_base_z_range[1]


# The flat plate captures three flush TPU spools: fill, draw and independent air.
# The casing conduits guide the liquid lines; each air line has its own protected
# 5.2mm passage through the top cup and lid.
fill_position = reservoir_fill_port
draw_position = reservoir_draw_port
vent_position = tube_ports.air_position
fill_bore_diameter = tube_ports.liquid_grip['waist_d']


# One fill station per physical reservoir — A and B — so this is the reservoir count itself,
# read by firmware's own census (reeds, rods) and the bench cards rather than kept there.
reservoir_count = len(fill_position)


# Level-sensing rod: a vertical [3.175 mm](ROD_DIAMETER) (1/8") × 305 mm (12") 316 SS
# round rod, body-anchored and cap-registered. A small magnetic float
# slides up and down the rod as the syrup level changes; [4](REEDS_PER_RES) reed
# switches mounted outside the reservoir pocket's far +X wall detect the
# float's position. They drop into the foam shell's reed channel as one
# pre-soldered column after the body pour has cured — held mechanically,
# never foam-encapsulated (`level-sensing.md`). Same
# rod SKU as the carbonator's reed+float level sensing — Tandefio B0CY4DWJFQ;
# see `hardware/README.md` "Carbonation".
#
#   - Body: a solid PETG cylindrical boss rises from the flat floor at
#     (±rod_position_x, rod_position_y); a blind bore from above stops
#     rod_anchor_boss_floor mm short of the boss base, so the rod tip
#     bottoms out on printed-solid PETG and the floor stays unbroken.
#   - Cap: a hollow register boss hangs down from the underside with a
#     downward-opening blind bore around the rod's top. The rod is captured
#     at BOTH ends against float-load lean.
#
# Sits on the +Y half, in the wider part of the cavity (~38 mm wide at y=+45
# vs ~24 mm at y=0) where the donut float has clearance, clear of all screw
# bosses and the vent boss.
# `rod_position_x` is struck off the cavity's own far wall, further down with that wall.
rod_position_y = level_rod_y  # y of the rod centerline; does NOT mirror with side —
# the reed column outside stands on this same station (`_cold_core_interface.level_rod_y`)
rod_diameter = _float.guide_diameter  # 1/8" 316 SS round rod OD
# [3.475 mm](ROD_BORE) — rod ⌀ + 0.3 mm diametral slip clearance; shared by body anchor boss and cap register boss.
rod_bore = rod_diameter + 2.0 * fits.slip  # stationary rod seats; float's running bore is separate
# [7.475 mm](ROD_BOSS_OD) — bore ⌀ + 4 mm (2 mm radial wall); shared by body anchor and cap register bosses.
rod_boss_od = rod_bore + 4.0  # 2 mm radial wall around the bore
rod_register_boss_height = 2.0  # CAP-side boss EXTRA height beyond cap rim
rod_anchor_boss_height = 6.0  # BODY-side anchor boss
rod_anchor_boss_floor = 0.0  # printed-solid PETG floor INSIDE the body boss


# Heat-set insert + screw spec. ruthex M3 brass heat-set inserts, RX-M3x5.7
# (same as foam-shell cap-stack joinery). Insert ⌀4.6 knurl × length 5.7 mm;
# pocket is 4 mm bore × [7 mm](INSERT_POCKET_DEPTH) deep (5.7 mm insert + 1.3 mm relief). Screws:
# BNUOK M3 × 12 mm DIN 912 SHCS, 304 stainless steel, 18-8 (Amazon
# B0DJQGMQZM). The M3 × 12 length suits the reservoir's thinner cap-stack
# geometry (under-head stack is 7 mm cap-plus-gasket vs the foam-shell's
# ~19 mm).
# With M3 × 12, the shaft seats 5 mm into the insert and stops 0.7 mm short
# of its blind end, so the screw is thread-limited and not pocket-limited:
# the insert's last 0.7 mm is grip in the PETG, not thread the screw takes.
# THIS JOINT IS NEVER REOPENED. The cap is bolted down onto its gasket at
# CC-09 and the reservoir goes into the foam; refill is through the funnel
# and the fill port, not through this cap. What the insert has to hold is
# gasket preload against syrup for the life of the machine, in a part no
# one can reach to re-torque — which is what the longer body buys.
insert_pocket_radius = 2.0
insert_pocket_depth = 7.0

# Boss + gasket-pad radii. The body boss is the ø4 insert pocket + a
# boss_annulus PETG wall (the material that carries the heat-set insert
# grip + screw clamp load). The cap boss and the gasket pad share the body
# boss radius so the screw-clamp stack — body boss / gasket pad / cap boss —
# is one uniform compressed disk at each insert position.
boss_annulus = 3.0
# [5 mm](BODY_BOSS_R) — insert pocket radius + boss_annulus.
body_boss_radius = insert_pocket_radius + boss_annulus
# [5 mm](CAP_BOSS_R) — matches the body boss.
cap_boss_radius = body_boss_radius
gasket_pad_radius = body_boss_radius  # matches the body boss (clamp-stack footprint)

# Body boss vertical layout (extruding downward from the wall top):
#   top [7 mm](INSERT_POCKET_DEPTH):  pocket (ø4 hole for heat-set insert + screw shaft)
#   below:     solid ⌀[10 mm](BODY_BOSS_D) cylinder. Built extra-long (extending below
#              the intended boss-bottom z) and then cut with a flat
#              45° plane through the wall at that boss-bottom z, so
#              the wall side of the cylinder stays straight (and gets
#              fused into the wall) and the cavity side of the
#              cylinder gets sliced off at 45° — an FDM-printable
#              overhang anchored on the wall.
#
# Every body boss gets a 45° flat cut at its bottom. Bosses 1/2/3/6
# sit 2 mm inside the cavity from the wall's inner face; the cut
# starts at the wall inner face / corner at z = boss_bottom_z, NOT
# at the boss center, so the kept material on the wall side reaches
# all the way down to that z. Bosses 4/5 (curve × ±Y corner, at the
# outer-fillet center) sit inside the post-fillet wall material and
# use a virtual pivot 2 mm along the wall direction so the cut depth
# stays within the [7 mm](INSERT_POCKET_DEPTH) heat-set pocket (see body_boss_cut_info_for_side_plus_1
# below). The outer fillet radius ([6 mm](OUTER_FILLET_R)) is at least body_boss_radius,
# so the corner-boss disks sit inside the fillet arc.
boss_height = 15.0  # 7 mm pocket + 8 mm of solid+cut (the +8 keeps a solid floor under the pocket after the 45° cut, including the deeper diagonal cut on the corner bosses)
_cyl_extra_below_bottom = 5.0  # extra cylinder length to be sliced off by the cut

# Insert / screw positions, derived from the wall geometry so the body
# and cap bosses at each position fit fully inside the outer envelope
# (the larger of the two boss radii sets the inset).
#
# Outer envelope (body and cap share this footprint). Inner extents
# (cavity side) sit one wall thickness in on the rectangular sides and
# one wall thickness OUT on the centerward concave arc.
outer_far_x_abs = bag_pocket_far_inner_x - reservoir_clearance
outer_y_max = bag_pocket_y_inner_max - reservoir_clearance
outer_centerward_radius = pocket_centerward_arc_outer_radius + reservoir_clearance
inner_far_x_abs = outer_far_x_abs - reservoir_wall_thickness
inner_y_max = outer_y_max - reservoir_wall_thickness
inner_centerward_radius = outer_centerward_radius + reservoir_wall_thickness

# The 36 mm ASA Aero float clears the wet wall without relying on wall contact.
# The guide's nominal axis is 20 mm inboard; body and cap use the same station.
float_capsule_od = _float.diameter
float_capsule_bore = _float.bore_diameter
rod_position_x = inner_far_x_abs - _float.rod_axis_from_inner_wall

# Interior angles of the corners where the centerward arc meets the ±Y walls
# — DERIVED from the geometry, not eyeballed. The arc tangent crosses the
# horizontal ±Y wall at acos(y_max / R): a sharp "pointy tab" on the outer
# envelope ([30°](OUTER_TAB_ANGLE)) and a gentler corner on the inner cavity
# boundary ([37°](INNER_CORNER_ANGLE)).
outer_tab_interior_angle = math.degrees(math.acos(outer_y_max / outer_centerward_radius))
inner_corner_interior_angle = math.degrees(math.acos(inner_y_max / inner_centerward_radius))

# Body Z ranges. outer_z_range is the body's vertical extent (floor's
# outer face to wall top). inner_z_range is the cavity's extent (cavity
# floor sits one wall up; top opens to the cap above the gasket).
# cap_stack_above_body is how much room the gasket + cap takes above
# the body's wall top — leaves the cap's top face flush at z=[213.2 mm](CAP_TOP_Z)
# ([0.25 mm](RESERVOIR_CLEARANCE) clear of the bag-pocket wall top); body alone is [199.9 mm](RESERVOIR_H) tall.
# [11 mm](CAP_STACK_H) — gasket + cap perimeter wall + cap base plate.
cap_stack_above_body = gasket_thickness + cap_wall_height + cap_base_thickness
outer_z_range = (
    bag_pocket_floor_top_z + reservoir_clearance,
    bag_pocket_walls_top_z - reservoir_clearance - cap_stack_above_body,
)
inner_z_range = (outer_z_range[0] + reservoir_wall_thickness, outer_z_range[1])
# Assembled-stack references — pinned into the docstring/comments below.
cap_assembly_lift = outer_z_range[1] + gasket_thickness  # [204.2 mm](CAP_ASSEMBLY_LIFT) — cap-local z=0 lands here on the body
cap_top_z = cap_assembly_lift + cap_total_height          # assembled cap top face

# The wet floor is the cavity's own bottom: flat, one wall over the body's underside.
rod_floor_z = inner_z_range[0]

# Level-sensing rod cut length. Seat-to-seat = the top register seat (cap-local
# cap_wall_height, raised to assembled coords by cap_assembly_lift) minus the
# body anchor-boss bore floor; cut reservoir_rod_clearance under so the rod
# never holds the cap off its gasket. (Seat-to-seat
# [203.9 mm](RESERVOIR_SEAT_TO_SEAT); this is the cut figure.)
reservoir_rod_clearance = fits.slip  # static end clearance; the lower end seats on its datum
reservoir_rod_len = (
    (cap_assembly_lift + cap_wall_height)
    - (rod_floor_z + rod_anchor_boss_floor)
    - reservoir_rod_clearance
)  # [203.8 mm (8.02 in)](RESERVOIR_ROD_LEN) — 1/8" 316 SS rod, seat-to-seat − 0.15 mm

# The bosses are wider than the float bore and are its end stops. These are
# magnet-centre travel limits, not liquid level or reed switching measurements.
float_magnet_travel_z = (
    rod_floor_z + rod_anchor_boss_height + _float.magnet_midplane,
    cap_assembly_lift - rod_register_boss_height - (_float.height - _float.magnet_midplane),
)
# The four reeds span that whole travel, end stop to end stop, at the whole-millimetre
# pitch that fits it — so the column reads the reservoir from its floor to its cap.
_float_travel = float_magnet_travel_z[1] - float_magnet_travel_z[0]
reservoir_reed_pitch = float(math.floor(_float_travel / (reeds_per_reservoir - 1)))
_reed_span = (reeds_per_reservoir - 1) * reservoir_reed_pitch
_reed_mid = sum(float_magnet_travel_z) / 2
reservoir_reed_centres_z = tuple(_reed_mid - _reed_span / 2 + i * reservoir_reed_pitch
                               for i in range(reeds_per_reservoir))
assert _reed_span < _float_travel

# The dip tube's mouth: the 45° cut's centre, one tube radius over the floor its tip rests on.
dip_tube_mouth_z = rod_floor_z + lldpe_tube_od / 2

# X position where the centerward arc meets ±outer_y_max (the acute
# "tab" corner that gets filleted on every outer envelope — body,
# cap, gasket). Same shape applied at the inner cavity edge.
outer_corner_x = math.sqrt(outer_centerward_radius**2 - outer_y_max**2)
inner_corner_x = math.sqrt(inner_centerward_radius**2 - inner_y_max**2)

# Inset equals the outer corner fillet radius so the corner bosses (1/2,
# 4/5) sit on the fillet centers; with the boss radius ≤ this, every boss
# stays inside the outer envelope (no protrusion past the outer face, no
# overhang into the bag pocket clearance).
_screw_setback = outer_corner_fillet_radius

# Positions 1/2 — inset [6 mm](OUTER_FILLET_R) from outer +X face × outer ±Y face.
_corner_xy_x = outer_far_x_abs - _screw_setback
_corner_xy_y = outer_y_max - _screw_setback

# Position 3 — inset [6 mm](OUTER_FILLET_R) from outer +X face, y = 0.
_far_mid_x = outer_far_x_abs - _screw_setback

# Position 6 — [6 mm](OUTER_FILLET_R) outward from outer curve (radially), y = 0.
_curve_apex_x = outer_centerward_radius + _screw_setback

# Positions 4/5 — corner of outer curve × outer ±Y face. The corner
# is filleted at outer_corner_fillet_radius (= [6 mm](OUTER_FILLET_R)). The fillet
# center is the unique point that is [6 mm](OUTER_FILLET_R) from BOTH the outer +Y
# face and the outer curve, measured along the shortest path. The
# ⌀[10 mm](BODY_BOSS_D) body boss disk (radius [5 mm](BODY_BOSS_R)) fits within the
# [6 mm](OUTER_FILLET_R) fillet arc, so at these positions the boss material sits inside
# the post-fillet wall. The 45° cut still applies (see the cut-info
# entries for 4/5 below) but uses a virtual pivot rather than the
# literal corner.
_corner_curve_y = outer_y_max - outer_corner_fillet_radius
_corner_curve_r = outer_centerward_radius + outer_corner_fillet_radius
_corner_curve_x = math.sqrt(_corner_curve_r**2 - _corner_curve_y**2)

# Insert positions for the side=+1 reservoir; sign flips for −1.
insert_positions_for_side_plus_1 = [
    (_corner_xy_x, _corner_xy_y),  # 1: +X × +Y outer corner
    (_corner_xy_x, -_corner_xy_y),  # 2: +X × −Y outer corner
    (_far_mid_x, 0.0),  # 3: +X face midpoint
    (_corner_curve_x, _corner_curve_y),  # 4: curve × +Y outer corner (at outer fillet center)
    (_corner_curve_x, -_corner_curve_y),  # 5: curve × −Y outer corner (at outer fillet center)
    (_curve_apex_x, 0.0),  # 6: curve apex
]

# For each body boss, record the wall pivot point (the (x, y) on the
# wall's inner face from which the cut plane originates) and the unit
# direction in XY from the boss center toward that pivot. The cut
# plane passes through (pivot_x, pivot_y, boss_bottom_z) and is
# tilted at 45° from horizontal, rising away from the wall — keep
# above, cut below. Bosses 4/5 (corner-of-curve positions) use a
# virtual pivot 2 mm along wall_dir from the boss center because the
# literal inner-wall corner is too far for a sensible cut depth (a
# [8.894 mm](CORNER_CURVE_DIST) cut depth would eat into the 7 mm heat-set pocket).
#
# Values stored for side=+1; the x component is multiplied by `side`
# in the body-boss loop to mirror across x=0 for side=−1.
_far_wall_inner_x = outer_far_x_abs - reservoir_wall_thickness
_plus_y_wall_inner_y = outer_y_max - reservoir_wall_thickness
_curve_inner_x_at_y0 = outer_centerward_radius + reservoir_wall_thickness
_inv_sqrt2 = 1.0 / math.sqrt(2.0)

# Bosses 4 / 5 need their cut direction pointed at the inner-wall
# CORNER (where the inner curve at radius _curve_inner_x_at_y0 = 76
# meets the inner ±Y wall at y = ±_plus_y_wall_inner_y = ±[67.25 mm](INNER_Y_MAX)), not
# at the closest point on the curve along the inward radial line.
# Pointing at the corner is the same pattern bosses 1 / 2 use (their
# cuts slope down away from the +X × ±Y inner corner). For boss 4
# the corner is at (≈[49.91 mm](INNER_CORNER_CURVE_X), [67.25 mm](INNER_Y_MAX)),
# [8.894 mm](CORNER_CURVE_DIST) from the boss in the (−X, +Y) direction — too
# far to use as a literal pivot (a [8.894 mm](CORNER_CURVE_DIST) cut depth would
# eat into the 7 mm heat-set pocket). Instead, take
# the unit vector toward the corner as wall_dir, and place the pivot
# VIRTUALLY at 2 mm along that direction from the boss center, so
# the cut depth at boss center matches boss 6 (the curve apex) and
# stays well clear of the pocket.
_inner_corner_curve_x = math.sqrt(_curve_inner_x_at_y0**2 - _plus_y_wall_inner_y**2)
_corner_curve_to_inner_corner_dx = _inner_corner_curve_x - _corner_curve_x
_corner_curve_to_inner_corner_dy = _plus_y_wall_inner_y - _corner_curve_y
_corner_curve_to_inner_corner_dist = math.sqrt(
    _corner_curve_to_inner_corner_dx**2 + _corner_curve_to_inner_corner_dy**2
)
_corner_curve_wall_dir_x = _corner_curve_to_inner_corner_dx / _corner_curve_to_inner_corner_dist
_corner_curve_wall_dir_y = _corner_curve_to_inner_corner_dy / _corner_curve_to_inner_corner_dist
_corner_curve_pivot_distance = 2.0
_corner_curve_virtual_pivot_x = _corner_curve_x + _corner_curve_pivot_distance * _corner_curve_wall_dir_x
_corner_curve_virtual_pivot_y = _corner_curve_y + _corner_curve_pivot_distance * _corner_curve_wall_dir_y

body_boss_cut_info_for_side_plus_1 = {
    # (boss_x, boss_y) → (pivot_x, pivot_y, wall_dir_x, wall_dir_y)
    # wall_dir is a UNIT vector in XY pointing from the boss center toward the wall pivot.
    (_corner_xy_x, _corner_xy_y):
        (_far_wall_inner_x, _plus_y_wall_inner_y, _inv_sqrt2, _inv_sqrt2),  # 1
    (_corner_xy_x, -_corner_xy_y):
        (_far_wall_inner_x, -_plus_y_wall_inner_y, _inv_sqrt2, -_inv_sqrt2),  # 2
    (_far_mid_x, 0.0):
        (_far_wall_inner_x, 0.0, 1.0, 0.0),  # 3
    (_corner_curve_x, _corner_curve_y):
        (_corner_curve_virtual_pivot_x, _corner_curve_virtual_pivot_y,
         _corner_curve_wall_dir_x, _corner_curve_wall_dir_y),  # 4
    (_corner_curve_x, -_corner_curve_y):
        (_corner_curve_virtual_pivot_x, -_corner_curve_virtual_pivot_y,
         _corner_curve_wall_dir_x, -_corner_curve_wall_dir_y),  # 5
    (_curve_apex_x, 0.0):
        (_curve_inner_x_at_y0, 0.0, -1.0, 0.0),  # 6
}


def _build_envelope(side, z_range, wall_offset=0.0):
    """`[`-shape solid spanning z_range: rectangle on three sides +
    concave cylindrical cutout on the centerward side. Used for body,
    cap, and gasket footprints. `wall_offset` shrinks the footprint
    inward by that amount on every face (negative growth on the
    concave radius); wall_offset=0 is the outer envelope,
    wall_offset=wall_thickness is the inner cavity."""
    floor_z, top_z = z_range
    height = top_z - floor_z
    far_x_abs = outer_far_x_abs - wall_offset
    y_max = outer_y_max - wall_offset
    centerward_radius = outer_centerward_radius + wall_offset
    rect = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=floor_z)
        .center(side * far_x_abs / 2, 0)
        .rect(far_x_abs, 2 * y_max)
        .extrude(height)
    )
    cyl = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=floor_z)
        .circle(centerward_radius)
        .extrude(height)
    )
    return rect.cut(cyl)


def _fillet_edge_at(solid, point, radius):
    """Fillet the edge nearest the given world point with the given radius."""
    return (
        solid
        .edges(cq.NearestToPointSelector(point))
        .fillet(radius)
    )


def _fillet_pair_at_y(solid, x_signed, z_mid, y_range, radius):
    """Fillet the two vertical edges nearest (x_signed, ±y_range, z_mid)
    with the given radius. Used to round both +Y and −Y corners on a
    shared outer profile."""
    for sharp_y in (y_range, -y_range):
        solid = _fillet_edge_at(solid, (x_signed, sharp_y, z_mid), radius)
    return solid


def build_reservoir_body(side=1):
    """Open-top `[`-shaped PETG body with uniform wall-thickness walls and one flat
    floor, sized to fit one side of the bag-pocket cavity with reservoir_clearance
    mm of slack on every outer face, the floor's underside included. Six insert
    bosses at the top perimeter (one per insert_positions_for_side_plus_1) host
    ruthex M3 inserts in ø4 × 7 mm pockets. side=+1 builds the +X reservoir;
    side=−1 the −X (mirror across x=0)."""
    outer_envelope = _build_envelope(side, outer_z_range)
    inner_cavity = _build_envelope(side, inner_z_range, wall_offset=reservoir_wall_thickness)

    body = outer_envelope.cut(inner_cavity)

    # Fillet the four sharp corners where the centerward concave curve
    # meets the ±Y walls — applied to the bare wall geometry BEFORE
    # unioning the insert bosses, because two of the inner corners
    # coincide with boss positions ([49.91 mm](INNER_CORNER_CURVE_X), ±[67.25 mm](INNER_Y_MAX)) and unioning a cylinder
    # there would replace the sharp edge with a curved boss-to-wall
    # transition that the fillet operation can't pick up.
    #
    # Exterior corners (outer perimeter, [30°](OUTER_TAB_ANGLE) interior angle) are pointy
    # tabs. Interior corners (cavity boundary, [37°](INNER_CORNER_ANGLE) interior angle) are
    # sharp inside the syrup volume. Both get rounded with the same
    # radius for visual consistency.
    z_mid_body = (outer_z_range[0] + outer_z_range[1]) / 2

    def _apply_outer_fillets(solid):
        """Round both outer corner pairs (curve × ±Y acute tabs, +X ×
        ±Y 90° corners). Bosses 1/2 sit at the +X × ±Y fillet centers
        (boss disk inscribes the fillet arc, same trick as bosses 4/5 —
        see body_boss_cut_info), so boss material stays inside the
        rounded wall and the 45° overhang cut still applies normally."""
        solid = _fillet_pair_at_y(solid, side * outer_corner_x, z_mid_body, outer_y_max, outer_corner_fillet_radius)
        solid = _fillet_pair_at_y(solid, side * outer_far_x_abs, z_mid_body, outer_y_max, outer_corner_fillet_radius)
        return solid

    body = _apply_outer_fillets(body)

    # Separately-filleted outer envelope, used below to clip the wedge
    # so the wedge's sharp [-shape corner at (inner_corner_x, ±inner_y_max)
    # can't poke through the outer fillet arc. (Without this clip, the
    # wedge restores the pre-fillet outer corner geometry in the wedge's
    # z range, leaving a sharp tab visible from the centerward face in a
    # narrow Z range matching the wedge's extent.)
    outer_envelope_filleted = _apply_outer_fillets(_build_envelope(side, outer_z_range))

    # Inner fillets: curve × ±Y (sharp crevice in syrup volume) and
    # +X × ±Y (analogous interior corner). Same radius as outer for
    # visual consistency. Rounds the full-height vertical cavity-corner
    # edges so syrup can't pool in a sharp crevice; the V floor is
    # unioned in afterward and meets these rounded corners cleanly.
    body = _fillet_pair_at_y(body, side * inner_corner_x, z_mid_body, inner_y_max, inner_corner_fillet_radius)
    body = _fillet_pair_at_y(body, side * inner_far_x_abs, z_mid_body, inner_y_max, inner_corner_fillet_radius)

    # Insert bosses at the top perimeter (unioned AFTER the fillets so
    # the bosses sit on top of the now-rounded corners cleanly).
    boss_bottom_z = outer_z_range[1] - boss_height
    pocket_bottom_z = outer_z_range[1] - insert_pocket_depth

    for (px, py) in insert_positions_for_side_plus_1:
        px_signed = px * side
        cut_info = body_boss_cut_info_for_side_plus_1.get((px, py))

        # A boss that takes a 45° cut runs _cyl_extra_below_bottom past
        # the intended boss bottom so the cut has material to slice off;
        # otherwise the cylinder starts at the intended bottom.
        if cut_info is None:
            cyl_bottom_z = boss_bottom_z
        else:
            cyl_bottom_z = boss_bottom_z - _cyl_extra_below_bottom
        boss = _z_cylinder((px_signed, py), (cyl_bottom_z, outer_z_range[1]), 2 * body_boss_radius)

        if cut_info is not None:
            pivot_x, pivot_y, dir_x, dir_y = cut_info
            pivot_x_signed = pivot_x * side
            dir_x_signed = dir_x * side
            # Cut plane: passes through (pivot_x_signed, pivot_y, boss_bottom_z),
            # tilted 45° from horizontal with the high side toward the
            # wall (along (dir_x_signed, dir_y) in XY). Plane normal
            # = (wall_dir_x, wall_dir_y, 1), magnitude sqrt(2), 45° from
            # vertical when wall_dir is unit in XY. xDir is perpendicular
            # to normal in the XY plane (so the workplane's Y axis is
            # the cut plane's "horizontal" axis).
            cut_plane = cq.Plane(
                origin=(pivot_x_signed, pivot_y, boss_bottom_z),
                xDir=(-dir_y, dir_x_signed, 0),
                normal=(dir_x_signed, dir_y, 1),
            )
            # Half-space below the cut plane (toward cavity-and-down)
            # is the volume to remove. Extrude a large rect on the plane
            # in the -normal direction.
            cut_tool = (
                cq.Workplane(cut_plane)
                .rect(500, 500)
                .extrude(-500)
            )
            boss = boss.cut(cut_tool)

        body = body.union(boss)

        # +0.1 extrude overshoot breaks the top surface cleanly.
        pocket = _z_cylinder(
            (px_signed, py),
            (pocket_bottom_z, pocket_bottom_z + insert_pocket_depth + 0.1),
            2 * insert_pocket_radius,
        )
        body = body.cut(pocket)

    # Level-sensing rod body anchor: a solid cylindrical boss rising
    # from the flat floor at (±rod_position_x, rod_position_y), with a
    # blind bore cut into it from above — bore stops rod_anchor_boss_floor
    # mm short of the boss base so the printed PETG floor inside the boss
    # is what the rod tip bottoms out on.
    #
    # Unioned after every selector-based fillet and cut so the boss
    # cannot perturb an earlier edge/face selection.
    rod_x_signed = rod_position_x * side
    rod_anchor_boss_cylinder = _z_cylinder(
        (rod_x_signed, rod_position_y),
        (rod_floor_z, rod_floor_z + rod_anchor_boss_height),
        rod_boss_od,
    )
    body = body.union(rod_anchor_boss_cylinder)

    # Blind bore: base rod_anchor_boss_floor mm above the floor, extruded up
    # through the top of the boss with a +0.1 overshoot so the cut
    # cleanly opens at the boss top face.
    bore_bottom_z = rod_floor_z + rod_anchor_boss_floor
    rod_bore_cut = _z_cylinder(
        (rod_x_signed, rod_position_y),
        (bore_bottom_z, bore_bottom_z + rod_anchor_boss_height - rod_anchor_boss_floor + 0.1),
        rod_bore,
    )
    body = body.cut(rod_bore_cut)

    return body.unwrap()


def build_reservoir_cap(side=1):
    """PETG cap that sits on top of the reservoir body through a [2 mm](GASKET_THICKNESS)
    TPU gasket. Built in cap-local coordinates spanning cap_perimeter_z_range
    (the downward-hanging rim) and cap_base_z_range (the flat top, full
    `[` footprint). The cap's top face hosts six counterbored M3 holes
    flush with the screw heads, clearance holes continuing through the
    perimeter wall into the body's insert pockets below. Six cap-side
    bosses mirror the body bosses inside the perimeter wall, giving the
    gasket a matching cross-section at each screw position.

    To visualize the assembled stack, translate the cap up by
    cap_assembly_lift (= outer_z_range[1] + gasket_thickness; the pinned value
    lives in the comment at that constant, since docgen does not reach
    docstrings)."""
    # Perimeter wall (outer − inner footprint) at the BOTTOM of the cap.
    # The "lip" that hangs down around the gasket.
    perimeter_outer = _build_envelope(side, cap_perimeter_z_range)
    perimeter_inner = _build_envelope(side, cap_perimeter_z_range, wall_offset=cap_wall_width)
    perimeter_wall = perimeter_outer.cut(perimeter_inner)

    # Base plate (full footprint) at the TOP of the cap. The flat
    # surface the user sees from above; hosts the counterbores for
    # the screw heads.
    base = _build_envelope(side, cap_base_z_range)

    cap = base.union(perimeter_wall)

    # Fillet the two exterior sharp corners (same outer footprint as
    # the body, so same sharp tabs). Done BEFORE the bosses are
    # unioned because the corner bosses (4/5) sit exactly at the
    # outer-fillet center, where the boss disk's outer edge IS the
    # fillet arc — unioning them first leaves no sharp corner edge
    # for the fillet selector to find, and CadQuery silently produces
    # malformed geometry (a leftover triangular tab where the corner
    # tip should have been rounded off). Filleting first, then
    # unioning the bosses via .pushPoints, leaves the fillet correct;
    # at positions 4/5 the boss disk sits inside the post-fillet
    # perimeter wall material so its union is geometrically a no-op,
    # and the bosses at the other four positions union normally.
    z_mid_cap = cap_total_height / 2

    # Match the body's outer fillets so the cap and body share the same
    # outer envelope (gasket between them sees the same footprint on
    # both sides).
    cap = _fillet_pair_at_y(cap, side * outer_corner_x, z_mid_cap, outer_y_max, outer_corner_fillet_radius)
    cap = _fillet_pair_at_y(cap, side * outer_far_x_abs, z_mid_cap, outer_y_max, outer_corner_fillet_radius)

    # At each insert position: cap-side boss thickening the perimeter
    # wall inward (matching the body boss footprint so the gasket sees
    # a consistent compression cross-section), ø[3.3 mm](CAP_CLEARANCE_HOLE_D) clearance hole
    # through the cap for the screw shaft, and ø[5.8 mm](CAP_COUNTERBORE_D) counterbore recessing
    # the M3 SHCS head flush with the cap's top face.
    insert_anchors = [(px * side, py) for (px, py) in insert_positions_for_side_plus_1]
    bosses = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=cap_perimeter_z_range[0])
        .pushPoints(insert_anchors)
        .circle(cap_boss_radius)
        .extrude(cap_perimeter_z_range[1] - cap_perimeter_z_range[0])
    )
    cap = cap.union(bosses)
    clearances = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=-0.1)
        .pushPoints(insert_anchors)
        .circle(cap_clearance_hole_diameter / 2)
        .extrude(cap_total_height + 0.2)
    )
    cap = cap.cut(clearances)
    counterbores = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=cap_total_height - cap_counterbore_depth)
        .pushPoints(insert_anchors)
        .circle(cap_counterbore_diameter / 2)
        .extrude(cap_counterbore_depth + 0.1)
    )
    cap = cap.cut(counterbores)

    # The independent air tube passes through a flush TPU spool in this plain,
    # open seat. Its lower end opens directly into the reservoir headspace.
    vent_xy = vent_position[side]
    cap = cap.cut(tube_ports.seat_tool(vent_xy, cap_wall_height, tube_ports.air_grip))

    # Level-sensing rod register boss: a hollow boss hanging down from
    # the cap's underside into the body cavity. The rod top slides into
    # the boss's bore from below as the cap is lowered onto the body.
    # The gasket is a perimeter ring only — at the rod position
    # (cavity interior) there is nothing between the body wall top and
    # the cap's underside, so the boss is free to extend below cap-local
    # z=0. Boss outer cylinder: solid PETG from cap-local z=-rod_register_boss_height
    # up to the base plate at cap-local z=cap_wall_height. Boss bore
    # extends from boss bottom up to the base plate's underside (cap
    # closes the bore from above).
    rod_x_signed = rod_position_x * side
    boss_outer = _z_cylinder(
        (rod_x_signed, rod_position_y),
        (-rod_register_boss_height, cap_wall_height),
        rod_boss_od,
    )
    cap = cap.union(boss_outer)

    boss_bore = _z_cylinder(
        (rod_x_signed, rod_position_y),
        (-rod_register_boss_height - 0.1, cap_wall_height),
        rod_bore,
    )
    cap = cap.cut(boss_bore)

    # Liquid mouths take flush TPU spools in the flat plate. The foam cap
    # seats reservoir_clearance above this face, with no projecting flange.
    if side in reservoir_fill_sides:
        cap = _add_port(cap, fill_position[side])
    cap = _add_port(cap, draw_position[side])

    return cap.unwrap()


def _add_port(cap, anchor_xy):
    """Matching double countersink through the flat plate for one liquid-tube spool."""
    return cap.cut(tube_ports.seat_tool(anchor_xy, cap_wall_height, tube_ports.liquid_grip))


def build_reservoir_gasket(side=1):
    """Flat TPU 85A gasket between the reservoir body wall top and the
    cap base plate bottom. Same `[ø10](GASKET_PAD_D) pad extending inward
    beyond the ring so the screw clamp compresses a uniform disk of
    TPU (matching the body boss footprint), with an ø[3.3 mm](CAP_CLEARANCE_HOLE_D) clearance
    hole through its center. side=+1 builds the +X gasket; side=−1
    builds the −X (mirror)."""
    gasket_z_range = (0.0, gasket_thickness)
    outer = _build_envelope(side, gasket_z_range)
    inner = _build_envelope(side, gasket_z_range, wall_offset=gasket_strip_width)
    gasket = outer.cut(inner)

    # Outer fillets at the curve × ±Y and +X × ±Y corners (match the
    # body/cap outer profile so the gasket aligns flush with both above
    # and below it when clamped).
    z_mid_gasket = gasket_thickness / 2.0
    gasket = _fillet_pair_at_y(gasket, side * outer_corner_x, z_mid_gasket, outer_y_max, outer_corner_fillet_radius)
    gasket = _fillet_pair_at_y(gasket, side * outer_far_x_abs, z_mid_gasket, outer_y_max, outer_corner_fillet_radius)

    # At each insert position: [ø10](GASKET_PAD_D) pad unioned BEFORE the hole is cut
    # so each hole sits at the center of a full pad disk.
    insert_anchors = [(px * side, py) for (px, py) in insert_positions_for_side_plus_1]
    pads = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=gasket_z_range[0])
        .pushPoints(insert_anchors)
        .circle(gasket_pad_radius)
        .extrude(gasket_z_range[1] - gasket_z_range[0])
    )
    gasket = gasket.union(pads)
    holes = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=-0.1)
        .pushPoints(insert_anchors)
        .circle(cap_clearance_hole_diameter / 2)
        .extrude(gasket_thickness + 0.2)
    )
    gasket = gasket.cut(holes)

    return gasket.unwrap()


def build_reservoir_tube_grip():
    """Four identical TPU 90A spools per machine, two per reservoir lid."""
    return tube_ports.build_grommet(tube_ports.liquid_grip)


def build_reservoir_air_grip():
    """Two identical TPU 90A spools per machine, one per reservoir air tube."""
    return tube_ports.build_grommet(tube_ports.air_grip)


def main():
    from _show_skin import write_bed_file
    from flute_payload import cut as write_print_payload
    # Left/right naming is geometric: side=+1 → +X reservoir →
    # "*-right.step"; side=-1 → -X reservoir → "*-left.step". The machine's
    # front face is −Y (toward the user — the dispense side); +Y is the rear.
    #
    # A and B use their own fill, draw and air stations. The y-symmetric rim
    # gasket flips between sides; the two concentric spool designs fit either lid.
    here = Path(__file__).resolve().parent

    for side, label in ((+1, "right"), (-1, "left")):
        body = build_reservoir_body(side=side)
        cap = build_reservoir_cap(side=side)
        export_assembly(one_body(body, f"reservoir-{label}", _mat.C_RESERVOIR),
                        str(here / f"reservoir-{label}.step"))
        export_assembly(one_body(cap, f"reservoir-cap-{label}", _mat.C_RES_CAP),
                        str(here / f"reservoir-cap-{label}.step"))
        print(f"-> reservoir-{label}.step")
        print(f"-> reservoir-cap-{label}.step")
        write_bed_file(cap, here / f"reservoir-cap-{label}.stl")
        write_print_payload(here / f"reservoir-cap-{label}.step",
                            here / f"reservoir-cap-{label}.stl",
                            preserve_print_triangles=True)

    gasket = build_reservoir_gasket(side=+1)  # y-symmetric: flip to install on −X side
    export_assembly(one_body(gasket, "reservoir-gasket", _mat.C_SILICONE),
                    str(here / "reservoir-gasket.step"))
    print("-> reservoir-gasket.step")
    for name, grip in (("reservoir-tube-grip", build_reservoir_tube_grip()),
                       ("reservoir-air-grip", build_reservoir_air_grip())):
        export_assembly(one_body(grip, name, _mat.M_TPU_BLACK), str(here / f"{name}.step"))
        write_bed_file(grip, here / f"{name}.stl")
        write_print_payload(here / f"{name}.step", here / f"{name}.stl",
                            preserve_print_triangles=True)
        print(f"-> {name}.step / .stl")

    # WHAT THE RESERVOIR HOLDS, read off the body just built: the cavity from the
    # floor to the rim, less what the body stands in it (the rod's anchor boss, the
    # insert bosses, the corner fillets). The window is the same reading between the
    # first and last reed's heights.
    def held(z_range):
        envelope = _build_envelope(+1, z_range, wall_offset=reservoir_wall_thickness).val()
        return (envelope.Volume() - envelope.intersect(body_plus_x).Volume()) / 1e6
    body_plus_x = build_reservoir_body(side=+1).val()
    capacity_l = held(inner_z_range)
    window_l = held((min(reservoir_reed_centres_z), max(reservoir_reed_centres_z)))
    print(f"   capacity {capacity_l:.3f} L floor to rim; {window_l:.3f} L between the end reeds")

    # Short names scoped to this part. Units live inside the value so
    # the script controls them — change a unit in source and every
    # sibling doc + dynamic-comment marker follows. The foam-shell
    # README also references RESERVOIR_W/D/H here; the foam-shell script
    # owns its own variables on that same README, and unknown names in
    # either script's variables dict are left untouched.
    res_w = 2 * outer_y_max
    res_d = outer_far_x_abs - outer_centerward_radius
    res_h = outer_z_range[1] - outer_z_range[0]
    variables = {
        # Foam-shell README — reservoir-section envelope.
        "RESERVOIR_W": f"{res_w:.4g} mm",
        "RESERVOIR_D": f"{res_d:.4g} mm",
        "RESERVOIR_H": f"{res_h:.4g} mm",
        # The cap's fill bore — the reservoir's second mouth, above the liquid.
        "FILL_BORE_D": f"{fill_bore_diameter:.4g} mm",
        # And the cap conduit standing over a reed channel's mouth, which `level-sensing.md`
        # reads. Same standard, a different feature — neither is the other's figure.
        "CONDUIT_BORE_D": f"{port_hole_radius * 2:.4g} mm",
        "FILL_POSITION_A": "({:.4g}, {:.4g})".format(*fill_position[+1]),
        "FILL_POSITION_B": "({:.4g}, {:.4g})".format(*fill_position[-1]),
        # level-sensing.md rod placement + size + reed count.
        "ROD_DIAMETER": f"{rod_diameter:.4g} mm",
        "ROD_POSITION_X": f"{rod_position_x:.2f}",
        "CAVITY_FAR_WALL_X": f"{inner_far_x_abs:.2f}",
        "ROD_WALL_DISTANCE": f"{_float.rod_axis_from_inner_wall:g} mm",
        "FLOAT_DIAMETER": f"{_float.diameter:g} mm",
        "FLOAT_HEIGHT": f"{_float.height:g} mm",
        "FLOAT_TRAVEL": f"{float_magnet_travel_z[0]:.2f}–{float_magnet_travel_z[1]:.2f} mm",
        "REED_CENTRES": ", ".join(f"{z:.2f}" for z in reservoir_reed_centres_z),
        "ROD_POSITION_Y": f"{rod_position_y:.4g}",
        "REEDS_PER_RES": f"{reeds_per_reservoir:.4g}",
        "RESERVOIR_ROD_LEN": f"{reservoir_rod_len:.4g} mm ({reservoir_rod_len / 25.4:.3g} in)",
        "RESERVOIR_SEAT_TO_SEAT": f"{reservoir_rod_len + reservoir_rod_clearance:.4g} mm",
        "ROD_END_CLEARANCE": f"{reservoir_rod_clearance:g} mm",
        "REED_PITCH": f"{reservoir_reed_pitch:g} mm",
        # level-sensing.md — the reed cable leaves up its channel and out the bore the
        # cap stands over that channel's mouth, stated in the SHELL's frame.
        "REED_CONDUIT_XY": ", ".join(
            f"{n} ({cap_conduit_shell_xy(n)[0]:.4g}, {cap_conduit_shell_xy(n)[1]:.4g})"
            for n in ("reed-cable-a", "reed-cable-b")),
        # The floor, the draw's dip tube and what the cavity holds (floor-and-dip-tube.md).
        "DRAW_POSITION_A": "({:.4g}, {:.4g})".format(*draw_position[+1]),
        "DRAW_POSITION_B": "({:.4g}, {:.4g})".format(*draw_position[-1]),
        "FLOOR_Z": f"{rod_floor_z:.4g} mm",
        "RESERVOIR_CAPACITY": f"{capacity_l:.2f} L",
        "RESERVOIR_WINDOW": f"{window_l:.2f} L",
        # Dynamic-comment markers above derived constants in this .py file.
        "RESERVOIR_WALL_T": f"{reservoir_wall_thickness:.4g} mm",
        "CAP_TOTAL_H": f"{cap_total_height:.4g} mm",
        "ROD_BORE": f"{rod_bore:.4g} mm",
        "ROD_BOSS_OD": f"{rod_boss_od:.4g} mm",
        "BODY_BOSS_R": f"{body_boss_radius:.4g} mm",
        "BODY_BOSS_D": f"{2 * body_boss_radius:.4g} mm",
        "CAP_BOSS_R": f"{cap_boss_radius:.4g} mm",
        "CAP_STACK_H": f"{cap_stack_above_body:.4g} mm",
        "CAP_ASSEMBLY_LIFT": f"{cap_assembly_lift:.4g} mm",
        "CAP_TOP_Z": f"{cap_top_z:.4g} mm",
        "OUTER_Y_MAX": f"{outer_y_max:.4g} mm",
        "OUTER_CENTERWARD_R": f"{outer_centerward_radius:.4g} mm",
        "INNER_Y_MAX": f"{inner_y_max:.4g} mm",
        "OUTER_TAB_ANGLE": f"{outer_tab_interior_angle:.0f}°",
        "INNER_CORNER_ANGLE": f"{inner_corner_interior_angle:.0f}°",
        "CAP_COUNTERBORE_D": f"{cap_counterbore_diameter:.4g} mm",
        "CAP_CLEARANCE_HOLE_D": f"{cap_clearance_hole_diameter:.4g} mm",
        "GASKET_STRIP_W": f"{gasket_strip_width:.4g} mm",
        "GASKET_THICKNESS": f"{gasket_thickness:.4g} mm",
        "RESERVOIR_CLEARANCE": f"{reservoir_clearance:.4g} mm",
        "INSERT_POCKET_DEPTH": f"{insert_pocket_depth:.4g} mm",
        "OUTER_FILLET_R": f"{outer_corner_fillet_radius:.4g} mm",
        # Screw-boss corner row Y, and the inner-wall corner the boss-4/5
        # cut planes aim at (curve × inner +Y wall), plus the boss-to-corner
        # distance that explains the virtual-pivot offset.
        "CORNER_XY_Y": f"{_corner_xy_y:.4g}",
        "INNER_CORNER_CURVE_X": f"{_inner_corner_curve_x:.4g} mm",
        "CORNER_CURVE_DIST": f"{_corner_curve_to_inner_corner_dist:.4g} mm",
        # Gasket insert pad OD.
        "GASKET_PAD_D": f"ø{2 * gasket_pad_radius:.4g}",
    }
    substitute_md(
        here / ".." / "foam-shell" / "README.md",
        variables=variables,
    )
    print("-> foam-shell/README.md (reservoir section)")
    substitute_md(
        here / "vent.md",
        variables=variables,
    )
    print("-> vent.md")
    substitute_md(
        here / "level-sensing.md",
        variables=variables,
    )
    print("-> level-sensing.md")
    substitute_md(
        here / "floor-and-dip-tube.md",
        variables=variables,
    )
    print("-> floor-and-dip-tube.md")
    substitute_py_comments(
        Path(__file__),
        variables=variables,
    )
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
