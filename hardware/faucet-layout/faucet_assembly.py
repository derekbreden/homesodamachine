"""The faucet, whole — every body above the counter, the countertop it clamps
through, and the three tubes running down past it into the umbilical.

`printed-parts/faucet/` holds the printed pieces individually and
`cut-parts/faucet/` the plate under the slab; this is the column they stack into,
with the harvested Westbrass they are built around
(`reference/touch-flo-faucet/westbrass-reference/`) and the display on the tip.

FRAME: the repo's +Z-up. +Z is height and the Westbrass's axis, +X is lateral (the
two flavor tubes mirror across X = 0), -Y is the front — the gooseneck dispenses
toward -Y and the lever points toward -Y, so the water port and the flavor-tube
pill sit BEHIND the Westbrass's axis at +Y. Z = 0 is the above-counter plate's
top face; the countertop stands below the plate and above-counter gasket.

TWO WATER PORTS, and the tube in each is a different size. The blue 1/4" soda
umbilical tube lands on the compression port at the BOTTOM of the shank (Z = -50)
and water rises inside the shank; the 3/8"
soda faucet tube leaves the Westbrass's Ø10 top port and runs up the gooseneck,
sealed into that port by the printed TPU thimble. `assembly/faucet-and-umbilical.md` is the bench
that makes both up.

The column, top to bottom:

    display               Waveshare ESP32-S3-Touch-LCD-1.47, on the dispense tip
    shell                 three printed pieces, as printed — joint voids and all
    tubes                 3/8" soda faucet tube up the middle, two 1/4" flavor behind it
    lever                 retained donor lever in its rest position
    Westbrass             the harvested R2031-NL
    o-ring                printed TPU thimble in the Westbrass's top water port
    above-counter plate   printed oval with hidden base screws
    above-counter gasket  matching TPU oval
    countertop            30 mm slab
    under-counter plate   existing cut 316 SS plate
    soda umbilical tube   1/4" blue, on the shank's own compression port

AND BELOW THE PLATE, THE UMBILICAL — the same three tubes gathered into the pack a sleeve makes of
them, down to the end the installer pushes into the +Y wall of back-top:

    unions           a White faucet's two John Guest PP0408W, end to end at the top of the
                     wrap, each joining a white flavor tube to its black run; a Black
                     faucet's flavor tubes run through the same places unjoined
    foam             CARGEN nitrile on the blue tube only, five 1-ft segments butted, from
                     below the lower union
    sleeve           PET braid over the unions and then the pack, a segment to each of the
                     foam's, the top one run on up over both unions
    tube collars     SODA on the blue, FLAVOR on each black, on the bare tails at the wall

Its run is drawn to `umbilical_drawn` rather than to the factory cut: the metre and a half between
the gather and the wall is one straight, and what a picture of it is worth is the end that has
features on it.

Regenerate:
    tools/cad-venv/bin/python hardware/faucet-layout/faucet_assembly.py
"""

import functools
import json
import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "scripts"),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
from _cadq_export import export_assembly, import_step
import _materials as _mat
from docgen import substitute_py_comments


_assembly_dir = Path(__file__).resolve().parent
_repo_hardware_dir = _assembly_dir.parent
_faucet_printed_dir = _repo_hardware_dir / "printed-parts" / "faucet"
_faucet_cut_dir = _repo_hardware_dir / "cut-parts" / "faucet"

ref_westbrass_step = (_repo_hardware_dir / "reference" / "touch-flo-faucet"
                 / "westbrass-reference" / "westbrass-reference.step")
under_counter_dxf = (_faucet_cut_dir / "under-counter-plate"
                     / "under-counter-plate.dxf")

sys.path.insert(0, str(_repo_hardware_dir / "printed-parts" / "cadlib"))
from world_workplane import WorldWorkplane, xy_plane_z_up

# Each printed part's build_*() returns +Z-up.
sys.path.insert(0, str(_faucet_printed_dir))  # for _faucet_interface
sys.path.insert(0, str(_faucet_printed_dir / "above-counter-plate"))
sys.path.insert(0, str(_faucet_printed_dir / "above-counter-gasket"))
sys.path.insert(0, str(_faucet_printed_dir / "tpu-o-ring"))
sys.path.insert(0, str(_faucet_printed_dir / "faucet-shell"))
sys.path.insert(0, str(_faucet_printed_dir / "faucet-display-cover"))
# The identification the tubes carry below the counter, and the filaments it prints in — one part
# and one colour table, shared with the chips on the +Y wall of back-top.
sys.path.insert(0, str(_faucet_printed_dir / "tube-collar"))
sys.path.insert(0, str(_repo_hardware_dir / "printed-parts" / "enclosure" / "y-wall-of-back-top"))
# The union a White faucet joins each flavor tube's white run to its black one with.
sys.path.insert(0, str(_repo_hardware_dir / "reference" / "jg-pp0408w"))
import tube_collar
import _y_wall_dimensions as _rear
import jg_pp0408w
import above_counter_plate
import above_counter_gasket
import tpu_o_ring
import faucet_shell
import _faucet_interface as _fi
import faucet_display_cover
from _faucet_interface import (
    display_housing_width,
    display_housing_length,
    display_pcb_width,
    display_pcb_length,
    display_corner_r,
    display_pcb_corner_r,
    display_total_depth,
    display_pcb_bottom_z,
    display_pcb_top_z,
)


# Reference Westbrass geometry, shared with
# `../westbrass-reference/westbrass_reference.py`. The Westbrass's
# water port sits at depth Y = +port_center_depth (BEHIND its own axis,
# toward the back); +Z is the Westbrass's vertical axis.
port_center_depth = 8.875
plateau_z = 39.0
westbrass_od = 31.50  # cylinder OD = rectangle long dim
westbrass_r = westbrass_od / 2
shank_od = 11.0
shank_length = 50.0  # shank runs from Z=0 down to Z=-shank_length
countertop_hole_diameter = 34.93  # 1-3/8", the standard the shank is sized for


# Soda faucet tube — ⌀[9.525 mm](SODA_FAUCET_TUBE_OD) (3/8" LLDPE) — seated in the
# Westbrass's 10.0 mm water port and running up through the gooseneck. The
# 0.475 mm diametric (0.2375 mm radial) gap is sealed by a printed TPU
# bushing on the real tube (not modeled).
# [9.525 mm](SODA_FAUCET_TUBE_OD) — 3/8" LLDPE in millimeters.
soda_faucet_tube_od = 0.375 * 25.4
soda_faucet_tube_r = soda_faucet_tube_od / 2.0
soda_faucet_tube_above_plateau = 40.0
soda_faucet_tube_into_port = 15.0
soda_faucet_tube_z_bottom = plateau_z - soda_faucet_tube_into_port  # [24 mm](SODA_FAUCET_TUBE_Z_BOTTOM)
soda_faucet_tube_z_top = plateau_z + soda_faucet_tube_above_plateau  # [79 mm](SODA_FAUCET_TUBE_Z_TOP)


# Flavor tubes — Ø 1/4" — pass behind the Westbrass, on either side of D.
# The lower row is symmetric about X=0; the shared faucet paths spread it
# at the vent seals and return it to the symmetric three-tube drink face.
# Below the mounting plate, flavor-b steps out past the unions.
# [6.35 mm](FLAVOR_TUBE_OD) — 1/4" LLDPE in millimeters.
flavor_tube_od = 1.0 / 4.0 * 25.4
flavor_tube_r = flavor_tube_od / 2.0
# [18.93 mm](FLAVOR_TUBE_DEPTH_LOWER) — tangent to the Westbrass's +Y (back) face.
flavor_tube_depth_lower = westbrass_r + flavor_tube_r
flavor_tube_x_offset = _fi.flavor_tube_x_offset

# THE COUNTER THE STACK CLAMPS THROUGH. The slab is not a part — it is the customer's kitchen — but
# it is what sets where the cut plate lands and so where the umbilical hangs from, and the assembly
# carries it at the figure `assembly/faucet-and-umbilical.md` sums its tube lengths on: 30 mm of 3 cm
# stone, in a 19–38 range.
countertop_thickness = 30.0
countertop_top_z = above_counter_gasket.gasket_z_range[0]      # [-6 mm](COUNTERTOP_TOP_Z)
countertop_bottom_z = countertop_top_z - countertop_thickness       # [-36 mm](COUNTERTOP_BOTTOM_Z)
under_counter_plate_thickness = 1.524  # 0.060" 316 SS, the DXF's own sidecar
# The plate's underside: the first plane below the counter a tube is free to bend on.
under_counter_plate_bottom_z = countertop_bottom_z - under_counter_plate_thickness

# Below the plate the four tubes gather under one sleeve
# (`faucet-and-umbilical.md` §3). The flavor pair holds its lower X spacing
# and touches the foam on the blue tube. D touches its opposite side.
#
# CARGEN nitrile foam, 1/4" ID × 3/8" wall, on the blue tube only — the cold run. Its OD is what the
# pack is built around and what does not pass the countertop hole, which is why the blue tube is
# entirely below the counter.
foam_od = 25.4
foam_r = foam_od / 2.0
# Where each flavour tube's axis stands in depth once it is tangent to that foam, at the X it
# already has. Same Pythagorean tangency `flavor_tube_depth_upper` is struck on, one circle out.
# [14.9102 mm](PACK_FLAVOR_DEPTH) — tangent to the foam on the blue tube.
pack_flavor_depth = math.sqrt((foam_r + flavor_tube_r) ** 2 - flavor_tube_x_offset ** 2)

# The dedicated white vent line passes between the flavor pair. Below the counter it
# steps forward past the color-change unions, then gathers against the cold-line foam.
drain_tube_r = _fi.drain_tube_od / 2.0
drain_pack_y = -math.sqrt((foam_r + drain_tube_r) ** 2 - _fi.drain_tube_x ** 2)
drain_bypass_y = 8.9
drain_tail_y = drain_pack_y - 20.0
drain_bend_radius = _fi.drain_bend_min_radius


# A WHITE FAUCET'S FLAVOUR TUBES ARE WHITE THROUGH THE FAUCET AND BLACK IN THE UMBILICAL, and a John
# Guest PP0408W union (`reference/jg-pp0408w/`) joins each white tube to its black run at the top of
# the wrap. A Black faucet's flavour tube is black end to end, on the same centreline, unjoined.
#
# THE TWO UNIONS STAND END TO END, NOT SIDE BY SIDE: a union is Ø15.1 and the pair runs tangent, 6.35
# apart, so at each union the other tube passes it. AND NEITHER STANDS BESIDE THE FOAM: a union
# against the Ø25.4 foam is 40.5 mm across, and the countertop hole the whole umbilical drops
# through is 34.93, so the foam starts below the lower one.
union = jg_pp0408w
union_length = union.OVERALL        # release sleeves out — the envelope a neighbour sees
union_ring_r = union.RING_D / 2.0
# Between the two square ends a union's tube stops hold apart — the length a Black faucet's tube runs
# on through where a White faucet's two colours meet. [9.8 mm](UNION_GAP)
union_gap = union_length - 2.0 * union.INSERTION
# The pair's axes where a union stands: its ring, the tube passing it, and the two millimetres of air
# the collars keep at the wall. [12.72 mm](UNION_PASS)
union_air = 2.0
union_pass = union_ring_r + flavor_tube_r + union_air

# FLAVOR-B STEPS OUT AND FLAVOR-A HOLDS ITS LINE. The SIG-6 ribbon comes down the +X side of the pair
# (`faucet_shell.signal_lower_exit_x`) and nothing stands on flavor-b's, so flavor-b is the one that
# moves: out along −X by what the pass is short of, off the plate's underside, as the S-bend is — two
# arcs of one radius sharing an angle. [1.825 mm](STEP_X)
step_bend_radius = 30.0
step_x = union_pass - 2.0 * flavor_tube_x_offset
step_theta_rad = math.acos(1.0 - step_x / (2.0 * step_bend_radius))
step_rise = 2.0 * step_bend_radius * math.sin(step_theta_rad)


# The flavour pair by side: flavor-a at +X, flavor-b at −X — and so a White faucet's two unions.
flavor_sides = (+1, -1)


def union_x(x_sign):
    """A flavour tube's X past the plate and down both unions: flavor-a (+X) on its own line,
    flavor-b (−X) stepped out."""
    return x_sign * flavor_tube_x_offset - (step_x if x_sign < 0 else 0.0)


# WHERE THE UNIONS STAND. Flavor-b's on the plane its step lands on, which is where the wrapped
# umbilical starts, and flavor-a's end to end below it: the stagger is one union's length.
union_b_top_z = under_counter_plate_bottom_z - step_rise    # [-52.21 mm](UNION_B_TOP_Z)
union_a_top_z = union_b_top_z - union_length                # [-94.01 mm](UNION_A_TOP_Z)
# Below the lower union neither tube stands beside one, and both turn into the pack.
union_foot_z = union_a_top_z - union_length                 # [-135.8 mm](UNION_FOOT_Z)


def union_top_z(x_sign):
    """The top port face of the union on flavor-a (+X) or flavor-b (−X)."""
    return union_a_top_z if x_sign > 0 else union_b_top_z


def upper_stop_z(x_sign):
    """Where a White faucet's white tube bottoms in its union, `INSERTION` past the top port face.
    The black run's square end stands `union_gap` below it."""
    return union_top_z(x_sign) - union.INSERTION


# THE GATHER, from where each tube stands at the unions to its place in the pack: flavor-a in depth
# alone, flavor-b in depth and back across X. Each is two arcs of one radius on the vertical plane its
# own move lies in, and both leave the plane below the lower union.
umbilical_bend_radius = 30.0


def gather_offset(x_sign):
    """How far a flavour tube moves in plan, off its line at the unions and into the pack."""
    return math.hypot(x_sign * flavor_tube_x_offset - union_x(x_sign),
                      pack_flavor_depth - flavor_tube_depth_lower)


def gather_theta(x_sign):
    """The per-arc angle absorbing `gather_offset`."""
    return math.acos(1.0 - gather_offset(x_sign) / (2.0 * umbilical_bend_radius))


def gather_rise(x_sign):
    return 2.0 * umbilical_bend_radius * math.sin(gather_theta(x_sign))


# THE PACK STARTS where the longer gather lands, and the foam and the braid's run over the pack start
# with it. [-178.3 mm](UMBILICAL_Z_BOTTOM)
drain_gather_rise = 2 * drain_bend_radius * math.sin(math.acos(
    1 - abs(drain_pack_y - drain_bypass_y) / (2 * drain_bend_radius)))
umbilical_z_bottom = union_foot_z - max(gather_rise(+1), gather_rise(-1), drain_gather_rise)

# THE FACTORY CUT, off `faucet-and-umbilical.md` §1 — what the bench cuts, installer-trim allowance
# included. The blue is measured from the shank's bottom face and the flavour pair from the printed
# tip. `main` prints where the two land against each other; what the assembly DRAWS is below.
blue_cut_length = 1540.0

# WHAT IS DRAWN IS THE TERMINATED END. Between the pack and the wall the umbilical is one straight run
# of more than a metre, and a picture of that is a line with a faucet on it. So the drawing carries
# the length that has features on it — the unions, the sleeve, the plane it stops on, and the four
# tails and their collars below that — measured down from the Westbrass's compression port, the way
# the countertop below is drawn 120 mm square rather than to a kitchen.
umbilical_drawn = 230.0

# Carbonated water arrives at the OTHER port: the compression fitting on the
# bottom of the shank, [44 mm](SODA_UMBILICAL_BELOW_COUNTER) below the countertop's top
# face, and rises inside the shank to it. So the blue tube is 1/4" and is
# entirely below the counter, where the 3/8" soda faucet tube above is not. The
# harvested Westbrass models no shank bore and no fitting, so this butts on the
# shank's own bottom face.
soda_umbilical_tube_od = flavor_tube_od
soda_umbilical_tube_r = soda_umbilical_tube_od / 2.0
soda_umbilical_tube_z_top = -shank_length
# All four tails share the termination plane.
# [-280 mm](UMBILICAL_TAIL_Z) — the square-cut end, as drawn.
umbilical_tail_z = soda_umbilical_tube_z_top - umbilical_drawn
soda_umbilical_tube_z_bottom = umbilical_tail_z

# The foam's own run on that tube (`faucet-and-umbilical.md` §3): five 1-ft segments butted from the
# pack's first plane, bare above it past both unions to the compression end, and bare again at the
# wall. `foam_length` is what the five come to; what is drawn is the run's two ends.
foam_z_top = umbilical_z_bottom
# [128.3 mm](FOAM_BARE_AT_WESTBRASS) of bare blue tube below the compression port.
foam_bare_at_westbrass = soda_umbilical_tube_z_top - foam_z_top
foam_bare_at_wall = 75.0
foam_length = blue_cut_length - foam_bare_at_westbrass - foam_bare_at_wall
foam_z_bottom = umbilical_tail_z + foam_bare_at_wall   # [-205 mm](FOAM_Z_BOTTOM)
if foam_z_bottom >= foam_z_top:
    raise ValueError(
        f"the drawn umbilical stops at Z {umbilical_tail_z:g} and leaves no foam below the pack's "
        f"first plane at Z {foam_z_top:.1f} — draw it longer")

# [14.9345 mm](FLAVOR_TUBE_DEPTH_UPPER) — tight upstream pack depth.
flavor_tube_depth_upper = port_center_depth + faucet_shell._paths.TIGHT_FLAVOR_N

# Lower centerlines use the shared smooth transition in faucet_paths.py.
# These dimensional references remain available to the assembly/document readers.
flavor_bend_radius = faucet_shell.flavor_bend_radius
_flavor_depth_offset = flavor_tube_depth_lower - flavor_tube_depth_upper
# [0.3172 rad](FLAVOR_BEND_THETA) — per-bend angle absorbing the S-bend depth offset.
flavor_bend_theta_rad = faucet_shell.flavor_bend_angle_rad

pre_bend_rise = 3.0
# [42 mm](PRE_BEND_Z) — S-bend starts here.
pre_bend_z = faucet_shell.flavor_bend_start_z


# Above the lever the shared gooseneck bends toward −Y. Soda follows its
# circular centerline; the flavor and drain paths retain their own spacing
# through the seal spread. D ends at the wet chamber. The flavor pair returns
# to its display-face spacing before the final straight.
# The tip's exit angle below horizontal = (bend1_sweep + bend2_sweep) - 90°.
lever_top_z = plateau_z + 13.0  # [52 mm](LEVER_TOP_Z)
gn_bend1_r = faucet_shell.gn_bend1_r
gn_bend2_r = faucet_shell.gn_bend2_r
gn_bend1_sweep_rad = faucet_shell.gn_bend1_sweep_rad
gn_bend2_sweep_rad = faucet_shell.gn_bend2_sweep_rad
# [172 mm](GN_BEND_MID_Z) — bend-1 midpoint, 35 mm above lever_top_z.
gn_bend1_mid_z = faucet_shell.gn_bend1_z_mid
# [153.39 mm](GN_BEND_START_Z) — bend-1 start.
gn_bend1_start_z = faucet_shell.gn_bend1_z_start
gn_mid_straight_len = faucet_shell.gn_mid_straight_len
gn_tip_straight_len = faucet_shell.gn_tip_straight_len

# Flavor tubes sit further +Y than the soda faucet tube (deeper, behind it).
# The gooseneck bends toward -Y, so the flavor tubes are on the OUTSIDE
# of every bend: they trace parallel-offset arcs sharing each bend's
# center of curvature with water, at the larger radius water_r +
# offset_depth. At the bare gooseneck radius the perpendicular component
# of the centerline separation shrinks below water_r + flavor_r and the
# tubes ride into each other through the bend.
_gn_flavor_depth_offset = flavor_tube_depth_upper - port_center_depth
# [77.8595 mm](GN_FLAVOR_BEND_ONE_R) — parallel offset of gn_bend1_r.
gn_flavor_bend1_r = gn_bend1_r + _gn_flavor_depth_offset
# [77.8595 mm](GN_FLAVOR_BEND_TWO_R) — parallel offset of gn_bend2_r.
gn_flavor_bend2_r = gn_bend2_r + _gn_flavor_depth_offset


def load_westbrass():
    """The harvested Westbrass, authored Z-up in the repo frame."""
    return import_step(str(ref_westbrass_step))


def load_above_counter_plate():
    """The printed above-counter plate, +Z-up."""
    return above_counter_plate.build_above_counter_plate()


def load_above_counter_gasket():
    """The printed-TPU above-counter gasket, +Z-up."""
    return above_counter_gasket.build_above_counter_gasket()


def load_display_cover():
    """Nominal seated cover surface, with its relaxed print supplied separately."""
    return faucet_display_cover.build_seated_display_cover()


def load_shell_pieces():
    """The two faucet-shell pieces, +Z-up, in assembled position —
    as printed, joint void and all."""
    full = faucet_shell.build_shell()
    return (
        faucet_shell.build_shell_base(full),
        faucet_shell.build_shell_tip(full),
    )


def _arc_from_tangent(start, tangent, radius, theta_rad, ccw):
    """(mid, end, end_tangent) of a 2D arc from `start` along `tangent`,
    sweeping `theta_rad` at `radius`, ccw or cw."""
    sign = +1 if ccw else -1
    if ccw:
        perp_to_tangent = (-tangent[1], tangent[0])
    else:
        perp_to_tangent = (tangent[1], -tangent[0])
    center = (start[0] + radius * perp_to_tangent[0], start[1] + radius * perp_to_tangent[1])
    rad = (start[0] - center[0], start[1] - center[1])

    def _rot(v, a):
        c, s = math.cos(a), math.sin(a)
        return (v[0] * c - v[1] * s, v[0] * s + v[1] * c)

    rad_mid = _rot(rad, sign * theta_rad / 2.0)
    rad_end = _rot(rad, sign * theta_rad)
    mid = (center[0] + rad_mid[0], center[1] + rad_mid[1])
    end = (center[0] + rad_end[0], center[1] + rad_end[1])
    end_tangent = _rot(tangent, sign * theta_rad)
    return mid, end, end_tangent


def _gooseneck_segments(start, tangent, bend1_r, bend2_r):
    """Waypoints for the four-segment gooseneck path from `start` along
    `tangent`: bend 1 (R=bend1_r, sweep=gn_bend1_sweep_rad) → mid
    straight (gn_mid_straight_len) → bend 2 (R=bend2_r,
    sweep=gn_bend2_sweep_rad) → tip straight (gn_tip_straight_len). Both
    bends turn CCW in the path's 2D frame, which tube_path_plane maps to
    a bend toward -world Y (toward the user)."""
    arc1_mid, arc1_end, tan1 = _arc_from_tangent(
        start, tangent, bend1_r, gn_bend1_sweep_rad, ccw=True
    )
    mid_end = (arc1_end[0] + gn_mid_straight_len * tan1[0],
               arc1_end[1] + gn_mid_straight_len * tan1[1])
    arc2_mid, arc2_end, tan2 = _arc_from_tangent(
        mid_end, tan1, bend2_r, gn_bend2_sweep_rad, ccw=True
    )
    tip_end = (arc2_end[0] + gn_tip_straight_len * tan2[0],
               arc2_end[1] + gn_tip_straight_len * tan2[1])
    return (arc1_mid, arc1_end), mid_end, (arc2_mid, arc2_end), tip_end


# Tube centerline paths live in the world Y-Z plane (no lateral X
# motion):
#   2D x  =  +world Y   (positive 2D x points BACK)
#   2D y  =  +world Z   (positive 2D y points UP)
tube_path_plane = cq.Plane(origin=(0, 0, 0), xDir=(0, 1, 0), normal=(1, 0, 0))


def _soda_faucet_path():
    """The soda faucet tube's centreline, in the path plane: vertical from where it bottoms in the
    Westbrass's port up to the gooseneck, then bend 1, mid straight, bend 2, tip straight."""
    p_bottom = (0.0, 0.0)
    p_gn_start = (0.0, gn_bend1_start_z - soda_faucet_tube_z_bottom)

    arc1, mid_end, arc2, tip_end = _gooseneck_segments(
        p_gn_start, (0.0, 1.0), gn_bend1_r, gn_bend2_r
    )

    path = (
        cq.Workplane(tube_path_plane)
        .moveTo(*p_bottom)
        .lineTo(*p_gn_start)
        .threePointArc(*arc1)
    )
    if gn_mid_straight_len > 0.0:
        path = path.lineTo(*mid_end)
    return path.threePointArc(*arc2).lineTo(*tip_end)


def build_soda_faucet_tube():
    """Ø soda_faucet_tube_od tube along `_soda_faucet_path`."""
    # Circular cross-section perpendicular to the path's starting +Z tangent.
    profile = cq.Workplane(xy_plane_z_up).circle(soda_faucet_tube_r)
    tube = profile.sweep(_soda_faucet_path(), transition="round")
    return tube.translate((0, +port_center_depth, soda_faucet_tube_z_bottom))


def _length(path):
    return path.wire().val().Length()


# The soda faucet tube as the bench cuts it: bottomed on the thimble's cap and square at the printed
# tip, in the faucet's finish. Rounded up, since the outlet is trimmed flush there.
soda_faucet_cut_length = float(math.ceil(_length(_soda_faucet_path())))


def _faucet_flavor_path(x_sign=1):
    """Shared production centreline: lower row, centered neck and symmetric face."""
    return cq.Workplane(obj=faucet_shell._paths.path_wire(
        "flavor",under_counter_plate_bottom_z,x_sign))


def _step_path(x_sign, bottom_z):
    """A flavor tube's centreline below the plate, down to `bottom_z` on its line at the unions: in
    `splay_path_plane`, relative to the tube's own X and the plate's underside. Flavor-b steps out
    along −X first; flavor-a, which holds its line, runs straight the whole way."""
    path = cq.Workplane(splay_path_plane).moveTo(0.0, 0.0)
    out = union_x(x_sign) - x_sign * flavor_tube_x_offset
    foot_x = 0.0
    if out:
        a1_mid, a1_end, a1_tan = _arc_from_tangent(
            (0.0, 0.0), (0.0, -1.0), step_bend_radius, step_theta_rad, ccw=(out > 0))
        a2_mid, a2_end, _a2_tan = _arc_from_tangent(
            a1_end, a1_tan, step_bend_radius, step_theta_rad, ccw=(out < 0))
        path = path.threePointArc(a1_mid, a1_end).threePointArc(a2_mid, a2_end)
        foot_x = a2_end[0]
    return path.lineTo(foot_x, bottom_z - under_counter_plate_bottom_z)


def _gather_plane(x_sign):
    """The vertical plane a flavor tube's gather lies in: 2D x along its move into the pack, 2D y
    world Z."""
    dx = x_sign * flavor_tube_x_offset - union_x(x_sign)
    dy = pack_flavor_depth - flavor_tube_depth_lower
    ux, uy = dx / gather_offset(x_sign), dy / gather_offset(x_sign)
    return cq.Plane(origin=(0, 0, 0), xDir=(ux, uy, 0), normal=(uy, -ux, 0))


def _gather_path(x_sign, top_z):
    """A flavor tube's centreline from `top_z` on its line at the unions down to `splay_top_z` in the
    pack, in its gather's plane and relative to its union X and `union_foot_z`: straight down to the
    foot, two arcs across into the pack, straight on down."""
    g1_mid, g1_end, g1_tan = _arc_from_tangent(
        (0.0, 0.0), (0.0, -1.0), umbilical_bend_radius, gather_theta(x_sign), ccw=True)
    g2_mid, g2_end, _g2_tan = _arc_from_tangent(
        g1_end, g1_tan, umbilical_bend_radius, gather_theta(x_sign), ccw=False)
    # A line of no length is not an edge: measured from the foot itself, the run starts on the arc.
    path = cq.Workplane(_gather_plane(x_sign)).moveTo(0.0, top_z - union_foot_z)
    if top_z - union_foot_z > 1e-9:
        path = path.lineTo(0.0, 0.0)
    return (path.threePointArc(g1_mid, g1_end).threePointArc(g2_mid, g2_end)
            .lineTo(g2_end[0], splay_top_z - union_foot_z))


def flavor_centerlines(x_sign):
    """Every piece of one flavor tube's centreline, tip to tail, as the paths its sweeps run: the
    faucet's run, the step to its line at the unions, the gather into the pack, the splay at the
    wall."""
    return (_faucet_flavor_path(x_sign), _step_path(x_sign, union_foot_z),
            _gather_path(x_sign, union_foot_z), _splay_path(x_sign))


def flavor_faucet_run_length(x_sign):
    """Flavor centreline from the printed tip to where a White faucet's white tube bottoms in its
    union."""
    return _length(_faucet_flavor_path(x_sign)) + _length(_step_path(x_sign, upper_stop_z(x_sign)))


def flavor_path_above_pack(x_sign):
    """Flavor centreline from the printed tip to the pack's first plane."""
    in_pack = (union_foot_z - gather_rise(x_sign)) - umbilical_z_bottom
    return (_length(_faucet_flavor_path(x_sign)) + _length(_step_path(x_sign, union_foot_z))
            + 2.0 * umbilical_bend_radius * gather_theta(x_sign) + in_pack)


def flavor_path_above_foot():
    """Flavor centreline above the shell foot — the faucet's run less its straight below Z = 0."""
    return _length(_faucet_flavor_path()) + under_counter_plate_bottom_z


flavor_tube_z_bottom = umbilical_tail_z
flavor_tube_z_top = soda_faucet_tube_z_top


# The lane the SIG-6 ribbon rides in, between the tube pack and the braid's inner face. The braid
# stands off every tube in the pack by it.
#
# One 28 AWG silicone conductor's OD, which is the ribbon's own thickness — four conductors lie
# side by side and none stands over another. BNTECHGO states the section 1.2 x 4 mm +/- 0.1 for
# B07PNPHWMG (`ledger/bom.md` §9), so the lane is that 1.2 and the ribbon is 4 wide across it.
# Vendor figure, not a caliper: the spool is on the shelf and a measurement across it still refines
# this to the tolerance's own width.
cable_lane = faucet_shell.signal_ribbon_max_depth
# The ribbon across its four conductors, off the same BNTECHGO figure.
cable_width = faucet_shell.signal_ribbon_max_width
sleeve_wall = 1.0


def build_display_ribbon():
    """The SIG-6 cable's maximum stated 4.1 × 1.3 mm envelope through the faucet.

    The lower handoff passes through the mounting stack; the upper end reaches the
    factory fan-out beside the PCB, 0.30 mm below its measured underside.
    """
    parts = [
        faucet_shell.build_lower_signal_ribbon().val(),
        faucet_shell.build_signal_transition_ribbon().val(),
        faucet_shell.build_display_ribbon_transition().val(),
    ]
    joined=parts[0].fuse(*parts[1:],tol=1e-5)
    if not joined.isValid() or len(joined.Solids())!=1:
        raise ValueError("the joined ribbon and four peeled conductors must form one continuous envelope")
    return cq.Workplane(obj=joined)


def build_vent_seal(upstream=True):
    import vent_seals
    p=faucet_shell._paths
    station=p.UPSTREAM_GLAND_S if upstream else p.DOWNSTREAM_GLAND_S
    return faucet_shell._gland_world(vent_seals.build_installed_bung(upstream),station)


def bundle_hull(grow: float = 0.0) -> cq.Sketch:
    """The pack's outline, standing `grow` off every tube in it.

    A braid lies on the tubes it is drawn over and bridges tangent between them: its inner face is
    this outline at `cable_lane` and its outer the same at `cable_lane` plus `sleeve_wall`.

    Growing every circle by `grow` offsets the hull by it — the boundary is arcs and the tangents
    between them, and a common growth carries each arc out and leaves each tangent where it lies."""
    return (
        cq.Sketch()
        .arc((0.0, 0.0), foam_r + grow, 0.0, 360.0)
        .arc((+flavor_tube_x_offset, pack_flavor_depth), flavor_tube_r + grow, 0.0, 360.0)
        .arc((-flavor_tube_x_offset, pack_flavor_depth), flavor_tube_r + grow, 0.0, 360.0)
        .arc((_fi.drain_tube_x, drain_pack_y), drain_tube_r + grow, 0.0, 360.0)
        .hull()
    )


def gather_hull(grow: float = 0.0) -> cq.Sketch:
    """Clearance envelope below the unions, over the tube gathers and foam start."""
    circles = [(0.0, 0.0, foam_r + grow)]
    circles += [(x, y, flavor_tube_r + grow) for x, y in
                ((union_x(+1), flavor_tube_depth_lower),
                 (union_x(-1), flavor_tube_depth_lower),
                 (+flavor_tube_x_offset, pack_flavor_depth),
                 (-flavor_tube_x_offset, pack_flavor_depth))]
    circles += [(_fi.drain_tube_x, y, drain_tube_r + grow)
                for y in (drain_pack_y, drain_bypass_y)]
    # A circle wholly inside another cannot contribute to the convex boundary.
    # Remove it before CadQuery's arc-tangent hull calculation.
    boundary = [circle for i, circle in enumerate(circles) if not any(
        j != i and math.hypot(circle[0]-other[0], circle[1]-other[1])
        + circle[2] <= other[2] + 1e-9
        for j, other in enumerate(circles))]
    sketch = cq.Sketch()
    for x, y, radius in boundary:
        sketch = sketch.arc((x, y), radius, 0.0, 360.0)
    return sketch.hull()


@functools.lru_cache(maxsize=None)
def _hull_face(grow: float):
    """`bundle_hull(grow)` as one planar face, read off the floor of a prism raised on it."""
    return (cq.Workplane(xy_plane_z_up).placeSketch(bundle_hull(grow))
            .extrude(1.0).faces("<Z").val())


def bundle_girth(grow: float = None) -> float:
    """The perimeter the braid closes on, and the figure a braid is bought by."""
    return max(w.Length() for w in _hull_face(cable_lane if grow is None else grow).Wires())


def bundle_bore() -> float:
    """That perimeter as the diameter of the circle carrying it — the size a braid opens to."""
    return bundle_girth() / math.pi


def union_hull(grow: float = 0.0) -> cq.Sketch:
    """The outline over the unions' stretch, standing `grow` off everything in it: the bare blue tube
    and both unions, each union's footprint held down the whole stretch as the braid over the two
    is. Every flavour tube there stands inside one union's circle or the other's."""
    return (
        cq.Sketch()
        .arc((0.0, 0.0), soda_umbilical_tube_r + grow, 0.0, 360.0)
        .arc((union_x(+1), flavor_tube_depth_lower), union_ring_r + grow, 0.0, 360.0)
        .arc((union_x(-1), flavor_tube_depth_lower), union_ring_r + grow, 0.0, 360.0)
        .arc((_fi.drain_tube_x, drain_bypass_y), drain_tube_r + grow, 0.0, 360.0)
        .hull()
    )


def union_girth() -> float:
    """The perimeter the braid closes on over the unions, beside `bundle_girth` over the pack. The
    braid is bought by the larger of the two."""
    face = (cq.Workplane(xy_plane_z_up).placeSketch(union_hull(cable_lane))
            .extrude(1.0).faces("<Z").val())
    return max(w.Length() for w in face.Wires())


# [2.0270 mm](SLEEVE_CENTER_Y) behind the Westbrass's axis — the pack's own centre of area, which is what
# a collar's flag is turned away from. Ø[33.08 mm](SLEEVE_BORE) is what the braid opens to over it
# — a 1" nominal PET braid that expands 50% (`ledger/bom.md` §11; the wall above is the figure the
# assembly draws it at).
sleeve_center_y = _hull_face(cable_lane).Center().y
# THE BRAID'S RUN IS THE FOAM'S, AND THE TOP ONE GOES ON OVER THE UNIONS. One braid segment goes over
# each foam segment as that segment seats (`faucet-and-umbilical.md` §3), so the two stop on one
# plane at the wall and the installer's trim takes one of each; the top segment runs on above its
# foam over both unions, to the plane the upper one starts on. What that leaves bare at the wall is
# `foam_bare_at_wall`, where the installer flexes the three apart and pushes each into its own union.
sleeve_z_top = union_b_top_z
sleeve_z_bottom = foam_z_bottom
# THE TAILS COME APART BEFORE THE COLLARS GO ON. The +Y wall of back-top does not take this
# triangle — the installer flexes the three apart in the un-sleeved stretch and pushes each into its
# own union (`faucet-and-umbilical.md` §3) — and the collars need the same room: two of them clear
# when their tubes' axes stand further apart than the two reach. The flavour pair splays in X until
# the TIGHTEST of the three pairs makes that, which is a flavour tube against the blue standing
# forward of them, not the two flavours against each other.
collar_air = 2.0
_tails_clear = 2.0 * tube_collar.reach() + collar_air
# [13.372 mm](TAIL_HALF_X) — each flavour tail's own X, off the Westbrass's axis.
tail_half_x = max(_tails_clear / 2.0,
                  math.sqrt(max(0.0, _tails_clear ** 2 - pack_flavor_depth ** 2)))
# The splay, as the gather and the S-bend are: two arcs of one radius sharing an angle.
splay_bend_radius = 30.0
# [0.6497 rad](SPLAY_THETA) — per-arc angle absorbing the lateral the pair comes out by.
splay_theta_rad = math.acos(
    1.0 - (tail_half_x - flavor_tube_x_offset) / (2.0 * splay_bend_radius))
# What it spends of the un-sleeved stretch getting there.
splay_rise = 2.0 * splay_bend_radius * math.sin(splay_theta_rad)

# Where the sleeve lets go and the splay takes over — one plane, so nothing runs bare and straight
# between them.
splay_top_z = sleeve_z_bottom
# WHERE THE THREE COLLARS HANG, level with each other, on the first plane below the splay — a bore
# is straight and a tube coming out of a bend is not, so no collar stands in one.
drain_splay_rise = 2 * drain_bend_radius * math.sin(
    math.acos(1 - abs(drain_tail_y - drain_pack_y) / (2 * drain_bend_radius)))
drain_splay_top_z = splay_top_z
collar_top_z = splay_top_z - max(splay_rise, drain_splay_rise)


# The splay's own plane: 2D x is world X and 2D y is world Z, so the pair comes apart across the
# bundle while `tube_path_plane` above works in depth. Both are the S-bend, on their own axis.
splay_path_plane = cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, -1, 0))


def _splay_path(x_sign):
    """One flavour tail's centreline through the splay, in `splay_path_plane` and relative to the
    tube's own X and to `splay_top_z`: straight down out of the sleeve is where it starts, two arcs
    carry it out to `tail_half_x`, and it runs straight from there to the cut end."""
    start = (0.0, 0.0)
    a1_mid, a1_end, a1_tan = _arc_from_tangent(
        start, (0.0, -1.0), splay_bend_radius, splay_theta_rad, ccw=(x_sign > 0))
    a2_mid, a2_end, _a2_tan = _arc_from_tangent(
        a1_end, a1_tan, splay_bend_radius, splay_theta_rad, ccw=(x_sign < 0))
    foot = (a2_end[0], umbilical_tail_z - splay_top_z)
    return (
        cq.Workplane(splay_path_plane)
        .moveTo(*start)
        .threePointArc(a1_mid, a1_end)
        .threePointArc(a2_mid, a2_end)
        .lineTo(*foot)
    )


# Every bend spends more tube than its vertical drop. The factory cut
# includes this splay and the complete route above the pack.
splay_extra_length = (_splay_path(+1).wire().val().Length()
                     - (splay_top_z - umbilical_tail_z))
# ONE CUT FOR THE PAIR, off the longer route — flavor-b's, which steps out and comes back. It is
# the Black faucet's whole flavour tube, and the White faucet's two colours and union come to it.
flavor_cut_length = float(math.ceil(
    blue_cut_length + max(flavor_path_above_pack(+1), flavor_path_above_pack(-1))
    + splay_extra_length + umbilical_z_bottom - soda_umbilical_tube_z_top))


def tail_z(x_sign):
    """Where a flavour tube cut at `flavor_cut_length` would end, hung straight below the pack."""
    return umbilical_z_bottom - (flavor_cut_length - flavor_path_above_pack(x_sign)
                                 - splay_extra_length)


# [0.5931 mm](TAILS_APART) — how far apart the three tails land: the flavor cut's rounding to a
# whole millimetre, and flavor-a's shorter route against the one cut both take.
_tail_planes = (soda_umbilical_tube_z_top - blue_cut_length, tail_z(+1), tail_z(-1))
tails_apart = max(_tail_planes) - min(_tail_planes)


def white_cut_length(x_sign):
    """A White faucet's white flavour tube, printed tip to its union's tube stop — rounded up, since
    the outlet is trimmed flush at the tip."""
    return float(math.ceil(flavor_faucet_run_length(x_sign)))


def black_run_cut_length(x_sign):
    """The black run a White faucet's union joins it to: the Black faucet's cut less the white tube
    and the gap between the union's two tube stops, so its tail lands where a Black faucet's does."""
    return float(math.ceil(flavor_cut_length - flavor_faucet_run_length(x_sign) - union_gap))


def _flavor_tube(path, start_z=0.0):
    """A 1/4" tube swept along `path`. A SWEEP CARRIES ITS PROFILE FROM WHERE THE PROFILE STANDS and
    not from the spine's first point, so the profile stands at the spine's start, `start_z` up the
    path's own Z."""
    return (cq.Workplane(xy_plane_z_up).workplane(offset=start_z).circle(flavor_tube_r)
            .sweep(path, transition="round"))


def build_flavor_faucet_run(x_sign):
    """One flavour tube's run through the faucet: the printed tip down to where a White faucet's white
    tube bottoms in its union — white on a White faucet, black on a Black one. x_sign ∈ {±1} selects
    flavor-a (+X) or flavor-b (−X).

    TWO SWEEPS, FUSED ON ONE TANGENT at the plate's underside. The faucet's run works in depth and
    nothing else, which is the plane `_faucet_flavor_path` is drawn on; the step below it works across
    the bundle, which is another. Both leave the joining plane running straight, so the two meet on
    one tangent and the fuse leaves no corner."""
    at_plate = (x_sign*flavor_tube_x_offset,flavor_tube_depth_lower,under_counter_plate_bottom_z)
    path=_faucet_flavor_path(x_sign)
    plane=cq.Plane(origin=at_plate,xDir=(1,0,0),normal=(0,0,1))
    faucet=cq.Workplane(plane).circle(flavor_tube_r).sweep(path,transition="round")
    step=_flavor_tube(_step_path(x_sign,upper_stop_z(x_sign))).translate(at_plate)
    return faucet.union(step)


def build_flavor_union(x_sign):
    """A White faucet's PP0408W on one flavour tube, off the reference's own file, on the tube's line
    at the unions with its top port face at `union_top_z`."""
    return import_step(str(union.STEP)).translate((
        union_x(x_sign), flavor_tube_depth_lower, union_top_z(x_sign) - union.port_face_z))


def build_flavor_bridge(x_sign):
    """What a Black faucet's flavour tube runs through where a White faucet has its union: the
    `union_gap` between the union's two tube stops, as tube."""
    return (cq.Workplane("XY").workplane(offset=upper_stop_z(x_sign) - union_gap)
            .center(union_x(x_sign), flavor_tube_depth_lower)
            .circle(flavor_tube_r).extrude(union_gap))


def build_flavor_umbilical_run(x_sign):
    """One flavour tube's black run in the umbilical, from the union's lower tube stop to the square-cut
    tail — black on either finish.

    TWO SWEEPS, FUSED ON ONE TANGENT where the sleeve lets go: the gather into the pack and the run
    down it on the gather's own plane, then the splay across the bundle."""
    stop_z = upper_stop_z(x_sign) - union_gap
    gather = (_flavor_tube(_gather_path(x_sign, stop_z), stop_z - union_foot_z)
              .translate((union_x(x_sign), flavor_tube_depth_lower, union_foot_z)))
    tail = (_flavor_tube(_splay_path(x_sign))
            .translate((x_sign * flavor_tube_x_offset, pack_flavor_depth, splay_top_z)))
    return gather.union(tail)


def build_flavor_tube(x_sign):
    """One Ø 1/4" flavor tube tip to tail as a Black faucet runs it, black end to end: the faucet's
    run, the bridge and the umbilical's run, fused. The two tubes mirror across X = 0 through the
    faucet and the pack; below the plate flavor-b steps out and back."""
    return (build_flavor_faucet_run(x_sign)
            .union(build_flavor_bridge(x_sign))
            .union(build_flavor_umbilical_run(x_sign)))


def _drain_lower_path():
    """Continuous R25 route around the two flavor unions and into the sleeve."""
    plane = cq.Plane(origin=(_fi.drain_tube_x, 0, 0), xDir=(0, 1, 0), normal=(1, 0, 0))
    path = cq.Workplane(plane).moveTo(drain_tail_y, umbilical_tail_z)
    def rise(dy):
        theta = math.acos(1 - abs(dy) / (2 * drain_bend_radius))
        return 2 * drain_bend_radius * math.sin(theta)
    current_y = drain_tail_y
    for target_y, top_z in ((drain_pack_y, drain_splay_top_z),
                           (drain_bypass_y, union_foot_z),
                           (flavor_tube_depth_lower, under_counter_plate_bottom_z)):
        start = (current_y, top_z - rise(target_y - current_y))
        path = path.lineTo(*start)
        theta = math.acos(1 - abs(target_y - current_y) / (2 * drain_bend_radius))
        turn = target_y < current_y
        mid, end, tangent = _arc_from_tangent(start, (0, 1), drain_bend_radius, theta, turn)
        path = path.threePointArc(mid, end)
        mid, end, _tangent = _arc_from_tangent(end, tangent, drain_bend_radius, theta, not turn)
        path = path.threePointArc(mid, end)
        current_y = target_y
    return path.wire().val()


def drain_path():
    lower = _drain_lower_path()
    upper = faucet_shell.build_drain_neck_path(bottom_z=under_counter_plate_bottom_z)
    upper = upper.val() if hasattr(upper, "val") else upper
    return cq.Wire.assembleEdges(lower.Edges() + upper.Edges())


def drain_factory_cut_length():
    """Complete external factory run, including the supplied cabinet/service reach."""
    return float(math.ceil(drain_path().Length()+blue_cut_length-umbilical_drawn))


def build_drain_tube(envelope=False):
    """4 mm OD / 2.5 mm ID white LLDPE, tail to the separate underside outlet."""
    profile = (cq.Workplane("XY").workplane(offset=umbilical_tail_z)
               .center(_fi.drain_tube_x, drain_tail_y).circle(drain_tube_r))
    if not envelope:
        profile = profile.circle(_fi.drain_tube_id / 2)
    return profile.sweep(cq.Workplane(obj=drain_path()), transition="round")


# Nominal clearance-animation axis, parallel to world X. This is not a measured
# pin hinge: the donor lever seats down and forward around the valve cylinder,
# and the installed soda tube blocks its aft disengagement. The assembled
# contact motion is not yet measured; see faucet-shell/ASSEMBLY.md.
lever_pivot_y = +1.5
lever_pivot_z = plateau_z + 7.0
lever_press_angle_deg = 18.0


def build_lever_at(angle_deg=0.0):
    """Dimensioned donor-lever stand-in at a nominal clearance pose.

    Geometry:
      - The lever's body is a 13 (X) × 15 (Y) × 12 (Z) box,
        centered laterally on X = 0, spanning depth Y = [-6, +9]
        (back end at +Y abutting the Westbrass, front face at Y = -6 where
        the user presses), at height Z = [plateau_z+1, plateau_z+13].
      - From the front face it tapers forward as a 13 × shrinking-Z
        tongue out to Y = -42 — the handle toward the user.
      - The pivot axis is parallel to world X (lateral), through
        (X = 0, Y = +1.5, Z = plateau_z + 7), so the lever rotates in
        the Y-Z plane (no lateral motion).
    """
    # Soda-faucet-tube clearance through the lever. That tube sits at
    # world Y = +port_center_depth; this cut is 0.125 mm further +Y for
    # margin, vertical along +Z, 50 mm tall to span both lever positions.
    cut_cylinder = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=plateau_z + 1)
        .moveTo((0, +(port_center_depth + 0.125)))
        .circle(soda_faucet_tube_r + 1)
        .extrude(50)
        .unwrap()
    )

    # Tapered tongue extending forward (toward -Y, the user) from the
    # lever's front face, narrowing in Z. First rect at the front face
    # (Y = -6): 13 (X) × 8.5 (Z), bottom-anchored so its top edge sits at
    # plateau_z+13. Second rect 36 mm further forward (Y = -42): 13 × 3,
    # bottom-anchored so its top edge stays at plateau_z+13 and its
    # bottom edge rises from plateau_z+4.5 to plateau_z+10.
    #
    # Plane: xDir=(1,0,0), normal=(0,-1,0) (perpendicular to world -Y,
    # offset advances toward -Y). localY = +Z world. Sketch local (x, y)
    # maps to world (x, -offset, y).
    _taper_plane = cq.Plane(
        origin=(0, 0, 0),
        xDir=(1, 0, 0),
        normal=(0, -1, 0),
    )
    add_taper = (
        cq.Workplane(_taper_plane)
        .workplane(offset=6)
        .moveTo(0, plateau_z + 4.5)
        .rect(13, 8.5, centered=(True, False))
        .workplane(offset=36)
        .moveTo(0, plateau_z + 10)
        .rect(13, 3, centered=(True, False))
        .loft(combine=True)
    )

    # Bare lever in the rest position — 13 (X) × 15 (Y) footprint,
    # 12 (Z) tall, no clearance cuts.
    base_lever = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=plateau_z + 1)
        .moveTo((0, +1.5))
        .rect(13, 15)
        .extrude(12)
        .unwrap()
        .union(add_taper)
    )

    # Pivot axis along +X through (0, lever_pivot_y, lever_pivot_z):
    # rotating +lever_press_angle_deg drops the front tongue toward -Z.
    pivot_a = (0, lever_pivot_y, lever_pivot_z)
    pivot_b = (1, lever_pivot_y, lever_pivot_z)

    lever_rest = base_lever.cut(cut_cylinder)

    # The soda-faucet-tube cut is vertical in world +Z, so it clears the
    # upright tube in the pressed (tilted) position too.
    lever_pressed = lever_rest.rotate(pivot_a, pivot_b, +lever_press_angle_deg).cut(cut_cylinder)
    lever_rest_final = lever_pressed.rotate(pivot_a, pivot_b, -lever_press_angle_deg)

    return lever_rest_final.rotate(pivot_a, pivot_b, angle_deg)


def build_lever():
    """The retained donor lever in its rest position."""
    return build_lever_at(0.0)


def build_base_screw(x, y):
    """M3 socket-head screw in its installed position; thread is a cylinder."""
    f = faucet_shell
    seat = f.base_screw_seat_z
    shaft = cq.Workplane("XY").workplane(offset=seat).center(x, y).circle(1.5).extrude(f.base_screw_length)
    head_bottom = seat - f.base_screw_head_height
    head = cq.Workplane("XY").workplane(offset=head_bottom).center(x, y).circle(2.75).extrude(f.base_screw_head_height)
    socket = cq.Workplane("XY").workplane(offset=head_bottom - 0.1).center(x, y).polygon(6, 2.5 / math.cos(math.pi / 6)).extrude(1.6)
    return shaft.union(head).cut(socket)


def build_base_insert(x, y):
    """Actual insert outside diameter after heat setting; knurl omitted."""
    f = faucet_shell
    return (cq.Workplane("XY").workplane(offset=f.base_insert_bottom_z)
            .center(x, y).circle(f.base_insert_outer_dia / 2).circle(1.5)
            .extrude(f.base_insert_length))


# Faucet display — Waveshare ESP32-S3-Touch-LCD-1.47 (BOM §1),
# modeled as a dimensioned stand-in. Device dims live in
# _faucet_interface, shared with the shell's display cradle (table in
# display-reference/README.md). Component envelopes below the PCB come
# from the vendor model, with their heights corrected to the measured
# PCB underside. The metal feet retain their measured zero datum.
#
# Native frame: X = width, Y = length, Z = outward thickness; the feet
# plane at z = 0, screen faces +Z. The long axis follows the tip and
# the screen faces the user. Four printed pads carry the feet; the
# component spaces remain open to the tube passages. The bezel's
# lower enclosure rim lies in the dispense plane.
display_pocket_inset = faucet_shell.display_pocket_inset
# Active (lit) display area, on the front face.
display_screen_width = 17.75
display_screen_length = 32.93
display_screen_depth = 0.4

_display_component_path = (Path(__file__).resolve().parents[1]
                           / "reference/touch-flo-faucet/display-reference/component-envelopes.json")
_display_components = json.loads(_display_component_path.read_text())
if abs(_display_components["measured_pcb_underside_above_feet_mm"] - display_pcb_bottom_z) > 1e-6:
    raise ValueError("display component envelopes need the current measured PCB height")


def build_display_components_native():
    """Conservative underside component envelopes in the display's native frame."""
    bodies = []
    for row in _display_components["components"]:
        cylinder = row.get("conservative_cylinder")
        if cylinder is not None:
            x, y = cylinder["center_xy_mm"]
            bottom, top = cylinder["z_mm"]
            bodies.append(cq.Solid.makeCylinder(cylinder["radius_mm"], top - bottom,
                                               cq.Vector(x, y, bottom)))
            continue
        low, high = row["bounds_mm"]
        # The envelope extends to the PCB underside; tiny vendor solder gaps
        # are contained within the same conservative component column.
        top = max(high[2], display_pcb_bottom_z + 0.02)
        bodies.append(cq.Solid.makeBox(high[0] - low[0], high[1] - low[1],
                                      top - low[2], cq.Vector(*low)))
    return cq.Workplane(obj=cq.Compound.makeCompound(bodies))


def _tip_centerline_world():
    """(tip_start, tip_end) of the soda faucet tube's dispense-tip straight in world coords."""
    p_gn_start = (0.0, gn_bend1_start_z - soda_faucet_tube_z_bottom)
    _, _, arc2, tip_end = _gooseneck_segments(
        p_gn_start, (0.0, 1.0), gn_bend1_r, gn_bend2_r
    )
    def to_world(p):
        return cq.Vector(0.0, p[0] + port_center_depth, p[1] + soda_faucet_tube_z_bottom)
    return to_world(arc2[1]), to_world(tip_end)


def _seat_on_tip(part):
    """Place a display part (native frame: X width, Y length, Z outward
    with the feet plane at z = 0) onto the dispense tip. The tip straight
    runs (gn_bend1_sweep + gn_bend2_sweep − 90°) below horizontal;
    rotating that angle about world X lays the part's length up the
    gooseneck and turns its screen (+Z) up toward the user. It is then
    offset out along the tip's top normal to the four feet pads. The
    feet datum and display center come from the shell's shared display
    constants, which leave 2 mm stock behind the dispense plane.
    """
    tip_below_horiz_rad = (gn_bend1_sweep_rad + gn_bend2_sweep_rad) - math.pi / 2.0
    tip_end, up_gooseneck, top_normal = faucet_shell._tip_frame()
    seat = (
        tip_end
        + top_normal.multiply(faucet_shell.display_floor_n)
        + up_gooseneck.multiply(
            display_housing_length / 2.0
            + faucet_shell.display_s_bottom
            + faucet_shell.display_cradle_clearance
        )
    )
    return (
        part
        .rotate((0, 0, 0), (1, 0, 0), math.degrees(tip_below_horiz_rad))
        .translate(seat.toTuple())
    )


def _screen_pocket():
    """Active-area recess in the front face so the screen solid mates flush."""
    z0 = display_total_depth - display_screen_depth
    return (
        cq.Workplane("XY").workplane(offset=z0)
        .box(display_screen_width, display_screen_length, display_screen_depth + 1.0, centered=(True, True, False))
        .edges("|Z").fillet(2.0)
    )


def build_display_body():
    """Caliper-sized housing/PCB with individual underside component bounds."""
    pcb = (
        cq.Workplane("XY").workplane(offset=display_pcb_bottom_z)
        .box(display_pcb_width, display_pcb_length,
             display_pcb_top_z - display_pcb_bottom_z,
             centered=(True, True, False))
        .edges("|Z").fillet(display_pcb_corner_r)
    )
    housing = (
        cq.Workplane("XY").workplane(offset=display_pcb_top_z)
        .box(display_housing_width, display_housing_length,
             display_total_depth - display_pcb_top_z, centered=(True, True, False))
        .edges("|Z").fillet(display_corner_r)
    )
    parts = [pcb.val(), housing.val(), *build_display_components_native().val().Solids()]
    body = cq.Workplane(obj=parts[0].fuse(*parts[1:])).cut(_screen_pocket())
    return _seat_on_tip(body)


def build_display_screen():
    """Active (lit) display area, flush in the front face."""
    z0 = display_total_depth - display_screen_depth
    screen = (
        cq.Workplane("XY").workplane(offset=z0)
        .box(display_screen_width, display_screen_length, display_screen_depth, centered=(True, True, False))
        .edges("|Z").fillet(2.0)
    )
    return _seat_on_tip(screen)


# --- below the counter -------------------------------------------------------
#
# The slab, at `countertop_thickness` under the stack, drawn `countertop_slab_xy` square, which is
# enough to read as a slab around the under-counter plate.
countertop_slab_xy = 120.0

hole_radius = countertop_hole_diameter / 2.0


def shank_hole_margin(center_y):
    """Slab left between the drilled hole and the shank, at a hole on the
    Westbrass's axis' own X and `center_y` in depth."""
    return hole_radius - (abs(center_y) + shank_od / 2.0)


def flavor_hole_margin(center_y):
    """The same for the flavor pair — measured to the far tube's far wall."""
    reach = math.hypot(flavor_tube_x_offset, flavor_tube_depth_lower - center_y)
    return hole_radius - (reach + flavor_tube_r)


def seated_hole_center_y():
    """Seat the four tube bundle in the existing 1-3/8-inch accessory hole."""
    return max(
        flavor_tube_depth_lower - math.sqrt((hole_radius - radius) ** 2 - x ** 2)
        for x, radius in ((flavor_tube_x_offset, flavor_tube_r),
                          (_fi.drain_tube_x, drain_tube_r)))


# [5.715 mm](HOLE_CENTER_Y) behind the Westbrass's axis, once it is back against the wall.
countertop_hole_center_y = seated_hole_center_y()
# [6.25 mm](HOLE_MARGIN) of slab forward of the shank — the play the faucet has
# left to give, which is what lets the gasket cover the hole behind it.
countertop_hole_margin = shank_hole_margin(countertop_hole_center_y)


def gasket_hole_cover():
    """Narrowest gasket band outside the drilled hole, around the whole oval."""
    gasket_bottom = above_counter_gasket.build_above_counter_gasket().faces("<Z").val()
    hole_center = cq.Vertex.makeVertex(0.0, countertop_hole_center_y, gasket_bottom.Center().z)
    return gasket_bottom.outerWire().distance(hole_center) - hole_radius


def build_countertop():
    """The slab the stack clamps through, with its drilled hole."""
    slab = (
        cq.Workplane("XY").workplane(offset=countertop_bottom_z)
        .box(countertop_slab_xy, countertop_slab_xy, countertop_thickness,
             centered=(True, True, False))
    )
    hole = (
        cq.Workplane("XY").workplane(offset=countertop_bottom_z - 1.0)
        .center(0, countertop_hole_center_y)
        .circle(hole_radius)
        .extrude(countertop_thickness + 2.0)
    )
    return slab.cut(hole)


def build_under_counter_plate():
    """The cut plate, off the DXF the laser reads, at the slab's underside.

    That DXF's own X is world depth and its Y is world lateral (see the part's
    docstring), so the outline turns a quarter about Z on its way into this
    frame: DXF (x, y) lands at world (-y, x), which puts the pill pocket at
    world +Y over the flavor pair and opens both channels toward +X."""
    outline = cq.importers.importDXF(str(under_counter_dxf))
    plate = outline.wires().toPending().extrude(under_counter_plate_thickness)
    return (
        plate
        .rotate((0, 0, 0), (0, 0, 1), 90.0)
        .translate((0, 0, countertop_bottom_z - under_counter_plate_thickness))
    )


def build_o_ring():
    """The printed TPU thimble sealing the soda faucet tube into the Westbrass's
    Ø10 top port. Its Z = 0 face is the port floor and the tube bottoms on its
    cap, so the cap's top face is where the soda faucet tube starts."""
    return tpu_o_ring.build_o_ring().translate((
        0,
        +port_center_depth,
        soda_faucet_tube_z_bottom - tpu_o_ring.cap_thickness,
    ))


def build_soda_umbilical_tube(bottom_z=None):
    """The blue 1/4" soda umbilical tube, butted on the shank's bottom face and running down.
    It is on the Westbrass's own axis the whole way, so it takes no part in the gather — the
    flavour pair comes to IT."""
    bottom_z = umbilical_tail_z if bottom_z is None else bottom_z
    return (
        cq.Workplane("XY").workplane(offset=bottom_z)
        .circle(soda_umbilical_tube_r)
        .extrude(soda_umbilical_tube_z_top - bottom_z)
    )


def build_foam():
    """The CARGEN segments on the blue tube, drawn as the one sleeve their butts make.

    Five 1-ft lengths butted end to end (`faucet-and-umbilical.md` §3), bare at the compression end
    where the tube lands on the Westbrass and bare again at the wall, where the installer's
    trim takes a whole segment off in a nominal kitchen."""
    return (
        cq.Workplane("XY").workplane(offset=foam_z_bottom)
        .circle(foam_r).circle(soda_umbilical_tube_r)
        .extrude(foam_z_top - foam_z_bottom)
    )


def build_sleeve():
    """The braid over the assembled bundle: over both unions from the upper one's top, and over the
    pack from the foam's first plane down to its last.

    What it leaves bare at the bottom is what the installer flexes apart to reach three bulkheads
    standing on one line, and it is where the collars ride.

    DRAWN AS ONE RUN AND FITTED IN SEGMENTS — five of them, one to each of the foam's, the top one
    carried on up over the unions. It lies on what is inside it, so it steps where the foam starts:
    over the unions' outline above that plane and the pack's below it."""
    def sleeve(hull, z_bottom, z_top):
        def prism(grow):
            return (cq.Workplane(xy_plane_z_up).workplane(offset=z_bottom)
                    .placeSketch(hull(grow)).extrude(z_top - z_bottom))
        return prism(cable_lane + sleeve_wall).cut(prism(cable_lane))
    return (sleeve(union_hull, union_foot_z, sleeve_z_top)
            .union(sleeve(gather_hull, umbilical_z_bottom, union_foot_z))
            .union(sleeve(bundle_hull, sleeve_z_bottom, umbilical_z_bottom)))


def build_collar(which, x, y):
    """One tube collar threaded onto the tube at `(x, y)`, as `(collar, word)`.

    The part's own +Y is outboard along its tube, which here is DOWN toward the tail: a quarter turn
    about X lays that on −Z and stands the flag on +Y, and a turn about Z then points the flag out
    of the bundle, away from `sleeve_center_y`, so no two of the three face each other."""
    bodies = tube_collar.split(import_step(str(tube_collar.STEPS[which])).val())
    ux, uy = x - 0.0, y - sleeve_center_y
    reach = math.hypot(ux, uy)
    azimuth = math.degrees(math.atan2(-ux / reach, uy / reach))
    return tuple(
        body.rotate((0, 0, 0), (1, 0, 0), -90.0)
            .rotate((0, 0, 0), (0, 0, 1), azimuth)
            .translate((x, y, collar_top_z))
        for body in bodies
    )


def umbilical_collars():
    """The three collars the bench threads on, as `(name, solid, colour)` — one per tail, each in
    the filament its chip on the +Y wall of back-top prints in."""
    out = []
    for which, x, y in (("carb", 0.0, 0.0),
                        ("flavor-a", +tail_half_x, pack_flavor_depth),
                        ("flavor-b", -tail_half_x, pack_flavor_depth),
                        ("drain", _fi.drain_tube_x, drain_tail_y)):
        fluid = tube_collar.STATIONS[which].fluid
        collar, word = build_collar(which, x, y)
        out.append((f"collar_{which.replace('-', '_')}", collar,
                    cq.Color(*(c / 255.0 for c in _rear.chip_color(fluid)))))
        out.append((f"collar_{which.replace('-', '_')}_word", word,
                    cq.Color(*(c / 255.0 for c in _rear.word_color(fluid)))))
    return out


def build_assembly():
    """The faucet and its umbilical in the repo's +Z-up frame — the sub-assembly the bench bags,
    from the display on the tip down to the three square-cut tails and the collar on each."""
    westbrass = load_westbrass()
    soda_faucet_tube = build_soda_faucet_tube()
    lever = build_lever()
    above_counter_plate = load_above_counter_plate()
    above_counter_gasket = load_above_counter_gasket()
    o_ring = build_o_ring()
    shell_base, shell_tip = load_shell_pieces()
    display_cover = load_display_cover()
    display_body = build_display_body()
    display_screen = build_display_screen()
    countertop = build_countertop()
    under_counter_plate = build_under_counter_plate()
    soda_umbilical_tube = build_soda_umbilical_tube()

    # The umbilical tubes carry the identification colour of their stock, off the one table that
    # says what a colour means on this machine — `_y_wall_dimensions.port_colors`, the same read
    # by the bulkhead rings, the runs inside the cabinet and the collars on these three tails.
    # The blue 1/4-inch soda umbilical tube stops on the Westbrass's lower compression port. The
    # separate 3/8-inch soda faucet tube inside the gooseneck and the flavour pair's runs through
    # the faucet are drawn black LLDPE, and white on a White faucet: `web/contracts/faucet-options.js`
    # paints them in the finish, and shows each finish its own joint — a White faucet's two unions
    # or a Black faucet's bridges through the same places.
    def spool(fluid):
        return cq.Color(*(c / 255.0 for c in _rear.port_colors[fluid]))

    black_lldpe = spool("flavor")

    # The donor faucet is matte black (`ledger/bom.md` §9, Westbrass A2031-NL-62) and the printed
    # stack around it is PET-GF15; what a hand meets above the counter is one colour end to end.
    # Every one of these is `_materials`, so a body here and its own card are one colour.
    donor_black = _mat.M_DONOR_BLACK
    faucet_black = _mat.C_FAUCET_BLACK
    tpu_black = _mat.M_TPU_BLACK
    # The gooseneck's 1.47" Waveshare (`ledger/bom.md` §1) is black at the customer-facing
    # display and under its black printed cover. The glass is drawn dark because a screen is lit
    # only while the machine is dispensing, and a render that paints it lit is drawing a state
    # rather than a part.
    display_black = _mat.C_FAUCET_DISPLAY
    display_glass = _mat.C_FAUCET_DISPLAY_GLASS
    steel = _mat.M_STAINLESS  # the 316 SS under-counter cut plate
    stone = cq.Color(0.55, 0.55, 0.58, 0.25)  # the kitchen's slab — context, not a part
    foam_black = _mat.M_NITRILE_BLACK  # CARGEN nitrile, on the blue tube only
    sleeve_black = _mat.M_PET_BRAID    # PET braid, over the lot

    assy = cq.Assembly(name="faucet-assembly")
    assy.add(westbrass, name="westbrass", color=donor_black)
    assy.add(soda_faucet_tube, name="soda_faucet_tube", color=black_lldpe)
    assy.add(o_ring, name="tpu_o_ring", color=tpu_black)
    for x_sign in flavor_sides:
        side = "pos_x" if x_sign > 0 else "neg_x"
        assy.add(build_flavor_faucet_run(x_sign), name=f"flavor_tube_{side}", color=black_lldpe)
        assy.add(build_flavor_union(x_sign), name=f"flavor_union_{side}", color=_mat.M_JG_WHITE_PP)
        assy.add(build_flavor_bridge(x_sign), name=f"flavor_tube_bridge_{side}", color=black_lldpe)
        assy.add(build_flavor_umbilical_run(x_sign), name=f"flavor_umbilical_tube_{side}",
                 color=black_lldpe)
    assy.add(soda_umbilical_tube, name="soda_umbilical_tube", color=spool("carb"))
    assy.add(build_drain_tube(), name="drain_tube", color=spool("drain"))
    assy.add(build_vent_seal(True),name="vent_upstream_bung",color=tpu_black)
    assy.add(build_vent_seal(False),name="vent_downstream_bung",color=tpu_black)
    assy.add(lever, name="lever", color=donor_black)
    assy.add(above_counter_plate, name="above_counter_plate", color=faucet_black)
    assy.add(above_counter_gasket, name="above_counter_gasket", color=tpu_black)
    assy.add(shell_base, name="shell_base", color=faucet_black)
    assy.add(shell_tip, name="shell_tip", color=faucet_black)
    assy.add(display_cover, name="faucet-display-cover-seated", color=faucet_black)
    for i, (x, y) in enumerate(faucet_shell.base_pod_centers, 1):
        assy.add(build_base_screw(x, y), name=f"base_screw_{i}", color=donor_black)
        assy.add(build_base_insert(x, y), name=f"base_insert_{i}", color=_mat.M_BRASS)
    assy.add(display_body, name="faucet_display", color=display_black)
    assy.add(display_screen, name="faucet_display_screen", color=display_glass)
    assy.add(build_display_ribbon(), name="display_signal_ribbon", color=_mat.M_SILICONE_BLACK)
    assy.add(countertop, name="countertop", color=stone)
    assy.add(under_counter_plate, name="under_counter_plate", color=steel)
    assy.add(build_foam(), name="cold_line_foam", color=foam_black)
    assy.add(build_sleeve(), name="umbilical_sleeve", color=sleeve_black)
    for name, solid, color in umbilical_collars():
        assy.add(solid, name=name, color=color)
    return assy


def main():
    out = _assembly_dir / "faucet-assembly.step"
    export_assembly(build_assembly(), str(out))

    # Keep the viewer on the checked printable meshes using the shared payload pipeline.
    import flute_payload                                                # noqa: E402
    grafted = flute_payload.graft(
        Path(str(out) + ".mesh"), flute_payload.surfaces(flute_payload.FAUCET_DIRS))
    if grafted:
        print(f"-> {out.name}.mesh  ({grafted} printable piece(s))")

    bend1_deg = math.degrees(gn_bend1_sweep_rad)
    bend2_deg = math.degrees(gn_bend2_sweep_rad)
    tip_below_horiz = (bend1_deg + bend2_deg) - 90.0
    print("Touch-Flo faucet assembly")
    print(f"  Reference Westbrass:   {ref_westbrass_step.name}")
    print(f"  Soda faucet tube:      Ø{soda_faucet_tube_od:.3f} mm")
    print(f"                         Z_bottom = {soda_faucet_tube_z_bottom:.2f} mm "
          f"({soda_faucet_tube_into_port} mm into port)")
    print(f"                         vertical → gooseneck")
    print(f"                         center at X=0, Y={+port_center_depth:.3f} mm")
    print(f"  Flavor tubes (×2):     Ø{flavor_tube_od:.3f} mm")
    print(f"                         Z_bottom = {flavor_tube_z_bottom:.1f} mm")
    print(f"                         lower depth = {flavor_tube_depth_lower:.4f} mm "
          f"(tangent to the Westbrass's back face)")
    print(f"                         tight pack depth = {flavor_tube_depth_upper:.4f} mm")
    print(f"                         lower/umbilical X = ±{flavor_tube_x_offset:.4f} mm; "
          f"seal and face positions follow faucet_paths.py")
    print(f"                         smooth lower transition starts at Z = {pre_bend_z:.1f}")
    print(f"  Gooseneck:             bend 1 {bend1_deg:.0f}°, bend 2 {bend2_deg:.0f}°, "
          f"midpoint Z={gn_bend1_mid_z:.1f}, start Z={gn_bend1_start_z:.2f}")
    print(f"                         bend 1: water R={gn_bend1_r:.2f} mm, "
          f"flavor R={gn_flavor_bend1_r:.2f} mm (parallel offset)")
    print(f"                         bend 2: water R={gn_bend2_r:.2f} mm, "
          f"flavor R={gn_flavor_bend2_r:.2f} mm (parallel offset)")
    print(f"                         {gn_mid_straight_len} mm angled straight "
          f"@ {bend1_deg:.0f}° from vertical")
    print(f"                         {gn_tip_straight_len} mm tip "
          f"({tip_below_horiz:.0f}° below horizontal)")
    print(f"  Soda umbilical tube:   Ø{soda_umbilical_tube_od:.3f} mm, "
          f"Z = {soda_umbilical_tube_z_bottom:.1f} → {soda_umbilical_tube_z_top:.1f} "
          f"(on the shank's bottom face)")
    print(f"  Unions (White faucet): PP0408W Ø{union.RING_D:g} × {union_length:g}, flavor-b's "
          f"Z = {union_b_top_z:.2f} → {union_a_top_z:.2f}, flavor-a's → {union_foot_z:.2f}")
    print(f"                         the pair {union_pass:.3f} apart there: flavor-b stepped "
          f"{step_x:.3f} along −X over {step_rise:.2f} mm, flavor-a on its own line")
    print(f"                         tube stops {union_gap:g} mm apart in each — a Black "
          f"faucet's bridge")
    print(f"  Umbilical:             gathers of {gather_rise(+1):.2f} (flavor-a) and "
          f"{gather_rise(-1):.2f} (flavor-b) to the pack at Z = {umbilical_z_bottom:.2f}, "
          f"depth {pack_flavor_depth:.4f} at X = ±{flavor_tube_x_offset:.4f}")
    print(f"                         drawn {umbilical_drawn:g} mm below the compression port, "
          f"all four tails on Z = {umbilical_tail_z:.1f}")
    print(f"  Factory cut:           blue {blue_cut_length:g}, flavour {flavor_cut_length:g} "
          f"({flavor_path_above_pack(+1):.1f} / {flavor_path_above_pack(-1):.1f} of it "
          f"above the pack)")
    print(f"                         the three tails land within {tails_apart:.2f} mm — "
          f"§1 sums them to one plane")
    print(f"                         White faucet: white {white_cut_length(+1):g} / "
          f"{white_cut_length(-1):g}, black {black_run_cut_length(+1):g} / "
          f"{black_run_cut_length(-1):g} (flavor-a / flavor-b)")
    print(f"                         soda faucet tube {soda_faucet_cut_length:g}, "
          f"in the faucet's finish")
    print(f"                         4 mm DRAIN tube {drain_factory_cut_length():g}, untrimmed")
    print(f"  Foam (blue only):      Ø{foam_od:g}, {foam_length:.1f} mm over five segments, drawn "
          f"Z = {foam_z_bottom:.1f} → {foam_z_top:.1f} "
          f"({foam_bare_at_westbrass:.1f} bare at the Westbrass, "
          f"{foam_bare_at_wall:g} bare at the wall)")
    print(f"  Sleeve:                {bundle_girth():.2f} mm of girth, Ø{bundle_bore():.2f} opened, "
          f"at Y = {sleeve_center_y:.4f}, "
          f"Z = {sleeve_z_bottom:.1f} → {umbilical_z_bottom:.1f} over the pack "
          f"({foam_bare_at_wall:.1f} mm of bundle left bare, five segments over the foam's)")
    print(f"                         {union_girth():.2f} mm of girth over the unions, "
          f"Z = {umbilical_z_bottom:.1f} → {sleeve_z_top:.2f}")
    print(f"  Tube collars:          {tube_collar.OD:g} × {tube_collar.LENGTH:g}, "
          f"Z = {collar_top_z - tube_collar.LENGTH:.1f} → {collar_top_z:.1f} — "
          f"SODA on the blue, FLAVOR on each black")
    print(f"  TPU o-ring:            in the Ø{tpu_o_ring.westbrass_port_diameter:.1f} mm top port, "
          f"Z = {soda_faucet_tube_z_bottom - tpu_o_ring.cap_thickness:.2f} → "
          f"{soda_faucet_tube_z_bottom - tpu_o_ring.cap_thickness + tpu_o_ring.total_height:.2f}")
    print(f"  Above-counter plate:   above_counter_plate.build_above_counter_plate()")
    print(f"  Above-counter gasket:  above_counter_gasket.build_above_counter_gasket()")
    print(f"  Shell pieces:          faucet_shell.build_shell_base/tip()")
    print(f"  Display cover:         faucet_display_cover.build_seated_display_cover()")
    print(f"  Countertop:            {countertop_thickness:.0f} mm slab, "
          f"Z = {countertop_bottom_z:.1f} → {countertop_top_z:.1f}")
    print(f"    standard hole:       Ø{countertop_hole_diameter:.2f} mm at Y = "
          f"{countertop_hole_center_y:.3f} mm — the faucet back against its wall")
    print(f"                         flavor pair on the wall, "
          f"{countertop_hole_margin:.3f} mm of slab forward of the shank")
    print(f"                         gasket covers the hole behind by "
          f"{gasket_hole_cover():.3f} mm")
    print(f"  Under-counter plate:   {under_counter_plate_thickness} mm 316 SS off "
          f"{under_counter_dxf.name}, Z = "
          f"{countertop_bottom_z - under_counter_plate_thickness:.3f} → {countertop_bottom_z:.1f}")
    print(f"-> {out.name}")

    substitute_py_comments(
        Path(__file__),
        variables={
            "SODA_FAUCET_TUBE_OD": f"{soda_faucet_tube_od:.4g} mm",
            "SODA_FAUCET_TUBE_Z_BOTTOM": f"{soda_faucet_tube_z_bottom:.4g} mm",
            "SODA_FAUCET_TUBE_Z_TOP": f"{soda_faucet_tube_z_top:.4g} mm",
            "FLAVOR_TUBE_OD": f"{flavor_tube_od:.4g} mm",
            "FLAVOR_TUBE_DEPTH_LOWER": f"{flavor_tube_depth_lower:.4g} mm",
            "FLAVOR_TUBE_DEPTH_UPPER": f"{flavor_tube_depth_upper:.4f} mm",
            "FLAVOR_BEND_THETA": f"{flavor_bend_theta_rad:.4f} rad",
            "PRE_BEND_Z": f"{pre_bend_z:.4g} mm",
            "LEVER_TOP_Z": f"{lever_top_z:.4g} mm",
            "GN_BEND_MID_Z": f"{gn_bend1_mid_z:.4g} mm",
            "GN_BEND_START_Z": f"{gn_bend1_start_z:.2f} mm",
            "GN_FLAVOR_BEND_ONE_R": f"{gn_flavor_bend1_r:.4f} mm",
            "GN_FLAVOR_BEND_TWO_R": f"{gn_flavor_bend2_r:.4f} mm",
            "UMBILICAL_Z_BOTTOM": f"{umbilical_z_bottom:.4g} mm",
            "PACK_FLAVOR_DEPTH": f"{pack_flavor_depth:.4f} mm",
            "UNION_GAP": f"{union_gap:.4g} mm",
            "UNION_PASS": f"{union_pass:.4g} mm",
            "STEP_X": f"{step_x:.4g} mm",
            "UNION_B_TOP_Z": f"{union_b_top_z:.4g} mm",
            "UNION_A_TOP_Z": f"{union_a_top_z:.4g} mm",
            "UNION_FOOT_Z": f"{union_foot_z:.4g} mm",
            "UMBILICAL_TAIL_Z": f"{umbilical_tail_z:.5g} mm",
            "TAILS_APART": f"{tails_apart:.4g} mm",
            "FOAM_BARE_AT_WESTBRASS": f"{foam_bare_at_westbrass:.4g} mm",
            "FOAM_Z_BOTTOM": f"{foam_z_bottom:.4g} mm",
            "SLEEVE_CENTER_Y": f"{sleeve_center_y:.4f} mm",
            "SLEEVE_GIRTH": f"{bundle_girth():.4g} mm",
            "SLEEVE_BORE": f"{bundle_bore():.4g} mm",
            "SODA_UMBILICAL_BELOW_COUNTER": f"{countertop_top_z - soda_umbilical_tube_z_top:.4g} mm",
            "COUNTERTOP_TOP_Z": f"{countertop_top_z:.4g} mm",
            "COUNTERTOP_BOTTOM_Z": f"{countertop_bottom_z:.4g} mm",
            "HOLE_CENTER_Y": f"{countertop_hole_center_y:.4g} mm",
            "HOLE_MARGIN": f"{countertop_hole_margin:.4g} mm",
        },
    )


if __name__ == "__main__":
    main()
