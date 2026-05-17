"""Touch-Flo faucet assembly — work-in-progress build-up of the user's
faucet vision on top of the reference valve body.

A growing assembly model that combines the harvested Touch-Flo valve
body (read from `../valve-body-reference/touch-flo-valve-body-reference.step`)
with the parts we are designing around it. The script writes a single
multi-solid STEP file so each iteration can be eyeballed in a viewer.

This is NOT the printed shell. The shell will be a separate file that
wraps around the assembly described here. This file is the body +
tubes + (eventually) other inserts that the shell must accommodate.

Parts currently modeled:
1. Valve body (loaded from the reference STEP — never modified here).
2. Water dispense tube — Ø 9.525 mm (3/8" LLDPE), inserted into the
   body's 9.75 mm water port and extending up through the gooseneck.
   The TPU O-ring sealing the 0.225 mm radial gap is not modeled
   (geometry only; envelope is the bare 9.525 mm OD).
3. Two flavor dispense tubes — Ø 1/4" (6.35 mm), behind the water
   tube. Each tube starts at X = body_r + tube_r = 18.925 mm (butting
   against the body's +X rectangular face and the other flavor tube),
   runs vertical from Z = -50, then S-bends just above the plateau to
   come in tangent against the water tube. After the bends the tubes
   run vertical to Z = 79, butted against the water tube. Not inserted
   into the body.
4. Lever (build_lever) — swing-clearance blob. Union of the lever in
   rest position and pressed-down position (-18° around X=1.5, Z=46),
   each with vertical water-tube clearance for both extremes.
5. Mounting plate (loaded from `../../../printed-parts/faucet/touch-flo-mounting-plate/`).
   Ø 54.35 × 4 mm disc centered at (3.175, 0), spans Z = [-4, 0]. Shank
   hole at (0, 0); flavor-tube pill slot at (18.925, 0). 5 mm radial
   gap from the shell base (Ø 44.35) so the plate reads as a finished
   shoulder under the shell.
6. Shell (loaded from `../../../printed-parts/faucet/touch-flo-shell/`).
   Single-piece shroud covering zones 1–6, centered at (3.175, 0).
   Outer Ø 44.35 mm cylindrical base (zone 1, Z = [0, 13]) → cove
   transition into a 41.175 × 23.5 mm rectangular column (zone 2,
   Z = [13, 39]) → arch wings + plateau fill over the body's arched
   top (zone 3, Z = [39, 44.25]) → tube wrapper above the arch and
   lever (zones 4 + 4.5 + 5, Z = [44.25, 67.5]) → gooseneck wrapper
   following the bent dispense tubes through bend 1, mid straight,
   bend 2, and the tip (zone 6).
7. Mounting gasket (loaded from `../../../printed-parts/faucet/touch-flo-mounting-gasket/`).
   Ø 54.35 × 2.0 mm TPU 90A disc, sits between the mounting plate
   and the countertop (Z = [-6, -4]). Hole pattern mirrors the plate.

Regenerate:
    tools/cad-venv/bin/python generate_step_cadquery.py
"""

import math
import sys
from pathlib import Path

import cadquery as cq

sys.path.insert(
    0,
    str(next(p for p in Path(__file__).resolve().parents if p.name == "hardware")),
)
from _cadq_export import export_assembly


# Reference body geometry. Duplicated from
# `../valve-body-reference/generate_step_cadquery.py` — keep in sync.
port_center_x = 8.875
port_center_y = 0.0
plateau_z = 39.0
body_od = 31.50  # cylinder OD = rectangle long dim
body_r = body_od / 2
shank_length = 50.0  # shank extends from Z=0 down to Z=-shank_length


# Water dispense tube — Ø 9.525 mm (3/8" LLDPE) — drops into the body's
# 9.75 mm water port. The 0.225 mm radial gap is taken up by a TPU
# O-ring on the real tube (not modeled). Extends a comfortable amount
# into the port for retention, and runs through the gooseneck.
water_tube_od = 0.375 * 25.4  # 3/8" LLDPE
water_tube_r = water_tube_od / 2.0
water_tube_above_plateau = 40.0
water_tube_into_port = 15.0
water_tube_z_bottom = plateau_z - water_tube_into_port
water_tube_z_top = plateau_z + water_tube_above_plateau


# Flavor dispense tubes — Ø 1/4" — sit behind the water tube. Not
# inserted into the body. At their lower X, each tube is tangent to
#   - the +X rectangular face of the body (X = body_r)
#   - the other flavor tube (so both touch at Y = 0)
# Mirror across the X-Z plane: one at +Y, one at -Y. Z span runs from
# the bottom of the shank up to the top of the water tube.
flavor_tube_od = 1.0 / 4.0 * 25.4  # 1/4"
flavor_tube_r = flavor_tube_od / 2.0
flavor_tube_x_lower = body_r + flavor_tube_r  # tangent to body +X
flavor_tube_y_offset = flavor_tube_r  # ± — tangent to other tube at Y=0
flavor_tube_z_bottom = -shank_length
flavor_tube_z_top = water_tube_z_top

# Upper X is set by tangency to the water tube at the same Y:
#   (x_upper - port_center_x)² + y_offset² = (water_tube_r + flavor_tube_r)²
# with Y constant through both bends.
flavor_tube_x_upper = port_center_x + math.sqrt(
    (water_tube_r + flavor_tube_r) ** 2 - flavor_tube_y_offset ** 2
)

# S-bend absorbs the X offset between lower and upper positions. Bend
# radius chosen for clean hand-bending of 1/8" SS — 2.5× OD, well above
# the kink threshold and visually generous. Bend angle is derived from
# 2·R·(1 − cos θ) = x_offset (no middle straight); both bends use the
# same R and θ.
flavor_bend_radius = 8.0
_flavor_x_offset = flavor_tube_x_lower - flavor_tube_x_upper
flavor_bend_theta_rad = math.acos(1.0 - _flavor_x_offset / (2.0 * flavor_bend_radius))

# How far above the plateau the first bend starts. Kept short to mimic
# the user's "shortly after that, as shortly as is reasonable."
pre_bend_rise = 3.0
pre_bend_z = plateau_z + pre_bend_rise


# Gooseneck — above the lever's swing envelope all three tubes sweep
# forward toward -X with the same shape:
#   1. vertical straight up to bend 1 start
#   2. bend 1 — sweep gn_bend1_sweep_rad at R = gn_bend1_r (tighter)
#   3. angled straight of gn_mid_straight_len
#   4. bend 2 — sweep gn_bend2_sweep_rad at R = gn_bend2_r (wider)
#   5. tip straight of gn_tip_straight_len
# The tip's exit angle below horizontal = (bend1_sweep + bend2_sweep) - 90°.
# Bend-1 midpoint is anchored at Z = lever_top_z + 35, so the start of
# bend 1 sits gn_bend1_r·sin(bend1_sweep/2) below that.
lever_top_z = plateau_z + 13.0
gn_bend1_r = 30.0
gn_bend2_r = 40.0
gn_bend1_sweep_rad = math.radians(30.0)
gn_bend2_sweep_rad = math.radians(110.0)
gn_bend1_mid_z = lever_top_z + 35.0
gn_bend1_start_z = gn_bend1_mid_z - gn_bend1_r * math.sin(gn_bend1_sweep_rad / 2.0)
gn_mid_straight_len = 115.0
gn_tip_straight_len = 25.0

# The flavor tubes sit at +X of the water tube (X-offset in their local
# frame = flavor_tube_x_upper - port_center_x). The gooseneck bends
# toward -X, so flavor tubes are on the OUTSIDE of every bend and must
# trace parallel-offset arcs sharing each bend's center of curvature
# with water — i.e. at the *larger* radius water_r + offset_x.
# Otherwise the tubes ride into each other through the bend (the
# perpendicular component of the centerline separation shrinks below
# water_r + flavor_r).
_gn_flavor_offset_x = flavor_tube_x_upper - port_center_x
gn_flavor_bend1_r = gn_bend1_r + _gn_flavor_offset_x
gn_flavor_bend2_r = gn_bend2_r + _gn_flavor_offset_x


# Reference STEP files — body, mounting plate, mounting gasket, shell.
_assembly_dir = Path(__file__).resolve().parent
_harvested_dir = _assembly_dir.parent
_repo_hardware_dir = _harvested_dir.parent.parent
_faucet_printed_dir = _repo_hardware_dir / "printed-parts" / "faucet"

ref_body_step = _harvested_dir / "valve-body-reference" / "touch-flo-valve-body-reference.step"
mounting_plate_step = _faucet_printed_dir / "touch-flo-mounting-plate" / "touch-flo-mounting-plate.step"
mounting_gasket_step = _faucet_printed_dir / "touch-flo-mounting-gasket" / "touch-flo-mounting-gasket.step"
shell_step = _faucet_printed_dir / "touch-flo-shell" / "touch-flo-shell.step"


def load_valve_body():
    """Load the harvested valve body from the reference STEP file.
    Read-only — this file never modifies the body geometry."""
    return cq.importers.importStep(str(ref_body_step))


def load_mounting_plate():
    """Load the printed mounting plate from its printed-parts STEP.
    Read-only here — see
    `hardware/printed-parts/faucet/touch-flo-mounting-plate/generate_step_cadquery.py`
    for the source of truth."""
    return cq.importers.importStep(str(mounting_plate_step))


def load_mounting_gasket():
    """Load the printed-TPU mounting gasket from its printed-parts STEP.
    Read-only here — see
    `hardware/printed-parts/faucet/touch-flo-mounting-gasket/generate_step_cadquery.py`
    for the source of truth."""
    return cq.importers.importStep(str(mounting_gasket_step))


def load_shell():
    """Load the printed shell from its printed-parts STEP.
    Read-only here — see
    `hardware/printed-parts/faucet/touch-flo-shell/generate_step_cadquery.py`
    for the source of truth."""
    return cq.importers.importStep(str(shell_step))


def _arc_from_tangent(start, tangent, radius, theta_rad, ccw):
    """Compute waypoints of an arc starting at `start` with `tangent`,
    sweeping `theta_rad` with the given `radius`.

    ccw=True: tangent rotates counterclockwise (tube turns left when
    looking along +Y). ccw=False: clockwise.

    Returns (mid, end, end_tangent) — all in the same 2D X-Z frame."""
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
    """Waypoints for the four-segment gooseneck path starting at
    `start` with `tangent`: bend 1 (R=bend1_r, sweep=gn_bend1_sweep_rad)
    → mid straight (gn_mid_straight_len) → bend 2 (R=bend2_r,
    sweep=gn_bend2_sweep_rad) → tip straight (gn_tip_straight_len).
    Both bends turn CCW (toward -X for the tubes' starting tangent).

    Returns ((arc1_mid, arc1_end), mid_end, (arc2_mid, arc2_end),
    tip_end) — call sites unpack into threePointArc / lineTo calls."""
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


def build_water_dispense_tube():
    """Bent water tube — vertical from inside the body's port up to
    the gooseneck, then bend 1, mid straight, bend 2, tip straight.
    Profile is Ø water_tube_od swept along the centerline path."""
    # Tube-local (X-Z) frame: bottom at (0, 0), Z=0 == water_tube_z_bottom.
    p_bottom = (0.0, 0.0)
    p_gn_start = (0.0, gn_bend1_start_z - water_tube_z_bottom)

    arc1, mid_end, arc2, tip_end = _gooseneck_segments(
        p_gn_start, (0.0, 1.0), gn_bend1_r, gn_bend2_r
    )

    path = (
        cq.Workplane("XZ")
        .moveTo(*p_bottom)
        .lineTo(*p_gn_start)
        .threePointArc(*arc1)
        .lineTo(*mid_end)
        .threePointArc(*arc2)
        .lineTo(*tip_end)
    )
    profile = cq.Workplane("XY").circle(water_tube_r)
    tube = profile.sweep(path, transition="round")
    return tube.translate((port_center_x, port_center_y, water_tube_z_bottom))


def _build_flavor_tube_at_origin():
    """Build one bent flavor tube at the origin.

    Tube-local frame: bottom of the tube at Z = 0, X = 0, going +Z.
    Path:
      1. Vertical from Z=0 up to the S-bend start (pre_bend_z)
      2. S-bend (CCW + CW pair) shifting X by flavor_tube_x_upper −
         flavor_tube_x_lower toward the water tube, ending tangent
         to +Z by construction
      3. Vertical from S-bend end up to the gooseneck start (Z =
         gn_bend1_start_z, in tube-local coords)
      4. Gooseneck: bend 1 → mid straight → bend 2 → tip, all bending
         toward -X. Each bend uses its own parallel-offset radius
         (gn_flavor_bend1_r / gn_flavor_bend2_r), so the flavor tube
         traces a parallel-offset arc on the outside of each gooseneck
         bend, staying tangent to the water tube.
    """
    p_bottom = (0.0, 0.0)
    p_s_bend_start = (0.0, pre_bend_z - flavor_tube_z_bottom)

    # S-bend (CCW then CW, ends tangent to +Z by construction).
    s1_mid, s1_end, s1_tangent = _arc_from_tangent(
        p_s_bend_start, (0.0, 1.0), flavor_bend_radius, flavor_bend_theta_rad, ccw=True
    )
    s2_mid, s2_end, s2_tangent = _arc_from_tangent(
        s1_end, s1_tangent, flavor_bend_radius, flavor_bend_theta_rad, ccw=False
    )

    # Vertical to the gooseneck start, X unchanged.
    p_gn_start = (s2_end[0], gn_bend1_start_z - flavor_tube_z_bottom)

    arc1, mid_end, arc2, tip_end = _gooseneck_segments(
        p_gn_start, s2_tangent, gn_flavor_bend1_r, gn_flavor_bend2_r
    )

    path = (
        cq.Workplane("XZ")
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

    profile = cq.Workplane("XY").circle(flavor_tube_r)
    return profile.sweep(path, transition="round")


def build_flavor_tube(y_sign):
    """One Ø 1/4" flavor tube placed at its world position.

    Built at the origin, then translated to (flavor_tube_x_lower,
    y_sign · flavor_tube_y_offset, flavor_tube_z_bottom)."""
    tube = _build_flavor_tube_at_origin()
    return tube.translate((
        flavor_tube_x_lower,
        y_sign * flavor_tube_y_offset,
        flavor_tube_z_bottom,
    ))


# Lever pivot — axis parallel to Y at (X=lever_pivot_x, Z=lever_pivot_z).
# The lever swings between rest (0°) and pressed (-lever_press_angle_deg)
# around this axis, sweeping the clearance volume the shell must avoid.
lever_pivot_x = 1.5
lever_pivot_z = plateau_z + 7.0
lever_press_angle_deg = 18.0


def build_lever():
    """The lever as a swing-clearance blob: union of rest position +
    pressed-down position.

    The shell needs to clear the volume the lever sweeps through during
    actuation, not just the rest envelope. Modeling that as the union
    of the two extremes (0° and -lever_press_angle_deg around the pivot)
    is a deliberate approximation — visually an "ugly blob" — but it
    captures what the shell must avoid. Each position carries its own
    vertical water-tube clearance cut."""
    cut_cylinder = (
        cq.Workplane("XY")
        .workplane(offset=plateau_z + 1)
        .moveTo(9, 0)
        .circle(water_tube_r + 1)  # slightly larger than water tube for clearance
        .extrude(50)
    )
    add_taper = (
        cq.Workplane("YZ")
        .workplane(offset=-6)
        .moveTo(0, plateau_z + 4.5)
        .rect(13, 8.5, centered=(True, False))
        .workplane(offset=-36)
        .moveTo(0, plateau_z + 1 + 9)
        .rect(13, 3, centered=(True, False))
        .loft(combine=True)
    )

    # Bare lever shape — no clearance cuts, in the rest position.
    base_lever = (
        cq.Workplane("YZ")
        .workplane(offset=9)
        .moveTo(0, plateau_z + 1)
        .rect(13, 12, centered=(True, False))
        .extrude(-15)
        .union(add_taper)
    )

    pivot_a = (lever_pivot_x, 0, lever_pivot_z)
    pivot_b = (lever_pivot_x, 1, lever_pivot_z)

    # Rest position: lever as-is, with its rest-position water-tube cut.
    lever_rest = base_lever.cut(cut_cylinder)

    # Pressed-down position: rotate down around the pivot, then take
    # the same vertical water-tube clearance cut. The cut is vertical
    # in world coordinates, so it correctly clears the upright water
    # tube even though the lever itself is tilted.
    lever_pressed = lever_rest.rotate(pivot_a, pivot_b, -lever_press_angle_deg).cut(cut_cylinder)
    lever_rest_final = lever_pressed.rotate(pivot_a, pivot_b, lever_press_angle_deg)

    # Union of both extremes — the swing-clearance envelope.
    return lever_rest_final.union(lever_pressed)


def build_assembly():
    """Combine the reference body and our new parts into one assembly."""
    body = load_valve_body()
    water_tube = build_water_dispense_tube()
    flavor_tube_pos_y = build_flavor_tube(+1)
    flavor_tube_neg_y = build_flavor_tube(-1)
    lever = build_lever()
    mounting_plate = load_mounting_plate()
    mounting_gasket = load_mounting_gasket()
    shell = load_shell()

    silver = cq.Color(0.85, 0.85, 0.88)  # near-stainless silver
    petg_tan = cq.Color(0.85, 0.78, 0.62)  # printed-part tan
    tpu_black = cq.Color(0.15, 0.15, 0.15)  # TPU 90A black gasket — slightly
                                            # lighter than the body so the two
                                            # read apart

    assy = cq.Assembly(name="touch-flo-faucet-assembly")
    assy.add(body, name="valve_body", color=cq.Color("black"))
    assy.add(water_tube, name="water_dispense_tube", color=silver)
    assy.add(flavor_tube_pos_y, name="flavor_tube_pos_y", color=silver)
    assy.add(flavor_tube_neg_y, name="flavor_tube_neg_y", color=silver)
    assy.add(lever, name="lever", color=silver)
    assy.add(mounting_plate, name="mounting_plate", color=petg_tan)
    assy.add(mounting_gasket, name="mounting_gasket", color=tpu_black)
    assy.add(shell, name="shell", color=petg_tan)
    return assy


def main():
    assy = build_assembly()

    out = _assembly_dir / "touch-flo-faucet-assembly.step"
    # cq.Assembly.save() emits a deprecation warning in this CadQuery
    # version but still produces correct multi-solid STEP. The
    # cq.exporters.export(assy, ...) replacement currently rejects
    # Assembly objects on this install — revisit when the venv is bumped.
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
    print(f"                         center at X={port_center_x} mm, Y={port_center_y} mm")
    print(f"  Flavor tubes (×2):     Ø{flavor_tube_od:.3f} mm")
    print(f"                         Z_bottom = {flavor_tube_z_bottom:.1f} mm")
    print(f"                         lower X = {flavor_tube_x_lower:.4f} mm "
          f"(tangent to body +X + to each other)")
    print(f"                         upper X = {flavor_tube_x_upper:.4f} mm "
          f"(tangent to water tube + to each other)")
    print(f"                         Y = ±{flavor_tube_y_offset:.4f} mm (constant)")
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
    print(f"  Mounting plate:        loaded from printed-parts/")
    print(f"                         {mounting_plate_step.name}")
    print(f"  Mounting gasket:       loaded from printed-parts/")
    print(f"                         {mounting_gasket_step.name}")
    print(f"  Shell (zones 1-6):     loaded from printed-parts/")
    print(f"                         {shell_step.name}")
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
