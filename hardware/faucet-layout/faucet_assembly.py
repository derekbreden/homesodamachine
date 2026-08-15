"""The faucet, whole — every body above the counter, the countertop it clamps
through, and the three tubes running down past it into the umbilical.

`printed-parts/faucet/` holds the four printed pieces one at a time and
`cut-parts/faucet/` the plate under the slab; this is the column they stack into,
with the harvested Westbrass body they are built around
(`reference/touch-flo-faucet/valve-body-reference/`) and the display on the tip.

FRAME: the repo's +Z-up. +Z is height and the body axis, +X is lateral (the two
flavor tubes mirror across X = 0), -Y is the front — the gooseneck dispenses
toward -Y and the lever points toward -Y, so the water port and the flavor-tube
pill sit BEHIND the body axis at +Y. Z = 0 is the mounting plate's underside;
the countertop's top face is at Z = -6, under the TPU gasket.

TWO WATER PORTS, and the tube in each is a different size. The blue 1/4" supply
lands on the compression port at the BOTTOM of the shank (Z = -50, 44 mm below
the countertop's top face) and water rises inside the shank; the 3/8" dispense
tube leaves the body's Ø10 top port and runs up the gooseneck, sealed into that
port by the printed TPU thimble. `assembly/faucet-and-umbilical.md` is the bench
that makes both up.

The column, top to bottom:

    display          Waveshare ESP32-S3-Touch-LCD-1.47, on the dispense tip
    shell            three printed pieces, as printed — joint voids and all
    dispense tubes   3/8" water up the middle, two 1/4" flavor behind it
    lever            rest and pressed, as one swing-clearance blob
    valve body       harvested Westbrass R2031-NL
    o-ring           printed TPU thimble in the body's top water port
    mounting plate   Ø54.35 × 4 printed disc,       Z = [-4, 0]
    mounting gasket  Ø54.35 × 2 printed TPU disc,   Z = [-6, -4]
    countertop       30 mm slab,                    Z = [-36, -6]
    under-counter    Ø54.45 × 1.524 cut 316 SS,     Z = [-37.524, -36]
    supply tube      1/4" blue, on the shank's own compression port

Regenerate:
    tools/cad-venv/bin/python hardware/faucet-layout/faucet_assembly.py
"""

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
from docgen import substitute_py_comments


_assembly_dir = Path(__file__).resolve().parent
_repo_hardware_dir = _assembly_dir.parent
_faucet_printed_dir = _repo_hardware_dir / "printed-parts" / "faucet"
_faucet_cut_dir = _repo_hardware_dir / "cut-parts" / "faucet"

ref_body_step = (_repo_hardware_dir / "reference" / "touch-flo-faucet"
                 / "valve-body-reference" / "touch-flo-valve-body-reference.step")
under_counter_dxf = (_faucet_cut_dir / "touch-flo-under-counter-plate"
                     / "touch-flo-under-counter-plate.dxf")

sys.path.insert(0, str(_repo_hardware_dir / "printed-parts" / "cadlib"))
from world_workplane import WorldWorkplane, xy_plane_z_up

# Each printed part's build_*() returns +Z-up.
sys.path.insert(0, str(_faucet_printed_dir))  # for _touch_flo_interface
sys.path.insert(0, str(_faucet_printed_dir / "touch-flo-mounting-plate"))
sys.path.insert(0, str(_faucet_printed_dir / "touch-flo-mounting-gasket"))
sys.path.insert(0, str(_faucet_printed_dir / "touch-flo-tpu-o-ring"))
sys.path.insert(0, str(_faucet_printed_dir / "touch-flo-shell"))
import touch_flo_mounting_plate
import touch_flo_mounting_gasket
import touch_flo_tpu_o_ring
import touch_flo_shell
from _touch_flo_interface import (
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


# Reference body geometry, shared with
# `../valve-body-reference/valve_body_reference.py`. The Westbrass body's
# water port sits at depth Y = +port_center_depth (BEHIND the body axis,
# toward the back); +Z is the body's vertical axis.
port_center_depth = 8.875
plateau_z = 39.0
body_od = 31.50  # cylinder OD = rectangle long dim
body_r = body_od / 2
shank_od = 11.0
shank_length = 50.0  # shank runs from Z=0 down to Z=-shank_length
countertop_hole_diameter = 34.93  # 1-3/8", the standard the shank is sized for


# Water dispense tube — ⌀[9.525 mm](WATER_TUBE_OD) (3/8" LLDPE) — seated in the
# body's 10.0 mm water port and running up through the gooseneck. The
# 0.475 mm diametric (0.2375 mm radial) gap is sealed by a printed TPU
# bushing on the real tube (not modeled).
# [9.525 mm](WATER_TUBE_OD) — 3/8" LLDPE in millimeters.
water_tube_od = 0.375 * 25.4
water_tube_r = water_tube_od / 2.0
water_tube_above_plateau = 40.0
water_tube_into_port = 15.0
water_tube_z_bottom = plateau_z - water_tube_into_port  # [24 mm](WATER_TUBE_Z_BOTTOM)
water_tube_z_top = plateau_z + water_tube_above_plateau  # [79 mm](WATER_TUBE_Z_TOP)


# Flavor dispense tubes — Ø 1/4" — sit BEHIND the water tube. Not
# inserted into the body. At their lower (deeper) depth, each tube is
# tangent to
#   - the back face of the body (Y = -body_r)
#   - the other flavor tube (so both touch at X = 0)
# Mirror across X = 0: one at +X, one at -X. Z span runs from the
# bottom of the shank up to the top of the water tube.
# [6.35 mm](FLAVOR_TUBE_OD) — 1/4" LLDPE in millimeters.
flavor_tube_od = 1.0 / 4.0 * 25.4
flavor_tube_r = flavor_tube_od / 2.0
# [18.93 mm](FLAVOR_TUBE_DEPTH_LOWER) — tangent to body +Y (back) face.
flavor_tube_depth_lower = body_r + flavor_tube_r
flavor_tube_x_offset = flavor_tube_r  # ± — tangent to other tube at X=0

# Below the plate the three tubes run together — the sleeve goes on just under
# it and the umbilical runs 1.2 m to the rear wall (`faucet-and-umbilical.md`
# §"Cut the three LLDPE tubes to length"). This is the stub of that run the
# assembly draws, so all three leave on one plane.
umbilical_stub = 30.0
umbilical_z_bottom = -shank_length - umbilical_stub  # [-80 mm](UMBILICAL_Z_BOTTOM)

flavor_tube_z_bottom = umbilical_z_bottom
flavor_tube_z_top = water_tube_z_top

# Carbonated water arrives at the OTHER port: the compression fitting on the
# bottom of the shank, [44 mm](SUPPLY_BELOW_COUNTER) below the countertop's top
# face, and rises inside the shank to the body. So the blue tube is 1/4" and is
# entirely below the counter, where the 3/8" dispense tube above is not. The
# harvested body models no shank bore and no fitting, so this butts on the
# shank's own bottom face.
supply_tube_od = flavor_tube_od
supply_tube_r = supply_tube_od / 2.0
supply_tube_z_top = -shank_length

# Upper depth is set by tangency to the water tube at the same X:
#   (depth_upper - port_center_depth)² + x_offset² = (water_tube_r + flavor_tube_r)²
# with X constant through both bends.
# [16.1498 mm](FLAVOR_TUBE_DEPTH_UPPER) — Pythagorean tangency to water tube.
flavor_tube_depth_upper = port_center_depth + math.sqrt(
    (water_tube_r + flavor_tube_r) ** 2 - flavor_tube_x_offset ** 2
)

# S-bend absorbs the depth offset between lower and upper positions.
# Both bends share R and θ; with no middle straight, the two arcs satisfy
# 2·R·(1 − cos θ) = depth_offset.
flavor_bend_radius = 8.0
_flavor_depth_offset = flavor_tube_depth_lower - flavor_tube_depth_upper
# [0.5978 rad](FLAVOR_BEND_THETA) — per-bend angle absorbing the S-bend depth offset.
flavor_bend_theta_rad = math.acos(1.0 - _flavor_depth_offset / (2.0 * flavor_bend_radius))

pre_bend_rise = 3.0
# [42 mm](PRE_BEND_Z) — S-bend starts here.
pre_bend_z = plateau_z + pre_bend_rise


# Gooseneck — above the lever's swing envelope all three tubes sweep
# forward (toward -Y, toward the user) with the same shape:
#   1. vertical straight up to bend 1 start
#   2. bend 1 — sweep gn_bend1_sweep_rad at R = gn_bend1_r (tighter)
#   3. angled straight of gn_mid_straight_len
#   4. bend 2 — sweep gn_bend2_sweep_rad at R = gn_bend2_r (wider)
#   5. tip straight of gn_tip_straight_len
# The tip's exit angle below horizontal = (bend1_sweep + bend2_sweep) - 90°.
lever_top_z = plateau_z + 13.0  # [52 mm](LEVER_TOP_Z)
gn_bend1_r = 30.0
gn_bend2_r = 40.0
gn_bend1_sweep_rad = math.radians(30.0)
gn_bend2_sweep_rad = math.radians(110.0)
# [87 mm](GN_BEND_MID_Z) — bend-1 midpoint, 35 mm above lever_top_z.
gn_bend1_mid_z = lever_top_z + 35.0
# [79.24 mm](GN_BEND_START_Z) — bend-1 start.
gn_bend1_start_z = gn_bend1_mid_z - gn_bend1_r * math.sin(gn_bend1_sweep_rad / 2.0)
gn_mid_straight_len = 115.0
gn_tip_straight_len = 25.0

# Flavor tubes sit further +Y than the water tube (deeper, behind it).
# The gooseneck bends toward -Y, so the flavor tubes are on the OUTSIDE
# of every bend: they trace parallel-offset arcs sharing each bend's
# center of curvature with water, at the larger radius water_r +
# offset_depth. At the bare gooseneck radius the perpendicular component
# of the centerline separation shrinks below water_r + flavor_r and the
# tubes ride into each other through the bend.
_gn_flavor_depth_offset = flavor_tube_depth_upper - port_center_depth
# [37.2748 mm](GN_FLAVOR_BEND_ONE_R) — parallel offset of gn_bend1_r.
gn_flavor_bend1_r = gn_bend1_r + _gn_flavor_depth_offset
# [47.2748 mm](GN_FLAVOR_BEND_TWO_R) — parallel offset of gn_bend2_r.
gn_flavor_bend2_r = gn_bend2_r + _gn_flavor_depth_offset


def load_valve_body():
    """Harvested valve body, authored Z-up in the repo frame."""
    return import_step(str(ref_body_step))


def load_mounting_plate():
    """Printed mounting plate, +Z-up."""
    return touch_flo_mounting_plate.build_mounting_plate()


def load_mounting_gasket():
    """Printed-TPU mounting gasket, +Z-up."""
    return touch_flo_mounting_gasket.build_mounting_gasket()


def load_shell_pieces():
    """The three printed shell pieces, +Z-up, in assembled position —
    as printed, joint voids and all."""
    full = touch_flo_shell.build_shell()
    return (
        touch_flo_shell.build_shell_bottom(full),
        touch_flo_shell.build_shell_middle(full),
        touch_flo_shell.build_shell_top(full),
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


def build_water_dispense_tube():
    """Ø water_tube_od tube — vertical from inside the body's port up to
    the gooseneck, then bend 1, mid straight, bend 2, tip straight."""
    p_bottom = (0.0, 0.0)
    p_gn_start = (0.0, gn_bend1_start_z - water_tube_z_bottom)

    arc1, mid_end, arc2, tip_end = _gooseneck_segments(
        p_gn_start, (0.0, 1.0), gn_bend1_r, gn_bend2_r
    )

    path = (
        cq.Workplane(tube_path_plane)
        .moveTo(*p_bottom)
        .lineTo(*p_gn_start)
        .threePointArc(*arc1)
        .lineTo(*mid_end)
        .threePointArc(*arc2)
        .lineTo(*tip_end)
    )
    # Circular cross-section perpendicular to the path's starting +Z tangent.
    profile = cq.Workplane(xy_plane_z_up).circle(water_tube_r)
    tube = profile.sweep(path, transition="round")
    return tube.translate((0, +port_center_depth, water_tube_z_bottom))


def _build_flavor_tube_at_origin():
    """One bent flavor tube at the path origin. Path:
      1. Vertical up to the S-bend start (pre_bend_z)
      2. S-bend (CCW + CW pair) shifting depth by
         flavor_tube_depth_lower − flavor_tube_depth_upper toward the
         water tube, ending tangent to +Z
      3. Vertical from S-bend end up to the gooseneck start
         (Z = gn_bend1_start_z, in tube-local coords)
      4. Gooseneck: bend 1 → mid straight → bend 2 → tip, all bending
         toward -Y. Each bend uses its own parallel-offset radius
         (gn_flavor_bend1_r / gn_flavor_bend2_r) on the outside of the
         gooseneck bend, staying tangent to the water tube.
    """
    p_bottom = (0.0, 0.0)
    p_s_bend_start = (0.0, pre_bend_z - flavor_tube_z_bottom)

    # S-bend (CCW then CW), ends tangent to +Z.
    s1_mid, s1_end, s1_tangent = _arc_from_tangent(
        p_s_bend_start, (0.0, 1.0), flavor_bend_radius, flavor_bend_theta_rad, ccw=True
    )
    s2_mid, s2_end, s2_tangent = _arc_from_tangent(
        s1_end, s1_tangent, flavor_bend_radius, flavor_bend_theta_rad, ccw=False
    )

    # Vertical to the gooseneck start, depth unchanged.
    p_gn_start = (s2_end[0], gn_bend1_start_z - flavor_tube_z_bottom)

    arc1, mid_end, arc2, tip_end = _gooseneck_segments(
        p_gn_start, s2_tangent, gn_flavor_bend1_r, gn_flavor_bend2_r
    )

    path = (
        cq.Workplane(tube_path_plane)
        .moveTo(*p_bottom)
        .lineTo(*p_s_bend_start)
        .threePointArc(s1_mid, s1_end)
        .threePointArc(s2_mid, s2_end)
        .lineTo(*p_gn_start)
        .threePointArc(*arc1)
        .lineTo(*mid_end)
        .threePointArc(*arc2)
        .lineTo(*tip_end)
    )

    profile = cq.Workplane(xy_plane_z_up).circle(flavor_tube_r)
    return profile.sweep(path, transition="round")


def build_flavor_tube(x_sign):
    """One Ø 1/4" flavor tube at +Y behind the body axis. x_sign ∈ {±1}
    selects the lateral side; the two tubes mirror across the X = 0
    plane."""
    tube = _build_flavor_tube_at_origin()
    return tube.translate((
        x_sign * flavor_tube_x_offset,
        +flavor_tube_depth_lower,
        flavor_tube_z_bottom,
    ))


# Lever pivot — axis parallel to world X at (Y = lever_pivot_y, Z = lever_pivot_z).
# The lever swings between rest (0°) and pressed (+lever_press_angle_deg)
# around this axis, sweeping the clearance volume the shell must avoid.
lever_pivot_y = +1.5
lever_pivot_z = plateau_z + 7.0
lever_press_angle_deg = 18.0


def build_lever():
    """The lever's swing-clearance blob: union of the rest position and
    the pressed-down position (0° and -lever_press_angle_deg around the
    pivot), each carrying its own vertical water-tube clearance cut.

    Geometry:
      - The lever's body is a 13 (X) × 15 (Y) × 12 (Z) box,
        centered laterally on X = 0, spanning depth Y = [-6, +9]
        (back end at +Y abutting the body, front face at Y = -6 where
        the user presses), at height Z = [plateau_z+1, plateau_z+13].
      - From the front face it tapers forward as a 13 × shrinking-Z
        tongue out to Y = -42 — the handle toward the user.
      - The pivot axis is parallel to world X (lateral), through
        (X = 0, Y = +1.5, Z = plateau_z + 7), so the lever rotates in
        the Y-Z plane (no lateral motion).
    """
    # Water-tube clearance through the lever. The water tube sits at
    # world Y = +port_center_depth; this cut is 0.125 mm further +Y for
    # margin, vertical along +Z, 50 mm tall to span both lever positions.
    cut_cylinder = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=plateau_z + 1)
        .moveTo((0, +(port_center_depth + 0.125)))
        .circle(water_tube_r + 1)
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

    # The water-tube cut is vertical in world +Z, so it clears the
    # upright water tube in the pressed (tilted) position too.
    lever_pressed = lever_rest.rotate(pivot_a, pivot_b, +lever_press_angle_deg).cut(cut_cylinder)
    lever_rest_final = lever_pressed.rotate(pivot_a, pivot_b, -lever_press_angle_deg)

    return lever_rest_final.union(lever_pressed)


# Faucet flavor display — Waveshare ESP32-S3-Touch-LCD-1.47 (BOM §1),
# modeled as a dimensioned stand-in. Device dims live in
# _touch_flo_interface, shared with the shell's display cradle (table in
# display-reference/README.md). The under-PCB zone is a full-footprint
# bounding block down to the feet plane — it shares the PCB's outline,
# so the PCB underside (display_pcb_bottom_z) has no edge in the solid.
#
# Native frame: X = width, Y = length, Z = outward thickness; the feet
# plane (bounding back) at z = 0, screen faces +Z. Seated on the tip:
# long axis along the tip, screen toward the user, lower edge one
# end-wall thickness up the tip (behind the shell's PCB cover), feet
# display_pocket_inset below the shell's outer face above the flavor
# pill — the inset, the web it leaves over the pill bore, and the end
# wall are the shell's display-cradle constants.
display_pocket_inset = touch_flo_shell.display_pocket_inset
# Active (lit) display area, on the front face.
display_screen_width = 17.75
display_screen_length = 32.93
display_screen_depth = 0.4


def _tip_centerline_world():
    """(tip_start, tip_end) of the water-tube dispense-tip straight in world coords."""
    p_gn_start = (0.0, gn_bend1_start_z - water_tube_z_bottom)
    _, _, arc2, tip_end = _gooseneck_segments(
        p_gn_start, (0.0, 1.0), gn_bend1_r, gn_bend2_r
    )
    def to_world(p):
        return cq.Vector(0.0, p[0] + port_center_depth, p[1] + water_tube_z_bottom)
    return to_world(arc2[1]), to_world(tip_end)


def _seat_on_tip(part):
    """Place a display part (native frame: X width, Y length, Z outward
    with the feet plane at z = 0) onto the dispense tip. The tip straight
    runs (gn_bend1_sweep + gn_bend2_sweep − 90°) below horizontal;
    rotating that angle about world X lays the part's length up the
    gooseneck and turns its screen (+Z) up toward the user. It is then
    offset out along the tip's top normal so the feet plane sits
    display_pocket_inset below the shell's outer face above the flavor
    pill (the two flavor tubes stack above the water tube here, so they
    set the skin). The housing's lower edge is anchored one end-wall
    thickness up the tip from the tip end — behind the shell's PCB
    cover; it extends up the tip from there (the far end is
    unconstrained)."""
    tip_below_horiz_rad = (gn_bend1_sweep_rad + gn_bend2_sweep_rad) - math.pi / 2.0
    top_normal = cq.Vector(
        0.0, -math.sin(tip_below_horiz_rad), math.cos(tip_below_horiz_rad)
    )
    tip_start, tip_end = _tip_centerline_world()
    tip_axis = tip_end - tip_start
    tip_axis = tip_axis.multiply(1.0 / tip_axis.Length)
    # The display sits over the FLAVOR pill, not the water tube: the two
    # flavor tubes stack above the water tube on the user-facing side, so
    # they set the outer skin here. Distance from the water-tube
    # centerline out along top_normal to the shell's outer face above the
    # flavor pill = flavor-pill center offset + half the pill's short (Y)
    # axis + the tube-shell wall. This is exactly the +Y outer edge of the
    # flavor-pill slot in touch_flo_shell._tube_shell_outer_sketch.
    flavor_pill_outer_from_water = (
        touch_flo_shell.flavor_offset_y_from_water
        + touch_flo_shell.pill_width_y / 2.0
        + touch_flo_shell.zone5_wall
    )
    # Anchor the housing's lower (nozzle-end) edge one end-wall thickness
    # up the tip from the tip end (behind the shell's PCB cover), at the
    # flavor-pill outer face minus the inset; it extends up the tip.
    seat = (
        tip_end
        + top_normal.multiply(flavor_pill_outer_from_water - display_pocket_inset)
        - tip_axis.multiply(
            display_housing_length / 2.0 + touch_flo_shell.display_line_width
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
    """Display module body — the under-PCB bounding block + PCB as one
    prism up to the housing bottom, the wider plastic housing above it,
    and an active-area recess in the front face. Seated on the tip."""
    pcb_and_under = (
        cq.Workplane("XY")
        .box(display_pcb_width, display_pcb_length, display_pcb_top_z,
             centered=(True, True, False))
        .edges("|Z").fillet(display_pcb_corner_r)
    )
    housing = (
        cq.Workplane("XY").workplane(offset=display_pcb_top_z)
        .box(display_housing_width, display_housing_length,
             display_total_depth - display_pcb_top_z, centered=(True, True, False))
        .edges("|Z").fillet(display_corner_r)
    )
    body = pcb_and_under.union(housing).cut(_screen_pocket())
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
# The slab is not a part — it is the customer's kitchen — but it is what sets
# where the cut plate lands, so the assembly carries it at the figure
# `assembly/faucet-and-umbilical.md` sums its tube lengths on: 30 mm of 3 cm
# stone, in a 19–38 range. Drawn 120 mm square, which is enough to read as a
# slab around a Ø54.45 plate.
countertop_thickness = 30.0
countertop_slab_xy = 120.0
countertop_top_z = touch_flo_mounting_gasket.gasket_z_range[0]      # [-6 mm](COUNTERTOP_TOP_Z)
countertop_bottom_z = countertop_top_z - countertop_thickness       # [-36 mm](COUNTERTOP_BOTTOM_Z)

under_counter_plate_thickness = 1.524  # 0.060" 316 SS, the DXF's own sidecar

hole_radius = countertop_hole_diameter / 2.0


def shank_hole_margin(center_y):
    """Slab left between the drilled hole and the shank, at a hole on the body
    axis' own X and `center_y` in depth."""
    return hole_radius - (abs(center_y) + shank_od / 2.0)


def flavor_hole_margin(center_y):
    """The same for the flavor pair — measured to the far tube's far wall."""
    reach = math.hypot(flavor_tube_x_offset, flavor_tube_depth_lower - center_y)
    return hole_radius - (reach + flavor_tube_r)


def balanced_hole_center_y():
    """THE DRILLED HOLE DOES NOT CENTRE ON THE SHANK. The flavor pair stands at
    depth 18.925 and ±3.175 lateral, so its far wall lies 22.365 from the body
    axis — the hypotenuse of the two, plus the tube's own radius, and not the
    22.1 the depth alone would give. A 1-3/8" hole on the axis reaches 17.465
    and cuts that wall by 4.899. Shank margin falls as the hole moves back and
    flavor margin rises, so one depth leaves both the same — bisected here
    rather than solved, and the margin it leaves is printed by the run."""
    lo, hi = 0.0, flavor_tube_depth_lower
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if shank_hole_margin(mid) > flavor_hole_margin(mid):
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


# [8.537 mm](HOLE_CENTER_Y) behind the body axis.
countertop_hole_center_y = balanced_hole_center_y()
# [3.428 mm](HOLE_MARGIN) of slab, to the shank and to the flavor pair alike.
countertop_hole_margin = shank_hole_margin(countertop_hole_center_y)


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
    world +Y over the flavor pair and opens both channels toward -X."""
    outline = cq.importers.importDXF(str(under_counter_dxf))
    plate = outline.wires().toPending().extrude(under_counter_plate_thickness)
    return (
        plate
        .rotate((0, 0, 0), (0, 0, 1), 90.0)
        .translate((0, 0, countertop_bottom_z - under_counter_plate_thickness))
    )


def build_o_ring():
    """The printed TPU thimble sealing the dispense tube into the body's Ø10 top
    port. Its Z = 0 face is the port floor and the tube bottoms on its cap, so
    the cap's top face is where the water tube starts."""
    return touch_flo_tpu_o_ring.build_o_ring().translate((
        0,
        +port_center_depth,
        water_tube_z_bottom - touch_flo_tpu_o_ring.cap_thickness,
    ))


def build_supply_tube():
    """The blue 1/4" carbonated-water supply, butted on the shank's bottom face
    and running down to the umbilical stub."""
    return (
        cq.Workplane("XY").workplane(offset=umbilical_z_bottom)
        .circle(supply_tube_r)
        .extrude(supply_tube_z_top - umbilical_z_bottom)
    )


def build_assembly():
    """The full faucet assembly in the repo's +Z-up frame."""
    body = load_valve_body()
    water_tube = build_water_dispense_tube()
    flavor_tube_pos_x = build_flavor_tube(+1)
    flavor_tube_neg_x = build_flavor_tube(-1)
    lever = build_lever()
    mounting_plate = load_mounting_plate()
    mounting_gasket = load_mounting_gasket()
    o_ring = build_o_ring()
    shell_bottom, shell_middle, shell_top = load_shell_pieces()
    display_body = build_display_body()
    display_screen = build_display_screen()
    countertop = build_countertop()
    under_counter_plate = build_under_counter_plate()
    supply_tube = build_supply_tube()

    silver = cq.Color(0.85, 0.85, 0.88)  # near-stainless silver
    petg_tan = cq.Color(0.85, 0.78, 0.62)  # printed-part tan
    tpu_black = cq.Color(0.15, 0.15, 0.15)  # TPU 90A black gasket
    display_slate = cq.Color(0.12, 0.13, 0.18)  # dark display module
    display_glass = cq.Color(0.20, 0.55, 0.85)  # lit-screen blue
    steel = cq.Color(0.72, 0.74, 0.78)  # 316 SS cut plate
    water_blue = cq.Color(0.25, 0.45, 0.80)  # blue LLDPE, the cold line
    stone = cq.Color(0.55, 0.55, 0.58, 0.25)  # the kitchen's slab, not a part

    assy = cq.Assembly(name="faucet-assembly")
    assy.add(body, name="valve_body", color=cq.Color("black"))
    assy.add(water_tube, name="water_dispense_tube", color=silver)
    assy.add(o_ring, name="tpu_o_ring", color=tpu_black)
    assy.add(flavor_tube_pos_x, name="flavor_tube_pos_x", color=silver)
    assy.add(flavor_tube_neg_x, name="flavor_tube_neg_x", color=silver)
    assy.add(supply_tube, name="carb_supply_tube", color=water_blue)
    assy.add(lever, name="lever", color=silver)
    assy.add(mounting_plate, name="mounting_plate", color=petg_tan)
    assy.add(mounting_gasket, name="mounting_gasket", color=tpu_black)
    assy.add(shell_bottom, name="shell_bottom", color=petg_tan)
    assy.add(shell_middle, name="shell_middle", color=petg_tan)
    assy.add(shell_top, name="shell_top", color=petg_tan)
    assy.add(display_body, name="faucet_display", color=display_slate)
    assy.add(display_screen, name="faucet_display_screen", color=display_glass)
    assy.add(countertop, name="countertop", color=stone)
    assy.add(under_counter_plate, name="under_counter_plate", color=steel)
    return assy


def main():
    assy = build_assembly()

    out = _assembly_dir / "faucet-assembly.step"
    export_assembly(assy, str(out))

    bend1_deg = math.degrees(gn_bend1_sweep_rad)
    bend2_deg = math.degrees(gn_bend2_sweep_rad)
    tip_below_horiz = (bend1_deg + bend2_deg) - 90.0
    print("Touch-Flo faucet assembly")
    print(f"  Reference body:        {ref_body_step.name}")
    print(f"  Water dispense tube:   Ø{water_tube_od:.3f} mm")
    print(f"                         Z_bottom = {water_tube_z_bottom:.2f} mm "
          f"({water_tube_into_port} mm into port)")
    print(f"                         vertical → gooseneck")
    print(f"                         center at X=0, Y={+port_center_depth:.3f} mm")
    print(f"  Flavor tubes (×2):     Ø{flavor_tube_od:.3f} mm")
    print(f"                         Z_bottom = {flavor_tube_z_bottom:.1f} mm")
    print(f"                         lower depth = {flavor_tube_depth_lower:.4f} mm "
          f"(tangent to body back face + to each other)")
    print(f"                         upper depth = {flavor_tube_depth_upper:.4f} mm "
          f"(tangent to water tube + to each other)")
    print(f"                         X = ±{flavor_tube_x_offset:.4f} mm (constant)")
    print(f"                         S-bend: 2 × R{flavor_bend_radius:.1f} mm "
          f"@ {math.degrees(flavor_bend_theta_rad):.2f}° starting at Z = {pre_bend_z:.1f}")
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
    print(f"  Carb supply tube:      Ø{supply_tube_od:.3f} mm, "
          f"Z = {umbilical_z_bottom:.1f} → {supply_tube_z_top:.1f} "
          f"(on the shank's bottom face)")
    print(f"  TPU o-ring:            in the Ø{touch_flo_tpu_o_ring.body_port_diameter:.1f} mm top port, "
          f"Z = {water_tube_z_bottom - touch_flo_tpu_o_ring.cap_thickness:.2f} → "
          f"{water_tube_z_bottom - touch_flo_tpu_o_ring.cap_thickness + touch_flo_tpu_o_ring.total_height:.2f}")
    print(f"  Mounting plate:        touch_flo_mounting_plate.build_mounting_plate()")
    print(f"  Mounting gasket:       touch_flo_mounting_gasket.build_mounting_gasket()")
    print(f"  Shell pieces:          touch_flo_shell.build_shell_bottom/middle/top()")
    print(f"  Countertop:            {countertop_thickness:.0f} mm slab, "
          f"Z = {countertop_bottom_z:.1f} → {countertop_top_z:.1f}")
    print(f"    drilled hole:        Ø{countertop_hole_diameter:.2f} mm at Y = "
          f"{countertop_hole_center_y:.3f} mm — NOT on the body axis")
    print(f"                         {countertop_hole_margin:.3f} mm of slab to the shank, "
          f"{flavor_hole_margin(countertop_hole_center_y):.3f} mm to the flavor pair")
    print(f"                         (on the axis it would leave "
          f"{flavor_hole_margin(0.0):.3f} mm — the flavor pair cuts the slab)")
    print(f"  Under-counter plate:   {under_counter_plate_thickness} mm 316 SS off "
          f"{under_counter_dxf.name}, Z = "
          f"{countertop_bottom_z - under_counter_plate_thickness:.3f} → {countertop_bottom_z:.1f}")
    print(f"-> {out.name}")

    substitute_py_comments(
        Path(__file__),
        variables={
            "WATER_TUBE_OD": f"{water_tube_od:.4g} mm",
            "WATER_TUBE_Z_BOTTOM": f"{water_tube_z_bottom:.4g} mm",
            "WATER_TUBE_Z_TOP": f"{water_tube_z_top:.4g} mm",
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
            "SUPPLY_BELOW_COUNTER": f"{countertop_top_z - supply_tube_z_top:.4g} mm",
            "COUNTERTOP_TOP_Z": f"{countertop_top_z:.4g} mm",
            "COUNTERTOP_BOTTOM_Z": f"{countertop_bottom_z:.4g} mm",
            "HOLE_CENTER_Y": f"{countertop_hole_center_y:.4g} mm",
            "HOLE_MARGIN": f"{countertop_hole_margin:.4g} mm",
        },
    )


if __name__ == "__main__":
    main()
