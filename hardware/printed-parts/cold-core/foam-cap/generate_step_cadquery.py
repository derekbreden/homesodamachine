"""Foam-cap stack — the three parts that close one end of the
foam shell during the pour-in-place foam cure: the cap tray, the
lid that sits atop the cap during pouring, and the TPU 90A gasket
that compresses between the cap and the outer-shell mating face.
Printed twice per build (one stack on each end of the shell)."""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
sys.path.insert(0, str(_here.parent))

from _cadq_export import export_step
from _foam_shell_geometry import (
    build_foam_cap,
    build_foam_cap_lid,
    build_foam_cap_gasket,
    build_a_y_axis_hole_punch,
    tank_copper_shell_radius,
    wall_and_floor_thickness,
    foam_cap_height,
    foam_cap_interior_height,
    xz_plane_y_up,
)


# Lid Y extent. The lid is a flat solid extruded `wall_and_floor_thickness`
# (2 mm) high in +Y from `xz_plane_y_up` (y=0), so it spans y ∈ [0, 2].
lid_y_height = wall_and_floor_thickness


# CO2 inlet Z position — mirrors `cut_co2_inlet` in
# _foam_shell_geometry.py. Recomputed here from the same primary
# constants so the top cap's CO2 pass-through stays aligned with the
# foam shell's Y-axis CO2 inlet hole without hard-coding −68.75.
_R_back_outer = tank_copper_shell_radius                                # 72.5
_R_back_inner = tank_copper_shell_radius - wall_and_floor_thickness     # 70.5
_R_arch_outer = _R_back_inner                                            # 70.5
_R_arch_inner = _R_arch_outer - 9                                        # 61.5
_z_back_mid   = -(_R_back_outer + _R_back_inner) / 2                    # −71.5
_z_arch_mid   = -(_R_arch_outer + _R_arch_inner) / 2                    # −66.0
co2_inlet_z   = (_z_back_mid + _z_arch_mid) / 2                          # −68.75


def cut_co2_inlet(cap):
    """Y-axis ⌀6.5 cylindrical cut through the top cap at the same
    (x, z) as the foam shell's CO2 inlet, continuing the CO2 tube path
    from the shell's −Z support arch up through the top cap."""
    return cap.cut(
        build_a_y_axis_hole_punch(
            origin=(0, 0, co2_inlet_z),
            hole_punch_height=foam_cap_height,
        )
    )


def cut_co2_inlet_lid(lid):
    """Y-axis ⌀6.5 cylindrical cut through the foam-cap lid at the same
    (x, z) as the top cap's CO2 through-hole. The lid sits atop the cap
    during the foam pour; this hole continues the CO2 path from the
    outside through the lid → cap stack. Same axis (Y), same XZ position,
    same diameter (⌀6.5) as `cut_co2_inlet`."""
    return lid.cut(
        build_a_y_axis_hole_punch(
            origin=(0, 0, co2_inlet_z),
            hole_punch_height=lid_y_height,
        )
    )


# Boss/tube geometry. The boss is a hollow cylindrical tube inside the
# cap's foam-fill cavity, centered on the CO2 through-hole. It isolates
# the through-hole from the foam pour: foam goes in the cavity around
# the boss, but cannot reach the hole because the boss walls separate
# them. With the boss present, the cap can lay flat during the foam
# pour without a plug protruding from the through-hole.
#
# Inner radius matches the existing through-hole (3.25 → ⌀6.5), so the
# tube's internal bore is continuous with the hole. Outer radius =
# inner + wall_and_floor_thickness (per the cap's 2 mm wall convention).
# Y range: from the cavity-side face of the floor (y =
# wall_and_floor_thickness) to the cavity-opening face of the cap
# (y = foam_cap_height) — i.e. the full interior cavity height.
co2_boss_inner_radius = 3.25
co2_boss_outer_radius = co2_boss_inner_radius + wall_and_floor_thickness
co2_boss_y_bottom = wall_and_floor_thickness
co2_boss_y_top = foam_cap_height


def add_co2_boss(cap):
    """Union an annular boss around the CO2 through-hole on the cap
    floor's cavity side. The boss is a 2 mm-wall hollow tube spanning
    the full interior cavity height, sealing the through-hole off from
    the foam pour while keeping the bore clear so CO2 line can pass.

    `workplane(origin=...)` shifts only in the in-plane axes; to shift
    along the workplane normal (Y here) we pass `offset=co2_boss_y_bottom`
    — same pattern used by `build_a_y_axis_hole_punch`."""
    outer = (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(0, co2_boss_y_bottom, co2_inlet_z),
                   offset=co2_boss_y_bottom)
        .circle(co2_boss_outer_radius)
        .extrude(co2_boss_y_top - co2_boss_y_bottom)
    )
    inner = (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(0, co2_boss_y_bottom, co2_inlet_z),
                   offset=co2_boss_y_bottom)
        .circle(co2_boss_inner_radius)
        .extrude(co2_boss_y_top - co2_boss_y_bottom)
    )
    boss = outer.cut(inner)
    return cap.union(boss)


def main():
    cap = build_foam_cap()
    cap_top = cut_co2_inlet(cap)
    cap_top = add_co2_boss(cap_top)
    cap_bottom = cap
    lid = build_foam_cap_lid()
    lid_top = cut_co2_inlet_lid(lid)
    lid_bottom = lid
    gasket = build_foam_cap_gasket()

    # Sanity check: cap_top differs from cap_bottom by the floor
    # through-hole (subtracted) plus the cavity-side annular boss
    # (added). With the boss present, the net volume change is:
    #   boss_annular_volume − through_hole_volume
    # where the through-hole is the ⌀6.5 floor pass and the boss is
    # the (R_outer² − R_inner²)·π · cavity_height annular ring.
    through_hole_volume = math.pi * co2_boss_inner_radius ** 2 * wall_and_floor_thickness
    boss_annular_volume = (
        math.pi
        * (co2_boss_outer_radius ** 2 - co2_boss_inner_radius ** 2)
        * (co2_boss_y_top - co2_boss_y_bottom)
    )
    expected_diff = boss_annular_volume - through_hole_volume
    actual_diff = cap_top.val().Volume() - cap_bottom.val().Volume()
    n_solids = len(cap_top.solids().vals())
    print(f"co2_inlet_z = {co2_inlet_z}")
    print(f"foam_cap_height = {foam_cap_height}")
    print(f"foam_cap_interior_height = {foam_cap_interior_height}")
    print(f"boss y range = [{co2_boss_y_bottom}, {co2_boss_y_top}] (height {co2_boss_y_top - co2_boss_y_bottom})")
    print(f"boss radii = [{co2_boss_inner_radius}, {co2_boss_outer_radius}]")
    print(f"cap_top.Volume() - cap_bottom.Volume() = {actual_diff:.3f}")
    print(f"expected (boss annular − through-hole) = {expected_diff:.3f}")
    print(f"cap_top solids = {n_solids}")

    # Sanity check for the lid: lid_top differs from lid_bottom by the
    # Y-axis ⌀6.5 cylindrical pass through the lid's full Y extent.
    lid_hole_volume = math.pi * co2_boss_inner_radius ** 2 * lid_y_height
    lid_actual_diff = lid_bottom.val().Volume() - lid_top.val().Volume()
    print(f"lid_y_height = {lid_y_height}")
    print(f"lid_bottom.Volume() - lid_top.Volume() = {lid_actual_diff:.3f}")
    print(f"expected (⌀6.5 cylinder × lid_y_height) = {lid_hole_volume:.3f}")

    export_step(cap_top, str(_here / "foam-cap-top.step"))
    export_step(cap_bottom, str(_here / "foam-cap-bottom.step"))
    export_step(lid_top, str(_here / "foam-cap-lid-top.step"))
    export_step(lid_bottom, str(_here / "foam-cap-lid-bottom.step"))
    export_step(gasket, str(_here / "foam-cap-gasket.step"))
    print("-> foam-cap-top.step")
    print("-> foam-cap-bottom.step")
    print("-> foam-cap-lid-top.step")
    print("-> foam-cap-lid-bottom.step")
    print("-> foam-cap-gasket.step")


if __name__ == "__main__":
    main()
