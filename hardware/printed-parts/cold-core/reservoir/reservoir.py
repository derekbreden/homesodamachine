"""Reservoir — open-top `[`-shaped PETG cup that sits in each bag
pocket of the foam shell, closed by a separately-printed cap clamped
through a TPU gasket. Mirrored ±X. Houses the bulkhead union, the
level-sensing rod, and the cap-mounted vent.

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

from world_workplane import WorldWorkplane, xz_plane_y_up, xy_plane_z_up
from _cadq_export import export_step
from docgen import substitute_md, substitute_py_comments
from _cold_core_interface import (
    bag_pocket_far_inner_x,
    bag_pocket_y_inner_max,
    bag_pocket_floor_top_z,
    bag_pocket_walls_top_z,
    pocket_centerward_arc_outer_radius,
    port_hole_radius,
    reservoir_clearance,
    reservoir_floor_thickness,
    reservoir_bulkhead_port_x,
    reservoir_bulkhead_port_y,
    level_rod_y,
    bulkhead_floor_clearance,
    bulkhead_elbow_exit_z,
    make_box,
)
from _reed_channels import reeds_per_reservoir, cable_hole_offset_from_bulkhead_hole_x
from _port_cuts import flavor_line_hole_x


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
# screws into heat-set inserts.
#
# Equals reservoir_floor_thickness on the shell side — the PETG layer the
# foam-shell leaves clearance above.
# [3 mm](RESERVOIR_WALL_T) — uniform PETG thickness for floor + every wall.
reservoir_wall_thickness = reservoir_floor_thickness


# Fillets where the centerward curve meets the ±Y walls. At
# y = ±[70 mm](OUTER_Y_MAX) the outer centerward curve (radius
# [81 mm](OUTER_CENTERWARD_R)) meets the outer ±Y walls at a [30°](OUTER_TAB_ANGLE)
# interior-angle tab; at y = ±[67 mm](INNER_Y_MAX) the inner centerward curve
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
cap_base_thickness = 4.0  # flat top spans the cavity unsupported and hosts the screw counterbores
cap_wall_height = 5.0
cap_wall_width = 6.0

# Screw recess geometry. M3 SHCS head OD ~5.5 mm → ⌀[6 mm](CAP_COUNTERBORE_D)
# counterbore. The counterbore recesses the head through the full base plate;
# the clearance hole through the perimeter wall carries the shaft to the
# gasket + body insert below.
cap_counterbore_diameter = 6.0
cap_counterbore_depth = cap_base_thickness
cap_clearance_hole_diameter = 3.5


# TPU 85A flat gasket between the body wall top and the cap base plate
# bottom, compressed by the six M3 × 12 screws. [5 mm](GASKET_STRIP_W)-wide perimeter ring
# covering the body wall top and extending inward over the cavity opening;
# circular pads at each insert position give the screw clamp a uniform
# compressed disk; ⌀[3.5 mm](CAP_CLEARANCE_HOLE_D) clearance holes through each pad.
gasket_thickness = 2.0
gasket_strip_width = 5.0


# Cap-local Z ranges, anchored at the cap's own z=0 (perimeter wall
# bottom). In the assembled stack the cap sits at world z = outer_z_range[1]
# + gasket_thickness.
cap_perimeter_z_range = (0, cap_wall_height)
cap_base_z_range = (cap_wall_height, cap_wall_height + cap_base_thickness)
# [9 mm](CAP_TOTAL_H) — perimeter-wall height + base-plate thickness.
cap_total_height = cap_base_z_range[1]


# Vent feature: a hydrophobic PTFE membrane filter sits in a cylindrical
# pocket at the top of the cap, held down by a press-fit TPU 90A
# retaining ring. Air vents through a small hole below the filter into a
# cylindrical shell that hangs into the reservoir. The cylinder has a
# closed floor at the bottom (in use) and four slots in its walls, so
# splash-up syrup hits the closed floor or the cylinder walls and has to
# take a 90°-turn path through a slot before it could reach the membrane
# above.
#
# Filter: LVDALAB ⌀[13 mm](FILTER_D) PTFE-on-PET membrane (Amazon B0D41KT345)
# Retaining ring: [2 mm](RETAINING_RING_T)-thick TPU 90A, press-fit into the cap pocket
filter_diameter = 13.0
filter_thickness = 0.5

retaining_ring_thickness = 2.0
retaining_ring_outer_diameter = 13.4  # 0.1 mm interference per side vs the ⌀[13.2 mm](VENT_POCKET_D) pocket, so the TPU 90A ring compresses in for a light press-fit
retaining_ring_inner_diameter = 9.0   # leaves most of the membrane exposed for airflow

# Filter pocket (cylindrical recess in the cap top) holds the
# filter + ring stack with 0.2 mm of slip-fit clearance.
# [13.2 mm](VENT_POCKET_D) — filter ⌀ + 0.1 mm/side clearance.
vent_pocket_diameter = filter_diameter + 0.2
vent_pocket_depth = filter_thickness + retaining_ring_thickness

# Below the pocket the cap thickens locally into a boss carrying the
# small vent hole; the boss protrudes below the standard base plate bottom.
vent_hole_diameter = 5.0
vent_below_pocket_material = 2.5  # cap material thickness between pocket bottom and boss bottom
vent_boss_wall_around_pocket = 2.0
# [17.2 mm](VENT_BOSS_OD) — pocket ⌀ + 2 × wall around pocket.
vent_boss_outer_diameter = vent_pocket_diameter + 2 * vent_boss_wall_around_pocket
_vent_boss_depth = vent_pocket_depth + vent_below_pocket_material
_vent_boss_extension_below_base_plate = _vent_boss_depth - cap_base_thickness

# Cylinder shell hangs below the boss into the reservoir, inside diameter
# equal to the vent hole so the air column has no internal step. Outer
# diameter matches the brim diameter (a [2.5 mm](VENT_CYL_WALL_T) wall) so the brim
# is flush with the cylinder, becoming the closed bottom of a single
# ⌀[10 mm](VENT_CYL_OD) cylinder.
vent_cylinder_inner_diameter = vent_hole_diameter
vent_cylinder_wall_thickness = 2.5
# [10 mm](VENT_CYL_OD) — cylinder ID + 2 × wall (matches brim ⌀ so brim is flush with cylinder).
vent_cylinder_outer_diameter = vent_cylinder_inner_diameter + 2 * vent_cylinder_wall_thickness
vent_brim_thickness = 1.0
vent_brim_diameter = vent_cylinder_outer_diameter

# Side slots cut through the cylinder walls — four rectangular
# windows at 0°/90°/180°/270°. Slot height equals the cylinder wall
# height (no margin above or below), so the wall in the slot zone is
# four angular ribs spanning between the brim below and the boss
# extension above.
vent_slot_count = 4
vent_slot_width = 3.0
vent_slot_height = 2.0

vent_cylinder_length = vent_slot_height + vent_brim_thickness

# Vent position on the cap, in the side=+1 frame. Centered between
# the y=0 and y=−[64](CORNER_XY_Y) rows of screw bosses (so the ø[17.2 mm](VENT_BOSS_OD) vent boss and
# its counterbore-sized pocket clear every screw counterbore and
# every cap-side boss), and inside the perimeter wall. Mirrored
# across x=0 for side=−1.
vent_position_x = 96.0
vent_position_y = -32.5

# Vent z stack, in cap-local coordinates (anchored from cap_total_height
# at the top). Top→bottom: filter pocket / boss extension below the
# base plate / cylinder shell with the four side slots / closed brim.
vent_pocket_bottom_z = cap_total_height - vent_pocket_depth
vent_boss_bottom_z = cap_total_height - _vent_boss_depth
vent_cylinder_walls_bottom_z = vent_boss_bottom_z - (vent_cylinder_length - vent_brim_thickness)
vent_brim_bottom_z = vent_cylinder_walls_bottom_z - vent_brim_thickness


# Level-sensing rod: a vertical [3.175 mm](ROD_DIAMETER) (1/8") × 305 mm (12") 316 SS
# round rod, body-anchored and cap-registered. A small magnetic float
# slides up and down the rod as the syrup level changes; [4](REEDS_PER_RES) reed
# switches mounted outside the reservoir pocket's far +X wall detect the
# float's position. They drop into the foam shell's reed channel as one
# pre-soldered column after the body pour has cured — held mechanically,
# never foam-encapsulated (`level-sensing.md`). Same
# rod SKU as the carbonator's reed+float level sensing — Tandefio B0CY4DWJFQ;
# see `hardware/future.md` "Level sensing".
#
#   - Body: a solid PETG cylindrical boss rises from the wet slope at
#     (±rod_position_x, rod_position_y); a blind bore from above stops
#     rod_anchor_boss_floor mm short of the boss base, so the rod tip
#     bottoms out on printed-solid PETG and the wet slope stays unbroken.
#   - Cap: a hollow register boss hangs down from the underside with a
#     downward-opening blind bore around the rod's top. The rod is captured
#     at BOTH ends against float-load lean.
#
# Sits opposite the bulkhead pass-through (on the −Y front), on the +Y rear
# half in the wider part of the cavity (~38 mm wide at y=+45 vs ~24 mm at
# y=0) where the donut float has clearance, clear of all screw bosses and
# the vent boss.
rod_position_x = 107.0  # |x| of the rod centerline; mirrors with `side`
rod_position_y = level_rod_y  # y of the rod centerline; does NOT mirror with side —
# the reed column outside stands on this same station (`_cold_core_interface.level_rod_y`)
rod_diameter = 3.175  # 1/8" 316 SS round rod OD
# [3.675 mm](ROD_BORE) — rod ⌀ + 0.5 mm slip-fit clearance; shared by body anchor boss and cap register boss.
rod_bore = rod_diameter + 0.5  # ~0.5 mm radial slip-fit clearance; shared by body anchor boss and cap register boss
# [7.675 mm](ROD_BOSS_OD) — bore ⌀ + 4 mm (2 mm radial wall); shared by body anchor and cap register bosses.
rod_boss_od = rod_bore + 4.0  # 2 mm radial wall around the bore
rod_register_boss_height = 2.0  # CAP-side boss EXTRA height beyond cap rim
rod_anchor_boss_height = 6.0  # BODY-side anchor boss
rod_anchor_boss_floor = 0.0  # printed-solid PETG floor INSIDE the body boss


# Outlet bulkhead port + V floor. A PureSec 1/4" RO push-to-connect 90°
# elbow bulkhead (Amazon B0968K4JRN — white polypropylene, water/RO/
# beverage-rated, ships WITHOUT a panel o-ring) clamps VERTICALLY through
# the cavity floor's central trough. The part is an L-body and mounts
# elbow-DOWN: the integral 90° elbow + its ⌀[18.7 mm](BULKHEAD_DRY_FLANGE_OD)
# dry-side flange hang BELOW the trough floor in the open bag-pocket space,
# the threaded barrel passes UP through the floor, and the hex nut threads
# on from ABOVE — in the cavity (wet side) — clamping the floor between the
# below flange and the nut. The elbow turns the dry line laterally toward
# the bag-pocket +Y pass-through; the barrel-end PTC sits on the barrel axis
# in the cavity above the nut.
#
# The PureSec ships without an o-ring, so a printed TPU face seal sits in
# a counterbore on EACH floor face (a washer sized to each face): the
# wet/top washer is clamped by the ⌀[21.9 mm](BULKHEAD_WET_NUT_OD) nut-side
# face, the dry/under washer by the ⌀[18.7 mm](BULKHEAD_DRY_FLANGE_OD)
# elbow-side flange. Each seats on a PETG rim outside its counterbore. Only
# the barrel bore pierces the trough floor.
#
# Dimensions are those of the PureSec part; see
# ../../../off-the-shelf-parts/puresec-90-bulkhead/geometry-description.md.
#
# Floor: a Y-symmetric V swept across the full cavity X width. From
# each ±Y wall the floor slopes inward and DOWN to a flat rectangular
# trough centered at y=0 that spans the full interior X width and hosts
# the port. The floor is a single Y–Z section (slope down / flat /
# slope up) extruded straight across X; the only curved floor boundary
# is the cavity's existing centerward arc. There is NO circular pad.
# Syrup drains by gravity from anywhere in the cavity down the V to the
# trough and into the port. This wet V is the floor's INTERIOR; its
# EXTERIOR underside is a single flat horizontal plane (floor_flat_bottom_z),
# the floor solid between them. The floor is RAISED (see floor_trough_lift)
# so the below flange + integral 90° elbow fit in the open bag-pocket space
# below that flat bottom.
#
# reservoir_bulkhead_port_x: midpoint between the cavity's inner +X face and
#   the concave arc's peak (imported from _cold_core_interface); the trough/
#   port X center. The port sits at y=0.

bulkhead_panel_hole_diameter = 16.0  # PureSec thread OD ⌀15.5 + 0.5 mm slip; well under the ⌀[18.7 mm](BULKHEAD_DRY_FLANGE_OD) dry-side flange so the below flange can't pull up through the hole. Cut straight through the trough floor on the barrel axis.

# The hex nut sits in open cavity (wet side) above the trough floor,
# threaded onto the barrel from above against the wet-side TPU washer, with
# open space all around it.

# The two PureSec clamping faces the washers seat under (see
# geometry-description.md).
bulkhead_wet_nut_od = 21.9  # nut-side clamping face OD (wet/top)
bulkhead_dry_flange_od = 18.7  # elbow-side flange OD (dry/under)

# Bulkhead/floor face seals — one on EACH face, the only fluid seal at the
# barrel-to-floor joint. The WET (top) face is the primary seal: a PURCHASED
# silicone flat washer (uxcell B07D23JJMR, ⌀16 ID × ⌀24 OD × 3 mm) compressed
# by the ⌀[21.9 mm](BULKHEAD_WET_NUT_OD) nut face — its ⌀24 OD is wider than the
# nut, so the nut presses down onto the washer inside the counterbore (squeeze
# set by nut torque). The DRY (under) face is a printed TPU 85A washer
# compressed by the ⌀[18.7 mm](BULKHEAD_DRY_FLANGE_OD) elbow flange, seating
# flush on the PETG rim outside its counterbore — (thickness − depth)/thickness
# = 30%.
bulkhead_seal_id = 16.0  # SHARED washer ID = PureSec barrel OD ⌀15.5 + 0.5 mm so the washer slips over the barrel. Equals the ⌀[16 mm](BULKHEAD_PANEL_HOLE_D) panel hole — a face seal (against the clamping face + the floor face), not a radial seal on the barrel.
bulkhead_seal_thickness = 2.0  # printed DRY washer thickness (the purchased wet washer is 3 mm — a part spec, not a CAD value)
bulkhead_seal_counterbore_depth = 1.4  # SHARED counterbore depth (both faces): 30% squeeze of the 2 mm dry washer; the 3 mm wet washer sits recessed 1.4 mm (proud 1.6 mm), compressed by the nut
# WET (top) face — the PURCHASED silicone washer (⌀24 × 3 mm) sits in this counterbore; the ⌀[21.9 mm](BULKHEAD_WET_NUT_OD) nut compresses it.
bulkhead_seal_wet_od = 24.0  # ⌀[16 mm](BULKHEAD_SEAL_ID)–[24 mm](BULKHEAD_SEAL_WET_OD) purchased uxcell B07D23JJMR silicone washer; ⌀16 ID slips over the barrel
bulkhead_seal_wet_counterbore_diameter = 24.3  # ⌀[24.3 mm](BULKHEAD_SEAL_WET_CB_D): 0.15 mm/side around the ⌀24 washer; the ⌀[21.9 mm](BULKHEAD_WET_NUT_OD) nut presses the washer down inside it (OD > nut, so no PETG rim outside)
# DRY (under) washer + counterbore — clamped by the ⌀[18.7 mm](BULKHEAD_DRY_FLANGE_OD) elbow flange.
bulkhead_seal_dry_od = 18.5  # ⌀[16 mm](BULKHEAD_SEAL_ID)–[18.5 mm](BULKHEAD_SEAL_DRY_OD) ring; the ⌀[18.7 mm](BULKHEAD_DRY_FLANGE_OD) flange caps how wide this can go
bulkhead_seal_dry_counterbore_diameter = bulkhead_seal_dry_od  # ⌀[18.5 mm](BULKHEAD_SEAL_DRY_CB_D) = the dry washer OD ⌀[18.5 mm](BULKHEAD_SEAL_DRY_OD): hugs it with no radial clearance (the soft TPU compresses), leaving the maximum PETG rim under the ⌀[18.7 mm](BULKHEAD_DRY_FLANGE_OD) flange.
assert bulkhead_seal_dry_counterbore_diameter < bulkhead_dry_flange_od, (
    f"dry seal counterbore ({bulkhead_seal_dry_counterbore_diameter}) must stay under "
    f"the dry flange OD ({bulkhead_dry_flange_od}) to leave a PETG seat rim"
)

# Each seal counterbore recesses into a raised seat boss, not the bare
# trough floor. The boss is counterbored from BOTH faces (a washer per
# side): bulkhead_seal_seat_thickness is the PETG from the wet-face
# counterbore down to the boss underside, and the dry-face counterbore cuts
# up into it from below — leaving a solid PETG mid-rim of
# (seat_thickness − counterbore_depth) = [3 mm](RESERVOIR_WALL_T) (the wall
# thickness, enforced by the seat derivation below) that carries the
# flange+nut clamp without crushing. The boss contains the wet counterbore
# (the ⌀[21.9 mm](BULKHEAD_WET_NUT_OD) nut presses the washer down inside that
# bore) and sits flush in the floor underside above the open bag-pocket space.
bulkhead_seal_boss_diameter = bulkhead_seal_wet_counterbore_diameter + 2 * 0.8  # ⌀[25.9 mm](BULKHEAD_SEAL_BOSS_D): contains the wet counterbore (a thin wall — the ⌀[21.9 mm](BULKHEAD_WET_NUT_OD) nut presses the washer down inside the bore, not on a PETG rim) and hosts the dry-flange rim below; still fits within the flat trough (see floor_trough_half_width_y)
bulkhead_seal_seat_thickness = reservoir_wall_thickness + bulkhead_seal_counterbore_depth  # the solid PETG mid-rim between the wet + dry counterbores is (seat − counterbore_depth); seat = wall + counterbore_depth makes that mid-rim exactly reservoir_wall_thickness, the minimum floor thickness at the port

# PureSec integral 90° elbow + push-to-connect ports. See
# ../../../off-the-shelf-parts/puresec-90-bulkhead/geometry-description.md.
# The dry line turns laterally at the elbow and runs out to the
# bag-pocket +Y pass-through, in the open space below the trough floor.
bulkhead_elbow_flange_to_bottom = 19.6  # dry-side flange top face (seats on the boss underside) → elbow's lowest point; how far the elbow hangs below the floor

# Interior wet V section (Y–Z), extruded straight across the full cavity X.
# The flat trough at y=0 is the cavity's low point and the lowest
# drainable line; the slopes rise from the trough edges to the ±Y
# walls. (floor_trough_z, the slope rate, and the wedge extrusion top
# are derived below, after inner_z_range / inner_y_max are defined.)
#
# The floor is raised as far as the bulkhead hardware below it demands.
# Below the flat exterior bottom hang, in order, the dry-side TPU washer and
# the flange-to-elbow standoff; bulkhead_floor_clearance then buffers the
# elbow bottom off the bag-pocket floor. The (boss_height − wall) term keeps
# the budget measured from the wet-V-offset reference line (one wall below
# the wet trough); the flat exterior bottom sits at the resulting lowest
# point (floor_flat_bottom_z). The corner support posts (in the foam shell
# via _reservoir_supports) carry the reservoir and meet this flat bottom.
bulkhead_seal_boss_height = bulkhead_seal_counterbore_depth + bulkhead_seal_seat_thickness  # boss top flush with the trough; the (boss_height − wall) term below places the flat bottom that far under the wet-V-offset reference line
bulkhead_below_floor_stack = (
    (bulkhead_seal_boss_height - reservoir_wall_thickness)  # seal-boss protrusion below the floor underside
    + bulkhead_seal_thickness                                # dry-side TPU washer, full thickness
    + bulkhead_elbow_flange_to_bottom                        # flange-top → elbow-bottom standoff
)
floor_trough_lift = bulkhead_floor_clearance + bulkhead_below_floor_stack - reservoir_clearance
floor_trough_half_width_y = 14.0  # half the flat trough's Y extent; wide enough to host the ⌀[25.9 mm](BULKHEAD_SEAL_BOSS_D) seal-seat boss (≈1 mm Y margin each side)
floor_slope_rise = 6.0  # mm the floor rises from the trough surface to each ±Y wall


# Heat-set insert + screw spec. M3 ruthex-style brass heat-set inserts
# (same as foam-shell cap-stack joinery). Insert OD 4 mm × length 4 mm;
# pocket is 4 mm bore × [7 mm](INSERT_POCKET_DEPTH) deep (4 mm insert + 3 mm relief). Screws:
# BNUOK M3 × 12 mm DIN 912 SHCS, 304 stainless steel, 18-8 (Amazon
# B0DJQGMQZM). The M3 × 12 length suits the reservoir's thinner cap-stack
# geometry (under-head stack is 7 mm cap-plus-gasket vs the foam-shell's
# ~19 mm).
# With M3 × 12, the shaft seats 4 mm into the insert, runs another 1 mm
# into the pocket relief, and leaves 2 mm of slack between the shaft
# tip and the pocket floor.
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
# the body's wall top — leaves the cap's top face flush at z=[212.9 mm](CAP_TOP_Z)
# ([0.5 mm](RESERVOIR_CLEARANCE) clear of the bag-pocket wall top); body alone is [199.4 mm](RESERVOIR_H) tall.
# [11 mm](CAP_STACK_H) — gasket + cap perimeter wall + cap base plate.
cap_stack_above_body = gasket_thickness + cap_wall_height + cap_base_thickness
outer_z_range = (
    bag_pocket_floor_top_z + reservoir_clearance,
    bag_pocket_walls_top_z - reservoir_clearance - cap_stack_above_body,
)
inner_z_range = (outer_z_range[0] + reservoir_wall_thickness, outer_z_range[1])
# Assembled-stack references — pinned into the docstring/comments below so they
# can never drift again (an earlier hand-typed "214.9" did exactly that).
cap_assembly_lift = outer_z_range[1] + gasket_thickness  # [203.9 mm](CAP_ASSEMBLY_LIFT) — cap-local z=0 lands here on the body
cap_top_z = cap_assembly_lift + cap_total_height          # assembled cap top face

# V-floor derived geometry (needs inner_z_range / inner_y_max above).
# floor_trough_z is the INTERIOR (wet) V's trough surface. It is RAISED
# floor_trough_lift above the base cavity floor (inner_z_range[0]) so the
# PureSec below-side flange + integral 90° elbow clear in the open
# bag-pocket space below the floor. The interior wet surface is a V: the
# flat trough at floor_trough_z rising at floor_slope_rate to the ±Y walls,
# from (|y| = floor_trough_half_width_y, z = floor_trough_z) up to
# (|y| = inner_y_max, z += floor_slope_rise). The EXTERIOR (dry) underside
# is a single flat horizontal plane at floor_flat_bottom_z (below), not a
# wall-offset copy of the V — the floor is filled solid between the wet V
# and that plane, so it prints support-free.
floor_trough_z = inner_z_range[0] + floor_trough_lift  # wet (top) surface of the flat trough = cavity low point, raised so the below flange/elbow fit below
# Flat exterior bottom plane: the whole footprint's dry underside sits at
# this single Z, the seal-boss underside and the reservoir's lowest printed
# point. The seal boss is flush with this plane and the dry-side counterbore
# opens flush in it as a shallow recess. Below this plane is open central
# bag-pocket space where the ⌀[18.7 mm](BULKHEAD_DRY_FLANGE_OD) flange + 90°
# elbow hang.
floor_flat_bottom_z = floor_trough_z - bulkhead_seal_counterbore_depth - bulkhead_seal_seat_thickness
# Open headroom below the flat exterior bottom, down to the bag-pocket floor
# (the foam-shell pocket the reservoir drops into). The flat bottom is the
# reservoir's lowest point, so this is also how far that lowest point clears
# the bag-pocket floor.
floor_below_trough_headroom = floor_flat_bottom_z - bag_pocket_floor_top_z
floor_slope_y_distance = inner_y_max - floor_trough_half_width_y
floor_slope_rate = floor_slope_rise / floor_slope_y_distance

# Level-sensing rod cut length. Seat-to-seat = the top register seat (cap-local
# cap_wall_height, raised to assembled coords by cap_assembly_lift) minus the
# body anchor-boss bore floor at the rod's y; cut reservoir_rod_clearance under
# so the rod never holds the cap off its gasket. (Geometry-verified seat-to-seat
# = 174.99 mm; this is the cut figure.)
reservoir_rod_clearance = 1.0  # mm
reservoir_rod_len = (
    (cap_assembly_lift + cap_wall_height)
    - (floor_trough_z + floor_slope_rate * (abs(rod_position_y) - floor_trough_half_width_y)
       + rod_anchor_boss_floor)
    - reservoir_rod_clearance
)  # [175.4 mm (6.91 in)](RESERVOIR_ROD_LEN) — 1/8" 316 SS rod, seat-to-seat − 1 mm
# Floor wedge extrusion top — above the highest slope point so the
# slope half-spaces cut a clean upper face on the wedge fill.
floor_wedge_top_z = floor_trough_z + floor_slope_rise + 2.0

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
# [8.794 mm](CORNER_CURVE_DIST) cut depth would eat into the 7 mm heat-set pocket).
#
# Values stored for side=+1; the x component is multiplied by `side`
# in the body-boss loop to mirror across x=0 for side=−1.
_far_wall_inner_x = outer_far_x_abs - reservoir_wall_thickness
_plus_y_wall_inner_y = outer_y_max - reservoir_wall_thickness
_curve_inner_x_at_y0 = outer_centerward_radius + reservoir_wall_thickness
_inv_sqrt2 = 1.0 / math.sqrt(2.0)

# Bosses 4 / 5 need their cut direction pointed at the inner-wall
# CORNER (where the inner curve at radius _curve_inner_x_at_y0 = 76
# meets the inner ±Y wall at y = ±_plus_y_wall_inner_y = ±[67 mm](INNER_Y_MAX)), not
# at the closest point on the curve along the inward radial line.
# Pointing at the corner is the same pattern bosses 1 / 2 use (their
# cuts slope down away from the +X × ±Y inner corner). For boss 4
# the corner is at (≈[50.67 mm](INNER_CORNER_CURVE_X), [67 mm](INNER_Y_MAX)),
# [8.794 mm](CORNER_CURVE_DIST) from the boss in the (−X, +Y) direction — too
# far to use as a literal pivot (a [8.794 mm](CORNER_CURVE_DIST) cut depth would
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
    """Open-top `[`-shaped PETG body with uniform wall-thickness walls + floor,
    sized to fit one side of the bag-pocket cavity with reservoir_clearance
    mm of slack on every outer face. Six insert bosses at the top
    perimeter (one per insert_positions_for_side_plus_1) host ø4 × 7 mm
    heat-set inserts. side=+1 builds the +X reservoir; side=−1 the −X
    (mirror across x=0)."""
    outer_envelope = _build_envelope(side, outer_z_range)
    inner_cavity = _build_envelope(side, inner_z_range, wall_offset=reservoir_wall_thickness)

    body = outer_envelope.cut(inner_cavity)

    # Fillet the four sharp corners where the centerward concave curve
    # meets the ±Y walls — applied to the bare wall geometry BEFORE
    # unioning the insert bosses, because two of the inner corners
    # coincide with boss positions ([50.67 mm](INNER_CORNER_CURVE_X), ±[67 mm](INNER_Y_MAX)) and unioning a cylinder
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

    # Floor — Y-symmetric interior wet V on top, single FLAT horizontal
    # exterior bottom underneath, swept across the full cavity X width and
    # RAISED floor_trough_lift so the PureSec below-side flange + integral
    # 90° elbow hang in OPEN space below the flat bottom. The interior (wet)
    # surface is the V: a flat trough at floor_trough_z for
    # |y| ≤ floor_trough_half_width_y, sloping up at floor_slope_rate to the
    # ±Y walls. The exterior (dry) surface is the flat plane at
    # floor_flat_bottom_z; the floor is solid between the wet V and that plane
    # (the ±Y side voids are filled, not left open under the V), so the
    # underside is a single horizontal face that prints with no support. Below
    # the flat bottom is open central bag-pocket space; the only thing piercing
    # the floor is the bulkhead barrel bore.
    #
    # _v_floor_solid(trough_top_z) is the cavity-footprint solid capped by the
    # V whose flat trough wet surface sits at trough_top_z: a trough-fill prism
    # (cavity base up to trough_top_z) unioned with the two ±Y slope wedges.
    # The floor solid = that interior-V solid, trimmed to the flat plane below.
    def _above_slope_plane(edge_y, dy_rate, anchor_z):
        """Half-space ABOVE the slope plane through (0, edge_y, anchor_z),
        surface slope dz/dy = dy_rate. Cutting it away leaves material only
        below the slope surface."""
        plane = cq.Plane(
            origin=(0, edge_y, anchor_z),
            xDir=(1, 0, 0),
            normal=(0, -dy_rate, 1),
        )
        return cq.Workplane(plane).rect(2000, 2000).extrude(2000)

    def _y_half_beyond_trough(sign):
        """Solid filling the Y half beyond the trough edge (sign=+1 → y ≥
        +half; sign=−1 → y ≤ −half)."""
        return (
            cq.Workplane(xz_plane_y_up)
            .workplane(offset=sign * floor_trough_half_width_y)
            .rect(2000, 2000)
            .extrude(sign * 2000)
        )

    def _v_floor_solid(trough_top_z):
        fill = _build_envelope(
            side,
            (inner_z_range[0], trough_top_z),
            wall_offset=reservoir_wall_thickness,
        ).intersect(outer_envelope_filleted)
        wedge_prism = _build_envelope(
            side,
            (trough_top_z, trough_top_z + floor_slope_rise + 2.0),
            wall_offset=reservoir_wall_thickness,
        )
        solid = fill
        for sign in (+1, -1):
            wedge = (
                wedge_prism
                .intersect(_y_half_beyond_trough(sign))
                .cut(_above_slope_plane(sign * floor_trough_half_width_y,
                                        sign * floor_slope_rate, trough_top_z))
                .intersect(outer_envelope_filleted)
            )
            solid = solid.union(wedge)
        return solid

    # Floor solid: the full interior-V solid — the wet V on top, cavity-
    # footprint solid all the way down to be trimmed flat below.
    body = body.union(_v_floor_solid(floor_trough_z))

    # Trim the whole body underside FLAT at floor_flat_bottom_z: remove all
    # material below that single horizontal plane across the full footprint,
    # so walls, fillets, and floor share one flat bottom face. This fills the
    # ±Y side voids solid and backfills under the V; below the plane is
    # open bag-pocket space for the bulkhead hardware. The wet V above is
    # untouched. (The seal boss is unioned AFTER this cut, so it keeps its
    # below-plane geometry — here, exactly flush with the plane.)
    z_below = outer_z_range[0] - 50.0
    below_flat = make_box(
        (-(outer_far_x_abs + 50.0), outer_far_x_abs + 50.0),
        (-(outer_y_max + 50.0), outer_y_max + 50.0),
        (z_below, floor_flat_bottom_z),
    )
    body = body.cut(below_flat)

    # Vertical bulkhead port through the trough at (port_x, y=0). The
    # PureSec mounts elbow-DOWN (barrel axis along world Z): the threaded
    # barrel passes UP through the trough floor, the ⌀[18.7 mm](BULKHEAD_DRY_FLANGE_OD)
    # elbow-side flange + integral 90° elbow hang BELOW the floor in the open bag-pocket
    # space, and the hex nut threads on from ABOVE in the cavity, clamping
    # the floor between the below flange and the nut through a TPU washer on
    # each face. The elbow turns the dry line laterally; the barrel-end PTC
    # sits on the barrel axis in the cavity. Only the barrel bore pierces
    # the trough floor.
    port_x_signed = reservoir_bulkhead_port_x * side

    # Seal seat boss — the bulkhead_seal_boss_diameter pad around the port,
    # spanning the wet trough surface on top down to the flat exterior bottom
    # (floor_flat_bottom_z). With the solid flat-bottomed floor it sits flush
    # in that plane (no protrusion), embedded in the surrounding solid floor;
    # unioned before the bore + both counterbores so all three cut through
    # it. It hosts a face-seal counterbore on BOTH faces (wet top + dry under).
    seal_boss = _z_cylinder(
        (port_x_signed, 0.0),
        (floor_flat_bottom_z, floor_trough_z),
        bulkhead_seal_boss_diameter,
    )
    body = body.union(seal_boss)

    # Panel hole — ⌀[16 mm](BULKHEAD_PANEL_HOLE_D) cut straight through the
    # trough floor on the barrel axis, from above the trough wet surface
    # down through the flat exterior bottom into the open space below.
    panel_hole = _z_cylinder(
        (port_x_signed, 0.0),
        (outer_z_range[0] - 5.0, floor_trough_z + 0.1),
        bulkhead_panel_hole_diameter,
    )
    body = body.cut(panel_hole)

    # Wet-side face-seal counterbore — cut down into the trough's wet (top)
    # face; seats the PURCHASED ⌀24 silicone washer. The ⌀[21.9 mm](BULKHEAD_WET_NUT_OD)
    # nut presses the washer down inside this bore (OD > nut, no rim outside).
    wet_seal_counterbore = _z_cylinder(
        (port_x_signed, 0.0),
        (floor_trough_z - bulkhead_seal_counterbore_depth, floor_trough_z + 0.1),
        bulkhead_seal_wet_counterbore_diameter,
    )
    body = body.cut(wet_seal_counterbore)

    # Dry-side TPU face-seal counterbore — a shallow recess opening flush in
    # the flat exterior bottom (floor_flat_bottom_z = the seal-boss underside),
    # cut UP from it. The ⌀[18.7 mm](BULKHEAD_DRY_FLANGE_OD) elbow-side flange
    # seats on the PETG rim outside it, compressing the dry washer 30%. The two
    # counterbores leave a [3 mm](RESERVOIR_WALL_T) solid PETG mid-rim between
    # them (= the wall thickness; see bulkhead_seal_seat_thickness).
    dry_seal_counterbore = _z_cylinder(
        (port_x_signed, 0.0),
        (floor_flat_bottom_z - 0.1,
         floor_flat_bottom_z + bulkhead_seal_counterbore_depth),
        bulkhead_seal_dry_counterbore_diameter,
    )
    body = body.cut(dry_seal_counterbore)

    # Level-sensing rod body anchor: a solid cylindrical boss rising
    # from the V floor at (±rod_position_x, rod_position_y), with a
    # blind bore cut into it from above — bore stops rod_anchor_boss_floor
    # mm short of the boss base so the printed PETG floor inside the boss
    # is what the rod tip bottoms out on. rod_position_y = +45 sits on
    # the +Y slope (between the trough edge at +14 and the +Y wall at
    # +66), so the boss base z is the slope height at that y.
    #
    # Unioned after every selector-based fillet and cut so the boss
    # cannot perturb an earlier edge/face selection.
    rod_x_signed = rod_position_x * side
    rod_floor_z_at_y = floor_trough_z + floor_slope_rate * (abs(rod_position_y) - floor_trough_half_width_y)
    rod_anchor_boss_cylinder = _z_cylinder(
        (rod_x_signed, rod_position_y),
        (rod_floor_z_at_y, rod_floor_z_at_y + rod_anchor_boss_height),
        rod_boss_od,
    )
    body = body.union(rod_anchor_boss_cylinder)

    # Blind bore: base rod_anchor_boss_floor mm above the floor, extruded up
    # through the top of the boss with a +0.1 overshoot so the cut
    # cleanly opens at the boss top face.
    bore_bottom_z = rod_floor_z_at_y + rod_anchor_boss_floor
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
    # a consistent compression cross-section), ø[3.5 mm](CAP_CLEARANCE_HOLE_D) clearance hole
    # through the cap for the screw shaft, and ø[6 mm](CAP_COUNTERBORE_D) counterbore recessing
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

    # Vent feature. Z-stack runs top→bottom from cap_total_height: filter
    # pocket (ø[13.2 mm](VENT_POCKET_D)) at the top of the base plate, then the small vent
    # hole through the remaining base plate material, then the boss
    # extension below the base plate, then the cylinder shell (slot
    # zone), then the closed brim. Z-anchors live at module scope
    # (vent_pocket_bottom_z, vent_boss_bottom_z, vent_cylinder_walls_bottom_z,
    # vent_brim_bottom_z).
    vent_anchor_xy = (vent_position_x * side, vent_position_y)

    # Solid pieces: boss extension, cylinder body (cut hollow later),
    # brim. All unioned with the cap so the air-column cut below
    # carves a single continuous channel through them.
    boss_extension = _z_cylinder(
        vent_anchor_xy,
        (vent_boss_bottom_z, vent_boss_bottom_z + _vent_boss_extension_below_base_plate),
        vent_boss_outer_diameter,
    )
    cap = cap.union(boss_extension)

    cylinder_solid = _z_cylinder(
        vent_anchor_xy,
        (vent_cylinder_walls_bottom_z, vent_boss_bottom_z),
        vent_cylinder_outer_diameter,
    )
    cap = cap.union(cylinder_solid)

    brim = _z_cylinder(
        vent_anchor_xy,
        (vent_brim_bottom_z, vent_cylinder_walls_bottom_z),
        vent_brim_diameter,
    )
    cap = cap.union(brim)

    # Cut filter pocket from the cap top face (+0.1 breaks the surface cleanly).
    pocket = _z_cylinder(
        vent_anchor_xy,
        (vent_pocket_bottom_z, cap_total_height + 0.1),
        vent_pocket_diameter,
    )
    cap = cap.cut(pocket)

    # Cut the air column: ø[5 mm](VENT_HOLE_D) from the cylinder bottom (top of brim) up
    # to the pocket bottom. This both hollows out the cylinder body we
    # just unioned in and drills the small vent hole through the boss
    # and the [1.5 mm](VENT_BASE_PLATE_T) of base plate below the pocket.
    air_column = _z_cylinder(
        vent_anchor_xy,
        (vent_cylinder_walls_bottom_z, vent_pocket_bottom_z),
        vent_hole_diameter,
    )
    cap = cap.cut(air_column)

    # Side slots — four rectangular windows through the cylinder wall,
    # spaced 90° apart. Slot fills the cylinder wall top to bottom:
    # slot bottom = brim top, slot top = boss extension bottom. The
    # boss above and the brim below carry the load across the slot.
    slot_center_z = vent_cylinder_walls_bottom_z + vent_slot_height / 2.0
    vent_x_signed, vent_y = vent_anchor_xy
    for i in range(vent_slot_count):
        theta = 2.0 * math.pi * i / vent_slot_count
        slot_x = vent_x_signed + (vent_cylinder_outer_diameter / 2.0) * math.cos(theta)
        slot_y = vent_y + (vent_cylinder_outer_diameter / 2.0) * math.sin(theta)
        tangent = (-math.sin(theta), math.cos(theta), 0.0)
        radial = (math.cos(theta), math.sin(theta), 0.0)
        slot_cut = (
            cq.Workplane(cq.Plane(
                origin=(slot_x, slot_y, slot_center_z),
                xDir=tangent,
                normal=radial,
            ))
            .rect(vent_slot_width, vent_slot_height)
            .extrude(-(vent_cylinder_wall_thickness + 1.0))
        )
        cap = cap.cut(slot_cut)

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

    return cap.unwrap()


def build_reservoir_gasket(side=1):
    """Flat TPU 85A gasket between the reservoir body wall top and the
    cap base plate bottom. Same `[ø10](GASKET_PAD_D) pad extending inward
    beyond the ring so the screw clamp compresses a uniform disk of
    TPU (matching the body boss footprint), with an ø[3.5 mm](CAP_CLEARANCE_HOLE_D) clearance
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


def build_reservoir_retaining_ring():
    """TPU 90A annular retaining ring that presses into the cap's
    filter pocket above the membrane and clamps it against the
    pocket floor (the shelf around the small ø[5 mm](VENT_HOLE_D) vent hole). [2 mm](RETAINING_RING_T)
    thick. Outer [ø13.4](RETAINING_RING_OD) nominal — sized for a light interference
    press-fit into the ø[13.2 mm](VENT_POCKET_D) pocket (TPU 90A is soft enough to
    compress 0.1 mm per side without trouble). Inner ø[9 mm](RETAINING_RING_ID) leaves
    most of the membrane exposed for airflow.

    Symmetric, so one ring design works on either side; print 2
    per build (one per reservoir cap)."""
    return (
        WorldWorkplane(xy_plane_z_up)
        .circle(retaining_ring_outer_diameter / 2.0)
        .circle(retaining_ring_inner_diameter / 2.0)
        .extrude(retaining_ring_thickness)
        .unwrap()
    )


def build_reservoir_bulkhead_seal(od):
    """Flat TPU 85A washer for the DRY (under) bulkhead face — od=bulkhead_seal_dry_od,
    shared ID + thickness. Sits in a [1.4 mm](BULKHEAD_SEAL_CB_DEPTH)-deep counterbore in the seal boss;
    the exposed 0.6 mm compresses ~30% when the elbow flange seats flush against
    the PETG rim outside the counterbore. Print 2 per build (one per reservoir).

    The WET (top) face is no longer printed — it is a purchased silicone washer
    (uxcell B07D23JJMR, ⌀24 × 3 mm) that the body's wet counterbore seats. See
    floor-and-bulkhead.md."""
    return (
        WorldWorkplane(xy_plane_z_up)
        .circle(od / 2.0)
        .circle(bulkhead_seal_id / 2.0)
        .extrude(bulkhead_seal_thickness)
        .unwrap()
    )


def main():
    # Left/right naming is geometric: side=+1 → +X reservoir →
    # "*-right.step"; side=-1 → -X reservoir → "*-left.step". The machine's
    # front face is −Y (toward the user — the dispense side); +Y is the rear.
    #
    # Body and cap genuinely differ between sides — they're NOT
    # y-symmetric. The bulkhead port is centered at y=0 (its elbow turns
    # toward the −Y front pass-through), and the strut and vent positions
    # stay at fixed world Y (the strut/rod at y=+45 on the rear half, the
    # cap vent at y=−32.5) so they keep their place for both reservoirs.
    # Mirror across x=0 only — never across y=0.
    #
    # The gasket and the retaining ring are BOTH y-symmetric in their
    # own right (perimeter rings with y-mirrored hole patterns), and
    # under y-symmetry a 180° rotation about Z collapses to an x-mirror
    # — i.e. the −X gasket is just the +X gasket flipped over. So one
    # print serves either reservoir; only a single un-suffixed STEP is
    # exported for each.
    here = Path(__file__).resolve().parent

    for side, label in ((+1, "right"), (-1, "left")):
        body = build_reservoir_body(side=side)
        cap = build_reservoir_cap(side=side)
        export_step(body, str(here / f"reservoir-{label}.step"))
        export_step(cap, str(here / f"reservoir-cap-{label}.step"))
        print(f"-> reservoir-{label}.step")
        print(f"-> reservoir-cap-{label}.step")

    gasket = build_reservoir_gasket(side=+1)  # y-symmetric: flip to install on −X side
    retaining_ring = build_reservoir_retaining_ring()
    bulkhead_seal_dry = build_reservoir_bulkhead_seal(bulkhead_seal_dry_od)
    export_step(gasket, str(here / "reservoir-gasket.step"))
    export_step(retaining_ring, str(here / "reservoir-retaining-ring.step"))
    export_step(bulkhead_seal_dry, str(here / "reservoir-bulkhead-seal-dry.step"))
    print(f"-> reservoir-gasket.step")
    print(f"-> reservoir-retaining-ring.step")
    print(f"-> reservoir-bulkhead-seal-dry.step")

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
        # vent.md headline values.
        "FILTER_D": f"{filter_diameter:.4g} mm",
        "FILTER_T": f"{filter_thickness:.4g} mm",
        "VENT_POCKET_D": f"{vent_pocket_diameter:.4g} mm",
        "VENT_POCKET_DEPTH": f"{vent_pocket_depth:.4g} mm",
        "VENT_BOSS_OD": f"{vent_boss_outer_diameter:.4g} mm",
        "VENT_BOSS_WALL": f"{vent_boss_wall_around_pocket:.4g} mm",
        "VENT_HOLE_D": f"{vent_hole_diameter:.4g} mm",
        "VENT_CYL_OD": f"{vent_cylinder_outer_diameter:.4g} mm",
        "VENT_CYL_ID": f"{vent_cylinder_inner_diameter:.4g} mm",
        "VENT_SLOT_COUNT": f"{vent_slot_count}",
        "VENT_SLOT_W": f"{vent_slot_width:.4g} mm",
        "VENT_SLOT_H": f"{vent_slot_height:.4g} mm",
        # level-sensing.md rod placement + size + reed count.
        "ROD_DIAMETER": f"{rod_diameter:.4g} mm",
        "ROD_POSITION_X": f"{rod_position_x:.4g}",
        "ROD_POSITION_Y": f"{rod_position_y:.4g}",
        "REEDS_PER_RES": f"{reeds_per_reservoir:.4g}",
        "RESERVOIR_ROD_LEN": f"{reservoir_rod_len:.4g} mm ({reservoir_rod_len / 25.4:.3g} in)",
        # level-sensing.md — the two −Y wall holes that flank the bulkhead
        # axis, cut by _port_cuts (flavor line) and _reed_channels (cable).
        "FLAVOR_HOLE_X": f"±{flavor_line_hole_x:.4g}",
        "CABLE_HOLE_X": f"±{reservoir_bulkhead_port_x + cable_hole_offset_from_bulkhead_hole_x:.4g}",
        "WALL_HOLE_Y": f"{reservoir_bulkhead_port_y:.4g}",
        "WALL_HOLE_Z": f"{bulkhead_elbow_exit_z:.4g}",
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
        "BULKHEAD_PANEL_HOLE_D": f"{bulkhead_panel_hole_diameter:.4g} mm",
        "BULKHEAD_WET_NUT_OD": f"{bulkhead_wet_nut_od:.4g} mm",
        "BULKHEAD_DRY_FLANGE_OD": f"{bulkhead_dry_flange_od:.4g} mm",
        "BULKHEAD_SEAL_ID": f"{bulkhead_seal_id:.4g} mm",
        "BULKHEAD_SEAL_WET_OD": f"{bulkhead_seal_wet_od:.4g} mm",
        "BULKHEAD_SEAL_DRY_OD": f"{bulkhead_seal_dry_od:.4g} mm",
        "BULKHEAD_SEAL_WET_CB_D": f"{bulkhead_seal_wet_counterbore_diameter:.4g} mm",
        "BULKHEAD_SEAL_DRY_CB_D": f"{bulkhead_seal_dry_counterbore_diameter:.4g} mm",
        "BULKHEAD_SEAL_BOSS_D": f"{bulkhead_seal_boss_diameter:.4g} mm",
        "BULKHEAD_SEAL_THICKNESS": f"{bulkhead_seal_thickness:.4g} mm",
        "BULKHEAD_SEAL_CB_DEPTH": f"{bulkhead_seal_counterbore_depth:.4g} mm",
        "BULKHEAD_SEAL_COMPRESSION": f"{(bulkhead_seal_thickness - bulkhead_seal_counterbore_depth) / bulkhead_seal_thickness * 100:.0f}%",
        "BULKHEAD_BELOW_FLOOR_STACK": f"{bulkhead_below_floor_stack:.4g} mm",
        "FLOOR_BELOW_TROUGH_HEADROOM": f"{floor_below_trough_headroom:.4g} mm",
        "OUTER_Y_MAX": f"{outer_y_max:.4g} mm",
        "OUTER_CENTERWARD_R": f"{outer_centerward_radius:.4g} mm",
        "INNER_Y_MAX": f"{inner_y_max:.4g} mm",
        "OUTER_TAB_ANGLE": f"{outer_tab_interior_angle:.0f}°",
        "INNER_CORNER_ANGLE": f"{inner_corner_interior_angle:.0f}°",
        "CAP_COUNTERBORE_D": f"{cap_counterbore_diameter:.4g} mm",
        "CAP_CLEARANCE_HOLE_D": f"{cap_clearance_hole_diameter:.4g} mm",
        "GASKET_STRIP_W": f"{gasket_strip_width:.4g} mm",
        "GASKET_THICKNESS": f"{gasket_thickness:.4g} mm",
        "RETAINING_RING_T": f"{retaining_ring_thickness:.4g} mm",
        "RETAINING_RING_ID": f"{retaining_ring_inner_diameter:.4g} mm",
        "RESERVOIR_CLEARANCE": f"{reservoir_clearance:.4g} mm",
        "VENT_CYL_WALL_T": f"{vent_cylinder_wall_thickness:.4g} mm",
        "INSERT_POCKET_DEPTH": f"{insert_pocket_depth:.4g} mm",
        "OUTER_FILLET_R": f"{outer_corner_fillet_radius:.4g} mm",
        # Screw-boss corner row Y, and the inner-wall corner the boss-4/5
        # cut planes aim at (curve × inner +Y wall), plus the boss-to-corner
        # distance that explains the virtual-pivot offset.
        "CORNER_XY_Y": f"{_corner_xy_y:.4g}",
        "INNER_CORNER_CURVE_X": f"{_inner_corner_curve_x:.4g} mm",
        "CORNER_CURVE_DIST": f"{_corner_curve_to_inner_corner_dist:.4g} mm",
        # Gasket insert pad OD, retaining-ring OD, vent base-plate thickness.
        "GASKET_PAD_D": f"ø{2 * gasket_pad_radius:.4g}",
        "RETAINING_RING_OD": f"ø{retaining_ring_outer_diameter:.4g}",
        "VENT_BASE_PLATE_T": f"{cap_base_thickness - vent_pocket_depth:.4g} mm",
    }
    substitute_md(
        here / ".." / "foam-shell" / "README.md",
        variables=variables,
        expected_counts={
            "RESERVOIR_W": 1,
            "RESERVOIR_D": 1,
            "RESERVOIR_H": 1,
        },
    )
    print("-> foam-shell/README.md (reservoir section)")
    substitute_md(
        here / "vent.md",
        variables=variables,
        expected_counts={
            "FILTER_D": 3,
            "FILTER_T": 3,
            "VENT_POCKET_D": 2,
            "VENT_POCKET_DEPTH": 2,
            "VENT_BOSS_OD": 1,
            "VENT_BOSS_WALL": 1,
            "VENT_HOLE_D": 1,
            "VENT_CYL_OD": 1,
            "VENT_CYL_ID": 1,
            "VENT_SLOT_COUNT": 1,
            "VENT_SLOT_W": 1,
            "VENT_SLOT_H": 1,
        },
    )
    print("-> vent.md")
    substitute_md(
        here / "level-sensing.md",
        variables=variables,
        expected_counts={
            "ROD_DIAMETER": 2,
            "ROD_POSITION_X": 2,
            "ROD_POSITION_Y": 1,
            "REEDS_PER_RES": 9,
            "RESERVOIR_ROD_LEN": 1,
            "FLAVOR_HOLE_X": 1,
            "CABLE_HOLE_X": 2,
            "WALL_HOLE_Y": 1,
            "WALL_HOLE_Z": 1,
            "RESERVOIR_CLEARANCE": 1,
        },
    )
    print("-> level-sensing.md")
    substitute_md(
        here / "floor-and-bulkhead.md",
        variables=variables,
        expected_counts={
            "BULKHEAD_PANEL_HOLE_D": 2,
            "BULKHEAD_DRY_FLANGE_OD": 2,
            "BULKHEAD_SEAL_WET_OD": 1,
            "BULKHEAD_WET_NUT_OD": 1,
            "BULKHEAD_SEAL_DRY_OD": 1,
            "BULKHEAD_BELOW_FLOOR_STACK": 1,
            "FLOOR_BELOW_TROUGH_HEADROOM": 1,
        },
    )
    print("-> floor-and-bulkhead.md")
    substitute_md(
        here / ".." / ".." / ".." / "off-the-shelf-parts" / "puresec-90-bulkhead" / "geometry-description.md",
        variables=variables,
        expected_counts={
            "BULKHEAD_PANEL_HOLE_D": 2,
            "BULKHEAD_SEAL_ID": 2,
            "BULKHEAD_DRY_FLANGE_OD": 4,
            "BULKHEAD_WET_NUT_OD": 3,
            "BULKHEAD_SEAL_WET_OD": 3,
            "BULKHEAD_SEAL_DRY_OD": 3,
            "BULKHEAD_SEAL_THICKNESS": 1,
            "BULKHEAD_SEAL_COMPRESSION": 1,
            "BULKHEAD_SEAL_WET_CB_D": 1,
            "BULKHEAD_SEAL_DRY_CB_D": 1,
            "BULKHEAD_SEAL_CB_DEPTH": 2,
            "RESERVOIR_WALL_T": 2,
        },
    )
    print("-> off-the-shelf-parts/puresec-90-bulkhead/geometry-description.md")
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "RESERVOIR_WALL_T": 3,
            "CAP_TOTAL_H": 1,
            "VENT_POCKET_D": 4,
            "VENT_BOSS_OD": 2,
            "VENT_HOLE_D": 2,
            "VENT_CYL_OD": 2,
            "ROD_BORE": 1,
            "ROD_DIAMETER": 1,
            "FILTER_D": 1,
            "CAP_COUNTERBORE_D": 2,
            "CAP_CLEARANCE_HOLE_D": 3,
            "GASKET_STRIP_W": 1,
            "GASKET_THICKNESS": 1,
            "RETAINING_RING_T": 2,
            "RETAINING_RING_ID": 1,
            "RESERVOIR_CLEARANCE": 1,
            "BULKHEAD_SEAL_CB_DEPTH": 1,
            "VENT_CYL_WALL_T": 1,
            "INSERT_POCKET_DEPTH": 3,
            "OUTER_FILLET_R": 8,
            "ROD_BOSS_OD": 1,
            "BODY_BOSS_R": 3,
            "BODY_BOSS_D": 2,
            "CAP_BOSS_R": 1,
            "CAP_STACK_H": 1,
            "CAP_ASSEMBLY_LIFT": 1,
            "CAP_TOP_Z": 1,
            "RESERVOIR_H": 1,
            "RESERVOIR_ROD_LEN": 1,
            "REEDS_PER_RES": 1,
            "BULKHEAD_PANEL_HOLE_D": 2,
            "BULKHEAD_WET_NUT_OD": 7,
            "BULKHEAD_DRY_FLANGE_OD": 10,
            "BULKHEAD_SEAL_ID": 2,
            "BULKHEAD_SEAL_WET_OD": 1,
            "BULKHEAD_SEAL_DRY_OD": 2,
            "BULKHEAD_SEAL_WET_CB_D": 1,
            "BULKHEAD_SEAL_DRY_CB_D": 1,
            "BULKHEAD_SEAL_BOSS_D": 2,
            "OUTER_Y_MAX": 1,
            "OUTER_CENTERWARD_R": 1,
            "INNER_Y_MAX": 4,
            "OUTER_TAB_ANGLE": 3,
            "INNER_CORNER_ANGLE": 3,
            "CORNER_XY_Y": 1,
            "INNER_CORNER_CURVE_X": 2,
            "CORNER_CURVE_DIST": 3,
            "GASKET_PAD_D": 2,
            "RETAINING_RING_OD": 1,
            "VENT_BASE_PLATE_T": 1,
        },
    )
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
