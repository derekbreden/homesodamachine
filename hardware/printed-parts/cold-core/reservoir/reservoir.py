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
    bulkhead_nut_cavity_diameter,
    reservoir_bulkhead_port_x,
    reservoir_bulkhead_port_z,
    reservoir_bulkhead_nut_z,
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


# Outlet bulkhead pocket + sloped floor. A John Guest PP1208E 1/4"
# push-to-connect bulkhead union (Amazon B00JYFU8MM, NSF 51 + NSF 61)
# is recessed entirely inside the reservoir's floor: the floor locally
# thickens into a chunky "boss" in the +X × +Y quadrant, with the
# bulkhead lying horizontally inside along the +Y axis. The wet-collet
# port opens out the boss's −Y face into the syrup volume; on the +Y
# side a ⌀6.5 channel carries the 1/4" tube out through the reservoir's
# +Y outer wall, aligning with the foam-shell pass-through at
# (±reservoir_bulkhead_port_x, reservoir_bulkhead_port_z).
#
# Body geometry (catalog): ≈ ø22.9 flange/collet OD, ≈ 34.5 overall
# length, ⌀6.35 push-to-connect at each end. Both reservoirs put the
# bulkhead on the +Y side; only x mirrors.
#
# Installation: the dry side of the pocket is wide-open below a 4 mm
# ceiling slab, so the bulkhead body passes through the panel hole
# from below and the locknut + dry collet + tube push-in are
# unobstructed. No print-pause-and-insert or split-boss assembly needed.
#
# reservoir_bulkhead_port_x: midpoint between cavity's inner +X face and the
#   concave arc's peak (imported from _cold_core_interface).
# reservoir_bulkhead_port_z: Z of the BULKHEAD BODY AXIS. Sits 1 mm above
#   reservoir_bulkhead_nut_z. Used for body chamber, wet exit tube, panel hole,
#   seal counterbores, foam-shell pass-through, dry slab anchor,
#   wet/dry slope anchor. NOT used for the nut cavity.
# reservoir_bulkhead_nut_z: Z of the NUT CAVITY center. Anchored to the floor's
#   low point so the washer counterbore sits on top of the 4 mm
#   reservoir floor, preserving the full fluid barrier. 1 mm below
#   reservoir_bulkhead_port_z per the 2026-05-16 print test.

# The pocket is asymmetric across the panel. Wet side (y < panel):
# a STEPPED cavity conforming to the bulkhead body's release-ring →
# collet → flange profile, with each step's ceiling open to the
# cavity above so syrup drains around the body to the −Y port. Dry
# side (y > panel): wide-open below a 4 mm ceiling slab — no
# symmetric "dry chamber" — so the locknut, dry collet, and 1/4"
# tube push-in are unobstructed from below, +X, and +Y. The annulus
# of PETG between the wet chamber and the slab IS the panel the
# bulkhead clamps — its −Y face seats the flange and its +Y face is
# where the locknut bears.
#
# Section lengths along +Y are estimates from typical JG bulkhead-
# union proportions (catalog total length 34.5 mm; threading section
# 3–5 mm panel range). Adjust if a caliper measurement of the part
# in hand disagrees.
# bulkhead_nut_cavity_diameter: 23.0 — ø22.9 flange + 0.1 clearance.
# Imported from _cold_core_interface because that module derives
# reservoir_bulkhead_port_z from this diameter.
bulkhead_panel_hole_diameter = 17.5  # 0.5 mm Ø over the JG catalog spec (0.67" / ⌀17.0) so the printed hole reliably accepts the JG body through print tolerance + slight body OD variation. Catalog-spec sizing is too tight in practice.

# The bulkhead body's wet side is *stepped* along its axis (flange,
# collet body, release ring — narrower toward the port). The chamber
# steps in matching sections so the syrup volume conforms to the body
# and the residual film below the port is small.
#
# Section lengths and diameters below come from a pixel-measured side
# view of the JG CI1208W (same body family, white acetal), calibrated
# against the catalog 34.5 mm total length. The full measurement
# table, confidence levels, and raw images live at
# `hardware/off-the-shelf-parts/jg-bulkhead-union/extracted-results/
# geometry-description.md`.
bulkhead_wet_chamber_length = 22.2  # sum of the three wet-side sections: flange (= nut total depth) + collet body + release ring.
bulkhead_wet_antechamber_length = 2.0  # gap on the bulkhead's wet face — must exist or syrup can't reach the port
bulkhead_panel_thickness = 6.8  # 1.4 mm-deep TPU seal counterbore on each face + 4 mm minimum PETG between the two counterbore floors = 1.4 + 4.0 + 1.4 = 6.8 mm. Panel's +Y face is anchored at bulkhead_panel_y_range[1]; the panel extends in the −Y direction from there.

# Wet-side nut. The actual hardware sitting at y=bulkhead_panel_y_range[0] on the
# wet side is the *nut*, not an integral flange — the bulkhead is
# inserted from the dry side and the integral flange ("not-a-nut",
# fused to the body) ends up on the dry side. The nut is a stepped
# washer+hex piece dropped into the wet pocket before insertion and
# held there by a hex-shaped print pocket while the bulkhead screws
# in through it. The nut's hex portion is technically a 12-sided shape
# (the 6 hex corners are clipped well inside the washer's outer ⌀),
# but the print pocket can safely treat it as a regular hex of the
# given flat-to-flat dimension — the pocket overshoots by ~1 mm of
# air at each corner, which doesn't affect the grip on the 6 flats.
bulkhead_nut_hex_flat_to_flat = 19.8  # the 6 flats that grip the pocket for anti-rotation
bulkhead_nut_hex_corner_to_corner = bulkhead_nut_hex_flat_to_flat / math.cos(math.radians(30))  # ~1 mm past the actual clipped corners
bulkhead_nut_washer_diameter = 22.1
bulkhead_nut_hex_depth = 4.6  # axial depth of the hex portion. Sized ~0.5 mm over the nominal nut hex height so the nut seats fully despite print-tolerance variation. NOTE: bulkhead_release_ring_length is derived from bulkhead_wet_chamber_length − bulkhead_flange_length − bulkhead_collet_body_length, so growth here shrinks the release-ring chamber proportionally.
bulkhead_nut_washer_depth = 1.6  # axial depth of the washer portion
bulkhead_nut_total_depth = bulkhead_nut_hex_depth + bulkhead_nut_washer_depth
bulkhead_nut_clearance = 0.1  # per-side clearance for press-fit (both hex flats and washer ⌀)

# Flat-top hex profile for the nut pocket. Vertices at 0°, 60°, ...
# 300° from +X put flats at ±Z so the ceiling box opens along a flat
# edge, matching the round chambers' stadium geometry.
nut_hex_radius = (bulkhead_nut_hex_corner_to_corner + 2 * bulkhead_nut_clearance) / 2
nut_hex_profile = [
    (nut_hex_radius * math.cos(math.radians(a)),
     nut_hex_radius * math.sin(math.radians(a)))
    for a in (0, 60, 120, 180, 240, 300)
]

# TPU 85A face seals at the bulkhead/panel joint. One on each side of
# the panel: a flat printed washer that sits in a shallow counterbore
# in the panel face and gets compressed when the mating face (nut
# washer on the wet side, integral flange on the dry side) seats flush
# against the panel rim outside the counterbore. Compression ratio is
# (seal_thickness − counterbore_depth) / seal_thickness = 30%, which
# is standard for face-seal elastomers. The counterbore Ø is sized
# smaller than both mating-face ODs (nut washer ⌀22.1, integral flange
# ⌀23) so the mating faces seat directly on PETG outside the
# counterbore — PETG carries the clamping force, the elastomer
# carries only the seal-compression load.
bulkhead_seal_id = 16.5  # under the panel hole ([17.5 mm](BULKHEAD_PANEL_HOLE_D)): the seal's inner edge overhangs the panel hole by 0.5 mm/side and the bulkhead body passes through the seal, not around it. If the JG body OD at the seal location is ≤16.5 mm the seal clears it; if larger, the seal stretches over the body and adds a radial bore-seal effect on top of the axial face seal.
bulkhead_seal_od = 21.3  # 0.1 mm/side clearance in the counterbore
bulkhead_seal_thickness = 2.0  # matches the reservoir gasket convention
bulkhead_seal_counterbore_diameter = 21.5  # 0.3 mm/side PETG seating ring under the wet-side nut washer ⌀22.1 (tighter constraint); 0.75 mm/side under the dry-side flange ⌀23
bulkhead_seal_counterbore_depth = 1.4  # 30% compression of the 2 mm seal when the mating face seats flush

# Wet-side section lengths.
bulkhead_flange_length = bulkhead_nut_total_depth  # the wet-side pocket against the panel holds the *nut* (a stepped washer+hex piece), not an integral flange. The variable name labels the geometric region.
bulkhead_collet_body_length = 13.5  # middle of the wet section. Sized longer than the JG body's smooth collet section so the body has room to translate as it threads through the nut. Changes to this value shift bulkhead_release_ring_length, which absorbs the remainder of bulkhead_wet_chamber_length.
bulkhead_release_ring_length = (
    bulkhead_wet_chamber_length - bulkhead_flange_length - bulkhead_collet_body_length
)  # the visible end with the push-to-release ring
#
# Wet-side chamber diameters per section (body OD + clearance).  The
# nut pocket diameter is set by the bulkhead_nut_* constants above
# (stepped hex + washer), so it isn't repeated here.
bulkhead_collet_chamber_diameter = 19.0  # est. body OD ø17–18 + ~0.5 mm/side
bulkhead_release_chamber_diameter = 11.0  # caliper-measured release ring ø9.57 + ~0.7 mm/side

# Bulkhead Y sections, stacked +Y from the wet face (the port) outward
# through the panel. The body's release-ring → collet → flange profile
# fits into the matching wet-side step pattern; the panel hole threads
# through the +Y-most section. bulkhead_wet_end_y is the port anchor —
# stays fixed at 30; everything downstream slides as section lengths
# change. The "flange" range is named for the geometric region; it
# actually houses the nut (the integral flange ends up on the dry side).
bulkhead_wet_end_y = 30.0
bulkhead_wet_y_range = (
    bulkhead_wet_end_y - bulkhead_wet_antechamber_length,
    bulkhead_wet_end_y + bulkhead_release_ring_length,
)  # antechamber + release ring, one geometric piece
bulkhead_collet_y_range = (
    bulkhead_wet_y_range[1],
    bulkhead_wet_y_range[1] + bulkhead_collet_body_length,
)  # collet body section
bulkhead_flange_y_range = (
    bulkhead_collet_y_range[1],
    bulkhead_collet_y_range[1] + bulkhead_flange_length,
)  # nut pocket
bulkhead_panel_y_range = (
    bulkhead_flange_y_range[1],
    bulkhead_flange_y_range[1] + bulkhead_panel_thickness,
)  # panel (−Y face moved 1.8 mm in −Y to fit seal counterbores on both faces)

# The floor thickens uniformly across the cavity to a baseline whose
# inner-top z sits just above the bulkhead pocket, so the bulkhead body
# is fully encased in PETG along the panel section. The slope rises ON
# TOP of this baseline — every point of the floor surface is at least
# floor_baseline_z, and rises by floor_slope_rise to the far −Y wall.
# Outer floor stays flat at z=1 for FDM printability.
#
# Syrup drains: cavity → wet ceiling opening (above z=reservoir_bulkhead_port_z)
# → wet chamber (around the bulkhead's wet collet body) → port at
# body's −Y face. The bulkhead inlet is the lowest point the pump can
# drain to.
#
# Dry-section ceiling slab: the only PETG above the dry chamber, a
# fluid barrier above the cavity (4 mm minimum, same as the body walls
# and cap base plate). The slab's bottom is constrained from below by
# the bulkhead's dry-side flange (⌀22.9 OD, top at z=reservoir_bulkhead_port_z +
# 11.45 = 28.45), so the slab can only grow upward — i.e. the cavity
# floor rises by the slab's thickness above the chamber top.
bulkhead_dry_slab_thickness = 4.0

# 2026-05-16 print + assembly test: the dry-side slab sat directly
# on the chamber top, leaving no vertical clearance above the
# bulkhead's integral flange for a wrench to grip and rotate the
# body during install. Raise the slab BOTTOM by this much above the
# chamber top to open up wrench room. The slab still maintains its
# 4 mm thickness as the fluid barrier above; the new space between
# chamber top and slab bottom is just the air gap where a wrench /
# fingers / collet-release ring fits.
dry_ceiling_clearance = 20.0

# floor_baseline_z = top face of the dry-side slab at the panel's −Y
# edge (bulkhead_panel_y_range[0]). Stack from the chamber's curved top:
#   chamber_top + dry_ceiling_clearance + slab_thickness
# = (reservoir_bulkhead_port_z + 11.5) + 20 + 4 = reservoir_bulkhead_port_z + 35.5
# The slope tilts the slab top upward as y increases, so the
# bulkhead dry-flange clearance is positive everywhere in
# y ≥ bulkhead_panel_y_range[1].
floor_baseline_z = reservoir_bulkhead_port_z + bulkhead_nut_cavity_diameter / 2 + dry_ceiling_clearance + bulkhead_dry_slab_thickness

# On the wet side (y < bulkhead_panel_y_range[0]), the slope's lowest
# line is anchored at the bulkhead INLET MIDPOINT (reservoir_bulkhead_port_z =
# z of the port's center) — about 15.5 mm below the dry-side baseline.
# That recovers ~90 mL of cavity volume across the slope region;
# functional drainage is unchanged (syrup at the slope drops straight
# into the wet chamber's open ceiling), the win is purely volume.
slope_low_z = reservoir_bulkhead_port_z  # slope's lowest z, at y = bulkhead_panel_y_range[0] (the wet/dry boundary)

floor_slope_rise = 6.0  # mm above floor_baseline_z at the far −Y wall

# Margin keeping the wedge extrusion's top above the slope-cut planes
# so the slope half-spaces cut a clean upper face on the wedge.
wedge_extrusion_z_margin = 2.0

# How far the bulkhead chamber's ceiling cuts extend above
# floor_baseline_z. Ensures the cuts fully clear the chamber's curved
# top through the floor baseline with margin to spare.
bulkhead_ceiling_overshoot_z = 2.0

# Radius of the 90° quarter-arc swept tube continuing the wet-collet
# chamber's exit (y = bulkhead_wet_y_range[0]) through +Z until the
# tube's axis turns vertical. Arc punches well clear of the floor
# material into the open cavity above, giving syrup a designed
# curved channel from the cavity down into the bulkhead's wet face.
wet_exit_arc_radius = 30.0


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

# Floor slope rate (dz/dy). The wet-side slope rises from z=slope_low_z at
# y=bulkhead_panel_y_range[0] to z=slope_low_z + floor_slope_rise at
# y=-inner_y_max, over slope_y_distance in Y. The dry-side slope mirrors —
# same magnitude, opposite sign across the panel.
slope_y_distance = bulkhead_panel_y_range[0] - (-inner_y_max)
slope_rate = floor_slope_rise / slope_y_distance

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
    # +X × ±Y (analogous interior corner, exposed in syrup above the
    # wet wedge top). Same radius as outer for visual consistency. Adds
    # a small amount of material into the cavity tip; volume cost is
    # small because the affected z range is narrow (the wedge top sits
    # ~2 mm above floor_baseline_z, well below the cavity ceiling).
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

    # Thick sloped floor + bulkhead pocket.
    # Floor inner surface is piecewise across y, with the split at the
    # PANEL's −Y face (= where the wet nut seats and the actual
    # wet/dry boundary lives). Both slopes share the same rate
    # (floor_slope_rise / wet-slope y-distance), tilted in opposite
    # directions so they meet at the split.
    #
    #   y < bulkhead_panel_y_range[0] (wet side): floor = wet slope plane,
    #       drains to slope_low_z at y=bulkhead_panel_y_range[0], rises
    #       floor_slope_rise mm to the far −Y wall.
    #   y ≥ bulkhead_panel_y_range[0] (dry side): floor = dry slope plane,
    #       anchored at (y=bulkhead_panel_y_range[0], z=floor_baseline_z),
    #       rises at the same rate toward +Y. Stays ≥ floor_baseline_z
    #       across the dry chamber's y range so the 2 mm ceiling is
    #       preserved.
    #
    # The two planes meet at y=bulkhead_panel_y_range[0] with a vertical
    # step from slope_low_z up to floor_baseline_z. The wet chamber's
    # open ceiling already removes material at that y within the
    # chamber's x range; the step only appears outside the chamber's
    # x range, where it's a wall in the cavity right at the wet
    # flange's panel-seat face.
    def _above_slope(anchor_z, dy_rate):
        """Half-space above a slope plane anchored at
        (0, bulkhead_panel_y_range[0], anchor_z) with dz/dy = dy_rate."""
        plane = cq.Plane(
            origin=(0, bulkhead_panel_y_range[0], anchor_z),
            xDir=(1, 0, 0),
            normal=(0, dy_rate, 1),
        )
        return cq.Workplane(plane).rect(500, 500).extrude(500)

    above_slope = _above_slope(slope_low_z, slope_rate)
    above_dry_slope = _above_slope(floor_baseline_z, -slope_rate)

    # Split the wedge at the panel's −Y face.
    slope_region = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=bulkhead_panel_y_range[0])
        .rect(500, 500)
        .extrude(-500)
    )
    dry_region = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=bulkhead_panel_y_range[0])
        .rect(500, 500)
        .extrude(500)
    )

    # The wedge extrusion has to extend above the highest slope point
    # so the slope half-spaces cut a clean upper face on the wedge.
    # The dry slope tops out at floor_baseline_z + floor_slope_rise at
    # y=outer_y_max; +2 mm of margin keeps the slope cut well inside
    # the extrusion's Z range.
    wedge_top_z_safe = floor_baseline_z + floor_slope_rise + wedge_extrusion_z_margin
    wedge_extrusion = _build_envelope(
        side,
        (inner_z_range[0], wedge_top_z_safe),
        wall_offset=reservoir_wall_thickness,
    )
    wedge_slope = wedge_extrusion.intersect(slope_region).cut(above_slope)
    wedge_dry = wedge_extrusion.intersect(dry_region).cut(above_dry_slope)
    wedge = wedge_slope.union(wedge_dry)
    # Clip the wedge to the post-outer-fillet envelope, so the wedge's
    # sharp [-shape corner at (inner_corner_x, ±inner_y_max) doesn't
    # poke past the outer fillet arc and leave a sharp tab visible
    # from the centerward face in the wedge's z range.
    wedge = wedge.intersect(outer_envelope_filleted)
    body = body.union(wedge)

    port_x_signed = reservoir_bulkhead_port_x * side

    # Bulkhead pocket — horizontal cavity along +Y. Three logical
    # sections: stepped wet chamber (conforming to the bulkhead body's
    # release-ring / collet / flange profile), panel hole ([17.5 mm](BULKHEAD_PANEL_HOLE_D) through
    # the PETG annulus that the threading section clamps), and the
    # dry section (a slab only — see the slab cut below for why).
    # The annulus across bulkhead_panel_y_range IS the panel — flange
    # seats on its −Y face, locknut bears on its +Y face.
    def _y_pocket_cut(y_range, diameter):
        y_start, y_end = y_range
        return (
            WorldWorkplane(xz_plane_y_up)
            .workplane(offset=y_start)
            .center(port_x_signed, reservoir_bulkhead_port_z)
            .circle(diameter / 2)
            .extrude(y_end - y_start)
        )

    # Stepped wet chamber, conforming to the bulkhead body's profile.
    # First two sections are simple (cylinder lower-half + matching-width
    # box upper-half) "stadiums". The third section (against the panel)
    # is the nut pocket — handled separately below because it's stepped
    # (hex + washer counterbore), not a single cylinder.
    wet_sections = [
        (bulkhead_wet_y_range, bulkhead_release_chamber_diameter),  # antechamber + release ring
        (bulkhead_collet_y_range, bulkhead_collet_chamber_diameter),  # collet body — bulkhead's smooth main section rests here when fully screwed forward
    ]
    ceiling_z_top = floor_baseline_z + bulkhead_ceiling_overshoot_z
    for y_range, diameter in wet_sections:
        y_start, y_end = y_range
        body = body.cut(_y_pocket_cut(y_range, diameter))
        ceiling_box = (
            WorldWorkplane(xy_plane_z_up)
            .workplane(offset=reservoir_bulkhead_port_z)
            .center(port_x_signed, (y_start + y_end) / 2.0)
            .rect(diameter, y_end - y_start)
            .extrude(ceiling_z_top - reservoir_bulkhead_port_z)
        )
        body = body.cut(ceiling_box)

    # Curved exit from the wet collet chamber. The existing straight
    # ⌀11 half-cylinder dead-ends at y=bulkhead_wet_y_range[0] into
    # solid PETG, leaving the bulkhead's wet face only the radial
    # 0.5 mm-per-side gap around the collet and the stadium ceiling
    # box as flow paths to the cavity. Continue the cylinder past
    # there with a 90° quarter-arc swept tube of the same ⌀11,
    # joining tangentially (same axis along −Y, no step in cross-
    # section) and curving up through +Z over wet_exit_arc_radius
    # until the tube's axis is vertical.

    # Profile: ⌀11 circle in the plane perpendicular to the path's
    # initial tangent (which is world −Y), centered at the chamber's
    # −Y face on the bulkhead axis.
    wet_exit_profile = (
        WorldWorkplane(xz_plane_y_up)
        .workplane(offset=bulkhead_wet_y_range[0])
        .center(port_x_signed, reservoir_bulkhead_port_z)
        .circle(bulkhead_release_chamber_diameter / 2)
    )

    # Path: 90° arc in the world YZ plane at x=port_x_signed.
    #   Workplane local +x = world −Y (the direction of travel)
    #   Workplane normal   = world −X (chirality-flipped vs. natural +X
    #                        so local +y = world +Z, not −Z)
    #   Workplane local +y = world +Z (computed from normal × xDir)
    # Start at local (0, 0), end at local (R, R). Arc curves through
    # midpoint (R sin45°, R − R cos45°).
    wet_exit_path_plane = cq.Plane(
        origin=(port_x_signed, bulkhead_wet_y_range[0], reservoir_bulkhead_port_z),
        xDir=(0, -1, 0),
        normal=(-1, 0, 0),
    )
    r = wet_exit_arc_radius
    arc_mid = (r * math.sin(math.radians(45)),
               r * (1 - math.cos(math.radians(45))))
    arc_end = (r, r)
    wet_exit_path = (
        cq.Workplane(wet_exit_path_plane)
        .moveTo(0, 0)
        .threePointArc(arc_mid, arc_end)
    )

    wet_exit_tube = wet_exit_profile.sweep(wet_exit_path)
    body = body.cut(wet_exit_tube)

    # Nut cavity: third wet section. The bulkhead "nut" is a single
    # stepped washer+hex piece — hex portion at the −Y end gripped by
    # a flat-top hex pocket (⌀19.8 flat-to-flat + clearance) against
    # rotation, washer portion at the panel (+Y) end cleared by a
    # round counterbore (⌀22.1 + clearance). Install sequence: drop
    # the nut in from above (ceiling boxes open the cavity), gravity
    # seats it, hex flats prevent rotation. Then thread the bulkhead
    # in from the dry side; thread engagement locks the nut axially.
    # Anchored in Z to reservoir_bulkhead_nut_z (the floor's low point) so the
    # washer counterbore sits on top of the 4 mm reservoir floor,
    # preserving the full PETG fluid barrier below.
    nut_hex_y_range = (
        bulkhead_flange_y_range[0],
        bulkhead_flange_y_range[0] + bulkhead_nut_hex_depth,
    )
    nut_washer_y_range = (nut_hex_y_range[1], bulkhead_panel_y_range[0])

    nut_hex_part = (
        WorldWorkplane(xz_plane_y_up)
        .workplane(offset=nut_hex_y_range[0])
        .center(port_x_signed, reservoir_bulkhead_nut_z)
        .polyline(nut_hex_profile)
        .close()
        .extrude(nut_hex_y_range[1] - nut_hex_y_range[0])
    )
    nut_washer_part = (
        WorldWorkplane(xz_plane_y_up)
        .workplane(offset=nut_washer_y_range[0])
        .center(port_x_signed, reservoir_bulkhead_nut_z)
        .circle((bulkhead_nut_washer_diameter + 2 * bulkhead_nut_clearance) / 2)
        .extrude(nut_washer_y_range[1] - nut_washer_y_range[0])
    )
    nut_cavity = nut_hex_part.union(nut_washer_part)
    body = body.cut(nut_cavity)

    # Ceiling boxes — one per nut section (hex + washer) — that open
    # the nut cavity upward to the wet volume so the nut can be
    # dropped in before the cap is installed. Anchored to
    # `reservoir_bulkhead_nut_z` to stay co-centered with the nut cavity (NOT
    # the bulkhead axis, which sits 1 mm above).
    for (y_range, width) in (
        (nut_hex_y_range,
         bulkhead_nut_hex_corner_to_corner + 2 * bulkhead_nut_clearance),
        (nut_washer_y_range,
         bulkhead_nut_washer_diameter + 2 * bulkhead_nut_clearance),
    ):
        y_start, y_end = y_range
        nut_ceiling_box = (
            WorldWorkplane(xy_plane_z_up)
            .workplane(offset=reservoir_bulkhead_nut_z)
            .center(port_x_signed, (y_start + y_end) / 2.0)
            .rect(width, y_end - y_start)
            .extrude(ceiling_z_top - reservoir_bulkhead_nut_z)
        )
        body = body.cut(nut_ceiling_box)

    # Panel hole [17.5 mm](BULKHEAD_PANEL_HOLE_D) through the body.
    body = body.cut(_y_pocket_cut(bulkhead_panel_y_range, bulkhead_panel_hole_diameter))

    # TPU seal counterbores — one on each panel face. A flat printed
    # TPU washer seats in each counterbore; the mating face (nut
    # washer on the wet side, integral flange on the dry side) presses
    # on the exposed 0.6 mm of TPU until flush against the panel rim
    # outside the counterbore, giving 30% compression. Panel thickness
    # leaves ≥4 mm of PETG between the two counterbore floors.
    body = body.cut(_y_pocket_cut(
        (bulkhead_panel_y_range[0],
         bulkhead_panel_y_range[0] + bulkhead_seal_counterbore_depth),
        bulkhead_seal_counterbore_diameter,
    ))  # wet-side seal counterbore
    body = body.cut(_y_pocket_cut(
        (bulkhead_panel_y_range[1] - bulkhead_seal_counterbore_depth,
         bulkhead_panel_y_range[1]),
        bulkhead_seal_counterbore_diameter,
    ))  # dry-side seal counterbore
    # Wide-open dry section: instead of cutting a ⌀23 dry chamber + a
    # dry-floor box (the symmetric counterpart to the wet ceiling), the
    # dry section keeps ONLY a PETG ceiling slab spanning the entire
    # dry footprint (y=bulkhead_panel_y_range[1]..outer_y_max), with
    # the slab's top face on the same dry slope as the wedge above the
    # panel. Everything below the slab is removed — empty space all the
    # way down to the reservoir's outer floor and out through the side
    # walls in the dry y-range — giving a much larger opening than a
    # ⌀23 cylinder for fiddling with the locknut, collet, and tube
    # push-in from below. The slab is supported on its −Y edge by the
    # panel material at y=bulkhead_panel_y_range[1] and along its
    # perimeter by the +X / +Y wall material above slab_top.
    #
    # Slab is bulkhead_dry_slab_thickness (4 mm) thick — a fluid
    # barrier (cavity above holds syrup vapor + slosh), so it gets the
    # same 4 mm minimum as the body walls. It can only grow upward
    # because the bulkhead's dry-side ⌀22.9 flange occupies the z
    # range immediately below the slab; the upward growth is baked
    # into floor_baseline_z's offset above the chamber top.
    slab_bottom_plane = cq.Plane(
        origin=(0, bulkhead_panel_y_range[0], floor_baseline_z - bulkhead_dry_slab_thickness),
        xDir=(1, 0, 0),
        normal=(0, -slope_rate, 1),
    )
    below_slab = cq.Workplane(slab_bottom_plane).rect(500, 500).extrude(-500)
    dry_section_y = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=bulkhead_panel_y_range[1])
        .rect(500, 500)
        .extrude(500)
    )
    body = body.cut(below_slab.intersect(dry_section_y))

    # Fillet the new acute vertical edge at curve × panel-face.
    # The slab cut exposed the panel's +Y face for z < slab_bottom_z,
    # creating a new vertical edge where this face meets the centerward
    # curve. In XY projection the corner is acute (~49° interior angle
    # — sharper than a right angle, narrower than the curve × ±Y peaks
    # filleted earlier in this builder). The same reasons to fillet
    # apply: (a) it would print as a knife-edge tab on the FDM bed,
    # (b) it's a sharp protrusion sticking down into the dry section
    # right where the part is handled during install, (c) the inside
    # face of the protrusion (panel +Y face × curve face) makes a
    # narrow crevice for any leaked syrup to wick into. Same radius as
    # the curve × ±Y corners.
    new_corner_x_abs = math.sqrt(
        outer_centerward_radius**2 - bulkhead_panel_y_range[1]**2
    )
    slab_bottom_at_panel_face = (
        floor_baseline_z
        - bulkhead_dry_slab_thickness
        + slope_rate * (bulkhead_panel_y_range[1] - bulkhead_panel_y_range[0])
    )
    new_corner_z_mid = (outer_z_range[0] + slab_bottom_at_panel_face) / 2
    body = _fillet_edge_at(
        body,
        (side * new_corner_x_abs, bulkhead_panel_y_range[1], new_corner_z_mid),
        outer_corner_fillet_radius,
    )

    # Inner counterpart of the fillet above: round the analogous edge
    # on the cavity side of the panel, where the cavity-facing curve
    # (radius inner_centerward_radius) meets the wet nut seat face
    # (y = bulkhead_panel_y_range[0]). Same Z orientation, just on the
    # opposite face of the panel — exposed to syrup instead of dry-side
    # air. This corner sits inside the cavity above the wet wedge top
    # (z = slope_low_z) and below the cavity floor (z = floor_baseline_z);
    # without rounding it would be a narrow inner crevice the syrup
    # could pool against.
    inner_panel_corner_x_abs = math.sqrt(
        inner_centerward_radius**2 - bulkhead_panel_y_range[0]**2
    )
    inner_panel_corner_z_mid = (slope_low_z + floor_baseline_z) / 2
    body = _fillet_edge_at(
        body,
        (side * inner_panel_corner_x_abs, bulkhead_panel_y_range[0], inner_panel_corner_z_mid),
        inner_corner_fillet_radius,
    )

    # No well needed: with the wet ceiling open, syrup drains directly
    # from the cavity into the wet chamber and around the bulkhead
    # body's narrower wet-collet section, reaching the port at the
    # body's −Y face without any separate vertical channel.

    # No separate tube exit: the dry section is wide open from below,
    # +X, and +Y (all bounded only by the 4 mm slab + the perimeter
    # wall material above slab_top). After install, the bulkhead body
    # passes through the panel hole and its dry collet projects into
    # the open dry section; the tube push-in is unobstructed.

    # Level-sensing rod body anchor: a solid cylindrical boss rising
    # from the wet slope, with a blind bore cut into it from above —
    # bore stops rod_anchor_boss_floor mm short of the boss base so the
    # printed PETG floor inside the boss is what the rod tip bottoms
    # out on. The wet slope stays continuous and unbroken (no hole cut
    # through the slope into the wedge interior).
    #
    # Added LAST in build_reservoir_body, after every existing feature
    # (wedge, bulkhead pocket, slab cut, fillets), so the new boss
    # geometry cannot perturb any earlier edge/face selector.
    rod_x_signed = rod_position_x * side
    rod_slope_z_at_y = slope_low_z + slope_rate * (bulkhead_panel_y_range[0] - rod_position_y)
    rod_anchor_boss_cylinder = _z_cylinder(
        (rod_x_signed, rod_position_y),
        (rod_slope_z_at_y, rod_slope_z_at_y + rod_anchor_boss_height),
        rod_boss_od,
    )
    body = body.union(rod_anchor_boss_cylinder)

    # Blind bore: base rod_anchor_boss_floor mm above the slope, extruded up
    # through the top of the boss with a +0.1 overshoot so the cut
    # cleanly opens at the boss top face.
    bore_bottom_z = rod_slope_z_at_y + rod_anchor_boss_floor
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
            "BULKHEAD_PANEL_HOLE_D": 3,
        },
    )
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
