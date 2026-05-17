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
from _cold_core_interface import (
    bag_pocket_far_inner_x as _shell_bag_pocket_far_inner_x,
    bag_pocket_z_inner_max as _shell_bag_pocket_z_inner_max,
    bag_pocket_floor_top_y as _shell_bag_pocket_floor_top_y,
    bag_pocket_walls_top_y as _shell_bag_pocket_walls_top_y,
    pocket_centerward_arc_outer_radius as _shell_pocket_centerward_arc_outer_radius,
    reservoir_clearance as _shell_reservoir_clearance,
    reservoir_floor_thickness as _shell_reservoir_floor_thickness,
    bulkhead_pocket_diameter as _shell_bulkhead_pocket_diameter,
    reservoir_bulkhead_port_x as _shell_reservoir_bulkhead_port_x,
    reservoir_bulkhead_port_y as _shell_reservoir_bulkhead_port_y,
    reservoir_bulkhead_nut_y as _shell_reservoir_bulkhead_nut_y,
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
# reservoir fits. They are imported from ../_cold_core_interface.py so
# the reservoir cannot drift out of sync with wall_and_floor_thickness
# or any other shell input. Previously the values were hardcoded as a
# "stable interface," which silently fell out of date when the shell
# walls were bumped from 1 mm to 2 mm — the reservoir's centerward
# face then overlapped the pocket's centerward arc cavity face by
# 0.5 mm. Re-importing whenever the generator runs makes that class
# of bug impossible.
#
# Bag-pocket inner faces (the surfaces the reservoir must clear),
# at the current wall_and_floor_thickness = 2 mm:
#   - Far (away from cold-core axis): x = ±105.5 mm (sign flips with reservoir side)
#   - +Z / −Z side: z = ±70.5 mm
#   - Floor top: y = 2.0 mm
#   - Top of bag-pocket walls: y = 213.4 mm
#   - Centerward (toward cold-core axis): cylindrical surface of
#     radius 72.5 mm centered on the cold-core axis — this is the
#     pocket centerward wall's cavity-side face, which the reservoir's
#     centerward face follows.
#
bag_pocket_far_inner_x = _shell_bag_pocket_far_inner_x
bag_pocket_z_inner_max = _shell_bag_pocket_z_inner_max
bag_pocket_floor_top_y = _shell_bag_pocket_floor_top_y
bag_pocket_walls_top_y = _shell_bag_pocket_walls_top_y
pocket_centerward_arc_outer_radius = _shell_pocket_centerward_arc_outer_radius
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
vent_position_x = 96.0
vent_position_z = 32.5
#
# -------------------------------------------------------


# -------------------------------------------------------
# Level-sensing rod (1/8" × 12" 316 stainless steel)
# -------------------------------------------------------
#
# A vertical 3.175 mm (1/8") × 305 mm (12") 316 stainless steel
# round rod, body-pocketed and cap-registered (NOT cap-cantilever).
# A small magnetic float slides up and down the rod as the syrup
# level changes; ten reed switches mounted outside the reservoir
# pocket's far +X wall (foam-encapsulated during the body foam pour)
# detect the float's position for level sensing. Same architecture
# AND same SS rod SKU as the carbonator's existing reed+float level
# sensing (see `hardware/future.md` "Level sensing" and `bom.md`
# Tandefio B0CY4DWJFQ): rod captured at one end, registered at the
# other — just extended to 10 reeds per reservoir for finer
# granularity.
#
# Why SS rod + printed bosses instead of a printed PETG strut:
#   - Print reliability. The previous design unioned a 4 mm × ~200
#     mm PETG cylinder into the body; the top ~50 % consistently
#     came out mangled (long thin un-supported axial features are
#     not FDM-friendly). A separately-supplied SS rod side-steps
#     the print problem entirely.
#   - 10-year residue. The appliance is designed for ~10 years of
#     unmaintained service. Sugary syrup builds up on FDM layer
#     lines noticeably faster than on the smooth drawn surface of
#     a SS rod, and the float would eventually stick. The SS rod
#     also doesn't shed plasticizer into the syrup over a decade.
#
# Architecture:
#   - The body has a STANDING CYLINDRICAL BOSS (build_reservoir_body)
#     rising from the wet slope at (x = ±ROD_POSITION_X,
#     z = ROD_POSITION_Z). The boss is a solid PETG cylinder unioned
#     onto the body's wet-slope surface — the slope itself stays
#     continuous and unbroken; no hole is cut through it. A blind
#     cylindrical bore is then cut DOWN into the boss from above,
#     stopping BODY_BOSS_FLOOR mm short of the boss base so a
#     printed-solid floor remains inside the boss. The rod's bottom
#     end drops into this bore with ~0.5 mm radial clearance for
#     slip-fit assembly and bottoms out on the printed floor inside
#     the boss. Rod engagement is BODY_BOSS_HEIGHT − BODY_BOSS_FLOOR
#     ≈ 8 mm of solid axial location, plus the OD shoulder of the
#     boss preventing radial drift at the rod's bottom end.
#   - The rod's top is captured by a slip-fit REGISTER BOSS
#     hanging down from the cap's underside — a hollow boss
#     unioned to the cap body, extending below the cap's base
#     plate, with a downward-opening blind ø3.7 hole around the
#     ø3.175 rod top (~0.5 mm radial clearance). See
#     build_reservoir_cap for the boss + pocket geometry.
#   - During assembly the rod is dropped into the body boss first;
#     then the cap is lowered onto the body and the rod's top
#     slides into the cap register as the cap seats on the gasket.
#     The rod is mechanically captured at BOTH ends — that two-
#     point capture is what makes a 1/8" × 305 mm rod structurally
#     stiff enough to take float-loading without leaning. (A
#     single-ended press-fit in only the body, or only the cap,
#     would let the free tip walk and the float would bind.) The
#     carbonator's rod is welded to its bottom plate; we don't
#     have a plate to weld to, so a printed standing boss with a
#     blind bore is the printed-equivalent capture.
#
# Position: at (x = ±ROD_POSITION_X, z = ROD_POSITION_Z) in the
# reservoir coordinate frame — x sign follows `side`; z stays
# negative for both sides (no z mirroring). Chosen to:
#   - sit OPPOSITE the bulkhead, which occupies z = 28..64 on the
#     +Z half of the reservoir. Placing the rod on the -Z half
#     puts the float in the wider, uncluttered part of the cavity
#     and removes any geometric coupling between the level-sensing
#     hardware and the outlet-bulkhead pocket.
#   - sit in a wider part of the cavity (~38 mm cavity width at
#     z=-45 vs only ~24 mm at z=0), giving generous clearance for
#     the donor donut float regardless of its precise OD/hole.
#   - keep clear of all screw bosses (#1/#4 at z=+64, #2/#5 at
#     z=-64, #3/#6 at z=0): rod at z=-45 is at least 19 mm from
#     the nearest boss on the -Z side.
#   - keep clear of the vent boss (centered at z=+32.5) and the
#     bulkhead pocket (z=28..64): rod at z=-45 is on the opposite
#     half of the cavity.
#
# ROD_DIAMETER = 3.175 mm (1/8") sits comfortably inside whatever
# sliding clearance the donor donut provides; the wider cavity at
# z=-45 means precise hole-to-rod tolerance is no longer a critical
# fit question (vs. the original z=0 position where the cavity was
# only 24 mm wide and a tight float fit mattered more).
#
ROD_POSITION_X = 100.0         # |x| of the rod centerline; mirrors with `side`
ROD_POSITION_Z = -45.0         # z of the rod centerline (does NOT mirror with side); opposite the bulkhead's +Z half, in the wider part of the cavity
ROD_DIAMETER = 3.175           # 1/8" 316 SS round rod OD; supplied as Tandefio B0CY4DWJFQ (already in bom.md for the carbonator's identical job — no new SKU)
ROD_BORE = ROD_DIAMETER + 0.5  # 3.675 mm — printed bore diameter shared by body boss and cap register; ~0.5 mm radial clearance for slip-fit assembly accounting for PETG shrink + FDM hole undersize
ROD_BOSS_OD = ROD_BORE + 4.0   # 7.675 mm — boss outer diameter (2 mm radial wall around the bore, comfortably above the 1.5–2 mm minimum for PETG to print solidly around a small bore); shared by body-side anchor boss and cap-side register boss
ROD_BOSS_HEIGHT = 4.0          # mm; CAP-side boss extends DOWN from cap-local y=0 (cap underside) to y=-ROD_BOSS_HEIGHT. Boss bottom is 2 mm below the rod top at cap-local y=-2, giving 2 mm of axial rod-boss engagement.
BODY_BOSS_HEIGHT = 10.0        # mm; BODY-side anchor boss rises from the wet slope at (x = ±ROD_POSITION_X, z = ROD_POSITION_Z). Boss top sits at slope_y + BODY_BOSS_HEIGHT. Taller than the cap boss because this end ANCHORS the rod (vs the cap-side which only REGISTERS the top against tip walk); ≈3× ROD_DIAMETER, the standard rule of thumb for solid axial location of a round pin in a printed boss.
BODY_BOSS_FLOOR = 2.0          # mm; thickness of the printed-solid PETG floor INSIDE the body boss, between the blind bore's bottom and the wet-slope surface beneath the boss base. The bore is cut down to bore_bottom = slope_y + BODY_BOSS_FLOOR, leaving 2 mm of solid PETG for the rod tip to bottom out on. The wet slope below the boss footprint remains completely intact — there is no hole through the slope.
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
# from `_foam_shell_geometry.py`, so the flange chamber's curved
# bottom sits exactly on top of the 4 mm outer floor (4 mm of PETG
# below the chamber as a fluid barrier) and the pocket is centered
# in X between the cavity's inner +X face and the concave arc's peak
# (the tank-facing arc's deepest reach at z = 0).
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
port_position_x = _shell_reservoir_bulkhead_port_x  # derived in _foam_shell_geometry.py as the midpoint between the body's inner +X face and the inner concave-arc peak (at z=0) — i.e. centered between the two interior X walls of the cavity. The matching foam-shell pass-through hole reads the same constant, so the two cannot drift apart on future wall-thickness changes.
port_position_y = _shell_reservoir_bulkhead_port_y  # Y of the BULKHEAD BODY AXIS. Sits 1 mm ABOVE the nut cavity center (nut_position_y) per the bulkhead_axis_lift_above_nut in _cold_core_interface.py. Used for: bulkhead body chamber (release ring + collet body), wet exit tube, panel hole, wet/dry TPU seal counterbores, foam-shell pass-through hole, dry slab anchor, wet/dry slope anchor, rod body boss (via slope_low_y). NOT used for the nut cavity — see nut_position_y below.
nut_position_y = _shell_reservoir_bulkhead_nut_y    # Y of the NUT CAVITY center. Anchored to the floor's low point so the washer counterbore (the deepest part of the cavity) sits on top of the 4 mm reservoir floor, preserving the full fluid barrier. Sits 1 mm BELOW port_position_y per the 2026-05-16 print test — the bulkhead axis lifts up 1 mm above the nut, while the nut stays at the floor.
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
bulkhead_wet_chamber_length = 22.2      # wet nut + collet body + release ring — adjusted from 24 to free 1.8 mm for the panel's growth in −Z direction (see panel_thickness below). The reduction comes entirely from the collet body section.
bulkhead_wet_antechamber_length = 2.0   # gap on the bulkhead's wet face — must exist or syrup can't reach the port
bulkhead_panel_thickness = 6.8          # was 5 mm. Grown by 1.8 mm to fit 1.4 mm-deep TPU seal counterbores on BOTH faces while preserving the 4 mm minimum wall thickness in the panel core (between the two counterbores). Growth is in the −Z direction: panel's +Z face stays at z=panel_z_max, panel's −Z face moves to z=panel_z_max − 6.8.
# (bulkhead_dry_chamber_length, bulkhead_pocket_length, and the
# downstream bulkhead_dry_end_z below were here when the dry side was
# enclosed; the dry side is now wide-open from the panel +Z face so
# none of those lengths/positions feed any geometry — removed.)
#
# Wet-side nut. The actual hardware sitting at z=panel_z_min on the
# wet side is the *nut*, not an integral flange — the bulkhead is
# inserted from the dry side and the integral flange ("not-a-nut",
# fused to the body) ends up on the dry side. The nut is a stepped
# washer+hex piece dropped into the wet pocket before insertion and
# held there by a hex-shaped print pocket while the bulkhead screws
# in through it.
#
# The nut's hex portion is technically a 12-sided shape (the 6 hex
# corners are clipped well inside the washer's outer ⌀), but the
# print pocket can safely treat it as a regular hex of the given
# flat-to-flat dimension — the pocket overshoots by ~1 mm of air at
# each corner, which doesn't affect the grip on the 6 flats.
bulkhead_nut_hex_flat_to_flat = 19.8     # the 6 flats that grip the pocket for anti-rotation
bulkhead_nut_hex_corner_to_corner = bulkhead_nut_hex_flat_to_flat / math.cos(math.radians(30))  # 22.86 mm, ~1 mm past the actual clipped corners
bulkhead_nut_washer_diameter = 22.1
bulkhead_nut_hex_depth = 4.1             # axial depth of the hex portion
bulkhead_nut_washer_depth = 1.6          # axial depth of the washer portion
bulkhead_nut_total_depth = bulkhead_nut_hex_depth + bulkhead_nut_washer_depth  # 5.7
bulkhead_nut_clearance = 0.1             # per-side clearance for press-fit (both hex flats and washer ⌀)
#
# TPU 90A face seals at the bulkhead/panel joint. One on each side of
# the panel: a flat printed washer that sits in a shallow counterbore
# in the panel face and gets compressed when the mating face (nut
# washer on the wet side, integral flange on the dry side) seats flush
# against the panel rim outside the counterbore. Compression ratio is
# (seal_thickness − counterbore_depth) / seal_thickness = 30%, which
# is standard for face-seal elastomers.
#
# Sizing the counterbore smaller than both mating-face ODs (nut washer
# ⌀22.1, integral flange ⌀22.9) ensures the mating faces still seat
# directly on PETG outside the counterbore — the elastomer carries
# only the seal load, not the clamping force.
bulkhead_seal_id = 17.5                  # 0.25 mm/side clearance around the panel hole (⌀17)
bulkhead_seal_od = 20.3                  # 0.1 mm/side clearance in the counterbore
bulkhead_seal_thickness = 2.0            # matches the reservoir gasket convention
bulkhead_seal_counterbore_diameter = 20.5
bulkhead_seal_counterbore_depth = 1.4    # 30% compression of the 2 mm seal when the mating face seats flush
#
# Wet-side section lengths (estimates — refine with drawing measurements):
bulkhead_flange_length = bulkhead_nut_total_depth              # 5.7 — the wet-side pocket against the panel holds the *nut* (a stepped washer+hex piece), not an integral flange. Name kept for now as the geometric region label.
bulkhead_collet_body_length = 13.5                             # middle of the wet section — extended ~7.5 mm beyond the CI1208W's 6 mm so the bulkhead's smooth body has room to rest comfortably when fully screwed forward into the nut. Reduced from 15.3 → 13.5 to absorb the 1.8 mm panel growth (5 → 6.8 mm) needed to fit TPU seal counterbores on both panel faces. Panel's +Z face stays at z=panel_z_max=59; everything else cascades.
bulkhead_release_ring_length = (
    bulkhead_wet_chamber_length - bulkhead_flange_length - bulkhead_collet_body_length
)                                                              # 3 — the visible end with the push-to-release ring
#
# Wet-side chamber diameters per section (body OD + clearance).  The
# nut pocket diameter is set by the bulkhead_nut_* constants above
# (stepped hex + washer), so it isn't repeated here.
bulkhead_collet_chamber_diameter = 19.0                        # est. body OD ø17–18 + ~0.5 mm/side
bulkhead_release_chamber_diameter = 11.0                       # caliper-measured release ring ø9.57 + ~0.7 mm/side
#
bulkhead_wet_end_z = 30.0                # z of bulkhead body's wet face (the port) — stays fixed; everything downstream of it slides 12 mm in +Z by way of the longer collet section
bulkhead_wet_chamber_z_min = bulkhead_wet_end_z - bulkhead_wet_antechamber_length  # 28 (tip-channel −Z edge, stays put)
bulkhead_release_z_start = bulkhead_wet_end_z                   # 30 — release-ring section starts at the body's wet face (stays)
bulkhead_collet_z_start = bulkhead_release_z_start + bulkhead_release_ring_length  # 33 (release-ring → collet boundary, stays)
bulkhead_flange_z_start = bulkhead_collet_z_start + bulkhead_collet_body_length    # 46.5 — start of the nut pocket (named flange because the geometry was originally laid out for an integral flange here; it actually houses the nut)
bulkhead_panel_z_min = bulkhead_flange_z_start + bulkhead_flange_length             # 52.2 (panel's −Z face; was 54 before the panel grew 1.8 mm in −Z to fit the seal counterbores)
bulkhead_panel_z_max = bulkhead_panel_z_min + bulkhead_panel_thickness              # 59 (panel's +Z face; stays put — panel grows in −Z direction only)
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
# 2026-05-16 print + assembly test: the dry-side slab sat directly
# on the chamber top, leaving no vertical clearance above the
# bulkhead's integral flange for a wrench to grip and rotate the
# body during install. Raise the slab BOTTOM by this much above the
# chamber top to open up wrench room. The slab still maintains its
# 4 mm thickness as the fluid barrier above; the new space between
# chamber top and slab bottom is just the air gap where a wrench /
# fingers / collet-release ring fits.
dry_ceiling_clearance = 20.0
#
# floor_baseline_y = top face of the dry-side slab at z =
# bulkhead_panel_z_min. Stack from the chamber's curved top:
#   chamber_top + dry_ceiling_clearance + slab_thickness
# = (port_position_y + 11.5) + 20 + 4 = port_position_y + 35.5
# The slope tilts the slab top upward as z increases, so the
# bulkhead dry-flange clearance is positive everywhere in z ≥
# bulkhead_panel_z_max.
floor_baseline_y = port_position_y + bulkhead_pocket_diameter / 2 + dry_ceiling_clearance + bulkhead_dry_slab_thickness
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
_outer_far_x_abs = bag_pocket_far_inner_x - reservoir_clearance        # 121
_outer_z_max = bag_pocket_z_inner_max - reservoir_clearance            # 70
_outer_centerward_radius = pocket_centerward_arc_outer_radius + reservoir_clearance  # 73
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
# Bosses 4 / 5 need their cut direction pointed at the inner-wall
# CORNER (where the inner curve at radius _CURVE_INNER_X_AT_Z0 = 76
# meets the inner ±Z wall at z = ±_PLUS_Z_WALL_INNER_Z = ±66), not
# at the closest point on the curve along the inward radial line.
# Pointing at the corner is the same pattern bosses 1 / 2 use (their
# cuts slope down away from the +X × ±Z inner corner). For boss 4
# the corner is at (≈37.68, 66), 7.19 mm from the boss in the
# (−X, +Z) direction — too far to use as a literal pivot (a 7.19 mm
# cut depth would eat into the 7 mm heat-set pocket). Instead, take
# the unit vector toward the corner as wall_dir, and place the pivot
# VIRTUALLY at 2 mm along that direction from the boss center, so
# the cut depth at boss center matches boss 6 (the curve apex) and
# stays well clear of the pocket.
_inner_corner_curve_x = math.sqrt(_CURVE_INNER_X_AT_Z0**2 - _PLUS_Z_WALL_INNER_Z**2)  # ≈ 37.68
_corner_curve_to_inner_corner_dx = _inner_corner_curve_x - _corner_curve_x        # ≈ −6.91
_corner_curve_to_inner_corner_dz = _PLUS_Z_WALL_INNER_Z - _corner_curve_z         # ≈ 2
_corner_curve_to_inner_corner_dist = math.sqrt(
    _corner_curve_to_inner_corner_dx**2 + _corner_curve_to_inner_corner_dz**2
)                                                                                  # ≈ 7.19
_corner_curve_wall_dir_x = _corner_curve_to_inner_corner_dx / _corner_curve_to_inner_corner_dist  # ≈ −0.961
_corner_curve_wall_dir_z = _corner_curve_to_inner_corner_dz / _corner_curve_to_inner_corner_dist  # ≈ +0.278
_corner_curve_pivot_distance = 2.0
_corner_curve_virtual_pivot_x = _corner_curve_x + _corner_curve_pivot_distance * _corner_curve_wall_dir_x  # ≈ 42.67
_corner_curve_virtual_pivot_z = _corner_curve_z + _corner_curve_pivot_distance * _corner_curve_wall_dir_z  # ≈ 64.56
BODY_BOSS_CUT_INFO_FOR_SIDE_PLUS_1 = {
    # (boss_x, boss_z) → (pivot_x, pivot_z, wall_dir_x, wall_dir_z)
    #   wall_dir is a UNIT vector in XZ pointing from the boss center toward the wall pivot
    (_corner_xz_x, _corner_xz_z):
        (_FAR_WALL_INNER_X, _PLUS_Z_WALL_INNER_Z, _INV_SQRT2, _INV_SQRT2),    # 1
    (_corner_xz_x, -_corner_xz_z):
        (_FAR_WALL_INNER_X, -_PLUS_Z_WALL_INNER_Z, _INV_SQRT2, -_INV_SQRT2),  # 2
    (_far_mid_x, 0.0):
        (_FAR_WALL_INNER_X, 0.0, 1.0, 0.0),                                   # 3
    (_corner_curve_x, _corner_curve_z):
        (_corner_curve_virtual_pivot_x, _corner_curve_virtual_pivot_z,
         _corner_curve_wall_dir_x, _corner_curve_wall_dir_z),                 # 4
    (_corner_curve_x, -_corner_curve_z):
        (_corner_curve_virtual_pivot_x, -_corner_curve_virtual_pivot_z,
         _corner_curve_wall_dir_x, -_corner_curve_wall_dir_z),                # 5
    (_curve_apex_x, 0.0):
        (_CURVE_INNER_X_AT_Z0, 0.0, -1.0, 0.0),                               # 6
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
    #
    # The reservoir-body's outer_top_y must leave room above for the
    # full body-cap stack (TPU gasket + PETG cap), with reservoir_
    # clearance to spare against the bag-pocket wall top.  Stack from
    # the body's top face upward, in order:
    #   body wall top         y = outer_top_y
    #   gasket                + gasket_thickness        (2 mm)
    #   cap perimeter rim     + cap_wall_height         (5 mm)
    #   cap base plate        + cap_base_thickness      (4 mm)
    #   reservoir_clearance   + reservoir_clearance     (0.5 mm)
    #   bag-pocket wall top   = bag_pocket_walls_top_y  (= foam-shell wall top)
    # so outer_top_y = bag_pocket_walls_top_y − reservoir_clearance −
    # (gasket_thickness + cap_wall_height + cap_base_thickness).
    #
    # At 2 mm foam-shell wall thickness this resolves to 213.4 − 0.5 −
    # (2 + 5 + 4) = 201.9, leaving the cap's top face flush at
    # y = 212.9 (0.5 mm clear of the bag-pocket wall top).  The
    # body alone is 201.9 − 2.5 = 199.4 mm tall.
    cap_stack_above_body = gasket_thickness + cap_wall_height + cap_base_thickness
    outer_far_x_abs = bag_pocket_far_inner_x - reservoir_clearance
    outer_z_max = bag_pocket_z_inner_max - reservoir_clearance
    outer_floor_bottom_y = bag_pocket_floor_top_y + reservoir_clearance
    outer_top_y = bag_pocket_walls_top_y - reservoir_clearance - cap_stack_above_body
    outer_centerward_radius = pocket_centerward_arc_outer_radius + reservoir_clearance
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
    # Thick sloped floor + bulkhead pocket
    # ─────────────────────────────────────────────────────
    # Floor inner surface is piecewise across z, with the split at the
    # PANEL's −Z face (= where the wet nut seats and the actual
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
    # First two sections are simple (cylinder lower-half + matching-width
    # box upper-half) "stadiums". The third section (against the panel)
    # is the nut pocket — handled separately below because it's stepped
    # (hex + washer counterbore), not a single cylinder.
    wet_sections = [
        # (z_start,                                z_end,                    diameter)
        (bulkhead_wet_chamber_z_min,               bulkhead_collet_z_start,  bulkhead_release_chamber_diameter),  # release ring + antechamber
        (bulkhead_collet_z_start,                  bulkhead_flange_z_start,  bulkhead_collet_chamber_diameter),   # collet body — bulkhead's smooth main section rests here when fully screwed forward
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

    # Curved exit from the wet collet chamber. The existing straight
    # ⌀11 half-cylinder dead-ends at z=bulkhead_wet_chamber_z_min into
    # solid PETG, leaving the bulkhead's wet face only the radial
    # 0.5 mm-per-side gap around the collet and the stadium ceiling
    # box as flow paths to the cavity. Continue the cylinder past
    # z=28 with a 90° quarter-arc swept tube of the same ⌀11, joining
    # tangentially at z=28 (same axis along −Z, no step in cross-
    # section), curving up through +Y over a 30 mm radius until the
    # tube's axis is vertical. The arc punches well clear of the
    # floor material into the open cavity above, giving syrup a
    # designed curved flow channel from the cavity down into the
    # bulkhead's wet face.
    wet_exit_arc_radius = 30.0

    # Profile: ⌀11 circle in the plane perpendicular to the path's
    # initial tangent (which is world −Z), centered at the chamber's
    # −Z face on the bulkhead axis.
    wet_exit_profile = cq.Workplane(cq.Plane(
        origin=(port_x_signed, port_position_y, bulkhead_wet_chamber_z_min),
        xDir=(1, 0, 0),
        normal=(0, 0, -1),
    )).circle(bulkhead_release_chamber_diameter / 2)

    # Path: 90° arc in the world YZ plane at x=port_x_signed.
    #   Workplane local +x = world −Z (the direction of travel)
    #   Workplane normal   = world +X
    #   Workplane local +y = world +Y (computed from normal × xDir)
    # Start at local (0, 0), end at local (R, R). Arc curves through
    # midpoint (R sin45°, R − R cos45°).
    wet_exit_path_plane = cq.Plane(
        origin=(port_x_signed, port_position_y, bulkhead_wet_chamber_z_min),
        xDir=(0, 0, -1),
        normal=(1, 0, 0),
    )
    _R = wet_exit_arc_radius
    _arc_mid = (_R * math.sin(math.radians(45)),
                _R * (1 - math.cos(math.radians(45))))
    _arc_end = (_R, _R)
    wet_exit_path = (
        cq.Workplane(wet_exit_path_plane)
        .moveTo(0, 0)
        .threePointArc(_arc_mid, _arc_end)
    )

    wet_exit_tube = wet_exit_profile.sweep(wet_exit_path)
    body = body.cut(wet_exit_tube)

    # Nut cavity: third wet section. The bulkhead "nut" is a single
    # stepped washer+hex piece — hex portion at the deeper (−Z) end
    # gripped by a flat-top hex pocket (⌀19.8 flat-to-flat +
    # clearance) against rotation, washer portion at the panel (+Z)
    # end cleared by a round counterbore (⌀22.1 + clearance) so the
    # washer can seat against the panel's −Z face through a TPU seal.
    # Install sequence: drop the nut in from above (ceiling boxes
    # open the cavity from above), gravity seats it, hex flats
    # prevent rotation. Then thread the bulkhead in from the dry
    # side; thread engagement locks the nut axially.
    #
    # Anchored in Y to `nut_position_y` (the floor's low point), 1 mm
    # BELOW the bulkhead axis at `port_position_y`. The nut is the
    # deepest feature in this area, and anchoring it at the floor
    # preserves the full 4 mm of PETG fluid barrier below. The
    # bulkhead's ⌀~13 threaded section engages the nut at the 1 mm
    # offset, comfortably within the ⌀17 panel hole's clearance.
    nut_hex_z_min    = bulkhead_flange_z_start
    nut_hex_z_max    = nut_hex_z_min + bulkhead_nut_hex_depth
    nut_washer_z_max = bulkhead_panel_z_min

    # Flat-top hex (one flat at workplane +Y, one at workplane −Y),
    # so the stadium-pattern ceiling box opens along a flat edge —
    # matching the round chambers' geometry. Vertices at angles
    # 0°, 60°, 120°, 180°, 240°, 300° from +X put flats at ±Y.
    hex_R = (bulkhead_nut_hex_corner_to_corner + 2 * bulkhead_nut_clearance) / 2
    hex_vertices_local = [
        (hex_R * math.cos(math.radians(a)), hex_R * math.sin(math.radians(a)))
        for a in (0, 60, 120, 180, 240, 300)
    ]
    nut_hex_part = (
        cq.Workplane(cq.Plane(
            origin=(port_x_signed, nut_position_y, nut_hex_z_min),
            xDir=(1, 0, 0),
            normal=(0, 0, 1),
        ))
        .polyline(hex_vertices_local)
        .close()
        .extrude(nut_hex_z_max - nut_hex_z_min)
    )
    nut_washer_part = (
        cq.Workplane(cq.Plane(
            origin=(port_x_signed, nut_position_y, nut_hex_z_max),
            xDir=(1, 0, 0),
            normal=(0, 0, 1),
        ))
        .circle((bulkhead_nut_washer_diameter + 2 * bulkhead_nut_clearance) / 2)
        .extrude(nut_washer_z_max - nut_hex_z_max)
    )
    nut_cavity = nut_hex_part.union(nut_washer_part)
    body = body.cut(nut_cavity)

    # Ceiling boxes — one per nut section (hex + washer) — that open
    # the nut cavity upward to the wet volume so the nut can be
    # dropped in before the cap is installed. Anchored to
    # `nut_position_y` to stay co-centered with the nut cavity (NOT
    # the bulkhead axis, which sits 1 mm above).
    for (z_start, z_end, width) in (
        (nut_hex_z_min, nut_hex_z_max,
         bulkhead_nut_hex_corner_to_corner + 2 * bulkhead_nut_clearance),
        (nut_hex_z_max, nut_washer_z_max,
         bulkhead_nut_washer_diameter + 2 * bulkhead_nut_clearance),
    ):
        nut_ceiling_box = (
            _wp_at(port_x_signed, nut_position_y, (z_start + z_end) / 2.0)
            .rect(width, z_end - z_start)
            .extrude(ceiling_y_top - nut_position_y)
        )
        body = body.cut(nut_ceiling_box)

    body = body.cut(_z_pocket_cut(
        bulkhead_panel_z_min, bulkhead_panel_z_max, bulkhead_panel_hole_diameter,
    ))                                       # panel hole ⌀17

    # TPU seal counterbores — one on each panel face. A flat printed
    # TPU washer seats in each counterbore; the mating face (nut
    # washer on the wet side, integral flange on the dry side) presses
    # on the exposed 0.6 mm of TPU until flush against the panel rim
    # outside the counterbore, giving 30% compression. Panel thickness
    # was grown from 5 → 6.8 mm to keep ≥4 mm of PETG between the two
    # counterbore bottoms.
    body = body.cut(_z_pocket_cut(
        bulkhead_panel_z_min,
        bulkhead_panel_z_min + bulkhead_seal_counterbore_depth,
        bulkhead_seal_counterbore_diameter,
    ))                                       # wet-side seal counterbore
    body = body.cut(_z_pocket_cut(
        bulkhead_panel_z_max - bulkhead_seal_counterbore_depth,
        bulkhead_panel_z_max,
        bulkhead_seal_counterbore_diameter,
    ))                                       # dry-side seal counterbore
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
    # (radius inner_centerward_radius) meets the wet nut seat face
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
    # Level-sensing rod body anchor (standing boss + blind bore)
    # ─────────────────────────────────────────────────────
    # A standing cylindrical PETG boss rising from the wet slope at
    # (x = ±ROD_POSITION_X, z = ROD_POSITION_Z), with a blind
    # cylindrical bore cut into the boss from above. A separately-
    # supplied 1/8" × 12" 316 SS round rod (ROD_DIAMETER = 3.175)
    # drops bottom-first into the bore during assembly; the rod's
    # top is then captured by a register boss in the cap underside
    # (built in build_reservoir_cap). See the "Level-sensing rod"
    # section at the top of this file for the full architecture
    # rationale.
    #
    # The wet slope stays continuous and unbroken — the boss is
    # added ON TOP of the slope as new material, and the bore stops
    # BODY_BOSS_FLOOR (2) mm short of the boss base so the printed
    # PETG floor inside the boss is what the rod tip bottoms out
    # on. No hole is cut through the wet slope, so syrup doesn't
    # see any opening into the wedge interior.
    #
    # Implementation:
    #   1. Compute slope_y at (z = ROD_POSITION_Z) from the same
    #      slope plane the body uses, so the boss base always sits
    #      flush on the slope even if slope_rate or slope anchor
    #      change later.
    #   2. UNION a solid cylinder of diameter ROD_BOSS_OD, base at
    #      slope_y, height BODY_BOSS_HEIGHT — this is the boss.
    #   3. CUT a cylinder of diameter ROD_BORE, base at
    #      slope_y + BODY_BOSS_FLOOR, height (BODY_BOSS_HEIGHT
    #      − BODY_BOSS_FLOOR + 0.1) — the +0.1 ensures CADQuery
    #      cleanly breaks through the boss top face. This carves
    #      the blind bore.
    #
    # Added LAST in build_reservoir_body, after every existing
    # feature (wedge, bulkhead pocket, slab cut, fillets), so the
    # new boss geometry cannot perturb any earlier edge/face
    # selector.
    rod_x_signed = ROD_POSITION_X * side
    # Slope y at (z = ROD_POSITION_Z = -45): ≈ 22.8 with current
    # slope parameters. Boss base sits at this y, boss top at
    # slope_y + 10 ≈ 32.8.
    rod_slope_y_at_z = slope_low_y + slope_rate * (bulkhead_panel_z_min - ROD_POSITION_Z)
    body_boss_cylinder = (
        _wp_at(rod_x_signed, rod_slope_y_at_z, ROD_POSITION_Z)
        .circle(ROD_BOSS_OD / 2.0)
        .extrude(BODY_BOSS_HEIGHT)
    )
    body = body.union(body_boss_cylinder)
    # Blind bore: base BODY_BOSS_FLOOR (2) mm above the slope,
    # extruded up through the top of the boss with a small
    # overshoot so the cut cleanly opens at the boss top face.
    bore_bottom_y = rod_slope_y_at_z + BODY_BOSS_FLOOR
    rod_bore_cut = (
        _wp_at(rod_x_signed, bore_bottom_y, ROD_POSITION_Z)
        .circle(ROD_BORE / 2.0)
        .extrude(BODY_BOSS_HEIGHT - BODY_BOSS_FLOOR + 0.1)
    )
    body = body.cut(rod_bore_cut)

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
    outer_centerward_radius = pocket_centerward_arc_outer_radius + reservoir_clearance

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
    # Level-sensing rod register boss
    # ─────────────────────────────────────────────────────
    # Hollow boss hanging DOWN from the cap's underside into the body
    # cavity. The rod top slides into the boss's bore from below as
    # the cap is lowered onto the body. The gasket is a perimeter ring
    # only — at the rod position (cavity interior) there is nothing
    # between the body wall top and the cap's underside, so the boss
    # is free to extend below cap-local y=0.
    #
    # Bore is sized for the 1/8" SS rod (ROD_BORE = 3.675 — 0.5 mm
    # radial clearance around the 3.175 rod) — same slip-fit
    # clearance used by the body socket below, so the cap drops
    # straight down onto a rod already seated in the body socket
    # without binding. Boss OD ROD_BOSS_OD gives ~2 mm radial wall
    # of PETG around the bore, comfortably above the print-strength
    # minimum.
    #
    # Boss outer cylinder: solid PETG from cap-local y=-ROD_BOSS_HEIGHT
    # up to the base plate at cap-local y=cap_wall_height (=5).
    # Boss bore: extends from boss bottom up to the base plate's
    # underside, where the base plate (cap-local y=5..9) closes the
    # bore from above.
    rod_x_signed = ROD_POSITION_X * side
    boss_outer = (
        _wp_at(rod_x_signed, -ROD_BOSS_HEIGHT, ROD_POSITION_Z)
        .circle(ROD_BOSS_OD / 2.0)
        .extrude(ROD_BOSS_HEIGHT + cap_wall_height)
    )
    cap = cap.union(boss_outer)

    boss_bore = (
        _wp_at(rod_x_signed, -ROD_BOSS_HEIGHT - 0.1, ROD_POSITION_Z)
        .circle(ROD_BORE / 2.0)
        .extrude(ROD_BOSS_HEIGHT + cap_wall_height + 0.1)
    )
    cap = cap.cut(boss_bore)

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
    outer_centerward_radius = pocket_centerward_arc_outer_radius + reservoir_clearance

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


def build_reservoir_bulkhead_seal():
    """Flat TPU 90A washer that seals between the bulkhead's clamping
    face and the reservoir body's panel face. Sits in a 1.4 mm-deep
    counterbore in the panel; the exposed 0.6 mm compresses to 0 (30%
    compression) when the mating face (nut washer on the wet side or
    integral flange on the dry side) seats flush against the panel
    rim outside the counterbore.

    Same part on both sides (symmetric, ID/OD/thickness are
    side-independent). Print 4 per build (one per panel face × two
    reservoirs)."""
    return (
        cq.Workplane(xz_plane_y_up)
        .circle(bulkhead_seal_od / 2.0)
        .circle(bulkhead_seal_id / 2.0)
        .extrude(bulkhead_seal_thickness)
    )


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════


def main():
    # Left/right convention. The machine's front face is +Z — water
    # outlet, bulkhead ports, and the dispense faucet all live on the
    # +Z side. Looking AT the machine from the front (viewer at +Z
    # looking in the −Z direction, +Y up), the cross product x̂ × ŷ = ẑ
    # points back toward the viewer, which puts +X on the viewer's
    # RIGHT and −X on the viewer's LEFT.
    #
    #   side = +1  →  +X reservoir  →  user's RIGHT  →  "*-right.step"
    #   side = −1  →  −X reservoir  →  user's LEFT   →  "*-left.step"
    #
    # Body and cap genuinely differ between sides — they're NOT
    # z-symmetric. The bulkhead pocket housing lives on +Z (front) for
    # both reservoirs, and the strut and vent positions stay at fixed
    # world Z (the strut at z=−45, the cap vent at z=+32.5) so they
    # remain on the back / front of the machine for both reservoirs.
    # Mirror across x=0 only — never across z=0.
    #
    # The gasket and the retaining ring are BOTH z-symmetric in their
    # own right (perimeter rings with z-mirrored hole patterns), and
    # under z-symmetry a 180° rotation about Y collapses to an x-mirror
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

    gasket = build_reservoir_gasket(side=+1)  # z-symmetric: flip to install on −X side
    retaining_ring = build_reservoir_retaining_ring()
    bulkhead_seal = build_reservoir_bulkhead_seal()
    export_step(gasket, str(here / "reservoir-gasket.step"))
    export_step(retaining_ring, str(here / "reservoir-retaining-ring.step"))
    export_step(bulkhead_seal, str(here / "reservoir-bulkhead-seal.step"))
    print(f"-> reservoir-gasket.step")
    print(f"-> reservoir-retaining-ring.step")
    print(f"-> reservoir-bulkhead-seal.step")


if __name__ == "__main__":
    main()
