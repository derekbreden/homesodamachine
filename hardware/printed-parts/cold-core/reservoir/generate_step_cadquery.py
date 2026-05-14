import math
import sys
from pathlib import Path
import cadquery as cq

_here = Path(__file__).resolve().parent
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware")),
)
sys.path.insert(0, str(_here.parent))
from _cadq_export import export_step
from _foam_shell_geometry import (
    bag_pocket_far_inner_x as _shell_bag_pocket_far_inner_x,
    bag_pocket_z_inner_max as _shell_bag_pocket_z_inner_max,
    bag_pocket_floor_top_y as _shell_bag_pocket_floor_top_y,
    bag_pocket_walls_top_y as _shell_bag_pocket_walls_top_y,
    tank_copper_shell_radius as _shell_tank_copper_shell_radius,
    reservoir_clearance as _shell_reservoir_clearance,
    reservoir_floor_thickness as _shell_reservoir_floor_thickness,
    bulkhead_pocket_diameter as _shell_bulkhead_pocket_diameter,
    reservoir_bulkhead_port_x as _shell_reservoir_bulkhead_port_x,
    reservoir_bulkhead_port_y as _shell_reservoir_bulkhead_port_y,
)

# ═══════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════


# -------------------------------------------------------
# General
# -------------------------------------------------------
#
# Same coordinate convention as ../foam-shell/: +Y vertical, +X is
# the bag-pocket axis (two cavities sit on opposite sides), +Z is
# perpendicular to it.
xz_plane_y_up = cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, 1, 0))


def _wp_at(x, y, z):
    """A Workplane parallel to the xz plane at world point (x, y, z), normal
    +Y. Use this instead of ``cq.Workplane(xz_plane_y_up).workplane(origin=(x, y, z))``
    — the latter silently drops the Y component (which is along the
    plane's normal, not the in-plane direction), leaving every
    extrusion stuck at world Y=0."""
    return cq.Workplane(
        cq.Plane(origin=(x, y, z), xDir=(1, 0, 0), normal=(0, 1, 0))
    )
#
# -------------------------------------------------------


# -------------------------------------------------------
# Cavity envelope (mirrors as-built foam-shell inner-face values)
# -------------------------------------------------------
#
# These constants describe the bag-pocket cavity into which this
# reservoir fits. They are imported from ../_foam_shell_geometry.py (the
# shared foam-shell / foam-cap geometry module) so the reservoir cannot
# drift out of sync with wall_and_floor_thickness or any other shell
# input. Previously the values were hardcoded as a "stable interface,"
# which silently fell out of date when the shell walls were bumped from
# 1 mm to 2 mm — the reservoir's centerward face then overlapped the
# tank_copper_shell outer surface by 0.5 mm. Re-importing whenever the
# generator runs makes that class of bug impossible.
#
# Bag-pocket inner faces (the surfaces the reservoir must clear),
# at the current wall_and_floor_thickness = 2 mm:
#   - Far (away from tank): x = ±105.5 mm (sign flips with reservoir side)
#   - +Z / −Z side: z = ±70.5 mm
#   - Floor top: y = 2.0 mm
#   - Top of bag-pocket walls: y = 213.4 mm
#   - Centerward (toward tank): cylindrical surface, radius 72.5 mm,
#     vertical axis on +Y through origin — this is the tank_copper_shell
#     outer surface, which the reservoir's centerward face follows.
#
bag_pocket_far_inner_x = _shell_bag_pocket_far_inner_x
bag_pocket_z_inner_max = _shell_bag_pocket_z_inner_max
bag_pocket_floor_top_y = _shell_bag_pocket_floor_top_y
bag_pocket_walls_top_y = _shell_bag_pocket_walls_top_y
tank_copper_shell_outer_radius = _shell_tank_copper_shell_radius
#
# -------------------------------------------------------


# -------------------------------------------------------
# Reservoir geometry
# -------------------------------------------------------
#
# The body is an OPEN-TOP `[` cup: floor + four walls (far, +Z, −Z,
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
# Imported from the shared geometry module so the foam shell's
# bulkhead-pass-through hole and the reservoir's bulkhead pocket
# cannot drift apart on future wall-thickness changes. Wall and
# floor of the reservoir are the same 4 mm — `reservoir_floor_thickness`
# on the shell side names the dimension the foam-shell cares about
# (the PETG layer it leaves clearance above); reused locally for
# every wall in the reservoir body.
reservoir_wall_thickness = _shell_reservoir_floor_thickness
#
# Clearance between reservoir outer surfaces and bag-pocket inner
# faces on every face. Slack for sliding the printed reservoir into
# the cavity from above + FDM tolerance on both prints.
reservoir_clearance = _shell_reservoir_clearance
#
# -------------------------------------------------------


# -------------------------------------------------------
# Sharp-corner fillets (where the centerward curve meets the ±Z walls)
# -------------------------------------------------------
#
# At z = ±70 mm the outer centerward curve (radius 72 mm) meets the
# outer ±Z walls. Interior angle of the body's exterior at that point
# is only ~13° — a pointy tab that's structurally useless, won't FDM
# cleanly, and looks like a defect. Filleted off externally.
#
# At z = ±66 mm the inner centerward curve (radius 76 mm) meets the
# inner ±Z walls (cavity boundary). Interior angle of the cavity at
# that point is ~30° — a sharp corner inside the syrup volume that
# would trap residual liquid through clean cycles and concentrate
# stress in the wall. Filleted off internally.
#
# Same fillet radius on both for visual consistency. 6 mm is chosen
# to match body_boss_radius so the corner bosses (positions 4/5,
# centered on the outer fillet) fit fully inside the post-fillet
# wall material — see body_boss_radius below.
#
outer_corner_fillet_radius = 6.0
inner_corner_fillet_radius = 6.0
#
# -------------------------------------------------------


# -------------------------------------------------------
# Cap geometry
# -------------------------------------------------------
#
# Base plate (top, the flat surface) + perimeter wall (bottom, the
# "lip" hanging down around the gasket joint). The base plate hosts
# the counterbored screw heads on its flat top face; the perimeter
# wall provides depth for the screw shaft to pass through to the
# gasket + body insert below.
#
cap_base_thickness = 4.0                # = reservoir_wall_thickness; the cap's flat top is a fluid barrier (only the perimeter is gasket-sealed; the cavity interior reaches the cap base plate directly), so it carries the same 4 mm minimum as the body walls
cap_wall_height = 5.0
cap_wall_width = 6.0
#
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
#
# -------------------------------------------------------


# -------------------------------------------------------
# Gasket
# -------------------------------------------------------
#
# TPU 90A flat gasket that sits between the body wall top and the
# cap base plate bottom, compressed by the six M3 × 12 screws. Same
# material spec as the foam-shell cap gasket; printed flat at
# 2 mm thick.
#
# Geometry pattern, mirroring foam-cap-gasket:
#   - 5 mm-wide perimeter ring matching the body wall outer
#     footprint. The 4 mm-thick body wall is fully covered, plus
#     1 mm of the ring extends inward over the cavity opening for
#     print stability (a 4 mm-wide TPU strip alone is narrow enough
#     to warp during a TPU print).
#   - ø12 circular pads at each insert position. The pads extend
#     inward beyond the perimeter ring to give the screw clamp a
#     uniform compressed disk the same size as the body boss above
#     (and 0.25 mm wider than the cap boss below at ø11.5) — so each
#     screw seats squarely on TPU and the seal is uniform around every
#     hole rather than being a thin ring through the wall section and
#     a wide disk through the cavity-side pad.
#   - ø3.5 clearance holes through each pad for the screw shaft.
#
gasket_thickness = 2.0
gasket_strip_width = 5.0
gasket_pad_radius = 6.0  # ø12, matches body boss (insert_pocket_radius + 4); the gasket pad provides full compression contact under each cap boss / body boss face
#
# -------------------------------------------------------


# -------------------------------------------------------
# Vent feature
# -------------------------------------------------------
#
# A hydrophobic PTFE membrane filter sits in a cylindrical pocket at
# the top of the cap, held down by a press-fit TPU 90A retaining
# ring. Air vents through a small hole below the filter into a
# cylindrical shell that hangs into the reservoir. The cylinder has
# a closed floor at the bottom (in use) and four slots in its walls,
# so syrup that splashes upward hits the closed floor or the cylinder
# walls and has to take a 90°-turn path through a slot before it
# could reach the membrane above.
#
# Filter: LVDALAB ø13 PTFE-on-PET membrane (Amazon B0D41KT345)
# Retaining ring: 2 mm-thick TPU 90A, press-fit into the cap pocket
#
filter_diameter = 13.0
filter_thickness = 0.5
#
retaining_ring_thickness = 2.0
retaining_ring_outer_diameter = 13.4  # 0.1 mm interference per side vs the ø13.2 pocket, so the TPU 90A ring compresses in for a light press-fit
retaining_ring_inner_diameter = 9.0   # leaves most of the membrane exposed for airflow
#
# Filter pocket (cylindrical recess in the cap top) holds the
# filter + ring stack with 0.2 mm of slip-fit clearance.
vent_pocket_diameter = filter_diameter + 0.2                            # 13.2
vent_pocket_depth = filter_thickness + retaining_ring_thickness         # 2.5
#
# Below the pocket, the cap material is locally thicker than the
# standard base plate so the small vent hole has enough material
# around it to pass through cleanly before transitioning to the
# cylinder. This local thickening = "the boss" — it protrudes below
# the standard base plate bottom by (boss depth − base plate thickness).
vent_hole_diameter = 5.0
vent_below_pocket_material = 2.5  # cap material thickness between pocket bottom and boss bottom
vent_boss_wall_around_pocket = 2.0
vent_boss_outer_diameter = vent_pocket_diameter + 2 * vent_boss_wall_around_pocket  # 17.2
_vent_boss_depth = vent_pocket_depth + vent_below_pocket_material       # 5.0
_vent_boss_extension_below_base_plate = _vent_boss_depth - cap_base_thickness  # 1.0
#
# Cylinder shell hangs below the boss into the reservoir, with the
# same inside diameter as the vent hole so there's no internal step
# in the air column. The cylinder outer diameter matches the brim
# diameter (= a beefy 2.5 mm wall) so the brim is flush with the
# cylinder rather than overhanging it — the brim becomes the closed
# bottom of a single ø10 cylinder, and the cylinder→brim transition
# has no overhang to print during top-down FDM of the cap.
vent_cylinder_inner_diameter = vent_hole_diameter                       # 5
vent_cylinder_wall_thickness = 2.5
vent_cylinder_outer_diameter = vent_cylinder_inner_diameter + 2 * vent_cylinder_wall_thickness  # 10
vent_brim_thickness = 1.0
vent_brim_diameter = vent_cylinder_outer_diameter                       # 10 — matches cylinder outer
#
# Side slots cut through the cylinder walls — four rectangular
# windows at 0°/90°/180°/270°. Slot height equals the cylinder wall
# height (no margin above or below), so the wall in the slot zone is
# four angular ribs spanning between the brim below and the boss
# extension above.
vent_slot_count = 4
vent_slot_width = 3.0
vent_slot_height = 2.0
#
vent_cylinder_length = vent_slot_height + vent_brim_thickness           # 3
#
# Vent position on the cap, in the side=+1 frame. Centered between
# the z=0 and z=+65 rows of screw bosses (so the ø17 vent boss and
# its counterbore-sized pocket clear every screw counterbore and
# every cap-side boss), and inside the perimeter wall. Mirrored
# across x=0 for side=−1.
vent_position_x = 85.0
vent_position_z = 32.5
#
# -------------------------------------------------------


# -------------------------------------------------------
# Level-sensing strut
# -------------------------------------------------------
#
# A vertical solid PETG cylinder, body-anchored and cap-registered
# (NOT cap-cantilever). A small magnetic float slides up and down
# the strut as the syrup level changes; ten reed switches mounted
# outside the bag_pocket_shell's far +X wall (foam-encapsulated
# during the body foam pour) detect the float's position for level
# sensing. Same architecture as the carbonator's existing reed+float
# level sensing (see `hardware/future.md` "Level sensing"): rod
# anchored at one plate, registered at the other — just extended to
# 10 reeds per reservoir for finer granularity.
#
# Architecture:
#   - The strut is unioned into the BODY (build_reservoir_body),
#     extending UP from the wet-side wedge.
#   - The strut is anchored well INTO the wedge at the wet slope
#     top. The wedge is fully fused into the body's PETG mass,
#     giving a solid bond at the strut's bottom end.
#   - The strut top is captured by a slip-fit REGISTER POCKET cut
#     into the cap's base plate from below — 2 mm deep, 0.5 mm
#     radial clearance (ø5 pocket around the ø4 strut). The pocket
#     is a downward-opening blind hole, cap-local y = 5..7
#     (cap_wall_height .. cap_wall_height + STRUT_REGISTER_DEPTH).
#   - During assembly the cap is lowered onto the body and the
#     strut tip slides into the register as the cap seats on the
#     gasket. The strut is doubly anchored: floor-bonded at the
#     bottom, register-captured at the top.
#
# Position: at (x = ±STRUT_POSITION_X, z = STRUT_POSITION_Z) in the
# reservoir coordinate frame — x sign follows `side`; z stays
# negative for both sides (no z mirroring). Chosen to:
#   - sit OPPOSITE the bulkhead, which occupies z = 28..64 on the
#     +Z half of the reservoir. Placing the strut on the -Z half
#     puts the float in the wider, uncluttered part of the cavity
#     and removes any geometric coupling between the level-sensing
#     hardware and the outlet-bulkhead pocket.
#   - sit in a wider part of the cavity (~38 mm cavity width at
#     z=-45 vs only ~24 mm at z=0), giving generous clearance for
#     the donor donut float regardless of its precise OD/hole.
#   - keep clear of all screw bosses (#1/#4 at z=+64, #2/#5 at
#     z=-64, #3/#6 at z=0): strut at z=-45 is at least 19 mm from
#     the nearest boss on the -Z side.
#   - keep clear of the vent boss (centered at z=+32.5) and the
#     bulkhead pocket (z=28..64): strut at z=-45 is on the opposite
#     half of the cavity.
#
# STRUT_DIAMETER = 4 mm sits comfortably inside whatever sliding
# clearance the donor donut provides; the wider cavity at z=-45
# means precise hole-to-strut tolerance is no longer a critical
# fit question (vs. the original z=0 position where the cavity was
# only 24 mm wide and a tight float fit mattered more).
#
STRUT_POSITION_X = 88.0       # |x| of the strut centerline; mirrors with `side`
STRUT_POSITION_Z = -45.0      # z of the strut centerline (does NOT mirror with side); opposite the bulkhead's +Z half, in the wider part of the cavity
STRUT_DIAMETER = 4.0          # solid PETG cylinder OD; double-anchored so 4 mm is structurally adequate over the ~200 mm length
STRUT_BOTTOM_Y = 20.0         # reservoir-frame y of the strut's bottom end; the wet slope crests near y≈22.8 at z=-45, so the strut embeds ~2.8 mm into the wedge for a solid PETG bond
STRUT_REGISTER_DIAMETER = STRUT_DIAMETER + 1.0  # 5 mm — slip-fit pocket in the cap base plate, 0.5 mm radial clearance around the strut tip
STRUT_REGISTER_DEPTH = 2.0    # depth of the register pocket cut up into the cap base plate (cap-local y=5..7)
#
# -------------------------------------------------------


# -------------------------------------------------------
# Outlet bulkhead pocket + sloped floor
# -------------------------------------------------------
#
# Single outlet port: a John Guest PP1208E 1/4" black push-to-
# connect bulkhead union (Amazon B00JYFU8MM, NSF 51 + NSF 61, FDA-
# compliant) recessed ENTIRELY inside the reservoir's floor. Only
# the 1/4" OD tube travels through the foam channel — the bulkhead
# itself stays on the syrup side. The body geometry (catalog):
# ≈ ø22.9 mm flange/collet OD, ≈ 34.5 mm overall length, ⌀6.35 mm
# tube push-to-connect at each end.
#
# Geometry: the floor locally thickens into a chunky "boss" in the
# +X × +Z quadrant. The bulkhead lies horizontally inside this boss
# with its axis along +Z. The wet-collet tube port (⌀6.5 mm) opens
# out the boss's −Z face into the syrup volume; on the +Z side a
# ⌀6.5 mm cylindrical channel carries the 1/4" tube the rest of the
# way out through the reservoir's +Z outer wall, aligning with the
# foam-shell pass-through at (±port_position_x, port_position_y) — see
# `_foam_shell_geometry.py` `cut_circular_port_holes`. Both sides
# import `reservoir_bulkhead_port_x` and `reservoir_bulkhead_port_y`
# from `_foam_shell_geometry.py` (current values 88.0 and 18.0 at 2 mm
# shell wall), so the flange chamber's curved bottom sits exactly on
# top of the 4 mm outer floor (4 mm of PETG below the chamber as a
# fluid barrier) and the pocket's +X edge stays 1.5 mm clear of the
# cavity's inner +X face.
#
# Both reservoirs (side=+1 and side=−1) put the bulkhead on the +Z
# side; only x mirrors.
#
# Installation: the dry side of the pocket is wide-open below a 4 mm
# ceiling slab (see "Wide-open dry section" in build_reservoir_body),
# so the bulkhead body passes through the panel hole from below and
# the locknut + dry collet + 1/4" tube push-in are unobstructed. No
# print-pause-and-insert or split-boss assembly needed.
#
port_position_x = _shell_reservoir_bulkhead_port_x  # derived in _foam_shell_geometry.py from bag_pocket_far_inner_x − reservoir_clearance − reservoir_floor_thickness − bulkhead_pocket_diameter/2 − 1.5; 88.0 at the current 2 mm shell wall, leaving 1.5 mm of PETG between the pocket's +X edge and the cavity's inner +X face. The matching foam-shell pass-through hole reads the same constant, so the two cannot drift apart on future wall-thickness changes.
port_position_y = _shell_reservoir_bulkhead_port_y  # derived in _foam_shell_geometry.py; 18.0 at the current 2 mm shell wall, placing the flange chamber's curved bottom exactly on top of the 4 mm outer floor (4 mm of PETG below the chamber as a fluid barrier). The matching foam-shell pass-through hole reads the same constant, so the two cannot drift apart on future wall-thickness changes.
port_tube_diameter = 6.5                # 1/4" OD tube clearance
#
# The pocket is asymmetric across the panel. Wet side (z < panel):
# a STEPPED cavity conforming to the bulkhead body's release-ring →
# collet → flange profile, with each step's ceiling open to the
# cavity above so syrup drains around the body to the −Z port. Dry
# side (z > panel): wide-open below a 4 mm ceiling slab — no
# symmetric "dry chamber" — so the locknut, dry collet, and 1/4"
# tube push-in are unobstructed from below, +X, and +Z. The annulus
# of PETG between the wet chamber and the slab IS the panel the
# bulkhead clamps — its −Z face seats the flange and its +Z face is
# where the locknut bears.
#
# Section lengths along +Z are estimates from typical JG bulkhead-
# union proportions (catalog total length 34.5 mm; threading section
# 3–5 mm panel range). Adjust if a caliper measurement of the part
# in hand disagrees.
#
bulkhead_pocket_diameter = _shell_bulkhead_pocket_diameter  # 23.0 — ø22.9 flange + 0.1 clearance (snug fit). Imported from `_foam_shell_geometry.py` because that module derives `reservoir_bulkhead_port_y` (the Y of the foam-shell pass-through hole) from this diameter.
bulkhead_panel_hole_diameter = 17.0     # JG catalog spec for the 1/4" body family (0.67")
#
# The bulkhead body's wet side is *stepped* along its axis (flange,
# collet body, release ring — narrower toward the port). The chamber
# steps in matching sections so the syrup volume conforms to the body
# and the residual film below the port is small.
#
# Section lengths and diameters below are the first-pass values from a
# pixel-measured side view of the CI1208W (same body, white acetal),
# calibrated against the catalog 34.5 mm total length. See
# `hardware/off-the-shelf-parts/jg-bulkhead-union/extracted-results/
# geometry-description.md` for the full measurement table, confidence
# levels, and the raw images. Refine after a caliper pass on the
# PI1208S we already own; the workflow is documented in
# `tools/measure-from-drawings/README.md`.
#
bulkhead_wet_chamber_length = 12.0      # wet flange + collet body + release ring (catalog total length 34.5 ÷ split)
bulkhead_wet_antechamber_length = 2.0   # gap on the bulkhead's wet face — must exist or syrup can't reach the port
bulkhead_panel_thickness = 5.0          # = panel + threading section
bulkhead_dry_chamber_length = 17.0      # locknut + dry collet
bulkhead_pocket_length = (
    bulkhead_wet_chamber_length + bulkhead_panel_thickness + bulkhead_dry_chamber_length
)                                       # 34 (bulkhead body length, catalog ~34.5)
#
# Wet-side section lengths (estimates — refine with drawing measurements):
bulkhead_flange_length = 3.0                                   # last segment, against the panel
bulkhead_collet_body_length = 6.0                              # middle of the wet section
bulkhead_release_ring_length = (
    bulkhead_wet_chamber_length - bulkhead_flange_length - bulkhead_collet_body_length
)                                                              # 3 — the visible end with the push-to-release ring
#
# Wet-side chamber diameters per section (body OD + clearance):
bulkhead_flange_chamber_diameter = bulkhead_pocket_diameter    # 23 (ø22.9 flange + 0.1 clearance)
bulkhead_collet_chamber_diameter = 19.0                        # est. body OD ø17–18 + ~0.5 mm/side
bulkhead_release_chamber_diameter = 11.0                       # caliper-measured release ring ø9.57 + ~0.7 mm/side
#
bulkhead_wet_end_z = 30.0                # z of bulkhead body's wet face (the port)
bulkhead_wet_chamber_z_min = bulkhead_wet_end_z - bulkhead_wet_antechamber_length  # 28
bulkhead_release_z_start = bulkhead_wet_end_z                   # 30 — release-ring section starts at the body's wet face
bulkhead_collet_z_start = bulkhead_release_z_start + bulkhead_release_ring_length  # 33
bulkhead_flange_z_start = bulkhead_collet_z_start + bulkhead_collet_body_length    # 39
bulkhead_panel_z_min = bulkhead_flange_z_start + bulkhead_flange_length             # 42
bulkhead_panel_z_max = bulkhead_panel_z_min + bulkhead_panel_thickness              # 47
bulkhead_dry_end_z = bulkhead_wet_end_z + bulkhead_pocket_length                    # 64
# The floor thickens uniformly across the cavity to a baseline whose
# inner-top y sits just above the bulkhead pocket, so the bulkhead body
# is fully encased in PETG along the panel section. The slope rises ON
# TOP of this baseline — every point of the floor surface is at least
# `floor_baseline_y`, and rises by `floor_slope_rise` to the far −Z
# wall. Outer floor stays flat at y=1 for FDM printability.
#
# The wet chamber's CEILING (above y=port_position_y) is open to the
# cavity, and the dry chamber's FLOOR (below y=port_position_y) is open
# to the outside of the reservoir — both because the bulkhead body is
# only fully surrounded around y=port_position_y (the chamber's
# centerline), and the PETG above the wet body or below the dry body
# wasn't doing structural work for syrup containment.
#
# Syrup drains: cavity → wet ceiling opening → wet chamber (around the
# bulkhead's wet collet body) → port at body's −Z face. The bulkhead
# inlet is the lowest point the pump can drain to.
#
# Dry-section ceiling slab. The dry section's ONLY material in y is a
# slab whose top face is the dry slope and whose bottom face is 4 mm
# below that. The slab is a fluid barrier (syrup vapor and slosh sit
# in the cavity above it; if it cracks, syrup leaks into the dry
# section), so it carries the same 4 mm minimum as the body walls and
# the cap base plate. The slab's bottom is constrained from below by
# the bulkhead's dry-side flange (⌀22.9 OD, top at y=port_position_y +
# 11.45 = 28.45), so the slab can only grow upward — i.e. the cavity
# floor rises by the slab's thickness above the chamber top.
bulkhead_dry_slab_thickness = 4.0
#
# floor_baseline_y is anchored so the slab's bottom face at z =
# bulkhead_panel_z_min sits exactly on the chamber's curved top
# (y=port_position_y + bulkhead_pocket_diameter / 2). The slope tilts
# the slab bottom upward as z increases, so the bulkhead dry-flange
# clearance is positive everywhere in z ≥ bulkhead_panel_z_max.
floor_baseline_y = port_position_y + bulkhead_pocket_diameter / 2 + bulkhead_dry_slab_thickness  # 33.5 = chamber_top (29.5) + slab_thickness (4); the slab top sits this high at z = bulkhead_panel_z_min and the slope rises with z
#
# On the wet side (z < bulkhead_wet_end_z), the slope's lowest line is
# anchored at the bulkhead INLET MIDPOINT (port_position_y = y of the
# port's center) — about 15.5 mm below the dry-side baseline. That
# recovers ~90 mL of cavity volume across the slope region; functional
# drainage is unchanged (syrup at the slope drops straight into the
# wet chamber's open ceiling), the win is purely volume.
slope_low_y = port_position_y  # 18 — slope's lowest line at z = bulkhead_wet_end_z
#
port_inlet_bottom_y = port_position_y - port_tube_diameter / 2  # 14.75 — bottom edge of the wet-collet port
floor_slope_rise = 6.0  # mm above floor_baseline_y at the far −Z wall
#
# -------------------------------------------------------


# -------------------------------------------------------
# Heat-set insert + screw spec
# -------------------------------------------------------
#
# M3 ruthex-style brass heat-set inserts (same as foam-shell cap-
# stack joinery). Insert OD 4 mm × length 4 mm; pocket is 4 mm bore
# × 7 mm deep (4 mm insert + 3 mm relief). Screws: BNUOK M3 × 12 mm
# DIN 912 SHCS, black oxide 12.9 alloy (Amazon B0DJQGVK8S), same
# brand/finish as the M3 × 25 used on the foam-shell cap stack
# but the right length for the reservoir's thinner cap-stack geometry
# (under-head stack is 7 mm cap-plus-gasket vs ~19 mm there). With
# M3 × 12, the shaft seats 4 mm into the insert, runs another 1 mm
# into the pocket relief, and leaves 2 mm of slack between the shaft
# tip and the pocket floor.
#
insert_pocket_radius = 2.0
insert_pocket_depth = 7.0
#
# Boss radii — chosen so each through-hole has a 4 mm PETG annulus
# around it (matches the body-wall / floor / cap fluid-barrier minimum,
# since the boss wall around the pocket/clearance hole separates the
# cavity from the pocket interior):
#   Body insert pocket ø4 + 4 mm PETG → body boss ø12 (radius 6)
#   Cap clearance hole ø3.5 + 4 mm PETG → cap boss ø11.5 (radius 5.75)
#
body_boss_radius = insert_pocket_radius + 4.0                          # 6
cap_boss_radius = cap_clearance_hole_diameter / 2.0 + 4.0              # 5.75
#
# Body boss vertical layout (extruding downward from the wall top):
#   top 7 mm:  pocket (ø4 hole for heat-set insert + screw shaft)
#   below:     solid ø12 cylinder. Built extra-long (extending below
#              the intended boss-bottom y) and then cut with a flat
#              45° plane through the wall at that boss-bottom y, so
#              the wall side of the cylinder stays straight (and gets
#              fused into the wall) and the cavity side of the
#              cylinder gets sliced off at 45° — an FDM-printable
#              overhang anchored on the wall.
#
# Bosses 1/2/3/6 sit 2 mm inside the cavity from the wall's inner
# face. The 45° cut starts at the wall inner face / corner at
# y = boss_bottom_y, NOT at the boss center, so the kept material on
# the wall side reaches all the way down to that y. Bosses 4/5
# (curve × ±Z corner, at outer-fillet center) sit inside the post-
# fillet wall material and don't get a cut — the body-boss loop
# skips them. The outer fillet radius (6 mm) equals body_boss_radius
# so the corner-boss disks inscribe the fillet arc exactly.
boss_height = 13.0                                                     # 7 mm pocket + 6 mm of solid+cut
_cyl_extra_below_bottom = 5.0                                          # extra cylinder length to be sliced off by the cut
#
# Insert / screw positions, derived from the wall geometry so the body
# and cap bosses at each position fit fully inside the outer envelope
# (the larger of the two boss radii sets the inset).
#
# Outer envelope (body and cap share this footprint):
_outer_far_x_abs = bag_pocket_far_inner_x - reservoir_clearance        # 104
_outer_z_max = bag_pocket_z_inner_max - reservoir_clearance            # 70
_outer_centerward_radius = tank_copper_shell_outer_radius + reservoir_clearance  # 72
#
# Inset equals the larger boss radius so the boss outer edge just
# reaches the outer face at every position (no boss protrusion past
# the body / cap outer envelope, no overhang into the bag pocket
# clearance).
_screw_setback = max(body_boss_radius, cap_boss_radius)                # 6
#
# Positions 1/2 — inset 6 mm from outer +X face × outer ±Z face.
_corner_xz_x = _outer_far_x_abs - _screw_setback                       # 98
_corner_xz_z = _outer_z_max - _screw_setback                           # 64
#
# Position 3 — inset 6 mm from outer +X face, z = 0.
_far_mid_x = _outer_far_x_abs - _screw_setback                         # 98
#
# Position 6 — 6 mm outward from outer curve (radially), z = 0.
_curve_apex_x = _outer_centerward_radius + _screw_setback              # 78
#
# Positions 4/5 — corner of outer curve × outer ±Z face. The corner
# is filleted at outer_corner_fillet_radius (= 6 mm). The fillet
# center is the unique point that is 6 mm from BOTH the outer +Z
# face and the outer curve, measured along the shortest path. The
# ø12 body boss disk INSCRIBES the fillet arc (radius 6 = body
# boss radius), so at these positions the boss is a no-op subset of
# the post-fillet wall material — no cavity bump, no chamfer needed
# (the body-boss loop below skips the chamfer for these two positions
# explicitly, for code-reading clarity).
_corner_curve_z = _outer_z_max - outer_corner_fillet_radius             # 64
_corner_curve_R = _outer_centerward_radius + outer_corner_fillet_radius  # 78
_corner_curve_x = math.sqrt(_corner_curve_R**2 - _corner_curve_z**2)    # ~44.55
#
# (for the side=+1 reservoir; sign flips for −1)
INSERT_POSITIONS_FOR_SIDE_PLUS_1 = [
    (_corner_xz_x, _corner_xz_z),         # 1: +X × +Z outer corner
    (_corner_xz_x, -_corner_xz_z),        # 2: +X × −Z outer corner
    (_far_mid_x, 0.0),                    # 3: +X face midpoint
    (_corner_curve_x, _corner_curve_z),   # 4: curve × +Z outer corner (at outer fillet center)
    (_corner_curve_x, -_corner_curve_z),  # 5: curve × −Z outer corner (at outer fillet center)
    (_curve_apex_x, 0.0),                 # 6: curve apex
]
#
# For each body boss that needs the 45° flat cut at its bottom (i.e.,
# the four bosses whose disks extend into the cavity, not the two
# curve-corner bosses which sit inside the post-fillet wall), record
# the wall pivot point (the (x, z) on the wall's inner face from which
# the cut plane originates) and the unit direction in XZ from the boss
# center toward that pivot. The cut plane passes through (pivot_x,
# boss_bottom_y, pivot_z) and is tilted at 45° from horizontal, rising
# away from the wall — keep above, cut below.
#
# Values stored for side=+1; the x component is multiplied by `side`
# in the body-boss loop to mirror across x=0 for side=−1.
_FAR_WALL_INNER_X = _outer_far_x_abs - reservoir_wall_thickness        # 100
_PLUS_Z_WALL_INNER_Z = _outer_z_max - reservoir_wall_thickness         # 66
_CURVE_INNER_X_AT_Z0 = _outer_centerward_radius + reservoir_wall_thickness  # 76
_INV_SQRT2 = 1.0 / math.sqrt(2.0)
BODY_BOSS_CUT_INFO_FOR_SIDE_PLUS_1 = {
    # (boss_x, boss_z) → (pivot_x, pivot_z, wall_dir_x, wall_dir_z)
    #   wall_dir is a UNIT vector in XZ pointing from the boss center toward the wall pivot
    (_corner_xz_x, _corner_xz_z):
        (_FAR_WALL_INNER_X, _PLUS_Z_WALL_INNER_Z, _INV_SQRT2, _INV_SQRT2),    # 1
    (_corner_xz_x, -_corner_xz_z):
        (_FAR_WALL_INNER_X, -_PLUS_Z_WALL_INNER_Z, _INV_SQRT2, -_INV_SQRT2),  # 2
    (_far_mid_x, 0.0):
        (_FAR_WALL_INNER_X, 0.0, 1.0, 0.0),                                   # 3
    (_curve_apex_x, 0.0):
        (_CURVE_INNER_X_AT_Z0, 0.0, -1.0, 0.0),                               # 6
    # 4 and 5 deliberately absent — those bosses sit inside the
    # post-fillet wall material, no cavity overhang to slice.
}
#
# -------------------------------------------------------


# ═══════════════════════════════════════════════════════
# FEATURES
# ═══════════════════════════════════════════════════════


def _build_outer_envelope(side, outer_far_x_abs, outer_z_max, outer_centerward_radius, floor_y, height):
    """`[`-shape solid: rectangle on three sides + concave cylindrical
    cutout on the centerward side. Used for both reservoir-body and
    cap footprints."""
    rect = (
        _wp_at(side * outer_far_x_abs / 2, floor_y, 0)
        .rect(outer_far_x_abs, 2 * outer_z_max)
        .extrude(height)
    )
    cyl = (
        _wp_at(0, floor_y, 0)
        .circle(outer_centerward_radius)
        .extrude(height)
    )
    return rect.cut(cyl)


def build_reservoir_body(side=1):
    """
    Open-top `[`-shaped PETG body with 4 mm walls + 4 mm floor, sized
    to fit one side of the bag-pocket cavity with `reservoir_clearance`
    mm of slack on every outer face.

    Six insert bosses (one per `INSERT_POSITIONS_FOR_SIDE_PLUS_1`) are
    unioned at the top of the perimeter, each with an ø4 × 5 mm-deep
    heat-set-insert pocket drilled into the top face. The bosses
    locally thicken the wall to ø8 mm wide so the insert has 2 mm of
    PETG around it on all sides.

    side=+1 builds the +X reservoir; side=−1 builds the −X (mirrored
    across x = 0).
    """
    # Outer envelope dimensions.
    outer_far_x_abs = bag_pocket_far_inner_x - reservoir_clearance
    outer_z_max = bag_pocket_z_inner_max - reservoir_clearance
    outer_floor_bottom_y = bag_pocket_floor_top_y + reservoir_clearance
    outer_top_y = bag_pocket_walls_top_y - reservoir_clearance
    outer_centerward_radius = tank_copper_shell_outer_radius + reservoir_clearance
    outer_height = outer_top_y - outer_floor_bottom_y

    # Inner cavity dimensions. No ceiling — cavity extends all the way
    # to outer_top_y; the cap closes the top with a gasket between.
    W = reservoir_wall_thickness
    inner_far_x_abs = outer_far_x_abs - W
    inner_z_max = outer_z_max - W
    inner_floor_top_y = outer_floor_bottom_y + W
    inner_top_y = outer_top_y  # <- no ceiling
    inner_centerward_radius = outer_centerward_radius + W
    inner_height = inner_top_y - inner_floor_top_y

    outer_envelope = _build_outer_envelope(
        side, outer_far_x_abs, outer_z_max, outer_centerward_radius,
        outer_floor_bottom_y, outer_height,
    )
    inner_cavity = _build_outer_envelope(
        side, inner_far_x_abs, inner_z_max, inner_centerward_radius,
        inner_floor_top_y, inner_height,
    )

    body = outer_envelope.cut(inner_cavity)

    # Fillet the four sharp corners where the centerward concave curve
    # meets the ±Z walls — applied to the bare wall geometry BEFORE
    # unioning the insert bosses, because two of the inner corners
    # coincide with boss positions (37.68, ±66) and unioning a cylinder
    # there would replace the sharp edge with a curved boss-to-wall
    # transition that the fillet operation can't pick up.
    #
    # Exterior corners (outer perimeter, ~13° interior angle) are pointy
    # tabs. Interior corners (cavity boundary, ~30° interior angle) are
    # sharp inside the syrup volume. Both get rounded with the same
    # radius for visual consistency.
    outer_corner_x = math.sqrt(outer_centerward_radius**2 - outer_z_max**2)
    inner_corner_x = math.sqrt(inner_centerward_radius**2 - inner_z_max**2)
    y_mid_body = (outer_floor_bottom_y + outer_top_y) / 2

    for sharp_z in (outer_z_max, -outer_z_max):
        body = (
            body
            .edges(cq.NearestToPointSelector(
                (side * outer_corner_x, y_mid_body, sharp_z),
            ))
            .fillet(outer_corner_fillet_radius)
        )

    # +X × ±Z outer corners (90° corners between the +X face and the
    # ±Z faces). The original fillet pass skipped these — the curve ×
    # ±Z corners above were ~13° acute "pointy tabs" and so were the
    # priority. The +X × ±Z corners are the remaining unfilleted outer
    # corners on the perimeter; rounding them with the same 6 mm radius
    # cleans up the appliance's exterior. Bosses 1 and 2 sit at these
    # corners' fillet centers (the same _screw_setback = 6 = boss radius
    # trick used for bosses 4/5 — boss disk inscribes the fillet arc),
    # so the boss material is entirely inside the rounded wall and the
    # boss's 45° cavity-overhang cut still applies normally.
    for sharp_z in (outer_z_max, -outer_z_max):
        body = (
            body
            .edges(cq.NearestToPointSelector(
                (side * outer_far_x_abs, y_mid_body, sharp_z),
            ))
            .fillet(outer_corner_fillet_radius)
        )

    # Separately-filleted outer envelope, used below to clip the wedge
    # so the wedge's sharp [-shape corner at (inner_corner_x, ±inner_z_max)
    # can't poke through the outer fillet arc. (Without this clip, the
    # wedge restores the pre-fillet outer corner geometry in the wedge's
    # y range, leaving a sharp tab visible from the centerward face in a
    # narrow Y range matching the wedge's extent — the bug that
    # previously left a sharp protrusion under the slab cut area.)
    outer_envelope_filleted = _build_outer_envelope(
        side, outer_far_x_abs, outer_z_max, outer_centerward_radius,
        outer_floor_bottom_y, outer_height,
    )
    for sharp_z in (outer_z_max, -outer_z_max):
        outer_envelope_filleted = (
            outer_envelope_filleted
            .edges(cq.NearestToPointSelector(
                (side * outer_corner_x, y_mid_body, sharp_z),
            ))
            .fillet(outer_corner_fillet_radius)
        )
    # Match the +X × ±Z corner fillets above on the clipping envelope.
    for sharp_z in (outer_z_max, -outer_z_max):
        outer_envelope_filleted = (
            outer_envelope_filleted
            .edges(cq.NearestToPointSelector(
                (side * outer_far_x_abs, y_mid_body, sharp_z),
            ))
            .fillet(outer_corner_fillet_radius)
        )

    for sharp_z in (inner_z_max, -inner_z_max):
        body = (
            body
            .edges(cq.NearestToPointSelector(
                (side * inner_corner_x, y_mid_body, sharp_z),
            ))
            .fillet(inner_corner_fillet_radius)
        )

    # Inner counterpart of the +X × ±Z outer fillets above. Rounds the
    # cavity-side corner where the inner +X face (x=inner_far_x_abs)
    # meets the inner ±Z face (z=±inner_z_max). Same role as the inner
    # fillets at the curve × ±Z corners — smooths a sharp inner crevice
    # in the syrup volume above dry_slope_y where both inner faces are
    # exposed. Same 6 mm radius for visual consistency. Adds a small
    # amount of material into the cavity tip; volume cost is small
    # because the affected y range only extends from dry_slope_y up.
    for sharp_z in (inner_z_max, -inner_z_max):
        body = (
            body
            .edges(cq.NearestToPointSelector(
                (side * inner_far_x_abs, y_mid_body, sharp_z),
            ))
            .fillet(inner_corner_fillet_radius)
        )

    # Insert bosses at the top perimeter (unioned AFTER the fillets so
    # the bosses sit on top of the now-rounded corners cleanly).
    boss_bottom_y = outer_top_y - boss_height
    pocket_bottom_y = outer_top_y - insert_pocket_depth

    for (px, pz) in INSERT_POSITIONS_FOR_SIDE_PLUS_1:
        px_signed = px * side
        cut_info = BODY_BOSS_CUT_INFO_FOR_SIDE_PLUS_1.get((px, pz))

        # Build the boss cylinder. If this boss needs a 45° cut,
        # extend the cylinder _cyl_extra_below_bottom past the
        # intended boss bottom so the cut has material to slice
        # off; otherwise build it straight from the intended bottom.
        if cut_info is None:
            cyl_bottom_y = boss_bottom_y
        else:
            cyl_bottom_y = boss_bottom_y - _cyl_extra_below_bottom
        boss = (
            _wp_at(px_signed, cyl_bottom_y, pz)
            .circle(body_boss_radius)
            .extrude(outer_top_y - cyl_bottom_y)
        )

        if cut_info is not None:
            pivot_x, pivot_z, dir_x, dir_z = cut_info
            pivot_x_signed = pivot_x * side
            dir_x_signed = dir_x * side
            # Cut plane: passes through (pivot_x_signed, boss_bottom_y, pivot_z),
            # tilted 45° from horizontal with the high side toward the
            # wall (along (dir_x_signed, dir_z) in XZ). Plane normal
            # = (wall_dir_x, 1, wall_dir_z), magnitude sqrt(2), 45° from
            # vertical when wall_dir is unit in XZ. xDir is perpendicular
            # to normal in the XZ plane (so the workplane's Z axis is
            # the cut plane's "horizontal" axis).
            cut_plane = cq.Plane(
                origin=(pivot_x_signed, boss_bottom_y, pivot_z),
                xDir=(-dir_z, 0, dir_x_signed),
                normal=(dir_x_signed, 1, dir_z),
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

        pocket = (
            _wp_at(px_signed, pocket_bottom_y, pz)
            .circle(insert_pocket_radius)
            .extrude(insert_pocket_depth + 0.1)  # +0.1 to break the top surface cleanly
        )
        body = body.cut(pocket)

    # ─────────────────────────────────────────────────────
    # Thick sloped floor + bulkhead pocket + well + tube exit
    # ─────────────────────────────────────────────────────
    # Floor inner surface is piecewise across z, with the split at the
    # PANEL's −Z face (= where the wet flange seats and the actual
    # wet/dry boundary lives). Both slopes share the same rate
    # (floor_slope_rise / wet-slope z-distance), tilted in opposite
    # directions so they meet at the split.
    #
    #   z < bulkhead_panel_z_min (wet side): floor = wet slope plane,
    #       drains to slope_low_y at z=bulkhead_panel_z_min, rises
    #       floor_slope_rise mm to the far −Z wall.
    #   z ≥ bulkhead_panel_z_min (dry side): floor = dry slope plane,
    #       anchored at (z=bulkhead_panel_z_min, y=floor_baseline_y),
    #       rises at the same rate toward +Z. Stays ≥ floor_baseline_y
    #       across the dry chamber's z range so the 2 mm ceiling is
    #       preserved.
    #
    # The two planes meet at z=bulkhead_panel_z_min with a vertical
    # step from slope_low_y up to floor_baseline_y. The wet chamber's
    # open ceiling already removes material at that z within the
    # chamber's x range; the step only appears outside the chamber's
    # x range, where it's a wall in the cavity right at the wet
    # flange's panel-seat face.
    slope_z_distance = bulkhead_panel_z_min - (-inner_z_max)
    slope_rate = floor_slope_rise / slope_z_distance

    slope_plane = cq.Plane(
        origin=(0, slope_low_y, bulkhead_panel_z_min),
        xDir=(1, 0, 0),
        normal=(0, 1, slope_rate),
    )
    above_slope = cq.Workplane(slope_plane).rect(500, 500).extrude(500)

    dry_slope_plane = cq.Plane(
        origin=(0, floor_baseline_y, bulkhead_panel_z_min),
        xDir=(1, 0, 0),
        normal=(0, 1, -slope_rate),
    )
    above_dry_slope = cq.Workplane(dry_slope_plane).rect(500, 500).extrude(500)

    # Split the wedge at the panel's −Z face.
    slope_region = (
        cq.Workplane(cq.Plane(
            origin=(0, 0, bulkhead_panel_z_min),
            xDir=(1, 0, 0),
            normal=(0, 0, -1),
        ))
        .rect(500, 500).extrude(500)
    )
    dry_region = (
        cq.Workplane(cq.Plane(
            origin=(0, 0, bulkhead_panel_z_min),
            xDir=(1, 0, 0),
            normal=(0, 0, 1),
        ))
        .rect(500, 500).extrude(500)
    )

    wedge_top_y_safe = floor_baseline_y + floor_slope_rise + 2.0
    wedge_extrusion = _build_outer_envelope(
        side, inner_far_x_abs, inner_z_max, inner_centerward_radius,
        inner_floor_top_y, wedge_top_y_safe - inner_floor_top_y,
    )
    wedge_slope = wedge_extrusion.intersect(slope_region).cut(above_slope)
    wedge_dry = wedge_extrusion.intersect(dry_region).cut(above_dry_slope)
    wedge = wedge_slope.union(wedge_dry)
    # Clip the wedge to the post-outer-fillet envelope, so the wedge's
    # sharp [-shape corner at (inner_corner_x, ±inner_z_max) doesn't
    # poke past the outer fillet arc and leave a sharp tab visible
    # from the centerward face in the wedge's y range.
    wedge = wedge.intersect(outer_envelope_filleted)
    body = body.union(wedge)

    port_x_signed = port_position_x * side

    # Bulkhead pocket — horizontal cavity along +Z. Three logical
    # sections: stepped wet chamber (conforming to the bulkhead body's
    # release-ring / collet / flange profile), panel hole (⌀17 through
    # the PETG annulus that the threading section clamps), and the
    # dry section (a slab only — see the slab cut below for why).
    # The annulus between the wet and dry sections at
    # z=bulkhead_panel_z_min..z=bulkhead_panel_z_max IS the panel —
    # flange seats on its −Z face, locknut bears on its +Z face.
    def _z_pocket_cut(z_start, z_end, diameter):
        return (
            cq.Workplane(cq.Plane(
                origin=(port_x_signed, port_position_y, z_start),
                xDir=(1, 0, 0),
                normal=(0, 0, 1),
            ))
            .circle(diameter / 2)
            .extrude(z_end - z_start)
        )

    # Stepped wet chamber, conforming to the bulkhead body's profile.
    # Each section is a (cylinder lower-half + matching-width box
    # upper-half) "stadium" — cylinder gives a snug fit around the
    # body's lower half, box opens the upper half to the cavity above.
    wet_sections = [
        # (z_start,                                z_end,                    diameter)
        (bulkhead_wet_chamber_z_min,               bulkhead_collet_z_start,  bulkhead_release_chamber_diameter),  # release ring + antechamber
        (bulkhead_collet_z_start,                  bulkhead_flange_z_start,  bulkhead_collet_chamber_diameter),   # collet body
        (bulkhead_flange_z_start,                  bulkhead_panel_z_min,     bulkhead_flange_chamber_diameter),   # flange (against panel)
    ]
    ceiling_y_top = floor_baseline_y + 2.0
    for z_start, z_end, diameter in wet_sections:
        body = body.cut(_z_pocket_cut(z_start, z_end, diameter))
        ceiling_box = (
            _wp_at(
                port_x_signed,
                port_position_y,
                (z_start + z_end) / 2.0,
            )
            .rect(diameter, z_end - z_start)
            .extrude(ceiling_y_top - port_position_y)
        )
        body = body.cut(ceiling_box)
    body = body.cut(_z_pocket_cut(
        bulkhead_panel_z_min, bulkhead_panel_z_max, bulkhead_panel_hole_diameter,
    ))                                       # panel hole ⌀17
    # Wide-open dry section: instead of cutting a ⌀23 dry chamber + a
    # dry-floor box (the symmetric counterpart to the wet ceiling), the
    # dry section keeps ONLY a PETG ceiling slab spanning the entire
    # dry footprint (z=bulkhead_panel_z_max..outer_z_max), with the
    # slab's top face on the same dry slope as the wedge above the
    # panel. Everything below the slab is removed — empty space all the
    # way down to the reservoir's outer floor and out through the side
    # walls in the dry z-range — giving a much larger opening than a
    # ⌀23 cylinder for fiddling with the locknut, collet, and tube
    # push-in from below. The slab is supported on its −Z edge by the
    # panel material at z=bulkhead_panel_z_max and along its perimeter
    # by the +X / +Z wall material above slab_top.
    #
    # Slab is bulkhead_dry_slab_thickness (4 mm) thick — a fluid
    # barrier (cavity above holds syrup vapor + slosh), so it gets the
    # same 4 mm minimum as the body walls. It can only grow upward
    # because the bulkhead's dry-side ⌀22.9 flange occupies the y
    # range immediately below the slab; the upward growth is baked
    # into floor_baseline_y's offset above the chamber top.
    slab_bottom_plane = cq.Plane(
        origin=(0, floor_baseline_y - bulkhead_dry_slab_thickness, bulkhead_panel_z_min),
        xDir=(1, 0, 0),
        normal=(0, 1, -slope_rate),
    )
    below_slab = cq.Workplane(slab_bottom_plane).rect(500, 500).extrude(-500)
    dry_section_z = (
        cq.Workplane(cq.Plane(
            origin=(0, 0, bulkhead_panel_z_max),
            xDir=(1, 0, 0),
            normal=(0, 0, 1),
        ))
        .rect(500, 500)
        .extrude(500)
    )
    body = body.cut(below_slab.intersect(dry_section_z))

    # Fillet the new acute vertical edge at curve × panel-face.
    # The slab cut exposed the panel's +Z face for y < slab_bottom_y,
    # creating a new vertical edge where this face meets the centerward
    # curve. In XZ projection the corner is acute (~49° interior angle
    # — sharper than a right angle, narrower than the original peaks at
    # curve × ±Z which were already filleted). Same reasons to fillet
    # apply: (a) it would print as a knife-edge tab on the FDM bed,
    # (b) it's a sharp protrusion sticking down into the dry section
    # right where the part is handled during install, (c) the inside
    # face of the protrusion (panel +Z face × curve face) makes a
    # narrow crevice for any leaked syrup to wick into. Same radius as
    # the original ± Z curve corners.
    new_corner_x_abs = math.sqrt(
        outer_centerward_radius**2 - bulkhead_panel_z_max**2
    )
    slab_bottom_at_panel_face = (
        floor_baseline_y
        - bulkhead_dry_slab_thickness
        + slope_rate * (bulkhead_panel_z_max - bulkhead_panel_z_min)
    )
    new_corner_y_mid = (outer_floor_bottom_y + slab_bottom_at_panel_face) / 2
    body = (
        body
        .edges(cq.NearestToPointSelector(
            (side * new_corner_x_abs, new_corner_y_mid, bulkhead_panel_z_max),
        ))
        .fillet(outer_corner_fillet_radius)
    )

    # Inner counterpart of the fillet above: round the analogous edge
    # on the cavity side of the panel, where the cavity-facing curve
    # (radius inner_centerward_radius) meets the wet flange seat face
    # (z = bulkhead_panel_z_min). Same Y orientation, just on the
    # opposite face of the panel — exposed to syrup instead of dry-side
    # air. This corner sits inside the cavity above the wet wedge top
    # (y = slope_low_y) and below the cavity floor (y = floor_baseline_y);
    # without rounding it would be a narrow inner crevice the syrup
    # could pool against.
    inner_panel_corner_x_abs = math.sqrt(
        inner_centerward_radius**2 - bulkhead_panel_z_min**2
    )
    inner_panel_corner_y_mid = (slope_low_y + floor_baseline_y) / 2
    body = (
        body
        .edges(cq.NearestToPointSelector(
            (side * inner_panel_corner_x_abs, inner_panel_corner_y_mid, bulkhead_panel_z_min),
        ))
        .fillet(inner_corner_fillet_radius)
    )

    # No well needed: with the wet ceiling open, syrup drains directly
    # from the cavity into the wet chamber and around the bulkhead
    # body's narrower wet-collet section, reaching the port at the
    # body's −Z face without any separate vertical channel.

    # No separate tube exit: the dry section is wide open from below,
    # +X, and +Z (all bounded only by the 4 mm slab + the perimeter
    # wall material above slab_top). After install, the bulkhead body
    # passes through the panel hole and its dry collet projects into
    # the open dry section; the tube push-in is unobstructed.

    # ─────────────────────────────────────────────────────
    # Level-sensing strut (body-anchored, cap-registered)
    # ─────────────────────────────────────────────────────
    # Vertical solid PETG cylinder extending UP from the wet-side
    # wedge into the cavity, acting as a guide rod for a magnetic
    # float that rides up and down with the syrup level. The top
    # end is captured by a slip-fit register pocket in the cap's
    # base plate (cut in build_reservoir_cap).
    #
    # The strut bottom sits at reservoir y=STRUT_BOTTOM_Y (20.0),
    # which is ~0.3 mm BELOW the wet slope's max at z=0 (slope
    # crests near y≈20.3 at z=0), so the strut embeds into the
    # solid wedge PETG for a structural bond at the bottom.
    #
    # The strut top reaches the body wall top (outer_top_y) — the
    # same level the gasket bottom sits on. No further. The cap's
    # boss (built in build_reservoir_cap) engages the strut top from
    # above.
    #
    # Added LAST in build_reservoir_body, after every existing
    # feature (wedge, bulkhead pocket, slab cut, fillets), so the
    # new cylinder geometry cannot perturb any earlier edge/face
    # selector.
    strut_x_signed = STRUT_POSITION_X * side
    strut_top_y = outer_top_y
    strut = (
        _wp_at(strut_x_signed, STRUT_BOTTOM_Y, STRUT_POSITION_Z)
        .circle(STRUT_DIAMETER / 2.0)
        .extrude(strut_top_y - STRUT_BOTTOM_Y)
    )
    body = body.union(strut)

    return body


def build_reservoir_cap(side=1):
    """
    PETG cap that sits on top of the reservoir body through a 2 mm TPU
    gasket.

    Orientation: the cap is a flat lid with a downward-hanging rim.
    The flat top face (the 4 mm base plate) is what the user sees
    from above, and is the surface the counterbored screw heads sit
    flush in. The 5 mm-tall × 6 mm-wide perimeter wall ("lip") hangs
    DOWN from the base plate around the gasket joint.

    In cap-local coordinates:
      - y = 0 .. 5  : perimeter wall (the downward-hanging rim)
      - y = 5 .. 9  : base plate (the flat top, full `[` footprint)
      - y = 9       : top face of the cap (the surface the screw
                      heads recess into; faces up / toward the user)

    To visualize the assembled stack, translate the cap up by
    (reservoir wall top y + gasket thickness) ≈ 214.9 mm. The
    perimeter-wall bottom face (cap y=0) lands at body y=214.9, the
    cap's top face (cap y=9) at body y=223.9.

    Six counterbored M3 holes pass through the cap at the same XZ
    positions as the body's insert bosses. ø6 × 4 mm counterbore on
    the top face recesses the M3 SHCS head flush in the base plate
    (head is ~3 mm, leaving ~1 mm of empty clearance above it);
    ø3.5 clearance hole continues through the rest of the cap.
    Six cap-side bosses mirror the body bosses inside the perimeter
    wall, providing additional PETG around the clearance hole and a
    matching cross-section for the gasket compression at each screw.
    """
    # Same outer footprint as the reservoir body.
    outer_far_x_abs = bag_pocket_far_inner_x - reservoir_clearance
    outer_z_max = bag_pocket_z_inner_max - reservoir_clearance
    outer_centerward_radius = tank_copper_shell_outer_radius + reservoir_clearance

    # Perimeter wall inner footprint (offset inward by cap_wall_width).
    inner_far_x_abs = outer_far_x_abs - cap_wall_width
    inner_z_max = outer_z_max - cap_wall_width
    inner_centerward_radius = outer_centerward_radius + cap_wall_width

    # Perimeter wall (outer − inner footprint, 5 mm tall) at the BOTTOM
    # of the cap, y = [0, 5]. The "lip" that hangs down around the gasket.
    perimeter_outer = _build_outer_envelope(
        side, outer_far_x_abs, outer_z_max, outer_centerward_radius,
        0.0, cap_wall_height,
    )
    perimeter_inner = _build_outer_envelope(
        side, inner_far_x_abs, inner_z_max, inner_centerward_radius,
        0.0, cap_wall_height,
    )
    perimeter_wall = perimeter_outer.cut(perimeter_inner)

    # Base plate (full footprint, 3 mm thick) at the TOP of the cap,
    # y = [5, 8]. The flat surface the user sees from above; hosts the
    # counterbores for the screw heads.
    base = _build_outer_envelope(
        side, outer_far_x_abs, outer_z_max, outer_centerward_radius,
        cap_wall_height, cap_base_thickness,
    )

    cap = base.union(perimeter_wall)

    cap_total_height = cap_base_thickness + cap_wall_height

    # Fillet the two exterior sharp corners (same outer footprint as
    # the body, so same sharp tabs). Done BEFORE the bosses are
    # unioned because the corner bosses (4/5) sit exactly at the
    # outer-fillet center, where the boss disk's outer edge IS the
    # fillet arc — unioning them first leaves no sharp corner edge
    # for the fillet selector to find, and CadQuery silently produces
    # malformed geometry (a leftover triangular tab where the corner
    # tip should have been rounded off). Filleting first, then
    # unioning the boss, leaves the fillet correct; the corner
    # bosses become a no-op there (the perimeter wall already covers
    # the boss-disk footprint inside the fillet arc), and the bosses
    # at the other four positions union normally.
    outer_corner_x = math.sqrt(outer_centerward_radius**2 - outer_z_max**2)
    y_mid_cap = cap_total_height / 2

    for sharp_z in (outer_z_max, -outer_z_max):
        cap = (
            cap
            .edges(cq.NearestToPointSelector(
                (side * outer_corner_x, y_mid_cap, sharp_z),
            ))
            .fillet(outer_corner_fillet_radius)
        )

    # Match the body's +X × ±Z corner fillets so the cap and body
    # share the same outer envelope (gasket between them sees the
    # same footprint on both sides).
    for sharp_z in (outer_z_max, -outer_z_max):
        cap = (
            cap
            .edges(cq.NearestToPointSelector(
                (side * outer_far_x_abs, y_mid_cap, sharp_z),
            ))
            .fillet(outer_corner_fillet_radius)
        )

    # Cap-side bosses at each insert position, mirroring the body
    # bosses. They sit inside the perimeter wall at y = [0, 5],
    # locally thickening the wall inward and providing extra PETG
    # around the clearance hole. Matching cross-sections on body and
    # cap also give the gasket a consistent bearing surface at each
    # screw position.
    for (px, pz) in INSERT_POSITIONS_FOR_SIDE_PLUS_1:
        px_signed = px * side
        boss = (
            _wp_at(px_signed, 0.0, pz)
            .circle(cap_boss_radius)
            .extrude(cap_wall_height)
        )
        cap = cap.union(boss)

    # Counterbored screw holes. The counterbore recesses the M3 SHCS
    # head 3 mm into the base plate (y = [5, 8.1], opening at the cap's
    # top face); the ø3.5 clearance hole continues through the rest of
    # the cap so the screw shaft can pass through the perimeter wall,
    # gasket, and into the body's insert pocket below.
    for (px, pz) in INSERT_POSITIONS_FOR_SIDE_PLUS_1:
        px_signed = px * side
        clearance = (
            _wp_at(px_signed, -0.1, pz)
            .circle(cap_clearance_hole_diameter / 2)
            .extrude(cap_total_height + 0.2)
        )
        cap = cap.cut(clearance)

        counterbore = (
            _wp_at(
                px_signed, cap_total_height - cap_counterbore_depth, pz,
            )
            .circle(cap_counterbore_diameter / 2)
            .extrude(cap_counterbore_depth + 0.1)
        )
        cap = cap.cut(counterbore)

    # ─────────────────────────────────────────────────────
    # Vent feature
    # ─────────────────────────────────────────────────────
    # Cap-local y, top→bottom (with cap_base_thickness=4, cap_wall_height=5,
    # cap_total_height=9; base plate spans y=5..9, perimeter wall y=0..5):
    #   y=9 .. 6.5  filter pocket (ø13.2, holds filter + retaining ring)
    #   y=6.5 .. 5  remaining 1.5 mm of base plate, vent hole ø5 through it
    #   y=5 .. 4    boss extension below base plate (ø17 outer), vent hole continues
    #   y=4 .. 2    cylinder shell (ø10 outer, ø5 inner) — wall is entirely slot zone
    #   y=4 .. 2    four side slots cut through the cylinder walls (full wall height)
    #   y=2 .. 1    closed brim (ø10) — same OD as the cylinder, no overhang
    vent_x_signed = vent_position_x * side

    boss_bottom_y = cap_total_height - _vent_boss_depth                # 4
    cylinder_walls_bottom_y = boss_bottom_y - (
        vent_cylinder_length - vent_brim_thickness
    )                                                                   # 2
    brim_bottom_y = cylinder_walls_bottom_y - vent_brim_thickness       # 1
    pocket_bottom_y = cap_total_height - vent_pocket_depth              # 6.5

    # Solid pieces: boss extension, cylinder body (cut hollow later),
    # brim. All unioned with the cap so the air-column cut below
    # carves a single continuous channel through them.
    boss_extension = (
        _wp_at(vent_x_signed, boss_bottom_y, vent_position_z)
        .circle(vent_boss_outer_diameter / 2.0)
        .extrude(_vent_boss_extension_below_base_plate)
    )
    cap = cap.union(boss_extension)

    cylinder_solid = (
        _wp_at(vent_x_signed, cylinder_walls_bottom_y, vent_position_z)
        .circle(vent_cylinder_outer_diameter / 2.0)
        .extrude(vent_cylinder_length - vent_brim_thickness)
    )
    cap = cap.union(cylinder_solid)

    brim = (
        _wp_at(vent_x_signed, brim_bottom_y, vent_position_z)
        .circle(vent_brim_diameter / 2.0)
        .extrude(vent_brim_thickness)
    )
    cap = cap.union(brim)

    # Cut filter pocket from the cap top face.
    pocket = (
        _wp_at(vent_x_signed, pocket_bottom_y, vent_position_z)
        .circle(vent_pocket_diameter / 2.0)
        .extrude(vent_pocket_depth + 0.1)  # +0.1 breaks the cap top surface cleanly
    )
    cap = cap.cut(pocket)

    # Cut the air column: ø5 from the cylinder bottom (top of brim) up
    # to the pocket bottom. This both hollows out the cylinder body we
    # just unioned in and drills the small vent hole through the boss
    # and the 0.5 mm of base plate below the pocket.
    air_column = (
        _wp_at(vent_x_signed, cylinder_walls_bottom_y, vent_position_z)
        .circle(vent_hole_diameter / 2.0)
        .extrude(pocket_bottom_y - cylinder_walls_bottom_y)
    )
    cap = cap.cut(air_column)

    # Side slots — four rectangular windows through the cylinder wall,
    # spaced 90° apart. Slot fills the cylinder wall top to bottom:
    # slot bottom = brim top, slot top = boss extension bottom. The
    # boss above and the brim below carry the load across the slot.
    slot_center_y = cylinder_walls_bottom_y + vent_slot_height / 2.0
    for i in range(vent_slot_count):
        theta = 2.0 * math.pi * i / vent_slot_count
        slot_x = vent_x_signed + (vent_cylinder_outer_diameter / 2.0) * math.cos(theta)
        slot_z = vent_position_z + (vent_cylinder_outer_diameter / 2.0) * math.sin(theta)
        tangent = (-math.sin(theta), 0.0, math.cos(theta))
        radial = (math.cos(theta), 0.0, math.sin(theta))
        slot_cut = (
            cq.Workplane(cq.Plane(
                origin=(slot_x, slot_center_y, slot_z),
                xDir=tangent,
                normal=radial,
            ))
            .rect(vent_slot_width, vent_slot_height)
            .extrude(-(vent_cylinder_wall_thickness + 1.0))
        )
        cap = cap.cut(slot_cut)

    # ─────────────────────────────────────────────────────
    # Level-sensing strut register pocket
    # ─────────────────────────────────────────────────────
    # The strut itself is unioned into the BODY (see build_reservoir_body),
    # extending up from the wet-side wedge. The strut's TOP end is
    # captured here by a slip-fit blind pocket cut into the cap's
    # base plate from below — opens at the cap's bottom face (cap-
    # local y = cap_wall_height = 5) and extends upward into the
    # base plate by STRUT_REGISTER_DEPTH (cap-local y = 5..7).
    # STRUT_REGISTER_DIAMETER = STRUT_DIAMETER + 1.0 → 5 mm pocket
    # around the 4 mm strut → 0.5 mm radial clearance for a slip
    # fit. During assembly the cap is lowered onto the body and the
    # strut tip slides into this register as the cap seats on the
    # gasket. See the "Level-sensing strut" constants block for
    # the full architecture rationale.
    #
    # Cut LAST in build_reservoir_cap, after every existing feature
    # (vent boss, screw bosses, counterbores), so the new pocket
    # cannot perturb any earlier edge/face selector.
    strut_x_signed = STRUT_POSITION_X * side
    register_pocket = (
        _wp_at(strut_x_signed, cap_wall_height - 0.1, STRUT_POSITION_Z)
        .circle(STRUT_REGISTER_DIAMETER / 2.0)
        .extrude(STRUT_REGISTER_DEPTH + 0.1)  # +0.1 breaks the cap's bottom face cleanly
    )
    cap = cap.cut(register_pocket)

    return cap


def build_reservoir_gasket(side=1):
    """
    Flat TPU 90A gasket between the reservoir body wall top and the
    cap base plate bottom. 2 mm thick, exported in its own coordinate
    space (y = 0 .. 2). To visualize the assembled stack, translate
    up by the reservoir wall top y = 211.9 mm.

    Same `[`-shape outer footprint as the body and cap (with the
    outer-corner fillet at the curve × ±Z corners). Inner edge of
    the perimeter ring is `gasket_strip_width` inward of the outer
    edge — 5 mm-wide ring covers the 4 mm-thick body wall fully plus
    1 mm extending inward over the cavity opening.

    At each of the six insert positions, an ø8 pad extends inward
    beyond the ring so the screw clamp compresses a uniform disk of
    TPU (matching the body boss footprint), with an ø3.5 hole through
    its center for the screw shaft.

    side=+1 builds the +X gasket; side=−1 builds the −X (mirror).
    """
    outer_far_x_abs = bag_pocket_far_inner_x - reservoir_clearance
    outer_z_max = bag_pocket_z_inner_max - reservoir_clearance
    outer_centerward_radius = tank_copper_shell_outer_radius + reservoir_clearance

    inner_far_x_abs = outer_far_x_abs - gasket_strip_width
    inner_z_max = outer_z_max - gasket_strip_width
    inner_centerward_radius = outer_centerward_radius + gasket_strip_width

    outer = _build_outer_envelope(
        side, outer_far_x_abs, outer_z_max, outer_centerward_radius,
        0.0, gasket_thickness,
    )
    inner = _build_outer_envelope(
        side, inner_far_x_abs, inner_z_max, inner_centerward_radius,
        0.0, gasket_thickness,
    )
    gasket = outer.cut(inner)

    # Outer fillet at the curve × ±Z corners (matches the body/cap
    # outer profile so the gasket aligns flush with both above and
    # below it when clamped).
    outer_corner_x = math.sqrt(outer_centerward_radius**2 - outer_z_max**2)
    y_mid_gasket = gasket_thickness / 2.0
    for sharp_z in (outer_z_max, -outer_z_max):
        gasket = (
            gasket
            .edges(cq.NearestToPointSelector(
                (side * outer_corner_x, y_mid_gasket, sharp_z),
            ))
            .fillet(outer_corner_fillet_radius)
        )

    # Match the body/cap +X × ±Z corner fillets.
    for sharp_z in (outer_z_max, -outer_z_max):
        gasket = (
            gasket
            .edges(cq.NearestToPointSelector(
                (side * outer_far_x_abs, y_mid_gasket, sharp_z),
            ))
            .fillet(outer_corner_fillet_radius)
        )

    # Pads at every insert position — unioned BEFORE the holes are
    # cut so each hole sits at the center of a full ø8 disk.
    for (px, pz) in INSERT_POSITIONS_FOR_SIDE_PLUS_1:
        px_signed = px * side
        pad = (
            _wp_at(px_signed, 0.0, pz)
            .circle(gasket_pad_radius)
            .extrude(gasket_thickness)
        )
        gasket = gasket.union(pad)

    # Screw clearance holes.
    for (px, pz) in INSERT_POSITIONS_FOR_SIDE_PLUS_1:
        px_signed = px * side
        hole = (
            _wp_at(px_signed, -0.1, pz)
            .circle(cap_clearance_hole_diameter / 2.0)
            .extrude(gasket_thickness + 0.2)
        )
        gasket = gasket.cut(hole)

    return gasket


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
        cq.Workplane(xz_plane_y_up)
        .circle(retaining_ring_outer_diameter / 2.0)
        .circle(retaining_ring_inner_diameter / 2.0)
        .extrude(retaining_ring_thickness)
    )


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════


def main():
    body = build_reservoir_body(side=1)
    cap = build_reservoir_cap(side=1)
    gasket = build_reservoir_gasket(side=1)
    retaining_ring = build_reservoir_retaining_ring()

    here = Path(__file__).resolve().parent
    export_step(body, str(here / "reservoir.step"))
    export_step(cap, str(here / "reservoir-cap.step"))
    export_step(gasket, str(here / "reservoir-gasket.step"))
    export_step(retaining_ring, str(here / "reservoir-retaining-ring.step"))
    print(f"-> reservoir.step")
    print(f"-> reservoir-cap.step")
    print(f"-> reservoir-gasket.step")
    print(f"-> reservoir-retaining-ring.step")


if __name__ == "__main__":
    main()
