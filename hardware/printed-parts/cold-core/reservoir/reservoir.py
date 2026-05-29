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
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
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
    reservoir_clearance,
    reservoir_floor_thickness,
    reservoir_bulkhead_port_x,
    reservoir_bulkhead_port_y,
    make_box,
)
from _reed_channels import reeds_per_reservoir


def _z_cylinder(anchor_xy, z_range, diameter):
    """Solid cylinder with axis along world +Z, centered at anchor_xy =
    (world_x, world_y), spanning z_range = (z_bottom, z_top). The Z-axis
    is the natural extrude direction for almost every cylindrical
    feature in this file (boss, bore, pocket, cap, vent shell)."""
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
# centerward concave-curve) of uniform 4 mm PETG. The top is closed by
# a separately-printed cap clamped down through a TPU gasket with six
# M3 screws into heat-set inserts.
#
# All six surfaces of the assembled stack (floor + 4 walls + cap) are
# 4 mm thick where the body provides them; the cap adds another base
# plate + perimeter wall on top. FDM can't reliably bridge a 140 × 90 mm
# horizontal span at 4 mm thickness with no internal supports — hence
# the open-top + separate-cap split.
#
# `reservoir_floor_thickness` on the shell side names the PETG layer
# the foam-shell cares about (the layer it leaves clearance above);
# reused locally for every wall in the reservoir body.
# [4 mm](RESERVOIR_WALL_T) — uniform PETG thickness for floor + every wall.
reservoir_wall_thickness = reservoir_floor_thickness


# Sharp-corner fillets where the centerward curve meets the ±Y walls.
# At y = ±70 mm the outer centerward curve (radius 72 mm) meets the
# outer ±Y walls — ~13° interior angle, a pointy tab that's structurally
# useless and won't FDM cleanly. At y = ±66 mm the inner centerward curve
# meets the inner ±Y walls inside the syrup volume — ~30° interior angle
# that would trap residual liquid. Same radius on both for visual
# consistency. 6 mm is chosen to match body_boss_radius so the corner
# bosses (positions 4/5, centered on the outer fillet) fit fully inside
# the post-fillet wall material — see body_boss_radius below.
outer_corner_fillet_radius = 6.0
inner_corner_fillet_radius = 6.0


# Cap geometry. Base plate (top, the flat surface) + perimeter wall
# (bottom, the "lip" hanging down around the gasket joint). The base
# plate hosts the counterbored screw heads on its flat top face; the
# perimeter wall provides depth for the screw shaft to pass through to
# the gasket + body insert below.
cap_base_thickness = 4.0  # = reservoir_wall_thickness; the cap's flat top is a fluid barrier (only the perimeter is gasket-sealed; the cavity interior reaches the cap base plate directly), so it carries the same 4 mm minimum as the body walls
cap_wall_height = 5.0
cap_wall_width = 6.0

# Screw recess geometry. M3 SHCS head OD ~5.5 mm; ø6 counterbore is
# the standard fit. Counterbore depth tracks cap_base_thickness so
# the counterbore recesses the screw head through the full base
# plate (M3 SHCS head is ~3 mm tall, so the deeper counterbore has
# ~1 mm of empty clearance above the head — harmless); the remaining
# clearance hole through the perimeter wall carries the shaft to the
# gasket + body insert below. Keeping counterbore = base thickness
# preserves the M3 × 12 screw stack length.
cap_counterbore_diameter = 6.0
cap_counterbore_depth = cap_base_thickness
cap_clearance_hole_diameter = 3.5


# TPU 85A flat gasket between the body wall top and the cap base plate
# bottom, compressed by the six M3 × 12 screws. 5 mm-wide perimeter ring
# (covers the 4 mm body wall plus 1 mm extending inward over the cavity
# opening, since a 4 mm TPU strip alone warps during print); ø12 circular
# pads at each insert position give the screw clamp a uniform compressed
# disk; ø3.5 clearance holes through each pad.
gasket_thickness = 2.0
gasket_strip_width = 5.0
gasket_pad_radius = 6.0  # ø12, matches body boss (insert_pocket_radius + 4); the gasket pad provides full compression contact under each cap boss / body boss face


# Cap-local Z ranges. Cap is built around its own z=0 (perimeter wall
# bottom). To visualize the assembled stack, translate the cap up by
# (outer_z_range[1] + gasket_thickness).
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
# Filter: LVDALAB ø13 PTFE-on-PET membrane (Amazon B0D41KT345)
# Retaining ring: 2 mm-thick TPU 90A, press-fit into the cap pocket
filter_diameter = 13.0
filter_thickness = 0.5

retaining_ring_thickness = 2.0
retaining_ring_outer_diameter = 13.4  # 0.1 mm interference per side vs the ø13.2 pocket, so the TPU 90A ring compresses in for a light press-fit
retaining_ring_inner_diameter = 9.0   # leaves most of the membrane exposed for airflow

# Filter pocket (cylindrical recess in the cap top) holds the
# filter + ring stack with 0.2 mm of slip-fit clearance.
# [13.2 mm](VENT_POCKET_D) — filter ⌀ + 0.1 mm/side clearance.
vent_pocket_diameter = filter_diameter + 0.2
vent_pocket_depth = filter_thickness + retaining_ring_thickness

# Below the pocket, the cap material is locally thicker than the
# standard base plate so the small vent hole has enough material
# around it to pass through cleanly before transitioning to the
# cylinder. This local thickening = "the boss" — it protrudes below
# the standard base plate bottom by (boss depth − base plate thickness).
vent_hole_diameter = 5.0
vent_below_pocket_material = 2.5  # cap material thickness between pocket bottom and boss bottom
vent_boss_wall_around_pocket = 2.0
# [17.2 mm](VENT_BOSS_OD) — pocket ⌀ + 2 × wall around pocket.
vent_boss_outer_diameter = vent_pocket_diameter + 2 * vent_boss_wall_around_pocket
_vent_boss_depth = vent_pocket_depth + vent_below_pocket_material
_vent_boss_extension_below_base_plate = _vent_boss_depth - cap_base_thickness

# Cylinder shell hangs below the boss into the reservoir, with the
# same inside diameter as the vent hole so there's no internal step
# in the air column. The cylinder outer diameter matches the brim
# diameter (= a beefy 2.5 mm wall) so the brim is flush with the
# cylinder rather than overhanging it — the brim becomes the closed
# bottom of a single ø10 cylinder, and the cylinder→brim transition
# has no overhang to print during top-down FDM of the cap.
vent_cylinder_inner_diameter = vent_hole_diameter
vent_cylinder_wall_thickness = 2.5
# [10 mm](VENT_CYL_OD) — cylinder ID + 2 × wall (matches brim ⌀ so brim is flush with cylinder).
vent_cylinder_outer_diameter = vent_cylinder_inner_diameter + 2 * vent_cylinder_wall_thickness
vent_brim_thickness = 1.0
vent_brim_diameter = vent_cylinder_outer_diameter  # matches cylinder outer (10)

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
# the y=0 and y=+65 rows of screw bosses (so the ø17 vent boss and
# its counterbore-sized pocket clear every screw counterbore and
# every cap-side boss), and inside the perimeter wall. Mirrored
# across x=0 for side=−1.
vent_position_x = 96.0
vent_position_y = 32.5

# Vent z stack, in cap-local coordinates (anchored from cap_total_height
# at the top). Top→bottom: filter pocket / boss extension below the
# base plate / cylinder shell with the four side slots / closed brim.
vent_pocket_bottom_z = cap_total_height - vent_pocket_depth
vent_boss_bottom_z = cap_total_height - _vent_boss_depth
vent_cylinder_walls_bottom_z = vent_boss_bottom_z - (vent_cylinder_length - vent_brim_thickness)
vent_brim_bottom_z = vent_cylinder_walls_bottom_z - vent_brim_thickness


# Level-sensing rod: a vertical 3.175 mm (1/8") × 305 mm (12") 316 SS
# round rod, body-anchored and cap-registered. A small magnetic float
# slides up and down the rod as the syrup level changes; [4](REEDS_PER_RES) reed
# switches mounted outside the reservoir pocket's far +X wall (foam-
# encapsulated during the foam pour) detect the float's position. Same
# rod SKU as the carbonator's existing reed+float level sensing — see
# `hardware/future.md` "Level sensing" and bom.md Tandefio B0CY4DWJFQ.
#
# Architecture:
#   - The body has a standing solid PETG cylindrical boss rising from
#     the wet slope at (±rod_position_x, rod_position_y). A blind bore
#     is cut down into the boss from above, stopping rod_anchor_boss_floor
#     mm short of the boss base so the rod tip bottoms out on printed-
#     solid PETG inside the boss. The wet slope is unbroken (no hole).
#   - The cap has a hollow register boss hanging down from its
#     underside, with a downward-opening blind bore around the rod's
#     top. The rod is captured at BOTH ends — that two-point capture
#     is what keeps a 1/8" × 305 mm rod stiff enough to take float-
#     loading without leaning.
#   - During assembly the rod drops into the body boss first; the cap
#     is then lowered onto the body and the rod's top slides into the
#     cap register as the cap seats on the gasket.
#
# Position chosen to sit opposite the bulkhead (y = 28..64 on the +Y
# half), in the wider part of the cavity (~38 mm wide at y=-45 vs
# ~24 mm at y=0) where the donor donut float has generous clearance,
# clear of all screw bosses and the vent boss.
rod_position_x = 100.0  # |x| of the rod centerline; mirrors with `side`
rod_position_y = -45.0  # y of the rod centerline; does NOT mirror with side
rod_diameter = 3.175  # 1/8" 316 SS round rod OD; supplied as Tandefio B0CY4DWJFQ
# [3.675 mm](ROD_BORE) — rod ⌀ + 0.5 mm clearance; shared by body anchor boss and cap register boss.
rod_bore = rod_diameter + 0.5  # printed bore shared by body anchor boss and cap register boss; ~0.5 mm radial slip-fit clearance accounting for PETG shrink + FDM hole undersize
# [7.675 mm](ROD_BOSS_OD) — bore ⌀ + 4 mm (2 mm radial wall); shared by body anchor and cap register bosses.
rod_boss_od = rod_bore + 4.0  # 2 mm radial wall around the bore; shared by body-side anchor boss and cap-side register boss
rod_register_boss_height = 4.0  # CAP-side boss height; boss bottom 2 mm below the rod top, 2 mm of axial rod-boss engagement
rod_anchor_boss_height = 10.0  # BODY-side anchor boss height; taller than the cap boss because this end ANCHORS the rod (≈3× rod_diameter, standard rule of thumb for solid axial location)
rod_anchor_boss_floor = 2.0  # thickness of the printed-solid PETG floor INSIDE the body boss between the blind bore's bottom and the slope surface — the rod tip bottoms out on this


# Outlet bulkhead port + V floor. A PureSec 1/4" RO push-to-connect 90°
# elbow bulkhead (Amazon B0968K4JRN — white polypropylene, water/RO/
# beverage-rated, ships WITHOUT a panel o-ring) clamps VERTICALLY through
# the cavity floor's central trough. Its threaded barrel passes DOWN
# through the trough floor; its integral flange disc (⌀22) seats on the
# wet (cavity-side, top) face of the trough floor through a printed TPU
# face seal in a horizontal (Z-down) counterbore; the hex locknut threads
# on from BELOW the floor, in the open bag-pocket cavity beneath the
# reservoir, registered against rotation by a shallow floor-underside hex
# pocket. The part is an L-body: the wet-side push-to-connect port is on
# the barrel axis (faces UP into the syrup volume); an integral cast 90°
# elbow on the dry side turns the line laterally toward the bag-pocket +Y
# pass-through, so no separate union elbow is needed. The elbow body +
# its lateral PTC port sit just above/around the flange (low in the
# cavity); the threads, locknut, and barrel-end PTC hang below the floor.
#
# Geometry is best-estimate from the listing + a single cluttered photo;
# see ../../../off-the-shelf-parts/puresec-90-bulkhead/geometry-description.md
# for the per-constant mapping + confidence. The ⌀16 mounting hole, the
# no-o-ring fact, and the integral 90° elbow are HIGH confidence; thread
# OD/length, flange OD, locknut across-flats, and the elbow envelope/
# offset are MEDIUM/LOW (flagged inline below).
#
# Floor: a Y-symmetric V swept across the full cavity X width. From
# each ±Y wall the floor slopes inward and DOWN to a flat rectangular
# trough centered at y=0 that spans the full interior X width and hosts
# the port. The floor is a single Y–Z section (slope down / flat /
# slope up) extruded straight across X; the only curved floor boundary
# is the cavity's existing centerward arc. There is NO circular pad.
# Syrup drains by gravity from anywhere in the cavity down the V to the
# trough and into the up-facing wet port. The whole V is RAISED (see
# floor_trough_lift) so the locknut + integral elbow fit in the open
# bag-pocket space below the trough floor underside.
#
# reservoir_bulkhead_port_x: midpoint between cavity's inner +X face and
#   the concave arc's peak (imported from _cold_core_interface). Reused
#   AS-IS as the trough/port X center. The port sits at y=0.

bulkhead_panel_hole_diameter = 16.5  # PureSec listing ⌀16 mounting hole + 0.5 mm print/clearance allowance so the printed hole reliably accepts the ⌀15 threaded barrel through print tolerance + slight body OD variation. Threads are NOT modelled — this is a plain bore. Cut straight down (−Z) through the trough floor.

# Nut hex pocket on the floor underside. The locknut threads on from
# below in the open bag-pocket space; this shallow hex recess in the
# dry (underside) floor face registers the nut against rotation while
# it's tightened. The nut's hex portion is technically a 12-sided shape
# (the 6 hex corners are clipped well inside the washer's outer ⌀), but
# the print pocket can safely treat it as a regular hex of the given
# flat-to-flat dimension — the pocket overshoots by ~1 mm of air at
# each corner, which doesn't affect the grip on the 6 flats.
bulkhead_nut_hex_flat_to_flat = 20.0  # PureSec hex locknut across-flats (MEDIUM — photo ratio to the ⌀15 threaded bore); the 6 flats grip the pocket for anti-rotation
bulkhead_nut_hex_corner_to_corner = bulkhead_nut_hex_flat_to_flat / math.cos(math.radians(30))  # ~1 mm past the actual clipped corners
bulkhead_nut_clearance = 0.1  # per-side clearance for the hex flats
bulkhead_nut_hex_pocket_depth = 1.5  # shallow register only — most of the nut hangs in the open bag-pocket space below the floor, so the pocket needn't recess the full nut height

# Flat-top hex profile for the nut pocket, sketched in the XY plane
# (the floor underside). Vertices at 0°, 60°, ... 300° from +X.
nut_hex_radius = (bulkhead_nut_hex_corner_to_corner + 2 * bulkhead_nut_clearance) / 2
nut_hex_profile = [
    (nut_hex_radius * math.cos(math.radians(a)),
     nut_hex_radius * math.sin(math.radians(a)))
    for a in (0, 60, 120, 180, 240, 300)
]

# TPU 85A wet-side face seal at the bulkhead/floor joint. The PureSec
# ships with NO panel o-ring, so this printed TPU washer is the only
# fluid seal at the barrel-to-floor joint. A flat printed washer sits in
# a shallow Z-down counterbore in the trough's wet (top) face and is
# compressed when the integral flange seats flush against the floor rim
# outside the counterbore. Compression ratio is
# (seal_thickness − counterbore_depth) / seal_thickness = 30%, standard
# for face-seal elastomers. The counterbore Ø is sized smaller than the
# PureSec flange OD (⌀22) so the flange seats directly on PETG outside
# the counterbore — PETG carries the clamping force, the elastomer
# carries only the seal-compression load. (Only the wet-side seal is
# modelled; the dry side seats against the locknut in open space below,
# no counterbore there.)
bulkhead_seal_id = 15.5  # washer ID = PureSec threaded barrel OD (⌀15) + ~0.5 mm so the washer slips over the barrel; the barrel passes through the seal, not around it (MEDIUM). Slightly under the ⌀[16.5 mm](BULKHEAD_PANEL_HOLE_D) panel hole, so the seal's inner edge overhangs the hole by 0.5 mm/side.
bulkhead_seal_od = 21.3  # 0.1 mm/side clearance in the counterbore; stays under the ⌀22 PureSec flange so the flange seats on PETG outside the seal
bulkhead_seal_thickness = 2.0  # matches the reservoir gasket convention
bulkhead_seal_counterbore_diameter = 21.5  # 0.3 mm/side PETG seating ring under the PureSec ⌀22 integral flange disc
bulkhead_seal_counterbore_depth = 1.4  # 30% compression of the 2 mm seal when the flange seats flush

# PureSec integral 90° elbow + push-to-connect ports (the JG part had no
# integral elbow). All best-estimate from the listing photo; see
# ../../../off-the-shelf-parts/puresec-90-bulkhead/geometry-description.md.
# The dry line turns laterally at the elbow and runs out to the
# bag-pocket +Y pass-through; modelled here as a clearance KEEP-OUT
# volume below/around the trough floor, NOT a precise replica of the
# fitting.
bulkhead_ptc_tube_diameter = 6.35  # 1/4" tube OD (HIGH — shared JG 1/4" collet family)
bulkhead_ptc_release_ring_diameter = 9.57  # PTC collet release-ring OD (HIGH — shared JG 1/4" collet family)
bulkhead_ptc_port_body_diameter = 12.5  # PTC collet barrel OD (MEDIUM — photo column-scan)
bulkhead_elbow_lateral_offset = 15.0  # barrel axis → lateral-PTC centerline (LOW-MED — photo ratio ≈1× thread OD)
bulkhead_elbow_envelope_x = 28.0  # lateral extent of the cast 90° body + lateral collet barrel (LOW — photo bounding box). Modelled along ±Y here (toward the pass-through), see orientation note below.
bulkhead_elbow_envelope_y = 16.0  # transverse extent of the elbow body (LOW)
bulkhead_elbow_envelope_z = 16.0  # vertical extent of the elbow body (LOW)

# ORIENTATION (FLAG for STEP review — low confidence, derived from one
# cluttered photo): the PureSec is an L-body with the wet PTC on the
# barrel axis and the lateral PTC on the elbow leg. The exact pose of
# the L — which way the elbow turns, and whether its body sits just
# above/around the flange (inside the cavity) vs purely below the floor
# — is uncertain. Here the barrel is kept vertical through the trough,
# and the elbow's lateral PTC port is aimed toward +Y (the existing
# bag-pocket pass-through at reservoir_bulkhead_port_y), so the modelled
# elbow keep-out + lateral PTC stub extend in +Y from the barrel axis.
# The elbow is modelled as a clearance volume only. CONFIRM against the
# physical part on arrival; this assumption does not change the
# panel-hole / nut-pocket / seal numbers.
bulkhead_elbow_lateral_sign = +1  # +Y; the pass-through is on +Y

# V floor section (Y–Z), extruded straight across the full cavity X.
# The flat trough at y=0 is the cavity's low point and the lowest
# drainable line; the slopes rise from the trough edges to the ±Y
# walls. (floor_trough_z, the slope rate, and the wedge extrusion top
# are derived below, after inner_z_range / inner_y_max are defined.)
#
# The reservoir's weight rides on the corner support posts — they stand
# on the bag-pocket floor and reach the floor underside. So the V floor is
# raised only as far as the bulkhead hardware hanging below it demands: the
# PureSec locknut + elbow body drop bulkhead_below_floor_stack beneath the
# trough underside, and that lowest point clears the bag-pocket floor by
# just bulkhead_floor_clearance — the elbow sits basically on the pocket
# floor and never bears the reservoir's weight. The lift is derived from
# that intent, not set by hand. (floor underside = bag_pocket_floor_top_z
# + reservoir_clearance + floor_trough_lift, so the lift below puts the
# underside exactly stack+clearance above the pocket floor.)
bulkhead_below_floor_stack = 10.0  # PureSec locknut + elbow body hanging below the trough-floor underside
bulkhead_floor_clearance = 1.0  # gap from the lowest bulkhead hardware down to the bag-pocket floor — kept non-load-bearing
floor_trough_lift = bulkhead_floor_clearance + bulkhead_below_floor_stack - reservoir_clearance
floor_trough_half_width_y = 14.0  # half the flat trough's Y extent; wide enough to host the ⌀21.5 seal counterbore + the flange seat with margin
floor_slope_rise = 6.0  # mm the floor rises from the trough surface to each ±Y wall


# Heat-set insert + screw spec. M3 ruthex-style brass heat-set inserts
# (same as foam-shell cap-stack joinery). Insert OD 4 mm × length 4 mm;
# pocket is 4 mm bore × 7 mm deep (4 mm insert + 3 mm relief). Screws:
# BNUOK M3 × 12 mm DIN 912 SHCS, black oxide 12.9 alloy (Amazon
# B0DJQGVK8S), same brand/finish as the M3 × 25 used on the foam-shell
# cap stack but the right length for the reservoir's thinner cap-stack
# geometry (under-head stack is 7 mm cap-plus-gasket vs ~19 mm there).
# With M3 × 12, the shaft seats 4 mm into the insert, runs another 1 mm
# into the pocket relief, and leaves 2 mm of slack between the shaft
# tip and the pocket floor.
insert_pocket_radius = 2.0
insert_pocket_depth = 7.0

# Boss radii — chosen so each through-hole has a 4 mm PETG annulus
# around it (matches the body-wall / floor / cap fluid-barrier minimum,
# since the boss wall around the pocket/clearance hole separates the
# cavity from the pocket interior):
#   Body insert pocket ø4 + 4 mm PETG → body boss ø12 (radius 6)
#   Cap clearance hole ø3.5 + 4 mm PETG → cap boss ø11.5 (radius 5.75)
# [6 mm](BODY_BOSS_R) — insert pocket radius + 4 mm PETG annulus.
body_boss_radius = insert_pocket_radius + 4.0
# [5.75 mm](CAP_BOSS_R) — half of cap clearance ⌀ + 4 mm PETG annulus.
cap_boss_radius = cap_clearance_hole_diameter / 2.0 + 4.0

# Body boss vertical layout (extruding downward from the wall top):
#   top 7 mm:  pocket (ø4 hole for heat-set insert + screw shaft)
#   below:     solid ø12 cylinder. Built extra-long (extending below
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
# stays within the 7 mm heat-set pocket (see body_boss_cut_info_for_side_plus_1
# below). The outer fillet radius (6 mm) equals body_boss_radius so
# the corner-boss disks inscribe the fillet arc exactly.
boss_height = 13.0  # 7 mm pocket + 6 mm of solid+cut
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

# Body Z ranges. outer_z_range is the body's vertical extent (floor's
# outer face to wall top). inner_z_range is the cavity's extent (cavity
# floor sits one wall up; top opens to the cap above the gasket).
# cap_stack_above_body is how much room the gasket + cap takes above
# the body's wall top — leaves the cap's top face flush at z=212.9
# (0.5 mm clear of the bag-pocket wall top); body alone is 199.4 mm tall.
# [11 mm](CAP_STACK_H) — gasket + cap perimeter wall + cap base plate.
cap_stack_above_body = gasket_thickness + cap_wall_height + cap_base_thickness
outer_z_range = (
    bag_pocket_floor_top_z + reservoir_clearance,
    bag_pocket_walls_top_z - reservoir_clearance - cap_stack_above_body,
)
inner_z_range = (outer_z_range[0] + reservoir_wall_thickness, outer_z_range[1])

# V-floor derived geometry (needs inner_z_range / inner_y_max above).
# floor_trough_z is the trough's wet (top) surface. It is RAISED
# floor_trough_lift above the base cavity floor (inner_z_range[0]) so the
# PureSec locknut + barrel-end PTC + integral elbow clear in the open
# bag-pocket space below the trough-floor underside (the underside sits
# at floor_trough_z − reservoir_wall_thickness; below it, down to the
# bag-pocket floor, is open). The slope runs from
# (|y| = floor_trough_half_width_y, z = floor_trough_z) up to
# (|y| = inner_y_max, z += floor_slope_rise). The fluid-barrier PETG
# below the trough surface is the full raised thickness (the body's
# outer floor face is at outer_z_range[0], well below).
floor_trough_z = inner_z_range[0] + floor_trough_lift  # wet (top) surface of the flat trough = cavity low point, raised so the locknut/elbow fit below
# Open headroom below the trough-floor underside, down to the bag-pocket
# floor (the foam-shell pocket the reservoir drops into) — the space the
# locknut + barrel-end PTC + lower elbow body hang in. (Reported for the
# STEP review; the locknut is ~9 mm tall and registers only ~1.5 mm in
# the floor-underside pocket, so the rest of this is for it + the PTC.)
floor_below_trough_headroom = (floor_trough_z - reservoir_wall_thickness) - bag_pocket_floor_top_z
floor_slope_y_distance = inner_y_max - floor_trough_half_width_y
floor_slope_rate = floor_slope_rise / floor_slope_y_distance
# Floor wedge extrusion top — above the highest slope point so the
# slope half-spaces cut a clean upper face on the wedge fill.
floor_wedge_top_z = floor_trough_z + floor_slope_rise + 2.0

# X position where the centerward arc meets ±outer_y_max (the acute
# "tab" corner that gets filleted on every outer envelope — body,
# cap, gasket). Same shape applied at the inner cavity edge.
outer_corner_x = math.sqrt(outer_centerward_radius**2 - outer_y_max**2)
inner_corner_x = math.sqrt(inner_centerward_radius**2 - inner_y_max**2)

# Inset equals the larger boss radius so the boss outer edge just
# reaches the outer face at every position (no boss protrusion past
# the body / cap outer envelope, no overhang into the bag pocket
# clearance).
_screw_setback = max(body_boss_radius, cap_boss_radius)

# Positions 1/2 — inset 6 mm from outer +X face × outer ±Y face.
_corner_xy_x = outer_far_x_abs - _screw_setback
_corner_xy_y = outer_y_max - _screw_setback

# Position 3 — inset 6 mm from outer +X face, y = 0.
_far_mid_x = outer_far_x_abs - _screw_setback

# Position 6 — 6 mm outward from outer curve (radially), y = 0.
_curve_apex_x = outer_centerward_radius + _screw_setback

# Positions 4/5 — corner of outer curve × outer ±Y face. The corner
# is filleted at outer_corner_fillet_radius (= 6 mm). The fillet
# center is the unique point that is 6 mm from BOTH the outer +Y
# face and the outer curve, measured along the shortest path. The
# ø12 body boss disk INSCRIBES the fillet arc (radius 6 = body
# boss radius), so at these positions the boss material sits inside
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
# 7.19 mm cut depth would eat into the 7 mm heat-set pocket).
#
# Values stored for side=+1; the x component is multiplied by `side`
# in the body-boss loop to mirror across x=0 for side=−1.
_far_wall_inner_x = outer_far_x_abs - reservoir_wall_thickness
_plus_y_wall_inner_y = outer_y_max - reservoir_wall_thickness
_curve_inner_x_at_y0 = outer_centerward_radius + reservoir_wall_thickness
_inv_sqrt2 = 1.0 / math.sqrt(2.0)

# Bosses 4 / 5 need their cut direction pointed at the inner-wall
# CORNER (where the inner curve at radius _curve_inner_x_at_y0 = 76
# meets the inner ±Y wall at y = ±_plus_y_wall_inner_y = ±66), not
# at the closest point on the curve along the inward radial line.
# Pointing at the corner is the same pattern bosses 1 / 2 use (their
# cuts slope down away from the +X × ±Y inner corner). For boss 4
# the corner is at (≈37.68, 66), 7.19 mm from the boss in the
# (−X, +Y) direction — too far to use as a literal pivot (a 7.19 mm
# cut depth would eat into the 7 mm heat-set pocket). Instead, take
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
    """Open-top `[`-shaped PETG body with 4 mm walls + 4 mm floor,
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
    # coincide with boss positions (37.68, ±66) and unioning a cylinder
    # there would replace the sharp edge with a curved boss-to-wall
    # transition that the fillet operation can't pick up.
    #
    # Exterior corners (outer perimeter, ~13° interior angle) are pointy
    # tabs. Interior corners (cavity boundary, ~30° interior angle) are
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

        # Build the boss cylinder. If this boss needs a 45° cut,
        # extend the cylinder _cyl_extra_below_bottom past the
        # intended boss bottom so the cut has material to slice
        # off; otherwise build it straight from the intended bottom.
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

    # V floor — a uniform reservoir_wall_thickness (4 mm) shell, Y-symmetric,
    # swept across the full cavity X width and RAISED floor_trough_lift so the
    # PureSec locknut + integral 90° elbow hang in OPEN space below it. The
    # interior (wet) surface is the V: a flat trough at floor_trough_z for
    # |y| ≤ floor_trough_half_width_y, sloping up at floor_slope_rate to the
    # ±Y walls. The exterior (dry) surface is the same V shifted down one wall
    # thickness, so the floor is a constant 4 mm layer between them — exterior
    # slope parallels interior slope. Below the exterior surface is nothing:
    # open bag-pocket space. There is NO solid fill block and NO modelled
    # elbow/locknut keep-out — the only thing piercing the floor is the
    # bulkhead barrel bore. (Nothing supports the raised floor from below
    # yet; that is deferred.)
    #
    # _v_floor_solid(trough_top_z) is the cavity-footprint solid capped by the
    # V whose flat trough wet surface sits at trough_top_z: a trough-fill prism
    # (cavity base up to trough_top_z) unioned with the two ±Y slope wedges.
    # The shell = (solid below the interior V) − (solid below the exterior V,
    # one wall thickness lower); the subtraction also leaves everything below
    # the exterior V open.
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

    floor_underside_z = floor_trough_z - reservoir_wall_thickness
    floor_shell = _v_floor_solid(floor_trough_z).cut(_v_floor_solid(floor_underside_z))
    body = body.union(floor_shell)

    # Raise the walls + corner fillets to the floor: remove ALL material
    # below the exterior V surface across the full footprint, so the whole
    # body underside follows the 4 mm-offset V — walls, fillets, and floor
    # share one raised V bottom, with open bag-pocket space beneath for the
    # bulkhead hardware. (The exterior V is flat at floor_underside_z for
    # |y| ≤ floor_trough_half_width_y, sloping up at floor_slope_rate beyond;
    # it is a function of y only, swept across X.)
    z_below = outer_z_range[0] - 50.0
    below_v = (
        cq.Workplane(xy_plane_z_up)
        .workplane(offset=z_below)
        .rect(800, 2 * floor_trough_half_width_y)
        .extrude(floor_underside_z - z_below)
    )  # trough band: below the flat exterior underside
    for sign in (+1, -1):
        below_slope = (
            cq.Workplane(cq.Plane(
                origin=(0, sign * floor_trough_half_width_y, floor_underside_z),
                xDir=(1, 0, 0),
                normal=(0, -sign * floor_slope_rate, 1),
            ))
            .rect(2000, 2000)
            .extrude(-2000)  # below the slope (opposite the +normal "above" side)
        )
        below_v = below_v.union(below_slope.intersect(_y_half_beyond_trough(sign)))
    body = body.cut(below_v)

    # Vertical bulkhead port through the trough at (port_x, y=0). The
    # PureSec barrel clamps vertically (axis along world −Z): wet PTC port
    # up into the cavity, integral flange seated on the trough's wet (top)
    # face through a TPU face seal, hex locknut threaded on from below in
    # the open space under the floor, integral 90° elbow turning the dry
    # line laterally. Only the barrel bore pierces the 4 mm trough floor.
    port_x_signed = reservoir_bulkhead_port_x * side

    # Panel hole — ⌀[16.5 mm](BULKHEAD_PANEL_HOLE_D) cut straight down through the trough floor,
    # from above the trough wet surface down past the floor underside into
    # the open space below.
    panel_hole = _z_cylinder(
        (port_x_signed, 0.0),
        (outer_z_range[0] - 5.0, floor_trough_z + 0.1),
        bulkhead_panel_hole_diameter,
    )
    body = body.cut(panel_hole)

    # Wet-side TPU face-seal counterbore — ⌀21.5 × 1.4 mm deep, cut down
    # into the trough's wet (top) face. The flange seats on the PETG rim
    # outside it, compressing the seal 30%.
    seal_counterbore = _z_cylinder(
        (port_x_signed, 0.0),
        (floor_trough_z - bulkhead_seal_counterbore_depth, floor_trough_z + 0.1),
        bulkhead_seal_counterbore_diameter,
    )
    body = body.cut(seal_counterbore)

    # No keep-out, locknut-clearance, or nut-pocket cuts: the whole volume
    # below the raised shell is already open space, so the locknut + elbow
    # hang there freely.

    # Level-sensing rod body anchor: a solid cylindrical boss rising
    # from the NEW V floor at (±rod_position_x, rod_position_y), with a
    # blind bore cut into it from above — bore stops rod_anchor_boss_floor
    # mm short of the boss base so the printed PETG floor inside the boss
    # is what the rod tip bottoms out on. rod_position_y = −45 sits on
    # the −Y slope (between the trough edge at −14 and the −Y wall at
    # −66), so the boss base z is the slope height at that y.
    #
    # Added LAST in build_reservoir_body, after the V floor + bulkhead
    # port, so the new boss geometry cannot perturb any earlier
    # edge/face selector.
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
    """PETG cap that sits on top of the reservoir body through a 2 mm
    TPU gasket. Built in cap-local coordinates spanning cap_perimeter_z_range
    (the downward-hanging rim) and cap_base_z_range (the flat top, full
    `[` footprint). The cap's top face hosts six counterbored M3 holes
    flush with the screw heads, clearance holes continuing through the
    perimeter wall into the body's insert pockets below. Six cap-side
    bosses mirror the body bosses inside the perimeter wall, giving the
    gasket a matching cross-section at each screw position.

    To visualize the assembled stack, translate the cap up by
    (outer_z_range[1] + gasket_thickness) ≈ 214.9 mm."""
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
    # a consistent compression cross-section), ø3.5 clearance hole
    # through the cap for the screw shaft, and ø6 counterbore recessing
    # the M3 SHCS head flush with the cap's top face. Built with
    # .pushPoints over the side-mirrored anchor list — six features
    # per extrude rather than a per-position loop.
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
    # pocket (ø13.2) at the top of the base plate, then the small vent
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

    # Cut the air column: ø5 from the cylinder bottom (top of brim) up
    # to the pocket bottom. This both hollows out the cylinder body we
    # just unioned in and drills the small vent hole through the boss
    # and the 0.5 mm of base plate below the pocket.
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
    cap base plate bottom. Same `[`-shape outer footprint as the body
    and cap (with outer-corner fillets). The perimeter ring is
    gasket_strip_width inward of the outer edge — covers the 4 mm body
    wall fully plus 1 mm extending inward over the cavity opening.
    Each of the six insert positions has an ø8 pad extending inward
    beyond the ring so the screw clamp compresses a uniform disk of
    TPU (matching the body boss footprint), with an ø3.5 clearance
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

    # At each insert position: ø8 pad unioned BEFORE the hole is cut
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
    pocket floor (the shelf around the small ø5 vent hole). 2 mm
    thick. Outer ø13.0 nominal — sized for a light interference
    press-fit into the ø13.2 pocket (TPU 90A is soft enough to
    compress 0.1 mm per side without trouble). Inner ø9.0 leaves
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


def build_reservoir_bulkhead_seal():
    """Flat TPU 85A washer that seals between the bulkhead's clamping
    face and the reservoir body's panel face. Sits in a 1.4 mm-deep
    counterbore in the panel; the exposed 0.6 mm compresses to 0 (30%
    compression) when the mating face (nut washer on the wet side or
    integral flange on the dry side) seats flush against the panel
    rim outside the counterbore.

    Same part on both sides (symmetric, ID/OD/thickness are
    side-independent). Print 4 per build (one per panel face × two
    reservoirs)."""
    return (
        WorldWorkplane(xy_plane_z_up)
        .circle(bulkhead_seal_od / 2.0)
        .circle(bulkhead_seal_id / 2.0)
        .extrude(bulkhead_seal_thickness)
        .unwrap()
    )


def main():
    # Left/right convention: the machine's front face is +Y, and from
    # the front +X is the viewer's RIGHT. So side=+1 → +X reservoir →
    # "*-right.step"; side=-1 → -X reservoir → "*-left.step".
    #
    # Body and cap genuinely differ between sides — they're NOT
    # y-symmetric. The bulkhead pocket housing lives on +Y (front) for
    # both reservoirs, and the strut and vent positions stay at fixed
    # world Y (the strut at y=−45, the cap vent at y=+32.5) so they
    # remain on the back / front of the machine for both reservoirs.
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
    bulkhead_seal = build_reservoir_bulkhead_seal()
    export_step(gasket, str(here / "reservoir-gasket.step"))
    export_step(retaining_ring, str(here / "reservoir-retaining-ring.step"))
    export_step(bulkhead_seal, str(here / "reservoir-bulkhead-seal.step"))
    print(f"-> reservoir-gasket.step")
    print(f"-> reservoir-retaining-ring.step")
    print(f"-> reservoir-bulkhead-seal.step")

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
        # Dynamic-comment markers above derived constants in this .py file.
        "RESERVOIR_WALL_T": f"{reservoir_wall_thickness:.4g} mm",
        "CAP_TOTAL_H": f"{cap_total_height:.4g} mm",
        "ROD_BORE": f"{rod_bore:.4g} mm",
        "ROD_BOSS_OD": f"{rod_boss_od:.4g} mm",
        "BODY_BOSS_R": f"{body_boss_radius:.4g} mm",
        "CAP_BOSS_R": f"{cap_boss_radius:.4g} mm",
        "CAP_STACK_H": f"{cap_stack_above_body:.4g} mm",
        "BULKHEAD_PANEL_HOLE_D": f"{bulkhead_panel_hole_diameter:.4g} mm",
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
            "ROD_POSITION_X": 1,
            "ROD_POSITION_Y": 1,
            "REEDS_PER_RES": 10,
        },
    )
    print("-> level-sensing.md")
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "RESERVOIR_WALL_T": 1,
            "CAP_TOTAL_H": 1,
            "VENT_POCKET_D": 1,
            "VENT_BOSS_OD": 1,
            "VENT_CYL_OD": 1,
            "ROD_BORE": 1,
            "ROD_BOSS_OD": 1,
            "BODY_BOSS_R": 1,
            "CAP_BOSS_R": 1,
            "CAP_STACK_H": 1,
            "REEDS_PER_RES": 1,
            "BULKHEAD_PANEL_HOLE_D": 2,
        },
    )
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
